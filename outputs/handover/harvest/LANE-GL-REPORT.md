# LANE GL report

Base and final HEAD: `dcde90b139a8466b35b110162d160494d3bff05d`. No commit, push, deployment, or network source acquisition. The standalone LANE_BASE.txt was absent; the base SHA stated in LANE_PROMPT.md matches HEAD.

The B-prime page and both delivery strands were rebuilt. All numerical inputs come from held trial publications or FDA documents. The release gate remains refused; this report does not certify the page as shipped. Remaining prose and audit debt is enumerated below.

## Measured strands

| Strand | k | HR | HKSJ 95% CI | tau² | t(k−1) prediction interval |
|---|---:|---:|---|---:|---|
| MEASURED CONVENTIONAL_GLP1RA | 10 | 0.8613375078 | 0.8069437883–0.9193977488 | 0.0026952651 | 0.7530592916–0.9851844479 |
| MEASURED GLP1RA_ANY_DELIVERY | 11 | 0.8672878085 | 0.7998743599–0.9403828657 | 0.0073698925 | 0.7046341607–1.0674874775 |

Engine: unchanged `harness.synth.pool`, Paule–Mandel tau², HKSJ with variance floor and t(k−1). CONVENTIONAL_GLP1RA is primary under the retrospective B-prime class-boundary decision; GLP1RA_ANY_DELIVERY adds continuous-delivery ITCA 650.

The eight legacy primary trials remain. ELIXA and FLOW increase the primary from 8 to 10; FREEDOM-CVO increases the any-delivery strand to 11. Its end-of-treatment HR 1.36 (0.96, 1.92) is rendered as a sensitivity value and never pooled.

FLOW: value from PMID 38785209, level 1; endpoint identity from the recorded AACT design_outcomes row for NCT03819153, level 3. The local 2026-08-30 snapshot row was inspected and matches the adjudication title, description and timeframe. The registry description says on-treatment; the abstract does not bind the censoring of HR 0.82. `censoring=UNKNOWN` and `analysis_set=UNKNOWN` remain typed. No harness/effect_type.py TY binding-axis gate exists on this base; FLOW is pooled with that caveat, not assigned on-study censoring by assumption. The effect is not taken from the registry or from a meta-analysis.

AACT design eligibility evidence for all three additions is recorded in [LANE-GL-AACT-CHECK.json](LANE-GL-AACT-CHECK.json). SELECT is retrieved and refused as X2 (population without diabetes); Giugliano is retrieved and refused as X1 (meta-analysis). Eligibility and target-result status are separate rendered columns. No newly pooled trial remains in the known-missing panel.

## Provenance coverage

MEASURED 11 of 11 distinct pooled trial rows are FACT; 0 of 11 are UNVERIFIED_FACT. Across the graph's 12 FACT objects (including the separately rendered sensitivity value), 0 of 12 fail source verification.

Every row has source_level, document reference, full document digest, exact located span and character offset. The eight legacy rows use the unchanged committed records.json as their held document. Decimal middots are recognized as decimal notation only for numeric checking; bytes are never normalized for source verification. FDA CRLF bytes remain in the source objects; HTML display normalizes newlines, making the rendered page replayable through universal-newline readers.

Legacy retrieval dates have day precision, explicitly labelled. FLOW records the measured offline local-read timestamp in source_reads.json; its original remote retrieval time is not invented.

## Admission spans (verbatim JSON string values)

Offsets count decoded UTF-8 characters, from zero. Escaped CRLF in the following JSON represents exact held bytes, not editorial whitespace.

```json
{
  "pmid": "26630143",
  "source_level": 2,
  "document_ref": "outputs/handover/glp1_regulatory/held/208471Orig1s000StatR.pdf",
  "document_sha256": "cf2b3ef92247b85e7be7c3b56c3cc4fc0af007b3950acee95eea9c995653db38",
  "extracted_text": "outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt",
  "extracted_text_sha256": "952b8088e14b457d97364f13bb0f9407803bf875faed5fa30d995972e2687a26",
  "span_offset": 47847,
  "source": "ITT analyses (on-study and on-treatment) of MACE, defined as cardiovascular death, non-fatal \r\nMI, and non-fatal stroke, are consistent with those of MACE+ (Table 8). The reason for the \r\nsimilarity is that only 0.3% of subjects in the ITT population experienced hospitalization for \r\nunstable angina. For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and \r\nlixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, \r\n1.172) with a point estimate of 1.02.",
  "effect": 1.02,
  "ci_low": 0.887,
  "ci_high": 1.172,
  "analysis_set": "ITT",
  "censoring": "on-study",
  "timepoint": "end of randomised follow-up"
}
```

```json
{
  "pmid": "38785209",
  "source_level": 1,
  "document_ref": "outputs/search_v2/lanes/R3/lane_r3/raw/058-pubmed-glp1-ra-mace-t2d-flow-efetch.xml",
  "document_sha256": "2fc31abdf24b1a27d1ee79dd424b3faac680c376e1c86b819c0d0f1bd6c89e40",
  "extracted_text": "outputs/search_v2/lanes/R3/lane_r3/raw/058-pubmed-glp1-ra-mace-t2d-flow-efetch.xml",
  "extracted_text_sha256": "2fc31abdf24b1a27d1ee79dd424b3faac680c376e1c86b819c0d0f1bd6c89e40",
  "span_offset": 3249,
  "source": "the risk of major cardiovascular events 18% lower (hazard ratio, 0.82; 95% CI, 0.68 to 0.98; P&#x2009;=&#x2009;0.029)",
  "effect": 0.82,
  "ci_low": 0.68,
  "ci_high": 0.98,
  "analysis_set": "UNKNOWN",
  "censoring": "UNKNOWN",
  "timepoint": "end of randomised follow-up"
}
```

```json
{
  "pmid": "34873344",
  "source_level": 2,
  "document_ref": "outputs/handover/glp1_regulatory/held/fda_media_172242_ITCA650.pdf",
  "document_sha256": "719362393b2029c2d4a081ab1bc69647034b2168efe686808d419f16177f0103",
  "extracted_text": "outputs/handover/glp1_regulatory/fda_media_172242_ITCA650.pdf.txt",
  "extracted_text_sha256": "e27b9985959e139b9c84f15b7e364d3c82a2fed861819e2b777f6b3f5aef963e",
  "span_offset": 157878,
  "source": "Table 19. Time to First Occurrence of 3-Point MACE (CV Death, Nonfatal MI, Nonfatal Stroke) and 4-Point MACE (CV \r\nDeath, Nonfatal MI, Nonfatal Stroke, Unstable Angina) – ITT Population End of Study, FREEDOM (CLP-107) \r\nMACE Type \r\nITCA 650 Number of \r\nEvents/Total No. (%) \r\nIR (n/100 PY) \r\nControl Number of \r\nEvents/Total No. (%) \r\nIR (n/100 PY) HR (95% CI)** \r\n3-Point MACE* 85/2075 (4.1%) \r\n2.94 \r\n69/2081 (3.3%) \r\n2.37 1.24 (0.90, 1.70) \r\n4-Point MACE 95/2075 (4.6%) \r\n3.29 \r\n79/2081 (3.8%) \r\n2.72 1.21 (0.90, 1.63) \r\nSource: CDER Review staff. Analysis: R v. 4.2 (MACE.R); data: adef.xpt from SDN0000. \r\n* One hundred fifty-four positively adjudicated 3-point MACE events. \r\n** Based on a Cox proportional hazards regression model.",
  "effect": 1.24,
  "ci_low": 0.9,
  "ci_high": 1.7,
  "analysis_set": "ITT",
  "censoring": "on-study",
  "timepoint": "end of randomised follow-up"
}
```

## Base plants: failing output verbatim

The plants were written and run before implementation against the stated base. The first preliminary run exposed a test-reader newline issue; that reader was corrected to read raw bytes, and the archived base run below fails on the actual three intended contracts.

```text
FFF                                                                      [100%]
================================== FAILURES ===================================
__________________ test_glp1_unlocated_verified_row_refused ___________________
tests\test_glp1_lane.py:31: in test_glp1_unlocated_verified_row_refused
    assert not outcome['trials'], f"UNLOCATED ROW WOULD POOL: {outcome['trials']}"
E   AssertionError: UNLOCATED ROW WOULD POOL: [{'label': 'ELIXA', 'id': 'PMID 26630143', 'effect': 1.02, 'ci_low': 0.887, 'ci_high': 1.172, 'scale': 'HR', 'provenance': 'fulltext_verified', 'source': 'ITT analyses (on-study and on-treatment) of MACE, defined as cardiovascular death, non-fatal \r\nMI, and non-fatal stroke, are consistent with those of MACE+ (Table 8). The reason for the \r\nsimilarity is that only 0.3% of subjects in the ITT population experienced hospitalization for \r\nunstable angina. For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and \r\nlixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, \r\n1.172) with a point estimate of 1.02. INVENTED SPAN', 'derivation': 'reported', 'selection_rule': 'KEEP_REPORTED_EFFECT', 'selected_estimator': 'published_effect_ci', 'alternatives': [], 'verified': 'verified', 'verify_basis': 'effect present in committed source', 'design': {'unit_of_randomisation': 'UNKNOWN', 'design': 'UNKNOWN', 'estimator_source': 'PUBLISHED_UNADJUSTED', 'correlation_handling': {'method': 'none', 'evidence': []}, 'se_provenance': 'synth.Study.yi_vi:reported-effect-ci', 'basis': [], 'design_action': {'action': 'DESIGN_UNPROVEN', 'gate_id': 'design-key:design-unproven', 'decision_state': 'design not established from committed evidence; pooled through the parallel path on an assumption the harness could not verify', 'reason': 'no committed design evidence (registry intervention model or design phrase); UNKNOWN is not PARALLEL', 'validity_critical': False}}, 'study_effect': {'effect_estimate': 1.02, 'standard_error': 0.07107834379231279, 'estimand': 'HR', 'analysis_population': 'UNKNOWN', 'randomisation_unit': 'UNKNOWN', 'study_design': 'UNKNOWN', 'estimator_method': 'PUBLISHED_UNADJUSTED', 'correlation_handling': {'method': 'none', 'evidence': []}, 'source_provenance': {'source': 'fulltext_verified', 'span': 'ITT analyses (on-study and on-treatment) of MACE, defined as cardiovascular death, non-fatal \r\nMI, and non-fatal stroke, are consistent with those of MACE+ (Table 8). The reason for the \r\nsimilarity is that only 0.3% of subjects in the ITT population experienced hospitalization for \r\nunstable angina. For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and \r\nlixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, \r\n1.172) with a point estimate of 1.02. INVENTED SPAN'}, 'design_action': {'action': 'DESIGN_UNPROVEN', 'gate_id': 'design-key:design-unproven', 'decision_state': 'design not established from committed evidence; pooled through the parallel path on an assumption the harness could not verify', 'reason': 'no committed design evidence (registry intervention model or design phrase); UNKNOWN is not PARALLEL', 'validity_critical': False}}, 'effect_object': {'reported_label': 'HR', 'statistical_model': None, 'canonical_estimand': 'HAZARD_RATIO_FIRST_EVENT'}}]
E   assert not [{'alternatives': [], 'ci_high': 1.172, 'ci_low': 0.887, 'derivation': 'reported', ...}]
_______________ test_glp1_elixa_located_and_primary_membership ________________
tests\test_glp1_lane.py:42: in test_glp1_elixa_located_and_primary_membership
    assert primary is not None, 'CONVENTIONAL_GLP1RA strand is absent on base'
E   AssertionError: CONVENTIONAL_GLP1RA strand is absent on base
E   assert None is not None
_________________ test_glp1_freedom_sensitivity_never_pooled __________________
tests\test_glp1_lane.py:52: in test_glp1_freedom_sensitivity_never_pooled
    assert strands, 'GLP1 strands absent on base'
E   AssertionError: GLP1 strands absent on base
E   assert []
=========================== short test summary info ===========================
FAILED tests/test_glp1_lane.py::test_glp1_unlocated_verified_row_refused - As...
FAILED tests/test_glp1_lane.py::test_glp1_elixa_located_and_primary_membership
FAILED tests/test_glp1_lane.py::test_glp1_freedom_sensitivity_never_pooled - ...
3 failed in 42.04s
```

## Final verification

| Step | Exit code | Exact log |
|---|---:|---|
| build | 0 | [LANE-GL-BUILD.txt](LANE-GL-BUILD.txt) |
| replay | 0 | [LANE-GL-REPLAY.txt](LANE-GL-REPLAY.txt) |
| gate | 1 | [LANE-GL-GATE.txt](LANE-GL-GATE.txt) |
| scope | 0 | [LANE-GL-SCOPE.txt](LANE-GL-SCOPE.txt) |
| focused | 0 | [LANE-GL-FOCUSED.txt](LANE-GL-FOCUSED.txt) |
| full | 1 | [LANE-GL-FULL.txt](LANE-GL-FULL.txt) |

Build output:
```text
protocol_sha=b10c53d3783facb7e630219f0bb447fe6e22843e
PRIMARY: 3-point major adverse cardiovascular events  k=10  HR=0.8613 (0.8069-0.9194)  tau2=0.0027
included trials: ['31185157', '27633186', '27295427', '34215025', '31189511', '30291013', '28910237', '26630143', 'SOUL', 'FLOW']
declared-absent trials: []
comparator OA=True k=8
canonical: docs/reviews/glp1-ra-mace-t2d/index.html
```

Replay output:
```text
  OK  glp1-ra-mace-t2d

1/1 reproduce (all reproducible)
```

Gate verdict (same `harness.gate.gate_page` invoked by verify_all.limb_gate_every_page):
```text
REFUSED
```
The complete 1273-reason verdict is in LANE-GL-GATE.txt. No gate or synthesis implementation was changed.

Focused tests:
```text
.......................................                                  [100%]
39 passed, 849 deselected in 93.75s (0:01:33)
```

Full suite final summary:
```text
tests\test_stage_additions.py:271: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
FAILED tests/test_gate.py::test_valid_page_passes_non_replay_limbs - Assertio...
FAILED tests/test_gate.py::test_real_review_reproduces_and_passes_full_gate
FAILED tests/test_gate_scorecard.py::test_real_registry_passes - AssertionErr...
FAILED tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews
FAILED tests/test_override_audit.py::test_override_audit_covers_every_committed_override
FAILED tests/test_stage_additions.py::test_manuscript_limb_passes_on_every_live_review
FAILED tests/test_stage_additions.py::test_error_rate_is_fresh_against_current_pooled_population
8 failed, 880 passed in 634.19s (0:10:34)
```

The browser E2E test serves the built page only on http://127.0.0.1:8000, blocks nonlocal requests, checks both strands, the sensitivity value and censoring caveat, clicks every tab, and rejects JavaScript errors and UNVERIFIED_FACT markers.

## Exact prose-coverage debt

MEASURED 18 of 1289 rendered text units match registered object renderings; 1271 of 1289 units remain listed by the scanner. N is the CGX conservative visible prose/table text-run denominator, not a claimed linguistic sentence count.

The full, untruncated list of all units is in [LANE-GL-SCOPE.json](LANE-GL-SCOPE.json), under `pages[0].served.violation_examples` (each entry includes code, claim id and exact text). The primary class-boundary judgement, FLOW uncertainty interpretation and new standalone numerical facts were migrated to typed objects. The existing page-wide prose and table labels are not claimed migrated. This is the lane prompt’s explicit list-the-uncovered-sentences alternative.

## Remaining blockers and limits

- The page gate is refused for the reasons in its exact log; prose coverage and unresolved harms remain. The historical retrieval process remains known-item enumeration, not a newly executed concept search.
- Formal RoB 2 is not supplied by machine signals. The new records preserve domain-level uncertainty. GRADE is provisional while any domain is unassessed; no certainty category is promoted.
- Current integrity checks for ELIXA and FLOW are unassessed in this offline lane; the page names them and the checked denominator. The AACT arm-label parser was not rerun for the additions and its status is explicitly unknown.
- The portfolio error-rate/dual-extraction census was not fabricated or expanded with unperformed measurements. Any resulting coverage failure is retained in the full-suite log.
- Existing failures on other pages and portfolio gate registries remain outside this page-only lane. No other review page was rebuilt.

## Static versus dynamic disclosure

| Element | Kind | What is fixed / computed |
|---|---|---|
| B-prime class rules and source selectors | Static | Protocol rules, PMIDs and document paths; lexical table anchors are explicitly source-specific |
| FDA values | Source data | Read from the held regulatory source record, then exact source bytes/digests/CI digits validated |
| Legacy and FLOW values | Dynamic | Parsed from their own held abstracts; no meta-analysis values |
| Strands and pooled statistics | Dynamic | Current validated members passed to the unchanged canonical engine |
| Provenance coverage | Dynamic | Committed byte comparison and exact span/offset verification |
| Censoring and missing audit domains | Typed uncertainty | UNKNOWN / NOT_ASSESSED is retained, never filled to obtain a pass |
| Source retrieval time | Recorded event | Historical date precision disclosed; FLOW records an offline local read |

Second pass reviewed identifiers, endpoints, timepoints and statistics against the held evidence. No source PDF, synthesis engine, gate implementation, other review page, ProjectIndex or workbook was edited. No commit was made.
