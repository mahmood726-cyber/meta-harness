"""Unit-of-analysis detection (ME-26/27): flag a pooled trial that is CLUSTER-randomized or CROSSOVER.

Pooling a cluster-randomized trial's patient-level counts without a design-effect (ICC) adjustment
understates its variance; pooling a crossover trial as a parallel-arm 2x2 ignores within-subject pairing.
The harness cannot compute the design effect (the ICC is essentially never reported), so this is a
RENDERED DISCLOSURE, not an adjustment: it names the trials whose design needs a unit-of-analysis
caveat so a reader is not misled that they were pooled as simple parallel-arm trials.

Conservative on purpose: only STRONG design phrases fire (a bare 'multicenter'/'by center' must NOT),
so a real cluster/crossover design is disclosed while an ordinary multicentre parallel trial is not.
Pure and fixture-tested; runs on the committed abstract text, so it replays offline and reproduces.
"""
from __future__ import annotations

import re

_CLUSTER = re.compile(r"cluster[-\s]?randomi[sz]ed|cluster[-\s]?randomisation|randomi[sz]ed\s+by\s+"
                      r"(?:hospital|ward|clinic|cluster|icu|unit|site)\b", re.I)
_CROSSOVER = re.compile(r"\b(?:multiple[-\s]?crossover|double[-\s]?crossover|cross[-\s]?over\s+"
                        r"(?:trial|design|study)|two[-\s]?period\s+crossover)\b", re.I)


def detect(text: str) -> str | None:
    """Return 'cluster-randomized', 'crossover', 'cluster-randomized crossover', or None.
    A crossover marker alone fires only for a DESIGN phrase (not the word 'crossover' in passing)."""
    if not text:
        return None
    cl = bool(_CLUSTER.search(text))
    co = bool(_CROSSOVER.search(text))
    if cl and co:
        return "cluster-randomized crossover"
    if cl:
        return "cluster-randomized"
    if co:
        return "crossover"
    return None


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
            design = detect(text)
            if design:
                seen.add(pid)
                m = _CLUSTER.search(text) or _CROSSOVER.search(text)
                span = text[max(0, m.start() - 20):m.end() + 40] if m else ""
                out.append({"id": t.get("id"), "design": design,
                            "span": re.sub(r"\s+", " ", span).strip()})
    return out
