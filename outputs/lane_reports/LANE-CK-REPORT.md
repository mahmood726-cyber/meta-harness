# LANE CK report

All counts, estimates, ids, and test timings in this report are MEASURED from this working tree unless a row is explicitly marked CLAIMED or INFERRED.

## 1. What was wrong, mechanism, files

The failure was a silent compatibility-key assertion gap. Outcome-level keys asserted uniform dimensions, but no gate re-derived those dimensions from the pooled trial rows and cached source text.

Mechanism added:

- `harness/compat_check.py` derives per-trial `analysis_set`, `follow_up_window`, `endpoint_definition`, `population_age`, and intervention ontology fields from trial rows, cached records, and `docs/definition_audit.json`.
- `harness/pipeline.py` runs the enrichment during page build.
- `harness/gate.py::check_compat_key_underlying` refuses `COMPAT_ASSERTED_NOT_UNDERLYING`.
- `harness/page.py` renders heterogeneous dimensions and `HARMS_INCOMPLETE` instead of an isolated harms number.
- `harness/grade.py`, `harness/page.py`, and `harness/limitations.py` carry/render `rob_basis`.
- `harness/hazard_consumers.py` wires `HARMS_INCOMPLETE/PARTIAL` limitation objects to a compat-underlying consumer verdict.
- `scripts/compat_underlying_sweep.py` writes `docs/compat_underlying_sweep.json`.

Corpus sweep:

| Metric | Result |
|---|---:|
| Pages with >=1 asserted violation | MEASURED: 28 of 32 |
| Violations by dimension | MEASURED: analysis_set 2; endpoint 41; follow_up_window 10 |
| Underivable dimensions | MEASURED: 0 |
| Harms incomplete panels | MEASURED: 4 |
| Outstanding OWED markers | MEASURED: 15 |

## 2. Plant

Plant tests in `tests/test_compat_underlying.py`:

- `test_pre_fix_probiotics_key_fires_on_underlying_trial_rows`: asserts pre-fix `aa8ed28a:docs/reviews/probiotics-aad-prevention/review.json` fires `COMPAT_ASSERTED_NOT_UNDERLYING` for `analysis_set`, `follow_up_window`, and `endpoint`.
- Exact assertions include SPAADA `value == "completers efficacy set"` with span containing `no efficacy data`; PLACIDE `value == "modified intention-to-treat"` with span containing `modified intention-to-treat`; Kotowska endpoint value containing `otherwise-unexplained`.
- `test_post_fix_probiotics_key_is_mixed_and_no_asserted_violation`: asserts rebuilt key starts `mixed (` and `trial-defined`, each heterogeneous dimension has `dimension_matches == False`, and `page_gate_violations(...) == []`.
- `test_comparator_population_match_is_derived_false_for_adult_comparator_with_paediatric_pool`: asserts probiotic comparator `topic_is_class == True`, `population_match == False`, and paediatric trials include one of `40488914`, `15740542`, or `18701826`.
- Synthetic controls assert uniform trials have `[]`, and a missing analysis field produces `COMPAT_DIMENSION_UNDERIVABLE`.
- Omega plants assert AF is `HARMS_INCOMPLETE`, REDUCE-IT `30415628` is named, Alpha Omega `20929341` counts as factorial, and Risk and Prevention `23656645` remains refused for endpoint identity.

Pre-fix measured output:

```text
PREFX count 3
VIOL analysis_set asserted intention-to-treat
39529939 => completers efficacy set | ... 9 participants discontinued the trial early ... had no efficacy data, and were excluded from the efficacy analysis ...
23932219 => modified intention-to-treat | ... Analysis was by modified intention-to-treat ...
VIOL follow_up_window asserted study end
39529939 => 14 days | ... until 14 days after the last antibiotic dose ...
23932219 => within 8 weeks | ... occurrence of AAD within 8 weeks ...
18410562 => during treatment plus 2 weeks | ... during or up to 2 weeks after the antibiotic therapy ...
VIOL endpoint asserted single endpoint
15740542 => ... otherwise-unexplained diarrhoea ...
18410562 => diarrhoea (>or=3 loose or watery stools/day for >or=48 h ...)
```

Post-fix measured output:

```text
POST key analysis_set=mixed (ITT x13, mITT x1, completers x1, per-protocol x1)
POST key follow_up_window=trial-defined (14-56 d; per trial listed)
POST key endpoint=trial-defined antibiotic-associated diarrhoea (definitions listed per trial)
POST page_gate_violations []
```

Targeted test output:

```text
7 passed in 1.79s
```

## 3. Rebuilt pages whose bytes changed

Primary arithmetic did not change.

| Page | Before | After |
|---|---|---|
| `probiotics-aad-prevention` | MEASURED: primary k=16, RR=0.702, CI 0.5352-0.921, tau2=0.15045. Key asserted `analysis_set=intention-to-treat`, `follow_up_window=study end`, `endpoint=single endpoint`. Comparator scope said topic/comparator not class and `population_match=True`. | MEASURED: primary k=16, RR=0.702, CI 0.5352-0.921, tau2=0.15045. Key now `analysis_set=mixed (ITT x13, mITT x1, completers x1, per-protocol x1)`, `follow_up_window=trial-defined (14-56 d; per trial listed)`, `endpoint=trial-defined antibiotic-associated diarrhoea (definitions listed per trial)`, with `COMPAT_DIMENSION_HETEROGENEOUS`. Comparator scope now class/class and `population_match=False` with paediatric trials `40488914`, `35727573`, `18701826`, `18410562`, `15740542`. Serious adverse events now `HARMS_INCOMPLETE` with 1 unresolved primary-pool report. `rob_basis`: D3 unassessed on 16 of 16 trials. |
| `omega3-cardiovascular-events` | MEASURED: primary k=7, RR=0.943, CI 0.846-1.051, tau2=0.00925. Key asserted `endpoint=composite`, `follow_up_window=trial end / longest randomized follow-up`. AF rendered k=1, RR=1.2296, CI 0.9819-1.5398. Unit-of-analysis counted 3 factorial trials. | MEASURED: primary k=7, RR=0.943, CI 0.846-1.051, tau2=0.00925. Key now `endpoint=trial-defined Major vascular events / MACE (definitions listed per trial)` and `follow_up_window=trial-defined (per trial listed)`. AF and bleeding now `HARMS_INCOMPLETE` with 2 unresolved primary-pool reports each. Unit-of-analysis counts 4 factorial trials, adding Alpha Omega `20929341`. Comparator scope is class/class for omega-3 preparations. `rob_basis`: D3 unassessed on 7 of 7 trials. |
| `pcsk9-mace` | MEASURED: primary k=2, RR=0.85, CI 0.5852-1.2346, tau2=0.0. Key asserted `endpoint=composite`. Injection-site reactions were reported-but-not-extractable prose. | MEASURED: primary k=2, RR=0.85, CI 0.5852-1.2346, tau2=0.0. Key now `endpoint=trial-defined Major adverse cardiovascular events (definitions listed per trial)`. Injection-site reactions now `HARMS_INCOMPLETE` with 2 unresolved primary-pool reports. `rob_basis`: D3 unassessed on 2 of 2 trials. |

Reproduction checks:

```text
OK probiotics-aad-prevention
1/1 reproduce (all reproducible)
OK omega3-cardiovascular-events
1/1 reproduce (all reproducible)
OK pcsk9-mace
1/1 reproduce (all reproducible)
```

## Screening ground truth for Phase-2A

No screening decisions were changed.

| PMID | Committed cache and screening verdict |
|---|---|
| `28057659` | MEASURED: cache title is a prevention trial protocol; pubtypes are Journal Article and Randomized Controlled Trial; abstract says protocol and trial registration `NCT02871908`. Screening currently includes it. Verdict for screening lane: false inclusion. |
| `22559011` | MEASURED: cache title is the PLACIDE study protocol; completed pooled trial is `23932219`. Screening currently includes protocol `22559011`. Verdict for screening lane: false inclusion. |
| `22370839` | MEASURED: cache title says AAD treatment; abstract says probiotics in the treatment of AAD. Screening currently includes it. Verdict for screening lane: false inclusion. |
| `34585011` | MEASURED: cache title says therapeutic efficacy in antibiotic-associated diarrhea; abstract says probiotic treatment. Screening currently includes it. Verdict for screening lane: false inclusion. |
| `14627358` | MEASURED: cache title is randomized yogurt for prevention of antibiotic-associated diarrhea; pubtypes include Clinical Trial and Randomized Controlled Trial. Screening excludes it with X3 no eligible comparator. Verdict for screening lane: false exclusion. |

## Extraction debt vs discovery failure

N is the committed primary `declared_absent_trials` / screened-in-not-pooled set for probiotics.

| Class | Count |
|---|---:|
| DISCOVERY_FAILURE | MEASURED: 27 of 44 |
| EXTRACTION_DEBT | MEASURED: 11 of 44 |
| ABSENT_IN_SOURCE | MEASURED: 4 of 44 |
| INELIGIBLE | MEASURED: 2 of 44 |

Measured ids:

- DISCOVERY_FAILURE: PMID 40716758, PMID 33032474, PMID 30439760, PMID 30149135, PMID 28871492, PMID 27169634, PMID 22370839, PMID 21552138, PMID 18949181, PMID 10547243, PMID 10545590, PMID 9570649, PMID 2184848, PMID 24044687, PMID 23618760, PMID 21871144, PMID 20145608, PMID 16292090, NCT06990568, NCT04529980, NCT02993419, NCT02722993, NCT03516409, NCT03755765, NCT02589964, NCT07234448, NCT05845073.
- EXTRACTION_DEBT: PMID 41699149, PMID 39935568, PMID 39497860, PMID 39429834, PMID 38258024, PMID 30912409, PMID 28057659, PMID 22559011, PMID 16572062, PMID 22371721, PMID 19138244.
- ABSENT_IN_SOURCE: PMID 42608299, PMID 40548185, PMID 39467682, PMID 34585011.
- INELIGIBLE: PMID 22472744, PMID 17356555.

## 4. Tests

Final required test command:

```text
python -m pytest tests -x -q
646 passed in 195.59s (0:03:15)
```

Additional targeted checks run after final edits:

```text
python -m pytest tests\test_compat_underlying.py -q
7 passed in 1.79s

python -m pytest tests\test_hazard_consumers.py -q
5 passed in 0.91s

python -m pytest tests\test_gate.py::test_real_review_reproduces_and_passes_full_gate -q
1 passed in 12.09s

python -m pytest tests\test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews -q
1 passed in 2.16s

python -m pytest tests\test_fixstate.py::test_real_store_validates -q
1 passed in 56.30s
```

## 5. Not done

- Did not change pooling arithmetic, trial inclusion, screening decisions, search code, `harness/synth.py`, or `harness/estmeasure.py`; these were explicitly out of scope.
- Did not rerun network search; the lane required committed cache only.
- Did not formally age-classify non-pooled adult/paediatric sensitivity or change the probiotic pool; classification was added as an exposed compatibility dimension only.
- Did not commit, stage, stash, reset, checkout, or clean.

## 6. Changed or added files

Added:

- `LANE-CK-REPORT.md`
- `docs/compat_underlying_sweep.json`
- `harness/compat_check.py`
- `scripts/compat_underlying_sweep.py`
- `tests/test_compat_underlying.py`

Changed:

- `docs/evidence/hazard-consumers-2026-09-14/README.md`
- `docs/evidence/search-v2-measurement-2026-09-15/README.md`
- `docs/fix_ledger.json`
- `docs/gate_scorecard.json`
- `docs/index.html`
- `docs/m/m586876fa/index.html`
- `docs/m/me0751432/index.html`
- `docs/m/mf6cd36c2/index.html`
- `docs/reviews/omega3-cardiovascular-events/REPRODUCTION.json`
- `docs/reviews/omega3-cardiovascular-events/index.html`
- `docs/reviews/omega3-cardiovascular-events/manifest.json`
- `docs/reviews/omega3-cardiovascular-events/review.json`
- `docs/reviews/pcsk9-mace/REPRODUCTION.json`
- `docs/reviews/pcsk9-mace/index.html`
- `docs/reviews/pcsk9-mace/manifest.json`
- `docs/reviews/pcsk9-mace/review.json`
- `docs/reviews/probiotics-aad-prevention/REPRODUCTION.json`
- `docs/reviews/probiotics-aad-prevention/index.html`
- `docs/reviews/probiotics-aad-prevention/manifest.json`
- `docs/reviews/probiotics-aad-prevention/review.json`
- `harness/gate.py`
- `harness/grade.py`
- `harness/hazard_consumers.py`
- `harness/limitations.py`
- `harness/page.py`
- `harness/pipeline.py`
- `harness/scope.py`
- `harness/unit_of_analysis.py`
- `registry/blind_map.json`
- `registry/gate_scorecard.json`
