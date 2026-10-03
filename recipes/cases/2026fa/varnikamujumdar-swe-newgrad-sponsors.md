---
status: DRAFT          # prototype runs on the shipped CSV, but 8 typed TODOs stay open, so SPECIFIED is not yet earned
todos_open: 8
last_gate: null
attestation: null
recipe_version: 0.1.0
---

# New-grad SWE sponsor shortlist with a pre-OPT timeline gate

## Executive summary

**What it does:** takes a list of companies a student is thinking about applying to and, for each one, answers two questions from records instead of guesswork: *has this company actually sponsored work visas for software engineers, and specifically non-senior ones?* and *if I start a hiring process today, can the job begin before my post-graduation work permit clock runs out?* It returns apply, consider, or skip for each company, with every number labeled by where it came from.

**Who it's for:** an international master's student in computer science on an F-1 visa, a few months before graduation, who has not yet received a post-graduation work permit (OPT) and wants an entry-level software engineering job that will later need a visa sponsor.

**What it decides, and what it leaves to a person:** it sorts companies into proven, likely, none, or unknown sponsors and computes a timing factor. It never checks whether a job posting is real or still open, and it does not judge whether the student fits a role. Every "apply" stays blocked until a person checks the actual posting. A company with no visa record comes back as *unknown*, never as *does not sponsor*.

## Purpose

Most visible H-1B history is for senior engineers, so "does Company X sponsor software engineers?" is the wrong question for a new grad. This recipe asks a narrower one. It also handles a timeline no other recipe in this repo models: a student who is **not yet on OPT**. For that student the risk is not "days left" but whether an offer can turn into a start date they're allowed to work on.

Engine layers: **80 Days to Stay** (H-1B history in the company CSV) and the **visa-timeline gate**. Role quality is shown for context only (see Facts that bite).

## Source inventory

| What | Exact path / command | Status |
|---|---|---|
| Company + H-1B table | `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv` (30,369 rows; 1,557 have H-1B data) | exists, shipped |
| Occupation wage context | `data/bls/compact/soc_occupation_compact.csv`, row `15-1252` | exists, shipped |
| Scorer (combine + gates) | `node scripts/score/role-scorer.mjs <roles.json> --out-dir <dir>` | exists, used unchanged |
| Scorer input shape | `data/examples/ch11-roles.json` | exists |
| Liveness (human, at gate G3) | `npm run ats:liveness -- <posting url>` | exists; needs `npx playwright install chromium` on a fresh clone |
| **Prototype** | `python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/sponsor_shortlist.py --persona <persona.json> --targets <targets.json>` | exists |
| Prototype tests | `python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/test_sponsor_shortlist.py` | exists, 22 tests, offline |
| Persona (fictional) | `scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/persona.bella.json` | exists |
| Break fixtures | `scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/breaks/persona.*.json` | exists (bad date, window closed, late filing, slow hiring) |
| Run output | `course/2026fa/submissions/varnikamujumdar/runs/<as_of>/` (or `<as_of>-2`, … if that folder exists; never overwritten) | written by the prototype |

## Inputs

| Input | Field / format | Label |
|---|---|---|
| Target companies | JSON list of names as the student types them | your-input |
| Program end date | `timeline.program_end`, YYYY-MM-DD | your-input |
| Requested OPT start | `timeline.opt_requested_start`, must be after program end and within the OPT start window | your-input |
| OPT filing date | `timeline.opt_filed`, must fall inside the filing window, or `null` (assume filed on the run date, or when the window opens if later) | your-input |
| EAD wait | `timeline.ead_wait_days` | your-input (see TODO 4) |
| Hiring lag | `timeline.hiring_lag_days`, same for every company | your-input (see TODO 3) |
| OPT filing window / unemployment limit | `timeline.opt_filing_window_before_days` (90), `timeline.opt_start_window_days` (60), `timeline.unemployment_limit_days` (90) | your-input until cited (see TODO 2) |
| Run date | `timeline.as_of` | your-input |

## Steps

1. **G1, input gate.** The prototype checks that the CSV exists and has the required columns, that the persona parses, that every date is valid, that the OPT filing date (if given) falls inside the filing window (90 days before to 60 days after program end), that the requested OPT start is inside the start window, and that the window is not already closed without a filing. If any check fails, it exits 2 and writes nothing.
2. **Resolve names.** Uppercase, strip punctuation, and drop legal suffixes (INC, LLC, CORP…), then require an **exact** match on the result. A miss returns up to 3 prefix "possible matches" for the human, and those are **never** used as evidence.
3. **Sponsorship tier** (rule = your-input, applied to record fields; the p value is sent to the scorer labeled **your-input**):
   - **Proven** (p 0.9): ≥10 approvals, ≥90% approval rate, and at least one software title without a seniority word.
   - **Likely** (p 0.6): sponsors, but its software history is senior-only, it has no software title, it has <10 approvals, or its rate is below 90%.
   - **None** (p 0.0): 0 approvals on record.
   - **Unknown** (no p sent): not in the CSV, ambiguous, or H-1B columns blank.
4. **Timeline factor** (your-input): `clock_start = max(opt_requested_start, opt_filed + ead_wait_days)`, `work_start = max(as_of + hiring_lag_days, clock_start)`, `factor = max(0, 1 − (work_start − clock_start)/unemployment_limit_days)`.
5. **Build `roles.json`.** Liveness is sent **explicitly** as `{factor: 1.0, source: your-input, status: UNCHECKED}`, because the scorer turns a missing liveness into `1.0 [record]`. No `fit` vote is sent.
6. **Score** with the existing scorer, unchanged.
7. **Write** `run.json` (agent) and `report.md` (person).
8. **G2–G4:** human gates, below.

## Phase gates (hard stops)

| Gate | Testable condition | Who clears it, and what they need to see |
|---|---|---|
| **G1 input** | prototype exit code is 0 and `run.json` exists in the output folder it prints | machine; a non-zero exit is a halt, not a warning |
| **G2 visa timeline** (gate) | `run.json` → `timeline.factor` > 0.05 | the student checks the four timeline assumptions in `report.md` against their own I-20 / DSO advice, including the filing window shown in `report.md` |
| **G3 liveness** (gate) | for each Apply row, a human ran `npm run ats:liveness -- <url>` and the result is `active` | the student, per posting; recorded in `logs/runs/2026fa-varnikamujumdar-<n>.md` |
| **G4 release** | a signed line in `logs/runs/2026fa-varnikamujumdar-<n>.md` naming which rows become applications | the student (see TODO 7) for the first live use |

## What it can and can't verify

**Can verify (record):**
- Whether a company name, after normalization, matches exactly one row of the shipped CSV.
- That row's approvals, denials, approval rate, and top sponsored titles, exactly as the CSV states them (CSV sha256 logged).
- Whether any listed software title lacks a seniority word.
- The SOC 15-1252 national median wage in the BLS compact table.

**Can't verify:**
- **Whether a company sponsors when it has no record.** 28,812 of 30,369 CSV rows have no H-1B data, and well-known employers (e.g. DraftKings: blank columns; HubSpot, Wayfair: absent) come back Unknown.
- **Which years the H-1B counts cover.** The CSV's README doesn't say (see TODO 1).
- **Whether a title is actually entry level.** "Software Engineer II" is counted senior; "Member of Technical Staff" isn't recognized as software (see TODO 5).
- **Which company a student meant.** "Notion" vs "NOTION LABS INC" is not matched automatically (see TODO 6).
- **Whether any posting is live.** Not fetched; see G3 (see TODO 8) to feed `ats:liveness` results in.
- **How long this company takes to hire, or how long USCIS takes to issue an EAD.** Both are typed assumptions.
- **Whether the student fits the role.** Not assessed.

## Facts that bite (addressed)

- **Role quality weight is 0:** not relied on; the 15-1252 wage is shown as context only.
- **`bls:local-wage` feeds nothing / fails on a fresh clone:** not used.
- **Only SEC Form D samples ship:** not used. Funding recency comes only from the CSV's `latest_funding_date`, which is carried in `run.json` but not scored.
- **Planned dirs don't exist:** gates point only at the prototype's outputs and `logs/runs/`.
- **`snickerdoodle` CLI is roadmap:** not used.
- **Scorer default (found while building):** a missing liveness becomes `1.0 [record]`. The prototype never leaves it missing. The scorer also has no "unchecked" state, so its own `role-scores.md` calls UNCHECKED liveness "gates healthy" and calls Unknown rows "time better spent elsewhere". `report.md` is the human-facing file and says so.
- **Sensitivity:** with no fit vote, a Proven company scores 0.315 against a 0.30 Apply threshold, so a timeline factor below 0.9524 (0.30 / 0.315), i.e. from the 5th unemployment day, turns every Apply into Consider.

## Output contract

| File | Reader | Contents |
|---|---|---|
| `runs/<as_of>/run.json` | agent | inputs and CSV sha256, tier rule, senior regex, timeline inputs and derived dates, per-company raw CSV fields, match status, possible matches, tier, flags, composite, recommendation, next action |
| `runs/<as_of>/report.md` | person | executive summary, decision table, flags, verified-vs-inferred table, timeline assumptions, sensitivity note |
| `runs/<as_of>/roles.json`, `role-scores.json`, `role-scores.md` | audit only | scorer input and the scorer's own unmodified output. **Not** for deciding: it doesn't know liveness is unchecked |

## Stop conditions and next action per result

| Result | Next action (3-3-2 block) |
|---|---|
| Apply (Proven, gates open) | **Blocked** until G3. If the posting is live, tailor the application (2-hour apply block). |
| Consider (Likely) | Network in first (3-hour networking block): ask a contact whether the team sponsors new-grad SWE. |
| Skip, Unknown | Not a "no". Check the listed possible matches or ask a contact before dropping it. |
| Skip, None | Skip. |
| Skip, timeline gate closed | Stop. Re-run with corrected dates or talk to the DSO; no amount of applying fixes timing. |
| G1 halt | Stop. Fix the input; nothing was written. |

## Open TODOs

1. [TODO: DATA SOURCE] Fiscal-year coverage of the H-1B columns in the 80-days CSV. *Why:* an approval count from 2016 and one from 2025 mean different things for a 2027 start, and the README doesn't say.
2. [TODO: DATA SOURCE] Cite the OPT filing window (90 days before / 60 days after program end) and the 90-day unemployment limit to USCIS / 8 CFR 214.2(f). *Why:* G1 and G2 rest on these numbers, and today they are typed in from memory.
3. [TODO: DATA SOURCE] Per-company hiring lag. *Why:* one lag for every company makes the timeline gate identical across rows, so it can't tell a fast hirer from a slow one.
4. [TODO: DATA SOURCE] USCIS published I-765 (OPT) processing time for `ead_wait_days`. *Why:* the EAD date decides the earliest legal start, and 90 days is a guess.
5. [TODO: DEV] A seniority classifier better than the title regex. *Why:* "Software Engineer II" is counted senior and "Member of Technical Staff" isn't counted as software, which moved Klaviyo from Proven to Likely in the sample run.
6. [TODO: DEV] A human-confirmed alias table for company names (no automatic fuzzy matching). *Why:* "Notion" and "6sense" were lost as Unknown in the sample run although their legal names are in the CSV.
7. [TODO: APPROVE] G4 release sign-off before the first live use. *Why:* nothing becomes an application without a named person choosing it.
8. [TODO: DEV] Read `ats:liveness` results into `roles.json` instead of sending UNCHECKED. *Why:* today the liveness gate is a manual step, and the scorer's own report can't show that it's missing.

## Run-log template (`logs/runs/2026fa-varnikamujumdar-<n>.md`)

```markdown
## YYYY-MM-DD — swe-newgrad-sponsors sample run

- **Recipe:** recipes/cases/2026fa/varnikamujumdar-swe-newgrad-sponsors.md v0.1.0
- **Inputs:** persona <path>; targets <path>; CSV sha256 <first 16>
- **Outputs:** course/2026fa/submissions/varnikamujumdar/runs/<as_of>/ (report.md, run.json, roles.json, role-scores.*)
- **Result:** Apply n · Consider n · Skip n (skip %); tiers Proven n · Likely n · None n · Unknown n; timeline factor x
- **Gates:** G1 machine pass/halt · G2 cleared by <name>/<date> or open · G3 per Apply row: <url> → active/expired/not run · G4 <name>/<date> or open
- **Open issues:** <what didn't work>
```
