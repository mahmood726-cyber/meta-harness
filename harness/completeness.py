"""COMPLETENESS, PER OUTCOME: which eligible families could contribute to THIS outcome and why each does not (yet).

The finerenone page said "3 eligible families not pooled => pool incomplete". Two of the three were registrations with
PLANNED completion in 2028/2029 (their lifecycle was misread as 'completed' through a record-identity defect); a trial
that cannot yet report does not make a pool incomplete -- it makes it PROVISIONAL. And a claim about completeness is a
claim about one outcome: a mechanistic trial that reports no kidney events is no gap in the kidney pool.

Per outcome, each eligible family (screened in, awaiting classification, or a known-missing trial not in the inventory):
  ACCEPTED                     pooled for this outcome
  ONGOING                      lifecycle ONGOING / NOT_YET_RECRUITING (a planned completion): cannot yet report
  COMPLETED_AWAITING           completed (or lifecycle unknown/conflicting) with no report of this outcome held yet
  PUBLISHED_NO_TARGET_OUTCOME  a held report that does not report this outcome (retrieved, not reported / not measured)
  REPORTED_UNRESOLVED          reported, but not in a form admitted to the pool (incl. extracted-not-admitted, zero events)
  NOT_YET_RETRIEVED            a report exists that has not been retrieved
  UNRESOLVED_ELIGIBILITY       the family's eligibility itself awaits a decision
The claim: COMPLETE (all ACCEPTED / PUBLISHED_NO_TARGET_OUTCOME), PROVISIONAL (plus ONGOING only), or INCOMPLETE (any
of the other states), naming the families behind it.
"""
from __future__ import annotations

import re
from typing import Any

_GAP = ("COMPLETED_AWAITING", "REPORTED_UNRESOLVED", "NOT_YET_RETRIEVED", "UNRESOLVED_ELIGIBILITY")
_FROM_STATUS = {"ADMITTED": "ACCEPTED", "ADMITTED_PENDING_SIGNATURE": "ACCEPTED",
                "RETRIEVED_NOT_REPORTED": "PUBLISHED_NO_TARGET_OUTCOME", "NOT_MEASURED": "PUBLISHED_NO_TARGET_OUTCOME",
                "REPORTED_UNRESOLVED": "REPORTED_UNRESOLVED", "EXTRACTED_NOT_ADMITTED": "REPORTED_UNRESOLVED",
                "REPORTED_ZERO_EVENTS": "REPORTED_UNRESOLVED", "WITHDRAWN": "REPORTED_UNRESOLVED",
                "NOT_YET_RETRIEVED": "NOT_YET_RETRIEVED",
                # NO_RESULT_YET is deliberately NOT mapped: ONGOING comes from the registry LIFECYCLE itself (checked
                # first in _family_state), one source of truth -- a copied row status never answers for the lifecycle
                # the trial's own collection rules did not ascertain the outcome (SELECT): not a gap, never zero
                "NOT_SYSTEMATICALLY_COLLECTED": "NOT_SYSTEMATICALLY_COLLECTED"}
# a trial that REPORTS at another timepoint than the protocol's (STEP 11 at week 44, STEP 10 at week 52, for a week-68
# question): in the inventory, its result available at its own timepoint -- never 'missing week-68 inputs' (a gap it can
# never close) and never silently pooled as week 68. Declared in docs/timepoint_availability.json with a witness.
from .recovery_map import STATES as RECOVERY_STATES
_FROM_STATUS.update({state: "REPORTED_UNRESOLVED" for state in RECOVERY_STATES})
AVAILABLE_AT_OTHER_TIMEPOINT = "AVAILABLE_AT_OTHER_TIMEPOINT"


def _ids(x) -> set[str]:
    return set(re.findall(r"NCT\d{8}|\b\d{7,8}\b", str(x or "")))


def _family_state(sr: dict[str, Any], rows: list[dict[str, Any]]) -> tuple[str, str]:
    lc = (sr.get("lifecycle") or {}).get("state")
    if lc in ("ONGOING", "NOT_YET_RECRUITING"):
        # it cannot report before its planned completion, whatever its eligibility turns out to be
        comp = ((sr.get("lifecycle") or {}).get("completion_date") or {}).get("value")
        pend = "; eligibility also awaits classification" if sr.get("decision") == "awaiting_classification" else ""
        return "ONGOING", f"lifecycle {lc}, planned completion {comp}{pend}"
    if sr.get("decision") == "awaiting_classification":
        return "UNRESOLVED_ELIGIBILITY", sr.get("rule_id") or "awaiting classification"
    for r in rows:
        ta = r.get("timepoint_availability")
        if ta:
            return AVAILABLE_AT_OTHER_TIMEPOINT, (f"reports at {ta['available']} (protocol timepoint {ta['protocol']}); "
                                                  f"witness: {ta['span']}")
    for r in rows:
        st = (r.get("result_status") or {}).get("state")
        if st in _FROM_STATUS:
            return _FROM_STATUS[st], st
    if str(sr.get("id_type")) == "nct" and not rows:
        return "COMPLETED_AWAITING", f"lifecycle {lc or 'UNKNOWN'}; no report of this outcome held"
    return "COMPLETED_AWAITING", "no row for this outcome"


def build(review: dict[str, Any], known_missing: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    fams = [r for r in (review.get("screening") or {}).get("records") or []
            if r.get("decision") in ("include", "awaiting_classification")]
    out = []
    for o in review.get("outcomes") or []:
        rows = [dict(t, _pooled=True) for t in o.get("trials") or []] + list(o.get("declared_absent_trials") or [])
        fam_states = []
        for sr in fams:
            keys = _ids(sr.get("id")) | _ids(sr.get("trial_family_id"))
            mine = [r for r in rows if _ids(r.get("id")) & keys]
            state, why = ("ACCEPTED", "pooled") if any(r.get("_pooled") for r in mine) else _family_state(sr, mine)
            fam_states.append({"family": sr.get("id"), "state": state, "basis": why})
        for km in known_missing or []:
            decl = str((km.get("per_outcome") or {}).get(o.get("name")) or "")
            state = decl.split(" ")[0] if decl else "NOT_YET_RETRIEVED"
            state = "REPORTED_UNRESOLVED" if state == "EXTRACTED_NOT_ADMITTED" else \
                    "PUBLISHED_NO_TARGET_OUTCOME" if state == "RETRIEVED_NOT_REPORTED" else state
            fam_states.append({"family": f"{km.get('trial')} (known missing: not in the inventory)", "state": state,
                               "basis": decl or "no per-outcome state declared"})
        gaps = [f for f in fam_states if f["state"] in _GAP]
        ongoing = [f for f in fam_states if f["state"] == "ONGOING"]
        claim = "INCOMPLETE" if gaps else ("PROVISIONAL" if ongoing else "COMPLETE")
        out.append({"outcome": o.get("name"), "claim": claim, "families": sorted(fam_states, key=lambda f: str(f["family"])),
                    "statement": (
                        f"{o.get('name')}: " + (
                            "INCOMPLETE -- " + "; ".join(f"{f['family']} {f['state']}" for f in gaps) if gaps else
                            "PROVISIONAL -- complete for every eligible family that can report; still ongoing: "
                            + "; ".join(f"{f['family']} ({f['basis']})" for f in ongoing) if ongoing else
                            "COMPLETE for every eligible family"))})
    return out


def attach_timepoints(review: dict[str, Any], slug: str | None) -> None:
    """Tag each declared trial x outcome with the timepoint it reports at (witness re-verified, fail closed)."""
    import json, os
    from .comparison_family import _verified, _ROOT
    p = os.path.join(_ROOT, "docs", "timepoint_availability.json")
    decl = ((json.load(open(p, encoding="utf-8")).get("topics") or {}).get(slug) or []) if os.path.exists(p) else []
    for d in decl:
        _verified(_ROOT, {"witness": d["witness"]})
        for o in review.get("outcomes") or []:
            if o.get("name") != d["outcome"]:
                continue
            for r in (o.get("declared_absent_trials") or []):
                if _ids(r.get("id")) & _ids(d["trial"]):
                    r["timepoint_availability"] = {"available": d["available"], "protocol": d["protocol"],
                                                   "span": d["witness"]["span"], "why": d.get("why")}


def attach(review: dict[str, Any], slug: str | None) -> None:
    import json, os
    attach_timepoints(review, slug)
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "known_eligible_missing.json")
    km = (json.load(open(p, encoding="utf-8")).get("topics") or {}).get(slug) or [] if os.path.exists(p) else []
    review["completeness_by_outcome"] = build(review, [k for k in km if k.get("per_outcome")])
