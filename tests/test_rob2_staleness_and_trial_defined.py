"""Plants (8 Oct; approved fixes for the RoB drift in 7 topics, outputs/d11/ROB_DRIFT.md).

1. TRIAL-DEFINED PRIMARY. A pooled outcome labelled 'Trial-defined primary cardiorenal composite' pools EACH trial's own
   registered primary; the D5 component parser found no components in the generic label, so a fresh build called
   CREDENCE's and DAPA-CKD's registered primaries 'unregistered' (some concerns). The D11 panel read the registry and
   abstract: D5 low for both. A label that says trial-defined but NOT primary stays a component/text comparison.
2. STALENESS. cache/<slug>/rob2.json was built from the review's primary outcome (its name and pooled trials) but
   recorded neither, so a rebuilt review never invalidated it: 3 trials no longer pooled were still rated and 5 topics
   carried a stale D5 input. rob2.json now records its input set; staleness() names every difference.
"""
from __future__ import annotations

from harness import rob2

CREDENCE_PRIMARY = {"measure": "Primary Composite Endpoint of Doubling of Serum Creatinine (DoSC), End-stage Kidney Disease "
                               "(ESKD), and Renal or Cardiovascular (CV) Death", "title": "", "description": ""}


def test_a_trial_defined_primary_label_is_compared_with_the_trials_own_registered_primary():
    d = rob2.derive_d5([CREDENCE_PRIMARY], "Trial-defined primary cardiorenal composite", None, [])
    assert d["level"] == "low" and d["inputs"]["comparison"]["method"] == "trial_defined_primary", d


def test_trial_defined_without_primary_is_not_assumed_to_be_the_primary():
    d = rob2.derive_d5([CREDENCE_PRIMARY], "Trial-defined major coronary/cardiovascular composite", None, [])
    assert d["inputs"]["comparison"]["method"] != "trial_defined_primary"


def test_the_rule_rederives_from_its_own_inputs():
    d = rob2.derive_d5([CREDENCE_PRIMARY], "Trial-defined primary cardiorenal composite", None, [])
    assert rob2.rederive_domain(d)["level"] == d["level"]


REVIEW = {"outcomes": [{"name": "Trial-defined primary cardiorenal composite", "primary": True,
                        "trials": [{"id": "PMID 1", "effect": 0.6}, {"id": "PMID 2", "effect": 0.7}]},
                       {"name": "Amputation", "primary": False, "trials": [{"id": "PMID 2", "effect": 1.0}]}]}


def test_a_rob_object_without_its_input_set_is_stale():
    assert rob2.staleness(REVIEW, {"trials": {"1": {}, "2": {}}}) == ["NO_INPUT_SET"]


def test_a_current_rob_object_is_not_stale():
    obj = {"input_set": rob2.input_set(REVIEW), "trials": {"1": {}, "2": {}}}
    assert rob2.staleness(REVIEW, obj) == []


def test_renamed_outcome_and_changed_membership_are_named():
    obj = {"input_set": rob2.input_set(REVIEW), "trials": {"1": {}, "2": {}}}
    rev = {"outcomes": [{"name": "Kidney composite", "primary": True, "trials": [{"id": "PMID 1", "effect": 0.6},
                                                                                 {"id": "PMID 3", "effect": 0.8}]}]}
    reasons = rob2.staleness(rev, obj)
    assert any(r.startswith("PRIMARY_OUTCOME_RENAMED") for r in reasons)
    assert any(r.startswith("RATED_NOT_POOLED") and "2" in r for r in reasons)
    assert any(r.startswith("POOLED_NOT_RATED") and "3" in r for r in reasons)
