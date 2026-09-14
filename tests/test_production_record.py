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


def _tar_of(docs, mutate=None):
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
