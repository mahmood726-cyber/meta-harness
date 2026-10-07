# Protocol - SGLT2 inhibitors for hospitalization for heart failure in type 2 diabetes or cardiovascular risk

**Registration.** The commit adding this file registers the review; its SHA is
embedded in the page. Committed before the synthesis runs. Eligibility is on
P/I/C/design only; outcome reporting affects extraction status, not screening.

## PICO
- **P** - adults with type 2 diabetes or cardiovascular risk enrolled in broad
  cardiovascular outcome trials, not trials whose entry criterion is HFrEF/HFpEF
  or chronic kidney disease.
- **I** - SGLT2 inhibitors, including empagliflozin, canagliflozin,
  dapagliflozin, and ertugliflozin.
- **C** - placebo.
- **O (primary)** - hospitalization for heart failure, using the trial-reported
  time-to-first-event effect for HHF.

## Estimand / population / timepoint
- **Estimand** - hazard ratio (HR), SGLT2 inhibitor vs placebo, pooled on the log
  ratio scale.
- **Population** - intention-to-treat as randomised / full analysis set, as
  reported by each cardiovascular outcome trial.
- **Timepoint** - trial end / longest trial-reported follow-up.

## Eligibility - P/I/C/DESIGN only
Include a record iff all hold:
- **I1** - randomised controlled trial;
- **I2** - population is adults with type 2 diabetes or cardiovascular risk in a
  broad cardiovascular outcome trial;
- **I3** - empagliflozin, canagliflozin, dapagliflozin, ertugliflozin, or SGLT2
  inhibitor as the randomised intervention;
- **I4** - placebo comparator;
- **design** - double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only, or
  meta-analysis);
- **X2** - wrong population, including heart failure with reduced or preserved
  ejection fraction as an entry criterion, chronic kidney disease / diabetic
  nephropathy as an entry criterion, type 1 diabetes, or no diabetes/CV-risk
  population;
- **X3** - wrong intervention/comparison, including active comparators;
- **X-DESIGN** - not double-blind and placebo-controlled;
- **X5** - off-topic: a primary trial of another topic in this set (negative
  control).

Eligibility is NOT on the outcome axis. Whether an eligible trial reports HHF,
and whether it reports arm counts or only an effect plus confidence interval, is
recorded at extraction. A published HR plus 95% CI is a poolable input; crude
event counts from CT.gov or labels are not substituted for HRs.

## Search
- PubMed: direct UID queries for EMPA-REG OUTCOME, CANVAS Program,
  DECLARE-TIMI 58, VERTIS CV, and an OA SGLT2 heart-failure-hospitalization
  meta-analysis comparator.
- ClinicalTrials.gov: condition "type 2 diabetes cardiovascular", intervention
  "SGLT2 inhibitor".
- Registry-first enumeration: condition "type 2 diabetes", intervention
  "SGLT2 inhibitor".

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log ratio; Paule-Mandel tau2; HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1,Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau2+se2)`. DerSimonian-Laird forbidden. Published HR
inputs are pooled on the log ratio scale.

## Comparator (resolved; OA confirmed)
Zhang et al., *Frontiers in Endocrinology* 2021, "Sodium Glucose Cotransporter 2
Inhibitors Reduce the Risk of Heart Failure Hospitalization in Patients With Type
2 Diabetes Mellitus: A Systematic Review and Meta-Analysis of Randomized
Controlled Trials" (PMID 33519713, PMCID PMC7843571, DOI
10.3389/fendo.2020.604250). Zelniker et al. 2019 (PMID 30424892) was considered
first for CVOT scope, but Unpaywall reported the article closed access.

## Pivotal
- **DECLARE-TIMI 58** - NCT01730534; positive-control PMID 30415602.

## Controls
- **Positive** - the search must recover and include DECLARE-TIMI 58 (PMID
  30415602).
- **Negative** - FIDELIO-DKD (finerenone in CKD and type 2 diabetes, PMID
  33264825) must be recovered and EXCLUDED as wrong intervention.

## Retrospective executable-screen amendment (2026-09-16)
`PROTOCOL_CONFIG_DIVERGENCE`: known-answer screening audit SC found that the
protocol's broad cardiovascular-outcome-trial scope was not executable. The config
now requires cardiovascular-outcome / cardiovascular-events / MACE wording, so
short glycaemic or imaging-marker diabetes trials are not included merely because
they are randomized SGLT2 placebo trials. This amendment changes screening only.

## Amendment 2026-10-05 -- identification sources (search+screen audit)

- **A1 REVIEW_REFERENCE_LIST (standing identification source).** Added: the comparator's (PMID 33519713) backward reference list (PubMed elink and Europe PMC) and its forward citations, and the backward reference lists of 2 other open meta-analyses (PMID 34336954, 33586910; rule: most trial rows read by the secondary-meta lane, ties to the newer). Rationale: the registered search identified 4 of 5 of the comparator's eligible trials; with this route and the full retrieval below, 5 of 5 (4 of 5 without the comparator's own reference list, which contains its trials by construction). The route retrieves 120 records (recorded: outputs/search_audit/rrl_probe.json). Identification only: every record still passes the registered screen.
- **A2 ClinicalTrials.gov retrieval.** The registered query {"cond": "type 2 diabetes cardiovascular", "intr": "SGLT2 inhibitor"} is unchanged. It returns 51 studies; the earlier retrieval kept the first 30 (a one-page cap in harness.fetch, now paginated with the source's own total recorded).
- **A3 Concept query: not adopted** (KEEP_CURRENT: volume 12649 > cap 5000; recorded call mc-e70a3e49041601de4b495b246a71423b.json).

## Amendment 2026-10-06 -- search volume cap raised to 10,000 (decision under Mahmood's delegation)

- **A5 Volume cap 10,000 (was 5,000) for this topic; concept query added** (union; none removed): `(("Diabetes Mellitus, Type 2"[Mesh] OR "Cardiovascular Diseases"[Mesh] OR "type 2 diabet*"[tiab] OR "type II diabet*"[tiab] OR T2DM[tiab] OR T2D[tiab] OR NIDDM[tiab] OR "noninsulin dependent diabet*"[tiab] OR "non insulin dependent diabet*"[tiab] OR "adult onset diabet*"[tiab] OR "cardiovascular disease*"[tiab] OR "cardiovascular risk*"[tiab] OR "cardiovascular outcome*"[tiab] OR "cardiovascular event*"[tiab] OR "cardiovascular safety"[tiab] OR "CV risk*"[tiab] OR "cardiometabolic risk*"[tiab] OR "coronary disease*"[tiab] OR "coronary artery disease*"[tiab] OR "coronary heart disease*"[tiab] OR "atherosclerotic disease*"[tiab] OR ASCVD[tiab] OR atherosclero*[tiab] OR CVOT*[tiab]) AND ("Sodium-Glucose Transporter 2 Inhibitors"[Majr] OR ((SGLT2[tiab] OR "SGLT-2"[tiab] OR "SGLT 2"[tiab] OR "SGLT1/2"[tiab] OR "SGLT-1/2"[tiab] OR "sodium glucose cotransporter 2"[tiab] OR "sodium glucose co-transporter 2"[tiab] OR "sodium glucose transporter 2"[tiab] OR "sodium glucose cotransporter type 2"[tiab] OR "sodium dependent glucose transporter 2"[tiab] OR "sodium glucose linked transporter 2"[tiab]) AND (inhibit*[tiab] OR block*[tiab] OR antagonis*[tiab])) OR gliflozin*[tiab] OR dapagliflozin[tiab] OR empagliflozin[tiab] OR canagliflozin[tiab] OR ertugliflozin[tiab] OR sotagliflozin[tiab] OR ipragliflozin[tiab] OR luseogliflozin[tiab] OR tofogliflozin[tiab] OR bexagliflozin[tiab] OR remogliflozin[tiab] OR sergliflozin[tiab] OR licogliflozin[tiab] OR henagliflozin[tiab] OR enavogliflozin[tiab] OR Farxiga[tiab] OR Forxiga[tiab] OR Jardiance[tiab] OR Invokana[tiab] OR Steglatro[tiab] OR Inpefa[tiab] OR Zynquista[tiab] OR Suglat[tiab] OR Lusefi[tiab] OR Apleway[tiab] OR Deberza[tiab] OR Brenzavvy[tiab] OR Enblo[tiab] OR Remo[tiab] OR Remozen[tiab] OR Xigduo[tiab] OR Synjardy[tiab] OR Invokamet[tiab] OR Vokanamet[tiab] OR Segluromet[tiab] OR Glyxambi[tiab] OR Qtern[tiab] OR Steglujan[tiab] OR Trijardy[tiab] OR Qternmet[tiab]) AND (randomized controlled trial[pt] OR controlled clinical trial[pt] OR randomized[ab] OR placebo[ab] OR "Clinical Trials as Topic"[Mesh:NoExp] OR randomly[ab] OR trial[ti])) NOT (animals[Mesh] NOT humans[Mesh])`. Decided 2026-10-06 by the captain under Mahmood's delegation. Reason: the blind query audit (query_audit_precise.json, recorded call mc-08d9ed028f7c7a7565a88e749f074db4.json) measured a recall gain on the comparator's eligible trials -- registered queries 4 of 5, with this query 5 of 5 -- at 5237 records, above the old 5,000 cap. Run in full on 2026-10-06: 5237 records, 5153 not already held; rule screen of the new records: {'include': 40, 'exclude': 4629, 'dedup_collapsed': 471, 'no_decision': 0}. Eligible comparator trials identified: 4 -> 5 of 5 (1 of the 1 newly identified pass the screen). Recorded: outputs/search_audit/expanded/sglt2-primary-prevention-hf.json.

## Amendment 2026-10-07 -- open search sources: OpenAlex and WHO ICTRP (additive)

- **A7 Open sources added** (decided 2026-10-07 by Mahmood: open sources only, no CENTRAL or Embase). (a) OpenAlex query (title_and_abstract.search; precise blind proposal, recorded call mc-9e6300c2a21f0756f87ecf53522a5039.json, written without sight of any comparator trial): `(diabetes OR diabetic OR T2D OR T2DM OR NIDDM OR cardiovascular OR atherosclerosis OR atherosclerotic OR "coronary artery disease" OR "coronary heart disease") AND (SGLT2 OR "SGLT-2" OR SGLT2i OR "SGLT-2i" OR "sodium glucose cotransporter 2" OR "sodium-glucose cotransporter-2" OR "sodium glucose co-transporter 2" OR "sodium glucose linked transporter 2" OR gliflozin OR empagliflozin OR dapagliflozin OR canagliflozin OR ertugliflozin OR sotagliflozin OR bexagliflozin OR ipragliflozin OR luseogliflozin OR tofogliflozin OR remogliflozin OR sergliflozin OR licogliflozin OR henagliflozin OR enavogliflozin OR janagliflozin OR Jardiance OR Farxiga OR Forxiga OR Invokana OR Steglatro OR Inpefa OR Zynquista OR Brenzavvy OR Suglat OR Lusefi OR Apleway OR Deberza) AND (randomized OR randomised OR randomly OR randomization OR randomisation OR trial) AND placebo AND ("double blind" OR "double-blind" OR "double blinded" OR "double-blinded" OR "double masking" OR "double masked" OR "double-masked")` -- 1349 records on 2026-10-07. Measured on the current comparator's eligible trials: OpenAlex alone 1 of 5, registered PubMed 5 of 5, together 5 of 5; no gain. Not adopted, over the 10,000 cap: round 1 15172 records. (b) **WHO ICTRP** (trial registrations): registered; run by its open route, a person's Search Portal CSV/XML export (or WHO's full-dataset request form) ingested by scripts/g1_open_sources.py --ictrp-export. Automated querying is not used: trialsearch.who.int/robots.txt disallows all agents and WHO's web/crawling services are for agreed partners. Not yet run.
