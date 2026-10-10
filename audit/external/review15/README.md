# Topic 15 audit — semaglutide and MACE in obesity without diabetes

Audit date: 10 October 2026.

Repository: `mahmood726-cyber/meta-harness`
Pinned reference: `0730234d0b4f`
Review: `semaglutide-obesity-mace`
Recorded review SHA-256:
`b3e40a3d206ff265345fd40a0e0a37136e86912150d7779a0b2ad3311acd4de0`

## Verdict and scope
The displayed SELECT primary HR agrees with the original report, both supplied
passage digests match, and the count-derived discontinuation RR/CI reproduces.
These checks do not validate search completeness, all family decisions, the
complete manuscript, or the production publication pathway.

The principal findings are a false population exclusion of a SELECT companion
report, known population evidence not propagated into structural family states,
and unsupported completeness/scope statements in the comparator narrative.
No new independent eligible RCT was established, and no correction to the
currently displayed primary HR is proposed.

## Files
- `audit_checks.py`: standard-library independent checks, executable offline.
- `inputs.json`: explicitly labelled manual transcriptions, including both
  user-supplied/source-checked passages and the displayed 66-record ID ledger.
- `results.json`: output from the executed checks.
- `findings.md`: detailed findings, corrections, and qualifications.
- `sources.json`: pinned repository paths and original scholarly sources.
- `build_inputs.py`: convenience script that recreates the input fixture.

Run:
```sh
python audit_checks.py
```

## What was executed
1. UTF-8 SHA-256 calculation on each supplied passage.
2. Independent risk-ratio and log-Wald interval calculations from arm counts.
3. A diagnostic crude MACE RR/OR calculation, NOT a Cox-HR reconstruction.
4. An isolated positive whole-token title-alias check for the companion report,
   including a diagnostic title fixture with the word "but" removed.
5. Counts/set membership of the manually transcribed family and record-ID fixtures.

## What was not executed
No complete `review.json` was acquired. The GitHub content action returned no
content for that large file, and a raw connector fetch failed. No complete
review, HTML or certificate hash was regenerated. Agreement of recorded review
identities is not independent canonical-hash verification.

No `reproduce_review.py`, full `screen_record`, production gate, model-call
replay, or full registry JSON verification was run. The title test is deliberately
an isolated reproduction of the positive lexical branch, not a full re-execution
of the pipeline or an exact copy of its synonym and negation machinery.

The 66-record fixture was manually transcribed from the pinned rendered ledger.
Absence of PMID 39948761 from that fixture does not prove absence from every
repository cache or a different build. Four family rows were inspected, but only
SELECT and SUSTAIN-6 received source-based population adjudication here. Not all
66 screening records or all unresolved candidate reports were independently
readjudicated. No new systematic search or exact-PICO exhaustive census was
completed. No source article was assessed through a claimed PDF screenshot.

No repository, website, email or external file was modified. The ZIP is an
auditor-created diagnostic bundle, NOT an original harness evidence bundle.
