import json
from copy import deepcopy

import pytest

from harness import dose_arms as da, recovery_map as rm, result_status, synth, extract

SLUG = 'tocilizumab-covid19-mortality'


def records(slug):
    return json.loads((rm.ROOT / 'cache' / slug / 'records.json').read_text(encoding='utf-8'))['records']


def disperse():
    return next(r for r in records('ticagrelor-vs-clopidogrel-acs') if 'DISPERSE-2' in r['title'])


def test_relay_cannot_enter_pool_even_if_claimed_ready():
    e = rm.load_map()[SLUG]['entries'][0]
    row = dict(e, provenance='RELAYED', state='ANALYSIS_READY')
    assert synth.Study(label=e['trial'], **{k: e[k] for k in rm.COUNT_KEYS}).yi_vi()
    with pytest.raises(ValueError, match='RELAYED_COUNTS_NOT_BOUND'):
        rm.require_poolable(row)
    assert rm.require_poolable({'id': 'fixture', 'provenance': 'abstract'})


def test_selected_mortality_population_never_safety():
    d = rm.denominator_for('28-day mortality', 'REMDACTA')
    assert (d['n1i'], d['n2i']) == (430, 210)
    assert d['provenance'] == 'RELAYED' and not d['poolable']
    with pytest.raises(ValueError, match='OUTCOME_POPULATION_NOT_HELD'):
        rm.denominator_for('Serious adverse events', 'REMDACTA')


@pytest.mark.parametrize('trial', ['EMPACTA', 'COVACTA'])
def test_generic_absence_replaced_with_own_reported_form(trial):
    data = rm.load_map()[SLUG]
    entry = next(e for e in data['entries'] if e['trial'] == trial)
    row = dict(id='PMID ' + entry['pmid'], state='OUTCOME_NOT_IN_SOURCE', reason_code='OUTCOME_NOT_IN_SOURCE')
    assert result_status.status_of(row, False, set())['state'] == 'RETRIEVED_NOT_REPORTED'
    review = {'outcomes': [{'name': '28-day mortality', 'population': data['population'], 'trials': [],
                            'declared_absent_trials': [row]}]}
    rm.attach(review, SLUG)
    assert row['state'] == 'REPORTED_OTHER_FORM'
    assert row['recovery_map']['reported_other_form']
    assert not review['outcomes'][0]['trials']


def test_population_mismatch_and_other_outcome_negative():
    data = rm.load_map()[SLUG]
    e = data['entries'][0]
    s = rm.classify(e, data['population'], {'population': 'intention-to-treat'}, '')
    assert s['state'] == 'POPULATION_UNRESOLVED'
    assert rm.classify(e, data['population'], {'population': data['population']}, '')['state'] == 'COUNTS_RECOVERED'
    review = {'outcomes': [{'name': 'Serious adverse events', 'declared_absent_trials': [{'id': e['pmid']}]}]}
    before = deepcopy(review['outcomes'])
    rm.attach(review, SLUG)
    assert review['outcomes'] == before


def test_missing_pmid_not_guessed_and_no_ready_relay():
    entries = rm.load_map()[SLUG]['entries']
    assert next(e for e in entries if e['trial'] == 'REMAP-CAP')['pmid'] is None
    held = {r['id'] for r in records(SLUG)}
    assert all(e['pmid'] is None or e['pmid'] in held for e in entries)


def test_disperse_arms_no_invented_n_and_active_refusal():
    r = disperse()
    assessment = da.assess(r)
    arms = assessment['arms']
    assert len(arms) == 3
    assert [a['drug'] for a in arms] == ['AZD6140', 'AZD6140', 'clopidogrel']
    assert all('twice daily' in a['dose'] for a in arms[:2])
    assert all(a['n'] is None for a in arms)
    assert assessment['status'] == 'REFUSED' and assessment['recovery'] == 'ACTIVE'
    with pytest.raises(ValueError, match='FULL_TABLE_NOT_HELD'):
        da.require_poolable(dict(r, full_table_held=True), {})
    assert da.assess({'abstract': 'A two-arm trial.'})['status'] == 'NO_RULE_FIRED'
    assert da.parse_arms('A total of 990 participants.') == []


def comparisons():
    return [dict(trial_id='fixture', outcome='bleeding', control_id='C', control_n=101,
                 control_events=11, n2i=101, ci=11, dose=d) for d in ('low', 'high')]


def test_shared_control_split_events_and_n_or_use_once():
    rows = comparisons()
    assert da.control_problems(rows)[0]['problem'] == 'SHARED_CONTROL_DOUBLE_COUNTED'
    with pytest.raises(ValueError, match='SHARED_CONTROL_DOUBLE_COUNTED'):
        da.require_controls(rows)
    fixed = da.split_control(rows)
    assert not da.control_problems(fixed)
    assert da.require_controls(fixed) == fixed
    assert sum(r['n2i'] for r in fixed) == 101 and sum(r['ci'] for r in fixed) == 11
    assert not da.control_problems(rows[:1])
    assert rows[0]['n2i'] == 101


def test_control_identity_or_counts_missing_fails_closed():
    rows = comparisons()
    rows[0].pop('control_id')
    with pytest.raises(ValueError, match='SHARED_CONTROL_IDENTITY_UNRESOLVED'):
        da.split_control(rows)
    rows = comparisons()
    rows[0].pop('control_events')
    with pytest.raises(ValueError, match='SHARED_CONTROL_UNBOUND'):
        da.split_control(rows)


def test_km_product_refused_and_raw_percentage_negative():
    row = dict(ai=round(9.8 * 330 / 100), n1i=330, ci=round(8.1 * 330 / 100), n2i=330)
    assert da.km_products(row, disperse()['abstract'])
    with pytest.raises(ValueError, match='KM_PERCENT_TO_COUNT'):
        da.require_poolable(disperse(), row)
    assert not da.km_products(row, 'Observed bleeding occurred in 9.8% and 8.1%.')
    assert not da.km_products({'effect': 0.8}, disperse()['abstract'])


def test_mi_not_composite_and_exact_negative():
    target = 'Composite of cardiovascular death, myocardial infarction or stroke'
    assert da.endpoint_problem('Myocardial infarction (MI): 5.6%', target) == 'MI_ONLY_NOT_COMPOSITE'
    assert da.endpoint_problem('Cardiovascular death, myocardial infarction or stroke: 5.6%', target) is None
    assert da.endpoint_problem('Myocardial infarction: 5.6%', 'myocardial infarction') is None


def test_mi_composite_base_extractor_plant():
    span = 'Myocardial infarction occurred in 10 (10%) of 100 ticagrelor patients and 20 (20%) of 100 clopidogrel patients.'
    row = extract.extract_trial(span, ['myocardial infarction'], ['ticagrelor'], ['clopidogrel'], declared_composite=True)
    assert row['ai'] == 10
    with pytest.raises(ValueError, match='MI_ONLY_NOT_COMPOSITE'):
        da.require_poolable({'id': 'fixture', 'abstract': span}, row, 'Composite cardiovascular death, MI or stroke', span)
