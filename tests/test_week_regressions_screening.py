"""Hostile-audit counterexamples, with owner patches kept unapplied."""
import importlib.util
from pathlib import Path
import pytest
from harness import harms, known_missing, comparator_second_pass, screen, reason_audit, design_key

ROOT = Path(__file__).resolve().parents[1]


from test_week_regressions_audit import load_pin, estimator_requirement

def test_title_omission_requires_review_not_ineligibility():
    record = {'id': 'plant', 'id_type': 'pmid', 'title': 'Cardiovascular outcomes',
              'abstract': 'Adults with diabetes were randomly assigned to liraglutide or placebo in a double-blind trial.',
              'pubtypes': ['Randomized Controlled Trial'], 'conditions': [], 'interventions': []}
    inc = {'population_any': ['diabetes'], 'intervention_any': ['liraglutide'], 'intervention_in_title': True}
    result = screen.screen_record(record, inc, set())
    assert result[0] != 'exclude', result


