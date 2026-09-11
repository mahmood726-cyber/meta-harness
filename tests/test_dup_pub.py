"""Duplicate-publication guard: two pooled trials sharing an NCT (same trial twice) refuses."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import gate  # noqa: E402


def _setup(trials, nct_map):
    d = tempfile.mkdtemp(prefix="mh-dup-")
    os.makedirs(os.path.join(d, "cache"), exist_ok=True)
    json.dump({"outcomes": [{"name": "Mortality", "primary": True, "trials": trials}]},
              open(os.path.join(d, "review.json"), "w", encoding="utf-8"))
    # point ROOT's cache at a temp file via a fake slug dir
    cdir = os.path.join(gate.ROOT, "cache", "__dup_test__")
    os.makedirs(cdir, exist_ok=True)
    json.dump({"records": [{"id": k, "nct": v} for k, v in nct_map.items()]},
              open(os.path.join(cdir, "records.json"), "w", encoding="utf-8"))
    return d


def _teardown():
    import shutil
    shutil.rmtree(os.path.join(gate.ROOT, "cache", "__dup_test__"), ignore_errors=True)


def test_shared_nct_refuses():
    d = _setup([{"id": "PMID 1"}, {"id": "PMID 2"}], {"1": "NCT9", "2": "NCT9"})
    try:
        reasons = gate.check_duplicate_publication(d, {"slug": "__dup_test__"})
        assert reasons and "same trial twice" in reasons[0]
    finally:
        _teardown()


def test_distinct_ncts_pass():
    d = _setup([{"id": "PMID 1"}, {"id": "PMID 2"}], {"1": "NCT9", "2": "NCT8"})
    try:
        assert gate.check_duplicate_publication(d, {"slug": "__dup_test__"}) == []
    finally:
        _teardown()
