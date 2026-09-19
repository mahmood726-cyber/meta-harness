"""Plant: a swapped validator must move the certificate.

A fourth independent audit declined to issue a gate verdict because a hostile-test verdict
must bind to the validator's bytes as well as the review's identity, and the certificate's
analysis_code_blobs was a hand-written literal of five files. The endpoint binder, the
publication gate, the manuscript renderer, the canonicalizer that computes every digest and
the certificate builder itself were all unpinned: swapping any of them produced a
byte-identical certificate. This file was written before the fix and fired on all five.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SLUG = "glp1-ra-mace-t2d"

# Each was unpinned at 4d33b7af; pipeline.py is the positive control (pinned before the fix).
SWAPPABLE = ["harness/target_endpoint.py", "harness/gate.py", "harness/manuscript.py",
             "harness/canonical.py", "harness/certificate.py", "harness/pipeline.py"]


def _tree(tmp_path):
    for folder in ("cache/" + SLUG, "topics", "protocols", "harness", "scripts",
                   "outputs/handover/glp1_regulatory"):
        shutil.copytree(ROOT / folder, tmp_path / folder)
    return tmp_path


def _compute(monkeypatch, root):
    from harness import certificate
    monkeypatch.setattr(certificate, "ROOT", root)
    review = json.loads((ROOT / "docs/reviews" / SLUG / "review.json").read_text(encoding="utf-8"))
    return certificate.compute(SLUG, review, review["reproduction"]["certificate"]["protocol_sha"])


@pytest.mark.parametrize("ref", SWAPPABLE)
def test_swapped_validator_bytes_move_the_certificate(tmp_path, monkeypatch, ref):
    root = _tree(tmp_path)
    before = _compute(monkeypatch, root)
    target = root / ref
    # The smallest possible swap: different bytes, same behaviour. A real swap is at least this.
    target.write_bytes(target.read_bytes() + b"\n# swapped implementation\n")
    after = _compute(monkeypatch, root)
    assert ref in before["analysis_code_blobs"], f"{ref} is not pinned by the certificate"
    assert after["analysis_code_blobs"][ref] != before["analysis_code_blobs"][ref]
    assert after["release_sha256"] != before["release_sha256"], (
        f"swapping {ref} produced an identical certificate")
    moved = {k for k in before if before[k] != after[k]}
    assert moved == {"analysis_code_blobs", "analysis_code_sha256", "release_sha256"}, moved
    print(f"swap plant {ref}: release_sha256 {before['release_sha256'][:12]} -> {after['release_sha256'][:12]}")


def test_pinned_map_is_the_import_closure_of_the_declared_roots():
    from harness import certificate
    from harness.code_closure import closure
    cert = json.loads((ROOT / "docs/reviews" / SLUG / "CERTIFICATE.json").read_text(encoding="utf-8"))
    reached = set(closure(certificate.ROOTS, ROOT))
    present = {k for k, v in cert["analysis_code_blobs"].items() if v != certificate.NOT_PRESENT}
    assert present == reached, {"unpinned": reached - present, "extra": present - reached}
    absent = {k for k, v in cert["analysis_code_blobs"].items() if v == certificate.NOT_PRESENT}
    assert absent == {r for r in (*certificate.ROOTS, *certificate.OPTIONAL) if not (ROOT / r).exists()}
    assert "harness/effect_type.py" in absent  # the honest marker survives the derivation
    for name in ("harness/target_endpoint.py", "harness/gate.py", "harness/manuscript.py",
                 "harness/canonical.py", "harness/certificate.py", "harness/code_closure.py"):
        assert name in present


def test_pinned_blob_identities_are_what_git_stores():
    """The stdlib blob computation must agree with git for every pinned path, so an auditor
    without git and an auditor with git compute the same identity."""
    cert = json.loads((ROOT / "docs/reviews" / SLUG / "CERTIFICATE.json").read_text(encoding="utf-8"))
    present = {k: v for k, v in cert["analysis_code_blobs"].items() if v != "NOT_PRESENT"}
    out = subprocess.run(["git", "hash-object", "--", *present], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.split()
    assert dict(zip(present, out)) == present


def _stdlib_audit(cert_path, tree=None, cwd=None):
    """Run the independent auditor script from OUTSIDE the checkout, importing no harness code."""
    args = [sys.executable, str(ROOT / "scripts/audit_certificate_stdlib.py"), str(cert_path)]
    if tree is not None:
        args.append(str(tree))
    env = {**os.environ, "PYTHONPATH": ""}
    return subprocess.run(args, capture_output=True, text=True, cwd=cwd or tempfile.gettempdir(), env=env)


def test_stdlib_audit_reproduces_every_served_certificate():
    for directory in sorted((ROOT / "docs/reviews").iterdir()):
        proc = _stdlib_audit(directory / "CERTIFICATE.json", ROOT)
        assert proc.returncode == 0 and "RESULT REPRODUCED" in proc.stdout, (directory.name, proc.stdout)
        blobs = json.loads((directory / "CERTIFICATE.json").read_text(encoding="utf-8"))["analysis_code_blobs"]
        n = sum(1 for v in blobs.values() if v != "NOT_PRESENT")
        assert f"{n} blob identities recomputed" in proc.stdout


def test_stdlib_audit_refuses_a_swapped_blob_and_a_tampered_body(tmp_path):
    cert = json.loads((ROOT / "docs/reviews" / SLUG / "CERTIFICATE.json").read_text(encoding="utf-8"))
    swapped = json.loads(json.dumps(cert))
    swapped["analysis_code_blobs"]["harness/target_endpoint.py"] = "0" * 40
    (tmp_path / "swapped.json").write_text(json.dumps(swapped), encoding="utf-8")
    proc = _stdlib_audit(tmp_path / "swapped.json", ROOT)
    assert proc.returncode == 1 and "harness/target_endpoint.py: stored 0000" in proc.stdout
    assert "MISMATCH analysis_code_sha256" in proc.stdout and "MISMATCH release_sha256" in proc.stdout
    tampered = json.loads(json.dumps(cert))
    tampered["certificate_scope"]["covers"] = "everything"
    (tmp_path / "tampered.json").write_text(json.dumps(tampered), encoding="utf-8")
    proc = _stdlib_audit(tmp_path / "tampered.json")
    assert proc.returncode == 1 and "MISMATCH release_sha256" in proc.stdout


def test_certificate_scope_names_its_limits():
    from harness import certificate
    cert = json.loads((ROOT / "docs/reviews" / SLUG / "CERTIFICATE.json").read_text(encoding="utf-8"))
    scope = cert["certificate_scope"]
    assert list(scope["roots"]) == list(certificate.ROOTS)
    unreached = sorted(p.as_posix() for p in (ROOT / "harness").glob("*.py")
                       if "harness/" + p.name not in cert["analysis_code_blobs"]
                       for p in [Path("harness") / p.name])
    assert scope["not_covered"]["in_tree_modules_not_imported_by_any_root"] == unreached
    for phrase in ("standard library", "third-party", "scripts/verify_all.py", "search_v2"):
        assert phrase in json.dumps(scope), phrase
    # Pinning bytes is not vouching for a component's self-reported status (e.g. an OWED field may be stale).
    assert "never by reading the field" in scope["pins_bytes_not_self_reports"]
    assert "OWED" in scope["pins_bytes_not_self_reports"]
    assert scope["not_covered"]["in_tree_modules_not_imported_by_any_root"], "an empty list here would be a claim of total coverage"
    # The scope is part of what release_sha256 covers: editing it is a release change.
    assert "certificate_scope" in cert["hash_inputs"]
