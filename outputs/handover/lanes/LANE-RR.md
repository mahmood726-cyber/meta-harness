# LANE RR — refusal reasons must be true of the cached source: sweep every declared-absent / refusal row against the committed source

Report file: `LANE-RR-REPORT.md`.

## The failure

`iv-iron-hfref-hosp`, primary outcome (Heart-failure hospitalization, estimand RR / first-event): AFFIRM-AHF (PMID 33197395) is declared absent with `reason: "no percentage-corroborated arm counts or effect+CI for this outcome found in the abstract"`, `state: SOURCE_NOT_RETRIEVED`, `state_basis: "only the abstract was retrieved and it does not report this outcome"`. The cached abstract (`cache/iv-iron-hfref-hosp/records.json`, record id 33197395) contains: "217 total heart failure hospitalisations occurred in the ferric carboxymaltose group and 294 occurred in the placebo group (RR 0·74; 95% CI 0·58–0·94, p=0·013)". The abstract DOES report the outcome — as a recurrent-event rate ratio, whose estimand class (RATE) is incompatible with the outcome's FIRST_EVENT_RATIO class. The correct refusal is `ESTIMAND_CLASS_MISMATCH` (which `docs/iv_iron_strands.json` strand B already applies by USING that number). The mid-dot decimal is already normalised by `harness/extract.py:38-39`, so this is not a parse miss: the reason text and the state are generic fallbacks emitted when the extractor found nothing it could pool, regardless of WHY.

This is the family `AUDIT_QUEUE.md` item 6 names ("a guard may cite itself only if its precondition is true of the record"). Same page: 36347265 (IRONMAN) and 37632463 (HEART-FID) carry the same `SOURCE_NOT_RETRIEVED` text while the strands object and the parity text use their numbers.

## What to build

1. Find where declared-absent rows get `reason` / `state` / `state_basis` (`harness/pipeline.py`; grep `machine_absent`, `SOURCE_NOT_RETRIEVED`, `no percentage-corroborated`). Make the absence reason a typed outcome of what the extractor actually saw, with at least these codes: `OUTCOME_NOT_IN_SOURCE` (no sentence about the outcome), `EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH` (an effect+CI for the outcome exists but its class ≠ the outcome's class; record the value, its class and the verbatim span), `COUNTS_PRESENT_NOT_CORROBORATED` (arm counts found but percentage check failed; record them), `MULTI_ARM_UNRESOLVED`, `TIMEPOINT_MISMATCH`, `POPULATION_MISMATCH`, `SOURCE_NOT_RETRIEVED` (ONLY when the abstract itself is missing from cache). `state_basis` must quote the span it rests on. Keep the ontology names already in the codebase where they exist (`tests/test_absence_ontology.py`, `DECLARED_ABSENT_INVENTORY.md`) — extend, don't fork.
2. **Corpus-wide sweep** `scripts/refusal_reason_sweep.py`: for all 32 topics, for every declared-absent / refused / estimand-excluded row on every outcome, re-read the committed source and classify whether the stated reason is TRUE of it. Output `docs/refusal_reason_sweep.json` and a table in the report: slug, outcome, trial_key, stated reason/state, what the source actually contains (verbatim span ≤200 chars), verdict TRUE / FALSE / NOT_CHECKABLE, corrected code. Report `n FALSE of N rows over 32 topics`, N derived from the committed review.json files, not from your loop.
3. Apply the corrected reasons in the build, rebuild affected pages, `reproduce_review.py` each. Do NOT pool anything new — a corrected reason never turns into a pooled row in this lane.

## Plant (must fire pre-fix)

`tests/test_refusal_reason_truth.py`: load the pre-fix `docs/reviews/iv-iron-hfref-hosp/review.json` (fixture copy) and the cached AFFIRM-AHF record; assert the sweep's classifier returns FALSE for the 33197395 row with the RR 0·74 span quoted; assert the corrected code is `EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH`. Synthetic controls: a record with no outcome sentence → `OUTCOME_NOT_IN_SOURCE` is TRUE; a record whose abstract is absent from cache → `SOURCE_NOT_RETRIEVED` is TRUE. Quote outputs pre- and post-fix.

Do not touch: `harness/extract.py` parsing (you classify what it returns; you may add a function that reports the candidates it found), `harness/synth.py`, `harness/page.py` beyond rendering the new reason code + span in the declared-absent table, search code, `docs/refusals.json`.
