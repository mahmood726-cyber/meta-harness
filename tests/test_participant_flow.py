"""Participant-flow acquisition for the attrition (D3) domain -- data-only landing.

Guards three things:
  1. The coverage cascade is a real denominator by KIND, not an assumed one: every pooled
     trial is exactly one of {no NCT, NCT but no CT.gov results, usable flow}, and the kinds
     sum to the pooled total. (The denominator-trap lesson: enumerate kinds, never assume.)
  2. The AMPLITUDE-O rule: a non-completion REASON is a verbatim string carried from the
     source, never a number derived from started-minus-completed.
  3. The index renders the section with the object-derived usable count.

PLANT: a doc that labels a no-NCT trial 'USABLE' (or whose kinds don't sum) must fail the
consistency check -- proving the check can fail.
"""
import json
import os

import harness.index as IDX

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DOCS = os.path.join(_ROOT, "docs")
_PF = os.path.join(_DOCS, "participant_flow.json")


def _load():
    return json.load(open(_PF, encoding="utf-8"))


def _cascade_consistent(doc):
    c = doc["coverage_cascade"]
    pooled = c["pooled_trials_across_32_topics"]
    kinds = (c["no_nct__registry_cannot_supply_flow"]
             + c["has_nct_but_no_ctgov_results_posted"]
             + c["has_nct_with_usable_participant_flow"])
    # the per-trial entries must also sum to the same totals, by kind
    seen = {"NO_NCT_REGISTRY_CANNOT_SUPPLY": 0, "NCT_NO_CTGOV_RESULTS": 0, "USABLE": 0}
    n_entries = 0
    for td in doc["topics"].values():
        for tr in td["trials"]:
            n_entries += 1
            seen[tr["flow_status"]] += 1
    return (kinds == pooled == n_entries
            and seen["USABLE"] == c["has_nct_with_usable_participant_flow"]
            and seen["NO_NCT_REGISTRY_CANNOT_SUPPLY"] == c["no_nct__registry_cannot_supply_flow"]
            and seen["NCT_NO_CTGOV_RESULTS"] == c["has_nct_but_no_ctgov_results_posted"])


def test_cascade_is_consistent_denominator():
    assert _cascade_consistent(_load())


def test_plant_broken_cascade_is_caught():
    # promote one no-NCT trial to USABLE without changing the cascade -> kinds no longer sum.
    doc = _load()
    for td in doc["topics"].values():
        for tr in td["trials"]:
            if tr["flow_status"] == "NO_NCT_REGISTRY_CANNOT_SUPPLY":
                tr["flow_status"] = "USABLE"
                assert not _cascade_consistent(doc), "consistency check failed to fire on plant"
                return
    # if no no-NCT trial exists, plant a kind-sum mismatch directly
    doc["coverage_cascade"]["has_nct_with_usable_participant_flow"] += 1
    assert not _cascade_consistent(doc)


def test_reasons_are_verbatim_strings_not_derived():
    doc = _load()
    checked = 0
    for td in doc["topics"].values():
        for tr in td["trials"]:
            if tr["flow_status"] != "USABLE":
                continue
            for per in tr["periods"]:
                for arm in per["arms"]:
                    for r in arm["noncompletion_reasons"]:
                        assert isinstance(r["reason"], str) and r["reason"].strip(), r
                        # a reason is a labelled cause, never a bare arithmetic count
                        assert not r["reason"].replace(".", "").isdigit(), r
                        checked += 1
    assert checked > 0, "no non-completion reasons present to check"


def test_leader_flow_landed():
    # LEADER (liraglutide MACE, NCT01179048) must carry its real per-arm flow.
    doc = _load()
    trials = doc["topics"]["glp1-ra-mace-t2d"]["trials"]
    leader = [t for t in trials if t["nct"] == "NCT01179048"]
    assert leader, "LEADER not found in glp1 pooled set"
    arms = leader[0]["periods"][0]["arms"]
    started = {a["arm"]: a["started"] for a in arms}
    assert set(started.values()) == {"4668", "4672"}, started


def test_index_renders_section_with_derived_count():
    html = IDX._participant_flow_section(_DOCS)
    assert "attrition domain (D3)" in html
    c = _load()["coverage_cascade"]
    assert str(c["has_nct_with_usable_participant_flow"]) in html
    # data-only posture must be explicit
    assert "judgement" in html.lower() and "pending" in html.lower()
