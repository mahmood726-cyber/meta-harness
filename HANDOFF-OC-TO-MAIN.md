# STATUS FOR THE RELEASE CAPTAIN: P10/P11 ARE DONE, NOT "NOT STARTED"

Pieces (1) effect-scoped estimator witness + P10 value check + ESTIMATOR_VALUE_MISMATCH incl. HR->RR, (2) P11 registered
contrast/estimator + COMPARATOR_DIRECTION_MISMATCH + declared reciprocal (PERMITTED, the owner's decision) and (3) the pre-log
pooling refusal are on branch `oc/ordered-contrast` (pointer branch `oc/V1-READY-p10-p11`). It is merged with origin/main
e3a20ff1, and CI `verify` (full verify_all, complete tree) ran green on a557d240 (run 36123517783) and on 812840f2
(run 36126221747). Reproduce every piece in about a minute from the repo root:

    sh evidence/ordered_contrast/prove_pieces.sh

Output on 812840f2 (also in evidence/ordered_contrast/PROOF_on_812840f2.txt):

```
(1) effect-scoped estimator witness + P10 value + ESTIMATOR_VALUE_MISMATCH incl. HR->RR
canonical (witness = LEADER's result clause) verdict PASS LEADER ADMISSIBLE   codes []
estimator_owner_methods                      verdict FAIL LEADER INADMISSIBLE codes ['ESTIMATOR_OWNER_MISMATCH', 'POOL_MEASURE_UNIDENTIFIED']
estimator_claim_or                           verdict FAIL LEADER INADMISSIBLE codes ['ESTIMATOR_MISMATCH', 'POOL_MEASURE_UNIDENTIFIED']
estimator_label_rr (HR->RR, class matches)   verdict FAIL LEADER INADMISSIBLE codes ['BOUND_TO_UNREGISTERED_ESTIMAND', 'ESTIMATOR_MISMATCH', 'ESTIMATOR_VALUE_MISMATCH', 'POOL_MEASURE_MIXED', 'POOL_MEASURE_UNIDENTIFIED']
estimator_hr_abbrev (control)                verdict PASS LEADER ADMISSIBLE   codes []
estimator_linked_method (control)            verdict PASS LEADER ADMISSIBLE   codes []
(2) P11 registered contrast/estimator + COMPARATOR_DIRECTION_MISMATCH + declared reciprocal (PERMITTED)
contrast_reverse (no reciprocal)             verdict FAIL LEADER INADMISSIBLE codes ['COMPARATOR_DIRECTION_MISMATCH']
contrast_reverse_served                      verdict FAIL LEADER INADMISSIBLE codes ['BOUND_TO_UNREGISTERED_ESTIMAND', 'COMPARATOR_DIRECTION_MISMATCH']
contrast_reverse_declared (served policy)    verdict PASS LEADER ADMISSIBLE   codes []
contrast_reverse_declared_forbidden          verdict FAIL LEADER INADMISSIBLE codes ['BOUND_TO_UNREGISTERED_ESTIMAND', 'CONTRAST_NORMALISATION_NOT_PERMITTED', 'POOL_INPUT_DISAGREES_WITH_ROW']
contrast_reverse_declared_away (0.87->1.149) verdict FAIL LEADER INADMISSIBLE codes ['BOUND_TO_UNREGISTERED_ESTIMAND']
estimator_genuine_rr (RR not registered)     verdict FAIL LEADER INADMISSIBLE codes ['BOUND_TO_UNREGISTERED_ESTIMAND', 'POOL_MEASURE_MIXED']
(3) measure-agnostic pooling refused before any log
measure_unidentified                         verdict FAIL LEADER INADMISSIBLE codes ['BOUND_TO_UNREGISTERED_ESTIMAND', 'ESTIMATOR_VALUE_MISMATCH', 'POOL_MEASURE_UNIDENTIFIED']
pool_input_reciprocal                        verdict FAIL LEADER ADMISSIBLE   codes ['POOL_INPUT_DISAGREES_WITH_ROW']
estimator_genuine_rr_permitted (row ok, pool mixed) verdict FAIL LEADER ADMISSIBLE   codes ['POOL_MEASURE_MIXED']
restore
canonical again                              verdict PASS LEADER ADMISSIBLE   codes []
```

---

# Lane OC → main lane (release captain): what is ready for V1, what is held

Branch `oc/ordered-contrast`. Each piece below is on the pushed branch, tested and plant-proven, and names the commit that carries
it. The V1 integration freeze is Saturday 09:00; items in "Held" are disclosed limitations, not candidates.

## NEW (release-captain gap): a refused pool is never COMPUTED -- `pool_guarded` (commit 4cc42b86)

`pool_guarded(inputs, rows_by_pmid, declared_scale)` is the ONLY route from a verdict to `pool()`: `pool_measure_guard` runs first
and on refusal returns `(None, guard)` without calling `pool()`. **To apply on the candidate:** inside `check_pool_contract`
replace `pool(x)` with `got, mg = pool_guarded(x, rows_by_pmid, declared_scale)` and report `mg`.
`tests/test_pool_guarded.py` enforces it independent of names:
- an AST walk refuses any call to `pool()` outside `pool_guarded` / `_plant_expected_pool` (a limb's producer model). It fired on
  the pre-fix verifier (d587d9aa) and fires on a planted `check_pool_contract` that pools and then asks the guard, so it will
  fire on the candidate until the call is rerouted;
- a runtime sentinel replaces `pool()` and raises if reached; five refusing plants run through the real `run()` and report
  `refused_before_logs` without reaching it; the canonical pool is still computed and reproduced to 1e-9.
The `check_pool_contract` function itself is not in any pushed ref or any tree on this host, so this lane could not edit it in
place; the rule above is written to catch it by shape.

## Page wording (OC-Q1)

The patch (sha256 `dfb2109d...`) applies cleanly (`git apply --check`) to origin/main be57137a (2026-09-25 15:42). It re-releases
all 32 pages; it needs the full cache to rebuild them, which this host lacks.

## Merge facts (measured with `git merge-tree`, no checkout)

- `oc/ordered-contrast` + `origin/main`: **clean**.
- `oc/ordered-contrast` + `origin/enforcement-gate` (1fa77f2c): the conflicting file set is **identical** to the one
  `origin/main` + `origin/enforcement-gate` already has (197 files, all served per-page files that enforcement-gate re-releases). Lane OC
  adds **none**. `scripts/verify_bundle.py`, `scripts/build_bundle.py` and every test file merge cleanly; the region split in
  `OWNERSHIP-ordered-contrast.md` held.
- The only generated file both lanes touch is `docs/reviews/glp1-ra-mace-t2d/BUNDLE.json` (plus the served verifier mirror and the
  GLP-1 page that names its sha256). Resolve by regenerating, never by hand:
  `python scripts/build_bundle.py glp1-ra-mace-t2d`, then, if the verifier bytes changed,
  `python scripts/build_topic.py glp1-ra-mace-t2d --now 2026-09-11` followed by `build_bundle.py` again. The GLP-1 page must then
  pass `reproduce_review.reproduce` and `gate_page`; both passed on this branch.
- F4 schema: lane OC **reuses** F4 arm identities (`<NCT>:<AACT design_group id>`, from certified `families.json`) and **never
  consumes** F4 `role`. Orientation is derived independently from the clause and the arm ids, so T5 role anchoring
  (`ARM_ROLE_MISMATCH`) can land before or after this without interaction. Until T5 lands, F4 roles are "asserted, not proven",
  and lane OC does not rely on them.

## Ready, in the owner's priority order

**(1) Effect-scoped estimator witness + P10 value check + ESTIMATOR_VALUE_MISMATCH (incl. HR→RR)**
- `estimand_evidence` is effect-scoped for every field. The owner is EFFECT_CLAUSE, or LINKED_METHOD_SPAN (typed link: the
  sentence names the same result object); any other mention is listed and never a witness. An unowned departing value fails
  closed (UNRESOLVED).
- New codes: `ESTIMATOR_OWNER_MISMATCH`, `ESTIMAND_OWNER_MISMATCH`, `ESTIMATOR_VALUE_MISMATCH` (label vs the owning evidence; no
  class is consulted), `ESTIMATOR_MISMATCH`.
- New predicate `P15_estimator_source_bound`, in the verifier and in the producer's admission.
- Plants: `--corrupt 27295427 estimator_owner_methods | estimator_claim_or | estimator_label_rr` refuse;
  `estimator_hr_abbrev | estimator_linked_method` pass; restore passes. The served-tree plants pass the pre-fix verifier **on
  the pre-fix served state** and fail now (`tests/test_ordered_contrast.py::test_plant_passed_the_prefix_verifier_and_is_refused_now`).
- Commits: 32703b8a (fix), plus the rebuild commit that follows it.

**(2) P11 registered contrast/estimator + COMPARATOR_DIRECTION_MISMATCH + declared reciprocal normalisation (PERMITTED, owner's decision)**
- A recomputed ordered contrast `{measure, experimental_arm, reference_arm, numerator_side, estimate, CI, direction_witness,
  rate_witness}` with three ordering rules plus a numeric rate witness.
- P11 requires the registered orientation and `estimators_permitted`.
- `registered_estimand.contrast_normalisation` = PERMITTED_WHEN_DECLARED, with `decided_by` recorded and `registered_in_protocol: false`.
- Plants: `contrast_reverse | contrast_reverse_served | contrast_reverse_declared_away` refuse; `contrast_reverse_declared(_permitted)`
  pass; `_forbidden` refuses.
- Commits: 88f07c74, 332c43ae, 4ecd8f49, plus the policy commit.

**(3) Measure-agnostic pooling refusal (verifier)**
- `pool_measure_guard` refuses POOL_MEASURE_UNIDENTIFIED / _MIXED / _NOT_RATIO and POOL_INPUT_DISAGREES_WITH_ROW **before**
  `pool()` is called.
- Plants: `measure_unidentified`, `pool_input_reciprocal`, `estimator_label_rr` (mixed).
- Commit: 88f07c74 (guard); 32703b8a (P15 keys the guard).

**(4) armcontrast orientation**
- `scripts/arm_orientation.py` (not `harness/`: `armcontrast.py` is certificate-pinned, and any new `harness/*.py` changes every
  certificate's scope).
- Two independent routes give the same arm ids on all 8 pooled GLP-1 trials.
- Commit: 332c43ae.

## Held: known limitations for V1 (each hash-bound in `evidence/ordered_contrast/SIGNATURE_QUEUE.md`)

- **OC-Q1, page wording** "parser-confirmed contrast" → "in the randomised difference (eligibility, not direction)". Patch sha256
  `dfb2109d…`. It re-releases all 32 pages (`page.py` / `armcontrast.py` are pinned) and must follow enforcement-gate, whose
  `page.py` hunk sits beside `_AC_LABEL`. **V1 limitation:** the served label claims more than eligibility; the ordered contrast
  in `BUNDLE.json` is the direction record.
- **OC-Q2, producer pooling guard** (`harness/synth.py` / `pipeline.py`, pinned). Census of the served surface: 51 pooled
  outcomes, 0 pool an unidentified measure, **5 pool HR with RR** (4 primary). Refusing the mix moves 5 served results, so it
  is a methods decision. **V1 limitation:** the producer still pools HR with RR under 'compatible_labels'; the bundle verifier
  refuses such a pool.
- **OC-Q3, the publication gate and estmeasure see only the CLAIMED label** (`harness/gate.py`, `estmeasure.py`, pinned). The
  real gate, run differentially on a page relabelled RR, raised only integrity/staleness reasons, none about the estimator.
  Census of 111 served pooled trial rows: 41 bind MATCH, **0 disagree**, 35 have no located clause, 28 are counts-only, 6 are
  continuous, 1 is unstated. A gate check that refuses on disagreement would falsely refuse nothing today; one that *requires*
  binding would refuse 36 rows. **V1 limitation:** estimator identity is source-bound in the bundle verifier and the bundle
  producer (P15), not yet in the publication gate.

## CI

`verify` run 36123517783 on `a557d240` (branch tip at handoff, merged with origin/main e3a20ff1): **success**. That is the full `scripts/verify_all.py` standard in the complete tree (unit tests, offline reproduction of every live page, publication gate on every page, index currency, fix-state). Local lane suites after the merge: 241 passed, 6 deselected (they copy the whole tree; CI ran them).
