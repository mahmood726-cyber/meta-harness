"""Family integration plants using the real held topic."""
import copy
import json
from pathlib import Path
from harness import pipeline, trial_family
ROOT=Path(__file__).resolve().parents[1]
SLUG='daratumumab-rrmm-pfs-bench'
CONFIG=json.loads((ROOT/'topics'/(SLUG+'.json')).read_text(encoding='utf8'))
RECORDS=json.loads((ROOT/'cache'/SLUG/'records.json').read_text(encoding='utf8'))
def test_prefixless_registration():
    r=next(r for r in RECORDS['records'] if r['id']=='30237264')
    assert trial_family.registry_ids(r)==['NCT02136134']
def test_latest_whole_population_and_members():
    config=copy.deepcopy(CONFIG)
    config.pop('report_selection', None)  # legacy latest-cut policy remains covered without opt-in
    inp=pipeline.outcome_inputs(SLUG,config,copy.deepcopy(RECORDS))
    ids={d['id'] for d in inp['included']}
    assert '37163358' in ids
    assert not ids.intersection({'32682484','34871550'})
    assert any(c['pmid']=='32682484' and c['parent_pmid']=='37163358' for c in inp['config'].get('companion_reports',[]))
def test_curated_unchanged():
    config=copy.deepcopy(CONFIG)
    config.pop('report_selection', None)
    config['companion_reports']=[{'pmid':'34871550','parent_pmid':'32682484','reason':'curated control'}]
    inp=pipeline.outcome_inputs(SLUG,config,copy.deepcopy(RECORDS))
    assert [r['id'] for r in inp['merged'] if r.get('id_type')=='pmid']==[r['id'] for r in pipeline._dedup(RECORDS) if r.get('id_type')=='pmid']

def test_selection_is_order_independent_and_does_not_take_os_only_update():
    a=trial_family.automatic_companions(copy.deepcopy(RECORDS['records']),CONFIG)
    b=trial_family.automatic_companions(list(reversed(copy.deepcopy(RECORDS['records']))),CONFIG)
    links=lambda rows: sorted((r['pmid'],r['parent_pmid']) for r in rows)
    assert links(a)==links(b)
    assert any(r['pmid']=='37793772' and r['parent_pmid']=='34087126' for r in a)
def test_same_cut_tie_uses_earliest_pmid():
    rec=copy.deepcopy(next(r for r in RECORDS['records'] if r['id']=='32682484'))
    later=dict(rec,id='34871550') # identity-only plant; same held abstract/cut
    links=trial_family.automatic_companions([later,rec],CONFIG)
    assert [(r['pmid'],r['parent_pmid']) for r in links]==[('34871550','32682484')]
def test_no_registry_is_not_inferred_from_trial_name():
    for pid in ['32482541','32001798','29712896']:
        rec=next(r for r in RECORDS['records'] if r['id']==pid)
        assert trial_family.registry_ids(rec)==[]

def test_indirect_comparison_is_not_the_randomized_family_estimate():
    rows=trial_family.automatic_companions(copy.deepcopy(RECORDS['records']),CONFIG)
    assert not any(r['parent_pmid']=='40768190' for r in rows)
