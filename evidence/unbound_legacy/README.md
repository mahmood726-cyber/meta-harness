# UNBOUND_LEGACY fail-open: reproduced, fixed on a branch, impact measured (NOT for landing without Mahmood's decision)

External audit, 2026-09-26. `harness/target_endpoint.admissibility()` (blob 1b309c5b at v1/candidate 3876a62d) refuses a classified
non-target row but ADMITS a row with no endpoint class as `UNBOUND_LEGACY`, and `admit_rows()` keeps it. The invariant:
**losing endpoint identity must never increase admissibility.**

## 1. Reproduced on the real function (`repro.py`)

The rows come from held bytes (GLP-1 records.json at 3876a62d). The class comes from the real `classify_bound`, and the verdict
from the real `admissibility` and `admit_rows`.

| case | class | pre-fix (1b309c5b) | fixed |
|---|---|---|---|
| LEADER 3-point, HR 0.87 (0.78-0.97) | EXACT_TARGET | admitted | admitted |
| ELIXA 4-point, HR 1.02 (0.89-1.17) | NEAR_MATCH | refused (RESULT_INCOMPATIBLE) | refused |
| ELIXA, class forced to DIFFERENT_OUTCOME | DIFFERENT_OUTCOME | refused | refused |
| **ELIXA, class deleted** | none | **ADMITTED, UNBOUND_LEGACY** | **abstains, ENDPOINT_IDENTITY_MISSING** |
| restore | NEAR_MATCH / EXACT_TARGET | as first | as first |

Correction to the finding as relayed: the real classifier puts ELIXA's 4-point composite in **NEAR_MATCH** (3-point plus
hospitalisation for unstable angina; GLP-1 declares no near-match permission), not DIFFERENT_OUTCOME. Both are refused, so the
finding stands.

## 2. The fix (`harness/target_endpoint.py`)

- A non-hand row with no class, or a class the module does not define, now ABSTAINS with `ENDPOINT_IDENTITY_MISSING`. It is never
  admissible. The conservative composite-mismatch refusal still comes first, and a test shows it actually fires.
- `_class_verdict`'s fallthrough for an unknown class returned `admissible: None` (UNCLASSIFIED). It now abstains the same way.
- `admit_rows` records the abstention's own code; it used to always write ENDPOINT_UNBOUND. The row stays visible as
  EXTRACTION_DEBT, with its candidate tuple.
- One existing test **defended the defect**. `test_m2_hand_row_binding.py::test_registry_and_derived_rows_keep_unbound_legacy_and_are_still_admitted`
  asserted that registry and derived routes are ADMITTED as UNBOUND_LEGACY. It is rewritten as the requirement: they abstain, and
  their tuple stays visible.

## 3. Corpus-wide impact at the candidate (`measure.py` -> `impact_3876a62d.json`)

- **65 of 127** served pooled rows (all outcomes) are admitted only through UNBOUND_LEGACY, on **22 of 32** topics. GLP-1 has 0.
- Primary outcomes: **51 of 87** served primary pooled rows are UNBOUND_LEGACY.
- **19 of 27** served primary pools would change under fail-closed:
  - **17 withdrawn (k -> 0).** Every row of the pool is legacy, so this is derived from membership alone.
  - **2 come to include 1 (the no-difference line).** Each served pool was first reproduced from its rows with the producer's
    own `synth.pool`, and only then recomputed without the legacy rows:
    - noac-vs-warfarin-af-stroke: 0.807 (0.661-0.985) -> 0.838 (0.379-1.853), 2 of 4 rows legacy
    - sglt2-ckd-progression: 0.684 (0.554-0.844) -> 0.670 (0.236-1.903), 1 of 3 rows legacy
- Secondary and harms: 8 more pools are withdrawn. ticagrelor major bleeding (1 of 2) did not reproduce, so no move is claimed.

## 4. Why so many: the abstract route never classifies these topics (`classify_legacy_rows.py`)

51 of the 65 legacy rows came from the **abstract** route, not from registry or hand routes. For these topics the classifier was
never run, so they reached the gate with no class. Running the real `classify_bound` on each row's held abstract gives:

| class | rows |
|---|---|
| EXACT_TARGET | **8** (would stay admitted under classify-then-gate) |
| ENDPOINT_UNBOUND | **43** (the binder cannot bind single-outcome result sentences such as "no effect on risk of AAD (RR 0.81...)" -- it is built around composite components) |
| not an abstract row: registry / derived | 14 (identity must come from the registry outcome measure) |

## 5. Options for Mahmood (a decision, not an engineering default)

- **A. Land fail-closed now.** 17 primary pools are withdrawn and 2 cross null, all as notices. This is honest, but most of the
  site loses its primary result until binding catches up.
- **B. Fail-closed plus classify every route first.** This rescues 8 rows and changes little on its own, because of the binder gap.
- **C. Fix the binder for single-outcome results, and bind registry rows to their outcome-measure titles, then fail-closed.** This
  gives the smallest honest move, but it is real producer work. It is the recommended order: a producer must not be left in a state
  where deleting a field raises admissibility, and the served numbers should move once, for a known reason.

Every served-number move is a notice for Mahmood's hash-bound signature. Nothing here lands unsigned.
