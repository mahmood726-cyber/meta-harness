"""C3 (k=1 pooling wording; external audit r15 + H13/H19): a single-trial outcome is never described as pooled, nor with
the random-effects method, heterogeneity or a prediction interval. CONTROL: k >= 2 text is unchanged, so the fix cannot
pass by rewording "pooled" everywhere."""
from __future__ import annotations

import json
from pathlib import Path

from harness import grade, manuscript, page, rob_sensitivity

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "docs" / "reviews").glob("*/review.json"))]


def _k(r):
    return ((next((o for o in r["outcomes"] if o.get("primary")), {}).get("result")) or {}).get("k")


def test_PLANT_the_methods_sentence_follows_k():
    assert "Pooling used random effects" not in manuscript._pooling_method_sentence({"k": 1, "ci_provenance": "source-reported-CI:k=1-verbatim"})
    assert "reported 95% CI, verbatim" in manuscript._pooling_method_sentence({"k": 1, "ci_provenance": "source-reported-CI:k=1-verbatim"})
    assert "reconstructed" in manuscript._pooling_method_sentence({"k": 1, "ci_provenance": "synth.pool:single-trial-Wald-z(k=1):v1"})
    assert "Pooling used random effects" in manuscript._pooling_method_sentence({"k": 3})


def test_PLANT_stale_note_and_rob_reason_at_k1():
    r = {"invalidation": {"reasons": [{"code": "eligible_declared_absent"}]},
         "outcomes": [{"primary": True, "result": {"k": 1}}]}
    s = grade.stale_heterogeneity(r)
    assert "pooled" not in s and "tau^2" not in s and "single-trial" in s
    r2 = dict(r, outcomes=[{"primary": True, "result": {"k": 3}}])
    assert "pooled membership" in grade.stale_heterogeneity(r2)                       # control
    sens = {"full": {"k": 1}, "low_only": {"k": 1}, "low_only_relation": "LOW_ONLY_IDENTICAL_TO_FULL"}
    assert "full pool" not in rob_sensitivity.suppression_reason(dict(sens, formally_assessed=True))


def test_sweep_no_served_k1_review_is_described_as_pooled_and_k2plus_still_is():
    k1 = [r for r in REVIEWS if _k(r) == 1]
    def served_pool(r):
        res = next((o for o in r["outcomes"] if o.get("primary")), {}).get("result") or {}
        return not (res.get("suppressed_incompatible") or res.get("pool_refused"))
    k2 = [r for r in REVIEWS if isinstance(_k(r), int) and _k(r) >= 2 and served_pool(r)]
    assert len(REVIEWS) == 32 and k1 and k2                                          # the denominator
    for r in k1:
        html = page.render_overview(r)
        man = manuscript.render(r)
        assert "Pooling used random effects" not in man, r["slug"]
        assert "Trials pooled (k)" not in html, r["slug"]
    for r in k2:                                                                       # control: unchanged
        assert "Trials pooled (k)" in page.render_overview(r), r["slug"]
