"""Synthetic PLANTS only; their values are never corpus evidence."""
from copy import deepcopy
import json
from pathlib import Path

import pytest
from harness import disperse2_gate as g, table_rows
from reproducible_ai import model_source as ms

TEXT = 'DISPERSE2 treated 400 male and 200 female patients.'
CAPTION = 'Table 1. DISPERSE-2 ICAC clinical endpoints at Week 4 and overall'
SHA = g.sha(b'synthetic image only')
CONTEXT = CAPTION + '\nSynthetic fixture, not held evidence.'
IMAGES = {SHA: {'captions': [CAPTION], 'text': CONTEXT, 'study': 'DISPERSE-2', 'path': 'synthetic-image'}}


def proposal():
    rows = [dict(outcome_definition='ICAC major bleeding', arm=a, n=n // 10, N=n, percent='10.0',
                 printed_cell=f'{n // 10} (10.0)', footnote_markers='', timepoint='4 weeks', percent_kind='CRUDE', count_basis='PRINTED_PATIENTS')
            for a, n in zip(g.ARMS, (100, 200, 300))]
    return {'trial': 'DISPERSE-2', 'provenance': 'IMAGE_TRANSCRIPTION', 'tables': [
        {'table_id': 'Table 1', 'caption': CAPTION, 'footnotes': CONTEXT, 'image_sha256': SHA,
         'arm_sizes': dict(zip(g.ARMS, (100, 200, 300))),
         'arm_headers': {a: f'{a} n={n}' for a, n in zip(g.ARMS, (100, 200, 300))},
         'printed_footnotes': '', 'rows': rows}]}


def records(a=None, b=None, c=None):
    a = a if a is not None else proposal()
    b = b if b is not None else deepcopy(a)
    c = c if c is not None else deepcopy(a)
    return [ms.build_record(prompt_bytes=b'Independent synthetic plant', response_bytes=ms.canonical(p),
             model={'id_requested': f'synthetic-{i}', 'id_reported': f'synthetic-{i}', 'provider': 'test'},
             params={'independent_run_id': str(i), 'image_inputs': [{'sha256': SHA}]},
             not_controllable=[], client={'name': 'synthetic-test-only'},
             request_utc=f'2000-01-01T00:00:0{i}Z', response_utc=f'2000-01-01T00:00:0{i}Z',
             caller={'file': __file__, 'line': '1', 'purpose': 'synthetic PLANT, not model call'},
             input_digests=[{'ref': 'synthetic-image', 'sha256': SHA, 'media_type': 'image/png'}]) for i, p in enumerate((a, b, c))]


def gate_records(records, text=TEXT, images=IMAGES, **kwargs):
    return g.gate_records(records, text, images, replay_response=ms.replay, record_problems=ms.record_problems, **kwargs)


def baseline(p):
    """Feed the SAME row values to the existing typed text-table parser."""
    table = p['tables'][0]
    rows = table['rows']
    row = {'label': rows[0]['outcome_definition'], 'cells': [f"{r['n']} ({r['percent']})" for r in rows]}
    base = {'caption': table['caption'], 'comments': [table['footnotes']],
            'footnotes': [table['footnotes']],
            'header': ['Outcome'] + [f"{r['arm']} patients N={r['N']}" for r in rows]}
    return table_rows.typed(row, base)


def plant(rule):
    p = proposal()
    row = p['tables'][0]['rows'][0]
    if rule == 'ARM_N':
        row['N'] += 1
    elif rule == 'PERCENT':
        row['percent'] = '99.9'
    elif rule == 'KM_COUNT':
        row['percent_kind'] = 'KM'
        p['tables'][0]['printed_footnotes'] += ' Kaplan-Meier percentage.'
    elif rule == 'SHARED_CONTROL':
        p['tables'][0]['rows'].append(deepcopy(p['tables'][0]['rows'][-1]))
    return p


@pytest.mark.parametrize('rule', ['ARM_N', 'PERCENT', 'KM_COUNT', 'SHARED_CONTROL'])
def test_positive_plants(rule):
    p = plant(rule)
    base = baseline(p)
    assert len(base['arms']) == len(p['tables'][0]['rows'])  # base parser retains defect
    result = gate_records(records(p), TEXT, IMAGES)
    assert result['status'] == 'REFUSED' and result['reason'].startswith(rule + ':')
    assert result['rows'] == []


def test_agreement_plant():
    a, b = proposal(), proposal()
    b['tables'][0]['rows'][0]['percent'] = '10.00'
    c = deepcopy(a)
    c['tables'][0]['rows'][0]['percent'] = '10.000'
    pair = records(a, b, c)
    assert [json.loads(ms.replay(r)) for r in pair] == [a, b, c]  # base replays both, no cross-call check
    assert gate_records(pair, TEXT, IMAGES)['reason'].startswith('AGREEMENT:')


def test_negative_all_rules_and_typed_rows():
    result = gate_records(records(), TEXT, IMAGES)
    assert result['status'] == 'ADMIT' and len(result['rows']) == 3
    assert result['pool_admission'] is False
    assert result['rows'][0]['variant_flags'] == ['ICAC', 'MAJOR']
    assert sum(r['arm'] == 'clopidogrel' for r in result['rows']) == 1


def test_same_record_and_missing_record():
    pair = records()
    for bad in ([pair[0], pair[0]], [pair[0]], []):
        assert gate_records(bad, TEXT, IMAGES)['reason'].startswith('AGREEMENT:')


def test_tamper_and_image_attachment():
    pair = records()
    pair[0]['params']['independent_run_id'] = 'tamper'
    assert gate_records(pair, TEXT, IMAGES)['status'] == 'REFUSED'
    pair = records()
    pair[0]['input_digests'][0]['media_type'] = 'text/plain'
    pair[0]['record_id'] = ms.record_id_of(pair[0])
    assert gate_records(pair, TEXT, IMAGES)['reason'].startswith('IMAGE_SOURCE:')
    assert gate_records(records(), TEXT, {})['reason'].startswith('IMAGE_SOURCE:')


def test_total_and_across_tables():
    p = proposal()
    p['tables'][0]['arm_sizes']['90 mg bd'] = 101
    assert gate_records(records(p), TEXT, IMAGES)['reason'].startswith('ARM_N:')
    p = proposal()
    second = deepcopy(p['tables'][0])
    second['arm_sizes']['90 mg bd'] += 1
    second['arm_sizes']['180 mg bd'] -= 1
    second['arm_headers'] = {a: f'{a} n={n}' for a, n in second['arm_sizes'].items()}
    p['tables'].append(second)
    assert 'inconsistent across' in gate_records(records(p), TEXT, IMAGES)['reason']


def test_printed_N_and_missing_total():
    text = TEXT + '\nDISPERSE-2 90 mg bd (N=99)'
    assert 'printed text N' in gate_records(records(), text, IMAGES)['reason']
    assert gate_records(records(), 'No treated total', IMAGES)['reason'].startswith('ARM_N:')


@pytest.mark.parametrize('field,value', [('n', True), ('n', -1), ('N', 100.0), ('percent', 10.0),
                                      ('percent', 'NaN'), ('timepoint', 'unknown'), ('count_basis', 'NOT_PRINTED')])
def test_bad_types(field, value):
    p = proposal()
    p['tables'][0]['rows'][0][field] = value
    assert gate_records(records(p), TEXT, IMAGES)['status'] == 'REFUSED'


def test_relayed_overall_and_bleeding_definition():
    p = proposal()
    p['provenance'] = 'RELAYED'
    assert gate_records(records(p), TEXT, IMAGES)['reason'].startswith('RELAYED:')
    p = proposal()
    for row in p['tables'][0]['rows']:
        row['timepoint'] = 'overall'
    result = gate_records(records(p), TEXT, IMAGES)
    assert result['status'] == 'ADMIT'
    assert 'OVERALL_NOT_FIXED_12_WEEKS' in result['rows'][0]['variant_flags']
    p['tables'][0]['rows'][0]['outcome_definition'] = 'Major bleeding'
    assert gate_records(records(p), TEXT, IMAGES)['reason'].startswith('DEFINITION:')


def test_wrong_study_and_footnotes():
    images = deepcopy(IMAGES)
    images[SHA]['study'] = 'DISPERSE'
    assert gate_records(records(), TEXT, images)['reason'].startswith('STUDY_IDENTITY:')
    # A caption that is not the held caption still refuses the image binding.
    p = proposal()
    p['tables'][0]['caption'] = 'Table 99. Something else'
    assert gate_records(records(p), TEXT, IMAGES)['reason'].startswith('IMAGE_SOURCE:')
    # The page context is the HELD text, not the model's echo of it: an omitted or truncated echo changes nothing,
    # and the post-lock caveat still comes from the held text.
    p = proposal()
    p['tables'][0]['footnotes'] = ''
    held = gate_records(records(proposal()), TEXT, IMAGES)
    echo_dropped = gate_records(records(p), TEXT, IMAGES)
    assert echo_dropped['status'] == held['status']
    assert [r.get('variant_flags') for r in echo_dropped.get('rows', [])] == [r.get('variant_flags') for r in held.get('rows', [])]


def test_shared_control_whitespace_and_distinct_outcomes():
    p = plant('SHARED_CONTROL')
    p['tables'][0]['rows'][-1]['outcome_definition'] = ' ICAC  major bleeding '
    assert gate_records(records(p), TEXT, IMAGES)['reason'].startswith('SHARED_CONTROL:')
    p = proposal()
    for row in deepcopy(p['tables'][0]['rows']):
        row['outcome_definition'] = 'All cause death'
        p['tables'][0]['rows'].append(row)
    assert gate_records(records(p), TEXT, IMAGES)['status'] == 'ADMIT'


@pytest.mark.parametrize('percent,admitted', [('0.5', True), ('1', True), ('0', False), ('0.50', True)])
def test_printed_precision_rounding(percent, admitted):
    p = proposal()
    row = p['tables'][0]['rows'][1]
    row['n'], row['percent'] = 1, percent
    row['printed_cell'] = f'1 ({percent})'
    assert (gate_records(records(p), TEXT, IMAGES)['status'] == 'ADMIT') == admitted


def test_held_total_and_manifest():
    root = Path(__file__).resolve().parents[1]
    text, images = g.held_inputs(root)
    evidence = g.text_evidence(text)
    assert evidence['total'] == sum(map(int, __import__('re').findall(r'\d+', evidence['sex_spans'][0])[1:]))
    assert images


def test_prepare_schema_and_offline_api_refusal():
    import subprocess
    import sys
    from scripts.disperse2_figure_proposal import SCHEMA
    assert SCHEMA['additionalProperties'] is False
    result = subprocess.run([sys.executable, 'scripts/disperse2_figure_proposal.py', '--call'], capture_output=True, text=True)
    assert result.returncode == 2 and '--call requires --image and --model' in result.stderr


def test_majority_cannot_override_arithmetic():
    bad, correct = plant('PERCENT'), proposal()
    result = gate_records(records(bad, bad, correct))
    assert result['status'] == 'REFUSED' and result['reason'].startswith('PERCENT:')
    assert gate_records(records(correct, correct, bad))['status'] == 'ADMIT'


def test_cell_votes_not_whole_proposal_votes():
    a, b, c = proposal(), proposal(), proposal()
    a['tables'][0]['rows'][0]['n'] += 1
    b['tables'][0]['rows'][1]['n'] += 1
    c['tables'][0]['rows'][2]['n'] += 1
    result = gate_records(records(a, b, c))
    assert result['status'] == 'ADMIT'
    assert [r['n'] for r in result['rows']] == [10, 20, 30]


def test_duplicate_model_counts_once_and_conflicting_repeat_refuses():
    rs = records()
    rs[2]['model'] = deepcopy(rs[1]['model'])
    rs[2]['record_id'] = ms.record_id_of(rs[2])
    assert 'three distinct model' in gate_records(rs)['reason']
    rs = records()
    result = gate_records(rs + [rs[0]])
    assert result['status'] == 'ADMIT' and len(result['model_ids']) == 3
    assert len(result['duplicate_models']) == 1
    dissent = records(plant('PERCENT'))[0]
    assert 'duplicate proposals conflict' in gate_records(rs + [dissent])['reason']


def test_error_listed_excluded_never_a_third_vote():
    rs = records()
    error = deepcopy(rs[-1])
    error['state'], error['error'] = 'RAN_ERROR', 'synthetic failure'
    error['record_id'] = ms.record_id_of(error)
    result = gate_records(rs[:2] + [error])
    assert result['status'] == 'REFUSED' and result['excluded_records'][0]['state'] == 'RAN_ERROR'
    result = gate_records(rs + [error])
    assert result['status'] == 'ADMIT' and len(result['excluded_records']) == 1


def test_population_conflict_and_mace_typing():
    p = proposal()
    for row in p['tables'][0]['rows']:
        row['outcome_definition'] = 'CV death / MI (excl silent) / stroke'
        row['timepoint'] = 'overall study'
    p['tables'][0]['printed_footnotes'] = 'Events after post database lock are excluded.'
    text = 'DISPERSE2 treated 390 male and 200 female patients. 600 were randomized and 590 (98%) patients received at least one dose'
    target = g.target_from_topic(Path(__file__).resolve().parents[1])
    result = gate_records(records(p), text, target=target)
    assert result['status'] == 'ADMIT'
    for row in result['rows']:
        assert row['population'] == dict(status='NOT_ADJUDICATED', randomized_total=600, treated_total=590, header_total=600, conflict=True)
        assert row['mace_candidate'] and row['component_note'] == 'MI excludes silent MI'
        assert set(row['component_set']) == set(target['components'])
        assert row['POOLABLE'] is False and row['window'] == 'overall study'
        assert 'POST_LOCK_EVENTS_EXCLUDED' in row['flags']
        assert 'RANDOMIZED_TREATED_DENOMINATOR_CONFLICT' in row['flags']
    for row in p['tables'][0]['rows']:
        row['outcome_definition'] += ' / SRI'
    result = gate_records(records(p), text, target=target)
    assert result['status'] == 'ADMIT' and not any(r['mace_candidate'] for r in result['rows'])
    assert all('SRI' in r['component_typing']['untyped'] for r in result['rows'])


def test_header_cell_and_marker_plants():
    p = proposal()
    p['tables'][0]['arm_headers']['90 mg bd'] = '90 mg bd n=101'
    assert gate_records(records(p))['reason'].startswith('ARM_N:')
    p = proposal()
    p['tables'][0]['rows'][0]['printed_cell'] = '11 (10.0)'
    assert gate_records(records(p))['reason'].startswith('PERCENT:')
    p = proposal()
    p['tables'][0]['rows'][0]['printed_cell'] += '*'
    p['tables'][0]['rows'][0]['footnote_markers'] = '*'
    assert gate_records(records(p))['status'] == 'ADMIT'


def test_live_call_wiring_offline_stub(monkeypatch, capsys):
    from scripts import disperse2_figure_proposal as cli
    from reproducible_ai import model_call_live
    root = Path(__file__).resolve().parents[1]
    path = root / g.IMAGE_DIR / 'page-0516-image-01-rendered.png'
    image_sha = g.sha(path.read_bytes())
    images = {image_sha: dict(path=path.relative_to(root).as_posix(), study='DISPERSE-2', text='context', captions=['caption'])}
    monkeypatch.setattr(g, 'held_inputs', lambda root: ('text', images))
    def call(prompt, **kw):
        assert kw['images'] == (path.resolve(),) and kw['model'] == 'synthetic-offline'
        assert kw['image_root'] == root and image_sha.encode() in prompt
        assert 'arm_headers' in kw['schema']['properties']['tables']['items']['properties']
        assert kw['caller']['lane'] == 'DISP2CALL'
        return {'state': 'RAN_OK'}
    monkeypatch.setattr(model_call_live, 'call', call)
    monkeypatch.setattr(ms, 'write_record', lambda rec, directory: directory / 'synthetic.json')
    assert cli.main(['--call', '--image', str(path), '--model', 'synthetic-offline']) == 0
    assert 'evidence/model_calls/synthetic.json' in capsys.readouterr().out


def test_prompt_pin_and_unresolved_cells_refuse():
    rs = records()
    rs[0]['model']['id_reported'] = 'wrong'
    rs[0]['record_id'] = ms.record_id_of(rs[0])
    assert 'model pin mismatch' in gate_records(rs)['reason']
    with pytest.raises(ValueError, match='no unique value'):
        g.consensus([1, 1, 2, 2])
    with pytest.raises(ValueError, match='inventory'):
        g.consensus([[1], [1, 2], [1]])


def test_batch_headers_and_negative_distinct_table():
    first = records()
    other_sha = g.sha(b'synthetic second image')
    images = {**IMAGES, other_sha: {**IMAGES[SHA], 'path': 'synthetic-other'}}
    p = proposal()
    p['tables'][0]['table_id'] = 'Table 2'
    p['tables'][0]['caption'] = CAPTION.replace('Table 1.', 'Table 2.')
    images[other_sha]['captions'] = [p['tables'][0]['caption']]
    p['tables'][0]['image_sha256'] = other_sha
    for row in p['tables'][0]['rows']:
        row['outcome_definition'] = 'Stroke'
    def second_records(p):
        rs = records(p)
        for r in rs:
            r['input_digests'] = [{'sha256': other_sha, 'ref': 'synthetic-other', 'media_type': 'image/png'}]
            r['record_id'] = ms.record_id_of(r)
        return rs
    def batch(p):
        return g.gate_batches(first + second_records(p), TEXT, images,
                              replay_response=ms.replay, record_problems=ms.record_problems)
    assert batch(p)['status'] == 'ADMIT'
    # Swap two valid headers, keeping their totals and percentages internally valid.
    table = p['tables'][0]
    table['arm_sizes']['90 mg bd'], table['arm_sizes']['180 mg bd'] = 200, 100
    table['arm_headers'] = {a: f'{a} n={n}' for a, n in table['arm_sizes'].items()}
    for row in table['rows']:
        row['N'] = table['arm_sizes'][row['arm']]
        row['n'] = row['N'] // 10
        row['printed_cell'] = f"{row['n']} (10.0)"
    assert 'inconsistent across recorded tables' in batch(p)['reason']


def test_no_validator_and_broken_structure_fail_closed():
    assert g.gate_records(records(), TEXT, IMAGES)['status'] == 'REFUSED'
    p = proposal()
    p['tables'] = None
    result = gate_records(records(p))
    assert result['status'] == 'REFUSED' and result['reason'].startswith('SCHEMA:')


def test_census_includes_all_topics_and_unexamined_rules():
    from scripts.disperse2_figure_proposal import census
    root = Path(__file__).resolve().parents[1]
    result = census(root)
    assert result['topics_examined'] == len(list((root / 'topics').glob('*.json')))
    assert len(result['topic_names']) == result['topics_examined']
    for rule in g.RULES + ('ACROSS_TABLE_ARM_N', 'RANDOMIZED_TREATED_DENOMINATOR_CONFLICT', 'POST_LOCK_EVENTS_EXCLUDED', 'MACE_CANDIDATE', 'KEY_ALIGNMENT', 'PERCENT_NORMALIZATION', 'HEADER_N_FALLBACK'):
        assert rule in result['rules']
        item = result['rules'][rule]
        assert item['n'] == len(item['items'])
        assert item['n_of_N'] == f"{item['n']} of {item['N']}"


# DISP2FIX plants: synthetic inputs, never corpus evidence.
def test_keyed_permutation_and_outvoted_audit():
    import itertools
    a, b, c = proposal(), proposal(), proposal()
    expected = gate_records(records(a, b, c))['rows']
    for order in itertools.permutations(range(3)):
        b['tables'][0]['rows'] = [deepcopy(a['tables'][0]['rows'][i]) for i in order]
        for other_order in itertools.permutations(range(3)):
            c['tables'][0]['rows'] = [deepcopy(a['tables'][0]['rows'][i]) for i in other_order]
            result = gate_records(records(a, b, c))
            assert result['status'] == 'ADMIT' and result['rows'] == expected
    for p, n in zip((a, b, c), (11, 12, 13)):
        next(r for r in p['tables'][0]['rows'] if r['arm'] == '90 mg bd')['n'] = n
    result = gate_records(records(a, b, c))
    assert result['status'] == 'REFUSED' and '90 mg bd/4 weeks/n' in result['reason']
    assert 'no unique value' in result['reason']


def test_missing_key_quorum_and_duplicate_key():
    a, b, c = proposal(), proposal(), proposal()
    c['tables'][0]['rows'].pop(0)
    assert gate_records(records(a, b, c))['status'] == 'ADMIT'
    b['tables'][0]['rows'].pop(0)
    result = gate_records(records(a, b, c))
    assert '90 mg bd/4 weeks' in result['reason'] and 'fewer than two' in result['reason']
    a = proposal()
    a['tables'][0]['rows'].append(deepcopy(a['tables'][0]['rows'][0]))
    assert gate_records(records(a))['reason'].startswith('DUPLICATE_ARM:')


def test_percent_suffix_normalization_precision_and_cell_binding():
    a, b, c = proposal(), proposal(), proposal()
    for p in (b, c):
        p['tables'][0]['rows'][0]['percent'] = ' 10.0% '
    result = gate_records(records(a, b, c))
    assert result['status'] == 'ADMIT'
    assert len(result['agreement_audit']['normalizations']) == 2
    for p, pct in zip((a, b, c), ('4.5%', '4.6', '4.7')):
        p['tables'][0]['rows'][0]['percent'] = pct
    assert gate_records(records(a, b, c))['reason'].startswith('AGREEMENT:')
    # Only two readers carry this key: different numeric readings cannot agree.
    c['tables'][0]['rows'].pop(0)
    assert gate_records(records(a, b, c))['reason'].startswith('AGREEMENT:')
    for pct in ('10.0%%', '10.00%', '10.1%'):
        p = proposal()
        p['tables'][0]['rows'][0]['percent'] = pct
        assert gate_records(records(p))['reason'].startswith('PERCENT:')
    # Majority keeps its authority; malformed minority is explicitly outvoted.
    result = gate_records(records(proposal(), proposal(), p))
    assert result['status'] == 'ADMIT'
    assert any(d['readings'][0]['value'] == '10.1' for d in result['agreement_audit']['outvoted'])


def test_null_N_requires_header_quorum_and_held_check():
    a, b, c = proposal(), proposal(), proposal()
    for p in (b, c):
        p['tables'][0]['rows'][0]['N'] = None
    result = gate_records(records(a, b, c))
    assert result['status'] == 'ADMIT'
    assert result['rows'][0]['N'] == 100
    assert len(result['agreement_audit']['normalizations']) == 2
    for p, n in zip((a, b, c), (100, 101, 102)):
        p['tables'][0]['rows'][0]['N'] = None
        p['tables'][0]['arm_sizes']['90 mg bd'] = n
        p['tables'][0]['arm_headers']['90 mg bd'] = f'90 mg bd n={n}'
    assert gate_records(records(a, b, c))['reason'].startswith('AGREEMENT:')
    p = proposal()
    p['tables'][0]['rows'][0]['N'] = None
    assert 'held total/printed text check' in gate_records(records(p), TEXT + '\nDISPERSE-2 90 mg bd (N=99)')['reason']
    for arm in g.ARMS:
        p['tables'][0]['arm_headers'][arm] = arm  # Missing printed n even with typed arm sizes.
    assert gate_records(records(p))['status'] == 'REFUSED'


def test_label_key_preserves_components_and_raw_footnote_marks():
    a, b, c = proposal(), proposal(), proposal()
    for p in (a, c):
        p['tables'][0]['rows'][0]['outcome_definition'] += '\u1d9c'
    result = gate_records(records(a, b, c))
    assert result['status'] == 'ADMIT'
    assert result['rows'][0]['outcome_label_verbatim'].endswith('\u1d9c')
    assert any(d['path'].endswith('/outcome_definition') for d in result['agreement_audit']['outvoted'])
    c['tables'][0]['rows'][0]['outcome_definition'] += ' / stroke'
    assert gate_records(records(a, b, c))['reason'].startswith('AGREEMENT:')


def test_real_records_order_invariance_and_audit():
    root = Path(__file__).resolve().parents[1]
    rs = [ms.load_record(root / p) for p in (root / 'evidence/model_calls/disperse2_table_records.txt').read_text().splitlines()]
    text, images = g.held_inputs(root)
    kwargs = dict(replay_response=ms.replay, record_problems=ms.record_problems, target=g.target_from_topic(root))
    result = g.gate_batches(rs, text, images, **kwargs)
    assert result['status'] == 'ADMIT', result.get('reason')
    assert result['pool_admission'] is False
    # Synthetic replay adapter permutes parsed rows but leaves held records untouched.
    def permuted(record):
        claim = json.loads(ms.replay(record))
        for table in claim['tables']:
            table['rows'].reverse()
        return json.dumps(claim)
    kwargs['replay_response'] = permuted
    reordered = g.gate_batches(list(reversed(rs)), text, images, **kwargs)
    assert reordered['status'] == result['status'] and reordered['rows'] == result['rows']
    candidates = [r for r in result['rows'] if r['mace_candidate']]
    assert len(candidates) == len(g.ARMS)
    assert all(r['POOLABLE'] is False and r['population']['conflict'] for r in candidates)
