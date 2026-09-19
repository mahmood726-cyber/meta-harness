import copy
import json
import re
from html import unescape
from pathlib import Path

from harness import page

ROOT = Path(__file__).resolve().parents[1]


def text(html):
    return ' '.join(unescape(re.sub(r'<[^>]+>', ' ', html)).split())


def review():
    return json.loads((ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json').read_text(encoding='utf-8'))


def item5(html):
    return next(text(row) for row in re.findall(r'<tr\b[^>]*>.*?</tr>', html, re.S)
                if '5 Eligibility criteria' in row)


def test_PLANT_committed_glp1_no_vacuous_agreement():
    html = page.render_page(review())
    rendered = text(html)
    row = item5(html)
    vacuous = 'agree on these checked dimensions: none' in rendered
    backed = 'declared == enforced is backed' in row or '✓' in row
    assert not (vacuous and backed and 'NOT ESTABLISHED' not in rendered), row


def test_PLANT_zero_dimension_proposition_never_tick():
    r = copy.deepcopy(review())
    r['protocol_config'] = {'checked_dimensions': [], 'divergences': []}
    state = {'state': 'NOT_ESTABLISHED', 'checked_dimensions': [],
             'divergences': [], 'basis': 'no dimension was checked'}
    r.setdefault('propositions', {})['declared_equals_enforced'] = state
    r['propositions']['objects'] = [dict(kind='declared_equals_enforced', **state)]
    html = page.render_page(r)
    assert 'NOT ESTABLISHED' in text(html)
    assert 'declared == enforced: NOT ESTABLISHED' in item5(html)
    assert '✓' not in item5(html)


def test_comparison_established_divergent_and_empty():
    from harness import protocol_compiler as pc, propositions as p
    md = '- **Estimand** - hazard ratio (HR).'
    for config, expected in [({}, 'NOT_ESTABLISHED'),
                             ({'primary_outcome': {'estimand': 'HR'}}, 'ESTABLISHED'),
                             ({'primary_outcome': {'estimand': 'RR'}}, 'DIVERGENT')]:
        comparison = pc.comparison('synthetic', md, config)
        r = {'protocol_config': comparison, 'protocol': {'eligibility': 'synthetic'}}
        state = p.declared_equals_enforced(r)
        assert state['state'] == expected
        attached = p.attach(r)
        obj = next(o for o in attached['propositions']['objects'] if o['kind'] == 'declared_equals_enforced')
        assert obj['asserted_equal'] == (expected == 'ESTABLISHED')
        assert obj['state'] == expected
        assert p.check_propositions(attached) == []


def test_glp1_comparison_names_only_comparable_dimensions():
    from harness import protocol_compiler as pc
    config = json.loads((ROOT / 'topics/glp1-ra-mace-t2d.json').read_text(encoding='utf-8'))
    md = (ROOT / 'protocols/glp1-ra-mace-t2d.md').read_text(encoding='utf-8')
    result = pc.comparison('glp1-ra-mace-t2d', md, config)
    assert {'estimand', 'analysis_set', 'intervention_i_line'} <= set(result['checked_dimensions'])
    assert 'ascertainment_axis' not in result['checked_dimensions']
    assert 'result_availability_not_axis' not in result['checked_dimensions']
    assert len(result['unchecked_dimensions']) == 2
    config['primary_outcome']['estimand'] = 'RR'
    assert any(d['code'] == 'ESTIMAND_DIVERGENCE' for d in pc.comparison('glp1-ra-mace-t2d', md, config)['divergences'])


def test_forged_zero_dimension_agreement_rejected():
    from harness import propositions as p
    r = p.attach({'protocol': {'eligibility': 'synthetic'},
                  'protocol_config': {'checked_dimensions': [], 'divergences': []}})
    obj = next(o for o in r['propositions']['objects'] if o['kind'] == 'declared_equals_enforced')
    obj['asserted_equal'] = True
    assert any(v['code'] == 'DECLARED_ENFORCED_FALSE' for v in p.check_propositions(r))


def test_zero_dimensions_retain_divergence_without_establishing_agreement():
    from harness import propositions as p
    r = review()
    r['protocol_config'] = {'checked_dimensions': [], 'divergences': [
        {'code': 'SYNTHETIC_DIVERGENCE', 'dimension': 'synthetic', 'prose': 'a', 'config': 'b'}]}
    r.pop('propositions', None)
    assert p.declared_equals_enforced(r)['state'] == 'NOT_ESTABLISHED'
    row = item5(page.render_page(r))
    assert 'NOT ESTABLISHED' in row and 'SYNTHETIC_DIVERGENCE' in row and '✓' not in row


def test_empty_intervention_declarations_are_not_checked_dimensions():
    from harness import protocol_compiler as pc, propositions as p
    config = {'intervention_terms': [], 'intervention_agents': {}, 'intervention_class_terms': []}
    comparison = pc.comparison('synthetic', '', config)
    assert comparison['checked_dimensions'] == []
    assert p.declared_equals_enforced({'protocol_config': comparison})['state'] == 'NOT_ESTABLISHED'
