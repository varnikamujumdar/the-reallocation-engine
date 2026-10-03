#!/usr/bin/env python3
"""sponsor_shortlist.py — new-grad SWE sponsor shortlist with a pre-OPT timeline gate.

Recipe: recipes/cases/2026fa/varnikamujumdar-swe-newgrad-sponsors.md

For an F-1 student who has not yet filed OPT, take a list of target companies,
look each one up in the 80 Days to Stay CSV (H-1B history), assign a
sponsorship tier from the record, compute one timeline gate from the
persona's dates, and hand the result to the EXISTING scorer
(scripts/score/role-scorer.mjs). Nothing here re-implements the scorer.

Every value is labeled record / model-judgment / your-input. This script makes
no model judgments, so that label never appears in its output.

What it does NOT do:
  - check whether any posting is live (liveness is sent as UNCHECKED, see below);
  - judge whether the student fits a role (no `fit` vote is sent);
  - fuzzy-match company names (near matches are listed for a human, never used).

Usage (from the repo root):
  python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/sponsor_shortlist.py \
      --persona scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/persona.bella.json \
      --targets scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/targets.bella.json

Exit codes: 0 ok · 2 input gate (G1) failed, nothing written · 3 scorer failed.
"""

import argparse
import ast
import csv
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
DEFAULT_CSV = REPO / "data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv"
DEFAULT_SOC_CSV = REPO / "data/bls/compact/soc_occupation_compact.csv"
SCORER = REPO / "scripts/score/role-scorer.mjs"
DEFAULT_OUT_ROOT = REPO / "course/2026fa/submissions/varnikamujumdar/runs"

REQUIRED_COLUMNS = ["company_name", "state", "Total Approvals", "Total Denials",
                    "Approval_Rate", "top_job_titles_sponsored", "latest_funding_date"]

RECORD, INPUT = "record", "your-input"

# ── Tier rule. Thresholds and p values are MY design choices (your-input), not
#    records. p values mirror the Proven/Likely examples in data/examples/ch11-roles.json.
TIER_RULE = {
    "proven_min_approvals": 10,
    "proven_min_rate": 90.0,
    "p": {"Proven": 0.9, "Likely": 0.6, "None": 0.0},
    "source": INPUT,
}
# A title counts as "senior" if any of these words appear. Known to be crude:
# "Software Engineer II" is counted senior, "Member of Technical Staff" is not
# a software title at all (CHANGE-BRIEF §7.1).
SENIOR_RE = re.compile(r"\b(senior|sr|staff|principal|lead|manager|director|architect|head|vp|ii|iii|iv)\b", re.I)
SOFTWARE_RE = re.compile(r"software", re.I)
SUFFIXES = {"INC", "LLC", "CORP", "CORPORATION", "CO", "LTD", "LP", "LLP", "PLC", "INCORPORATED", "COMPANY"}


class GateError(Exception):
    """G1 input gate failure: halt, write nothing."""


# ───────────────────────────── inputs ─────────────────────────────

def parse_date(value, field):
    try:
        return dt.date.fromisoformat(str(value))
    except (TypeError, ValueError):
        raise GateError(f"{field} is not a YYYY-MM-DD date: {value!r}")


def load_json(path, what):
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        raise GateError(f"{what} file not found: {path}")
    except json.JSONDecodeError as e:
        raise GateError(f"{what} file is not valid JSON: {path} ({e})")


def load_csv(path):
    path = Path(path)
    if not path.exists():
        raise GateError(f"80-days CSV not found: {path}")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise GateError(f"80-days CSV is missing required columns: {missing}")
        rows = list(reader)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return rows, digest


def validate_timeline(t):
    """Return parsed timeline dates or raise GateError (failure case F4)."""
    d = {k: parse_date(t.get(k), f"timeline.{k}") for k in ("as_of", "program_end", "opt_requested_start")}
    d["opt_filed"] = parse_date(t["opt_filed"], "timeline.opt_filed") if t.get("opt_filed") else None
    for k in ("ead_wait_days", "hiring_lag_days", "opt_filing_window_before_days",
              "opt_start_window_days", "unemployment_limit_days"):
        v = t.get(k)
        if not isinstance(v, int) or isinstance(v, bool) or v < 0:
            raise GateError(f"timeline.{k} must be a non-negative integer, got {v!r}")
        d[k] = v
    # Post-completion OPT can be filed from N days before program end until the
    # start window closes after it. Both N values are your-input (see recipe TODO 2).
    window_open = d["program_end"] - dt.timedelta(days=d["opt_filing_window_before_days"])
    window_close = d["program_end"] + dt.timedelta(days=d["opt_start_window_days"])
    d["filing_window_open"], d["filing_window_close"] = window_open, window_close
    if d["as_of"] > window_close and d["opt_filed"] is None:
        raise GateError(
            f"program ended {d['program_end']} and the {d['opt_start_window_days']}-day window to start OPT "
            f"closed {window_close}; no OPT filing recorded. This tool cannot help — talk to your DSO.")
    if d["opt_filed"] is not None and not (window_open <= d["opt_filed"] <= window_close):
        raise GateError(
            f"opt_filed {d['opt_filed']} is outside the OPT filing window {window_open} to {window_close} "
            f"({d['opt_filing_window_before_days']} days before program end to {d['opt_start_window_days']} days after)")
    if not (d["program_end"] < d["opt_requested_start"] <= window_close):
        raise GateError(
            f"opt_requested_start {d['opt_requested_start']} must fall after program_end "
            f"{d['program_end']} and on/before {window_close}")
    return d


# ─────────────────────────── company lookup ───────────────────────────

def normalize(name):
    tokens = re.sub(r"[^A-Z0-9]+", " ", str(name).upper()).split()
    while tokens and tokens[-1] in SUFFIXES:
        tokens.pop()
    return " ".join(tokens)


def build_index(rows):
    index = {}
    for row in rows:
        index.setdefault(normalize(row["company_name"]), []).append(row)
    return index


def lookup(typed, index):
    """Exact match on the normalized name. Near matches are listed, never used."""
    key = normalize(typed)
    hits = index.get(key, [])
    if len(hits) == 1:
        return {"status": "matched", "row": hits[0], "possible_matches": []}
    if len(hits) > 1:
        return {"status": "ambiguous", "row": None,
                "possible_matches": [h["company_name"] for h in hits][:3]}
    near = sorted(k for k in index if key and k.startswith(key))[:3]
    return {"status": "not-in-csv", "row": None,
            "possible_matches": [index[k][0]["company_name"] for k in near]}


def parse_titles(raw):
    if not raw or not raw.strip():
        return [], None
    try:
        titles = ast.literal_eval(raw)
        if isinstance(titles, (list, tuple)):
            return [str(t).strip() for t in titles], None
    except (ValueError, SyntaxError):
        pass
    return [], "top_job_titles_sponsored could not be parsed"


def to_float(raw):
    try:
        return float(raw) if str(raw).strip() != "" else None
    except ValueError:
        return None


def classify(row):
    """Sponsorship tier from one CSV row. Returns tier, p (or None), flags, raw fields."""
    raw = {c: row.get(c, "") for c in REQUIRED_COLUMNS}
    approvals = to_float(row["Total Approvals"])
    denials = to_float(row["Total Denials"])
    rate = to_float(row["Approval_Rate"])
    titles, title_err = parse_titles(row["top_job_titles_sponsored"])
    software = [t for t in titles if SOFTWARE_RE.search(t)]
    entry = [t for t in software if not SENIOR_RE.search(t)]
    flags = [title_err] if title_err else []

    if approvals is None:  # F2: in the CSV but no H-1B data. Absence is not "no".
        return {"tier": "Unknown", "p": None, "flags": ["H-1B columns blank in CSV"] + flags,
                "software_titles": software, "entry_titles": entry, "raw": raw}
    if approvals == 0:  # F5
        flags.append(f"0 approvals, {denials if denials is not None else '?'} denials on record")
        return {"tier": "None", "p": TIER_RULE["p"]["None"], "flags": flags,
                "software_titles": software, "entry_titles": entry, "raw": raw}

    if not software:
        flags.append("sponsors, but no software title in its top sponsored titles")
    elif not entry:
        flags.append("senior-only software sponsorship history")  # F3
    if approvals < TIER_RULE["proven_min_approvals"]:
        flags.append(f"low volume ({approvals:g} approvals)")
    if rate is None:
        flags.append("approval rate blank")
    elif rate < TIER_RULE["proven_min_rate"]:
        flags.append(f"approval rate {rate:.1f}% below {TIER_RULE['proven_min_rate']:g}%")

    proven = (entry and approvals >= TIER_RULE["proven_min_approvals"]
              and rate is not None and rate >= TIER_RULE["proven_min_rate"])
    tier = "Proven" if proven else "Likely"
    return {"tier": tier, "p": TIER_RULE["p"][tier], "flags": flags,
            "software_titles": software, "entry_titles": entry, "raw": raw}


# ─────────────────────────── timeline gate ───────────────────────────

def timeline_factor(d):
    """One factor for every company (same hiring-lag assumption). All inputs your-input."""
    # Not filed yet: assume filing on the run date, or on the day the window opens if that is later.
    filed = d["opt_filed"] or max(d["as_of"], d["filing_window_open"])
    ead_ready = filed + dt.timedelta(days=d["ead_wait_days"])
    clock_start = max(d["opt_requested_start"], ead_ready)
    earliest_offer_start = d["as_of"] + dt.timedelta(days=d["hiring_lag_days"])
    work_start = max(earliest_offer_start, clock_start)
    days_used = (work_start - clock_start).days
    factor = max(0.0, 1 - days_used / d["unemployment_limit_days"])
    return {
        "factor": round(factor, 4), "source": INPUT,
        "ead_ready_estimate": ead_ready.isoformat(),
        "unemployment_clock_start_estimate": clock_start.isoformat(),
        "earliest_work_start_estimate": work_start.isoformat(),
        "unemployment_days_used_estimate": days_used,
        "opt_filed_assumed": None if d["opt_filed"] else filed.isoformat(),
        "filing_window": [d["filing_window_open"].isoformat(), d["filing_window_close"].isoformat()],
        "formula": "max(0, 1 - days_used / unemployment_limit_days) [your-input design choice]",
    }


def soc_context(soc_csv, soc):
    """Read-only wage context; carries no weight (scorer role_quality weight is 0)."""
    try:
        with Path(soc_csv).open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("bls_soc_code") == soc:
                    return {"status": "ok", "title": row["title"], "annual_median_wage": row["annual_median_wage"],
                            "oews_year": row["oews_year"], "source": RECORD}
    except FileNotFoundError:
        return {"status": "soc-csv-missing", "source": RECORD}
    return {"status": "no-soc-row", "soc": soc, "source": RECORD}


# ─────────────────────────── outputs ───────────────────────────

def next_free_dir(base):
    """Default output never overwrites an earlier run: <as_of>, then <as_of>-2, -3, ..."""
    candidate, n = base, 1
    while candidate.exists():
        n += 1
        candidate = base.with_name(f"{base.name}-{n}")
    return candidate


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def build_role(entry, timeline):
    s = entry["sponsorship"]
    # p comes from MY tier rule applied to record fields, so the number itself is your-input.
    sponsorship = {"tier": s["tier"], "source": INPUT, "basis": "tier rule (your-input) on 80-days CSV fields (record)"}
    if s["p"] is not None:
        sponsorship["p"] = s["p"]
    return {
        "role_id": slug(entry["typed"]),
        "company": entry["csv_name"] or entry["typed"],
        "title": "Software Engineer (new grad)",
        "sponsorship": sponsorship,
        # The scorer defaults a MISSING liveness to 1.0 labeled "record"
        # (role-scorer.mjs). Sending it explicitly keeps "not checked" honest.
        "liveness": {"factor": 1.0, "source": INPUT, "status": "UNCHECKED"},
        "timeline": {"factor": timeline["factor"], "source": INPUT},
    }


def next_action(rec, tier, reason):
    if rec == "Apply":
        return "BLOCKED until liveness: run `npm run ats:liveness -- <posting url>`; if active, tailor the application (2-hour block)"
    if rec == "Consider":
        return "Network in first (3-hour block): ask whether they sponsor *new-grad* SWE roles"
    if "gated" in (reason or ""):
        return "Skip: the timeline gate is closed for this run's dates"
    if tier == "Unknown":
        return "No H-1B record. That is NOT evidence they don't sponsor; check possible matches or ask a contact before dropping"
    return "Skip"


def render_report(run):
    p, t, soc = run["persona"], run["timeline"], run["soc_context"]
    by = {}
    for e in run["companies"]:
        by.setdefault(e["recommendation"], []).append(e)
    n = len(run["companies"])
    skip = len(by.get("Skip", []))
    lines = [
        f"# New-grad SWE sponsor shortlist — {p['name']} — {t['as_of']}",
        "",
        "## Executive summary",
        "",
        f"This is a shortlist of {n} companies for a fictional international student finishing a master's in "
        f"computer science on {t['program_end']} who wants an entry-level software engineering job and will need visa sponsorship. "
        "Each company was looked up in a public list of past work-visa approvals, and the student's own dates were used "
        "to check whether a job could start in time.",
        "",
        f"Result: **{len(by.get('Apply', []))} apply, {len(by.get('Consider', []))} consider, {skip} skip** "
        f"({skip * 100 // n if n else 0}% skipped). "
        "No job posting was checked. Every \"apply\" stays blocked until a person confirms the posting is real and open. "
        f"{sum(1 for e in run['companies'] if e['sponsorship']['tier'] == 'Unknown')} companies had no visa record at all, "
        "which means *unknown*, not *does not sponsor*.",
        "",
        "## Decisions",
        "",
        "| Company (as typed) | Matched CSV name [record] | Tier [your-input rule] | Approvals / denials / rate [record] | Composite | Decision | Next action |",
        "|---|---|---|---|---|---|---|",
    ]
    for e in run["companies"]:
        raw = e["sponsorship"]["raw"] or {}
        rate = to_float(raw.get("Approval_Rate")) if raw else None
        rec = (f"{raw.get('Total Approvals') or '—'} / {raw.get('Total Denials') or '—'} / "
               f"{'—' if rate is None else f'{rate:.2f}%'}") if raw else "—"
        matched = e["csv_name"] or f"*{e['match']['status']}*"
        if e["match"]["possible_matches"]:
            matched += " (possible: " + "; ".join(e["match"]["possible_matches"]) + " — not used)"
        decision = e["recommendation"] + (" — BLOCKED: liveness unchecked" if e["recommendation"] == "Apply" else "")
        lines.append(f"| {e['typed']} | {matched} | {e['sponsorship']['tier']} | {rec} | {e['composite']:.3f} | **{decision}** | {e['next_action']} |")
    lines += ["", "### Flags per company", ""]
    for e in run["companies"]:
        if e["sponsorship"]["flags"]:
            lines.append(f"- **{e['typed']}**: " + "; ".join(e["sponsorship"]["flags"]))
    lines += [
        "",
        "## Verified vs inferred",
        "",
        "| Value | Label | Where it came from |",
        "|---|---|---|",
        "| H-1B approvals, denials, rate, top sponsored titles | record | 80 Days to Stay CSV (sha256 below; rates rounded here, raw strings in run.json). The CSV does not say which fiscal years it covers |",
        "| Sponsorship tier (Proven / Likely / None / Unknown) | record fields → your-input rule | thresholds: ≥10 approvals, ≥90% rate, one non-senior software title |",
        "| Sponsorship p (0.9 / 0.6 / 0.0) | your-input | mirrors data/examples/ch11-roles.json; sent to the scorer labeled your-input |",
        f"| Timeline factor {t['factor']} | your-input | dates and assumptions below; same for every company |",
        "| Liveness 1.0 | your-input, **UNCHECKED** | no posting was fetched |",
        "| Fit | not sent | no record exists; not guessed |",
        f"| SOC {run['soc']} wage context | record | {soc.get('title', soc['status'])}, median ${soc.get('annual_median_wage', '—')} (OEWS {soc.get('oews_year', '—')}); carries no weight |",
        "",
        "## Timeline assumptions (all your-input)",
        "",
        f"- Program end {t['program_end']}; requested OPT start {t['opt_requested_start']}; OPT filed "
        f"{t['opt_filed'] or 'not yet (assumed filed ' + t['opt_filed_assumed'] + ')'}; filing window "
        f"{t['filing_window'][0]} to {t['filing_window'][1]}",
        f"- EAD wait {t['ead_wait_days']} days → EAD estimate {t['ead_ready_estimate']}; hiring lag {t['hiring_lag_days']} days",
        f"- Earliest work start {t['earliest_work_start_estimate']}; unemployment days used ≈ {t['unemployment_days_used_estimate']} "
        f"of {t['unemployment_limit_days']} → factor {t['factor']}",
        f"- Regulatory constants ({t['opt_filing_window_before_days']} days before / {t['opt_start_window_days']} days after program end to file, "
        f"{t['unemployment_limit_days']}-day unemployment limit) "
        "are typed in, not read from a record. Check them against USCIS before relying on this.",
        "- Sensitivity: with no fit vote, a Proven company (p 0.9 × weight 0.35 = 0.315) drops from Apply to Consider "
        "once the timeline factor falls below 0.9524 (0.30 / 0.315), i.e. from the 5th unemployment day.",
        "",
        "## Run record",
        "",
        f"- CSV: `{run['inputs']['csv']}` sha256 `{run['inputs']['csv_sha256'][:16]}…` ({run['inputs']['csv_rows']} rows)",
        f"- Scorer: `{run['inputs']['scorer']}` (unchanged); its own report: `role-scores.md`. **Read that file as a raw audit only:** "
        "the scorer has no 'unchecked' state, so it calls the UNCHECKED liveness of 1.0 \"gates healthy\" and says Unknown rows are "
        "\"time better spent elsewhere\". This report, not the scorer's, carries the BLOCKED and NOT-a-no labels.",
        "- Agent log: `run.json`",
        "",
        "*Human gate: nothing here is an application. A person picks which rows to act on and records that choice in the run log.*",
    ]
    return "\n".join(lines) + "\n"


def run(args):
    persona = load_json(args.persona, "persona")
    targets = load_json(args.targets, "targets")
    if not isinstance(targets, list) or not all(isinstance(x, str) and x.strip() for x in targets):
        raise GateError("targets must be a JSON list of company-name strings")
    if not isinstance(persona.get("timeline"), dict):
        raise GateError("persona is missing a `timeline` object")
    dates = validate_timeline(persona["timeline"])
    rows, digest = load_csv(args.csv)
    index = build_index(rows)
    tl = timeline_factor(dates)

    companies = []
    for typed in targets:
        m = lookup(typed, index)
        if m["row"] is not None:
            spons = classify(m["row"])
        else:
            spons = {"tier": "Unknown", "p": None, "software_titles": [], "entry_titles": [], "raw": None,
                     "flags": [f"no unique CSV row ({m['status']})"]}  # F1
        companies.append({"typed": typed, "csv_name": m["row"]["company_name"] if m["row"] else None,
                          "match": {"status": m["status"], "possible_matches": m["possible_matches"],
                                    "source": RECORD, "possible_matches_used": False},
                          "labels": {"raw": RECORD, "tier": "your-input rule on record fields", "p": INPUT, "flags": RECORD},
                          "sponsorship": spons})

    out_dir = Path(args.out_dir) if args.out_dir else next_free_dir(DEFAULT_OUT_ROOT / dates["as_of"].isoformat())
    out_dir.mkdir(parents=True, exist_ok=True)
    roles = [build_role(e, tl) for e in companies]
    roles_path = out_dir / "roles.json"
    roles_path.write_text(json.dumps(roles, indent=2) + "\n")

    proc = subprocess.run(["node", str(SCORER), str(roles_path), "--out-dir", str(out_dir)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout + proc.stderr)
        raise RuntimeError(f"scorer exited {proc.returncode}")
    scored = {r["role_id"]: r for r in json.loads((out_dir / "role-scores.json").read_text())["roles"]}

    for e, role in zip(companies, roles):
        s = scored[role["role_id"]]
        e.update(role_id=role["role_id"], composite=s["composite"], recommendation=s["recommendation"],
                 scorer_reason=s["reason"], next_action=next_action(s["recommendation"], e["sponsorship"]["tier"], s["reason"]))

    def rel(p):
        try:
            return str(Path(p).resolve().relative_to(REPO))
        except ValueError:
            return str(p)

    t = persona["timeline"]
    record = {
        "_tool": "varnikamujumdar-swe-newgrad-sponsors/sponsor_shortlist.py",
        "_recipe": "recipes/cases/2026fa/varnikamujumdar-swe-newgrad-sponsors.md",
        "generated": dt.date.today().isoformat(),
        "_out_dir": rel(out_dir),
        "persona": {"name": persona.get("name"), "source": INPUT},
        "soc": persona.get("soc", "15-1252"),
        "inputs": {"csv": rel(args.csv), "csv_sha256": digest, "csv_rows": len(rows),
                   "persona": rel(args.persona), "targets": rel(args.targets), "scorer": rel(SCORER)},
        "tier_rule": TIER_RULE,
        "senior_title_regex": SENIOR_RE.pattern,
        "timeline": {**{k: t.get(k) for k in ("as_of", "program_end", "opt_requested_start", "opt_filed",
                                              "ead_wait_days", "hiring_lag_days", "opt_filing_window_before_days",
                                              "opt_start_window_days",
                                              "unemployment_limit_days")}, **tl},
        "liveness": {"status": "UNCHECKED", "factor_sent": 1.0, "source": INPUT,
                     "human_gate": "npm run ats:liveness -- <posting url> before any Apply"},
        "soc_context": soc_context(args.soc_csv, persona.get("soc", "15-1252")),
        "companies": companies,
    }
    (out_dir / "run.json").write_text(json.dumps(record, indent=2) + "\n")
    (out_dir / "report.md").write_text(render_report(record))
    return record, out_dir, proc.stdout.strip()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--persona", required=True)
    ap.add_argument("--targets", required=True)
    ap.add_argument("--csv", default=str(DEFAULT_CSV))
    ap.add_argument("--soc-csv", default=str(DEFAULT_SOC_CSV))
    ap.add_argument("--out-dir", default=None, help="default: course/2026fa/submissions/varnikamujumdar/runs/<as_of>/")
    args = ap.parse_args(argv)
    try:
        record, out_dir, scorer_out = run(args)
    except GateError as e:
        print(f"✗ G1 input gate: {e}\n  nothing written.", file=sys.stderr)
        return 2
    except RuntimeError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 3
    print(scorer_out)
    tiers = {}
    for c in record["companies"]:
        tiers[c["sponsorship"]["tier"]] = tiers.get(c["sponsorship"]["tier"], 0) + 1
    print(f"✓ tiers [your-input rule on record data]: " + " · ".join(f"{k} {v}" for k, v in sorted(tiers.items())))
    print(f"✓ timeline factor [your-input] {record['timeline']['factor']} · liveness UNCHECKED (human gate)")
    print(f"  {record['_out_dir']}/report.md  +  run.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
