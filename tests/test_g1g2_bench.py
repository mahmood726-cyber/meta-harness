"""Held-source plants: numeric inputs derived from bytes, mutations are adversarial."""
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import g1_tracker as gt
from harness.hcq_primary_table import read


@pytest.mark.parametrize('slug', ['daratumumab-rrmm-pfs-bench','hcq-covid-prophylaxis-bench'])
def test_g1_bench_enumerated(slug):
    data = json.loads((ROOT/'registry/secondary_meta'/f'{slug}.json').read_text(encoding='utf8'))
    assert data['rows']
    table = json.loads((ROOT/'outputs/k_gap/k_gap_table.json').read_text(encoding='utf8'))
    assert any(t['slug'] == slug for t in table['trials'])


def test_g1_hcq_arm_sum_and_negative():
    text = (ROOT/'cache/hcq-covid-prophylaxis-bench/PMC7665393.xml').read_text(encoding='utf8')
    row = read(text)
    ours = dict(zip(('events_t','n_t','events_c','n_c'), (row[k] for k in ('ai','n1i','ci','n2i'))))
    secondary = json.loads((ROOT/'registry/secondary_meta/hcq-covid-prophylaxis-bench.json').read_text(encoding='utf8'))
    theirs = next(r for r in secondary['rows'] if r['family_id'] == 'PMID '+row['report_id'])
    side = gt.disagreement_side(ours, theirs, text)
    assert side and side.startswith('COMPARATOR_ROW_NOT_IN_TRIAL_REPORT')
    assert gt.disagreement_side(dict(ours, events_t=ours['events_t']+1), theirs, text) is None
    assert gt.disagreement_side(ours, theirs, '') is None


def test_g1g2_recorded_retrieval_consumer():
    from harness import hazard_consumers as hc
    obj = {'kind':'RETRIEVAL_CLASS','evidence_state':'RECORDED'}
    core = {'search':{'retrieval_class':{'retrieval_auditable':True}}, 'outcomes':[]}
    before = hc.consumer_for(core, obj)
    assert before is not None
    core['search']['retrieval_class']['retrieval_auditable'] = False
    after = hc.consumer_for(core, obj)
    assert before['gate_verdict_at_build'] != after['gate_verdict_at_build']


def test_g1g2_harms_held_cells_and_debt():
    from harness import hand_binding, verified_inputs
    slug = 'hcq-covid-prophylaxis-bench'
    cfg = json.loads((ROOT/'topics'/f'{slug}.json').read_text(encoding='utf8'))
    data = verified_inputs.load(slug)['verified_arms.json']
    extracted = [dict(r,id=pid) for pid,value in data.items() for r in verified_inputs.entries(value)
                 if r.get('kind') == 'extracted_counts']
    assert {r['outcome'] for r in extracted} >= {s['name'] for s in cfg['harm_outcomes']}
    for row in extracted:
        spec = next(s for s in cfg['harm_outcomes'] if s['name']==row['outcome'])
        assert hand_binding.bind_hand_row(spec,row)['hand_binding_state']=='BOUND'
        changed = dict(row,ai=row['ai']+1)
        assert hand_binding.bind_hand_row(spec,changed)['hand_binding_state']=='ABSTAIN'
    for slug in ['daratumumab-rrmm-pfs-bench',slug]:
        debt=json.loads((ROOT/'registry/benchmarks'/f'{slug}_harms_debt.json').read_text(encoding='utf8'))
        assert debt['entries'] and all(e['source_span'] and e['document_sha256'] for e in debt['entries'])


def test_g1g2_hcq_attributed_table_rows():
    from harness import hand_binding
    import xml.etree.ElementTree as ET
    text=(ROOT/'cache/hcq-covid-prophylaxis-bench/PMC7722693.xml').read_text(encoding='utf8')
    doc=ET.fromstring(text)
    table=next(t for t in doc.iter('table-wrap') if t.get('id')=='t3')
    labels={''.join(r[0].itertext()) for r in table.find('.//tbody').iter('tr') if len(r)>1 and ''.join(r[1].itertext())}
    parsed={r['label'] for r in hand_binding.table_rows(text)}
    compact=lambda values: {''.join(v.split()) for v in values}
    assert compact(labels) <= compact(parsed)


def test_g1g2_typed_primary_route_preserves_harms():
    from harness import pipeline,verified_inputs
    slug='hcq-covid-prophylaxis-bench'
    cfg=json.loads((ROOT/'topics'/f'{slug}.json').read_text(encoding='utf8'))
    records=json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf8'))
    held=verified_inputs.load(slug)['verified_arms.json']
    actual=pipeline.outcome_inputs(slug,cfg,records)['varms']
    for spec in cfg['harm_outcomes']:
        assert verified_inputs.for_outcome(actual,spec['name']) == verified_inputs.for_outcome(held,spec['name'])


def test_g1_dara_primary_effect_difference_is_source_named():
    from harness import extract
    slug='daratumumab-rrmm-pfs-bench'
    secondary=json.loads((ROOT/'registry/secondary_meta'/f'{slug}.json').read_text(encoding='utf8'))
    records=json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf8'))['records']
    review=json.loads((ROOT/'docs/reviews'/slug/'review.json').read_text(encoding='utf8'))
    primary=next(o for o in review['outcomes'] if o.get('primary'))
    checked=[]
    for comparator in secondary['rows']:
        trial=next(t for t in primary['trials'] if t['id']==comparator['family_id'])
        ours=gt.our_value_from_row(trial)
        if gt.agreement(ours,gt._row(comparator))!='DISAGREE': continue
        rec=next(r for r in records if 'PMID '+str(r['id'])==trial['id'])
        side=gt.disagreement_side(ours,comparator,rec['abstract'])
        assert side and side.startswith('DIFFERENT_REPORTED_TUPLE')
        assert gt.disagreement_side(ours,comparator,'') is None
        bad=dict(ours,effect=str(float(ours['effect'])+1))
        assert gt.disagreement_side(bad,comparator,rec['abstract']) is None
        checked.append(trial['id'])
    assert checked
