"""G1 tocilizumab: REMDACTA's open full text (PMID 34609549, Intensive Care Med 2021) STATES its day-28 deaths in Table 2
-- 'Mortality at day 28, n (%) [95% CI] g 78 (18.1) [14.5-21.8] 41 (19.5) [14.2-24.9]' under 'Tocilizumab + remdesivir
N = 430 / Placebo + remdesivir N = 210' (footnote g: the weighted difference, CMH -- the counts are crude). The lane's
table reader missed the row three ways (the 'n (%) [95% CI]' label annotation, the bracketed CI after each cell, and
'N = 430' headers without parentheses), so REMDACTA sat ONE_SOURCE (AACT's posted percentage only) -> now ESTABLISHED,
PRIMARY by AACT + TEXT. Radius: every held tocilizumab text (59) -- only REMDACTA's paper (held twice) changes."""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from g1 import tocilizumab as g  # noqa: E402

ROW = ("Table 2 Primary and key secondary efficacy outcomes Tocilizumab + remdesivir N = 430 Placebo + remdesivir N = 210 "
       "Hazard ratio (95% CI) d 0.95 (0.65-1.39) Mortality at day 28, n (%) [95% CI] g "
       "78 (18.1) [14.5-21.8] 41 (19.5) [14.2-24.9] Weighted difference = -1.3")


def test_the_annotated_table_row_is_read():
    c = g.table_candidates(ROW)
    assert [(x["deaths_t"], x["n_t"], x["deaths_c"], x["n_c"]) for x in c] == [(78, 430, 41, 210)]


def test_the_reader_still_refuses_a_percentage_that_does_not_round_trip():
    assert g.table_candidates(ROW.replace("78 (18.1)", "78 (28.1)")) == []


def test_the_reader_still_refuses_a_composite_row():
    assert g.table_candidates(ROW.replace("Mortality at day 28", "Ventilation or death at day 28")) == []


def test_remdacta_is_primary_by_two_independent_sources():
    o = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", "tocilizumab-covid19-mortality.json"), encoding="utf-8"))
    x = next(t for t in o["trials"] if t["label"] == "REMDACTA")
    assert x["route"] == "PRIMARY" and "AACT + TEXT" in x["basis"] and x["agreement_with_comparator_row"] == "AGREE"
    assert o["k_matched"] == 6
