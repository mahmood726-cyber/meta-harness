P VERDICT: 18 of 20 plants FIRED; DID-NOT-FIRE: D1c, D3i

## Plants
D1a-class: FIRED -- CTGOV_CONDITION_INTERVENTION refused NAME_SEEDED: PCSK9
D1a-pop: FIRED -- PUBMED_CONCEPT_QUERY refused NAME_SEEDED: FOURIER
D1b: FIRED -- CTGOV_CONDITION_INTERVENTION refused NAME_SEEDED: PCSK9
D1c: DID-NOT-FIRE -- query built with sealed empty collision list; reason=vocabulary matches its seal; exempted=['FOURIER', 'PCSK9']
D2: FIRED -- C:/mh-r-P/.tmp/lane-p-d2-flodrkyc/harness/search_v2_pathlib_plant.py opens or names isolated target search_benchmark.json
D3i: DID-NOT-FIRE -- search_v2 measurement current for engine a57dc45d6824 (outputs/search_v2/candidates-2026-09-15r3-all.json); states: RAN_OK 0 of 21; RAN_OK_WITH_SOURCE_ERRORS 20 of 21; RAN_ZERO 0 of 21; RAN_ERROR 0...
D3ii: FIRED -- search completeness REFUSED: colchicine-postop-af/pubmed_concept_query#1: RAN_ZERO with 3 records || states: RAN_OK 0 of 21; RAN_OK_WITH_SOURCE_ERRORS 21 of 21; RAN_ZERO 0 of 21; RAN_ERROR 0 of 21;...
D3iii: FIRED -- search completeness REFUSED: engine changed since the published search_v2 measurement (057dc45d6824 -> a57dc45d6824); re-run scripts/search_v2_run.py and re-publish before landing | docs/search_rec...
D3iv: FIRED -- search completeness REFUSED: docs/search_recall_regression_corpus_search_v2.json was measured on engine ['000000000000'] not a57dc45d6824 || states: RAN_OK 0 of 21; RAN_OK_WITH_SOURCE_ERRORS 21 of ...
D3v: FIRED -- search completeness REFUSED: docs/evidence/search-v2-measurement-2026-09-15/README.md does not name engine blob a57dc45d6824 -- the number is not published || states: RAN_OK 0 of 21; RAN_OK_WITH_SO...
D4a: FIRED -- TARGET production_record.check_artifact: head=0123456789abcdef0123456789abcdef01234567 base=none tree=artifact:manifest-sha256=78e6bfa68353e5b8 files=4 C:/mh-r-P/.tmp/lane-p-d4-fg9auggu/manifest.js...
D4b: FIRED -- TARGET production_record.check_artifact: head=0123456789abcdef0123456789abcdef01234567 base=none tree=artifact:manifest-sha256=78e6bfa68353e5b8 files=4 C:/mh-r-P/.tmp/lane-p-d4-fg9auggu/manifest.js...
D4c: FIRED -- TARGET production_record.check_artifact: head=0123456789abcdef0123456789abcdef01234567 base=none tree=artifact:manifest-sha256=78e6bfa68353e5b8 files=4 C:/mh-r-P/.tmp/lane-p-d4-fg9auggu/manifest.js...
D5a: FIRED -- raw bodies preserved: 1 of 2; DIGEST MISMATCH: raw/source1/body1.txt
D5b: FIRED -- raw bodies preserved: 0 of 2; DIGEST MISMATCH: raw/source1/body1.txt | NOT PRESERVED: raw/source1/body2.txt (not in snapshot; not in archive C:\mh-r-P\.tmp\lane-p-d5-0y5e6spo\archive)
D6a: FIRED -- lost banner block b6f0ec4ee42a22f99043b2d7d326c38eae34e7e26e01545b2b91a66f891d3eb6: What this is A reproducible harness that builds meta-analyses from a committed protocol, and publishes each as a ...
D6b: FIRED -- lost banner block b6f0ec4ee42a22f99043b2d7d326c38eae34e7e26e01545b2b91a66f891d3eb6: What this is A reproducible harness that builds meta-analyses from a committed protocol, and publishes each as a ...
D7i: FIRED -- json has 12 objects, report says NEW 14 | could not re-derive N: [Errno 2] No such file or directory: 'C:\\mh-r-P\\cache\\colchicine-postop-af\\snapshots\\2026-09-15r2-search_v2\\records.json'
D7ii: FIRED -- verdict without quote: ['35268478'] | could not re-derive N: [Errno 2] No such file or directory: 'C:\\mh-r-P\\cache\\colchicine-postop-af\\snapshots\\2026-09-15r2-search_v2\\records.json'
D7iii: FIRED -- verdict not in list: ['NCT07569328'] | could not re-derive N: [Errno 2] No such file or directory: 'C:\\mh-r-P\\cache\\colchicine-postop-af\\snapshots\\2026-09-15r2-search_v2\\records.json'

## D1(c) Finding
D1c DID-NOT-FIRE means a benchmark acronym present in edited sealed vocabulary built successfully when the monkeypatched seal had an empty collision list. The real sealer registry reports 11 of 278 benchmark positives have a resolvable registered acronym and FOURIER present=False; therefore the real collision list would not have caught FOURIER for pcsk9-mace.

## Captures
- lane_p/01-d1-vocabulary.txt
- lane_p/02-d2-isolation.txt
- lane_p/03-d3-search-completeness.txt
- lane_p/04-d4-production-record.txt
- lane_p/05-d5-raw-archive.txt
- lane_p/06-d6-honest-ratchet.txt
- lane_p/07-d7-verification-adjudicate.txt

## git status --porcelain
```text
?? LANE-P-REPORT.md
?? LANE_PROMPT.md
?? lane.log
?? lane.pid
?? lane.winpid
?? lane_p/
```

## Commands Run
- `Get-Content -LiteralPath 'LANE_PROMPT.md'`
- `Test-Path -LiteralPath 'F:\ProjectIndex\INDEX.md'; Test-Path -LiteralPath 'F:\E156\rewrite-workbook.txt'; if (Test-Path -LiteralPath 'LIVE_CONTEXT.md') { Get-Content -LiteralPath 'LIVE_CONTEXT.md' }`
- `git status --short`
- `Get-Content -LiteralPath 'F:\ProjectIndex\INDEX.md' -TotalCount 80`
- `Get-Content -LiteralPath 'F:\E156\rewrite-workbook.txt' -TotalCount 80`
- `rg --files`
- `Get-Content -LiteralPath 'harness/search_v2.py'`
- `Get-Content -LiteralPath 'scripts/seal_search_vocabulary.py'`
- `Get-Content -LiteralPath 'tests/test_search_benchmark_isolation.py'`
- `Get-Content -LiteralPath 'harness/search_completeness.py'`
- `Get-Content -LiteralPath 'tests/test_search_completeness.py'`
- `Get-Content -LiteralPath 'scripts/production_record.py'`
- `Get-Content -LiteralPath 'tests/test_production_record.py'; Get-Content -LiteralPath 'tests/test_production_record_deploy_target.py'`
- `Get-Content -LiteralPath 'scripts/archive_raw_bodies.py'`
- `Get-Content -LiteralPath 'tests/test_fulltext.py'; Get-Content -LiteralPath 'tests/test_retrieval_class.py'`
- `Get-Content -LiteralPath 'harness/honest_ratchet.py'`
- `Get-Content -LiteralPath 'tests/test_honest_ratchet.py'; Get-Content -LiteralPath 'tests/test_honest_states_renderable.py'`
- `rg -n "archive_raw|DIGEST MISMATCH|NOT PRESERVED|raw bodies preserved" -S .`
- `Get-Content -LiteralPath 'scripts/verification_adjudicate.py'`
- `rg -n "verification_adjudicate|verdict without quote|json has|verdict not in list|HARVEST" tests scripts docs -S`
- `Get-Content -LiteralPath 'tests/test_verified_effects.py'; Get-Content -LiteralPath 'tests/test_verified_override.py'; Get-Content -LiteralPath 'tests/test_verify_all_target.py'`
- `Get-ChildItem -LiteralPath 'outputs\search_v2\verification' -Directory | Select-Object -First 20 -ExpandProperty Name`
- `Get-Content -LiteralPath 'registry\search_completeness.json'; Get-ChildItem -LiteralPath 'outputs\search_v2' | Select-Object -First 20 Name`
- `Get-Content -LiteralPath 'topics\pcsk9-mace.json'; Get-Content -LiteralPath 'protocols\pcsk9-mace.md' -TotalCount 120`
- `Get-Content -LiteralPath 'registry\search_vocabulary_seal.json' -TotalCount 120`
- `rg -n '"pcsk9-mace"|"FOURIER"|"fourier"' registry\search_vocabulary_seal.json registry\search_benchmark.json cache\pcsk9-mace\records.json cache\pcsk9-mace\snapshots -S`
- `Get-Content -LiteralPath 'outputs\search_v2\verification\balanced-crystalloids-vs-saline-mortality\LANE-V-balanced-crystalloids-vs-saline-mortality-REPORT.md' -TotalCount 5; Get-Content -LiteralPath 'outputs\search_v2\verification\balanced-crystalloids-vs-saline-mortality\balanced-crystalloids-vs-saline-mortality.json' -TotalCount 80`
- `Get-Content -LiteralPath 'docs\ratchet_acknowledgements.json' -TotalCount 80`
- `python - <<'PY' ... PY  # failed in PowerShell; no files written`
- `rg -n "VERDICTS: NEW [0-9]+; ELIGIBLE_RCT [1-9]" outputs\search_v2\verification -g "LANE-V-*-REPORT.md"`
- `@' ... honest_ratchet.blocks docs/index.html ... '@ | python -  # stdout hit cp1252 encode error after printing initial blocks; no files written`
- `@' ... search_completeness.check('.') ... '@ | python -`
- `python scripts\seal_search_vocabulary.py --check`
- `$env:PYTHONIOENCODING='utf-8'; @'<this in-memory lane runner>'@ | python -`

## Internal Subprocess Commands From Plant Runner
- `C:\Users\mahmo\AppData\Local\Programs\Python\Python313\python.exe scripts/seal_search_vocabulary.py --check`
- `C:\Users\mahmo\AppData\Local\Programs\Python\Python313\python.exe C:\mh-r-P\.tmp\lane-p-d4-fg9auggu\pr\scripts\production_record.py check-artifact --manifest C:\mh-r-P\.tmp\lane-p-d4-fg9auggu\manifest.json --tar C:\mh-r-P\.tmp\lane-p-d4-fg9auggu\bad-diff.tar  # cwd=C:\mh-r-P\.tmp\lane-p-d4-fg9auggu`
- `C:\Users\mahmo\AppData\Local\Programs\Python\Python313\python.exe C:\mh-r-P\.tmp\lane-p-d4-fg9auggu\pr\scripts\production_record.py check-artifact --manifest C:\mh-r-P\.tmp\lane-p-d4-fg9auggu\manifest.json --tar C:\mh-r-P\.tmp\lane-p-d4-fg9auggu\bad-extra.tar  # cwd=C:\mh-r-P\.tmp\lane-p-d4-fg9auggu`
- `C:\Users\mahmo\AppData\Local\Programs\Python\Python313\python.exe C:\mh-r-P\.tmp\lane-p-d4-fg9auggu\pr\scripts\production_record.py check-artifact --manifest C:\mh-r-P\.tmp\lane-p-d4-fg9auggu\manifest.json --tar C:\mh-r-P\.tmp\lane-p-d4-fg9auggu\good.tar  # cwd=C:\mh-r-P\.tmp\lane-p-d4-fg9auggu`
- `git status --porcelain  # cwd=C:\mh-r-P`
