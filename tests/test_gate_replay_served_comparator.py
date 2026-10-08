"""Plant: the publication gate's offline replay builds with the SERVED comparator. build_topic and reproduce_review
apply served_comparator.served_config; the gate's L1 replay read topics/<slug>.json raw, so on the five topics whose
comparator switch was unsigned (V8 pending) it replayed against the adopted comparator and refused every one of them
on PR #13's CI ('offline replay does NOT regenerate the committed numbers').

The unsigned case is SIMULATED (switch_signed forced False): read against the live register this control retired
itself the day V8 was signed (7 Oct). The signed case is asserted on the live register."""
import json
import os

from harness import gate, served_comparator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "dpp4-mace-t2d"


def _replay_comparators(monkeypatch):
    seen = {}
    from harness import fetch, pipeline
    monkeypatch.setattr(gate, "_registration_sha", lambda slug: "sha")
    monkeypatch.setattr(fetch, "ensure", lambda cfg, *a, **k: seen.setdefault("fetch", cfg.get("comparator_pmid")) and [])
    monkeypatch.setattr(pipeline, "build_review_core",
                        lambda slug, cfg, records, sha: seen.setdefault("build", cfg.get("comparator_pmid")) and {})
    gate.check_reproduction(".", {"slug": SLUG, "review_sha256": "x"})
    return str(seen.get("fetch")), str(seen.get("build"))


def test_replay_uses_the_served_comparator_while_a_switch_is_unsigned(monkeypatch):
    adopted = str(json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))["comparator_pmid"])
    monkeypatch.setattr(served_comparator, "switch_signed", lambda *a, **k: False)
    retired = served_comparator.unsigned_switch(SLUG, adopted)
    assert retired and retired != adopted
    assert _replay_comparators(monkeypatch) == (retired, retired)


def test_replay_uses_the_adopted_comparator_once_signed(monkeypatch):
    """V8-01 signed 7 Oct: the served comparator is the adopted one."""
    adopted = str(json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))["comparator_pmid"])
    assert served_comparator.unsigned_switch(SLUG, adopted) is None
    assert _replay_comparators(monkeypatch) == (adopted, adopted)
