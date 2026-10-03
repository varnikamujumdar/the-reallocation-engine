---
owner: varnikamujumdar
term: 2026fa
component: swe-newgrad-sponsors
status: DRAFT   # matches the recipe; 8 typed TODOs open
promoted_to: null
---

# New-grad SWE sponsor shortlist

## Executive summary

This folder holds a small tool for one kind of job seeker: an international master's student on an F-1 visa, about to graduate, who wants an entry-level software engineering job and will need a visa sponsor. Given a list of companies, it looks each one up in a public record of past work-visa approvals, sorts them into proven, likely, none, or unknown sponsors, and checks whether a job started now could begin before the student's post-graduation work permit clock runs out. It then hands everything to the engine's existing scorer for an apply / consider / skip decision. It does **not** check whether any job posting is real and does not judge personal fit. A person has to check both before applying.

## Run it (one command, from the repo root)

```bash
python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/sponsor_shortlist.py \
  --persona scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/persona.bella.json \
  --targets scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/targets.bella.json
```

Writes to `course/2026fa/submissions/varnikamujumdar/runs/<as_of>/`, or to `<as_of>-2`, `-3`, … if that folder already exists, so an earlier run is never overwritten. Pass `--out-dir <folder>` to choose the folder yourself.

| File | For | Written by |
|---|---|---|
| `report.md` | the person | this tool |
| `run.json` | the agent (inputs, CSV sha256, raw fields, labels, rules, results) | this tool |
| `roles.json` | scorer input | this tool |
| `role-scores.json` / `role-scores.md` | audit only (it calls unchecked liveness "gates healthy"; decide from `report.md`) | `scripts/score/role-scorer.mjs` (unchanged) |

## Test (offline, fixtures only)

```bash
python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/test_sponsor_shortlist.py
```

22 tests; exits 0 on pass, 1 on failure. The end-to-end test runs the real scorer locally with `node` (no network).

## Requirements

Python 3.9+ (standard library only), Node 20+. No network access, no API keys.

## Exit codes

- `0` ok
- `2` input gate failed (bad date, missing CSV column, OPT filing date outside the filing window, or the window already closed). Nothing is written.
- `3` scorer failed

## Files

- `sponsor_shortlist.py`: the prototype
- `test_sponsor_shortlist.py`: tests
- `fixtures/persona.bella.json`: **fictional** persona; every value is your-input
- `fixtures/targets.bella.json`: company names as the persona would type them
- `fixtures/mini_80days.csv`: 7 invented rows in the real CSV's column format, used only by tests
- `fixtures/breaks/persona.*.json`: the persona with one deliberate fault each (bad date, window closed, late filing) plus one sensitivity case (slow hiring); used in the worked run's break attempts

Recipe: `recipes/cases/2026fa/varnikamujumdar-swe-newgrad-sponsors.md`
