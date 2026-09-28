"""The interval level of a served effect+CI row, typed from the held REGISTRY analysis that reports the same tuple
(lane NR V1.0.1, NR-C13). EMPEROR-Preserved's abstract prints '95% CI' for HR 0.79 (0.69-0.90); the registered primary
analysis states 95.03% (alpha-adjusted). The level is carried as the typed ci_pct with its basis, the SE is derived at
it, and the verifier re-derives it from the same held data (scripts/verify_bundle.py registry_ci_level)."""
from __future__ import annotations


def registry_ci_level(record, scale, effect, ci_low, ci_high, ctgov_results=None):
    """Bind a served tuple to held analyses; decimal equality, never rounding."""
    from decimal import Decimal, InvalidOperation

    aliases = {
        "hr": "HR", "hazard ratio": "HR", "hazard ratio (hr)": "HR",
        "rr": "RR", "risk ratio": "RR", "risk ratio (rr)": "RR",
        "relative risk": "RR", "relative risk (rr)": "RR",
        "or": "OR", "odds ratio": "OR", "odds ratio (or)": "OR",
        "irr": "IRR", "rate ratio": "IRR", "rate_ratio": "IRR",
        "incidence rate ratio": "IRR", "incidence rate ratio (irr)": "IRR",
    }

    def decimal(value):
        try:
            number = Decimal(str(value))
            return number if number.is_finite() else None
        except (InvalidOperation, ValueError):
            return None

    wanted_scale = aliases.get(str(scale).strip().lower())
    wanted = tuple(decimal(v) for v in (effect, ci_low, ci_high))
    if not wanted_scale or None in wanted:
        return None
    if not (0 < wanted[1] <= wanted[0] <= wanted[2] and wanted[1] < wanted[2]):
        return None
    nct = (record or {}).get("nct")
    outcomes = (ctgov_results or {}).get(nct) if isinstance(nct, str) else None
    if not isinstance(outcomes, list):
        return None
    matches = []
    levels = set()
    for outcome in outcomes:
        if not isinstance(outcome, dict):
            return None
        for index, analysis in enumerate(outcome.get("analyses") or []):
            if not isinstance(analysis, dict):
                return None
            if aliases.get(str(analysis.get("paramType")).strip().lower()) != wanted_scale:
                continue
            values = tuple(decimal(analysis.get(k)) for k in
                           ("paramValue", "ciLowerLimit", "ciUpperLimit"))
            if values != wanted:
                continue
            pct = decimal(analysis.get("ciPctValue"))
            if pct is None or not 0 < pct < 100:
                return None
            levels.add(pct)
            group = str(analysis.get("groupDescription") or "").strip()
            span = (
                (f"{group}: " if group else "")
                + f"{analysis['paramType']} {analysis['paramValue']} "
                + f"({analysis['ciPctValue']}% CI {analysis['ciLowerLimit']} to "
                + f"{analysis['ciUpperLimit']}; {analysis.get('statisticalMethod') or 'method not stated'})"
            )
            matches.append({"source": "ClinicalTrials.gov results analysis",
                            "nct_id": nct, "outcome_title": outcome.get("title"),
                            "analysis_index": index, "span": span})
    if not matches or len(levels) != 1:
        return None
    # Source order selects only the citation; every matching analysis agrees.
    return {"ci_pct": float(next(iter(levels))), "basis": matches[0]}
