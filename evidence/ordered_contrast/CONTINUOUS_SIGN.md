# Continuous sign orientation

Retrospective rule, 2026-09-27, under Mahmood's delegation. Corpus pinned to `3876a62dca66764dff1b4f84d6b43356a1a9e3bb`; this is a source audit, not a regeneration or release of the served site.

## Rule

MD/SMD carry an orientation independently of their numeric value: `INTERVENTION_MINUS_COMPARATOR`, `COMPARATOR_MINUS_INTERVENTION`, `REDUCTION_POSITIVE_FAVOURS_INTERVENTION`, or `NOT_STATED`. For the sleep-onset-latency question, the served convention is intervention change minus comparator change: negative means shorter latency with melatonin. An unordered “versus” or an MD sign alone supplies no subtraction convention.

`contrast_normalisation.negation_for_additive_measures` defaults to `FORBIDDEN`. Only `PERMITTED_WHEN_DECLARED` plus a row declaration `{operation: NEGATION, orientation, estimate, ci_low, ci_high}` can reverse an additive contrast. The original tuple and orientation remain recorded. Recompute `(-estimate, -ci_high, -ci_low)` at the source's printed precision (Decimal, half-even rounding); never use absolute values or destination precision to widen tolerance. Missing, malformed, non-finite, or reversed intervals cannot reproduce. Ratio reciprocal policy, precision rule and log-pool guard remain unchanged.

A positive benefit-coded improvement is not necessarily opposite to an intervention-minus-comparator difference: sleep duration increases while sleep latency decreases. `lower_is_better` must therefore be declared before converting the benefit convention. No orientation or endpoint direction is inferred from a positive/negative number. Unknown orientation or an undeclared required negation is a departure, with equality unset. Even an aligned tuple comparison is not a claim of clinical equivalence or independent corroboration.

**The requested plant has a real CI discrepancy:** negating `6.7 (0.2 to 13.6)` produces `-6.7 (-13.6 to -0.2)`. The supplied pool `-6.70 (-13.63 to +0.23)` matches the point but does not reproduce the CI. `-13.63` rounds correctly; `+0.23` cannot become `-0.2`. Tests preserve this distinction rather than manufacture equality. These numbers are synthetic test plants, not the pinned melatonin result.

## Static versus dynamic disclosure

| Item | Static or dynamic | Evidence / limitation |
|---|---|---|
| Four orientation types, phrase grammar, allowed operations and default prohibition | Static rule | Review-author task; no fitted clinical constants |
| Source orientation and tuple checks | Dynamic | Recomputed from the owning clause and supplied source tuple, separately inside the producer and standalone standard-library verifier |
| Comparator comparison/display | Dynamic | Source-bound clause, original value, declaration and result retained; unknowns withhold numeric agreement/disagreement |
| Census below | Static snapshot | `git show` of the pinned objects; named manual interpretation where a full table/methods section provides more context than the conservative clause parser |
| Synthetic plants | Static tests | Explicit fixtures only; never served as research findings |

## Census scope and method

Inspected **32 of 32** served `docs/reviews/*/review.json` objects, **32 of 32** `cache/<slug>/comparators.json` panels and **29 of 29** held per-topic `comparator_fulltext.txt` files using `git show 3876a62dca66764dff1b4f84d6b43356a1a9e3bb:<path>`. No checkout or git write was used. Exact duplicate mentions of the same endpoint/analysis/tuple are counted once; different CIs, malformed renderings, and opposite-sign prose are retained separately. Census units are additive between-arm contrasts (including comparator trial rows and sensitivity/subgroup estimates), not every continuous baseline measurement, SD, age, dose, regression slope, Egger intercept, or prediction-interval endpoint. Those are not MD/SMD contrasts and cannot acquire orientation through this rule.

All three continuous-review legacy `comparator.reported` arrays are empty in this snapshot; all 32 held/identity panels have **0 extracted continuous effect values**. That does not mean no value is held in text: the full-text census below names **69 of 69 distinct continuous contrast representations**, including secondary outcomes of ratio-based reviews. One is malformed (`-032`) and remains as printed. This census does not silently promote any unextracted value to a served comparator.

### Served rows: 6 of 6, in 3 of 32 reviews

| Topic / outcome | Trial identifier as served | Intervention mean | Comparator mean | Derived MD | Orientation |
|---|---|---:|---:|---:|---|
| esketamine-trd-madrs / Observed-case Day-28 raw change-score MADRS MD | PMID 37025256 (37025256) | -10.1 | -8.1 | -2 | `INTERVENTION_MINUS_COMPARATOR` |
| esketamine-trd-madrs / Observed-case Day-28 raw change-score MADRS MD | PMID 31109201 (31109201) | -21.4 | -17.0 | -4.4 | `INTERVENTION_MINUS_COMPARATOR` |
| esketamine-trd-madrs / Observed-case Day-28 raw change-score MADRS MD | NCT02422186 (TRANSFORM-3) | -10.0 | -6.3 | -3.7 | `INTERVENTION_MINUS_COMPARATOR` |
| melatonin-primary-insomnia-sol / Sleep-onset latency | PMID 20712869 (20712869) | -19.1 | -1.7 | -17.4 | `INTERVENTION_MINUS_COMPARATOR` |
| semaglutide-obesity-weight / Percent change in body weight | PMID 33625476 (33625476) | -16.5 | -5.8 | -10.7 | `INTERVENTION_MINUS_COMPARATOR` |
| semaglutide-obesity-weight / Percent change in body weight | PMID 33567185 (33567185) | -15.6 | -2.8 | -12.8 | `INTERVENTION_MINUS_COMPARATOR` |

Basis: the served row's `source` names its CT.gov arm means; `harness/synth.py::Study.yi_vi` computes `mean1 - mean2`. This is a derivation with identified arms, not an orientation inferred from “vs”. The labels/identifiers above are transcribed from the pinned review objects, not independently re-identified from memory.

Served outcome summaries in the same snapshot: esketamine MD -3.1004 (-7.3323 to 1.1315), k=3; melatonin MD -17.4 (-28.5214 to -6.2786), k=1; semaglutide weight MD -11.8449, k=2, registered pooled CI withheld (`K2_SINGLE_DF`). All inherit the same explicitly derived intervention-minus-comparator convention. The requested -6.70 plant is not the pinned melatonin pool.

### Held comparator contrasts: 69 of 69

Abbreviations in the orientation column: **I** = `INTERVENTION_MINUS_COMPARATOR`; **R** = `REDUCTION_POSITIVE_FAVOURS_INTERVENTION`; **N** = `NOT_STATED`. No held item explicitly states `COMPARATOR_MINUS_INTERVENTION`. **13/69 I, 8/69 R, 48/69 N**. N means the held text does not explicitly resolve the arithmetic convention to the required standard; it does not mean no clinical direction was described. Esketamine's full-text negative-benefit convention plus its lower-is-better scales and semaglutide's paired-mean table support I; a bare single MD clause would remain unknown to the parser.

| # | Comparator topic | Named value / analysis | Estimate, lower, upper (as printed) | Orientation | Source locator / basis |
|---:|---|---|---|---|---|
| 1 | esketamine-trd-madrs | MADRS change, Day 28 | -2.99 -5.10 -0.89 | **I** | Table 3; negative MD favors esketamine; methods define negative change as improvement |
| 2 | esketamine-trd-madrs | MADRS change, Day 2 | -3.25 -4.65 -1.85 | **I** | Table 3; negative MD favors esketamine; methods define negative change as improvement |
| 3 | esketamine-trd-madrs | SDS change, Day 28 | -1.70 -2.61 -0.79 | **I** | Table 3; negative MD favors esketamine; methods define negative change as improvement |
| 4 | esketamine-trd-madrs | MADRS Bayesian sensitivity | -3.02 -5.44 -0.63 | **I** | Robustness and small-study effects; credible interval, same MADRS direction |
| 5 | finerenone-ckd-t2d-renal | UACR, Results | -0.49 -0.53 -0.43 | **N** | Results, SMD; different upper CI from Discussion |
| 6 | finerenone-ckd-t2d-renal | eGFR decline, Results (malformed estimate) | -032 -0.37 -0.27 | **N** | Results prints -032 literally; do not silently repair it to -0.32 |
| 7 | finerenone-ckd-t2d-renal | UACR, Discussion | -0.49 -0.53 -0.46 | **N** | Discussion, SMD; retained separately from Results |
| 8 | finerenone-ckd-t2d-renal | eGFR decline, Discussion | -0.32 -0.37 -0.27 | **N** | Discussion, SMD; reduction/retardation does not explicitly define subtraction |
| 9 | iv-iron-hfref-hosp | 6-minute walk distance, 24 weeks | 14.03 -10.94 38.99 | **N** | Section 3.5, WMD; comparison between FCM and placebo, subtraction not stated |
| 10 | iv-iron-hfref-hosp | KCCQ change | 3.85 -0.55 8.24 | **N** | Section 3.5, WMD; no explicit subtraction/positive-benefit convention |
| 11 | melatonin-primary-insomnia-sol | Sleep latency, fixed effect | 7.06 4.37 9.75 | **R** | Sleep Onset Latency; earlier/reduced latency, positive WMD; Figure 1 defines reduction |
| 12 | melatonin-primary-insomnia-sol | Sleep latency, random effects | 10.18 6.1 14.27 | **R** | Sleep Onset Latency; earlier/reduced latency, positive WMD; Figure 1 defines reduction |
| 13 | melatonin-primary-insomnia-sol | Sleep latency, objective | 5.50 2.29 8.71 | **R** | Sleep Onset Latency; earlier/reduced latency, positive WMD; Figure 1 defines reduction |
| 14 | melatonin-primary-insomnia-sol | Sleep latency, subjective | 10.68 5.78 15.58 | **R** | Sleep Onset Latency; earlier/reduced latency, positive WMD; Figure 1 defines reduction |
| 15 | melatonin-primary-insomnia-sol | Total sleep time, fixed effect | 8.25 1.74 14.75 | **I** | Total Sleep Time; melatonin longer/increased versus placebo, positive WMD |
| 16 | melatonin-primary-insomnia-sol | Total sleep time, random effects | 8.48 -4.02 20.98 | **I** | Total Sleep Time; melatonin longer/increased versus placebo, positive WMD |
| 17 | melatonin-primary-insomnia-sol | Total sleep time, subjective | 11.93 4.06 19.81 | **I** | Total Sleep Time; melatonin longer/increased versus placebo, positive WMD |
| 18 | melatonin-primary-insomnia-sol | Total sleep time, objective | 0.33 -11.19 11.87 | **I** | Total Sleep Time; melatonin longer/increased versus placebo, positive WMD |
| 19 | melatonin-primary-insomnia-sol | Sleep quality, overall (fixed and random same) | 0.22 0.12 0.32 | **R** | Sleep Quality; positive SMD denotes improvement; raw scale direction needs separate declaration |
| 20 | melatonin-primary-insomnia-sol | Sleep quality, subjective | 0.23 0.12 0.34 | **R** | Sleep Quality; positive SMD denotes improvement; raw scale direction needs separate declaration |
| 21 | melatonin-primary-insomnia-sol | Sleep quality, objective | 0.20 -0.04 0.44 | **R** | Sleep Quality; positive SMD denotes improvement; raw scale direction needs separate declaration |
| 22 | metformin-pcos-ovulation | 1.9 BMI overall | -0.04 -0.29 0.21 | **N** | Data and analyses, analysis 1.9; vs heading alone is not subtraction |
| 23 | metformin-pcos-ovulation | 1.9.1 BMI <30 | -0.04 -0.30 0.22 | **N** | Data and analyses, analysis 1.9.1; vs heading alone is not subtraction |
| 24 | metformin-pcos-ovulation | 1.9.2 BMI >=30 | 0.00 -0.82 0.82 | **N** | Data and analyses, analysis 1.9.2; vs heading alone is not subtraction |
| 25 | metformin-pcos-ovulation | 1.10 testosterone overall | -0.41 -0.48 -0.35 | **N** | Data and analyses, analysis 1.10; vs heading alone is not subtraction |
| 26 | metformin-pcos-ovulation | 1.10.1 testosterone BMI <30 | -0.43 -0.50 -0.37 | **N** | Data and analyses, analysis 1.10.1; vs heading alone is not subtraction |
| 27 | metformin-pcos-ovulation | 1.10.2 testosterone BMI >=30 | -0.28 -0.45 -0.12 | **N** | Data and analyses, analysis 1.10.2; vs heading alone is not subtraction |
| 28 | metformin-pcos-ovulation | 1.11 SHBG overall | -1.70 -4.77 1.36 | **N** | Data and analyses, analysis 1.11; vs heading alone is not subtraction |
| 29 | metformin-pcos-ovulation | 1.11.1 SHBG BMI <30 | 1.10 -6.62 8.82 | **N** | Data and analyses, analysis 1.11.1; vs heading alone is not subtraction |
| 30 | metformin-pcos-ovulation | 1.11.2 SHBG BMI >=30 | -2.23 -5.56 1.11 | **N** | Data and analyses, analysis 1.11.2; vs heading alone is not subtraction |
| 31 | metformin-pcos-ovulation | 1.12 fasting glucose overall | 0.01 -0.04 0.06 | **N** | Data and analyses, analysis 1.12; vs heading alone is not subtraction |
| 32 | metformin-pcos-ovulation | 1.12.1 fasting glucose BMI <30 | 0.03 -0.03 0.09 | **N** | Data and analyses, analysis 1.12.1; vs heading alone is not subtraction |
| 33 | metformin-pcos-ovulation | 1.12.2 fasting glucose BMI >=30 | -0.13 -0.28 0.01 | **N** | Data and analyses, analysis 1.12.2; vs heading alone is not subtraction |
| 34 | metformin-pcos-ovulation | 1.13 fasting insulin overall | -1.84 -4.27 0.59 | **N** | Data and analyses, analysis 1.13; vs heading alone is not subtraction |
| 35 | metformin-pcos-ovulation | 1.13.1 fasting insulin BMI <30 | -1.77 -6.04 2.50 | **N** | Data and analyses, analysis 1.13.1; vs heading alone is not subtraction |
| 36 | metformin-pcos-ovulation | 1.13.2 fasting insulin BMI >=30 | -1.88 -4.84 1.07 | **N** | Data and analyses, analysis 1.13.2; vs heading alone is not subtraction |
| 37 | metformin-pcos-ovulation | 2.10 BMI overall | -4.44 -6.11 -2.77 | **N** | Data and analyses, analysis 2.10; vs heading alone is not subtraction |
| 38 | metformin-pcos-ovulation | 2.10.1 BMI <30 | -3.90 -6.20 -1.60 | **N** | Data and analyses, analysis 2.10.1; vs heading alone is not subtraction |
| 39 | metformin-pcos-ovulation | 2.10.2 BMI >=30 | -5.04 -7.47 -2.61 | **N** | Data and analyses, analysis 2.10.2; vs heading alone is not subtraction |
| 40 | metformin-pcos-ovulation | 2.11 testosterone overall | -0.37 -0.60 -0.13 | **N** | Data and analyses, analysis 2.11; vs heading alone is not subtraction |
| 41 | metformin-pcos-ovulation | 2.11.1 testosterone BMI >=30 | -0.37 -0.61 -0.13 | **N** | Data and analyses, analysis 2.11.1; vs heading alone is not subtraction |
| 42 | metformin-pcos-ovulation | 2.11.2 testosterone BMI <30 | -0.20 -1.47 1.07 | **N** | Data and analyses, analysis 2.11.2; vs heading alone is not subtraction |
| 43 | metformin-pcos-ovulation | 2.12 fasting glucose overall | -0.21 -0.29 -0.12 | **N** | Data and analyses, analysis 2.12; vs heading alone is not subtraction |
| 44 | metformin-pcos-ovulation | 2.12.1 fasting glucose BMI <30 | -0.30 -0.64 0.04 | **N** | Data and analyses, analysis 2.12.1; vs heading alone is not subtraction |
| 45 | metformin-pcos-ovulation | 2.12.2 fasting glucose BMI >=30 | -0.20 -0.29 -0.11 | **N** | Data and analyses, analysis 2.12.2; vs heading alone is not subtraction |
| 46 | metformin-pcos-ovulation | 2.13 fasting insulin overall | -6.57 -7.84 -5.29 | **N** | Data and analyses, analysis 2.13; vs heading alone is not subtraction |
| 47 | metformin-pcos-ovulation | 2.13.1 fasting insulin BMI <30 | -15.20 -18.33 -12.07 | **N** | Data and analyses, analysis 2.13.1; vs heading alone is not subtraction |
| 48 | metformin-pcos-ovulation | 2.13.2 fasting insulin BMI >=30 | -4.86 -6.26 -3.47 | **N** | Data and analyses, analysis 2.13.2; vs heading alone is not subtraction |
| 49 | metformin-pcos-ovulation | 3.8 BMI | -5.10 -9.40 -0.80 | **N** | Data and analyses, analysis 3.8; vs heading alone is not subtraction |
| 50 | metformin-pcos-ovulation | 3.9 testosterone | 0.30 -0.82 1.42 | **N** | Data and analyses, analysis 3.9; vs heading alone is not subtraction |
| 51 | metformin-pcos-ovulation | 3.10 fasting glucose | -0.20 -0.79 0.39 | **N** | Data and analyses, analysis 3.10; vs heading alone is not subtraction |
| 52 | metformin-pcos-ovulation | 3.11 fasting insulin | -13.0 -16.96 -9.04 | **N** | Data and analyses, analysis 3.11; vs heading alone is not subtraction |
| 53 | metformin-pcos-ovulation | 6.7 BMI | -3.60 -13.48 6.28 | **N** | Data and analyses, analysis 6.7; vs heading alone is not subtraction |
| 54 | metformin-pcos-ovulation | 6.8 testosterone | -0.16 -1.09 0.77 | **N** | Data and analyses, analysis 6.8; vs heading alone is not subtraction |
| 55 | metformin-pcos-ovulation | 1.9 BMI, largest study (Baillargeon 2004) | 0.00 -0.28 0.28 | **N** | Body mass index narrative, not the overall table row |
| 56 | metformin-pcos-ovulation | 1.12 glucose, sensitivity | -0.09 -0.17 0.00 | **N** | Fasting glucose narrative sensitivity, mmol/L |
| 57 | semaglutide-obesity-weight | O’Neil 2018 | -11.50 -13.68 -9.32 | **I** | Table 3: labelled semaglutide/placebo means numerically reproduce intervention-minus-comparator |
| 58 | semaglutide-obesity-weight | Rubino 2021 | -12.40 -14.75 -10.05 | **I** | Table 3: labelled semaglutide/placebo means numerically reproduce intervention-minus-comparator |
| 59 | semaglutide-obesity-weight | Wadden 2021 | -10.30 -12.00 -8.60 | **I** | Table 3: labelled semaglutide/placebo means numerically reproduce intervention-minus-comparator |
| 60 | semaglutide-obesity-weight | Wilding 2021 | -12.44 -13.37 -11.51 | **I** | Table 3: labelled semaglutide/placebo means numerically reproduce intervention-minus-comparator |
| 61 | semaglutide-obesity-weight | Pooled total | -11.85 -12.81 -10.90 | **I** | Table 3: labelled semaglutide/placebo means numerically reproduce intervention-minus-comparator |
| 62 | semaglutide-obesity-weight | Positive weight-reduction prose (same pooled clinical claim) | 11.85 | **R** | Discussion/Conclusion: reduction of 11.85%; CI not repeated here |
| 63 | ticagrelor-vs-clopidogrel-acs | Platelet reactivity, 6 h, all controls | -45.45 -123.97 33.07 | **N** | Platelet reactivity / Figure 8; clinical lower direction, no explicit subtraction convention |
| 64 | ticagrelor-vs-clopidogrel-acs | Platelet reactivity, 6 h, prasugrel subgroup | -3.65 -40.52 33.22 | **N** | Platelet reactivity / Figure 8; clinical lower direction, no explicit subtraction convention |
| 65 | ticagrelor-vs-clopidogrel-acs | Platelet reactivity, 8 h, all controls | -47.28 -81.14 -13.43 | **N** | Platelet reactivity / Figure 8; clinical lower direction, no explicit subtraction convention |
| 66 | ticagrelor-vs-clopidogrel-acs | Platelet reactivity, 8 h, prasugrel subgroup | -53.57 -117.59 10.10 | **N** | Platelet reactivity / Figure 8; clinical lower direction, no explicit subtraction convention |
| 67 | ticagrelor-vs-clopidogrel-acs | Platelet reactivity, Maintenance, all controls | -53.78 -73.73 -33.82 | **N** | Platelet reactivity / Figure 8; clinical lower direction, no explicit subtraction convention |
| 68 | ticagrelor-vs-clopidogrel-acs | Platelet reactivity, Maintenance, prasugrel subgroup | -44.59 -59.16 -30.02 | **N** | Platelet reactivity / Figure 8; clinical lower direction, no explicit subtraction convention |
| 69 | tranexamic-acid-pph | Peripartum haemoglobin decrease | 0.64 0.39 0.89 | **N** | Results: smaller decrease with TXA but positive MD; signed change vs positive decrease not resolved |

Metformin comparison keys: 1 = metformin versus placebo/no treatment; 2 = metformin + clomiphene versus clomiphene; 3 = metformin versus clomiphene; 6 = metformin versus laparoscopic ovarian drilling. Preserve the subgroup order actually printed (the testosterone subgroups in comparison 2 reverse the usual order). The two extra narrative largest-study/sensitivity tuples are distinct from the 33 tabulated MDs.

The finerenone text contains two incompatible UACR upper CI limits (-0.43 and -0.46) and a malformed eGFR estimate (-032). Neither issue is repaired or interpreted as an orientation change. Tranexamic acid describes a smaller haemoglobin decrease but gives a positive MD: without an explicit signed-change versus decrease-magnitude definition, N is the honest result. Melatonin quality SMDs use positive benefit coding; do not apply the latency convention to quality without declaring the scale direction.

### Complete topic inventory and immutable evidence

Each continuous count refers to the named representations above. A zero means no numeric additive contrast found in that topic's held comparator text/panel; methods-only mentions of MD/SMD are not values. `TEXT_NOT_HELD` denotes an absent per-topic file. Source blob IDs below authenticate the `git show` input.

| Topic | Served continuous rows | Held continuous representations | Comparator fulltext git blob |
|---|---:|---:|---|
| balanced-crystalloids-vs-saline-mortality | 0 | 0 | `679446009e70b131f462374107a662af80f6b3f7` |
| colchicine-postop-af | 0 | 0 | `d047f313ebd5ebb03bddd0bdcb8f529b481d7354` |
| colchicine-recurrent-pericarditis | 0 | 0 | `ba14659a70a3b0a574edeca5554e16f0eba5d4cd` |
| colchicine-secondary-cv-prevention | 0 | 0 | `3abbdd598d5b272fd1b301420695ba6f46283697` |
| corticosteroids-cap-mortality | 0 | 0 | `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391` |
| corticosteroids-covid19-mortality | 0 | 0 | `43588599ee07b19f15892f6659a873e2fd8add2c` |
| dapagliflozin-hfpef-hosp | 0 | 0 | `87798cbc34a10498035e6d0cb7da8eb0f5351e38` |
| denosumab-vertebral-fracture | 0 | 0 | `c1d99d208664499eef0546035414c30e9b434ffc` |
| doac-vte-recurrence | 0 | 0 | `TEXT_NOT_HELD` |
| dpp4-mace-t2d | 0 | 0 | `TEXT_NOT_HELD` |
| empagliflozin-hfpef-hosp | 0 | 0 | `8f0cb80e367448014d33b4dff21f1f6c8204e4db` |
| esketamine-trd-madrs | 3 | 4 | `793c1b614f5ac0b6aa13b42b4e2c1967da426c43` |
| finerenone-ckd-t2d-renal | 0 | 4 | `7b8255ffd28fa39af06186c00efbc474dbe2572c` |
| glp1-ra-mace-t2d | 0 | 0 | `4293339a44b6ccb6619edd7f11c899426f5109ea` |
| iv-iron-hfref-hosp | 0 | 2 | `d363e3ccb11811ff0c16bfda80b396b729cd6194` |
| melatonin-primary-insomnia-sol | 1 | 11 | `2d2a8cd8ff078ec30fa6b992427d57725e239377` |
| metformin-pcos-ovulation | 0 | 35 | `c5b8e1ff8450d90d9312b108b5e7f9afa795d2a1` |
| noac-vs-warfarin-af-stroke | 0 | 0 | `f9a751191b9620813dc41bf92e314413d2bcd945` |
| omega3-cardiovascular-events | 0 | 0 | `d2187d39361f79b6a1c7b5fc8eeb403045d93589` |
| pcsk9-mace | 0 | 0 | `bd3c08d30ebd12ab29ffbf412723df35ddbe53b8` |
| probiotics-aad-prevention | 0 | 0 | `7bf0dc17bc2ffb27d114e953279e3bf0e80e7279` |
| sacubitril-valsartan-hfref | 0 | 0 | `f8281f40faccfbefc54df151377f11ade2ab014d` |
| semaglutide-obesity-mace | 0 | 0 | `114cb00766a76d79eb1fe3a150576c747ce95803` |
| semaglutide-obesity-weight | 2 | 6 | `fc33853490d888c670384cec8bbceb3dbf32b0f3` |
| sglt2-ckd-progression | 0 | 0 | `22d27a28ac4f4eb9b3ed6d50f30953141fb9d4b0` |
| sglt2-hfref-hosp-cvdeath | 0 | 0 | `e5b16e347e231fa813b019398d441fe998811279` |
| sglt2-primary-prevention-hf | 0 | 0 | `TEXT_NOT_HELD` |
| spironolactone-hfref-mortality | 0 | 0 | `f26d21f483d2a725114c5bcdaf825469abeffa25` |
| statins-primary-prevention-elderly | 0 | 0 | `c0be1d6217005aae53a081a78c027e83fa6d682a` |
| ticagrelor-vs-clopidogrel-acs | 0 | 6 | `29033beb0ba822db2a4755fd90f48f296718ce1e` |
| tocilizumab-covid19-mortality | 0 | 0 | `52ea5d89f06a0c4396f9dfa69ffbfd12682782db` |
| tranexamic-acid-pph | 0 | 1 | `f86d359a9e99980f96687a05debf644d4721bb8a` |

## Verification and limits

Only `tests/test_continuous_sign_orientation.py` and unchanged `tests/test_ordered_contrast.py` are run. The independent verifier imports no producer or harness module. Its existing log-ratio pooling engine is not extended to additive pooling: it still refuses unsupported measures before logs. This change types and audits continuous signs, and checks comparator displays; it does not certify new continuous bundles or rebuild the served site.

The sparse worktree lacks `docs/reviews/glp1-ra-mace-t2d/BUNDLE.json`. The corpus-dependent ordered-contrast tests are therefore unavailable: 17 direct FileNotFoundError test failures, 10 FileNotFoundError setup errors, one missing-artefact baseline assertion, and one downstream KeyError after the missing-bundle refusal. These are reported separately; no docs fixture is fabricated or restored.

Final requested-test result: **73 passed, 19 failed, 10 errors**: all **42** continuous-sign tests and **31** self-contained ordered-contrast tests pass. The **29** corpus-dependent outcomes are exactly the missing-docs cases described above. Command: `python -m pytest -q -p no:cacheprovider tests/test_continuous_sign_orientation.py tests/test_ordered_contrast.py --tb=no`. `git diff --check` passes. No git writes, commits, source-data edits, or served-docs changes were made.
