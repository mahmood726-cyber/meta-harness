"""Report selection reads HELD records when the PubMed pubtype cache lacks a PMID (consolidation 2026-10-04).

WOMAN-2 (tranexamic-acid-pph, NCT03475342): the merged identity chain linked a second PMID (35303924) ahead of the
results report 39461792; AACT types both DERIVED, so the RCT-typed rule decides -- but 39461792 was absent from
pubmed_pubtypes.json, so selection fell back to pmids[0] (a record we do not hold) and the trial became NO_RECORD_HELD,
although outputs/k_gap/member_records.json holds 39461792 typed 'Randomized Controlled Trial'."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]


def test_PLANT_womans2_results_report_is_selected_from_the_held_record():
    import k_gap_identity_reader2 as r2
    r = {"pmids": ["35303924", "39461792"], "ncts": ["NCT03475342"], "label": "WOMAN-210", "slug": "tranexamic-acid-pph"}
    assert r2.shown_pmid(r) == "39461792"


def test_an_unheld_unknown_pmid_still_falls_back_as_before():
    import k_gap_identity_reader2 as r2
    assert r2.shown_pmid({"pmids": ["1", "2"], "ncts": ["NCT00000000"]}) == "1"
