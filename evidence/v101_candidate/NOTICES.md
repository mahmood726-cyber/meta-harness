# V1.0.1 candidate stack -- every served move, for Mahmood's hash-bound signature (NOTHING here is landed)

## How this was measured

- **Stack:** `oc/v101-candidate-stack` at `83495751`. It merges, on top of `oc/v101-effect-identity` (e11c7613):
  - continuous identity and class denominators (`oc/v101-continuous-stack`, 2de823f5);
  - effect-identity fixtures, multi-arm, polarity and relative reductions (`oc/cx-fixtures-effid`);
  - derived labels, tiers, the composite rule and narrative rules (`oc/cx-fixtures-measure`, on `oc/v101-measure-derived`);
  - matched placebo (`oc/v101-matched-placebo`, on `oc/v101-on-candidate`).
- **Deliberately NOT in the stack:** UNBOUND_LEGACY fail-closed (`oc/v101-unbound-failclosed`, `oc/cx-unbound-binder`).
  That is your A/B/C decision and it would withdraw many more pools; see `evidence/unbound_legacy/README.md` on that branch.
- **Measurement:** all 32 topics rebuilt with `scripts/build_topic.py` at 83495751 (rc=0 for every topic). Each is compared
  with the SERVED `docs/reviews/<slug>/review.json` at 3876a62d by `compare_full.py`, which writes `moves_83495751.json`.
- **Scope of the comparison:** pooled result (k, estimate, CI, scale label), pooled trial ids and n, declared-absent ids,
  and screening decisions.
- **Result:** 72 outcomes unchanged, **31 moves**. Every move is below with its rule. None is unexplained.

## A. Pooled results that are withdrawn or refused (a served number disappears)

| topic / outcome | served at 3876a62d | stack | rule (branch) |
|---|---|---|---|
| noac-vs-warfarin-af-stroke / SSE (primary) | HR 0.8069 (0.6611-0.9850), k 4 | REFUSED: POOL_MEASURE_MIXED (3 HR + 1 RR) | a mixture of measures is refused unless a per-outcome `measure_mixture_policy` declares it (measure-derived) |
| spironolactone-hfref-mortality / all-cause mortality (primary) | HR 0.7294 (0.5609-0.9486), k 3 | REFUSED: POOL_MEASURE_MIXED (2 HR + 1 RR) | same |
| probiotics-aad-prevention / AAD (primary) | RR 0.6874 (0.4803-0.9839), k 11 | REFUSED: POOL_ADJUSTMENT_MIXED | the pool mixes one covariate-ADJUSTED RR (PMID 7872284: "the adjusted relative risk ... RR = 0.29, 95% CI 0.08, 0.98", from "a multivariate model") with unadjusted ones. Pooling them needs a declared `allow_adjustment_mixture` (measure-derived rule, typed by effect-identity's `published_model`). **This move was NOT in any earlier per-branch measurement; it appears only when the two branches meet.** |
| balanced-crystalloids / mortality (primary) | HR 0.9774, k 2 (CI withheld at k=2) | no pooled number: DESIGN REFUSAL at k=1 | BaSICS's published HR (PMID 34375394) is routed out of the risk pool (effect-identity `hr_route`). SMART was already refused for its cluster-crossover design, so k=1 remains. |
| ticagrelor-vs-clopidogrel / major bleeding (harm) | HR 1.1658, k 2 (CI withheld) | HARMS_INCOMPLETE, k=1 | PMID 26376600's HR is routed out of the risk pool (`hr_route`); a harm with an unresolved reported outcome is not rendered as absence |

**Decisions these need:**
- noac and spironolactone: declare a mixture policy with an HR-only sensitivity analysis (as DOAC does), or accept the refusal.
- probiotics: declare `allow_adjustment_mixture`, pool the unadjusted rows only, or accept the refusal.

## B. Pooled results that change value or label

| topic / outcome | served | stack | rule |
|---|---|---|---|
| esketamine / MADRS MD (primary) | MD -3.1004 (-7.3323 to 1.1315), k 3 | MD -3.3436 (-6.0691 to -0.6180), k 4 | declared combine-eligible-doses rule adds TRANSFORM-1 (continuous identity) -- the interval stops including 0 |
| semaglutide / % weight (primary) | MD -11.8449, n 1306/655 and 407/204 | MD -11.8523, n 1212/577 and 373/189 | the n behind a class-level mean/SD is the class's own n (continuous identity); CI withheld at k=2 in both |
| colchicine-recurrent-pericarditis / recurrence (primary) | RR 0.4643, k 2 (CI withheld) | RR 0.44 (0.27-0.73), k 1 | CORP-2 (PMID 24694983) held: its published effect conflicts with its own counts (effect identity) |
| corticosteroids-covid19 / 28-day mortality (primary) | "RR" 0.83 (0.75-0.93) | OR 0.8596 (0.7606-0.9716), counts 2104/4321 | RECOVERY's age-adjusted RATE ratio is not a risk ratio; the protocol target is OR, reconstructed from the held counts (effect identity) |
| tocilizumab-covid19 / 28-day mortality (primary) | "RR" 0.85 (0.76-0.94) | OR 0.83 (0.7285-0.9456), counts 2022/2094 | same (RECOVERY-tocilizumab) |
| doac-vte-recurrence / recurrent VTE (primary) | label HR | label "mixed ratio (HR+RR, approximation per protocol)"; number unchanged, HR-only sensitivity shown | declared mixture policy (measure-derived) |
| corticosteroids-cap / hyperglycaemia (secondary) | label INCOMPATIBLE (OR + RR), no estimate | label RR, still no estimate | STEP's OR reconstructed to RR from its counts 392/393 (effect identity); the pool stays unrendered for its existing reason |

## C. Screening and absence inventories (no pooled number moves)

- Six trials move from X-CONTRAST to INCLUDE: SAK-HFpEF, Neu I, VITAL-Echo, DRC-04, SYNAPSE and NCT01968668.
  - Cause: "placebo for X" is a matched placebo, and "every arm" means every arm (matched placebo).
  - Each now appears in its topic's declared-absent lists: 14 outcome lists across 6 topics.
  - None contributes a poolable row (pre/post rebuilds on the matched-placebo branch).
- esketamine: TRANSFORM-1 leaves the absent list of the primary, because it is pooled.

## D. What is NOT a served number and is in the stack

- Typed fields and refusals recorded in review.json:
  - `continuous_analysis`, `n_analysis_set`, `multi_arm_combined`;
  - `event_polarity`, `transform_provenance`, `published_model`, `typed_uncertainty`;
  - `ordered_contrasts`, derived labels and tiers.
- New page blocks: continuous analysis, measure sensitivity, time-to-event and definition adjudication.
- Certificates pin `harness/*.py`, so CI is red on this stack until the pages are regenerated.
- **Built before 885d3621:** the matched-placebo parser fix (slash = level only in "X/X placebo"; a double-dummy arm is
  exposed) is merged after this build. It changes only `ordered_contrasts` fields on arm objects. The screening
  measurement it feeds is unchanged (15 X-CONTRAST, 7 by the arm-list fallback, 6 wrong).

## E. Held outside the stack (your decisions, no served move here)

- UNBOUND_LEGACY fail-closed: options A, B or C.
- Registry-route composites that differ from their own trial declaration: 4 of 13 served registry rows (FOURIER, STRENGTH,
  REDUCE-IT, DAPA-HF). See `evidence/unbound_legacy/SERVED_REGISTRY_ROUTE.md` on `oc/cx-unbound-binder`.
- The esketamine protocol states no missing-data assumption for its observed-case primary. Stating one is a protocol
  amendment.
