# Legacy ledgers for the 32 pre-ledger topics + raw external inputs preserved (2026-09-14)

**Fix state (four-state rule): LANDED, author-demonstrated; NOT independently VERIFIED; NOT GENERALIZED.**

| file | what it is |
|---|---|
| `01-regeneration-with-legacy-ledgers.txt` | the 32 pages rebuilt after `scripts/write_legacy_ledgers.py` wrote an explicit `LEGACY_UNRECORDED` ledger per topic; per-key comparison shows only acquisition-provenance keys (and the retrieval-class basis listing) changed; no primary result moved; every page renders the snapshot mode, the REPLAY sentence, a `found by` column and `hits: unknown` |

What the legacy ledger asserts and refuses to assert: every record was retrieved by a pre-ledger fetch whose per-query
yield was never recorded. Each committed query is a source in state `RAN_UNRECORDED` (attempted, yield unknown — a
legacy-only state that `validate()` refuses on any live snapshot); one `LEGACY_UNRECORDED` source carries every record's
`found_by`. Nothing says which query found which record, because nothing knows.

Raw external inputs: from this commit every live fetch records each HTTP call (URL, params, status, body bytes, timestamp,
adapter identity and blob sha) under `raw/` beside the snapshot, indexed and hashed; legacy snapshots carry `raw_calls: 0`.
