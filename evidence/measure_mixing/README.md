# The pooled effect measure is DERIVED, never declared (branch only; served changes are notices for Mahmood)

External review of balanced-crystalloids, 2026-09-26: the headline says **HR**, but the 2-trial pool mixes PLUS's count-reconstructed
**RR 0.9918** with BaSICS's **adjusted HR 0.97** (0.90-1.05).
- `pipeline.py` fell back to the topic's declared estimand whenever an input lacked a stated scale.
- `estmeasure`'s FIRST_EVENT_RATIO class passed HR+RR as `compatible_labels`.

## Reviewer's reconstruction, reproduced exactly

The producer's own `synth.pool`, run on the served rows at v1/candidate 3876a62d, gives mixed **0.97744**, tau² **0**, Q **0.10970**,
common-effect CI **0.91829-1.04040**. This matches the review. The HKSJ CI at k=2 is 0.652-1.465.

## The fix (`harness/estmeasure.py`, `harness/pipeline.py`)

**(a) Derived label.** `input_label()` gives each admitted input's measure as the engine pools it: a stated effect's scale; counts
-> the reconstructed RR or OR; IRR; MD. The pool's label is that one measure. The declared-estimand fallback is gone.

**(b) Mixed measures refused by default.** `pool_measure_decision()` refuses mixed measures (POOL_MEASURE_MIXED; an unknown
input gives POOL_MEASURE_UNIDENTIFIED).
- The only exception is a **predeclared** per-outcome `measure_mixture_policy` that names exactly that mixture (allow, predeclared,
  decided_by, decided_on, rationale). The label then reads **"mixed ratio (HR+RR)"** and the policy is served with the number.
- An incomplete policy is no policy.
- A refusal reuses the existing fail-closed suppression: no number, CI, tau², forest or leave-one-out is rendered. An auditable
  counterfactual is kept.
- `pool_compatibility()` is unchanged and stays a description of the effect classes. The GATE is new.

**(c) Adjusted and unadjusted kept apart.** `adjustment_of()` tags each input from covariate-adjustment evidence in its OWN
quotation: counts -> UNADJUSTED; "adjusted HR/RR/OR", "adjust(ed) for", multivariable/multivariate -> ADJUSTED; otherwise UNSTATED.
- "multiplicity-adjusted" and "dose-adjusted" do not count. NOAC ENGAGE-AF's 97.5% CI was a false tag under a bare-word rule.
- Every result carries `analysis_groups`: each group is pooled on its own.
- ADJUSTED beside UNADJUSTED refuses the headline (POOL_ADJUSTMENT_MIXED) unless the policy says `allow_adjustment_mixture`.

## Verified end to end (real `build_topic`, balanced-crystalloids, throwaway tree)

- **Default:** "REFUSED: mixed ratio (HR+RR)" with POOL_MEASURE_MIXED. The page shows the suppression block and no "Pooled effect"
  row. Counterfactual 0.9774. Groups: ADJUSTED BaSICS HR 0.97 (0.90-1.05); UNADJUSTED PLUS RR 0.9918 (0.8917-1.1031).
- **With a throwaway predeclared policy** allowing HR+RR and the adjustment mix: "mixed ratio (HR+RR)", 0.9774, tau² 0, Q 0.1097,
  CE 0.9183-1.0404, with the policy shown. That is the reviewer's number, labelled honestly.

## Served pools that mix measures today (`measure_mixing.py`, which uses the gate's own readers)

- **4 of 27** topics with a served primary pool mix measures: balanced-crystalloids, doac-vte-recurrence, noac-vs-warfarin-af-stroke,
  spironolactone-hfref-mortality.
- 5 of 51 served pools (on 5 of 29 topics) mix measures; the fifth is ticagrelor major bleeding. **All 5** labels are declared over a
  mixed pool; no unmixed pool has a label that differs from its inputs.
- **2** served primary pools mix covariate-ADJUSTED with UNADJUSTED inputs: balanced-crystalloids (BaSICS adjusted HR) and
  probiotics (PMID 7872284's multivariate-adjusted RR 0.29 beside count-derived RRs).

## Notices if landed with NO policies declared (for Mahmood's decision and signature)

| topic | pool | served now | after | reason |
|---|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | primary | 0.9774 (HR) | refused | HR+RR mixed; adjusted beside unadjusted |
| doac-vte-recurrence | primary | 0.9091 (HR) | refused | 5 HR + 1 RR |
| noac-vs-warfarin-af-stroke | primary | 0.8069 (HR) | refused | 3 HR + 1 RR |
| spironolactone-hfref-mortality | primary | 0.7294 (HR) | refused | RALES "RR" + 2 HR. RALES's relative risk is Cox-based in the paper, but the held quotation carries no model evidence, so the harness cannot call it an HR |
| probiotics-aad-prevention | primary | 0.6874 (RR) | refused | one adjusted RR beside unadjusted counts |
| ticagrelor-vs-clopidogrel-acs | major bleeding | 1.1658 (HR) | refused | count RR + HR |

Each topic owner can instead predeclare a `measure_mixture_policy`. The number then returns, labelled "mixed ratio (...)" with the
policy shown. That is a protocol decision, not an engineering default. Many of these topics are also moved by the UNBOUND_LEGACY
fail-closed work (branch oc/v101-unbound-failclosed), so the notices should be decided together.
