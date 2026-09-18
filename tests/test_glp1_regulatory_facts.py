"""Offline extraction contract, including deliberate corruption plants."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts import glp1_regulatory_facts as facts


def artifact():
    return json.loads(facts.read_text(facts.ROOT / facts.OUTPUT))


def test_cli_regenerates_byte_identically(tmp_path):
    target = tmp_path / 'regenerated.json'
    subprocess.run([sys.executable, str(facts.ROOT / 'scripts/glp1_regulatory_facts.py'),
                    '--output', str(target)], cwd=facts.ROOT, check=True, capture_output=True)
    assert target.read_bytes() == (facts.ROOT / facts.OUTPUT).read_bytes()


def test_hashes_and_index_admission():
    for fact in artifact()['facts']:
        assert fact['document_sha256'] == facts.sha(facts.ROOT / fact['document'])
        assert fact['text_sha256'] == facts.sha(facts.ROOT / fact['text_file'])
        meta = facts.provenance(facts.ROOT, fact['trial'])
        assert fact['provenance_check'] == meta['provenance_check']
        if meta['provenance_check']['state'] != 'MATCH':
            assert fact['state'] == 'NOT_LOCATED'
            assert 'effect' not in fact and 'counts' not in fact
        else:
            records = json.loads(facts.read_text(facts.ROOT / facts.INDEX))['sources']
            record = next(r for r in records if r['source_id'] == fact['source_id'])
            assert fact['document_sha256'] == record['document_sha256']
            assert fact['text_sha256'] == record['extracted_text_sha256']


def test_spans_and_numbers_round_trip():
    data = artifact()
    facts.validate(data)
    for fact in data['facts']:
        text = facts.read_text(facts.ROOT / fact['text_file'])
        raw = (facts.ROOT / fact['text_file']).read_bytes()
        def walk(node):
            if isinstance(node, dict):
                if 'char_start' in node:
                    assert text[node['char_start']:node['char_end']] == node['text']
                    assert raw[node['byte_start']:node['byte_end']].decode('utf-8') == node['text']
                if 'effect' in node:
                    effect, counts = facts.parse_result(fact['trial'], node['result_span']['text'])
                    assert (effect, counts) == (node['effect'], node['counts'])
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)
        walk(fact)
        if fact['state'] == 'LOCATED':
            effect, counts = facts.parse_result(fact['trial'], fact['result_span']['text'])
            assert effect == fact['effect'] and counts == fact['counts']


@pytest.mark.parametrize('plant', ['one_digit', 'no_result_span'])
def test_pre_fix_plants_refused_on_disk(tmp_path, plant):
    data = artifact()
    fact = next(f for f in data['facts'] if f['state'] == 'LOCATED')
    if plant == 'one_digit':
        original = str(fact['effect']['value'])
        replacement = original[:-1] + str((int(original[-1]) + 1) % 10)
        assert sum(a != b for a, b in zip(original, replacement)) == 1
        fact['effect']['value'] = float(replacement)
        message = 'stored numeric value differs from parsed result_span'
    else:
        del fact['result_span']
        message = 'numeric value without result_span'
    scratch = tmp_path / (plant + '.json')
    scratch.write_bytes(facts.serialize(data))
    # Run the real validator against the still-corrupt file, before any repair.
    result = subprocess.run([sys.executable, str(facts.ROOT / 'scripts/glp1_regulatory_facts.py'),
                             '--validate', str(scratch)], cwd=facts.ROOT, capture_output=True, text=True)
    assert result.returncode != 0
    assert message in result.stderr
    print(f'PLANT {plant}: pre-fix CLI exit={result.returncode}; {message}')


def test_synthetic_caption_without_target_row():
    source = artifact()['facts'][0]
    synthetic = source['table']['text'] + '\nMACE Type\nNo target row exists.\n'
    result = facts.locate('FREEDOM-CVO', synthetic)
    assert result['state'] == 'NOT_LOCATED'
    assert 'effect' not in result and 'counts' not in result


def test_flow_binds_cv_row_not_primary_kidney_or_cv_death():
    fact = artifact()['facts'][1]
    located = facts.locate('FLOW', facts.read_text(facts.ROOT / fact['text_file']))
    assert located['state'] == 'LOCATED'
    assert located['components'] == ['cardiovascular death', 'myocardial infarction', 'stroke']
    match = facts.FLOW_ROW.search(located['result_span']['text'])
    assert located['effect']['value'] == float(match['hr'])
    assert located['counts']['intervention']['events'] == int(match['ie'])
    assert located['counts']['comparator']['events'] == int(match['ce'])
    assert 'primary composite endpoint' in located['primary_endpoint_context_span']['text']
    assert located['nct'] == located['nct_span']['text']
    assert located['analysis_set_span'] == 'NOT_STATED_IN_SPAN'


def test_conflicting_table_candidates_are_not_selected():
    fact = artifact()['facts'][0]
    table = fact['table']['text'] + fact['result_span']['text']
    old = facts.FREEDOM_ROW.search(table)['hr']
    new = old[:-1] + str((int(old[-1]) + 1) % 10)
    changed = table.replace(old, new)
    located = facts.locate('FREEDOM-CVO', table + '\n' + changed)
    assert located['state'] == 'CONFLICT'
    assert len(located['conflicts']) == 2
    assert 'effect' not in located


def test_duplicate_identical_tables_are_ambiguous():
    fact = artifact()['facts'][0]
    table = fact['table']['text'] + fact['result_span']['text']
    assert facts.locate('FREEDOM-CVO', table + '\n' + table)['state'] == 'AMBIGUOUS'


def test_conflicting_rows_within_one_table_are_both_preserved():
    fact = artifact()['facts'][0]
    table = fact['table']['text'] + fact['result_span']['text']
    row = facts.FREEDOM_ROW.search(table)
    old = row['hr']
    new = old[:-1] + str((int(old[-1]) + 1) % 10)
    located = facts.locate('FREEDOM-CVO', table + '\n' + row.group().replace(old, new))
    assert located['state'] == 'CONFLICT'
    assert len(located['conflicts']) == 2
    for candidate in located['conflicts']:
        effect, counts = facts.parse_result('FREEDOM-CVO', candidate['result_span']['text'])
        assert effect == candidate['effect'] and counts == candidate['counts']


@pytest.mark.parametrize('trial', ['FREEDOM-CVO', 'ELIXA'])
def test_hash_mismatch_refuses_values(tmp_path, trial):
    records = json.loads(facts.read_text(facts.ROOT / facts.INDEX))
    for record in records['sources']:
        if (record.get('held', {}).get('held_in_tree') or '').endswith(facts.SOURCES[trial]):
            record['document_sha256'] = 'corrupted'
    index = tmp_path / facts.INDEX
    index.parent.mkdir(parents=True)
    index.write_bytes(facts.serialize(records))
    for fact in artifact()['facts']:
        for key in ('document', 'text_file'):
            target = tmp_path / fact[key]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((facts.ROOT / fact[key]).read_bytes())
    result = next(f for f in facts.build(tmp_path)['facts'] if f['trial'] == trial)
    assert result['provenance_check']['state'] == 'HASH_OR_PATH_MISMATCH'
    assert result['state'] == 'NOT_LOCATED' and 'effect' not in result
    def check(node):
        if isinstance(node, dict):
            assert 'effect' not in node and 'counts' not in node
            for value in node.values():
                check(value)
        elif isinstance(node, list):
            for value in node:
                check(value)
    check(result)


def test_wrong_definition_rejected():
    data = artifact()
    data['facts'][0]['definition_span'] = copy.deepcopy(data['facts'][0]['table'])
    with pytest.raises(ValueError, match='definition components mismatch'):
        facts.validate(data)


def test_elixa_conflict_and_separate_analysis():
    fact = next(f for f in artifact()['facts'] if f['trial'] == 'ELIXA')
    assert fact['state'] == 'CONFLICT' and 'effect' not in fact
    assert [c['kind'] for c in fact['conflicts']] == ['table', 'text']
    assert facts.differences(*fact['conflicts']) == fact['comparison']['differing_fields']
    assert fact['comparison']['differing_fields']
    assert fact['components'] == ['cardiovascular death', 'myocardial infarction', 'stroke']
    assert 'Secondary endpoints' in fact['endpoint_role_span']['text']
    assert len(fact['other_analyses']) == 1
    assert fact['other_analyses'][0]['analysis_label_span']['text'] == 'on-treatment'
    assert 'last injection' in fact['other_analyses'][0]['censoring_rule_span']['text']


@pytest.mark.parametrize('plant', ['conflict_effect', 'identical_conflicts', 'table_digit', 'text_digit'])
def test_elixa_pre_fix_plants(tmp_path, plant):
    data = artifact()
    fact = next(f for f in data['facts'] if f['trial'] == 'ELIXA')
    if plant == 'conflict_effect':
        fact['effect'] = copy.deepcopy(fact['conflicts'][0]['effect'])
        message = 'CONFLICT must omit top-level effect'
    elif plant == 'identical_conflicts':
        fact['conflicts'][1] = copy.deepcopy(fact['conflicts'][0])
        message = 'CONFLICT requires differing parsed values'
    else:
        candidate = fact['conflicts'][0 if plant == 'table_digit' else 1]
        old = str(candidate['effect']['ci_high'])
        new = old[:-1] + str((int(old[-1])+1) % 10)
        assert sum(a != b for a, b in zip(old, new)) == 1
        candidate['effect']['ci_high'] = float(new)
        message = 'stored numeric value differs from parsed result_span'
    scratch = tmp_path / (plant + '.json')
    scratch.write_bytes(facts.serialize(data))
    result = subprocess.run([sys.executable, str(facts.ROOT / 'scripts/glp1_regulatory_facts.py'),
                             '--validate', str(scratch)], cwd=facts.ROOT, capture_output=True, text=True)
    assert result.returncode != 0 and message in result.stderr
    print(f'PLANT {plant}: pre-fix CLI exit={result.returncode}; {message}')


def test_elixa_agreeing_passages_are_located():
    fact = next(f for f in artifact()['facts'] if f['trial'] == 'ELIXA')
    text = facts.read_text(facts.ROOT / fact['text_file'])
    passage = fact['conflicts'][1]['result_span']
    parsed = facts.ELIXA_TEXT.fullmatch(passage['text'])
    table = fact['conflicts'][0]['effect']
    amended = passage['text']
    for key, field in [('hi', 'ci_high'), ('lo', 'ci_low')]:
        amended = amended[:parsed.start(key)] + str(table[field]) + amended[parsed.end(key):]
    located = facts.locate('ELIXA', text[:passage['char_start']] + amended + text[passage['char_end']:])
    assert located['state'] == 'LOCATED'
    assert len(located['corroborating']) == 2 and 'conflicts' not in located
