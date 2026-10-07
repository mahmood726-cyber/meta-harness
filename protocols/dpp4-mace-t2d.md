# Protocol - DPP-4 inhibitors for 3-point MACE in type 2 diabetes

**Registration.** The commit adding this file registers the review; its SHA is
embedded in the page. Committed before the synthesis runs. Eligibility is on
P/I/C/design only; outcome reporting affects extraction status, not screening.

## PICO
- **P** - adults with type 2 diabetes.
- **I** - DPP-4 inhibitors, including sitagliptin, saxagliptin, alogliptin, and
  linagliptin.
- **C** - placebo.
- **O (primary)** - 3-point major adverse cardiovascular events, using the
  trial-reported cardiovascular death, myocardial infarction, or stroke composite.

## Estimand / population / timepoint
- **Estimand** - hazard ratio (HR), DPP-4 inhibitor vs placebo, pooled on the log
  ratio scale.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - trial end / longest trial-reported follow-up.

## Eligibility - P/I/C/DESIGN only
Include a record iff all hold:
- **I1** - randomised controlled trial;
- **I2** - population is adults with type 2 diabetes;
- **I3** - sitagliptin, saxagliptin, alogliptin, linagliptin, or a DPP-4 inhibitor
  as the randomised intervention;
- **I4** - placebo comparator;
- **design** - double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only, or
  meta-analysis);
- **X2** - wrong population, including type 1 diabetes;
- **X3** - wrong intervention/comparison, including active-comparator DPP-4 CVOTs
  such as CAROLINA;
- **X-DESIGN** - not double-blind and placebo-controlled;
- **X5** - off-topic: a primary trial of another topic in this set (negative control).

Eligibility is NOT on the outcome axis. Whether an eligible trial reports 3-point
MACE, and whether it reports arm counts or only an effect plus confidence interval,
is recorded at extraction. A published effect plus 95% CI is a poolable input.

## Search
- PubMed: direct UID queries for SAVOR-TIMI 53, EXAMINE, TECOS, CARMELINA, and
  CAROLINA primary reports, plus a DPP-4 cardiovascular-outcome-trial
  meta-analysis comparator.
- ClinicalTrials.gov: condition "type 2 diabetes", intervention "DPP-4 inhibitor".

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log ratio; Paule-Mandel tau2; HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1,Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau2+se2)`. DerSimonian-Laird forbidden. Published HR inputs
are pooled on the log ratio scale.

## Comparator (resolved; OA confirmed)
Patoulias et al., *World Journal of Cardiology* 2021, "Cardiovascular efficacy and
safety of dipeptidyl peptidase-4 inhibitors: A meta-analysis of cardiovascular
outcome trials" (PMID 34754403, PMC8554356, DOI 10.4330/wjc.v13.i10.585).

## Pivotal
- **TECOS** - NCT00790205; positive-control PMID 26052984.

## Controls
- **Positive** - the search must recover and include TECOS (PMID 26052984).
- **Negative** - DECLARE-TIMI 58 (dapagliflozin in type 2 diabetes, PMID 30415602)
  must be recovered and EXCLUDED as wrong intervention.

## Amendment 2026-10-05 -- identification sources (search+screen audit)

- **A1 REVIEW_REFERENCE_LIST (standing identification source).** Added: the comparator's (PMID 34754403) backward reference list (PubMed elink and Europe PMC) and its forward citations; no other open meta-analysis is held for this topic yet. Rationale: the registered search identified 5 of 5 of the comparator's eligible trials; with this route and the full retrieval below, 5 of 5 (5 of 5 without the comparator's own reference list, which contains its trials by construction). The route retrieves 87 records (recorded: outputs/search_audit/rrl_probe.json). Identification only: every record still passes the registered screen.
- **A2 ClinicalTrials.gov retrieval.** The registered query {"cond": "type 2 diabetes", "intr": "DPP-4 inhibitor"} is unchanged. It returns 244 studies; the earlier retrieval kept the first 30 (a one-page cap in harness.fetch, now paginated with the source's own total recorded).
- **A3 Concept query: not adopted** (KEEP_CURRENT: volume 6894 > cap 5000; recorded call mc-65afae791f805fc027209c42ab91327f.json).

## Amendment 2026-10-06 -- identification sources, query audit round 2 (search+screen audit)

- **A4 Concept query added, precision variant (over-cap topic, volume target, still blind)** (union; none removed): `("Diabetes Mellitus, Type 2"[Mesh] OR "type 2 diabetes"[tiab] OR "type II diabetes"[tiab] OR "type two diabetes"[tiab] OR "type 2 diabetic"[tiab] OR "type II diabetic"[tiab] OR T2D[tiab] OR T2DM[tiab] OR NIDDM[tiab] OR "noninsulin dependent diabetes"[tiab] OR "non insulin dependent diabetes"[tiab] OR "adult onset diabetes"[tiab]) AND ("Dipeptidyl-Peptidase IV Inhibitors"[Majr] OR (("DPP-4"[tiab] OR DPP4[tiab] OR "DPP-IV"[tiab] OR DPPIV[tiab] OR "dipeptidyl peptidase 4"[tiab] OR "dipeptidyl peptidase IV"[tiab] OR "dipeptidylpeptidase 4"[tiab] OR "dipeptidylpeptidase IV"[tiab]) AND (inhibit*[tiab] OR antagonist*[tiab] OR block*[tiab])) OR gliptin*[tiab] OR sitagliptin[tiab] OR saxagliptin[tiab] OR alogliptin[tiab] OR linagliptin[tiab] OR vildagliptin[tiab] OR teneligliptin[tiab] OR anagliptin[tiab] OR gemigliptin[tiab] OR evogliptin[tiab] OR omarigliptin[tiab] OR trelagliptin[tiab] OR gosogliptin[tiab] OR dutogliptin[tiab] OR retagliptin[tiab] OR denagliptin[tiab] OR melogliptin[tiab] OR besigliptin[tiab] OR carmegliptin[tiab] OR imigliptin[tiab] OR fotagliptin[tiab] OR cetagliptin[tiab] OR Januvia[tiab] OR Xelevia[tiab] OR Tesavel[tiab] OR Ristaben[tiab] OR Zituvio[tiab] OR Janumet[tiab] OR Velmetia[tiab] OR Ristfor[tiab] OR Zituvimet[tiab] OR Juvisync[tiab] OR Onglyza[tiab] OR Kombiglyze[tiab] OR Komboglyze[tiab] OR Qtern[tiab] OR Qternmet[tiab] OR Nesina[tiab] OR Vipidia[tiab] OR Kazano[tiab] OR Vipdomet[tiab] OR Oseni[tiab] OR Incresync[tiab] OR Tradjenta[tiab] OR Trajenta[tiab] OR Jentadueto[tiab] OR Glyxambi[tiab] OR Trijardy[tiab] OR Galvus[tiab] OR Eucreas[tiab] OR Jalra[tiab] OR Xiliarx[tiab] OR Zomelis[tiab] OR Equa[tiab] OR EquMet[tiab] OR Tenelia[tiab] OR Suiny[tiab] OR Zemiglo[tiab] OR Zemimet[tiab] OR Suganon[tiab] OR Marizev[tiab] OR Zafatek[tiab] OR Satereks[tiab]) AND ("randomized controlled trial"[pt] OR random*[tiab]) AND ("Placebos"[Mesh] OR placebo*[tiab]) NOT (animals[Mesh] NOT humans[Mesh])`. Proposed blind (recorded call mc-662e859cac65497a5bfadde9a4381806.json, model gpt-6-astra); returns 1000 records today; on the comparator's eligible trials the queries registered after the 2026-10-05 amendment match 4 of 5 and with this query 5 of 5. Limitation: the proposer may know well-known trials from training.
