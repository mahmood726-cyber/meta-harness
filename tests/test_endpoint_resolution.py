"""Same-source endpoint resolution (pass 16; codex P16b, verified corpus-wide with P16c: exactly DELIVER and EMPEROR-Preserved
change). A named endpoint reference resolves only to its definition in the SAME source; negatives: no definition, another endpoint."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# All fixture numbers below are synthetic, not study data.
import pytest

from harness import evidence_identity, reason_audit


OUTCOME = {"name": "Composite cardiovascular death or worsening heart failure", "estimand": "HR"}
ROW = {"id": "fixture-trial", "reason_code": "EXTRACTION_NOT_PERFORMED"}
DEFINITION = (
    "The primary outcome was a composite of worsening heart failure or cardiovascular death."
)
RESULT = (
    "The primary outcome occurred in 12 of 100 patients in the intervention group "
    "and in 20 of 100 patients in the placebo group "
    "(hazard ratio, 0.60; 95% CI, 0.30 to 0.90)."
)


def audit(text, outcome=None):
    return reason_audit.audit_reason_row(
        outcome or OUTCOME, ROW, [{"source_id": "fixture-source", "text": text}], {}
    )


@pytest.mark.parametrize("reference,definition", [
    ("The primary outcome", DEFINITION),
    ("A primary outcome event", DEFINITION),
    ("The primary end point", DEFINITION.replace("outcome", "end point")),
    ("The primary endpoint", DEFINITION.replace("outcome", "endpoint")),
    ("The key secondary outcome", DEFINITION.replace("primary", "key secondary")),
])
def test_plant_resolves_same_source_definition(reference, definition):
    # Pass-15 leaves this unnamed / COMPONENT and cannot disprove the refusal.
    result = audit(definition + " " + RESULT.replace("The primary outcome", reference))
    assert result["verdict"] == reason_audit.REASON_FALSE_VALUE_HELD
    identity = result["evidence_identity"]
    assert identity["endpoint_resolved_from"] == definition
    assert identity["part"] == "COMPOSITE"
    assert identity["mismatch"] == []


@pytest.mark.parametrize("prefix", [
    "",  # no definition anywhere
    DEFINITION.replace("primary", "secondary"),  # a DIFFERENT endpoint
    DEFINITION.replace("primary", "key secondary"),
    "The primary outcome was assessed by a blinded committee.",
])
def test_no_matching_definition_stays_unnamed(prefix):
    result = audit(prefix + " " + RESULT)
    assert result["verdict"] == reason_audit.REASON_NOT_DISPROVED
    assert result["candidates"]
    assert all("endpoint_resolved_from" not in c for c in result["candidates"])
    assert all("outcome" in c["mismatch"] for c in result["candidates"])


def test_definition_of_different_content_does_not_name_requested_outcome():
    definition = "The primary outcome was kidney failure."
    result = audit(definition + " " + RESULT)
    assert result["verdict"] == reason_audit.REASON_NOT_DISPROVED
    assert all(c["endpoint_resolved_from"] == definition for c in result["candidates"])
    assert all("outcome" in c["mismatch"] for c in result["candidates"])


def test_definitions_never_cross_sources():
    result = reason_audit.audit_reason_row(OUTCOME, ROW, [
        {"source_id": "definition-only", "text": DEFINITION},
        {"source_id": "result-only", "text": RESULT},
    ], {})
    assert result["verdict"] == reason_audit.REASON_NOT_DISPROVED
    assert all("endpoint_resolved_from" not in c for c in result["candidates"])


def test_no_resolution_state_leaks_between_trials():
    audit(DEFINITION + " " + RESULT)
    result = reason_audit.audit_reason_row(OUTCOME, {**ROW, "id": "other-fixture-trial"}, [
        {"source_id": "other-source", "text": RESULT},
    ], {})
    assert result["verdict"] == reason_audit.REASON_NOT_DISPROVED
    assert all("endpoint_resolved_from" not in c for c in result["candidates"])


def test_conflicting_definitions_fail_closed():
    result = audit(DEFINITION + " The primary outcome was kidney failure. " + RESULT)
    assert result["verdict"] == reason_audit.REASON_NOT_DISPROVED
    assert all("endpoint_resolved_from" not in c for c in result["candidates"])


def test_reference_must_be_the_subject():
    label = "Kidney failure, unlike the primary outcome, occurred in both groups."
    assert evidence_identity.endpoint_reference(label) is None


def test_composite_definition_cannot_disprove_component_refusal():
    result = audit(DEFINITION + " " + RESULT,
                   {"name": "Worsening heart failure", "estimand": "HR"})
    assert result["verdict"] == reason_audit.REASON_NOT_DISPROVED
    assert all("part:COMPOSITE!=COMPONENT" in c["mismatch"] for c in result["candidates"])


def test_definition_does_not_supply_timepoint_or_effect_measure():
    definition = DEFINITION.replace("cardiovascular death.", "cardiovascular death at 30 days.")
    result = audit(definition + " " + RESULT, {**OUTCOME, "timepoint": "30 days", "estimand": "OR"})
    assert result["verdict"] == reason_audit.REASON_NOT_DISPROVED
    effect = next(c for c in result["candidates"] if c["role"] == "EFFECT_ESTIMATE")
    assert effect["endpoint_resolved_from"] == definition
    assert effect["mismatch"] == ["timepoint:None", "effect_measure:HR!=OR"]
