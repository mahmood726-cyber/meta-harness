import hashlib
import json

from harness.gate import check_limitation_decision_links
from harness.limitations import (
    classify_limitation,
    compare_limitation_sets,
    publication_gate_refusals,
)


def _obj(limitation_id="topic:x:test", severity="BLOCKS_CLAIM", state="SUPPRESSED", text="blocked"):
    return {
        "limitation_id": limitation_id,
        "kind": "SUPPRESSED_POOL",
        "severity": severity,
        "claim_affected": "pooled claim",
        "evidence_state": state,
        "source_fields": ["/x"],
        "rendered_text": text,
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def test_compare_limitation_sets_allows_unchanged_pair():
    before = [_obj()]

    ok, reasons = compare_limitation_sets(before, [_obj()], {"acknowledgements": []})

    assert ok is True
    assert reasons == []


def test_compare_limitation_sets_refuses_removed_id():
    before = [_obj()]

    ok, reasons = compare_limitation_sets(before, [], {"acknowledgements": []})

    assert ok is False
    assert reasons == ["removed limitation_id topic:x:test"]


def test_compare_limitation_sets_refuses_severity_softening():
    before = [_obj(severity="BLOCKS_CLAIM")]
    after = [_obj(severity="QUALIFIES_CLAIM")]

    ok, reasons = compare_limitation_sets(before, after, {"acknowledgements": []})

    assert ok is False
    assert reasons == [
        "topic:x:test: severity moved toward less limitation BLOCKS_CLAIM -> QUALIFIES_CLAIM"
    ]


def test_compare_limitation_sets_refuses_evidence_state_softening():
    before = [_obj(state="SUPPRESSED")]
    after = [_obj(state="RECORDED")]

    ok, reasons = compare_limitation_sets(before, after, {"acknowledgements": []})

    assert ok is False
    assert reasons == [
        "topic:x:test: evidence_state moved toward less limitation SUPPRESSED -> RECORDED"
    ]


def test_compare_limitation_sets_refuses_text_change_without_state_change():
    before = [_obj(text="blocked")]
    after = [_obj(text="softened")]

    ok, reasons = compare_limitation_sets(before, after, {"acknowledgements": []})

    assert ok is False
    assert reasons == [
        "topic:x:test: rendered_text changed without state change or renderer acknowledgement"
    ]


def test_validity_threatening_limitation_without_linked_decision_refuses_publication_gate():
    obj = _obj()
    obj["limitation_class"] = "VALIDITY_THREATENING"
    obj.pop("linked_decision", None)

    reasons = publication_gate_refusals([obj])

    assert reasons == [
        "topic:x:test: VALIDITY_THREATENING limitation has no linked_decision",
        "declared hazard with no consumer: topic:x:test",
    ]


def test_validity_threatening_limitation_without_linked_decision_refuses_page_gate(tmp_path):
    obj = _obj()
    obj["limitation_class"] = "VALIDITY_THREATENING"
    obj.pop("linked_decision", None)
    review_dir = tmp_path / "review"
    review_dir.mkdir()
    (review_dir / "review.json").write_text(
        json.dumps({"limitations": [obj]}) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    reasons = check_limitation_decision_links(review_dir)

    assert reasons == [
        "L1: validity-threatening limitation lacks a linked analytic decision or executable consumer -- "
        "topic:x:test: VALIDITY_THREATENING limitation has no linked_decision; "
        "declared hazard with no consumer: topic:x:test"
    ]


def test_named_limitation_kind_classification():
    assert classify_limitation("UNIT_OF_ANALYSIS", "NOT_ASSESSED") == "VALIDITY_THREATENING"
    assert classify_limitation("SUPPRESSED_POOL", "SUPPRESSED") == "VALIDITY_THREATENING"
    assert classify_limitation("RETRACTED_TRIAL_POOLED", "RETRACTED") == "VALIDITY_THREATENING"
    assert classify_limitation("STALE_TOPIC", "STALE") == "VALIDITY_THREATENING"
    assert classify_limitation("SEARCH_PROVENANCE", "RETRACTED") == "VALIDITY_THREATENING"
    assert classify_limitation("RETRIEVAL_CLASS", "NOT_RUN") == "VALIDITY_THREATENING"
    assert classify_limitation("CLAIM_CHECK_ZERO", "NOT_RUN") == "VALIDITY_THREATENING"
    assert classify_limitation("AUDITABILITY_SCOPE", "RECORDED") == "INFORMATIONAL"
