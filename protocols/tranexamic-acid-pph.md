# Protocol - tranexamic acid for postpartum haemorrhage

**Registration.** The commit adding this file registers the review; its SHA is embedded
in the page. Committed before the synthesis runs.

## PICO
- **P** - women with a clinical diagnosis of postpartum haemorrhage after vaginal birth
  or caesarean section.
- **I** - tranexamic acid added to usual care.
- **C** - matching placebo added to usual care.
- **O (primary)** - death due to bleeding.
- **O (harms)** - thromboembolic events and adverse events.

## Estimand / population / timepoint
- **Estimand** - risk ratio (RR), tranexamic acid vs placebo.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - in hospital.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff all hold:
- **I1** - randomised controlled trial;
- **I2** - population is established postpartum haemorrhage, judged from the title or
  registry conditions;
- **I3** - tranexamic acid vs placebo, both added to usual care;
- **design** - double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only);
- **X2** - wrong population (e.g. prophylaxis/prevention at delivery before postpartum
  haemorrhage, placenta previa prophylaxis, trauma, gastrointestinal bleeding);
- **X3** - wrong intervention/comparison (no tranexamic-acid-vs-placebo contrast);
- **X-DESIGN** - not double-blind and placebo-controlled (e.g. open-label);
- **X5** - off-topic: a primary trial of another topic in this set (negative control).

Eligibility is NOT on the outcome axis. Whether a trial reports death due to bleeding,
or gives arm counts versus only an effect plus CI, is recorded as target-result status
at extraction and is never an exclusion. A published effect plus 95% CI is a poolable
input.

## Search (fetch-once; raw results committed under cache/<slug>/records.json; screening replays offline)
- PubMed: tranexamic acid x postpartum haemorrhage/hemorrhage x WOMAN/death/trial terms,
  plus oral treatment/placebo and TRACES sweeps for recall.
- ClinicalTrials.gov: condition "postpartum hemorrhage", intervention "tranexamic acid".

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log(RR); Paule-Mandel tau^2; HKSJ 95% CI on t_{k-1}
(floor max(1,Q/(k-1))); prediction interval mu +/- t_{k-1}*sqrt(tau^2+se^2).
DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
The 2024 Lancet individual-patient-data systematic review and meta-analysis
"Tranexamic acid for postpartum bleeding: a systematic review and individual patient
data meta-analysis of randomised controlled trials" (PMID 39461793, PMC12197804, DOI
10.1016/S0140-6736(24)02102-0; Unpaywall is_oa=true). It reports the comparator primary
effect for life-threatening postpartum bleeding as pooled OR 0.77 (95% CI 0.63-0.93)
and thromboembolic events as pooled OR 0.96 (95% CI 0.65-1.41).

## Controls
- **Positive** - the search must recover and include WOMAN (PMID 28456509), oral TXA
  adjunct treatment for PPH (PMID 32143721), and TRACES haemorrhagic caesarean dose
  ranging (PMID 36243576).
- **Negative** - HALT-IT (tranexamic acid for acute gastrointestinal bleeding, PMID
  32563378 - another disease area) must be recovered and EXCLUDED as the wrong
  population.

## Amendment 2026-10-07 (D10 multi-outcome: outcomes the comparator also reports)
**Status: registered BEFORE any extraction of these outcomes; retrospective with respect to the trial pool**
(the pool, search and eligibility were fixed before D10 and are unchanged). Decision: Mahmood D10 (relayed
2026-10-07): add outcomes the comparator meta also reports -- all-cause mortality, key harms and its
prespecified secondaries. Rule `registry/outcome_amendments/D10_rule.json` (commit a40e00850); proposal
`registry/outcome_amendments/tranexamic-acid-pph.proposal.json` (commit 10878e620). The outcomes were chosen from the
comparator's (PMID 39461793) own text by that rule alone; no trial-level result for them
was extracted or viewed by this lane before this amendment.

- **New secondary outcome: Death within 24 h** (P1_ALL_CAUSE_MORTALITY). Estimand OR; timepoint within 24 h;
  keywords death within 24 h, all-cause mortality, all-cause death, death from any cause, deaths from any cause, any-cause death, any-cause mortality, total mortality, overall mortality. The comparator prints Pooled OR 0·76
  (0·62 to 0·94): "Death within 24 h | WOMAN, 1 WOMAN-2, 10 TRAAP, 11 TRAAP-2, 12 and TXA-MFMU 13 | 159/27 308 | 206/27 096 | 0·76 (0·62–0·94)" [R2 CC_FULL_TEXT].
- **New harm outcome: Myocardial infarction** (P2_KEY_HARMS). Estimand OR; timepoint trial-reported follow-up;
  keywords myocardial infarction. The comparator prints Pooled OR 1·33
  (0·30 to 5·92): "Myocardial infarction | WOMAN, 1 WOMAN-2, 10 TRAAP, 11 TRAAP-2, 12 and TXA-MFMU 13 | 4/27 025 | 3/26 848 | 1·33 (0·30–5·92)" [R2 CC_FULL_TEXT].
- **New harm outcome: Stroke** (P2_KEY_HARMS). Estimand OR; timepoint trial-reported follow-up;
  keywords stroke. The comparator prints Pooled OR 1·66
  (0·60 to 4·56): "Stroke | WOMAN, 1 WOMAN-2, 10 TRAAP, 11 TRAAP-2, 12 and TXA-MFMU 13 | 10/27 025 | 6/26 848 | 1·66 (0·60–4·56)" [R2 CC_FULL_TEXT].
- **New harm outcome: Sepsis** (P2_KEY_HARMS). Estimand OR; timepoint trial-reported follow-up;
  keywords sepsis. The comparator prints Pooled OR 1·01
  (0·83 to 1·23): "Sepsis | WOMAN, 1 WOMAN-2, 10 TRAAP-2, 12 and TXA-MFMU 13 | 205/25 185 | 202/25 000 | 1·01 (0·83–1·23)" [R2 CC_FULL_TEXT].
- **New harm outcome: Seizures** (P2_KEY_HARMS). Estimand OR; timepoint trial-reported follow-up;
  keywords seizures. The comparator prints Pooled OR 0·97
  (0·65 to 1·46): "Seizures | WOMAN, 1 WOMAN-2, 10 TRAAP, 11 TRAAP-2, 12 and TXA-MFMU 13 | 46/26 570 | 47/26 371 | 0·97 (0·65–1·46)" [R2 CC_FULL_TEXT].
- **Linked, already registered: Thromboembolic events** -- compared with the comparator's "fatal or non-fatal thromboembolic events",
  pooled OR 0·96 (0·65 to 1·41). No change to its spec.
- **Linked, already registered: Thromboembolic events** -- compared with the comparator's "Deep vein thrombosis",
  Pooled OR 0·92 (0·40 to 2·08). No change to its spec.
- **Linked, already registered: Thromboembolic events** -- compared with the comparator's "Pulmonary embolism",
  Pooled OR 0·81 (0·42 to 1·53). No change to its spec.
- **Extraction.** The served ladder is unchanged (abstract, CT.gov results, held open full texts, verified
  inputs); trials it leaves without a value may be read by recorded codex over open sources only (CC BY / CC0
  full text, abstracts, AACT, FDA, EMA with acknowledgement, NICE OGL/CC), every value quote-gated.
- **Comparison.** Each outcome's pooled result is compared with the comparator's printed result on the
  comparator's measure; a measure difference is reported, never converted. Nothing is served until
  Mahmood signs its notice.
