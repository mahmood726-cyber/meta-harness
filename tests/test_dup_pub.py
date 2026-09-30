"""Duplicate-publication guard: two pooled trials sharing an NCT (same trial twice) refuses."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import gate  # noqa: E402


def _setup(trials, nct_map, tmp_path, monkeypatch):
    monkeypatch.setattr(gate, "ROOT", str(tmp_path))
    d = tempfile.mkdtemp(prefix="mh-dup-")
    os.makedirs(os.path.join(d, "cache"), exist_ok=True)
    json.dump({"outcomes": [{"name": "Mortality", "primary": True, "trials": trials}]},
              open(os.path.join(d, "review.json"), "w", encoding="utf-8"))
    # The synthetic cache is under pytest scratch, never the held repository cache.
    cdir = os.path.join(gate.ROOT, "cache", "__dup_test__")
    os.makedirs(cdir, exist_ok=True)
    json.dump({"records": [{"id": k, "nct": v} for k, v in nct_map.items()]},
              open(os.path.join(cdir, "records.json"), "w", encoding="utf-8"))
    return d


def _teardown():
    import shutil
    target = os.path.abspath(os.path.join(gate.ROOT, "cache", "__dup_test__"))
    assert os.path.commonpath([target, os.path.abspath(gate.ROOT)]) == os.path.abspath(gate.ROOT)
    shutil.rmtree(target, ignore_errors=True)


def test_shared_nct_refuses(tmp_path, monkeypatch):
    d = _setup([{"id": "PMID 1"}, {"id": "PMID 2"}], {"1": "NCT9", "2": "NCT9"}, tmp_path, monkeypatch)
    try:
        reasons = gate.check_duplicate_publication(d, {"slug": "__dup_test__"})
        assert reasons and "same trial twice" in reasons[0]
    finally:
        _teardown()


def test_distinct_ncts_pass(tmp_path, monkeypatch):
    d = _setup([{"id": "PMID 1"}, {"id": "PMID 2"}], {"1": "NCT9", "2": "NCT8"}, tmp_path, monkeypatch)
    try:
        assert gate.check_duplicate_publication(d, {"slug": "__dup_test__"}) == []
    finally:
        _teardown()
