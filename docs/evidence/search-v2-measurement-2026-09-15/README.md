# Search v2 measurement (2026-09-15)

**Fix state (orthogonal fields rule): LANDED / NONE / CORPUS / STALE** - generated from MEASURE-search-v2-recall-2026-09-15; stale dependencies: docs/evidence/CAPTIONS.json, docs/search_recall_regression_corpus.json

3 runs of the engine on the same sealed benchmark, scored by the same scorer. Run 1 (lane S3) is kept
exactly as sealed; every later run follows the guard protocol (docs/evidence/search-v2-guard-2026-09-15/PROTOCOL.md,
RETROSPECTIVE) and is written beside the earlier ones. No run replaces another.

## Run 1 (engine blob 3652170, snapshot 2026-09-15-search_v2)

MEASUREMENT topics (21, sealed before the engine existed): audit-found positives found 1 of 12 (named); pooled-or-declared positives found 120 of 135; 5 of 21 topics RAN_ERROR (the engine refused its own query; contribute 0 found, counted in N); sealed regression register 18 of 20 -- measured with the LEGACY concept-query engine (harness/acquisition.py, re-run because that file changed), NOT with search_v2, which has not been run against the sealed register; development topics excluded

## Run r2 (engine blob 9cf898d02afbde097aca72405f1baffe3124c13b, snapshot 2026-09-15r2-search_v2, registries ['ctgov'])

MEASUREMENT topics (21, sealed before the engine existed), run r2 (engine 9cf898d02afb, snapshot 2026-09-15r2-search_v2, guard protocol registered at 8d7cf8fc66ef): audit-found positives found 1 of 12 (named); pooled-or-declared positives found 135 of 135; topic states: RAN_OK 0 of 21; RAN_OK_WITH_SOURCE_ERRORS 21 of 21; RAN_ZERO 0 of 21; RAN_ERROR 0 of 21; NOT_RUN 0 of 21; source-level RAN_ERROR 163 of 837 sources across the 21; sealed regression register ON search_v2: within kind (PubMed concept query alone) 19 of 20 over 5 of 5 topics, whole engine 20 of 20 over 5 of 5 topics; development topics excluded

## Run r3 (engine blob a57dc45d68249c71ac2cf4a8319c53c8a1259d20, snapshot 2026-09-15r3-search_v2, registries ['ctgov', 'isrctn'])

MEASUREMENT topics (21, sealed before the engine existed), run r3 (engine a57dc45d6824, snapshot 2026-09-15r3-search_v2, guard protocol registered at 8d7cf8fc66ef): audit-found positives found 1 of 12 (named); pooled-or-declared positives found 135 of 135; topic states: RAN_OK 0 of 21; RAN_OK_WITH_SOURCE_ERRORS 21 of 21; RAN_ZERO 0 of 21; RAN_ERROR 0 of 21; NOT_RUN 0 of 21; source-level RAN_ERROR 164 of 847 sources across the 21; sealed regression register ON search_v2: within kind (PubMed concept query alone) 15 of 16 over 4 of 5 topics, whole engine 20 of 20 over 5 of 5 topics; development topics excluded

Snapshots are unpinned and written beside the pinned caches; served review pages and pools were not moved.

Captures (run 1):
- `01-recall-21.txt`: per-topic recall table with every benchmark-positive name.
- `02-routes.txt`: route attribution for every found positive.
- `03-misses-diagnosed.txt`: source-presence and emitted-query diagnostics for every missed positive.
- `04-heldout-register.txt`: sealed/register measurement summary without plaintext rows (LEGACY engine).
- `05-reverse-direction.txt`: candidate counts not in the benchmark by topic and route.

Captures (run r2):
- `06-run-r2-states.txt`: the five topic states on all 32 topics, source errors by kind, raw-archive custody.
- `07-recall-21-r2.txt`: per-positive FOUND/MISSED beside run 1.
- `08-routes-r2.txt`: route attribution and unique-route contribution.
- `09-register-search-v2-r2.txt`: the sealed register ON search_v2, within kind and whole engine, beside legacy.
- `10-reverse-direction-r2.txt`: candidates not in the benchmark.
- `11-before-after-32-r2.txt`: pinned legacy cache vs run r2 on all 32 topics.

Captures (run r3):
- `06-run-r3-states.txt`: the five topic states on all 32 topics, source errors by kind, raw-archive custody.
- `07-recall-21-r3.txt`: per-positive FOUND/MISSED beside run 1.
- `08-routes-r3.txt`: route attribution and unique-route contribution.
- `09-register-search-v2-r3.txt`: the sealed register ON search_v2, within kind and whole engine, beside legacy.
- `10-reverse-direction-r3.txt`: candidates not in the benchmark.
- `11-before-after-32-r3.txt`: pinned legacy cache vs run r3 on all 32 topics.
