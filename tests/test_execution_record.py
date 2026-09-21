"""M1: the generator's execution record, the verifier's two certificate-pin invariants, and the record cross-link the verifier can
refuse. Nothing here adds a capability to the bundle: one field's SOURCE (generating_commit) and three named refusals."""
import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(ROOT / "tests"))
import execution_record as er  # noqa: E402  (scripts/execution_record.py)
import test_bundle_verifier as T  # noqa: E402
from harness.canonical import canonical_json, sha256_text  # noqa: E402

SLUG = "glp1-ra-mace-t2d"


@pytest.fixture(autouse=True)
def _reclaim_tmp_path(tmp_path):
    """Test hygiene: reclaim this test's tmp_path in teardown -- AFTER the test body and all its assertions -- so a session's basetemp
    peaks at one fixture (~60-150 MB) instead of the sum (~2.8 GB measured 2026-09-20). Nothing a test asserts depends on the
    fixture surviving teardown; equivalence was measured file by file with and without this fixture (identical verdicts and counts)."""
    yield
    import shutil
    shutil.rmtree(tmp_path, ignore_errors=True)


def _fake_release(tmp_path):
    rd = tmp_path / "docs" / "reviews" / "x"; rd.mkdir(parents=True)
    (rd / "review.json").write_text('{"slug": "x"}', encoding="utf-8")
    (rd / "index.html").write_text("<html>x</html>", encoding="utf-8")
    (rd / "CERTIFICATE.json").write_text(json.dumps({"release_sha256": "r" * 64, "review_sha256": "v" * 64}), encoding="utf-8")
    (rd / "manifest.json").write_text(json.dumps({"review_sha256": "v" * 64, "html_sha256": "h" * 64, "protocol_sha": "p" * 40}), encoding="utf-8")
    return rd


def test_record_names_tree_command_environment_inputs_outputs_and_release(tmp_path, monkeypatch):
    rd = _fake_release(tmp_path)
    monkeypatch.setattr(er, "_git", lambda *a: {"rev-parse HEAD": "c" * 40, "rev-parse --abbrev-ref HEAD": "main",
                                                "status --porcelain --untracked-files=all": " M docs/reviews/x/review.json\n?? docs/reviews/x/index.html\n"}[" ".join(a)])
    rec = er.write_execution_record(rd, "x", ["python", "scripts/build_topic.py", "x", "--now", "2026-09-11"], "2026-09-11")
    on_disk = json.loads((rd / er.RECORD_NAME).read_text(encoding="utf-8"))
    assert on_disk == rec
    assert rec["tree"]["generating_commit"] == "c" * 40 and rec["tree"]["branch"] == "main"
    assert rec["tree"]["tree_state"] == "CLEAN_EXCEPT_OWN_OUTPUTS" and rec["tree"]["dirty_other_paths"] == []
    assert {Path(k).name for k in rec["outputs"]} == {"review.json", "index.html", "CERTIFICATE.json", "manifest.json"}
    assert rec["release"] == {"release_sha256": "r" * 64, "review_sha256": "v" * 64, "html_sha256": "h" * 64, "protocol_sha": "p" * 40, "meaning": rec["release"]["meaning"]}
    assert rec["command"]["argv"][-2:] == ["--now", "2026-09-11"] and rec["command"]["now_argument"] == "2026-09-11"
    assert rec["environment"]["python"] == sys.version and rec["environment"]["host"] and rec["utc"].endswith("Z")
    assert next(v for k, v in rec["outputs"].items() if k.endswith("review.json"))["sha256"] == hashlib.sha256(b'{"slug": "x"}').hexdigest()


def test_dirty_input_side_is_named_not_omitted(tmp_path, monkeypatch):
    rd = _fake_release(tmp_path)
    monkeypatch.setattr(er, "_git", lambda *a: {"rev-parse HEAD": "c" * 40, "rev-parse --abbrev-ref HEAD": "b",
                                                "status --porcelain --untracked-files=all": " M harness/pipeline.py\n M docs/reviews/x/review.json\n"}[" ".join(a)])
    rec = er.write_execution_record(rd, "x", ["p"], None)
    assert rec["tree"]["tree_state"] == "DIRTY" and rec["tree"]["dirty_other_paths"] == ["harness/pipeline.py"]
    assert "does not reproduce" in rec["tree"]["meaning"]


def test_no_git_is_recorded_as_no_git_never_inferred(tmp_path, monkeypatch):
    rd = _fake_release(tmp_path)
    monkeypatch.setattr(er, "_git", lambda *a: None)
    rec = er.write_execution_record(rd, "x", ["p"], None)
    assert rec["tree"]["generating_commit"] == "NO_GIT" and rec["tree"]["tree_state"] == "UNKNOWN_NO_GIT"


def test_this_build_is_recorded_and_the_pre_release_stays_unrecorded(bundle_path=ROOT / "docs" / "reviews" / SLUG / "BUNDLE.json"):
    """From the relabel on, the generator writes EXECUTION_RECORD.json itself: the bundle reads generating_commit from it and names the
    tree state. The FROZEN pre-release (316d2e48) is still unrecorded -- that statement lives in the pre-release notice, not here."""
    b = json.load(open(bundle_path, encoding="utf-8"))
    src = b["source"]
    rec = json.load(open(ROOT / "docs" / "reviews" / SLUG / er.RECORD_NAME, encoding="utf-8"))
    assert src["generating_commit"] == rec["tree"]["generating_commit"] and len(src["generating_commit"]) == 40
    assert src["execution_record"]["sha256"] == hashlib.sha256((ROOT / "docs" / "reviews" / SLUG / er.RECORD_NAME).read_bytes()).hexdigest()
    assert src["execution_record"]["tree_state"] == rec["tree"]["tree_state"] in ("CLEAN", "CLEAN_EXCEPT_OWN_OUTPUTS", "DIRTY")
    if rec["tree"]["tree_state"] == "DIRTY":
        assert rec["tree"]["dirty_other_paths"], "DIRTY must name the paths"      # a scoped pass names its scope
    rs = json.load(open(ROOT / "registry" / "release_status.json", encoding="utf-8"))
    assert rs["reasons"][0]["id"] == "GENERATING_TREE_NOT_RECORDED" and "not reconstructed" in rs["reasons"][0]["text"]


# ---- verifier: the two pin invariants and the cross-link ------------------------------------------------------------------------

def _reseal(root, edit_cert):
    cert_path = os.path.join(root, "reviews", SLUG, "CERTIFICATE.json")
    cert = json.load(open(cert_path, encoding="utf-8"))
    edit_cert(cert)
    cert.pop("release_sha256")
    cert["release_sha256"] = sha256_text(canonical_json(cert))
    cb = json.dumps(cert, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    open(cert_path, "wb").write(cb)
    bpath = os.path.join(root, "reviews", SLUG, "BUNDLE.json")
    b = json.load(open(bpath, encoding="utf-8"))
    b["certificate"]["sha256_of_file"], b["certificate"]["bytes"], b["certificate"]["release_sha256"] = hashlib.sha256(cb).hexdigest(), len(cb), cert["release_sha256"]
    for rf in b["review_files"]:
        if rf["file"] == "CERTIFICATE.json":
            rf["sha256"], rf["bytes"] = hashlib.sha256(cb).hexdigest(), len(cb)
    json.dump(b, open(bpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return cert


def test_verifier_baseline_reports_pins_and_absence_agree(tmp_path):
    root = T._doctored_site(tmp_path)
    rep = T._verify(root)
    cp = rep["certificate_pins"]
    # the closure's size is a property of the import graph (81 at 2026-09-20; 83 after M2 added harness/hand_binding.py and
    # harness/result_changes.py) -- the invariant is the accounting: every entry is a blob id or a declared-absent sentinel
    assert cp["entries"] == cp["blob_ids"] + len(cp["sentinels"]) and cp["entries"] >= 81
    assert cp["sentinels"] == ["harness/effect_type.py"] == cp["declared_but_absent"] and cp["malformed"] == {}
    er_rep = rep["execution_record"]
    assert er_rep["present"] and er_rep["sha256_matches_bundle"] and er_rep["release_sha256_matches_certificate"] and er_rep["review_sha256_matches_certificate"], er_rep
    assert not any(f.startswith("CERTIFICATE_PIN_MALFORMED") or f.startswith("CERTIFICATE_ABSENCE_UNDECLARED") for f in rep["failures"])


def test_verifier_refuses_a_pin_that_is_neither_hex_nor_sentinel(tmp_path):
    root = T._doctored_site(tmp_path)
    _reseal(root, lambda c: c["analysis_code_blobs"].__setitem__("harness/verify.py", "not_present"))    # looks like the sentinel, is not
    rep = T._verify(root)
    assert any(f.startswith("CERTIFICATE_PIN_MALFORMED") and "harness/verify.py" in f for f in rep["failures"]), rep["failures"][:5]


def test_verifier_refuses_absence_declared_without_sentinel_and_sentinel_without_declaration(tmp_path):
    root = T._doctored_site(tmp_path)
    _reseal(root, lambda c: c["certificate_scope"].__setitem__("declared_but_absent", []))                # sentinel hidden
    rep = T._verify(root)
    assert any(f.startswith("CERTIFICATE_ABSENCE_UNDECLARED") for f in rep["failures"])
    root2 = T._doctored_site(tmp_path / "b")
    _reseal(root2, lambda c: c["certificate_scope"]["declared_but_absent"].append("harness/nothing.py"))  # declared without a sentinel
    rep2 = T._verify(root2)
    assert any(f.startswith("CERTIFICATE_ABSENCE_UNDECLARED") for f in rep2["failures"])


def _serve_record(root, record):
    rd = os.path.join(root, "reviews", SLUG)
    rb = (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    open(os.path.join(rd, er.RECORD_NAME), "wb").write(rb)
    bpath = os.path.join(rd, "BUNDLE.json")
    b = json.load(open(bpath, encoding="utf-8"))
    b["review_files"] = [f for f in b["review_files"] if f["file"] != er.RECORD_NAME] + [
        {"file": er.RECORD_NAME, "served_path": f"reviews/{SLUG}/{er.RECORD_NAME}", "served_url": "", "bytes": len(rb), "sha256": hashlib.sha256(rb).hexdigest()}]
    json.dump(b, open(bpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return rb


def test_verifier_accepts_a_matching_record_and_refuses_a_swapped_one(tmp_path):
    root = T._doctored_site(tmp_path)
    cert = json.load(open(os.path.join(root, "reviews", SLUG, "CERTIFICATE.json"), encoding="utf-8"))
    good = {"record_version": 1, "slug": SLUG, "utc": "2026-09-20T10:00:00Z", "tree": {"generating_commit": "a" * 40, "tree_state": "CLEAN_EXCEPT_OWN_OUTPUTS", "dirty_other_paths": []},
            "release": {"release_sha256": cert["release_sha256"], "review_sha256": cert["review_sha256"]}}
    _serve_record(root, good)
    rep = T._verify(root)
    assert rep["execution_record"]["present"] and rep["execution_record"]["sha256_matches_bundle"] and rep["execution_record"]["release_sha256_matches_certificate"]
    assert rep["execution_record"]["generating_commit"] == "a" * 40 and not any(f.startswith("EXECUTION_RECORD") for f in rep["failures"])
    # swapped: a record from another release (release_sha256 differs), bytes consistent with the bundle
    root2 = T._doctored_site(tmp_path / "b")
    _serve_record(root2, dict(good, release={"release_sha256": "f" * 64, "review_sha256": cert["review_sha256"]}))
    rep2 = T._verify(root2)
    assert any(f.startswith("EXECUTION_RECORD_MISMATCH") and "release_ok=False" in f for f in rep2["failures"])
    # tampered bytes: the record changed after the bundle digested it
    root3 = T._doctored_site(tmp_path / "c")
    _serve_record(root3, good)
    p = os.path.join(root3, "reviews", SLUG, er.RECORD_NAME)
    open(p, "ab").write(b"\n")
    rep3 = T._verify(root3)
    assert any(f.startswith("EXECUTION_RECORD_MISMATCH") and "digest_ok=False" in f for f in rep3["failures"])
