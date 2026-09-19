"""Hostile-audit counterexamples, with owner patches kept unapplied."""
import importlib.util
from pathlib import Path
import pytest
from harness import harms, known_missing, comparator_second_pass, screen, reason_audit, design_key

ROOT = Path(__file__).resolve().parents[1]


from test_week_regressions_audit import load_pin, estimator_requirement

def test_kidney_and_cv_death_values_do_not_prove_mace_value():
    sources = [{'source_id': 'synthetic-plant', 'text': 'Results were similar for a composite of the kidney-specific components of the primary outcome (hazard ratio, 0.79; 95% CI, 0.66 to 0.94) and for death from cardiovascular causes (hazard ratio, 0.71; 95% CI, 0.56 to 0.89).'}]
    assert reason_audit.find_value_in_sources(sources, ['major adverse cardiovascular events', 'death from cardiovascular causes'], 'Major adverse cardiovascular events') is None


