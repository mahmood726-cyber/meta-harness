"""Plants (E1 part 2, 11 Oct): every OUTCOME_NOT_IN_SOURCE is conditional on the coverage of what was searched (the
bundle's asymmetric rule), and 'held full text: CHECKED' is said only of a held article body. Each plant fails on main."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import absence, harms  # noqa: E402
from harness import source_coverage as sc  # noqa: E402

KW = ["discontinuation due to side effects", "discontinued treatment because of side effects"]


def _ft(slug, pid):
    return open(os.path.join(ROOT, "cache", slug, f"ft_{pid}.txt"), encoding="utf-8").read()


def test_PLANT_coverage_for_reads_the_held_bytes_and_the_census():
    cov = sc.coverage_for("metformin-pcos-ovulation", "16769748")          # Moll: the PMC no-download stub
    assert cov["fulltext"] == "STUB" and cov["fulltext_reason"] == "PMC_NO_DOWNLOAD"
    assert sc.coverage_for("dpp4-mace-t2d", "28893244")["abstract"] == "EXCERPT"   # OMNeON, abridged


def test_PLANT_a_stub_full_text_is_not_searched_and_absence_rests_on_the_abstract_scope():
    out = absence.classify_reason(["no such outcome term"], "A complete abstract about something else.",
                                  _ft("metformin-pcos-ovulation", "16769748"), outcome_name="no such outcome term",
                                  coverage={"abstract": "FULL_ABSTRACT", "fulltext": "STUB",
                                            "fulltext_reason": "PMC_NO_DOWNLOAD"})
    assert out["reason_code"] == absence.OUTCOME_NOT_IN_SOURCE and out["absence_scope"] == "abstract"
    assert "STUB" in out["state_basis"] and out["coverage_searched"]["fulltext"] == "NOT_SEARCHED:STUB"


def test_PLANT_an_abridged_abstract_licenses_no_absence():
    out = absence.classify_reason(["heart failure hospitalisation"], "An abridged abstract.", None,
                                  outcome_name="heart failure hospitalisation",
                                  coverage={"abstract": "EXCERPT", "fulltext": None})
    assert out["reason_code"] == absence.SOURCE_NOT_RETRIEVED
    assert "EXCERPT" in out["state_basis"]


def test_PLANT_an_unknown_coverage_licenses_no_absence():
    out = absence.classify_reason(["x outcome"], "Some abstract.", None, outcome_name="x outcome",
                                  coverage={"abstract": None, "fulltext": None})
    assert out["reason_code"] == absence.SOURCE_NOT_RETRIEVED


def test_without_coverage_the_legacy_behaviour_is_unchanged():
    out = absence.classify_reason(["x outcome"], "Some abstract.", None, outcome_name="x outcome")
    assert out["reason_code"] == absence.OUTCOME_NOT_IN_SOURCE and "absence_scope" not in out


def test_PLANT_the_harms_rung_says_checked_only_of_an_article_body():
    rec = {"1": {"abstract": "x"}}
    lad = harms._ladder("1", rec, {"1": "stub text"}, None, fulltext_coverage={"1": "STUB"})
    assert lad[1] == {"rung": "held full text", "state": "NOT_CHECKED_STUB"}
    lad = harms._ladder("1", rec, {"1": "body"}, None, fulltext_coverage={"1": "FULLTEXT"})
    assert lad[1]["state"] == "CHECKED"
