"""Synthetic measure/transform boundaries plus real pinned CORP regressions."""
import importlib.util
import json
from pathlib import Path

import pytest

from harness import effect_identity as ei, extract


@pytest.mark.parametrize("phrase,scale", [
    ("relative risk reduction", "RR"),
    ("hazard reduction", "HR"),
    ("reduced the hazard by", "HR"),
    ("relative reduction in the hazard", "HR"),
    ("odds reduction", "OR"),
    ("reduced the odds by", "OR"),
    ("rate reduction", "RATE_RATIO"),
    ("reduced the rate by", "RATE_RATIO"),
])
@pytest.mark.parametrize("numbers", [
    "0.20 (95% CI 0.05 to 0.33)",
    "20% (95% CI 5% to 33%)",
    "20 percent (95% CI 5 percent to 33 percent)",
    "20% (95% CI 5 to 33)",
])
def test_named_measure_and_exact_complement(phrase, scale, numbers):
    sentence = f"{phrase} {numbers}"
    assert extract.extract_effect(sentence) == (scale, 0.80, 0.67, 0.95)
    row = dict(scale=scale, effect=0.8, ci_low=0.67, ci_high=0.95, source=sentence)
    provenance = ei.transform_provenance(row)
    assert provenance["derived"] == dict(measure=scale, estimate=0.8, ci_low=0.67, ci_high=0.95)
    assert provenance["reported"] == dict(estimate=0.2, ci_low=0.05, ci_high=0.33)
    assert "CI endpoints swapped" in provenance["transform"]
    if scale != "RR":
        assert ei.transform_provenance(dict(row, scale="RR")) is None


@pytest.mark.parametrize("sentence", [
    "reduced by 20%",
    "reduced by 20% (95% CI 5% to 33%)",
    "Treatment reduced mortality by 20% (95% CI 5% to 33%)",
    "relative reduction 0.20 (95% CI 0.05 to 0.33)",
    "absolute risk reduction 0.20 (95% CI 0.05 to 0.33)",
    "ARR 20% (95% CI 5% to 33%)",
    "relative risk reduction 20 percentage points (95% CI 5 to 33)",
    "relative risk reduction 0.20 (95% CI 0.05 to 0.33 percentage points)",
    "absolute hazard reduction 0.20 (95% CI 0.05 to 0.33)",
    "hazard reduction 20 (95% CI 5 to 33)",
    "hazard reduction 0.2 (95% CI 5% to 33%)",
    "hazard reduction 20% (95% CI 25% to 33%)",
    "hazard reduction 20% (95% CI 5% to 100%)",
    "hazard reduction -0.2 (95% CI 0.05 to 0.33)",
    "hazard reduction 0.2 (95% CI -0.05 to 0.33)",
])
def test_untyped_absolute_or_invalid_reduction_is_no_ratio(sentence):
    # No effect is the extractor's fail-closed representation; bare reductions
    # are MEASURE_NOT_STATED, not an implicit RR.
    assert extract.extract_effect(sentence) is None
    assert ei.transform_provenance(dict(scale="RR", effect=0.8, ci_low=0.67,
                                       ci_high=0.95, source=sentence)) is None


def test_zero_reduction_limit_and_decimal_precision():
    assert extract.extract_effect("hazard reduction 20% (95% CI 0% to 33%)") == ("HR", 0.8, 0.67, 1.0)
    assert extract.extract_effect("odds reduction 0.123456 (95% CI 0.012345 to 0.234567)") == (
        "OR", 0.876544, 0.765433, 0.987655)


def test_rate_reduction_never_becomes_risk_or_borrows_context_type():
    assert extract.extract_effect("Events occurred 264 times; rate reduction 20% (95% CI 5% to 33%)") == (
        "RATE_RATIO", 0.8, 0.67, 0.95)


@pytest.fixture(scope="module")
def pinned():
    path = Path(__file__).resolve().parents[1] / "evidence/fixtures/build_effect_identity_fixture.py"
    spec = importlib.util.spec_from_file_location("relative_reduction_fixture", path)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    return builder.pinned_inputs()


@pytest.mark.parametrize("outcome", ["Recurrent pericarditis", "Symptom persistence at 72 hours"])
def test_real_corp_served_tuple_is_byte_identical(pinned, outcome):
    _, blobs, paths = pinned
    slug = "colchicine-recurrent-pericarditis"
    review = blobs[f"docs/reviews/{slug}/review.json"]
    row = next(t for o in review["outcomes"] if o["name"] == outcome
               for t in o["trials"] if t["id"] == "PMID 21873705")
    abstract = next(r["abstract"] for r in blobs[paths[slug]]["records"] if str(r["id"]) == "21873705")
    sentence = next(s for s in extract._sentences(abstract)
                    if ("At 18 months" if outcome == "Recurrent pericarditis" else "persistence of symptoms") in s)
    wanted = [row[k] for k in ("scale", "effect", "ci_low", "ci_high")]
    effect = extract.extract_effect(sentence)
    assert json.dumps(effect).encode() == json.dumps(wanted).encode()
    assert ei.transform_provenance(row, abstract)["derived"]["measure"] == "RR"
