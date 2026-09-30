"""FIX1 plants: synthetic defects and held-source requirement checks."""
from copy import deepcopy
from pathlib import Path
import json
import pytest
from harness import lane_integration as lane, measure_identity as mi, recovery_excerpt as rx, extract, page
ROOT=Path(__file__).resolve().parents[1]

def row(**kw):
    return dict(dict(id='synthetic',label='synthetic',effect=.8,ci_low=.6,ci_high=.95,scale='RR',source='risk ratio 0.8 at 28 days'),**kw)

def prepare(rows,target='RR',time='28 days'):
    o=dict(name='Mortality',trials=rows,declared_absent_trials=[])
    spec=dict(name=o['name'],estimand=target,timepoint=time)
    lane.prepare(o,spec,{},{});lane.finish(o,spec);return o

def test_f1_target_first_counts_and_no_collateral_refusal():
    c=dict(id='counts',label='counts',ai=10,n1i=100,ci=20,n2i=100,source='10 of 100 patients vs 20 of 100 patients at 28 days')
    selected=lane.select_estimator(c,[row()], 'OR', ['RR'])
    assert selected['reconstruction_measure']=='OR'
    assert selected.get('effect') is None and selected['alternatives']
    assert mi.measure_of(selected)==mi.Measure.ODDS_RATIO
    o=prepare([selected,row(id='wrong')],'OR')
    assert [r['id'] for r in o['trials']]==['counts']
    assert o['declared_absent_trials'][0]['lane_refusals']==['TARGET_MEASURE_UNAVAILABLE']
    hr_fallback = prepare([dict(c)], 'HR')
    assert hr_fallback['trials'][0]['measure_identity'] == 'RISK_RATIO'
    assert hr_fallback['served_measure'] == 'RISK_RATIO'  # never manufacture HR from counts
    published=row(scale='OR',source='odds ratio 0.8 at 28 days')
    assert lane.select_estimator(c,[published],'OR')['effect']==.8
    assert prepare([published],'OR')['trials']

@pytest.mark.parametrize('source,refused', [('Mortality during 30 days of follow-up risk ratio 0.8',True),('In-hospital mortality risk ratio 0.8',False)])
def test_f2_semantic_window(source,refused):
    o=prepare([row(source=source)],time='in-hospital')
    assert bool(o['declared_absent_trials'])==refused
    assert bool(extract.timepoint_mismatch('in-hospital',source))==refused

def test_f3_local_clause_and_unresolved():
    r=row(effect=.7,scale='HR',source='The relative risk was 30% lower (hazard ratio, 0.70; 95% CI 0.6 to 0.9).')
    assert mi.measure_of(r)==mi.Measure.HAZARD_RATIO
    assert prepare([r],'HR')['served_measure']=='HAZARD_RATIO'
    bad=row(source='hazard ratio and risk ratio')
    o=prepare([bad])
    assert o['declared_absent_trials'][0]['lane_refusals']==['UNRESOLVED_MEASURE_ATTRIBUTION']
    assert 'MEASURE_MIX_POOLED' not in str(o['lane_problems'])
    assert mi.measure_of(row())==mi.Measure.RISK_RATIO

def test_f5_local_html_cannot_change_build_input(tmp_path):
    dest=tmp_path/rx.OUTPUT;dest.parent.mkdir(parents=True);dest.write_bytes((ROOT/rx.OUTPUT).read_bytes())
    before=rx.load(tmp_path)
    local=tmp_path/rx.HELD;local.parent.mkdir(parents=True);local.write_bytes(b'corrupt synthetic HTML')
    assert rx.load(tmp_path)==before
    with pytest.raises(ValueError,match='HELD_SHA256_MISMATCH'): rx.verify_local_html(tmp_path)

def test_f6_unreadable_origin_is_not_time_mismatch(tmp_path,monkeypatch):
    # Under ROOT so this is the same source-reference route as the production build.
    path=ROOT/'.tmp/fix1/origin-plant.txt';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('Day 1 is baseline. Deaths at day 29.',encoding='utf-8')
    r=row(source='Deaths at day 29.',source_span='Deaths at day 29.',document_ref=path.relative_to(ROOT).as_posix())
    assert prepare([deepcopy(r)])['trials']
    original=Path.read_text
    def fail(p,*args,**kw):
        if p==path: raise OSError('PLANTED_READ_FAILURE')
        return original(p,*args,**kw)
    monkeypatch.setattr(Path,'read_text',fail)
    o=prepare([r]); refused=o['declared_absent_trials'][0]
    assert refused['lane_refusals']==['ORIGIN_SOURCE_UNREADABLE']
    assert path.name in refused['origin_source_error']
    assert 'PLANTED_READ_FAILURE' in refused['origin_source_error']

@pytest.mark.parametrize('slug,pid,counts',[
 ('corticosteroids-covid19-mortality','32876695',(85,151,91,148)),
 ('corticosteroids-covid19-mortality','32678530',(482,2104,1110,4321)),
 ('tocilizumab-covid19-mortality','33933206',(621,2022,729,2094))])
def test_f1_held_counts_served_on_protocol_or(slug,pid,counts):
    from harness import pipeline
    cfg=json.loads((ROOT/'topics'/f'{slug}.json').read_text(encoding='utf-8'))
    records=json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf-8'))
    inp=pipeline.outcome_inputs(slug,cfg,records)
    spec,kind=next((s,k) for s,k in pipeline._outcome_specs(cfg) if s.get('primary'))
    o=pipeline.build_outcome_from_inputs(inp,spec,kind,slug)
    r=next(r for r in o['trials'] if r['id']=='PMID '+pid)
    assert tuple(r[k] for k in ('ai','n1i','ci','n2i'))==counts
    assert r['reconstruction_measure']=='OR'
    if r.get('count_witnesses'):
        abstract=inp['rec_by_id'][pid]['abstract']
        for key,w in r['count_witnesses'].items():
            assert abstract[w['start']:w['end']]==w['span']
            assert int(w['span'].replace(',', ''))==r[key]
    assert o['result']['served_measure']=='ODDS_RATIO'


def test_f3_rendered_scale_uses_result_identity():
    res=dict(k=3, estimate=.68, ci_low=.55, ci_high=.84, scale='HR', served_measure='UNKNOWN')
    assert '(UNKNOWN)' in page._effect_rows(res)[0][1]
    assert '(HR)' not in page._effect_rows(res)[0][1]
    res['served_measure']='HAZARD_RATIO'
    assert '(HR)' in page._effect_rows(res)[0][1]


def test_allocated_counts_abstain_for_ambiguous_arms_or_hr():
    from harness.target_reconstruction import allocated_mortality_counts
    text='100 patients were assigned to receive drug and 100 to receive placebo. Overall, 10 patients (10.0%) in the drug group and 20 patients (20.0%) in the placebo group died within 28 days after randomization.'
    spec={'name':'Mortality','estimand':'OR','timepoint':'28 days'}
    assert allocated_mortality_counts({'abstract':text},spec,['drug'],['placebo'])['ai']==10
    assert allocated_mortality_counts({'abstract':text},spec,['drug','placebo'],['placebo']) is None
    assert allocated_mortality_counts({'abstract':text},dict(spec,estimand='HR'),['drug'],['placebo']) is None


def test_held_cap_and_credence_and_refusal_code_survive_build():
    from harness import pipeline
    reviews={}
    for slug in ('corticosteroids-cap-mortality','sglt2-ckd-progression'):
        cfg=json.loads((ROOT/'topics'/f'{slug}.json').read_text(encoding='utf-8'))
        data=json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf-8'))
        reviews[slug]=pipeline.build_review_core(slug,cfg,data,'fix1')
    cap=next(o for o in reviews['corticosteroids-cap-mortality']['outcomes'] if o['name']=='Hyperglycaemia')
    assert tuple(cap['result'][k] for k in ('k','estimate','ci_low','ci_high'))==(3,2.5522,.2174,29.9652)
    refused=next(r for r in cap['declared_absent_trials'] if r['id']=='PMID 25608756')
    assert refused['reason_code']=='TARGET_MEASURE_UNAVAILABLE'
    o=reviews['sglt2-ckd-progression']['outcomes'][0]
    r=next(r for r in o['trials'] if r['id']=='PMID 30990260')
    assert r['measure_identity']=='HAZARD_RATIO'
    assert o['result']['served_measure']=='HAZARD_RATIO'
    html=page._outcome_block(o,show_inputs=False)
    assert 'served measure: UNKNOWN' not in html


def test_governing_clause_can_name_comparator_and_ci_header():
    r=row(effect=.65,scale='HR',source='Hazard ratio vs warfarin (95% CI) 0.65 (0.52, 0.81); supersedes relative risk 0.66 (0.53-0.82).')
    assert mi.measure_of(r)==mi.Measure.HAZARD_RATIO


def test_target_endpoint_selector_uses_target_only_across_odds(monkeypatch):
    from harness import target_endpoint
    text=('The primary outcome was cardiovascular death or heart failure hospitalization. '
          'Cardiovascular death or heart failure hospitalization occurred in 10 of 100 patients in the drug group and 20 of 100 patients '
          'in the placebo group (hazard ratio, 0.5; 95% CI, 0.3 to 0.8).')
    spec=dict(name='Cardiovascular death or heart failure hospitalization',keywords=['cardiovascular death'],estimand='RR')
    published=target_endpoint.enumerate_candidates(spec,text,None,['drug'],['placebo'])[0]
    counts={k:v for k,v in published.items() if k not in ('effect','ci_low','ci_high','scale')}
    counts.update(ai=10,n1i=100,ci=20,n2i=100,candidate_id='synthetic-counts',source_rank=100)
    monkeypatch.setattr(target_endpoint,'enumerate_candidates',lambda *args:[published,counts])
    r=target_endpoint.select_target_endpoint(spec,text,None,['drug'],['placebo'])['selected']
    assert r['effect']==published['effect'] and r['scale']=='HR'
    odds_spec=dict(spec,estimand='OR')
    r=target_endpoint.select_target_endpoint(odds_spec,text,None,['drug'],['placebo'])['selected']
    assert r['ai']==10 and r.get('effect') is None
    assert r['target_endpoint_class']=='EXACT_TARGET'
    r=target_endpoint.select_target_endpoint(dict(spec,estimand='HR'),text,None,['drug'],['placebo'])['selected']
    assert r['effect']==.5 and r['scale']=='HR'

    recurrent=dict(published, candidate_id='synthetic-recurrent', registry_title='Recurrent hospitalizations and cardiovascular death', scale='RR', source='risk ratio 0.5', source_rank=500)
    monkeypatch.setattr(target_endpoint,'enumerate_candidates',lambda *args:[dict(recurrent),dict(counts)])
    r=target_endpoint.select_target_endpoint(spec,text,None,['drug'],['placebo'])['selected']
    assert r['ai']==10
    assert any(a.get('endpoint_binding_reason')=='RECURRENT_EVENTS_NOT_FIRST_EVENT_PATIENTS' for a in r['target_endpoint_alternatives'])
    r=target_endpoint.select_target_endpoint(dict(spec,name='Recurrent cardiovascular death or heart failure hospitalization'),text,None,['drug'],['placebo'])['selected']
    assert r['effect']==.5
