# Topic 19 audit — SGLT2 inhibitors and HF hospitalisation

Audit date: 10 October 2026. Pinned repository reference: `0730234d0b4f`.
Review: `sglt2-primary-prevention-hf`.
Recorded review SHA-256: `35134b4721fd1704c29aef2277a726d3bf3f12b3ca3e538d2a4c92004429fcbd`.

## Verdict
The four selected first-HF-hospitalisation HR inputs are supported by original trial reports. The independent PM/floored-HKSJ calculation reproduces the pinned manuscript at its printed precision: HR 0.70 (95% CI 0.58–0.84). All three sampled passage hashes match.

A confirmed inconsistency remains in the pinned comparison artifact. Its `in_our_pool` list has five reports and includes PMID 28284707; the current forest plot has four inputs and does not include that report. The original PMID 28284707 is an analysis pooling baseline-HF participants from five clinical trials, not one additional independent CVOT. This audit does not establish that the currently served four-input numerical pool contains it.

## Run
Python 3.10+ and scipy are required. Run `python audit_topic19.py` from this folder. The script writes `audit_results.json` and `inputs_and_passages.json`. The saved `execution_log.txt` was produced by an actual execution.

## What these files prove
- Independent log-HR inverse-variance calculations from manually transcribed printed triplets.
- Paule–Mandel tau-squared and a modified Hartung–Knapp interval with the variance factor floored at one.
- SHA-256 identity of the three passages supplied in the user's audit pack (HTML numeric entities decoded in the transcription).
- A set comparison between manually transcribed forest-plot input IDs and G1 `in_our_pool: true` IDs from the pinned files.
- Leave-one-out calculations as a diagnostic, not a completed sensitivity audit of the repository.

## What they do not prove
No complete review JSON, canonical review hash, certificate or HTML hash was regenerated. This is not the production harness, a full repository replay, a G1 predicate run, or a fresh systematic search. Input HRs cannot be independently reconstructed from individual participant data because no IPD was obtained. Some long HTML sections and the live page could not be acquired. Not all 294 screening records were re-adjudicated; in particular the exact original NCT03190798 registry record could not be independently obtained. No repository or website was modified.

## Confirmed finding 19-01
Component: `outputs/k_gap/g1/sglt2-primary-prevention-hf.json`, at the same pin as the review.

The G1 header records `k_in_our_pool: 5`, `k_ours_total: 5` and `k_matched: 5`. Its Kosiborod row for PMID 28284707 records `in_our_pool: true`, `g1_countable: true`, and `agreement_with_comparator_row: AGREE`. Its cached outcome representation is a participant-count RR, whereas the four served inputs are HRs. The current manuscript and forest plot list only PMIDs 28605608, 26378978, 32966714 and 30415602.

Severity: **record only for the inspected comparison artifact**. Rebuilding or historically labelling this file may alter descriptive comparison counts. No change to the current pooled efficacy number is established. Do not automatically include the fifth report to make these files agree, and do not claim that the mismatch establishes a full G1 status change.

The proposed invariant is that a current `in_our_pool` claim must resolve to a current analysis input, including its report/family identity and effect type; stale historical comparisons must instead identify their own reference analysis and version.

## Sampling notes
- PMID 22517736: ADA/EASD management position statement; X1 supported.
- PMID 30652541: report on a federated real-world-data research platform; X1 supported.
- PMID 23573151: uncontrolled eight-week diet intervention; X1 supported.
- PMID 24336217: animal-/plant-diet microbiome intervention, outside the SGLT2 question; final exclusion supported, exact randomisation-based X1 rationale not fully adjudicated.
- NCT03190798: exact original registry response not acquired; no independent sign-off of its stated exclusion reason.

## Source-report navigation
CANVAS's supplied passage is from PMID 29526832, although the row is keyed by primary-report PMID 28605608. EMPA-REG's supplied passage is from PMID 26819227, although its row is keyed by PMID 26378978. The inspected verified-effects cache explicitly identifies the companion sources. This is not evidence that the source text is absent or invented. A practical audit-pack improvement is to display both trial/report identity and the actual passage-source link.
