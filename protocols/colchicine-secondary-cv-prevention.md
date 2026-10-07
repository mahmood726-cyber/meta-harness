# Protocol - colchicine for secondary cardiovascular prevention

**Registration.** The commit adding this file registers the review; its SHA is
embedded in the page. Committed before the synthesis runs. This topic uses the
same fixed harness and declared method as the existing colchicine topics.

## PICO
- **P** - adults with coronary disease or recent myocardial infarction.
- **I** - low-dose colchicine added to guideline-based medical therapy.
- **C** - placebo added to guideline-based medical therapy.
- **O (primary)** - major adverse cardiovascular events (MACE) composite.
- **O (harms)** - gastrointestinal adverse effects; non-cardiovascular death.

## Estimand / population / timepoint
- **Estimand** - hazard ratio or other ratio effect as reported by each trial,
  pooled on the ratio scale by the fixed harness.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - trial end / longest planned follow-up for the primary MACE
  composite.

## Eligibility - on P/I/C/DESIGN only
Include a record iff **all** hold:
- **I1** - randomised controlled trial;
- **I2** - population is coronary disease or recent myocardial infarction;
- **I3** - low-dose colchicine versus placebo;
- **design** - double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only);
- **X2** - wrong population (e.g. pericarditis, postoperative atrial fibrillation,
  primary stroke-only populations, hypertension, COVID-19, osteoarthritis);
- **X3** - wrong intervention/comparison (no colchicine-vs-placebo contrast);
- **X-DESIGN** - not double-blind and placebo-controlled;
- **X5** - off-topic: a primary trial of another topic in this set (negative
  control).

Eligibility is NOT on the outcome axis. Whether an included trial reports MACE
in its abstract, gives 2x2 data, gives only an effect plus confidence interval,
or reports neither extractable form is extraction status only, never a screening
exclusion.

## Search
- PubMed: exact landmark-trial title queries for COLCOT and LoDoCo2, plus a
  colchicine x coronary disease x placebo x randomised/double-blind sweep.
- ClinicalTrials.gov: condition "coronary artery disease", intervention
  "colchicine".

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log ratio effects; Paule-Mandel tau^2; HKSJ
95% CI on t_{k-1} (floor max(1,Q/(k-1))); prediction interval mu +/- t_{k-1} *
sqrt(tau^2+se^2). 0.5 continuity correction to all four cells of a study only
if it has a zero cell. DerSimonian-Laird forbidden. Engine validated vs metafor
5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
Frontiers in Cardiovascular Medicine 2022, "Colchicine and coronary heart
disease risks: A meta-analysis of randomized controlled clinical trials" (PMID
36176989, PMC9512890, DOI 10.3389/fcvm.2022.947959; Unpaywall is_oa=true).
It reports colchicine reduced MACE (RR 0.65, 95% CI 0.38-0.77) in coronary
atherosclerotic heart disease trials, and reports gastrointestinal and mortality
safety outcomes.

## Controls
- **Positive** - the search must recover and include COLCOT (PMID 31733140) and
  LoDoCo2 (PMID 32865380).
- **Negative** - CORP recurrent pericarditis (PMID 21873705), a double-blind
  placebo colchicine trial from another topic/disease, must be recovered and
  excluded as the wrong population.

## Retrospective executable-screen amendment (2026-09-16)
`PROTOCOL_CONFIG_DIVERGENCE`: known-answer screening audit SC found that duplicate
secondary/economic analyses of already-pooled colchicine cardiovascular trials
were being treated as independent eligible trials. The config now excludes
cost-effectiveness / cost-utility analyses and secondary/subgroup analyses such as
LoDoCo2 prior-ACS subgroup reports. This amendment changes screening only; primary
trial reports remain eligible.

## Amendment 2026-10-05 -- identification sources (search+screen audit)

- **A1 REVIEW_REFERENCE_LIST (standing identification source).** Added: the comparator's (PMID 36176989) backward reference list (PubMed elink and Europe PMC) and its forward citations, and the backward reference lists of 2 other open meta-analyses (PMID 41517355, 39431112; rule: most trial rows read by the secondary-meta lane, ties to the newer). Rationale: the registered search identified 11 of 11 of the comparator's eligible trials; with this route and the full retrieval below, 11 of 11 (11 of 11 without the comparator's own reference list, which contains its trials by construction). The route retrieves 126 records (recorded: outputs/search_audit/rrl_probe.json). Identification only: every record still passes the registered screen.
- **A2 ClinicalTrials.gov retrieval.** The registered query {"cond": "coronary artery disease", "intr": "colchicine"} is unchanged. It returns 62 studies; the earlier retrieval kept the first 30 (a one-page cap in harness.fetch, now paginated with the source's own total recorded).
- **A3 Concept query added** (union with the registered queries; none removed): `("Coronary Disease"[Mesh] OR "Coronary Artery Disease"[Mesh] OR "Myocardial Ischemia"[Mesh] OR "Myocardial Infarction"[Mesh] OR "Acute Coronary Syndrome"[Mesh] OR "Angina Pectoris"[Mesh] OR "coronary disease*"[tiab] OR "coronary artery disease*"[tiab] OR "coronary heart disease*"[tiab] OR "coronary atherosclero*"[tiab] OR "coronary arteriosclero*"[tiab] OR "coronary syndrome*"[tiab] OR "ischemic heart disease*"[tiab] OR "ischaemic heart disease*"[tiab] OR "myocardial ischem*"[tiab] OR "myocardial ischaem*"[tiab] OR "myocardial infarct*"[tiab] OR "heart attack*"[tiab] OR angina[tiab] OR CAD[tiab] OR CHD[tiab] OR IHD[tiab] OR ACS[tiab] OR STEMI[tiab] OR NSTEMI[tiab]) AND ("Colchicine"[Mesh] OR colchicin*[tiab] OR Colcrys[tiab] OR Mitigare[tiab] OR Gloperba[tiab] OR Lodoco[tiab] OR Colgout[tiab] OR "microtubule inhibitor*"[tiab] OR "microtubule polymerization inhibitor*"[tiab] OR "microtubule polymerisation inhibitor*"[tiab] OR "microtubule assembly inhibitor*"[tiab] OR "tubulin inhibitor*"[tiab] OR "antimitotic agent*"[tiab] OR "anti-mitotic agent*"[tiab]) AND (randomized controlled trial[pt] OR controlled clinical trial[pt] OR randomized[tiab] OR randomised[tiab] OR placebo[tiab] OR drug therapy[sh] OR randomly[tiab] OR trial[tiab] OR groups[tiab]) NOT (animals[mh] NOT humans[mh])`. Proposed blind (the proposer saw the PICO and the current queries with their volumes, never the comparator's trials or our misses; recorded call mc-49bedaf50d0abf044bbc38b1ae6aeaa7.json); returns 585 records today; on the comparator's eligible trials the registered queries match 10 of 11 and the union 11 of 11. Limitation: the proposer may know well-known trials from training.
