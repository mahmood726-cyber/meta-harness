"""Measured family sweep on the exact held r3 32-topic cohort. No network or pooling edits."""
from pathlib import Path
import copy
import json
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from harness import trial_family, pipeline, page, identity
from harness.family_compact import write_families, read_families
ROOT = Path(__file__).resolve().parents[1]

def load(p):
    if p.name == 'families.json':
        return read_families(p)
    return json.loads(p.read_text(encoding='utf8'))

def write(p, data):
    if p.name == 'families.json':
        return write_families(p, data)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf8')

def pool_signature(review):
    keys = ('id','effect','ci_low','ci_high','scale','ai','ci','n1i','n2i','mean1','sd1','nc1','mean2','sd2','nc2','e1i','t1i','e2i','t2i')
    def numbers(value):
        if isinstance(value,dict):
            return {k:numbers(v) for k,v in value.items() if k not in
                    {'claim','input_set_version','claim_id','depends_on','claim_kind','family_id','family_identity_state'}}
        if isinstance(value,list):
            return [numbers(v) for v in value]
        return value
    return [{'name':o['name'],'trials':[{k:t[k] for k in keys if k in t} for t in o.get('trials',[])],
             'result':numbers(o.get('result'))} for o in review.get('outcomes',[])]

def clarify_denominators(summary):
    for slug, measurement in summary['topics'].items():
        records = load(ROOT/'cache'/slug/'records.json')
        cfg = load(ROOT/'topics'/f'{slug}.json')
        screened = pipeline._dedup(records,cfg.get('pivotal_trials'))
        measurement['before']['records_screened'] = len(screened)
        measurement['before']['publications_screened'] = sum(r.get('id_type')!='nct' for r in screened)
        measurement['before']['registry_records_screened'] = sum(r.get('id_type')=='nct' for r in screened)
        for name in ('reports_counted_as_trials','extensions_counted_as_comparisons'):
            measurement[name]['denominator'] = 'base screened-in report/registry rows'
    return summary

def main():
    cohort = sorted(load(ROOT/'outputs/search_v2/candidates-2026-09-15r3-all.json')['candidates'])
    full_cohort = list(cohort)
    prior = None
    if '--topics' in sys.argv:
        selected = set(sys.argv[sys.argv.index('--topics')+1].split(','))
        if not selected <= set(cohort):
            raise ValueError('Requested topic outside the held cohort')
        prior = load(ROOT/'docs/trial_family_sweep.json')
        if set(prior['topics']) | {f['slug'] for f in prior['failures']} != set(cohort):
            raise ValueError('Targeted rerun requires a complete attempted sweep')
        cohort = sorted(selected)
    summary = {'classification':'MEASURED','cohort_source':'outputs/search_v2/candidates-2026-09-15r3-all.json:candidates',
               'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
               'topics':{}, 'failures':[]}
    if '--refresh-annotations' in sys.argv:
        summary = load(ROOT/'docs/trial_family_sweep.json')
        if summary['failures'] or set(summary['topics']) != set(cohort):
            raise ValueError('Annotation refresh requires a complete green pool-invariance sweep')
        for slug in cohort:
            cfg = load(ROOT/'topics'/f'{slug}.json')
            recs = load(ROOT/'cache'/slug/'records.json')
            artifact = load(ROOT/'cache'/slug/'families.json')
            old = {f['family_id']:f for f in artifact['families']}
            ledger_path = ROOT/'cache'/slug/'retrieval_ledger.json'
            nodes = trial_family.prepare(ROOT,slug,list(recs['records'])+list(recs.get('ctgov') or []),cfg,
                                         load(ledger_path) if ledger_path.exists() else None)
            if {f['family_id'] for f in nodes} != set(old):
                raise ValueError('Family membership changed; full sweep required: '+slug)
            for f in nodes:
                statuses = {s['outcome']:s for s in old[f['family_id']]['outcome_status']}
                for s in f['outcome_status']:
                    for key in ('measured','reported','extractable','in_primary_pool'):
                        s[key] = statuses[s['outcome']][key]
            artifact['families'] = nodes
            chain = artifact['count_chain']
            chain['eligible_families'] = sum(f['eligibility']['state']=='ELIGIBLE' for f in nodes)
            chain['eligibility_unresolved'] = sum(f['eligibility']['state']=='UNKNOWN' for f in nodes)
            if slug == 'glp1-ra-mace-t2d':
                previous = load(ROOT/'.tmp/fn-glp1-review.json')
                current = pipeline.build_review_core(slug,copy.deepcopy(cfg),recs,'lane-fn-local-verification')
                if pool_signature(previous) != pool_signature(current):
                    raise ValueError('GLP-1 refresh changed numeric pool or membership')
                artifact = {'schema_version':1,'count_chain':current['family_count_chain'],'families':current['trial_families']}
                write(ROOT/'.tmp/fn-glp1-review.json',current)
                (ROOT/'.tmp/fn-glp1.html').write_text(page.render_page(current),encoding='utf8')
            write(ROOT/'cache'/slug/'families.json',artifact)
            summary['topics'][slug]['after'] = artifact['count_chain']
        summary['annotation_refresh'] = 'Same family membership; final protocol requirements and registered-outcome evidence applied. GLP-1 pipeline rebuilt and pool signature rechecked.'
        write(ROOT/'docs/trial_family_sweep.json',clarify_denominators(summary))
        return 0
    # Cache repeated identical local reads between baseline and new pipeline.
    # Values remain produced by the unchanged AACT adapter, never fixtures.
    from harness import aact
    from functools import lru_cache
    # Read each large local table once, retaining the complete NCT inventory
    # needed by BOTH pipelines. Refuse any out-of-inventory request below.
    wanted = set()
    for slug in cohort:
        doc = load(ROOT/'cache'/slug/'records.json')
        # The newer base augments GLP-1 from held source documents before pooling.
        # Include those source-backed IDs and the compact discovery universe.
        wanted.update(trial_family.load_registry(ROOT, slug))
        for rec in list(doc['records'])+list(doc.get('ctgov') or []):
            wanted.update(n.upper() for n in trial_family.registry_ids(rec) if n.upper().startswith('NCT'))
    iter_rows = aact._iter_rows
    scoped_tables = {}
    for name in ('studies','sponsors','responsible_parties'):
        path = aact._table(name)
        if path:
            scoped_tables[str(Path(path).resolve())] = [r for r in iter_rows(path) if r.get('nct_id','').upper() in wanted]
    def scoped_rows(path):
        key = str(Path(path).resolve())
        yield from scoped_tables[key] if key in scoped_tables else iter_rows(path)
    aact._iter_rows = scoped_rows
    for name in ('study_dates','sponsor_records'):
        original_reader = getattr(aact,name)
        cached = lru_cache(maxsize=None)(original_reader)
        def reader(ncts, root=None, _cached=cached):
            if not {str(n).upper() for n in ncts} <= wanted:
                raise ValueError('AACT request outside measured corpus inventory')
            return copy.deepcopy(_cached(tuple(sorted(set(ncts))),root))
        setattr(aact,name,reader)
    # Run the original pipeline on the same held inputs, not stale rendered pages.
    original = subprocess.check_output(['git','show','HEAD:harness/pipeline.py'],text=True,encoding='utf8')
    namespace = {'__name__':'harness._family_baseline','__package__':'harness','__file__':str(ROOT/'harness/pipeline.py')}
    exec(compile(original,'<landing-3 pipeline>','exec'),namespace)
    for slug in cohort:
        try:
            cfg, records = load(ROOT/'topics'/f'{slug}.json'), load(ROOT/'cache'/slug/'records.json')
            before = namespace['build_review_core'](slug,copy.deepcopy(cfg),copy.deepcopy(records),'lane-fn-local-verification')
            after = pipeline.build_review_core(slug,copy.deepcopy(cfg),copy.deepcopy(records),'lane-fn-local-verification')
            if pool_signature(before) != pool_signature(after):
                raise AssertionError('Pooling membership or numeric result changed')
            nodes = after['trial_families']
            write(ROOT/'cache'/slug/'families.json', {'schema_version':1,'count_chain':after['family_count_chain'],'families':nodes})
            before_recs = before.get('screening',{}).get('records',[])
            before_in = [r for r in before_recs if r.get('decision')=='include']
            primary = next((o for o in after['outcomes'] if o.get('primary')), {})
            pooled = primary.get('trials',[])
            by_id = {f['family_id']:f for f in nodes}
            included_ids = {identity._norm(r['id']) for r in before_in}
            collapse = [r for f in nodes for r in f['reports'] if r['report_id'] in included_ids and
                        r['role'] in {'SECONDARY_ANALYSIS','SUBGROUP','COST_EFFECTIVENESS','EXTENSION','PROTOCOL','SAP','CORRECTION','RETRACTION'}]
            extensions = [r for r in collapse if r['role']=='EXTENSION' and r.get('randomised_contrast_preserved') is False]
            summary['topics'][slug] = {
                'before':{'publications_screened':len(before_recs),'families':len({r.get('trial_family_id') or r['id'] for r in before_recs}),
                          'eligible_families':identity.included_counts(before)['trials']},
                'after':after['family_count_chain'],
                'reports_counted_as_trials':{'n':len(collapse),'N':len(before_in),'denominator':'base screened-in publication rows','reports':collapse},
                'extensions_counted_as_comparisons':{'n':len(extensions),'N':len(before_in),'denominator':'base screened-in publication rows'},
                'no_registry_record':{'n':sum('NO_REGISTRY_RECORD' in f['flags'] for f in nodes),'N':len(nodes),'denominator':'family nodes'},
                'structural_contrast_proven':{'before_n':sum(bool(t.get('family_id') and t.get('randomised_contrasts')) for t in
                    next((o for o in before['outcomes'] if o.get('primary')),{}).get('trials',[])),
                    'n':sum(bool(by_id.get(t.get('family_id'),{}).get('randomised_contrasts')) for t in pooled),
                    'N':len(pooled),'denominator':'unchanged primary pooled rows'},
                'pool_membership_and_results_unchanged':True}
            if slug=='glp1-ra-mace-t2d':
                write(ROOT/'.tmp/fn-glp1-review.json',after)
                (ROOT/'.tmp/fn-glp1.html').write_text(page.render_page(after),encoding='utf8')
            print(slug,after['family_count_chain'],flush=True)
        except Exception as exc:
            summary['failures'].append({'slug':slug,'error':str(exc)})
            print('FAIL',slug,str(exc)[:300],flush=True)
    if prior is not None:
        prior['topics'].update(summary['topics'])
        prior['failures'] = [f for f in prior['failures'] if f['slug'] not in selected] + summary['failures']
        prior['targeted_recheck'] = cohort
        summary = prior
    summary['coverage'] = {'n':len(summary['topics']),'N':len(full_cohort),'denominator':'held r3 topic cohort'}
    write(ROOT/'docs/trial_family_sweep.json',clarify_denominators(summary))
    if summary['failures']:
        write(ROOT/'STUCK_FAILURES.fn.json',summary['failures'])
        return 1
    return 0

if __name__=='__main__': raise SystemExit(main())
