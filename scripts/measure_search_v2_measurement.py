"""Run and report the sealed search_v2 measurement lane.

This wrapper deliberately leaves harness/search_v2.py, topic configs, query
text, pinned caches, docs/reviews, and the benchmark untouched. It calls the
frozen engine for the 21 MEASUREMENT topics, writes a scorer-compatible
candidate file, then builds the lane evidence/report around that output.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import traceback
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import gitblob, http, search_v2  # noqa: E402


RUN_DATE = "2026-09-15"
FIX_ID = "MEASURE-search-v2-recall-2026-09-15"
EVIDENCE_DIR = ROOT / "docs" / "evidence" / "search-v2-measurement-2026-09-15"
CANDIDATE_PATH = ROOT / "outputs" / "search_v2" / f"candidates-{RUN_DATE}-measurement.json"
REPORT_PATH = ROOT / "LANE-S3-REPORT.md"
BENCHMARK_PATH = ROOT / "registry" / "search_benchmark.json"
SPLIT_PATH = ROOT / "registry" / "search_benchmark_split.json"
FIXES_PATH = ROOT / "registry" / "fixes.json"
CAPTIONS_PATH = ROOT / "docs" / "evidence" / "CAPTIONS.json"
REGRESSION_RECALL_PATH = ROOT / "docs" / "search_recall_regression_corpus.json"

MEASUREMENT_TOPICS = [
    "colchicine-postop-af",
    "colchicine-secondary-cv-prevention",
    "corticosteroids-cap-mortality",
    "dapagliflozin-hfpef-hosp",
    "denosumab-vertebral-fracture",
    "empagliflozin-hfpef-hosp",
    "esketamine-trd-madrs",
    "finerenone-ckd-t2d-renal",
    "iv-iron-hfref-hosp",
    "noac-vs-warfarin-af-stroke",
    "omega3-cardiovascular-events",
    "pcsk9-mace",
    "sacubitril-valsartan-hfref",
    "semaglutide-obesity-weight",
    "sglt2-hfref-hosp-cvdeath",
    "sglt2-primary-prevention-hf",
    "spironolactone-hfref-mortality",
    "statins-primary-prevention-elderly",
    "ticagrelor-vs-clopidogrel-acs",
    "tocilizumab-covid19-mortality",
    "tranexamic-acid-pph",
]

AUDIT_ORIGINS = {
    "known_eligible_missing",
    "never_considered",
    "probiotics_goodman_42",
    "comparator_only_theirs",
}

ROUTE_LABELS = {
    "PUBMED_CONCEPT_QUERY": "concept query PubMed",
    "EUROPEPMC_CONCEPT_QUERY": "concept query Europe PMC",
    "CTGOV_CONDITION_INTERVENTION": "concept query CT.gov",
    "PUBMED_NCT_LINK": "CT.gov cross-link",
    "EPMC_NCT_LINK": "CT.gov cross-link",
    "CTGOV_NCT_LINK": "CT.gov cross-link",
    "EPMC_BACKWARD_CITATION": "backward citation",
    "EPMC_FORWARD_CITATION": "forward citation",
    "COMPARATOR_REFERENCE_LIST": "comparator reference list",
    "PUBMED_ELINK_BACKWARD_CITATION": "backward citation (PubMed elink)",
    "COMPARATOR_REFERENCE_LIST_PUBMED": "comparator reference list (PubMed elink)",
}

PMID_RE = re.compile(r"^(?:PMID[:\s]*)?(\d{1,9})$", re.I)
NCT_RE = re.compile(r"\b(NCT\d{8})\b", re.I)
DOI_RE = re.compile(r"\b(10\.\S+/\S+)\b", re.I)


def _utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _utc_minute() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%MZ")


def _posix(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def _rel(path: str | Path) -> str:
    return _posix(Path(path).resolve().relative_to(ROOT))


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=1, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def _git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return proc.stdout.strip()


def _blob(relpath: str) -> str:
    blob = gitblob.blob_sha(ROOT, relpath)
    if not blob:
        raise RuntimeError(f"cannot hash dependency: {relpath}")
    return blob


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _pmid(value: Any) -> str | None:
    raw = str(value or "").strip()
    match = PMID_RE.match(raw)
    return match.group(1) if match else None


def _nct(value: Any) -> str | None:
    match = NCT_RE.search(str(value or ""))
    return match.group(1).upper() if match else None


def _doi(value: Any) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    match = DOI_RE.search(raw)
    return match.group(1).rstrip(".,;").lower() if match else None


def _norm_title(text: Any) -> str:
    text = str(text or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _fold(text: Any) -> str:
    text = str(text or "").lower()
    text = re.sub(r"[^a-z0-9*]+", " ", text)
    return " ".join(text.split())


def _positive_key(row: dict[str, Any]) -> tuple[str, str]:
    pmid = _pmid(row.get("pmid"))
    if pmid:
        return "pmid", pmid
    nct = _nct(row.get("nct"))
    if nct:
        return "nct", nct
    doi = _doi(row.get("doi"))
    if doi:
        return "doi", doi
    return "title", _norm_title(row.get("trial"))


def _candidate_keys(item: Any) -> tuple[list[tuple[str, str]], str]:
    keys: list[tuple[str, str]] = []
    label = ""
    if isinstance(item, dict):
        label = str(item.get("trial") or item.get("title") or item.get("name") or item.get("id") or "")
        for field in ("pmid", "id"):
            pmid = _pmid(item.get(field))
            if pmid:
                keys.append(("pmid", pmid))
        for field in ("nct", "id"):
            nct = _nct(item.get(field))
            if nct:
                keys.append(("nct", nct))
        for field in ("doi", "id"):
            doi = _doi(item.get(field))
            if doi:
                keys.append(("doi", doi))
        title = _norm_title(item.get("trial") or item.get("title") or item.get("name"))
        if title:
            keys.append(("title", title))
    else:
        label = str(item)
        pmid = _pmid(label)
        nct = _nct(label)
        doi = _doi(label)
        if pmid:
            keys.append(("pmid", pmid))
        if nct:
            keys.append(("nct", nct))
        if doi:
            keys.append(("doi", doi))
        title = _norm_title(label)
        if title and not keys:
            keys.append(("title", title))
    out: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for key in keys:
        if key[1] and key not in seen:
            seen.add(key)
            out.append(key)
    return out, label


def _id_label(row: dict[str, Any]) -> str:
    kind, value = _positive_key(row)
    return f"{kind}:{value}" if value else "title:<blank>"


def _origins(row: dict[str, Any]) -> set[str]:
    return {part for part in str(row.get("origin") or "").split(";") if part}


def _route_labels_from_ids(found_by: list[str], source_map: dict[str, dict[str, Any]]) -> list[str]:
    labels: list[str] = []
    for source_id in found_by:
        kind = (source_map.get(source_id) or {}).get("kind") or source_id
        label = ROUTE_LABELS.get(str(kind), str(kind))
        if label not in labels:
            labels.append(label)
    return labels or ["unrouted"]


def _candidate_id(record: dict[str, Any]) -> tuple[str, str]:
    if record.get("pmid"):
        return str(record["pmid"]), "pmid"
    if record.get("nct"):
        return str(record["nct"]), "nct"
    if record.get("doi"):
        return str(record["doi"]), "doi"
    if record.get("pmcid"):
        return str(record["pmcid"]), "pmcid"
    return str(record.get("id") or ""), str(record.get("id_type") or "unknown")


def _validate_measurement_split() -> None:
    split = _load_json(SPLIT_PATH)
    assignments = split.get("assignments") or {}
    observed = [
        slug
        for slug, row in assignments.items()
        if row.get("set") == "MEASUREMENT"
    ]
    if set(observed) != set(MEASUREMENT_TOPICS):
        raise RuntimeError(
            "measurement topic list mismatch: "
            f"split={sorted(observed)} prompt={sorted(MEASUREMENT_TOPICS)}"
        )


def _topic_candidates(row: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records_dict = row["records"]
    ledger = row["ledger"]
    source_map = {s.get("source_id"): s for s in (ledger.get("sources") or [])}
    candidates: list[dict[str, Any]] = []
    for rec in records_dict.get("records") or []:
        cid, id_type = _candidate_id(rec)
        found_by = [str(x) for x in (rec.get("found_by") or [])]
        labels = _route_labels_from_ids(found_by, source_map)
        candidates.append({
            "id": cid,
            "id_type": id_type,
            "pmid": rec.get("pmid") or (cid if id_type == "pmid" else ""),
            "nct": rec.get("nct") or (cid if id_type == "nct" else ""),
            "doi": rec.get("doi") or "",
            "title": rec.get("title") or "",
            "found_by": found_by,
            "found_by_routes": labels,
            "route": " | ".join(labels),
        })
    source_rows = []
    for src in ledger.get("sources") or []:
        source_rows.append({
            "source_id": src.get("source_id"),
            "kind": src.get("kind"),
            "state": src.get("state"),
            "error": src.get("error"),
            "funnel": src.get("funnel"),
            "query": src.get("query"),
            "record_count": len(src.get("record_ids") or []),
        })
    state = "RAN_OK"
    if any(src.get("state") == "RAN_ERROR" for src in source_rows):
        state = "RAN_OK_WITH_SOURCE_ERRORS"
    meta = {
        "state": state,
        "snapshot_dir": _rel(row["snapshot_dir"]),
        "candidate_count": len(candidates),
        "sources": source_rows,
        "screen_summary": (records_dict.get("search_v2") or {}).get("screen_summary"),
    }
    return candidates, meta


def refresh_measurement() -> int:
    _validate_measurement_split()
    base_commit = _git("rev-parse", "HEAD")
    engine_sha = _git("hash-object", "--", "harness/search_v2.py")
    candidates: dict[str, list[dict[str, Any]]] = {}
    topics: dict[str, dict[str, Any]] = {}
    for slug in MEASUREMENT_TOPICS:
        print(f"[measurement] refresh {slug}", flush=True)
        try:
            row = search_v2.refresh_topic(slug, RUN_DATE)
            items, meta = _topic_candidates(row)
            candidates[slug] = items
            topics[slug] = meta
        except Exception as exc:  # noqa: BLE001 - lane rule: record row, do not patch/rerun.
            candidates[slug] = []
            topics[slug] = {
                "state": "RAN_ERROR",
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "candidate_count": 0,
                "sources": [],
            }
            print(f"[measurement] RAN_ERROR {slug}: {exc}", flush=True)
        CANDIDATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _write_json(
            CANDIDATE_PATH,
            {
                "_doc": (
                    "search_v2 measurement candidate set. Built by calling the frozen "
                    "harness/search_v2.py refresh_topic entry point for the sealed "
                    "MEASUREMENT topics only. Development topics are excluded."
                ),
                "engine_sha": engine_sha,
                "base_commit": base_commit,
                "run_utc": _utc_now(),
                "split": "MEASUREMENT",
                "snapshot_date": RUN_DATE,
                "measurement_topics": MEASUREMENT_TOPICS,
                "candidates": candidates,
                "topics": topics,
            },
        )
    print(f"[measurement] wrote {_rel(CANDIDATE_PATH)}", flush=True)
    return 0


def _parsed_candidates(candidates: list[Any]) -> tuple[dict[tuple[str, str], list[dict[str, Any]]], list[dict[str, Any]]]:
    index: dict[tuple[str, str], list[dict[str, Any]]] = {}
    parsed: list[dict[str, Any]] = []
    for item in candidates:
        keys, label = _candidate_keys(item)
        routes = []
        if isinstance(item, dict):
            raw_routes = item.get("found_by_routes")
            if isinstance(raw_routes, list):
                routes = [str(r) for r in raw_routes if str(r)]
            if not routes and item.get("route"):
                routes = [str(item.get("route"))]
        if not routes:
            routes = ["unrouted"]
        row = {"keys": keys, "label": label, "routes": routes, "item": item}
        parsed.append(row)
        for key in keys:
            index.setdefault(key, []).append(row)
    return index, parsed


def score_candidate_file(candidate_path: Path = CANDIDATE_PATH) -> dict[str, Any]:
    benchmark = _load_json(BENCHMARK_PATH)
    payload = _load_json(candidate_path)
    candidate_topics = payload.get("candidates") or {}
    rows = []
    totals = {
        "all": {"found": 0, "N": 0},
        "audit": {"found": 0, "N": 0},
        "pooled": {"found": 0, "N": 0},
    }
    reverse_total = 0
    for slug in MEASUREMENT_TOPICS:
        positives = (benchmark.get("topics") or {}).get(slug, {}).get("positives") or []
        cindex, parsed = _parsed_candidates(candidate_topics.get(slug, []))
        benchmark_keys = {_positive_key(row) for row in positives}
        found = []
        missed = []
        for positive in positives:
            key = _positive_key(positive)
            hits = cindex.get(key) or []
            origins = _origins(positive)
            is_found = bool(hits)
            totals["all"]["N"] += 1
            totals["all"]["found"] += 1 if is_found else 0
            if origins & AUDIT_ORIGINS:
                totals["audit"]["N"] += 1
                totals["audit"]["found"] += 1 if is_found else 0
            if "pooled_or_declared_absent" in origins:
                totals["pooled"]["N"] += 1
                totals["pooled"]["found"] += 1 if is_found else 0
            if hits:
                route_labels = sorted({r for hit in hits for r in hit["routes"]})
                found.append({"positive": positive, "match_key": f"{key[0]}:{key[1]}", "routes": route_labels})
            else:
                missed.append(positive)
        reverse = [
            item
            for item in parsed
            if not item["keys"] or not any(key in benchmark_keys for key in item["keys"])
        ]
        reverse_total += len(reverse)
        rows.append({
            "slug": slug,
            "N": len(positives),
            "name_only": sum(1 for row in positives if row.get("identifier_state") == "NAME_ONLY"),
            "found": found,
            "missed": missed,
            "reverse": reverse,
            "candidate_count": len(parsed),
        })
    totals["reverse_not_in_benchmark"] = reverse_total
    return {"rows": rows, "totals": totals, "candidate_payload": payload, "benchmark": benchmark}


class DiagnosticRecorder:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self._source_id: str | None = None
        self._adapter: str | None = None

    @contextmanager
    def source(self, source_id: str, adapter: str):
        prev_source, prev_adapter = self._source_id, self._adapter
        self._source_id, self._adapter = source_id, adapter
        try:
            yield
        finally:
            self._source_id, self._adapter = prev_source, prev_adapter

    def record_current(self, url: str, params: dict | None, status: Any, body: bytes) -> None:
        if self._source_id is None:
            return
        data = bytes(body or b"")
        self.calls.append({
            "source_id": self._source_id,
            "url": str(url),
            "params": params or {},
            "status": status,
            "fetched_utc": _utc_now(),
            "adapter": self._adapter or "scripts.measure_search_v2_measurement",
            "body_sha256": hashlib.sha256(data).hexdigest(),
            "body_bytes": data,
        })

    def write(self, snapshot_dir: Path) -> dict[str, Any]:
        diag_root = snapshot_dir / "measurement_diagnostics" / "raw"
        if diag_root.exists():
            for child in sorted(diag_root.rglob("*"), reverse=True):
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
        diag_root.mkdir(parents=True, exist_ok=True)
        per_source: Counter[str] = Counter()
        index = []
        for call in self.calls:
            source_id = str(call["source_id"])
            per_source[source_id] += 1
            dirname = diag_root / source_id
            dirname.mkdir(parents=True, exist_ok=True)
            filename = f"{per_source[source_id]:03d}.json"
            body = bytes(call.get("body_bytes") or b"")
            payload = {k: v for k, v in call.items() if k != "body_bytes"}
            payload["body_bytes_b64"] = base64.b64encode(body).decode("ascii")
            raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            out = dirname / filename
            out.write_bytes(raw)
            index.append({
                "source_id": source_id,
                "path": _posix(out.relative_to(snapshot_dir)),
                "url": call.get("url"),
                "params": call.get("params"),
                "status": call.get("status"),
                "fetched_utc": call.get("fetched_utc"),
                "adapter": call.get("adapter"),
                "body_sha256": call.get("body_sha256"),
                "file_sha256": hashlib.sha256(raw).hexdigest(),
            })
        index_bytes = json.dumps(index, ensure_ascii=False, indent=2).encode("utf-8")
        (diag_root / "INDEX.json").write_bytes(index_bytes)
        return {"raw_calls": len(index), "raw_index_sha256": hashlib.sha256(index_bytes).hexdigest()}


def _safe_get_json(rec: DiagnosticRecorder, source_id: str, url: str, params: dict[str, Any]) -> tuple[dict | None, str | None]:
    try:
        with rec.source(source_id, "scripts.measure_search_v2_measurement"):
            return http.get_json(url, params), None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def _pubmed_esearch(rec: DiagnosticRecorder, source_id: str, query: str, retmax: int = 5) -> dict[str, Any]:
    payload, error = _safe_get_json(
        rec,
        source_id,
        f"{search_v2.EUTILS}/esearch.fcgi",
        {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": retmax,
            "tool": "meta-harness",
            "email": "meta-harness@example.org",
        },
    )
    if error:
        return {"state": "RAN_ERROR", "count": None, "ids": [], "error": error, "query": query}
    esr = (payload or {}).get("esearchresult") or {}
    ids = [str(x) for x in (esr.get("idlist") or [])]
    try:
        count = int(esr.get("count"))
    except (TypeError, ValueError):
        count = None
    return {
        "state": "RAN_OK" if count else "RAN_ZERO",
        "count": count,
        "ids": ids,
        "error": None,
        "query": query,
    }


def _epmc_search(rec: DiagnosticRecorder, source_id: str, query: str) -> dict[str, Any]:
    payload, error = _safe_get_json(
        rec,
        source_id,
        search_v2.EPMC_SEARCH,
        {"query": query, "format": "json", "pageSize": 5, "resultType": "core"},
    )
    if error:
        return {"state": "RAN_ERROR", "count": None, "ids": [], "error": error, "query": query}
    try:
        count = int((payload or {}).get("hitCount"))
    except (TypeError, ValueError):
        count = None
    rows = (((payload or {}).get("resultList") or {}).get("result") or [])
    ids = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        ids.append(str(row.get("pmid") or row.get("id") or row.get("doi") or ""))
    return {
        "state": "RAN_OK" if count else "RAN_ZERO",
        "count": count,
        "ids": [x for x in ids if x],
        "error": None,
        "query": query,
    }


def _ctgov_get(rec: DiagnosticRecorder, source_id: str, nct: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
    payload, error = _safe_get_json(
        rec,
        source_id,
        f"{search_v2.CTGOV}/{nct}",
        {
            "fields": (
                "protocolSection.identificationModule,protocolSection.designModule,"
                "protocolSection.conditionsModule,protocolSection.armsInterventionsModule,"
                "protocolSection.statusModule,hasResults"
            )
        },
    )
    if error:
        if "HTTP Error 404" in error or "404" in error:
            return {"state": "RAN_ZERO", "count": 0, "ids": [], "error": None, "query": nct}, None
        return {"state": "RAN_ERROR", "count": None, "ids": [], "error": error, "query": nct}, None
    rec_id = (((payload or {}).get("protocolSection") or {}).get("identificationModule") or {}).get("nctId")
    return {"state": "RAN_OK", "count": 1, "ids": [str(rec_id or nct)], "error": None, "query": nct}, payload


def _ctgov_search(rec: DiagnosticRecorder, source_id: str, params: dict[str, Any]) -> dict[str, Any]:
    request = {
        "pageSize": 5,
        "countTotal": "true",
        "fields": (
            "protocolSection.identificationModule,protocolSection.designModule,"
            "protocolSection.conditionsModule,protocolSection.armsInterventionsModule,"
            "protocolSection.statusModule,hasResults"
        ),
    }
    request.update({k: v for k, v in params.items() if v})
    payload, error = _safe_get_json(rec, source_id, search_v2.CTGOV, request)
    if error:
        return {"state": "RAN_ERROR", "count": None, "ids": [], "error": error, "query": request}
    try:
        count = int((payload or {}).get("totalCount"))
    except (TypeError, ValueError):
        count = None
    studies = (payload or {}).get("studies") or []
    ids = []
    for study in studies if isinstance(studies, list) else []:
        if not isinstance(study, dict):
            continue
        nct = (((study.get("protocolSection") or {}).get("identificationModule") or {}).get("nctId"))
        if nct:
            ids.append(str(nct))
    return {
        "state": "RAN_OK" if count else "RAN_ZERO",
        "count": count,
        "ids": ids,
        "error": None,
        "query": request,
    }


def _pubmed_record(rec: DiagnosticRecorder, pmid: str) -> dict[str, Any] | None:
    prev = http.RECORDER
    http.RECORDER = rec
    try:
        with rec.source(f"diag_pubmed_efetch_{pmid}", "harness.search_v2._pubmed_efetch"):
            rows = search_v2._pubmed_efetch([pmid])  # noqa: SLF001 - diagnostic uses frozen parser.
        return rows[0] if rows else None
    except Exception:
        return None
    finally:
        http.RECORDER = prev


def _ctgov_text(study: dict[str, Any] | None) -> str:
    if not study:
        return ""
    ps = study.get("protocolSection") or {}
    idm = ps.get("identificationModule") or {}
    cond = (ps.get("conditionsModule") or {}).get("conditions") or []
    arms = (ps.get("armsInterventionsModule") or {}).get("interventions") or []
    intr = [i.get("name") for i in arms if isinstance(i, dict)]
    return " ".join(str(x or "") for x in [
        idm.get("briefTitle"),
        idm.get("officialTitle"),
        idm.get("acronym"),
        " ".join(cond if isinstance(cond, list) else []),
        " ".join(intr),
    ])


def _term_matches(terms: list[str], text: str) -> list[str]:
    folded = _fold(text)
    matches = []
    for term in terms or []:
        raw = _fold(term).replace("*", "")
        if raw and raw in folded:
            matches.append(str(term))
    return matches


def _source_text(pubmed_row: dict[str, Any] | None, ctgov_row: dict[str, Any] | None, positive: dict[str, Any]) -> str:
    parts = [
        positive.get("trial") or "",
        (pubmed_row or {}).get("title") or "",
        (pubmed_row or {}).get("abstract") or "",
        _ctgov_text(ctgov_row),
    ]
    return " ".join(str(p) for p in parts if p)


def _coverage_diagnosis(text: str, queries: dict[str, Any]) -> dict[str, Any]:
    terms = ((queries or {}).get("terms") or {})
    intervention = terms.get("intervention") or []
    population = terms.get("population") or []
    intervention_hits = _term_matches(intervention, text)
    population_hits = _term_matches(population, text)
    rct_hits = _term_matches(
        ["randomized", "randomised", "placebo", "controlled trial", "trial"],
        text,
    )
    absent = []
    if not intervention_hits:
        absent.append("intervention")
    if not population_hits:
        absent.append("population")
    if not rct_hits:
        absent.append("rct_filter")
    return {
        "intervention_terms_matched": intervention_hits,
        "population_terms_matched": population_hits,
        "rct_filter_terms_matched": rct_hits,
        "absent_required_query_term_groups": absent,
        "emitted_intervention_terms": intervention,
        "emitted_population_terms": population,
    }


def diagnose_miss(slug: str, positive: dict[str, Any], topic_meta: dict[str, Any]) -> dict[str, Any]:
    snapshot_dir = ROOT / str(topic_meta.get("snapshot_dir", ""))
    rec = DiagnosticRecorder()
    prev_recorder = http.RECORDER
    http.RECORDER = rec
    try:
        pmid = _pmid(positive.get("pmid"))
        nct = _nct(positive.get("nct"))
        doi = _doi(positive.get("doi"))
        title = str(positive.get("trial") or "")
        pubmed_row = None
        ctgov_payload = None

        if pmid:
            pubmed_presence = _pubmed_esearch(rec, f"diag_pubmed_presence_{pmid}", f"{pmid}[uid]")
            pubmed_row = _pubmed_record(rec, pmid)
            if pubmed_row and not nct:
                nct = _nct(pubmed_row.get("nct"))
            epmc_presence = _epmc_search(rec, f"diag_epmc_presence_{pmid}", f"EXT_ID:{pmid} AND SRC:MED")
        elif doi:
            pubmed_presence = _pubmed_esearch(rec, "diag_pubmed_presence_doi", f'"{doi}"[AID]')
            epmc_presence = _epmc_search(rec, "diag_epmc_presence_doi", f'DOI:"{doi}"')
        elif nct:
            pubmed_presence = _pubmed_esearch(rec, f"diag_pubmed_presence_{nct}", f'"{nct}"[si]')
            epmc_presence = _epmc_search(rec, f"diag_epmc_presence_{nct}", f"NCT:{nct}")
        else:
            pubmed_presence = _pubmed_esearch(rec, "diag_pubmed_presence_title", f'"{title}"[Title]')
            epmc_presence = _epmc_search(rec, "diag_epmc_presence_title", f'TITLE:"{title}"')

        if nct:
            ctgov_presence, ctgov_payload = _ctgov_get(rec, f"diag_ctgov_presence_{nct}", nct)
        elif title:
            ctgov_presence = _ctgov_search(rec, "diag_ctgov_presence_title", {"query.term": title})
        else:
            ctgov_presence = {"state": "NOT_RUN", "count": None, "ids": [], "error": "no NCT or title", "query": None}

        queries = {}
        try:
            records_dict = _load_json(snapshot_dir / "records.json")
            queries = ((records_dict.get("search_v2") or {}).get("queries") or {})
        except Exception:
            queries = {}

        intersections: dict[str, Any] = {}
        if pmid and queries.get("pubmed"):
            intersections["pubmed_concept_query"] = _pubmed_esearch(
                rec,
                f"diag_pubmed_query_intersection_{pmid}",
                f"({queries['pubmed']}) AND {pmid}[uid]",
                retmax=5,
            )
        else:
            intersections["pubmed_concept_query"] = {"state": "NOT_RUN", "reason": "no PMID or no emitted PubMed query"}
        if pmid and queries.get("europepmc"):
            intersections["europepmc_concept_query"] = _epmc_search(
                rec,
                f"diag_epmc_query_intersection_{pmid}",
                f"({queries['europepmc']}) AND EXT_ID:{pmid} AND SRC:MED",
            )
        else:
            intersections["europepmc_concept_query"] = {"state": "NOT_RUN", "reason": "no PMID or no emitted Europe PMC query"}
        if nct and queries.get("ctgov"):
            ctgov_params = dict(queries["ctgov"])
            ctgov_params["query.id"] = nct
            intersections["ctgov_condition_intervention"] = _ctgov_search(
                rec,
                f"diag_ctgov_query_intersection_{nct}",
                ctgov_params,
            )
        else:
            intersections["ctgov_condition_intervention"] = {"state": "NOT_RUN", "reason": "no NCT or no emitted CT.gov query"}

        source_text = _source_text(pubmed_row, ctgov_payload, positive)
        coverage = _coverage_diagnosis(source_text, queries)
        source_exists = any(
            item.get("state") == "RAN_OK" and (item.get("count") or 0) > 0
            for item in (pubmed_presence, epmc_presence, ctgov_presence)
        )
        any_query_match = any(
            isinstance(item, dict) and item.get("state") == "RAN_OK" and (item.get("count") or 0) > 0
            for item in intersections.values()
        )
        status = "NOT_IN_ANY_SOURCE" if not source_exists else ("QUERY_MATCHED_IN_PRINCIPLE" if any_query_match else "QUERY_DID_NOT_MATCH")
        return {
            "slug": slug,
            "positive": positive,
            "status": status,
            "pubmed_presence": pubmed_presence,
            "europepmc_presence": epmc_presence,
            "ctgov_presence": ctgov_presence,
            "query_intersections": intersections,
            "text_coverage": coverage,
            "diagnostic_raw": rec.write(snapshot_dir) if snapshot_dir.is_dir() else {"raw_calls": rec.calls and len(rec.calls), "raw_index_sha256": None},
        }
    finally:
        http.RECORDER = prev_recorder


def diagnose_misses(score: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    payload = score["candidate_payload"]
    diagnostics: dict[str, list[dict[str, Any]]] = {}
    for row in score["rows"]:
        slug = row["slug"]
        topic_meta = (payload.get("topics") or {}).get(slug) or {}
        diagnostics[slug] = []
        for positive in row["missed"]:
            print(f"[measurement] diagnose miss {slug}: {_id_label(positive)}", flush=True)
            diagnostics[slug].append(diagnose_miss(slug, positive, topic_meta))
            time.sleep(0.34)
    return diagnostics


def _heldout_summary() -> dict[str, Any]:
    if not REGRESSION_RECALL_PATH.is_file():
        return {"recall_text": "not measured", "trials_recalled": 0, "trials_known_eligible": 0}
    data = _load_json(REGRESSION_RECALL_PATH)
    summary = data.get("summary") or {}
    return {
        "recall_text": summary.get("recall_text") or "not measured",
        "trials_recalled": summary.get("trials_recalled"),
        "trials_known_eligible": summary.get("trials_known_eligible"),
        "topics": summary.get("topics"),
        "topics_scored": summary.get("topics_scored"),
        "topics_not_scored": summary.get("topics_not_scored") or [],
        "engine_sha": data.get("engine_sha"),
        "measured_utc": data.get("measured_utc"),
    }


def _corpus_line(score: dict[str, Any], heldout: dict[str, Any]) -> str:
    totals = score["totals"]
    states = (score.get("candidate_payload") or {}).get("topics") or {}
    n_err = sum(1 for slug in MEASUREMENT_TOPICS if (states.get(slug) or {}).get("state") == "RAN_ERROR")
    return (
        "MEASUREMENT topics (21, sealed before the engine existed): "
        f"audit-found positives found {totals['audit']['found']} of {totals['audit']['N']} (named); "
        f"pooled-or-declared positives found {totals['pooled']['found']} of {totals['pooled']['N']}; "
        f"{n_err} of {len(MEASUREMENT_TOPICS)} topics RAN_ERROR (the engine refused its own query; contribute 0 found, counted in N); "
        f"sealed regression register {heldout.get('recall_text')} -- measured with the LEGACY concept-query engine "
        f"(harness/acquisition.py, re-run because that file changed), NOT with search_v2, which has not been run against "
        f"the sealed register; development topics excluded"
    )


def _format_positive(row: dict[str, Any]) -> str:
    note = f" | note={row['note']}" if row.get("note") else ""
    return f"{row.get('trial')} | {_id_label(row)} | origin={row.get('origin')}{note}"


def render_recall(score: dict[str, Any], heldout: dict[str, Any]) -> str:
    payload = score["candidate_payload"]
    lines = [
        "SEARCH V2 MEASUREMENT RECALL",
        _corpus_line(score, heldout),
        f"Base commit: {payload.get('base_commit')}",
        f"Engine sha (harness/search_v2.py): {payload.get('engine_sha')}",
        f"Candidate file: {_rel(CANDIDATE_PATH)}",
        f"Snapshot date: {payload.get('snapshot_date')}",
        "",
    ]
    for row in score["rows"]:
        lines.append(
            f"## {row['slug']} - N={row['N']} named={row['N']} name_only={row['name_only']} "
            f"found={len(row['found'])} missed={len(row['missed'])} "
            f"candidates={row['candidate_count']} reverse_not_in_benchmark={len(row['reverse'])}"
        )
        lines.append("found:")
        if row["found"]:
            for hit in row["found"]:
                lines.append(
                    f"- FOUND {_format_positive(hit['positive'])} | "
                    f"routes={'; '.join(hit['routes'])} | match_key={hit['match_key']}"
                )
        else:
            lines.append("- none")
        lines.append("missed:")
        if row["missed"]:
            for miss in row["missed"]:
                lines.append(f"- MISSED {_format_positive(miss)}")
        else:
            lines.append("- none")
        lines.append("")
    return "\n".join(lines)


def render_routes(score: dict[str, Any]) -> str:
    lines = [
        "SEARCH V2 ROUTE ATTRIBUTION FOR FOUND POSITIVES",
        f"Engine sha (harness/search_v2.py): {score['candidate_payload'].get('engine_sha')}",
        "",
    ]
    for row in score["rows"]:
        lines.append(f"## {row['slug']}")
        if not row["found"]:
            lines.append("- no positives found")
        for hit in row["found"]:
            lines.append(f"- {_format_positive(hit['positive'])} | routes={'; '.join(hit['routes'])}")
        lines.append("")
    return "\n".join(lines)


def _presence_text(item: dict[str, Any]) -> str:
    state = item.get("state")
    count = item.get("count")
    if state == "NOT_RUN":
        return f"NOT_RUN ({item.get('reason') or item.get('error')})"
    if state == "RAN_ERROR":
        return f"RAN_ERROR ({item.get('error')})"
    return f"{'YES' if state == 'RAN_OK' and (count or 0) > 0 else 'NO'} count={count}"


def render_misses(score: dict[str, Any], diagnostics: dict[str, list[dict[str, Any]]]) -> str:
    lines = [
        "SEARCH V2 MISSES DIAGNOSED",
        "Each raw diagnostic response is cached under cache/<slug>/snapshots/2026-09-15-search_v2/measurement_diagnostics/raw/.",
        "",
    ]
    for row in score["rows"]:
        lines.append(f"## {row['slug']}")
        if not diagnostics.get(row["slug"]):
            lines.append("- no missed positives")
        for diag in diagnostics.get(row["slug"], []):
            cov = diag.get("text_coverage") or {}
            intersections = diag.get("query_intersections") or {}
            lines.append(f"- {_format_positive(diag['positive'])}")
            lines.append(f"  status={diag.get('status')}")
            lines.append(
                "  source_presence: "
                f"PubMed={_presence_text(diag.get('pubmed_presence') or {})}; "
                f"EuropePMC={_presence_text(diag.get('europepmc_presence') or {})}; "
                f"CT.gov={_presence_text(diag.get('ctgov_presence') or {})}"
            )
            lines.append(
                "  query_intersection: "
                + "; ".join(f"{name}={_presence_text(value)}" for name, value in intersections.items())
            )
            absent = cov.get("absent_required_query_term_groups") or []
            lines.append(
                "  emitted-term coverage: "
                f"intervention={cov.get('intervention_terms_matched') or []}; "
                f"population={cov.get('population_terms_matched') or []}; "
                f"rct_filter={cov.get('rct_filter_terms_matched') or []}; "
                f"absent_required_groups={absent or []}"
            )
            if absent:
                for group in absent:
                    key = "emitted_intervention_terms" if group == "intervention" else "emitted_population_terms"
                    if group == "rct_filter":
                        lines.append("  absent detail: no emitted RCT-filter text term was found in the source text")
                    else:
                        lines.append(f"  absent detail: no emitted {group} term matched the source text; emitted terms={cov.get(key) or []}")
            raw = diag.get("diagnostic_raw") or {}
            lines.append(f"  diagnostic_raw_calls={raw.get('raw_calls')} raw_index_sha256={raw.get('raw_index_sha256')}")
        lines.append("")
    return "\n".join(lines)


def render_heldout(heldout: dict[str, Any]) -> str:
    return "\n".join([
        "SEALED HELD-OUT/REGRESSION REGISTER MEASUREMENT",
        "No plaintext register rows are copied into this evidence capture.",
        "",
        f"sealed regression register {heldout.get('recall_text')} -- LEGACY concept-query engine (acquisition.concept_query), not search_v2",
        f"topics={heldout.get('topics')} topics_scored={heldout.get('topics_scored')} topics_not_scored={heldout.get('topics_not_scored')}",
        f"engine_sha (harness/acquisition.py): {heldout.get('engine_sha')}",
        f"measured_utc: {heldout.get('measured_utc')}",
        f"source artifact: {_rel(REGRESSION_RECALL_PATH)}",
        f"source artifact sha256: {_sha256_file(REGRESSION_RECALL_PATH) if REGRESSION_RECALL_PATH.is_file() else 'missing'}",
    ])


def render_reverse(score: dict[str, Any]) -> str:
    lines = [
        "SEARCH V2 REVERSE DIRECTION",
        "Counts are candidate records not in the benchmark; this is not an eligibility judgement.",
        "",
    ]
    grand = Counter()
    for row in score["rows"]:
        route_counts = Counter()
        for item in row["reverse"]:
            for route in item.get("routes") or ["unrouted"]:
                route_counts[route] += 1
                grand[route] += 1
        lines.append(
            f"## {row['slug']} - candidates={row['candidate_count']} "
            f"reverse_not_in_benchmark={len(row['reverse'])}"
        )
        if route_counts:
            for route, count in sorted(route_counts.items()):
                lines.append(f"- {route}: {count}")
        else:
            lines.append("- none")
        lines.append("")
    lines.append("## corpus route counts")
    for route, count in sorted(grand.items()):
        lines.append(f"- {route}: {count}")
    return "\n".join(lines)


def render_readme(score: dict[str, Any], heldout: dict[str, Any]) -> str:
    return "\n".join([
        "# Search v2 measurement (2026-09-15)",
        "",
        _corpus_line(score, heldout),
        "",
        "This bundle measures the frozen search_v2 engine on the 21 sealed MEASUREMENT topics only.",
        "Development topics are excluded from the capability number.",
        "Snapshots are unpinned and written beside the pinned caches; served review pages and pools were not moved.",
        "",
        "Captures:",
        "- `01-recall-21.txt`: per-topic recall table with every benchmark-positive name.",
        "- `02-routes.txt`: route attribution for every found positive.",
        "- `03-misses-diagnosed.txt`: source-presence and emitted-query diagnostics for every missed positive.",
        "- `04-heldout-register.txt`: sealed/register measurement summary without plaintext rows.",
        "- `05-reverse-direction.txt`: candidate counts not in the benchmark by topic and route.",
    ])


def _update_captions() -> None:
    captions = _load_json(CAPTIONS_PATH)
    captions["search-v2-measurement-2026-09-15"] = {
        "_title": "search_v2 measurement (2026-09-15): sealed 21-topic recall, routes, misses, and reverse direction",
        "_intro": "Lane S3 evidence: the frozen search_v2 engine run on MEASUREMENT topics only, with scored recall, found-route attribution, diagnosed misses, sealed-register summary, and reverse-direction candidate counts.",
        "README.md": "Bundle summary with the exact measurement corpus line and generated fix-state line.",
        "01-recall-21.txt": "Per-topic recall table for all 21 MEASUREMENT topics, with every named benchmark positive marked FOUND or MISSED and route labels for found positives.",
        "02-routes.txt": "Route attribution for every found positive: concept-query PubMed, Europe PMC, CT.gov cross-link, backward citation, forward citation, or comparator reference list.",
        "03-misses-diagnosed.txt": "Per-missed-positive source-presence checks in PubMed, Europe PMC and CT.gov plus emitted-query intersection/term-coverage diagnostics; raw responses cached under each snapshot directory.",
        "04-heldout-register.txt": "Summary-only sealed/register recall measurement for verify_all currency; plaintext register rows are not copied here.",
        "05-reverse-direction.txt": "Reverse-direction accounting: candidates not in the benchmark counted by topic and route, explicitly not an eligibility judgement.",
    }
    _write_json(CAPTIONS_PATH, captions)


def _dependency_map(paths: list[str]) -> dict[str, str]:
    return {path: _blob(path) for path in paths}


def _update_fixes(score: dict[str, Any]) -> None:
    payload = score["candidate_payload"]
    heldout = _heldout_summary()
    deps = [
        "docs/evidence/search-v2-measurement-2026-09-15/README.md",
        "docs/evidence/search-v2-measurement-2026-09-15/01-recall-21.txt",
        "docs/evidence/search-v2-measurement-2026-09-15/02-routes.txt",
        "docs/evidence/search-v2-measurement-2026-09-15/03-misses-diagnosed.txt",
        "docs/evidence/search-v2-measurement-2026-09-15/04-heldout-register.txt",
        "docs/evidence/search-v2-measurement-2026-09-15/05-reverse-direction.txt",
        "outputs/search_v2/candidates-2026-09-15-measurement.json",
        "docs/search_recall_regression_corpus.json",
        "registry/search_benchmark.json",
        "registry/search_benchmark_split.json",
        "scripts/measure_search_recall.py",
        "scripts/measure_regression_corpus_recall.py",
        "scripts/measure_search_v2_measurement.py",
        "harness/search_v2.py",
        "harness/acquisition.py",
        "docs/evidence/CAPTIONS.json",
    ]
    event_evidence = [
        "docs/evidence/search-v2-measurement-2026-09-15/README.md",
        "docs/evidence/search-v2-measurement-2026-09-15/01-recall-21.txt",
        "docs/evidence/search-v2-measurement-2026-09-15/02-routes.txt",
        "docs/evidence/search-v2-measurement-2026-09-15/03-misses-diagnosed.txt",
        "docs/evidence/search-v2-measurement-2026-09-15/04-heldout-register.txt",
        "docs/evidence/search-v2-measurement-2026-09-15/05-reverse-direction.txt",
        "outputs/search_v2/candidates-2026-09-15-measurement.json",
        "docs/search_recall_regression_corpus.json",
    ]
    entry = {
        "finding_id": FIX_ID,
        "fix_id": FIX_ID,
        "title": "search_v2 recall measurement on the sealed 21-topic measurement split",
        "kind": "finding",
        "implementation": "LANDED",
        "verification": "NONE",
        "scope": "CORPUS",
        "author": "Codex lane S3",
        "opened_utc": f"{RUN_DATE}T00:00:00Z",
        "evidence_dir": "docs/evidence/search-v2-measurement-2026-09-15",
        "events": [
            {
                "implementation": "LANDED",
                "verification": "NONE",
                "scope": "CORPUS",
                "when_utc": f"{RUN_DATE}T00:00:00Z",
                "by": "Codex lane S3",
                "commit": payload.get("base_commit") or _git("rev-parse", "HEAD"),
                "evidence": event_evidence,
                "reason": "Measured the frozen search_v2 engine on the sealed MEASUREMENT split, reported recall, routes, miss diagnostics, reverse-direction counts, and the verify_all regression-register currency measurement.",
            }
        ],
        "verified_by": {"identity": None, "kind": None},
        "verifications": [],
        "authored_against": [
            payload.get("base_commit") or "",
            f"harness/search_v2.py:{payload.get('engine_sha')}",
        ],
        "generalized_on": ["21 named MEASUREMENT topics in registry/search_benchmark_split.json"],
        "executable_evidence": {
            "command": "python scripts/measure_search_recall.py outputs/search_v2/candidates-2026-09-15-measurement.json",
            "expected_substring": "MEASUREMENT TOPICS",
            "scope_basis": "21 named MEASUREMENT topics in registry/search_benchmark_split.json",
            "topic_list": MEASUREMENT_TOPICS,
            "heldout_register": heldout.get("recall_text"),
        },
        "seal": {
            "sealed_utc": _utc_now(),
            "commit": payload.get("base_commit") or _git("rev-parse", "HEAD"),
            "dependencies": _dependency_map(deps),
            "configuration": {
                "schema": "fixes-v3",
                "lane": "S3",
                "split": "MEASUREMENT",
                "snapshot_date": RUN_DATE,
                "topics": "21 named",
                "engine_sha": payload.get("engine_sha"),
                "corpus_line": _corpus_line(score, heldout),
            },
        },
        "note": "Local lane entry only; no commit was made per user instruction.",
    }
    store = _load_json(FIXES_PATH)
    entries = [item for item in store.get("entries", []) if item.get("fix_id") != FIX_ID]
    entries.append(entry)
    store["entries"] = entries
    _write_json(FIXES_PATH, store)


def render_report(score: dict[str, Any], heldout: dict[str, Any]) -> str:
    payload = score["candidate_payload"]
    lines = [
        _corpus_line(score, heldout),
        "",
        "# LANE S3 Report",
        "",
        f"Base commit: {payload.get('base_commit')}",
        f"Engine sha (harness/search_v2.py blob): {payload.get('engine_sha')}",
        f"Candidate file: {_rel(CANDIDATE_PATH)}",
        f"Evidence dir: {_rel(EVIDENCE_DIR)}",
        "",
        "Per-topic names:",
    ]
    for row in score["rows"]:
        lines.append(
            f"## {row['slug']} - found {len(row['found'])} of {row['N']}; "
            f"reverse_not_in_benchmark={len(row['reverse'])}"
        )
        for hit in row["found"]:
            lines.append(f"- FOUND {_format_positive(hit['positive'])} | routes={'; '.join(hit['routes'])}")
        for miss in row["missed"]:
            lines.append(f"- MISSED {_format_positive(miss)}")
        lines.append("")
    lines.extend([
        "Commands recorded:",
        f"- python scripts/measure_search_v2_measurement.py refresh -> wrote {_rel(CANDIDATE_PATH)}",
        f"- python scripts/measure_search_recall.py {_rel(CANDIDATE_PATH)} -> scored MEASUREMENT topics",
        "- python scripts/measure_regression_corpus_recall.py -> refreshed verify_all currency artifact",
        "- python scripts/measure_search_v2_measurement.py evidence -> wrote evidence, captions, fixes entry, and this report",
    ])
    return "\n".join(lines)


def write_evidence() -> int:
    score = score_candidate_file(CANDIDATE_PATH)
    diagnostics = diagnose_misses(score)
    heldout = _heldout_summary()
    _write_text(EVIDENCE_DIR / "01-recall-21.txt", render_recall(score, heldout))
    _write_text(EVIDENCE_DIR / "02-routes.txt", render_routes(score))
    _write_text(EVIDENCE_DIR / "03-misses-diagnosed.txt", render_misses(score, diagnostics))
    _write_text(EVIDENCE_DIR / "04-heldout-register.txt", render_heldout(heldout))
    _write_text(EVIDENCE_DIR / "05-reverse-direction.txt", render_reverse(score))
    _write_text(EVIDENCE_DIR / "README.md", render_readme(score, heldout))
    _update_captions()
    _update_fixes(score)
    _write_text(REPORT_PATH, render_report(score, heldout))
    print(_corpus_line(score, heldout))
    print(f"[measurement] wrote {_rel(EVIDENCE_DIR)} and {_rel(REPORT_PATH)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("refresh")
    sub.add_parser("evidence")
    args = parser.parse_args(argv)
    if args.cmd == "refresh":
        return refresh_measurement()
    if args.cmd == "evidence":
        return write_evidence()
    raise AssertionError(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
