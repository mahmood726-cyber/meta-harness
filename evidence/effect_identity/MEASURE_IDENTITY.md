# Measure identity from the model -- the NOAC-AF countercheck (2026-09-27, hash f1867881) -- RETROSPECTIVE, NOT landed

Branch `oc/v101-noac-countercheck`, from the V1.0.1 candidate stack (c15ed111). This keeps the mixed-measure refusal from
over-refusing.

## The rule (`harness/measure_identity.py`)

- **The measure comes from the statistical MODEL.** The model is read from the row's own source text; if the text is silent, it
  comes from the same trial's registry analysis of the SAME outcome.
- **The outcome process is recorded separately** (e.g. rates per year, i.e. time-to-event).
- **The source's wording is kept as its own field, `source_term`.** The word alone never decides.
- **No stated model:** the measure is the source term's, recorded as `model: NOT_STATED`.

### RE-LY (PMID 19717844)

- The abstract: "relative risk, 0.66; 95% CI, 0.53 to 0.82", with rates "per year".
- The held AACT rows (`family_registry.rows.json.gz`): NCT00262600 outcome 258397029, "Yearly Event Rate for Composite Endpoint
  of Stroke/SEE", has analyses 128857122 and 128857123, both **"Cox Proportional Hazard"**.
- So the measure is **HAZARD_RATIO**; source term "relative risk", model COX.
- The registry's values (0.65, 0.9) come from its updated analysis. They supply the MODEL only. The pooled number stays the
  published 0.66.

### An ordinary count RR stays RR

- A registry Cox analysis of a DIFFERENT outcome of the same trial does not transfer.

## CI provenance

ENGAGE AF-TIMI 48 (PMID 24251359) reports HR 0.87 with a **97.5%** CI 0.73 to 1.04. The row now carries:
- the published level and interval;
- the transform: SE = (ln 1.04 - ln 0.73) / (2 x 2.2414) = **0.078953**;
- the **derived ~95% interval 0.7453 to 1.0156**;
- the state DERIVED_95_FROM_PUBLISHED_LEVEL.

The page says it is not a published 95% CI.

## Served effect

`noac-vs-warfarin-af-stroke` was rebuilt on c15ed111 with this branch's files.

| | served at 3876a62d | candidate stack (before this) | this branch |
|---|---|---|---|
| primary | HR 0.8069 (0.6611-0.9850), k 4, flagged "mixed HR+RR" | REFUSED: POOL_MEASURE_MIXED (3 HR + 1 RR) | **HR 0.8069 (0.6611-0.9850), k 4, inputs HR x4, no mixture flag** |

So the stack's NOAC withdrawal, listed in NOTICES.md, is reversed. Against the served page, the number is identical, the false
mixture flag goes, and a provenance block is added.

## Corpus at 3876a62d (`measure_measure_identity.py` -> `measure_identity_3876a62d.json`)

- The model changes the measure in **1 of 86** served effect rows: RE-LY.
- **2** rows say "relative risk" about a time-based process with **no model held**: CORP PMID 21873705, two outcomes. They stay
  RR and are listed, not changed.
- **1** row has a CI level other than 95%: ENGAGE, already correctly converted and now typed.
- **Spironolactone** (refused on the stack for 2 HR + 1 RR) is not changed. Nothing held shows its RR row came from a Cox
  model, so its refusal stands on the evidence.

## Tests

- `tests/test_measure_identity.py` (5) and `tests/test_pool_measure_derived.py`: 17 passed.
- **Guard removal:** ignoring the model turns 2 tests red; letting any outcome's model transfer turns 2 red.
- Dose regimens (Weitz twice-daily vs once-daily) are on `oc/cx-dose-regimen`.
