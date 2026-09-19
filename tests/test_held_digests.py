"""Held-bytes digest limb (harness/held_digests.py). PLANT: the two classes the 2026-09-19 corpus sweep found live on
main -- a digest of CRLF bytes git never stored (cache/pcsk9-mace/harms_aact_held.json, 5 citing records incl. the
served pcsk9 review) and the digest of an unheld PDF recorded against its extracted text (glp1 MedR, 7 citing records
incl. the served glp1 review) -- are re-created in a throwaway tree and the limb must refuse each by name; the main
tree at the pre-fix commit 8c8874b4 is checked from git and must refuse too (the limb fired pre-fix)."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import held_digests as H  # noqa: E402

PRE_FIX = "8c8874b4"


def _tree(tmp_path: Path) -> Path:
    root = tmp_path / "tree"
    (root / "cache" / "t").mkdir(parents=True)
    (root / "docs").mkdir()
    return root


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1), encoding="utf-8", newline="\n")


def test_plant_crlf_of_committed_is_refused_by_name(tmp_path):
    root = _tree(tmp_path)
    held = root / "cache" / "t" / "held.json"
    held.write_bytes(b'{"a": 1}\n{"b": 2}\n')
    crlf_digest = hashlib.sha256(b'{"a": 1}\r\n{"b": 2}\r\n').hexdigest()
    _write_json(root / "cache" / "t" / "verified_arms.json",
                {"1": {"outcome": "x", "document_ref": "cache/t/held.json", "document_sha256": crlf_digest}})
    ok, problems, counts = H.check(str(root))
    assert not ok and counts.get(H.CRLF_OF_COMMITTED) == 1
    assert "cache/t/verified_arms.json/1/document_sha256" in problems[0] and "CRLF" in problems[0]


def test_plant_unheld_original_recorded_against_its_text_is_refused(tmp_path):
    root = _tree(tmp_path)
    txt = root / "cache" / "t" / "doc.pdf.txt"
    txt.write_bytes(b"extracted text\n")
    pdf_digest = hashlib.sha256(b"%PDF the original, not in the tree").hexdigest()
    _write_json(root / "cache" / "t" / "verified_effects.json",
                {"2": [{"outcome": "y", "document_ref": "cache/t/doc.pdf.txt", "document_sha256": pdf_digest}]})
    ok, problems, counts = H.check(str(root))
    assert not ok and counts.get(H.OTHER_MISMATCH) == 1 and "does not equal the bytes on disk" in problems[0]


def test_declared_unheld_document_passes_and_undeclared_missing_file_refuses(tmp_path):
    root = _tree(tmp_path)
    d = "0" * 64
    _write_json(root / "cache" / "t" / "a.json", {"document_sha256": d, "document_held": False, "path": "cache/t/x.txt"})
    ok, problems, counts = H.check(str(root))
    assert ok and counts.get(H.UNHELD_DECLARED) == 1
    _write_json(root / "cache" / "t" / "b.json", {"document_sha256": d, "document_path": "cache/t/missing.pdf"})
    ok, problems, counts = H.check(str(root))
    assert not ok and counts.get(H.UNHELD) == 1 and "not in the tree" in problems[0]


def test_pairing_is_by_name_then_kind(tmp_path):
    root = _tree(tmp_path)
    body = root / "cache" / "t" / "body.txt"; body.write_bytes(b"body\n")
    raw = root / "cache" / "t" / "raw.xml"; raw.write_bytes(b"<xml/>\n")
    _write_json(root / "cache" / "t" / "manifest.json",
                {"body_file": "cache/t/body.txt", "body_raw_file": "cache/t/raw.xml",
                 "body_sha256": hashlib.sha256(b"body\n").hexdigest()})
    ok, problems, counts = H.check(str(root))
    assert ok and counts.get(H.MATCH) == 1, problems
    # a document digest never pairs with a text-only sibling
    _write_json(root / "cache" / "t" / "src.json",
                {"document_sha256": "1" * 64, "extracted_text_path": "cache/t/body.txt"})
    ok, problems, counts = H.check(str(root))
    assert ok and counts.get(H.NOT_CHECKABLE) == 1


def test_main_at_prefix_refused_and_this_tree_passes():
    """The limb on the pre-fix corpus: the two served reviews and their caches are read from git."""
    def show(path):
        return subprocess.run(["git", "show", f"{PRE_FIX}:{path}"], cwd=ROOT, capture_output=True, text=True,
                              encoding="utf-8", errors="replace").stdout
    row = json.loads(show("cache/pcsk9-mace/verified_arms.json"))["25773378"]
    row = row if isinstance(row, dict) else row[0]
    committed = show("cache/pcsk9-mace/harms_aact_held.json").encode("utf-8")
    assert row["document_sha256"] != hashlib.sha256(committed).hexdigest()
    assert row["document_sha256"] == hashlib.sha256(committed.replace(b"\n", b"\r\n")).hexdigest(), "pre-fix: digest of the CRLF form"
    ok, problems, counts = H.check(str(ROOT))
    assert ok, problems
    assert counts.get(H.MATCH, 0) > 1000 and not any(k in counts for k in H.REFUSING)
