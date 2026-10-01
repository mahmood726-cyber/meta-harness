"""A pooled row read from a held document carries the analysis qualifiers that document states -- derived, never typed.

omega3-cardiovascular-events, PMID 38199870 (DO-HEALTH), 2026-10-01: enabling the topic's held full texts entered
"omega-3 versus no omega-3 (adjusted hazard ratio (aHR) = 1.00, 95% CI 0.64-1.56)" into the MACE pool. The protocol
admits it (its estimand rule: "Published ratio effects with 95% CI are poolable when arm counts are not
abstract-extractable"; nothing excludes an adjusted or exploratory result). But the paper itself says the estimate is
covariate-adjusted, and that "The risk of MACE ... was an exploratory endpoint of DO-HEALTH". A reviewer asked to
countersign the change must be told both, in the paper's own words, and a person typing them into a notice is not a
derivation. So the harness reads them from the bytes, with the verbatim span, and the notice quotes what it read.

Each qualifier has a positive and a negative plant so it cannot degenerate into always/never.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import extract  # noqa: E402

DOHEALTH_ROW = ("abstract effect+CI (HR): Based on the main effects analysis, we did not find any statistically "
                "significant benefit of any of the three interventions with regard to the risk of MACE: omega-3 versus "
                "no omega-3 (adjusted hazard ratio (aHR) = 1.00, 95% CI 0.64-1.56), nor vitamin D 3 versus no vitamin "
                "D 3 (aHR = 1.37, 95% CI 0.88-2.14)")
DOHEALTH_DOC = ("Methods The risk of MACE (coronary heart event or intervention, heart failure, stroke) was an "
                "exploratory endpoint of DO-HEALTH, incident hypertension and change in biomarkers were secondary "
                "endpoints. DO-HEALTH is a completed multicentre, randomised, placebo-controlled trial. " + DOHEALTH_ROW)
JEMPHASIS_ROW = ("abstract effect+CI (HR): Death from any cause occurred in 17 patients (15.3%) in the eplerenone group "
                 "and 10 patients (9.1%) in the placebo group (hazard ratio, 1.77; 95% CI, 0.81-3.87; P=0.15)")
UNADJUSTED_ROW = "the unadjusted hazard ratio for MACE was 0.91 (95% CI 0.80-1.03)"
EXPLORATORY_OTHER_OUTCOME = ("Incident hypertension was an exploratory endpoint. The primary outcome, MACE, occurred "
                             "in 120 vs 140 patients (HR 0.85, 95% CI 0.67-1.08).")
MACE_KW = ["MACE", "major cardiovascular events", "primary endpoint"]


def _codes(q):
    return sorted(x["code"] for x in q)


def test_dohealth_row_is_qualified_adjusted_and_exploratory_with_verbatim_spans():
    q = extract.analysis_qualifiers(DOHEALTH_ROW, DOHEALTH_DOC, MACE_KW)
    assert _codes(q) == ["COVARIATE_ADJUSTED", "EXPLORATORY_ENDPOINT"], q
    for x in q:
        assert x["quote"] and x["quote"] in DOHEALTH_DOC, x          # the words are the paper's, located in its bytes
    assert "adjusted hazard ratio" in next(x for x in q if x["code"] == "COVARIATE_ADJUSTED")["quote"]
    assert "exploratory endpoint" in next(x for x in q if x["code"] == "EXPLORATORY_ENDPOINT")["quote"]


def test_an_itt_primary_result_carries_no_qualifier():
    assert extract.analysis_qualifiers(JEMPHASIS_ROW, JEMPHASIS_ROW, ["death from any cause"]) == []


def test_unadjusted_is_not_adjusted():
    assert extract.analysis_qualifiers(UNADJUSTED_ROW, UNADJUSTED_ROW, MACE_KW) == []


def test_exploratory_is_tied_to_the_declared_outcome_not_to_any_outcome():
    q = extract.analysis_qualifiers(EXPLORATORY_OTHER_OUTCOME, EXPLORATORY_OTHER_OUTCOME, MACE_KW)
    assert "EXPLORATORY_ENDPOINT" not in _codes(q), q


def test_a_label_only_keyword_does_not_tie_an_exploratory_sentence_to_the_outcome():
    doc = "A secondary endpoint was exploratory. " + JEMPHASIS_ROW
    assert extract.analysis_qualifiers(JEMPHASIS_ROW, doc, ["primary endpoint", "secondary endpoint"]) == []


def test_a_truncated_row_snippet_is_read_back_to_its_full_sentence():
    """The real DO-HEALTH row's snippet stops at '(adjusted hazard' (220 chars). Reading only the snippet misses the
    qualifier; the sentence in the held document has it."""
    snippet = DOHEALTH_ROW[: DOHEALTH_ROW.index("(adjusted hazard") + len("(adjusted hazard")]
    assert not extract._ADJUSTED_EFFECT.search(snippet)
    q = extract.analysis_qualifiers(snippet, DOHEALTH_DOC, MACE_KW)
    assert "COVARIATE_ADJUSTED" in _codes(q), q
