"""Unit-of-analysis/design caveat rendering.

Balanced crystalloids keeps design-refused reconstructed cluster-crossover rows out of the pool.
The unit-of-analysis caveat now covers the remaining pooled factorial marginal contrast, while
the refused cluster-crossover rows are carried by the typed design-refusal object.
"""
import json
import os
import re

from harness import page

DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "reviews")


def _load(slug):
    return json.load(open(os.path.join(DOCS, slug, "review.json"), encoding="utf-8"))


def test_crystalloids_uoa_caveat_matches_post_refusal_factorial_state():
    r = _load("balanced-crystalloids-vs-saline-mortality")
    uoa = r.get("unit_of_analysis") or []
    assert sorted(u.get("design") for u in uoa) == ["factorial"]
    primary = next(o for o in r["outcomes"] if o.get("primary"))
    refused = ((primary.get("result") or {}).get("design_refusal") or {}).get("refused") or []
    assert {row.get("trial") for row in refused} >= {"SMART", "SALT", "SPLIT"}
    html = page._riskofbias(r, False)
    assert "point estimate is unaffected" not in html, "the false invariance claim must be gone"
    assert "within-subject" not in html
    assert "individual-randomized factorial designs" in html
    assert "source-reported adjusted marginal estimate" in html
