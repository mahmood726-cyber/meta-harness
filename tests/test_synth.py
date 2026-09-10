"""Unit tests for the synthesis engine's documented behaviours.

The metafor agreement (tau2/mu/se/CI/PI < 1e-6) is proven by
scripts/validate_synth.py on dat.bcg. Here we test the two things that are NOT
validated against metafor because they are deliberate house-rule deviations or
edge cases: the HKSJ variance floor under under-dispersion, and zero-cell handling.
"""
from __future__ import annotations
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.synth import Study, pool_rr, _wmean, _effects  # noqa: E402


def test_hksj_floor_inactive_when_overdispersed():
    # Studies that disagree strongly -> Q > k-1 -> factor > 1 -> CI wider than a
    # naive RE-only interval. se_log should exceed the RE-only se.
    studies = [
        Study("a", 10, 100, 30, 100),
        Study("b", 50, 100, 20, 100),
        Study("c", 5, 100, 40, 100),
        Study("d", 60, 100, 10, 100),
    ]
    res = pool_rr(studies)
    yi, vi = _effects(studies)
    _, _, sw = _wmean(yi, vi, res.tau2)
    se_re = math.sqrt(1.0 / sw)
    assert res.se_log > se_re, "over-dispersed: HKSJ should widen beyond RE se"


def test_hksj_floor_active_when_underdispersed():
    # Near-identical effects -> Q < k-1 -> factor floored at 1 -> se_log == RE se
    # (HKSJ must NOT narrow below the RE model).
    studies = [
        Study("a", 20, 100, 40, 100),
        Study("b", 20, 100, 40, 100),
        Study("c", 20, 100, 40, 100),
        Study("d", 20, 100, 40, 100),
        Study("e", 20, 100, 40, 100),
    ]
    res = pool_rr(studies)
    yi, vi = _effects(studies)
    _, _, sw = _wmean(yi, vi, res.tau2)
    se_re = math.sqrt(1.0 / sw)
    assert abs(res.se_log - se_re) < 1e-12, "under-dispersed: HKSJ se must be floored to RE se"


def test_zero_cell_continuity_applied_only_to_that_study():
    # One study has a zero event cell -> 0.5 correction to all four of ITS cells.
    studies = [Study("z", 0, 100, 10, 100), Study("y", 15, 100, 20, 100)]
    yi, vi = _effects(studies)
    # study z log RR uses (0.5/101)/(10.5/101); finite, negative
    assert math.isfinite(yi[0]) and yi[0] < 0
    # study y untouched: log((15/100)/(20/100))
    assert abs(yi[1] - math.log((15 / 100) / (20 / 100))) < 1e-12


ALL = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]


def main():
    p = f = 0
    for t in ALL:
        try:
            t(); print(f"PASS  {t.__name__}"); p += 1
        except Exception as e:  # noqa: BLE001
            print(f"FAIL  {t.__name__}: {e}"); f += 1
    print(f"\n{p} passed, {f} failed, {len(ALL)} total")
    return 1 if f else 0


if __name__ == "__main__":
    sys.exit(main())
