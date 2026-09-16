# LANE RR Report

## 1. What Was Wrong

The defect was that declared-absent/refused rows could carry a generic fallback reason even when the cached source contradicted that reason. In the handed case, `iv-iron-hfref-hosp` / primary outcome / AFFIRM-AHF (`PMID 33197395`) said `SOURCE_NOT_RETRIEVED` with "no percentage-corroborated arm counts or effect+CI ... found in the abstract", but the cached abstract reports: "217 total heart failure hospitalisations ... (RR 0.74; 95% CI 0.58-0.94...)". That value is not poolable for the registered first-event RR outcome because it is a recurrent-event/rate-class effect, so the true refusal is `EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH`, not source absence.

Mechanism fixed:

- `harness/absence.py`: added source-audit refusal classification with typed codes, source spans, observed effect text, declared-vs-observed class checks, count-candidate detection, and truth-verdict helpers.
- `harness/pipeline.py`: replaced the old late three-bucket absence annotation with the typed classifier for every declared-absent/refused row.
- `harness/page.py`: rendered the new `reason_code`, source span, and basis in the declared-absent table.
- `scripts/refusal_reason_sweep.py`: added the corpus-wide sweep over committed `docs/reviews/*/review.json` rows and committed source cache.

Static-vs-dynamic disclosure:

| Item | Type | Disclosure |
|---|---|---|
| Reason-code names | STATIC | Fixed ontology labels only. |
| Effect/count values and spans | DYNAMIC | Read from committed `cache/<slug>/records.json`, optional `cache/<slug>/ft_<pmid>.txt`, and rebuilt review objects. |
| Sweep denominator | DYNAMIC | MEASURED from `declared_absent_trials` in committed `docs/reviews/*/review.json`. |
| Page primary results | DYNAMIC | Rebuilt by `scripts/build_topic.py` from committed cache; no new pooling rule was added. |

## 2. Plant

Plant test: `tests/test_refusal_reason_truth.py::test_plant_prefix_affirm_refusal_reason_is_false`.

Exact assertions:

- load `aa8ed28a:docs/reviews/iv-iron-hfref-hosp/review.json` by read-only `git show`;
- classify the `33197395` declared-absent row against the cached AFFIRM-AHF record;
- assert `classified["verdict"] == "FALSE"`;
- assert `classified["corrected_code"] == "EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH"`;
- assert the quoted span contains `217 total heart failure hospitalisations` and `RR 0.74`.

Pre-rebuild output, MEASURED:

```text
.F.. [100%]
FAILED tests/test_refusal_reason_truth.py::test_postfix_affirm_refusal_reason_is_true
1 failed, 3 passed in 7.06s
```

The plant assertion on the pre-fix object passed; the post-fix check failed because the served page had not yet been rebuilt.

Post-fix output, MEASURED:

```text
.... [100%]
4 passed in 6.10s
```

## 3. Rebuilt Pages

All 32 topics were rebuilt offline with `python scripts/build_topic.py <slug> --now 2026-09-11`; `doac-vte-recurrence` rebuilt cleanly but had no byte diff. The 31 pages below changed bytes. Primary results and declared-absent row counts were unchanged; the changed sentences are the declared-absent/refusal table details, which now show typed `reason_code` plus source span/basis.

| Page | Primary before -> after | Declared-absent rows |
|---|---|---|
| `balanced-crystalloids-vs-saline-mortality` | MEASURED `k=2, estimate=0.9774, suppressed=None` -> `k=2, estimate=0.9774, suppressed=None` | MEASURED 6 -> 6 |
| `colchicine-postop-af` | MEASURED `k=4, estimate=0.6735, suppressed=None` -> `k=4, estimate=0.6735, suppressed=None` | MEASURED 4 -> 4 |
| `colchicine-recurrent-pericarditis` | MEASURED `k=2, estimate=0.4813, suppressed=None` -> `k=2, estimate=0.4813, suppressed=None` | MEASURED 1 -> 1 |
| `colchicine-secondary-cv-prevention` | MEASURED `k=3, estimate=0.8134, suppressed=None` -> `k=3, estimate=0.8134, suppressed=None` | MEASURED 26 -> 26 |
| `corticosteroids-cap-mortality` | MEASURED `k=2, estimate=0.5458, suppressed=None` -> `k=2, estimate=0.5458, suppressed=None` | MEASURED 7 -> 7 |
| `corticosteroids-covid19-mortality` | MEASURED `k=1, estimate=0.83, suppressed=None` -> `k=1, estimate=0.83, suppressed=None` | MEASURED 7 -> 7 |
| `dapagliflozin-hfpef-hosp` | MEASURED `k=1, estimate=0.82, suppressed=None` -> `k=1, estimate=0.82, suppressed=None` | MEASURED 4 -> 4 |
| `denosumab-vertebral-fracture` | MEASURED `k=1, estimate=0.32, suppressed=None` -> `k=1, estimate=0.32, suppressed=None` | MEASURED 0 -> 0 |
| `dpp4-mace-t2d` | MEASURED `k=3, estimate=1.0074, suppressed=None` -> `k=3, estimate=1.0074, suppressed=None` | MEASURED 2 -> 2 |
| `empagliflozin-hfpef-hosp` | MEASURED `k=1, estimate=0.79, suppressed=None` -> `k=1, estimate=0.79, suppressed=None` | MEASURED 3 -> 3 |
| `esketamine-trd-madrs` | MEASURED `k=4, estimate=-3.3445, suppressed=None` -> `k=4, estimate=-3.3445, suppressed=None` | MEASURED 2 -> 2 |
| `finerenone-ckd-t2d-renal` | MEASURED `k=2, estimate=0.8407, suppressed=None` -> `k=2, estimate=0.8407, suppressed=None` | MEASURED 4 -> 4 |
| `glp1-ra-mace-t2d` | MEASURED `k=8, estimate=0.856, suppressed=None` -> `k=8, estimate=0.856, suppressed=None` | MEASURED 1 -> 1 |
| `iv-iron-hfref-hosp` | MEASURED `k=2, estimate=None, suppressed=True` -> `k=2, estimate=None, suppressed=True` | MEASURED 7 -> 7 |
| `melatonin-primary-insomnia-sol` | MEASURED `k=1, estimate=-17.4, suppressed=None` -> `k=1, estimate=-17.4, suppressed=None` | MEASURED 8 -> 8 |
| `metformin-pcos-ovulation` | MEASURED `k=3, estimate=2.0733, suppressed=None` -> `k=3, estimate=2.0733, suppressed=None` | MEASURED 6 -> 6 |
| `noac-vs-warfarin-af-stroke` | MEASURED `k=4, estimate=0.8069, suppressed=None` -> `k=4, estimate=0.8069, suppressed=None` | MEASURED 5 -> 5 |
| `omega3-cardiovascular-events` | MEASURED `k=7, estimate=0.943, suppressed=None` -> `k=7, estimate=0.943, suppressed=None` | MEASURED 15 -> 15 |
| `pcsk9-mace` | MEASURED `k=2, estimate=0.85, suppressed=None` -> `k=2, estimate=0.85, suppressed=None` | MEASURED 0 -> 0 |
| `probiotics-aad-prevention` | MEASURED `k=16, estimate=0.702, suppressed=None` -> `k=16, estimate=0.702, suppressed=None` | MEASURED 44 -> 44 |
| `sacubitril-valsartan-hfref` | MEASURED `k=1, estimate=0.8, suppressed=None` -> `k=1, estimate=0.8, suppressed=None` | MEASURED 6 -> 6 |
| `semaglutide-obesity-mace` | MEASURED `k=1, estimate=0.8, suppressed=None` -> `k=1, estimate=0.8, suppressed=None` | MEASURED 0 -> 0 |
| `semaglutide-obesity-weight` | MEASURED `k=2, estimate=-11.8449, suppressed=None` -> `k=2, estimate=-11.8449, suppressed=None` | MEASURED 12 -> 12 |
| `sglt2-ckd-progression` | MEASURED `k=3, estimate=0.6836, suppressed=None` -> `k=3, estimate=0.6836, suppressed=None` | MEASURED 5 -> 5 |
| `sglt2-hfref-hosp-cvdeath` | MEASURED `k=2, estimate=0.7755, suppressed=None` -> `k=2, estimate=0.7755, suppressed=None` | MEASURED 1 -> 1 |
| `sglt2-primary-prevention-hf` | MEASURED `k=4, estimate=0.6956, suppressed=None` -> `k=4, estimate=0.6956, suppressed=None` | MEASURED 16 -> 16 |
| `spironolactone-hfref-mortality` | MEASURED `k=3, estimate=0.8685, suppressed=None` -> `k=3, estimate=0.8685, suppressed=None` | MEASURED 0 -> 0 |
| `statins-primary-prevention-elderly` | MEASURED `k=2, estimate=0.6803, suppressed=None` -> `k=2, estimate=0.6803, suppressed=None` | MEASURED 3 -> 3 |
| `ticagrelor-vs-clopidogrel-acs` | MEASURED `k=2, estimate=1.0479, suppressed=None` -> `k=2, estimate=1.0479, suppressed=None` | MEASURED 1 -> 1 |
| `tocilizumab-covid19-mortality` | MEASURED `k=1, estimate=0.83, suppressed=None` -> `k=1, estimate=0.83, suppressed=None` | MEASURED 11 -> 11 |
| `tranexamic-acid-pph` | MEASURED `k=1, estimate=0.81, suppressed=None` -> `k=1, estimate=0.81, suppressed=None` | MEASURED 3 -> 3 |

Handed iv-iron before/after rows, MEASURED:

| PMID | Before | After |
|---|---|---|
| `33197395` | `SOURCE_NOT_RETRIEVED`; generic no effect/counts text | `EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH`; span `217 total heart failure hospitalisations ... RR 0.74; 95% CI 0.58-0.94` |
| `36347265` | `SOURCE_NOT_RETRIEVED`; generic no effect/counts text | `EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH`; span `rate ratio [RR] 0.82 [95% CI 0.66 to 1.02]` |
| `37632463` | `SOURCE_NOT_RETRIEVED`; generic no effect/counts text | `COUNTS_PRESENT_NOT_CORROBORATED`; span `a total of 297 and 332 hospitalizations for heart failure` |

Sweep result, MEASURED:

```text
OUT_WRITTEN C:\mh-r-RR\docs\refusal_reason_sweep.json FALSE=0 N=674 topics=32
```

JSON summary, MEASURED:

```text
topics=32; N=674; counts={'TRUE': 674, 'FALSE': 0, 'NOT_CHECKABLE': 0}
```

## 4. Tests

Targeted plant:

```text
python -m pytest tests/test_refusal_reason_truth.py -q
.... [100%]
4 passed in 6.10s
```

Leakscan after changing the sweep artifact to avoid machine-readable suppressed CI keys:

```text
python -m pytest tests/test_leakscan.py::test_shipped_corpus_has_no_suppressed_leak -q
. [100%]
1 passed in 4.12s
```

Reproduction:

```text
python scripts/reproduce_review.py
32/32 reproduce (all reproducible)
```

Full required suite:

```text
python -m pytest tests -x -q
643 passed in 631.33s (0:10:31)
```

Interim blockers fixed during verification:

- First full run failed on stale fix-state generated files; fixed with `python scripts/render_fix_ledger.py` and `python scripts/rewrite_fixstate_lines.py`.
- Second full run failed because `docs/refusal_reason_sweep.json` used nested numeric `observed_effect.ci_low/ci_high` keys for a suppressed topic; fixed by emitting `observed_effect_text` instead.

## 5. Not Done

- Did not run any search, fetch, or network path.
- Did not modify `harness/extract.py`, `harness/synth.py`, `harness/page.py` beyond rendering the new reason code/span, search code, or `docs/refusals.json`.
- Did not add or remove any trial from any pool.
- Did not weaken endpoint, estimand, timepoint, or population gates.
- Did not commit, stage, stash, checkout, reset, clean, or touch `.git/`.

## 6. Files Changed Or Added

Core code:

- `harness/absence.py`
- `harness/page.py`
- `harness/pipeline.py`

New lane code/tests/artifacts:

- `scripts/refusal_reason_sweep.py`
- `tests/test_refusal_reason_truth.py`
- `docs/refusal_reason_sweep.json`
- `LANE-RR-REPORT.md`

Generated fix-state artifacts:

- `docs/fix_ledger.json`
- `docs/evidence/hazard-consumers-2026-09-14/README.md`
- `docs/evidence/search-v2-measurement-2026-09-15/README.md`

Generated review artifacts:

- For each changed slug listed in section 3: `docs/reviews/<slug>/review.json`, `index.html`, `manifest.json`, and `REPRODUCTION.json`.

Generated blind-page artifacts:

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

Pre-existing untracked lane inputs/logs left unmodified:

- `LANE_PROMPT.md`
- `lane.log`
- `lane.pid`
- `lane.winpid`
