# LANE VS Report

## 1. What was wrong

The served `pcsk9-mace` page was built from title/name-seeded retrieval and omitted VESALIUS-CV (PMID 41211925), a published eligible evolocumab-vs-placebo trial. That left the primary pool at k=2 and the registered HKSJ interval refused under `K2_SINGLE_DF`, while the common-effect sensitivity still looked favorable.

Mechanism fixed:
- Added VESALIUS-CV, ODYSSEY LONG TERM, and GLAGOV as `EXTRA_PMIDS` records with `discovery_capable=false`; no search was rerun.
- Added the 2026-09-16 protocol amendment before extraction, including the co-primary endpoint rule and explicit disclosure that both VESALIUS co-primary results were known.
- Pooled VESALIUS using the published 3-point MACE HR 0.75 [0.65, 0.86], not crude RR from 336/6129 vs 443/6128.
- Kept ODYSSEY LONG TERM and GLAGOV P/I/C/design eligible but outcome-layer absent: `outcome_post_hoc_not_pooled` and `outcome_not_reported`.
- Added endpoint-component compatibility disclosure, strict 3-point strand, missing-effect classifier/sweep, and freshness artifacts required by the new pooled trial.

Static vs dynamic disclosure:

| Item | Static source | Dynamic computation |
| --- | --- | --- |
| Three new PubMed records | Verbatim in `LANE_PROMPT.md` | None |
| VESALIUS selected primary effect | Abstract HR 0.75 [0.65, 0.86] | Pooled by `harness.synth.pool` |
| VESALIUS count provenance | Abstract 336/6129 vs 443/6128 | Verify gate locates digits in committed span |
| Alternative VESALIUS co-primary | Abstract HR 0.81 [0.73, 0.89] | Sensitivity pool by `harness.synth.pool` |
| Missing-effect corpus sweep | `docs/known_eligible_missing.json` + cache overrides | `scripts/missing_effect_sweep.py` |

## 2. Plant

Test: `tests/test_missing_effect.py`

Plant assertions:
- `test_baseline_has_no_missing_effect_panel` loads `git show ad5e7c66e97cf0e328daf7b3e15e7e4d4dda3b1d:docs/reviews/pcsk9-mace/review.json` and asserts no `missing_evidence_effect` or `reverses_significance_to_effect` field exists pre-fix.
- `test_vesalius_missing_effect_reverses_pcsk9_baseline_to_effect` adds VESALIUS as known-missing HR 0.75 [0.65, 0.86] to the pre-fix object and asserts `reverses_significance_to_effect` and re-pooled k=3.
- Synthetic controls assert concordant significant missing evidence is directional, not reversal, and no extractable effect is `not_estimable`.

Measured output:

```text
python -m pytest tests/test_missing_effect.py -q
4 passed in 14.73s
```

## 3. Rebuilt Page Changes

Changed pages/artifacts:
- `docs/reviews/pcsk9-mace/index.html`
- `docs/m/mf6cd36c2/index.html`
- `docs/index.html`

Measured primary result before, from `ad5e7c66`:
- k=2; trials 28304224 and 30403574.
- Registered HKSJ CI refused: `K2_SINGLE_DF`.
- Quarantined HKSJ audit interval: HR 0.85 [0.5852, 1.2346].
- Common-effect sensitivity: HR 0.85 [0.8024, 0.9004].
- tau2=0, Q=0, I2=0.
- No declared-absent rows.
- STALE reason: `search_not_executed`.
- GRADE: moderate; imprecision had one conservative downgrade because k=2 registered CI was refused.

Measured primary result after rebuild:
- k=3; trials 28304224, 30403574, 41211925.
- HR 0.83 [0.7147, 0.9638], tau2=0.00124, Q=2.62684, I2=23.9.
- Prediction interval: 0.6708 to 1.0269.
- Claim now present/significant, direction benefit.
- Alternative VESALIUS 4-point co-primary sensitivity: k=3 HR 0.8397 [0.7528, 0.9367], tau2=0.
- Leave-one-out estimates: 0.8083 to 0.85; most influential drop 28304224.

Screening:
- Before: 9 records, 2 included trial families (`NCT01663402`, `NCT01764633`).
- After: 12 records, 5 included trial families (`NCT01507831`, `NCT01663402`, `NCT01764633`, `NCT01813422`, `NCT03872401`).
- The three new records all screen `INCLUDE` under P/I/C/design.

Declared absent after:
- ODYSSEY LONG TERM / PMID 25773378: `outcome_post_hoc_not_pooled`; reason: MACE effect explicitly post hoc.
- GLAGOV / PMID 27846344: `outcome_not_reported`; reason: abstract reports IVUS percent atheroma volume, no MACE effect.

Compatibility key after:
- Endpoint: `component-defined composite`.
- Component dimension heterogeneous:
  - 41211925: `CHD_DEATH | MI | ISCHEMIC_STROKE`
  - 30403574: `CHD_DEATH | MI | ISCHEMIC_STROKE | UA_HOSP`
  - 28304224: `CV_DEATH | MI | STROKE | UA_HOSP | CORONARY_REVASCULARIZATION`
- Randomised contrast: 2 of 3 registry-confirmed; VESALIUS is explicit but not registry-confirmed in local AACT.

Strict 3-point strand:
- FOURIER key secondary + VESALIUS 3-point co-primary.
- k=2 HR 0.7842428728642973 [0.4738544913365308, 1.2979446114432796], tau2=0.
- Common-effect sensitivity: HR 0.7842428728642973 [0.7256033356925063, 0.8476213564418956].
- ODYSSEY OUTCOMES is declared absent from the strand as `not_in_abstract_in_full_text`.

GRADE after:
- Overall certainty: moderate.
- Risk of bias: not downgraded; 3 of 3 assessed, none high or some concerns. VESALIUS uses abstract-corrected randomisation/blinding/selective-reporting domains; missing outcome data remains not assessed.
- Inconsistency: not downgraded; `tau2=0.00124; prediction interval not markedly wider than the CI`.
- Imprecision: not downgraded; `95% CI [0.7147, 0.9638]; excludes the null with a reasonably tight interval -> precise`.
- Publication bias: not assessed, broad contaminated registry denominator.
- Indirectness: human judgement.
- Certainty remains capped below high because all D3 missing-outcome-data domains are unassessed.

STALE:
- Page remains STALE.
- Reasons after rebuild: `search_not_executed`; `eligible_declared_absent` for `NCT01507831` and `NCT01813422`.

Missing-effect sweep:

```text
python scripts/missing_effect_sweep.py
missing-effect sweep: 32 pages, 15 entries, 0 with source-verified effects, 0 pages with reversal classes
```

The corpus sweep has 0 verifiable-effect entries because the committed `known_eligible_missing` rows do not carry identifiers matching source-verified effect overrides. The PCSK9 plant demonstrates the reversal class on the pre-fix object.

Blocks changed/reworded requiring integrator ratchet judgement:
- PCSK9 primary result block: k=2 `K2_SINGLE_DF` refusal/sensitivity wording replaced by k=3 registered HR result.
- PCSK9 GRADE imprecision wording changed from k=2 conservative downgrade to precise k=3 CI.
- PCSK9 screening flow changed from 2 to 5 eligible trial families.
- PCSK9 declared-absent table gained ODYSSEY LONG TERM and GLAGOV.
- PCSK9 compatibility key gained component enumerations.

## 4. Tests

Build:

```text
python scripts/build_topic.py pcsk9-mace --now 2026-09-11
protocol_sha=38478f5e060a9d63bcb073cb652d0e6f70d27c58
PRIMARY: Major adverse cardiovascular events  k=3  RR=0.83 (0.7147-0.9638)  tau2=0.00124
included trials: ['28304224', '30403574', '41211925']
declared-absent trials: ['25773378', '27846344']
comparator OA=True k=12
canonical: docs/reviews/pcsk9-mace/index.html
blind: docs/m/mf6cd36c2/  docs/m/mf6f36ebe/
```

Replay:

```text
python scripts/reproduce_review.py
32/32 reproduce (all reproducible)
```

Full test suite:

```text
python -m pytest tests -q
720 passed in 779.00s (0:12:59)
```

Also run:
- `python -m py_compile harness/missing_effect.py harness/pipeline.py harness/invalidation.py harness/absence.py harness/compat.py harness/page.py scripts/missing_effect_sweep.py tests/test_missing_effect.py`
- `python -m pytest tests/test_missing_effect.py -q`
- focused freshness tests after artifact updates: 9 passed in 409.16s; final RoB/fixstate focus: 2 passed in 336.94s.

## 5. Not Done

- No network fetches or live searches were run. VESALIUS, ODYSSEY LONG TERM, and GLAGOV use only the inlined PubMed records from `LANE_PROMPT.md`.
- No commits were made.
- No ratchet acknowledgements were written; changed/reworded blocks are listed above for the integrator.
- I did not rebuild unrelated review pages. I did patch `scripts/reproduce_review.py` so replay uses each page's committed manifest `protocol_sha`; this made the existing spironolactone manifest pin replayable without changing that unrelated page.

## 6. Files Changed or Added

Changed:
- `cache/pcsk9-mace/arm_contrast.json`
- `cache/pcsk9-mace/integrity.json`
- `cache/pcsk9-mace/records.json`
- `cache/pcsk9-mace/retrieval_ledger.json`
- `cache/pcsk9-mace/rob2.json`
- `docs/error_rate.json`
- `docs/error_rate_sample.json`
- `docs/evidence/override-audit-2026-09-14/overrides.json`
- `docs/fix_ledger.json`
- `docs/index.html`
- `docs/m/mf6cd36c2/index.html`
- `docs/reviews/pcsk9-mace/REPRODUCTION.json`
- `docs/reviews/pcsk9-mace/index.html`
- `docs/reviews/pcsk9-mace/manifest.json`
- `docs/reviews/pcsk9-mace/review.json`
- `harness/absence.py`
- `harness/compat.py`
- `harness/invalidation.py`
- `harness/page.py`
- `harness/pipeline.py`
- `protocols/pcsk9-mace.md`
- `registry/blind_map.json`
- `scripts/reproduce_review.py`
- `topics/pcsk9-mace.json`

Added:
- `cache/pcsk9-mace/verified_arms.json`
- `cache/pcsk9-mace/verified_effects.json`
- `docs/missing_effect_sweep.json`
- `docs/pcsk9_mace_strands.json`
- `harness/missing_effect.py`
- `scripts/missing_effect_sweep.py`
- `tests/test_missing_effect.py`
- `LANE-VS-REPORT.md`

Pre-existing untracked lane inputs left uncommitted/unchanged: `LANE_PROMPT.md`, `lane.log`, `lane.pid`, `lane.winpid`.
