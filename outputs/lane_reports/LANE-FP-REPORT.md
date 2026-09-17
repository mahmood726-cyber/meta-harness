# LANE FP Report

## 1. What was wrong

MEASURED: `31` committed review pages carried a `rob_sensitivity` object. MEASURED from the committed objects at `aa8ed28a`: `17 of 31` had `low_only.k == full.k`, `9 of 31` had `low_only.k < full.k`, and `5 of 31` had no low-risk-only pool.

Mechanism: `harness/rob_sensitivity.py::sensitivity` exposed only `low_only_informative`, defined as `low_only.k < full.k and low_only.k >= 1`. That made two non-informative states indistinguishable to renderers: `low_only.k == full.k` and empty low-risk-only strata. `harness/page.py` and `harness/limitations.py` therefore appended the "fewer trials than the full pool -- see coverage" sentence when the low-risk-only pool was identical to the full pool. `harness/manuscript.py` carried the same conflation in prose by always using the coverage-caveat wording when a low-risk-only estimate existed.

Fix: `rob_sensitivity.sensitivity` now writes `low_only_relation` with one of `identical_to_full`, `fewer_trials`, `empty`, or `not_assessable`. `low_only_informative` remains for compatibility and is now derived as `low_only_relation == "fewer_trials"`. Page, limitation, and manuscript text all route through the same helper functions in `harness/rob_sensitivity.py`.

Static-vs-dynamic disclosure:

| Item | Kind | Source |
|---|---|---|
| Relation enum names | Static code contract | `harness/rob_sensitivity.py` |
| Expected pre-fix slug sets in the plant test | Static test expectations | MEASURED once from `aa8ed28a` and locked in `tests/test_rob_sensitivity_predicate.py` |
| Relation counts and before/after snippets | Dynamic evidence | `git show aa8ed28a:docs/reviews/*` plus rebuilt working-tree `docs/reviews/*` |
| Page rebuild outputs | Dynamic evidence | `python scripts/build_topic.py <slug> --now 2026-09-11` |
| Reproduction checks | Dynamic evidence | `python scripts/reproduce_review.py <slug>` |

## 2. The plant

Test file: `tests/test_rob_sensitivity_predicate.py`.

Exact pre-fix assertion:

```python
count_line = f"{len(failures)} of {len(rows)}"
assert len(rows) == 31
assert count_line == "17 of 31"
assert failures == EXPECTED_IDENTICAL_SLUGS
assert fewer_true == EXPECTED_FEWER_SLUGS
```

The checker loads pre-fix objects and rendered HTML with read-only `git show aa8ed28a:...`. It refuses a rendered "fewer trials than the full pool" statement unless the object relation is actually `fewer_trials`.

MEASURED pre-fix plant output:

```text
pre-fix predicate failures: 17 of 31
.
1 passed in 16.81s
```

Exact post-fix assertion:

```python
count_line = f"{len(rows) - len(failures)} of {len(rows)}"
assert len(rows) == 31
assert count_line == "31 of 31"
assert failures == []
```

MEASURED post-fix targeted output:

```text
pre-fix predicate failures: 17 of 31
.post-fix predicate passes: 31 of 31
..
3 passed in 24.13s
```

Synthetic guard: `test_synthetic_fewer_trials_sentence_survives_and_renderers_agree` builds a synthetic `fewer_trials` object and asserts both `page.py` and `limitations.py` render `fewer trials than the full pool`. It also checks the `identical_to_full` sentence and requires the two renderer cells to match exactly.

## 3. Rebuilt page changes

MEASURED: rebuilt all `31 of 31` pages carrying `rob_sensitivity`, because the review object schema now stores `low_only_relation`. MEASURED relation distribution after rebuild: `17 identical_to_full`, `9 fewer_trials`, `5 empty`. MEASURED snippets below are normalized to plain text; HTML `&mdash;` is shown as `--`.

| Slug | Relation | full k | low-only k | Before | After |
|---|---:|---:|---:|---|---|
| `balanced-crystalloids-vs-saline-mortality` | `identical_to_full` | `2` | `2` | k=2, RR 0.9774 [0.6521, 1.465] (fewer trials than the full pool -- see coverage) | k=2, RR 0.9774 [0.6521, 1.465] (all pooled trials are low risk; the re-pool is the full pool) |
| `colchicine-postop-af` | `identical_to_full` | `4` | `4` | k=4, RR 0.6735 [0.376, 1.2067] (fewer trials than the full pool -- see coverage) | k=4, RR 0.6735 [0.376, 1.2067] (all pooled trials are low risk; the re-pool is the full pool) |
| `colchicine-recurrent-pericarditis` | `identical_to_full` | `2` | `2` | k=2, RR 0.4813 [0.064, 3.6169] (fewer trials than the full pool -- see coverage) | k=2, RR 0.4813 [0.064, 3.6169] (all pooled trials are low risk; the re-pool is the full pool) |
| `colchicine-secondary-cv-prevention` | `fewer_trials` | `3` | `2` | k=2, HR 0.7215 [0.2824, 1.8432] | k=2, HR 0.7215 [0.2824, 1.8432] (fewer trials than the full pool -- see coverage) |
| `corticosteroids-cap-mortality` | `fewer_trials` | `2` | `1` | k=1, RR 0.5253 [0.33, 0.8361] | k=1, RR 0.5253 [0.33, 0.8361] (fewer trials than the full pool -- see coverage) |
| `corticosteroids-covid19-mortality` | `empty` | `1` | `None` | An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage -- read the widened interval with that caveat, not as instability of the effect. | No pooled trial qualifies as low risk, so the low-only stratum is not estimable; an empty subgroup is not agreement with the full pool. |
| `dapagliflozin-hfpef-hosp` | `identical_to_full` | `1` | `1` | k=1, HR 0.82 [0.7304, 0.9205] (fewer trials than the full pool -- see coverage) | k=1, HR 0.82 [0.7304, 0.9205] (all pooled trials are low risk; the re-pool is the full pool) |
| `denosumab-vertebral-fracture` | `identical_to_full` | `1` | `1` | k=1, RR 0.32 [0.2548, 0.4018] (fewer trials than the full pool -- see coverage) | k=1, RR 0.32 [0.2548, 0.4018] (all pooled trials are low risk; the re-pool is the full pool) |
| `doac-vte-recurrence` | `fewer_trials` | `6` | `4` | k=4, HR 0.917 [0.6926, 1.2141] | k=4, HR 0.917 [0.6926, 1.2141] (fewer trials than the full pool -- see coverage) |
| `dpp4-mace-t2d` | `identical_to_full` | `3` | `3` | k=3, HR 1.0074 [0.8391, 1.2094] (fewer trials than the full pool -- see coverage) | k=3, HR 1.0074 [0.8391, 1.2094] (all pooled trials are low risk; the re-pool is the full pool) |
| `empagliflozin-hfpef-hosp` | `identical_to_full` | `1` | `1` | k=1, HR 0.79 [0.6917, 0.9022] (fewer trials than the full pool -- see coverage) | k=1, HR 0.79 [0.6917, 0.9022] (all pooled trials are low risk; the re-pool is the full pool) |
| `esketamine-trd-madrs` | `empty` | `4` | `None` | An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage -- read the widened interval with that caveat, not as instability of the effect. | No pooled trial qualifies as low risk, so the low-only stratum is not estimable; an empty subgroup is not agreement with the full pool. |
| `finerenone-ckd-t2d-renal` | `identical_to_full` | `2` | `2` | k=2, HR 0.8407 [0.4625, 1.5281] (fewer trials than the full pool -- see coverage) | k=2, HR 0.8407 [0.4625, 1.5281] (all pooled trials are low risk; the re-pool is the full pool) |
| `glp1-ra-mace-t2d` | `fewer_trials` | `8` | `6` | k=6, HR 0.8321 [0.7668, 0.9029] | k=6, HR 0.8321 [0.7668, 0.9029] (fewer trials than the full pool -- see coverage) |
| `melatonin-primary-insomnia-sol` | `identical_to_full` | `1` | `1` | k=1, MD -17.4 [-28.5214, -6.2786] (fewer trials than the full pool -- see coverage) | k=1, MD -17.4 [-28.5214, -6.2786] (all pooled trials are low risk; the re-pool is the full pool) |
| `metformin-pcos-ovulation` | `fewer_trials` | `3` | `2` | k=2, OR 4.3142 [0.0033, 5557.8501] | k=2, OR 4.3142 [0.0033, 5557.8501] (fewer trials than the full pool -- see coverage) |
| `noac-vs-warfarin-af-stroke` | `identical_to_full` | `4` | `4` | k=4, HR 0.8069 [0.6611, 0.985] (fewer trials than the full pool -- see coverage) | k=4, HR 0.8069 [0.6611, 0.985] (all pooled trials are low risk; the re-pool is the full pool) |
| `omega3-cardiovascular-events` | `fewer_trials` | `7` | `5` | k=5, RR 0.9775 [0.9018, 1.0595] | k=5, RR 0.9775 [0.9018, 1.0595] (fewer trials than the full pool -- see coverage) |
| `pcsk9-mace` | `identical_to_full` | `2` | `2` | k=2, HR 0.85 [0.5852, 1.2346] (fewer trials than the full pool -- see coverage) | k=2, HR 0.85 [0.5852, 1.2346] (all pooled trials are low risk; the re-pool is the full pool) |
| `probiotics-aad-prevention` | `identical_to_full` | `16` | `16` | k=16, RR 0.702 [0.5352, 0.921] (fewer trials than the full pool -- see coverage) | k=16, RR 0.702 [0.5352, 0.921] (all pooled trials are low risk; the re-pool is the full pool) |
| `sacubitril-valsartan-hfref` | `identical_to_full` | `1` | `1` | k=1, HR 0.8 [0.7328, 0.8733] (fewer trials than the full pool -- see coverage) | k=1, HR 0.8 [0.7328, 0.8733] (all pooled trials are low risk; the re-pool is the full pool) |
| `semaglutide-obesity-mace` | `empty` | `1` | `None` | An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage -- read the widened interval with that caveat, not as instability of the effect. | No pooled trial qualifies as low risk, so the low-only stratum is not estimable; an empty subgroup is not agreement with the full pool. |
| `semaglutide-obesity-weight` | `identical_to_full` | `2` | `2` | k=2, MD -11.8449 [-25.1318, 1.442] (fewer trials than the full pool -- see coverage) | k=2, MD -11.8449 [-25.1318, 1.442] (all pooled trials are low risk; the re-pool is the full pool) |
| `sglt2-ckd-progression` | `identical_to_full` | `3` | `3` | k=3, HR 0.6836 [0.5537, 0.844] (fewer trials than the full pool -- see coverage) | k=3, HR 0.6836 [0.5537, 0.844] (all pooled trials are low risk; the re-pool is the full pool) |
| `sglt2-hfref-hosp-cvdeath` | `identical_to_full` | `2` | `2` | k=2, RR 0.7755 [0.4457, 1.3493] (fewer trials than the full pool -- see coverage) | k=2, RR 0.7755 [0.4457, 1.3493] (all pooled trials are low risk; the re-pool is the full pool) |
| `sglt2-primary-prevention-hf` | `fewer_trials` | `4` | `3` | k=3, HR 0.7023 [0.5281, 0.934] | k=3, HR 0.7023 [0.5281, 0.934] (fewer trials than the full pool -- see coverage) |
| `spironolactone-hfref-mortality` | `fewer_trials` | `3` | `2` | k=2, RR/HR 0.7218 [0.3236, 1.6097] | k=2, RR/HR 0.7218 [0.3236, 1.6097] (fewer trials than the full pool -- see coverage) |
| `statins-primary-prevention-elderly` | `identical_to_full` | `2` | `2` | k=2, HR 0.6803 [0.2897, 1.5975] (fewer trials than the full pool -- see coverage) | k=2, HR 0.6803 [0.2897, 1.5975] (all pooled trials are low risk; the re-pool is the full pool) |
| `ticagrelor-vs-clopidogrel-acs` | `fewer_trials` | `2` | `1` | k=1, HR 0.84 [0.7685, 0.9182] | k=1, HR 0.84 [0.7685, 0.9182] (fewer trials than the full pool -- see coverage) |
| `tocilizumab-covid19-mortality` | `empty` | `1` | `None` | An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage -- read the widened interval with that caveat, not as instability of the effect. | No pooled trial qualifies as low risk, so the low-only stratum is not estimable; an empty subgroup is not agreement with the full pool. |
| `tranexamic-acid-pph` | `empty` | `1` | `None` | An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage -- read the widened interval with that caveat, not as instability of the effect. | No pooled trial qualifies as low risk, so the low-only stratum is not estimable; an empty subgroup is not agreement with the full pool. |

MEASURED: the table's primary numbers did not move within these snippets; the changed content is the relation sentence and the generated hashes/reproduction metadata.

## 4. Tests and reproduction

Commands run and outcomes:

```text
python -m py_compile harness\rob_sensitivity.py harness\page.py harness\limitations.py harness\manuscript.py tests\test_rob_sensitivity_predicate.py
PASS (exit 0)
```

```text
python -m pytest tests/test_rob_sensitivity_predicate.py::test_prefix_rendered_predicate_fires_on_identical_low_only_pages -q -s
pre-fix predicate failures: 17 of 31
.
1 passed in 16.81s
```

```text
python -m pytest tests/test_rob_sensitivity_predicate.py -q -s
pre-fix predicate failures: 17 of 31
.post-fix predicate passes: 31 of 31
..
3 passed in 24.13s
```

MEASURED: ran `python scripts/build_topic.py <slug> --now 2026-09-11` for all `31` slugs in the table; all exited `0`.

MEASURED: ran `python scripts/reproduce_review.py <slug>` for all `31` slugs in the table; every slug printed `OK <slug>` and `1/1 reproduce (all reproducible)`.

Initial full-suite rerun found stale generated fix-state artifacts:

```text
FAILED tests/test_fixstate.py::test_real_store_validates
1 failed, 184 passed in 410.02s (0:06:50)
```

I then ran the repo-specified refreshers:

```text
python scripts/rewrite_fixstate_lines.py
rewrote evidence README fix-state lines

python scripts/render_fix_ledger.py
rendered docs/fix_ledger.json
```

Final full-suite result:

```text
python -m pytest tests -x -q
642 passed in 538.82s (0:08:58)
```

Diff hygiene:

```text
git diff --check
PASS (exit 0)
```

## 5. What I did not do

I did not touch pooling, `harness/synth.py`, `harness/grade.py`, `harness/estmeasure.py`, search code, extractor code, or the RoB2 join-key lane. I did not add or remove trials from any pool. I did not run any search or network-dependent script. I did not run `scripts/verify_all.py`. I did not run `git add`, `git commit`, `git stash`, `git checkout`, `git reset`, or `git clean`.

## 6. Files changed or added

Source, test, and report files:

- `harness/rob_sensitivity.py`
- `harness/page.py`
- `harness/limitations.py`
- `harness/manuscript.py`
- `tests/test_rob_sensitivity_predicate.py`
- `LANE-FP-REPORT.md`

Generated fix-state artifacts:

- `docs/fix_ledger.json`
- `docs/evidence/design-key-2026-09-14/README.md`
- `docs/evidence/hazard-consumers-2026-09-14/README.md`

Generated neutral harness pages:

- `docs/m/m0594e053/index.html`
- `docs/m/m078be06c/index.html`
- `docs/m/m0c0e2bf1/index.html`
- `docs/m/m175bd0c3/index.html`
- `docs/m/m22bf81d5/index.html`
- `docs/m/m24cd09bc/index.html`
- `docs/m/m250220c2/index.html`
- `docs/m/m2da64325/index.html`
- `docs/m/m3c1155fb/index.html`
- `docs/m/m5384fd3c/index.html`
- `docs/m/m586876fa/index.html`
- `docs/m/m5b3fd56c/index.html`
- `docs/m/m5e5590d5/index.html`
- `docs/m/m612a48aa/index.html`
- `docs/m/m6dd4233b/index.html`
- `docs/m/m6e7e8ab7/index.html`
- `docs/m/m87167438/index.html`
- `docs/m/m89f8021b/index.html`
- `docs/m/m8db5253b/index.html`
- `docs/m/m979b0810/index.html`
- `docs/m/ma0b91971/index.html`
- `docs/m/maf69923c/index.html`
- `docs/m/mb53e1ed5/index.html`
- `docs/m/mb6ceb13c/index.html`
- `docs/m/mc16cd596/index.html`
- `docs/m/md68c6ad6/index.html`
- `docs/m/me0751432/index.html`
- `docs/m/me17c0a34/index.html`
- `docs/m/me5d639f4/index.html`
- `docs/m/me79cb3b0/index.html`
- `docs/m/mf6cd36c2/index.html`

Generated review artifacts, one set per listed slug:

- `docs/reviews/balanced-crystalloids-vs-saline-mortality/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/colchicine-postop-af/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/colchicine-recurrent-pericarditis/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/colchicine-secondary-cv-prevention/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/corticosteroids-cap-mortality/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/corticosteroids-covid19-mortality/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/dapagliflozin-hfpef-hosp/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/denosumab-vertebral-fracture/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/doac-vte-recurrence/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/dpp4-mace-t2d/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/empagliflozin-hfpef-hosp/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/esketamine-trd-madrs/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/finerenone-ckd-t2d-renal/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/glp1-ra-mace-t2d/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/melatonin-primary-insomnia-sol/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/metformin-pcos-ovulation/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/noac-vs-warfarin-af-stroke/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/omega3-cardiovascular-events/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/pcsk9-mace/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/probiotics-aad-prevention/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/sacubitril-valsartan-hfref/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/semaglutide-obesity-mace/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/semaglutide-obesity-weight/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/sglt2-ckd-progression/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/sglt2-primary-prevention-hf/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/spironolactone-hfref-mortality/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/statins-primary-prevention-elderly/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/ticagrelor-vs-clopidogrel-acs/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/tocilizumab-covid19-mortality/{REPRODUCTION.json,index.html,manifest.json,review.json}`
- `docs/reviews/tranexamic-acid-pph/{REPRODUCTION.json,index.html,manifest.json,review.json}`

Temporary ignored helper used for report extraction:

- `.tmp/extract_rob_report.py`
