# Worked run — new-grad SWE sponsor shortlist, 2026-10-03

## Executive summary

This document shows the tool running once on a realistic scenario: a fictional international student checking 12 companies they might apply to for an entry-level software engineering job. It's worth reading because it shows the actual output, which parts are backed by public records and which are the student's own assumptions, how the output was checked by hand, and five deliberate attempts to break the tool. The run kept 3 companies as "apply, but only after checking the posting", sent 3 to networking, and skipped 6, five of them because no visa record exists rather than because the company refuses to sponsor. A spot check outside the tool found that two of the three "apply" companies had no new-grad posting open that day.

## Inputs

- **Persona (fictional, all your-input):** `scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/persona.bella.json`. Bella, F-1, MS CS (STEM), program ends 2026-12-23, OPT filing planned 2026-10-15, requested OPT start 2026-12-24, assumed EAD wait 90 days, assumed hiring lag 56 days, OPT filing window 90 days before to 60 days after program end, run date 2026-10-03.
- **Targets (your-input):** Stripe, Figma, Notion, Datadog, Klaviyo, 1upHealth, 6sense, DraftKings, HubSpot, Wayfair, Braze, Mobilio. Typed the way a student would, not as legal names. *Chosen after browsing the CSV; see FRICTIONAL.md.*
- **Data (record):** `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv`, 30,369 rows, sha256 `eccdee2addf472b1…` (full hash in `runs/2026-10-03/run.json`). The full CSV ships with the repo; no SEC Form D samples were used.

## Command and real output

```
$ python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/sponsor_shortlist.py --persona scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/persona.bella.json --targets scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/targets.bella.json --out-dir course/2026fa/submissions/varnikamujumdar/runs/2026-10-03
✓ scored 12 roles → Apply 3 · Consider 3 · Skip 6 (skip 50%)
  course/2026fa/submissions/varnikamujumdar/runs/2026-10-03/role-scores.json  +  course/2026fa/submissions/varnikamujumdar/runs/2026-10-03/role-scores.md
✓ tiers [your-input rule on record data]: Likely 3 · None 1 · Proven 3 · Unknown 5
✓ timeline factor [your-input] 1.0 · liveness UNCHECKED (human gate)
  course/2026fa/submissions/varnikamujumdar/runs/2026-10-03/report.md  +  run.json
exit=0
```

(`--out-dir` is given here so this saved run stays at a fixed path. Without it, the tool writes to `runs/<as_of>/`, or to `runs/<as_of>-2/` and so on if that folder already exists, so it never overwrites an earlier run.)

Decision table, copied from `runs/2026-10-03/report.md`:

| Company (as typed) | Matched CSV name | Tier | Approvals / denials / rate | Composite | Decision |
|---|---|---|---|---|---|
| Stripe | STRIPE INC | Proven | 1250.0 / 22.0 / 98.27% | 0.315 | Apply — BLOCKED: liveness unchecked |
| Figma | FIGMA INC | Proven | 188.0 / 2.0 / 98.95% | 0.315 | Apply — BLOCKED: liveness unchecked |
| Datadog | DATADOG INC | Proven | 340.0 / 0.0 / 100.00% | 0.315 | Apply — BLOCKED: liveness unchecked |
| Klaviyo | KLAVIYO INC | Likely | 154.0 / 4.0 / 97.47% | 0.210 | Consider |
| 1upHealth | 1UPHEALTH INC | Likely | 12.0 / 0.0 / 100.00% | 0.210 | Consider |
| Braze | BRAZE INC | Likely | 50.0 / 2.0 / 96.15% | 0.210 | Consider |
| Notion | *not-in-csv* (possible: NOTION LABS INC; NOTIONAL FINANCE INC, not used) | Unknown | — | 0.000 | Skip |
| 6sense | *not-in-csv* (possible: 6SENSE INSIGHTS INC, not used) | Unknown | — | 0.000 | Skip |
| DraftKings | DRAFTKINGS INC | Unknown | — / — / — | 0.000 | Skip |
| HubSpot | *not-in-csv* | Unknown | — | 0.000 | Skip |
| Wayfair | *not-in-csv* | Unknown | — | 0.000 | Skip |
| Mobilio | MOBILIO LLC | None | 0.0 / 2.0 / 0.00% | 0.000 | Skip |

The scorer's own `role-scores.md` says "gates healthy" for the three Apply rows and "time is better spent elsewhere" for the Unknown rows. That's because the existing scorer has no "unchecked" state. `report.md` is the file that carries the BLOCKED and "not a no" labels, and it says so.

## Verified vs inferred

| Line | Value | Label |
|---|---|---|
| Stripe / Figma / Datadog / Klaviyo / 1upHealth / Braze / Mobilio approvals, denials, rate | as in the CSV | **record** |
| Top sponsored titles (e.g. Klaviyo: 'Software Engineer II', 'Senior Software Engineer', …) | as in the CSV | **record** |
| "not-in-csv" for Notion, 6sense, HubSpot, Wayfair | no normalized exact match | **record** (absence in the file), which is *not* a claim about the company |
| DraftKings blank H-1B columns | as in the CSV | **record** (blank) |
| Tier (Proven / Likely / None / Unknown) | my rule: ≥10 approvals, ≥90% rate, one non-senior software title | **your-input** rule applied to record fields |
| Senior-title word list (senior, sr, staff, principal, lead, manager, director, architect, head, vp, ii, iii, iv) | my design | **your-input** |
| Sponsorship p 0.9 / 0.6 / 0.0 | copied from the Proven/Likely examples in `data/examples/ch11-roles.json`; sent to the scorer labeled your-input | **your-input** |
| Timeline factor 1.0 (EAD estimate 2027-01-13, earliest work start 2027-01-13, 0 unemployment days) | computed from persona dates | **your-input** |
| OPT filing window (90 days before / 60 days after program end), 90-day unemployment limit | typed in, not cited to a record yet | **your-input** |
| Liveness 1.0 | sent so the scorer can't default it; status UNCHECKED | **your-input**, not verified |
| Fit | not sent | none (no record, not guessed) |
| SOC 15-1252 median $133,080 (OEWS 2024) | BLS compact CSV, context only | **record** |
| Composite and Apply/Consider/Skip | `scripts/score/role-scorer.mjs`, unchanged | computed from the above |
| **model-judgment** | none. No value in this run came from a language model | — |

## Verification

**1. Hand cross-check against the source CSV**, parsed with Python's `csv` module:

```
DRAFTKINGS INC | approvals '' | denials '' | rate ''
KLAVIYO INC | approvals '154.0' | denials '4.0' | rate '97.46835443037976'
MOBILIO LLC | approvals '0.0' | denials '2.0' | rate '0.0'
STRIPE INC | approvals '1250.0' | denials '22.0' | rate '98.27044025157232'
Stripe | run.json raw: {'Total Approvals': '1250.0', 'Total Denials': '22.0', 'Approval_Rate': '98.27044025157232'} | tier Proven | Apply
Klaviyo | run.json raw: {'Total Approvals': '154.0', 'Total Denials': '4.0', 'Approval_Rate': '97.46835443037976'} | tier Likely | Consider
DraftKings | run.json raw: {'Total Approvals': '', 'Total Denials': '', 'Approval_Rate': ''} | tier Unknown | Skip
Mobilio | run.json raw: {'Total Approvals': '0.0', 'Total Denials': '2.0', 'Approval_Rate': '0.0'} | tier None | Skip
```

All four match. The first attempt used `grep | cut -d,` and printed the wrong columns, because the CSV has commas inside quoted fields. See FRICTIONAL.md.

**2. Tests:** 22 tests, `OK` (full list in TEST-REPORT.md).

**3. Deliberate breaks.** Each persona file is saved in `fixtures/breaks/`, so every command below can be re-run as written:

```
$ python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/sponsor_shortlist.py --persona scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/breaks/persona.bad-date.json --targets scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/targets.bella.json
✗ G1 input gate: timeline.program_end is not a YYYY-MM-DD date: '2026-13-40'
  nothing written.
exit=2

$ python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/sponsor_shortlist.py --persona scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/breaks/persona.window-closed.json --targets scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/targets.bella.json
✗ G1 input gate: program ended 2026-12-23 and the 60-day window to start OPT closed 2027-02-21; no OPT filing recorded. This tool cannot help — talk to your DSO.
  nothing written.
exit=2

$ python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/sponsor_shortlist.py --persona scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/breaks/persona.late-filing.json --targets scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/targets.bella.json
✗ G1 input gate: opt_filed 2027-05-01 is outside the OPT filing window 2026-09-24 to 2027-02-21 (90 days before program end to 60 days after)
  nothing written.
exit=2

$ sed '1s/Total Approvals/Approvals/' data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv > /tmp/broken-80days.csv
$ python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/sponsor_shortlist.py --persona scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/persona.bella.json --targets scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/targets.bella.json --csv /tmp/broken-80days.csv
✗ G1 input gate: 80-days CSV is missing required columns: ['Total Approvals']
  nothing written.
exit=2

$ python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/sponsor_shortlist.py --persona scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/breaks/persona.slow-hiring.json --targets scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/targets.bella.json --out-dir course/2026fa/submissions/varnikamujumdar/runs/2026-10-03-slow-hiring
✓ scored 12 roles → Apply 0 · Consider 3 · Skip 9 (skip 75%)
  course/2026fa/submissions/varnikamujumdar/runs/2026-10-03-slow-hiring/role-scores.json  +  course/2026fa/submissions/varnikamujumdar/runs/2026-10-03-slow-hiring/role-scores.md
✓ tiers [your-input rule on record data]: Likely 3 · None 1 · Proven 3 · Unknown 5
✓ timeline factor [your-input] 0.8 · liveness UNCHECKED (human gate)
  course/2026fa/submissions/varnikamujumdar/runs/2026-10-03-slow-hiring/report.md  +  run.json
exit=0
```

The last one is a sensitivity check, not a crash. Changing one typed guess (hiring lag 120 days instead of 56) removed every Apply. The offer start of 2027-01-31 against a clock start of 2027-01-13 is 18 days, so 1 − 18/90 = 0.8, and 0.9 × 0.35 × 0.8 = 0.252 < 0.30.

The late-filing break exists because an independent review found that the first version accepted an OPT filing date outside the legal window and still said Apply. See "Broke during testing, fixed".

**4. Mutation check on the tests.** Each change was made in memory only (no file changed) and run separately:

| Mutant | Tests that failed |
|---|---|
| senior-title filter disabled | `test_F3_senior_only_history_is_likely_and_flagged`, `test_full_path_through_real_scorer` (2 of 22) |
| Unknown companies silently given p = 0.0 | `test_full_path_through_real_scorer` (1 of 22) |
| OPT filing date ignored | `test_filing_after_window_halts`, `test_filing_before_window_halts`, `test_late_search_closes_gate` (3 of 22) |

So the tests catch each of these mistakes.

**5. Outside the tool: the public job boards** (an observation, **not** a gate clearance). On 2026-10-03 the AI assistant ran this command once in the session. The raw responses weren't saved, so the result can't be reproduced exactly; job boards change daily.

```
$ for b in stripe figma datadog; do curl -s "https://boards-api.greenhouse.io/v1/boards/$b/jobs" | python3 -c "...filter titles matching new grad|university|graduate|early career|entry AND engineer|software|developer..."; done
stripe: 715 jobs, 9 new-grad SWE-like
   Software Engineer, Early Career — Immediate Start | San Francisco, Seattle, New York | https://stripe.com/jobs/search?gh_jid=8212508
figma: 162 jobs, 0 new-grad SWE-like
datadog: 445 jobs, 0 new-grad SWE-like
```

Two of three "Apply" companies had no new-grad engineering posting open that day. Gate G3 (a human running `npm run ats:liveness` on a specific posting) was **not** cleared in this run.

## Reflection

**What worked**
- Unknown stayed unknown. Five companies came back with no p value and a label saying absence is not a "no".
- No failure case invented a value. The data cases (company missing, blank visa columns, senior-only history, zero approvals) came back as Unknown, Likely or None rows, and the input cases (bad date, OPT window closed, filing date outside the window, damaged CSV) halted with exit 2 and wrote nothing.
- The existing scorer was used unchanged.

**What the recipe or prototype got wrong or missed**
- **§7.1 came true.** Klaviyo lists "Software Engineer II", which the senior word list treats as senior, so Klaviyo landed in Likely.
- **§7.2 came true.** "Notion" and "6sense" weren't matched. The right legal names were listed as possible matches, but a student who doesn't read the flags loses two real sponsors.
- **The timeline factor didn't discriminate between companies at all.** It was 1.0 for all 12 because one hiring lag applies to everyone. Meanwhile the scoring is so tight with no fit vote (0.315 vs 0.30) that 5 days of unemployment flips every Apply.
- **The first version let an impossible OPT filing date through.** Found by an independent review, then fixed and tested.
- **Not predicted:** the existing scorer turns a missing liveness into `1.0 [record]`, and its own report calls unchecked liveness "healthy". The prototype works around the first; the second is documented, not fixable from my namespace.
- **Not modeled:** "Immediate Start" in Stripe's posting. The tool assumes any start date after EAD approval is fine.

**One concrete next improvement**
Add a human-confirmed alias file (`fixtures/aliases.json`, mapping "Notion" → "NOTION LABS INC") that the lookup checks after the exact match and labels `your-input`. That recovers the two lost sponsors without automatic fuzzy matching.

## Attestation

- Recipe: varnikamujumdar-swe-newgrad-sponsors v0.1.0
- By: Varnika Mujumdar · 2026-10-03. *After the review fixes, Varnika personally ran three of the rows below on 2026-10-03, on the final code: the test suite (22 tests, OK in 0.302s), the sample command with `--out-dir /tmp/bella-check` (Apply 3 · Consider 3 · Skip 6; tiers Likely 3 · None 1 · Proven 3 · Unknown 5; timeline 1.0), and the late-filing break (`✗ G1 input gate: opt_filed 2027-05-01 is outside the OPT filing window 2026-09-24 to 2027-02-21 …  nothing written.`). The other rows were executed by the AI assistant in Varnika's session.*

### Tested

| Ran | Saw | Expected |
|---|---|---|
| the one documented command, full CSV | Apply 3 · Consider 3 · Skip 6; Proven 3 · Likely 3 · None 1 · Unknown 5; exit 0 | a decision per company, ≥50% skipped, no invented values |
| `test_sponsor_shortlist.py` | 22 tests, OK | all pass offline |
| hand check: Stripe, Klaviyo, DraftKings, Mobilio vs the CSV | raw values identical | identical |
| **break:** `fixtures/breaks/persona.bad-date.json` | exit 2, "not a YYYY-MM-DD date", nothing written | halt, nothing written |
| **break:** `persona.window-closed.json` | exit 2, "window … closed 2027-02-21" | halt, nothing written |
| **break:** `persona.late-filing.json` | exit 2, "outside the OPT filing window" | halt, nothing written |
| **break:** CSV with the `Total Approvals` header renamed | exit 2, "missing required columns" | halt, nothing written |
| **break:** `persona.slow-hiring.json` | factor 0.8; Apply 0 · Consider 3 · Skip 9 | the decision depends visibly on the assumption |
| three in-memory mutants, one at a time | 2, 1, and 3 tests failed respectively | each mutant detected |
| `node scripts/conformance.mjs` on all new paths; `npm run verify` | all conform; manifest check passed | pass |

### Did not test
- Gate G3: `npm run ats:liveness` on any posting from this run's Apply list.
- Any persona other than Bella, and any non-SWE role.
- Very long target lists (the whole CSV) or non-ASCII company names.
- Whether the 90 / 60 / 90-day OPT constants are correct. Not checked against USCIS.
- Running without `node` installed: the scorer call would raise a Python error instead of a clean exit 3, and `roles.json` is written before the scorer runs, so a failed run leaves that one file behind.
- A run on Python 3.12 (CI's version); only 3.9.6 was used here.
- (Since done: a run from a clean clone of the pushed branch at `052820b` gave the same results; see TEST-REPORT.md.)

### Broke during testing, fixed
- **OPT filing date not checked** (found by an independent AI review). A filing date of 2027-05-01, four months after graduation, still gave timeline 1.0 and Apply. Fixed with a filing-window check in `validate_timeline`, two tests, and a break fixture.
- **Sponsorship p was labeled `record`** although 0.9 / 0.6 / 0.0 come from my rule. Relabeled `your-input`, with a `basis` field naming the record fields. Test `test_sponsorship_p_is_labeled_your_input`.
- **Default output could overwrite an earlier run.** It now goes to the next free folder (`<as_of>-2`, …). Test `test_default_output_never_overwrites`.
- **No test for a scorer failure** (exit 3). Added `test_scorer_failure_exits_3`.
- **Console output** printed an absolute path containing the local username → changed to repo-relative paths.
- **The CHANGE-BRIEF's F4 said "halt if the program end is in the past".** That would wrongly block a student still inside the OPT start window, so the build halts only once the window has closed. Recorded under Revisions in CHANGE-BRIEF.md.
- **The recipe repeated `[TODO]` markers** (16 markers vs `todos_open: 8`) → cross-references changed to "(see TODO n)".
