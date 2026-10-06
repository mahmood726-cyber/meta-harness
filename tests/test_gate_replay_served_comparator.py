"""Plant: the publication gate's offline replay builds with the SERVED comparator. build_topic and reproduce_review
apply served_comparator.served_config; the gate's L1 replay read topics/<slug>.json raw, so on the five topics whose
comparator switch is unsigned (V8 pending) it replayed against the adopted comparator and refused every one of them
on PR #13's CI ('offline replay does NOT regenerate the committed numbers')."""
import json
import os

from harness import gate, served_comparator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "dpp4-mace-t2d"


def test_replay_uses_the_served_comparator(monkeypatch):
    adopted = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))["comparator_pmid"]
    retired = served_comparator.unsigned_switch(SLUG, str(adopted))
    assert retired and retired != str(adopted)          # the switch is unsigned on this tree (V8 pending)
    seen = {}
    from harness import fetch, pipeline
    monkeypatch.setattr(gate, "_registration_sha", lambda slug: "sha")
    monkeypatch.setattr(fetch, "ensure", lambda cfg, *a, **k: seen.setdefault("fetch", cfg.get("comparator_pmid")) and [])
    monkeypatch.setattr(pipeline, "build_review_core",
                        lambda slug, cfg, records, sha: seen.setdefault("build", cfg.get("comparator_pmid")) and {})
    gate.check_reproduction(".", {"slug": SLUG, "review_sha256": "x"})
    assert str(seen.get("fetch")) == retired and str(seen.get("build")) == retired
