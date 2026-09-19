"""Second-pass identifier, date and source-span audit of the generated artifacts."""
from pathlib import Path
import json
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from harness import trial_family
from harness.family_compact import read_registry, read_families
ROOT = Path(__file__).resolve().parents[1]

def load(path):
    if path.name == 'families.json':
        return read_families(path)
    if path.name == 'family_registry.json':
        return read_registry(path)
    return json.loads(path.read_text(encoding='utf8'))

def main():
    sweep = load(ROOT/'docs/trial_family_sweep.json')
    assert not sweep['failures']
    checks = 0
    ambiguous = []
    secondary_nct_aliases = []
    for slug, measurement in sweep['topics'].items():
        artifact = load(ROOT/'cache'/slug/'families.json')
        registry = load(ROOT/'cache'/slug/'family_registry.json')['records']
        assert sum(f['is_trial_family'] for f in artifact['families']) == measurement['after']['trial_families']
        assert artifact['count_chain'] == measurement['after']
        assert len({f['family_id'] for f in artifact['families']}) == len(artifact['families'])
        for f in artifact['families']:
            for report in f['reports']:
                assert not report['report_id'].startswith('fixture')
                record = next(r for r in f['source_records'] if r['id']==report['report_id'])
                basis = report['span_basis']
                if basis.get('source') in {'record.title','record.pubtypes','record.abstract'}:
                    value = record[basis['source'].split('.')[1]]
                    assert basis['quote']==(' '.join(value) if isinstance(value,list) else value)
                    checks += 1
            for stage, value in f['lifecycle'].items():
                if value.get('value') is None:
                    assert value.get('absence_code')
                    continue
                if stage=='publication_found':
                    source = next(r for r in f['source_records'] if r['id']==value['span']['report_id'])
                    assert value['value']==source['year']
                else:
                    source = registry[f['family_id']]['raw']['studies'][0]
                    assert value['value']==source[value['span']['source'].split('.')[-1]]
                checks += 1
            for status in f['outcome_status']:
                for key in ('prospectively_specified','measured','reported','extractable','in_primary_pool'):
                    assert status[key].get('span') or status[key].get('absence_code')
                    evidence = status[key].get('span')
                    if isinstance(evidence,dict) and evidence.get('source')=='AACT registry results':
                        raw = registry[f['family_id']]['raw']
                        assert evidence['outcome_row'] in raw['outcomes']
                        for value in evidence['typed_values']:
                            row = value['source_row']
                            table = 'outcome_measurement_samples' if value['source_table']=='outcome_measurements' else 'outcome_analyses'
                            assert row in raw[table]
                            assert row['nct_id']==f['family_id']
                            assert row['outcome_id']==evidence['outcome_row']['id']
                            assert value['value']==float(row.get('param_value_num') or row['param_value'])
                            checks += 1
                for candidate in status['registered_outcome_candidates']:
                    assert candidate['row'] in registry[f['family_id']]['design_outcomes']
                    checks += 1
            ncts = {n for r in f['source_records'] for n in r.get('registry_ids',[]) if n.upper().startswith('NCT')}
            assert len(ncts)<=1, 'Distinct NCT parents were merged: '+f['family_id']
            extra = {n for n in f['aliases']['registry_ids'] if n.upper().startswith('NCT')}-ncts
            for n in extra:
                evidence = [r for r in registry[f['family_id']]['raw']['id_information'] if r['id_value']==n]
                assert evidence, 'Secondary registry alias lacks held id_information evidence'
                secondary_nct_aliases.append({'family_id':f['family_id'],'secondary_id':n,'source_rows':evidence})
                checks += 1
            if 'MULTIPLE_REGISTRY_PARENTS' in f['flags']:
                ambiguous.append({'slug':slug,'family_id':f['family_id'],'mentioned_ids':f['aliases']['mentioned_registry_ids']})
    glp = load(ROOT/'cache/glp1-ra-mace-t2d/families.json')
    wanted = ['SUSTAIN 1','PIONEER 1','AWARD-8','LEAD-2','Harmony 1','AMPLITUDE-M',
              'GetGoal-P','GetGoal-L','GetGoal-Mono','FREEDOM-1']
    normalize = lambda x: re.sub(r'[^a-z0-9]','',x.lower())
    named = []
    for name in wanted:
        hits = [f['family_id'] for f in glp['families'] if any(normalize(a)==normalize(name) for a in f['aliases']['acronym'])]
        named.append({'protocol_name':name,'family_ids':hits,
                      'state':'HELD_ACRONYM_MATCH' if hits else 'NAME_TO_REGISTRY_LINK_UNRESOLVED'})
    out = {'classification':'MEASURED','checks':checks,'coverage':sweep['coverage'],
           'assertions_passed':True,'ambiguous_parent_reports':ambiguous,'review_a_name_linkage':named,
           'source_declared_secondary_nct_ids':secondary_nct_aliases}
    (ROOT/'docs/trial_family_evidence_audit.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps({'checks':checks,'coverage':sweep['coverage'],'ambiguous_parent_reports':len(ambiguous),
                      'review_a_names_linked':sum(bool(r['family_ids']) for r in named),'review_a_names_requested':len(named)}))

if __name__=='__main__': main()
