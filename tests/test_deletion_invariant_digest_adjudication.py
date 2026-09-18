"""Real-input deletion plants through the production builder and certificate verifier."""
import copy
import hashlib
import json
import shutil
import socket
import subprocess
from pathlib import Path

import pytest

from harness import census, certificate, gate, pipeline, registration, verified_inputs
from harness.synth import method_text

ROOT = Path(__file__).resolve().parents[1]
TOPICS = ('glp1-ra-mace-t2d', 'colchicine-recurrent-pericarditis')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    empty = ROOT / '.tmp/empty_aact'
    empty.mkdir(parents=True, exist_ok=True)
    assert not list(empty.iterdir())
    monkeypatch.setenv('AACT_DIR', str(empty))
    def denied(*args, **kwargs):
        raise AssertionError('DEL2 forbids network')
    monkeypatch.setattr(socket.socket, 'connect', denied)
    monkeypatch.setattr(socket, 'create_connection', denied)


def core(slug):
    return pipeline.build_review_core(slug, read(ROOT / 'topics' / (slug + '.json')),
        read(ROOT / 'cache' / slug / 'records.json'), registration.protocol_sha(slug))


def publish(slug, review, directory):
    primary = next(o for o in review['outcomes'] if o.get('primary'))
    declared = review.get('method_declared', pipeline.METHOD)
    scale = primary.get('result', {}).get('scale')
    meta = dict(slug=slug, declared_method=declared,
                served_method=method_text(scale) if scale else declared,
                generator='harness', build_utc='2026-09-11',
                comparator={k: review['comparator'][k] for k in
                    ('name', 'year', 'journal', 'pmid', 'doi', 'url', 'open_access', 'overlap')})
    return census.build_review_dir(copy.deepcopy(review), meta, str(directory),
        registration.protocol_sha(slug), from_cache=True, certify=True)


def snapshot(directory):
    review = read(directory / 'review.json')
    state = dict(gate=gate.gate_page(str(directory))[1], grade=review.get('grade'),
                 k=[o.get('result', {}).get('k') for o in review['outcomes']],
                 certificate=certificate.verify(directory))
    # Keep the complete compared objects, not just a claim that they were inspected.
    with (directory / 'DEL2_STATES.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(state, ensure_ascii=False, sort_keys=True) + '\n')
    return state


def isolate(slug, directory, cert):
    shutil.copytree(ROOT / 'cache' / slug, directory / 'cache' / slug)
    refs = [*certificate.CODE, 'topics/' + slug + '.json',
            cert['hash_inputs']['protocol_text_sha256'].split(' UTF-8')[0],
            *[d['ref'] for d in cert['held_documents']]]
    for ref in refs:
        if ref == 'harness/effect_type.py' and not (ROOT / ref).exists():
            assert cert['analysis_code_blobs'][ref] == certificate.NOT_PRESENT
            continue
        dest = directory / ref
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / ref, dest)


def entries(slug, name):
    return [(pid, i, e) for pid, value in read(ROOT / 'cache' / slug / name).items()
            for i, e in enumerate(value if isinstance(value, list) else [value])]


@pytest.mark.parametrize('slug', TOPICS)
@pytest.mark.parametrize('kind', ['extracted_counts', 'typed_refusal'])
def test_deleted_input_digest(slug, kind, tmp_path, monkeypatch):
    name = 'verified_arms.json' if kind == 'extracted_counts' else 'verified_effects.json'
    pid, index, entry = next(x for x in entries(slug, name)
                             if x[2].get('kind') == kind and x[2].get('document_sha256'))
    before_core = core(slug)
    candidates = [t for o in before_core['outcomes'] for t in
                  o.get('trials' if kind == 'extracted_counts' else 'declared_absent_trials', [])]
    assert any(t.get('document_sha256') == entry['document_sha256']
               and t['id'] == 'PMID ' + pid for t in candidates)
    baseline = tmp_path / 'baseline'
    publish(slug, before_core, baseline)
    before = snapshot(baseline)
    isolate(slug, tmp_path, read(baseline / 'CERTIFICATE.json'))
    path = tmp_path / 'cache' / slug / name
    data = read(path)
    row = data[pid][index] if isinstance(data[pid], list) else data[pid]
    del row['document_sha256']
    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    original = verified_inputs.load
    monkeypatch.setattr(verified_inputs, 'load',
                        lambda s, cache_root=None: original(s, tmp_path / 'cache'))
    monkeypatch.setattr(certificate, 'ROOT', tmp_path)
    expected = 'MISSING_DOCUMENT_SHA256: ' + f'cache/{slug}/{name}/{pid}/{entry["outcome"]}'
    after_dir = tmp_path / 'after'
    try:
        publish(slug, core(slug), after_dir)
    except ValueError as exc:
        print(f'{slug}/{kind}: REFUSED: {exc}')
        assert str(exc) == expected
        # No replacement publication/certificate exists: no stronger verdict can ship.
        assert not (after_dir / 'CERTIFICATE.json').exists()
        assert not (after_dir / 'index.html').exists()
        return
    after = snapshot(after_dir)
    print(f'{slug}/{kind}: SURVIVED; k={after["k"]}; grade_equal={after["grade"] == before["grade"]}; '
          f'gate_equal={after["gate"] == before["gate"]}; certificate={after["certificate"]}')
    assert set(before['gate']) <= set(after['gate'])
    assert before['grade'] == after['grade'] and before['k'] == after['k']
    assert after['certificate'] or before['certificate'] == after['certificate']
    pytest.fail('FIRED: deleted document_sha256 still builds and certifies')


@pytest.mark.parametrize('slug,source', [(TOPICS[0], 'records.json'),
                                       (TOPICS[1], 'records.json'),
                                       (TOPICS[0], 'ft_27295427.txt')])
@pytest.mark.parametrize('mutation', ['delete', 'corrupt'])
def test_held_document(slug, source, mutation, tmp_path, monkeypatch):
    baseline = tmp_path / 'baseline'
    publish(slug, core(slug), baseline)
    cert = read(baseline / 'CERTIFICATE.json')
    isolate(slug, tmp_path, cert)
    monkeypatch.setattr(certificate, 'ROOT', tmp_path)
    before = snapshot(baseline)
    assert before['certificate'] == []
    # A digest actually cited by an input; not an arbitrary supplementary file.
    entry = next(e for _, _, e in entries(slug, 'verified_arms.json')
                 if e.get('document_sha256') and source in e.get('document_ref', ''))
    ref = entry['document_ref'].split('#')[0]
    held = tmp_path / ref
    assert hashlib.sha256(held.read_bytes()).hexdigest() == entry['document_sha256']
    if mutation == 'delete':
        held.unlink()
    else:
        raw = held.read_bytes()
        # Change a single whitespace byte, preserving valid JSON when this is records.json.
        offset = raw.index(b' ')
        held.write_bytes(raw[:offset] + b'\t' + raw[offset + 1:])
    after = snapshot(baseline)
    print(f'{slug}/{source}/{mutation}: {after["certificate"]}')
    assert after['certificate']
    assert set(before['gate']) <= set(after['gate'])
    assert before['grade'] == after['grade'] and before['k'] == after['k']
    reason = 'HELD_DOCUMENT_MISSING: ' if mutation == 'delete' else 'DOCUMENT_SHA256_MISMATCH: '
    assert after['certificate'] == [
        'CERTIFICATE.json release_sha256 could not be verified: ' + reason + ref]


def test_adjudication_inventory():
    reviews = sorted((ROOT / 'docs/reviews').glob('*/review.json'))
    cache = sorted((ROOT / 'cache').rglob('*.json'))
    review_hits = [p for p in reviews if 'ADJ-' in p.read_text(encoding='utf-8')]
    cache_hits = [p for p in cache if 'ADJ-' in p.read_text(encoding='utf-8')]
    handover = ROOT / 'outputs/handover/glp1_reviewerB/ADJUDICATIONS.json'
    assert 'ADJ-' in handover.read_text(encoding='utf-8')
    print(f'ADJ citations: {len(review_hits)} of {len(reviews)} reviews; '
          f'{len(cache_hits)} of {len(cache)} cache JSON files; handover records present')
    assert not review_hits and not cache_hits, 'New real citations require deletion/alteration plants'
    # Sparse checkout omits historical snapshots; inspect their committed bytes as well.
    tracked = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', 'cache'], text=True).splitlines()
    tracked_json = [p for p in tracked if p.endswith('.json')]
    scan = subprocess.run(['git', '-C', str(ROOT), 'grep', '-n', 'ADJ-', 'HEAD', '--',
                           'cache', 'docs/reviews/*/review.json'], capture_output=True, text=True)
    assert scan.returncode == 1 and not scan.stdout, scan.stdout + scan.stderr
    print(f'HEAD scan: 0 of {len(reviews)} reviews; 0 of {len(tracked_json)} tracked cache JSON files')
    pytest.skip('NOT_CONSTRUCTIBLE: no committed review/cache row cites an ADJ- record')
