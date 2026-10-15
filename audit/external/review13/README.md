# Topic 13 external audit — DOACs versus warfarin in AF

Audit date: 9 October 2026.
Repository: `mahmood726-cyber/meta-harness`.
Pinned reference: `0730234d0b4f`.
Review: `noac-vs-warfarin-af-stroke`.
Review SHA-256 identity (checked for agreement, not recomputed):
`e6ee5e700c0ad1b7e6966b5874f62118ad3822bdba0819b7dcde550707d28d23`.

## Verdict

The displayed primary efficacy arithmetic reproduces from its four displayed input
triplets. The review is not signed off: family eligibility contradicts record-level
population exclusions, selected-effect metadata is not consistently bound to the
selected analysis, and a harms absence state overstates what is absent.

The results are an external audit of pinned repository text, not proof that these
exact bytes were deployed at the audit time. The live web-tool retrieval exposed a
legacy identity. A cache response is not sufficient evidence of a deployment
regression.

## Run the checks

```sh
python -m pip install numpy scipy
python audit.py
```

`inputs.json` is a **manual transcription**, not a downloaded review-core JSON.
`audit.py` independently implements generic inverse-variance log-ratio pooling,
Paule–Mandel tau-squared, floored HKSJ t(k−1) intervals and the page's declared
prediction interval. It does not import or execute production harness code.

The script checks three user-supplied passage hashes, reconstructs the primary
calculation, supplies complete leave-one-out intervals, evaluates conversion of the
printed ENGAGE interval, and applies an auditor-proposed consistency invariant to
five manually transcribed screening contradictions. That last exercise is NOT a
production-gate test or a complete screening re-adjudication.

## Executed results

Primary: 0.8069362995, 95% CI 0.6610953782–0.9849504518.
Tau-squared: 0.0074060950; Q: 5.2099759404; I-squared: 42.41816019%.
Declared prediction interval: 0.5750749479–1.1322805729.
All three sampled passage hashes matched.

All four leave-one-out point estimates are below one, but all four HKSJ 95%
intervals include one. The t critical value also changes as the degrees of freedom
fall from three to two. This does not establish lack of benefit or identify an
invalid trial; it limits a robustness claim based on point estimates alone.

## Findings

### 13-01 — Conflicting family eligibility

The pinned family table labels all five of these ELIGIBLE, whereas the record-level
ledger excludes the same registry IDs for protocol-defined populations/settings:

- NCT02561897, ENTICED-AF: device procedures.
- NCT02942576, ELIMINATE-AF: catheter ablation.
- NCT04121767: thoracoscopic ablation.
- NCT05006287: early after cardiac surgery.
- NCT05540587, ERTEMIS: mitral stenosis.

These are trial-population/setting exclusions, not merely exclusions of duplicate
or protocol publications. They also enter the eligible-family missing-evidence
inventory. Removing these five while holding all other classifications fixed
changes the displayed eligible count from 12 to 7. That is not a definitive census
of seven eligible trials, and it leaves the four-trial efficacy pool unchanged.

Severity: changes a served number (eligibility count), not a demonstrated change
to the current efficacy estimate. This is the same failure class seen in topic 12.

### 13-02 — Incorrect RE-LY effect-type interpretation

The original RE-LY paper uses Cox regression for its reported relative risks.
The 0.66 estimate is therefore a Cox-derived relative hazard, not a reconstructed
cumulative participant risk ratio. Preserve the paper's literal label separately
from the canonical estimand. Relabelling this input does not alter the current
log-effect or variance, so it does not change the primary numerical pool.

Severity: changes served wording / effect metadata.

### 13-03 — Metadata bound to another analysis or outcome

ROCKET-AF's extracted 0.88 (0.74–1.03) belongs to its ITT analysis. The metadata
instead derives per-protocol status from an earlier methods sentence and describes
the four-trial pool as mixed ITT/per-protocol.

ARISTOTLE's major-bleeding row contains the stroke/systemic-embolism efficacy
endpoint as its endpoint-definition witness. The bleeding effect triplet itself
is correctly reported in the original abstract.

Severity: changes served wording / analysis metadata. No change to either verified
triplet is established by this finding.

### 13-04 — Harms reported versus tuple not held

The RE-LY abstract reports major bleeding but the rejected row is assigned an
outcome-not-reported state. Not possessing an admissible held effect/CI tuple is
different from the source not reporting the outcome.

The publicly readable original paper's Bleeding section additionally supplies the
150-mg estimate 0.93 (95% CI 0.81–1.07). Its Statistical Analysis section provides
the Cox interpretation. This identifies a primary-source repair candidate, not an
automatically admitted row and not permission to restore a class-level harms pool.

Severity: changes served wording and the evidence-status record.

## Acknowledged ENGAGE issue: do not count as new

The original ITT efficacy estimate is 0.87 with a printed 97.5% CI 0.73–1.04.
The pinned page serves converted 95% limits 0.745–1.016. Under a log-Wald
interpretation, the printed bounds imply SE approximately 0.0789531 and converted
95% limits 0.7452710–1.0156037. This is an approximate reconstruction from rounded
printed numbers, not recovery of the exact original unrounded SE.

The pinned D16 decision (8 October 2026) already acknowledges the D7 policy conflict:
search for a printed compatible 95% interval first; a narrow exception is conditional
and not yet applied in that snapshot. This audit does not certify completion of the
D16 search or approval of that exception. Do not substitute an on-treatment,
renal-subgroup or different-composite estimate just because its CI is printed at 95%.

Using the unrounded converted limits yields 0.8069714 (0.6611432–0.9849649).
This immaterial rounding difference is not a separate substantive numerical defect.

## G1 / IPD comparator

The pinned G1 record refers to comparator PMID 34985309 and four matched pivotal
families. The comparator reports HR 0.81 (0.74–0.89) for standard-dose DOACs versus
warfarin. Its patient-level trial-stratified Cox/network analysis differs from the
harness's aggregate PM/HKSJ calculation. Numerical proximity does not establish
independent corroboration or validate the separate eligibility inventory.
The G1 eligible count refers to its comparator universe and should not be confused
with the family-screening universe.

## Limits

- No whole-review SHA-256 or HTML SHA-256 independently recomputed.
- No full offline repository replay, build, publication gate or screening pipeline executed.
- `review.json` content was not acquired successfully through the connector.
- Raw file acquisition failed; pinned HTML, certificate portions, G1 JSON and selected
  source modules remained readable through the GitHub connector.
- Not all 35 screening records or 33 family classifications were independently re-adjudicated.
- Some direct registry URLs returned HTML shells; papers, indexed primary registry
  material and sponsor records supplied checks where available. No claim to have
  downloaded every live registry JSON is made.
- No claim of a completed systematic search or quantitative validation of all risk-of-bias gates.
- No repository or deployed page was modified.

## Files

- `audit.py`: independent executable checks.
- `inputs.json`: transcribed inputs and user-provided sample passages.
- `results.json`: executed numerical results and scope flags.
- `execution_log.txt`: output from the successful run.
- `sources.md`: pinned paths and primary-source locations.
- `requirements.txt`: dependencies.
