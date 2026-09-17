# LANE TE Report

## 1. What Was Wrong

MEASURED: `sglt2-hfref-hosp-cvdeath` pooled DAPA-HF's broader primary composite as arm-count RR input even though held CT.gov results contained the review target endpoint. The pre-fix object at `ad5e7c66:docs/reviews/sglt2-hfref-hosp-cvdeath/review.json` used 386/2373 vs 502/2371 and the source string:

> abstract arm-level counts (percentage-corroborated): RESULTS: Over a median of 18.2 months, the primary outcome occurred in 386 of 2373 patients (16.3%) in the dapagliflozin group and in 502 of 2371 patients (21.2%) in the placebo group (hazard ratio, 0

Mechanism fixed:

- Added `harness/target_endpoint.py` to enumerate abstract and CT.gov candidates, classify `EXACT_TARGET`, `NEAR_MATCH`, or `DIFFERENT_OUTCOME`, and select exact target endpoints before near matches; source rank is published target effect > registry published effect > reconstruction.
- Wired selection in `harness/pipeline.py` without changing membership, screening, search, K2, or synthesis.
- Rendered selector status, components, endpoint counts, alternatives, and multiple-primary disclosure in `harness/page.py`.
- Added protocol-compiler detection for `ESTIMAND_PREFERENCE_UNDECLARED` when prose permits both count RR and published HR/RR without a preference.
- Added `scripts/near_match_sweep.py` and wrote `docs/near_match_sweep.json`.

`LANE-SH-REPORT.md` and `SH.patch` were not present in this checkout. I read the available adjacent context reports: `LANE-OC-REPORT.md`, `LANE-EN-REPORT.md`, and `LANE-XS-REPORT.md`.

## 2. Plant

Test file: `tests/test_target_endpoint.py`.

Plant assertions:

- `test_sglt2_dapa_plant_prefixed_row_and_rebuilt_exact_target` loads `git show ad5e7c66:docs/reviews/sglt2-hfref-hosp-cvdeath/review.json` and asserts DAPA-HF was 386/2373 vs 502/2371 with the urgent-visit component pre-fix; it then asserts the rebuilt row is `EXACT_TARGET`, HR 0.75 [0.65, 0.85], endpoint counts 382/2373 vs 495/2371, without urgent HF visit in the target components.
- Positive controls assert EMPEROR-Reduced exact target HR 0.75 [0.65, 0.86], FIDELIO published HR 0.82 [0.73, 0.93] beats count reconstruction, synthetic CT.gov exact beats abstract near-match, and `ESTIMAND_PREFERENCE_UNDECLARED` fires on the SGLT2 protocol.

Pre-fix firing evidence, MEASURED before final wiring: `python -m pytest tests\test_target_endpoint.py -q` produced `5 failed, 1 passed in 5.21s`; after selector fixes but before rebuilding the current page it produced `1 failed, 5 passed in 6.78s` on the rebuilt-object assertion. Post-fix: `6 passed in 3.90s`.

## 3. Rebuilt Pages

MEASURED rebuild/replay:

- `sglt2-hfref-hosp-cvdeath`: DAPA-HF changed from reconstructed near-match primary composite 386/2373 vs 502/2371 to exact target HR 0.75 [0.65, 0.85], with endpoint counts 382/2373 vs 495/2371. EMPEROR-Reduced is exact target HR 0.75 [0.65, 0.86]. Pool is HR 0.75, common-effect CI 0.6808 to 0.8263; registered k=2 HKSJ CI is refused, with audit-only 0.4003 to 1.4052.
- `pcsk9-mace`: FOURIER uses exact 3-point target HR 0.80 [0.73, 0.88]; the broader 5-point primary remains visible as a different endpoint/measure in `cross_source`. ODYSSEY remains a near-match because no exact held source candidate exists.
- `ticagrelor-vs-clopidogrel-acs`: PLATO is exact 3-point MACE HR 0.84 [0.77, 0.92]; the k=2 pool remains refused for direction conflict with PHILO.
- `dapagliflozin-hfpef-hosp`: DELIVER row carries the multiple registered primary disclosure; sweep found 1 of 93 checked pooled rows with >1 registered primary in-family, this row.
- `noac-vs-warfarin-af-stroke`: protocol divergence renders `ESTIMAND_PREFERENCE_UNDECLARED`.

Replay outputs, MEASURED:

- `python scripts\reproduce_review.py sglt2-hfref-hosp-cvdeath` -> `1/1 reproduce (all reproducible)`.
- `python scripts\reproduce_review.py pcsk9-mace` -> `1/1 reproduce (all reproducible)`.
- `python scripts\reproduce_review.py ticagrelor-vs-clopidogrel-acs` -> `1/1 reproduce (all reproducible)`.
- `python scripts\reproduce_review.py dapagliflozin-hfpef-hosp` -> `1/1 reproduce (all reproducible)`.
- `python scripts\reproduce_review.py noac-vs-warfarin-af-stroke` -> `1/1 reproduce (all reproducible)`.

Corpus sweep, MEASURED: `near-match sweep: 0 NEAR_MATCH rows with an exact held target among 115 pooled rows; 2 protocols lack estimand preference among 32 topics; 1 pooled rows have >1 registered primary in-family`. The two protocol slugs are `noac-vs-warfarin-af-stroke` and `sglt2-hfref-hosp-cvdeath`.

## 4. Tests

MEASURED:

- `python -m pytest tests\test_target_endpoint.py -q` -> `6 passed in 3.90s`.
- `python -m pytest tests\test_cross_source_endpoint.py::test_rebuilt_fourier_row_is_different_measure_not_corroboration -q` -> `1 passed in 10.15s`.
- `python -m pytest tests\test_gate.py::test_real_review_reproduces_and_passes_full_gate -q` -> `1 passed in 30.05s`.
- `python scripts\near_match_sweep.py` -> sweep output quoted above.
- `python -m pytest tests -x -q` -> `722 passed in 955.31s (0:15:55)`.
- `git diff --check` -> no output.

## 5. Not Done

No commit, no staging, no push. No network. I did not edit `harness/synth.py`, K2 policy, screening, search, pool membership, or `protocols/pcsk9-mace.md`. I did not write ratchet acknowledgements; changed/reworded rendered blocks are the protocol target-endpoint selection row, trial Source-column selector disclosures, endpoint-count input text, and protocol divergence rendering on the rebuilt pages for the integrator to acknowledge if needed.

## 6. Files Changed Or Added

Added:

- `LANE-TE-REPORT.md`
- `docs/near_match_sweep.json`
- `harness/target_endpoint.py`
- `scripts/near_match_sweep.py`
- `tests/test_target_endpoint.py`

Modified:

- `docs/fix_ledger.json`
- `docs/index.html`
- `docs/m/m0c0e2bf1/index.html`
- `docs/m/m2da64325/index.html`
- `docs/m/m6dd4233b/index.html`
- `docs/m/m8db5253b/index.html`
- `docs/m/mf6cd36c2/index.html`
- `docs/reviews/dapagliflozin-hfpef-hosp/REPRODUCTION.json`
- `docs/reviews/dapagliflozin-hfpef-hosp/index.html`
- `docs/reviews/dapagliflozin-hfpef-hosp/manifest.json`
- `docs/reviews/dapagliflozin-hfpef-hosp/review.json`
- `docs/reviews/noac-vs-warfarin-af-stroke/REPRODUCTION.json`
- `docs/reviews/noac-vs-warfarin-af-stroke/index.html`
- `docs/reviews/noac-vs-warfarin-af-stroke/manifest.json`
- `docs/reviews/noac-vs-warfarin-af-stroke/review.json`
- `docs/reviews/pcsk9-mace/REPRODUCTION.json`
- `docs/reviews/pcsk9-mace/index.html`
- `docs/reviews/pcsk9-mace/manifest.json`
- `docs/reviews/pcsk9-mace/review.json`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/REPRODUCTION.json`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/index.html`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/manifest.json`
- `docs/reviews/sglt2-hfref-hosp-cvdeath/review.json`
- `docs/reviews/ticagrelor-vs-clopidogrel-acs/REPRODUCTION.json`
- `docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html`
- `docs/reviews/ticagrelor-vs-clopidogrel-acs/manifest.json`
- `docs/reviews/ticagrelor-vs-clopidogrel-acs/review.json`
- `harness/page.py`
- `harness/pipeline.py`
- `harness/protocol_compiler.py`
- `registry/blind_map.json`

Pre-existing untracked lane files left untouched: `LANE_PROMPT.md`, `lane.log`, `lane.pid`, `lane.winpid`.
