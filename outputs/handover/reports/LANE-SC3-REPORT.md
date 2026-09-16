# LANE SC3 Report

## Summary

Implemented the lane as an additive canonical arm-object contract. The defect was that screening could see topic words in a title/abstract and mark a record `INCLUDE` even when the randomised arm object was a different contrast, a different dose, a different age group, or a population explicitly excluded by the protocol. That left false-positive screened-in records to show up as declared-absent downstream.

Core mechanism and files:
- `harness/arm_object.py`: derives `trial -> randomised arm -> drug -> dose -> background therapy -> population (age, entry condition) -> timepoint -> analysis set -> effect source`, preserving `NOT_DERIVABLE` instead of inventing fields.
- `harness/screen.py`: applies the arm-object contract at screening for topics that declare `arm_object`.
- `harness/pipeline.py`: carries relevant arm-object evidence into review objects.
- `harness/gate.py`: refuses a page with `TRIAL_FAILS_CONTRACT` if a pooled trial fails the arm-object contract.
- `scripts/arm_object_sweep.py`: corpus sweep to `docs/arm_object_sweep.json`.
- Topic configs added executable `arm_object` declarations for semaglutide obesity, balanced crystalloids, and SGLT2 CKD.

`harness/eligibility_chain.py` was absent in this clone, so there was no file to extend there.

## Plants

Plant tests are in `tests/test_arm_object.py`.

Pre-fix evidence is loaded from `ad5e7c66:docs/reviews/<slug>/review.json`; post-fix evidence is from current `screen.run(...)`. Exact before/after row quote from the verification helper:

```text
40629530 :: include INCLUDE => exclude X-CONTRAST
41778920 :: include INCLUDE => exclude X-DOSE
41296499 :: include INCLUDE => exclude X-AGE
41045908 :: include INCLUDE => exclude ELIGIBILITY_STATE_INCONSISTENT
40069849 :: include INCLUDE => exclude X-POPULATION
42575111 :: include INCLUDE => exclude X-POPULATION
NCT07189091 :: include INCLUDE => exclude X-CONTRAST
NCT06350123 :: include INCLUDE => exclude X-CONTRAST
NCT05884866 :: include INCLUDE => exclude X-CONTRAST
```

Specific assertions:
- PYY1875 / PMID 40629530: pre `decision == "include"`; post `decision == "exclude"`, `rule_id == "X-CONTRAST"`, reason contains `background=semaglutide 2.4 mg both arms`.
- CRUSADERS / NCT07189091: pre included; post `X-CONTRAST(strategy_bundle)`.
- HISTORI / PMID 41778920: pre included; post `X-DOSE`, reason contains `1.0 mg`.
- STEP TEENS / PMID 41296499: pre included; post `X-AGE`, reason contains `12 to <18`.
- HFpEF / PMID 41045908: pre included; post `ELIGIBILITY_STATE_INCONSISTENT`, reason contains `population_none:heart failure`.
- MIRO-CKD / NCT06350123: pre included; post `X-CONTRAST`, reason contains `background=dapagliflozin 10 mg both arms`.
- STEP7 / PMID 40069849 and STEP12 / PMID 42575111: pre included; post `X-POPULATION(mixed T2D)`.
- Positives still include: STEP1 33567185, STEP3 33625476, DAPA-HF 31535829, EMPEROR-Reduced 32865377.
- Synthetic CONFIDENCE passes through the arm object.
- Synthetic STEP8 phrase `active treatment groups double-blinded against matched placebo groups` yields a hidden eligible semaglutide-vs-matched-placebo contrast.
- Gate plant: a pooled trial failing the contract returns `TRIAL_FAILS_CONTRACT`.

Targeted plant run:

```text
python -m pytest tests/test_arm_object.py -q
11 passed in 18.32s
```

## Rebuilt Pages

All affected pages were rebuilt sequentially with `--now 2026-09-11` and replayed.

Semaglutide obesity:
- Old: screened 143, included 14, excluded `X1=84, X2=35, X3=10`; primary `k=2`, trials `33625476`, `33567185`.
- New: screened 143, included 8, excluded `X1=84, X2=35, X3=10, X-CONTRAST=1, X-DOSE=1, X-AGE=1, X-POPULATION=2, ELIGIBILITY_STATE_INCONSISTENT=1`; primary `k=2`, same trials.
- Declared-absent primary list removed 41045908, 40629530, 41778920, 41296499, 40069849, 42575111.

Balanced crystalloids:
- Old: screened 29, included 8, excluded `X1=7, X2=4, X3=10`; primary `k=2`, trials `35041780`, `34375394`.
- New: screened 29, included 7, excluded `X1=7, X2=4, X3=10, X-CONTRAST=1`; primary `k=2`, same trials.
- Declared-absent primary list removed `CRUSADERS`.

SGLT2 CKD:
- Old: screened 35, included 8, excluded `X1=9, X2=11, X3=7`; primary `k=3`, trials `32970396`, `30990260`, `36331190`.
- New: screened 35, included 6, excluded `X1=9, X2=11, X3=7, X-CONTRAST=2`; primary `k=3`, same trials.
- Declared-absent primary list removed `DapaBalci-Leap` and `MIRO-CKD`.

Rebuilt commands reported:

```text
semaglutide-obesity-weight: PRIMARY Percent change in body weight k=2; included trials ['33625476', '33567185']
balanced-crystalloids-vs-saline-mortality: PRIMARY Mortality k=2; included trials ['35041780', '34375394']
sglt2-ckd-progression: PRIMARY Trial-defined major kidney / cardiorenal composite k=3; included trials ['32970396', '30990260', '36331190']
```

Byte-changed rebuilt artefacts include each canonical `index.html`, `review.json`, `manifest.json`, `REPRODUCTION.json`, and the affected blind pages under `docs/m/`.

## Sweep

Final sweep:

```text
topics_measured: 32
included_refused_by_arm_object: n=0, N=296
hidden_eligible_contrast: n=1, N=3143
not_derivable_fields: n=28861, N=44963
wrote docs/arm_object_sweep.json
```

Initial diagnostic before rebuilding found 14 of 305 included records refused by the new contract, 1 hidden eligible contrast of 3143 screened records, and 28685 `NOT_DERIVABLE` fields of 44963 canonical field values.

## Verification

Replays:

```text
python scripts/reproduce_review.py semaglutide-obesity-weight
OK semaglutide-obesity-weight
1/1 reproduce (all reproducible)

python scripts/reproduce_review.py balanced-crystalloids-vs-saline-mortality
OK balanced-crystalloids-vs-saline-mortality
1/1 reproduce (all reproducible)

python scripts/reproduce_review.py sglt2-ckd-progression
OK sglt2-ckd-progression
1/1 reproduce (all reproducible)
```

Additional targeted checks:

```text
python -m pytest tests/test_gate.py::test_real_review_reproduces_and_passes_full_gate -q
1 passed in 28.36s

python -m pytest tests/test_gate_scorecard.py::test_real_registry_passes -q
1 passed in 4.54s

python -m pytest tests/test_stage_additions.py::test_absent_override_declared_and_flag_gated -q
1 passed in 5.26s
```

Full suite:

```text
python -m pytest tests -x -q
727 passed in 485.32s (0:08:05)
```

Other checks:

```text
python scripts/render_fix_ledger.py
rendered docs/fix_ledger.json

git diff --check
clean
```

## Ratchet Rewording For Integrator

No `docs/ratchet_acknowledgements.json` entry was written. Blocks reworded by the rebuild, for integrator review/signing if needed:
- `docs/reviews/semaglutide-obesity-weight/index.html`: Screening flow/counts, exclusion-rule breakdown, screening rows for six false includes, and Results declared-absent list changed because those records are now screening exclusions.
- `docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html`: Screening flow/counts, `X-CONTRAST` row for CRUSADERS, and Results declared-absent list changed because CRUSADERS is now a screening exclusion.
- `docs/reviews/sglt2-ckd-progression/index.html`: Screening flow/counts, `X-CONTRAST` rows for DapaBalci-Leap and MIRO-CKD, and Results declared-absent list changed because both are now screening exclusions.
- Corresponding blind pages changed under `docs/m/m5b3fd56c/`, `docs/m/m89f8021b/`, and `docs/m/me17c0a34/`.

## Static vs Dynamic Disclosure

| Item | Static or dynamic | Disclosure |
| --- | --- | --- |
| Topic arm-object declarations | Static config | Drug/comparator terms and semaglutide dose/population requirements are explicit in topic JSON; they are protocol gates, not result outputs. |
| Canonical arm object | Dynamic | Derived from committed cache records only; unknown fields stay `NOT_DERIVABLE`. |
| Screening refusals | Dynamic | Computed from each record's derived arm object plus topic config. |
| Sweep counts | Dynamic | Computed from committed review pages and caches by `scripts/arm_object_sweep.py`. |
| Synthetic CONFIDENCE/STEP8 plants | Static tests | Labelled synthetic and used only to prove parser behavior; not shipped as evidence. |
| Effect sizes, k, declared-absent lists | Dynamic | Produced by existing pipeline rebuilds and replayed; no hardcoded research outputs were added. |

## Not Done

- No commit, per instruction.
- No network access.
- Did not touch pooling logic, `harness/synth.py`, search code, or extractor code.
- Did not write ratchet acknowledgements; only listed changed blocks above.
- Did not update `F:\ProjectIndex\INDEX.md` or `F:\E156\rewrite-workbook.txt`; no project status/submission state changed.
- Did not create `harness/eligibility_chain.py` because it was absent in the clone.

## Files Changed Or Added

Added:
- `LANE-SC3-REPORT.md`
- `docs/arm_object_sweep.json`
- `harness/arm_object.py`
- `scripts/arm_object_sweep.py`
- `tests/test_arm_object.py`

Modified:
- `docs/fix_ledger.json`
- `docs/gate_scorecard.json`
- `docs/m/m5b3fd56c/index.html`
- `docs/m/m89f8021b/index.html`
- `docs/m/me17c0a34/index.html`
- `docs/reviews/balanced-crystalloids-vs-saline-mortality/REPRODUCTION.json`
- `docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html`
- `docs/reviews/balanced-crystalloids-vs-saline-mortality/manifest.json`
- `docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json`
- `docs/reviews/semaglutide-obesity-weight/REPRODUCTION.json`
- `docs/reviews/semaglutide-obesity-weight/index.html`
- `docs/reviews/semaglutide-obesity-weight/manifest.json`
- `docs/reviews/semaglutide-obesity-weight/review.json`
- `docs/reviews/sglt2-ckd-progression/REPRODUCTION.json`
- `docs/reviews/sglt2-ckd-progression/index.html`
- `docs/reviews/sglt2-ckd-progression/manifest.json`
- `docs/reviews/sglt2-ckd-progression/review.json`
- `harness/gate.py`
- `harness/pipeline.py`
- `harness/screen.py`
- `registry/blind_map.json`
- `registry/gate_scorecard.json`
- `tests/test_stage_additions.py`
- `topics/balanced-crystalloids-vs-saline-mortality.json`
- `topics/semaglutide-obesity-weight.json`
- `topics/sglt2-ckd-progression.json`

Untracked pre-existing lane files left untouched except reading `LANE_PROMPT.md`: `LANE_PROMPT.md`, `lane.log`, `lane.pid`, `lane.winpid`.
