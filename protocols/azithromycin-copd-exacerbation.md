# Protocol - azithromycin for prevention of COPD exacerbations

**Registration.** The commit that adds this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab.
Committed BEFORE the synthesis is run.

## PICO
- **P** - adults with COPD receiving chronic prophylaxis or maintenance treatment to
  prevent acute COPD exacerbations.
- **I** - azithromycin added to usual COPD care.
- **C** - placebo added to usual COPD care.
- **O (primary)** - patients with at least one acute COPD exacerbation during follow-up.
- **O (harms)** - hearing impairment and gastrointestinal adverse effects.

## Estimand / population / timepoint
- **Estimand** - risk ratio (RR), azithromycin vs placebo.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - study end, preferably 6 to 12 months.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** - randomised controlled trial;
- **I2** - adults with COPD in a chronic prophylaxis/maintenance setting;
- **I3** - azithromycin vs placebo, added to usual care;
- **design** - placebo-controlled randomised trial; double-blinding is recorded when
  reported but is not a separate eligibility requirement for this topic.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only);
- **X2** - wrong population or setting (e.g. non-COPD disease; acute COPD exacerbation
  requiring hospitalization rather than chronic prevention);
- **X3** - wrong intervention/comparison (no azithromycin-vs-placebo contrast);
- **X-DESIGN** - not placebo-controlled;
- **X5** - off-topic: a primary trial of another topic in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports patients with
> at least one exacerbation, or gives a 2x2 vs only an effect+CI, is recorded as
> target-result status at extraction - never as an exclusion. A published effect +
> 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/records.json; screening replays offline)
- PubMed: targeted searches for the MACRO/Albert and COLUMBUS azithromycin COPD
  prevention trial reports, plus smaller stable-COPD azithromycin placebo trials.
- ClinicalTrials.gov: condition "COPD", intervention "azithromycin".
- Comparator-reference seeding is disabled for this topic because PubMed links a
  newer MACRO ancillary paper to the same NCT record; seeding would cause the fixed
  deduper to retain the ancillary paper instead of the main trial report.

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(RR); **Paule-Mandel** tau^2; **HKSJ** 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells of a study
only if it has a zero cell. DerSimonian-Laird forbidden. Engine validated vs metafor
5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
Ni et al., *International Journal of Chronic Obstructive Pulmonary Disease* 2018,
"Long-term macrolide treatment for the prevention of acute exacerbations in COPD: a
systematic review and meta-analysis" (PMID 30538443, DOI 10.2147/COPD.S181246;
PMCID PMC6254503; Unpaywall is_oa=true). It reports that long-term macrolides reduced
the total number of patients with one or more exacerbations (OR 0.40, 95% CI 0.24-0.65)
and reports nonfatal adverse events, including azithromycin-specific adverse events.

## Controls
- **Positive** - the search must recover the canonical azithromycin-vs-placebo COPD
  prevention RCTs: MACRO/Albert 2011 (PMID 21864166) and COLUMBUS/Uzun 2014
  (PMID 24746000).
- **Negative** - the primary-antibody-deficiency azithromycin prophylaxis RCT
  (PMID 30910492) must be recovered and EXCLUDED as non-COPD.
