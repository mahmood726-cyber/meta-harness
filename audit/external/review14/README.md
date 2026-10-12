# Topic 14 — sacubitril/valsartan HFrEF audit

Audit date: 9 October 2026. Repository reference: `0730234d0b4f`.

review_sha256: `312aa902b8209842bc5aa3ebcf1c9a349f5eb1d109886e5558d1eecde967de67`

## Verdict
The two extracted primary efficacy results agree with their original publications at published precision. The quarantined PM/HKSJ analysis is numerically reproducible. The page follows its stated small-k withholding rule, but its screening, endpoint metadata and current-state descriptions are not mutually consistent. Do not treat this as a signed-off complete meta-analysis or an independently verified live deployment.

## Run
`python -m pip install -r requirements.txt`

`python audit.py`

The program has no network access and does not modify a repository. It reproduces two passage digests; independently calculates the diagnostic two-study synthesis and heterogeneity; and compares two manually transcribed eligibility sets. Dependencies and the actual execution environment are recorded in results.json.

## Files and provenance
- inputs.json: MANUALLY TRANSCRIBED values/passages and membership sets from the supplied pack and pinned HTML; not the complete review object.
- audit.py: independent numerical implementation, not copied production harness code.
- results.json and execution_log.txt: outputs of the executed local check.
- findings.md: one finding per record with source URLs and scope.
- sources.md: source-access notes and references.
- FILES_SHA256.json: digests of files in THIS AUDIT BUNDLE, not the website certificate or original research corpus.

## Limits
The pinned page and certificate agree on the review identity; the complete canonical review, HTML and certificate digests were not recomputed. The full review.json could not be acquired through the available path. No offline harness rebuild, original production-gate test, or full screening census was executed. Container raw-file acquisition encountered DNS failures; pinned HTML/code text was available through the GitHub connector. The live-page lookup yielded a different older identity and is not a verified live-byte measurement.

The first trial estimate was checked against the original report. PARALLEL-HF's original published result (1.09, 0.65–1.82) corroborates the registry-origin tuple to publication precision, not its final decimal digits. Live registry structured results were not independently acquired. The PARALLEL-HF HTML article was readable; PDF screenshot attempts failed. No successful visual PDF-table inspection is claimed.

## Interpretation
The reconstructed HR 0.83664 (HKSJ interval 0.21082–3.32020) is an audit-only counterfactual for the TWO HELD ROWS. It is not a recommended replacement review result. The common-effect calculation is diagnostic only. Neither calculation resolves incomplete evidence, policy choice, clinical heterogeneity or admissibility. Opposite point estimates do not themselves establish opposing true effects. The nonsignificant Q test does not establish homogeneity.
