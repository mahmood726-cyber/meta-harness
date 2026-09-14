"""COMPARATOR_RESULT_CONTEXT_MISMATCH — the comparator matcher must key 'same question' on the SAME
estimand. Comparing our RR to their OR (or HR to RR) on the log scale is comparing different quantities;
an 'agrees on the same question' claim across estimands is suppressed until a scale-matched,
event-rate-justified conversion is verified. Plant: a cross-estimand pair with a tiny log-diff must NOT
count as agreement (the old matcher counted it)."""
import importlib.util
import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("external_agreement", os.path.join(_ROOT, "scripts", "external_agreement.py"))
EA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(EA)


def test_same_estimand_close_is_agreement():
    r = EA._classify("t", 0.80, "RR", 0.82, "RR", "O")
    assert r["category"] == "same_estimand_agree" and r["agree_within_12pct"] is True


def test_same_estimand_far_is_diverge():
    r = EA._classify("t", 0.50, "RR", 0.90, "RR", "O")
    assert r["category"] == "same_estimand_diverge" and r["agree_within_12pct"] is False


def test_PLANT_cross_estimand_close_is_NOT_agreement():
    # RR 0.92 vs OR 0.92: |log diff| = 0 — the OLD matcher counted this as agreement. It is a cross-
    # estimand comparison (an OR is not an RR), so 'same question' must be SUPPRESSED despite the numbers
    # being identical.
    r = EA._classify("t", 0.92, "RR", 0.92, "OR", "O")
    assert r["category"] == "cross_estimand_pending"
    assert r["agree_within_12pct"] is False
    assert r["same_question"] is False
    assert r["direction_consistent"] is True


def test_cross_estimand_opposite_direction_flagged():
    r = EA._classify("t", 1.05, "HR", 0.83, "OR", "O")
    assert r["category"] == "cross_estimand_opposite"
    assert r["agree_within_12pct"] is False


def test_md_vs_ratio_is_non_comparable():
    r = EA._classify("t", -4.07, "MD", 1.44, "RR", "response rate")
    assert r["category"] == "non_comparable" and r["same_question"] is False


def test_committed_json_counts_only_same_estimand_agreements():
    d = json.load(open(os.path.join(_ROOT, "docs", "external_agreement.json"), encoding="utf-8"))
    # the back-compat headline equals the same-estimand agreement count (never cross-estimand)
    assert d["agree_within_12pct"] == d["same_estimand_agree"]
    for row in d["rows"]:
        if row["category"].startswith("cross_estimand") or row["category"] == "non_comparable":
            assert row["agree_within_12pct"] is False, row["slug"]
            assert row.get("same_question") is False, row["slug"]


def test_index_prose_does_not_assert_cross_estimand_agreement():
    # The rendered index must not resurrect the old "21 agree on the same question" claim.
    h = open(os.path.join(_ROOT, "docs", "index.html"), encoding="utf-8").read()
    i = h.find("External validation")
    assert i >= 0
    seg = h[i:i + 2000]
    assert "SUPPRESSED" in seg
    assert "same estimand" in seg
