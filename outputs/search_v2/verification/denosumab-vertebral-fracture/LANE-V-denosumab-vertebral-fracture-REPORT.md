V-denosumab-vertebral-fracture VERDICTS: NEW 34; ELIGIBLE_RCT 1; ELIGIBLE_RCT_NO_PRIMARY 2; NOT_RCT 19; WRONG_* 6; DUPLICATE_OF_ACCOUNTED 2; UNDECIDABLE 4; NOT_VERIFIED_CAP 0
automated screen agreed on 3 of 34 verified
r2 includes 35 of 2569; already accounted for 1; NEW 34

Marks: all counts in the first three lines are MEASURED from the snapshot, legacy cache, and review object; verdict labels are INFERRED from each quoted title/abstract span plus identifier fields already present in the snapshot.
HTTP bodies relied on: 0 (MEASURED); no PubMed efetch was needed because no relied-on PubMed include had an empty or truncated snapshot abstract, and NCT-only records were not supplemented from live HTTP.

## ELIGIBLE_RCT ids with titles
- 21927920: Dose-response study of denosumab on bone mineral density and bone turnover markers in Japanese postmenopausal women with osteoporosis.

## DUPLICATE_OF_ACCOUNTED pairs
- 28546097 -> PMID 19671655 / FREEDOM / NCT00089791: 10 years of denosumab treatment in postmenopausal women with osteoporosis: results from the phase 3 randomised FREEDOM trial and open-label extension.
- NCT00089791 -> PMID 19671655 / FREEDOM / NCT00089791: A Study to Evaluate Denosumab in the Treatment of Postmenopausal Osteoporosis

## Verdict Count Detail (MEASURED)
- ELIGIBLE_RCT: 1
- ELIGIBLE_RCT_NO_PRIMARY: 2
- NOT_RCT: 19
- WRONG_POPULATION: 1
- WRONG_INTERVENTION: 3
- WRONG_COMPARATOR: 2
- WRONG_OUTCOME_ONLY: 0
- DUPLICATE_OF_ACCOUNTED: 2
- UNDECIDABLE_FROM_RECORD: 4
- NOT_VERIFIED_CAP: 0

## Commands run
- `Get-Content -LiteralPath .\LANE_PROMPT.md`
- `if (Test-Path -LiteralPath 'F:\ProjectIndex\INDEX.md') { Get-Content -LiteralPath 'F:\ProjectIndex\INDEX.md' -TotalCount 80 } elseif (Test-Path -LiteralPath 'C:\ProjectIndex\INDEX.md') { Get-Content -LiteralPath 'C:\ProjectIndex\INDEX.md' -TotalCount 80 } else { Write-Output 'INDEX_NOT_AVAILABLE' }`
- `if (Test-Path -LiteralPath 'F:\E156\rewrite-workbook.txt') { Get-Content -LiteralPath 'F:\E156\rewrite-workbook.txt' -TotalCount 80 } elseif (Test-Path -LiteralPath 'C:\E156\rewrite-workbook.txt') { Get-Content -LiteralPath 'C:\E156\rewrite-workbook.txt' -TotalCount 80 } else { Write-Output 'WORKBOOK_NOT_AVAILABLE' }`
- `git status --short`
- `Get-Content -LiteralPath .\protocols\denosumab-vertebral-fracture.md`
- `Get-Content -LiteralPath .\topics\denosumab-vertebral-fracture.json`
- `Get-Content -LiteralPath .\docs\reviews\denosumab-vertebral-fracture\review.json`
- `python -c \"import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/denosumab-vertebral-fracture.json',encoding='utf-8')); d=json.load(open('cache/denosumab-vertebral-fracture/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))\"`
- `python -c \"import json; p='cache/denosumab-vertebral-fracture/snapshots/2026-09-15r2-search_v2/records.json'; d=json.load(open(p,encoding='utf-8')); print(type(d).__name__); print(d.keys() if isinstance(d,dict) else len(d)); print('records', len(d.get('records',[]))); print('decisions', len(d.get('screening',{}).get('decisions',[]))); print('includes', sum(1 for x in d.get('screening',{}).get('decisions',[]) if x.get('decision')=='include'))\"`
- `python -c \"import json,pprint; d=json.load(open('docs/reviews/denosumab-vertebral-fracture/review.json',encoding='utf-8')); ... print primary outcome trials and declared_absent_trials\"`
- `python -c \"import json; p='cache/denosumab-vertebral-fracture/snapshots/2026-09-15r2-search_v2/records.json'; ... print all automated include records, screen rules, identifiers, titles, and abstract snippets\"`
- `python -c \"import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; ... print legacy include ids one per line\"`
- `python -c \"import json; ... print keys/full JSON snippets for 20839290, NCT00089791, and NCT01495000\"`
- `python -c \"import json,re; ... compute NEW include count/order by year desc and PMID/NCT key\"`
- `python -c \"import json,re; ... print decisive keyword sentences for each NEW include\"`
- `rg -n \"NCT00091793|NCT00089791|NCT01495000|NCT01457950|NCT02753283|NCT05278338|NCT07806331\" .`
- `rg -n \"NCT00091793|NCT02753283|TST002|JMT103|MW031|25593843|27189284\" cache topics docs protocols`
- `python -c \"import json; ... print identifier_scope/ghost excerpts and linked records for selected NCTs\"`
- `python -c \"import json; p='cache/denosumab-vertebral-fracture/snapshots/2026-09-15r2-search_v2/raw/INDEX.json'; ... inspect raw index\"`
- `Get-ChildItem -LiteralPath .\cache\denosumab-vertebral-fracture\snapshots\2026-09-15r2-search_v2\raw | Select-Object -First 80 | Format-Table -AutoSize`
- `PowerShell here-string piped to python - (wrote lane_v/denosumab-vertebral-fracture.json, lane_v/denosumab-vertebral-fracture-raw/, and LANE-V-denosumab-vertebral-fracture-REPORT.md; embedded validation passed)`
