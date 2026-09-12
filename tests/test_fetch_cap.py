"""The fetch cap must never sacrifice a FORCED pmid (extra_pmids / controls / comparator) to a size
limit. This is a regression test for the semaglutide incident: at max_records=120 the query loop
filled the cap and the pivotal STEP-1/STEP-3 PMIDs — appended AFTER the query loop — were silently
truncated out, so the built pool was missing its defining trial (the gate's pivotal-present limb
then correctly refused the page). The fix protects forced pmids from truncation."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import fetch  # noqa: E402


def test_protected_pmids_survive_truncation():
    # query loop already filled the cap with non-forced pmids; the two pivotals sit past the cap.
    query = [f"q{i}" for i in range(120)]
    pivotals = ["33567185", "33625476"]
    pmids = query + pivotals
    kept = fetch._apply_cap(pmids, pivotals, cap=120)
    assert len(kept) == 120
    for p in pivotals:
        assert p in kept, f"forced pmid {p} was truncated — the semaglutide bug"
    # and the cap is still respected: exactly 120, so two non-forced pmids were dropped instead
    assert sum(1 for p in kept if p not in pivotals) == 118


def test_no_truncation_preserves_order_exactly():
    """When nothing needs dropping, output must equal input (byte-identical fetch for existing topics)."""
    pmids = ["a", "b", "c", "d"]
    assert fetch._apply_cap(pmids, ["d"], cap=10) == pmids
    assert fetch._apply_cap(pmids, [], cap=10) == pmids


def test_protected_set_larger_than_cap_is_never_sacrificed():
    prot = ["p1", "p2", "p3"]
    pmids = prot + ["x", "y"]
    kept = fetch._apply_cap(pmids, prot, cap=2)
    for p in prot:
        assert p in kept  # a forced trial is never dropped even below the cap
    assert "x" not in kept and "y" not in kept


def test_protected_pmids_reads_all_forced_lists():
    cfg = {"extra_pmids": ["1"], "positive_control_pmids": ["2"],
           "negative_control_pmids": ["3"], "comparator_pmid": "4"}
    assert fetch._protected_pmids(cfg) == ["1", "2", "3", "4"]
    # empty/absent comparator is dropped, no duplicates
    cfg2 = {"extra_pmids": ["1", "1"], "comparator_pmid": ""}
    assert fetch._protected_pmids(cfg2) == ["1"]
