"""Denosumab review fixtures (V1.0.1). Written BEFORE the vocabulary refinement and the known-missing state wiring.

(1) FREEDOM serious infection was stored ABSENT_BY_DESIGN + REFUSED_ON_EVIDENCE although FREEDOM measured and reported it
    (159/3,886 vs 133/3,876), also in a dedicated infection report of the same trial (not a second trial). A statement
    scoped to the inspected abstract never becomes a claim about the trial's design; a held result invalidates it.
(2) FREEDOM SAE 1,004/3,886 vs 972/3,876 from the trial's own posted registry results, labelled as treated (seven
    placebo-randomised participants who received denosumab are in the denosumab arm).
(3) Koh 2016: randomised 6-month placebo phase vs open-label extension, split per phase; SAE narrative 6 vs 2 vs Table 3
    2 vs 1 (n 69/66) -> SOURCE_INTERNALLY_INCONSISTENT for SAE only (the registry gives a third value, 7/69 vs 2/66).
(4) Nakamura 2012: an eligible dose-response RCT reporting ZERO vertebral fractures in all arms -> REPORTED_ZERO_EVENTS.
"""
import copy
import json
import os

import pytest

from harness import claimgraph, fetch, invalidation, pipeline

ROOT = pipeline.ROOT
SLUG = "denosumab-vertebral-fracture"
_CACHE = {}


def _config():
    return json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))


def _outcome(name):
    if name not in _CACHE:
        if "inp" not in _CACHE:
            _CACHE["inp"] = pipeline.outcome_inputs(SLUG, _config(), fetch.ensure(_config(), ""))
        spec, kind = next((s, k) for s, k in pipeline._outcome_specs(_config()) if s["name"] == name)
        _CACHE[name] = pipeline.build_outcome_from_inputs(_CACHE["inp"], spec, kind, SLUG)
    return _CACHE[name]


def test_freedom_serious_infection_is_bound_from_its_companion_report_as_one_trial():
    o = _outcome("Serious infection")
    rows = [t for t in o["trials"] if t["id"] == "PMID 19671655"]
    assert len(rows) == 1 and (rows[0]["ai"], rows[0]["n1i"], rows[0]["ci"], rows[0]["n2i"]) == (159, 3886, 133, 3876)
    assert rows[0]["hand_binding_state"] == "BOUND" and "not a second trial" in rows[0]["companion_report"]
    assert rows[0]["supersedes"]["provenance"] == "REFUSED_ON_EVIDENCE"      # the scoped refusal is kept as history


def test_freedom_sae_from_registry_results_labelled_as_treated():
    t = next(t for t in _outcome("Serious adverse events")["trials"] if t["id"] == "PMID 19671655")
    assert (t["ai"], t["n1i"], t["ci"], t["n2i"]) == (1004, 3886, 972, 3876) and t["hand_binding_state"] == "BOUND"
    assert "as treated" in t["safety_population"] and "seven" in t["safety_population"]


def test_a_scoped_refusal_never_becomes_absent_by_design_and_a_held_result_invalidates_it():
    from harness import result_status as rs
    row = {"id": "PMID 19671655", "reason_code": "REFUSED_ON_EVIDENCE", "absent_kind": "adjudicated_absent",
           "reason": "The source describes no increased infection risk but gives no serious-infection aggregate"}
    assert rs.status_of(row, False, set())["state"] == rs.RETRIEVED_NOT_REPORTED
    assert rs.status_of(row, False, set(), mentioned=True)["state"] == rs.REPORTED_UNRESOLVED
    # PLANT: a design-absence claim on a row whose held source reports the result
    rev = {"outcomes": [{"name": "Serious infection", "result": {"reported_by": ["19671655"]}, "trials": [],
                         "declared_absent_trials": [{**row, "not_measured_span": "not assessed"}]}]}
    rs.derive(rev)
    assert rev["outcomes"][0]["declared_absent_trials"][0]["result_status"]["state"] == rs.REPORTED_UNRESOLVED
    assert [p["kind"] for p in rs.problems(rev)] == ["DESIGN_ABSENCE_VS_HELD_RESULT"]


def test_koh_is_internally_inconsistent_for_sae_only_with_the_registry_as_a_third_value():
    f = next(x for x in claimgraph.regulatory_facts(ROOT, SLUG) if x["trial"] == "Koh 2016")
    assert invalidation.inconsistency_scope(f) == ["Serious adverse events"]
    assert invalidation.missing_state(f, outcome="Serious adverse events") == invalidation.SOURCE_INTERNALLY_INCONSISTENT
    assert invalidation.missing_state(f, outcome="New vertebral fracture") == invalidation.SOURCE_RETRIEVED_NOT_EXTRACTED
    spans = {s["kind"]: s["span"] for s in f["spans"]}
    assert "6 subjects (9%)" in spans["narrative_sae_6_vs_2"] and spans["table3_sae_row"].startswith("Serious AEs (SAEs) 2 (3) 1 (2)")
    reg = f["decision"]["other_source_values"]["registry_results"]
    assert (reg["randomized_phase_denosumab"], reg["randomized_phase_placebo"]) == ("7/69", "2/66")


def test_koh_phases_are_split_placebo_phase_eligible_extension_not():
    from harness import comparison_family as cf
    fam = next(f for f in cf.load(ROOT) if f["registration"] == "NCT01457950")
    got = {c["comparison_id"]: cf.evaluate(ROOT, c, _config()) for c in fam["comparisons"]}
    db = got["Koh2016:DB:denosumab-vs-placebo-6-month"]
    ole = got["Koh2016:OLE:denosumab-after-denosumab-vs-denosumab-after-placebo"]
    assert db["eligibility"] == "ELIGIBLE" and db["arms"] == {"denosumab": 69, "placebo": 66}
    assert ole["eligibility"] == "INELIGIBLE" and ole["fails"][0]["rule"] == "X3"


def _kem_rows():
    rev = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "review.json"), encoding="utf-8"))
    prim = next(o for o in rev["outcomes"] if o.get("primary"))
    return {r.get("name") or r.get("trial_key"): r for r in (prim.get("known_missing_sensitivity") or {}).get("rows") or []}


def test_nakamura_zero_events_is_reported_never_not_reported():
    r = _kem_rows()["Nakamura 2012"]
    assert r["result_status"]["state"] == "REPORTED_ZERO_EVENTS"
    assert r["result_status"]["span"] == "No new vertebral fracture was observed on spinal radiographs in either group."


def test_koh_fracture_absence_is_scoped_to_the_inspected_full_text():
    r = _kem_rows()["Koh 2016"]
    assert r["result_status"]["state"] == "RETRIEVED_NOT_REPORTED" and "inspected full text" in r["result_status"]["scope"]
    assert r["held_fact"]["decision"]["decision"] == "SOURCE_INTERNALLY_INCONSISTENT"


def test_a_tampered_zero_event_witness_fails_closed():
    from harness import comparison_family as cf
    kem = json.load(open(os.path.join(ROOT, "docs", "known_eligible_missing.json"), encoding="utf-8"))
    w = copy.deepcopy(next(r for r in kem["topics"][SLUG] if r["trial"] == "Nakamura 2012")
                      ["result_states"]["New vertebral fracture"]["witness"])
    w["span"] = "Two new vertebral fractures were observed"
    with pytest.raises(ValueError, match="witness span not in"):
        cf._verified(ROOT, {"witness": w})


def test_the_page_verifier_checks_a_hand_row_against_its_named_held_document():
    # a table row's denominators live in its headers: the row verifies against the held document it names (one row
    # read with its headers), and a wrong count or a changed document does not
    from harness import verify, verified_inputs as vi
    for slug, pid, outcome in (("corticosteroids-covid19-mortality", "32876695", "28-day all-cause mortality"),
                               (SLUG, "19671655", "Serious infection"), (SLUG, "19671655", "Serious adverse events")):
        rows = vi.load(slug)["verified_arms.json"][pid]
        rows = rows if isinstance(rows, list) else [rows]
        e = dict(next(vi.runtime(r) for r in rows if r["outcome"] == outcome), id="PMID " + pid)
        assert verify.verify_pooled(e, "")[0] == "verified", (slug, outcome)
        assert verify.verify_pooled(dict(e, ai=e["ai"] + 1), "")[0] == "not-yet"
        assert verify.verify_pooled(dict(e, document_sha256="0" * 64), "")[0] == "not-yet"
