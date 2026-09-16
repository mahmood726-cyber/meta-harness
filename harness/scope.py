"""Comparator SCOPE-MATCH (PICO-match) — a machine field decided by one uniform rule for every topic.

A comparator is a valid benchmark only if it answers the SAME question. The decisive axis is
intervention LEVEL: a SINGLE-drug topic benchmarked against a drug-CLASS meta-analysis is a PICO
mismatch (the NMA error class — the network is not one drug), even when the class meta names our drug,
and the k difference is then a SCOPE difference, not unretrieved evidence. Computed in-pipeline from
the config + comparator title (deterministic, replay-safe). The rule is fixed here and applied
uniformly — it validates same-scope comparators (including low-k topics) and flags class-vs-single
ones regardless of which way it makes a page look.
"""
from __future__ import annotations

_CLASS_TERMS = ("inhibitors", "antagonists", "agonists", "sglt2", "sglt-2", "glp-1", "glp1",
                "mineralocorticoid receptor", "statins", "anticoagulants", "receptor blocker",
                "beta-blockers", "ace inhibitor", " arb ", "doac", "noac", "crystalloids")


def _has_class(text: str) -> bool:
    t = (text or "").lower()
    return any(c in t for c in _CLASS_TERMS)


def _has_any(text, terms) -> bool:
    t = (text or "").lower()
    return any(x and x.lower() in t for x in terms or [])


def assess(config: dict, comparator_title: str, comparator_abstract: str = "") -> dict:
    inc = config.get("include", {})
    topic_terms = (config.get("intervention_terms") or []) + (inc.get("intervention_any") or [])
    class_terms = tuple(config.get("intervention_class_terms") or ()) + _CLASS_TERMS
    topic_is_class = _has_class(" ".join(topic_terms)) or _has_any(" ".join(topic_terms), class_terms)
    comparator_is_class = _has_class(comparator_title) or _has_any(comparator_title, class_terms)
    iv_level_match = not (comparator_is_class and not topic_is_class)
    pop = _has_any((comparator_title or "") + " " + (comparator_abstract or ""), inc.get("population_any") or [])
    valid = bool(iv_level_match and pop)
    if valid:
        note = "same-question comparator (matching intervention level and population)"
    elif not iv_level_match:
        note = ("comparator is a DRUG-CLASS meta-analysis while this topic is a single agent — a PICO "
                "scope mismatch (single-drug review vs class-level review); the k difference vs this "
                "comparator is a scope difference, not unretrieved evidence")
    else:
        note = "comparator population does not clearly match the topic"
    return {"topic_is_class": topic_is_class, "comparator_is_class": comparator_is_class,
            "intervention_level_match": iv_level_match, "population_match": pop,
            "scope_valid": valid, "note": note}
