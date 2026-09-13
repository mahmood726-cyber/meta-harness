"""Invalidation propagation: a per-topic STALE verdict from committed signals, poisoning
dependent outputs. Must fire on each condition and stay quiet on a clean topic."""
import harness.invalidation as INV


def test_clean_topic_is_current():
    core = {"outcomes": [{"primary": True, "result": {"k": 3, "estimate": 0.8, "ci_low": 0.6,
                                                      "ci_high": 0.95, "scale": "RR"}}],
            "search": {"source_status": {"PubMed": "RAN_OK", "Europe PMC": "RAN_OK"}}}
    v = INV.assess(core)
    assert v["stale"] is False and v["reasons"] == []


def test_retracted_pooled_trial_is_stale():
    core = {"outcomes": [{"primary": True, "result": {"k": 2, "estimate": 0.8}}],
            "integrity": {"retracted": ["12345678"], "concern": []}}
    v = INV.assess(core)
    assert v["stale"] and v["reasons"][0]["code"] == "retracted_pooled_trial"


def test_primary_reported_not_extracted_is_stale():
    core = {"outcomes": [{"primary": True, "result": {"present": False,
                                                      "reported_not_extracted": True,
                                                      "reported_by": ["99999999"]}}]}
    v = INV.assess(core)
    assert v["stale"] and any(r["code"] == "primary_reported_not_extracted" for r in v["reasons"])


def test_eligible_declared_absent_is_stale():
    core = {"outcomes": [{"primary": True, "result": {"k": 1, "estimate": 0.9},
                          "declared_absent_trials": [
                              {"id": "40000000", "reason": "ELIGIBLE under the registered broad PICO ..."}]}]}
    v = INV.assess(core)
    assert v["stale"] and any(r["code"] == "eligible_declared_absent" for r in v["reasons"])


def test_search_source_errored_is_stale():
    core = {"outcomes": [{"primary": True, "result": {"k": 2, "estimate": 0.8}}],
            "search": {"source_status": {"PubMed": "RAN_OK", "Registry-first (AACT)": "RAN_ERROR"}}}
    v = INV.assess(core)
    assert v["stale"] and any(r["code"] == "search_source_errored" for r in v["reasons"])


def test_ran_zero_is_not_stale():
    # RAN_ZERO (ran, matched nothing) is not an error and must NOT mark the topic stale.
    core = {"outcomes": [{"primary": True, "result": {"k": 2, "estimate": 0.8}}],
            "search": {"source_status": {"PubMed": "RAN_OK", "Citation chase": "RAN_ZERO"}}}
    assert INV.assess(core)["stale"] is False
