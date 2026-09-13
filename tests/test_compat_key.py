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
