"""The manuscript must not assess publication bias without a computed object."""
import importlib.util
from pathlib import Path
import pytest
from harness import manuscript


def requirement(module):
    review = {'slug': 'plant', 'outcomes': [{'primary': True, 'name': 'plant outcome', 'result': {'present': False}}], 'grade': {'certainty': 'low', 'downgrades': 2}}
    html = module.render(review)
    assert 'publication bias assessed from the trial registry' not in html


def test_missing_publication_bias_object_cannot_be_claimed_assessed():
    requirement(manuscript)


def test_publication_bias_plant_fires_on_pinned_parent():
    path = Path(__file__).resolve().parents[1] / 'tests/fixtures/week_regressions/prefix/publication/manuscript.py'
    spec = importlib.util.spec_from_file_location('harness._rg_old_manuscript', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with pytest.raises(AssertionError):
        requirement(module)
