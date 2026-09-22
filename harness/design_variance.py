"""Design-aware variance consumption helpers.

This module sits beside ``harness.synth``.  The synthesis engine still refuses a
naive reconstructed cluster/crossover SE; this layer only supplies a consumable
study when a source-backed design variance is available.
"""
from __future__ import annotations

import copy
import math
import re
from typing import Any

from scipy.stats import norm as _norm

from . import design_key


ENGINE_CANNOT_CONSUME = "ENGINE_CANNOT_CONSUME"
MISSING_DESIGN_VARIANCE = "design_adjusted_effect|ICC"
ENGINE_ABSENT_KIND = "engine_cannot_consume"
DESIGN_VARIANCE_METHOD = "ICC_DESIGN_EFFECT"


def _num(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _trial_key(value: Any) -> str:
    text = str(value or "").strip()
    if text.upper().startswith("PMID "):
        return text.split()[-1]
    if text.upper().startswith("PMID:"):
        return text.split(":", 1)[1].strip()
    m = re.search(r"\b(\d{7,9})\b", text)
    if m:
        return m.group(1)
    m = re.search(r"\bNCT\d{8}\b", text, flags=re.I)
    if m:
        return m.group(0).upper()
    return text


def design_effect(cluster_size: Any, icc: Any) -> float:
    """Closed-form design effect for equal-size clusters: 1 + (m - 1) * ICC."""

    m = _num(cluster_size)
    rho = _num(icc)
    if m is None or rho is None or m <= 0 or rho < 0:
        raise ValueError("ICC_DESIGN_EFFECT requires positive cluster_size and non-negative ICC")
    return 1.0 + (m - 1.0) * rho


def raw_log_effect_variance(trial: dict[str, Any], measure: str | None = None) -> tuple[float, float]:
    """Return the ordinary reconstructed log effect and variance for a binary row."""

    a = _num(trial.get("ai"))
    n1 = _num(trial.get("n1i"))
    c = _num(trial.get("ci"))
    n2 = _num(trial.get("n2i"))
    if None in (a, n1, c, n2) or not n1 or not n2:
        raise ValueError("raw 2x2 reconstruction requires ai, n1i, ci and n2i")
    if min(a, c, n1 - a, n2 - c) == 0:
        a, c, n1, n2 = a + 0.5, c + 0.5, n1 + 1.0, n2 + 1.0
    if (measure or trial.get("measure") or trial.get("scale") or "RR").upper() == "OR":
        b, d = n1 - a, n2 - c
        return math.log((a * d) / (b * c)), 1.0 / a + 1.0 / b + 1.0 / c + 1.0 / d
    return math.log((a / n1) / (c / n2)), 1.0 / a - 1.0 / n1 + 1.0 / c - 1.0 / n2


def inflated_log_effect_variance(trial: dict[str, Any], measure: str | None = None) -> tuple[float, float]:
    adj = trial.get("design_adjustment") or {}
    if adj.get("kind") != DESIGN_VARIANCE_METHOD:
        raise ValueError("only ICC_DESIGN_EFFECT can inflate a reconstructed 2x2 variance here")
    yi, vi = raw_log_effect_variance(trial, measure)
    m = adj.get("cluster_size") or adj.get("average_cluster_size") or adj.get("m")
    de = design_effect(m, adj.get("icc"))
    return yi, vi * de


def apply_design_adjustment(trial: dict[str, Any], declared_estimand: str | None = None) -> bool:
    """Convert a held ICC design effect into a consumable effect+CI row.

    The original arm counts remain under ``raw_reconstruction`` for audit.  The
    row still has derivation ``reconstructed``; its design key carries
    ``reconstructed_with_ICC`` evidence so ``synth.Study.yi_vi`` may emit an SE.
    """

    adj = trial.get("design_adjustment")
    if not isinstance(adj, dict) or adj.get("kind") != DESIGN_VARIANCE_METHOD:
        return False
    if trial.get("ai") is None:
        return False
    yi, vi = inflated_log_effect_variance(trial, declared_estimand or trial.get("measure") or "RR")
    z = _norm.ppf(0.975)
    se = math.sqrt(vi)
    raw = {
        key: trial.get(key)
        for key in ("ai", "n1i", "ci", "n2i")
        if trial.get(key) is not None
    }
    trial["raw_reconstruction"] = raw
    for key in raw:
        trial.pop(key, None)
    trial["effect"] = math.exp(yi)
    trial["ci_low"] = math.exp(yi - z * se)
    trial["ci_high"] = math.exp(yi + z * se)
    trial["scale"] = (declared_estimand or trial.get("scale") or trial.get("measure") or "RR").upper()
    trial["derivation"] = "reconstructed"
    trial["selected_estimator"] = "reconstructed_with_ICC"
    trial["design_adjusted_variance"] = {
        "method": DESIGN_VARIANCE_METHOD,
        "design_effect": design_effect(adj.get("cluster_size") or adj.get("average_cluster_size") or adj.get("m"), adj.get("icc")),
        "variance": vi,
        "missing": "",
    }
    design = trial.setdefault("design", {})
    evidence = [{
        "source": str(adj.get("source") or "design_adjustment"),
        "span": str(adj.get("span") or f"ICC={adj.get('icc')}; cluster_size={adj.get('cluster_size') or adj.get('m')}"),
    }]
    design["correlation_handling"] = design_key.correlation_handling("reconstructed_with_ICC", evidence)
    design["se_provenance"] = "harness.design_variance:ICC_DESIGN_EFFECT"
    design["estimator_source"] = "RECONSTRUCTED_DESIGN_ADJUSTED"
    design["design_action"] = design_key.decision_for_trial(trial, declared_estimand)
    return True


def refusal_reason(trial: dict[str, Any]) -> str:
    design = str((trial.get("design") or {}).get("design") or "UNKNOWN").lower()
    return (
        f"{ENGINE_CANNOT_CONSUME}(design={design}, missing={MISSING_DESIGN_VARIANCE}): "
        f"{design_key.refusal_reason(trial)}"
    )


def refusal_absence(trial: dict[str, Any]) -> dict[str, Any]:
    row = {
        "label": trial.get("label"),
        "id": trial.get("id"),
        "absent_kind": ENGINE_ABSENT_KIND,
        "state": ENGINE_CANNOT_CONSUME,
        "reason_code": ENGINE_CANNOT_CONSUME,
        "missing": MISSING_DESIGN_VARIANCE,
        "reason": refusal_reason(trial),
        "state_basis": f"{ENGINE_CANNOT_CONSUME}: design-adjusted effect or ICC design effect is not held",
        "design": trial.get("design"),
    }
    if (trial.get("design") or {}).get("design_action"):
        row["design_action"] = (trial.get("design") or {}).get("design_action")
    alt = (trial.get("design") or {}).get("published_alternative")
    if alt:
        row["published_alternative"] = alt
    return row


def is_engine_refusal_row(row: dict[str, Any]) -> bool:
    return (
        row.get("state") == ENGINE_CANNOT_CONSUME
        or row.get("reason_code") == ENGINE_CANNOT_CONSUME
        or row.get("absent_kind") == ENGINE_ABSENT_KIND
    )


def design_refusal_row(trial: dict[str, Any]) -> dict[str, Any]:
    row = {
        "trial": design_key.display_name(trial),
        "id": trial.get("id"),
        "design": (trial.get("design") or {}).get("design"),
        "state": ENGINE_CANNOT_CONSUME,
        "reason_code": ENGINE_CANNOT_CONSUME,
        "missing": MISSING_DESIGN_VARIANCE,
        "reason": refusal_reason(trial),
    }
    alt = (trial.get("design") or {}).get("published_alternative")
    if alt:
        row["published_alternative"] = alt
    return row


def consumption_summary(outcome: dict[str, Any]) -> dict[str, Any]:
    pooled = outcome.get("trials") or []
    refused = outcome.get("design_refusals") or []
    k = len(pooled)
    refused_n = len(refused)
    eligible_with_outcome = k + refused_n
    if refused_n:
        headline = (
            "pooled: the subset this engine can safely consume "
            f"(k={k} of {eligible_with_outcome} eligible with mortality data; "
            f"{refused_n} refused for want of a variance model)"
        )
        state = "CONSUMABLE_SUBSET"
    else:
        headline = f"pooled: all {k} eligible trial(s) with a consumable variance model"
        state = "ALL_CONSUMED"
    return {
        "state": state,
        "headline": headline,
        "consumable_k": k,
        "eligible_with_outcome": eligible_with_outcome,
        "design_refused": refused_n,
        "missing": MISSING_DESIGN_VARIANCE if refused_n else "",
        "refused_for_want_of_variance_model": refused_n,
        "pooled_trial_ids": [t.get("id") for t in pooled],
        "refused_trial_ids": [r.get("id") for r in refused],
    }


def current_arm_contrast(arm_contrast: dict[str, Any] | None, outcome: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(arm_contrast, dict):
        return arm_contrast
    all_trials = copy.deepcopy(arm_contrast.get("trials") or {})
    pooled = {_trial_key(t.get("id") or t.get("label")) for t in outcome.get("trials") or []}
    if not all_trials:
        return copy.deepcopy(arm_contrast)
    # an EMPTY pooled set filters like any other (2026-09-21, lane T regression on balanced-crystalloids: with every
    # candidate set aside on admission the unfiltered cache was returned and the page said "2 of 3 pooled trials")
    filtered = {
        key: value for key, value in all_trials.items()
        if _trial_key(key) in pooled
    }
    dropped = sorted(k for k in all_trials if _trial_key(k) not in pooled)
    if not dropped:
        return copy.deepcopy(arm_contrast)
    out = copy.deepcopy(arm_contrast)
    out["trials_all"] = all_trials
    out["trials"] = filtered
    out["current_pooled_trial_ids"] = sorted(pooled)
    out["stale_block_unrenderable"] = {
        "state": "UNRENDERABLE",
        "reason": "cached arm-contrast membership named trials not in the current consumed pool",
        "dropped_trial_ids": dropped,
        "current_pooled_trial_ids": sorted(pooled),
    }
    return out


def protocol_control_expectations(review: dict[str, Any]) -> list[dict[str, Any]]:
    text = ((review.get("protocol") or {}).get("text") or "")
    if "BaSICS" not in text or "expected to fail closed" not in text:
        return []
    records = ((review.get("screening") or {}).get("records") or [])
    basics = next((r for r in records if "34375394" in str(r.get("id") or "")), None)
    if not basics or basics.get("decision") != "include":
        return []
    return [{
        "state": "UNRENDERABLE",
        "control": "BaSICS expected to fail closed at the RCT-publication-type screen",
        "reason": "protocol control expectation depends_on the screening decision; live screening includes BaSICS",
        "depends_on": {
            "screening_decision": "PMID 34375394 include",
            "screening_rule": basics.get("rule_id"),
        },
    }]


def annotate_grade(review: dict[str, Any]) -> None:
    primary = next((o for o in review.get("outcomes", []) or [] if o.get("primary")), None)
    grade = review.get("grade")
    if not primary or not isinstance(grade, dict):
        return
    dc = primary.get("design_consumption") or {}
    refused = dc.get("design_refused") or 0
    if not refused:
        return
    note = (
        f"Design-aware availability: k={dc.get('consumable_k')} of "
        f"{dc.get('eligible_with_outcome')} eligible-with-outcome trial(s) were consumable; "
        f"{refused} trial(s) were evidence refused for want of a variance model "
        f"({ENGINE_CANNOT_CONSUME}, missing={MISSING_DESIGN_VARIANCE}), distinct from evidence absent."
    )
    grade["design_consumption"] = dc
    grade["basis"] = (grade.get("basis") or "").rstrip() + " " + note
    domains = grade.setdefault("domains", {})
    imp = domains.setdefault("imprecision", {})
    imp["basis"] = (imp.get("basis") or "").rstrip() + " " + note


def check_review(review: dict[str, Any]) -> list[str]:
    """Small audit used by tests: it must fail on the pre-fix object and pass after rebuild."""

    out: list[str] = []
    primary = next((o for o in review.get("outcomes", []) or [] if o.get("primary")), None)
    if not primary:
        return ["NO_PRIMARY_OUTCOME"]
    refusals = primary.get("design_refusals") or []
    if refusals:
        dc = primary.get("design_consumption") or (primary.get("result") or {}).get("design_consumption") or {}
        if "subset this engine can safely consume" not in str(dc.get("headline") or ""):
            out.append("HEADLINE_MISSING_DESIGN_CONSUMPTION")
        refused_ids = {_trial_key(r.get("id")) for r in refusals}
        rows = [r for r in primary.get("declared_absent_trials") or [] if _trial_key(r.get("id")) in refused_ids]
        if len(rows) != len(refusals) or any(not is_engine_refusal_row(r) for r in rows):
            out.append("DESIGN_REFUSAL_NOT_ENGINE_CODE")
        grade = review.get("grade") or {}
        # GRADE is deliberately absent when nothing is pooled (a withdrawn result, or every candidate set aside on
        # admission): only a GRADE that EXISTS must carry the variance-model rationale
        if grade and "want of a variance model" not in str(grade.get("basis") or ""):
            out.append("GRADE_MISSING_DESIGN_VARIANCE_RATIONALE")
        ac = ((review.get("arm_contrast") or {}).get("trials") or {})
        if ac and len(ac) != len(primary.get("trials") or []):
            out.append("STALE_ARM_CONTRAST_DENOMINATOR")
    if protocol_control_expectations(review) and not ((review.get("protocol") or {}).get("control_expectations")):
        out.append("STALE_PROTOCOL_CONTROL_EXPECTATION")
    return out
