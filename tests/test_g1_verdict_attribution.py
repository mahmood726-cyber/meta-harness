"""G1 colchicine-postop-af: the same-trials verdict is DIFFERENT_CONCLUSION; it is closed TRIAL BY TRIAL by single-trial
swaps of the two pools (g1_tracker.verdict_attribution), and a trial named out of protocol scope is never one of the
'same trials' (Zarpelon [20] entered through a verified meta row before it was named -- acq 9abe38d's matched rule
already excludes named scope differences; the comparison now does too)."""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import g1_tracker as gt  # noqa: E402
from harness import secondary_meta as sm  # noqa: E402


def _row(label, e, lo, hi):
    return sm.SecondaryRow(meta_pmid="X", meta_doi="", location={}, source_digest="", provenance="T", trial_label=label,
                           measure="RR", outcome_definition="", effect=str(e), lower=str(lo), upper=str(hi))


def test_the_single_trial_that_flips_the_conclusion_is_the_driver():
    pairs = [(_row("A", 0.81, 0.62, 1.06), _row("A", 0.66, 0.45, 0.96)),      # the disagreeing trial
             (_row("B", 0.83, 0.56, 1.24), _row("B", 0.83, 0.56, 1.24))]      # an agreeing trial
    st = gt.same_trials_pool(pairs, "FE")
    assert st["verdict"]["verdict"] == "DIFFERENT_CONCLUSION"
    a = gt.verdict_attribution(pairs, "FE", [])
    assert a["drivers"] == ["A"]
    assert next(r for r in a["per_trial"] if r["trial"] == "B")["driver"] is False


def test_colchicine_is_closed_per_trial_and_never_compares_a_named_trial():
    o = json.load(open(os.path.join(gt.G1_DIR, "colchicine-postop-af.json"), encoding="utf-8"))
    st = o["same_trials"]
    # the requirement: every trial withheld from the comparison is a NAMED scope difference, and no named trial is
    # compared (Zarpelon [20] is named where its CC full text is held -- it is, cache/colchicine-postop-af/ft_27223641.txt)
    named = {d["trial"] for d in o.get("named_differences") or []}
    assert set(st["excluded_named_scope_differences"]) <= named and "Zarpelon [20]" in st["excluded_named_scope_differences"]
    compared = {p.get("trial") for p in (st.get("attribution") or {}).get("per_trial") or []}
    assert not (compared & named), compared & named
    # 5 Oct decision 5 (0d7e6649, the captain's decisions under Mahmood's delegation): a verified comparator-row MISMATCH
    # pointing at the comparator is compared on the trial's OWN values, finding kept -- so the same-trials verdict is
    # AGREE, and Imazio [18]'s printed 0.66 stays on its row as the comparator's error, never silently dropped
    assert st["verdict"]["verdict"] == "AGREE"
    imazio = next(t for t in o["trials"] if t["label"] == "Imazio [18]")
    assert imazio["comparator_row_state"] == "MISMATCH" and imazio["agreement_with_comparator_row"].startswith("DISAGREE")
    assert imazio["disagreement_side"].startswith("SECONDARY_WRONG")


def test_colchicine_disagreement_is_resolved_against_the_comparators_copps2_row():
    # with decision 5 the verdict AGREEs, so no disagreement is left to resolve; the row-level finding (above) carries it
    o = json.load(open(os.path.join(gt.G1_DIR, "colchicine-postop-af.json"), encoding="utf-8"))
    assert "result_disagreement" not in o["g1_status"] and "RESULT_AGREES" not in o["g1_status"]["unmet"]


def test_an_undetermined_side_never_resolves():
    pairs = [(_row("A", 0.81, 0.62, 1.06), _row("A", 0.66, 0.45, 0.96)),
             (_row("B", 0.83, 0.56, 1.24), _row("B", 0.83, 0.56, 1.24))]
    trials = [{"label": "A", "comparator_row": {"effect": "0.66", "lower": "0.45", "upper": "0.96"},
               "agreement_with_comparator_row": "DISAGREE", "disagreement_side": "UNDETERMINED (primary value not anchored)"},
              {"label": "B", "comparator_row": {"effect": "0.83", "lower": "0.56", "upper": "1.24"},
               "agreement_with_comparator_row": "AGREE"}]
    a = gt.verdict_attribution(pairs, "FE", trials)
    assert a["drivers"] == ["A"] and a["resolution"]["state"] == "UNRESOLVED"
    trials[0]["disagreement_side"] = "SECONDARY_WRONG (primary numbers are in the primary's own span)"
    assert gt.verdict_attribution(pairs, "FE", trials)["resolution"]["state"] == "RESOLVED_AGAINST_COMPARATOR_ROW"
