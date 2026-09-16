# LANE CP Report

## 1. What Was Wrong

Mechanism:
- `docs/parity.json` carried hand status words (`PARITY`, `PARITY-effective`, `GAP`, `NEAR`) and `harness/census.py::_parity_row` attached them verbatim.
- `harness/page.py` rendered that hand status on the Reproduction tab, so stale labels could sit beside contradictory k values.
- `harness/scope.py` ignored topic `intervention_class_terms`, so probiotics rendered as "a single agent" even though the topic is heterogeneous strains/formulations.
- Statins had one object with two verdicts: comparator scope said "same question" while parity said the comparator was invalid because it pooled observational studies, not an RCT meta-analysis.
- `scripts/external_agreement.py` counted same-estimand close matches as "agreement" even when the trial set was identical, which is arithmetic replication, not independent corroboration.

Files carrying the mechanism:
- `docs/parity.json`
- `harness/parity_relation.py`
- `harness/census.py`
- `harness/page.py`
- `harness/pipeline.py`
- `harness/scope.py`
- `scripts/external_agreement.py`
- `scripts/parity_relation_sweep.py`

Static-vs-dynamic disclosure:

| Item | Static or dynamic | Disclosure |
|---|---|---|
| Relation vocabulary | Static | Fixed enum in `harness/parity_relation.py`: `IDENTICAL_SET`, `DOMINANT_SUBSET`, `SUBSET`, `SUPERSET`, `OVERLAPPING`, `DISTINCT`, `COMPARATOR_INVALID`, `NOT_ENUMERABLE`. |
| Relation assignment | Dynamic | Computed from parity k values, comparator overlap fields, scope validity, and named shared/only sets where exposed. |
| Dominant-subset patient share | Dynamic from commentary | Parsed only when the parity reason states a percent tied to patients/events; PCSK9 reports 87% from the existing reason text. |
| Sweep denominator | Dynamic | Recomputed from `docs/reviews/*/review.json`, not typed: 21 topics with parity rows + 11 without = 32. |
| Trial pools | Not changed | No pooled trials, estimates, endpoints, search, `harness/synth.py`, RoB, GRADE, or effect-measure code changed. |

## 2. Plant

Plant file: `tests/test_parity_relation.py`

Exact assertions:
- `test_PLANT_prefix_hand_parity_status_refused[pcsk9-mace-DOMINANT_SUBSET]`: loads `aa8ed28a:docs/reviews/pcsk9-mace/review.json` and `aa8ed28a:docs/parity.json`; asserts computed relation is `DOMINANT_SUBSET` and `hand_status_disagrees is True`.
- `test_PLANT_prefix_hand_parity_status_refused[ticagrelor-vs-clopidogrel-acs-SUPERSET]`: asserts computed relation is `SUPERSET` and the old hand `PARITY` status disagrees.
- `test_PLANT_prefix_invalid_comparator_scope_refused`: asserts pre-fix statins had `scope_valid is True`, computed relation is `COMPARATOR_INVALID`, and `scope_consistency_errors(...)` returns a refusal.
- `test_PLANT_identical_trial_set_is_replication`: asserts noac, finerenone, and sglt2-hfref compute `IDENTICAL_SET` and the label contains `arithmetic replication`.
- `test_PLANT_prefix_external_agreement_said_agrees_for_same_set`: asserts pre-fix noac external row was `same_estimand_agree` / `agree_within_12pct=True`, and the fixed classifier returns `same_estimand_replication` / `agree_within_12pct=False`.
- `test_synthetic_controls_cover_every_relation`: covers every vocabulary term with synthetic controls.

Pre-fix object findings (MEASURED from `git show aa8ed28a:...`):
- PCSK9 before: `status=PARITY-effective our_k=2 comp_k=2`; computed relation now detects `DOMINANT_SUBSET`, comparator k `12`.
- Ticagrelor before: `status=PARITY our_k=2 comp_k=1`; computed relation detects `SUPERSET`.
- Statins before: scope `valid=True` with note `same-question comparator`; computed relation detects `COMPARATOR_INVALID`.
- Noac before external agreement: `category=same_estimand_agree agree=True same_question=True`.

Post-fix test output:
- `python -m pytest tests/test_parity_relation.py tests/test_external_agreement_estimand.py -q`
- Summary: `23 passed in 7.58s`

## 3. Rebuilt Pages And Before/After

All 21 topics with a parity row were rebuilt with `python scripts/build_topic.py <slug> --now 2026-09-11`, then replayed with `python scripts/reproduce_review.py <slug>`. Each replay printed `1/1 reproduce (all reproducible)`.

Rebuilt page relation changes:

| Slug | Before status | After computed relation |
|---|---:|---:|
| finerenone-ckd-t2d-renal | `PARITY` | `IDENTICAL_SET` |
| glp1-ra-mace-t2d | `PARITY-effective` | `SUPERSET` |
| sglt2-hfref-hosp-cvdeath | `PARITY` | `IDENTICAL_SET` |
| balanced-crystalloids-vs-saline-mortality | `GAP-DESIGN-REFUSAL` | `OVERLAPPING` |
| ticagrelor-vs-clopidogrel-acs | `PARITY` | `SUPERSET` |
| colchicine-postop-af | `NEAR` | `OVERLAPPING` |
| spironolactone-hfref-mortality | `PARITY` | `SUPERSET` |
| noac-vs-warfarin-af-stroke | `PARITY` | `IDENTICAL_SET` |
| colchicine-recurrent-pericarditis | `GAP` | `OVERLAPPING` |
| pcsk9-mace | `PARITY-effective` | `DOMINANT_SUBSET` |
| iv-iron-hfref-hosp | `NEAR` | `OVERLAPPING` |
| omega3-cardiovascular-events | `GAP` | `OVERLAPPING` |
| sglt2-ckd-progression | `GAP` | `SUBSET` |
| tranexamic-acid-pph | `GAP` | `SUBSET` |
| corticosteroids-covid19-mortality | `GAP` | `OVERLAPPING` |
| statins-primary-prevention-elderly | `COMPARATOR-INVALID` | `COMPARATOR_INVALID` |
| denosumab-vertebral-fracture | `NOT-ENUMERABLE` | `NOT_ENUMERABLE` |
| probiotics-aad-prevention | `GAP` | `OVERLAPPING` |
| semaglutide-obesity-weight | `PARITY` | `IDENTICAL_SET` |
| esketamine-trd-madrs | `GAP` | `IDENTICAL_SET` |
| melatonin-primary-insomnia-sol | `GAP` | `OVERLAPPING` |

Requested before/after quotes:

| Slug | Before | After |
|---|---|---|
| pcsk9-mace | `status=PARITY-effective our_k=2 comp_k=2` | `relation=DOMINANT_SUBSET our_k=2 comp_k=12 label=INFERRED dominant-trial subset -- ours is contained in the comparator; carries 87% of comparator patients/events (source: parity reason text)` |
| ticagrelor-vs-clopidogrel-acs | `status=PARITY our_k=2 comp_k=1` | `relation=SUPERSET our_k=2 comp_k=1 label=INFERRED superset -- the comparator trial set is contained in ours` |
| statins-primary-prevention-elderly | scope before: `valid=True ... note=same-question comparator` | scope after: `valid=False ... note=comparator invalid -- not an RCT meta / not the same question`; parity after `COMPARATOR_INVALID` |
| probiotics-aad-prevention | scope before: `topic_class=False comp_class=False` | scope after: `topic_class=True comp_class=True`; parity after `OVERLAPPING` |
| noac-vs-warfarin-af-stroke | external before: `same_estimand_agree agree=True` | external after: `same_estimand_replication agree=False basis=arithmetic_replication relation=IDENTICAL_SET` |
| finerenone-ckd-t2d-renal | external before: `same_estimand_agree agree=True` | external after: `same_estimand_replication agree=False basis=arithmetic_replication relation=IDENTICAL_SET` |
| sglt2-hfref-hosp-cvdeath | external before: `cross_estimand_pending agree=False` | external after: `cross_estimand_pending agree=False basis=arithmetic_replication relation=IDENTICAL_SET` |

Corpus sweep:
- Command: `python scripts/parity_relation_sweep.py`
- Output: `parity relation disagreements: 0 of 32 topics; without parity row: 11`
- JSON: `docs/parity_relation_sweep.json`
- Topics without parity rows: `colchicine-secondary-cv-prevention`, `corticosteroids-cap-mortality`, `dapagliflozin-hfpef-hosp`, `doac-vte-recurrence`, `dpp4-mace-t2d`, `empagliflozin-hfpef-hosp`, `metformin-pcos-ovulation`, `sacubitril-valsartan-hfref`, `semaglutide-obesity-mace`, `sglt2-primary-prevention-hf`, `tocilizumab-covid19-mortality`.

External agreement:
- Command: `python scripts/external_agreement.py`
- Output: `same-ESTIMAND agreement (different evidence base only): 10/27`
- Output: `same-estimand arithmetic replication: 2`

## 4. Tests

Targeted:
- `python -m pytest tests/test_parity_relation.py tests/test_external_agreement_estimand.py -q`
- Summary: `23 passed in 7.58s`

Full:
- `python -m pytest tests -x -q`
- First run stopped after stale generated fix-state files: `1 failed, 185 passed in 405.49s (0:06:45)`.
- Ran the named generators: `python scripts/render_fix_ledger.py` and `python scripts/rewrite_fixstate_lines.py`.
- Rerun summary: `655 passed in 530.41s (0:08:50)`.

Whitespace:
- `git diff --check` passed; only warning was line-ending normalization for `docs/external_agreement.json`.

## 5. What I Did Not Do

- Did not commit.
- Did not run network searches.
- Did not touch pooling, `harness/synth.py`, `harness/rob_sensitivity.py`, `harness/grade.py`, `harness/estmeasure.py`, search code, trial inclusion/exclusion, or hand `reason` prose.
- Did not add/remove trials from any pool.
- Did not run `scripts/verify_all.py`.
- Did not use `git add`, `git commit`, `git stash`, `git checkout`, `git reset`, or `git clean`.

## 6. Files Changed Or Added

New source/test/script/report files:
- `harness/parity_relation.py`
- `scripts/parity_relation_sweep.py`
- `tests/test_parity_relation.py`
- `LANE-CP-REPORT.md`

Modified source/test/script files:
- `harness/census.py`
- `harness/index.py`
- `harness/page.py`
- `harness/pipeline.py`
- `harness/scope.py`
- `scripts/external_agreement.py`
- `scripts/reproduce_review.py`
- `tests/test_external_agreement_estimand.py`

Modified generated data/index/ledger files:
- `docs/parity.json`
- `docs/parity_relation_sweep.json`
- `docs/external_agreement.json`
- `docs/index.html`
- `docs/fix_ledger.json`
- `docs/evidence/hazard-consumers-2026-09-14/README.md`
- `docs/evidence/search-v2-measurement-2026-09-15/README.md`
- `registry/blind_map.json`

Modified blind pages:
- `docs/m/m586876fa/index.html`
- `docs/m/m612a48aa/index.html`
- `docs/m/mb53e1ed5/index.html`
- `docs/m/me0751432/index.html`

For each rebuilt topic below, these four files changed: `REPRODUCTION.json`, `index.html`, `manifest.json`, `review.json`.
- `docs/reviews/balanced-crystalloids-vs-saline-mortality/`
- `docs/reviews/colchicine-postop-af/`
- `docs/reviews/colchicine-recurrent-pericarditis/`
- `docs/reviews/corticosteroids-covid19-mortality/`
- `docs/reviews/denosumab-vertebral-fracture/`
- `docs/reviews/esketamine-trd-madrs/`
- `docs/reviews/finerenone-ckd-t2d-renal/`
- `docs/reviews/glp1-ra-mace-t2d/`
- `docs/reviews/iv-iron-hfref-hosp/`
- `docs/reviews/melatonin-primary-insomnia-sol/`
- `docs/reviews/noac-vs-warfarin-af-stroke/`
- `docs/reviews/omega3-cardiovascular-events/`
- `docs/reviews/pcsk9-mace/`
- `docs/reviews/probiotics-aad-prevention/`
- `docs/reviews/semaglutide-obesity-weight/`
- `docs/reviews/sglt2-ckd-progression/`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/`
- `docs/reviews/spironolactone-hfref-mortality/`
- `docs/reviews/statins-primary-prevention-elderly/`
- `docs/reviews/ticagrelor-vs-clopidogrel-acs/`
- `docs/reviews/tranexamic-acid-pph/`

Pre-existing untracked lane files left unmodified/uncommitted:
- `LANE_PROMPT.md`
- `lane.log`
- `lane.pid`
- `lane.winpid`
