"""Synthetic odds-boundary plants; no research values are supplied here."""
from copy import deepcopy
import pytest
from harness import lane_integration as lane
from test_fix1 import row, prepare


@pytest.mark.parametrize('target,scale,word', [
    ('OR','RR','risk ratio'), ('OR','HR','hazard ratio'),
    ('OR','IRR','rate ratio'), ('RR','OR','odds ratio'),
    ('HR','OR','odds ratio'), ('IRR','OR','odds ratio')])
def test_cross_odds_boundary_refuses_named_row(target,scale,word):
    r=row(scale=scale,source=word+' 0.8 at 28 days')
    selected=lane.select_estimator(r,[],target)
    o=prepare([selected],target)
    assert not o['trials']
    assert o['declared_absent_trials'][0]['lane_refusals']==['TARGET_MEASURE_UNAVAILABLE']
    assert selected['scale']==scale


@pytest.mark.parametrize('target', ['RR','HR','IRR'])
@pytest.mark.parametrize('scale,word,identity', [
    ('RR','risk ratio','RISK_RATIO'),('HR','hazard ratio','HAZARD_RATIO'),
    ('IRR','rate ratio','RATE_RATIO')])
def test_within_family_admitted_and_disclosed(target,scale,word,identity):
    r=row(scale=scale,source=word+' 0.8 at 28 days')
    selected=lane.select_estimator(r,[],target)
    o=prepare([selected],target)
    assert o['trials'][0]['measure_identity']==identity
    assert not o['declared_absent_trials']
    assert o['served_measure']==identity
    assert selected['scale']==scale


def test_counts_reconstruct_or_published_rr_is_not_relabelled():
    rr=row()
    counts=dict(id='counts',ai=10,n1i=100,ci=20,n2i=100,
                source='10 of 100 patients vs 20 of 100 patients at 28 days')
    selected=lane.select_estimator(rr,[counts],'OR')
    assert selected.get('effect') is None
    assert selected['reconstruction_measure']=='OR'
    assert prepare([selected],'OR')['served_measure']=='ODDS_RATIO'
    assert selected['alternatives'][0]['scale']=='RR'
    assert rr['scale']=='RR'
    published=row(scale='OR',source='odds ratio 0.8 at 28 days')
    assert lane.select_estimator(rr,[counts,published],'OR')['effect']==published['effect']


def test_mixed_risk_rate_is_advisory_with_actual_classes():
    spec=dict(name='Mortality',estimand='RR',timepoint='28 days')
    o=dict(name='Mortality',trials=[row(id='rr'),row(id='hr',scale='HR',source='hazard ratio 0.8 at 28 days')],
           declared_absent_trials=[],result=dict(estimate=.8,scale='RR'))
    lane.prepare(o,spec,{},{}); lane.finish(o,spec)
    assert len(o['trials'])==2 and not o['declared_absent_trials']
    p=next(p for p in o['lane_problems'] if p['code']=='MEASURE_MIX_POOLED')
    assert p['blocking'] is False and p['severity']=='ADVISORY'
    assert o['result']['measure_inputs']=={'HAZARD_RATIO':['hr'],'RISK_RATIO':['rr']}
    assert o['result']['measure_disclosure']['target_measure']=='RISK_RATIO'


def test_hr_target_falls_back_to_published_rr_before_unusable_hr_counts():
    counts=dict(id='counts',ai=10,n1i=100,ci=20,n2i=100,source='at 28 days')
    selected=lane.select_estimator(counts,[row()],'HR')
    assert selected['effect']==.8 and selected['scale']=='RR'
    assert not selected.get('reconstruction_measure')


@pytest.mark.parametrize('target,accepted',[('RR',True),('HR',True),('OR',False)])
def test_design_adjusted_fallback_respects_only_odds_boundary(target,accepted):
    from harness import design_key
    r=dict(id='design-plant',ai=10,n1i=100,ci=20,n2i=100,
           design=dict(design='CLUSTER',unit='CLUSTER',
                       design_action=dict(action='REFUSE'),
                       published_alternative=dict(effect=.8,ci_low=.6,ci_high=.95,
                                                  scale='HR',adjusted=True,
                                                  source='adjusted hazard ratio 0.8',span='adjusted hazard ratio 0.8')))
    assert design_key.maybe_use_published_adjusted(r,target) is accepted
    if accepted:
        assert r['scale']=='HR' and r['effect']==.8 and 'ai' not in r
