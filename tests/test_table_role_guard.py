"""A baseline / demographic / design table is never an effect source.

Found in colchicine-secondary-cv-prevention, PMID 32295417, when committed held full texts first
reached pool construction. The extracted span was a supplementary TABLE whose caption reads
"Baseline demographic and clinical characteristics of subjects". A baseline table's numbers are arm
sizes and patient characteristics: same shape as outcome counts, two arms, arithmetically perfect,
and completely fictitious as an effect. Nothing downstream would have flagged it -- the build was
refused only because docs/refusals.json independently refuses that trial and the claimgraph will not
publish a trial that is both refused and pooled. That is luck, not a gate.

Three required answers, so the guard cannot degenerate into refusing or admitting everything.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import extract  # noqa: E402

BASELINE = ("abstract arm-level counts (percentage-corroborated): Supplementary Material "
            "Supplementary Material === TABLES (structured; cell boundaries = ' | ') === "
            "TABLE Table 1.: Baseline demographic and clinical characteristics of subjects")
JEMPHASIS = ("abstract effect+CI (HR): Death from any cause occurred in 17 patients (15.3%) in the "
             "eplerenone group and 10 patients (9.1%) in the placebo group (hazard ratio, 1.77; "
             "95% CI, 0.81-3.87; P=0.15) (Table 3, Figure 1D)")
CHANGE_FROM_BASELINE = ("TABLE Table 2.: Change from baseline in LDL cholesterol at week 24 and "
                        "major vascular events")


def test_a_baseline_characteristics_table_is_refused():
    """The negative plant: PMID 32295417's actual extracted span."""
    why = extract.table_role_refusal(BASELINE)
    assert why, "an effect read from a baseline-characteristics table was not refused"
    assert "baseline demographic" in why


def test_a_real_results_table_is_admitted():
    """The positive plant: J-EMPHASIS Table 3, the ITT mortality row we went and acquired."""
    assert extract.table_role_refusal(JEMPHASIS) == ""


def test_change_from_baseline_in_a_results_table_is_admitted():
    """The false positive that would cost real effects.

    A results table legitimately says 'change from baseline'. A guard keyed on the word 'baseline'
    anywhere in the span would refuse it and silently drop genuine continuous outcomes, which is a
    worse failure than the one being fixed because it removes evidence rather than adding it.
    """
    assert extract.table_role_refusal(CHANGE_FROM_BASELINE) == ""


def test_the_guard_is_wired_into_both_extraction_routes():
    """A guard that exists and is never called is not a guard."""
    src = open(os.path.join(ROOT, "harness", "pipeline.py"), encoding="utf-8").read()
    assert src.count("extract.table_role_refusal(") >= 2, (
        "the table-role guard is not applied on both the abstract and full-text routes")
