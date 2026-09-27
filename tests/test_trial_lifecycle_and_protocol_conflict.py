"""Empagliflozin-HFpEF review, EMPA-PRED (NCT06249945). Written BEFORE the fix.

The page labelled it "included, eligible, completed, awaiting results". Its own held records say otherwise:
- AACT (snapshot 2026-08-30): overall_status RECRUITING, completion_date 2030-12-31 -- a PLANNED date in the future;
- CT.gov design row: masking SINGLE (the protocol requires double-blind);
- CT.gov interventions: "Empagliflozin 25 MG" (the protocol's intervention is 10 mg daily).

Two root causes:
(1) design_key.registry_designs() updated the SHARED ClinicalTrials.gov record object with the cached design row,
    whose own surrogate `id` (227983957) replaced the trial's NCT id. Everything downstream that reads rec['id'] lost
    the trial (the AACT dates lookup among them), and an empty status fell through to 'completed'.
(2) the screener took the word 'placebo' as proof of double-blinding even where the registry explicitly says SINGLE,
    and never compared the registered dose with the protocol's.
"""
import json
import os

import pytest

from harness import design_key, fetch, pipeline

ROOT = pipeline.ROOT
SLUG = "empagliflozin-hfpef-hosp"


def _lc():
    from harness import lifecycle
    return lifecycle


# ---------------------------------------------------------------------------------------------- (1) identity
def test_merging_registry_designs_never_rewrites_a_records_identity():
    ct = {"id": "NCT01", "id_type": "nct", "masking": "", "title": "t"}
    records = {"ctgov": [ct], "designs": [{"id": "227983957", "nct_id": "NCT01", "masking": "SINGLE"}]}
    out = design_key.registry_designs(records)
    assert ct["id"] == "NCT01" and ct["masking"] == ""           # the shared record is untouched
    assert out["NCT01"]["id"] == "NCT01" and out["NCT01"]["masking"] == "SINGLE"
    assert out["NCT01"]["design_row_id"] == "227983957"


# ---------------------------------------------------------------------------------------------- (2) lifecycle
@pytest.mark.parametrize("status,completion,expect_state,expect_pva", [
    ("RECRUITING", "2030-12-31", "ONGOING", "PLANNED"),
    ("", "2030-12-31", "UNKNOWN", "PLANNED"),                     # PLANT: no status + future date: never COMPLETED
    ("UNKNOWN", "2030-12-31", "UNKNOWN", "PLANNED"),
    ("COMPLETED", "2030-12-31", "CONFLICT", "PLANNED"),           # PLANT: 'completed' with a future planned date
    ("COMPLETED", "2019-10-09", "COMPLETED", "ACTUAL"),
    ("", "", "UNKNOWN", "UNKNOWN"),                               # PLANT: the old default said 'completed'
    ("NOT_YET_RECRUITING", "2029-06-30", "NOT_YET_RECRUITING", "PLANNED"),
    ("TERMINATED", "2021-01-01", "TERMINATED", "ACTUAL"),
])
def test_a_future_planned_completion_never_yields_completed(status, completion, expect_state, expect_pva):
    lc = _lc().lifecycle({"overall_status": status, "completion_date": completion}, source_date="2026-08-30")
    assert lc["state"] == expect_state
    assert lc["planned_vs_actual_completion"]["value"] == expect_pva
    assert lc["recruitment_status"]["value"] == (status or None)
    assert lc["source_date"] == "2026-08-30"
    assert lc["state"] != "COMPLETED" or completion <= "2026-08-30"


def test_a_registry_declared_date_type_outranks_the_source_date_comparison():
    # FIVE-STAR (NCT05887817): completion 2026-07-31 typed ESTIMATED, status UNKNOWN (last verified 2024-02). The date
    # is before the source date, but the registry itself says it is a plan: PLANNED, never ACTUAL, never COMPLETED.
    lc = _lc().lifecycle({"overall_status": "UNKNOWN", "completion_date": "2026-07-31", "completion_date_type": "ESTIMATED"},
                         source_date="2026-09-27")
    assert lc["planned_vs_actual_completion"]["value"] == "PLANNED" and lc["state"] == "UNKNOWN"
    lc = _lc().lifecycle({"overall_status": "COMPLETED", "completion_date": "2026-07-31", "completion_date_type": "ESTIMATED"},
                         source_date="2026-09-27")
    assert lc["state"] == "CONFLICT"
    lc = _lc().lifecycle({"overall_status": "COMPLETED", "completion_date": "2025-03-17", "completion_date_type": "ACTUAL"},
                         source_date="2026-09-27")
    assert lc["state"] == "COMPLETED" and lc["planned_vs_actual_completion"]["value"] == "ACTUAL"


def test_completeness_state_is_derived_from_the_lifecycle():
    lc = _lc()
    assert lc.completeness_state({"state": "ONGOING"}, has_results=False) == "eligible+ongoing"
    assert lc.completeness_state({"state": "UNKNOWN"}, has_results=False) == "eligible+lifecycle_unknown"
    assert lc.completeness_state({"state": "CONFLICT"}, has_results=False) == "eligible+lifecycle_conflict"
    assert lc.completeness_state({"state": "COMPLETED"}, has_results=True) == "eligible+completed+results_available"


# ---------------------------------------------------------------------------------------------- (3) protocol conflicts
PROTO = {"include": {"design_double_blind": True},
         "protocol_dose": {"intervention": "empagliflozin", "dose_mg": 10,
                           "protocol_span": "- **I** - Empagliflozin 10 mg daily, added to usual heart-failure therapy."}}


def _conf(rec):
    from harness import protocol_conflict
    return protocol_conflict.check(rec, PROTO)


def test_registry_masking_single_conflicts_with_a_double_blind_protocol():
    kinds = [c["kind"] for c in _conf({"id": "NCT1", "id_type": "nct", "masking": "SINGLE", "interventions": ["Placebo"]})]
    assert kinds == ["MASKING_CONFLICT"]
    assert _conf({"id": "NCT1", "id_type": "nct", "masking": "QUADRUPLE", "interventions": []}) == []
    assert _conf({"id": "NCT1", "id_type": "nct", "masking": "", "interventions": []}) == []   # not stated: no claim


def test_a_registered_dose_other_than_the_protocols_conflicts():
    c = _conf({"id": "NCT1", "id_type": "nct", "masking": "DOUBLE", "interventions": ["Empagliflozin 25 MG", "Placebo"]})
    assert [x["kind"] for x in c] == ["DOSE_CONFLICT"] and "25 MG" in c[0]["record_span"]
    assert c[0]["protocol_span"] == PROTO["protocol_dose"]["protocol_span"]
    assert _conf({"id": "NCT1", "id_type": "nct", "masking": "DOUBLE", "interventions": ["Empagliflozin 10 mg"]}) == []
    assert _conf({"id": "NCT1", "id_type": "nct", "masking": "DOUBLE", "interventions": ["Empagliflozin"]}) == []
    # a dose of ANOTHER drug in the record is not this conflict
    assert _conf({"id": "NCT1", "id_type": "nct", "masking": "DOUBLE",
                  "interventions": ["Empagliflozin 10 mg", "Potassium Chloride 20 MG"]}) == []


# ---------------------------------------------------------------------------------------------- (4) end to end
_REV = {}


def _review():
    if "rv" not in _REV:
        config = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
        _REV["rv"] = pipeline.build_review_core(SLUG, config, fetch.ensure(config, ""), "test")
    return _REV["rv"]


def test_empa_pred_is_ongoing_and_unresolved_not_eligible_completed():
    row = next(r for r in _review()["screening"]["records"] if "NCT06249945" in r["id"])
    assert row["decision"] == "awaiting_classification" and row["rule_id"] == "A-PROTOCOL-CONFLICT"
    kinds = sorted(p["kind"] for p in row["pending_decisions"])
    assert kinds == ["DOSE_CONFLICT", "MASKING_CONFLICT"]
    assert row["completeness_state"] == "eligible+ongoing"
    lc = row["lifecycle"]
    assert lc["state"] == "ONGOING" and lc["planned_vs_actual_completion"]["value"] == "PLANNED"
    assert lc["completion_date"]["value"] == "2030-12-31" and lc["recruitment_status"]["value"] == "RECRUITING"
    assert row["screening_record"]["parent_eligibility"]["state"] == "UNRESOLVED"


def test_no_registry_record_in_any_built_review_has_lost_its_nct_identity():
    rv = _review()
    for r in rv["screening"]["records"]:
        if r.get("id_type") == "nct":
            assert "NCT" in str(r["id"]).upper(), r["id"]
