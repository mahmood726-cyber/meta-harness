# Producer role anchoring -- for the main lane (item 36 follow-up), evid2, 2026-09-25

## 1. `arm_roles` in every witness packet -- ON THIS BRANCH (evid2/typed-arms), landing on main
`evidence/typed_arms/witness/arm_roles.py` builds the block your `ARM_ROLE_ANCHOR.patch` (sha256 ee531676...) reads:
`{"intervention": [...], "comparator": [...], "source": "topics/<slug>.json", "registry": [{nct, scope, state,
intervention_group, comparator_group}]}` -- terms from the topic config (the source pipeline.py passes on), registry
roles from `harness.ctgov_results._classify_arms` (imported, not copied) over every group-defining scope. Your patch's
semantics are integrated in `check_witness.py`: T6 (role vs protocol terms; `arm_roles` first; ROLE_UNANCHORED /
ROLE_UNMATCHED flagged, never a silent pass) and T5b (a registry-owned arm's group id must be the classifier's group for
its declared role in its witnesses' scope). Every packet is stamped (276). Result on every real reading: 0 mismatches,
0 unclassified scopes, no state change, v2 byte-identical. Tests in `tests/test_witness.py`.

## 2. Positional role stamping in `harness/count_observations.py` -- a PATCH for your tree
`count_observations.py` is not on any pushed branch, so evid2 cannot land it. `DECLARED_ROLE_ANCHOR.patch`
(sha256 92555002bc491337...) is against the F4B version evid2 reconstructed (file sha256 of the base as checked out:
3dc101c1a6ebc045...; `git apply --check` clean). Your note cites :180 and :379-404, so your current file is newer;
the change is small and local:
- **The defect:** `names(arm_terms, declared)` added the two sides of the row's declared `comparator_direction`
  ("A vs B") by POSITION (`zip(SIDES, pair)`), so the first name became an intervention term. A label written
  comparator-first put the drug's name among the comparator terms and `side_of` then stamped the reversed role.
- **The fix:** `classify_declared` places each declared name by the PROTOCOL (control vocabulary / comparator terms ->
  comparator; intervention terms -> intervention; the same principle as `_classify_arms`); a name it cannot place
  contributes nothing; `bind` refuses a label whose order is the protocol's reverse as `DECLARED_DIRECTION_REVERSED`
  instead of silently re-stamping it.
- **Tests:** your 27 pass unchanged; 3 added (reversed label refused; unplaceable names get no role from position;
  the protocol order still binds) -- the first two FAIL on the old code.
