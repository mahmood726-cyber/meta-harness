import copy
import json

import pytest

from harness import claimgraph, manuscript, page, risk_prose


@pytest.fixture(scope='module')
def review():
    return json.loads((claimgraph.ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json').read_text(encoding='utf-8'))


def test_owned_sections_have_no_unregistered_units(review):
    graph = claimgraph.review_graph(review)
    for rendered in (manuscript.render(review), page._riskofbias(review, False)):
        scan = claimgraph.scan_rendered(rendered, graph)
        assert scan['rendered_units'] == scan['with_object']
        assert not scan['violations']
    assert not graph.check()


def test_typed_number_plant_fails_and_marker_cannot_launder_it(review):
    graph = claimgraph.review_graph(review)
    rendered = manuscript.render(review)
    scan = claimgraph.scan_rendered(rendered + '<p>The pooled hazard ratio was 7.77.</p>', graph)
    assert scan['violations'][-1]['code'] == 'SENTENCE_WITHOUT_OBJECT'
    forged = graph.render('risk-d3-states').replace('7 of 7', '8 of 7')
    assert forged != graph.render('risk-d3-states')
    assert claimgraph.scan_rendered(forged, graph)['violations'][0]['code'] == 'RENDERING_MISMATCH'


def test_d3_and_sensitivity_rederive_from_items_not_aggregate_flags(review):
    changed = copy.deepcopy(review)
    changed['rob_sensitivity'].update(n_trials=12345, n_rob_rated=12345, any_high=True)
    rendered = risk_prose.render(changed)
    assert 'NOT ASSESSED for 7 of 7' in rendered
    assert '12345' not in rendered
    key = next(k for k, entry in changed['rob2']['trials'].items()
               if entry['domains']['D3_missing_outcome_data']['level'] == 'not assessed')
    changed['rob2']['trials'][key]['domains']['D3_missing_outcome_data']['level'] = 'low'
    assert 'NOT ASSESSED for 6 of 7' in risk_prose.render(changed)
    changed['rob2']['trials'][key]['overall'] = 'high'
    rendered = risk_prose.render(changed)
    assert '1 adverse rating exclusions' in rendered
    assert '6 of 7 rows retained' in rendered


def test_interpretations_always_render_alternative_and_missing_alternative_refuses(review):
    graph = claimgraph.review_graph(review)
    ids = [cid for cid, obj in graph.objects.items() if obj['class'] == 'INTERPRETATION']
    assert ids
    for cid in ids:
        assert 'Alternative:' in graph.render(cid)
    graph.objects[ids[0]]['alternatives'] = []
    assert 'INTERPRETATION_WITHOUT_ALTERNATIVE' in graph.render(ids[0])


def test_grade_is_arithmetic_or_provisional_never_stale_label(review):
    changed = copy.deepcopy(review)
    changed['grade'].update(certainty='high', downgrades=999)
    rendered = risk_prose.render(changed)
    assert 'GRADE certainty: provisional.' in rendered
    assert 'Recorded domain downgrades: 0.' in rendered
    assert 'Recorded domain downgrades: 999.' not in rendered
    for domain in changed['grade']['domains'].values():
        domain.update(assessed=True, downgrade=0)
    changed['grade']['domains']['imprecision']['downgrade'] = 1
    assert 'GRADE certainty: moderate.' in risk_prose.render(changed)


def test_source_mutation_refuses_registered_pool(review):
    graph = claimgraph.review_graph(review)
    ref = graph.objects['manuscript-result']['input_refs'][0]
    graph.objects[ref]['row']['effect'] = 7.77
    assert 'UNRENDERABLE' in graph.render('manuscript-result')
    assert 'UNRENDERABLE' in graph.render('manuscript-forest-point-0')


def test_all_owned_ids_registered_before_html_is_consumed(review):
    graph = claimgraph.review_graph(review)
    expected = set(graph.objects)
    manuscript.render(review)
    risk_prose.render(review)
    assert set(graph.objects) == expected
    graph.objects['risk-d3-states']['inputs'][0]['level'] = 'high'
    assert 'TRANSFORMATION_MISMATCH' in graph.render('risk-d3-states')


def test_funding_denominator_does_not_claim_primary_pool_membership(review):
    graph = claimgraph.review_graph(review)
    summary = graph.render('risk-funding-summary')
    assert 'Recorded funding entries:' in summary
    assert 'pooled trials' not in summary
    assert graph.objects['risk-funding-summary']['inputs'] == review['funding']
