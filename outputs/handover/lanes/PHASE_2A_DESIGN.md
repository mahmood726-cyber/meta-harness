# Phase 2A design — two lists (from the architecture answer + Mahmood's reproducibility decision, 2026-09-16)

## Moves to the reproducible model source (`harness/model_source.judge()`: pinned identity + decoding, verbatim prompt, cached committed response, five acquisition fields, four states with RAN_ERROR ≠ RAN_ZERO, a verified source span behind every field, rule-vs-model disagreement recorded)
| Judgement task | Typed output the model returns (each field with a span) | The RULE that then decides |
|---|---|---|
| Screening eligibility — population | `entry_condition`, `severity_definition` (ICU / IDSA-ATS / PSI / organ support / oxygen threshold), `lvef_threshold`, `hf_acuity` (acute vs chronic; peri-discharge), `ef_phenotype`, `case_confirmation` (lab-confirmed vs suspected), `age_range`, `population_basis` (whole-trial vs prespecified randomised subgroup) | compare typed values to the protocol's executable fields; `PROTOCOL_CRITERION_NOT_EXECUTABLE` where the protocol is silent → decision owed |
| Screening eligibility — arms and contrast | arm list with `drug`, `dose`, `schedule`, `route`, `background_therapy`, `formulation`; the isolated randomised contrast(s) | eligibility from the arm object: drug-in-every-arm, same-class active comparator, strategy bundle, dose ≠ PICO, route ≠ PICO → typed refusal |
| Intervention-class boundary | `intervention_class` (selective SGLT2 vs dual SGLT1/2; steroidal vs non-steroidal MRA; FCM vs derisomaltose; conventional GLP-1RA vs implanted device) | protocol's admitted class list |
| Comparator equivalence | `comparator_class ∈ {PLACEBO, NO_TREATMENT, USUAL_CARE, SAME_CLASS_ACTIVE, OTHER_ACTIVE, ACEI, ARB, ENALAPRIL_SPECIFIC}` | protocol's admitted set (bare "versus placebo" is never written again) |
| Endpoint identity | per reported outcome: `components[]`, `timepoint`, `definition_thresholds`, `is_primary`, `prespecified`, `changed_pre_analysis` | deterministic comparison of component enumerations to the review's canonical set; primary ≠ eligible; co-primary rule |
| Population vocabulary | mapping of the record's population phrase to the protocol's population class ("myocardial revascularization" → cardiac surgery) | cached per phrase; the rule consumes the class |
| Design and conduct | `masking`, `allocation`, `early_termination(reason)`, `run_in_enrichment`, `post_randomisation_exclusion(n, reason)`, `functional_unblinding_risk` | RoB/conduct flags for human adjudication; never eligibility |
| Trial-family proposal | proposed family from acronym / NCT / shared arms | **confirmed only by identifier**; otherwise `FAMILY_PROPOSED_UNCONFIRMED` |

## Stays deterministic (the answer is in the data; a model here adds variance where there was none)
identifier resolution (PMID / NCT / DOI / PMC); family confirmation by identifier; every arithmetic step (pooling, HKSJ, PI, RR/HR/MD from counts or means, common-effect caveat, GRADE inputs); participant-count reconciliation (`PARITY_REFUTED_BY_N`); round-trip checks (published effect vs 2×2); span location and sha/hash/anchor logic; membership, claim ids, input-set versions, the claim graph and UNRENDERABLE; STALE reasons and the five-state completeness classifier once its inputs are typed; rendering. **A model never supplies a number.**

## Gate additions
`verify_all` limb `model_source_discipline` (every model-derived field traces to a committed cached response with pin + verified span; disagreement objects rendered; RAN_ERROR never RAN_ZERO). Acceptance set = the regex failures of 2026-09-16 (truncated title; vocabulary miss; drug-in-every-arm ×3; same-class active ×2; dose; age; diabetes veto; composite identity; undeclared axes) each flipping to the correct decision **with a verified span**, plus a synthetic record whose cited span is absent → refused.

## Open measurement before the RoB rebuild
Lane EP: precision of the cosine ≥ 0.45 registry-outcome decider in `rob2_build.py` (`n of N` pairs, false matches quoted, pages whose RoB rests on one).
