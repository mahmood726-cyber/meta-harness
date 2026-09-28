# Pre-existing verification blockers

Observed before any implementation edit and rechecked after the change.
No existing tests or unrelated docs were edited to hide these failures.

| Test in tests/test_screen_contrast_and_ledger.py | Missing artifact |
|---|---|
| test_required_prefixed_plants_transition_on_current_replay | docs/study_families.json |
| test_genuine_drug_vs_placebo_record_stays_include | docs/study_families.json |
| test_screening_delta_artifact_records_required_corpus_sweep | docs/screening_delta.json |

Baseline requested existing suite: 51 passed, 3 failed. These are absent-file
failures, not changed decisions or failed blinding assertions. Resolution needs
the missing upstream artifacts; creating substitutes is outside this task.
