"""Is a duration in the source an OUTCOME-ASCERTAINMENT window, or a TREATMENT/DOSING duration?

A follow-up window is the period over which the outcome was ascertained ('during 14 days of follow-up', 'assessed at
14 days after surgery', 'until hospital discharge'). A dosing duration is how long the drug was given ('1 mg daily ...
for 14 days', 'a 14-day regimen'). They are different fields: binding a dosing sentence as the follow-up window is a
wrong field link (Farzaneh, PMID 42132185: '... maintenance dose (0.5 mg daily ...) for 14 days' was served as the
follow-up window). Every reader that binds a follow-up value runs its evidence span through is_follow_up_evidence;
a span that fails leaves the window unresolved rather than bound to the regimen.

duration_role(text, start, end) classifies ONE duration match, deciding in this order:
  1. the match itself and the words right after it ('of follow-up' / 'after surgery' -> ASCERTAINMENT;
     'of treatment' / 'regimen' / 'course' -> DOSING)
  2. the word right before it ('at', 'within', 'until', 'over', 'through' -> ASCERTAINMENT)
  3. the rest of its clause before it (an ascertainment cue wins over a dosing cue: 'received 1 mg daily and were
     followed for 14 days' is a follow-up statement)
'followed by' is sequencing ('a loading dose followed by a maintenance dose'), never follow-up.
"""
from __future__ import annotations

import re

DURATION = re.compile(r"\d+(?:\.\d+)?(?:\s*-\s*|\s+)(?:days?|weeks?|months?|years?)\b", re.I)

_ASC = (r"follow(?:ed)?[\s-]*up|followed\s+(?!by\b)|observ\w*|monitor\w*|assess\w*|ascertain\w*|surveillance|"
        r"evaluat\w*|visits?|telemetry|holter|discharge|end\s*points?|outcomes?|record(?:ed|ing)|diar(?:y|ies)")
_DOSE = (r"\d+(?:\.\d+)?\s*(?:mg|mcg|µg|μg|g|iu|ml|units?)\b|daily|twice|once|thrice|b\.?i\.?d|t\.?i\.?d|"
         r"q\.?d|doses?|dosing|dosage|regimens?|tablets?|capsules?|administ\w*|infus\w*|loading|maintenance|"
         r"supplement\w*|given|received|receiving|taking|treated|treatment|therapy|course|"
         # 'followed by tapering for a total of 8 or 14 days' (CAPE COD 36942789) is the regimen, not follow-up
         r"taper\w*|intravenous\w*|orally|per\s+day|"
         # 'randomized to receive Lactobacillus GG, 20 x 10(9) CFU/d, or placebo for 14 days' (11560298, probiotics)
         r"receive|cfu|colony[\s-]forming|sachets?|times\s+(?:a|per)\s+day")
_ASC_AFTER = re.compile(r"^\s*(?:of\s+)?(?:follow[\s-]*up|observation|monitoring|surveillance)\b|"
                        r"^\s*(?:after|following|post-?)\s*(?:the\s+)?(?:surgery|operation|randomi[sz]ation|discharge|"
                        r"enrol\w*|cabg|procedure|index|admission|intervention)\b", re.I)
_DOSE_AFTER = re.compile(r"^\s*(?:of\s+)?(?:treatment|therapy|administration|dosing|study\s+drug|drug|colchicine|"
                         r"supplementation|intervention\s+period)\b|^\s*(?:regimen|course|treatment|therapy)\b", re.I)
_ASC_IMMEDIATE = re.compile(r"\b(?:at|within|until|over|through|throughout|by|up\s+to)\s*$", re.I)
_ASC_RX = re.compile(rf"\b(?:{_ASC})", re.I)
_DOSE_RX = re.compile(rf"(?:{_DOSE})\b", re.I)


# a sentence ends at a single period + whitespace + a capital, "(" or a digit (a sentence may open with a number);
# an ellipsis '...' inside a quoted span is not a sentence end, and '0.5' (no whitespace) is not one either
_SENT_END = re.compile(r"(?<!\.)\.(?!\.)\s+(?=[A-Z(\d])")


def _clause_before(text: str, start: int, reach: int = 90) -> str:
    """The text of the match's own sentence before it, at most `reach` characters."""
    lo = max(0, start - reach)
    # search up to start+1 so a sentence that BEGINS with the match ('...failure). In-hospital mortality') is seen to
    # begin there, and the previous sentence's words are not read as this match's clause
    ends = [m for m in _SENT_END.finditer(text, lo, min(len(text), start + 1)) if m.end() <= start]
    return text[ends[-1].end():start] if ends else text[lo:start]


def _after(text: str, end: int, reach: int = 40) -> str:
    after = text[end:end + reach]
    m = _SENT_END.search(after)
    return after[:m.start()] if m else after


def duration_role(text: str, start: int, end: int) -> str:
    """ASCERTAINMENT, DOSING or UNSTATED for the duration at text[start:end]."""
    text = text or ""
    inside, after = text[start:end], _after(text, end)
    if _ASC_AFTER.search(after) or _ASC_RX.search(inside):
        return "ASCERTAINMENT"
    if _DOSE_AFTER.search(after) or _DOSE_RX.search(inside):
        return "DOSING"
    before = _clause_before(text, start)
    if _ASC_IMMEDIATE.search(before):
        return "ASCERTAINMENT"
    if _ASC_RX.search(before):
        return "ASCERTAINMENT"
    if _DOSE_RX.search(before):
        return "DOSING"
    return "UNSTATED"


def is_follow_up_evidence(span: str) -> bool:
    """False when the span's evidence for a window is a dosing/treatment duration; True otherwise.

    A span with a duration passes unless every duration in it reads as DOSING. A span with no duration (e.g. 'until the
    discharge from the hospital') passes unless it is a dosing statement with no ascertainment cue at all."""
    span = span or ""
    roles = [duration_role(span, m.start(), m.end()) for m in DURATION.finditer(span)]
    if roles:
        return any(r != "DOSING" for r in roles)
    return bool(_ASC_RX.search(span)) or not _DOSE_RX.search(span)


# The window a RESULT's own sentence states ('By day 28, death had occurred in ...', 'In-hospital mortality did not
# differ ...'): an extracted result's timepoint binds to the sentence that owns THAT result before anything else in the
# text (corticosteroids-cap-mortality review: CAPE COD's day-28 deaths were given the 14-day regimen as follow-up; Torres's
# in-hospital deaths were given the review's own timepoint).
_RESULT_WINDOWS = (
    (re.compile(r"\bin[\s-]hospital\b|\bduring\s+(?:the\s+)?hospital(?:i[sz]ation|\s+stay)\b|\b(?:until|at|before)\s+"
                r"(?:hospital\s+)?discharge\b", re.I), lambda m: "in-hospital"),
    (re.compile(r"\b(?:by|at|through|to|until|within|on)\s+day\s+(\d+)\b", re.I), lambda m: f"{m.group(1)} days"),
    (re.compile(r"\b(\d+)[\s-]day\b", re.I), lambda m: f"{m.group(1)} days"),
    (re.compile(r"\b(?:at|by|within|after|over|through|during)\s+(\d+(?:\.\d+)?)\s*(day|week|month|year)s?\b", re.I),
     lambda m: f"{m.group(1)} {m.group(2).lower()}{'' if m.group(1) == '1' else 's'}"),
)


def result_window(span: str | None):
    """(value, match) for the window the result's OWN span states, or None. A dosing duration in the span is skipped."""
    span = span or ""
    for rx, value in _RESULT_WINDOWS:
        for m in rx.finditer(span):
            if DURATION.search(m.group(0)) and duration_role(span, m.start(), m.end()) == "DOSING":
                continue
            return value(m), m
    return None
