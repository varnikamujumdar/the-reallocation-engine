# Setup log — first run of the engine on a fresh clone

## Executive summary

This is a record of getting the job-search engine running on my laptop for the first time, before building anything of my own. It matters because the assignment asks for a "before" baseline, and because three things broke on a fresh clone that the setup instructions don't mention. All three were fixed with one install command each. After that, the health check, the conformance check, the job-board scan, the posting-liveness check, and the role scorer all ran successfully.

## Run record

- Date: 2026-10-03
- Machine: macOS (arm64), Node v26.10.0, npm 11.19.1, Python 3.9.6
- Clone: fork `varnikamujumdar/the-reallocation-engine`, branch `main` @ `015843d`

### Baseline (before any fixes)

| Command | Result |
|---|---|
| `npm install` | ok (warning: `fsevents`, `sharp` install scripts not yet allow-listed) |
| `npm run doctor` | ✓ environment runnable; no private paths tracked; 33 recipes (DRAFT 28 · RUNNABLE-SAMPLE 4 · RUNNABLE-LIVE 1); 318 open TODOs |
| `npm run verify` | **FAILED**: conformance ✓ (158 files), but manifest check errored with `ModuleNotFoundError: No module named 'yaml'` |
| `npm run ats:scan -- --dry-run` | **FAILED**: `Error: portals.yml not found. Run onboarding first.` |
| `npm run ats:liveness -- <url>` | **FAILED**: Playwright Chromium executable not installed |
| `npm run score -- data/examples/ch11-roles.json --out-dir course/2026fa/submissions/varnikamujumdar/runs` | ✓ `scored 5 roles → Apply 2 · Consider 1 · Skip 2 (skip 40%)` |

### Fixes applied

1. `python3 -m pip install --user pyyaml`. After this, `npm run verify` passes with 3 warnings. The two `W2 private path not gitignored` warnings for `private/` and `data/ats/` are **false positives**: `git check-ignore` confirms both are ignored by `/private/*` and `/data/ats/*` in `.gitignore`. The manifest checker seems to match the literal pattern string rather than asking git.
2. `cp data/ats/portals.example.yml data/ats/portals.yml` (the copy is gitignored, confirmed with `git check-ignore`).
3. `npx playwright install chromium`.

### After fixes

```
$ npm run ats:scan -- --dry-run
Companies scanned:     1
Total jobs found:      886
Filtered by title:     392 removed
Filtered by location:  423 removed
Duplicates:            10 skipped
New offers added:      61
```

```
$ npm run ats:liveness -- "https://databricks.com/company/careers/open-positions/job?gh_jid=8805655002"
✅ active     https://databricks.com/company/careers/open-positions/job?gh_jid=8805655002
Results: 1 active  0 expired  0 uncertain
```

```
$ npm run score -- data/examples/ch11-roles.json --out-dir course/2026fa/submissions/varnikamujumdar/runs
✓ scored 5 roles → Apply 2 · Consider 1 · Skip 2 (skip 40%)
```

### Observations worth keeping

- **Location filter leaks non-US roles.** The example `portals.yml` puts `"Remote"` in `location_filter.allow`, so "Remote - India" and a European multi-country listing passed the filter as US roles. For an F-1/OPT student who needs a US employer, that counts as a false Consider.
- **Example scorer run skips only 40%,** below the ~50% a healthy run should skip. The scorer reports this itself.
- **Role quality weight is 0 `[VERIFY]`** in the scorer header, as the assignment's "Facts that bite" warns.
