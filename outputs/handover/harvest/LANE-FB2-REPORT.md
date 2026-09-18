# LANE FB2 — NOT COMPLETE

HEAD: `3f8add72d50b84eae2000625387e3194137a06ea`. No commit, reset, checkout, stash, or network. Initial working tree had 860 changed/untracked status entries.

## Finish condition

**NOT MET.** The production pooling hook is not installed, served pages still contain the original 20 UNVERIFIED_FACT rows, and the requested 32-page build/gate PASS is not established. The new API and scratch calculations must not be mistaken for a production fix.

Two scope blockers and one additional integration requirement prevent completion:

1. `pipeline.py::_build_outcome` creates and pools Studies before the existing held-provenance binder runs. `pipeline.py` is outside the lane’s listed owned files. A minimal hook to `verified_inputs.fact_precondition` was requested; no approval arrived. No pipeline edits were made.
2. Builds and gates raise `ImportError: cannot import name CounterfactualStudy from harness.synth`. `fragility.py:11` imports this missing class, via `statistical_layers.py` during build and `integration_display.py` during gate. The lane explicitly forbids editing `synth.py`. Five completed build/gate attempts reproduced the blocker; the repeated full sweep was stopped after that bounded failure loop.
3. The existing k=1 outcome path renders the remaining source estimate, rather than the k<2 refusal described in the prompt. A production hook also needs an explicit k<2 branch and must preserve FACT refusal states through later absence annotation.

## MEASURED — initial and final served census

Command: `python scripts/fact_census.py .`, run before edits and after binding work. Both runs returned the following table. Failed rebuilds did not update review.json.

```text
class | reason | old verified | has document_path | has sha | has span | has retrieved_utc
119 ('FACT', '', 'verified', True, True, True, True)
9 ('UNVERIFIED_FACT', 'missing full document_sha256', 'verified', False, False, False, False)
4 ('UNVERIFIED_FACT', 'missing full document_sha256', 'verified_handchecked', False, False, False, False)
3 ('UNVERIFIED_FACT', 'record and ledger retrieval disagree', 'verified', True, True, True, True)
2 ('UNVERIFIED_FACT', 'effect=0.44 is not in located span', 'verified', True, True, True, True)
1 ('UNVERIFIED_FACT', 'ai=9 is not in located span', 'verified', True, True, True, True)
1 ('UNVERIFIED_FACT', 'n1i=162 is not in located span', 'not-yet', True, True, True, True)
```

119 FACT of 139 served trial-outcome rows; 20 UNVERIFIED_FACT of 139.

## MEASURED — changes in owned files

- `legacy_facts.py`: walk held full text after an abstract fails; follow explicit secondary-publication and local-document references without matching unrelated trials by numbers; record middle-dot numeric transformations; never replace a corrupt document or extraction digest with a saved good edge.
- `held_provenance.py`: retain a mismatched digest as a failed row receipt instead of raising a page-level exception.
- `verified_inputs.py`: callable precondition binds/checks every extracted row with unchanged `claimgraph.verify_fact`, partitions FACT rows in place, names refusals and examined rungs, preserves conflicts, and records a count chain. It is **not called by the production builder yet**.
- `known_missing.py`: a FACT refusal cannot be reintroduced through a known-missing sensitivity reconstruction.
- `tests/test_fact_pool_precondition.py`: real held-source corruption, membership, idempotence, sensitivity exclusion, and full-text ladder tests.
- Three `legacy_fact_bindings.json` files changed. No `verified_effects.json` research number or provenance field was edited. No forbidden source file was edited.

## MEASURED — new bindings (3 of 20)

- probiotics-aad-prevention / Antibiotic-associated diarrhoea / PMID 18026577: `cache/probiotics-aad-prevention/ft_18026577.txt#fulltext/18026577`; SHA-256 `2aade0ceebb2d4406bc91fe54ec801f2f02c1cef8ec74e9bf9d37ac141bd0b44`.
- semaglutide-obesity-mace / 3-point major adverse cardiovascular events / PMID 37952131: `cache/semaglutide-obesity-mace/records.json#ctgov_results/NCT03574597/Participants From Time of Randomization to First Occurrence of a Composite Outcome Measure Consisting of: Cardiovascular (CV) Death, Non-fatal Myocardial Infarction (MI), or Non-fatal Stroke`; SHA-256 `5ada8141d3d2d9d5e5a22fcd7e4bfbd07b08f435385464fa7fe82812cc249d4c`.
- sglt2-primary-prevention-hf / Hospitalization for heart failure / PMID 32966714: `cache/sglt2-primary-prevention-hf/records.json#hhf_source_records/33026243/abstract`; SHA-256 `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`.

All three passed the unchanged FACT verifier. The probiotics count span is the held French-language abstract sentence containing 7/44 and 16/45. The ertugliflozin span is the explicitly referenced secondary report, PMID 33026243, under hhf_source_records. The semaglutide span is the selected CT.gov primary endpoint object. Trial identifiers and source links were inspected in held records; no external source was fetched.

## MEASURED — PCSK9 consistency audit

```json
{
  "record_date": "2026-09-11",
  "snapshot": {
    "records_sha256": "2804ee5b78dc7981da8c409728db9b0f0a63619fb89cb6c3b1680843e02ab41f",
    "retrieved_utc": "2026-09-16",
    "mode": "LEGACY_UNRECORDED_PLUS_EXTRA_PMIDS",
    "engine_sha": "aabf7b0e56c7b2e34cf681cfd03c84d64fd99a6b",
    "raw_calls": 0
  },
  "derived_records_sha256": "bd3de447b7369f383d04940a208d92dcba9293bb14f9156f8db0318b19e2f564"
}
```

The record date and independently re-derived records digest both disagree with the ledger snapshot. Neither changing an edge date nor copying the ledger date into records would repair this evidence. No date or source file was altered. All four affected PCSK9 candidates are SOURCE_CONFLICT in the scratch precondition, including the previously unbound FOURIER row.

## MEASURED — scratch plant, not a served rebuild

`.tmp/fb2_plant.py` rebuilds the primary DPP4 outcome in memory, binds a real FACT, corrupts only PMID 30418475’s document hash before Study construction, and captures the actual builder result. No held source is mutated. This is an in-memory scratch copy, not a full filesystem clone.

| Stage | FACT verdict | k | HR | Refusal |
| --- | --- | ---: | ---: | --- |
| Pre-fix builder | UNVERIFIED_FACT: held document digest mismatch | 2 | 1.0156 | None for the planted row |
| Explicit API call at scratch boundary | Same failed receipt | 1 | 1.0 | PMID 30418475, SOURCE_CONFLICT |

The after value is the remaining trial’s source HR with source CI 0.77–1.29, **not a pooled estimate**. The requested production k<2 refusal and rendered refusal-table proof remain unimplemented/unverified. The full evidence is in `.tmp/fb2-plant-pre.json` and `.tmp/fb2-plant-post.json`.

## MEASURED — all-page served result comparison

Served results were not successfully rebuilt. Every served k/estimate remains unchanged. “Scratch FACT rows” below measures the new API on saved outcome objects and is not the served k. All scales are reported as stored; non-HR estimates are not relabelled HR.

| Page | Served primary k before → after | Scale / served estimate before → after | Scratch FACT rows / candidates | Rows withheld across outcomes in scratch |
| --- | --- | --- | --- | --- |
| balanced-crystalloids-vs-saline-mortality | 2 → 2 | HR / 0.9774 → 0.9774 | 2 / 2 | none |
| colchicine-postop-af | 3 → 3 | RR / 0.6509 → 0.6509 | 3 / 3 | none |
| colchicine-recurrent-pericarditis | 2 → 2 | RR / 0.4643 → 0.4643 | 1 / 2 | Recurrent pericarditis: PMID 21873705; Symptom persistence at 72 hours: PMID 21873705; Adverse events (gastrointestinal): PMID 24694983 |
| colchicine-secondary-cv-prevention | 3 → 3 | HR / 0.8134 → 0.8134 | 3 / 3 | none |
| corticosteroids-cap-mortality | 2 → 2 | RR / 0.5458 → 0.5458 | 2 / 2 | none |
| corticosteroids-covid19-mortality | 1 → 1 | RR / 0.83 → 0.83 | 1 / 1 | none |
| dapagliflozin-hfpef-hosp | 1 → 1 | HR / 0.88 → 0.88 | 1 / 1 | Adverse events: PMID 34711976 |
| denosumab-vertebral-fracture | 1 → 1 | RR / 0.32 → 0.32 | 1 / 1 | none |
| doac-vte-recurrence | 6 → 6 | HR / 0.9091 → 0.9091 | 6 / 6 | none |
| dpp4-mace-t2d | 2 → 2 | HR / 1.0156 → 1.0156 | 2 / 2 | none |
| empagliflozin-hfpef-hosp | 1 → 1 | HR / 0.91 → 0.91 | 1 / 1 | none |
| esketamine-trd-madrs | 4 → 4 | MD / -3.3445 → -3.3445 | 3 / 4 | Observed-case Day-28 raw change-score MADRS MD: NCT02417064 |
| finerenone-ckd-t2d-renal | 2 → 2 | HR / 0.8407 → 0.8407 | 2 / 2 | none |
| glp1-ra-mace-t2d | 7 → 7 | HR / 0.8884 → 0.8884 | 7 / 7 | none |
| iv-iron-hfref-hosp | 2 → 2 | INCOMPATIBLE (HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO) / None → None | 2 / 2 | none |
| melatonin-primary-insomnia-sol | 1 → 1 | MD / -17.4 → -17.4 | 1 / 1 | none |
| metformin-pcos-ovulation | 3 → 3 | OR / 2.0733 → 2.0733 | 1 / 3 | Ovulation with metformin added to clomifene: PMID 19522426, PMID 16769748 |
| noac-vs-warfarin-af-stroke | 4 → 4 | HR / 0.8069 → 0.8069 | 3 / 4 | Stroke or systemic embolism: PMID 24251359; Major bleeding: PMID 21830957, PMID 19717844 |
| omega3-cardiovascular-events | 4 → 4 | HR / 0.9202 → 0.9202 | 4 / 4 | none |
| pcsk9-mace | 3 → 3 | HR / 0.8106 → 0.8106 | 0 / 3 | Major adverse cardiovascular events: PMID 28304224, PMID 30403574, PMID 41211925; Injection-site reactions: PMID 25773378 |
| probiotics-aad-prevention | 16 → 16 | RR / 0.6907 → 0.6907 | 15 / 16 | Antibiotic-associated diarrhoea: PMID 15740542 |
| sacubitril-valsartan-hfref | 0 → 0 | None / None → None | 0 / 0 | none |
| semaglutide-obesity-mace | 1 → 1 | HR / 0.8 → 0.8 | 1 / 1 | none |
| semaglutide-obesity-weight | 2 → 2 | MD / -11.8449 → -11.8449 | 2 / 2 | none |
| sglt2-ckd-progression | 3 → 3 | HR / 0.6836 → 0.6836 | 3 / 3 | none |
| sglt2-hfref-hosp-cvdeath | 2 → 2 | HR / 0.75 → 0.75 | 2 / 2 | none |
| sglt2-primary-prevention-hf | 3 → 3 | HR / 0.7023 → 0.7023 | 2 / 3 | Hospitalization for heart failure: PMID 26378978 |
| spironolactone-hfref-mortality | 3 → 3 | HR / 0.7294 → 0.7294 | 3 / 3 | none |
| statins-primary-prevention-elderly | 2 → 2 | HR / 0.6803 → 0.6803 | 2 / 2 | none |
| ticagrelor-vs-clopidogrel-acs | 2 → 2 | HR / None → None | 2 / 2 | none |
| tocilizumab-covid19-mortality | 1 → 1 | RR / 0.85 → 0.85 | 1 / 1 | none |
| tranexamic-acid-pph | 1 → 1 | RR / 0.81 → 0.81 | 1 / 1 | Thromboembolic events: PMID 28456509 |

## MEASURED — scratch subset arithmetic for changed outcomes

These are exploratory recomputations over FACT rows on the saved input objects, not served-result changes. Existing incompatible results are not made publishable. Where k<2, this audit suppresses a pooled estimate; that audit choice has not changed production behavior.

| Page / outcome | Candidate rows → FACT rows | Prior scale / estimate | Scratch subset estimate |
| --- | --- | --- | --- |
| colchicine-recurrent-pericarditis / Recurrent pericarditis | 2 → 1 | RR / 0.4643 | REFUSED / unavailable |
| colchicine-recurrent-pericarditis / Symptom persistence at 72 hours | 1 → 0 | RR / 0.44 | REFUSED / unavailable |
| colchicine-recurrent-pericarditis / Adverse events (gastrointestinal) | 1 → 0 | RR / 1.0 | REFUSED / unavailable |
| dapagliflozin-hfpef-hosp / Adverse events | 1 → 0 | RR / 1.1579 | REFUSED / unavailable |
| esketamine-trd-madrs / Observed-case Day-28 raw change-score MADRS MD | 4 → 3 | MD / -3.3445 | -3.1004 |
| metformin-pcos-ovulation / Ovulation with metformin added to clomifene | 3 → 1 | OR / 2.0733 | REFUSED / unavailable |
| noac-vs-warfarin-af-stroke / Stroke or systemic embolism | 4 → 3 | HR / 0.8069 | REFUSED / unavailable |
| noac-vs-warfarin-af-stroke / Major bleeding | 4 → 2 | HR / 0.8544 | REFUSED / unavailable |
| pcsk9-mace / Major adverse cardiovascular events | 3 → 0 | HR / 0.8106 | REFUSED / unavailable |
| pcsk9-mace / Injection-site reactions | 1 → 0 | RR / 1.4019 | REFUSED / unavailable |
| probiotics-aad-prevention / Antibiotic-associated diarrhoea | 16 → 15 | RR / 0.6907 | 0.7402 |
| sglt2-primary-prevention-hf / Hospitalization for heart failure | 3 → 2 | HR / 0.7023 | 0.7197 |
| tranexamic-acid-pph / Thromboembolic events | 1 → 0 | RR / 0.8781 | REFUSED / unavailable |

## MEASURED — remaining 17 of 20 rows and exact examined rungs

SOURCE_RETRIEVED_NOT_EXTRACTED is deliberately conservative: held commentary or transformed numbers may plausibly support the value, but no verifier-accepted literal edge was found. This is not a claim of no outcome data in the trial. No exhaustive cross-file ladder is falsely asserted.

### colchicine-recurrent-pericarditis / Recurrent pericarditis / PMID 21873705

SOURCE_RETRIEVED_NOT_EXTRACTED: FACT precondition failed: effect=0.44 is not in located span. Held-source locator audit: cache/colchicine-recurrent-pericarditis/records.json#records/21873705/abstract: effect=0.44 is not in located span

Examined identity-matched rungs:

- `cache/colchicine-recurrent-pericarditis/records.json#records/21873705/abstract`

### colchicine-recurrent-pericarditis / Symptom persistence at 72 hours / PMID 21873705

SOURCE_RETRIEVED_NOT_EXTRACTED: FACT precondition failed: effect=0.44 is not in located span. Held-source locator audit: cache/colchicine-recurrent-pericarditis/records.json#records/21873705/abstract: effect=0.44 is not in located span

Examined identity-matched rungs:

- `cache/colchicine-recurrent-pericarditis/records.json#records/21873705/abstract`

### colchicine-recurrent-pericarditis / Adverse events (gastrointestinal) / PMID 24694983

SOURCE_RETRIEVED_NOT_EXTRACTED: FACT precondition failed: ai=9 is not in located span. Held-source locator audit: cache/colchicine-recurrent-pericarditis/records.json#records/24694983/abstract: ai=9 is not in located span; cache/colchicine-recurrent-pericarditis/verified_arms.json#verified_arms.json/24694983/source (held legacy transcription): document is not under an allowed held directory

Examined identity-matched rungs:

- `cache/colchicine-recurrent-pericarditis/records.json#records/24694983/abstract`
- `cache/colchicine-recurrent-pericarditis/verified_arms.json#verified_arms.json/24694983/source (held legacy transcription)`

### dapagliflozin-hfpef-hosp / Adverse events / PMID 34711976

SOURCE_RETRIEVED_NOT_EXTRACTED: FACT precondition failed: n1i=162 is not in located span. Held-source locator audit: cache/dapagliflozin-hfpef-hosp/records.json#records/34711976/abstract: n1i=162 is not in located span; cache/dapagliflozin-hfpef-hosp/verified_arms.json#verified_arms.json/34711976/source (held legacy transcription): document is not under an allowed held directory

Examined identity-matched rungs:

- `cache/dapagliflozin-hfpef-hosp/records.json#records/34711976/abstract`
- `cache/dapagliflozin-hfpef-hosp/verified_arms.json#verified_arms.json/34711976/source (held legacy transcription)`

### esketamine-trd-madrs / Observed-case Day-28 raw change-score MADRS MD / NCT02417064

SOURCE_RETRIEVED_NOT_EXTRACTED: FACT precondition failed: missing full document_sha256. Held-source locator audit: cache/esketamine-trd-madrs/verified_arms.json#verified_arms.json/NCT02417064/source (held legacy transcription): document is not under an allowed held directory

Examined identity-matched rungs:

- `cache/esketamine-trd-madrs/verified_arms.json#verified_arms.json/NCT02417064/source (held legacy transcription)`

### metformin-pcos-ovulation / Ovulation with metformin added to clomifene / PMID 19522426

SOURCE_RETRIEVED_NOT_EXTRACTED: FACT precondition failed: missing full document_sha256. Held-source locator audit: cache/metformin-pcos-ovulation/records.json#records/19522426/abstract: ai=10 is not in located span; cache/metformin-pcos-ovulation/verified_arms.json#verified_arms.json/19522426/source (held legacy transcription): document is not under an allowed held directory

Examined identity-matched rungs:

- `cache/metformin-pcos-ovulation/records.json#records/19522426/abstract`
- `cache/metformin-pcos-ovulation/verified_arms.json#verified_arms.json/19522426/source (held legacy transcription)`

### metformin-pcos-ovulation / Ovulation with metformin added to clomifene / PMID 16769748

SOURCE_RETRIEVED_NOT_EXTRACTED: FACT precondition failed: missing full document_sha256. Held-source locator audit: cache/metformin-pcos-ovulation/records.json#records/16769748/abstract: ai=71 is not in located span; cache/metformin-pcos-ovulation/ft_16769748.txt#fulltext/16769748: ai=71 is not in located span; cache/metformin-pcos-ovulation/verified_arms.json#verified_arms.json/16769748/source (held legacy transcription): document is not under an allowed held directory

Examined identity-matched rungs:

- `cache/metformin-pcos-ovulation/records.json#records/16769748/abstract`
- `cache/metformin-pcos-ovulation/ft_16769748.txt#fulltext/16769748`
- `cache/metformin-pcos-ovulation/verified_arms.json#verified_arms.json/16769748/source (held legacy transcription)`

### noac-vs-warfarin-af-stroke / Stroke or systemic embolism / PMID 24251359

SOURCE_RETRIEVED_NOT_EXTRACTED: FACT precondition failed: missing full document_sha256. Held-source locator audit: cache/noac-vs-warfarin-af-stroke/records.json#records/24251359/abstract: ci_low=0.745 is not in located span; cache/noac-vs-warfarin-af-stroke/dose_selection.json#dose_selection.json/24251359/source (held legacy transcription): document is not under an allowed held directory

Examined identity-matched rungs:

- `cache/noac-vs-warfarin-af-stroke/records.json#records/24251359/abstract`
- `cache/noac-vs-warfarin-af-stroke/dose_selection.json#dose_selection.json/24251359/source (held legacy transcription)`

### noac-vs-warfarin-af-stroke / Major bleeding / PMID 21830957

SOURCE_RETRIEVED_NOT_EXTRACTED: FACT precondition failed: missing full document_sha256. Held-source locator audit: cache/noac-vs-warfarin-af-stroke/records.json#records/21830957/abstract: effect=1.04 is not in located span; cache/noac-vs-warfarin-af-stroke/verified_effects.json#verified_effects.json/21830957/source (held legacy transcription): document is not under an allowed held directory

Examined identity-matched rungs:

- `cache/noac-vs-warfarin-af-stroke/records.json#records/21830957/abstract`
- `cache/noac-vs-warfarin-af-stroke/verified_effects.json#verified_effects.json/21830957/source (held legacy transcription)`

### noac-vs-warfarin-af-stroke / Major bleeding / PMID 19717844

SOURCE_RETRIEVED_NOT_EXTRACTED: FACT precondition failed: missing full document_sha256. Held-source locator audit: cache/noac-vs-warfarin-af-stroke/records.json#records/19717844/abstract: effect=0.93 is not in located span; cache/noac-vs-warfarin-af-stroke/verified_effects.json#verified_effects.json/19717844/source (held legacy transcription): document is not under an allowed held directory

Examined identity-matched rungs:

- `cache/noac-vs-warfarin-af-stroke/records.json#records/19717844/abstract`
- `cache/noac-vs-warfarin-af-stroke/verified_effects.json#verified_effects.json/19717844/source (held legacy transcription)`

### pcsk9-mace / Major adverse cardiovascular events / PMID 28304224

SOURCE_CONFLICT: FACT precondition failed: missing full document_sha256. Held-source locator audit: cache/pcsk9-mace/records.json#ctgov_results/NCT01764633/Time to Cardiovascular Death, Myocardial Infarction, or Stroke: record and ledger retrieval disagree

Examined identity-matched rungs:

- `cache/pcsk9-mace/records.json#ctgov_results/NCT01764633/Time to Cardiovascular Death, Myocardial Infarction, or Stroke`

### pcsk9-mace / Major adverse cardiovascular events / PMID 30403574

SOURCE_CONFLICT: FACT precondition failed: record and ledger retrieval disagree. Held-source locator audit: cache/pcsk9-mace/records.json#records/30403574/abstract

Examined identity-matched rungs:

- `cache/pcsk9-mace/records.json#records/30403574/abstract`

### pcsk9-mace / Major adverse cardiovascular events / PMID 41211925

SOURCE_CONFLICT: FACT precondition failed: record and ledger retrieval disagree. Held-source locator audit: cache/pcsk9-mace/records.json#records/41211925/abstract; cache/pcsk9-mace/verified_effects.json#verified_effects.json/41211925/source (held legacy transcription); cache/pcsk9-mace/verified_arms.json#verified_arms.json/41211925/source (held legacy transcription)

Examined identity-matched rungs:

- `cache/pcsk9-mace/records.json#records/41211925/abstract`
- `cache/pcsk9-mace/verified_effects.json#verified_effects.json/41211925/source (held legacy transcription)`
- `cache/pcsk9-mace/verified_arms.json#verified_arms.json/41211925/source (held legacy transcription)`

### pcsk9-mace / Injection-site reactions / PMID 25773378

SOURCE_CONFLICT: FACT precondition failed: record and ledger retrieval disagree. Held-source locator audit: cache/pcsk9-mace/records.json#records/25773378/abstract; cache/pcsk9-mace/verified_arms.json#verified_arms.json/25773378/source (held legacy transcription)

Examined identity-matched rungs:

- `cache/pcsk9-mace/records.json#records/25773378/abstract`
- `cache/pcsk9-mace/verified_arms.json#verified_arms.json/25773378/source (held legacy transcription)`

### probiotics-aad-prevention / Antibiotic-associated diarrhoea / PMID 15740542

SOURCE_RETRIEVED_NOT_EXTRACTED: FACT precondition failed: missing full document_sha256. Held-source locator audit: cache/probiotics-aad-prevention/records.json#records/15740542/abstract: ai=4 is not in located span; cache/probiotics-aad-prevention/verified_arms.json#verified_arms.json/15740542/source (held legacy transcription): document is not under an allowed held directory

Examined identity-matched rungs:

- `cache/probiotics-aad-prevention/records.json#records/15740542/abstract`
- `cache/probiotics-aad-prevention/verified_arms.json#verified_arms.json/15740542/source (held legacy transcription)`

### sglt2-primary-prevention-hf / Hospitalization for heart failure / PMID 26378978

SOURCE_RETRIEVED_NOT_EXTRACTED: FACT precondition failed: missing full document_sha256. Held-source locator audit: cache/sglt2-primary-prevention-hf/records.json#records/26378978/abstract: effect=0.65 is not in located span; cache/sglt2-primary-prevention-hf/pmc_26819227_fulltext.txt#explicit legacy document reference: document is not under an allowed held directory; cache/sglt2-primary-prevention-hf/verified_effects.json#verified_effects.json/26378978/source (held legacy transcription): document is not under an allowed held directory

Examined identity-matched rungs:

- `cache/sglt2-primary-prevention-hf/records.json#records/26378978/abstract`
- `cache/sglt2-primary-prevention-hf/pmc_26819227_fulltext.txt#explicit legacy document reference`
- `cache/sglt2-primary-prevention-hf/verified_effects.json#verified_effects.json/26378978/source (held legacy transcription)`

### tranexamic-acid-pph / Thromboembolic events / PMID 28456509

SOURCE_RETRIEVED_NOT_EXTRACTED: FACT precondition failed: missing full document_sha256. Held-source locator audit: cache/tranexamic-acid-pph/records.json#records/28456509/abstract: ci=34 is not in located span; cache/tranexamic-acid-pph/verified_arms.json#verified_arms.json/28456509/source (held legacy transcription): document is not under an allowed held directory

Examined identity-matched rungs:

- `cache/tranexamic-acid-pph/records.json#records/28456509/abstract`
- `cache/tranexamic-acid-pph/verified_arms.json#verified_arms.json/28456509/source (held legacy transcription)`

The fixed FACT verifier does not interpret a general number_transformations schema for spelled-out counts, percentage-derived counts, relative-risk-reduction complements, combined-arm SDs, CI-level conversion, or split-document denominators. Such values were not laundered through a nearby unrelated digit. The allowed-directory contract also rejects verified_arms/verified_effects transcriptions and the explicitly cited pmc_26819227_fulltext.txt pathname. Relaxing claimgraph.py or manufacturing newly committed source bytes was prohibited.

## Verification

- Final targeted command: `python -m pytest -q tests/test_fact_pool_precondition.py tests/test_legacy_fact_binding.py` → **15 passed of 15**, in 19.72 seconds. A transient test-placement NameError was corrected before this green rerun. Scoped `git diff --check` also passed.
- Expanded known-missing tests: 17 passed / 19 tested at that revision; failures `test_colchicine_panel_passes_and_combined_sensitivity_changes_null_crossing` and `test_committed_counts_sensitivity_equals_direct_synth_pool` (missing combined/sensitivity keys). Re-running those six tests with only this lane’s early-return branch removed in memory produced the same two failures: 4 passed / 6. They pre-exist this branch.
- `python scripts/retraction_survival.py 3f8add72`: `pages with every marking kept (count >= base): 32 of 32`.
- Gate: **0 PASS of 32 required**; 5 of 32 completed gate attempts, all raised; 27 of 32 not completed after the repeated shared blocker. This is not a completed 32-page gate census.
- Rebuild with `--now 2026-09-11`: 0 successful of 5 completed attempts; remaining topics blocked. The offline harness reads held caches directly and disables socket connections.

Completed attempts and every returned error:

- balanced-crystalloids-vs-saline-mortality: build FAIL; gate: ImportError: cannot import name 'CounterfactualStudy' from 'harness.synth' (C:\mh-r-FB2\harness\synth.py)
- colchicine-postop-af: build FAIL; gate: ImportError: cannot import name 'CounterfactualStudy' from 'harness.synth' (C:\mh-r-FB2\harness\synth.py)
- colchicine-recurrent-pericarditis: build FAIL; gate: ImportError: cannot import name 'CounterfactualStudy' from 'harness.synth' (C:\mh-r-FB2\harness\synth.py)
- colchicine-secondary-cv-prevention: build FAIL; gate: ImportError: cannot import name 'CounterfactualStudy' from 'harness.synth' (C:\mh-r-FB2\harness\synth.py)
- corticosteroids-cap-mortality: build FAIL; gate: ImportError: cannot import name 'CounterfactualStudy' from 'harness.synth' (C:\mh-r-FB2\harness\synth.py)

## Hardcode disclosure

| Item | Static / dynamic | Evidence |
| --- | --- | --- |
| 2026-09-11; 3f8add72 | Static task parameters | LANE_PROMPT.md |
| Corrupt hash of 64 zeroes | Static negative-test mutation | Scratch only; never research data |
| Numeric effects, counts, confidence bounds | Dynamic reads; unchanged inputs | Held cache and saved review.json |
| FACT verdicts, hashes, dates, refusals | Dynamic verification | Unchanged claimgraph.verify_fact and source ledger audit |
| Scratch subset estimates | Dynamic arithmetic, not published | .tmp/fb2-subsets.json |

## INFERRED / CLAIMED

INFERRED: a minimal early pipeline hook plus preservation of refusal states and an explicit k<2 branch can integrate this API. That is not yet established by a production E2E test. The missing CounterfactualStudy import is independent of the provenance changes, as none of its defining/importing files were edited.

CLAIMED: no completion, ship-readiness, 32-page PASS, or rendered production refusal is claimed. No index/workbook submission status was changed. To finish, resolve the protected synth import in the integration lane, authorize the minimal pipeline/absence boundary hooks, then rebuild all 32, gate all 32, rerun census and plants, and replace this blocked report with measured served-result comparisons.
