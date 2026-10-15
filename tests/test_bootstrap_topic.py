"""Bootstrap plants: real cached pipeline, isolated publication outputs."""
import importlib
import json
from pathlib import Path
import sys
import types

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
import build_topic_recorded as recorded
from harness.gate import gate_page

SLUG = 'glp1-ra-mace-t2d'


def test_gate_refuses_bootstrap_before_missing_publication_files(tmp_path):
    (tmp_path / 'review.json').write_text(json.dumps({'status': 'DRAFT_BOOTSTRAP'}))
    ok, reasons = gate_page(str(tmp_path))
    assert not ok
    assert 'DRAFT_BOOTSTRAP is never servable' in reasons


def isolate(monkeypatch, tmp_path):
    (tmp_path / 'topics').mkdir()
    (tmp_path / 'topics' / f'{SLUG}.json').write_bytes((ROOT / 'topics' / f'{SLUG}.json').read_bytes())
    monkeypatch.setattr(recorded, 'ROOT', str(tmp_path))
    monkeypatch.setattr(recorded.build_topic, 'ROOT', str(tmp_path))
    monkeypatch.setattr(recorded.build_topic, 'write_index', lambda *a: None)
    # Execution metadata is outside review.json; avoid unrelated tree enumeration.
    stub = lambda *a: {'tree': {'generating_commit': 'TEST', 'tree_state': 'UNKNOWN'}, 'release': {'release_sha256': None}}
    monkeypatch.setattr(recorded.build_topic, 'write_execution_record', stub)
    monkeypatch.setattr(recorded, 'write_execution_record', stub)


def test_draft_full_pipeline_no_publication_files(tmp_path, monkeypatch):
    isolate(monkeypatch, tmp_path)
    recorded.main([SLUG, '--now', '2026-10-15', '--bootstrap-draft'])
    review = json.loads((tmp_path / 'docs/reviews' / SLUG / 'review.json').read_text(encoding='utf-8'))
    assert review['status'] == 'DRAFT_BOOTSTRAP'
    assert next(o for o in review['outcomes'] if o.get('primary'))['trials']
    assert review['screening']
    assert 'reproduction' not in review
    for name in ('CERTIFICATE.json', 'manifest.json', 'index.html', 'EXECUTION_RECORD.json'):
        assert not list(tmp_path.rglob(name)), name


def test_unregistered_protocol_refused_before_any_step(tmp_path, monkeypatch):
    bootstrap = importlib.import_module('bootstrap_topic')
    monkeypatch.setattr(bootstrap, 'ROOT', tmp_path)
    monkeypatch.setattr(bootstrap, 'run_step', lambda *a, **kw: pytest.fail('producer ran before registration'))
    assert bootstrap.main(['unregistered-topic', '--now', '2026-10-15']) != 0


def test_normal_review_byte_identical_to_prechange_generator(tmp_path, monkeypatch):
    isolate(monkeypatch, tmp_path)
    baseline = types.ModuleType('prechange_build_topic')
    baseline.__file__ = str(ROOT / 'scripts/build_topic.py')
    exec(compile((ROOT / '.codex_logs/boot_build_topic_before.py').read_bytes(), baseline.__file__, 'exec'), baseline.__dict__)
    baseline.ROOT = str(tmp_path)
    baseline.write_index = recorded.build_topic.write_index
    baseline.write_execution_record = recorded.build_topic.write_execution_record
    baseline.main(SLUG, '2026-10-15')
    path = tmp_path / 'docs/reviews' / SLUG / 'review.json'
    before = path.read_bytes()
    recorded.main([SLUG, '--now', '2026-10-15'])
    assert path.read_bytes() == before

@pytest.mark.parametrize('failure', ['comparators', 'acquisition', 'draft', 'rob2', 'build', 'replay', 'census', 'gate'])
def test_bootstrap_stops_at_first_failure(tmp_path, monkeypatch, failure):
    bootstrap = importlib.import_module('bootstrap_topic')
    monkeypatch.setattr(bootstrap, 'ROOT', tmp_path)
    monkeypatch.setattr(bootstrap.subprocess, 'run', lambda *a, **kw: types.SimpleNamespace(returncode=0))
    calls = []
    def step(name, command, log):
        calls.append((name, command))
        return 9 if name == failure else 0
    monkeypatch.setattr(bootstrap, 'run_step', step)
    assert bootstrap.main(['registered-topic', '--now', '2026-10-15']) == 9
    expected = ['comparators', 'acquisition', 'draft', 'rob2', 'build', 'replay', 'census', 'gate']
    assert [name for name, _ in calls] == expected[:expected.index(failure) + 1]
    if any(name == 'rob2' for name, _ in calls):
        assert '--write' in next(command for name, command in calls if name == 'rob2')


def test_execution_record_does_not_claim_clean_when_scan_disabled(monkeypatch):
    import execution_record
    monkeypatch.setenv('CAPTAIN_NO_WORKTREE_SCAN', '1')
    def git(*args):
        assert args[0] != 'status'
        return 'test-head' if args[-1] == 'HEAD' else 'test-branch'
    monkeypatch.setattr(execution_record, '_git', git)
    state = execution_record.git_state()
    assert state['tree_state'] == 'UNKNOWN_NOT_INSPECTED'
    assert state['dirty_paths'] is None
