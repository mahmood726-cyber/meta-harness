# Protocol - daratumumab-containing regimens for progression-free survival in RRMM

**Registration.** The commit that adds this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab.
Committed BEFORE any search, screening or synthesis is run.

## PICO
- **P** - adults (age >=18 years) with confirmed relapsed/refractory multiple
  myeloma (RRMM).
- **I** - daratumumab-containing regimens.
- **C** - non-daratumumab-containing regimens; no particular background regimen
  is required by the comparator's stated methods.
- **O (primary)** - progression-free survival (PFS): the length of time from the
  start of treatment to disease progression or death. A sole primary outcome is
  not stated by the comparator; use the first pooled outcome reported in its
  abstract, PFS, under the captain adjudication.
- **O (harms / secondary)** - overall response rate (ORR), complete response (CR)
  rate, and minimal residual disease (MRD) negativity rate are also listed by the
  comparator. Its abstract reports harms involving pneumonia, upper respiratory
  tract infections, and diarrhea; these do not become additional eligibility criteria.

## Estimand / population / timepoint
- **Estimand** - hazard ratio (HR), daratumumab-containing vs
  non-daratumumab-containing regimens, for PFS. Published HR + 95% CI is a
  poolable input; the comparator uses RR for dichotomous outcomes.
- **Population** - a common analysis population is not stated by the comparator;
  use each trial's reported analysis population as pooled by the meta-analysis,
  recording it without assuming intention-to-treat.
- **Timepoint** - a common horizon is not stated by the comparator; use each
  trial's reported analysis as the meta pooled it, without inventing a common horizon.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff all hold:
- **I1** - "Randomized controlled trials (RCTs) that evaluated the use of
  daratumumab in the treatment of RRMM."
- **I2** - "Studies that included adult patients (age ≥ 18 years) with confirmed
  diagnosis of RRMM."
- **I3** - "Studies that compared daratumumab-containing regimens with
  non-daratumumab-containing regimens in the treatment of RRMM."
- **design** - randomised controlled trial; a double-blinding requirement is
  not stated by the comparator; do not add one.
- **Restrictions** - studies conducted in humans and published in English.

Exclude (reason must be true of the record):
- **X1** - not an RCT evaluating daratumumab for RRMM.
- **X2** - outside the stated adult confirmed-RRMM population; the comparator
  explicitly excludes studies including pediatric patients or other malignancies.
- **X3** - no daratumumab-containing vs non-daratumumab-containing regimen contrast.
- **Outcome / restrictions** - no listed outcome reported, or outside the stated
  human-study / English-publication restrictions.

> The template heading is retained for format compatibility. This benchmark copies
> its comparator's eligibility, including its reported-outcome restriction; the
> heading does not override that restriction. Reporting PFS specifically is not
> required when another listed outcome qualifies. PFS availability and extractability
> are recorded separately; a published HR + 95% CI does not require a 2x2 table.

## Search (fetch-once; raw results committed under cache/daratumumab-rrmm-pfs-bench/records.json; screening replays offline)
- PubMed: `daratumumab[tiab] AND "multiple myeloma"[tiab] AND (relapsed[tiab] OR refractory[tiab]) AND ("randomized controlled trial"[pt] OR randomized[tiab] OR randomised[tiab])`.
- ClinicalTrials.gov: condition "relapsed/refractory multiple myeloma",
  intervention "daratumumab".
- These are the committed topic's unexecuted operational translations, not
  verbatim comparator search strategies or claims of completed retrieval.
- The comparator searched PubMed, Web of Science, Embase, and the Cochrane
  Central Register of Controlled Trials from inception through December 1, 2022,
  restricted to humans and English, and manually searched reference lists of
  identified articles and relevant reviews.
- Under the captain adjudication, apply **no date filter** to our recorded search.
  Report trials published after the comparator search date through
  `PUBLISHED_AFTER_COMPARATOR`; never hide them. The historical cutoff describes
  the comparator and is not our retrieval cutoff.

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log(HR) for primary PFS; Paule-Mandel tau^2;
HKSJ 95% CI on `t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. DerSimonian-Laird forbidden. This is the
benchmark harness method inherited from the protocol templates, not an attribution
of these estimator choices to the comparator. Pool published HR + 95% CI on the
log-HR scale; do not substitute dichotomous RRs for PFS HRs.

## Comparator (resolved; open-access confirmed)
"Efficacy and safety of daratumumab in the treatment of relapsed/refractory
multiple myeloma: A meta-analysis of randomized controlled trials" (PMID 37747011;
PubMed Central PMCID PMC10519573). Its abstract reports PFS first among pooled
outcomes. PICO and eligibility evidence is recorded in
`registry/benchmarks/protocol_quotes/daratumumab-rrmm-pfs-bench.json`; the abstract
is available in the registry-named source `cache/benchmarks/v1/PMC10519573.xml`.

## Controls
- **Positive** - named positive controls are not stated by the comparator in the
  supplied topic or quote registry; no trial-specific controls are invented here.
- **Negative** - named negative controls are not stated by the comparator in the
  supplied topic or quote registry; apply the stated exclusion rules without
  inventing a control trial.

## Benchmark
- **Comparator meta PMID** - 37747011.
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
