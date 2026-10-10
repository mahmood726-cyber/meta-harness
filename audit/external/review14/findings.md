# Findings register — topic 14

Every finding below applies to review_sha256 `312aa902b8209842bc5aa3ebcf1c9a349f5eb1d109886e5558d1eecde967de67`, repository ref `0730234d0b4f`, not a verified current deployment.

Pinned page: https://github.com/mahmood726-cyber/meta-harness/blob/0730234d0b4f/docs/reviews/sacubitril-valsartan-hfref/index.html

## 14-01 — Equal eligibility counts conceal different trial sets
Tabs: Protocol, Screening, Included studies.
Page: family table marks NCT06142383 (XXB750) ELIGIBLE. Its overall study masking is DOUBLE, but this does not establish masking of the selected sacubitril/valsartan contrast. NCT04853758 (ANSWER-HF) is UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED in the family table while the record-level ledger includes it. Both sets contain seven families; six are common.
Source: XXB750 original abstract states the sacubitril/valsartan allocation was open-label, while XXB750/placebo allocations were blinded. The participants were already on ACEI/ARB background; therefore a placebo label alone is NOT evidence that there was no active-RAS comparator. The decisive confirmed exclusion is failure of the double-blind contrast criterion.
https://pubmed.ncbi.nlm.nih.gov/41912806/
Source: ANSWER-HF original abstract establishes double-blind randomisation, sacubitril/valsartan versus enalapril, and adults with Chagas cardiomyopathy and HFrEF. A different primary endpoint does not exclude the trial under this protocol's P/I/C/design-only rule.
https://pubmed.ncbi.nlm.nih.gov/41396086/
Severity: changes served wording and screening/membership records; intermediate counts change when either correction is applied alone. No demonstrated change to the currently extracted efficacy numbers. Do not claim seven is the final independently validated census.
Repair: judge population and masking for the actual comparison; propagate one adjudicated family state. Check membership IDs, not only aggregate counts.

## 14-02 — PARALLEL-HF report remains disconnected and incorrectly design-excluded
Tabs: Protocol decisions, Screening, Included studies.
Page: D13 records the signed PMID 33731544 -> NCT02468232 identity link. Nevertheless, the main family table gives the registry no publication, the article remains a separate REGISTRY_PARENT_UNRESOLVED candidate, the record is excluded X-DESIGN, and the included-trial PMID is missing.
Source: the original PARALLEL-HF article identifies the trial and its double-blind design.
https://www.jstage.jst.go.jp/article/circj/85/5/85_CJ-20-0854/_html/-char/en
Severity: changes served wording/provenance and screening records; resolving this one candidate would locally reduce unresolved report candidates from 27 to 26. Does not add another independent trial or change the current primary inputs.
Qualification: D13 is documented as a G1 identity mechanism. This finding is failure to reconcile that established identity with the main review, not a claim that its G1-specific implementation was executed and failed.
Repair: link the report to its family and correct its design disposition. Preserve report-level and trial-level counts separately.

## 14-03 — Outcome identity differs between the selected estimate, alternatives and RoB signals
Tabs: Results & conclusions; Risk of bias & GRADE.
Page: PARALLEL-HF's selected HR is the first-event primary composite, yet D5 describes a prespecified secondary total/recurrent-event composite. A separate alternative with an additional outpatient-worsening component is labelled EXACT_TARGET although it is explicitly not pooled. PARADIGM-HF D5 raises a possibly post-hoc/unregistered signal because the string matcher failed to find a registry outcome match.
Source: original PARALLEL-HF article distinguishes its first-event primary endpoint from recurrent-event and broader composites. The original 2013 PARADIGM-HF rationale/design article pre-specifies the composite of CV death and HF hospitalisation before results.
https://www.jstage.jst.go.jp/article/circj/85/5/85_CJ-20-0854/_html/-char/en
https://doi.org/10.1093/eurjhf/hft052
Severity: changes served wording and endpoint/RoB metadata; no demonstrated wrong primary HR. Formal RoB 2 is explicitly unassessed on the page, so these are incorrect machine signals, not a completed formal judgement overturned by this audit.
Repair: use a shared outcome definition with event handling, components, timepoint and analysis population. Failed automated matching should remain unresolved, not be converted into evidence of post-hoc outcome selection. Do not substitute a broader or recurrent-event estimate to avoid a refusal.

## 14-04 — Current comparator narrative still describes an obsolete one-trial state
Tab: Comparison with published meta-analysis.
Page quote: “k=1 CONTRIBUTING”; “PARADIGM-HF supplies the only EXTRACTABLE primary-outcome estimate here”; “6 are declared absent”. The current extracted data contain both PARADIGM-HF and PARALLEL-HF, five declared-absent rows, and no served primary pool. This paragraph is not explicitly labelled superseded; a different old report-flow block is explicitly labelled superseded and is NOT counted as this finding.
Source: internal comparison of the same pinned page's extraction/results sections with its comparator-resolution paragraph.
Severity: changes a served number (descriptive counts only) and wording; not an efficacy-estimate change.
Repair: generate the current comparator narrative from current trial membership and analysis state, or explicitly date and label the paragraph as historical.

## Rechecked methodological issue — small-k policy
The pinned policy withholds the pool when two point estimates straddle the null OR two confidence intervals do not overlap. Here only the first condition is true. Both intervals overlap from 0.73 to 0.87. The independent Q test gives p approximately 0.249. That does not prove homogeneity, but it also does not support presenting opposite point estimates as established opposite treatment effects. The broad quarantined HKSJ interval is numerically correct. No recommendation is made to restore this incomplete pool or switch models because one interval excludes the null.
Policy source: https://github.com/mahmood726-cyber/meta-harness/blob/0730234d0b4f/harness/k2.py

## Existing limitation still visible — PIONEER-HF scope
The pinned protocol and main screening include PIONEER-HF, while an old harms-refusal note excludes its acute setting from a purported chronic-only review. This is retained as an unresolved scope inconsistency, not represented as a newly discovered trial or an automatically admissible missing effect. Generic incomplete search, absent D11 sign-off and replay limitations were already disclosed; not counted as novel findings.

## Supplied screening sample
- PMID 25176015: include supported by original double-blind randomised comparison.
- PMID 40689605: X1 exclude as an independent trial supported; publication is a meta-analysis.
- PMID 40100325: X1 exclude supported; nationwide longitudinal observational dose cohort (not REAL.IT).
- PMID 36315602: X1 exclude supported; mechanistic review.
- PMID 27206819: X1 exclude supported; practice guideline.
These five supported decisions do not validate the complete screening census.
