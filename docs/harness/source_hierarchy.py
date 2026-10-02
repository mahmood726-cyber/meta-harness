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
            hits = [k for k in kl if k in clause]
            if hits:
                eff = extract._effect_from_match(m, sentence[max(0, m.start() - 260):m.end() + 120])
                if eff:
                    candidates.append({
                        "effect": eff[1],
                        "ci_low": eff[2],
                        "ci_high": eff[3],
                        "scale": eff[0],
                        "source": _snippet(sentence, prev_end, m.end()),
                        # WHICH declared keywords put this candidate here, and the sentence it came
                        # from. Needed because a keyword that is only an endpoint LABEL ("primary
                        # endpoint") says nothing about which endpoint is being reported -- see
                        # effect_candidates_for_outcome below.
                        "matched_keywords": hits,
                        "sentence": sentence,
                    })
            prev_end = m.end()
    return candidates


# An endpoint LABEL is a name for whichever endpoint a trial designated, not a description of one.
# "primary endpoint" identifies a different quantity in every trial that uses it.
_LABEL_ONLY_KEYWORD = re.compile(
    r"^(?:the\s+)?(?:co-?primary|primary|key secondary|secondary|main)[\s-]+(?:composite\s+)?"
    r"(?:outcome|end[\s-]?point|measure|variable)s?$"
    r"|^(?:the\s+)?composite(?:\s+(?:outcome|end[\s-]?point))?$",
    re.I,
)
_COMPOSITE_OUTCOME_NAME = re.compile(
    r"composite|\bMACE\b|major adverse cardiovascular|major vascular|major coronary"
    r"|\bor\b|/", re.I,
)


def _declared_outcome_is_composite(spec: dict[str, Any]) -> bool:
    canon = (spec.get("endpoint_canonical") or {})
    if len(canon.get("components") or []) >= 2:
        return True
    return bool(_COMPOSITE_OUTCOME_NAME.search(str(spec.get("name") or "")))


def label_only_harvest_refusal(spec: dict[str, Any], text: str, candidate: dict[str, Any],
                               *, unresolved_is_refusal: bool = False) -> str | None:
    """Why this candidate must not be offered for this outcome, or None if it may be.

    A candidate is in question only when EVERY keyword that surfaced it is a bare endpoint label.
    Such a sentence ("The primary endpoint occurred in 29.7% ... [hazard ratio=0.85]") names no
    outcome at all; it names whatever the trial designated. So the label is resolved to its own
    definition span in the SAME held text and the endpoint is settled from that.

    Refuse when the definition is a composite of two or more components and the declared outcome is
    not itself a composite: that is a different quantity, and offering it lets the source-hierarchy
    selector prefer it over a correct reconstruction, which is how a CV-death/HHF composite came to
    be served as all-cause mortality (PMID 28824029).

    Do NOT refuse when the declared outcome IS the composite the label resolves to -- that is the
    label doing its job, and it is the only route by which some MACE trials report a result at all
    (PMID 30418475). A rule that refuses both is a rule that deleted the keyword.
    """
    hits = [str(k) for k in (candidate.get("matched_keywords") or [])]
    if not hits or not all(_LABEL_ONLY_KEYWORD.match(k.strip()) for k in hits):
        return None
    if _declared_outcome_is_composite(spec):
        return None
    from . import target_endpoint as _te
    binding = _te.bind_result_span(text or "", candidate.get("sentence") or candidate.get("source"))
    components = sorted(binding.get("components") or [])
    if len(components) >= 2:
        return (
            f"the sentence names its endpoint only as {hits[0]!r}, which this document defines as a "
            f"composite of {', '.join(components)}; the declared outcome "
            f"{str(spec.get('name') or '')!r} is a single component, so this is a different quantity"
        )
    if not components and unresolved_is_refusal:
        return (
            f"the sentence names its endpoint only as {hits[0]!r} and no definition span for that "
            "label is present in the text supplied, so which endpoint it reports is unknown"
        )
    return None


def candidate_scope_refusal(candidate: dict[str, Any]) -> str | None:
    """The row-level scope guards, applied to a HARVESTED candidate.

    The pipeline applies extract's guards to the row it extracts, but the source-hierarchy selector can then
    REPLACE that row's number with a harvested candidate (provenance pmc_fulltext_effect), and nothing guarded
    the candidate. That is how a subgroup RR (probiotics PMID 34541475, patients on regular PPI) reached the pool
    when held full texts were enabled. The sentence the number came from is checked, falling back to the snippet.
    """
    text = candidate.get("sentence") or candidate.get("source") or ""
    return (extract.subgroup_refusal(text) or extract.table_role_refusal(text)) or None


def effect_candidates_for_outcome(spec: dict[str, Any], text: str,
                                  record: list[str] | None = None) -> list[dict[str, Any]]:
    """Harvested effect candidates for the declared outcome, with label-only mismatches removed.

    ENDPOINT ELIGIBILITY BEFORE SOURCE PREFERENCE. The selector downstream ranks candidates by
    source and estimand class and never asks what endpoint they are about, so a candidate that is
    about the wrong endpoint must not reach it.
    """
    kept = []
    for cand in _effect_candidates_in_outcome(text or "", spec.get("keywords") or []):
        refusal = (label_only_harvest_refusal(spec, text or "", cand)
                   or candidate_scope_refusal(cand))
        if refusal:
            # A refusal that is not recorded cannot be explained later. The pooled result moves,
            # the notice says a different number is now contributed, and nothing anywhere says
            # why the previous one was dropped -- so the reason is carried out with the candidate.
            if record is not None:
                record.append(refusal)
            continue
        kept.append(cand)
    return kept


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
    record: list[str] | None = None,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for eff in effect_candidates_for_outcome(spec, abstract or "", record):
        _append_unique(candidates, reported_effect_candidate(eff, "abstract", "abstract"))
    if fulltext:
        for eff in effect_candidates_for_outcome(spec, fulltext, record):
            _append_unique(candidates, reported_effect_candidate(eff, "pmc_fulltext_effect", "cached full text"))
    if ctgov_outcomes:
        text = json.dumps(ctgov_outcomes, ensure_ascii=False)
        for eff in effect_candidates_for_outcome(spec, text, record):
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


def span_effect_candidates(spec: dict[str, Any], selected: dict[str, Any],
                           base_candidates: list[dict[str, Any]], text: str | None = None,
                           record: list[str] | None = None):
    """`text` is the HELD DOCUMENT, not the row's source snippet.

    A label-only candidate is settled by resolving the label to its definition span, and that span
    is almost never inside the snippet the row carries (PMID 28824029's is 171 chars and holds the
    result sentence alone). Filtering against the snippet would resolve nothing and refuse nothing
    while looking like a filter, so the held document is passed in and the snippet is only a
    fallback -- and on that fallback an unresolvable label-only candidate is REFUSED, not admitted.
    """
    span_text = selected.get("source", "") or ""
    resolve_text = text or span_text
    candidates = list(base_candidates or [])
    for eff in _effect_candidates_in_outcome(span_text, spec.get("keywords") or []):
        refusal = (label_only_harvest_refusal(spec, resolve_text, eff, unresolved_is_refusal=not text)
                   or candidate_scope_refusal(eff))
        if refusal:
            if record is not None:
                record.append(refusal)
            continue
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
