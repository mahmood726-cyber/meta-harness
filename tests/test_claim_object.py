"""Canonical claim object: one significance/crossing derivation + a contradiction scan
that must be able to FIRE (mutation test) and must pass on consistent surfaces."""
import harness.claim as C


def test_significant_when_ci_excludes_null_ratio():
    cl = C.derive({"k": 3, "estimate": 0.62, "ci_low": 0.45, "ci_high": 0.85, "scale": "RR"})
    assert cl["present"] and cl["significant"] and cl["crosses_null"] is False
    assert cl["direction"] == "benefit"


def test_not_significant_when_ci_crosses_null():
    cl = C.derive({"k": 2, "estimate": 0.55, "ci_low": 0.036, "ci_high": 8.26, "scale": "RR"})
    assert cl["present"] and cl["significant"] is False and cl["crosses_null"] is True


def test_limit_exactly_on_null_is_not_a_cross():
    # WOMAN 0.65-1.00: a bound printed exactly on the null is rounded, NOT a definite cross.
    cl = C.derive({"k": 1, "estimate": 0.81, "ci_low": 0.65, "ci_high": 1.00, "scale": "RR"})
    assert cl["crosses_null"] is False and cl["touches_null"] is True and cl["significant"] is True


def test_md_null_is_zero():
    cl = C.derive({"k": 3, "estimate": -1.2, "ci_low": -2.0, "ci_high": -0.4, "scale": "MD"})
    assert cl["null"] == 0.0 and cl["significant"] is True and cl["direction"] == "benefit"
    cl2 = C.derive({"k": 3, "estimate": -1.2, "ci_low": -3.0, "ci_high": 0.6, "scale": "MD"})
    assert cl2["significant"] is False and cl2["crosses_null"] is True


def test_suppressed_is_not_present():
    cl = C.derive({"k": 2, "estimate": 0.9, "ci_low": 0.7, "ci_high": 1.1, "scale": "RR",
                   "suppressed_incompatible": True})
    assert cl["present"] is False and cl["significant"] is False


def test_contradiction_scan_fires_on_opposite_assertion():
    # canonical SIGNIFICANT, but a surface says "not significant" -> must be caught.
    cl = C.derive({"k": 3, "estimate": 0.62, "ci_low": 0.45, "ci_high": 0.85, "scale": "RR"})
    con = C.significance_contradictions(cl, {"manuscript": "The effect was not statistically significant."})
    assert len(con) == 1 and con[0]["canonical"] == "significant"
    # canonical NOT significant, but a surface says "significantly reduced" -> caught.
    cl2 = C.derive({"k": 2, "estimate": 0.55, "ci_low": 0.036, "ci_high": 8.26, "scale": "RR"})
    con2 = C.significance_contradictions(cl2, {"page": "corticosteroids significantly reduced mortality"})
    assert len(con2) == 1 and con2[0]["canonical"].startswith("not significant")


def test_common_effect_interval_excluding_null_is_not_a_contradiction():
    # k=2: HKSJ crosses the null (not significant) but the common-effect CI excludes it. A surface
    # stating the common-effect interval 'excludes no-effect' must NOT be flagged (colchicine-recurrent).
    cl = C.derive({"k": 2, "estimate": 0.48, "ci_low": 0.064, "ci_high": 3.62, "scale": "RR",
                   "ci_low_fixed": 0.30, "ci_high_fixed": 0.77})
    assert cl["significant"] is False and cl["significant_fixed"] is True
    con = C.significance_contradictions(cl, {
        "overview": "the common-effect interval shown alongside the HKSJ interval excludes no-effect"})
    assert con == []


def test_contradiction_scan_passes_on_consistent_surface():
    cl = C.derive({"k": 2, "estimate": 0.55, "ci_low": 0.036, "ci_high": 8.26, "scale": "RR"})
    con = C.significance_contradictions(cl, {
        "page": "The pooled RR crosses the null and is compatible with no effect.",
        "manuscript": "The 95% CI spans the null; the result is not statistically significant."})
    assert con == []


def test_absent_claim_asserts_nothing():
    cl = C.derive({"present": False})
    con = C.significance_contradictions(cl, {"page": "significantly reduced everything"})
    assert con == []


def test_claim_check_helper_and_build_gate_fire(monkeypatch):
    """Integration: _claim_check catches a renderer that asserts the opposite of the object,
    and build_review_dir refuses the build. Proves the gate can FAIL (not only pass)."""
    import harness.census as census

    core = {"slug": "x", "title": "t", "question": "q",
            "outcomes": [{"name": "Mortality", "primary": True, "estimand": "RR",
                          "result": {"k": 2, "estimate": 0.55, "ci_low": 0.036, "ci_high": 8.26,
                                     "scale": "RR",
                                     "claim": C.derive({"k": 2, "estimate": 0.55, "ci_low": 0.036,
                                                        "ci_high": 8.26, "scale": "RR"})}}]}
    # canonical says NOT significant; force the outcome's rendered block to assert significance.
    monkeypatch.setattr(census.page, "render_outcome_block",
                        lambda o: "<p>corticosteroids significantly reduced mortality</p>")
    monkeypatch.setattr(census.page, "render_overview", lambda *a, **k: "")
    monkeypatch.setattr(census.page, "render_manuscript", lambda *a, **k: "")
    cc = census._claim_check(core)
    assert cc["claims_checked"] == 1 and len(cc["contradictions"]) == 1

    import pytest
    with pytest.raises(ValueError, match="CLAIM-OBJECT CONTRADICTION"):
        census.build_review_dir(core, {"slug": "x", "declared_method": "m", "served_method": "m",
                                       "comparator": {}}, "F:/claude-temp/claude/_cc_gate_test",
                                 "deadbeef", from_cache=True)
