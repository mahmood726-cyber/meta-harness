"""General synthetic plants; no audit or validation papers are fixtures."""
import importlib.util
from pathlib import Path
import pytest

SPEC = importlib.util.spec_from_file_location('v11', Path(__file__).resolve().parents[1] / 'scripts/bench_screen_v1_1.py')
b = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(b)


def root(body=''):
    return b.parse_xml(('<article><body>' + body + '</body></article>').encode())


@pytest.mark.parametrize('number,value', list(b.WORDS.items()) + [('1,234', 1234)])
def test_numbers(number, value):
    assert b.extract_k(f'We included {number} randomized controlled trials.', root())[0] == value


@pytest.mark.parametrize('statement,k', [
    ('We included twenty-two studies (eleven RCTs and eleven observational studies).', 11),
    ('Eleven trials involving 800 participants were included.', 11),
    ('We included nine RCTs.', 9),
    ('A total of thirty-one randomised trials were included.', 31),
    ('We included 8 RCTs. Four trials reported mortality.', 8),
    ('We included 8 RCTs. Sensitivity analysis included 7 RCTs.', 8),
    ('We included 8 RCTs. We excluded 3 RCTs. Two trials were ongoing.', 8),
    ('We included 8 RCTs. Our review included 9 RCTs.', None),
    ('We included 19 observational studies and six RCTs.', 6),
    ('Twenty seven studies were included.', 27),
    ('No eligible studies were found.', None),
])
def test_count_attribution(statement, k):
    assert b.extract_k('We searched for randomized controlled trials. ' + statement, root())[0] == k


def test_review_total_over_outcome_count_in_results():
    assert b.extract_k('We included nine randomized trials.', root('<sec><title>Results</title><p>Six RCTs reported mortality.</p></sec>'))[0] == 9


@pytest.mark.parametrize('body,ok', [
    ('We performed pairwise meta-analyses using random effects and a network meta-analysis.', True),
    ('Pair-wise meta-analysis was conducted for direct comparisons.', True),
    ('We did not perform pairwise meta-analysis.', False),
    ('Previous reviews performed pairwise meta-analyses.', False),
    ('We performed only network meta-analysis.', False),
    ('We performed pairwise and network meta-analyses.', True),
])
def test_pairwise_with_network(body, ok):
    assert b.design_decision('Network meta-analysis', 'We included randomized control trials.', body, [])[0] is ok


@pytest.mark.parametrize('title', ['Umbrella review', 'Diagnostic accuracy meta-analysis', 'Review of observational studies', 'Retraction notice', 'Individual participant data meta-analysis'])
def test_excluded_designs(title):
    assert not b.design_decision(title, 'We included randomized trials.', '', [])[0]


def test_excluded_rows_do_not_bleed():
    xml = root('<table-wrap><caption>Characteristics of included and excluded trials</caption><table><tr><td>NCT00000001</td><td>excluded</td></tr><tr><td>NCT00000002</td><td>included</td></tr><tr><td>NCT00000003</td><td>ongoing</td></tr></table></table-wrap>')
    ids, evidence = b.included_ids(xml)
    assert ids == ['NCT00000002']
    assert evidence[0]['attribution'] == 'table row'


def test_myeloma_is_condition_before_infection():
    hit = {'title': 'Infections during treatment of myeloma', 'meshHeadingList': {'meshHeading': [{'descriptorName': 'Infections', 'majorTopic_YN': 'Y'}, {'descriptorName': 'Multiple Myeloma', 'majorTopic_YN': 'Y'}]}}
    area, evidence = b.therapeutic_area(hit)
    assert area == 'oncology'
    assert evidence['matched'].lower() == 'myeloma'
