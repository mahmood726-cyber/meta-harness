import json
import subprocess
from pathlib import Path

from harness import absence
from scripts import refusal_reason_sweep as sweep

ROOT = Path(__file__).resolve().parents[1]
SLUG = "iv-iron-hfref-hosp"


def _primary_row(review, pmid="33197395"):
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    row = next(t for t in primary["declared_absent_trials"] if pmid in str(t.get("id")))
    return primary, row


def _prefix_review():
    raw = subprocess.check_output(
        ["git", "show", f"aa8ed28a:docs/reviews/{SLUG}/review.json"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    return json.loads(raw)


def test_plant_prefix_affirm_refusal_reason_is_false():
    review = _prefix_review()
    outcome, row = _primary_row(review)
    classified = sweep.classify_row(SLUG, outcome, row)
    assert classified["verdict"] == "FALSE", classified
    assert classified["corrected_code"] == absence.EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH
    assert "217 total heart failure hospitalisations" in classified["source_contains"]
    assert "RR 0.74" in classified["source_contains"]


def test_postfix_affirm_refusal_reason_is_true():
    review = json.loads((ROOT / "docs" / "reviews" / SLUG / "review.json").read_text(encoding="utf-8"))
    outcome, row = _primary_row(review)
    classified = sweep.classify_row(SLUG, outcome, row)
    assert classified["verdict"] == "TRUE", classified
    assert row["reason_code"] == absence.EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH
    assert "217 total heart failure hospitalisations" in row["source_span"]


def test_synthetic_outcome_not_in_source_is_true():
    row = {"reason_code": absence.OUTCOME_NOT_IN_SOURCE}
    actual = absence.classify_reason(
        ["heart failure hospitalization"],
        "The trial reported quality of life and six-minute walk distance only.",
        outcome_name="Heart-failure hospitalization RR",
        declared_estimand="RR",
        row=row,
    )
    assert actual["reason_code"] == absence.OUTCOME_NOT_IN_SOURCE
    assert absence.verdict_for_row(row, actual) == "TRUE"


def test_synthetic_missing_abstract_is_source_not_retrieved_true():
    row = {"reason_code": absence.SOURCE_NOT_RETRIEVED}
    actual = absence.classify_reason(
        ["heart failure hospitalization"],
        "",
        outcome_name="Heart-failure hospitalization RR",
        declared_estimand="RR",
        row=row,
    )
    assert actual["reason_code"] == absence.SOURCE_NOT_RETRIEVED
    assert absence.verdict_for_row(row, actual) == "TRUE"
