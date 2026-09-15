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


def test_eligible_declared_absent_object_derived():
    # OBJECT-DERIVED predicate: screened-in (decision=include) but not in the pooled set -> STALE.
    core = {"outcomes": [{"primary": True, "result": {"k": 1, "estimate": 0.9},
                          "trials": [{"id": "PMID 111"}]}],
            "screening": {"records": [{"id": "AAA · 111", "decision": "include"},
                                      {"id": "BBB · 222", "decision": "include"}]}}
    v = INV.assess(core)
    assert v["stale"] and any(r["code"] == "eligible_declared_absent" for r in v["reasons"])


def test_all_screened_in_pooled_is_not_eligible_declared_absent():
    # Every include record is pooled -> no eligible_declared_absent (id-normalisation across formats).
    core = {"outcomes": [{"primary": True, "result": {"k": 1, "estimate": 0.9},
                          "trials": [{"id": "PMID 111"}]}],
            "screening": {"records": [{"id": "AAA · 111", "decision": "include"},
                                      {"id": "CCC · 333", "decision": "exclude"}]}}
    assert not any(r["code"] == "eligible_declared_absent" for r in INV.assess(core)["reasons"])


def test_no_checkable_claim_is_stale():
    core = {"outcomes": [{"primary": True, "result": {"present": False, "reason": "none"}}]}
    v = INV.assess(core)
    assert v["stale"] and any(r["code"] == "no_checkable_claim" for r in v["reasons"])


def test_never_considered_signal_is_stale():
    core = {"outcomes": [{"primary": True, "result": {"k": 1, "estimate": 0.9}, "trials": [{"id": "PMID 1"}]}],
            "screening": {"records": [{"id": "PMID 1", "decision": "include"}]}}
    v = INV.assess(core, {"never_considered": [{"trial": "J-EMPHASIS-HF", "nct": "NCT01115855"}]})
    assert v["stale"] and any(r["code"] == "never_considered" for r in v["reasons"])


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


def test_search_not_executed_signal_is_stale():
    core = {"outcomes": [{"primary": True, "result": {"k": 2, "estimate": 0.8}}],
            "search": {"source_status": {"PubMed": "RAN_OK"}}}
    v = INV.assess(core, {"search_not_executed": {"class": "PMID_ENUMERATION_explicit", "detail": "x"}})
    assert v["stale"] and any(r["code"] == "search_not_executed" for r in v["reasons"])


def test_identifier_scope_detects_agent_identifier_over_class_pool():
    cfg = {
        "protocol_i_line": "- **I** - specifically spironolactone or eplerenone.",
        "intervention_agents": {
            "spironolactone": ["spironolactone"],
            "eplerenone": ["eplerenone"],
        },
        "intervention_class_terms": ["mineralocorticoid receptor antagonist", "MRA"],
    }
    records = [
        {"id": "RALES · 10471456", "decision": "include", "matched_intervention": "spironolactone"},
        {"id": "EMPHASIS-HF · 21073363", "decision": "include", "matched_intervention": "eplerenone"},
    ]
    scope = INV.identifier_scope("spironolactone-hfref-mortality", cfg, records)
    assert scope["verdict"] == "SINGLE_AGENT_OVER_CLASS_POOL"
    assert scope["identifier_agent"] == "spironolactone"
    assert "identifier names spironolactone" in scope["detail"]
    assert "class-level" in scope["detail"]
    core = {"identifier_scope": scope,
            "outcomes": [{"primary": True, "result": {"k": 2, "estimate": 0.8}}]}
    v = INV.assess(core)
    assert any(r["code"] == "identifier_single_agent_class_pool" for r in v["reasons"])


def test_identifier_scope_class_slug_is_not_applicable():
    cfg = {"intervention_agents": {"dapagliflozin": ["dapagliflozin"]},
           "intervention_class_terms": ["SGLT2", "SGLT-2"]}
    scope = INV.identifier_scope(
        "sglt2-hfref-hosp-cvdeath",
        cfg,
        [{"id": "1", "decision": "include", "matched_intervention": "dapagliflozin"}],
    )
    assert scope["level"] == "CLASS"
    assert scope["verdict"] == "NOT_APPLICABLE"


def test_identifier_scope_compact_prefix_does_not_turn_class_slug_into_agent():
    cfg = {
        "intervention_agents": {
            "omega-3 carboxylic acids": ["omega-3 CA", "omega-3 carboxylic acids"],
            "icosapent ethyl": ["icosapent"],
        },
        "intervention_class_terms": ["omega-3", "omega 3"],
    }
    scope = INV.identifier_scope(
        "omega3-cardiovascular-events",
        cfg,
        [{"id": "1", "decision": "include", "matched_intervention": "omega-3"}],
    )
    assert scope["level"] == "CLASS"
    assert scope["verdict"] == "NOT_APPLICABLE"


def test_identifier_scope_unmapped_included_term_is_unresolved():
    cfg = {"intervention_agents": {"melatonin": ["melatonin"]}, "intervention_class_terms": []}
    scope = INV.identifier_scope(
        "melatonin-primary-insomnia-sol",
        cfg,
        [{"id": "1", "decision": "include", "matched_intervention": "ramelteon"}],
    )
    assert scope["verdict"] == "UNRESOLVED"
    v = INV.assess({"identifier_scope": scope, "outcomes": [{"primary": True, "result": {"k": 1, "estimate": 1}}]})
    assert any(r["code"] == "identifier_scope_unresolved" for r in v["reasons"])


def test_known_eligible_missing_signal_is_stale():
    core = {"outcomes": [{"primary": True, "result": {"k": 1, "estimate": 0.9}}]}
    v = INV.assess(core, {"known_eligible_missing": [{"trial": "PHILO", "mechanism": "concept-query"}]})
    assert v["stale"] and any(r["code"] == "known_eligible_missing" for r in v["reasons"])
    assert "PHILO" in v["reasons"][0]["detail"]


def test_ran_error_reason_suppressed_when_search_not_executed_fires():
    # The same fact must be stated once: RAN_ERROR is subsumed by search_not_executed.
    core = {"outcomes": [{"primary": True, "result": {"k": 2, "estimate": 0.8}}],
            "search": {"source_status": {"Registry-first (AACT)": "RAN_ERROR"}}}
    v = INV.assess(core, {"search_not_executed": {"class": "RAN_ERROR_rendered_as_run", "detail": "x"}})
    codes = [r["code"] for r in v["reasons"]]
    assert "search_not_executed" in codes and "search_source_errored" not in codes
