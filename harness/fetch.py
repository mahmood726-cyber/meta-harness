"""Fetch-once acquisition: PubMed (E-utilities) + ClinicalTrials.gov API v2.

Writes a committed cache/<slug>/records.json that the offline pipeline reads. Fetch
runs only when the cache is absent (idempotent), so re-running from a protocol SHA on a
fresh clone replays the committed cache and reproduces byte-for-byte.
"""
from __future__ import annotations
import os
import re
import time
import xml.etree.ElementTree as ET

_NCT_RE = re.compile(r"NCT\d{8}")

from . import http

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CTGOV = "https://clinicaltrials.gov/api/v2/studies"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _esearch(query: str, retmax: int = 40) -> list[str]:
    d = http.get_json(f"{EUTILS}/esearch.fcgi",
                      {"db": "pubmed", "term": query, "retmode": "json",
                       "retmax": retmax, "tool": "meta-harness", "email": "meta-harness@example.org"})
    time.sleep(0.34)
    return d.get("esearchresult", {}).get("idlist", [])


def _txt(el):
    return "".join(el.itertext()).strip() if el is not None else ""


def _efetch(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    xml = http.get_text(f"{EUTILS}/efetch.fcgi",
                        {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml",
                         "tool": "meta-harness", "email": "meta-harness@example.org"})
    time.sleep(0.34)
    root = ET.fromstring(xml)
    out = []
    for art in root.findall(".//PubmedArticle"):
        pmid = _txt(art.find(".//PMID"))
        title = _txt(art.find(".//ArticleTitle"))
        abstract = " ".join(
            (a.get("Label", "") + ": " if a.get("Label") else "") + _txt(a)
            for a in art.findall(".//Abstract/AbstractText")).strip()
        pubtypes = [_txt(p) for p in art.findall(".//PublicationType")]
        year = _txt(art.find(".//JournalIssue/PubDate/Year")) or _txt(art.find(".//JournalIssue/PubDate/MedlineDate"))[:4]
        journal = _txt(art.find(".//Journal/ISOAbbreviation"))
        doi = ""
        for eid in art.findall(".//ELocationID"):
            if eid.get("EIdType") == "doi":
                doi = _txt(eid)
        if not doi:
            for aid in art.findall(".//ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = _txt(aid)
        nct = ""
        for db in art.findall(".//DataBank"):
            if _txt(db.find("DataBankName")).lower().startswith("clinicaltrials"):
                acc = db.find(".//AccessionNumber")
                if acc is not None:
                    nct = _txt(acc)
        if not nct:  # fall back to an NCT id stated in the abstract (registry linkage)
            m = _NCT_RE.search(abstract)
            if m:
                nct = m.group(0)
        out.append({"id": pmid, "id_type": "pmid", "title": title, "abstract": abstract,
                    "pubtypes": pubtypes, "year": year, "journal": journal, "doi": doi, "nct": nct})
    return out


def _refs(pmid: str) -> list[str]:
    """PMIDs the given article cites (comparator-reference seeding for recall)."""
    try:
        d = http.get_json(f"{EUTILS}/elink.fcgi",
                          {"dbfrom": "pubmed", "db": "pubmed", "linkname": "pubmed_pubmed_refs",
                           "id": pmid, "retmode": "json", "tool": "meta-harness",
                           "email": "meta-harness@example.org"})
        time.sleep(0.34)
        out = []
        for ls in d.get("linksets", [{}])[0].get("linksetdbs", []):
            if ls.get("linkname") == "pubmed_pubmed_refs":
                out = ls.get("links", [])
        return out
    except Exception:  # noqa: BLE001
        return []


def _pmc_fulltext(pmid: str) -> str:
    """Best-effort: resolve PubMed->PMC and return the article body text, else ''."""
    try:
        d = http.get_json(f"{EUTILS}/elink.fcgi",
                          {"dbfrom": "pubmed", "db": "pmc", "id": pmid, "retmode": "json",
                           "tool": "meta-harness", "email": "meta-harness@example.org"})
        time.sleep(0.34)
        linksets = d.get("linksets", [{}])[0].get("linksetdbs", [])
        pmcid = None
        for ls in linksets:
            if ls.get("dbto") == "pmc" and ls.get("links"):
                pmcid = ls["links"][0]
                break
        if not pmcid:
            return ""
        xml = http.get_text(f"{EUTILS}/efetch.fcgi",
                           {"db": "pmc", "id": pmcid, "retmode": "xml",
                            "tool": "meta-harness", "email": "meta-harness@example.org"})
        time.sleep(0.34)
        root = ET.fromstring(xml)
        body = root.find(".//body")
        return " ".join(body.itertext()).strip() if body is not None else ""
    except Exception:  # noqa: BLE001 - full text is optional; fall back to abstract
        return ""


def _ctgov_results(nct: str):
    """Structured outcome-measure tables for a trial with posted results (AACT-equivalent)."""
    try:
        d = http.get_json(f"{CTGOV}/{nct}",
                          {"fields": "hasResults,resultsSection.outcomeMeasuresModule"})
        time.sleep(0.2)
        if not d.get("hasResults"):
            return None
        oms = d.get("resultsSection", {}).get("outcomeMeasuresModule", {}).get("outcomeMeasures", [])
        return oms or None
    except Exception:  # noqa: BLE001 - results are optional
        return None


def _ctgov_search(cond: str, intr: str, page_size: int = 30) -> list[dict]:
    params = {"pageSize": page_size, "fields":
              "protocolSection.identificationModule,protocolSection.designModule,"
              "protocolSection.conditionsModule,protocolSection.armsInterventionsModule,"
              "protocolSection.statusModule,hasResults"}
    if cond:
        params["query.cond"] = cond
    if intr:
        params["query.intr"] = intr
    d = http.get_json(CTGOV, params)
    out = []
    for s in d.get("studies", []):
        ps = s.get("protocolSection", {})
        idm = ps.get("identificationModule", {})
        dm = ps.get("designModule", {})
        design = dm.get("designInfo", {}) or {}
        masking = (design.get("maskingInfo", {}) or {}).get("masking", "")
        interventions = [i.get("name", "") for i in (ps.get("armsInterventionsModule", {}) or {}).get("interventions", [])]
        out.append({
            "id": idm.get("nctId"), "id_type": "nct",
            "title": idm.get("briefTitle", ""),
            "acronym": idm.get("acronym", ""),
            "study_type": dm.get("studyType", ""),
            "allocation": design.get("allocation", ""),
            "masking": masking,
            "conditions": (ps.get("conditionsModule", {}) or {}).get("conditions", []),
            "interventions": interventions,
            "has_results": s.get("hasResults", False),
            "abstract": ""})
    return out


def run(config: dict) -> dict:
    """Fetch and return the records dict for a topic config (does not write)."""
    pmids: list[str] = []
    for q in config.get("pubmed_queries", []):
        for pid in _esearch(q, config.get("retmax", 25)):
            if pid not in pmids:
                pmids.append(pid)
    for pid in config.get("extra_pmids", []) + config.get("negative_control_pmids", []) + [config.get("comparator_pmid", "")]:
        if pid and pid not in pmids:
            pmids.append(pid)
    # F4 recall: seed with the trials the comparator itself cited, then screen by our rules.
    if config.get("comparator_pmid") and config.get("seed_comparator_refs", True):
        for pid in _refs(config["comparator_pmid"]):
            if pid not in pmids:
                pmids.append(pid)
    pmids = pmids[:config.get("max_records", 150)]
    pubmed = []
    for i in range(0, len(pmids), 20):
        pubmed.extend(_efetch(pmids[i:i + 20]))
    ctgov = []
    cg = config.get("ctgov")
    if cg:
        ctgov = _ctgov_search(cg.get("cond", ""), cg.get("intr", ""))
    comparator_oa = None
    comp_doi = ""
    for r in pubmed:
        if r["id"] == config.get("comparator_pmid"):
            comp_doi = r.get("doi", "")
    if comp_doi:
        try:
            d = http.get_json(f"https://api.unpaywall.org/v2/{comp_doi}",
                              {"email": "meta-harness@example.org"})
            loc = d.get("best_oa_location") or {}
            comparator_oa = {"is_oa": bool(d.get("is_oa")), "oa_url": loc.get("url", "")}
        except Exception as exc:  # noqa: BLE001
            comparator_oa = {"is_oa": None, "error": str(exc)}
    comparator_fulltext = ""
    if config.get("comparator_pmid"):
        comparator_fulltext = _pmc_fulltext(config["comparator_pmid"])
    # AACT/registry-results adapter: structured arm-level outcome tables per NCT with results.
    ncts = []
    for r in pubmed:
        if r.get("nct") and r["nct"] not in ncts:
            ncts.append(r["nct"])
    for c in ctgov:
        if c.get("has_results") and c.get("id") and c["id"] not in ncts:
            ncts.append(c["id"])
    ctgov_results = {}
    for nct in ncts[:config.get("max_results_lookup", 60)]:
        oms = _ctgov_results(nct)
        if oms:
            ctgov_results[nct] = oms
    return {"slug": config["slug"], "fetched_utc": config.get("_now", ""),
            "pubmed_queries": config.get("pubmed_queries", []),
            "ctgov_query": cg, "records": pubmed, "ctgov": ctgov,
            "comparator_pmid": config.get("comparator_pmid"), "comparator_oa": comparator_oa,
            "comparator_fulltext": comparator_fulltext, "ctgov_results": ctgov_results}


def cache_path(slug: str) -> str:
    return os.path.join(ROOT, "cache", slug, "records.json")


def ensure(config: dict, now: str):
    """Fetch into the committed cache if absent; return the loaded records dict."""
    import json
    path = cache_path(config["slug"])
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    config = dict(config, _now=now)
    data = run(config)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2))
    return data
