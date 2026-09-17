# LANE SH — source hierarchy: a published effect on the target estimand beats a crude effect reconstructed from arm counts

Report file: `LANE-SH-REPORT.md`.

## The failure

`spironolactone-hfref-mortality`: J-EMPHASIS-HF (PMID 28824029) row is `derivation: reconstructed`, crude RR 1.685 [0.808, 3.514] from 17/111 vs 10/110 all-cause deaths (a safety tally in a 221-patient trial). That single row creates τ²=0.14 and moves a 4,600-patient pool from 0.72 to 0.87. The trial publishes a time-to-event HR for death (1.77 [0.81, 3.87] per `AUDIT_QUEUE.md` item 7) — the site's own declared hierarchy says a source-reported effect+CI on the target estimand beats a count reconstruction.

Where the hierarchy is implemented: find it — `harness/pipeline.py` extraction/selection (`selected_estimator`, `derivation`, `study_effect.estimator_method`), `harness/extract.py` (read-only for you: do NOT rebuild the extractor; you may only change which already-extracted candidate is SELECTED). Read `harness/design_key.py` for `selected_estimator` and any existing preference logic. Read `DECLARED_ABSENT_INVENTORY.md` and `AUDIT_QUEUE.md` item 7.

## What to build

1. A single selection rule, in one function with a docstring stating the hierarchy: for a trial×outcome, if the committed source (cached abstract, cached full text under `cache/<slug>/` if present, or CT.gov results in cache) carries a published effect+CI whose estimand class matches the outcome's declared estimand class (see `harness/estmeasure.py` for classes; HR and RR are both FIRST_EVENT_RATIO — a published HR is preferred over a reconstructed RR for an HR/RR outcome), select it over any count reconstruction. Record on the trial row: `derivation`, `selection_rule` (a short code), and `alternatives` (the candidates NOT selected, with their values) so a reader can see what was passed over.
2. **Corpus-wide sweep** `scripts/source_hierarchy_sweep.py`: for all 32 topics, over every outcome's pooled rows, list rows where a published effect+CI on the target estimand exists in committed sources but a reconstruction was pooled. Output `docs/source_hierarchy_sweep.json` + a table in the report: slug, outcome, trial_key, reconstructed value, published value, source span (verbatim, ≤200 chars), whether the switch changes the pooled estimate/CI (rebuild and quote before/after). Report `n rows changed of N pooled rows over 32 topics`.
3. Apply the rule in the build; rebuild every affected page; `reproduce_review.py <slug>` on each.
4. J-EMPHASIS-HF specifically: check whether the HR 1.77 [0.81, 3.87] exists in ANY committed source in this clone (`cache/spironolactone-hfref-mortality/`, grep for `1.77` / `1·77`, PMC full text if cached). If it does, switch and report. If it does NOT (the abstract carries only the counts), do NOT invent it: leave the row reconstructed, add a typed limitation on the row — `PUBLISHED_EFFECT_KNOWN_NOT_IN_COMMITTED_SOURCE` with the AUDIT_QUEUE citation — and report "not switched: source not committed; fetch is a separate job". Fetching is out of scope for this lane.

## Plant (must fire pre-fix)

`tests/test_source_hierarchy.py`: (a) a synthetic trial×outcome where the source text carries both arm counts and a published HR with CI, outcome estimand HR → the selector MUST pick the published HR (assert this fails against the pre-fix selector — show the pre-fix behaviour by calling the pre-fix code path or by loading the pre-fix `docs/reviews/spironolactone-hfref-mortality/review.json` fixture and asserting the row is `reconstructed` while a published candidate is present in `alternatives` — if the pre-fix object records no alternatives, construct the fixture from the cached abstract and show the pre-fix selector's output); (b) a control where ONLY counts exist → reconstruction is kept; (c) a control where the published effect is on a DIFFERENT estimand class (rate ratio for a first-event outcome) → NOT selected (this must not weaken the estimand gate). Quote outputs.

Do not touch: `harness/synth.py`, `harness/page.py` rendering beyond adding the `alternatives` disclosure to the trial row, `harness/rob_sensitivity.py`, `harness/grade.py`, `docs/refusals.json`, search code. Do not change which trials are pooled — only which of a trial's already-extracted candidate effects is selected.
