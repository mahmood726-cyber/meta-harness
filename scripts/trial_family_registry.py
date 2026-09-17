"""Offline AACT ingredient extraction and GLP-1 concept query; no search-code changes."""
from pathlib import Path
import json
import sys
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import aact
from harness.trial_family import field, registry_ids
from harness.family_compact import compact_registry, write_registry

ROOT = Path(__file__).resolve().parents[1]

def write(path, obj):
    if path.name == 'family_registry.json':
        return write_registry(path, compact_registry(obj))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n', encoding='utf8')

def rows(name, required):
    path = aact._table(name)
    if not path:
        raise ValueError('AACT table unavailable: '+name)
    with open(path, encoding='utf8') as f:
        header = f.readline().strip().split('|')
    if not set(required) <= set(header):
        raise ValueError('AACT columns missing in '+name+': '+str(set(required)-set(header)))
    yield from aact._iter_rows(path)

def span(table, row):
    return {'source':'AACT.'+table, 'row':row}

def main():
    snapshot = aact.snapshot_dir()
    if not snapshot:
        raise ValueError('No local AACT snapshot')
    cfg = json.loads((ROOT/'topics/glp1-ra-mace-t2d.json').read_text(encoding='utf8'))
    agents = cfg['include']['intervention_any']
    query = {'conditions.name_contains_any':cfg['include']['population_any'],
             'interventions.name_contains_any':agents, 'interventions.intervention_type':'drug',
             'designs.allocation':'RANDOMIZED', 'interventions.placebo_name_contains':'placebo'}
    source = {'source_id':'aact_family_concept#1', 'kind':'AACT_CONCEPT_QUERY',
              'query':json.dumps(query,sort_keys=True), 'run_utc':datetime.now(timezone.utc).isoformat(),
              'snapshot':Path(snapshot).name, 'state':'NOT_RUN', 'discovery_capable':True,
              'four_states':['NOT_RUN','RAN_OK','RAN_ZERO','RAN_ERROR']}
    try:
        conditions = {}
        for r in rows('conditions', ['nct_id','name']):
            if any(t.lower() in r['name'].lower() for t in query['conditions.name_contains_any']):
                conditions.setdefault(r['nct_id'],[]).append(r)
        print('condition matches',len(conditions),flush=True)
        interventions = {}
        for r in rows('interventions', ['id','nct_id','intervention_type','name','description']):
            if r['nct_id'] in conditions:
                interventions.setdefault(r['nct_id'],[]).append(r)
        agent_ncts = {n for n, rs in interventions.items() if any(r['intervention_type'].lower() == 'drug' and
                     any(a.lower() in r['name'].lower() for a in agents) for r in rs)}
        placebo = {n for n in agent_ncts if any('placebo' in r['name'].lower() for r in interventions[n])}
        designs = {r['nct_id']:r for r in rows('designs',['nct_id','allocation']) if r['nct_id'] in agent_ncts}
        selected = {n for n in placebo if designs.get(n,{}).get('allocation','').upper() == 'RANDOMIZED'}
        decisions = [{'id':n,'decision':'retain' if n in selected else 'refuse',
                      'reason_code':'PICD_MATCH' if n in selected else 'NO_PLACEBO' if n not in placebo else 'RANDOMIZATION_NOT_ESTABLISHED',
                      'span':{'conditions':conditions[n],'interventions':interventions[n],'design':designs.get(n)}} for n in sorted(agent_ncts)]
        source.update(state='RAN_OK' if selected else 'RAN_ZERO', error=None,
                      funnel={'condition_hits':len(conditions),'agent_hits':len(agent_ncts),'placebo_hits':len(placebo),
                              'hits':len(selected),'fetched':len(selected),'retained':len(selected),
                              'cap':{'kind':'none','n':None,'remainder':None}},
                      record_ids=sorted(selected), decisions=decisions)
        print('concept selected',len(selected),flush=True)
        caches = {p.parent.name:json.loads(p.read_text(encoding='utf8')) for p in (ROOT/'cache').glob('*/records.json')}
        r3 = json.loads((ROOT/'outputs/search_v2/candidates-2026-09-15r3-all.json').read_text(encoding='utf8'))['candidates']
        caches = {slug:d for slug,d in caches.items() if slug in r3}
        # Every current GLP-1 report plus all r3 reports; no invented identifier maps.
        # Lane-requested held r3 reports, not the 12k raw search-hit universe.
        requested = {'38785209','34873344','26630143','37952131','40162642','34526024'}
        extras = [r for r in r3['glp1-ra-mace-t2d'] if str(r['id']) in requested]
        if {str(r['id']) for r in extras} != requested:
            raise ValueError('Required r3 reports absent from held candidate source')
        pmids = {str(r['id']) for d in caches.values() for r in d['records'] if str(r['id']).isdigit()}
        pmids.update(str(r['id']) for r in extras if str(r['id']).isdigit())
        refs = {}
        for r in rows('study_references',['nct_id','pmid','reference_type']):
            if r.get('pmid') in pmids and r['reference_type'].upper() in aact.OWN_PUB_TYPES:
                refs.setdefault(r['pmid'],[]).append(r)
        want = set(selected)
        want.update(n for d in caches.values() for r in list(d['records'])+list(d.get('ctgov') or [])
                    for n in registry_ids(r) if n.upper().startswith('NCT'))
        want.update(r['nct_id'] for rs in refs.values() for r in rs)
        data = {n:{} for n in sorted(want)}
        for name, columns in [
            ('studies',['nct_id','start_date','completion_date','study_first_posted_date','results_first_posted_date']),
            ('designs',['nct_id','allocation']), ('design_groups',['id','nct_id','title','description']),
            ('interventions',['id','nct_id','name','description']),
            ('design_group_interventions',['nct_id','design_group_id','intervention_id']),
            ('eligibilities',['nct_id','minimum_age','maximum_age','gender','criteria']),
            ('conditions',['nct_id','name']), ('design_outcomes',['nct_id','outcome_type','measure']),
            ('outcomes',['id','nct_id','title','param_type']),
            ('outcome_analyses',['nct_id','outcome_id','param_type','param_value','ci_lower_limit','ci_upper_limit']),
            ('id_information',['nct_id','id_value']), ('milestones',['nct_id','result_group_id','count','title'])]:
            for r in rows(name,columns):
                if r['nct_id'] in want:
                    data[r['nct_id']].setdefault(name,[]).append(r)
            print('extracted',name,flush=True)
        # One numeric source row per outcome is enough to establish that it was
        # measured/reported. It is NOT an arm contrast or a new pooling input.
        measured = set()
        for r in rows('outcome_measurements',['nct_id','outcome_id','param_value_num']):
            key = (r['nct_id'],r['outcome_id'])
            if r['nct_id'] in want and key not in measured and r.get('param_value_num'):
                data[r['nct_id']].setdefault('outcome_measurement_samples',[]).append(r)
                measured.add(key)
        print('extracted outcome measurement evidence',len(measured),flush=True)
        registry = {}
        for n, tables in data.items():
            if not tables.get('studies'):
                continue
            study = tables['studies'][0]
            iv = {r['id']:r for r in tables.get('interventions',[])}
            arms = []
            for g in tables.get('design_groups',[]):
                links = [r for r in tables.get('design_group_interventions',[]) if r['design_group_id']==g['id']]
                linked = [iv[r['intervention_id']] for r in links if r['intervention_id'] in iv]
                active = sorted({r['name'].lower().strip() for r in linked if 'placebo' not in r['name'].lower() and 'sham' not in r['name'].lower()})
                arms.append({'arm_id':n+':'+g['id'],'label':field(g['title'],span('design_groups',g)),
                             'drug':field([r['name'] for r in linked],{'source':'AACT.interventions','rows':linked}),
                             'dose':field(code='NOT_SEPARATELY_CODED'),'schedule':field(code='NOT_SEPARATELY_CODED'),
                             'route':field(code='NOT_SEPARATELY_CODED'),'background_therapy':[],
                             'n_randomised':field(code='NO_DESIGN_GROUP_TO_RESULT_GROUP_LINK'),
                             'active_interventions':active,'linkage_complete':bool(links) and len(linked)==len(links),
                             'span':{'design_group':span('design_groups',g),'links':links,'interventions':linked}})
            common = set.intersection(*(set(a['active_interventions']) for a in arms)) if arms else set()
            for a in arms:
                a['background_therapy'] = sorted(common)
            el = (tables.get('eligibilities') or [{}])[0]
            pop = {k:field(el.get(v),span('eligibilities',el)) for k,v in
                   [('age_min','minimum_age'),('age_max','maximum_age'),('sex','gender'),('criteria','criteria'),('entry_population','population')]}
            pop['conditions'] = field([r['name'] for r in tables.get('conditions',[])],{'source':'AACT.conditions','rows':tables.get('conditions',[])})
            life = {k:field(study.get(col),{'source':'AACT.studies.'+col,'nct_id':n,'quote':study.get(col)}) for k,col in
                    [('registered','study_first_posted_date'),('started','start_date'),('completed','completion_date'),('results_posted','results_first_posted_date')]}
            design = (tables.get('designs') or [{}])[0]
            registry[n] = {'arms':arms,'population':pop,'lifecycle':life,
                           'randomized':design.get('allocation','').upper()=='RANDOMIZED',
                           'design':design,'design_outcomes':tables.get('design_outcomes',[]),
                           'registry_results':[{'outcome':o,
                               'analyses':[a for a in tables.get('outcome_analyses',[]) if a['outcome_id']==o['id']],
                               'measurement_samples':[m for m in tables.get('outcome_measurement_samples',[]) if m['outcome_id']==o['id']]}
                               for o in tables.get('outcomes',[])],
                           'raw':tables,'snapshot':Path(snapshot).name}
        for slug, d in caches.items():
            recs = list(d['records']) + list(d.get('ctgov') or []) + (extras if slug=='glp1-ra-mace-t2d' else [])
            ns = {n for r in recs for n in registry_ids(r)}
            ns.update(rr['nct_id'] for r in recs for rr in refs.get(str(r['id']),[]))
            if slug=='glp1-ra-mace-t2d': ns.update(selected)
            write(ROOT/'cache'/slug/'family_registry.json', {'snapshot':Path(snapshot).name,
                  'records':{n:registry[n] for n in sorted(ns) if n in registry},
                  'report_links':{str(r['id']):refs[str(r['id'])] for r in recs if str(r['id']) in refs}})
        discovery = []
        for n in sorted(selected):
            t = data[n]; study = t['studies'][0]; design = (t.get('designs') or [{}])[0]
            discovery.append({'id':n,'id_type':'nct','nct':n,'title':study['brief_title'],
                              'acronym':study.get('acronym'),'conditions':[r['name'] for r in t.get('conditions',[])],
                              'interventions':[r['name'] for r in t.get('interventions',[])],
                              'allocation':design.get('allocation'), 'masking':design.get('masking'),
                              'found_by':[source['source_id']]})
        write(ROOT/'cache/glp1-ra-mace-t2d/family_discovery.json', {'source':source,'records':discovery,'r3_records':extras})
        print('registry families',len(registry),flush=True)
    except (ValueError, OSError) as exc:
        source.update(state='RAN_ERROR',error=str(exc),funnel={'hits':None,'fetched':0,'retained':0})
        raise
    finally:
        write(ROOT/'cache/glp1-ra-mace-t2d/family_query.json',source)

if __name__ == '__main__': main()
