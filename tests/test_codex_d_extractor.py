"""Job D regression plants. All sentences/tables below are SYNTHETIC, not research data.

Each test contains an assertion that fails with d3f8f80. These tests are supplied
for the isolated runner; they were NOT executed on the shared host.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import evidence_identity as ei, reason_audit as ra


def candidates(text, name="Injury", measure="HR", reason=""):
    return ra.typed_candidates(
        {"name": name, "estimand": measure}, {"id": "synthetic", "reason": reason},
        [{"source_id": "synthetic", "text": text}], {"keywords": [name]})


def test_grid_headers_and_adjacent_effect_keep_column_identity():
    # SYNTHETIC: multi-row headers, both spans, a self-closing label header and a body row header.
    table = ('<table><thead><tr><th rowspan="2"/><th colspan="2">Patients</th>'
             '<th rowspan="2">Adjusted HR (95% CI)</th></tr><tr>'
             '<th>A (n=100)</th><th>B (n=120)</th></tr></thead><tbody>'
             '<tr><th>Injury</th><td>5/90 (5.6)</td><td>9/110 (8.2)</td>'
             '<td>0.6 (0.3 to 1.2)</td></tr></tbody></table>')
    effect = ei.from_tables(table, "synthetic", "synthetic")[0]
    assert effect["arms"][0]["arm"] == "Patients | A (n=100)"
    assert [(a["events"], a["n"], a["n_group"]) for a in effect["arms"]] == [(5, 90, 100), (9, 110, 120)]
    assert effect["effect_measure"] == "HR" and effect["adjusted"]
    assert effect["ci"] == [0.3, 1.2]
    # SYNTHETIC: the label header is absent altogether.
    missing = '<table><tr><th>A (n=100)</th><th>B (n=100)</th><th>OR (95% CI)</th></tr><tr><td>Injury</td><td>5 (5)</td><td>9 (9)</td><td>0.6 (0.3 to 1.2)</td></tr></table>'
    assert [a["events"] for a in ei.from_tables(missing, "s", "s")[0]["arms"]] == [5, 9]


def test_explicit_count_cells_override_percent_label_only_with_arm_support():
    # SYNTHETIC: printed counts reproduce the arm percentages despite a shorthand % label.
    template = '<table><tr><th/><th>A (n=100)</th><th>B (n=100)</th></tr><tr><td>Injury, %</td><td>{}</td><td>{}</td></tr></table>'
    rows = ei.count_rows(template.format('5 (5)', '9 (9)'), 's', 's')
    assert [a['events'] for a in rows[0]['arms']] == [5, 9]
    assert rows[0]['arms'][0]['n'] is None
    assert ei.count_rows(template.format('5%', '9%'), 's', 's') == []


def test_spelled_counts_and_delayed_percentage_before_none():
    # SYNTHETIC: ordinary numbers through ninety-nine; none is explicitly in the other arm.
    rows = candidates('Thirty-three patients in the treatment group and seven patients in the control group experienced injury.')
    assert [a['events'] for a in rows[0]['arms']] == [33, 7]
    rows = candidates('Four patients in the treatment group had major bleeding (0.7%), versus none in the control group.', 'Bleeding')
    assert [a['events'] for a in rows[0]['arms']] == [4, 0]


def test_distributive_values_keep_separate_predicates():
    # SYNTHETIC: two different shared values in one sentence.
    rows = candidates('Injury occurred in two patients in each group and necessitated treatment discontinuation in one patient in each group.')
    assert [[a['events'] for a in r['arms']] for r in rows] == [[2, 2], [1, 1]]
    assert 'discontinuation' not in rows[0]['span']
    numeric = candidates('Injury occurred in 3 patients in both groups.')
    assert [a['events'] for a in numeric[0]['arms']] == [3, 3]
    percent = candidates('Injury occurred in 8.1% of the patients in each group.')
    assert percent[0]['effect_measure'] == 'PERCENT'
    assert all('events' not in a for a in percent[0]['arms'])
    assert ei.result_clauses('Injury occurred in two patients across both groups combined.') == []


def test_counts_rates_and_effects_are_distinct_representations():
    # SYNTHETIC: a rate denominator and CI confidence level must never become event counts.
    quote = ('Injury occurred in 12 patients (6%) in the treatment group and 18 patients (9%) in the control group '
             '(incidence, 2.5 vs. 3.6 events per 100 person-years; hazard ratio, 0.69; 95% confidence interval [CI], 0.57 to 0.83).')
    rows = {r['effect_measure']: r for r in candidates(quote)}
    assert set(rows) == {'COUNTS', 'RATE', 'HR'}
    assert rows['RATE']['unit'] == 'PATIENT_YEARS'
    assert rows['RATE']['arms'] == [{'rate': 2.5, 'per': 100}, {'rate': 3.6, 'per': 100}]
    assert rows['HR']['unit'] == 'PATIENTS_WITH_EVENT'
    assert rows['HR']['ci'] == [0.57, 0.83]
    assert rows['COUNTS']['estimate'] is None


def test_closing_effects_and_hyphen_cis_stay_with_own_endpoint():
    # SYNTHETIC: the second outcome's OR must not be attached to the first percentage pair.
    quote = ('Diarrhea occurred in 25% vs. 12% (OR 2.5; 95% Cl 1.3-5.1), and '
             'abdominal pain occurred in 7% vs. 2% (OR 4.7; 95% CI 1.0-22.9).')
    effects = {r['estimate']: r for r in candidates(quote, 'Diarrhea', 'OR') if r['estimate'] is not None}
    assert set(effects) == {2.5, 4.7}
    assert effects[2.5]['ci'] == [1.3, 5.1]
    assert 'abdominal pain' not in effects[2.5]['span']
    assert 'outcome' in effects[4.7]['mismatch']
    foreign = candidates('Diarrhea occurred in 5% vs 7%; bleeding (HR 0.8; 95% CI 0.5-1.2).', 'Diarrhea')
    assert all(r['estimate'] is None or 'outcome' in r['mismatch'] for r in foreign)


def test_composite_numeric_result_is_retained_as_wrong_part():
    # SYNTHETIC: an established composite acronym need not share the requested component's words.
    rows = candidates('MAKE30 did not differ between groups (24.7% vs. 24.6%; P = 0.98).', 'Mortality', 'RR')
    assert rows and rows[0]['part'] == 'COMPOSITE'
    assert 'part:COMPOSITE!=COMPONENT' in rows[0]['mismatch']
    assert 'outcome' in rows[0]['mismatch']
    spelled = candidates('A composite of death or injury occurred in two patients in each group.', 'Mortality', 'RR')
    assert spelled[0]['part'] == 'COMPOSITE'


def test_one_sided_bound_is_recorded_without_two_sided_ci():
    # SYNTHETIC: the point estimate and one-sided repeated upper bound are different fields.
    quote = ('Injury occurred in 30 patients in the treatment group and 31 patients in the control group '
             '(hazard ratio, 0.96; upper boundary of the one-sided repeated confidence interval, 1.16).')
    effect = next(r for r in candidates(quote) if r['effect_measure'] == 'HR')
    assert effect['estimate'] == 0.96 and effect['ci'] is None
    assert effect['confidence_bound'] == {'side': 'upper', 'value': 1.16, 'one_sided': True, 'repeated': True}
    assert 'precision:ONE_SIDED_CI' in effect['mismatch']
    lower = ei.from_sentence(quote.replace('upper boundary', 'lower boundary').replace('1.16', '0.76'), 's', 's')
    assert lower['confidence_bound']['side'] == 'lower' and lower['ci'] is None


def test_explicit_patient_subject_outranks_nearby_event_nouns():
    # SYNTHETIC: a patient subject may be separated from its predicate by the arm description.
    assert ei.unit_of('More patients in the treatment group than in the control group were hospitalized for heart failure (3.5% vs. 2.8%).') == 'PATIENTS_WITH_EVENT'
    assert ei.unit_of('Seven patients had one or more episodes of injury.') == 'PATIENTS_WITH_EVENT'
    assert ei.unit_of('There were seven episodes of injury.') == 'EVENTS'
    assert ei.unit_of('Injury occurred in 3 patients.') == 'PATIENTS_WITH_EVENT'


def test_coordinated_patient_subject_does_not_convert_episode_totals():
    # SYNTHETIC: inherit the explicit patient referent for "had", but not for "there were ... events".
    quote = ('Adverse events occurred in 70 (70%) and 80 (80%) patients in the treatment and control groups; '
             '30 (30%) and 40 (40%) had 1 or more episodes of hypoglycemia; '
             'and there were 9 (9%) vs 5 (5%) events of pancreatitis.')
    rows = candidates(quote, 'Hypoglycemia', 'RR', 'unique patients required')
    glucose = next(r for r in rows if r['arms'][0].get('events') == 30)
    pancreatitis = next(r for r in rows if r['arms'][0].get('events') == 9)
    assert glucose['unit'] == 'PATIENTS_WITH_EVENT'
    assert pancreatitis['unit'] == 'EVENTS' and 'unit:EVENTS' in pancreatitis['mismatch']


def test_comma_separated_numeric_predicates_keep_own_labels():
    # SYNTHETIC: the second clause's patient subject is shared, its endpoint is not.
    quote = ('Thirty-three patients (22%) in the treatment group vs 43 (29%) in the control group experienced infections, '
             '47 (31%) vs 42 (28%) needed insulin for glucose control, and 5 (3%) vs 9 (6%) experienced other serious adverse events.')
    rows = candidates(quote, 'Infections', 'RR')
    insulin = next(r for r in rows if r['arms'][0].get('events') == 47)
    assert 'infections' not in insulin['span']
    assert insulin['unit'] == 'PATIENTS_WITH_EVENT' and 'outcome' in insulin['mismatch']
    residual = next(r for r in rows if r['arms'][0].get('events') == 5)
    assert residual['definition'] == 'RESIDUAL'


def test_bare_integer_outcome_contrasts_are_not_rates():
    # SYNTHETIC: keep an integer death contrast; never parse the rate's scale as a count.
    rows = candidates('There was higher mortality in the treatment group (8 versus 1; P=0.02).', 'Mortality')
    assert [a['events'] for a in rows[0]['arms']] == [8, 1]
    rates = candidates('Mortality incidence was 8 versus 1 per 100 person-years.', 'Mortality')
    assert all(r['effect_measure'] == 'RATE' for r in rates)


def test_ordered_multiarm_list_remains_unresolved():
    # SYNTHETIC: do not silently choose a contrast or sum arms.
    rows = candidates('Injury occurred in 4 (3%), 5 (3%), and 1 (1%) patients in the low-dose, high-dose, and control groups, respectively.', 'Injury', 'RR')
    assert [a['events'] for a in rows[0]['arms']] == [4, 5, 1]
    assert rows[0]['comparison'] == 'MULTI_ARM_UNRESOLVED'
    assert 'comparison' in rows[0]['mismatch']


def test_cause_restricted_discontinuation_cannot_disprove_all_cause():
    # SYNTHETIC: newly recovered shared values still obey the definition refusal.
    assert ei.definition_of('Injury necessitated treatment discontinuation in one patient in each group.', 'Treatment discontinuation') == 'RESTRICTED'
