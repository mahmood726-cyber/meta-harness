"""Synthetic held documents keep binding decisions independent of network and readers."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_regulator_fill as rf
import g1_regulatory_source as rs

URL = "https://www.nice.org.uk/guidance/synthetic/documents/committee-papers"
CFG = {"primary_outcome": {"estimand": "HR", "keywords": ["MACE"]}}
TRIAL = {"label": "TRIALX", "pmid": None, "ncts": []}


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    import socket

    def blocked(*a, **kw):
        pytest.fail("network or reader call in synthetic regulator tests")
    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket, "getaddrinfo", blocked)
    monkeypatch.setattr(rf.rf, "_call", blocked)


def evidence(monkeypatch, text):
    rec = {"agency": "NICE", "licence": "NICE_NOTICE_OF_RIGHTS", "doc_sha256": "synthetic",
           "text_sha256": rs.text_sha256(text)}
    held = {URL: {"text": text, "names": ["TRIALX"], "record": rec}}
    monkeypatch.setattr(rs, "regulatory_evidence", lambda *a: ([], held))


def test_bound_ruling_admits_and_missing_ruling_holds(monkeypatch):
    evidence(monkeypatch, "TRIALX MACE HR 0.52 (95% CI 0.31 to 0.90)")
    ruling = dict.fromkeys(("arm", "outcome", "timepoint", "population", "analysis_set", "ruled_by", "ruled_on", "reason"),
                           "synthetic")
    ruling["decision"] = "BOUND"
    calls = []
    monkeypatch.setattr(rs, "binding_for", lambda *a: calls.append(a) or ruling)
    bound = rf.run_trial("x", "NICE", CFG, None, TRIAL)
    assert bound["stage"] == "TYPED" and bound["verdict"] == "ADMITTED"
    assert bound["decision"] == "ADMITTED_DETERMINISTIC_BOUND" and bound["admitted"]["binding"] == ruling
    assert calls == [("x", "TRIALX", URL, bound["admitted"]["text_sha256"])]
    monkeypatch.setattr(rs, "binding_for", lambda *a: None)
    held = rf.run_trial("x", "NICE", CFG, None, TRIAL)
    assert held["stage"] == "TYPED" and held["verdict"] == "NOT_ADMITTED"
    assert held["decision"] == "TYPED_HELD_PENDING_BINDING_RULING" and "admitted" not in held
    assert held["candidate"] == {k: v for k, v in bound["admitted"].items() if k != "binding"}
    monkeypatch.setattr(rs, "binding_for", lambda *a: dict(ruling, decision="NOT_BOUND", reason="wrong population"))
    refused = rf.run_trial("x", "NICE", CFG, None, TRIAL)
    assert refused["decision"] == "TYPED_NOT_BOUND:wrong population" and refused["verdict"] == "NOT_ADMITTED"
    assert refused["candidate"] == held["candidate"]


def test_typed_only_windows_relabelled(monkeypatch):
    evidence(monkeypatch, "TRIALX MACE was discussed without an effect.")
    result = rf.run_trial("x", "NICE", CFG, None, TRIAL)
    assert result["decision"] == "NAMED_TYPED_ONLY_NO_ROW_PARSED" and result["typed_only_windows"] == 1
    assert result["verdict"] == "NOT_ADMITTED" and result["stage"] == "NAMED"
    evidence(monkeypatch, "TRIALX unrelated discussion.")
    assert rf.run_trial("x", "NICE", CFG, None, TRIAL)["decision"] == "NAMED_NO_WINDOW_WITH_OUTCOME_TERMS"
