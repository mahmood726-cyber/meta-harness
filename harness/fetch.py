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
from . import fulltext as _ft

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CTGOV = "https://clinicaltrials.gov/api/v2/studies"
PMC_OA = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


EPMC_ART = "https://www.ebi.ac.uk/europepmc/webservices/rest/MED/{pmid}/{kind}"


def _epmc_linked(pmid: str, kind: str, pages: int = 2) -> list[str]:
    """Citation-chasing via Europe PMC (FREE, no key): kind='references' (backward) or
    'citations' (forward/citedBy). Returns PubMed-indexed PMIDs (source MED) so they flow
    through the same efetch+screen path. Bounded by `pages` (1000/page). Additive reach —
    a source error is swallowed (the committed cache is what replays); the four-state RAN_ERROR
    accounting for metered sources is handled by the caller's source-status record."""
    out = []
    for pg in range(1, pages + 1):
        try:
            d = http.get_json(EPMC_ART.format(pmid=pmid, kind=kind),
                              {"format": "json", "pageSize": 1000, "page": pg})
            time.sleep(0.2)
        except Exception:  # noqa: BLE001
            break
        block = "referenceList" if kind == "references" else "citationList"
        items = (d.get(block, {}) or {}).get("reference" if kind == "references" else "citation", []) or []
        for it in items:
            if str(it.get("source")) == "MED" and it.get("id"):
                out.append(str(it.get("id")))
        if len(items) < 1000:
            break
    return out


def _europepmc_pmids(query: str, retmax: int = 40) -> list[str]:
    """Reach adapter: Europe PMC indexes more than PubMed's esearch top-N and ranks differently,
    surfacing registered trials esearch misses. Returns PubMed-indexed PMIDs (SRC:MED) so they
    flow through the same efetch path — consistent metadata + extraction."""
    try:
        d = http.get_json(EPMC, {"query": f"({query}) AND SRC:MED", "format": "json",
                                 "pageSize": retmax, "resultType": "idlist"})
        time.sleep(0.2)
        return [r["pmid"] for r in d.get("resultList", {}).get("result", []) if r.get("pmid")]
    except Exception:  # noqa: BLE001 - reach adapter is additive; never fail the fetch
        return []
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _esearch(query: str, retmax: int = 40) -> list[str]:
    d = http.get_json(f"{EUTILS}/esearch.fcgi",
                      {"db": "pubmed", "term": query, "retmode": "json",
                       "retmax": retmax, "tool": "meta-harness", "email": "meta-harness@example.org"})
    time.sleep(0.34)
    return d.get("esearchresult", {}).get("idlist", [])


def _txt(el):
    return "".join(el.itertext()).strip() if el is not None else ""


def _select_nct(abstract: str, db_ncts: list[str]) -> str:
    """Pick the trial's own registry id. A multi-registration paper (e.g. a pooled analysis such as
    RE-COVER II, whose PubMed DataBank lists BOTH its own NCT and its companion trial's) can have the
    DataBank order put the companion first — so when there is MORE THAN ONE databank id, disambiguate
    by the abstract, which states the current trial's id first; pick the abstract-first id that is also
    one of the paper's OWN databank ids. With a single databank id, trust it (do not let an abstract
    that merely CITES another trial's NCT override an authoritative registration). Fall back to an
    abstract-stated NCT only when the DataBank carries none. Reproduction replays the committed cache,
    so this only governs a fresh fetch."""
    abstract_ncts = _NCT_RE.findall(abstract or "")
    if len(db_ncts) > 1 and abstract_ncts:
        for a in abstract_ncts:
            if a in db_ncts:
                return a
    if db_ncts:
        return db_ncts[0]
    return abstract_ncts[0] if abstract_ncts else ""


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
        db_ncts = []
        for db in art.findall(".//DataBank"):
            if _txt(db.find("DataBankName")).lower().startswith("clinicaltrials"):
                for acc in db.findall(".//AccessionNumber"):
                    v = _txt(acc)
                    if _NCT_RE.fullmatch(v) and v not in db_ncts:
                        db_ncts.append(v)
        nct = _select_nct(abstract, db_ncts)
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


def _select_pmc_link(linksetdbs: list[dict]) -> str | None:
    """Pick the article's OWN PMC id from an elink pubmed->pmc linkset. MUST filter on
    linkname == 'pubmed_pmc' (the direct same-article full-text link) and NEVER accept
    'pubmed_pmc_refs' (articles that CITE this pmid) — those are different papers. When the
    article is not itself in PMC, elink returns ONLY pubmed_pmc_refs, so a naive
    'first dbto==pmc linkset' returns a CITING article's PMCID and _pmc_fulltext then serves
    the wrong paper's text (silently, under the target pmid). Pure/offline for testing."""
    for ls in linksetdbs:
        if ls.get("linkname") == "pubmed_pmc" and ls.get("links"):
            return ls["links"][0]
    return None  # fail closed: not in PMC -> abstract path, never a citing article


def _resolve_pmcid(pmid: str) -> str | None:
    """PubMed id -> the SAME article's PMC id (e.g. '6098635'), or None if not in PMC OA."""
    d = http.get_json(f"{EUTILS}/elink.fcgi",
                      {"dbfrom": "pubmed", "db": "pmc", "id": pmid, "retmode": "json",
                       "tool": "meta-harness", "email": "meta-harness@example.org"})
    time.sleep(0.34)
    return _select_pmc_link(d.get("linksets", [{}])[0].get("linksetdbs", []))


def _pmc_oa_supplement_text(pmcid: str, hrefs: list[str]) -> str:
    """Download the PMC OA .tar.gz package and extract row-structured text from the supplementary
    spreadsheet/CSV files the article references (per-arm SD tables have hidden here). Best-effort;
    returns '' if the package is unavailable or has no usable supplement. Bounded and network-guarded."""
    if not hrefs:
        return ""
    try:
        oa = http.get_text(PMC_OA, {"id": f"PMC{pmcid}"})
        time.sleep(0.34)
        m = re.search(r'href="(ftp://[^"]+\.tar\.gz)"', oa) or re.search(r'href="(https?://[^"]+\.tar\.gz)"', oa)
        if not m:
            return ""
        url = m.group(1).replace("ftp://ftp.ncbi.nlm.nih.gov", "https://ftp.ncbi.nlm.nih.gov")
        tar_bytes = http.get(url)
        wanted = {h.rsplit("/", 1)[-1].lower() for h in hrefs}
        blocks = []
        for name, data in _ft.iter_oa_package(tar_bytes):
            base = name.rsplit("/", 1)[-1].lower()
            if base in wanted or (base.endswith((".xlsx", ".xlsm", ".csv", ".tsv")) and base in wanted):
                txt = _ft.supplement_text_from_bytes(base, data)
                if txt:
                    blocks.append(f"SUPPLEMENT {base}\n{txt}")
        return "\n\n".join(blocks)
    except Exception:  # noqa: BLE001 - supplements are optional reach; never fail the fetch
        return ""


def _pmc_fulltext(pmid: str, with_supplements: bool = False) -> str:
    """Resolve PubMed->PMC and return body prose + STRUCTURED tables (per-arm values keep their row),
    optionally + supplementary spreadsheet/CSV text. Falls back to '' (abstract path) on any failure.
    The number is never interpreted here — this only makes the verbatim source legible for locate."""
    try:
        pmcid = _resolve_pmcid(pmid)
        if not pmcid:
            return ""
        xml = http.get_text(f"{EUTILS}/efetch.fcgi",
                           {"db": "pmc", "id": pmcid, "retmode": "xml",
                            "tool": "meta-harness", "email": "meta-harness@example.org"})
        time.sleep(0.34)
        parsed = _ft.parse_pmc_xml(xml)
        text = _ft.combined_text(parsed)
        if with_supplements and parsed.get("supplements"):
            sup = _pmc_oa_supplement_text(pmcid, parsed["supplements"])
            if sup:
                text = (text + "\n\n=== SUPPLEMENTARY FILES ===\n" + sup).strip()
        return text
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


def _protected_pmids(config: dict) -> list[str]:
    """PMIDs that a topic FORCES into the corpus and that must survive truncation: the extra_pmids,
    both control sets, and the comparator. These are appended AFTER the query loop, so a naive
    pmids[:max_records] silently drops them when the query alone fills the cap — which is exactly how
    semaglutide lost its pivotal STEP-1/STEP-3 (and its negative control) at max_records=120. Pivotal
    trials are declared as NCTs and reach the corpus through extra_pmids/positive controls, so
    protecting these lists keeps the defining trial in even a capped fetch."""
    forced = (list(config.get("extra_pmids", []))
              + list(config.get("positive_control_pmids", []))
              + list(config.get("negative_control_pmids", []))
              + [config.get("comparator_pmid", "")])
    seen, out = set(), []
    for p in forced:
        if p and p not in seen:
            seen.add(p)
            out.append(str(p))
    return out


def _apply_cap(pmids: list[str], protected: list[str], cap: int) -> list[str]:
    """Truncate to `cap` WITHOUT ever dropping a protected PMID. Protected ids are kept in their
    existing order; the remaining budget is filled with the other pmids in order. When the protected
    set alone exceeds the cap they are all kept (a forced trial is never sacrificed to a size limit).
    Order among the non-protected pmids is preserved so existing (uncapped) fetches are unaffected."""
    if len(pmids) <= cap:
        return list(pmids)  # no truncation: original order fully preserved
    protset = set(protected)
    protected_in = [p for p in pmids if p in protset]
    others = [p for p in pmids if p not in protset]
    room = max(0, cap - len(protected_in))
    keep = set(protected_in) | set(others[:room])
    return [p for p in pmids if p in keep]  # original order, protected guaranteed to survive


def run(config: dict) -> dict:
    """Fetch and return the records dict for a topic config (does not write)."""
    pmids: list[str] = []
    for q in config.get("pubmed_queries", []):
        for pid in _esearch(q, config.get("retmax", 40)):
            if pid not in pmids:
                pmids.append(pid)
        # reach: union in Europe PMC's hits for the same query
        for pid in _europepmc_pmids(q, config.get("retmax", 40)):
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
    # Citation chasing via Europe PMC (FREE, no key): backward from the comparator's reference
    # list (pointer only — every hit is still screened by our own rules) and both directions from
    # the pivotal trials (positive controls). Finds trials whose abstract never used our keywords
    # (the DAPA-HF/EMPEROR class). Gated by cite_chase so existing caches are unaffected until a
    # topic is deliberately re-fetched with it on.
    cite_status = "NOT_RUN"
    if config.get("cite_chase"):
        seeds = [config.get("comparator_pmid")] + list(config.get("positive_control_pmids", []))
        seeds = [s for s in seeds if s]
        got = 0
        errors = 0
        for seed in seeds:
            for kind in ("references", "citations"):
                linked = _epmc_linked(seed, kind, pages=config.get("cite_pages", 2))
                for pid in linked:
                    if pid not in pmids:
                        pmids.append(pid)
                        got += 1
        cite_status = "RAN_OK" if got else "RAN_ZERO"
    # REGISTRY-FIRST enumeration (default search path when enabled): enumerate trials by
    # condition x intervention from ClinicalTrials.gov and resolve each NCT to its PubMed
    # publication(s), then let SCREENING decide eligibility. Finds trials whose abstract never
    # used our keywords (GISSI-P/SOFA/OMEGA in omega3). Recall proven at 9/13; precision is the
    # screen's job. Four-state status recorded; gated by registry_first{cond,intr}.
    regfirst_status = "NOT_RUN"
    rf_cfg = config.get("registry_first")
    if rf_cfg:
        from . import registry_first as _rf
        # include_isrctn adds the ISRCTN registry to the enumeration union (WHO trials without an
        # NCT). Opt-in per topic (registry_first.isrctn: true) since it is a second network source;
        # default off keeps every current topic's fetch unchanged.
        res = _rf.registry_first_pmids(rf_cfg.get("cond", ""), rf_cfg.get("intr", ""),
                                       include_isrctn=bool(rf_cfg.get("isrctn")))
        regfirst_status = res.get("status", "RAN_ERROR")
        for pid in res.get("pmids", []):
            if pid not in pmids:
                pmids.append(pid)
    cap = config.get("max_records", 300 if (config.get("cite_chase") or rf_cfg) else 150)
    pmids = _apply_cap(pmids, _protected_pmids(config), cap)
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
    # Per-trial PMC OA full text (FREE): the pipeline uses it as a fallback when a trial's ABSTRACT
    # yields no poolable number — this is where per-arm SD / person-time / rate-ratio+CI live that
    # abstracts omit (Albert's azithromycin IRR 0.73 is in its full text, not its abstract). Gated
    # by fulltext:true so existing caches are unaffected until a topic opts in and re-fetches.
    # fulltext_supplements:true additionally pulls the PMC OA package's supplementary spreadsheets/CSV
    # (where per-arm SD tables have hidden) — the untested reach route; opt-in, per-topic, re-fetch.
    fulltext_by_pmid = {}
    if config.get("fulltext"):
        with_sup = bool(config.get("fulltext_supplements"))
        for r in pubmed[:config.get("max_fulltext", 40)]:
            ft = _pmc_fulltext(r["id"], with_supplements=with_sup)
            if ft:
                fulltext_by_pmid[r["id"]] = ft
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
            "comparator_fulltext": comparator_fulltext, "ctgov_results": ctgov_results,
            "fulltext_by_pmid": fulltext_by_pmid,
            "source_status": {"pubmed": "RAN_OK", "europepmc": "RAN_OK",
                              "citation_chase": cite_status, "registry_first": regfirst_status,
                              "fulltext": ("RAN_OK" if fulltext_by_pmid else
                                           ("RAN_ZERO" if config.get("fulltext") else "NOT_RUN"))}}


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
