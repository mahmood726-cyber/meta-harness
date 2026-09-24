"""Delegated bulk acceptance (reproducible_ai/delegated.py) is a distinct status and never a human countersignature."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

from harness import result_changes
from reproducible_ai import delegated, model_source as ms

ROOT = Path(__file__).resolve().parents[1]
ACC = ROOT / "registry" / "model_proposals" / "screening.delegated_acceptance.json"


@pytest.fixture(scope="module")
def world():
    spec = importlib.util.spec_from_file_location("_rda", ROOT / "scripts" / "record_delegated_acceptance.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    queue, records, held = mod.inputs("screening")
    return queue, records, held, delegated.load(ACC)


def _first(queue, records, held, basis):
    for e in queue["items"]:
        ok, why = delegated.classify(e, records.get(e.get("record_id")), held.get(e["item_id"]))
        if ok and why == basis:
            return e
    raise AssertionError(f"no item with basis {basis}")


def test_the_record_says_what_it_is(world):
    *_, acc = world
    assert acc["status"] == "DELEGATED_BULK_ACCEPTANCE" and acc["authorised_by"] == "Mahmood Ahmad"
    assert acc["instruction_text"] == "yes record as bulk acceptance"
    assert acc["how_it_reached_the_reviewer"] == "Dispatch chat relay; blanket instruction; no item-by-item review"
    assert acc["display"] == "AI-proposed, accepted under delegated authority without individual human review"
    assert acc["is_human_countersignature"] is False and acc["satisfies_countersignature_predicates"] is False


def test_every_item_is_accounted_for_exactly_once(world):
    queue, *_, acc = world
    ids = [a["item_id"] for a in acc["accepted"]] + [x["item_id"] for x in acc["not_accepted"]]
    assert sorted(ids) == sorted(e["item_id"] for e in queue["items"]) and len(ids) == len(set(ids)) == acc["N"]


def test_an_accepted_item_is_still_unsigned_to_every_countersignature_predicate(world):
    queue, records, held, acc = world
    accepted = {a["item_id"] for a in acc["accepted"]}
    for e in queue["items"]:
        if e["item_id"] not in accepted:
            continue
        rec = records[e["record_id"]]
        assert ms.status_of(e, rec, held[e["item_id"]]) == "PROPOSED"
        assert any(p.startswith("COUNTERSIGNATURE:") for p in ms.gate_problems(e, rec, held[e["item_id"]]))
        assert e.get("reviewer_countersignature", {}).get("state") == "OPEN"
        notice = {"reviewer_countersignature": e.get("reviewer_countersignature"), "conclusion_changed": "X"}
        assert result_changes.signature_problem(notice, ms.render_proposal_block(e, rec))


def test_building_the_record_never_edits_the_queue(world):
    queue, records, held, _ = world
    before = copy.deepcopy(queue)
    delegated.build("screening", queue, records, held)
    assert queue == before


def test_unstable_cannot_tell_unmeasured_and_refused_are_not_accepted(world):
    queue, records, held, _ = world
    e = _first(queue, records, held, "STABLE_ELIGIBLE")
    rec, h = records[e["record_id"]], held[e["item_id"]]
    unstable = copy.deepcopy(e)
    unstable["reask"]["same_derived_decision"] = False
    assert delegated.classify(unstable, rec, h)[1].startswith("UNSTABLE_ON_REASK")
    unmeasured = copy.deepcopy(e)
    unmeasured.pop("reask")
    assert delegated.classify(unmeasured, rec, h)[1].startswith("STABILITY_NOT_MEASURED")
    assert delegated.classify(e, rec, h + " ")[1].startswith("GATE_REFUSED")        # held text mismatch
    cannot = [x for x in acc_not(world) if x["reason"].startswith("NO_DECISION_TO_ACCEPT")]
    assert cannot and all("CANNOT_TELL" in x["reason"] for x in cannot)


def acc_not(world):
    return world[3]["not_accepted"]


def test_a_changed_proposal_makes_its_acceptance_stale(world):
    queue, records, held, acc = world
    assert delegated.stale(acc, queue, records) == []
    q2 = copy.deepcopy(queue)
    target = acc["accepted"][0]["item_id"]
    for e in q2["items"]:
        if e["item_id"] == target:
            e["verification"]["model_decision"] = "INELIGIBLE" if e["verification"]["model_decision"] == "ELIGIBLE" else "ELIGIBLE"
    assert any(s.startswith(target) for s in delegated.stale(acc, q2, records))


def test_the_delegation_written_as_a_signature_is_still_refused(world):
    # plant #20: result_changes.signature_problem accepts a well-formed SEEN_AND_SIGNED whose basis is a relay; the
    # blanket delegation copied into reviewer_countersignature would therefore have passed as a human signature
    queue, records, held, acc = world
    e = copy.deepcopy(_first(queue, records, held, "STABLE_INELIGIBLE"))
    rec = records[e["record_id"]]
    e["reviewer_countersignature"] = {
        "state": "SEEN_AND_SIGNED", "by": "Mahmood Ahmad", "when_utc": "2026-09-24T19:00:00Z",
        "rendered_sha256": result_changes.rendered_sha256(ms.render_proposal_block(e, rec)),
        "how_it_reached_the_reviewer": delegated.HOW}
    probs = ms.gate_problems(e, rec, held[e["item_id"]])
    assert any(p.startswith("DELEGATED_IS_NOT_A_SIGNATURE") for p in probs), probs
    assert ms.status_of(e, rec, held[e["item_id"]]) == "PROPOSED"
