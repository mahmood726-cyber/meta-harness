# LANE TC — trial-conduct flags for human adjudication: early termination, run-in enrichment, functional unblinding, post-randomisation exclusions, baseline imbalance noted by the investigators. The machine names them; it does not rate them.

Report file: `LANE-TC-REPORT.md`. Base `ad5e7c66`. Lane D5 (running) owns the RoB domain rules and the `partial machine assessment` relabel; you own a separate, additive `conduct_flags` object per trial (`harness/conduct_flags.py`), rendered in the RoB tab as "flags for human adjudication", never folded into a domain rating.

## Named instances (CLAIMED until located in cached abstracts / registry records)
- dpp4-mace-t2d: omarigliptin CVOT (OMNEON) terminated early for commercial reasons → `EARLY_TERMINATION(reason: sponsor decision)`.
- sglt2-hfref / sglt2-pp: run-in enrichment (active or placebo run-in with exclusion of non-tolerant/non-adherent) where the abstract/registry states it → `RUN_IN_ENRICHMENT`.
- esketamine-trd-madrs: functional unblinding (dissociation/sedation) — the human RoB2 in the 2026 comparator rated "some concerns" on this basis → `FUNCTIONAL_UNBLINDING_RISK(basis: intervention with perceptible acute effects)`, flagged for every trial whose intervention class has this property, with the basis sentence.
- spironolactone: J-EMPHASIS investigators noted an unexpectedly low placebo death rate, chance baseline imbalances, most eplerenone-arm deaths >30 days after discontinuation → `INVESTIGATOR_NOTED_IMBALANCE`, `OFF_TREATMENT_EVENTS` (only if the sentences are in held text).
- finerenone: FIDELIO analysed 5,674 of 5,734 (60 excluded for GCP violations), FIGARO 7,352 of 7,437 → `POST_RANDOMISATION_EXCLUSION(n_excluded, reason)`; colchicine-postop 2026 CABG trial 163 of 172; COCS 240 of 267.
- iv-iron / others: any trial whose registry status is "Terminated" with results.

## Build
1. `harness/conduct_flags.py`: per pooled trial, scan held abstract/full text and the cached registry record for the flag vocabulary; every flag carries `basis_span` and `source_id`; absence of a sentence → no flag (never "no concerns"). `NOT_ASSESSABLE_FROM_HELD_TEXT` when no source is held.
2. Render: RoB tab section "Trial-conduct flags (for human adjudication; not a domain rating)"; GRADE untouched.
3. Plants (pre-fix `ad5e7c66`): `tests/test_conduct_flags.py` — no `conduct_flags` field pre-fix on any page (assert); post-fix OMNEON `EARLY_TERMINATION` if the sentence is held (else `in_source_not_held` with the publication named); FIDELIO `POST_RANDOMISATION_EXCLUSION(60)` from the abstract if held; synthetic abstract with "terminated early" → flag; synthetic with none → no flag and no "no concerns" text.
4. Sweep `scripts/conduct_flags_sweep.py` → `docs/conduct_flags_sweep.json`: `n pooled trials with ≥1 flag of N pooled trials` by flag type; `n flags with a held span of N flags`; pages by count.
5. Rebuild affected pages; replay; list reworded blocks.

Do not touch: RoB domain ratings, GRADE, pooling, membership, screening. No network.

## Added 2026-09-16 13:58 (topic 18)
- PLUS analysed 4,846 of 5,037 randomised; BaSICS 10,520 of 11,052, excluding 486 consent refusals and 46 duplicates — a **legally mandated** post-randomisation exclusion (deferred consent) deserves its own label `POST_RANDOMISATION_EXCLUSION(kind=consent_withdrawal_mandated)` distinct from investigator-chosen exclusions. Seventh ITT-overstated instance; the analysis-set label is EN's `AVAILABLE_CASE`/`MODIFIED_ITT`, your flag names the cause.
