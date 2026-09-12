"""Per-trial funding / COI disclosure (ME-32). Source-anchored classification, verbatim span, and
refuse-on-absence: a trial with no funding statement is reported 'not stated in source', never guessed.
An industry/public marker classifies only when it sits in the FUNDING sentence, so a company named in an
unrelated sentence does not mislabel the trial."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import funding  # noqa: E402
from harness import error_library as EL  # noqa: E402


def test_industry_funding_detected_from_statement():
    txt = "Background. This is an RCT. Funding: This study was funded by Novo Nordisk. Results were positive."
    d = funding.detect(txt)
    assert d and d["type"] == "industry"
    assert "Novo Nordisk" in d["span"]


def test_public_funding_detected():
    txt = "Methods... The trial was supported by a grant from the National Institutes of Health (NIH)."
    d = funding.detect(txt)
    assert d and d["type"] == "public/non-profit"


def test_mixed_funding():
    txt = "Funded by the Medical Research Council and Pfizer Inc., with additional academic support."
    d = funding.detect(txt)
    assert d and d["type"] == "mixed"


def test_no_statement_returns_none():
    assert funding.detect("A randomized trial of drug X versus placebo in adults. The primary outcome was met.") is None
    assert funding.detect("") is None


def test_company_outside_funding_sentence_does_not_classify_as_industry():
    # A company named far from any funding anchor must NOT flip the classification to industry.
    txt = ("Pfizer manufactures the comparator tablet used in routine care. " + ("filler. " * 40)
           + "This work was supported by a grant from the National Institutes of Health.")
    d = funding.detect(txt)
    assert d and d["type"] == "public/non-profit", d


def test_scan_pooled_reports_not_stated_when_silent():
    review = {"outcomes": [{"primary": True, "trials": [{"id": "PMID 1"}, {"id": "PMID 2"}]}]}
    rec = {"1": {"title": "Trial one", "abstract": "supported by AstraZeneca."},
           "2": {"title": "Trial two", "abstract": "no funding statement here at all."}}
    out = funding.scan_pooled(review, rec)
    by = {f["id"]: f for f in out}
    assert by["PMID 1"]["type"] == "industry"
    assert by["PMID 2"]["type"] == "not stated in source"


def test_scan_pooled_prefers_full_text():
    review = {"outcomes": [{"primary": True, "trials": [{"id": "PMID 9"}]}]}
    rec = {"9": {"title": "T", "abstract": "no funding line in abstract"}}
    ft = {"9": "Full text ... Funding: supported by a grant from the Wellcome Trust foundation."}
    out = funding.scan_pooled(review, rec, ft)
    assert out[0]["type"] == "public/non-profit" and out[0]["source"] == "full text"


def test_me32_is_now_rendered_and_no_unchecked_remain():
    entry = next(e for e in EL.LIBRARY if e[0] == "ME-32")
    assert entry[2] == EL.RENDERED
    assert EL.not_checked() == [], f"unexpected NOT_CHECKED entries: {EL.not_checked()}"
    s = EL.summary()
    assert s.get("NOT_CHECKED", 0) == 0
