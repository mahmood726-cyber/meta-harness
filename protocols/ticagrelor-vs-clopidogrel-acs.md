# Protocol - ticagrelor vs clopidogrel for MACE in acute coronary syndrome

**Registration.** The commit that adds this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and Reproducibility tab.
The integrator will commit this working-tree protocol on main.

## PICO
- **Population** - adults with acute coronary syndrome, including non-ST-elevation
  acute coronary syndrome and ST-elevation myocardial infarction.
- **Intervention** - ticagrelor, including the development name AZD6140.
- **Comparator** - clopidogrel.
- **Primary outcome** - major adverse cardiovascular events, defined as the composite
  of cardiovascular or vascular death, myocardial infarction, or stroke.
- **Secondary outcomes** - none prespecified for this micro-topic.
- **Harm outcomes** - major bleeding and dyspnea when extractable from the same source
  hierarchy.

## Eligibility - P/I/C/design only
Include a record iff all criteria hold:
- randomized controlled trial;
- adults with acute coronary syndrome, NSTE-ACS, or STEMI, judged from title,
  registry conditions, or acronym;
- ticagrelor/AZD6140 is the randomized intervention;
- clopidogrel is the randomized comparator;
- double-blind design.

Exclude records for wrong population, wrong intervention or comparator, non-randomized
design, non-double-blind design, reviews/meta-analyses, protocols without randomized
outcome results, or same-drug wrong-topic trials such as acute stroke/TIA. Prasugrel
comparisons are wrong-comparator trials for this PICO.

Eligibility is not based on whether the MACE outcome is reported. A screened-in trial
that does not report the exact primary outcome in its abstract with arm counts or an
effect plus 95% CI is declared target-result absent.

## Outcome Identity Discipline
The primary pooled value must be the trial result for MACE: cardiovascular or vascular
death, myocardial infarction, or stroke. Do not substitute a different primary endpoint,
platelet reactivity, myocardial infarction alone, bleeding, dyspnea, pharmacokinetics,
body weight, kidney outcomes, a subgroup result, or a design/rationale paper.

PLATO's outcomes paper is PMID 19717846. The PLATO rationale/design paper and early
pharmacodynamic or pharmacokinetic substudies are not outcome-result sources for this
review unless their abstracts state the exact MACE endpoint with a valid extractable
effect or count.

## Analysis Method
Random-effects inverse-variance synthesis on log ratio effects, using the harness
implementation declared in the served review: Paule-Mandel tau^2, HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1,Q/(k-1))`, and prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. A trial-level published HR plus 95% CI is the
preferred input for the primary outcome. If no HR is reported but percentage-
corroborated arm counts are available for the exact MACE outcome, those counts may be
used by the harness fallback; otherwise the trial is declared absent.

## Comparator
Comparator PMID 28545073 is Tan et al., *PLoS One* 2017, "The clinical efficacy and
safety evaluation of ticagrelor for acute coronary syndrome in general ACS patients and
diabetic patients: A systematic review and meta-analysis" (PMCID PMC5435320, DOI
10.1371/journal.pone.0177872). It is an open-access meta-analysis of ticagrelor versus
clopidogrel/prasugrel in ACS; the comparator extraction uses the ticagrelor-versus-
clopidogrel composite endpoint reported in the abstract.

## Amendment 2026-10-09 (estimand RR -> HR, post hoc; V13-03Q)
**Status: POST HOC.** This amendment was made after the results were seen and is signed by Mahmood (V13-03Q, option A, 9 Oct 2026: 'sign v13' / 'yes to all recommended'; packet lane_status/v13_packet.md sha256 d9842124e80997c0a72ab3c7dca687fe8a0c86c2e21e84f6207f4d44e0f99ace). The original declaration above is kept unchanged.

- **Major bleeding.** Declared estimand: RR. Amended to: HR (time to first event).
- **Reason.** For these time-to-first-event outcomes the trials print a hazard ratio, which the review already served under the source hierarchy; the declaration is brought into line with what is served. No served number changes.
