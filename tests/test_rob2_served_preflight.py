from contextlib import contextmanager
from copy import deepcopy
import json
import os
from pathlib import Path

import pytest
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = (str(ROOT), str(ROOT / 'scripts'))
import rob2_served_preflight as pf
# Deliberately import before session configuration, as test_rob2_dev_switch does.
import rob2_fulltext_acquire as acquire
import rob2_dual as rd
from robgrade import prompt_licence


# Audited scripts/rob2_{dual,served,fulltext_acquire}.py, robgrade/*.py,
# and harness/aact*.py: these are the lazy module caches; aact has none.
CACHE_GLOBALS = ((rd, '_AACT_REF'), (rd, '_AACT_DESIGNS'),
                 (rd, '_REG_TEXT'), (rd, '_DEV'), (prompt_licence, '_TRACKED'))
INPUT_ENV_NAMES = ('AACT_DIR', 'ROBGRADE_LOCAL_FT', 'ROBGRADE_DEV_OPEN_CC',
                   'ROBGRADE_FT_STORE', 'ROBGRADE_SEED_UPW')


def snapshot_caches():
    return tuple((module, name, getattr(module, name), deepcopy(getattr(module, name)))
                 for module, name in CACHE_GLOBALS)


def assert_caches_restored(caches):
    for module, name, original, contents in caches:
        assert getattr(module, name) is original, f'{module.__name__}.{name} identity leaked'
        assert getattr(module, name) == contents, f'{module.__name__}.{name} contents leaked'


@contextmanager
def isolated_caches():
    # Preserve identity as well as contents, including already-warm caches.
    # Fresh caches prevent a previous consumer's snapshot from affecting this one.
    before = snapshot_caches()
    try:
        with pytest.MonkeyPatch.context() as patch:
            for module, name, _, _ in before:
                patch.setattr(module, name, {} if name == '_AACT_DESIGNS' else None)
            yield
    finally:
        assert_caches_restored(before)


@pytest.fixture
def consumer_caches():
    with isolated_caches():
        yield


@pytest.fixture(scope='session')
def collected_store_paths():
    return set()


@pytest.fixture(scope='session')
def original_input_state():
    return (
        tuple((name, os.environ.get(name)) for name in
              INPUT_ENV_NAMES),
        tuple((name, getattr(acquire, name)) for name in
              ('STORE', 'UPW_CACHE', 'UPW_INDEX', 'ACQ_UPW', 'store_path')),
        snapshot_caches(),
    )


@pytest.fixture(scope='session')
def input_settings(tmp_path_factory, original_input_state):
    # Configure before collection: absent AACT_DIR must never discover a local
    # workstation snapshot via the adapter's fallback search.
    snapshot = os.environ.get('AACT_DIR')
    if not snapshot:
        snapshot = tmp_path_factory.mktemp('source-snapshot')
        for table in ('study_references', 'designs', 'brief_summaries', 'detailed_descriptions'):
            (snapshot / (table + '.txt')).write_text('nct_id\n', encoding='utf-8')
    store = tmp_path_factory.mktemp('empty-ft')
    return str(snapshot), store


def patch_input_settings(patch, settings, collected_store_paths):
    snapshot, store = settings
    for name, value in (('AACT_DIR', snapshot), ('ROBGRADE_LOCAL_FT', '1'),
                        ('ROBGRADE_DEV_OPEN_CC', '1'), ('ROBGRADE_FT_STORE', str(store))):
        patch.setenv(name, value)
    # Another test may have imported acquire before this environment existed.
    for name, path in (('STORE', store), ('UPW_CACHE', store / '_upw'),
                       ('UPW_INDEX', store / '_upw_index.json')):
        patch.setattr(acquire, name, str(path))
    original_store_path = acquire.store_path
    def observed_store_path(pmid):
        path = original_store_path(pmid)
        collected_store_paths.add(Path(path).parent)
        return path
    patch.setattr(acquire, 'store_path', observed_store_path)


@pytest.fixture(scope='session')
def inputs(input_settings, collected_store_paths):
    with isolated_caches(), pytest.MonkeyPatch.context() as patch:
        patch_input_settings(patch, input_settings, collected_store_paths)
        sv = pf.load_driver()
        with pf.never_writes():
            pairs, todo, covered, items = pf.collect_items(sv)
    # Restore session collection patches before any test consumes these inputs.
    yield sv, pairs, todo, covered, items


@pytest.fixture
def configured_inputs(inputs, input_settings, collected_store_paths, monkeypatch):
    with isolated_caches():
        patch_input_settings(monkeypatch, input_settings, collected_store_paths)
        yield inputs



def test_preimported_acquire_uses_temporary_store(configured_inputs, collected_store_paths):
    store = Path(os.environ['ROBGRADE_FT_STORE'])
    assert collected_store_paths == {store}
    assert Path(acquire.STORE) == store
    assert Path(acquire.UPW_CACHE) == store / '_upw'
    assert Path(acquire.UPW_INDEX) == store / '_upw_index.json'
    assert tuple(store.iterdir()) == ()


@pytest.fixture
def private(configured_inputs, tmp_path):
    sv, pairs, todo, covered, items = configured_inputs
    stores = {}
    # All served stores start empty; never inspect or copy workstation stores.
    for key, value in sv.STORES.items():
        dst = tmp_path / key / Path(value).name
        if key in ('quarantine', 'dual_runs', 'ctx_runs'):
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text('{}', encoding='utf-8')
        else:
            dst.mkdir(parents=True)
        stores[key] = str(dst)
    return sv, pairs, todo, covered, items, stores


def report(private):
    sv, pairs, todo, covered, items, stores = private
    with pf.never_writes():
        return pf.analyze(sv, pairs, todo, covered, items, stores)


def plant(private, stale=False):
    sv, _, todo, _, items, stores = private
    before = report(private)
    row = next(r for r in before['rows'] if r['codex']['state'] == 'CALL')
    item = next(i for i in items if i['key'] == row['key'])
    runs = pf.read_json(stores['dual_runs'])
    # Synthetic NI-only reply: no held response or manifest is a fixture input.
    # Record construction/validation uses the driver's own offline helpers;
    # the manifest has the same shape returned by rob2_dual._call.
    prompt = sv.rd.prompt_bytes(item) + (b'\nSTALE TEST PROMPT' if stale else b'')
    response = {'answers': tuple({'qid': q, 'answer': 'NI', 'quote': '',
                                 'source_id': '', 'rationale': 'Synthetic test fixture.'}
                                for q in sv.rd.QIDS), 'notes': 'Synthetic test fixture.'}
    rec = sv.rd.ms.build_record(
        prompt_bytes=prompt, response_bytes=json.dumps(response).encode('utf-8'),
        model={'id_requested': 'fixture', 'id_reported': 'fixture', 'provider': 'fixture'},
        params={}, not_controllable=list(), client={'name': 'offline fixture'},
        request_utc='2000-01-01T00:00:00Z', response_utc='2000-01-01T00:00:00Z',
        caller={'file': 'scripts/rob2_dual.py', 'line': 'call:codex',
                'purpose': 'Synthetic preflight regression fixture'},
        input_digests=sv.rd.digests(item), owner_lines=())
    assert not sv.rd.ms.record_problems(rec)
    sv.rd.ms.write_record(rec, stores['dual_rec'])
    runs.setdefault(item['key'], {})['codex'] = {
        'record_id': rec['record_id'], 'state': rec['state'], 'error': rec.get('error'),
        'prompt_sha256': sv._sha(prompt), 'model': rec['model']['id_reported']}
    Path(stores['dual_runs']).write_text(json.dumps(runs), encoding='utf-8')
    return before, item['key']


def test_counts_come_from_temp_store_copy(private):
    before, key = plant(private)
    after = report(private)
    assert after['totals']['codex']['REUSE'] == before['totals']['codex']['REUSE'] + 1
    assert after['totals']['codex']['CALL'] == before['totals']['codex']['CALL'] - 1


def test_stale_record_is_not_reuse(private):
    before, key = plant(private, stale=True)
    after = report(private)
    row = next(r for r in after['rows'] if r['key'] == key)
    assert row['codex']['state'] == 'STALE'
    assert after['status'] == 'WOULD_REFUSE'
    assert any(r['key'] == key and 'unaccounted' in r['reason'] for r in after['would_refuse'])
    assert after['will_recall']['codex'] == 1


def test_preflight_never_writes_store_or_calls_model(private, monkeypatch, tmp_path):
    sv = private[0]
    attempted = []
    def forbidden(*a, **k):
        attempted.append((a, k))
        raise AssertionError('store write or model execution attempted')
    for obj, name in ((sv.rd, '_save'), (sv.rd.ms, 'write_record'), (sv.rd, '_call'),
                      (sv, 'run_dual'), (sv, 'run_ctx'), (sv, 'adopt_stage')):
        monkeypatch.setattr(obj, name, forbidden)
    before = {p: p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    result = report(private)
    assert before == {p: p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    assert result['rows']
    assert not attempted
    # Guard rejects the write before open() can create or truncate anything.
    with pf.never_writes(), pytest.raises(PermissionError, match='preflight'):
        open(ROOT / 'PREFLIGHT_MUST_NOT_WRITE', 'w')


@pytest.mark.parametrize('relative', ('docs/preflight.json', 'evidence/model_calls/preflight.json',
                                     'outputs/preflight.json', 'registry/preflight.json'))
def test_output_rejects_repository_paths(relative):
    with pytest.raises(ValueError, match='--out'):
        pf.output_path(ROOT / relative)


def test_guard_blocks_temp_writes_and_processes_but_restores_fixture_access(tmp_path):
    target = tmp_path / 'blocked'
    with pf.never_writes():
        with pytest.raises(PermissionError, match='preflight'):
            target.write_text('forbidden', encoding='utf-8')
        with pytest.raises(PermissionError, match='preflight'):
            sys.audit('subprocess.Popen', 'unused', (), None, None)
        with pytest.raises(PermissionError, match='preflight'):
            sys.audit('socket.connect', None, None)
    assert not target.exists()
    target.write_text('fixture access restored', encoding='utf-8')


def test_output_accepts_external_temp_and_rejects_source_store(tmp_path, monkeypatch):
    monkeypatch.setenv('ROBGRADE_FT_STORE', str(tmp_path / 'source'))
    assert pf.output_path(tmp_path / 'report.json') == (tmp_path / 'report.json').resolve()
    with pytest.raises(ValueError, match='--out'):
        pf.output_path(tmp_path / 'source' / 'report.json')


def test_cli_writes_only_requested_report_and_prints_portable_command(tmp_path, monkeypatch, capsys):
    result = {'totals': {}, 'adjudicator_max_trials': 0, 'preconditions': [],
              'live_command': 'python scripts/rob2_served.py --run',
              'environment_guidance': 'AACT_DIR: pinned source configuration'}
    monkeypatch.setattr(pf, 'load_driver', lambda: object())
    monkeypatch.setattr(pf, 'collect_items', lambda sv: ())
    monkeypatch.setattr(pf, 'analyze', lambda *a: result)
    target = tmp_path / 'chosen' / 'preflight.json'
    assert pf.main(('--out', str(target))) == 0
    assert json.loads(target.read_text(encoding='utf-8')) == result
    assert tuple(p for p in tmp_path.rglob('*') if p.is_file()) == (target,)
    output = capsys.readouterr().out
    assert 'python scripts/rob2_served.py --run' in output
    assert 'AACT_DIR: pinned source configuration' in output


@pytest.fixture
def r1_case(consumer_caches, monkeypatch, tmp_path):
    from types import SimpleNamespace
    from reproducible_ai import record_licence
    from harness import aact
    sv = pf.load_driver()
    pairs = {str(n): [str(i) for i in range(91 if n == 0 else 0)] for n in range(32)}
    items = [{'key': str(i), 'sources': [], 'outcome': 'outcome'} for i in range(65)]
    runs = {i['key']: {w: {'record_id': w, 'state': 'RAN_OK', 'prompt_sha256': sv._sha(b'prompt')}
                           for w in ('codex', 'agy', 'adjudicator')} for i in items}
    snapshot = tmp_path / 'source-snapshot'
    snapshot.mkdir()
    monkeypatch.setenv('AACT_DIR', str(snapshot))
    monkeypatch.setenv('ROBGRADE_FT_STORE', str(tmp_path / 'ft'))
    for name in ('ROBGRADE_LOCAL_FT', 'ROBGRADE_DEV_OPEN_CC'):
        monkeypatch.setenv(name, '1')
    monkeypatch.setattr(aact, '_table', lambda t: t)
    monkeypatch.setattr(pf, 'read_json', lambda p: runs)
    monkeypatch.setattr(pf, 'outside_driver', lambda s: {'nct_only': [0]*5, 'non_primary_only': [0]*11})
    monkeypatch.setattr(sv, 'served_keys', lambda p: {i['key'] for i in items})
    for name in ('adopt_orphans', 'check_manifest_records', 'check_accounted', 'audit'):
        monkeypatch.setattr(sv, name, lambda *a, **k: None)
    monkeypatch.setattr(sv, '_record_state', lambda d, r: 'RAN_OK' if r else None)
    monkeypatch.setattr(sv, '_record_role', lambda d, r: r)
    monkeypatch.setattr(sv, '_record_prompt_sha256', lambda d, r: sv._sha(b'prompt'))
    monkeypatch.setattr(sv.rd, 'evidence_block', lambda i: [])
    monkeypatch.setattr(sv.rd, 'prompt_bytes', lambda *a: b'prompt')
    monkeypatch.setattr(sv.rd, 'digests', lambda i: {})
    monkeypatch.setattr(sv.rd, 'open_sources', lambda i: [{'kind': 'abstract'}])
    monkeypatch.setattr(sv.rd, 'replay', lambda e: e)
    monkeypatch.setattr(sv.rd, 'verify_answers', lambda r, i: {})
    monkeypatch.setattr(sv.rt, 'typed_answers', lambda *a, **k: ({}, {}))
    monkeypatch.setattr(record_licence, 'record_problems', lambda *a, **k: [])
    return sv, pairs, pairs, {}, items, runs


def r1_report(case):
    return pf.analyze(*case[:5])


def r1_cli(monkeypatch, result, target):
    monkeypatch.setattr(pf, 'load_driver', lambda: None)
    monkeypatch.setattr(pf, 'collect_items', lambda sv: ())
    monkeypatch.setattr(pf, 'analyze', lambda *a: result)
    return pf.main(('--out', str(target)))


def test_r1_atomic_hardlink(r1_case, monkeypatch, tmp_path):
    import os
    result = r1_report(r1_case)
    sentinel = tmp_path / 'repo' / 'sentinel'
    sentinel.parent.mkdir()
    sentinel.write_bytes(b'untouched sentinel')
    monkeypatch.setattr(pf, 'ROOT', sentinel.parent)
    link = tmp_path / 'report.json'
    os.link(sentinel, link)
    monkeypatch.delenv('AACT_DIR')
    r1_cli(monkeypatch, result, link)
    assert sentinel.read_bytes() == b'untouched sentinel'
    assert json.loads(link.read_text()) == json.loads(json.dumps(result))


@pytest.mark.parametrize('check', ('check_manifest_records', 'check_accounted', 'audit', 'reader_verdict'))
def test_r1_refusal_invalidates_every_slot(r1_case, monkeypatch, check):
    def refuse(*a, **k):
        raise SystemExit('REFUSED: planted integrity failure')
    monkeypatch.setattr(r1_case[0], check, refuse)
    result = r1_report(r1_case)
    assert all(r[w]['state'] == 'UNVERIFIED' for r in result['rows'] for w in r1_case[0].ROLES)
    assert result['status'] == 'REFUSED'
    assert all(t['REUSE'] == 0 for t in result['totals'].values())


@pytest.mark.parametrize('state,held', (('CONFLICT', True), ('NOT_NEEDED', False),
    ('UNKNOWN', True), ('UNKNOWN', False), ('REUSE', True), ('STALE', True), ('CALL', False)))
def test_r1_adjudicator_states(r1_case, monkeypatch, state, held):
    sv, *_, runs = r1_case
    if not held:
        for row in runs.values():
            row.pop('adjudicator')
    if state == 'UNKNOWN':
        for row in runs.values():
            row.pop('agy')
    if state in ('REUSE', 'STALE', 'CALL'):
        q = sv.rd.QIDS[0]
        monkeypatch.setattr(sv.rd, 'verify_answers', lambda r, i: {q: {'answer': 'Y' if r['record_id'] == 'codex' else 'N'}})
    if state == 'STALE':
        for row in runs.values():
            row['adjudicator']['prompt_sha256'] = 'old'
    result = r1_report(r1_case)
    assert {r['adjudicator']['state'] for r in result['rows']} == {state}
    if state == 'CONFLICT':
        assert result['status'] == 'WOULD_REFUSE'
        assert {r['key'] for r in result['would_refuse']} == set(runs)


def test_r1_cli_contract(r1_case, monkeypatch):
    monkeypatch.setattr(r1_case[0], 'FLAGS', ('--dual-only',))
    result = r1_report(r1_case)
    assert next(c for c in result['preconditions'] if c['check'] == 'CLI flags')['status'] == 'REFUSED'
    assert result['status'] == 'REFUSED'


def test_r1_refused_record_writes_json(r1_case, monkeypatch, tmp_path):
    sv = r1_case[0]
    path = tmp_path / 'mc-corrupt.json'
    path.write_text('broken')
    def refuse(*a, **k):
        raise SystemExit(f'REFUSED: unreadable record {path}: invalid JSON')
    monkeypatch.setattr(sv, '_record_state', refuse)
    monkeypatch.setattr(pf, 'collect_items', lambda s: r1_case[1:5])
    target = tmp_path / (tmp_path.name + '-report.json')
    assert pf.main(('--out', str(target))) != 0
    result = json.loads(target.read_text())
    assert result['status'] == 'REFUSED'
    assert str(path) in result['reason']
    assert 'invalid JSON' in json.dumps(result)
    assert all(t['REUSE'] == 0 for t in result['totals'].values())


def test_r1_snapshot_and_stale_warning(r1_case, monkeypatch, tmp_path, capsys):
    for row in r1_case[-1].values():
        row['codex']['prompt_sha256'] = 'old'
    result = r1_report(r1_case)
    assert result['aact_snapshot'] == 'source-snapshot'
    assert result['ft_store_root'] == str((tmp_path / 'ft').resolve())
    r1_cli(monkeypatch, result, tmp_path / (tmp_path.name + '-warning.json'))
    output = capsys.readouterr().err
    assert 'WARNING' in output and 'STALE' in output and 'source-snapshot' in output
    assert 'different AACT snapshot' in output and 'changes prompts' in output


def test_r1_real_cli_and_planted_refusal(private, monkeypatch, tmp_path):
    sv, pairs, todo, covered, items, stores = private
    _, key = plant(private)
    monkeypatch.setattr(sv, 'STORES', stores)
    monkeypatch.setattr(pf, 'collect_items', lambda driver: (pairs, todo, covered, items))
    target = tmp_path / 'baseline.json'
    assert pf.main(('--out', str(target))) == 0
    baseline = json.loads(target.read_text(encoding='utf-8'))
    assert baseline['status'] == 'PASS'
    assert next(r for r in baseline['rows'] if r['key'] == key)['codex']['state'] == 'REUSE'
    corrupt = Path(stores['dual_rec']) / 'mc-planted-corrupt.json'
    corrupt.write_text('not JSON', encoding='utf-8')
    target = tmp_path / 'refused.json'
    assert pf.main(('--out', str(target))) != 0
    refused = json.loads(target.read_text(encoding='utf-8'))
    assert refused['status'] == 'REFUSED'
    assert str(corrupt) in refused['reason']
    assert all(t['REUSE'] == 0 and t['UNVERIFIED'] == len(baseline['rows']) for t in refused['totals'].values())


def test_r1_audit_findings_refuse(r1_case, monkeypatch):
    monkeypatch.setattr(r1_case[0], 'audit', lambda d: [('mc-conflict', ['D1'])])
    result = r1_report(r1_case)
    assert result['status'] == 'REFUSED'
    assert all(t['REUSE'] == 0 for t in result['totals'].values())


def test_r1_stops_before_classification(r1_case, monkeypatch):
    def refuse(*a, **k):
        raise SystemExit('REFUSED: manifest')
    monkeypatch.setattr(r1_case[0], 'check_manifest_records', refuse)
    def forbidden(*a, **k):
        pytest.fail('classification continued after refusal')
    monkeypatch.setattr(pf, 'classify', forbidden)
    assert r1_report(r1_case)['status'] == 'REFUSED'


@pytest.mark.parametrize('mode', ('gate_refusal', 'no_open_sources'))
def test_r2_blocked_trial_has_no_reuse_or_call(r1_case, monkeypatch, mode):
    sv = r1_case[0]
    # Isolate the source gate: agreeing readers must not retain an adjudication.
    for held in r1_case[-1].values():
        held.pop('adjudicator')
    key = r1_case[4][-1]['key']
    original = sv.rd.evidence_block
    if mode == 'gate_refusal':
        def evidence(item):
            if item['key'] == key:
                raise sv.rd.D8Refused('source is not CC')
            return original(item)
        monkeypatch.setattr(sv.rd, 'evidence_block', evidence)
    else:
        monkeypatch.setattr(sv.rd, 'open_sources', lambda i: [] if i['key'] == key else [{'kind': 'abstract'}])
    original_verdict = sv.reader_verdict
    def verdict(item, *args):
        assert item['key'] != key, 'blocked trial must not be read'
        return original_verdict(item, *args)
    monkeypatch.setattr(sv, 'reader_verdict', verdict)
    result = r1_report(r1_case)
    assert result['status'] == 'PASS'
    row = next(r for r in result['rows'] if r['key'] == key)
    assert row['d8'] == 'blocked'
    assert next(r for r in result['d8_per_trial'] if r['key'] == key)['gate'] == 'blocked'
    assert all(row[w]['state'] == 'BLOCKED' for w in pf.ROLES)
    assert all(result['totals'][w]['BLOCKED'] == 1 for w in pf.ROLES)


@pytest.mark.parametrize('mode', ('violation', 'licence_d8_exception', 'evidence_exception'))
def test_r2_licence_failure_refuses_and_writes_report(r1_case, monkeypatch, tmp_path, mode):
    from reproducible_ai import record_licence
    sv = r1_case[0]
    calls = []
    def failure(*args, **kwargs):
        calls.append(None)
        if len(calls) < 2:
            return []
        if mode == 'violation':
            return ['planted D8 violation']
        if mode == 'licence_d8_exception':
            raise sv.rd.D8Refused('planted licence machinery exception')
        raise RuntimeError('planted evidence machinery exception')
    monkeypatch.setattr(sv.rd if mode == 'evidence_exception' else record_licence,
                        'evidence_block' if mode == 'evidence_exception' else 'record_problems', failure)
    monkeypatch.setattr(pf, 'collect_items', lambda s: r1_case[1:5])
    target = tmp_path / (tmp_path.name + '-refused.json')
    assert pf.main(('--out', str(target))) != 0
    result = json.loads(target.read_text(encoding='utf-8'))
    assert result['status'] == 'REFUSED'
    assert len(result['rows']) == len(r1_case[4])
    assert all(r[w]['state'] == 'UNVERIFIED' for r in result['rows'] for w in pf.ROLES)
    assert all(t['REUSE'] == 0 for t in result['totals'].values())


@pytest.mark.parametrize('marker', ('file', 'directory'))
def test_r2_output_rejects_any_git_worktree(tmp_path, marker):
    tree = tmp_path / 'unrelated-worktree'
    tree.mkdir()
    git = tree / '.git'
    if marker == 'file':
        git.write_text('gitdir: elsewhere', encoding='utf-8')
    else:
        git.mkdir()
    with pytest.raises(ValueError, match='--out'):
        pf.output_path(tree / 'not-yet-created' / 'nested' / 'report.json')
    assert pf.output_path(tmp_path / 'plain' / 'report.json') == (tmp_path / 'plain' / 'report.json').resolve()


@pytest.mark.parametrize('mode', ('violation', 'exception'))
def test_r2_held_record_d8_failure_refuses(r1_case, monkeypatch, tmp_path, mode):
    from reproducible_ai import record_licence
    sv = r1_case[0]
    monkeypatch.setattr(sv, '_read_record', lambda p: {'record_id': 'held-test-record'})
    def validate(*args, **kwargs):
        sv._read_record('held-test-record.json')
    monkeypatch.setattr(sv, 'check_manifest_records', validate)
    def problems(record, **kwargs):
        if record.get('record_id') != 'held-test-record':
            return []
        if mode == 'exception':
            raise sv.rd.D8Refused('held licence exception')
        return ['held D8 violation']
    monkeypatch.setattr(record_licence, 'record_problems', problems)
    monkeypatch.setattr(pf, 'collect_items', lambda s: r1_case[1:5])
    target = tmp_path / (tmp_path.name + '-held-refused.json')
    assert pf.main(('--out', str(target))) != 0
    result = json.loads(target.read_text(encoding='utf-8'))
    assert result['status'] == 'REFUSED'
    assert len(result['rows']) == len(r1_case[4])
    assert all(r[w]['state'] == 'UNVERIFIED' for r in result['rows'] for w in pf.ROLES)
    assert all(t['REUSE'] == 0 for t in result['totals'].values())


def test_r3_early_refusal_totals_not_computed(monkeypatch, tmp_path, capsys):
    def refuse():
        raise ValueError('before items load')
    monkeypatch.setattr(pf, 'load_driver', refuse)
    monkeypatch.delenv('ROBGRADE_FT_STORE', raising=False)
    target = tmp_path / 'early.json'
    assert pf.main(('--out', str(target))) == 1
    result = json.loads(target.read_text())
    assert result['totals'] is None
    assert result['totals_note'] == 'not computed'
    assert result['ft_store_root'] == 'unset (ROBGRADE_FT_STORE not set)'
    assert 'not computed' in capsys.readouterr().out


def test_r3_failed_stale_reader_will_recall(r1_case, monkeypatch):
    sv, *_, runs = r1_case
    for row in runs.values():
        row.pop('adjudicator')
        row['codex'].update(state='RAN_ERROR', prompt_sha256='old')
    monkeypatch.setattr(sv, '_record_state', lambda d, r: 'RAN_ERROR' if r == 'codex' else 'RAN_OK')
    result = r1_report(r1_case)
    assert result['status'] == 'PASS'
    assert result['will_recall']['codex'] == 65
    assert all(r['codex']['state'] == 'STALE' for r in result['rows'])


def test_unreadable_successful_reader_predicts_quarantine(private):
    sv, _, _, _, items, stores = private
    _, key = plant(private)
    item = next(it for it in items if it['key'] == key)
    runs = pf.read_json(stores['dual_runs'])
    entry = runs[key]['codex']
    old = Path(stores['dual_rec'], entry['record_id'] + '.json')
    record = pf.read_json(old)
    record['response'] = sv.rd.ms._blob(b'Unreadable reply regression fixture')
    record['record_id'] = sv.rd.ms.record_id_of(record)
    assert not sv.rd.ms.record_problems(record)
    Path(stores['dual_rec'], record['record_id'] + '.json').write_text(json.dumps(record), encoding='utf-8')
    old.unlink()
    entry['record_id'] = record['record_id']
    Path(stores['dual_runs']).write_text(json.dumps(runs), encoding='utf-8')
    with pf.stores_context(sv, stores):
        assert sv.rd.replay(entry) is None
        assert sv.reader_verdict(item, runs[key], sv.rd.REC_DIR) == 'unreadable reply: codex'
    result = report(private)
    row = next(r for r in result['rows'] if r['key'] == key)
    assert row['codex']['state'] == 'QUARANTINE'
    assert row['adjudicator']['state'] == 'SKIPPED (trial quarantined)'
    assert result['status'] == 'PASS'
    assert any(q['key'] == key and q['reason'] == 'unreadable reply: codex'
               for q in result['quarantined_trials'])


@pytest.mark.parametrize('missing', ('absent', 'null'))
def test_current_success_without_record_id_refuses(private, missing):
    sv, _, _, _, items, stores = private
    _, key = plant(private)
    runs = pf.read_json(stores['dual_runs'])
    entry = runs[key]['codex']
    Path(stores['dual_rec'], entry.pop('record_id') + '.json').unlink()
    if missing == 'null':
        entry['record_id'] = None
    item = next(it for it in items if it['key'] == key)
    assert entry['state'] == 'RAN_OK'
    assert entry['prompt_sha256'] == sv._sha(sv.rd.prompt_bytes(item))
    with pf.stores_context(sv, stores):
        assert not sv.adopt_orphans((item,), runs, sv.rd.REC_DIR)
        with pytest.raises((KeyError, TypeError)):
            sv.rd.replay(entry)
    Path(stores['dual_runs']).write_text(json.dumps(runs), encoding='utf-8')
    result = report(private)
    assert result['status'] == 'WOULD_REFUSE'
    row = next(r for r in result['rows'] if r['key'] == key)
    assert row['codex']['state'] == 'WOULD_REFUSE'
    assert any(r['key'] == key and r['reason'] == 'malformed RAN_OK manifest entry (missing record_id/prompt_sha256)'
               for r in result['would_refuse'])


def test_success_without_record_id_and_prompt_hash_refuses(private):
    sv, _, _, _, items, stores = private
    _, key = plant(private)
    runs = pf.read_json(stores['dual_runs'])
    entry = runs[key]['codex']
    Path(stores['dual_rec'], entry.pop('record_id') + '.json').unlink()
    entry.pop('prompt_sha256')
    assert entry['state'] == 'RAN_OK'
    item = next(it for it in items if it['key'] == key)
    with pf.stores_context(sv, stores):
        assert not sv.adopt_orphans((item,), runs, sv.rd.REC_DIR)
    Path(stores['dual_runs']).write_text(json.dumps(runs), encoding='utf-8')
    result = report(private)
    assert result['status'] == 'WOULD_REFUSE'
    row = next(r for r in result['rows'] if r['key'] == key)
    assert row['codex']['state'] == 'WOULD_REFUSE'
    assert any(r['key'] == key and r['reason'] ==
               'malformed RAN_OK manifest entry (missing record_id/prompt_sha256)'
               for r in result['would_refuse'])


@pytest.mark.parametrize('raises', (False, True))
def test_cache_isolation_preserves_warm_objects(monkeypatch, raises):
    for module, name in CACHE_GLOBALS:
        monkeypatch.setattr(module, name, {'fixture-cache': {'nested': ('original',)}})
    before = snapshot_caches()

    def consume():
        with isolated_caches():
            for module, name in CACHE_GLOBALS:
                assert getattr(module, name) == ({} if name == '_AACT_DESIGNS' else None)
                if getattr(module, name) is None:
                    setattr(module, name, {})
                getattr(module, name)['consumer-cache'] = {'nested': ('changed',)}
            if raises:
                raise RuntimeError('fixture consumer failure')

    if raises:
        with pytest.raises(RuntimeError, match='fixture consumer failure'):
            consume()
    else:
        consume()
    assert_caches_restored(before)


@pytest.mark.parametrize('part', ('environment', 'acquire', 'caches'))
def test_input_patches_restored_before_session_teardown(inputs, original_input_state, part):
    # Keep this after the consumers: session teardown must not be needed to
    # restore state for the next test module in the same pytest invocation.
    environment, attributes, caches = original_input_state
    if part == 'environment':
        assert tuple((name, os.environ.get(name)) for name, _ in environment) == environment
    elif part == 'acquire':
        assert tuple((name, getattr(acquire, name)) for name, _ in attributes) == attributes
    else:
        assert_caches_restored(caches)
