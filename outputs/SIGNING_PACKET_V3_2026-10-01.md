# Signing packet v3 — 2026-10-01

Every block below is the FULL visible text of a result-change notice as the review page renders it, headed by the full `rendered_sha256` a signature on it will name. Nothing elided. Split by the harness's own `conclusion_changed` annotation: a changed or withdrawn conclusion takes its own line.

Built from branch captain/table-role-guard (not yet on main). Every hash recomputed from that tree by the page's own renderer; the guard (scripts/signing_packet.py guard) must pass again at the landed main commit before any signature is recorded. Signed notices on main: 13, all carried unchanged; none is re-presented here.

## A. BATCHABLE — 2 decision(s), one signature line → `BATCH_SEEN_AND_SIGNED`

### V3-01 — omega3-cardiovascular-events / Major vascular events / MACE

`rendered_sha256 07c8fd020dc05fc5a68921075e9c6e1912e15941dae52d0f328406a09197eb9f`

Major vascular events / MACE: the pooled result changed on 2026-10-01. Previously served: k = 5, 0.94 (0.77 to 1.14). Now: k = 6, 0.94 (0.80 to 1.10). The direction of the estimate is unchanged. Entered the pool: PMID 38199870. Why: PMID 38199870 entered the pool contributing HR 1.0 (0.64 to 1.56) (source pmc_fulltext from its committed held full text). The source reports this estimate as covariate-adjusted: "risk of MACE: omega-3 versus no omega-3 (adjusted hazard ratio (aHR) = 1.00, 95% CI 0.64–1.56), nor vitamin". The source reports this estimate as an exploratory endpoint: "2.2.2 Major cardiovascular events Incident major CVD events (MACE) were an exploratory endpoint of DO-HEALTH and used as a composite (any of the events) individual endpoint and included myocardial infarction, stroke, procedures leading to coronary revascularization, incident congestive heart disease". Entering trials are new evidence, not a correction: the previously served number is not asserted wrong; it was computed without the held document(s) this topic now admits to pool construction. — Claude Opus 5.5 (captain lane, captain/table-role-guard); reviewer countersignature owed: Mahmood.

### V3-02 — probiotics-aad-prevention / Antibiotic-associated diarrhoea

`rendered_sha256 e842eba1a95efd8689f9f95934a30a2595a6d15a78b95f787f512584a0f7c0ee`

Antibiotic-associated diarrhoea: the pooled result changed on 2026-10-01. Previously served: k = 11, 0.69 (0.48 to 0.98). Now: k = 12, 0.63 (0.45 to 0.89). The direction of the estimate is unchanged. Entered the pool: PMID 39529939. Why: PMID 39529939 entered the pool contributing RR 0.36 (0.24 to 0.55) (source pmc_fulltext_effect from its committed held full text). PMID 39497860 refused on evidence: the effect was read from an uncaptioned table whose header is 'Characteristic' and whose rows are patient demographics (a baseline table reports arm composition, not outcome events); a number from such a table is not an effect. Entering trials are new evidence, not a correction: the previously served number is not asserted wrong; it was computed without the held document(s) this topic now admits to pool construction. — Claude Opus 5.5 (captain lane, captain/table-role-guard); reviewer countersignature owed: Mahmood.

```
SIGNED-BY: Mahmood  BATCH: v3-A  COVERS: V3-01, V3-02  DATE: ____
```

## B. INDIVIDUAL — 1 decision(s), each its own line → `SEEN_AND_SIGNED`

### V3-03 — spironolactone-hfref-mortality / All-cause mortality

**Cannot be batched:** the interval now includes the null: the previous conclusion of a difference is withdrawn

`rendered_sha256 6750c0743295145de268453d3f17fe323faabfea05ead4a331bc5f4fc74188a4`

All-cause mortality: the pooled result changed on 2026-10-01. Previously served: k = 3, 0.73 (0.56 to 0.95). Now: k = 3, 0.88 (0.29 to 2.63). Conclusion withdrawn: the interval now includes the null: the previous conclusion of a difference is withdrawn. Why: PMID 28824029 stayed in the pool but now contributes a different number: HR 0.85 (0.53 to 1.36) -> HR 1.77 (0.81 to 3.87) (estimator selection PUBLISHED_EFFECT_TARGET_CLASS -> PUBLISHED_EFFECT_TARGET_CLASS; source reported -> reported). The previously contributed candidate is no longer eligible: the sentence names its endpoint only as 'primary endpoint', which this document defines as a composite of cardiovascular death, heart failure hospitalization; the declared outcome 'All-cause mortality' is a single component, so this is a different quantity. This is not a set-aside: the previously served number was the WRONG QUANTITY for this outcome, and is asserted wrong. The trial stays in the pool and contributes the quantity the outcome declares, read from the same held document. — Claude Opus 5.5 (captain lane, captain/table-role-guard); reviewer countersignature owed: Mahmood.

```
SIGNED-BY: Mahmood  NOTICE: V3-03  SHA256: 6750c0743295145de268453d3f17fe323faabfea05ead4a331bc5f4fc74188a4  DATE: ____
```
