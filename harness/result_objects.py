"""ONE RESULT OBJECT ACROSS ANALYSES (PCSK9 review, 2026-09-27; retrospective, Dispatch under Mahmood's delegation).

VESALIUS-CV's 3-point MACE result -- HR 0.75 (0.65 to 0.86), the sentence "A 3-point MACE event occurred in 336 patients ... (hazard
ratio, 0.75; 95% confidence interval [CI], 0.65 to 0.86)" -- is REFUSED by the page's main MACE pool (NEAR_MATCH without a
declared near-match permission: "lacks ... cardiovascular death") and ADMITTED by the supplemental strict 3-point strand, which
pools it with FOURIER (0.784243, 0.473854 to 1.297945). The same source-bound result, two contradictory admission decisions, and
no recorded reason why the strand's requirements differ.

A result object is identified by its trial, measure, point estimate and interval. Every analysis on the page records its decision
about the object against that identity, with its OWN additional compatibility requirements. The consistency check fails when an
object is ADMITTED in one analysis and REFUSED in another, unless the admitting analysis DECLARES that it waives the other's
refusal reason (`requirements.waives: [reason_code, ...]` with a stated `because`). An undeclared difference is a contradiction.
"""
from __future__ import annotations

from typing import Any

ADMITTED, REFUSED = "ADMITTED", "REFUSED"


def _num(x):
    try:
        return round(float(x), 4)
    except (TypeError, ValueError):
        return None


def _trial(x: Any) -> str:
    return str(x or "").split(" · ")[-1].replace("PMID ", "").strip()


def result_id(trial: Any, scale: Any, effect: Any, lo: Any, hi: Any) -> str | None:
    e, a, b = _num(effect), _num(lo), _num(hi)
    if e is None or a is None or b is None:
        return None
    return f"{_trial(trial)}|{str(scale or '').upper()}|{e}|{a}|{b}"


def ledger(review: dict[str, Any]) -> list[dict[str, Any]]:
    """Every admission decision on the page about a source-bound effect result, keyed by result_id."""
    out = []
    for o in review.get("outcomes") or []:
        analysis = f"outcome:{o.get('name')}"
        req = {"declared": "the outcome's main pool (topic eligibility, endpoint identity and admissibility gates)"}
        for t in o.get("trials") or []:
            rid = result_id(t.get("id"), t.get("scale"), t.get("effect"), t.get("ci_low"), t.get("ci_high"))
            if rid:
                out.append({"result_id": rid, "analysis": analysis, "decision": ADMITTED, "requirements": req})
        for a in o.get("declared_absent_trials") or []:
            rf = a.get("refused_effect") or {}
            rid = result_id(a.get("id"), rf.get("scale"), rf.get("effect"), rf.get("ci_low"), rf.get("ci_high"))
            if rid:
                out.append({"result_id": rid, "analysis": analysis, "decision": REFUSED, "requirements": req,
                            "reason_code": a.get("reason_code") or a.get("endpoint_admissibility") or a.get("state"),
                            "target_endpoint_class": a.get("target_endpoint_class"), "reason": a.get("reason")})
    for s in (review.get("strands") or {}).get("strands") or []:
        analysis = f"strand:{s.get('id')}"
        req = dict(s.get("requirements") or {})
        req.setdefault("declared", s.get("endpoint"))
        for m in s.get("members") or []:
            rid = result_id(m.get("pmid") or m.get("trial"), m.get("scale") or s.get("effect_measure"),
                            m.get("effect"), m.get("ci_low"), m.get("ci_high"))
            if rid:
                out.append({"result_id": rid, "analysis": analysis, "decision": ADMITTED, "requirements": req,
                            "label": m.get("trial")})
        for d in s.get("declared_absent") or []:
            rf = d.get("refused_effect") or d
            rid = result_id(d.get("pmid") or d.get("trial"), rf.get("scale") or s.get("effect_measure"), rf.get("effect"),
                            rf.get("ci_low"), rf.get("ci_high"))
            if rid:
                out.append({"result_id": rid, "analysis": analysis, "decision": REFUSED, "requirements": req,
                            "reason_code": d.get("reason_code") or d.get("state"), "reason": d.get("reason")})
    return out


def consistency(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Contradictions: the same result ADMITTED in one analysis and REFUSED in another, with no declared waiver of the refusal."""
    by: dict[str, list[dict[str, Any]]] = {}
    for e in entries:
        by.setdefault(e["result_id"], []).append(e)
    contradictions, explained = [], []
    for rid, es in by.items():
        adm = [e for e in es if e["decision"] == ADMITTED]
        ref = [e for e in es if e["decision"] == REFUSED]
        for a in adm:
            for r in ref:
                if a["analysis"] == r["analysis"]:
                    continue
                waived = set((a.get("requirements") or {}).get("waives") or [])
                rec = {"result_id": rid, "admitted_in": a["analysis"], "refused_in": r["analysis"],
                       "refusal_code": r.get("reason_code"), "refusal_reason": r.get("reason"),
                       "admitting_requirements": a.get("requirements")}
                if r.get("reason_code") in waived:
                    explained.append({**rec, "because": (a.get("requirements") or {}).get("because")})
                else:
                    contradictions.append(rec)
    return {"objects": len(by), "shared": sum(1 for es in by.values() if len({e['analysis'] for e in es}) > 1),
            "contradictions": contradictions, "explained_differences": explained,
            "state": "CONTRADICTORY_ADMISSION" if contradictions else "CONSISTENT"}
