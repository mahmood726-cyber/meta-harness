"""scripts/countersign_model_proposal.py routes and refuses exactly as the gate does.

Plant (observed 2026-09-24): the tool asked only whether the VERDICT agrees, so an agreement flagged unstable on
re-ask (LEADER, 27295427) was offered for a batch signature the gate would then refuse -- and the "individual" packet
said 150 where the gate's count is 151. The tool must use the gate's own predicate. Runs on a temp copy of the queue;
never signs anything in the repo.
"""
from __future__ import annotations

import importlib.util
import json
import types
from pathlib import Path

from reproducible_ai import model_source as ms

ROOT = Path(__file__).resolve().parents[1]


def _tool():
    spec = importlib.util.spec_from_file_location("_cs", ROOT / "scripts" / "countersign_model_proposal.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_tools_routing_is_the_gates_predicate():
    doc = json.loads((ROOT / ms.PROPOSAL_DIR / "screening.json").read_text(encoding="utf-8"))
    flagged = [e for e in doc["items"] if "verification" in e and e.get("individual_signature_required")
               and not ms.needs_individual_signature(e["verification"])]
    tool = _tool()
    for e in flagged:                      # verdict agrees, re-ask did not reproduce: individual, per the gate
        assert ms.individual_required(e, e["verification"])
        assert tool.routes_individual(e)


def test_sign_batch_refuses_an_unstable_agreement(tmp_path, monkeypatch):
    tool = _tool()
    doc = json.loads((ROOT / ms.PROPOSAL_DIR / "estimand.json").read_text(encoding="utf-8"))
    e = next(x for x in doc["items"] if "verification" in x and not ms.individual_required(x, x["verification"]))
    e["individual_signature_required"] = True                  # planted: the re-ask did not reproduce
    a = types.SimpleNamespace(task="estimand", by="Reviewer Fixture", basis="fixture", when="2026-09-24T09:00:00Z")
    why = tool._sign_one(doc["items"], e, a, "B1")
    assert why and "batch" in why
    assert e["reviewer_countersignature"] == {"state": "OPEN"}
