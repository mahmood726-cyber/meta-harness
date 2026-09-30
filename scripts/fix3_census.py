"""Offline FIX3 census and full committed-before/in-memory-after ledger."""
from pathlib import Path
import json, sys, subprocess, os
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/'tests'))
BASE='b0ae05a7cf440048ef07338ab2cf756dccf3241a'
SCRATCH=ROOT/'.tmp/fix3'

GUARD=r'''import os, sys, re
from pathlib import Path
ROOT=Path(os.environ['LANE_ROOT']).resolve()
def protected(p):
    if isinstance(p, int) or not isinstance(p, (str, bytes, os.PathLike)): return False
    p=Path(os.fsdecode(p)).resolve()
    return p.is_relative_to(ROOT) and not p.is_relative_to(ROOT/'.tmp')
def audit(event,args):
    if event=='open':
        p,mode,flags=args
        if ((mode and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)) and protected(p):
            raise PermissionError('LANE_PROTECTED_WRITE: '+str(p))
    if event in ('os.remove','os.rmdir','os.mkdir','os.rename','os.replace'):
        for p in args[:2] if event in ('os.rename','os.replace') else args[:1]:
            if protected(p): raise PermissionError('LANE_PROTECTED_WRITE: '+str(p))
    if event=='socket.connect' and args[1][0] not in ('127.0.0.1','::1','localhost'):
        raise PermissionError('LANE_NETWORK_FORBIDDEN')
    if event=='subprocess.Popen':
        exe,argv,cwd,env=args
        # On Windows executable can be None even for a direct argv-list call.
        words=list(argv) if isinstance(argv,(list,tuple)) else re.findall(r'"[^"\n]*"|[^\s"]+',str(argv))
        executable=os.fsdecode(exe) if exe is not None else (str(words[0]).strip('"') if words else '')
        if Path(executable).stem.lower()=='git':
            forbidden={'add','commit','push','checkout','reset','switch','restore','update-index','update-ref','symbolic-ref','init','clean','merge','rebase','fetch','pull','tag','config','branch','rm','mv','stash','gc','prune','repack','worktree','maintenance','reflog','clone','submodule','am','apply','cherry-pick','revert','bisect','notes','replace','-w','--write'}
            normalized=[str(w).strip('"') for w in words]
            # This exact query is read-only and used by fixstate validation.
            if 'branch' in normalized and normalized[normalized.index('branch')+1:] == ['--show-current']:
                forbidden=forbidden-{'branch'}
            if forbidden.intersection(normalized):
                raise PermissionError('LANE_GIT_MUTATION_FORBIDDEN')
sys.addaudithook(audit)
# Old fixture helpers request scratch directly under cwd; relocate only that
# temporary directory request, preserving the test's fixture content and assertions.
import tempfile
_original_mkdtemp = tempfile.mkdtemp
def _lane_mkdtemp(suffix=None, prefix=None, dir=None):
    if dir is not None and Path(dir).resolve() == ROOT:
        dir = ROOT / '.tmp' / 'fix3'
    return _original_mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
tempfile.mkdtemp = _lane_mkdtemp
'''

def environment():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    guard=SCRATCH/'guard'; guard.mkdir(exist_ok=True)
    (guard/'sitecustomize.py').write_text(GUARD, encoding='utf-8')
    env=dict(os.environ, PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0',
             LANE_ROOT=str(ROOT),PYTHONPATH=os.pathsep.join([str(guard),str(ROOT),str(ROOT/'tests')]),
             TEMP=str(SCRATCH),TMP=str(SCRATCH))
    return env

def build(slug):
    from harness import pipeline
    cfg=json.loads((ROOT/'topics'/f'{slug}.json').read_text(encoding='utf-8'))
    records=json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf-8'))
    return pipeline.build_review_core(slug,cfg,records,'fix3-offline')

def snapshot(o):
    return dict(result=o.get('result'), trials=o.get('trials'), absent=o.get('declared_absent_trials'))

if __name__=='__main__':
    if '--worker' in sys.argv:
        try: result=build(sys.argv[-1])
        except Exception as exc: result={'error':type(exc).__name__+': '+str(exc)}
        print(json.dumps(result,ensure_ascii=False));sys.exit()
    env=environment(); ledger={}; rules={k:[] for k in ['TARGET_MEASURE_UNAVAILABLE','TARGET_FIRST_SELECTION','TIMEPOINT_MISMATCH','RESULT_LOCAL_MEASURE','ORIGIN_SOURCE_UNREADABLE','COMMITTED_EXCERPT','UNRESOLVED_MEASURE_ATTRIBUTION','RECURRENT_EVENTS_NOT_FIRST_EVENT_PATIENTS','SEMANTIC_WINDOW_MISMATCH','WITHIN_FAMILY_ADMITTED','DESIGN_ADJUSTED_WITHIN_FAMILY','PUBLISHED_WITHIN_FAMILY_FALLBACK']}; rows=0; errors={}; changes=[]
    from concurrent.futures import ThreadPoolExecutor, as_completed
    env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    def run(path):
        slug=path.stem
        baseproc=subprocess.run(['git','--no-optional-locks','show',f'{BASE}:docs/reviews/{slug}/review.json'],cwd=ROOT,capture_output=True)
        before=json.loads(baseproc.stdout) if baseproc.returncode==0 else {'error':'COMMITTED_REVIEW_MISSING'}
        proc=subprocess.run([sys.executable,__file__,'--worker',slug],env=env,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=300)
        after=json.loads(proc.stdout) if proc.returncode==0 else {'error':proc.stderr}
        receipt=SCRATCH/'topic-receipts';receipt.mkdir(exist_ok=True)
        (receipt/(slug+'.json')).write_text(json.dumps({'before':before,'after':after},ensure_ascii=False),encoding='utf-8')
        print(slug+(': ERROR' if 'error' in after else ': built'),file=sys.stderr,flush=True)
        return slug, {'before':before,'after':after}
    if '--summarize' in sys.argv:
        ledger=json.loads((SCRATCH/'ledger.json').read_text(encoding='utf-8'))
    else:
        with ThreadPoolExecutor(max_workers=2) as pool:
            for future in as_completed([pool.submit(run,p) for p in sorted((ROOT/'topics').glob('*.json'))]):
                slug,pair=future.result();ledger[slug]=pair
        ledger=dict(sorted(ledger.items()))
        (SCRATCH/'ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf-8')
    for slug,pair in ledger.items():
        before,after=pair['before'],pair['after']
        if 'error' in after: errors[slug]=after['error']
        else:
            old={o['name']:o for o in before.get('outcomes',[])}
            for o in after.get('outcomes',[]):
                name=slug+' / '+o['name']; b=old.get(o['name'],{})
                if snapshot(b)!=snapshot(o): changes.append(name)
                for r in o.get('trials',[])+o.get('declared_absent_trials',[]):
                    rows+=1; item=name+' / '+str(r.get('id'))
                    if r.get('timepoint_reason'):
                        rules['SEMANTIC_WINDOW_MISMATCH'].append(item)
                    for code in r.get('lane_refusals',[]):
                        if code in rules: rules[code].append(item)
                    if r in o.get('trials',[]) and r.get('measure_identity') != o.get('target_measure'):
                        rules['WITHIN_FAMILY_ADMITTED'].append(item)
                        if r.get('selected_estimator') == 'published_adjusted':
                            rules['DESIGN_ADJUSTED_WITHIN_FAMILY'].append(item)
                        if r.get('effect') is not None and r.get('selection_rule') == 'TARGET_FIRST_AVAILABLE':
                            rules['PUBLISHED_WITHIN_FAMILY_FALLBACK'].append(item)
                    previous=next((x for x in b.get('trials',[]) if x.get('id')==r.get('id')), {})
                    fields=('effect','ci_low','ci_high','ai','n1i','ci','n2i')
                    if r in o.get('trials',[]) and tuple(r.get(k) for k in fields)!=tuple(previous.get(k) for k in fields):
                        rules['TARGET_FIRST_SELECTION'].append(item)
                    if any(a.get('endpoint_binding_reason')=='RECURRENT_EVENTS_NOT_FIRST_EVENT_PATIENTS' for a in r.get('target_endpoint_alternatives',[])):
                        rules['RECURRENT_EVENTS_NOT_FIRST_EVENT_PATIENTS'].append(item)
                    from harness import measure_identity as mi
                    if len(mi.word_measures(mi.row_span(r)))>1 and mi.measure_of(r)!=mi.Measure.UNKNOWN and r.get('effect') is not None:
                        rules['RESULT_LOCAL_MEASURE'].append(item)
                    if (r.get('recovery_binding') or {}).get('evidence',{}).get('mode')=='COMMITTED_EXCERPT': rules['COMMITTED_EXCERPT'].append(item)
    # Recovery receipts can be nested in row recovery maps; count via their actual binding evidence.
    rules['COMMITTED_EXCERPT']=[]
    for slug,pair in ledger.items():
        for o in pair['after'].get('outcomes',[]):
            for r in o.get('trials',[])+o.get('declared_absent_trials',[]):
                if 'COMMITTED_EXCERPT' in json.dumps(r): rules['COMMITTED_EXCERPT'].append(slug+' / '+o['name']+' / '+str(r.get('id')))
    summary={'topics':len(ledger),'successful_builds':len(ledger)-len(errors),'rows_examined':rows,'rules':{k:{'n':len(v),'N':rows,'n of N':f'{len(v)} of {rows}','items':v} for k,v in rules.items()},'build_errors':errors,'missing_committed_reviews':[slug for slug,pair in ledger.items() if 'error' in pair['before']], 'changed_outcomes':changes}
    numeric=[]; outcomes=0; advisory=[]
    for slug,pair in ledger.items():
        old={o['name']:o for o in pair['before'].get('outcomes',[])}
        for o in pair['after'].get('outcomes',[]):
            outcomes+=1
            if any(p.get('code')=='MEASURE_MIX_POOLED' for p in o.get('lane_problems',[])):
                advisory.append(slug+' / '+o['name'])
            b=old.get(o['name'],{})
            fields=('k','estimate','ci_low','ci_high')
            before={k:(b.get('result') or {}).get(k) for k in fields}
            after={k:(o.get('result') or {}).get(k) for k in fields}
            if before!=after: numeric.append(dict(item=slug+' / '+o['name'],before=before,after=after))
    # These are observed retained routes, not a claim that every published row
    # had a usable count alternative. Numeric deltas retain their own census.
    preserved=[]
    for slug,pair in ledger.items():
        for o in pair['after'].get('outcomes',[]):
            for r in o.get('trials',[]):
                if (r.get('effect') is not None and r.get('measure_identity') != o.get('target_measure')
                        and r.get('selection_rule') in ('KEEP_REPORTED_EFFECT','PUBLISHED_EFFECT_TARGET_CLASS')
                        and r.get('measure_identity') in ('RISK_RATIO','HAZARD_RATIO','RATE_RATIO')
                        and o.get('target_measure') in ('RISK_RATIO','HAZARD_RATIO','RATE_RATIO')):
                    preserved.append(slug+' / '+o['name']+' / '+str(r.get('id')))
    summary['rules']['PUBLISHED_RISK_RATE_PRESERVED']={'n':len(preserved),'N':rows,'n of N':f'{len(preserved)} of {rows}','items':preserved}
    summary['rules']['SELECTED_NUMERIC_INPUT_CHANGED']=summary['rules'].pop('TARGET_FIRST_SELECTION')
    summary['rules']['MEASURE_MIX_POOLED']={'n':len(advisory),'N':outcomes,'n of N':f'{len(advisory)} of {outcomes}','items':advisory}
    summary['numeric_changes']={'n':len(numeric),'N':outcomes,'n of N':f'{len(numeric)} of {outcomes}','items':numeric}
    summary['served_changes']={'n':len(changes),'N':outcomes,'n of N':f'{len(changes)} of {outcomes}','items':changes}
    (SCRATCH/'census.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
