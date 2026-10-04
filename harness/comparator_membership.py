"""COMPARATOR MEMBERSHIP stated by the comparator itself (lane G1, doac-vte-recurrence).

A comparator's trial list is sometimes seeded from its REFERENCE LIST (unit_source REFERENCE_SEED), and a reference is
not necessarily an included trial: van Es 2014 (PMID 24963045) cites Majeed 2013 (PMID 24081972), a pooled analysis of
major bleeding across 5 dabigatran phase III trials (one of them in atrial fibrillation), beside its 6 included VTE
trials. Its own abstract states the membership: '6 phase 3 trials including a total of 27,023 patients'.

This gate SHRINKS a denominator, so it fails closed. A reference-seeded unit leaves the eligible set ONLY when all hold:
  1. the comparator's abstract states ONE trial count k for ITSELF -- not in a BACKGROUND / INTRODUCTION section, not a
     previous / earlier / cited review's count, not an identified-before-screening or 'of which' count, not a subgroup's,
     not a range (stated_trial_count);
  2. our matched trials number exactly k, each a DISTINCT report, and the unit is not one of them;
  3. the unit is itself a pooled analysis: PubMed types it Meta-Analysis, or its TITLE says pooled / combined analysis;
  4. its own record says it pools several trials, outside a BACKGROUND section and never of 'this (single) trial'
     (pooled_unit_span).
Cross-vendor review NR-C22 (Codex) found each condition's hole; every one is planted (tests/test_g1_doac_adversarial.py).
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
STATED_K = re.compile(r"(?<![\d-])" + _K + r"\s+(?:phase\s+(?:3|III|three)\s+)?(?:randomi[sz]ed\s+)?(?:controlled\s+)?"
                      r"(?:clinical\s+)?(?:trials|RCTs|studies)\s+(?:including|enrolling|involving|with|of|comprising|in)\s+"
                      r"(?:a\s+total\s+of\s+)?(?P<n>\d{1,3}(?:,\d{3})+|\d{2,7})\s+(?:patients|participants|subjects)\b",
                      re.I)
# a count sentence that is NOT this review's own inclusion count (NR-C22)
_NOT_OWN_COUNT = re.compile(r"\b(?:previous|prior|earlier|former|another|other|cited|identified|screened|screening|"
                            r"retrieved|searched|before|of which|subgroup|subset|stratum|strata)\b|\d\s*[-–]\s*\d", re.I)
# a section label that puts a sentence in the BACKGROUND
_SECTION = re.compile(r"\b(BACKGROUND|INTRODUCTION|CONTEXT|OBJECTIVES?|AIMS?|PURPOSE|METHODS(?: AND RESULTS)?|"
                      r"RESULTS|FINDINGS|CONCLUSIONS?|INTERPRETATION|DISCUSSION)\s*:", re.I)
_BACKGROUND = {"background", "introduction", "context"}
# the unit pools several trials: '<patients/individuals/bleeds ...> enrolled in 5 phase III trials', 'data from 4 trials',
# 'pooled analysis of <trials>' -- never 'participating in' (investigators), never of 'this (single) trial'
POOLED_UNIT = re.compile(r"\b(?:patients|individuals|participants|subjects|bleeds|events)\b[^.;]{0,60}?\b(?:enrolled|included|"
                         r"randomi[sz]ed)\s+in\s+" + _K + r"\s+(?:[\w-]+\s+){0,3}?trials\b|"
                         r"\bdata\s+from\s+" + _K.replace("?P<k>", "?:") + r"\s+(?:[\w-]+\s+){0,3}?trials\b", re.I)
_THIS_TRIAL = re.compile(r"\bth(?:is|e present)\s+(?:single\s+)?(?:randomi[sz]ed\s+)?(?:controlled\s+)?trial\b", re.I)
_TITLE_POOLED = re.compile(r"\b(?:pooled|combined|integrated)\s+analys[ie]s\b|\bmeta-analys[ie]s\b", re.I)


def _int(k: str) -> int:
    return int(k) if k.isdigit() else _WORDS[k.lower()]


def _section_at(text: str, pos: int) -> str | None:
    lab = None
    for m in _SECTION.finditer(text, 0, pos):
        lab = m.group(1).lower()
    return lab


def _sentence(text: str, m: re.Match) -> str:
    i = text.rfind(". ", 0, m.start())
    a = i + 2 if i >= 0 else 0
    b = text.find(". ", m.end())
    return text[a: (len(text) if b < 0 else b + 1)].strip()


def stated_trial_count(abstract: str) -> dict[str, Any] | None:
    """The comparator's own statement of how many trials (and patients) IT pooled, with its verbatim sentence. None when
    it states none, two different ones, or only a count that is not its own (background, previous review, identified
    before screening, 'of which', subgroup, range)."""
    own = []
    for m in STATED_K.finditer(abstract or ""):
        sent = _sentence(abstract, m)
        if _NOT_OWN_COUNT.search(sent) or (_section_at(abstract, m.start()) or "") in _BACKGROUND:
            continue
        own.append((m, sent))
    if len({_int(m.group("k")) for m, _ in own}) != 1:
        return None
    m, sent = own[0]
    return {"k": _int(m.group("k")), "n_patients": int(m.group("n").replace(",", "")),
            "span": {"field": "abstract", "text": sent, "match": m.group(0)}}


def pooled_unit_span(abstract: str) -> dict[str, Any] | None:
    """The unit's own words saying IT pools several trials (verbatim sentence), or None."""
    for m in POOLED_UNIT.finditer(abstract or ""):
        k = m.groupdict().get("k")
        if k and _int(k) < 2:
            continue
        sent = _sentence(abstract, m)
        if (_section_at(abstract, m.start()) or "") in _BACKGROUND or _THIS_TRIAL.search(sent):
            continue
        return {"field": "abstract", "text": sent, "match": m.group(0)}
    return None


def not_an_included_trial(comparator_abstract: str, k_matched: int, unit_abstract: str, unit_source: str | None, *,
                          unit_pubtypes=(), unit_title: str = "", unit_pmid: str | None = None,
                          matched_pmids=()) -> dict[str, Any] | None:
    """The named difference for a reference-seeded unit outside the comparator's stated membership, or None."""
    if unit_source != "REFERENCE_SEED":
        return None
    matched = [str(p) for p in matched_pmids or []]
    if len(set(matched)) != k_matched or (unit_pmid and str(unit_pmid) in set(matched)):
        return None                                       # matched reports not distinct, or the unit IS a matched report
    if not (any("meta-analysis" in str(p).lower() for p in unit_pubtypes or []) or _TITLE_POOLED.search(unit_title or "")):
        return None                                       # the unit is not itself typed / titled as a pooled analysis
    st = stated_trial_count(comparator_abstract)
    if not st or st["k"] != k_matched:
        return None
    sp = pooled_unit_span(unit_abstract)
    if not sp:
        return None
    # a GATE, not a protocol rule: the exclusion is the comparator's own stated membership, not our eligibility
    return {"kind": "NOT_AN_INCLUDED_TRIAL", "rule_id": RULE_ID, "span": sp,
            "gate": f"{RULE_ID}: comparator states {st['k']} trials == {k_matched} distinct matched reports; the unit is a "
                    f"pooled analysis of several trials (harness/comparator_membership.py)",
            "comparator_span": st["span"], "comparator_stated_k": st["k"], "comparator_stated_patients": st["n_patients"],
            "unit_pubtypes": list(unit_pubtypes or []),
            "basis": (f"the comparator states {st['k']} trials; {k_matched} distinct trials are matched; this reference "
                      f"seed is itself a pooled analysis of several trials, not one of them")}
