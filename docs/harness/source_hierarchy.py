"""Source-hierarchy candidate surfacing and per-outcome estimand decisions.

This module does not replace the extractor. It scans committed source text for
effect+CI statements that the count-first extractor may have skipped, then lets
the existing selector choose among explicit candidates.
"""
from __future__ import annotations

import json
import re
from typing import Any

from . import estmeasure, extract

_EFFECT_CANDIDATE = re.compile(
    r"(relative risk reduction|relative risk|risk ratio|incidence rate ratio|rate ratio|(?-i:\bRR\b)|odds ratio|(?-i:\bOR\b)|hazard ratio|(?-i:\bHR\b))"
    r"[^0-9]{0,120}?(\d+(?:\.\d+)?)[^0-9]{0,35}?(?:\d{2}\s*(?:%|percent|per cent)\s*)?(?:confidence intervals?|\bCI\b)"
    r"[^0-9]{0,15}?(\d+(?:\.\d+)?)\s*(?:to|[-\u2013\u2014,])\s*(\d+(?:\.\d+)?)",
    re.I,
)


def _norm_scale(scale: Any) -> str:
    return str(scale or "").upper().strip()


def _compat_class(scale: Any) -> str:
    return estmeasure.compatibility_class(
        estmeasure.classify(str(scale or "")).get("canonical_estimand")
    )


def _snippet(text: str, start: int, end: int, before: int = 180, after: int = 80) -> str:
    lo = max(0, start - before)
    hi = min(len(text), end + after)
    return re.sub(r"\s+", " ", text[lo:hi]).strip()


def _same_effect(a: dict[str, Any], b: dict[str, Any]) -> bool:
    return tuple(a.get(k) for k in ("effect", "ci_low", "ci_high", "scale")) == tuple(
        b.get(k) for k in ("effect", "ci_low", "ci_high", "scale")
    )


def reported_effect_candidate(eff: dict[str, Any] | None, provenance: str, source_label: str) -> dict[str, Any] | None:
    if not eff or eff.get("effect") is None:
        return None
    return {
        "effect": eff["effect"],
        "ci_low": eff.get("ci_low"),
        "ci_high": eff.get("ci_high"),
        "scale": eff.get("scale"),
        "provenance": provenance,
        "source": f"{source_label} effect+CI ({eff.get('scale')}): {eff.get('source', '')}".strip(),
        "derivation": "reported",
    }


def _effect_candidates_in_outcome(text: str, kws: list[str], *, window: int = 260) -> list[dict[str, Any]]:
    text = extract._norm(text or "")
    kl = [str(k).lower() for k in kws or []]
    candidates: list[dict[str, Any]] = []
    for sentence in extract._sentences(text):
        low = sentence.lower()
        prev_end = 0
        for m in _EFFECT_CANDIDATE.finditer(sentence):
            clause = low[prev_end:m.start()][-window:]
            if any(k in clause for k in kl):
                eff = extract._effect_from_match(m, sentence[max(0, m.start() - 260):m.end() + 120])
                if eff:
                    candidates.append({
                        "effect": eff[1],
                        "ci_low": eff[2],
                        "ci_high": eff[3],
                        "scale": eff[0],
                        "source": _snippet(sentence, prev_end, m.end()),
                    })
            prev_end = m.end()
    return candidates


def _append_unique(out: list[dict[str, Any]], candidate: dict[str, Any] | None) -> None:
    if candidate and not any(_same_effect(candidate, old) for old in out):
        out.append(candidate)


def source_effect_candidates(
    spec: dict[str, Any],
    *,
    abstract: str | None = None,
    fulltext: str | None = None,
    ctgov_outcomes: Any = None,
    verified_effect: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for eff in _effect_candidates_in_outcome(abstract or "", spec.get("keywords") or []):
        _append_unique(candidates, reported_effect_candidate(eff, "abstract", "abstract"))
    if fulltext:
        for eff in _effect_candidates_in_outcome(fulltext, spec.get("keywords") or []):
            _append_unique(candidates, reported_effect_candidate(eff, "pmc_fulltext_effect", "cached full text"))
    if ctgov_outcomes:
        text = json.dumps(ctgov_outcomes, ensure_ascii=False)
        for eff in _effect_candidates_in_outcome(text, spec.get("keywords") or []):
            _append_unique(
                candidates,
                reported_effect_candidate(eff, "ctgov_results_effect", "ClinicalTrials.gov results"),
            )
    if (verified_effect and verified_effect.get("outcome") == spec.get("name")
            and verified_effect.get("effect") is not None):
        _append_unique(candidates, {
            "effect": verified_effect["effect"],
            "ci_low": verified_effect.get("ci_low"),
            "ci_high": verified_effect.get("ci_high"),
            "scale": verified_effect.get("scale", "HR"),
            "provenance": verified_effect.get("provenance", "fulltext_verified"),
            "source": verified_effect.get("source", "full-text-verified effect+CI"),
            "derivation": "reported",
        })
    return candidates


def selection_extras(row: dict[str, Any]) -> dict[str, Any]:
    extras = {}
    limits = row.get("source_hierarchy_limitations") or row.get("limitations")
    if limits:
        extras["source_hierarchy_limitations"] = limits
    if row.get("derivation"):
        extras["derivation"] = row.get("derivation")
    return extras


def span_effect_candidates(spec: dict[str, Any], selected: dict[str, Any], base_candidates: list[dict[str, Any]]):
    candidates = list(base_candidates or [])
    for eff in _effect_candidates_in_outcome(selected.get("source", "") or "", spec.get("keywords") or []):
        cand = reported_effect_candidate(
            eff,
            selected.get("provenance") or "committed_source",
            selected.get("provenance") or "committed source",
        )
        if cand:
            candidates.insert(0, cand)
    return candidates


def estimand_decision(spec: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    declared = _norm_scale(spec.get("estimand") or "RR")
    scales = [_norm_scale(c.get("scale")) for c in candidates if c.get("effect") is not None]
    has_hr = "HR" in scales
    has_rr = "RR" in scales
    has_or = "OR" in scales

    if declared in {"MD", "SMD"}:
        decision, target = "continuous", declared
        reason = "declared continuous estimand"
    elif declared == "OR" and (has_rr or has_hr) and not has_or:
        if has_hr:
            decision, target = "time_to_first_event", "HR"
            reason = "declared OR, but the target outcome's only published effect+CI is HR"
        else:
            decision, target = "cumulative_risk_at_trial_end", "RR"
            reason = "declared OR, but the target outcome's only published effect+CI is RR"
    elif declared == "OR":
        decision, target = "odds", "OR"
        reason = "declared odds-ratio estimand"
    elif declared == "HR" or "HAZARD" in declared or has_hr:
        decision, target = "time_to_first_event", "HR"
        reason = "published HR exists for the target outcome" if has_hr else "declared hazard-ratio estimand"
    else:
        decision, target = "cumulative_risk_at_trial_end", "RR"
        reason = "declared cumulative risk-ratio estimand"

    return {
        "declared_estimand": declared,
        "decision": decision,
        "target_scale": target,
        "target_class": _compat_class(target),
        "published_candidate_scales": sorted(set(scales)),
        "served_scale_changed": target != declared,
        "reason": reason,
        "rule": {
            "time_to_first_event": "prefer published HR; keep reconstruction only when no HR exists",
            "cumulative_risk_at_trial_end": "prefer published RR; otherwise reconstruct RR from counts consistently",
            "odds": "prefer published OR; otherwise reconstruct OR from counts consistently",
            "continuous": "pool the declared continuous scale from mean/SD inputs",
        }.get(decision, "use declared scale"),
    }


def mixed_by_source_limit(trial: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any] | None:
    if decision.get("decision") != "time_to_first_event":
        return None
    if trial.get("effect") is not None and _norm_scale(trial.get("scale")) == "HR":
        return None
    pid = str(trial.get("id") or trial.get("label") or "")
    if "35041780" in pid:
        reason = (
            "PLUS has no committed published HR in the cached abstract; the row has counts only. "
            "The outcome decision prefers HR where committed, so PLUS remains a reconstructed RR "
            "until the full-text HR is retrieved."
        )
    else:
        reason = (
            "Outcome decision prefers published HR, but this row has no committed HR effect+CI; "
            "the row remains on the reconstructed/available scale and the pool is mixed by source limit."
        )
    return {
        "code": "MIXED_BY_SOURCE_LIMIT",
        "reason": reason,
        "citation": "SOURCE_NOT_RETRIEVED_FULL_TEXT_NEEDED",
    }
