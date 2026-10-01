"""V1.1: the measure guard runs INSIDE check_pool_contract, so a refused pool is never COMPUTED there either.

The parked POOL work computed its authoritative pool inside check_pool_contract (`got = pool(derived)`) and only afterwards let
run() consult pool_measure_guard -- the refusal then discarded a number already derived from log(effect). Its own merge note said
so: "it does not yet preserve 'not COMPUTED at all'. Closing that needs the guard inside check_pool_contract."

These plants call the real contract on the served GLP-1 objects with pool() replaced by a sentinel that raises. Each fires on the
parked contract (the sentinel is reached, or the contract takes no guard evidence at all) and passes once the guard is inside it.
"""
import json
from pathlib import Path

import pytest

from scripts import verify_bundle as verifier

ROOT = Path(__file__).resolve().parents[1]
SLUG = "glp1-ra-mace-t2d"


@pytest.fixture
def objects():
    # the same real, certified objects tests/test_pool_binding.py uses
    store = verifier.Store(str(ROOT / "docs"), None)
    return (store.json(f"reviews/{SLUG}/review.json"), store.json(f"reviews/{SLUG}/BUNDLE.json"),
            store.json(f"cache/{SLUG}/records.json"))


class Computed(AssertionError):
    pass


def _sentinel(*_a, **_k):
    raise Computed("pool() was reached for a pool the measure guard refuses")


def _measure_rows(review, measure_of):
    """Guard evidence in the verifier's shape (report['ordered_contrasts']), one row per certified primary trial."""
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    return {t["id"].removeprefix("PMID "): {"measure": measure_of(i), "p10": []} for i, t in enumerate(primary["trials"])}


@pytest.mark.parametrize("case,measure_of,code", [
    ("mixed_measures", lambda i: "OR" if i == 0 else "HR", "POOL_MEASURE_MIXED"),
    ("unidentified_measure", lambda i: None if i == 0 else "HR", "POOL_MEASURE_UNIDENTIFIED"),
    ("no_verified_rows", None, "POOL_MEASURE_UNIDENTIFIED"),
])
def test_a_refused_measure_is_never_computed_inside_the_contract(objects, monkeypatch, case, measure_of, code):
    review, bundle, records = objects
    rows = {} if measure_of is None else _measure_rows(review, measure_of)
    monkeypatch.setattr(verifier, "pool", _sentinel)
    contract, errors = verifier.check_pool_contract(review, json.loads(json.dumps(bundle)), records, measure_rows=rows)
    assert contract["recomputed"] is None
    assert contract["pool_measure_guard"]["refused"] is True
    assert any(e.startswith(code) for e in errors), errors
    assert contract["binding_ok"] is False and contract["reproduced_to_1e-9"] is False


def test_an_identified_single_measure_still_pools_through_the_guard(objects):
    # the control: the guard must not refuse everything -- the served HR rows pool and reproduce the certified result
    review, bundle, records = objects
    contract, errors = verifier.check_pool_contract(review, json.loads(json.dumps(bundle)), records,
                                                    measure_rows=_measure_rows(review, lambda i: "HR"))
    assert contract["recomputed"] is not None and contract["pool_measure_guard"]["refused"] is False
    assert contract["certified_result_agrees"] is True, errors
    assert contract["pool_measure_guard"]["measure_basis"].startswith("VERIFIED_ORDERED_CONTRAST")


def test_the_verifiers_contrast_value_equals_the_producers(objects):
    # the served verifier carries its own copy of contrast_order.contrast_value (it imports nothing from the producer): pin parity
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import contrast_order
    _, bundle, _ = objects
    ocs = [((r.get("analysis_identity") or {}).get("comparator_direction") or {}).get("ordered_contrast") or {}
           for r in bundle["verification_rows"]]
    flipped = [dict(o, numerator_side="REFERENCE") for o in ocs if o]
    unordered = [dict(o, state="UNORDERED") for o in ocs if o]
    cases = [o for o in ocs if o] + flipped + unordered
    assert len(cases) >= 3 * 8
    assert [verifier._served_contrast_value(o) for o in cases] == [contrast_order.contrast_value(o) for o in cases]


def test_pool_contrast_is_checked_on_the_typed_contrast_not_a_prose_string(objects):
    # the parked contract required a prose string lane OC's producer no longer writes, and refused all 8 correct served rows;
    # the typed check passes them and still refuses a reference-numerator (reciprocal) contrast
    review, bundle, records = objects
    _, errors = verifier.check_pool_contract(review, json.loads(json.dumps(bundle)), records)
    assert not [e for e in errors if e.startswith("POOL_CONTRAST_MISMATCH")], errors
    flipped = json.loads(json.dumps(bundle))
    cd = flipped["verification_rows"][0]["analysis_identity"]["comparator_direction"]
    cd["ordered_contrast"]["numerator_side"] = "REFERENCE"
    _, errors = verifier.check_pool_contract(review, flipped, records)
    assert any(e.startswith("POOL_CONTRAST_MISMATCH") for e in errors), errors


def test_the_producer_path_is_guarded_and_names_its_weaker_basis(objects, monkeypatch):
    # a producer has no verifier rows: the guard runs over each certified row's declared scale and SAYS so
    review, bundle, records = objects
    contract, _ = verifier.check_pool_contract(review, json.loads(json.dumps(bundle)), records)
    assert contract["pool_measure_guard"]["measure_basis"].startswith("CERTIFIED_ROW_SCALE")
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    primary["trials"][0]["scale"] = "OR"                  # one certified row declares another ratio measure
    monkeypatch.setattr(verifier, "pool", _sentinel)
    contract, errors = verifier.check_pool_contract(review, json.loads(json.dumps(bundle)), records)
    assert contract["recomputed"] is None and any(e.startswith("POOL_MEASURE_MIXED") for e in errors), errors
