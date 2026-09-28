"""SETTING is a design requirement, established only by the trial's OWN design statements (V1.0.1, SGLT2 HHF-in-CVOTs
review).

The protocol's Sept-16 amendment restricts the review to broad cardiovascular outcome trials, executed as "the record
mentions cardiovascular events / outcomes / MACE". SIMPLE (PMID 35061894; 13-week haemodynamics) and EMPA-HEART
(PMID 31434508; 6-month LV mass) passed because their abstracts OPEN with background about other trials ("SGLT2
inhibitors lower cardiovascular events in type 2 diabetes...") and EMPA-HEART's conclusion mentions EMPA-REG OUTCOME.
A background or discussion sentence about cardiovascular benefit never establishes a CVOT design.

With include.design_any_where = "own_design", a setting term counts only where the record states its OWN design:
  - its title (a registry record's title);
  - an abstract sentence that states the trial's own primary end point / outcome / objective;
and never in a BACKGROUND / INTRODUCTION / CONCLUSIONS section. This is separate from outcome availability: a CVOT
that does not report the outcome is still a CVOT, and a mechanistic trial that reports heart-failure events is not.
"""
from __future__ import annotations

import re

_SECTION = re.compile(r"\b([A-Z][A-Z /&]{3,40}):\s")
_CONTEXT = {"BACKGROUND", "INTRODUCTION", "CONTEXT", "RATIONALE", "IMPORTANCE", "CONCLUSIONS", "CONCLUSION",
            "INTERPRETATION", "DISCUSSION", "CONCLUSIONS AND RELEVANCE"}
_OWN = re.compile(r"\b(?:primary (?:efficacy )?(?:end ?point|outcome|composite)|we (?:conducted|performed|designed) "
                  r"(?:a|an|this) [^.]{0,40}(?:outcome|trial))", re.I)


def _sentences(text: str) -> list:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if s.strip()]


def own_design_text(rec: dict) -> list:
    """The record's own design statements: its title, and the abstract sentences (outside context sections) that
    state its own primary end point / outcome."""
    out = [str(rec.get("title") or "")]
    ab = str(rec.get("abstract") or "")
    marks = list(_SECTION.finditer(ab))
    if marks:
        parts = [(m.group(1).strip(), ab[m.end():(marks[i + 1].start() if i + 1 < len(marks) else len(ab))])
                 for i, m in enumerate(marks)]
    else:
        parts = [("", ab)]
    for label, body in parts:
        if label.upper() in _CONTEXT:
            continue
        out += [s for s in _sentences(body) if _OWN.search(s)]
    return out


def setting_hit(rec: dict, terms, has) -> str | None:
    """The first setting term found in the record's own design statements (has = screen._has), else None."""
    for chunk in own_design_text(rec):
        hit = has(chunk.lower(), terms)
        if hit:
            return hit
    return None
