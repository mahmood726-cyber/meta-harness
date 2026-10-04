"""G1 sacubitril-valsartan-hfref: PARALLEL-HF (Tsutsui 2021, PMID 33731544) was screened out X-DESIGN on its abstract,
which never states blinding. Its open full text (J-STAGE, CC BY-NC-ND, via Unpaywall; sha256 recorded) states 'the study
was a multicenter, randomized, double-blind study ... vs. enalapril'. With the full text our OWN ruleset includes it:
a screener error of an abstract-only screen, classed SCREENER_ERROR:ELIGIBLE_ON_FULL_TEXT with the full text's span.
Pre-fix: INCONSISTENT RULESET_INCLUDES (an unresolved reading); before that, INSUFFICIENT_RECORD:BLINDING_NOT_STATED."""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)


def test_the_full_text_pass_classes_parallel_hf_a_screener_error_with_its_span():
    rows = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "exclusion_fulltext.json"), encoding="utf-8"))["rows"]
    r = next(r for r in rows if r["pmid"] == "33731544")
    assert r["class_after"] == "SCREENER_ERROR" and r["subclass_after"].startswith("ELIGIBLE_ON_FULL_TEXT")
    assert r["span"]["field"] == "fulltext" and "double-blind" in r["span"]["text"] and r["how"] == "REGEX_ON_FULLTEXT"


def test_the_missing_fact_pattern_needs_this_studys_design_not_a_citation():
    import k_gap_exclusion_fulltext as eft
    rx = eft._MISSING_FACT["X-DESIGN"]
    assert rx.search("Briefly, the study was a multicenter, randomized, double-blind study to assess")
    assert not rx.search("TITRATION, a double-blind, randomized comparison of two uptitration regimens")   # a cited trial
    assert not rx.search("the open-label extension of the PIONEER-HF trial")


def test_the_tracker_keeps_it_an_eligible_open_gap_with_the_precise_blocker():
    import g1_tracker as gt
    o = json.load(open(os.path.join(gt.G1_DIR, "sacubitril-valsartan-hfref.json"), encoding="utf-8"))
    x = next(x for x in o["trials"] if x["label"] == "Tsutsui, 2021")
    assert "Tsutsui, 2021" in o["open_gaps"] and x["blocker"].startswith("SCREENER_ERROR:ELIGIBLE_ON_FULL_TEXT")
