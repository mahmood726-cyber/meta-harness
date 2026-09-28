"""Semaglutide-weight review (rule hash e209c1d5, 2026-09-28; RETROSPECTIVE, decided by Dispatch under Mahmood's delegation).

(1) a raw mean/SD uses the n that CONTRIBUTED the observations; an imputed registry summary is held;
(2) the estimand label is derived from the analysis actually used -- raw observed summaries are not "treatment-policy";
(3) the primary is the published model-based treatment-policy difference by generic inverse variance (SE from the reported CI,
    never an arm SD); raw observed data is a labelled sensitivity analysis.
"""
import json
import os
import subprocess
import types

import pytest

from harness import continuous_identity as ci

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "c15ed111"
SLUG = "semaglutide-obesity-weight"


def _held_measure(nct, title="Change in Body Weight (%)"):
    recs = json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"), encoding="utf-8"))
    return next(o for o in recs["ctgov_results"][nct] if o.get("title") == title)


def _prefix_module():
    src = subprocess.check_output(["git", "show", f"{BASE}:harness/continuous_identity.py"], cwd=ROOT, text=True, encoding="utf-8")
    mod = types.ModuleType("continuous_identity_prefix")
    mod.__dict__["__name__"] = "continuous_identity_prefix"
    exec(compile(src, f"continuous_identity@{BASE}", "exec"), mod.__dict__)
    return mod


@pytest.mark.parametrize("nct,value,low,high", [("NCT03548935", -12.44, -13.37, -11.51), ("NCT03611582", -10.27, -11.97, -8.57)])
def test_plant_prefix_could_not_admit_the_ancova_treatment_policy_difference(nct, value, low, high):
    om = _held_measure(nct)
    pre = _prefix_module().model_based_row(om, [], None)
    # pre-fix: "Treatment difference" by ANCOVA was untyped, so the published treatment-policy difference could not be used
    assert pre["state"] == "NO_ADJUSTED_DIFFERENCE"
    row = ci.model_based_row(om, [], None, estimand="TREATMENT_POLICY")
    assert row["state"] == "ADMITTED" and row["estimand"] == "TREATMENT_POLICY" and row["method"] == "ANCOVA"
    assert (row["value"], row["ci"]["low"], row["ci"]["high"]) == (value, low, high)
    assert row["se"] == round((high - low) / (2 * 1.959963984540054), 4)


def test_two_estimands_on_the_same_arms_are_not_two_doses_and_none_is_picked():
    om = _held_measure("NCT03548935")
    row = ci.model_based_row(om, [], None)
    assert row["state"] == "ESTIMAND_NOT_SELECTED"
    assert row["reported_estimands"] == ["HYPOTHETICAL", "TREATMENT_POLICY"]
    assert ci.model_based_row(om, [], None, estimand="HYPOTHETICAL")["value"] == -14.42


def test_declared_estimand_not_reported_is_named_not_assumed():
    # STEP 8's only analysis is semaglutide vs LIRAGLUTIDE with no estimand label: never taken as the treatment-policy estimate
    om = next(o for o in json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"), encoding="utf-8"))["ctgov_results"]["NCT04074161"]
              if o.get("type") == "PRIMARY")
    assert ci.model_based_row(om, [], None, estimand="TREATMENT_POLICY")["state"] == "DECLARED_ESTIMAND_NOT_REPORTED"


def test_observed_contribution_states():
    assert ci.observed_contribution(_held_measure("NCT03548935"))["state"] == "OBSERVED"
    imputed = {"populationDescription": "Full analysis set. Missing data were imputed using multiple imputation (retrieved dropouts)."}
    assert ci.observed_contribution(imputed)["state"] == "IMPUTED"
    fas_only = {"populationDescription": "Overall number of participants analyzed = full analysis set (FAS)."}
    assert ci.observed_contribution(fas_only)["state"] == "NOT_ESTABLISHED"


def test_raw_label_is_never_treatment_policy():
    lab = ci.estimand_label("RAW_OBSERVED")
    assert lab.startswith("observed data") and "not a treatment-policy estimate" in lab
    assert ci.estimand_label("MODEL_BASED", "TREATMENT_POLICY", "ANCOVA").startswith("treatment-policy estimand")


def test_an_se_of_the_difference_is_never_an_arm_sd():
    with pytest.raises(ci.NotAnArmSD):
        ci.arm_sd(0.4745, "SE")


def _live():
    p = os.path.join(ROOT, "docs", "reviews", SLUG, "review.json")
    if not os.path.exists(p):
        pytest.skip("built review not present in this worktree")
    return json.load(open(p, encoding="utf-8"))


def test_built_primary_is_model_based_and_raw_is_a_labelled_sensitivity():
    o = next(x for x in _live()["outcomes"] if x.get("primary"))
    rows = {str(t["id"]): t for t in o["trials"]}
    s1, s3 = rows["PMID 33567185"], rows["PMID 33625476"]
    assert (s1["effect"], s1["ci_low"], s1["ci_high"]) == (-12.44, -13.37, -11.51)
    assert (s3["effect"], s3["ci_low"], s3["ci_high"]) == (-10.27, -11.97, -8.57)
    for t in (s1, s3):
        assert t.get("mean1") is None and t["selection_rule"] == "ANALYSIS_PLAN_PRIMARY_MODEL_BASED_DIFFERENCE"
        assert t["estimand_label"].startswith("treatment-policy estimand")
    assert o["result"]["k"] == 2 and o["result"]["scale"] == "MD"
    sens = o["continuous_analysis"]["raw_observed_sensitivity"]
    n = {str(r["id"]): (r["nc1"], r["nc2"]) for r in sens["rows"]}
    # (1) the n that contributed the observations -- never the full-analysis-set count
    assert n == {"PMID 33567185": (1212, 577), "PMID 33625476": (373, 189)}
    assert sens["label"].startswith("observed data")
    assert "treatment-policy" not in (o.get("population") or "")


def test_built_step8_pooled_placebo_is_named_supportive_never_pooled():
    # (4) STEP 8 is screened in at comparison level (matched placebo); the held registry reports weight only against a POOLED
    # placebo, which is not the eligible contrast: named, shown as supportive, and in neither the primary nor the sensitivity
    o = next(x for x in _live()["outcomes"] if x.get("primary"))
    ids = lambda rows: {str(r.get("id")) for r in rows}
    ab = [a for a in o["declared_absent_trials"] if "NCT04074161" in str(a.get("id"))]
    assert len(ab) == 1 and ab[0]["state"] == "POOLED_PLACEBO_NOT_THE_ELIGIBLE_CONTRAST"
    assert ab[0]["matched_placebo"] == "NOT_REPORTED_IN_HELD_SOURCES"
    assert ab[0]["supportive_pooled_placebo"]["nc2"] == 78
    assert not any("NCT04074161" in i for i in ids(o["trials"]))
    assert not any("NCT04074161" in i for i in ids(o["continuous_analysis"]["raw_observed_sensitivity"]["rows"]))


def test_plant_fallback_took_an_active_arm_as_the_placebo_comparator():
    # STEP 8's primary registry measure is semaglutide vs LIRAGLUTIDE. The pre-fix 2-arm fallback assigned "Liraglutide 3.0 mg"
    # as the comparator of a semaglutide-vs-placebo question; the fallback now fills the comparator only with a control arm.
    from harness import ctgov_results as cr
    om = next(o for o in json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"), encoding="utf-8"))["ctgov_results"]["NCT04074161"]
              if o.get("type") == "PRIMARY")
    src = subprocess.check_output(["git", "show", f"{BASE}:harness/ctgov_results.py"], cwd=ROOT, text=True, encoding="utf-8")
    pre = types.ModuleType("ctgov_results_prefix")
    pre.__dict__.update(__name__="ctgov_results_prefix", __package__="harness")
    exec(compile(src, f"ctgov_results@{BASE}", "exec"), pre.__dict__)
    iv, cp = ["semaglutide 2.4 mg", "semaglutide"], ["placebo", "control"]
    assert pre._classify_arms(om["groups"], iv, cp) == ("OG000", "OG001")      # OG001 = Liraglutide 3.0 mg
    assert cr._classify_arms(om["groups"], iv, cp) == ("OG000", None)
    ctl = [{"id": "A", "title": "Semaglutide 2.4 mg"}, {"id": "B", "title": "Arm 1: Inactive Substance"}]
    assert cr._classify_arms(ctl, iv, cp) == ("A", "B")                        # a control arm still fills the fallback
