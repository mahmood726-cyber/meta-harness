"""STRATEGY CONTINUITY: "longest follow-up" means the longest follow-up while the RANDOMISED STRATEGIES are the same
(sacubitril-HFrEF review, 2026-09-28, hash 0d5f8f77; retrospective, Dispatch under Mahmood's delegation).

PIONEER-HF: weeks 0-8, sacubitril/valsartan vs enalapril, double-blind; at week 8 the enalapril patients were switched to
open-label sacubitril/valsartan, so weeks 8-12 compare EARLY vs DELAYED initiation. The 12-week HR 0.69 (0.49-0.97) is therefore an
early-vs-delayed estimate, not sacubitril/valsartan vs enalapril. A switch splits follow-up into PERIODS, each with its own
contrast and blinding; a result whose timepoint lies past a switch belongs to the later period and never stands in for the
randomised contrast. Periods are read from held text only; with no stated switch the periods are NOT_STATED, never assumed.
"""
from __future__ import annotations

import re
from typing import Any

_SWITCH = re.compile(
    r"(?i)(?:after|at|from|beyond)\s+(?:week|wk)\s*(?P<wk>\d{1,3})\b[^.;]{0,160}?\b(?:switched|transitioned|crossed\s+over|"
    r"changed|converted)\s+to\s+(?:open[- ]label\s+)?(?P<to>[a-z][a-z0-9/ -]{2,60}?)(?=[,.;)]|\s+for\b|\s+until\b|$)"
    r"|(?P<from>[a-z][a-z0-9/ -]{2,40}?)\s+(?:group|arm|patients)\s+(?:were\s+|was\s+)?(?:switched|transitioned|crossed\s+over)\s+to\s+"
    r"(?:open[- ]label\s+)?(?P<to2>[a-z][a-z0-9/ -]{2,60}?)\s+(?:at|after|from)\s+(?:week|wk)\s*(?P<wk2>\d{1,3})\b")
_OPEN_LABEL_PHASE = re.compile(r"(?i)open[- ]label\s+(?:extension|phase|period)[^.;]{0,80}?\b(?:week|wk)s?\s*(?P<a>\d{1,3})\s*(?:-|–|to|through)\s*"
                               r"(?:week|wk)?\s*(?P<b>\d{1,3})")
# "a 36-week open-label extension ... following a 16-week, randomized, placebo-controlled, double-blind period" (30800562)
_OLE_AFTER_RANDOMISED = re.compile(r"(?i)open[- ]label\s+extension[^.;]{0,120}?following\s+(?:a|an)\s+(?P<n>\d{1,3})[- ](?P<u>week|day|month)s?\b"
                                   r"[^.;]{0,60}?\b(?:randomi[sz]ed|double[- ]blind)")
# "a 7-day, randomized, double-blind ... trial with a 6-month open-label extension phase" (41879760)
_RANDOMISED_THEN_OLE = re.compile(r"(?i)(?P<n>\d{1,3})[- ](?P<u>week|day|month)s?\b,?\s+randomi[sz]ed[^.;]{0,120}?\bwith\s+(?:a|an)\s+[^.;]{0,20}?"
                                  r"open[- ]label\s+extension")
# a switch with no stated timing: "patients on high-dose therapy were crossed over to low-dose therapy" (19853510); "patients will be
# switched to placebo in the experimental arm" (40442449)
_UNTIMED_SWITCH = re.compile(r"(?i)\b(?:patients|participants)\b[^.;]{0,80}?\b(?:were|will\s+be)\s+(?:switched|crossed\s+over|transitioned)\s+to\b"
                             r"(?P<to>[^.;]{2,60})")
_TO_WEEKS = {"week": 1.0, "day": 1 / 7.0, "month": 4.345}
_TIMEPOINT = re.compile(r"(?i)(?:at|through|to|after|over)\s+(?:week|wk)\s*(\d{1,3})\b|\b(\d{1,3})[- ]weeks?\b|\bweek\s*(\d{1,3})\b")


def periods(text: str | None) -> dict[str, Any]:
    """The randomised periods stated in held text: [{from_week, to_week, contrast, blinding, basis}], or NOT_STATED."""
    t = text or ""
    m = _SWITCH.search(t)
    ol = _OPEN_LABEL_PHASE.search(t)
    if not m and not ol:
        for rx in (_OLE_AFTER_RANDOMISED, _RANDOMISED_THEN_OLE):
            mm = rx.search(t)
            if mm:
                wk = round(int(mm.group("n")) * _TO_WEEKS[mm.group("u").lower()], 2)
                return {"state": "SWITCH_STATED", "switch_week": wk, "switched_to": "open-label treatment",
                        "basis": mm.group(0)[:300],
                        "periods": [
                            {"from_week": 0, "to_week": wk, "contrast": "the randomised comparison", "blinding": "as randomised"},
                            {"from_week": wk, "to_week": None, "contrast": "open-label extension (no randomised contrast)",
                             "blinding": "open-label"}]}
        um = _UNTIMED_SWITCH.search(t)
        if um:
            return {"state": "SWITCH_STATED_TIMING_NOT_STATED", "switch_week": None, "switched_to": um.group("to").strip(),
                    "basis": um.group(0)[:300], "periods": []}
        return {"state": "NOT_STATED", "periods": []}
    if m:
        wk = int(m.group("wk") or m.group("wk2"))
        to = (m.group("to") or m.group("to2") or "").strip()
        basis = m.group(0)
    else:
        wk, to, basis = int(ol.group("a")), "the open-label treatment", ol.group(0)
    return {"state": "SWITCH_STATED", "switch_week": wk, "switched_to": to, "basis": basis[:300],
            "periods": [
                {"from_week": 0, "to_week": wk, "contrast": "the randomised comparison", "blinding": "as randomised"},
                {"from_week": wk, "to_week": None, "contrast": f"EARLY vs DELAYED {to}".strip(), "blinding": "open-label",
                 "note": "after the switch both arms receive the switched-to treatment: the contrast is timing, not drug"}]}


def timepoint_weeks(text: str | None) -> int | None:
    vals = [int(g) for m in _TIMEPOINT.finditer(text or "") for g in m.groups() if g]
    return max(vals) if vals else None


def continuity(row: dict[str, Any], held_text: str | None) -> dict[str, Any] | None:
    """None when no switch is stated. Otherwise the period the row's timepoint falls in; STRATEGY_CHANGED when it lies past the
    switch (the row estimates early vs delayed initiation, not the randomised contrast)."""
    pr = periods(held_text)
    if pr["state"] == "SWITCH_STATED_TIMING_NOT_STATED":
        # a switch is stated but not when: the row cannot be placed before it -- flagged, never assumed to be randomised follow-up
        return {**pr, "state": "CONTINUITY_NOT_ESTABLISHED", "row_week": None,
                "reason": "the held text states a switch of strategy without its timing; this result is not shown to lie within the randomised period"}
    if pr["state"] != "SWITCH_STATED":
        return None
    wk = row.get("timeframe_weeks")
    if wk is None:
        wk = timepoint_weeks(str(row.get("source") or ""))
    if wk is None:
        return {**pr, "state": "TIMEPOINT_NOT_STATED", "row_week": None}
    if float(wk) > pr["switch_week"]:
        return {**pr, "state": "STRATEGY_CHANGED", "row_week": wk,
                "reason": (f"the result is at week {wk:g}, after the week-{pr['switch_week']} switch to {pr['switched_to']}: it "
                           f"estimates {pr['periods'][1]['contrast']}, not the randomised comparison")}
    return {**pr, "state": "WITHIN_RANDOMISED_PERIOD", "row_week": wk}
