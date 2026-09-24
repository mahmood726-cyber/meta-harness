"""Delegated bulk acceptance of model proposals -- a DISTINCT status, never a human countersignature.

Mahmood asked for every screening proposal to be signed in his name; that was declined (a signature the system
applies to its own result is a password, not a check), and a truthful record of bulk delegation was offered instead.
His answer, relayed through Dispatch on 2026-09-24: "yes record as bulk acceptance".

What this module guarantees:
  * the acceptance lives in its OWN file (registry/model_proposals/<task>.delegated_acceptance.json); it never writes
    `reviewer_countersignature`, so model_source.gate_problems / status_of and harness.result_changes.signature_problem
    still see every item as unsigned -- no predicate that requires a human countersignature is satisfied by it;
  * it names only items that have ONE well-defined, stable proposal that passes the deterministic gate (everything but
    the countersignature): a recorded re-ask of the identical prompt reached the same decision, and that decision is a
    decision (ELIGIBLE / INELIGIBLE), not "cannot tell";
  * each accepted item is bound to its proposal (record id, response sha256, rendered-block sha256), so a changed
    proposal is reported STALE, never silently carried;
  * everything not accepted is listed with its reason (n of N both ways).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reproducible_ai import model_source as ms

STATUS = "DELEGATED_BULK_ACCEPTANCE"
DISPLAY = "AI-proposed, accepted under delegated authority without individual human review"
AUTHORISED_BY = "Mahmood Ahmad"
DATE = "2026-09-24"
HOW = "Dispatch chat relay; blanket instruction; no item-by-item review"
INSTRUCTION = "yes record as bulk acceptance"
CONTEXT = ('Reply to the offer of a truthful bulk-delegated record, made after Mahmood asked for the proposals to be '
           '"sign all for me" and signing in his name was declined.')
SCOPE_RULE = ("accepted: the proposal passes the deterministic gate except for the human countersignature, a recorded "
              "re-ask of the identical prompt reached the same derived decision, and that decision is ELIGIBLE or "
              "INELIGIBLE. Not accepted: unstable on re-ask; never re-asked; gate refused; the model could not tell "
              "(a stable 'cannot tell' is not a decision, so there is nothing to accept -- the item stays UNRESOLVED).")


def _gate_without_countersignature(entry: dict, record: dict, held_text: str) -> list[str]:
    return [p for p in ms.gate_problems(entry, record, held_text) if not p.startswith("COUNTERSIGNATURE:")]


def classify(entry: dict, record: dict | None, held_text: str | None) -> tuple[bool, str]:
    """(accepted?, reason). Pure: depends only on the queue entry, its record and its held text."""
    if entry.get("status") != "PROPOSED" or record is None or held_text is None:
        return False, f"NO_PROPOSAL: {entry.get('status') or entry.get('state')}"
    probs = _gate_without_countersignature(entry, record, held_text)
    if probs:
        return False, "GATE_REFUSED: " + "; ".join(probs)
    rq = entry.get("reask")
    if not isinstance(rq, dict) or not rq.get("records"):
        return False, "STABILITY_NOT_MEASURED: no recorded re-ask of the identical prompt"
    if not rq.get("same_derived_decision"):
        return False, f"UNSTABLE_ON_REASK: decisions {rq.get('decisions')}"
    decision = (entry.get("verification") or {}).get("model_decision")
    if decision not in ("ELIGIBLE", "INELIGIBLE"):
        return False, f"NO_DECISION_TO_ACCEPT: the model's stable answer is {decision}"
    return True, f"STABLE_{decision}"


def binding(entry: dict, record: dict) -> dict:
    return {"item_id": entry["item_id"], "record_id": entry["record_id"],
            "response_sha256": entry.get("response_sha256"),
            "proposal_sha256": __import__("harness.result_changes", fromlist=["x"]).rendered_sha256(
                ms.render_proposal_block(entry, record)),
            "accepted_decision": (entry.get("verification") or {}).get("model_decision"),
            "rule_decision": entry.get("rule_decision"),
            "reask_records": (entry.get("reask") or {}).get("records")}


def build(task: str, queue: dict, records: dict[str, dict], held: dict[str, str]) -> dict:
    accepted, not_accepted = [], []
    for e in queue["items"]:
        rec = records.get(e.get("record_id"))
        ok, why = classify(e, rec, held.get(e["item_id"]))
        if ok:
            accepted.append({**binding(e, rec), "basis": why})
        else:
            not_accepted.append({"item_id": e["item_id"], "state": "UNRESOLVED", "reason": why})
    n = len(queue["items"])
    return {"status": STATUS, "display": DISPLAY, "task": task,
            "authorised_by": AUTHORISED_BY, "date": DATE, "how_it_reached_the_reviewer": HOW,
            "instruction_text": INSTRUCTION, "instruction_context": CONTEXT,
            "is_human_countersignature": False,
            "satisfies_countersignature_predicates": False,
            "scope_rule": SCOPE_RULE,
            "N": n, "accepted_n_of_N": f"{len(accepted)} of {n}", "not_accepted_n_of_N": f"{len(not_accepted)} of {n}",
            "accepted": sorted(accepted, key=lambda a: a["item_id"]),
            "not_accepted": sorted(not_accepted, key=lambda a: a["item_id"])}


def stale(acceptance: dict, queue: dict, records: dict[str, dict]) -> list[str]:
    """Accepted items whose proposal is no longer the one accepted (any field of the binding differs)."""
    by = {e["item_id"]: e for e in queue["items"]}
    out = []
    for a in acceptance.get("accepted") or []:
        e = by.get(a["item_id"])
        rec = records.get((e or {}).get("record_id"))
        if e is None or rec is None:
            out.append(f"{a['item_id']}: no longer in the queue")
            continue
        now = binding(e, rec)
        diff = [k for k in ("record_id", "response_sha256", "proposal_sha256", "accepted_decision") if now[k] != a.get(k)]
        if diff:
            out.append(f"{a['item_id']}: {diff} changed since the acceptance")
    return out


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
