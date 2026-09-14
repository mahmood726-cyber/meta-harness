# What wrong page could this system still emit? — a gate-by-gate adversary map

The external auditor's design question, adopted: not *"is this page right?"* but *"could this system emit
an indefensible scientific statement without a gate preventing or visibly qualifying it?"* For every gate
we have, the indefensible output it would NOT stop is named below. That list IS the remaining defect map.

## Gates we have, and what each would NOT stop
1. **Two-limb publication gate** (reproduce-all + census + leak-scan). Stops: non-reproducible / hand-edited
   pages; stale index. **Would NOT stop:** a page that reproduces deterministically but is *systematically
   wrong* — a stable wrong extraction reproduces perfectly. Reproducibility ≠ correctness.
2. **Canonical claim object** (significance / null-crossing). Stops: cross-surface *significance*
   contradiction. **Would NOT stop:** a CATEGORICAL contradiction ("pooled" here, "not pooled" there) or a
   METHODOLOGICAL one ("byte-reproducible" asserted + retracted). → seventh gate, still unbuilt.
3. **Invalidation / STALE.** Stops: a dependent output invalidated by a *committed* signal. **Would NOT
   stop:** a topic that SHOULD be stale but whose invalidating fact was never committed (an eligible trial
   nobody flagged) — absence of a signal reads as currency.
4. **Compatibility key.** Stops: pooling across effect-measure *classes* (RR vs IRR). **Would NOT stop:**
   incompatible ENDPOINTS within one class (HF-hosp-alone vs HF-hosp+CV-death — the iv-iron finding) unless
   the endpoint dimension is actually populated and checked; a comparator declared "same question" with a
   different outcome/estimand.
5. **Interval-provenance gate** (new). Stops: a CI not produced by the canonical engine. **Would NOT stop:**
   a wrong POINT ESTIMATE the engine faithfully pools from wrong per-arm inputs (garbage-in), or a wrong
   scale chosen upstream.
6. **Verify gate** (pooled digits present in source). Stops: a number absent from its cited source. **Would
   NOT stop:** a number present in source but on the WRONG endpoint (right-number-wrong-endpoint); a refusal
   whose REASON is factually false of the source; an aact_verified label on counts that are really a
   percentage synthesis (partially closed by the percentage-provenance gate).
7. **Leak scan** (no pooled stat for a suppressed topic). Stops: a derived stat attributed to a suppressed
   slug in docs/*.json. **Would NOT stop:** the same stat under a different slug spelling, or on a surface
   the scan does not read (only docs/*.json top-level is scanned).
8. **Percentage-provenance gate** (new). Stops: `%×N` counts badged verified with the exact count absent
   from source. **Would NOT stop:** a wrong outcome-specific denominator that happens to appear in the
   source (plausible-but-wrong denom).
9. **RoB coverage** (now 100/100). Stops: a pooled trial left unassessed. **Would NOT stop:** a WRONG RoB
   verdict — an abstract mislabelled double-blind, or a "low" that a human would call "some concerns"
   (judgement); the ASSESSMENT existing ≠ the assessment being right.
10. **Prevention screening** (population ≠ prevented outcome). Stops: the population=outcome inversion.
    **Would NOT stop:** a subtler population mismodelling on a non-prevention topic.

## The indefensible outputs still emittable → the queue (each maps to one of the auditor's 5 root systems)
- **(3 STATE):** categorical + methodological contradictions (seventh gate); `DECLARED_ABSENT` split four ways;
  `NOT_ASSESSED` ≠ `NOT_DOWNGRADED` across every GRADE domain; `Claims checked: 0` as a failing state.
- **(2 PROVENANCE):** refusal reasons factually false of source; extraction hierarchy (published effect
  beats reconstruction); overrides that manufacture an unverified absence/reason (23 enumerated, 8 force
  ABSENT — reasons unverified, and overrides not rendered AS overrides); `trial → source-documents` object.
- **(1 IDENTITY):** the randomised-contrast check silently passing any trial it cannot identify;
  trial-family / randomised-comparison uniqueness (publications counted as trials).
- **(4 INFERENCE):** ITT-as-randomised mislabel (randomised N ≠ analysed N; CAPE COD); wrong point estimate
  from wrong per-arm inputs.
- **(5 SEARCH):** `union(displayed queries) == screened set`; comparator matcher rebuilt on one key
  (outcome/estimand identity, granularity, evidence geometry, search date); systematic-search recall (weakest layer).

## Standing self-test (from the auditor): three deployment states, all three carried in the ledger
`LANDED_IN_CODE` (committed) · `LANDED_IN_SERVED_BYTES` (live URL hash proves it) · `INDEPENDENTLY_VERIFIED`
(an external party confirmed it). A fix is not done until all three, and "silence about a limitation counts
as a regression even if the numbers improve."
