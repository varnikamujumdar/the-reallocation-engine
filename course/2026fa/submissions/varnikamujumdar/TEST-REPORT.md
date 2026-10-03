# Test report — new-grad SWE sponsor shortlist

## Executive summary

This report records whether the tool actually runs and whether it breaks safely. Before anything was built, the repo's own health checks failed on a fresh laptop for three setup reasons, all fixed with one install command each. After the build, the checks pass, the tool runs on the real data, all 22 offline tests pass, and every named failure case stops with a clear message without writing anything. Everything was also re-run from a fresh clone of the pushed branch, with the same results, and the branch-history privacy scan that CI runs came back clean.

## Toolchain baseline

| Check | Before (fresh clone, 2026-10-03) | After (all new files in place) |
|---|---|---|
| `npm run doctor` | ✓ runnable; no private paths tracked | ✓ runnable; no private paths tracked. *Doctor counts only top-level `recipes/`, not `recipes/cases/`, so it says nothing about the new recipe.* |
| `npm run verify` | ✗ `ModuleNotFoundError: No module named 'yaml'` (fixed: `pip install --user pyyaml`) | ✓ conformance pass; manifest check passed (3 warnings, pre-existing; the two `W2` ones are false positives confirmed with `git check-ignore`) |
| `node scripts/conformance.mjs` on my paths | — | `conformance: 31 files (16 md · 13 json · 2 py)` ✓ all conform |
| `node scripts/pii-scan.mjs` | 1 finding: `[email] package-lock.json` (the `glob` maintainer's public address) | the same single finding, pre-existing in upstream `015843d`; my paths scanned alone: `pii-scan: clean ✓` |

Full setup output: `SETUP-LOG.md`.

## Sample run

```
$ python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/sponsor_shortlist.py --persona scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/persona.bella.json --targets scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/targets.bella.json --out-dir course/2026fa/submissions/varnikamujumdar/runs/2026-10-03
✓ scored 12 roles → Apply 3 · Consider 3 · Skip 6 (skip 50%)
  course/2026fa/submissions/varnikamujumdar/runs/2026-10-03/role-scores.json  +  course/2026fa/submissions/varnikamujumdar/runs/2026-10-03/role-scores.md
✓ tiers [your-input rule on record data]: Likely 3 · None 1 · Proven 3 · Unknown 5
✓ timeline factor [your-input] 1.0 · liveness UNCHECKED (human gate)
  course/2026fa/submissions/varnikamujumdar/runs/2026-10-03/report.md  +  run.json
exit=0
```

## Offline tests

```
$ python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/test_sponsor_shortlist.py
test_F4_halt_writes_nothing (__main__.EndToEnd) ... ok
test_default_output_never_overwrites (__main__.EndToEnd) ... ok
test_full_path_through_real_scorer (__main__.EndToEnd) ... ok
test_missing_column_halts (__main__.EndToEnd) ... ok
test_scorer_failure_exits_3 (__main__.EndToEnd) ... ok
test_near_matches_listed_but_never_used (__main__.Names) ... ok
test_normalize_drops_suffix_case_punctuation (__main__.Names) ... ok
test_F1_absent_company_is_unknown_not_zero (__main__.Tiers) ... ok
test_F2_blank_h1b_columns_is_unknown_without_p (__main__.Tiers) ... ok
test_F3_senior_only_history_is_likely_and_flagged (__main__.Tiers) ... ok
test_F5_zero_approvals_is_none_with_raw_numbers (__main__.Tiers) ... ok
test_low_volume_is_likely (__main__.Tiers) ... ok
test_no_software_title_is_likely_and_flagged (__main__.Tiers) ... ok
test_proven_needs_entry_level_software_title (__main__.Tiers) ... ok
test_F4_bad_date_halts (__main__.Timeline) ... ok
test_F4_window_closed_without_filing_halts (__main__.Timeline) ... ok
test_filing_after_window_halts (__main__.Timeline) ... ok
test_filing_before_window_halts (__main__.Timeline) ... ok
test_late_search_closes_gate (__main__.Timeline) ... ok
test_on_time_search_keeps_gate_open (__main__.Timeline) ... ok
test_sponsorship_p_is_labeled_your_input (__main__.Timeline) ... ok
test_unfiled_opt_assumed_filed_when_window_opens (__main__.Timeline) ... ok

----------------------------------------------------------------------
Ran 22 tests in 0.271s

OK
```

The tests use only `fixtures/mini_80days.csv` (7 invented rows) and call the real scorer locally with `node`. No network access.

## Each failure case exercised

| Case | How | Result |
|---|---|---|
| F1 company not in CSV | real run: HubSpot, Wayfair; test `test_F1_…` | tier Unknown, no `p` sent, Skip with "NOT evidence they don't sponsor" |
| F2 H-1B columns blank | real run: DraftKings; test `test_F2_…` | Unknown, no `p` |
| F3 senior-only history | real run: 1upHealth, Klaviyo; test `test_F3_…` | Likely + flag → Consider |
| F4 bad date / OPT window closed | `fixtures/breaks/persona.bad-date.json`, `persona.window-closed.json`; tests `test_F4_…` | exit 2, "✗ G1 input gate: …", **no output folder created** |
| OPT filing date outside the filing window | `fixtures/breaks/persona.late-filing.json`; tests `test_filing_after_window_halts`, `test_filing_before_window_halts` | exit 2, "outside the OPT filing window 2026-09-24 to 2027-02-21" |
| F5 zero approvals | real run: Mobilio; test `test_F5_…` | None, raw `0.0 / 2.0 / 0.0` shown |
| Missing CSV column | CSV with the header renamed via `sed`; test `test_missing_column_halts` | exit 2, "missing required columns: ['Total Approvals']" |
| Scorer fails | test `test_scorer_failure_exits_3` | exit 3 |

The exact commands and terminal output for every break are in `WORKED-RUN.md` §Verification.

## Files changed

Every path is inside my namespaces. No tracked file is modified.

```
19 files  course/2026fa/submissions/varnikamujumdar/
          (CHANGE-BRIEF, FRICTIONAL, JUSTIFICATION, SETUP-LOG, SOURCES, TEST-REPORT, WORKED-RUN,
           runs/2026-10-03/ ×5, runs/2026-10-03-slow-hiring/ ×5, runs/role-scores.{json,md} from the setup run of the Ch.11 example)
 1 file   logs/runs/2026fa-varnikamujumdar-1.md
 2 files  recipes/cases/2026fa/varnikamujumdar-swe-newgrad-sponsors{.md,.card.md}
10 files  scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/
          (sponsor_shortlist.py, test_sponsor_shortlist.py, README.md, fixtures/ ×3, fixtures/breaks/ ×4)
```

`git diff --stat origin/main...HEAD` in the clean clone (commit `052820b`) ends with `32 files changed, 4515 insertions(+)`, with no deletions and no file outside the four namespaces above. Full output below.

## Clean-checkout run

Run on 2026-10-03 by the AI assistant: a fresh `git clone` of `contrib/2026fa-varnikamujumdar-swe-newgrad-sponsors` from GitHub into an empty scratch folder, at HEAD `052820b68d839863472e46104582dbb8e9e91017`. (PyYAML was already installed for the user account from setup, so `verify` didn't hit the `yaml` error here.)

```
$ npm run doctor
  ✓ no private/PII paths are tracked
  environment: ✓ runnable
$ npm run verify
conformance: 169 files (88 md · 38 py · 30 js · 9 json · 4 sh)
✓ all conform (machine half of P4). Adequacy is still the human gate.
✓ manifest check passed (3 warnings)
$ python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/test_sponsor_shortlist.py
Ran 22 tests in 0.097s

OK
$ python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/sponsor_shortlist.py --persona scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/persona.bella.json --targets scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/targets.bella.json
✓ scored 12 roles → Apply 3 · Consider 3 · Skip 6 (skip 50%)
  course/2026fa/submissions/varnikamujumdar/runs/2026-10-03-2/role-scores.json  +  course/2026fa/submissions/varnikamujumdar/runs/2026-10-03-2/role-scores.md
✓ tiers [your-input rule on record data]: Likely 3 · None 1 · Proven 3 · Unknown 5
✓ timeline factor [your-input] 1.0 · liveness UNCHECKED (human gate)
  course/2026fa/submissions/varnikamujumdar/runs/2026-10-03-2/report.md  +  run.json
exit=0
$ git diff --stat origin/main...HEAD
 .../submissions/varnikamujumdar/CHANGE-BRIEF.md    | 109 +++++
 .../submissions/varnikamujumdar/FRICTIONAL.md      |  66 +++
 .../submissions/varnikamujumdar/JUSTIFICATION.md   |  42 ++
 .../submissions/varnikamujumdar/SETUP-LOG.md       |  57 +++
 .../2026fa/submissions/varnikamujumdar/SOURCES.md  |  59 +++
 .../submissions/varnikamujumdar/TEST-REPORT.md     | 114 +++++
 .../submissions/varnikamujumdar/WORKED-RUN.md      | 196 ++++++++
 .../runs/2026-10-03-slow-hiring/report.md          |  64 +++
 .../runs/2026-10-03-slow-hiring/role-scores.json   | 415 ++++++++++++++++
 .../runs/2026-10-03-slow-hiring/role-scores.md     |  22 +
 .../runs/2026-10-03-slow-hiring/roles.json         | 237 +++++++++
 .../runs/2026-10-03-slow-hiring/run.json           | 528 +++++++++++++++++++++
 .../varnikamujumdar/runs/2026-10-03/report.md      |  64 +++
 .../runs/2026-10-03/role-scores.json               | 415 ++++++++++++++++
 .../varnikamujumdar/runs/2026-10-03/role-scores.md |  22 +
 .../varnikamujumdar/runs/2026-10-03/roles.json     | 237 +++++++++
 .../varnikamujumdar/runs/2026-10-03/run.json       | 528 +++++++++++++++++++++
 .../varnikamujumdar/runs/role-scores.json          | 241 ++++++++++
 .../varnikamujumdar/runs/role-scores.md            |  15 +
 logs/runs/2026fa-varnikamujumdar-1.md              |   8 +
 .../varnikamujumdar-swe-newgrad-sponsors.card.md   |  72 +++
 .../2026fa/varnikamujumdar-swe-newgrad-sponsors.md | 145 ++++++
 .../varnikamujumdar-swe-newgrad-sponsors/README.md |  59 +++
 .../fixtures/breaks/persona.bad-date.json          |  21 +
 .../fixtures/breaks/persona.late-filing.json       |  21 +
 .../fixtures/breaks/persona.slow-hiring.json       |  21 +
 .../fixtures/breaks/persona.window-closed.json     |  21 +
 .../fixtures/mini_80days.csv                       |   8 +
 .../fixtures/persona.bella.json                    |  21 +
 .../fixtures/targets.bella.json                    |  14 +
 .../sponsor_shortlist.py                           | 487 +++++++++++++++++++
 .../test_sponsor_shortlist.py                      | 186 ++++++++
 32 files changed, 4515 insertions(+)
$ node scripts/pii-scan.mjs --diff origin/main
pii-scan: clean ✓
exit=0
```

Note what the clean run shows: the clone already contained the committed `runs/2026-10-03/`, so the tool wrote to `runs/2026-10-03-2/` instead of overwriting it. That's the no-overwrite rule working on a real checkout. Still **not tested:** Python 3.12, which CI uses; the clone ran on 3.9.6.

## What the gates require a human to judge

- **G2 timeline:** whether the typed assumptions (EAD wait 90 days, hiring lag 56 days, the 90-days-before / 60-days-after OPT filing window, the 90-day unemployment limit) are right for this student. The tool can't know, and a 120-day hiring lag alone removes every Apply.
- **G3 liveness:** for each Apply row, whether a real, open, new-grad posting exists and whether its start date is compatible. Example: Stripe's US early-career posting says "Immediate Start". **Not cleared in this run.** The scorer's own `role-scores.md` will still say "gates healthy", because it has no "unchecked" state; decide from `report.md`.
- **G4 release:** which rows become applications, and which Unknown / Consider rows become networking targets instead.
