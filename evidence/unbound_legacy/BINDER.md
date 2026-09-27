# Single-outcome binder evidence

Pinned source: `3876a62dca66764dff1b4f84d6b43356a1a9e3bb`. Local patch only; no commit, release, registry binding, or served-data regeneration.

## Classification comparison

| Class | Before | After |
|---|---:|---:|
| EXACT_TARGET | 8 | 10 |
| ENDPOINT_UNBOUND | 43 | 41 |
| NOT_AN_ABSTRACT_ROW | 14 | 14 |

All 65 rows compared by topic, outcome and identifier. The only class changes are the two ENDPOINT_UNBOUND -> EXACT_TARGET rows below. All eight previously EXACT rows and all 14 non-abstract rows are unchanged. This preserves existing classifications; it does not independently certify their correctness.

## Patch and conservative coverage

The fallback runs only after the existing component binder abstains. It requires a full name, definition, or explicit synonym in the estimate's own adjacent outcome slot. Retrieval `keywords` are not treated as equivalent outcome names: a source-defined abbreviation is accepted only if it also occurs in the declared keywords. The held AAD expansion is resolved from each abstract, not from a topic-specific dictionary. Orthographic normalization handles whitespace, hyphens, diarrhoea/diarrhea, and reversible legacy encoding damage.

Only one source-reported ratio is supported. The point must match the explicit `effect` argument, or (for the existing three-argument API) an estimate actually present in the source quotation. The abstract-candidate caller now supplies its effect. The requested classifier script is unchanged and uses the three-argument API; a quotation truncated before its estimate therefore remains unbound in this report. Count-derived rows, transformed relative-risk reductions, long/non-adjacent outcome descriptions and multi-effect sentences remain abstentions. These are coverage limitations, not proof that their underlying results concern the wrong outcome.

Composite declarations (including unrecognized component vocabularies and trial annotation component lists), subgroup/secondary qualifiers, unresolved timepoints/populations, and ambiguous outcome clauses cannot use this fallback. Existing GLP-1/composite behavior remains on the original path. `_identity_missing` and admissibility are unchanged.

## Static versus dynamic disclosure

| Item | Static rule or dynamic evidence |
|---|---|
| Grammar, qualifier rejection, unique-estimate requirement | Static conservative parsing rules |
| Outcome identity terms | Dynamic topic spec; no per-topic synonym table |
| Abbreviation expansion | Dynamic held abstract plus declared keywords |
| Sentences, PMIDs, effects | Pinned git records and impact rows; newly bound points checked against held sentences |
| Counts and class changes below | Computed from baseline and rerun JSON |

## Every newly bound row

### probiotics-aad-prevention / Antibiotic-associated diarrhoea / PMID 35727573

Row point: 0.81. single outcome: declared phrase 'aad' adjacent to the row's estimate.

> Compared with placebo (n = 155), the probiotic (n = 158) had no effect on risk of AAD (relative risk [RR], 0.81; 95% CI, 0.49-1.33).

### probiotics-aad-prevention / Antibiotic-associated diarrhoea / PMID 24772726

Row point: 0.7. single outcome: declared phrase 'aad' adjacent to the row's estimate.

> The relative risk for AAD was 0.7 with the 95% CI being 0.4 to 1.2.

## Every remaining unbound abstract row

| Topic | Outcome | PMID | Reason |
|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | Mortality | PMID 35041780 | single outcome: timepoint identity is missing or different |
| balanced-crystalloids-vs-saline-mortality | Mortality | PMID 34375394 | single outcome: source quotation does not uniquely prefix a held sentence |
| balanced-crystalloids-vs-saline-mortality | New renal-replacement therapy | PMID 35041780 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| colchicine-postop-af | Postoperative atrial fibrillation | PMID 42132185 | single outcome: row point estimate is unavailable or differs from the sentence |
| colchicine-postop-af | Postoperative atrial fibrillation | PMID 32720823 | single outcome: row point estimate is unavailable or differs from the sentence |
| colchicine-postop-af | Postoperative atrial fibrillation | PMID 25172965 | single outcome: subgroup or secondary identity is unresolved |
| colchicine-recurrent-pericarditis | Recurrent pericarditis | PMID 24694983 | single outcome: source quotation does not uniquely prefix a held sentence |
| colchicine-recurrent-pericarditis | Recurrent pericarditis | PMID 21873705 | single outcome: timepoint identity is missing or different |
| colchicine-recurrent-pericarditis | Symptom persistence at 72 hours | PMID 21873705 | single outcome: timepoint identity is missing or different |
| colchicine-secondary-cv-prevention | Gastrointestinal adverse effects | PMID 34876021 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| colchicine-secondary-cv-prevention | Non-cardiovascular death | PMID 32865380 | single outcome: row point estimate is unavailable or differs from the sentence |
| corticosteroids-cap-mortality | All-cause mortality | PMID 36942789 | single outcome: timepoint identity is missing or different |
| corticosteroids-cap-mortality | All-cause mortality | PMID 25688779 | single outcome: timepoint identity is missing or different |
| corticosteroids-cap-mortality | Hyperglycaemia | PMID 25688779 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| corticosteroids-cap-mortality | Hyperglycaemia | PMID 25608756 | single outcome: row point estimate is unavailable or differs from the sentence |
| corticosteroids-covid19-mortality | 28-day all-cause mortality | PMID 32678530 | single outcome: row point estimate is unavailable or differs from the sentence |
| denosumab-vertebral-fracture | New vertebral fracture | PMID 19671655 | single outcome: timepoint identity is missing or different |
| denosumab-vertebral-fracture | Nonvertebral fracture | PMID 19671655 | single outcome: row point estimate is unavailable or differs from the sentence |
| denosumab-vertebral-fracture | Hip fracture | PMID 19671655 | single outcome: row point estimate is unavailable or differs from the sentence |
| doac-vte-recurrence | Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | PMID 24344086 | single outcome: composite identity is outside this fallback |
| doac-vte-recurrence | Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | PMID 19966341 | single outcome: composite identity is outside this fallback |
| doac-vte-recurrence | Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | PMID 22449293 | single outcome: composite identity is outside this fallback |
| doac-vte-recurrence | Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | PMID 21128814 | single outcome: composite identity is outside this fallback |
| doac-vte-recurrence | Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | PMID 23991658 | single outcome: composite identity is outside this fallback |
| doac-vte-recurrence | Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | PMID 23808982 | single outcome: composite identity is outside this fallback |
| metformin-pcos-ovulation | Ovulation with metformin added to clomifene | PMID 11172832 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| noac-vs-warfarin-af-stroke | Major bleeding | PMID 24251359 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| noac-vs-warfarin-af-stroke | Major bleeding | PMID 21870978 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| probiotics-aad-prevention | Antibiotic-associated diarrhoea | PMID 32035998 | single outcome: row point estimate is unavailable or differs from the sentence |
| probiotics-aad-prevention | Antibiotic-associated diarrhoea | PMID 23932219 | single outcome: row point estimate is unavailable or differs from the sentence |
| probiotics-aad-prevention | Antibiotic-associated diarrhoea | PMID 18701826 | single outcome: timepoint identity is missing or different |
| probiotics-aad-prevention | Antibiotic-associated diarrhoea | PMID 18410562 | single outcome: source quotation does not uniquely prefix a held sentence |
| probiotics-aad-prevention | Antibiotic-associated diarrhoea | PMID 11560298 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| probiotics-aad-prevention | Antibiotic-associated diarrhoea | PMID 7872284 | single outcome: row point estimate is unavailable or differs from the sentence |
| probiotics-aad-prevention | Antibiotic-associated diarrhoea | PMID 21165295 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| spironolactone-hfref-mortality | All-cause mortality | PMID 10471456 | single outcome: row point estimate is unavailable or differs from the sentence |
| statins-primary-prevention-elderly | Major vascular events | PMID 42670961 | single outcome: row point estimate is unavailable or differs from the sentence |
| tocilizumab-covid19-mortality | 28-day all-cause mortality | PMID 33933206 | single outcome: source quotation does not uniquely prefix a held sentence |
| tocilizumab-covid19-mortality | Serious adverse events | PMID 33631066 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| tocilizumab-covid19-mortality | Serious adverse events | PMID 33332779 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| tranexamic-acid-pph | Death due to bleeding | PMID 28456509 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |

## Negative plants and the clauses that stop them

| Plant (synthetic) | Defect if accepted | Patch clause |
|---|---|---|
| Mortality or adverse events under AAD; primary-outcome label with an AAD definition elsewhere | Another outcome inherits target identity | Full declared phrase must occupy the ratio's own outcome slot |
| Diarrhoea under diarrhoea-or-vomiting composite | Component substituted for composite | Composite declaration guard, even with no recognized canonical components |
| Subgroup, men-only, secondary, or day-7 result | Restricted population/timepoint substituted for target | Qualifier/population/ordinal guards and timepoint equality |
| Mortality with/and AAD, non-AAD, recurrent AAD, or a trailing men-only qualifier | Incidental, combined, or negated mention treated as target | Qualified/ambiguous prefix guard |
| Correct outcome but row point 0.70 versus sentence 0.81 | Endpoint identity attached to another estimate | Exact point equality |
| Truncated quote with no point | Recovered sentence presumed to be the row's numeric result | Explicit row effect or quoted estimate required |
| Two effects in one sentence | First number silently attached to another outcome | Exactly one ratio required |
| Unexpanded AAD | Acronym guessed from retrieval keyword | Held name-to-abbreviation expansion required |

Tests include positive controls for the exact-point and truncation plants, and validate every previously classified held abstract row. Wrong-outcome plants keep the same ratio and place the correct target definition elsewhere in the abstract, so a whole-abstract keyword fallback would wrongly admit them.

## Reproduction

```text
python evidence/unbound_legacy/classify_legacy_rows.py 3876a62dca66764dff1b4f84d6b43356a1a9e3bb evidence/unbound_legacy/impact_3876a62d.json evidence/unbound_legacy/legacy_rows_classified_binder.json
python -m pytest -q -p no:cacheprovider tests/test_single_outcome_binding.py tests/test_unbound_legacy_failclosed.py
```

Final verification: **33 passed in 67.94s**, using only the two test files above (including held GLP-1/composite controls). `git diff --check` passed. All four output files are UTF-8 without BOM. The final classifier rerun retained the table above; no already-classified row changed class.
