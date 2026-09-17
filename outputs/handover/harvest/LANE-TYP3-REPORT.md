# LANE TYP3 report

MEASURED from held local bytes; no network and no commit.

Base and final HEAD: `e3b70bfa36dc65a3920b20fd4e2d628a270e7d28`. `LANE_BASE.txt` is absent; this matches the hash embedded in `LANE_PROMPT.md`.

The evidence pass covers every base primary-pool row and every harm row carrying a value. Rows refused on rebuild remain in the fixed audit denominator. No trial selection, protocol, coercion register, or membership/parity declaration was edited. This is an evidence handoff, not a passing release.

## Hardcode disclosure

| Component | Static | Dynamic / validation |
|---|---|---|
| Scope | Ten slugs from the prompt; literal source selectors reviewed against held text | 27 base rows read from committed review objects |
| Numeric inputs | No authored estimates or substituted denominators | Original values retained; exact spans, SHA-256, character offsets and committed-source checks |
| Types | Reviewed literal mappings such as hazard ratio → HR; twelve-axis schema | Builder consumes axis evidence; each basis resolves against held bytes |
| Unstated fields | No default ITT, censoring, estimator, or reconstructed effect measure | UNKNOWN and explicit refusal |
| Summaries | No asserted portfolio count | Fixed-denominator measurements and captured command outputs |

## Implementation and source coverage

`cache/<slug>/verified_inputs.json` is an additive, outcome-and-numeric-tuple-bound evidence sidecar. `harness/verified_inputs.py` resolves committed abstracts, primary full texts and exact cached registry JSON spans. The pipeline attaches that evidence before the TY builder; the builder writes `effect_types.json`. The strict held-only branch prevents efficacy analysis sets from leaking into safety rows. Unknown fields cannot be supplied through a protocol-derived default.

`harness/claimgraph.py` adds the requested cached-document reference contract while retaining committed-byte, hash, span and digit checks. It reads printed middle-dot decimals and thin-space grouped digits without changing the verbatim span. A FACT means the digits are located in a held source; it does not certify that the endpoint, denominator, or estimand is appropriate for the pool. `harness/gate.py`, `harness/synth.py`, search, screening, GLP1 pages and other lanes’ pages were not edited.

AACT was read offline through `harness/aact.py`: design_groups, interventions, eligibilities, design_outcomes, and outcome_analyses. See `outputs/handover/lane_typ3/aact_read_audit.json` for selected NCT IDs, table rows and snapshot folder name. The folder name is not asserted to be its data date. AACT supplied no WOMAN outcome-analysis row. No additional type value was inferred merely from a registry trial name.

## Base plants (run before edits; exact base-module rerun retained)

```text
Base: e3b70bfa36dc65a3920b20fd4e2d628a270e7d28
ELIXA positive control: True
One-digit span plant: {"verified": false, "class": "UNVERIFIED_FACT", "reason": "span is not located verbatim in extracted text"}
Basisless axis plant: {"value": "UNKNOWN", "basis": {"absence_code": "NO_ROW_EVIDENCE"}}
Binding verdict: {"status": "UNKNOWN_FAILS_CLOSED", "axis": 3, "axis_name": "analysis_set", "reason": "UNTYPED — axis 3 unknown: NO_ROW_EVIDENCE"}
```

The base builder refuses a basisless axis by returning UNKNOWN, followed by UNKNOWN_FAILS_CLOSED at unification; it does not raise an exception. The added strict held-evidence branch also rejects missing or corrupted bases.

## Fixed-denominator measurements

**N means base primary-pool rows plus value-carrying harm rows, including single-trial rows.** “Binding typed” means every binding axis has evidence; it does not imply that its value matches the target. “Refused” is the per-row TY verdict on the same fixed candidates. Page gate verdicts are reported separately.

| Page | FACT before → after | Binding typed before → after | Still type-refused | Rebuild | Page gate |
|---|---|---|---|---|---|
| semaglutide-obesity-mace | 0 of 2 → 2 of 2 | 0 of 2 → 1 of 2 | 1 of 2 | exit 0 | REFUSED |
| semaglutide-obesity-weight | 0 of 2 → 2 of 2 | 2 of 2 → 0 of 2 | 2 of 2 | exit 1 | REFUSED |
| sglt2-ckd-progression | 0 of 4 → 4 of 4 | 0 of 4 → 1 of 4 | 3 of 4 | exit 0 | REFUSED |
| sglt2-hfref-hosp-cvdeath | 0 of 2 → 2 of 2 | 0 of 2 → 0 of 2 | 2 of 2 | exit 1 | REFUSED |
| sglt2-primary-prevention-hf | 0 of 4 → 4 of 4 | 0 of 4 → 1 of 4 | 4 of 4 | exit 0 | REFUSED |
| spironolactone-hfref-mortality | 0 of 3 → 3 of 3 | 0 of 3 → 1 of 3 | 2 of 3 | exit 1 | REFUSED |
| statins-primary-prevention-elderly | 0 of 2 → 2 of 2 | 2 of 2 → 2 of 2 | 2 of 2 | exit 0 | REFUSED |
| ticagrelor-vs-clopidogrel-acs | 0 of 3 → 3 of 3 | 0 of 3 → 1 of 3 | 2 of 3 | exit 1 | REFUSED |
| tocilizumab-covid19-mortality | 0 of 3 → 3 of 3 | 1 of 3 → 0 of 3 | 3 of 3 | exit 0 | REFUSED |
| tranexamic-acid-pph | 0 of 2 → 1 of 2 | 1 of 2 → 1 of 2 | 1 of 2 | exit 0 | REFUSED |

MEASURED total: 26 FACT of 27 base rows; 8 of 27 fully typed on binding axes; 22 of 27 still type-refused.

## Row-level unknowns and refusals

### semaglutide-obesity-mace

| Row / outcome | FACT | Binding verdict / axes | All UNKNOWN axes |
|---|---|---|---|
| PMID 37952131 / 3-point major adverse cardiovascular events | FACT | MATCH | censoring, adjustment, estimator |
| PMID 37952131 / Adverse events leading to permanent discontinuation | FACT | UNKNOWN_FAILS_CLOSED; unknown: effect_measure | analysis_set, first_or_recurrent, time_origin, censoring, effect_measure, adjustment, estimator |

### semaglutide-obesity-weight

| Row / outcome | FACT | Binding verdict / axes | All UNKNOWN axes |
|---|---|---|---|
| PMID 33625476 / Percent change in body weight | FACT | UNKNOWN_FAILS_CLOSED; unknown: effect_measure | analysis_set, first_or_recurrent, effect_measure, adjustment, estimator |
| PMID 33567185 / Percent change in body weight | FACT | UNKNOWN_FAILS_CLOSED; unknown: effect_measure | analysis_set, first_or_recurrent, effect_measure, adjustment, estimator |

### sglt2-ckd-progression

| Row / outcome | FACT | Binding verdict / axes | All UNKNOWN axes |
|---|---|---|---|
| PMID 32970396 / Trial-defined primary cardiorenal composite | FACT | UNKNOWN_FAILS_CLOSED; unknown: analysis_set | analysis_set, first_or_recurrent, time_origin, censoring, adjustment, estimator |
| PMID 30990260 / Trial-defined primary cardiorenal composite | FACT | UNKNOWN_FAILS_CLOSED; unknown: analysis_set | analysis_set, first_or_recurrent, time_origin, censoring, adjustment, estimator |
| PMID 36331190 / Trial-defined primary cardiorenal composite | FACT | MATCH | time_origin, censoring |
| PMID 36331190 / Diabetic ketoacidosis | FACT | UNKNOWN_FAILS_CLOSED; unknown: effect_measure | first_or_recurrent, time_origin, censoring, effect_measure, adjustment, estimator |

### sglt2-hfref-hosp-cvdeath

| Row / outcome | FACT | Binding verdict / axes | All UNKNOWN axes |
|---|---|---|---|
| PMID 31535829 / Composite cardiovascular death or hospitalisation for heart failure | FACT | UNKNOWN_FAILS_CLOSED; unknown: analysis_set; mismatch: effect_measure | analysis_set, first_or_recurrent, time_origin, censoring |
| PMID 32865377 / Composite cardiovascular death or hospitalisation for heart failure | FACT | UNKNOWN_FAILS_CLOSED; unknown: analysis_set; mismatch: effect_measure | analysis_set, first_or_recurrent, time_origin, censoring, adjustment, estimator |

### sglt2-primary-prevention-hf

| Row / outcome | FACT | Binding verdict / axes | All UNKNOWN axes |
|---|---|---|---|
| PMID 28605608 / Hospitalization for heart failure | FACT | UNKNOWN_FAILS_CLOSED; unknown: analysis_set | analysis_set, first_or_recurrent, time_origin, censoring, adjustment, estimator |
| PMID 26378978 / Hospitalization for heart failure | FACT | REFUSE; mismatch: analysis_set | first_or_recurrent, time_origin, follow_up, censoring |
| PMID 32966714 / Hospitalization for heart failure | FACT | UNKNOWN_FAILS_CLOSED; unknown: analysis_set | analysis_set, time_origin, follow_up, censoring, adjustment |
| PMID 30415602 / Hospitalization for heart failure | FACT | UNKNOWN_FAILS_CLOSED; unknown: analysis_set | analysis_set, first_or_recurrent, time_origin, censoring, adjustment, estimator |

### spironolactone-hfref-mortality

| Row / outcome | FACT | Binding verdict / axes | All UNKNOWN axes |
|---|---|---|---|
| PMID 10471456 / All-cause mortality | FACT | UNKNOWN_FAILS_CLOSED; unknown: analysis_set | analysis_set, first_or_recurrent, time_origin, censoring, adjustment, estimator |
| PMID 21073363 / All-cause mortality | FACT | MATCH | first_or_recurrent, time_origin, censoring, adjustment, estimator |
| PMID 28824029 / All-cause mortality | FACT | UNKNOWN_FAILS_CLOSED; unknown: analysis_set | analysis_set, first_or_recurrent, time_origin, censoring, adjustment, estimator |

### statins-primary-prevention-elderly

| Row / outcome | FACT | Binding verdict / axes | All UNKNOWN axes |
|---|---|---|---|
| PMID 20404379 / Major vascular events | FACT | REFUSE; mismatch: effect_measure | analysis_set, time_origin, follow_up, censoring, adjustment, estimator |
| PMID 42670961 / Major vascular events | FACT | REFUSE; mismatch: effect_measure | analysis_set, first_or_recurrent, time_origin, censoring, adjustment, estimator |

### ticagrelor-vs-clopidogrel-acs

| Row / outcome | FACT | Binding verdict / axes | All UNKNOWN axes |
|---|---|---|---|
| PMID 19717846 / Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke | FACT | MATCH | first_or_recurrent, censoring, adjustment, estimator |
| PMID 26376600 / Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke | FACT | UNKNOWN_FAILS_CLOSED; unknown: analysis_set | analysis_set, first_or_recurrent, time_origin, censoring, adjustment, estimator |
| PMID 19717846 / Major bleeding | FACT | UNKNOWN_FAILS_CLOSED; unknown: effect_measure | analysis_set, first_or_recurrent, censoring, effect_measure, adjustment, estimator |

### tocilizumab-covid19-mortality

| Row / outcome | FACT | Binding verdict / axes | All UNKNOWN axes |
|---|---|---|---|
| PMID 33933206 / 28-day all-cause mortality | FACT | UNKNOWN_FAILS_CLOSED; unknown: effect_measure | first_or_recurrent, time_origin, censoring, effect_measure, adjustment, estimator |
| PMID 33631066 / Serious adverse events | FACT | UNKNOWN_FAILS_CLOSED; unknown: effect_measure | analysis_set, first_or_recurrent, time_origin, follow_up, censoring, effect_measure, adjustment, estimator |
| PMID 33332779 / Serious adverse events | FACT | UNKNOWN_FAILS_CLOSED; unknown: effect_measure | analysis_set, first_or_recurrent, time_origin, follow_up, censoring, effect_measure, adjustment, estimator |

### tranexamic-acid-pph

| Row / outcome | FACT | Binding verdict / axes | All UNKNOWN axes |
|---|---|---|---|
| PMID 28456509 / Death due to bleeding | FACT | MATCH | first_or_recurrent, censoring, adjustment, estimator |
| PMID 28456509 / Thromboembolic events | UNVERIFIED_FACT | UNKNOWN_FAILS_CLOSED; unknown: effect_measure | first_or_recurrent, censoring, effect_measure, adjustment, estimator, report |

## Coercions for integrator review

- sglt2-hfref-hosp-cvdeath / PMID 31535829: COERCION NEEDED: effect_measure HR → RR, evidence `"paramType": "Hazard Ratio (HR)"`. No coercion authored.
- sglt2-hfref-hosp-cvdeath / PMID 32865377: COERCION NEEDED: effect_measure HR → RR, evidence `hazard ratio`. No coercion authored.
- sglt2-primary-prevention-hf / PMID 26378978: COERCION NEEDED: analysis_set mITT → ITT, evidence `modified intent-to-treat approach in patients treated with at least one dose of study drug`. No coercion authored.
- statins-primary-prevention-elderly / PMID 20404379: COERCION NEEDED: effect_measure HR → RR, evidence `hazard ratio`. No coercion authored.
- statins-primary-prevention-elderly / PMID 42670961: COERCION NEEDED: effect_measure HR → RR, evidence `hazard ratio`. No coercion authored.

- tocilizumab-covid19-mortality / PMID 33933206: COERCION NEEDED: effect_measure rate ratio → OR (protocol target), evidence `rate ratio 0·85; 95% CI 0·76-0·94`. The current schema has no rate-ratio enum; retained UNKNOWN. The existing row labels this RR. No equivalence was assumed.
- spironolactone-hfref-mortality / PMID 28824029: COERCION NEEDED: endpoint_components cardiovascular death or HF hospitalization → all-cause mortality, evidence `The primary endpoint was a composite of death from cardiovascular causes or hospitalization for HF.` This is a semantic incompatibility for integrator adjudication, not a recommended conversion. Endpoint components are not currently binding for this protocol.

## Source-level second-pass findings

- **UNVERIFIED_FACT:** tranexamic-acid-pph / PMID 28456509 / Thromboembolic events. The held abstract does not state the input tuple 30/10033 versus 34/9985. No linked primary full text is held in this cache; AACT outcome_analyses also has no matching NCT00872469 row. The authored verified_arms summary is not treated as a held source.
- **MEASURED denominator inconsistency:** the STEP registry records contain the stored means/SDs and overall randomized Ns, so the digits pass the provenance check. The selected in-trial class provides smaller available-data Ns. See each sidecar’s `denominator_review`. The inputs remain unchanged; the analysis set and effect measure remain UNKNOWN instead of attaching another estimand’s ITT/ANCOVA metadata.
- **MEASURED source discrepancy:** SELECT’s cached registry HR upper bound is 0.89; the selected abstract says 0.90. Only the explicitly randomized population and origin are carried from that registry endpoint. Its estimator/censoring were not attributed to the publication estimate.
- **MEASURED endpoint mismatch:** J-EMPHASIS-HF’s stored HR concerns its composite primary outcome, not all-cause mortality; the held text also separately reports death counts. No endpoint or value was substituted.
- **MEASURED population limitation:** the HHF source reports are overall trial effects, including people with previous HF/CVD; the secondary-publication links are retained (CANVAS 29526832, EMPA-REG 26819227, VERTIS 33026243). Nothing was re-labelled as a no-prior-HF subgroup.
- Safety populations, last-known-event-free censoring and available-case means do not map exactly to all existing schema enums. Relevant unmapped text is retained in the evidence sidecars. Crude arm-count and mean-difference transformations are not presented as a source-stated effect measure.

INFERRED: accepting these remaining rows requires additional held evidence, explicit type/schema decisions, or integrator-reviewed changes to source/endpoint/membership selection. CLAIMED: no release-readiness, external authenticity, exhaustive source recovery, or all-pages-pass claim is made.

## Rebuild commands and results

### semaglutide-obesity-mace

`python scripts/build_topic.py semaglutide-obesity-mace --now 2026-09-11`

```text
protocol_sha=3fb64a1e01434eb6ee9ea8a764a84c749270dfff
PRIMARY: 3-point major adverse cardiovascular events  k=1  RR=0.8 (0.72-0.9)  tau2=None
included trials: ['37952131']
declared-absent trials: []
comparator OA=True k=16
canonical: docs/reviews/semaglutide-obesity-mace/index.html
blind: docs/m/me5d639f4/  docs/m/m9e04a632/
```

### semaglutide-obesity-weight

`python scripts/build_topic.py semaglutide-obesity-weight --now 2026-09-11`

```text
Traceback (most recent call last):
  File "C:\mh-r-TYP3\scripts\build_topic.py", line 101, in <module>
    main(args[0], now)
    ~~~~^^^^^^^^^^^^^^
  File "C:\mh-r-TYP3\scripts\build_topic.py", line 68, in main
    manifest = build_review_dir(core, manifest_meta, review_dir, protocol_sha, from_cache=True)
  File "C:\mh-r-TYP3\harness\census.py", line 197, in build_review_dir
    _pa = membership.annotate_parity(_parity_row(_root, manifest_meta.get("slug", ""), review_core_obj), review_core_obj)
                                     ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\mh-r-TYP3\harness\census.py", line 115, in _parity_row
    return parity_relation.enrich(row, review_core_obj)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "C:\mh-r-TYP3\harness\parity_relation.py", line 239, in enrich
    raise ValueError(
    ...<3 lines>...
    )
ValueError: PARITY-RELATION REFUSED: hand status 'IDENTICAL_SET' disagrees with computed relation SUBSET for semaglutide-obesity-weight
```

### sglt2-ckd-progression

`python scripts/build_topic.py sglt2-ckd-progression --now 2026-09-11`

```text
protocol_sha=f6f7b14c820bdadd258122ac0bb54c7e4d2a989a
PRIMARY: Trial-defined primary cardiorenal composite  k=1  RR=0.72 (0.64-0.82)  tau2=None
included trials: ['36331190']
declared-absent trials: ['NCT05735197', 'NCT07344922', 'EMPA-CKD', 'ZODIAC', 'NCT05614115', 'DIAMOND', '32970396', '30990260']
comparator OA=True k=10
canonical: docs/reviews/sglt2-ckd-progression/index.html
blind: docs/m/me17c0a34/  docs/m/m42da3313/
```

### sglt2-hfref-hosp-cvdeath

`python scripts/build_topic.py sglt2-hfref-hosp-cvdeath --now 2026-09-11`

```text
Traceback (most recent call last):
  File "C:\mh-r-TYP3\scripts\build_topic.py", line 101, in <module>
    main(args[0], now)
    ~~~~^^^^^^^^^^^^^^
  File "C:\mh-r-TYP3\scripts\build_topic.py", line 68, in main
    manifest = build_review_dir(core, manifest_meta, review_dir, protocol_sha, from_cache=True)
  File "C:\mh-r-TYP3\harness\census.py", line 197, in build_review_dir
    _pa = membership.annotate_parity(_parity_row(_root, manifest_meta.get("slug", ""), review_core_obj), review_core_obj)
                                     ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\mh-r-TYP3\harness\census.py", line 115, in _parity_row
    return parity_relation.enrich(row, review_core_obj)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "C:\mh-r-TYP3\harness\parity_relation.py", line 239, in enrich
    raise ValueError(
    ...<3 lines>...
    )
ValueError: PARITY-RELATION REFUSED: hand status 'PARITY_REFUTED_BY_N' disagrees with computed relation SUBSET for sglt2-hfref-hosp-cvdeath
```

### sglt2-primary-prevention-hf

`python scripts/build_topic.py sglt2-primary-prevention-hf --now 2026-09-11`

```text
protocol_sha=f6f7b14c820bdadd258122ac0bb54c7e4d2a989a
PRIMARY: Hospitalization for heart failure  k=0  RR=None (None-None)  tau2=None
included trials: []
declared-absent trials: ['35061894', '31434508', '28605608', '26378978', '32966714', '30415602']
comparator OA=True k=8
canonical: docs/reviews/sglt2-primary-prevention-hf/index.html
blind: docs/m/m24cd09bc/  docs/m/mabc6654a/
```

### spironolactone-hfref-mortality

`python scripts/build_topic.py spironolactone-hfref-mortality --now 2026-09-11`

```text
Traceback (most recent call last):
  File "C:\mh-r-TYP3\scripts\build_topic.py", line 101, in <module>
    main(args[0], now)
    ~~~~^^^^^^^^^^^^^^
  File "C:\mh-r-TYP3\scripts\build_topic.py", line 68, in main
    manifest = build_review_dir(core, manifest_meta, review_dir, protocol_sha, from_cache=True)
  File "C:\mh-r-TYP3\harness\census.py", line 197, in build_review_dir
    _pa = membership.annotate_parity(_parity_row(_root, manifest_meta.get("slug", ""), review_core_obj), review_core_obj)
                                     ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\mh-r-TYP3\harness\census.py", line 115, in _parity_row
    return parity_relation.enrich(row, review_core_obj)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "C:\mh-r-TYP3\harness\parity_relation.py", line 239, in enrich
    raise ValueError(
    ...<3 lines>...
    )
ValueError: PARITY-RELATION REFUSED: hand status 'SUPERSET' disagrees with computed relation SUBSET for spironolactone-hfref-mortality
```

### statins-primary-prevention-elderly

`python scripts/build_topic.py statins-primary-prevention-elderly --now 2026-09-11`

```text
protocol_sha=036ee46c6c45cb5c10607def1eeda86ba536d750
PRIMARY: Major vascular events  k=0  RR=None (None-None)  tau2=None
included trials: []
declared-absent trials: ['30251369', '28531241', '20404379', '42670961']
comparator OA=True k=not stated in the comparator abstract/full text
canonical: docs/reviews/statins-primary-prevention-elderly/index.html
blind: docs/m/mb53e1ed5/  docs/m/ma178f5d6/
```

### ticagrelor-vs-clopidogrel-acs

`python scripts/build_topic.py ticagrelor-vs-clopidogrel-acs --now 2026-09-11`

```text
Traceback (most recent call last):
  File "C:\mh-r-TYP3\scripts\build_topic.py", line 101, in <module>
    main(args[0], now)
    ~~~~^^^^^^^^^^^^^^
  File "C:\mh-r-TYP3\scripts\build_topic.py", line 68, in main
    manifest = build_review_dir(core, manifest_meta, review_dir, protocol_sha, from_cache=True)
  File "C:\mh-r-TYP3\harness\census.py", line 197, in build_review_dir
    _pa = membership.annotate_parity(_parity_row(_root, manifest_meta.get("slug", ""), review_core_obj), review_core_obj)
                                     ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\mh-r-TYP3\harness\census.py", line 115, in _parity_row
    return parity_relation.enrich(row, review_core_obj)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "C:\mh-r-TYP3\harness\parity_relation.py", line 239, in enrich
    raise ValueError(
    ...<3 lines>...
    )
ValueError: PARITY-RELATION REFUSED: hand status 'SUPERSET' disagrees with computed relation IDENTICAL_SET for ticagrelor-vs-clopidogrel-acs
```

### tocilizumab-covid19-mortality

`python scripts/build_topic.py tocilizumab-covid19-mortality --now 2026-09-11`

```text
protocol_sha=38478f5e060a9d63bcb073cb652d0e6f70d27c58
PRIMARY: 28-day all-cause mortality  k=0  RR=None (None-None)  tau2=None
included trials: []
declared-absent trials: ['40232661', '38157348', '34609549', '33631066', '33332779', '33080017', '33080005', '33085857', '33472855', 'ARCHITECTS', 'CORON-ACT', '33933206']
comparator OA=True k=not stated in the comparator abstract/full text
canonical: docs/reviews/tocilizumab-covid19-mortality/index.html
blind: docs/m/m175bd0c3/  docs/m/m4670a8f9/
```

### tranexamic-acid-pph

`python scripts/build_topic.py tranexamic-acid-pph --now 2026-09-11`

```text
protocol_sha=dcb1b98082b6416b68ee073b09460626cfe07f0a
PRIMARY: Death due to bleeding  k=1  RR=0.81 (0.65-1.0)  tau2=None
included trials: ['28456509']
declared-absent trials: ['32143721', '36243576', 'TA TEG']
comparator OA=True k=not stated in the comparator abstract/full text
canonical: docs/reviews/tranexamic-acid-pph/index.html
blind: docs/m/md68c6ad6/  docs/m/m51474705/
```

Four parity declarations block page serialization after type refusals. Their existing pages remain at base bytes; their newly built type artifacts and evidence sidecars are available for integration. Successful rebuilds render their candidate type refusals. Shared index/blind-map side effects were restored to their pre-run bytes.

## Exact per-page limb_gate_every_page verdicts

The actual function was called once per page with only its review-directory enumeration scoped to that page. All gate checks were unchanged.

### semaglutide-obesity-mace

```text
REFUSED
```

MEASURED reason codes: `HARMS_INCOMPLETE`, `SENTENCE_WITHOUT_OBJECT`.

The complete unabridged function detail is retained under this slug in [verification.json](outputs/handover/lane_typ3/verification.json).

### semaglutide-obesity-weight

```text
REFUSED
```

MEASURED reason codes: `EFFECT_TYPE_REFUSED`, `HARMS_INCOMPLETE`, `PROSE_PREDICATE_FALSE`, `SENTENCE_WITHOUT_OBJECT`, `UNVERIFIED_FACT`.

The complete unabridged function detail is retained under this slug in [verification.json](outputs/handover/lane_typ3/verification.json).

### sglt2-ckd-progression

```text
REFUSED
```

MEASURED reason codes: `HARMS_INCOMPLETE`, `SENTENCE_WITHOUT_OBJECT`.

The complete unabridged function detail is retained under this slug in [verification.json](outputs/handover/lane_typ3/verification.json).

### sglt2-hfref-hosp-cvdeath

```text
REFUSED
```

MEASURED reason codes: `EFFECT_TYPE_REFUSED`, `HARMS_INCOMPLETE`, `PROSE_PREDICATE_FALSE`, `SENTENCE_WITHOUT_OBJECT`, `UNVERIFIED_FACT`.

The complete unabridged function detail is retained under this slug in [verification.json](outputs/handover/lane_typ3/verification.json).

### sglt2-primary-prevention-hf

```text
REFUSED
```

MEASURED reason codes: `HARMS_INCOMPLETE`, `SENTENCE_WITHOUT_OBJECT`.

The complete unabridged function detail is retained under this slug in [verification.json](outputs/handover/lane_typ3/verification.json).

### spironolactone-hfref-mortality

```text
REFUSED
```

MEASURED reason codes: `EFFECT_TYPE_REFUSED`, `HARMS_INCOMPLETE`, `SENTENCE_WITHOUT_OBJECT`, `UNVERIFIED_FACT`.

The complete unabridged function detail is retained under this slug in [verification.json](outputs/handover/lane_typ3/verification.json).

### statins-primary-prevention-elderly

```text
REFUSED
```

MEASURED reason codes: `HARMS_INCOMPLETE`, `SENTENCE_WITHOUT_OBJECT`.

The complete unabridged function detail is retained under this slug in [verification.json](outputs/handover/lane_typ3/verification.json).

### ticagrelor-vs-clopidogrel-acs

```text
REFUSED
```

MEASURED reason codes: `EFFECT_TYPE_REFUSED`, `HARMS_INCOMPLETE`, `SENTENCE_WITHOUT_OBJECT`, `UNVERIFIED_FACT`.

The complete unabridged function detail is retained under this slug in [verification.json](outputs/handover/lane_typ3/verification.json).

### tocilizumab-covid19-mortality

```text
REFUSED
```

MEASURED reason codes: `HARMS_INCOMPLETE`, `SENTENCE_WITHOUT_OBJECT`.

The complete unabridged function detail is retained under this slug in [verification.json](outputs/handover/lane_typ3/verification.json).

### tranexamic-acid-pph

```text
REFUSED
```

MEASURED reason codes: `HARMS_INCOMPLETE`, `SENTENCE_WITHOUT_OBJECT`.

The complete unabridged function detail is retained under this slug in [verification.json](outputs/handover/lane_typ3/verification.json).

## Sweeps

`python scripts/claim_scope_sweep.py`

```text
exit 0
UNVERIFIED_FACT: 28 of 28 verified_effects rows
Pages scanned: 32; scope_complete=false
```

`python scripts/effect_type_sweep.py`

```text
exit 0
{"topics": 32, "N": 98, "fully_typed": 0, "unknown_binding": 72, "would_be_refused": 78}
```

The stock claim sweep counts legacy `verified_effects.json` entries; it does not join the new canonical evidence sidecars. The stock type sweep counts currently served non-suppressed pools and omits refused rows. Neither is the requested fixed-base denominator. `outputs/handover/lane_typ3/fixed_row_audit.json` and the table above provide that measurement, including pages blocked before serialization.

## Tests and completion limits

```text
....................                                                     [100%]
20 passed in 16.11s
```

The focused suite includes digit/hash/span corruption, missing axis bases, cross-NCT span borrowing, middle-dot decimals, stale numeric tuple rejection, safety-set separation, and all-base-row persistence/render contracts. The TY suite includes pipeline → type → gate → renderer checks.

The expanded affected legacy suite had 23 passed and 5 failed; loading the shared modules from the exact base reproduced those same five failures (4 passed, 5 failed). See `base-legacy-tests.txt`. No fixture was relaxed to manufacture a pass. `git diff --check` passed.

Unresolved parity and page-gate failures are recorded in `STUCK_FAILURES.md`. There was no commit, push, deployment, workbook change, index-status promotion, or Overmind certification.
