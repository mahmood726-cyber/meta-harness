"""Generate comparison from review output, source XML, and machine-read figure cells."""
import json,re,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
LOG=ROOT/'.codex_logs'
SLUG='daratumumab-rrmm-pfs-bench'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
def report():
 r=read(ROOT/f'docs/reviews/{SLUG}/review.json');data=read(ROOT/f'cache/{SLUG}/records.json');o=r['outcomes'][0];result=o['result']
 xml=ET.parse(ROOT/'cache/benchmarks/v1/PMC10519573.xml')
 cells=read(LOG/'dara_contrast_forest_ocr.txt')['cells']
 effects=[c for c in cells if re.fullmatch(r'\d+\.\d+\s*\[\d+\.\d+,\s*\d+\.\d+\]',c[1])]
 rows=[]
 for tr in xml.findall(".//table-wrap[@id='T1']/table/tbody/tr"):
  cols=[''.join(td.itertext()) for td in tr.findall('td')]
  author=next(c for c in cells if norm(c[1])==norm(cols[0]))
  y=sum(p[1] for p in author[0])/4
  cell=min(effects,key=lambda c:abs(sum(p[1] for p in c[0])/4-y))
  assert abs(sum(p[1] for p in cell[0])/4-y)<8
  nct=cols[2];trial=next(t for t in o['trials'] if t['family_id']==nct)
  rec=next(x for x in data['records'] if x['id']==trial['id'].removeprefix('PMID '))
  names=[w for w in re.findall(r'\b[A-Z][A-Z-]{3,}\b',rec['abstract']) if w not in {'BACKGROUND','METHODS','PATIENTS','RESULTS','CONCLUSIONS','FINDINGS','INTERPRETATION','FUNDING','RRMM'}]
  rows.append({'trial':names[0],'nct':nct,'report':trial['id'],'effect':trial['effect'],'ci_low':trial['ci_low'],'ci_high':trial['ci_high'],'comparator_author':cols[0],'comparator_cell':cell[1],'regimen_cell':cols[5],'source':trial['source']})
 lines=['# Daratumumab contrast repair','',
 'The old arm_index retained common/differing drug sets but discarded experimental/comparator roles. It explicitly abstained on absent arm data; screen.run swallowed index errors into an empty index. Daratumumab had no measured arm index and did not enable the older arm_object contract. These routes could not enforce the requested contrast.','',
 'Existing rule locations: harness/screen.py::run and _background_only_randomised_contrast; harness/armcontrast.py::build_arm_index and background_only_inclusion; harness/arm_object.py::assess. The latter is enabled only by a topic arm_object declaration. The new implementation is harness/registry_contrast.py, invoked at eligibility by screen.run and checked again before automatic report-family promotion.', '',
 'The new parser reads saved registry arms and intervention links, then treatment descriptions in the abstract when registry contrast is unreadable. Unknown contrasts are UNRESOLVED and cannot pool. Registry labels/descriptions resolve standard-therapy arms, add-on backbone subsets, matching placebo, and post-progression crossover. No trial ID or topic slug is used by the eligibility rule.','',
 'Scope assumption: intervention_agents plus an add-on/containing-regimen declaration in topic intervention/question. A replacement comparison is not classified as an add-on merely because it has an agent vocabulary.','',
 '| Input | Static/dynamic |','|---|---|','| Plant expectations | Static, user-supplied IDs; never parser rules |','| Topic scope and agent vocabulary | Dynamic topic JSON |','| Registry arms and report links | Dynamic AACT rows, cached without local paths |','| Pool and per-trial effects | Dynamic existing pipeline output |','| Comparator HR cells | Dynamic OCR of XML-linked CC BY Figure 4; visually checked |','',
 '## Rebuilt pool','',f"k={result['k']}; pooled HR={result['estimate']}; 95% CI {result['ci_low']}–{result['ci_high']}; 95% PI {result['pi_low']}–{result['pi_high']}.",'',
 '| Trial | NCT | Our report | Our HR (95% CI) | Comparator study | Figure 4 cell (verbatim OCR) |','|---|---|---|---|---|---|']
 for x in rows:lines.append(f"| {x['trial']} | {x['nct']} | {x['report']} | {x['effect']} ({x['ci_low']}–{x['ci_high']}) | {x['comparator_author']} | `{x['comparator_cell']}` |")
 lines+=['','Source: cache/benchmarks/v1/PMC10519573.xml, Table 1 (study-to-NCT mapping) and Figure 4 graphic medi-102-e35319-g004.jpg. Figure retrieved via Europe PMC supplementaryFiles API. OCR cells and bounding boxes: dara_contrast_forest_ocr.txt. Figure values were not entered into pooling.','',
 'Comparator and benchmark include the same trial identities but do not consistently use the same report/analysis. The values above are quoted from the comparator itself, not substituted from primary articles.','', '## Effect source spans','']
 for x in rows:lines += [f"- {x['trial']} ({x['report']}): {x['source']}"]
 lines+=['','## Contrast decisions','', '| Record | Decision | Rule |','|---|---|---|']
 for d in r['screening']['records']:
  if d['rule_id'] in {'X-CONTRAST','UNRESOLVED-CONTRAST'}:lines.append(f"| {d['id']} | {d['decision']} | {d['rule_id']} |")
 path=LOG/'dara_contrast_rebuild_results.txt'
 if path.exists():
  builds=read(path);lines+=['','## Sequential rebuild versus HEAD','',f'Completed entries: {len(builds)}. This section is provisional until all requested builds complete.','', '| Topic | Build | Changed outcomes |','|---|---|---|']
  for b in builds:lines.append(f"| {b['slug']} | {b['status']} | {len(b.get('changes',{}))} |")
  for b in builds:
   if b.get('changes'):lines+=['',f"### {b['slug']}",'','```json',json.dumps(b['changes'],indent=2,ensure_ascii=False),'```']
 (LOG/'dara_contrast_report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
 (LOG/'dara_contrast_pool.txt').write_text(json.dumps({'result':{k:result[k] for k in ['k','estimate','ci_low','ci_high','pi_low','pi_high']},'trials':rows},indent=2,ensure_ascii=False),encoding='utf8')
 print('report generated',flush=True)
if __name__=='__main__':report()
