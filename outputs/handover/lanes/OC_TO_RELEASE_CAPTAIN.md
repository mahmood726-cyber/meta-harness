# Lane OC → release captain (pointer; docs only)

**Branch:** `oc/ordered-contrast` (pointer `oc/V1-READY-p10-p11`), tip `23642e0d`, CI `verify` green (run 36155157542). The full
handoff with merge facts, commits, plants and held items is `HANDOFF-OC-TO-MAIN.md` on that branch. Reproduce every piece in about
a minute: `sh evidence/ordered_contrast/prove_pieces.sh`.

| V1 piece | State |
|---|---|
| (1) Effect-scoped estimator witness + P10 value + `ESTIMATOR_VALUE_MISMATCH` incl. HR→RR (+ `ESTIMATOR_OWNER_MISMATCH`, P15) | ready, plant-proven |
| (2) P11 registered contrast/estimator + `COMPARATOR_DIRECTION_MISMATCH` + declared reciprocal (PERMITTED, owner's decision) | ready, plant-proven |
| (3) Pooling refused before any log: `pool_measure_guard`, now reachable only through `pool_guarded()` | ready, plant-proven |
| (4) Arm orientation (`scripts/arm_orientation.py`, F4 arm ids, two routes agree 8/8) | ready |
| Page wording "parser-confirmed contrast" → "in the randomised difference (eligibility, not direction)" | patch ready (sha256 `dfb2109d…`, applies to main be57137a); re-releases 32 pages; **not applied** |

**Your gap (check_pool_contract computes the log before the guard):** on the candidate, replace `pool(x)` inside
`check_pool_contract` with `got, mg = pool_guarded(x, rows_by_pmid, declared_scale)` and report `mg`.
`tests/test_pool_guarded.py::test_pool_is_reachable_only_through_the_guard` fails on any unguarded `pool()` call, whatever the
function is named; it fired on a planted `check_pool_contract` of exactly that shape.

**Merge:** clean with main. Against enforcement-gate it adds no conflicts beyond the served per-page files enforcement-gate already
conflicts on. Generated files (the GLP-1 `BUNDLE.json`, the served verifier mirror and the page that names its sha) are
regenerated, never hand-merged: `build_bundle.py glp1-ra-mace-t2d`, then `build_topic.py glp1-ra-mace-t2d --now 2026-09-11`,
then `build_bundle.py` again. F4 `role` is not consumed, so T5 can land in either order.

**Held for signature (V1 limitations):** OC-Q1 page wording; OC-Q2 producer HR+RR pooling (5 served pools, 4 primary); OC-Q3 the
publication gate and estmeasure authenticate the claimed label (0 of 111 served rows disagree today). Details and hashes:
`evidence/ordered_contrast/SIGNATURE_QUEUE.md` on the branch.
