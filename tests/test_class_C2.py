"""C2: scope verdicts require five known, matching PICO axes."""
import copy
import json
from pathlib import Path

import pytest

from harness.page import _comparator
from harness.scope import AXES, assess, compare_pico

ROOT = Path(__file__).resolve().parents[1]


def affirmative(markup):
    return "same question.</strong>" in markup


def test_plant_keyword_match_without_comparator_pico():
    config = {"intervention_terms": ["colchicine"],
              "include": {"intervention_any": ["colchicine"],
                          "population_any": ["pericarditis"]}}
    title = "Colchicine for pericarditis: systematic review"
    result = assess(config, title, "")
    assert result["scope_valid"] is False
    review = {"comparator": {"name": title, "scope": {
        "scope_valid": True, "topic_is_class": False,
        "comparator_is_class": False, "intervention_level_match": True,
        "population_match": True}}}
    assert not affirmative(_comparator(review, False))


def matching_review():
    # Constructed scope descriptions, not claims about any served review.
    pico = {"population": "adults", "intervention_level": "single agent",
            "comparator": "placebo", "outcome": "symptom resolution",
            "design": "double-blind randomized trials"}
    return {"pico": pico, "comparator": {"name": "Constructed comparator",
            "pico": dict(pico), "scope": {"scope_valid": True}}}


def test_complete_match():
    review = matching_review()
    assert assess(review, "", comparator_pico=review["comparator"]["pico"])["scope_valid"]
    assert affirmative(_comparator(review, False))


@pytest.mark.parametrize("axis", AXES)
@pytest.mark.parametrize("side", ["ours", "theirs"])
@pytest.mark.parametrize("value", ["different scope", None, "", "unknown", {}])
def test_each_axis_must_be_known_and_equal(axis, side, value):
    review = matching_review()
    pico = review["pico"] if side == "ours" else review["comparator"]["pico"]
    if value is None:
        del pico[axis]
    else:
        pico[axis] = value
    derived = compare_pico(review["pico"], review["comparator"]["pico"])
    assert derived["scope_valid"] is False
    assert derived["axis_matches"][axis] != "MATCH"
    assert not affirmative(_comparator(review, False))


def test_equal_unknowns_do_not_match_and_negative_override_is_preserved():
    review = matching_review()
    review["pico"]["design"] = review["comparator"]["pico"]["design"] = "unknown"
    assert not affirmative(_comparator(review, False))
    review = matching_review()
    review["comparator"]["scope"] = {"scope_valid": False, "note": "comparator invalid"}
    markup = _comparator(review, False)
    assert "COMPARATOR INVALID" in markup
    assert not affirmative(markup)


def test_sweep_served_reviews():
    paths = sorted((ROOT / "docs" / "reviews").glob("*/review.json"))
    assert len(paths) == 32
    before = after = 0
    for path in paths:
        review = json.loads(path.read_text(encoding="utf-8"))
        original = copy.deepcopy(review)
        old_markup = path.with_name("index.html").read_text(encoding="utf-8")
        before += affirmative(old_markup)
        markup = _comparator(review, False)
        assert "Scope match (is this the same question?)" in markup, path.parent.name
        derived = compare_pico(review.get("pico"), review["comparator"].get("pico"))
        unsupported = affirmative(markup) and not derived["scope_valid"]
        after += unsupported
        assert not unsupported, path.parent.name
        for axis, status in derived["axis_matches"].items():
            assert f"{axis.replace('_', ' ')}: {status}" in markup, path.parent.name
        assert review == original  # Rendering cannot change any stored results.
    assert before == 22
    assert after == 0
