# LANE CP — comparator-parity labels must be derived from the trial-set RELATION, and an identical trial set is arithmetic replication, not corroboration

Report file: `LANE-CP-REPORT.md`.

## The failures (external audit of all 22 pooled pages, 2026-09-16; each confirmed on served bytes at aa8ed28a)

- `pcsk9-mace`: parity status "PARITY-effective" for ours k=2 vs comparator k=12 (FOURIER+ODYSSEY ≈ 87% of their patients). That relation is a DOMINANT-TRIAL SUBSET, not parity.
- `ticagrelor-vs-clopidogrel-acs`: "PARITY … 1 valid RCT (PLATO) = ours" while our pool is k=2 (PLATO + PHILO). That is a SUPERSET of the valid comparator set, and the sentence is also stale (it predates PHILO).
- `statins-primary-prevention-elderly`: the comparator card says "✓ same question" (scope match) and the parity row concludes "COMPARATOR-INVALID: pools 12 OBSERVATIONAL studies, 0 RCTs". The first label must be invalidated by the second, not sit beside it.
- `probiotics-aad-prevention`: the comparator `scope` metadata treats the topic as effectively a single agent; probiotics are heterogeneous strains/formulations, and that metadata feeds the parity/scope-match logic.
- Trial-set-overlap rule: where agreement rests on the same trial set — `noac-vs-warfarin-af-stroke` (4 = their comparable 4), `finerenone-ckd-t2d-renal` (FIDELIO+FIGARO = their pool), `sglt2-hfref-hosp-cvdeath` (DAPA-HF+EMPEROR-Reduced = their LVEF≤40 pool) — the "agrees with the published comparator" rendering is ARITHMETIC REPLICATION and must not read as independent corroboration.

Where the objects live: `docs/parity.json` (hand rows: `status`, `reason`, `our_k`, `comparable_comparator_k`), read by `harness/census.py::_parity_row` and rendered on the Reproduction tab; `review["comparator"]["overlap"]` (`ours_k`, `theirs_k`, `shared_k`, `only_ours`, `only_theirs`, `method`) and `review["comparator"]["scope"]` (`topic_is_class`, `comparator_is_class`, `scope_valid`, `note`) built in `harness/pipeline.py::build_comparator_core` / the comparator matcher; `docs/external_agreement.json` built by `scripts/external_agreement.py`; `harness/page.py` comparator tab. Read `AUDIT_QUEUE.md` items 8 and 10 first (the comparator matcher and k-vs-estimate coherence are known-open).

## What to build

1. A typed `parity_relation` computed — not typed by hand — from the numbers the page already holds: inputs `ours_k`, `comparable_comparator_k` (or `theirs_k`), the named shared/only-ours/only-theirs sets where present, and `comparator_valid` (RCT-meta or not). Vocabulary: `IDENTICAL_SET` (ours == comparable theirs → label "arithmetic replication — same trials; agreement is not independent corroboration"), `DOMINANT_SUBSET` (ours ⊂ theirs, ours carries ≥ x% of their patients or events — state x and its source), `SUBSET`, `SUPERSET` (theirs ⊂ ours), `OVERLAPPING` (neither contains the other), `DISTINCT`, `COMPARATOR_INVALID` (not an RCT meta / not the same question), `NOT_ENUMERABLE` (comparator trial list not exposed and no k). Rule: when `shared_k` is "not exactly verifiable", the relation is INFERRED from k's and dates and must render with that word. Keep the hand `reason` text as commentary, but the STATUS word on the page comes from the computed relation, and a hand status that disagrees with the computed relation is a gate refusal (so the ticagrelor "PARITY" row cannot render beside k=2).
2. "Same question" scope label: `scope_valid` must be false when the parity row / comparator object records the comparator as invalid (observational-only, wrong design); one object, one verdict. Statins must render "comparator invalid — not an RCT meta" everywhere it previously said "same question".
3. `docs/external_agreement.json` and its rendering: an `IDENTICAL_SET` relation renders as replication; the "agrees" wording is reserved for `OVERLAPPING`/`DISTINCT`/`SUBSET` with a different evidence base. Confirm what `scripts/external_agreement.py` does today and change it accordingly (it already suppresses cross-estimand "agrees" — extend the same idea to same-set).
4. Probiotics: correct the comparator `scope` metadata so `topic_is_class` reflects heterogeneous strains/formulations; report what changed in the scope-match output.
5. Corpus-wide sweep `scripts/parity_relation_sweep.py` → `docs/parity_relation_sweep.json`: for all 32 topics, hand status vs computed relation; table in the report with `n disagreements of N` (N = topics with a parity row + topics without one, both named).
6. Rebuild affected pages; `reproduce_review.py` each; quote before/after status words on pcsk9, ticagrelor, statins, probiotics, noac, finerenone, sglt2-hfref.

## Plants (must fire pre-fix)

`tests/test_parity_relation.py` on pre-fix fixture copies of the four pages' `review.json` + the pre-fix `docs/parity.json`: pcsk9 hand "PARITY-effective" vs computed `DOMINANT_SUBSET` → disagreement fires; ticagrelor hand "PARITY" vs computed `SUPERSET` fires; statins `scope_valid=True` while parity says COMPARATOR-INVALID → fires; noac/finerenone/sglt2-hfref computed `IDENTICAL_SET` → the external-agreement rendering pre-fix says "agrees" (quote it) → post-fix says replication. Synthetic controls for each vocabulary term. Quote outputs.

Do not touch: pooling, `harness/synth.py`, `harness/rob_sensitivity.py`, `harness/grade.py`, `harness/estmeasure.py`, which trials are pooled, search code. Do not rewrite the hand `reason` prose — leave it as commentary; the integrator decides wording.
