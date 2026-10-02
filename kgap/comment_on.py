"""COMMENT-ON identity edge: a comparator unit that is a LETTER / COMMENT stands for the article it comments on.

PubMed records it as typed data: <CommentsCorrections RefType="CommentOn"><PMID>...</PMID>. A comparator sometimes cites
a trial through a letter about it -- sglt2-primary-prevention-hf's 'Isreb (19)' is the NEJM letter 31509682
('Canagliflozin and Renal Outcomes in Diabetic Nephropathy', Letter + Comment), and the comparator's row for it
(89/2202 vs 141/2199) is CREDENCE's heart-failure data. The letter's own record says nothing about the trial's design or
population; the article it comments on does.

  fetch(pmids)          PubMed efetch (harness.http), once; each answer recorded in outputs/k_gap/comment_on.json with the
                        query, the date and the sha256 of the XML it was read from
  record(pmid)          the recorded entry: comment_on (resolved PMIDs, one per CommentOn ELEMENT, in order) and
                        comment_on_unresolved (CommentOn elements with no PMID) -- offline; {} when not recorded

Parsed STRUCTURALLY (xml.etree): a PMID belongs to the CommentsCorrections element that contains it, never to the next
one (NR-C24: a regex read a PMID-less CommentOn as the following CommentIn's target); PMIDs are stripped and must be
digits; two records with the same own PMID and different edges are refused.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(ROOT, "outputs", "k_gap", "comment_on.json")
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _load():
    if os.path.exists(REC):
        with open(REC, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def _pmid(el) -> str | None:
    t = (el.text or "").strip() if el is not None else ""
    return t if t.isdigit() else None


def parse(xml: str) -> dict:
    """{pmid: {'comment_on': [...], 'comment_on_unresolved': n, 'pubtypes': [...]}} for every PubmedArticle."""
    out = {}
    root = ET.fromstring(xml)
    for art in root.iter("PubmedArticle"):
        mc = art.find("MedlineCitation")
        own = _pmid(mc.find("PMID")) if mc is not None else None
        if not own:
            continue
        edges, unresolved = [], 0
        for cc in art.iter("CommentsCorrections"):
            if cc.get("RefType") != "CommentOn":
                continue
            p = _pmid(cc.find("PMID"))
            if p:
                edges.append(p)
            else:
                unresolved += 1
        entry = {"comment_on": edges, "comment_on_unresolved": unresolved,
                 "pubtypes": [(p.text or "").strip() for p in art.iter("PublicationType")]}
        if own in out and out[own] != entry:
            raise ValueError(f"PubMed returned two different records for PMID {own}: refusing to choose")
        out[own] = entry
    return out


def fetch(pmids) -> dict:
    """Record the CommentOn edges of `pmids` (network, once; already-recorded PMIDs are not refetched)."""
    from harness import http
    rec = _load()
    todo = sorted({str(p) for p in pmids} - set(rec))
    if todo:
        params = {"db": "pubmed", "id": ",".join(todo), "retmode": "xml", "tool": "meta-harness",
                  "email": "meta-harness@example.org"}
        xml = http.get_text(f"{EUTILS}/efetch.fcgi", params)
        sha = hashlib.sha256(xml.encode("utf-8")).hexdigest()
        got = parse(xml)
        for p in todo:
            if p not in got:
                raise RuntimeError(f"PubMed efetch returned no article for PMID {p} (refusing to record an absence)")
            rec[p] = dict(got[p], source=f"PubMed efetch db=pubmed id={params['id']} retmode=xml",
                          xml_sha256=sha, when=datetime.date.today().isoformat())
        with open(REC, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(rec, fh, indent=1, sort_keys=True)
    return {p: rec[str(p)] for p in pmids}


def record(pmid) -> dict:
    return dict(_load().get(str(pmid)) or {})


def comment_on(pmid) -> list[str]:
    return list(record(pmid).get("comment_on") or [])
