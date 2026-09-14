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
  cache/<slug>/snapshots/<retrieved_utc>-<sha8>/  refresh outputs: records.json + retrieval_ledger.json

LEDGER SCHEMA (version 1)
  {
    "version": 1, "slug": "<slug>",
    "snapshot": {"records_sha256": "<sha256 of canonical_json(records list)>", "retrieved_utc": "YYYY-MM-DD",
                 "mode": "REFRESH" | "LEGACY_UNRECORDED", "engine_sha": "<git blob sha of harness/acquisition.py>"},
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

LEDGER_VERSION = 1

STATES = ("RAN_OK", "RAN_ZERO", "RAN_ERROR", "NOT_RUN")
SNAPSHOT_MODES = ("REFRESH", "LEGACY_UNRECORDED")
SOURCE_KINDS = (
    "PUBMED_CONCEPT_QUERY",      # built from the registered P/I/C/design; paginated full boolean set
    "PUBMED_LEGACY_QUERY",       # a committed pubmed_queries string that is a real query (not an enumeration)
    "PUBMED_PMID_ENUMERATION",   # a <uid>[uid] list: retrieves only what it was told; discovery_capable=false
    "EUROPEPMC_QUERY",
    "COMPARATOR_REFERENCES",     # reference list of the comparator meta-analysis (seeding)
    "CITATION_CHASE",
    "REGISTRY_FIRST",            # condition x intervention enumeration on ClinicalTrials.gov/AACT -> PMIDs
    "CTGOV_SEARCH",
    "EXTRA_PMIDS",               # config.extra_pmids: hand-named, discovery_capable=false
    "CONTROL_PMIDS",             # positive/negative controls and the comparator itself
    "MODEL_CALL",                # a model asked to find/recover a trial: query = the verbatim prompt
)
CAP_KINDS = ("none", "relevance_top_n", "record_cap", "hard_hits_cap")

LEDGER_FILENAME = "retrieval_ledger.json"
SNAPSHOT_DIRNAME = "snapshots"

# Implementation lands in this file (refresh / pin / load_ledger / concept_query / esearch_all / validate).
