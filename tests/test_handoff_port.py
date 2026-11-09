"""Offline contracts for the handoff port; no repository or engine execution."""
import hashlib
import json
from pathlib import Path

import pytest

from harness.exchange_v01 import validate_manifest
from harness.exchange_v01 import wire

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / 'benchmarks/cross_repo/v0.1'


def test_registered_raw_manifest_guard_is_not_run_and_uses_original_fixture():
    manifest = json.loads((BENCHMARK / 'manifest.json').read_bytes())
    assert {c['id'] for c in manifest['cases']} == {
        f'CROSS-EXCH-{i:03d}' for i in range(1, 16)
    }
    case = next(c for c in manifest['cases'] if c['id'] == 'CROSS-EXCH-015')
    assert case['status'] == 'NOT_RUN'
    assert case['input_sha256'] == manifest['cases'][0]['input_sha256']
    assert case['input_sha256'] == hashlib.sha256((BENCHMARK / case['input']).read_bytes()).hexdigest()
    assert all(c['status'] == 'NOT_RUN' for c in manifest['cases'])
    validate_manifest(manifest, BENCHMARK)


def test_manifest_requires_fifteenth_case_even_if_last_case_is_removed():
    manifest = json.loads((BENCHMARK / 'manifest.json').read_bytes())
    manifest['cases'] = [c for c in manifest['cases'] if c['id'] != 'CROSS-EXCH-015']
    with pytest.raises(ValueError, match='missing required IDs:.*CROSS-EXCH-015'):
        validate_manifest(manifest, BENCHMARK)


def test_schema_keeps_closed_shapes_and_requires_fifteen_cases():
    schema = json.loads((BENCHMARK / 'manifest.schema.json').read_bytes())
    assert schema['properties']['cases']['minItems'] == 15
    assert schema['additionalProperties'] is False
    assert schema['$defs']['case']['additionalProperties'] is False
    assert schema['$defs']['repository']['additionalProperties'] is False
    assert schema['properties']['coverage']['items']['additionalProperties'] is False


def test_importer_uses_the_existing_wire_decoder_once(monkeypatch):
    from test_exchange_v01_wire import _exchange
    original = wire._decode
    calls = []

    def record(raw, label):
        calls.append((raw, label))
        return original(raw, label)

    monkeypatch.setattr(wire, '_decode', record)
    raw = json.dumps(_exchange()).encode('utf-8')
    imported = wire.import_exchange_json(raw, ROOT)
    assert imported == _exchange()
    assert calls == [(raw, 'exchange')]
    assert wire.validate_exchange_json(raw, ROOT) is None
    assert calls == [(raw, 'exchange'), (raw, 'exchange')]


@pytest.mark.parametrize('raw', [b'\xff', b'\xef\xbb\xbf{}', b'{"x": NaN}',
                                b'{"x": Infinity}', b'{"x": 1, "x": 2}', {}, '\ud800'])
def test_importer_retains_stricter_main_raw_boundary(raw):
    with pytest.raises(ValueError):
        wire.import_exchange_json(raw, ROOT)


@pytest.mark.parametrize('argv', [[], ['--archive-root', '.'],
    ['manifest.json', '--exchange', 'wire.json', '--archive-root', '.']])
def test_cli_rejects_ambiguous_or_incomplete_modes(argv):
    with pytest.raises(SystemExit) as exc:
        wire.main(argv)
    assert exc.value.code == 2


def test_package_importer_delegates_to_wire(monkeypatch):
    import harness.exchange_v01 as package
    expected = {'validated': True}
    calls = []

    def imported(raw, root):
        calls.append((raw, root))
        return expected

    monkeypatch.setattr(wire, 'import_exchange_json', imported)
    assert package.import_exchange_json(b'raw', ROOT) is expected
    assert calls == [(b'raw', ROOT)]


@pytest.mark.parametrize('filename,case_id,source_key', [
    ('frozen-cli-api-016.json', 'CROSS-EXCH-016', 'frozen_source'),
    ('frozen-handoff-017.json', 'CROSS-EXCH-017', 'synthetic_source'),
    ('frozen-estimand-018.json', 'CROSS-EXCH-018', 'frozen_source'),
])
def test_frozen_registrations_remain_unexecuted_with_intact_source(filename, case_id, source_key):
    spec = json.loads((BENCHMARK / filename).read_bytes())
    assert spec['case_id'] == case_id
    assert spec['registered_status'] == 'NOT_RUN'
    assert spec['input_type'] == 'SYNTHETIC_FIXTURE_ONLY'
    source = spec[source_key]
    assert hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest() == source['sha256']
    assert spec['repositories']['e156']['role'] == 'NOT_EXECUTED'
    assert spec['repositories']['e156-ecosystem-starter']['role'] == 'NOT_EXECUTED'


def test_candidate_produces_registered_frozen_wires_without_engine_execution():
    import importlib.util

    def load(name):
        spec = importlib.util.spec_from_file_location(name, BENCHMARK / (name + '.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    canary = load('pinned_pairwise_canary')
    runner = load('frozen_cli_api_handoff_016')
    registration = json.loads((BENCHMARK / 'frozen-cli-api-016.json').read_bytes())
    cases = runner.make_cases(canary)
    assert set(cases) == set(registration['scenarios'])
    for label, expected in {**registration['allowed_input_sha256'],
                            **registration['negative_input_sha256']}.items():
        assert hashlib.sha256(cases[label]).hexdigest() == expected, label
