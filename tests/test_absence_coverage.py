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


def test_PLANT_an_abridged_cached_abstract_is_checked_against_the_retained_verbatim_one():
    # OMNeON 28893244: the cached abstract (1,138 chars) lost 'HHF 20/2092 v 33/2100, HR 0.60 (0.35-1.05)'; the
    # verbatim EFetch acquisition (registry/source_acquisitions) holds it. The absence check searches the best-coverage
    # object held -- the served cache is not rewritten.
    cov = sc.coverage_for("dpp4-mace-t2d", "28893244")
    assert cov["abstract"] == "EXCERPT" and "0.60" in (cov.get("complete_abstract_text") or "")
    import json
    rec = next(r for r in json.load(open(os.path.join(ROOT, "cache", "dpp4-mace-t2d", "records.json"),
                                         encoding="utf-8"))["records"] if str(r["id"]) == "28893244")
    out = absence.classify_reason(["hospitalization for heart failure", "heart failure hospitalization", "hHF"],
                                  rec["abstract"], None, outcome_name="Hospitalization for heart failure",
                                  declared_estimand="HR", coverage=cov)
    assert out["reason_code"] in (absence.EXTRACTION_NOT_PERFORMED, absence.EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH,
                                  absence.COUNTS_PRESENT_NOT_CORROBORATED), out
    assert "0.60" in out["source_span"]


def test_PLANT_an_abbreviation_the_text_defines_for_the_outcome_is_the_outcome():
    # OMNeON's complete abstract defines 'hospitalization for heart failure (hHF)' and reports 'The hHF outcome occurred
    # in 20/2092 ... 33/2100 ... HR 0.60 (0.35, 1.05)': without the text's own abbreviation the classifier declared the
    # outcome absent from a complete source
    cov = sc.coverage_for("dpp4-mace-t2d", "28893244")
    out = absence.classify_reason([], "", None, outcome_name="Hospitalization for heart failure", declared_estimand="HR",
                                  coverage=cov)
    assert out["reason_code"] != absence.OUTCOME_NOT_IN_SOURCE and "0.60" in out["source_span"], out


def test_a_short_abbreviation_matches_only_as_a_whole_word_and_only_if_it_fits_the_phrase():
    text = "Atrial fibrillation (AF) was recorded. After 30 days, AF occurred in 12/100 v 20/100 (RR 0.60, 0.31-1.15)."
    terms = absence._terms_with_abbreviations([], "Atrial fibrillation", [text])
    assert absence._matches_term("AF occurred in 12/100", terms)
    assert not absence._matches_term("After 30 days nothing occurred", terms)   # 'af' inside 'after' is not AF
    bad = absence._terms_with_abbreviations([], "Atrial fibrillation", ["Atrial fibrillation (XYZ) was recorded."])
    assert not any(t.startswith(absence.ABBR_MARK) for t in bad)            # XYZ does not fit 'atrial fibrillation'


# ---- PR2 review round 1 (agy e1p2-r1-agy mc-936c03ad): plants that failed first ----
def test_lowercase_lead_abbreviation_is_learned_from_a_shorter_term():
    from harness import absence
    text = "The hospitalization for heart failure (hHF) outcome was prespecified. The hHF outcome occurred in 20/2092."
    terms = absence._terms_with_abbreviations(["heart failure"], "Heart failure", [text])
    assert absence.ABBR_MARK + "hHF" in terms


def test_harms_rung_reads_coverage_for_an_integer_pid():
    from harness.harms import _fulltext_rung
    assert _fulltext_rung(28893244, {28893244: "Full text ..."}, {"28893244": "FULLTEXT"}) == "CHECKED"
    assert _fulltext_rung(28893244, {28893244: "x"}, {"28893244": "STUB"}) == "NOT_CHECKED_STUB"
