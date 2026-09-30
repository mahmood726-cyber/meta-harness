"""FIX4 refusal-ontology and assertion-preservation plants (synthetic inputs)."""
from copy import deepcopy
import pytest
from harness import lane_integration as lane
from test_integrate2 import row, outcome
from scripts import error_rate_blind_v2 as blind
from regex_layer.specs import FIX4_SPECS
from test_regex_plants import _inline_pattern


@pytest.mark.parametrize('changes,code', [
    ({'source': 'day 60'}, 'TIMEPOINT_MISMATCH'),
    ({'scale': 'OR', 'source': 'odds ratio at 28 days'}, 'TARGET_MEASURE_UNAVAILABLE'),
    ({'source': 'hazard ratio and odds ratio'}, 'UNRESOLVED_MEASURE_ATTRIBUTION'),
    ({'provenance': 'RELAYED'}, 'RELAYED_COUNTS_NOT_BOUND'),
    ({'table_conflict': 'TABLE_VALUE_MISMATCH'}, 'TABLE_VALUE_MISMATCH'),
])
def test_row_refusals_have_ontology_without_erasing_reason(changes, code):
    o = outcome([row(**changes), row(id='negative')])
    spec = dict(name='event', estimand='RR', timepoint='28 days')
    lane.prepare(o, spec, {}, {})
    assert [r['id'] for r in o['trials']] == ['negative']
    r, = o['declared_absent_trials']
    assert r['state'] == 'REFUSED_ON_EVIDENCE'
    assert r['reason_code'] == code and r['lane_refusals'] == [code]
    assert r['source'] == row(**changes)['source']
    assert 'state' not in o['trials'][0]


def test_population_hold_has_ontology_and_same_population_negative():
    refused = row(id='refused', source='safety population', reason_code='POPULATION_MISMATCH')
    original = outcome([row(source='safety population')], kind='harm', declared_absent_trials=[refused])
    spec = dict(name='event', estimand='RR')
    cfg = {'harm_outcomes': [spec]}
    actual = deepcopy(original)
    assert lane.prepare(actual, spec, cfg, {})
    moved = next(r for r in actual['declared_absent_trials'] if r['id'] == 'plant-A')
    assert moved['state'] == 'REFUSED_ON_EVIDENCE'
    assert moved['lane_refusals'] == ['POPULATION_RULE_INCONSISTENT']
    assert not actual['trials']
    original['declared_absent_trials'] = []
    assert not lane.prepare(original, spec, cfg, {})
    assert [r['id'] for r in original['trials']] == ['plant-A']
    assert 'state' not in original['trials'][0]


@pytest.mark.parametrize('site', sorted(FIX4_SPECS))
def test_new_regex_plants_and_mutants(site):
    import re
    spec = FIX4_SPECS[site]
    rx = _inline_pattern(site)
    for text, groups in spec['plants']['accept']:
        assert rx.search(text).groups() == groups
    for text in spec['plants']['refuse']:
        assert rx.search(text) is None
    # Each pair rejects both the always-match and never-match mutants.
    assert any(re.compile(r'(?!)').search(t) is None for t, _ in spec['plants']['accept'])
    assert any(re.compile(r'.*').search(t) is not None for t in spec['plants']['refuse'])


def test_incremental_mode_only_checks_missing_ids(monkeypatch):
    pop, topics = blind.population()
    sample = blind.read(blind.ROOT / 'docs/error_rate_sample.json')
    ids = {r['row_id'] for r in sample['rows']}
    summary, rows, _ = blind.census(new_only=True)
    assert {r['row_id'] for r in rows} == set(pop) - ids
    assert summary['N_uncensused'] == len(rows)
    rid = 'synthetic::Hyperkalemia::plant'
    pop[rid] = ({'name': 'Hyperkalemia'}, {'id': 'plant', 'ai': 8}, 'real pooled number')
    monkeypatch.setattr(blind, 'population', lambda root: (pop, topics))
    calls = []
    def missing(request, root):
        calls.append(request['row_id'])
        return {'verdict': 'NOT_RECHECKABLE', 'reason': 'synthetic source absent'}
    monkeypatch.setattr(blind, 'extract', missing)
    _, rows, _ = blind.census(new_only=True)
    assert set(calls) == (set(pop) - ids)
    assert next(r for r in rows if r['row_id'] == rid)['verdict'] == 'NOT_RECHECKABLE'
