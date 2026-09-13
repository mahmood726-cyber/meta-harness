"""Guard: the states that make the corpus honest must survive any template change. Each asserts
the renderer still EMITS the state for a core that should trigger it. A future edit that quietly
drops one fails here."""
import harness.page as P


def _base(**kw):
    core = {"title": "T", "question": "Q", "slug": "s",
            "outcomes": [{"name": "O", "primary": True, "kind": "efficacy",
                          "result": {"present": False, "reason": "none"}}],
            "reproduction": {"review_sha256": "abc123def456abcd", "protocol_sha": "x"}}
    core.update(kw)
    return core


def test_pinned_audit_identity_renderable():
    html = P.render_page(_base())
    assert "Pinned audit identity" in html and "abc123def456abcd"[:16] in html


def test_claims_checked_zero_is_a_limitation():
    core = _base()
    core["reproduction"]["claim_check"] = {"claims_checked": 0, "contradictions": []}
    html = P.render_page(core)
    assert "No checkable pooled claim" in html and "Claims checked: 0" in html


def test_never_considered_renderable():
    core = _base(never_considered=[{"trial": "J-EMPHASIS-HF", "nct": "NCT01115855"}])
    html = P.render_page(core)
    assert "Never considered" in html and "J-EMPHASIS-HF" in html


def test_suppressed_counterfactual_renderable():
    core = _base()
    core["outcomes"] = [{"name": "O", "primary": True, "kind": "efficacy",
                         "result": {"suppressed_incompatible": True, "k": 2,
                                    "suppressed_reason": "mixed classes",
                                    "estmeasure": {"canonicals": ["RISK_RATIO", "INCIDENCE_RATE_RATIO"]},
                                    "counterfactual": {"reason_code": "INCOMPATIBLE_ESTIMANDS",
                                                       "would_be_estimate": 0.61, "would_be_ci_low": 0.01,
                                                       "would_be_ci_high": 51.59}}}]
    html = P.render_page(core)
    assert "INCOMPATIBLE_ESTIMANDS" in html and "would have been" in html
