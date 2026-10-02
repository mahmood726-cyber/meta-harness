"""PLANTS for the tracker defects found by the cross-vendor reviews of 3 Oct (codex 8, agy/Gemini 2: one agy finding
refuted -- its excerpt lacked as_row) and by the 31-topic batch (an MD trial pooled from arm means read as 'not pooled').
Each test is the reproduction, asserting the requirement."""
import os
import sys

from harness import secondary_meta as sm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "scripts"))
import g1_tracker as gt  # noqa: E402

MORT = "28-day all-cause mortality"


def test_registry_binding_needs_the_outcome_named_not_just_no_extra_component():
    # a mortality topic must not bind 'Death or mechanical ventilation' merely because it is the PRIMARY outcome
    v = gt.binding_verdict(MORT, ["28-day mortality", "all-cause mortality", "death"], "Death or Mechanical Ventilation",
                           2, is_primary=True)
    assert v["verdict"] == "REFUSED" and v["gate"] == "ESTIMAND"
    v = gt.binding_verdict(MORT, ["28-day mortality", "all-cause mortality"], "Time to Recovery", 2, is_primary=True)
    assert v["verdict"] == "REFUSED" and v["gate"] == "OUTCOME_NOT_NAMED"
    v = gt.binding_verdict(MORT, ["all-cause mortality"], "All-cause Mortality at Day 28", 2, is_primary=False)
    assert v["verdict"] == "BINDABLE"


def test_one_estimand_refusal_does_not_name_a_trial_whose_matching_outcome_failed_elsewhere():
    x = {"registry_binding": {"state": "REFUSED", "candidates": [
        {"gate": "ESTIMAND", "verdict": "REFUSED", "reason": "4-point", "title": "4P", "arms": [], "analysis": None,
         "snapshot": {}},
        {"gate": "ARMS", "verdict": "REFUSED", "reason": "one group", "title": "3P MACE", "arms": [], "analysis": None,
         "snapshot": {}}]}}
    assert gt.scope_difference(x, {}, "s") is None


def test_a_screened_out_trial_is_never_named_by_the_estimand_path():
    est = {"state": "REFUSED", "candidates": [{"gate": "ESTIMAND", "verdict": "REFUSED", "reason": "r", "title": "t",
                                               "arms": [], "analysis": None, "snapshot": {}}]}
    for f in ({"stage": "SCREENED_OUT", "rule_id": "X2", "pmid": "999999999"},     # unaudited
              {"stage": "SCREENED_OUT", "rule_id": None, "pmid": "999999999"}):    # no rule id (agy)
        assert gt.scope_difference({"seeded_funnel": f, "registry_binding": est}, {}, "no-such-topic") is None


def test_agreement_on_counts_requires_the_same_measure():
    theirs = sm.SecondaryRow(meta_pmid="m", meta_doi="", location={}, source_digest="", provenance="T", trial_label="A",
                             measure="HR", outcome_definition="", effect="0.90", lower="0.80", upper="1.01",
                             events_t=10, n_t=100, events_c=20, n_c=100)
    ours = {"measure": "RR", "events_t": 10, "n_t": 100, "events_c": 20, "n_c": 100}
    assert gt.agreement(ours, theirs).startswith("NOT_COMPARABLE")


def test_verdict_is_decided_on_unrounded_intervals():
    assert gt.result_verdict({"estimate": -0.1, "ci_low": -0.2, "ci_high": -0.00001},
                             {"estimate": -0.1, "ci_low": -0.2, "ci_high": 0.00001}, "MD")["verdict"] == \
        "DIFFERENT_CONCLUSION"
    seen = []
    real = gt.result_verdict
    gt.result_verdict = lambda o, t, m: seen.append((o, t)) or real(o, t, m)
    try:
        a = sm.SecondaryRow(meta_pmid="m", meta_doi="", location={}, source_digest="", provenance="T", trial_label="A",
                            measure="MD", outcome_definition="", effect="-0.123456", lower="-0.2", upper="-0.046912")
        gt.same_trials_pool([(a, a), (a, a)], "FE")
    finally:
        gt.result_verdict = real
    o, _ = seen[0]
    assert o["estimate"] != round(o["estimate"], 4)          # the verdict saw the UNROUNDED pool, not the display


def test_a_row_with_neither_effect_nor_counts_is_not_poolable_and_does_not_crash():
    r = sm.SecondaryRow(meta_pmid="m", meta_doi="", location={}, source_digest="", provenance="T", trial_label="A",
                        measure="RR", outcome_definition="")
    assert sm.row_yi_vi(r) is None


def test_pooled_membership_does_not_depend_on_the_value_format():
    # esketamine: an MD trial pooled from arm means carries no effect+CI and no 2x2 -> it read as 'not in our pool'
    assert gt.is_pooled({"id": "PMID 1", "primary": None}, {"PMID 1"})
    assert not gt.is_pooled({"id": "PMID 2", "primary": {"effect": "1"}}, {"PMID 1"})
    assert not gt.is_pooled(None, {"PMID 1"})


def test_the_seeded_report_is_the_result_typed_pmid_not_pmids_0():
    t = {"pmids": ["111", "222"], "ncts": [], "label": "X"}
    assert gt.report_pmid(t, shown=lambda r: "222") == "222"
    assert gt.report_pmid({"pmids": ["111"], "ncts": [], "label": "X"}, shown=lambda r: None) == "111"


def test_our_counts_are_compared_with_the_comparators_printed_ratio():
    # COPPS-2 (colchicine-postop-af): ours 61/180 vs 75/180 (RR 0.81); the comparator prints RR 0.66 (0.45-0.96)
    theirs = sm.SecondaryRow(meta_pmid="m", meta_doi="", location={}, source_digest="", provenance="T", trial_label="I",
                             measure="RR", outcome_definition="", effect="0.66", lower="0.45", upper="0.96")
    ours = {"measure": "RR", "events_t": 61, "n_t": 180, "events_c": 75, "n_c": 180}
    assert gt.agreement(ours, theirs) == "DISAGREE:our_counts_imply_0.81_vs_printed_0.66"
    theirs.effect = "0.81"
    assert gt.agreement(ours, theirs) == "AGREE_ON_POINT"
