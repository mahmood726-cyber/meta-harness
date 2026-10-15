"""Temporary A4 behavioural regression markers, not signature enforcement."""
import hashlib
import json
import os
import sys
from concurrent.futures import Future
import pytest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, 'scripts')]
import rob2_dual as rd
AWAITING = "awaiting Mahmood's signature for amendment A4 (outputs/robgrade/SIGNING_A4_REQUEST.md)"
# Synthetic fixture only; these identifiers are not research claims.
TEXT = 'Recruiters could not foresee which group the next participant would enter.'
SRC = dict(id='abstract:PMID 1', kind='abstract', text=TEXT,
           sha256=hashlib.sha256(TEXT.encode()).hexdigest(), open_for_prompt=True, licence='PubMed abstract')
ITEM = dict(slug='t', pmid='1', nct=None, outcome='o', sources=[SRC], machine_d5=None, key='t::1::o')

def reply(answer='PY'):
    return dict(answers=[dict(qid='1.2', answer=answer, quote=TEXT, source_id=SRC['id'], rationale='Fixture')], notes='')

class InlinePool:
    def submit(self, fn, *args):
        f = Future()
        f.set_result(fn(*args))
        return f

@pytest.fixture
def records(tmp_path, monkeypatch):
    monkeypatch.setattr(rd, 'REC_DIR', str(tmp_path))
    consumed, calls = [], []
    original = rd.ms.replay
    def spy(rec):
        consumed.append(rec['record_id'])
        return original(rec)
    monkeypatch.setattr(rd.ms, 'replay', spy)
    def write(who, prompt, answer='PY', held=None):
        rec = rd.ms.build_record(prompt_bytes=prompt if held is None else held,
            response_bytes=json.dumps(reply(answer)).encode(),
            model=dict(id_requested=who, id_reported=who, provider='fixture'),
            params={}, not_controllable=[], client=dict(name='offline fixture'),
            request_utc='2026-10-14T00:00:00Z', response_utc='2026-10-14T00:00:01Z',
            caller=dict(file='tests/test_rob2_dual_a4.py', line='fixture', purpose='A4 plant'),
            input_digests=[dict(ref=SRC['id'], sha256=SRC['sha256'])], owner_lines=[])
        rd.ms.write_record(rec, tmp_path)
        return dict(state='RAN_OK', record_id=rec['record_id'], prompt_sha256=hashlib.sha256(prompt).hexdigest())
    def call(item, who, prompt):
        calls.append((who, prompt))
        return write(who, prompt)
    monkeypatch.setattr(rd, '_call', call)
    return write, consumed, calls

def setup(records, role=None, field='held', disagreement=False):
    write = records[0]
    p = rd.prompt_bytes(ITEM)
    answers = dict(codex='PY', agy='PN' if disagreement else 'PY')
    runs = {w: write(w, p, a) for w, a in answers.items()}
    prompts = dict(codex=p, agy=p)
    if disagreement:
        a, b = [rd.verify_answers(reply(answers[w]), ITEM) for w in ('codex', 'agy')]
        _, dis = rd.agree(a, b)
        typed, _ = rd.rt.typed_answers(ITEM['sources'], None, outcome=ITEM['outcome'])
        shown = {q: {'reader 1': x, 'reader 2': y} for q, (x, y) in dis.items() if q not in typed}
        prompts['adjudicator'] = rd.prompt_bytes(ITEM, 'adjudicator', shown)
        runs['adjudicator'] = write('adjudicator', prompts['adjudicator'])
    if role:
        if field == 'held':
            runs[role] = write(role, prompts[role], answers.get(role, 'PY'), b'OLD prompt')
        else:
            runs[role]['prompt_sha256'] = hashlib.sha256(b'OLD prompt').hexdigest()
    return {ITEM['key']: runs}, prompts

@pytest.mark.parametrize('order', [('PY', 'PN'), ('PN', 'PY')])
@pytest.mark.xfail(strict=True, reason=AWAITING)
def test_A4_duplicate_rows(order):
    a = rd.verify_answers(dict(answers=[reply(v)['answers'][0] for v in order]), ITEM)['1.2']
    assert (a['answer'], a.get('dropped', {}).get('why')) == ('NI', 'AMBIGUOUS_CONFLICTING_ROWS')

@pytest.mark.parametrize('role', ('codex', 'agy', 'adjudicator'))   # a tuple: a list headed by a CLI name reads as an argv (model inventory)
@pytest.mark.parametrize('field', ['held', 'manifest'])
@pytest.mark.xfail(strict=True, reason=AWAITING)
def test_A4_stale_never_replayed(records, role, field):
    runs, _ = setup(records, role, field, disagreement=role == 'adjudicator')
    stale = runs[ITEM['key']][role]['record_id']
    obj, _ = rd.process(ITEM, runs, False, {})
    assert stale not in records[1], f'stale {role} response was consumed'
    assert obj['domains']['D1']['answers']['1.2']['answer'] == 'NI'

@pytest.mark.parametrize('role', ('codex', 'agy', 'adjudicator'))   # a tuple: a list headed by a CLI name reads as an argv (model inventory)
@pytest.mark.xfail(strict=True, reason=AWAITING)
def test_A4_live_replacement(records, role):
    runs, prompts = setup(records, role, disagreement=role == 'adjudicator')
    stale = runs[ITEM['key']][role]['record_id']
    obj, updated = rd.process(ITEM, runs, True, dict(codex=InlinePool(), agy=InlinePool()))
    assert (role, prompts[role]) in records[2], f'stale {role} did not trigger replacement call'
    assert stale not in records[1]
    assert updated[role]['record_id'] != stale
    assert obj['domains']['D1']['answers']['1.2']['answer'] == 'PY'

@pytest.mark.parametrize('live', [False, True])
@pytest.mark.parametrize('disagreement', [False, True])
def test_A4_fresh_controls(records, live, disagreement):
    runs, _ = setup(records, disagreement=disagreement)
    obj, _ = rd.process(ITEM, runs, live, dict(codex=InlinePool(), agy=InlinePool()))
    assert obj['domains']['D1']['answers']['1.2']['answer'] == 'PY'
    assert set(records[1]) == {r['record_id'] for r in runs[ITEM['key']].values()}
    assert records[2] == []