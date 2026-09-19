"""Source digests bind physical bytes, including line endings."""
import hashlib
import json
import subprocess
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]


def verify_bytes(path, digest, text_attribute):
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, str(path) + ': byte digest differs'
    assert text_attribute == 'unset', str(path) + ': held bytes require -text'


def source_pairs(value):
    if isinstance(value, dict):
        for key, digest in value.items():
            if key == 'sha256':
                path = value.get('path') or value.get('local_path')
            elif key.endswith('_sha256'):
                stem = key[:-7]
                path = value.get(stem) or value.get(stem + '_path')
            else:
                continue
            if isinstance(path, str) and path.startswith('outputs/handover/') and isinstance(digest, str):
                yield path, digest
        for child in value.values():
            yield from source_pairs(child)
    elif isinstance(value, list):
        for child in value:
            yield from source_pairs(child)


def test_crlf_plant_fires_on_lf_digest(tmp_path):
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    attributes = tmp_path / '.gitattributes'
    attributes.write_text('* text=auto eol=lf' + chr(10), encoding='utf-8')
    path = tmp_path / 'held.txt'
    path.write_bytes(b'held' + bytes([13, 10]))
    def attr():
        return subprocess.check_output(['git', '-C', str(tmp_path), 'check-attr', 'text', '--', path.name], text=True).strip().rsplit(': ', 1)[-1]
    digest = hashlib.sha256(b'held' + bytes([10])).hexdigest()
    with pytest.raises(AssertionError, match='digest differs'):
        verify_bytes(path, digest, attr())
    with pytest.raises(AssertionError, match='require -text'):
        verify_bytes(path, hashlib.sha256(path.read_bytes()).hexdigest(), attr())
    attributes.write_text('* -text' + chr(10), encoding='utf-8')
    verify_bytes(path, hashlib.sha256(path.read_bytes()).hexdigest(), attr())


def test_every_held_provenance_digest_and_git_attribute():
    pairs = set()
    for record in (ROOT / 'outputs/handover').rglob('*.json'):
        pairs.update(source_pairs(json.loads(record.read_text(encoding='utf-8'))))
    assert pairs, 'no provenance records discovered'
    errors = []
    for rel, digest in sorted(pairs):
        attr = subprocess.check_output(['git', 'check-attr', 'text', '--', rel], cwd=ROOT, text=True).strip().rsplit(': ', 1)[-1]
        try:
            verify_bytes(ROOT / rel, digest, attr)
        except (AssertionError, OSError) as exc:
            errors.append(str(exc))
    assert not errors, '\n'.join(errors)
