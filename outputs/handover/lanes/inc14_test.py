"""Mahmood's review of the served glp1 page (edaf5f6b / 98726cc1), item 4: the headline still rendered the prediction
interval 0.81-0.91 (x8) and the pooled effect with no subset framing while the pool's membership is known incomplete
(3 eligible families not pooled). Requirement: while membership is incomplete the headline effect is labelled a subset
estimate with its denominator (from the trial-family ledger), "not the current systematic-review estimate", and tau^2 /
I^2 / prediction-interval numerals are withheld from the headline and the manuscript's result sentence (they stay in the
outcome audit block as descriptive values). Plant: on bf2af50d the glp1 headline carries the prediction interval and no
subset label.
"""
import json
import pathlib
import re

from harness import manuscript, page

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _review(slug):
    return json.loads((ROOT / "docs/reviews" / slug / "review.json").read_text(encoding="utf-8"))


def _plain(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def test_glp1_headline_is_a_subset_estimate_without_heterogeneity_numerals():
    review = _review("glp1-ra-mace-t2d")
    sub = page.subset_headline(review)
    assert sub and "Subset estimate (k=8 of 11 eligible families; not the current systematic-review estimate)" == sub["label"], sub
    html = page.render_page(review)
    text = _plain(html)
    assert "Subset estimate (k=8 of 11 eligible families; not the current systematic-review estimate)" in text
    # the headline block ends where the known-missing panel begins; no PI/tau numerals before it
    head = text[: text.find("Known eligible trials not in this pool")]
    assert "Prediction interval 0.81" not in head and "withheld from the headline" in head
    assert "Between-study" not in head
    ms = _plain(manuscript.render(review))
    assert "not the current systematic-review estimate" in ms
    assert "prediction interval was" not in ms


def test_complete_pool_keeps_its_headline():
    review = _review("glp1-ra-mace-t2d")
    review["invalidation"] = {"reasons": []}
    for o in review["outcomes"]:
        o.pop("known_missing_sensitivity", None)
    review.pop("known_missing_sensitivity", None)
    assert page.subset_headline(review) is None
