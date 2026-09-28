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
         r"receive|cfu|colony[\s-]forming|sachets?|times\s+(?:a|per)\s+day|"
         # 'starting 48 to 72 hours before surgery and continued for 1 month after surgery' (COPPS-2 25172965)
         r"continu(?:ed|ing|ation)")
# an EXPLICIT ascertainment phrase right after the duration ('14 days of follow-up')
_ASC_AFTER = re.compile(r"^\s*(?:of\s+)?(?:follow[\s-]*up|observation|monitoring|surveillance)\b", re.I)
# a time ANCHOR right after it ('14 days after surgery / randomization'): ascertainment only when nothing in the clause says
# the duration is an administration ('received dexamethasone for 14 days after randomization' is a regimen; NR-C04)
_ANCHOR_AFTER = re.compile(r"^\s*(?:after|following|post-?)\s*(?:the\s+)?(?:surgery|operation|randomi[sz]ation|discharge|"
                           r"enrol\w*|cabg|procedure|index|admission|intervention)\b", re.I)
_DOSE_AFTER = re.compile(r"^\s*(?:of\s+)?(?:treatment|therapy|administration|dosing|study\s+drug|drug|colchicine|"
                         r"supplementation|intervention\s+period)\b|^\s*(?:regimen|course|treatment|therapy)\b", re.I)
_ASC_IMMEDIATE = re.compile(r"\b(?:at|within|until|over|through|throughout|by|up\s+to)\s*$", re.I)
_ASC_RX = re.compile(rf"\b(?:{_ASC})", re.I)
# the clause-level test: the explicit ascertainment words only. 'discharge' is an ANCHOR ('until discharge', '28 days
# after discharge' are read by the preposition/anchor step): 'After discharge, patients received study medication for 14
# days' is a regimen (NR-C07 #3)
_ASC_CLAUSE_RX = re.compile(rf"\b(?:{_ASC.replace('discharge|', '')})", re.I)
# #10: a window BEFORE an enrolment anchor is a history/eligibility window, never a result or follow-up window
# ('Among patients hospitalized within 30 days before randomization, mortality at 90 days was 12%')
_PRIOR_AFTER = re.compile(r"^\s*(?:before|prior\s+to|preceding)\s+(?:the\s+)?(?:randomi[sz]ation|enrol\w*|screening|"
                          r"inclusion|study\s+entry|baseline|admission|surgery|hospitali[sz]ation|index)\b", re.I)
NOT_A_WINDOW = ("DOSING", "PRIOR")
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
    """ASCERTAINMENT, DOSING, PRIOR or UNSTATED for the duration at text[start:end]."""
    text = text or ""
    inside, after = text[start:end], _after(text, end)
    before = _clause_before(text, start)
    # 0. a window before an enrolment anchor is history, not follow-up ('within 30 days before randomization')
    if _PRIOR_AFTER.match(after):
        return "PRIOR"
    # 1. an EXPLICIT ascertainment word in the clause decides: 'assessed at', 'followed for', '14 days of follow-up'
    if _ASC_AFTER.search(after) or _ASC_CLAUSE_RX.search(inside) or _ASC_CLAUSE_RX.search(before):
        return "ASCERTAINMENT"
    # 2. an administration cue in the clause makes it a regimen -- even after 'up to' / 'over' or before 'after
    #    randomization' ('received study treatment for up to 14 days'; NR-C04 #3, #4)
    if _DOSE_AFTER.search(after) or _DOSE_RX.search(inside) or _DOSE_RX.search(before):
        return "DOSING"
    # 3. only then does a bare preposition or anchor read as a window
    if _ASC_IMMEDIATE.search(before) or _ANCHOR_AFTER.search(after):
        return "ASCERTAINMENT"
    return "UNSTATED"


def is_follow_up_evidence(span: str) -> bool:
    """False when the span's evidence for a window is a dosing/treatment duration; True otherwise.

    A span with a duration passes unless every duration in it reads as DOSING. A span with no duration (e.g. 'until the
    discharge from the hospital') passes unless it is a dosing statement with no ascertainment cue at all."""
    span = span or ""
    roles = [duration_role(span, m.start(), m.end()) for m in DURATION.finditer(span)]
    if roles:
        return any(r not in NOT_A_WINDOW for r in roles)
    return bool(_ASC_RX.search(span)) or not _DOSE_RX.search(span)


# The window a RESULT's own sentence states ('By day 28, death had occurred in ...', 'In-hospital mortality did not
# differ ...'): an extracted result's timepoint binds to the sentence that owns THAT result before anything else in the
# text (corticosteroids-cap-mortality review: CAPE COD's day-28 deaths were given the 14-day regimen as follow-up; Torres's
# in-hospital deaths were given the review's own timepoint).
_RESULT_WINDOWS = (
    (re.compile(r"\bin[\s-]hospital\b|\bduring\s+(?:the\s+)?hospital(?:i[sz]ation|\s+stay)\b|\b(?:until|at|before)\s+"
                r"(?:hospital\s+)?discharge\b", re.I), lambda m: "in-hospital"),
    (re.compile(r"\b(?:by|at|through|to|until|within|on)\s+day\s+(\d+)\b", re.I), lambda m: f"{m.group(1)} days"),
    # 'At week 12, mortality was ...' / 'at month 6' (NR-C04 #5)
    (re.compile(r"\b(?:by|at|through|to|until|within|on)\s+(week|month)\s+(\d+)\b", re.I),
     lambda m: f"{m.group(2)} {m.group(1).lower()}{'' if m.group(2) == '1' else 's'}"),
    (re.compile(r"\b(\d+)[\s-](day|week|month|year)\b(?![\s-]*old\b)", re.I),
     lambda m: f"{m.group(1)} {m.group(2).lower()}{'' if m.group(1) == '1' else 's'}"),
    (re.compile(r"\b(?:at|by|within|after|over|through|during)\s+(\d+(?:\.\d+)?)\s*(day|week|month|year)s?\b", re.I),
     lambda m: f"{m.group(1)} {m.group(2).lower()}{'' if m.group(1) == '1' else 's'}"),
)


def result_window(span: str | None, estimates=()):
    """(value, match) for the window the result's OWN span states, or None. Every candidate is checked for dosing (a
    'treatment was stopped on day 14' is not the result's window), and the EARLIEST remaining one wins: it is the window
    that governs the sentence ('At 90 days, mortality among patients discharged by day 28 was 12%' is the 90-day result;
    NR-C04 #14, #16), not whichever pattern happens to be listed first.

    Exception -- an ENUMERATION of per-timepoint results ('at 14 days (7.9% vs. 16.7%; RR: 0.47 ...); at 21 days (...);
    and at 56 days (9.1% vs. 19.6%; RR: 0.46 ...)'): each window owns the result group attached directly to it, so when
    the row's own estimate (`estimates`) sits in the group attached to one window, that window is the row's (PEARL 40488914:
    RR 0.46 is the 56-day result, not the 14-day one). A window followed by a verb ('by day 28 was 12%') has no attached
    group and is never chosen this way."""
    span = span or ""
    found = []
    for rx, value in _RESULT_WINDOWS:
        for m in rx.finditer(span):
            if duration_role(span, m.start(), m.end()) in NOT_A_WINDOW:
                continue
            found.append((m.start(), value(m), m))
    if not found:
        return None
    found.sort(key=lambda x: x[0])
    ests = [float(e) for e in estimates or () if _is_num(e)]
    if ests:
        for i, (_, v, m) in enumerate(found):
            nxt = next((f[0] for f in found[i + 1:] if f[0] >= m.end()), len(span))
            group = span[m.end():nxt]
            nums = _EFFECT_NUM.findall(group)
            # the group's EFFECT is its first number that is not a percentage; a CI bound equal to the estimate is not
            if _ATTACHED.match(group) and nums and any(_same(nums[0], e) for e in ests):
                return v, m
        # no attached group: the CLAUSE that holds the estimate decides ('Clinical cure at 14 days was improved (RR 1.20),
        # whereas major bleeding at 90 days was similar (RR 0.95)' is the 90-day result for RR 0.95)
        for c in _CLAUSE.split(span):
            if any(_same(n, e) for n in _NUM.findall(c) for e in ests):
                lo = span.find(c)
                inside = [f for f in found if lo <= f[0] < lo + len(c)]
                if inside:
                    _, v, m = inside[0]
                    return v, m
                break
    _, v, m = found[0]
    return v, m


_ATTACHED = re.compile(r"\s*[(:\[|]")
_EFFECT_NUM = re.compile(r"(?<![\d.])\d+\.\d+(?![\d.])(?!\s*%)")
_CLAUSE = re.compile(r";|,\s*(?:whereas|while|but)\b|\bwhereas\b")
_NUM = re.compile(r"(?<![\d.])\d+\.\d+(?![\d.])")


def _is_num(x) -> bool:
    try:
        float(x)
        return True
    except (TypeError, ValueError):
        return False


def _same(text_num: str, est: float) -> bool:
    """A number printed in the text equals the estimate at the text's own precision ('0.46' == 0.46; '0.5' == 0.46 no)."""
    places = len(text_num.split(".")[1])
    return abs(float(text_num) - round(est, places)) < 10 ** -(places + 3)
