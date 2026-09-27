"""Held single-outcome positives and adversarial identity-loss plants.

Only the pinned git objects supply research text/numbers. Plants are explicitly
synthetic. A naive keyword-only fallback would admit them; each assertion names
the clause that prevents that defect.
"""
import json
import subprocess
from functools import lru_cache
from pathlib import Path

import pytest

from harness import target_endpoint as te
from evidence.unbound_legacy.classify_legacy_rows import outcome_spec

ROOT = Path(__file__).resolve().parents[1]
REF = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"


@lru_cache(None)
def held(path):
    return json.loads(subprocess.check_output(["git", "show", f"{REF}:{path}"], cwd=ROOT, stderr=subprocess.DEVNULL))


@lru_cache(None)
def records(slug):
    try:
        data = held(f"docs/cache/{slug}/records.json")
    except subprocess.CalledProcessError:
        data = held(f"cache/{slug}/records.json")
    return {str(r["id"]): r for r in data["records"]}


def corpus_rows():
    impact = json.loads((ROOT / "evidence/unbound_legacy/impact_3876a62d.json").read_text(encoding="utf-8"))
    for outcome in impact["outcomes"]:
        slug = outcome["slug"]
        spec = outcome_spec(held(f"topics/{slug}.json"), outcome["outcome"])
        for row in outcome["legacy_rows"]:
            if row["provenance"] == "abstract":
                abstract = records(slug)[row["id"].removeprefix("PMID ")]["abstract"]
                yield outcome, row, spec, abstract


@pytest.fixture
def aad():
    return held("topics/probiotics-aad-prevention.json")["primary_outcome"]


@pytest.mark.parametrize("pmid", ["35727573", "24772726"])
def test_held_aad_sentence_and_point_bind(pmid):
    _, row, spec, abstract = next(x for x in corpus_rows() if x[0]["slug"] == "probiotics-aad-prevention" and x[1]["id"] == "PMID " + pmid)
    got = te.classify_bound(spec, abstract, row["source"])
    assert got["target_endpoint_class"] == te.EXACT_TARGET, got
    assert te.extract.extract_effect(got["endpoint_result_span"]).point == row["effect"][0]
    assert got["endpoint_result_span"] in abstract
    assert got["endpoint_binding"] == "single_outcome_phrase_and_estimate"


def classify_plant(spec, sentence, *, effect=0.81, background=""):
    # Same estimate as the held positive, but deliberately changed identity.
    return te.classify_bound(spec, background + sentence, "abstract effect+CI (RR): " + sentence, effect=effect)


@pytest.mark.parametrize("sentence,reason", [
    ("Mortality (RR 0.81, 95% CI 0.49-1.33).", "no declared outcome phrase"),
    ("Adverse events (RR 0.81, 95% CI 0.49-1.33).", "no declared outcome phrase"),
    ("The primary outcome (RR 0.81, 95% CI 0.49-1.33).", "no declared outcome phrase"),
    ("Antibiotic-associated diarrhoea in a subgroup (RR 0.81, 95% CI 0.49-1.33).", "subgroup or secondary"),
    ("In men, antibiotic-associated diarrhoea (RR 0.81, 95% CI 0.49-1.33).", "qualified or ambiguous"),
    ("Secondary antibiotic-associated diarrhoea (RR 0.81, 95% CI 0.49-1.33).", "subgroup or secondary"),
    ("At 7 days, antibiotic-associated diarrhoea (RR 0.81, 95% CI 0.49-1.33).", "timepoint identity"),
    ("Mortality with antibiotic-associated diarrhoea (RR 0.81, 95% CI 0.49-1.33).", "qualified or ambiguous"),
    ("Mortality and antibiotic-associated diarrhoea (RR 0.81, 95% CI 0.49-1.33).", "qualified or ambiguous"),
    ("Recurrent antibiotic-associated diarrhoea (RR 0.81, 95% CI 0.49-1.33).", "qualified or ambiguous"),
    ("Antibiotic-associated diarrhoea (RR 0.81, 95% CI 0.49-1.33) in men.", "qualified or ambiguous"),
    ("Non-antibiotic-associated diarrhoea (RR 0.81, 95% CI 0.49-1.33).", "qualified or ambiguous"),
    ("Antibiotic-associated diarrhoea (RR 0.81, 95% CI 0.49-1.33) and mortality (RR 0.70, 95% CI 0.40-1.20).", "requires one source-reported ratio"),
])
def test_identity_plants_stay_unbound(aad, sentence, reason):
    got = classify_plant(aad, sentence, background="The primary outcome was antibiotic-associated diarrhoea. ")
    assert got["target_endpoint_class"] == te.ENDPOINT_UNBOUND, got
    assert reason in got["endpoint_binding_reason"]


def test_component_cannot_bind_composite_even_without_canonical_components():
    spec = {"name": "Diarrhoea or vomiting", "keywords": ["diarrhoea"]}
    got = classify_plant(spec, "Diarrhoea (RR 0.81, 95% CI 0.49-1.33).")
    assert got["target_endpoint_class"] == te.ENDPOINT_UNBOUND
    assert "composite identity" in got["endpoint_binding_reason"]


def test_mismatched_estimate_is_not_rescued_by_correct_outcome(aad):
    sentence = "Antibiotic-associated diarrhoea (RR 0.81, 95% CI 0.49-1.33)."
    assert classify_plant(aad, sentence)["target_endpoint_class"] == te.EXACT_TARGET
    got = classify_plant(aad, sentence, effect=0.70)
    assert got["target_endpoint_class"] == te.ENDPOINT_UNBOUND
    assert "point estimate" in got["endpoint_binding_reason"]


def test_losing_estimate_or_name_cannot_increase_admissibility(aad):
    sentence = "Antibiotic-associated diarrhoea (RR 0.81, 95% CI 0.49-1.33)."
    source = "abstract effect+CI (RR): Antibiotic-associated diarrhoea ("
    assert te.classify_bound(aad, sentence, source)["target_endpoint_class"] == te.ENDPOINT_UNBOUND
    assert te.classify_bound(aad, sentence, source, effect=0.81)["target_endpoint_class"] == te.EXACT_TARGET
    stripped = dict(aad, name="", keywords=["primary outcome"])
    assert classify_plant(stripped, sentence)["target_endpoint_class"] == te.ENDPOINT_UNBOUND


def test_declared_synonym_and_definition_are_supported_without_topic_lists():
    sentence = "An explicitly declared endpoint (RR 0.81, 95% CI 0.49-1.33)."
    for key, value in [("synonyms", ["An explicitly declared endpoint"]), ("definition", "An explicitly declared endpoint")]:
        assert classify_plant({"name": "Synthetic test outcome", key: value}, sentence)["target_endpoint_class"] == te.EXACT_TARGET


def test_undeclared_or_unexpanded_acronym_is_not_identity(aad):
    sentence = "Risk of AAD (RR 0.81, 95% CI 0.49-1.33)."
    assert classify_plant(aad, sentence)["target_endpoint_class"] == te.ENDPOINT_UNBOUND
    assert classify_plant(aad, sentence, background="Antibiotic-associated diarrhoea (AAD) was measured. ")["target_endpoint_class"] == te.EXACT_TARGET


def test_every_previously_classified_held_row_is_unchanged():
    baseline = json.loads((ROOT / "evidence/unbound_legacy/legacy_rows_classified.json").read_text(encoding="utf-8"))
    classes = {(r["slug"], r["outcome"], r["id"]): r["class"] for r in baseline["detail"]}
    for outcome, row, spec, abstract in corpus_rows():
        old = classes[outcome["slug"], outcome["outcome"], row["id"]]
        if old != te.ENDPOINT_UNBOUND:
            assert te.classify_bound(spec, abstract, row["source"])["target_endpoint_class"] == old
