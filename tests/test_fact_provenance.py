"""Binding CGX plant: plausible typed digits are not document provenance."""
import json
from pathlib import Path

from harness.gate import check_pooled_verified
from harness import claimgraph


def test_typed_number_without_document_is_refused(tmp_path):
    root = tmp_path
    cache = root / 'cache' / '__plant_cgx__'
    cache.mkdir(parents=True)
    row = {'effect': 0.87, 'ci_low': 0.78, 'ci_high': 0.97,
           'scale': 'HR', 'source': 'Plant trial reported HR 0.87 (0.78-0.97).',
           'verified': 'verified'}
    (cache / 'verified_effects.json').write_text(json.dumps({'plant-row': row}), encoding='utf-8')
    page = root / 'docs' / 'reviews' / '__plant_cgx__'
    page.mkdir(parents=True)
    review = {'slug': '__plant_cgx__', 'outcomes': [{'name': 'Plant outcome',
              'trials': [dict(row, id='plant-row')]}]}
    (page / 'review.json').write_text(json.dumps(review), encoding='utf-8')
    reasons = check_pooled_verified(str(page))
    assert any('UNVERIFIED_FACT' in reason and 'plant-row' in reason for reason in reasons), (
        f'gate pooled-number limb let typed plant-row through: {reasons}')


def elixa_row():
    source = json.loads((claimgraph.ROOT / 'outputs/handover/glp1_regulatory/regulatory_sources_glp1.json').read_text(encoding='utf-8'))['sources'][0]
    return claimgraph.regulatory_fact(source, source['decisions'][0])


def test_real_elixa_positive_control(tmp_path):
    row = elixa_row()
    assert claimgraph.verify_fact(row)['verified']
    assert '[FACT]' in claimgraph.fact_render(row)
    row['verified'] = 'verified'
    page = tmp_path / 'page'
    page.mkdir()
    (page / 'review.json').write_text(json.dumps({'outcomes': [{'trials': [row]}]}), encoding='utf-8')
    assert check_pooled_verified(page) == []


def test_changed_span_or_digits_refused():
    import copy
    row = elixa_row()
    altered = copy.deepcopy(row)
    altered['provenance']['span'] += ' fabricated'
    assert not claimgraph.verify_fact(altered)['verified']
    altered = copy.deepcopy(row)
    altered['effect'] = 0.87
    assert not claimgraph.verify_fact(altered)['verified']
    altered = copy.deepcopy(row)
    altered['provenance']['document_sha256'] = '0' * 64
    assert not claimgraph.verify_fact(altered)['verified']


def test_exact_downstream_invalidation():
    import copy
    graph = claimgraph.ClaimGraph()
    row = elixa_row()
    graph.add('trial', 'FACT', row=row)
    graph.add('pool', 'TRANSFORMATION', operation='count', inputs=[1], value=1, depends_on=['trial'])
    graph.add('claim', 'INTERPRETATION', text='One reading.', alternatives=['Another reading.'], depends_on=['pool'])
    graph.add('independent', 'TRANSFORMATION', operation='count', inputs=[], value=0)
    digest = row['provenance']['document_sha256']
    altered = copy.deepcopy(graph)
    altered.objects['trial']['row']['provenance']['span'] += ' tampered cached span'
    assert not claimgraph.verify_fact(altered.objects['trial']['row'])['verified']
    assert altered.invalidate(digest) == ['claim', 'pool', 'trial']
    assert 'UNRENDERABLE' in altered.render('claim')
    assert 'UNRENDERABLE' not in altered.render('independent')
    assert not graph.invalidated
