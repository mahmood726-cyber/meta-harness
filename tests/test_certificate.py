"""Certificate refusal plants, runnable before the certificate implementation exists."""
import importlib
import json
import shutil
from pathlib import Path
import pytest

from harness import gate
from scripts import reproduce_review

ROOT = Path(__file__).resolve().parents[1]
SLUG = "glp1-ra-mace-t2d"


def test_held_document_byte_mutation_refuses(tmp_path, monkeypatch):
    # Copy held inputs only; the statistical replay continues using its unchanged cache.
    for folder in ("cache/" + SLUG, "topics", "protocols", "harness", "scripts",
                   "outputs/handover/glp1_regulatory"):
        shutil.copytree(ROOT / folder, tmp_path / folder)
    held = next((tmp_path / "outputs/handover/glp1_regulatory").rglob("*.txt"))
    before = held.read_bytes()
    held.write_bytes(bytes([before[0] ^ 1]) + before[1:])
    try:
        certificate = importlib.import_module("harness.certificate")
    except ModuleNotFoundError:
        certificate = None
    if certificate:
        monkeypatch.setattr(certificate, "ROOT", tmp_path)
        review = json.loads((ROOT / "docs/reviews" / SLUG / "review.json").read_text(encoding="utf-8"))
        saved = review["reproduction"]["certificate"]
        changed = certificate.compute(SLUG, review, saved["protocol_sha"])
        assert changed["release_sha256"] != saved["release_sha256"]
        assert {k for k in saved if saved[k] != changed[k]} == {"held_documents", "release_sha256"}
        print(f"one-byte plant: saved release_sha256={saved['release_sha256']}; recomputed={changed['release_sha256']}")
    ok, reasons = reproduce_review.reproduce(SLUG)
    print(f"held-document reproduction: ok={ok}; reasons={reasons}")
    assert not ok and any("release_sha256" in r for r in reasons), (
        f"held text changed by one byte but reproduce returned {ok}: {reasons}")


def test_missing_certificate_gate_refuses(tmp_path):
    review_dir = tmp_path / SLUG
    shutil.copytree(ROOT / "docs/reviews" / SLUG, review_dir)
    (review_dir / "CERTIFICATE.json").unlink(missing_ok=True)
    ok, reasons = gate.gate_page(str(review_dir))
    print(f"missing-certificate gate: ok={ok}; reasons={reasons}")
    assert not ok and any("CERTIFICATE.json" in r for r in reasons), (
        f"missing certificate has no certificate refusal: {reasons}")


def test_certificate_body_tampering_refuses(tmp_path):
    from harness import certificate
    directory = tmp_path / SLUG
    shutil.copytree(ROOT / "docs/reviews" / SLUG, directory)
    path = directory / "CERTIFICATE.json"
    saved = json.loads(path.read_text(encoding="utf-8"))
    saved["held_documents"] = []  # Keep the original release hash: must still refuse.
    path.write_text(json.dumps(saved), encoding="utf-8")
    assert any("release_sha256 mismatch" in r for r in certificate.verify(directory))


@pytest.mark.parametrize("replacement", [None, [], True])
def test_malformed_certificate_refuses(tmp_path, replacement):
    from harness import certificate
    directory = tmp_path / SLUG
    shutil.copytree(ROOT / "docs/reviews" / SLUG, directory)
    (directory / "CERTIFICATE.json").write_text(json.dumps(replacement), encoding="utf-8")
    assert certificate.verify(directory)


def test_json_type_change_cannot_reuse_release_hash(tmp_path):
    from harness import certificate
    directory = tmp_path / SLUG
    shutil.copytree(ROOT / "docs/reviews" / SLUG, directory)
    path = directory / "CERTIFICATE.json"
    saved = json.loads(path.read_text(encoding="utf-8"))
    saved["schema_version"] = True  # Python True == 1, but canonical JSON bytes differ.
    path.write_text(json.dumps(saved), encoding="utf-8")
    assert certificate.verify(directory)


def test_fresh_clone_path_cannot_bypass_missing_certificate(tmp_path, monkeypatch):
    import tempfile
    original = tmp_path / "original"
    clone = tmp_path / "clone"
    for base in (original, clone):
        shutil.copytree(ROOT / "docs/reviews" / SLUG, base / "docs/reviews" / SLUG)
    (original / "docs/reviews" / SLUG / "CERTIFICATE.json").unlink()
    # Isolate the fresh-clone comparison, with identical original/clone HTML.
    monkeypatch.setattr(reproduce_review, "ROOT", str(original))
    monkeypatch.setattr(tempfile, "mkdtemp", lambda **kwargs: str(clone))
    monkeypatch.setattr(reproduce_review.subprocess, "check_call", lambda *a, **kw: 0)
    monkeypatch.setattr(reproduce_review.subprocess, "check_output", lambda *a, **kw: "HEAD")
    assert reproduce_review._fresh_clone_check() == [SLUG]


def test_all_certificate_inputs_and_manuscript_match():
    from harness import certificate, manuscript
    from harness.canonical import canonical_json, sha256_text
    for directory in sorted((ROOT / "docs/reviews").iterdir()):
        cert = json.loads((directory / "CERTIFICATE.json").read_text(encoding="utf-8"))
        review = json.loads((directory / "review.json").read_text(encoding="utf-8"))
        assert not certificate.verify(directory)
        assert cert["release_sha256"] == sha256_text(canonical_json(
            {k: v for k, v in cert.items() if k != "release_sha256"}))
        assert cert["manuscript_sha256"] == sha256_text(manuscript.render(review))
        assert manuscript.render(review) in (directory / "index.html").read_text(encoding="utf-8")
