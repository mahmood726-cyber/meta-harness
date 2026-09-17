import json
import subprocess
from pathlib import Path

from harness import consumer_consistency as cc

ROOT = Path(__file__).resolve().parents[1]
PREFIX_REF = "ad5e7c66"


def _prefix_review(slug):
    raw = subprocess.check_output(
        ["git", "show", f"{PREFIX_REF}:docs/reviews/{slug}/review.json"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    return json.loads(raw)


def _current_review(slug):
    return json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))


def _cfg(slug):
    return cc.load_topic_config(slug)


def _records(slug):
    return cc.load_records_blob(slug)


def _outcome(review, name):
    return next(o for o in review["outcomes"] if o.get("name") == name)


def _cell(review, slug, outcome_name, trial_id):
    outcome = _outcome(review, outcome_name)
    return cc.classify_outcome_cell(slug, review, _cfg(slug), _records(slug), outcome, trial_id)


def test_plant_prefix_akrami_mace_source_value_is_unaccounted():
    slug = "colchicine-secondary-cv-prevention"
    cell = _cell(_prefix_review(slug), slug, "Major adverse cardiovascular events", "34876021")
    assert cell["reason_code_false"], cell
    assert cell["unaccounted_source_value"], cell
    assert "8 events" in cell["source_span"] and "28 events" in cell["source_span"]


def test_plant_prefix_cops_mace_reason_code_false():
    slug = "colchicine-secondary-cv-prevention"
    cell = _cell(_prefix_review(slug), slug, "Major adverse cardiovascular events", "32862667")
    assert cell["reason_code_false"], cell
    assert cell["source_reason_code"] == cc.KNOWN_REPORTED_NOT_YET_EXTRACTED
    assert "24 events" in cell["source_span"] and "38 events" in cell["source_span"]


def test_plant_prefix_esketamine_japanese_ctgov_means_refuse_false_absence():
    slug = "esketamine-trd-madrs"
    cell = _cell(_prefix_review(slug), slug, "Change in MADRS", "34696742")
    assert cell["reason_code_false"], cell
    assert cell["source_reason_code"] == "RETRIEVED_REFUSED_WITH_REASON"
    assert "mean -15.2 (SD 13.07, n=39)" in cell["source_span"]
    assert "mean -15.3 (SD 11.68, n=72)" in cell["source_span"]


def test_plant_prefix_esketamine_funding_janssen_not_unknown():
    slug = "esketamine-trd-madrs"
    review = _prefix_review(slug)
    cell = cc.classify_funding_cell(slug, review, _records(slug), "37025256")
    assert cell["reason_code_false"], cell
    assert cell["source_state"] == "INDUSTRY_SPONSORED"
    assert "Janssen" in cell["source_span"]


def test_synthetic_retrieved_outcome_not_reported_is_not_a_violation():
    slug = "synthetic"
    config = {
        "primary_outcome": {
            "name": "Major adverse cardiovascular events",
            "keywords": ["major adverse cardiovascular", "MACE"],
            "estimand": "RR",
        }
    }
    records = {"records": [{"id": "1", "title": "Synthetic trial", "abstract": "The abstract reports sleep quality only."}]}
    review = {
        "slug": slug,
        "screening": {"records": [{"id": "1", "decision": "include"}]},
        "outcomes": [{
            "name": "Major adverse cardiovascular events",
            "estimand": "RR",
            "trials": [],
            "declared_absent_trials": [{"id": "PMID 1", "reason_code": cc.RETRIEVED_OUTCOME_NOT_REPORTED}],
        }],
    }
    outcome = review["outcomes"][0]
    cell = cc.classify_outcome_cell(slug, review, config, records, outcome, "1")
    assert cell["source_state"] == cc.RETRIEVED_OUTCOME_NOT_REPORTED
    assert not cell["source_has_value"]
    assert not cell["reason_code_false"]


def test_postfix_named_rows_are_accounted_after_rebuild():
    cslug = "colchicine-secondary-cv-prevention"
    crev = _current_review(cslug)
    live_mace = "Trial-defined major coronary/cardiovascular composite"
    akrami = _cell(crev, cslug, live_mace, "34876021")
    cops = _cell(crev, cslug, live_mace, "32862667")
    assert not akrami["reason_code_false"] and not akrami["unaccounted_source_value"], akrami
    assert not cops["reason_code_false"] and not cops["unaccounted_source_value"], cops

    eslug = "esketamine-trd-madrs"
    erev = _current_review(eslug)
    japanese = _cell(erev, eslug, "Observed-case Day-28 raw change-score MADRS MD", "34696742")
    funding = cc.classify_funding_cell(eslug, erev, _records(eslug), "37025256")
    assert not japanese["reason_code_false"] and not japanese["unaccounted_source_value"], japanese
    assert not funding["reason_code_false"] and not funding["unaccounted_source_value"], funding
