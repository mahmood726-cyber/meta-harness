"""Defect plants and held-source integration checks for the incremental audit."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import error_rate_blind_v2 as v2
from scripts.error_rate_compare import _cmp


def request(**changes):
    r = dict(row_id='plant::Hyperkalemia::trial', endpoint='Hyperkalemia',
             kind='real pooled number', rowtype='count2x2', record_id='trial',
             document_ref='missing-source.txt')
    return dict(r, **changes)


TABLE = 'Event | Drug (N=100) | Placebo (N=90)\nHyperkalemia | 8 (8.0) | 6 (6.7)'


def test_blind_input_rejects_stored_values():
    for key in ('stored', 'effect', 'source_span', 'study_effect', 'handed_abstract'):
        with pytest.raises(ValueError, match='refused checker input keys'):
            v2.extract(dict(request(), **{key: 999999.125}))
    trial = dict(id='trial', label='trial', ai=999999.125, source_span='secret 999999.125')
    r = v2.checker_input('plant::Hyperkalemia::trial', {'name': 'Hyperkalemia'}, trial, 'real pooled number')
    assert '999999.125' not in json.dumps(r)
    assert set(r) == v2.INPUT_KEYS
    assert v2.extract(r)['verdict'] == 'NOT_RECHECKABLE'


def test_wrong_number_and_negative_plant():
    ext = v2.tables(TABLE, 'Hyperkalemia', 'count2x2')
    assert ext['values'] == dict(ai=8, n1i=100, ci=6, n2i=90)
    assert v2.compare(ext['values'], ext, 'count2x2')['verdict'] == 'EXACT_MATCH'
    bad = dict(ext['values'], ai=9)
    result = v2.compare(bad, ext, 'count2x2')
    assert result['verdict'] == 'DISAGREE'
    assert result['differences'][0]['field'] == 'ai'
    assert result['spans'][-1].startswith('Hyperkalemia')


def test_printed_precision_not_legacy_broad_tolerance():
    ext = v2.effect_result(('0.90', '0.74', '1.08'), ['HR 0.90; 95% CI 0.74-1.08'])
    bad = dict(effect=0.92, ci_low=0.74, ci_high=1.08)
    assert _cmp(dict(stored=bad, rowtype='effect'), dict(found=True, **ext['values'])) == ('MATCH', '')
    assert v2.compare(bad, ext, 'effect')['verdict'] == 'DISAGREE'
    assert v2.compare(dict(bad, effect=0.904), ext, 'effect')['verdict'] == 'EXACT_MATCH'


def test_control_excluded_and_named():
    kind = v2.classify({'is_control': True}, {'ai': 8})
    result = v2.extract(request(kind=kind))
    assert result['verdict'] == 'EXCLUDED'
    assert 'plant::Hyperkalemia::trial' in result['reason']
    assert v2.classify({}, {'ai': 8}) == 'real pooled number'


def test_control_does_not_enter_census_denominator(monkeypatch):
    pop, topics = v2.population()
    n_real = sum(kind == 'real pooled number' for _, _, kind in pop.values())
    rid = 'plant-control::Hyperkalemia::fixture'
    pop[rid] = ({'name': 'Hyperkalemia'}, {'label': 'fixture', 'ai': 8}, 'control')
    monkeypatch.setattr(v2, 'population', lambda root: (pop, topics))
    summary, rows, _ = v2.census()
    assert summary['data_denominator'] == n_real
    assert {'row_id': rid, 'kind': 'control'} in summary['excluded']
    assert next(r for r in rows if r['row_id'] == rid)['verdict'] == 'EXCLUDED'


def test_missing_or_ambiguous_source_fails_closed():
    assert 'missing-source.txt' in v2.extract(request())['reason']
    assert 'out-of-root' in v2.extract(request(document_ref='../escape.txt'))['reason']
    ambiguous = TABLE + '\nHyperkalemia | 9 (9.0) | 7 (7.8)'
    assert v2.tables(ambiguous, 'Hyperkalemia', 'count2x2')['verdict'] == 'NOT_RECHECKABLE'
    assert 'values' in v2.tables(TABLE, 'Hyperkalemia', 'count2x2')


def test_endpoint_section_and_event_columns():
    table = ('Event | Semaglutide (N=100) participants | Semaglutide events | Placebo (N=90) participants | Placebo events\n'
             'Gastrointestinal disorders | 8 (8.0) | 600 | 6 (6.7) | 700\n'
             'Serious adverse events: Gastrointestinal disorders | 2 (2.0) | 300 | 1 (1.1) | 200')
    ext = v2.tables(table, 'Gastrointestinal adverse events', 'count2x2')
    assert ext['values']['ai'] == 8 and ext['values']['ci'] == 6
    assert v2.tables(table, 'Serious gastrointestinal adverse events', 'count2x2')['values']['ai'] == 2
    assert v2.tables(table, 'Gastrointestinal adverse events leading to permanent discontinuation', 'count2x2')['verdict'] == 'NOT_RECHECKABLE'


def test_tecos_component_selection():
    table = ('Outcome | HR\n'
             'Composite (Cardiovascular death, nonfatal myocardial infarction, nonfatal stroke, unstable angina) | 0.98 (0.89–1.08)\n'
             'Composite (Cardiovascular death, nonfatal myocardial infarction, nonfatal stroke) | 0.99 (0.89–1.10)')
    e = v2.tables(table, '3-point major adverse cardiovascular events', 'effect')
    assert e['values']['effect'] == .99
    assert v2.tables(table.splitlines()[0]+'\n'+table.splitlines()[1], '3-point major adverse cardiovascular events', 'effect')['verdict'] == 'NOT_RECHECKABLE'


def test_registry_group_ids_and_units():
    data = v2.read(ROOT/'cache/sacubitril-valsartan-hfref/records.json')
    good = v2.registry(data, 'NCT02554890', 'Hypotension')
    assert good['values'] == dict(ai=66, n1i=440, ci=56, n2i=441)
    bad = copy.deepcopy(data)
    for m in bad['ctgov_results']['NCT02554890']:
        if 'Hypotension' in m['title']:
            m['unitOfMeasure'] = 'events'
    assert v2.registry(bad, 'NCT02554890', 'Hypotension')['verdict'] == 'NOT_RECHECKABLE'


def test_current_population_exactly_matches_base_and_no_number_input():
    spec = importlib.util.spec_from_file_location('stage_additions', ROOT/'tests/test_stage_additions.py')
    stage = importlib.util.module_from_spec(spec); spec.loader.exec_module(stage)
    pop, _ = v2.population()
    assert set(pop) == stage._pooled_population()
    summary, rows, _ = v2.census()
    assert summary['data_denominator'] == len(pop) - len(summary['excluded'])
    assert summary['live_population'] == len(pop)
    for row in rows:
        o, t, kind = pop[row['row_id']]
        changed = dict(t, **{k: 999999.125 for k in v2.FIELDS if k in t})
        assert v2.checker_input(row['row_id'], o, changed, kind) == row['checker_input']
        assert row['verdict'] == 'EXACT_MATCH'


# The pre-write census is pinned to the last commit before the blind-v2 wave, so the preservation check runs from
# any clone (a lane-local snapshot would make this test skip everywhere but the lane that wrote it).
PRE_BLIND_V2_COMMIT = '055e856afaf8d819140db88964eb62190d4dd132'


def _at_commit(path):
    import subprocess
    out = subprocess.run(['git', 'show', f'{PRE_BLIND_V2_COMMIT}:{path}'], cwd=ROOT, capture_output=True)
    assert out.returncode == 0, f'pre-blind-v2 commit not reachable for {path}: {out.stderr[:200]!r}'
    return out.stdout


def test_original_rows_byte_identical_and_historical_snapshot():
    before = v2.row_byte_spans(_at_commit('docs/error_rate_sample.json'))[0]
    after = v2.row_byte_spans((ROOT/'docs/error_rate_sample.json').read_bytes())[0]
    assert len(before) == 156
    assert after[:len(before)] == before
    audit = v2.read(ROOT/'docs/error_rate.json')
    assert audit['HISTORICAL_before_blind_v2'] == json.loads(_at_commit('docs/error_rate.json'))
