# Protocol - hydroxychloroquine or chloroquine prophylaxis for COVID-19

**Registration.** The commit that adds this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab.
Committed BEFORE any search, screening or synthesis is run.

## PICO
- **P** - adults (>=18 years) SARS CoV-2 negative (PCR negative or asymptomatic)
  at enrolment, in contact with an infected individual or at high risk of exposure,
  such as healthcare workers.
- **I** - oral hydroxychloroquine or chloroquine, at any dose, frequency, or
  duration, as pre- or post-exposure prophylaxis.
- **C** - no quinines or placebo, including usual care / no prophylaxis.
- **O (primary)** - developing COVID-19, defined by either symptoms or PCR
  confirmation. A sole primary outcome is not stated by the comparator; use the
  first pooled outcome reported in its abstract, developing COVID-19, under the
  captain adjudication. PCR-positive-only infection is a separate analysis.
- **O (harms / secondary)** - severity and duration of COVID-19 symptoms,
  hospitalization, mortality at longest follow-up, ICU admission, medication
  compliance, and adverse events are also listed in comparator eligibility.

## Estimand / population / timepoint
- **Estimand** - relative risk (RR), prophylactic hydroxychloroquine or chloroquine
  vs no quinines / placebo, for developing COVID-19, with 95% CI.
- **Population** - a common analysis population is not stated by the comparator;
  use each trial's reported analysis population as pooled by the meta-analysis,
  recording it without assuming intention-to-treat.
- **Timepoint** - a common infection-assessment horizon is not stated by the
  comparator; use each trial's reported analysis as the meta pooled it, without
  inventing a common horizon. Mortality at longest follow-up remains the
  comparator's separately listed mortality outcome.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff all hold:
- **I1** - "We included RCTs, while pseudo or quasi-randomized and non-randomized
  studies were excluded."
- **I2** - "The trial population included adults (≥18 years old) who are SARS
  CoV-2 negative [via polymerase chain reaction (PCR) or asymptomatic] at the time
  of enrolment, and were either in contact with an individual positive for SARS
  CoV-2, or at high risk of exposure to SARS CoV-2 such as HCWs."
- **I3** - "The intervention group received oral hydroxychloroquine or chloroquine,
  at any dose, frequency, or duration, as either pre or post-exposure prophylaxis.
  The control group did not receive quinines or received placebo for blinding."
- **design** - randomised controlled trial; a double-blinding requirement is
  not stated by the comparator; do not add one.
- **Restrictions** - no publication-status or language restriction.

Exclude (reason must be true of the record):
- **X1** - pseudo-randomized, quasi-randomized, non-randomized, or otherwise not an RCT.
- **X2** - outside the stated adult, negative-at-enrolment, exposed or high-risk
  population, including treatment rather than prophylaxis populations.
- **X3** - outside oral hydroxychloroquine / chloroquine prophylaxis versus no
  quinines or placebo.

> The template heading is retained for format compatibility. This benchmark copies
> its comparator's eligibility, including its reported-outcome restriction; the
> heading does not override that restriction. Reporting developing COVID-19
> specifically is not required when another listed outcome qualifies. Primary-result
> availability and extractability are recorded separately. Retain chloroquine and
> no-prophylaxis controls even though the included trials used hydroxychloroquine.

## Search (fetch-once; raw results committed under cache/hcq-covid-prophylaxis-bench/records.json; screening replays offline)
- PubMed: `(hydroxychloroquine[tiab] OR chloroquine[tiab]) AND (COVID-19[tiab] OR SARS-CoV-2[tiab]) AND (prophylaxis[tiab] OR prevention[tiab]) AND ("randomized controlled trial"[pt] OR randomized[tiab] OR randomised[tiab])`.
- ClinicalTrials.gov: condition "COVID-19", intervention "hydroxychloroquine OR
  chloroquine".
- These are the committed topic's unexecuted operational translations, not
  verbatim comparator search strategies or claims of completed retrieval.
- The comparator searched EMBASE, MEDLINE, the Cochrane COVID-19 Register of
  Controlled Trials (CENTRAL), and Epistemonikos COVID-19 every two weeks from
  inception through September 28, 2020; it also searched ClinicalTrials.gov and
  WHO ICTRP through that date, screened review reference lists, and contacted
  trial authors when required. No publication-status or language restriction
  applied; database strategies were referenced in S1-S4 Tables.
- Under the captain adjudication, apply **no date filter** to our recorded search.
  Report trials published after the comparator search date through
  `PUBLISHED_AFTER_COMPARATOR`; never hide them. The historical cutoff describes
  the comparator and is not our retrieval cutoff.

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log(RR); Paule-Mandel tau^2; HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. Apply a 0.5 continuity correction to all four
cells of a study only if it has a zero cell. DerSimonian-Laird forbidden. This is
the benchmark harness method inherited from the protocol templates, not an
attribution of these estimator choices to the comparator. A published RR + 95% CI
is poolable when 2x2 counts are unavailable.

## Comparator (resolved; open-access confirmed)
"The efficacy and safety of hydroxychloroquine for COVID-19 prophylaxis: A
systematic review and meta-analysis of randomized trials" (PMID 33406138;
PubMed Central PMCID PMC7787432). Its abstract reports developing COVID-19 first
among pooled outcomes. Its stated research question includes transmission,
mortality, and hospitalization; its eligibility allows both hydroxychloroquine and
chloroquine and controls without quinines as well as placebo. PICO and eligibility
evidence is recorded in
`registry/benchmarks/protocol_quotes/hcq-covid-prophylaxis-bench.json`; the abstract
is available in the registry-named source `cache/benchmarks/v1/PMC7787432.xml`.

## Controls
- **Positive** - named positive controls are not stated by the comparator in the
  supplied topic or quote registry; no trial-specific controls are invented here.
- **Negative** - named negative controls are not stated by the comparator in the
  supplied topic or quote registry; apply the stated exclusion rules without
  inventing a control trial.

## Benchmark
- **Comparator meta PMID** - 33406138.
- **Prereg commit** - `4adf8793ab88`.
- **v1.1 commit** - `b4842f04d8b8`.
- **Protocol topic commit** - `3d9e65bf196b`.
- **Scope** - Open-access meta-analyses whose included trials are all recent (started 2010 or later) and prospectively registered.
  This is benchmark selection scope, not an additional eligibility restriction
  attributed to the comparator.
- **Captain adjudication** - captain, 15 Oct 2026 (benchmark build ruled by
  Dispatch D1 on Mahmood's delegation): use the abstract's first-reported pooled
  outcome as primary when no sole primary is designated; use each trial's reported
  analysis as pooled; mirror the meta's own stated eligibility; apply no search
  date filter and report post-cutoff trials through `PUBLISHED_AFTER_COMPARATOR`.
  This adjudication governs the older pending-adjudication labels in the topic.

## Named divergence from the comparator's method (captain, 15 Oct 2026)
- The comparator also required an included trial to REPORT one of its listed outcomes. This harness screens on
  P/I/C/design only (excluding on outcome reporting builds in selective-reporting bias); a trial that does not
  report the primary outcome is included and shown as declared-absent for that outcome. Any trial the
  comparator excluded for this reason is reported by the G1 tracker as DIVERGENT_NAMED (OUTCOME_DEFINITION /
  eligibility-on-outcome), not as a mismatch.
