"""Canonical per-trial design key and design-aware analytic decisions.

Auditor defect class recorded verbatim: DIAGNOSTIC–DECISION DECOUPLING — a
validity hazard is correctly detected and represented, but its state is not
causally connected to the analytic decision it should constrain. Plain alias:
disclosure-as-control. Class PROCESS, direction optimistic, severity
major-to-critical.
"""
from __future__ import annotations

import json
import math
import os
import re
from typing import Any

from . import estmeasure, unit_of_analysis, adjustment


UNSUPPORTED_RECONSTRUCTED = {"CLUSTER", "CROSSOVER", "CLUSTER_CROSSOVER", "STEPPED_WEDGE"}
ADJUSTMENT_KINDS = {"ICC_DESIGN_EFFECT", "PAIRED_ANALYSIS", "PUBLISHED_ADJUSTED_SUBSTITUTED"}
ACTION_VALUES = ("ALLOW", "ALLOW_WITH_LABEL", "ADJUST", "MANUAL_REVIEW", "REFUSE", "DESIGN_UNPROVEN")
BLOCKING_ACTIONS = {"MANUAL_REVIEW", "REFUSE"}
CORRELATION_METHODS = {
    "published_model",
    "published_adjusted_SE",
    "reconstructed_with_ICC",
    "paired_effect",
    "none",
}
STUDY_EFFECT_REQUIRED_FIELDS = (
    "effect_estimate",
    "standard_error",
    "estimand",
    "analysis_population",
    "randomisation_unit",
    "study_design",
    "estimator_method",
    "correlation_handling",
    "source_provenance",
)

_KNOWN_NAMES = {
    "29485925": "SMART",
    "27749094": "SALT",
    "26444692": "SPLIT",
    "34375394": "BaSICS",
    "21115589": "Alpha Omega",
}

_TEXT_MAP = {
    "cluster-randomized": ("CLUSTER", "CLUSTER"),
    "crossover": ("CROSSOVER", "UNKNOWN"),
    "cluster-randomized crossover": ("CLUSTER_CROSSOVER", "CLUSTER"),
    "factorial": ("FACTORIAL", "INDIVIDUAL"),
    "stepped-wedge": ("STEPPED_WEDGE", "CLUSTER"),
}

# the order a conflict resolves in: the design that carries the greater validity hazard wins
_DESIGN_SEVERITY = {"PARALLEL": 1, "SINGLE_GROUP": 2, "FACTORIAL": 3, "CROSSOVER": 4, "CLUSTER": 5, "STEPPED_WEDGE": 6, "CLUSTER_CROSSOVER": 7}

_REGISTRY_MAP = {
    "FACTORIAL ASSIGNMENT": ("FACTORIAL", "INDIVIDUAL"),
    "CROSSOVER ASSIGNMENT": ("CROSSOVER", "UNKNOWN"),
    "PARALLEL ASSIGNMENT": ("PARALLEL", "INDIVIDUAL"),
    "SEQUENTIAL ASSIGNMENT": ("STEPPED_WEDGE", "CLUSTER"),
    # ClinicalTrials.gov API v2 / AACT enumerations of the same field: every pooled glp1 row carried the
    # registry value PARALLEL as design evidence while the decision said "no committed design evidence"
    # (Mahmood's review of 98726cc1, item 2) because only the legacy spellings were mapped
    "FACTORIAL": ("FACTORIAL", "INDIVIDUAL"),
    "CROSSOVER": ("CROSSOVER", "UNKNOWN"),
    "PARALLEL": ("PARALLEL", "INDIVIDUAL"),
    "SEQUENTIAL": ("STEPPED_WEDGE", "CLUSTER"),
    "SINGLE_GROUP": ("SINGLE_GROUP", "UNKNOWN"),
}

_ALT_RE = re.compile(
    r"\b(adjusted\s+)?(hazard ratio|odds ratio|risk ratio|relative risk|rate ratio|HR|OR|RR|IRR)"
    r"[,:\s]+(?P<effect>\d+(?:\.\d+)?)\s*(?:\[\s*)?(?:(?:\(|,\s*)?95%\s*(?:confidence interval|CI)[,\s]*)?"
    r"(?P<lo>\d+(?:\.\d+)?)\s*(?:-|to|\u2013)\s*(?P<hi>\d+(?:\.\d+)?)",
    re.I,
)
_NO_INTERACTION_RE = re.compile(
    r"\bno\s+significant\s+interaction\b.{0,120}?\b(?:P|p)\s*[=<>]\s*\.?\d+",
    re.I,
)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _pid(trial: dict[str, Any]) -> str:
    return str(trial.get("id") or trial.get("label") or "").replace("PMID ", "").replace("PMID:", "").strip()


def display_name(trial: dict[str, Any]) -> str:
    pid = _pid(trial)
    return _KNOWN_NAMES.get(pid) or str(trial.get("label") or trial.get("id") or pid)


def registry_designs(records: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in records.get("ctgov") or []:
        nct = str(row.get("id") or row.get("nct_id") or "").upper()
        if nct:
            out[nct] = row
    for row in records.get("designs") or []:
        nct = str(row.get("nct_id") or row.get("id") or "").upper()
        if nct:
            out.setdefault(nct, {}).update(row)
    slug = records.get("slug")
    if slug:
        path = os.path.join(ROOT, "cache", str(slug), "registry_designs.json")
        try:
            cached = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            cached = {}
        if isinstance(cached, dict):
            for nct, row in cached.items():
                key = str(nct or "").upper()
                if key and isinstance(row, dict):
                    out.setdefault(key, {}).update(row)
    return out


def derivation_for_trial(trial: dict[str, Any]) -> str | None:
    if trial.get("ai") is not None or trial.get("mean1") is not None or trial.get("e1i") is not None:
        return "reconstructed"
    if trial.get("effect") is not None:
        return "reported"
    return None


def _is_reconstructed_derivation(value: Any) -> bool:
    return str(value or "").startswith("reconstructed")


_RECONSTRUCTED_FIELDS = (
    "ai", "mean1", "e1i",
)


def _source_span(text: Any, limit: int = 200) -> str:
    span = re.sub(r"\s+", " ", str(text or "")).strip()
    return span if len(span) <= limit else span[:limit - 3] + "..."


def _candidate_derivation(candidate: dict[str, Any]) -> str | None:
    if candidate.get("derivation"):
        return str(candidate.get("derivation"))
    if any(candidate.get(k) is not None for k in _RECONSTRUCTED_FIELDS):
        return "reconstructed"
    if candidate.get("effect") is not None:
        return "reported"
    return None


def _is_reported_effect(candidate: dict[str, Any]) -> bool:
    return (
        candidate.get("effect") is not None
        and candidate.get("ci_low") is not None
        and candidate.get("ci_high") is not None
        and candidate.get("scale")
    )


def _declared_estimand_class(declared_estimand: str | None) -> str:
    text = str(declared_estimand or "").upper()
    tokens = [t for t in re.split(r"[^A-Z0-9]+", text) if t]
    if not tokens:
        tokens = [text] if text else []
    classes = {
        estmeasure.compatibility_class(estmeasure.classify(token).get("canonical_estimand"))
        for token in tokens
    }
    classes.discard("OTHER")
    if len(classes) == 1:
        return next(iter(classes))
    return "OTHER"


def _candidate_estimand_class(candidate: dict[str, Any]) -> str:
    return estmeasure.compatibility_class(
        estmeasure.classify(candidate.get("scale"), candidate.get("source", "")).get("canonical_estimand")
    )


def _same_candidate(a: dict[str, Any], b: dict[str, Any]) -> bool:
    if _is_reported_effect(a) and _is_reported_effect(b):
        return tuple(a.get(k) for k in ("effect", "ci_low", "ci_high", "scale")) == tuple(
            b.get(k) for k in ("effect", "ci_low", "ci_high", "scale")
        )
    if a.get("ai") is not None and b.get("ai") is not None:
        return tuple(a.get(k) for k in ("ai", "n1i", "ci", "n2i")) == tuple(
            b.get(k) for k in ("ai", "n1i", "ci", "n2i")
        )
    keys = (
        "effect", "ci_low", "ci_high", "scale",
        "ai", "n1i", "ci", "n2i",
        "e1i", "t1i", "e2i", "t2i",
        "mean1", "sd1", "nc1", "mean2", "sd2", "nc2",
        "provenance", "source",
    )
    return tuple(a.get(k) for k in keys) == tuple(b.get(k) for k in keys)


def _crude_rr(candidate: dict[str, Any]) -> float | None:
    ai, n1i, ci, n2i = (candidate.get(k) for k in ("ai", "n1i", "ci", "n2i"))
    if None in (ai, n1i, ci, n2i) or not n1i or not n2i or not ci:
        return None
    return (float(ai) / float(n1i)) / (float(ci) / float(n2i))


def _candidate_summary(candidate: dict[str, Any], chosen: dict[str, Any], declared_class: str) -> dict[str, Any]:
    derivation = _candidate_derivation(candidate) or "unknown"
    row: dict[str, Any] = {
        "derivation": derivation,
        "provenance": candidate.get("provenance"),
        "source_span": _source_span(candidate.get("source")),
    }
    if _is_reported_effect(candidate):
        cclass = _candidate_estimand_class(candidate)
        row.update({
            "effect": candidate.get("effect"),
            "ci_low": candidate.get("ci_low"),
            "ci_high": candidate.get("ci_high"),
            "scale": candidate.get("scale"),
            "estimand_class": cclass,
        })
        if cclass != declared_class:
            row["not_selected_reason"] = "NOT_TARGET_CLASS"
            row["not_selected_detail"] = f"{cclass}!={declared_class}"
        elif not _same_candidate(candidate, chosen):
            row["not_selected_reason"] = "source_hierarchy_lower_precedence"
    elif candidate.get("ai") is not None:
        row.update({
            "ai": candidate.get("ai"),
            "n1i": candidate.get("n1i"),
            "ci": candidate.get("ci"),
            "n2i": candidate.get("n2i"),
            "implied_rr": _crude_rr(candidate),
        })
        if not _same_candidate(candidate, chosen):
            row["not_selected_reason"] = "source_hierarchy_lower_precedence"
    elif candidate.get("e1i") is not None:
        row.update({
            "e1i": candidate.get("e1i"),
            "t1i": candidate.get("t1i"),
            "e2i": candidate.get("e2i"),
            "t2i": candidate.get("t2i"),
            "scale": candidate.get("measure") or "IRR",
        })
    elif candidate.get("mean1") is not None:
        row.update({
            "mean1": candidate.get("mean1"),
            "sd1": candidate.get("sd1"),
            "nc1": candidate.get("nc1"),
            "mean2": candidate.get("mean2"),
            "sd2": candidate.get("sd2"),
            "nc2": candidate.get("nc2"),
            "scale": "MD",
        })
    return {k: v for k, v in row.items() if v is not None}


def select_estimator_by_source_hierarchy(
    selected: dict[str, Any],
    candidates: list[dict[str, Any]] | None,
    declared_estimand: str | None,
) -> dict[str, Any]:
    """Select the trial-outcome estimator by the declared source hierarchy.

    For a trial x outcome, a source-reported effect plus 95% CI from committed bytes
    (cached abstract, cached full text, CT.gov results cache, or committed verified
    effect) whose estimand compatibility class matches the outcome's declared
    estimand class is selected over any count, rate, or continuous reconstruction.
    HR and RR share the FIRST_EVENT_RATIO class, so a published HR can be preferred
    over a reconstructed RR for a time-to-first-event outcome. OR is its own class.
    Published effects from a different class, such as OR or RATE for a
    FIRST_EVENT_RATIO outcome, remain disclosed alternatives and do not weaken the
    estimand gate.
    """

    current = dict(selected)
    current["derivation"] = _candidate_derivation(current) or current.get("derivation") or "unknown"
    pool = [current]
    for cand in candidates or []:
        if cand and not any(_same_candidate(cand, existing) for existing in pool):
            cc = dict(cand)
            cc["derivation"] = _candidate_derivation(cc) or cc.get("derivation") or "unknown"
            pool.append(cc)

    declared_class = _declared_estimand_class(declared_estimand)
    published_target = [
        cand for cand in pool
        if _is_reported_effect(cand) and _candidate_estimand_class(cand) == declared_class
    ]
    current_is_reconstructed = _is_reconstructed_derivation(current.get("derivation"))
    if current_is_reconstructed and published_target:
        chosen = dict(published_target[0])
        rule = "PUBLISHED_EFFECT_TARGET_CLASS"
    else:
        chosen = current
        if current.get("derivation") == "reported":
            rule = "KEEP_REPORTED_EFFECT"
        elif any(_is_reported_effect(cand) for cand in pool[1:]):
            rule = "KEEP_RECONSTRUCTION_EFFECT_CLASS_MISMATCH"
        elif current_is_reconstructed:
            rule = "KEEP_RECONSTRUCTION_NO_TARGET_PUBLISHED_EFFECT"
        else:
            rule = "KEEP_CURRENT_ESTIMATOR"

    for key in ("label", "id"):
        if current.get(key) is not None:
            chosen[key] = current[key]
    chosen["derivation"] = _candidate_derivation(chosen) or chosen.get("derivation") or "unknown"
    chosen["selection_rule"] = rule
    chosen["selected_estimator"] = (
        "published_effect_ci" if chosen.get("derivation") == "reported"
        else "reconstructed"
    )
    chosen["alternatives"] = [
        _candidate_summary(cand, chosen, declared_class)
        for cand in pool
        if not _same_candidate(cand, chosen)
    ]
    return chosen


def _se_provenance(trial: dict[str, Any]) -> str:
    if trial.get("ai") is not None:
        return "synth.Study.yi_vi:2x2:" + str(trial.get("measure") or trial.get("scale") or "RR")
    if trial.get("e1i") is not None:
        return "synth.Study.yi_vi:incidence-rate-ratio"
    if trial.get("mean1") is not None:
        return "synth.Study.yi_vi:mean-difference"
    if trial.get("effect") is not None:
        return "synth.Study.yi_vi:reported-effect-ci"
    return "not-poolable"


def _published_alternative(source: str) -> dict[str, Any] | None:
    m = _ALT_RE.search(source or "")
    if not m:
        return None
    label = m.group(2).upper()
    scale = {"HAZARD RATIO": "HR", "ODDS RATIO": "OR", "RISK RATIO": "RR",
             "RELATIVE RISK": "RR", "RATE RATIO": "IRR"}.get(label, label)
    return {
        "effect": float(m.group("effect")),
        "ci_low": float(m.group("lo")),
        "ci_high": float(m.group("hi")),
        "scale": scale,
        "adjusted": bool(m.group(1)),
        "span": re.sub(r"\s+", " ", m.group(0)).strip(),
    }


def _interaction_evidence(text: str) -> dict[str, str] | None:
    m = _NO_INTERACTION_RE.search(text or "")
    if not m:
        return None
    return {
        "source": "committed title/abstract interaction phrase",
        "span": re.sub(r"\s+", " ", m.group(0)).strip(),
    }


def _has_span(evidence: Any) -> bool:
    if not isinstance(evidence, list):
        return False
    return any(isinstance(item, dict) and str(item.get("span") or "").strip() for item in evidence)


def correlation_handling(method: str, evidence: list[dict[str, str]] | None = None) -> dict[str, Any]:
    """Normalize correlation-handling provenance.

    A method other than ``none`` is trusted only when it carries at least one
    evidence span. This is the CAPE COD correction: labels are not authority.
    """

    evidence = [item for item in (evidence or []) if isinstance(item, dict)]
    method = str(method or "none")
    if method not in CORRELATION_METHODS:
        method = "none"
    if method != "none" and not _has_span(evidence):
        return {"method": "none", "evidence": []}
    return {"method": method, "evidence": evidence if method != "none" else []}


def _correlation_for_trial(
    trial: dict[str, Any],
    *,
    estimator_source: str,
    alt: dict[str, Any] | None,
) -> dict[str, Any]:
    adj = trial.get("design_adjustment")
    if isinstance(adj, dict):
        ev = [{"source": str(adj.get("source") or "design_adjustment"),
               "span": str(adj.get("span") or adj.get("reason") or adj.get("kind") or "")}]
        kind = adj.get("kind")
        if kind == "ICC_DESIGN_EFFECT":
            return correlation_handling("reconstructed_with_ICC", ev)
        if kind == "PAIRED_ANALYSIS":
            return correlation_handling("paired_effect", ev)
        if kind == "PUBLISHED_ADJUSTED_SUBSTITUTED":
            return correlation_handling("published_model", ev)
    if estimator_source == "PUBLISHED_ADJUSTED":
        ev = []
        if alt:
            ev.append({"source": "trial reported adjusted estimate", "span": alt.get("span", "")})
        elif trial.get("source"):
            ev.append({"source": "trial reported adjusted estimate", "span": str(trial.get("source"))})
        return correlation_handling("published_model", ev)
    return correlation_handling("none", [])


def _scale_class(scale: str | None) -> str:
    s = (scale or "").upper()
    if s in {"RR", "HR"}:
        return "FIRST_EVENT_RATIO"
    if s == "OR":
        return "ODDS_RATIO"
    if s in {"IRR", "RATE_RATIO", "RATE_RATIO_RECURRENT"}:
        return "RATE"
    if s in {"MD", "SMD"}:
        return "CONTINUOUS"
    return "OTHER"


def _same_declared_estimand(alt: dict[str, Any], declared_estimand: str | None) -> bool:
    return str(alt.get("scale") or "").upper() == str(declared_estimand or "").upper()


def _compatible_estimand(alt: dict[str, Any], declared_estimand: str | None) -> bool:
    return _scale_class(alt.get("scale")) == _scale_class(declared_estimand)


def _decision(
    action: str,
    *,
    gate_id: str,
    decision_state: str,
    reason: str,
    validity_critical: bool = False,
) -> dict[str, Any]:
    if action not in ACTION_VALUES:
        raise ValueError(f"invalid design action {action!r}")
    return {
        "action": action,
        "gate_id": gate_id,
        "decision_state": decision_state,
        "reason": reason,
        "validity_critical": bool(validity_critical),
    }


def decision_for_trial(trial: dict[str, Any], declared_estimand: str | None = None) -> dict[str, Any]:
    """Map the detected design/estimator state to one typed action."""

    d = trial.get("design") or {}
    design = d.get("design") or "UNKNOWN"
    unit = d.get("unit_of_randomisation") or "UNKNOWN"
    corr = correlation_handling(
        (d.get("correlation_handling") or {}).get("method", "none"),
        (d.get("correlation_handling") or {}).get("evidence", []),
    )
    alt = d.get("published_alternative")
    derivation = trial.get("derivation") or derivation_for_trial(trial) or "UNKNOWN"

    if alt and alt.get("adjusted") and _is_reconstructed_derivation(derivation):
        if _same_declared_estimand(alt, declared_estimand):
            return _decision(
                "REFUSE",
                gate_id="design-key:published-adjusted-available",
                decision_state="raw reconstruction refused; published adjusted estimand is available",
                reason=("published adjusted estimate is available for the declared estimand, but the "
                        "harness selected a raw reconstruction"),
                validity_critical=True,
            )
        return _decision(
            "MANUAL_REVIEW",
            gate_id="design-key:published-adjusted-available",
            decision_state="raw reconstruction cannot silently substitute for a published adjusted estimand",
            reason=("published adjusted estimate is available but its estimand differs from the declared "
                    f"{declared_estimand or 'UNKNOWN'} estimand"),
            validity_critical=True,
        )

    if design in {"CLUSTER", "CLUSTER_CROSSOVER"} and corr["method"] == "none":
        return _decision(
            "REFUSE",
            gate_id="design-key:cluster-unadjusted-se",
            decision_state="refused before PM/HKSJ",
            reason="cluster design + SE not design-adjusted",
            validity_critical=True,
        )
    if _is_reconstructed_derivation(derivation) and design == "CROSSOVER" and corr["method"] not in {"paired_effect", "published_model", "published_adjusted_SE"}:
        return _decision(
            "REFUSE",
            gate_id="design-key:crossover-correlation-unknown",
            decision_state="refused before PM/HKSJ",
            reason="crossover + within-person correlation unknown",
            validity_critical=True,
        )
    if _is_reconstructed_derivation(derivation) and design == "STEPPED_WEDGE" and corr["method"] not in {"published_model", "reconstructed_with_ICC"}:
        return _decision(
            "REFUSE",
            gate_id="design-key:stepped-wedge-no-model",
            decision_state="refused before PM/HKSJ",
            reason="stepped-wedge + no design model",
            validity_critical=True,
        )
    if design == "FACTORIAL" and unit == "INDIVIDUAL":
        return _decision(
            "ALLOW_WITH_LABEL",
            gate_id="design-key:factorial-marginal",
            decision_state="factorial marginal contrast labelled, not refused",
            reason="factorial + valid marginal effect + acceptable interaction",
        )
    if _is_reconstructed_derivation(derivation) and corr["method"] in {"reconstructed_with_ICC", "paired_effect"}:
        return _decision(
            "ADJUST",
            gate_id="design-key:adjusted-correlation",
            decision_state="explicit correlation adjustment carried into SE",
            reason=f"{corr['method']} evidence present",
        )
    if design == "UNKNOWN" or unit == "UNKNOWN":
        # Not observed is not parallel. The effect may still travel through the parallel-group path,
        # but the design key must not call that an allow state.
        return _decision(
            "DESIGN_UNPROVEN",
            gate_id="design-key:design-unproven",
            decision_state=("design not established from committed evidence; pooled through the parallel path "
                            "on an assumption the harness could not verify"),
            reason=(("committed design evidence does not establish an individually randomised parallel design: "
                     + "; ".join(f"{b.get('source')}: {b.get('span')}" for b in (d.get("basis") or [])
                                 if b.get("source") != "trial reported estimate label"))
                    if any(b.get("source") != "trial reported estimate label" for b in (d.get("basis") or []))
                    else "no committed design evidence (registry intervention model or design phrase)")
                   + "; UNKNOWN is not PARALLEL",
        )
    return _decision(
        "ALLOW",
        gate_id="design-key:parallel",
        decision_state="no detected validity-critical design hazard",
        reason="individually randomised parallel design established from committed evidence",
    )


def _registry_basis(nct: str | None, registry: dict[str, Any]) -> tuple[str | None, str | None, dict[str, str] | None]:
    if not nct:
        return None, None, None
    row = registry.get(str(nct).upper()) or {}
    raw = row.get("intervention_model") or row.get("interventionModel") or row.get("model")
    if not raw:
        return None, None, None
    val = str(raw).strip()
    mapped = _REGISTRY_MAP.get(val.upper())
    if not mapped:
        return None, None, {"source": "AACT designs.intervention_model", "span": val}
    return mapped[0], mapped[1], {"source": "AACT designs.intervention_model", "span": val}


def key_for_trial(trial: dict[str, Any], rec: dict[str, Any] | None = None,
                  registry: dict[str, Any] | None = None,
                  declared_estimand: str | None = None) -> dict[str, Any]:
    rec = rec or {}
    registry = registry or {}
    basis: list[dict[str, str]] = []
    text = (str(rec.get("title") or "") + " " + str(rec.get("abstract") or "")).strip()
    text_detail = unit_of_analysis.detect_detail(text)
    text_design = text_unit = None
    if text_detail:
        text_design, text_unit = _TEXT_MAP[text_detail["design"]]
        basis.append({"source": "committed title/abstract design phrase", "span": text_detail["span"]})

    reg_design, reg_unit, reg_basis = _registry_basis(rec.get("nct"), registry)
    if reg_basis:
        basis.append(reg_basis)

    candidates = [(d, u) for d, u in ((text_design, text_unit), (reg_design, reg_unit)) if d]
    conflict = len({d for d, _ in candidates}) > 1
    if conflict:
        # Two sources disagree. The conflict is recorded, and the design resolves to the MOST RESTRICTIVE candidate:
        # a conflict must never be more permissive than either source. Resolving it to UNKNOWN let SMART and SALT-ED
        # (abstract: "cluster-randomized, multiple-crossover"; registry: PARALLEL) fall from REFUSE into the parallel
        # path on the crystalloids page (k 2 -> 4) the moment the registry enumeration was mapped -- the deletion
        # invariant inside the design key (2026-09-19).
        design, unit = max(candidates, key=lambda du: _DESIGN_SEVERITY.get(du[0], 0))
        basis.append({"source": "design-key conflict", "span": " | ".join(d for d, _ in candidates)
                      + f" -> resolved to the most restrictive ({design})"})
    elif candidates:
        design, unit = candidates[0]
    else:
        design, unit = "UNKNOWN", "UNKNOWN"

    detected_derivation = derivation_for_trial(trial)
    derivation = trial.get("derivation") or detected_derivation
    if detected_derivation and not trial.get("derivation"):
        trial["derivation"] = detected_derivation
    alt = _published_alternative(trial.get("source") or "")
    interaction = _interaction_evidence(text + " " + str(trial.get("source") or ""))
    estimator_source = "RECONSTRUCTED"
    adjustment_axis = adjustment.axis_for_trial(trial)
    if derivation == "reported":
        estimator_source = adjustment.label(trial)
    if alt:
        basis.append({"source": "trial reported estimate label", "span": alt["span"]})

    out: dict[str, Any] = {
        "unit_of_randomisation": unit,
        "design": design,
        "estimator_source": estimator_source,
        "adjustment_status": adjustment_axis["status"],
        "adjustment_axis": adjustment_axis,
        "correlation_handling": _correlation_for_trial(trial, estimator_source=estimator_source, alt=alt),
        "se_provenance": _se_provenance(trial),
        "basis": basis,
    }
    if conflict:
        out["conflict"] = True
    if alt:
        out["published_alternative"] = alt
    if interaction:
        out["factorial_interaction"] = interaction
    shadow = dict(trial)
    shadow["design"] = out
    out["design_action"] = decision_for_trial(shadow, declared_estimand)
    return out


def stamp_trial(trial: dict[str, Any], rec_by_id: dict[str, dict[str, Any]],
                registry: dict[str, Any] | None = None,
                declared_estimand: str | None = None) -> dict[str, Any]:
    pid = _pid(trial)
    trial["design"] = key_for_trial(trial, rec_by_id.get(pid), registry, declared_estimand)
    return trial


def maybe_use_published_adjusted(trial: dict[str, Any], declared_estimand: str | None = None) -> bool:
    """Substitute a source-reported adjusted estimate when raw reconstruction would be the defect."""

    d = trial.get("design") or {}
    alt = d.get("published_alternative")
    action = (d.get("design_action") or {}).get("action")
    if not (alt and alt.get("adjusted") and action in BLOCKING_ACTIONS):
        return False
    if not _compatible_estimand(alt, declared_estimand):
        return False
    if d.get("design") == "FACTORIAL" and not d.get("factorial_interaction"):
        return False
    trial["raw_reconstruction"] = {
        key: trial.get(key)
        for key in ("ai", "n1i", "ci", "n2i", "e1i", "t1i", "e2i", "t2i", "mean1", "sd1", "nc1", "mean2", "sd2", "nc2")
        if trial.get(key) is not None
    }
    for key in list(trial["raw_reconstruction"]):
        trial.pop(key, None)
    trial["effect"] = alt["effect"]
    trial["ci_low"] = alt["ci_low"]
    trial["ci_high"] = alt["ci_high"]
    trial["scale"] = alt["scale"]
    trial["derivation"] = "reported"
    trial["selected_estimator"] = "published_adjusted"
    d["estimator_source"] = adjustment.label(trial)
    span = alt.get("span", "")
    start = (trial.get("source") or "").find(span) if span else -1
    trial["adjustment_axis"] = {"status": "ADJUSTED", "source": "selected published adjusted estimate",
                                "span": span, "start": start, "end": start + len(span)}
    d["adjustment_axis"] = adjustment.axis_for_trial(trial)
    d["adjustment_status"] = d["adjustment_axis"]["status"]
    evidence = [{"source": "trial reported adjusted estimate", "span": alt.get("span", "")}]
    if d.get("factorial_interaction"):
        evidence.append(d["factorial_interaction"])
    d["correlation_handling"] = correlation_handling("published_model", evidence)
    d["se_provenance"] = _se_provenance(trial)
    d["design_action"] = decision_for_trial(trial, declared_estimand)
    return True


def needs_design_refusal(trial: dict[str, Any]) -> bool:
    d = trial.get("design") or {}
    action = d.get("design_action") or decision_for_trial(trial)
    return action.get("action") in BLOCKING_ACTIONS


def naive_error_direction(design: str | None) -> str:
    if design == "CLUSTER":
        return "OPTIMISTIC"
    if design == "CLUSTER_CROSSOVER":
        return "OPTIMISTIC"
    if design == "CROSSOVER":
        return "PESSIMISTIC"
    if design == "STEPPED_WEDGE":
        return "OPTIMISTIC"
    if design in {"FACTORIAL", "PARALLEL"}:
        return "NONE"
    return "UNKNOWN"


def refusal_reason(trial: dict[str, Any]) -> str:
    d = trial.get("design") or {}
    action = d.get("design_action") or decision_for_trial(trial)
    label = str(d.get("design") or "UNKNOWN").replace("_", "-").lower()
    return (
        f"typed design action {action.get('action')}: {display_name(trial)} is {label}; "
        f"{action.get('reason')}; naive precision direction: {naive_error_direction(d.get('design'))}"
    )


def refusal_absence(trial: dict[str, Any]) -> dict[str, Any]:
    row = {
        "label": trial.get("label"),
        "id": trial.get("id"),
        "absent_kind": "engine_cannot_consume",
        "state": "ENGINE_CANNOT_CONSUME",
        "reason_code": "ENGINE_CANNOT_CONSUME",
        "missing": "design_adjusted_effect|ICC",
        "reason": (
            "ENGINE_CANNOT_CONSUME("
            f"design={str((trial.get('design') or {}).get('design') or 'UNKNOWN').lower()}, "
            "missing=design_adjusted_effect|ICC): "
            + refusal_reason(trial)
        ),
        "state_basis": "ENGINE_CANNOT_CONSUME: design-adjusted effect or ICC design effect is not held",
        "design": trial.get("design"),
    }
    if (trial.get("design") or {}).get("design_action"):
        row["design_action"] = (trial.get("design") or {}).get("design_action")
    alt = ((trial.get("design") or {}).get("published_alternative"))
    if alt:
        row["published_alternative"] = alt
    return row


def split_design_refusals(trials: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    kept, refused = [], []
    for trial in trials:
        (refused if needs_design_refusal(trial) else kept).append(trial)
    return kept, refused


def study_effect_object(
    trial: dict[str, Any],
    *,
    yi: float,
    vi: float,
    estimand: str | None,
    analysis_population: str | None,
    scale: str | None,
) -> dict[str, Any]:
    """The complete per-study effect object required before PM/HKSJ."""

    d = trial.get("design") or {}
    ratio = (scale or "").upper() not in {"MD", "SMD"}
    return {
        "effect_estimate": math.exp(yi) if ratio else yi,
        "standard_error": math.sqrt(vi),
        "estimand": estimand or "UNKNOWN",
        "analysis_population": analysis_population or "UNKNOWN",
        "randomisation_unit": d.get("unit_of_randomisation") or "UNKNOWN",
        "study_design": d.get("design") or "UNKNOWN",
        "estimator_method": d.get("estimator_source") or "UNKNOWN",
        "correlation_handling": correlation_handling(
            (d.get("correlation_handling") or {}).get("method", "none"),
            (d.get("correlation_handling") or {}).get("evidence", []),
        ),
        "source_provenance": {
            "source": trial.get("provenance") or "UNKNOWN",
            "span": trial.get("source") or "UNKNOWN",
        },
        "design_action": d.get("design_action") or decision_for_trial(trial, estimand),
    }


def validate_study_effect_object(obj: Any) -> list[str]:
    if not isinstance(obj, dict):
        return ["study_effect must be an object"]
    reasons = [f"study_effect missing {key}" for key in STUDY_EFFECT_REQUIRED_FIELDS if key not in obj]
    corr = obj.get("correlation_handling")
    if not isinstance(corr, dict):
        reasons.append("study_effect.correlation_handling must be an object")
    else:
        normalized = correlation_handling(corr.get("method", "none"), corr.get("evidence", []))
        if normalized.get("method") != corr.get("method"):
            reasons.append("study_effect.correlation_handling method lacks evidence and normalizes to none")
    return reasons
