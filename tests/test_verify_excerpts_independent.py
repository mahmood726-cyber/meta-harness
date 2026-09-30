"""Plants modify only pytest tmp_path, never evidence/."""
from pathlib import Path
import re

import pytest

from scripts import verify_excerpts_independent as second


@pytest.fixture(scope='module')
def models():
    return [second.source_model(second.ROOT, i) for i in range(len(second.FILES))]


def planted(tmp_path, index, transform):
    original = second.ROOT / second.BASE / 'excerpts' / second.FILES[index]
    target = tmp_path / original.name
    target.write_text(transform(original.read_text(encoding='utf-8')), encoding='utf-8')
    return target


@pytest.mark.parametrize('index', range(4))
def test_correct_copy_all_cells_agree(tmp_path, models, index):
    target = planted(tmp_path, index, lambda text: text)
    result = second.verify(second.ROOT, index, target, models[index])
    assert result['N'] > 0
    assert result['counts'] == {'AGREE': result['N']}
    assert all(c['source_span'] and c['excerpt_span'] for c in result['cells'])


@pytest.mark.parametrize('index', range(4))
def test_column_swap(tmp_path, models, index):
    def transform(text):
        lines = text.splitlines()
        for pos, line in enumerate(lines):
            if '|' in line and not line.startswith(('Outcome', 'Trial')):
                cols = line.split('|')
                a, b = ((2, 3) if index == 3 else (1, 2))
                cols[a], cols[b] = cols[b], cols[a]
                lines[pos] = '|'.join(cols)
                break
        return '\n'.join(lines) + '\n'
    target = planted(tmp_path, index, transform)
    result = second.verify(second.ROOT, index, target, models[index])
    assert result['counts']['DISAGREE'] == 2
    assert all(c['source_span'] and c['excerpt_span'] for c in result['flagged_items'])


@pytest.mark.parametrize('index', range(4))
def test_changed_digit(tmp_path, models, index):
    def transform(text):
        lines = text.splitlines()
        for pos, line in enumerate(lines):
            if '|' in line and not line.startswith(('Outcome', 'Trial')):
                cols = line.split('|')
                col = 2 if index == 3 else 1
                cols[col] = re.sub(r'\d', lambda m: str((int(m[0]) + 1) % 10), cols[col], count=1)
                lines[pos] = '|'.join(cols)
                break
        return '\n'.join(lines) + '\n'
    result = second.verify(second.ROOT, index, planted(tmp_path, index, transform), models[index])
    assert result['counts']['DISAGREE'] == 1


@pytest.mark.parametrize('index', range(4))
def test_sha_mismatch_refused(tmp_path, models, index):
    path = planted(tmp_path, index, lambda text: re.sub(r'sha256 [0-9a-f]{64}', 'sha256 ' + '0' * 64, text))
    with pytest.raises(ValueError, match='REFUSED source SHA-256/path mismatch'):
        second.verify(second.ROOT, index, path, models[index])


def test_measure_word_change(tmp_path, models):
    path = planted(tmp_path, 0, lambda t: t.replace('| HR (95% CI)', '| RR (95% CI)'))
    assert second.verify(second.ROOT, 0, path, models[0])['counts']['DISAGREE'] == 1


def test_unknown_label_and_missing_row_fail_closed(tmp_path, models):
    path = planted(tmp_path, 0, lambda t: t.replace('Dyspnea |', 'Unknown outcome |'))
    result = second.verify(second.ROOT, 0, path, models[0])
    assert result['counts']['NOT_FOUND_BY_SECOND_INSTRUMENT'] == 4
    assert result['counts']['DISAGREE'] == 1


def test_page_and_caption_defects_and_corrected_negative(tmp_path, models):
    # The committed Table12 excerpt is the CORRECTED one (the table's own page and heading): it must agree.
    assert all(c['status'] == 'AGREE' for c in second.verify(second.ROOT, 1, model=models[1])['provenance_checks'])
    # PLANT the defect this verifier caught in the first generator: the list-of-tables page (202) and its
    # dot-leader caption ('....... 37') taken for the table's own locator. Both must DISAGREE.
    path = planted(tmp_path, 1, lambda t: t.replace('PDF page 235', 'PDF page 202')
                   .replace('hazard ratios\n', 'hazard ratios....................... 37 \n', 1))
    result = second.verify(second.ROOT, 1, path, models[1])
    assert [c['status'] for c in result['provenance_checks']] == ['DISAGREE', 'DISAGREE']


def test_unbound_hr_changed_digit(tmp_path, models):
    original = second.verify(second.ROOT, 2, model=models[2])
    item = original['provenance_checks'][0]
    assert item['status'] == 'AGREE'
    changed = re.sub(r'\d', '9', item['excerpt_value'], count=1)
    path = planted(tmp_path, 2, lambda t: t.replace(item['excerpt_value'], changed))
    assert second.verify(second.ROOT, 2, path, models[2])['provenance_checks'][0]['status'] == 'DISAGREE'


def test_regeneration_without_writes():
    assert all(r['byte_identical'] and r['repeat_identical'] for r in second.regeneration())


def test_percent_sign_is_part_of_cell(tmp_path, models):
    path = planted(tmp_path, 2, lambda t: t.replace('(14.6%)', '(14.6)'))
    assert second.verify(second.ROOT, 2, path, models[2])['counts']['DISAGREE'] == 1


def test_dom_quote_plant_and_negative(tmp_path, models):
    original = second.verify(second.ROOT, 3, model=models[3])
    assert all(c['status'] == 'AGREE' for c in original['provenance_checks'])
    path = planted(tmp_path, 3, lambda t: t.replace('no deaths by 28 days', 'no deaths by 29 days'))
    items = second.verify(second.ROOT, 3, path, models[3])['provenance_checks']
    assert sum(c['status'] == 'NOT_FOUND_BY_SECOND_INSTRUMENT' for c in items) == 3


def test_population_digit_and_negative(tmp_path, models):
    original = second.verify(second.ROOT, 0, model=models[0])
    assert all(c['status'] == 'AGREE' for c in original['provenance_checks'])
    token = original['provenance_checks'][0]['excerpt_value']
    path = planted(tmp_path, 0, lambda t: t.replace('Of the ' + token, 'Of the 0' + token))
    assert second.verify(second.ROOT, 0, path, models[0])['provenance_checks'][0]['status'] == 'DISAGREE'


def test_missing_marker_refused(tmp_path, models):
    path = planted(tmp_path, 0, lambda t: t.replace('=== TABLES (excerpt) ===', ''))
    with pytest.raises(ValueError, match='REFUSED missing/duplicate TABLES marker'):
        second.verify(second.ROOT, 0, path, models[0])


def test_preferred_terms_definition_plant(tmp_path, models):
    original = second.verify(second.ROOT, 2, model=models[2])
    assert original['provenance_checks'][1]['status'] == 'AGREE'
    path = planted(tmp_path, 2, lambda t: t.replace('painful respiration', 'painless respiration'))
    assert second.verify(second.ROOT, 2, path, models[2])['provenance_checks'][1]['status'] == 'DISAGREE'
