"""Hostile-audit counterexamples, with owner patches kept unapplied."""
import importlib.util
from pathlib import Path
import pytest
from harness import harms, known_missing, comparator_second_pass, screen, reason_audit, design_key

ROOT = Path(__file__).resolve().parents[1]


def load_pin(rel):
    path = ROOT / 'tests/fixtures/week_regressions/prefix' / rel
    spec = importlib.util.spec_from_file_location('harness._rg_pin_' + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def estimator_requirement(module):
    for source in ('No adjustments for multiplicity were performed.', 'A hazard ratio was reported.'):
        trial = {'id': 'plant', 'derivation': 'reported', 'scale': 'HR', 'source': source}
        result = module.key_for_trial(trial)
        assert result['estimator_source'] not in {'PUBLISHED_ADJUSTED', 'PUBLISHED_UNADJUSTED'}


