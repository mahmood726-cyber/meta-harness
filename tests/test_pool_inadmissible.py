"""V1.0.1 (auditor, 2026-09-26): the pool is formed only from rows that JUST PASSED ADMISSION. A pooled row the verifier did not
admit refuses the pool -- POOL_CONTAINS_INADMISSIBLE_ROW -- with membership unchanged, and nothing is computed; it is never
silently dropped. No trial is special-cased: HARMONY is admissible or not on its evidence (Mahmood's D04 decides whether abstract
text may stand at registry rank). Plants fired on the pre-fix contract (it took no admission at all)."""
import json
from pathlib import Path

import pytest

from scripts import verify_bundle as verifier

ROOT = Path(__file__).resolve().parents[1]
SLUG = "glp1-ra-mace-t2d"


@pytest.fixture
def objects():
    store = verifier.Store(str(ROOT / "docs"), None)
    return (store.json(f"reviews/{SLUG}/review.json"), store.json(f"reviews/{SLUG}/BUNDLE.json"),
            store.json(f"cache/{SLUG}/records.json"))


def _members(review):
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    return [t["id"].removeprefix("PMID ") for t in primary["trials"]]


def _rows(review, measure="HR"):
    return {pid: {"measure": measure, "p10": []} for pid in _members(review)}


class Computed(AssertionError):
    pass


def test_every_member_admitted_pools(objects):
    review, bundle, records = objects
    contract, errors = verifier.check_pool_contract(review, json.loads(json.dumps(bundle)), records,
                                                    measure_rows=_rows(review), admitted=set(_members(review)))
    assert contract["recomputed"] is not None
    assert not [e for e in errors if e.startswith("POOL_CONTAINS_INADMISSIBLE_ROW")], errors


def test_one_member_marked_inadmissible_refuses_the_pool_and_computes_nothing(objects, monkeypatch):
    review, bundle, records = objects
    members = _members(review)
    marked = members[2]                                   # LEADER; membership itself is unchanged
    monkeypatch.setattr(verifier, "pool", lambda *a, **k: (_ for _ in ()).throw(Computed("pooled an inadmissible row")))
    contract, errors = verifier.check_pool_contract(review, json.loads(json.dumps(bundle)), records,
                                                    measure_rows=_rows(review), admitted=set(members) - {marked})
    assert [e for e in errors if e.startswith(f"POOL_CONTAINS_INADMISSIBLE_ROW PMID {marked}")], errors
    assert contract["recomputed"] is None and contract["binding_ok"] is False
    assert sorted(contract["selected_set"]["members"]) == sorted(f"PMID {m}" for m in members)   # not dropped


def test_restoring_admission_restores_the_pool(objects):
    review, bundle, records = objects
    contract, errors = verifier.check_pool_contract(review, json.loads(json.dumps(bundle)), records,
                                                    measure_rows=_rows(review), admitted=set(_members(review)))
    assert contract["recomputed"] is not None


def test_the_code_is_an_input_linkage_failure():
    assert "POOL_CONTAINS_INADMISSIBLE_ROW x".startswith(verifier.LINKAGE_CODES)
