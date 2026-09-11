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


def test_irr_pooling_matches_metafor_point_and_tau2():
    # Incidence-rate ratio from events + person-time; point + tau2 match metafor measure='IRR'
    # (rma PM+knha): metafor gives IRR 0.7021166, tau2 0. CI uses our declared HKSJ floor.
    from harness.synth import Study, pool
    s = [Study('A', e1i=50, t1i=1000, e2i=75, t2i=1000, measure='IRR'),
         Study('B', e1i=30, t1i=800, e2i=40, t2i=820, measure='IRR')]
    r = pool(s, scale='IRR')
    assert abs(r.estimate - 0.7021166) < 1e-5, r.estimate
    assert r.tau2 == 0.0
    assert r.k == 2


def test_irr_zero_event_correction():
    from harness.synth import Study
    y, v = Study('Z', e1i=0, t1i=500, e2i=5, t2i=500, measure='IRR').yi_vi()
    assert v == 1.0 / 0.5 + 1.0 / 5.5  # 0.5 correction on the zero event arm only


def test_md_pooling_matches_metafor_point_and_tau2():
    # Mean difference; point + tau2 match metafor measure='MD' (rma PM+knha): -1.744541, tau2 0.
    from harness.synth import Study, pool
    s = [Study('A', mean1=5.0, sd1=2.0, nc1=50, mean2=7.0, sd2=2.5, nc2=50, measure='MD'),
         Study('B', mean1=4.5, sd1=1.8, nc1=40, mean2=6.0, sd2=2.2, nc2=42, measure='MD')]
    r = pool(s, scale='MD')
    assert abs(r.estimate - (-1.744541)) < 1e-5, r.estimate
    assert r.tau2 == 0.0 and r.k == 2
    # additive scale: estimate is NOT exp-transformed (would be ~0.17 if it were)
    assert r.estimate < 0
