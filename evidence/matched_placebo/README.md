# "Placebo for X" is a placebo matched to X -- and "every arm" means every arm (NOT for landing without Mahmood's signature)

External review of empagliflozin-hfpef-hosp, 2026-09-27.

## The defect, reproduced

SAK-HFpEF (NCT05138575) is served as `X-CONTRAST`: "the intervention of interest appears in every structured CT.gov arm
entry". Its arms (held record, `records.json` `ctgov`):

| arm | label | exposure to empagliflozin |
|---|---|---|
| A | Empagliflozin + Potassium Chloride | ACTIVE |
| B | Empagliflozin + Potassium Nitrate | ACTIVE |
| C | Potassium Chloride + Placebo for Empagliflozin | **MATCHED_PLACEBO** (was read as ACTIVE) |

`screen._record_arm_interventions_background_only` tested `"empagliflozin" in label`. That is a substring test, so it read
C as exposed. `arm_object._arm` made the same mistake and gave arm C `drug = empagliflozin`. The AACT route
(`armcontrast._norm_intv`) already dropped placebo interventions, but SAK has no AACT arm rows, so it reached the
fallback.

The same function had a second defect. It removed a plain `Placebo` arm *before* testing "every arm". So a dose-ranging
trial with a placebo arm read as "the drug is in every arm".

## The fix (`harness/arm_parse.py`, used by `screen.py` and `arm_object.py`)

- **Arm parsing.** Each arm label is split into components:
  - `placebo for X`, `placebo X`, `X placebo`, `X-matching placebo`, `matching placebo for X`, `placebo (X)` and
    `placebo to match X` all become MATCHED_PLACEBO(X). They are never exposure to X.
  - `X/X placebo` means two levels collapsed into one listed arm, so exposure is VARIES_WITHIN_ARM.
- **"Every arm".** `interest_in_every_arm` is true only when every listed arm is ACTIVELY exposed. A matched-placebo arm, a
  plain placebo arm or a varying arm makes it false. The check can still only remove a provable background inclusion.
- **Ordered contrasts.** `ordered_contrasts` returns every (exposed arm, unexposed arm) pair:
  - SAK A vs C is **CLEAN**: empagliflozin vs matched placebo, potassium chloride held constant.
  - B vs C is **CONFOUNDED**: KNO3 and KCl also differ.
  - A vs B is not an empagliflozin contrast.
  - The arm object now carries these as `ordered_contrasts`, and the placebo arm's `drug` is `placebo` with
    `matched_placebo_for = empagliflozin`.
- **Design on the contrast.** `design_object` reads the held registry design. For SAK it records `CROSSOVER`
  (`registry_designs.json`: intervention_model CROSSOVER, "3 interventions will be randomized and administered in a
  double-blind fashion"). The contrast carries `within_person: true`, plus the requirement that periods are never treated
  as independent parallel arms.
  - **Not in the held bytes:** the number of periods, the 6-week period length, the ~2-week washouts and carryover
    handling. The review states these from the protocol, but they are recorded as `NOT_IN_HELD_BYTES`, not filled in.
    They need the protocol held as a source first.

## Corpus-wide, at the pinned candidate 3876a62d (`measure.py` -> `measure_3876a62d.json`)

- **15** served `X-CONTRAST` exclusions across 32 reviews. **7** were made by the arm-list fallback; the other 8 came from
  curated evictions, the AACT arm index or arm-object background rules, and are listed but not re-judged.
- **6 of the 7 are wrong**:

| cause | n | trials |
|---|---|---|
| matched-placebo phrasing read as exposure | **2** | SAK-HFpEF NCT05138575 ("Placebo for Empagliflozin"); Neu I NCT00816673 ("placebo Circadin") |
| two levels collapsed into one arm label | 1 | VITAL-Echo NCT01630213 ("fish oil/fish oil placebo") |
| a plain placebo arm dropped before "every arm" | 3 | DRC-04 NCT03376698; SYNAPSE NCT01998958; NCT01968668 (BAY94-8862 doses + placebo) |

- The 7th, DANNOAC-VTE NCT03129555 (four DOACs head-to-head), stays correctly excluded.
- So the answer to "how many X-CONTRAST exclusions come from matched-placebo phrasing" is **2 of 15** (2 of the 7 made by
  the arm-list route). Counting the collapsed factorial label as matched-placebo phrasing makes it 3.

## What moves (a notice, not a landing)

Re-screened with the fixed code, each of the six is now `INCLUDE` at eligibility
("eligible double-blind/placebo-controlled RCT ..."). That changes the served screening flow on six pages. Whether any
pooled number moves depends on whether these registry records carry usable results. That needs the six topics rebuilt,
which is **not yet done**. Every such move is a notice for Mahmood's hash-bound signature.

## Tests

`tests/test_matched_placebo.py` (23 passed) contains:

- **Plants.** The served SAK decision; the pre-fix `screen.py` at 887fea85 still calls SAK background; the pre-fix arm
  object's substring drug.
- **Parse table.**
- **Contrasts.** A vs C CLEAN, B vs C CONFOUNDED.
- **Crossover design.** Only held facts are filled.
- **Other cases.** The five corpus shapes, including MIRO-CKD and DOAC-vs-DOAC, which must stay background.
- **n of N.** Recomputed against the stored measurement.

Across the arm, contrast and screen suites, the same 38 tests fail with and without the fix (sparse-tree files). None are
caused by it.
