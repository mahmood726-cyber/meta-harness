"""The committed release archives (docs/releases/<slug>/<commit12>/) are FROZEN and self-verifying: each one, unpacked in a
fresh directory with nothing from this repository on the path, passes its own offline replay -- and a damaged copy fails it.

These tests exercise the committed archive bytes, never a rebuild, so a later change to the served tree cannot make an
archive look stale: an archive describes its commit, not HEAD (scripts/release_archive.py).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RELEASES = sorted((ROOT / "docs" / "releases").glob("*/*/RELEASE.json"))


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def test_there_is_a_frozen_glp1_archive():
    # the denominator: without this, every parametrised test below would silently collect nothing
    assert any(p.parts[-3] == "glp1-ra-mace-t2d" for p in RELEASES), RELEASES


def _unpack(rel_json: Path, dest: Path) -> tuple[dict, Path]:
    rel = json.loads(rel_json.read_text(encoding="utf-8"))
    z = rel_json.parent / f"{rel['archive']}.zip"
    listed = (rel_json.parent / "SHA256SUMS").read_text(encoding="utf-8").split()
    assert listed == [_sha(z.read_bytes()), z.name], "the served SHA256SUMS does not describe the served zip"
    with zipfile.ZipFile(z) as f:
        f.extractall(dest)
    root = dest / rel["archive"]
    assert (root / "RELEASE.json").read_bytes() == rel_json.read_bytes(), "served RELEASE.json differs from the archived one"
    return rel, root


@pytest.mark.parametrize("rel_json", RELEASES, ids=lambda p: "/".join(p.parts[-3:-1]))
def test_served_sha256sums_is_what_sha256sum_c_reads(rel_json):
    """`sha256sum -c SHA256SUMS` is the check the README invites. It reads each line as `<64 hex>  <name>` up to LF; a CR
    becomes part of the file name and the check fails open-or-read (measured on the served file of 00b8337c, which a
    Windows write_text had given CRLF). Every served text file of an archive is LF-only."""
    d = rel_json.parent
    for name in ("SHA256SUMS", "README.md", "RELEASE.json"):
        assert b"\r" not in (d / name).read_bytes(), f"{name} carries CR"
    lines = (d / "SHA256SUMS").read_bytes().decode("ascii").split("\n")
    assert lines[-1] == "" and all(len(ln.split("  ", 1)[0]) == 64 and (d / ln.split("  ", 1)[1]).is_file()
                                   for ln in lines[:-1]), lines


@pytest.mark.parametrize("rel_json", RELEASES, ids=lambda p: "/".join(p.parts[-3:-1]))
def test_archive_is_complete_and_every_digest_holds(rel_json, tmp_path):
    rel, root = _unpack(rel_json, tmp_path)
    sums = dict(reversed(line.split("  ", 1)) for line in (root / "SHA256SUMS").read_text(encoding="utf-8").splitlines())
    on_disk = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    assert sorted(sums) == on_disk, "SHA256SUMS does not list exactly the files in the archive"
    assert all(_sha((root / n).read_bytes()) == d for n, d in sums.items())
    assert sorted(f["path"] for f in rel["files"]) == sorted(n for n in on_disk if n.startswith("site/"))
    for f in rel["files"]:
        assert _sha((root / f["path"]).read_bytes()) == f["sha256"], f["path"]
    # the pinned modules are the certificate's bytes (git blob id recomputed from the archived file)
    cert = json.loads((root / f"site/reviews/{rel['slug']}/CERTIFICATE.json").read_text(encoding="utf-8"))
    assert cert["release_sha256"] == rel["release_sha256"]
    for p, blob in cert["analysis_code_blobs"].items():
        if blob == "NOT_PRESENT":
            continue
        data = (root / "site" / p).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest() == blob, p


@pytest.mark.parametrize("rel_json", RELEASES, ids=lambda p: "/".join(p.parts[-3:-1]))
def test_archive_replays_offline_from_a_fresh_directory(rel_json, tmp_path):
    """The README's offline commands, run as an outsider would: cwd inside the unpacked archive, PYTHONPATH empty, the
    archive's own copies of the verifiers."""
    rel, root = _unpack(rel_json, tmp_path)
    env = {"PATH": "", "SYSTEMROOT": __import__("os").environ.get("SYSTEMROOT", ""), "PYTHONPATH": "", "PYTHONIOENCODING": "utf-8"}
    sums = subprocess.run([sys.executable, "check_sha256sums.py"], cwd=root, capture_output=True, text=True, env=env,
                          stdin=subprocess.DEVNULL)
    assert sums.returncode == 0, sums.stdout + sums.stderr
    vb = subprocess.run([sys.executable, "site/scripts/verify_bundle.py", "--root", "site", "--slug", rel["slug"]],
                        cwd=root, capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL, encoding="utf-8")
    assert vb.returncode == 0 and "verdict PASS" in vb.stdout, vb.stdout[-2000:] + vb.stderr[-2000:]
    au = subprocess.run([sys.executable, "site/scripts/audit_certificate_stdlib.py",
                         f"site/reviews/{rel['slug']}/CERTIFICATE.json", "site"],
                        cwd=root, capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL, encoding="utf-8")
    assert au.returncode == 0 and "RESULT REPRODUCED" in au.stdout and rel["release_sha256"] in au.stdout, au.stdout


@pytest.mark.parametrize("rel_json", RELEASES, ids=lambda p: "/".join(p.parts[-3:-1]))
def test_plant_a_damaged_archive_fails_its_own_checks(rel_json, tmp_path):
    rel, root = _unpack(rel_json, tmp_path)
    review = root / f"site/reviews/{rel['slug']}/review.json"
    # a VALUE change, not whitespace: the verifier hashes canonical JSON, so reformatting alone would rightly still pass
    doc = json.loads(review.read_text(encoding="utf-8"))
    primary = next(o for o in doc["outcomes"] if o.get("primary"))
    primary["result"]["estimate"] = primary["result"]["estimate"] * 1.01
    before = review.read_bytes()
    review.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    assert review.read_bytes() != before
    sums = subprocess.run([sys.executable, "check_sha256sums.py"], cwd=root, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL)
    assert sums.returncode == 1 and "FAILED" in sums.stdout
    spec = importlib.util.spec_from_file_location("_archived_verify_bundle", root / "site/scripts/verify_bundle.py")
    vb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vb)
    try:
        rep = vb.run(vb.Store(str(root / "site"), None), rel["slug"], None)
        verdict = rep["verdict"]
    except vb.Refusal:
        verdict = "REFUSED"
    assert verdict != "PASS"
