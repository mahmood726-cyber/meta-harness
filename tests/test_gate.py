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
                   "run_utc": "2026-01-01T00:00:00Z", "databases": ["PubMed"],
                   "sources": [{"name": "PubMed", "queries": ["X AND Y"]}]},
        "screening": {"records": [{"id": "PMID1", "id_type": "pmid", "decision": "include",
                                   "rule_id": "I1", "reason": "RCT of X vs placebo"}]},
        "outcomes": [
            {"name": "Primary event", "kind": "efficacy", "primary": True,
             "estimand": "RR", "population": "ITT", "timepoint": "12 mo",
             "method": "Paule-Mandel RE, HKSJ, PI t_{k-1}",
             "result": {"k": 3, "estimate": 0.47, "ci_low": 0.35, "ci_high": 0.63,
                        "tau2": 0.0, "pi_low": 0.3, "pi_high": 0.72, "scale": "RR"},
             "trials": [{"label": "T1", "id": "NCT1", "ai": 20, "n1i": 100,
                         "ci": 40, "n2i": 100, "source": "pub"}]},
            {"name": "Any adverse event", "kind": "harm", "estimand": "RR",
             "result": {"present": False, "reason": "reported as similar; no counts"}},
        ],
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

def test_valid_page_passes_non_replay_limbs():
    # The synthetic fixture has no committed topic/cache, so the Level-B replay limb cannot
    # run against it (correctly: a page with no reproducible pipeline is not publishable).
    # Here we assert the fixture satisfies every OTHER limb; full reproduction is tested
    # against a real committed review below.
    from harness.gate import check_limb1, check_limb2, check_primary_result, _load
    with tempfile.TemporaryDirectory() as tmp:
        d = _build(tmp)
        manifest, html, rep = _load(d)
        reasons = (check_limb1(d, manifest, html, rep)
                   + check_primary_result(d) + check_limb2(manifest, html))
        assert not reasons, f"valid page should pass non-replay limbs, got: {reasons}"


def test_real_review_reproduces_and_passes_full_gate():
    # A real committed page must pass the WHOLE gate including Level-B replay (the pipeline
    # re-run from committed cache regenerates the committed numbers). Skips only if run
    # outside the repo (no docs/reviews present).
    import os as _os
    root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    d = _os.path.join(root, "docs", "reviews", "probiotics-aad-prevention")
    if not _os.path.isdir(d):
        return
    ok, reasons = gate_page(d)
    assert ok, f"real committed review must pass the full gate, got: {reasons}"


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
        html = io.open(p, encoding="utf-8").read().replace("0.47", "0.42")
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


# --- primary outcome must have a result (a k=0 page is a decline, not a publish) ---
import tempfile, json as _json, os as _os
from harness.gate import check_primary_result


def test_gate_refuses_primary_with_no_result():
    d = tempfile.mkdtemp()
    _json.dump({"outcomes": [{"name": "X", "primary": True,
                              "result": {"present": False, "reason": "no trial reported it"}}]},
               open(_os.path.join(d, "review.json"), "w", encoding="utf-8"))
    assert check_primary_result(d), "a resultless primary must be refused"


def test_gate_accepts_primary_with_result():
    d = tempfile.mkdtemp()
    _json.dump({"outcomes": [{"name": "X", "primary": True,
                              "result": {"k": 2, "estimate": 0.8}}]},
               open(_os.path.join(d, "review.json"), "w", encoding="utf-8"))
    assert check_primary_result(d) == []


# --- pivotal-trial presence limb (sacubitril class: pivotal absent from the fetched cache) ---
from harness.gate import _pivotal_missing, check_pivotal_present  # noqa: E402


def test_pivotal_missing_pure():
    recs = [{"id": "25176015", "nct": "NCT01035255"}, {"id": "999"}]
    assert _pivotal_missing(["25176015"], recs) == []          # present by pmid
    assert _pivotal_missing(["NCT01035255"], recs) == []        # present by nct
    assert _pivotal_missing(["11111111"], recs) == ["11111111"]  # absent -> flagged
    assert _pivotal_missing(["25176015", "11111111"], recs) == ["11111111"]


def test_pivotal_present_passes_on_live_topic():
    # finerenone declares its two pivotals (FIDELIO+FIGARO) and its committed cache contains them
    assert check_pivotal_present({"slug": "finerenone-ckd-t2d-renal"}) == []


# --- prespecification-in-protocol limb (external audit #9) --------------------------------------
from harness.gate import check_prespecification_in_protocol, ROOT as GATE_ROOT  # noqa: E402


def test_prespecification_limb_refuses_uncited_rule_and_passes_amendment():
    # A dose-selection rule claimed "pre-specified" but absent from the protocol must be REFUSED;
    # the same rule framed as a dated post-hoc amendment (as noac does) must PASS.
    import shutil
    slug = "__control_prespec"
    rd = os.path.join(GATE_ROOT, "docs", "reviews", slug)
    pr = os.path.join(GATE_ROOT, "protocols", f"{slug}.md")
    cd = os.path.join(GATE_ROOT, "cache", slug)
    try:
        os.makedirs(rd, exist_ok=True); os.makedirs(cd, exist_ok=True)
        io.open(os.path.join(rd, "index.html"), "w", encoding="utf-8").write("<p>page</p>")
        io.open(pr, "w", encoding="utf-8").write("# Protocol\n## PICO\n- P: adults\n")
        json.dump({"1": {"source": "Pre-specified approved-dose rule: 150 mg arm."}},
                  io.open(os.path.join(cd, "dose_selection.json"), "w", encoding="utf-8"))
        assert check_prespecification_in_protocol(rd), \
            "a pre-specified dose rule absent from the protocol must be refused"
        io.open(pr, "w", encoding="utf-8").write("# Protocol\n## Amendment 2026-09-12 (POST-HOC)\n"
                                                 "- Dose rule: pool the approved higher dose.\n")
        json.dump({"1": {"source": "Approved-dose rule (protocol amendment 2026-09-12, post-hoc)."}},
                  io.open(os.path.join(cd, "dose_selection.json"), "w", encoding="utf-8"))
        assert check_prespecification_in_protocol(rd) == []
    finally:
        shutil.rmtree(rd, ignore_errors=True); shutil.rmtree(cd, ignore_errors=True)
        if os.path.exists(pr):
            os.remove(pr)


def test_pivotal_check_is_optin():
    # a topic with no pivotal_trials declared is unaffected (absence != enforcement)
    assert check_pivotal_present({"slug": "colchicine-postop-af"}) == []
