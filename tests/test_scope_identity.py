from __future__ import annotations
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # tests/ on the path for _contracts

import json
import subprocess
from pathlib import Path

from harness import scope_identity

ROOT = Path(__file__).resolve().parents[1]
BASE = "ad5e7c66"


def _git_text(path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{BASE}:{path}"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _git_json(path: str) -> dict:
    return json.loads(_git_text(path))


def _current_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _current_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_doac_prefixed_known_item_scope_mismatch_fires_on_unsafe_text():
    review = _git_json("docs/reviews/doac-vte-recurrence/review.json")
    html = _git_text("docs/reviews/doac-vte-recurrence/index.html")

    assert review["search"]["retrieval_class"]["class"] == "KNOWN_ITEM_RETRIEVAL"
    assert "6 reported this outcome with an extractable number and were pooled" in html
    assert scope_identity.QUALIFIED_SCOPE_PHRASE not in html

    violations = scope_identity.check_scope_identity(review, html, root=ROOT)
    assert [v["code"] for v in violations] == [scope_identity.SCOPE_MISMATCH]


def test_doac_rebuilt_scope_mismatch_is_qualified_and_passes_check():
    review = _current_json("docs/reviews/doac-vte-recurrence/review.json")
    html = _current_text("docs/reviews/doac-vte-recurrence/index.html")

    assert review["scope_identity"]["verdict"] == scope_identity.SCOPE_MISMATCH
    assert "of the pre-identified set met eligibility" in html
    assert scope_identity.QUALIFIED_SCOPE_PHRASE in html
    assert scope_identity.check_scope_identity(review, html, root=ROOT) == []


def test_noac_prefixed_scope_mismatch_and_posthoc_amendment_fire():
    review = _git_json("docs/reviews/noac-vs-warfarin-af-stroke/review.json")
    html = _git_text("docs/reviews/noac-vs-warfarin-af-stroke/index.html")

    assert review["search"]["retrieval_class"]["class"] == "KNOWN_ITEM_RETRIEVAL"
    assert scope_identity.QUALIFIED_SCOPE_PHRASE not in html
    assert [v["code"] for v in scope_identity.check_scope_identity(review, html, root=ROOT)] == [
        scope_identity.SCOPE_MISMATCH
    ]

    sweep = scope_identity.posthoc_amendment_sweep(ROOT)
    row = next(r for r in sweep["amendments"] if r["slug"] == "noac-vs-warfarin-af-stroke")
    assert row["type"] == "POST_HOC_AMENDMENT"
    assert row["required_render"] == scope_identity.NOAC_REQUIRED_RENDER
    assert row["all_dose_alternative"]["status"] == "NOT_COMPUTED_SOURCE_INCOMPLETE"
    from _contracts import partition
    current = json.loads((ROOT / "docs/reviews/noac-vs-warfarin-af-stroke/review.json").read_text(encoding="utf-8"))
    primary = next(o for o in current["outcomes"] if o.get("primary"))
    pooled, _ = partition(ROOT, "noac-vs-warfarin-af-stroke", primary)
    assert row["standard_dose_result"]["k"] == primary["result"].get("k")
    if not pooled:
        assert primary["result"].get("estimate") is None and primary["result"].get("reason")


def test_noac_rebuilt_scope_mismatch_is_qualified_and_passes_check():
    review = _current_json("docs/reviews/noac-vs-warfarin-af-stroke/review.json")
    html = _current_text("docs/reviews/noac-vs-warfarin-af-stroke/index.html")

    assert review["scope_identity"]["verdict"] == scope_identity.SCOPE_MISMATCH
    assert "of the pre-identified set met eligibility" in html
    assert scope_identity.QUALIFIED_SCOPE_PHRASE in html
    assert scope_identity.check_scope_identity(review, html, root=ROOT) == []


def test_synthetic_concept_search_open_eligibility_has_no_violation():
    config = {
        "include": {
            "population_any": ["condition"],
            "intervention_any": ["drug"],
            "comparator_any": ["placebo"],
        }
    }
    review = {
        "slug": "synthetic-concept",
        "protocol": {"eligibility": "P/I/C/design open eligibility"},
        "search": {
            "retrieval_class": {"class": "CONCEPT_SEARCH", "label": "concept"},
            "sources": [{"name": "PubMed", "queries": ["condition AND drug"]}],
        },
    }
    ledger = {
        "sources": [
            {
                "kind": "PUBMED_CONCEPT_QUERY",
                "state": "RAN_OK",
                "query": "condition AND drug",
                "discovery_capable": True,
            }
        ]
    }

    scope = scope_identity.assess(
        config=config,
        protocol_text="# Protocol\nP/I/C/design only.",
        search=review["search"],
        ledger=ledger,
        review=review,
        slug=review["slug"],
    )
    assert scope["verdict"] == scope_identity.OK
    assert scope_identity.check_scope_identity({**review, "scope_identity": scope}, "<html></html>", root=ROOT) == []


def test_hand_written_keyword_pages_are_separate_unregistered_scope_rows():
    rows = scope_identity.sweep(ROOT)["pages"]
    hand = {
        row["slug"]: row
        for row in rows
        if row["search_scope"]["retrieval_class"] == scope_identity.HAND_WRITTEN_RETRIEVAL_CLASS
    }

    assert set(hand) == {
        "colchicine-postop-af",
        "colchicine-recurrent-pericarditis",
        "corticosteroids-cap-mortality",
        "probiotics-aad-prevention",
    }
    assert {row["verdict"] for row in hand.values()} == {scope_identity.HAND_WRITTEN_SCOPE}
    assert all("not a pre-identified PMID/title set" in row["reason"] for row in hand.values())

    sweep = scope_identity.sweep(ROOT)
    assert sweep["n_pages"] == 32
    assert sweep["n_scope_mismatch"] == 28
