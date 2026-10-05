"""Plant (5 Oct, forest lane): the reader's meta selection matches a meta's JATS reference list against the unmatched
trials' identifiers. Reference lists often carry DOIs only (corticosteroids meta 33612824 cites CAPE COVID / CoDEX /
REMAP-CAP as 10.1001/jama.2020.1676x), so PMIDs + NCTs alone silently dropped 99 of 100 candidates."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_forest_reader as gfr  # noqa: E402


def test_trial_ids_include_the_trials_doi_casefolded():
    t = {"pmids": ["32876689"], "ncts": ["NCT02517489"]}
    ids = gfr.trial_ids(t, lambda pmid: {"32876689": "10.1001/JAMA.2020.16761"}.get(pmid))
    assert ids == {"32876689", "nct02517489", "10.1001/jama.2020.16761"}


def test_a_doi_only_reference_list_now_selects_the_meta():
    refs = {"10.1001/jama.2020.16761", "10.1056/nejmoa2021436"}
    ids = gfr.trial_ids({"pmids": ["32876689"], "ncts": []}, lambda p: "10.1001/jama.2020.16761")
    assert ids & refs
