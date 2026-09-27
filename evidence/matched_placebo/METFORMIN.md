# Metformin-PCOS fixtures (2026-09-27, hash f1643a71) -- RETROSPECTIVE, Dispatch under Mahmood's delegation (NOT landed)

Branch `oc/v101-metformin`, from the V1.0.1 candidate stack (c15ed111).

## (1) Arm-based comparator recognition

- **The defect.** Legro 2007 (PMID 17287476, 626 women) is served as `X3 "no eligible comparator"`. The screen only matched
  phrases ("placebo group", "placebo-controlled", ...), but the abstract names its ARMS: "clomiphene citrate plus placebo,
  extended-release metformin plus placebo, or a combination of metformin and clomiphene".
- **`arm_parse.abstract_arms`** reads those arms. **`arm_based_comparator`** returns the CLEAN contrast against a placebo arm:
  metformin + clomiphene vs clomiphene + placebo, clomiphene held constant ("clomiphene citrate" and "a combination of ...
  clomiphene" are canonicalised to one agent). Metformin + placebo vs clomiphene + placebo is CONFOUNDED and never counts.
- **A registry intervention list is not a list of arms.** Pairing NCT02792400's seven interventions invented "linagliptin vs
  LY2403021 placebo". From such a list, only a placebo matched to the agent, or a two-entry list of the agent and a plain
  placebo, is a comparator.
- **Corpus at 3876a62d** (`measure_x3_comparator.py` -> `x3_comparator_3876a62d.json`): **175** served X3 "no eligible
  comparator" exclusions.
  - **5** now pass X3; **4** are now INCLUDE: Legro, and the DPP-4 registry records NCT02192853 (sitagliptin vs placebo),
    NCT00918879 (saxagliptin vs placebo) and NCT02792400 (linagliptin vs its matched placebo).
  - NCT02280057 (metformin) passes X3 and stops at X-DESIGN.
- **Legro's ovulation numbers are not held.** No registry results for NCT00068861, no full text; the abstract reports live birth
  and conception, not ovulation.
  - Included at screening, it is declared absent (OUTCOME_NOT_IN_SOURCE), so **k stays 3**.
  - The review's k=4 diagnostic OR 1.8031 (0.3861-8.4193) cannot be reproduced from held bytes and is not entered.
  - Legro joins the pool when its ovulation counts are held.
- **Served move (a notice):** screening flow only. Legro and three DPP-4 records move X3 -> INCLUDE. Rebuilt: no pooled number
  moves in metformin or dpp4.
- **Dual screening:** screener 2 still excludes Legro. Its full-abstract population check hits "first-trimester" (in "rates of
  first-trimester pregnancy loss"), which is on metformin's population exclusion list. The disagreement is recorded as dual
  screening does; screener 1 adjudicates.

## (2) Outcome definition record (`harness/outcome_definition.py`)

- **The defect.** The served label `endpoint_canonical_status: HOMOGENEOUS` was ASSERTED: `endpoint_canonical._component_tokens`
  returns the fixed token `["OVULATION"]` for every metformin trial.
- **The record.** Each trial's record (criterion, woman vs cycle denominator, treatment sequence, stopping rules, observation
  period) is read from its held text, and the status is derived:

| field | Ben Ayed 19522426 | Moll 16769748 | Vandermolen 11172832 | state |
|---|---|---|---|---|
| criterion | follicle > 16 mm + estradiol + endometrium (+ ultrasound) | not stated | serum progesterone >= 4 ng/mL | HETEROGENEOUS |
| denominator | not stated | not stated | women ("9 of 12 participants ... ovulated") | NOT_STATED |
| sequence | clomifene + metformin / + placebo | clomifene + metformin / + placebo | placebo or metformin for 7 weeks | HETEROGENEOUS |
| stopping | "three trials maximum" | not stated | "six ovulatory cycles, became pregnant, or ... anovulation on 150 mg CC" | HETEROGENEOUS |
| observation | not stated ("within 7 months" is recruitment) | not stated | 7 weeks | NOT_STATED |

- **Derived status: DEFINITION_HETEROGENEOUS.** `endpoint_canonical` keeps the component status as `component_status`.
- **Correction to the review's attribution:** in the held bytes, the stopping rule "until pregnancy, 6 ovulatory cycles or
  resistance" is **Vandermolen's (11172832)**. Moll's held text (its full text is 11 KB, essentially the abstract) states no
  criterion, stopping rule or observation period.
- **Served move (a notice):** the endpoint label moves HOMOGENEOUS -> DEFINITION_HETEROGENEOUS. The pooled OR 2.0733
  (0.0922-46.6008), k=3, is unchanged.

## (3) Narrative (`narrative_rules.check_or_narrative`, gate `check_narrative_or_magnitude`)

- An OR is never worded as a probability ratio ("twice as many women", "2-fold more likely").
- An uninformative interval (ratio span >= 10-fold; 0.09-46.6 spans 518-fold) carries no magnitude word.
- Verbatim quotations of held text pass, and "doubling of serum creatinine" is an endpoint name.
- No served page violates either rule today (scan of all 32 pages). The gate passed on the metformin, dpp4 and sglt2-ckd
  rebuilds.

## Checks

- **Tests:** `tests/test_metformin_fixtures.py` (12) with `test_matched_placebo.py` and `test_narrative_and_mixture_label.py`,
  60 passed in total.
- **Guard removal:** no arm-based comparator turns 4 tests red; status always HOMOGENEOUS turns 1 red; OR wording unchecked
  turns 2 red.
