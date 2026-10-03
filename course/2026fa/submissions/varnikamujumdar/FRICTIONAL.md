# FRICTIONAL — honest log

## Executive summary

This is the honest record of how this assignment was actually done: what was tried, what broke, what was checked, and who did what. Most of the code and writing was done by an AI coding assistant (Claude Code) working in my repository at my direction. I made the decisions about my situation, the persona, the branch, and what to keep or remove, and I'm responsible for checking all of it. Several things broke on a fresh clone and during the build, and they're listed here with what was done about each.

## Who did what

| Part | Me (Varnika) | AI assistant |
|---|---|---|
| Fork + clone | did it | — |
| Toolchain setup (npm install, PyYAML, Playwright, portals.yml) | approved | ran the commands, wrote SETUP-LOG.md |
| Choosing the recipe idea | asked for "the easiest" option; **accepted** the recommendation | recommended the sponsor shortlist + timeline gate after counting rows in the CSV |
| Career situation (F-1, SWE, graduating 2026-12-23, STEM program) | provided | — |
| Persona name | **rejected** using my own real name after the AI explained the privacy risk; first picked a fictional name that shared my surname; after the review flagged that it could still be traced to me, **chose "Bella"** | first proposed "Nisha Rao"; advised against a real name; raised the surname issue as a question for me to decide |
| CHANGE-BRIEF §1–6 | reviewed | drafted |
| CHANGE-BRIEF §7 predictions | asked the AI to write them; **accepted** them; later asked to remove the in-file "drafted by AI" note, so the disclosure lives here instead | drafted all three before any code existed |
| Branch `contrib/2026fa-varnikamujumdar-swe-newgrad-sponsors` | created it myself | — |
| Build plan | **approved** it | wrote it |
| Prototype, tests, fixtures, recipe, card, README | reviewed | wrote |
| Target company list | accepted | picked the 12 names **after** browsing the CSV, so the mix of outcomes was partly known in advance |
| JUSTIFICATION, WORKED-RUN, run log, this file, SOURCES | reviewing | drafted |
| Pre-commit check | **asked** for a full check against the assignment before committing | ran mechanical checks and sent an independent reviewer agent; fixed its findings (item 14) |
| git add / commit / push / PR | doing it myself | told not to touch git, and didn't |

## Attempts, expectations, what happened, response

1. **`npm run verify` on a fresh clone.** Expected it to pass. It failed: `ModuleNotFoundError: No module named 'yaml'`. Response: `pip install --user pyyaml`, then it passed. Learned: CI installs PyYAML itself, but a fresh laptop doesn't, and the setup steps don't say so.
2. **`npm run ats:scan -- --dry-run`.** Expected output. Got `portals.yml not found`. Response: copied `data/ats/portals.example.yml` to `data/ats/portals.yml` and confirmed with `git check-ignore` that it can't be committed.
3. **`npm run ats:liveness`.** Failed: Playwright's browser wasn't installed. Response: `npx playwright install chromium`; then the Databricks posting came back `active`.
4. **The scan's location filter.** Noticed "Remote - India" and European roles passing a "United States" filter, because `"Remote"` matches any location containing that word. Not fixed (not my namespace); noted.
5. **The `verify` warning "private path not gitignored".** Worried at first. Checked with `git check-ignore`: both paths are ignored, so the warning is a false positive.
6. **Reading the scorer before building.** Found that if a role has no liveness value, the scorer uses `1.0` and labels it `record`. Response: the prototype always sends liveness explicitly as `your-input`, `UNCHECKED`. Unresolved: the scorer itself still does this for anyone else.
7. **First real run.** Expected some name-match misses (prediction §7.2). "Notion" and "6sense" missed, as predicted. Expected the seniority regex to misfire (§7.1). Klaviyo's "Software Engineer II" was counted as senior, as predicted. Not changed, because changing the rule to make a company I like pass would be weakening a rule.
8. **All 16 tests passed on the first try**, which made me suspicious that they test nothing. Response: broke the code in memory. The first record of this was wrong: it said "2 tests failed each time", but the two changes had been applied together. After the review, each change was re-run separately on the final 22-test suite: senior filter off → 2 failures; Unknown given p = 0.0 → 1 failure; OPT filing date ignored → 3 failures. Each mistake is caught.
9. **Hand-checking values against the CSV.** First try: `grep … | cut -d, -f1,16-19` printed executives' names instead of approval counts, because the CSV has commas inside quoted fields. Response: redid it with Python's `csv` module, and all four companies matched. That output was never put in any file, since it contained people's names.
10. **PII scan.** Got 1 finding: the `glob` maintainer's public address in `package-lock.json`. Checked: the file is unchanged from the instructor's repo at `015843d`, which has the same line (a library's deprecation notice). Scanning only my folders gives `clean ✓`. Decided **not** to edit the lockfile or the scanner, because that would be weakening a rule.
11. **Console output** printed my full local path (including my username). Fixed to print paths relative to the repo.
12. **F4 changed during the build.** The brief said "halt if graduation is in the past". That would block a student still inside the 60-day OPT start window, so the build halts only once the window has closed. Logged as a revision in CHANGE-BRIEF.md rather than rewriting the prediction.
13. **Job-board check.** The AI queried the public Greenhouse boards for Stripe, Figma, and Datadog. Only Stripe had a US early-career SWE posting, and it says "Immediate Start", which this persona can't meet. This was done in the session, not by the prototype, and does **not** count as clearing the liveness gate. I chose not to run `ats:liveness` myself for this submission.

14. **Independent review before committing.** Before running `git add`, I asked for a full check. An AI reviewer agent read everything against the assignment and ran the code. It found real problems:
    - The timeline gate accepted an OPT filing date of 2027-05-01 (after the filing window) and still said Apply.
    - The sponsorship p was labeled `record` but came from my rule.
    - The scorer's own report says "gates healthy" for unchecked liveness.
    - Re-running would overwrite the saved run.
    - The break commands were paraphrased, not pasted.
    - The persona shared my surname.
    - Several counts were off (302 vs 301; the number of failing tests).

    Response: fixed the code (filing-window check, label, output folder, exit-3 test), added break fixtures so every break command can be pasted word for word, renamed the persona to "Bella", and corrected the documents. Tests went from 16 to 22. **Not fixed:** the scorer's "gates healthy" wording is in a file outside my namespace, so it's documented instead. Because the code changed, my earlier re-run no longer counts for the attestation and has to be repeated.

## Still unresolved

- Which fiscal years the CSV's H-1B counts cover.
- Whether the 60-day and 90-day OPT rules as typed are exactly right (not checked against USCIS).
- How to tell entry-level titles apart from senior ones better than a word list.
- Whether CI on Python 3.12 behaves the same as my 3.9.6.

## Traceability

- Setup output: `course/2026fa/submissions/varnikamujumdar/SETUP-LOG.md`
- Run outputs: `course/2026fa/submissions/varnikamujumdar/runs/2026-10-03/`
- Tests: `scripts/contrib/2026fa/varnikamujumdar-swe-newgrad-sponsors/test_sponsor_shortlist.py`
- Break attempts and hand check: `WORKED-RUN.md` §Verification
- Commits, in order: `3e8cbe8` setup log + change brief · `b3db05f` recipe + card · `19f5da0` prototype, tests, fixtures · `bbb7ddf` run outputs · `78328fe` run log · `052820b` write-ups. A final commit adds the clean-checkout results (see `git log`).
- Clean-checkout run and branch-history PII scan: `TEST-REPORT.md` §Clean-checkout run
