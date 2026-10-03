"""G1 doac-vte-recurrence reconciliation: the same 6 trials, our HR pool vs the comparator's RR -- what IS decidable
without arm sizes (harness/event_total_check.py), and three defects of scripts/g1_reconcile.py found when it first ran
on a topic other than colchicine (each failed before its fix)."""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import g1_reconcile as rc  # noqa: E402
from harness import event_total_check as ec  # noqa: E402

COMP = ("Recurrent VTE occurred in 2.0% of DOAC recipients compared with 2.2% in VKA recipients (relative risk [RR] "
        "0.90, 95% confidence interval [CI] 0.77-1.06).")


def test_the_trials_report_more_events_than_the_comparators_rates_can_hold():
    r = rc.reconcile("doac-vte-recurrence")["comparator_conclusion"]["whole_pool"]["event_total_check"]
    assert r["state"] == "EVENTS_INCOMPATIBLE_WITH_COMPARATOR_RATES"
    assert r["trial_events_total"] == 702 and r["comparator_max_events"] == 608.0
    assert {p: v["events"] for p, v in r["per_trial"].items()} == {
        "19966341": [30, 27], "24344086": [30, 28], "23991658": [130, 146], "23808982": [59, 71],
        "21128814": [36, 51], "22449293": [50, 44]}


def test_event_check_is_consistent_or_not_decidable_otherwise():
    t = {"1": "RESULTS: The primary outcome occurred in 20 of 1000 patients and 22 of 1000 patients."}
    assert ec.check(COMP, ["recurrent VTE"], 2000, t)["state"] == "CONSISTENT"          # 42 <= 45
    t2 = {"1": "RESULTS: The primary outcome occurred in 2.0% of patients."}            # no two counts: never guessed
    assert ec.check(COMP, ["recurrent VTE"], 2000, t2)["state"] == "NOT_DECIDABLE"
    assert ec.check(COMP, ["recurrent VTE"], None, t)["state"] == "NOT_DECIDABLE"      # no stated total


def test_reconcile_classes_on_a_whole_pool_topic():
    r = rc.reconcile("doac-vte-recurrence")
    cls = sorted({t["cls"] for t in r["trials"]})
    assert cls[0] == "MATCHED_NO_COMPARATOR_ROW" and len(cls) == 2                      # never DISAGREE / UNCLASSIFIED
    assert cls[1] in ("NOT_AN_INCLUDED_TRIAL", "TRUE_SCOPE_DIFFERENCE:SECONDARY_ANALYSIS_OF_TRIALS_STATED")
    assert r["comparator_conclusion"]["on_shared_trials"] == "NOT_TESTABLE_ON_SHARED_ROWS"   # never SURVIVES on None==None


def test_a_full_text_scope_verdict_survives_a_clone_without_the_body():
    t = next(t for t in rc.reconcile("colchicine-postop-af")["trials"] if t["trial"] == "Zarpelon [20]")
    assert t["verdict"].startswith("out of the registered protocol's scope; the held OA FULL TEXT states it")
    assert t["stating_span"].startswith("Methods Study Design and Participants This is a prospective, randomized, open")


def test_the_tracker_carries_why_doac_vte_cannot_agree():
    # 6 / 6 eligible matched; RESULT_AGREES unmet. The tracker row itself says why: different measures, AND the
    # comparator's printed rates cannot hold the trials' own primary-outcome events -- it counted a different outcome
    import g1_tracker as gt
    o = json.load(open(os.path.join(gt.G1_DIR, "doac-vte-recurrence.json"), encoding="utf-8"))
    assert o["N_eligible"] == 6 and o["k_matched"] == 6 and o["g1_status"]["unmet"] == ["RESULT_AGREES"]
    oc = o["same_trials"]["outcome_check"]
    assert o["same_trials"]["state"] == "WHOLE_POOL_MEASURE_DIFFERS"
    assert oc["state"] == "EVENTS_INCOMPATIBLE_WITH_COMPARATOR_RATES" and oc["trial_events_total"] == 702
