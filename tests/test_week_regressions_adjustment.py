"""Hostile-audit counterexamples, with owner patches kept unapplied."""
import importlib.util
from pathlib import Path
import pytest
from harness import harms, known_missing, comparator_second_pass, screen, reason_audit, design_key

ROOT = Path(__file__).resolve().parents[1]


from test_week_regressions_audit import load_pin, estimator_requirement

def test_adjustment_labels_require_estimator_evidence():
    estimator_requirement(design_key)


def test_adjustment_plant_fires_on_pinned_parent():
    with pytest.raises(AssertionError):
        estimator_requirement(load_pin('adjustment/design_key.py'))


