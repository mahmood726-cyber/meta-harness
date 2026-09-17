# Protocol - metformin for ovulation in polycystic ovary syndrome

**Registration.** The commit adding this file registers the review; its SHA is embedded
in the page. The protocol is committed before the synthesis runs.

## PICO
- **P** - women with polycystic ovary syndrome (PCOS) undergoing ovulation induction,
  including clomiphene-resistant or anovulatory PCOS populations.
- **I** - metformin, alone or added to the same background ovulation-induction regimen
  in both trial arms.
- **C** - placebo or placebo-controlled non-metformin treatment, with the same
  background regimen where a background regimen is used.
- **O (primary)** - ovulation rate.
- **O (harms)** - gastrointestinal adverse events; treatment discontinuation due to
  adverse events.

## Estimand / population / timepoint
- **Estimand** - odds ratio (OR), metformin vs placebo.
- **Population** - as randomised.
- **Timepoint** - end of treatment.

## Eligibility - P/I/C/DESIGN only
Include a record iff **all** hold:
- **I1** - randomised controlled trial;
- **I2** - population is women with PCOS, polycystic ovarian syndrome, or polycystic
  ovaries in an ovulation-induction/subfertility context;
- **I3** - the randomised contrast is metformin vs placebo, including trials with the
  same background ovulation-induction treatment in both arms;
- **design** - placebo-controlled RCT; double blinding is not required.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only);
- **X2** - wrong population/context (e.g. IVF/ICSI or pregnancy/offspring follow-up);
- **X3** - wrong intervention/comparison (no metformin-vs-placebo contrast, or an
  active non-metformin intervention is the randomised contrast);
- **X5** - off-topic: a primary trial of another disease/topic in this set (negative
  control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports ovulation rate,
> and whether it reports it as a 2x2 table versus only an effect plus CI, is recorded
> as target-result status at extraction - never as an exclusion. A published effect
> plus 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/records.json; screening replays offline)
- PubMed: metformin x PCOS/polycystic ovary syndrome x placebo x ovulation/randomised.
- ClinicalTrials.gov: condition "polycystic ovary syndrome", intervention "metformin".

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(OR); **Paule-Mandel** tau^2; **HKSJ** 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells of a
study only if it has a zero cell. DerSimonian-Laird forbidden. Engine validated vs
metafor 5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
Sharpe et al., *Cochrane Database of Systematic Reviews* 2019, "Metformin for
ovulation induction (excluding gonadotrophins) in women with polycystic ovary
syndrome" (PMID 31845767, PMCID PMC6915832, DOI 10.1002/14651858.CD013505;
Unpaywall is_oa=true). It reports ovulation OR 2.64 (95% CI 1.85 to 3.75) for
metformin versus placebo/no treatment and gastrointestinal side effects OR 4.00
(95% CI 2.63 to 6.09).

## Controls
- **Positive** - the search must recover and include canonical placebo-controlled
  PCOS ovulation-induction metformin trials: Moll 2006 (PMID 16769748), Ng 2001
  (PMID 11473953), and Sturrock 2002 (PMID 11994052).
- **Negative** - the Diabetes Prevention Program metformin trial in impaired glucose
  tolerance/type 2 diabetes prevention (PMID 11832527) must be recovered and EXCLUDED
  as wrong population/topic.

## Retrospective executable-screen amendment (2026-09-16)
`PROTOCOL_CONFIG_DIVERGENCE`: known-answer screening audit SC found that ovulation
induction context and the gonadotrophin exclusion in the comparator review were
not executable. The config now requires ovulation-induction / clomiphene context
and excludes hMG / human menopausal gonadotrophin add-on designs. The PCOS title
miss for PMID 19552097 is fixed mechanically in screening negation handling rather
than by a record-specific override. This amendment changes screening only.
