"""COMMENT-ON identity edge: a comparator unit that is a LETTER / COMMENT stands for the article it comments on.

PubMed records it as typed data: <CommentsCorrections RefType="CommentOn"><PMID>...</PMID>. A comparator sometimes cites
a trial through a letter about it -- sglt2-primary-prevention-hf's 'Isreb (19)' is the NEJM letter 31509682
('Canagliflozin and Renal Outcomes in Diabetic Nephropathy', Letter + Comment), and the comparator's row for it
(89/2202 vs 141/2199) is CREDENCE's heart-failure data. The letter's own record says nothing about the trial's design or
population; the article it comments on does.

  fetch(pmids)          PubMed efetch (harness.http), once; each answer recorded in outputs/k_gap/comment_on.json with the
                        query, the date and the sha256 of the XML it was read from
  comment_on(pmid)      the recorded CommentOn PMIDs (offline; [] when not recorded)
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(ROOT, "outputs", "k_gap", "comment_on.json")
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

_ARTICLE = re.compile(r"<PubmedArticle>.*?</PubmedArticle>", re.S)
_OWN_PMID = re.compile(r"<MedlineCitation[^>]*>\s*<PMID[^>]*>(\d+)</PMID>")
_CC = re.compile(r'<CommentsCorrections RefType="CommentOn">.*?<PMID[^>]*>(\d+)</PMID>.*?</CommentsCorrections>', re.S)
_PUBTYPE = re.compile(r"<PublicationType[^>]*>([^<]+)</PublicationType>")


def _load():
    if os.path.exists(REC):
        with open(REC, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def parse(xml: str) -> dict:
    """{pmid: {'comment_on': [...], 'pubtypes': [...]}} for every article in a PubMed efetch XML."""
    out = {}
    for art in _ARTICLE.findall(xml or ""):
        m = _OWN_PMID.search(art)
        if m:
            out[m.group(1)] = {"comment_on": sorted(set(_CC.findall(art))), "pubtypes": _PUBTYPE.findall(art)}
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


def comment_on(pmid) -> list[str]:
    return list((_load().get(str(pmid)) or {}).get("comment_on") or [])
