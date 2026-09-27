# V1.0.1 -- GLP-1 family population read from source evidence (branch evid2/v101-population)

From the auditor's record of the live release 9eacfe09 (MetaHarness_search_screening_20260927_0002UTC.json). Their
finding: "ELIXA, HARMONY and SELECT retain ENTRY_POPULATION_NOT_ESTABLISHED; code still reads conditions rather than
criteria/report evidence and positive match precedes exclusions." Their next action: "verify ELIXA/HARMONY T2D
established and SELECT excluded without treating population passage as full eligibility."

Main is frozen; this branch is for the V1.0.1 candidate.
- **Pooled results moved: 0 of 32.** The GLP-1 pool is unchanged (k = 8); HARMONY was already pooled.
- **Topics whose served content changed: 1 of 32** (glp1-ra-mace-t2d). The other 31 are code pins only.

## Root cause
`screen_family` (harness/trial_family.py) decided the population from the registry `conditions` list, which is the
registrant's topic label and not an entry criterion:
- ELIXA lists "Acute Coronary Syndrome";
- HARMONY lists "Diabetes Mellitus";
- SELECT lists "Overweight; Obesity".

It also tested the positive match before the `population_none` exclusions. The held registry eligibility criteria
(AACT eligibilities.criteria, held for all 84 unresolved families) and the held primary abstracts were never read.

## The fix: harness/population_witness.py, one axis read through the harness (no hand edits)
- **Witnesses (strong):**
  - the registry eligibility criteria, split into inclusion and exclusion items (inline headers and " - " bullets
    handled);
  - the primary report's own enrolment sentence ("we randomly assigned/enrolled ..."), outside
    BACKGROUND/RESULTS/CONCLUSIONS.
- **Witness (weak):** the registry conditions label. It may establish the population only when every strong
  witness is silent, and it never outvotes an entry statement.
- **Exclusions first.** A population exclusion is decided before any design axis abstains, and the family is then
  INELIGIBLE on population. Possible outcomes are EXCLUDED, CONFLICT, MIXED, ESTABLISHED and NOT_ESTABLISHED.
- **Population passage is one axis, never eligibility.** An ESTABLISHED family continues through the contrast,
  blinding and placebo checks. The auditor's caution is a test (ELIXA/HARMONY are ELIGIBLE only because those passed
  too).
- **Terms come only from the topic config** (`population_any` / `population_none`). The only equivalence added at
  match time is hyphen/space/comma.
- **Gated on the protocol's structured declaration.** The route applies where the B-prime eligibility line declares
  the entry population; only glp1 does ("in adults with type 2 diabetes"). The diabetes-specific rules (a negated
  diabetes condition; a generic "diabetes" exclusion) apply only to a declared diabetes population.
  - Measured: regenerating the family ledger of all 32 topics under main's code and under this code, **only glp1
    changes (3 families)**.
  - The other 31 topics keep the legacy screen and are NOT yet migrated. A survey with the new reader shows they
    would change, e.g. a diabetes-negation rule read against an obesity-without-diabetes population. Each needs its
    own validation.
- **The page:** the family ledger gains an "Entry population (source evidence)" column with every witness's verbatim
  quote. Eligibility spans carry the deciding witnesses.

## Fixtures (tests/test_population_witness.py)
| family | before (live) | now | criteria witness | primary report witness |
|---|---|---|---|---|
| ELIXA NCT01147250 | UNKNOWN ENTRY_POPULATION_NOT_ESTABLISHED | **ELIGIBLE**, population ESTABLISHED | inclusion: "Participants with a history of type 2 diabetes ..." | PMID 26630143: "We randomly assigned patients with type 2 diabetes who had had a myocardial infarction ..." |
| HARMONY Outcomes NCT02465515 | UNKNOWN ENTRY_POPULATION_NOT_ESTABLISHED (pooled without structural eligibility) | **ELIGIBLE**, population ESTABLISHED | inclusion: "Diagnosis of type 2 diabetes." | PMID 30291013 (held abstract): "We randomly assigned patients aged 40 years and older with type 2 diabetes and cardiovascular disease ..." |
| SELECT NCT03574597 | UNKNOWN ENTRY_POPULATION_NOT_ESTABLISHED | **INELIGIBLE on population** (EXCLUDED) | exclusion: "History of type 1 or type 2 diabetes (history of gestational diabetes is allowed)" | PMID 37952131: enrolment sentence "... but no history of diabetes" |

Plants cover the reader's refusals, each found in the GLP-1 criteria during this work:
- LEADER's inline "Exclusion Criteria: - Type 1 diabetes" had been read as part of an inclusion item.
- "not on oral anti-diabetic medications", "without metformin as only diabetes therapy", "No ocular treatment for
  diabetic retinopathy", "Other than diabetes, subjects must be in good general health", "any clinically significant
  disease other than type 2 diabetes" and "Type 1 diabetes, special types of diabetes, or gestational diabetes" are
  NOT population exclusions.
- "(except type 1 or 2 diabetes)" (NCT01234649) IS one.
- "Type 1 or type 2 diabetes" is MIXED.

## GLP-1 count chain (live -> now)
| | live 9eacfe09 | now |
|---|---|---|
| trial families | 238 | 238 |
| eligible families | 143 | **145** |
| eligibility unresolved | 84 | **81** |
| contributing | 8 | 8 |
| contributing without structural eligibility | NCT02465515 (HARMONY) | **none** |
| bundle: admissible pool rows | 7 of 8 | **8 of 8** (HARMONY passes P5) |

## n of 84 (the families unresolved on the live release, re-run; evidence/v101_population/N_OF_84.json)
**Population axis:**
- **established 83 of 84**:
  - 66 by an inclusion criterion;
  - 2 by an inclusion criterion AND the primary report (ELIXA, HARMONY);
  - **15 only by the registry conditions label, because their criteria are silent** on the population (e.g. HbA1c
    and background-therapy rules only). On entry evidence alone these 15 are still unresolved: **68 established, 15
    unresolved on population**.
- **excluded 1 of 84**: SELECT.
- **still unresolved on population: 0 of 84** (15 on entry evidence alone, as above).

**Eligibility (all axes):**
- **ELIGIBLE 2 of 84** (ELIXA, HARMONY);
- **INELIGIBLE 1 of 84** (SELECT, on population);
- **still UNKNOWN 81 of 84**, every one on a DESIGN axis this change does not touch:
  - **PARALLEL_DESIGN_NOT_PROVEN, 40:** the registry records CROSSOVER for 34, SINGLE_GROUP for 3, FACTORIAL for 2 and
    SEQUENTIAL for 1;
  - **INTERVENTION_CONTRAST_NOT_PROVEN, 34:** mostly active-comparator arms (glimepiride, glibenclamide, sitagliptin),
    but some list a placebo arm the contrast reader did not bind;
  - **BLINDING_NOT_PROVEN, 7:** masking SINGLE for 6, NONE for 1.

**Finding for the next pass (not changed here):** 47 of the 81 are UNKNOWN although the registry states a design the
B-prime protocol excludes: 40 non-parallel and 7 not double-blind. That is the same abstain-on-a-proven-fact shape
the auditor flagged for population. Deciding them INELIGIBLE is a design-axis change for its own review.

## Known limits, stated
- **Error rate measured:** a fixed-seed sample (seed 20260927) of 20 ESTABLISHED GLP-1 families was checked by hand.
  19 are correct. NCT02759107 reads "Healthy participants (Parts A and B) and participants with T2DM" -- a mixed
  population the reader cannot see, because "healthy" is not a config exclusion term. The term was not added after
  seeing the data. The sample is burned for tuning.
- **Reader author = labeller**, which is a weakness.
- **The certified family caches are not byte-identical to a regeneration, and this predates the branch:**
  build_families --offline --check reports 23 of 32 DIFFERENT with this branch's code, and main's own code also
  reports DIFFERENT on the 3 topics tried (balanced-crystalloids, dpp4, glp1). The eligibility states regenerated
  under main's code and under this code differ only on glp1's 3 families. Only glp1's cache was regenerated here,
  and its semantic diff against the committed cache is exactly this change.
