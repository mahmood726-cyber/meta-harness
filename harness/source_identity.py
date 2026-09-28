"""SOURCE IDENTITY: every identifier a cited source carries must resolve to ONE publication, or verification FAILS.

SGLT2-CKD: EMPA-KIDNEY was cited as PMC9761906 -- a paper about starfish. Its PMID 36331190 resolves (Europe PMC's
own record) to PMC7614055, "Empagliflozin in Patients with Chronic Kidney Disease". A PMID, a PMCID, a DOI, a title and
a registration that point at different publications are not a citation; they are several, and a span 'verified'
against the wrong one proves nothing. The same class, found live in this lane (2026-09-28): a DOI typed from memory for
EMPERIAL (10.1002/ejhf.2084) made Unpaywall hand over another paper's PMC page, held under EMPERIAL.

  check_citation(cited, record)  -> mismatches between a cited {pmid, pmcid, doi, title, registration} and the PMID's
                                    held Europe PMC record (the reference identity of the publication)
  check_held_document(path, rec) -> a held article whose OWN title (citation_title / article-title / the first pages of a
                                    PDF) is not the record's title
  ledger_check(root)             -> every held article in evidence/acquisition_cascade/held/HELD.json checked against its
                                    target's record; a document QUARANTINED in the ledger (identity_quarantine: reason)
                                    is reported as quarantined, never used and never a pass
The check is executable offline: the reference identity is the held record, never a lookup made at verification time.
"""
from __future__ import annotations

import glob
import html
import json
import os
import re
from typing import Any

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HELD = os.path.join("evidence", "acquisition_cascade", "held")


def norm(s: Any) -> str:
    # unescape FIRST: a record title may carry escaped markup ("&lt;i&gt;Lactobacillus&lt;/i&gt;")
    return re.sub(r"[^a-z0-9]+", " ", re.sub(r"<[^>]+>", " ", html.unescape(str(s or ""))).lower()).strip()


def record_identity(path: str) -> dict[str, Any]:
    """The reference identity of a publication: its held Europe PMC record."""
    r = ((json.load(open(path, encoding="utf-8")).get("resultList") or {}).get("result") or [{}])[0]
    return {"pmid": str(r.get("pmid") or ""), "pmcid": str(r.get("pmcid") or ""), "doi": str(r.get("doi") or "").lower(),
            "title": r.get("title") or "", "abstract": r.get("abstractText") or "", "record_path": path}


def check_citation(cited: dict[str, Any], rec: dict[str, Any]) -> list[str]:
    out = []
    if cited.get("pmid") and str(cited["pmid"]) != rec["pmid"]:
        out.append(f"PMID {cited['pmid']} is not the record's PMID {rec['pmid']}")
    if cited.get("pmcid") and rec["pmcid"] and str(cited["pmcid"]).upper() != rec["pmcid"].upper():
        out.append(f"PMCID {cited['pmcid']} resolves to a different publication: PMID {rec['pmid']} is {rec['pmcid']}")
    if cited.get("pmcid") and not rec["pmcid"]:
        out.append(f"PMCID {cited['pmcid']} is cited, but PMID {rec['pmid']} has no PMC copy in its record")
    if cited.get("doi") and rec["doi"] and str(cited["doi"]).lower() != rec["doi"]:
        out.append(f"DOI {cited['doi']} resolves to a different publication: PMID {rec['pmid']} is {rec['doi']}")
    if cited.get("title") and norm(cited["title"])[:80] != norm(rec["title"])[:80]:
        out.append(f"title '{str(cited['title'])[:80]}' is not the record's title '{rec['title'][:80]}'")
    if cited.get("registration") and str(cited["registration"]).upper() not in (rec["abstract"] or "").upper():
        reg_ok = cited.get("registration_evidence")      # e.g. the registry's own reference list names the PMID
        if not reg_ok:
            out.append(f"registration {cited['registration']} is not named by the record of PMID {rec['pmid']}")
    return out


def document_title(path: str) -> str | None:
    if path.endswith(".html"):
        s = open(path, encoding="utf-8", errors="replace").read()
        m = re.search(r'name="citation_title" content="([^"]+)"', s)
        return m.group(1) if m else None
    if path.endswith(".xml"):
        s = open(path, encoding="utf-8", errors="replace").read()
        m = re.search(r"<article-title[^>]*>(.*?)</article-title>", s, re.S)
        return m.group(1) if m else None
    if path.endswith(".pdf"):
        try:
            import pypdf
            pages = pypdf.PdfReader(path).pages
            return " ".join((pages[i].extract_text() or "") for i in range(min(2, len(pages))))
        except Exception:                                  # noqa: BLE001  (unreadable -> no identity, not a pass)
            return None
    return None


def check_held_document(path: str, rec: dict[str, Any]) -> str | None:
    got = document_title(path)
    if got is None:
        return f"{path}: no title could be read (identity not established)"
    want = norm(rec["title"]).rstrip(" .")
    have = norm(got)
    # formatting is not identity: subscripts and italics split words ('HbA<sub>1c</sub>' -> 'hba 1c'), a PDF breaks a
    # title across lines and hyphenates it. Compare with whitespace removed; for a PDF (title somewhere in the first
    # pages' text) require >= 90% of the record title's words to be present.
    ns = lambda s: s.replace(" ", "")
    if want and (ns(want)[:60] in ns(have) or ns(have)[:60] in ns(want)):
        return None
    if path.endswith(".pdf") and want:
        joined = ns(have)
        # the record's own DOI printed in the document is the strongest identity a PDF carries (CREDENCE's first
        # pages do not reproduce its title contiguously, but they print 'doi 10.1056/NEJMoa1811744')
        if rec.get("doi") and ns(norm(rec["doi"])) in joined:
            return None
        words = [w for w in want.split() if len(w) > 2]
        if words and sum(1 for w in words if w in joined) / len(words) >= 0.9:
            return None
    return f"{path}: its own title '{norm(got)[:90]}' is not the record's '{want[:90]}'"


def ledger_check(root: str = _ROOT) -> dict[str, list[str]]:
    """{'mismatch': [...], 'quarantined': [...], 'no_record': [...], 'ok': [...]} over every held article whose file is
    present locally (a PDF/HTML that is not redistributed may be absent from a clean clone: that is not a pass either,
    it is simply not checkable there)."""
    led = json.load(open(os.path.join(root, HELD, "HELD.json"), encoding="utf-8"))
    out = {"mismatch": [], "quarantined": [], "no_record": [], "ok": []}
    for rel, meta in sorted(led.items()):
        if not re.search(r"\.(pdf|html|xml)$", rel) or rel.startswith("_secondary/"):
            continue
        p = os.path.join(root, HELD, rel)
        if not os.path.exists(p):
            continue
        if meta.get("identity_quarantine"):
            out["quarantined"].append(f"{rel}: {meta['identity_quarantine']}")
            continue
        if meta.get("route") in ("regulatory_label",) or "regulatory" in rel.split("/")[0]:
            continue                                       # a regulator's document is not a journal publication
        recs = sorted(glob.glob(os.path.join(root, HELD, rel.split("/")[0], "europepmc_record_*.json")))
        recs = [r for r in recs if not re.search(r"\.[0-9a-f]{12}\.json$", r)] or recs
        if not recs:
            out["no_record"].append(rel)
            continue
        problem = check_held_document(p, record_identity(recs[0]))
        (out["mismatch"] if problem else out["ok"]).append(problem or rel)
    return out
