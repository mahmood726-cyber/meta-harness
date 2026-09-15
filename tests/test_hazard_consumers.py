import hashlib

from harness import hazard_consumers
from harness.limitations import check_consumers
from harness.page import render_page


def _uoa_obj(consumer=None):
    text = "<div class='absent'>unit of analysis plant</div>"
    return {
        "limitation_id": "topic:plant:riskofbias:unit-of-analysis",
        "kind": "UNIT_OF_ANALYSIS",
        "limitation_class": "VALIDITY_THREATENING",
        "severity": "QUALIFIES_CLAIM",
        "claim_affected": "primary pooled variance and precision",
        "evidence_state": "NOT_ASSESSED",
        "source_fields": ["/unit_of_analysis"],
        "rendered_text": text,
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "linked_decision": {
            "action": "ALLOW_WITH_LABEL",
            "gate_id": "limitation:unit-of-analysis",
            "decision_state": "design state is labelled",
        },
        "consumer": consumer,
    }


def test_every_wired_mapping_has_a_plant_that_changes_gate_verdict():
    rows = hazard_consumers.plant_results()

    assert rows
    assert all(row["changed"] for row in rows), rows
    assert {
        (row["kind"], row["evidence_state"]) for row in rows
    } == set(hazard_consumers.wired_pairs())


def test_unwired_pairs_return_consumer_null_and_marker():
    review = {"slug": "plant", "outcomes": []}
    obj = {
        "limitation_id": "topic:plant:funding",
        "kind": "FUNDING_COI",
        "severity": "QUALIFIES_CLAIM",
        "evidence_state": "PARTIAL",
    }

    annotated = hazard_consumers.annotate_object(review, obj, {"acknowledgements": []})

    assert annotated["consumer"] is None
    assert annotated["unwired"] is True
    assert annotated["unwired_reason"]


def test_unit_of_analysis_without_consumer_refuses_publication_gate():
    reasons = check_consumers({"limitations": [_uoa_obj()]}, {"acknowledgements": []})

    assert reasons == [
        "declared hazard with no consumer: topic:plant:riskofbias:unit-of-analysis"
    ]


def test_unit_of_analysis_with_acknowledgement_passes_publication_gate():
    ack = {
        "acknowledgements": [
            {
                "limitation_id": "topic:plant:riskofbias:unit-of-analysis",
                "signed_by": "test signer",
                "date": "2026-09-15",
                "reason": "plant acknowledgement",
                "tranche": "TRANCHE-hazard-consumers",
            }
        ]
    }

    reasons = check_consumers({"limitations": [_uoa_obj()]}, ack)

    assert reasons == []


def test_acknowledgement_renders_from_limitation_object():
    obj = _uoa_obj()
    obj["unwired"] = True
    obj["unwired_acknowledged"] = {
        "signed_by": "test signer",
        "date": "2026-09-15",
        "reason": "plant acknowledgement",
        "tranche": "TRANCHE-hazard-consumers",
    }
    html = render_page(
        {
            "slug": "plant",
            "title": "Plant",
            "question": "Plant?",
            "limitations": [obj],
            "outcomes": [{"primary": True, "result": {"present": False, "reason": "none"}}],
        }
    )

    assert "Hazard acknowledgements" in html
    assert "topic:plant:riskofbias:unit-of-analysis" in html
    assert "plant acknowledgement" in html
