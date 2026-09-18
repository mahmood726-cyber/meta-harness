# LANE FX report

HEAD: `237e90946f5b257265b0a3b1c986a8907d12eded`. No commit; no network.

MEASURED: 2 of 2 requested endpoint rows located in held text; 1 of 2 admitted as numeric facts; 1 of 2 refused because the required provenance index has no FLOW record. Both held PDF/text pairs exist in git. FREEDOM hashes match the index; FLOW hashes are measured on disk but cannot be matched to that index.

INFERRED: FLOW cardiovascular MACE is a secondary endpoint: the section explicitly names the kidney/CV-death composite as primary, separately describes cardiovascular MACE, and the table caption distinguishes primary and secondary endpoints. The numeric result is bound only to its own cardiovascular row definition, never to the primary kidney definition.

CLAIMED: no submission, certification, deployment, or portfolio-status change. No Overmind PASS claimed. This is a bounded extraction artefact, not a release.

## Scope and limitations

`NOT_LOCATED` for FLOW is the contract-compatible admission refusal state, not a claim that its text is missing; `span_location_state: LOCATED` and `refusal_scope` disambiguate it. No FLOW effect/count fields are admitted. Repair of the provenance index requires its owner; this lane does not invent a retrieval record or self-certify an expected hash. FREEDOM NCT is NOT_LOCATED (no NCT token in the held document). FLOW analysis set and censoring rule are NOT_STATED_IN_SPAN; no ITT assumption is made.

Offsets are zero-based/end-exclusive in UTF-8 decoded committed bytes with CRLF preserved; byte offsets are also stored. Pages come from the extraction page markers. Result spans deliberately include arm headers to source denominators and arm order. FLOW therefore includes preceding kidney/component rows, but the parser anchors solely on the cardiovascular-composite row.

Helper ownership inspected: `harness/locate.py` is a cached model judgment reader, `harness/fda.py` is a remote acquisition adapter; `harness/verified_source.py` is absent (file search confirmed). Neither existing module locates held-text offsets. Reused `harness.target_endpoint._components_from_text` for definition vocabulary. No shared `heldtext.py` was needed; the small task-specific locator stays in the owned script. The abstract-oriented `bind_result_span` is not applied to an entire mixed-endpoint table; the table parser binds each result to the specific caption subspan or row definition.

## Static versus dynamic disclosure

| Item | Static mechanism or dynamic data |
|---|---|
| Trial labels, file names, caption/row patterns | Static source-selection configuration; no clinical result constants |
| HR, confidence limits, events, denominators | Dynamically parsed from verbatim result span |
| Definitions, NCT, analysis/censoring text | Located in held text; missing information remains explicit |
| Hashes, offsets, PDF pages | Computed from held bytes and page markers |
| Component names | Existing target_endpoint vocabulary applied only to definition span |
| Admission | Deterministic comparison to existing provenance index; missing/mismatching entry refuses values |
| Cross-check | Model proposal consulted after artefact generation; never an extraction input |

## FREEDOM-CVO

State: LOCATED; provenance: MATCH.
PDF SHA-256: `719362393b2029c2d4a081ab1bc69647034b2168efe686808d419f16177f0103`.
Text SHA-256: `e27b9985959e139b9c84f15b7e364d3c82a2fed861819e2b777f6b3f5aef963e`.
NCT: NOT_LOCATED. Components: cardiovascular death, myocardial infarction, stroke.

table: chars [157878, 158097), bytes [158559, 158780), PDF page 58.

```text
Table 19. Time to First Occurrence of 3-Point MACE (CV Death, Nonfatal MI, Nonfatal Stroke) and 4-Point MACE (CV 
Death, Nonfatal MI, Nonfatal Stroke, Unstable Angina) – ITT Population End of Study, FREEDOM (CLP-107) 
```

definition_span: chars [157916, 157969), bytes [158597, 158650), PDF page 58.

```text
3-Point MACE (CV Death, Nonfatal MI, Nonfatal Stroke)
```

result_span: chars [158097, 158320), bytes [158780, 159003), PDF page 58.

```text

MACE Type 
ITCA 650 Number of 
Events/Total No. (%) 
IR (n/100 PY) 
Control Number of 
Events/Total No. (%) 
IR (n/100 PY) HR (95% CI)** 
3-Point MACE* 85/2075 (4.1%) 
2.94 
69/2081 (3.3%) 
2.37 1.24 (0.90, 1.70)
```

analysis_set_span: chars [158049, 158076), bytes [158732, 158759), PDF page 58.

```text
ITT Population End of Study
```

censoring_rule_span: chars [158049, 158076), bytes [158732, 158759), PDF page 58.

```text
ITT Population End of Study
```

Admitted parsed values:

```json
{
  "effect": {
    "scale": "HR",
    "value": 1.24,
    "ci_low": 0.9,
    "ci_high": 1.7
  },
  "counts": {
    "intervention": {
      "events": 85,
      "n": 2075
    },
    "comparator": {
      "events": 69,
      "n": 2081
    }
  }
}
```

Conflicts: no disagreeing candidate in the caption-bounded target table search. Other populations, censoring windows, and four-point endpoints are not interchangeable candidates.

## FLOW

State: NOT_LOCATED; provenance: MISSING_INDEX_RECORD.
PDF SHA-256: `547606a71cf2cee768b1f98848be7ed53c06ea640bc6968f485c0fa3da455c42`.
Text SHA-256: `8882f70933720c2ae710adfe512e8c1cf3a24968f3d7153ece6184af186d068f`.
NCT: NCT03819153. Components: cardiovascular death, myocardial infarction, stroke.

section_span: chars [76064, 76189), bytes [76355, 76480), PDF page 24.

```text
14.3 Kidney Outcomes Trial of OZEMPIC in Adults with Type 2 Diabetes Mellitus and Chronic 
Kidney Disease 
FLOW (NCT03819153)
```

table: chars [79057, 79161), bytes [79354, 79458), PDF page 25.

```text
Table 10: Analyses of the Primary and Secondary Endpoints and their Individual Components in FLOW 
Trial
```

definition_span: chars [79859, 79973), bytes [80160, 80274), PDF page 25.

```text
Composite of cardiovascular death, 
non-fatal myocardial infarction, 
non-fatal stroke (time to first 
occurrence)
```

result_span: chars [79161, 80016), bytes [79458, 80317), PDF page 25.

```text
 
Placebo 
N=1766 (%) 
OZEMPIC 
1 mg 
N=1767 
(%) 
Hazard 
ratio vs 
placebo 
(95% CI)1 
p-value2 
Number of Patients 
(%) 
Composite Endpoint (≥ 50% 
sustained eGFR decline, sustained 
eGFR < 15 mL/min/1.73 m
2 , 
chronic renal replacement therapy, 
or renal or cardiovascular death 
(time to first occurrence)3 
410 (23.2) 331 (18.7) 0.76 (0.66, 
0.88) 0.0003      
≥ 50% sustained eGFR decline3 
213 (12.1) 165 (9.3) 0.73 (0.59, 
0.89) 
Sustained eGFR 
<15mL/min/1.73 m2 3 110 (6.2) 92 (5.2) 0.80 (0.61, 
1.06) 
Chronic renal replacement 
therapy 100 (5.7) 87 (4.9) 0.84 (0.63, 
1.12) 
Renal death 5 (0.3) 5 (0.3) 0.97 (0.27, 
3.49) 
Cardiovascular death 169 (9.6) 123 (7.0) 0.71 (0.56, 
0.89) 
Composite of cardiovascular death, 
non-fatal myocardial infarction, 
non-fatal stroke (time to first 
occurrence) 
254 (14.4) 212 (12.0) 
0.82 (0.68, 
0.98)
```

analysis_set_span: NOT_STATED_IN_SPAN

censoring_rule_span: NOT_STATED_IN_SPAN

primary_endpoint_context_span: chars [77730, 78030), bytes [78023, 78325), PDF page 24.

```text
OZEMPIC was superior to placebo in reducing the incidence of the primary composite endpoint of a sustained 
decline in eGFR of ≥50%, sustained eGFR <15 mL/min/1.73 m2, chronic renal replacement therapy, renal 
death, CV death (HR 0.76 [95% CI 0.66, 0.88], p=0.0003) as shown in Table 10 and Figure 7.
```

Diagnostic parse ONLY; refused for admission because provenance is missing:

```json
{
  "effect": {
    "scale": "HR",
    "value": 0.82,
    "ci_low": 0.68,
    "ci_high": 0.98
  },
  "counts": {
    "intervention": {
      "events": 212,
      "n": 1767
    },
    "comparator": {
      "events": 254,
      "n": 1766
    }
  }
}
```

Conflicts: no disagreeing candidate in the caption-bounded target table search. Other populations, censoring windows, and four-point endpoints are not interchangeable candidates.

## Independent proposal cross-check (after first artefact generation)

Proposal: `.tmp/ref/agy_freedom.txt`; SHA-256 `0fb8bbb65b97789caf17e604151a923324b9e8fa48ce08ae0faa2de0fe1fecda`. This is a model proposal, not source evidence. Every quoted fragment below was searched on its proposed page after whitespace folding only; ellipses split fragments, and each successful hit maps back to held-text character offsets. A failed literal match is disclosed, not treated as a numerical conflict. Abbreviated/reordered quotes need not be verbatim.

| Proposal passage | Held-page quoted fragments located | Missing fragments (proposal text only) |
|---|---|---|
| 1 | 0 of 1;  | `The range of HRs include HR=1.12 (95% CI: 0.84, 1.50) for the pooled analysis of 4-point MACE using “On-Study” censoring, HR=1.24 (95% CI: 0.9, 1.70) for the FREEDOM analysis of 3-point MACE using “On-Study” censoring, HR=1.36 (95% CI: 0.96, 1.92) for the FREEDOM analysis of 3-point MACE using “On-Treatment” censoring` |
| 2 | 1 of 1; [27454, 27685) | None |
| 3 | 1 of 1; [155343, 155641) | None |
| 4 | 1 of 1; [155642, 155781) | None |
| 5 | 2 of 3; [155842, 155933); [156240, 156317) | `ITT Population End of Study, Pooled Analysis of CLP-103, CLP-105, and CLP-107` |
| 6 | 2 of 3; [155842, 155879); [156320, 156396) | `4-Point MACE (CV Death, Nonfatal MI, Nonfatal Stroke, Unstable Angina) – ITT Population End of Study, Pooled Analysis of CLP-103, CLP-105, and CLP-107` |
| 7 | 1 of 1; [157111, 157432) | None |
| 8 | 3 of 3; [157878, 157969); [158049, 158095); [158243, 158320) | None |
| 9 | 3 of 3; [157878, 157915); [157974, 158095); [158323, 158399) | None |
| 10 | 6 of 6; [163475, 163580); [163583, 163594); [163793, 163805); [163808, 163830); [163916, 163941); [164025, 164053) | None |
| 11 | 2 of 6; [163475, 163580); [163793, 163805) | `CVOT FREEDOM`; `Drug, n (%) 85 (4.1)`; `Placebo, n (%) 69 (3.3)`; `HR (95% CI) 1.24 (0.90, 1.70)` |
| 12 | 2 of 6; [163475, 163580); [164199, 164213) | `CVOT FREEDOM`; `Drug, n (%) 95 (4.6)`; `Placebo, n (%) 79 (3.8)`; `HR (95% CI) 1.21 (0.90, 1.63)` |
| 13 | 1 of 1; [166148, 166418) | None |
| 14 | 3 of 3; [166655, 166746); [166826, 166918); [167066, 167140) | None |
| 15 | 3 of 3; [166655, 166692); [166751, 166918); [167143, 167209) | None |
| 16 | 3 of 3; [167830, 167921); [168001, 168051); [168199, 168274) | None |
| 17 | 3 of 3; [167830, 167867); [167926, 168051); [168277, 168349) | None |
| 18 | 3 of 3; [224730, 224821); [224901, 224984); [225132, 225212) | None |
| 19 | 3 of 3; [224730, 224767); [224826, 224984); [225215, 225293) | None |
| 20 | 3 of 3; [225968, 226059); [226139, 226198); [226346, 226424) | None |
| 21 | 3 of 3; [225968, 226005); [226064, 226198); [226427, 226504) | None |

Interpretation: passage 8 agrees with the extracted Table 19 definition, counts, estimate, interval, population and end-of-study window. Passages 1 (FREEDOM on-study clause), 7 (first endpoint), and 11 are corroborating pointers; no numeric disagreement with Table 19 is identified. The proposal calls these a conflict in its final list, but decimal formatting differences are not numeric conflicts. Its pooled-analysis conflicts concern different estimands and are not imported into the FREEDOM-only fact. Passages 2–6, 9–10, and 12–21 concern other endpoints, populations, trials or censoring windows; the table above audits their quoted fragments, not their analytical correctness. The search preserves punctuation and line-end hyphens; it does not reconstruct flattened table columns. There is no FLOW proposal in this file.

## Verification

Initial focused run: 1 failed, 10 passed. Failure was a null `held_in_tree` value in an unrelated provenance record inside the hash-mismatch test fixture. Fixed the fixture to handle null paths; no source data changed. The corruption plants are validated on scratch files while still corrupt, and remain rejected without repairing them.

Final exact test output:

```text
python -m pytest -q -s tests/test_glp1_regulatory_facts.py tests/test_target_endpoint.py
...PLANT one_digit: pre-fix CLI exit=1; stored numeric value differs from parsed result_span
.PLANT no_result_span: pre-fix CLI exit=1; numeric value without result_span
...............
19 passed in 5.18s
```

The universal hash-match requirement is deliberately not claimed: 1 of 2 pairs matches the index; the other is tested to refuse admission. Deterministic regeneration compares complete artefact bytes. No source files, index, workbook, protected harness modules, or git history changed.

