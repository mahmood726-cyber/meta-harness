V-colchicine-postop-af VERDICTS: NEW 14; ELIGIBLE_RCT 1; ELIGIBLE_RCT_NO_PRIMARY 6; NOT_RCT 0; WRONG_* 0; DUPLICATE_OF_ACCOUNTED 5; UNDECIDABLE 2; NOT_VERIFIED_CAP 0
automated screen agreed on 7 of 14 verified

r2 includes 22 of 540
already accounted for 8
NEW 14

Measurement labels: all counts in the first two lines and population lines are MEASURED from the named JSON files by the artifact-writing validation command. Verdict labels and duplicate-pair interpretations are INFERRED from the quoted snapshot title/abstract plus typed identifier metadata.

ELIGIBLE_RCT ids with titles (could move the primary POAF pool):
- 35268478 - Colchicine for Prevention of Atrial Fibrillation after Cardiac Surgery in the Early Postoperative Period.

DUPLICATE_OF_ACCOUNTED pairs:
- NCT04224545 -> PMID 36286314 (declared-absent; same NCT04224545 / COCS) INFERRED from record metadata and titles.
- NCT03015831 -> PMID 32720823 (pooled; same NCT03015831 / END-AF Low Dose) INFERRED from record metadata and titles.
- NCT01552187 -> PMID 25172965 (pooled; same NCT01552187 / COPPS-2) INFERRED from record metadata and titles.
- 21884871 -> PMID 22090167 (declared-absent; same NCT00128427 / COPPS) INFERRED from record metadata and titles.
- 20805112 -> PMID 22090167 (declared-absent; same NCT00128427 / COPPS) INFERRED from record metadata and titles.

Commands run:
1. `Get-Content -Raw -LiteralPath .\LANE_PROMPT.md`
2. `if (Test-Path -LiteralPath 'F:\ProjectIndex\INDEX.md') { Get-Content -TotalCount 80 -LiteralPath 'F:\ProjectIndex\INDEX.md' } else { Write-Output 'F:\ProjectIndex\INDEX.md unavailable' }`
3. `if (Test-Path -LiteralPath 'F:\E156\rewrite-workbook.txt') { Get-Content -TotalCount 80 -LiteralPath 'F:\E156\rewrite-workbook.txt' } else { Write-Output 'F:\E156\rewrite-workbook.txt unavailable' }`
4. `git status --short`
5. `Get-Content -Raw -LiteralPath .\protocols\colchicine-postop-af.md`
6. `Get-Content -Raw -LiteralPath .\topics\colchicine-postop-af.json`
7. `Get-Content -Raw -LiteralPath .\docs\reviews\colchicine-postop-af\review.json`
8. `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/colchicine-postop-af.json',encoding='utf-8')); d=json.load(open('cache/colchicine-postop-af/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
9. `python -c "import json; p='cache/colchicine-postop-af/snapshots/2026-09-15r2-search_v2/records.json'; d=json.load(open(p,encoding='utf-8')); print(type(d).__name__, d.keys()); print('records', len(d.get('records',[]))); dec=d.get('screening',{}).get('decisions') or d.get('screening',{}).get('records') or []; print('decisions', len(dec)); print('include', sum(1 for x in dec if x.get('decision')=='include')); print('first_record_keys', sorted(d.get('records',[{}])[0].keys())); print('first_decision_keys', sorted(dec[0].keys()) if dec else [])"`
10. `python -c "import json; d=json.load(open('docs/reviews/colchicine-postop-af/review.json',encoding='utf-8')); print('top_keys', sorted(d.keys())); print('outcome keys', [o.get('name') or o.get('outcome') or o.get('id') for o in d.get('outcomes',[])][:5]); import pprint; po=d.get('outcomes',[{}])[0] if d.get('outcomes') else {}; print('primary_keys', sorted(po.keys())); print('trials', po.get('trials')); print('declared_absent_trials', po.get('declared_absent_trials'))"`
11. `python -c <long local new-include inspection one-liner> (failed: PowerShell newline quoting SyntaxError)`
12. `@'<Python stdin: compute NEW includes and print records>'@ | python - (failed: year sort TypeError)`
13. `@'<Python stdin: compute NEW includes and print records with normalized year sort>'@ | python -`
14. `@'<Python stdin: print full snapshot abstracts for PMID NEW records>'@ | python -`
15. `@'<Python stdin: inspect accounted/shared NCT records for duplicate links>'@ | python -`
16. `@'<Python stdin: write lane_v artefacts and validate counts/quotes>'@ | python - (failed: one quote exceeded 300 chars)`
17. `@'<Python stdin: write lane_v artefacts and validate counts/quotes>'@ | python -`

Validation: MEASURED JSON object count equals NEW; category counts sum to NEW; all non-UNDECIDABLE/non-cap verdicts have non-empty quotes <=300 characters; no PubMed efetch was needed, so the raw HTTP body directory is empty.
