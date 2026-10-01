"""Checks for the audit harness, not repairs to the audited system."""
import copy
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SPEC = importlib.util.spec_from_file_location("f6_audit", ROOT / "scripts/f6_acceptance.py")
f6 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(f6)


def test_rotated_ids_preserve_arithmetic_but_change_linkage():
    from scripts.verify_bundle import pool
    selected = next(o for o in f6.read(f6.REVIEW / "review.json")["outcomes"] if o.get("primary"))["trials"]
    inputs = [{k: t[k] for k in ("id", "effect", "ci_low", "ci_high")} for t in selected]
    changed = copy.deepcopy(inputs)
    for row, identity in zip(changed, [t["id"] for t in inputs[1:] + inputs[:1]]):
        row["id"] = identity
    assert pool(changed) == pool(inputs)
    assert f6.evaluate_linkage(selected, inputs)["verdict"] == "PASS"
    assert f6.evaluate_linkage(selected, changed)["verdict"] == "FAIL"


def test_trace_propagates_input_fixture_without_mutating_selected_review():
    from scripts import build_bundle
    review = f6.read(f6.REVIEW / "review.json")
    original = copy.deepcopy(review)
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    trace = f6.PoolPlant("rotated_ids", primary)
    rows = [{k: t[k] for k in ("id", "effect", "ci_low", "ci_high")} for t in primary["trials"]]
    for row, identity in zip(rows, [t["id"] for t in primary["trials"][1:] + primary["trials"][:1]]):
        row["id"] = identity
    trace.actual_primary = rows
    baseline = build_bundle.pooled_reference(review)
    sys.settrace(trace.trace)
    try:
        planted = build_bundle.pooled_reference(review)
    finally:
        sys.settrace(None)
    assert planted["inputs"] == rows
    assert planted["inputs"] != baseline["inputs"]
    assert planted["expected"] == baseline["expected"]
    assert review == original


def test_first_blocker_is_not_replaced_by_later_semantic_refusal():
    result = {"stages": [
        {"stage": "publication_gate", "returncode": 1,
         "stdout": "GATE REFUSE topic\n    - L1: unrelated blocker\n", "stderr": ""},
        {"stage": "independent_verifier", "returncode": 1, "stdout": "", "stderr": ""}],
        "verifier": {"failures": ["INPUT_TUPLE_MISMATCH row"]}}
    first = f6.first_refusal(result)
    assert {k: first[k] for k in ("stage", "code", "message")} == {"stage": "publication_gate", "code": "L1", "message": "L1: unrelated blocker"}
    assert first["stdout"] == result["stages"][0]["stdout"]


def test_missing_native_linkage_verdict_is_not_invented():
    result = {"stages": [], "input_linkage_audit": {"verdict": "FAIL"}}
    assert f6.verdicts(result)["input_linkage"] == "NOT_IMPLEMENTED"


def test_primary_capture_uses_primary_flag_not_efficacy_kind():
    from harness import pipeline, synth
    primary = next(o for o in f6.read(f6.REVIEW / "review.json")["outcomes"] if o.get("primary"))
    tracer = f6.PoolPlant("rotated_ids", primary)

    def _build_outcome():
        # Exercise the actual statistics function with the producer's real
        # primary/efficacy calling convention, including its separate trials.
        spec = {"primary": True}
        kind = "efficacy"
        trials = copy.deepcopy(primary["trials"])
        studies = [synth.Study(label=t["label"], effect=t["effect"], ci_low=t["ci_low"],
                               ci_high=t["ci_high"], study_effect=t["study_effect"]) for t in trials]
        return pipeline._pool_result(studies, "HR", require_study_effect=True)

    sys.settrace(tracer.trace)
    try:
        result = _build_outcome()
    finally:
        sys.settrace(None)
    assert result["estimate"] == primary["result"]["estimate"]
    assert tracer.selected is not None
    assert tracer.actual_primary is not None
    assert tracer.actual_primary[0]["id"] == primary["trials"][1]["id"]
    assert tracer.actual_primary[0]["effect"] == primary["trials"][0]["effect"]
