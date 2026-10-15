# Topic 27 external audit — metformin added to clomifene for PCOS ovulation

Audit date: 10 October 2026. Repository reference: `0730234d0b4f`.
Review hash recorded in the inspected certificate:
`531b64bc578443ae91b79c80c3d3bd87670ba038d6fb657a13e11804ffbd149d`.
Status remains **ABANDONED_BY_DECISION**.

## Run

From this directory, using Python 3.10 or later:

```sh
python audit.py
# An alternative output path:
python audit.py --output checked-results.json
```

No network access or third-party Python packages are required. The diagnostic
statistics implementation is deliberately limited to 2–4 positive-cell studies.
It does not implement a general-purpose clinical evidence synthesis engine.

## Files

- `inputs.json`: manually transcribed pinned/source inputs with their origins,
  exact displayed passage strings and hashes, and separately labelled candidate
  analyses. This is NOT the repository's complete `review.json`.
- `screening_ids.txt`: one manually transcribed displayed screening record per
  line. Some registry IDs have acronym prefixes; the sampler uses the last token.
- `screen_excerpt.py`: isolated lexical helper transcriptions from the pinned
  code. The fixtures are short source-informed paraphrases, not full records.
- `audit.py`: independent log-OR, Paule–Mandel, floored-HKSJ calculations, passage
  digests, seeded sample, manual family-set reconciliation and isolated fixtures.
- `results.json`: executed results and each check's name and outcome.
- `FINDINGS.md`, `SOURCES.md`: interpretation and source/acquisition qualifications.

## What was checked

The current three-input arithmetic and three displayed passage hashes reproduce.
A synthetic lexical test diagnoses the missing bare-placebo term. Manual family
IDs show the local removal of two IVF families from an eight-family eligible list.
The current primary pool does NOT contain the retracted Kazerooni paper.

Legro's per-woman candidate is computed by complementing explicitly reported
counts with no documented ovulation: 209−35=174 and 209−52=157. This is not the
cycle-level ovulation rate, not a printed OR, and not an admitted harness row.
Moll's side-effect-discontinuation candidate uses 18/111 versus 6/114; it is also
an auditor-derived, single-trial diagnostic, not a reinstated safety result.

## Important limits

This is not a full repository replay, G1 run, licence-guard test, production
screening run, complete literature search or formal risk-of-bias assessment.
Canonical review/certificate/HTML hashes were not regenerated. Recorded identity
agreement was checked, not a new deployment attestation. The live-page fetch
failed; complete review JSON was not acquired. Long HTML sections were inspected
through connector resources; the sample order and family IDs are manual fixtures.

Ben Ayed's counts remain conditional on the reported equal allocation and rounded
rates; an independent complete original table was not acquired. Moll's efficacy
counts were checked against original Table 2; its discontinuation counts are in
the Results narrative, NOT Table 2. The cached Moll XML lacks the article body,
so it does not supply that safety numerator evidence. Its availability on a web
page does not automatically satisfy the harness's separate source-licensing rules.

The Kazerooni retraction was published 24 September 2026, after the recorded
September retrieval/integrity-check dates but before the October audit pack.
The historically dated earlier check is not retrospectively labelled false.
Correct the current integrity disposition and keep the study excluded.

No journal PDFs, font files, restricted full articles or repository modifications
are included. No visual PDF inspection was performed or claimed.

Passing the 24 checks verifies the calculations and named fixtures only; several
tests deliberately reproduce wrong classifications. They are not 24 independent
clinical validations and do not certify all trial eligibility decisions.
