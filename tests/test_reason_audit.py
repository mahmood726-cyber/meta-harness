import json
import subprocess
from pathlib import Path

from harness import absence, reason_audit
from scripts import reason_audit_sweep

ROOT = Path(__file__).resolve().parents[1]


def _prefix_review(slug):
    raw = subprocess.check_output(
        ["git", "show", f"ad5e7c66:docs/reviews/{slug}/review.json"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    return json.loads(raw)


def test_plant_cocs_reason_code_false_value_held():
    slug = "colchicine-postop-af"
    review = _prefix_review(slug)
    outcome = next(o for o in review["outcomes"] if o.get("name") == "Postoperative atrial fibrillation")
    row = next(t for t in outcome["declared_absent_trials"] if "36286314" in str(t.get("id")))

    audit = reason_audit_sweep.classify_row(slug, outcome, row)

    assert audit["verdict"] == reason_audit.REASON_FALSE_VALUE_HELD, audit
    assert audit["source_id"] == "abstract:36286314"
    assert "POAF was observed" in audit["source_span"]
    assert "21 (18.6%)" in audit["source_span"]
    assert "39 (30.7%)" in audit["source_span"]


def test_synthetic_reason_true_when_value_absent():
    outcome = {"name": "Myocardial infarction"}
    row = {"reason_code": absence.OUTCOME_NOT_IN_SOURCE}
    sources = [{"source_id": "abstract:T1", "source_kind": "abstract",
                "text": "The trial reported quality of life and headache only."}]
    audit = reason_audit.audit_reason_row(outcome, row, sources, {"keywords": ["myocardial infarction"]})
    assert audit["verdict"] == reason_audit.REASON_TRUE


def test_synthetic_estimand_mismatch_on_unreported_outcome_is_wrong_kind():
    outcome = {"name": "Myocardial infarction"}
    row = {"reason_code": absence.EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH}
    sources = [{"source_id": "abstract:T1", "source_kind": "abstract",
                "text": "The trial reported quality of life and headache only."}]
    audit = reason_audit.audit_reason_row(outcome, row, sources, {"keywords": ["myocardial infarction"]})
    assert audit["verdict"] == reason_audit.REASON_WRONG_KIND
