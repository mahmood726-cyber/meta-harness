import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import design_key as D  # noqa: E402


def test_factorial_rr_keeps_reconstructed_estimand_and_records_adjusted_alternative():
    trial = {
        "id": "PMID 34375394",
        "label": "BaSICS",
        "ai": 1381,
        "n1i": 5230,
        "ci": 1439,
        "n2i": 5290,
        "source": "By day 90 ... (adjusted hazard ratio, 0.97 [95% CI, 0.90-1.05]; P=.47).",
    }
    rec = {
        "title": "BaSICS",
        "abstract": ("Double-blind, factorial, randomized clinical trial conducted at 75 ICUs. "
                     "There was no significant interaction between fluid type and infusion speed; P = .98."),
    }
    trial["derivation"] = "reconstructed"
    key = D.key_for_trial(trial, rec, {}, "RR")
    assert key["design"] == "FACTORIAL"
    assert key["unit_of_randomisation"] == "INDIVIDUAL"
    assert key["estimator_source"] == "RECONSTRUCTED"
    assert key["published_alternative"]["scale"] == "HR"
    assert key["published_alternative"]["adjusted"] is True
    assert key["correlation_handling"]["method"] == "none"
    assert key["design_action"]["action"] == "MANUAL_REVIEW"
    trial["design"] = key
    assert D.maybe_use_published_adjusted(trial, "RR")
    assert trial["effect"] == 0.97
    assert trial["scale"] == "HR"
    assert trial["design"]["design_action"]["action"] == "ALLOW_WITH_LABEL"


def test_reconstructed_cluster_crossover_needs_refusal():
    trial = {"id": "PMID 29485925", "label": "SMART", "ai": 818, "n1i": 7942, "ci": 875, "n2i": 7860}
    rec = {"title": "SMART", "abstract": "a pragmatic, cluster-randomized, multiple-crossover trial"}
    D.stamp_trial(trial, {"29485925": rec}, {}, "RR")
    assert trial["design"]["design"] == "CLUSTER_CROSSOVER"
    assert D.needs_design_refusal(trial)
    assert trial["design"]["design_action"]["action"] == "REFUSE"
    row = D.refusal_absence(trial)
    assert row["state"] == "REFUSED_ON_EVIDENCE"
    assert "typed design action REFUSE" in row["reason"]


def test_correlation_method_without_evidence_is_treated_as_none_and_refused():
    trial = {"id": "PMID 1", "label": "CAPE-COD-like", "ai": 10, "n1i": 100, "ci": 20, "n2i": 100,
             "derivation": "reconstructed",
             "design": {"design": "CLUSTER", "unit_of_randomisation": "CLUSTER",
                        "estimator_source": "RECONSTRUCTED",
                        "correlation_handling": {"method": "published_adjusted_SE", "evidence": []}}}
    decision = D.decision_for_trial(trial, "RR")
    assert decision["action"] == "REFUSE"
    assert D.needs_design_refusal(trial)
