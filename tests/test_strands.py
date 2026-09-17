"""Synthetic fixtures test general strand refusal, never clinical findings."""
import copy
import json
from pathlib import Path

from harness import effect_type


def test_two_strands_render_refused_source():
    from harness.strands import build, render
    target = {'binding_axes': ['effect_measure'], 'axes': {
        'effect_measure': effect_type.field('HR', rule_id='synthetic protocol')}}
    rows = [dict(id=str(i), label='Synthetic ' + str(i), scale='HR', effect=e,
                 ci_low=e / 1.2, ci_high=e * 1.2, source='synthetic fixture')
            for i, e in enumerate([0.8, 0.9, 1.0], 1)]
    rows[-1].update(source_level=1, document_sha256='invalid',
                    document_path='missing-fixture', span='unlocated')
    config = {'slug': 'synthetic-fixture', 'strands': [
        {'id': 'PRIMARY', 'label': 'Primary fixture', 'primary': True,
         'membership_rule': {'exclude_ids': ['2']}},
        {'id': 'ALL', 'label': 'All fixture', 'primary': False,
         'membership_rule': {'exclude_ids': []}}]}
    decisions = [dict(id=r['id'], decision='include') for r in rows]
    doc = build(config, rows, target, decisions)
    assert [s['k'] for s in doc['strands']] == [1, 2]
    assert all(s['refused'][0]['status'] == 'UNVERIFIED_FACT/REFUSED' for s in doc['strands'])
    assert 'UNVERIFIED_FACT/REFUSED' in render({'strands': doc})
    assert 'source' in render({'strands': doc})
    assert doc == build(config, copy.deepcopy(rows), target, decisions)


def test_harness_contains_no_topic_slugs():
    root = Path(__file__).resolve().parents[1]
    slugs = [p.stem for p in (root / 'topics').glob('*.json')]
    found = [(p.name, slug) for p in (root / 'harness').rglob('*.py')
             for slug in slugs if slug in p.read_text(encoding='utf-8')]
    assert found == []


def test_binding_and_eligibility_refusals_are_visible():
    from harness.strands import build, render
    target = {'binding_axes': ['censoring'], 'axes': {
        'censoring': effect_type.field('on-study', rule_id='fixture protocol')}}
    rows = [dict(id=str(i), label='Synthetic ' + str(i), scale='HR', effect=0.8,
                 ci_low=0.6, ci_high=1.0, source='on-treatment') for i in range(2)]
    config = {'slug': 'fixture', 'strands': [dict(id='A', label='A', primary=True,
                                                membership_rule={'exclude_ids': []})]}
    doc = build(config, rows, target, [dict(id='0', decision='include'),
                                      dict(id='1', decision='exclude', reason='wrong design')])
    strand = doc['strands'][0]
    assert strand['k'] == 0 and strand['pool'] is None
    assert [(r['axis'], r['status']) for r in strand['refused']] == [
        ('censoring', 'REFUSED'), ('eligibility', 'REFUSED')]
    html = render({'strands': doc})
    assert 'wrong design' in html and 'censoring' in html


def test_primary_selection_is_applied_before_outcome_pooling():
    from harness.pipeline import _build_outcome
    declaration = dict(id='A', label='A', primary=True, membership_rule={'exclude_ids': ['2']})
    spec = dict(name='Synthetic endpoint', keywords=['endpoint'], estimand='HR', primary=True,
                effect_type_target={'binding_axes': ['effect_measure'], 'axes': {
                    'effect_measure': effect_type.field('HR', rule_id='fixture protocol')}})
    included = [dict(id=str(i), id_type='pmid', label='Synthetic ' + str(i)) for i in (1, 2)]
    records = {str(i): dict(id=str(i), abstract='Synthetic endpoint hazard ratio 0.8 (95% CI 0.6 to 1.0).') for i in (1, 2)}
    outcome = _build_outcome(spec, 'efficacy', included, records, ['synthetic'], ['placebo'],
                             strand_rule=declaration)
    assert outcome['result']['k'] == 1
    assert [r['id'] for r in outcome['trials']] == ['PMID 1']
    assert len(outcome['strand_candidates']) == 2


def test_typed_report_metadata_render_is_key_order_independent():
    from harness.page import typed_effects_html
    row = effect_type.build_effect(dict(id='fixture', scale='HR', source='fixture',
                                        provenance='fulltext_verified', document_sha256='fixture-digest'))
    outcome = {'effect_types': [row]}
    assert typed_effects_html(outcome) == typed_effects_html(json.loads(json.dumps(outcome, sort_keys=True)))
