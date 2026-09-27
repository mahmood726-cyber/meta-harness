# Compatibility narrative audit

Retrospective review: 2026-09-27, Dispatch under Mahmood's delegation. Pinned served commit: `3876a62dca66764dff1b4f84d6b43356a1a9e3bb`.

## Corpus census

**24 of 117 served pooled trial rows have a confirmed compatibility/definition narrative contradiction.** A row is one trial within one outcome, including single-trial results. Denominator: every `docs/reviews/*/review.json` at the pin, outcomes with truthy `result.k`, excluding `present: false` and `suppressed_incompatible`. Refused rows are outside this denominator. This is a retrospective source comparison, not a claim that all 117 have complete endpoint provenance.

All 117 inputs, served narratives and row-level adjudications are in [census_inputs.json](census_inputs.json). Each finding below was compared with the bound definition/result or the input's numeric source. Row 79 additionally uses the pinned `cache/probiotics-aad-prevention/records.json`, PMID 11560298: 14 days of treatment; diarrhea recorded for 21 days. Absence of a bound definition is not itself counted as contradiction. Median and maximum follow-up are not treated as interchangeable.

| Row | Topic | Outcome | PMID | Contradiction |
|---:|---|---|---|---|
| 12 | colchicine-secondary-cv-prevention | Non-cardiovascular death | PMID 32865380 | Primary cardiovascular composite substituted for non-cardiovascular death. |
| 13 | corticosteroids-cap-mortality | All-cause mortality | PMID 36942789 | Follow-up says 14 days; the input counts are deaths by day 28. |
| 14 | corticosteroids-cap-mortality | All-cause mortality | PMID 25688779 | Treatment-failure primary composite substituted for in-hospital mortality. |
| 16 | corticosteroids-covid19-mortality | Serious adverse events | PMID 34138478 | Days alive without life support substituted for serious adverse reactions (1/16 versus 0/14). |
| 19 | denosumab-vertebral-fracture | Nonvertebral fracture | PMID 19671655 | New vertebral fracture substituted for nonvertebral fracture. |
| 20 | denosumab-vertebral-fracture | Hip fracture | PMID 19671655 | New vertebral fracture substituted for hip fracture. |
| 28 | doac-vte-recurrence | Major bleeding | PMID 19966341 | Primary recurrent VTE composite substituted for major bleeding. |
| 33 | doac-vte-recurrence | Any bleeding | PMID 19966341 | Primary recurrent VTE composite substituted for any bleeding. |
| 37 | dpp4-mace-t2d | Adverse events | PMID 30418475 | Primary CV death/MI/stroke composite substituted for adverse events. |
| 38 | dpp4-mace-t2d | Hypoglycemia | PMID 30418475 | Primary CV death/MI/stroke composite substituted for hypoglycemia. |
| 54 | glp1-ra-mace-t2d | Gastrointestinal adverse events | PMID 31189511 | Primary MACE composite substituted for gastrointestinal adverse events. |
| 65 | omega3-cardiovascular-events | Major vascular events / MACE | PMID 33190147 | STRENGTH: 5-point primary narrative; input is 3-point SECONDARY, HR 1.05 (0.93-1.19). |
| 67 | omega3-cardiovascular-events | Major vascular events / MACE | PMID 30415628 | REDUCE-IT: 5-point primary narrative; input is 3-point key secondary, HR 0.74 (0.65-0.83). Median 4.9 years and registry maximum approximately 6 years are different summaries, not a timepoint contradiction. |
| 70 | pcsk9-mace | Major adverse cardiovascular events | PMID 28304224 | FOURIER: 5-point primary narrative; input is 3-point key secondary, HR 0.80 (0.73-0.88). |
| 79 | probiotics-aad-prevention | Antibiotic-associated diarrhoea | PMID 11560298 | Follow-up says 14 days (treatment duration); held abstract defines the reported diarrhea outcome over 21 days. |
| 85 | probiotics-aad-prevention | Serious adverse events | PMID 34541475 | Primary AAD outcome substituted for severe adverse events. |
| 95 | sglt2-ckd-progression | Diabetic ketoacidosis | PMID 36331190 | Primary kidney progression composite substituted for ketoacidosis. |
| 96 | sglt2-ckd-progression | Lower-limb amputation | PMID 36331190 | Primary kidney progression composite substituted for lower-limb amputation. |
| 97 | sglt2-hfref-hosp-cvdeath | Composite cardiovascular death or hospitalisation for heart failure | PMID 31535829 | DAPA-HF: primary worsening-HF composite including urgent HF visits described; bound input is SECONDARY CV death or HF hospitalization, HR 0.75 (0.65-0.85), excluding urgent visits. |
| 99 | sglt2-primary-prevention-hf | Hospitalization for heart failure | PMID 28605608 | Primary CV death/MI/stroke composite substituted for hospitalized HF alone. |
| 103 | sglt2-primary-prevention-hf | Lower-limb amputation | PMID 28605608 | Primary CV death/MI/stroke composite substituted for lower-limb amputation. |
| 105 | spironolactone-hfref-mortality | All-cause mortality | PMID 21073363 | Primary CV death/HF hospitalization composite substituted for all-cause mortality (HR 0.76). |
| 114 | tocilizumab-covid19-mortality | Serious adverse events | PMID 33631066 | Primary ordinal clinical-status outcome substituted for serious adverse events. |
| 115 | tocilizumab-covid19-mortality | Serious adverse events | PMID 33332779 | Primary ventilation/death composite substituted for serious adverse events. |

Two separate input defects are not counted as stale descriptions: Alpha Omega (20929341) has a bound definition including cardiac interventions but an incomplete three-component array; J-EMPHASIS-HF (28824029) supplies a primary composite estimate under an all-cause-mortality outcome label. Its primary-composite description matches its actual input. These need endpoint/input repairs outside this narrative change.

## PCSK9 selection declaration

**RESULT_SELECTION_RULE_NOT_DECLARED** at topic/outcome-wide scope. Neither requested enum is declared. The protocol calls MACE ?as defined by each trial? and longest follow-up for the primary MACE endpoint; the 2026-09-16 amendment explicitly restricts closest-component selection to trials registering more than one primary MACE definition. It does not authorize selecting a secondary result instead of a sole primary result. The VESALIUS annotation repeats that scoped rule. No topic or protocol file was edited, and neither global policy was inferred from the implemented selector.

The following are diagnostic alternatives over held abstract composite results, not instructions to pool refused trials. Primary selection uses the declared VESALIUS co-primary tie-break. Closest selection uses the protocol's common cardiovascular/coronary-death, MI and stroke concept; subtype spellings remain disclosed in the candidate objects. Post-hoc status is retained and selection does not override refusal.

| Trial (PMID) | EACH_TRIAL_PRIMARY_COMPOSITE | CLOSEST_TO_COMMON_COMPONENT_SET | Pinned served input / inconsistency |
|---|---|---|---|
| FOURIER (28304224) | 5-point primary HR 0.85 (0.79?0.92) | 3-point key secondary HR 0.80 (0.73?0.88) | Served 3-point; matches closest only. Annotation and definition audit describe 5-point: STALE_NARRATIVE. |
| ODYSSEY OUTCOMES (30403574) | 4-point primary HR 0.85 (0.78?0.93) | Same held 4-point primary | Served 4-point; matches both. Includes CHD death, MI, ischemic stroke, hospitalized unstable angina. Annotation agrees. |
| VESALIUS-CV (41211925) | 3-point co-primary HR 0.75 (0.65?0.86), applying scoped amendment | Same 3-point co-primary | Refused RESULT_INCOMPATIBLE for missing cardiovascular death despite CHD-death allowance in amendment. Does not serve either selection. Alternative 4-point co-primary HR 0.81 (0.73?0.89) is held. |
| ODYSSEY LONG TERM (25773378) | No primary MACE composite; primary is LDL change | Held post-hoc 4-point MACE HR 0.52 (0.31?0.90) | Refused outcome_post_hoc_not_pooled; consistent with prespecification restriction. Diagnostic closest selection is not permission to pool it. |
| GLAGOV (27846344) | No held MACE result; primary is percent atheroma volume | No held MACE result | Refused outcome_not_reported; neither rule has a MACE result to select. |

[held_results.json](held_results.json) contains source-backed candidate definitions and result spans; the new tests verify every span and HR/CI tuple against the pinned abstracts. [selection_report.json](selection_report.json) contains the per-trial function output and verbatim protocol evidence. Registry candidate summaries in the served object are not a complete inventory of numeric results; this comparison explicitly uses the held abstracts requested in the task.

## Implementation and hardcode disclosure

| Item | Static or dynamic | Evidence / limitation |
|---|---|---|
| Policy enums and lexical checks | Static generic code | No PCSK9 IDs, estimates, or trial-specific branches in harness. Unrecognized facts remain unknown. |
| Display description | Dynamic | Derived exclusively from each input's binding/source, components and own time fields. No whole-record abstract or annotation fallback. |
| Contradiction detector | Dynamic, bounded lexical coverage | Explicit role, component, endpoint-subject and time conflicts; absence of a detected conflict is labelled NOT_CONTRADICTED, never verified. Retrospective census additionally uses manual source adjudication; it is not the detector's recall score. |
| Census decisions | Static retrospective adjudications | Every row linked to exact pinned served bytes; 24/117 computed from row records. No simulated data. |
| Held PCSK9 candidates | Static source transcriptions | Verbatim source spans and extracted tuples checked against pin by tests; all five pooled/refused trials included. |
| Result-selection report | Dynamic | Explicit declaration only; both policies returned if undeclared. Unresolved ties reported, not guessed. No pooling arithmetic or eligibility changes. |

Runtime integration: `compat_check` derives endpoint/time dimensions from the input, records STALE_NARRATIVE, preserves original annotations, and replaces the compatibility display table. `page` repeats derivation on a copy before rendering to protect older served objects; the historic definition-audit section is labelled as historical. Original stale text remains in `narrative_audit`, never as the current input description.

No commit, push, rebuild, deployment, project-status update, or git write command was performed.

The final lexical detector flags all 24 adjudicated corpus rows when replayed on the pinned inputs. For PMID 11560298, it flags the conflicting 21-day definition narrative and 14-day follow-up narrative without choosing either as truth: the derived timepoint remains unknown. The pinned held abstract separately establishes the 21-day endpoint for the census. This observed corpus agreement does not establish general semantic completeness.


## Validation

- Final new file: **16 passed** (`python -m pytest -q tests/test_derived_narrative.py --basetemp=.pytest-narrative-plants --tb=short`).
- Existing-test baseline: **66 passed, 24 failed, 10 errors, 1 skipped**.
- Broad changed comparison (including the then-current 14 plants): **79 passed, 25 failed, 10 errors, 1 skipped**.
- Final targeted existing-module recheck plus then-current 15 plants: **60 passed, 3 failed**; two failures reproduce without changes, one is the legacy fallback expectation described below.
- **One additional legacy failure**, `test_compat_underlying.py::test_pre_fix_probiotics_key_fires_on_underlying_trial_rows`, expects whole-record/audit fallback details now deliberately refused. It passes without this change. No existing test was edited.
- The other **34 failures/errors reproduce without this change** (missing served artifacts and verifier fixture permissions). Exact test names, reasons and baseline status: [STUCK_FAILURES.md](STUCK_FAILURES.md); all case-level outcomes: [verification.json](verification.json); broad command and existing-file list: [test_commands.json](test_commands.json).
- `git diff --check`: passed. New plants verify all 117 saved census inputs against the pinned bytes and every held PCSK9 candidate span and numeric tuple against its pinned record.

Final targeted command: `python -m pytest -q tests/test_derived_narrative.py tests/test_compat_underlying.py tests/test_page.py tests/test_narrative_and_mixture_label.py tests/test_derived_label_corpus_fixture.py tests/test_outcome_tiers.py --basetemp=.pytest-narrative-last --tb=line`.
