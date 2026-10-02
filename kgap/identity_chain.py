"""IDENTITY CHAIN: a comparator's bare trial label -> NCT -> PMID, from the versioned AACT snapshot, deterministic.

The class IDENTITY_UNRESOLVED (65 comparator trials over 31 topics) is labels with no reference link: trial acronyms
('COPPS study', 'SOLOIST-WHF', 'Semler (SMART trial)') and Cochrane-style 'Author Year' ('Legro 2007'). The NOAC lane
resolved ROCKET AF this way (AACT study_references NCT00403767|21830957); this module makes that a class fix.

    ACRONYM      a label acronym (kgap.k_gap._label_tokens) equals a study's AACT `acronym` (case/dash/space folded)
    AUTHOR_YEAR  a study_references citation BEGINS with the label's surname and carries the label's year
Every candidate must be INTERVENTIONAL and name one of the topic's agents (its interventions, brief/official title, or
the citation itself). Exactly ONE surviving NCT -> RESOLVED, with its RESULT-typed PMID (else DERIVED; else none) and
the evidence rows; two or more -> AMBIGUOUS (never a pick); none -> NOT_FOUND.

Three streaming passes over studies / study_references / interventions, restricted to what the labels need.

    resolve(items, snapshot_dir) -> {(slug, label): {...}}    items: [(slug, label, [agent terms])]
"""
from __future__ import annotations

import csv
import os
import re

from . import k_gap

csv.field_size_limit(10 ** 8)
_YEAR = re.compile(r"\b((?:19|20)\d\d)\b")


def _fold(s):
    return re.sub(r"[\s\-]+", "", k_gap.fold_dashes(s or "")).upper()


def _rows(d, name):
    with open(os.path.join(d, name), encoding="utf-8", errors="replace", newline="") as fh:
        yield from csv.DictReader(fh, delimiter="|", quoting=csv.QUOTE_NONE)


def label_keys(label):
    """(acronyms folded, (surname, year) or None) for one comparator label."""
    t = k_gap._label_tokens(label)
    acr = {_fold(a) for a in t["acronyms"]}
    # 'COPPS study', 'SMART trial' -> the word before study/trial is the acronym even when _ACRO's length rule misses it
    for m in re.finditer(r"\b([A-Z][A-Za-z0-9\-]{2,})\s+(?:study|trial)\b", k_gap.fold_dashes(label or "")):
        acr.add(_fold(m.group(1)))
    acr = {a for a in acr if a and a not in k_gap._NOT_ACRO}
    ay = (t["author"], t["year"]) if t["author"] and t["year"] else None
    return acr, ay


def resolve(items, snapshot_dir):
    want_acr, want_ay, keys = {}, {}, {}
    for slug, label, agents in items:
        acr, ay = label_keys(label)
        keys[(slug, label)] = (acr, ay, [a.lower() for a in agents if a])
        for a in acr:
            want_acr.setdefault(a, set()).add((slug, label))
        if ay:
            want_ay.setdefault((ay[0].lower(), ay[1]), set()).add((slug, label))
    studies, by_acr = {}, {}
    for r in _rows(snapshot_dir, "studies.txt"):
        a = _fold(r.get("acronym"))
        if a and a in want_acr:
            by_acr.setdefault(a, []).append(r["nct_id"])
            studies[r["nct_id"]] = r
    refs, by_ay = {}, {}
    acr_ncts = {n for v in by_acr.values() for n in v}
    for r in _rows(snapshot_dir, "study_references.txt"):
        n, cit = r.get("nct_id"), r.get("citation") or ""
        if n in acr_ncts:
            refs.setdefault(n, []).append(r)
        m = re.match(r"\s*([A-Z][A-Za-z'\-]+)\s", cit)
        # only the trial's OWN publications identify it: a BACKGROUND reference is a study citing someone else's paper
        # (Baillargeon 2004 matched a 2012 letrozole trial that cites it)
        if (r.get("reference_type") or "").upper() not in ("RESULT", "DERIVED"):
            m = None
        if m and want_ay:
            ys = set(_YEAR.findall(cit))
            for y in ys:
                k = (m.group(1).lower(), y)
                if k in want_ay:
                    by_ay.setdefault(k, []).append(r)
                    refs.setdefault(n, []).append(r)
    cand_ncts = acr_ncts | {r["nct_id"] for v in by_ay.values() for r in v}
    interv = {}
    for r in _rows(snapshot_dir, "interventions.txt"):
        if r.get("nct_id") in cand_ncts:
            interv.setdefault(r["nct_id"], []).append((r.get("name") or "") + " " + (r.get("description") or ""))
    missing = cand_ncts - set(studies)
    if missing:
        for r in _rows(snapshot_dir, "studies.txt"):
            if r["nct_id"] in missing:
                studies[r["nct_id"]] = r

    def eligible(n, agents, extra=""):
        s = studies.get(n) or {}
        if (s.get("study_type") or "").upper() != "INTERVENTIONAL":
            return False
        text = " ".join(interv.get(n, []) + [s.get("brief_title") or "", s.get("official_title") or "", extra]).lower()
        return any(a in text for a in agents)

    def report_pmid(n):
        rs = refs.get(n, [])
        for t in ("RESULT", "DERIVED"):
            p = sorted({r["pmid"] for r in rs if (r.get("reference_type") or "").upper() == t and r.get("pmid")})
            if p:
                return p[0], t, len(p)
        return None, None, 0

    out = {}
    for (slug, label), (acr, ay, agents) in keys.items():
        basis, cands = None, set()
        hits = {n for a in acr for n in by_acr.get(a, []) if eligible(n, agents)}
        if hits:
            basis, cands = "ACRONYM", hits
        elif ay:
            rs = by_ay.get((ay[0].lower(), ay[1]), [])
            cands = {r["nct_id"] for r in rs if eligible(r["nct_id"], agents, r.get("citation") or "")}
            basis = "AUTHOR_YEAR" if cands else None
        if len(cands) == 1:
            n = next(iter(cands))
            pmid, ptype, npm = report_pmid(n)
            s = studies.get(n) or {}
            out[(slug, label)] = {"state": "RESOLVED", "basis": basis, "nct": n, "pmid": pmid, "pmid_type": ptype,
                                  "n_pmids_of_type": npm, "acronym": s.get("acronym"), "brief_title": s.get("brief_title"),
                                  "evidence": [r.get("citation", "")[:240] for r in refs.get(n, [])
                                               if r.get("pmid") == pmid][:1]}
        elif len(cands) > 1:
            out[(slug, label)] = {"state": "AMBIGUOUS", "basis": basis, "candidates": sorted(cands)[:10]}
        else:
            out[(slug, label)] = {"state": "NOT_FOUND", "keys": {"acronyms": sorted(acr), "author_year": ay}}
    return out


OWN_PUBLICATION = ("RESULT", "DERIVED")


def pmid_to_ncts(pmids, snapshot_dir):
    """PMID -> {NCT: reference_type} from AACT study_references, ONLY where the paper is the study's OWN publication
    (RESULT / DERIVED). A BACKGROUND reference is a later registration citing an older paper: CORE (Imazio 2005,
    PMID 16186468) is cited by NCT04218786 (registered 2020) and was resolved to it."""
    want, out = {str(p) for p in pmids}, {}
    for r in _rows(snapshot_dir, "study_references.txt"):
        p = (r.get("pmid") or "").strip()
        t = (r.get("reference_type") or "").upper()
        if p in want and t in OWN_PUBLICATION:
            out.setdefault(p, {})[r["nct_id"]] = t
    return out


def result_pmids(ncts, snapshot_dir):
    """NCT -> sorted RESULT-typed PMIDs (else DERIVED) of that study: the trial's own result reports. The REPORT of a
    trial is the earliest of them (lowest PMID), not whichever paper happened to name the acronym in its title (SMART's
    self-naming title is a 2019 secondary analysis; its 2018 main report does not say 'SMART' in the title)."""
    want, by = set(ncts), {}
    for r in _rows(snapshot_dir, "study_references.txt"):
        if r.get("nct_id") in want and r.get("pmid"):
            by.setdefault(r["nct_id"], {}).setdefault((r.get("reference_type") or "").upper(), set()).add(r["pmid"].strip())
    out = {}
    for n, d in by.items():
        ps = d.get("RESULT") or d.get("DERIVED") or set()
        out[n] = sorted(ps, key=lambda x: int(x) if x.isdigit() else 10 ** 12)
    return out
