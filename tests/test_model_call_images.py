"""Image-input contract: fake client only, with process/network tripwires."""
import hashlib
import socket
import subprocess
from pathlib import Path

import pytest

from reproducible_ai import model_call_live as live, model_source as ms


def fake_runner(*args, **kwargs):
    assert kwargs['images'][0].is_absolute()
    return {'rc': 0, 'stdout': b'', 'stderr': b'--------\nmodel: fixture\nprovider: fixture\nreasoning effort: low\n--------',
            'last_message': b'{"rows":[]}', 'argv': ['fixture']}


def call(tmp_path, runner=fake_runner):
    return live.call(b'image proposal', schema={'type': 'object'}, model='fixture', effort='low',
                     caller={'file': __file__, 'line': 'call', 'purpose': 'fixture'}, input_digests=[],
                     runner=runner, client_version='fixture', images=('figure.jpg',), image_root=tmp_path)


def test_image_is_digest_only_changed_byte_changes_record_id(tmp_path, monkeypatch):
    monkeypatch.setattr(live, '_utc', lambda: '2026-09-30T00:00:00Z')
    path = tmp_path / 'figure.jpg'
    path.write_bytes(b'synthetic-image-A')
    first = call(tmp_path)
    image = first['input_digests'][0]
    assert image == {'ref': 'figure.jpg', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                     'media_type': 'image/jpeg', 'what': 'held image input; bytes not copied'}
    path.write_bytes(b'synthetic-image-B')
    second = call(tmp_path)
    assert first['record_id'] != second['record_id']
    assert first['response'] == second['response']


def test_replay_needs_neither_image_nor_process_nor_network(tmp_path, monkeypatch):
    path = tmp_path / 'figure.jpg'
    path.write_bytes(b'synthetic')
    rec = call(tmp_path)
    path.unlink()
    def trip(*a, **k):
        raise AssertionError('offline replay reached a process/network')
    for obj, name in [(subprocess, 'run'), (subprocess, 'Popen'), (socket, 'socket'), (socket, 'create_connection')]:
        monkeypatch.setattr(obj, name, trip)
    assert ms.replay(rec) == b'{"rows":[]}'


def test_image_mutation_during_call_refused(tmp_path):
    path = tmp_path / 'figure.jpg'
    path.write_bytes(b'first')
    def mutate(*args, **kwargs):
        path.write_bytes(b'second')
        return fake_runner(*args, **kwargs)
    with pytest.raises(ms.RecordIncomplete, match='IMAGE_CHANGED_DURING_CALL'):
        call(tmp_path, mutate)


def test_missing_or_outside_image_refused(tmp_path):
    with pytest.raises(ms.RecordIncomplete, match='IMAGE_MISSING'):
        call(tmp_path)
    with pytest.raises(ms.RecordIncomplete, match='IMAGE_OUTSIDE'):
        live.image_inputs([tmp_path.parent / 'outside.jpg'], tmp_path)


def test_codex_argv_attaches_image_and_redacts_absolute_path(tmp_path, monkeypatch):
    image = tmp_path / 'figure.jpg'
    image.write_bytes(b'synthetic')
    monkeypatch.setattr(live, '_codex_exe', lambda: 'fixture-codex')
    monkeypatch.setenv('MODEL_CALL_WORKDIR', str(tmp_path))
    def run(argv, **kwargs):
        assert argv[argv.index('-i') + 1] == str(image)
        assert argv[-1] == '-'
        assert kwargs['input'] == b'prompt'
        Path(argv[argv.index('--output-last-message') + 1]).write_bytes(b'{}')
        class Result:
            returncode, stdout, stderr = 0, b'', b''
        return Result()
    monkeypatch.setattr(subprocess, 'run', run)
    result = live.codex_runner(b'prompt', {}, 'fixture', 'low', 1, images=(image,))
    assert '<image:0>' in result['argv']
    assert str(image) not in result['argv']


def test_text_only_runner_contract_unchanged():
    def text_runner(prompt, schema, model, effort, timeout):
        return {'rc': 0, 'stderr': b'--------\nmodel: fixture\nprovider: fixture\n--------', 'last_message': b'{}'}
    rec = live.call(b'text', schema={}, model='fixture', effort='low', caller={'file': __file__, 'line': 1, 'purpose': 'fixture'},
                    input_digests=[], runner=text_runner, client_version='fixture')
    assert ms.replay(rec) == b'{}'
