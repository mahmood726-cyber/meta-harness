"""A lane-imported SECONDARY_SINGLE row counts only with STRUCTURED provenance (meta + location + digest), the same rule the
page's renderer applies (consolidation 2026-10-04): tocilizumab CORIMUNO-TOCI-1 and EMPACTA arrived from the lane file
with their sources only in prose ('2 REACT-independent meta row(s) ... two readers agree'), so the tracker counted them
INDEPENDENT while the page refused them. Both now refuse; the reason is recorded on the row."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]


def _o(trials):
    return {"slug": "x", "comparator_pmid": "1", "trials": trials, "routes": {}, "k_matched": 1}


def test_PLANT_prose_only_secondary_single_is_demoted():
    import g1_tracker as gt
    o = _o([{"label": "A", "route": "SECONDARY_SINGLE", "g1_countable": True, "in_our_pool": False,
             "basis": "SECONDARY_SINGLE: 2 meta rows ... two readers agree", "secondary_single": {"state": "ADMITTED"}}])
    gt.demote_unstructured_secondary_single(o)
    x = o["trials"][0]
    assert x["route"] == "UNVERIFIED" and not x["g1_countable"] and "structured provenance" in x["provenance_refusal"]


def test_structured_secondary_single_is_kept():
    import g1_tracker as gt
    o = _o([{"label": "A", "route": "SECONDARY_SINGLE", "g1_countable": True, "in_our_pool": False,
             "secondary_single": {"provenance": {"meta_pmid": "24348885", "where": "figure 2", "digest": "8" * 64}}}])
    gt.demote_unstructured_secondary_single(o)
    assert o["trials"][0]["route"] == "SECONDARY_SINGLE"
