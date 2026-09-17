# Protocol - GLP-1 receptor agonists for 3-point MACE in type 2 diabetes

**Registration.** The commit that adds this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab.
Committed BEFORE the synthesis is run.

## PICO
- **P** - adults with type 2 diabetes.
- **I** - GLP-1 receptor agonist therapy (liraglutide, semaglutide, dulaglutide,
  albiglutide, efpeglenatide, exenatide, or lixisenatide) added to usual care.
- **C** - placebo added to usual care.
- **O (primary)** - 3-point major adverse cardiovascular events, defined as cardiovascular
  death, nonfatal myocardial infarction, or nonfatal stroke.
- **O (harms / secondary)** - gastrointestinal adverse events, discontinuation for adverse
  events, and any further harm outcome the resolved comparator reports.

## Estimand / population / timepoint
- **Estimand** - hazard ratio (HR), GLP-1 receptor agonist vs placebo.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - trial end / longest primary cardiovascular outcome follow-up.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** - randomised controlled trial;
- **I2** - population is adults with type 2 diabetes, judged from the title or registry
  conditions;
- **I3** - a GLP-1 receptor agonist vs placebo contrast;
- **design** - double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only);
- **X2** - wrong population (e.g. obesity without diabetes, type 1 diabetes, or gestational
  diabetes);
- **X3** - wrong intervention/comparison (no GLP-1 receptor agonist-vs-placebo contrast);
- **X-DESIGN** - not double-blind and placebo-controlled;
- **X5** - off-topic: a primary trial of another topic in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports 3-point MACE, or gives
> a 2x2 vs only an effect+CI, is recorded as target-result status at extraction - never as
> an exclusion. A published effect + 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/search.json; screening replays offline)
- PubMed: exact-title sweeps for the large GLP-1 receptor agonist cardiovascular outcome
  trials in type 2 diabetes (LEADER, SUSTAIN-6, REWIND, HARMONY Outcomes, AMPLITUDE-O,
  PIONEER-6, EXSCEL, and ELIXA).
- ClinicalTrials.gov: condition "type 2 diabetes cardiovascular", intervention
  "efpeglenatide".
- Fixed-screen note: several PubMed abstracts for verified double-blind CVOTs do not use
  the literal phrase "double-blind"; the config therefore does not require that literal
  abstract/title string, while the protocol eligibility criterion remains double-blind
  placebo-controlled design.

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(RR); **Paule-Mandel** tau^2; **HKSJ** 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. DerSimonian-Laird forbidden. Engine validated vs
metafor 5.0.1 (<1e-6). For this topic, the poolable input is the published HR + 95% CI
path on the same ratio/log scale; 2x2 extraction is available but is not required when a
trial reports an HR + CI.

## Comparator (resolved; open-access confirmed)
Giugliano et al., *Cardiovascular Diabetology* 2021, "GLP-1 receptor agonists and
cardiorenal outcomes in type 2 diabetes: an updated meta-analysis of eight CVOTs" (PMID
34526024, DOI 10.1186/s12933-021-01366-8; Unpaywall is_oa=true; PubMed Central
PMC8442438). It reports pooled MACE HR 0.86 (95% CI 0.79-0.94) over 8 cardiovascular
outcome trials.

## Controls
- **Positive** - the search must recover and include LEADER, SUSTAIN-6, and REWIND.
- **Negative** - SELECT (semaglutide, double-blind, placebo-controlled, but obesity without
  diabetes - another disease population) must be recovered and EXCLUDED by the population
  rule.

## Amendment 2026-09-16 (eligibility, estimand, effect measure, timepoint, screening, search, comparator, harms, RoB 2, GRADE -- "B-prime")
**Status: RETROSPECTIVE.** Registered under Mahmood's authority ("fix all in reproducible harness", 16 Sep 2026, via Dispatch) after an independent protocol audit of registration commit `4091958ce4af7f1ca9ed4c30e1021672b0c21223` found that the registered eligibility (a broad GLP-1 review; eligibility explicitly not on the outcome axis) and the registered search (exact-title sweeps for eight named cardiovascular outcome trials) define two different reviews. This amendment is appended before the page is rebuilt against it and does not rename the pinned slug/URL. **Both alternative answers were known when this rule was written**, and are disclosed below; that disclosure is the point of the RETROSPECTIVE label.

- **Question.** Among adults with type 2 diabetes, what is the effect of GLP-1 receptor agonist therapy versus placebo on time to first adjudicated 3-point MACE?
- **Eligibility (B-prime).** Parallel-group randomised, double-blind, placebo-controlled trials of the prespecified GLP-1 RAs (liraglutide, semaglutide, dulaglutide, albiglutide, efpeglenatide, exenatide, lixisenatide) in adults with type 2 diabetes **in which 3-point MACE, or its exact three components, was prospectively specified and systematically ascertained** -- preferably with blinded or independent adjudication. Eligibility does **not** depend on the direction, statistical significance or published availability of the MACE result. **If MACE was measured but the result is unavailable, the trial is retained and the result is pursued** through full text, registry results, regulatory documents or investigators, with an OPEN recovery obligation rendered until it is held.
- **Alternatives disclosed.** Under **A** (the literal registered rule: outcome not an eligibility axis) the universe would additionally include SUSTAIN-1, PIONEER-1, AWARD-8, LEAD-2, Harmony 1, AMPLITUDE-M, GetGoal-P, GetGoal-L, GetGoal-Mono, FREEDOM-1 and others, entering screening and exiting on outcome availability. Under **B** ("large cardiovascular outcome trials") the universe would be the eight seeded CVOTs, with "large" and "CVOT" undefined. B-prime yields the intended small universe by a stated, executable criterion (prospective systematic ascertainment of the outcome), not by a label or by which results are convenient. FLOW (semaglutide, T2D with CKD; MACE prospectively adjudicated) is eligible under B-prime; FREEDOM-CVO (ITCA 650) is eligible under B-prime on the intervention-class strand that admits continuous delivery (see the class-boundary decision: `CONVENTIONAL_GLP1RA` primary strand, `GLP1RA_ANY_DELIVERY` rendered alongside); ELIXA (lixisenatide; 4-point primary, 3-point components prospectively ascertained) is eligible, its 3-point result pursued from the primary supplement or regulatory record, never from a secondary meta-analysis.
- **Estimand.** Intention-to-treat effect of assignment to GLP-1 RA versus placebo on **time to first** occurrence of cardiovascular death, nonfatal myocardial infarction or nonfatal stroke during the prespecified randomised cardiovascular follow-up. Trial definitions that count **undetermined death as cardiovascular death** are accepted as each trial's prespecified adjudicated definition and recorded per trial in the compatibility key (`undetermined_death_counted_as_cv: yes/no/unstated`); no re-adjudication is attempted.
- **Effect measure.** The primary analysis pools **log-HRs only** (published, or validly reconstructed from a time-to-event analysis). Ordinary RRs, ORs and IRRs do not enter the primary pool. Where only fixed-time counts are recoverable, a separate RR sensitivity analysis is reported. (Supersedes the registered synthesis sentence "random-effects inverse-variance on log(RR)", which contradicted the registered HR estimand.)
- **Timepoint.** The trial's prespecified primary cardiovascular analysis **at the end of randomised, blinded follow-up**. Post-trial and extension follow-up are analysed separately and never substitute for the primary analysis.
- **Screening.** The **clinical eligibility rule** (above) is separate from the **machine screening heuristic**. Title and registry-condition term matching is a first-pass heuristic only; final eligibility is decided from abstract, then registry record, then full text/protocol as needed, on a canonical trial object (trial / arm / drug / dose / route / background therapy / population / timepoint / analysis set). A trial must not become ineligible because a term is absent from its title. Every screening decision carries the source span it rests on.
- **Search.** Independent concept search across all seven eligible agents in PubMed/MEDLINE and Europe PMC, **the Cochrane CENTRAL register** (free; carries Embase-derived records), ClinicalTrials.gov via the local AACT snapshot (queried symmetrically across agents, not only efpeglenatide), **WHO ICTRP** (non-US registries) and ISRCTN, plus citation chasing and the trial-family assembly of every report, registry record, supplement and regulatory document. **No trial-name seed list is the primary retrieval mechanism.** Every retrieved record carries `entered_via` (executed query / seeded identifier / manual addition) and the rejection trail (families retrieved and refused, each with a typed reason) is rendered.
- **Declared scope boundary (not a defect): no Embase.** This review does not search Embase. Its unique contribution over MEDLINE is mainly conference abstracts and European/pharma-journal reports; for large registered cardiovascular outcome trials -- this topic -- the marginal yield is low because every such trial is MEDLINE-indexed and registered, and CENTRAL + registries recover part of Embase's unique yield. The completeness claim is therefore for **registered trials**; Embase-equivalent coverage of conference and grey literature is not claimed. (For topics dominated by small or older trials the gap matters considerably more; each topic's protocol states which kind it is.)
- **Source hierarchy for every extracted value (recorded and rendered as `source_level`):** 1 the trial's own publication and supplement; 2 regulatory review (FDA, EMA) -- primary re-analysis of trial data; 3 registry results (ClinicalTrials.gov / AACT) -- sponsor-posted structured data; 4 HTA assessment (NICE); 5 older meta-analyses -- **pointers only, never the number itself** (several published reviews relabelled ELIXA's 4-point MACE as 3-point; a value found in a meta is traced to a level 1-4 source or refused). A label such as `PUBLISHED_UNADJUSTED` is assigned only after the estimator is read at the source.
- **Full-text reachability ladder.** Before `abstract only` may be recorded the extractor tries, in order: PMC / Europe PMC deposits; supplementary appendices (where exact secondary endpoints such as ELIXA's and FREEDOM-CVO's 3-point MACE live); publisher open-access versions; author accepted manuscripts in institutional repositories; regulatory documents (FDA, EMA); ClinicalTrials.gov / AACT results. The route that succeeded is recorded; `abstract only` is replaced by `full text not reachable after N named attempts`, listing them. An unreachability claim with no attempt log is the same defect as an absence claim with no negative citation.
- **Comparator.** The published comparator meta-analysis is resolved **only after the independent evidence search is locked**; published meta-analyses are used for reference checking, never for seeding. Parity compares the comparator's eligibility rules, not only its trial list.
- **Harms.** Gastrointestinal adverse events and discontinuation due to adverse events are prespecified harm outcomes. Any further harm outcome a resolved comparator happens to report is **exploratory**, not prespecified, and is labelled so.
- **Risk of bias.** Full outcome-specific RoB 2 on the primary result (effect of assignment): five domains, signalling questions, information sources (protocol, statistical analysis plan, registry record, primary publication and supplement), adjudication method (two assessors, disagreements recorded, not silently resolved), and a planned sensitivity analysis restricted to low-risk-of-bias trials. Registry-derived machine signals are rendered as `machine signal consistent with low risk; formal RoB 2 not assessed` until the sources above have been read; they are never rendered as RoB 2 judgements.
- **GRADE.** Prespecified across all five domains (risk of bias, inconsistency, imprecision, indirectness, publication bias). **No certainty category is issued while any domain is unassessed**; the page renders `GRADE provisional -- not yet fully assessable` instead. Imprecision reflects whether the confidence interval permits materially different clinical conclusions, not a mechanical significance test; a prediction interval approaching 1 is not by itself grounds for downgrading.
- **Pre-specified list (intervention agents).** liraglutide; semaglutide (subcutaneous and oral); dulaglutide; albiglutide; efpeglenatide; exenatide (immediate- and extended-release; ITCA 650 continuous subcutaneous delivery on the `GLP1RA_ANY_DELIVERY` strand); lixisenatide.
