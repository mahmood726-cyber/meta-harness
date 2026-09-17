import copy
import json

from harness import claimgraph as cg, page, section_claims as sections
from scripts.claim_scope_cgx3c import census


def review():
    return json.loads((cg.ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json').read_text(encoding='utf-8'))


def test_plain_number_and_forged_marker_are_refused():
    r = review()
    graph = cg.review_graph(r)
    body = page._screening(r, False)
    scan = cg.scan_rendered(body + '<p>There were 987654 screened records.</p>', graph)
    assert any(v['code'] == 'SENTENCE_WITHOUT_OBJECT' and '987654' in v['detail'] for v in scan['violations'])
    cid = next(cid for cid, obj in graph.objects.items() if obj.get('operation') == 'selection_flow')
    forged = f'<p data-claim-id="{cid}" data-claim-class="TRANSFORMATION">987654 records screened.</p>'
    assert cg.scan_rendered(forged, graph)['violations'][0]['code'] == 'RENDERING_MISMATCH'


def test_selection_counts_ignore_stale_totals_and_follow_per_item_states():
    r = review()
    r['search']['n_records'] = 987654
    r['outcomes'][0]['result']['k'] = 987654
    graph = sections.local_graph(r)
    cid = next(cid for cid, obj in graph.objects.items() if obj.get('operation') == 'selection_flow')
    value = graph.recompute(cid)
    assert value['screened_records'] == len(r['screening']['records'])
    assert value['pooled_primary']['trials'] != 987654
    row = graph.objects[cid]['inputs']['primary']['declared_absent_trials'][0]
    row['state'] = 'REFUSED_ON_EVIDENCE'
    assert 'TRANSFORMATION_MISMATCH' in graph.render(cid)


def test_ledger_field_is_a_projection_not_a_verified_fact():
    graph = cg.ClaimGraph()
    row = {'id': 'fixture', 'state': 'EXTRACTION_NOT_PERFORMED'}
    cid = sections.projection(graph, row, 'state')
    assert 'Recorded state: EXTRACTION_NOT_PERFORMED' in graph.render(cid)
    assert graph.objects[cid]['class'] == 'TRANSFORMATION'
    row['state'] = 'OUTCOME_NOT_IN_SOURCE'
    assert 'TRANSFORMATION_MISMATCH' in graph.render(cid)
    row = {'found_by': ['source-one']}
    graph = cg.ClaimGraph()
    cid = sections.projection(graph, row, 'found_by')
    row['found_by'].append('source-two')
    assert 'TRANSFORMATION_MISMATCH' in graph.render(cid)


def test_harms_are_fully_registered_without_promoting_absence():
    r = review()
    scan = cg.scan_rendered(page._harms(r, False), cg.review_graph(r))
    assert not scan['violations']
    assert scan['with_object'] == scan['rendered_units']
    assert 'KNOWN_REPORTED_NOT_YET_EXTRACTED' in page._harms(r, False)
    assert 'do not establish harm absence' in page._harms(r, False)


def test_parity_contradiction_is_computed_not_repeated():
    r = review()
    assert 'UNRENDERABLE parity relation' in sections.parity_check(r)
    altered = copy.deepcopy(r)
    altered['comparator']['overlap']['only_ours'] = []
    assert 'Counts reconcile' in sections.parity_check(altered)
    assert 'identifier-level trial-set validation remains owed' in sections.parity_check(altered)


def test_interpretations_render_alternatives_and_do_not_mask_plants():
    r = review()
    graph = cg.review_graph(r)
    for key in ('small-k', 'oa', 'screening'):
        html = sections.boundary(r, key)
        assert 'Alternative:' in html
        assert cg.scan_rendered(html, graph)['with_object'] == 1
    html = sections.boundary(r, 'oa') + '<th>7 trials were included.</th>'
    assert cg.scan_rendered(html, graph)['violations'][0]['code'] == 'SENTENCE_WITHOUT_OBJECT'


def test_duplicate_screened_identifier_fails_closed():
    r = review()
    r['screening']['records'].append(copy.deepcopy(r['screening']['records'][0]))
    assert 'UNRECOMPUTABLE_TRANSFORMATION' in sections.selection_flow(r)


def test_retrieval_cells_and_query_basis_are_registered():
    r = review()
    graph = cg.review_graph(r)
    for html in (sections.retrieval_rows(r['search']['retrieval']),
                 sections.retrieval_basis_rows(r['search']['retrieval_class'])):
        assert not cg.scan_rendered(html, graph)['violations']
    source = r['search']['sources'][0]
    for index in range(len(source['queries'])):
        assert cg.scan_rendered(sections.query_render(source, index), graph)['with_object'] == 1


def test_query_removal_and_retrieval_mutation_refuse():
    source = {'queries': ['fixture query']}
    graph = sections.local_graph({'search': {'sources': [source]}})
    cid = next(cid for cid, obj in graph.objects.items() if obj.get('operation') == 'query_item')
    source['queries'].clear()
    assert 'UNRECOMPUTABLE_TRANSFORMATION' in graph.render(cid)
    source = {'state': 'RAN_ERROR', 'error': 'fixture failure'}
    graph = cg.ClaimGraph()
    cid = sections.aggregate(graph, 'retrieval_cell', {'source': source, 'field': 'state'}, 'Retrieval ledger')
    source['state'] = 'RAN_ZERO'
    assert 'TRANSFORMATION_MISMATCH' in graph.render(cid)
