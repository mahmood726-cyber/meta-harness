"""Synthetic decision boundaries are test controls, not clinical evidence."""
import pytest
from harness import grade
from harness.limitations import _grade_block


def assess(low=0.60, high=0.99, scale="HR", **support):
    review = {"outcomes": [{"primary": True, "result": {
        "k": 3, "tau2": 0, "ci_low": low, "ci_high": high,
        "scale": scale, **support}}]}
    return grade.grade(review, {"pico_scoped": True})


def test_missing_denominator():
    g = assess()
    d = g["domains"]["publication_bias"]
    assert d["assessed"] is False
    assert d["state"] == "NOT_ASSESSABLE"
    assert d["ghost_fraction"] is None
    assert "0%" not in d["basis"]
    assert g["certainty"] == "provisional"
    assert "downgrade(s)" not in _grade_block(g)


@pytest.mark.parametrize("low,high,scale", [(0.60, 0.99, "HR"), (-10, -0.01, "MD"), (0.65, 1.00, "HR")])
def test_missing_precision_support(low, high, scale):
    g = assess(low, high, scale)
    d = g["domains"]["imprecision"]
    assert d["assessed"] is False
    assert d["state"] == "REQUIRES_JUDGEMENT"
    assert "clinical" in d["basis"] and "information" in d["basis"]
    assert str(low) in d["basis"] and str(high) in d["basis"]
    assert "-> precise" not in d["basis"]
    if high == 1.0:
        assert "uncertain_due_to_rounding" in d["basis"]
        assert "excludes the null" not in _grade_block(g)


@pytest.mark.parametrize("boundary,down", [(0.90, 1), (0.50, 0)])
def test_explicit_synthetic_positive_controls(boundary, down):
    g = assess(clinical_threshold={"value": boundary, "basis": "synthetic decision boundary"},
               information_size_assessment={"assessed": True, "adequate": True, "basis": "synthetic adequate information"})
    d = g["domains"]["imprecision"]
    assert d["assessed"] is True
    assert d["downgrade"] == down
    assert "clinical" in d["basis"]
    if not down:
        assert "precise" in d["basis"]

@pytest.mark.parametrize("support,missing", [
    ({"clinical_threshold": {"value": 0.5, "basis": "synthetic"}}, "information-size"),
    ({"information_size_assessment": {"assessed": True, "adequate": True, "basis": "synthetic"}}, "clinical"),
])
def test_each_precision_input_is_independently_required(support, missing):
    d = assess(**support)["domains"]["imprecision"]
    assert not d["assessed"]
    assert missing in d["basis"]


def test_rounding_requires_judgement_even_with_complete_support():
    d = assess(0.65, 1.0, clinical_threshold={"value": 0.5, "basis": "synthetic"},
               information_size_assessment={"assessed": True, "adequate": True, "basis": "synthetic"})["domains"]["imprecision"]
    assert d["state"] == "REQUIRES_JUDGEMENT"
    assert d["crosses_null"] is None
    assert "excludes the null" not in d["basis"]


@pytest.mark.parametrize("ghost", [None, {"pico_scoped": True, "enumerated": 0, "ongoing_or_recent": 0, "ghost_upper_bound": 0},
    {"pico_scoped": True, "enumerated": 2, "ongoing_or_recent": 3, "ghost_upper_bound": 0},
    {"pico_scoped": True, "enumerated": 2, "ongoing_or_recent": 0, "ghost_upper_bound": 3}])
def test_invalid_denominators_never_produce_a_fraction(ghost):
    d = grade._pubbias_domain(ghost)
    assert d["state"] == "NOT_ASSESSABLE"
    assert d["ghost_fraction"] is None
    assert d["missing_inputs"]


def test_complete_zero_unpublished_census_is_assessable():
    d = grade._pubbias_domain({"pico_scoped": True, "enumerated": 5,
                              "ongoing_or_recent": 0, "ghost_upper_bound": 0})
    assert d["assessed"] and d["ghost_fraction"] == 0


def test_inadequate_information_downgrades_despite_clear_boundary():
    d = assess(clinical_threshold={"value": 0.5, "basis": "synthetic"},
               information_size_assessment={"assessed": True, "adequate": False, "basis": "synthetic"})["domains"]["imprecision"]
    assert d["assessed"] and d["downgrade"] == 1


def test_missing_heterogeneity_and_risk_inputs_are_typed():
    g = grade.grade({"outcomes": [{"primary": True, "result": {"k": 3}}]})
    for key in ("risk_of_bias", "inconsistency", "imprecision", "publication_bias"):
        assert g["domains"][key]["state"] == "NOT_ASSESSABLE"
        assert g["domains"][key]["missing_inputs"]
    rendered = _grade_block(g)
    assert "NOT_ASSESSABLE" in rendered and "REQUIRES_JUDGEMENT" in rendered
    assert "downgrade(s)" not in rendered

def test_no_served_page_loses_a_downgrade():
    import json
    import subprocess
    from pathlib import Path
    from harness.pipeline import build_review_core
    from harness.registration import protocol_sha
    losses = []
    paths = sorted(Path('docs/reviews').glob('*/review.json'))
    assert len(paths) == 32
    for path in paths:
        slug = path.parent.name
        before = json.loads(subprocess.check_output(['git', 'show', 'HEAD:' + path.as_posix()]))
        config = json.loads(Path('topics', slug + '.json').read_text(encoding='utf-8'))
        records = json.loads(Path('cache', slug, 'records.json').read_text(encoding='utf-8'))
        after = build_review_core(slug, config, records, protocol_sha(slug))
        # Missing is not favourable: a page may carry no rating ONLY because its result is explicitly withdrawn
        # (a withdrawn result has no certainty to rate). A rating that vanishes without a withdrawal, or a
        # withdrawn page that still carries one, is a loss of every downgrade at once.
        if 'grade' not in before or 'grade' not in after:
            if not after.get('withdrawn') or 'grade' in after:
                losses.append((slug, 'GRADE object absent without a declared withdrawal'))
            continue
        for name, domain in before['grade']['domains'].items():
            if after['grade']['domains'][name]['downgrade'] < domain['downgrade']:
                losses.append((slug, name))
    assert losses == [], losses

@pytest.mark.parametrize('low,high', [(0.57, 1.78), (0.585, 1.235), (0.75, 1.1), (0.9, 1.25)])
def test_default_appreciable_downgrade_survives_missing_support(low, high):
    d = assess(low, high)['domains']['imprecision']
    assert d['downgrade'] == 1 and d['state'] == 'ASSESSED'
    assert 'GRADE default appreciable-effect thresholds 0.75/1.25; no topic threshold registered' in d['basis']


def test_tight_null_requires_judgement_without_support():
    d = assess(0.91, 1.08)['domains']['imprecision']
    assert d['downgrade'] == 0 and d['state'] == 'REQUIRES_JUDGEMENT'
    assert 'clinical' in d['basis'] and 'information-size' in d['basis']


def test_spanning_registered_threshold_downgrades_without_information_statement():
    d = assess(clinical_threshold={'value': 0.9, 'basis': 'synthetic'})['domains']['imprecision']
    assert d['downgrade'] == 1 and d['state'] == 'ASSESSED'


@pytest.mark.parametrize('scale', ['MD', 'SMD'])
def test_continuous_registered_mid_control(scale):
    d = assess(-2, 0.5, scale, clinical_threshold={'value': 1, 'basis': 'synthetic'})['domains']['imprecision']
    assert d['downgrade'] == 1 and d['state'] == 'ASSESSED'


def test_missing_ongoing_census_input_is_not_assessable():
    d = grade._pubbias_domain({'pico_scoped': True, 'enumerated': 25, 'ghost_upper_bound': 11})
    assert d['state'] == 'NOT_ASSESSABLE' and d['ghost_fraction'] is None
