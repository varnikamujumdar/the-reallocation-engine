# New-grad SWE sponsor shortlist — Bella — 2026-10-03

## Executive summary

This is a shortlist of 12 companies for a fictional international student finishing a master's in computer science on 2026-12-23 who wants an entry-level software engineering job and will need visa sponsorship. Each company was looked up in a public list of past work-visa approvals, and the student's own dates were used to check whether a job could start in time.

Result: **0 apply, 3 consider, 9 skip** (75% skipped). No job posting was checked. Every "apply" stays blocked until a person confirms the posting is real and open. 5 companies had no visa record at all, which means *unknown*, not *does not sponsor*.

## Decisions

| Company (as typed) | Matched CSV name [record] | Tier [your-input rule] | Approvals / denials / rate [record] | Composite | Decision | Next action |
|---|---|---|---|---|---|---|
| Stripe | STRIPE INC | Proven | 1250.0 / 22.0 / 98.27% | 0.252 | **Consider** | Network in first (3-hour block): ask whether they sponsor *new-grad* SWE roles |
| Figma | FIGMA INC | Proven | 188.0 / 2.0 / 98.95% | 0.252 | **Consider** | Network in first (3-hour block): ask whether they sponsor *new-grad* SWE roles |
| Notion | *not-in-csv* (possible: NOTION LABS INC; NOTIONAL FINANCE INC — not used) | Unknown | — | 0.000 | **Skip** | No H-1B record. That is NOT evidence they don't sponsor; check possible matches or ask a contact before dropping |
| Datadog | DATADOG INC | Proven | 340.0 / 0.0 / 100.00% | 0.252 | **Consider** | Network in first (3-hour block): ask whether they sponsor *new-grad* SWE roles |
| Klaviyo | KLAVIYO INC | Likely | 154.0 / 4.0 / 97.47% | 0.168 | **Skip** | Skip |
| 1upHealth | 1UPHEALTH INC | Likely | 12.0 / 0.0 / 100.00% | 0.168 | **Skip** | Skip |
| 6sense | *not-in-csv* (possible: 6SENSE INSIGHTS INC — not used) | Unknown | — | 0.000 | **Skip** | No H-1B record. That is NOT evidence they don't sponsor; check possible matches or ask a contact before dropping |
| DraftKings | DRAFTKINGS INC | Unknown | — / — / — | 0.000 | **Skip** | No H-1B record. That is NOT evidence they don't sponsor; check possible matches or ask a contact before dropping |
| HubSpot | *not-in-csv* | Unknown | — | 0.000 | **Skip** | No H-1B record. That is NOT evidence they don't sponsor; check possible matches or ask a contact before dropping |
| Wayfair | *not-in-csv* | Unknown | — | 0.000 | **Skip** | No H-1B record. That is NOT evidence they don't sponsor; check possible matches or ask a contact before dropping |
| Braze | BRAZE INC | Likely | 50.0 / 2.0 / 96.15% | 0.168 | **Skip** | Skip |
| Mobilio | MOBILIO LLC | None | 0.0 / 2.0 / 0.00% | 0.000 | **Skip** | Skip |

### Flags per company

- **Notion**: no unique CSV row (not-in-csv)
- **Klaviyo**: senior-only software sponsorship history
- **1upHealth**: senior-only software sponsorship history
- **6sense**: no unique CSV row (not-in-csv)
- **DraftKings**: H-1B columns blank in CSV
- **HubSpot**: no unique CSV row (not-in-csv)
- **Wayfair**: no unique CSV row (not-in-csv)
- **Braze**: sponsors, but no software title in its top sponsored titles
- **Mobilio**: 0 approvals, 2.0 denials on record

## Verified vs inferred

| Value | Label | Where it came from |
|---|---|---|
| H-1B approvals, denials, rate, top sponsored titles | record | 80 Days to Stay CSV (sha256 below; rates rounded here, raw strings in run.json). The CSV does not say which fiscal years it covers |
| Sponsorship tier (Proven / Likely / None / Unknown) | record fields → your-input rule | thresholds: ≥10 approvals, ≥90% rate, one non-senior software title |
| Sponsorship p (0.9 / 0.6 / 0.0) | your-input | mirrors data/examples/ch11-roles.json; sent to the scorer labeled your-input |
| Timeline factor 0.8 | your-input | dates and assumptions below; same for every company |
| Liveness 1.0 | your-input, **UNCHECKED** | no posting was fetched |
| Fit | not sent | no record exists; not guessed |
| SOC 15-1252 wage context | record | Software Developers, median $133080.0 (OEWS 2024); carries no weight |

## Timeline assumptions (all your-input)

- Program end 2026-12-23; requested OPT start 2026-12-24; OPT filed 2026-10-15; filing window 2026-09-24 to 2027-02-21
- EAD wait 90 days → EAD estimate 2027-01-13; hiring lag 120 days
- Earliest work start 2027-01-31; unemployment days used ≈ 18 of 90 → factor 0.8
- Regulatory constants (90 days before / 60 days after program end to file, 90-day unemployment limit) are typed in, not read from a record. Check them against USCIS before relying on this.
- Sensitivity: with no fit vote, a Proven company (p 0.9 × weight 0.35 = 0.315) drops from Apply to Consider once the timeline factor falls below 0.9524 (0.30 / 0.315), i.e. from the 5th unemployment day.

## Run record

- CSV: `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv` sha256 `eccdee2addf472b1…` (30369 rows)
- Scorer: `scripts/score/role-scorer.mjs` (unchanged); its own report: `role-scores.md`. **Read that file as a raw audit only:** the scorer has no 'unchecked' state, so it calls the UNCHECKED liveness of 1.0 "gates healthy" and says Unknown rows are "time better spent elsewhere". This report, not the scorer's, carries the BLOCKED and NOT-a-no labels.
- Agent log: `run.json`

*Human gate: nothing here is an application. A person picks which rows to act on and records that choice in the run log.*
