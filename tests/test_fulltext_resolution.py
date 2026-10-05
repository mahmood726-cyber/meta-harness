"""The tracker reads the full-text exclusion stage (exclusion_fulltext.json) for an exclusion the abstract-level audit left
INSUFFICIENT_RECORD, and checks a 'fulltext' span against the held full text by its recorded digest: colchicine-postop
Zarpelon's open-label statement is in its full text only.

Requirement-level (consolidation 2026-10-05: g1/finish-line and another lane built this twice; the kept implementation is
g1_tracker._ft_resolution / held_fulltext, which also keeps a recorded MODEL reader's verdict a proposal)."""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402
import k_gap_counterfactual as cfm  # noqa: E402

FT = "Methods. This is a prospective, randomized, open, single-center clinical assay, whose 140 participants were recruited."
SPAN = "This is a prospective, randomized, open, single-center clinical assay"
KEY = ("colchicine-postop-af", "27223641")


def _setup(monkeypatch, how="REGEX_ON_FULLTEXT", sha=None):
    monkeypatch.setattr(gt, "_AUDIT", {KEY: {"class": "INSUFFICIENT_RECORD", "subclass": "BLINDING_NOT_STATED"}})
    sha = sha or hashlib.sha256(FT.encode("utf-8")).hexdigest()
    monkeypatch.setattr(gt, "_FT", {KEY: {"class_after": "TRUE_SCOPE_DIFFERENCE", "subclass_after": "OPEN_LABEL_STATED",
                                          "how": how, "span": {"field": "fulltext", "text": SPAN},
                                          "fulltext_sha256": sha, "fulltext": "PMC_OA"}})
    monkeypatch.setattr(cfm, "pmc_fulltext_cached", lambda pmid, offline=True: FT)
    return sha


def test_a_full_text_resolution_names_the_exclusion(monkeypatch):
    sha = _setup(monkeypatch)
    assert gt.exclusion_audit_class(*KEY)[0] == "TRUE_SCOPE_DIFFERENCE"
    got = gt.exclusion_audit_span(*KEY)
    assert got["text"] == SPAN and got["field"] == "fulltext" and got["fulltext_sha256"] == sha
    assert gt.span_is_verbatim(KEY[0], KEY[1], got)


def test_a_different_full_text_never_verifies_the_span(monkeypatch):
    _setup(monkeypatch, sha="0" * 64)
    assert not gt.span_is_verbatim(KEY[0], KEY[1], gt.exclusion_audit_span(*KEY))


def test_a_model_readers_verdict_stays_a_proposal(monkeypatch):
    _setup(monkeypatch, how="RECORDED_READER")
    assert gt.exclusion_audit_class(*KEY)[0] == "INSUFFICIENT_RECORD"
    assert gt.exclusion_audit_span(*KEY) is None
