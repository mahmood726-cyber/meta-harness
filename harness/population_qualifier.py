"""POPULATION QUALIFIER of a single-trial (k=1) result, DERIVED from the trial's own held text (lane NR V1.0.1; tocilizumab
COVID review).

A k=1 result is the trial's own result, never a synthesis, and it holds only in the trial's own population. RECOVERY-
tocilizumab randomised hospitalised adults with COVID-19 only if they had BOTH hypoxia (oxygen saturation <92% on air or
requiring oxygen therapy) AND systemic inflammation (C-reactive protein >=75 mg/L), and 82% were receiving systemic
corticosteroids; served under the question 'In hospitalised adults with COVID-19 ...' it read as all hospitalised COVID-19.
The qualifier is read from the eligibility sentence and the co-treatment sentence of the held abstract / full text, with
the spans quoted; nothing is asserted, and a trial whose text states no restriction gets no qualifier.
"""
from __future__ import annotations

import re
from typing import Any

RULE_ID = "population_qualifier:eligibility_and_cotreatment_v1"

# an ELIGIBILITY sentence (who could be randomised), not a result or background sentence
_ELIGIBILITY_SENTENCE = re.compile(r"\b(?:were|was)\s+eligible\b|\beligib(?:le|ility)\s+(?:for|criteria)\b|"
                                   r"\binclusion\s+criteria\b|\bwere\s+(?:enrolled|randomi[sz]ed)\s+if\b", re.I)
# restricting conditions named in it (each kept with its own parenthetical definition when the text gives one)
_RESTRICTION = re.compile(
    r"\b(?:hypoxi(?:a|c)|systemic\s+inflammation|respiratory\s+failure|requiring\s+(?:supplemental\s+)?oxygen|"
    r"(?:invasive\s+)?mechanical(?:ly)?\s+ventilat\w*|elevated\s+(?:c-reactive\s+protein|crp|ferritin|d-dimer|il-6))"
    r"(?:\s*\([^()]{3,120}\))?", re.I)
# the share of participants on a named co-treatment: '3385 (82%) patients receiving systemic corticosteroids'
_COTREATMENT = re.compile(
    r"(?:\d[\d,\s]*\(\s*)?(\d{1,3}(?:[.·]\d)?)\s*%\s*\)?\s*(?:of\s+)?(?:patients|participants)?\s*"
    r"(?:were\s+)?(?:receiving|received|on|treated\s+with)\s+((?:systemic\s+)?(?:corticosteroids?|dexamethasone|"
    r"steroids?|remdesivir|anticoagula\w+))", re.I)
_SENT = re.compile(r"(?<=[.;])\s+(?=[A-Z])")
_WS = re.compile(r"\s+")


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT.split(_WS.sub(" ", text or "")) if s.strip()]


def derive(record: dict[str, Any] | None, exclude_terms=()) -> dict[str, Any] | None:
    """{'restrictions': [...], 'eligibility_span', 'co_treatment': {...}|None, 'rule_id'} or None when the held text
    states no restriction and no co-treatment share. A 'co-treatment' that is the review's own intervention
    (`exclude_terms`, e.g. corticosteroids in a corticosteroid review) is the randomised arm, not a co-treatment."""
    excluded = [str(x).lower() for x in exclude_terms or () if str(x).strip()]
    text = " ".join(x for x in ((record or {}).get("abstract"), (record or {}).get("fulltext")) if x)
    restrictions, elig_span, co = [], None, None
    for s in _sentences(text):
        if elig_span is None and _ELIGIBILITY_SENTENCE.search(s):
            found = [_WS.sub(" ", m.group(0)).strip() for m in _RESTRICTION.finditer(s)]
            if found:
                restrictions, elig_span = list(dict.fromkeys(found)), s
        if co is None:
            m = _COTREATMENT.search(s)
            if m and not any(x in m.group(2).lower() or m.group(2).lower().rstrip("s") in x for x in excluded):
                co = {"share_pct": float(m.group(1).replace("·", ".")), "treatment": m.group(2).lower(),
                      "text": f"{m.group(1).replace(chr(183), '.')}% receiving {m.group(2).lower()}", "span": s}
    if not restrictions and not co:
        return None
    return {"restrictions": restrictions, "eligibility_span": elig_span, "co_treatment": co, "rule_id": RULE_ID}


def served_text(qualifier: dict[str, Any] | None) -> str | None:
    """The served population qualifier for the result: the trial's own population, never the whole question population."""
    if not qualifier:
        return None
    bits = []
    if qualifier.get("restrictions"):
        bits.append("only participants with " + " and ".join(qualifier["restrictions"]))
    if qualifier.get("co_treatment"):
        bits.append(qualifier["co_treatment"]["text"])
    return "; ".join(bits)


def single_trial_violations(review: dict[str, Any], records: dict[str, Any] | None, page_text: str | None,
                            exclude_terms=()) -> list[dict[str, Any]]:
    """Detector (pre-fix and post-fix outputs alike): a PRIMARY k=1 result served as a synthesis ('Trials pooled (k) 1'),
    or served without the population qualifier its own held text derives. Derives the qualifier itself from `records`."""
    bad = []
    text = page_text or ""
    for o in review.get("outcomes") or []:
        res = o.get("result") or {}
        if not o.get("primary") or res.get("k") != 1 or res.get("present") is False or len(o.get("trials") or []) != 1:
            continue
        t = o["trials"][0]
        pid = str(t.get("id", "")).replace("PMID ", "").strip()
        if "Trials pooled (k) 1" in text:
            bad.append({"outcome": o.get("name"), "trial": t.get("id"), "kind": "K1_SERVED_AS_SYNTHESIS",
                        "detail": "the overview labels the single trial 'Trials pooled (k) 1'"})
        q = derive((records or {}).get(pid), exclude_terms)
        if q and q.get("restrictions"):
            shown = "Population of this result" in text and all(r.split(" (")[0] in text for r in q["restrictions"])
            if not shown:
                bad.append({"outcome": o.get("name"), "trial": t.get("id"), "kind": "K1_POPULATION_UNQUALIFIED",
                            "detail": "served without its own population: " + served_text(q)})
    return bad
