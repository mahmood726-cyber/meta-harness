# Protocol - intravenous iron for heart-failure hospitalization in HFrEF with iron deficiency

**Registration.** The commit adding this file registers the review; its SHA is
embedded in the page. The protocol is committed before the synthesis is run.

## PICO
- **P** - adults with heart failure with reduced or mildly reduced ejection fraction and iron deficiency.
- **I** - intravenous iron, including ferric carboxymaltose, ferric derisomaltose, or iron sucrose.
- **C** - placebo, usual care, standard care, or no-treatment control.
- **O (primary)** - heart-failure hospitalization at trial end / longest reported follow-up.
- **O (harms)** - injection-site/administration-site reactions; hypersensitivity reactions.

## Estimand / population / timepoint
- **Estimand** - risk ratio (RR), intravenous iron vs placebo/standard care.
- **Population** - intention-to-treat as randomized.
- **Timepoint** - trial end / longest reported follow-up.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** - randomized controlled trial;
- **I2** - population is heart failure with reduced or mildly reduced ejection fraction and iron deficiency;
- **I3** - intravenous iron vs placebo, usual care, standard care, or no-treatment control;
- **design** - placebo-controlled or standard-care-controlled RCT; double blinding is not required.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only);
- **X2** - wrong population (for example HFpEF, COPD, pulmonary hypertension, dialysis, pregnancy/postpartum, inflammatory bowel disease, or restless legs);
- **X3** - wrong intervention/comparison (no intravenous iron vs eligible control contrast);
- **X5** - off-topic: a primary trial of another disease area in this set (negative control).

> Eligibility is NOT on the outcome axis. Whether a trial reports heart-failure
> hospitalization, or gives a 2x2 vs only an effect+CI, is recorded as target-result
> status at extraction - never as an exclusion. A published effect + 95% CI is a
> poolable input. Composite cardiovascular-death/heart-failure-hospitalization effects
> are not treated as standalone heart-failure hospitalization for the primary outcome.

## Search (fetch-once; raw results committed under cache/iv-iron-hfref-hosp/records.json; screening replays offline)
- PubMed: targeted primary-report searches for FAIR-HF2, AFFIRM-AHF, and IRONMAN.
- PubMed comparator-reference seeding: trials cited by the resolved comparator are fetched and screened by the same rules.
- ClinicalTrials.gov: condition "heart failure reduced ejection fraction iron deficiency", intervention "intravenous iron".

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(RR); Paule-Mandel tau^2; HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells of a
study only if it has a zero cell. DerSimonian-Laird forbidden. Engine validated vs
metafor 5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
Parmananda et al., *Diseases* 2024, "The Efficacy and Safety of Ferric
Carboxymaltose in Heart Failure with Reduced Ejection Fraction and Iron Deficiency:
An Updated Systematic Review and Meta-Analysis of Randomized Controlled Trials"
(PMID 39727669, PMC11727542, DOI 10.3390/diseases12120339; Unpaywall is_oa=true).
It reports total HF hospitalizations OR 0.59 (95% CI 0.40 to 0.88) over six RCTs,
plus serious adverse events and qualitative angioedema/hypersensitivity detail.

## Controls
- **Positive** - the search must recover FAIR-HF2 (PMID 40159390), AFFIRM-AHF
  (PMID 33197395), and IRONMAN (PMID 36347265).
- **Negative** - the COPD intravenous-iron RCT (PMID 32565444) must be recovered
  and EXCLUDED as wrong population.

## Amendment 2026-10-05 -- identification sources (search+screen audit)

- **A1 REVIEW_REFERENCE_LIST (standing identification source).** Added: the comparator's (PMID 39727669) backward reference list (PubMed elink and Europe PMC) and its forward citations, and the backward reference lists of 2 other open meta-analyses (PMID 36734033, 39527395; rule: most trial rows read by the secondary-meta lane, ties to the newer). Rationale: the registered search identified 5 of 5 of the comparator's eligible trials; with this route and the full retrieval below, 5 of 5 (5 of 5 without the comparator's own reference list, which contains its trials by construction). The route retrieves 64 records (recorded: outputs/search_audit/rrl_probe.json). Identification only: every record still passes the registered screen.
- **A3 Concept query added** (union with the registered queries; none removed): `("Heart Failure"[Mesh] OR "Ventricular Dysfunction, Left"[Mesh] OR "heart failure"[tiab] OR "cardiac failure"[tiab] OR "cardiac insufficiency"[tiab] OR "myocardial failure"[tiab] OR HFrEF[tiab] OR HFREF[tiab] OR "HF-REF"[tiab] OR "systolic dysfunction"[tiab] OR "reduced ejection fraction"[tiab] OR "impaired ejection fraction"[tiab] OR "left ventricular dysfunction"[tiab]) AND ((("Iron"[Mesh] OR "Iron Compounds"[Mesh] OR iron[tiab] OR ferric[tiab] OR ferrous[tiab]) AND ("Administration, Intravenous"[Mesh] OR "Infusions, Intravenous"[Mesh] OR "Injections, Intravenous"[Mesh] OR intravenous[tiab] OR intravenously[tiab] OR parenteral[tiab] OR infusion*[tiab] OR IV[tiab])) OR "Iron-Dextran Complex"[Mesh] OR "Ferric Oxide, Saccharated"[Mesh] OR "ferric carboxymaltose"[tiab] OR "iron carboxymaltose"[tiab] OR "ferric derisomaltose"[tiab] OR "iron derisomaltose"[tiab] OR "iron isomaltoside"[tiab] OR "ferric isomaltoside"[tiab] OR "iron sucrose"[tiab] OR "iron saccharate"[tiab] OR "saccharated ferric oxide"[tiab] OR "ferric gluconate"[tiab] OR "iron gluconate"[tiab] OR "iron dextran"[tiab] OR "iron polymaltose"[tiab] OR "iron dextrin"[tiab] OR ferumoxytol[tiab] OR Ferinject[tiab] OR Injectafer[tiab] OR Monofer[tiab] OR Monoferric[tiab] OR Diafer[tiab] OR Venofer[tiab] OR Ferrlecit[tiab] OR Feraheme[tiab] OR Rienso[tiab] OR INFeD[tiab] OR Cosmofer[tiab] OR Dexferrum[tiab] OR Imferon[tiab] OR Ferosig[tiab] OR "Ferrum Hausmann"[tiab]) AND (randomized controlled trial[pt] OR controlled clinical trial[pt] OR randomized[tiab] OR randomised[tiab] OR placebo[tiab] OR drug therapy[sh] OR randomly[tiab] OR trial[tiab] OR groups[tiab]) NOT (animals[Mesh] NOT humans[Mesh])`. Proposed blind (the proposer saw the PICO and the current queries with their volumes, never the comparator's trials or our misses; recorded call mc-4e753b9f3d0bc21ade9a33c9cd75b8ac.json); returns 774 records today; on the comparator's eligible trials the registered queries match 1 of 5 and the union 5 of 5. Limitation: the proposer may know well-known trials from training.
