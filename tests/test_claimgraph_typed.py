import math

import pytest

from harness import claimgraph


def test_registered_id_cannot_launder_different_sentence():
    graph = claimgraph.ClaimGraph()
    graph.add('count', 'TRANSFORMATION', operation='count', inputs=['a', 'b'], value=2)
    rendered = graph.render('count')
    assert claimgraph.scan_rendered(rendered, graph)['with_object'] == 1
    altered = rendered.replace('count: 2.', 'count: 7.')
    assert claimgraph.scan_rendered(altered, graph)['violations'][0]['code'] == 'RENDERING_MISMATCH'
    naked = '<p>Seven trials were eligible.</p>'
    assert claimgraph.scan_rendered(naked, graph)['violations'][0]['code'] == 'SENTENCE_WITHOUT_OBJECT'
    with pytest.raises(ValueError, match='SENTENCE_WITHOUT_OBJECT'):
        graph.render('nonexistent')


def test_all_four_class_contracts():
    graph = claimgraph.ClaimGraph()
    graph.add('fact', 'FACT', row={'id': 'plant', 'effect': 0.87})
    graph.add('log', 'TRANSFORMATION', operation='log', inputs=0.87, value=math.log(0.87))
    graph.add('judgement', 'JUDGEMENT', text='Endpoint compatibility is owed.', basis={'rule_id': 'test-only'}, adjudication='OWED')
    graph.add('interpretation', 'INTERPRETATION', text='One reasonable reading.', alternatives=['Another reasonable reading.'])
    assert [v['code'] for v in graph.check()] == ['UNVERIFIED_FACT']
    assert '[UNVERIFIED_FACT]' in graph.render('fact')
    assert '0.87' in graph.render('fact')
    assert '[TRANSFORMATION]' in graph.render('log')
    assert '[JUDGEMENT]' in graph.render('judgement')
    assert 'Alternative:' in graph.render('interpretation')
    graph.objects['log']['value'] = 0
    graph.objects['judgement']['basis'] = None
    graph.objects['interpretation']['alternatives'] = []
    codes = {v['code'] for v in graph.check()}
    assert {'TRANSFORMATION_MISMATCH', 'JUDGEMENT_WITHOUT_BASIS', 'INTERPRETATION_WITHOUT_ALTERNATIVE'} <= codes
    assert 'UNRENDERABLE' in graph.render('interpretation')


def test_certainty_arithmetic_and_missing_domain():
    names = ('risk_of_bias', 'inconsistency', 'imprecision', 'publication_bias', 'indirectness')
    grade = {'start': 'high', 'domains': {n: {'assessed': True, 'downgrade': 0} for n in names}, 'certainty': 'moderate', 'downgrades': 0}
    assert claimgraph.certainty_violations({'grade': grade})
    assert claimgraph.certainty_object(grade)['value'] == 'high'
    grade['domains']['indirectness']['assessed'] = False
    assert claimgraph.certainty_object(grade)['value'] == 'provisional'
    assert 'moderate' not in claimgraph.certainty_render({'grade': grade})
    del grade['domains']['publication_bias']
    assert claimgraph.certainty_object(grade)['value'] == 'provisional'


def test_unknown_document_invalidates_nothing():
    graph = claimgraph.ClaimGraph()
    graph.add('a', 'FACT', row={'provenance': 'abstract'})
    assert graph.invalidate('0' * 64) == []


def test_claim_mark_is_checked_not_just_id():
    graph = claimgraph.ClaimGraph()
    row = {'id': 'plant', 'effect': 0.87}
    graph.add('a', 'FACT', row=row)
    forged = graph.render('a').replace('data-claim-class="UNVERIFIED_FACT"', 'data-claim-class="FACT"')
    assert claimgraph.scan_rendered(forged, graph)['violations'][0]['code'] == 'RENDERING_MISMATCH'


def test_page_and_manuscript_use_provisional_glp1():
    import json
    from harness import page, manuscript
    review = json.loads((claimgraph.ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json').read_text(encoding='utf-8'))
    for rendered in (page.render_page(review), manuscript.render(review)):
        assert 'GRADE certainty: provisional.' in rendered
        assert 'data-claim-id="grade-certainty"' in rendered


def test_cycles_refused():
    graph = claimgraph.ClaimGraph()
    graph.add('a', 'TRANSFORMATION', operation='count', inputs=[], value=0, depends_on=['b'])
    graph.add('b', 'TRANSFORMATION', operation='count', inputs=[], value=0, depends_on=['a'])
    assert {v['code'] for v in graph.check()} == {'CYCLIC_DEPENDENCY'}


@pytest.mark.parametrize('slug', ['corticosteroids-cap-mortality', 'colchicine-secondary-cv-prevention'])
def test_base_blanket_absence_plant_and_fresh_consumer(slug):
    import json
    from harness import manuscript
    folder = claimgraph.ROOT / 'docs/reviews' / slug
    review = json.loads((folder / 'review.json').read_text(encoding='utf-8'))
    # The plant is the immutable lane base, not regenerated working-tree HTML.
    import subprocess
    baseline = subprocess.check_output(['git', 'show', 'e3b70bfa36dc65a3920b20fd4e2d628a270e7d28:docs/reviews/' + slug + '/index.html']).decode('utf-8')
    assert claimgraph.legacy_scope_violations(review, baseline)
    rendered = manuscript.render(review)
    assert not claimgraph.legacy_scope_violations(review, rendered)
    assert 'Unpooled per-item states' in rendered


def test_index_provenance_is_not_legacy_verification_label(tmp_path):
    import json
    from harness import index
    folder = tmp_path / 'docs/reviews/plant'
    folder.mkdir(parents=True)
    review = {'outcomes': [{'trials': [{'id': 'plant', 'verified': 'verified', 'effect': .87}]}]}
    (folder / 'review.json').write_text(json.dumps(review), encoding='utf-8')
    rendered = index._verification_section(str(tmp_path / 'docs'))
    assert '0 FACT of 1' in rendered
    assert '1 UNVERIFIED_FACT of 1' in rendered


def test_gate_refuses_unregistered_html_and_unbased_judgement(tmp_path):
    import json
    from harness import gate
    review = {'outcomes': [], 'claimgraph': {'typed_objects': [
        {'claim_id': 'j', 'class': 'JUDGEMENT', 'text': 'Eligible.', 'adjudication': 'OWED'}]}}
    (tmp_path / 'review.json').write_text(json.dumps(review), encoding='utf-8')
    (tmp_path / 'index.html').write_text('<p>Seven trials were eligible.</p>', encoding='utf-8')
    reasons = gate.check_typed_renderings(tmp_path)
    assert any('SENTENCE_WITHOUT_OBJECT' in r for r in reasons)
    assert any('JUDGEMENT_WITHOUT_BASIS' in r for r in reasons)
