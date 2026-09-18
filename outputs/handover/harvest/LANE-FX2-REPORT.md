# LANE FX2 report

HEAD: `237e90946f5b257265b0a3b1c986a8907d12eded`. No commit; no network.

MEASURED: 1 of 1 requested target definitions, 2 of 2 primary-analysis result passages, and 1 of 1 on-treatment table rows located. 2 of 2 ELIXA PDF/text digests match the required provenance index. The raw-text digest was computed before decoding/any normalization; extraction preserves CRLF. The locator-only artefact `.tmp/elixa-located-before-provenance.json` was produced before consulting the ELIXA provenance index or either proposal. The final artefact applies required provenance admission.

INFERRED: the requested three-point target is the secondary MACE endpoint, not the trial primary MACE+ endpoint. The source explicitly classifies it as secondary. The on-study table and adjacent ITT prose refer to the same target; the general methods span defines on-study follow-up through the common study end date, including treatment discontinuation. The adjacent prose does not itself restate censoring, so its censoring_rule_span remains NOT_STATED_IN_SPAN.

CLAIMED: bounded offline extraction only; no release, submission, certification, pooling, or portfolio-status change. No protected harness modules, source files, index, workbook, or original FX report changed.

## Static versus dynamic disclosure

| Item | Static configuration | Dynamic evidence |
|---|---|---|
| Selection | Trial/file labels, caption/row regexes, endpoint vocabulary | Unique source matches; missing/ambiguous required matches fail closed |
| Results | No clinical result constants | Effects and counts parsed from held spans; prose denominators explicitly absent |
| Provenance | Existing index path | SHA-256 over raw PDF/text bytes compared to index |
| Locations | Zero-based, end-exclusive convention | Character/UTF-8 byte offsets; PDF pages from extraction markers |
| Conflict | Exact comparison without rounding; only shared numeric count fields compared | Differing fields computed from independently parsed passages |
| Proposal audit | Whitespace-only folding, ellipsis splitting | Post-generation substring matching; never seeds extraction |

## Provenance and comparison

State: CONFLICT; source: FDA_NDA208471_StatR_2016; provenance: MATCH.
PDF SHA-256: `cf2b3ef92247b85e7be7c3b56c3cc4fc0af007b3950acee95eea9c995653db38`.
Raw text SHA-256: `952b8088e14b457d97364f13bb0f9407803bf875faed5fa30d995972e2687a26`.
Mechanical differing fields: `["ci_low", "ci_high"]`. No top-level effect is present.
The lower-bound discrepancy is retained under exact comparison as requested; no rounding-based reconciliation is attempted. Matching estimates and event counts do not resolve the interval conflict.

## Located evidence

definition_span: chars [34512, 34703), bytes [34567, 34758), PDF page 16 (end page 16).

```text
MACE, a composite endpoint defined as 
cardiovascular death, non-fatal myocardial infarction, or non-fatal stroke, as adjudicated by the 
cardiovascular events adjudication committee (CAC).
```

endpoint_role_span: chars [34709, 34850), bytes [34764, 34905), PDF page 16 (end page 16).

```text
Secondary endpoints include alternate composites of cardiovascular outcomes, MACE and all-
cause mortality, and other exploratory endpoints.
```

Components: cardiovascular death, myocardial infarction, stroke.

### conflicts / 1: table

Parsed values:
```json
{
  "effect": {
    "scale": "HR",
    "value": 1.02,
    "ci_low": 0.89,
    "ci_high": 1.18
  },
  "counts": {
    "intervention": {
      "events": 400,
      "n": 3034
    },
    "comparator": {
      "events": 392,
      "n": 3034
    }
  }
}
```

table: chars [48566, 48605), bytes [48634, 48673), PDF page 24 (end page 24).

```text
Table 8: Analysis of the MACE Endpoint 
```

row_span: chars [48683, 48785), bytes [48751, 48853), PDF page 24 (end page 24).

```text
MACE endpoint (on-study) 1.02 
(0.89, 1.18) 
 No. of patients with event (%) 392 (12.9%) 400 (13.2%)
```

result_span: chars [48605, 48785), bytes [48673, 48853), PDF page 24 (end page 24).

```text

 Placebo 
(N=3,034) 
Lixisenatide 
(N=3,034) 
Hazard ratio 
(95% CI) 
MACE endpoint (on-study) 1.02 
(0.89, 1.18) 
 No. of patients with event (%) 392 (12.9%) 400 (13.2%)
```

analysis_label_span: chars [48698, 48706), bytes [48766, 48774), PDF page 24 (end page 24).

```text
on-study
```

analysis_set_span: chars [47847, 48013), bytes [47915, 48081), PDF page 24 (end page 24).

```text
ITT analyses (on-study and on-treatment) of MACE, defined as cardiovascular death, non-fatal 
MI, and non-fatal stroke, are consistent with those of MACE+ (Table 8).
```

censoring_rule_span: chars [35142, 35605), bytes [35197, 35660), PDF page 16 (end page 16).

```text
The primary analysis population is intent to treat (ITT) and the events considered are on study. 
ITT is defined as all randomized subjects, that have a subject number and a treatment kit number 
allocated to them based on the randomization scheme. Using an on study analysis, cardiovascular 
events contributing to the analysis include those occurring from randomization to the common 
study end date, even if a subject has discontinued randomized treatment.
```

### conflicts / 2: text

Parsed values:
```json
{
  "effect": {
    "scale": "HR",
    "value": 1.02,
    "ci_low": 0.887,
    "ci_high": 1.172
  },
  "counts": {
    "intervention": {
      "events": 400,
      "n": "NOT_STATED_IN_SPAN"
    },
    "comparator": {
      "events": 392,
      "n": "NOT_STATED_IN_SPAN"
    }
  }
}
```

result_span: chars [48149, 48359), bytes [48217, 48427), PDF page 24 (end page 24).

```text
For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and 
lixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, 
1.172) with a point estimate of 1.02.
```

analysis_set_span: chars [48149, 48165), bytes [48217, 48233), PDF page 24 (end page 24).

```text
For ITT analysis
```

censoring_rule_span: NOT_STATED_IN_SPAN.

analysis_context_span: chars [35142, 35605), bytes [35197, 35660), PDF page 16 (end page 16).

```text
The primary analysis population is intent to treat (ITT) and the events considered are on study. 
ITT is defined as all randomized subjects, that have a subject number and a treatment kit number 
allocated to them based on the randomization scheme. Using an on study analysis, cardiovascular 
events contributing to the analysis include those occurring from randomization to the common 
study end date, even if a subject has discontinued randomized treatment.
```

### other_analyses / 1: table

Parsed values:
```json
{
  "effect": {
    "scale": "HR",
    "value": 1.01,
    "ci_low": 0.87,
    "ci_high": 1.17
  },
  "counts": {
    "intervention": {
      "events": 334,
      "n": 3034
    },
    "comparator": {
      "events": 342,
      "n": 3034
    }
  }
}
```

table: chars [48566, 48605), bytes [48634, 48673), PDF page 24 (end page 24).

```text
Table 8: Analysis of the MACE Endpoint 
```

row_span: chars [48851, 48957), bytes [48919, 49025), PDF page 24 (end page 24).

```text
MACE endpoint (on-treatment) 1.01 
(0.87, 1.17) 
 No. of patients with event (%) 342 (11.3%) 334 (11.0%)
```

result_span: chars [48605, 48957), bytes [48673, 49025), PDF page 24 (end page 24).

```text

 Placebo 
(N=3,034) 
Lixisenatide 
(N=3,034) 
Hazard ratio 
(95% CI) 
MACE endpoint (on-study) 1.02 
(0.89, 1.18) 
 No. of patients with event (%) 392 (12.9%) 400 (13.2%) 
 Total Person Year 6340.2 6368.7 
 Incidence Rate 6.18 6.28 
MACE endpoint (on-treatment) 1.01 
(0.87, 1.17) 
 No. of patients with event (%) 342 (11.3%) 334 (11.0%)
```

analysis_label_span: chars [48866, 48878), bytes [48934, 48946), PDF page 24 (end page 24).

```text
on-treatment
```

analysis_set_span: chars [47847, 48013), bytes [47915, 48081), PDF page 24 (end page 24).

```text
ITT analyses (on-study and on-treatment) of MACE, defined as cardiovascular death, non-fatal 
MI, and non-fatal stroke, are consistent with those of MACE+ (Table 8).
```

censoring_rule_span: chars [36814, 36962), bytes [36869, 37017), PDF page 16 (end page 16).

```text
The on-treatment period for CV 
endpoints is defined as the time from randomization up to 30 days after the last injection of 
randomized product.
```

### additional_passages / 1: summary_text

Parsed values:
```json
{
  "effect": {
    "scale": "HR",
    "value": 1.02,
    "ci_low": 0.89,
    "ci_high": 1.17
  },
  "counts": {
    "intervention": {
      "events": 400,
      "n": "NOT_STATED_IN_SPAN"
    },
    "comparator": {
      "events": 392,
      "n": "NOT_STATED_IN_SPAN"
    }
  }
}
```

result_span: chars [16863, 17167), bytes [16875, 17179), PDF page 7 (end page 7).

```text
There were 792 secondary MACE events observed in the study for the ITT population, 400 in 
the lixisenatide group and 392 in the placebo group. The pre-specified Cox proportional hazards 
analysis resulted in a hazard ratio estimate of 1.02 with an associated 95% confidence interval of 
(0.89, 1.17).
```

analysis_set_span: chars [16863, 16944), bytes [16875, 16956), PDF page 7 (end page 7).

```text
There were 792 secondary MACE events observed in the study for the ITT population
```

censoring_rule_span: NOT_STATED_IN_SPAN.

The on-treatment result_span retains the preceding arm headers and on-study row; the parser accepts only the terminal on-treatment row. Its row_span isolates that row. The executive-summary result is an additional same-target passage, with its own comparison to the table; it is not misclassified as a different analysis.

## Post-generation proposal cross-check

Proposal: `.tmp/ref/agy_elixa.txt`. Each quoted fragment is searched only on its proposed PDF page. Whitespace is folded for this audit only; all reported offsets map back to unchanged raw text.

| Passage | PDF page | Located fragments | Not located fragments |
|---|---|---|---|
| 1 | 7 | 1 of 2; chars [16424, 16583) | `In the 6068 randomized subjects, a total of 805 primary MACE+ events were included in the pre-specified final analysis on the intention-to-treat (ITT) population` |
| 2 | 7 | 1 of 1; chars [16863, 17167) | None |
| 3 | 8 | 2 of 2; chars [20052, 20223); chars [20253, 20473) | None |
| 4 | 9 | 1 of 1; chars [20524, 20757) | None |
| 5 | 22 | 2 of 2; chars [45772, 45915); chars [46067, 46207) | None |
| 6 | 22 | 1 of 1; chars [46216, 46456) | None |
| 7 | 23 | 1 of 1; chars [47237, 47600) | None |
| 8 | 24 | 3 of 3; chars [47847, 48012); chars [48149, 48244); chars [48260, 48359) | None |
| 9 | 24 | 1 of 1; chars [48566, 48785) | None |
| 10 | 24 | 1 of 1; chars [48851, 48992) | None |
| 11 | 35 | 1 of 1; chars [64454, 64752) | None |
| 12 | 36 | 0 of 1;  | `The pre-specified Cox proportional hazards model for the primary MACE+ endpoint (cardiovascular death, non-fatal myocardial infarction, and non-fatal ischemic stroke, and hospitalization for unstable angina) estimated a hazard ratio of 1.02 with an associated 95% confidence interval of (0.89, 1.17).` |
| 13 | 92 | 1 of 1; chars [165551, 165765) | None |

MEASURED: 16 of 18 proposal fragments located with the stated exact-after-whitespace-folding rule.

The ELX report describes eight handover spans on PDF pages 7, 8, 22, 24 and 35. The fragment audit above checks these source regions independently. The target table and adjacent result are on page 24; the executive summary is on page 7. The locator binds the fuller definition on page 16, while the proposal also quotes the shorter definition on page 24. MACE+ regions are audit-only, not imported as three-point facts. This is a region cross-check, not a claim to have independently replayed all eight handover records; those records are not extraction inputs.

## Not located / limitations

No NCT identifier was located by this bounded locator. No trial-primary three-point endpoint definition is located: the source calls MACE secondary. Denominators and censoring rules are NOT_STATED_IN_SPAN in the nearby prose and executive summary. Proposal fragments listed as not located above are not repaired or used as evidence. The search is bounded to these source formats, not an exhaustive semantic audit of every passage. PDF page numbers come from held extraction markers; no independent PDF rendering is claimed. Existing FLOW provenance refusal remains unchanged.

## Verification

Command: `python -m pytest -q -s tests/test_glp1_regulatory_facts.py tests/test_target_endpoint.py`.

The first FX2 focused run passed. Corruption plants are validated from still-corrupt scratch artefacts before any repair. Tests cover byte-identical regeneration, all nested spans/values, hash-mismatch refusal, conflict rejection, and the agreeing-passages branch.

```text
...PLANT one_digit: pre-fix CLI exit=1; stored numeric value differs from parsed result_span
.PLANT no_result_span: pre-fix CLI exit=1; numeric value without result_span
..........PLANT conflict_effect: pre-fix CLI exit=1; CONFLICT must omit top-level effect
.PLANT identical_conflicts: pre-fix CLI exit=1; CONFLICT requires differing parsed values
.PLANT table_digit: pre-fix CLI exit=1; stored numeric value differs from parsed result_span
.PLANT text_digit: pre-fix CLI exit=1; stored numeric value differs from parsed result_span
.........
26 passed in 11.05s
```

