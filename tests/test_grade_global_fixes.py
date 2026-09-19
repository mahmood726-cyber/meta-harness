"""Regression tests for the global GRADE-integrity fixes (tranexamic + statins cold audits):
rounded-CI precision hierarchy, contaminated ghost-census denominator, and D5 registered-secondary.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import grade, rob2  # noqa: E402


def test_rounded_ci_limit_on_null_not_downgraded():
    # RR 0.81 (0.65, 1.00): the 1.00 is a rounded limit; count-recomputed it is 0.9961 (excludes 1).
    imp = grade._imprecision_domain({"k": 1, "ci_low": 0.65, "ci_high": 1.0}, "RR")
    assert imp["downgrade"] == 0 and imp["crosses_null"] is None
    assert "rounding" in imp["basis"]


def test_genuine_null_cross_still_downgrades():
    imp = grade._imprecision_domain({"k": 2, "ci_low": 0.57, "ci_high": 1.78}, "RR")
    assert imp["downgrade"] == 1


def test_contaminated_ghost_census_does_not_downgrade():
    pb = grade._pubbias_domain({"enumerated": 25, "ghost_upper_bound": 11, "ongoing_or_recent": 0})  # 44%, not pico_scoped
    assert pb["downgrade"] == 0 and pb.get("not_assessable") is True
    # a PICO-scoped census with a high fraction still downgrades
    pbs = grade._pubbias_domain({"enumerated": 25, "ghost_upper_bound": 11, "ongoing_or_recent": 0, "pico_scoped": True})
    assert pbs["downgrade"] == 1


def test_d5_registered_secondary_is_not_selective_reporting():
    m = lambda a, b: b == "Death due to bleeding"  # noqa: E731
    dom = rob2.assess({"allocation": "Randomized", "masking": "Double"}, ["Primary X"],
                      "Death due to bleeding", m, registered_secondaries=["Death due to bleeding"])
    assert dom["D5_selective_reporting"]["level"] == "low"
    # a genuinely unregistered (post-hoc) outcome still gets some concerns
    dom2 = rob2.assess({"allocation": "Randomized", "masking": "Double"}, ["Primary X"],
                       "Posthoc Y", lambda a, b: False, registered_secondaries=["Sec Z"])
    assert dom2["D5_selective_reporting"]["level"] == "some concerns"
