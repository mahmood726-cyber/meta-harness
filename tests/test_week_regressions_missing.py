"""Hostile-audit counterexamples, with owner patches kept unapplied."""
import importlib.util
from pathlib import Path
import pytest
from harness import harms, known_missing, comparator_second_pass, screen, reason_audit, design_key

ROOT = Path(__file__).resolve().parents[1]


from test_week_regressions_audit import load_pin, estimator_requirement

def test_missing_candidates_merge_family_and_report_identity():
    review = {'screening': {'records': [{'id': 'PLANT · report-a', 'trial_family_id': 'PLANT', 'decision': 'include'}]},
              'outcomes': [{'primary': True, 'declared_absent_trials': [{'id': 'report-a'}]}]}
    rows = known_missing._missing_candidates(review, {'known_eligible_missing': [{'trial': 'PLANT'}]})
    assert len(rows) == 1, 'one family must not be counted twice'


