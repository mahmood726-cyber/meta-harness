# Finding register — topic 18

Applies only to review SHA-256
`57e56790d978ea3d9bde6bc86021e9c6fb17d284d8eae5e8072c2398375f5127`
at reference `0730234d0b4f`.

## 18-01 — Selected endpoint correction did not propagate to its D5 evidence and notices

**Tabs:** Results, Risk of bias & GRADE; `harness/rob2.py`.
**Severity:** changes served wording/metadata; no demonstrated error in the two currently pooled effect triplets.

The extraction selects DAPA-HF's secondary cardiovascular-death/HF-hospitalisation first-event estimate, HR 0.75. Its stored definition explicitly says Secondary. An older definition-audit notice still says the pool includes the urgent-HF-visit component. D5 further says the pooled outcome matches the registered primary, citing a title that includes urgent visits. The excerpt test shows that urgent visits disappear from the component representation and both titles are therefore returned as matching. The synthetic unstable-angina extra-component control is correctly rejected.

The Results tab also lists recurrent-hospitalisation/CV-death alternatives as EXACT_TARGET while explicitly not pooling them. This is additional endpoint-selection metadata risk, not proof that a recurrent-event result entered the current pool.

**Correction:** bind metadata and D5 evidence to the actual selected secondary outcome; preserve event components and first-versus-recurrent handling. Do not automatically downgrade bias merely because a prespecified secondary outcome is selected. Retain the verified 0.75 input.

## 18-02 — Unsupported current-row claim of two identical abstract re-extractions

**Tab:** Reproduce.
**Severity:** changes served wording/assurance status.

The page says both current pooled numbers are abstract-checkable and that both independent abstract extractions are identical. The current DAPA-HF narrow tuple is absent from the primary abstract, which gives the broader primary HR 0.74. EMPEROR-Reduced's tuple is in its abstract. Therefore a statement of 2/2 identical abstract confirmations does not describe the current selected rows.

This audit did not execute the harness's blind extractor and does not establish precisely when the assurance record became wrong or stale. The original paper/registry can support the selected secondary estimate, but that is a different acquisition and confirmation claim.

**Correction:** refresh confirmation per selected row and actual source, retaining endpoint and input identity, rather than carrying an earlier abstract-status summary across a changed extraction.

## 18-03 — Family-level eligibility disagrees with record-level inclusion and outcome inventories

**Tabs:** Screening, Included studies, Results, Manuscript.
**Severity:** changes served wording and eligibility inventories; reconciled counts require adjudication.

NCT04304560 and NCT06229678 are included in the record ledger but INELIGIBLE in the family table, citing AACT conditions. NCT04385589 is included in the ledger but UNKNOWN/PLACEBO_CONTROL_NOT_PROVEN in the family table. All three are nevertheless listed as eligible-but-absent in current outcome/manuscript text.

NCT04304560's held record identifies HFrEF plus type 2 diabetes. The written protocol excludes diabetes-only populations, not HFrEF merely because patients also have diabetes; `screen_entry.population_exclusion` explicitly allows that distinction. Its family rejection therefore requires correction or an explicit different source-backed reason. The final clinical eligibility of NCT06229678 was not established here; do not use this audit to promote it automatically without checking its detailed EF criteria and contrast. No definitive replacement family census is claimed.

The historical selection-flow table is clearly labelled superseded and is NOT the subject of the finding. The conflict persists in current labelled outputs.

## 18-04 — An insulin comparator override does not establish placebo control

**Tabs:** Protocol, Screening, Included studies; topic configuration.
**Severity:** changes served wording/eligibility reasoning; no demonstrated change in the current efficacy pool.

The written comparator is placebo. The configuration contains a named comparator override accepting insulin for NCT04385589, and the ledger renders it as an eligible double-blind/placebo-controlled comparison. The original publication (Ibrahim et al., 2020; DOI 10.3389/fcvm.2020.602251) describes dapagliflozin with insulin if needed against insulin-based control treatment, with furosemide and conventional HF therapy. It does not establish matching placebo administration in the described regimen. The held registry-derived family labels say Placebo group and the cached masking field says DOUBLE, creating a source discrepancy rather than sufficient proof that insulin is placebo.

The report explicitly gives NCT04385589. Yet the page's family table records no publication and the extraction says source not retrieved. Link and adjudicate the report; do not count it as another independent trial.

**Correction:** replace the named eligibility shortcut with a source-backed contrast/blinding decision, preserving any unresolved registry/publication disagreement. Do not admit insulin as an interchangeable comparator, and do not manufacture a cardiorenal-event HR from short-term diuresis outcomes.

## Confirmed / retained

Both efficacy triplets and passage hashes are supported at the levels tested. The pooled point HR 0.75 and normal common-effect sensitivity 0.680771–0.826269 reproduce. The HKSJ 0.400305–1.405180 interval is diagnostic and already withheld by policy. This finding does not authorise a class-level harms result or alteration of G1 status.

ERTU-SODIUM uses ertugliflozin, outside the written protocol's explicit dapagliflozin/empagliflozin restriction. Its exclusion is not a false negative merely because the review title says SGLT2 inhibitors. Better wording would identify the out-of-scope agent.

## Priority

First connect all labels, risk-of-bias evidence and second-extraction status to the selected outcome. Then reconcile one source-backed family eligibility decision across screening and outcome inventories. Resolve the insulin-control discrepancy through the original report and registry, not a named drug-word override. Rebuild and run the real offline replay afterward; that replay was not performed here.
