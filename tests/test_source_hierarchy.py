"""Proves the comparator source hierarchy: abstract headline wins; full text only fills.

This pins the fix for the topic-1 near-miss where full-text extraction overrode the
comparator's abstract headline RR 0.40 (0.30-0.54) with a different in-text figure
0.46 (0.37-0.58). The hierarchy is now explicit in extract.comparator_effect and this
test fails if anyone lets full text override an abstract headline.
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.extract import comparator_effect  # noqa: E402

ABSTRACT = ("Colchicine reduced recurrent pericarditis during follow-up "
            "(RR=0.40, 95% CI 0.30 to 0.54). Adverse events were not increased.")
FULLTEXT = ("In a sensitivity analysis of recurrent pericarditis the risk ratio was "
            "RR 0.46 (95% CI 0.37 to 0.58). Gastrointestinal adverse events occurred more often "
            "with colchicine (RR 1.85, 95% CI 1.04 to 3.29).")


def test_abstract_headline_wins_over_fulltext():
    eff = comparator_effect(ABSTRACT, FULLTEXT, ["recurren"])
    assert eff is not None and abs(eff["effect"] - 0.40) < 1e-9, eff
    assert abs(eff["ci_low"] - 0.30) < 1e-9 and abs(eff["ci_high"] - 0.54) < 1e-9, eff


def test_fulltext_fills_outcome_absent_from_abstract():
    # The abstract says AEs "not increased" but gives no effect; full text supplies it.
    eff = comparator_effect(ABSTRACT, FULLTEXT, ["gastrointestinal", "adverse"])
    assert eff is not None and abs(eff["effect"] - 1.85) < 1e-9, eff


def test_absent_everywhere_returns_none():
    assert comparator_effect(ABSTRACT, FULLTEXT, ["mortality", "death"]) is None


ALL = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]


def main():
    p = f = 0
    for t in ALL:
        try:
            t(); print("PASS ", t.__name__); p += 1
        except Exception as e:  # noqa: BLE001
            print("FAIL ", t.__name__, e); f += 1
    print(f"\n{p} passed, {f} failed")
    return 1 if f else 0


if __name__ == "__main__":
    sys.exit(main())
