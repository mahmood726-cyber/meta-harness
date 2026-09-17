# LANE EM Report

## 1. What was wrong

At commit `aa8ed28a`, the esketamine primary outcome had [MEASURED] pooled `k=4`, but three consumers were reading three different membership states:

- Integrity read only PubMed-checkable pooled rows, so it reported [MEASURED] `n_pooled=2` while the outcome pooled [MEASURED] `4` rows.
- RoB sensitivity joined `rob2.trials` through display labels for the registry rows, so [MEASURED] `NCT02422186` and [MEASURED] `NCT02417064` were rated and pooled but invisible to `levels`.
- Comparator parity rendered hand-written stale prose saying TRANSFORM-1 was a gap/refused trial while [MEASURED] `NCT02417064` was pooled.

Mechanism fixed:

- `harness/membership.py` now builds the per-outcome membership contract keyed by `trial["id"]`, with pooled/declared/refused/screened buckets and a dynamic `input_set_version`.
- `harness/pipeline.py` attaches `outcome["membership"]` and wraps integrity through that membership so registry-only rows count as pooled but PubMed retraction is explicitly not checkable.
- `harness/rob_sensitivity.py` and `harness/compat.py` resolve RoB by trial key/canonical key instead of display label.
- `harness/census.py`, `scripts/reproduce_review.py`, `harness/page.py`, and `harness/gate.py` annotate stale parity rows as `STALE_VS_MEMBERSHIP`, suppress stale prose, and avoid treating that unrenderable hand row as a parity gate failure.
- `scripts/membership_consistency_sweep.py` writes the 32-topic membership-consumer sweep to `docs/membership_consistency_sweep.json`.

Static-vs-dynamic hardcode disclosure:

| Item | Static or dynamic | Disclosure |
| --- | --- | --- |
| Outcome `membership` buckets | Dynamic | Built from the review outcome rows and included screening records at build time. |
| `input_set_version` | Dynamic | SHA-256 over the outcome name and membership seed. |
| Registry-only integrity source text | Static label | Static explanatory label only: `ctgov_results_only - retraction not checkable via PubMed`; not a research result. |
| Stale parity block text | Static wrapper, dynamic trigger | Wrapper text is fixed; it renders only when membership conflict detection finds a stale hand parity row. |
| Pre-fix plant object | Static historical object | Loaded read-only with `git show aa8ed28a:...`; no fixture numbers invented. |
| Pooled trials/effects | Dynamic existing data | Not changed by this lane. |

## 2. Plant

Test file: `tests/test_membership_consistency.py`.

Exact assertions planted:

```python
assert [v["code"] for v in violations] == [
    "INTEGRITY_COUNT_MISMATCH",
    "ROB_JOIN_MISS",
    "PARITY_TEXT_STALE",
]
assert violations[0]["detail"] == "2 vs 4"
assert violations[1]["detail"] == "2 rated-and-pooled trials invisible to levels"
assert "TRANSFORM-1" in violations[2]["conflicts"][0]["sentence"]
```

Pre-fix output on the committed object [MEASURED]:

```json
[
  {
    "code": "INTEGRITY_COUNT_MISMATCH",
    "detail": "2 vs 4",
    "integrity_n_pooled": 2,
    "membership_pooled": 4
  },
  {
    "code": "ROB_JOIN_MISS",
    "detail": "2 rated-and-pooled trials invisible to levels",
    "trial_keys": [
      "NCT02422186",
      "NCT02417064"
    ]
  },
  {
    "code": "PARITY_TEXT_STALE",
    "detail": "names a pooled trial as refused/not pooled",
    "conflicts": [
      {
        "trial_key": "NCT02417064",
        "label": "TRANSFORM-1",
        "sentence": "The 2 gap trials (TRANSFORM-1 and the phase-2 dose-finding) are 3-arm FIXED-DOSE (56/84 mg) designs: our multi-arm continuous guard refuses per-arm extraction because we pool the approved FLEXIBLE-dose estimand, not a single fixed-dose arm."
      }
    ]
  }
]
```

Post-fix output [MEASURED]:

```text
violations= []
```

Post-fix esketamine membership [MEASURED]: pooled `PMID 37025256`, `PMID 31109201`, `NCT02422186`, `NCT02417064`; integrity `n_pooled=4`, `n_pubmed_checked=2`, `n_not_checkable=2`; RoB sensitivity `n_rob_rated=4`; parity `membership_status=STALE_VS_MEMBERSHIP`.

Synthetic control assertion: `assert membership.consistency_violations(review) == []`.

## 3. Page changes

TRANSFORM-1 arm combination check [MEASURED]: `cache/esketamine-trd-madrs/verified_arms.json` says the row uses CT.gov MADRS Day-28 MMRM arm values: [MEASURED] 56 mg `-19.0` SD `13.86` n `111`, [MEASURED] 84 mg `-18.8` SD `14.12` n `98`, placebo `-14.8` SD `15.07` n `108`. The two intranasal esketamine arms are combined against shared placebo: combined mean `-18.91`, SD `13.95`, n `209`, using the Cochrane RevMan subgroup-combination formula. The rendered row source already discloses this combination, so no separate `arm_combination` field was added.

Sweep output [MEASURED]: `0 topics disagreeing of 32`.

All [MEASURED] 32 review pages rebuilt and byte-changed because `membership` is now part of each canonical review object and integrity output now records PubMed coverage. The integrity sentence changed from the old template `Trial integrity: none of the {n} trials pooled across all outcomes on this page is retracted...` to the new template `Trial integrity: {n} trials pooled; {checked} checked via PubMed, {not_checkable} not checkable (registry-only rows)...`.

| Page | Primary membership | Integrity before -> after | RoB before -> after | Parity render |
| --- | --- | --- | --- | --- |
| `balanced-crystalloids-vs-saline-mortality` | [MEASURED] absent -> `2` | [MEASURED] `2` -> `2`; PubMed checked absent -> `2`; not checkable absent -> `0` | [MEASURED] `2` -> `2` | unchanged |
| `colchicine-postop-af` | [MEASURED] absent -> `4` | [MEASURED] `4` -> `4`; PubMed checked absent -> `4`; not checkable absent -> `0` | [MEASURED] `4` -> `4` | `STALE_VS_MEMBERSHIP` |
| `colchicine-recurrent-pericarditis` | [MEASURED] absent -> `2` | [MEASURED] `2` -> `2`; PubMed checked absent -> `2`; not checkable absent -> `0` | [MEASURED] `2` -> `2` | `STALE_VS_MEMBERSHIP` |
| `colchicine-secondary-cv-prevention` | [MEASURED] absent -> `3` | [MEASURED] `4` -> `4`; PubMed checked absent -> `4`; not checkable absent -> `0` | [MEASURED] `2` -> `3` | unchanged |
| `corticosteroids-cap-mortality` | [MEASURED] absent -> `2` | [MEASURED] `3` -> `3`; PubMed checked absent -> `3`; not checkable absent -> `0` | [MEASURED] `2` -> `2` | unchanged |
| `corticosteroids-covid19-mortality` | [MEASURED] absent -> `1` | [MEASURED] `1` -> `1`; PubMed checked absent -> `1`; not checkable absent -> `0` | [MEASURED] `1` -> `1` | unchanged |
| `dapagliflozin-hfpef-hosp` | [MEASURED] absent -> `1` | [MEASURED] `1` -> `1`; PubMed checked absent -> `1`; not checkable absent -> `0` | [MEASURED] `1` -> `1` | unchanged |
| `denosumab-vertebral-fracture` | [MEASURED] absent -> `1` | [MEASURED] `1` -> `1`; PubMed checked absent -> `1`; not checkable absent -> `0` | [MEASURED] `1` -> `1` | unchanged |
| `doac-vte-recurrence` | [MEASURED] absent -> `6` | [MEASURED] `6` -> `6`; PubMed checked absent -> `6`; not checkable absent -> `0` | [MEASURED] `6` -> `6` | unchanged |
| `dpp4-mace-t2d` | [MEASURED] absent -> `3` | [MEASURED] `3` -> `3`; PubMed checked absent -> `3`; not checkable absent -> `0` | [MEASURED] `3` -> `3` | unchanged |
| `empagliflozin-hfpef-hosp` | [MEASURED] absent -> `1` | [MEASURED] `1` -> `1`; PubMed checked absent -> `1`; not checkable absent -> `0` | [MEASURED] `1` -> `1` | unchanged |
| `esketamine-trd-madrs` | [MEASURED] absent -> `4` | [MEASURED] `2` -> `4`; PubMed checked absent -> `2`; not checkable absent -> `2` | [MEASURED] `2` -> `4` | `STALE_VS_MEMBERSHIP` |
| `finerenone-ckd-t2d-renal` | [MEASURED] absent -> `2` | [MEASURED] `2` -> `2`; PubMed checked absent -> `2`; not checkable absent -> `0` | [MEASURED] `2` -> `2` | unchanged |
| `glp1-ra-mace-t2d` | [MEASURED] absent -> `8` | [MEASURED] `8` -> `8`; PubMed checked absent -> `8`; not checkable absent -> `0` | [MEASURED] `7` -> `8` | `STALE_VS_MEMBERSHIP` |
| `iv-iron-hfref-hosp` | [MEASURED] absent -> `2` | [MEASURED] `2` -> `2`; PubMed checked absent -> `2`; not checkable absent -> `0` | [MEASURED] absent -> absent | unchanged |
| `melatonin-primary-insomnia-sol` | [MEASURED] absent -> `1` | [MEASURED] `1` -> `1`; PubMed checked absent -> `1`; not checkable absent -> `0` | [MEASURED] `1` -> `1` | unchanged |
| `metformin-pcos-ovulation` | [MEASURED] absent -> `3` | [MEASURED] `3` -> `3`; PubMed checked absent -> `3`; not checkable absent -> `0` | [MEASURED] `3` -> `3` | unchanged |
| `noac-vs-warfarin-af-stroke` | [MEASURED] absent -> `4` | [MEASURED] `4` -> `4`; PubMed checked absent -> `4`; not checkable absent -> `0` | [MEASURED] `4` -> `4` | unchanged |
| `omega3-cardiovascular-events` | [MEASURED] absent -> `7` | [MEASURED] `7` -> `7`; PubMed checked absent -> `7`; not checkable absent -> `0` | [MEASURED] `7` -> `7` | unchanged |
| `pcsk9-mace` | [MEASURED] absent -> `2` | [MEASURED] `2` -> `2`; PubMed checked absent -> `2`; not checkable absent -> `0` | [MEASURED] `2` -> `2` | unchanged |
| `probiotics-aad-prevention` | [MEASURED] absent -> `16` | [MEASURED] `16` -> `16`; PubMed checked absent -> `16`; not checkable absent -> `0` | [MEASURED] `16` -> `16` | unchanged |
| `sacubitril-valsartan-hfref` | [MEASURED] absent -> `1` | [MEASURED] `1` -> `1`; PubMed checked absent -> `1`; not checkable absent -> `0` | [MEASURED] `1` -> `1` | unchanged |
| `semaglutide-obesity-mace` | [MEASURED] absent -> `1` | [MEASURED] `1` -> `1`; PubMed checked absent -> `1`; not checkable absent -> `0` | [MEASURED] `1` -> `1` | unchanged |
| `semaglutide-obesity-weight` | [MEASURED] absent -> `2` | [MEASURED] `2` -> `2`; PubMed checked absent -> `2`; not checkable absent -> `0` | [MEASURED] `2` -> `2` | unchanged |
| `sglt2-ckd-progression` | [MEASURED] absent -> `3` | [MEASURED] `3` -> `3`; PubMed checked absent -> `3`; not checkable absent -> `0` | [MEASURED] `3` -> `3` | unchanged |
| `sglt2-hfref-hosp-cvdeath` | [MEASURED] absent -> `2` | [MEASURED] `2` -> `2`; PubMed checked absent -> `2`; not checkable absent -> `0` | [MEASURED] `2` -> `2` | unchanged |
| `sglt2-primary-prevention-hf` | [MEASURED] absent -> `4` | [MEASURED] `4` -> `4`; PubMed checked absent -> `4`; not checkable absent -> `0` | [MEASURED] `4` -> `4` | unchanged |
| `spironolactone-hfref-mortality` | [MEASURED] absent -> `3` | [MEASURED] `3` -> `3`; PubMed checked absent -> `3`; not checkable absent -> `0` | [MEASURED] `2` -> `3` | unchanged |
| `statins-primary-prevention-elderly` | [MEASURED] absent -> `2` | [MEASURED] `2` -> `2`; PubMed checked absent -> `2`; not checkable absent -> `0` | [MEASURED] `2` -> `2` | unchanged |
| `ticagrelor-vs-clopidogrel-acs` | [MEASURED] absent -> `2` | [MEASURED] `2` -> `2`; PubMed checked absent -> `2`; not checkable absent -> `0` | [MEASURED] `1` -> `2` | unchanged |
| `tocilizumab-covid19-mortality` | [MEASURED] absent -> `1` | [MEASURED] `3` -> `3`; PubMed checked absent -> `3`; not checkable absent -> `0` | [MEASURED] `1` -> `1` | unchanged |
| `tranexamic-acid-pph` | [MEASURED] absent -> `1` | [MEASURED] `1` -> `1`; PubMed checked absent -> `1`; not checkable absent -> `0` | [MEASURED] `1` -> `1` | unchanged |

Esketamine exact sentence changes:

- Integrity before [MEASURED]: `Trial integrity: none of the 2 trials pooled across all outcomes on this page is retracted (checked 2026-09-13T08:44:17Z via PubMed efetch (PublicationType + CommentsCorrections) + AACT dates).`
- Integrity after [MEASURED]: `Trial integrity: 4 trials pooled; 2 checked via PubMed, 2 not checkable (registry-only rows). None of the PubMed-checkable pooled trials is retracted (checked 2026-09-13T08:44:17Z via PubMed efetch (PublicationType + CommentsCorrections)).`
- RoB before [MEASURED]: `2 of 4 pooled trials have a risk-of-bias rating`.
- RoB after [MEASURED]: `4 of 4 pooled trials have a risk-of-bias rating`.
- Parity stale sentence suppressed [MEASURED]: `The 2 gap trials (TRANSFORM-1 and the phase-2 dose-finding) are 3-arm FIXED-DOSE (56/84 mg) designs: our multi-arm continuous guard refuses per-arm extraction because we pool the approved FLEXIBLE-dose estimand, not a single fixed-dose arm.`
- Parity fixed block after [MEASURED]: `STALE_VS_MEMBERSHIP. The stored comparator-parity row is not rendered because it contradicts the current outcome membership object: TRANSFORM-1 (NCT02417064) is pooled in this review but the stored parity text describes it as a gap/refused/not-pooled trial. The stale prose is suppressed until the hand parity object is rewritten from the current membership.`

Other stale parity rows suppressed [MEASURED]: `colchicine-postop-af`, `colchicine-recurrent-pericarditis`, `glp1-ra-mace-t2d`.

## 4. Tests

- [MEASURED] `python scripts/membership_consistency_sweep.py` -> `0 topics disagreeing of 32`
- [MEASURED] `python scripts/reproduce_review.py` -> `32/32 reproduce (all reproducible)`
- [MEASURED] `python -m pytest tests/test_membership_consistency.py -q` -> `3 passed in 1.10s`
- [MEASURED] `python -m pytest tests/test_fixstate.py::test_real_store_validates -q` -> `1 passed in 61.08s (0:01:01)`
- [MEASURED] `python -m pytest tests -x -q` -> `642 passed in 180.71s (0:03:00)`

## 5. What I did not do

- Did not commit, stage, stash, checkout, reset, clean, or touch `.git/`, per lane rule.
- Did not change pooling arithmetic, `harness/synth.py`, `harness/grade.py`, `harness/estmeasure.py`, search code, or trial inclusion.
- Did not rewrite the hand parity prose in `docs/parity.json`; stale rows are made unrenderable instead.
- Did not run networked searches or `scripts/verify_all.py`; the lane forbids both.
- Did not add a structured `arm_combination` field because the current rendered row source already discloses the TRANSFORM-1 arm combination from committed cache.

## 6. Files changed or added

Source/test/report files changed or added:

- `LANE-EM-REPORT.md`
- `docs/membership_consistency_sweep.json`
- `harness/census.py`
- `harness/compat.py`
- `harness/gate.py`
- `harness/membership.py`
- `harness/page.py`
- `harness/pipeline.py`
- `harness/rob_sensitivity.py`
- `scripts/membership_consistency_sweep.py`
- `scripts/reproduce_review.py`
- `tests/test_membership_consistency.py`

Generated evidence/fix-state files changed:

- `docs/evidence/design-key-2026-09-14/README.md`
- `docs/evidence/hazard-consumers-2026-09-14/README.md`
- `docs/evidence/search-v2-measurement-2026-09-15/README.md`
- `docs/fix_ledger.json`

Generated blind-page files changed:

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
- `docs/m/mdd4bf0ae/index.html`
- `docs/m/me0751432/index.html`
- `docs/m/me17c0a34/index.html`
- `docs/m/me5d639f4/index.html`
- `docs/m/me79cb3b0/index.html`
- `docs/m/mf6cd36c2/index.html`

Generated review files changed:

- `docs/reviews/balanced-crystalloids-vs-saline-mortality/REPRODUCTION.json`
- `docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html`
- `docs/reviews/balanced-crystalloids-vs-saline-mortality/manifest.json`
- `docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json`
- `docs/reviews/colchicine-postop-af/REPRODUCTION.json`
- `docs/reviews/colchicine-postop-af/index.html`
- `docs/reviews/colchicine-postop-af/manifest.json`
- `docs/reviews/colchicine-postop-af/review.json`
- `docs/reviews/colchicine-recurrent-pericarditis/REPRODUCTION.json`
- `docs/reviews/colchicine-recurrent-pericarditis/index.html`
- `docs/reviews/colchicine-recurrent-pericarditis/manifest.json`
- `docs/reviews/colchicine-recurrent-pericarditis/review.json`
- `docs/reviews/colchicine-secondary-cv-prevention/REPRODUCTION.json`
- `docs/reviews/colchicine-secondary-cv-prevention/index.html`
- `docs/reviews/colchicine-secondary-cv-prevention/manifest.json`
- `docs/reviews/colchicine-secondary-cv-prevention/review.json`
- `docs/reviews/corticosteroids-cap-mortality/REPRODUCTION.json`
- `docs/reviews/corticosteroids-cap-mortality/index.html`
- `docs/reviews/corticosteroids-cap-mortality/manifest.json`
- `docs/reviews/corticosteroids-cap-mortality/review.json`
- `docs/reviews/corticosteroids-covid19-mortality/REPRODUCTION.json`
- `docs/reviews/corticosteroids-covid19-mortality/index.html`
- `docs/reviews/corticosteroids-covid19-mortality/manifest.json`
- `docs/reviews/corticosteroids-covid19-mortality/review.json`
- `docs/reviews/dapagliflozin-hfpef-hosp/REPRODUCTION.json`
- `docs/reviews/dapagliflozin-hfpef-hosp/index.html`
- `docs/reviews/dapagliflozin-hfpef-hosp/manifest.json`
- `docs/reviews/dapagliflozin-hfpef-hosp/review.json`
- `docs/reviews/denosumab-vertebral-fracture/REPRODUCTION.json`
- `docs/reviews/denosumab-vertebral-fracture/index.html`
- `docs/reviews/denosumab-vertebral-fracture/manifest.json`
- `docs/reviews/denosumab-vertebral-fracture/review.json`
- `docs/reviews/doac-vte-recurrence/REPRODUCTION.json`
- `docs/reviews/doac-vte-recurrence/index.html`
- `docs/reviews/doac-vte-recurrence/manifest.json`
- `docs/reviews/doac-vte-recurrence/review.json`
- `docs/reviews/dpp4-mace-t2d/REPRODUCTION.json`
- `docs/reviews/dpp4-mace-t2d/index.html`
- `docs/reviews/dpp4-mace-t2d/manifest.json`
- `docs/reviews/dpp4-mace-t2d/review.json`
- `docs/reviews/empagliflozin-hfpef-hosp/REPRODUCTION.json`
- `docs/reviews/empagliflozin-hfpef-hosp/index.html`
- `docs/reviews/empagliflozin-hfpef-hosp/manifest.json`
- `docs/reviews/empagliflozin-hfpef-hosp/review.json`
- `docs/reviews/esketamine-trd-madrs/REPRODUCTION.json`
- `docs/reviews/esketamine-trd-madrs/index.html`
- `docs/reviews/esketamine-trd-madrs/manifest.json`
- `docs/reviews/esketamine-trd-madrs/review.json`
- `docs/reviews/finerenone-ckd-t2d-renal/REPRODUCTION.json`
- `docs/reviews/finerenone-ckd-t2d-renal/index.html`
- `docs/reviews/finerenone-ckd-t2d-renal/manifest.json`
- `docs/reviews/finerenone-ckd-t2d-renal/review.json`
- `docs/reviews/glp1-ra-mace-t2d/REPRODUCTION.json`
- `docs/reviews/glp1-ra-mace-t2d/index.html`
- `docs/reviews/glp1-ra-mace-t2d/manifest.json`
- `docs/reviews/glp1-ra-mace-t2d/review.json`
- `docs/reviews/iv-iron-hfref-hosp/REPRODUCTION.json`
- `docs/reviews/iv-iron-hfref-hosp/index.html`
- `docs/reviews/iv-iron-hfref-hosp/manifest.json`
- `docs/reviews/iv-iron-hfref-hosp/review.json`
- `docs/reviews/melatonin-primary-insomnia-sol/REPRODUCTION.json`
- `docs/reviews/melatonin-primary-insomnia-sol/index.html`
- `docs/reviews/melatonin-primary-insomnia-sol/manifest.json`
- `docs/reviews/melatonin-primary-insomnia-sol/review.json`
- `docs/reviews/metformin-pcos-ovulation/REPRODUCTION.json`
- `docs/reviews/metformin-pcos-ovulation/index.html`
- `docs/reviews/metformin-pcos-ovulation/manifest.json`
- `docs/reviews/metformin-pcos-ovulation/review.json`
- `docs/reviews/noac-vs-warfarin-af-stroke/REPRODUCTION.json`
- `docs/reviews/noac-vs-warfarin-af-stroke/index.html`
- `docs/reviews/noac-vs-warfarin-af-stroke/manifest.json`
- `docs/reviews/noac-vs-warfarin-af-stroke/review.json`
- `docs/reviews/omega3-cardiovascular-events/REPRODUCTION.json`
- `docs/reviews/omega3-cardiovascular-events/index.html`
- `docs/reviews/omega3-cardiovascular-events/manifest.json`
- `docs/reviews/omega3-cardiovascular-events/review.json`
- `docs/reviews/pcsk9-mace/REPRODUCTION.json`
- `docs/reviews/pcsk9-mace/index.html`
- `docs/reviews/pcsk9-mace/manifest.json`
- `docs/reviews/pcsk9-mace/review.json`
- `docs/reviews/probiotics-aad-prevention/REPRODUCTION.json`
- `docs/reviews/probiotics-aad-prevention/index.html`
- `docs/reviews/probiotics-aad-prevention/manifest.json`
- `docs/reviews/probiotics-aad-prevention/review.json`
- `docs/reviews/sacubitril-valsartan-hfref/REPRODUCTION.json`
- `docs/reviews/sacubitril-valsartan-hfref/index.html`
- `docs/reviews/sacubitril-valsartan-hfref/manifest.json`
- `docs/reviews/sacubitril-valsartan-hfref/review.json`
- `docs/reviews/semaglutide-obesity-mace/REPRODUCTION.json`
- `docs/reviews/semaglutide-obesity-mace/index.html`
- `docs/reviews/semaglutide-obesity-mace/manifest.json`
- `docs/reviews/semaglutide-obesity-mace/review.json`
- `docs/reviews/semaglutide-obesity-weight/REPRODUCTION.json`
- `docs/reviews/semaglutide-obesity-weight/index.html`
- `docs/reviews/semaglutide-obesity-weight/manifest.json`
- `docs/reviews/semaglutide-obesity-weight/review.json`
- `docs/reviews/sglt2-ckd-progression/REPRODUCTION.json`
- `docs/reviews/sglt2-ckd-progression/index.html`
- `docs/reviews/sglt2-ckd-progression/manifest.json`
- `docs/reviews/sglt2-ckd-progression/review.json`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/REPRODUCTION.json`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/index.html`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/manifest.json`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/review.json`
- `docs/reviews/sglt2-primary-prevention-hf/REPRODUCTION.json`
- `docs/reviews/sglt2-primary-prevention-hf/index.html`
- `docs/reviews/sglt2-primary-prevention-hf/manifest.json`
- `docs/reviews/sglt2-primary-prevention-hf/review.json`
- `docs/reviews/spironolactone-hfref-mortality/REPRODUCTION.json`
- `docs/reviews/spironolactone-hfref-mortality/index.html`
- `docs/reviews/spironolactone-hfref-mortality/manifest.json`
- `docs/reviews/spironolactone-hfref-mortality/review.json`
- `docs/reviews/statins-primary-prevention-elderly/REPRODUCTION.json`
- `docs/reviews/statins-primary-prevention-elderly/index.html`
- `docs/reviews/statins-primary-prevention-elderly/manifest.json`
- `docs/reviews/statins-primary-prevention-elderly/review.json`
- `docs/reviews/ticagrelor-vs-clopidogrel-acs/REPRODUCTION.json`
- `docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html`
- `docs/reviews/ticagrelor-vs-clopidogrel-acs/manifest.json`
- `docs/reviews/ticagrelor-vs-clopidogrel-acs/review.json`
- `docs/reviews/tocilizumab-covid19-mortality/REPRODUCTION.json`
- `docs/reviews/tocilizumab-covid19-mortality/index.html`
- `docs/reviews/tocilizumab-covid19-mortality/manifest.json`
- `docs/reviews/tocilizumab-covid19-mortality/review.json`
- `docs/reviews/tranexamic-acid-pph/REPRODUCTION.json`
- `docs/reviews/tranexamic-acid-pph/index.html`
- `docs/reviews/tranexamic-acid-pph/manifest.json`
- `docs/reviews/tranexamic-acid-pph/review.json`

Pre-existing lane-control files visible as untracked but not changed by this lane: `LANE_PROMPT.md`, `lane.log`, `lane.pid`, `lane.winpid`.
