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

## (13) Typed uncertainty: a one-sided or repeated bound never becomes a 95% CI (DPP-4 review)

EXAMINE (23992602) reports "hazard ratio, 0.96; upper boundary of the one-sided repeated confidence interval, 1.16". It was served
as **OUTCOME_NOT_IN_SOURCE**, which is false: the outcome is reported, and the extractor simply found no two-sided interval.
- `ci_representation()` types every stated interval: {sidedness two-sided / one-sided-upper / one-sided-lower, repeated, level}.
  EXAMINE's level is **not stated in the held abstract** (the one-sided 99% is in the full text), so the record says None rather than
  asserting it.
- `se_permitted()`: only a two-sided, non-repeated interval at a stated level supports an SE.
- `uncertainty_state()` gives **UNCERTAINTY_REPRESENTATION_UNRESOLVED** ("outcome reported; required uncertainty representation
  unresolved"). The point and bound are kept as stated; nothing is reflected or re-levelled.
- Pipeline:
  - a pooled row whose quotation states only such a bound is held;
  - a declared-absent row whose abstract reports this outcome with only such a bound is re-stated from OUTCOME_NOT_IN_SOURCE;
  - the code survives the absence layer.
- `synth`: a non-positive ratio limit is refused explicitly (the old message was "has neither a 2x2 nor an effect+CI", or a bare
  math-domain error).
- **Count RR is a different measure.** EXAMINE's count RR (0.9573, 0.8257-1.1100 from 305/2701 vs 316/2679) cannot be rebuilt from
  held bytes, because the abstract gives only the 5380 total and the per-arm n are in the full text. The reconstruction refuses with
  that reason, and a count RR never enters the HR pool under the HR label. The review's counts are a synthetic fixture.

## (14) Effect-only shared controls and same-estimate polarity fallback (3876a62d)

Offline measurement uses the immutable served corpus at `3876a62dca66764dff1b4f84d6b43356a1a9e3bb`, before patching; no pipeline rebuild or live source substitution.

| Input | Static vs dynamic / hardcode disclosure |
|---|---|
| Pin and synthetic boundary plants | Static; plants are not research observations |
| Rows, identifiers, abstract sentences and estimates | Dynamic reads of pinned review/topic/cache git objects |
| Counts and rule states | Computed from those inputs; no invented effects, correlations or source identifiers |

### Gap 1 measurement: every same-family group within each outcome

Inspected all **127 rows across 97 outcomes on 32 served pages**. All 127 carry `trial_family_id`, `family_id` and `trial_id`; these are real fields in the rows, not assumed schema. `trial_family_label` exists on only 3 rows. Each identity field was checked independently within outcomes (arm suffixes after `#` removed), as were available labels. The existing `_family` prefers `trial_family_id`, then `trial_id`, then `id`; the patch also accepts `family_id` when the first field is absent.

**0 of 127 within-outcome family buckets contain >=2 rows** (also zero for `family_id` and `trial_id` separately). Thus **0 of 127 rows** belong to repeated-family groups: **0 of 35 rows with direct binary counts**, **0 of 86 effect-only rows**, and **0 of 6 other continuous-input rows**. Alternative count records do not turn an effect-only input into a direct-count input.

Complete group inventory: **none**. There is consequently no group abstract to classify as separate arms versus one comparison. No served shared-control state changes. This zero result is a corpus measurement, not evidence that effect-only grouping was safe; synthetic arm plants exercise the previously uncovered path.

Grouping now partitions endpoint, follow-up, population, comparator and concrete trial/control identity. Same program membership alone cannot join separate trials. Effect-only candidates are HELD with `MULTI_ARM_SHARED_CONTROL_UNDECLARED`; `COMBINE_ARMS` and `SPLIT_CONTROL` cannot release published effects by changing unused/missing counts. Their hold explains the count requirement. `SELECT_ARM` plus an exact `multi_arm_selected_id` retains one prespecified comparison and records all original arms; missing/ambiguous selections stay held. No correlation is inferred.

### Gap 2 measurement: all eight original NOT_STATED rows

Baseline: **8 of 20** reported-effect rows on death/mortality/survival-labelled outcomes were NOT_STATED. Matching the measure, point and both CI ends finds a held sentence for **7 of 8**: **1 of 8 DEATH**, **0 of 8 BENEFIT_EVENT**, **7 of 8 still NOT_STATED** (six sentences name no event; one abstract is absent). Composite VTE outcomes are included because the existing death-outcome guard matches their word "death"; that guard is unchanged.

The exact sentence is retained below. No preceding endpoint-definition sentence is borrowed. The matcher extends the extractor's label-to-point text allowance to handle an explicitly named endpoint, but requires exact numeric equality and the same measure. Conflicting matching sentence orientations remain NOT_STATED.

- **doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 19966341 [outcome 0, row 1]**: HR 1.1 (0.65-1.84); **NOT_STATED**.

> The hazard ratio with dabigatran was 1.10 (95% CI, 0.65 to 1.84).

- **doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 22449293 [outcome 0, row 2]**: HR 1.12 (0.75-1.68); **NOT_STATED**.

> RESULTS: Rivaroxaban was noninferior to standard therapy (noninferiority margin, 2.0; P=0.003) for the primary efficacy outcome, with 50 events in the rivaroxaban group (2.1%) versus 44 events in the standard-therapy group (1.8%) (hazard ratio, 1.12; 95% confidence interval [CI], 0.75 to 1.68).

- **doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 21128814 [outcome 0, row 3]**: HR 0.68 (0.44-1.04); **NOT_STATED**.

> Rivaroxaban had noninferior efficacy with respect to the primary outcome (36 events [2.1%], vs. 51 events with enoxaparin-vitamin K antagonist [3.0%]; hazard ratio, 0.68; 95% confidence interval [CI], 0.44 to 1.04; P<0.001).

- **doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 23991658 [outcome 0, row 4]**: HR 0.89 (0.7-1.13); **NOT_STATED**.

> Edoxaban was noninferior to warfarin with respect to the primary efficacy outcome, which occurred in 130 patients in the edoxaban group (3.2%) and 146 patients in the warfarin group (3.5%) (hazard ratio, 0.89; 95% confidence interval [CI], 0.70 to 1.13; P<0.001 for noninferiority).

- **doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 23808982 [outcome 0, row 5]**: RR 0.84 (0.6-1.18); **NOT_STATED**.

> RESULTS: The primary efficacy outcome occurred in 59 of 2609 patients (2.3%) in the apixaban group, as compared with 71 of 2635 (2.7%) in the conventional-therapy group (relative risk, 0.84; 95% confidence interval [CI], 0.60 to 1.18; difference in risk [apixaban minus conventional therapy], -0.4 percentage points; 95% CI, -1.3 to 0.4).

- **sacubitril-valsartan-hfref / Composite cardiovascular death or heart-failure hospitalization / NCT02468232 [outcome 0, row 1]**: HR 1.0881 (0.6501-1.8212); **NOT_STATED**.

No held record matching pipeline ID `NCT02468232`; no sentence can be quoted or substituted. Its registry quotation is not a held abstract.

- **sglt2-hfref-hosp-cvdeath / Composite cardiovascular death or hospitalisation for heart failure / PMID 32865377 [outcome 0, row 1]**: HR 0.75 (0.65-0.86); **DEATH**.

> RESULTS: During a median of 16 months, a primary outcome event occurred in 361 of 1863 patients (19.4%) in the empagliflozin group and in 462 of 1867 patients (24.7%) in the placebo group (hazard ratio for cardiovascular death or hospitalization for heart failure, 0.75; 95% confidence interval [CI], 0.65 to 0.86; P<0.001).

- **spironolactone-hfref-mortality / All-cause mortality / PMID 28824029 [outcome 0, row 2]**: HR 0.85 (0.53-1.36); **NOT_STATED**.

> The primary endpoint occurred in 29.7% of patients in the eplerenone group vs. 32.7% in the placebo group [hazard ratio=0.85 (95% CI: 0.53-1.36)].

After fallback: **13 of 20 CONSISTENT**, **7 of 20 NOT_STATED**, **0 of 20 polarity mismatches**. The sole served-input state change is **sglt2-hfref-hosp-cvdeath / Composite cardiovascular death or hospitalisation for heart failure / PMID 32865377**, NOT_STATED -> DEATH / CONSISTENT (fixture UNEVALUABLE -> CONSISTENT). The six matched but unstated rows gain sentence provenance without a state change. No served numerical estimate changes; deployed artifacts were not rebuilt.

Plants in `tests/test_effect_only_multiarm_and_polarity.py` cover effect-only holds under undeclared/count rules, single-arm selection, duplicate comparisons, distinct outcomes/timepoints/populations/trials/controls, and survival-oriented same-HR fallback. Different point, either CI end, measure, incomplete CI or adjacent benefit sentence cannot supply polarity. Existing row polarity takes precedence.

Validation: `python -m pytest -q tests/test_effect_only_multiarm_and_polarity.py tests/test_effect_identity.py tests/test_effect_identity_corpus_fixture.py -p no:cacheprovider` -> **120 passed**. Only these three files were run. Fixture JSON and report were regenerated and their exact recomputation test passes. A second-pass comparison of all 127 fixture identities and rule states confirms only the PMID 32865377 polarity state changes. Additional plants reject equal counts across separate reports and inconsistent counts under one explicit control ID. `git diff --check` passes. No commit or deployment.
