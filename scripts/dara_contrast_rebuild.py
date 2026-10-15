"""Targeted sequential rebuild and exact HEAD result/membership comparison."""
import json, os, subprocess, sys, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from scripts.dara_contrast_measure import cohort
from harness import registry_contrast as rc
LOG=ROOT/'.codex_logs'

def read(p): return json.loads(Path(p).read_text(encoding='utf8'))
def state(r):
 return {o['name']:{'result':{k:v for k,v in (o.get('result') or {}).items() if k in ('k','estimate','ci_low','ci_high','pi_low','pi_high','tau2','Q','i2','pool_refused')},'members':[{k:t.get(k) for k in ('id','label','effect','ci_low','ci_high')} for t in o.get('trials',[])]} for o in r['outcomes']}
def preflight():
 out=[]
 for s in cohort():
  cfg=read(ROOT/f'topics/{s}.json');doc=rc.load(cfg);data=read(ROOT/f'cache/{s}/records.json');records={str(r['id']):r for r in data['records']+data.get('ctgov',[])}
  review=read(ROOT/f'docs/reviews/{s}/review.json')
  for pid in sorted({t['id'].replace('PMID ','') for o in review['outcomes'] for t in o.get('trials',[])}):
   r=records.get(pid,{});a=rc.assess(r,cfg,doc)
   if a and a['decision']!='include':out.append({'slug':s,'id':pid,'nct':r.get('nct'),'decision':a['decision'],'abstract':r.get('abstract'),'arms':a['arms']})
 (LOG/'dara_contrast_preflight.txt').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf8')
 print('nonpassing pooled members',len(out),flush=True)
 print([(r['slug'],r['id'],r['decision']) for r in out],flush=True)

def rebuild():
 os.environ['CAPTAIN_NO_WORKTREE_SCAN']='1'
 os.environ['PYTHONUTF8']='1'
 from scripts import build_topic
 slugs=cohort();assert len(slugs)==32, len(slugs)
 allrows=[]
 selected=slugs+['daratumumab-rrmm-pfs-bench']
 if '--resume' in sys.argv:
  prior=read(LOG/'dara_contrast_rebuild_results.txt')
  (LOG/'dara_contrast_round1_results.txt').write_text(json.dumps(prior,indent=2,ensure_ascii=False),encoding='utf8')
  # The fallback refinement affects add-on scopes only. Replay every enabled
  # topic, plus every unfinished topic, sequentially under the final code.
  allrows=[r for r in prior if r['status']=='PASS' and not rc.enabled(read(ROOT/f"topics/{r['slug']}.json"))]
  done={r['slug'] for r in allrows}
  selected=[s for s in selected if s not in done]
 for s in selected:
  p=f'docs/reviews/{s}/review.json'
  r=subprocess.run(['git','show','HEAD:'+p],capture_output=True)
  base=json.loads(r.stdout) if r.returncode==0 else None
  before=read(ROOT/p)
  print('BUILD',s,flush=True)
  try:
   build_topic.main(s,'2026-10-15',['scripts/dara_contrast_rebuild.py'])
   after=read(ROOT/p)
   b=state(base) if base else None;a=state(after)
   changes={k:{'before':(b or {}).get(k),'after':a.get(k)} for k in set(b or {})|set(a) if (b or {}).get(k)!=a.get(k)}
   row={'slug':s,'status':'PASS','baseline':'HEAD' if base else 'HEAD_ABSENT','changes':changes,'workspace_before':state(before),'after':a}
  except Exception as e:
   traceback.print_exc();row={'slug':s,'status':'FAIL','error':str(e)}
  allrows.append(row)
  (LOG/'dara_contrast_rebuild_results.txt').write_text(json.dumps(allrows,indent=2,ensure_ascii=False),encoding='utf8')
  print('DONE',s,row['status'],'changed',len(row.get('changes',{})),flush=True)
if __name__=='__main__':
 preflight() if '--preflight' in sys.argv else rebuild()
