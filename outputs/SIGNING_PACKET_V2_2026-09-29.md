# Signing packet v2 — 2026-09-29

Replaces v1. v1 named JSON-object digests; a signature names the **rendered block** the reviewer
reads (`rendered_sha256`, recomputed by the gate from the served review object). v1 also presented
everything as one batch; the harness refuses a batch signature over a withdrawn conclusion, and 8
of these 13 are in that class. v1's MAIN-14 (spironolactone) is gone: no derived notice exists for
it, so there is nothing to countersign until the binding lands.

Base: `91f057a4` (main, reproduces 32 of 32). Every hash recomputed from that tree. Each block
below is the FULL visible text of the notice as the review page renders it — nothing elided.

## A. BATCHABLE — 5 decisions, one signature line → `BATCH_SEEN_AND_SIGNED`

### MAIN-03 — dpp4-mace-t2d / Hospitalization for heart failure

`rendered_sha256 eb1fe986638139d90275062fa796eecf5fa3d68aa497ae59a3c6757d178c5fa0`

Result changed Hospitalization for heart failure: the pooled result changed on 2026-09-20. Previously served: k = 2, 1.13 (interval not served: refused at k = 2, K2_SINGLE_DF). Now: k = 1, 1.00 (0.83 to 1.20). The direction of the estimate is unchanged. Left the pool: PMID 23992601. Why: PMID 23992601 set aside (ENDPOINT_UNBOUND): span names neither components nor an endpoint. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong. — Claude Opus 5 (lane m2/bind-hand-rows, 2026-09-20); reviewer countersignature owed: Mahmood.

### MAIN-06 — omega3-cardiovascular-events / Major vascular events / MACE

`rendered_sha256 1eab7c820e4c47b06aab567147890f2c343088be2a33aee8f63f4af3f983ecaa`

Result changed Major vascular events / MACE: the pooled result changed on 2026-09-21. Previously served: k = 6, 0.95 (0.82 to 1.10). Now: k = 5, 0.94 (0.77 to 1.14). The direction of the estimate is unchanged. Left the pool: PMID 22686415. Why: PMID 22686415 set aside (ENDPOINT_UNBOUND): named endpoint has no definition span in the held text. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong. — Claude Opus 5 (lane m2/bind-hand-rows); reviewer countersignature owed: Mahmood.

### MAIN-07 — pcsk9-mace / Major adverse cardiovascular events

`rendered_sha256 e198a89b1ac6594f7f59177ee021472e0a2a7f67ae93746b483f7dc3fe0ada94`

Result changed Major adverse cardiovascular events: the pooled result changed on 2026-09-20. Previously served: k = 3, 0.81 (0.70 to 0.93). Now: k = 2, 0.83 (interval not served: refused at k = 2, K2_SINGLE_DF). The direction of the estimate is unchanged. Left the pool: PMID 41211925. Why: PMID 41211925 set aside (ENDPOINT_UNBOUND): result sentence names an endpoint but the held text holds 2 different definitions of it. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong. — Claude Opus 5 (lane m2/bind-hand-rows, 2026-09-20); reviewer countersignature owed: Mahmood.

### MAIN-09 — probiotics-aad-prevention / Antibiotic-associated diarrhoea

`rendered_sha256 f6938296ae3277ee649b21669a11a0d8d54f892a6b99d5584ba3a8c347cd2064`

Result changed Antibiotic-associated diarrhoea: the pooled result changed on 2026-09-20. Previously served: k = 16, 0.69 (0.52 to 0.92). Now: k = 11, 0.69 (0.48 to 0.98). The direction of the estimate is unchanged. Left the pool: PMID 24456384, PMID 26973849, PMID 34541475, PMID 39529939, PMID 40488914. Why: PMID 24456384 set aside (ENDPOINT_UNBOUND): tuple not located in the held document cache/probiotics-aad-prevention/records.json#PMID-24456384 (abstract): no span carries it. PMID 26973849 set aside (ENDPOINT_UNBOUND): tuple not located in the held document cache/probiotics-aad-prevention/ft_26973849.txt (xml): no span carries it. PMID 34541475 set aside (ENDPOINT_UNBOUND): table label 'AAD – Abx+30d (n, %)' names an endpoint but the held text holds no definition span carrying its words. PMID 39529939 set aside (ENDPOINT_UNBOUND): tuple located in 2 spans of the held document; ambiguity abstains. PMID 40488914 refused (RESULT_INCOMPATIBLE): the bound endpoint span defines a different outcome from 'Antibiotic-associated diarrhoea'. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong. — Claude Opus 5 (lane m2/bind-hand-rows, 2026-09-20); reviewer countersignature owed: Mahmood.

### MAIN-12 — tocilizumab-covid19-mortality / Serious adverse events

`rendered_sha256 1ea7d1ddf291af37beed43dbdd7cd94d991da649bac610943c1323fbaacca5a4`

Result changed Serious adverse events: the pooled result changed on 2026-09-20. Previously served: k = 3, 0.87 (0.45 to 1.69). Now: k = 2, 0.81 (interval not served: refused at k = 2, K2_SINGLE_DF). The direction of the estimate is unchanged. Left the pool: PMID 33085857. Why: PMID 33085857 set aside (ENDPOINT_UNBOUND): tuple not located in the held document cache/tocilizumab-covid19-mortality/ft_33085857.txt (xml): no span carries it. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong. — Claude Opus 5 (lane m2/bind-hand-rows, 2026-09-20); reviewer countersignature owed: Mahmood.

```
SIGNED-BY: Mahmood  BATCH: v2-A-2026-09-29  COVERS: MAIN-03, MAIN-06, MAIN-07, MAIN-09, MAIN-12  DATE: ____
```

## B. INDIVIDUAL — 8 decisions, each its own line → `SEEN_AND_SIGNED`

### MAIN-01 — colchicine-postop-af / Treatment discontinuation

**Cannot be batched:** the outcome no longer has a pooled estimate

`rendered_sha256 1328cf01b62b4446ee4b0982e4aad3cf90fb3ee48cf2e8fa17d6e15355e5d39b`

Result changed Treatment discontinuation: the pooled result changed on 2026-09-20. Previously served: k = 1, 0.88 (0.06 to 13.76). Now: no pooled estimate (k = 0). Conclusion withdrawn: the outcome no longer has a pooled estimate. Left the pool: PMID 32720823. Why: PMID 32720823 set aside (ENDPOINT_UNBOUND): tuple located in 3 spans of the held document; ambiguity abstains. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong. — Claude Opus 5 (lane m2/bind-hand-rows, 2026-09-20); reviewer countersignature owed: Mahmood.

```
SIGNED-BY: Mahmood  NOTICE: MAIN-01  SHA256: 1328cf01b62b4446ee4b0982e4aad3cf90fb3ee48cf2e8fa17d6e15355e5d39b  DATE: ____
```

### MAIN-02 — colchicine-recurrent-pericarditis / Adverse events (gastrointestinal)

**Cannot be batched:** the outcome no longer has a pooled estimate

`rendered_sha256 a570ad242b5c313f64a880e6e2fdbfc50861a51b88ddf3bf4a6c2e557974ce09`

Result changed Adverse events (gastrointestinal): the pooled result changed on 2026-09-20. Previously served: k = 1, 1.00 (0.41 to 2.43). Now: no pooled estimate (k = 0). Conclusion withdrawn: the outcome no longer has a pooled estimate. Left the pool: PMID 24694983. Why: PMID 24694983 set aside (ENDPOINT_UNBOUND): tuple not located in the held document cache/colchicine-recurrent-pericarditis/records.json#PMID-24694983 (abstract): no span carries it. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong. — Claude Opus 5 (lane m2/bind-hand-rows, 2026-09-20); reviewer countersignature owed: Mahmood.

```
SIGNED-BY: Mahmood  NOTICE: MAIN-02  SHA256: a570ad242b5c313f64a880e6e2fdbfc50861a51b88ddf3bf4a6c2e557974ce09  DATE: ____
```

### MAIN-04 — esketamine-trd-madrs / Observed-case Day-28 raw change-score MADRS MD

**Cannot be batched:** the interval now includes the null: the previous conclusion of a difference is withdrawn

`rendered_sha256 e2b6ca01798b4c64b83f33060c10bcddea787324459ff8afbef490da459d56c5`

Result changed Observed-case Day-28 raw change-score MADRS MD: the pooled result changed on 2026-09-20. Previously served: k = 4, -3.34 (-6.07 to -0.62). Now: k = 3, -3.10 (-7.33 to 1.13). Conclusion withdrawn: the interval now includes the null: the previous conclusion of a difference is withdrawn. Left the pool: NCT02417064. Why: NCT02417064 (TRANSFORM-1) left the pool: its hand-transcribed combined-dose-arm values (mean, SD, n versus the shared placebo arm) are not located in the held record for the trial, so the binder set the row aside as KNOWN_REPORTED_NOT_YET_EXTRACTED (the trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong). The remaining three trials re-pool to a mean difference whose interval includes zero. — Claude Opus 5 (lane m2/bind-hand-rows, 2026-09-20); reviewer countersignature owed: Mahmood.

```
SIGNED-BY: Mahmood  NOTICE: MAIN-04  SHA256: e2b6ca01798b4c64b83f33060c10bcddea787324459ff8afbef490da459d56c5  DATE: ____
```

### MAIN-05 — noac-vs-warfarin-af-stroke / Major bleeding

**Cannot be batched:** the outcome no longer has a pooled estimate

`rendered_sha256 6e437ce1b28becfa52c928ef9a7eb57532416a656fe9aeb52adae977d1775858`

Result changed Major bleeding: the pooled result changed on 2026-09-20. Previously served: k = 4, 0.85 (0.64 to 1.13). Now: no pooled estimate (k = 0). Conclusion withdrawn: the outcome no longer has a pooled estimate. Left the pool: PMID 19717844, PMID 21830957. Why: PMID 19717844 set aside (ENDPOINT_UNBOUND): tuple not located in the held document cache/noac-vs-warfarin-af-stroke/records.json#PMID-19717844 (abstract): no span carries it. PMID 21830957 set aside (ENDPOINT_UNBOUND): tuple not located in the held document cache/noac-vs-warfarin-af-stroke/records.json#PMID-21830957 (abstract): no span carries it. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong. — Claude Opus 5 (lane m2/bind-hand-rows, 2026-09-20); reviewer countersignature owed: Mahmood.

```
SIGNED-BY: Mahmood  NOTICE: MAIN-05  SHA256: 6e437ce1b28becfa52c928ef9a7eb57532416a656fe9aeb52adae977d1775858  DATE: ____
```

### MAIN-08 — pcsk9-mace / Injection-site reactions

**Cannot be batched:** the outcome no longer has a pooled estimate

`rendered_sha256 4aa3fbcea446392bc5e4dd0cc029214863ae8145f83e4b6cafafa790affa2b79`

Result changed Injection-site reactions: the pooled result changed on 2026-09-20. Previously served: k = 1, 1.40 (0.95 to 2.07). Now: no pooled estimate (k = 0). Conclusion withdrawn: the outcome no longer has a pooled estimate. Left the pool: PMID 25773378. Why: PMID 25773378 set aside (ENDPOINT_UNBOUND) -- a STALE APPROVAL caught by digest, not a number that could not be found: the entry's approval was recorded against the held registry document cache/pcsk9-mace/harms_aact_held.json at sha256 108efeb5ed7e…, and that document now has sha256 142c68c1dd5a…; whatever was approved was approved against bytes that have since changed, so the approval no longer certifies this number and the row is set aside until it is re-approved against the current document (the same class as attack W5a in the battery, occurring naturally in the corpus). Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong. — Claude Opus 5 (lane m2/bind-hand-rows, 2026-09-20); reviewer countersignature owed: Mahmood.

```
SIGNED-BY: Mahmood  NOTICE: MAIN-08  SHA256: 4aa3fbcea446392bc5e4dd0cc029214863ae8145f83e4b6cafafa790affa2b79  DATE: ____
```

### MAIN-10 — probiotics-aad-prevention / Any adverse events

**Cannot be batched:** the outcome no longer has a pooled estimate

`rendered_sha256 f3acc4c89e1a73f9a47a0ee453a68034e3b143375e52dedbc1e0fd9fbf1e90cb`

Result changed Any adverse events: the pooled result changed on 2026-09-20. Previously served: k = 3, 1.05 (0.56 to 1.97). Now: k = 2, no pooled estimate (pool refused at k = 2, DIRECTION_CONFLICT_K2: k=2 pooled row refused because point estimates are on opposite sides of the null). Conclusion withdrawn: the outcome no longer has a pooled estimate. Left the pool: PMID 26973849. Why: PMID 26973849 set aside (ENDPOINT_UNBOUND): tuple not located in the held document cache/probiotics-aad-prevention/ft_26973849.txt (xml): no span carries it. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong. — Claude Opus 5 (lane m2/bind-hand-rows, 2026-09-20); reviewer countersignature owed: Mahmood.

```
SIGNED-BY: Mahmood  NOTICE: MAIN-10  SHA256: f3acc4c89e1a73f9a47a0ee453a68034e3b143375e52dedbc1e0fd9fbf1e90cb  DATE: ____
```

### MAIN-11 — probiotics-aad-prevention / Serious adverse events

**Cannot be batched:** a pooled estimate is now served where none was served before: a new claim, not a continuation

`rendered_sha256 35cb7440a3a7ecb0dfb6201a24359f67017a067f1ac83025593b8e42636f4eed`

Result changed Serious adverse events: the pooled result changed on 2026-09-20. Previously served: k = 2, no pooled estimate (pool refused at k = 2, DIRECTION_CONFLICT_K2: k=2 pooled row refused because point estimates are on opposite sides of the null). Now: k = 1, 0.66 (0.19 to 2.28). Conclusion changed: a pooled estimate is now served where none was served before: a new claim, not a continuation. Left the pool: PMID 39529939. Why: PMID 39529939 set aside (ENDPOINT_UNBOUND): tuple located in 9 spans of the held document; ambiguity abstains. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong. — Claude Opus 5 (lane m2/bind-hand-rows, 2026-09-20); reviewer countersignature owed: Mahmood.

```
SIGNED-BY: Mahmood  NOTICE: MAIN-11  SHA256: 35cb7440a3a7ecb0dfb6201a24359f67017a067f1ac83025593b8e42636f4eed  DATE: ____
```

### MAIN-13 — tranexamic-acid-pph / Thromboembolic events

**Cannot be batched:** the outcome no longer has a pooled estimate

`rendered_sha256 bffe51380555a1e9549e214033f2bc812ca978196f442b61f6b89c6227d34108`

Result changed Thromboembolic events: the pooled result changed on 2026-09-20. Previously served: k = 1, 0.88 (0.54 to 1.43). Now: no pooled estimate (k = 0). Conclusion withdrawn: the outcome no longer has a pooled estimate. Left the pool: PMID 28456509. Why: PMID 28456509 set aside (ENDPOINT_UNBOUND): tuple not located in the held document cache/tranexamic-acid-pph/records.json#PMID-28456509 (abstract): no span carries it. Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong. — Claude Opus 5 (lane m2/bind-hand-rows, 2026-09-20); reviewer countersignature owed: Mahmood.

```
SIGNED-BY: Mahmood  NOTICE: MAIN-13  SHA256: bffe51380555a1e9549e214033f2bc812ca978196f442b61f6b89c6227d34108  DATE: ____
```

---

**Integrity.** This file does not state its own digest; it is in the sidecar
`SIGNING_PACKET_V2_2026-09-29.md.sha256`.
