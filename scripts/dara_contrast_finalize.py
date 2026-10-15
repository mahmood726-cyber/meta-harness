"""Complete screening membership audit against named HEAD files and refresh report."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.dara_contrast_measure import cohort
from scripts.dara_contrast_report import report
LOG=ROOT/'.codex_logs'
rows=json.loads((LOG/'dara_contrast_rebuild_results.txt').read_text(encoding='utf8'))
completed={r['slug'] for r in rows if r['status']=='PASS'}
out=[]
for s in cohort():
 if s not in completed:continue
 p=f'docs/reviews/{s}/review.json'
 b=subprocess.run(['git','show','HEAD:'+p],capture_output=True,check=True)
 before=json.loads(b.stdout);after=json.loads((ROOT/p).read_text(encoding='utf8'))
 bb={str(d['id']):d for d in before['screening']['records']};aa={str(d['id']):d for d in after['screening']['records']}
 changes=[{'id':i,'before':bb.get(i,{}).get('decision'),'after':aa.get(i,{}).get('decision'),'rule':aa.get(i,{}).get('rule_id'),'reason':aa.get(i,{}).get('reason')} for i in sorted(bb.keys()|aa.keys()) if bb.get(i,{}).get('decision')!=aa.get(i,{}).get('decision')]
 out.append({'slug':s,'changes':changes})
(LOG/'dara_contrast_screen_changes.txt').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf8')
report()
p=LOG/'dara_contrast_report.md';text=p.read_text(encoding='utf8')
legacy=[r for r in rows if r['slug'] in cohort()]
text+='\n## Verification and coverage\n\n'
text+=f"Legacy builds complete: {len(legacy)}/{len(cohort())}; failed builds: {sum(r['status']!='PASS' for r in legacy)}; topics with pooled-result/membership changes: {sum(bool(r.get('changes')) for r in legacy)}.\n\n"
text+=f"Screening decisions compared for {len(out)} topics; topics with changes: {sum(bool(r['changes']) for r in out)}.\n\n"
for r in out:
 if r['changes']:text+=f"### Screening: {r['slug']}\n\n```json\n"+json.dumps(r['changes'],indent=2,ensure_ascii=False)+'\n```\n\n'
from harness import registry_contrast
active=[slug for slug in cohort() if registry_contrast.enabled(json.loads((ROOT/f'topics/{slug}.json').read_text(encoding='utf8')))]
text+='Add-on enforcement in legacy topics (derived from declarations): '+', '.join(active)+'. The new benchmark is also covered.\n\n'
text+='Focused/regression tests: see dara_contrast_regression_tests.txt. Browser contract: dara_contrast_ui.txt. Five source/result consistency checks: dara_contrast_second_pass.txt. No commits.\n'
if len(legacy)==len(cohort()) and all(r['status']=='PASS' for r in rows):
 text=text.replace(f'Completed entries: {len(rows)}. This section is provisional until all requested builds complete.',f'Completed entries: {len(rows)}. All requested builds completed sequentially.')
p.write_text(text,encoding='utf8')
print('legacy complete',len(legacy),'pool changes',sum(bool(r.get('changes')) for r in legacy),'screen changes',sum(bool(r['changes']) for r in out))
