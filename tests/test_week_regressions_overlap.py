"""Hostile-audit counterexamples, with owner patches kept unapplied."""
import importlib.util
from pathlib import Path
import pytest
from harness import harms, known_missing, comparator_second_pass, screen, reason_audit, design_key

ROOT = Path(__file__).resolve().parents[1]


from test_week_regressions_audit import load_pin, estimator_requirement

def test_comparator_only_text_cannot_establish_current_pool_overlap():
    profile = comparator_second_pass.PROFILES['glp1-ra-mace-t2d']['trial_set']
    text = profile['source_term'] + ' ' + ' '.join(t['aliases'][0] for t in profile['trials'])
    result = comparator_second_pass.parse_trial_set('glp1-ra-mace-t2d', text)
    assert result['k'] == len(profile['trials'])
    assert result.get('shared_k') is None, 'current pool is not an input to this parser'
    from unittest.mock import patch
    analysis = {key: {} for key in ('quantity_match', 'comparator_recency', 'treatment_strategy_match', 'outcome_match', 'scope_override')}
    analysis['comparator_trial_set'] = result
    with patch.object(comparator_second_pass, 'analyze', return_value=analysis), patch.object(comparator_second_pass, 'comparator_text', return_value=text):
        updated = comparator_second_pass.apply('plant', {}, {}, {}, {'overlap': {'shared_k': 999, 'shared_trials': ['stale-plant']}})
    assert updated['overlap']['shared_k'] != 999
    assert not updated['overlap'].get('shared_trials')


