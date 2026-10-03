# New-grad SWE sponsor shortlist — human card

## Executive summary

This card is the one-page version of a recipe that checks a list of companies against public records of past work-visa sponsorship and against the student's own graduation and work-permit dates. Read it before trusting the tool's apply / consider / skip list. It says what the tool actually checked, what it only assumed, and the one step (checking the real job posting) that a person must always do before applying.

## About this card

**Audience:** an international CS master's student on F-1, a few months before graduation, OPT not yet approved, deciding where to spend limited application time on entry-level software engineering roles.
**Agent twin:** `recipes/cases/2026fa/varnikamujumdar-swe-newgrad-sponsors.md` (DRAFT, v0.1.0)

## Purpose

Answer two questions from records: did this company sponsor visas for **non-senior** software engineers, and can a hiring process started today end in a start date I'm allowed to work on? If the record is missing, the answer is **unknown**, not no.

## What it can verify

- A typed company name matches exactly one CSV row after removing case, punctuation, and legal suffixes. A miss is `not-in-csv`, an exact duplicate is `ambiguous`; neither is guessed.
- That row's H-1B approvals, denials, approval rate, and top sponsored titles, as the CSV states them (file hash logged).
- Whether any listed software title lacks a seniority word.

## What it cannot verify

- Whether a company with **no record** sponsors. Most of the CSV has no H-1B data; DraftKings, HubSpot, and Wayfair come back Unknown.
- Which years the H-1B counts cover. The source doesn't say.
- Whether "Software Engineer II" is entry level. The rule counts it as senior.
- Whether any posting is real or open. **Never checked.**
- Hiring speed, USCIS processing time, and the OPT filing-window rules. All typed in, not cited to a record yet.
- Personal fit. Not assessed.

## Dependencies

- Python 3.9+ (standard library), Node 20+. No network.
- `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv`
- `data/bls/compact/soc_occupation_compact.csv` (context only)
- `scripts/score/role-scorer.mjs` (unchanged)

## Annotated commands

Sample run (expected: 12 companies → Apply 3 · Consider 3 · Skip 6; 5 Unknown):

```bash
python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/sponsor_shortlist.py \
  --persona scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/persona.bella.json \
  --targets scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/fixtures/targets.bella.json
```

Offline tests (expected: 22 tests, OK):

```bash
python3 scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/test_sponsor_shortlist.py
```

Before acting on any Apply row (gate G3; expected `active`):

```bash
npm run ats:liveness -- <the actual posting URL>
```

## What it produces

`course/2026fa/submissions/varnikamujumdar/runs/<as_of>/report.md` for you, and `run.json` for the agent. The folder becomes `<as_of>-2`, … if it already exists, so nothing is overwritten. It also holds the scorer's own `role-scores.md`, which is an audit file only: it calls unchecked liveness "gates healthy" because the scorer has no "unchecked" state. Decide from `report.md`.

## How to read a result

| You see | It means | Do this |
|---|---|---|
| Apply — BLOCKED | proven new-grad-level sponsor, timing fine, posting unchecked | check the posting, then tailor (apply block) |
| Consider | sponsors, but senior-only, low volume, or no software titles | network in and ask about new-grad sponsorship |
| Skip, Unknown | no record, which is not a "no" | check possible matches or ask a contact |
| Skip, None | 0 approvals on record | skip |
| exit 2, nothing written | an input is wrong, the OPT filing date is outside the filing window, or the window has closed | fix the input, or talk to your DSO |
