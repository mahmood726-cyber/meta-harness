"""CONTINUOUS-OUTCOME identity (external review of esketamine-trd-madrs, 2026-09-27, hash f5b8f4cb).

Plants run on the held registry bytes at the pinned candidate 3876a62d (a missing commit fails, never skips):
  * SE != SD: TRANSFORM-2's registry analysis states the SE OF THE DIFFERENCE, 1.69, beside arm SDs 12.32 / 13.88;
  * flexible CI: TRANSFORM-3's held abstract gives a median-unbiased estimate with a weighted-combination interval, so its
    width is not 2 z SE -- CI / 3.92 is refused; TRANSFORM-2's "flexible doses" is dosing, not an interval procedure;
  * combined doses: TRANSFORM-1 (56 mg, 84 mg, placebo) is refused by the multi-arm guard without a rule, and under the
    declared rule becomes one arm against the placebo counted ONCE;
  * primary vs sensitivity: the protocol's primary is raw per-arm mean/SD; its missing-data assumption is not declared.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import continuous_identity as ci, synth   # noqa: E402
from harness.ctgov_results import _extract_ctgov_continuous, extract_ctgov   # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
SLUG = "esketamine-trd-madrs"


def _show(path):
    p = subprocess.run(["git", "show", f"{PINNED}:{path}"], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        pytest.fail(f"{PINNED[:8]}:{path} not in history (never a skip)", pytrace=False)
    return p.stdout.decode("utf-8")


@pytest.fixture(scope="module")
def held():
    return json.loads(_show(f"cache/{SLUG}/records.json"))


@pytest.fixture(scope="module")
def topic():
    return json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))


def _om(held, nct):
    return held["ctgov_results"][nct][0]


def _abstract(held, pmid):
    return next(r["abstract"] for r in held["records"] if str(r["id"]) == pmid)


# ------------------------------------------------------------------ (1) typed fields; SE is never an arm SD
def test_typed_fields_separate_arm_sd_se_of_difference_raw_and_adjusted(held):
    tm = ci.typed_measure(_om(held, "NCT02418585"))                        # TRANSFORM-2
    assert [(a["mean_change"], a["dispersion"], a["dispersion_kind"], a["n_observed"]) for a in tm["arms"]] == \
        [(-21.4, 12.32, "SD", 101.0), (-17.0, 13.88, "SD", 100.0)]        # raw, observed at Day 28 (FAS is 114/109)
    assert all(a["estimate_kind"] == "RAW_ARM_MEAN" for a in tm["arms"])
    (an,) = tm["analyses"]
    assert (an["estimate_kind"], an["value"], an["se_of_difference"]) == ("ADJUSTED_DIFFERENCE", -4.0, 1.69)
    assert round(tm["arms"][0]["mean_change"] - tm["arms"][1]["mean_change"], 1) == -4.4      # raw -4.4 vs adjusted -4.0


def test_plant_the_se_of_a_difference_is_never_an_arm_sd(held):
    (an,) = ci.typed_measure(_om(held, "NCT02418585"))["analyses"]
    with pytest.raises(ci.NotAnArmSD):
        ci.arm_sd(an["se_of_difference"], "SE")                          # 1.69 offered as an arm SD
    with pytest.raises(ci.NotAnArmSD):
        ci.arm_sd(2.1, "CI")
    assert ci.arm_sd(12.32, "SD") == 12.32


def test_plant_an_se_dispersion_measure_is_refused_by_the_registry_route(held):
    om = dict(_om(held, "NCT02418585"), dispersionType="Standard Error")    # the same arms, labelled SE
    assert _extract_ctgov_continuous(om, ["esketamine"], ["placebo"]) is None
    with pytest.raises(ci.NotAnArmSD):
        ci.combine_arms([{"mean": -19.0, "sd": 1.3, "dispersion_kind": "SE", "n": 111},
                         {"mean": -18.8, "sd": 1.4, "dispersion_kind": "SE", "n": 98}])


# ------------------------------------------------------------------ CI procedure
def test_plant_a_stage_weighted_ci_is_refused_for_the_width_derivation(held, topic):
    t3 = _abstract(held, "31734084")                                      # TRANSFORM-3 held abstract
    (an,) = ci.typed_measure(_om(held, "NCT02422186"))["analyses"]
    assert an["ci"] == {"level": 95.0, "sidedness": "two-sided", "low": -7.2, "high": 0.07}   # registry says "95% two-sided"
    proc = ci.ci_procedure([t3], an["ci"])
    assert proc["procedure"] == ci.FLEXIBLE and "median-unbiased" in proc["evidence"]
    with pytest.raises(ValueError, match="STAGE_WEIGHTED_FLEXIBLE"):
        ci.se_from_ci(an["ci"], proc)
    row = ci.model_based_row(_om(held, "NCT02422186"), [t3], None)
    assert row["state"] == "SE_NOT_ESTABLISHED" and row["value"] == -3.6
    # the declared procedure (EMA footnote, cited by the review) refuses it even with no held text
    decl = topic["primary_outcome"]["ci_procedure_declared"]["NCT02422186"]
    assert ci.ci_procedure([], an["ci"], decl)["procedure"] == ci.FLEXIBLE


def test_flexible_doses_is_not_a_flexible_interval_and_a_standard_ci_gives_its_se(held):
    t2 = _abstract(held, "31109201")                                      # TRANSFORM-2: "flexible doses"
    (an,) = ci.typed_measure(_om(held, "NCT02418585"))["analyses"]
    proc = ci.ci_procedure([t2, "flexibly dosed esketamine 56 or 84 mg"], an["ci"])
    assert proc["procedure"] == ci.STANDARD
    assert abs(ci.se_from_ci(an["ci"], proc) - 1.69) < 0.02                # width / 3.92 agrees with the stated 1.69
    assert ci.difference_se(an, proc) == {"se": 1.69, "basis": "stated SE of the difference (registry analysis)"}


# ------------------------------------------------------------------ (2) combined doses
def test_plant_without_a_rule_the_three_arm_trial_is_refused_and_served_absent(held):
    om = _om(held, "NCT02417064")
    assert _extract_ctgov_continuous(om, ["esketamine"], ["placebo"]) is None
    rv = json.loads(_show(f"docs/reviews/{SLUG}/review.json"))
    o = next(x for x in rv["outcomes"] if x.get("primary"))
    assert "NCT02417064" not in [t["id"] for t in o["trials"]] and o["result"]["k"] == 3


def test_the_declared_rule_combines_eligible_doses_against_placebo_counted_once(held, topic):
    rule = topic["primary_outcome"]["combine_eligible_doses"]
    cg = extract_ctgov(held["ctgov_results"]["NCT02417064"], topic["primary_outcome"]["keywords"],
                       topic["intervention_terms"], topic["comparator_terms"], combine_rule=rule)
    assert (cg["mean1"], cg["sd1"], cg["nc1"], cg["mean2"], cg["sd2"], cg["nc2"]) == (-18.9062, 13.9491, 209, -14.8, 15.07, 108)
    rec = cg["multi_arm_combined"]
    assert rec["shared_comparator"]["counted"] == "once" and [a["n"] for a in rec["arms"]] == [111, 98]
    assert rec["prespecified_in_trial"] is False and "NOT demonstrably prospective" in rule["registration"]
    # the placebo appears once: 209 + 108 = 317 participants, not 111 + 108 + 98 + 108
    assert cg["nc1"] + cg["nc2"] == 317


def test_a_rule_never_drops_an_arm_it_does_not_name(held):
    rule = {"eligible_arm_terms": ["56 mg"], "basis": "plant"}             # 84 mg arm not named
    assert ci.combined_contrast(_om(held, "NCT02417064"), ["esketamine"], ["placebo"], rule) is None


def test_adding_transform1_takes_k3_to_k4_and_the_interval_stops_spanning_zero(held, topic):
    rv = json.loads(_show(f"docs/reviews/{SLUG}/review.json"))
    o = next(x for x in rv["outcomes"] if x.get("primary"))
    def st(t):
        return synth.Study(label=t["id"], mean1=t["mean1"], sd1=t["sd1"], nc1=t.get("nc1"), mean2=t["mean2"], sd2=t["sd2"],
                           nc2=t.get("nc2"), measure="MD")
    served = [dict(t) for t in o["trials"]]
    for t in served:                                                        # served rows carry n in the quoted source
        import re
        n = [int(x) for x in re.findall(r"n=(\d+)", t["source"])]
        t["nc1"], t["nc2"] = n[0], n[1]
    k3 = synth.pool([st(t) for t in served], scale="MD")
    assert (round(k3.estimate, 4), round(k3.ci_low, 4), round(k3.ci_high, 4)) == (-3.1004, -7.3323, 1.1315)   # served
    cg = extract_ctgov(held["ctgov_results"]["NCT02417064"], topic["primary_outcome"]["keywords"], topic["intervention_terms"],
                       topic["comparator_terms"], combine_rule=topic["primary_outcome"]["combine_eligible_doses"])
    k4 = synth.pool([st(t) for t in served] + [st(dict(cg, id="NCT02417064"))], scale="MD")
    assert k4.k == 4 and (round(k4.estimate, 3), round(k4.ci_low, 3), round(k4.ci_high, 3)) == (-3.344, -6.069, -0.618)
    # the review's diagnostic -3.342 (-6.068, -0.616) uses Table 4's rounded -18.9 / 13.95; the held registry arms give the above
    t4 = synth.pool([st(t) for t in served] + [synth.Study(label="T1", mean1=-18.9, sd1=13.95, nc1=209, mean2=-14.8, sd2=15.07,
                                                           nc2=108, measure="MD")], scale="MD")
    assert (round(t4.estimate, 3), round(t4.ci_low, 3), round(t4.ci_high, 3)) == (-3.342, -6.068, -0.616)


# ------------------------------------------------------------------ (3) primary vs sensitivity
def test_the_primary_is_named_and_its_missing_data_assumption_is_reported_undeclared(topic):
    plan = ci.analysis_plan(topic["primary_outcome"])
    assert plan["primary"]["kind"] == "RAW_ARM_MEAN_SD" and "never a least-squares mean" in plan["primary"]["protocol_quote"]
    assert plan["state"] == "MISSING_DATA_ASSUMPTION_NOT_DECLARED"       # the registered protocol does not state one
    assert ci.analysis_plan({})["state"] == "PRIMARY_ANALYSIS_NOT_DECLARED"
    declared = {"analysis_plan": {"primary": {"kind": "RAW_ARM_MEAN_SD", "missing_data_assumption": "MAR"}}}
    assert ci.analysis_plan(declared)["state"] == "DECLARED"


def test_model_based_sensitivity_admits_only_established_ses(held):
    t2 = ci.model_based_row(_om(held, "NCT02418585"), [_abstract(held, "31109201")], None)
    assert (t2["state"], t2["value"], t2["se"]) == ("ADMITTED", -4.0, 1.69)
    t1 = ci.model_based_row(_om(held, "NCT02417064"), [], None)
    assert t1["state"] == "PER_DOSE_ADJUSTED_ONLY"                         # no combined adjusted difference is constructed
    t3 = ci.model_based_row(_om(held, "NCT02422186"), [_abstract(held, "31734084")], None)
    assert t3["state"] == "SE_NOT_ESTABLISHED"


# ------------------------------------------------------------------ n observed vs n in the analysis set (census finding)
def test_plant_the_class_level_n_behind_a_mean_sd_is_used_not_the_measure_level_fas_n():
    """STEP 1 (NCT03548935): the mean/SD (-15.6, 10.1 vs -2.8, 6.5) are the class 'In-trial observation period', whose own
    denominators are 1212/577; the measure-level 1306/655 is the FAS. Served at 3876a62d with 1306/655 (SE understated)."""
    held = json.loads(_show("cache/semaglutide-obesity-weight/records.json"))
    t = json.load(open(os.path.join(ROOT, "topics", "semaglutide-obesity-weight.json"), encoding="utf-8"))
    rv = json.loads(_show("docs/reviews/semaglutide-obesity-weight/review.json"))
    served = next(x for o in rv["outcomes"] for x in o["trials"] if "33567185" in str(x["id"]))
    assert (served["nc1"], served["nc2"]) == (1306, 655)                                   # the plant: served FAS n
    cg = extract_ctgov(held["ctgov_results"]["NCT03548935"], t["primary_outcome"]["keywords"], t["intervention_terms"],
                       t["comparator_terms"])
    assert (cg["mean1"], cg["sd1"], cg["nc1"], cg["mean2"], cg["sd2"], cg["nc2"]) == (-15.6, 10.1, 1212, -2.8, 6.5, 577)
    assert cg["n_analysis_set"] == {"nc1": 1306.0, "nc2": 655.0}
    arms = ci.typed_measure(held["ctgov_results"]["NCT03548935"][0])["arms"]
    assert [(a["n_observed"], a["n_analysis_set"]) for a in arms] == [(1212, 1306.0), (577, 655.0)]


def test_a_measure_without_class_denominators_is_unchanged(held):
    om = _om(held, "NCT02418585")
    cg = _extract_ctgov_continuous(om, ["esketamine"], ["placebo"])
    assert (cg["nc1"], cg["nc2"], cg["n_source"]) == (101, 100, "measure-level denominators") and "n_analysis_set" not in cg


# ------------------------------------------------------------------ fixture finding: no fall-through, no silent dose pick
def test_plant_a_continuous_outcome_never_falls_through_to_a_responder_count(held, topic):
    """Codex fixture finding: without a combine rule, extract_ctgov refused TRANSFORM-1's MEAN measure and then returned the
    '>=50% reduction' responder percentage, 53/98 vs 38/108 -- a count row for an MD outcome, from the 84 mg arm alone."""
    oms = held["ctgov_results"]["NCT02417064"]
    kw, iv, cp = topic["primary_outcome"]["keywords"], topic["intervention_terms"], topic["comparator_terms"]
    assert extract_ctgov(oms, kw, iv, cp, estimand="MD") is None                       # continuous: no fall-through
    assert extract_ctgov(oms, kw, iv, cp) is None                                      # counts: two dose arms -> refused


def test_the_counts_route_still_reads_a_two_arm_measure():
    om = {"title": "Number of Participants With Response", "type": "PRIMARY", "paramType": "COUNT_OF_PARTICIPANTS",
          "groups": [{"id": "A", "title": "Esketamine"}, {"id": "B", "title": "Placebo"}],
          "denoms": [{"units": "Participants", "counts": [{"groupId": "A", "value": "100"}, {"groupId": "B", "value": "100"}]}],
          "classes": [{"categories": [{"measurements": [{"groupId": "A", "value": "40"}, {"groupId": "B", "value": "30"}]}]}]}
    cg = extract_ctgov([om], ["response"], ["esketamine"], ["placebo"])
    assert (cg["ai"], cg["n1i"], cg["ci"], cg["n2i"]) == (40, 100, 30, 100)
