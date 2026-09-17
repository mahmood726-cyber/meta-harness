# LANE XS2 — a second-source "corroboration" is meaningless until OUTCOME IDENTITY is verified; magnitude agreement on a different endpoint manufactures false confidence. Sweep every cross-source row in the corpus.

Report file: `LANE-XS2-REPORT.md`. Base `ad5e7c66`. Start from lane XS (`LANE-XS-REPORT.md`, `harness/ctgov_results.py` endpoint match) — extend it, do not fork.

## Findings (topic 15 `pcsk9-mace`, served hash `1a477e05fe47692e`; CLAIMED until re-measured; note the integrated tree already differs from the served page — measure BOTH `git show aa8ed28a:docs/reviews/pcsk9-mace/review.json` and `ad5e7c66:...` and say which you quote)
- FOURIER: served "source HR 0.85; CT.gov RR 0.666 — corroboration". FOURIER's primary counts are 1344 vs 1563 (~9.8% vs 11.3%), crude RR ≈0.86. 0.666 cannot be that endpoint. The integrated tree shows `ctgov_rr 0.881` from KM_ESTIMATE 2.74 vs 3.11 on the 5-component primary — a Kaplan–Meier estimate ratio, which is not a risk ratio either.
- ODYSSEY OUTCOMES: served CT.gov RR 0.818 against primary counts 903/9462 vs 1052/9462, crude RR ≈0.858; integrated tree 0.856 from PERCENTAGE 9.5 vs 11.1 (a ratio of percentages).
- Rule: **outcome identity before magnitude**. A cross-source value may be labelled corroboration only when (a) the registry outcome's title AND component set match the pooled outcome (XS's matcher, extended to components and measure type), (b) the measure types are commensurable (a KM estimate ratio or percentage ratio is NOT a risk ratio; label it by what it is), (c) the analysis population matches (denominators vs randomised). Otherwise it renders as `SECOND_SOURCE_DIFFERENT_ENDPOINT` / `SECOND_SOURCE_DIFFERENT_MEASURE` / `SECOND_SOURCE_DIFFERENT_POPULATION` with both values shown and NO agreement word.

## Build
1. Extend `harness/ctgov_results.py` (or `harness/second_source.py`): typed `identity = {title_match, component_match, measure_type, population_match, verdict}` per cross-source row; agreement statistics computed only on `verdict == IDENTICAL_ENDPOINT`.
2. Plants (pre-fix on `aa8ed28a` AND `ad5e7c66` objects): `tests/test_second_source_identity.py` — FOURIER and ODYSSEY rows carry "corroboration" pre-fix with unverified identity; post-fix FOURIER = `DIFFERENT_MEASURE` (KM estimate ratio ≠ RR) and the served 0.666 provenance is named if it can be located in cache (if not: `VALUE_NOT_REPRODUCIBLE_FROM_CACHE`, a finding in itself); ODYSSEY = `percentage ratio` labelled as such. Synthetic control: a CT.gov row with identical title, components, RR from counts → `IDENTICAL_ENDPOINT`, corroboration allowed.
3. Corpus sweep `scripts/second_source_sweep.py` → `docs/second_source_sweep.json`: every `cross_source` row on 32 pages: `n rows labelled corroboration whose endpoint identity is unverified or wrong of N cross-source rows`, N named; by verdict class; by page.
4. Rebuild affected pages (expect many: every page with `cross_source`); replay; list reworded blocks.

Do not touch: pooling, membership, screening, search, `harness/synth.py`. No network.
