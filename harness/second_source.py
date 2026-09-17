"""Second-source outcome identity for CT.gov cross-source rows.

Magnitude agreement is only meaningful after endpoint identity is established:
title, composite components, measure type, and population all have to line up.
"""
from __future__ import annotations

import math
import re
from typing import Any

IDENTICAL_ENDPOINT = "IDENTICAL_ENDPOINT"
SECOND_SOURCE_DIFFERENT_ENDPOINT = "SECOND_SOURCE_DIFFERENT_ENDPOINT"
SECOND_SOURCE_DIFFERENT_MEASURE = "SECOND_SOURCE_DIFFERENT_MEASURE"
SECOND_SOURCE_DIFFERENT_POPULATION = "SECOND_SOURCE_DIFFERENT_POPULATION"
SECOND_SOURCE_NOT_CHECKABLE = "SECOND_SOURCE_NOT_CHECKABLE"

_COMPOSITE_MARKERS = (
    "mace", "major adverse cardiovascular", "major cardiovascular", "composite",
    "cardiovascular events", "vascular events",
)

_COMPONENT_PATTERNS = (
    ("cardiovascular death", (
        r"cardiovascular death", r"\bcv death\b", r"death from cardiovascular",
    )),
    ("coronary heart disease death", (
        r"coronary heart disease .*death", r"\bchd death\b", r"death from coronary heart disease",
    )),
    ("myocardial infarction", (
        r"myocardial infarction", r"\bmi\b",
    )),
    ("stroke", (
        r"stroke", r"ischemic stroke", r"ischaemic stroke",
    )),
    ("unstable angina", (
        r"unstable angina", r"\bua\b",
    )),
    ("coronary revascularization", (
        r"coronary revascular", r"revasculari[sz]ation",
    )),
    ("heart failure hospitalization", (
        r"heart failure hospitali[sz]ation", r"\bhf hospitali[sz]ation",
    )),
)

_MEASURE_LABELS = {
    "COUNT_OF_PARTICIPANTS": "risk ratio from counts",
    "COUNT_OF_UNITS": "unit-count ratio",
    "PERCENTAGE": "percentage ratio",
    "KM_ESTIMATE": "KM estimate ratio",
}


def _fmt_effect(x: Any) -> str:
    return "NA" if x is None else f"{float(x):.3g}"


def _canon_component_text(text: str) -> set[str]:
    lower = (text or "").lower()
    found = set()
    for label, pats in _COMPONENT_PATTERNS:
        if any(re.search(pat, lower) for pat in pats):
            found.add(label)
    return found


def _canon_components(components: list[Any] | tuple[Any, ...] | None) -> set[str]:
    found = set()
    for component in components or []:
        text = str(component or "")
        canon = _canon_component_text(text)
        found.update(canon or {re.sub(r"\s+", " ", text.lower()).strip()})
    return {x for x in found if x}


def _needs_components(spec_name: str, declared_components: list[Any] | tuple[Any, ...] | None) -> bool:
    if declared_components:
        return True
    lower = (spec_name or "").lower()
    return any(marker in lower for marker in _COMPOSITE_MARKERS)


def component_identity(spec_name: str, declared_components, registry_title: str, registry_description: str) -> tuple[bool, str]:
    if not _needs_components(spec_name, declared_components):
        return True, "component set not applicable to this endpoint"
    expected = _canon_components(declared_components)
    if not expected:
        return False, "declared composite component set is not available"
    observed = _canon_component_text(" ".join([registry_title or "", registry_description or ""]))
    if expected == observed:
        return True, "registry component set matches the pooled trial component set"
    return (
        False,
        "registry component set does not match the pooled trial component set "
        f"(expected {sorted(expected) or 'none'}; observed {sorted(observed) or 'none'})",
    )


def measure_identity(registry_measure_type: str | None, pooled_scale: str | None) -> tuple[bool, str, str]:
    rtype = (registry_measure_type or "UNKNOWN").upper()
    label = _MEASURE_LABELS.get(rtype, rtype.lower().replace("_", " "))
    scale = (pooled_scale or "").upper()
    if rtype == "COUNT_OF_PARTICIPANTS" and scale in ("RR", "RISK_RATIO", "RISK RATIO", "RELATIVE RISK"):
        return True, label, "registry and pooled values are both risk ratios"
    if rtype == "COUNT_OF_PARTICIPANTS":
        return False, label, f"registry value is a risk ratio from counts, not pooled {pooled_scale or 'effect'}"
    if rtype == "PERCENTAGE":
        return False, label, "registry value is a percentage ratio, not a risk ratio"
    if rtype == "KM_ESTIMATE":
        return False, label, "registry value is a Kaplan-Meier estimate ratio, not a risk ratio"
    return False, label, f"registry measure type {rtype} is not established as commensurable"


def population_identity(declared_population: str | None, registry_population: str | None) -> tuple[bool, str]:
    declared = (declared_population or "").lower()
    registry = (registry_population or "").lower()
    if not registry:
        return True, "registry population not named; no mismatch detected"
    mismatch_markers = (
        "per protocol", "per-protocol", "on-treatment", "on treatment", "as treated",
        "safety population", "completer", "subgroup",
    )
    if any(marker in registry for marker in mismatch_markers):
        return False, f"registry population is not the randomized/ITT analysis set: {registry_population}"
    if "intention" in declared or "intent" in declared or "random" in declared:
        if any(marker in registry for marker in ("intent-to-treat", "itt", "randomized", "randomised", "all randomized")):
            return True, "registry population matches the randomized/ITT analysis set"
    return True, "no population mismatch detected"


def classify_identity(*, title_match: bool, spec_name: str, registry_title: str,
                      registry_description: str = "", declared_components=None,
                      registry_measure_type: str | None = None, pooled_scale: str | None = None,
                      pooled_effect=None, registry_effect=None, pooled_population: str | None = None,
                      registry_population: str | None = None, registry_timepoint: str | None = None,
                      log_tolerance: float = 0.12) -> dict[str, Any]:
    component_match, component_reason = component_identity(
        spec_name, declared_components, registry_title, registry_description
    )
    measure_match, measure_type, measure_reason = measure_identity(registry_measure_type, pooled_scale)
    population_match, population_reason = population_identity(pooled_population, registry_population)
    identity = {
        "title_match": bool(title_match),
        "component_match": bool(component_match),
        "measure_type": measure_type,
        "population_match": bool(population_match),
        "verdict": SECOND_SOURCE_NOT_CHECKABLE,
    }
    if not title_match:
        verdict = SECOND_SOURCE_DIFFERENT_ENDPOINT
        reason = f"registry title is not the pooled endpoint: {registry_title or 'untitled registry outcome'}"
    elif not component_match:
        verdict = SECOND_SOURCE_DIFFERENT_ENDPOINT
        reason = component_reason
    elif not measure_match:
        verdict = SECOND_SOURCE_DIFFERENT_MEASURE
        timepoint = f" ({registry_timepoint})" if registry_timepoint else ""
        reason = f"{measure_reason}{timepoint}: {registry_title or 'untitled registry outcome'}"
    elif not population_match:
        verdict = SECOND_SOURCE_DIFFERENT_POPULATION
        reason = population_reason
    elif pooled_effect is None or registry_effect is None or pooled_effect <= 0 or registry_effect <= 0:
        verdict = SECOND_SOURCE_NOT_CHECKABLE
        reason = f"cannot compare pooled and registry effects for: {registry_title or 'untitled registry outcome'}"
    else:
        delta = abs(math.log(float(pooled_effect) / float(registry_effect)))
        if delta > log_tolerance:
            verdict = SECOND_SOURCE_DIFFERENT_ENDPOINT
            reason = (f"registry-implied value {_fmt_effect(registry_effect)} differs from "
                      f"pooled {_fmt_effect(pooled_effect)} by log delta {delta:.3g} "
                      f"> tolerance {log_tolerance}: {registry_title}")
        else:
            verdict = IDENTICAL_ENDPOINT
            reason = (f"registry title, component set, measure type ({measure_type}), population, "
                      f"and numeric value match the pooled endpoint within log tolerance {log_tolerance}.")
    identity["verdict"] = verdict
    return {
        "identity": identity,
        "second_source_verdict": verdict,
        "endpoint_match": verdict,
        "endpoint_match_reason": reason,
        "registry_effect_label": "CT.gov " + measure_type,
    }


def counted_as_corroboration(cross_source: dict[str, Any]) -> bool:
    return (
        ((cross_source.get("identity") or {}).get("verdict") == IDENTICAL_ENDPOINT)
        and cross_source.get("agree") is not False
    )
