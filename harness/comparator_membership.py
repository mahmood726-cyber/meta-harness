"""COMPARATOR MEMBERSHIP stated by the comparator itself (lane G1, doac-vte-recurrence).

A comparator's trial list is sometimes seeded from its REFERENCE LIST (unit_source REFERENCE_SEED), and a reference is
not necessarily an included trial: van Es 2014 (PMID 24963045) cites Majeed 2013 (PMID 24081972), a pooled analysis of
major bleeding across 5 dabigatran phase III trials (one of them in atrial fibrillation), beside its 6 included VTE
trials. Its own abstract states the membership: '6 phase 3 trials including a total of 27,023 patients'.

A reference-seeded unit leaves the eligible denominator ONLY when all of these hold, each verbatim in a held record:
  1. the comparator's abstract STATES its trial count k (stated_trial_count);
  2. our matched trials number exactly k (so the stated set is accounted for without the unit);
  3. the unit's own record STATES that it pools several trials (pooled_unit_span).
Anything less leaves it an eligible open gap (Mahmood 3 Oct: a denominator never shrinks on an unevidenced claim).
"""
from __future__ import annotations

import re
from typing import Any

RULE_ID = "COMPARATOR_STATED_K"

_WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
          "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
          "eighteen": 18, "nineteen": 19, "twenty": 20}
_K = r"(?P<k>\d{1,3}|" + "|".join(_WORDS) + r")"
# '6 phase 3 trials including a total of 27,023 patients' / 'eight randomized controlled trials involving 10,000 participants'
STATED_K = re.compile(_K + r"\s+(?:phase\s+(?:3|III|three)\s+)?(?:randomi[sz]ed\s+)?(?:controlled\s+)?(?:clinical\s+)?"
                      r"(?:trials|RCTs|studies)\s+(?:including|enrolling|involving|with|of|comprising)\s+"
                      r"(?:a\s+total\s+of\s+)?(?P<n>\d{1,3}(?:,\d{3})+|\d{2,7})\s+(?:patients|participants|subjects)\b",
                      re.I)
# the unit pools several trials: 'enrolled in 5 phase III trials', 'pooled analysis of', 'data from 4 randomized trials'
POOLED_UNIT = re.compile(r"\b(?:enrolled|included|participating|randomi[sz]ed)\s+in\s+" + _K +
                         r"\s+(?:\w+\s+){0,3}?trials\b|\bpooled\s+analysis\s+of\b|\bdata\s+from\s+" + _K.replace("?P<k>", "?:") +
                         r"\s+(?:\w+\s+){0,3}?trials\b", re.I)


def _int(k: str) -> int:
    return int(k) if k.isdigit() else _WORDS[k.lower()]


def _sentence(text: str, m: re.Match) -> str:
    a = max(text.rfind(". ", 0, m.start()) + 2, 0) if text.rfind(". ", 0, m.start()) >= 0 else 0
    b = text.find(". ", m.end())
    return text[a: (len(text) if b < 0 else b + 1)].strip()


def stated_trial_count(abstract: str) -> dict[str, Any] | None:
    """The comparator's own statement of how many trials (and patients) it pooled, with its verbatim sentence; None
    when it states no count, or states two different counts (no single membership)."""
    hits = list(STATED_K.finditer(abstract or ""))
    ks = {_int(m.group("k")) for m in hits}
    if len(ks) != 1:
        return None
    m = hits[0]
    return {"k": _int(m.group("k")), "n_patients": int(m.group("n").replace(",", "")),
            "span": {"field": "abstract", "text": _sentence(abstract, m), "match": m.group(0)}}


def pooled_unit_span(abstract: str) -> dict[str, Any] | None:
    """The unit's own words saying it pools several trials (verbatim sentence), or None."""
    m = POOLED_UNIT.search(abstract or "")
    if not m:
        return None
    k = m.groupdict().get("k")
    if k and _int(k) < 2:
        return None
    return {"field": "abstract", "text": _sentence(abstract, m), "match": m.group(0)}


def not_an_included_trial(comparator_abstract: str, k_matched: int, unit_abstract: str,
                          unit_source: str | None) -> dict[str, Any] | None:
    """The named difference for a reference-seeded unit outside the comparator's stated membership, or None."""
    if unit_source != "REFERENCE_SEED":
        return None
    st = stated_trial_count(comparator_abstract)
    if not st or st["k"] != k_matched:
        return None
    sp = pooled_unit_span(unit_abstract)
    if not sp:
        return None
    # a GATE, not a protocol rule: the exclusion is the comparator's own stated membership, not our eligibility
    return {"kind": "NOT_AN_INCLUDED_TRIAL", "rule_id": RULE_ID, "span": sp,
            "gate": f"{RULE_ID}: comparator states {st['k']} trials == {k_matched} matched; unit pools several trials "
                    f"(harness/comparator_membership.py)",
            "comparator_span": st["span"], "comparator_stated_k": st["k"], "comparator_stated_patients": st["n_patients"],
            "basis": (f"the comparator states {st['k']} trials; {k_matched} are matched; this reference seed is itself a "
                      f"pooled analysis of several trials, not one of them")}
