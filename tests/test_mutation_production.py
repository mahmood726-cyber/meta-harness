"""Production mutation contracts on committed records (DEL boundary harness reused).

All edited data and generated publications live below .tmp/mut; no acquisition.
"""
import copy
import json
import os
import socket
import shutil
from pathlib import Path

import pytest

from harness import census, pipeline, registration, gate, claimgraph, claim
from harness.synth import method_text

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / '.tmp' / 'mut' / os.environ.get('MU_TEST_RUN', 'production')
assert SCRATCH.resolve().is_relative_to((ROOT / '.tmp' / 'mut').resolve())
TOPICS = ('glp1-ra-mace-t2d', 'colchicine-postop-af')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def core(slug, records=None):
    return pipeline.build_review_core(slug, read(ROOT / 'topics' / (slug + '.json')),
        records if records is not None else read(ROOT / 'cache' / slug / 'records.json'),
        registration.protocol_sha(slug))


def primary(review):
    return next(o for o in review['outcomes'] if o.get('primary'))


def publish(slug, review, directory):
    """Same production boundary/metadata as DEL and scripts/build_topic.py."""
    directory = directory / slug  # production gate resolves comparator cache by leaf slug
    assert directory.resolve().is_relative_to(SCRATCH.resolve())
    if directory.exists():
        shutil.rmtree(directory)
    declared = review.get('method_declared', pipeline.METHOD)
    scale = primary(review).get('result', {}).get('scale')
    meta = dict(slug=slug, declared_method=declared,
                served_method=method_text(scale) if scale else declared,
                generator='harness', build_utc='2026-09-11',
                comparator={k: review['comparator'][k] for k in
                    ('name', 'year', 'journal', 'pmid', 'doi', 'url', 'open_access', 'overlap')})
    census.build_review_dir(copy.deepcopy(review), meta, str(directory),
        registration.protocol_sha(slug), from_cache=True, certify=True)
    ok, reasons = gate.gate_page(str(directory))
    return {'gate_ok': ok, 'gate_reasons': reasons,
            'review': read(directory / 'review.json'),
            'manifest': read(directory / 'manifest.json'),
            'certificate': read(directory / 'CERTIFICATE.json')}


@pytest.fixture(scope='module')
def baselines():
    empty = SCRATCH / 'empty_aact'
    empty.mkdir(parents=True, exist_ok=True)
    assert not list(empty.iterdir())
    previous = os.environ.get('AACT_DIR')
    os.environ['AACT_DIR'] = str(empty)
    result = {}
    for slug in TOPICS:
        review = core(slug)
        write(SCRATCH / slug / 'core.json', review)
        result[slug] = (review, publish(slug, review, SCRATCH / slug / 'baseline'))
    yield result
    if previous is None:
        os.environ.pop('AACT_DIR', None)
    else:
        os.environ['AACT_DIR'] = previous


def observe(name, slug, review):
    try:
        result = publish(slug, review, SCRATCH / slug / name)
    except ValueError as exc:
        result = {'refusal': str(exc)}
    write(SCRATCH / 'observations' / (name + '.json'), result)
    return result


def emit(name, data):
    write(SCRATCH / 'observations' / (name + '-summary.json'), data)
    print(name + ' ' + json.dumps(data, sort_keys=True, ensure_ascii=True))


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError('mutation contracts prohibit network acquisition')
    monkeypatch.setattr(socket.socket, 'connect', refuse)
    monkeypatch.setattr(socket, 'create_connection', refuse)


def test_baseline(baselines):
    for slug, (review, built) in baselines.items():
        print(slug, 'k=', primary(review)['result'].get('k'),
              'gate=', built['gate_ok'], built['gate_reasons'])
        assert built['manifest']['review_sha256']
        assert built['gate_ok'], built['gate_reasons']


@pytest.mark.parametrize('slug', TOPICS)
def test_duplicate(baselines, slug):
    original, before = baselines[slug]
    records = read(ROOT / 'cache' / slug / 'records.json')
    pooled = {t['id'].removeprefix('PMID ') for t in primary(original)['trials']}
    record = next(r for r in records['records'] if r['id'] in pooled and r.get('nct'))
    duplicate = copy.deepcopy(record)
    duplicate['id'] = '99999998'  # synthetic publication identity, never a real source
    records['records'].append(duplicate)
    write(SCRATCH / slug / 'duplicate-input' / 'records.json', records)
    changed = core(slug, read(SCRATCH / slug / 'duplicate-input' / 'records.json'))
    result = observe('duplicate-' + slug, slug, changed)
    def counts(r):
        rows = r['screening']['records']
        return {'k': primary(r)['result']['k'], 'screening': len(rows),
                'families': len({x['trial_family_id'] for x in rows})}
    data = {'before': counts(original), 'after': counts(changed),
            'source_id': record['id'], 'nct': record['nct'],
            'refusal': result.get('refusal'), 'gate_reasons': result.get('gate_reasons')}
    emit('duplicate-' + slug, data)
    assert counts(original) == counts(changed), data
    assert '99999998' not in {t['id'].removeprefix('PMID ') for t in primary(changed)['trials']}
    assert result.get('gate_ok'), data


def test_component_endpoint(baselines, monkeypatch):
    slug = TOPICS[0]
    original, before = baselines[slug]
    records = read(ROOT / 'cache' / slug / 'records.json')
    row = next(t for t in primary(original)['trials'] if t['id'] == 'PMID 27633186')
    record = next(r for r in records['records'] if r['id'] == '27633186')
    sentence = row['endpoint_result_span']
    assert sentence in record['abstract']
    edited = sentence.replace('The primary outcome', 'Cardiovascular death', 1)
    assert edited != sentence
    record['abstract'] = record['abstract'].replace(sentence, edited, 1)
    write(SCRATCH / slug / 'component-input' / 'records.json', records)
    # Observe the genuine production admission calls, preserving their return values.
    from harness import target_endpoint
    admission = target_endpoint.admissibility
    receipts = []
    def track(spec, trial):
        verdict = admission(spec, trial)
        if verdict.get('verdict') == 'RESULT_INCOMPATIBLE':
            receipts.append(verdict)
        return verdict
    monkeypatch.setattr(target_endpoint, 'admissibility', track)
    changed = core(slug, read(SCRATCH / slug / 'component-input' / 'records.json'))
    result = observe('component', slug, changed)
    absent = [t for t in primary(changed).get('declared_absent_trials', []) if t['id'] == row['id']]
    data = {'before_k': primary(original)['result']['k'], 'after_k': primary(changed)['result']['k'],
            'admission': receipts, 'absent': absent, 'refusal': result.get('refusal'),
            'gate_reasons': result.get('gate_reasons')}
    emit('component', data)
    assert row['id'] not in {t['id'] for t in primary(changed)['trials']}, data
    assert any(r['verdict'] == 'RESULT_INCOMPATIBLE' for r in receipts), data
    assert result.get('gate_ok') or result.get('refusal'), data


def test_analysis_set(baselines):
    slug = TOPICS[0]
    changed = copy.deepcopy(baselines[slug][0])
    row = next(t for t in primary(changed)['trials'] if t['id'] == 'PMID 31189511')
    axis = row['compat_dimensions']['analysis_set']
    assert axis['source'] == 'committed source text'
    assert 'intention-to-treat' in axis['span']
    axis['span'] = axis['span'].replace('intention-to-treat', 'per-protocol')
    axis['value'] = row['analysis_set'] = 'per-protocol'
    result = observe('analysis', slug, changed)
    data = {'declared': primary(changed)['population'], 'changed_axis': axis,
            'refusal': result.get('refusal'), 'gate_reasons': result.get('gate_reasons')}
    emit('analysis', data)
    assert (result.get('refusal') and 'ANALYSIS_SET' in result['refusal']) or any(
        'ANALYSIS_SET' in r for r in result.get('gate_reasons', [])), data


@pytest.mark.parametrize('field', ('endpoint_definition_span', 'source'))
def test_required_support(baselines, field):
    slug = TOPICS[0]
    changed = copy.deepcopy(baselines[slug][0])
    row = next(t for t in primary(changed)['trials'] if t.get('endpoint_definition_span'))
    assert row.pop(field)
    result = observe('missing-' + field, slug, changed)
    expected = 'MISSING_ENDPOINT_SUPPORT: ' + field + ': ' + row['id']
    data = {'expected': expected, 'refusal': result.get('refusal'),
            'gate_reasons': result.get('gate_reasons')}
    emit('missing-' + field, data)
    assert result.get('refusal') == expected or any(expected in r for r in result.get('gate_reasons', [])), data


def test_checker_crash(baselines, monkeypatch):
    slug = TOPICS[1]
    calls = []
    def crash(*args, **kwargs):
        calls.append(True)
        raise RuntimeError('SYNTHETIC MU significance checker crash')
    monkeypatch.setattr(claim, 'significance_contradictions', crash)
    try:
        result = observe('checker', slug, baselines[slug][0])
    except RuntimeError as exc:
        assert str(exc) == 'SYNTHETIC MU significance checker crash'
        result = {'refusal': 'RuntimeError: ' + str(exc)}
    emit('checker', {'calls': len(calls), 'refusal': result.get('refusal')})
    assert calls and result.get('refusal')
    assert not (SCRATCH / slug / 'checker' / slug / 'CERTIFICATE.json').exists()


@pytest.mark.xfail(strict=True, reason='READY-BEHIND-ELX: .tmp/patches/source-dependants.diff')
def test_source_dependants(baselines):
    slug = TOPICS[0]
    original, before = baselines[slug]
    changed = copy.deepcopy(original)
    row = primary(changed)['trials'][0]
    from decimal import Decimal
    old = Decimal(str(row['ci_high']))
    row['ci_high'] = float(old + Decimal(1).scaleb(old.as_tuple().exponent))
    result = observe('dependants', slug, changed)
    after = result.get('review', changed)
    def identities(review):
        out = primary(review)
        return {
            'source.input_set_version': claimgraph.input_set_version(out),
            'pool.input_set_version': out['result']['input_set_version'],
            'pool.claim_id': out['result']['claim_id'],
            'pool.result': {k: out['result'].get(k) for k in ('estimate', 'ci_low', 'ci_high')},
            'grade.input_set_version': review['grade']['input_set_version'],
            'grade.imprecision': review['grade']['domains']['imprecision'],
            'claim_objects': review['claimgraph']['objects'],
        }
    a, b = identities(original), identities(after)
    status = {k: 'CHANGED' if a[k] != b[k] else 'UNCHANGED' for k in a}
    for label, section, field in [('certificate.release_sha256', 'certificate', 'release_sha256'),
                                  ('manifest.review_sha256', 'manifest', 'review_sha256')]:
        status[label] = ('NOT_ISSUED' if section not in result else
                         'CHANGED' if before[section][field] != result[section][field] else 'UNCHANGED')
    data = {'row': row['id'], 'before_ci_high': str(old), 'after_ci_high': row['ci_high'],
            'dependants': status, 'refusal': result.get('refusal'), 'gate_reasons': result.get('gate_reasons')}
    emit('dependants', data)
    # A production refusal is a valid fail-closed invalidation, never a silent restamp.
    if result.get('refusal'):
        assert 'STALE_DEPENDENT' in result['refusal'], data
        # Every cached scientific consumer must be identified, not only prose
        # siblings that happen to use a different stamp representation.
        violations = json.loads(result['refusal'].split(': ', 1)[1])
        paths = {v.get('object_path') for v in violations if v['code'] == 'STALE_DEPENDENT'}
        assert {'/outcomes/0/result', '/grade', '/claimgraph/objects/0',
                '/claimgraph/objects/1'} <= paths, data
    else:
        assert all(v == 'CHANGED' for v in status.values()), data
