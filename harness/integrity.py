"""Trial-integrity checks — the biggest current gap in evidence synthesis and fully automatable.

Retracted RCTs are still being pooled in published meta-analyses. PubMed exposes retraction and
expression-of-concern status for free (PublicationType "Retracted Publication"; CommentsCorrections
RefType "RetractionIn"/"ExpressionOfConcernIn"). This runs at measure time; results are committed to
cache/<slug>/integrity.json and replayed offline, and the gate REFUSES a page that pools a retracted
trial (a catastrophic defect). Verified true-positive on PMID 32450107 (the retracted Surgisphere
paper) and true-negative on a clean RCT.
"""
from __future__ import annotations

import re

from . import http

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL, EMAIL = "meta-harness", "meta-harness@example.org"

_PMID_BLOCK = re.compile(r"<PubmedArticle>.*?</PubmedArticle>", re.S)
_PMID = re.compile(r"<PMID[^>]*>(\d+)</PMID>")
_PUBTYPE = re.compile(r"<PublicationType[^>]*>([^<]+)</PublicationType>")
_REFTYPE = re.compile(r'<CommentsCorrections RefType="([^"]+)"')


def retraction_status(pmids: list[str]) -> dict[str, dict]:
    """Return {pmid: {retracted, concern, evidence}} for each PMID, from PubMed efetch. A trial is
    retracted if its own record carries the 'Retracted Publication' type or a 'RetractionIn' link;
    'ExpressionOfConcernIn' raises a (non-blocking) concern flag. Network is allowed to raise; the
    caller decides how to record failure (a check that cannot run must not silently pass)."""
    pmids = [str(p) for p in pmids if str(p).isdigit()]
    out: dict[str, dict] = {}
    for i in range(0, len(pmids), 100):
        chunk = pmids[i:i + 100]
        xml = http.get_text(f"{EUTILS}/efetch.fcgi",
                            {"db": "pubmed", "id": ",".join(chunk), "retmode": "xml",
                             "tool": TOOL, "email": EMAIL})
        for block in _PMID_BLOCK.findall(xml):
            m = _PMID.search(block)
            if not m:
                continue
            pmid = m.group(1)
            pubtypes = _PUBTYPE.findall(block)
            reftypes = _REFTYPE.findall(block)
            retracted = ("Retracted Publication" in pubtypes) or ("RetractionIn" in reftypes)
            concern = "ExpressionOfConcernIn" in reftypes
            ev = []
            if "Retracted Publication" in pubtypes:
                ev.append("PublicationType 'Retracted Publication'")
            if "RetractionIn" in reftypes:
                ev.append("CommentsCorrections 'RetractionIn'")
            if concern:
                ev.append("CommentsCorrections 'ExpressionOfConcernIn'")
            out[pmid] = {"retracted": retracted, "concern": concern,
                         "evidence": "; ".join(ev) or "no retraction/concern notice in PubMed"}
        for p in chunk:
            out.setdefault(p, {"retracted": False, "concern": False,
                               "evidence": "PMID not returned by PubMed efetch"})
    return out
