"""REPORT LINKAGE, derived: which held reports are reports of the SAME trial, from their own text -- deterministic
regex rules, never a hand list (statins in older adults, 2026-09-28: Orkaby 2018, an RMST re-analysis of ALLHAT-LLT,
entered as a separate trial until a hand-written docs/study_families.json row linked it).

Two rules, each typed with its spans; a link needs rule A, or rule B for the same intervention; a conflict abstains:
  A  PARENT LINKAGE   the report calls itself an analysis of a named trial -- '(secondary | post hoc | ancillary |
                      exploratory | pre-specified | subgroup | restricted mean survival time ...) analysis of ...
                      (ACRONYM)' -- and exactly one OTHER held report of the topic carries that acronym in its
                      title/abstract AND a registration
  B  SHARED ARMS      both reports state the same randomised arm sizes (>= 2 identical arm numbers >= 50, e.g.
                      '(n=1,467)' / '1400 participants'), for the same intervention term
The parent is the report that carries the registration. Output rows have the study_families shape (pmid, parent_pmid,
trial_family_id, publication_role, kind) plus `derived` with the rule and its spans. (harness/report_family.py is a
different object: reports of one trial at different FOLLOW-UP TIMES.)

  derive(records, config) -> [companion rows]
"""
from __future__ import annotations

import re
from typing import Any

_ANALYSIS_OF = re.compile(
    r"\b(?:secondary|post[\s-]?hoc|ancillary|exploratory|pre-?specified|sub-?group|restricted mean survival time|rmst)"
    r"(?:\s+\w+){0,3}?\s+analys[ie]s\s+of\s+(?:the\s+|data\s+from\s+the\s+)?(?P<name>[^.;]{3,220}?)\s*"
    r"\((?P<acr>[A-Z][A-Za-z0-9]*(?:[-‐][A-Za-z0-9]+)*)\)", re.I)
_ARM_N = re.compile(r"\(\s*n\s*=\s*(?P<n>\d{1,3}(?:,\d{3})+|\d{2,6})\s*\)"
                    r"|\b(?P<n2>\d{1,3}(?:,\d{3})+|\d{3,6})\s+(?:participants|patients|subjects)\b", re.I)
_NCT = re.compile(r"NCT\d{8}")


def _num(s: str) -> int:
    return int(s.replace(",", ""))


def arm_sizes(text: str) -> set[int]:
    """Stated arm sizes (>= 50) in a text: '(n=1,467)', '(n = 1400)', '1467 participants'."""
    out = set()
    for m in _ARM_N.finditer(text or ""):
        v = m.group("n") or m.group("n2")
        if v and _num(v) >= 50:
            out.add(_num(v))
    return out


def _nct_of(rec: dict[str, Any]) -> str:
    m = _NCT.search(str(rec.get("nct") or "")) or _NCT.search(str(rec.get("abstract") or ""))
    return m.group(0) if m else ""


def _interventions(rec: dict[str, Any], config: dict[str, Any]) -> set[str]:
    """Every protocol intervention term the report names (a set: 'statin' and 'pravastatin' are compared as sets)."""
    text = f"{rec.get('title') or ''} {rec.get('abstract') or ''}".lower()
    return {str(t).lower() for t in (config.get("include") or {}).get("intervention_any") or config.get("intervention_terms") or []
            if re.search(r"(?<!\w)" + re.escape(str(t).lower()) + r"(?!\w)", text)}


def derive(records: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    pubs = [r for r in records if str(r.get("id_type") or "pmid") != "nct" and re.fullmatch(r"\d{6,9}", str(r.get("id")))]
    out = []
    for child in pubs:
        ab = str(child.get("abstract") or "")
        if _nct_of(child):
            continue                                    # a report with its own registration anchors its own family
        a = _ANALYSIS_OF.search(ab)
        cand_a = []
        # a trial ACRONYM, not an abbreviation: >= 3 characters with >= 2 capitals, named in the parent's TITLE (a
        # '(LD)' for 'loading dose' linked a stable-CAD platelet study to a STEMI trial whose abstract also says 'LD')
        if a and len(a.group("acr")) >= 3 and sum(ch.isupper() for ch in a.group("acr")) >= 2:
            rx = re.compile(r"(?<![A-Za-z0-9])" + re.escape(a.group("acr")) + r"(?![A-Za-z0-9])")
            cand_a = [p for p in pubs if p is not child and _nct_of(p) and rx.search(str(p.get("title") or ""))]
        sizes = arm_sizes(ab)
        iv = _interventions(child, config)
        cand_b = [p for p in pubs if p is not child and _nct_of(p) and iv & _interventions(p, config)
                  and len(sizes & arm_sizes(str(p.get("abstract") or ""))) >= 2]
        if len(cand_a) > 1 or len(cand_b) > 1:
            continue                                    # ambiguous: abstain
        pa, pb = (cand_a or [None])[0], (cand_b or [None])[0]
        if pa is not None and pb is not None and pa is not pb:
            continue                                    # the rules disagree: abstain
        parent = pa or pb
        if parent is None:
            continue
        rules = []
        if pa is not None:
            rules.append({"rule": "A_PARENT_LINKAGE", "span": a.group(0), "acronym": a.group("acr")})
        if pb is not None:
            rules.append({"rule": "B_SHARED_ARM_SIZES", "intervention": sorted(iv & _interventions(parent, config)),
                          "shared": sorted(sizes & arm_sizes(str(parent.get("abstract") or "")))})
        out.append({"pmid": str(child["id"]), "parent_pmid": str(parent["id"]), "trial_family_id": _nct_of(parent),
                    "parent": f"{parent.get('title')} ({parent['id']})", "publication_role": "secondary_analysis",
                    "kind": ("a report of the SAME trial, derived from its own text ("
                             + " + ".join(r["rule"] for r in rules) + "): never a new trial"),
                    "derived": {"by": "harness.report_linkage.derive", "rules": rules}})
    return out
