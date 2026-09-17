# LANE TYP1 report

Base and finish HEAD: `e3b70bfa36dc65a3920b20fd4e2d628a270e7d28`. The checkout matches the commit printed in LANE_PROMPT.md; LANE_BASE.txt was absent. No commit, push, network retrieval, screening edit, protocol edit, coercion, or manually selected membership change was made.

**MEASURED:** denominator N is the 32 original trial–outcome rows in the eleven pages’ primary pools plus every value-bearing harm trial row, including suppressed harm pools. Frozen input: [baseline.json](outputs/typ1/baseline.json). Detailed transformations, exact evidence, twelve-axis objects and verdicts: [row_audit.json](outputs/typ1/row_audit.json). Rebuild refusals remain candidate rows and are rendered as such.

**INFERRED:** mappings such as an explicitly stated all-randomized analysis set to ITT, or a literal hazard-ratio label to HR, are conservative normalizations of cited text. Unknown analysis populations, recurrent-event counting rules, censoring policies and reconstructed effect measures were not filled from the protocol. Disease recurrence is not evidence that the estimator counts recurrent events.

**CLAIMED:** no submission-ready, release-ready, universal source-identity, or Overmind PASS claim is made. FACT establishes that the digits are located; it does not establish that the selected endpoint matches the page.

## Static versus dynamic disclosure

| Item | Static | Dynamic / validation |
|---|---|---|
| Scope | Eleven named slugs and frozen base candidate rows | Compared to the HEAD review objects; candidate values preserved by integration test |
| Text interpretation | Conservative lexical selectors, endpoint exceptions, enum normalizations | Every populated axis has a held-document SHA-256, literal span and character offset |
| Estimates and source evidence | No invented estimates or substitute papers | Numeric inputs copied from base; evidence bytes read from held abstracts, registry cache, own full text or exact AACT rows |
| FACT | Existing committed-byte requirement retained | Abstract UTF-8 field hash, or whole held-file hash, literal offset, all numeric fields checked; middle-dot decimal typography retained |
| Type | Opt-in held-text-v1 evidence mode | Existing TY builder constructs every effect_types.json; missing or invalid basis becomes UNKNOWN |
| AACT | Required table/column names and exact NCT/effect/CI matching rule | Snapshot read offline; original row bytes and source-table SHA recorded; surrogate outcome ID used only within the same snapshot |
| Counts and verdicts | Stable baseline denominator definition | Calculated from row_audit.json and executed gate/sweep logs |

## Base plants, before data edits

The ELIXA positive control verified as FACT. The following are the actual refusal outputs from the base (a negative plant passing its test means the attempted claim failed):
```text
ONE DIGIT PLANT: {'verified': False, 'class': 'UNVERIFIED_FACT', 'reason': 'span is not located verbatim in extracted text'}
NO BASIS PLANT: {'value': 'UNKNOWN', 'basis': {'absence_code': 'NO_ROW_EVIDENCE'}} {'status': 'UNKNOWN_FAILS_CLOSED', 'axis': 3, 'axis_name': 'analysis_set', 'reason': 'UNTYPED — axis 3 unknown: NO_ROW_EVIDENCE'}
```

## Per-page measured coverage

Fully typed below means every **declared binding axis is known**, not that its value matches the protocol. A known mismatch still refuses. FACT/type counts use the same frozen N before and after; this avoids counting a vanished row as a coverage improvement.

| Page | FACT before → after | Binding axes known before → after | Still type-refused / original N | Gate limb |
|---|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | 0 of 3 → 3 of 3 | 0 of 3 → 0 of 3 | 3 of 3 | REFUSED |
| colchicine-postop-af | 0 of 5 → 5 of 5 | 0 of 5 → 0 of 5 | 5 of 5 | REFUSED |
| colchicine-recurrent-pericarditis | 0 of 2 → 1 of 2 | 2 of 2 → 1 of 2 | 1 of 2 | REFUSED |
| colchicine-secondary-cv-prevention | 0 of 5 → 5 of 5 | 1 of 5 → 1 of 5 | 4 of 5 | REFUSED |
| corticosteroids-cap-mortality | 0 of 4 → 4 of 4 | 1 of 4 → 1 of 4 | 4 of 4 | REFUSED |
| corticosteroids-covid19-mortality | 0 of 1 → 1 of 1 | 0 of 1 → 1 of 1 | 1 of 1 | REFUSED |
| dapagliflozin-hfpef-hosp | 0 of 1 → 1 of 1 | 0 of 1 → 0 of 1 | 1 of 1 | REFUSED |
| denosumab-vertebral-fracture | 0 of 1 → 1 of 1 | 0 of 1 → 0 of 1 | 1 of 1 | REFUSED |
| doac-vte-recurrence | 0 of 6 → 6 of 6 | 0 of 6 → 0 of 6 | 6 of 6 | REFUSED |
| dpp4-mace-t2d | 0 of 3 → 3 of 3 | 0 of 3 → 0 of 3 | 3 of 3 | REFUSED |
| empagliflozin-hfpef-hosp | 0 of 1 → 1 of 1 | 0 of 1 → 1 of 1 | 0 of 1 | REFUSED |

Across all original rows: 31 FACT of 32 rows; 5 rows known on every binding axis of 32; 29 type-refused of 32. These are three different measurements.

## Every row: missing axes and refusal

Nonbinding UNKNOWN axes are also named; a known measure for a reported effect is not copied onto an effect reconstructed from arm counts. For reconstructed rows, a future explicit transformation basis would be needed; it is not held-text FACT evidence.

| Page / PMID / outcome | FACT | UNKNOWN binding axes | Other UNKNOWN axes | Type verdict |
|---|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality / 35041780 / Mortality | FACT | analysis_set, effect_measure | first_or_recurrent, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: analysis_set |
| balanced-crystalloids-vs-saline-mortality / 34375394 / Mortality | FACT | analysis_set | first_or_recurrent, time_origin, censoring, estimator | UNKNOWN_FAILS_CLOSED: analysis_set |
| balanced-crystalloids-vs-saline-mortality / 35041780 / New renal-replacement therapy | FACT | effect_measure | analysis_set, first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: effect_measure |
| colchicine-postop-af / 42132185 / Postoperative atrial fibrillation | FACT | analysis_set | first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: analysis_set |
| colchicine-postop-af / 32720823 / Postoperative atrial fibrillation | FACT | analysis_set, effect_measure | first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: analysis_set |
| colchicine-postop-af / 25172965 / Postoperative atrial fibrillation | FACT | analysis_set, effect_measure | first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: analysis_set |
| colchicine-postop-af / 27502857 / Postoperative atrial fibrillation | FACT | analysis_set, effect_measure | first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: analysis_set |
| colchicine-postop-af / 27502857 / Gastrointestinal adverse effects | FACT | effect_measure | analysis_set, first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: effect_measure |
| colchicine-recurrent-pericarditis / 24694983 / Recurrent pericarditis | FACT | none | first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator | MATCH |
| colchicine-recurrent-pericarditis / 21873705 / Recurrent pericarditis | UNVERIFIED_FACT | effect_measure | analysis_set, first_or_recurrent, time_origin, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: effect_measure |
| colchicine-secondary-cv-prevention / 31733140 / Trial-defined major coronary/cardiovascular composite | FACT | analysis_set | first_or_recurrent, time_origin, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: analysis_set |
| colchicine-secondary-cv-prevention / 32865380 / Trial-defined major coronary/cardiovascular composite | FACT | analysis_set | first_or_recurrent, time_origin, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: analysis_set |
| colchicine-secondary-cv-prevention / 39555823 / Trial-defined major coronary/cardiovascular composite | FACT | analysis_set | first_or_recurrent, time_origin, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: analysis_set |
| colchicine-secondary-cv-prevention / 34876021 / Gastrointestinal adverse effects | FACT | effect_measure | analysis_set, first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: effect_measure |
| colchicine-secondary-cv-prevention / 32865380 / Non-cardiovascular death | FACT | none | analysis_set, first_or_recurrent, time_origin, censoring, adjustment, estimator | MATCH |
| corticosteroids-cap-mortality / 36942789 / All-cause mortality | FACT | analysis_set, effect_measure | first_or_recurrent, time_origin, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: analysis_set |
| corticosteroids-cap-mortality / 25688779 / All-cause mortality | FACT | analysis_set, effect_measure | first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: analysis_set |
| corticosteroids-cap-mortality / 25688779 / Hyperglycaemia | FACT | effect_measure | analysis_set, first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: effect_measure |
| corticosteroids-cap-mortality / 25608756 / Hyperglycaemia | FACT | none | analysis_set, first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator | REFUSE: effect_measure |
| corticosteroids-covid19-mortality / 32678530 / 28-day all-cause mortality | FACT | none | first_or_recurrent, censoring | REFUSE: effect_measure |
| dapagliflozin-hfpef-hosp / 36027570 / Composite cardiovascular death or worsening heart failure | FACT | analysis_set | first_or_recurrent, time_origin, censoring | UNKNOWN_FAILS_CLOSED: analysis_set |
| denosumab-vertebral-fracture / 19671655 / New vertebral fracture | FACT | analysis_set | first_or_recurrent, time_origin, censoring, adjustment | UNKNOWN_FAILS_CLOSED: analysis_set |
| doac-vte-recurrence / 24344086 / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | FACT | analysis_set | first_or_recurrent, time_origin, censoring, adjustment | UNKNOWN_FAILS_CLOSED: analysis_set |
| doac-vte-recurrence / 19966341 / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | FACT | analysis_set | first_or_recurrent, time_origin, follow_up, censoring, adjustment | UNKNOWN_FAILS_CLOSED: analysis_set |
| doac-vte-recurrence / 22449293 / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | FACT | analysis_set | population, first_or_recurrent, time_origin, follow_up, censoring | UNKNOWN_FAILS_CLOSED: analysis_set |
| doac-vte-recurrence / 21128814 / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | FACT | analysis_set | first_or_recurrent, time_origin, follow_up, censoring | UNKNOWN_FAILS_CLOSED: analysis_set |
| doac-vte-recurrence / 23991658 / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | FACT | analysis_set | first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: analysis_set |
| doac-vte-recurrence / 23808982 / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | FACT | analysis_set | first_or_recurrent, time_origin, follow_up, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: analysis_set |
| dpp4-mace-t2d / 23992601 / 3-point major adverse cardiovascular events | FACT | analysis_set | first_or_recurrent, time_origin, censoring, adjustment, estimator | UNKNOWN_FAILS_CLOSED: analysis_set |
| dpp4-mace-t2d / 30418475 / 3-point major adverse cardiovascular events | FACT | analysis_set | time_origin, censoring | UNKNOWN_FAILS_CLOSED: analysis_set |
| dpp4-mace-t2d / 28893244 / 3-point major adverse cardiovascular events | FACT | analysis_set | time_origin, censoring, adjustment | UNKNOWN_FAILS_CLOSED: analysis_set |
| empagliflozin-hfpef-hosp / 34449189 / Composite cardiovascular death or worsening heart failure | FACT | none | first_or_recurrent | MATCH |

## Unverified numeric row

`colchicine-recurrent-pericarditis / PMID 21873705 / Recurrent pericarditis` remains **UNVERIFIED_FACT**. The held abstract states relative risk **reduction** 0.56 (CI 0.27 to 0.73); the existing row is RR 0.44 (0.27 to 0.73). The estimate is a transformation and the interval endpoints happen to be unchanged under the complement transformation, but this is not verbatim evidence of a reported RR. No corrected estimate or interval was authored. [Held abstract](cache/colchicine-recurrent-pericarditis/records.json).

## Coercions and endpoint findings for the integrator

No coercion record was created. These are disclosures, not authorizations to equate different estimands.

**COERCION NEEDED: effect_measure HR→RR**, balanced-crystalloids-vs-saline-mortality / PMID 34375394 / Mortality; evidence: “By day 90, 1381 of 5230 patients (26.4%) assigned to a balanced solution died vs 1439 of 5290 patients (27.2%) assigned to saline solution (adjusted hazard ratio, 0.97 [95% CI, 0.90-1.05]; P = .47).”.

**COERCION NEEDED: effect_measure OR→RR**, corticosteroids-cap-mortality / PMID 25608756 / Hyperglycaemia; evidence: “The prednisone group had a higher incidence of in-hospital hyperglycaemia needing insulin treatment (76 [19%] vs 43 [11%]; OR 1·96, 95% CI 1·31-2·93, p=0·0010).”.

**COERCION NEEDED: effect_measure HR→OR**, corticosteroids-covid19-mortality / PMID 32678530 / 28-day all-cause mortality; evidence: “For the primary outcome of 28-day mortality, the hazard ratio from Cox regression was used to estimate the mortality rate ratio.”.

**COERCION NEEDED: effect_measure RR→HR**, doac-vte-recurrence / PMID 23808982 / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death); evidence: “RESULTS: The primary efficacy outcome occurred in 59 of 2609 patients (2.3%) in the apixaban group, as compared with 71 of 2635 (2.7%) in the conventional-therapy group (relative risk, 0.84; 95% confidence interval [CI], 0.60 to 1.18; difference in risk [apixaban minus conventional therapy], -0.4 percentage points; 95% CI, -1.3 to 0.4).”.

**Endpoint mismatch, not repaired by numeric provenance:** dapagliflozin PMID 36027570 currently selects CV death HR 0.88 (0.74–1.05), whereas the held abstract’s composite is HR 0.82 (0.73–0.92). Empagliflozin PMID 34449189 currently selects registry CV death HR 0.91 (0.76–1.09), whereas its held abstract’s composite is HR 0.79 (0.69–0.90). Both row types say CV_DEATH only. The protocols’ compiled binding axes do not bind endpoint_components, so the empagliflozin row can MATCH the type contract despite this endpoint mismatch. Integrator action is required; do not interpret MATCH as endpoint validation. [Dapagliflozin source](cache/dapagliflozin-hfpef-hosp/records.json); [empagliflozin source](cache/empagliflozin-hfpef-hosp/records.json).

**COERCION NEEDED: endpoint_components CV_DEATH→the declared cardiovascular-death/worsening-HF composite**, for those two HFpEF rows, if anyone proposes to pool the current numbers under that composite. Evidence: the held registry titles are “Subjects Included in the Endpoint of Cardiovascular Death” and “Time to Adjudicated Cardiovascular (CV) Death”. This is an endpoint-selection defect; replacing the selection requires integrator adjudication, not an automatic coercion.

**Source-specific analysis caveat:** the denosumab held registry defines its primary efficacy analysis set as randomized participants with a baseline and at least one postbaseline vertebral-fracture evaluation, using last observation carried forward. It was not labeled ITT by inference. SAVOR’s abstract does not state nonfatal status for its MI/stroke components; those component distinctions remain explicit rather than adopting a generic 3-point MACE definition.

## Offline evidence and implementation

All eleven caches and own held full texts were inspected. Matching abstracts are hashed over exact UTF-8 `abstract` field bytes. Registry JSON and own full-text files are hashed over file bytes. Offsets count decoded characters. Existing source bytes, values, protocols, eligibility and coercion registers were not edited.

The local AACT snapshot directory label was read through harness/aact.py; the label is not asserted to be the true data date. Schema checks and matched-row inventory for design_groups, interventions, eligibilities, design_outcomes and outcome_analyses are in [aact_inventory.json](outputs/typ1/aact_inventory.json). Exact selected outcome_analyses rows are held under the five affected cache/held directories with manifests in aact_axis_evidence.json. New type evidence can cite those held extracts without a commit; FACT verification still requires committed source bytes. No new AACT extract was promoted to FACT.

Additive integration: harness/verified_inputs.py joins by page, outcome and PMID, rejects changed numeric values/measure, and attaches evidence before TY unification. The opt-in builder validates held hashes/spans/offsets and bypasses legacy inference from source summaries. Other pages without overlays retain the prior path. harness/gate.py, harness/synth.py, search, screening and other lanes’ review directories were not edited.

## Rebuilds, tests and sweeps

Every page was rebuilt with `python scripts/build_topic.py <slug> --now 2026-09-11`; each final build exited 0. This is build execution success, not a publication-gate PASS. Logs: [final-commands.json](outputs/typ1/final-commands.json), [supplement-commands.json](outputs/typ1/supplement-commands.json), and the per-page build-*.txt files. Network socket connections were blocked for authoring, rebuild, sweep and verification subprocesses.

Final source/identity audit also passed: all 32 frozen rows equal their HEAD source review rows exactly; protected files and other review pages are unchanged ([final-audit.json](outputs/typ1/final-audit.json)). `git diff --check` passed.

Final targeted tests (provenance, TY, evidence integration and rendered-refusal/candidate-preservation contract):
```text
...................                                                      [100%]
19 passed in 13.41s
```

Both required sweep scripts were run before and after. Their default coverage is currently served, nonsuppressed pools (and cache verified_effects for the claim sweep), not the frozen primary-plus-harms denominator above. After rebuilding, refused candidates disappear from that sweep denominator but remain in effect_types.json and row_audit.json. Scoped outputs are held in outputs/typ1/before-*.json and after-*.json; shared global sweep files were restored to avoid overwriting other lanes’ reports.

```text
UNVERIFIED_FACT: 28 of 28 verified_effects rows
Pages scanned: 32; scope_complete=false
{"topics": 32, "N": 112, "fully_typed": 0, "unknown_binding": 85, "would_be_refused": 94}
UNVERIFIED_FACT: 28 of 28 verified_effects rows
Pages scanned: 32; scope_complete=false
{"topics": 32, "N": 84, "fully_typed": 0, "unknown_binding": 59, "would_be_refused": 66}
```

## Exact gate-limb verdicts

`scripts/typ1_verify.py` invokes the unmodified `scripts/verify_all.py::limb_gate_every_page` once per page, restricting only the directory enumeration to that page. No gate check or refusal was patched out.

### balanced-crystalloids-vs-saline-mortality: REFUSED
```text
REFUSED
TARGET verify_all.limb_gate_every_page: head=e3b70bfa36dc65a3920b20fd4e2d628a270e7d28 base=none tree=dirty:111 files files=1 docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json
```
Complete unabridged limb output: [gates.json](outputs/typ1/gates.json). Refusal classes observed: SENTENCE_WITHOUT_OBJECT, CERTAINTY_ARITHMETIC_MISMATCH, HARMS_INCOMPLETE, scope_identity, no pooled result, manuscript prose contains numerals.

### colchicine-postop-af: REFUSED
```text
REFUSED
TARGET verify_all.limb_gate_every_page: head=e3b70bfa36dc65a3920b20fd4e2d628a270e7d28 base=none tree=dirty:111 files files=1 docs/reviews/colchicine-postop-af/review.json
```
Complete unabridged limb output: [gates.json](outputs/typ1/gates.json). Refusal classes observed: SENTENCE_WITHOUT_OBJECT, CERTAINTY_ARITHMETIC_MISMATCH, HARMS_INCOMPLETE, no pooled result, manuscript prose contains numerals.

### colchicine-recurrent-pericarditis: REFUSED
```text
REFUSED
TARGET verify_all.limb_gate_every_page: head=e3b70bfa36dc65a3920b20fd4e2d628a270e7d28 base=none tree=dirty:111 files files=1 docs/reviews/colchicine-recurrent-pericarditis/review.json
```
Complete unabridged limb output: [gates.json](outputs/typ1/gates.json). Refusal classes observed: SENTENCE_WITHOUT_OBJECT, CERTAINTY_ARITHMETIC_MISMATCH, UNVERIFIED_FACT, HARMS_INCOMPLETE, manuscript prose contains numerals.

### colchicine-secondary-cv-prevention: REFUSED
```text
REFUSED
TARGET verify_all.limb_gate_every_page: head=e3b70bfa36dc65a3920b20fd4e2d628a270e7d28 base=none tree=dirty:111 files files=1 docs/reviews/colchicine-secondary-cv-prevention/review.json
```
Complete unabridged limb output: [gates.json](outputs/typ1/gates.json). Refusal classes observed: SENTENCE_WITHOUT_OBJECT, CERTAINTY_ARITHMETIC_MISMATCH, HARMS_INCOMPLETE, scope_identity, no pooled result, manuscript prose contains numerals.

### corticosteroids-cap-mortality: REFUSED
```text
REFUSED
TARGET verify_all.limb_gate_every_page: head=e3b70bfa36dc65a3920b20fd4e2d628a270e7d28 base=none tree=dirty:111 files files=1 docs/reviews/corticosteroids-cap-mortality/review.json
```
Complete unabridged limb output: [gates.json](outputs/typ1/gates.json). Refusal classes observed: SENTENCE_WITHOUT_OBJECT, CERTAINTY_ARITHMETIC_MISMATCH, HARMS_INCOMPLETE, no pooled result, manuscript prose contains numerals.

### corticosteroids-covid19-mortality: REFUSED
```text
REFUSED
TARGET verify_all.limb_gate_every_page: head=e3b70bfa36dc65a3920b20fd4e2d628a270e7d28 base=none tree=dirty:111 files files=1 docs/reviews/corticosteroids-covid19-mortality/review.json
```
Complete unabridged limb output: [gates.json](outputs/typ1/gates.json). Refusal classes observed: SENTENCE_WITHOUT_OBJECT, CERTAINTY_ARITHMETIC_MISMATCH, HARMS_INCOMPLETE, scope_identity, no pooled result, manuscript prose contains numerals.

### dapagliflozin-hfpef-hosp: REFUSED
```text
REFUSED
TARGET verify_all.limb_gate_every_page: head=e3b70bfa36dc65a3920b20fd4e2d628a270e7d28 base=none tree=dirty:111 files files=1 docs/reviews/dapagliflozin-hfpef-hosp/review.json
```
Complete unabridged limb output: [gates.json](outputs/typ1/gates.json). Refusal classes observed: SENTENCE_WITHOUT_OBJECT, CERTAINTY_ARITHMETIC_MISMATCH, HARMS_INCOMPLETE, scope_identity, no pooled result, manuscript prose contains numerals.

### denosumab-vertebral-fracture: REFUSED
```text
REFUSED
TARGET verify_all.limb_gate_every_page: head=e3b70bfa36dc65a3920b20fd4e2d628a270e7d28 base=none tree=dirty:111 files files=1 docs/reviews/denosumab-vertebral-fracture/review.json
```
Complete unabridged limb output: [gates.json](outputs/typ1/gates.json). Refusal classes observed: SENTENCE_WITHOUT_OBJECT, CERTAINTY_ARITHMETIC_MISMATCH, HARMS_INCOMPLETE, scope_identity, no pooled result, manuscript prose contains numerals.

### doac-vte-recurrence: REFUSED
```text
REFUSED
TARGET verify_all.limb_gate_every_page: head=e3b70bfa36dc65a3920b20fd4e2d628a270e7d28 base=none tree=dirty:111 files files=1 docs/reviews/doac-vte-recurrence/review.json
```
Complete unabridged limb output: [gates.json](outputs/typ1/gates.json). Refusal classes observed: SENTENCE_WITHOUT_OBJECT, CERTAINTY_ARITHMETIC_MISMATCH, HARMS_INCOMPLETE, scope_identity, no pooled result, manuscript prose contains numerals.

### dpp4-mace-t2d: REFUSED
```text
REFUSED
TARGET verify_all.limb_gate_every_page: head=e3b70bfa36dc65a3920b20fd4e2d628a270e7d28 base=none tree=dirty:111 files files=1 docs/reviews/dpp4-mace-t2d/review.json
```
Complete unabridged limb output: [gates.json](outputs/typ1/gates.json). Refusal classes observed: SENTENCE_WITHOUT_OBJECT, CERTAINTY_ARITHMETIC_MISMATCH, HARMS_INCOMPLETE, scope_identity, no pooled result, manuscript prose contains numerals.

### empagliflozin-hfpef-hosp: REFUSED
```text
REFUSED
TARGET verify_all.limb_gate_every_page: head=e3b70bfa36dc65a3920b20fd4e2d628a270e7d28 base=none tree=dirty:111 files files=1 docs/reviews/empagliflozin-hfpef-hosp/review.json
```
Complete unabridged limb output: [gates.json](outputs/typ1/gates.json). Refusal classes observed: SENTENCE_WITHOUT_OBJECT, CERTAINTY_ARITHMETIC_MISMATCH, manuscript prose contains numerals.

## Completion and remaining ship blockers

The lane evidence pass and requested proof are complete. Gate refusals and unresolved source/type defects are retained, not bypassed. No page is promoted to shipped/certified. The integrator must decide endpoint selection, missing binding evidence, declared coercions, and any unrelated gate debt before release. [STUCK_FAILURES.md](STUCK_FAILURES.md) records the remaining blockers. No commit was made.
