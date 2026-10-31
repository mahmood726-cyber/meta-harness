"""Retained PubMed bytes must reach the ordinary extractor, never a verified cache."""
import json
from pathlib import Path

import pytest
from harness import extract, pipeline
from harness.provenance_class import classify_served

ROOT = Path(__file__).resolve().parents[1]
SLUG = "dpp4-mace-t2d"
PMID = "28893244"
OUTCOME = "Hospitalization for heart failure"


def test_dpp4_retained_source_reaches_extractor():
    config = json.loads((ROOT / "topics" / f"{SLUG}.json").read_text(encoding="utf-8"))
    spec = next(s for s in config["harm_outcomes"] if s["name"] == OUTCOME)
    records = json.loads((ROOT / "cache" / SLUG / "records.json").read_text(encoding="utf-8"))["records"]
    rec = next(r for r in records if str(r["id"]) == PMID)
    out = pipeline._build_outcome(spec, "harm", [{"id": PMID, "id_type": "pmid"}],
                                  {PMID: rec}, config["intervention_terms"], config["comparator_terms"], slug=SLUG)
    row = next(t for t in out["trials"] if t["id"] == "PMID " + PMID)
    served = json.loads((ROOT / "docs" / "reviews" / SLUG / "review.json").read_text(encoding="utf-8"))
    expected = next(t for o in served["outcomes"] if o["name"] == OUTCOME
                    for t in o["trials"] if t["id"] == row["id"])
    assert {k: row[k] for k in ("effect", "ci_low", "ci_high")} == {
        k: expected[k] for k in ("effect", "ci_low", "ci_high")}
    assert classify_served(row, lambda _: False)[0] == "EXTRACTOR"
    import hashlib
    assert hashlib.sha256((ROOT / row["document_ref"]).read_bytes()).hexdigest() == row["document_sha256"]
    assert row["source_span"] in (ROOT / row["document_ref"]).read_text(encoding="utf-8")


def test_dpp4_source_mutation_refuses(tmp_path):
    from harness.dpp4_source import route_records
    from harness.source_coverage import coverage_for
    ref = coverage_for(SLUG, PMID)["complete_abstract_ref"]
    target = tmp_path / ref["path"]
    target.parent.mkdir(parents=True)
    target.write_bytes((ROOT / ref["path"]).read_bytes() + b" ")
    with pytest.raises(ValueError, match="SHA-256"):
        route_records(SLUG, OUTCOME, {PMID: {}}, root=tmp_path)


def test_dpp4_no_hand_entered_fallback():
    data = json.loads((ROOT / "cache" / SLUG / "verified_effects.json").read_text(encoding="utf-8"))
    rows = data.get(PMID, [])
    rows = rows if isinstance(rows, list) else [rows]
    assert not any(r.get("outcome") == OUTCOME for r in rows)
