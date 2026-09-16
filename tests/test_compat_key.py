"""Pooling compatibility key: assembles the six-dimension key per pooled outcome, and a backstop
that refuses a pool mixing incompatible effect-measure classes."""
import harness.compat as CM


def _core(outcome, arm_contrast=None):
    c = {"outcomes": [outcome]}
    if arm_contrast is not None:
        c["arm_contrast"] = {"trials": arm_contrast}
    return c


def test_key_assembled_for_pool():
    o = {"name": "All-cause mortality", "primary": True, "timepoint": "28-day",
         "population": "intention-to-treat",
         "result": {"k": 2, "estimate": 0.8, "scale": "RR",
                    "estmeasure": {"status": "homogeneous", "classes": ["FIRST_EVENT_RATIO"],
                                   "labels": ["RR"], "canonicals": ["RISK_RATIO"]}},
         "trials": [{"id": "PMID 111"}, {"id": "PMID 222"}]}
    k = CM.outcome_key(o, _core(o, {"111": {"status": "verified"}, "222": {"status": "unverified"}}))
    assert k["matched"] is True
    assert k["event_process"] == ["FIRST_EVENT_RATIO"]
    assert k["follow_up_window"] == "28-day" and k["analysis_set"] == "intention-to-treat"
    assert k["randomised_contrast"] == {"verified": 1, "total": 2}


def test_no_key_for_suppressed_or_absent():
    assert CM.outcome_key({"name": "x", "result": {"suppressed_incompatible": True, "k": 3}}, {}) is None
    assert CM.outcome_key({"name": "x", "result": {"present": False}}, {}) is None
    assert CM.outcome_key({"name": "x", "result": {"k": 0}}, {}) is None


def test_backstop_fires_on_incompatible_class_in_a_pool():
    o = {"name": "MACE", "primary": True,
         "result": {"k": 2, "estimate": 0.9, "scale": "RR",
                    "estmeasure": {"status": "incompatible", "classes": ["FIRST_EVENT_RATIO", "RATE"],
                                   "labels": ["RR", "IRR"], "canonicals": ["RISK_RATIO", "INCIDENCE_RATE_RATIO"]}},
         "trials": [{"id": "PMID 1"}, {"id": "PMID 2"}]}
    bad = CM.check(_core(o))
    assert len(bad) == 1 and bad[0]["outcome"] == "MACE"


def test_backstop_clean_on_homogeneous_pool():
    o = {"name": "MACE", "primary": True,
         "result": {"k": 2, "estimate": 0.9, "scale": "RR",
                    "estmeasure": {"status": "homogeneous", "classes": ["FIRST_EVENT_RATIO"],
                                   "labels": ["RR"], "canonicals": ["RISK_RATIO"]}},
         "trials": [{"id": "PMID 1"}, {"id": "PMID 2"}]}
    assert CM.check(_core(o)) == []


# --- Per-key-field plants: each dimension of the compatibility key must REFUSE a violation.
# Enforcement is distributed (estmeasure + extract mismatch guards + the compat backstop); each
# plant proves the dimension's refusal path fires pre-fix, and a matched case does NOT over-refuse.
import harness.extract as EX
import json as _json
import glob as _glob
import os as _os

_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))


def test_plant_effect_measure_event_process_refused():
    # FIRST_EVENT_RATIO + RATE in one pool -> compat backstop refuses.
    o = {"name": "MACE", "primary": True,
         "result": {"k": 2, "estimate": 0.9, "scale": "RR",
                    "estmeasure": {"status": "incompatible", "classes": ["FIRST_EVENT_RATIO", "RATE"],
                                   "labels": ["RR", "IRR"], "canonicals": ["RISK_RATIO", "INCIDENCE_RATE_RATIO"]}},
         "trials": [{"id": "1"}, {"id": "2"}]}
    assert CM.check({"outcomes": [o]}), "incompatible estimand classes must be refused"


def test_plant_endpoint_composite_refused_and_identity_not():
    assert EX.composite_component_mismatch(
        "3-point major adverse cardiovascular events",
        "the 4-component primary (CV death, MI, stroke, hospitalization for unstable angina) occurred")
    # IDENTICAL composites must NOT be flagged (finerenone audit-8 defect: do not invent a difference)
    assert not EX.composite_component_mismatch(
        "3-point major adverse cardiovascular events", "the 3-point MACE (CV death, MI, stroke) occurred")


def test_plant_follow_up_window_refused_and_match_not():
    assert EX.timepoint_mismatch("index admission mortality", "mortality during 90 days of follow-up was 12%")
    assert not EX.timepoint_mismatch("index admission mortality", "in-hospital mortality was 12%")


def test_plant_analysis_set_refused_and_itt_not():
    assert EX.population_mismatch("the per-protocol population who completed the study showed 12/100 vs 20/100")
    assert not EX.population_mismatch("the intention-to-treat population showed 12/100 vs 20/100")


def test_plant_randomised_contrast_disclosed():
    # A pooled trial not parser-confirmed as a randomised contrast is disclosed (verified < total).
    o = {"name": "x", "primary": True,
         "result": {"k": 2, "estimate": 0.9, "scale": "RR",
                    "estmeasure": {"status": "homogeneous", "classes": ["FIRST_EVENT_RATIO"],
                                   "labels": ["RR"], "canonicals": ["RISK_RATIO"]}},
         "trials": [{"id": "PMID 1"}, {"id": "PMID 2"}]}
    k = CM.outcome_key(o, {"outcomes": [o], "arm_contrast": {"trials": {"1": {"status": "verified"}}}})
    assert k["randomised_contrast"] == {"verified": 1, "total": 2}


def test_positive_controls_still_pool_with_matched_keys():
    # finerenone (IDENTICAL composites), sglt2-ckd (3 HRs), glp1 (7 HRs) must pool, key matched.
    for slug, exp_k in [("finerenone-ckd-t2d-renal", 2), ("sglt2-ckd-progression", 3), ("glp1-ra-mace-t2d", 8)]:
        p = _os.path.join(_ROOT, "docs", "reviews", slug, "review.json")
        if not _os.path.exists(p):
            continue
        d = _json.load(open(p, encoding="utf-8"))
        o = next(x for x in d["outcomes"] if x.get("primary"))
        assert o["result"].get("k") == exp_k, f"{slug}: k={o['result'].get('k')} expected {exp_k}"
        k = CM.outcome_key(o, d)
        assert k and k["matched"], f"{slug}: compatibility key not matched (over-refusal)"
