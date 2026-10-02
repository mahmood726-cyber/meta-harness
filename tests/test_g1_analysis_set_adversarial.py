"""Plants from the cross-vendor adversarial review NR-C20 (Codex, recorded in C:/mh-lanes/nr/codex/CALL_LOG.jsonl;
artefact F:/mh-nr101-codex/c20-g1-analysis-set/last_message.txt). Each was executed against the code before the fix and
failed there; the review's findings were proposals, these tests are the lane's verification of them."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import analysis_set as A  # noqa: E402

T, C, O = ["colchicine"], ["placebo", "control"], ["postoperative AF", "AF"]


def test_modified_itt_is_not_itt():                                                       # C20 #5
    s = A.labelled_counts("In the modified ITT analysis, postoperative AF occurred (colchicine, 38/141 patients; "
                          "placebo, 61/148 patients).", T, C, O)
    assert [x["analysis_set"] for x in s] == ["modified intention-to-treat"]


def test_an_unlabelled_group_is_all_randomised_only_when_its_n_is_the_randomised_n():     # C20 #6
    txt = ("Patients were randomized to placebo (n=180) or colchicine (n=180). The on-treatment analysis included 289 "
           "patients. Postoperative AF occurred (colchicine, 38/141 patients; placebo, 61/148 patients).")
    assert [x["analysis_set"] for x in A.labelled_counts(txt, T, C, O)] == [A.NO_SET_NAMED]
    txt2 = "Patients were randomized to placebo (n=180) or colchicine (n=180). Postoperative AF occurred (colchicine, 61 patients; placebo, 75 patients)."
    assert [x["analysis_set"] for x in A.labelled_counts(txt2, T, C, O)] == [A.ALL_RANDOMISED]


def test_counts_bind_to_their_own_clause_not_an_earlier_outcome():                        # C20 #7
    s = A.labelled_counts("Postoperative AF was assessed; adverse events occurred (colchicine, 36/180 patients; "
                          "placebo, 21/180 patients).", T, C, O)
    assert s == []


def test_a_restricted_set_never_inherits_the_randomised_denominator():                    # C20 #10
    s = A.labelled_counts("Patients were randomized to colchicine (n=180) or placebo (n=180). Among completers, "
                          "postoperative AF occurred (colchicine, 38 patients; placebo, 61 patients).", T, C, O)
    assert all(x["treatment"]["n"] is None and x["control"]["n"] is None for x in s)
    assert A.attribute({"measure": "RR", "effect": "0.62", "lower": "0.44", "upper": "0.89"}, s)["state"] == "NO_HELD_COUNTS"


def test_two_sets_reproducing_the_row_is_ambiguous_not_the_first():                       # C20 #11
    s = A.labelled_counts("In the intention-to-treat analysis, postoperative AF occurred (colchicine, 20/100 patients; "
                          "placebo, 40/100 patients). In the per-protocol analysis, postoperative AF occurred "
                          "(colchicine, 20/100 patients; placebo, 40/100 patients).", T, C, O)
    r = A.attribute({"measure": "RR", "effect": "0.50", "lower": "0.32", "upper": "0.79"}, s)
    assert r["state"] == "REPRODUCED_BY_SEVERAL" and r["reproduced_by"] is None
    assert sorted(r["reproduced_by_all"]) == ["intention-to-treat", "per-protocol"]


def test_percent_back_calculation_needs_one_count_per_percentage():                       # C20 #13
    r = A.percent_back_calculation("Patients were randomized, 690 to the control group and 1000 to the colchicine "
                                   "group. AF occurred in 7% versus 13.04%.", T, C, O)
    assert r.get("state") == "AMBIGUOUS"


def test_percentages_bind_to_their_own_clause():                                          # C20 #15
    r = A.percent_back_calculation("Patients were randomized, 69 to the control group and 71 to the colchicine group. "
                                   "AF was assessed; deaths occurred in 7.04% versus 13.04%.", T, C, O)
    assert r is None or "treatment" not in r


def test_a_negated_arm_name_is_the_control():                                             # C20 #8
    s = A.labelled_counts("Postoperative AF occurred (no-colchicine, 37/181 patients; colchicine, 26/179 patients).",
                          ["colchicine"], ["no-colchicine"], O)
    assert [(x["treatment"]["events"], x["control"]["events"]) for x in s] == [(26, 37)]


def test_zarpelon_and_copps2_still_hold():
    z = ("Patients were randomized, 69 to the control group and 71 to the colchicine group. Colchicine group patients "
         "showed no reduction in AF incidence as compared to control group patients (7.04% versus 13.04%, respectively; "
         "p = 0.271).")
    r = A.percent_back_calculation(z, T, C, O)
    assert (r["treatment"]["events"], r["control"]["events"]) == (5, 9)
