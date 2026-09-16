"""Plants for the two integrator edits of 2026-09-16:
- a marker-count decrease refuses unless a signed, count-exact acknowledgement names page, kind and both counts;
- the declared-absent marker survives renaming to a typed absence code (rewording is not loss);
- invalidation.no_checkable_claim does not fire when a declared strand pool carries a claim."""
from harness import honest_ratchet as hr
from harness import invalidation


def _page(n_marker, phrase="not assessed"):
    return "<html><body>" + " ".join(f"<p>{phrase} {i}</p>" for i in range(n_marker)) + "</body></html>"


PAGE = "docs/reviews/x/index.html"


def test_marker_decrease_refuses_without_acknowledgement():
    out = hr.compare(_page(3), _page(2), {"marker_acknowledgements": []}, PAGE)
    assert out == ["not_assessed: base count 3, new count 2"]


def test_marker_decrease_allowed_only_with_exact_signed_entry():
    ack = {"page": PAGE, "kind": "not_assessed", "base_count": 3, "new_count": 2,
           "reason": "8 of 8 trials now rated; the sentence's condition is false", "by": "integrator",
           "when_utc": "2026-09-16T00:00:00Z"}
    assert hr.compare(_page(3), _page(2), {"marker_acknowledgements": [ack]}, PAGE) == []
    # wrong count, wrong page, wrong kind, unsigned: each still refuses
    for bad in (dict(ack, new_count=1), dict(ack, page="docs/reviews/y/index.html"), dict(ack, kind="stale"),
                {k: v for k, v in ack.items() if k != "by"}):
        assert hr.compare(_page(3), _page(2), {"marker_acknowledgements": [bad]}, PAGE) != [], bad


def test_declared_absent_marker_survives_typed_code_rename():
    base = _page(2, "declared absent")
    new = _page(1, "declared absent") + _page(1, "OUTCOME_NOT_IN_SOURCE")
    assert hr.compare(base, new) == []


def test_no_checkable_claim_not_fired_when_a_strand_pool_exists():
    core = {"outcomes": [{"name": "HF hospitalisation", "primary": True,
                          "result": {"present": False, "suppressed_incompatible": True, "estimate": None}}],
            "strands": {"strands": [{"strand": "B", "pool": {"k": 2, "effect": 0.765}}]},
            "search": {}, "screening": {}}
    reasons = invalidation.assess(core) if hasattr(invalidation, "assess") else invalidation.invalidate(core)
    codes = [r["code"] for r in (reasons.get("reasons") if isinstance(reasons, dict) else reasons)]
    assert "no_checkable_claim" not in codes
    core_none = dict(core, strands={"strands": []})
    reasons2 = invalidation.assess(core_none) if hasattr(invalidation, "assess") else invalidation.invalidate(core_none)
    codes2 = [r["code"] for r in (reasons2.get("reasons") if isinstance(reasons2, dict) else reasons2)]
    assert "no_checkable_claim" in codes2
