# LANE HM3 report

MEASURED: 50 of 50 baseline trial × harm items resolved from held sources: 6 count extractions, 2 published effect+CI extractions, 38 typed refusals, and 4 spurious signals.

HEAD: `f6f7b14c820bdadd258122ac0bb54c7e4d2a989a` (matches specified WIP base). No commit; no network; no deployment.
Builds use the instructed fixed date `2026-09-11`. Work and verification performed 2026-09-17.

HM completeness: 17/17 pages pass. Full publication gate: 16/17 pass.
Ticagrelor retains its pre-existing scope_identity refusal. The lane prohibits changes to search, screening and membership; it is not reported as publication-ready.

## Per-page measured resolution

| Page | Resolved of baseline N | Counts | Effect+CI | Typed refusal | Spurious |
|---|---:|---:|---:|---:|---:|
| tocilizumab-covid19-mortality | 6 of 6 | 1 | 0 | 5 | 0 |
| melatonin-primary-insomnia-sol | 5 of 5 | 1 | 0 | 4 | 0 |
| balanced-crystalloids-vs-saline-mortality | 4 of 4 | 0 | 0 | 3 | 1 |
| corticosteroids-covid19-mortality | 4 of 4 | 1 | 0 | 3 | 0 |
| omega3-cardiovascular-events | 4 of 4 | 0 | 0 | 3 | 1 |
| semaglutide-obesity-weight | 4 of 4 | 0 | 0 | 4 | 0 |
| spironolactone-hfref-mortality | 4 of 4 | 0 | 0 | 4 | 0 |
| corticosteroids-cap-mortality | 3 of 3 | 2 | 0 | 1 | 0 |
| esketamine-trd-madrs | 2 of 2 | 1 | 0 | 1 | 0 |
| metformin-pcos-ovulation | 2 of 2 | 0 | 0 | 1 | 1 |
| sglt2-ckd-progression | 2 of 2 | 0 | 1 | 1 | 0 |
| sglt2-hfref-hosp-cvdeath | 2 of 2 | 0 | 0 | 2 | 0 |
| statins-primary-prevention-elderly | 2 of 2 | 0 | 0 | 2 | 0 |
| ticagrelor-vs-clopidogrel-acs | 2 of 2 | 0 | 1 | 1 | 0 |
| tranexamic-acid-pph | 2 of 2 | 0 | 0 | 2 | 0 |
| denosumab-vertebral-fracture | 1 of 1 | 0 | 0 | 1 | 0 |
| semaglutide-obesity-mace | 1 of 1 | 0 | 0 | 0 | 1 |

N is the number of baseline `known_reported_not_yet_extracted` trial–outcome pairs, not unique trials. Unresolved harm items: none. A typed refusal resolves extraction debt; it does not establish absence of harm.

## Gate output, verbatim

Each page was built with `python scripts/build_topic.py <slug> --now 2026-09-11`, then checked with `harness.gate.gate_page`, the function used by `verify_all.limb_gate_every_page`. Every build exited 0. The runner blocks socket connections and restores shared index/blind-map bytes after builds.

```text
tocilizumab-covid19-mortality: PASS
melatonin-primary-insomnia-sol: PASS
balanced-crystalloids-vs-saline-mortality: PASS
corticosteroids-covid19-mortality: PASS
omega3-cardiovascular-events: PASS
semaglutide-obesity-weight: PASS
spironolactone-hfref-mortality: PASS
corticosteroids-cap-mortality: PASS
esketamine-trd-madrs: PASS
metformin-pcos-ovulation: PASS
sglt2-ckd-progression: PASS
sglt2-hfref-hosp-cvdeath: PASS
statins-primary-prevention-elderly: PASS
ticagrelor-vs-clopidogrel-acs: L1(scope_identity): open P/I/C/design eligibility was evaluated only inside a pre-identified retrieval set; the open eligibility universe was not tested -- render the pre-identified-set qualification before claiming screening count = k
tranexamic-acid-pph: PASS
denosumab-vertebral-fracture: PASS
semaglutide-obesity-mace: PASS
```

Raw build output and structured gate results: [evidence directory](docs/evidence/hm3-held-source-audit/).

## Plant-first proof

Before implementation changes, the synthetic fixture contained one KNOWN_REPORTED_NOT_YET_EXTRACTED item. Running `python -m pytest tests/test_hm3_contract.py -q` with an assertion that the gate accepted it failed as follows (test-only synthetic data):

```text
F                                                                        [100%]
================================== FAILURES ===================================
_____________________________ test_hm3_gate_plant _____________________________

tmp_path = WindowsPath('C:/mh-r-HM3/.tmp/pytest-of-mahmo/pytest-0/test_hm3_gate_plant0')

    def test_hm3_gate_plant(tmp_path):
        spec = {'name': 'Adverse events', 'keywords': ['adverse events'], 'estimand': 'RR'}
        out = {'name': spec['name'], 'kind': 'harm', 'trials': [],
               'declared_absent_trials': [{'id': 'fixture', 'reason_code': 'OUTCOME_NOT_IN_SOURCE'}],
               'result': {'present': False}}
        harms.annotate_outcome(out, spec, [{'id': 'fixture'}],
                               {'fixture': {'abstract': 'Adverse events were similar between groups.'}})
        (tmp_path / 'review.json').write_text(json.dumps({'outcomes': [out]}), encoding='utf-8')
>       assert gate.check_harms_complete(str(tmp_path)) == []
E       AssertionError: assert ['L1: HARMS_I...arm absence.'] == []
E         
E         Left contains one more item: 'L1: HARMS_INCOMPLETE -- Adverse events: HARMS_INCOMPLETE -- 1 known reported outcome(s) unresolved (fixture) among 1 source-reporting trial(s); extracted k=0. The page must not render this as harm absence.'
E         Use -v to get more diff

tests\test_hm3_contract.py:15: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_hm3_contract.py::test_hm3_gate_plant - AssertionError: asse...
1 failed in 3.50s
```

The final test first asserts this refusal, then applies a cited REFUSED_ON_EVIDENCE adjudication, reannotates the outcome and requires the same unchanged HM gate to pass.

## Verification

`python -m pytest tests/test_harms_recovery.py tests/test_override_audit.py -q`

```text
.....                                                                    [100%]
5 passed in 2.50s
```

`python -m pytest tests/test_hm3_contract.py tests/test_hm3_pages.py tests/test_absence_ontology.py tests/test_verified_override.py tests/test_verified_effects.py tests/test_source_hierarchy.py tests/test_source_hierarchy_regression.py tests/test_missing_effect.py tests/test_page.py tests/test_honest_states_renderable.py -q`

```text
............................................................             [100%]
60 passed in 4.58s
```

The rebuilt-page E2E contract checks every baseline item against its served review, verbatim refusal spans, extracted values and verification states, plus unchanged screening records and primary trial values. The second pass checks source PMIDs, source hashes, count bounds and interval ordering, and the three pre-existing overrides against held records.

## Implementation and audit

- Added distinct-outcome lists while retaining the legacy single-object format; duplicate trial–outcome inputs fail closed. Pipeline selection is outcome-specific.
- Missing-effect enrichment uses the explicit outcome or the registered primary outcome; it cannot borrow a harm estimate.
- Added SIGNAL_SPURIOUS and a typed-refusal path that requires a recognized code, reason and exact span in the held abstract/full text.
- Count overrides retain their actual abstract/full-text provenance and receive digit verification rather than the AACT trusted-entry shortcut.
- Extended override auditing to every list member. Replaced the three stale audit outcome labels for esketamine NCT02417064 and CKD PMIDs 32970396/36331190; preserved their existing numeric inputs.
- `harness/gate.py`, `harness/synth.py`, search, screening, membership and other lane pages were not modified.

## Held-source boundaries

Local AACT was read through the adapter schema from snapshot folder `2026-08-30`; this is an archive locator, not a claim about source-record currency. Verbatim filtered rows and hashes are retained in [aact/](docs/evidence/hm3-held-source-audit/aact/), including reported_events, reported_event_totals, outcome_counts, outcomes, outcome_measurements and result_groups. No percentages were multiplied by an assumed denominator. Overlapping adverse-event categories were not summed.

Second-pass identity checks excluded embedded fulltext_by_pmid entries for melatonin PMID 33157425 (ARE/MLT study), semaglutide PMID 40825340 (review text), and esketamine PMID 31109201 (French prospective cohort). These texts were not used as numbers for the named trials; the held abstracts and matching primary sources were used. Source-cache repairs are outside this harm lane.

The tocilizumab PMID 33085857 extraction uses the published narrative participant totals (28 and 12), with Table 4 denominators (161 and 82); it does not sum the 36 and 38 events. The local registry totals differ (19 and 8), so the published participant counts are explicitly identified as the chosen source.

## Static versus dynamic disclosure

| Component | Static / dynamic | Evidence and transformation |
|---|---|---|
| Outcome identities and refusal judgments | Static, reviewed | Existing protocol/specifications and verbatim held spans |
| New counts and HRs | Static source transcription | Exact digits; no imputed denominator or variance |
| Original combined MADRS input | Existing derived value | Rechecked original per-arm values and weighted mean/pooled-SD arithmetic; not changed |
| Baseline N, resolved counts, gates and synthesis | Dynamic | Baseline review objects, new verified inputs, unchanged gate and synthesis |
| Synthetic fixture | Static test data | Explicitly synthetic; never included in published evidence |

MEASURED: baseline lists, source spans, values, hashes, rebuild exits, gate results and test results. INFERRED: endpoint/population/timepoint compatibility and refusal judgments, stated per item below. CLAIMED: no clinical effect conclusion, completeness of an unheld source, or release certification beyond those measured checks.

## Item-by-item decisions

Full verbatim spans and source document references are in [decisions.json](docs/evidence/hm3-held-source-audit/decisions.json) and each topic’s verified input file. The machine-readable audit identifies each trial and outcome separately.

### tocilizumab-covid19-mortality

- **40232661 — Serious adverse events**: typed refusal (`POPULATION_MISMATCH`). The abstract reports no serious adverse events, but the held safety analysis uses SOC 29 and tocilizumab 33 rather than the randomized 30 and 32, so an as-randomized safety denominator is not established. [Held source](cache/tocilizumab-covid19-mortality/ft_40232661.txt).
- **38157348 — Serious adverse events**: typed refusal (`TIMEPOINT_MISMATCH`). The held table gives patients with serious adverse events through study day 29, whereas this protocol specifies by day 28; the day-28 counts are not separately reported. [Held source](cache/tocilizumab-covid19-mortality/ft_38157348.txt).
- **34609549 — Serious adverse events**: typed refusal (`POPULATION_MISMATCH`). The safety table reports 128/429 and 72/213 in the treated safety population rather than the randomized 434 and 215 required by the protocol. [Held source](cache/tocilizumab-covid19-mortality/ft_34609549.txt).
- **33080017 — Serious adverse events**: typed refusal (`POPULATION_MISMATCH`). The source reports 20 and 29 serious-adverse-event patients but excludes a tocilizumab consent withdrawal from analysis, so these are not the protocol as-randomized counts over 64 and 67. [Held source](cache/tocilizumab-covid19-mortality/records.json).
- **33085857 — Serious adverse events**: extracted (counts). Published safety narrative reports 28 and 12 participants with serious adverse events (not 36 and 38 recurrent events); Table 4 provides the randomized 161 and 82 denominators. AACT totals differ (19 and 8); the published all-SAE participant counts are used, not summed registry categories. [Held source](cache/tocilizumab-covid19-mortality/ft_33085857.txt).
- **33472855 — Serious adverse events**: typed refusal (`POPULATION_MISMATCH`). The safety table explicitly assigns patients according to treatment received (67 and 62), whereas the protocol requires the randomized groups (65 and 64). [Held source](cache/tocilizumab-covid19-mortality/ft_33472855.txt).

### melatonin-primary-insomnia-sol

- **33157425 — Adverse events**: typed refusal (`REFUSED_ON_EVIDENCE`). The source reports no serious adverse events but supplies no count of patients with any adverse event or side effect, the registered broader endpoint. [Held source](cache/melatonin-primary-insomnia-sol/records.json).
- **22346363 — Adverse events**: typed refusal (`POPULATION_MISMATCH`). The safety analysis pools randomized, single-blind and open-label studies and therefore cannot supply an independent randomized-trial adverse-event comparison. [Held source](cache/melatonin-primary-insomnia-sol/records.json).
- **20712869 — Adverse events**: extracted (counts). Table 8: Any AE in the initial three-week randomized treatment period, entire adult safety population; extension-period rerandomization is not combined with it. [Held source](cache/melatonin-primary-insomnia-sol/ft_20712869.txt).
- **18036082 — Adverse events**: typed refusal (`REFUSED_ON_EVIDENCE`). The source describes a low incidence and minor severity of adverse events but reports no arm counts or effect with confidence interval. [Held source](cache/melatonin-primary-insomnia-sol/records.json).
- **12790159 — Adverse events**: typed refusal (`MULTI_ARM_UNRESOLVED`). The source reports no significant side-effect difference across placebo and two melatonin doses without dose-specific counts or effect with confidence interval. [Held source](cache/melatonin-primary-insomnia-sol/records.json).

### balanced-crystalloids-vs-saline-mortality

- **35041780 — Acute kidney injury**: typed refusal (`REFUSED_ON_EVIDENCE`). The source gives renal-replacement therapy counts and mean creatinine changes, but no incidence count or ratio estimate for acute kidney injury itself. [Held source](cache/balanced-crystalloids-vs-saline-mortality/records.json).
- **34375394 — Acute kidney injury**: spurious signal (`SIGNAL_SPURIOUS`). The acute-kidney-injury phrase describes background literature, not a reported kidney-injury result of this trial. [Held source](cache/balanced-crystalloids-vs-saline-mortality/records.json).
- **27749094 — Acute kidney injury**: typed refusal (`REFUSED_ON_EVIDENCE`). The study uses a cluster-randomized multiple-crossover design; held AACT supplies unadjusted AKI counts but no cluster-adjusted harm effect or design effect, so a binomial participant analysis would ignore the randomized unit. [Held source](cache/balanced-crystalloids-vs-saline-mortality/records.json).
- **27604335 — Acute kidney injury**: typed refusal (`REFUSED_ON_EVIDENCE`). The source reports only a P value for the AKI comparison, without per-arm counts or a ratio estimate and confidence interval. [Held source](cache/balanced-crystalloids-vs-saline-mortality/records.json).

### corticosteroids-covid19-mortality

- **34138478 — Serious adverse events**: extracted (counts). Direct serious-adverse-reaction fractions at day 28; matches the harm specification keywords and randomized hydrocortisone/placebo arms. [Held source](cache/corticosteroids-covid19-mortality/records.json).
- **32876697 — Serious adverse events**: typed refusal (`MULTI_ARM_UNRESOLVED`). The source reports separate fixed-dose and shock-dependent hydrocortisone arms against one control without a prespecified harm arm-selection or combination rule. [Held source](cache/corticosteroids-covid19-mortality/records.json).
- **32876689 — Serious adverse events**: typed refusal (`REFUSED_ON_EVIDENCE`). The source says no serious adverse events were related to treatment but does not provide per-arm all-SAE incidence or a serious-reaction result at the specified day 28. [Held source](cache/corticosteroids-covid19-mortality/records.json).
- **32876695 — Serious adverse events**: typed refusal (`REFUSED_ON_EVIDENCE`). The source reports other serious adverse events separately from secondary infections and insulin use, without a deduplicated total matching serious adverse reactions. [Held source](cache/corticosteroids-covid19-mortality/records.json).

### omega3-cardiovascular-events

- **30415628 — Atrial fibrillation**: typed refusal (`REFUSED_ON_EVIDENCE`). The source reports hospitalization for atrial fibrillation or flutter as percentages only; AACT serious preferred-term rows are narrower treated-population events and do not reconstruct that hospitalized composite. [Held source](cache/omega3-cardiovascular-events/records.json).
- **30415637 — Bleeding**: typed refusal (`REFUSED_ON_EVIDENCE`). The held text gives only a narrative bleeding comparison; AACT reports gastrointestinal bleeding and nosebleeds separately, without a deduplicated overall bleeding count. [Held source](cache/omega3-cardiovascular-events/records.json).
- **30415628 — Bleeding**: typed refusal (`REFUSED_ON_EVIDENCE`). The source reports serious bleeding percentages without event counts; AACT splits bleeding across potentially overlapping preferred terms, so their sum cannot establish patients with bleeding. [Held source](cache/omega3-cardiovascular-events/records.json).
- **30146932 — Bleeding**: spurious signal (`SIGNAL_SPURIOUS`). The signal is an exclusion in the vascular efficacy endpoint definition, not a bleeding result; the AACT major-bleed endpoint is explicitly for the aspirin comparison only. [Held source](cache/omega3-cardiovascular-events/records.json).

### semaglutide-obesity-weight

- **42070571 — Gastrointestinal adverse events**: typed refusal (`REFUSED_ON_EVIDENCE`). The source describes transient mild-to-moderate gastrointestinal effects without per-arm numbers or an effect and confidence interval. [Held source](cache/semaglutide-obesity-weight/records.json).
- **40825340 — Gastrointestinal adverse events**: typed refusal (`REFUSED_ON_EVIDENCE`). The source calls gastrointestinal events the most common adverse events but supplies no aggregate per-arm incidence; AACT individual symptom rows cannot be summed into unique patients. [Held source](cache/semaglutide-obesity-weight/records.json).
- **33625476 — Gastrointestinal adverse events**: typed refusal (`REFUSED_ON_EVIDENCE`). The source provides gastrointestinal-event percentages without numerators, while AACT reports individual symptoms and total event counts rather than deduplicated gastrointestinal patients. [Held source](cache/semaglutide-obesity-weight/records.json).
- **33567185 — Gastrointestinal adverse events**: typed refusal (`REFUSED_ON_EVIDENCE`). The source counts treatment discontinuations due to gastrointestinal events rather than all patients with gastrointestinal events; AACT individual symptom rows do not supply that aggregate. [Held source](cache/semaglutide-obesity-weight/records.json).

### spironolactone-hfref-mortality

- **10471456 — Hyperkalemia**: typed refusal (`REFUSED_ON_EVIDENCE`). The source describes serious hyperkalemia as minimal in both groups without arm counts or a reported effect and confidence interval. [Held source](cache/spironolactone-hfref-mortality/records.json).
- **21073363 — Hyperkalemia**: typed refusal (`REFUSED_ON_EVIDENCE`). The source gives potassium-threshold percentages only; AACT separates serious and nonserious investigator-coded hyperkalemia and hospitalization, which do not reconstruct the unique patients exceeding that laboratory threshold. [Held source](cache/spironolactone-hfref-mortality/records.json).
- **28824029 — Hyperkalemia**: typed refusal (`REFUSED_ON_EVIDENCE`). The source reports hyperkalemia narratively; AACT supplies nonserious coded hyperkalemia and hospitalization endpoints, without the overall laboratory-threshold count or a matching effect and confidence interval. [Held source](cache/spironolactone-hfref-mortality/records.json).
- **10471456 — Gynecomastia or breast pain**: typed refusal (`REFUSED_ON_EVIDENCE`). The source reports gynecomastia or breast pain percentages among men, without male-specific arm denominators or numerators. [Held source](cache/spironolactone-hfref-mortality/records.json).

### corticosteroids-cap-mortality

- **33446608 — Hyperglycaemia**: extracted (counts). Explicit randomized arm denominators and hyperglycaemia counts in the same results paragraph; no percentage inversion. [Held source](cache/corticosteroids-cap-mortality/records.json).
- **21636122 — Hyperglycaemia**: extracted (counts). Explicit per-arm patients with hyperglycaemia and denominators in the same sentence. [Held source](cache/corticosteroids-cap-mortality/records.json).
- **36942789 — Gastrointestinal bleeding**: typed refusal (`REFUSED_ON_EVIDENCE`). The source describes similar gastrointestinal bleeding frequencies without per-arm counts or an effect and confidence interval. [Held source](cache/corticosteroids-cap-mortality/records.json).

### esketamine-trd-madrs

- **37025256 — Adverse events**: extracted (counts). Table 4 reports patients with at least one treatment-emergent AE in the double-blind induction phase, not a sum of symptom events. [Held source](cache/esketamine-trd-madrs/ft_37025256.txt).
- **31109201 — Adverse events**: typed refusal (`REFUSED_ON_EVIDENCE`). The source lists common adverse events and discontinuation percentages, while AACT separates serious and other events without a deduplicated any-AE total for induction. [Held source](cache/esketamine-trd-madrs/records.json).

### metformin-pcos-ovulation

- **16769748 — Gastrointestinal adverse events**: spurious signal (`SIGNAL_SPURIOUS`). The source reports discontinuation because of side effects rather than gastrointestinal-specific adverse-event incidence. [Held source](cache/metformin-pcos-ovulation/records.json).
- **16769748 — Treatment discontinuation due to adverse events**: typed refusal (`EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH`). The source reports discontinuation percentages and a risk-difference interval, without exact discontinuation numerators or a ratio effect and confidence interval for the registered RR. [Held source](cache/metformin-pcos-ovulation/records.json).

### sglt2-ckd-progression

- **30990260 — Lower-limb amputation**: typed refusal (`REFUSED_ON_EVIDENCE`). The source reports no significant amputation difference without counts or a ratio interval, and the AACT amputation-stump-pain term is not an amputation endpoint. [Held source](cache/sglt2-ckd-progression/records.json).
- **36331190 — Lower-limb amputation**: extracted (effect+CI). Table 2 explicitly labels hazard ratios (95% CI) and reports lower limb amputation HR 1.43 (0.80-2.57); preserve the published HR rather than derive an RR. [Held source](cache/sglt2-ckd-progression/ft_36331190.txt).

### sglt2-hfref-hosp-cvdeath

- **31535829 — Volume depletion or hypotension**: typed refusal (`REFUSED_ON_EVIDENCE`). The source reports volume depletion narratively; AACT separates hypotension, orthostatic hypotension and dehydration in a treated safety population, without a deduplicated as-randomized composite. [Held source](cache/sglt2-hfref-hosp-cvdeath/records.json).
- **31535829 — Diabetic ketoacidosis**: typed refusal (`REFUSED_ON_EVIDENCE`). The abstract signal concerns volume depletion, renal dysfunction and hypoglycemia; AACT has separate diabetic-ketoacidosis and ketoacidosis preferred terms in treated patients, without a deduplicated as-randomized ketoacidosis total. [Held source](cache/sglt2-hfref-hosp-cvdeath/records.json).

### statins-primary-prevention-elderly

- **42670961 — Muscle symptoms/myopathy**: typed refusal (`REFUSED_ON_EVIDENCE`). The source describes musculoskeletal events within aggregate serious adverse events, without muscle-symptom or myopathy-specific counts or effect with confidence interval. [Held source](cache/statins-primary-prevention-elderly/records.json).
- **42670961 — New-onset diabetes**: typed refusal (`REFUSED_ON_EVIDENCE`). The source says diabetes-related adverse events were more common but does not provide new-onset diabetes counts or an effect with confidence interval. [Held source](cache/statins-primary-prevention-elderly/records.json).

### ticagrelor-vs-clopidogrel-acs

- **17980250 — Major bleeding**: typed refusal (`MULTI_ARM_UNRESOLVED`). The source reports Kaplan-Meier major-bleeding percentages for two ticagrelor doses and one clopidogrel arm, without harm event counts or a dose-specific ratio effect and confidence interval. [Held source](cache/ticagrelor-vs-clopidogrel-acs/records.json).
- **26376600 — Major bleeding**: extracted (effect+CI). PHILO 12-month major bleeding HR and 95% CI, not the adjacent primary efficacy HR 1.47; endpoint and treatment direction checked in held abstract. [Held source](cache/ticagrelor-vs-clopidogrel-acs/records.json).

### tranexamic-acid-pph

- **32143721 — Adverse events**: typed refusal (`REFUSED_ON_EVIDENCE`). The source reports similar side effects and acceptability without an adverse-event count or effect with confidence interval. [Held source](cache/tranexamic-acid-pph/records.json).
- **28456509 — Adverse events**: typed refusal (`REFUSED_ON_EVIDENCE`). The source reports no significant difference in adverse events including thromboembolism but gives no aggregate adverse-event counts or effect with confidence interval. [Held source](cache/tranexamic-acid-pph/records.json).

### denosumab-vertebral-fracture

- **19671655 — Serious infection**: typed refusal (`REFUSED_ON_EVIDENCE`). The source describes no increased infection risk but gives no serious-infection aggregate; AACT lists individual infection diagnoses which may overlap and cannot be summed into unique patients. [Held source](cache/denosumab-vertebral-fracture/records.json).

### semaglutide-obesity-mace

- **37952131 — Gastrointestinal adverse events**: spurious signal (`SIGNAL_SPURIOUS`). The signal counts all-cause adverse-event discontinuations rather than gastrointestinal events; AACT serious gastrointestinal diagnoses do not supply the deduplicated all-GI endpoint. [Held source](cache/semaglutide-obesity-mace/records.json).

