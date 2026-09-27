"""Omission reasons on the one record, and endpoint-scoped internal inconsistency (pericarditis-recurrence review).

(1) ICAP (PMID 23992557, colchicine-recurrent-pericarditis) is explained three ways on one page: the known-missing panel
says "population is ACUTE (first-episode) pericarditis, NOT the recurrent-pericarditis population of this topic", while
the caveat says ICAP is ELIGIBLE and NOT refused for population (the registered protocol includes acute first episodes),
and the ledger includes it. An omission reason must agree with the record, and a population refusal must be consistent
with the protocol's stated scope.
(3) An internal inconsistency is scoped to the ENDPOINT it touches (ICAP discontinuation: 14 vs 10 in Table 3, 14 vs 12
in the flow diagram); the same paper's other endpoints stay usable -- never all-or-nothing per paper.

Written BEFORE the fix (evidence/screening_roles/TESTS_PREFIX.txt). Needs no network; the served-page tests read git.
"""
import copy
import json
import os
import subprocess

from harness import pipeline

ROOT = pipeline.ROOT
CANDIDATE = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
PERI = "colchicine-recurrent-pericarditis"
ICAP = "23992557"


def _served(sha, slug):
    return json.loads(subprocess.run(["git", "show", f"{sha}:docs/reviews/{slug}/review.json"], cwd=ROOT,
                                     capture_output=True, check=True).stdout)


# ------------------------------------------------------------------------------------------ (1) omission reasons
def test_served_v1_page_explains_icaps_omission_by_a_population_the_protocol_includes():
    from harness import screening_record
    probs = [p for p in screening_record.consistency_problems(_served(CANDIDATE, PERI)) if p["report_id"] == ICAP]
    kinds = {p["kind"] for p in probs}
    assert "OMISSION_VS_RECORD" in kinds, probs       # "population ... NOT the topic population" vs ledger include
    assert "OMISSION_VS_PROTOCOL" in kinds, probs     # 'acute (first-episode) pericarditis' is inside population_any
    assert all(p["blocking"] for p in probs if p["kind"].startswith("OMISSION"))


def _omission_review(reason, decision="include", elig="ELIGIBLE"):
    rec = {"report_id": "11111111", "parent_family": "NCT1", "parent_eligibility": {"state": elig},
           "report_relevance": {"state": "PRIMARY_REPORT"}, "result_admissibility": {},
           "ledger_decision": decision, "ledger_rule": "INCLUDE" if decision == "include" else "X2"}
    return {"slug": "t", "screening": {"protocol_include": {"population_any": ["pericarditis"],
                                                            "population_none": ["tuberculous"]},
                                       "records": [{"id": "11111111", "decision": decision, "rule_id": rec["ledger_rule"],
                                                    "reason": "", "span": "", "screening_record": rec}]},
            "trial_families": [], "screening_narrative": [],
            "outcomes": [{"name": "Recurrent pericarditis", "primary": True, "trials": [],
                          "declared_absent_trials": [{"id": "PMID 11111111", "reason": reason}]}]}


def test_PLANT_population_omission_of_an_eligible_report_is_refused():
    from harness import screening_record
    r = _omission_review("population is chronic constrictive pericarditis, NOT the population of this topic")
    kinds = {p["kind"] for p in screening_record.consistency_problems(r)}
    assert "OMISSION_VS_RECORD" in kinds


def test_PLANT_population_refusal_inside_the_protocol_scope_is_refused():
    from harness import screening_record
    r = _omission_review("population is acute pericarditis, NOT eligible", decision="exclude", elig="INELIGIBLE")
    kinds = {p["kind"] for p in screening_record.consistency_problems(r)}
    assert "OMISSION_VS_PROTOCOL" in kinds and "OMISSION_VS_RECORD" not in kinds


def test_a_population_refusal_the_protocol_supports_passes():
    from harness import screening_record
    r = _omission_review("population is tuberculous pericarditis, NOT eligible", decision="exclude", elig="INELIGIBLE")
    assert not [p for p in screening_record.consistency_problems(r) if p["kind"].startswith("OMISSION")]


# ------------------------------------------------------------------------------------------ (3) endpoint scope
def _fact(scope=None):
    return {"trial": "ICAP", "trial_key": ICAP, "admissible": False, "adjudication": {"state": "PROPOSED"},
            "decision": {"decision": "SOURCE_INTERNALLY_INCONSISTENT", **({"scope_outcomes": scope} if scope else {}),
                         "source_conflict": {"state": "SOURCE_INTERNALLY_INCONSISTENT"}},
            "spans": [{"kind": "table3_discontinuation_14_vs_10"}, {"kind": "flow_discontinued_14_vs_12"}]}


def test_an_endpoint_scoped_inconsistency_touches_only_that_endpoint():
    from harness import invalidation
    f = _fact(["Treatment discontinuation"])
    assert invalidation.missing_state(f, outcome="Treatment discontinuation") == "SOURCE_INTERNALLY_INCONSISTENT"
    assert invalidation.missing_state(f, outcome="Recurrent pericarditis") == "SOURCE_RETRIEVED_NOT_EXTRACTED"
    assert invalidation.missing_state(f, outcome="Adverse events (gastrointestinal)") == "SOURCE_RETRIEVED_NOT_EXTRACTED"
    assert invalidation.inconsistency_scope(f) == ["Treatment discontinuation"]


def test_an_unscoped_inconsistency_is_the_whole_document():
    from harness import invalidation
    f = _fact()
    assert invalidation.inconsistency_scope(f) is None
    for o in ("Recurrent pericarditis", "Treatment discontinuation", None):
        assert invalidation.missing_state(f, outcome=o) == "SOURCE_INTERNALLY_INCONSISTENT"


def test_admissibility_marks_only_the_scoped_endpoint_and_keeps_the_others():
    from harness import screening_record
    names = ["Recurrent pericarditis", "Adverse events (gastrointestinal)", "Treatment discontinuation"]
    rec = {"report_id": ICAP, "parent_family": "NCT00128453", "parent_eligibility": {"state": "ELIGIBLE"},
           "report_relevance": {"state": "PRIMARY_REPORT"}, "result_admissibility": {},
           "ledger_decision": "include", "ledger_rule": "INCLUDE"}
    review = {"slug": PERI, "held_regulatory_facts": [_fact(["Treatment discontinuation"])],
              "screening": {"records": [{"id": ICAP, "decision": "include", "rule_id": "INCLUDE", "screening_record": rec}]},
              "outcomes": [{"name": names[0], "primary": True, "trials": [{"id": f"PMID {ICAP}"}], "declared_absent_trials": []},
                           {"name": names[1], "trials": [{"id": f"PMID {ICAP}"}], "declared_absent_trials": []},
                           {"name": names[2], "trials": [], "declared_absent_trials": [{"id": f"PMID {ICAP}", "reason_code": "X"}]}]}
    screening_record.fill_admissibility(review)
    per = review["screening"]["records"][0]["screening_record"]["result_admissibility"]["per_outcome"]
    assert per[names[0]]["state"] == "POOLED" and per[names[1]]["state"] == "POOLED"
    assert per[names[2]]["state"] == "SOURCE_INTERNALLY_INCONSISTENT"
    assert per[names[2]]["spans"] == ["flow_discontinued_14_vs_12", "table3_discontinuation_14_vs_10"]
