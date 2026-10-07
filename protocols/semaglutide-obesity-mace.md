# Protocol - semaglutide for 3-point MACE in obesity without diabetes

**Registration.** The commit that adds this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab.
Committed BEFORE the synthesis is run.

## PICO
- **P** - adults with overweight or obesity and established cardiovascular disease but
  without diabetes.
- **I** - once-weekly subcutaneous semaglutide 2.4 mg added to standard care.
- **C** - placebo added to standard care.
- **O (primary)** - 3-point major adverse cardiovascular events, defined as
  cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke.
- **O (harms / secondary)** - gastrointestinal adverse events, adverse events leading to
  permanent discontinuation, and any further outcome the resolved comparator reports.

## Estimand / population / timepoint
- **Estimand** - hazard ratio (HR), semaglutide vs placebo.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - trial end / mean follow-up 39.8 months.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** - randomised controlled trial;
- **I2** - adults with overweight or obesity and established cardiovascular disease but
  without diabetes, judged from the title or registry conditions;
- **I3** - semaglutide vs placebo contrast;
- **design** - double-blind, placebo-controlled.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only);
- **X2** - wrong population (e.g. type 2 diabetes, type 1 diabetes, chronic kidney
  disease, heart failure, sleep apnea, or obesity trials without established
  cardiovascular disease);
- **X3** - wrong intervention/comparison (no semaglutide-vs-placebo contrast);
- **X-DESIGN** - not double-blind and placebo-controlled;
- **X5** - off-topic: a primary trial of another topic in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports 3-point MACE, or gives
> a 2x2 vs only an effect+CI, is recorded as target-result status at extraction - never as
> an exclusion. A published effect + 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/search.json; screening replays offline)
- PubMed: exact SELECT title/PMID sweeps for the main MACE report. Later SELECT secondary
  analyses are not configured as positive controls because they share NCT03574597 and the
  fixed harness deduplicates same-NCT PubMed records to the latest-year publication.
- ClinicalTrials.gov: condition "cardiovascular disease obesity without diabetes",
  intervention "semaglutide".
- Comparator/reference seeding is disabled so the broader comparator's reference list does
  not pull in semaglutide obesity trials outside the established-CVD SELECT population.

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(RR); **Paule-Mandel** tau^2; **HKSJ** 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. DerSimonian-Laird forbidden. Engine validated vs
metafor 5.0.1 (<1e-6). For this topic, the poolable input is the published HR + 95% CI
path on the same ratio/log scale; 2x2 extraction is available but is not required when a
trial reports an HR + CI.

## Comparator (resolved; open-access confirmed)
Stefanou et al., *Therapeutic Advances in Neurological Disorders* 2024, "Risk of major
adverse cardiovascular events and all-cause mortality under treatment with GLP-1 RAs or
the dual GIP/GLP-1 receptor agonist tirzepatide in overweight or obese adults without
diabetes: a systematic review and meta-analysis" (PMID 39345822, DOI
10.1177/17562864241281903; Unpaywall is_oa=true; PubMed Central PMC11437580). It reports
pooled MACE OR 0.79 (95% CI 0.71-0.89) over 16 RCTs in overweight or obese adults
without diabetes. This comparator is broader than the registered lane's semaglutide-only
SELECT population; the exact registered lane has one landmark eligible RCT.

## Controls
- **Positive** - SELECT main MACE report (PMID 37952131), the verified eligible landmark
  trial report. Only this positive control is configured to avoid same-NCT secondary
  SELECT reports superseding the main MACE paper during fixed harness deduplication.
- **Negative** - SUSTAIN-6 (PMID 27633186: semaglutide, randomized, placebo-controlled,
  but type 2 diabetes rather than obesity without diabetes) must be recovered and
  EXCLUDED by the population rule.

## Amendment 2026-10-05 -- identification sources (search+screen audit)

- **A1 REVIEW_REFERENCE_LIST (standing identification source).** Added: the comparator's (PMID 39345822) backward reference list (PubMed elink and Europe PMC) and its forward citations, and the backward reference lists of 1 other open meta-analysis (PMID 40890879; rule: most trial rows read by the secondary-meta lane, ties to the newer). Rationale: the registered search identified 1 of 2 of the comparator's eligible trials; with this route and the full retrieval below, 2 of 2 (1 of 2 without the comparator's own reference list, which contains its trials by construction). The route retrieves 111 records (recorded: outputs/search_audit/rrl_probe.json). Identification only: every record still passes the registered screen.
- **A3 Concept query: not adopted** (KEEP_CURRENT: volume 5005 > cap 5000; recorded call mc-984db8161135747397bf617cc473ccfd.json).

## Amendment 2026-10-06 -- search volume cap raised to 10,000 (decision under Mahmood's delegation)

- **A5 Volume cap 10,000 (was 5,000) for this topic; concept query added** (union; none removed): `("Obesity"[Mesh] OR "Overweight"[Mesh] OR obes*[tiab] OR overweight[tiab] OR "over weight"[tiab] OR "excess weight"[tiab] OR "excess body weight"[tiab]) AND ("Semaglutide"[Supplementary Concept] OR "Glucagon-Like Peptide-1 Receptor Agonists"[Mesh] OR semaglutid*[tiab] OR Ozempic[tiab] OR Wegovy[tiab] OR Rybelsus[tiab] OR (("GLP-1"[tiab] OR GLP1[tiab] OR "GLP 1"[tiab] OR "glucagon-like peptide-1"[tiab] OR "glucagon like peptide 1"[tiab]) AND (agonist*[tiab] OR analog*[tiab] OR mimetic*[tiab]))) AND (randomized controlled trial[pt] OR controlled clinical trial[pt] OR randomized[tiab] OR randomised[tiab] OR placebo[tiab] OR drug therapy[sh] OR randomly[tiab] OR trial[tiab] OR groups[tiab]) NOT (animals[mh] NOT humans[mh])`. Decided 2026-10-06 by the captain under Mahmood's delegation. Reason: the blind query audit (query_audit.json, recorded call mc-984db8161135747397bf617cc473ccfd.json) measured a recall gain on the comparator's eligible trials -- registered queries 1 of 2, with this query 2 of 2 -- at 5005 records, above the old 5,000 cap. Run in full on 2026-10-06: 5006 records, 4962 not already held; rule screen of the new records: {'include': 1, 'exclude': 4836, 'dedup_collapsed': 119, 'no_decision': 0}. Eligible comparator trials identified: 1 -> 2 of 2 (0 of the 1 newly identified pass the screen). Recorded: outputs/search_audit/expanded/semaglutide-obesity-mace.json.
