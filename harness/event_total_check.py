"""EVENT-TOTAL CHECK of a whole-pool comparison (lane G1, doac-vte-recurrence).

When our pool and the comparator's are the SAME trials but different measures (our HR, its RR), the numbers cannot be
compared directly. One question is still typed and decidable without arm sizes: can the comparator's printed outcome
RATES over its stated patient total contain the events the trials themselves report for their primary outcome?

  most events the comparator's rates allow  = (larger printed rate + half its last printed digit) x stated total
  events the trials report (held abstracts) = sum of the two arm counts in each trial's primary-outcome sentence

If the trials report MORE events than the comparator's rates can hold, the comparator's outcome is narrower than the
trials' primary outcome (a different definition or window): OUTCOME_EVENTS_EXCEED_COMPARATOR_RATES. Every count is a
verbatim span; a trial whose sentence does not give exactly two counts makes the check NOT_DECIDABLE (never guessed).
"""
from __future__ import annotations

import re
from typing import Any

# a whole count of patients/events: '30 of the 1274 patients', '59 of 2609', '130 patients in the edoxaban group',
# '36 events', '30 of the 1279 dabigatran patients'
_COUNT = re.compile(r"(?<![\d.,])(?P<e>\d{1,5})\s+(?:of\s+(?:the\s+)?(?P<n>\d[\d,]{2,})(?![\d.])|events\b|"
                    r"(?:[A-Za-z-]+\s+)?patients\b)", re.I)
# a sentence about the PRIMARY outcome
_PRIMARY = re.compile(r"\bprimary (?:efficacy )?(?:outcome|end ?point)|\brecurren(?:t|ce)\b", re.I)
# a percentage, as printed
_PCT = re.compile(r"(?<![\d.])(?P<p>\d{1,2}(?:\.\d{1,2})?)\s*%")
_SENT = re.compile(r"(?<=[.;])\s+(?=[A-Z])")


def _sentences(text: str):
    return _SENT.split(re.sub(r"\s+", " ", text or ""))


def trial_event_counts(abstract: str) -> dict[str, Any] | None:
    """The two arm event counts of the trial's primary-outcome result: the FIRST sentence that names the primary outcome
    and holds exactly two whole counts. None when no sentence does (the check is then not decidable)."""
    for s in _sentences(abstract):
        if not _PRIMARY.search(s):
            continue
        cs = list(_COUNT.finditer(s))
        if len(cs) == 2:
            return {"events": [int(c.group("e")) for c in cs], "span": s, "matches": [c.group(0) for c in cs]}
    return None


def comparator_rates(abstract: str, outcome_terms) -> dict[str, Any] | None:
    """The comparator's two printed arm RATES for the outcome: the first sentence naming an outcome term with exactly two
    percentages before its effect estimate."""
    for s in _sentences(abstract):
        low = s.lower()
        if not any(t.lower() in low for t in outcome_terms or [] if t):
            continue
        head = re.split(r"\(\s*(?:relative risk|RR|hazard ratio|HR|odds ratio|OR)\b", s, maxsplit=1)[0]
        ps = [m.group("p") for m in _PCT.finditer(head)]
        if len(ps) == 2:
            return {"rates": ps, "span": s}
    return None


def check(comparator_abstract: str, outcome_terms, stated_patients: int | None, trial_abstracts: dict) -> dict[str, Any]:
    rates = comparator_rates(comparator_abstract, outcome_terms)
    per = {pmid: trial_event_counts(ab) for pmid, ab in trial_abstracts.items()}
    if not rates or not stated_patients or any(v is None for v in per.values()):
        return {"state": "NOT_DECIDABLE", "comparator_rates": rates, "stated_patients": stated_patients,
                "trials_without_two_counts": sorted(p for p, v in per.items() if v is None)}
    hi = max(float(p) + 0.5 * 10 ** -(len(p.split(".")[1]) if "." in p else 0) for p in rates["rates"])
    max_events = hi / 100 * stated_patients
    total = sum(sum(v["events"]) for v in per.values())
    return {"state": "OUTCOME_EVENTS_EXCEED_COMPARATOR_RATES" if total > max_events else "CONSISTENT",
            "trial_events_total": total, "comparator_max_events": round(max_events, 1),
            "comparator_rates": rates, "stated_patients": stated_patients, "per_trial": per,
            "basis": (f"the trials report {total} primary-outcome events; the comparator's printed rates "
                      f"({rates['rates'][0]}% / {rates['rates'][1]}%) over its {stated_patients} patients hold at most "
                      f"{max_events:.0f}")}
