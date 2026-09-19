"""Unit-of-analysis detection (ME-26/27): flag a pooled trial with a non-simple-parallel design.

Pooling a cluster-randomized trial's patient-level counts without a design-effect (ICC) adjustment
understates its variance; pooling a crossover trial as a parallel-arm 2x2 ignores within-subject pairing.
The harness cannot compute the design effect (the ICC is essentially never reported), so this is a
RENDERED DISCLOSURE, not an adjustment: it names the trials whose design needs a unit-of-analysis
caveat so a reader is not misled that they were pooled as simple parallel-arm trials.

Conservative on purpose: only STRONG design phrases fire (a bare 'multicenter'/'by center' must NOT),
so a real cluster/crossover/factorial/stepped-wedge design is disclosed while an ordinary multicentre
parallel trial is not.
Pure and fixture-tested; runs on the committed abstract text, so it replays offline and reproduces.
"""
from __future__ import annotations

import re

_CLUSTER = re.compile(r"cluster[-\s]?randomi[sz]ed|cluster[-\s]?randomisation|randomi[sz]ed\s+by\s+"
                      r"(?:hospital|ward|clinic|cluster|icu|unit|site)\b", re.I)
_CROSSOVER = re.compile(r"\b(?:multiple[-\s]?crossover|double[-\s]?crossover|cross[-\s]?over\s+"
                        r"(?:trial|design|study)|two[-\s]?period\s+crossover)\b", re.I)
_FACTORIAL = re.compile(
    r"\b(?:factorial(?:,\s*|\s+)(?:randomi[sz]ed|clinical trial|trial|design|assignment)"
    r"|randomi[sz]ed\b.{0,80}\b\d+\s*(?:x|\u00d7|by)\s*\d+\b.{0,80}\bfactorial"
    r"|randomi[sz]ed\b.{0,120}\bone of four trial margarines\b"
    r"|one of four trial margarines\b.{0,180}\bEPA\b.{0,80}\bDHA\b.{0,80}\bALA\b)\b",
    re.I,
)
_STEPPED_WEDGE = re.compile(r"\bstepped[-\s]?wedge(?:\s+(?:cluster[-\s]?randomi[sz]ed|trial|design|study))?\b", re.I)


def _span(text: str, match: re.Match | None) -> str:
    if not match:
        return ""
    return re.sub(r"\s+", " ", text[max(0, match.start() - 20):match.end() + 40]).strip()


def detect_detail(text: str) -> dict | None:
    """Return a conservative detected design object with a source span, or None."""
    if not text:
        return None
    cl_m = _CLUSTER.search(text)
    co_m = _CROSSOVER.search(text)
    sw_m = _STEPPED_WEDGE.search(text)
    fa_m = _FACTORIAL.search(text)
    if cl_m and co_m:
        m = cl_m if cl_m.start() <= co_m.start() else co_m
        return {"design": "cluster-randomized crossover", "span": _span(text, m)}
    if sw_m:
        return {"design": "stepped-wedge", "span": _span(text, sw_m)}
    if cl_m:
        return {"design": "cluster-randomized", "span": _span(text, cl_m)}
    if co_m:
        return {"design": "crossover", "span": _span(text, co_m)}
    if fa_m:
        return {"design": "factorial", "span": _span(text, fa_m)}
    return None


def detect(text: str) -> str | None:
    """Return a detected design label, or None.
    A crossover marker alone fires only for a DESIGN phrase (not the word 'crossover' in passing)."""
    detail = detect_detail(text)
    return detail["design"] if detail else None


def scan_pooled(review, rec_by_id):
    """Return [{id, design, span}] for every pooled trial (across all outcomes) whose committed abstract
    carries a strong cluster/crossover design phrase. rec_by_id maps pmid -> record (with 'abstract')."""
    seen, out = set(), []
    for o in review.get("outcomes", []) or []:
        for t in o.get("trials", []) or []:
            pid = str(t.get("id", "")).replace("PMID ", "").strip()
            if not pid or pid in seen:
                continue
            rec = rec_by_id.get(pid) or {}
            text = (rec.get("title", "") + " " + rec.get("abstract", "")).strip()
            detail = detect_detail(text)
            if detail:
                seen.add(pid)
                out.append({"id": t.get("id"), "design": detail["design"],
                            "span": detail["span"]})
    return out
