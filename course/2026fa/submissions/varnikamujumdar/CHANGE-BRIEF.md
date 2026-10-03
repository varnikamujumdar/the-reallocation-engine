# Change brief — new-grad software engineer sponsor shortlist

## Executive summary

**What this is:** the plan, written before any code exists, for a small tool that helps one kind of student: an international master's student on an F-1 visa who graduates in December 2026 and wants an entry-level software engineering job in the US.

**Why read it:** it records what I expect to build, where I expect it to break, and which decisions a person (not the tool) has to make. It's written now so the finished work can be checked against it honestly.

**What it decides:** the tool takes a public list of about 30,000 companies, keeps the ones whose records show they have sponsored work visas for software roles, and checks whether a job started now could begin before the student's work permit clock runs out. It returns a ranked shortlist: apply, consider, or skip. It does **not** check whether any job posting is real, and it doesn't judge whether the student is a good fit. A person has to do both before applying.

## Run record

- Author: Varnika Mujumdar (GitHub `varnikamujumdar`) · drafted 2026-10-03, with an AI assistant (see FRICTIONAL.md / SOURCES.md)
- Planned slug: `varnikamujumdar-swe-newgrad-sponsors`
- Planned branch: `contrib/2026fa-varnikamujumdar-swe-newgrad-sponsors`
- Status of this file: **original predictions**. Later revisions are appended under "Revisions" at the end; nothing above that line is rewritten.

## 1. The career situation

**Persona (fictional, mirrors my own situation):** "Bella", bella@example.com.

| Field | Value | Label |
|---|---|---|
| Visa | F-1, currently a student. OPT **not yet filed or approved** | your-input |
| Degree | MS, Computer Science (STEM-designated, so STEM OPT eligible later) | your-input |
| Program end date | 2026-12-23 | your-input |
| Target role | Software Engineer, new grad / entry level | your-input |
| Target occupation | SOC 15-1252 Software Developers | record (`data/bls/compact/soc_occupation_compact.csv`, one row, OEWS 2024 median $133,080) |
| Search start | 2026-10-03, about 11 weeks before graduation | your-input |

Why this is specific: the student isn't on OPT yet, so the clock that matters isn't "days left." It's whether a hiring process started today ends with a start date the student is allowed to work on. They're also competing for **new-grad** roles, while most visible sponsorship history is for senior engineers.

**Engine layer:** 80 Days to Stay (H-1B sponsorship history + Form D funding, one CSV), plus the visa-timeline gate. Role quality is used only as a read-only reference (see §5).

## 2. What I reuse (exact paths)

| What | Path / command | Used for |
|---|---|---|
| Company + sponsorship + funding table | `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv` (30,369 rows) | sponsorship vote (`Total Approvals`, `Total Denials`, `Approval_Rate`, `top_job_titles_sponsored`), funding recency (`latest_funding_date`) |
| Occupation wage reference | `data/bls/compact/soc_occupation_compact.csv`, row `15-1252` | display only in the report, no weight |
| Scorer | `npm run score -- <roles.json> --out-dir <my folder>` (`scripts/score/role-scorer.mjs`) | combining votes and gates. **Not re-implemented.** |
| Input shape | `data/examples/ch11-roles.json` | the shape my `roles.json` must match |
| Liveness (manual, by the human at the gate) | `npm run ats:liveness -- <url>` | the human runs it before acting on an Apply |

What I checked in the CSV before planning (2026-10-03, by script):

- 1,557 of 30,369 companies have any H-1B approval data. The other 28,812 are **unknown**, not "non-sponsor."
- 519 sponsors list "software" in `top_job_titles_sponsored`. Only 302 of those list a software title without a senior/staff/lead/manager marker.
- `latest_funding_date` among those 519 runs from 2012-10-29 to 2025-09-11.
- 1 row (MOBILIO LLC) has 0 approvals, 2 denials, 0% rate.
- The CSV's README does **not** say which fiscal year(s) the H-1B counts cover. That's a provenance gap I'll have to state, not fill in.

## 3. What I'm proposing that the repo doesn't have

1. **A new-grad title filter** over `top_job_titles_sponsored` (`[TODO: DEV]`). The repo has no way to tell "sponsors software engineers" apart from "sponsors *senior* software engineers," and that difference is the whole asymmetry for a new grad.
2. **A pre-OPT timeline factor** (`[TODO: DEV]`). The existing personas all have an OPT start date. This persona doesn't have one yet. The factor is computed from program end date + assumed EAD wait + assumed hiring lag. Every assumption is labeled `your-input`.
3. **The regulatory constants** the timeline needs (the 60-day window to start OPT after program end, the 90-day OPT unemployment limit) aren't recorded anywhere in the repo (`[TODO: DATA SOURCE]`). I'll cite USCIS / 8 CFR 214.2(f) and label them `your-input` until a record backs them.

## 4. Gates (hard stops)

| Gate | Testable condition | What the human needs to see to clear it |
|---|---|---|
| **G1, input sanity** | persona file parses; program end date is a valid date; CSV exists at the path above with the expected columns | the prototype's input check line in the report; it halts otherwise |
| **G2, visa timeline** (gate, not vote) | timeline factor > 0.05 for the role | the assumptions used (EAD wait, hiring lag) and the resulting earliest start date, each labeled |
| **G3, liveness** (gate, not vote) | **not checked by the prototype**: liveness is sent to the scorer as unverified | before acting on any Apply, the human runs `npm run ats:liveness -- <url>` on the actual posting and records the result |
| **G4, release** | the human reads the Markdown report and picks which rows become applications | a signed line in the run log (`logs/runs/2026fa-varnikamujumdar-1.md`) |

## 5. Facts that bite, and how I handle them

- **Role quality weight is 0:** I don't rely on it. The SOC 15-1252 wage is shown in the report as context only.
- **`bls:local-wage` feeds nothing / fails on a fresh clone:** not used.
- **Only SEC samples ship:** I use only the 80-days CSV for funding, not `data/sec/form-d/processed/sample/`. I'll say so.
- **Planned dirs don't exist** (`data/raw/`, `data/verified/`, `logs/gate-decisions/`): my gates point only at the paths above.
- **`snickerdoodle` CLI isn't real:** not used.

## 6. Predicted failure cases (and how I'll check each)

| # | Failure case | Expected behavior | How I'll test it |
|---|---|---|---|
| F1 | Company not in the CSV | sponsorship = **unknown**, tier `Unknown`, no number invented; never scored as 0 | fixture with a company name absent from the fixture CSV |
| F2 | Company in CSV but approval columns blank | same as F1: unknown, not 0 | fixture row with empty `Total Approvals` |
| F3 | Sponsors only senior software titles | flagged "senior-only history"; tier lowered, not excluded | fixture row with `['Senior Software Engineer']` only |
| F4 | Program end date already in the past, or not a date | halt at G1 with a clear error, no output | run with `2025-01-01` and with `not-a-date` |
| F5 | Malformed approvals (e.g. 0 approvals, denials > 0) | tier `None`, shown with its raw numbers | fixture row copying the MOBILIO pattern |

## 7. What I predict my prototype will get wrong on the first pass

1. **The new-grad title filter will misclassify titles.** It decides "junior vs. senior" from the job title text alone. Titles like "Software Engineer II", "Member of Technical Staff", or "Software Development Engineer" don't say their level, so I expect some mid-level roles to pass as new-grad and some real entry-level history to be missed. `top_job_titles_sponsored` also lists only a company's *top* titles, so a company that sponsors many new grads but even more seniors may look senior-only.
2. **Company names won't match cleanly.** The CSV uses legal names ("1UPHEALTH INC", "6SENSE INSIGHTS INC"), but a student types "1upHealth" or "6sense". I expect the first version's exact-match lookup to report real sponsors as "not found / unknown".
3. **The timeline factor will look more precise than it is.** It rests entirely on my guesses for EAD processing time and hiring lag. Small changes to those guesses could flip a role between Apply and Skip, and the first pass won't show how sensitive the result is to them.

## Revisions

*(append dated entries here; do not edit the sections above)*

### 2026-10-03 — after the first build

- **F4 changed during the build.** I predicted a halt whenever the program end date is in the past. The build halts only when the 60-day window to start OPT has **already closed** and no OPT filing is recorded, or when a date isn't valid. A student who graduated last week is still inside that window and can still use the tool, so halting them would have been wrong. Tested by `test_F4_window_closed_without_filing_halts`, `test_F4_bad_date_halts`, and `test_F4_halt_writes_nothing`.
- **§7.1 confirmed on the first run:** Klaviyo's "Software Engineer II" was counted as a senior title, so Klaviyo came out Likely instead of Proven.
- **§7.2 confirmed on the first run:** "Notion" and "6sense" did not match `NOTION LABS INC` / `6SENSE INSIGHTS INC`. Both came back Unknown, with the right company listed only as a possible match.
- **§7.3 partly confirmed:** the timeline factor was 1.0 for every company, so it did not discriminate between companies at all. With no fit vote, a Proven company scores 0.315 against a 0.30 threshold, so about 5 days of unemployment would flip every Apply to Consider.
- **Not predicted:** the existing scorer turns a *missing* liveness value into `1.0` labeled `record`. The prototype sends liveness explicitly as UNCHECKED to avoid this.

### 2026-10-03 — after an independent review, before the first commit

- **Persona renamed for privacy.** The persona originally shared my surname. Combined with the real graduation date and visa status, that could tie it to me in a public repo, so it was renamed to "Bella" (bella@example.com) everywhere, including §1 above. This is the only edit made above the Revisions line, and it's a redaction, not a change to any prediction.
- **Count correction (§2).** "302 of those list a software title without a senior/staff/lead/manager marker" came from a quick check before the build. With the prototype's actual senior-title rule, the count is **301**. The original line is kept as written.
- **New G1 check.** The review found the first build accepted an OPT filing date outside the filing window (e.g. 2027-05-01) and still said Apply. G1 now also halts when the filing date falls outside 90 days before to 60 days after program end. These numbers are your-input until cited (recipe TODO 2).
- **Label correction.** The sponsorship p (0.9 / 0.6 / 0.0) was sent to the scorer labeled `record`. Because it comes from my rule, it is now labeled `your-input`.
