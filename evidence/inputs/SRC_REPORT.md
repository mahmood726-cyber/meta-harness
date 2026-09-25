# Lane SRC — held-source recovery

Status: complete. Audit-only artefacts; no production files changed, no commit or push.

Scope: the 23 of 46 served trial-outcome rows that lane UA classified as UNLOCATED. Unit: page × outcome name × exact served trial ID. Literal recovery does not establish endpoint validity, source authenticity beyond the held cache, or admission safety.

Baseline: `9ff4c6b07275b737aafb198cdab85ad3fae8058c`. `ua.json` SHA256: `e268341a48a6e324310e33e14d7a8916671cafea250b7b74afb226bc7b8d6d31`. Every target row is compared to its current served review JSON before analysis.

## Priority: ADMISSIBLE rows

The 2 of 23 target rows marked ADMISSIBLE are reported first, in full. Their recorded build verdict evaluates only P5/P8; P1/P2/P3 are explicitly not evaluated. Recovery here does not update those verdicts.

### UA-021 — PMID 31189511 — 3-point major adverse cardiovascular events

Page: `glp1-ra-mace-t2d`. Served row: `docs/reviews/glp1-ra-mace-t2d/review.json#/outcomes/0/trials/4`. Admission: `ADMISSIBLE`.

Source kind: `REPORTED_TEXT`; recovery: `LOCATED_REPORTED_RESULT`.

ADMISSIBLE evaluates family eligibility and endpoint binding; the stored verdict explicitly does not evaluate P1_source_bytes/P2_span_located/P3_effect_tokens_in_span. Raw source now recovered in this audit only.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| effect | `0·88` | 0.88 | A07 | A06 |  |
| ci_low | `0·79` | 0.79 | A08 | A06 |  |
| ci_high | `0·99` | 0.99 | A09 | A06 |  |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/extract.py::_effect_from_match",
  "source_sha256": "c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50",
  "scale": "HR",
  "effect": 0.88,
  "ci_low": 0.79,
  "ci_high": 0.99,
  "parameters": {
    "normalization": "harness/extract.py::_norm",
    "round_digits": null
  },
  "effect_delta": 0.0,
  "reported_tuple_exact": true,
  "formula": "Read reported point/CI from the located sentence after explicitly recorded decimal normalization; no count reconstruction.",
  "yi": -0.12783337150988489,
  "vi": 0.003314356141013421,
  "standard_error": 0.057570445030531256,
  "served_effect": 0.88,
  "served_standard_error": 0.057570445030531256,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.88",
  "effect_hex": "0x1.c28f5c28f5c29p-1",
  "served_effect_hex": "0x1.c28f5c28f5c29p-1"
}
```

Normalization: `harness/extract.py::_norm`, file SHA256 `c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50`. Changed: True. The following normalized form is a transformation, not a quotation:

```text
During a median follow-up of 5.4 years (IQR 5.1-5.9), the primary composite outcome occurred in 594 (12.0%) participants at an incidence rate of 2.4 per 100 person-years in the dulaglutide group and in 663 (13.4%) participants at an incidence rate of 2.7 per 100 person-years in the placebo group (hazard ratio [HR] 0.88, 95% CI 0.79-0.99; p=0.026).
```

Control: `{"name": "REWIND raw versus normalized positive control", "scope": "cache/glp1-ra-mace-t2d/records.json#/records/4/abstract", "raw_find": 1704, "normalized_find": -1, "normalization_exactly_matches_served_endpoint_span": true, "raw_match_anchor": "A06"}`

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/glp1-ra-mace-t2d/records.json#/records/4/id`; SHA256 `1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750`; file characters [12016,12026), bytes [12024,12034).

```text
"31189511"
```

**A02 — source identity nct**: `cache/glp1-ra-mace-t2d/records.json#/records/4/nct`; SHA256 `1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750`; file characters [15052,15065), bytes [15087,15100).

```text
"NCT01394952"
```

**A03 — source identity doi**: `cache/glp1-ra-mace-t2d/records.json#/records/4/doi`; SHA256 `1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750`; file characters [15009,15040), bytes [15044,15075).

```text
"10.1016/S0140-6736(19)31149-3"
```

**A04 — source identity year**: `cache/glp1-ra-mace-t2d/records.json#/records/4/year`; SHA256 `1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750`; file characters [14967,14973), bytes [15002,15008).

```text
"2019"
```

**A05 — source identity title**: `cache/glp1-ra-mace-t2d/records.json#/records/4/title`; SHA256 `1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750`; file characters [12062,12185), bytes [12070,12193).

```text
"Dulaglutide and cardiovascular outcomes in type 2 diabetes (REWIND): a double-blind, randomised placebo-controlled trial."
```

**A06 — source sentence**: `cache/glp1-ra-mace-t2d/records.json#/records/4/abstract`; SHA256 `1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750`; file characters [13907,14256), bytes [13922,14282). Decoded-string characters [1704,2053).

```text
During a median follow-up of 5·4 years (IQR 5·1-5·9), the primary composite outcome occurred in 594 (12·0%) participants at an incidence rate of 2·4 per 100 person-years in the dulaglutide group and in 663 (13·4%) participants at an incidence rate of 2·7 per 100 person-years in the placebo group (hazard ratio [HR] 0·88, 95% CI 0·79-0·99; p=0·026).
```

**A07 — raw numerical token effect**: `cache/glp1-ra-mace-t2d/records.json#/records/4/abstract`; SHA256 `1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750`; file characters [14223,14227), bytes [14245,14250). Decoded-string characters [2020,2024).

```text
0·88
```

**A08 — raw numerical token ci_low**: `cache/glp1-ra-mace-t2d/records.json#/records/4/abstract`; SHA256 `1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750`; file characters [14236,14240), bytes [14259,14264). Decoded-string characters [2033,2037).

```text
0·79
```

**A09 — raw numerical token ci_high**: `cache/glp1-ra-mace-t2d/records.json#/records/4/abstract`; SHA256 `1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750`; file characters [14241,14245), bytes [14265,14270). Decoded-string characters [2038,2042).

```text
0·99
```

### UA-039 — PMID 31535829 — Composite cardiovascular death or hospitalisation for heart failure

Page: `sglt2-hfref-hosp-cvdeath`. Served row: `docs/reviews/sglt2-hfref-hosp-cvdeath/review.json#/outcomes/0/trials/0`. Admission: `ADMISSIBLE`.

Source kind: `REPORTED_REGISTRY_CELLS`; recovery: `LOCATED_REPORTED_RESULT`.

Registry: `NCT03036124`, outcome index 1 (zero-based), `/ctgov_results/NCT03036124/1`; Subjects Included in the Composite Endpoint of CV Death or Hospitalization Due to Heart Failure..

Analysis index 0; raw analysis group IDs `["OG001"]`. Outcome groups: OG000 = Dapa 10 mg, OG001 = Placebo.

ADMISSIBLE despite no byte/span/effect-token predicates evaluated; generated prose is not a quotation. Cite the three structured cells and analysis object.

The outcome table has OG000 (Dapa 10 mg) and OG001 (Placebo), but analyses[0].groupIds is exactly [OG001]. Do not silently replace it with two group IDs. The numerical tuple is located; contrast orientation requires independent adjudication if two-group analysis membership is mandatory.

Selected registry outcome index 1 is SECONDARY and names CV death or HF hospitalization; do not substitute the broader primary worsening-HF composite from outcome index 0.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| effect | `0.75` | 0.75 | A13 | A14 |  |
| ci_low | `0.65` | 0.65 | A15 | A16 |  |
| ci_high | `0.85` | 0.85 | A17 | A18 |  |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "JSON pointer selection + float parsing (no derived HR)",
  "scale": "HR",
  "effect": 0.75,
  "ci_low": 0.65,
  "ci_high": 0.85,
  "effect_delta": 0.0,
  "reported_tuple_exact": true,
  "yi": -0.2876820724517809,
  "vi": 0.004683478976527634,
  "standard_error": 0.06843594798443019,
  "served_effect": 0.75,
  "served_standard_error": 0.06843594798443019,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.75",
  "effect_hex": "0x1.8000000000000p-1",
  "served_effect_hex": "0x1.8000000000000p-1"
}
```

Control: `{"name": "generated-sentence absence in the selected literal file only", "scope": "cache/sglt2-hfref-hosp-cvdeath/records.json", "query": "ClinicalTrials.gov results (structured target endpoint): outcome 'Subjects Included in the Composite Endpoint of CV Death or Hospitalization Due to Heart Failure.' HR 0.75 (95% CI 0.65 to 0.85); endpoint counts 382/2373 (Dapa 10 mg) vs 495/2371 (Placebo)", "found": -1, "positive_control_anchor": "A19", "positive_control_fires": true}`

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/records/0/id`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [268,278), bytes [268,278).

```text
"31535829"
```

**A02 — source identity nct**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/records/0/nct`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [2969,2982), bytes [2969,2982).

```text
"NCT03036124"
```

**A03 — source identity doi**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/records/0/doi`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [2931,2954), bytes [2931,2954).

```text
"10.1056/NEJMoa1911303"
```

**A04 — source identity year**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/records/0/year`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [2877,2883), bytes [2877,2883).

```text
"2019"
```

**A05 — source identity title**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/records/0/title`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [320,397), bytes [320,397).

```text
"Dapagliflozin in Patients with Heart Failure and Reduced Ejection Fraction."
```

**A06 — registry context title**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/title`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [33117,33215), bytes [33290,33388).

```text
"Subjects Included in the Composite Endpoint of CV Death or Hospitalization Due to Heart Failure."
```

**A07 — registry context type**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/type`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [33087,33098), bytes [33260,33271).

```text
"SECONDARY"
```

**A08 — registry context timeFrame**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/timeFrame`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [33398,33418), bytes [33571,33591).

```text
"Up to 27.8 months."
```

**A09 — registry context paramType**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/paramType`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [33311,33334), bytes [33484,33507).

```text
"COUNT_OF_PARTICIPANTS"
```

**A10 — registry context unitOfMeasure**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/unitOfMeasure`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [33361,33375), bytes [33534,33548).

```text
"Participants"
```

**A11 — group identity**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/groups/0`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [33450,33613), bytes [33623,33786).

```text
{
            "id": "OG000",
            "title": "Dapa 10 mg",
            "description": "Dapagliflozin 10 mg tablets administered orally once daily"
          }
```

**A12 — group identity**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/groups/1`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [33625,33802), bytes [33798,33975).

```text
{
            "id": "OG001",
            "title": "Placebo",
            "description": "Placebo tablet to match dapagliflozin 10 mg, given once daily per oral use."
          }
```

**A13 — raw input effect**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/analyses/0/paramValue`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [35032,35038), bytes [35205,35211).

```text
"0.75"
```

**A14 — input cell context effect**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/analyses/0`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [34590,35154), bytes [34763,35327).

```text
{
            "groupIds": [
              "OG001"
            ],
            "nonInferiorityType": "SUPERIORITY",
            "pValue": "<0.0001",
            "statisticalMethod": "Regression, Cox",
            "statisticalComment": "Stratified by Type 2 Diabetes status at randomization and including the history of hospitalizations due to Heart failure as a factor.",
            "paramType": "Hazard Ratio (HR)",
            "paramValue": "0.75",
            "ciPctValue": "95",
            "ciLowerLimit": "0.65",
            "ciUpperLimit": "0.85"
          }
```

**A15 — raw input ci_low**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/analyses/0/ciLowerLimit`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [35100,35106), bytes [35273,35279).

```text
"0.65"
```

**A16 — input cell context ci_low**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/analyses/0`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [34590,35154), bytes [34763,35327).

```text
{
            "groupIds": [
              "OG001"
            ],
            "nonInferiorityType": "SUPERIORITY",
            "pValue": "<0.0001",
            "statisticalMethod": "Regression, Cox",
            "statisticalComment": "Stratified by Type 2 Diabetes status at randomization and including the history of hospitalizations due to Heart failure as a factor.",
            "paramType": "Hazard Ratio (HR)",
            "paramValue": "0.75",
            "ciPctValue": "95",
            "ciLowerLimit": "0.65",
            "ciUpperLimit": "0.85"
          }
```

**A17 — raw input ci_high**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/analyses/0/ciUpperLimit`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [35136,35142), bytes [35309,35315).

```text
"0.85"
```

**A18 — input cell context ci_high**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/analyses/0`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [34590,35154), bytes [34763,35327).

```text
{
            "groupIds": [
              "OG001"
            ],
            "nonInferiorityType": "SUPERIORITY",
            "pValue": "<0.0001",
            "statisticalMethod": "Regression, Cox",
            "statisticalComment": "Stratified by Type 2 Diabetes status at randomization and including the history of hospitalizations due to Heart failure as a factor.",
            "paramType": "Hazard Ratio (HR)",
            "paramValue": "0.75",
            "ciPctValue": "95",
            "ciLowerLimit": "0.65",
            "ciUpperLimit": "0.85"
          }
```

**A19 — reported HR analysis object**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/analyses/0`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [34590,35154), bytes [34763,35327).

```text
{
            "groupIds": [
              "OG001"
            ],
            "nonInferiorityType": "SUPERIORITY",
            "pValue": "<0.0001",
            "statisticalMethod": "Regression, Cox",
            "statisticalComment": "Stratified by Type 2 Diabetes status at randomization and including the history of hospitalizations due to Heart failure as a factor.",
            "paramType": "Hazard Ratio (HR)",
            "paramValue": "0.75",
            "ciPctValue": "95",
            "ciLowerLimit": "0.65",
            "ciUpperLimit": "0.85"
          }
```

**A20 — analysis paramType**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/analyses/0/paramType`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [34985,35004), bytes [35158,35177).

```text
"Hazard Ratio (HR)"
```

**A21 — analysis ciPctValue**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/analyses/0/ciPctValue`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [35066,35070), bytes [35239,35243).

```text
"95"
```

**A22 — analysis statisticalMethod**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/analyses/0/statisticalMethod`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [34770,34787), bytes [34943,34960).

```text
"Regression, Cox"
```

**A23 — analysis statisticalComment**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/analyses/0/statisticalComment`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [34823,34958), bytes [34996,35131).

```text
"Stratified by Type 2 Diabetes status at randomization and including the history of hospitalizations due to Heart failure as a factor."
```

**A24 — analysis groupIds**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/analyses/0/groupIds`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [34616,34653), bytes [34789,34826).

```text
[
              "OG001"
            ]
```

**A25 — endpoint counts context; not used to calculate reported HR**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/denoms`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [33832,34143), bytes [34005,34316).

```text
[
          {
            "units": "Participants",
            "counts": [
              {
                "groupId": "OG000",
                "value": "2373"
              },
              {
                "groupId": "OG001",
                "value": "2371"
              }
            ]
          }
        ]
```

**A26 — endpoint counts context; not used to calculate reported HR**: `cache/sglt2-hfref-hosp-cvdeath/records.json#/ctgov_results/NCT03036124/1/classes`; SHA256 `1b8317d41dcb9f5ccfab12def62e359ef3238c6dfd290b7f9cfe1640efea7826`; file characters [34164,34556), bytes [34337,34729).

```text
[
          {
            "categories": [
              {
                "measurements": [
                  {
                    "groupId": "OG000",
                    "value": "382"
                  },
                  {
                    "groupId": "OG001",
                    "value": "495"
                  }
                ]
              }
            ]
          }
        ]
```

## Other target rows

### UA-001 — PMID 32720823 — Postoperative atrial fibrillation

Page: `colchicine-postop-af`. Served row: `docs/reviews/colchicine-postop-af/review.json#/outcomes/0/trials/0`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `COUNT_DERIVED_RR`; recovery: `LOCATED_FULL_INPUT_SET`.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| ai | `13` | 13 | A08 | A06 | intervention |
| ci | `13` | 13 | A09 | A06 | comparator |
| n1i | `81` | 81 | A10 | A07 | intervention |
| n2i | `71` | 71 | A11 | A07 | comparator |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/synth.py::Study.yi_vi",
  "source_sha256": "735d9793ed5e28119be22390e73daea3c74732291c3279687abc8cc3028532dc",
  "formula": "RR = (ai/n1i)/(ci/n2i); variance(log RR) = 1/ai - 1/n1i + 1/ci - 1/n2i; no zero-cell correction triggered",
  "parameters": {
    "measure": "RR",
    "zero_cell_correction_applied": false
  },
  "scale": "RR",
  "yi": -0.13176927763112345,
  "vi": 0.12741596779155465,
  "standard_error": 0.35695373340470143,
  "effect": 0.8765432098765431,
  "effect_delta": 0.0,
  "served_effect": 0.8765432098765431,
  "served_standard_error": 0.35695373340470143,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.8765432098765431",
  "effect_hex": "0x1.c0ca4587e6b74p-1",
  "served_effect_hex": "0x1.c0ca4587e6b74p-1"
}
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/colchicine-postop-af/records.json#/records/30/id`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [67461,67471), bytes [67691,67701).

```text
"32720823"
```

**A02 — source identity nct**: `cache/colchicine-postop-af/records.json#/records/30/nct`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [69353,69366), bytes [69597,69610).

```text
"NCT03015831"
```

**A03 — source identity doi**: `cache/colchicine-postop-af/records.json#/records/30/doi`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [69312,69338), bytes [69556,69582).

```text
"10.1177/0300060520939832"
```

**A04 — source identity year**: `cache/colchicine-postop-af/records.json#/records/30/year`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [69257,69263), bytes [69501,69507).

```text
"2020"
```

**A05 — source identity title**: `cache/colchicine-postop-af/records.json#/records/30/title`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [67513,67639), bytes [67743,67869).

```text
"Effect of Low-dose ColchiciNe on the InciDence of Atrial Fibrillation in Open Heart Surgery Patients: END-AF Low Dose Trial."
```

**A06 — source sentence**: `cache/colchicine-postop-af/records.json#/records/30/abstract`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [68604,68766), bytes [68844,69010). Decoded-string characters [944,1106).

```text
POAF occurred in 13 patients (16.1%) in the colchicine group and 13 patients (18.3%) in the placebo group (odds ratio 0.85 [95% Confidence Interval = 0.37-1.99]).
```

**A07 — source sentence**: `cache/colchicine-postop-af/records.json#/records/30/abstract`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [68049,68368), bytes [68279,68606). Decoded-string characters [389,708).

```text
METHODS: In this prospective, randomized, double-blind, placebo-controlled study, consecutive adult patients admitted for elective cardiac surgeries randomly received a 1-mg dose of colchicine (n = 81) or placebo (n = 71) orally 12 to 24 hours before surgery followed by a daily dose of 0.5 mg until hospital discharge.
```

**A08 — raw input ai**: `cache/colchicine-postop-af/records.json#/records/30/abstract`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [68621,68623), bytes [68861,68863). Decoded-string characters [961,963).

```text
13
```

**A09 — raw input ci**: `cache/colchicine-postop-af/records.json#/records/30/abstract`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [68669,68671), bytes [68909,68911). Decoded-string characters [1009,1011).

```text
13
```

**A10 — raw input n1i**: `cache/colchicine-postop-af/records.json#/records/30/abstract`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [68247,68249), bytes [68481,68483). Decoded-string characters [587,589).

```text
81
```

**A11 — raw input n2i**: `cache/colchicine-postop-af/records.json#/records/30/abstract`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [68267,68269), bytes [68505,68507). Decoded-string characters [607,609).

```text
71
```

### UA-002 — PMID 25172965 — Postoperative atrial fibrillation

Page: `colchicine-postop-af`. Served row: `docs/reviews/colchicine-postop-af/review.json#/outcomes/0/trials/1`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `COUNT_DERIVED_RR`; recovery: `LOCATED_FULL_INPUT_SET`.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| ai | `61` | 61 | A08 | A06 | intervention |
| ci | `75` | 75 | A09 | A06 | comparator |
| n1i | `180` | 180 | A10 | A07 | intervention |
| n2i | `180` | 180 | A11 | A07 | comparator |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/synth.py::Study.yi_vi",
  "source_sha256": "735d9793ed5e28119be22390e73daea3c74732291c3279687abc8cc3028532dc",
  "formula": "RR = (ai/n1i)/(ci/n2i); variance(log RR) = 1/ai - 1/n1i + 1/ci - 1/n2i; no zero-cell correction triggered",
  "parameters": {
    "measure": "RR",
    "zero_cell_correction_applied": false
  },
  "scale": "RR",
  "yi": -0.20661424936299916,
  "vi": 0.01861566484517304,
  "standard_error": 0.13643923499189314,
  "effect": 0.8133333333333334,
  "effect_delta": 0.0,
  "served_effect": 0.8133333333333334,
  "served_standard_error": 0.13643923499189314,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.8133333333333334",
  "effect_hex": "0x1.a06d3a06d3a07p-1",
  "served_effect_hex": "0x1.a06d3a06d3a07p-1"
}
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/colchicine-postop-af/records.json#/records/37/id`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [82549,82559), bytes [82859,82869).

```text
"25172965"
```

**A02 — source identity nct**: `cache/colchicine-postop-af/records.json#/records/37/nct`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [85996,86009), bytes [86316,86329).

```text
"NCT01552187"
```

**A03 — source identity doi**: `cache/colchicine-postop-af/records.json#/records/37/doi`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [85956,85981), bytes [86276,86301).

```text
"10.1001/jama.2014.11026"
```

**A04 — source identity year**: `cache/colchicine-postop-af/records.json#/records/37/year`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [85910,85916), bytes [86230,86236).

```text
"2014"
```

**A05 — source identity title**: `cache/colchicine-postop-af/records.json#/records/37/title`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [82601,82737), bytes [82911,83047).

```text
"Colchicine for prevention of postpericardiotomy syndrome and postoperative atrial fibrillation: the COPPS-2 randomized clinical trial."
```

**A06 — source sentence**: `cache/colchicine-postop-af/records.json#/records/37/abstract`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [84407,85028), bytes [84723,85344). Decoded-string characters [1649,2270).

```text
There were no significant differences between the colchicine and placebo groups for the secondary end points of postoperative AF (colchicine, 61 patients [33.9%]; placebo, 75 patients [41.7%]; absolute difference, 7.8%; 95% CI, -2.2% to 17.6%) or postoperative pericardial/pleural effusion (colchicine, 103 patients [57.2%]; placebo, 106 patients [58.9%]; absolute difference, 1.7%; 95% CI, -8.5% to 11.7%), although there was a reduction in postoperative AF in the prespecified on-treatment analysis (placebo, 61/148 patients [41.2%]; colchicine, 38/141 patients [27.0%]; absolute difference, 14.2%; 95% CI, 3.3%-24.7%).
```

**A07 — source sentence**: `cache/colchicine-postop-af/records.json#/records/37/abstract`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [83738,83994), bytes [84048,84306). Decoded-string characters [980,1236).

```text
INTERVENTIONS: Patients were randomized to receive placebo (n=180) or colchicine (0.5 mg twice daily in patients ≥70 kg or 0.5 mg once daily in patients <70 kg; n=180) starting between 48 and 72 hours before surgery and continued for 1 month after surgery.
```

**A08 — raw input ai**: `cache/colchicine-postop-af/records.json#/records/37/abstract`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [84549,84551), bytes [84865,84867). Decoded-string characters [1791,1793).

```text
61
```

**A09 — raw input ci**: `cache/colchicine-postop-af/records.json#/records/37/abstract`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [84579,84581), bytes [84895,84897). Decoded-string characters [1821,1823).

```text
75
```

**A10 — raw input n1i**: `cache/colchicine-postop-af/records.json#/records/37/abstract`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [83901,83904), bytes [84213,84216). Decoded-string characters [1143,1146).

```text
180
```

**A11 — raw input n2i**: `cache/colchicine-postop-af/records.json#/records/37/abstract`; SHA256 `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`; file characters [83800,83803), bytes [84110,84113). Decoded-string characters [1042,1045).

```text
180
```

### UA-003 — PMID 24694983 — Recurrent pericarditis

Page: `colchicine-recurrent-pericarditis`. Served row: `docs/reviews/colchicine-recurrent-pericarditis/review.json#/outcomes/0/trials/0`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `REPORTED_TEXT`; recovery: `LOCATED_REPORTED_RESULT`.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| effect | `0·49` | 0.49 | A07 | A06 |  |
| ci_low | `0·24` | 0.24 | A08 | A06 |  |
| ci_high | `0·65` | 0.65 | A09 | A06 |  |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/extract.py::_effect_from_match",
  "source_sha256": "c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50",
  "scale": "RR",
  "effect": 0.49,
  "ci_low": 0.24,
  "ci_high": 0.65,
  "parameters": {
    "normalization": "harness/extract.py::_norm",
    "round_digits": null
  },
  "effect_delta": 0.0,
  "reported_tuple_exact": true,
  "formula": "Read reported point/CI from the located sentence after explicitly recorded decimal normalization; no count reconstruction.",
  "yi": -0.7133498878774648,
  "vi": 0.06460308238977577,
  "standard_error": 0.25417136422062925,
  "served_effect": 0.49,
  "served_standard_error": 0.25417136422062925,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.49",
  "effect_hex": "0x1.f5c28f5c28f5cp-2",
  "served_effect_hex": "0x1.f5c28f5c28f5cp-2"
}
```

Normalization: `harness/extract.py::_norm`, file SHA256 `c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50`. Changed: True. The following normalized form is a transformation, not a quotation:

```text
The proportion of patients who had recurrent pericarditis was 26 (21.6%) of 120 in the colchicine group and 51 (42.5%) of 120 in the placebo group (relative risk 0.49; 95% CI 0.24-0.65; p=0.0009; number needed to treat 5).
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/colchicine-recurrent-pericarditis/records.json#/records/38/id`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [89811,89821), bytes [90048,90058).

```text
"24694983"
```

**A02 — source identity nct**: `cache/colchicine-recurrent-pericarditis/records.json#/records/38/nct`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [92443,92456), bytes [92690,92703).

```text
"NCT00235079"
```

**A03 — source identity doi**: `cache/colchicine-recurrent-pericarditis/records.json#/records/38/doi`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [92397,92428), bytes [92644,92675).

```text
"10.1016/S0140-6736(13)62709-9"
```

**A04 — source identity year**: `cache/colchicine-recurrent-pericarditis/records.json#/records/38/year`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [92349,92355), bytes [92596,92602).

```text
"2014"
```

**A05 — source identity title**: `cache/colchicine-recurrent-pericarditis/records.json#/records/38/title`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [89863,90029), bytes [90100,90266).

```text
"Efficacy and safety of colchicine for treatment of multiple recurrences of pericarditis (CORP-2): a multicentre, double-blind, placebo-controlled, randomised trial."
```

**A06 — source sentence**: `cache/colchicine-recurrent-pericarditis/records.json#/records/38/abstract`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [91122,91344), bytes [91363,91591). Decoded-string characters [1072,1294).

```text
The proportion of patients who had recurrent pericarditis was 26 (21·6%) of 120 in the colchicine group and 51 (42·5%) of 120 in the placebo group (relative risk 0·49; 95% CI 0·24-0·65; p=0·0009; number needed to treat 5).
```

**A07 — raw numerical token effect**: `cache/colchicine-recurrent-pericarditis/records.json#/records/38/abstract`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [91284,91288), bytes [91527,91532). Decoded-string characters [1234,1238).

```text
0·49
```

**A08 — raw numerical token ci_low**: `cache/colchicine-recurrent-pericarditis/records.json#/records/38/abstract`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [91297,91301), bytes [91541,91546). Decoded-string characters [1247,1251).

```text
0·24
```

**A09 — raw numerical token ci_high**: `cache/colchicine-recurrent-pericarditis/records.json#/records/38/abstract`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [91302,91306), bytes [91547,91552). Decoded-string characters [1252,1256).

```text
0·65
```

### UA-004 — PMID 21873705 — Recurrent pericarditis

Page: `colchicine-recurrent-pericarditis`. Served row: `docs/reviews/colchicine-recurrent-pericarditis/review.json#/outcomes/0/trials/1`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `RRR_COMPLEMENT`; recovery: `LOCATED_FULL_INPUT_SET`.

The source reports RRR; the served derivation label is reported, but complementing and reversing bounds is a computation.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| RRR | `0.56` | 0.56 | A07 | A06 |  |
| RRR_lower | `0.27` | 0.27 | A08 | A06 |  |
| RRR_upper | `0.73` | 0.73 | A09 | A06 |  |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/extract.py::_effect_from_match",
  "source_sha256": "c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50",
  "scale": "RR",
  "effect": 0.44,
  "ci_low": 0.27,
  "ci_high": 0.73,
  "parameters": {
    "normalization": "harness/extract.py::_norm",
    "round_digits": 4
  },
  "effect_delta": 0.0,
  "reported_tuple_exact": true,
  "formula": "RR = 1-RRR; lower = 1-RRR_upper; upper = 1-RRR_lower; round each to 4 decimals",
  "before_producer_rounding": {
    "effect": 0.43999999999999995,
    "ci_low": 0.27,
    "ci_high": 0.73
  },
  "pre_round_effect_exact": false,
  "yi": -0.8209805520698302,
  "vi": 0.06438140516155855,
  "standard_error": 0.25373491119977665,
  "served_effect": 0.44,
  "served_standard_error": 0.25373491119977665,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.44",
  "effect_hex": "0x1.c28f5c28f5c29p-2",
  "served_effect_hex": "0x1.c28f5c28f5c29p-2"
}
```

Normalization: `harness/extract.py::_norm`, file SHA256 `c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50`. Changed: False. The following normalized form is a transformation, not a quotation:

```text
RESULTS: At 18 months, the recurrence rate was 24% in the colchicine group and 55% in the placebo group (absolute risk reduction, 0.31 [95% CI, 0.13 to 0.46]; relative risk reduction, 0.56 [CI, 0.27 to 0.73]; number needed to treat, 3 [CI, 2 to 7]).
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/id`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [103540,103550), bytes [103813,103823).

```text
"21873705"
```

**A02 — source identity nct**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/nct`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [105721,105734), bytes [105994,106007).

```text
"NCT00128414"
```

**A03 — source identity doi**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/doi`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [105665,105706), bytes [105938,105979).

```text
"10.7326/0003-4819-155-7-201110040-00359"
```

**A04 — source identity year**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/year`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [105609,105615), bytes [105882,105888).

```text
"2011"
```

**A05 — source identity title**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/title`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [103592,103659), bytes [103865,103932).

```text
"Colchicine for recurrent pericarditis (CORP): a randomized trial."
```

**A06 — source sentence**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/abstract`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [104687,104936), bytes [104960,105209). Decoded-string characters [1007,1256).

```text
RESULTS: At 18 months, the recurrence rate was 24% in the colchicine group and 55% in the placebo group (absolute risk reduction, 0.31 [95% CI, 0.13 to 0.46]; relative risk reduction, 0.56 [CI, 0.27 to 0.73]; number needed to treat, 3 [CI, 2 to 7]).
```

**A07 — raw numerical token RRR**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/abstract`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [104871,104875), bytes [105144,105148). Decoded-string characters [1191,1195).

```text
0.56
```

**A08 — raw numerical token RRR_lower**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/abstract`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [104881,104885), bytes [105154,105158). Decoded-string characters [1201,1205).

```text
0.27
```

**A09 — raw numerical token RRR_upper**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/abstract`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [104889,104893), bytes [105162,105166). Decoded-string characters [1209,1213).

```text
0.73
```

### UA-005 — PMID 21873705 — Symptom persistence at 72 hours

Page: `colchicine-recurrent-pericarditis`. Served row: `docs/reviews/colchicine-recurrent-pericarditis/review.json#/outcomes/1/trials/0`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `RRR_COMPLEMENT`; recovery: `LOCATED_FULL_INPUT_SET`.

The source reports RRR; the served derivation label is reported, but complementing and reversing bounds is a computation.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| RRR | `0.56` | 0.56 | A07 | A06 |  |
| RRR_lower | `0.27` | 0.27 | A08 | A06 |  |
| RRR_upper | `0.74` | 0.74 | A09 | A06 |  |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/extract.py::_effect_from_match",
  "source_sha256": "c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50",
  "scale": "RR",
  "effect": 0.44,
  "ci_low": 0.26,
  "ci_high": 0.73,
  "parameters": {
    "normalization": "harness/extract.py::_norm",
    "round_digits": 4
  },
  "effect_delta": 0.0,
  "reported_tuple_exact": true,
  "formula": "RR = 1-RRR; lower = 1-RRR_upper; upper = 1-RRR_lower; round each to 4 decimals",
  "before_producer_rounding": {
    "effect": 0.43999999999999995,
    "ci_low": 0.26,
    "ci_high": 0.73
  },
  "pre_round_effect_exact": false,
  "yi": -0.8209805520698302,
  "vi": 0.06935992376198645,
  "standard_error": 0.26336272280257594,
  "served_effect": 0.44,
  "served_standard_error": 0.26336272280257594,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.44",
  "effect_hex": "0x1.c28f5c28f5c29p-2",
  "served_effect_hex": "0x1.c28f5c28f5c29p-2"
}
```

Normalization: `harness/extract.py::_norm`, file SHA256 `c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50`. Changed: False. The following normalized form is a transformation, not a quotation:

```text
Colchicine reduced the persistence of symptoms at 72 hours (absolute risk reduction, 0.30 [CI, 0.13 to 0.45]; relative risk reduction, 0.56 [CI, 0.27 to 0.74]) and mean number of recurrences, increased the remission rate at 1 week, and prolonged the time to subsequent recurrence.
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/id`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [103540,103550), bytes [103813,103823).

```text
"21873705"
```

**A02 — source identity nct**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/nct`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [105721,105734), bytes [105994,106007).

```text
"NCT00128414"
```

**A03 — source identity doi**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/doi`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [105665,105706), bytes [105938,105979).

```text
"10.7326/0003-4819-155-7-201110040-00359"
```

**A04 — source identity year**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/year`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [105609,105615), bytes [105882,105888).

```text
"2011"
```

**A05 — source identity title**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/title`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [103592,103659), bytes [103865,103932).

```text
"Colchicine for recurrent pericarditis (CORP): a randomized trial."
```

**A06 — source sentence**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/abstract`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [104937,105217), bytes [105210,105490). Decoded-string characters [1257,1537).

```text
Colchicine reduced the persistence of symptoms at 72 hours (absolute risk reduction, 0.30 [CI, 0.13 to 0.45]; relative risk reduction, 0.56 [CI, 0.27 to 0.74]) and mean number of recurrences, increased the remission rate at 1 week, and prolonged the time to subsequent recurrence.
```

**A07 — raw numerical token RRR**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/abstract`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [105072,105076), bytes [105345,105349). Decoded-string characters [1392,1396).

```text
0.56
```

**A08 — raw numerical token RRR_lower**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/abstract`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [105082,105086), bytes [105355,105359). Decoded-string characters [1402,1406).

```text
0.27
```

**A09 — raw numerical token RRR_upper**: `cache/colchicine-recurrent-pericarditis/records.json#/records/44/abstract`; SHA256 `69b0f26fee0d411d6b88904e8ce95d43a6a1ab97bec06a48089326c456d32d78`; file characters [105090,105094), bytes [105363,105367). Decoded-string characters [1410,1414).

```text
0.74
```

### UA-006 — PMID 31733140 — Trial-defined major coronary/cardiovascular composite

Page: `colchicine-secondary-cv-prevention`. Served row: `docs/reviews/colchicine-secondary-cv-prevention/review.json#/outcomes/0/trials/0`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `REPORTED_TEXT`; recovery: `LOCATED_REPORTED_RESULT`.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| effect | `0.77` | 0.77 | A07 | A06 |  |
| ci_low | `0.61` | 0.61 | A08 | A06 |  |
| ci_high | `0.96` | 0.96 | A09 | A06 |  |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/extract.py::_effect_from_match",
  "source_sha256": "c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50",
  "scale": "HR",
  "effect": 0.77,
  "ci_low": 0.61,
  "ci_high": 0.96,
  "parameters": {
    "normalization": "harness/extract.py::_norm",
    "round_digits": null
  },
  "effect_delta": 0.0,
  "reported_tuple_exact": true,
  "formula": "Read reported point/CI from the located sentence after explicitly recorded decimal normalization; no count reconstruction.",
  "yi": -0.2613647641344075,
  "vi": 0.013382869315651313,
  "standard_error": 0.11568435207776077,
  "served_effect": 0.77,
  "served_standard_error": 0.11568435207776077,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.77",
  "effect_hex": "0x1.8a3d70a3d70a4p-1",
  "served_effect_hex": "0x1.8a3d70a3d70a4p-1"
}
```

Normalization: `harness/extract.py::_norm`, file SHA256 `c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50`. Changed: False. The following normalized form is a transformation, not a quotation:

```text
The primary end point occurred in 5.5% of the patients in the colchicine group, as compared with 7.1% of those in the placebo group (hazard ratio, 0.77; 95% confidence interval [CI], 0.61 to 0.96; P = 0.02).
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/colchicine-secondary-cv-prevention/records.json#/records/12/id`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [28894,28904), bytes [29041,29051).

```text
"31733140"
```

**A02 — source identity nct**: `cache/colchicine-secondary-cv-prevention/records.json#/records/12/nct`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [31361,31374), bytes [31520,31533).

```text
"NCT02551094"
```

**A03 — source identity doi**: `cache/colchicine-secondary-cv-prevention/records.json#/records/12/doi`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [31326,31349), bytes [31485,31508).

```text
"10.1056/NEJMoa1912388"
```

**A04 — source identity year**: `cache/colchicine-secondary-cv-prevention/records.json#/records/12/year`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [31278,31284), bytes [31437,31443).

```text
"2019"
```

**A05 — source identity title**: `cache/colchicine-secondary-cv-prevention/records.json#/records/12/title`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [28940,29013), bytes [29087,29160).

```text
"Efficacy and Safety of Low-Dose Colchicine after Myocardial Infarction."
```

**A06 — source sentence**: `cache/colchicine-secondary-cv-prevention/records.json#/records/12/abstract`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [30001,30208), bytes [30148,30359). Decoded-string characters [970,1177).

```text
The primary end point occurred in 5.5% of the patients in the colchicine group, as compared with 7.1% of those in the placebo group (hazard ratio, 0.77; 95% confidence interval [CI], 0.61 to 0.96; P = 0.02).
```

**A07 — raw numerical token effect**: `cache/colchicine-secondary-cv-prevention/records.json#/records/12/abstract`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [30148,30152), bytes [30295,30299). Decoded-string characters [1117,1121).

```text
0.77
```

**A08 — raw numerical token ci_low**: `cache/colchicine-secondary-cv-prevention/records.json#/records/12/abstract`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [30184,30188), bytes [30331,30335). Decoded-string characters [1153,1157).

```text
0.61
```

**A09 — raw numerical token ci_high**: `cache/colchicine-secondary-cv-prevention/records.json#/records/12/abstract`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [30192,30196), bytes [30339,30343). Decoded-string characters [1161,1165).

```text
0.96
```

### UA-007 — PMID 39555823 — Trial-defined major coronary/cardiovascular composite

Page: `colchicine-secondary-cv-prevention`. Served row: `docs/reviews/colchicine-secondary-cv-prevention/review.json#/outcomes/0/trials/1`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `REPORTED_TEXT`; recovery: `LOCATED_REPORTED_RESULT`.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| effect | `0.99` | 0.99 | A07 | A06 |  |
| ci_low | `0.85` | 0.85 | A08 | A06 |  |
| ci_high | `1.16` | 1.16 | A09 | A06 |  |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/extract.py::_effect_from_match",
  "source_sha256": "c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50",
  "scale": "HR",
  "effect": 0.99,
  "ci_low": 0.85,
  "ci_high": 1.16,
  "parameters": {
    "normalization": "harness/extract.py::_norm",
    "round_digits": null
  },
  "effect_delta": 0.0,
  "reported_tuple_exact": true,
  "formula": "Read reported point/CI from the located sentence after explicitly recorded decimal normalization; no count reconstruction.",
  "yi": -0.01005033585350145,
  "vi": 0.006292077149137129,
  "standard_error": 0.07932261436146144,
  "served_effect": 0.99,
  "served_standard_error": 0.07932261436146144,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.99",
  "effect_hex": "0x1.fae147ae147aep-1",
  "served_effect_hex": "0x1.fae147ae147aep-1"
}
```

Normalization: `harness/extract.py::_norm`, file SHA256 `c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50`. Changed: False. The following normalized form is a transformation, not a quotation:

```text
A primary-outcome event occurred in 322 of 3528 patients (9.1%) in the colchicine group and 327 of 3534 patients (9.3%) in the placebo group over a median follow-up period of 3 years (hazard ratio, 0.99; 95% confidence interval [CI], 0.85 to 1.16; P = 0.93).
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/colchicine-secondary-cv-prevention/records.json#/records/94/id`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [215912,215922), bytes [216652,216662).

```text
"39555823"
```

**A02 — source identity nct**: `cache/colchicine-secondary-cv-prevention/records.json#/records/94/nct`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [218460,218473), bytes [219200,219213).

```text
"NCT03048825"
```

**A03 — source identity doi**: `cache/colchicine-secondary-cv-prevention/records.json#/records/94/doi`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [218425,218448), bytes [219165,219188).

```text
"10.1056/NEJMoa2405922"
```

**A04 — source identity year**: `cache/colchicine-secondary-cv-prevention/records.json#/records/94/year`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [218356,218360), bytes [219096,219100).

```text
2025
```

**A05 — source identity title**: `cache/colchicine-secondary-cv-prevention/records.json#/records/94/title`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [215958,216002), bytes [216698,216742).

```text
"Colchicine in Acute Myocardial Infarction."
```

**A06 — source sentence**: `cache/colchicine-secondary-cv-prevention/records.json#/records/94/abstract`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [216990,217248), bytes [217730,217988). Decoded-string characters [970,1228).

```text
A primary-outcome event occurred in 322 of 3528 patients (9.1%) in the colchicine group and 327 of 3534 patients (9.3%) in the placebo group over a median follow-up period of 3 years (hazard ratio, 0.99; 95% confidence interval [CI], 0.85 to 1.16; P = 0.93).
```

**A07 — raw numerical token effect**: `cache/colchicine-secondary-cv-prevention/records.json#/records/94/abstract`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [217188,217192), bytes [217928,217932). Decoded-string characters [1168,1172).

```text
0.99
```

**A08 — raw numerical token ci_low**: `cache/colchicine-secondary-cv-prevention/records.json#/records/94/abstract`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [217224,217228), bytes [217964,217968). Decoded-string characters [1204,1208).

```text
0.85
```

**A09 — raw numerical token ci_high**: `cache/colchicine-secondary-cv-prevention/records.json#/records/94/abstract`; SHA256 `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`; file characters [217232,217236), bytes [217972,217976). Decoded-string characters [1212,1216).

```text
1.16
```

### UA-008 — PMID 36942789 — All-cause mortality

Page: `corticosteroids-cap-mortality`. Served row: `docs/reviews/corticosteroids-cap-mortality/review.json#/outcomes/0/trials/0`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `COUNT_DERIVED_RR`; recovery: `LOCATED_FULL_INPUT_SET`.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| ai | `25` | 25 | A07 | A06 | intervention |
| n1i | `400` | 400 | A08 | A06 | intervention |
| ci | `47` | 47 | A09 | A06 | comparator |
| n2i | `395` | 395 | A10 | A06 | comparator |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/synth.py::Study.yi_vi",
  "source_sha256": "735d9793ed5e28119be22390e73daea3c74732291c3279687abc8cc3028532dc",
  "formula": "RR = (ai/n1i)/(ci/n2i); variance(log RR) = 1/ai - 1/n1i + 1/ci - 1/n2i; no zero-cell correction triggered",
  "parameters": {
    "measure": "RR",
    "zero_cell_correction_applied": false
  },
  "scale": "RR",
  "yi": -0.643850559048718,
  "vi": 0.05624495017506059,
  "standard_error": 0.23716017830795413,
  "effect": 0.5252659574468085,
  "effect_delta": 0.0,
  "served_effect": 0.5252659574468085,
  "served_standard_error": 0.23716017830795413,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.5252659574468085",
  "effect_hex": "0x1.0cefa8d9df51bp-1",
  "served_effect_hex": "0x1.0cefa8d9df51bp-1"
}
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/corticosteroids-cap-mortality/records.json#/records/7/id`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [18909,18919), bytes [19003,19013).

```text
"36942789"
```

**A02 — source identity nct**: `cache/corticosteroids-cap-mortality/records.json#/records/7/nct`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [21510,21523), bytes [21608,21621).

```text
"NCT02517489"
```

**A03 — source identity doi**: `cache/corticosteroids-cap-mortality/records.json#/records/7/doi`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [21472,21495), bytes [21570,21593).

```text
"10.1056/NEJMoa2215145"
```

**A04 — source identity year**: `cache/corticosteroids-cap-mortality/records.json#/records/7/year`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [21418,21424), bytes [21516,21522).

```text
"2023"
```

**A05 — source identity title**: `cache/corticosteroids-cap-mortality/records.json#/records/7/title`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [18961,19017), bytes [19055,19111).

```text
"Hydrocortisone in Severe Community-Acquired Pneumonia."
```

**A06 — source sentence**: `cache/corticosteroids-cap-mortality/records.json#/records/7/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [19900,20184), bytes [19994,20282). Decoded-string characters [862,1146).

```text
By day 28, death had occurred in 25 of 400 patients (6.2%; 95% confidence interval [CI], 3.9 to 8.6) in the hydrocortisone group and in 47 of 395 patients (11.9%; 95% CI, 8.7 to 15.1) in the placebo group (absolute difference, -5.6 percentage points; 95% CI, -9.6 to -1.7; P = 0.006).
```

**A07 — raw input ai**: `cache/corticosteroids-cap-mortality/records.json#/records/7/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [19933,19935), bytes [20027,20029). Decoded-string characters [895,897).

```text
25
```

**A08 — raw input n1i**: `cache/corticosteroids-cap-mortality/records.json#/records/7/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [19939,19942), bytes [20033,20036). Decoded-string characters [901,904).

```text
400
```

**A09 — raw input ci**: `cache/corticosteroids-cap-mortality/records.json#/records/7/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [20036,20038), bytes [20130,20132). Decoded-string characters [998,1000).

```text
47
```

**A10 — raw input n2i**: `cache/corticosteroids-cap-mortality/records.json#/records/7/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [20042,20045), bytes [20136,20139). Decoded-string characters [1004,1007).

```text
395
```

### UA-009 — PMID 25688779 — All-cause mortality

Page: `corticosteroids-cap-mortality`. Served row: `docs/reviews/corticosteroids-cap-mortality/review.json#/outcomes/0/trials/1`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `COUNT_DERIVED_RR`; recovery: `LOCATED_FULL_INPUT_SET`.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| ai | `6` | 6 | A08 | A06 | intervention |
| ci | `9` | 9 | A09 | A06 | comparator |
| n1i | `61` | 61 | A10 | A07 | intervention |
| n2i | `59` | 59 | A11 | A07 | comparator |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/synth.py::Study.yi_vi",
  "source_sha256": "735d9793ed5e28119be22390e73daea3c74732291c3279687abc8cc3028532dc",
  "formula": "RR = (ai/n1i)/(ci/n2i); variance(log RR) = 1/ai - 1/n1i + 1/ci - 1/n2i; no zero-cell correction triggered",
  "parameters": {
    "measure": "RR",
    "zero_cell_correction_applied": false
  },
  "scale": "RR",
  "yi": -0.43880152837575626,
  "vi": 0.24443518261245406,
  "standard_error": 0.494403865895539,
  "effect": 0.6448087431693988,
  "effect_delta": 0.0,
  "served_effect": 0.6448087431693988,
  "served_standard_error": 0.494403865895539,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.6448087431693988",
  "effect_hex": "0x1.4a245f202cc3dp-1",
  "served_effect_hex": "0x1.4a245f202cc3dp-1"
}
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/corticosteroids-cap-mortality/records.json#/records/50/id`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [114675,114685), bytes [115053,115063).

```text
"25688779"
```

**A02 — source identity nct**: `cache/corticosteroids-cap-mortality/records.json#/records/50/nct`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [118099,118112), bytes [118501,118514).

```text
"NCT00908713"
```

**A03 — source identity doi**: `cache/corticosteroids-cap-mortality/records.json#/records/50/doi`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [118062,118084), bytes [118464,118486).

```text
"10.1001/jama.2015.88"
```

**A04 — source identity year**: `cache/corticosteroids-cap-mortality/records.json#/records/50/year`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [118016,118022), bytes [118418,118424).

```text
"2015"
```

**A05 — source identity title**: `cache/corticosteroids-cap-mortality/records.json#/records/50/title`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [114727,114905), bytes [115105,115283).

```text
"Effect of corticosteroids on treatment failure among hospitalized patients with severe community-acquired pneumonia and high inflammatory response: a randomized clinical trial."
```

**A06 — source sentence**: `cache/corticosteroids-cap-mortality/records.json#/records/50/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [117055,117273), bytes [117449,117671). Decoded-string characters [2129,2347).

```text
In-hospital mortality did not differ between the 2 groups (6 patients [10%] in the methylprednisolone group vs 9 patients [15%] in the placebo group; P = .37); the difference between groups was 5% (95% CI, -6% to 17%).
```

**A07 — source sentence**: `cache/corticosteroids-cap-mortality/records.json#/records/50/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [115764,115977), bytes [116142,116363). Decoded-string characters [838,1051).

```text
INTERVENTIONS: Patients were randomized to receive either an intravenous bolus of 0.5 mg/kg per 12 hours of methylprednisolone (n = 61) or placebo (n = 59) for 5 days started within 36 hours of hospital admission.
```

**A08 — raw input ai**: `cache/corticosteroids-cap-mortality/records.json#/records/50/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [117114,117115), bytes [117508,117509). Decoded-string characters [2188,2189).

```text
6
```

**A09 — raw input ci**: `cache/corticosteroids-cap-mortality/records.json#/records/50/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [117166,117167), bytes [117560,117561). Decoded-string characters [2240,2241).

```text
9
```

**A10 — raw input n1i**: `cache/corticosteroids-cap-mortality/records.json#/records/50/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [115896,115898), bytes [116278,116280). Decoded-string characters [970,972).

```text
61
```

**A11 — raw input n2i**: `cache/corticosteroids-cap-mortality/records.json#/records/50/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [115916,115918), bytes [116302,116304). Decoded-string characters [990,992).

```text
59
```

### UA-010 — PMID 25688779 — Hyperglycaemia

Page: `corticosteroids-cap-mortality`. Served row: `docs/reviews/corticosteroids-cap-mortality/review.json#/outcomes/1/trials/0`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `COUNT_DERIVED_RR`; recovery: `LOCATED_FULL_INPUT_SET`.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| ai | `11` | 11 | A08 | A06 | intervention |
| ci | `7` | 7 | A09 | A06 | comparator |
| n1i | `61` | 61 | A10 | A07 | intervention |
| n2i | `59` | 59 | A11 | A07 | comparator |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/synth.py::Study.yi_vi",
  "source_sha256": "735d9793ed5e28119be22390e73daea3c74732291c3279687abc8cc3028532dc",
  "formula": "RR = (ai/n1i)/(ci/n2i); variance(log RR) = 1/ai - 1/n1i + 1/ci - 1/n2i; no zero-cell correction triggered",
  "parameters": {
    "measure": "RR",
    "zero_cell_correction_applied": false
  },
  "scale": "RR",
  "yi": 0.4186487034754654,
  "vi": 0.20042363860091006,
  "standard_error": 0.4476869873035289,
  "effect": 1.5199063231850116,
  "effect_delta": 0.0,
  "served_effect": 1.5199063231850116,
  "served_standard_error": 0.4476869873035289,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "1.5199063231850116",
  "effect_hex": "0x1.851894af102ffp+0",
  "served_effect_hex": "0x1.851894af102ffp+0"
}
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/corticosteroids-cap-mortality/records.json#/records/50/id`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [114675,114685), bytes [115053,115063).

```text
"25688779"
```

**A02 — source identity nct**: `cache/corticosteroids-cap-mortality/records.json#/records/50/nct`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [118099,118112), bytes [118501,118514).

```text
"NCT00908713"
```

**A03 — source identity doi**: `cache/corticosteroids-cap-mortality/records.json#/records/50/doi`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [118062,118084), bytes [118464,118486).

```text
"10.1001/jama.2015.88"
```

**A04 — source identity year**: `cache/corticosteroids-cap-mortality/records.json#/records/50/year`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [118016,118022), bytes [118418,118424).

```text
"2015"
```

**A05 — source identity title**: `cache/corticosteroids-cap-mortality/records.json#/records/50/title`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [114727,114905), bytes [115105,115283).

```text
"Effect of corticosteroids on treatment failure among hospitalized patients with severe community-acquired pneumonia and high inflammatory response: a randomized clinical trial."
```

**A06 — source sentence**: `cache/corticosteroids-cap-mortality/records.json#/records/50/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [117274,117405), bytes [117672,117807). Decoded-string characters [2348,2479).

```text
Hyperglycemia occurred in 11 patients (18%) in the methylprednisolone group and in 7 patients (12%) in the placebo group (P = .34).
```

**A07 — source sentence**: `cache/corticosteroids-cap-mortality/records.json#/records/50/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [115764,115977), bytes [116142,116363). Decoded-string characters [838,1051).

```text
INTERVENTIONS: Patients were randomized to receive either an intravenous bolus of 0.5 mg/kg per 12 hours of methylprednisolone (n = 61) or placebo (n = 59) for 5 days started within 36 hours of hospital admission.
```

**A08 — raw input ai**: `cache/corticosteroids-cap-mortality/records.json#/records/50/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [117300,117302), bytes [117698,117700). Decoded-string characters [2374,2376).

```text
11
```

**A09 — raw input ci**: `cache/corticosteroids-cap-mortality/records.json#/records/50/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [117357,117358), bytes [117755,117756). Decoded-string characters [2431,2432).

```text
7
```

**A10 — raw input n1i**: `cache/corticosteroids-cap-mortality/records.json#/records/50/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [115896,115898), bytes [116278,116280). Decoded-string characters [970,972).

```text
61
```

**A11 — raw input n2i**: `cache/corticosteroids-cap-mortality/records.json#/records/50/abstract`; SHA256 `ce1169669dd255dce8f83c85846730a490b2f684015fe380d42e3f1c2621b591`; file characters [115916,115918), bytes [116302,116304). Decoded-string characters [990,992).

```text
59
```

### UA-014 — PMID 31109201 — Observed-case Day-28 raw change-score MADRS MD

Page: `esketamine-trd-madrs`. Served row: `docs/reviews/esketamine-trd-madrs/review.json#/outcomes/0/trials/0`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `ARM_MEAN_DIFFERENCE`; recovery: `LOCATED_FULL_INPUT_SET`.

Registry: `NCT02418585`, outcome index 0 (zero-based), `/ctgov_results/NCT02418585/0`; Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 in the Double-blind Induction Phase- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis.

Served output is an unadjusted arm-mean subtraction. Located model-adjusted registry analyses are separate estimands and are not substituted.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| mean1 | `-21.4` | -21.4 | A15 | A16 | OG000 |
| nc1 | `101` | 101 | A17 | A18 | OG000 |
| sd1 | `12.32` | 12.32 | A19 | A20 | OG000 |
| mean2 | `-17.0` | -17 | A21 | A22 | OG001 |
| nc2 | `100` | 100 | A23 | A24 | OG001 |
| sd2 | `13.88` | 13.88 | A25 | A26 | OG001 |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/synth.py::Study.yi_vi",
  "source_sha256": "735d9793ed5e28119be22390e73daea3c74732291c3279687abc8cc3028532dc",
  "formula": "MD = mean1 - mean2; variance = sd1^2/nc1 + sd2^2/nc2",
  "parameters": {
    "measure": "MD",
    "zero_cell_correction_applied": false
  },
  "scale": "MD",
  "yi": -4.399999999999999,
  "vi": 3.4293400396039604,
  "standard_error": 1.8518477366144228,
  "effect": -4.399999999999999,
  "effect_delta": 0.0,
  "served_effect": -4.399999999999999,
  "served_standard_error": 1.8518477366144228,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "-4.399999999999999",
  "effect_hex": "-0x1.1999999999998p+2",
  "served_effect_hex": "-0x1.1999999999998p+2"
}
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/esketamine-trd-madrs/records.json#/records/19/id`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [47311,47321), bytes [47601,47611).

```text
"31109201"
```

**A02 — source identity nct**: `cache/esketamine-trd-madrs/records.json#/records/19/nct`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [50382,50395), bytes [50673,50686).

```text
"NCT02418585"
```

**A03 — source identity doi**: `cache/esketamine-trd-madrs/records.json#/records/19/doi`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [50335,50367), bytes [50626,50658).

```text
"10.1176/appi.ajp.2019.19020172"
```

**A04 — source identity year**: `cache/esketamine-trd-madrs/records.json#/records/19/year`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [50278,50284), bytes [50569,50575).

```text
"2019"
```

**A05 — source identity title**: `cache/esketamine-trd-madrs/records.json#/records/19/title`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [47363,47563), bytes [47653,47853).

```text
"Efficacy and Safety of Flexibly Dosed Esketamine Nasal Spray Combined With a Newly Initiated Oral Antidepressant in Treatment-Resistant Depression: A Randomized Double-Blind Active-Controlled Study."
```

**A06 — registry context title**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/title`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [413230,413427), bytes [414954,415151).

```text
"Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 in the Double-blind Induction Phase- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis"
```

**A07 — registry context type**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/type`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [413202,413211), bytes [414926,414935).

```text
"PRIMARY"
```

**A08 — registry context timeFrame**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/timeFrame`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [414535,414590), bytes [416259,416314).

```text
"Baseline up to Day 28 of Double-blind Induction Phase"
```

**A09 — registry context paramType**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/paramType`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [414413,414419), bytes [416137,416143).

```text
"MEAN"
```

**A10 — registry context dispersionType**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/dispersionType`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [414447,414467), bytes [416171,416191).

```text
"Standard Deviation"
```

**A11 — registry context unitOfMeasure**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/unitOfMeasure`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [414494,414512), bytes [416218,416236).

```text
"Units on a scale"
```

**A12 — registry context populationDescription**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/populationDescription`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [414008,414353), bytes [415732,416077).

```text
"Full analysis set (FAS) defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of oral antidepressant (AD) medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure."
```

**A13 — group identity**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/groups/0`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [414622,415783), bytes [416346,417507).

```text
{
            "id": "OG000",
            "title": "Intranasal Esketamine (Esk) Plus Oral Antidepressant (AD)",
            "description": "Participants self-administered (under direct supervision by HCP) esketamine 56 milligram (mg) or 84 mg intranasally twice weekly for 4 weeks (on Day 1,4,8,11,15,18,22,25). Simultaneously, participants initiated per fixed titration scheme a new open-label oral AD with one of following: \\[Duloxetine (60 milligram (mg)/day- Weeks 1-4 with minimum dose for tolerability \\[MDT\\] of 60 mg/day); Escitalopram (10 mg/day-Week 1 and 20 mg/day- Weeks 2-4 with MDT of 10 mg/day); Sertraline (50 mg/day-Week 1, 100 mg/day-Week 2, 150 mg/day-Week 3 and 200 mg/day-Week 4 with MDT of 50 mg/day) or Venlafaxine XR (75 mg/day-Week 1, 150 mg/day-Week 2, and 225 mg/day-Weeks 3 and 4 with MDT of 150 mg/day) during DB Induction Phase. Participants who were not eligible or who chose to not participate in maintenance of effect study (ESKETINTRD3003\\[NCT02493868\\]) and had received at least 1 dose of intranasal Esketamine+ Oral AD in DB induction phase were followed in posttreatment follow-up phase for up to 24 weeks."
          }
```

**A14 — group identity**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/groups/1`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [415795,416929), bytes [417519,418653).

```text
{
            "id": "OG001",
            "title": "Intranasal Placebo Plus Oral AD",
            "description": "Participants self-administered (under direct supervision by HCP) esketamine matched placebo intranasally twice weekly for 4 weeks (on Day 1,4,8,11,15,18,22 and 25). Simultaneously, participants initiated per fixed titration scheme a new open-label oral AD with one of following: \\[Duloxetine (60 milligram (mg)/day- Weeks 1-4 with minimum dose for tolerability \\[MDT\\] of 60 mg/day); Escitalopram (10 mg/day- Week 1 and 20 mg/day- Weeks 2-4 with MDT of 10 mg/day); Sertraline (50 mg/day- Week 1, 100 mg/day- Week 2, 150 mg/day- Week 3 and 200 mg/day- Week 4 with MDT of 50 mg/day) or Venlafaxine XR (75 mg/day- Week 1, 150 mg/day- Week 2, and 225 mg/day- Weeks 3 and 4 with MDT of 150 mg/day) during DB Induction Phase. Participants who were not eligible or who chose to not participate in maintenance of effect study (ESKETINTRD3003 \\[NCT02493868\\]) and had received at least 1 dose of intranasal Placebo+ Oral AD in DB induction phase were followed in posttreatment follow-up phase for up to 24 weeks."
          }
```

**A15 — raw input mean1**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/classes/0/categories/0/measurements/0/value`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [417470,417477), bytes [419194,419201).

```text
"-21.4"
```

**A16 — input cell context mean1**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/classes/0/categories/0/measurements/0`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [417399,417536), bytes [419123,419260).

```text
{
                    "groupId": "OG000",
                    "value": "-21.4",
                    "spread": "12.32"
                  }
```

**A17 — raw input nc1**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/denoms/0/counts/0/value`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [417111,417116), bytes [418835,418840).

```text
"101"
```

**A18 — input cell context nc1**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/denoms/0/counts/0`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [417048,417132), bytes [418772,418856).

```text
{
                "groupId": "OG000",
                "value": "101"
              }
```

**A19 — raw input sd1**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/classes/0/categories/0/measurements/0/spread`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [417509,417516), bytes [419233,419240).

```text
"12.32"
```

**A20 — input cell context sd1**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/classes/0/categories/0/measurements/0`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [417399,417536), bytes [419123,419260).

```text
{
                    "groupId": "OG000",
                    "value": "-21.4",
                    "spread": "12.32"
                  }
```

**A21 — raw input mean2**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/classes/0/categories/0/measurements/1/value`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [417627,417634), bytes [419351,419358).

```text
"-17.0"
```

**A22 — input cell context mean2**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/classes/0/categories/0/measurements/1`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [417556,417693), bytes [419280,419417).

```text
{
                    "groupId": "OG001",
                    "value": "-17.0",
                    "spread": "13.88"
                  }
```

**A23 — raw input nc2**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/denoms/0/counts/1/value`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [417211,417216), bytes [418935,418940).

```text
"100"
```

**A24 — input cell context nc2**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/denoms/0/counts/1`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [417148,417232), bytes [418872,418956).

```text
{
                "groupId": "OG001",
                "value": "100"
              }
```

**A25 — raw input sd2**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/classes/0/categories/0/measurements/1/spread`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [417666,417673), bytes [419390,419397).

```text
"13.88"
```

**A26 — input cell context sd2**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/classes/0/categories/0/measurements/1`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [417556,417693), bytes [419280,419417).

```text
{
                    "groupId": "OG001",
                    "value": "-17.0",
                    "spread": "13.88"
                  }
```

**A27 — reported model-adjusted analyses (not the served raw reconstruction)**: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0/analyses`; SHA256 `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`; file characters [417785,418396), bytes [419509,420120).

```text
[
          {
            "groupIds": [
              "OG000",
              "OG001"
            ],
            "nonInferiorityType": "SUPERIORITY",
            "pValue": "=0.020",
            "statisticalMethod": "Mixed Model for Repeated Measures",
            "paramType": "Difference of Least Square (LS) Means",
            "paramValue": "-4.0",
            "ciPctValue": "95",
            "ciNumSides": "TWO_SIDED",
            "ciLowerLimit": "-7.31",
            "ciUpperLimit": "-0.64",
            "dispersionType": "STANDARD_ERROR_OF_MEAN",
            "dispersionValue": "1.69"
          }
        ]
```

### UA-027 — PMID 20712869 — Sleep-onset latency

Page: `melatonin-primary-insomnia-sol`. Served row: `docs/reviews/melatonin-primary-insomnia-sol/review.json#/outcomes/0/trials/0`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `ARM_MEAN_DIFFERENCE`; recovery: `LOCATED_FULL_INPUT_SET`.

Registry: `NCT00397189`, outcome index 0 (zero-based), `/ctgov_results/NCT00397189/0`; The Change From Baseline in Subjective Sleep Latency..

Served output is an unadjusted arm-mean subtraction. Located model-adjusted registry analyses are separate estimands and are not substituted.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| mean1 | `-19.1` | -19.1 | A15 | A16 | OG000 |
| nc1 | `137` | 137 | A17 | A18 | OG000 |
| sd1 | `47.3` | 47.3 | A19 | A20 | OG000 |
| mean2 | `-1.7` | -1.7 | A21 | A22 | OG001 |
| nc2 | `144` | 144 | A23 | A24 | OG001 |
| sd2 | `47.8` | 47.8 | A25 | A26 | OG001 |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/synth.py::Study.yi_vi",
  "source_sha256": "735d9793ed5e28119be22390e73daea3c74732291c3279687abc8cc3028532dc",
  "formula": "MD = mean1 - mean2; variance = sd1^2/nc1 + sd2^2/nc2",
  "parameters": {
    "measure": "MD",
    "zero_cell_correction_applied": false
  },
  "scale": "MD",
  "yi": -17.400000000000002,
  "vi": 32.19752838605028,
  "standard_error": 5.674286597101902,
  "effect": -17.400000000000002,
  "effect_delta": 0.0,
  "served_effect": -17.400000000000002,
  "served_standard_error": 5.674286597101902,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "-17.400000000000002",
  "effect_hex": "-0x1.1666666666667p+4",
  "served_effect_hex": "-0x1.1666666666667p+4"
}
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/melatonin-primary-insomnia-sol/records.json#/records/84/id`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [206027,206037), bytes [206748,206758).

```text
"20712869"
```

**A02 — source identity nct**: `cache/melatonin-primary-insomnia-sol/records.json#/records/84/nct`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [208883,208896), bytes [209604,209617).

```text
"NCT00397189"
```

**A03 — source identity doi**: `cache/melatonin-primary-insomnia-sol/records.json#/records/84/doi`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [208844,208868), bytes [209565,209589).

```text
"10.1186/1741-7015-8-51"
```

**A04 — source identity year**: `cache/melatonin-primary-insomnia-sol/records.json#/records/84/year`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [208795,208801), bytes [209516,209522).

```text
"2010"
```

**A05 — source identity title**: `cache/melatonin-primary-insomnia-sol/records.json#/records/84/title`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [206079,206273), bytes [206800,206994).

```text
"Nightly treatment of primary insomnia with prolonged release melatonin for 6 months: a randomized placebo controlled trial on age and endogenous melatonin as predictors of efficacy and safety."
```

**A06 — registry context title**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/title`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [439269,439324), bytes [440424,440479).

```text
"The Change From Baseline in Subjective Sleep Latency."
```

**A07 — registry context type**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/type`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [439241,439250), bytes [440396,440405).

```text
"PRIMARY"
```

**A08 — registry context timeFrame**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/timeFrame`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [440292,440314), bytes [441447,441469).

```text
"Baseline and 3 weeks"
```

**A09 — registry context paramType**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/paramType`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [440179,440185), bytes [441334,441340).

```text
"MEAN"
```

**A10 — registry context dispersionType**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/dispersionType`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [440213,440233), bytes [441368,441388).

```text
"Standard Deviation"
```

**A11 — registry context unitOfMeasure**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/unitOfMeasure`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [440260,440269), bytes [441415,441424).

```text
"minutes"
```

**A12 — registry context populationDescription**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/populationDescription`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [440069,440119), bytes [441224,441274).

```text
"Pre-planned analysis on ITT population age 65-80"
```

**A13 — group identity**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/groups/0`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [440346,440537), bytes [441501,441692).

```text
{
            "id": "OG000",
            "title": "Circadin",
            "description": "Prolonged release melatonin 2 mg. Tablets should be taken 1-2 hours before going to bed."
          }
```

**A14 — group identity**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/groups/1`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [440549,440736), bytes [441704,441891).

```text
{
            "id": "OG001",
            "title": "Placebo",
            "description": "Identical tablets to Circadin. Tablets should be taken 1-2 hours before going to bed."
          }
```

**A15 — raw input mean1**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/classes/0/categories/0/measurements/0/value`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [441277,441284), bytes [442432,442439).

```text
"-19.1"
```

**A16 — input cell context mean1**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/classes/0/categories/0/measurements/0`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [441206,441342), bytes [442361,442497).

```text
{
                    "groupId": "OG000",
                    "value": "-19.1",
                    "spread": "47.3"
                  }
```

**A17 — raw input nc1**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/denoms/0/counts/0/value`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [440918,440923), bytes [442073,442078).

```text
"137"
```

**A18 — input cell context nc1**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/denoms/0/counts/0`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [440855,440939), bytes [442010,442094).

```text
{
                "groupId": "OG000",
                "value": "137"
              }
```

**A19 — raw input sd1**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/classes/0/categories/0/measurements/0/spread`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [441316,441322), bytes [442471,442477).

```text
"47.3"
```

**A20 — input cell context sd1**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/classes/0/categories/0/measurements/0`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [441206,441342), bytes [442361,442497).

```text
{
                    "groupId": "OG000",
                    "value": "-19.1",
                    "spread": "47.3"
                  }
```

**A21 — raw input mean2**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/classes/0/categories/0/measurements/1/value`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [441433,441439), bytes [442588,442594).

```text
"-1.7"
```

**A22 — input cell context mean2**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/classes/0/categories/0/measurements/1`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [441362,441497), bytes [442517,442652).

```text
{
                    "groupId": "OG001",
                    "value": "-1.7",
                    "spread": "47.8"
                  }
```

**A23 — raw input nc2**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/denoms/0/counts/1/value`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [441018,441023), bytes [442173,442178).

```text
"144"
```

**A24 — input cell context nc2**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/denoms/0/counts/1`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [440955,441039), bytes [442110,442194).

```text
{
                "groupId": "OG001",
                "value": "144"
              }
```

**A25 — raw input sd2**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/classes/0/categories/0/measurements/1/spread`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [441471,441477), bytes [442626,442632).

```text
"47.8"
```

**A26 — input cell context sd2**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/classes/0/categories/0/measurements/1`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [441362,441497), bytes [442517,442652).

```text
{
                    "groupId": "OG001",
                    "value": "-1.7",
                    "spread": "47.8"
                  }
```

**A27 — reported model-adjusted analyses (not the served raw reconstruction)**: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0/analyses`; SHA256 `1330610ba90e710cb6fae526f1b4067ca454faa1c8559f6161e9313cf3e3e44d`; file characters [441589,442432), bytes [442744,443588).

```text
[
          {
            "groupIds": [
              "OG000",
              "OG001"
            ],
            "groupDescription": "The analysis was a comparison of sleep latency as measured by the sleep diary at Visit 3 in the ITT 65-80 population, using a linear regression model with terms for treatment (Circadin® 2mg vs. Placebo) and baseline sleep latency.",
            "nonInferiorityType": "SUPERIORITY_OR_OTHER",
            "pValue": "<0.05",
            "statisticalMethod": "ANCOVA",
            "paramType": "Mean Difference (Final Values)",
            "paramValue": "-15.6",
            "ciPctValue": "95",
            "ciNumSides": "TWO_SIDED",
            "ciLowerLimit": "-25.3",
            "ciUpperLimit": "-6",
            "dispersionType": "STANDARD_DEVIATION",
            "dispersionValue": "47"
          }
        ]
```

### UA-030 — PMID 30146932 — Atrial fibrillation

Page: `omega3-cardiovascular-events`. Served row: `docs/reviews/omega3-cardiovascular-events/review.json#/outcomes/1/trials/0`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `COUNT_DERIVED_RR`; recovery: `LOCATED_FULL_INPUT_SET`.

Registry: `NCT00135226`, outcome index 22 (zero-based), `/ctgov_results/NCT00135226/22`; Number of Participants With Event: Atrial Fibrillation (Omega-3 Comparison Only).

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| ai | `166` | 166 | A13 | A14 | OG000 |
| n1i | `7740` | 7740 | A15 | A16 | OG000 |
| ci | `135` | 135 | A17 | A18 | OG001 |
| n2i | `7740` | 7740 | A19 | A20 | OG001 |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/synth.py::Study.yi_vi",
  "source_sha256": "735d9793ed5e28119be22390e73daea3c74732291c3279687abc8cc3028532dc",
  "formula": "RR = (ai/n1i)/(ci/n2i); variance(log RR) = 1/ai - 1/n1i + 1/ci - 1/n2i; no zero-cell correction triggered",
  "parameters": {
    "measure": "RR",
    "zero_cell_correction_applied": false
  },
  "scale": "RR",
  "yi": 0.20671300991811378,
  "vi": 0.01317310586013304,
  "standard_error": 0.1147741515330566,
  "effect": 1.2296296296296296,
  "effect_delta": 0.0,
  "served_effect": 1.2296296296296296,
  "served_standard_error": 0.1147741515330566,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "1.2296296296296296",
  "effect_hex": "0x1.3ac901e573ac9p+0",
  "served_effect_hex": "0x1.3ac901e573ac9p+0"
}
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/omega3-cardiovascular-events/records.json#/records/4/id`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [12639,12649), bytes [12662,12672).

```text
"30146932"
```

**A02 — source identity nct**: `cache/omega3-cardiovascular-events/records.json#/records/4/nct`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [15055,15068), bytes [15078,15091).

```text
"NCT00135226"
```

**A03 — source identity doi**: `cache/omega3-cardiovascular-events/records.json#/records/4/doi`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [15017,15040), bytes [15040,15063).

```text
"10.1056/NEJMoa1804989"
```

**A04 — source identity year**: `cache/omega3-cardiovascular-events/records.json#/records/4/year`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [14963,14969), bytes [14986,14992).

```text
"2018"
```

**A05 — source identity title**: `cache/omega3-cardiovascular-events/records.json#/records/4/title`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [12691,12752), bytes [12714,12775).

```text
"Effects of n-3 Fatty Acid Supplements in Diabetes Mellitus."
```

**A06 — registry context title**: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22/title`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [463278,463360), bytes [463812,463894).

```text
"Number of Participants With Event: Atrial Fibrillation (Omega-3 Comparison Only)"
```

**A07 — registry context type**: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22/type`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [463238,463259), bytes [463772,463793).

```text
"OTHER_PRE_SPECIFIED"
```

**A08 — registry context timeFrame**: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22/timeFrame`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [463570,463625), bytes [464104,464159).

```text
"Randomized treatment phase during a mean of 7.4 years"
```

**A09 — registry context paramType**: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22/paramType`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [463483,463506), bytes [464017,464040).

```text
"COUNT_OF_PARTICIPANTS"
```

**A10 — registry context unitOfMeasure**: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22/unitOfMeasure`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [463533,463547), bytes [464067,464081).

```text
"Participants"
```

**A11 — group identity**: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22/groups/0`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [463657,463876), bytes [464191,464410).

```text
{
            "id": "OG000",
            "title": "Omega-3",
            "description": "Group includes 3870 participants in the Omega-3+Aspirin arm, and 3870 participants in the Omega-3+Placebo Aspirin arm"
          }
```

**A12 — group identity**: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22/groups/1`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [463888,464131), bytes [464422,464665).

```text
{
            "id": "OG001",
            "title": "Placebo Omega-3",
            "description": "Group includes 3870 participants in the Placebo Omega-3+Aspirin arm, and 3870 participants in the Placebo Omega-3+Placebo Aspirin arm"
          }
```

**A13 — raw input ai**: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22/classes/0/categories/0/measurements/0/value`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [464674,464679), bytes [465208,465213).

```text
"166"
```

**A14 — input cell context ai**: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22/classes/0/categories/0/measurements/0`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [464603,464699), bytes [465137,465233).

```text
{
                    "groupId": "OG000",
                    "value": "166"
                  }
```

**A15 — raw input n1i**: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22/denoms/0/counts/0/value`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [464313,464319), bytes [464847,464853).

```text
"7740"
```

**A16 — input cell context n1i**: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22/denoms/0/counts/0`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [464250,464335), bytes [464784,464869).

```text
{
                "groupId": "OG000",
                "value": "7740"
              }
```

**A17 — raw input ci**: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22/classes/0/categories/0/measurements/1/value`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [464790,464795), bytes [465324,465329).

```text
"135"
```

**A18 — input cell context ci**: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22/classes/0/categories/0/measurements/1`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [464719,464815), bytes [465253,465349).

```text
{
                    "groupId": "OG001",
                    "value": "135"
                  }
```

**A19 — raw input n2i**: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22/denoms/0/counts/1/value`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [464414,464420), bytes [464948,464954).

```text
"7740"
```

**A20 — input cell context n2i**: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22/denoms/0/counts/1`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [464351,464436), bytes [464885,464970).

```text
{
                "groupId": "OG001",
                "value": "7740"
              }
```

**A21 — reported model-adjusted analyses (not the served raw reconstruction)**: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22/analyses`; SHA256 `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`; file characters [464907,465286), bytes [465441,465820).

```text
[
          {
            "groupIds": [
              "OG000",
              "OG001"
            ],
            "nonInferiorityType": "OTHER",
            "paramType": "Rate Ratio",
            "paramValue": "1.23",
            "ciPctValue": "95",
            "ciNumSides": "TWO_SIDED",
            "ciLowerLimit": "0.98",
            "ciUpperLimit": "1.54"
          }
        ]
```

### UA-032 — PMID 33625476 — Percent change in body weight

Page: `semaglutide-obesity-weight`. Served row: `docs/reviews/semaglutide-obesity-weight/review.json#/outcomes/0/trials/0`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `ARM_MEAN_DIFFERENCE`; recovery: `LOCATED_FULL_INPUT_SET`.

Registry: `NCT03611582`, outcome index 0 (zero-based), `/ctgov_results/NCT03611582/0`; Change in Body Weight (%).

Served output is an unadjusted arm-mean subtraction. Located model-adjusted registry analyses are separate estimands and are not substituted.

Producer reads outcome-level overall FAS n, while means/SDs come from class 0 with its own available-data n. PopulationDescription explicitly distinguishes the two.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| mean1 | `-16.5` | -16.5 | A15 | A16 | OG000 |
| nc1 | `407` | 407 | A17 | A18 | OG000 |
| sd1 | `10.1` | 10.1 | A19 | A20 | OG000 |
| mean2 | `-5.8` | -5.8 | A21 | A22 | OG001 |
| nc2 | `204` | 204 | A23 | A24 | OG001 |
| sd2 | `7.7` | 7.7 | A25 | A26 | OG001 |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/synth.py::Study.yi_vi",
  "source_sha256": "735d9793ed5e28119be22390e73daea3c74732291c3279687abc8cc3028532dc",
  "formula": "MD = mean1 - mean2; variance = sd1^2/nc1 + sd2^2/nc2",
  "parameters": {
    "measure": "MD",
    "zero_cell_correction_applied": false
  },
  "scale": "MD",
  "yi": -10.7,
  "vi": 0.5412760755407814,
  "standard_error": 0.735714669923593,
  "effect": -10.7,
  "effect_delta": 0.0,
  "served_effect": -10.7,
  "served_standard_error": 0.735714669923593,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "-10.7",
  "effect_hex": "-0x1.5666666666666p+3",
  "served_effect_hex": "-0x1.5666666666666p+3"
}
```

Denominator finding:

```json
{
  "code": "CLASS_DENOMINATOR_MISMATCH",
  "source_anchor": "A29",
  "served_n": [
    407,
    204
  ],
  "available_data_n": [
    373,
    189
  ],
  "explanation": "Producer reads outcome-level overall FAS n, while means/SDs come from class 0 with its own available-data n. PopulationDescription explicitly distinguishes the two.",
  "class_coherent_replay": {
    "effect": -10.7,
    "vi": 0.5871889583953928,
    "standard_error": 0.7662825578044907,
    "relative_se_increase": 0.04154856377143101,
    "status": "diagnostic only; no served data changed"
  }
}
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/semaglutide-obesity-weight/records.json#/records/117/id`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [289502,289512), bytes [291296,291306).

```text
"33625476"
```

**A02 — source identity nct**: `cache/semaglutide-obesity-weight/records.json#/records/117/nct`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [292633,292646), bytes [294455,294468).

```text
"NCT03611582"
```

**A03 — source identity doi**: `cache/semaglutide-obesity-weight/records.json#/records/117/doi`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [292594,292618), bytes [294416,294440).

```text
"10.1001/jama.2021.1831"
```

**A04 — source identity year**: `cache/semaglutide-obesity-weight/records.json#/records/117/year`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [292548,292554), bytes [294370,294376).

```text
"2021"
```

**A05 — source identity title**: `cache/semaglutide-obesity-weight/records.json#/records/117/title`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [289554,289738), bytes [291348,291532).

```text
"Effect of Subcutaneous Semaglutide vs Placebo as an Adjunct to Intensive Behavioral Therapy on Body Weight in Adults With Overweight or Obesity: The STEP 3 Randomized Clinical Trial."
```

**A06 — registry context title**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/title`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1794063,1794090), bytes [1796396,1796423).

```text
"Change in Body Weight (%)"
```

**A07 — registry context type**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/type`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1794035,1794044), bytes [1796368,1796377).

```text
"PRIMARY"
```

**A08 — registry context timeFrame**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/timeFrame`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1795206,1795236), bytes [1797539,1797569).

```text
"Baseline (week 0) to week 68"
```

**A09 — registry context paramType**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/paramType`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1795090,1795096), bytes [1797423,1797429).

```text
"MEAN"
```

**A10 — registry context dispersionType**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/dispersionType`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1795124,1795144), bytes [1797457,1797477).

```text
"Standard Deviation"
```

**A11 — registry context unitOfMeasure**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/unitOfMeasure`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1795171,1795183), bytes [1797504,1797516).

```text
"Percentage"
```

**A12 — registry context populationDescription**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/populationDescription`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1794856,1795030), bytes [1797189,1797363).

```text
"Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data."
```

**A13 — group identity**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/groups/0`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1795268,1796112), bytes [1797601,1798445).

```text
{
            "id": "OG000",
            "title": "Semaglutide 2.4 mg",
            "description": "Participants were to receive once-weekly subcutaneous (s.c) injection of semaglutide using a PDS290 pre-filled pen-injector with a 3 mL cartridge containing semaglutide 1.0 mg/mL or 3.0 mg/mL or 3.2 mg/mL in 16 week dose escalation period with dose escalation (0.25 mg, 0.5 mg, 1.0 mg and 1.7 mg) every fourth week until maintenance dose of 2.4 mg of semaglutide was reached. Treatment was continued on the maintenance dose of 2.4 mg once weekly for an additional 52 weeks until week 68. The treatment was an adjunct to Intensive Behavioural Therapy (IBT), which involves physical activity and dietary intervention with the first 8 weeks of a low-calorie diet (LCD) followed by a strict hypo-caloric diet till the end of treatment."
          }
```

**A14 — group identity**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/groups/1`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1796124,1796925), bytes [1798457,1799258).

```text
{
            "id": "OG001",
            "title": "Placebo",
            "description": "Participants were to receive once-weekly s.c injection of matching semaglutide placebo using a PDS290 pre-filled pen-injector with a 3 mL cartridge containing semaglutide placebo 1.0 mg/mL or 3.0 mg/mL or 3.2 mg/mL in 16 week dose escalation period with dose escalation (0.25 mg, 0.5 mg, 1.0 mg, and 1.7 mg) every fourth week until a maintenance dose of 2.4 mg of semaglutide placebo was reached. Treatment was continued on the maintenance dose of 2.4 mg once weekly for an additional 52 weeks until week 68. The treatment was an adjunct to IBT, which involves physical activity and dietary intervention with the first 8 weeks of LCD followed by a strict hypo-caloric diet till the end of treatment."
          }
```

**A15 — raw input mean1**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/0/categories/0/measurements/0/value`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1797907,1797914), bytes [1800240,1800247).

```text
"-16.5"
```

**A16 — input cell context mean1**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/0/categories/0/measurements/0`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1797836,1797972), bytes [1800169,1800305).

```text
{
                    "groupId": "OG000",
                    "value": "-16.5",
                    "spread": "10.1"
                  }
```

**A17 — raw input nc1**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/denoms/0/counts/0/value`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1797107,1797112), bytes [1799440,1799445).

```text
"407"
```

**A18 — input cell context nc1**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/denoms/0/counts/0`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1797044,1797128), bytes [1799377,1799461).

```text
{
                "groupId": "OG000",
                "value": "407"
              }
```

**A19 — raw input sd1**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/0/categories/0/measurements/0/spread`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1797946,1797952), bytes [1800279,1800285).

```text
"10.1"
```

**A20 — input cell context sd1**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/0/categories/0/measurements/0`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1797836,1797972), bytes [1800169,1800305).

```text
{
                    "groupId": "OG000",
                    "value": "-16.5",
                    "spread": "10.1"
                  }
```

**A21 — raw input mean2**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/0/categories/0/measurements/1/value`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1798063,1798069), bytes [1800396,1800402).

```text
"-5.8"
```

**A22 — input cell context mean2**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/0/categories/0/measurements/1`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1797992,1798126), bytes [1800325,1800459).

```text
{
                    "groupId": "OG001",
                    "value": "-5.8",
                    "spread": "7.7"
                  }
```

**A23 — raw input nc2**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/denoms/0/counts/1/value`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1797207,1797212), bytes [1799540,1799545).

```text
"204"
```

**A24 — input cell context nc2**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/denoms/0/counts/1`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1797144,1797228), bytes [1799477,1799561).

```text
{
                "groupId": "OG001",
                "value": "204"
              }
```

**A25 — raw input sd2**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/0/categories/0/measurements/1/spread`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1798101,1798106), bytes [1800434,1800439).

```text
"7.7"
```

**A26 — input cell context sd2**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/0/categories/0/measurements/1`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1797992,1798126), bytes [1800325,1800459).

```text
{
                    "groupId": "OG001",
                    "value": "-5.8",
                    "spread": "7.7"
                  }
```

**A27 — reported model-adjusted analyses (not the served raw reconstruction)**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/analyses`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1799122,1800215), bytes [1801455,1802548).

```text
[
          {
            "groupIds": [
              "OG000",
              "OG001"
            ],
            "groupDescription": "Treatment policy estimand",
            "nonInferiorityType": "SUPERIORITY",
            "pValue": "<.0001",
            "statisticalMethod": "ANCOVA",
            "paramType": "Treatment difference",
            "paramValue": "-10.27",
            "ciPctValue": "95",
            "ciNumSides": "TWO_SIDED",
            "ciLowerLimit": "-11.97",
            "ciUpperLimit": "-8.57"
          },
          {
            "groupIds": [
              "OG000",
              "OG001"
            ],
            "groupDescription": "Hypothetical estimand",
            "nonInferiorityType": "SUPERIORITY",
            "pValue": "<0.0001",
            "statisticalMethod": "MMRM (mixed model repeated measurement)",
            "paramType": "Treatment difference",
            "paramValue": "-12.67",
            "ciPctValue": "95",
            "ciNumSides": "TWO_SIDED",
            "ciLowerLimit": "-14.34",
            "ciUpperLimit": "-11.00"
          }
        ]
```

**A28 — selected measurement class**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/0/title`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1797320,1797349), bytes [1799653,1799682).

```text
"In-trial observation period"
```

**A29 — class-specific available-data denominators**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0/classes/0/denoms`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1797373,1797738), bytes [1799706,1800071).

```text
[
              {
                "units": "Participants",
                "counts": [
                  {
                    "groupId": "OG000",
                    "value": "373"
                  },
                  {
                    "groupId": "OG001",
                    "value": "189"
                  }
                ]
              }
            ]
```

### UA-033 — PMID 33567185 — Percent change in body weight

Page: `semaglutide-obesity-weight`. Served row: `docs/reviews/semaglutide-obesity-weight/review.json#/outcomes/0/trials/1`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `ARM_MEAN_DIFFERENCE`; recovery: `LOCATED_FULL_INPUT_SET`.

Registry: `NCT03548935`, outcome index 0 (zero-based), `/ctgov_results/NCT03548935/0`; Change in Body Weight (%).

Served output is an unadjusted arm-mean subtraction. Located model-adjusted registry analyses are separate estimands and are not substituted.

Producer reads outcome-level overall FAS n, while means/SDs come from class 0 with its own available-data n. PopulationDescription explicitly distinguishes the two.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| mean1 | `-15.6` | -15.6 | A15 | A16 | OG000 |
| nc1 | `1306` | 1306 | A17 | A18 | OG000 |
| sd1 | `10.1` | 10.1 | A19 | A20 | OG000 |
| mean2 | `-2.8` | -2.8 | A21 | A22 | OG001 |
| nc2 | `655` | 655 | A23 | A24 | OG001 |
| sd2 | `6.5` | 6.5 | A25 | A26 | OG001 |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/synth.py::Study.yi_vi",
  "source_sha256": "735d9793ed5e28119be22390e73daea3c74732291c3279687abc8cc3028532dc",
  "formula": "MD = mean1 - mean2; variance = sd1^2/nc1 + sd2^2/nc2",
  "parameters": {
    "measure": "MD",
    "zero_cell_correction_applied": false
  },
  "scale": "MD",
  "yi": -12.8,
  "vi": 0.14261254573723156,
  "standard_error": 0.3776407628120031,
  "effect": -12.8,
  "effect_delta": 0.0,
  "served_effect": -12.8,
  "served_standard_error": 0.3776407628120031,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "-12.8",
  "effect_hex": "-0x1.999999999999ap+3",
  "served_effect_hex": "-0x1.999999999999ap+3"
}
```

Denominator finding:

```json
{
  "code": "CLASS_DENOMINATOR_MISMATCH",
  "source_anchor": "A29",
  "served_n": [
    1306,
    655
  ],
  "available_data_n": [
    1212,
    577
  ],
  "explanation": "Producer reads outcome-level overall FAS n, while means/SDs come from class 0 with its own available-data n. PopulationDescription explicitly distinguishes the two.",
  "class_coherent_replay": {
    "effect": -12.8,
    "vi": 0.1573902368573079,
    "standard_error": 0.39672438399638094,
    "relative_se_increase": 0.05053379577532002,
    "status": "diagnostic only; no served data changed"
  }
}
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/semaglutide-obesity-weight/records.json#/records/118/id`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [292672,292682), bytes [294494,294504).

```text
"33567185"
```

**A02 — source identity nct**: `cache/semaglutide-obesity-weight/records.json#/records/118/nct`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [295632,295645), bytes [297458,297471).

```text
"NCT03548935"
```

**A03 — source identity doi**: `cache/semaglutide-obesity-weight/records.json#/records/118/doi`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [295594,295617), bytes [297420,297443).

```text
"10.1056/NEJMoa2032183"
```

**A04 — source identity year**: `cache/semaglutide-obesity-weight/records.json#/records/118/year`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [295540,295546), bytes [297366,297372).

```text
"2021"
```

**A05 — source identity title**: `cache/semaglutide-obesity-weight/records.json#/records/118/title`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [292724,292787), bytes [294546,294609).

```text
"Once-Weekly Semaglutide in Adults with Overweight or Obesity."
```

**A06 — registry context title**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/title`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1919362,1919389), bytes [1921721,1921748).

```text
"Change in Body Weight (%)"
```

**A07 — registry context type**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/type`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1919334,1919343), bytes [1921693,1921702).

```text
"PRIMARY"
```

**A08 — registry context timeFrame**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/timeFrame`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1920515,1920545), bytes [1922874,1922904).

```text
"Baseline (week 0) to week 68"
```

**A09 — registry context paramType**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/paramType`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1920393,1920399), bytes [1922752,1922758).

```text
"MEAN"
```

**A10 — registry context dispersionType**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/dispersionType`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1920427,1920447), bytes [1922786,1922806).

```text
"Standard Deviation"
```

**A11 — registry context unitOfMeasure**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/unitOfMeasure`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1920474,1920492), bytes [1922833,1922851).

```text
"Percentage point"
```

**A12 — registry context populationDescription**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/populationDescription`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1920159,1920333), bytes [1922518,1922692).

```text
"Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data."
```

**A13 — group identity**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/groups/0`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1920577,1921305), bytes [1922936,1923664).

```text
{
            "id": "OG000",
            "title": "Semaglutide 2.4 mg",
            "description": "Participants were to receive once-weekly subcutaneous (s.c) injection of 0.25 mg Semaglutide administered using a PDS290 pre-filled pen-injector with a 3 mL cartridge containing Semaglutide 1.0 mg/mL or 3.0 mg/mL and followed a fixed-dose escalation regimen, with dose increases every 4 weeks (to doses of 0.5, 1.0, 1.7 and 2.4 mg/week), aiming at reaching the maintenance dose of 2.4 mg after 16 weeks. Treatment was continued on the maintenance dose of 2.4 mg Semaglutide once weekly for an additional 52 weeks until week 68. The treatment was an adjunct to a reduced-calorie diet and increased physical activity."
          }
```

**A14 — group identity**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/groups/1`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1921317,1922058), bytes [1923676,1924417).

```text
{
            "id": "OG001",
            "title": "Placebo",
            "description": "Participants were to receive once-weekly subcutaneous (s.c) injection of 0.25 mg Semaglutide placebo administered using a PDS290 pre-filled pen-injector with a 3 mL cartridge containing Semaglutide placebo 1.0 mg/mL or 3.0 mg/mL and followed a fixed-dose escalation regimen, with dose increases every 4 weeks (to doses of 0.5, 1.0, 1.7 and 2.4 mg/week), aiming at reaching the maintenance dose of 2.4 mg Semaglutide placebo after 16 weeks. Treatment was continued on the maintenance dose of 2.4 mg once weekly for an additional 52 weeks until week 68. The treatment was an adjunct to a reduced-calorie diet and increased physical activity."
          }
```

**A15 — raw input mean1**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/0/categories/0/measurements/0/value`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1923042,1923049), bytes [1925401,1925408).

```text
"-15.6"
```

**A16 — input cell context mean1**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/0/categories/0/measurements/0`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1922971,1923107), bytes [1925330,1925466).

```text
{
                    "groupId": "OG000",
                    "value": "-15.6",
                    "spread": "10.1"
                  }
```

**A17 — raw input nc1**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/denoms/0/counts/0/value`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1922240,1922246), bytes [1924599,1924605).

```text
"1306"
```

**A18 — input cell context nc1**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/denoms/0/counts/0`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1922177,1922262), bytes [1924536,1924621).

```text
{
                "groupId": "OG000",
                "value": "1306"
              }
```

**A19 — raw input sd1**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/0/categories/0/measurements/0/spread`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1923081,1923087), bytes [1925440,1925446).

```text
"10.1"
```

**A20 — input cell context sd1**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/0/categories/0/measurements/0`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1922971,1923107), bytes [1925330,1925466).

```text
{
                    "groupId": "OG000",
                    "value": "-15.6",
                    "spread": "10.1"
                  }
```

**A21 — raw input mean2**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/0/categories/0/measurements/1/value`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1923198,1923204), bytes [1925557,1925563).

```text
"-2.8"
```

**A22 — input cell context mean2**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/0/categories/0/measurements/1`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1923127,1923261), bytes [1925486,1925620).

```text
{
                    "groupId": "OG001",
                    "value": "-2.8",
                    "spread": "6.5"
                  }
```

**A23 — raw input nc2**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/denoms/0/counts/1/value`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1922341,1922346), bytes [1924700,1924705).

```text
"655"
```

**A24 — input cell context nc2**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/denoms/0/counts/1`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1922278,1922362), bytes [1924637,1924721).

```text
{
                "groupId": "OG001",
                "value": "655"
              }
```

**A25 — raw input sd2**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/0/categories/0/measurements/1/spread`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1923236,1923241), bytes [1925595,1925600).

```text
"6.5"
```

**A26 — input cell context sd2**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/0/categories/0/measurements/1`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1923127,1923261), bytes [1925486,1925620).

```text
{
                    "groupId": "OG001",
                    "value": "-2.8",
                    "spread": "6.5"
                  }
```

**A27 — reported model-adjusted analyses (not the served raw reconstruction)**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/analyses`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1924258,1925319), bytes [1926617,1927678).

```text
[
          {
            "groupIds": [
              "OG000",
              "OG001"
            ],
            "groupDescription": "Treatment policy estimand",
            "nonInferiorityType": "SUPERIORITY",
            "pValue": "<.0001",
            "statisticalMethod": "ANCOVA",
            "paramType": "Treatment difference",
            "paramValue": "-12.44",
            "ciPctValue": "95",
            "ciNumSides": "TWO_SIDED",
            "ciLowerLimit": "-13.37",
            "ciUpperLimit": "-11.51"
          },
          {
            "groupIds": [
              "OG000",
              "OG001"
            ],
            "groupDescription": "Hypothetical estimand",
            "nonInferiorityType": "SUPERIORITY",
            "pValue": "<0.0001",
            "statisticalMethod": "ANCOVA",
            "paramType": "Treatment difference",
            "paramValue": "-14.42",
            "ciPctValue": "95",
            "ciNumSides": "TWO_SIDED",
            "ciLowerLimit": "-15.29",
            "ciUpperLimit": "-13.55"
          }
        ]
```

**A28 — selected measurement class**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/0/title`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1922454,1922483), bytes [1924813,1924842).

```text
"In-trial observation period"
```

**A29 — class-specific available-data denominators**: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0/classes/0/denoms`; SHA256 `8779e517b6f07fcfec0e548dc817f4dfdd3b4537e7070e4b4de86c7e2c26a7d9`; file characters [1922507,1922873), bytes [1924866,1925232).

```text
[
              {
                "units": "Participants",
                "counts": [
                  {
                    "groupId": "OG000",
                    "value": "1212"
                  },
                  {
                    "groupId": "OG001",
                    "value": "577"
                  }
                ]
              }
            ]
```

### UA-035 — PMID 30990260 — Trial-defined primary cardiorenal composite

Page: `sglt2-ckd-progression`. Served row: `docs/reviews/sglt2-ckd-progression/review.json#/outcomes/0/trials/1`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `REPORTED_TEXT`; recovery: `LOCATED_REPORTED_RESULT`.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| effect | `0.70` | 0.7 | A07 | A06 |  |
| ci_low | `0.59` | 0.59 | A08 | A06 |  |
| ci_high | `0.82` | 0.82 | A09 | A06 |  |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/extract.py::_effect_from_match",
  "source_sha256": "c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50",
  "scale": "HR",
  "effect": 0.7,
  "ci_low": 0.59,
  "ci_high": 0.82,
  "parameters": {
    "normalization": "harness/extract.py::_norm",
    "round_digits": null
  },
  "effect_delta": 0.0,
  "reported_tuple_exact": true,
  "formula": "Read reported point/CI from the located sentence after explicitly recorded decimal normalization; no count reconstruction.",
  "yi": -0.35667494393873245,
  "vi": 0.007052051363835542,
  "standard_error": 0.08397649292412455,
  "served_effect": 0.7,
  "served_standard_error": 0.08397649292412455,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.7",
  "effect_hex": "0x1.6666666666666p-1",
  "served_effect_hex": "0x1.6666666666666p-1"
}
```

Normalization: `harness/extract.py::_norm`, file SHA256 `c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50`. Changed: False. The following normalized form is a transformation, not a quotation:

```text
The relative risk of the primary outcome was 30% lower in the canagliflozin group than in the placebo group, with event rates of 43.2 and 61.2 per 1000 patient-years, respectively (hazard ratio, 0.70; 95% confidence interval [CI], 0.59 to 0.82; P = 0.00001).
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/sglt2-ckd-progression/records.json#/records/1/id`; SHA256 `964416f6cb8b1746eab4965809e83e0b3ec1b7f217f8783615bc6403b94408d0`; file characters [3266,3276), bytes [3274,3284).

```text
"30990260"
```

**A02 — source identity nct**: `cache/sglt2-ckd-progression/records.json#/records/1/nct`; SHA256 `964416f6cb8b1746eab4965809e83e0b3ec1b7f217f8783615bc6403b94408d0`; file characters [6261,6274), bytes [6281,6294).

```text
"NCT02065791"
```

**A03 — source identity doi**: `cache/sglt2-ckd-progression/records.json#/records/1/doi`; SHA256 `964416f6cb8b1746eab4965809e83e0b3ec1b7f217f8783615bc6403b94408d0`; file characters [6223,6246), bytes [6243,6266).

```text
"10.1056/NEJMoa1811744"
```

**A04 — source identity year**: `cache/sglt2-ckd-progression/records.json#/records/1/year`; SHA256 `964416f6cb8b1746eab4965809e83e0b3ec1b7f217f8783615bc6403b94408d0`; file characters [6169,6175), bytes [6189,6195).

```text
"2019"
```

**A05 — source identity title**: `cache/sglt2-ckd-progression/records.json#/records/1/title`; SHA256 `964416f6cb8b1746eab4965809e83e0b3ec1b7f217f8783615bc6403b94408d0`; file characters [3318,3388), bytes [3326,3396).

```text
"Canagliflozin and Renal Outcomes in Type 2 Diabetes and Nephropathy."
```

**A06 — source sentence**: `cache/sglt2-ckd-progression/records.json#/records/1/abstract`; SHA256 `964416f6cb8b1746eab4965809e83e0b3ec1b7f217f8783615bc6403b94408d0`; file characters [4756,5014), bytes [4764,5026). Decoded-string characters [1347,1605).

```text
The relative risk of the primary outcome was 30% lower in the canagliflozin group than in the placebo group, with event rates of 43.2 and 61.2 per 1000 patient-years, respectively (hazard ratio, 0.70; 95% confidence interval [CI], 0.59 to 0.82; P = 0.00001).
```

**A07 — raw numerical token effect**: `cache/sglt2-ckd-progression/records.json#/records/1/abstract`; SHA256 `964416f6cb8b1746eab4965809e83e0b3ec1b7f217f8783615bc6403b94408d0`; file characters [4951,4955), bytes [4959,4963). Decoded-string characters [1542,1546).

```text
0.70
```

**A08 — raw numerical token ci_low**: `cache/sglt2-ckd-progression/records.json#/records/1/abstract`; SHA256 `964416f6cb8b1746eab4965809e83e0b3ec1b7f217f8783615bc6403b94408d0`; file characters [4987,4991), bytes [4995,4999). Decoded-string characters [1578,1582).

```text
0.59
```

**A09 — raw numerical token ci_high**: `cache/sglt2-ckd-progression/records.json#/records/1/abstract`; SHA256 `964416f6cb8b1746eab4965809e83e0b3ec1b7f217f8783615bc6403b94408d0`; file characters [4995,4999), bytes [5003,5007). Decoded-string characters [1586,1590).

```text
0.82
```

### UA-042 — PMID 28824029 — All-cause mortality

Page: `spironolactone-hfref-mortality`. Served row: `docs/reviews/spironolactone-hfref-mortality/review.json#/outcomes/0/trials/0`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `REPORTED_TEXT`; recovery: `LOCATED_REPORTED_RESULT`.

Endpoint mismatch: the source HR is for CV death or HF hospitalization, but this served row is labelled All-cause mortality. Literal recovery does not validate that attribution.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| effect | `0.85` | 0.85 | A07 | A06 |  |
| ci_low | `0.53` | 0.53 | A08 | A06 |  |
| ci_high | `1.36` | 1.36 | A09 | A06 |  |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/extract.py::_effect_from_match",
  "source_sha256": "c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50",
  "scale": "HR",
  "effect": 0.85,
  "ci_low": 0.53,
  "ci_high": 1.36,
  "parameters": {
    "normalization": "harness/extract.py::_norm",
    "round_digits": null
  },
  "effect_delta": 0.0,
  "reported_tuple_exact": true,
  "formula": "Read reported point/CI from the located sentence after explicitly recorded decimal normalization; no count reconstruction.",
  "yi": -0.16251892949777494,
  "vi": 0.05779366724949472,
  "standard_error": 0.24040313485787726,
  "served_effect": 0.85,
  "served_standard_error": 0.24040313485787726,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.85",
  "effect_hex": "0x1.b333333333333p-1",
  "served_effect_hex": "0x1.b333333333333p-1"
}
```

Normalization: `harness/extract.py::_norm`, file SHA256 `c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50`. Changed: False. The following normalized form is a transformation, not a quotation:

```text
The primary endpoint occurred in 29.7% of patients in the eplerenone group vs. 32.7% in the placebo group [hazard ratio=0.85 (95% CI: 0.53-1.36)].
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/spironolactone-hfref-mortality/records.json#/records/220/id`; SHA256 `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`; file characters [458394,458404), bytes [459625,459635).

```text
"28824029"
```

**A02 — source identity nct**: `cache/spironolactone-hfref-mortality/records.json#/records/220/nct`; SHA256 `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`; file characters [460410,460423), bytes [461643,461656).

```text
"NCT01115855"
```

**A03 — source identity doi**: `cache/spironolactone-hfref-mortality/records.json#/records/220/doi`; SHA256 `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`; file characters [460372,460398), bytes [461605,461631).

```text
"10.1253/circj.CJ-17-0323"
```

**A04 — source identity year**: `cache/spironolactone-hfref-mortality/records.json#/records/220/year`; SHA256 `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`; file characters [460319,460323), bytes [461552,461556).

```text
2017
```

**A05 — source identity title**: `cache/spironolactone-hfref-mortality/records.json#/records/220/title`; SHA256 `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`; file characters [458440,458606), bytes [459671,459837).

```text
"Double-Blind, Randomized, Placebo-Controlled Trial Evaluating the Efficacy and Safety of Eplerenone in Japanese Patients With Chronic Heart Failure (J-EMPHASIS-HF)."
```

**A06 — source sentence**: `cache/spironolactone-hfref-mortality/records.json#/records/220/abstract`; SHA256 `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`; file characters [459628,459774), bytes [460861,461007). Decoded-string characters [1004,1150).

```text
The primary endpoint occurred in 29.7% of patients in the eplerenone group vs. 32.7% in the placebo group [hazard ratio=0.85 (95% CI: 0.53-1.36)].
```

**A07 — raw numerical token effect**: `cache/spironolactone-hfref-mortality/records.json#/records/220/abstract`; SHA256 `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`; file characters [459748,459752), bytes [460981,460985). Decoded-string characters [1124,1128).

```text
0.85
```

**A08 — raw numerical token ci_low**: `cache/spironolactone-hfref-mortality/records.json#/records/220/abstract`; SHA256 `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`; file characters [459762,459766), bytes [460995,460999). Decoded-string characters [1138,1142).

```text
0.53
```

**A09 — raw numerical token ci_high**: `cache/spironolactone-hfref-mortality/records.json#/records/220/abstract`; SHA256 `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`; file characters [459767,459771), bytes [461000,461004). Decoded-string characters [1143,1147).

```text
1.36
```

**A10 — endpoint definition**: `cache/spironolactone-hfref-mortality/records.json#/records/220/abstract`; SHA256 `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`; file characters [459528,459627), bytes [460761,460860). Decoded-string characters [904,1003).

```text
The primary endpoint was a composite of death from cardiovascular causes or hospitalization for HF.
```

### UA-043 — PMID 42670961 — Major vascular events

Page: `statins-primary-prevention-elderly`. Served row: `docs/reviews/statins-primary-prevention-elderly/review.json#/outcomes/0/trials/0`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `REPORTED_TEXT`; recovery: `LOCATED_REPORTED_RESULT`.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| effect | `0.70` | 0.7 | A07 | A06 |  |
| ci_low | `0.61` | 0.61 | A08 | A06 |  |
| ci_high | `0.82` | 0.82 | A09 | A06 |  |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/extract.py::_effect_from_match",
  "source_sha256": "c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50",
  "scale": "HR",
  "effect": 0.7,
  "ci_low": 0.61,
  "ci_high": 0.82,
  "parameters": {
    "normalization": "harness/extract.py::_norm",
    "round_digits": null
  },
  "effect_delta": 0.0,
  "reported_tuple_exact": true,
  "formula": "Read reported point/CI from the located sentence after explicitly recorded decimal normalization; no count reconstruction.",
  "yi": -0.35667494393873245,
  "vi": 0.005696045095207543,
  "standard_error": 0.07547214781101398,
  "served_effect": 0.7,
  "served_standard_error": 0.07547214781101398,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.7",
  "effect_hex": "0x1.6666666666666p-1",
  "served_effect_hex": "0x1.6666666666666p-1"
}
```

Normalization: `harness/extract.py::_norm`, file SHA256 `c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50`. Changed: False. The following normalized form is a transformation, not a quotation:

```text
After a median of 5.9 years, a primary cardiovascular event had occurred in 297 participants (10.9 events per 1000 person-years) in the atorvastatin group and in 412 participants (15.5 events per 1000 person-years) in the placebo group (hazard ratio, 0.70; 95% confidence interval [CI], 0.61 to 0.82; P<0.001).
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/statins-primary-prevention-elderly/records.json#/records/3/id`; SHA256 `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`; file characters [9411,9421), bytes [9431,9441).

```text
"42670961"
```

**A02 — source identity nct**: `cache/statins-primary-prevention-elderly/records.json#/records/3/nct`; SHA256 `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`; file characters [12116,12129), bytes [12142,12155).

```text
"NCT02099123"
```

**A03 — source identity doi**: `cache/statins-primary-prevention-elderly/records.json#/records/3/doi`; SHA256 `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`; file characters [12078,12101), bytes [12104,12127).

```text
"10.1056/NEJMoa2607314"
```

**A04 — source identity year**: `cache/statins-primary-prevention-elderly/records.json#/records/3/year`; SHA256 `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`; file characters [12024,12030), bytes [12050,12056).

```text
"2026"
```

**A05 — source identity title**: `cache/statins-primary-prevention-elderly/records.json#/records/3/title`; SHA256 `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`; file characters [9463,9547), bytes [9483,9567).

```text
"Atorvastatin, Cardiovascular Events, and Disability-free Survival in Older Adults."
```

**A06 — source sentence**: `cache/statins-primary-prevention-elderly/records.json#/records/3/abstract`; SHA256 `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`; file characters [10717,11027), bytes [10739,11049). Decoded-string characters [1149,1459).

```text
After a median of 5.9 years, a primary cardiovascular event had occurred in 297 participants (10.9 events per 1000 person-years) in the atorvastatin group and in 412 participants (15.5 events per 1000 person-years) in the placebo group (hazard ratio, 0.70; 95% confidence interval [CI], 0.61 to 0.82; P<0.001).
```

**A07 — raw numerical token effect**: `cache/statins-primary-prevention-elderly/records.json#/records/3/abstract`; SHA256 `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`; file characters [10968,10972), bytes [10990,10994). Decoded-string characters [1400,1404).

```text
0.70
```

**A08 — raw numerical token ci_low**: `cache/statins-primary-prevention-elderly/records.json#/records/3/abstract`; SHA256 `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`; file characters [11004,11008), bytes [11026,11030). Decoded-string characters [1436,1440).

```text
0.61
```

**A09 — raw numerical token ci_high**: `cache/statins-primary-prevention-elderly/records.json#/records/3/abstract`; SHA256 `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`; file characters [11012,11016), bytes [11034,11038). Decoded-string characters [1444,1448).

```text
0.82
```

### UA-044 — PMID 33631066 — Serious adverse events

Page: `tocilizumab-covid19-mortality`. Served row: `docs/reviews/tocilizumab-covid19-mortality/review.json#/outcomes/1/trials/0`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `COUNT_DERIVED_OR`; recovery: `LOCATED_FULL_INPUT_SET`.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| ai | `103` | 103 | A07 | A06 | intervention |
| n1i | `295` | 295 | A08 | A06 | intervention |
| ci | `55` | 55 | A09 | A06 | comparator |
| n2i | `143` | 143 | A10 | A06 | comparator |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/synth.py::Study.yi_vi",
  "source_sha256": "735d9793ed5e28119be22390e73daea3c74732291c3279687abc8cc3028532dc",
  "formula": "OR = ai*(n2i-ci)/((n1i-ai)*ci); variance(log OR) = 1/ai + 1/(n1i-ai) + 1/ci + 1/(n2i-ci); no zero-cell correction triggered",
  "parameters": {
    "measure": "OR",
    "zero_cell_correction_applied": false
  },
  "scale": "OR",
  "yi": -0.15276275455241028,
  "vi": 0.04446252574286555,
  "standard_error": 0.21086138988175515,
  "effect": 0.8583333333333333,
  "effect_delta": 0.0,
  "served_effect": 0.8583333333333333,
  "served_standard_error": 0.21086138988175515,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.8583333333333333",
  "effect_hex": "0x1.b777777777777p-1",
  "served_effect_hex": "0x1.b777777777777p-1"
}
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/tocilizumab-covid19-mortality/records.json#/records/10/id`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [19239,19249), bytes [19306,19316).

```text
"33631066"
```

**A02 — source identity nct**: `cache/tocilizumab-covid19-mortality/records.json#/records/10/nct`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [21982,21995), bytes [22057,22070).

```text
"NCT04320615"
```

**A03 — source identity doi**: `cache/tocilizumab-covid19-mortality/records.json#/records/10/doi`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [21944,21967), bytes [22019,22042).

```text
"10.1056/NEJMoa2028700"
```

**A04 — source identity year**: `cache/tocilizumab-covid19-mortality/records.json#/records/10/year`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [21890,21896), bytes [21965,21971).

```text
"2021"
```

**A05 — source identity title**: `cache/tocilizumab-covid19-mortality/records.json#/records/10/title`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [19291,19361), bytes [19358,19428).

```text
"Tocilizumab in Hospitalized Patients with Severe Covid-19 Pneumonia."
```

**A06 — source sentence**: `cache/tocilizumab-covid19-mortality/records.json#/records/10/abstract`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [20974,21143), bytes [21045,21214). Decoded-string characters [1592,1761).

```text
In the safety population, serious adverse events occurred in 103 of 295 patients (34.9%) in the tocilizumab group and in 55 of 143 patients (38.5%) in the placebo group.
```

**A07 — raw input ai**: `cache/tocilizumab-covid19-mortality/records.json#/records/10/abstract`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [21035,21038), bytes [21106,21109). Decoded-string characters [1653,1656).

```text
103
```

**A08 — raw input n1i**: `cache/tocilizumab-covid19-mortality/records.json#/records/10/abstract`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [21042,21045), bytes [21113,21116). Decoded-string characters [1660,1663).

```text
295
```

**A09 — raw input ci**: `cache/tocilizumab-covid19-mortality/records.json#/records/10/abstract`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [21095,21097), bytes [21166,21168). Decoded-string characters [1713,1715).

```text
55
```

**A10 — raw input n2i**: `cache/tocilizumab-covid19-mortality/records.json#/records/10/abstract`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [21101,21104), bytes [21172,21175). Decoded-string characters [1719,1722).

```text
143
```

### UA-045 — PMID 33332779 — Serious adverse events

Page: `tocilizumab-covid19-mortality`. Served row: `docs/reviews/tocilizumab-covid19-mortality/review.json#/outcomes/1/trials/1`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `COUNT_DERIVED_OR`; recovery: `LOCATED_FULL_INPUT_SET`.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| ai | `38` | 38 | A07 | A06 | intervention |
| n1i | `250` | 250 | A08 | A06 | intervention |
| ci | `25` | 25 | A09 | A06 | comparator |
| n2i | `127` | 127 | A10 | A06 | comparator |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/synth.py::Study.yi_vi",
  "source_sha256": "735d9793ed5e28119be22390e73daea3c74732291c3279687abc8cc3028532dc",
  "formula": "OR = ai*(n2i-ci)/((n1i-ai)*ci); variance(log OR) = 1/ai + 1/(n1i-ai) + 1/ci + 1/(n2i-ci); no zero-cell correction triggered",
  "parameters": {
    "measure": "OR",
    "zero_cell_correction_applied": false
  },
  "scale": "OR",
  "yi": -0.3129031265295564,
  "vi": 0.08083669217438713,
  "standard_error": 0.2843179420549944,
  "effect": 0.7313207547169811,
  "effect_delta": 0.0,
  "served_effect": 0.7313207547169811,
  "served_standard_error": 0.2843179420549944,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.7313207547169811",
  "effect_hex": "0x1.766fac88ca7b4p-1",
  "served_effect_hex": "0x1.766fac88ca7b4p-1"
}
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/tocilizumab-covid19-mortality/records.json#/records/11/id`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [22021,22031), bytes [22096,22106).

```text
"33332779"
```

**A02 — source identity nct**: `cache/tocilizumab-covid19-mortality/records.json#/records/11/nct`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [24836,24849), bytes [24917,24930).

```text
"NCT04372186"
```

**A03 — source identity doi**: `cache/tocilizumab-covid19-mortality/records.json#/records/11/doi`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [24798,24821), bytes [24879,24902).

```text
"10.1056/NEJMoa2030340"
```

**A04 — source identity year**: `cache/tocilizumab-covid19-mortality/records.json#/records/11/year`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [24744,24750), bytes [24825,24831).

```text
"2021"
```

**A05 — source identity title**: `cache/tocilizumab-covid19-mortality/records.json#/records/11/title`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [22073,22136), bytes [22148,22211).

```text
"Tocilizumab in Patients Hospitalized with Covid-19 Pneumonia."
```

**A06 — source sentence**: `cache/tocilizumab-covid19-mortality/records.json#/records/11/abstract`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [24031,24196), bytes [24112,24277). Decoded-string characters [1874,2039).

```text
In the safety population, serious adverse events occurred in 38 of 250 patients (15.2%) in the tocilizumab group and 25 of 127 patients (19.7%) in the placebo group.
```

**A07 — raw input ai**: `cache/tocilizumab-covid19-mortality/records.json#/records/11/abstract`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [24092,24094), bytes [24173,24175). Decoded-string characters [1935,1937).

```text
38
```

**A08 — raw input n1i**: `cache/tocilizumab-covid19-mortality/records.json#/records/11/abstract`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [24098,24101), bytes [24179,24182). Decoded-string characters [1941,1944).

```text
250
```

**A09 — raw input ci**: `cache/tocilizumab-covid19-mortality/records.json#/records/11/abstract`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [24148,24150), bytes [24229,24231). Decoded-string characters [1991,1993).

```text
25
```

**A10 — raw input n2i**: `cache/tocilizumab-covid19-mortality/records.json#/records/11/abstract`; SHA256 `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`; file characters [24154,24157), bytes [24235,24238). Decoded-string characters [1997,2000).

```text
127
```

### UA-046 — PMID 28456509 — Death due to bleeding

Page: `tranexamic-acid-pph`. Served row: `docs/reviews/tranexamic-acid-pph/review.json#/outcomes/0/trials/0`. Admission: `MIGRATION_STATE_UNBOUND_LEGACY`.

Source kind: `REPORTED_TEXT`; recovery: `LOCATED_REPORTED_RESULT`.

| Input | Raw value | Parsed value | Value anchor | Context anchor | Group |
| --- | --- | --- | --- | --- | --- |
| effect | `0·81` | 0.81 | A07 | A06 |  |
| ci_low | `0·65` | 0.65 | A08 | A06 |  |
| ci_high | `1·00` | 1 | A09 | A06 |  |

Replay (full binary-float precision; `EXACT` means equality to the stored number, not just page rounding):

```json
{
  "function": "harness/extract.py::_effect_from_match",
  "source_sha256": "c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50",
  "scale": "RR",
  "effect": 0.81,
  "ci_low": 0.65,
  "ci_high": 1.0,
  "parameters": {
    "normalization": "harness/extract.py::_norm",
    "round_digits": null
  },
  "effect_delta": 0.0,
  "reported_tuple_exact": true,
  "formula": "Read reported point/CI from the located sentence after explicitly recorded decimal normalization; no count reconstruction.",
  "yi": -0.21072103131565253,
  "vi": 0.012077047383498081,
  "standard_error": 0.1098956204018071,
  "served_effect": 0.81,
  "served_standard_error": 0.1098956204018071,
  "standard_error_delta": 0.0,
  "standard_error_exact": true,
  "effect_exact": true,
  "comparison": "EXACT",
  "effect_repr": "0.81",
  "effect_hex": "0x1.9eb851eb851ecp-1",
  "served_effect_hex": "0x1.9eb851eb851ecp-1"
}
```

Normalization: `harness/extract.py::_norm`, file SHA256 `c7083c851ec430735c78d452de2cd8bad761913f9dff68a256117b613a117f50`. Changed: True. The following normalized form is a transformation, not a quotation:

```text
Death due to bleeding was significantly reduced in women given tranexamic acid (155 [1.5%] of 10 036 patients vs 191 [1.9%] of 9985 in the placebo group, risk ratio [RR] 0.81, 95% CI 0.65-1.00; p=0.045), especially in women given treatment within 3 h of giving birth (89 [1.2%] in the tranexamic acid group vs 127 [1.7%] in the placebo group, RR 0.69, 95% CI 0.52-0.91; p=0.008).
```

Located evidence (all ranges are zero-based, end-exclusive; SHA256 hashes original whole-file bytes):

**A01 — source identity id**: `cache/tranexamic-acid-pph/records.json#/records/47/id`; SHA256 `283b2c2862f0dd20e2087c7625f444acf2093d7bf70482f7ebcb52ac40162520`; file characters [121566,121576), bytes [122052,122062).

```text
"28456509"
```

**A02 — source identity nct**: `cache/tranexamic-acid-pph/records.json#/records/47/nct`; SHA256 `283b2c2862f0dd20e2087c7625f444acf2093d7bf70482f7ebcb52ac40162520`; file characters [125564,125577), bytes [126090,126103).

```text
"NCT00872469"
```

**A03 — source identity doi**: `cache/tranexamic-acid-pph/records.json#/records/47/doi`; SHA256 `283b2c2862f0dd20e2087c7625f444acf2093d7bf70482f7ebcb52ac40162520`; file characters [125518,125549), bytes [126044,126075).

```text
"10.1016/S0140-6736(17)30638-4"
```

**A04 — source identity year**: `cache/tranexamic-acid-pph/records.json#/records/47/year`; SHA256 `283b2c2862f0dd20e2087c7625f444acf2093d7bf70482f7ebcb52ac40162520`; file characters [125470,125476), bytes [125996,126002).

```text
"2017"
```

**A05 — source identity title**: `cache/tranexamic-acid-pph/records.json#/records/47/title`; SHA256 `283b2c2862f0dd20e2087c7625f444acf2093d7bf70482f7ebcb52ac40162520`; file characters [121618,121833), bytes [122104,122319).

```text
"Effect of early tranexamic acid administration on mortality, hysterectomy, and other morbidities in women with post-partum haemorrhage (WOMAN): an international, randomised, double-blind, placebo-controlled trial."
```

**A06 — source sentence**: `cache/tranexamic-acid-pph/records.json#/records/47/abstract`; SHA256 `283b2c2862f0dd20e2087c7625f444acf2093d7bf70482f7ebcb52ac40162520`; file characters [123951,124330), bytes [124451,124844). Decoded-string characters [2097,2476).

```text
Death due to bleeding was significantly reduced in women given tranexamic acid (155 [1·5%] of 10 036 patients vs 191 [1·9%] of 9985 in the placebo group, risk ratio [RR] 0·81, 95% CI 0·65-1·00; p=0·045), especially in women given treatment within 3 h of giving birth (89 [1·2%] in the tranexamic acid group vs 127 [1·7%] in the placebo group, RR 0·69, 95% CI 0·52-0·91; p=0·008).
```

**A07 — raw numerical token effect**: `cache/tranexamic-acid-pph/records.json#/records/47/abstract`; SHA256 `283b2c2862f0dd20e2087c7625f444acf2093d7bf70482f7ebcb52ac40162520`; file characters [124121,124125), bytes [124625,124630). Decoded-string characters [2267,2271).

```text
0·81
```

**A08 — raw numerical token ci_low**: `cache/tranexamic-acid-pph/records.json#/records/47/abstract`; SHA256 `283b2c2862f0dd20e2087c7625f444acf2093d7bf70482f7ebcb52ac40162520`; file characters [124134,124138), bytes [124639,124644). Decoded-string characters [2280,2284).

```text
0·65
```

**A09 — raw numerical token ci_high**: `cache/tranexamic-acid-pph/records.json#/records/47/abstract`; SHA256 `283b2c2862f0dd20e2087c7625f444acf2093d7bf70482f7ebcb52ac40162520`; file characters [124139,124143), bytes [124645,124650). Decoded-string characters [2285,2289).

```text
1·00
```

## Totals and interpretation

23 of 23 target rows now have located reported spans/cells or all inputs used by the producer; 0 of 23 remain unlocated. Replaying the exact harness transformation (14 of 23 derived rows) or rereading the reported values (9 of 23 reported rows) matches the served point exactly for 23 of 23; 0 of 23 match only to display rounding; 0 of 23 fail numerical replay. All 23 of 23 served standard errors also replay exactly. This is source-location closure, not scientific/admission closure. Two of 14 derived rows (UA-004 and UA-005, PMID 21873705: recurrent pericarditis and symptom persistence at 72 hours) explicitly round the RRR complement to four decimals; their pre-round binary-float point is 0.43999999999999995 rather than the served 0.44. Two of 14 derived rows (UA-032 PMID 33625476 and UA-033 PMID 33567185, semaglutide percent weight change) use located but incompatible overall versus class-specific denominators. UA-042 PMID 28824029 locates a composite HR under an all-cause-mortality row. UA-039 DAPA-HF retains a one-group analysis selector ambiguity. None of these conflicts is cured by numerical replay.

```json
{
  "denominator": 23,
  "denominator_name": "lane-UA unlocated served trial-outcome rows",
  "now_locatable": 23,
  "still_unlocated": 0,
  "unlocated_rows": [],
  "cause_counts": {
    "SOURCE_EXISTS_NOT_RECORDED": 8,
    "OTHER": 1,
    "NEVER_HAD_A_SOURCE": 14
  },
  "exact_harness_or_direct_source_replay": 23,
  "rounding_only_replay": 0,
  "mismatch_replay": 0,
  "replay_rows": {
    "EXACT": [
      "UA-021",
      "UA-039",
      "UA-001",
      "UA-002",
      "UA-003",
      "UA-004",
      "UA-005",
      "UA-006",
      "UA-007",
      "UA-008",
      "UA-009",
      "UA-010",
      "UA-014",
      "UA-027",
      "UA-030",
      "UA-032",
      "UA-033",
      "UA-035",
      "UA-042",
      "UA-043",
      "UA-044",
      "UA-045",
      "UA-046"
    ],
    "ROUNDING_ONLY": [],
    "MISMATCH": []
  },
  "derived_rows": 14,
  "derived_rows_exact_harness_replay": 14,
  "direct_reported_rows": 9,
  "explicit_producer_rounding_rows": [
    "UA-004",
    "UA-005"
  ],
  "pre_round_binary_float_effect_differs_rows": [
    "UA-004",
    "UA-005"
  ],
  "denominator_conflict_rows": [
    "UA-032",
    "UA-033"
  ],
  "endpoint_mismatch_rows": [
    "UA-042"
  ],
  "registry_analysis_group_ambiguity_rows": [
    "UA-039"
  ],
  "prose": "23 of 23 target rows now have located reported spans/cells or all inputs used by the producer; 0 of 23 remain unlocated. Replaying the exact harness transformation (14 of 23 derived rows) or rereading the reported values (9 of 23 reported rows) matches the served point exactly for 23 of 23; 0 of 23 match only to display rounding; 0 of 23 fail numerical replay. All 23 of 23 served standard errors also replay exactly. This is source-location closure, not scientific/admission closure. Two of 14 derived rows (UA-004 and UA-005, PMID 21873705: recurrent pericarditis and symptom persistence at 72 hours) explicitly round the RRR complement to four decimals; their pre-round binary-float point is 0.43999999999999995 rather than the served 0.44. Two of 14 derived rows (UA-032 PMID 33625476 and UA-033 PMID 33567185, semaglutide percent weight change) use located but incompatible overall versus class-specific denominators. UA-042 PMID 28824029 locates a composite HR under an all-cause-mortality row. UA-039 DAPA-HF retains a one-group analysis selector ambiguity. None of these conflicts is cured by numerical replay."
}
```

## Static versus dynamic disclosure

| Item | Disclosure |
| --- | --- |
| Target membership | Dynamic: read ua.json, then exact equality against served review JSON |
| Source values and identities | Dynamic: reread held records, independently parse values, validate IDs and registry keys |
| Row selectors | Static audit choices suggested by UA, verified against original bytes and context |
| Formulas and parameters | Existing checked-out harness functions; explicit rounding and scale recorded |
| Proposed schema and page text | Static design only; no implementation or admission promotion |

## Proposed derivation record — design only

Place a versioned `study_effect.derivation_record` beside `study_effect.source_provenance`; retain the original source representation. The record binds the exact row key and typed PMID/NCT identity to the outcome, estimand, intervention/comparator mapping, time window, analysis population, and selected registry class/category/analysis. Each input stores its raw string, typed value and unit, source file hash, JSON pointer or document selector, verbatim span, character/byte offsets, contextual group and denominator anchors, and any explicit normalization with the untouched original.

The recipe stores the function module/qualified name, repository commit plus file SHA256, runtime/library versions, ordered arguments, measure, zero-cell correction, transformation order and rounding. It stores full-precision yi, vi, SE, estimate and interval where applicable, alongside the served values, absolute differences, exact comparison, and a separately declared display-rounding comparison. A direct reported registry effect uses a typed structured-source record rather than pretending to be derived.

`DERIVED_WITH_VERIFIED_INPUTS` requires all necessary inputs located in hash-matched bytes, exact role/group/population/denominator compatibility, and successful deterministic replay. `DERIVED_INPUTS_UNANCHORED` applies if any input lacks a location or hash match; it fails closed. A separate `DERIVED_INPUTS_INCONSISTENT` or refusal reason is necessary for located but incompatible inputs, including the semaglutide denominator mismatch. A replay pass alone must never promote a row to ADMISSIBLE. Endpoint mismatches and ambiguous contrast selectors remain separate blocking predicates.

Page wording for a verified derivation: “Calculated from verified source inputs; view each input and replay.” Show the actual formula, inputs, units, source links, full precision and displayed rounding. For unanchored inputs: “Calculated result withheld: one or more source inputs cannot be located.” For incompatible inputs: “Calculated result withheld: source inputs refer to different analysis populations.” For REWIND: “Reported HR; original decimal typography preserved; normalized value shown.” For DAPA-HF: “Reported registry HR; outcome index 1, analysis index 0; source analysis lists group OG001 only.”

No new schema, gate, page or harness code is implemented by this lane. The local `.tmp/src_audit.py` helper only reads evidence and writes the two requested audit artefacts.

## Validation and limits

Zero-based half-open Unicode character offsets; file_char_* use literal UTF-8-decoded file without newline translation; byte_* use original file bytes. start/end for prose are within the JSON string selected by pointer. SHA256 always hashes the complete file bytes.

No claim that a numerical value appears nowhere in all held documents is made. Negative searches are explicitly scoped and paired with a positive control that fires. UA classifications are retained as provenance history, not asserted as exhaustive absence proofs. All facts and identifiers are verified against held records; no network refresh or independent publication authenticity check is represented.

```json
{
  "completed_rows": 23,
  "served_row_equality_checks": 23,
  "identity_checks": 23,
  "anchor_count": 324,
  "all_anchor_file_slices_validated": true,
  "all_anchor_byte_slices_validated": true,
  "all_prose_find_controls_pass": true,
  "all_source_file_hashes_match_ua": true,
  "all_standard_errors_exact": true,
  "audit_helper": ".tmp/src_audit.py",
  "audit_helper_sha256": "abfd4aaffd326da30cd650b8a574848ddbbed1c84ff99221ff70fc0e405400db",
  "independent_validation": {
    "status": "PASS",
    "rows": {
      "passed": 23,
      "denominator": 23,
      "unit": "target trial-outcome rows"
    },
    "anchors": {
      "passed": 324,
      "denominator": 324,
      "unit": "saved evidence anchors"
    },
    "input_tokens": {
      "passed": 89,
      "denominator": 89,
      "unit": "raw numerical input tokens"
    },
    "held_source_files": 15,
    "checks": [
      "independently resolve JSON pointers",
      "whole-file SHA256",
      "literal file character slices",
      "original UTF-8 byte slices",
      "decoded prose spans",
      "text.find positive controls",
      "input tokens within context spans",
      "served effect and SE equality",
      "reported CI tuple equality",
      "semaglutide class-denominator diagnostic recalculation",
      "UTF-8 without BOM"
    ],
    "method": "Separate inline Python validator, independent of the audit helper parser."
  },
  "focused_tests": {
    "command": "python -B -m pytest -q -p no:cacheprovider tests/test_synth.py tests/test_extract_class.py",
    "status": "PASS",
    "passed": 44,
    "denominator": 44,
    "unit": "collected tests",
    "elapsed_seconds": 3.0
  },
  "second_pass": {
    "status": "PASS_WITH_RECORDED_FINDINGS",
    "scope": "PMID/NCT identity, held publication year/DOI, endpoint and group labels, selected outcome/analysis/class, denominators, full precision and normalization. No external source refresh.",
    "findings": [
      "UA-032 and UA-033: class denominators differ from overall FAS n used by producer",
      "UA-042: cited composite HR under all-cause-mortality row",
      "UA-039: analyses[0].groupIds contains only OG001"
    ]
  },
  "worktree_check": {
    "git_diff_check": "PASS",
    "tracked_changes": 0,
    "commit_or_push_performed": false,
    "production_edits": false,
    "processes_signalled": false
  }
}
```
