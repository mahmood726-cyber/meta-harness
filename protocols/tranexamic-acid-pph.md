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
