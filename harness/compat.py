"""Pooling compatibility key.

Two trials may be pooled only when they describe the SAME quantity. Across the harness that
contract is enforced by several separate guards -- estmeasure (effect-measure class), the
composite-component / timepoint / population mismatch checks that declare a divergent trial
absent BEFORE it reaches the pool, and the arm-contrast layer. This module makes the contract
EXPLICIT and auditable: it assembles the one compatibility KEY a pooled outcome satisfies, across
six dimensions, and a backstop that FAILS CLOSED if a pool is ever rendered whose trials do not
share the hard dimensions (defense in depth -- a regression that bypassed an upstream guard would
otherwise pool incompatible quantities silently).

Dimensions:
  effect_measure   : RR/OR/HR vs IRR vs MD -- the reported effect scale (from estmeasure labels)
  event_process    : FIRST_EVENT_RATIO vs RATE vs continuous -- the compatibility CLASS; mixing
                     classes is the hard incompatibility estmeasure already suppresses
  endpoint         : single endpoint vs composite -- a composite pools only a matching component set
  follow_up_window : the outcome's timepoint
  analysis_set     : ITT / mITT / per-protocol -- the analysis population
  randomised_contrast : whether each pooled trial is a registry-confirmed randomised contrast of the
                     intervention of interest (from the arm-contrast layer), reported as verified/total
"""
from . import extract


def _canon_id(label):
    s = str(label or "")
    for pre in ("PMID ", "PMID:", "NCT", "PMC"):
        if s.upper().startswith(pre.upper()):
            return s[len(pre):].strip() or s.strip()
    # "ACRONYM · 12345678" -> take the trailing id token
    return s.split()[-1].strip() if s.split() else s.strip()


def outcome_key(o, core):
    """Assemble the compatibility key for one pooled outcome. Returns None if the outcome is not a
    rendered pool (absent / suppressed / no trials)."""
    res = o.get("result") or {}
    if res.get("present") is False or res.get("suppressed_incompatible") or not res.get("k"):
        return None
    em = res.get("estmeasure") or {}
    classes = em.get("classes") or ([_scale_class(res.get("scale"))] if res.get("scale") else [])
    is_composite = extract.declared_is_composite(o.get("name", "")) if hasattr(extract, "declared_is_composite") else None
    # randomised contrast: fraction of pooled trials the arm-contrast layer confirms as a randomised
    # contrast of the intervention of interest.
    ac = ((core.get("arm_contrast") or {}).get("trials")) or {}
    trials = o.get("trials") or []
    verified = 0
    for t in trials:
        cid = _canon_id(t.get("id") or t.get("label"))
        if (ac.get(cid) or {}).get("status") == "verified":
            verified += 1
    mismatches = []
    if em.get("status") == "incompatible":
        mismatches.append({"dimension": "event_process/effect_measure",
                           "detail": "pooled trials span >1 effect-measure compatibility class: "
                                     + " + ".join(em.get("canonicals", []))})
    return {
        "effect_measure": em.get("labels") or ([res.get("scale")] if res.get("scale") else []),
        "event_process": classes,
        "endpoint": ("composite" if is_composite else "single endpoint") if is_composite is not None else "unclassified",
        "follow_up_window": o.get("timepoint"),
        "analysis_set": o.get("population"),
        "randomised_contrast": {"verified": verified, "total": len(trials)},
        "matched": not mismatches,
        "mismatches": mismatches,
    }


def _scale_class(scale):
    s = (scale or "").upper()
    if s in ("RR", "OR", "HR"):
        return "FIRST_EVENT_RATIO"
    if s in ("IRR", "RATE_RATIO", "RATE_RATIO_RECURRENT"):
        return "RATE"
    if s in ("MD", "SMD"):
        return "CONTINUOUS"
    return "OTHER"


def check(core):
    """Backstop: return the list of pooled outcomes whose compatibility key does NOT match on a
    HARD dimension (an incompatible effect-measure class inside a rendered pool). Empty on a
    well-formed corpus; a non-empty result is a build-refusal condition."""
    bad = []
    for o in (core.get("outcomes") or []):
        k = outcome_key(o, core)
        if k and not k["matched"]:
            bad.append({"outcome": o.get("name"), "mismatches": k["mismatches"]})
    return bad
