# Comparison-level screening evidence

RETROSPECTIVE: semaglutide-weight review, rule hash `e209c1d5`, 2026-09-28. Decision made by Dispatch under Mahmood's delegation; this is not a prospective protocol amendment.

## Decision and implementation

The eligible STEP 8 contrast is semaglutide versus its MATCHED placebo. Pooled placebo is at most a labelled supportive analysis. These are ALTERNATIVES: one trial never contributes both, and a placebo arm must never be counted in two comparisons in the same analysis. The screening output selects one contrast, not a list of independent effects.

The delegated rationale is that pooling the placebo matched to once-daily liraglutide does not preserve blinding against once-weekly semaglutide. The held registry row names the matched agents but does not contain dosing frequencies; therefore the emitted reason uses only the generic regimen distinction, without inventing frequencies from those bytes. No pooled effect or extraction is generated here.

`harness/arm_parse.py` reads randomized registry interventions or arm-group titles. Publications require explicit alternatives in an allocation sentence; incidental title/background mentions cannot establish arms. The parser deliberately supports a bounded grammar and fails closed for unsupported prose. Registry allocation must explicitly be RANDOMIZED.

`harness/screen.py` suppresses an arm-name population veto only when those arms provide an intervention-of-interest versus configured comparator contrast. A placebo matched to another agent cannot qualify. Other population and design/intervention gates remain active. The second screener uses the same exemption and then applies its OWN gates to the adjusted criteria; it does not call the first screener (review correction: a call into screener 1 would make the two screeners agree by construction on exactly these records). Decisions retain legacy four-value unpacking and expose `.comparison`; `screen.run` copies it to its emitted decision dictionary.

## Measurement

**1 of 4080 held cache entries changed**: 3330 publication-array entries (`records`) and 750 registry-array entries (`ctgov`). Every topic JSON and both arrays of its held cache were enumerated; no deduplication or sampling. No missing caches. The unit is a topic/array/index entry, not a unique trial.

Baseline: `git show c15ed111:harness/screen.py`, loaded with subprocess into a separate package-scoped module. Dependencies remain those of this candidate; existing arm-parser functions were not changed. Change detection compares decision/rule and also counts newly attached comparison metadata. The sweep calls `screen_record` directly, not downstream extraction, dose adjudication, deduplication or release gates. This is not a new release or a claim of downstream poolability.

Served check: read `docs/reviews/<slug>/review.json` using `git show` at `3876a62dca66764dff1b4f84d6b43356a1a9e3bb`. Match complete typed identifiers, including human-prefixed served IDs and trial-family identifiers; an exact raw ID-string match alone would miss STEP 8.

### Every changed record

**SERVED-CHANGE NOTICE: semaglutide-obesity-weight / NCT04074161**

Research Study to Investigate How Well Semaglutide Works Compared to Liraglutide in People Living With Overweight or Obesity

Old: `X2` / `exclude`. New: `INCLUDE` / `include`. Second screener: `include`.

Served row: [{"id": "STEP 8 · NCT04074161", "decision": "exclude", "rule_id": "X2"}]. The served artifact itself has not been edited.

```json
{
  "experimental_arm": "Semaglutide",
  "comparator_arm": "Placebo (semaglutide)",
  "comparator_kind": "MATCHED_PLACEBO",
  "other_arms": [
    "Liraglutide",
    "Placebo (liraglutide)"
  ],
  "pooled_placebo_alternative": {
    "arms": [
      "Placebo (semaglutide)",
      "Placebo (liraglutide)"
    ],
    "state": "NOT_THE_ELIGIBLE_CONTRAST",
    "reason": "pools a placebo matched to a different regimen that is not blinded against the experimental regimen"
  }
}
```

### Denominators by topic and kind

| Topic | records | ctgov |
| --- | ---: | ---: |
| antibiotics-vs-appendectomy-appendicitis | 9 | 9 |
| azithromycin-copd-exacerbation | 83 | 26 |
| balanced-crystalloids-vs-saline-mortality | 14 | 19 |
| colchicine-postop-af | 67 | 6 |
| colchicine-recurrent-pericarditis | 50 | 10 |
| colchicine-secondary-cv-prevention | 95 | 30 |
| corticosteroids-cap-mortality | 112 | 6 |
| corticosteroids-covid19-mortality | 28 | 30 |
| dapagliflozin-hfpef-hosp | 80 | 20 |
| denosumab-vertebral-fracture | 71 | 0 |
| doac-vte-recurrence | 220 | 30 |
| dpp4-mace-t2d | 8 | 30 |
| empagliflozin-hfpef-hosp | 80 | 21 |
| esketamine-trd-madrs | 120 | 30 |
| finerenone-ckd-t2d-renal | 5 | 21 |
| glp1-ra-mace-t2d | 11 | 1 |
| hfnc-vs-conventional-o2-reintubation | 150 | 30 |
| iv-iron-hfref-hosp | 31 | 9 |
| melatonin-primary-insomnia-sol | 120 | 8 |
| metformin-pcos-ovulation | 125 | 30 |
| noac-vs-warfarin-af-stroke | 6 | 30 |
| omega3-cardiovascular-events | 86 | 30 |
| pcsk9-mace | 9 | 3 |
| probiotics-aad-prevention | 449 | 30 |
| prone-positioning-ards-mortality | 150 | 30 |
| sacubitril-valsartan-hfref | 57 | 30 |
| semaglutide-obesity-mace | 64 | 2 |
| semaglutide-obesity-weight | 120 | 30 |
| sglt2-ckd-progression | 5 | 30 |
| sglt2-hfref-hosp-cvdeath | 4 | 14 |
| sglt2-primary-prevention-hf | 300 | 30 |
| spironolactone-hfref-mortality | 221 | 7 |
| statins-primary-prevention-elderly | 6 | 23 |
| ticagrelor-vs-clopidogrel-acs | 30 | 2 |
| tocilizumab-covid19-mortality | 20 | 30 |
| tranexamic-acid-pph | 54 | 30 |
| vitamin-d-acute-respiratory-infection | 150 | 30 |
| zinc-common-cold-duration | 120 | 3 |

609 records with a population-veto match and unreadable randomized arms remain excluded. Each is listed by topic, ID, title, array index, matched term and final rule in `measurement.json` under `unreadable_arms_excluded`. This includes records rejected earlier by X1; it is not a count of missed eligible comparisons. Existing inclusions without arm-dependent population vetoes are outside this fail-closed exception.

## Static versus dynamic disclosure

| Item | Static or dynamic | Basis |
| --- | --- | --- |
| Retrospective date, rule hash, delegation, matched-versus-pooled decision | Static | Explicit task decision; not inferred research results |
| Arm grammar, token matching, comparator selection and one-contrast policy | Static | General rules implemented before corpus measurement; no topic/ID-specific rescue list |
| STEP 8 ID, allocation, masking, conditions and arm names | Dynamic | Held `cache/semaglutide-obesity-weight/records.json`; regression fixture reads these bytes |
| Eligibility decisions, comparison labels, denominators and changed IDs | Dynamic | All held topic/cache entries evaluated by old and new screeners |
| Served status and served decision | Dynamic | Requested historical git object; prefixed IDs checked |
| Synthetic negative and portable-drug plants | Static test-only | Explicit SYNTHETIC IDs; never added to measurement or real outputs |

## Validation and reproduction

Run from the repository root:

```text
python evidence/comparison_screening/measure.py
python -m pytest -q tests/test_comparison_screening.py tests/test_screen_contrast_and_ledger.py tests/test_screen_entry.py tests/test_screen_no_outcome_axis.py tests/test_screen_span.py -p no:cacheprovider
```

Plants load pre-fix `screen.py` using read-only `git show`: STEP 8 is X2 before and included after, with its matched comparison. A liraglutide-only trial (including liraglutide-treated obesity conditions) remains excluded; type 2 diabetes remains X2 even with a liraglutide arm. Additional tests cover unrandomized/unreadable arms, wrong matched placebo, absent comparator, publication allocation evidence, other design gates, generic drug names, served-ID normalization and emitted comparison metadata.

The sparse worktree lacked three existing test inputs: `docs/study_families.json`, `docs/screening_delta.json`, and `docs/contrast_evictions.json`. They were materialized byte-for-byte with read-only `git show HEAD:<path>` inside this worktree; no git write command was used. No full-suite run, network fetch, push, deployment or portfolio-status update was performed.

Final validation: **39 passed** across the new comparison tests and all four `tests/test_screen*.py` files. `git diff --check` passed. Measurement totals, current source hashes, served identifier and selected arm labels were checked against the held evidence.
