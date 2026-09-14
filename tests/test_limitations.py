import hashlib

from harness.limitations import compare_limitation_sets


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
