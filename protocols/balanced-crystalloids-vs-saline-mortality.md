# Protocol - balanced crystalloids vs saline for mortality in critically ill adults

**Registration.** The commit that adds this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab.
Committed BEFORE the synthesis is run.

## PICO
- **P** - critically ill adults, including adult ICU, sepsis, or trauma resuscitation populations matched on title or registry conditions.
- **I** - balanced or buffered crystalloid solution, including balanced crystalloids, balanced multielectrolyte solution/BMES, Plasma-Lyte, Ringer's acetate, or lactated Ringer's.
- **C** - 0.9% saline / normal saline / sodium chloride.
- **O (primary)** - mortality, using in-hospital mortality or 28-90 day mortality where the abstract reports a poolable count or effect estimate.
- **O (harms)** - acute kidney injury and new renal-replacement therapy.

## Estimand / population / timepoint
- **Estimand** - risk ratio (RR), balanced crystalloid vs saline.
- **Population** - intention-to-treat as randomised when reported.
- **Timepoint** - 28-90 day mortality or in-hospital mortality.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** - randomised trial;
- **I2** - population is critically ill adults, ICU patients, adult sepsis patients, or adult trauma resuscitation patients, judged from title or registry conditions;
- **I3** - balanced/buffered crystalloid solution vs 0.9% saline / normal saline / sodium chloride;
- **design** - randomised trial with a saline comparator; double-blinding is not required.

Exclude (reason must be true of the record):
- **X1** - not a randomised trial (review, guideline, observational study, protocol-only when not a trial results record);
- **X2** - wrong population (e.g. pediatric/PICU, neonatal, non-critically ill emergency-department adults, diabetic ketoacidosis);
- **X3** - wrong intervention/comparison (no balanced-crystalloid-vs-saline contrast);
- **X-DESIGN** - not randomised;
- **X5** - off-topic: a primary trial of another population/topic in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports mortality, or
> gives a 2x2 vs only an effect+CI, is recorded as *target-result status* at
> extraction - never as an exclusion. A published effect + 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/records.json; screening replays offline)
- PubMed: title-level searches for SMART, PLUS, BaSICS, SPLIT, SALT, the Plasma-Lyte 148 pilot, and the trauma Plasma-Lyte A trial.
- ClinicalTrials.gov: condition "critical illness", intervention "balanced crystalloids".

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(RR); **Paule-Mandel** tau^2; **HKSJ** 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells of a study only if
it has a zero cell. DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
Zayed et al., *Journal of Intensive Care* 2018, "Balanced crystalloids versus isotonic
saline in critically ill patients: systematic review and meta-analysis" (PMID 30140441,
DOI 10.1186/s40560-018-0320-x; Unpaywall is_oa=true; PMC6098635). It reports six RCTs
and in-hospital mortality OR 0.92 (95% CI 0.85-1.01), plus acute kidney injury and new
renal-replacement therapy.

## Controls
- **Positive** - SMART (PMID 29485925) and PLUS (PMID 35041780) must be recovered and included by P/I/C/design.
- **Tracked landmark** - BaSICS (PMID 34375394) is queried and verified as a real large trial, but PubMed tags the fetched record as Journal Article only; under this fixed harness it is expected to fail closed at the RCT-publication-type screen rather than be force-included.
- **Negative** - SPLYT-P (PMID 36534387), a pediatric/PICU balanced-fluid trial, must be recovered and EXCLUDED as wrong population.
