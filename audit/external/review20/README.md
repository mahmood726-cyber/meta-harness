# Topic 20 independent audit — 10 October 2026

Review: `spironolactone-hfref-mortality` at `0730234d0b4f`.
Recorded review identity: `ea6d5d8ee6d60ae9d3217a3d2349c7231fcfa3cab01bcd2e022a94fd24d9cea9`.

## Re-run

```sh
python -m pip install -r requirements.txt
python audit.py
```

The script has no network calls and does not modify a repository. It writes local
`results.json`. The supplied execution log and results were produced by running it.
All seven self-checks passed. Numerical inputs and the three audit-pack passage
strings were manually transcribed, not exported from production review.json.

## Findings

The published efficacy calculation is reproduced to the precision shown in the
pinned manuscript: 0.88 (0.29–2.63), with prediction interval 0.12–6.63 under the
specified t(k−1) convention. This is not independent reconstruction of a trial's
Cox model from individual participant data.

20-01: the RALES effect-type label confuses publication terminology with the
statistical model. Its canonical estimate is a Cox hazard ratio; the current
mixed HR/RR description and the G1 measure-only incompatibility need correction.
This relabelling does not alter any input triplet or the pooled calculation.

20-02: J-EMPHASIS-HF's configuration retains a reconstructed-RR source label,
whereas the actual current input is its reported ITT Cox HR. The incorrect
configuration annotation is established; a separate wrong rendered consumer is
not established by this audit.

20-R1: original EMPHASIS-HF full-text data permit a laboratory-threshold safety
extraction unavailable from the abstract. This is a recovery opportunity, not
proof that the existing abstract-specific refusal is false. The reconstructed
risk ratios in results.json are auditor diagnostics and have not been admitted
to the harness. Laboratory thresholds, investigator-reported hyperkalemia,
serious events, and hospitalization are not interchangeable outcomes.

## Numerical scope

`audit.py` independently implements inverse-variance log-ratio pooling,
Paule–Mandel heterogeneity estimation, a floored HKSJ confidence interval, and the
review's prediction-interval convention. It derives standard errors from rounded
printed confidence limits. It also calculates crude participant-risk diagnostics,
which are explicitly NOT replacements for reported mortality HRs.

The leave-one-out k=2 intervals are auditor diagnostics. The harness has its own
k=2 publication rule; this script does not apply or validate that rule. The common-
effect sensitivity is not offered as an alternative primary result.

## Inspection and acquisition limits

- The canonical review hash, HTML hash and certificate release hash were not
  regenerated. Agreement of recorded identities is all that was checked.
- Complete review.json was not acquired. The connector returned empty content.
- Long minified HTML sections could not be completely extracted. A read-only
  browser attempt ended without verified content. Do not infer any missing tabs.
- The live page fetch failed at the retrieval tool; that does not establish that
  the deployed site is broken or matches this historical version.
- No full production screening, G1, gate or offline replay was executed. Five
  sampled exclusions were checked, not the full 226-record ledger.
- EMPHASIS-HF printed pages 18 and 20 were visually checked. RALES and
  J-EMPHASIS-HF PDF screenshot attempts failed; RALES used parsed text and
  J-EMPHASIS-HF also used the original publisher HTML.
- Publicly accessible PDF mirrors do not establish open-access licensing for the
  harness's D8 admission policy. Licence review and source binding remain necessary.
- No original journal PDFs, full articles, fonts or repository clone are included.
- No repository, clinical record or live website was modified.

## Files

`inputs.json`: manually transcribed inputs and user-supplied passage strings.
`audit.py`: executable independent checks.
`results.json`, `execution_log.json`: executed outputs.
`manual_inspection.json`: inspected labels, G1 fields and screening sample.
`findings.csv`: findings and repair classification.
`sources.json`: source locations and actual acquisition scope.
`requirements.txt`, `environment.json`: execution environment.
`SHA256SUMS.txt`: integrity list for the deliverable files, NOT review certification.
