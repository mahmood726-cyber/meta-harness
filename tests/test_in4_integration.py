"""Integration contracts: source quotations are distinct from pooled assertions."""
import json
from pathlib import Path
from harness import page, census, claim

ROOT = Path(__file__).resolve().parents[1]

def test_trial_quote_is_visible_but_not_a_pooled_significance_assertion(monkeypatch):
    review = json.loads((ROOT/'docs/reviews/colchicine-postop-af/review.json').read_text(encoding='utf-8'))
    outcome = next(o for o in review['outcomes'] if o.get('primary'))
    assert outcome['result']['claim'] == claim.derive(outcome['result'])
    assert outcome['result']['k'] == len(outcome['trials'])
    assert outcome['strict_contract_sensitivity']['k'] < outcome['result']['k']
    assert 'significantly lower' in page._outcome_block(outcome)
    assert not census._claim_check(review)['contradictions']
    original = page.render_outcome_block
    monkeypatch.setattr(page, 'render_outcome_block', lambda o: original(o) + '<p>The pooled result significantly lower.</p>')
    assert census._claim_check(review)['contradictions']

def test_legacy_strand_identifier_preserves_source_refusal():
    from harness import envelope
    review = {'slug': 'fixture', 'outcomes': [], 'strands': {'strands': [
        {'id': 'legacy', 'members': [{'id': 'fixture', 'scale': 'HR',
         'effect': .8, 'ci_low': .7, 'ci_high': .9}]}]}}
    spec = envelope.build(review)['specifications'][-1]
    assert spec['spec_id'] == 'all-candidates-legacy'
    assert not spec['computable']

def test_typed_retractions_preserve_explicit_historical_boundaries():
    from harness import integration_prose, manuscript
    assert 'is retracted' in integration_prose.limit('integrity')
    assert 'historical checked set' in integration_prose.limit('integrity')
    assert 'RETRACTED' in manuscript.compute('availability', {'slug': 'fixture'})


def test_legacy_strand_effect_gate_refuses_untyped_members_without_crashing():
    from harness.effect_type import check_review
    review = {'outcomes': [{'primary': True, 'result': {'k': 0}}],
              'strands': {'strands': [{'id': 'legacy', 'pool': {'k': 1},
                                      'members': [{'id': 'untyped'}]}]}}
    assert any('EFFECT_TYPE_REFUSED legacy' in e for e in check_review(review))


def test_grade_audit_retains_suppression_rationale_without_leaking_pool():
    from scripts.grade_arithmetic_sweep import public_grade
    original = {'domains': {'inconsistency': {'i2': 69., 'basis': 'incompatible'}}}
    result = public_grade(original, True)
    assert original['domains']['inconsistency']['i2'] == 69.
    assert 'i2' not in result['domains']['inconsistency']
    assert result['domains']['inconsistency']['suppressed_fields'] == ['i2']
    assert result['domains']['inconsistency']['basis'] == 'incompatible'
