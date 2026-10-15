# Findings bound to review b3e40a3d206ff265345fd40a0e0a37136e86912150d7779a0b2ad3311acd4de0

## Numerical checks
SELECT's source-reported MACE HR is 0.80 (95% CI 0.72–0.90). A Cox model cannot
be independently reconstructed from its aggregate event counts. The diagnostic
crude RR is 0.811513; the crude OR is 0.798488. Neither is a replacement for the
registered HR.

From 1461/8803 versus 718/8801, the reconstructed adverse-event discontinuation
RR is 2.0343566403 (log-Wald 95% CI 1.8698848486–2.2132950822). This matches the
rendered rounding. Both supplied passage digests match; see results.json.

## 15-01 — False population exclusion of a SELECT companion report
Severity: changes served wording/record disposition and report-family linkage;
no demonstrated change to the primary numerical result.

PMID 38907684 is X2-excluded because its title does not contain the configured
literal population aliases. It also remains a separate unresolved candidate,
SYN-25796f0d0033, rather than a linked SELECT secondary report. The original
publication explicitly describes a prespecified SELECT analysis in the same
randomized population.

The positive-title fixture matches the primary title, not the companion's
"obesity but without diabetes" wording. Removing "but" makes the positive
alias match. This isolates brittle title phrasing; it is not a full screen test
and removing words from source records is not the proposed remedy.

Correct by retaining the report within SELECT (NCT03574597), preserving its
secondary-analysis role. Do not count it as another trial, double-count patients,
replace the overall HR with a subgroup estimate, or let a later report displace
the canonical primary report. If only this unresolved candidate is resolved,
the displayed candidate count moves from 37 to 36, all else held fixed.

## 15-02 — Population evidence is available but family eligibility remains unresolved
Severity: changes displayed eligibility/count metadata, not the efficacy HR.

All four structural families are UNKNOWN/ENTRY_POPULATION_NOT_ESTABLISHED.
Meanwhile SELECT's record is INCLUDE, and SUSTAIN-6's record is correctly X2
excluded for type 2 diabetes. The original reports establish those respective
populations. The page visibly discloses that a contributing family lacks
established structural eligibility; this is not an allegation of hidden admission.

If these two family states alone are adjudicated, the four-family inventory
becomes one eligible, one ineligible and two unresolved (rather than zero eligible
and four unresolved). This is a local correction, not an exhaustive trial census.
The empty eligible-family missing-evidence inventory must not be interpreted as
proof of complete outcome reporting.

## 15-03 — Unsupported completeness assertion and comparator scope description
Severity: changes served wording.

The comparator narrative calls k=1 the COMPLETE evidence base and not a search
gap, while the search tab retracts systematic-search claims. The audit did not
find a new independent eligible RCT, so it does not establish that k=1 is wrong.
It does establish that completeness has not been demonstrated by the process
shown, and companion-report losses provide a concrete counterexample to report
completeness.

The scope panel says population match=True and describes the comparator as a
network-level question. The comparator's own held full text describes an
aggregate pairwise random-effects odds-ratio meta-analysis. Its population is
broader than established-CVD-only SELECT, including general obesity cohorts.
The difference is not only single-agent versus drug-class treatment scope.

The pinned G1 tracker records G1_MATCHED, one matched/eligible comparator trial,
D12 count-based OR matching, and named differences. Those fields were read, not
re-executed. They are not evidence of an independent exhaustive search. This
audit does not overturn the recorded G1 result merely because broader trial
families or the full comparator contain different denominators.

## 15-04 — Source-reported versus reconstructed effect wording
Severity: changes served wording; arithmetic unchanged.

The discontinuation row correctly labels its value harness-reconstructed. Its
single-trial method paragraph nevertheless calls it the trial's own effect.
Label it as the review's unadjusted RR with a log-Wald CI, reconstructed from
reported participant counts. The generic manuscript statement that pooling used
PM/HKSJ should be conditional: no such pooling was performed at k=1.

## Harms coverage: valid refusal, but add the specific ascertainment limit
The all-GI refusal correctly rejects the all-cause discontinuation signal as the
wrong endpoint. A serious-GI count or a GI-discontinuation count cannot replace
an all-GI participant-risk outcome.

The original 2025 SELECT safety report, PMID 39948761, is not in the displayed
66-record fixture. Its methods describe targeted safety ascertainment; nonserious
AEs outside the specified collection categories were not systematically collected.
The omission from the rendered ledger is not proof of absence from every cache.

Use that source to document the ascertainment limit and, where permitted by a
dated amendment, extract separately defined serious-event and discontinuation
endpoints with exact participant denominators. Do not label failure to collect
all nonserious events as absence of such events or mere extractor failure.

## Supplied five-record screening sample
- 42555627: X1 supported; original observational study, also a different population.
- 42225300: final exclusion supported; the report is an indirect comparison using
  OASIS 4 and STEP 1, not a newly randomized trial. X1/report-role classification
  would be more informative than a title-alias X2 reason. The indexed RCT tag
  should not override the report's stated methods.
- 41889157: X1 supported; propensity-score matched observational study.
- 41968220: X1 supported; narrative review.
- 39345822: X1 supported as an independent-RCT exclusion; a meta-analysis usable
  as a comparator or source-discovery resource is not itself another trial.

## Repair order
Reconcile trial-family identity and population evidence; repair report-level
screening and report-role retention; bind safety collection categories; remove
unsupported completeness and method claims; rebuild and run the full pinned
replay. Do not edit verified primary numbers merely to make status tables agree.
