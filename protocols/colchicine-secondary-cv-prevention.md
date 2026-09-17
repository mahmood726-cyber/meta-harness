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
