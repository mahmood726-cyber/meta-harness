# Topic 29 external audit — PCSK9 inhibitors and cardiovascular events

Audit date: 2026-10-10. Repository: mahmood726-cyber/meta-harness.
Pinned reference: 0730234d0b4f.
Review SHA-256 (recorded identity, NOT regenerated):
c1341006e13430827d2b36100479dfd098dea87cb4e84e15264f045d0b90129d
Status remains ABANDONED_BY_DECISION. No repository or website changes were made.

## Run

Python 3.10 or later, standard library only:

    python audit.py

Writes results.json. An alternative output path may be supplied with --output.

The 19 checks include numerical invariants, two supplied/rendered passage hashes,
a seeded sample from manually transcribed screening IDs, and deliberately
isolated endpoint-component/fallback fixtures. They are not 19 independent
clinical validations, a complete systematic review, or production-gate tests.

## What was established

The current two-input point estimate is independently reproduced. Original trial
reports support FOURIER's key secondary HR 0.80 (0.73–0.88) and ODYSSEY OUTCOMES's
primary HR 0.85 (0.78–0.93). The current HKSJ confidence interval is withheld by
the harness's k=2 policy; the interval calculated here is audit-only.

The ODYSSEY D5 cache incorrectly calls its MACE estimate a match to registered
CHD death alone. The correct four-component primary definition is present in the
same cache. The component parser does not recognize CHD death; a generic MACE
name supplies three default components. The isolated tests show rejection of the
actual four-component definition and the permissiveness of a deliberately
synthetic callback when the candidate has no recognized components.

IMPORTANT: the actual production matches callback was NOT reproduced. With no
callback, the isolated CHD-death fixture returns NO MATCH. Therefore this bundle
does NOT reproduce the whole production mechanism that selected CHD death.
The stored wrong match is directly observed in cache/pcsk9-mace/rob2.json and
the pinned page. No claim that the numerical efficacy row contains a CHD-death
estimate is made; that row correctly contains the composite HR.

VESALIUS is an already-known binding gap. Its addition here is a conditional,
unadmitted diagnostic, not a newly discovered missing trial, an approved update,
or a claim that this three-study set is complete. Three-point and four-point
co-primary alternatives are kept separate, not pooled together.

ODYSSEY LONG TERM's MACE analysis is post hoc and remains excluded under the
recorded policy. A source-present result does not falsify that valid refusal.
Its injection-reaction row was withdrawn because its source approval digest no
longer matched; this is reported-but-unapproved evidence, not an unreported
outcome. No safety result is reinstated by this audit.

## Files and origins

- independent_math.py: auditor-authored standard-library implementation, not
  production synthesis.py. CI-derived variances; Paule–Mandel; HKSJ floor.
- endpoint_excerpt.py: manually transcribed subset of inspected harness/rob2.py;
  original connector-reported blob 0b66b00267ac6c2b138174cc38644b3bf7a955d9.
  No claim that this excerpt's bytes match the full original module.
- inputs.json: manual transcriptions, two exact displayed passage strings,
  counterfactual inputs, and explicit test scope.
- audit.py / results.json: executable checks and their actual output.
- numerical_crosscheck.json: separate installed NumPy/SciPy calculation compared
  with the standard-library results. Not a metafor test or production replay.
- FINDINGS.md / SOURCES.md / screening_sample.json: findings and external checks.

## Limits

Live-page and raw-container network retrieval attempts failed. The GitHub
connector supplied the pinned documents. Full review.json was not acquired.
Canonical review/HTML/certificate hashes were not regenerated. No complete
repository checkout/replay, production screening run, production D5 run, G1
predicate execution, or full trial-universe validation occurred. No visual PDF
inspection is claimed; original abstracts/HTML and repository records were used.
