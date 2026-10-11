"""ALL CANDIDATE OUTCOME ROWS before a refusal stands (external audit D3: r26-01 ESCAPe, r2 F5 CoDEX).

A refusal cites ONE witness. ESCAPe (corticosteroids-cap-mortality, PMID 35723686) was refused on its 60-day mortality
OR because the outcome declares '30-day or in-hospital' -- while the same held Table 2 prints 'Hospital Mortality 34/291
v 28/281, OR 1.2 (0.7, 2.03)', a row inside the declared window that nothing ever assessed. A refusal is complete only
when EVERY candidate row of the outcome in the held article has been assessed against the same rules.

Scope, stated:
  - only a held FULLTEXT is read (harness/source_coverage: a stub or portal page has no tables to assess);
  - candidate = a row of a NON-baseline table (extract._TABLE_ROLE_NEVER_AN_EFFECT_SOURCE on its caption) whose label names the outcome (the absence
    classifier's own outcome terms) and that prints arm counts or an effect;
  - each candidate's measurement window is read from its OWN label ('study day 60', 'by 1 year', 'Hospital
    Mortality', '28-day'); assessment: WINDOW_MATCH (inside the declared windows), IN_HOSPITAL_MATCH (the outcome
    declares in-hospital), WINDOW_MISMATCH, or WINDOW_UNSTATED (needs adjudication);
  - this module ADMITS NOTHING. An admissible candidate a refusal did not assess is reported as
    CANDIDATE_ROW_UNASSESSED for a person to adjudicate (population, missing data, measure) -- a pool change is a
    signed V-packet item, never automatic.
"""
from __future__ import annotations

import html
import re

from . import absence, extract, lexicon
from . import source_coverage as sc

_WS = re.compile(r"\s+")
_COUNTS = re.compile(r"\b\d+\s*/\s*\d+\b|\b\d+\s*\(\s*\d+(?:\.\d+)?\s*%?\s*\)")
_EFFECT = re.compile(r"\b\d+(?:\.\d+)?\s*\(\s*[−-]?\s*\d+(?:\.\d+)?\s*[,–-]\s*[−-]?\s*\d+(?:\.\d+)?\s*\)")
_DAY = re.compile(r"(?:\bday\s+(\d{1,3})\b|\b(\d{1,3})\s*[- ]?\s*days?\b)", re.I)
_YEAR = re.compile(r"\b(?:by\s+|at\s+)?(\d{1,2}|one|two|three)\s*[- ]?\s*years?\b", re.I)
_MONTH = re.compile(r"\b(\d{1,2})\s*[- ]?\s*months?\b", re.I)
_HOSPITAL = re.compile(r"\b(?:in[- ]?)?hospital\b", re.I)
_WORDNUM = {"one": 1, "two": 2, "three": 3}


def _text(cell_xml: str) -> str:
    return _WS.sub(" ", html.unescape(re.sub(r"<[^>]+>", " ", cell_xml))).strip()


def table_rows(jats: str):
    """[{table, caption, section, label, cells}] of every data row of every table-wrap; a one-cell row is a section
    heading carried onto the rows below it."""
    out = []
    for m in re.finditer(r"<table-wrap\b[^>]*>.*?</table-wrap>", jats or "", re.S):
        tw = m.group(0)
        tid = (re.search(r'\bid="([^"]+)"', tw[:300]) or re.match("", "")).group(1) if re.search(r'\bid="', tw[:300]) else None
        cap = _text((re.search(r"<caption>(.*?)</caption>", tw, re.S) or re.search(r"<label>(.*?)</label>", tw, re.S)
                     or re.match("(.*)", "")).group(1))
        section = None
        for tr in re.findall(r"<tr\b.*?</tr>", tw, re.S):
            cells = [_text(c) for c in re.findall(r"<t[dh]\b.*?</t[dh]>", tr, re.S)]
            if len([c for c in cells if c]) == 1:
                section = next(c for c in cells if c)
                continue
            if cells:
                out.append({"table": tid, "caption": cap, "section": section, "label": cells[0], "cells": cells})
    return out


def row_window(label: str):
    """('DAYS', n) | ('IN_HOSPITAL', None) | ('UNSTATED', None) from the row's OWN label (never another row's)."""
    lab = label or ""
    days = [int(a or b) for a, b in _DAY.findall(lab)]
    days += [365 * (_WORDNUM.get(y.lower()) or int(y)) for y in _YEAR.findall(lab)
             if y.lower() in _WORDNUM or y.isdigit()]
    days += [30 * int(mo) for mo in _MONTH.findall(lab)]
    if days:
        return ("DAYS", max(days))
    if _HOSPITAL.search(lab):
        return ("IN_HOSPITAL", None)
    return ("UNSTATED", None)


def allowed_windows(declared_timepoint: str, keywords) -> set:
    """The day windows an outcome declares -- the SAME reading extract.outcome_window_mismatch uses."""
    allowed = set()
    for s in [declared_timepoint or ""] + [str(k) for k in keywords or []]:
        s = s.lower()
        allowed |= {int(n) for n in re.findall(r"(\d{1,3})\s*[- ]?\s*day", s)}
        allowed |= {int(n) for n in re.findall(r"\bday\s+(\d{1,3})\b", s)}
        m = re.fullmatch(r"(\d{1,3})\s*-\s*(\d{1,3})", s.strip())
        if m:
            allowed |= set(range(int(m.group(1)), int(m.group(2)) + 1))
    return allowed


def _names_outcome(label: str, terms) -> bool:
    lf = lexicon.fold(label).replace("-", " ")
    return any(t and lexicon.fold(t).replace("-", " ") in lf for t in terms)


def candidates(jats: str, keywords, outcome_name: str, declared_timepoint: str) -> list:
    terms = list(absence._terms(keywords, outcome_name))
    if re.search(r"mortal|death", outcome_name or "", re.I):
        terms += ["mortality", "death", "died", "deaths"]
    allowed = allowed_windows(declared_timepoint, keywords)
    in_hospital_declared = bool(_HOSPITAL.search(declared_timepoint or ""))
    out = []
    for r in table_rows(jats):
        if any(ph in (r["caption"] or "").lower() for ph in extract._TABLE_ROLE_NEVER_AN_EFFECT_SOURCE):
            continue        # a baseline / design table never holds an outcome result (extract's own role vocabulary)
        if not _names_outcome(r["label"], terms):
            continue
        data = " | ".join(r["cells"][1:])
        if not (_COUNTS.search(data) or _EFFECT.search(data)):
            continue
        kind, n = row_window(r["label"])
        if kind == "DAYS":
            verdict = "WINDOW_MATCH" if n in allowed else "WINDOW_MISMATCH"
        elif kind == "IN_HOSPITAL":
            verdict = "IN_HOSPITAL_MATCH" if in_hospital_declared else "WINDOW_MISMATCH"
        else:
            verdict = "WINDOW_UNSTATED"
        out.append({"table": r["table"], "section": r["section"], "label": r["label"], "cells": r["cells"][1:],
                    "window": {"kind": kind, "days": n}, "assessment": verdict})
    return out


ADMISSIBLE = ("WINDOW_MATCH", "IN_HOSPITAL_MATCH")


def audit_refusal(slug: str, pid, row: dict, keywords, outcome_name: str, declared_timepoint: str, root=None) -> dict:
    """{state, candidates}: CANDIDATE_ROW_UNASSESSED when the held FULLTEXT prints a candidate inside the declared
    window that the refusal's own witness is not; ALL_CANDIDATES_OUTSIDE_WINDOW / NO_CANDIDATE_ROWS /
    NOT_A_FULLTEXT otherwise. The refusal itself is left exactly as it is."""
    import os
    cov = sc.coverage_for(slug, pid, root=root)
    if cov["fulltext"] != "FULLTEXT":
        return {"state": "NOT_A_FULLTEXT", "coverage": cov["fulltext"], "candidates": []}
    root = root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pid = str(pid).replace("PMID ", "")
    p = next(os.path.join(root, "cache", slug, f"ft_{pid}.{e}") for e in ("txt", "xml")
             if os.path.isfile(os.path.join(root, "cache", slug, f"ft_{pid}.{e}")))
    cands = candidates(open(p, encoding="utf-8", errors="replace").read(), keywords, outcome_name, declared_timepoint)
    witness = _WS.sub(" ", row.get("source_span") or row.get("verbatim_span") or "")
    for c in cands:
        c["is_refusal_witness"] = bool(witness) and any(x and x in witness for x in c["cells"][-2:] if len(x) > 4)
    unassessed = [c for c in cands if c["assessment"] in ADMISSIBLE and not c["is_refusal_witness"]]
    if unassessed:
        state = "CANDIDATE_ROW_UNASSESSED"
    elif not cands:
        state = "NO_CANDIDATE_ROWS"
    elif all(c["assessment"] == "WINDOW_MISMATCH" for c in cands):
        state = "ALL_CANDIDATES_OUTSIDE_WINDOW"
    else:
        state = "CANDIDATES_NEED_ADJUDICATION"
    return {"state": state, "candidates": cands, "unassessed": unassessed}
