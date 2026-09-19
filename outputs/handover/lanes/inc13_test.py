"""Mahmood's review of the served glp1 page (98726cc1, 19 Sep 2026), item 5: PIONEER-6's gastrointestinal-harms obligation
was closed on a typed refusal from the abstract ("Typed refusal resolves the extraction obligation; other routes remain
unverified") while the held full text, supplement, registry results and regulatory routes -- each permitted by B-prime --
were NOT_CHECKED. Requirement: the obligation is a state on the source ladder, OPEN while any permitted route is unchecked,
RESOLVED only by located outcome-specific evidence or by exhausting every route. Keeping the harms synthesis suppressed is
correct and stays. Plant: on bf2af50d the ladder carries the closing sentence and no obligation state.
"""
import json
import pathlib

from harness import harms

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _ladder_for(slug, pmid, outcome_name):
    review = json.loads((ROOT / "docs/reviews" / slug / "review.json").read_text(encoding="utf-8"))
    for outcome in review["outcomes"]:
        if outcome.get("kind") == "harm" and outcome_name in str(outcome.get("name")):
            for item in (outcome.get("result") or {}).get("harm_reporting_trials") or []:
                if str(item.get("id")) == pmid:
                    return item.get("source_ladder") or []
    return None


def test_pioneer6_gi_harms_obligation_is_open():
    ladder = _ladder_for("glp1-ra-mace-t2d", "31185157", "Gastrointestinal")
    assert ladder, "fixture assumption: PIONEER-6 has a GI-harms ladder"
    states = {r.get("rung"): r.get("state") for r in ladder}
    assert states.get("obligation") == "OPEN", states
    assert not any("resolves the extraction obligation" in str(r.get("obligation")) for r in ladder)
    assert states.get("held full text") == "NOT_CHECKED"


def test_obligation_state_is_derived_from_the_rungs():
    ladder = harms._ladder("1", {"1": {"abstract": "x"}}, {}, {"document_ref": "cache/none.json", "source_span": "y"})
    assert next(r for r in ladder if r["rung"] == "obligation")["state"] == "OPEN"
    ladder = harms._ladder("1", {"1": {"abstract": "x"}}, {"1": "full text"}, {})
    assert next(r for r in ladder if r["rung"] == "obligation")["state"] == "OPEN"  # supplement/registry rung is never checked here


def test_every_typed_refusal_ladder_carries_an_obligation_state():
    bad = []
    for path in sorted((ROOT / "docs/reviews").glob("*/review.json")):
        review = json.loads(path.read_text(encoding="utf-8"))
        for outcome in review["outcomes"]:
            if outcome.get("kind") != "harm":
                continue
            for item in (outcome.get("result") or {}).get("harm_reporting_trials") or []:
                ladder = item.get("source_ladder") or []
                if ladder and not any(r.get("rung") == "obligation" for r in ladder):
                    bad.append((path.parent.name, item.get("id")))
    assert bad == []
