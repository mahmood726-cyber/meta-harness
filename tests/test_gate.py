"""Proves the two-limb gate REFUSES a page that fails either limb.

Runs standalone (`python tests/test_gate.py`) and under pytest. No stdout
reassignment (that breaks pytest capture); repo root is put on sys.path so the
harness package imports whether or not pytest set the cwd.
"""
from __future__ import annotations
import copy
import io
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness.census import build_review_dir  # noqa: E402
from harness.gate import gate_page  # noqa: E402
from harness.canonical import sha256_text  # noqa: E402

PROTO_SHA = "0" * 40

COMPARATOR = {
    "name": "Example et al.",
    "year": 2020,
    "journal": "J Example",
    "pmid": "12345678",
    "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
    "open_access": True,
    "overlap": {"ours_k": 5, "theirs_k": 5, "shared_k": 5,
                "only_ours": [], "only_theirs": [], "method": "NCT-id match"},
}


def _review_core():
    return {
        "slug": "fixture-topic",
        "title": "Fixture topic (test)",
        "question": "Does X vs placebo reduce Y?",
        "protocol": {"sha": PROTO_SHA, "committed_utc": "2026-01-01T00:00:00Z",
                     "method_declared": "Paule-Mandel RE, HKSJ, PI t_{k-1}"},
        "search": {"n_records": 20, "cache_ref": "cache/fixture.jsonl",
                   "run_utc": "2026-01-01T00:00:00Z",
                   "sources": [{"name": "PubMed", "queries": ["X AND Y"]}]},
        "screening": {"records": [{"id": "PMID1", "decision": "include",
                                   "rule_id": "I1", "rule": "RCT of X vs placebo"}]},
        "extraction": {"field_source_hierarchy": ["registry results", "publication"],
                       "trials": [{"id": "NCT1", "name": "T1",
                                   "arms": [{"label": "X", "n": 100, "events": 10, "source": "reg"},
                                            {"label": "placebo", "n": 100, "events": 20, "source": "reg"}]}]},
        "synthesis": {"estimand": "RR", "population": "ITT", "timepoint": "12 mo",
                      "method": "Paule-Mandel RE, HKSJ, PI t_{k-1}",
                      "result": {"k": 5, "estimate": 0.55, "ci_low": 0.4, "ci_high": 0.76,
                                 "tau2": 0.0, "pi_low": 0.3, "pi_high": 1.0, "scale": "RR"}},
        "harms": {"outcomes": [{"name": "any AE", "estimate": 1.1, "ci_low": 0.9,
                                "ci_high": 1.3, "k": 5, "scale": "RR"}]},
        "comparator": COMPARATOR,
    }


def _manifest_meta(method="Paule-Mandel RE, HKSJ, PI t_{k-1}", served=None, generator="harness"):
    return {"slug": "fixture-topic", "declared_method": method,
            "served_method": served if served is not None else method,
            "generator": generator, "comparator": COMPARATOR,
            "build_utc": "2026-01-01T00:00:00Z"}


def _build(tmp, review=None, meta=None):
    d = os.path.join(tmp, "reviews", "fixture-topic")
    build_review_dir(review or _review_core(), meta or _manifest_meta(), d, PROTO_SHA)
    return d


def _refuses(d, needle):
    ok, reasons = gate_page(d)
    assert not ok, f"expected REFUSE but gate PASSED: {d}"
    joined = " | ".join(reasons)
    assert needle in joined, f"expected reason containing {needle!r}, got: {joined}"
    return reasons


# --- the happy path: a correctly built page passes both limbs -----------------

def test_valid_page_passes():
    with tempfile.TemporaryDirectory() as tmp:
        d = _build(tmp)
        ok, reasons = gate_page(d)
        assert ok, f"valid page should pass, got: {reasons}"


# --- Limb 1 refusals ----------------------------------------------------------

def test_method_mismatch_refused():
    with tempfile.TemporaryDirectory() as tmp:
        d = _build(tmp, meta=_manifest_meta(served="DerSimonian-Laird"))
        _refuses(d, "served method != declared method")


def test_handmade_generator_refused():
    with tempfile.TemporaryDirectory() as tmp:
        d = _build(tmp, meta=_manifest_meta(generator="hand"))
        _refuses(d, "generator is 'hand'")


def test_handmade_marker_in_page_refused():
    with tempfile.TemporaryDirectory() as tmp:
        d = _build(tmp)
        p = os.path.join(d, "index.html")
        html = io.open(p, encoding="utf-8").read().replace("<body>", "<body><!-- handmade -->")
        io.open(p, "w", encoding="utf-8", newline="").write(html)
        _refuses(d, "hand-made marker")


def test_hand_edited_html_refused():
    """Edit the served page after the census: sha no longer matches -> refuse."""
    with tempfile.TemporaryDirectory() as tmp:
        d = _build(tmp)
        p = os.path.join(d, "index.html")
        html = io.open(p, encoding="utf-8").read().replace("0.55", "0.42")
        io.open(p, "w", encoding="utf-8", newline="").write(html)
        _refuses(d, "index.html")


def test_census_failures_refused():
    with tempfile.TemporaryDirectory() as tmp:
        d = _build(tmp)
        p = os.path.join(d, "REPRODUCTION.json")
        rep = json.load(io.open(p, encoding="utf-8"))
        rep["failures"] = 2
        json.dump(rep, io.open(p, "w", encoding="utf-8", newline=""))
        _refuses(d, "failures")


def test_missing_census_refused():
    with tempfile.TemporaryDirectory() as tmp:
        d = _build(tmp)
        os.remove(os.path.join(d, "REPRODUCTION.json"))
        _refuses(d, "no committed reproduction census")


# --- Limb 2 refusals ----------------------------------------------------------

def _rewrite_manifest(d, mutate):
    p = os.path.join(d, "manifest.json")
    m = json.load(io.open(p, encoding="utf-8"))
    mutate(m)
    json.dump(m, io.open(p, "w", encoding="utf-8", newline=""))


def test_missing_comparator_refused():
    with tempfile.TemporaryDirectory() as tmp:
        d = _build(tmp)
        _rewrite_manifest(d, lambda m: m.__setitem__("comparator", None))
        _refuses(d, "no named published comparator")


def test_comparator_not_open_access_refused():
    with tempfile.TemporaryDirectory() as tmp:
        d = _build(tmp)
        _rewrite_manifest(d, lambda m: m["comparator"].__setitem__("open_access", False))
        _refuses(d, "not marked open_access")


def test_missing_identifier_refused():
    with tempfile.TemporaryDirectory() as tmp:
        d = _build(tmp)
        def mut(m):
            m["comparator"]["pmid"] = None
            m["comparator"]["doi"] = None
        _rewrite_manifest(d, mut)
        _refuses(d, "no PMID or DOI")


def test_overlap_not_stated_on_page_refused():
    """Manifest overlap present, but the served page does not state the counts."""
    with tempfile.TemporaryDirectory() as tmp:
        # Build a page whose review has NO comparator (so overlap absent from HTML),
        # but whose manifest DOES claim a comparator+overlap. Served != declared.
        review = _review_core()
        review["comparator"] = {"present": False, "reason": "omitted to test the gate"}
        d = _build(tmp, review=review)
        # Either refusal proves the served page fails to state the comparator.
        _refuses(d, "not present on the served page")


ALL = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]


def main():
    passed = failed = 0
    for t in ALL:
        try:
            t()
            print(f"PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {t.__name__}: {e}")
            failed += 1
        except Exception as e:  # noqa: BLE001
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed, {len(ALL)} total")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
