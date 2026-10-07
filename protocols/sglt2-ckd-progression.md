# Protocol - SGLT2 inhibitors for CKD progression in chronic kidney disease

**Registration.** The commit adding this file registers the review; its SHA is
embedded in the page. Committed before the synthesis runs. Eligibility is on
P/I/C/design only; outcome reporting affects extraction status, not screening.

## PICO
- **P** - adults with chronic kidney disease, including diabetic nephropathy terminology.
- **I** - an SGLT2 inhibitor, specifically dapagliflozin, canagliflozin, or
  empagliflozin, added to background standard care.
- **C** - placebo added to background standard care.
- **O (primary)** - CKD progression / kidney composite outcome, using the
  trial-reported composite definition.
- **O (harms)** - diabetic ketoacidosis and lower-limb amputation.

## Estimand / population / timepoint
- **Estimand** - hazard ratio (HR), SGLT2 inhibitor vs placebo, pooled on the log
  ratio scale when trial-reported HRs are extractable; percentage-corroborated arm
  counts are accepted by the harness as poolable ratio inputs when the abstract
  presents them.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - trial end / longest trial-reported follow-up.

## Eligibility - P/I/C/DESIGN only
Include a record iff all hold:
- **I1** - randomised controlled trial;
- **I2** - adult chronic kidney disease / kidney disease / diabetic nephropathy
  population, judged from title or registry conditions;
- **I3** - dapagliflozin, canagliflozin, or empagliflozin versus placebo;
- **design** - double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only, or
  meta-analysis);
- **X2** - wrong population (for example heart failure, myocardial infarction,
  pericarditis, atrial fibrillation, or another non-CKD population);
- **X3** - wrong intervention/comparison (no eligible SGLT2-inhibitor-vs-placebo
  contrast);
- **X-DESIGN** - not double-blind and placebo-controlled in the machine-readable
  record;
- **X5** - off-topic: a primary trial of another topic in this set (negative
  control).

Eligibility is NOT on the outcome axis. Whether an eligible trial reports CKD
progression, and whether it reports arm counts or only an effect plus confidence
interval, is recorded at extraction. A published effect plus 95% CI is a poolable
input.

## Search
- PubMed: UID-anchored queries for the DAPA-CKD, CREDENCE, and EMPA-KIDNEY
  primary reports, plus the resolved open-access comparator.
- ClinicalTrials.gov: condition "chronic kidney disease", intervention "SGLT2
  inhibitor".

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log ratio; Paule-Mandel tau2; HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1,Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau2+se2)`. DerSimonian-Laird forbidden. Engine validated vs
metafor 5.0.1 for the binary RR path; published HR inputs are pooled on the same
log ratio scale.

## Comparator (resolved; OA confirmed)
The SMART-C collaborative meta-analysis in *JAMA* 2026, "SGLT2 Inhibitors and Kidney
Outcomes by Glomerular Filtration Rate and Albuminuria: A Meta-Analysis" (PMID
41203232, PMC12595549, DOI 10.1001/jama.2025.20834; Unpaywall is_oa=true). It reports
CKD progression HR 0.62 (95% CI 0.57-0.68) across 10 randomized trials.

## Controls
- **Positive** - the search must recover the landmark CKD SGLT2 inhibitor trials:
  DAPA-CKD (PMID 32970396), CREDENCE (PMID 30990260), and EMPA-KIDNEY (PMID
  36331190).
- **Negative** - DAPA-HF (dapagliflozin, placebo-controlled, but HFrEF rather than
  CKD; PMID 31535829) must be recovered and EXCLUDED as wrong population.

## Retrospective executable-screen amendment (2026-09-16)
`PROTOCOL_CONFIG_DIVERGENCE`: known-answer screening audit SC found one vocabulary
miss and one sparse-registry comparator miss. The executable population terms now
recognize plural "Chronic Kidney Diseases"; DIAMOND NCT03190694 is source-backed
as eligible for P/I/C/design despite the committed registry intervention list
omitting the placebo/crossover comparator label. This amendment changes screening
only; short duration, proteinuria/mGFR, or outcome incompatibility remains an
extraction/compatibility question, not a screening exclusion.

## Amendment 2026-10-05 -- identification sources (search+screen audit)

- **A1 REVIEW_REFERENCE_LIST (standing identification source).** Added: the comparator's (PMID 41203232) backward reference list (PubMed elink and Europe PMC) and its forward citations, and the backward reference lists of 2 other open meta-analyses (PMID 38238025, 34336954; rule: most trial rows read by the secondary-meta lane, ties to the newer). Rationale: the registered search identified 3 of 6 of the comparator's eligible trials; with this route and the full retrieval below, 6 of 6 (6 of 6 without the comparator's own reference list, which contains its trials by construction). The route retrieves 194 records (recorded: outputs/search_audit/rrl_probe.json). Identification only: every record still passes the registered screen.
- **A2 ClinicalTrials.gov retrieval.** The registered query {"cond": "chronic kidney disease", "intr": "SGLT2 inhibitor"} is unchanged. It returns 55 studies; the earlier retrieval kept the first 30 (a one-page cap in harness.fetch, now paginated with the source's own total recorded).
- **A3 Concept query added** (union with the registered queries; none removed): `("Renal Insufficiency, Chronic"[Mesh] OR "Kidney Failure, Chronic"[Mesh] OR "Diabetic Nephropathies"[Mesh] OR "chronic kidney disease*"[tiab] OR "chronic renal disease*"[tiab] OR "chronic kidney insufficien*"[tiab] OR "chronic renal insufficien*"[tiab] OR "chronic kidney failure"[tiab] OR "chronic renal failure"[tiab] OR "chronic kidney impair*"[tiab] OR "chronic renal impair*"[tiab] OR "chronic kidney dysfunction"[tiab] OR "chronic renal dysfunction"[tiab] OR CKD[tiab] OR "diabetic kidney disease*"[tiab] OR "diabetic nephropath*"[tiab] OR "diabetic renal disease*"[tiab] OR "end stage kidney disease*"[tiab] OR "end stage renal disease*"[tiab] OR ESKD[tiab] OR ESRD[tiab]) AND ("Sodium-Glucose Transporter 2 Inhibitors"[Mesh] OR SGLT2[tiab] OR "SGLT-2"[tiab] OR "SGLT 2"[tiab] OR "SGLT2i"[tiab] OR "SGLT2is"[tiab] OR "sodium glucose cotransporter 2"[tiab] OR "sodium glucose co-transporter 2"[tiab] OR "sodium glucose transporter 2"[tiab] OR "sodium glucose cotransport* inhibit*"[tiab] OR "sodium glucose co-transport* inhibit*"[tiab] OR "sodium dependent glucose transporter 2"[tiab] OR "SGLT1/2"[tiab] OR "SGLT-1/2"[tiab] OR gliflozin*[tiab] OR dapagliflozin[tiab] OR Farxiga[tiab] OR Forxiga[tiab] OR empagliflozin[tiab] OR Jardiance[tiab] OR canagliflozin[tiab] OR Invokana[tiab] OR ertugliflozin[tiab] OR Steglatro[tiab] OR ipragliflozin[tiab] OR Suglat[tiab] OR luseogliflozin[tiab] OR Lusefi[tiab] OR tofogliflozin[tiab] OR Apleway[tiab] OR Deberza[tiab] OR remogliflozin[tiab] OR bexagliflozin[tiab] OR Brenzavvy[tiab] OR sotagliflozin[tiab] OR Inpefa[tiab] OR Zynquista[tiab] OR licogliflozin[tiab] OR sergliflozin[tiab] OR enavogliflozin[tiab] OR Envlo[tiab] OR Xigduo[tiab] OR Synjardy[tiab] OR Glyxambi[tiab] OR Qtern[tiab] OR Invokamet[tiab] OR Vokanamet[tiab] OR Steglujan[tiab] OR Segluromet[tiab] OR Trijardy[tiab]) AND (randomized controlled trial[pt] OR controlled clinical trial[pt] OR randomized[tiab] OR randomised[tiab] OR placebo[tiab] OR drug therapy[sh] OR randomly[tiab] OR trial[tiab] OR groups[tiab]) NOT (animals[Mesh] NOT humans[Mesh])`. Proposed blind (the proposer saw the PICO and the current queries with their volumes, never the comparator's trials or our misses; recorded call mc-bc0f65e11e03110bd2635dd3f306c403.json); returns 3242 records today; on the comparator's eligible trials the registered queries match 3 of 6 and the union 4 of 6. Limitation: the proposer may know well-known trials from training.

## Amendment 2026-10-06 -- identification sources, query audit round 2 (search+screen audit)

- **A4 Concept query added, round 2 (independent blind proposer)** (union; none removed): `(("Renal Insufficiency, Chronic"[Mesh] OR "Kidney Failure, Chronic"[Mesh] OR "Kidney Diseases"[Mesh] OR "chronic kidney disease"[tiab] OR "chronic kidney diseases"[tiab] OR CKD[tiab] OR "chronic renal disease"[tiab] OR "chronic renal diseases"[tiab] OR "chronic renal insufficiency"[tiab] OR "chronic kidney insufficiency"[tiab] OR "chronic renal failure"[tiab] OR "chronic kidney failure"[tiab] OR "chronic renal impairment"[tiab] OR "chronic kidney impairment"[tiab] OR "diabetic kidney disease"[tiab] OR "diabetic kidney diseases"[tiab] OR "diabetic nephropathy"[tiab] OR "diabetic nephropathies"[tiab]) AND ("Sodium-Glucose Transporter 2 Inhibitors"[Mesh] OR "sodium glucose cotransporter 2 inhibitor"[tiab] OR "sodium glucose cotransporter 2 inhibitors"[tiab] OR "sodium-glucose cotransporter 2 inhibitor"[tiab] OR "sodium-glucose cotransporter 2 inhibitors"[tiab] OR "sodium glucose co-transporter 2 inhibitor"[tiab] OR "sodium glucose co-transporter 2 inhibitors"[tiab] OR "sodium-glucose co-transporter 2 inhibitor"[tiab] OR "sodium-glucose co-transporter 2 inhibitors"[tiab] OR "sodium glucose transporter 2 inhibitor"[tiab] OR "sodium glucose transporter 2 inhibitors"[tiab] OR "SGLT2 inhibitor"[tiab] OR "SGLT2 inhibitors"[tiab] OR "SGLT 2 inhibitor"[tiab] OR "SGLT 2 inhibitors"[tiab] OR "SGLT-2 inhibitor"[tiab] OR "SGLT-2 inhibitors"[tiab] OR gliflozin*[tiab] OR dapagliflozin[tiab] OR Farxiga[tiab] OR Forxiga[tiab] OR empagliflozin[tiab] OR Jardiance[tiab] OR canagliflozin[tiab] OR Invokana[tiab] OR ertugliflozin[tiab] OR Steglatro[tiab] OR sotagliflozin[tiab] OR Inpefa[tiab] OR Zynquista[tiab] OR bexagliflozin[tiab] OR Brenzavvy[tiab] OR ipragliflozin[tiab] OR Suglat[tiab] OR tofogliflozin[tiab] OR Apleway[tiab] OR Deberza[tiab] OR luseogliflozin[tiab] OR Lusefi[tiab] OR remogliflozin[tiab] OR "remogliflozin etabonate"[tiab])) AND ((randomized controlled trial[pt] OR controlled clinical trial[pt] OR randomized[tiab] OR randomised[tiab] OR placebo[tiab] OR drug therapy[sh] OR randomly[tiab] OR trial[tiab] OR groups[tiab]) NOT (animals[mh] NOT humans[mh]))`. Proposed blind (recorded call mc-d82607f217f4f51e0ac067399c18155c.json, model gpt-5.5); returns 3439 records today; on the comparator's eligible trials the queries registered after the 2026-10-05 amendment match 4 of 6 and with this query 5 of 6. Limitation: the proposer may know well-known trials from training.
