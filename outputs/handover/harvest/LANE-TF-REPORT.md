# Lane TF report

HEAD: `237e90946f5b257265b0a3b1c986a8907d12eded`. Required base: `237e90946f5b257265b0a3b1c986a8907d12eded`. No commit, staging, reset, checkout, stash, push, or network retrieval. Candidate tree was read-only. `AACT_DIR` was an existing empty directory for builds and verification.

**IN PROGRESS — verification pending**. This is a lane integration result, not a CERTIFIED/SHIP or Overmind verdict.

## MEASURED

Numerical preservation: **32 of 32 topics**; 0 remaining sweep failures. Every primary/secondary/harm row identifier and numeric input/result is compared against the required HEAD pipeline on identical held input bytes. Only dependency/claim metadata and the new family identity annotations are excluded. The first run exposed one metadata-only comparison difference and one mixed primary/pooled-publication identity; targeted rechecks passed without moving values.

Second-pass source audit: **9378 assertions**, coverage **32 of 32 topics**. Source spans, registry aliases, dates, and typed registry values are checked. Mixed primary/pooled-report localization also has a held-source regression test.

GLP-1 manifest review_sha256: old `98726cc125e9fcc749601459bce442a9b581ef4cce81c60cf891fa6d643917f7` → new `32dfca4fd4002b5d1d5807f34952e1e58f862c33af7e020b387a7e0f189dddc9`.

Retained analysis inputs are distinguished from actual pooling. Seven held outcomes have a refused or suppressed pool: their input contributions remain auditable, but their pooled-family count is zero. This metadata correction changes no effect estimate, interval, sample size or other statistical result. The final refresh independently checks all 32 served review signatures against HEAD. Registry compact serialization also round-trips byte-identically for 32 of 32 topics (`.tmp/tf-registry-roundtrip.json`).

## Implementation and scope

The pipeline prepares family evidence before screening and attaches family IDs before dependent sensitivity/claim stamps. The ledger retains eligibility with spans/absence codes; declared strands or NONE; report/registry source roles, SHA-256 and retrieval origin; identity conflicts and typed registry value disagreements with all spans; and per-outcome MEASURED/REPORTED/EXTRACTABLE/POOLED or UNKNOWN states. A missing pool entry is not evidence of non-measurement. Duplicate family membership in an outcome or strand refuses the build. Deleting a held report source degrades eligibility and availability to SOURCE_RECORD_DELETED.

Unlinked reports are explicitly UNRESOLVED_REPORT_CANDIDATE nodes. They are retained for audit and their pre-existing pooled rows are preserved, but they are excluded from the registry-anchored family denominator. `membership.pooled_family_ids`/`pooled_family_count` count anchored families and `unresolved_pooled_candidate_ids` records the separate candidate set; original report-keyed membership remains for source joins. Family membership counts and dependency stamps use family IDs; source-facing trial_key remains report-keyed so source joins and dispute checks retain their original identifiers. Family counts therefore need not equal old report-row k. Eligibility and pooling are separate observed states: the chain explicitly names contributions without established structural eligibility instead of pretending these sets are nested.

The page replaces the current PRISMA count table and overview reconciliation with ledger-derived counts. Historical overview reconciliation is retained under “Superseded report-based reconciliation” so retractions are not erased. The index has a ledger-derived per-topic overview. Page and graph edits are one contiguous helper block plus one call-site change each; re-apply diffs: `.tmp/patches/page.py.diff`, `.tmp/patches/claimgraph.py.diff`. `harness/census.py` was not changed. Protected synth/envelope/invalidation/target_endpoint modules were not changed.

## INFERRED / CLAIMED

**INFERRED:** lexical role/structural-eligibility rules interpret held evidence; they are not human clinical adjudication. The mixed publication is localized only when its text explicitly identifies “this study/trial” with a held registry acronym and that registry cites the publication; other registration mentions remain visible. No identifier is selected from an acronym alone.

**CLAIMED scope:** held, offline corpus only. No exhaustive retrieval, historical registry reconstruction from missing bytes, fully resolved eligibility, or newly recovered treatment effect is claimed. Source conflict detection covers held identity-link conflicts and differing typed registry observations with matching outcome/group/parameter/category keys; unstructured prose disagreements are not exhaustively extracted. A source digest covers the canonical held operational record (or the original AACT row digest in its source reference), not the complete source PDF.

## Static versus dynamic disclosure

| Component | Static policy/inputs | Dynamic evidence and validation |
|---|---|---|
| Identity | Registry precedence; conservative parent-link and role patterns | Held IDs, citation rows, acronym spans; unresolved reports kept separate |
| Eligibility | Explicit P/I/C/design rules; protocol requirements | Held arms, conditions, dates/design spans; UNKNOWN on missing support |
| Ledger | Typed state vocabulary and SHA-256 encoding | Source records, source references, declared strands and actual membership |
| Counts/panel | State definitions only | Derived solely from ledger family objects, no typed result counts |
| Clinical numbers | No new effect/CI/N/p-value constants | Existing pool; all-outcome numerical preservation comparison |
| Snapshot | Acquisition snapshot label 2026-08-30 | Frozen ingredient bytes; label is not proof of historical cutoff |
| Plants | Explicit synthetic fixtures | Never enter research caches; held mixed-publication test is separate |

## Sweep table

| Topic | Eligible / ledger N | Contributing / N | Primary pooled / N | Unresolved report candidates | Pool preserved |
|---|---:|---:|---:|---:|---|
| balanced-crystalloids-vs-saline-mortality | 0 of 23 | 2 of 23 | 2 of 23 | 3 | True |
| colchicine-postop-af | 4 of 15 | 2 of 15 | 2 of 15 | 32 | True |
| colchicine-recurrent-pericarditis | 3 of 18 | 2 of 18 | 2 of 18 | 23 | True |
| colchicine-secondary-cv-prevention | 12 of 48 | 3 of 48 | 3 of 48 | 53 | True |
| corticosteroids-cap-mortality | 3 of 18 | 5 of 18 | 2 of 18 | 78 | True |
| corticosteroids-covid19-mortality | 1 of 37 | 2 of 37 | 1 of 37 | 10 | True |
| dapagliflozin-hfpef-hosp | 3 of 22 | 2 of 22 | 1 of 22 | 57 | True |
| denosumab-vertebral-fracture | 0 of 9 | 1 of 9 | 1 of 9 | 45 | True |
| doac-vte-recurrence | 1 of 78 | 5 of 78 | 5 of 78 | 136 | True |
| dpp4-mace-t2d | 5 of 37 | 4 of 37 | 3 of 37 | 0 | True |
| empagliflozin-hfpef-hosp | 1 of 25 | 1 of 25 | 1 of 25 | 68 | True |
| esketamine-trd-madrs | 2 of 40 | 4 of 40 | 4 of 40 | 63 | True |
| finerenone-ckd-t2d-renal | 4 of 22 | 2 of 22 | 2 of 22 | 0 | True |
| glp1-ra-mace-t2d | 143 of 238 | 8 of 238 | 8 of 238 | 0 | True |
| iv-iron-hfref-hosp | 2 of 17 | 2 of 17 | 0 of 17 | 12 | True |
| melatonin-primary-insomnia-sol | 3 of 16 | 1 of 16 | 1 of 16 | 76 | True |
| metformin-pcos-ovulation | 8 of 36 | 1 of 36 | 1 of 36 | 49 | True |
| noac-vs-warfarin-af-stroke | 0 of 33 | 4 of 33 | 4 of 33 | 1 | True |
| omega3-cardiovascular-events | 2 of 46 | 7 of 46 | 6 of 46 | 59 | True |
| pcsk9-mace | 2 of 9 | 4 of 9 | 3 of 9 | 2 | True |
| probiotics-aad-prevention | 0 of 61 | 5 of 61 | 5 of 61 | 343 | True |
| sacubitril-valsartan-hfref | 1 of 41 | 2 of 41 | 0 of 41 | 27 | True |
| semaglutide-obesity-mace | 0 of 4 | 1 of 4 | 1 of 4 | 37 | True |
| semaglutide-obesity-weight | 20 of 54 | 2 of 54 | 2 of 54 | 50 | True |
| sglt2-ckd-progression | 7 of 34 | 3 of 34 | 3 of 34 | 0 | True |
| sglt2-hfref-hosp-cvdeath | 2 of 17 | 2 of 17 | 2 of 17 | 0 | True |
| sglt2-primary-prevention-hf | 6 of 95 | 3 of 95 | 3 of 95 | 175 | True |
| spironolactone-hfref-mortality | 1 of 14 | 2 of 14 | 2 of 14 | 189 | True |
| statins-primary-prevention-elderly | 1 of 25 | 1 of 25 | 1 of 25 | 2 | True |
| ticagrelor-vs-clopidogrel-acs | 0 of 10 | 2 of 10 | 0 of 10 | 15 | True |
| tocilizumab-covid19-mortality | 4 of 39 | 4 of 39 | 1 of 39 | 10 | True |
| tranexamic-acid-pph | 5 of 39 | 1 of 39 | 1 of 39 | 23 | True |

## Three plants — verbatim pre/post

Command before implementation: `python -m pytest tests/test_trial_family_contract.py -q --tb=short`. The three tests respectively exercise two reports of one NCT pooled twice, an eligible family without a poolable value, and deletion of a family source record.

```text
FFF                                                                      [100%]
================================== FAILURES ===================================
__________ test_two_reports_of_one_nct_pooled_as_two_trials_refused ___________
tests\test_trial_family_contract.py:28: in test_two_reports_of_one_nct_pooled_as_two_trials_refused
    with pytest.raises(ValueError, match='DUPLICATE_FAMILY'):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE <class 'ValueError'>
____ test_eligible_family_without_poolable_value_is_named_in_missing_panel ____
tests\test_trial_family_contract.py:40: in test_eligible_family_without_poolable_value_is_named_in_missing_panel
    assert 'missing-evidence' in html and 'NCT00000001' in html and 'UNKNOWN' in html
E   AssertionError: assert ('missing-evidence' in '')
______________ test_deleting_source_record_degrades_ledger_state ______________
tests\test_trial_family_contract.py:49: in test_deleting_source_record_degrades_ledger_state
    assert nodes[0]['eligibility']['state'] == 'UNKNOWN'
E   AssertionError: assert 'ELIGIBLE' == 'UNKNOWN'
E     
E     - UNKNOWN
E     + ELIGIBLE
=========================== short test summary info ===========================
FAILED tests/test_trial_family_contract.py::test_two_reports_of_one_nct_pooled_as_two_trials_refused
FAILED tests/test_trial_family_contract.py::test_eligible_family_without_poolable_value_is_named_in_missing_panel
FAILED tests/test_trial_family_contract.py::test_deleting_source_record_degrades_ledger_state
3 failed in 3.51s
```

Post-fix command: `python -m pytest tests/test_trial_family.py tests/test_trial_family_contract.py tests/test_trial_family_ui.py -q --tb=short`. Includes the same three plants plus transplanted contracts, held-source validation and browser E2E.

```text
...................................                                      [100%]
35 passed in 103.05s (0:01:43)
```

## GLP-1 as rendered

Families screened 238 of 238; eligible 143 of 238; contributing to any outcome 8 of 238; pooled in primary 8 of 238. Unresolved eligibility 84 of 238. Unresolved report-only candidates 0 (outside family denominator). Contributing without established structural eligibility: NCT02465515. These are separate evidence states, not a nested eligibility funnel.

```text
Missing evidence in eligible families
Eligible families without a poolable value, by registered outcome; UNKNOWN is not NO.
NCT00085969 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00085969 / Gastrointestinal adverse events / UNKNOWN
NCT00085969 / Adverse events leading to discontinuation / UNKNOWN
NCT00099320 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00099320 / Gastrointestinal adverse events / UNKNOWN
NCT00099320 / Adverse events leading to discontinuation / UNKNOWN
NCT00103935 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00103935 / Gastrointestinal adverse events / UNKNOWN
NCT00103935 / Adverse events leading to discontinuation / UNKNOWN
NCT00241423 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00241423 / Gastrointestinal adverse events / UNKNOWN
NCT00241423 / Adverse events leading to discontinuation / UNKNOWN
NCT00318461 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00318461 / Gastrointestinal adverse events / UNKNOWN
NCT00318461 / Adverse events leading to discontinuation / UNKNOWN
NCT00324363 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00324363 / Gastrointestinal adverse events / UNKNOWN
NCT00324363 / Adverse events leading to discontinuation / UNKNOWN
NCT00375492 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00375492 / Gastrointestinal adverse events / UNKNOWN
NCT00375492 / Adverse events leading to discontinuation / UNKNOWN
NCT00381342 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00381342 / Gastrointestinal adverse events / UNKNOWN
NCT00381342 / Adverse events leading to discontinuation / UNKNOWN
NCT00382239 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00382239 / Gastrointestinal adverse events / UNKNOWN
NCT00382239 / Adverse events leading to discontinuation / UNKNOWN
NCT00516074 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00516074 / Gastrointestinal adverse events / UNKNOWN
NCT00516074 / Adverse events leading to discontinuation / UNKNOWN
NCT00577824 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00577824 / Gastrointestinal adverse events / UNKNOWN
NCT00577824 / Adverse events leading to discontinuation / UNKNOWN
NCT00603239 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00603239 / Gastrointestinal adverse events / UNKNOWN
NCT00603239 / Adverse events leading to discontinuation / UNKNOWN
NCT00612794 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00612794 / Gastrointestinal adverse events / UNKNOWN
NCT00612794 / Adverse events leading to discontinuation / UNKNOWN
NCT00620282 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00620282 / Gastrointestinal adverse events / UNKNOWN
NCT00620282 / Adverse events leading to discontinuation / UNKNOWN
NCT00688701 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00688701 / Gastrointestinal adverse events / UNKNOWN
NCT00688701 / Adverse events leading to discontinuation / UNKNOWN
NCT00696657 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00696657 / Gastrointestinal adverse events / UNKNOWN
NCT00696657 / Adverse events leading to discontinuation / UNKNOWN
NCT00712673 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00712673 / Gastrointestinal adverse events / UNKNOWN
NCT00712673 / Adverse events leading to discontinuation / UNKNOWN
NCT00713830 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00713830 / Gastrointestinal adverse events / UNKNOWN
NCT00713830 / Adverse events leading to discontinuation / UNKNOWN
NCT00715624 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00715624 / Gastrointestinal adverse events / UNKNOWN
NCT00715624 / Adverse events leading to discontinuation / UNKNOWN
NCT00763451 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00763451 / Gastrointestinal adverse events / UNKNOWN
NCT00763451 / Adverse events leading to discontinuation / UNKNOWN
NCT00765817 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00765817 / Gastrointestinal adverse events / UNKNOWN
NCT00765817 / Adverse events leading to discontinuation / UNKNOWN
NCT00839527 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00839527 / Gastrointestinal adverse events / UNKNOWN
NCT00839527 / Adverse events leading to discontinuation / UNKNOWN
NCT00866658 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00866658 / Gastrointestinal adverse events / UNKNOWN
NCT00866658 / Adverse events leading to discontinuation / UNKNOWN
NCT00870194 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00870194 / Gastrointestinal adverse events / UNKNOWN
NCT00870194 / Adverse events leading to discontinuation / UNKNOWN
NCT00975286 / 3-point major adverse cardiovascular events / UNKNOWN
NCT00975286 / Gastrointestinal adverse events / UNKNOWN
NCT00975286 / Adverse events leading to discontinuation / UNKNOWN
NCT01136798 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01136798 / Gastrointestinal adverse events / UNKNOWN
NCT01136798 / Adverse events leading to discontinuation / UNKNOWN
NCT01140893 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01140893 / Gastrointestinal adverse events / UNKNOWN
NCT01140893 / Adverse events leading to discontinuation / UNKNOWN
NCT01144338 / Gastrointestinal adverse events / UNKNOWN
NCT01144338 / Adverse events leading to discontinuation / UNKNOWN
NCT01169779 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01169779 / Gastrointestinal adverse events / UNKNOWN
NCT01169779 / Adverse events leading to discontinuation / UNKNOWN
NCT01179048 / Gastrointestinal adverse events / UNKNOWN
NCT01270789 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01270789 / Gastrointestinal adverse events / UNKNOWN
NCT01270789 / Adverse events leading to discontinuation / UNKNOWN
NCT01364584 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01364584 / Gastrointestinal adverse events / UNKNOWN
NCT01364584 / Adverse events leading to discontinuation / UNKNOWN
NCT01394952 / Adverse events leading to discontinuation / UNKNOWN
NCT01473953 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01473953 / Gastrointestinal adverse events / UNKNOWN
NCT01473953 / Adverse events leading to discontinuation / UNKNOWN
NCT01507285 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01507285 / Gastrointestinal adverse events / UNKNOWN
NCT01507285 / Adverse events leading to discontinuation / UNKNOWN
NCT01508949 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01508949 / Gastrointestinal adverse events / UNKNOWN
NCT01508949 / Adverse events leading to discontinuation / UNKNOWN
NCT01511172 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01511172 / Gastrointestinal adverse events / UNKNOWN
NCT01511172 / Adverse events leading to discontinuation / UNKNOWN
NCT01572740 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01572740 / Gastrointestinal adverse events / UNKNOWN
NCT01572740 / Adverse events leading to discontinuation / UNKNOWN
NCT01617434 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01617434 / Gastrointestinal adverse events / UNKNOWN
NCT01617434 / Adverse events leading to discontinuation / UNKNOWN
NCT01618162 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01618162 / Gastrointestinal adverse events / UNKNOWN
NCT01618162 / Adverse events leading to discontinuation / UNKNOWN
NCT01620463 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01620463 / Gastrointestinal adverse events / UNKNOWN
NCT01620463 / Adverse events leading to discontinuation / UNKNOWN
NCT01620489 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01620489 / Gastrointestinal adverse events / UNKNOWN
NCT01620489 / Adverse events leading to discontinuation / UNKNOWN
NCT01628445 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01628445 / Gastrointestinal adverse events / UNKNOWN
NCT01628445 / Adverse events leading to discontinuation / UNKNOWN
NCT01632163 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01632163 / Gastrointestinal adverse events / UNKNOWN
NCT01632163 / Adverse events leading to discontinuation / UNKNOWN
NCT01667900 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01667900 / Gastrointestinal adverse events / UNKNOWN
NCT01667900 / Adverse events leading to discontinuation / UNKNOWN
NCT01720446 / Gastrointestinal adverse events / UNKNOWN
NCT01720446 / Adverse events leading to discontinuation / UNKNOWN
NCT01733758 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01733758 / Gastrointestinal adverse events / UNKNOWN
NCT01733758 / Adverse events leading to discontinuation / UNKNOWN
NCT01744236 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01744236 / Gastrointestinal adverse events / UNKNOWN
NCT01744236 / Adverse events leading to discontinuation / UNKNOWN
NCT01769378 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01769378 / Gastrointestinal adverse events / UNKNOWN
NCT01769378 / Adverse events leading to discontinuation / UNKNOWN
NCT01779362 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01779362 / Gastrointestinal adverse events / UNKNOWN
NCT01779362 / Adverse events leading to discontinuation / UNKNOWN
NCT01798706 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01798706 / Gastrointestinal adverse events / UNKNOWN
NCT01798706 / Adverse events leading to discontinuation / UNKNOWN
NCT01870297 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01870297 / Gastrointestinal adverse events / UNKNOWN
NCT01870297 / Adverse events leading to discontinuation / UNKNOWN
NCT01923181 / 3-point major adverse cardiovascular events / UNKNOWN
NCT01923181 / Gastrointestinal adverse events / UNKNOWN
NCT01923181 / Adverse events leading to discontinuation / UNKNOWN
NCT02020616 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02020616 / Gastrointestinal adverse events / UNKNOWN
NCT02020616 / Adverse events leading to discontinuation / UNKNOWN
NCT02054897 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02054897 / Gastrointestinal adverse events / UNKNOWN
NCT02054897 / Adverse events leading to discontinuation / UNKNOWN
NCT02057172 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02057172 / Gastrointestinal adverse events / UNKNOWN
NCT02057172 / Adverse events leading to discontinuation / UNKNOWN
NCT02113332 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02113332 / Gastrointestinal adverse events / UNKNOWN
NCT02113332 / Adverse events leading to discontinuation / UNKNOWN
NCT02119819 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02119819 / Gastrointestinal adverse events / UNKNOWN
NCT02119819 / Adverse events leading to discontinuation / UNKNOWN
NCT02146079 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02146079 / Gastrointestinal adverse events / UNKNOWN
NCT02146079 / Adverse events leading to discontinuation / UNKNOWN
NCT02152371 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02152371 / Gastrointestinal adverse events / UNKNOWN
NCT02152371 / Adverse events leading to discontinuation / UNKNOWN
NCT02161588 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02161588 / Gastrointestinal adverse events / UNKNOWN
NCT02161588 / Adverse events leading to discontinuation / UNKNOWN
NCT02212067 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02212067 / Gastrointestinal adverse events / UNKNOWN
NCT02212067 / Adverse events leading to discontinuation / UNKNOWN
NCT02229240 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02229240 / Gastrointestinal adverse events / UNKNOWN
NCT02229240 / Adverse events leading to discontinuation / UNKNOWN
NCT02305381 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02305381 / Gastrointestinal adverse events / UNKNOWN
NCT02305381 / Adverse events leading to discontinuation / UNKNOWN
NCT02461589 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02461589 / Gastrointestinal adverse events / UNKNOWN
NCT02461589 / Adverse events leading to discontinuation / UNKNOWN
NCT02472717 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02472717 / Gastrointestinal adverse events / UNKNOWN
NCT02472717 / Adverse events leading to discontinuation / UNKNOWN
NCT02597049 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02597049 / Gastrointestinal adverse events / UNKNOWN
NCT02597049 / Adverse events leading to discontinuation / UNKNOWN
NCT02650206 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02650206 / Gastrointestinal adverse events / UNKNOWN
NCT02650206 / Adverse events leading to discontinuation / UNKNOWN
NCT02692716 / Gastrointestinal adverse events / UNKNOWN
NCT02692716 / Adverse events leading to discontinuation / EXTRACTABLE
NCT02759107 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02759107 / Gastrointestinal adverse events / UNKNOWN
NCT02759107 / Adverse events leading to discontinuation / UNKNOWN
NCT02827708 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02827708 / Gastrointestinal adverse events / UNKNOWN
NCT02827708 / Adverse events leading to discontinuation / UNKNOWN
NCT02863419 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02863419 / Gastrointestinal adverse events / UNKNOWN
NCT02863419 / Adverse events leading to discontinuation / UNKNOWN
NCT02906930 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02906930 / Gastrointestinal adverse events / UNKNOWN
NCT02906930 / Adverse events leading to discontinuation / UNKNOWN
NCT02964247 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02964247 / Gastrointestinal adverse events / UNKNOWN
NCT02964247 / Adverse events leading to discontinuation / UNKNOWN
NCT02973100 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02973100 / Gastrointestinal adverse events / UNKNOWN
NCT02973100 / Adverse events leading to discontinuation / UNKNOWN
NCT02973321 / 3-point major adverse cardiovascular events / UNKNOWN
NCT02973321 / Gastrointestinal adverse events / UNKNOWN
NCT02973321 / Adverse events leading to discontinuation / UNKNOWN
NCT03018028 / 3-point major adverse cardiovascular events / UNKNOWN
NCT03018028 / Gastrointestinal adverse events / UNKNOWN
NCT03018028 / Adverse events leading to discontinuation / UNKNOWN
NCT03021187 / 3-point major adverse cardiovascular events / UNKNOWN
NCT03021187 / Gastrointestinal adverse events / UNKNOWN
NCT03021187 / Adverse events leading to discontinuation / UNKNOWN
NCT03086330 / 3-point major adverse cardiovascular events / UNKNOWN
NCT03086330 / Gastrointestinal adverse events / UNKNOWN
NCT03086330 / Adverse events leading to discontinuation / UNKNOWN
NCT03131687 / 3-point major adverse cardiovascular events / UNKNOWN
NCT03131687 / Gastrointestinal adverse events / UNKNOWN
NCT03131687 / Adverse events leading to discontinuation / UNKNOWN
NCT03144271 / 3-point major adverse cardiovascular events / UNKNOWN
NCT03144271 / Gastrointestinal adverse events / UNKNOWN
NCT03144271 / Adverse events leading to discontinuation / UNKNOWN
NCT03235050 / 3-point major adverse cardiovascular events / UNKNOWN
NCT03235050 / Gastrointestinal adverse events / UNKNOWN
NCT03235050 / Adverse events leading to discontinuation / UNKNOWN
NCT03288740 / 3-point major adverse cardiovascular events / UNKNOWN
NCT03288740 / Gastrointestinal adverse events / UNKNOWN
NCT03288740 / Adverse events leading to discontinuation / UNKNOWN
NCT03353350 / 3-point major adverse cardiovascular events / UNKNOWN
NCT03353350 / Gastrointestinal adverse events / UNKNOWN
NCT03353350 / Adverse events leading to discontinuation / UNKNOWN
NCT03419624 / 3-point major adverse cardiovascular events / UNKNOWN
NCT03419624 / Gastrointestinal adverse events / UNKNOWN
NCT03419624 / Adverse events leading to discontinuation / UNKNOWN
NCT03449654 / 3-point major adverse cardiovascular events / UNKNOWN
NCT03449654 / Gastrointestinal adverse events / UNKNOWN
NCT03449654 / Adverse events leading to discontinuation / UNKNOWN
NCT03496298 / Gastrointestinal adverse events / UNKNOWN
NCT03496298 / Adverse events leading to discontinuation / UNKNOWN
NCT03555994 / 3-point major adverse cardiovascular events / UNKNOWN
NCT03555994 / Gastrointestinal adverse events / UNKNOWN
NCT03555994 / Adverse events leading to discontinuation / UNKNOWN
NCT03713684 / 3-point major adverse cardiovascular events / UNKNOWN
NCT03713684 / Gastrointestinal adverse events / UNKNOWN
NCT03713684 / Adverse events leading to discontinuation / UNKNOWN
NCT03770728 / 3-point major adverse cardiovascular events / UNKNOWN
NCT03770728 / Gastrointestinal adverse events / UNKNOWN
NCT03770728 / Adverse events leading to discontinuation / UNKNOWN
NCT03811561 / 3-point major adverse cardiovascular events / UNKNOWN
NCT03811561 / Gastrointestinal adverse events / UNKNOWN
NCT03811561 / Adverse events leading to discontinuation / UNKNOWN
NCT03819153 / 3-point major adverse cardiovascular events / EXTRACTABLE
NCT03819153 / Gastrointestinal adverse events / UNKNOWN
NCT03819153 / Adverse events leading to discontinuation / UNKNOWN
NCT03914326 / Gastrointestinal adverse events / UNKNOWN
NCT03914326 / Adverse events leading to discontinuation / UNKNOWN
NCT03951753 / 3-point major adverse cardiovascular events / UNKNOWN
NCT03951753 / Gastrointestinal adverse events / UNKNOWN
NCT03951753 / Adverse events leading to discontinuation / UNKNOWN
NCT03985384 / 3-point major adverse cardiovascular events / UNKNOWN
NCT03985384 / Gastrointestinal adverse events / UNKNOWN
NCT03985384 / Adverse events leading to discontinuation / UNKNOWN
NCT04016974 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04016974 / Gastrointestinal adverse events / UNKNOWN
NCT04016974 / Adverse events leading to discontinuation / UNKNOWN
NCT04032197 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04032197 / Gastrointestinal adverse events / UNKNOWN
NCT04032197 / Adverse events leading to discontinuation / UNKNOWN
NCT04057261 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04057261 / Gastrointestinal adverse events / UNKNOWN
NCT04057261 / Adverse events leading to discontinuation / UNKNOWN
NCT04109547 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04109547 / Gastrointestinal adverse events / UNKNOWN
NCT04109547 / Adverse events leading to discontinuation / UNKNOWN
NCT04126603 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04126603 / Gastrointestinal adverse events / UNKNOWN
NCT04126603 / Adverse events leading to discontinuation / UNKNOWN
NCT04143802 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04143802 / Gastrointestinal adverse events / UNKNOWN
NCT04143802 / Adverse events leading to discontinuation / UNKNOWN
NCT04153929 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04153929 / Gastrointestinal adverse events / UNKNOWN
NCT04153929 / Adverse events leading to discontinuation / UNKNOWN
NCT04251156 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04251156 / Gastrointestinal adverse events / UNKNOWN
NCT04251156 / Adverse events leading to discontinuation / EXTRACTABLE
NCT04259801 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04259801 / Gastrointestinal adverse events / UNKNOWN
NCT04259801 / Adverse events leading to discontinuation / UNKNOWN
NCT04515576 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04515576 / Gastrointestinal adverse events / UNKNOWN
NCT04515576 / Adverse events leading to discontinuation / UNKNOWN
NCT04515849 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04515849 / Gastrointestinal adverse events / UNKNOWN
NCT04515849 / Adverse events leading to discontinuation / UNKNOWN
NCT04560998 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04560998 / Gastrointestinal adverse events / UNKNOWN
NCT04560998 / Adverse events leading to discontinuation / UNKNOWN
NCT04591626 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04591626 / Gastrointestinal adverse events / UNKNOWN
NCT04591626 / Adverse events leading to discontinuation / UNKNOWN
NCT04639414 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04639414 / Gastrointestinal adverse events / UNKNOWN
NCT04639414 / Adverse events leading to discontinuation / UNKNOWN
NCT04641312 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04641312 / Gastrointestinal adverse events / UNKNOWN
NCT04641312 / Adverse events leading to discontinuation / UNKNOWN
NCT04741074 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04741074 / Gastrointestinal adverse events / UNKNOWN
NCT04741074 / Adverse events leading to discontinuation / UNKNOWN
NCT04865770 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04865770 / Gastrointestinal adverse events / UNKNOWN
NCT04865770 / Adverse events leading to discontinuation / UNKNOWN
NCT04867785 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04867785 / Gastrointestinal adverse events / UNKNOWN
NCT04867785 / Adverse events leading to discontinuation / UNKNOWN
NCT04892199 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04892199 / Gastrointestinal adverse events / UNKNOWN
NCT04892199 / Adverse events leading to discontinuation / UNKNOWN
NCT04916470 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04916470 / Gastrointestinal adverse events / UNKNOWN
NCT04916470 / Adverse events leading to discontinuation / UNKNOWN
NCT04979130 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04979130 / Gastrointestinal adverse events / UNKNOWN
NCT04979130 / Adverse events leading to discontinuation / UNKNOWN
NCT04982575 / 3-point major adverse cardiovascular events / UNKNOWN
NCT04982575 / Gastrointestinal adverse events / UNKNOWN
NCT04982575 / Adverse events leading to discontinuation / UNKNOWN
NCT05048719 / 3-point major adverse cardiovascular events / UNKNOWN
NCT05048719 / Gastrointestinal adverse events / UNKNOWN
NCT05048719 / Adverse events leading to discontinuation / UNKNOWN
NCT05078255 / 3-point major adverse cardiovascular events / UNKNOWN
NCT05078255 / Gastrointestinal adverse events / UNKNOWN
NCT05078255 / Adverse events leading to discontinuation / UNKNOWN
NCT05144984 / 3-point major adverse cardiovascular events / UNKNOWN
NCT05144984 / Gastrointestinal adverse events / UNKNOWN
NCT05144984 / Adverse events leading to discontinuation / UNKNOWN
NCT05303857 / 3-point major adverse cardiovascular events / UNKNOWN
NCT05303857 / Gastrointestinal adverse events / UNKNOWN
NCT05303857 / Adverse events leading to discontinuation / UNKNOWN
NCT05377333 / 3-point major adverse cardiovascular events / UNKNOWN
NCT05377333 / Gastrointestinal adverse events / UNKNOWN
NCT05377333 / Adverse events leading to discontinuation / UNKNOWN
NCT05407961 / 3-point major adverse cardiovascular events / UNKNOWN
NCT05407961 / Gastrointestinal adverse events / UNKNOWN
NCT05407961 / Adverse events leading to discontinuation / UNKNOWN
NCT05441267 / 3-point major adverse cardiovascular events / UNKNOWN
NCT05441267 / Gastrointestinal adverse events / UNKNOWN
NCT05441267 / Adverse events leading to discontinuation / UNKNOWN
NCT05486065 / 3-point major adverse cardiovascular events / UNKNOWN
NCT05486065 / Gastrointestinal adverse events / UNKNOWN
NCT05486065 / Adverse events leading to discontinuation / UNKNOWN
NCT05649137 / 3-point major adverse cardiovascular events / UNKNOWN
NCT05649137 / Gastrointestinal adverse events / UNKNOWN
NCT05649137 / Adverse events leading to discontinuation / UNKNOWN
NCT05780905 / 3-point major adverse cardiovascular events / UNKNOWN
NCT05780905 / Gastrointestinal adverse events / UNKNOWN
NCT05780905 / Adverse events leading to discontinuation / UNKNOWN
NCT06005012 / 3-point major adverse cardiovascular events / UNKNOWN
NCT06005012 / Gastrointestinal adverse events / UNKNOWN
NCT06005012 / Adverse events leading to discontinuation / UNKNOWN
NCT06042153 / 3-point major adverse cardiovascular events / UNKNOWN
NCT06042153 / Gastrointestinal adverse events / UNKNOWN
NCT06042153 / Adverse events leading to discontinuation / UNKNOWN
NCT06050577 / 3-point major adverse cardiovascular events / UNKNOWN
NCT06050577 / Gastrointestinal adverse events / UNKNOWN
NCT06050577 / Adverse events leading to discontinuation / UNKNOWN
NCT06065540 / 3-point major adverse cardiovascular events / UNKNOWN
NCT06065540 / Gastrointestinal adverse events / UNKNOWN
NCT06065540 / Adverse events leading to discontinuation / UNKNOWN
NCT06131372 / 3-point major adverse cardiovascular events / UNKNOWN
NCT06131372 / Gastrointestinal adverse events / UNKNOWN
NCT06131372 / Adverse events leading to discontinuation / UNKNOWN
NCT06403761 / 3-point major adverse cardiovascular events / UNKNOWN
NCT06403761 / Gastrointestinal adverse events / UNKNOWN
NCT06403761 / Adverse events leading to discontinuation / UNKNOWN
NCT06579105 / 3-point major adverse cardiovascular events / UNKNOWN
NCT06579105 / Gastrointestinal adverse events / UNKNOWN
NCT06579105 / Adverse events leading to discontinuation / UNKNOWN
NCT06797869 / 3-point major adverse cardiovascular events / UNKNOWN
NCT06797869 / Gastrointestinal adverse events / UNKNOWN
NCT06797869 / Adverse events leading to discontinuation / UNKNOWN
NCT06974825 / 3-point major adverse cardiovascular events / UNKNOWN
NCT06974825 / Gastrointestinal adverse events / UNKNOWN
NCT06974825 / Adverse events leading to discontinuation / UNKNOWN
NCT07109700 / 3-point major adverse cardiovascular events / UNKNOWN
NCT07109700 / Gastrointestinal adverse events / UNKNOWN
NCT07109700 / Adverse events leading to discontinuation / UNKNOWN
NCT07112872 / 3-point major adverse cardiovascular events / UNKNOWN
NCT07112872 / Gastrointestinal adverse events / UNKNOWN
NCT07112872 / Adverse events leading to discontinuation / UNKNOWN
NCT07163624 / 3-point major adverse cardiovascular events / UNKNOWN
NCT07163624 / Gastrointestinal adverse events / UNKNOWN
NCT07163624 / Adverse events leading to discontinuation / UNKNOWN
NCT07187856 / 3-point major adverse cardiovascular events / UNKNOWN
NCT07187856 / Gastrointestinal adverse events / UNKNOWN
NCT07187856 / Adverse events leading to discontinuation / UNKNOWN
NCT07415954 / 3-point major adverse cardiovascular events / UNKNOWN
NCT07415954 / Gastrointestinal adverse events / UNKNOWN
NCT07415954 / Adverse events leading to discontinuation / UNKNOWN
NCT07581145 / 3-point major adverse cardiovascular events / UNKNOWN
NCT07581145 / Gastrointestinal adverse events / UNKNOWN
NCT07581145 / Adverse events leading to discontinuation / UNKNOWN
NCT07668388 / 3-point major adverse cardiovascular events / UNKNOWN
NCT07668388 / Gastrointestinal adverse events / UNKNOWN
NCT07668388 / Adverse events leading to discontinuation / UNKNOWN
```

## Offline regeneration

`python scripts/build_families.py all --offline --check` recomputes nodes from held records/config/registry/discovery/retrieval bytes, attaches the held review membership, and compares both families.json and its deterministic gzip evidence sidecar. It writes only temporary comparison outputs. `--offline` without `--check` regenerates the family caches. The full verification separately rebuilds analysis membership from the held source inputs.

```text
balanced-crystalloids-vs-saline-mortality BYTE_IDENTICAL
colchicine-postop-af BYTE_IDENTICAL
colchicine-recurrent-pericarditis BYTE_IDENTICAL
colchicine-secondary-cv-prevention BYTE_IDENTICAL
corticosteroids-cap-mortality BYTE_IDENTICAL
corticosteroids-covid19-mortality BYTE_IDENTICAL
dapagliflozin-hfpef-hosp BYTE_IDENTICAL
denosumab-vertebral-fracture BYTE_IDENTICAL
doac-vte-recurrence BYTE_IDENTICAL
dpp4-mace-t2d BYTE_IDENTICAL
empagliflozin-hfpef-hosp BYTE_IDENTICAL
esketamine-trd-madrs BYTE_IDENTICAL
finerenone-ckd-t2d-renal BYTE_IDENTICAL
glp1-ra-mace-t2d BYTE_IDENTICAL
iv-iron-hfref-hosp BYTE_IDENTICAL
melatonin-primary-insomnia-sol BYTE_IDENTICAL
metformin-pcos-ovulation BYTE_IDENTICAL
noac-vs-warfarin-af-stroke BYTE_IDENTICAL
omega3-cardiovascular-events BYTE_IDENTICAL
pcsk9-mace BYTE_IDENTICAL
probiotics-aad-prevention BYTE_IDENTICAL
sacubitril-valsartan-hfref BYTE_IDENTICAL
semaglutide-obesity-mace BYTE_IDENTICAL
semaglutide-obesity-weight BYTE_IDENTICAL
sglt2-ckd-progression BYTE_IDENTICAL
sglt2-hfref-hosp-cvdeath BYTE_IDENTICAL
sglt2-primary-prevention-hf BYTE_IDENTICAL
spironolactone-hfref-mortality BYTE_IDENTICAL
statins-primary-prevention-elderly BYTE_IDENTICAL
ticagrelor-vs-clopidogrel-acs BYTE_IDENTICAL
tocilizumab-covid19-mortality BYTE_IDENTICAL
tranexamic-acid-pph BYTE_IDENTICAL
Byte-identical family caches: 32 of 32
```

Registry-cache byte preservation is separately checked by `read_compact_registry` → `write_registry`; results are in `.tmp/tf-registry-roundtrip.json`. This is serialization reproducibility, not a fresh acquisition. `scripts/trial_family_registry.py` regenerates registry/query/discovery acquisitions from a real local AACT snapshot. `scripts/build_families.py <slug> --snapshot <snapshot>` verifies all original full-row hashes and reconstructs those rows. That full reconstruction cannot run from the empty AACT directory: the committed compact references intentionally omit non-operational raw columns. The query/discovery caches are frozen acquisition inputs, including their original run timestamp, rather than newly acquired evidence. The copied `docs/trial_family_preservation.json` is inherited candidate evidence, not a source-snapshot audit performed by this lane. No local AACT snapshot was required by a page or offline ledger rebuild.

## Verification ledger

### source-audit

```text
{"checks": 9378, "coverage": {"n": 32, "N": 32, "denominator": "held r3 topic cohort"}, "ambiguous_parent_reports": 24, "review_a_names_linked": 7, "review_a_names_requested": 10}
```

### retractions

```text
pages with every marking kept (count >= base): 32 of 32
```

### ratchet

```text

```

### Full verify_all

Command: `python scripts/verify_all.py` with empty AACT_DIR. Full details: `.tmp/tf-verify-final.log`. An earlier run against superseded code was canceled and is not counted as verification. Cache/audit checks that overlapped the metadata refresh were rerun against frozen final artifacts; the ledger below uses those final results.

```text
PENDING
```

| Piece | Status |
|---|---|
| Ledger, source/absence states, duplicate refusal, missing panel | READY |
| All-outcome numerical preservation | READY |
| Offline cache replay | READY |
| Shared page/claimgraph integration and global ship gates | PENDING |

Global gate failures, if any, must be resolved by the owning integration lane; no gate or ratchet was relaxed. Exact failures are retained in the full log and STUCK_FAILURES.md.

## Candidate hunk ledger

Every candidate tracked-file hunk against its own base `3f8add72` is enumerated below. Family modules/scripts/cache files were transplanted by file copy (inventory `.tmp/tf-copied.json`) then adjusted for this base. No wholesale shared file was copied. TAKEN means the stated family-only lines/concept; all other lines inside that hunk were LEFT. “Reimplemented” entries use the new helper block to satisfy shared-file ownership.

### harness/pipeline.py

| Candidate hunk | Decision |
|---|---|
| `@@ -9,6 +9,8 @@ disclosure-as-control. Class PROCESS, direction optimistic, severity` | LEFT — unrelated candidate changes. |
| `@@ -33,6 +35,7 @@ from . import invalidation as invalidation_mod` | LEFT — unrelated candidate changes. |
| `@@ -546,7 +549,7 @@ def _refresh_cross_source_identity(cross_source, spec, trial_components=None):` | LEFT — unrelated candidate changes. |
| `@@ -613,7 +616,23 @@ def _cross_source(ex, nct, ctgov_results, spec, interv, comp):` | LEFT — unrelated candidate changes. |
| `@@ -997,13 +1016,25 @@ def _apply_trial_annotations(spec, trials):` | LEFT — unrelated candidate changes. |
| `@@ -1081,7 +1112,7 @@ def _build_outcome(spec, kind, included, rec_by_id, interv, comp, ctgov_results=` | LEFT — unrelated candidate changes. |
| `@@ -1093,6 +1124,7 @@ def _build_outcome(spec, kind, included, rec_by_id, interv, comp, ctgov_results=` | LEFT — unrelated candidate changes. |
| `@@ -1104,7 +1136,8 @@ def _build_outcome(spec, kind, included, rec_by_id, interv, comp, ctgov_results=` | LEFT — unrelated candidate changes. |
| `@@ -1193,6 +1226,7 @@ def _build_outcome(spec, kind, included, rec_by_id, interv, comp, ctgov_results=` | LEFT — unrelated candidate changes. |
| `@@ -1211,6 +1245,7 @@ def _build_outcome(spec, kind, included, rec_by_id, interv, comp, ctgov_results=` | LEFT — unrelated candidate changes. |
| `@@ -1225,7 +1260,8 @@ def _build_outcome(spec, kind, included, rec_by_id, interv, comp, ctgov_results=` | LEFT — unrelated candidate changes. |
| `@@ -1345,14 +1381,75 @@ def _build_outcome(spec, kind, included, rec_by_id, interv, comp, ctgov_results=` | LEFT — unrelated candidate changes. |
| `@@ -1407,7 +1504,7 @@ def _build_outcome(spec, kind, included, rec_by_id, interv, comp, ctgov_results=` | LEFT — unrelated candidate changes. |
| `@@ -1419,21 +1516,24 @@ def _build_outcome(spec, kind, included, rec_by_id, interv, comp, ctgov_results=` | LEFT — unrelated candidate changes. |
| `@@ -1514,7 +1614,7 @@ def _build_outcome(spec, kind, included, rec_by_id, interv, comp, ctgov_results=` | LEFT — unrelated candidate changes. |
| `@@ -1529,11 +1629,12 @@ def _build_outcome(spec, kind, included, rec_by_id, interv, comp, ctgov_results=` | LEFT — unrelated candidate changes. |
| `@@ -1591,6 +1692,12 @@ def _build_outcome(spec, kind, included, rec_by_id, interv, comp, ctgov_results=` | LEFT — unrelated candidate changes. |
| `@@ -1648,11 +1755,11 @@ def _ledger_source_status(ledger):` | LEFT — unrelated candidate changes. |
| `@@ -1667,7 +1774,8 @@ def _retrieval_summary(ledger):` | LEFT — unrelated candidate changes. |
| `@@ -1676,9 +1784,25 @@ def _retrieval_summary(ledger):` | LEFT — unrelated candidate changes. |
| `@@ -1706,10 +1830,49 @@ def _source_status(slug, config, records, merged, ledger=None):` | LEFT — unrelated candidate changes. |
| `@@ -1734,6 +1897,8 @@ def build_review_core(slug, config, records, protocol_sha):` | TAKEN — family preparation / attachment only; attachment rebased before dependent sensitivity stamps. |
| `@@ -1755,13 +1920,23 @@ def build_review_core(slug, config, records, protocol_sha):` | LEFT — unrelated candidate changes. |
| `@@ -1816,7 +1991,8 @@ def build_review_core(slug, config, records, protocol_sha):` | LEFT — unrelated candidate changes. |
| `@@ -1903,8 +2079,10 @@ def build_review_core(slug, config, records, protocol_sha):` | LEFT — unrelated candidate changes. |
| `@@ -1936,6 +2114,7 @@ def build_review_core(slug, config, records, protocol_sha):` | TAKEN — family preparation / attachment only; attachment rebased before dependent sensitivity stamps. |
| `@@ -1952,7 +2131,27 @@ def build_review_core(slug, config, records, protocol_sha):` | LEFT — candidate strand/effect-type machinery; family strand links implemented inside ledger helper. |
| `@@ -1984,6 +2183,11 @@ def build_review_core(slug, config, records, protocol_sha):` | LEFT — unrelated candidate changes. |
| `@@ -2062,7 +2266,6 @@ def build_review_core(slug, config, records, protocol_sha):` | LEFT — unrelated candidate changes. |
| `@@ -2071,7 +2274,7 @@ def build_review_core(slug, config, records, protocol_sha):` | LEFT — unrelated candidate changes. |
| `@@ -2095,6 +2298,8 @@ def build_review_core(slug, config, records, protocol_sha):` | LEFT — unrelated candidate changes. |
| `@@ -2116,6 +2321,13 @@ def build_review_core(slug, config, records, protocol_sha):` | LEFT — unrelated candidate changes. |
| `@@ -2127,6 +2339,25 @@ def build_review_core(slug, config, records, protocol_sha):` | LEFT — unrelated candidate changes. |
### harness/identity.py

| Candidate hunk | Decision |
|---|---|
| `@@ -13,6 +13,20 @@ audit-identified report/trial links and are reported, never inferred.` | LEFT — unrelated candidate changes. |
| `@@ -40,7 +54,7 @@ def _ids_of(rec):` | TAKEN — strict registry/DOI/parent links; no scientific-input machinery. |
| `@@ -60,7 +74,23 @@ def build_identities(records):` | TAKEN — strict registry/DOI/parent links; no scientific-input machinery. |
### harness/membership.py

| Candidate hunk | Decision |
|---|---|
| No candidate diff | New family membership fields/refusal added locally; legacy source joins retained. |
### harness/page.py

| Candidate hunk | Decision |
|---|---|
| `@@ -13,6 +13,9 @@ which page is the harness's). Both the harness page and the comparator benchmark` | LEFT — unrelated candidate changes. |
| `@@ -27,6 +30,8 @@ from . import identity as _identity_mod` | LEFT — unrelated candidate changes. |
| `@@ -207,15 +212,9 @@ def _retrieval_mode_label(mode: Any) -> str:` | LEFT — unrelated candidate changes. |
| `@@ -227,27 +226,15 @@ def _retrieval_html(ret: dict) -> str:` | LEFT — unrelated candidate changes. |
| `@@ -283,22 +270,12 @@ def _retrieval_class_html(rc: dict) -> str:` | LEFT — unrelated candidate changes. |
| `@@ -306,15 +283,7 @@ def _search_provenance_html(rc: dict) -> str:` | LEFT — unrelated candidate changes. |
| `@@ -400,69 +369,8 @@ _ROB_SENS_REFUSED_HTML = "<h4>Risk-of-bias sensitivity (re-pooled with the same` | LEFT — unrelated candidate changes. |
| `@@ -501,6 +409,10 @@ def render_strands_section(d: dict) -> str:` | LEFT — unrelated candidate changes. |
| `@@ -510,6 +422,8 @@ def render_strands_section(d: dict) -> str:` | LEFT — unrelated candidate changes. |
| `@@ -521,10 +435,14 @@ def render_strands_section(d: dict) -> str:` | LEFT — unrelated candidate changes. |
| `@@ -534,13 +452,9 @@ def _identifier_scope_block(r):` | LEFT — unrelated candidate changes. |
| `@@ -631,7 +545,27 @@ def _stale_topic_overview(r):` | LEFT — unrelated candidate changes. |
| `@@ -681,7 +615,10 @@ def _overview(r, neutral):` | TAKEN concept, REIMPLEMENTED — family table/count-chain helper; FACT/integrated rendering and all other changes LEFT. |
| `@@ -744,35 +681,7 @@ def _overview(r, neutral):` | LEFT — unrelated candidate changes. |
| `@@ -826,24 +735,11 @@ def _protocol(r, neutral):` | LEFT — unrelated candidate changes. |
| `@@ -852,242 +748,78 @@ def _search(r, neutral):` | TAKEN concept, REIMPLEMENTED — family table/count-chain helper; FACT/integrated rendering and all other changes LEFT. |
| `@@ -1180,30 +912,9 @@ def _alternative_label(alt):` | LEFT — unrelated candidate changes. |
| `@@ -1235,6 +946,11 @@ def _compat_direction_block(o):` | LEFT — unrelated candidate changes. |
| `@@ -1255,7 +971,10 @@ def _trial_inputs(o):` | LEFT — unrelated candidate changes. |
| `@@ -1264,6 +983,7 @@ def _trial_inputs(o):` | LEFT — unrelated candidate changes. |
| `@@ -1427,51 +1147,9 @@ def _trial_inputs(o):` | LEFT — unrelated candidate changes. |
| `@@ -1493,19 +1171,13 @@ def _loo_text(loo):` | LEFT — unrelated candidate changes. |
| `@@ -1514,9 +1186,21 @@ def _outcome_block(o, show_inputs=True, review=None):` | LEFT — unrelated candidate changes. |
| `@@ -1689,7 +1373,7 @@ def _outcome_block(o, show_inputs=True, review=None):` | LEFT — unrelated candidate changes. |
| `@@ -1755,71 +1439,23 @@ def _outcome_block(o, show_inputs=True, review=None):` | LEFT — unrelated candidate changes. |
| `@@ -1830,17 +1466,14 @@ def _outcomes(r, neutral):` | LEFT — unrelated candidate changes. |
| `@@ -1900,394 +1533,60 @@ def _comparator(r, neutral):` | LEFT — unrelated candidate changes. |
| `@@ -2332,283 +1631,8 @@ def _uoa_sensitivity(r, uoa_ids):` | LEFT — unrelated candidate changes. |
| `@@ -2653,37 +1677,70 @@ document.querySelectorAll('nav button').forEach(function(b){b.classList.toggle('` | LEFT — unrelated candidate changes. |
### harness/claimgraph.py

| Candidate hunk | Decision |
|---|---|
| `@@ -14,6 +14,11 @@ import hashlib` | LEFT — unrelated candidate changes. |
| `@@ -48,7 +53,17 @@ def trial_key(trial_dict: dict[str, Any]) -> str:` | TAKEN family-key/alias/count concept in isolated helper block; FACT/claim-graph expansion and other lines LEFT. |
| `@@ -80,13 +95,14 @@ def _trial_inputs(trial: dict[str, Any]) -> dict[str, Any]:` | LEFT — unrelated candidate changes. |
| `@@ -127,11 +143,12 @@ def strand_member_keys(strands_doc: dict[str, Any] / None) -> set[str]:` | LEFT — unrelated candidate changes. |
| `@@ -160,7 +177,7 @@ def attach_strands(review: dict[str, Any], root: str) -> None:` | LEFT — unrelated candidate changes. |
| `@@ -184,6 +201,9 @@ def _strand_names_by_member(strands_doc: dict[str, Any] / None) -> dict[str, lis` | LEFT — unrelated candidate changes. |
| `@@ -234,8 +254,10 @@ def stamp_review(review: dict[str, Any]) -> dict[str, Any]:` | LEFT — unrelated candidate changes. |
| `@@ -256,7 +278,8 @@ def _rob_join_miss(review: dict[str, Any]) -> list[dict[str, Any]]:` | LEFT — unrelated candidate changes. |
| `@@ -287,7 +310,7 @@ def disputes(review: dict[str, Any], registries: dict[str, Any] / None = None) -` | LEFT — unrelated candidate changes. |
| `@@ -306,9 +329,9 @@ def _refused_and_pooled(review: dict[str, Any], registries: dict[str, Any] / Non` | LEFT — unrelated candidate changes. |
| `@@ -383,7 +406,7 @@ def _membership_conflicts(review: dict[str, Any]) -> list[dict[str, Any]]:` | LEFT — unrelated candidate changes. |
| `@@ -475,19 +498,42 @@ def _scan_dependents(review: dict[str, Any]) -> list[dict[str, Any]]:` | LEFT — unrelated candidate changes. |
| `@@ -499,12 +545,12 @@ def _scan_dependents(review: dict[str, Any]) -> list[dict[str, Any]]:` | LEFT — unrelated candidate changes. |
| `@@ -571,3 +617,1028 @@ def check(review: dict[str, Any], registries: dict[str, Any] / None = None) -> l` | TAKEN family-key/alias/count concept in isolated helper block; FACT/claim-graph expansion and other lines LEFT. |
### harness/index.py

| Candidate hunk | Decision |
|---|---|
| `@@ -4,6 +4,8 @@ Scans docs/reviews/*/manifest.json and writes docs/index.html. Deterministic:` | LEFT — unrelated candidate changes. |
| `@@ -14,21 +16,10 @@ from . import parity_relation` | LEFT — unrelated candidate changes. |
| `@@ -69,17 +60,7 @@ def _parity_section(docs_dir: str) -> str:` | LEFT — unrelated candidate changes. |
| `@@ -156,21 +137,9 @@ def _recovery_section(docs_dir: str) -> str:` | LEFT — unrelated candidate changes. |
| `@@ -384,29 +353,15 @@ def _gate_scorecard_section(docs_dir: str) -> str:` | LEFT — unrelated candidate changes. |
| `@@ -478,25 +433,7 @@ def _error_rate_section(docs_dir: str) -> str:` | LEFT — unrelated candidate changes. |
| `@@ -593,21 +530,7 @@ def _crossfamily_section(docs_dir: str) -> str:` | LEFT — unrelated candidate changes. |
| `@@ -682,31 +605,7 @@ def _provenance_section(docs_dir: str) -> str:` | LEFT — unrelated candidate changes. |
| `@@ -726,10 +625,9 @@ def _screen_section(docs_dir: str) -> str:` | LEFT — unrelated candidate changes. |
| `@@ -831,8 +729,7 @@ def _fair_section(docs_dir: str) -> str:` | LEFT — unrelated candidate changes. |
| `@@ -897,7 +794,7 @@ def _prose_derived_numerals(docs_dir: str) -> set:` | LEFT — unrelated candidate changes. |
| `@@ -1076,7 +973,7 @@ def _continuous_section(docs_dir: str) -> str:` | LEFT — unrelated candidate changes. |
| `@@ -1161,112 +1058,8 @@ def build_index(docs_dir: str) -> str:` | LEFT — unrelated candidate changes. |
| Local addition | New family-ledger overview function and one call; candidate index rewrites LEFT. |

## Files changed

```text
LANE-TF-REPORT.md
cache/balanced-crystalloids-vs-saline-mortality/families.evidence.json.gz
cache/balanced-crystalloids-vs-saline-mortality/families.json
cache/balanced-crystalloids-vs-saline-mortality/family_registry.json
cache/balanced-crystalloids-vs-saline-mortality/family_registry.payload.json.gz
cache/balanced-crystalloids-vs-saline-mortality/family_registry.rows.json.gz
cache/colchicine-postop-af/families.evidence.json.gz
cache/colchicine-postop-af/families.json
cache/colchicine-postop-af/family_registry.json
cache/colchicine-postop-af/family_registry.payload.json.gz
cache/colchicine-postop-af/family_registry.rows.json.gz
cache/colchicine-recurrent-pericarditis/families.evidence.json.gz
cache/colchicine-recurrent-pericarditis/families.json
cache/colchicine-recurrent-pericarditis/family_registry.json
cache/colchicine-recurrent-pericarditis/family_registry.payload.json.gz
cache/colchicine-recurrent-pericarditis/family_registry.rows.json.gz
cache/colchicine-secondary-cv-prevention/families.evidence.json.gz
cache/colchicine-secondary-cv-prevention/families.json
cache/colchicine-secondary-cv-prevention/family_registry.json
cache/colchicine-secondary-cv-prevention/family_registry.payload.json.gz
cache/colchicine-secondary-cv-prevention/family_registry.rows.json.gz
cache/corticosteroids-cap-mortality/families.evidence.json.gz
cache/corticosteroids-cap-mortality/families.json
cache/corticosteroids-cap-mortality/family_registry.json
cache/corticosteroids-cap-mortality/family_registry.payload.json.gz
cache/corticosteroids-cap-mortality/family_registry.rows.json.gz
cache/corticosteroids-covid19-mortality/families.evidence.json.gz
cache/corticosteroids-covid19-mortality/families.json
cache/corticosteroids-covid19-mortality/family_registry.json
cache/corticosteroids-covid19-mortality/family_registry.payload.json.gz
cache/corticosteroids-covid19-mortality/family_registry.rows.json.gz
cache/dapagliflozin-hfpef-hosp/families.evidence.json.gz
cache/dapagliflozin-hfpef-hosp/families.json
cache/dapagliflozin-hfpef-hosp/family_registry.json
cache/dapagliflozin-hfpef-hosp/family_registry.payload.json.gz
cache/dapagliflozin-hfpef-hosp/family_registry.rows.json.gz
cache/denosumab-vertebral-fracture/families.evidence.json.gz
cache/denosumab-vertebral-fracture/families.json
cache/denosumab-vertebral-fracture/family_registry.json
cache/denosumab-vertebral-fracture/family_registry.payload.json.gz
cache/denosumab-vertebral-fracture/family_registry.rows.json.gz
cache/doac-vte-recurrence/families.evidence.json.gz
cache/doac-vte-recurrence/families.json
cache/doac-vte-recurrence/family_registry.json
cache/doac-vte-recurrence/family_registry.payload.json.gz
cache/doac-vte-recurrence/family_registry.rows.json.gz
cache/dpp4-mace-t2d/families.evidence.json.gz
cache/dpp4-mace-t2d/families.json
cache/dpp4-mace-t2d/family_registry.json
cache/dpp4-mace-t2d/family_registry.payload.json.gz
cache/dpp4-mace-t2d/family_registry.rows.json.gz
cache/empagliflozin-hfpef-hosp/families.evidence.json.gz
cache/empagliflozin-hfpef-hosp/families.json
cache/empagliflozin-hfpef-hosp/family_registry.json
cache/empagliflozin-hfpef-hosp/family_registry.payload.json.gz
cache/empagliflozin-hfpef-hosp/family_registry.rows.json.gz
cache/esketamine-trd-madrs/families.evidence.json.gz
cache/esketamine-trd-madrs/families.json
cache/esketamine-trd-madrs/family_registry.json
cache/esketamine-trd-madrs/family_registry.payload.json.gz
cache/esketamine-trd-madrs/family_registry.rows.json.gz
cache/finerenone-ckd-t2d-renal/families.evidence.json.gz
cache/finerenone-ckd-t2d-renal/families.json
cache/finerenone-ckd-t2d-renal/family_registry.json
cache/finerenone-ckd-t2d-renal/family_registry.payload.json.gz
cache/finerenone-ckd-t2d-renal/family_registry.rows.json.gz
cache/glp1-ra-mace-t2d/families.evidence.json.gz
cache/glp1-ra-mace-t2d/families.json
cache/glp1-ra-mace-t2d/family_discovery.json
cache/glp1-ra-mace-t2d/family_query.json
cache/glp1-ra-mace-t2d/family_registry.json
cache/glp1-ra-mace-t2d/family_registry.payload.json.gz
cache/glp1-ra-mace-t2d/family_registry.rows.json.gz
cache/iv-iron-hfref-hosp/families.evidence.json.gz
cache/iv-iron-hfref-hosp/families.json
cache/iv-iron-hfref-hosp/family_registry.json
cache/iv-iron-hfref-hosp/family_registry.payload.json.gz
cache/iv-iron-hfref-hosp/family_registry.rows.json.gz
cache/melatonin-primary-insomnia-sol/families.evidence.json.gz
cache/melatonin-primary-insomnia-sol/families.json
cache/melatonin-primary-insomnia-sol/family_registry.json
cache/melatonin-primary-insomnia-sol/family_registry.payload.json.gz
cache/melatonin-primary-insomnia-sol/family_registry.rows.json.gz
cache/metformin-pcos-ovulation/families.evidence.json.gz
cache/metformin-pcos-ovulation/families.json
cache/metformin-pcos-ovulation/family_registry.json
cache/metformin-pcos-ovulation/family_registry.payload.json.gz
cache/metformin-pcos-ovulation/family_registry.rows.json.gz
cache/noac-vs-warfarin-af-stroke/families.evidence.json.gz
cache/noac-vs-warfarin-af-stroke/families.json
cache/noac-vs-warfarin-af-stroke/family_registry.json
cache/noac-vs-warfarin-af-stroke/family_registry.payload.json.gz
cache/noac-vs-warfarin-af-stroke/family_registry.rows.json.gz
cache/omega3-cardiovascular-events/families.evidence.json.gz
cache/omega3-cardiovascular-events/families.json
cache/omega3-cardiovascular-events/family_registry.json
cache/omega3-cardiovascular-events/family_registry.payload.json.gz
cache/omega3-cardiovascular-events/family_registry.rows.json.gz
cache/pcsk9-mace/families.evidence.json.gz
cache/pcsk9-mace/families.json
cache/pcsk9-mace/family_registry.json
cache/pcsk9-mace/family_registry.payload.json.gz
cache/pcsk9-mace/family_registry.rows.json.gz
cache/probiotics-aad-prevention/families.evidence.json.gz
cache/probiotics-aad-prevention/families.json
cache/probiotics-aad-prevention/family_registry.json
cache/probiotics-aad-prevention/family_registry.payload.json.gz
cache/probiotics-aad-prevention/family_registry.rows.json.gz
cache/sacubitril-valsartan-hfref/families.evidence.json.gz
cache/sacubitril-valsartan-hfref/families.json
cache/sacubitril-valsartan-hfref/family_registry.json
cache/sacubitril-valsartan-hfref/family_registry.payload.json.gz
cache/sacubitril-valsartan-hfref/family_registry.rows.json.gz
cache/semaglutide-obesity-mace/families.evidence.json.gz
cache/semaglutide-obesity-mace/families.json
cache/semaglutide-obesity-mace/family_registry.json
cache/semaglutide-obesity-mace/family_registry.payload.json.gz
cache/semaglutide-obesity-mace/family_registry.rows.json.gz
cache/semaglutide-obesity-weight/families.evidence.json.gz
cache/semaglutide-obesity-weight/families.json
cache/semaglutide-obesity-weight/family_registry.json
cache/semaglutide-obesity-weight/family_registry.payload.json.gz
cache/semaglutide-obesity-weight/family_registry.rows.json.gz
cache/sglt2-ckd-progression/families.evidence.json.gz
cache/sglt2-ckd-progression/families.json
cache/sglt2-ckd-progression/family_registry.json
cache/sglt2-ckd-progression/family_registry.payload.json.gz
cache/sglt2-ckd-progression/family_registry.rows.json.gz
cache/sglt2-hfref-hosp-cvdeath/families.evidence.json.gz
cache/sglt2-hfref-hosp-cvdeath/families.json
cache/sglt2-hfref-hosp-cvdeath/family_registry.json
cache/sglt2-hfref-hosp-cvdeath/family_registry.payload.json.gz
cache/sglt2-hfref-hosp-cvdeath/family_registry.rows.json.gz
cache/sglt2-primary-prevention-hf/families.evidence.json.gz
cache/sglt2-primary-prevention-hf/families.json
cache/sglt2-primary-prevention-hf/family_registry.json
cache/sglt2-primary-prevention-hf/family_registry.payload.json.gz
cache/sglt2-primary-prevention-hf/family_registry.rows.json.gz
cache/spironolactone-hfref-mortality/families.evidence.json.gz
cache/spironolactone-hfref-mortality/families.json
cache/spironolactone-hfref-mortality/family_registry.json
cache/spironolactone-hfref-mortality/family_registry.payload.json.gz
cache/spironolactone-hfref-mortality/family_registry.rows.json.gz
cache/statins-primary-prevention-elderly/families.evidence.json.gz
cache/statins-primary-prevention-elderly/families.json
cache/statins-primary-prevention-elderly/family_registry.json
cache/statins-primary-prevention-elderly/family_registry.payload.json.gz
cache/statins-primary-prevention-elderly/family_registry.rows.json.gz
cache/ticagrelor-vs-clopidogrel-acs/families.evidence.json.gz
cache/ticagrelor-vs-clopidogrel-acs/families.json
cache/ticagrelor-vs-clopidogrel-acs/family_registry.json
cache/ticagrelor-vs-clopidogrel-acs/family_registry.payload.json.gz
cache/ticagrelor-vs-clopidogrel-acs/family_registry.rows.json.gz
cache/tocilizumab-covid19-mortality/families.evidence.json.gz
cache/tocilizumab-covid19-mortality/families.json
cache/tocilizumab-covid19-mortality/family_registry.json
cache/tocilizumab-covid19-mortality/family_registry.payload.json.gz
cache/tocilizumab-covid19-mortality/family_registry.rows.json.gz
cache/tranexamic-acid-pph/families.evidence.json.gz
cache/tranexamic-acid-pph/families.json
cache/tranexamic-acid-pph/family_registry.json
cache/tranexamic-acid-pph/family_registry.payload.json.gz
cache/tranexamic-acid-pph/family_registry.rows.json.gz
docs/index.html
docs/m/m0594e053/index.html
docs/m/m078be06c/index.html
docs/m/m0c0e2bf1/index.html
docs/m/m175bd0c3/index.html
docs/m/m22bf81d5/index.html
docs/m/m24cd09bc/index.html
docs/m/m250220c2/index.html
docs/m/m2da64325/index.html
docs/m/m3c1155fb/index.html
docs/m/m5384fd3c/index.html
docs/m/m586876fa/index.html
docs/m/m5b3fd56c/index.html
docs/m/m5e5590d5/index.html
docs/m/m612a48aa/index.html
docs/m/m6dd4233b/index.html
docs/m/m6e7e8ab7/index.html
docs/m/m87167438/index.html
docs/m/m89f8021b/index.html
docs/m/m8db5253b/index.html
docs/m/m979b0810/index.html
docs/m/ma0b91971/index.html
docs/m/maf69923c/index.html
docs/m/mb53e1ed5/index.html
docs/m/mb6ceb13c/index.html
docs/m/mc16cd596/index.html
docs/m/md68c6ad6/index.html
docs/m/mdd4bf0ae/index.html
docs/m/me0751432/index.html
docs/m/me17c0a34/index.html
docs/m/me5d639f4/index.html
docs/m/me79cb3b0/index.html
docs/m/mf6cd36c2/index.html
docs/reviews/balanced-crystalloids-vs-saline-mortality/CERTIFICATE.json
docs/reviews/balanced-crystalloids-vs-saline-mortality/REPRODUCTION.json
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html
docs/reviews/balanced-crystalloids-vs-saline-mortality/manifest.json
docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json
docs/reviews/colchicine-postop-af/CERTIFICATE.json
docs/reviews/colchicine-postop-af/REPRODUCTION.json
docs/reviews/colchicine-postop-af/index.html
docs/reviews/colchicine-postop-af/manifest.json
docs/reviews/colchicine-postop-af/review.json
docs/reviews/colchicine-recurrent-pericarditis/CERTIFICATE.json
docs/reviews/colchicine-recurrent-pericarditis/REPRODUCTION.json
docs/reviews/colchicine-recurrent-pericarditis/index.html
docs/reviews/colchicine-recurrent-pericarditis/manifest.json
docs/reviews/colchicine-recurrent-pericarditis/review.json
docs/reviews/colchicine-secondary-cv-prevention/CERTIFICATE.json
docs/reviews/colchicine-secondary-cv-prevention/REPRODUCTION.json
docs/reviews/colchicine-secondary-cv-prevention/index.html
docs/reviews/colchicine-secondary-cv-prevention/manifest.json
docs/reviews/colchicine-secondary-cv-prevention/review.json
docs/reviews/corticosteroids-cap-mortality/CERTIFICATE.json
docs/reviews/corticosteroids-cap-mortality/REPRODUCTION.json
docs/reviews/corticosteroids-cap-mortality/index.html
docs/reviews/corticosteroids-cap-mortality/manifest.json
docs/reviews/corticosteroids-cap-mortality/review.json
docs/reviews/corticosteroids-covid19-mortality/CERTIFICATE.json
docs/reviews/corticosteroids-covid19-mortality/REPRODUCTION.json
docs/reviews/corticosteroids-covid19-mortality/index.html
docs/reviews/corticosteroids-covid19-mortality/manifest.json
docs/reviews/corticosteroids-covid19-mortality/review.json
docs/reviews/dapagliflozin-hfpef-hosp/CERTIFICATE.json
docs/reviews/dapagliflozin-hfpef-hosp/REPRODUCTION.json
docs/reviews/dapagliflozin-hfpef-hosp/index.html
docs/reviews/dapagliflozin-hfpef-hosp/manifest.json
docs/reviews/dapagliflozin-hfpef-hosp/review.json
docs/reviews/denosumab-vertebral-fracture/CERTIFICATE.json
docs/reviews/denosumab-vertebral-fracture/REPRODUCTION.json
docs/reviews/denosumab-vertebral-fracture/index.html
docs/reviews/denosumab-vertebral-fracture/manifest.json
docs/reviews/denosumab-vertebral-fracture/review.json
docs/reviews/doac-vte-recurrence/CERTIFICATE.json
docs/reviews/doac-vte-recurrence/REPRODUCTION.json
docs/reviews/doac-vte-recurrence/index.html
docs/reviews/doac-vte-recurrence/manifest.json
docs/reviews/doac-vte-recurrence/review.json
docs/reviews/dpp4-mace-t2d/CERTIFICATE.json
docs/reviews/dpp4-mace-t2d/REPRODUCTION.json
docs/reviews/dpp4-mace-t2d/index.html
docs/reviews/dpp4-mace-t2d/manifest.json
docs/reviews/dpp4-mace-t2d/review.json
docs/reviews/empagliflozin-hfpef-hosp/CERTIFICATE.json
docs/reviews/empagliflozin-hfpef-hosp/REPRODUCTION.json
docs/reviews/empagliflozin-hfpef-hosp/index.html
docs/reviews/empagliflozin-hfpef-hosp/manifest.json
docs/reviews/empagliflozin-hfpef-hosp/review.json
docs/reviews/esketamine-trd-madrs/CERTIFICATE.json
docs/reviews/esketamine-trd-madrs/REPRODUCTION.json
docs/reviews/esketamine-trd-madrs/index.html
docs/reviews/esketamine-trd-madrs/manifest.json
docs/reviews/esketamine-trd-madrs/review.json
docs/reviews/finerenone-ckd-t2d-renal/CERTIFICATE.json
docs/reviews/finerenone-ckd-t2d-renal/REPRODUCTION.json
docs/reviews/finerenone-ckd-t2d-renal/index.html
docs/reviews/finerenone-ckd-t2d-renal/manifest.json
docs/reviews/finerenone-ckd-t2d-renal/review.json
docs/reviews/glp1-ra-mace-t2d/CERTIFICATE.json
docs/reviews/glp1-ra-mace-t2d/REPRODUCTION.json
docs/reviews/glp1-ra-mace-t2d/index.html
docs/reviews/glp1-ra-mace-t2d/manifest.json
docs/reviews/glp1-ra-mace-t2d/review.json
docs/reviews/iv-iron-hfref-hosp/CERTIFICATE.json
docs/reviews/iv-iron-hfref-hosp/REPRODUCTION.json
docs/reviews/iv-iron-hfref-hosp/index.html
docs/reviews/iv-iron-hfref-hosp/manifest.json
docs/reviews/iv-iron-hfref-hosp/review.json
docs/reviews/melatonin-primary-insomnia-sol/CERTIFICATE.json
docs/reviews/melatonin-primary-insomnia-sol/REPRODUCTION.json
docs/reviews/melatonin-primary-insomnia-sol/index.html
docs/reviews/melatonin-primary-insomnia-sol/manifest.json
docs/reviews/melatonin-primary-insomnia-sol/review.json
docs/reviews/metformin-pcos-ovulation/CERTIFICATE.json
docs/reviews/metformin-pcos-ovulation/REPRODUCTION.json
docs/reviews/metformin-pcos-ovulation/index.html
docs/reviews/metformin-pcos-ovulation/manifest.json
docs/reviews/metformin-pcos-ovulation/review.json
docs/reviews/noac-vs-warfarin-af-stroke/CERTIFICATE.json
docs/reviews/noac-vs-warfarin-af-stroke/REPRODUCTION.json
docs/reviews/noac-vs-warfarin-af-stroke/index.html
docs/reviews/noac-vs-warfarin-af-stroke/manifest.json
docs/reviews/noac-vs-warfarin-af-stroke/review.json
docs/reviews/omega3-cardiovascular-events/CERTIFICATE.json
docs/reviews/omega3-cardiovascular-events/REPRODUCTION.json
docs/reviews/omega3-cardiovascular-events/index.html
docs/reviews/omega3-cardiovascular-events/manifest.json
docs/reviews/omega3-cardiovascular-events/review.json
docs/reviews/pcsk9-mace/CERTIFICATE.json
docs/reviews/pcsk9-mace/REPRODUCTION.json
docs/reviews/pcsk9-mace/index.html
docs/reviews/pcsk9-mace/manifest.json
docs/reviews/pcsk9-mace/review.json
docs/reviews/probiotics-aad-prevention/CERTIFICATE.json
docs/reviews/probiotics-aad-prevention/REPRODUCTION.json
docs/reviews/probiotics-aad-prevention/index.html
docs/reviews/probiotics-aad-prevention/manifest.json
docs/reviews/probiotics-aad-prevention/review.json
docs/reviews/sacubitril-valsartan-hfref/CERTIFICATE.json
docs/reviews/sacubitril-valsartan-hfref/REPRODUCTION.json
docs/reviews/sacubitril-valsartan-hfref/index.html
docs/reviews/sacubitril-valsartan-hfref/manifest.json
docs/reviews/sacubitril-valsartan-hfref/review.json
docs/reviews/semaglutide-obesity-mace/CERTIFICATE.json
docs/reviews/semaglutide-obesity-mace/REPRODUCTION.json
docs/reviews/semaglutide-obesity-mace/index.html
docs/reviews/semaglutide-obesity-mace/manifest.json
docs/reviews/semaglutide-obesity-mace/review.json
docs/reviews/semaglutide-obesity-weight/CERTIFICATE.json
docs/reviews/semaglutide-obesity-weight/REPRODUCTION.json
docs/reviews/semaglutide-obesity-weight/index.html
docs/reviews/semaglutide-obesity-weight/manifest.json
docs/reviews/semaglutide-obesity-weight/review.json
docs/reviews/sglt2-ckd-progression/CERTIFICATE.json
docs/reviews/sglt2-ckd-progression/REPRODUCTION.json
docs/reviews/sglt2-ckd-progression/index.html
docs/reviews/sglt2-ckd-progression/manifest.json
docs/reviews/sglt2-ckd-progression/review.json
docs/reviews/sglt2-hfref-hosp-cvdeath/CERTIFICATE.json
docs/reviews/sglt2-hfref-hosp-cvdeath/REPRODUCTION.json
docs/reviews/sglt2-hfref-hosp-cvdeath/index.html
docs/reviews/sglt2-hfref-hosp-cvdeath/manifest.json
docs/reviews/sglt2-hfref-hosp-cvdeath/review.json
docs/reviews/sglt2-primary-prevention-hf/CERTIFICATE.json
docs/reviews/sglt2-primary-prevention-hf/REPRODUCTION.json
docs/reviews/sglt2-primary-prevention-hf/index.html
docs/reviews/sglt2-primary-prevention-hf/manifest.json
docs/reviews/sglt2-primary-prevention-hf/review.json
docs/reviews/spironolactone-hfref-mortality/CERTIFICATE.json
docs/reviews/spironolactone-hfref-mortality/REPRODUCTION.json
docs/reviews/spironolactone-hfref-mortality/index.html
docs/reviews/spironolactone-hfref-mortality/manifest.json
docs/reviews/spironolactone-hfref-mortality/review.json
docs/reviews/statins-primary-prevention-elderly/CERTIFICATE.json
docs/reviews/statins-primary-prevention-elderly/REPRODUCTION.json
docs/reviews/statins-primary-prevention-elderly/index.html
docs/reviews/statins-primary-prevention-elderly/manifest.json
docs/reviews/statins-primary-prevention-elderly/review.json
docs/reviews/ticagrelor-vs-clopidogrel-acs/CERTIFICATE.json
docs/reviews/ticagrelor-vs-clopidogrel-acs/REPRODUCTION.json
docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html
docs/reviews/ticagrelor-vs-clopidogrel-acs/manifest.json
docs/reviews/ticagrelor-vs-clopidogrel-acs/review.json
docs/reviews/tocilizumab-covid19-mortality/CERTIFICATE.json
docs/reviews/tocilizumab-covid19-mortality/REPRODUCTION.json
docs/reviews/tocilizumab-covid19-mortality/index.html
docs/reviews/tocilizumab-covid19-mortality/manifest.json
docs/reviews/tocilizumab-covid19-mortality/review.json
docs/reviews/tranexamic-acid-pph/CERTIFICATE.json
docs/reviews/tranexamic-acid-pph/REPRODUCTION.json
docs/reviews/tranexamic-acid-pph/index.html
docs/reviews/tranexamic-acid-pph/manifest.json
docs/reviews/tranexamic-acid-pph/review.json
docs/trial_family_evidence_audit.json
docs/trial_family_held_plants.json
docs/trial_family_preservation.json
docs/trial_family_sweep.json
harness/claimgraph.py
harness/family_compact.py
harness/identity.py
harness/index.py
harness/membership.py
harness/page.py
harness/pipeline.py
harness/trial_family.py
scripts/build_families.py
scripts/trial_family_audit.py
scripts/trial_family_registry.py
scripts/trial_family_sweep.py
tests/test_trial_family.py
tests/test_trial_family_contract.py
tests/test_trial_family_ui.py
```
