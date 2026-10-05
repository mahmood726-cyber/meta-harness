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


def test_a_partial_full_text_rerun_keeps_every_row_it_did_not_touch(tmp_path, monkeypatch):
    import k_gap_exclusion_fulltext as ef
    prev = {"rows": [{"slug": "a", "pmid": "1", "class_after": "TRUE_SCOPE_DIFFERENCE", "how": "RECORDED_READER:x"},
                     {"slug": "b", "pmid": "2", "class_after": "SCREENER_ERROR", "how": "REGEX_ON_FULLTEXT"}]}
    (tmp_path / "exclusion_fulltext.json").write_text(json.dumps(prev), encoding="utf-8")
    monkeypatch.setattr(ef, "OUT", str(tmp_path))
    monkeypatch.setattr(ef, "RUNS", str(tmp_path / "runs.json"))
    monkeypatch.setattr(ef, "_pilot", lambda: None)
    monkeypatch.setattr(ef, "items", lambda run: [{"slug": "c", "pmid": "3", "label": "C", "rule_id": "X1",
                                                   "subclass_before": "S", "rec": None, "fulltext": "",
                                                   "fulltext_source": None}])
    ef.main(["--only=c:3"])
    rows = {(r["slug"], r["pmid"]): r for r in json.load(open(tmp_path / "exclusion_fulltext.json"))["rows"]}
    assert rows[("a", "1")] == prev["rows"][0] and rows[("b", "2")] == prev["rows"][1]
    assert rows[("c", "3")]["class_after"] == "INSUFFICIENT_RECORD"
