# k-gap fill: cumulative funnel by source phase (13 Oct 2026)

Population: comparator trials we do not pool and that are not named out of scope (`g1_trial_acquire.targets`): **141** over 32 topics.

| phase | source | reached | n of N | admitted |
|---|---|---|---|---|
| 1 | CT.gov / AACT (snapshot 2026-08-30 + CT.gov v2) | NCT 57 / 141 -> posted 21 / 57 -> outcome bound 3 / 21 | | **1** (SALT; deterministic arm pick = reader tuple) |
| 2 | FDA (Drugs@FDA reviews + labels) | named 11 / 140 -> typed 0 -> read 10 | | 0 |
| 2 | EMA (EPARs) | named 8 / 136 -> typed 0 -> read 9 (incl. 1 read of a trial no longer named) | | 0 |
| 2 | IQWiG / G-BA (AMNOG; typed-only) | 5 topics with procedures; named 13 / 67 -> typed 0 | | 0 |
| 2 | PMDA | not run: PMDA terms forbid automated download. 3 pilot review reports identified; permission and a PDL 1.0 ruling are needed | | -- |
| 2 | Health Canada (clinical information portal) | not attempted: account required (Mahmood, 13 Oct: skip) | | -- |
| 2 | EMA Policy 0070 (clinical data packages) | not attempted: account required (Mahmood, 13 Oct: skip) | | -- |
| 2 | NICE (typed-only) | named 21 / 140 -> typed 0 | | 0 |
| 3 | open sources (started) | 61 PMID-bearing identity-less trials: 23 with an open copy, 1 CC BY. Under the current gates, 0 readable acquisition targets with text | | 0 |
| 4 | published metas (SECONDARY) | not started | | -- |
| **cumulative** | | | | **1 of 141** (phase 1) |

**Where the missing trials stand:**
- **No identity: 83.** 61 have a PMID and no registration (phase 3); 22 have neither (IDENTIFICATION_QUEUE.md).
- **Registered, nothing posted:** 36.
- **Posted, nothing binds: 18** (ARMS 4, OUTCOME_NOT_NAMED 14, ESTIMAND 0). No named-divergence admission is possible without coercion (PHASE1_FUNNEL.md).
- **Regulators:** they name 13 to 21 trials per agency. Every such document gives either no per-trial result for the protocol outcome or one on another estimand / population / definition (G-BA pcsk9 Table 4-52).

**Decisions waiting** (none made by the lane; each needs Mahmood or the Captain):
1. population named by enrollment equality (phase 1, SALT);
2. ASCEND: take the trial's PRIMARY outcome when several bound outcomes each give one gated pair (#103);
3. deterministic reading of bronze / green open copies with no licence. Mahmood's ladder says "other OA text is regex-only", but the `OPEN_COPY` gate refuses them (19 trials);
4. PMDA: download permission for 3 named review reports, and PDL 1.0 for prompts;
5. comparator label defects: ODYSSEY JAPAN's NCT02017898 should be NCT02107898; corticosteroids-cap "Ampicillin dosage and use".
