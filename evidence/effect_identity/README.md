# Effect identity before source preference (branch only; served changes are notices for Mahmood)

External review of colchicine-recurrent-pericarditis (hash f42a3bf5...), 2026-09-26.

## (1) SOURCE_EFFECT_CONFLICT: a published ratio that disagrees with its own counts

- **CORP-2 (PMID 24694983).** The served value is RR 0.49 (0.24-0.65), `PUBLISHED_EFFECT_TARGET_CLASS`. It was preferred over its own
  counts, 26/120 vs 51/120, which give RR **0.5098 (0.3421-0.7596)**, the review's 0.342-0.760.
- **The source mislabels it.** The held abstract itself says "relative risk 0.49; 95% CI 0.24-0.65": the mislabel is in the
  source, not the extractor. 1 - 0.5098 = 0.490, and 1 - the count CI = 0.240-0.658, so the published number is the relative risk
  REDUCTION.

`harness/effect_identity.conflict_check()` runs after source-hierarchy selection:
- It recomputes the count-implied RR (Katz) and OR (Woolf).
- It tests named hypotheses against the point AND both CI ends, within the published rounding plus a 0.006 method slack:
  AS_LABELLED, RRR_AS_RR (1-x, ends swapped), OR_AS_RR / RR_AS_OR, RECIPROCAL.
- A mismatch emits `SOURCE_EFFECT_CONFLICT` with the hypotheses that match. **Nothing is relabelled.**
- The row is **HELD**: moved out of the pool, visible with its tuple, counts and every hypothesis.
- The one exception: its own quotation documents an adjusted model (covariate adjustment only, e.g. "adjusted relative risk",
  "age-adjusted"; not "multiplicity-" or "dose-adjusted"). Then the published effect is kept and the conflict disclosed.
- An HR is recorded NOT_COMPARABLE, since it is not the crude ratio of its counts. A zero cell is never corrected into a number.

## (2) Transformation provenance

CORP (PMID 21873705) reports "relative risk reduction, 0.56 [CI, 0.27 to 0.73]" (recurrence) and "0.56 [CI, 0.27 to 0.74]"
(symptoms). `extract` correctly converts these to RR 0.44 (0.27-0.73) and 0.44 (0.26-0.73), but the rows said
`KEEP_REPORTED_EFFECT` with `reported_label` RR.
- `transform_provenance()` now records {reported_measure RRR, the reported values, transform "RR = 1 - RRR; CI endpoints swapped",
  derived RR}. It reads the row's quotation, then the held abstract (the recurrence quotation is cut mid-CI).
- A transform is accepted only if it reproduces the served tuple exactly.
- The rule becomes `KEEP_REPORTED_EFFECT_TRANSFORMED`, and `effect_object.reported_label` becomes RRR. The canonical estimand stays
  RR, so compatibility is unchanged.
- The recurrence record carries a note that its interval is symmetric about 0.5 (0.27 + 0.73 = 1). That is why the transform is
  invisible in the numbers, and why it must be recorded.

## A hold must reach the reader (found in the real build, fixed)

`absence.classify_reason` re-classified the held row as **EXTRACTION_NOT_PERFORMED**, so the hold read as "not extracted". It now
keeps HELD_SOURCE_EFFECT_CONFLICT, like the RESULT_INCOMPATIBLE / ENDPOINT_UNBOUND codes it already preserved. The plant is the
pre-fix absence layer, which returns EXTRACTION_NOT_PERFORMED.

## Corpus-wide at v1/candidate 3876a62d (`measure_effect_identity.py`, which uses the module's own functions)

**Conflicts.** 127 served pooled rows; 86 carry a reported effect; 6 have counts for the same result; 4 of those are comparable
(RR/OR; 2 are HR). **3 of 4 comparable rows conflict:**

| topic | trial | published | count-implied RR | hypothesis | resolution |
|---|---|---|---|---|---|
| colchicine-recurrent-pericarditis | CORP-2 24694983 | RR 0.49 (0.24-0.65) | 0.5098 (0.342-0.760) | **RRR_AS_RR** | HOLD |
| probiotics-aad-prevention | 7872284 | RR 0.29 (0.08-0.98) | 0.4948 (0.209-1.172) | none | KEEP_DISCLOSED (a documented multivariate-adjusted RR) |
| tocilizumab-covid19-mortality | RECOVERY 33933206 | "RR" 0.85 (0.76-0.94) | 0.8822 (0.808-0.963) | none | HOLD. The held abstract says "rate ratio" and documents no model; the age adjustment is only in the full paper, which is not held. This is the same row the ordered-contrast census flagged as a rate ratio labelled RR |

**Provenance.** **2 of 86** reported rows are transforms served without a record: CORP recurrence and CORP symptoms. Both are
RRR->RR, `KEEP_REPORTED_EFFECT`, labelled RR.

## Notices if landed (for Mahmood)

| topic | pool | served now | after |
|---|---|---|---|
| colchicine-recurrent-pericarditis | primary | 0.4643 (k=2) | 0.44 (0.27-0.73), k=1 (CORP only); CORP-2 held with RRR_AS_RR. Verified with a real build_topic |
| tocilizumab-covid19-mortality | primary | 0.85 (0.76-0.94), k=1 | withdrawn: RECOVERY held (unexplained conflict with its counts) |
| colchicine-recurrent-pericarditis | 2 CORP rows | labelled a reported RR | labelled a transformed RRR (no number moves) |

A reviewer's typed resolution (which number the source means, with evidence) releases a held row. For RECOVERY, holding the full
text that documents the age-adjusted model would resolve it as KEEP_DISCLOSED.

## (3) A published HR stays an HR -- SONIA's rule (CAP-corticosteroids review)

SONIA (NEJM 2025, PMID 41159889; held only in the search snapshot, not yet in any served pool): 246 (22.6%) vs 284 (26.0%) deaths,
**HR 0.84 (0.73-0.97)**, site-stratified Cox, 98 missing day-30 vital status (the full text; not held).
- `hr_route()`: a published HR on an outcome whose declared estimand is not HR, **in a pool that is actually a risk pool** (another
  admitted input is an RR or OR), is never converted by dividing events by randomised. It goes to `time_to_event_analysis`: kept as
  an HR, pooled with other HRs only when there are two or more, and shown on the page.
- It joins the risk pool only through a typed `ascertained_denominators` record with its span, never inferred.
- A pool of HRs alone is untouched: it already is a time-to-event analysis (omega3, statins, sglt2-hfref).

**Corpus: 2 served rows** are HRs inside genuine risk pools:
- BaSICS 34375394 in balanced-crystalloids' primary, beside PLUS's count RR;
- the ticagrelor major-bleeding HR 26376600, beside a count RR.
A first count said 17. It included pools made of HRs alone and was corrected before reporting.

## (4) Reconstruction route for an incompatible published OR (STEP)

`reconstruct_from_counts()` rebuilds the RR:
- counts from the effect's own sentence ("76 [19%] vs 43 [11%]");
- denominators from the held abstract's randomisation sentence ("the prednisone group (n=392) ... the placebo group (n=393)");
- arms matched by the topic's terms;
- each count corroborated against its stated percentage, at the precision the source wrote.

Result: **RR 1.772 (1.2526-2.5066)**, the review's 1.772 (1.253-2.507). The row is labelled `RECONSTRUCTED_FROM_COUNTS`, with
`published_effect_retained` = OR 1.96 (1.31-2.93). A failure returns a typed reason (no arm named / no denominators / a
count off its own percentage / a zero cell); the row then stays as published. **Corpus: 1 of 1** published OR in an RR outcome is
reconstructed.

## (5) Endpoint-definition compatibility is adjudicated, not assumed

Once measures agree, the hyperglycaemia pool is homogeneous RR. But STEP's quotation defines the endpoint as insulin-requiring, and
Torres' and the others' quotations state no definition. The pool is therefore held: `definition_adjudication` PENDING, the
counterfactual kept (would-be RR 2.07), and the page shows the per-input definitions. It stays held until the topic records
`definition_adjudication`.

## Verified with real builds (throwaway trees)

- balanced-crystalloids: BaSICS routed to the time-to-event block (HR 0.97, shown on the page). PLUS remains alone; with SMART
  design-refused, the existing design-refusal rule serves no number at k=1.
- corticosteroids-cap: STEP reconstructed; hyperglycaemia measures homogeneous; definition adjudication PENDING, shown on the page.

A mistake of mine, caught by a test: I first said the topic lacks "prednisone" (I had printed only the first 8 terms). It lists
prednisone in both intervention_terms and intervention_agents, and STEP reconstructs on the real topic.

## Notices if landed

| topic | outcome | now | after |
|---|---|---|---|
| balanced-crystalloids | primary | 0.9774 (HR label, HR+RR) | BaSICS to a separate time-to-event analysis; with SMART design-refused, PLUS alone (k=1): no pooled number |
| ticagrelor-vs-clopidogrel | major bleeding | 1.1658 (HR+RR) | the HR row routed to time-to-event; the count RR alone |
| corticosteroids-cap | hyperglycaemia | suppressed (OR+RR incompatible) | still no number: held for definition adjudication; STEP now RR 1.772 with its OR retained |

## (6) RATE is not RISK, and the target measure comes from the protocol (COVID-corticosteroids review)

RECOVERY (PMID 32678530) reports an **age-adjusted rate ratio, 0.83 (0.75-0.93)**.
- `extract` mapped a bare first-event "rate ratio" to RR (audit 22), and `source_hierarchy.estimand_decision` then set the
  **target** from the first published label. The protocol's **OR** became RR (`served_scale_changed: true`).
- Now a bare first-event rate ratio is `RATE_RATIO`, canonical `RATE_RATIO_FIRST_EVENT` in its own class: never a risk ratio,
  never an IRR.
- The target is the protocol's declared measure, always. An input of another measure is recorded in
  `protocol_measure_departures` and rebuilt to the target from held counts (the reconstruction route now takes a target measure and
  RECOVERY's "n (p%) in the X group and ..." wording).
- In a real `build_topic`, RECOVERY enters the OR pool as **OR 0.8596 (0.7606-0.9716)** from 482/2104 vs 1110/4321, the review's
  number. The rate ratio is retained alongside. The RR from the same counts is 0.8918 (0.8123-0.9791).
- Measured at 3876a62d: the target departs from the protocol's measure on **14 of 97** outcomes with an estimand decision.
  - 2 are OR -> RR (COVID-corticosteroids, tocilizumab: both via RECOVERY's rate ratio).
  - 12 are RR -> HR (balanced-crystalloids; denosumab x3; omega3; statins; sglt2 x3; spironolactone; ticagrelor bleeding;
    iv-iron). Those protocols declare RR while their evidence is HR. That is a protocol amendment for each topic owner, not a
    switch the pipeline may make; these are notices.
- **2 of 127** served rows are rate ratios stored as RR (both RECOVERY).
- Two tests pinned `== "RR"` for a first-event rate ratio. Their stated requirement ("must not be typed IRR") is kept; the RR
  half was the defect. They were rewritten to `RATE_RATIO`, and the change was isolated by rerunning the failing tests on the
  pre-fix harness: only these two are caused by it.

## (7) Outcome polarity: which EVENT is modelled

REMAP-CAP's adjusted ORs (1.43, 1.22) are "the odds of improvement" in organ support-free days: >1 = benefit.
- `event_modelled()` reads the effect's own quotation: BENEFIT_EVENT, DEATH or NOT_STATED.
- In a death or mortality outcome, a benefit-event effect is **refused** (`EVENT_POLARITY_MISMATCH`, held visible), unless the
  outcome declares `polarity_normalisation.reciprocal_for_benefit_event`. Then the reciprocal is applied with ends swapped
  (1.43 (0.91-2.27) -> 0.6993 (0.4405-1.0989)) and the original is kept.
- Served today: 0 of 20 stated-effect rows in death outcomes model a benefit event. The plant is REMAP-CAP's own held abstract.

## (8) Multi-arm shared control

REMAP-CAP's fixed-dose (41/137) and shock-dependent (37/141) hydrocortisone arms share one control (33/99). These are the review's
counts; the held abstract gives only percentages over 137 / 146 / 101, so this is a synthetic fixture.
- `apply_multi_arm_rule()` groups rows by trial family with identical control counts. A declared `multi_arm_rule`:
  - `COMBINE_ARMS` -> 78/278 vs 33/99;
  - `SPLIT_CONTROL` -> 41/137 vs 16.5/49.5 and 37/141 vs 16.5/49.5 (Cochrane Handbook 23.3.4).
- Either way the control's 99 patients enter once. Undeclared, the group is **held** (`MULTI_ARM_SHARED_CONTROL_UNDECLARED`), never
  entered as two independent comparisons.
- Both new codes are preserved by the absence layer, so they reach the reader. Served today: 0 shared-control groups among 127
  pooled rows.

## (9) Counts under an HR target (dapagliflozin HFmrEF/HFpEF review)

PRESERVED-HF reports HF events descriptively (HF hospitalisation or urgent HF visit 9/162 vs 9/162, 12-week treatment).
- `count_only_under_hr()`: a count-only row in an HR-target outcome gets state **CLINICAL_EVENT_COUNTS_RECOVERED_HR_NOT_ESTABLISHED**.
- Its count-RR (**1.000, 0.4074-2.4545**; the review's 0.407-2.454) is recorded as `is_hazard_ratio: false`. It is never labelled
  an HR and never enters the HR primary.
- It enters only an explicitly defined `secondary_count_analysis` (with its definition); otherwise it is reported, held visible,
  and its code survives the absence layer.
- The held abstract carries only KCCQ-CS and adverse events, so for the held bytes PRESERVED-HF stays OUTCOME_NOT_IN_SOURCE. The
  9/162 counts are the review's, used as a synthetic fixture. Served today: 0 count-only rows among 55 pooled rows in HR-target
  outcomes.

## (10) CI provenance is derived from the computation

The served adverse-events pool is k=1 (44/162 vs 38/162, RR 1.157895 (0.795441-1.685505)), yet it carried the PM-tau2+HKSJ token.
At k=1 `synth.pool` computes no tau2 and no HKSJ, only the study's own z-based Wald interval. It now stamps
`synth.pool:k=1:single-study-log-ratio-Wald-z(no-tau2,no-HKSJ):v1` (or the additive twin for MD/SMD) and keeps PM/HKSJ for k>=2.
The census gate's allow-list gains exactly these tokens.

## (11) Double-zero studies (denosumab review)

A trial with 0 events in both arms (Nakamura) has no conventional log-ratio.
- `synth.Study.yi_vi` used to add 0.5 to all four cells whenever ANY cell was zero, **including double-zero**, which manufactures
  pseudo-events. The plant is the pre-fix engine returning log-RR 0 for 0/50 vs 0/50.
- It now raises `DoubleZero` (2x2 and events/person-time alike), unless a DECLARED zero-event method is set on the study.
- The pipeline moves such a row out of the pool with state **DOUBLE_ZERO**: `eligible: true`, `outcome_observed: true`, absent kind
  `observed_no_estimable_effect`, counts shown. The code survives the absence layer.
- A zero-event method runs only as a predeclared `zero_event_sensitivity` (`CC_0.5`), in its own pool marked SENSITIVITY ONLY.
  Undeclared, none is run and that is stated.
- A single-zero correction (the house rule) stays, and is disclosed for every outcome kind; harms.py already disclosed it for harm
  rows. My first claim that the one served single-zero row (COVID serious adverse events 1/16 vs 0/14) was corrected silently was
  wrong; a test caught it.
- Served today: 0 double-zero rows among 35 served count rows. Nakamura is not in the served denosumab review; its row is a synthetic
  fixture.

## (12) Prefer the published model; crude counts corroborate only (denosumab review)

FREEDOM (19671655) serves the published RR 0.32 (0.26-0.41) and HRs 0.80 / 0.60 (`KEEP_REPORTED_EFFECT`); no path replaced them.
- The rows now carry `published_model`: read from the quotation / held abstract, or from a typed record with its span. FREEDOM's
  held abstract gives percentages only and does not state the age-stratified Mantel-Haenszel / age-adjusted Cox models (those are in
  the full text), so each row says `NOT_STATED_IN_HELD_TEXT` rather than asserting a model.
- With a typed record the model is recorded. Same-measure crude counts become `crude_corroboration` with role CORROBORATION_ONLY:
  86/3702 vs 264/3691 -> RR 0.32479 (0.25573-0.41249), the review's number. They are never a replacement.
- A documented model (stratified / Mantel-Haenszel / Cox / adjusted) makes a count disagreement KEEP_DISCLOSED, never HOLD. The
  same estimate with no documented model is HOLD (tested both ways).
- Not built end to end: both drives are below the 3 GB regeneration floor (C: 2.5 GB, F: 2.4 GB).
