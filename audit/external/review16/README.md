# Topic 16 — independent audit checks

Audit date: 10 October 2026.
Topic: semaglutide-obesity-weight.
Pinned repository reference: 0730234d0b4f.
Recorded review_sha256:
f4438abd8845e86c345fee8631b94629c278f781990d9750fdfe1d8e38ca50a2.

## What was executed

- `audit_checks.py`: an independent additive mean-difference inverse-variance
  reconstruction, Paule–Mandel tau-squared, floored HKSJ interval and common-effect
  sensitivity. The normal quantile is calculated with scipy.stats.norm.ppf.
- SHA-256 of both passage strings supplied in the user's audit pack, with HTML
  entities decoded. Inputs are explicit manual transcriptions, not a downloaded
  canonical review JSON.
- An auditor-derived unadjusted risk ratio and log-Wald interval from the original
  STEP 3 Table 3 gastrointestinal participant counts (337/407 vs 129/204).
- `isolated_precedence_test.py`: a manually transcribed audit_pair control-flow
  excerpt with deliberately stubbed helper outputs. It tests precedence of a
  supplied numeric-candidate match over a TIMEPOINT_MISMATCH. It does NOT execute
  the production candidate detector, screening system or publication gate.

Run with Python 3, numpy and scipy:

    python audit_checks.py
    python isolated_precedence_test.py

Both scripts ran successfully in this audit. The numerical checks include
assertions for the two passage hashes, the displayed pooled rounding (-11.47)
and the displayed five-decimal tau-squared (1.71137).

## Key results

The two published effect/CI inputs reconstruct the displayed pooled MD:
-11.4731860884 percentage points; tau-squared 1.7113724256; I-squared 77.6133%.
The common-effect sensitivity reconstructs to -11.9002636783, 95% interval
[-12.7295599863, -11.0709673703].

The HKSJ interval [-24.7225666078, 1.7761944311] is an AUDITOR DIAGNOSTIC. The
pinned review withholds that interval under its two-study policy. This audit does
not recommend switching to the common-effect model to obtain a narrower result.

The recovered STEP 3 GI counts yield an auditor-derived RR 1.3094108908,
log-Wald 95% interval [1.1687810701, 1.4669615421]. This is NOT an admitted or served
harness result. Source-specific safety observation period and endpoint binding
remain necessary. The total event counts, 1760 and 333, were NOT used as numbers
of participants. No symptom counts or rounded percentages were summed/inverted.

## Findings and source checks

### 16-01: protocol and estimator/source rule are inconsistent
The accessible pinned protocol requires registry per-arm raw means and SDs,
whereas the two displayed inputs are publication-reported treatment differences
and confidence intervals. This is a protocol/estimator-description mismatch, not
proof that publication-reported adjusted treatment-policy estimates are invalid.
No reconciliation was visible in the retrieved protocol or topic configuration.
The complete later Changes tab could not be extracted, so an absolute claim that
no signed notice exists anywhere in the repository is NOT made.
The prose specifies Week 68 while the configuration has an eight-week tolerance.
That discrepancy should be resolved before admission of nearby timepoints.

### 16-02: generic value availability is not target-outcome availability
The pinned overview names 42070571, 40825340 and 40544433 as papers whose primary
outcome is reported but not pooled. The first is a 26-week alcohol-use-disorder
trial; the second is 44-week STEP 11. Neither establishes a Week-68 weight result.
In the first, the headline -13.7 percentage-point effect is heavy-drinking days.
This audit does NOT assert that the production parser necessarily selected that
exact sentence, or that either effect entered the pooled estimate.

The source code in unextracted.audit_pair checks a generic found-value result
before an explicit design/timepoint mismatch. reason_audit.find_value_in_sources
has no timepoint or contrast argument. The isolated test demonstrates that branch
ordering; it is not a production replay. A better representation retains both
candidate evidence and target-specific admissibility instead of conflating them.

### 16-03: multi-arm exclusion needs contrast-level adjudication
The supplied screening sample excludes STEP UP (40961952) for the occurrence of
7.2 mg in its title. Its original report also contains 2.4-mg and placebo arms,
201 participants each. Final admission is not resolved by this observation:
the study is at Week 72 and the protocol's multi-arm/pre-specified-comparison rule
must be applied explicitly. An entire-trial wrong-population reason based on the
headline dose is not an adequate contrast-level judgement.

### 16-04: recoverable GI evidence and a disconnected refusal witness
The cache's STEP 3 GI refusal is based on an abstract supplying percentages but
not numerators. The original full-text Table 3 contains the actual aggregate
participant counts. This is a source-acquisition/binding repair opportunity, not
proof that the abstract-only statement about its held text was false.
The STEP 1 GI refusal's stored source_span instead quotes a 5%-weight-loss efficacy
result. That string does not support its GI-specific reason, regardless of
whether the final refusal is otherwise defensible.

### Already-known gap, now with a concrete source route: STEP 8
STEP 8/NCT04074161 is already listed by the page as missing. Its original full
text reports a Week-68 semaglutide-versus-POOLED-placebo MD of -13.9 with interval
[-16.7, -11.0]. The main active-comparator result (-9.4 vs liraglutide) is NOT the
placebo comparison. Pooled-placebo composition, masking of the actual contrast,
multi-arm rules and permitted estimator must be adjudicated before using this.
No STEP 8 value was added to the audit's primary reconstruction.

## Screening sample scope

41211586: review, exclusion X1 supported.
40961952: exclusion reason needs correction; final admission remains conditional.
42536519: meta-analysis, exclusion X1 supported.
42220875: systematic review, exclusion X1 supported.
NCT05579249: original conference report describes an active-controlled pragmatic
trial, supporting exclusion for no placebo. No claim to have downloaded its live
registry JSON.

## Explicit limits

- Not a full offline replay; no complete repository or production-path execution.
- No canonical review, HTML, release or certificate hash independently regenerated.
- The certificate's full hash and page-header prefix agree with the supplied pack.
- The live page could not be independently retrieved for byte-level verification.
- The large pinned review JSON was not acquired; long minified HTML sections were
  truncated by connectors. No full checklist sign-off is claimed for unread tabs.
- Neither all 143 screening records nor all 54 families were re-adjudicated.
- Original trial HTML, abstracts and tables were used; no PDF visual inspection is
  claimed.
- No source full texts or font files are redistributed in this ZIP.
- No repository, live page, protocol or database was modified.
- No repaired complete meta-analysis or clinical recommendation is claimed.
