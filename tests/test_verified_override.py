"""The hand-verified endpoint-correction override (verified_effects entry flagged override:true) must
BEAT the abstract for that trial+outcome, while an UNFLAGGED verified_effects entry stays a pure fallback.
This is the ORIGIN (PMID 22686415) fix: the abstract's 'primary outcome' is death from cardiovascular
causes (HR 0.98) but our outcome is major vascular events (HR 1.01). Uses ORIGIN's REAL cached abstract so
the test exercises the actual mis-selection the override corrects."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import pipeline  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CFG = json.load(open(os.path.join(ROOT, "topics", "omega3-cardiovascular-events.json"), encoding="utf-8"))
_RECS = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "cache", "omega3-cardiovascular-events",
         "records.json"), encoding="utf-8")).get("records", [])}
_SPEC = _CFG["primary_outcome"]
_INC = [{"id": "22686415", "id_type": "pmid", "label": "ORIGIN"}]
_INTERV = _CFG.get("intervention_terms", ["n-3", "fatty acid"])
_COMP = _CFG.get("comparator_terms", ["placebo", "control"])


def _origin_outcome(verified_effects):
    return pipeline._build_outcome(_SPEC, "efficacy", _INC, _RECS, _INTERV, _COMP,
                                   verified_effects=verified_effects)


def _origin_effect(verified_effects):
    o = _origin_outcome(verified_effects)
    t = [x for x in o["trials"] if x["id"] == "PMID 22686415"]
    return t[0].get("effect") if t else None


def _origin_refusal(verified_effects):
    o = _origin_outcome(verified_effects)
    return next((a for a in o.get("declared_absent_trials") or [] if a["id"] == "PMID 22686415"), None)


def test_without_override_the_wrong_endpoint_is_refused_not_pooled():
    # The real bug: no override -> the generic 'primary outcome' anchor grabs ORIGIN's CV-death primary 0.98.
    # Since the endpoint-span binding landing (2026-09-18) that number is bound to its own definition span
    # (death from cardiovascular causes = one component of major vascular events) and REFUSED with the
    # refused number shown -- never pooled under the composite label. (Before that landing this test
    # asserted `== 0.98`, i.e. it pinned the defect as the expected behaviour.)
    assert _origin_effect(None) is None
    refusal = _origin_refusal(None)
    assert refusal is not None
    assert refusal.get("refused_effect", {}).get("effect") == 0.98
    assert "cardiovascular death" in json.dumps(refusal).lower() or "component" in json.dumps(refusal).lower()


def test_override_beats_the_abstract_route_but_is_bound_to_held_bytes_or_set_aside():
    """The override BEATS the abstract's wrong-endpoint decision (0.98 is no longer the refusal), and the
    override's own number is then bound to held bytes like any hand row: ORIGIN's held abstract names 'major
    vascular events' but never defines it, and the spec's components derive from its name, so the row is set
    aside as ENDPOINT_UNBOUND with 1.01 visible as the candidate -- never pooled on its hand-written source
    string (which is what this test asserted before M2, 2026-09-20)."""
    ve = {"22686415": {"outcome": _SPEC["name"], "override": True, "effect": 1.01, "ci_low": 0.93,
                       "ci_high": 1.1, "scale": "HR", "provenance": "fulltext_verified",
                       "source": "ORIGIN abstract: ... major vascular events ... hazard ratio, 1.01 ..."}}
    assert _origin_effect(ve) is None
    refusal = _origin_refusal(ve)
    assert refusal is not None and refusal["reason_code"] == "ENDPOINT_UNBOUND"
    assert refusal["candidate_tuple"]["effect"] == 1.01
    assert refusal.get("refused_effect", {}).get("effect") != 0.98


def test_unflagged_verified_effect_does_not_override():
    ve = {"22686415": {"outcome": _SPEC["name"], "effect": 1.01, "scale": "HR"}}  # no override flag
    # an UNFLAGGED verified_effect is a fallback for an abstract that yields NOTHING; it never replaces
    # what the abstract route decided. Here the abstract route decides a typed refusal (wrong endpoint),
    # so the unflagged entry is not pooled either: neither 0.98 (wrong endpoint) nor 1.01 (unauthorised).
    assert _origin_effect(ve) is None, "an UNFLAGGED verified_effect must not override the abstract route"
    assert _origin_refusal(ve) is not None


def test_verified_arms_override_beats_abstract():
    """The override flag also works on verified_arms (count corrections), symmetric with verified_effects.
    probiotics 15740542: the abstract yields the ANY-diarrhoea RR 0.3; the override pins the AAD counts
    4/119 vs 22/127 (RR 0.19). Without the flag, an entry must NOT override."""
    from harness import pipeline
    import json as _j, os as _o
    recs = {r["id"]: r for r in _j.load(open(_o.path.join(ROOT, "cache", "probiotics-aad-prevention",
            "records.json"), encoding="utf-8")).get("records", [])}
    spec = {"name": "Antibiotic-associated diarrhoea", "keywords": ["antibiotic-associated diarrh",
            "antibiotic associated diarrh", "AAD", "diarrh"], "estimand": "RR"}
    inc = [{"id": "15740542", "id_type": "pmid", "label": "Can 2006"}]
    va = {"15740542": {"outcome": spec["name"], "override": True, "ai": 4, "n1i": 119, "ci": 22, "n2i": 127,
                       "provenance": "aact_verified", "source": "Can 2006: AAD 4/119 vs 22/127 (RR 0.2)"}}
    o = pipeline._build_outcome(spec, "efficacy", inc, recs, ["probiotic", "boulardii", "saccharomyces"],
                                ["placebo", "control"], verified_arms=va)
    t = [x for x in o["trials"] if x["id"] == "PMID 15740542"][0]
    assert t.get("ai") == 4 and t.get("n1i") == 119 and t.get("ci") == 22, f"arms override failed: {t}"
    # unflagged verified_arms must NOT override (stays a fallback)
    va2 = {"15740542": {k: v for k, v in va["15740542"].items() if k != "override"}}
    o2 = pipeline._build_outcome(spec, "efficacy", inc, recs, ["probiotic", "boulardii", "saccharomyces"],
                                 ["placebo", "control"], verified_arms=va2)
    t2 = [x for x in o2["trials"] if x["id"] == "PMID 15740542"][0]
    assert t2.get("ai") != 4, "an UNFLAGGED verified_arms entry must not override the abstract"
