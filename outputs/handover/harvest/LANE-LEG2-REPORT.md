# LANE LEG2 report

MEASURED: offline replay of all 32 served reviews, with an existing empty `AACT_DIR=.tmp/empty_aact`. Final JSON and HTML: `.tmp/leg2/docs/reviews/`. Base main: `237e90946f5b257265b0a3b1c986a8907d12eded`. No commit, reset, checkout, stash, push, or network retrieval.

## Policy and implementation

Located legacy ENDPOINT_UNBOUND rows remain admitted as `located_unbindable` / `UNBOUND_LEGACY`, with both `binding_reason` and `endpoint_binding_reason`. Unlocated rows retain admission and labels. Only established endpoint incompatibility refuses. Keyword absence without recognized components is uncertainty, not proof of another endpoint.

The shared binder now returns `BINDING_NONE` when the named MACE/MVE, secondary, or primary endpoint has no matching definition; it cannot fall back to unrelated definitions. The legacy locator splits sentences starting with numbers, selects a unique sentence by effect/CI or arm numbers, and accepts singular “adverse event” for a declared plural keyword. Digests, offsets, and SOUL binding are retained.

REWIND evidence detail: its GI sentence contains both event counts but not either denominator. The held randomisation sentence explicitly states `n=4949` and `n=4952`. The locator requires all four numbers in the selected sentence unless the denominators are explicit `n=` declarations in the same held text. This checks denominator presence, not independent clinical denominator applicability or effect recalculation.

## Static versus dynamic disclosure

| Item | Kind / evidence |
|---|---|
| Endpoint filtering, numeric sentence selection, singular keyword adapter, admission policy | Static rules; no trial-ID exceptions |
| ORIGIN-style abstract and test counts | Explicit synthetic regression fixture, not research output |
| REWIND, ORIGIN, SOUL and STRENGTH identifiers and quotations | Read from held cache records |
| Counts, classes, pool estimates, SHA-256 and offsets | Dynamically measured from replays and held bytes |

## Corpus table (MEASURED)

Denominator: the previously unbound legacy cohort (legacy provenance routes plus registry fallback rows carrying the legacy audit fields), matching LEG’s 71-row definition. Already-bound structured registry rows are not legacy rows. Located includes EXACT, located_unbindable, and any located refusal. The additional abstract fallback rows are disclosed separately.

| Page | N | Located n/N | EXACT n/N | Located_unbindable n/N | Unlocated n/N | REFUSED n/N |
|---|---:|---:|---:|---:|---:|---:|
| balanced-crystalloids-vs-saline-mortality | 0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| colchicine-postop-af | 1 | 1/1 | 0/1 | 1/1 | 0/1 | 0/1 |
| colchicine-recurrent-pericarditis | 1 | 1/1 | 0/1 | 1/1 | 0/1 | 0/1 |
| colchicine-secondary-cv-prevention | 0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| corticosteroids-cap-mortality | 2 | 2/2 | 2/2 | 0/2 | 0/2 | 0/2 |
| corticosteroids-covid19-mortality | 1 | 1/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| dapagliflozin-hfpef-hosp | 1 | 1/1 | 0/1 | 1/1 | 0/1 | 0/1 |
| denosumab-vertebral-fracture | 0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| doac-vte-recurrence | 7 | 7/7 | 7/7 | 0/7 | 0/7 | 0/7 |
| dpp4-mace-t2d | 5 | 4/5 | 3/5 | 1/5 | 1/5 | 0/5 |
| empagliflozin-hfpef-hosp | 0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| esketamine-trd-madrs | 5 | 1/5 | 0/5 | 1/5 | 4/5 | 0/5 |
| finerenone-ckd-t2d-renal | 1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 |
| glp1-ra-mace-t2d | 3 | 2/3 | 1/3 | 1/3 | 1/3 | 0/3 |
| iv-iron-hfref-hosp | 1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 |
| melatonin-primary-insomnia-sol | 2 | 1/2 | 0/2 | 1/2 | 1/2 | 0/2 |
| metformin-pcos-ovulation | 2 | 0/2 | 0/2 | 0/2 | 2/2 | 0/2 |
| noac-vs-warfarin-af-stroke | 4 | 0/4 | 0/4 | 0/4 | 4/4 | 0/4 |
| omega3-cardiovascular-events | 3 | 1/3 | 0/3 | 1/3 | 2/3 | 0/3 |
| pcsk9-mace | 2 | 0/2 | 0/2 | 0/2 | 2/2 | 0/2 |
| probiotics-aad-prevention | 12 | 7/12 | 3/12 | 4/12 | 5/12 | 0/12 |
| sacubitril-valsartan-hfref | 1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 |
| semaglutide-obesity-mace | 1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 |
| semaglutide-obesity-weight | 2 | 0/2 | 0/2 | 0/2 | 2/2 | 0/2 |
| sglt2-ckd-progression | 4 | 2/4 | 1/4 | 1/4 | 2/4 | 0/4 |
| sglt2-hfref-hosp-cvdeath | 0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| sglt2-primary-prevention-hf | 5 | 1/5 | 1/5 | 0/5 | 4/5 | 0/5 |
| spironolactone-hfref-mortality | 0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| statins-primary-prevention-elderly | 0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| ticagrelor-vs-clopidogrel-acs | 3 | 1/3 | 1/3 | 0/3 | 2/3 | 0/3 |
| tocilizumab-covid19-mortality | 1 | 1/1 | 0/1 | 1/1 | 0/1 | 0/1 |
| tranexamic-acid-pph | 1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 |
| **TOTAL** | 71 | 34/71 | 20/71 | 14/71 | 37/71 | 0/71 |

Additional fallback audit: `{('abstract', 'unbound_legacy_unlocated'): 51}`. All located-row document hashes and result offsets were revalidated against held files.

MEASURED: REWIND changes from incompatible to EXACT. Dapagliflozin-HFpEF / Adverse events / PMID 34711976 changes from EXACT to located_unbindable because the stricter four-number check cannot select a unique result sentence; it remains admitted. These offsetting changes explain why the EXACT count remains 20. This is a locator limitation, not a wrong-endpoint finding.

## Refused legacy rows (MEASURED)

None.

## Changed pools (MEASURED)

The original-admission replay disables only the LEG convergence call and restores the pre-fix binder in memory; inputs and empty AACT directory match final replay. `None` means no synthesis result. Comparison includes the whole result object, not only k.

| Page / outcome | Served k | Original-admission k | LEG k | LEG2 k | Original estimate → LEG2 estimate |
|---|---:|---:|---:|---:|---|
| omega3-cardiovascular-events / Major vascular events / MACE | 6 | 6 | 5 | 6 | 0.9408 → 0.9505 |

MEASURED cause: STRENGTH's abstract HR 0.99 [0.90, 1.09] is no longer admissible. The existing selector instead chooses held structured registry outcome index 2 (zero-based), `The Composite of CV Events`, from `cache/omega3-cardiovascular-events/records.json`, `ctgov_results.NCT02104817`. It reports HR 1.05 [0.93, 1.19], with 541/6539 versus 517/6539 events, and explicitly defines CV death, MI and stroke. Thus k stays 6 while the estimate changes. The replacement numbers and PMID-to-NCT mapping were checked against that held record. This is an endpoint replacement, not a lost trial or an unbound abstract row being readmitted.

LEG → LEG2 changes (includes restoration of LEG false refusals):

| Page / outcome | LEG k | LEG2 k |
|---|---:|---:|
| colchicine-postop-af / Treatment discontinuation | None | 1 |
| colchicine-recurrent-pericarditis / Adverse events (gastrointestinal) | None | 1 |
| dpp4-mace-t2d / Hospitalization for heart failure | 1 | 2 |
| esketamine-trd-madrs / Adverse events | None | 1 |
| glp1-ra-mace-t2d / Gastrointestinal adverse events | None | 1 |
| glp1-ra-mace-t2d / Adverse events leading to discontinuation | None | 1 |
| melatonin-primary-insomnia-sol / Adverse events | None | 1 |
| omega3-cardiovascular-events / Major vascular events / MACE | 5 | 6 |
| probiotics-aad-prevention / Antibiotic-associated diarrhoea | 15 | 16 |
| probiotics-aad-prevention / Any adverse events | 2 | 3 |
| probiotics-aad-prevention / Serious adverse events | None | 2 |
| sglt2-ckd-progression / Lower-limb amputation | None | 1 |
| tocilizumab-covid19-mortality / Serious adverse events | 2 | 3 |

## Abstract-route class changes (MEASURED)

2 distinct extractor candidates changed class; matching source-record IDs and both spans follow. Repeated calls in one build are deduplicated by page, outcome and extractor source.

Both abstract candidates have post-fix admissibility `ENDPOINT_UNBOUND` (refused). Because an independently bound registry candidate is selected for the same trial, the final review contains a registry trial row rather than a declared-absent trial row.

```json
{
  "slug": "omega3-cardiovascular-events",
  "outcome": "Major vascular events / MACE",
  "pmids": [
    "33190147"
  ],
  "source": "abstract source-reported HR (registered estimand): The primary end point occurred in 785 patients (12.0%) treated with omega-3 CA vs 795 (12.2%) treated with corn oil (hazard ratio, 0.99 [95% CI, 0.90-1.09]; P = .84).",
  "before": {
    "target_endpoint_class": "EXACT_TARGET",
    "target_components": [
      "cardiovascular death",
      "myocardial infarction",
      "stroke"
    ],
    "extra_components": [],
    "missing_components": [],
    "component_distance": 0,
    "endpoint_binding": "named_endpoint_resolved_to_definition_span",
    "endpoint_result_span": "The primary end point occurred in 785 patients (12.0%) treated with omega-3 CA vs 795 (12.2%) treated with corn oil (hazard ratio, 0.99 [95% CI, 0.90-1.09]; P = .84).",
    "endpoint_definition_span": "CONCLUSIONS AND RELEVANCE: Among statin-treated patients at high cardiovascular risk, the addition of omega-3 CA, compared with corn oil, to usual background therapies resulted in no significant difference in a composite outcome of major adverse cardiovascular events.",
    "endpoint_binding_reason": "result sentence names an endpoint; one definition span found"
  },
  "after": {
    "target_endpoint_class": "ENDPOINT_UNBOUND",
    "target_components": [],
    "extra_components": [],
    "missing_components": [],
    "component_distance": 999,
    "endpoint_binding": "unbound",
    "endpoint_result_span": "The primary end point occurred in 785 patients (12.0%) treated with omega-3 CA vs 795 (12.2%) treated with corn oil (hazard ratio, 0.99 [95% CI, 0.90-1.09]; P = .84).",
    "endpoint_definition_span": null,
    "endpoint_binding_reason": "named endpoint has no definition span in the held text"
  }
}
```

```json
{
  "slug": "omega3-cardiovascular-events",
  "outcome": "Major vascular events / MACE",
  "pmids": [
    "33190147"
  ],
  "source": "abstract arm-level counts (percentage-corroborated): The primary end point occurred in 785 patients (12.0%) treated with omega-3 CA vs 795 (12.2%) treated with corn oil (hazard ratio, 0.99 [95% CI, 0.90-1.09]; P = .84).",
  "before": {
    "target_endpoint_class": "EXACT_TARGET",
    "target_components": [
      "cardiovascular death",
      "myocardial infarction",
      "stroke"
    ],
    "extra_components": [],
    "missing_components": [],
    "component_distance": 0,
    "endpoint_binding": "named_endpoint_resolved_to_definition_span",
    "endpoint_result_span": "The primary end point occurred in 785 patients (12.0%) treated with omega-3 CA vs 795 (12.2%) treated with corn oil (hazard ratio, 0.99 [95% CI, 0.90-1.09]; P = .84).",
    "endpoint_definition_span": "CONCLUSIONS AND RELEVANCE: Among statin-treated patients at high cardiovascular risk, the addition of omega-3 CA, compared with corn oil, to usual background therapies resulted in no significant difference in a composite outcome of major adverse cardiovascular events.",
    "endpoint_binding_reason": "result sentence names an endpoint; one definition span found"
  },
  "after": {
    "target_endpoint_class": "ENDPOINT_UNBOUND",
    "target_components": [],
    "extra_components": [],
    "missing_components": [],
    "component_distance": 999,
    "endpoint_binding": "unbound",
    "endpoint_result_span": "The primary end point occurred in 785 patients (12.0%) treated with omega-3 CA vs 795 (12.2%) treated with corn oil (hazard ratio, 0.99 [95% CI, 0.90-1.09]; P = .84).",
    "endpoint_definition_span": null,
    "endpoint_binding_reason": "named endpoint has no definition span in the held text"
  }
}
```

INFERRED from held source review: these two candidates belong to one STRENGTH trial (PMID 33190147). This is both a vocabulary gap (`primary efficacy measure` is not recognized as the primary definition) and a real wrong-definition binding: the old binder used a generic concluding MACE sentence, expanded it to three components, and missed the stated revascularization and unstable-angina components. The held five-component definition is:

> MAIN OUTCOMES AND MEASURES: The primary efficacy measure was a composite of cardiovascular death, nonfatal myocardial infarction, nonfatal stroke, coronary revascularization, or unstable angina requiring hospitalization.

Final STRENGTH pool/refusal state:

```json
{
  "group": "trials",
  "id": "PMID 33190147",
  "endpoint_admissibility": "EXACT_TARGET",
  "target_endpoint_class": "EXACT_TARGET",
  "reason_code": null,
  "endpoint_result_span": "ClinicalTrials.gov outcome measure #2: The Composite of CV Events",
  "endpoint_definition_span": "The Composite of CV Events CV events include: cardiovascular (CV) death, non-fatal myocardial infarction (MI) and non-fatal stroke. Participants with no observed events are censored at the earliest of withdrawal of consent date and last study contact (defined as the latest of the dates of assessments contributing to an opportunity to assess as to whether the participant has had every component of the endpoint being analyzed).",
  "refused_effect": null
}
```

## Plants: verbatim pre/post (MEASURED)

### Synthetic ORIGIN-style abstract

> The primary outcome was death from cardiovascular causes. Major vascular events occurred less often (hazard ratio, 1.01; 95% CI, 0.90 to 1.14).

```json
{
  "stage": "PRE",
  "abstract_route": {
    "endpoint_binding": "named_endpoint_resolved_to_definition_span",
    "target_endpoint_class": "NEAR_MATCH",
    "endpoint_admissibility": "RESULT_INCOMPATIBLE",
    "endpoint_result_span": "Major vascular events occurred less often (hazard ratio, 1.01; 95% CI, 0.90 to 1.14).",
    "endpoint_definition_span": "The primary outcome was death from cardiovascular causes.",
    "endpoint_binding_reason": "result sentence names an endpoint; one definition span found",
    "binding_offsets": null,
    "binding_document_sha256": null
  },
  "legacy_override": {
    "endpoint_binding": "located_in_held_bytes",
    "target_endpoint_class": "NEAR_MATCH",
    "endpoint_admissibility": "RESULT_INCOMPATIBLE",
    "endpoint_result_span": "Major vascular events occurred less often (hazard ratio, 1.01; 95% CI, 0.90 to 1.14).",
    "endpoint_definition_span": "The primary outcome was death from cardiovascular causes.",
    "endpoint_binding_reason": "result sentence names an endpoint; one definition span found",
    "binding_offsets": [
      58,
      143
    ],
    "binding_document_sha256": "db7124a2a70a265b4b6a3e8cf83dc392809788c236dcd90972a355680ca5675d"
  }
}
```
```json
{
  "stage": "POST",
  "abstract_route": {
    "endpoint_binding": "unbound",
    "target_endpoint_class": "ENDPOINT_UNBOUND",
    "endpoint_admissibility": "ENDPOINT_UNBOUND",
    "endpoint_result_span": "Major vascular events occurred less often (hazard ratio, 1.01; 95% CI, 0.90 to 1.14).",
    "endpoint_definition_span": null,
    "endpoint_binding_reason": "named endpoint has no definition span in the held text",
    "binding_offsets": null,
    "binding_document_sha256": null
  },
  "legacy_override": {
    "endpoint_binding": "located_unbindable",
    "target_endpoint_class": "ENDPOINT_UNBOUND",
    "endpoint_admissibility": "UNBOUND_LEGACY",
    "endpoint_result_span": "Major vascular events occurred less often (hazard ratio, 1.01; 95% CI, 0.90 to 1.14).",
    "endpoint_definition_span": null,
    "endpoint_binding_reason": "named endpoint has no definition span in the held text",
    "binding_offsets": [
      58,
      143
    ],
    "binding_document_sha256": "db7124a2a70a265b4b6a3e8cf83dc392809788c236dcd90972a355680ca5675d"
  }
}
```

### REWIND held two-sentence quotation

Held denominator clause: were enrolled and randomly assigned to receive dulaglutide (n=4949) or placebo (n=4952).

> All-cause mortality did not differ between groups (536 [10·8%] in the dulaglutide group vs 592 [12·0%] in the placebo group; HR 0·90, 95% CI 0·80-1·01; p=0·067). 2347 (47·4%) participants assigned to dulaglutide reported a gastrointestinal adverse event during follow-up compared with 1687 (34·1%) participants assigned to placebo (p<0·0001).

```json
{
  "stage": "PRE",
  "endpoint_binding": "located_in_held_bytes",
  "target_endpoint_class": "DIFFERENT_OUTCOME",
  "endpoint_admissibility": "RESULT_INCOMPATIBLE",
  "endpoint_result_span": "All-cause mortality did not differ between groups (536 [10·8%] in the dulaglutide group vs 592 [12·0%] in the placebo group; HR 0·90, 95% CI 0·80-1·01; p=0·067). 2347 (47·4%) participants assigned to dulaglutide reported a gastrointestinal adverse event during follow-up compared with 1687 (34·1%) participants assigned to placebo (p<0·0001).",
  "endpoint_definition_span": "All-cause mortality did not differ between groups (536 [10·8%] in the dulaglutide group vs 592 [12·0%] in the placebo group; HR 0·90, 95% CI 0·80-1·01; p=0·067). 2347 (47·4%) participants assigned to dulaglutide reported a gastrointestinal adverse event during follow-up compared with 1687 (34·1%) participants assigned to placebo (p<0·0001).",
  "endpoint_binding_reason": "located result sentence; non-composite keyword classification",
  "binding_offsets": [
    2054,
    2396
  ],
  "binding_document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750"
}
```
```json
{
  "stage": "POST",
  "endpoint_binding": "located_in_held_bytes",
  "target_endpoint_class": "EXACT_TARGET",
  "endpoint_admissibility": "EXACT_TARGET",
  "endpoint_result_span": "2347 (47·4%) participants assigned to dulaglutide reported a gastrointestinal adverse event during follow-up compared with 1687 (34·1%) participants assigned to placebo (p<0·0001).",
  "endpoint_definition_span": "2347 (47·4%) participants assigned to dulaglutide reported a gastrointestinal adverse event during follow-up compared with 1687 (34·1%) participants assigned to placebo (p<0·0001).",
  "endpoint_binding_reason": "located result sentence; non-composite keyword classification",
  "binding_offsets": [
    2216,
    2396
  ],
  "binding_document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750"
}
```

SOUL exact-binding, CV-death component refusal, and digest-mismatch admission plants remain covered by the focused suite. The missing-definition fixture is synthetic; REWIND and SOUL use held records. No fixture is included in corpus counts.

## Verification

Focused command: `AACT_DIR=.tmp/empty_aact python -m pytest tests/test_legacy_binding.py tests/test_wrong_endpoint_acceptance.py tests/test_target_endpoint.py -q`

```text
..........................................                               [100%]
42 passed in 77.39s (0:01:17)
```

Repository-root full-suite command: `python -m pytest -q` stopped at collection because `outputs/search_v2/lanes/R2/test_search_v2_isrctn.py` and `tests/test_search_v2_isrctn.py` have the same module name. No unrelated files were changed to mask this.

Maintained full-suite command: `AACT_DIR=.tmp/empty_aact python -m pytest tests -q`:

```text
5 failed, 997 passed in 1203.60s (0:20:03)
```

The five failing tests were rerun with the saved pre-LEG2 binder and legacy modules loaded in memory, without changing the working tree:

```text
5 failed in 170.59s (0:02:50)
```

| Failing test | Baseline-confirmed blocker |
|---|---|
| `test_aact_cache.py::test_replay_with_snapshot_access_forbidden` | Saved review / held-document / HTML replay mismatch |
| `test_certificate.py::test_held_document_byte_mutation_refuses` | Analysis-code fields also differ from the saved certificate, violating the expected key set |
| `test_certificate.py::test_all_certificate_inputs_and_manuscript_match` | Saved certificate release hash mismatch |
| `test_fixstate.py::test_real_store_validates` | Stale `docs/fix_ledger.json` |
| `test_gate.py::test_real_review_reproduces_and_passes_full_gate` | Served HTML, certificate and offline replay mismatches |

Evidence logs: `.tmp/leg2/focused.txt`, `.tmp/leg2/full-suite.txt`, `.tmp/leg2/full-tests.txt`, `.tmp/leg2/baseline-failures.txt`. Blockers are also recorded in `STUCK_FAILURES.md`. One baseline diagnostic rerun; no unrelated gate/certificate changes or release certification. The browser contract passed within the focused suite. The test-generated line-ending-only change in `docs/compat_direction_sweep.json` was removed after checking normalized content equality with its original tracked content.

MEASURED: all 32 final JSON/HTML pairs generated; all located legacy result offsets and SHA-256 values checked; `git diff --check` passed. INFERRED: unbound labels communicate missing binding evidence, not evidence of clinical correctness. CLAIMED limitation: this lane does not independently revalidate every research effect or resolve parser vocabulary outside the owned fallback fix.
