#!/usr/bin/env python3
"""Offline tests for sponsor_shortlist.py. Fixtures only, no network.

Run from the repo root:
  python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/test_sponsor_shortlist.py

The end-to-end test calls the real scorer (scripts/score/role-scorer.mjs) with
node, which is local, not a network call. Exits 0 when all pass, 1 otherwise.
"""

import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sponsor_shortlist as ss  # noqa: E402

FIX = HERE / "fixtures"
MINI_CSV = FIX / "mini_80days.csv"
PERSONA = json.loads((FIX / "persona.bella.json").read_text())


def index():
    rows, _ = ss.load_csv(MINI_CSV)
    return ss.build_index(rows)


class Tiers(unittest.TestCase):
    def tier_of(self, typed):
        m = ss.lookup(typed, index())
        return m, (ss.classify(m["row"]) if m["row"] else None)

    def test_proven_needs_entry_level_software_title(self):
        _, s = self.tier_of("Alpha Software")
        self.assertEqual((s["tier"], s["p"]), ("Proven", 0.9))

    def test_F1_absent_company_is_unknown_not_zero(self):
        m, s = self.tier_of("Omega Nowhere")
        self.assertEqual(m["status"], "not-in-csv")
        self.assertIsNone(s)

    def test_F2_blank_h1b_columns_is_unknown_without_p(self):
        _, s = self.tier_of("Gamma Blank Corp")
        self.assertEqual(s["tier"], "Unknown")
        self.assertIsNone(s["p"])

    def test_F3_senior_only_history_is_likely_and_flagged(self):
        _, s = self.tier_of("Beta Senior Labs")
        self.assertEqual(s["tier"], "Likely")
        self.assertIn("senior-only software sponsorship history", s["flags"])

    def test_F5_zero_approvals_is_none_with_raw_numbers(self):
        _, s = self.tier_of("Delta Zero LLC")
        self.assertEqual((s["tier"], s["p"]), ("None", 0.0))
        self.assertEqual(s["raw"]["Total Denials"], "2.0")

    def test_low_volume_is_likely(self):
        _, s = self.tier_of("epsilon small")
        self.assertEqual(s["tier"], "Likely")

    def test_no_software_title_is_likely_and_flagged(self):
        _, s = self.tier_of("Zeta Health")
        self.assertEqual(s["tier"], "Likely")
        self.assertTrue(any("no software title" in f for f in s["flags"]))


class Names(unittest.TestCase):
    def test_normalize_drops_suffix_case_punctuation(self):
        self.assertEqual(ss.normalize("Alpha Software, Inc."), "ALPHA SOFTWARE")
        self.assertEqual(ss.normalize("1upHealth"), ss.normalize("1UPHEALTH INC"))

    def test_near_matches_listed_but_never_used(self):
        m = ss.lookup("Zeta", index())
        self.assertEqual(m["status"], "not-in-csv")
        self.assertIsNone(m["row"])
        self.assertEqual(m["possible_matches"], ["ZETA HEALTH INC", "ZETA HEALTHCARE INC"])


class Timeline(unittest.TestCase):
    def dates(self, **over):
        t = copy.deepcopy(PERSONA["timeline"])
        t.update(over)
        return ss.validate_timeline(t)

    def test_on_time_search_keeps_gate_open(self):
        self.assertEqual(ss.timeline_factor(self.dates())["factor"], 1.0)

    def test_late_search_closes_gate(self):
        # Searching from the day the clock starts with an 8-week lag and a 30-day limit: gate shut.
        tl = ss.timeline_factor(self.dates(as_of="2027-01-13", unemployment_limit_days=30))
        self.assertEqual(tl["factor"], 0.0)

    def test_F4_bad_date_halts(self):
        with self.assertRaises(ss.GateError):
            self.dates(program_end="not-a-date")

    def test_F4_window_closed_without_filing_halts(self):
        with self.assertRaises(ss.GateError):
            self.dates(as_of="2027-06-01", opt_filed=None)

    def test_filing_after_window_halts(self):
        with self.assertRaises(ss.GateError):
            self.dates(opt_filed="2027-05-01")

    def test_filing_before_window_halts(self):
        with self.assertRaises(ss.GateError):
            self.dates(opt_filed="2026-01-01")

    def test_unfiled_opt_assumed_filed_when_window_opens(self):
        # Run date is before the window opens (2026-09-24), so filing is assumed on the opening day.
        tl = ss.timeline_factor(self.dates(as_of="2026-08-01", opt_filed=None))
        self.assertEqual(tl["opt_filed_assumed"], "2026-09-24")

    def test_sponsorship_p_is_labeled_your_input(self):
        entry = {"typed": "x", "csv_name": None, "sponsorship": {"tier": "Proven", "p": 0.9}}
        role = ss.build_role(entry, {"factor": 1.0})
        self.assertEqual(role["sponsorship"]["source"], "your-input")


class EndToEnd(unittest.TestCase):
    def run_tool(self, persona, targets, csv=MINI_CSV):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "persona.json").write_text(json.dumps(persona))
        (tmp / "targets.json").write_text(json.dumps(targets))
        out = tmp / "out"
        argv = ["--persona", str(tmp / "persona.json"), "--targets", str(tmp / "targets.json"),
                "--csv", str(csv), "--out-dir", str(out)]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = ss.main(argv)
        return code, out

    def test_full_path_through_real_scorer(self):
        code, out = self.run_tool(PERSONA, ["Alpha Software", "Beta Senior Labs", "Gamma Blank", "Omega Nowhere"])
        self.assertEqual(code, 0)
        for f in ("roles.json", "role-scores.json", "run.json", "report.md"):
            self.assertTrue((out / f).exists(), f)
        roles = json.loads((out / "roles.json").read_text())
        for r in roles:  # liveness is never left for the scorer to default to "record"
            self.assertEqual(r["liveness"], {"factor": 1.0, "source": "your-input", "status": "UNCHECKED"})
            self.assertIn(r["timeline"]["source"], ("your-input",))
        unknown = [r for r in roles if r["sponsorship"]["tier"] == "Unknown"]
        self.assertTrue(unknown and all("p" not in r["sponsorship"] for r in unknown))
        recs = {r["company"]: r["recommendation"] for r in json.loads((out / "role-scores.json").read_text())["roles"]}
        self.assertEqual(recs["ALPHA SOFTWARE INC"], "Apply")
        self.assertEqual(recs["BETA SENIOR LABS LLC"], "Consider")
        self.assertIn("BLOCKED: liveness unchecked", (out / "report.md").read_text())

    def test_F4_halt_writes_nothing(self):
        bad = copy.deepcopy(PERSONA)
        bad["timeline"]["program_end"] = "2025-13-45"
        code, out = self.run_tool(bad, ["Alpha Software"])
        self.assertEqual(code, 2)
        self.assertFalse(out.exists())

    def test_scorer_failure_exits_3(self):
        real = ss.SCORER
        ss.SCORER = HERE / "fixtures" / "no-such-scorer.mjs"
        try:
            code, _ = self.run_tool(PERSONA, ["Alpha Software"])
        finally:
            ss.SCORER = real
        self.assertEqual(code, 3)

    def test_default_output_never_overwrites(self):
        base = Path(tempfile.mkdtemp()) / "2026-10-03"
        base.mkdir()
        self.assertEqual(ss.next_free_dir(base).name, "2026-10-03-2")

    def test_missing_column_halts(self):
        tmp = Path(tempfile.mkdtemp())
        broken = tmp / "broken.csv"
        broken.write_text(MINI_CSV.read_text().replace("Total Approvals", "Approvals", 1))
        code, out = self.run_tool(PERSONA, ["Alpha Software"], csv=broken)
        self.assertEqual(code, 2)
        self.assertFalse(out.exists())


if __name__ == "__main__":
    result = unittest.main(exit=False, verbosity=2).result
    sys.exit(0 if result.wasSuccessful() else 1)
