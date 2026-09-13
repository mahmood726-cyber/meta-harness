"""Regression tests for the method-declaration defect (melatonin cold audit, cycle 84):
a mean-difference outcome was labelled with the log-ratio method, and the declared==served gate
limb compared one METHOD constant to itself and could never fire. These tests prove the method
string is scale-aware and that gate.check_method_matches_scale CAN fail on a mislabel.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import gate  # noqa: E402
from harness.synth import method_text, METHOD_MD, METHOD_RATIO  # noqa: E402


def test_method_text_is_scale_aware():
    assert method_text("MD") == METHOD_MD
    assert method_text("SMD") == METHOD_MD
    assert "mean difference" in method_text("MD").lower()
    assert "log ratio" not in method_text("MD").lower()   # the exact melatonin defect
    for s in ("RR", "OR", "HR", "IRR", "mixed (HR/IRR/RR)"):
        assert method_text(s) == METHOD_RATIO
        assert "log ratio" in method_text(s).lower()


def test_gate_method_check_FIRES_on_md_outcome_labelled_log_ratio(tmp_path):
    """Plant the melatonin defect: an MD-scale pooled outcome carrying the log-ratio method string.
    The gate must refuse it (the anti-'check that cannot fail' proof)."""
    rd = tmp_path / "planted"
    rd.mkdir()
    review = {"slug": "planted", "outcomes": [
        {"name": "Change in minutes", "primary": True, "estimand": "MD",
         "method": METHOD_RATIO,  # WRONG: log-ratio method on a mean-difference pool
         "result": {"k": 2, "scale": "MD", "estimate": -12.0}}]}
    (rd / "review.json").write_text(json.dumps(review), encoding="utf-8")
    reasons = gate.check_method_matches_scale(str(rd))
    assert reasons and "does not match the pooled scale" in reasons[0], reasons


def test_gate_method_check_PASSES_when_md_outcome_has_md_method(tmp_path):
    rd = tmp_path / "clean"
    rd.mkdir()
    review = {"slug": "clean", "outcomes": [
        {"name": "Change in minutes", "primary": True, "estimand": "MD",
         "method": METHOD_MD, "result": {"k": 2, "scale": "MD", "estimate": -12.0}}]}
    (rd / "review.json").write_text(json.dumps(review), encoding="utf-8")
    assert gate.check_method_matches_scale(str(rd)) == []


def test_gate_method_check_FIRES_on_ratio_outcome_labelled_md(tmp_path):
    rd = tmp_path / "planted2"
    rd.mkdir()
    review = {"slug": "planted2", "outcomes": [
        {"name": "MACE", "primary": True, "estimand": "RR",
         "method": METHOD_MD,  # WRONG: mean-difference method on a ratio pool
         "result": {"k": 3, "scale": "RR", "estimate": 0.9}}]}
    (rd / "review.json").write_text(json.dumps(review), encoding="utf-8")
    reasons = gate.check_method_matches_scale(str(rd))
    assert reasons and "does not match the pooled scale" in reasons[0], reasons


def test_every_live_review_method_matches_its_scale():
    """Corpus-wide: no live review may carry a method string inconsistent with its pooled scale."""
    import glob
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bad = []
    for rp in glob.glob(os.path.join(root, "docs", "reviews", "*", "review.json")):
        rd = os.path.dirname(rp)
        r = gate.check_method_matches_scale(rd)
        if r:
            bad.append((os.path.basename(rd), r[0]))
    assert not bad, "method/scale mismatches still live: " + "; ".join(f"{s}: {m}" for s, m in bad)
