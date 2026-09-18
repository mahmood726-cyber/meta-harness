# LANE EX Report

## 1. What was wrong, mechanism, files

Within-trial consumer consistency was not enforced after extraction. The page could say "absent" or "not stated" while its own committed cache contained usable source text:

- outcome cells: declared-absent rows could keep false codes such as `OUTCOME_NOT_IN_SOURCE` even when the cached abstract, CT.gov results, or cached full text contained event counts or mean/SD/n.
- funding cells: funding disclosure was generated for pooled trials only, so included-but-unpooled trials with cached funder text were invisible to the page and appeared as unknown/not stated.
- identity cells: rows did not consistently carry separate `trial_id`, `report_id`, `effect_source_id`, and `outcome_effect_id`; SGLT2 rows using companion reports rendered as if the trial report itself supplied the effect.
- reconstructed rows: AMPLIFY in `doac-vte-recurrence` used reconstructed counts while the same source span also reported RR+CI; this needed a visible row state, not a pool change.

Files/mechanism:

- Added `harness/consumer_consistency.py`: cache-only audit/annotation for included trial x registered outcome plus funding. It annotates source-visible non-pooled values as typed extraction debt/refusal, refreshes funding from cached full text/abstract/linked records, stamps row identity fields, and records `EXTRACTED_RECONSTRUCTION_WHILE_PUBLISHED_EXISTS` when a reconstructed row's source span also reports an effect+CI.
- Added `scripts/consumer_consistency_sweep.py`: writes `docs/consumer_consistency_sweep.json` with `n_source_value_not_accounted` and `n_reason_code_false` over the 32 tracked review pages.
- Added `tests/test_consumer_consistency.py`: plants for Akrami, COPS, Japanese esketamine, esketamine funding, and a true-absence synthetic control.
- Modified `harness/absence.py`: added typed states `RETRIEVED_INCOMPATIBLE_STRUCTURE`, `RETRIEVED_REFUSED_WITH_REASON`, `UNIT_MISMATCH_CYCLE_LEVEL`.
- Modified `harness/pipeline.py`: calls the consumer-consistency annotator after the review object is built; it does not alter search, screening, or synthesis.
- Modified `harness/page.py` and `harness/limitations.py`: render included-trial funding language, identity/effect-source labels, and the consumer-consistency warning.

Hardcode disclosure:

| Item | Static or dynamic | Disclosure |
| --- | --- | --- |
| Sweep denominator | Dynamic | Reads served `docs/reviews/*/review.json`, topic configs, and `cache/<slug>/records.json`. |
| Source values | Dynamic | Read from committed cache and sidecar `ft_*.txt`/CT.gov result payloads; no network. |
| Detection patterns | Static | Regex/source-shape recognizers for counts, mean/SD/n, funding anchors, and effect+CI-in-source. |
| Trial effects/pool values | Dynamic | Existing extractor/synthesis outputs; no hardcoded HR/RR/MD/N values are added to production code. |
| Plant assertions | Static test fixtures | Tests assert known source spans on the committed `ad5e7c66` objects only to prove the gate fires pre-fix. |

Measured sweep before and after:

- Pre-fix command: `python scripts/consumer_consistency_sweep.py --ref ad5e7c66 --out .\.tmp\consumer_consistency_sweep-prefix.json`
- Pre-fix output: `OUT_WRITTEN .tmp\consumer_consistency_sweep-prefix.json source=ad5e7c66 value_not_accounted=39 of 1088 cells; reason_code_false=43 of 1088 cells; pages=32`
- Post-fix command: `python scripts/consumer_consistency_sweep.py`
- Post-fix output: `OUT_WRITTEN C:\mh-r-EX\docs\consumer_consistency_sweep.json source=current value_not_accounted=0 of 1088 cells; reason_code_false=0 of 1088 cells; pages=32`
- Primary pool result changes: MEASURED `primary_result_changes 0`.

## 2. Plants

`tests/test_consumer_consistency.py` contains these exact plant assertions:

- `test_plant_prefix_akrami_mace_source_value_is_unaccounted`: `reason_code_false`, `unaccounted_source_value`, and source span contains `8 events` and `28 events` for PMID 34876021 MACE.
- `test_plant_prefix_cops_mace_reason_code_false`: `reason_code_false`, `source_reason_code == KNOWN_REPORTED_NOT_YET_EXTRACTED`, and source span contains `24 events` and `38 events` for PMID 32862667.
- `test_plant_prefix_esketamine_japanese_ctgov_means_refuse_false_absence`: `reason_code_false`, `source_reason_code == RETRIEVED_REFUSED_WITH_REASON`, and CT.gov source span includes `mean -15.2 (SD 13.07, n=39)` and `mean -15.3 (SD 11.68, n=72)`.
- `test_plant_prefix_esketamine_funding_janssen_not_unknown`: `reason_code_false`, `source_state == INDUSTRY_SPONSORED`, and source span includes `Janssen`.
- `test_synthetic_retrieved_outcome_not_reported_is_not_a_violation`: true absence returns `RETRIEVED_OUTCOME_NOT_REPORTED`, `source_has_value == False`, and no false reason code.
- `test_postfix_named_rows_are_accounted_after_rebuild`: current rebuilt Akrami, COPS, Japanese esketamine, and esketamine funding cells are no longer false/unaccounted.

Pre-fix targeted output after adding the plant but before rebuilding current pages:

```text
.....F                                                                   [100%]
1 failed, 5 passed in 3.31s
```

Post-fix targeted output:

```text
......                                                                   [100%]
6 passed in 7.50s
```

## 3. Rebuilt page byte changes

Common reworded block for integrator ratchet acknowledgement:

- Heading block: `Funding / conflict-of-interest disclosure`.
- Before sentence family: `per pooled trial`, `each pooled trial`, and `pooled trials are`.
- After sentence family: `per included trial`, `each included trial`, and `included trials are`.
- Why: funding is now a consumer-consistency cell for every included trial, not only pooled trials.

Every listed page had regenerated `review.json`, `index.html`, `manifest.json`, and `REPRODUCTION.json`. Primary k/effect/CI/tau2 did not change on any page.

| Page | Before -> after specific page content |
| --- | --- |
| `balanced-crystalloids-vs-saline-mortality` | Funding rows 2 -> 8; known industry-tied count unchanged `0 of 1 known`; added included-trial funding rows for PMID 23732264, 26444692, 27604335, 27749094, 29485925, NCT07189091. Identity fields added to pooled rows. |
| `colchicine-postop-af` | Funding rows 4 -> 8; added PMID 22090167, 36286314, NCT07287345, NCT07611019. Reconstructed rows with published effect+CI now show `EXTRACTED_RECONSTRUCTION_WHILE_PUBLISHED_EXISTS` where applicable. |
| `colchicine-recurrent-pericarditis` | Funding rows 2 -> 3; added PMID 23992557. Reconstructed rows with published effect+CI now show the same consumer-consistency warning where applicable. |
| `colchicine-secondary-cv-prevention` | Funding rows 4 -> 27. MACE absence reasons for PMID 34876021 and 32862667: `OUTCOME_NOT_IN_SOURCE` -> `KNOWN_REPORTED_NOT_YET_EXTRACTED`; COPS GI and non-cardiovascular death rows likewise moved to extraction-debt rather than false absence. |
| `corticosteroids-cap-mortality` | Funding rows 3 -> 9; added PMID 15557131, 21406101, 21636122, 33446608, 35723686, 8339624. |
| `corticosteroids-covid19-mortality` | Funding rows 1 -> 8; added PMID 32785710, 32876689, 32876695, 32876697, 34138478, NCT04344730, NCT04561180. |
| `dapagliflozin-hfpef-hosp` | Funding rows 1 -> 5; added PMID 34711976, 37534453, NCT03877224, NCT04475042. |
| `denosumab-vertebral-fracture` | Identity fields added for vertebral, nonvertebral, and hip fracture rows; visible trial IDs unchanged. |
| `doac-vte-recurrence` | AMPLIFY PMID 23808982 now carries `EXTRACTED_RECONSTRUCTION_WHILE_PUBLISHED_EXISTS` while retaining 59/2609 vs 71/2635 and the same pooled result. |
| `dpp4-mace-t2d` | Funding rows 3 -> 5; industry-known count `1 of 1` -> `3 of 3`; added EXAMINE PMID 23992602 and TECOS PMID 26052984 funding statements. |
| `empagliflozin-hfpef-hosp` | Funding rows 1 -> 4; added NCT03448406, NCT05138575, NCT06249945. |
| `esketamine-trd-madrs` | Funding rows 4 -> 6; industry-known count `0 of 0` -> `3 of 3`; added PMID 34696742 and NCT01998958. Japanese trial PMID 34696742 reason `COUNTS_PRESENT_NOT_CORROBORATED` -> `RETRIEVED_REFUSED_WITH_REASON` with CT.gov mean/SD/n span. |
| `finerenone-ckd-t2d-renal` | Funding rows 2 -> 6; added PMID 26325557, NCT01968668, NCT07026539, NCT07775846. |
| `glp1-ra-mace-t2d` | Funding rows 8 -> 9; industry-known count `8 of 8` -> `9 of 9`; added ELIXA PMID 26630143. |
| `iv-iron-hfref-hosp` | Funding rows 2 -> 9; known industry/mixed count `0 of 0` -> `5 of 6`; added PMID 18191732, 19920054, 28701470, 33197395, 34080008, 36347265, 37632463. |
| `melatonin-primary-insomnia-sol` | Funding rows 1 -> 9; known count `0 of 0` -> `2 of 2`; added PMID 12790159, 17875243, 18036082, 19584739, 22346363, 27559258, 33157425, NCT00816673. |
| `metformin-pcos-ovulation` | Funding rows 3 -> 9; known count `0 of 0` -> `1 of 1`; added six included-but-unpooled funding rows. Cycle-level and incompatible-structure refusal states remain typed. |
| `noac-vs-warfarin-af-stroke` | Funding rows 4 -> 9; added NCT00504556, NCT00806624, NCT00829933, NCT02935855, NCT05006287. |
| `omega3-cardiovascular-events` | Funding rows 7 -> 22; known industry-tied count `2 of 5` -> `3 of 6`; added included-trial funding rows for unpooled PMIDs/NCTs. Reconstructed rows with source-reported effect+CI now show the consumer-consistency warning where applicable. |
| `pcsk9-mace` | Identity fields added for both pooled MACE rows; visible trial IDs unchanged. |
| `probiotics-aad-prevention` | Funding rows 16 -> 60; known industry/mixed count `1 of 2` -> `5 of 8`; added funding cells for included unpooled records. Reconstructed rows with published effect+CI now show the consumer-consistency warning where applicable. |
| `sacubitril-valsartan-hfref` | Funding rows 1 -> 7; added NCT02468232, NCT02554890, NCT02874794, NCT02900378, NCT04853758, NCT05487261. |
| `semaglutide-obesity-mace` | Identity fields added for MACE and discontinuation rows; visible trial IDs unchanged. |
| `semaglutide-obesity-weight` | Funding rows 2 -> 14; industry/mixed known count `1 of 1` -> `6 of 6`; several source-visible weight-change rows moved from estimand/timepoint/source false absence to `KNOWN_REPORTED_NOT_YET_EXTRACTED`. |
| `sglt2-ckd-progression` | Funding rows 3 -> 8; added NCT05614115, NCT05884866, NCT06350123, NCT07060417, NCT07344922. |
| `sglt2-hfref-hosp-cvdeath` | Funding rows 2 -> 3; added NCT06229678. |
| `sglt2-primary-prevention-hf` | Funding rows 4 -> 20; known industry count `4 of 4` -> `9 of 9`. Visible identities now render effect sources: CANVAS `PMID 28605608 (effect from PMID 29526832)`, EMPA-REG `PMID 26378978 (effect from PMID 26819227)`, VERTIS `PMID 32966714 (effect from PMID 33026243)`. |
| `spironolactone-hfref-mortality` | Identity fields added for mortality rows; visible trial IDs unchanged. |
| `statins-primary-prevention-elderly` | Funding rows 2 -> 5; added PMID 28531241, 30251369, NCT00127218. |
| `ticagrelor-vs-clopidogrel-acs` | Funding rows 2 -> 3; added PMID 17980250. |
| `tocilizumab-covid19-mortality` | Funding rows 3 -> 12; known industry/mixed count `2 of 3` -> `5 of 6`; added PMID 33080005, 33080017, 33085857, 33472855, 34609549, 38157348, 40232661, NCT04335071, NCT04412772. |
| `tranexamic-acid-pph` | Funding rows 1 -> 4; added PMID 32143721, 36243576, NCT02026297. |

## 4. Tests

Commands and final outputs:

```text
python scripts/consumer_consistency_sweep.py
OUT_WRITTEN C:\mh-r-EX\docs\consumer_consistency_sweep.json source=current value_not_accounted=0 of 1088 cells; reason_code_false=0 of 1088 cells; pages=32
```

```text
python scripts/reproduce_review.py
32/32 reproduce (all reproducible)
```

```text
python -m pytest tests/test_consumer_consistency.py -q
6 passed in 7.50s
```

```text
python -m pytest tests -x -q
722 passed in 1349.40s (0:22:29)
```

```text
git diff --check
PASS (no output)
```

## 5. What I did not do and why

- Did not commit, stage, stash, checkout, reset, clean, push, or touch `.git`.
- Did not run network searches or fetch new sources.
- Did not change pooling arithmetic, pooled-trial membership, screening decisions, `harness/synth.py`, or search code.
- Did not sign ratchet acknowledgements. Reworded funding blocks and marker/count changes are listed above for the integrator to acknowledge.
- Did not promote extraction-debt rows into primary pools. COPS, Akrami MACE, and other source-visible values are rendered/typed as debt or refusal unless already poolable by the existing protocol path.

## 6. Files changed or added

Added:

- `LANE-EX-REPORT.md`
- `docs/consumer_consistency_sweep.json`
- `harness/consumer_consistency.py`
- `scripts/consumer_consistency_sweep.py`
- `tests/test_consumer_consistency.py`

Modified code:

- `harness/absence.py`
- `harness/limitations.py`
- `harness/page.py`
- `harness/pipeline.py`

Modified generated/support files:

- `docs/fix_ledger.json`
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

For each of these 32 tracked review directories, `REPRODUCTION.json`, `index.html`, `manifest.json`, and `review.json` were regenerated:

- `balanced-crystalloids-vs-saline-mortality`
- `colchicine-postop-af`
- `colchicine-recurrent-pericarditis`
- `colchicine-secondary-cv-prevention`
- `corticosteroids-cap-mortality`
- `corticosteroids-covid19-mortality`
- `dapagliflozin-hfpef-hosp`
- `denosumab-vertebral-fracture`
- `doac-vte-recurrence`
- `dpp4-mace-t2d`
- `empagliflozin-hfpef-hosp`
- `esketamine-trd-madrs`
- `finerenone-ckd-t2d-renal`
- `glp1-ra-mace-t2d`
- `iv-iron-hfref-hosp`
- `melatonin-primary-insomnia-sol`
- `metformin-pcos-ovulation`
- `noac-vs-warfarin-af-stroke`
- `omega3-cardiovascular-events`
- `pcsk9-mace`
- `probiotics-aad-prevention`
- `sacubitril-valsartan-hfref`
- `semaglutide-obesity-mace`
- `semaglutide-obesity-weight`
- `sglt2-ckd-progression`
- `sglt2-hfref-hosp-cvdeath`
- `sglt2-primary-prevention-hf`
- `spironolactone-hfref-mortality`
- `statins-primary-prevention-elderly`
- `ticagrelor-vs-clopidogrel-acs`
- `tocilizumab-covid19-mortality`
- `tranexamic-acid-pph`

Temp/diagnostic:

- `.tmp/consumer_consistency_sweep-prefix.json`

Untracked lane control files present but not part of my implementation:

- `LANE_PROMPT.md`
- `lane.log`
- `lane.pid`
- `lane.winpid`
