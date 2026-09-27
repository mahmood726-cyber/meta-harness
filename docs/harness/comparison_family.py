"""COMPARISON FAMILIES: one registration, several randomised COMPARISONS, each with its own population, comparator and
eligibility -- a platform's DOMAINS (REMAP-CAP: the non-pandemic corticosteroid domain and the COVID-19 corticosteroid
domain) or a trial's RECRUITMENT PERIODS whose comparator changed mid-trial (COVIDICUS: high-dose dexamethasone vs
placebo, then vs standard-dose dexamethasone after the September 2020 amendment).

A registration's condition labels list EVERY comparison's population ('Community-acquired Pneumonia, Influenza,
COVID-19'), so screening a comparison against them judges one domain by another's population. Here:
  * a DECLARED family (docs/comparison_families.json) is screened per comparison, on that comparison's own witnessed
    population, exclusions, strata, comparator and timepoint -- each witness re-hashed and its span required, or the
    family FAILS CLOSED;
      - a protocol-excluded population term the comparison itself EXCLUDES (REMAP-CAP non-pandemic domain: 'known or
        presumed COVID-19' is an exclusion criterion) is not a veto;
      - one it randomises as a STRATUM (influenza Y/N) is a pending decision, not a silent inclusion or exclusion;
      - an active comparator of the intervention itself (standard-dose dexamethasone) is outside a placebo/usual-care
        protocol for that comparison only;
      - a timepoint off the protocol's, or a Bayesian/adjusted-only estimate, is a pending decision;
    the registration's decision is the best comparison's: ELIGIBLE -> include; UNRESOLVED -> awaiting classification
    (with the pending decisions named); INELIGIBLE everywhere -> exclude, with each comparison's own reason;
  * an UNDECLARED platform registration may be vetoed only on its own TITLE; otherwise it awaits classification
    (its domains are not known, and its condition labels are not evidence about any one of them);
  * a result pooled for a multi-comparison family must name its comparison; a whole-trial result that spans
    comparisons with different comparators is never pooled.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from .report_family import _witness_text

PATH = os.path.join("docs", "comparison_families.json")
ELIGIBLE, UNRESOLVED, INELIGIBLE = "ELIGIBLE", "UNRESOLVED", "INELIGIBLE"
AWAITING = "awaiting_classification"
PLATFORM_TITLE = re.compile(r"\bplatform\b|\bREMAP\b|multi-?arm,? multi-?stage|\bMAMS\b|master protocol|"
                            r"\bumbrella trial|\bbasket trial|multifactorial adaptive", re.I)
_RANK = {ELIGIBLE: 0, UNRESOLVED: 1, INELIGIBLE: 2}
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(root: str = _ROOT) -> list[dict[str, Any]]:
    p = os.path.join(root, PATH)
    return list((json.load(open(p, encoding="utf-8")) or {}).get("families") or []) if os.path.exists(p) else []


def _verified(root: str, field: dict[str, Any] | None) -> dict[str, Any] | None:
    """A declared field whose witness span is present in the held bytes (else ValueError: fail closed). The span IS
    the field's text: nothing but the witnessed words is ever judged, so a declaration cannot add a term."""
    if not field:
        return None
    w = field.get("witness")
    if not w:
        raise ValueError(f"comparison-family field without a witness: {field}")
    span = re.sub(r"\s+", " ", w["span"])
    if span not in _witness_text(root, w):
        raise ValueError(f"comparison-family witness span not in {w['path']}: {span!r}")
    return {**field, "text": span}


def _active(text: str, agents) -> list[str]:
    """Intervention agents NAMED AS GIVEN in a comparator ('standard dexamethasone'), not negated ('no corticosteroid')."""
    return [a for a in _terms_in(text, agents)
            if not re.search(r"\b(?:no|without|non-?)\s*" + re.escape(a.lower()), (text or "").lower())]


def _terms_in(text: str, terms) -> list[str]:
    t = (text or "").lower()
    return [x for x in (terms or []) if re.search(r"(?<![a-z])" + re.escape(x.lower()) + r"(?![a-z])", t)]


def _days(s: str | None) -> tuple[int, int] | None:
    """'28 days' -> (28, 28); '30-day or in-hospital' -> (30, 30); '28-30 days' -> (28, 30); None if no day count."""
    s = s or ""
    m = re.search(r"(\d{1,3})\s*[-–]\s*(\d{1,3})\s*-?\s*days?", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    nums = [int(x) for x in re.findall(r"(\d{1,3})\s*-?\s*days?\b", s)] + [int(x) for x in re.findall(r"\bday\s*(\d{1,3})", s)]
    return (min(nums), max(nums)) if nums else None


def evaluate(root: str, comp: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """One comparison judged against one topic's protocol, on the comparison's own witnessed fields only."""
    inc = config.get("include") or {}
    pop = _verified(root, comp.get("population")) or {}
    cmp_ = _verified(root, comp.get("comparator")) or {}
    for f in ("intervention", "arms", "primary_timepoint", "estimate", "crude_counts"):
        _verified(root, comp.get(f))
    excls = [_verified(root, f) for f in comp.get("population_exclusions") or []]
    strata = [_verified(root, f) for f in comp.get("population_strata") or []]
    fails, pending, pool_pending = [], [], []
    pa = list(inc.get("population_any") or []) + list(inc.get("population_any_extra") or [])
    if pa and not _terms_in(pop.get("text"), pa):
        fails.append({"rule": "X2", "why": f"the comparison's population ({pop.get('text')!r}) names none of {pa}"})
    excl_text = " ".join(f["text"] for f in excls)
    strata_text = " ".join(f["text"] for f in strata)
    for term in inc.get("population_none") or []:
        if _terms_in(pop.get("text"), [term]):
            fails.append({"rule": "X2", "why": f"the comparison's own population names {term!r}"})
        elif _terms_in(excl_text, [term]):
            continue      # the comparison itself EXCLUDES it: agrees with the protocol, never a veto
        elif _terms_in(strata_text, [term]):
            pending.append({"decision": "MIXED_POPULATION_STRATUM", "term": term,
                            "detail": (f"the protocol excludes {term!r}; this comparison randomises it as a stratum "
                                       f"({strata_text!r}): include the comparison, include only the other stratum, "
                                       "or exclude it -- undecided")})
    ca = list(inc.get("comparator_any") or []) + list(inc.get("comparator_any_extra") or [])
    active = _active(cmp_.get("text"), config.get("intervention_agents") or inc.get("intervention_any") or [])
    if active:
        fails.append({"rule": "X3", "why": (f"comparator {cmp_.get('text')!r} is an active dose of the intervention "
                                            f"({', '.join(active)}), not {ca}")})
    elif cmp_ and ca and not _terms_in(cmp_.get("text"), ca):      # no witnessed comparator: not assessed, not failed
        fails.append({"rule": "X3", "why": f"comparator {cmp_.get('text')!r} is none of {ca}"})
    prim = config.get("primary_outcome") or {}
    want = _days(prim.get("timepoint"))
    tp = comp.get("primary_timepoint") or {}
    if tp and (_days((_verified(root, tp) or {}).get("text")) or (None,))[0] != tp.get("days"):
        raise ValueError(f"{comp['comparison_id']}: declared primary timepoint {tp.get('days')} days is not what its "
                         f"witnessed span states ({tp['witness']['span']!r})")
    # PRIMARY-POOL questions (not eligibility): the timepoint and the estimate the protocol admits
    if want and tp.get("days") and not (want[0] <= tp["days"] <= want[1]):
        pool_pending.append({"decision": "TIMEPOINT", "detail": (f"the comparison's primary result is at day "
                                                                   f"{tp['days']} ({(_verified(root, tp) or {}).get('text')!r}); "
                                                                   f"the protocol's primary timepoint is "
                                                                   f"{prim.get('timepoint')!r}; no window policy admits it")})
    est = comp.get("estimate") or {}
    if est.get("kind") in ("BAYESIAN_ADJUSTED", "ADJUSTED_ONLY"):
        pool_pending.append({"decision": "ADJUSTED_ESTIMATE", "detail": (
            f"reported estimate: {(_verified(root, est) or {}).get('text')!r}; crude counts: "
            f"{(_verified(root, comp.get('crude_counts')) or {}).get('text')!r} -- which the protocol admits is undecided")})
    state = INELIGIBLE if fails else (UNRESOLVED if pending else ELIGIBLE)
    pool = INELIGIBLE if fails else (UNRESOLVED if (pending or pool_pending) else ELIGIBLE)
    return {"comparison_id": comp["comparison_id"], "kind": comp.get("kind"), "reports": comp.get("reports") or [],
            "population": pop.get("text"), "comparator": cmp_.get("text"),
            "arms": {k: v for k, v in (comp.get("arms") or {}).items() if k != "witness"},
            "eligibility": state, "fails": fails, "pending_decisions": pending,
            "primary_pool_eligibility": pool, "primary_pool_pending": pending + pool_pending,
            "result_state": (comp.get("result") or {}).get("state"),
            "result_basis": (comp.get("result") or {}).get("basis")}


def _family_for(rec: dict[str, Any], fams: list[dict[str, Any]]) -> dict[str, Any] | None:
    keys = {str(rec.get("id") or ""), str(rec.get("nct") or "")}
    return next((f for f in fams if f.get("registration") in keys), None)


def screen_registration(rec: dict[str, Any], config: dict[str, Any], root: str = _ROOT) -> dict[str, Any] | None:
    """The comparison-level screening of a registration record, or None when it is not a comparison family."""
    if rec.get("id_type") != "nct":
        return None
    fam = _family_for(rec, load(root))
    if fam:
        comps = [evaluate(root, c, config) for c in fam.get("comparisons") or []]
        best = min(comps, key=lambda c: _RANK[c["eligibility"]])
        label = fam.get("label") or rec.get("id")
        if best["eligibility"] == ELIGIBLE:
            dec, rule = "include", "INCLUDE"
            reason = (f"{label}: comparison {best['comparison_id']} is eligible on its own population and comparator "
                      f"(the other comparisons are judged separately below).")
        elif best["eligibility"] == UNRESOLVED:
            dec, rule = AWAITING, "A-COMPARISON-UNRESOLVED"
            reason = (f"{label}: comparison {best['comparison_id']} passes population and comparator on its own "
                      "terms; primary-pool eligibility UNRESOLVED pending: "
                      + "; ".join(p["decision"] for p in best["primary_pool_pending"]) + ".")
        else:
            dec, rule = "exclude", best["fails"][0]["rule"]
            reason = f"{label}: no comparison is eligible -- " + "; ".join(
                f"{c['comparison_id']}: {c['fails'][0]['why']}" for c in comps) + "."
        span = (best.get("population") or rec.get("title") or "")[:160]
        return {"decision": dec, "rule_id": rule, "reason": reason, "span": span, "comparisons": comps,
                "family_id": fam["family_id"], "pending": best["primary_pool_pending"] if dec == AWAITING else []}
    return None


def is_undeclared_platform(rec: dict[str, Any], root: str = _ROOT) -> bool:
    """A registration whose own title/acronym says it is a platform, with no declared comparison family."""
    return (rec.get("id_type") == "nct" and _family_for(rec, load(root)) is None
            and bool(PLATFORM_TITLE.search(f"{rec.get('title') or ''} {rec.get('acronym') or ''}")))


def undeclared_platform_population(rec: dict[str, Any], decision: tuple, config: dict[str, Any]) -> dict[str, Any] | None:
    """For an undeclared platform screened WITHOUT its condition labels: a population failure its own title does not
    settle awaits classification (its domains' populations are unknown). A title-level population veto, and every
    design / intervention / comparator rule, stand as screened. Returns the replacement row fields, or None."""
    dec, rule, reason, span = decision
    if rule != "X2":
        return None
    if _terms_in(rec.get("title"), (config.get("include") or {}).get("population_none")):
        return None
    return {"decision": AWAITING, "rule_id": "A-PLATFORM-DOMAINS-UNDECLARED", "span": (rec.get("title") or "")[:160],
            "reason": ("platform registration with undeclared domains: its title does not settle the population "
                       f"({reason}), and its condition labels list every domain's population, so it is screened "
                       "neither in nor out on them; awaiting classification."),
            "pending": [{"decision": "DECLARE_DOMAINS", "detail": ("declare the platform's domains so each is screened "
                                                                  "on its own population")}]}


def attach(review: dict[str, Any]) -> None:
    """review['comparison_families']: the per-comparison screening carried on each registration's ledger row."""
    out = []
    for r in ((review.get("screening") or {}).get("records") or []):
        if r.get("comparisons"):
            out.append({"registration": r.get("id"), "decision": r.get("decision"), "rule_id": r.get("rule_id"),
                        "comparisons": r["comparisons"], "pending_decisions": r.get("pending_decisions") or []})
    if out:
        review["comparison_families"] = out


def hold_whole_trial(slug: str | None, outcome_name: str, trials: list[dict[str, Any]], root: str = _ROOT):
    """A pooled row of a multi-comparison family must name its comparison; a whole-trial row is held out."""
    fams = {f["registration"]: f for f in load(root) if len(f.get("comparisons") or []) > 1}
    if not fams:
        return trials, []
    keep, absent = [], []
    for t in trials:
        m = re.search(r"NCT\d{8}", str(t.get("id")) + " " + str(t.get("nct") or ""))
        fam = fams.get(m.group(0)) if m else None
        if fam and not t.get("comparison_id"):
            absent.append({"id": t.get("id"), "reason_code": "WHOLE_TRIAL_ACROSS_COMPARISONS",
                           "state": "WHOLE_TRIAL_ACROSS_COMPARISONS",
                           "reason": (f"{fam.get('label')}: a whole-trial result spans comparisons with different "
                                      "comparators (" + "; ".join(c["comparison_id"] for c in fam["comparisons"])
                                      + "); only a comparison-level result can be pooled."),
                           "held_out_row": {k: t.get(k) for k in ("ai", "n1i", "ci", "n2i", "effect", "ci_low",
                                                                  "ci_high") if t.get(k) is not None}})
        else:
            keep.append(t)
    return keep, absent
