"""Nested reports of ONE trial inside a comparator's analysis (V1.0.1, ticagrelor-ACS review).

Tan 2017 (PLOS ONE) pools, for its composite endpoint (Figure 4), Wallentin 2009 -- PLATO, 18,624 patients -- and
Cannon 2010 -- PLATO's planned-invasive cohort, 13,408 of those same 18,624 -- as two entries. They are two REPORTS of
one TRIAL, and the second is a SUBGROUP of the first: its patients are counted twice in the pooled OR 0.83.

Overlap is therefore stated at three levels, never by dates:
  report overlap   comparator rows that are reports of a trial we pool
  trial overlap    distinct registrations those rows share with our pooled trials
  population       SUBGROUP_OF -- a nested row's own held report prints "<its n> (x%) of <the parent row's n>";
                   the duplicated participants are that n. Without that printed statement two rows of one
                   registration are SAME_REGISTRATION_POPULATION_NOT_ESTABLISHED, never assumed nested or distinct.
A row's registration comes only from held text: our record's registry id, or the DataBank accession on the comparator-
named PubMed record (cache/<slug>/comparator_named_pubmed.xml). A comparator whose analysis carries a SUBGROUP_OF pair
is DUPLICATED_POPULATION: its pooled estimate is not a benchmark until de-duplicated.
"""
from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path
from typing import Optional

_SUBSET = re.compile(r"(\d{1,3}(?:[\s,  ]\d{3})*|\d+)\s*\(\s*\d+(?:\.\d+)?\s*%\s*\)\s*of\s+(\d{1,3}(?:[\s,  ]\d{3})*|\d+)")


def _int(s: str) -> int:
    return int(re.sub(r"\D", "", s))


def _held_pubmed(root, slug) -> dict:
    """{pmid: {"ncts": [...], "text": title + abstract, "ref": document}} from records.json and the comparator-named XML."""
    out = {}
    rp = Path(root) / "cache" / slug / "records.json"
    if rp.exists():
        for r in json.loads(rp.read_text(encoding="utf-8")).get("records") or []:
            ncts = [str(r["nct"])] if str(r.get("nct") or "").upper().startswith("NCT") else []
            out[str(r.get("id"))] = {"ncts": ncts, "text": f"{r.get('title') or ''} {r.get('abstract') or ''}",
                                     "ref": f"cache/{slug}/records.json"}
    xp = Path(root) / "cache" / slug / "comparator_named_pubmed.xml"
    if xp.exists():
        for m in re.finditer(r"<PubmedArticle>.*?</PubmedArticle>", xp.read_text(encoding="utf-8"), re.S):
            a = m.group(0)
            pm = re.search(r"<PMID[^>]*>(\d+)</PMID>", a)
            if not pm or pm.group(1) in out:
                continue
            title = re.sub(r"<[^>]+>", " ", (re.search(r"<ArticleTitle>(.*?)</ArticleTitle>", a, re.S) or [None, ""])[1])
            ab = " ".join(re.sub(r"<[^>]+>", " ", x) for x in re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", a, re.S))
            out[pm.group(1)] = {"ncts": [n for n in re.findall(r"<AccessionNumber>(NCT\d{8})</AccessionNumber>", a)],
                                "text": _html.unescape(re.sub(r"\s+", " ", f"{title} {ab}")),
                                "ref": f"cache/{slug}/comparator_named_pubmed.xml"}
    return out


def assess(root, slug: str, analysis: Optional[dict], panel: Optional[dict], pooled_ncts) -> Optional[dict]:
    """analysis: comparator_analysis.assess(...) output (membership rows with panel_row and counts); panel: the
    comparator panel entry (trial_set rows with aliases); pooled_ncts: registrations of our pooled trial families."""
    mem = (analysis or {}).get("membership") or {}
    rows = [m for m in mem.get("members") or [] if m.get("panel_row") and m.get("counts")]
    if len(rows) < 2 or not panel:
        return None
    alias = {t["family_id"]: [a["id"] for a in t.get("aliases") or [] if str(a.get("id")).isdigit()]
             for t in panel.get("trial_set") or []}
    held = _held_pubmed(root, slug)
    by_reg: dict = {}
    for m in rows:
        pmids = alias.get(m["panel_row"]) or []
        regs = sorted({n for p in pmids for n in (held.get(p) or {}).get("ncts") or []})
        m = dict(m, pmids=pmids, registrations=regs, n=m["counts"][1] + m["counts"][3])
        if len(regs) == 1:
            by_reg.setdefault(regs[0], []).append(m)
    nested = []
    for reg, ms in sorted(by_reg.items()):
        if len(ms) < 2:
            continue
        ms = sorted(ms, key=lambda x: -x["n"])
        parent = ms[0]
        for child in ms[1:]:
            proof = None
            for p in child["pmids"]:
                h = held.get(p) or {}
                for sm in _SUBSET.finditer(h.get("text") or ""):
                    if _int(sm.group(1)) == child["n"] and _int(sm.group(2)) == parent["n"]:
                        proof = {"document_ref": h["ref"], "pmid": p, "quote": sm.group(0)}
                        break
                if proof:
                    break
            nested.append({"registration": reg, "parent": {"label": parent["label"], "n": parent["n"]},
                           "row": {"label": child["label"], "n": child["n"]},
                           "relation": "SUBGROUP_OF" if proof else "SAME_REGISTRATION_POPULATION_NOT_ESTABLISHED",
                           "duplicated_participants": child["n"] if proof else None, "proof": proof})
    pooled = {str(n).upper() for n in pooled_ncts or []}
    ours = [m for ms in by_reg.values() for m in ms if any(r in pooled for r in m["registrations"])]
    return {"report_overlap": len(ours), "trial_overlap": len({r for m in ours for r in m["registrations"]}),
            "shared_registrations": sorted({r for m in ours for r in m["registrations"]}),
            "nested": nested,
            "state": "DUPLICATED_POPULATION" if any(x["relation"] == "SUBGROUP_OF" for x in nested) else
                     ("SAME_REGISTRATION_ROWS" if nested else "NO_NESTED_REPORTS")}


def render(a: Optional[dict]) -> str:
    if not a or a["state"] == "NO_NESTED_REPORTS":
        return ""
    e = lambda s: _html.escape(str(s), quote=True)  # noqa: E731
    parts = [f"<p><strong>Nested reports of one trial:</strong> <code>{e(a['state'])}</code>. Report overlap with our pool: "
             f"{e(a['report_overlap'])} rows; trial overlap: {e(a['trial_overlap'])} "
             f"({e(', '.join(a['shared_registrations']) or 'none')}).</p>"]
    for x in a["nested"]:
        pr = x.get("proof") or {}
        parts.append(f"<p><code>{e(x['relation'])}</code> {e(x['registration'])}: {e(x['row']['label'])} "
                     f"(n = {e(x['row']['n'])}) within {e(x['parent']['label'])} (n = {e(x['parent']['n'])})"
                     + (f"; its own report: &ldquo;{e(pr['quote'])}&rdquo; ({e(pr['document_ref'])}, PMID {e(pr['pmid'])}). "
                        f"{e(x['duplicated_participants'])} participants are counted twice in the comparator's pooled "
                        "estimate, which is therefore not a benchmark until de-duplicated." if pr else
                        "; one registration, two rows; whether the populations overlap is not established.") + "</p>")
    return "<div class='comparator-nesting'>" + "".join(parts) + "</div>"
