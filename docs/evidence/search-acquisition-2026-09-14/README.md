# Acquisition layer - retrieval ledger, four run states, pagination, concept source, regression-corpus recall (2026-09-14)

**Fix state (orthogonal fields rule): LANDED / INTERNAL / INSTANCE / CURRENT** - generated from TRANCHE-acquisition-layer; verified by Codex lane G (internal_agent); evidence: docs/evidence/independent-verification-2026-09-14/10-acquisition-prefix-defect.txt

| file | what it is |
|---|---|
| `01-prefix-fetch-defects.txt` | offline demonstration on the old fetch: 40 of 764 hits fetched with no remainder recorded; a Europe PMC failure written as RAN_OK; no per-record provenance |
| `02-heldout-selection.txt` | the mechanical selection of the five zero-contact topics (later disqualified as held-out by the auditor; they are the regression-recall set) |
| `03-prefix-heldout-unenforced.txt` | a held-out slug in a test file passed the whole standard |
| `04-heldout-recall-measurement.txt` | 18 of 20 known-eligible trials recalled unaided on the five topics (now labelled regression-corpus recall) |
| `05-postfix-heldout-refusals.txt` | commit message / test file / engine-edit-without-measurement refusals (first, plaintext design) |
| `06-concept-source-plant-fires-prefix.txt` | the concept query was classified but never run by lane A; plant failed pre-fix, passes post-fix |
| `07-live-refresh-postfix.txt` | a live REFRESH: concept source 165/165, Europe PMC top-40 disclosed (remainder 589), 521 records all with found_by, pinned records untouched |
