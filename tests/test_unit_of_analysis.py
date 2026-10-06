"""Cluster designs (decision 5 Oct, Handbook, Mahmood's delegation): pooling unadjusted counts from a cluster trial is a
unit-of-analysis error -- the engine's gate stays; the trial is typed UNIT_OF_ANALYSIS_ADJUSTMENT_UNAVAILABLE, acquired
unadjusted counts never match it, and a comparator that pooled unadjusted counts gets
COMPARATOR_POOLED_UNADJUSTED_CLUSTER_COUNTS with quoted spans (balanced-crystalloids: SMART, SALT, SPLIT)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402

REF = ("ENGINE_CANNOT_CONSUME(design=cluster_crossover, missing=design_adjusted_effect|ICC): typed design action REFUSE: "
       "SMART is cluster-crossover")


def test_a_cluster_trial_without_adjustment_is_typed():
    x = {"label": "Semler (SMART trial)", "family": "PMID 29485925", "in_our_pool": False, "absent_code":
         "ENGINE_CANNOT_CONSUME", "our_refusal": REF, "seeded_funnel": None}
    assert gt.blocker_class(x, "balanced") == "UNIT_OF_ANALYSIS_ADJUSTMENT_UNAVAILABLE:cluster_crossover"


def test_acquired_unadjusted_counts_never_match_a_cluster_trial(monkeypatch):
    row = {"label": "Semler (SALT trial)", "verdict": "ADMITTED", "record_id": None,
           "admitted": {"kind": "AACT", "source": "AACT NCT02345486", "value": {"measure": "RR", "events_t": 72,
                        "n_t": 520, "events_c": 68, "n_c": 454, "effect": None, "lower": None, "upper": None}}}
    monkeypatch.setattr(gt, "acquired_rows", lambda slug: {"Semler (SALT trial)": row})
    x = {"label": "Semler (SALT trial)", "in_our_pool": False, "route": "UNVERIFIED", "our_refusal": REF}
    assert gt.acquired_merge("balanced", [x], None, None, "30140441") == []
    assert x["route"] == "UNVERIFIED" and x["acquired_refused"].startswith("UNIT_OF_ANALYSIS_ADJUSTMENT_UNAVAILABLE")


def test_the_comparator_finding_quotes_its_own_text_and_reproduces_the_crude_or(monkeypatch, tmp_path):
    comp_text = ("Statistics were pooled using random effect model; odds ratios (OR) for binary outcomes, with 95% "
                 "confidence intervals (95% CI) were calculated. Semler (SMART trial) 2018 Single center unblinded, "
                 "cluster randomized, multiple crossover trial Death at 60 days. Semler (SALT trial) 2016 Single-center "
                 "prospective, open-label, cluster-randomized, multiple crossover trial Death at 60 days.")
    monkeypatch.setattr(gt, "_comparator_text", lambda comp: (comp_text, "cache/comparators/x"))
    (tmp_path / "_ft").mkdir()
    (tmp_path / "_ft" / "29485925.txt").write_text(
        "Outcome | Balanced Crystalloids (N = 7942) | Saline (N = 7860)\nBefore 60 days | 928 (11.7) | 975 (12.4) | "
        "0.92 (0.83 to 1.02)\n", encoding="utf-8")
    monkeypatch.setattr(gt, "OUT", str(tmp_path))
    trials = [{"label": "Semler (SMART trial)", "family": "PMID 29485925", "our_refusal": REF,
               "comparator_row": {"measure": "OR", "effect": "0.934", "lower": "0.849", "upper": "1.028"}},
              {"label": "Semler (SALT trial)", "family": "PMID 27749094", "our_refusal": REF,
               "comparator_row": {"measure": "OR", "effect": "0.898", "lower": "0.645", "upper": "1.251"}}]
    f = {x["trial"]: x for x in gt.comparator_unadjusted_cluster_findings(trials, "30140441", "balanced")}
    assert f["Semler (SMART trial)"]["reproduced_from_trial_table"]["crude_or"] == [0.934, 0.849, 1.028]
    assert "SALT trial" in f["Semler (SALT trial)"]["spans"][1]["text"]            # its OWN table cell, not SMART's
    assert all(s["text"] in comp_text for s in f["Semler (SALT trial)"]["spans"])
    # a comparator that states a design adjustment gets no finding
    monkeypatch.setattr(gt, "_comparator_text", lambda comp: (comp_text + " We used the design effect (ICC 0.01).", "x"))
    assert gt.comparator_unadjusted_cluster_findings(trials, "30140441", "balanced") == []
