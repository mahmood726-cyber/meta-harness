"""Hostile-audit regressions: held evidence plus explicitly artificial plants."""
import copy
import json
from pathlib import Path

import pytest

from harness import harms, known_missing, effect_type, screen, reason_audit, design_key
from harness import comparator_second_pass, pipeline, gate

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'glp1-ra-mace-t2d'


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


@pytest.fixture
def review():
    return load(f'docs/reviews/{SLUG}/review.json')


@pytest.mark.parametrize('name', ['Gastrointestinal adverse events', 'Adverse events leading to discontinuation'])
def test_generic_adverse_events_are_not_specific_harms(name):
    assert harms.reporting_signal('Serious adverse events were similar between the two groups.', {'name': name}) is None
    assert harms.reporting_signal('Serious adverse events were reported in 49.6% vs. 53.8%.', {'name': name}) is None
    assert harms.reporting_signal('Adverse events were similar.', {'name': name, 'keywords': ['adverse events']}) is None


def test_discontinuation_requires_harm_cause():
    spec = {'name': 'Adverse events leading to discontinuation'}
    assert harms.reporting_signal('Participants returned for a final visit and discontinuation from study treatment.', spec) is None
    assert harms.reporting_signal('Adverse events led to treatment discontinuation in 10% versus 5%.', spec)
    assert harms.reporting_signal('Nausea occurred more frequently.', {'name': 'Gastrointestinal adverse events'})


def test_missing_deduplicates_family_and_preserves_refusal(review):
    signals = {'known_eligible_missing': [{'trial': 'FLOW'}]}
    rows = known_missing._missing_candidates(review, signals)
    assert sum('38785209' in str(r.get('id')) for r in rows) == 1
    assert not any(r.get('trial') == 'FLOW' for r in rows)
    panel = review['outcomes'][0]['known_missing_sensitivity']['rows']
    assert len(panel) == 3
    assert all(r['value_status'] == 'HELD_VALUE_TYPE_REFUSED' for r in panel)
    assert all(r['missing_class'] == 'EFFECT_TYPE_REFUSED' for r in panel)
    assert all('sensitivity' not in r for r in panel)
    assert all('effect' not in r and r['held_refused_effect']['effect'] is not None for r in panel)
    from harness.page import render_outcome_block
    outcome = review['outcomes'][0]
    assert render_outcome_block(outcome) == render_outcome_block(json.loads(json.dumps(outcome, sort_keys=True)))


def test_overlap_is_recomputed_when_pool_changes(review):
    records = load(f'cache/{SLUG}/records.json')
    records['comparator_fulltext'] = (ROOT / f'cache/{SLUG}/comparator_fulltext.txt').read_text(encoding='utf-8')
    rows = review['outcomes'][0]['trials']
    def overlap(selected):
        return comparator_second_pass.apply(SLUG, {}, records, {}, {}, pooled_rows=selected)['overlap']
    current = overlap(rows)
    assert current['shared_k'] == 6
    assert current['only_ours'] == ['SOUL']
    assert set(current['only_theirs']) == {'HARMONY Outcomes', 'AMPLITUDE-O'}
    changed = overlap([r for r in rows if '27295427' not in r['id']])
    assert changed['shared_k'] == current['shared_k'] - 1
    assert 'LEADER' in changed['only_theirs']


def test_title_only_leader_plant():
    config = load(f'topics/{SLUG}.json')
    rec = next(r for r in load(f'cache/{SLUG}/records.json')['records'] if r['id'] == '27295427')
    rec['title'] = 'Cardiovascular outcomes'
    assert screen.screen_record(rec, config['include'], [])[0] == 'include'
    assert screen.run([rec], config)['decisions'][0]['decision'] == 'include'
    rec['abstract'] = ''
    assert screen.screen_record(rec, config['include'], [])[0] == 'exclude'


def test_adjustment_unknown_without_typed_evidence():
    for source in ('No adjustments for multiplicity were performed.', 'hazard ratio, 0.8'):
        row = {'id': 'ARTIFICIAL', 'derivation': 'reported', 'source': source}
        assert design_key.key_for_trial(row)['estimator_source'] == 'ADJUSTMENT_UNKNOWN'


def test_gate_relocates_span_and_recomputes_id(review, tmp_path):
    assert effect_type.check_review(review) == []
    planted = copy.deepcopy(review)
    planted['outcomes'][0]['effect_types'][0]['axes']['censoring']['basis']['span'] = 'AUDIT_UNLOCATED_SPAN_NOT_REAL_EVIDENCE'
    errors = effect_type.check_review(planted)
    assert any('UNLOCATED_AXIS_SPAN' in e for e in errors)
    assert any('ID_MISMATCH' in e for e in errors)
    (tmp_path / 'review.json').write_text(json.dumps(planted), encoding='utf-8')
    assert gate.check_effect_types(tmp_path)
    planted = copy.deepcopy(review)
    planted['outcomes'][0]['trials'][0]['effect'] += 0.1
    assert any('ID_MISMATCH' in e for e in effect_type.check_review(planted))
    planted = copy.deepcopy(review)
    planted['strands']['additional_effect_types'][0]['axes']['censoring']['basis']['span'] = 'ARTIFICIAL UNLOCATED STRAND SPAN'
    assert effect_type.check_review(planted)


def test_reason_audit_requires_same_endpoint_and_preserves_flow_refusal(review):
    source = [{'source_id': 'artificial', 'text': 'The kidney-specific composite had a hazard ratio, 0.79; 95% CI, 0.66 to 0.94.'}]
    assert reason_audit.find_value_in_sources(source, ['cardiovascular', 'composite'], 'Major adverse cardiovascular events') is None
    flow = next(t for t in review['outcomes'][0]['effect_type_refusals'] if '38785209' in t['id'])
    assert flow['state'] == 'EFFECT_TYPE_REFUSED'
    assert flow['reason_code_audit']['verdict'] == 'REASON_TRUE'
    assert flow['reason_code_audit']['detail'] == flow['unification']['reason']


def test_search_obligations_are_ledger_derived(review):
    config = load(f'topics/{SLUG}.json')
    ledger = load(f'cache/{SLUG}/retrieval_ledger.json')
    obj = pipeline.independent_search_obligations(config, ledger)
    assert obj == review['search']['amended_obligations']
    assert obj['status'] == 'UNMET'
    assert len(obj['databases']) == 7
    assert all(r['status'] == 'UNMET' for r in obj['databases'])
    html = (ROOT / f'docs/reviews/{SLUG}/index.html').read_text(encoding='utf-8')
    for row in obj['databases']:
        assert row['database'] in html
    planted = {'sources': [{'kind': 'CENTRAL', 'state': 'RAN_ZERO', 'discovery_capable': True, 'source_id': 'artificial'}]}
    updated = pipeline.independent_search_obligations(config, planted)
    assert next(r for r in updated['databases'] if r['database'] == 'Cochrane CENTRAL')['status'] == 'MET'
    assert updated['status'] == 'UNMET'


def test_composite_describes_selected_endpoint(review):
    outcome = review['outcomes'][0]
    assert not outcome['result'].get('composite_heterogeneity')
    elixa = next(t for t in outcome['trials'] if '26630143' in t['id'])
    evidence = next(e for e in outcome['effect_types'] if e['effect_type_id'] == elixa['effect_type_id'])
    assert evidence['axes']['endpoint_components']['value'] == ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
    assert 'unstable angina' in elixa['source']
