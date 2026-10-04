"""G1 tocilizumab: TIMEPOINT_EXCLUSIVE_BOUND -- a per-arm death count over a window the report ITSELF closes before day
29 is a day-28 count, not another day's. ImmCoVA's open report (PMID 38157348, PLoS One, CC BY 4.0) states 'There were
6 deaths up to day 29, two in each arm. Two additional patients died on or after d29' and '77 had been randomized, 27 to
UC, 28 to anakinra and 22 to tocilizumab' -> 2/22 vs 2/27 (REACT's row: 2/22 vs 2/27). The lane rule 'another day is
never day 28' stands: without the report's own exclusion of day 29, 'up to day 29' is refused (plant W2).
Radius: every held text (one paper, held as abstract + full text) produces a window row."""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from g1 import tocilizumab as g  # noqa: E402

TXT = ("Out of a planned 195 patients, 77 had been randomized, 27 to UC, 28 to anakinra and 22 to tocilizumab. "
       "By that time, 77 out of an intended 195 patients had been randomized, 27 to usual care and 28 and 22 to "
       "anakinra and tocilizumab, respectively ( Fig 1 ). There were 6 deaths up to day 29, two in each arm. "
       "Two additional patients died on or after d29, please see S3 File for details.")


def _t(c):
    return [(x["deaths_t"], x["n_t"], x["deaths_c"], x["n_c"]) for x in c]


def test_w1_a_window_the_report_closes_before_day_29_is_day_28():
    c = g.window_candidates(TXT)
    assert _t(c) == [(2, 22, 2, 27)] and c[0]["denominator_kind"] == g.RANDOMISED
    assert c[0]["timepoint_typing"].startswith("TIMEPOINT_EXCLUSIVE_BOUND") and "died on or after d29" in c[0]["span"]


def test_w2_up_to_day_29_without_the_reports_own_exclusion_stays_another_day():
    assert g.window_candidates(TXT.replace("Two additional patients died on or after d29", "Two patients were lost")) == []


def test_w3_an_exclusive_bound_at_another_day_is_not_day_28():
    assert g.window_candidates(TXT.replace("day 29", "day 31").replace("d29", "d31")) == []


def test_w4_arm_sizes_that_disagree_between_statements_are_refused():
    assert g.window_candidates(TXT.replace("28 and 22 to anakinra", "28 and 23 to anakinra")) == []


def test_w5_a_per_arm_split_that_does_not_add_up_is_refused():
    assert g.window_candidates(TXT.replace("6 deaths up to day 29", "7 deaths up to day 29")) == []


def test_w6_a_ratio_is_never_an_arm_size():
    s = "Patients were randomized 1:2 to anakinra: no anakinra, then 1:1:1 to siltuximab: tocilizumab: no IL-6 blockade."
    assert g._allocations(g._fold(s)) == []


def test_w7_immcova_reads_as_one_bound_primary_stating_the_counts():
    ex = json.load(open(g.AACT_FILE, encoding="utf-8"))
    a = g.assess("ImmCoVA", ex)
    assert a["row"] and tuple(a["row"][k] for k in g._KEY) == (2, 22, 2, 27)
    src = [s["source"] for r in a["readings"] for s in r["sources"]]
    assert any("TIMEPOINT_EXCLUSIVE_BOUND" in s and "PMID 38157348" in s for s in src)
