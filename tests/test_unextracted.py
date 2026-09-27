import json
import subprocess
from pathlib import Path

from harness import absence, reason_audit, unextracted
from scripts import unextracted_sweep

ROOT = Path(__file__).resolve().parents[1]


def _prefix_review(slug):
    raw = subprocess.check_output(
        ["git", "show", f"ad5e7c66:docs/reviews/{slug}/review.json"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    return json.loads(raw)


def test_plant_akrami_mace_is_held_not_extracted():
    slug = "colchicine-secondary-cv-prevention"
    review = _prefix_review(slug)
    outcome = next(o for o in review["outcomes"] if o.get("name") == "Major adverse cardiovascular events")

    audit = unextracted_sweep.classify_pair(slug, review, outcome, "34876021")

    assert audit["status"] == unextracted.HELD_NOT_EXTRACTED, audit
    assert audit["source_id"] == "abstract:34876021"
    assert audit["value_text"] == "8/120 vs 28/129"
    assert "8 events" in audit["source_span"]
    assert "28 events" in audit["source_span"]


def test_synthetic_extracted_pair():
    outcome = {"name": "Stroke", "trials": [{"id": "PMID 111"}], "declared_absent_trials": []}
    audit = unextracted.audit_pair(outcome, "111", [], {"keywords": ["stroke"]})
    assert audit["status"] == unextracted.EXTRACTED


def test_synthetic_held_not_extracted_pair():
    outcome = {"name": "Stroke", "trials": [], "declared_absent_trials": []}
    sources = [{"source_id": "abstract:T1", "source_kind": "abstract",
                "text": "Stroke occurred in 4 patients (8%) with treatment vs. 9 patients (18%) with placebo."}]
    audit = unextracted.audit_pair(outcome, "T1", sources, {"keywords": ["stroke"]})
    assert audit["status"] == unextracted.HELD_NOT_EXTRACTED
    assert audit["source_id"] == "abstract:T1"


def test_synthetic_not_in_held_sources_pair():
    outcome = {"name": "Stroke", "trials": [], "declared_absent_trials": []}
    sources = [{"source_id": "abstract:T1", "source_kind": "abstract",
                "text": "The trial reported quality of life and headache only."}]
    audit = unextracted.audit_pair(outcome, "T1", sources, {"keywords": ["stroke"]})
    assert audit["status"] == unextracted.NOT_IN_HELD_SOURCES


def test_synthetic_timepoint_mismatch_is_reported_unresolved_not_absent_by_design():
    # REQUIREMENT (denosumab review, 2026-09-27): a timepoint mismatch means the trial REPORTED the outcome at another
    # time; the audit said ABSENT_BY_DESIGN, a claim about the trial's design that the row does not support.
    outcome = {"name": "Stroke", "trials": [], "declared_absent_trials": []}
    row = {"reason_code": absence.TIMEPOINT_MISMATCH}
    sources = [{"source_id": "abstract:T1", "source_kind": "abstract",
                "text": "The trial reported quality of life and headache only."}]
    audit = unextracted.audit_pair(outcome, "T1", sources, {"keywords": ["stroke"]}, row)
    assert audit["status"] == unextracted.REPORTED_UNRESOLVED
    assert audit["status"] != unextracted.ABSENT_BY_DESIGN


def test_a_refusal_about_the_inspected_source_stays_scoped():
    # FREEDOM serious infection: REFUSED_ON_EVIDENCE ("the source gives no serious-infection aggregate") is a statement
    # about what the inspected source says -- never ABSENT_BY_DESIGN
    outcome = {"name": "Serious infection", "trials": [], "declared_absent_trials": []}
    row = {"reason_code": absence.REFUSED_ON_EVIDENCE, "absent_kind": "adjudicated_absent"}
    silent = [{"source_id": "abstract:T1", "source_kind": "abstract", "text": "Fracture risk was reduced."}]
    a = unextracted.audit_pair(outcome, "T1", silent, {"keywords": ["infection"]}, row)
    assert a["status"] == unextracted.NOT_IN_HELD_SOURCES and "scoped" in a["scope"]
    discussed = [{"source_id": "abstract:T1", "source_kind": "abstract",
                  "text": "There was no increase in the risk of infection with denosumab."}]
    b = unextracted.audit_pair(outcome, "T1", discussed, {"keywords": ["infection"]}, row)
    assert b["status"] == unextracted.REPORTED_UNRESOLVED


def test_a_held_full_text_result_invalidates_any_design_absence():
    # PLANT: a design-absence row, but a held full text carries the result -> never absent by design
    outcome = {"name": "Serious infection", "trials": [], "declared_absent_trials": []}
    row = {"reason_code": absence.REFUSED_ON_EVIDENCE, "not_measured_span": "not assessed"}
    ft = [{"source_id": "fulltext:T1", "source_kind": "fulltext",
           "text": ("Serious infection occurred in 159 of 3886 patients (4.1%) in the denosumab group and in 133 of "
                    "3876 (3.4%) in the placebo group.")}]
    a = unextracted.audit_pair(outcome, "T1", ft, {"keywords": ["serious infection"]}, row)
    assert a["status"] == unextracted.HELD_NOT_EXTRACTED
