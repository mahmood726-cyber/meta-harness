"""Search v2 acquisition engine.

Builds auditable P/I/C concept queries for the development lane, writes unpinned
dated snapshots, and replays from those snapshots without network access.
"""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from contextlib import nullcontext
from datetime import datetime, timezone
from typing import Any

from . import acquisition as acq
from . import http
from . import lexicon
from . import screen
from .canonical import canonical_json
from .pipeline import _dedup, _query_classification, classify_query

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
EPMC_ARTICLE = "https://www.ebi.ac.uk/europepmc/webservices/rest/MED/{pmid}/{kind}"
CTGOV = "https://clinicaltrials.gov/api/v2/studies"

SEARCH_V2_VERSION = 1
SNAPSHOT_SUFFIX = "search_v2"
COCHRANE_RCT_FILTER_NAME = "Cochrane sensitivity-maximising RCT filter"
COCHRANE_PUBMED_RCT_FILTER = (
    "randomized controlled trial[pt] OR controlled clinical trial[pt] OR "
    "randomized[tiab] OR randomised[tiab] OR placebo[tiab] OR "
    "clinical trials as topic[mesh:noexp] OR randomly[tiab] OR trial[tiab]"
)
COCHRANE_EPMC_RCT_FILTER = (
    'PUB_TYPE:"randomized controlled trial" OR PUB_TYPE:"controlled clinical trial" OR '
    "TITLE_ABS:randomized OR TITLE_ABS:randomised OR TITLE_ABS:placebo OR "
    'TITLE_ABS:"controlled trial" OR TITLE_ABS:randomly'
)

DEVELOPMENT_TOPICS = [
    "balanced-crystalloids-vs-saline-mortality",
    "colchicine-recurrent-pericarditis",
    "corticosteroids-covid19-mortality",
    "doac-vte-recurrence",
    "dpp4-mace-t2d",
    "glp1-ra-mace-t2d",
    "melatonin-primary-insomnia-sol",
    "metformin-pcos-ovulation",
    "probiotics-aad-prevention",
    "semaglutide-obesity-mace",
    "sglt2-ckd-progression",
]

_NCT_RE = re.compile(r"\bNCT\d{8}\b", re.IGNORECASE)
_PMID_RE = re.compile(r"^\d+$")
_DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)


class QueryRefusal(ValueError):
    """A query would seed the search with a trial name or identifier."""


def _utc_now_seconds() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _today_utc() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _engine_sha() -> str:
    try:
        proc = subprocess.run(
            ["git", "hash-object", os.path.join("harness", "search_v2.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return proc.stdout.strip() or "unknown"
    except Exception:  # noqa: BLE001 - provenance only.
        return "unknown"


def _base_commit() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return proc.stdout.strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def _load_json(relpath: str) -> dict:
    with open(os.path.join(ROOT, relpath), encoding="utf-8") as f:
        return json.load(f)


def _read_text(relpath: str) -> str:
    with open(os.path.join(ROOT, relpath), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n").replace("\r", "\n")


def _dedupe(values) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values or []:
        text = str(value or "").strip()
        if not text:
            continue
        key = lexicon.fold(text)
        if key not in seen:
            seen.add(key)
            out.append(text)
    return out


def _flatten_agents(config: dict) -> list[str]:
    values: list[str] = []
    agents = config.get("intervention_agents") or {}
    if isinstance(agents, dict):
        for key, synonyms in agents.items():
            values.append(key)
            values.extend(synonyms or [])
    values.extend(config.get("intervention_class_terms") or [])
    if not values:
        values.extend(config.get("intervention_terms") or [])
    return _dedupe(values)


def _population_terms(config: dict) -> list[str]:
    return _dedupe((config.get("include") or {}).get("population_any") or [])


def _comparator_terms(config: dict) -> list[str]:
    return _dedupe(config.get("comparator_terms") or (config.get("include") or {}).get("comparator_any") or [])


def _pico_lines(protocol_text: str) -> list[str]:
    lines = protocol_text.splitlines()
    out: list[str] = []
    in_pico = False
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("## pico"):
            in_pico = True
            continue
        if in_pico and stripped.startswith("## "):
            break
        if in_pico and stripped:
            out.append(stripped)
    return out


def _feature_token(feature: str) -> str:
    return feature.split(":", 1)[1] if ":" in feature else feature


# --- sealed-vocabulary exemption (docs/evidence/search-v2-guard-2026-09-15/PROTOCOL.md) -------------------------
# The acronym heuristic in harness/pipeline.py flags any capitalised token with a hyphen or digit, or all-caps >= 4.
# Drug development codes (BAY94-8862, LCZ696), targets (PCSK9), procedures (CABG) and syndromes (NSTE-ACS) are all
# flagged, and a hand-grown allowlist is a record of which topics the engine has been run on, not a rule. A token is
# exempt only if it is covered by a term in the topic's registered vocabulary AND that vocabulary is sealed in
# registry/search_vocabulary_seal.json (hash of the vocabulary fields at the split-seal commit); a sealed term that
# equals a benchmark positive's registered acronym is refused AT SEAL TIME by scripts/seal_search_vocabulary.py (the
# engine never opens the benchmark; tests/test_search_benchmark_isolation.py). Unsealed vocabulary gets no exemption.
VOCABULARY_FIELDS = ("intervention_agents", "intervention_class_terms", "intervention_terms", "comparator_terms")
VOCABULARY_INCLUDE_FIELDS = ("population_any",)
VOCABULARY_SEAL_PATH = os.path.join("registry", "search_vocabulary_seal.json")
_WORD_SPLIT_RE = re.compile(r"\s+")


def vocabulary_fields(config: dict) -> dict:
    """Exactly the config fields the query builder draws terms from; the seal hashes this object."""
    out = {k: config.get(k) for k in VOCABULARY_FIELDS if config.get(k) is not None}
    include = config.get("include") or {}
    inc = {k: include.get(k) for k in VOCABULARY_INCLUDE_FIELDS if include.get(k) is not None}
    if inc:
        out["include"] = inc
    return out


def vocabulary_sha(config: dict) -> str:
    return _sha_text(canonical_json(vocabulary_fields(config)))


def registered_vocabulary(config: dict) -> list[str]:
    return _dedupe(_flatten_agents(config) + _population_terms(config) + _comparator_terms(config))


def load_vocabulary_seal() -> dict:
    path = os.path.join(ROOT, VOCABULARY_SEAL_PATH)
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sealed_vocabulary(slug: str | None, config: dict) -> dict:
    """Returns {sealed: bool, reason, seal_sha, working_sha, terms, exempt_tokens}. Never raises: an unsealed or
    drifted vocabulary simply yields no exemption, and the guard then behaves exactly as it did before the rule."""
    working = vocabulary_sha(config)
    row = ((load_vocabulary_seal().get("slugs") or {}).get(slug) if slug else None) or {}
    seal_sha = row.get("vocabulary_sha256")
    if not slug:
        return {"sealed": False, "reason": "no slug: exemption unavailable", "seal_sha": None,
                "working_sha": working, "terms": [], "exempt_tokens": [], "collision_check": None}
    if not seal_sha:
        return {"sealed": False, "reason": f"{slug} has no entry in {VOCABULARY_SEAL_PATH}", "seal_sha": None,
                "working_sha": working, "terms": [], "exempt_tokens": [], "collision_check": None}
    if seal_sha != working:
        return {"sealed": False, "reason": f"{slug} vocabulary drifted from its seal ({seal_sha[:12]} != {working[:12]})",
                "seal_sha": seal_sha, "working_sha": working, "terms": [], "exempt_tokens": [], "collision_check": None}
    collision = row.get("benchmark_acronym_collision") or {}
    if collision.get("collisions"):
        return {"sealed": False, "reason": f"{slug} sealed vocabulary collides with a benchmark acronym: {collision['collisions']}",
                "seal_sha": seal_sha, "working_sha": working, "terms": [], "exempt_tokens": [], "collision_check": collision}
    terms = registered_vocabulary(config)
    tokens: set[str] = set()
    for term in terms:
        low = str(term).strip().lower()
        tokens.add(low)
        tokens.update(w for w in _WORD_SPLIT_RE.split(low) if w)
    return {"sealed": True, "reason": "vocabulary matches its seal", "seal_sha": seal_sha, "working_sha": working,
            "terms": terms, "exempt_tokens": sorted(tokens), "collision_check": collision}


def assert_discovery_query_allowed(query: str, label: str, exempt_tokens=None) -> str:
    """Allow only structural free-text concept queries from the public classifier. `exempt_tokens` come ONLY from
    sealed_vocabulary(); passing anything else defeats the guard, which is why build_queries is the sole caller."""
    detail = _query_classification(query, exempt_tokens)
    kind = detail["kind"]
    if kind != "FREE_TEXT_KEYWORD":
        offenders = [f for f in (detail.get("features") or []) if not f.startswith("vocabulary_token:")]
        offender = _feature_token((offenders or [kind])[0])
        raise QueryRefusal(f"{label} refused {kind}: {offender}")
    # Keep the public function in the loop; tests assert its external behavior.
    public_kind = classify_query(query, exempt_tokens)
    if public_kind != kind:
        raise QueryRefusal(f"{label} classifier mismatch: {public_kind} != {kind}")
    return kind


def _quote_pubmed(term: str, field: str) -> str:
    text = str(term).strip()
    escaped = text.replace('"', " ")
    if " " in escaped or "-" in escaped or "*" in escaped or "." in escaped or "/" in escaped:
        return f'"{escaped}"[{field}]'
    return f"{escaped}[{field}]"


def _quote_epmc(term: str) -> str:
    text = str(term).strip().replace('"', " ")
    if " " in text or "-" in text or "*" in text or "." in text or "/" in text:
        return f'TITLE_ABS:"{text}"'
    return f"TITLE_ABS:{text}"


def _mesh_heading(term: str) -> str | None:
    payload = http.get_json(
        f"{EUTILS}/esearch.fcgi",
        {
            "db": "mesh",
            "term": term,
            "field": "mesh",
            "retmode": "json",
            "retmax": 1,
            "tool": "meta-harness",
            "email": "meta-harness@example.org",
        },
    )
    result = payload.get("esearchresult") if isinstance(payload, dict) else None
    ids = (result or {}).get("idlist") or []
    if not ids:
        return None
    # The MeSH esearch hit proves a heading exists; using the original term keeps the query
    # deterministic without depending on an esummary display-name shape.
    return str(term).strip()


def _pubmed_block(terms: list[str], mesh_terms: set[str]) -> str:
    pieces = []
    for term in terms:
        items = [_quote_pubmed(term, "tiab")]
        if term in mesh_terms and "*" not in term:
            items.append(_quote_pubmed(term, "MeSH Terms"))
        pieces.append("(" + " OR ".join(items) + ")")
    return "(" + " OR ".join(pieces) + ")" if pieces else ""


def _epmc_block(terms: list[str]) -> str:
    return "(" + " OR ".join(_quote_epmc(t) for t in terms) + ")" if terms else ""


def _ctgov_join(terms: list[str]) -> str:
    return " OR ".join(str(t).strip() for t in terms if str(t).strip())


def build_queries(config: dict, protocol_text: str, *, lookup_mesh: bool = True, slug: str | None = None) -> dict:
    intervention_terms = _dedupe(acq.expand_intervention(_flatten_agents(config)))
    population_terms = _population_terms(config)
    comparator_terms = _comparator_terms(config)
    if not intervention_terms or not population_terms:
        raise QueryRefusal("search_v2 requires both intervention and population terms")
    seal = sealed_vocabulary(slug, config)
    exempt = seal["exempt_tokens"]

    mesh_terms: set[str] = set()
    if lookup_mesh:
        for term in _dedupe(intervention_terms + population_terms):
            if "*" in term:
                continue
            try:
                if _mesh_heading(term):
                    mesh_terms.add(term)
            except Exception:
                # MeSH is a recall enrichment. The source query remains valid if lookup fails.
                continue

    pubmed_query = " AND ".join([
        _pubmed_block(intervention_terms, mesh_terms),
        _pubmed_block(population_terms, mesh_terms),
        "(" + COCHRANE_PUBMED_RCT_FILTER + ")",
    ])
    epmc_query = " AND ".join([
        _epmc_block(intervention_terms),
        _epmc_block(population_terms),
        "(" + COCHRANE_EPMC_RCT_FILTER + ")",
    ])
    ctgov_query = {
        "query.cond": _ctgov_join(population_terms),
        "query.intr": _ctgov_join(_flatten_agents(config)),
    }

    pubmed_kind = assert_discovery_query_allowed(pubmed_query, "PUBMED_CONCEPT_QUERY", exempt)
    epmc_kind = assert_discovery_query_allowed(epmc_query, "EUROPEPMC_CONCEPT_QUERY", exempt)
    ctgov_kind = assert_discovery_query_allowed(
        ctgov_query["query.cond"] + " " + ctgov_query["query.intr"],
        "CTGOV_CONDITION_INTERVENTION",
        exempt,
    )
    used: list[str] = []
    for q in (pubmed_query, epmc_query, ctgov_query["query.cond"] + " " + ctgov_query["query.intr"]):
        for feature in _query_classification(q, exempt).get("features") or []:
            if feature.startswith("vocabulary_token:"):
                used.append(_feature_token(feature))
    return {
        "pubmed": pubmed_query,
        "europepmc": epmc_query,
        "ctgov": ctgov_query,
        "structural_kinds": {
            "pubmed": pubmed_kind,
            "europepmc": epmc_kind,
            "ctgov": ctgov_kind,
        },
        "vocabulary_exemption": {
            "protocol": "docs/evidence/search-v2-guard-2026-09-15/PROTOCOL.md",
            "sealed": seal["sealed"],
            "reason": seal["reason"],
            "seal_sha256": seal["seal_sha"],
            "working_sha256": seal["working_sha"],
            "exempted_tokens_in_queries": sorted(set(used)),
            "benchmark_acronym_collision_check": (seal.get("collision_check") or {}).get("coverage_text") or "no seal: not checked",
        },
        "rct_filter": COCHRANE_RCT_FILTER_NAME,
        "terms": {
            "intervention": intervention_terms,
            "population": population_terms,
            "comparator": comparator_terms,
            "pico_lines": _pico_lines(protocol_text),
        },
    }


def _txt(el: ET.Element | None) -> str:
    return "".join(el.itertext()).strip() if el is not None else ""


def _record_id(record: dict) -> str:
    return str(record.get("id") or record.get("pmid") or record.get("pmcid") or record.get("doi") or record.get("nct"))


def _normalise_pmid(value: object) -> str | None:
    text = str(value or "").strip()
    return text if _PMID_RE.fullmatch(text) else None


def _normalise_nct(value: object) -> str | None:
    text = str(value or "").strip().upper()
    return text if _NCT_RE.fullmatch(text) else None


def _select_nct(abstract: str, databank_ncts: list[str]) -> str:
    abstract_ncts = [n.upper() for n in _NCT_RE.findall(abstract or "")]
    if len(databank_ncts) > 1 and abstract_ncts:
        for nct in abstract_ncts:
            if nct in databank_ncts:
                return nct
    if databank_ncts:
        return databank_ncts[0]
    return abstract_ncts[0] if abstract_ncts else ""


def _pubmed_efetch(pmids: list[str]) -> list[dict]:
    pmids = [p for p in _dedupe(pmids) if _normalise_pmid(p)]
    if not pmids:
        return []
    out: list[dict] = []
    for i in range(0, len(pmids), 200):
        chunk = pmids[i:i + 200]
        xml = http.get_text(
            f"{EUTILS}/efetch.fcgi",
            {
                "db": "pubmed",
                "id": ",".join(chunk),
                "retmode": "xml",
                "tool": "meta-harness",
                "email": "meta-harness@example.org",
            },
        )
        root = ET.fromstring(xml)
        for art in root.findall(".//PubmedArticle"):
            pmid = _txt(art.find(".//PMID"))
            title = _txt(art.find(".//ArticleTitle"))
            abstract = " ".join(
                (a.get("Label", "") + ": " if a.get("Label") else "") + _txt(a)
                for a in art.findall(".//Abstract/AbstractText")
            ).strip()
            pubtypes = [_txt(p) for p in art.findall(".//PublicationType")]
            year = _txt(art.find(".//JournalIssue/PubDate/Year")) or _txt(art.find(".//JournalIssue/PubDate/MedlineDate"))[:4]
            journal = _txt(art.find(".//Journal/ISOAbbreviation"))
            doi = ""
            pmcid = ""
            for eid in art.findall(".//ELocationID"):
                if eid.get("EIdType") == "doi":
                    doi = _txt(eid)
            for aid in art.findall(".//ArticleId"):
                if aid.get("IdType") == "doi" and not doi:
                    doi = _txt(aid)
                if aid.get("IdType") == "pmc":
                    pmcid = _txt(aid)
            databank_ncts: list[str] = []
            for db in art.findall(".//DataBank"):
                if _txt(db.find("DataBankName")).lower().startswith("clinicaltrials"):
                    for acc in db.findall(".//AccessionNumber"):
                        nct = _normalise_nct(_txt(acc))
                        if nct and nct not in databank_ncts:
                            databank_ncts.append(nct)
            nct = _select_nct(abstract, databank_ncts)
            out.append({
                "id": pmid,
                "id_type": "pmid",
                "pmid": pmid,
                "pmcid": pmcid,
                "doi": doi,
                "nct": nct,
                "title": title,
                "abstract": abstract,
                "pubtypes": pubtypes,
                "year": year,
                "journal": journal,
            })
        if i + 200 < len(pmids):
            time.sleep(0.34)
    return out


def _pubmed_search_records(query: str, page_size: int = 1000) -> tuple[list[dict], dict]:
    result = acq.esearch_all(query, page_size=page_size, sleep=0.34)
    if result.get("state") == "RAN_ERROR":
        raise RuntimeError(result.get("error") or "PubMed esearch failed")
    records = _pubmed_efetch(result.get("ids") or [])
    funnel = dict(result.get("funnel") or {})
    funnel["fetched"] = len(result.get("ids") or [])
    funnel["retained"] = len(records)
    return records, {
        "hits": result.get("count"),
        "state": result.get("state"),
        "error": result.get("error"),
        "funnel": funnel,
    }


def _pubmed_nct_records(nct: str) -> tuple[list[dict], dict]:
    query = f'"{nct}"[si]'
    return _pubmed_search_records(query, page_size=200)


def _chunks(values: list[str], size: int) -> list[list[str]]:
    return [values[i:i + size] for i in range(0, len(values), size)]


def _pubmed_nct_batch_records(ncts: list[str]) -> tuple[list[dict], dict]:
    query = " OR ".join(f'"{nct}"[si]' for nct in ncts)
    return _pubmed_search_records(query, page_size=1000)


def _epmc_record(row: dict) -> dict:
    pmid = _normalise_pmid(row.get("pmid") or row.get("id"))
    pmcid = str(row.get("pmcid") or "").strip()
    doi = str(row.get("doi") or "").strip()
    rid = pmid or pmcid or doi or str(row.get("id") or "").strip()
    id_type = "pmid" if pmid else ("pmcid" if pmcid else ("doi" if doi else "epmc"))
    pubtypes = []
    ptl = row.get("pubTypeList") or {}
    if isinstance(ptl, dict):
        raw = ptl.get("pubType") or []
        pubtypes = [str(p) for p in raw] if isinstance(raw, list) else [str(raw)]
    ncts = [n.upper() for n in _NCT_RE.findall(json.dumps(row, ensure_ascii=False))]
    return {
        "id": rid,
        "id_type": id_type,
        "pmid": pmid or "",
        "pmcid": pmcid,
        "doi": doi,
        "nct": ncts[0] if ncts else "",
        "title": str(row.get("title") or ""),
        "abstract": str(row.get("abstractText") or ""),
        "pubtypes": pubtypes,
        "year": str(row.get("pubYear") or row.get("year") or ""),
        "journal": str(row.get("journalTitle") or ""),
    }


def _epmc_search_records(query: str) -> tuple[list[dict], dict]:
    cursor = "*"
    page_size = 1000
    rows: list[dict] = []
    hit_count: int | None = None
    seen_cursor: set[str] = set()
    while True:
        payload = http.get_json(
            EPMC_SEARCH,
            {
                "query": query,
                "format": "json",
                "pageSize": page_size,
                "cursorMark": cursor,
                "resultType": "core",
            },
        )
        if hit_count is None:
            try:
                hit_count = int(payload.get("hitCount"))
            except (TypeError, ValueError):
                hit_count = None
        result_list = (payload.get("resultList") or {}).get("result") or []
        if not isinstance(result_list, list):
            raise ValueError("Europe PMC resultList.result was not a list")
        rows.extend(result_list)
        next_cursor = payload.get("nextCursorMark")
        if not result_list or not next_cursor or next_cursor == cursor or next_cursor in seen_cursor:
            break
        seen_cursor.add(cursor)
        cursor = next_cursor
        time.sleep(0.2)
    records = [_epmc_record(r) for r in rows]
    pmids = [r["pmid"] for r in records if r.get("pmid")]
    if pmids:
        pubmed = {_record_id(r): r for r in _pubmed_efetch(pmids)}
        merged = []
        for rec in records:
            if rec.get("pmid") and rec["pmid"] in pubmed:
                richer = dict(pubmed[rec["pmid"]])
                for key in ("pmcid", "doi", "nct", "abstract"):
                    if not richer.get(key) and rec.get(key):
                        richer[key] = rec[key]
                merged.append(richer)
            else:
                merged.append(rec)
        records = merged
    fetched = len(records)
    return records, {
        "hits": hit_count if hit_count is not None else fetched,
        "state": "RAN_OK" if fetched else "RAN_ZERO",
        "error": None,
        "funnel": {
            "hits": hit_count if hit_count is not None else fetched,
            "fetched": fetched,
            "retained": fetched,
            "cap": {"kind": "none", "n": None, "remainder": None},
        },
    }


def _epmc_nct_records(nct: str) -> tuple[list[dict], dict]:
    return _epmc_search_records(f"NCT:{nct}")


def _epmc_nct_batch_records(ncts: list[str]) -> tuple[list[dict], dict]:
    query = " OR ".join(f"NCT:{nct}" for nct in ncts)
    return _epmc_search_records(query)


def _ctgov_record(study: dict) -> dict:
    ps = study.get("protocolSection") or {}
    idm = ps.get("identificationModule") or {}
    dm = ps.get("designModule") or {}
    design = dm.get("designInfo") or {}
    masking = (design.get("maskingInfo") or {}).get("masking", "")
    arms = ps.get("armsInterventionsModule") or {}
    interventions = [i.get("name", "") for i in arms.get("interventions", []) if isinstance(i, dict)]
    nct = _normalise_nct(idm.get("nctId")) or str(idm.get("nctId") or "")
    return {
        "id": nct,
        "id_type": "nct",
        "pmid": "",
        "pmcid": "",
        "doi": "",
        "nct": nct,
        "title": idm.get("briefTitle") or idm.get("officialTitle") or "",
        "abstract": "",
        "acronym": idm.get("acronym", ""),
        "study_type": dm.get("studyType", ""),
        "allocation": design.get("allocation", ""),
        "masking": masking,
        "conditions": (ps.get("conditionsModule") or {}).get("conditions", []),
        "interventions": interventions,
        "has_results": bool(study.get("hasResults")),
        "year": ((ps.get("statusModule") or {}).get("startDateStruct") or {}).get("date", "")[:4],
        "pubtypes": [],
    }


def _ctgov_search_records(query: dict) -> tuple[list[dict], dict]:
    records: list[dict] = []
    page_token = None
    page_size = 1000
    total: int | None = None
    seen_tokens: set[str] = set()
    while True:
        params = {
            "pageSize": page_size,
            "countTotal": "true",
            "fields": (
                "protocolSection.identificationModule,protocolSection.designModule,"
                "protocolSection.conditionsModule,protocolSection.armsInterventionsModule,"
                "protocolSection.statusModule,hasResults"
            ),
        }
        for key, value in query.items():
            if str(key).startswith("query.") and value:
                params[key] = value
        if page_token:
            params["pageToken"] = page_token
        payload = http.get_json(CTGOV, params)
        if total is None:
            try:
                total = int(payload.get("totalCount"))
            except (TypeError, ValueError):
                total = None
        studies = payload.get("studies") or []
        if not isinstance(studies, list):
            raise ValueError("CT.gov studies was not a list")
        records.extend(_ctgov_record(s) for s in studies if isinstance(s, dict))
        next_token = payload.get("nextPageToken")
        if not next_token:
            break
        if next_token in seen_tokens:
            raise RuntimeError("CT.gov pagination repeated nextPageToken")
        seen_tokens.add(next_token)
        page_token = next_token
        time.sleep(0.2)
    fetched = len(records)
    return records, {
        "hits": total if total is not None else fetched,
        "state": "RAN_OK" if fetched else "RAN_ZERO",
        "error": None,
        "funnel": {
            "hits": total if total is not None else fetched,
            "fetched": fetched,
            "retained": fetched,
            "cap": {"kind": "none", "n": None, "remainder": None},
        },
    }


def _ctgov_nct_record(nct: str) -> tuple[list[dict], dict]:
    payload = http.get_json(
        f"{CTGOV}/{nct}",
        {
            "fields": (
                "protocolSection.identificationModule,protocolSection.designModule,"
                "protocolSection.conditionsModule,protocolSection.armsInterventionsModule,"
                "protocolSection.statusModule,hasResults"
            )
        },
    )
    rec = _ctgov_record(payload)
    return [rec], {
        "hits": 1,
        "state": "RAN_OK",
        "error": None,
        "funnel": {"hits": 1, "fetched": 1, "retained": 1, "cap": {"kind": "none", "n": None, "remainder": None}},
    }


def _ctgov_nct_batch_records(ncts: list[str]) -> tuple[list[dict], dict]:
    return _ctgov_search_records({"query.id": " OR ".join(ncts)})


def _epmc_linked_records(seed: str, kind: str) -> tuple[list[dict], dict]:
    block = "referenceList" if kind == "references" else "citationList"
    item_key = "reference" if kind == "references" else "citation"
    page_size = 1000
    rows: list[dict] = []
    for page in range(1, 10000):
        payload = http.get_json(
            EPMC_ARTICLE.format(pmid=seed, kind=kind),
            {"format": "json", "pageSize": page_size, "page": page},
        )
        items = ((payload.get(block) or {}).get(item_key) or [])
        if not isinstance(items, list):
            raise ValueError(f"Europe PMC {kind} items were not a list")
        rows.extend(items)
        if len(items) < page_size:
            break
        time.sleep(0.2)
    records = []
    pmids = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        pmid = _normalise_pmid(row.get("pmid") or row.get("id"))
        if pmid:
            pmids.append(pmid)
        else:
            records.append(_epmc_record(row))
    if pmids:
        records.extend(_pubmed_efetch(pmids))
    records = list(_dedupe_records(records).values())
    fetched = len(records)
    return records, {
        "hits": len(rows),
        "state": "RAN_OK" if fetched else "RAN_ZERO",
        "error": None,
        "funnel": {"hits": len(rows), "fetched": fetched, "retained": fetched, "cap": {"kind": "none", "n": None, "remainder": None}},
    }


def _pubmed_elink_refs_records(seed: str) -> tuple[list[dict], dict]:
    """Reference list of `seed` via PubMed elink pubmed_pubmed_refs -- a SECOND adapter for the backward-citation and
    comparator-reference-list routes. Added 2026-09-15 because the Europe PMC /references endpoint answered every call
    of run 1 with '503 This API is temporarily unavailable due to maintenance' (238 EPMC_BACKWARD_CITATION + 27
    COMPARATOR_REFERENCE_LIST sources RAN_ERROR), so that route was not measured. Both adapters run; each has its
    own source kind and state in the ledger, so a reader can see which one delivered."""
    payload = http.get_json(
        f"{EUTILS}/elink.fcgi",
        {"dbfrom": "pubmed", "db": "pubmed", "linkname": "pubmed_pubmed_refs", "id": seed, "retmode": "json",
         "tool": "meta-harness", "email": "meta-harness@example.org"},
    )
    time.sleep(0.34)
    linksets = payload.get("linksets") if isinstance(payload, dict) else None
    if not isinstance(linksets, list):
        raise ValueError("PubMed elink payload had no linksets list")
    pmids: list[str] = []
    for ls in (linksets[0] if linksets else {}).get("linksetdbs") or []:
        if ls.get("linkname") == "pubmed_pubmed_refs":
            pmids = [str(x) for x in (ls.get("links") or []) if str(x).isdigit()]
    records = _pubmed_efetch(pmids) if pmids else []
    records = list(_dedupe_records(records).values())
    fetched = len(records)
    return records, {
        "hits": len(pmids),
        "state": "RAN_OK" if fetched else "RAN_ZERO",
        "error": None,
        "funnel": {"hits": len(pmids), "fetched": fetched, "retained": fetched, "cap": {"kind": "none", "n": None, "remainder": None}},
    }


def _source_run(
    ledger: dict,
    kind: str,
    query: str,
    run_utc: str,
    discovery_capable: bool,
    call,
    *,
    source_id: str | None = None,
    adapter: str = "harness.search_v2",
    extra: dict | None = None,
) -> tuple[str, list[dict]]:
    sid = source_id or acq.reserve_source_id(ledger, kind)
    print(f"[search_v2] start {sid} {kind}", flush=True)
    recorder = getattr(http, "RECORDER", None)
    scope = recorder.source(sid, adapter) if recorder else nullcontext()
    try:
        with scope:
            records, meta = call()
        state = meta.get("state") or ("RAN_OK" if records else "RAN_ZERO")
        error = meta.get("error")
        funnel = meta.get("funnel") or {
            "hits": len(records),
            "fetched": len(records),
            "retained": len(records),
            "cap": {"kind": "none", "n": None, "remainder": None},
        }
    except Exception as exc:  # noqa: BLE001 - source state must be explicit.
        records = []
        state = "RAN_ERROR"
        error = str(exc)
        funnel = {"hits": None, "fetched": 0, "retained": 0, "cap": {"kind": "none", "n": None, "remainder": None}}
    ids = [_record_id(r) for r in records if _record_id(r)]
    acq.add_source(ledger, kind, query, run_utc, state, error, funnel, ids, discovery_capable, source_id=sid)
    if extra:
        ledger["sources"][-1].update(extra)
    print(f"[search_v2] done {sid} {kind} state={state} records={len(ids)}", flush=True)
    return sid, records


def _dedupe_records(records: list[dict]) -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for rec in records:
        rid = _record_id(rec)
        if not rid:
            continue
        if rid not in merged:
            merged[rid] = dict(rec)
            continue
        cur = merged[rid]
        for key, value in rec.items():
            if key == "found_by":
                continue
            if not cur.get(key) and value:
                cur[key] = value
    return merged


def _attach(ledger: dict, records_by_id: dict[str, dict], source_id: str, records: list[dict]) -> None:
    ids = []
    for rec in records:
        rid = _record_id(rec)
        if not rid:
            continue
        ids.append(rid)
        if rid not in records_by_id:
            records_by_id[rid] = dict(rec)
        else:
            for key, value in rec.items():
                if key != "found_by" and not records_by_id[rid].get(key) and value:
                    records_by_id[rid][key] = value
    acq.attach_records(ledger, source_id, ids)


def _sync_found_by(ledger: dict, records_by_id: dict[str, dict]) -> list[dict]:
    out = []
    for rid in sorted(records_by_id):
        rec = dict(records_by_id[rid])
        rec["found_by"] = list((ledger.get("records") or {}).get(rid, {}).get("found_by") or [])
        out.append(rec)
    return out


def _included_seed_pmids(slug: str, config: dict) -> list[str]:
    path = os.path.join(ROOT, "cache", slug, "records.json")
    if not os.path.exists(path):
        return []
    records = _load_json(os.path.join("cache", slug, "records.json"))
    merged = _dedup(records, config.get("pivotal_trials"))
    decisions = screen.run(merged, config).get("decisions") or []
    by_id = {str(r.get("id")): r for r in merged}
    seeds = []
    for decision in decisions:
        if decision.get("decision") != "include":
            continue
        rec = by_id.get(str(decision.get("id"))) or {}
        pmid = _normalise_pmid(rec.get("pmid") or rec.get("id"))
        if pmid:
            seeds.append(pmid)
    return _dedupe(seeds)


def _candidate_screen(records: list[dict], config: dict) -> dict:
    return screen.run(records, config)


def _screen_summary(records: list[dict], decisions: dict, ledger: dict) -> dict:
    source_by_id = {s["source_id"]: s for s in ledger.get("sources", [])}
    by_route: dict[str, dict[str, int]] = {}
    by_rule: dict[str, dict[str, int]] = {}
    ledger_records = ledger.get("records") or {}
    for decision in decisions.get("decisions") or []:
        rid = str(decision.get("id"))
        found_by = (ledger_records.get(rid) or {}).get("found_by") or []
        routes = sorted({source_by_id.get(sid, {}).get("kind", sid) for sid in found_by}) or ["UNRECORDED"]
        key = f"{decision.get('decision')}:{decision.get('rule_id')}"
        for route in routes:
            by_route.setdefault(route, {})
            by_route[route][key] = by_route[route].get(key, 0) + 1
        rule = decision.get("rule_id") or "UNKNOWN"
        by_rule.setdefault(rule, {"include": 0, "exclude": 0})
        by_rule[rule][decision.get("decision") or "exclude"] = by_rule[rule].get(decision.get("decision") or "exclude", 0) + 1
    return {
        "records_after_dedup": len(records),
        "by_route": by_route,
        "by_rule": by_rule,
    }


def split_of(slug: str) -> str:
    """DEVELOPMENT / MEASUREMENT from the sealed split registry (which names sets, not targets); UNSPLIT if the slug
    is not in it. Lane S3 hard-coded DEVELOPMENT into every snapshot, measurement ones included."""
    path = os.path.join(ROOT, "registry", "search_benchmark_split.json")
    if not os.path.exists(path):
        return "UNSPLIT"
    with open(path, encoding="utf-8") as f:
        row = ((json.load(f).get("assignments") or {}).get(slug)) or {}
    return str(row.get("set") or "UNSPLIT")


def _snapshot_dir(slug: str, run_date: str, snapshot_name: str | None = None) -> str:
    """A snapshot generation is named `<run_date><label>-search_v2`; a labelled re-run (e.g. 2026-09-15r2) sits
    BESIDE the first generation, never over it. `_latest_snapshot` sorts lexically, so 'r2' > '-'."""
    return os.path.join(ROOT, "cache", slug, "snapshots", snapshot_name or f"{run_date}-{SNAPSHOT_SUFFIX}")


def _write_snapshot(slug: str, records_dict: dict, ledger: dict, recorder: acq.RawRecorder, run_date: str,
                    snapshot_name: str | None = None) -> str:
    snapshot_dir = _snapshot_dir(slug, run_date, snapshot_name)
    os.makedirs(snapshot_dir, exist_ok=True)
    raw_calls, raw_index_sha = recorder.write_snapshot(snapshot_dir)
    ledger.setdefault("snapshot", {})["raw_calls"] = raw_calls
    if raw_index_sha:
        ledger["snapshot"]["raw_index_sha256"] = raw_index_sha
    path = os.path.join(snapshot_dir, "records.json")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(records_dict, ensure_ascii=False, indent=2, sort_keys=True))
    with open(os.path.join(snapshot_dir, acq.LEDGER_FILENAME), "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True))
    violations = acq.validate(ledger, records_dict.get("records", []), snapshot_dir=snapshot_dir)
    if violations:
        raise ValueError("invalid search_v2 snapshot: " + "; ".join(violations))
    return snapshot_dir


def replay_snapshot(slug: str, snapshot_dir: str | None = None) -> bytes:
    path = snapshot_dir or _latest_snapshot(slug)
    with open(os.path.join(path, "records.json"), "rb") as f:
        return f.read()


def load_snapshot(slug: str, run_date: str) -> dict | None:
    snapshot_dir = _snapshot_dir(slug, run_date)
    records_path = os.path.join(snapshot_dir, "records.json")
    ledger_path = os.path.join(snapshot_dir, acq.LEDGER_FILENAME)
    if not (os.path.exists(records_path) and os.path.exists(ledger_path)):
        return None
    with open(records_path, encoding="utf-8") as f:
        records = json.load(f)
    with open(ledger_path, encoding="utf-8") as f:
        ledger = json.load(f)
    return {"records": records, "ledger": ledger, "snapshot_dir": snapshot_dir}


def _latest_snapshot(slug: str) -> str:
    root = os.path.join(ROOT, "cache", slug, "snapshots")
    matches = sorted(
        os.path.join(root, name)
        for name in os.listdir(root)
        if name.endswith("-" + SNAPSHOT_SUFFIX) and os.path.isdir(os.path.join(root, name))
    )
    if not matches:
        raise FileNotFoundError(f"no search_v2 snapshot for {slug}")
    return matches[-1]


def pin(slug: str, snapshot_dir: str) -> None:
    dst = os.path.join(ROOT, "cache", slug)
    os.makedirs(dst, exist_ok=True)
    shutil.copyfile(os.path.join(snapshot_dir, "records.json"), os.path.join(dst, "records.json"))
    shutil.copyfile(os.path.join(snapshot_dir, acq.LEDGER_FILENAME), os.path.join(dst, acq.LEDGER_FILENAME))


def refresh_topic(slug: str, run_date: str | None = None, snapshot_name: str | None = None) -> dict:
    run_date = run_date or _today_utc()
    snapshot_name = snapshot_name or f"{run_date}-{SNAPSHOT_SUFFIX}"
    if not snapshot_name.endswith("-" + SNAPSHOT_SUFFIX):
        raise ValueError(f"snapshot_name must end with -{SNAPSHOT_SUFFIX}: {snapshot_name}")
    run_utc = _utc_now_seconds()
    print(f"[search_v2] topic {slug}: refresh start", flush=True)
    config = _load_json(os.path.join("topics", slug + ".json"))
    protocol_text = _read_text(os.path.join("protocols", slug + ".md"))
    split = split_of(slug)
    ledger = acq.new_ledger(slug)
    ledger["search_v2"] = {"version": SEARCH_V2_VERSION, "split": split}
    recorder = acq.RawRecorder()
    previous_recorder = http.RECORDER
    http.RECORDER = recorder
    records_by_id: dict[str, dict] = {}
    try:
        pubmed_sid = acq.reserve_source_id(ledger, "PUBMED_CONCEPT_QUERY")
        print(f"[search_v2] topic {slug}: build queries", flush=True)
        with recorder.source(pubmed_sid, "harness.search_v2.build_queries"):
            queries = build_queries(config, protocol_text, lookup_mesh=True, slug=slug)

        sid, records = _source_run(
            ledger,
            "PUBMED_CONCEPT_QUERY",
            queries["pubmed"],
            run_date,
            True,
            lambda: _pubmed_search_records(queries["pubmed"]),
            source_id=pubmed_sid,
            adapter="harness.search_v2._pubmed_search_records",
            extra={"structural_kind": "CONCEPT", "rct_filter": COCHRANE_RCT_FILTER_NAME},
        )
        _attach(ledger, records_by_id, sid, records)

        sid, records = _source_run(
            ledger,
            "EUROPEPMC_CONCEPT_QUERY",
            queries["europepmc"],
            run_date,
            True,
            lambda: _epmc_search_records(queries["europepmc"]),
            adapter="harness.search_v2._epmc_search_records",
            extra={"structural_kind": "CONCEPT", "rct_filter": COCHRANE_RCT_FILTER_NAME},
        )
        _attach(ledger, records_by_id, sid, records)

        sid, records = _source_run(
            ledger,
            "CTGOV_CONDITION_INTERVENTION",
            json.dumps(queries["ctgov"], sort_keys=True),
            run_date,
            True,
            lambda: _ctgov_search_records(queries["ctgov"]),
            adapter="harness.search_v2._ctgov_search_records",
            extra={"structural_kind": "CONCEPT"},
        )
        _attach(ledger, records_by_id, sid, records)

        # CT.gov -> literature identity links.
        ctgov_ncts = sorted({r.get("nct") for r in records_by_id.values() if r.get("id_type") == "nct" and r.get("nct")})
        for nct_chunk in _chunks(ctgov_ncts, 50):
            sid, records = _source_run(
                ledger,
                "PUBMED_NCT_LINK",
                " OR ".join(f'"{nct}"[si]' for nct in nct_chunk),
                run_date,
                True,
                lambda nct_chunk=nct_chunk: _pubmed_nct_batch_records(nct_chunk),
                adapter="harness.search_v2._pubmed_nct_batch_records",
                extra={"seed": nct_chunk, "structural_kind": "IDENTITY_LINK"},
            )
            _attach(ledger, records_by_id, sid, records)
        for nct_chunk in _chunks(ctgov_ncts, 50):
            sid, records = _source_run(
                ledger,
                "EPMC_NCT_LINK",
                " OR ".join(f"NCT:{nct}" for nct in nct_chunk),
                run_date,
                True,
                lambda nct_chunk=nct_chunk: _epmc_nct_batch_records(nct_chunk),
                adapter="harness.search_v2._epmc_nct_batch_records",
                extra={"seed": nct_chunk, "structural_kind": "IDENTITY_LINK"},
            )
            _attach(ledger, records_by_id, sid, records)

        # Literature -> registry identity links.
        lit_ncts = sorted({
            r.get("nct") for r in records_by_id.values()
            if r.get("id_type") != "nct" and r.get("nct") and r.get("nct") not in set(ctgov_ncts)
        })
        for nct_chunk in _chunks(lit_ncts, 50):
            sid, records = _source_run(
                ledger,
                "CTGOV_NCT_LINK",
                " OR ".join(nct_chunk),
                run_date,
                True,
                lambda nct_chunk=nct_chunk: _ctgov_nct_batch_records(nct_chunk),
                adapter="harness.search_v2._ctgov_nct_batch_records",
                extra={"seed": nct_chunk, "structural_kind": "IDENTITY_LINK"},
            )
            _attach(ledger, records_by_id, sid, records)

        # Candidate citation routes from our own included records. Backward citation runs through BOTH adapters
        # (Europe PMC /references and PubMed elink pubmed_pubmed_refs), each with its own source kind and state.
        for seed in _included_seed_pmids(slug, config):
            for endpoint, kind in (("references", "EPMC_BACKWARD_CITATION"), ("citations", "EPMC_FORWARD_CITATION")):
                sid, records = _source_run(
                    ledger,
                    kind,
                    f"{seed} {endpoint}",
                    run_date,
                    True,
                    lambda seed=seed, endpoint=endpoint: _epmc_linked_records(seed, endpoint),
                    adapter="harness.search_v2._epmc_linked_records",
                    extra={"seed": seed, "structural_kind": "CANDIDATE_ROUTE"},
                )
                _attach(ledger, records_by_id, sid, records)
            sid, records = _source_run(
                ledger,
                "PUBMED_ELINK_BACKWARD_CITATION",
                f"{seed} pubmed_pubmed_refs",
                run_date,
                True,
                lambda seed=seed: _pubmed_elink_refs_records(seed),
                adapter="harness.search_v2._pubmed_elink_refs_records",
                extra={"seed": seed, "structural_kind": "CANDIDATE_ROUTE"},
            )
            _attach(ledger, records_by_id, sid, records)

        comparator = str(config.get("comparator_pmid") or "").strip()
        if comparator:
            sid, records = _source_run(
                ledger,
                "COMPARATOR_REFERENCE_LIST",
                comparator,
                run_date,
                True,
                lambda comparator=comparator: _epmc_linked_records(comparator, "references"),
                adapter="harness.search_v2._epmc_linked_records",
                extra={"seed": comparator, "structural_kind": "CANDIDATE_ROUTE"},
            )
            _attach(ledger, records_by_id, sid, records)
            sid, records = _source_run(
                ledger,
                "COMPARATOR_REFERENCE_LIST_PUBMED",
                f"{comparator} pubmed_pubmed_refs",
                run_date,
                True,
                lambda comparator=comparator: _pubmed_elink_refs_records(comparator),
                adapter="harness.search_v2._pubmed_elink_refs_records",
                extra={"seed": comparator, "structural_kind": "CANDIDATE_ROUTE"},
            )
            _attach(ledger, records_by_id, sid, records)
    finally:
        http.RECORDER = previous_recorder

    records = _sync_found_by(ledger, records_by_id)
    decisions = _candidate_screen(records, config)
    screen_summary = _screen_summary(records, decisions, ledger)
    records_dict = {
        "slug": slug,
        "fetched_utc": run_utc,
        "search_v2": {
            "version": SEARCH_V2_VERSION,
            "mode": "REFRESH",
            "snapshot_date": run_date,
            "snapshot_name": snapshot_name,
            "split": split,
            "engine_sha": _engine_sha(),
            "base_commit": _base_commit(),
            "queries": queries,
            "screen_summary": screen_summary,
        },
        "records": records,
        "screening": decisions,
    }
    acq.finalize(ledger, records, run_date, "REFRESH")
    ledger["snapshot"]["engine_sha"] = _engine_sha()
    ledger["snapshot"]["search_v2_version"] = SEARCH_V2_VERSION
    ledger["snapshot"]["mode_detail"] = "REFRESH"
    ledger["snapshot"]["snapshot_name"] = snapshot_name
    snapshot_dir = _write_snapshot(slug, records_dict, ledger, recorder, run_date, snapshot_name)
    records_dict["search_v2"]["snapshot_dir"] = os.path.relpath(snapshot_dir, ROOT).replace("\\", "/")
    print(f"[search_v2] topic {slug}: wrote {snapshot_dir}", flush=True)
    return {"records": records_dict, "ledger": ledger, "snapshot_dir": snapshot_dir}


def _candidate_id(record: dict) -> tuple[str, str]:
    if record.get("pmid"):
        return str(record["pmid"]), "pmid"
    if record.get("nct"):
        return str(record["nct"]), "nct"
    if record.get("doi"):
        return str(record["doi"]), "doi"
    if record.get("pmcid"):
        return str(record["pmcid"]), "pmcid"
    return _record_id(record), str(record.get("id_type") or "unknown")


def _candidate_payload(run_rows: dict[str, dict], run_date: str) -> dict:
    topics = {}
    for slug, row in run_rows.items():
        records = row["records"]["records"]
        out = []
        for rec in records:
            cid, id_type = _candidate_id(rec)
            out.append({
                "id": cid,
                "id_type": id_type,
                "pmid": rec.get("pmid") or (cid if id_type == "pmid" else ""),
                "nct": rec.get("nct") or (cid if id_type == "nct" else ""),
                "doi": rec.get("doi") or "",
                "title": rec.get("title") or "",
                "found_by": rec.get("found_by") or [],
            })
        topics[slug] = out
    return {
        "engine_sha": _engine_sha(),
        "run_utc": _utc_now_seconds(),
        "split": "DEVELOPMENT",
        "snapshot_date": run_date,
        "topics": topics,
    }


def _historical_probiotics_counts() -> dict:
    cfg = _load_json(os.path.join("topics", "probiotics-aad-prevention.json"))
    return {"historical_hand_written_queries": len(cfg.get("pubmed_queries") or [])}


def _source_lines(slug: str, ledger: dict) -> list[str]:
    lines = [f"## {slug}"]
    for source in ledger.get("sources") or []:
        funnel = source.get("funnel") or {}
        cap = funnel.get("cap") or {}
        lines.append(
            f"- {source.get('source_id')} {source.get('kind')} state={source.get('state')} "
            f"hits={funnel.get('hits')} fetched={funnel.get('fetched')} retained={funnel.get('retained')} "
            f"cap={cap.get('kind')} remainder={cap.get('remainder')} query={source.get('query')}"
        )
    return lines


def _crosslink_lines(slug: str, row: dict) -> list[str]:
    ledger = row["ledger"]
    records = row["records"]["records"]
    by_kind: dict[str, int] = {}
    for source in ledger.get("sources") or []:
        by_kind[source.get("kind")] = by_kind.get(source.get("kind"), 0) + len(source.get("record_ids") or [])
    lines = [f"## {slug}", f"records_after_dedup={len(records)}"]
    for kind in sorted(by_kind):
        if kind in {
            "PUBMED_NCT_LINK",
            "EPMC_NCT_LINK",
            "CTGOV_NCT_LINK",
            "EPMC_BACKWARD_CITATION",
            "EPMC_FORWARD_CITATION",
            "COMPARATOR_REFERENCE_LIST",
        }:
            lines.append(f"- {kind}: records={by_kind[kind]}")
    screen_summary = row["records"]["search_v2"]["screen_summary"]
    lines.append("screen_by_route=" + json.dumps(screen_summary.get("by_route", {}), sort_keys=True))
    return lines


def _write_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def write_development_evidence(run_rows: dict[str, dict], run_date: str, replay: dict[str, str]) -> None:
    evidence_dir = os.path.join(ROOT, "docs", "evidence", f"search-v2-{run_date}")
    os.makedirs(evidence_dir, exist_ok=True)
    q_lines = [
        "SEARCH V2 BUILDER QUERIES",
        f"date={run_date}",
        "structural kinds permitted for emitted discovery queries: FREE_TEXT_KEYWORD / CONCEPT",
        "refusal plants: DOI, PMID, NCT, [Title], and trial-acronym tokens are refused with the offending token.",
    ]
    refusal_plants = [
        "10.1056/NEJMoa000000",
        "40159390",
        "NCT01234567",
        "Dapagliflozin[Title] randomized placebo",
        "FAIR-HF2 JAMA 2025 randomized trial",
    ]
    for plant in refusal_plants:
        try:
            assert_discovery_query_allowed(plant, "REFUSAL_PLANT")
            q_lines.append(f"PLANT_UNEXPECTED_PASS {plant}")
        except QueryRefusal as exc:
            q_lines.append(f"PLANT_REFUSED {exc}")
    for slug, row in run_rows.items():
        queries = row["records"]["search_v2"]["queries"]
        q_lines.append(f"## {slug}")
        q_lines.append(f"PUBMED_CONCEPT_QUERY kind=CONCEPT query={queries['pubmed']}")
        q_lines.append(f"EUROPEPMC_CONCEPT_QUERY kind=CONCEPT query={queries['europepmc']}")
        q_lines.append("CTGOV_CONDITION_INTERVENTION kind=CONCEPT query=" + json.dumps(queries["ctgov"], sort_keys=True))
        q_lines.append("PICO_LINES=" + json.dumps(queries["terms"].get("pico_lines", []), ensure_ascii=False))
    _write_text(os.path.join(evidence_dir, "01-builder-queries.txt"), "\n".join(q_lines) + "\n")

    funnel_lines = ["SEARCH V2 PER-SOURCE FUNNELS", f"date={run_date}"]
    for slug, row in run_rows.items():
        funnel_lines.extend(_source_lines(slug, row["ledger"]))
    _write_text(os.path.join(evidence_dir, "02-source-funnels.txt"), "\n".join(funnel_lines) + "\n")

    cross_lines = ["SEARCH V2 CROSS-LINK AND CITATION COUNTS", f"date={run_date}"]
    for slug, row in run_rows.items():
        cross_lines.extend(_crosslink_lines(slug, row))
    probiotics = run_rows.get("probiotics-aad-prevention")
    if probiotics:
        cross_lines.append("## probiotics historical hand-written comparison")
        cross_lines.append(json.dumps({
            **_historical_probiotics_counts(),
            "search_v2_retrieved_set_size": len(probiotics["records"]["records"]),
            "note": "Comparison uses the topic's committed historical query ledger/config, not the diagnostic trial list.",
        }, sort_keys=True))
    _write_text(os.path.join(evidence_dir, "03-crosslink-citation-counts.txt"), "\n".join(cross_lines) + "\n")

    replay_lines = ["SEARCH V2 REPLAY PROOF", f"date={run_date}"]
    for slug in sorted(replay):
        replay_lines.append(f"{slug}: {replay[slug]}")
    _write_text(os.path.join(evidence_dir, "04-replay-proof.txt"), "\n".join(replay_lines) + "\n")
    _write_text(
        os.path.join(evidence_dir, "README.md"),
        "\n".join([
            "# Search v2 evidence",
            "",
            "These outputs were generated only on the 11 DEVELOPMENT topics named by the lane prompt.",
            "No held-out, target, or recall number is claimed here.",
            "Snapshots are unpinned; served review pages and pools were not moved by this lane.",
            "",
        ]),
    )


def run_development(run_date: str | None = None) -> dict:
    run_date = run_date or _today_utc()
    rows: dict[str, dict] = {}
    replay: dict[str, str] = {}
    for slug in DEVELOPMENT_TOPICS:
        print(f"[search_v2] development topic {slug}", flush=True)
        row = load_snapshot(slug, run_date)
        if row:
            print(f"[search_v2] topic {slug}: reusing {row['snapshot_dir']}", flush=True)
        else:
            row = refresh_topic(slug, run_date)
        rows[slug] = row
        snap_records = os.path.join(row["snapshot_dir"], "records.json")
        with open(snap_records, "rb") as f:
            original = f.read()
        replayed = replay_snapshot(slug, row["snapshot_dir"])
        replay[slug] = (
            "bit-identical records.json "
            f"sha256={_sha_bytes(original)}"
            if original == replayed else
            f"MISMATCH original={_sha_bytes(original)} replay={_sha_bytes(replayed)}"
        )
    payload = _candidate_payload(rows, run_date)
    out_dir = os.path.join(ROOT, "outputs", "search_v2")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"candidates-{run_date}.json"), "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    write_development_evidence(rows, run_date, replay)
    return {"rows": rows, "candidates": payload, "replay": replay}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run or replay search_v2 acquisition.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    one = sub.add_parser("refresh-topic")
    one.add_argument("slug")
    one.add_argument("--date", default=_today_utc())
    dev = sub.add_parser("run-development")
    dev.add_argument("--date", default=_today_utc())
    rep = sub.add_parser("replay")
    rep.add_argument("slug")
    rep.add_argument("--snapshot-dir")
    args = parser.parse_args(argv)
    if args.cmd == "refresh-topic":
        row = refresh_topic(args.slug, args.date)
        print(row["snapshot_dir"])
        return 0
    if args.cmd == "run-development":
        run_development(args.date)
        print(f"wrote outputs/search_v2/candidates-{args.date}.json")
        return 0
    if args.cmd == "replay":
        data = replay_snapshot(args.slug, args.snapshot_dir)
        sys.stdout.buffer.write(data)
        return 0
    raise AssertionError(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
