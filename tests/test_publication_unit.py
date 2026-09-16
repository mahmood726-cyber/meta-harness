import json
import os
import subprocess
from pathlib import Path

from harness import identity
from scripts import publication_unit_sweep


ROOT = Path(__file__).resolve().parents[1]
BASE_REF = os.environ.get("PU_BASE_REF", "aa8ed28a")
COLCHICINE = "colchicine-secondary-cv-prevention"
SPIRONOLACTONE = "spironolactone-hfref-mortality"


def _json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _text(path):
    return (ROOT / path).read_text(encoding="utf-8")


def _git_text(path, ref=BASE_REF):
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT).decode("utf-8")


def _git_json(path, ref=BASE_REF):
    return json.loads(_git_text(path, ref=ref))


def _record_rows(bundle):
    return list(bundle.get("records") or []) + list(bundle.get("ctgov") or [])


def _norm_id(value):
    text = str(value or "").replace("PMID ", "").replace("PMID:", "").strip()
    for sep in ("·", "Â·"):
        if sep in text:
            text = text.split(sep)[-1].strip()
    return text.split()[-1] if text.split() else text


def test_synthetic_publication_units_count_trials_and_publications_separately():
    records = [
        {"id": "100", "id_type": "pmid", "nct": "NCT00000001", "acronym": "TRIALA",
         "title": "Primary trial report", "pubtypes": ["Randomized Controlled Trial"]},
        {"id": "101", "id_type": "pmid", "title": "Secondary analysis of TRIALA",
         "pubtypes": ["Randomized Controlled Trial"]},
        {"id": "102", "id_type": "pmid", "title": "Cost-effectiveness of TRIALA",
         "pubtypes": ["Randomized Controlled Trial"]},
        {"id": "200", "id_type": "pmid", "nct": "NCT00000002", "acronym": "TRIALB",
         "title": "Independent trial report", "pubtypes": ["Randomized Controlled Trial"]},
    ]
    companions = [
        {"pmid": "101", "parent": "TRIALA", "parent_pmid": "100", "trial_family_id": "TRIALA",
         "publication_role": "secondary", "kind": "secondary analysis of already-pooled trial"},
        {"pmid": "102", "parent": "TRIALA", "parent_pmid": "100", "trial_family_id": "TRIALA",
         "publication_role": "economic", "kind": "economic evaluation of already-pooled trial"},
    ]
    review = {
        "screening": {"records": [{"id": r["id"], "decision": "include"} for r in records]},
        "outcomes": [{"trials": [{"id": "100"}, {"id": "200"}], "declared_absent_trials": []}],
    }

    identity.annotate_review(review, records, companions)
    assert identity.included_counts(review) == {"trials": 2, "publications": 4}
    triala_rows = [r for r in review["screening"]["records"] if r["trial_family_id"] == "TRIALA"]
    assert identity.unit_counts(triala_rows) == {"trials": 1, "publications": 3}


def test_planted_prefix_colchicine_failure_is_detected_in_served_bytes():
    review = _git_json(f"docs/reviews/{COLCHICINE}/review.json")
    html = _git_text(f"docs/reviews/{COLCHICINE}/index.html")
    records = _record_rows(_json(f"cache/{COLCHICINE}/records.json"))
    study_families = _json("docs/study_families.json")

    identity.annotate_review(
        review,
        records,
        (study_families.get("topics") or {}).get(COLCHICINE) or [],
    )
    flagged = {row["id"]: row for row in identity.classify_screened_in_not_pooled(review)}

    assert flagged["32407460"]["publication_role"] == "economic"
    assert flagged["32407460"]["trial_family_id"] == "COLCOT"
    assert flagged["34446156"]["publication_role"] == "secondary"
    assert flagged["34446156"]["trial_family_id"] == "LoDoCo2"
    assert "26 further screened-in trial(s) had no poolable value" in html


def test_current_colchicine_page_uses_publication_units_after_rebuild():
    review = _json(f"docs/reviews/{COLCHICINE}/review.json")
    html = _text(f"docs/reviews/{COLCHICINE}/index.html")
    screening = {
        _norm_id(row.get("id")): row
        for row in ((review.get("screening") or {}).get("records") or [])
    }

    assert screening["32407460"]["decision"] == "exclude"
    assert screening["32407460"]["rule_id"] == "X-DEDUP"
    assert screening["32407460"]["publication_role"] == "economic"
    assert screening["32407460"]["trial_family_id"] == "COLCOT"
    assert screening["34446156"]["decision"] == "exclude"
    assert screening["34446156"]["rule_id"] == "X-DEDUP"
    assert screening["34446156"]["publication_role"] == "secondary"
    assert screening["34446156"]["trial_family_id"] == "LoDoCo2"
    assert screening["25784519"]["decision"] == "exclude"
    assert screening["25784519"]["rule_id"] == "X2"
    assert screening["23500260"]["decision"] == "include"
    absent_ids = {
        _norm_id(row.get("id"))
        for outcome in review.get("outcomes") or []
        for row in outcome.get("declared_absent_trials") or []
    }
    assert "23500260" in absent_ids
    assert "trial families" in html
    assert "26 further screened-in trial(s) had no poolable value" not in html


def test_publication_unit_sweep_finds_prefix_and_clears_colchicine_after_rebuild():
    pre = publication_unit_sweep.sweep(ref=BASE_REF)
    post = publication_unit_sweep.sweep()

    assert pre["topics"] == 32
    pre_col = next(row for row in pre["rows"] if row["slug"] == COLCHICINE)
    pre_ids = {item["id"] for item in pre_col["flagged"]}
    assert {"32407460", "34446156"} <= pre_ids

    post_col = next((row for row in post["rows"] if row["slug"] == COLCHICINE), None)
    post_ids = {item["id"] for item in (post_col or {}).get("flagged", [])}
    assert "32407460" not in post_ids
    assert "34446156" not in post_ids


def test_spironolactone_scope_amendment_replaces_identifier_block_after_rebuild():
    pre = _git_json(f"docs/reviews/{SPIRONOLACTONE}/review.json")
    assert pre["identifier_scope"]["verdict"] == "SINGLE_AGENT_OVER_CLASS_POOL"
    assert any(
        reason.get("code") == "identifier_single_agent_class_pool"
        for reason in ((pre.get("invalidation") or {}).get("reasons") or [])
    )

    current = _json(f"docs/reviews/{SPIRONOLACTONE}/review.json")
    html = _text(f"docs/reviews/{SPIRONOLACTONE}/index.html")
    assert current["identifier_scope"]["verdict"] == "DISCLOSED_SCOPE_AMENDMENT"
    assert current["identifier_scope"]["amendment"]["date"] == "2026-09-16"
    assert not any(
        reason.get("code") == "identifier_single_agent_class_pool"
        for reason in ((current.get("invalidation") or {}).get("reasons") or [])
    )
    assert "Identifier scope amendment" in html
    assert "Original scope" in html
    assert "widens the review to" in html
