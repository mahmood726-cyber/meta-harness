R2 VERDICT: ADAPTER BUILT, DEFAULT PATH UNCHANGED, PROBE 0 of 0 ISRCTN records not already in the r2 snapshot

## Summary

- Built an opt-in ISRCTN adapter in `harness/search_v2.py`.
- Added source kind `ISRCTN_CONDITION_INTERVENTION` to `harness/acquisition.py`, ledger group `ISRCTN` to `harness/pipeline.py`, and route label `concept query ISRCTN` to `scripts/measure_search_v2_measurement.py`.
- `build_queries(...)` now returns `queries["isrctn"]` and `structural_kinds["isrctn"]`, guarded by `assert_discovery_query_allowed(..., "ISRCTN_CONDITION_INTERVENTION", exempt)`.
- `refresh_topic(..., registries=("ctgov",))` keeps the default registry run on CT.gov only; ISRCTN runs only when the caller passes `registries=("ctgov", "isrctn")` or otherwise includes `"isrctn"`.
- The default path is intentionally unchanged because run r2 is one engine blob on all 32 topics; ISRCTN belongs to the next engine version with its own 32-topic before/after.
- I did not run `scripts/search_v2_run.py` and did not write under `cache/`.

## Adapter Details

- Endpoint: `GET https://www.isrctn.com/api/query/format/default`.
- Page size: `1000`. This matches the existing full-pagination scale used by PubMed/Europe PMC/CT.gov adapters, minimizes requests, and is still explicit pagination rather than a relevance top-N cap.
- Pagination: uses `limit=1000` and increasing `offset` until `offset >= totalCount`; no record cap.
- Rate limiting: sleeps `0.5` seconds between pages.
- Malformed XML, wrong root, missing non-integer `totalCount`, or `totalCount > 0` with no `<fullTrial>` records raises `ValueError`.
- Records carry `id_type: "isrctn"`, canonical `id`/`isrctn`, `title`, `year`, secondary `nct` when present, `acronym`, `conditions`, `interventions`, `source: "isrctn"`, plus compatible empty literature fields.

## Captures

- `lane_r2/00-isrctn-sample.xml`: live `q=colchicine&limit=3` sample, 52,064 bytes, `totalCount=31`, parsed 3 records.
- `tests/fixtures/isrctn_sample.xml`: copied from the saved sample fixture.
- `lane_r2/01-isrctn-live-probe.txt`: direct live probe output.

## Query Grammar Verified

All grammar checks used the ISRCTN XML API via `harness.http.get(...)`, parsed with `xml.etree.ElementTree`, with `limit=1`.

- `q=colchicine OR aspirin`: returned XML with `totalCount=562`, verifying `OR`.
- `q=colchicine AND "chronic obstructive pulmonary disease"`: returned XML with `totalCount=2`, verifying `AND` plus quoted phrase syntax.
- `q=colchicine AND (pericarditis OR pericardial)`: returned XML with `totalCount=1`, verifying parenthesized `OR` inside an `AND`.
- `q="recurrent pericarditis"`: returned well-formed XML with `totalCount=0`, verifying quoted phrases are accepted even when there are no matches.
- The registered development-topic query built from the sealed vocabulary was `(colchicine) AND (pericarditis)` and returned `totalCount=0`.

## Live Probe Numbers

- Topic: `colchicine-recurrent-pericarditis` (DEVELOPMENT).
- Query: `(colchicine) AND (pericarditis)`.
- `totalCount`: 0.
- Records returned: 0.
- Records carrying secondary NCT: 0.
- Missing by ISRCTN id versus `cache/colchicine-recurrent-pericarditis/snapshots/2026-09-15r2-search_v2/records.json`: 0 of 0.
- Missing by secondary NCT versus the same snapshot: 0 of 0.
- Not already in the r2 snapshot by ISRCTN id or NCT: 0 of 0.
- First 5 titles: none.

## Tests

New ISRCTN tests in `tests/test_search_v2_isrctn.py`:

- `test_parse_isrctn_sample_records_have_ids_titles_and_fields`
- `test_parse_isrctn_malformed_payload_raises`
- `test_isrctn_query_guard_refuses_name_seeded_term`
- `test_query_builder_allows_sealed_vocabulary_tokens_for_isrctn`
- `test_isrctn_adapter_paginates_without_record_cap_and_reports_meta`
- `test_refresh_topic_default_does_not_call_isrctn_adapter`

Adjusted existing exact query-shape assertions:

- `tests/test_search_v2.py::test_search_v2_builder_allows_development_drug_codes_without_seeded_trial_names`
- `tests/test_search_v2_guard.py::test_p4_both_answers_guard_alone_refuses_sealed_exemption_allows`

Full finish gate:

- `python -m pytest tests/ -q` -> `635 passed in 166.47s (0:02:46)`.

Focused checks run:

- `python -m pytest tests/test_search_v2_isrctn.py tests/test_search_v2.py tests/test_search_v2_guard.py tests/test_search_v2_run2_engine.py tests/test_search_benchmark_isolation.py -q` -> first run `28 passed, 6 failed`; after updating exact source-kind expectations, `34 passed in 3.32s`.
- `python -m pytest tests/test_production_record_deploy_target.py -q` -> `3 passed in 1.54s`.
- `python -m pytest tests/test_fixstate.py::test_real_store_validates -q` -> `1 passed in 44.42s`.

## Collateral Full-Suite Gate Repair

The first full-suite run failed outside the ISRCTN lane:

- `test_real_store_validates`: generated `docs/fix_ledger.json` and two evidence README fix-state lines were stale after the code/test changes. Fixed by running the repo's generators.
- `test_production_record_deploy_target`: the deploy-target helper treated a copied package under `.tmp` as a git worktree because Git found the parent repo. Fixed `_is_git_worktree` so the resolved git top-level must equal the script package root.

## Diff Summary

Output of `git diff --stat` after implementation and full-suite gate repair:

```text
 docs/evidence/search-v2-2026-09-15/README.md       |   2 +-
 .../search-v2-measurement-2026-09-15/README.md     |   2 +-
 docs/fix_ledger.json                               |   7 +-
 harness/acquisition.py                             |   1 +
 harness/pipeline.py                                |   1 +
 harness/search_v2.py                               | 238 ++++++++++-
 scripts/measure_search_v2_measurement.py           |   1 +
 scripts/production_record.py                       |   9 +-
 tests/fixtures/isrctn_sample.xml                   | 441 ---------------------
 tests/test_search_v2.py                            |   2 +
 tests/test_search_v2_guard.py                      |   7 +-
 11 files changed, 250 insertions(+), 461 deletions(-)
```

## Commands Run

```text
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\LANE_PROMPT.md'
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\LIVE_CONTEXT.md'
Get-Content -Raw -LiteralPath 'F:\ProjectIndex\INDEX.md'
Get-Content -Raw -LiteralPath 'F:\E156\rewrite-workbook.txt'
git status --short
Get-Content -LiteralPath 'C:\mh-r-R2\SEARCH_REBUILD_HANDOVER.md' -TotalCount 220
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\docs\evidence\search-v2-measurement-2026-09-15\12-international-registries-probe.txt'
rg -n "def _ctgov_search_records|def _ctgov_record|def _source_run|def refresh_topic|sealed_vocabulary|assert_discovery_query_allowed|def build_queries|SOURCE_KINDS|_LEDGER_SOURCE_GROUPS|ROUTE_LABELS" harness scripts tests
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\tests\test_search_benchmark_isolation.py'
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\tests\test_search_v2_guard.py'
$p='C:\mh-r-R2\harness\search_v2.py'; $l=Get-Content -LiteralPath $p; $l[0..180]
$p='C:\mh-r-R2\harness\search_v2.py'; $l=Get-Content -LiteralPath $p; $l[200..390]
$p='C:\mh-r-R2\harness\search_v2.py'; $l=Get-Content -LiteralPath $p; $l[600..735]
$p='C:\mh-r-R2\harness\search_v2.py'; $l=Get-Content -LiteralPath $p; $l[760..890]
$p='C:\mh-r-R2\harness\search_v2.py'; $l=Get-Content -LiteralPath $p; $l[970..1085]
$p='C:\mh-r-R2\harness\acquisition.py'; $l=Get-Content -LiteralPath $p; $l[90..125]
$p='C:\mh-r-R2\harness\pipeline.py'; $l=Get-Content -LiteralPath $p; $l[1115..1140]
$p='C:\mh-r-R2\scripts\measure_search_v2_measurement.py'; $l=Get-Content -LiteralPath $p; $l[60..90]
$p='C:\mh-r-R2\harness\search_v2.py'; $l=Get-Content -LiteralPath $p; $l[390..610]
rg -n "def _record_id|def _normalise_nct|def _normalise_pmid|id_type|isrctn|found_by|records.json" harness tests scripts
$p='C:\mh-r-R2\harness\search_v2.py'; $l=Get-Content -LiteralPath $p; $l[1085..1235]
$p='C:\mh-r-R2\harness\acquisition.py'; $l=Get-Content -LiteralPath $p; $l[500..570]
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\tests\test_search_v2.py'
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\tests\test_search_v2_run2_engine.py'
$p='C:\mh-r-R2\harness\registry_first.py'; $l=Get-Content -LiteralPath $p; $l[210..275]
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\tests\test_registry_multi.py'
Get-Content -LiteralPath 'C:\mh-r-R2\tests\fixtures\isrctn_sample.xml' -TotalCount 80
rg -n "refresh_topic\(|_source_run\(|build_queries\(" tests harness scripts | Select-Object -First 120
$p='C:\mh-r-R2\harness\acquisition.py'; $l=Get-Content -LiteralPath $p; $l[450..505]
$p='C:\mh-r-R2\harness\acquisition.py'; $l=Get-Content -LiteralPath $p; $l[620..650]
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\harness\http.py'
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\topics\colchicine-recurrent-pericarditis.json'
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\protocols\colchicine-recurrent-pericarditis.md'
Get-Content -LiteralPath 'C:\mh-r-R2\cache\colchicine-recurrent-pericarditis\snapshots\2026-09-15r2-search_v2\records.json' -TotalCount 80
Test-Path -LiteralPath 'C:\mh-r-R2\cache\colchicine-recurrent-pericarditis\snapshots\2026-09-15r2-search_v2\records.json'
$dir='C:\mh-r-R2\lane_r2'; New-Item -ItemType Directory -Force -Path $dir | Out-Null; Invoke-WebRequest -Uri 'https://www.isrctn.com/api/query/format/default?q=colchicine&limit=3' -OutFile (Join-Path $dir '00-isrctn-sample.xml'); Get-Item -LiteralPath (Join-Path $dir '00-isrctn-sample.xml') | Select-Object FullName,Length
python -c "from harness import http; import os; os.makedirs('lane_r2', exist_ok=True); data=http.get('https://www.isrctn.com/api/query/format/default', {'q':'colchicine','limit':3}); open('lane_r2/00-isrctn-sample.xml','wb').write(data); print(len(data))"
python -c "import xml.etree.ElementTree as ET; p='lane_r2/00-isrctn-sample.xml'; root=ET.parse(p).getroot(); print(root.tag, root.attrib); trials=list(root); print('children', [c.tag.rsplit('}',1)[-1] for c in trials[:5]], 'n', len(trials)); t=trials[0]; print('trial tag/attrs', t[0].tag.rsplit('}',1)[-1] if t.tag.rsplit('}',1)[-1]=='fullTrial' else t.tag, (t[0].attrib if t.tag.rsplit('}',1)[-1]=='fullTrial' else t.attrib)); trial=t[0] if t.tag.rsplit('}',1)[-1]=='fullTrial' else t; print('trial children', [c.tag.rsplit('}',1)[-1] for c in trial[:30]]); desc=next((c for c in trial if c.tag.rsplit('}',1)[-1]=='trialDescription'), None); print('desc children', [c.tag.rsplit('}',1)[-1] for c in list(desc)[:80]]); print('title', ''.join(desc.find('.//{*}title').itertext()).strip()[:200]); print('acronym', ''.join(desc.find('.//{*}acronym').itertext()).strip()); print('condition tags', [(e.tag.rsplit('}',1)[-1], ''.join(e.itertext()).strip()[:120]) for e in desc.iter() if 'condition' in e.tag.rsplit('}',1)[-1].lower()][:20]); print('intervention tags', [(e.tag.rsplit('}',1)[-1], ''.join(e.itertext()).strip()[:160]) for e in desc.iter() if 'intervention' in e.tag.rsplit('}',1)[-1].lower() or 'treatment' in e.tag.rsplit('}',1)[-1].lower()][:25])"
python -c "import xml.etree.ElementTree as ET; root=ET.parse('lane_r2/00-isrctn-sample.xml').getroot(); for i,full in enumerate(list(root),1): ..."
python -c "from harness import http; import xml.etree.ElementTree as ET; queries=['colchicine AND pericarditis','(colchicine) AND (pericarditis)','colchicine OR aspirin','\" recurrent pericarditis\','colchicine ..."
python -c "from harness import http; import xml.etree.ElementTree as ET; dq=chr(34); queries=['colchicine AND pericarditis','(colchicine) AND (pericarditis)','colchicine OR aspirin',dq+'recurrent pericarditis'+dq,'colchicine AND '+dq+'chronic obstructive pulmonary disease'+dq]; ..."
python -c "from harness import http; import xml.etree.ElementTree as ET; qs=['pericarditis','recurrent','pericardial','colchicine']; ..."
python -c "from harness import http; import xml.etree.ElementTree as ET; qs=['colchicine pericarditis','colchicine + pericarditis','colchicine AND (pericarditis OR pericardial)','(colchicine OR aspirin) AND pericarditis','colchicine AND COPD']; ..."
python -c "from harness import http; import xml.etree.ElementTree as ET; qs=['colchicine AND (pericarditis)','(colchicine) AND pericarditis','(colchicine OR colchicine) AND (pericarditis OR pericarditis)','colchicine AND (pericarditis OR xxxxx)']; ..."
$p='C:\mh-r-R2\harness\search_v2.py'; $l=Get-Content -LiteralPath $p; $l[180..225]
$p='C:\mh-r-R2\harness\pipeline.py'; $l=Get-Content -LiteralPath $p; $l[1140..1165]
$p='C:\mh-r-R2\harness\screen.py'; $l=Get-Content -LiteralPath $p; $l[400..435]
rg -n "def expand_intervention|def _dedupe_strings|CAP_KINDS|reserve_source_id" harness\acquisition.py harness\lexicon.py
$p='C:\mh-r-R2\harness\acquisition.py'; $l=Get-Content -LiteralPath $p; $l[380..450]
apply_patch: add ISRCTN adapter/query/refresh wiring/source labels/new test file
Copy-Item -LiteralPath 'C:\mh-r-R2\lane_r2\00-isrctn-sample.xml' -Destination 'C:\mh-r-R2\tests\fixtures\isrctn_sample.xml' -Force; Get-Item -LiteralPath 'C:\mh-r-R2\tests\fixtures\isrctn_sample.xml' | Select-Object FullName,Length
python -m pytest tests/test_search_v2_isrctn.py tests/test_search_v2.py tests/test_search_v2_guard.py tests/test_search_v2_run2_engine.py tests/test_search_benchmark_isolation.py -q
apply_patch: update existing exact structural_kinds test expectations
python -m pytest tests/test_search_v2_isrctn.py tests/test_search_v2.py tests/test_search_v2_guard.py tests/test_search_v2_run2_engine.py tests/test_search_benchmark_isolation.py -q
PowerShell here-string piped to python -: build colchicine query, call _isrctn_search_records directly, compare to r2 snapshot, write lane_r2/01-isrctn-live-probe.txt
python -m pytest tests/ -q
$p='C:\mh-r-R2\tests\test_fixstate.py'; $l=Get-Content -LiteralPath $p; $l[420..470]
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\tests\test_production_record_deploy_target.py'
rg -n "check_artifact|ref not resolvable|production_record|render_fix_ledger|rewrite_fixstate" -S .
git diff --stat
$p='C:\mh-r-R2\scripts\production_record.py'; $l=Get-Content -LiteralPath $p; $l[1..240]
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\harness\target.py'
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\docs\fix_ledger.json' | Select-String -Pattern 'search-v2' -Context 0,2
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\scripts\rewrite_fixstate_lines.py'
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\scripts\render_fix_ledger.py'
apply_patch: tighten scripts/production_record.py _is_git_worktree root detection
python -m pytest tests/test_production_record_deploy_target.py -q
python scripts/render_fix_ledger.py
python scripts/rewrite_fixstate_lines.py
python -m pytest tests/test_fixstate.py::test_real_store_validates -q
python -m pytest tests/ -q
git diff --stat
git status --short
Get-Content -Raw -LiteralPath 'C:\mh-r-R2\lane_r2\01-isrctn-live-probe.txt'
git diff -- harness/search_v2.py harness/acquisition.py harness/pipeline.py scripts/measure_search_v2_measurement.py tests/test_search_v2.py tests/test_search_v2_guard.py --
Get-ChildItem -LiteralPath 'C:\mh-r-R2\lane_r2' | Select-Object Name,Length
python -c "from harness import search_v2; import pathlib; xml=pathlib.Path('tests/fixtures/isrctn_sample.xml').read_text(encoding='utf-8'); records,total=search_v2._parse_isrctn_records(xml); print(total, len(records), records[0]['id'], records[0]['title'])"
python -c "import json, pathlib; from harness import search_v2; slug='colchicine-recurrent-pericarditis'; root=pathlib.Path(search_v2.ROOT); cfg=json.loads((root/'topics'/f'{slug}.json').read_text(encoding='utf-8')); protocol=(root/'protocols'/f'{slug}.md').read_text(encoding='utf-8'); q=search_v2.build_queries(cfg, protocol, lookup_mesh=False, slug=slug); print(q['isrctn']); print(q['structural_kinds'])"
git diff -- scripts\production_record.py docs\fix_ledger.json docs\evidence\search-v2-2026-09-15\README.md docs\evidence\search-v2-measurement-2026-09-15\README.md --
```
