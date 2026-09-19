"""A served generation date must be bound to a build input, or withdrawn."""
import hashlib
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]


def validate_stamp(document, root):
    if 'generated_on' not in document:
        return
    binding = document.get('generation_input')
    assert isinstance(binding, dict), 'generated_on lacks a build-input binding'
    path = root / binding['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == binding['sha256']
    source = json.loads(path.read_text(encoding='utf-8'))
    assert document['generated_on'] == source[binding['date_field']]


def test_inventory_stamp_has_build_input_provenance():
    validate_stamp(json.loads((ROOT / 'docs/model_stage_inventory.json').read_text(encoding='utf-8')), ROOT)


def test_generation_stamp_plant_and_bound_input(tmp_path):
    source = tmp_path / 'build.json'
    source.write_text(json.dumps({'build_date': '2031-02-03'}), encoding='utf-8')
    plant = {'generated_on': '2031-02-03'}
    with pytest.raises(AssertionError, match='binding'):
        validate_stamp(plant, tmp_path)
    plant['generation_input'] = {'path': source.name, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'date_field': 'build_date'}
    validate_stamp(plant, tmp_path)
    plant['generated_on'] = '2031-02-04'
    with pytest.raises(AssertionError):
        validate_stamp(plant, tmp_path)


def test_withdrawn_stamp_patch_holds():
    validate_stamp(json.loads((ROOT / 'tests/fixtures/week_regressions/prefix/patched/docs/model_stage_inventory.json').read_text(encoding='utf-8')), ROOT)
