"""Continuous sign plants; standalone verifier and producer, no served docs required."""
import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import contrast_order as co
import verify_bundle as vb
from harness import comparator_truth as truth, comparator_panel as panel

VOCAB = {"experimental": ["melatonin"], "reference": ["placebo"]}
I = "INTERVENTION_MINUS_COMPARATOR"
C = "COMPARATOR_MINUS_INTERVENTION"
R = "REDUCTION_POSITIVE_FAVOURS_INTERVENTION"
CLAUSE = "Melatonin reduced sleep-onset latency by 6.7 minutes (95% CI 0.2 to 13.6)."
SRC = {"estimate": "6.7", "ci_low": "0.2", "ci_high": "13.6"}
DST = {"estimate": "-6.7", "ci_low": "-13.6", "ci_high": "-0.2"}
OURS = {"estimate": -6.70, "ci_low": -13.63, "ci_high": 0.23, "orientation": I, "scale": "MD", "lower_is_better": True}
REG = {"orientation": I, "lower_is_better": True, "estimators_permitted": ["MD", "SMD"],
       "contrast_normalisation": {"negation_for_additive_measures": "PERMITTED_WHEN_DECLARED"}}
NORM = dict(DST, operation="NEGATION", orientation=I)


@pytest.mark.parametrize("clause,expected", [
    (CLAUSE, R),
    ("reduced sleep-onset latency by 6.7 minutes (95% CI 0.2 to 13.6)", R),
    ("placebo minus melatonin 6.7", C),
    ("melatonin minus placebo MD -6.7", I),
    ("intervention change minus comparator change MD -6.7", I),
    ("positive values favour melatonin; MD 6.7", R),
    ("improvement of 6.7 minutes", R),
    ("MD -6.7 (95% CI -13.6 to -0.2)", "NOT_STATED"),
    ("melatonin versus placebo MD -6.7", "NOT_STATED"),
    ("Placebo reduced latency by 6.7 minutes compared with melatonin", "NOT_STATED"),
    ("placebo minus melatonin; melatonin minus placebo MD 6.7", "NOT_STATED"),
])
def test_clause_plants_agree(clause, expected):
    a = co.ordered_contrast(clause, list(SRC.values()), VOCAB, scale="MD")
    b = vb.ordered_contrast(clause, list(SRC.values()), VOCAB, scale="MD")
    assert a == b
    assert a["orientation"] == expected
    witness = a["direction_witness"]
    if expected != "NOT_STATED":
        assert clause[witness["clause_start"]:witness["clause_end"]] == witness["text"]


@pytest.mark.parametrize("impl", [co, vb])
def test_negation_exact_at_source_precision_and_ci_sign_discrepancy(impl):
    assert impl.negation_reproduces(SRC, DST)
    assert impl.negation_reproduces(SRC, dict(DST, ci_low="-13.63", ci_high="-0.23"))
    # The user's +0.23 CI is NOT the negative of +0.2. Do not conceal it.
    assert not impl.negation_reproduces(SRC, OURS)
    assert not impl.negation_reproduces(SRC, SRC)
    assert not impl.negation_reproduces(SRC, dict(DST, ci_low="-0.2", ci_high="-13.6"))
    assert not impl.negation_reproduces(SRC, dict(DST, estimate="-6.8"))
    assert not impl.negation_reproduces(SRC, dict(DST, estimate="NaN"))
    assert not impl.negation_reproduces(SRC, dict(DST, ci_high=None))
    assert not impl.negation_reproduces(dict(SRC, estimate="6.70"), dict(DST, estimate="-6.74"))


@pytest.mark.parametrize("measure", ["MD", "SMD"])
@pytest.mark.parametrize("norm,reg,code", [
    (None, REG, "CONTINUOUS_ORIENTATION_DEPARTURE"),
    (NORM, REG, None),
    (NORM, {"orientation": I, "lower_is_better": True}, "CONTRAST_NORMALISATION_NOT_PERMITTED"),
    (dict(NORM, ci_high="0.23"), REG, "CONTRAST_NORMALISATION_NOT_REPRODUCED"),
    (dict(NORM, orientation=R), REG, "CONTRAST_NORMALISATION_NOT_REPRODUCED"),
    (dict(NORM, operation="RECIPROCAL"), REG, "CONTRAST_NORMALISATION_UNKNOWN"),
])
def test_declared_normalisation_and_departures_agree(measure, norm, reg, code):
    src = dict(SRC, orientation=R)
    a = co.additive_normalisation(src, measure, reg, norm)
    assert a == vb.additive_normalisation(src, measure, reg, norm)
    assert a["original"] == src
    assert (code in a["departures"]) if code else not a["departures"]
    oc = co.ordered_contrast(measure + " " + CLAUSE, list(SRC.values()), VOCAB, scale=measure)
    row = {"effect": dict(SRC, scale=measure, normalisation=norm),
           "analysis_identity": {"comparator_direction": {"value": R, "ordered_contrast": oc}}}
    check = vb.contrast_value_check(row, oc, {}, VOCAB, reg)
    departures = co.registered_departures(oc, measure, reg, VOCAB, norm)
    assert bool(check["p11"]) == bool(departures) == bool(code)
    if not code:
        assert not check["p10"]
        assert check["pooled"] == DST
        assert check["detail"]["normalisation"]["original"] == src


@pytest.mark.parametrize("impl", [co, vb])
def test_unknown_orientation_and_default_policy_fail_closed(impl):
    assert impl.normalisation_policy({}, "MD") == "FORBIDDEN"
    assert impl.normalisation_policy({"contrast_normalisation": {"reciprocal_for_ratio_measures": "PERMITTED_WHEN_DECLARED"}}, "SMD") == "FORBIDDEN"
    result = impl.additive_normalisation(dict(SRC, orientation="NOT_STATED"), "MD", REG, NORM)
    assert result["departures"] == ["CONTINUOUS_ORIENTATION_NOT_STATED"]
    assert result["normalisation"] is None


def test_comparator_never_equal_before_declared_negation_and_ci_still_differs():
    config = dict(REG, intervention_terms=["melatonin"], comparator_terms=["placebo"])
    rep = dict(SRC, scale="MD", source_clause=CLAUSE)
    original = copy.deepcopy(rep)
    undeclared = truth.continuous_comparison(rep, OURS, config, CLAUSE)
    assert undeclared["orientation"] == R
    assert undeclared["status"] == "DEPARTURE" and undeclared["equal"] is None
    declared = truth.continuous_comparison(dict(rep, normalisation=NORM), OURS, config, CLAUSE)
    assert declared["normalisation"]["original"] == dict(SRC, orientation=R)
    assert declared["status"] == "DIFFERENT_AFTER_ORIENTATION_CHECK" and declared["equal"] is False
    exact = truth.continuous_comparison(dict(rep, normalisation=NORM), dict(OURS, **DST), config, CLAUSE)
    assert exact["equal"] is True
    unknown = truth.continuous_comparison(rep, OURS, config, "")
    assert unknown["orientation"] == "NOT_STATED" and unknown["equal"] is None
    assert rep == original


def test_continuous_panel_renders_original_orientation_and_withholds_agreement():
    c = {"id": "plant", "citation": "Synthetic test plant", "scope_note": "test", "held": True,
         "document_ref": "plant.txt", "document_sha256": "test", "scale": "MD",
         "effect": {"value": 6.7, "span": {"start": 0, "end": len(CLAUSE), "quote": CLAUSE}},
         "ci": {"value": [0.2, 13.6], "span": {"start": 0, "end": len(CLAUSE), "quote": CLAUSE}},
         "trial_set": []}
    review = {"outcomes": [{"name": "Sleep-onset latency", "lower_is_better": True, "result": OURS}], "comparator_panel": [c]}
    markup = panel.render(review)
    assert R in markup and "DEPARTURE" in markup and "numeric agreement/disagreement withheld" in markup
    c["normalisation"] = NORM
    c["orientation_config"] = REG
    markup = panel.render(review)
    assert "Declared NEGATION" in markup and "DIFFERENT_AFTER_ORIENTATION_CHECK" in markup


def test_verifier_cannot_be_fooled_by_editing_only_typed_orientation():
    oc = co.ordered_contrast("MD " + CLAUSE, list(SRC.values()), VOCAB)
    row = {"effect": dict(SRC, scale="MD"), "analysis_identity": {"comparator_direction": {"value": R, "ordered_contrast": dict(oc, orientation=I)}}}
    assert "COMPARATOR_DIRECTION_MISMATCH" in [c for c, _ in vb.contrast_value_check(row, oc, {}, VOCAB, REG)["p10"]]


def test_verifier_uses_no_producer_import():
    import ast
    tree = ast.parse((ROOT / "scripts/verify_bundle.py").read_text(encoding="utf-8"))
    imports = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    imports += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
    assert not any("contrast_order" in name or name.startswith("harness") for name in imports)


def test_unrelated_or_wrong_sign_clause_does_not_authenticate_comparator():
    rep = dict(SRC, scale="MD", source_clause="placebo minus melatonin 9.1 (1.0 to 20.0)")
    audit = truth.continuous_comparison(rep, OURS, REG, rep["source_clause"])
    assert audit["orientation"] == "NOT_STATED"
    rep["source_clause"] = "placebo minus melatonin -6.7 (-13.6 to -0.2)"
    assert truth.continuous_comparison(rep, OURS, REG, rep["source_clause"])["orientation"] == "NOT_STATED"


def test_point_only_orientation_is_carried_but_not_claimed_equal():
    config = dict(REG, intervention_terms=["melatonin"], comparator_terms=["placebo"])
    clause = "placebo minus melatonin 6.7"
    audit = truth.continuous_comparison({"estimate": 6.7, "scale": "MD", "source_clause": clause}, OURS, config, clause)
    assert audit["orientation"] == C and audit["equal"] is None


def test_benefit_coding_requires_declared_endpoint_direction():
    src = dict(SRC, orientation=R)
    for impl in (co, vb):
        assert impl.additive_normalisation(src, "MD", {"orientation": I})["departures"]
        higher = impl.additive_normalisation(src, "MD", {"orientation": I, "lower_is_better": False})
        assert not higher["departures"] and higher["pooled"] == src


@pytest.mark.parametrize("impl", [co, vb])
def test_bare_continuous_clause_and_additive_measure_aliases(impl):
    assert impl.ordered_contrast(CLAUSE, list(SRC.values()), VOCAB)["orientation"] == R
    assert impl.clause_measure("standardized mean difference 0.2")["measure"] == "SMD"
    assert impl.clause_measure("standardised mean difference 0.2")["measure"] == "SMD"
    assert impl.clause_measure("weighted mean difference 6.7")["measure"] == "MD"
    assert impl.scale_measure("WMD") == "MD"


def test_producer_emits_continuous_orientation_without_ratio_favour_label(monkeypatch):
    import build_bundle
    monkeypatch.setattr(build_bundle, "registered_estimand", lambda slug: dict(
        REG, contrast=I, analysis_set="UNSTATED", treatment_strategy="UNSTATED", estimator="mean difference"))
    oc = co.ordered_contrast("MD " + CLAUSE, list(SRC.values()), VOCAB)
    ee = build_bundle.estimand_evidence("MD " + CLAUSE, "MD " + CLAUSE)
    result = build_bundle._analysis_identity({}, {"slug": "synthetic-plant"}, ee, oc)
    cd = result["comparator_direction"]
    assert cd["value"] == cd["orientation"] == R
    assert cd["ordered_contrast"] == oc
    assert "effect_less_than_1_favours" not in cd


def test_legacy_page_displays_unknown_and_declared_original():
    from harness.page import _comparator
    rep = dict(SRC, scale="MD", outcome="Latency")
    review = {"comparator": {"name": "Synthetic plant", "reported": [rep]}}
    assert "NOT_STATED" in _comparator(review, False)
    config = dict(REG, intervention_terms=["melatonin"], comparator_terms=["placebo"])
    rep["continuous_sign"] = truth.continuous_comparison(dict(rep, normalisation=NORM), OURS, config, CLAUSE)
    markup = _comparator(review, False)
    assert "Declared NEGATION" in markup and "Original:" in markup


def test_declaration_cannot_relax_source_precision_for_comparator_equality():
    clause = "melatonin reduced latency by 6.70 (95% CI 0.20 to 13.60)"
    rep = {"scale": "MD", "estimate": "6.70", "ci_low": "0.20", "ci_high": "13.60", "normalisation": NORM}
    audit = truth.continuous_comparison(rep, dict(OURS, estimate=-6.74, ci_low=-13.6, ci_high=-0.2), REG, clause)
    assert audit["normalisation"] and audit["equal"] is False


def test_ratio_source_relabelled_md_cannot_be_negated_into_agreement():
    clause = "positive values favour melatonin: HR 6.7 (95% CI 0.2 to 13.6)"
    rep = dict(SRC, scale="MD", normalisation=NORM)
    config = dict(REG, intervention_terms=["melatonin"])
    audit = truth.continuous_comparison(rep, dict(OURS, **DST), config, clause)
    assert "CONTINUOUS_SOURCE_MEASURE_MISMATCH" in audit["departures"] and audit["equal"] is None
    assert audit["normalisation"] is None and audit["pooled"] == audit["original"]
