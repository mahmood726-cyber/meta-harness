# DEV rule evaluation v silver labels (7 DEV trials with an open full text)

| rule | agrees | disagrees | fires, silver silent |
|---|---|---|---|
| outcome:all_cause_mortality_v1 | 3 | 0 | 0 |
| regex:allocation_concealment_v1 | 4 | 0 | 0 |
| regex:allocation_concealment_v3 | 1 | 0 | 0 |
| regex:assessors_blinded_relative_clause_v1 | 1 | 0 | 0 |
| regex:baseline_balanced_v1 | 2 | 0 | 0 |
| regex:baseline_qualified_or_demographic_balance_v1 | 2 | 0 | 0 |
| regex:complete_follow_up_v1 | 1 | 0 | 0 |
| regex:double_blind_v1 | 5 | 0 | 1 |
| regex:itt_stated_v2 | 1 | 0 | 2 |
| regex:itt_v1 | 2 | 0 | 2 |
| regex:sequence_generation_v1 | 4 | 0 | 0 |
| regex:sequence_generation_v2 | 1 | 0 | 0 |
| registry:allocation_randomized_v1 | 1 | 0 | 1 |
| registry:caregiver_masked_v1 | 2 | 0 | 0 |
| registry:masking_none_v1 | 2 | 0 | 0 |
| registry:outcomes_assessor_masked_v1 | 3 | 0 | 0 |
| registry:registered_outcome_identity_v1 | 0 | 0 | 2 |
| registry:subject_masked_v1 | 4 | 0 | 0 |

Recall gaps (silver answered from full text, no rule): 1.2: 1, 1.3: 3, 2.7: 2, 3.1: 4, 3.2: 1, 4.1: 6, 4.2: 6, 4.3: 2, 5.2: 3, 5.3: 1
