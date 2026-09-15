R4 VERDICT: COULD-NOT-EXECUTE (C: free space measured 1,871,450,112 bytes before r3, below LANE_PROMPT.md stop threshold of 2 GB)

All numbers below are MEASURED unless explicitly marked INFERRED.

## Stop Reason

- MEASURED: before starting the r3 refresh, `python -c "import shutil; u=shutil.disk_usage('C:/'); print(u.free)"` reported 1,871,450,112 bytes free on C:.
- MEASURED: a repeated disk check while writing lane artifacts reported 1,871,151,104 bytes free on C:.
- The lane prompt says to stop if free space drops under 2 GB, so r3 was not started and no topic refresh was attempted.
- MEASURED: `outputs/search_v2/candidates-2026-09-15r3-all.json` exists, records `registries=["ctgov","isrctn"]`, lists 32 requested topics, and contains 0 attempted topic rows.

## Integration Notes

- MEASURED: clone HEAD was `f62eec27416e4835b34dd193ff0997f9c0162236`.
- MEASURED: plain `git apply --3way C:/meta-harness/outputs/search_v2/lanes/R2/R2.diff` could not create `.git/index.lock` in this sandbox.
- MEASURED: temp-index three-way retries were blocked first by index stat mismatch, then by `.git/objects` write permission.
- MEASURED: plain `git apply C:/meta-harness/outputs/search_v2/lanes/R2/R2.diff` applied R2's diff without rejects.
- Hunk resolution: none. No failed hunk was manually resolved.
- MEASURED: copied `C:/meta-harness/outputs/search_v2/lanes/R2/test_search_v2_isrctn.py` to `tests/test_search_v2_isrctn.py`.
- MEASURED: integration checkpoint `python -m pytest tests/ -q` passed with 635 passed in 161.11 seconds.

## Driver Changes

- Added `--registries`, defaulting to `ctgov`, parsed as a validated tuple and passed into `search_v2.refresh_topic(..., registries=...)`.
- Recorded that tuple at candidate-file top level as `registries`.
- Added `--tar-only`; it moves raw bodies with `archive_raw_bodies.move`, creates the same tarball name and tar layout used by the upload path, computes `tar_sha256` and `tar_bytes`, deletes the expanded moved-body directory, keeps the tarball, and records `TAR-ONLY-UPLOAD-PENDING`.
- Extended `_write_archive_pointer` so `TAR-ONLY-UPLOAD-PENDING` writes custody text: `tarball held locally pending upload; digests in-tree are the authority`.
- Added `tests/test_search_v2_run_tar_only.py`.
- MEASURED: `python -m pytest tests/test_search_v2_run_tar_only.py -q` passed with 2 passed in 2.61 seconds.
- MEASURED: `python -m py_compile scripts/search_v2_run.py` exited 0.

## Tar-Only Ledger

No r3 topic was attempted after the disk-space stop, so no tarball bytes or sha256 values exist. Asset names below are INFERRED from the driver naming convention; bytes and sha256 are NOT MEASURED because the assets were not generated.

| Topic | Asset | Bytes | SHA256 | State |
|---|---|---:|---|---|
| balanced-crystalloids-vs-saline-mortality | raw-balanced-crystalloids-vs-saline-mortality-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| colchicine-postop-af | raw-colchicine-postop-af-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| colchicine-recurrent-pericarditis | raw-colchicine-recurrent-pericarditis-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| colchicine-secondary-cv-prevention | raw-colchicine-secondary-cv-prevention-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| corticosteroids-cap-mortality | raw-corticosteroids-cap-mortality-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| corticosteroids-covid19-mortality | raw-corticosteroids-covid19-mortality-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| dapagliflozin-hfpef-hosp | raw-dapagliflozin-hfpef-hosp-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| denosumab-vertebral-fracture | raw-denosumab-vertebral-fracture-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| doac-vte-recurrence | raw-doac-vte-recurrence-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| dpp4-mace-t2d | raw-dpp4-mace-t2d-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| empagliflozin-hfpef-hosp | raw-empagliflozin-hfpef-hosp-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| esketamine-trd-madrs | raw-esketamine-trd-madrs-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| finerenone-ckd-t2d-renal | raw-finerenone-ckd-t2d-renal-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| glp1-ra-mace-t2d | raw-glp1-ra-mace-t2d-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| iv-iron-hfref-hosp | raw-iv-iron-hfref-hosp-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| melatonin-primary-insomnia-sol | raw-melatonin-primary-insomnia-sol-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| metformin-pcos-ovulation | raw-metformin-pcos-ovulation-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| noac-vs-warfarin-af-stroke | raw-noac-vs-warfarin-af-stroke-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| omega3-cardiovascular-events | raw-omega3-cardiovascular-events-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| pcsk9-mace | raw-pcsk9-mace-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| probiotics-aad-prevention | raw-probiotics-aad-prevention-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| sacubitril-valsartan-hfref | raw-sacubitril-valsartan-hfref-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| semaglutide-obesity-mace | raw-semaglutide-obesity-mace-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| semaglutide-obesity-weight | raw-semaglutide-obesity-weight-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| sglt2-ckd-progression | raw-sglt2-ckd-progression-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| sglt2-hfref-hosp-cvdeath | raw-sglt2-hfref-hosp-cvdeath-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| sglt2-primary-prevention-hf | raw-sglt2-primary-prevention-hf-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| spironolactone-hfref-mortality | raw-spironolactone-hfref-mortality-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| statins-primary-prevention-elderly | raw-statins-primary-prevention-elderly-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| ticagrelor-vs-clopidogrel-acs | raw-ticagrelor-vs-clopidogrel-acs-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| tocilizumab-covid19-mortality | raw-tocilizumab-covid19-mortality-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |
| tranexamic-acid-pph | raw-tranexamic-acid-pph-2026-09-15r3-search_v2.tar.gz | N/A | N/A | NOT_ATTEMPTED |

## Lane Artifacts

- MEASURED: `lane_r4/01-integrate.txt` contains git-apply attempts, diff stat, and pytest tail.
- MEASURED: `lane_r4/02-driver.txt` contains diff stat, the new test pytest line, status, compile check, and disk check.
- MEASURED: `lane_r4/03-run-r3.stdout` through `lane_r4/07-r2-vs-r3.txt` each contain `COULD-NOT-EXECUTE` with the disk-space reason.
- MEASURED: `docs/search_recall_regression_corpus_search_v2.json` was not regenerated because Step 4 was not reached.

## Commands Run

- `Get-Content -Raw -LiteralPath 'F:\ProjectIndex\INDEX.md'`
- `Get-Content -Raw -LiteralPath 'F:\E156\rewrite-workbook.txt'`
- `Get-Content -Raw -LiteralPath '.\LANE_PROMPT.md'`
- `git status --short --branch`
- `rg --files`
- `git rev-parse HEAD`
- `Get-ChildItem -LiteralPath 'C:\meta-harness\outputs\search_v2\lanes\R2'`
- `Get-PSDrive -Name C`
- PowerShell logging wrapper for `git apply --3way C:/meta-harness/outputs/search_v2/lanes/R2/R2.diff`, R2 test copy, and `git diff --stat`; the wrapper itself failed on `New-Item -LiteralPath`, then failed to write `lane_r4/01-integrate.txt`.
- `git status --short --branch`
- `git diff --stat`
- `Test-Path -LiteralPath '.\tests\test_search_v2_isrctn.py'`
- `Get-Content -TotalCount 120 -LiteralPath 'C:/meta-harness/outputs/search_v2/lanes/R2/R2.diff'`
- `Select-String -Path 'C:/meta-harness/outputs/search_v2/lanes/R2/R2.diff' -Pattern '^diff --git'`
- PowerShell logging wrapper for `git apply --3way C:/meta-harness/outputs/search_v2/lanes/R2/R2.diff`, R2 test copy, and `git diff --stat`.
- `Get-Content -Raw -Path '.\lane_r4\01-integrate.txt'`
- `git ls-files tests/fixtures/isrctn_sample.xml tests/test_search_v2_isrctn.py`
- `Get-ChildItem -Force -Path '.\.tmp'`
- `git status --short`
- Attempted temp-index apply wrapper containing cleanup was rejected by sandbox policy before execution.
- PowerShell temp-index wrapper running `git read-tree HEAD`, `git apply --3way C:/meta-harness/outputs/search_v2/lanes/R2/R2.diff`, R2 test copy, and `git diff --stat`.
- `Get-Content -Raw -Path '.\lane_r4\01-integrate.txt'`
- PowerShell temp-index wrapper running `git read-tree HEAD`, `git update-index --refresh`, `git apply --3way C:/meta-harness/outputs/search_v2/lanes/R2/R2.diff`, and `git diff --stat`.
- `Get-Content -Tail 80 -Path '.\lane_r4\01-integrate.txt'`
- PowerShell fallback wrapper running `git apply C:/meta-harness/outputs/search_v2/lanes/R2/R2.diff` and `git diff --stat`.
- PowerShell wrapper running `python -m pytest tests/ -q`.
- `Get-Content -Raw -Path '.\lane_r4\01-integrate.txt'`
- `Get-Content -Raw -Path '.\scripts\search_v2_run.py'`
- `Get-Content -Raw -Path '.\scripts\archive_raw_bodies.py'`
- `rg -n "def _archive_and_upload|archive_raw_bodies|_write_archive_pointer|refresh_topic|registr" scripts harness tests`
- `Get-Content -Path '.\harness\search_v2.py' -TotalCount 1450 | Select-Object -Last 330`
- `Get-Content -Raw -Path '.\tests\test_search_v2_run2_engine.py'`
- `Get-Content -Raw -Path '.\tests\test_search_v2_guard.py'`
- `Get-Content -Raw -Path '.\tests\test_search_v2_isrctn.py'`
- PowerShell wrapper running `git diff --stat` and `python -m pytest tests/test_search_v2_run_tar_only.py -q`.
- `Get-Content -Raw -Path '.\lane_r4\02-driver.txt'`
- `git diff -- scripts/search_v2_run.py tests/test_search_v2_run_tar_only.py`
- `python -m py_compile scripts/search_v2_run.py`
- `Get-PSDrive C | Format-List *`
- `Get-Item -Path '.\tests\fixtures\isrctn_sample.xml' | Select-Object Length`
- `Get-Content -TotalCount 20 -Path '.\tests\fixtures\isrctn_sample.xml'`
- `git diff -- tests/fixtures/isrctn_sample.xml | Select-Object -First 60`
- `git status --short`
- `python -c "import shutil; u=shutil.disk_usage('C:/'); print(u.free)"`
- PowerShell wrapper writing `COULD-NOT-EXECUTE` into `lane_r4/03-run-r3.stdout` through `lane_r4/07-r2-vs-r3.txt`, then running `git status --short`, `python -m py_compile scripts/search_v2_run.py`, and the repeated disk check.
- Python one-liner writing `outputs/search_v2/candidates-2026-09-15r3-all.json` skeleton with zero attempted topic rows.
- `Get-ChildItem -Path '.\lane_r4' | Select-Object Name,Length`
- `python -c "import json; p=json.load(open('outputs/search_v2/candidates-2026-09-15r3-all.json',encoding='utf-8')); print(p['registries']); print(len(p['topics_requested'])); print(len(p['topics']))"`
- `git diff --stat`
- `Get-Content -Raw -Path '.\lane_r4\02-driver.txt'`
- `Get-Content -Raw -Path '.\outputs\search_v2\candidates-2026-09-15r3-all.json'`
