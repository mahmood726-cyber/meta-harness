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
# not out-of-hospital / out of hospital / pre-hospital / post-hospital (codex e1p2-r1 #3)
_HOSPITAL = re.compile(r"(?<!out.of.)(?<!pre.)(?<!post.)\b(?:in[- ]?)?hospital\b", re.I)
# after / following / post- discharge is OUTSIDE the stay (codex e1p2-r2 #4); 'before hospital discharge' is inside it
_POST_DISCHARGE = re.compile(r"\b(?:after|following|post)[- ]+(?:hospital[- ]+)?discharge|\bpost[- ]?discharge\b", re.I)
_INT_CELL = re.compile(r"^\d+$")
_PERCENT = re.compile(r"%|\bpercent", re.I)
_COUNT_MARK = re.compile(r"\bn\b|\bno\.|\bnumber\b|\bevents?\b|\bdeaths\b|\bpatients\s+who\s+died\b", re.I)
# an age is not a follow-up window: 'aged 60 years', '65 years of age', '60 years or older' (codex e1p2-r3 #4)
_AGE_BEFORE = re.compile(r"(?:\baged?|\bage\s+(?:of|over|under|above|below)?|[≥>≤<]=?)\s*$", re.I)
_AGE_AFTER = re.compile(r"^\s*(?:old\b|of\s+age\b|or\s+(?:older|younger|over|more)\b|and\s+(?:older|over)\b|\+)",
                        re.I)
_RANGE_DAYS = re.compile(r"\b(\d{1,3})\s*(?:-|–|to)\s*(\d{1,3})\s*[- ]?\s*days?\b", re.I)
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
        section, header = None, []
        for tr in re.findall(r"<tr\b.*?</tr>", tw, re.S):
            raw = re.findall(r"<t[dh]\b.*?</t[dh]>", tr, re.S)
            cells = [_text(c) for c in raw]
            if raw and all(c.startswith("<th") for c in raw):
                # EVERY column-header row of the table is kept, whole: a unit may sit in a grouped header ('Patients
                # (%)' over 'Treatment | Control') or in a header row with no stub cell -- column alignment is not
                # attempted (codex e1p2-r3 #3, agy e1p2-r3-agy P0)
                header = header + [c for c in cells if c]
                continue
            if len([c for c in cells if c]) == 1:
                section = next(c for c in cells if c)
                continue
            if cells:
                out.append({"table": tid, "caption": cap, "section": section, "label": cells[0], "cells": cells,
                            "header": header})
    return out


def _months_to_days(mo: int) -> int:
    return 365 * (mo // 12) if mo % 12 == 0 else 30 * mo


def _days(text: str) -> list:
    """Every window a phrase states, in days: 'day 60', '28-day', '1 year' (365), '12 months' (365), '6 months' (180)."""
    text = text or ""

    def not_age(m):
        return not (_AGE_BEFORE.search(text[:m.start()]) or _AGE_AFTER.search(text[m.end():]))

    days = [int(m.group(1) or m.group(2)) for m in _DAY.finditer(text) if not_age(m)]
    days += [365 * (_WORDNUM.get(m.group(1).lower()) or int(m.group(1))) for m in _YEAR.finditer(text)
             if (m.group(1).lower() in _WORDNUM or m.group(1).isdigit()) and not_age(m)]
    days += [_months_to_days(int(m.group(1))) for m in _MONTH.finditer(text) if not_age(m)]
    return days


def row_window(label: str):
    """('DAYS', n) | ('IN_HOSPITAL', None) | ('UNSTATED', None) from the row's OWN label (never another row's)."""
    lab = label or ""
    days = _days(lab)
    if days:
        return ("DAYS", max(days))
    if _HOSPITAL.search(lab) and not _POST_DISCHARGE.search(lab):
        return ("IN_HOSPITAL", None)
    return ("UNSTATED", None)


def allowed_windows(declared_timepoint: str, keywords) -> set:
    """The windows an outcome declares, in days, read by the SAME parser as a row's own label (row_window): days,
    years and months (codex+agy e1p2-r1: a declared '1 year' was read as no window at all, so a '1-year' row
    mismatched)."""
    allowed = set()
    for s in [declared_timepoint or ""] + [str(k) for k in keywords or []]:
        s = s.lower()
        allowed |= set(_days(s))
        allowed |= {int(n) for n in re.findall(r"(\d{1,3})\s*[- ]?\s*day", s)}
        for a, b in _RANGE_DAYS.findall(s):      # '28-30 days' is every day of the range (codex e1p2-r2 #3)
            if int(a) <= int(b):
                allowed |= set(range(int(a), int(b) + 1))
        m = re.fullmatch(r"(\d{1,3})\s*-\s*(\d{1,3})", s.strip())
        if m:
            allowed |= set(range(int(m.group(1)), int(m.group(2)) + 1))
    return allowed


_WINDOW_WORDS = re.compile(r"\b(?:at|by|on|within|through|up|to|after|study|follow[- ]?up|no|total|n|and|or|of|"
                           r"days?|months?|years?|weeks?|one|two|three|in[- ]?hospital|hospital|discharge)\b", re.I)


def _window_only(label: str) -> bool:
    """A label that states a window and nothing else ('28 days', 'At 1 year', 'In hospital, n (%)')."""
    if row_window(label)[0] == "UNSTATED":
        return False
    return not re.sub(r"[\W\d_]+", "", _WINDOW_WORDS.sub(" ", label or ""))


def _names_outcome(label: str, terms) -> bool:
    lf = lexicon.fold(label).replace("-", " ")
    return any(t and lexicon.fold(t).replace("-", " ") in lf for t in terms)


def candidates(jats: str, keywords, outcome_name: str, declared_timepoint: str) -> list:
    terms = list(absence._terms(keywords, outcome_name))
    if re.search(r"mortal|death", outcome_name or "", re.I):
        terms += ["mortality", "death", "died", "deaths"]
    allowed = allowed_windows(declared_timepoint, keywords)
    # the declared window is read by the SAME rule as a row's: 'after hospital discharge' is not in-hospital (r3 #1)
    in_hospital_declared = bool(_HOSPITAL.search(declared_timepoint or "")
                                and not _POST_DISCHARGE.search(declared_timepoint or ""))
    out = []
    for r in table_rows(jats):
        if any(ph in (r["caption"] or "").lower() for ph in extract._TABLE_ROLE_NEVER_AN_EFFECT_SOURCE):
            continue        # a baseline / design table never holds an outcome result (extract's own role vocabulary)
        # the outcome may be named by the section heading above a row whose OWN label is only a window
        # ('Mortality' / '28 days', agy e1p2-r1 #3) -- never by a heading over rows that name other outcomes
        # ('In-hospital morbidity and mortality' / 'Vasopressor dependent shock ...')
        if not (_names_outcome(r["label"], terms)
                or (_window_only(r["label"]) and _names_outcome(r["section"] or "", terms))):
            continue
        data = " | ".join(r["cells"][1:])
        # plain integers are arm COUNTS only when the label or a header says so ('30-day mortality, n'; 'No. of
        # events') and nothing in the table's headers, caption or the label says percentage (codex e1p2-r2 #2,
        # e1p2-r3 #3; agy e1p2-r3-agy P0) -- an unmarked '10 | 12' is never read as counts
        units = " | ".join([r["label"], r["caption"] or ""] + list(r.get("header") or []))
        ints = [c for c in r["cells"][1:] if _INT_CELL.match(c)]
        if _PERCENT.search(units) or not _COUNT_MARK.search(units):
            ints = []
        if not (_COUNTS.search(data) or _EFFECT.search(data) or len(ints) >= 2):
            continue        # plain integer arm counts ('30-day mortality, n | 10 | 12') are counts too
        kind, n = row_window(r["label"])
        if kind == "DAYS":
            verdict = "WINDOW_MATCH" if n in allowed else "WINDOW_MISMATCH"
        elif kind == "IN_HOSPITAL":
            verdict = "IN_HOSPITAL_MATCH" if in_hospital_declared else "WINDOW_MISMATCH"
        else:
            verdict = "WINDOW_UNSTATED"
        out.append({"table": r["table"], "caption": r["caption"], "section": r["section"], "label": r["label"],
                    "cells": r["cells"][1:],
                    "window": {"kind": kind, "days": n}, "assessment": verdict})
    return out


ADMISSIBLE = ("WINDOW_MATCH", "IN_HOSPITAL_MATCH")


def _is_witness(cells, witness: str) -> bool:
    """A candidate IS the refusal's witness only when at least two of its numeric cells (all, if it has one) occur in
    the witness span as whole tokens. One shared cell is not enough: a control arm's 28/281 is printed on every
    mortality row of a table (codex e1p2-r1 #4). Matches are counted as a multiset: two identical cells need two
    occurrences in the witness (codex e1p2-r2 #1)."""
    import collections
    nums = [x for x in cells if x and re.search(r"\d", x)]
    if not witness or not nums:
        return False
    # a token followed by '%' is a percentage, never a count cell's witness (codex e1p2-r3 #2)
    hit = sum(min(n, len(re.findall(r"(?<![\d.])" + re.escape(x) + r"(?![\d.]|\s*%)", witness)))
              for x, n in collections.Counter(nums).items())
    return hit >= min(2, len(nums))


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
        c["is_refusal_witness"] = _is_witness(c["cells"], witness)
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
