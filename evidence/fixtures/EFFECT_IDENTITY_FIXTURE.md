# Effect-identity pinned corpus fixture

Pinned source: `3876a62dca66764dff1b4f84d6b43356a1a9e3bb`.

Coverage: 32 served index pages, 97 outcomes, 127 trial rows. Every outcome is inventoried, including those with no trials. Scope is outcomes[].trials[], not declared-absent/recovery inventories.

This is an independent rule audit of frozen served inputs, not a sequential pipeline rebuild. Each probe uses the pipeline's arguments and applicability guard: pinned topic specification, row quotation, cache-first held abstract (docs/cache fallback), and complete same-outcome pool. Reconstruction, normalisation, and holding by one probe do not change another probe's inputs. Synthetic controls never enter totals or denominators. NOT_APPLICABLE reasons are retained on every row in JSON. UNEVALUABLE remains in N; fires counts only known positives.

| Input | Static vs dynamic / hardcode disclosure |
|---|---|
| Commit, previous measurements, control examples | Static: explicitly supplied pin/comparators and synthetic controls |
| Review rows, IDs, specifications, abstracts | Dynamic: read only from pinned git objects; no live network or guessed identifiers |
| Rule outputs and totals | Dynamic: local production functions; no hardcoded research effects or counts |

| Rule | Fires | N | What N counts / fire meaning |
|---|---:|---:|---|
| ci_representation | 0 | 86 | Reported-effect rows; fires if any parsed CI is one-sided or repeated. |
| uncertainty_state | 0 | 86 | Reported-effect rows; fires when uncertainty_state returns an unresolved state. |
| se_permitted | 0 | 50 | Reported-effect rows with at least one parsed CI; fires if any parsed CI is refused an SE (not permission granted). |
| zero_cell_state | 1 | 35 | Count-only rows with ai; fires on DOUBLE_ZERO or SINGLE_ZERO_CELL. Incomplete cells remain in N as unevaluable. |
| DoubleZero | 0 | 35 | Rows taking a binary-count or event/person-time Study.yi_vi path; fires only on the DoubleZero exception. Other refusals remain in N as unevaluable. |
| polarity_check | 0 | 20 | Reported-effect rows on death/mortality/survival outcomes; fires on EVENT_POLARITY_MISMATCH or NORMALISED. |
| multi_arm_groups | 0 | 127 | All served trial rows, grouped within each outcome; fires for each row belonging to a shared-control group (not per group). |
| apply_multi_arm_rule | 0 | 127 | All served trial rows, grouped within each outcome; fires for each row held for undeclared shared control; declared resolutions are separately typed. |
| count_only_under_hr | 0 | 55 | All rows on outcomes whose declared estimand names HR; fires on count-only input without an established HR. |
| hr_route | 2 | 67 | All reported HR rows, using the full served outcome pool and declared estimand; fires when a routing record is returned. |
| reconstruct_from_counts | 2 | 4 | Reported effects with RR/OR target and a different non-HR, nonempty scale (pipeline reconstruction guard); fires on RECONSTRUCTED. |
| transform_provenance | 2 | 86 | All reported-effect rows; fires on an exactly reproduced source-to-served transform. |
| conflict_check | 3 | 6 | Rows with a published point, both CI ends, and complete own/alternative counts; includes NOT_COMPARABLE, never silently drops them. Fires on SOURCE_EFFECT_CONFLICT. |
| published_model | 10 | 127 | All served trial rows (pipeline calls unconditionally); fires if a model is documented rather than NOT_STATED_IN_HELD_TEXT. |
| rate_ratio_labelled_as_rr | 2 | 127 | All served trial rows; fires when served RR quotes a matching effect typed RATE_RATIO or IRR by extract. Unlocated or ambiguous source effects remain in N as UNEVALUABLE. |

## Comparison with previous measurements

An unevaluable comparison is not reported as agreement, even when the known-positive count matches.

- double zero: **AGREES**; previous 0; now 0/35 known fires.
- polarity mismatch: **UNEVALUABLE**; previous 0; now 0/20 known fires.
  - Named unevaluable rows and reasons are listed below.
- undeclared shared control: **AGREES**; previous 0; now 0/127 known fires.
- counts under an HR target: **AGREES**; previous 0; now 0/55 known fires.
- rate ratio labelled as RR: **AGREES**; previous 2/127; now 2/127 known fires.
  - Fires: corticosteroids-covid19-mortality / 28-day all-cause mortality / PMID 32678530 [outcome 0, row 0]
  - Fires: tocilizumab-covid19-mortality / 28-day all-cause mortality / PMID 33933206 [outcome 0, row 0]
- transform provenance: **UNEVALUABLE**; previous 2/86; now 2/86 known fires.
  - Fires: colchicine-recurrent-pericarditis / Recurrent pericarditis / PMID 21873705 [outcome 0, row 1]
  - Fires: colchicine-recurrent-pericarditis / Symptom persistence at 72 hours / PMID 21873705 [outcome 1, row 0]
  - Named unevaluable rows and reasons are listed below.
- HR-in-risk-pool: **AGREES**; previous 2; now 2/67 known fires.
  - Fires: balanced-crystalloids-vs-saline-mortality / Mortality / PMID 34375394 [outcome 0, row 1]
  - Fires: ticagrelor-vs-clopidogrel-acs / Major bleeding / PMID 26376600 [outcome 1, row 1]
- OR reconstructed: **DISAGREES**; previous 1/1; now 2/4 known fires.
  - Fires: corticosteroids-cap-mortality / Hyperglycaemia / PMID 25608756 [outcome 1, row 2]
  - Fires: corticosteroids-covid19-mortality / 28-day all-cause mortality / PMID 32678530 [outcome 0, row 0]
  - Scope: The prior OR-input-only scope reproduces 1/1. The production guard also accepts other incompatible measures; all applicable rows are named below.
  - Evaluated: corticosteroids-cap-mortality / Hyperglycaemia / PMID 25608756 [outcome 1, row 2]; OR -> RR; RECONSTRUCTED
  - Evaluated: corticosteroids-covid19-mortality / 28-day all-cause mortality / PMID 32678530 [outcome 0, row 0]; RR -> OR; RECONSTRUCTED
  - Evaluated: iv-iron-hfref-hosp / Heart-failure hospitalization / PMID 40159390 [outcome 0, row 0]; IRR -> RR; NOT_RECONSTRUCTED
  - Evaluated: tocilizumab-covid19-mortality / 28-day all-cause mortality / PMID 33933206 [outcome 0, row 0]; RR -> OR; NOT_RECONSTRUCTED
- source-effect conflicts: **DISAGREES**; previous 3/4; now 3/6 known fires.
  - Fires: colchicine-recurrent-pericarditis / Recurrent pericarditis / PMID 24694983 [outcome 0, row 0]
  - Fires: probiotics-aad-prevention / Antibiotic-associated diarrhoea / PMID 7872284 [outcome 0, row 8]
  - Fires: tocilizumab-covid19-mortality / 28-day all-cause mortality / PMID 33933206 [outcome 0, row 0]
  - Scope: The prior comparable-ratio-only scope reproduces 3/4. Two published HRs also reach conflict_check and return NOT_COMPARABLE; retained in the broader N.
  - Evaluated: balanced-crystalloids-vs-saline-mortality / Mortality / PMID 34375394 [outcome 0, row 1]; HR -> RR; NOT_COMPARABLE
  - Evaluated: colchicine-recurrent-pericarditis / Recurrent pericarditis / PMID 24694983 [outcome 0, row 0]; RR -> RR; SOURCE_EFFECT_CONFLICT
  - Evaluated: doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 23808982 [outcome 0, row 5]; RR -> HR; CONSISTENT
  - Evaluated: probiotics-aad-prevention / Antibiotic-associated diarrhoea / PMID 7872284 [outcome 0, row 8]; RR -> RR; SOURCE_EFFECT_CONFLICT
  - Evaluated: spironolactone-hfref-mortality / All-cause mortality / PMID 28824029 [outcome 0, row 2]; HR -> RR/HR; NOT_COMPARABLE
  - Evaluated: tocilizumab-covid19-mortality / 28-day all-cause mortality / PMID 33933206 [outcome 0, row 0]; RR -> OR; SOURCE_EFFECT_CONFLICT

## Unevaluable rows

The rate-ratio probe uses extract._EFFECT and extract._effect_from_match with sentence context. It matches the served point and both CI ends (absolute tolerance 1e-6) in source/quotation/source_span, then falls back to held abstract sentences. Conflicting source types or missing matches are UNEVALUABLE. Rows with a quotation and a served scale other than RR cannot fire and remain in N. The synthetic negative control preserves the requested abbreviated quotation and supplies a synthetic held sentence with an explicit CI token, required by extract's regex, to exercise fallback. All unevaluable rows are named below with reasons.

- **polarity_check**: doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 19966341 [outcome 0, row 1] — event orientation not stated in row quotation or unambiguous same-estimate held sentence
- **polarity_check**: doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 22449293 [outcome 0, row 2] — event orientation not stated in row quotation or unambiguous same-estimate held sentence
- **polarity_check**: doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 21128814 [outcome 0, row 3] — event orientation not stated in row quotation or unambiguous same-estimate held sentence
- **polarity_check**: doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 23991658 [outcome 0, row 4] — event orientation not stated in row quotation or unambiguous same-estimate held sentence
- **polarity_check**: doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 23808982 [outcome 0, row 5] — event orientation not stated in row quotation or unambiguous same-estimate held sentence
- **polarity_check**: sacubitril-valsartan-hfref / Composite cardiovascular death or heart-failure hospitalization / NCT02468232 [outcome 0, row 1] — event orientation not stated in row quotation or unambiguous same-estimate held sentence
- **polarity_check**: spironolactone-hfref-mortality / All-cause mortality / PMID 28824029 [outcome 0, row 2] — event orientation not stated in row quotation or unambiguous same-estimate held sentence
- **transform_provenance**: sacubitril-valsartan-hfref / Composite cardiovascular death or heart-failure hospitalization / NCT02468232 [outcome 0, row 1] — no held record matching pipeline id 'NCT02468232'
- **published_model**: esketamine-trd-madrs / Observed-case Day-28 raw change-score MADRS MD / NCT02422186 [outcome 0, row 2] — no held record matching pipeline id 'NCT02422186'
- **published_model**: sacubitril-valsartan-hfref / Composite cardiovascular death or heart-failure hospitalization / NCT02468232 [outcome 0, row 1] — no held record matching pipeline id 'NCT02468232'

## Non-comparable source effects

These calls are evaluable as NOT_COMPARABLE, but cannot establish source-effect agreement; both stay in conflict_check N.

- balanced-crystalloids-vs-saline-mortality / Mortality / PMID 34375394 [outcome 0, row 1] — a published HR is not the crude ratio its counts give; no mislabel test is defined
- spironolactone-hfref-mortality / All-cause mortality / PMID 28824029 [outcome 0, row 2] — a published HR is not the crude ratio its counts give; no mislabel test is defined

## No typed CI available for se_permitted

The following reported-effect rows contain no interval recognised by ci_representation. No typed CI can be passed to se_permitted. These named rows are outside its explicitly typed-CI denominator, but remain in the ci_representation and uncertainty_state denominators. This is a parser limitation, not a finding that the source lacks uncertainty.

- colchicine-recurrent-pericarditis / Symptom persistence at 72 hours / PMID 21873705 [outcome 1, row 0] — ci_representation parsed no interval; no typed CI to pass
- colchicine-secondary-cv-prevention / Trial-defined major coronary/cardiovascular composite / PMID 32865380 [outcome 0, row 1] — ci_representation parsed no interval; no typed CI to pass
- colchicine-secondary-cv-prevention / Trial-defined major coronary/cardiovascular composite / PMID 39555823 [outcome 0, row 2] — ci_representation parsed no interval; no typed CI to pass
- colchicine-secondary-cv-prevention / Non-cardiovascular death / PMID 32865380 [outcome 2, row 0] — ci_representation parsed no interval; no typed CI to pass
- corticosteroids-covid19-mortality / 28-day all-cause mortality / PMID 32678530 [outcome 0, row 0] — ci_representation parsed no interval; no typed CI to pass
- denosumab-vertebral-fracture / New vertebral fracture / PMID 19671655 [outcome 0, row 0] — ci_representation parsed no interval; no typed CI to pass
- doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 24344086 [outcome 0, row 0] — ci_representation parsed no interval; no typed CI to pass
- doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 22449293 [outcome 0, row 2] — ci_representation parsed no interval; no typed CI to pass
- doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 21128814 [outcome 0, row 3] — ci_representation parsed no interval; no typed CI to pass
- doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) / PMID 23991658 [outcome 0, row 4] — ci_representation parsed no interval; no typed CI to pass
- dpp4-mace-t2d / 3-point major adverse cardiovascular events / PMID 23992601 [outcome 0, row 0] — ci_representation parsed no interval; no typed CI to pass
- dpp4-mace-t2d / 3-point major adverse cardiovascular events / PMID 28893244 [outcome 0, row 2] — ci_representation parsed no interval; no typed CI to pass
- glp1-ra-mace-t2d / 3-point major adverse cardiovascular events / PMID 31185157 [outcome 0, row 0] — ci_representation parsed no interval; no typed CI to pass
- glp1-ra-mace-t2d / 3-point major adverse cardiovascular events / PMID 27633186 [outcome 0, row 1] — ci_representation parsed no interval; no typed CI to pass
- glp1-ra-mace-t2d / 3-point major adverse cardiovascular events / PMID 27295427 [outcome 0, row 2] — ci_representation parsed no interval; no typed CI to pass
- glp1-ra-mace-t2d / 3-point major adverse cardiovascular events / PMID 34215025 [outcome 0, row 3] — ci_representation parsed no interval; no typed CI to pass
- glp1-ra-mace-t2d / 3-point major adverse cardiovascular events / PMID 31189511 [outcome 0, row 4] — ci_representation parsed no interval; no typed CI to pass
- glp1-ra-mace-t2d / 3-point major adverse cardiovascular events / PMID 30291013 [outcome 0, row 5] — ci_representation parsed no interval; no typed CI to pass
- glp1-ra-mace-t2d / 3-point major adverse cardiovascular events / PMID 28910237 [outcome 0, row 6] — ci_representation parsed no interval; no typed CI to pass
- iv-iron-hfref-hosp / Heart-failure hospitalization / PMID 25176939 [outcome 0, row 1] — ci_representation parsed no interval; no typed CI to pass
- noac-vs-warfarin-af-stroke / Stroke or systemic embolism / PMID 21830957 [outcome 0, row 0] — ci_representation parsed no interval; no typed CI to pass
- noac-vs-warfarin-af-stroke / Stroke or systemic embolism / PMID 21870978 [outcome 0, row 3] — ci_representation parsed no interval; no typed CI to pass
- omega3-cardiovascular-events / Major vascular events / MACE / PMID 30415637 [outcome 0, row 1] — ci_representation parsed no interval; no typed CI to pass
- omega3-cardiovascular-events / Major vascular events / MACE / PMID 21115589 [outcome 0, row 4] — ci_representation parsed no interval; no typed CI to pass
- pcsk9-mace / Major adverse cardiovascular events / PMID 30403574 [outcome 0, row 1] — ci_representation parsed no interval; no typed CI to pass
- probiotics-aad-prevention / Antibiotic-associated diarrhoea / PMID 24772726 [outcome 0, row 2] — ci_representation parsed no interval; no typed CI to pass
- probiotics-aad-prevention / Antibiotic-associated diarrhoea / PMID 18701826 [outcome 0, row 4] — ci_representation parsed no interval; no typed CI to pass
- probiotics-aad-prevention / Antibiotic-associated diarrhoea / PMID 18410562 [outcome 0, row 5] — ci_representation parsed no interval; no typed CI to pass
- probiotics-aad-prevention / Antibiotic-associated diarrhoea / PMID 7872284 [outcome 0, row 8] — ci_representation parsed no interval; no typed CI to pass
- semaglutide-obesity-mace / 3-point major adverse cardiovascular events / PMID 37952131 [outcome 0, row 0] — ci_representation parsed no interval; no typed CI to pass
- sglt2-ckd-progression / Trial-defined primary cardiorenal composite / PMID 30990260 [outcome 0, row 1] — ci_representation parsed no interval; no typed CI to pass
- sglt2-ckd-progression / Lower-limb amputation / PMID 36331190 [outcome 2, row 0] — ci_representation parsed no interval; no typed CI to pass
- sglt2-hfref-hosp-cvdeath / Composite cardiovascular death or hospitalisation for heart failure / PMID 32865377 [outcome 0, row 1] — ci_representation parsed no interval; no typed CI to pass
- spironolactone-hfref-mortality / All-cause mortality / PMID 10471456 [outcome 0, row 0] — ci_representation parsed no interval; no typed CI to pass
- statins-primary-prevention-elderly / Major vascular events / PMID 42670961 [outcome 0, row 1] — ci_representation parsed no interval; no typed CI to pass
- ticagrelor-vs-clopidogrel-acs / Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke / PMID 19717846 [outcome 0, row 0] — ci_representation parsed no interval; no typed CI to pass

## Reproduction

```text
python evidence/fixtures/build_effect_identity_fixture.py
python -m pytest -q tests/test_effect_identity_corpus_fixture.py -p no:cacheprovider
```

The test compares recomputed JSON and Markdown, checks full inventory and denominator accounting, and checks each synthetic control independently. Missing pinned history is pytest.fail, never a skip.
