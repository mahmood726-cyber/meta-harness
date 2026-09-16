# LANE FP — one false renderer predicate on 17 pages: "(fewer trials than the full pool — see coverage)" appended when the low-risk-only re-pool has the SAME k as the full pool

Report file: `LANE-FP-REPORT.md`.

## The failure (MEASURED on committed objects at aa8ed28a)

`review["rob_sensitivity"]["low_only_informative"]` is defined in `harness/rob_sensitivity.py::sensitivity` as `low_only.k < full.k and low_only.k >= 1`. Two renderers — `harness/page.py` (~line 1613, the Risk-of-bias sensitivity table) and `harness/limitations.py::_rob_sensitivity_block` (~line 530) — append the text "(fewer trials than the full pool — see coverage)" whenever `low_only_informative` is False. But `low_only_informative` is ALSO False when `low_only.k == full.k` (every pooled trial is low risk), so the predicate "fewer trials" is rendered when it is false. Pre-fix this fires on **17 of 31** pages that carry a `rob_sensitivity` object (MEASURED by the integrator; `low_only.k == full.k and not low_only_informative`): balanced-crystalloids-vs-saline-mortality, colchicine-postop-af, colchicine-recurrent-pericarditis, dapagliflozin-hfpef-hosp, denosumab-vertebral-fracture, dpp4-mace-t2d, empagliflozin-hfpef-hosp, finerenone-ckd-t2d-renal, melatonin-primary-insomnia-sol, noac-vs-warfarin-af-stroke, pcsk9-mace, probiotics-aad-prevention, sacubitril-valsartan-hfref, semaglutide-obesity-weight, sglt2-ckd-progression, sglt2-hfref-hosp-cvdeath, statins-primary-prevention-elderly. (The external audit named 12 of the 22 pooled pages; the other 5 are k=1 pages.) Confirm this count yourself from the committed objects and report it as `n of N`.

## What to build

1. In `rob_sensitivity.sensitivity`, replace the boolean with a typed `low_only_relation` ∈ {`identical_to_full` (same k, so the re-pool equals the full pool), `fewer_trials` (k smaller, ≥1), `empty` (k=0 / None), `not_assessable`}, keeping `low_only_informative` for compatibility but derived from it. Both renderers derive their sentence from the relation: identical → "(all pooled trials are low risk; the re-pool is the full pool)"; fewer → the existing sentence; empty → the existing NOT ESTIMABLE cell. One predicate, two consumers, same source.
2. Also check `harness/manuscript.py` (grep `low_only`, `rob_sensitivity`) for the same conflation and fix it from the same relation.
3. Rebuild all affected pages (`build_topic.py <slug> --now 2026-09-11` for each of the 17 + any manuscript-affected page), `reproduce_review.py` each; quote the before/after sentence for each page.

## Plant (must fire pre-fix)

`tests/test_rob_sensitivity_predicate.py`: parametrised over ALL 31 pages' committed pre-fix `review.json` (copy the 17 affected + 3 unaffected into `tests/fixtures/rob_predicate/`, or read `docs/reviews/*/review.json` at test time and assert the same counts): (a) a checker `predicate_is_true(sens, rendered_html)` returns False on the pre-fix rendered page for each of the 17 and True for pages where k differs (name them) — quote the count line `17 of 31`; (b) post-fix rebuilt objects → True on 31 of 31; (c) a synthetic object with low_only.k < full.k → "fewer trials" sentence is STILL rendered (the fix must not remove the true case). Also assert the two renderers (page.py and limitations.py) emit the same relation word for the same object.

Do not touch: pooling, `harness/synth.py`, which trials are pooled, `harness/grade.py`, `harness/estmeasure.py`, search code. Note another lane (CG) is rebuilding the rob2 join key (label vs PMID) — do not fix that here; if your rebuilt `low_only.k` changes because of it, that is not your change; report and move on.
