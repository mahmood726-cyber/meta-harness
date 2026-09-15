"""Unit-of-analysis/design caveat rendering.

Before the design-key refusal, balanced crystalloids had pooled cluster-period crossover trials and
needed a variance-inflation sensitivity. After the refusal, those trials are named exclusions and the
only remaining design caveat is BaSICS as an individual-randomized factorial marginal contrast.
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
    assert [u.get("design") for u in uoa] == ["factorial"]
    html = page._riskofbias(r, False)
    assert "point estimate is unaffected" not in html, "the false invariance claim must be gone"
    assert "within-subject" not in html
    assert "individual-randomized factorial designs" in html
    assert "source-reported adjusted marginal estimate" in html
    assert not re.search(r"re-pools \(illustrative DL\) from [0-9.]+ to [0-9.]+", re.sub(r"<[^>]+>", " ", html))
