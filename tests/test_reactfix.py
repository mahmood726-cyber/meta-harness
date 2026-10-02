"""REVIEW3 regressions. Mutated held readings are synthetic plants, never findings."""
from copy import deepcopy
import base64
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import pytest
from harness import forest_gate as fg, disperse2_gate as dg, recovery_binding as rb
from reproducible_ai import model_source as ms
from scripts.record_reading import build_reading

ROOT = Path(__file__).resolve().parents[1]


def base_module(name):
    # The PRE-FIX gate exactly as REVIEW3 attacked it (never committed as harness code), pinned as a test fixture so the
    # 'accepted before, refused now' plants do not depend on a lane directory.
    path = ROOT / 'tests/fixtures/review3_prefix' / (name + '.py.txt')
    loader = importlib.machinery.SourceFileLoader('prefix_' + name, str(path))
    spec = importlib.util.spec_from_loader('prefix_' + name, loader)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rebuild(record, claim, *, provider=None, model=None):
    pin = dict(record['model'])
    if provider is not None:
        pin.update(provider=provider, reported_by='self-reported synthetic plant; not a server attestation')
    if model is not None:
        pin.update(id_requested=model, id_reported=model)
    return ms.build_record(prompt_bytes=base64.b64decode(record['prompt']['b64']),
        response_bytes=ms.canonical(claim), model=pin, params={}, not_controllable=[],
        client={'name': 'synthetic regression plant'}, request_utc=record['request_utc'],
        response_utc=record['response_utc'], caller={'file': __file__, 'line': 'rebuild',
        'purpose': 'synthetic plant, never a source reading'}, input_digests=record['input_digests'])


@pytest.fixture(scope='module')
def held():
    records = [ms.load_record(p) for p in sorted((ROOT / 'evidence/model_calls').glob('*.json'))]
    # Plants attack the same-provider quorum, so they are built from the openai readings only; the real recorded
    # cross-provider reading (provider anthropic) is exercised by test_real_cross_provider_record below.
    forest = [r for r in records if r.get('caller', {}).get('lane') == 'REACTFIG' and r['state'] == 'RAN_OK'
              and r['model']['provider'] == 'openai']
    tables = [ms.load_record(ROOT / p) for p in (ROOT / 'evidence/model_calls/disperse2_table_records.txt').read_text(encoding='utf-8').split()]
    text, images = dg.held_inputs(ROOT)
    return forest, tables, text, images


def forest_run(records, module=fg):
    return module.gate(records, root=ROOT, replay_response=ms.replay)


def table_run(records, held, module=dg):
    return module.gate_records(records, held[2], held[3], replay_response=ms.replay, record_problems=ms.record_problems)


def group86(held):
    return [r for r in held[1] if json.loads(ms.replay(r))['tables'][0]['table_id'] == 'Table 86']


def table_plant(held, name):
    out = []
    for i, rec in enumerate(group86(held)):
        claim = json.loads(ms.replay(rec)); table = claim['tables'][0]
        if name == 'table_id': table['table_id'] = 'Table 999'
        elif name == 'window':
            for row in table['rows']:
                if row['timepoint'] == '4 weeks': row['timepoint'] = '12 weeks'
        elif name == 'echo_km': table['footnotes'] = 'Kaplan-Meier estimates only'
        elif name == 'empty_echo': table['footnotes'] = ''
        elif name == 'truncated_echo': table['footnotes'] = '  ' + ' '.join(table['footnotes'].split())[:60] + '  '
        elif name == 'dose_swap' and i < 2:
            a, b = dg.ARMS[:2]
            table['arm_sizes'][a], table['arm_sizes'][b] = table['arm_sizes'][b], table['arm_sizes'][a]
            table['arm_headers'] = {arm: f'{arm} (n={n})' for arm, n in table['arm_sizes'].items()}
            for row in table['rows']:
                if row['arm'] in (a, b): row['arm'] = b if row['arm'] == a else a
        elif name == 'rounded_count' and i < 2:
            row = next(r for r in table['rows'] if r['n'] == 0 and dg.normalized_percent(r['percent']) == '0' and r['arm'] == dg.ARMS[0])
            row['n'] = 1; row['printed_cell'] = row['printed_cell'].replace('0 (', '1 (', 1)
        out.append(rebuild(rec, claim))
    return out


@pytest.mark.parametrize('name,rule', [('table_id','TABLE_ID'),('window','TIMEPOINT'),('echo_km','CONTEXT_CONTRADICTION')])
def test_review3_semantic_plants(held, name, rule):
    records = table_plant(held, name)
    before = table_run(records, held, base_module('disperse2_gate'))
    after = table_run(records, held)
    assert before['status'] == 'ADMIT'
    assert after['status'] == 'REFUSED' and after['reason'].startswith(rule + ':')
    assert not after['rows'] and not after['pool_admission']


@pytest.mark.parametrize('name', ['empty_echo', 'truncated_echo'])
def test_context_negative_controls(held, name):
    result = table_run(table_plant(held, name), held)
    assert result['status'] == 'ADMIT'
    assert all(r['held_context'] and r['model_context_echo'] for r in result['rows'])
    assert all(r['transcription_state'] == fg.MODEL_TRANSCRIBED_CHECKED for r in result['rows'])


@pytest.mark.parametrize('kind', ['subgroup', 'overall'])
@pytest.mark.parametrize('field,value', [('or', '9.99'), ('ci_low', '0'), ('ci_high', '0.01')])
def test_interval_order(held, kind, field, value):
    proposal = {'rows': [r['row'] for r in forest_run(held[0])['rows']]}
    wrong = deepcopy(proposal)
    next(r for r in wrong['rows'] if r['kind'] == kind)[field] = value
    records = [rebuild(rec, wrong if i < 2 else proposal) for i, rec in enumerate(held[0])]
    before = forest_run(records, base_module('forest_gate'))
    assert not any('INTERVAL_ORDER' in reason for r in before['rows'] for reason in r['reasons'])
    after = forest_run(records)
    assert any('INTERVAL_ORDER' in json.dumps(c) for c in after['cell_resolutions'])
    assert not any(r['status'] == 'ADMITTED' for r in after['rows'])


def test_sarilumab_swap_disclosed_and_cross_provider_not_outvoted(held):
    source = {'rows': [r['row'] for r in forest_run(held[0])['rows']]}
    wrong = deepcopy(source)
    a, b = [r for r in wrong['rows'] if r['kind'] == 'trial' and r['agent'] == 'Sarilumab'][:2]
    for key in (*fg.COUNTS, *fg.EFFECTS, 'weight'): a[key], b[key] = b[key], a[key]
    records = [rebuild(rec, wrong if i < 2 else source) for i, rec in enumerate(held[0])]
    before = forest_run(records, base_module('forest_gate'))
    assert all(r['status'] == 'ADMITTED' for r in before['rows'] if r['row']['trial'] in (a['trial'], b['trial']))
    extra = rebuild(held[0][0], source, provider='anthropic', model='synthetic-other-provider')
    after = forest_run(records + [extra])
    for row in after['rows']:
        if row['row']['trial'] in (a['trial'], b['trial']):
            assert row['transcription_state'] == fg.MODEL_TRANSCRIBED_CHECKED
            assert row['identity_witness'] == 'NO_TABLE1_IDENTITY_WITNESS'
            assert row['cross_provider_witnesses'][0]['disagreeing_cells']


@pytest.mark.parametrize('name', ['dose_swap', 'rounded_count'])
def test_unverifiable_cells_cannot_become_verified_by_majority(held, name):
    records = table_plant(held, name)
    assert table_run(records, held, base_module('disperse2_gate'))['status'] == 'ADMIT'
    source = json.loads(ms.replay(group86(held)[0]))
    extra = rebuild(records[0], source, provider='anthropic', model='synthetic-other-provider')
    after = table_run(records + [extra], held)
    assert after['status'] == 'ADMIT' and not after['pool_admission']
    disputed = [r for r in after['rows'] if r['cross_provider_witnesses'][0]['disagreeing_cells']]
    assert disputed
    assert all(r['transcription_state'] == fg.MODEL_TRANSCRIBED_CHECKED and 'DOSE_COLUMN_UNVERIFIED' in r['flags'] for r in disputed)


def test_full_cross_provider_agreement_and_missing_cell(held):
    records = group86(held)
    initial = table_run(records, held)
    # Construct a synthetic agreeing witness from the actually resolved cells;
    # explicitly a fixture, never presented as an independent real reading.
    claim = json.loads(ms.replay(records[0]))
    table = claim['tables'][0]
    table['rows'] = [k['resolved'] for k in initial['agreement_audit']['keys']]
    table['arm_headers'] = {r['arm']: r['arm_header_verbatim'] for r in initial['rows']}
    table['printed_footnotes'] = initial['rows'][0]['printed_footnotes']
    extra = rebuild(records[0], claim, provider='anthropic', model='synthetic-other-provider')
    verified = table_run(records + [extra], held)
    assert all(r['transcription_state'] == fg.CROSS_PROVIDER_VERIFIED for r in verified['rows'])
    assert all('DOSE_COLUMN_UNVERIFIED' not in r['flags'] for r in verified['rows'])
    table['rows'].pop()
    missing = table_run(records + [rebuild(extra, claim)], held)
    assert sum(r['transcription_state'] == fg.MODEL_TRANSCRIBED_CHECKED for r in missing['rows']) == 1
    # A second disagreeing cross-provider witness cannot be outvoted by any group.
    mixed = table_run(records + [extra, rebuild(extra, claim, provider='third-provider', model='synthetic-third')], held)
    assert sum(r['transcription_state'] == fg.MODEL_TRANSCRIBED_CHECKED for r in mixed['rows']) == 1


def test_forest_cross_provider_agreement_and_no_quorum(held):
    source = {'rows': [r['row'] for r in forest_run(held[0])['rows']]}
    extra = rebuild(held[0][0], source, provider='anthropic', model='synthetic-other-provider')
    result = forest_run(held[0] + [extra])
    assert all(r['transcription_state'] == fg.CROSS_PROVIDER_VERIFIED for r in result['rows'] if r['status'] == 'ADMITTED')
    assert all(r['transcription_state'] != fg.CROSS_PROVIDER_VERIFIED for r in result['rows'] if r['status'] != 'ADMITTED')
    no_quorum = forest_run(held[0][:2] + [extra])
    assert all(r['status'] == 'REFUSED' for r in no_quorum['rows'])


def test_recorder_and_prompt_integrity(held):
    ref = held[0][0]; response = ms.replay(ref); prompt = base64.b64decode(ref['prompt']['b64'])
    kwargs = dict(provider='anthropic', model='self-reported-test', request_utc=ref['request_utc'], response_utc=ref['response_utc'])
    record = build_reading(response, prompt, ref, **kwargs)
    assert ms.replay(record) == response and not ms.record_problems(record)
    assert record['client'] == {'name': 'in-session assistant reading'}
    assert 'self-reported' in record['model']['reported_by'] and record['not_controllable']
    with pytest.raises(ValueError, match='PROMPT_REFUSED'):
        build_reading(response, prompt + b' changed', ref, **kwargs)
    with pytest.raises(ValueError, match='PROVIDER_REFUSED'):
        build_reading(response, prompt, ref, **dict(kwargs, provider=ref['model']['provider']))
    # An integrity-valid different prompt still cannot upgrade the gate.
    record['prompt'] = ms._blob(prompt + b' changed'); record['record_id'] = ms.record_id_of(record)
    assert all(r['status'] == 'REFUSED' for r in forest_run(held[0] + [record])['rows'])


def test_runtime_rejects_unwitnessed_upgrade():
    row = dict(transcription_state=fg.CROSS_PROVIDER_VERIFIED, consensus_provider='openai', cross_provider_witnesses=[])
    with pytest.raises(ValueError, match='TRANSCRIPTION_STATE_REFUSED'):
        rb.check_transcription_state(row)
    row['transcription_state'] = fg.MODEL_TRANSCRIBED_CHECKED
    rb.check_transcription_state(row)


def test_real_cross_provider_record():
    """The recorded anthropic reading upgrades a row only by agreeing on every cell, and never makes it poolable."""
    recs = [ms.load_record(p) for p in sorted((ROOT / 'evidence/model_calls').glob('*.json'))]
    forest = [r for r in recs if r.get('caller', {}).get('lane') == 'REACTFIG']
    other = [r for r in forest if r['state'] == 'RAN_OK' and r['model']['provider'] != 'openai']
    assert [r['model']['provider'] for r in other] == ['anthropic']
    assert 'not a server attestation' in other[0]['model']['reported_by']
    without = forest_run([r for r in forest if r not in other])
    assert {b['state'] for b in without['bindings']} == {fg.MODEL_TRANSCRIBED_CHECKED}
    with_ = forest_run(forest)
    assert {b['state'] for b in with_['bindings']} == {'CROSS_PROVIDER_VERIFIED'}
    assert not any(b['poolable'] for b in with_['bindings'])
    # every upgraded row is one where the other-provider reading agrees on every cell; refused rows stay refused
    assert sum(r['status'] == 'REFUSED' for r in with_['rows']) == sum(r['status'] == 'REFUSED' for r in without['rows'])
