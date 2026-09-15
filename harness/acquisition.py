"""ACQUISITION LAYER CONTRACT -- how every record was found, replayable from the protocol SHA.

WHY THIS EXISTS (2026-09-14). A review is reproducible iff re-running from its protocol SHA regenerates
the served page. Search was the reason that could not be true: the fetch listed its queries but recorded
NOTHING per record (which query/adapter found it), no per-query hit count or funnel, no run state per
query, and a failed adapter was written as RAN_OK (evidence/search-acquisition-2026-09-14/01-*). The
screening ledger (3,143 rule-id decisions) had no retrieval ledger to join to.

THE CONTRACT (five fields per source, joined to the screening ledger on the record id):
  1. the VERBATIM query (or prompt, for a model call)      -> source.query
  2. the date it ran                                        -> source.run_utc
  3. the denominator with the funnel hits -> retained       -> source.funnel {hits, fetched, retained, cap}
  4. the per-record decision with a rule id                 -> screening ledger, joined via records[id].found_by
  5. an explicit run state, one of four                     -> source.state
     RAN_OK    ran and returned >= 1 record
     RAN_ZERO  ran, HTTP/API success, returned 0 records         (a legitimate zero)
     RAN_ERROR attempted and FAILED (exception, non-2xx, malformed payload)   -- NEVER folded into RAN_ZERO
     NOT_RUN   not attempted for this topic
  A source that raised has NO count; it is RAN_ERROR with the error text, and nothing downstream may
  read its absence of records as "nothing there".

TWO MODES, decided deliberately:
  REFRESH -- runs the sources LIVE and writes a NEW DATED SNAPSHOT under cache/<slug>/snapshots/<id>/
             (records.json + retrieval_ledger.json). Never overwrites the pinned snapshot by itself.
  REPLAY  -- the build reads the PINNED snapshot (cache/<slug>/records.json + retrieval_ledger.json) and
             must be bit-identical; this is what scripts/reproduce_review.py checks.
  Every page build is a REPLAY by construction (fetch-once). "Fresh" is therefore a dated property of the
  SNAPSHOT (snapshot.retrieved_utc, snapshot.mode), not a flag on the build -- so reproducibility is always
  true and freshness is a fact the reader can date, never a claim the builder asserts. The page renders
  both: when the records were retrieved (and how), and that this build replayed that snapshot.
  Pinning a fresh snapshot (acquisition.pin) is a corpus-moving change: it goes through the full standard.

LEGACY. The 32 caches that predate this layer have no ledger. Their state is LEGACY_UNRECORDED: the queries
are known, which query found which record is NOT, and nothing may fabricate it. The pipeline adds the
`search.retrieval` block to the review core ONLY when a ledger file exists beside the pinned records, so
those pages are byte-unchanged until they are deliberately regenerated (that tranche writes their legacy
ledger explicitly as LEGACY_UNRECORDED, or refreshes them).

RANKED TRUNCATION. esearch(retmax=40) was a relevance-ranked top-N cut (764 hits -> 40 fetched, remainder
unrecorded). A size-ranked cap cannot close a k gap: pivotal is not largest. Concept-query sources paginate
the FULL boolean set; any cap that does apply is recorded in the funnel with its remainder and rendered.

PMID ENUMERATION IS NOT A SEARCH. A source whose query is a `<uid>[uid]` list can retrieve only what it was
told; it is recorded with kind PUBMED_PMID_ENUMERATION and discovery_capable=false, and the page says so.
Fourteen live topics have only such queries: they have had NO search, not a weak one.

FILE LAYOUT
  cache/<slug>/records.json                       pinned snapshot records (unchanged shape)
  cache/<slug>/retrieval_ledger.json              pinned snapshot ledger (schema below)
  cache/<slug>/raw/INDEX.json                     pinned raw retrieval-response index, if the cache was freshly fetched
  cache/<slug>/snapshots/<retrieved_utc>-<sha8>/  refresh outputs: records.json + retrieval_ledger.json
  cache/<slug>/snapshots/<retrieved_utc>-<sha8>/raw/<source_id>/<NNN>.json
                                                    raw retrieval responses for that dated refresh
  RAW BODIES OFF-TREE (search_v2 runs, 2026-09-15): a full-pagination run of one topic writes 200-600 MB of raw
  bodies, so for those snapshots the bodies are archived outside the repository by scripts/archive_raw_bodies.py and
  only raw/INDEX.json (one row per HTTP call with url, params, status, fetched_utc, adapter blob sha, body_sha256,
  file_sha256) and ARCHIVE.json (archive root, custody, index sha) stay in-tree. `archive_raw_bodies.py check`
  re-hashes every archived body against INDEX.json; a body the archive cannot produce reads NOT PRESERVED. Custody:
  the session author's machine; digests in-tree are the authority.

LEDGER SCHEMA (version 1)
  {
    "version": 1, "slug": "<slug>",
    "snapshot": {"records_sha256": "<sha256 of canonical_json(records list)>", "retrieved_utc": "YYYY-MM-DD",
                 "mode": "REFRESH" | "LEGACY_UNRECORDED", "engine_sha": "<git blob sha of harness/acquisition.py>",
                 "raw_calls": int, "raw_index_sha256": "<sha256 of raw/INDEX.json, if raw_calls > 0>"},
    "sources": [
      {"source_id": "<kind-lowercase>#<n>", "kind": <SOURCE_KINDS>, "query": "<verbatim>", "run_utc": "YYYY-MM-DD",
       "state": <STATES>, "error": null | "<text>", "discovery_capable": true|false,
       "funnel": {"hits": int|null, "fetched": int, "retained": int,
                  "cap": {"kind": "none" | "relevance_top_n" | "record_cap" | "hard_hits_cap", "n": int|null, "remainder": int|null}},
       "record_ids": ["<id>", ...]}
    ],
    "records": {"<id>": {"found_by": ["<source_id>", ...]}}
  }
  Invariants (tested): every id in records.json appears in ledger.records with >= 1 found_by; every found_by
  names a source_id in sources; a source with state RAN_ERROR has error != null and fetched == 0; a source
  with state RAN_ZERO has error == null and hits == 0; cap.kind != "none" implies remainder is an int >= 0.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
import base64
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any

from . import http
from . import lexicon
from .canonical import canonical_json

LEDGER_VERSION = 1

STATES = ("RAN_OK", "RAN_ZERO", "RAN_ERROR", "NOT_RUN",
          # RAN_UNRECORDED: LEGACY ONLY. A pre-ledger fetch attempted this source (the code path ran it) but its
          # yield was never recorded. Neither NOT_RUN ("not attempted") nor RAN_OK ("returned records") is true, and
          # asserting either would fabricate. A live run (snapshot.mode == REFRESH) may never produce it -- validate()
          # refuses it there -- so it can only describe the past, never hide a present failure.
          "RAN_UNRECORDED")
SNAPSHOT_MODES = ("REFRESH", "LEGACY_UNRECORDED")
SOURCE_KINDS = (
    "PUBMED_CONCEPT_QUERY",      # built from the registered P/I/C/design; paginated full boolean set
    "EUROPEPMC_CONCEPT_QUERY",
    "CTGOV_CONDITION_INTERVENTION",
    "ISRCTN_CONDITION_INTERVENTION",
    "PUBMED_NCT_LINK",
    "EPMC_NCT_LINK",
    "CTGOV_NCT_LINK",
    "EPMC_BACKWARD_CITATION",
    "EPMC_FORWARD_CITATION",
    "COMPARATOR_REFERENCE_LIST",
    "PUBMED_ELINK_BACKWARD_CITATION",   # PubMed elink pubmed_pubmed_refs of an included seed (second adapter, 2026-09-15)
    "COMPARATOR_REFERENCE_LIST_PUBMED", # PubMed elink pubmed_pubmed_refs of the comparator review (second adapter)
    "PUBMED_LEGACY_QUERY",       # a committed pubmed_queries string that is a real query (not an enumeration)
    "PUBMED_PMID_ENUMERATION",   # a <uid>[uid] list: retrieves only what it was told; discovery_capable=false
    "EUROPEPMC_QUERY",
    "COMPARATOR_REFERENCES",     # reference list of the comparator meta-analysis (seeding)
    "CITATION_CHASE",
    "REGISTRY_FIRST",            # condition x intervention enumeration on ClinicalTrials.gov/AACT -> PMIDs
    "CTGOV_SEARCH",
    "EXTRA_PMIDS",               # config.extra_pmids: hand-named, discovery_capable=false
    "CONTROL_PMIDS",             # NEGATIVE controls + the comparator itself (positive controls must be FOUND, never forced)
    "MODEL_CALL",                # a model asked to find/recover a trial: query = the verbatim prompt
    "LEGACY_UNRECORDED",         # a pre-ledger fetch; which query retrieved which record was not recorded; every record's found_by names this single source.
)
CAP_KINDS = ("none", "relevance_top_n", "record_cap", "hard_hits_cap")

LEDGER_FILENAME = "retrieval_ledger.json"
SNAPSHOT_DIRNAME = "snapshots"

# Implementation lands in this file (refresh / pin / load_ledger / concept_query / esearch_all / validate).

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _utc_now_seconds() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _jsonable(value: Any) -> Any:
    """Keep raw-call params replayable without assuming third-party encoders."""
    try:
        json.dumps(value, ensure_ascii=False)
        return value
    except TypeError:
        if isinstance(value, dict):
            return {str(k): _jsonable(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [_jsonable(v) for v in value]
        return str(value)


def _adapter_blob_sha(adapter: str | None) -> str:
    module_name = ".".join(str(adapter or "").split(".")[:-1])
    path = None
    if module_name:
        try:
            import importlib

            mod = importlib.import_module(module_name)
            path = getattr(mod, "__file__", None)
        except Exception:  # noqa: BLE001 - provenance should not make acquisition fail.
            path = None
    if not path:
        path = os.path.join(ROOT, "harness", "fetch.py")
    try:
        proc = subprocess.run(
            ["git", "hash-object", os.path.relpath(path, ROOT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return proc.stdout.strip() or "unknown"
    except Exception:  # noqa: BLE001 - git is provenance, not a runtime dependency.
        return "unknown"


class RawRecorder:
    """Run-local raw-response recorder; writes bodies only when the snapshot is written."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self._source_id: str | None = None
        self._adapter: str | dict[str, Any] | None = None

    @contextmanager
    def source(self, source_id: str, adapter: str | dict[str, Any]):
        prev_source, prev_adapter = self._source_id, self._adapter
        self._source_id, self._adapter = source_id, adapter
        try:
            yield
        finally:
            self._source_id, self._adapter = prev_source, prev_adapter

    def record_current(self, url: str, params: dict | None, status: Any, body_bytes: bytes) -> None:
        if self._source_id is None:
            return
        self.record(self._source_id, url, params, status, body_bytes, self._adapter)

    def record(self, source_id: str, url: str, params: dict | None,
               status: Any, body_bytes: bytes, adapter: str | dict[str, Any] | None) -> None:
        if isinstance(adapter, dict):
            adapter_name = adapter.get("adapter")
            adapter_sha = adapter.get("adapter_blob_sha") or _adapter_blob_sha(adapter_name)
        else:
            adapter_name = str(adapter or "unknown")
            adapter_sha = _adapter_blob_sha(adapter_name)
        body = bytes(body_bytes or b"")
        self.calls.append({
            "source_id": str(source_id),
            "url": str(url),
            "params": _jsonable(params or {}),
            "status": status,
            "fetched_utc": _utc_now_seconds(),
            "adapter": adapter_name,
            "adapter_blob_sha": adapter_sha,
            "body_sha256": hashlib.sha256(body).hexdigest(),
            "body_bytes": body,
        })

    @property
    def count(self) -> int:
        return len(self.calls)

    def write_snapshot(self, snapshot_dir: str) -> tuple[int, str | None]:
        if not self.calls:
            return 0, None
        raw_root = os.path.join(snapshot_dir, "raw")
        os.makedirs(raw_root, exist_ok=True)
        per_source: dict[str, int] = {}
        index: list[dict[str, Any]] = []
        for call in self.calls:
            source_id = call["source_id"]
            per_source[source_id] = per_source.get(source_id, 0) + 1
            dirname = os.path.join(raw_root, source_id)
            os.makedirs(dirname, exist_ok=True)
            filename = f"{per_source[source_id]:03d}.json"
            relpath = "/".join(["raw", source_id, filename])
            body = bytes(call.get("body_bytes") or b"")
            payload = {k: v for k, v in call.items() if k != "body_bytes"}
            payload["body_bytes_b64"] = base64.b64encode(body).decode("ascii")
            raw_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            with open(os.path.join(dirname, filename), "wb") as f:
                f.write(raw_bytes)
            index.append({
                "source_id": source_id,
                "path": relpath,
                "url": call.get("url"),
                "params": call.get("params"),
                "status": call.get("status"),
                "fetched_utc": call.get("fetched_utc"),
                "adapter": call.get("adapter"),
                "adapter_blob_sha": call.get("adapter_blob_sha"),
                "body_sha256": call.get("body_sha256"),
                "file_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            })
        index_bytes = json.dumps(index, ensure_ascii=False, indent=2).encode("utf-8")
        with open(os.path.join(raw_root, "INDEX.json"), "wb") as f:
            f.write(index_bytes)
        return len(index), hashlib.sha256(index_bytes).hexdigest()


def _none_cap() -> dict:
    return {"kind": "none", "n": None, "remainder": None}


def _funnel(hits: int | None, fetched: int, retained: int | None = None,
            cap: dict | None = None) -> dict:
    return {
        "hits": hits,
        "fetched": int(fetched),
        "retained": int(fetched if retained is None else retained),
        "cap": cap or _none_cap(),
    }


def _error_result(error: str) -> dict:
    return {
        "ids": [],
        "count": None,
        "state": "RAN_ERROR",
        "error": error,
        "funnel": _funnel(None, 0),
    }


def _as_int(value: Any, name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid esearch {name}: {value!r}") from exc


def esearch_all(query: str, page_size: int = 1000, hard_cap: int | None = None,
                sleep: float = 0.34) -> dict:
    """Run PubMed esearch over the full boolean result set with explicit state."""
    try:
        page_size = _as_int(page_size, "page_size")
        if page_size <= 0:
            raise ValueError("page_size must be positive")
        cap_n = None if hard_cap is None else _as_int(hard_cap, "hard_cap")
        if cap_n is not None and cap_n < 0:
            raise ValueError("hard_cap must be non-negative")

        ids: list[str] = []
        count: int | None = None
        retstart = 0
        while True:
            retmax = page_size
            if cap_n is not None:
                remaining_cap = cap_n - len(ids)
                if remaining_cap <= 0 and count is not None:
                    break
                retmax = min(retmax, max(remaining_cap, 0))
            payload = http.get_json(
                f"{EUTILS}/esearch.fcgi",
                {
                    "db": "pubmed",
                    "term": query,
                    "retmode": "json",
                    "retstart": retstart,
                    "retmax": retmax,
                    "tool": "meta-harness",
                    "email": "meta-harness@example.org",
                },
            )
            if not isinstance(payload, dict):
                raise ValueError("esearch response was not a JSON object")
            esr = payload.get("esearchresult")
            if not isinstance(esr, dict):
                raise ValueError("esearchresult missing from esearch response")
            if esr.get("ERROR"):
                raise ValueError(str(esr.get("ERROR")))
            if "count" not in esr:
                raise ValueError("count missing from esearchresult")
            count = _as_int(esr.get("count"), "count")
            batch = esr.get("idlist", [])
            if not isinstance(batch, list):
                raise ValueError("idlist was not a list")
            ids.extend(str(pid) for pid in batch)

            target = count if cap_n is None else min(count, cap_n)
            if len(ids) >= target or not batch:
                break
            retstart += len(batch)
            if sleep:
                time.sleep(sleep)

        assert count is not None
        if cap_n is not None and count > cap_n:
            cap = {"kind": "hard_hits_cap", "n": cap_n, "remainder": count - cap_n}
        else:
            cap = _none_cap()
        return {
            "ids": ids,
            "count": count,
            "state": "RAN_ZERO" if count == 0 else "RAN_OK",
            "error": None,
            "funnel": _funnel(count, len(ids), len(ids), cap),
        }
    except Exception as exc:  # noqa: BLE001 - source state must preserve adapter failure.
        return _error_result(str(exc))


# Drug CLASS -> members, for the class-term expansion (SONIA mechanism: search the molecules, not only
# the class label). Curated for the corpus's classes; a class label in the topic's intervention_terms
# triggers expansion to every member so a member-named trial is retrievable.
CLASS_MEMBERS = {
    "dpp-4 inhibitor": ["sitagliptin", "saxagliptin", "alogliptin", "linagliptin", "vildagliptin",
                        "omarigliptin", "trelagliptin", "gemigliptin", "teneligliptin", "anagliptin"],
    "glp-1 receptor agonist": ["semaglutide", "dulaglutide", "liraglutide", "exenatide", "lixisenatide",
                               "albiglutide", "efpeglenatide"],
    "sglt2 inhibitor": ["empagliflozin", "dapagliflozin", "canagliflozin", "ertugliflozin", "sotagliflozin"],
    "mineralocorticoid receptor antagonist": ["spironolactone", "eplerenone", "finerenone", "canrenone"],
}
_CLASS_TRIGGERS = {  # substrings in an intervention term that mean "this is the class label"
    "dpp-4": "dpp-4 inhibitor", "dpp4": "dpp-4 inhibitor",
    "glp-1": "glp-1 receptor agonist", "glp1": "glp-1 receptor agonist",
    "sglt2": "sglt2 inhibitor", "sglt-2": "sglt2 inhibitor",
    "mineralocorticoid": "mineralocorticoid receptor antagonist", "aldosterone": "mineralocorticoid receptor antagonist",
    "mra": "mineralocorticoid receptor antagonist",
}


def expand_intervention(terms):
    """Registered intervention terms + class-member expansion + abbreviation variants (recall net)."""
    out = set()
    for t in terms or []:
        tl = lexicon.fold(t)
        out.add(tl)
        for trig, cls in _CLASS_TRIGGERS.items():
            if trig in tl:
                out.update(CLASS_MEMBERS.get(cls, []))
        for variant, _ in lexicon.abbrev_variants(tl):
            out.add(variant)
    # drop pure class labels/abbreviations that add noise once members are in (keep the words though)
    return sorted(out)


def _or(terms):
    return " OR ".join(f'"{t}"[tiab]' if " " in t else f"{t}[tiab]" for t in terms if t)


def concept_query(config) -> str:
    """Concept query from registered P/I/C/design."""
    inc = config.get("include", {})
    interv = expand_intervention(config.get("intervention_terms"))
    pop = [lexicon.fold(p) for p in (inc.get("population_any") or [])]
    design = 'randomized controlled trial[pt] OR randomized[tiab] OR randomised[tiab] OR "controlled trial"[tiab]'
    parts = []
    if interv:
        parts.append("(" + _or(interv) + ")")
    if pop:
        parts.append("(" + _or(pop) + ")")
    parts.append("(" + design + ")")
    return " AND ".join(parts)


def classify_query(q: str) -> str:
    return "PUBMED_PMID_ENUMERATION" if "[uid]" in q else "PUBMED_LEGACY_QUERY"


def new_ledger(slug: str) -> dict:
    return {"version": LEDGER_VERSION, "slug": slug, "snapshot": None, "sources": [], "records": {}}


def _dedupe_strings(values) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values or []:
        s = str(value)
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def reserve_source_id(ledger: dict, kind: str) -> str:
    n = 1 + sum(1 for source in ledger.get("sources", []) if source.get("kind") == kind)
    source_id = f"{kind.lower()}#{n}"
    return source_id


def add_source(ledger: dict, kind: str, query: str, run_utc: str, state: str,
               error: str | None, funnel: dict, record_ids, discovery_capable: bool,
               source_id: str | None = None) -> str:
    source_id = source_id or reserve_source_id(ledger, kind)
    source = {
        "source_id": source_id,
        "kind": kind,
        "query": query,
        "run_utc": run_utc,
        "state": state,
        "error": error,
        "discovery_capable": bool(discovery_capable),
        "funnel": funnel,
        "record_ids": _dedupe_strings(record_ids),
    }
    ledger.setdefault("sources", []).append(source)
    return source_id


def attach_records(ledger: dict, source_id: str, ids) -> None:
    for rid in _dedupe_strings(ids):
        row = ledger.setdefault("records", {}).setdefault(rid, {"found_by": []})
        found_by = row.setdefault("found_by", [])
        if source_id not in found_by:
            found_by.append(source_id)


def records_sha256(records_list) -> str:
    return hashlib.sha256(canonical_json(records_list).encode("utf-8")).hexdigest()


def _engine_sha() -> str:
    try:
        proc = subprocess.run(
            ["git", "hash-object", os.path.join("harness", "acquisition.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return proc.stdout.strip() or "unknown"
    except Exception:  # noqa: BLE001 - git is provenance, not a runtime dependency.
        return "unknown"


def finalize(ledger: dict, records_list, retrieved_utc: str, mode: str) -> dict:
    ledger["snapshot"] = {
        "records_sha256": records_sha256(records_list),
        "retrieved_utc": retrieved_utc,
        "mode": mode,
        "engine_sha": _engine_sha(),
        "raw_calls": 0,
    }
    return ledger


def validate(ledger: dict, records_list, snapshot_dir: str | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(ledger, dict):
        return ["ledger is not a dict"]
    if ledger.get("version") != LEDGER_VERSION:
        errors.append(f"version is not {LEDGER_VERSION}")
    sources = ledger.get("sources")
    if not isinstance(sources, list):
        errors.append("sources is not a list")
        sources = []
    records = ledger.get("records")
    if not isinstance(records, dict):
        errors.append("records is not a dict")
        records = {}
    snapshot = ledger.get("snapshot")
    if isinstance(snapshot, dict):
        raw_calls = snapshot.get("raw_calls") or 0
        if raw_calls and snapshot_dir:
            raw_index = os.path.join(snapshot_dir, "raw", "INDEX.json")
            if not os.path.exists(raw_index):
                errors.append("snapshot.raw_calls > 0 but raw/INDEX.json is missing")

    source_ids: set[str] = set()
    for source in sources:
        sid = source.get("source_id")
        if not sid:
            errors.append("source missing source_id")
        elif sid in source_ids:
            errors.append(f"duplicate source_id {sid}")
        else:
            source_ids.add(sid)
        kind = source.get("kind")
        if kind not in SOURCE_KINDS:
            errors.append(f"{sid or '<unknown>'}: unknown kind {kind!r}")
        state = source.get("state")
        if state not in STATES:
            errors.append(f"{sid or '<unknown>'}: unknown state {state!r}")
        if state == "RAN_UNRECORDED" and (ledger.get("snapshot") or {}).get("mode") != "LEGACY_UNRECORDED":
            errors.append(f"{sid or '<unknown>'}: RAN_UNRECORDED is a legacy-only state; a live run must record its yield")
        funnel = source.get("funnel")
        if not isinstance(funnel, dict):
            errors.append(f"{sid or '<unknown>'}: funnel is not a dict")
            funnel = {}
        cap = funnel.get("cap")
        if not isinstance(cap, dict):
            errors.append(f"{sid or '<unknown>'}: cap is not a dict")
            cap = {}
        cap_kind = cap.get("kind")
        if cap_kind not in CAP_KINDS:
            errors.append(f"{sid or '<unknown>'}: unknown cap kind {cap_kind!r}")
        if cap_kind != "none":
            remainder = cap.get("remainder")
            unknown_relevance_remainder = cap_kind == "relevance_top_n" and remainder is None
            if not unknown_relevance_remainder and (not isinstance(remainder, int) or remainder < 0):
                errors.append(f"{sid or '<unknown>'}: cap remainder is not a non-negative int")
        fetched = funnel.get("fetched")
        hits = funnel.get("hits")
        if state == "RAN_ERROR":
            if not source.get("error"):
                errors.append(f"{sid or '<unknown>'}: RAN_ERROR without error")
            if fetched != 0:
                errors.append(f"{sid or '<unknown>'}: RAN_ERROR with fetched={fetched!r}")
        if state == "RAN_ZERO":
            if source.get("error") is not None:
                errors.append(f"{sid or '<unknown>'}: RAN_ZERO with error")
            if hits != 0:
                errors.append(f"{sid or '<unknown>'}: RAN_ZERO with hits={hits!r}")

    for rid, row in records.items():
        found_by = (row or {}).get("found_by") if isinstance(row, dict) else None
        if not found_by:
            errors.append(f"ledger record {rid} has no found_by")
            continue
        for sid in found_by:
            if sid not in source_ids:
                errors.append(f"ledger record {rid} names unknown source_id {sid}")

    for record in records_list or []:
        rid = str(record.get("id")) if isinstance(record, dict) else str(record)
        found_by = (records.get(rid) or {}).get("found_by") if rid in records else None
        if not found_by:
            errors.append(f"orphan record {rid}")
            continue
        for sid in found_by:
            if sid not in source_ids:
                errors.append(f"record {rid} names unknown source_id {sid}")
    return errors


def load_ledger(slug: str, root: str = ROOT) -> dict | None:
    path = os.path.join(root, "cache", slug, LEDGER_FILENAME)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _records_without_ledger(records_dict: dict) -> dict:
    out = dict(records_dict)
    out.pop("retrieval_ledger", None)
    out.pop("_raw_recorder", None)
    out.pop("_raw_calls", None)
    return out


def write_snapshot(slug: str, records_dict: dict, ledger: dict, root: str = ROOT) -> str:
    snapshot = ledger.get("snapshot") or {}
    retrieved_utc = snapshot.get("retrieved_utc")
    sha = snapshot.get("records_sha256")
    if not retrieved_utc or not sha:
        raise ValueError("ledger must be finalized before writing a snapshot")
    snapshot_dir = os.path.join(root, "cache", slug, SNAPSHOT_DIRNAME, f"{retrieved_utc}-{sha[:8]}")
    os.makedirs(snapshot_dir, exist_ok=True)
    raw_recorder = records_dict.get("_raw_recorder")
    if isinstance(raw_recorder, RawRecorder):
        raw_calls, raw_index_sha = raw_recorder.write_snapshot(snapshot_dir)
    else:
        raw_calls, raw_index_sha = 0, None
    ledger.setdefault("snapshot", {})["raw_calls"] = raw_calls
    if raw_index_sha:
        ledger["snapshot"]["raw_index_sha256"] = raw_index_sha
    else:
        ledger["snapshot"].pop("raw_index_sha256", None)
    clean_records = _records_without_ledger(records_dict)
    with open(os.path.join(snapshot_dir, "records.json"), "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(clean_records, ensure_ascii=False, indent=2))
    with open(os.path.join(snapshot_dir, LEDGER_FILENAME), "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(ledger, ensure_ascii=False, indent=2))
    return snapshot_dir


def pin(slug: str, snapshot_dir: str, root: str = ROOT) -> None:
    src_dir = snapshot_dir if os.path.isabs(snapshot_dir) else os.path.join(root, snapshot_dir)
    dst_dir = os.path.join(root, "cache", slug)
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copyfile(os.path.join(src_dir, "records.json"), os.path.join(dst_dir, "records.json"))
    shutil.copyfile(os.path.join(src_dir, LEDGER_FILENAME), os.path.join(dst_dir, LEDGER_FILENAME))


def refresh(config: dict, now: str, root: str = ROOT) -> str:
    from . import fetch  # local import keeps fetch.run free to use this module.

    data = fetch.run(dict(config, _now=now))
    ledger = data.get("retrieval_ledger")
    if not isinstance(ledger, dict):
        raise ValueError("fetch.run did not return retrieval_ledger")
    violations = validate(ledger, data.get("records", []))
    if violations:
        raise ValueError("invalid retrieval ledger: " + "; ".join(violations))
    snapshot_dir = write_snapshot(config["slug"], data, ledger, root=root)
    violations = validate(ledger, data.get("records", []), snapshot_dir=snapshot_dir)
    if violations:
        raise ValueError("invalid retrieval snapshot: " + "; ".join(violations))
    return snapshot_dir
