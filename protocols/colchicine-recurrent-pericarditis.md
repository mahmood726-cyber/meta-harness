# Protocol — colchicine for prevention of pericarditis recurrence

**Registration.** The commit that adds/updates this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab.
Committed BEFORE the synthesis is run. (Revised from the initial recurrent-only draft
to match the scope of the resolved open-access comparator and to put eligibility on
P/I/C/**design** only — see below.)

## PICO
- **P** — patients with pericarditis (acute first episode or recurrent) treated to prevent recurrence.
- **I** — colchicine added to conventional anti-inflammatory therapy.
- **C** — placebo added to conventional therapy.
- **O (primary)** — recurrent pericarditis during follow-up.
- **O (harms / secondary)** — adverse events, treatment discontinuation, and any further
  outcome the resolved comparator reports.

## Estimand / population / timepoint
- **Estimand** — risk ratio (RR), colchicine vs placebo.
- **Population** — intention-to-treat as randomised.
- **Timepoint** — longest recurrence follow-up each trial reports.

## Eligibility — on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** — randomised controlled trial;
- **I2** — population is pericarditis (acute or recurrent), treated to prevent recurrence;
- **I3** — colchicine vs placebo, both added to conventional therapy;
- **design** — double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** — not an RCT (review, guideline, observational, protocol-only);
- **X2** — wrong population (e.g. postpericardiotomy-syndrome prophylaxis);
- **X3** — wrong intervention/comparison (no colchicine-vs-placebo contrast);
- **X-DESIGN** — not double-blind and placebo-controlled (e.g. open-label);
- **X5** — off-topic: a primary trial of another topic in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports the recurrence
> outcome, or gives a 2×2 vs only an effect+CI, is recorded as *target-result status* at
> extraction — never as an exclusion. A published effect + 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/search.json; screening replays offline)
- PubMed: colchicine × pericarditis × (recurrent OR trial); plus meta-analysis sweeps to resolve the comparator.
- ClinicalTrials.gov: condition "recurrent pericarditis", intervention "colchicine".

## Synthesis method (DECLARED; served method must equal this — gate limb 1)
Random-effects inverse-variance on log(RR); **Paule-Mandel** τ²; **HKSJ** 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`μ ± t_{k-1}·√(τ²+se²)`. 0.5 continuity correction to all four cells of a study only if
it has a zero cell. DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
Imazio et al., *Heart* 2012, "Efficacy and safety of colchicine for pericarditis
prevention" (PMID 22442198, DOI 10.1136/heartjnl-2011-301306; Unpaywall is_oa=true). It
reports pooled recurrence RR 0.40 (0.30–0.54) over 5 controlled trials plus adverse
events and drug-withdrawal. Trial-set overlap is stated on the page.

## Controls
- **Positive** — the search must recover the canonical double-blind colchicine-vs-placebo
  pericarditis RCTs (CORP, CORP-2, ICAP).
- **Negative** — COLCOT (colchicine, double-blind, placebo-controlled, but post-MI coronary
  disease — another topic in this set) must be recovered and EXCLUDED (X5).
