"""Unit-of-analysis caveat (audit 26): the page must NOT claim the pooled point estimate is invariant to the
missing design correction (false in inverse-variance pooling), and must show the DERIVED sensitivity range;
the design must be described as cluster-period (policy) crossover, not within-person crossover."""
import json
import os
import re

from harness import page

DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "reviews")


def _load(slug):
    return json.load(open(os.path.join(DOCS, slug, "review.json"), encoding="utf-8"))


def test_crystalloids_uoa_estimate_moves_and_range_rendered():
    r = _load("balanced-crystalloids-vs-saline-mortality")
    uoa = r.get("unit_of_analysis") or []
    assert uoa, "expected cluster/crossover trials flagged for crystalloids"
    s = page._uoa_sensitivity(r, [u.get("id") for u in uoa])
    base = s["points"][0][1]
    top = s["points"][-1][1]
    assert top != base, "inflating cluster-trial variances must move the pooled estimate (it is NOT invariant)"
    html = page._riskofbias(r, False)
    assert "point estimate is unaffected" not in html, "the false invariance claim must be gone"
    assert "within-subject" not in html, "must not mis-describe cluster-period as within-person crossover"
    assert "cluster-period" in html.lower()
    assert re.search(r"re-pools \(illustrative DL\) from [0-9.]+ to [0-9.]+", re.sub(r"<[^>]+>", " ", html))
