# Sources and credits

## Executive summary

This page credits everything this submission is built on: the course repository and its rules, the public data files, the tools, and the AI assistant that wrote most of the code and text. It also says plainly what the AI did and what I personally decided, checked, or rejected.

## Repository and governing documents

- *The Reallocation Engine*, Nik Bear Brown: forked from `nikbearbrown/the-reallocation-engine` at commit `015843d`.
- `SNICKERDOODLE.md` (constitution), `DOMAIN.md`, `CONTRIBUTING.md`, `DATA_CONTRACT.md`, `recipes/README.md`, `recipes/_shared.md` (run-log template).
- Style models: `recipes/scan.md`, `recipes/local-wage-adjustment.md`, `recipes/local-wage-adjustment.card.md`.
- Persona format: `search/examples/*/profile.yml`.

## Data (all shipped in the repo; nothing downloaded by the prototype)

- `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv`. Per its README, it maps an SEC startup list against the DOL LCA Disclosure Data and the USCIS H-1B Employer Data Hub. The README does not state which fiscal years are covered.
- `data/bls/compact/soc_occupation_compact.csv`: BLS OEWS 2024 / O*NET, row 15-1252 (context only).
- `data/examples/ch11-roles.json`: the scorer's input shape and the Proven/Likely p values (0.9 / 0.6) reused here.

## Code reused, not modified

- `scripts/score/role-scorer.mjs`: the scorer (combines votes and gates).
- `scripts/ats/check-liveness.mjs` (`npm run ats:liveness`), `scripts/ats/scan.mjs`: run during setup only.
- `scripts/conformance.mjs`, `scripts/manifest-check.mjs`, `scripts/doctor.mjs`, `scripts/pii-scan.mjs`: checks.

## Regulatory facts used as assumptions (not yet verified against a primary source)

- Filing for post-completion OPT from 90 days before program end, the 60-day window after program end, and the 90-day unemployment limit on post-completion OPT: 8 CFR 214.2(f) and USCIS guidance. Typed in as your-input. **Not checked against the primary text for this submission.**

## Tools

- Python 3.9.6 (standard library only), Node 26.10.0, npm 11.19.1, Playwright Chromium (setup only), macOS.
- Public Greenhouse job-board API (`boards-api.greenhouse.io`), queried once by the AI in-session for Stripe, Figma, and Datadog postings. Not used by the prototype.

## AI contribution

**Tool:** Claude Code (Anthropic), working in my local repository.

**What the AI did:**
- set up the toolchain;
- inspected the data;
- drafted CHANGE-BRIEF.md, including the §7 predictions (at my request);
- wrote the build plan, `sponsor_shortlist.py`, the tests, fixtures, README, recipe, and card;
- ran every command and test shown in WORKED-RUN.md;
- drafted JUSTIFICATION.md, WORKED-RUN.md, FRICTIONAL.md, this file, TEST-REPORT.md, and the run log;
- ran an independent AI reviewer agent over the whole submission before the first commit, and fixed what it found (see FRICTIONAL.md item 14).

**What I decided, checked, changed, or rejected:**
- I chose my situation, the role, and the dates.
- I chose the "easiest" recipe option it offered.
- I rejected using my real name for the persona, and after the review chose the fictional name "Bella".
- I created the branch myself and approved the build plan.
- I had the AI-attribution note removed from the brief and moved the disclosure here and to FRICTIONAL.md.
- I chose to skip running the liveness gate myself.
- I asked for a full check against the assignment before committing.
- I did all git commits, pushes, and the PR myself; the AI made no git changes (it only ran read-only git commands for the clean-checkout check).
- I re-ran the offline tests and the documented sample command myself on 2026-10-03, before the review fixes, and got the same results as the AI's runs (16 tests OK; Apply 3 · Consider 3 · Skip 6). The code changed after that, so after the review fixes I re-ran on the final code: the test suite (22 tests OK), the sample command (Apply 3 · Consider 3 · Skip 6), and the late-filing break attempt, which halted with the expected filing-window error.

**Collaborators:** none.
