"""Defect plants are synthetic; held-source tests never author research counts."""
import json
from pathlib import Path
import re

import pytest

from harness import extract
from harness import population_rules as p
from harness import timepoint_identity as t

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'tocilizumab-covid19-mortality'


def held():
    config = json.loads((ROOT / 'topics' / f'{SLUG}.json').read_text(encoding='utf-8'))
    review = json.loads((ROOT / 'docs/reviews' / SLUG / 'review.json').read_text(encoding='utf-8'))
    return config, review


@pytest.mark.parametrize('target,span,expected', [
    ('28 days', 'day 60', 'MISMATCH'),
    (None, 'day 60', 'TARGET_MISSING'),
    ('28 days', 'study day 29; day 1 = day of inclusion', 'MATCH'),
    ('28 days', 'at 28 days', 'MATCH'),
    ('28 days', 'week 4', 'MATCH'),
    ('28 days', 'day 28; day 0 is baseline', 'MATCH'),
    ('28 days', 'day 29', 'MISMATCH'),
    ('28 days', 'day 28 and day 60', 'MISMATCH'),
    ('28 days', 'day 28-60', 'MISMATCH'),
    ('28 days', '', 'MISMATCH'),
])
def test_time_plants(target, span, expected):
    assert t.compare(target, span) == expected


def test_base_time_refuses_neither_missing_nor_wrong_day():
    assert extract.timepoint_mismatch('', 'day 60') == ''
    assert extract.timepoint_mismatch('28 days', 'day 60') == ''
    assert t.parse('28 days; day 1 = day of inclusion').elapsed_days == 28
    assert t.parse('week 4; day 1 = day of inclusion').elapsed_days == 28
    assert t.parse('day 29; day 1 is baseline; day 0 is baseline').refusal == 'TIME_ORIGIN_CONFLICT'


@pytest.mark.parametrize('span,unit', [
    ('patients with serious adverse events', 'PATIENTS'),
    ('participants who experienced an event', 'PATIENTS'),
    ('n (%) of patients', 'PATIENTS'),
    ('serious adverse events occurred in 3 of 20 patients', 'PATIENTS'),
    ('5 events', 'EVENTS'), ('episodes', 'EVENTS'),
    ('5 events among 3 patients with adverse events', 'UNKNOWN'),
    ('not reported', 'UNKNOWN'),
    ("outcome 'Composite of CV Events' HR 1.05", 'UNKNOWN'),
    ('Bleeding was observed in 26 patients. Other adverse events were similar.', 'PATIENTS'),
    ('20 patients with adverse events', 'PATIENTS'),
])
def test_count_units(span, unit):
    assert t.count_unit(span) == unit


def test_unit_pool_plant_and_negative():
    rows = [{'id': 'plant-A', 'source': 'patients with events'},
            {'id': 'plant-B', 'source': '5 episodes'}]
    assert t.pool_problems(rows)[0]['code'] == 'UNIT_MIX_POOLED'
    assert t.pool_problems(rows)[0]['refused'] == ['plant-A', 'plant-B']
    rows[1]['source'] = 'participants who experienced an event'
    assert t.pool_problems(rows) == []
    assert t.pool_problems([{'id': 'unknown', 'source': ''}])[0]['code'] == 'COUNT_UNIT_UNKNOWN'


def test_base_pool_does_not_check_count_units():
    from harness.synth import Study, pool
    # Deliberately synthetic defect, not clinical evidence.
    rows = [{'id': 'plant-A', 'source': 'patients with events'},
            {'id': 'plant-B', 'source': '5 episodes'}]
    studies = [Study(label=r['id'], ai=3, n1i=20, ci=4, n2i=20, source=r['source']) for r in rows]
    assert pool(studies).k == 2
    assert t.pool_problems(rows)[0]['code'] == 'UNIT_MIX_POOLED'


def test_population_plant_and_negative():
    config = {'harm_outcomes': [{'name': 'harm'}]}
    outcome = {'name': 'harm', 'trials': [{'id': 'accepted', 'source': 'safety population'}],
               'declared_absent_trials': [{'id': 'refused', 'source': 'treated safety population',
                                          'reason_code': 'POPULATION_MISMATCH'}]}
    review = {'outcomes': [outcome]}
    assert extract.population_mismatch('treated safety population') == ''
    assert p.consistency(review, config)[0]['code'] == 'POPULATION_RULE_INCONSISTENT'
    rule = p.rule_for(outcome, config)
    assert p.admissibility({'source': 'received at least one dose'}, rule)['allowed']
    assert not p.admissibility({'id': 'unknown', 'source': ''}, rule)['allowed']
    outcome['declared_absent_trials'][0]['reason_code'] = 'TIMEPOINT_MISMATCH'
    assert p.consistency(review, config) == []


def test_efficacy_policy_and_classification():
    config = {'primary_outcome': {'name': 'efficacy', 'population': 'modified intention-to-treat'}}
    rule = p.rule_for({'name': 'efficacy'}, config)
    assert rule.efficacy == 'MODIFIED_ITT'
    assert p.classify('randomised') == 'INTENTION_TO_TREAT'
    assert p.classify('per-protocol') == 'PER_PROTOCOL'
    assert not p.admissibility({'source': 'safety population'}, rule)['allowed']
    rule = p.rule_for({'name': 'efficacy'}, {}, '- **Population** - intention-to-treat as randomised.')
    assert rule.selected == 'INTENTION_TO_TREAT'


def test_held_immcova_and_empacta():
    config, review = held()
    sae = next(o for o in review['outcomes'] if o['name'] == 'Serious adverse events')
    imm = next(r for r in sae['declared_absent_trials'] if r['id'] == 'PMID 38157348')
    ft = (ROOT / 'cache' / SLUG / 'ft_38157348.txt').read_text(encoding='utf-8')
    origin = ' '.join(t.origin_spans(ft))
    assert origin
    target = config['primary_outcome']['timepoint']
    assert imm['reason_code'] == 'TIMEPOINT_MISMATCH'
    assert t.compare(target, t.parse(t.row_span(imm), origin)) == 'MATCH'
    footnote = re.search(r'Number of patients with any SAE:[^<]+', t.row_span(imm)).group(0)
    assert t.count_unit(footnote) == 'PATIENTS'
    emp = (ROOT / 'cache' / SLUG / 'ft_33332779.txt').read_text(encoding='utf-8')
    caption = re.search(r'Adverse Events through Day \d+ in the Safety Population', t.plain(emp)).group(0)
    assert t.compare(target, caption) == 'MISMATCH'
    sae_spec = next(o for o in config['harm_outcomes'] if o['name'] == sae['name'])
    assert t.compare(sae_spec.get('timepoint'), caption) == 'TARGET_MISSING'
    assert not sae['trials']
    assert sae['result']['state'] == 'LANE_REFUSED'
    held_rows = [r for r in sae['declared_absent_trials']
                 if 'POPULATION_RULE_INCONSISTENT' in r.get('lane_refusals', [])]
    assert {r['id'] for r in held_rows} == {'PMID 33332779', 'PMID 33631066'}
    from copy import deepcopy
    pre = deepcopy(sae)
    pre['trials'] = deepcopy(held_rows)
    pre['declared_absent_trials'] = [r for r in pre['declared_absent_trials']
                                   if r['id'] not in {t['id'] for t in held_rows}]
    problems = p.consistency({'outcomes': [pre]}, config)
    assert any('PMID 34609549' in x['refused'] and 'PMID 33332779' in x['accepted'] for x in problems)
    pre['declared_absent_trials'] = []
    assert p.consistency({'outcomes': [pre]}, config) == []


def test_census_denominators_and_names():
    from scripts.timepoint_population_census import census
    result = census()
    assert result['coverage']['topics'] == len(list((ROOT / 'topics').glob('*.json')))
    for metric in result['rules'].values():
        assert metric['n'] == len(metric['items']) <= metric['N']
    assert f'{SLUG}::Serious adverse events' in result['rules']['outcomes_without_target_timepoint']['items']
