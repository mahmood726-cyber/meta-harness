"""Fetch-once acquisition: PubMed (E-utilities) + ClinicalTrials.gov API v2.

Writes a committed cache/<slug>/records.json that the offline pipeline reads. Fetch
runs only when the cache is absent (idempotent), so re-running from a protocol SHA on a
fresh clone replays the committed cache and reproduces byte-for-byte.
"""
from __future__ import annotations
from contextlib import nullcontext
import json
import os
import re
import time
import xml.etree.ElementTree as ET

_NCT_RE = re.compile(r"NCT\d{8}")

from . import http
from . import fulltext as _ft
from . import acquisition as _acq

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
        d = http.get_json(EPMC_ART.format(pmid=pmid, kind=kind),
                          {"format": "json", "pageSize": 1000, "page": pg})
        time.sleep(0.2)
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
    d = http.get_json(EPMC, {"query": f"({query}) AND SRC:MED", "format": "json",
                             "pageSize": retmax, "resultType": "idlist"})
    time.sleep(0.2)
    return [r["pmid"] for r in d.get("resultList", {}).get("result", []) if r.get("pmid")]
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


def _dedupe(values) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values or []:
        s = str(value)
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _append_unique(target: list[str], ids) -> None:
    have = set(target)
    for pid in ids or []:
        s = str(pid)
        if s and s not in have:
            target.append(s)
            have.add(s)


def _source_funnel(hits, fetched: int, retained: int | None = None, cap: dict | None = None) -> dict:
    return {
        "hits": hits,
        "fetched": int(fetched),
        "retained": int(fetched if retained is None else retained),
        "cap": cap or {"kind": "none", "n": None, "remainder": None},
    }


def _uid_query_result(query: str) -> dict:
    ids = _dedupe(re.findall(r"(\d+)\s*\[uid\]", query, flags=re.I))
    return {
        "ids": ids,
        "count": len(ids),
        "state": "RAN_OK" if ids else "RAN_ZERO",
        "error": None,
        "funnel": _source_funnel(len(ids), len(ids)),
    }


def _maybe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _europepmc_result(query: str, retmax: int) -> dict:
    d = http.get_json(EPMC, {"query": f"({query}) AND SRC:MED", "format": "json",
                             "pageSize": retmax, "resultType": "idlist"})
    time.sleep(0.2)
    ids = [str(r["pmid"]) for r in d.get("resultList", {}).get("result", []) if r.get("pmid")]
    total = _maybe_int(d.get("hitCount"))
    if total is None:
        hits = None if ids else 0
        remainder = None if ids else 0
    else:
        hits = total
        remainder = max(0, total - len(ids))
    return {
        "ids": ids,
        "count": total,
        "state": "RAN_OK" if ids else "RAN_ZERO",
        "error": None,
        "funnel": _source_funnel(
            hits,
            len(ids),
            len(ids),
            {"kind": "relevance_top_n", "n": retmax, "remainder": remainder},
        ),
    }


def _registry_first_result(rf_cfg: dict) -> dict:
    from . import registry_first as _rf

    res = _rf.registry_first_pmids(rf_cfg.get("cond", ""), rf_cfg.get("intr", ""),
                                   include_isrctn=bool(rf_cfg.get("isrctn")))
    state = res.get("status", "RAN_ERROR")
    ids = _dedupe(res.get("pmids", [])) if state != "RAN_ERROR" else []
    error = None if state != "RAN_ERROR" else (res.get("error") or "registry_first returned RAN_ERROR")
    hits = len(ids) if state != "RAN_ERROR" else None
    return {"ids": ids, "count": hits, "state": state, "error": error,
            "funnel": _source_funnel(hits, len(ids))}


def _coerce_source_result(raw, id_getter=None) -> tuple[list[str], str, str | None, dict, object]:
    if isinstance(raw, dict) and "ids" in raw:
        state = raw.get("state") or ("RAN_OK" if raw.get("ids") else "RAN_ZERO")
        ids = _dedupe(raw.get("ids", [])) if state != "RAN_ERROR" else []
        error = raw.get("error")
        if state == "RAN_ERROR":
            error = error or "source returned RAN_ERROR"
            funnel = _source_funnel(None, 0)
        else:
            funnel = raw.get("funnel") or _source_funnel(len(ids), len(ids))
        return ids, state, error, funnel, raw
    items = list(raw or [])
    if id_getter:
        ids = _dedupe(id_getter(item) for item in items)
    else:
        ids = _dedupe(items)
    return ids, ("RAN_OK" if ids else "RAN_ZERO"), None, _source_funnel(len(ids), len(ids)), items


def _run_source(ledger: dict, kind: str, query: str, run_utc: str, discovery_capable: bool,
                call, id_getter=None, adapter: str | None = None) -> tuple[str, list[str], object]:
    source_id = _acq.reserve_source_id(ledger, kind)
    recorder = getattr(http, "RECORDER", None)
    scope = recorder.source(source_id, adapter or "harness.fetch._run_source") if recorder else nullcontext()
    try:
        with scope:
            ids, state, error, funnel, payload = _coerce_source_result(call(), id_getter=id_getter)
    except Exception as exc:  # noqa: BLE001 - every adapter failure is explicit provenance.
        ids, state, error, funnel, payload = [], "RAN_ERROR", str(exc), _source_funnel(None, 0), None
    source_id = _acq.add_source(
        ledger,
        kind,
        query,
        run_utc,
        state,
        error,
        funnel,
        ids,
        discovery_capable,
        source_id=source_id,
    )
    return source_id, ids, payload


_STATUS_RANK = {"NOT_RUN": 0, "RAN_ZERO": 1, "RAN_OK": 2, "RAN_ERROR": 3}


def _worst_state(states) -> str:
    states = [s for s in states if s in _STATUS_RANK]
    if not states:
        return "NOT_RUN"
    return max(states, key=lambda s: _STATUS_RANK[s])


def _source_status_from_ledger(ledger: dict, fulltext_status: str) -> dict:
    by_kind: dict[str, list[str]] = {}
    for source in ledger.get("sources", []):
        by_kind.setdefault(source.get("kind"), []).append(source.get("state"))
    return {
        "pubmed": _worst_state(
            by_kind.get("PUBMED_CONCEPT_QUERY", [])
            + by_kind.get("PUBMED_LEGACY_QUERY", [])
            + by_kind.get("PUBMED_PMID_ENUMERATION", [])
        ),
        "europepmc": _worst_state(by_kind.get("EUROPEPMC_QUERY", [])),
        "citation_chase": _worst_state(
            by_kind.get("COMPARATOR_REFERENCES", []) + by_kind.get("CITATION_CHASE", [])
        ),
        "registry_first": _worst_state(by_kind.get("REGISTRY_FIRST", [])),
        "fulltext": fulltext_status,
    }


def _attach_retained_records(ledger: dict, kept_pmids: list[str]) -> None:
    kept = set(kept_pmids)
    ledger["records"] = {}
    for source in ledger.get("sources", []):
        if source.get("kind") == "CTGOV_SEARCH":
            continue
        retained = [rid for rid in source.get("record_ids", []) if rid in kept]
        source["record_ids"] = retained
        source.setdefault("funnel", {})["retained"] = len(retained)
        if retained:
            _acq.attach_records(ledger, source["source_id"], retained)



def _run_with_recorder(config: dict, recorder: _acq.RawRecorder) -> dict:
    """Fetch records and a retrieval ledger for a topic config (does not write)."""
    run_utc = config.get("_now", "")
    ledger = _acq.new_ledger(config["slug"])
    pmids: list[str] = []

    # THE CONCEPT QUERY RUNS FOR EVERY TOPIC, FIRST. Fourteen live topics have only `<uid>[uid]` enumerations
    # as pubmed_queries -- they have had no search at all. The query built from the registered P/I/C/design is
    # the discovery-capable source; the legacy queries below are recorded for what they are. Skipped (NOT_RUN,
    # stated) only when the config carries neither intervention nor population terms, because a bare design
    # filter is not a question. Opt out per topic with concept_query: false (recorded as NOT_RUN, never silent).
    _cq = _acq.concept_query(config) if config.get("concept_query", True) else ""
    _has_terms = bool(config.get("intervention_terms")) or bool((config.get("include") or {}).get("population_any"))
    if _cq and _has_terms:
        _, ids, _ = _run_source(ledger, "PUBMED_CONCEPT_QUERY", _cq, run_utc, True,
                                lambda q=_cq: _acq.esearch_all(q, hard_cap=config.get("max_hits")),
                                adapter="harness.acquisition.esearch_all")
        _append_unique(pmids, ids)
    else:
        _acq.add_source(ledger, "PUBMED_CONCEPT_QUERY", _cq, run_utc, "NOT_RUN", None,
                        _source_funnel(None, 0), [], True)

    for q in config.get("pubmed_queries", []):
        kind = _acq.classify_query(q)
        discovery = kind != "PUBMED_PMID_ENUMERATION"
        if kind == "PUBMED_PMID_ENUMERATION":
            _, ids, _ = _run_source(
                ledger,
                kind,
                q,
                run_utc,
                discovery,
                lambda q=q: _uid_query_result(q),
                adapter="harness.fetch._uid_query_result",
            )
        else:
            _, ids, _ = _run_source(
                ledger,
                kind,
                q,
                run_utc,
                discovery,
                lambda q=q: _acq.esearch_all(q, hard_cap=config.get("max_hits")),
                adapter="harness.acquisition.esearch_all",
            )
        _append_unique(pmids, ids)

        retmax = config.get("retmax", 40)
        _, ids, _ = _run_source(
            ledger,
            "EUROPEPMC_QUERY",
            q,
            run_utc,
            True,
            lambda q=q, retmax=retmax: _europepmc_result(q, retmax),
            adapter="harness.fetch._europepmc_result",
        )
        _append_unique(pmids, ids)

    extras = _dedupe(config.get("extra_pmids", []))
    if extras:
        _, ids, _ = _run_source(ledger, "EXTRA_PMIDS", "config.extra_pmids", run_utc, False,
                                lambda extras=extras: list(extras),
                                adapter="harness.fetch._protected_config_pmids")
        _append_unique(pmids, ids)

    # NEGATIVE controls and the comparator are forced in (as before this layer). POSITIVE controls are NOT:
    # a positive control is a trial the search must FIND on its own -- fetching it by name would make the
    # positive-control recall check pass vacuously. (Lane A had added them; corrected at integration.)
    controls = _dedupe(
        list(config.get("negative_control_pmids", []))
        + [config.get("comparator_pmid", "")]
    )
    if controls:
        _, ids, _ = _run_source(ledger, "CONTROL_PMIDS", "config negative controls + comparator", run_utc, False,
                                lambda controls=controls: list(controls),
                                adapter="harness.fetch._protected_config_pmids")
        _append_unique(pmids, ids)

    if config.get("comparator_pmid") and config.get("seed_comparator_refs", True):
        _, ids, _ = _run_source(
            ledger,
            "COMPARATOR_REFERENCES",
            str(config["comparator_pmid"]),
            run_utc,
            True,
            lambda pmid=config["comparator_pmid"]: _refs(pmid),
            adapter="harness.fetch._refs",
        )
        _append_unique(pmids, ids)

    if config.get("cite_chase"):
        seeds = [config.get("comparator_pmid")] + list(config.get("positive_control_pmids", []))
        for seed in [s for s in seeds if s]:
            for kind in ("references", "citations"):
                _, ids, _ = _run_source(
                    ledger,
                    "CITATION_CHASE",
                    f"{seed} {kind} pages={config.get('cite_pages', 2)}",
                    run_utc,
                    True,
                    lambda seed=seed, kind=kind: _epmc_linked(seed, kind, pages=config.get("cite_pages", 2)),
                    adapter="harness.fetch._epmc_linked",
                )
                _append_unique(pmids, ids)

    rf_cfg = config.get("registry_first")
    if rf_cfg:
        _, ids, _ = _run_source(
            ledger,
            "REGISTRY_FIRST",
            json.dumps(rf_cfg, sort_keys=True),
            run_utc,
            True,
            lambda rf_cfg=rf_cfg: _registry_first_result(rf_cfg),
            adapter="harness.registry_first.registry_first_pmids",
        )
        _append_unique(pmids, ids)

    # RECORD CAP: a size cap is a ranked truncation and cannot close a k gap (pivotal is not largest). The
    # default is therefore NO cap; a topic that sets max_records keeps it, and the truncation is recorded on the
    # ledger (record_cap + dropped_by_cap) and rendered with its remainder -- never silent.
    cap = config.get("max_records")
    before_cap = list(pmids)
    if cap:
        pmids = _apply_cap(pmids, _protected_pmids(config), cap)
    dropped = [pid for pid in before_cap if pid not in set(pmids)]
    if dropped:
        ledger["record_cap"] = {
            "kind": "record_cap",
            "n": cap,
            "before": len(before_cap),
            "after": len(pmids),
            "remainder": len(before_cap) - len(pmids),
        }
        ledger["dropped_by_cap"] = dropped
    _attach_retained_records(ledger, pmids)

    pubmed = []
    for i in range(0, len(pmids), 20):
        with recorder.source(f"pubmed_efetch#{i // 20 + 1}", "harness.fetch._efetch"):
            pubmed.extend(_efetch(pmids[i:i + 20]))

    ctgov = []
    cg = config.get("ctgov")
    if cg:
        _, _, payload = _run_source(
            ledger,
            "CTGOV_SEARCH",
            json.dumps(cg, sort_keys=True),
            run_utc,
            True,
            lambda cg=cg: _ctgov_search(cg.get("cond", ""), cg.get("intr", "")),
            id_getter=lambda row: row.get("id"),
            adapter="harness.fetch._ctgov_search",
        )
        ctgov = payload if isinstance(payload, list) else []

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

    fulltext_by_pmid = {}
    if config.get("fulltext"):
        with_sup = bool(config.get("fulltext_supplements"))
        for r in pubmed[:config.get("max_fulltext", 40)]:
            ft = _pmc_fulltext(r["id"], with_supplements=with_sup)
            if ft:
                fulltext_by_pmid[r["id"]] = ft
    fulltext_status = ("RAN_OK" if fulltext_by_pmid else
                       ("RAN_ZERO" if config.get("fulltext") else "NOT_RUN"))

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

    data = {"slug": config["slug"], "fetched_utc": config.get("_now", ""),
            "pubmed_queries": config.get("pubmed_queries", []),
            "ctgov_query": cg, "records": pubmed, "ctgov": ctgov,
            "comparator_pmid": config.get("comparator_pmid"), "comparator_oa": comparator_oa,
            "comparator_fulltext": comparator_fulltext, "ctgov_results": ctgov_results,
            "fulltext_by_pmid": fulltext_by_pmid,
            "source_status": _source_status_from_ledger(ledger, fulltext_status)}
    _acq.finalize(ledger, pubmed, config.get("_now", ""), "REFRESH")
    ledger["snapshot"]["raw_calls"] = recorder.count
    data["retrieval_ledger"] = ledger
    data["_raw_recorder"] = recorder
    return data


def run(config: dict) -> dict:
    """Fetch records and a retrieval ledger for a topic config (does not write)."""
    recorder = _acq.RawRecorder()
    previous_recorder = http.RECORDER
    http.RECORDER = recorder
    try:
        return _run_with_recorder(config, recorder)
    finally:
        http.RECORDER = previous_recorder


def cache_path(slug: str) -> str:
    return os.path.join(ROOT, "cache", slug, "records.json")


def ensure(config: dict, now: str):
    """Fetch into the committed cache if absent; return the loaded records dict."""
    path = cache_path(config["slug"])
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    config = dict(config, _now=now)
    data = run(config)
    ledger = data.get("retrieval_ledger")
    records_data = dict(data)
    records_data.pop("retrieval_ledger", None)
    raw_recorder = records_data.pop("_raw_recorder", None)
    if isinstance(ledger, dict):
        violations = _acq.validate(ledger, records_data.get("records", []))
        if violations:
            raise ValueError("invalid retrieval ledger: " + "; ".join(violations))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(ledger, dict) and isinstance(raw_recorder, _acq.RawRecorder):
        raw_calls, raw_index_sha = raw_recorder.write_snapshot(os.path.dirname(path))
        ledger.setdefault("snapshot", {})["raw_calls"] = raw_calls
        if raw_index_sha:
            ledger["snapshot"]["raw_index_sha256"] = raw_index_sha
        else:
            ledger["snapshot"].pop("raw_index_sha256", None)
        violations = _acq.validate(ledger, records_data.get("records", []), snapshot_dir=os.path.dirname(path))
        if violations:
            raise ValueError("invalid retrieval snapshot: " + "; ".join(violations))
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(records_data, ensure_ascii=False, indent=2))
    if isinstance(ledger, dict):
        with open(os.path.join(os.path.dirname(path), _acq.LEDGER_FILENAME), "w",
                  encoding="utf-8", newline="") as f:
            f.write(json.dumps(ledger, ensure_ascii=False, indent=2))
    return records_data
