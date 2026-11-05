"""scripts/production_record.py: the per-file manifest must bind each page's html_sha256, and check-artifact
must REFUSE an artifact that differs from the manifest by one byte in one file (the defect class: a deploy
that re-tars a tree nobody verified). Synthetic docs tree in a temp dir; no network."""
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "production_record.py")


def _run(*args):
    return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", cwd=ROOT)


def _mini_docs(tmp, page_bytes=b"<p>page</p>", bind_ok=True):
    d = os.path.join(tmp, "docs")
    os.makedirs(os.path.join(d, "reviews", "zz-plant"))
    io.open(os.path.join(d, "index.html"), "wb").write(b"<p>index</p>")
    io.open(os.path.join(d, "reviews", "zz-plant", "index.html"), "wb").write(page_bytes)
    h = hashlib.sha256(page_bytes).hexdigest() if bind_ok else "0" * 64
    io.open(os.path.join(d, "reviews", "zz-plant", "manifest.json"), "w", encoding="utf-8").write(
        json.dumps({"slug": "zz-plant", "html_sha256": h, "review_sha256": "abc"}))
    return d


def _tar_of(docs, mutate=None, include_manifest=True):
    p = os.path.join(os.path.dirname(docs), "artifact.tar")
    with tarfile.open(p, "w") as t:
        for root, _, files in os.walk(docs):
            for fn in files:
                fp = os.path.join(root, fn)
                rel = os.path.relpath(fp, docs).replace(os.sep, "/")
                b = open(fp, "rb").read()
                if mutate and rel == mutate:
                    b += b" "
                ti = tarfile.TarInfo(rel)
                ti.size = len(b)
                t.addfile(ti, io.BytesIO(b))
        if include_manifest:
            # The actual Pages artifact includes the self-excluded production receipt.
            manifest_path = os.path.join(os.path.dirname(docs), "m.json")
            receipt = open(manifest_path, "rb").read()
            entry = tarfile.TarInfo("./_production/manifest.json")
            entry.size = len(receipt)
            t.addfile(entry, io.BytesIO(receipt))
    return p


def test_manifest_binds_html_sha256_and_refuses_when_unbound():
    with tempfile.TemporaryDirectory() as tmp:
        d = _mini_docs(tmp)
        out = os.path.join(tmp, "m.json")
        r = _run("manifest", "--docs", d, "--out", out)
        assert r.returncode == 0, r.stdout + r.stderr
        m = json.load(open(out, encoding="utf-8"))
        assert m["n_files"] == 3 and m["review_page_bindings"][0]["bound"] is True
    with tempfile.TemporaryDirectory() as tmp:
        d = _mini_docs(tmp, bind_ok=False)
        r = _run("manifest", "--docs", d, "--out", os.path.join(tmp, "m.json"))
        assert r.returncode == 1 and "MANIFEST REFUSED" in r.stdout


def test_check_artifact_refuses_a_one_byte_difference_and_passes_the_identical_tree():
    with tempfile.TemporaryDirectory() as tmp:
        d = _mini_docs(tmp)
        out = os.path.join(tmp, "m.json")
        assert _run("manifest", "--docs", d, "--out", out).returncode == 0
        good = _tar_of(d)
        r = _run("check-artifact", "--manifest", out, "--tar", good)
        assert r.returncode == 0 and "artifact == manifest" in r.stdout
        bad = _tar_of(d, mutate="reviews/zz-plant/index.html")
        r = _run("check-artifact", "--manifest", out, "--tar", bad)
        assert r.returncode == 1 and "ARTIFACT REFUSED" in r.stdout and "reviews/zz-plant/index.html" in r.stdout

def test_check_artifact_refuses_ambiguous_or_unsafe_tar_members():
    # The original verifier used name.lstrip("./") and overwrote duplicate keys.
    # All of these artificial archives previously passed the digest-set check.
    for case in ("parent_alias", "absolute_alias", "duplicate", "symlink",
                 "hardlink", "production_extra", "production_mutation"):
        with tempfile.TemporaryDirectory() as tmp:
            d = _mini_docs(tmp)
            manifest = os.path.join(tmp, "m.json")
            assert _run("manifest", "--docs", d, "--out", manifest).returncode == 0
            artifact = _tar_of(d)
            page = open(os.path.join(d, "reviews", "zz-plant", "index.html"), "rb").read()
            with tarfile.open(artifact, "a") as tar:
                if case in ("parent_alias", "absolute_alias", "duplicate"):
                    path = {"parent_alias": "../reviews/zz-plant/index.html",
                            "absolute_alias": "/reviews/zz-plant/index.html",
                            "duplicate": "reviews/zz-plant/index.html"}[case]
                    entry = tarfile.TarInfo(path)
                    entry.size = len(page)
                    tar.addfile(entry, io.BytesIO(page))
                elif case in ("symlink", "hardlink"):
                    entry = tarfile.TarInfo("other")
                    entry.type = tarfile.SYMTYPE if case == "symlink" else tarfile.LNKTYPE
                    entry.linkname = "../reviews/zz-plant/index.html"
                    tar.addfile(entry)
                else:
                    name = "_production/extra.txt" if case == "production_extra" else "_production/manifest.json"
                    data = b"unreceipted bytes" if case == "production_extra" else b"tampered manifest"
                    entry = tarfile.TarInfo(name)
                    entry.size = len(data)
                    tar.addfile(entry, io.BytesIO(data))
            result = _run("check-artifact", "--manifest", manifest, "--tar", artifact)
            assert result.returncode == 1, (case, result.stdout, result.stderr)
            assert "ARTIFACT REFUSED" in result.stdout, (case, result.stdout)


def test_check_artifact_accepts_exact_embedded_production_manifest():
    with tempfile.TemporaryDirectory() as tmp:
        d = _mini_docs(tmp)
        manifest = os.path.join(tmp, "m.json")
        assert _run("manifest", "--docs", d, "--out", manifest).returncode == 0
        artifact = _tar_of(d)
        result = _run("check-artifact", "--manifest", manifest, "--tar", artifact)
        assert result.returncode == 0, result.stdout + result.stderr


def test_check_artifact_refuses_missing_embedded_manifest():
    # Previous checker considered only manifest['files'] and allowed the served receipt to vanish.
    with tempfile.TemporaryDirectory() as tmp:
        d = _mini_docs(tmp)
        manifest = os.path.join(tmp, "m.json")
        assert _run("manifest", "--docs", d, "--out", manifest).returncode == 0
        artifact = _tar_of(d, include_manifest=False)
        result = _run("check-artifact", "--manifest", manifest, "--tar", artifact)
        assert result.returncode == 1, result.stdout + result.stderr
        assert "ARTIFACT REFUSED: missing embedded _production/manifest.json" in result.stdout


def test_check_artifact_refuses_unreceipted_file():
    with tempfile.TemporaryDirectory() as tmp:
        d = _mini_docs(tmp)
        manifest = os.path.join(tmp, "m.json")
        assert _run("manifest", "--docs", d, "--out", manifest).returncode == 0
        artifact = _tar_of(d)
        with tarfile.open(artifact, "a") as tar:
            entry = tarfile.TarInfo("unlisted.html")
            entry.size = 4
            tar.addfile(entry, io.BytesIO(b"oops"))
        result = _run("check-artifact", "--manifest", manifest, "--tar", artifact)
        assert result.returncode == 1, result.stdout + result.stderr
        assert "unlisted.html" in result.stdout


def test_attest_requires_exact_served_receipt_even_when_pages_match(monkeypatch, tmp_path):
    """The published production receipt is separately served; artifact equality is not enough.

    No network, article data, legacy cache or live deployment is touched.  The
    real cmd_attest executes with a stubbed HTTP fetch and deterministic clock.
    """
    import importlib.util
    from types import SimpleNamespace

    spec = importlib.util.spec_from_file_location("production_record_receipt_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    body = b"<p>synthetic served page</p>"
    manifest = tmp_path / "verified-manifest.json"
    manifest.write_text(json.dumps({
        "commit_sha": "a" * 40,
        "files": {"index.html": hashlib.sha256(body).hexdigest()},
    }), encoding="utf-8")
    exact_receipt = manifest.read_bytes()

    monkeypatch.setattr(module, "_attest_target", lambda _m, _base: "TARGET production_record.attest: synthetic")
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)

    for case, served_receipt, expected_exit in (
        ("missing", None, 1),
        ("mutated", b"changed but superficially valid", 1),
        ("exact", exact_receipt, 0),
    ):
        ticks = [0]

        def clock():
            ticks[0] += 1
            return 0.0 if ticks[0] == 1 else (0.1 if ticks[0] == 2 else 2.0)

        monkeypatch.setattr(module.time, "time", clock)
        calls = []

        def fetch(url, timeout=60):
            calls.append(url)
            if "/index.html?" in url:
                return 200, body
            if "/_production/manifest.json?" in url:
                return (404, b"") if served_receipt is None else (200, served_receipt)
            raise AssertionError("unexpected URL: " + url)

        monkeypatch.setattr(module, "_fetch", fetch)
        record_path = tmp_path / f"{case}-record.json"
        args = SimpleNamespace(
            manifest=str(manifest), base_url="https://synthetic.invalid/",
            record=str(record_path), pages_artifact_id="synthetic-id",
            environment="synthetic", retry_seconds=1,
        )
        assert module.cmd_attest(args) == expected_exit
        record = json.loads(record_path.read_text(encoding="utf-8"))
        assert record["n_files"] == 2
        assert record["n_mismatch"] == expected_exit
        assert record["verdict"] == ("ATTESTED" if expected_exit == 0 else "MISMATCH")
        assert record["files"]["index.html"]["equal"] is True
        assert record["files"]["_production/manifest.json"]["equal"] is (expected_exit == 0)
        assert len(calls) == 2, calls


def test_attest_refuses_receipt_only_empty_page_manifest(tmp_path):
    """Adding a required receipt must not turn an empty page set into success."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("production_record_empty_attest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manifest = tmp_path / "empty-manifest.json"
    manifest.write_text(json.dumps({"commit_sha": "a" * 40, "files": {}}), encoding="utf-8")
    target = module._attest_target(str(manifest), "https://synthetic.invalid/")
    assert target.startswith("TARGET production_record.attest: COULD-NOT-EXECUTE")
    assert "manifest has no page files" in target
