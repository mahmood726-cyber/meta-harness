# Override audit 2026-09-14

**Fix state (four-state rule): LANDED** - audit evidence, not a fix.

Recount: 23 override:true entries across 11 topics in cache/*/verified_effects.json and cache/*/verified_arms.json.
No row was judged a pure one-off fact: each numeric correction is trial-specific, but each override encodes a reusable harness rule candidate.

## Full table

| topic | file | trial | outcome | replaces | with | stated reason | source committed | judgement | module |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| colchicine-recurrent-pericarditis | verified_effects.json | 23992557 | Recurrent pericarditis | Candidate abstract composite: incessant or recurrent pericarditis, 20/120 vs 45/120. | Declared absent/refused for recurrence-specific outcome; source does not provide recurrence-only extraction. | ELIGIBLE under the registered broad PICO (population is pericarditis ? ACUTE first episode OR recurrent ? treated to prevent recurrence; the protocol was deliberately revised from a recurrent-only draft), so ICAP is NOT refused for population. It is not POO... | yes | General harness rule, not a one-off: composite containment and accessible-source absence should be enforced for any topic. | harness.extract; harness.compat; harness.absence |
| dpp4-mace-t2d | verified_effects.json | 26052984 | 3-point major adverse cardiovascular events | Abstract 4-point TECOS composite HR 0.98 (CV death, MI, stroke, or unstable-angina hospitalization). | Declared absent/refused for 3-point MACE because the 3-point value is not in the committed abstract. | declared absent (estimand mismatch): TECOS's abstract reports its primary as a FOUR-point composite (cardiovascular death, nonfatal myocardial infarction, nonfatal stroke, OR hospitalization for unstable angina), HR 0.98 (0.88-1.09). Our outcome is 3-point ... | yes | General harness rule: composite definitions must match before pooling; otherwise the trial is a refusal/absence state. | harness.compat; harness.extract; harness.absence |
| dpp4-mace-t2d | verified_effects.json | 30418475 | 3-point major adverse cardiovascular events | Extractor absence or failure to select CARMELINA's 3-point MACE primary HR. | Reported 3-point MACE HR 1.02 (95% CI 0.89-1.17). | PubMed abstract (PMID 30418475): During a median follow-up of 2.2 years, the primary outcome occurred in 434 of 3494 (12.4%) and 420 of 3485 (12.1%) in the linagliptin and placebo groups, respectively, (absolute incidence rate difference, 0.13 [95% CI, -0.6... | yes | General harness rule: endpoint-definition sentences and reported effect measures should be parsed across noninferiority abstracts. | harness.extract; harness.estmeasure |
| finerenone-ckd-t2d-renal | verified_effects.json | 33264825 | Kidney composite outcome | Count-derived RR about 0.84 from 504/2833 vs 600/2841. | Reported time-to-event HR 0.82 (95% CI 0.73-0.93). | FIDELIO-DKD (PMID 33264825) abstract: 'a primary outcome event occurred in 504 of 2833 patients (17.8%) in the finerenone group and 600 of 2841 patients (21.1%) in the placebo group (hazard ratio, 0.82; 95% confidence interval [CI], 0.73 to 0.93; P=0.001)'.... | yes | General harness rule: reported effect measure should control the pool scale; do not mix RR into HR pools. | harness.estmeasure; harness.compat; harness.pipeline |
| omega3-cardiovascular-events | verified_effects.json | 21115589 | Major vascular events / MACE | Abstract-path absence/factorial refusal for SU.FOL.OM3 omega-3 effect. | Full-text omega-3 marginal main-effect HR 1.08 (95% CI 0.79-1.47), collapsed over B-vitamin allocation. | SU.FOL.OM3 (PMID 21115589) full text (PMC2993045, Results / fig 4): 'Allocation to omega 3 fatty acids was not associated with any significant effect on major vascular events (81 v 76 patients, hazard ratio 1.08 (0.79 to 1.47), P=0.64; fig 4).' This is the ... | yes | General harness rule: factorial designs need factor binding, not blanket refusal when a target-factor marginal effect is available. | harness.extract; harness.unit_of_analysis; harness.fulltext |
| omega3-cardiovascular-events | verified_effects.json | 22686415 | Major vascular events / MACE | Wrong abstract primary endpoint: cardiovascular-death HR 0.98. | Target MACE/major vascular events HR 1.01 (95% CI 0.93-1.10). | ORIGIN (PMID 22686415) abstract: 'The use of n-3 fatty acids also had no significant effect on the rates of major vascular events (1034 patients [16.5%] vs. 1017 patients [16.3%]; hazard ratio, 1.01; 95% CI, 0.93 to 1.10; P=0.81)'. ENDPOINT CORRECTION (over... | yes | General harness rule: outcome identity beats generic primary-outcome wording. | harness.extract; harness.locate |
| omega3-cardiovascular-events | verified_effects.json | 23656645 | Major vascular events / MACE | Rischio e Prevenzione revised broad composite counts 733/6239 vs 745/6266. | Declared absent/refused for 3-point major vascular events. | declared absent (definition mismatch, cross-family definition audit): the stored 733/6239 vs 745/6266 is Rischio e Prevenzione's REVISED primary endpoint 'death from cardiovascular causes or admission to hospital for cardiovascular causes' (a broad CV-death... | yes | General harness rule: endpoint-definition drift within a trial must be represented as incompatibility, not pooled silently. | harness.compat; harness.absence |
| omega3-cardiovascular-events | verified_effects.json | 38184150 | Major vascular events / MACE | OMEGA-REMODEL idiosyncratic MACE HR 1.014 for a composite lacking stroke/CV-death. | Declared absent/refused for death/MI/stroke major vascular events. | declared absent (definition mismatch, cross-family definition audit): OMEGA-REMODEL's MACE is an idiosyncratic composite (all-cause death, heart-failure hospitalization, recurrent acute coronary syndrome, late CABG) with NO stroke and NO cardiovascular-deat... | yes | General harness rule: acronym-only endpoint matching is unsafe across topics. | harness.compat; harness.extract |
| probiotics-aad-prevention | verified_effects.json | 17356555 | Antibiotic-associated diarrhoea | Per-protocol/completer RR about 0.21 from 63 patients who completed according to protocol. | Declared absent/refused because randomized-denominator ITT AAD is not in the abstract. | declared absent (population mismatch, cross-family definition audit): the stored RR 0.21 is a PER-PROTOCOL analysis of the 63 patients who 'completed the study according to the protocol', not the 87 randomized (46 vs 41). An ITT/randomized-denominator AAD r... | yes | General harness rule: analysis set belongs in the compatibility key and refusal ontology. | harness.compat; harness.absence |
| probiotics-aad-prevention | verified_effects.json | 22472744 | Antibiotic-associated diarrhoea | Completer counts 16/106 vs 13/98 among 204 follow-up completers. | Declared absent/refused because ITT AAD among 275 randomized is not in the abstract. | declared absent (population mismatch, cross-family definition audit): the stored 16/106 vs 13/98 are the 204 patients who COMPLETED follow-up, not the 275 randomized (~26% excluded). An ITT/randomized-denominator AAD result is not in the abstract. Refuse ra... | yes | General harness rule: denominator provenance and analysis set should be checked before pooling. | harness.compat; harness.absence |
| probiotics-aad-prevention | verified_effects.json | 40488914 | Antibiotic-associated diarrhoea | 14-day AAD RR 0.47 selected from a multi-timepoint abstract. | Study-end 56-day AAD RR 0.46 (95% CI 0.30-0.69). | L. reuteri trial (PMID 40488914) abstract: primary endpoint AAD 'at 14 days (7.9% vs. 16.7%; RR: 0.47, 95%CI 0.30-0.7); at 21 days ... RR: 0.49; and at 56 days (9.1% vs. 19.6%; RR: 0.46, 95%CI 0.30-0.69)'. TIMEPOINT CORRECTION (override): the abstract extra... | yes | General harness rule: timepoint is a compatibility dimension and should not be left to first-match extraction. | harness.extract; harness.compat |
| sacubitril-valsartan-hfref | verified_effects.json | 25176015 | Composite cardiovascular death or heart-failure hospitalization | Count-derived RR about 0.823 from 914/4187 vs 1117/4212. | Reported time-to-event HR 0.80 (95% CI 0.73-0.87). | PARADIGM-HF (PMID 25176015) abstract: the primary composite of death from cardiovascular causes or hospitalization for heart failure occurred in 914 of 4187 (21.8%) LCZ696 vs 1117 of 4212 (26.5%) enalapril patients (hazard ratio in the LCZ696 group, 0.80; 9... | yes | General harness rule: structured counts corroborate but should not override the declared HR estimand. | harness.estmeasure; harness.compat; harness.ctgov_results |
| semaglutide-obesity-weight | verified_effects.json | 42575111 | Gastrointestinal adverse events | Overall adverse-event counts 141/161 vs 61/81 misfiled as gastrointestinal adverse events. | Declared absent/refused for GI-specific adverse events because no GI numerator/denominator is stated. | declared absent (override): the STEP-12 (China/Taiwan) abstract reports OVERALL adverse events ('Adverse events were reported in 141 [87.6%] of 161 ... and 61 [75.3%] of 81 ...'), with gastrointestinal disorders only named as the most common CATEGORY. It gi... | yes | General harness rule: specific harm outcomes need discriminating keywords and endpoint-specific numbers. | harness.extract; harness.absence |
| sglt2-ckd-progression | verified_effects.json | 32970396 | CKD progression / kidney composite outcome | Count-derived RR from 197/2152 vs 312/2152. | Reported kidney-composite HR 0.61 (95% CI 0.51-0.72). | DAPA-CKD (PMID 32970396) abstract: primary composite (sustained >=50% eGFR decline, ESKD, or renal/CV death) 197/2152 dapagliflozin vs 312/2152 placebo (hazard ratio, 0.61; 95% CI, 0.51 to 0.72; P<0.001). SCALE CORRECTION (override): the CT.gov/abstract cou... | yes | General harness rule: scale coherence should be automatic across HR-family kidney outcome pools. | harness.estmeasure; harness.compat |
| sglt2-ckd-progression | verified_effects.json | 36331190 | CKD progression / kidney composite outcome | Count-derived RR from EMPA-KIDNEY event counts. | Reported kidney-composite HR 0.72 (95% CI 0.64-0.82). | EMPA-KIDNEY (PMID 36331190) abstract: primary composite (kidney disease progression or CV death) in empagliflozin vs 558/3305 (16.9%) placebo (hazard ratio, 0.72; 95% CI, 0.64 to 0.82; P<0.001). SCALE CORRECTION (override): pool the reported kidney-composit... | yes | General harness rule: reported time-to-event scale must control the pooled estimand. | harness.estmeasure; harness.compat |
| sglt2-primary-prevention-hf | verified_effects.json | 26378978 | Hospitalization for heart failure | Absence or parent-trial extraction that did not expose hospitalized heart failure alone. | Committed full-text HHF HR 0.65 (95% CI 0.50-0.85). | cache/sglt2-primary-prevention-hf/pmc_26819227_fulltext.txt (PMID 26819227): As previously reported, hospitalization for heart failure occurred in a significantly lower percentage of patients treated with empagliflozin [126/4687 patients (2.7%)] than with p... | yes | General harness rule: secondary endpoint recovery should be source-backed, not trial-specific override data. | harness.pipeline; harness.fulltext; harness.extract |
| sglt2-primary-prevention-hf | verified_effects.json | 28605608 | Hospitalization for heart failure | Absence or composite CV-death/HHF source value for CANVAS. | Committed source-record hospitalized-HF-alone HR 0.67 (95% CI 0.52-0.87). | cache/sglt2-primary-prevention-hf/records.json hhf_source_records PMID 29526832 abstract: Overall, cardiovascular death or hospitalized HF was reduced in those treated with canagliflozin compared with placebo (16.3 versus 20.8 per 1000 patient-years; hazard... | yes | General harness rule: a linked outcome-specific source should not require an override when committed and identifiable. | harness.pipeline; harness.extract; harness.cites |
| sglt2-primary-prevention-hf | verified_effects.json | 30415602 | Hospitalization for heart failure | Composite or absence from DECLARE-TIMI 58 wording. | Hospitalization-for-heart-failure component HR 0.73 (95% CI 0.61-0.88). | cache/sglt2-primary-prevention-hf/records.json records PMID 30415602 abstract: which reflected a lower rate of hospitalization for heart failure (hazard ratio, 0.73; 95% CI, 0.61 to 0.88) | yes | General harness rule: component-vs-composite extraction should be label-bound within the sentence. | harness.extract; harness.compat |
| sglt2-primary-prevention-hf | verified_effects.json | 32966714 | Hospitalization for heart failure | Absence or broader VERTIS-CV source outcome. | First hospitalized-heart-failure HR 0.70 (95% CI 0.54-0.90). | cache/sglt2-primary-prevention-hf/records.json hhf_source_records PMID 33026243 abstract: Overall, ertugliflozin reduced risk for first HHF (HR, 0.70 [95% CI, 0.54-0.90]; P=0.006) | yes | General harness rule: target secondary endpoints need committed source-record plumbing, not one-off overrides. | harness.pipeline; harness.extract; harness.cites |
| esketamine-trd-madrs | verified_arms.json | NCT02417064 | Change in MADRS | CT.gov single-pair or refusal path for a 3-arm dose trial with shared placebo. | Combined esketamine arms: mean -18.91, SD 13.95, n=209 vs placebo mean -14.8, SD 15.07, n=108. | TRANSFORM-1 (NCT02417064) committed CT.gov MADRS Day-28 (MMRM) per-arm change scores: intranasal esketamine 56 mg + oral AD -19.0 (SD 13.86, n=111); 84 mg + oral AD -18.8 (SD 14.12, n=98); oral AD + intranasal placebo -14.8 (SD 15.07, n=108). MULTI-ARM COMB... | yes | General harness rule: RevMan-style multi-arm combination should be automated for any continuous multi-dose trial. | harness.ctgov_results; harness.unit_of_analysis |
| probiotics-aad-prevention | verified_arms.json | 15740542 | Antibiotic-associated diarrhoea | Any-diarrhoea counts 9/119 vs 29/127 or RR 0.3. | AAD-specific counts 4/119 vs 22/127. | Can 2006 (PMID 15740542) abstract: 'S. boulardii also reduced the risk of antibiotic-associated diarrhoea ... [four of 119 (3.4%) vs. 22 of 127 (17.3%), relative risk: 0.2; 95% confidence interval: 0.07-0.5]'. ENDPOINT CORRECTION (override): the abstract ex... | yes | General harness rule: target endpoint terms should bind counts more strongly than broader family terms. | harness.extract; harness.locate |
| probiotics-aad-prevention | verified_arms.json | 18026577 | Antibiotic-associated diarrhoea | Source OR 0.34 was selected into an RR-family count pool. | Per-arm AAD counts 7/44 vs 16/45, yielding count RR about 0.447. | Beausoleil 2007 (PMID 18026577) abstract: 'antibiotic-associated diarrhea occurred in seven of 44 patients (15.9%) in the lactobacilli group and in 16 of 45 patients (35.6%) in the placebo group (OR 0.34, 95% CI 0.125 to 0.944)'. SCALE CORRECTION (override)... | yes | General harness rule: OR and RR scales should not be mixed silently when arm counts permit the target scale. | harness.estmeasure; harness.armcontrast; harness.compat |
| spironolactone-hfref-mortality | verified_arms.json | 21073363 | Hyperkalemia | Synthesized hyperkalemia counts 161/1367 vs 99/1376 or wrong CT.gov hospitalization endpoint. | Declared absent/refused: abstract reports only percentages (11.8% vs 7.2%) and no verified denominators for serum K+ >5.5. | hyperkalemia (serum K+ >5.5) is reported in the EMPHASIS-HF abstract ONLY as percentages (11.8% eplerenone vs 7.2% placebo) with NO per-arm denominator, and the full text is not open-access; the CT.gov structured field is the WRONG endpoint (hospitalization... | yes | General harness rule: denominator and endpoint provenance must both validate before deriving counts from percentages. | harness.extract; harness.ctgov_results; harness.absence |

# General-rule candidates grouped

## Analysis-set compatibility

Harness module(s): harness.absence; harness.compat

- Completer denominators must not be silently substituted for randomized denominators.
- Observed-case or per-protocol effects must not be pooled as ITT/randomized-denominator effects.

Rows: probiotics-aad-prevention:verified_effects.json:17356555, probiotics-aad-prevention:verified_effects.json:22472744

## Component endpoint extraction

Harness module(s): harness.compat; harness.extract

- When a sentence explicitly reports the target component after a broader composite, the component effect should be extracted, not the composite.

Rows: sglt2-primary-prevention-hf:verified_effects.json:30415602

## Effect-measure and scale compatibility

Harness module(s): harness.armcontrast; harness.compat; harness.ctgov_results; harness.estmeasure; harness.pipeline

- A reported HR for a kidney-composite time-to-event endpoint beats a count-derived RR.
- For an HR-family outcome, a directly reported HR beats a count-derived RR from the same sentence.
- For time-to-event outcomes, directly reported HRs should not be replaced by event-count RRs.
- Use the reported HR when the target endpoint is analyzed as time to event.
- When an RR-family arm-count pool is required and counts are available, compute RR from counts rather than pooling a reported OR.

Rows: finerenone-ckd-t2d-renal:verified_effects.json:33264825, sacubitril-valsartan-hfref:verified_effects.json:25176015, sglt2-ckd-progression:verified_effects.json:32970396, sglt2-ckd-progression:verified_effects.json:36331190, probiotics-aad-prevention:verified_arms.json:18026577

## Endpoint identity and composite containment

Harness module(s): harness.absence; harness.compat; harness.extract

- A 4-point composite must not be pooled under a 3-point MACE label when the added component changes the endpoint.
- A composite that contains the target component must not be pooled as the target component unless the target component is separately reported.
- A label such as MACE is insufficient; component definitions must match the review endpoint.
- A revised broad composite cannot substitute for the originally named 3-point endpoint when the 3-point counts are absent.

Rows: colchicine-recurrent-pericarditis:verified_effects.json:23992557, dpp4-mace-t2d:verified_effects.json:26052984, omega3-cardiovascular-events:verified_effects.json:23656645, omega3-cardiovascular-events:verified_effects.json:38184150

## Endpoint identity and generic-harm guard

Harness module(s): harness.absence; harness.extract

- Generic any-adverse-event counts must not be pooled under a specific harm category without category-specific numerators.

Rows: semaglutide-obesity-weight:verified_effects.json:42575111

## Endpoint identity and generic-outcome guard

Harness module(s): harness.extract; harness.locate

- A broader any-diarrhoea endpoint must not be used for antibiotic-associated diarrhoea when AAD-specific counts are reported.

Rows: probiotics-aad-prevention:verified_arms.json:15740542

## Endpoint identity and primary-outcome selection

Harness module(s): harness.estmeasure; harness.extract; harness.locate

- Generic primary-outcome anchors must be disabled when the trial primary is not the review outcome and a separate target endpoint is reported.
- When a trial defines the target composite and reports its HR, the extractor should bind that endpoint even in noninferiority wording.

Rows: dpp4-mace-t2d:verified_effects.json:30418475, omega3-cardiovascular-events:verified_effects.json:22686415

## Factorial and unit-of-analysis handling

Harness module(s): harness.extract; harness.fulltext; harness.unit_of_analysis

- A 2x2 factorial trial may contribute the target factor's marginal main effect when the committed source explicitly reports that factor and endpoint.

Rows: omega3-cardiovascular-events:verified_effects.json:21115589

## Multi-arm unit-of-analysis handling

Harness module(s): harness.ctgov_results; harness.unit_of_analysis

- Multiple eligible dose arms sharing a comparator should be combined by the standard formula before pooling continuous outcomes.

Rows: esketamine-trd-madrs:verified_arms.json:NCT02417064

## Percentage-only and wrong-endpoint refusal

Harness module(s): harness.absence; harness.ctgov_results; harness.extract

- Percentages alone are insufficient for arm-count extraction unless denominators are source-backed and endpoint-matched; registry counts for a different endpoint must not fill the gap.

Rows: spironolactone-hfref-mortality:verified_arms.json:21073363

## Target secondary-outcome source recovery

Harness module(s): harness.cites; harness.extract; harness.fulltext; harness.pipeline

- Committed full-text/source records can supply a target secondary endpoint when trial binding and endpoint identity are explicit.
- Linked source records for a trial-specific secondary endpoint should be first-class extraction inputs with trial binding.
- Outcome-specific secondary publications/records linked to a parent trial should feed the extractor when the endpoint matches.

Rows: sglt2-primary-prevention-hf:verified_effects.json:26378978, sglt2-primary-prevention-hf:verified_effects.json:28605608, sglt2-primary-prevention-hf:verified_effects.json:32966714

## Timepoint compatibility

Harness module(s): harness.compat; harness.extract

- When multiple target-outcome timepoints are reported, choose the configured study-end/follow-up timepoint consistently or refuse.

Rows: probiotics-aad-prevention:verified_effects.json:40488914
