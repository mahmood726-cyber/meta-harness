"""Synthetic arithmetic PLANTS. No fixture count is presented as research data."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from harness import forest_gate as fg, recovery_excerpt, recovery_binding
from reproducible_ai import model_source as ms
from scripts.react_figure_proposal import census, output_schema, prompt

ROOT = Path(__file__).resolve().parents[1]


def proposal():
    # Synthetic, hand-calculable OR=0.4444, Wald CI=0.1964..1.0057.
    row = dict(kind='trial', agent='Tocilizumab', trial='Synthetic', registration='NCT00000001',
               ai=10, n1i=100, ci=20, n2i=100, **{'or': '0.44'}, ci_low='0.20', ci_high='1.01', weight='100.00')
    return {'rows': [row, dict(row, kind='subgroup', trial='Subtotal'),
                     dict(row, kind='overall', agent='All', trial='Overall')]}


def record(obj, model='fixture-reader-1', figure=b'synthetic-image'):
    return ms.build_record(prompt_bytes=b'Synthetic plant', response_bytes=ms.canonical(obj),
                           model={'id_requested': model, 'id_reported': model, 'provider': 'synthetic'},
                           params={}, not_controllable=[], client={'name': 'fixture'},
                           request_utc='2026-09-30T00:00:00Z', response_utc='2026-09-30T00:00:01Z',
                           caller={'file': __file__, 'line': 'record', 'purpose': 'synthetic plant', 'lane': 'REACTFIG'},
                           input_digests=[{'ref': fg.FIGURE, 'sha256': hashlib.sha256(figure).hexdigest(),
                                           'media_type': 'image/jpeg'}])


@pytest.fixture
def held(tmp_path):
    image = tmp_path / fg.FIGURE
    image.parent.mkdir(parents=True)
    image.write_bytes(b'synthetic-image')
    excerpt = tmp_path / recovery_excerpt.OUTPUT
    excerpt.parent.mkdir(parents=True)
    # Preserve the real parser's provenance/header contract, but replace data
    # rows with clearly synthetic bytes in a temporary root only.
    source = (ROOT / recovery_excerpt.OUTPUT).read_text(encoding='utf-8')
    header = 'Trial | NCT (or printed registration) | intervention arm n | comparator arm n'
    excerpt.write_bytes((source.split(header)[0] + header + '\nSynthetic | NCT00000001 | 100 | 100\n').encode('utf-8'))
    recovery = tmp_path / 'docs/recovery_maps.json'
    recovery.parent.mkdir(parents=True)
    recovery.write_text(json.dumps({'topics': {fg.SLUG: {'population': 'outcomes recorded', 'entries': [
        {'trial': 'Synthetic', 'ai': 10, 'n1i': 100, 'ci': 20, 'n2i': 100}]}}}), encoding='utf-8')
    return tmp_path


def run_gate(held, obj, second=None):
    records = [record(obj), record(second or obj, 'fixture-reader-2')]
    if second is None or fg.validate(second) == fg.validate(obj):
        records.append(record(obj, 'fixture-reader-3'))
    return fg.gate(records, root=held, replay_response=ms.replay)


def reasons(report):
    return '\n'.join(report['problems'] + [p for r in report['rows'] for p in r['reasons']])


def test_correct_synthetic_proposal_passes_all_rules(held):
    report = run_gate(held, proposal())
    assert [r['status'] for r in report['rows']] == ['ADMITTED', 'ADMITTED', 'UNVERIFIABLE']
    assert report['bindings'][0]['state'] == 'MODEL_TRANSCRIBED_CHECKED'
    assert report['bindings'][0]['figure_counts'] == dict(ai=10, n1i=100, ci=20, n2i=100)
    assert not report['poolable']
    with pytest.raises(ValueError):
        recovery_binding.require_poolable(report['bindings'][0])


def mutations():
    return [
        ('transposed', lambda p: p['rows'][0].update(ai=20, ci=10), 'ARITHMETIC:'),
        ('digit', lambda p: p['rows'][0].update(ai=11), 'ARITHMETIC:'),
        ('subtotal', lambda p: p['rows'][1].update(n1i=101), 'TOTALS:'),
        ('overall', lambda p: p['rows'][2].update(n2i=101), 'TOTALS:'),
        ('table1', lambda p: [r.update(n1i=101) for r in p['rows']], 'TABLE1_TOTAL_MISMATCH:'),
        ('weights', lambda p: p['rows'][0].update(weight='90.00'), 'WEIGHTS:'),
    ]


@pytest.mark.parametrize('name,mutate,reason', mutations())
def test_plants_base_replays_but_new_gate_refuses(held, name, mutate, reason):
    obj = proposal()
    mutate(obj)
    # PRE-FIX: base replay returns exactly this defective proposal, unchecked.
    assert json.loads(ms.replay(record(obj))) == obj
    report = run_gate(held, obj)
    assert reason in reasons(report)
    assert report['rows'][0]['status'] == 'REFUSED'
    assert report['bindings'][0]['state'] == 'RELAYED'


def test_two_proposals_differing_one_cell_are_refused(held):
    second = proposal()
    second['rows'][0]['ai'] += 1
    assert json.loads(ms.replay(record(second)))['rows'][0]['ai'] == 11
    report = run_gate(held, proposal(), second)
    assert 'AGREEMENT: Synthetic: ai' in reasons(report)
    assert all(r['status'] == 'REFUSED' for r in report['rows'])


@pytest.mark.parametrize('mode', ['one', 'duplicate', 'same-model', 'tampered', 'wrong-image', 'missing-image'])
def test_record_integrity_and_independence_fail_closed(held, mode):
    records = [record(proposal()), record(proposal(), 'fixture-reader-2')]
    if mode == 'one':
        records.pop()
    elif mode == 'duplicate':
        records[1] = copy.deepcopy(records[0])
    elif mode == 'same-model':
        records[1]['model'] = records[0]['model']
        records[1]['request_utc'] = '2026-09-30T00:00:02Z'
        records[1]['record_id'] = ms.record_id_of(records[1])
    elif mode == 'tampered':
        records[0]['params']['tamper'] = True
    elif mode == 'wrong-image':
        records[0] = record(proposal(), figure=b'wrong-image')
    else:
        (held / fg.FIGURE).unlink()
    report = fg.gate(records, root=held, replay_response=ms.replay)
    assert report['problems']
    assert all(r['status'] == 'REFUSED' for r in report['rows'])


@pytest.mark.parametrize('change', [lambda p: p['rows'][0].update(ai=True),
                                   lambda p: p['rows'][0].update(n1i=0),
                                   lambda p: p['rows'][0].update(ci=101),
                                   lambda p: p['rows'][0].update(weight='NaN'),
                                   lambda p: p['rows'].append(copy.deepcopy(p['rows'][0])),
                                   lambda p: p['rows'][0].pop('agent')])
def test_malformed_rows_are_named_refusals(held, change):
    obj = proposal()
    change(obj)
    report = run_gate(held, obj)
    assert 'RECORD_REFUSED:' in reasons(report)
    assert not any(r['status'] == 'ADMITTED' for r in report['rows'])


def test_zero_cell_rule_and_printed_bound():
    row = proposal()['rows'][0]
    row.update(ai=0, n1i=10, ci=2, n2i=11)
    effect = fg.recompute(row)
    assert effect[0] == pytest.approx((.5 * 9.5) / (10.5 * 2.5))
    assert fg.matches(.004, '<0.01')
    assert not fg.matches(.011, '<0.01')
    assert fg.matches(.4444, '0.44')
    assert not fg.matches(.4444, '0.45')
    row.update(ci=0)
    assert fg.recompute(row) is None


def test_double_zero_na_and_missing_summary_fail_closed(held):
    obj = proposal()
    for r in obj['rows']:
        r.update(ai=0, ci=0, **{'or': 'NA'}, ci_low='NA', ci_high='NA')
    assert run_gate(held, obj)['rows'][0]['status'] == 'ADMITTED'
    obj['rows'][0]['or'] = '1.00'
    assert 'double-zero requires NA' in reasons(run_gate(held, obj))
    obj = proposal()
    obj['rows'].pop(1)
    obj['rows'].insert(1, dict(obj['rows'][0], trial='Synthetic two'))
    assert 'missing/duplicate printed subgroup' in reasons(run_gate(held, obj))


def test_relay_conflict_names_figure_values_without_rewriting_map(held):
    path = held / 'docs/recovery_maps.json'
    block = json.loads(path.read_text())
    block['topics'][fg.SLUG]['entries'][0]['ci'] = 19
    path.write_text(json.dumps(block), encoding='utf-8')
    before = path.read_bytes()
    binding = run_gate(held, proposal())['bindings'][0]
    assert binding['state'] == 'CONFLICT'
    assert binding['conflicts'] == ['ci']
    assert binding['figure_counts']['ci'] == 20 and binding['relayed']['ci'] == 19
    assert path.read_bytes() == before


def test_authoritative_bad_registration_does_not_fall_back(held):
    obj = proposal()
    obj['rows'][0]['registration'] = 'NCT99999999'
    assert 'TABLE1_IDENTITY_UNRESOLVED' in reasons(run_gate(held, obj))


def test_different_prompts_and_failed_verifier_cannot_admit(held):
    records = [record(proposal()), record(proposal(), 'fixture-reader-2')]
    records[1]['prompt'] = ms._blob(b'Different prompt with prior answers')
    records[1]['record_id'] = ms.record_id_of(records[1])
    report = fg.gate(records, root=held, replay_response=ms.replay)
    assert 'identical prompt bytes' in reasons(report)
    assert all(r['status'] == 'REFUSED' for r in report['rows'])
    def broken(record):
        raise RuntimeError('verifier unavailable')
    report = fg.gate(records, root=held, replay_response=broken)
    assert 'RECORD_REFUSED: verifier unavailable' in reasons(report)
    assert report['rows'] == []


def test_schema_prompt_and_census_no_calls(held):
    assert output_schema()['additionalProperties'] is False
    assert b'EVERY row' in prompt()
    (held / 'topics').mkdir()
    for slug in [fg.SLUG, 'irrelevant-topic']:
        (held / 'topics' / (slug + '.json')).write_text('{}')
    c = census(held)
    assert c['topics_examined'] == 2
    assert c['no_recorded_proposal']['n_of_N'] == '1 of 2'
    assert all(r['n_of_N'] == '0 of 0' for r in c['rules'].values())


def plant_evidence():
    """Reportable base behavior, actually executed rather than guessed."""
    out = []
    for name, mutate, reason in mutations():
        obj = proposal()
        mutate(obj)
        replayed = json.loads(ms.replay(record(obj)))
        out.append({'plant': name, 'base_replay': replayed, 'new_refusal_prefix': reason})
    return out


def structural_plants():
    """Shared exact inputs for the before/after structural audit."""
    cases = {}
    obj = proposal()
    obj['rows'][-1]['agent'] = ''
    cases['empty overall agent (valid)'] = obj
    for kind in ('trial', 'subgroup'):
        obj = proposal()
        next(r for r in obj['rows'] if r['kind'] == kind)['agent'] = ''
        cases['empty ' + kind + ' agent'] = obj
    obj = proposal()
    obj['rows'].pop(1)
    cases['singleton without subtotal (valid)'] = obj
    obj = copy.deepcopy(obj)
    obj['rows'].insert(1, dict(obj['rows'][0], trial='Synthetic two'))
    for r in obj['rows'][:2]:
        r['weight'] = '50.00'
    for k in fg.COUNTS:
        obj['rows'][-1][k] *= 2
    cases['two trials without subtotal'] = obj
    for k in fg.COUNTS:
        obj = proposal()
        obj['rows'][-1][k] += 1
        cases['overall ' + k + ' above sum'] = obj
    obj = proposal()
    obj['rows'][-1].update(ci=19, n2i=99)
    cases['control below sum (unverifiable)'] = obj
    return cases


@pytest.mark.parametrize('name', list(structural_plants()))
def test_structural_rules_preserve_refusals(held, name):
    report = run_gate(held, structural_plants()[name])
    if '(valid)' in name or '(unverifiable)' in name:
        assert not report['problems']
        assert report['rows'][0]['status'] == 'ADMITTED'
        assert report['rows'][-1]['status'] == 'UNVERIFIABLE'
        assert not report['rows'][-1]['poolable']
        assert report['control_accounting'][0]['status'] == 'UNVERIFIABLE'
        if '(unverifiable)' in name:
            assert report['control_accounting'][0]['code'] == 'SHARED_CONTROL_DEDUP'
            assert report['control_accounting'][0]['fields']['ci']['gap'] == 1
    else:
        assert 'SCHEMA: agent required' in reasons(report) if name.startswith('empty') else 'TOTALS:' in reasons(report)
        assert all(r['status'] == 'REFUSED' for r in report['rows'])
        assert report['bindings'][0]['state'] == 'RELAYED'


def test_overall_agent_equivalence_preserves_input_and_other_cells(held):
    first, second = proposal(), proposal()
    first['rows'][-1]['agent'] = ''
    second['rows'][-1]['agent'] = 'Overall'
    before = copy.deepcopy(second)
    report = run_gate(held, first, second)
    assert second == before
    assert not report['problems']
    assert report['rows'][0]['status'] == 'ADMITTED'
    second['rows'][-1]['or'] = '0.45'
    assert 'AGREEMENT:' in reasons(run_gate(held, first, second))


def test_singleton_still_checks_arithmetic_and_optional_subtotal(held):
    obj = structural_plants()['singleton without subtotal (valid)']
    obj['rows'][0]['or'] = '0.45'
    assert 'ARITHMETIC:' in reasons(run_gate(held, obj))
    obj = proposal()
    obj['rows'][1]['ai'] += 1
    assert 'TOTALS: Tocilizumab.ai' in reasons(run_gate(held, obj))


@pytest.mark.parametrize('field', ['ai', 'n1i'])
def test_intervention_below_sum_is_also_refused(held, field):
    obj = proposal()
    obj['rows'][-1][field] -= 1
    assert f'TOTALS: overall.{field}:' in reasons(run_gate(held, obj))


def test_valid_multiple_sections_include_singleton_in_overall(held):
    obj = proposal()
    obj['rows'][0]['weight'] = obj['rows'][1]['weight'] = '50.00'
    obj['rows'].insert(2, dict(obj['rows'][0], agent='Other agent'))
    for k in ('ai', 'n1i'):
        obj['rows'][-1][k] *= 2
    report = run_gate(held, obj)
    assert not report['problems']
    assert [r['status'] for r in report['rows']] == ['ADMITTED'] * 3 + ['UNVERIFIABLE']
    controls = report['control_accounting'][0]
    assert controls['fields']['ci']['gap'] == 20
    assert controls['fields']['n2i']['gap'] == 100
    assert controls['candidates'][0]['basis'] == ['SAME_PRINTED_TRIAL_NAME', 'SAME_PRINTED_REGISTRATION']
    assert controls['candidates'][0]['shared_control_proven'] is False
    obj['rows'][-1]['n1i'] -= 100
    assert 'TOTALS: overall.n1i:' in reasons(run_gate(held, obj))


def test_candidate_programme_names_are_not_identity_or_deduplication():
    base = proposal()['rows'][0]
    left = dict(base, trial='PROGRAM-TOCI-1', registration='')
    right = dict(base, trial='PROGRAM-SARI-ICU', agent='Sarilumab', registration='')
    found = fg.shared_control_candidates([left, right])
    assert found[0]['basis'] == ['PROGRAMME_NAME_PATTERN_CANDIDATE_ONLY']
    assert not found[0]['shared_control_proven']
    assert not fg.shared_control_candidates([left, dict(right, trial='UNRELATED-SARI-ICU')])
    assert not fg.shared_control_candidates([left, dict(left, trial='PROGRAM-TOCI-ICU')])


def test_real_records_remain_quarantined_on_disagreement():
    paths = sorted((ROOT / 'evidence/model_calls').glob('*.json'))
    records = [ms.load_record(p) for p in paths if p.stem in {
        'mc-0ab836205e01d53bf971e57f2b779047', 'mc-972e1fe5face8e5131c4bf90bd4f5b01'}]
    assert len(records) == 2
    report = fg.gate(records, root=ROOT, replay_response=ms.replay)
    assert not any('RECORD_REFUSED:' in p or 'Siltuximab' in p for p in report['problems'])
    assert 'AGREEMENT: CORIMUNO-TOCI-ICU: ai' in reasons(report)
    assert all(r['status'] == 'REFUSED' for r in report['rows'])
    assert all(b['state'] == 'RELAYED' for b in report['bindings'])
    c = report['control_accounting'][0]
    assert c['status'] == 'UNVERIFIABLE' and c['code'] == 'SHARED_CONTROL_DEDUP'
    names = {r['trial'] for pair in c['candidates'] for r in pair['trials']}
    assert {'COV-AID', 'REMAP-CAP', 'CORIMUNO-TOCI-ICU', 'CORIMUNO-SARI-ICU'} <= names


def consensus_plants():
    cases = {}
    for name, values, models in [
        ('valid majority', [11, 10, 10], ['a', 'b', 'c']),
        ('bad arithmetic majority', [10, 11, 11], ['a', 'b', 'c']),
        ('three way split', [10, 11, 12], ['a', 'b', 'c']),
        ('same model votes once', [11, 10, 10], ['a', 'b', 'b']),
    ]:
        records = []
        for j, (value, model) in enumerate(zip(values, models)):
            obj = proposal()
            obj['rows'][0]['ai'] = value
            rec = record(obj, model)
            rec['params'] = {'replicate': j}
            rec['record_id'] = ms.record_id_of(rec)
            records.append(rec)
        cases[name] = records
    failed = record(proposal(), 'failed-reader')
    failed.update(state='RAN_ERROR', error='synthetic unavailable model', response=ms._blob(b''))
    failed['record_id'] = ms.record_id_of(failed)
    cases['failed call excluded'] = [record(proposal(), m) for m in ('a', 'b', 'c')] + [failed]
    return cases


@pytest.mark.parametrize('name', list(consensus_plants()))
def test_three_reader_plants(held, name):
    records = consensus_plants()[name]
    before = copy.deepcopy(records)
    result = fg.gate(records, root=held, replay_response=ms.replay)
    assert records == before
    assert result['rows'][0]['status'] == ('ADMITTED' if name in ('valid majority', 'failed call excluded') else 'REFUSED')
    assert not result['poolable']
    if name == 'valid majority':
        cell = result['cell_resolutions'][0]
        assert cell['status'] == 'RESOLVED' and cell['value'] == 10
        assert cell['outvoted_record_ids'] == [records[0]['record_id']]
        assert [r['value'] for r in cell['readings']] == [11, 10, 10]
    elif name == 'failed call excluded':
        assert result['excluded_records'][0]['record_id'] == records[-1]['record_id']
        assert result['excluded_records'][0]['verified']
        assert records[-1]['record_id'] not in result['rows'][0]['record_ids']
        assert not result['problems']
    else:
        assert 'DISAGREEMENT' in reasons(result)
        assert result['cell_resolutions'][0]['status'] == 'DISAGREEMENT'
        if name == 'bad arithmetic majority':
            assert any('ARITHMETIC:' in r for c in result['cell_resolutions'][0]['checks'] for r in c['reasons'])


def test_tampered_failed_call_is_not_silently_excluded(held):
    records = consensus_plants()['failed call excluded']
    records[-1]['error'] = 'tampered'
    result = fg.gate(records, root=held, replay_response=ms.replay)
    assert 'RECORD_REFUSED:' in reasons(result)
    assert not result['excluded_records'][0]['verified']
    assert result['rows'][0]['status'] == 'REFUSED'


@pytest.mark.parametrize('field,index,value,expected', [
    ('ai', 1, 11, 'TOTALS:'),
    ('n1i', 2, 101, 'TOTALS:'),
    ('weight', 0, '90.00', 'WEIGHTS:'),
    ('n2i', 0, 101, 'TABLE1_TOTAL_MISMATCH:'),
    ('trial', 0, 'Synthetic typo', 'TABLE1_'),
])
def test_majority_cannot_override_checks(held, field, index, value, expected):
    bad = proposal()
    bad['rows'][index][field] = value
    records = [record(proposal(), 'a'), record(bad, 'b'), record(bad, 'c')]
    result = fg.gate(records, root=held, replay_response=ms.replay)
    cell = result['cell_resolutions'][0]
    assert cell['status'] == 'DISAGREEMENT'
    assert any(expected in r for c in cell['checks'] for r in c['reasons'])
    assert result['rows'][index]['status'] == 'REFUSED'


def test_name_majority_requires_unique_join(held):
    bad = proposal()
    bad['rows'][0]['trial'] = 'Synthetic typo'
    result = fg.gate([record(bad, 'a'), record(proposal(), 'b'), record(proposal(), 'c')],
                     root=held, replay_response=ms.replay)
    assert result['cell_resolutions'][0]['value'] == 'Synthetic'
    assert result['rows'][0]['status'] == 'ADMITTED'
    excerpt = held / recovery_excerpt.OUTPUT
    excerpt.write_text(excerpt.read_text() + 'Synthetic | NCT00000001 | 100 | 100\n', encoding='utf-8')
    result = fg.gate([record(bad, 'a'), record(proposal(), 'b'), record(proposal(), 'c')],
                     root=held, replay_response=ms.replay)
    assert result['cell_resolutions'][0]['status'] == 'DISAGREEMENT'


@pytest.mark.parametrize('ambiguous', [False, True])
def test_alternative_with_two_votes_is_checked(held, ambiguous):
    other = proposal()
    if ambiguous:
        other['rows'][1]['or'] = '0.45'  # subgroup effects are not recomputed
    else:
        other['rows'][0]['ai'] = 11
    result = fg.gate([record(proposal(), 'a'), record(proposal(), 'b'),
                      record(other, 'c'), record(other, 'd')], root=held, replay_response=ms.replay)
    cell = result['cell_resolutions'][0]
    assert len(cell['candidates']) == 2
    assert cell['status'] == ('DISAGREEMENT' if ambiguous else 'RESOLVED')
    assert len(cell['passing_values']) == (2 if ambiguous else 1)


def test_duplicate_model_cannot_manufacture_support_with_three_models(held):
    records = consensus_plants()['same model votes once']
    third = proposal()
    third['rows'][0]['ai'] = 12
    result = fg.gate(records + [record(third, 'c')], root=held, replay_response=ms.replay)
    assert result['cell_resolutions'][0]['candidates'] == []
    assert result['rows'][0]['status'] == 'REFUSED'


def test_three_real_records_resolve_only_checked_cells():
    records = [ms.load_record(p) for p in sorted((ROOT / 'evidence/model_calls').glob('*.json'))
               if ms.load_record(p).get('caller', {}).get('lane') == 'REACTFIG'
               and ms.load_record(p)['model']['provider'] == 'openai']  # the same-provider quorum alone
    result = fg.gate(records, root=ROOT, replay_response=ms.replay)
    assert len(result['excluded_records']) == 2
    assert all(r['verified'] for r in result['excluded_records'])
    assert not result['problems']
    assert {(c['field'], c['value']) for c in result['cell_resolutions']} == {('ai', 8), ('trial', 'REMDACTA')}
    assert all(c['status'] == 'RESOLVED' for c in result['cell_resolutions'])
    assert all(b['state'] == 'MODEL_TRANSCRIBED_CHECKED' and not b['poolable']
               and b['population_equivalence'] == 'NOT_ADJUDICATED' for b in result['bindings'])
    assert len(result['bindings']) == 6
    assert sum(r['status'] == 'REFUSED' for r in result['rows']) == 5
    assert result['rows'][-1]['status'] == 'UNVERIFIABLE'
    c = census(ROOT)
    assert c['rules']['cell_resolved']['n'] == 2
    # REACTFIG records, by kind: 5 openai calls (3 RAN_OK, 2 RAN_ERROR) + 1 recorded anthropic reading (RAN_OK)
    assert c['rules']['failed_calls_excluded']['n_of_N'] == '2 of 6'
