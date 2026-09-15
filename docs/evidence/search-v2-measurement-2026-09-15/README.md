# Search v2 measurement (2026-09-15)

**Fix state (orthogonal fields rule): LANDED / NONE / CORPUS / STALE** - generated from MEASURE-search-v2-recall-2026-09-15; stale dependencies: docs/evidence/CAPTIONS.json, docs/search_recall_regression_corpus.json, harness/acquisition.py, +2 more

MEASUREMENT topics (21, sealed before the engine existed): audit-found positives found 1 of 12 (named); pooled-or-declared positives found 120 of 135; 5 of 21 topics RAN_ERROR (the engine refused its own query; contribute 0 found, counted in N); sealed regression register 18 of 20 -- measured with the LEGACY concept-query engine (harness/acquisition.py, re-run because that file changed), NOT with search_v2, which has not been run against the sealed register; development topics excluded

This bundle measures the frozen search_v2 engine on the 21 sealed MEASUREMENT topics only.
Development topics are excluded from the capability number.
Snapshots are unpinned and written beside the pinned caches; served review pages and pools were not moved.

Captures:
- `01-recall-21.txt`: per-topic recall table with every benchmark-positive name.
- `02-routes.txt`: route attribution for every found positive.
- `03-misses-diagnosed.txt`: source-presence and emitted-query diagnostics for every missed positive.
- `04-heldout-register.txt`: sealed/register measurement summary without plaintext rows.
- `05-reverse-direction.txt`: candidate counts not in the benchmark by topic and route.
