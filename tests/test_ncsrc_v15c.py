from functools import lru_cache
import json
import subprocess
from pathlib import Path

import pytest
from scripts import m2_pretriage as pre
from scripts import v15c_decisions as decisions
from scripts import refresh_result_change_notices as notices
from harness import enforcement, consumer_consistency as cc, pipeline, synth

ROOT = Path(__file__).resolve().parents[1]
CONT = ('mean1', 'sd1', 'nc1', 'mean2', 'sd2', 'nc2')


@lru_cache(maxsize=None)
def baseline(slug):
    return json.loads(subprocess.check_output(
        ['git', 'show', f'66219d315:docs/reviews/{slug}/review.json'], cwd=ROOT))


def rows():
    for slug in ('esketamine-trd-madrs', 'tocilizumab-covid19-mortality'):
        outcome = baseline(slug)['outcomes'][0]
        for t in outcome['trials']:
            if t['id'].startswith('NCT') or (slug.startswith('esketamine') and t['id'] in ('PMID 31109201', 'PMID 37025256')):
                yield dict(t, slug=slug, outcome=outcome['name'],
                           served={k: t[k] for k in enforcement.SERVED_KEYS + CONT if t.get(k) is not None})


@pytest.mark.parametrize('rid', ['NCT02417064', 'NCT02422186', 'PMID 31109201', 'PMID 37025256'])
def test_pretriage_ncsrc_registry(rid):
    row = next(r for r in rows() if r['id'] == rid)
    source = pre.open_source(row)
    assert source is not None
    assert source.licence_class == 'PUBLIC_DOMAIN_REGISTRY'
    assert 'paramType' in source[0] and 'PRIMARY' in source[0]


@pytest.mark.parametrize('rid,licence', [('NCT04403685', 'CC BY-NC'), ('NCT04320615', 'COPYRIGHT')])
def test_pretriage_ncsrc_refused_licence(rid, licence, monkeypatch):
    monkeypatch.setattr(pre.mcl, 'call', lambda *a, **k: pytest.fail('no model calls'))
    row = next(r for r in rows() if r['id'] == rid)
    result = pre.triage(row, '')
    assert result['state'] == 'NOT_ADMISSIBLE_LICENCE'
    assert result['licence_class'] == licence and result['licence_statement']


def test_enforcement_ncsrc_continuous_snapshot(monkeypatch):
    row = next(r for r in rows() if r['id'] == 'PMID 31109201')
    row['endpoint_admissibility'] = 'UNBOUND_LEGACY'
    decision = dict(row, decision='ADMIT', basis='test snapshot')
    monkeypatch.setattr(enforcement, 'decisions', lambda path: {(row['slug'], row['outcome'], row['id']): decision})
    kept, absent = enforcement.apply(row['slug'], {'name': row['outcome']}, [row])
    assert not absent and kept[0]['endpoint_admissibility'] == 'SIGNED_BINDING'
    generated = decisions.decide('BIND_DIFFERS_FROM_SERVED', row)
    assert generated['served'] == row['served']


def test_result_change_ncsrc_evidence_mechanism():
    row = {'id': 'test', 'state': 'REFUSED_ON_EVIDENCE', 'reason': 'different endpoint',
           'absent_kind': 'refused_on_evidence',
           'enforcement': {'decision': 'REFUSE', 'basis': 'signed different endpoint'}}
    text = notices._reason(['test'], {'test': row})
    assert 'signed different endpoint' in text
    assert 'not asserted wrong' not in text and 'hand-row binder' not in text


def test_consumer_consistency_ncsrc_preserves_refusal(monkeypatch):
    row = {'id': 'test', 'state': 'REFUSED_ON_EVIDENCE', 'reason_code': 'RESULT_INCOMPATIBLE',
           'reason': 'signed different endpoint', 'enforcement': {'decision': 'REFUSE'}}
    review = {'outcomes': [{'name': 'test', 'declared_absent_trials': [row]}]}
    monkeypatch.setattr(cc, 'outcome_source_candidate', lambda *a: {
        'source_has_value': True, 'reason_code': cc.KNOWN_REPORTED_NOT_YET_EXTRACTED, 'source_span': 'held value'})
    cc.annotate_review(review, 'test', {'primary_outcome': {'name': 'test'}}, {})
    assert row['state'] == 'REFUSED_ON_EVIDENCE' and row['reason'] == 'signed different endpoint'
    assert row['consumer_consistency_finding']['source_span'] == 'held value'


def test_pretriage_ncsrc_empty_md_method():
    spec = json.loads((ROOT / 'topics/esketamine-trd-madrs.json').read_text(encoding='utf-8'))['primary_outcome']
    out = pipeline._build_outcome(spec, 'continuous', [], {}, [], [])
    assert out['method'] == synth.method_text(spec['estimand'])


def test_pretriage_ncsrc_continuous_bind():
    row = next(r for r in rows() if r['id'] == 'PMID 31109201')
    source = pre.open_source(row)
    answer = {'decision': 'BIND', 'span': source[0], 'numbers': row['served']}
    assert pre.check_bind(answer, source[0])[0]
    assert pre.served_class(dict(row, state='AGREED_BIND', proposal=answer)) == 'BIND_CONFIRMS_SERVED'
    assert set(CONT) <= set(pre.SCHEMA['properties']['numbers']['properties'])


def test_pretriage_ncsrc_capture_continuous(monkeypatch):
    slug = 'esketamine-trd-madrs'
    review = baseline(slug)
    topic = json.loads((ROOT / 'topics' / (slug + '.json')).read_text(encoding='utf8'))
    class Result:
        returncode = 0
        stdout = 'docs/reviews/' + slug
    monkeypatch.setattr(pre.subprocess, 'run', lambda *a, **k: Result())
    monkeypatch.setattr(pre, '_main_files', lambda d: {d + '/review.json'})
    monkeypatch.setattr(pre, '_git_json', lambda path, **k: topic if path.startswith('topics/') else review)
    captured = next(r for r in pre.unbound_rows() if r['id'] == 'PMID 31109201' and r['primary'])
    assert set(CONT) <= set(captured['served'])


@pytest.mark.parametrize('statement,allowed', [
    ('This article is licensed under CC BY 4.0.', True),
    ('This article is licensed under CC0.', True),
    ('This article is licensed under CC BY-ND.', False),
    ('This article is licensed under CC BY-SA.', False),
    ('This article is not licensed under CC BY.', False),
])
def test_pretriage_ncsrc_explicit_licence(tmp_path, monkeypatch, statement, allowed):
    folder = tmp_path / 'cache' / 'test'
    folder.mkdir(parents=True)
    (folder / 'ft_1.txt').write_text(statement, encoding='utf8')
    monkeypatch.setattr(pre, 'ROOT', str(tmp_path))
    source = pre.open_source({'id': 'NCT00000001', 'family_report_id': '1', 'slug': 'test'})
    assert source.admissible is allowed
    assert source.licence_statement == statement
