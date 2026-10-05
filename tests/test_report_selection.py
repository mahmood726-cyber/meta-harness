"""A trial's REPORT when AACT types no RESULT reference for its NCT: DELIVER (NCT03619213) has 48 linked PMIDs, every
one DERIVED, so the selector fell back to the oldest (31081589, a 2019 review of SGLT2 inhibitors) and our screen
excluded THAT paper as 'not an RCT'. The next tier is the earliest PMID whose OWN PubMed record links the NCT, is typed
Randomized Controlled Trial, and is not a design / protocol / secondary-analysis paper; else the old fallback."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
import k_gap_identity_reader2 as r2  # noqa: E402

RCT = ["Journal Article", "Randomized Controlled Trial"]


def _set(monkeypatch, store, ncts, pubtypes):
    monkeypatch.setattr(r2, "_STORE", store)
    monkeypatch.setattr(r2, "_PM", (ncts, pubtypes))


def test_the_trials_own_rct_report_wins_over_the_oldest_derived_paper(monkeypatch):
    _set(monkeypatch, {"31081589": [["NCT03619213", "DERIVED"]], "36027570": [["NCT03619213", "DERIVED"]]},
         {"31081589": "", "34693515": "NCT03619213", "36027570": "NCT03619213"},
         {"31081589": {"pubtypes": ["Review"], "title": "Effects of SGLT2 inhibitors on heart failure."},
          "34693515": {"pubtypes": RCT, "title": "Dapagliflozin in HFpEF: baseline characteristics of DELIVER."},
          "36027570": {"pubtypes": RCT, "title": "Dapagliflozin in Heart Failure with Mildly Reduced or Preserved "
                                                 "Ejection Fraction."}})
    r = {"pmids": ["31081589", "34693515", "36027570"], "ncts": ["NCT03619213"]}
    assert r2.shown_pmid(r) == "36027570"


def test_an_aact_result_reference_still_wins_and_no_qualifying_paper_keeps_the_old_fallback(monkeypatch):
    _set(monkeypatch, {"200": [["NCT1", "RESULT"]]}, {"100": "NCT1"}, {"100": {"pubtypes": RCT, "title": "Main."}})
    assert r2.shown_pmid({"pmids": ["100", "200"], "ncts": ["NCT1"]}) == "200"
    # an RCT-typed paper that links ANOTHER trial's NCT, or a secondary analysis, never qualifies
    _set(monkeypatch, {}, {"100": "NCT9", "150": "NCT1"},
         {"100": {"pubtypes": RCT, "title": "Main."}, "150": {"pubtypes": RCT, "title": "A post hoc analysis of X."}})
    assert r2.shown_pmid({"pmids": ["90", "100", "150"], "ncts": ["NCT1"]}) == "90"


def test_a_title_set_inside_a_named_trial_is_a_secondary_paper_not_the_report(monkeypatch):
    # FOURIER: 'Inflammatory and Cholesterol Risk in the FOURIER Trial' (29530884) is a secondary analysis
    _set(monkeypatch, {}, {"29530884": "NCT01764633"},
         {"29530884": {"pubtypes": RCT, "title": "Inflammatory and Cholesterol Risk in the FOURIER Trial."}})
    assert r2.shown_pmid({"pmids": ["28859947", "29530884"], "ncts": ["NCT01764633"]}) == "28859947"
