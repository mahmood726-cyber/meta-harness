"""FIX2 planted contradictions: run before implementation on the recorded base."""
import json
from pathlib import Path

from harness import gate, grade, manuscript, limitations
import pytest
import re

ROOT = Path(__file__).resolve().parents[1]


def review():
    return json.loads((ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json').read_text(encoding='utf-8'))


def test_unassessed_is_provisional():
    g = grade.grade(review())
    assert g['certainty'] == 'provisional'


def test_machine_rob_not_formal():
    assert grade._rob_domain(review())['assessed'] is False


def test_incomplete_membership_not_homogeneity():
    assert grade.grade(review())['domains']['inconsistency']['assessed'] is False


def test_identical_rob_pool_not_rendered():
    text = limitations._rob_sensitivity_block(review()['rob_sensitivity'])
    assert 'Low risk of bias only' not in text
    assert 'suppressed' in text


def test_certainty_surface_plant_refused(tmp_path):
    r = review()
    r['grade']['certainty'] = 'provisional'
    r['grade']['certainty_state'] = 'GRADE provisional -- not yet fully assessable'
    (tmp_path / 'review.json').write_text(json.dumps(r), encoding='utf-8')
    (tmp_path / 'index.html').write_text('<p>Partial GRADE certainty was <strong>moderate</strong></p>', encoding='utf-8')
    assert gate.check_certainty_surfaces_agree(tmp_path)


def test_identical_pool_surface_plant_refused(tmp_path):
    (tmp_path / 'review.json').write_text(json.dumps(review()), encoding='utf-8')
    (tmp_path / 'index.html').write_text('<tr><td>Low risk of bias only</td><td>k=8</td></tr>', encoding='utf-8')
    assert gate.check_rob_sensitivity_surfaces(tmp_path)


def test_homogeneity_surface_plant_refused(tmp_path):
    (tmp_path / 'review.json').write_text(json.dumps(review()), encoding='utf-8')
    (tmp_path / 'index.html').write_text('<p>The pool is homogeneous; prediction interval not markedly wider than the CI.</p>', encoding='utf-8')
    assert gate.check_stale_heterogeneity_surfaces(tmp_path)


@pytest.mark.parametrize('surface', ['overview', 'riskofbias', 'manuscript', 'reporting'])
def test_mutated_surface_refused_with_other_surfaces_intact(tmp_path, surface):
    from harness.page import render_page
    r = review()
    r['grade'] = grade.grade(r)
    html = render_page(r)
    pattern = r'(<section class="tab" id="tab-' + surface + r'">)(.*?)(</section>)'
    match = re.search(pattern, html, re.S)
    assert match and grade.PROVISIONAL in match.group(2)
    html = html[:match.start(2)] + match.group(2).replace(grade.PROVISIONAL, 'moderate', 1) + html[match.end(2):]
    (tmp_path / 'review.json').write_text(json.dumps(r), encoding='utf-8')
    (tmp_path / 'index.html').write_text(html, encoding='utf-8')
    assert gate.check_certainty_surfaces_agree(tmp_path)


def test_membership_trigger_is_specific():
    r = {'invalidation': {'reasons': [{'code': 'search_not_executed'}]}}
    assert not grade.membership_incomplete(r)
    r['invalidation']['reasons'].append({'code': 'eligible_declared_absent'})
    assert grade.membership_incomplete(r)
    assert grade.membership_incomplete({'outcomes': [{'primary': True, 'known_missing_sensitivity': {'rows': [{'trial_key': 'fixture'}]}}]})


def test_formal_nonidentical_sensitivity_remains_available():
    sens = {'formally_assessed': True, 'full': {'k': 3}, 'low_only': {'k': 2}}
    from harness.rob_sensitivity import suppression_reason
    assert not suppression_reason(sens)
    sens['low_only']['k'] = 3
    assert 'equals the full pool' in suppression_reason(sens)
