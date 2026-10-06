"""G1 sacubitril-valsartan-hfref: PARALLEL-HF (Tsutsui 2021, PMID 33731544) was screened out X-DESIGN on its abstract,
which never states blinding. Its open full text (J-STAGE, CC BY-NC-ND, via Unpaywall; sha256 recorded) states 'the study
was a multicenter, randomized, double-blind study ... vs. enalapril'. With the full text our OWN ruleset includes it:
a screener error of an abstract-only screen, classed SCREENER_ERROR:ELIGIBLE_ON_FULL_TEXT with the full text's span.
Pre-fix: INCONSISTENT RULESET_INCLUDES (an unresolved reading); before that, INSUFFICIENT_RECORD:BLINDING_NOT_STATED.

Restated 6 Oct (PR #13): that full text is CC BY-NC-ND and held only in a gitignored download, so no clone (CI, the
worker) can re-read it; the k-gap lane decided it on the REGISTRY instead (8e473adc: NCT02468232's AACT design rows state
RANDOMIZED, QUADRUPLE masking, 'Double-blind' -> ELIGIBLE, SCREENER_ERROR:REGISTRY_STATES_BLINDING). The requirement is
unchanged: an eligible open gap with the precise blocker and a span a clone can reproduce."""
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
    # no open full text a clone can hold: the full-text pass makes NO claim from it (never a verdict from absent bytes)
    assert r["fulltext"] == "NO_OA_FULLTEXT" and r["class_after"] == "INSUFFICIENT_RECORD" and not r.get("span")
    # the eligibility fact comes from the registry, with its own verbatim span
    import g1_tracker as gt
    o = json.load(open(os.path.join(gt.G1_DIR, "sacubitril-valsartan-hfref.json"), encoding="utf-8"))
    se = next(x for x in o["trials"] if x["label"] == "Tsutsui, 2021")["screen_eligibility"]
    assert se["state"] == "ELIGIBLE" and se["basis"] == "SCREENER_ERROR:REGISTRY_STATES_BLINDING"
    assert se["span"]["nct"] == "NCT02468232" and "Double-blind" in se["span"]["text"] and "QUADRUPLE" in se["span"]["text"]


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
    assert "Tsutsui, 2021" in o["open_gaps"] and x["blocker"] == "SCREENER_ERROR:REGISTRY_STATES_BLINDING"
