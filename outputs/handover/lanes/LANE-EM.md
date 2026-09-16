# LANE EM — esketamine-trd-madrs: three consumers on three different membership states; reconcile every consumer to ONE membership object

Report file: `LANE-EM-REPORT.md`.

## The failure (MEASURED on committed objects at aa8ed28a)

Primary outcome `Change in MADRS`, k=4. Pooled rows: `PMID 37025256` (label `37025256`), `PMID 31109201` (label `31109201`), `NCT02422186` (label `TRANSFORM-3`), `NCT02417064` (label `TRANSFORM-1`) — the last two are CT.gov-results-only rows (no PMID). Three consumers disagree about who is pooled:

1. **Trial-integrity block** (`review["integrity"]`, built in the pipeline from PubMed efetch): `n_pooled: 2`; the page says "none of the 2 trials pooled across all outcomes on this page is retracted". It counts PMIDs only — NCT-only pooled rows are invisible to it. Two pooled trials were never integrity-checked and the sentence says 2 where the pool says 4.
2. **RoB sensitivity** (`review["rob_sensitivity"]`): `rob2.trials` is keyed `37025256, 31109201, NCT02422186, NCT02417064` (4 rows, all rated); `levels` is keyed by `label` → `TRANSFORM-3: None, TRANSFORM-1: None`; `n_rob_rated 2`; the page renders "2 of 4 pooled trials" in the compatibility key's randomised-contrast line and the sensitivity block. Same label-vs-id join defect another lane (CG) is fixing generically — you must still plant it here and make THIS page's consumers read one membership object.
3. **Comparator-parity narrative** (`docs/parity.json` row, rendered on the Reproduction tab): "We pool 2 (TRANSFORM-2 flexible-dose, TRANSFORM-3 elderly). The 2 gap trials (TRANSFORM-1 and the phase-2 dose-finding) are 3-arm FIXED-DOSE designs: our multi-arm continuous guard refuses per-arm extraction …" — while TRANSFORM-1 (NCT02417064) IS in the current primary pool, with per-arm mean/SD n=209 vs 108.

`Claims checked: 1; contradictions caught: 0`.

## What to build

1. One `membership` object per outcome on the review: `{"pooled": [trial_key...], "declared_absent": [...], "refused": [...], "screened_in_not_pooled": [...], "input_set_version": sha256(...)}` where `trial_key` is the identifier in `trial["id"]` (PMID or NCT), never `label`. Build it in `harness/pipeline.py` next to the outcome result. (Lane CG is building a general claim graph with the same key — name yours `membership` and keep it small; the integrator will merge.)
2. Make the three consumers read it: `integrity` must cover NCT-only rows (CT.gov has no retraction notice mechanism; record `integrity_source: "ctgov_results_only — retraction not checkable via PubMed"` for those rows and count them in `n_pooled` with that state, so the sentence reads "4 trials pooled; 2 checked via PubMed, 2 not checkable (registry-only rows)"); `rob_sensitivity`/compat-key randomised-contrast line join by `trial_key`; the parity row is a hand object — it cannot be made true by code, so mark it `STALE_VS_MEMBERSHIP` (it names TRANSFORM-1 as refused while membership pools it) and make it UNRENDERABLE (a fixed block naming the conflict, no prose from the stale row) rather than rewriting its text. Report the exact sentence that went dark.
3. Check the multi-arm question the parity text raises, without changing the pool: how were TRANSFORM-1's arms combined to n=209 vs 108 (two esketamine fixed-dose arms pooled against placebo?) — read the CT.gov results in `cache/esketamine-trd-madrs/` and state what the row's `source`/`derivation` says; if the combination is not disclosed on the page, add the disclosure to the row (`arm_combination: "56 mg + 84 mg arms combined; method: …"`) from what the cache shows, or state that it cannot be determined from committed sources. Do NOT drop or alter the row.
4. Sweep all 32 topics for the same three-consumer disagreement: `scripts/membership_consistency_sweep.py` → `docs/membership_consistency_sweep.json`, table: slug, outcome, pooled k, integrity n_pooled, rob levels rated, parity-text k, verdict; `n topics disagreeing of 32`.
5. Rebuild esketamine (and any other page the sweep flags and your change affects); `reproduce_review.py` each; quote before/after of the three sentences.

## Plants (must fire pre-fix)

`tests/test_membership_consistency.py`: pre-fix fixture copy of `docs/reviews/esketamine-trd-madrs/review.json` + the pre-fix `docs/parity.json` row → your consistency check returns three violations: `INTEGRITY_COUNT_MISMATCH (2 vs 4)`, `ROB_JOIN_MISS (2 rated-and-pooled trials invisible to levels)`, `PARITY_TEXT_STALE (names a pooled trial as refused)`; quote the output. Post-fix rebuilt object → 0 violations, and the parity row is rendered as the fixed STALE block. Synthetic control: a review where all three agree → 0.

Do not touch: pooling arithmetic, `harness/synth.py`, `harness/grade.py`, `harness/estmeasure.py`, search code, which trials are pooled. Do not rewrite the parity row's prose.
