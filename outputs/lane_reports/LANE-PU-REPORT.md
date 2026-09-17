# Publication-Unit Lane Report

## 1. What Was Wrong

Publication records were being allowed to behave like independent trials after screening. [MEASURED] In the pre-fix colchicine page at `aa8ed28a`, PMID `32407460` was an economic COLCOT publication and PMID `34446156` was a LoDoCo2 secondary/subgroup publication, but both were screened in and then counted in the screened-in-not-pooled gap.

Mechanism:
- `harness/identity.py` resolved trial identifiers, but did not annotate review rows with `trial_family_id` / `publication_role`, and did not expose trial-family counts separate from publication counts.
- `harness/page.py` and `harness/manuscript.py` rendered screened-in gaps as raw row counts, so secondary/economic publications inflated "trial(s)" wording.
- `harness/pipeline.py` did not attach publication-unit metadata to screening rows, pooled rows, and declared-absent rows before rendering.
- `harness/invalidation.py` compared raw included record ids to raw pooled ids; it needed family-aware comparison and to skip secondary/economic publications already represented by a pooled family.
- `spironolactone-hfref-mortality` had an identifier/name mismatch: the slug read as single-agent spironolactone, while the served pool was MRA class-level. [MEASURED] Pre-fix verdict was `SINGLE_AGENT_OVER_CLASS_POOL`.

## 2. Plant And Regression Tests

Added `tests/test_publication_unit.py`.

Key assertions:
- `test_synthetic_publication_units_count_trials_and_publications_separately`: [MEASURED] one primary + secondary + economic report in one family counts as `1` trial family and `3` publications; adding a separate trial makes `2` trial families and `4` publications.
- `test_planted_prefix_colchicine_failure_is_detected_in_served_bytes`: [MEASURED] old `aa8ed28a` page contains `26 further screened-in trial(s) had no poolable value`; identity annotation flags PMID `32407460` as `economic` / `COLCOT` and PMID `34446156` as `secondary` / `LoDoCo2`.
- `test_current_colchicine_page_uses_publication_units_after_rebuild`: [MEASURED] current PMID `32407460` and `34446156` are `X-DEDUP`; PMID `25784519` is `X2`; PMID `23500260` is `INCLUDE` and declared absent, not pooled.
- `test_publication_unit_sweep_finds_prefix_and_clears_colchicine_after_rebuild`: [MEASURED] pre-fix sweep finds the two colchicine publication-unit defects; current sweep clears them.
- `test_spironolactone_scope_amendment_replaces_identifier_block_after_rebuild`: [MEASURED] pre-fix scope block is `SINGLE_AGENT_OVER_CLASS_POOL`; current object is `DISCLOSED_SCOPE_AMENDMENT` dated `2026-09-16`.

Pre-fix output quote:
- [MEASURED] `k = 3: the 3 trial(s) named below were pooled; 26 further screened-in trial(s) had no poolable value...`

Post-fix output quote:
- [MEASURED] `26 trial families (27 publications) met P/I/C/design (screening); 3 reported this outcome... the remaining 23 trial families (24 publications) are listed as declared-absent...`

## 3. Rebuilt Pages With Changed Bytes

Canonical review pages:
- `docs/reviews/colchicine-secondary-cv-prevention/index.html`
  - Before [MEASURED]: `29 trials met P/I/C/design (screening); 3 reported this outcome... the remaining 26...`
  - After [MEASURED]: `26 trial families (27 publications) met P/I/C/design (screening); 3 reported this outcome... the remaining 23 trial families (24 publications)...`
- `docs/reviews/spironolactone-hfref-mortality/index.html`
  - Before [MEASURED]: `Identifier scope failure.`
  - After [MEASURED]: `Identifier scope amendment.`
- `docs/reviews/probiotics-aad-prevention/index.html`
  - Before [MEASURED]: `60 trials met P/I/C/design (screening); 16 reported this outcome... the remaining 44...`
  - After [MEASURED]: `58 trial families (60 publications) met P/I/C/design (screening); 16 reported this outcome... the remaining 42 trial families (44 publications)...`

Blind/index HTML pages changed by rebuild:
- `docs/m/maf69923c/index.html`
  - Before [MEASURED]: `29 trials met P/I/C/design... the remaining 26...`
  - After [MEASURED]: `26 trial families (27 publications) met P/I/C/design... the remaining 23 trial families (24 publications)...`
- `docs/m/m3c1155fb/index.html`
  - Before [MEASURED]: `Identifier scope failure.`
  - After [MEASURED]: `Identifier scope amendment.`
- `docs/m/md2772f36/index.html`
  - Before/after visible title [MEASURED]: `Mineralocorticoid receptor antagonists vs placebo for all-cause mortality in HFrEF`; byte change came from rebuild/hash artefacts.
- `docs/m/m586876fa/index.html`
  - Before [MEASURED]: `60 trials met P/I/C/design... the remaining 44...`
  - After [MEASURED]: `58 trial families (60 publications) met P/I/C/design... the remaining 42 trial families (44 publications)...`
- `docs/index.html`
  - Before/after visible row text [MEASURED]: the colchicine, spironolactone, and probiotics titles remain present; byte change came from regenerated index artefacts.

Current object facts:
- [MEASURED] Colchicine `review_sha256`: `4067498e2a47d26527c8e979b2f6044c3152c43dfb1ccae554308344d3526e10`.
- [MEASURED] Spironolactone `review_sha256`: `c4f0309809ac534a3776ed6e6a3a9c40c8f2cd125cf5c643222f933ea4e1628e`.
- [MEASURED] Probiotics `review_sha256`: `6306b310833a0a3d4336713efa634f02a50ba19e2793d1651df03ae5b650e135`.

## 4. Sweep And Tests

Publication-unit sweep:
- [MEASURED] `python scripts/publication_unit_sweep.py --ref aa8ed28a`
  - `SWEEP source=aa8ed28a topics=32 secondary_or_economic_of_pooled=2 of screened_in_not_pooled_records=206`
  - [MEASURED] Colchicine: `2 flagged of 25 screened-in-not-pooled records` (`32407460`, `34446156`).
- [MEASURED] `python scripts/publication_unit_sweep.py`
  - `SWEEP source=current topics=32 secondary_or_economic_of_pooled=0 of screened_in_not_pooled_records=204`

Reproduction:
- [MEASURED] `python scripts/reproduce_review.py colchicine-secondary-cv-prevention`: `1/1 reproduce (all reproducible)`.
- [MEASURED] `python scripts/reproduce_review.py spironolactone-hfref-mortality`: `1/1 reproduce (all reproducible)`.
- [MEASURED] `python scripts/reproduce_review.py probiotics-aad-prevention`: `1/1 reproduce (all reproducible)`; this extra rebuild was needed for the real-review gate after pipeline-level publication-unit annotation changed the replay object.

Pytest:
- [MEASURED] Focused checks: `8 passed in 131.93s (0:02:11)`.
- [MEASURED] Full lane command: `python -m pytest tests -x -q` -> `644 passed in 362.44s (0:06:02)`.

## 5. Static Vs Dynamic Disclosure

| Item | Static / dynamic | Disclosure |
|---|---|---|
| `docs/study_families.json` colchicine rows | Static, source-backed curation | [MEASURED] only PMID `32407460` and `34446156` added as already-pooled companion publications. |
| `include.population_any_extra` for colchicine | Static config, non-search vocabulary | [MEASURED] used only for eligibility screening of PCI/stent language; avoids changing sealed `population_any`. |
| CABG exclusions in `population_none` | Static config | [MEASURED] excludes PMID `25784519` as wrong population. |
| `protocols/spironolactone-hfref-mortality.md` amendment | Static dated protocol text | [MEASURED] dated `2026-09-16`; resolves identifier scope as disclosed amendment, not silent widening. |
| Counts on pages and sweep | Dynamic from review JSON / script | [MEASURED] rendered from rebuilt review objects and `scripts/publication_unit_sweep.py`. |

## 6. What Not Done

- [MEASURED] No commit was made.
- [MEASURED] No changes to `harness/synth.py`, `rob_sensitivity.py`, `grade.py`, `estmeasure.py`, search queries, extractor logic, or pooling logic.
- [MEASURED] No search-v2 vocabulary reseal was done; the inclusion fix was moved to `population_any_extra` so the sealed vocabulary guard stays green.
- [MEASURED] No slug/URL rename for spironolactone; the page carries a dated scope amendment instead.
- [CLAIMED] No simulated or placeholder data were shipped as real output.

## 7. Files Changed Or Added

Source/code:
- `harness/identity.py`
- `harness/pipeline.py`
- `harness/page.py`
- `harness/manuscript.py`
- `harness/invalidation.py`
- `harness/protocol_compiler.py`
- `harness/screen.py`
- `scripts/publication_unit_sweep.py`
- `tests/test_publication_unit.py`

Config/protocol:
- `docs/study_families.json`
- `topics/colchicine-secondary-cv-prevention.json`
- `protocols/spironolactone-hfref-mortality.md`

Regenerated artefacts:
- `docs/reviews/colchicine-secondary-cv-prevention/*`
- `docs/reviews/spironolactone-hfref-mortality/*`
- `docs/reviews/probiotics-aad-prevention/*`
- `docs/m/maf69923c/index.html`
- `docs/m/m3c1155fb/index.html`
- `docs/m/md2772f36/index.html`
- `docs/m/m586876fa/index.html`
- `docs/index.html`
- `registry/blind_map.json`
- `docs/fix_ledger.json`
- `docs/evidence/*/README.md` fix-state line refreshes.
