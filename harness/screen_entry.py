"""Entry-condition and randomised-contrast helpers for screening.

The ordinary screen is intentionally lexical and conservative. This module holds
the lane-specific rules that need structured metadata or explicit adjudication:
entry-condition-only exclusions, named comparator overrides, contrast metadata,
and completeness-state labels for eligible non-poolable trials.
"""
from __future__ import annotations

import re
from typing import Callable, Iterable

REGISTRY_FIELD_KEYS = ("phase", "status", "primary_completion", "completion", "enrollment")
DECISION_EXTRA_KEYS = REGISTRY_FIELD_KEYS + ("contrast_rule", "completeness_state")

_CONTROL = re.compile(r"placebo|matching|sham|standard care|usual care|control", re.I)


def _norm(x) -> str:
    return str(x or "").strip().lower()


def _record_keys(rec: dict) -> set[str]:
    return {
        str(x)
        for x in (rec.get("id"), rec.get("nct"), rec.get("acronym"))
        if x not in (None, "")
    }


def _matches_record(item: dict, rec: dict) -> bool:
    keys = _record_keys(rec)
    want = {str(item.get("key") or "")}
    want.update(str(x) for x in (item.get("alt") or []) if x not in (None, ""))
    return bool(keys & want)


def _term_list_contains(term: str | None, terms: Iterable[str] | None) -> bool:
    t = _norm(term)
    return bool(t) and any(_norm(x) == t for x in (terms or []))


def _entry_condition_terms(inc: dict) -> list[str]:
    return list(inc.get("entry_condition_any") or []) or (
        list(inc.get("population_any") or []) + list(inc.get("population_any_extra") or [])
    )


def population_exclusion(
    poptext: str,
    inc: dict,
    has: Callable[[str, Iterable[str] | None], str | None],
    all_occurrences_qualified: Callable[[str, str, Iterable[str]], bool],
) -> str | None:
    """Return the population_none term that should exclude this record, if any.

    Some population_none terms are entry-condition-only vetoes. They exclude a
    diabetes-only CVOT from an HFrEF review, but they do not exclude an HFrEF
    trial merely because diabetes is a comorbidity or subgroup.
    """
    bad = has(poptext, inc.get("population_none"))
    if bad and all_occurrences_qualified(
        poptext, bad, ("mildly ", "or preserved ", "preserved or ", "mid-range ")
    ):
        bad = None
    if not bad:
        return None
    if _term_list_contains(bad, inc.get("population_none_entry_condition_only")):
        if has(poptext, _entry_condition_terms(inc)):
            return None
    return bad


def comparator_override(rec: dict, inc: dict) -> dict | None:
    """Explicit source-backed comparator satisfaction for sparse registry rows."""
    for item in inc.get("comparator_overrides") or []:
        if _matches_record(item, rec):
            return item
    return None


def contrast_eviction(rec: dict, config: dict) -> dict | None:
    """Configured or minimal all-arms-background contrast eviction."""
    evict = config.get("contrast_evictions") or []
    for item in evict:
        if _matches_record(item, rec):
            return {**item, "contrast_rule": "CONTRAST_ABSENT"}

    if not config.get("exclude_background_intervention_contrast"):
        return None
    inc = config.get("include") or {}
    arms = [str(x) for x in (rec.get("interventions") or []) if str(x).strip()]
    active = [a for a in arms if not _CONTROL.search(a)]
    if len(active) < 2:
        return None
    for term in inc.get("intervention_any") or []:
        needle = _norm(term)
        if not needle:
            continue
        if all(needle in _norm(a) for a in active):
            return {
                "key": rec.get("id"),
                "trial": rec.get("acronym") or rec.get("id"),
                "contrast_rule": "CONTRAST_ABSENT",
                "basis": (
                    f"all cached registry intervention arms contain {term}; "
                    "the randomised contrast is a different intervention"
                ),
            }
    return None


def _randomised_interest_differs(rec: dict, config: dict) -> bool:
    inc = config.get("include") or {}
    arms = [str(x) for x in (rec.get("interventions") or []) if str(x).strip()]
    if len(arms) < 2:
        return False
    active_or_control = [a for a in arms if a]
    for term in inc.get("intervention_any") or []:
        needle = _norm(term)
        if not needle:
            continue
        hits = [needle in _norm(a) and not _CONTROL.search(a) for a in active_or_control]
        if any(hits) and not all(hits):
            return True
    return False


def completeness_state(rec: dict, config: dict) -> str | None:
    for item in config.get("completeness_states") or []:
        if _matches_record(item, rec):
            return item.get("state")
    return None


def annotate_decision(row: dict, rec: dict, config: dict) -> None:
    """Attach additive metadata fields to a screen decision in place."""
    if rec.get("id_type") == "nct" or str(rec.get("id", "")).upper().startswith("NCT"):
        for key in REGISTRY_FIELD_KEYS:
            row[key] = rec.get(key)
    if row.get("decision") != "include":
        return
    if _randomised_interest_differs(rec, config):
        row["contrast_rule"] = "RANDOMISED_CONTRAST_PRESENT"
    if state := completeness_state(rec, config):
        row["completeness_state"] = state
