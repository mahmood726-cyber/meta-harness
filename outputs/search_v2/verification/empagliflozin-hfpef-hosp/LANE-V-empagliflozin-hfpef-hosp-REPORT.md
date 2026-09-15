V-empagliflozin-hfpef-hosp VERDICTS: NEW 10; ELIGIBLE_RCT 0; ELIGIBLE_RCT_NO_PRIMARY 1; NOT_RCT 0; WRONG_* 0; DUPLICATE_OF_ACCOUNTED 9; UNDECIDABLE 0; NOT_VERIFIED_CAP 0
automated screen agreed on 1 of 10 verified

r2 includes 14 of 3867; already accounted for 4; NEW 10
MEASURED: N=10 is below the 150-record cap, so NOT_VERIFIED_CAP=0.
MEASURED: no PubMed efetch or other HTTP body was used; all verdict quotes came from local r2 snapshot title/abstract fields.

ELIGIBLE_RCT ids with titles:
None.

ELIGIBLE_RCT_NO_PRIMARY ids:
- 33351892 - Effect of empagliflozin on exercise ability and symptoms in heart failure patients with reduced and preserved ejection fraction, with and without type 2 diabetes.

DUPLICATE_OF_ACCOUNTED pairs:
- INFERRED: 34459213 -> pooled PMID 34449189 (EMPEROR-Preserved acronym/title; snapshot NCT field is NCT03057977).
- MEASURED: 36098051 -> pooled PMID 34449189 (NCT03057951; EMPEROR-Preserved).
- INFERRED: 37062866 -> pooled PMID 34449189 (EMPEROR-Preserved secondary analysis).
- INFERRED: 37278451 -> pooled PMID 34449189 (EMPEROR-Preserved trial title/abstract).
- MEASURED: 37942723 -> pooled PMID 34449189 (NCT03057951; EMPEROR-Preserved plain-language summary).
- INFERRED: 38439585 -> pooled PMID 34449189 (EMPEROR-Preserved analysis).
- MEASURED: 39453357 -> pooled PMID 34449189 (NCT03057951; EMPEROR-Preserved post hoc analysis).
- MEASURED: 41493412 -> pooled PMID 34449189 (NCT03057951; EMPEROR-Preserved).
- MEASURED: NCT03057951 -> pooled PMID 34449189 (same NCT as r2 PMID 34449189 record).

Commands run:
- `Get-Content -LiteralPath 'F:\ProjectIndex\INDEX.md' -Raw`
- `Get-Content -LiteralPath 'F:\E156\rewrite-workbook.txt' -Raw`
- `Get-Content -LiteralPath '.\LANE_PROMPT.md' -Raw`
- `Get-Content -LiteralPath '.\LIVE_CONTEXT.md' -Raw` (failed; file absent in this repo)
- `git status --short`
- `Get-Content -LiteralPath '.\protocols\empagliflozin-hfpef-hosp.md' -Raw`
- `Get-Content -LiteralPath '.\topics\empagliflozin-hfpef-hosp.json' -Raw`
- `Get-Content -LiteralPath '.\docs\reviews\empagliflozin-hfpef-hosp\review.json' -Raw`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/empagliflozin-hfpef-hosp.json',encoding='utf-8')); d=json.load(open('cache/empagliflozin-hfpef-hosp/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
- `python -c "import json; p='cache/empagliflozin-hfpef-hosp/snapshots/2026-09-15r2-search_v2/records.json'; d=json.load(open(p,encoding='utf-8')); print(type(d).__name__); print(d.keys() if isinstance(d,dict) else 'list'); print('records', len(d.get('records', d) if isinstance(d,dict) else d)); print('decisions', len(d.get('screening',{}).get('decisions', d.get('screening',{}).get('records', [])) if isinstance(d,dict) else 0))"`
- `python -c "import json; d=json.load(open('docs/reviews/empagliflozin-hfpef-hosp/review.json',encoding='utf-8')); import pprint; print(d.keys()); print('outcomes type', type(d.get('outcomes')).__name__); print('declared_absent_trials keys?', d.get('declared_absent_trials', 'MISSING')); print('primary outcome keys', (d.get('outcomes') or [{}])[0].keys() if isinstance(d.get('outcomes'),list) and d.get('outcomes') else None)"`
- `python -c "import json; r=json.load(open('docs/reviews/empagliflozin-hfpef-hosp/review.json',encoding='utf-8')); o=[x for x in r['outcomes'] if x.get('primary')][0]; print(json.dumps({'trials': o.get('trials', []), 'declared_absent_trials': o.get('declared_absent_trials', [])}, indent=2))"`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/empagliflozin-hfpef-hosp.json',encoding='utf-8')); legacy=sorted(x['id'] for x in screen.run(_dedup(json.load(open('cache/empagliflozin-hfpef-hosp/records.json',encoding='utf-8')), cfg.get('pivotal_trials')),cfg)['decisions'] if x['decision']=='include'); r2=json.load(open('cache/empagliflozin-hfpef-hosp/snapshots/2026-09-15r2-search_v2/records.json',encoding='utf-8')); recs=r2['records']; decs=r2['screening']['decisions']; inc=[x for x in decs if x.get('decision')=='include']; print('legacy', legacy); print('r2 records',len(recs)); print('r2 includes',len(inc)); print('first include decisions', json.dumps(inc[:10], indent=2)[:4000])"`
- `python -c "import json; d=json.load(open('cache/empagliflozin-hfpef-hosp/snapshots/2026-09-15r2-search_v2/records.json',encoding='utf-8')); print(json.dumps(d['records'][0], indent=2)[:4000])"`
- `python -c "import json; r2=json.load(open('cache/empagliflozin-hfpef-hosp/snapshots/2026-09-15r2-search_v2/records.json',encoding='utf-8')); recs={str(x.get('id')):x for x in r2['records']}; decs=[x for x in r2['screening']['decisions'] if x.get('decision')=='include']; print('n_inc',len(decs),'n_records',len(r2['records'])); ..."`
- `python -c "import json, textwrap; ids=['33351892','34459213','36098051','37062866','37278451','37942723','38439585','39453357','41493412','NCT03057951']; d=json.load(open('cache/empagliflozin-hfpef-hosp/snapshots/2026-09-15r2-search_v2/records.json',encoding='utf-8')); recs={str(x.get('id')):x for x in d['records']}; ..."`
- `python -c "import json; d=json.load(open('cache/empagliflozin-hfpef-hosp/snapshots/2026-09-15r2-search_v2/records.json',encoding='utf-8')); rec=next(x for x in d['records'] if str(x.get('id'))=='NCT03057951'); print(json.dumps(rec, indent=2, ensure_ascii=False))"`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/empagliflozin-hfpef-hosp.json',encoding='utf-8')); legacy=sorted(x['id'] for x in screen.run(_dedup(json.load(open('cache/empagliflozin-hfpef-hosp/records.json',encoding='utf-8')), cfg.get('pivotal_trials')),cfg)['decisions'] if x['decision']=='include'); rv=json.load(open('docs/reviews/empagliflozin-hfpef-hosp/review.json',encoding='utf-8')); primary=next(o for o in rv['outcomes'] if o.get('primary')); ..."`
- `New-Item -ItemType Directory -Force -Path '.\lane_v\empagliflozin-hfpef-hosp-raw'`
- `python -c "import json,re; rows=json.load(open('lane_v/empagliflozin-hfpef-hosp.json',encoding='utf-8')); report=open('LANE-V-empagliflozin-hfpef-hosp-REPORT.md',encoding='utf-8').read().splitlines(); allowed={'ELIGIBLE_RCT','ELIGIBLE_RCT_NO_PRIMARY','NOT_RCT','WRONG_POPULATION','WRONG_INTERVENTION','WRONG_COMPARATOR','WRONG_OUTCOME_ONLY','DUPLICATE_OF_ACCOUNTED','UNDECIDABLE_FROM_RECORD','NOT_VERIFIED_CAP'}; assert len(rows)==10; assert all(r.get('verdict') in allowed for r in rows); assert all(r.get('quote') or r.get('verdict') in {'UNDECIDABLE_FROM_RECORD','NOT_VERIFIED_CAP'} for r in rows); m=re.search(r'NEW (\d+); ELIGIBLE_RCT (\d+); ELIGIBLE_RCT_NO_PRIMARY (\d+); NOT_RCT (\d+); WRONG_\* (\d+); DUPLICATE_OF_ACCOUNTED (\d+); UNDECIDABLE (\d+); NOT_VERIFIED_CAP (\d+)', report[0]); nums=list(map(int,m.groups())); assert nums[0]==sum(nums[1:]); assert nums[0]==len(rows); print('lane_v validation ok')"`
- `git status --short`
