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


_ARM_TERMS: set | None = None


def arm_name_terms() -> set:
    """population_none terms that name an ARM (an agent), from harness/data/population_term_classes.json -- derived
    from the versioned AACT snapshot + WHO INN stems by scripts/build_population_term_classes.py, never typed by hand.
    A missing artefact raises: a population rule silently matching arm names again is the failure this prevents."""
    global _ARM_TERMS
    if _ARM_TERMS is None:
        import json
        import os
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "population_term_classes.json")
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
        _ARM_TERMS = {_norm(t) for rows in d["topics"].values() for t, r in rows.items() if r["class"] == "ARM_NAME"}
    return _ARM_TERMS


def population_descriptors(inc: dict) -> list:
    """The population_none terms a POPULATION rule (X2) may match: never an arm name -- the topic's own intervention /
    comparator terms, or an agent (arm_name_terms). O'Neil 2018 (semaglutide vs liraglutide vs placebo, adults with
    obesity) was excluded as 'wrong population: title mentions liraglutide' -- a word about the arms read as a word about
    who was enrolled, the condition-as-outcome family (Mahmood 3 Oct)."""
    arms = arm_name_terms() | {_norm(t) for k in ("intervention_any", "comparator_any") for t in inc.get(k) or []}
    return [t for t in inc.get("population_none") or [] if _norm(t) not in arms]


def misfiled_form_terms(inc: dict) -> list:
    """Arm-name terms in population_none that name a FORM of OUR OWN intervention ('oral semaglutide' in a once-weekly
    subcutaneous semaglutide protocol): taken out of the population rule, they are applied where they belong -- the
    intervention-form exclusion (X3, like intervention_none). Arm names of OTHER agents ('liraglutide') are not re-filed:
    an active arm beside a placebo-controlled contrast of ours is not an exclusion; the comparator rule decides."""
    ours = [_norm(t) for t in inc.get("intervention_any") or [] if _norm(t)]
    out = []
    for t in inc.get("population_none") or []:
        n = _norm(t)
        if n in arm_name_terms() and n not in ours and any(re.search(rf"\b{re.escape(o)}\b", n) for o in ours):
            out.append(t)
    return out


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
    bad = has(poptext, population_descriptors(inc))
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
