"""Regression tests for evidence-strength RCT detection (esketamine + metformin-PCOS cold audits):
a missing PubMed 'Randomized Controlled Trial' publication type is UNKNOWN, not NOT-AN-RCT -- the
abstract body overrules incomplete metadata (Chen 2023 was lost this way); and the mirror, a
quasi/alternate-allocation study is NOT a true RCT even when the pubtype says it is (Chaudhury 2008).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.screen import _is_rct, screen_record_2  # noqa: E402


def _rec(title, abstract, pubtypes):
    return {"id": "1", "id_type": "pmid", "title": title, "abstract": abstract, "pubtypes": pubtypes}


def test_body_randomized_overrules_missing_pubtype():
    # Chen 2023 shape: pubtype omits RCT, abstract states a randomized double-blind design.
    r = _rec("Esketamine nasal spray for treatment-resistant depression in China",
             "This Phase 3, randomized, double-blind study assigned patients 1:1 to intranasal "
             "esketamine or matching placebo; the primary endpoint was MADRS change at Day 28.",
             ["Journal Article"])
    assert _is_rct(r) is True


def test_quasi_random_overrules_rct_pubtype():
    # Chaudhury shape: pubtype says RCT but the body describes quasi/alternate allocation.
    r = _rec("Metformin in polycystic ovary syndrome",
             "Women were alternately allocated to metformin or placebo; ovulation assessed per cycle.",
             ["Randomized Controlled Trial"])
    assert _is_rct(r) is False
    # both screeners must agree it is not an RCT
    assert screen_record_2(r, {"population_any": ["ovary"], "intervention_any": ["metformin"]}) == "exclude"


def test_review_is_not_a_trial_even_if_it_mentions_randomized():
    r = _rec("Metformin for PCOS: a systematic review and meta-analysis",
             "We pooled randomized controlled trials of metformin versus placebo.",
             ["Systematic Review", "Meta-Analysis"])
    assert _is_rct(r) is False


def test_plain_pubtype_rct_still_included():
    assert _is_rct(_rec("A trial", "patients were randomly assigned to A or B", ["Randomized Controlled Trial"])) is True


def test_no_randomization_evidence_not_rct():
    assert _is_rct(_rec("Observational cohort study", "we followed patients over time", ["Journal Article"])) is False


def test_nonprimary_pubtypes_not_rct_even_with_body_rct_language():
    # Regression: the body-RCT signal must NOT sweep in Comments/Editorials/Protocols/Reviews that
    # merely CITE randomized placebo-controlled trials (probiotics 27688016 Comment, 31712614 Protocol,
    # 39529940 Editorial were wrongly included).
    cite = "This randomized, double-blind, placebo-controlled evidence is summarized here."
    assert _is_rct(_rec("Probiotics for prevention of pediatric AAD", cite, ["Journal Article", "Comment"])) is False
    assert _is_rct(_rec("An editorial on probiotics", cite, ["Editorial"])) is False
    assert _is_rct(_rec("Study protocol of a double-blind randomised placebo-controlled trial", cite,
                        ["Clinical Trial Protocol", "Journal Article"])) is False
    assert _is_rct(_rec("Probiotics: a meta-analysis of randomized trials", cite, ["Journal Article", "Meta-Analysis"])) is False


def test_meta_analysis_by_title_not_rct_even_if_pubtype_incomplete():
    # Regression: a meta-analysis tagged only 'Journal Article' (colchicine-postop 29766857 "...: A
    # Meta-Analysis", 36531704 "Meta-analysis of randomized...") must not be pooled as a trial.
    assert _is_rct(_rec("Colchicine for Prevention of Post-Operative Atrial Fibrillation: A Meta-Analysis",
                        "We pooled randomized controlled trials; colchicine reduced POAF.", ["Journal Article"])) is False
    assert _is_rct(_rec("Efficacy of X: a systematic review and meta-analysis of randomized trials",
                        "randomized, double-blind, placebo-controlled trials were pooled", ["Journal Article"])) is False


def test_protocol_by_title_not_rct():
    assert _is_rct(_rec("Rationale and design of a randomized placebo-controlled trial of X",
                        "randomly assigned, double-blind", ["Journal Article"])) is False


def test_rct_pubtype_overrides_pooled_analysis_title():
    # Regression: RE-COVER II (24344086) is a genuine RCT whose title says "... and pooled analysis";
    # an explicit RCT pubtype must NOT be reclassified a review by the title marker.
    r = _rec("Treatment of acute venous thromboembolism with dabigatran or warfarin and pooled analysis",
             "randomly assigned to dabigatran or warfarin",
             ["Clinical Trial, Phase III", "Journal Article", "Randomized Controlled Trial"])
    from harness.screen import _is_review
    assert _is_review(r) is False and _is_rct(r) is True
