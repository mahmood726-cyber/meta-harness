# ONE component-by-component compatibility rule for admitted and refused rows (branch only; admission changes are notices)

External review of colchicine-secondary-cv-prevention, 2026-09-26.
- COPS (PMID 32862667) was refused by a hand entry in `docs/refusals.json` as "a broader composite
  (mortality+ACS+revascularisation+stroke) than a 3-point MACE".
- The admitted trials are not 3-point either. COLCOT adds resuscitated cardiac arrest and urgent angina hospitalisation leading to
  revascularisation; LoDoCo2 and CLEAR add ischaemia-driven coronary revascularisation.
- The admitted rows never met a component rule at all (they are UNBOUND_LEGACY), so two different rules judged the two sides.

## The rule (`harness/composite_rule.py`; wired through `outcome_tiers.composite_compatibility`)

- **Read components.** Each row's definition is read into typed components (CV_DEATH, ALL_CAUSE_DEATH, MI, ACS, STROKE,
  CARDIAC_ARREST, CORONARY_REVASC, UA_HOSP, UA_HOSP_REVASC, HF_HOSP).
  - An admitted row uses its own served definition first, because the pooled outcome is not always the trial's primary composite.
  - A composite-refused row uses its held abstract's "primary ... was a composite of" sentence.
- **Type the differences** against the core: `ADDED:x`, `MISSING:x`, `SUBSTITUTED:<broader>_FOR_<core>` (all-cause death for CV
  death; ACS for MI). The rule reads **definitions only**, never an effect.
- **Core.** It is a policy's core, else the outcome's declared components, else 3-point **only for a MACE-type outcome**. A
  heart-failure composite has no declared core, so it is not judged.
- **Decision.** A predeclared `composite_component_policy` lists the difference types kept in PRIMARY. The existing predeclared
  near-match permission (`allow_near_match` / `component_compat_key`) counts as "additions allowed; substitutions and missing
  components not". **With no policy, nothing is allowed**, so a rule that refuses one broader composite flags every broader one.
- **Stated vocabulary equivalences.** Coronary-heart-disease death counts as CV death (the existing classifier's own rule).
  "Death from vascular causes" is the CV-death component of ACS trials (PLATO's wording).

## Colchicine-secondary under the rule (served rows at v1/candidate 3876a62d)

| trial | served | components vs the 3-point core | default rule (no policy) |
|---|---|---|---|
| COLCOT 31733140 | admitted | ADDED cardiac arrest, ADDED urgent angina hosp.->revasc | SEPARATE |
| LoDoCo2 32865380 | admitted | ADDED coronary revascularisation | SEPARATE |
| CLEAR 39555823 | admitted | ADDED coronary revascularisation | SEPARATE |
| COPS 32862667 | refused ("broader") | SUBSTITUTED all-cause death for CV death, SUBSTITUTED ACS for MI, ADDED revascularisation | SEPARATE |

- **The plant fires.** The served state refuses COPS as broader while admitting three broader composites. The rule gives all four
  the same verdict and reports COPS as a refusal judged like an admitted row.
- **Either or, never both.** A policy that allows what COPS has admits COPS too (tested). A policy that allows only additions keeps
  COLCOT, LoDoCo2 and CLEAR in PRIMARY and sends COPS to SEPARATE for a stated, different reason: substitution, not "broader".
- **COPS's other reason is independent.** Its "events" ambiguity (recurrent vs patients, no HR) is not a component question and
  stays its own refusal.

## Corpus-wide (`measure_composite_rule.py`; the pipeline's own functions)

**3 of 25** judged rows change admission under the uniform default rule, all in colchicine-secondary (COLCOT, LoDoCo2, CLEAR:
admitted -> separate analysis).
- 1 refusal is judged like an admitted row (COPS).
- 2 refused rows have no readable definition and are not judged (Akrami 34876021; COColchicine-PCI 32295417, whose refusal is
  really about timepoint and scope).

The other six composite topics show **0 changes**: GLP-1, dpp4, omega3, pcsk9, semaglutide-MACE, ticagrelor. The uniform rule
agrees with the gates those rows already passed, which validates it.

The first measurement said 18 of 30. That was the instrument, corrected before reporting:
- it read the trial's primary composite for pooled non-primary outcomes;
- it judged heart-failure outcomes against a MACE core;
- it lacked the "CV death" / "death from cardiovascular disease" / "vascular death" / CHD-death wordings.

## Notices if landed (for Mahmood and the topic owner)

With no `composite_component_policy`, colchicine-secondary's primary loses all three admitted trials to the separate analysis
(served 0.8134, k=3). Declaring a policy is the topic owner's protocol decision:
- allowing the additions keeps the three in primary and sends COPS to separate for its substitutions;
- allowing COPS's substitutions too admits COPS on components, and it is then blocked only by its own "events" ambiguity.
