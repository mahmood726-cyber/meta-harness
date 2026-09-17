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


def test_synthetic_absent_by_design_pair():
    outcome = {"name": "Stroke", "trials": [], "declared_absent_trials": []}
    row = {"reason_code": absence.TIMEPOINT_MISMATCH}
    sources = [{"source_id": "abstract:T1", "source_kind": "abstract",
                "text": "The trial reported quality of life and headache only."}]
    audit = unextracted.audit_pair(outcome, "T1", sources, {"keywords": ["stroke"]}, row)
    assert audit["status"] == unextracted.ABSENT_BY_DESIGN
