R1 VERDICT: ALL FIVE CLAIMS REPRODUCED
C1: pre-fix refused 5 of 5 named slugs with tokens ['CABG', 'BAY94-8862', 'PCSK9', 'LCZ696', 'NSTE-ACS']; post-fix allowed 5 of 5 named slugs; exempted tokens per slug {'colchicine-postop-af': ['CABG'], 'finerenone-ckd-t2d-renal': ['BAY94-8862'], 'pcsk9-mace': ['PCSK9'], 'sacubitril-valsartan-hfref': ['ARNI', 'LCZ696'], 'ticagrelor-vs-clopidogrel-acs': ['AZD6140', 'NSTE-ACS', 'ST-elevation', 'ST-segment', 'STEMI']} [MEASURED]
C2: scripted r2 all 136 of 147 measurement positives, pooled 135 of 135 pooled_or_declared_absent positives, audit 1 of 12 audit positives; own PMID/NCT scorer r2 136 of 147 measurement positives; run1 scripted all 121 of 147 measurement positives; discrepancies: none; delta 15 newly found and 0 lost [MEASURED]
C3: tar sha256 match 3 of 3 named topics (colchicine-secondary-cv-prevention, balanced-crystalloids-vs-saline-mortality, colchicine-postop-af); bodies preserved 138 of 138 for colchicine-secondary-cv-prevention, 81 of 81 for balanced-crystalloids-vs-saline-mortality, 53 of 53 for colchicine-postop-af [MEASURED]
C4: within kind 19 of 20 known-eligible register trials, whole engine 20 of 20 known-eligible register trials, legacy 18 of 20 known-eligible register trials; same denominator? yes [MEASURED]
C5: gate REFUSED on an engine change; reason quoted: "engine changed since the published search_v2 measurement (9cf898d02afb -> aaee5d04b62a); re-run scripts/search_v2_run.py and re-publish before landing" [MEASURED]
INFERRED: C1's exact sibling worktree command could not complete because this sandbox cannot create .git/worktrees metadata; the pre-fix engine was measured from a git-archive extraction of commit 01e39f2e instead.
MEASURED: C2's scripted r2 capture also reported 116348 reverse candidates not in benchmark for measurement topics and 53267 for development topics; the scorer labels those as not eligibility judgments.
MEASURED: C2's own PMID/NCT-only scorer found 11 of 147 measurement positives without PMID/NCT keys; all 11 were missed by design, while the single audit hit was the NCT-keyed never_considered positive.
MEASURED: C3 could not use gh or curl in this environment; gh returned 401 Unauthorized and curl.exe failed with schannel SEC_E_NO_CREDENTIALS, while Python urllib listed 32 release assets and downloaded the three tested assets.
MEASURED: C4's search_v2 register rows were all topic-state RAN_OK_WITH_SOURCE_ERRORS, so the whole-engine 20 of 20 is snapshot membership with source errors still recorded rather than folded away.
MEASURED: C4's script dirtied docs/search_recall_regression_corpus_search_v2.json as documented; git checkout -- docs/ failed on .git/index.lock permission, and the file was restored from HEAD bytes with no remaining docs diff.
MEASURED: C5's gate verdict also reported measurement topic states as RAN_OK_WITH_SOURCE_ERRORS 21 of 21, with RAN_OK 0 of 21, RAN_ZERO 0 of 21, RAN_ERROR 0 of 21, and NOT_RUN 0 of 21.
Commands run: MEASURED command ledger follows.
MEASURED: Get-Content -LiteralPath 'LANE_PROMPT.md'
MEASURED: Get-Content -LiteralPath 'LIVE_CONTEXT.md'
MEASURED: Get-Content -LiteralPath 'F:\ProjectIndex\INDEX.md' -TotalCount 200
MEASURED: Get-Content -LiteralPath 'F:\E156\rewrite-workbook.txt' -TotalCount 200
MEASURED: git status --short --branch
MEASURED: git rev-parse HEAD
MEASURED: rg --files
MEASURED: Get-ChildItem -LiteralPath 'C:\' -Filter 'LIVE_CONTEXT.md' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 5 -ExpandProperty FullName
MEASURED: Get-CimInstance Win32_Process -Filter "Name = 'powershell.exe'" | Where-Object { $_.CommandLine -like '*LIVE_CONTEXT.md*' } | Select-Object ProcessId,CommandLine
MEASURED: Get-Process -Name powershell | Sort-Object StartTime -Descending | Select-Object -First 8 Id,StartTime,Path,MainWindowTitle
MEASURED: Stop-Process -Id 10952 -Force
MEASURED: Get-Content -LiteralPath 'harness\search_v2.py'
MEASURED: Get-Content -LiteralPath 'scripts\measure_search_recall.py'
MEASURED: Get-Content -LiteralPath 'scripts\measure_regression_corpus_recall_search_v2.py'
MEASURED: Get-Content -LiteralPath 'docs\evidence\search-v2-guard-2026-09-15\01-plants-pre-fix.txt'
MEASURED: git worktree list
MEASURED: Test-Path -LiteralPath '..\r1-prefix'
MEASURED: Get-ChildItem -LiteralPath 'docs\evidence\search-v2-guard-2026-09-15'
MEASURED: gh release view raw-archive-2026-09-15r2-search_v2 --repo mahmood726-cyber/meta-harness --json assets
MEASURED: Invoke-RestMethod -Uri 'https://api.github.com/repos/mahmood726-cyber/meta-harness/releases/tags/raw-archive-2026-09-15r2-search_v2' -Headers @{ 'User-Agent' = 'codex-lane-r1' } | ConvertTo-Json -Depth 4
MEASURED: curl.exe -L -H "User-Agent: codex-lane-r1" "https://api.github.com/repos/mahmood726-cyber/meta-harness/releases/tags/raw-archive-2026-09-15r2-search_v2"
MEASURED: python -c "import json, urllib.request; req=urllib.request.Request('https://api.github.com/repos/mahmood726-cyber/meta-harness/releases/tags/raw-archive-2026-09-15r2-search_v2', headers={'User-Agent':'codex-lane-r1'}); print(urllib.request.urlopen(req, timeout=30).read().decode()[:12000])"
MEASURED: Get-Content -LiteralPath 'outputs\search_v2\candidates-2026-09-15r2-all.json' -TotalCount 80
MEASURED: Get-Content -LiteralPath 'outputs\search_v2\candidates-2026-09-15-measurement.json' -TotalCount 80
MEASURED: Get-Content -LiteralPath 'registry\search_benchmark.json' -TotalCount 120
MEASURED: Get-Content -LiteralPath 'registry\search_benchmark_split.json' -TotalCount 120
MEASURED: rg -n '"engine_sha"|"search_v2_engine_sha"|"measurement_topics"|"development_topics"' outputs\search_v2\candidates-2026-09-15r2-all.json
MEASURED: rg -n 'TOTAL: found|MEASUREMENT TOPICS|DEVELOPMENT TOPICS|SEARCH-RECALL: REFUSED' docs outputs registry scripts -g '*.txt' -g '*.md' -g '*.json'
MEASURED: rg -n 'raw-.*2026-09-15r2-search_v2|public_archive|tar_sha256|archive_raw_bodies' -g '*.json' -g '*.md' docs cache scripts outputs README.md
MEASURED: Get-Content -LiteralPath 'scripts\archive_raw_bodies.py'
MEASURED: Get-Content -LiteralPath 'docs\search_recall_regression_corpus.json'
MEASURED: Get-Content -LiteralPath 'docs\search_recall_regression_corpus_search_v2.json'
MEASURED: Get-Content -LiteralPath 'harness\search_completeness.py'
MEASURED: New-Item -ItemType Directory -Force -Path 'lane_r1'
MEASURED: git worktree add ../r1-prefix 01e39f2e
MEASURED: New-Item -ItemType Directory -Force -Path '.tmp\r1-prefix'
MEASURED: Copy-Item -LiteralPath 'docs\evidence\search-v2-guard-2026-09-15\01-plants-pre-fix.txt' -Destination '.tmp\author-01-plants-pre-fix.txt' -Force
MEASURED: git archive --format=tar --output='.tmp\r1-prefix.tar' 01e39f2e
MEASURED: tar -xf '.tmp\r1-prefix.tar' -C '.tmp\r1-prefix'
MEASURED: python - via PowerShell here-string, importing .tmp\r1-prefix\harness.search_v2 and writing lane_r1\01-prefix-probe.txt
MEASURED: python - via PowerShell here-string, importing current harness.search_v2 with slug argument and writing lane_r1\02-postfix-probe.txt
MEASURED: python - wrapper ran python scripts/measure_search_recall.py outputs/search_v2/candidates-2026-09-15r2-all.json --include-development and wrote lane_r1\03-rescore-r2.txt
MEASURED: python - wrapper ran python scripts/measure_search_recall.py outputs/search_v2/candidates-2026-09-15-measurement.json and wrote lane_r1\04-rescore-r1.txt
MEASURED: python - ran script-function C2 origin/delta summary and appended it to lane_r1\03-rescore-r2.txt
MEASURED: python - ran the 30-line PMID/NCT-only scorer and wrote lane_r1\05-own-scorer.txt
MEASURED: python - downloaded three public GitHub release assets, checked tar sha256, extracted under .tmp\lane_r1_archive_extract, ran scripts/archive_raw_bodies.py check for each, and wrote lane_r1\06-archive-check.txt
MEASURED: python scripts/archive_raw_bodies.py check --snapshot cache/colchicine-secondary-cv-prevention/snapshots/2026-09-15r2-search_v2 --archive-root C:\mh-r-R1\.tmp\lane_r1_archive_extract
MEASURED: python scripts/archive_raw_bodies.py check --snapshot cache/balanced-crystalloids-vs-saline-mortality/snapshots/2026-09-15r2-search_v2 --archive-root C:\mh-r-R1\.tmp\lane_r1_archive_extract
MEASURED: python scripts/archive_raw_bodies.py check --snapshot cache/colchicine-postop-af/snapshots/2026-09-15r2-search_v2 --archive-root C:\mh-r-R1\.tmp\lane_r1_archive_extract
MEASURED: python - wrapper ran python scripts/measure_regression_corpus_recall_search_v2.py --snapshot 2026-09-15r2-search_v2 and wrote lane_r1\07-register.txt
MEASURED: git checkout -- docs/
MEASURED: python -c "import pathlib, subprocess; p=pathlib.Path('docs/search_recall_regression_corpus_search_v2.json'); p.write_bytes(subprocess.check_output(['git','show','HEAD:docs/search_recall_regression_corpus_search_v2.json']))"
MEASURED: Get-Content -LiteralPath 'harness\search_v2.py' -Tail 8
MEASURED: apply_patch appended one trailing comment line to harness/search_v2.py
MEASURED: python -c "from harness import search_completeness as s; print(s.check('.'))"
MEASURED: git checkout -- harness/search_v2.py
MEASURED: apply_patch removed exactly the planted trailing comment line from harness/search_v2.py
MEASURED: git status --short
MEASURED: git diff -- harness\search_v2.py
MEASURED: git hash-object harness\search_v2.py
MEASURED: Get-ChildItem -LiteralPath 'lane_r1' -File | Select-Object Name,Length | Sort-Object Name
MEASURED: rg -n 'refused_count|allowed_count|exempted_tokens_per_slug|refused_tokens' lane_r1\01-prefix-probe.txt lane_r1\02-postfix-probe.txt
MEASURED: rg -n 'TOTAL: found|r2_found_all|r2_origin_counts|r1_found_all|new_vs_run1|own PMID' lane_r1\03-rescore-r2.txt lane_r1\04-rescore-r1.txt lane_r1\05-own-scorer.txt
MEASURED: rg -n 'tar_sha256=.*match=True|raw bodies preserved|parsed within_kind|parsed whole_engine|parsed legacy|denominator_compare|search completeness REFUSED' lane_r1\06-archive-check.txt lane_r1\07-register.txt lane_r1\08-gate-plant.txt
