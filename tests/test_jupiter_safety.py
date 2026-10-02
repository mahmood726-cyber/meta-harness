"""Defect plants use synthetic mutations of held rows, never research outputs."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from harness import jupiter_safety as js, table_rows, measure_identity, subgroup_provenance
from scripts import make_jupiter_older_table1_excerpt as source

ROOT = source.ROOT


@pytest.fixture(scope='module')
def evidence():
    return js.inspect()


def base_table():
    return table_rows.parse(ROOT/source.TABLE3)[0]


def plant_outputs():
    """Executable pre-fix witnesses using actual existing harness functions."""
    table = base_table()
    myopathy = next(r for r in table['rows'] if r['label'] == 'Myopathy')
    config = json.loads((ROOT/'topics'/f'{js.SLUG}.json').read_text(encoding='utf-8'))
    muscle = config['harm_outcomes'][0]
    narrow = dict(table, rows=[myopathy])
    wrong_age = deepcopy(table)
    wrong_age['caption'] = wrong_age['caption'].replace('70-97', '50-69')
    # Synthetic column defects exercise generic parsing limitations.
    rate = dict(table, caption='Safety', header=['Outcome','Rosuvastatin patients N=100','Placebo patients N=100'])
    rate['header_lines'] = [rate['header']]
    rate_row = dict(label='Synthetic rate per 100 person-years', cells=['10 (8.92)', '10 (8.50)'])
    labels = [dict(label='Muscle safety', measure='HR', effect=1.04),
              dict(label='Muscle safety', measure='RR', effect=1.035)]
    return {
        'rate_percent': table_rows.typed(rate_row, rate)['arms'],
        'myopathy_substitution': table_rows.select(narrow, muscle['keywords'], []),
        'summed_definition': table_rows.select(dict(table, rows=[dict(myopathy, label='Muscle symptoms + Myopathy')]), muscle['keywords'], []),
        'wrong_age': table_rows.select(wrong_age, ['Muscle weakness, stiffness or pain'], []),
        'shared_labels': [measure_identity.identity(c) for c in labels],
        'bare_N': table_rows.typed(table['rows'][0], table),
        'source_authentication': dict(declared_sha=table['source_sha'], authenticated_by_table_rows=False),
        'provenance': subgroup_provenance.classify('Effect estimates from this exploratory analysis with age cutpoint chosen after trial completion'),
    }


def test_dom_excerpt_and_determinism(evidence):
    assert source.render() == source.render() == (ROOT/source.OUTPUT).read_bytes()
    table = base_table()
    for row in table['rows']:
        bound = evidence['rows'][row['label']]
        assert bound['source_span'].replace('–','-') == ' | '.join([row['label']]+row['cells'])
    assert evidence['baseline']['arms'][0]['denominator'] > 0
    assert evidence['person_year_denominators'] is None
    assert 'Cox proportional hazards' in evidence['model_span']


def test_rate_is_never_patient_percent():
    assert plant_outputs()['rate_percent'][0]['percent'] == 8.92
    with pytest.raises(ValueError, match='RATE_NOT_PERCENT.*8.92'):
        js.rate_as_percent(8.92, 'PER_100_PERSON_YEARS')
    assert js.rate_as_percent(8.92, 'PERCENT_PATIENTS') == 8.92


@pytest.mark.parametrize('labels', [['Myopathy'], ['Muscle weakness, stiffness or pain', 'Myopathy'], ['Muscle symptoms + Myopathy']])
def test_no_substitution_or_sum(labels):
    with pytest.raises(ValueError, match='DEFINITION_MISMATCH'):
        js.select_definition('Muscle symptoms/myopathy', labels)
    assert js.select_definition('Muscle symptoms/myopathy', ['Muscle weakness, stiffness or pain'])
    assert js.select_definition('Myopathy', ['Myopathy']) == 'Myopathy'


def test_wrong_age(evidence):
    with pytest.raises(ValueError, match='POPULATION_MISMATCH.*50'):
        js.require_age('Age 50–69 years')
    js.require_age(evidence['baseline']['age'])
    soup = source.held()
    soup.select_one('#T1 table thead th[colspan="2"]').string = 'Age 50–69 years'
    with pytest.raises(ValueError, match='AGE_HEADER'):
        source.baseline(soup)


def test_hr_rr_distinct_labels():
    candidates = [dict(label='Muscle safety', measure='HR'), dict(label='Muscle safety', measure='RR')]
    with pytest.raises(ValueError, match='MEASURE_LABEL_COLLISION'):
        js.require_distinct_labels(candidates)
    candidates[1]['label'] = 'Muscle safety — reconstructed RR'
    assert js.require_distinct_labels(candidates) == candidates


def test_unknown_counts_refuse_rr(evidence):
    for row in evidence['rows'].values():
        assert row['count_unit'] == 'UNKNOWN'
        assert row['reconstruction_refusal'].startswith('JUPITER_REFUSED: COUNT_UNIT_UNRESOLVED')
        assert [c['measure'] for c in row['candidates']] == ['HAZARD_RATIO']
        with pytest.raises(ValueError, match='COUNT_UNIT_UNRESOLVED'):
            js.reconstruct(row['arms'], 'N', row['definition'])
    # Explicitly synthetic patient-labelled control, NOT a JUPITER finding.
    arms = [dict(n=10, denominator=100, age='Age 70–97 years'), dict(n=20, denominator=100, age='Age 70–97 years')]
    rr = js.reconstruct(arms, 'Patients with at least one event', 'Synthetic outcome')
    assert rr['effect'] == 0.5 and rr['derivation'] == 'RECONSTRUCTED'
    with pytest.raises(ValueError, match='COUNT_PROVENANCE.*RELAYED'):
        js.reconstruct(arms, 'Patients with at least one event', 'Synthetic outcome', derivation='RELAYED')


def test_source_tamper_refused(tmp_path):
    dest = tmp_path/source.SOURCE
    dest.parent.mkdir(parents=True)
    dest.write_bytes((ROOT/source.SOURCE).read_bytes()+b' ')
    with pytest.raises(ValueError, match='SOURCE_SHA_MISMATCH'):
        source.held(tmp_path)
    source.held()


def test_excerpt_mismatch_refused(tmp_path):
    dest = tmp_path/source.TABLE3
    dest.parent.mkdir(parents=True)
    original = (ROOT/source.TABLE3).read_text(encoding='utf-8')
    dest.write_text(original.replace('494 |', '495 |'), encoding='utf-8')
    # The identical tampered excerpt still parses with the base declared SHA.
    assert table_rows.parse(dest)[0]['rows'][0]['cells'][0] == '495'
    with pytest.raises(ValueError, match='TABLE3_DOM_MISMATCH.*Muscle'):
        source.verify_table3(source.held(), tmp_path)
    source.verify_table3(source.held())


def test_baseline_excerpt_tamper(tmp_path):
    for name in (source.SOURCE, source.TABLE3, source.OUTPUT):
        path = tmp_path/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT/name).read_bytes())
    dest = tmp_path/source.OUTPUT
    dest.write_bytes(dest.read_bytes()+b'\n')
    with pytest.raises(ValueError, match='BASELINE_EXCERPT_MISMATCH'):
        js.inspect(tmp_path)


def test_dom_columns_cannot_swap():
    soup = source.held()
    table = soup.select_one('#T3 table')
    rows = table.thead.find_all('tr')
    rows[2].find_all('th')[1].string = 'Placebo'
    with pytest.raises(ValueError, match='SAFETY_ARM_MEASURE_HEADER'):
        source.safety_dom(soup)


def test_provenance_and_identity(evidence):
    config = json.loads((ROOT/'topics'/f'{js.SLUG}.json').read_text(encoding='utf-8'))
    review = js.provenance_review(config, evidence)
    assert review['conflict'] == 'SUBGROUP_PROVENANCE_CONFLICT'
    assert review['state'] == 'POST_HOC' and review['numeric_change'] is False
    fixed = deepcopy(config)
    fixed['primary_outcome']['trial_annotations'][evidence['pmid']]['evidence_unit'] = 'post_hoc_subgroup'
    assert js.provenance_review(fixed, evidence)['conflict'] is None
    assert js.bind(js.SLUG, config['harm_outcomes'][0]['name'], evidence['pmid'], evidence)['selected']['measure'] == 'HAZARD_RATIO'
    with pytest.raises(ValueError, match='REPORT_IDENTITY'):
        js.bind(js.SLUG, config['harm_outcomes'][0]['name'], 'PMID 99999999', evidence)


def test_prefix_no_partial_matches():
    with pytest.raises(ValueError, match='DEFINITION_MISMATCH'):
        js.select_definition('Muscle symptoms/myopathy', ['Muscle weakness, stiffness or pain plus myopathy'])


def test_base_witnesses():
    outputs = plant_outputs()
    assert outputs['myopathy_substitution'][0]['label'] == 'Myopathy'
    assert outputs['summed_definition'][0] is not None
    assert outputs['wrong_age'][0] is not None
    assert all(r['admissible'] for r in outputs['shared_labels'])
