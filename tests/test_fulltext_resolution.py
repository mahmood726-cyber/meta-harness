"""The tracker reads the full-text exclusion stage (k_gap_exclusion_fulltext.json) for an exclusion the abstract-level
audit left INSUFFICIENT_RECORD, and checks a 'fulltext' span against the held full text by digest: colchicine-postop
Zarpelon's open-label statement is in its full text only."""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402

FT = "Methods. This is a prospective, randomized, open, single-center clinical assay, whose 140 participants were recruited."
SPAN = "This is a prospective, randomized, open, single-center clinical assay"


def _setup(tmp_path, monkeypatch, sha=None):
    (tmp_path / "_ft").mkdir()
    (tmp_path / "_ft" / "27223641.txt").write_text(FT, encoding="utf-8")
    monkeypatch.setattr(gt, "OUT", str(tmp_path))
    monkeypatch.setattr(gt, "_AUDIT", {("colchicine-postop-af", "27223641"):
                                       {"class": "INSUFFICIENT_RECORD", "subclass": "BLINDING_NOT_STATED"}})
    sp = {"field": "fulltext", "text": SPAN, "sha256": sha or hashlib.sha256(FT.encode("utf-8")).hexdigest(),
          "chars": len(FT)}
    monkeypatch.setattr(gt, "_FT_AUDIT", {("colchicine-postop-af", "27223641"):
                                          {"class_after": "TRUE_SCOPE_DIFFERENCE", "subclass_after": "OPEN_LABEL_STATED",
                                           "span": sp}})
    return sp


def test_a_full_text_resolution_names_the_exclusion(tmp_path, monkeypatch):
    sp = _setup(tmp_path, monkeypatch)
    assert gt.exclusion_audit_class("colchicine-postop-af", "27223641")[0] == "TRUE_SCOPE_DIFFERENCE"
    assert gt.exclusion_audit_span("colchicine-postop-af", "27223641") == sp
    assert gt.span_is_verbatim("colchicine-postop-af", "27223641", sp)


def test_a_different_full_text_never_verifies_the_span(tmp_path, monkeypatch):
    sp = _setup(tmp_path, monkeypatch, sha="0" * 64)
    assert not gt.span_is_verbatim("colchicine-postop-af", "27223641", sp)
