"""Synthetic selector plants: target-first applies only across odds."""
from copy import deepcopy
import pytest
from harness import design_key, lane_integration as lane, measure_identity as mi
from test_fix1 import row, prepare


def counts():
    return dict(id='synthetic', label='synthetic', ai=10, n1i=100, ci=20, n2i=100,
                source='10 of 100 patients vs 20 of 100 patients at 28 days')


@pytest.mark.parametrize('start_with_counts', [False, True])
def test_rr_target_preserves_published_hr_with_hr_peers(start_with_counts):
    hr = row(scale='HR', source='hazard ratio 0.8 at 28 days')
    selected, candidates = (counts(), [hr]) if start_with_counts else (hr, [counts()])
    original = deepcopy((selected, candidates))
    prior = design_key.select_estimator_by_source_hierarchy(selected, candidates, 'RR')
    actual = lane.select_estimator(selected, candidates, 'RR', [mi.Measure.HAZARD_RATIO])
    assert actual == prior
    assert actual['effect'] == hr['effect'] and actual['scale'] == 'HR'
    assert actual['selected_estimator'] == 'published_effect_ci'
    assert actual['alternatives'][0]['derivation'] != 'reported'
    out = prepare([actual, row(id='peer', scale='HR', source=hr['source'])], 'RR')
    assert out['served_measure'] == 'HAZARD_RATIO'
    assert out['target_measure'] == 'RISK_RATIO'
    assert all(r['measure_identity'] == 'HAZARD_RATIO' for r in out['trials'])
    assert (selected, candidates) == original


def test_or_target_reconstructs_from_counts_instead_of_published_rate():
    rate = row(scale='IRR', source='rate ratio 0.8 at 28 days')
    actual = lane.select_estimator(rate, [counts()], 'OR')
    assert actual.get('effect') is None and actual['reconstruction_measure'] == 'OR'
    assert actual['alternatives'][0]['scale'] == 'IRR'
    out = prepare([actual], 'OR')
    assert out['served_measure'] == 'ODDS_RATIO' and not out['declared_absent_trials']


def test_or_target_rr_without_counts_refuses_only_named_row():
    selected = lane.select_estimator(row(id='incompatible'), [], 'OR')
    out = prepare([selected, row(id='compatible', scale='OR', source='odds ratio 0.8 at 28 days')], 'OR')
    assert [r['id'] for r in out['trials']] == ['compatible']
    assert [(r['id'], r['lane_refusals']) for r in out['declared_absent_trials']] == [
        ('incompatible', ['TARGET_MEASURE_UNAVAILABLE'])]


@pytest.mark.parametrize('target', ['RR', 'HR', 'IRR'])
@pytest.mark.parametrize('scale,word', [('RR', 'risk ratio'), ('HR', 'hazard ratio'), ('IRR', 'rate ratio')])
def test_no_odds_crossing_returns_exact_prior_selector(target, scale, word):
    published = row(scale=scale, source=word+' 0.8 at 28 days')
    prior = design_key.select_estimator_by_source_hierarchy(published, [counts()], target)
    assert lane.select_estimator(published, [counts()], target) == prior


def test_unknown_measure_still_refuses_closed():
    actual = lane.select_estimator(row(source='hazard ratio and risk ratio'), [], 'RR')
    out = prepare([actual], 'RR')
    assert not out['trials']
    assert out['declared_absent_trials'][0]['lane_refusals'] == ['UNRESOLVED_MEASURE_ATTRIBUTION']


@pytest.mark.parametrize('target,scale,word,want_counts', [
    ('RR', 'HR', 'hazard ratio', False),
    ('RR', 'RR', 'risk ratio', False),
    ('OR', 'IRR', 'rate ratio', True),
    ('OR', 'OR', 'odds ratio', False),
    ('RR', 'OR', 'odds ratio', True)])
def test_endpoint_ranking_crosses_only_odds(monkeypatch, target, scale, word, want_counts):
    from harness import target_endpoint as ep
    published = dict(row(scale=scale, source=word+' 0.8 at 28 days'),
                     candidate_id='published', target_endpoint_class=ep.EXACT_TARGET, source_rank=3)
    registry = dict(counts(), candidate_id='registry', target_endpoint_class=ep.EXACT_TARGET, source_rank=1)
    monkeypatch.setattr(ep, 'canonical_components', lambda spec: ['synthetic endpoint'])
    monkeypatch.setattr(ep, 'enumerate_candidates', lambda *args: [deepcopy(published), deepcopy(registry)])
    selected = ep.select_target_endpoint(dict(name='Synthetic endpoint', estimand=target), '', [], [], [])['selected']
    if want_counts:
        assert selected['ai'] == registry['ai'] and selected.get('effect') is None
    else:
        assert selected['effect'] == published['effect'] and selected['scale'] == scale
