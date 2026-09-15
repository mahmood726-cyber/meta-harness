V-colchicine-recurrent-pericarditis VERDICTS: NEW 3; ELIGIBLE_RCT 0; ELIGIBLE_RCT_NO_PRIMARY 0; NOT_RCT 0; WRONG_* 0; DUPLICATE_OF_ACCOUNTED 0; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 3
automated screen agreed on 0 of 3 verified

r2 includes 6 of 646; already accounted for 3; NEW 3
MEASURED legacy includes: 21873705, 23992557, 24694983.
MEASURED primary pooled trials in served review: 21873705, 24694983.
MEASURED primary declared-absent trials in served review: 23992557.
MEASURED NEW includes by lane rule: NCT00128414, NCT00128453, NCT00235079.

ELIGIBLE_RCT ids with titles:
- None.

DUPLICATE_OF_ACCOUNTED pairs:
- None classified as DUPLICATE_OF_ACCOUNTED.

Registry-only links to accounted reports:
- NCT00128414 -> pooled PMID 21873705 (CORP), MEASURED by shared NCT/acronym in the r2 snapshot records.
- NCT00128453 -> declared-absent PMID 23992557 (ICAP), MEASURED by shared NCT in the r2 snapshot records.
- NCT00235079 -> pooled PMID 24694983 (CORP-2), MEASURED by shared NCT/acronym in the r2 snapshot records.

Notes:
- The three NEW records are NCT-only registry records with no PMID in the snapshot, so they are registrations, not trial reports.
- The snapshot NCT records materialize conditions, interventions, allocation, masking, and has_results, but not overall_status; that absence is stated in each JSON note.
- No PubMed efetch was run for verdicting because no NEW PMID record had an empty or truncated abstract.
- No HTTP body was newly fetched or relied on beyond committed snapshot records, so lane_v/colchicine-recurrent-pericarditis-raw/ is intentionally empty.

Commands run:
- `Get-Content -LiteralPath 'F:\ProjectIndex\INDEX.md' -TotalCount 80`
- `Get-Content -LiteralPath 'F:\E156\rewrite-workbook.txt' -TotalCount 80`
- `Get-Content -LiteralPath '.\LIVE_CONTEXT.md' -TotalCount 120` (failed: file not present in this checkout)
- `Get-Content -LiteralPath '.\LANE_PROMPT.md'`
- `git status --short`
- `Get-Content -LiteralPath '.\protocols\colchicine-recurrent-pericarditis.md'`
- `Get-Content -LiteralPath '.\topics\colchicine-recurrent-pericarditis.json'`
- `Get-Content -LiteralPath '.\docs\reviews\colchicine-recurrent-pericarditis\review.json'`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/colchicine-recurrent-pericarditis.json',encoding='utf-8')); d=json.load(open('cache/colchicine-recurrent-pericarditis/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
- `python - <<'PY' ... PY` (failed: Bash heredoc syntax rejected by PowerShell before Python ran)
- `python -c "import json, pathlib; d=json.load(open('cache/colchicine-recurrent-pericarditis/snapshots/2026-09-15r2-search_v2/records.json',encoding='utf-8')); recs=d.get('records', []); decs=d.get('screening',{}).get('decisions',[]); print('top_keys', sorted(d.keys())); print('records', len(recs)); print('decisions', len(decs)); print('record_keys', sorted(recs[0].keys()) if recs else []); print('decision_keys', sorted(decs[0].keys()) if decs else []); print('include_decisions', sum(1 for x in decs if x.get('decision')=='include'))"`
- `python -c "import json; d=json.load(open('docs/reviews/colchicine-recurrent-pericarditis/review.json',encoding='utf-8')); print('top_keys', sorted(d.keys())); outs=d.get('outcomes',[]); print('outcomes', len(outs)); print('outcome0_keys', sorted(outs[0].keys()) if outs else []); print('primary_trials', outs[0].get('trials') if outs else None); print('declared_absent_trials', d.get('declared_absent_trials')); print('declared_absent_outcome0', outs[0].get('declared_absent_trials') if outs else None)"`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/colchicine-recurrent-pericarditis.json',encoding='utf-8')); legacy=json.load(open('cache/colchicine-recurrent-pericarditis/records.json',encoding='utf-8')); m=_dedup(legacy, cfg.get('pivotal_trials')); print('legacy_includes', sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
- `python -c "import json; r=json.load(open('cache/colchicine-recurrent-pericarditis/snapshots/2026-09-15r2-search_v2/records.json',encoding='utf-8')); recs={x['id']:x for x in r['records']}; decs=[x for x in r['screening']['decisions'] if x.get('decision')=='include']; print('includes', len(decs)); [print(json.dumps({'id':d['id'],'id_type':d.get('id_type'),'rule_id':d.get('rule_id'),'reason':d.get('reason'),'span':d.get('span'),'title':recs[d['id']].get('title'),'pmid':recs[d['id']].get('pmid'),'nct':recs[d['id']].get('nct'),'doi':recs[d['id']].get('doi'),'year':recs[d['id']].get('year'),'abstract':(recs[d['id']].get('abstract') or '')[:500]}, ensure_ascii=False)) for d in decs]"`
- `python -c "import json; d=json.load(open('cache/colchicine-recurrent-pericarditis/snapshots/2026-09-15r2-search_v2/records.json',encoding='utf-8')); ids={'NCT00128414','NCT00128453','NCT00235079'}; [print(json.dumps(r, ensure_ascii=False, indent=2)) for r in d['records'] if r.get('id') in ids]"`
- `rg --files -g '*colchicine*' -g '*.json' -g '*.xml' -g '*.txt'`
- `rg -n "NCT00128414|NCT00128453|NCT00235079|overall_status|overallStatus" cache topics docs protocols`
- `rg --files 'cache/colchicine-recurrent-pericarditis/snapshots/2026-09-15r2-search_v2/raw'`
- `python -c "import json; d=json.load(open('cache/colchicine-recurrent-pericarditis/snapshots/2026-09-15r2-search_v2/raw/INDEX.json',encoding='utf-8')); print(json.dumps(d, ensure_ascii=False, indent=2)[:12000])"`
- `python -c "from pathlib import Path; paths=['cache/colchicine-recurrent-pericarditis/snapshots/2026-09-15r2-search_v2/raw/ctgov_condition_intervention#1/001.json','cache/colchicine-recurrent-pericarditis/snapshots/2026-09-15r2-search_v2/raw/pubmed_nct_link#1/002.json']; [print(p, Path(p).exists(), Path(p).stat().st_size if Path(p).exists() else '') for p in paths]"`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/colchicine-recurrent-pericarditis.json',encoding='utf-8')); legacy=json.load(open('cache/colchicine-recurrent-pericarditis/records.json',encoding='utf-8')); legacy_inc={x['id'] for x in screen.run(_dedup(legacy,cfg.get('pivotal_trials')),cfg)['decisions'] if x['decision']=='include'}; review=json.load(open('docs/reviews/colchicine-recurrent-pericarditis/review.json',encoding='utf-8')); primary=next(o for o in review['outcomes'] if o.get('primary')); pooled={t.get('label') or str(t.get('id','')).replace('PMID ','') for t in primary.get('trials',[])}; absent={t.get('label') or str(t.get('id','')).replace('PMID ','') for t in primary.get('declared_absent_trials',[])}; accounted=legacy_inc|pooled|absent; r2=json.load(open('cache/colchicine-recurrent-pericarditis/snapshots/2026-09-15r2-search_v2/records.json',encoding='utf-8')); recs={r['id']:r for r in r2['records']}; inc=[d for d in r2['screening']['decisions'] if d['decision']=='include']; key=lambda r: r.get('pmid') or r.get('nct') or r.get('doi') or r.get('id'); old=[d for d in inc if key(recs[d['id']]) in accounted]; new=[d for d in inc if key(recs[d['id']]) not in accounted]; print('legacy', sorted(legacy_inc)); print('pooled', sorted(pooled)); print('absent', sorted(absent)); print('accounted', sorted(accounted)); print('r2 records',len(r2['records'])); print('r2 includes',len(inc)); print('already accounted',len(old), sorted(d['id'] for d in old)); print('NEW',len(new), sorted(d['id'] for d in new)); print(json.dumps([{**{k:recs[d['id']].get(k) for k in ['id','id_type','pmid','nct','title','year','conditions','interventions','allocation','masking','has_results','acronym']}, 'screen_rule': d.get('rule_id'), 'span': d.get('span')} for d in new], ensure_ascii=False, indent=2))"`
- `New-Item -ItemType Directory -Force -Path '.\lane_v\colchicine-recurrent-pericarditis-raw' | Out-Null`
