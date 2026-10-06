"""harness/analysis_set.py plants (G1 colchicine-postop-af): which analysis set of a trial report a comparator row comes
from, typed and checkable, never guessed."""
from __future__ import annotations

import json
import os

from harness import analysis_set as a

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERMS = (["colchicine"], ["placebo"], ["atrial fibrillation", "poaf", "postoperative af"])


def _copps2():
    recs = json.load(open(os.path.join(ROOT, "cache", "colchicine-postop-af", "records.json"), encoding="utf-8"))
    return next(r for r in recs["records"] if str(r["id"]) == "25172965")["abstract"]


def test_copps2_states_two_analysis_sets_for_postoperative_af():
    sets = a.labelled_counts(_copps2(), *TERMS)
    got = [(s["analysis_set"], s["treatment"]["events"], s["treatment"]["n"], s["control"]["events"], s["control"]["n"])
           for s in sets]
    assert got == [(a.ALL_RANDOMISED, 61, 180, 75, 180), ("on-treatment", 38, 141, 61, 148)]
    # the effusion count group ('colchicine, 103 patients') is a different outcome and is not read
    assert all("effusion" not in s["span"].split("(")[-1] for s in sets)


def test_comparator_row_is_nearest_on_treatment_but_not_reproduced():
    res = a.attribute({"effect": "0.66", "lower": "0.45", "upper": "0.96", "measure": "RR"},
                      a.labelled_counts(_copps2(), *TERMS))
    assert res["state"] == "NOT_REPRODUCED" and res["reproduced_by"] is None and res["nearest"] == "on-treatment"
    per = {p["analysis_set"]: p for p in res["per_set"]}
    assert per[a.ALL_RANDOMISED]["rr"] == 0.8133 and per["on-treatment"]["rr"] == 0.6539


def test_an_exact_printed_row_is_reproduced():
    text = ("Patients were randomized to placebo (n=100) or colchicine (n=100). Postoperative AF occurred "
            "(colchicine, 20 patients [20%]; placebo, 40 patients [40%]).")
    sets = a.labelled_counts(text, *TERMS)
    rr, lo, hi = a.rr_ci(20, 100, 40, 100)
    res = a.attribute({"effect": f"{rr:.2f}", "lower": f"{lo:.2f}", "upper": f"{hi:.2f}", "measure": "RR"}, sets)
    assert res["state"] == "REPRODUCED" and res["reproduced_by"] == a.ALL_RANDOMISED


def test_zero_cell_gets_half_correction_only_when_needed():
    rr0 = a.rr_ci(0, 50, 5, 50)[0]
    assert abs(rr0 - (0.5 / 51) / (5.5 / 51)) < 1e-9
    assert abs(a.rr_ci(10, 50, 20, 50)[0] - 0.5) < 1e-12


def _rec(pid):
    recs = json.load(open(os.path.join(ROOT, "cache", "colchicine-postop-af", "records.json"), encoding="utf-8"))
    return next(r for r in recs["records"] if str(r["id"]) == pid)["abstract"]


def test_zarpelon_counts_back_calculated_and_reproduce_the_comparator_row():
    r = a.percent_back_calculation(_rec("27223641"), ["colchicine"], ["control", "placebo"], ["AF", "atrial fibrillation"])
    assert (r["treatment"]["events"], r["treatment"]["n"], r["control"]["events"], r["control"]["n"]) == (5, 71, 9, 69)
    rr, lo, hi = a.rr_ci(5, 71, 9, 69)
    assert (f"{rr:.2f}", f"{lo:.2f}", f"{hi:.2f}") == ("0.54", "0.19", "1.53")      # the comparator's printed row


def test_back_calculation_refuses_when_arm_sizes_are_not_stated_or_ambiguous():
    assert a.percent_back_calculation(_rec("22090167"), ["colchicine"], ["placebo"], ["POAF"]) is None   # COPPS substudy
    text = "Patients were randomized, 100 to the control group and 100 to the colchicine group. AF: 10% versus 20%."
    assert a.percent_back_calculation(text, ["colchicine"], ["control"], ["AF"])["state"] == "AMBIGUOUS"


def test_a_non_rr_row_is_not_compared():
    assert a.attribute({"effect": "0.66", "lower": "0.4", "upper": "0.9", "measure": "OR"}, [])["state"] == "NOT_COMPARABLE"
