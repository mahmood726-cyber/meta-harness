"""The served-artefact leak scanner (audit 25/26) must FIRE when an aggregate artefact publishes a derived
pooled statistic for a suppressed-state topic — the exact leak found live (iv-iron tau^2=0.178 in
weakness_survey.json while the page said "not a valid summary") — and must be CLEAN on the shipped corpus."""
import json
import os
import tempfile

from harness import leakscan

DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")


def _mini_docs(tmp, review_states, artefacts):
    """Build a minimal docs/ tree: review_states maps slug -> dict written as the primary result; artefacts
    maps filename -> json object written at docs/<filename>."""
    d = os.path.join(tmp, "docs")
    for slug, res in review_states.items():
        rd = os.path.join(d, "reviews", slug)
        os.makedirs(rd, exist_ok=True)
        json.dump({"outcomes": [{"primary": True, "result": res}]},
                  open(os.path.join(rd, "review.json"), "w", encoding="utf-8"))
    for name, obj in artefacts.items():
        json.dump(obj, open(os.path.join(d, name), "w", encoding="utf-8"))
    return d


def test_scanner_fires_on_planted_tau2_leak():
    with tempfile.TemporaryDirectory() as tmp:
        d = _mini_docs(
            tmp,
            {"iv-iron": {"suppressed_incompatible": True, "k": 2}},
            # the exact shape of the live leak: a suppressed topic with tau2 + ci_crosses_null in an aggregate
            {"weakness_survey.json": {"dimensions": {"8_statistical_fragility": [
                {"topic": "iv-iron", "k": 2, "tau2": 0.178, "ci_crosses_null": True}]}}},
        )
        leaks = leakscan.scan(d)
        assert leaks, "scanner did not fire on a planted tau2 leak for a suppressed topic"
        assert any("tau2" in lk["leak"] for lk in leaks)
        assert any(lk["slug"] == "iv-iron" for lk in leaks)


def test_scanner_fires_on_slug_keyed_estimate():
    with tempfile.TemporaryDirectory() as tmp:
        d = _mini_docs(
            tmp,
            {"omega3": {"suppressed_incompatible": True, "k": 7}},
            {"spec_curve.json": {"omega3": {"specs": {"RE_HKSJ": {"estimate": 0.94, "ci_low": 0.89}}}}},
        )
        leaks = leakscan.scan(d)
        assert any(lk["slug"] == "omega3" for lk in leaks), "scanner missed a slug-keyed estimate leak"


def test_scanner_clean_when_suppressed_entry_has_no_stats():
    with tempfile.TemporaryDirectory() as tmp:
        d = _mini_docs(
            tmp,
            {"iv-iron": {"suppressed_incompatible": True, "k": 2}},
            {"spec_curve.json": {"iv-iron": {"not_applicable": "suppressed", "suppressed_incompatible": True}},
             "deficit.json": {"iv-iron": {"our_k": "suppressed", "deficit": "SUPPRESSED"}}},
        )
        assert leakscan.scan(d) == [], "scanner false-fired on a correctly-suppressed aggregate entry"


def test_shipped_corpus_has_no_suppressed_leak():
    """The live guard: no served aggregate artefact publishes a derived pooled statistic for any
    suppressed-state topic on the shipped corpus."""
    leaks = leakscan.scan(DOCS)
    assert leaks == [], f"served artefacts leak suppressed statistics: {leaks}"
