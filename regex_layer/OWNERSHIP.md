# Regex layer -- file ownership between lanes (2026-09-24 to 2026-09-26 15:00)

The RAI lane (`rai/*` branches) owns the regex layer: R1 typed values, R2 per-pattern precision/recall, R3 a named plant
per pattern, R4 refusal of partial / ambiguous matches. The main lane keeps the §F audit contract.

Decided from the main lane's branch `enforcement-gate` (the files it changes). The RAI lane edits ONLY files in the
first list; a file in the second list is changed by the main lane only.

## RAI lane (regex layer)
- `regex_layer/**`, `tests/test_regex_plants.py`, `tests/test_regex_measure.py`, `scripts/measure_regex_layer.py`,
  `outputs/regex_layer/**`
- `harness/extract.py` (pinned: a change re-certifies every page, so it is ONE batched change, held for Mahmood where it
  moves a served number)
- `harness/screen.py`, `harness/compat_check.py`, `harness/eligibility_chain.py`, `harness/target_endpoint.py` (R2/R3
  only until a batched change is agreed)

## Main lane (not touched by the RAI lane)
- `harness/absence.py`, `harness/harms.py`, `harness/known_missing.py`, `harness/pipeline.py`, `harness/admission.py`,
  `harness/page.py`, `harness/gate*.py`, `harness/index.py`, `harness/parity_relation.py`, `harness/trial_family.py`,
  `harness/result_changes.py`, `scripts/verify_bundle.py`, `docs/scripts/verify_bundle.py`, `scripts/verify_all.py`,
  and the §F audit contract.

If a lane needs a file on the other list it asks first, on the other lane's branch; no silent edits.
