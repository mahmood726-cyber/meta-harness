"""RAI-D7 / RAI-C9: a DELEGATED_BULK_ACCEPTANCE can never satisfy the SERVED-number gate's human-countersignature
predicate (harness.result_changes.signature_problem, called by harness/gate.py for every result-change notice), and the
refusal is decided by the record TYPE, not by matching phrases."""
from __future__ import annotations

import json
from pathlib import Path

from harness import result_changes as rc
from reproducible_ai import delegated

ROOT = Path(__file__).resolve().parents[1]
BLOCK = "<div class='notice'>Major vascular events: HR 0.68 (k = 2) -> no pooled estimate (k = 0)</div>"
ACC = json.loads((ROOT / "registry" / "model_proposals" / "screening.delegated_acceptance.json").read_text(encoding="utf-8"))


def _notice(sig: dict, conclusion_changed=True) -> dict:
    return {"reviewer_countersignature": sig, "conclusion_changed": conclusion_changed}


def _signed(**extra) -> dict:
    base = {"state": "SEEN_AND_SIGNED", "by": "Mahmood Ahmad", "when_utc": "2026-09-24T19:00:00Z",
            "rendered_sha256": rc.rendered_sha256(BLOCK)}
    base.update(extra)
    return base


def test_a_delegated_item_dressed_as_a_signature_is_refused_by_the_served_gate():
    # plant (fired before the fix: signature_problem returned None -- the notice would have published)
    item = dict(ACC["accepted"][0])
    sig = _signed(how_it_reached_the_reviewer=ACC["how_it_reached_the_reviewer"], **item)
    p = rc.signature_problem(_notice(sig), BLOCK)
    assert p and p.startswith("DELEGATED_IS_NOT_A_SIGNATURE"), p


def test_the_delegations_own_basis_is_refused_whatever_else_the_signature_says():
    # plant (fired before the fix): no delegated field copied, only the delegation's recorded basis
    p = rc.signature_problem(_notice(_signed(how_it_reached_the_reviewer=ACC["how_it_reached_the_reviewer"])), BLOCK)
    assert p and p.startswith("DELEGATED_IS_NOT_A_SIGNATURE"), p


def test_the_delegated_status_is_named_as_a_delegation():
    p = rc.signature_problem(_notice({"state": rc.DELEGATED_STATUS, "by": "Mahmood Ahmad"}), BLOCK)
    assert p and p.startswith("DELEGATED_IS_NOT_A_SIGNATURE"), p
    assert rc.DELEGATED_STATUS not in rc.SIGNATURE_STATES and rc.DELEGATED_STATUS not in rc.SIGNED_STATES


def test_the_whole_record_presented_as_a_signature_is_refused():
    p = rc.signature_problem(_notice(dict(ACC)), BLOCK)
    assert p and p.startswith("DELEGATED_IS_NOT_A_SIGNATURE"), p


def test_the_type_is_defined_once_in_the_served_gate():
    assert delegated.STATUS is rc.DELEGATED_STATUS
    assert delegated.HOW == rc.DELEGATED_BASIS
    assert set(rc.DELEGATION_FIELDS) <= set(ACC) | set(ACC["accepted"][0])


def test_no_phrase_list_decides_it():
    src = (ROOT / "reproducible_ai" / "model_source.py").read_text(encoding="utf-8")
    assert "DELEGATION_TELLS" not in src          # RAI-C9: the six-phrase deny list is gone


def test_every_real_served_signature_still_publishes():
    notices = json.loads((ROOT / "docs" / "result_changes.json").read_text(encoding="utf-8"))["notices"]
    signed = [n for n in notices if (n.get("reviewer_countersignature") or {}).get("state") in rc.SIGNED_STATES]
    assert signed
    for n in signed:
        assert rc._delegation_problem(n["reviewer_countersignature"], n) is None, n.get("slug")
