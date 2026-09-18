# LANE S2A Report

Date: 2026-09-16. No commit made.

## 1. What Was Wrong, Mechanism, Files

Overall determination: the current committed code path does not make screening eligibility conditional on whether the target outcome is reported. The current missing item was a direct regression test proving a P/I/C/design-matching record stays screened in when the target outcome text is absent. I added that forward gate. The claimed historical defect of 132 outcome-axis exclusions is not reproducible from this clone's executable `harness/screen.py` history or committed review objects.

Hardcode disclosure:

| Item | Status | Disclosure |
|---|---:|---|
| Current corpus counts | MEASURED | Parsed `docs/reviews/*/review.json` from this clone. |
| Historical 132 outcome-axis exclusions | CLAIMED | Not found as a number or explicit rule in this repo history. |
| Historical 167 of 1068 code-decided rows | CLAIMED | Not found in this repo; current measured total is 3143 screening rows. |
| Synthetic regression record | INFERRED/STATIC | Test fixture only; not used as real evidence or corpus output. |
| PIONEER-HF pooling 0.872 to 0.828 | CLAIMED | Inputs for recomputation are not in the committed cache. |

### Q1 Verdict: LANDED

Evidence says current screening is P/I/C/design only. Outcome keywords are used downstream for extraction, absence classification, reporting, and diagnostics, not for include/exclude screening.

Commands run:

```text
rg -n 'def screen_record|def run\(|return \("exclude"|return \("include"|X-CONTRAST|X-DEDUP|INCLUDE|X-DESIGN|rule_id' harness\screen.py
rg -n "def concept_query|def _build_outcome|scr = screen\.run|included = \[|extract\.extract_trial|extract_ctgov|declared_absent|absence_mod\.classify|def _outcome_specs|screening_records|def build_review_core" harness\acquisition.py harness\pipeline.py harness\protocol_compiler.py harness\invalidation.py
rg -n -i "primary_outcome|outcome.{0,40}keyword|keyword.{0,40}outcome|reports? (the )?outcome|declared_absent|declared absent|absence|included =|screen\.run|screening_records" scripts topics
rg -n -i "reports? (the )?outcome|outcome.{0,50}(exclude|include|eligib|screen)|primary_outcome\.keywords|declared_absent|declared absent|absence" harness\pipeline.py harness\protocol_compiler.py harness\invalidation.py harness\acquisition.py
```

Rule ids the screener can emit:

| Rule id | File/function | What it tests |
|---|---|---|
| `X1` | `harness/screen.py:screen_record` | Not an RCT by publication type/text/registry design checks. |
| `X2` | `harness/screen.py:screen_record` | Wrong/off-topic population, including configured `population_none` or missing `population_any`. |
| `X3` | `harness/screen.py:screen_record` | Intervention missing/wrong form or comparator missing. |
| `X-DESIGN` | `harness/screen.py:screen_record` | Required double-blind/placebo/masked design not evidenced. |
| `INCLUDE` | `harness/screen.py:screen_record` | P/I/C/design met. |
| `X-CONTRAST` | `harness/screen.py:run` | Curated confirmed non-contrast eviction before ordinary screening output. |
| `X-DEDUP` | `harness/screen.py:run` | Curated duplicate/companion report eviction. |

Hit classification:

| Hit area | Classification | Evidence |
|---|---|---|
| `harness/acquisition.py:concept_query` | Neither eligibility defect nor target-result status | Search/retrieval query built from registered P/I/design concepts; no outcome keyword gate. |
| `harness/pipeline.py:build_review_core` | Eligibility | Calls `screen.run(merged, config)` and then `included = [d for d in scr["decisions"] if d["decision"] == "include"]` before outcome extraction. |
| `harness/pipeline.py:_build_outcome` and `_outcome_specs` | Target-result status, correct | Outcome specs/keywords drive `extract.extract_trial`, `extract_ctgov`, fulltext extraction, refusals, and `declared_absent_trials`. |
| `harness/pipeline.py` false-absence guard and `absence_mod.classify` | Target-result status, correct | Assigns `state`/`state_basis` to declared-absent rows after screening. |
| `harness/protocol_compiler.py` primary-outcome hits | Neither eligibility defect | Reads estimand/population metadata for protocol/config checks, not screening decisions. |
| `harness/invalidation.py` hits | Neither eligibility defect | Page staleness/completeness checks such as `eligible_declared_absent`. |
| `scripts/outcome_judgments.py`, `scripts/comparator_correctness_sweep.py` | Neither eligibility defect | Outcome identity/comparator audit scripts; not the screen include/exclude path. |
| `scripts/measure_regression_corpus_recall*.py`, `scripts/build_search_benchmark.py`, `scripts/fill_matrix.py` | Neither eligibility defect | Measurement scripts over pooled/declaration sets, not screen decisions. |
| `topics/*.json primary_outcome` | Target-result status config | Outcome specs exist, but are not read into `screen_record` eligibility. |

### Q2 Verdict: LANDED

Target-result status is a distinct populated field in current review objects.

Command run: a JSON measurement over `docs/reviews/*/review.json`, reading `screening.records`, `outcomes[].trials`, and `outcomes[].declared_absent_trials`.

Measured current objects:

| Metric | Result |
|---|---:|
| Review objects | MEASURED 32 |
| Screening rows | MEASURED 3143 |
| Screened-in records | MEASURED 307 |
| Unique screened-in-not-pooled records with at least one status row | MEASURED 206 of 206 |
| Outcome-level status rows populated | MEASURED 674 of 674 |
| Missing `absent_kind`/`state`/`reason` among status rows | MEASURED 0 of 674 |

Vocabulary actually present:

| Field | Values |
|---|---|
| `absent_kind` | MEASURED `machine_absent`: 651; `refused_on_evidence`: 15; `adjudicated_absent`: 8 |
| `state` | MEASURED `SOURCE_NOT_RETRIEVED`: 501; `NO_OUTCOME_DATA_IN_SOURCE`: 107; `EXTRACTION_NOT_PERFORMED`: 46; `REFUSED_ON_EVIDENCE`: 20 |

Per-topic declared-absent outcome cells, all populated:

```text
balanced-crystalloids-vs-saline-mortality 21 of 21
colchicine-postop-af 19 of 19
colchicine-recurrent-pericarditis 12 of 12
colchicine-secondary-cv-prevention 82 of 82
corticosteroids-cap-mortality 23 of 23
corticosteroids-covid19-mortality 15 of 15
dapagliflozin-hfpef-hosp 4 of 4
denosumab-vertebral-fracture 2 of 2
doac-vte-recurrence 0 of 0
dpp4-mace-t2d 2 of 2
empagliflozin-hfpef-hosp 3 of 3
esketamine-trd-madrs 8 of 8
finerenone-ckd-t2d-renal 16 of 16
glp1-ra-mace-t2d 19 of 19
iv-iron-hfref-hosp 25 of 25
melatonin-primary-insomnia-sol 17 of 17
metformin-pcos-ovulation 24 of 24
noac-vs-warfarin-af-stroke 12 of 12
omega3-cardiovascular-events 58 of 58
pcsk9-mace 4 of 4
probiotics-aad-prevention 164 of 164
sacubitril-valsartan-hfref 6 of 6
semaglutide-obesity-mace 1 of 1
semaglutide-obesity-weight 26 of 26
sglt2-ckd-progression 20 of 20
sglt2-hfref-hosp-cvdeath 7 of 7
sglt2-primary-prevention-hf 16 of 16
spironolactone-hfref-mortality 6 of 6
statins-primary-prevention-elderly 13 of 13
ticagrelor-vs-clopidogrel-acs 6 of 6
tocilizumab-covid19-mortality 33 of 33
tranexamic-acid-pph 10 of 10
```

Comparison files:

| File | Evidence |
|---|---|
| `harness/absence.py:classify` | Defines the state ontology and returns `EXTRACTION_NOT_PERFORMED`, `NO_OUTCOME_DATA_IN_SOURCE`, or `SOURCE_NOT_RETRIEVED` from available source text. |
| `tests/test_absence_ontology.py` | Tests that number-present rows are not trial absence, abstract-only misses are `SOURCE_NOT_RETRIEVED`, and only true source absence gets strong absence wording. |
| `harness/page.py` | Labels states separately; only `NO_OUTCOME_DATA_IN_SOURCE` licenses "declared absent" wording. |
| `DECLARED_ABSENT_INVENTORY.md` | Older inventory reports MEASURED-IN-FILE 705 re-extractable, 12 genuine exclusions, 122 positive-control/pivotal; current review objects measure 674 status rows, so the inventory is not an exact current object count. |

### Q3 Verdict: LANDED

The current "code-decided vs not" figures in this repo are not the claimed 167 of 1068. They measure as 3143 of 3143 rows carrying a `rule_id` and `span`, with 2583 rows still carrying `found_by: legacy_unrecorded`.

Command run: JSON measurement over all current review objects, reading `screening.records[].found_by`, `rule_id`, and `span`.

Measured totals:

| Metric | Result |
|---|---:|
| Review objects | MEASURED 32 |
| Screening rows | MEASURED 3143 |
| Rows with both `rule_id` and `span` fields populated | MEASURED 3143 of 3143 |
| Rows with no `rule_id` | MEASURED 0 of 3143 |
| Rows with `found_by: legacy_unrecorded` | MEASURED 2583 of 3143 |
| Rows with `found_by: UNRECORDED` | MEASURED 560 of 3143 |

Rule vocabulary:

```text
INCLUDE 307
X1 1941
X2 552
X3 315
X-DESIGN 14
X-DEDUP 12
X-CONTRAST 2
```

Per-topic row table:

```text
slug                                      rows  include  rule+span  legacy  no_rule
balanced-crystalloids-vs-saline-mortality 29   8        29         13      0
colchicine-postop-af                       67   8        67         63      0
colchicine-recurrent-pericarditis          53   3        53         47      0
colchicine-secondary-cv-prevention         120  29       120        94      0
corticosteroids-cap-mortality              114  9        114        110     0
corticosteroids-covid19-mortality          56   8        56         27      0
dapagliflozin-hfpef-hosp                   97   5        97         80      0
denosumab-vertebral-fracture               71   1        71         71      0
doac-vte-recurrence                        234  6        234        210     0
dpp4-mace-t2d                              38   5        38         8       0
empagliflozin-hfpef-hosp                   100  4        100        80      0
esketamine-trd-madrs                       136  6        136        109     0
finerenone-ckd-t2d-renal                   23   6        23         5       0
glp1-ra-mace-t2d                           11   9        11         11      0
iv-iron-hfref-hosp                         39   9        39         31      0
melatonin-primary-insomnia-sol             126  9        126        119     0
metformin-pcos-ovulation                   154  9        154        125     0
noac-vs-warfarin-af-stroke                 35   9        35         6       0
omega3-cardiovascular-events               114  22       114        84      0
pcsk9-mace                                 9    2        9          6       0
probiotics-aad-prevention                  468  60       468        444     0
sacubitril-valsartan-hfref                 81   7        81         52      0
semaglutide-obesity-mace                   66   1        66         64      0
semaglutide-obesity-weight                 143  14       143        115     0
sglt2-ckd-progression                      35   8        35         5       0
sglt2-hfref-hosp-cvdeath                   18   3        18         4       0
sglt2-primary-prevention-hf                294  20       294        276     0
spironolactone-hfref-mortality             226  3        226        219     0
statins-primary-prevention-elderly         28   5        28         6       0
ticagrelor-vs-clopidogrel-acs              32   3        32         30      0
tocilizumab-covid19-mortality              50   12       50         20      0
tranexamic-acid-pph                        76   4        76         49      0
```

Spot-check: MEASURED sample seed `20260916`, 40 screening rows drawn from 3143 rows. Result: 40 hits of 40, 0 misses, 0 not found. The checker verified source-backed evidence against cached records and included rule classes `X1`, `X2`, `X3`, `X-DEDUP`, and `INCLUDE`.

Quoted sample examples:

```text
X1: publication types: Journal Article
X2: examined title/conditions: Effect of Finerenone on Chronic Kidney Disease Outcomes in Type 2 Diabetes...
X3: examined: Effect of Dapagliflozin on Heart Failure and Mortality in Type 2 Diabetes Mellitus.
X-DEDUP: companion/duplicate report title span was present for the duplicate publication row.
INCLUDE: population and comparator snippets were present for the included trial rows.
```

### Q4 Verdict: CANNOT DETERMINE

I could not reproduce the claimed 132 historical outcome-axis exclusions from this clone.

Commands run:

```text
git log --oneline -S"outcome" -- harness/screen.py
git log --oneline -- harness/screen.py
git show 7a016378:harness/screen.py > .tmp/screen_7a016378.py
git show 7a016378^:harness/screen.py
git show 167f4b18:docs/reviews/sacubitril-valsartan-hfref/review.json
git show 57033614:docs/reviews/sacubitril-valsartan-hfref/review.json
```

Measured/inferred trail:

| Evidence | Result |
|---|---|
| `git log -S"outcome" -- harness/screen.py` | MEASURED hits: `a1193b9b PREVENTION_TRIAL_TITLE_OMITS_OUTCOME...` and `7a016378 Automate topic 1...`. The prevention commit is about enrolled population text, not target-outcome reporting eligibility. |
| Earliest executable `harness/screen.py` | MEASURED `7a016378`; parent says `fatal: path 'harness/screen.py' exists on disk, but not in '7a016378^'`. |
| Earliest executable screener behavior | MEASURED includes the synthetic no-target-outcome eligible record. |
| Sacubitril historical objects inspected | MEASURED `167f4b18` and `57033614` already show PIONEER-HF included with `INCLUDE` and declared-absent status. |
| Exhaustive read-only history sweep | MEASURED 225 commits, 32 paths, 5903 historical review objects checked, 1297 missing objects, 0 parse errors, 93 unique excluded-row hits containing outcome/report/endpoint words. |

The 93 historical hits were not explicit target-outcome reporting exclusions. Their rule ids/reasons were population, RCT, intervention/comparator, duplicate, contrast, or old negative-control classes (`X1`, `X2`, `X3`, `X-DEDUP`, `X-CONTRAST`, `X5`). Example output:

```text
01e39f2e|sacubitril-valsartan-hfref|40353367|X2|wrong population: title/conditions mention 'paediatric'.
01e39f2e|sacubitril-valsartan-hfref|32865377|X3|the randomised intervention is not [...]
40ebe401|colchicine-recurrent-pericarditis|COLCOT - 31733140|X5|COLCOT: colchicine vs placebo but in post-myocardial-infarction coronary disease - a primary trial of a DIFFERENT topic in this set [...]
```

Therefore:

| Requested historical number | Determination |
|---|---|
| Outcome-axis exclusions in history | CANNOT DETERMINE; MEASURED 0 explicit target-outcome rule rows, but history does not carry a pre-`7a016378` screener. |
| Revisited under P/I/C/design | CANNOT DETERMINE; no reproducible N of outcome-axis rows. |
| Flipped to include | CANNOT DETERMINE; no reproducible N of outcome-axis rows. |
| Now pooled vs declared-absent | CANNOT DETERMINE for the claimed 132; for inspected PIONEER-HF, current status is included and declared absent for the primary composite. |

### Q5 Verdict: LANDED

PIONEER-HF current status in `sacubitril-valsartan-hfref`:

Commands run:

```text
rg -n "30415601|Angiotensin-Neprilysin Inhibition in Acute Decompensated Heart Failure|PIONEER-HF" cache\sacubitril-valsartan-hfref\records.json docs\reviews\sacubitril-valsartan-hfref\review.json
python JSON inspection of docs/reviews/sacubitril-valsartan-hfref/review.json
python JSON inspection of cache/sacubitril-valsartan-hfref/records.json
```

Measured fields:

| Question | Result |
|---|---|
| Named PMID `30415601` in cache? | MEASURED no. |
| Exact title string in cache? | MEASURED no for `Angiotensin-Neprilysin Inhibition in Acute Decompensated Heart Failure`. |
| Current row present? | MEASURED yes as registry row `PIONEER-HF - NCT02554890`. |
| Current screening decision | MEASURED `include`. |
| Current rule id | MEASURED `INCLUDE`. |
| Target-result status for primary composite | MEASURED `absent_kind: machine_absent`, `state: SOURCE_NOT_RETRIEVED`, reason: no extractable primary-composite effect in abstract. |
| Cached CT.gov primary outcome | MEASURED `N-terminal Pro-brain Natriuretic Peptide (NT-proBNP) Values and Time-averaged Change From Baseline`. |
| Cached CV death/HF hospitalization composite | MEASURED not present among the 9 cached CT.gov outcome rows. |
| Pooling result if included | CANNOT DETERMINE from committed cache; `0.872 -> 0.828` remains CLAIMED. |

Cached `NCT02554890` CT.gov outcomes were NT-proBNP primary, symptomatic hypotension, hyperkalemia, angioedema, hs-troponin, urinary cGMP, urinary cGMP/creatinine ratio, BNP to NT-proBNP ratio, and NT-proBNP at Week 8. I did not pool it.

### Q6 Verdict: NOT LANDED as historical plant; LANDED as forward regression gate

Existing tests did not contain a direct assertion that a P/I/C/design-matching record without target-outcome words stays screened in. I added `tests/test_screen_no_outcome_axis.py`.

Test name:

```text
tests/test_screen_no_outcome_axis.py::test_screen_includes_pic_design_trial_even_when_target_outcome_not_reported
```

Exact assertions:

```python
assert not any(k.lower() in haystack for k in TARGET_KEYWORDS)
assert (decision, rule) == ("include", "INCLUDE"), (decision, rule, reason, span)
assert state == "SOURCE_NOT_RETRIEVED", basis
```

Post-fix/current output:

```text
python -m pytest tests/test_screen_no_outcome_axis.py -q
.                                                                        [100%]
1 passed in 1.65s
```

Historical plant attempt:

```text
git show 7a016378:harness/screen.py > .tmp/screen_7a016378.py
```

Output against earliest executable screener:

```text
7a016378 screen_record result: ('include', 'INCLUDE', 'RCT of sacubitril vs enalapril in heart failure; double-blind placebo-controlled <U+FFFD> P/I/C/design met.')
```

Pre-`7a016378` attempt:

```text
git show 7a016378^:harness/screen.py
fatal: path 'harness/screen.py' exists on disk, but not in '7a016378^'
```

So the new gate is useful going forward, but it was not shown to fire against an executable pre-fix screener in this repo.

### Q7 Verdict: LANDED for report-only observation

Trial-unit language is owned by lane PU and was not changed.

Measured current included screening id types:

```text
included id_type counts: pmid 243, nct 64, total 307
all screening id_type counts: pmid 2583, nct 560, total 3143
```

Observation: `harness/page.py` renders screening counts with trial language while many included screening rows are PMID publication records. That means the page wording can count publication records as "trials"; I did not fix this in S2A.

## 2. Plant

Plant status: partially blocked. The newly added regression gate passes current code and checks the intended invariant, but the historical pre-fix fire could not be demonstrated because the earliest executable old screener in this repo already satisfies the invariant and its parent has no `harness/screen.py`.

Test:

```text
tests/test_screen_no_outcome_axis.py::test_screen_includes_pic_design_trial_even_when_target_outcome_not_reported
```

Pre-fix probe output:

```text
7a016378 screen_record result: ('include', 'INCLUDE', 'RCT of sacubitril vs enalapril in heart failure; double-blind placebo-controlled <U+FFFD> P/I/C/design met.')
fatal: path 'harness/screen.py' exists on disk, but not in '7a016378^'
```

Post-fix/current output:

```text
python -m pytest tests/test_screen_no_outcome_axis.py -q
.                                                                        [100%]
1 passed in 1.65s
```

## 3. Pages Rebuilt Or Changed

None. I did not rebuild pages and did not change `docs/reviews/*`, `docs/m/*`, pooling, search, or extraction outputs.

## 4. Tests

Targeted test:

```text
python -m pytest tests/test_screen_no_outcome_axis.py -q
.                                                                        [100%]
1 passed in 1.65s
```

Full suite command required by the lane:

```text
python -m pytest tests -x -q
```

Full suite result:

```text
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: docs/fix_ledger.json is stale; run python scripts/render_fix_ledger.py
1 failed, 184 passed in 410.68s (0:06:50)
```

I did not update `docs/fix_ledger.json` because that is outside this lane's local screening/status determination and would change an unrelated generated artefact.

## 5. What I Did Not Do

- Did not commit, stage, stash, checkout, reset, clean, or touch `.git/` beyond allowed read-only `git log`/`git show`.
- Did not rerun search or use the network.
- Did not touch pooling, `harness/synth.py`, the extractor, or which trials are pooled.
- Did not rebuild pages.
- Did not add/remove any trial from any pool.
- Did not recompute the claimed PIONEER-HF 0.872 to 0.828 movement because the PMID/exact title and the primary-composite input were not present in the committed cache.
- Did not fix the unrelated stale `docs/fix_ledger.json` full-suite failure.

## 6. Files Changed Or Added

- Added `tests/test_screen_no_outcome_axis.py`
- Added `LANE-S2A-REPORT.md`
- Wrote temporary read-only probe file `.tmp/screen_7a016378.py`
