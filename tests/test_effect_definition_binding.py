"""Synthetic PLANTS are tests, not research output."""
from dataclasses import replace
from pathlib import Path
import hashlib
import pytest

from harness import source_hierarchy, target_endpoint
from harness.effect_definition_binding import (
    extract_documents, parse_passage, pair_counts, plain_outcome_binding,
    require_poolable, make_row,
)
from scripts.make_plato_fda_dyspnea_def_excerpt import read_sources, render

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def held():
    return extract_documents(read_sources(ROOT))[0]


@pytest.mark.parametrize('label,outcome', [
    ('PLATO-defined non-CABG major bleeding', 'Major bleeding'),
    ('Dyspnea single preferred term leading to discontinuation', 'Dyspnea'),
    ('Serious dyspnea single preferred term', 'Dyspnea'),
    ('TIMI major bleeding', 'Major bleeding'),
])
def test_plant_variant_not_plain(label, outcome):
    passage = label + ' HR 1.25 (95% CI 1.10, 1.42).'
    spec = {'name': outcome, 'keywords': [outcome.lower()]}
    assert target_endpoint._classify(spec, passage)['target_endpoint_class'] == 'EXACT_TARGET'
    assert source_hierarchy.source_effect_candidates(spec, abstract=passage)
    row = parse_passage(passage, trial='PLATO')[0]
    assert 'VARIANT_FOR_PLAIN_OUTCOME' in plain_outcome_binding(row, outcome)


def test_negative_plain_total():
    row = parse_passage('PLATO-defined total major bleeding HR 1.25 (95% CI 1.10, 1.42).', trial='PLATO')[0]
    assert plain_outcome_binding(row, 'Major bleeding') == 'BOUND'


def test_plant_onset_without_definition():
    passage = 'Time to first dyspnea event HR 1.25 (95% CI 1.10, 1.42).'
    assert source_hierarchy.source_effect_candidates({'keywords': ['dyspnea']}, abstract=passage)
    row = parse_passage(passage, trial='PLATO')[0]
    assert row.binding_state == 'UNRESOLVED'
    assert 'DEFINITION_NOT_STATED' in plain_outcome_binding(row, 'Dyspnea')


def test_negative_explicit_onset_definition():
    row = parse_passage('Time to first dyspnea event (single preferred term only) HR 1.25 (95% CI 1.10, 1.42).', trial='PLATO')[0]
    assert plain_outcome_binding(row, 'Dyspnea') == 'BOUND'


def test_plant_adjacent_definition_not_inherited():
    text = 'Preferred terms: dyspnea, orthopnea.\nTime to first dyspnea event HR 1.25 (95% CI 1.10, 1.42).'
    assert parse_passage(text, trial='PLATO')[0].binding_state == 'UNRESOLVED'


def test_plant_counts_cannot_cross_rows(held):
    major = next(r for r in held if r.trial == 'PHILO' and r.label == 'Major bleeding (PLATO-defined)')
    child = next(r for r in held if r.trial == 'PHILO' and 'Non-CABG' in r.label)
    with pytest.raises(ValueError, match='CROSS_DEFINITION_OR_SOURCE_ROW_COUNTS'):
        pair_counts(major, child)
    assert pair_counts(major, major) == major.counts


def test_plant_count_unit_not_events(held):
    major = next(r for r in held if r.trial == 'PHILO' and r.label == 'Major bleeding (PLATO-defined)')
    events = replace(major, unit='EVENTS')
    with pytest.raises(ValueError, match='NON_PATIENT_COUNTS'):
        pair_counts(events, events)


def test_plant_invalid_ci():
    with pytest.raises(ValueError, match='INVALID_HR_CI'):
        parse_passage('PLATO-defined total major bleeding HR 1.25 (95% CI 1.50, 1.60).', trial='PLATO')


def test_plant_sha_sidecar_and_pdf_fail_closed(monkeypatch):
    original = Path.read_bytes
    for suffix in ('.local.txt', '.pdf'):
        def tampered(path):
            data = original(path)
            return data + b'changed' if str(path).endswith(suffix) else data
        monkeypatch.setattr(Path, 'read_bytes', tampered)
        with pytest.raises(ValueError, match='SOURCE_SHA_MISMATCH'):
            read_sources(ROOT)
        monkeypatch.setattr(Path, 'read_bytes', original)


def test_plant_wrong_trial(held):
    other = next(r for r in held if r.trial == 'TRITON')
    assert 'TRIAL_NOT_TARGET' in plain_outcome_binding(other, 'Major bleeding')


def test_plant_ledger_never_pool_input(held):
    major = next(r for r in held if r.definition == 'STUDY_DEFINED_TOTAL_MAJOR_BLEEDING')
    with pytest.raises(ValueError, match='DEFINITION_LEDGER_NOT_POOL_INPUT'):
        require_poolable(major)
    assert not any(r.poolable for r in held)


def test_held_source_spans_and_no_dyspnea_hr_promotion(held):
    docs = {d['source']: d['text'] for d in read_sources(ROOT).values()}
    for row in held:
        assert docs[row.source][row.start:row.end] == row.quote
    onset = [r for r in held if r.label == 'Dyspnea onset']
    assert onset and all(r.binding_state == 'UNRESOLVED' for r in onset)
    assert not any(r.scale == 'HR' and 'dyspn' in r.label.lower() for r in held if r.trial == 'PHILO')
    assert any(r.label == 'Dyspnea' and r.counts for r in held if r.trial == 'PHILO')


def test_excerpt_determinism_and_hashes():
    a, b = render(ROOT), render(ROOT)
    assert a == b and a
    for excerpt in a.values():
        assert hashlib.sha256(excerpt['text'].encode('utf-8')).hexdigest() == excerpt['sha256']


def test_negative_patient_not_event_column(held):
    major = next(r for r in held if r.label == 'Total Major')
    counts = pair_counts(major, major)
    assert 'bleeding_events_1' not in counts
    assert counts['patients_1'] != major.counts['bleeding_events_1']


def test_plant_unknown_source_empty_span():
    with pytest.raises(ValueError, match='EMPTY_SOURCE_SPAN'):
        make_row('', 'missing', 'PLATO', 0, 0, 'Major bleeding')


def test_plant_malformed_table_row_not_silently_dropped():
    from harness.effect_definition_binding import medical_rows, statistical_rows
    docs = read_sources(ROOT)
    broken = docs['medical']['text'].replace('Total Major  ', 'Total UNKNOWN  ', 1)
    with pytest.raises(ValueError, match='FDA_TABLE_MISSING_OR_DUPLICATE_ROWS'):
        medical_rows(broken, 'synthetic-defect')
    stat = docs['statistical']['text']
    # Alter a cell inside the actual safety table, leaving its row label present.
    start = stat.index('Table 11 Analyses on Non CABG TIMI Major Bleeding by Median ASA in TRITON \n')
    tail = stat[start:]
    import re
    tail = re.sub(r'(?m)^(low)\s+\d', r'\1 INVALID', tail, count=1)
    with pytest.raises(ValueError, match='STATR_BLEEDING_ROW_LAYOUT'):
        statistical_rows(stat[:start]+tail, 'synthetic-defect')
