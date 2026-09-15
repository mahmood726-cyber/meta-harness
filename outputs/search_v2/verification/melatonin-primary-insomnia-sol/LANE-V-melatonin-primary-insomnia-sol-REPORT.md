V-melatonin-primary-insomnia-sol VERDICTS: NEW 29; ELIGIBLE_RCT 1; ELIGIBLE_RCT_NO_PRIMARY 2; NOT_RCT 0; WRONG_* 13; DUPLICATE_OF_ACCOUNTED 2; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 11
automated screen agreed on 3 of 29 verified
r2 includes 38 of 1141; already accounted for 9; NEW 29
All counts above are MEASURED from the commands listed below.

## Population
- MEASURED r2 records: 1141
- MEASURED r2 automated includes: 38
- MEASURED already accounted for among r2 includes: 9
- MEASURED NEW includes verified in this lane: 29
- MEASURED NOT_VERIFIED_CAP: 0; N <= 150, so no cap was applied.
- INFERRED note: NCT snapshot records expose allocation/masking/conditions/interventions/has_results but not overall_status; registry-only quotes therefore use available CT.gov-derived snapshot fields.

## ELIGIBLE_RCT ids with titles
- 8795804: Melatonin and insomnia.

## DUPLICATE_OF_ACCOUNTED pairs
- 21091391 -> already accounted PMID 20712869 / NCT00397189 (same ClinicalTrials.gov registry ID).
- NCT00397189 -> already accounted PMID 20712869 / NCT00397189 (same registered trial).

## Verdict Counts
- MEASURED ELIGIBLE_RCT: 1
- MEASURED ELIGIBLE_RCT_NO_PRIMARY: 2
- MEASURED NOT_RCT: 0
- MEASURED WRONG_*: 13
- MEASURED DUPLICATE_OF_ACCOUNTED: 2
- MEASURED UNDECIDABLE_FROM_RECORD: 0
- MEASURED NOT_VERIFIED_CAP: 0
- MEASURED REGISTRY_ONLY_NO_PUBLICATION: 11

## Static-vs-dynamic hardcode disclosure
| Item | Status | Basis |
|---|---|---|
| Denominator and counts | dynamic / MEASURED | Computed from r2 snapshot, legacy screen command, and served review JSON. |
| Verdict labels | static / source-backed | Manually assigned from each record's quoted title/abstract or registry fields. |
| Quotes | static / source-backed | Copied from the snapshot record fields used for the verdict. |
| Raw HTTP bodies | dynamic absence / MEASURED | No PubMed efetch was needed because every NEW PMID had a non-empty snapshot abstract. |

## Commands Run
- `Get-Content -Raw -LiteralPath .\LANE_PROMPT.md`
- `if (Test-Path -LiteralPath 'F:\ProjectIndex\INDEX.md') { Get-Content -Raw -LiteralPath 'F:\ProjectIndex\INDEX.md' } elseif (Test-Path -LiteralPath 'C:\ProjectIndex\INDEX.md') { Get-Content -Raw -LiteralPath 'C:\ProjectIndex\INDEX.md' } else { Write-Output 'PROJECT_INDEX_NOT_FOUND' }`
- `if (Test-Path -LiteralPath 'F:\E156\rewrite-workbook.txt') { Get-Content -Raw -LiteralPath 'F:\E156\rewrite-workbook.txt' } elseif (Test-Path -LiteralPath 'C:\E156\rewrite-workbook.txt') { Get-Content -Raw -LiteralPath 'C:\E156\rewrite-workbook.txt' } else { Write-Output 'REWRITE_WORKBOOK_NOT_FOUND' }`
- `git status --short`
- `Get-Content -Raw -LiteralPath .\protocols\melatonin-primary-insomnia-sol.md`
- `Get-Content -Raw -LiteralPath .\topics\melatonin-primary-insomnia-sol.json`
- `Get-Content -Raw -LiteralPath .\docs\reviews\melatonin-primary-insomnia-sol\review.json`
- `python -c \"import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/melatonin-primary-insomnia-sol.json',encoding='utf-8')); d=json.load(open('cache/melatonin-primary-insomnia-sol/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))\"`
- `python -c \"import json; p='cache/melatonin-primary-insomnia-sol/snapshots/2026-09-15r2-search_v2/records.json'; d=json.load(open(p,encoding='utf-8')); print(type(d).__name__); print(d.keys() if isinstance(d,dict) else len(d)); print('records',len(d.get('records',[]))); print('decisions',len(d.get('screening',{}).get('decisions',[])))\"`
- `python -c review/outcome structure inspection for docs/reviews/melatonin-primary-insomnia-sol/review.json`
- `python -c r2 include decision counter and first include inspection`
- `python -c first snapshot record key inspection`
- `python -c denominator/list command (failed once with SyntaxError due quoting)`
- `PowerShell here-string piped to python -: measured r2 includes/accounted/NEW and printed first-pass new-record details`
- `rg -n \"NCT07120880|NCT07695246|NCT06476392|NCT06600633|NCT06062953|NCT05440734|NCT02333149|NCT02798367|NCT00397189|NCT00230737|NCT00869128\" .`
- `Get-ChildItem -Recurse -File -LiteralPath .\cache\melatonin-primary-insomnia-sol | Select-Object -ExpandProperty FullName`
- `PowerShell here-string piped to python -: printed NCT snapshot records`
- `PowerShell here-string piped to python -: inspected retrieval_ledger.json for NCT records`
- `PowerShell here-string piped to python -: printed final 29-record NEW list`
- `PowerShell here-string piped to python -: inspected records 21091391, 21887103, 19888921, NCT00940550, 18261024`
- `PowerShell here-string piped to python -: checked all NEW PMID abstracts were non-empty`
- `PowerShell here-string piped to python -: wrote lane_v/melatonin-primary-insomnia-sol.json, lane_v/melatonin-primary-insomnia-sol-raw/, and LANE-V-melatonin-primary-insomnia-sol-REPORT.md`
