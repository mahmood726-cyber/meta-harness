# Signing packet v4 — 2026-10-03 (acq/k-gap G1 integration: 2 notices)

Every block below is the FULL visible text of a result-change notice as the review page renders it, headed by the full `rendered_sha256` a signature on it will name. Nothing elided. Split by the harness's own `conclusion_changed` annotation: a changed or withdrawn conclusion takes its own line.

Built from branch integrate/k-gap-2026-10-02 (not yet on main). Every hash recomputed from that tree by the page's own renderer; the guard must pass again on the landing tree before any signature is recorded. Signed notices on main: 17, carried unchanged; none is re-presented. Note on V4-02: the derived reason's generic substitution sentence calls the old semaglutide numbers 'the WRONG QUANTITY'; the actual change is published mean differences replacing arm-reconstructed ones -- read it with that in mind.

## A. BATCHABLE — 2 decision(s), one signature line → `BATCH_SEEN_AND_SIGNED`

### V4-01 — probiotics-aad-prevention / Antibiotic-associated diarrhoea

`rendered_sha256 081df1361b93ef93781b57a276e02ab0624812cbb662f9be107d9e0b94bfb620`

Antibiotic-associated diarrhoea: the pooled result changed on 2026-10-02. Previously served: k = 12, 0.63 (0.45 to 0.89). Now: k = 13, 0.62 (0.45 to 0.85). The direction of the estimate is unchanged. Entered the pool: PMID 17604300. Why: PMID 17604300 entered the pool contributing RR 0.362, reconstructed from 7/57 vs 19/56 (source abstract). PMID 7872284 stayed in the pool but now contributes a different number: RR 0.29 (0.08 to 0.98) -> RR 0.4948, reconstructed from 7/97 vs 14/96 (estimator selection PUBLISHED_EFFECT_TARGET_CLASS -> KEEP_RECONSTRUCTION_NO_TARGET_PUBLISHED_EFFECT; source reported -> reconstructed). Entering trials are new evidence, not a correction: the previously served number is not asserted wrong; it was computed without the held document(s) this topic now admits to pool construction. This is not a set-aside: the previously served number was the WRONG QUANTITY for this outcome, and is asserted wrong. The trial stays in the pool and contributes the quantity the outcome declares, read from the same held document. — Claude Opus 5.5 (captain lane, integrate/k-gap-2026-10-02); reviewer countersignature owed: Mahmood.

### V4-02 — semaglutide-obesity-weight / Percent change in body weight

`rendered_sha256 dc09b3061cce54117106f5f66a15620099664dfdd4e41416aaab41496c611961`

Percent change in body weight: the pooled result changed on 2026-10-02. Previously served: k = 2, -11.84 (interval not served: refused at k = 2, K2_SINGLE_DF). Now: k = 2, -11.47 (interval not served: refused at k = 2, K2_SINGLE_DF). The direction of the estimate is unchanged. Why: PMID 33567185 stayed in the pool but now contributes a different number: MD -12.8 -> MD -12.4 (-13.4 to -11.5) (estimator selection KEEP_RECONSTRUCTION_NO_TARGET_PUBLISHED_EFFECT -> KEEP_REPORTED_EFFECT; source reconstructed -> reported). PMID 33625476 stayed in the pool but now contributes a different number: MD -10.7 -> MD -10.3 (-12.0 to -8.6) (estimator selection KEEP_RECONSTRUCTION_NO_TARGET_PUBLISHED_EFFECT -> KEEP_REPORTED_EFFECT; source reconstructed -> reported). PMID 40544433 refused on evidence: contrast mismatch: the pooled row's source names another active agent 'cagrilintide' (a protocol arm-name term) -- not the registered intervention-vs-comparator contrast; declared absent, never pooled. NCT04074161 refused on evidence: source-visible value was not pooled; recorded as extraction debt / typed refusal, not as absence. This is not a set-aside: the previously served number was the WRONG QUANTITY for this outcome, and is asserted wrong. The trial stays in the pool and contributes the quantity the outcome declares, read from the same held document. — Claude Opus 5.5 (captain lane, integrate/k-gap-2026-10-02); reviewer countersignature owed: Mahmood.

```
SIGNED-BY: Mahmood  BATCH: v4-A  COVERS: V4-01, V4-02  DATE: ____
```

## B. INDIVIDUAL — 0 decision(s), each its own line → `SEEN_AND_SIGNED`
