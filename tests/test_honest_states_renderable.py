"""Guard: the states that make the corpus honest must survive any template change. Each asserts
the renderer still EMITS the state for a core that should trigger it. A future edit that quietly
drops one fails here."""
import harness.page as P

LABEL_A = "KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH"
LABEL_B = "TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH"
LABEL_C = "HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH"
DISTINCTION = "an auditable screening ledger attached to an unauditable retrieval process"
RETRACTION = "We retract any claim of a registry-first or systematic search for this topic."


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
    assert "canonical review object" in html


def test_known_item_retrieval_state_renderable():
    core = _base(search={"retrieval_class": {
        "class": "KNOWN_ITEM_RETRIEVAL",
        "label": LABEL_A,
        "basis": [{"query": "123[uid]", "kind": "PMID_ENUMERATION"}],
        "screening_auditable": True,
        "retrieval_auditable": False,
        "distinction": DISTINCTION,
        "retraction": RETRACTION,
    }})
    html = P.render_page(core)
    assert LABEL_A in html
    assert DISTINCTION in html
    assert RETRACTION in html
    assert "1 PMID-enumeration queries; 0 title/name-seeded queries" in html


def test_title_seeded_retrieval_state_renderable():
    core = _base(search={"retrieval_class": {
        "class": "TITLE_SEEDED_RETRIEVAL",
        "label": LABEL_B,
        "basis": [{"query": "trial name[Title]", "kind": "TITLE_OR_NAME_SEEDED"}],
        "screening_auditable": True,
        "retrieval_auditable": False,
        "distinction": DISTINCTION,
        "retraction": RETRACTION,
    }})
    html = P.render_page(core)
    assert LABEL_B in html
    assert DISTINCTION in html
    assert RETRACTION in html
    assert "0 PMID-enumeration queries; 1 title/name-seeded queries" in html


def test_hand_written_keyword_retrieval_state_renderable():
    core = _base(search={"retrieval_class": {
        "class": "HAND_WRITTEN_KEYWORD_SEARCH",
        "label": LABEL_C,
        "basis": [{"query": "drug disease randomized placebo", "kind": "FREE_TEXT_KEYWORD", "features": []}],
        "screening_auditable": True,
        "retrieval_auditable": False,
        "distinction": DISTINCTION,
        "retraction": RETRACTION,
    }})
    html = P.render_page(core)
    assert LABEL_C in html
    assert DISTINCTION in html
    assert RETRACTION in html
    assert "0 PMID-enumeration queries; 0 title/name-seeded queries; 1 free-text keyword queries" in html


def test_concept_search_does_not_render_retrieval_warning():
    core = _base(search={"retrieval_class": {
        "class": "CONCEPT_SEARCH",
        "label": "CONCEPT SEARCH — registered P/I/C query, full pagination",
        "basis": [{"query": "condition AND drug", "kind": "CONCEPT"}],
        "screening_auditable": True,
        "retrieval_auditable": True,
    }})
    html = P.render_page(core)
    assert LABEL_A not in html
    assert LABEL_B not in html
    assert LABEL_C not in html
    assert DISTINCTION not in html
    assert RETRACTION not in html


def test_claims_checked_zero_is_a_limitation():
    core = _base()
    core["reproduction"]["claim_check"] = {"claims_checked": 0, "contradictions": []}
    html = P.render_page(core)
    assert "No checkable pooled claim" in html and "Claims checked: 0" in html


def test_never_considered_renderable():
    core = _base(never_considered=[{"trial": "J-EMPHASIS-HF", "nct": "NCT01115855"}])
    html = P.render_page(core)
    assert "Never considered" in html and "J-EMPHASIS-HF" in html


def test_stale_marking_renderable():
    # A STALE verdict must poison the headline visibly. "silence about a limitation counts as a
    # regression" (external auditor): a template change that drops the STALE banner fails here.
    core = _base(invalidation={"stale": True,
                               "reasons": [{"code": "known_eligible_missing", "detail": "trial X eligible, not pooled"}]})
    html = P.render_page(core)
    assert "STALE" in html and "not current" in html


def test_engine_provenance_claim_is_visible_and_qualified():
    # The engine-validation claim must be rendered AND honestly qualified (canonical path, not every
    # pathway). A reader/auditor must be able to see the gate exists from the rendered surface.
    from harness.synth import METHOD_RATIO
    assert "canonical code path" in METHOD_RATIO and "gate-checked to originate here" in METHOD_RATIO


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
