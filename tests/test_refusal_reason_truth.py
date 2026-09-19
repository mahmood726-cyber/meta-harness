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


def test_postfix_affirm_first_event_row_is_admitted_and_recurrent_total_is_not():
    """Since the hyphen vocabulary fix (2026-09-19) AFFIRM-AHF (33197395) is POOLED on the primary from its CT.gov row 'number of
    participants with at least one HF hospitalisation' (time to first event), (the primary pool itself stays SUPPRESSED, INCOMPATIBLE_ESTIMANDS) so it is no longer a declared-absent row whose
    refusal reason could be audited. The requirement that replaces the old assertion: the pooled row is the first-event participant
    count (142/558 vs 178/550, HR 0.73) and NOT the recurrent-event total (217 vs 294, RR 0.74) the old refusal correctly refused."""
    review = json.loads((ROOT / "docs" / "reviews" / SLUG / "review.json").read_text(encoding="utf-8"))
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    row = next(t for t in primary["trials"] if "33197395" in str(t.get("id")))
    assert row.get("provenance") == "ctgov_results"
    assert row.get("target_endpoint_class") == "EXACT_TARGET"
    assert row.get("endpoint_counts") == {"ai": 142, "n1i": 558, "ci": 178, "n2i": 550}, row.get("endpoint_counts")
    assert (row.get("effect"), row.get("ci_low"), row.get("ci_high")) == (0.73, 0.59, 0.92)
    assert "recurrent" not in str(row.get("registry_title", "")).lower()
    assert "217" not in str(row.get("source", ""))
    assert not any("33197395" in str(t.get("id")) for t in primary.get("declared_absent_trials", []))


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
