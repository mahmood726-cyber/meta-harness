# LANE RX REPORT

## 1. What was wrong, mechanism, files

The pre-lane pages carried typed declared-absent/refusal reasons, but there was no corpus-wide check that the stated reason was true against the held source text. A trial could be labelled absent or refused while the source we already held contained the outcome number, or while the stated reason named the wrong cause.

The pre-lane pages also did not report included-trial x registered-outcome pairs where a held source contained a value that had not been extracted for the page outcome.

Mechanism added:

- `harness/reason_audit.py` builds held-source maps from committed records and classifies declared-absent/refusal rows as `REASON_TRUE`, `REASON_FALSE_VALUE_HELD`, `REASON_WRONG_KIND`, or `NOT_VERIFIABLE`.
- `harness/unextracted.py` audits included-trial x registered-outcome pairs as `EXTRACTED`, `HELD_NOT_EXTRACTED`, `NOT_IN_HELD_SOURCES`, or `ABSENT_BY_DESIGN`.
- `harness/pipeline.py` attaches both audit objects after existing absence annotation. It does not rewrite extractor output, pools, membership, or reason codes.
- `harness/page.py` renders an additive `Reason-code audit` block on every page and a row-level `reason-code audit:` line beside each declared-absent/refusal code.
- `scripts/reason_audit_sweep.py` writes `docs/reason_audit_sweep.json`.
- `scripts/unextracted_sweep.py` writes `docs/unextracted_sweep.json`.

MEASURED corpus outputs:

- Reason-code denominator: `668` declared-absent/refusal reason-code rows across `32` pages.
- Reason-code verdicts: `REASON_TRUE=575`, `REASON_FALSE_VALUE_HELD=64`, `REASON_WRONG_KIND=29`, `NOT_VERIFIABLE=0`.
- By code kind:
  - `OUTCOME_NOT_IN_SOURCE`: `12` false-held, `16` wrong-kind, `0` not-verifiable of `453` rows.
  - `SOURCE_NOT_RETRIEVED`: `0` false-held, `2` wrong-kind, `0` not-verifiable of `152` rows.
  - `EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH`: `8` false-held, `3` wrong-kind, `0` not-verifiable of `11` rows.
  - `REFUSED_ON_EVIDENCE`: `0` false-held, `1` wrong-kind, `0` not-verifiable of `1` row.
  - `EXTRACTION_NOT_PERFORMED`: `12` false-held, `0` wrong-kind, `0` not-verifiable of `12` rows.
  - `COUNTS_PRESENT_NOT_CORROBORATED`: `31` false-held, `6` wrong-kind, `0` not-verifiable of `37` rows.
  - `TIMEPOINT_MISMATCH`: `1` false-held, `1` wrong-kind, `0` not-verifiable of `2` rows.
- Unextracted denominator: `783` included-trial x registered-outcome pairs across `32` pages.
- Unextracted verdicts: `EXTRACTED=115`, `HELD_NOT_EXTRACTED=64`, `NOT_IN_HELD_SOURCES=597`, `ABSENT_BY_DESIGN=7`.
- By outcome kind:
  - `primary`: `30` held-not-extracted of `305` pairs.
  - `harm`: `34` held-not-extracted of `470` pairs.
  - `secondary`: `0` held-not-extracted of `8` pairs.

MEASURED contract check: comparing rebuilt `review.json` files to `ad5e7c66` after ignoring only the new audit fields found `contract_changed=[]` over `32` slugs. Pooled rows, declared-absent membership, and existing reason codes stayed unchanged.

Static-vs-dynamic hardcode disclosure:

| Item | Static or dynamic | Disclosure |
| --- | --- | --- |
| Verdict labels | Static | Fixed constants in `harness/reason_audit.py` and `harness/unextracted.py`; no research result encoded in the labels. |
| Plant expected spans | Static test expectations | The test literals are copied from the committed prefix objects and prove the instruments fire on known debts. |
| Sweep denominators and page counts | Dynamic | Read from `docs/reviews/*/review.json` at script runtime. |
| Source text | Dynamic | Read from committed cached records/source fields; no network search. |
| Rendered audit counts | Dynamic | Derived from attached audit rows during rebuild. |

## 2. Plants

`tests/test_reason_audit.py::test_plant_cocs_reason_code_false_value_held`

- Assertion: for `ad5e7c66:docs/reviews/colchicine-postop-af/review.json`, outcome `Postoperative atrial fibrillation`, row `PMID 36286314`, `verdict == REASON_FALSE_VALUE_HELD`, `source_id == abstract:36286314`, and the source span contains `POAF was observed`, `21 (18.6%)`, and `39 (30.7%)`.
- MEASURED pre-fix output:

```json
{"verdict":"REASON_FALSE_VALUE_HELD","stated_reason_code":"COUNTS_PRESENT_NOT_CORROBORATED","source_id":"abstract:36286314","source_span":"POAF was observed in 21 (18.6%) patients of the colchicine group vs. 39 (30.7%) control patients (OR 0.515; 95% Cl 0.281-0.943; p = 0.029)."}
```

- MEASURED post-fix output on rebuilt object: the same verdict is attached under the row's `reason_code_audit`; the original `COUNTS_PRESENT_NOT_CORROBORATED` code remains unchanged.

`tests/test_reason_audit.py::test_synthetic_reason_true_when_value_absent`

- Assertion: a synthetic `OUTCOME_NOT_IN_SOURCE` row with held text that reports only unrelated outcomes returns `REASON_TRUE`.
- MEASURED post-fix output: included in focused pytest, `10 passed in 174.61s (0:02:54)`.

`tests/test_reason_audit.py::test_synthetic_estimand_mismatch_on_unreported_outcome_is_wrong_kind`

- Assertion: a synthetic `EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH` row with no held outcome value returns `REASON_WRONG_KIND`.
- MEASURED post-fix output: included in focused pytest, `10 passed in 174.61s (0:02:54)`.

`tests/test_unextracted.py::test_plant_akrami_mace_is_held_not_extracted`

- Assertion: for `ad5e7c66:docs/reviews/colchicine-secondary-cv-prevention/review.json`, outcome `Major adverse cardiovascular events`, trial `34876021`, `status == HELD_NOT_EXTRACTED`, `source_id == abstract:34876021`, `value_text == 8/120 vs 28/129`, and the span contains `8 events` and `28 events`.
- MEASURED pre-fix output:

```json
{"status":"HELD_NOT_EXTRACTED","trial_key":"34876021","source_id":"abstract:34876021","value_text":"8/120 vs 28/129","source_span":"Over the 6 months' period, 36 MACE occurred that were 8 events in the colchicine group compared with 28 events in the placebo group experiencing the event (P = 0.001)."}
```

- MEASURED post-fix output on rebuilt object: the same record is attached under top-level `unextracted_outcome_audit.rows`; extraction and pooling were not changed.

`tests/test_unextracted.py` synthetic controls

- Assertions: synthetic controls cover `EXTRACTED`, `HELD_NOT_EXTRACTED`, `NOT_IN_HELD_SOURCES`, and `ABSENT_BY_DESIGN`.
- MEASURED post-fix output: included in focused pytest, `10 passed in 174.61s (0:02:54)`.

## 3. Rebuilt pages and before/after rendered text

Every row below is MEASURED from the rebuilt `review.json` files. Before state for every listed page: the `ad5e7c66` rendered page had no `Reason-code audit` block. After state: the rebuilt page has the sentence pattern `Reason-code audit: <false-held> of <N> declared-absent/refusal reason code(s) ... Registered-outcome sweep: <held-not-extracted> of <N> included-trial/outcome pair(s) ...`.

| Page | Before | After |
| --- | --- | --- |
| `balanced-crystalloids-vs-saline-mortality` | no `Reason-code audit` block | `6 of 21` false-held; `3` wrong-kind; `0` not-verifiable; `6 of 24` held-not-extracted |
| `colchicine-postop-af` | no `Reason-code audit` block | `4 of 19` false-held; `0` wrong-kind; `0` not-verifiable; `4 of 24` held-not-extracted |
| `colchicine-recurrent-pericarditis` | no `Reason-code audit` block | `0 of 12` false-held; `1` wrong-kind; `0` not-verifiable; `0 of 15` held-not-extracted |
| `colchicine-secondary-cv-prevention` | no `Reason-code audit` block | `2 of 76` false-held; `2` wrong-kind; `0` not-verifiable; `2 of 81` held-not-extracted |
| `corticosteroids-cap-mortality` | no `Reason-code audit` block | `2 of 23` false-held; `2` wrong-kind; `0` not-verifiable; `2 of 27` held-not-extracted |
| `corticosteroids-covid19-mortality` | no `Reason-code audit` block | `2 of 15` false-held; `1` wrong-kind; `0` not-verifiable; `2 of 16` held-not-extracted |
| `dapagliflozin-hfpef-hosp` | no `Reason-code audit` block | `0 of 4` false-held; `0` wrong-kind; `0` not-verifiable; `0 of 5` held-not-extracted |
| `denosumab-vertebral-fracture` | no `Reason-code audit` block | `0 of 2` false-held; `0` wrong-kind; `0` not-verifiable; `0 of 5` held-not-extracted |
| `doac-vte-recurrence` | no `Reason-code audit` block | `0 of 0` false-held; `0` wrong-kind; `0` not-verifiable; `0 of 6` held-not-extracted |
| `dpp4-mace-t2d` | no `Reason-code audit` block | `0 of 2` false-held; `1` wrong-kind; `0` not-verifiable; `0 of 5` held-not-extracted |
| `empagliflozin-hfpef-hosp` | no `Reason-code audit` block | `0 of 3` false-held; `0` wrong-kind; `0` not-verifiable; `0 of 4` held-not-extracted |
| `esketamine-trd-madrs` | no `Reason-code audit` block | `2 of 8` false-held; `1` wrong-kind; `0` not-verifiable; `2 of 12` held-not-extracted |
| `finerenone-ckd-t2d-renal` | no `Reason-code audit` block | `0 of 16` false-held; `0` wrong-kind; `0` not-verifiable; `0 of 18` held-not-extracted |
| `glp1-ra-mace-t2d` | no `Reason-code audit` block | `1 of 19` false-held; `0` wrong-kind; `0` not-verifiable; `1 of 27` held-not-extracted |
| `iv-iron-hfref-hosp` | no `Reason-code audit` block | `4 of 25` false-held; `0` wrong-kind; `0` not-verifiable; `4 of 27` held-not-extracted |
| `melatonin-primary-insomnia-sol` | no `Reason-code audit` block | `0 of 17` false-held; `0` wrong-kind; `0` not-verifiable; `0 of 18` held-not-extracted |
| `metformin-pcos-ovulation` | no `Reason-code audit` block | `0 of 24` false-held; `0` wrong-kind; `0` not-verifiable; `0 of 27` held-not-extracted |
| `noac-vs-warfarin-af-stroke` | no `Reason-code audit` block | `0 of 12` false-held; `0` wrong-kind; `0` not-verifiable; `0 of 18` held-not-extracted |
| `omega3-cardiovascular-events` | no `Reason-code audit` block | `2 of 58` false-held; `11` wrong-kind; `0` not-verifiable; `2 of 66` held-not-extracted |
| `pcsk9-mace` | no `Reason-code audit` block | `0 of 4` false-held; `0` wrong-kind; `0` not-verifiable; `0 of 6` held-not-extracted |
| `probiotics-aad-prevention` | no `Reason-code audit` block | `23 of 164` false-held; `2` wrong-kind; `0` not-verifiable; `23 of 180` held-not-extracted |
| `sacubitril-valsartan-hfref` | no `Reason-code audit` block | `0 of 6` false-held; `0` wrong-kind; `0` not-verifiable; `0 of 7` held-not-extracted |
| `semaglutide-obesity-mace` | no `Reason-code audit` block | `0 of 1` false-held; `0` wrong-kind; `0` not-verifiable; `0 of 3` held-not-extracted |
| `semaglutide-obesity-weight` | no `Reason-code audit` block | `6 of 26` false-held; `4` wrong-kind; `0` not-verifiable; `6 of 28` held-not-extracted |
| `sglt2-ckd-progression` | no `Reason-code audit` block | `1 of 20` false-held; `0` wrong-kind; `0` not-verifiable; `1 of 24` held-not-extracted |
| `sglt2-hfref-hosp-cvdeath` | no `Reason-code audit` block | `0 of 7` false-held; `0` wrong-kind; `0` not-verifiable; `0 of 9` held-not-extracted |
| `sglt2-primary-prevention-hf` | no `Reason-code audit` block | `0 of 16` false-held; `0` wrong-kind; `0` not-verifiable; `0 of 20` held-not-extracted |
| `spironolactone-hfref-mortality` | no `Reason-code audit` block | `0 of 6` false-held; `0` wrong-kind; `0` not-verifiable; `0 of 9` held-not-extracted |
| `statins-primary-prevention-elderly` | no `Reason-code audit` block | `2 of 13` false-held; `0` wrong-kind; `0` not-verifiable; `2 of 15` held-not-extracted |
| `ticagrelor-vs-clopidogrel-acs` | no `Reason-code audit` block | `1 of 6` false-held; `0` wrong-kind; `0` not-verifiable; `1 of 9` held-not-extracted |
| `tocilizumab-covid19-mortality` | no `Reason-code audit` block | `6 of 33` false-held; `1` wrong-kind; `0` not-verifiable; `6 of 36` held-not-extracted |
| `tranexamic-acid-pph` | no `Reason-code audit` block | `0 of 10` false-held; `0` wrong-kind; `0` not-verifiable; `0 of 12` held-not-extracted |

Specific row-level before/after example:

- Before, `colchicine-postop-af` row `PMID 36286314` rendered the existing reason and code `COUNTS_PRESENT_NOT_CORROBORATED`.
- After, that same row additionally renders `reason-code audit: REASON_FALSE_VALUE_HELD abstract:36286314: POAF was observed in 21 (18.6%) patients ... 39 (30.7%) control patients ...`.

Reworded ratchet blocks: MEASURED none intentionally. A draft build briefly used `class='banner'` for the new audit summary and tripped `test_limitations_legacy_compare`; final code uses `class='audit-block'`, and the legacy limitation comparison passes. No `docs/ratchet_acknowledgements.json` entries were written.

MEASURED rendered coverage: `32 of 32` review pages contain `Reason-code audit`; the instruments are shown to fail on plants, so this is not a silent all-pass audit.

## 4. Tests

MEASURED command outputs:

```text
python scripts/reason_audit_sweep.py
OUT_WRITTEN C:\mh-r-RX\docs\reason_audit_sweep.json FALSE_VALUE_HELD=64 NOT_VERIFIABLE=0 N=668 topics=32
```

```text
python scripts/unextracted_sweep.py
OUT_WRITTEN C:\mh-r-RX\docs\unextracted_sweep.json HELD_NOT_EXTRACTED=64 N=783 topics=32
```

```text
python -m pytest tests/test_reason_audit.py tests/test_unextracted.py tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews tests/test_fixstate.py::test_real_store_validates -q
10 passed in 174.61s (0:02:54)
```

```text
python scripts/reproduce_review.py
32/32 reproduce (all reproducible)
```

```text
git diff --check
<no output, exit 0>
```

```text
python -m pytest tests -x -q
724 passed in 450.67s (0:07:30)
```

Intermediate failures fixed before final report:

- MEASURED full-suite failure before ledger refresh: `docs/fix_ledger.json is stale; run python scripts/render_fix_ledger.py`.
- MEASURED full-suite failure before wrapper fix: `test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews`, caused by rendering the new audit summary as a ratcheted `banner` block. Fixed by rendering it as `audit-block`.

## 5. What I did not do

- No commit, stage, stash, checkout, reset, clean, push, deploy, or SHIP.
- No network search or live external source retrieval.
- No extraction output changes.
- No pooling changes.
- No trial membership changes.
- No screening/search changes.
- No reason-code rewrites.
- No ratchet acknowledgements written; integrator can sign any acknowledgement if desired, but the final render does not remove or reword legacy absent/banner limitation blocks.
- No `INDEX.md` or workbook update, because this lane did not change project status or submission state.
- Did not run `scripts/verify_all.py`, per lane instruction.

## 6. Files changed or added

Source, scripts, tests, and corpus sweep artifacts:

- `harness/reason_audit.py`
- `harness/unextracted.py`
- `harness/pipeline.py`
- `harness/page.py`
- `scripts/reason_audit_sweep.py`
- `scripts/unextracted_sweep.py`
- `tests/test_reason_audit.py`
- `tests/test_unextracted.py`
- `docs/reason_audit_sweep.json`
- `docs/unextracted_sweep.json`
- `docs/fix_ledger.json`

Generated review-page files, for each MEASURED slug in Section 3:

- `docs/reviews/<slug>/review.json`
- `docs/reviews/<slug>/index.html`
- `docs/reviews/<slug>/manifest.json`
- `docs/reviews/<slug>/REPRODUCTION.json`

Generated blind-page files:

- `docs/m/m031db369/index.html`
- `docs/m/m0594e053/index.html`
- `docs/m/m078be06c/index.html`
- `docs/m/m09091404/index.html`
- `docs/m/m0c0e2bf1/index.html`
- `docs/m/m0effd17d/index.html`
- `docs/m/m152f58d8/index.html`
- `docs/m/m175bd0c3/index.html`
- `docs/m/m22bf81d5/index.html`
- `docs/m/m24cd09bc/index.html`
- `docs/m/m250220c2/index.html`
- `docs/m/m284e6ef4/index.html`
- `docs/m/m28cd9b74/index.html`
- `docs/m/m29f6dc16/index.html`
- `docs/m/m2da64325/index.html`
- `docs/m/m3c1155fb/index.html`
- `docs/m/m42da3313/index.html`
- `docs/m/m4670a8f9/index.html`
- `docs/m/m4ee9db19/index.html`
- `docs/m/m51474705/index.html`
- `docs/m/m5384fd3c/index.html`
- `docs/m/m586876fa/index.html`
- `docs/m/m595c5e9f/index.html`
- `docs/m/m5b3fd56c/index.html`
- `docs/m/m5d324d5e/index.html`
- `docs/m/m5e5590d5/index.html`
- `docs/m/m612a48aa/index.html`
- `docs/m/m660dc5c7/index.html`
- `docs/m/m6840fc8a/index.html`
- `docs/m/m6c992fd1/index.html`
- `docs/m/m6dd4233b/index.html`
- `docs/m/m6e7e8ab7/index.html`
- `docs/m/m6f3cdffa/index.html`
- `docs/m/m7d28b3cd/index.html`
- `docs/m/m80e26e26/index.html`
- `docs/m/m87167438/index.html`
- `docs/m/m89f8021b/index.html`
- `docs/m/m8db5253b/index.html`
- `docs/m/m904d47d6/index.html`
- `docs/m/m971790c1/index.html`
- `docs/m/m979b0810/index.html`
- `docs/m/m9e04a632/index.html`
- `docs/m/ma014d0a4/index.html`
- `docs/m/ma0b91971/index.html`
- `docs/m/ma178f5d6/index.html`
- `docs/m/ma451f131/index.html`
- `docs/m/mabc6654a/index.html`
- `docs/m/mae710922/index.html`
- `docs/m/maf69923c/index.html`
- `docs/m/mb53e1ed5/index.html`
- `docs/m/mb6ceb13c/index.html`
- `docs/m/mc16cd596/index.html`
- `docs/m/md1780020/index.html`
- `docs/m/md2772f36/index.html`
- `docs/m/md68c6ad6/index.html`
- `docs/m/md7fd1d6e/index.html`
- `docs/m/mdd4bf0ae/index.html`
- `docs/m/me0751432/index.html`
- `docs/m/me17c0a34/index.html`
- `docs/m/me5d639f4/index.html`
- `docs/m/me79cb3b0/index.html`
- `docs/m/mec03e6db/index.html`
- `docs/m/mf6cd36c2/index.html`
- `docs/m/mf6f36ebe/index.html`

Existing untracked lane-control files left untouched except for reading where needed:

- `LANE_PROMPT.md`
- `lane.log`
- `lane.pid`
- `lane.winpid`
