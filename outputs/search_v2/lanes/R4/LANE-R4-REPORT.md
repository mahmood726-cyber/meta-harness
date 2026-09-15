R4 VERDICT: RUN r3 COMPLETE 32 of 32 topics ran (states: RAN_OK 0; RAN_OK_WITH_SOURCE_ERRORS 32; RAN_ZERO 0; RAN_ERROR 0 (none); NOT_RUN 0); ISRCTN source RAN_OK on 25 of 32, RAN_ZERO on 7 of 32, RAN_ERROR on 0 of 32; benchmark positives r2 136 of 147 -> r3 136 of 147; register within kind 15 of 20, whole engine 20 of 20

## Notes
- No commit was made.
- The r3 refresh log completed with `RUN r3 scope=all: states={'RAN_OK_WITH_SOURCE_ERRORS': 32} NOT_RUN=0 of 32`.
- The candidate JSON top-level `stop_reason` still contains the previous low-disk stop message, but `updated_utc`, topic rows, status output, and run log reflect the completed continuation run.
- `lane_r4/05-recall-r3.txt` includes both sections: MEASUREMENT `136 of 147`; DEVELOPMENT fit statistic `122 of 131`.
- Register tool raw within-kind line is `15 of 16 over 4 of 5 topics; not scored: ['statins-primary-prevention-elderly']`; the verdict line uses the requested denominator of 20.

## Disk Gate
- Before r3 start: 8483598336 bytes free.
- After topic 8: 7574974464 bytes free.
- After topic 16: 6745915392 bytes free.
- During topic 21: 6201765888 bytes free.
- After topic 24: 5943767040 bytes free.
- During topic 28: 5141327872 bytes free.
- After r3 completion: 4789813248 bytes free.

## Required Artefacts
- `lane_r4/03-run-r3.stdout`: exists True size 236262 bytes
- `lane_r4/04-status-r3.txt`: exists True size 4171 bytes
- `lane_r4/05-recall-r3.txt`: exists True size 52609730 bytes
- `lane_r4/06-register-r3.txt`: exists True size 1097 bytes
- `lane_r4/07-r2-vs-r3.txt`: exists True size 11753 bytes
- `outputs/search_v2/candidates-2026-09-15r3-all.json`: exists True size 87310949 bytes

## Tar-Only Ledger
| Topic | Asset | Bytes | SHA256 |
|---|---|---:|---|
| balanced-crystalloids-vs-saline-mortality | raw-balanced-crystalloids-vs-saline-mortality-2026-09-15r3-search_v2.tar.gz | 28583332 | d05450ca88231d8ae90ded7c4b5b77752a0408fb5c9ef5fb84fb175ea62d5ec3 |
| colchicine-postop-af | raw-colchicine-postop-af-2026-09-15r3-search_v2.tar.gz | 8645782 | 8588e339b19d0441bfdbf254fb3bf07335fb8fbf432d04136687fb4027ec5dbc |
| colchicine-recurrent-pericarditis | raw-colchicine-recurrent-pericarditis-2026-09-15r3-search_v2.tar.gz | 8890869 | 5cbb8b1def049efab577a41061d50a5e6554882502b3739eef6ce274fcdc750b |
| colchicine-secondary-cv-prevention | raw-colchicine-secondary-cv-prevention-2026-09-15r3-search_v2.tar.gz | 85391900 | c69da25f8b3c609f0ed5dbfdb7e454714bd9a1b56986db1581dfe17e135f085d |
| corticosteroids-cap-mortality | raw-corticosteroids-cap-mortality-2026-09-15r3-search_v2.tar.gz | 27203814 | a79478d6f19a1e8a47f1c1d82bf0d2f3982cb2f47f082580ed4838965430c2fd |
| corticosteroids-covid19-mortality | raw-corticosteroids-covid19-mortality-2026-09-15r3-search_v2.tar.gz | 167633335 | fdc55cb5b4dbe21e4c267a9162fbce36ade0ed9a6d0e36c01f53ff0946583a64 |
| dapagliflozin-hfpef-hosp | raw-dapagliflozin-hfpef-hosp-2026-09-15r3-search_v2.tar.gz | 40417643 | 8dd888719f6b700327482ed9fa097dd6adb26ca82fda7868e3e214be6f2c87a2 |
| denosumab-vertebral-fracture | raw-denosumab-vertebral-fracture-2026-09-15r3-search_v2.tar.gz | 23603922 | 3951e7772a35307f3c1a05809693f6441bc80e877c8d8903917a9431074c0246 |
| doac-vte-recurrence | raw-doac-vte-recurrence-2026-09-15r3-search_v2.tar.gz | 83159399 | e4370340bc0aecf7a761069b564d6ef37ffdeb1a15a7d235d6a4766f2b15d217 |
| dpp4-mace-t2d | raw-dpp4-mace-t2d-2026-09-15r3-search_v2.tar.gz | 110784866 | 5c1e3fb158ff490815c9d2d8dc85a770bee0b424ec7b3a3632b7cbd7bbba2711 |
| empagliflozin-hfpef-hosp | raw-empagliflozin-hfpef-hosp-2026-09-15r3-search_v2.tar.gz | 48821354 | a44b9c8d819116b78fec9f239c6ef9aadaca27e7e29f4640419c13f58b5ed87c |
| esketamine-trd-madrs | raw-esketamine-trd-madrs-2026-09-15r3-search_v2.tar.gz | 17299843 | 2fc9f53e71227f5dc7ad4347c8c9c7111cd2ee3140c435699ddfbc9efb317cc4 |
| finerenone-ckd-t2d-renal | raw-finerenone-ckd-t2d-renal-2026-09-15r3-search_v2.tar.gz | 61554361 | b185ccbe5de0dff733fa0edded0d6608471827f03f036e987afc0e362bf19e0f |
| glp1-ra-mace-t2d | raw-glp1-ra-mace-t2d-2026-09-15r3-search_v2.tar.gz | 295830035 | fd67b8291596fccf118737ebfa5275a94759762d75ef2f7527f3e947f874827b |
| iv-iron-hfref-hosp | raw-iv-iron-hfref-hosp-2026-09-15r3-search_v2.tar.gz | 44999704 | 796b4045df56a43655a6966824078238040bc7ff03e7e87d8acbb48d77cf8eb1 |
| melatonin-primary-insomnia-sol | raw-melatonin-primary-insomnia-sol-2026-09-15r3-search_v2.tar.gz | 14419967 | 6c905d0e037b8459752c0f4d20cb49d6e331b0c65089dff7a39666df5ce3145f |
| metformin-pcos-ovulation | raw-metformin-pcos-ovulation-2026-09-15r3-search_v2.tar.gz | 20919746 | 4f17d597df3bcc3d82f2d221237b09243bcad2abfc7d83faba9c154217bea890 |
| noac-vs-warfarin-af-stroke | raw-noac-vs-warfarin-af-stroke-2026-09-15r3-search_v2.tar.gz | 205889487 | 8948f926859fbc627229267d94b5e2d5a0c0473f50ece5347fa3137baa1845a9 |
| omega3-cardiovascular-events | raw-omega3-cardiovascular-events-2026-09-15r3-search_v2.tar.gz | 236997241 | 8f4113ae240953f7bca37234c8f8daaf8aeb5ec7571811af4efc670665fbf82b |
| pcsk9-mace | raw-pcsk9-mace-2026-09-15r3-search_v2.tar.gz | 87700952 | 5f533a785d64d1229cb471b36a333a2e10edf30d94ebd6e97d313be40a837e77 |
| probiotics-aad-prevention | raw-probiotics-aad-prevention-2026-09-15r3-search_v2.tar.gz | 34700577 | 0b1a1ba132f717bbc8d7a62631f96f945a83b16ea162f29be06d867c41e9663f |
| sacubitril-valsartan-hfref | raw-sacubitril-valsartan-hfref-2026-09-15r3-search_v2.tar.gz | 64227782 | de61b6d443d77816929f325da357825833f81b86d3399f67c2b95d9f284b878e |
| semaglutide-obesity-mace | raw-semaglutide-obesity-mace-2026-09-15r3-search_v2.tar.gz | 33888673 | b1294d512491cd49aa5a92ff4e5aad104cdf2623e317dd4b3e893ccda9b4e703 |
| semaglutide-obesity-weight | raw-semaglutide-obesity-weight-2026-09-15r3-search_v2.tar.gz | 84968934 | 56573aa2702aa225e6e70513d5f5bb470b46b7f92f71065c2371753bd7e4a849 |
| sglt2-ckd-progression | raw-sglt2-ckd-progression-2026-09-15r3-search_v2.tar.gz | 158884387 | 5ec4e9e9e4a0bf0ac014f3708b2052b520c369bdf22f1c8798fd35cb3d7fff0b |
| sglt2-hfref-hosp-cvdeath | raw-sglt2-hfref-hosp-cvdeath-2026-09-15r3-search_v2.tar.gz | 152885620 | b5731d920b1cb48adb7879665323e8746f37174002380dddcda341ec3c1f3b44 |
| sglt2-primary-prevention-hf | raw-sglt2-primary-prevention-hf-2026-09-15r3-search_v2.tar.gz | 331118330 | be56fcf743d4ae97048341b0585b02a113560fb315e805d0e3d4a7ae98e89161 |
| spironolactone-hfref-mortality | raw-spironolactone-hfref-mortality-2026-09-15r3-search_v2.tar.gz | 80331627 | b9caf9f7b8ad74cf39999b5afd01b9a0849c1bf81ac0e54058647c36da31749c |
| statins-primary-prevention-elderly | raw-statins-primary-prevention-elderly-2026-09-15r3-search_v2.tar.gz | 37632825 | 32a92dc45bed18d994a57c654cad682d06e8bae45fb74b94ba26f991a4ce9a69 |
| ticagrelor-vs-clopidogrel-acs | raw-ticagrelor-vs-clopidogrel-acs-2026-09-15r3-search_v2.tar.gz | 51608684 | e2d6d3ae603c9d2768319193787ba83f91910a384f559e4de26b67cea6cb605d |
| tocilizumab-covid19-mortality | raw-tocilizumab-covid19-mortality-2026-09-15r3-search_v2.tar.gz | 101541484 | 52268d7cef7936d66b216c2c8f9e33fe70d69ea06d630d4bedb83bd18ba35bec |
| tranexamic-acid-pph | raw-tranexamic-acid-pph-2026-09-15r3-search_v2.tar.gz | 10242095 | 8a0203f7c78343e933704a47f67a0e66a0ead388678af48efe0c4a0fdc9d8f34 |

## ISRCTN Source States
- balanced-crystalloids-vs-saline-mortality: RAN_OK records 6
- colchicine-postop-af: RAN_OK records 4
- colchicine-recurrent-pericarditis: RAN_ZERO records 0
- colchicine-secondary-cv-prevention: RAN_OK records 6
- corticosteroids-cap-mortality: RAN_OK records 14
- corticosteroids-covid19-mortality: RAN_OK records 199
- dapagliflozin-hfpef-hosp: RAN_ZERO records 0
- denosumab-vertebral-fracture: RAN_ZERO records 0
- doac-vte-recurrence: RAN_OK records 32
- dpp4-mace-t2d: RAN_OK records 20
- empagliflozin-hfpef-hosp: RAN_ZERO records 0
- esketamine-trd-madrs: RAN_ZERO records 0
- finerenone-ckd-t2d-renal: RAN_ZERO records 0
- glp1-ra-mace-t2d: RAN_OK records 39
- iv-iron-hfref-hosp: RAN_OK records 10
- melatonin-primary-insomnia-sol: RAN_OK records 27
- metformin-pcos-ovulation: RAN_OK records 30
- noac-vs-warfarin-af-stroke: RAN_OK records 25
- omega3-cardiovascular-events: RAN_OK records 223
- pcsk9-mace: RAN_OK records 2
- probiotics-aad-prevention: RAN_OK records 10
- sacubitril-valsartan-hfref: RAN_OK records 3
- semaglutide-obesity-mace: RAN_ZERO records 0
- semaglutide-obesity-weight: RAN_OK records 10
- sglt2-ckd-progression: RAN_OK records 22
- sglt2-hfref-hosp-cvdeath: RAN_OK records 28
- sglt2-primary-prevention-hf: RAN_OK records 49
- spironolactone-hfref-mortality: RAN_OK records 33
- statins-primary-prevention-elderly: RAN_OK records 72
- ticagrelor-vs-clopidogrel-acs: RAN_OK records 15
- tocilizumab-covid19-mortality: RAN_OK records 13
- tranexamic-acid-pph: RAN_OK records 8

## Command Ledger
- `Get-Content -Raw -LiteralPath 'F:\ProjectIndex\INDEX.md'`
- `Get-Content -Raw -LiteralPath 'F:\E156\rewrite-workbook.txt'`
- `Get-Content -Raw -LiteralPath '.\LANE_PROMPT.md'`
- `git status --short`
- `Get-Content -Raw -LiteralPath '.\LANE-R4-REPORT.md'`
- `Get-Content -Raw -LiteralPath '.\lane_r4\01-integrate.txt'`
- `Get-Content -Raw -LiteralPath '.\lane_r4\02-driver.txt'`
- `python -c "import shutil;print(shutil.disk_usage('C:/').free)"`
- `python scripts/search_v2_run.py refresh --help`
- `Get-ChildItem -LiteralPath '.\lane_r4'`
- `python - <<'PY' ... PY  # failed in PowerShell before any repo change`
- `python scripts/search_v2_run.py refresh --label r3 --topics all --scope all --registries ctgov,isrctn --tar-only --archive-root .tmp/arch-r3 > lane_r4/03-run-r3.stdout 2>&1`
- `write_stdin/poll session 9707 until process exit`
- `Get-Content -Tail 80/100/120 -LiteralPath '.\lane_r4\03-run-r3.stdout'  # repeated progress inspection`
- `python -c "import json,os,collections; p='outputs/search_v2/candidates-2026-09-15r3-all.json'; ..."  # repeated candidate-count inspection`
- `python -c "import shutil;print(shutil.disk_usage('C:/').free)"  # repeated disk-gate inspection`
- `python scripts/search_v2_run.py status --label r3 --scope all > lane_r4/04-status-r3.txt`
- `python scripts/measure_search_recall.py outputs/search_v2/candidates-2026-09-15r3-all.json --include-development > lane_r4/05-recall-r3.txt`
- `python scripts/measure_regression_corpus_recall_search_v2.py --snapshot 2026-09-15r3-search_v2 > lane_r4/06-register-r3.txt`
- `Get-Content -Raw -LiteralPath '.\lane_r4\04-status-r3.txt'`
- `Get-Content -Raw -LiteralPath '.\lane_r4\05-recall-r3.txt'`
- `Get-Content -Raw -LiteralPath '.\lane_r4\06-register-r3.txt'`
- `python -c "import json,pprint; d=json.load(open('outputs/search_v2/candidates-2026-09-15r3-all.json',encoding='utf-8')); ..."`
- `rg "def _|MEASUREMENT|TOTAL|found" scripts/measure_search_recall.py`
- `Get-Content -TotalCount 220 -LiteralPath '.\scripts\measure_search_recall.py'`
- `python -c "import json,pprint; d=json.load(open('outputs/search_v2/candidates-2026-09-15r2-all.json',encoding='utf-8')); ..."`
- `python -c "import json; d=json.load(open('registry/search_benchmark_split.json',encoding='utf-8')); ..."`
- `Get-Content -LiteralPath '.\scripts\measure_search_recall.py' -TotalCount 340 | Select-Object -Skip 220`
- `python -c "import json,pprint; d=json.load(open('registry/search_benchmark.json',encoding='utf-8')); ..."`
- `python -c "import json; d=json.load(open('outputs/search_v2/candidates-2026-09-15r3-all.json',encoding='utf-8')); ... ISRCTN ..."`
- `Get-ChildItem -Recurse -Filter 'retrieval_ledger.json' -Path '.\cache\balanced-crystalloids-vs-saline-mortality\snapshots\2026-09-15r3-search_v2' | Select-Object -First 5 -ExpandProperty FullName`
- `python -c "import json; p='cache/balanced-crystalloids-vs-saline-mortality/snapshots/2026-09-15r3-search_v2/retrieval_ledger.json'; ..."`
- `python -c "import json; d=json.load(open('outputs/search_v2/candidates-2026-09-15r3-all.json',encoding='utf-8')); c=d['candidates']['balanced-crystalloids-vs-saline-mortality']; ..."`
- `python -c "import json,collections; d=json.load(open('outputs/search_v2/candidates-2026-09-15r3-all.json',encoding='utf-8')); ..."`
- `apply_patch Add File: lane_r4/compare_r2_r3.py`
- `python lane_r4/compare_r2_r3.py > lane_r4/07-r2-vs-r3.txt`
- `Get-Content -Raw -LiteralPath '.\lane_r4\07-r2-vs-r3.txt'`
- `python -c "from pathlib import Path; ... lane_r4/03..07 file sizes ..."`
- `python -c "import json; d=json.load(open('outputs/search_v2/candidates-2026-09-15r3-all.json',encoding='utf-8')); print(len(d.get('topics',{}))); ..."`
- `python -c "import json; d=json.load(open('outputs/search_v2/candidates-2026-09-15r3-all.json',encoding='utf-8')); ... ISRCTN state counts ..."`
- `Select-String -Path '.\lane_r4\05-recall-r3.txt' -Pattern '^TOTAL: found'`
- `Select-String -Path '.\lane_r4\06-register-r3.txt' -Pattern 'within kind|whole engine'`
- `Select-String -Path '.\lane_r4\03-run-r3.stdout' -Pattern 'RUN r3 scope=all|done .*: RAN|refresh ' | Select-Object -Last 10`
- `apply_patch Add File: lane_r4/make_r4_report.py`
- `python lane_r4/make_r4_report.py  # first attempt failed before report write due UTF-16 redirected input`
- `python -c "import re; from pathlib import Path; text=Path('lane_r4/07-r2-vs-r3.txt').read_text(encoding='utf-8'); ..."  # confirmed UTF-16 decode issue`
- `Format-Hex -Path '.\lane_r4\04-status-r3.txt' -Count 8  # failed: this PowerShell lacks -Count`
- `Format-Hex -Path '.\lane_r4\05-recall-r3.txt' -Count 8  # failed: this PowerShell lacks -Count`
- `Format-Hex -Path '.\lane_r4\06-register-r3.txt' -Count 8  # failed: this PowerShell lacks -Count`
- `Format-Hex -Path '.\lane_r4\07-r2-vs-r3.txt' -Count 8  # failed: this PowerShell lacks -Count`
- `python -c "from pathlib import Path; ... read first bytes of lane_r4/03..07 ..."`
- `python -c "from pathlib import Path; ... detect UTF-16LE BOM in lane_r4/04..07 ..."`
- `python -c "from pathlib import Path; ... rewrite lane_r4/03..07 from utf-16 to utf-8 ..."`
- `apply_patch Update File: lane_r4/make_r4_report.py`
- `python lane_r4/make_r4_report.py`
- `Get-Content -TotalCount 1 -LiteralPath '.\LANE-R4-REPORT.md'`
- `python -c "from pathlib import Path; ... verify LANE-R4-REPORT.md and lane_r4/03..07 existence, size, first bytes ..."`
- `python -c "import json,collections; d=json.load(open('outputs/search_v2/candidates-2026-09-15r3-all.json',encoding='utf-8')); ... verify topics/candidates ..."`
- `git status --short`
- `apply_patch Update File: lane_r4/make_r4_report.py`
- `python lane_r4/make_r4_report.py`
