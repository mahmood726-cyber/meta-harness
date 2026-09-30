"""Offline all-topic served-change census; run from the clone root."""
from pathlib import Path
import json
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))

def snapshot(out):
    r = out.get('result') or {}
    from harness import measure_identity as mi
    return dict(k=r.get('k'), estimate=r.get('estimate'), ci=r.get('ci'),
                ci_low=r.get('ci_low'), ci_high=r.get('ci_high'),
                served_measure=r.get('served_measure') or (mi.normalize(r.get('scale')).value if mi.normalize(r.get('scale')) != mi.Measure.UNKNOWN else mi.outcome_identity(out, {'estimand':out.get('estimand')})['served_measure']),
                result_states=sorted({str((t.get('result_status') or {}).get('state'))
                                     for key in ('trials', 'declared_absent_trials') for t in out.get(key, [])}),
                present=r.get('present'), state=r.get('state'))

def rebuild(baseline):
    if baseline:
        from integrate2_helper import enable_baseline
        enable_baseline()
    from harness import pipeline, fetch
    results = {}
    paths = sorted((ROOT / 'topics').glob('*.json'))
    if '--slug' in sys.argv:
        paths = [p for p in paths if p.stem == sys.argv[sys.argv.index('--slug')+1]]
    for path in paths:
        cfg = json.loads(path.read_text(encoding='utf-8'))
        slug = cfg.get('slug', path.stem)
        if not (ROOT / 'cache' / slug / 'records.json').is_file():
            results[slug] = {'error': 'CACHE_NOT_HELD; no network allowed'}
            continue
        try:
            review = pipeline.build_review_core(slug, cfg, fetch.ensure(cfg, ''), 'lane')
            results[slug] = {o['name']: dict(snapshot=snapshot(o),
                                rules=sorted({p['code'] for p in o.get('lane_problems', [])} | {r['measure_selection'] for key in ('trials', 'declared_absent_trials') for r in o.get(key, []) if r.get('measure_selection')}),
                                metadata={k:(o.get('result') or {}).get(k) for k in ('target_measure','served_measure','timepoint_target','measure_disclosure','measure_mix')},
                                rows=[dict(id=t.get('id'), refusals=t.get('lane_refusals', []), measure_selection=t.get('measure_selection'),
                                           table_binding=t.get('table_binding'), recovery=t.get('recovery_map', {}).get('state'))
                                      for key in ('trials', 'declared_absent_trials') for t in o.get(key, [])])
                             for o in review['outcomes']}
        except Exception as exc:
            results[slug] = {'error': type(exc).__name__ + ': ' + str(exc)}
    print(json.dumps(results, ensure_ascii=False))

if __name__ == '__main__':
    if '--worker' in sys.argv:
        rebuild('--baseline' in sys.argv)
    else:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from integrate3_verify import environment
        worker_env = environment()
        scratch = ROOT / '.tmp' / 'integrate3'
        scratch.mkdir(parents=True, exist_ok=True)
        paths=sorted((ROOT / 'topics').glob('*.json'))
        summarize='--summarize-existing' in sys.argv
        reuse='--reuse-baseline' in sys.argv or summarize
        data=[json.loads((scratch/'baseline-snapshots.json').read_text(encoding='utf-8')) if reuse else {}, json.loads((scratch/'wired-snapshots.json').read_text(encoding='utf-8')) if summarize else {}]
        def run_one(index, slug):
            args=['--baseline'] if index == 0 else []
            try:
                raw=subprocess.check_output([sys.executable,__file__,'--worker','--slug',slug,*args],cwd=ROOT,timeout=600,env=worker_env)
                return index,json.loads(raw.decode('utf-8'))
            except (subprocess.TimeoutExpired,subprocess.CalledProcessError) as exc:
                return index,{slug:{'error':str(exc)}}
        # Independent read-only builds; full-suite tests remain strictly sequential.
        with ThreadPoolExecutor(max_workers=3) as executor:
            pending=[] if summarize else [executor.submit(run_one,i,p.stem) for p in paths for i in ((1,) if reuse else (0,1))]
            for future in as_completed(pending):
                i,result=future.result(); data[i].update(result)
                (scratch/('baseline-snapshots.json' if i==0 else 'wired-snapshots.json')).write_text(json.dumps(data[i],indent=2),encoding='utf-8')
                print('CENSUS '+('baseline ' if i==0 else 'wired ')+next(iter(result)),file=sys.stderr,flush=True)
        before,after=data
        changes=[]; metadata_changes=[]; rules={}; errors={}; total=0
        for slug, outcomes in sorted(after.items()):
            if 'error' in outcomes or 'error' in before[slug]:
                errors[slug]={'before':before[slug].get('error'), 'after':outcomes.get('error')}
                continue
            for name, item in outcomes.items():
                total += 1
                key=slug+' / '+name
                for code in item['rules']:
                    rules.setdefault(code,[]).append(key)
                bm=before[slug][name]['metadata']; am=item['metadata']
                if bm != am:
                    metadata_changes.append(dict(item=key,before=bm,after=am))
                b=before[slug][name]['snapshot']; a=item['snapshot']
                if a != b:
                    why=item['rules'] + (['RECOVERY_MAP'] if any(r['recovery'] for r in item['rows']) else [])
                    non_measure_keys=set(b)-{'served_measure'}
                    if b['served_measure'] != a['served_measure'] and all(b[k]==a[k] for k in non_measure_keys):
                        why.append('MEASURE_IDENTITY_DISCLOSED')
                    if not (set(why)-{'TARGET_TIMEPOINT_MISSING'}):
                        why.append('UNATTRIBUTED_SERVED_CHANGE')
                    changes.append(dict(item=key,before=b,after=a,rules=why,rows=item['rows']))
        from harness import lane_integration, dose_arms, verified_inputs
        declared_rules=set(lane_integration.BLOCKING) | {'TARGET_TIMEPOINT_MISSING','TIMEPOINT_MISMATCH',
            'RELAYED_COUNTS_NOT_BOUND','FULL_TABLE_NOT_HELD','TABLE_VALUE_MISMATCH','SAME_MEASURE_PUBLISHED_PREFERENCE',
            'RECOVERY_MAP','MEASURE_IDENTITY_DISCLOSED','MEASURE_MIX_POOLED'}
        for code in declared_rules:
            rules.setdefault(code, [])
        row_total=0; row_rules={'TABLE_BINDING_REFUSED':[], 'DISPERSE_ACTIVE_RECOVERY':[], 'RECOVERY_MAP':[]}
        for slug, outcomes in sorted(after.items()):
            if 'error' in outcomes: continue
            records={str(r['id']):r for r in json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf-8'))['records']}
            for name,item in outcomes.items():
                for row in item['rows']:
                    row_total+=1; item_name=slug+' / '+name+' / '+str(row['id'])
                    if (row.get('table_binding') or {}).get('state')=='REFUSED':
                        row_rules['TABLE_BINDING_REFUSED'].append(item_name)
                    if row.get('recovery'):
                        row_rules['RECOVERY_MAP'].append(item_name)
                    record=records.get(str(row['id']).replace('PMID ',''),{})
                    if dose_arms.assess(record)['recovery']=='ACTIVE':
                        row_rules['DISPERSE_ACTIVE_RECOVERY'].append(item_name)
        tables=[]; footnotes=[]
        for path in paths:
            slug=json.loads(path.read_text(encoding='utf-8')).get('slug',path.stem)
            for filename, entries in verified_inputs.load(slug).items():
                for pid, value in entries.items():
                    for row in verified_inputs.entries(value):
                        if not str(row.get('document_ref','')).split('#')[0].endswith('.tables.txt'): continue
                        key=slug+' / '+row['outcome']+' / '+str(pid)+' / '+filename
                        tables.append(key)
                        if (row.get('table_row') or {}).get('measure_basis')=='footnote': footnotes.append(key)
        row_census={k:dict(n=len(v),N=row_total,items=v) for k,v in row_rules.items()}
        row_census['TABLE_FOOTNOTE_IDENTITY']=dict(n=len(footnotes),N=len(tables),items=footnotes)
        changed_by_rule={k:[] for k in declared_rules}
        for change in changes:
            for code in change['rules']:
                if code not in ('TARGET_TIMEPOINT_MISSING', 'MEASURE_MIX_POOLED'):
                    changed_by_rule.setdefault(code, []).append(change['item'])
        summary = dict(unattributed_changes=[c['item'] for c in changes if 'UNATTRIBUTED_SERVED_CHANGE' in c['rules']], row_rule_census=row_census, served_changes_by_rule={k:dict(n=len(v),N=total,items=v) for k,v in sorted(changed_by_rule.items())}, topics=len(after), outcomes_examined=total, served_changes=dict(n=len(changes),N=total,items=changes),
                              rules={k:dict(n=len(v),N=total,items=v) for k,v in sorted(rules.items())}, metadata_changes=metadata_changes, errors=errors)

        notices=[]
        reasons={
            'TARGET_MEASURE_REWRITTEN':'the held input measures cross the immutable protocol odds-versus-risk/rate boundary',
            'TIMEPOINT_MISMATCH':'a held row has an elapsed timepoint that positively differs from the stated target',
            'SAME_MEASURE_PUBLISHED_PREFERENCE':'an endpoint-compatible held published effect matches the modal measure of the other inputs',
            'RECOVERY_MAP':'held recovery evidence supplies a typed state without admitting relayed counts',
            'POPULATION_RULE_INCONSISTENT':'the same source population is both accepted and explicitly refused within this outcome',
            'MEASURE_IDENTITY_DISCLOSED':'the served measure identity is disclosed from the actual input classes',
        }
        number_keys=('k','estimate','ci','ci_low','ci_high')
        for change in changes:
            slug,name=change['item'].split(' / ',1)
            causal=[r for r in change['rules'] if r not in ('TARGET_TIMEPOINT_MISSING','MEASURE_MIX_POOLED')]
            notices.append(dict(slug=slug,outcome=name,
                kind='NUMBER_CHANGE' if any(change['before'][k]!=change['after'][k] for k in number_keys) else 'STATE_CHANGE',
                before=change['before'],after=change['after'],rule=causal,
                reason_sentence='This outcome changes because '+'; '.join(reasons.get(r,r) for r in causal)+'.'))
        (scratch/'notices_proposed.json').write_text(json.dumps(notices,indent=2,ensure_ascii=False),encoding='utf-8')
        report=(ROOT/'lanes'/'INTEGRATE2'/'LANE_REPORT.md').read_text(encoding='utf-8')
        start=report.index('```json',report.index('### SERVED-CHANGE LEDGER'))+len('```json')
        prior=json.loads(report[start:report.index('```',start)])
        restored=[]
        numeric=('k','estimate','ci','ci_low','ci_high')
        for change in prior['served_changes']['items']:
            rules=set(change['rules'])-{'TARGET_TIMEPOINT_MISSING'}
            if rules != {'MEASURE_MIX_POOLED'}: continue
            slug,name=change['item'].split(' / ',1)
            b=before[slug][name]['snapshot']; a=after[slug][name]['snapshot']
            restored.append(dict(item=change['item'], baseline=b, integrate2=change['after'], integrate3=a,
                numbers_unchanged=all(b[k]==a[k] for k in numeric)))
        summary['integrate2_mix_only_restored']=dict(n=sum(r['numbers_unchanged'] for r in restored),N=len(restored),items=restored)
        summary['advisory_only_numeric_changes']=[c['item'] for c in changes
            if not (set(c['rules'])-{'TARGET_TIMEPOINT_MISSING','MEASURE_MIX_POOLED','MEASURE_IDENTITY_DISCLOSED'})
            and any(c['before'][k]!=c['after'][k] for k in numeric)]
        print(json.dumps(summary,indent=2,ensure_ascii=False))

        if any('UNATTRIBUTED_SERVED_CHANGE' in c['rules'] for c in changes):
            raise SystemExit(1)
