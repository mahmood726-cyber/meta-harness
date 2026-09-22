# Lane ACK — unsigned enforcement-gate acknowledgement drafts

Completed the requested audit against base `38c04411` and ratchet floor `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`: **232 of 232 lost-block pairs**, **25 of 25 heading classes**, **12 of 12 marker decreases**, and **1 of 1 requested GLP-1 parity entry**. The pairs span 26 of 33 served HTML pages (the index and 25 of 32 review pages); 128 of 232 losses are from the direct base and 104 of 232 are historical-floor losses. The supplied pair listing matches this extraction.

`reasons_gate.json` contains reasons for **19 of 25 classes / 186 of 232 pairs**. The other **6 of 25 classes / 46 of 232 pairs** are **UNEXPLAINED for acknowledgement purposes** and have no reason entry. A mechanically traced regression is still not an acceptable replacement. All 12 of 12 marker decreases are accounted for, but 1 of 12 is expressly UNEXPLAINED and must not be signed. `parity_ack_gate.json` is a standalone unsigned entry to append only after integrator review; `marker_reasons_gate.json` is a list. `_by` remains the literal `TO_BE_SIGNED_BY_INTEGRATOR`.

No commit or signature was made. `docs/ratchet_acknowledgements.json`, served files and source files were not edited. The ratchet remains REFUSED: drafts are not authorization, and OPEN result-change notices are not reviewer countersignatures. The finish condition here is the completed audit and these draft artefacts, not a ship or gate-PASS claim.

**Measured landing scope.** Primary rows changed from 87 of 87 to 34 of 87 retained (53 of 87 set aside); all outcomes changed from 127 of 127 to 46 of 127 retained (81 of 127 set aside). Of the 81 of 81 set-asides, 80 of 81 are UNKNOWN and 1 of 81 INELIGIBLE. Primary pools emptied on 11 of 32 topics. All 41 of 41 newly added result-change notices are OPEN; 54 of 54 total notices include 13 of 54 pre-existing notices. Admission evaluates 2 of 14 named predicates (P5/P8); the other 12 of 14 are explicitly outside its in-build scope, and retained unbound_legacy rows are separately labelled migration state.

**Prompt correction.** HARMONY / PMID 30291013 is associated with `NCT02465515`, not the prompt’s `NCT02692716`. The working page, declared-absent admission record, cached HARMONY publication and certified family map agree on NCT02465515 / UNKNOWN; the page and admission verdict name ENTRY_POPULATION_NOT_ESTABLISHED. NCT02692716 is PIONEER 6 / PMID 31185157, ELIGIBLE and still pooled. The parity draft explicitly records both facts instead of repeating the incorrect identifier. The comparator_trial_set object is unchanged, including its 8 of 8 source-enumerated labels; the comparable same-scope count remains 7 of 8. The inherited overlap.shared_k still counts HARMONY among its 7 shared labels, so the index-wide parity block is separately withheld as stale even though the specific relation transition is explainable.

| Item | Static or dynamic | Evidence / limitation |
|---|---|---|
| Base, floor, heading extraction and requested file schemas | Static audit configuration | Exact prompt and read_pairs.py head function, including truncated heading keys and the trailing space in the verification-banner key |
| Page text, SHA-256 digests, marker counts and memberships | Dynamic local reads | git show, harness.honest_ratchet.blocks/inventory, working HTML and review.json; no simulated evidence or recomputed clinical estimates |
| Eligibility and comparator identifiers | Held source-backed fields | Admission records, cached publication, page family table and docs/cache/glp1-ra-mace-t2d/families.json; no eligibility adjudication performed by this lane |
| Reasons and UNEXPLAINED decisions | Authored after full-text review | Interpretations tied to the displayed pairs and source conditions; not signatures or external verification |

**Class ledger.** Pages are out of 33 served pages; pairs are out of the 232 audited losses. Detailed pool counts, funding counts and full paired texts follow. A replacement_head is included only when the drafted target heading differs. For multi-outcome Admission at pooling blocks the integrator must use the named outcome, not the first matching block: DOAC’s k=2 loss is Any bleeding, and CAP’s mixed-estimand loss is Hyperglycaemia.

| Class | Pages | Pairs | What changed | Reason drafted / UNEXPLAINED |
|---|---:|---:|---|---|
| `We measured our own error rate` | 1 of 33 | 1 of 232 | Admission set aside 81 of 127 previously pooled trial-outcome rows, leaving 46 of 127; the live NOT_INDEPENDENTLY_RECHECKED subset changes from 24 of 127 to 6 of 46 (18 of 24 such rows left). The historical blind-audit sample remains 99 of 99, with 95 of 99 re-extractable and 92 of 95 matching; neither an independent recheck nor a new accuracy claim was added by removing rows. | Reason drafted; same heading |
| `External validation` | 1 of 33 | 1 of 232 | Recalculation on the post-admission served estimates reduces comparable topics from 23 of 32 to 15 of 32: same-estimand 13 of 23 -> 9 of 15, cross-estimand 10 of 23 -> 6 of 15, with same-estimand agreement 8 of 13 -> 5 of 9, arithmetic replication 2 of 13 -> 1 of 9, and divergence 3 of 13 -> 3 of 9. This is a changed comparison population after admission withdrawals, not newly validated trials; the separate historical Cochrane example and small-k prose are unchanged. | Reason drafted; same heading |
| `Every pooled number is verified against ` | 1 of 33 | 1 of 232 | The digit-location census changes from 127 of 127 pooled trial-outcome rows to 46 of 46 because admission set aside 81 of 127 rows on family eligibility before pooling. The replacement retains the located-is-not-correct warning and both 2 of 2 previously named wrong-endpoint withdrawals; digit location does not establish PICO eligibility or independent accuracy. | Reason drafted; same heading |
| `Corpus currency` | 1 of 33 | 1 of 232 | The corpus remains 0 of 32 current and 32 of 32 STALE, while admission withdrawals expand the named unpooled-family reasons and loss of remaining outcomes adds no_checkable_claim; the audit-versus-screen conflict is newly named on 5 of 32 topics. The protocol/config inventory remains 35 divergences across 18 of 32 topics, and the new banner records unresolved evidence rather than a currency improvement. | Reason drafted; same heading |
| `Declared strands` | 2 of 33 | 2 of 232 | The index replaces the saved results of strands B and C with admission refusals (2 of 4 strands), but the entire topic-page strand block disappears (1 of 2 affected pages): its rendering is conditional on a suppressed-incompatible primary, now a single admitted trial. The topic page therefore loses all 4 of 4 strand descriptions and its cross-endpoint counterfactual; an index replacement is not a same-page replacement. No class-wide acknowledgement is drafted until the topic-page disclosure is restored or an explicitly equivalent same-page block exists. | UNEXPLAINED — no reason entry |
| `iv-iron HF-hospitalisation` | 1 of 33 | 1 of 232 | On the index, 2 of 4 saved strand results (B and C, each formerly k=2 of 2) become REFUSED on admission because AFFIRM-AHF/NCT02937454, FAIR-HF2/NCT03036462 and IRONMAN/NCT02642562 have UNKNOWN eligibility with INTERVENTION_CONTRAST_NOT_PROVEN; the 2 of 4 CONFIRM-HF single-trial strands remain. Both saved pooled intervals and their common-effect sensitivities are withheld while the existing cross-endpoint refusal stays visible; this draft covers the index wrapper only, not the unexplained disappearance of the topic-page strand block. | Reason drafted; same heading |
| `Gate scorecard` | 1 of 33 | 1 of 232 | The admission-enforcement gate adds 1 of 63 current gates and 2 of 133 events (one adjudicated plant and one unresolved production refusal): gate coverage 62 of 62 -> 63 of 63, adjudications 59 of 131 -> 60 of 133, plant validations 58 of 68 -> 59 of 69 plant events, unresolved events 72 of 131 -> 73 of 133 and adjudicated production refusals 1 of 16 -> 1 of 17. Independently adjudicated events remain 0 of 131 -> 0 of 133, and UNVALIDATED gates remain all 62 of 62 -> 63 of 63; this is enforcement accounting, not external validation. | Reason drafted; same heading |
| `Parity with the published comparator` | 1 of 33 | 1 of 232 | The GLP-1 change is attributable and separately drafted, but the whole index block is unsafe: probiotics displays 11 of 42 -> 16 of 42 against its comparator while actual primary membership is 11 of 11 -> 0 of 11 retained. Missing result.k values fall back to hand counts; noac still displays IDENTICAL_SET and 4 of 4 despite 0 of 4 primary rows retained, so the displayed 3 of 21 identical-topic total cannot be treated as a current set census. Spironolactone also changes inferred SUPERSET -> SUBSET (displayed 3 of 2 -> 1 of 2) and stale prose survives. This class is UNEXPLAINED as a defensible replacement, not a claim that its faulty code path is unknown. | UNEXPLAINED — no reason entry |
| `STALE` | 23 of 33 | 42 of 232 | All 42 of 42 lost STALE blocks on 23 of 32 review pages are replaced by the current STALE warning, with the admission set-asides represented as unpooled families and the newly blocked known-missing re-pools explicitly named as audit-versus-screen conflicts. No topic becomes current (0 of 32 before and after); ACK_REPORT.md records each page’s before/after missing-family counts and distinguishes 19 of 42 historical-floor predecessors from the 23 of 42 direct-base blocks. | Reason drafted; same heading |
| `ENGINE_CANNOT_CONSUME design variance` | 1 of 33 | 1 of 232 | Balanced-crystalloids primary membership falls from 2 of 2 base rows to 0 of 2 after PLUS/PMID 35041780 and BaSICS/PMID 34375394 fail admission; the standalone design banner is replaced by a DECLARED ABSENT design-refusal statement with no pooled number. All 3 of 3 prior design refusals (SMART, SALT, SPLIT) remain in the review and individually named on the page; the change does not establish a missing design-adjusted effect or ICC. | Reason drafted; replacement: DECLARED ABSENT |
| `Registered pooled CI REFUSED at k=2` | 4 of 33 | 4 of 232 | The k=2 interval condition no longer holds in all 4 of 4 affected outcomes: balanced-crystalloids Mortality and doac Any bleeding retain 0 of 2 base rows, while pcsk9 MACE and statins Major vascular events retain 1 of 2. Their outcome-specific Admission at pooling blocks name the set-asides; only the remaining single trials supply intervals, and the separately rendered result-change notices are OPEN, not countersigned. | Reason drafted; replacement: Admission at pooling |
| `Unit-of-analysis/design caveat` | 2 of 33 | 2 of 232 | The factorial disclosure changes on 2 of 2 affected pages because admission removes BaSICS/PMID 34375394 from balanced-crystalloids (factorial 1 of 2 -> 0 of 0 retained primary rows) and Alpha Omega/PMID 20929341 plus SU.FOL.OM3/PMID 21115589 from omega3 (factorial 3 of 5 -> 1 of 1). The admission blocks identify why those candidate rows left; VITAL/PMID 30415637 remains explicitly factorial and no interaction or variance issue was newly resolved. | Reason drafted; replacement: Admission at pooling |
| `UNRENDERABLE stale contrast block` | 8 of 33 | 8 of 232 | In 3 of 8 affected pages (balanced-crystalloids, probiotics, tocilizumab), an empty primary pool bypasses current_arm_contrast filtering, removes the stale-cache warning and re-exposes cached trials as pooled; 5 of 8 pages instead correctly update their current/suppressed ID lists. The disappearing warnings cannot be acknowledged as successful cache reconciliation, so the entire class is withheld. | UNEXPLAINED — no reason entry |
| `Parser-confirmed contrast disclosure` | 14 of 33 | 14 of 232 | In 3 of 14 pages the displayed parser numerator/denominator increases after the primary pool empties: balanced-crystalloids 2 of 2 -> 2 of 3, probiotics 1 of 11 -> 3 of 16, tocilizumab 1 of 1 -> 3 of 3, while actual primary retention is respectively 0 of 2, 0 of 11 and 0 of 1. Those are cached lists, not newly admitted trials; the other 11 of 14 changes are consistent with removal. No blanket class reason is drafted. | UNEXPLAINED — no reason entry |
| `Funding / conflict-of-interest disclosur` | 18 of 33 | 36 of 232 | All 18 of 18 direct-base funding tables retain their complete row multisets, classifications, source spans and numerical summaries; admission changes pooled-first insertion order, and screened-in evidence is merged back by consumer_consistency so set-aside trials are not erased. The other 18 of 36 lost blocks are historical-floor disclosures whose previously reviewed successors now have new digests; this is reordering, not reduced industry involvement or new source acquisition, and the inherited per-pooled-trial heading still overstates the table’s broader population (per-page counts are in ACK_REPORT.md). | Reason drafted; same heading |
| `RoB-restricted re-pool suppressed` | 18 of 33 | 18 of 232 | Admission changes primary membership on all 18 of 18 affected pages: 9 of 18 keep the suppression block with the current smaller low-only/full set, while 9 of 18 empty their primary pool and instead render the explicit PRIMARY_ABSENT omission plus admission accounting. Formal human RoB assessment remains unperformed; ACK_REPORT.md supplies every before/after k and the replacement does not equate smaller membership with lower bias. | Reason drafted; replacement: Admission at pooling |
| `GRADE provisional -- not yet fully asses` | 22 of 33 | 22 of 232 | Across 22 of 22 affected pages, 11 of 22 lose the primary pool and omit GRADE rather than issue certainty about an absent estimate; the other 11 of 22 retain provisional GRADE with the admitted pool’s interval and current incomplete-membership basis. The outcome-specific admission block is the common replacement anchor, and ACK_REPORT.md preserves every changed interval/domain text and both primary row counts; no unassessed domain is treated as favourable and no new formal certainty assessment is asserted. | Reason drafted; replacement: Admission at pooling |
| `Unit-of-analysis caveat` | 1 of 33 | 1 of 232 | This 1 of 1 historical-floor block described patient-count pooling of 3 of 5 cluster-crossover trials, already replaced before the base by explicit design refusal; this landing then sets aside the remaining 2 of 2 primary rows on family admission. The current DECLARED ABSENT design-refusal block states no pooled number, and all 3 of 3 design-refused trials remain named, so neither the old naive pool nor its illustrative variance sensitivity is a current result. | Reason drafted; replacement: DECLARED ABSENT |
| `Randomised-contrast disclosure` | 12 of 33 | 12 of 232 | All 12 of 12 blocks are historical-floor predecessors of the newer parser disclosures. The balanced-crystalloids replacement is one of the empty-pool cache regressions: the historical 2 of 5 registry-confirmed display, base 2 of 2 parser-confirmed display and current 2 of 3 cached display cannot be acknowledged as a current-pool improvement when 0 of 2 base primary rows remain. The shared heading-level schema cannot safely sign only the other 11 of 12 pages, so this class is withheld. | UNEXPLAINED — no reason entry |
| `Does the result survive dropping the tri` | 21 of 33 | 23 of 232 | The 23 of 23 lost sensitivity blocks on 21 of 32 review pages comprise 20 of 23 historical-floor tables and 3 of 23 direct-base omission blocks: after admission, 13 of 23 map to explicit PRIMARY_ABSENT omissions and 10 of 23 to the current suppressed RoB re-pool statement. Admission accounting and the per-page before/after primary counts in ACK_REPORT.md explain the change; the iv-iron primary is now the single admitted CONFIRM-HF estimate rather than the former mixed-estimand pool, and none of these replacements establishes formal human RoB assessment. | Reason drafted; replacement: Admission at pooling |
| `Overall certainty` | 22 of 33 | 22 of 232 | All 22 of 22 blocks are historical-floor certainty statements whose later provisional successors changed under admission: 11 of 22 affected pages now omit GRADE because the primary pool emptied, and 11 of 22 retain GRADE provisional without a complete formal domain assessment. Re-anchor to the admission accounting with the old and current pool/domain values retained in ACK_REPORT.md; the old certainty categories and downgrade arithmetic are not reaffirmed. | Reason drafted; replacement: Admission at pooling |
| `DECLARED ABSENT` | 6 of 33 | 9 of 232 | All 9 of 9 lost blocks concern historical harm outcomes, not the current primary outcome. Existing acknowledgement edges for 6 of 9 point to funding disclosures, 1 of 9 to a stale contrast disclosure, and the remaining 2 of 9 follow earlier result-change chains; matching by shared trial IDs does not establish an equivalent harm disclosure. The supplied same-heading candidates on corticosteroids-COVID and probiotics are primary-absence blocks, not the lost Serious/Any adverse-event blocks. Some harm pools changed under admission and others did not; this needs outcome-specific re-pairing rather than a blanket heading-class reason, so no class reason is drafted. | UNEXPLAINED — no reason entry |
| `Pooled result SUPPRESSED` | 2 of 33 | 5 of 232 | All 5 of 5 lost mixed-estimand blocks concern 2 of 32 topics: corticosteroids-CAP Hyperglycaemia retains 2 of 4 rows after PMIDs 25608756 and 21636122 are set aside, while iv-iron Heart-failure hospitalization retains 1 of 2 after PMID 40159390 is set aside. Their admission blocks describe removal of the incompatible contributors, not a conversion between effect scales; the narrower remaining outcome and its OPEN result-change notice replace the former cross-scale counterfactual, with the separate topic-page strand loss left UNEXPLAINED. | Reason drafted; replacement: Admission at pooling |
| `No checkable pooled claim` | 2 of 33 | 2 of 232 | Both 2 of 2 lost warnings cease to describe the current result: iv-iron retains CONFIRM-HF as 1 of 2 prior primary rows after the mixed-estimand contributor leaves, and statins retains PMID 42670961 as 1 of 2 after PMID 20404379 is set aside. The admission block records that restriction, and statins’ canonical outcome claims increase from 0 of 1 current claim to 1 of 1; these newly checkable single-trial claims are disclosed in OPEN result-change notices, not evidence-strength upgrades. | Reason drafted; replacement: Admission at pooling |
| `Pooled result REFUSED` | 2 of 33 | 2 of 232 | Both 2 of 2 direction-conflict refusals are replaced by admission absence: sacubitril-valsartan sets aside PMID 25176015 and NCT02468232, and ticagrelor sets aside PMIDs 19717846 and 26376600, leaving 0 of 2 prior primary rows on each page. The incompatible-direction comparisons and ticagrelor’s formerly served PLATO anchor are no longer served estimates; their candidate values remain recorded and the admission block names the family-eligibility failure. | Reason drafted; replacement: Admission at pooling |

**Per-outcome membership accounting.** Every changed row below is tied to a typed admission record. Counts use the base outcome population as denominator, not a literature-completeness claim; entry counts are measured separately. Unchanged outcomes are not presented as gate recoveries.

| Topic / outcome | Base rows | Retained rows | Set aside | Exact row / family / eligibility accounting |
|---|---:|---:|---:|---|
| balanced-crystalloids-vs-saline-mortality / Mortality (primary) | 2 of 2 | 0 of 2 | 2 of 2 | PMID 35041780 → NCT02721654: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED; PMID 34375394 → NCT02875873: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN |
| balanced-crystalloids-vs-saline-mortality / New renal-replacement therapy | 1 of 1 | 0 of 1 | 1 of 1 | PMID 35041780 → NCT02721654: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| colchicine-postop-af / Postoperative atrial fibrillation (primary) | 3 of 3 | 2 of 3 | 1 of 3 | PMID 42132185 → SYN-f9c2d88aa0de: UNKNOWN / REGISTRY_PARENT_UNRESOLVED |
| colchicine-secondary-cv-prevention / Trial-defined major coronary/cardiovascular composite (primary) | 3 of 3 | 2 of 3 | 1 of 3 | PMID 32865380 → ACTRN12614000093684: UNKNOWN / INSUFFICIENT_PICD_EVIDENCE |
| colchicine-secondary-cv-prevention / Gastrointestinal adverse effects | 1 of 1 | 0 of 1 | 1 of 1 | PMID 34876021 → SYN-981b057cb68a: UNKNOWN / REGISTRY_PARENT_UNRESOLVED |
| colchicine-secondary-cv-prevention / Non-cardiovascular death | 1 of 1 | 0 of 1 | 1 of 1 | PMID 32865380 → ACTRN12614000093684: UNKNOWN / INSUFFICIENT_PICD_EVIDENCE |
| corticosteroids-cap-mortality / Hyperglycaemia | 4 of 4 | 2 of 4 | 2 of 4 | PMID 25608756 → NCT00973154: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN; PMID 21636122 → NCT00471640: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| corticosteroids-covid19-mortality / 28-day all-cause mortality (primary) | 1 of 1 | 0 of 1 | 1 of 1 | PMID 32678530 → NCT04381936: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| corticosteroids-covid19-mortality / Serious adverse events | 1 of 1 | 0 of 1 | 1 of 1 | PMID 34138478 → NCT04348305: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN |
| dapagliflozin-hfpef-hosp / Adverse events | 1 of 1 | 0 of 1 | 1 of 1 | PMID 34711976 → NCT03030235: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| denosumab-vertebral-fracture / New vertebral fracture (primary) | 1 of 1 | 0 of 1 | 1 of 1 | PMID 19671655 → NCT00089791: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| denosumab-vertebral-fracture / Nonvertebral fracture | 1 of 1 | 0 of 1 | 1 of 1 | PMID 19671655 → NCT00089791: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| denosumab-vertebral-fracture / Hip fracture | 1 of 1 | 0 of 1 | 1 of 1 | PMID 19671655 → NCT00089791: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| doac-vte-recurrence / Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) (primary) | 6 of 6 | 0 of 6 | 6 of 6 | PMID 24344086 → NCT00680186: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED; PMID 19966341 → NCT00291330: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED; PMID 22449293 → NCT00439777: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN; PMID 21128814 → SYN-968e8c7d0a82: UNKNOWN / REGISTRY_PARENT_UNRESOLVED; PMID 23991658 → NCT00986154: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN; PMID 23808982 → NCT00643201: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| doac-vte-recurrence / Major bleeding | 3 of 3 | 0 of 3 | 3 of 3 | PMID 24344086 → NCT00680186: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED; PMID 19966341 → NCT00291330: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED; PMID 22449293 → NCT00439777: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN |
| doac-vte-recurrence / Major or clinically relevant nonmajor bleeding | 2 of 2 | 0 of 2 | 2 of 2 | PMID 22449293 → NCT00439777: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN; PMID 23991658 → NCT00986154: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN |
| doac-vte-recurrence / Any bleeding | 2 of 2 | 0 of 2 | 2 of 2 | PMID 24344086 → NCT00680186: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED; PMID 19966341 → NCT00291330: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| dpp4-mace-t2d / 3-point major adverse cardiovascular events (primary) | 3 of 3 | 1 of 3 | 2 of 3 | PMID 30418475 → NCT01897532: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED; PMID 28893244 → NCT01703208: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN |
| dpp4-mace-t2d / Adverse events | 1 of 1 | 0 of 1 | 1 of 1 | PMID 30418475 → NCT01897532: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| dpp4-mace-t2d / Hypoglycemia | 1 of 1 | 0 of 1 | 1 of 1 | PMID 30418475 → NCT01897532: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| esketamine-trd-madrs / Observed-case Day-28 raw change-score MADRS MD (primary) | 3 of 3 | 1 of 3 | 2 of 3 | PMID 37025256 → NCT03434041: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED; NCT02422186 → NCT02422186: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| esketamine-trd-madrs / Adverse events | 1 of 1 | 0 of 1 | 1 of 1 | PMID 37025256 → NCT03434041: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| glp1-ra-mace-t2d / 3-point major adverse cardiovascular events (primary) | 8 of 8 | 7 of 8 | 1 of 8 | PMID 30291013 → NCT02465515: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| iv-iron-hfref-hosp / Heart-failure hospitalization (primary) | 2 of 2 | 1 of 2 | 1 of 2 | PMID 40159390 → NCT03036462: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN |
| metformin-pcos-ovulation / Ovulation with metformin added to clomifene (primary) | 3 of 3 | 0 of 3 | 3 of 3 | PMID 19522426 → SYN-a65b65385197: UNKNOWN / REGISTRY_PARENT_UNRESOLVED; PMID 16769748 → ISRCTN55906981: UNKNOWN / INSUFFICIENT_PICD_EVIDENCE; PMID 11172832 → SYN-90e1fc6ced9d: UNKNOWN / REGISTRY_PARENT_UNRESOLVED |
| noac-vs-warfarin-af-stroke / Stroke or systemic embolism (primary) | 4 of 4 | 0 of 4 | 4 of 4 | PMID 21830957 → NCT00403767: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN; PMID 19717844 → NCT00262600: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN; PMID 24251359 → NCT00781391: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN; PMID 21870978 → NCT00412984: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN |
| noac-vs-warfarin-af-stroke / Major bleeding | 2 of 2 | 0 of 2 | 2 of 2 | PMID 24251359 → NCT00781391: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN; PMID 21870978 → NCT00412984: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN |
| omega3-cardiovascular-events / Major vascular events / MACE (primary) | 5 of 5 | 1 of 5 | 4 of 5 | PMID 33190147 → NCT02104817: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN; PMID 30415628 → NCT01492361: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN; PMID 20929341 → NCT00127452: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN; PMID 21115589 → ISRCTN41926726: UNKNOWN / INSUFFICIENT_PICD_EVIDENCE |
| pcsk9-mace / Major adverse cardiovascular events (primary) | 2 of 2 | 1 of 2 | 1 of 2 | PMID 28304224 → NCT01764633: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| probiotics-aad-prevention / Antibiotic-associated diarrhoea (primary) | 11 of 11 | 0 of 11 | 11 of 11 | PMID 35727573 → NCT03334604: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED; PMID 32035998 → SYN-0419eae8aeb8: UNKNOWN / REGISTRY_PARENT_UNRESOLVED; PMID 24772726 → SYN-94f93929fa67: UNKNOWN / REGISTRY_PARENT_UNRESOLVED; PMID 23932219 → ISRCTN70017204: UNKNOWN / INSUFFICIENT_PICD_EVIDENCE; PMID 18701826 → SYN-3bb36b8c9d29: UNKNOWN / REGISTRY_PARENT_UNRESOLVED; PMID 18410562 → SYN-a2a3bd246f45: UNKNOWN / REGISTRY_PARENT_UNRESOLVED; PMID 15740542 → SYN-962dc41d54af: UNKNOWN / REGISTRY_PARENT_UNRESOLVED; PMID 11560298 → SYN-0b772df8adc9: UNKNOWN / REGISTRY_PARENT_UNRESOLVED; PMID 7872284 → SYN-e445a1f4ca49: UNKNOWN / REGISTRY_PARENT_UNRESOLVED; PMID 21165295 → SYN-2163745e2514: UNKNOWN / REGISTRY_PARENT_UNRESOLVED; PMID 18026577 → SYN-750512ad72a7: UNKNOWN / REGISTRY_PARENT_UNRESOLVED |
| probiotics-aad-prevention / Any adverse events | 2 of 2 | 0 of 2 | 2 of 2 | PMID 41699149 → SYN-dd9903025721: UNKNOWN / REGISTRY_PARENT_UNRESOLVED; PMID 39529939 → NCT05607056: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| probiotics-aad-prevention / Serious adverse events | 1 of 1 | 0 of 1 | 1 of 1 | PMID 34541475 → SYN-23fe0dd26422: UNKNOWN / REGISTRY_PARENT_UNRESOLVED |
| sacubitril-valsartan-hfref / Composite cardiovascular death or heart-failure hospitalization (primary) | 2 of 2 | 0 of 2 | 2 of 2 | PMID 25176015 → NCT01035255: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN; NCT02468232 → NCT02468232: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN |
| semaglutide-obesity-mace / 3-point major adverse cardiovascular events (primary) | 1 of 1 | 0 of 1 | 1 of 1 | PMID 37952131 → NCT03574597: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| semaglutide-obesity-mace / Adverse events leading to permanent discontinuation | 1 of 1 | 0 of 1 | 1 of 1 | PMID 37952131 → NCT03574597: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| sglt2-primary-prevention-hf / Hospitalization for heart failure (primary) | 4 of 4 | 1 of 4 | 3 of 4 | PMID 28605608 → SYN-c880f84165d0: UNKNOWN / REGISTRY_PARENT_UNRESOLVED; PMID 26378978 → NCT01131676: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED; PMID 30415602 → NCT01730534: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |
| sglt2-primary-prevention-hf / Lower-limb amputation | 1 of 1 | 0 of 1 | 1 of 1 | PMID 28605608 → SYN-c880f84165d0: UNKNOWN / REGISTRY_PARENT_UNRESOLVED |
| spironolactone-hfref-mortality / All-cause mortality (primary) | 3 of 3 | 1 of 3 | 2 of 3 | PMID 10471456 → SYN-983d4c339111: UNKNOWN / REGISTRY_PARENT_UNRESOLVED; PMID 21073363 → NCT00232180: INELIGIBLE / FAMILY_INELIGIBLE |
| statins-primary-prevention-elderly / Major vascular events (primary) | 2 of 2 | 1 of 2 | 1 of 2 | PMID 20404379 → SYN-f393bbca005f: UNKNOWN / REGISTRY_PARENT_UNRESOLVED |
| ticagrelor-vs-clopidogrel-acs / Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke (primary) | 2 of 2 | 0 of 2 | 2 of 2 | PMID 19717846 → NCT00391872: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN; PMID 26376600 → NCT01294462: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN |
| ticagrelor-vs-clopidogrel-acs / Major bleeding | 2 of 2 | 0 of 2 | 2 of 2 | PMID 19717846 → NCT00391872: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN; PMID 26376600 → NCT01294462: UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN |
| tocilizumab-covid19-mortality / 28-day all-cause mortality (primary) | 1 of 1 | 0 of 1 | 1 of 1 | PMID 33933206 → NCT04381936: UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED |

**Funding reconciliation.** All 18 of 18 direct-base blocks were checked as row multisets: order changes, source rows do not. The broader included-evidence table and its inherited “pooled trial” label already disagree in the base. Historical-floor differences predate this landing; they are not claimed as new funding discoveries.

| Topic | Industry-tied / known, base → current | Unknown / all table rows, base → current | Row multiset |
|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | 0 of 1 → 0 of 1 | 6 of 7 → 6 of 7 | 7 of 7 retained |
| colchicine-postop-af | 0 of 0 → 0 of 0 | 6 of 6 → 6 of 6 | 6 of 6 retained |
| colchicine-secondary-cv-prevention | 0 of 3 → 0 of 3 | 22 of 25 → 22 of 25 | 25 of 25 retained |
| corticosteroids-cap-mortality | 1 of 2 → 1 of 2 | 7 of 9 → 7 of 9 | 9 of 9 retained |
| corticosteroids-covid19-mortality | 0 of 1 → 0 of 1 | 6 of 7 → 6 of 7 | 7 of 7 retained |
| doac-vte-recurrence | 4 of 4 → 4 of 4 | 2 of 6 → 2 of 6 | 6 of 6 retained |
| dpp4-mace-t2d | 3 of 3 → 3 of 3 | 2 of 5 → 2 of 5 | 5 of 5 retained |
| esketamine-trd-madrs | 2 of 2 → 2 of 2 | 2 of 4 → 2 of 4 | 4 of 4 retained |
| glp1-ra-mace-t2d | 9 of 9 → 9 of 9 | 0 of 9 → 0 of 9 | 9 of 9 retained |
| iv-iron-hfref-hosp | 5 of 6 → 5 of 6 | 3 of 9 → 3 of 9 | 9 of 9 retained |
| metformin-pcos-ovulation | 1 of 1 → 1 of 1 | 6 of 7 → 6 of 7 | 7 of 7 retained |
| noac-vs-warfarin-af-stroke | 3 of 3 → 3 of 3 | 4 of 7 → 4 of 7 | 7 of 7 retained |
| omega3-cardiovascular-events | 4 of 7 → 4 of 7 | 13 of 20 → 13 of 20 | 20 of 20 retained |
| pcsk9-mace | 4 of 4 → 4 of 4 | 1 of 5 → 1 of 5 | 5 of 5 retained |
| probiotics-aad-prevention | 2 of 5 → 2 of 5 | 52 of 57 → 52 of 57 | 57 of 57 retained |
| sglt2-primary-prevention-hf | 4 of 4 → 4 of 4 | 2 of 6 → 2 of 6 | 6 of 6 retained |
| spironolactone-hfref-mortality | 1 of 1 → 1 of 1 | 2 of 3 → 2 of 3 | 3 of 3 retained |
| ticagrelor-vs-clopidogrel-acs | 0 of 0 → 0 of 0 | 3 of 3 → 3 of 3 | 3 of 3 retained |

**Marker accounting.** Counts are literal rendered-marker occurrences, not patient counts or the number of unassessed GRADE domains. `not_assessed` matches lowercase “not assessed” and uppercase `NOT_ASSESSED`; uppercase “NOT ASSESSED” with a space does not match. Full removal/addition contexts were reconciled to both inventories.

| Page / kind | Base | New | Exact accounting |
|---|---:|---:|---|
| docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html / design_refusal | 1 of 1 | 0 of 1 | Of 1 of 1 base design_refusal occurrences, the phrase "Pool changed because a design refusal was added" in the ENGINE_CANNOT_CONSUME banner disappears, leaving 0 of 1. Mortality retains 0 of 2 rows after PLUS/PMID 35041780 and BaSICS/PMID 34375394 fail P5; the replacement DECLARED ABSENT design-refusal statement and all 3 of 3 individually named SMART/SALT/SPLIT refusals remain, but use different words that this marker does not count. |
| docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html / not_assessed | 14 of 14 | 13 of 14 | The exact count is 14 of 14 -> 13 of 14 retained occurrences: the limitation-ledger row topic:balanced-crystalloids-vs-saline-mortality:outcomes:0:mortality:k2-ci-refused contributes the sole lost NOT_ASSESSED token after Mortality retains 0 of 2 base rows. Trial-integrity wording and manuscript certainty wording each still contribute 1 of 1 token despite changing text; the GRADE table says uppercase "NOT ASSESSED" with a space, which is not this case-sensitive marker. No new bias assessment explains the decrease. |
| docs/reviews/corticosteroids-cap-mortality/index.html / refusal_counterfactual | 1 of 1 | 0 of 1 | The sole "Refusal is reversible and auditable" occurrence in the Hyperglycaemia mixed OR/RR suppression block is removed: 1 of 1 -> 0 of 1. Admission sets aside PMIDs 25608756 and 21636122, leaving 2 of 4 prior rows; the former invalid cross-scale counterfactual is no longer applicable to those remaining rows and the change is disclosed in the outcome admission block and OPEN result-change notice. |
| docs/reviews/corticosteroids-cap-mortality/index.html / suppressed_pool | 1 of 1 | 0 of 1 | The only "Pooled result SUPPRESSED" occurrence belongs to Hyperglycaemia, not primary mortality, and falls from 1 of 1 to 0 of 1 when admission removes PMIDs 25608756 and 21636122 (2 of 4 prior rows retained). Its mixed OR/RR block is replaced by the smaller outcome’s own result and admission accounting; the primary pool does not change. |
| docs/reviews/doac-vte-recurrence/index.html / not_assessed | 34 of 34 | 33 of 34 | The exact count is 34 of 34 -> 33 of 34 retained occurrences: the only net loss is NOT_ASSESSED in limitation-ledger row topic:doac-vte-recurrence:harms:2:any-bleeding:k2-ci-refused. Any bleeding retains 0 of 2 rows (PMIDs 19966341 and 24344086 set aside), while the primary retains 0 of 6; the changed integrity and manuscript-certainty sentences each retain 1 of 1 marker, and the other 33 of 34 original marker units remain in the new count. |
| docs/reviews/iv-iron-hfref-hosp/index.html / refusal_counterfactual | 2 of 2 | 0 of 2 | UNEXPLAINED as an approvable decrease: 2 of 2 -> 0 of 2, comprising 1 of 2 lost occurrences of "Refusal is reversible and auditable" in the primary mixed-estimand Results block and 1 of 2 of "If forced it would be" in the vanished Declared strands cross-endpoint paragraph. The first follows removal of FAIR-HF2/PMID 40159390 (1 of 2 primary rows remains), but the second loses an independently relevant strand refusal from the topic page; the index retaining that text does not replace it on this page. Do not sign this entry until that same-page loss is resolved. |
| docs/reviews/iv-iron-hfref-hosp/index.html / suppressed_pool | 2 of 2 | 0 of 2 | Both 2 of 2 "Pooled result SUPPRESSED" occurrences disappear (0 of 2 retained): 1 of 2 is the Overview primary block and 1 of 2 the Results primary block. FAIR-HF2/PMID 40159390 fails P5 with family NCT03036462 UNKNOWN / INTERVENTION_CONTRAST_NOT_PROVEN, leaving CONFIRM-HF as 1 of 2 rows and an HR single-trial interval; this is removal of the recurrent-rate contributor, not estimand conversion or eligibility recovery. |
| docs/reviews/iv-iron-hfref-hosp/index.html / declared_absent | 63 of 63 | 62 of 63 | The exact count is 63 of 63 -> 62 of 63 retained occurrences: the single lost SOURCE_NOT_RETRIEVED token is the SOURCE_NOT_RETRIEVED_FULL_TEXT_NEEDED note attached to FAIR-HF2/PMID 40159390’s formerly consumed non-HR row. That row is set aside on P5, leaving 1 of 2 primary rows; manuscript Results changes its declared-absent family tally from 7 of 9 to 8 of 9 but still contributes 1 of 1 literal "declared absent" occurrence, so the increased family tally does not offset the removed token. |
| docs/reviews/iv-iron-hfref-hosp/index.html / not_assessed | 14 of 14 | 13 of 14 | The exact count is 14 of 14 -> 13 of 14 retained occurrences: NOT_ASSESSED disappears from the limitation-ledger row topic:iv-iron-hfref-hosp:riskofbias:grade-certainty when the incompatible primary is replaced by the 1 of 2 remaining CONFIRM-HF row after FAIR-HF2/PMID 40159390 is set aside. The revised integrity and manuscript-certainty text each retain 1 of 1 marker; formal RoB and provisional GRADE remain unassessed, so the token loss is a changed limitation target rather than assessment completion. |
| docs/reviews/pcsk9-mace/index.html / not_assessed | 19 of 19 | 18 of 19 | The exact count is 19 of 19 -> 18 of 19 retained occurrences: the sole net loss is NOT_ASSESSED in limitation-ledger row topic:pcsk9-mace:outcomes:0:major-adverse-cardiovascular-events:k2-ci-refused. FOURIER/PMID 28304224 is set aside (NCT01764633 UNKNOWN / ENTRY_POPULATION_NOT_ESTABLISHED), leaving ODYSSEY OUTCOMES/PMID 30403574 as 1 of 2 rows; the integrity sentence changes its trial count but retains 1 of 1 marker, and no formal bias assessment was completed. |
| docs/reviews/statins-primary-prevention-elderly/index.html / claims_checked_zero | 2 of 2 | 0 of 2 | Both 2 of 2 occurrences of "Claims checked: 0" disappear (0 of 2 retained): 1 of 2 in the canonical-claims paragraph becomes "Claims checked: 1", and 1 of 2 in the No checkable pooled claim block is removed. PMID 20404379 is set aside for UNKNOWN / REGISTRY_PARENT_UNRESOLVED, leaving PMID 42670961 as 1 of 2 rows with a single-trial interval; the former k=2 CI refusal no longer prevents the 1 of 1 current outcome claim being checked, and the result-change notice is OPEN. |
| docs/reviews/statins-primary-prevention-elderly/index.html / not_assessed | 14 of 14 | 13 of 14 | The exact count is 14 of 14 -> 13 of 14 retained occurrences: the sole net loss is NOT_ASSESSED in limitation-ledger row topic:statins-primary-prevention-elderly:outcomes:0:major-vascular-events:k2-ci-refused after PMID 20404379 is set aside, leaving PMID 42670961 as 1 of 2 primary rows. The changed trial-integrity sentence retains 1 of 1 marker; neither RoB nor GRADE has received a new human assessment. |

**Follow-up conditions for the integrator.** Restore a same-page iv-iron strand disclosure, correct empty-pool contrast filtering, derive index parity from actual membership without stale fallbacks, and re-pair historical harm obligations to their own outcomes before considering the withheld classes. Existing wrong-endpoint or source-data statements in the quoted text remain historical claims, not new endorsements. The empty-pool manuscript sentence “from 0 downgrade(s)” and the funding population label also require care: neither means a completed certainty/funding assessment.

**Validation.** Focused existing tests passed: `python -m pytest -q -p no:cacheprovider tests/test_ratchet_marker_ack.py tests/test_honest_ratchet.py tests/test_parity_relation.py --basetemp=.tmp/ack_pytest` — 33 of 33 passed. The artefact verification script passed 950 of 950 assertions: exact class and pair coverage, all 12 of 12 marker counts, all 81 of 81 set-aside candidate tuples and 46 of 46 retained tuples, the corrected GLP-1 mapping, the unchanged comparator set, UTF-8 without BOM, unsigned schemas, unchanged HEAD, and unchanged bytes in 3864 of 3864 pre-existing tracked files. The source-table recount also verifies plant validations as 58 of 68 -> 59 of 69 plant events. Detailed results are retained in `.tmp/ack_evidence/verification.json`; these checks validate the audit artefacts and do not certify the landing.

**Full pair evidence.** Each collapsed record contains the entire lost rendered text and every same-heading candidate printed by the source pair algorithm, without truncation. Where a class reason selects another heading, the selected same-page block is also included. Historical floor is labelled explicitly; a same-heading candidate can be wrong and is never automatically treated as proof.

<details><summary>Pair 1 of 232 — docs/index.html — We measured our own error rate</summary>

Source ref: `38c04411`; lost SHA-256: `f9c2c911cd518aa9b73d77025fd3e6178f71d735114bde04816f6a76192e432e`.

Lost full text:

```text
We measured our own error rate (no meta-analysis reports this about itself) Historical blind audit, measured 2026-09-12 on 99 then-pooled numbers; this is not a current-population error-rate estimate. The live inventory contains 127 pooled rows; 24 are explicitly NOT_INDEPENDENTLY_RECHECKED. The inventory refresh does not increase the historical independent-verification numerator. Every claim the harness makes rests on the assumption that its numbers are right. So we measured it: all 99 pooled numbers were independently re-extracted from the committed source by an offline checker blind to the stored value , then compared deterministically. 95 of 99 were re-extractable from the same source the checker was given; 92 of 95 matched exactly (‘exactly’ = the effect and both confidence limits agree to the rounding of the source's printed precision, and counts agree as integers). The 3 disagreements were hand-adjudicated against source: on adjudication 1 was a genuine error on our side (a gastrointestinal-adverse-event outcome that had pooled the trial's OVERALL adverse-event count — a wrong endpoint that had passed every gate; found here and fixed), and the remainder were checker-side (an incidence-rate ratio the checker called a plain rate ratio with identical numbers; an on-treatment vs intention-to-treat estimand choice where our ITT value is the standard one). The other 4 numbers source from ClinicalTrials.gov results or full text, so they were not re-checkable from the abstract and are not counted as verified here. The pre-adjudication disagreement rate was 3 of 95 (Wilson 95% CI 1.1–8.9%). The honest caveat that makes this credible: the blind checker and the extractor share a model architecture, so this is an internal-consistency measure, not an independent accuracy estimate — a genuinely independent, cross-family (non-Claude) re-extraction is the stronger check, and is being built. It is nonetheless the single most important number the project lacked, and it is measured, adjudicated, and reproducible from scripts/error_rate_compare.py .
```

Candidate 1 of 1; SHA-256 `242c1250f0a980e4e61908e84ac8d33f012d9fcd25eb94fb974ab4114f8ac75b`:

```text
We measured our own error rate (no meta-analysis reports this about itself) Historical blind audit, measured 2026-09-12 on 99 then-pooled numbers; this is not a current-population error-rate estimate. The live inventory contains 46 pooled rows; 6 are explicitly NOT_INDEPENDENTLY_RECHECKED. The inventory refresh does not increase the historical independent-verification numerator. Every claim the harness makes rests on the assumption that its numbers are right. So we measured it: all 99 pooled numbers were independently re-extracted from the committed source by an offline checker blind to the stored value , then compared deterministically. 95 of 99 were re-extractable from the same source the checker was given; 92 of 95 matched exactly (‘exactly’ = the effect and both confidence limits agree to the rounding of the source's printed precision, and counts agree as integers). The 3 disagreements were hand-adjudicated against source: on adjudication 1 was a genuine error on our side (a gastrointestinal-adverse-event outcome that had pooled the trial's OVERALL adverse-event count — a wrong endpoint that had passed every gate; found here and fixed), and the remainder were checker-side (an incidence-rate ratio the checker called a plain rate ratio with identical numbers; an on-treatment vs intention-to-treat estimand choice where our ITT value is the standard one). The other 4 numbers source from ClinicalTrials.gov results or full text, so they were not re-checkable from the abstract and are not counted as verified here. The pre-adjudication disagreement rate was 3 of 95 (Wilson 95% CI 1.1–8.9%). The honest caveat that makes this credible: the blind checker and the extractor share a model architecture, so this is an internal-consistency measure, not an independent accuracy estimate — a genuinely independent, cross-family (non-Claude) re-extraction is the stronger check, and is being built. It is nonetheless the single most important number the project lacked, and it is measured, adjudicated, and reproducible from scripts/error_rate_compare.py .
```

</details>

<details><summary>Pair 2 of 232 — docs/index.html — External validation</summary>

Source ref: `38c04411`; lost SHA-256: `f6b70c44e338426c4678ec18420375256622772604658548a77b1d36f185f459`.

Lost full text:

```text
External validation: our pooled numbers vs the published meta-analyses' The strongest check is against an external hand-built standard: our pooled primary estimate vs the published comparator meta-analysis's reported pooled estimate. But a comparison is only 'the same question' when the two share the same estimand — an RR is not an OR is not an HR (an odds ratio sits further from 1 than a risk ratio for common events; a hazard ratio is a rate, not a risk), so comparing them on the log scale as if interchangeable is a comparator-context mismatch . Keying on the estimand: of 23 topics, 13 are same-estimand comparisons, and 8 of those agree within ~12% on the log scale with a different evidence base; 2 are arithmetic replications on an identical trial set and are not counted as independent corroboration; 3 same-estimand comparison(s) diverge (adjudicated). 10 are cross-estimand (e.g. our HR vs their OR): direction-consistent but the same-question agreement claim is SUPPRESSED until a scale-matched, event-rate-justified conversion is verified — a previous version counted these as agreements, which compared different quantities. 0 cross-estimand comparison(s) disagree on direction, and 0 outcome(s) are not comparable at all (a mean difference vs a rate). Every case is enumerated in docs/external_agreement.json . This is pooled-level agreement. The per-trial head-to-head was attempted against the gold standard (the Cochrane review CD013505 of metformin for PCOS ovulation): its pooled OR 2.64 (k=13) sits far from our single-trial OR 8.25 (k=1) — a stark, honest illustration of the small-k weakness the expansion tier targets — but a true number-by-number check is blocked even for Cochrane : its per-woman arm counts live in forest-plot images, not the open-access text (only per-cycle data is tabulated). Per-trial ground truth needs vision/OCR or IPD ( docs/cochrane_headtohead.json ). Is our small k our limit or the question's? Of the topics with a same-scope comparator, 9 are at or above the complete same-scope evidence (our k equals the comparable comparator's — the smallness is the literature's, not ours); 1 are 1–2 trials short (bar-limited, decomposed on the page); and 9 face a genuinely larger literature where the gap is named per topic (open-label excluded, different outcome definition, prophylaxis-vs-treatment, or reach). So small k is labelled, not hidden — and where it is the question's limit we say so.
```

Candidate 1 of 1; SHA-256 `850863f8d0a694f050c457337c05e3e500fb62f8e758bad4529e2fe04130d4aa`:

```text
External validation: our pooled numbers vs the published meta-analyses' The strongest check is against an external hand-built standard: our pooled primary estimate vs the published comparator meta-analysis's reported pooled estimate. But a comparison is only 'the same question' when the two share the same estimand — an RR is not an OR is not an HR (an odds ratio sits further from 1 than a risk ratio for common events; a hazard ratio is a rate, not a risk), so comparing them on the log scale as if interchangeable is a comparator-context mismatch . Keying on the estimand: of 15 topics, 9 are same-estimand comparisons, and 5 of those agree within ~12% on the log scale with a different evidence base; 1 are arithmetic replications on an identical trial set and are not counted as independent corroboration; 3 same-estimand comparison(s) diverge (adjudicated). 6 are cross-estimand (e.g. our HR vs their OR): direction-consistent but the same-question agreement claim is SUPPRESSED until a scale-matched, event-rate-justified conversion is verified — a previous version counted these as agreements, which compared different quantities. 0 cross-estimand comparison(s) disagree on direction, and 0 outcome(s) are not comparable at all (a mean difference vs a rate). Every case is enumerated in docs/external_agreement.json . This is pooled-level agreement. The per-trial head-to-head was attempted against the gold standard (the Cochrane review CD013505 of metformin for PCOS ovulation): its pooled OR 2.64 (k=13) sits far from our single-trial OR 8.25 (k=1) — a stark, honest illustration of the small-k weakness the expansion tier targets — but a true number-by-number check is blocked even for Cochrane : its per-woman arm counts live in forest-plot images, not the open-access text (only per-cycle data is tabulated). Per-trial ground truth needs vision/OCR or IPD ( docs/cochrane_headtohead.json ). Is our small k our limit or the question's? Of the topics with a same-scope comparator, 9 are at or above the complete same-scope evidence (our k equals the comparable comparator's — the smallness is the literature's, not ours); 1 are 1–2 trials short (bar-limited, decomposed on the page); and 9 face a genuinely larger literature where the gap is named per topic (open-label excluded, different outcome definition, prophylaxis-vs-treatment, or reach). So small k is labelled, not hidden — and where it is the question's limit we say so.
```

</details>

<details><summary>Pair 3 of 232 — docs/index.html — Every pooled number is verified against </summary>

Source ref: `38c04411`; lost SHA-256: `9b96b22c1d6ff4c3eb321937dfcdbe290f43ee2c7405ad114805cdf97a9d1eb4`.

Lost full text:

```text
Every pooled number is verified against its source (gate-enforced) All 127 of 127 pooled trial-outcome numbers across these pages have their digits located in the committed source span they cite (arm counts, effect+CI, or per-arm mean/SD). A publication-gate limb ( check_pooled_verified ) refuses any page that pools a number not found in its source , so this cannot silently stop being true. No published meta-analysis makes — or can be forced to keep — this claim about every one of its numbers. Located is not correct. This count establishes where each number came from, not that it answers the review's question: 2 number(s) that passed this check digit for digit were withdrawn as the wrong endpoint -- dapagliflozin-hfpef-hosp (36027570: HR 0.88 (0.74-1.05), withdrawn 2026-09-19, see the page's notice); empagliflozin-hfpef-hosp (34449189: HR 0.91 (0.76-1.09), withdrawn 2026-09-19, see the page's notice).
```

Candidate 1 of 1; SHA-256 `f5d3fe86879da6834b0913032aee3fca3a2711323a1c6ba660cb1455c5f85730`:

```text
Every pooled number is verified against its source (gate-enforced) All 46 of 46 pooled trial-outcome numbers across these pages have their digits located in the committed source span they cite (arm counts, effect+CI, or per-arm mean/SD). A publication-gate limb ( check_pooled_verified ) refuses any page that pools a number not found in its source , so this cannot silently stop being true. No published meta-analysis makes — or can be forced to keep — this claim about every one of its numbers. Located is not correct. This count establishes where each number came from, not that it answers the review's question: 2 number(s) that passed this check digit for digit were withdrawn as the wrong endpoint -- dapagliflozin-hfpef-hosp (36027570: HR 0.88 (0.74-1.05), withdrawn 2026-09-19, see the page's notice); empagliflozin-hfpef-hosp (34449189: HR 0.91 (0.76-1.09), withdrawn 2026-09-19, see the page's notice).
```

</details>

<details><summary>Pair 4 of 232 — docs/index.html — Corpus currency</summary>

Source ref: `38c04411`; lost SHA-256: `d71beaca97fc7d075ed062f23fab25f05d0beb07804be00dcbdc01094aa421c6`.

Lost full text:

```text
Corpus currency (invalidation propagation) 0 of 32 topics current; 32 of 32 STALE. A topic is STALE when a committed signal invalidates a dependent output — a pooled trial is retracted, the primary outcome is reported by a trial that could not be pooled, a trial flagged ELIGIBLE is not pooled, or a search source errored (retrieval completeness unproven). The flag poisons every surface: each STALE topic renders the reason at the top of its page and cannot read as a settled current estimate. Published as it falls. balanced-crystalloids-vs-saline-mortality — eligible_declared_absent, never_considered, search_not_executed colchicine-postop-af — eligible_declared_absent, known_eligible_missing, search_not_executed colchicine-recurrent-pericarditis — eligible_declared_absent, search_not_executed colchicine-secondary-cv-prevention — eligible_declared_absent, search_not_executed corticosteroids-cap-mortality — eligible_declared_absent, known_eligible_missing, never_considered, search_not_executed corticosteroids-covid19-mortality — eligible_declared_absent, search_not_executed dapagliflozin-hfpef-hosp — eligible_declared_absent, primary_reported_not_extracted, search_not_executed denosumab-vertebral-fracture — search_not_executed doac-vte-recurrence — search_not_executed dpp4-mace-t2d — eligible_declared_absent, known_eligible_missing, search_not_executed empagliflozin-hfpef-hosp — eligible_declared_absent, known_eligible_missing, no_checkable_claim, primary_reported_not_extracted, search_not_executed esketamine-trd-madrs — eligible_declared_absent, search_not_executed finerenone-ckd-t2d-renal — eligible_declared_absent, search_not_executed glp1-ra-mace-t2d — EXTRACTED_NOT_ADMISSIBLE, EXTRACTED_SOURCE_CONFLICT, eligible_declared_absent, search_not_executed iv-iron-hfref-hosp — eligible_declared_absent, known_eligible_missing, search_not_executed melatonin-primary-insomnia-sol — eligible_declared_absent, search_not_executed metformin-pcos-ovulation — eligible_declared_absent, search_not_executed noac-vs-warfarin-af-stroke — eligible_declared_absent, search_not_executed omega3-cardiovascular-events — eligible_declared_absent, search_not_executed pcsk9-mace — eligible_declared_absent, search_not_executed probiotics-aad-prevention — eligible_declared_absent, search_not_executed sacubitril-valsartan-hfref — eligible_declared_absent, no_checkable_claim, search_not_executed semaglutide-obesity-mace — search_not_executed semaglutide-obesity-weight — eligible_declared_absent, search_not_executed sglt2-ckd-progression — eligible_declared_absent, search_not_executed sglt2-hfref-hosp-cvdeath — eligible_declared_absent, search_not_executed sglt2-primary-prevention-hf — eligible_declared_absent, search_not_executed spironolactone-hfref-mortality — search_not_executed statins-primary-prevention-elderly — eligible_declared_absent, search_not_executed ticagrelor-vs-clopidogrel-acs — eligible_declared_absent, search_not_executed tocilizumab-covid19-mortality — eligible_declared_absent, search_not_executed tranexamic-acid-pph — eligible_declared_absent, search_not_executed Protocol↔config: 35 divergence(s) across 18 of 32 topics (prose protocol vs executable config, compared as two independent sources; each a defect to resolve or a dated amendment to declare).
```

Candidate 1 of 1; SHA-256 `c54cff4fda492c6a62b26756fb9453723b464757ffc6db6a59fba1a931e97722`:

```text
Corpus currency (invalidation propagation) 0 of 32 topics current; 32 of 32 STALE. A topic is STALE when a committed signal invalidates a dependent output — a pooled trial is retracted, the primary outcome is reported by a trial that could not be pooled, a trial flagged ELIGIBLE is not pooled, or a search source errored (retrieval completeness unproven). The flag poisons every surface: each STALE topic renders the reason at the top of its page and cannot read as a settled current estimate. Published as it falls. balanced-crystalloids-vs-saline-mortality — eligible_declared_absent, never_considered, no_checkable_claim, search_not_executed colchicine-postop-af — audit_eligibility_vs_screen_conflict, eligible_declared_absent, known_eligible_missing, search_not_executed colchicine-recurrent-pericarditis — eligible_declared_absent, search_not_executed colchicine-secondary-cv-prevention — eligible_declared_absent, search_not_executed corticosteroids-cap-mortality — audit_eligibility_vs_screen_conflict, eligible_declared_absent, known_eligible_missing, never_considered, search_not_executed corticosteroids-covid19-mortality — eligible_declared_absent, no_checkable_claim, search_not_executed dapagliflozin-hfpef-hosp — eligible_declared_absent, no_checkable_claim, primary_reported_not_extracted, search_not_executed denosumab-vertebral-fracture — eligible_declared_absent, no_checkable_claim, search_not_executed doac-vte-recurrence — eligible_declared_absent, no_checkable_claim, search_not_executed dpp4-mace-t2d — audit_eligibility_vs_screen_conflict, eligible_declared_absent, known_eligible_missing, search_not_executed empagliflozin-hfpef-hosp — audit_eligibility_vs_screen_conflict, eligible_declared_absent, known_eligible_missing, no_checkable_claim, primary_reported_not_extracted, search_not_executed esketamine-trd-madrs — eligible_declared_absent, search_not_executed finerenone-ckd-t2d-renal — eligible_declared_absent, search_not_executed glp1-ra-mace-t2d — EXTRACTED_NOT_ADMISSIBLE, EXTRACTED_SOURCE_CONFLICT, eligible_declared_absent, search_not_executed iv-iron-hfref-hosp — audit_eligibility_vs_screen_conflict, eligible_declared_absent, known_eligible_missing, search_not_executed melatonin-primary-insomnia-sol — eligible_declared_absent, search_not_executed metformin-pcos-ovulation — eligible_declared_absent, no_checkable_claim, search_not_executed noac-vs-warfarin-af-stroke — eligible_declared_absent, no_checkable_claim, search_not_executed omega3-cardiovascular-events — eligible_declared_absent, search_not_executed pcsk9-mace — eligible_declared_absent, search_not_executed probiotics-aad-prevention — eligible_declared_absent, no_checkable_claim, search_not_executed sacubitril-valsartan-hfref — eligible_declared_absent, no_checkable_claim, search_not_executed semaglutide-obesity-mace — eligible_declared_absent, no_checkable_claim, search_not_executed semaglutide-obesity-weight — eligible_declared_absent, search_not_executed sglt2-ckd-progression — eligible_declared_absent, search_not_executed sglt2-hfref-hosp-cvdeath — eligible_declared_absent, search_not_executed sglt2-primary-prevention-hf — eligible_declared_absent, search_not_executed spironolactone-hfref-mortality — eligible_declared_absent, search_not_executed statins-primary-prevention-elderly — eligible_declared_absent, search_not_executed ticagrelor-vs-clopidogrel-acs — eligible_declared_absent, no_checkable_claim, search_not_executed tocilizumab-covid19-mortality — eligible_declared_absent, search_not_executed tranexamic-acid-pph — eligible_declared_absent, search_not_executed Protocol↔config: 35 divergence(s) across 18 of 32 topics (prose protocol vs executable config, compared as two independent sources; each a defect to resolve or a dated amendment to declare).
```

</details>

<details><summary>Pair 5 of 232 — docs/index.html — Declared strands</summary>

Source ref: `38c04411`; lost SHA-256: `8c1056e4ccd044af03d9589b7fe844ae3255053da184a3118df8f04102ea0766`.

Lost full text:

```text
Declared strands (the single pool is suppressed; these are the endpoint-clean decompositions) Strands A and B measure the SAME endpoint (HF hospitalisation) two incompatible ways -- first-event HR (CONFIRM-HF) vs recurrent rate ratio (AFFIRM-AHF + FAIR-HF2). A hazard ratio of the first event and a rate ratio of all events are not the same quantity and cannot be pooled; the single-pool primary is therefore correctly suppressed. The strands below are the honest decomposition. Strand A — First-event hazard ratio (time to first HF hospitalisation) [ FIRST_EVENT_RATIO ]: CONFIRM-HF 0.39 (HR), k=1 (single trial) Strand B — Recurrent-event rate ratio, HF hospitalisation ALONE [ RATE ]: pooled 0.765 (0.232–2.522), k=2, HKSJ/PM τ²=0.0, crosses null [common-effect sensitivity 0.765 (0.636–0.919), NOT the registered result] Strand C — Recurrent-event rate ratio, HF hospitalisation + CV death COMPOSITE [ RATE ]: pooled 0.807 (0.281–2.312), k=2, HKSJ/PM τ²=0.0, crosses null [common-effect sensitivity 0.807 (0.686–0.949), NOT the registered result] Strand D — Participant-level risk (patients with >=1 HF hospitalisation) [ PARTICIPANT_RISK ]: CONFIRM-HF 0.39 (RR (crude)), k=1 (single trial) Refused cross-endpoint pool: The recurrent-event rate ratios do NOT form one pool. A pool of AFFIRM-AHF's HF-hosp-ALONE rate (0.74) with IRONMAN's HF-hosp+CV-death COMPOSITE rate (0.82) crosses the endpoint dimension of the compatibility key. If forced it would be 0.783 (0.275-2.233) -- this is the 0.783 figure previously treated as the recurrent strand; it mixes endpoints and is refused, not published. — REFUSED -- endpoint mismatch (HF-hosp alone vs composite) . Every effect source-verified; intervals from the canonical engine. The compatibility key keeps strands apart; a cross-strand pool is refused, not computed.
```

Candidate 1 of 1; SHA-256 `b95ce492e867993e7f2a94875863a62df3372a76314e5552dcb46ed352f2404a`:

```text
Declared strands (the single pool is suppressed; these are the endpoint-clean decompositions) Strands A and B measure the SAME endpoint (HF hospitalisation) two incompatible ways -- first-event HR (CONFIRM-HF) vs recurrent rate ratio (AFFIRM-AHF + FAIR-HF2). A hazard ratio of the first event and a rate ratio of all events are not the same quantity and cannot be pooled; the single-pool primary is therefore correctly suppressed. The strands below are the honest decomposition. Strand A — First-event hazard ratio (time to first HF hospitalisation) [ FIRST_EVENT_RATIO ]: CONFIRM-HF 0.39 (HR), k=1 (single trial) Strand B — Recurrent-event rate ratio, HF hospitalisation ALONE [ RATE ]: REFUSED on admission -- saved result withheld: AFFIRM-AHF: P5_family_eligible (family NCT02937454, eligibility UNKNOWN INTERVENTION_CONTRAST_NOT_PROVEN); FAIR-HF2: P5_family_eligible (family NCT03036462, eligibility UNKNOWN INTERVENTION_CONTRAST_NOT_PROVEN). a declared strand pools only admitted members; its saved result is withheld until every member's family eligibility is established (recovery as for any set-aside row) Strand C — Recurrent-event rate ratio, HF hospitalisation + CV death COMPOSITE [ RATE ]: REFUSED on admission -- saved result withheld: AFFIRM-AHF: P5_family_eligible (family NCT02937454, eligibility UNKNOWN INTERVENTION_CONTRAST_NOT_PROVEN); IRONMAN: P5_family_eligible (family NCT02642562, eligibility UNKNOWN INTERVENTION_CONTRAST_NOT_PROVEN). a declared strand pools only admitted members; its saved result is withheld until every member's family eligibility is established (recovery as for any set-aside row) Strand D — Participant-level risk (patients with >=1 HF hospitalisation) [ PARTICIPANT_RISK ]: CONFIRM-HF 0.39 (RR (crude)), k=1 (single trial) Refused cross-endpoint pool: The recurrent-event rate ratios do NOT form one pool. A pool of AFFIRM-AHF's HF-hosp-ALONE rate (0.74) with IRONMAN's HF-hosp+CV-death COMPOSITE rate (0.82) crosses the endpoint dimension of the compatibility key. If forced it would be 0.783 (0.275-2.233) -- this is the 0.783 figure previously treated as the recurrent strand; it mixes endpoints and is refused, not published. — REFUSED -- endpoint mismatch (HF-hosp alone vs composite) . Every effect source-verified; intervals from the canonical engine. The compatibility key keeps strands apart; a cross-strand pool is refused, not computed.
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 6 of 232 — docs/index.html — iv-iron HF-hospitalisation</summary>

Source ref: `38c04411`; lost SHA-256: `fd039519a6457ab24b1a9a7c785a1580d7c642b019cf23e108eb454344175c29`.

Lost full text:

```text
iv-iron HF-hospitalisation: declared strands (topic-page and index render the same artefact) Declared strands (the single pool is suppressed; these are the endpoint-clean decompositions) Strands A and B measure the SAME endpoint (HF hospitalisation) two incompatible ways -- first-event HR (CONFIRM-HF) vs recurrent rate ratio (AFFIRM-AHF + FAIR-HF2). A hazard ratio of the first event and a rate ratio of all events are not the same quantity and cannot be pooled; the single-pool primary is therefore correctly suppressed. The strands below are the honest decomposition. Strand A — First-event hazard ratio (time to first HF hospitalisation) [ FIRST_EVENT_RATIO ]: CONFIRM-HF 0.39 (HR), k=1 (single trial) Strand B — Recurrent-event rate ratio, HF hospitalisation ALONE [ RATE ]: pooled 0.765 (0.232–2.522), k=2, HKSJ/PM τ²=0.0, crosses null [common-effect sensitivity 0.765 (0.636–0.919), NOT the registered result] Strand C — Recurrent-event rate ratio, HF hospitalisation + CV death COMPOSITE [ RATE ]: pooled 0.807 (0.281–2.312), k=2, HKSJ/PM τ²=0.0, crosses null [common-effect sensitivity 0.807 (0.686–0.949), NOT the registered result] Strand D — Participant-level risk (patients with >=1 HF hospitalisation) [ PARTICIPANT_RISK ]: CONFIRM-HF 0.39 (RR (crude)), k=1 (single trial) Refused cross-endpoint pool: The recurrent-event rate ratios do NOT form one pool. A pool of AFFIRM-AHF's HF-hosp-ALONE rate (0.74) with IRONMAN's HF-hosp+CV-death COMPOSITE rate (0.82) crosses the endpoint dimension of the compatibility key. If forced it would be 0.783 (0.275-2.233) -- this is the 0.783 figure previously treated as the recurrent strand; it mixes endpoints and is refused, not published. — REFUSED -- endpoint mismatch (HF-hosp alone vs composite) . Every effect source-verified; intervals from the canonical engine. The compatibility key keeps strands apart; a cross-strand pool is refused, not computed.
```

Candidate 1 of 1; SHA-256 `b91e2c182a653f9ec6634489b18a8b4e5cd1fc51657682912f830837cba8b381`:

```text
iv-iron HF-hospitalisation: declared strands (topic-page and index render the same artefact) Declared strands (the single pool is suppressed; these are the endpoint-clean decompositions) Strands A and B measure the SAME endpoint (HF hospitalisation) two incompatible ways -- first-event HR (CONFIRM-HF) vs recurrent rate ratio (AFFIRM-AHF + FAIR-HF2). A hazard ratio of the first event and a rate ratio of all events are not the same quantity and cannot be pooled; the single-pool primary is therefore correctly suppressed. The strands below are the honest decomposition. Strand A — First-event hazard ratio (time to first HF hospitalisation) [ FIRST_EVENT_RATIO ]: CONFIRM-HF 0.39 (HR), k=1 (single trial) Strand B — Recurrent-event rate ratio, HF hospitalisation ALONE [ RATE ]: REFUSED on admission -- saved result withheld: AFFIRM-AHF: P5_family_eligible (family NCT02937454, eligibility UNKNOWN INTERVENTION_CONTRAST_NOT_PROVEN); FAIR-HF2: P5_family_eligible (family NCT03036462, eligibility UNKNOWN INTERVENTION_CONTRAST_NOT_PROVEN). a declared strand pools only admitted members; its saved result is withheld until every member's family eligibility is established (recovery as for any set-aside row) Strand C — Recurrent-event rate ratio, HF hospitalisation + CV death COMPOSITE [ RATE ]: REFUSED on admission -- saved result withheld: AFFIRM-AHF: P5_family_eligible (family NCT02937454, eligibility UNKNOWN INTERVENTION_CONTRAST_NOT_PROVEN); IRONMAN: P5_family_eligible (family NCT02642562, eligibility UNKNOWN INTERVENTION_CONTRAST_NOT_PROVEN). a declared strand pools only admitted members; its saved result is withheld until every member's family eligibility is established (recovery as for any set-aside row) Strand D — Participant-level risk (patients with >=1 HF hospitalisation) [ PARTICIPANT_RISK ]: CONFIRM-HF 0.39 (RR (crude)), k=1 (single trial) Refused cross-endpoint pool: The recurrent-event rate ratios do NOT form one pool. A pool of AFFIRM-AHF's HF-hosp-ALONE rate (0.74) with IRONMAN's HF-hosp+CV-death COMPOSITE rate (0.82) crosses the endpoint dimension of the compatibility key. If forced it would be 0.783 (0.275-2.233) -- this is the 0.783 figure previously treated as the recurrent strand; it mixes endpoints and is refused, not published. — REFUSED -- endpoint mismatch (HF-hosp alone vs composite) . Every effect source-verified; intervals from the canonical engine. The compatibility key keeps strands apart; a cross-strand pool is refused, not computed.
```

</details>

<details><summary>Pair 7 of 232 — docs/index.html — Gate scorecard</summary>

Source ref: `38c04411`; lost SHA-256: `576e0b24d56ef4bea6a237af3ffc2bb6107edcb3784e2558b285d28014a5d5bf`.

Lost full text:

```text
Gate scorecard: plant validations and production refusals Adjudication coverage first, so the unresolved cannot disappear: 59 of 131 refusal events are adjudicated ( 45% ); 0 of 131 are independently adjudicated ( 0% ); over PRODUCTION refusals alone, 1 of 16 adjudicated (6%) and 0 of 16 independently (0%). No precision below is to be read as if the unresolved remainder were not there; an UNRESOLVED event is neither a true nor a false refusal. 62 production gates accounted for ; 131 events; 58 adjudicated plant validations; 62 are UNVALIDATED ; 72 events are UNRESOLVED ; adjudicator_independence is 0.000 ; 0 gates have an adjudicated production true refusal; 1 have an adjudicated false refusal: verify_all.limb_fixstate (the named pessimistic incident: the fix-state checker refused an evidence-only commit because its subject contained 'refusing'; commit 6b1039cd records the structural correction; author-adjudicated, not independent). If the same environment labels its own gate outputs true or false, that is: system produces output -> system labels its own output correct -> agreement read as validation (the 6/6 recall shape). So every refusal is an EVENT with an ADJUDICATION OBJECT, and a gate's numbers are computed only from those objects. The scorecard rule is: a gate with no adjudicated true refusal in production is UNVALIDATED, not green. precision is reported only beside its adjudication coverage; an UNRESOLVED refusal is neither. adjudicator_independence is the share of adjudications made by an external_auditor; today it is expected to be 0 because no external-auditor adjudication is recorded. Served JSON: gate_scorecard.json . gate computed line census.claim_check adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 census.compatibility_check adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 2 census.interval_provenance adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 census.proposition_check adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 deploy.attest adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 2 deploy.check_artifact adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 2; UNRESOLVED: 2 evidence_index.check adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_access_claim_supported adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_adjustment_span_backed adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 0 gate.check_arm_object_contract adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_cache_tracked adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 1 gate.check_certainty_surfaces_agree adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 0 gate.check_certificate adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 0 gate.check_claimgraph adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_compat_key_underlying adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_controls adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 3 gate.check_cross_source adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_duplicate_publication adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 2 gate.check_eligibility_chain adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_fetch_complete adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 2 gate.check_harms_complete adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_harms_synthesis_gated adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 0 gate.check_known_missing_panel adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 0 gate.check_limb1 adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_limb2 adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 2 gate.check_limitation_decision_links adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_manuscript_numbers adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_method_matches_scale adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_no_double_counted_trial adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_no_independent_corroboration_claim adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 0 gate.check_parity_our_k adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_pivotal_present adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_pooled_verified adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_population_identity adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_preregistration_not_build adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 1 gate.check_prespecification_in_protocol adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_primary_result adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_propositions adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_reproduction adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 1 gate.check_result_change_countersigned adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 0 gate.check_retraction adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_rob_rederivable adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_rob_sensitivity_surfaces adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 0 gate.check_scope_identity adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_stale_heterogeneity_surfaces adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 0 honest_ratchet.compare_blocks adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 2; UNRESOLVED: 2 hook.commit_msg adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 hook.pre_commit adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 invalidation.identifier_scope adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 2 pipeline.structural_query_classifier adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 2 ruleset.required_verify adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 1 production refusals = coverage 0.000); plants: 0; UNRESOLVED: 3 verify_all.limb_fixstate adjudicated precision TP/(TP+FP) = 0.000 (1 adjudicated of 1 production refusals = coverage 1.000); plants: 2; UNRESOLVED: 3 verify_all.limb_gate_every_page adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 verify_all.limb_gate_gaps adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 1 verify_all.limb_gate_scorecard adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 2; UNRESOLVED: 1 verify_all.limb_heldout adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 2; UNRESOLVED: 2 verify_all.limb_honest_ratchet adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 2; UNRESOLVED: 2 verify_all.limb_index_currency adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 1 production refusals = coverage 0.000); plants: 2; UNRESOLVED: 3 verify_all.limb_leak_scan adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 2; UNRESOLVED: 1 verify_all.limb_reproduction adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 verify_all.limb_search_completeness adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 0 verify_all.limb_unit_tests adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 2; UNRESOLVED: 2
```

Candidate 1 of 1; SHA-256 `5fed878b4e53568e5a3a1fd7f0760e8d56997ebe5ce8149b84fbf3b2aa4524dd`:

```text
Gate scorecard: plant validations and production refusals Adjudication coverage first, so the unresolved cannot disappear: 60 of 133 refusal events are adjudicated ( 45% ); 0 of 133 are independently adjudicated ( 0% ); over PRODUCTION refusals alone, 1 of 17 adjudicated (6%) and 0 of 17 independently (0%). No precision below is to be read as if the unresolved remainder were not there; an UNRESOLVED event is neither a true nor a false refusal. 63 production gates accounted for ; 133 events; 59 adjudicated plant validations; 63 are UNVALIDATED ; 73 events are UNRESOLVED ; adjudicator_independence is 0.000 ; 0 gates have an adjudicated production true refusal; 1 have an adjudicated false refusal: verify_all.limb_fixstate (the named pessimistic incident: the fix-state checker refused an evidence-only commit because its subject contained 'refusing'; commit 6b1039cd records the structural correction; author-adjudicated, not independent). If the same environment labels its own gate outputs true or false, that is: system produces output -> system labels its own output correct -> agreement read as validation (the 6/6 recall shape). So every refusal is an EVENT with an ADJUDICATION OBJECT, and a gate's numbers are computed only from those objects. The scorecard rule is: a gate with no adjudicated true refusal in production is UNVALIDATED, not green. precision is reported only beside its adjudication coverage; an UNRESOLVED refusal is neither. adjudicator_independence is the share of adjudications made by an external_auditor; today it is expected to be 0 because no external-auditor adjudication is recorded. Served JSON: gate_scorecard.json . gate computed line census.claim_check adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 census.compatibility_check adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 2 census.interval_provenance adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 census.proposition_check adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 deploy.attest adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 2 deploy.check_artifact adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 2; UNRESOLVED: 2 evidence_index.check adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_access_claim_supported adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_adjustment_span_backed adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 0 gate.check_admission_enforced adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 1 production refusals = coverage 0.000); plants: 1; UNRESOLVED: 1 gate.check_arm_object_contract adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_cache_tracked adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 1 gate.check_certainty_surfaces_agree adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 0 gate.check_certificate adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 0 gate.check_claimgraph adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_compat_key_underlying adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_controls adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 3 gate.check_cross_source adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_duplicate_publication adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 2 gate.check_eligibility_chain adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_fetch_complete adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 2 gate.check_harms_complete adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_harms_synthesis_gated adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 0 gate.check_known_missing_panel adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 0 gate.check_limb1 adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_limb2 adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 2 gate.check_limitation_decision_links adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_manuscript_numbers adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_method_matches_scale adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_no_double_counted_trial adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_no_independent_corroboration_claim adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 0 gate.check_parity_our_k adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_pivotal_present adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_pooled_verified adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_population_identity adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_preregistration_not_build adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 1 gate.check_prespecification_in_protocol adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_primary_result adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_propositions adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_reproduction adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 1 gate.check_result_change_countersigned adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 0 gate.check_retraction adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_rob_rederivable adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_rob_sensitivity_surfaces adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 0 gate.check_scope_identity adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 gate.check_stale_heterogeneity_surfaces adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 0 honest_ratchet.compare_blocks adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 2; UNRESOLVED: 2 hook.commit_msg adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 hook.pre_commit adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 invalidation.identifier_scope adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 2 pipeline.structural_query_classifier adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 2 ruleset.required_verify adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 1 production refusals = coverage 0.000); plants: 0; UNRESOLVED: 3 verify_all.limb_fixstate adjudicated precision TP/(TP+FP) = 0.000 (1 adjudicated of 1 production refusals = coverage 1.000); plants: 2; UNRESOLVED: 3 verify_all.limb_gate_every_page adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 verify_all.limb_gate_gaps adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 0; UNRESOLVED: 1 verify_all.limb_gate_scorecard adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 2; UNRESOLVED: 1 verify_all.limb_heldout adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 2; UNRESOLVED: 2 verify_all.limb_honest_ratchet adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 2; UNRESOLVED: 2 verify_all.limb_index_currency adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 1 production refusals = coverage 0.000); plants: 2; UNRESOLVED: 3 verify_all.limb_leak_scan adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 2; UNRESOLVED: 1 verify_all.limb_reproduction adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 1 verify_all.limb_search_completeness adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 1; UNRESOLVED: 0 verify_all.limb_unit_tests adjudicated precision TP/(TP+FP) = no adjudicated production refusal - UNVALIDATED, not green (0 adjudicated of 0 production refusals = coverage no production refusals); plants: 2; UNRESOLVED: 2
```

</details>

<details><summary>Pair 8 of 232 — docs/index.html — Parity with the published comparator</summary>

Source ref: `38c04411`; lost SHA-256: `13cde4ed23a642677780f367ebfa67bf05ad4fb4f50fa89615f7d6198b76174e`.

Lost full text:

```text
Parity with the published comparator (the finishing metric) For each same-scope topic: our pooled k vs the comparable comparator k (the comparator's pooled list, enumerated from its own references/full text, after removing trials that are out of scope, double-counted substudies, observational, or non-prespecified for the outcome). 3 of 21 topics with parity rows have an identical computed trial set; identical-set agreement is arithmetic replication, not independent corroboration. Every remaining relation has a named reason. This is a measurement snapshot (the enumeration is model-assisted; scope calls are assessments, and each pooled recovery was verified against source before it counted). Topic Our k Comparator k Computed relation Named reason for any difference finerenone-ckd-t2d-renal 2 2 IDENTICAL_SET arithmetic agreement -- same trials; overlapping inputs do not constitute an independent evidence set comparator renal-composite pool = FIDELIO+FIGARO = our exact pool glp1-ra-mace-t2d 8 7 SUPERSET superset -- the comparator trial set is contained in ours 8 pooled including SOUL (PMID 40162642, 2025, source-verified HR 0.86) which postdates the comparator meta (k=7); the remaining gap ELIXA is a 4-point MACE (estimand) correctly declared-absent sglt2-hfref-hosp-cvdeath 2 2 PARITY_REFUTED_BY_N participant-count refutation -- comparator n 9199 exceeds our shared-trial n 4744 by 4455; sets differ Pandey LVEF<=40 subgroup reports n=9199 in cached comparator text, while our shared DAPA-HF + EMPEROR-Reduced rows sum to n=8474; excess 725 indicates the comparator subgroup includes an additional reduced-EF subset outside our SGLT2-only HFrEF pool. balanced-crystalloids-vs-saline-mortality 2 5 OVERLAPPING INFERRED overlapping -- neither trial set contains the other Design-key update: primary mortality pool is now k=2 (PLUS + BaSICS). SMART, SALT, and SPLIT are cluster-crossover trials whose effects were reconstructed through the simple parallel-group path; they are refused unless an explicit design_adjustment is attached. Comparator mortality pool remains k=5, but the three refused trials are disclosed exclusions rather than pooled to preserve variance validity. ticagrelor-vs-clopidogrel-acs 2 1 SUPERSET INFERRED superset -- the comparator trial set is contained in ours comparator k=5 but 3 are a PLATO substudy(double-count)/observational/unindexed; 1 valid RCT (PLATO) = ours colchicine-postop-af 3 7 OVERLAPPING INFERRED overlapping -- neither trial set contains the other Comparator (Zhao 2022) pools 9; comparable same-scope k=7 (excludes 2 post-PVI-ablation trials). Decomposed: 4 POOLED BY US (COPPS-2 25172965, END-AF 27502857, END-AF-low-dose 32720823, and Post-CABG Arrhythmias RCT 42132185 recovered by the PREVENTION_TRIAL_TITLE_OMITS_OUTCOME screening fix — its title names 'Post-CABG Arrhythmias' not 'atrial fibrillation'; RR 0.37 verified against the abstract); Bessissow 29237033 NOT pooled (declared-absent); of the rest: 2 SCOPE-excluded (Deftereos x2, post-pulmonary-vein-isolation ablation recurrence, not post-surgery POAF); 1 MULTI-ARM (Zarpelon 27223641, pre+post-op dosing + late-admission single-dose subgroup, dose/timing ambiguity); 1 REACH (Sarzaeem 2014, no PMID/not in corpus); 2 flagged ELIGIBLE and now screened IN by the prevention fix but NOT cleanly poolable from the abstract (COPPS AF substudy 22090167 and COCS 36286314: real POAF percentages without exact per-arm N or a CI, declared-absent on ambiguity). So the k gap is scope + multi-arm + reach + percentage-only trials, not a search/extraction failure. spironolactone-hfref-mortality 3 2 SUPERSET INFERRED superset -- the comparator trial set is contained in ours 2/2 within PREREGISTERED scope: comparator HFrEF-mortality pool is RALES/EPHESUS/EMPHASIS, but EPHESUS is acute-post-MI LV dysfunction, which our population_none preregisters as excluded (chronic HFrEF only). RALES + EMPHASIS = our pool. EPHESUS is a named, preregistered scope difference, not a miss. noac-vs-warfarin-af-stroke 4 4 IDENTICAL_SET arithmetic agreement -- same trials; overlapping inputs do not constitute an independent evidence set CLOSED to parity: ENGAGE-AF added + RE-LY switched to the approved 150 mg dose, via a documented pre-specified approved-dose rule (dabigatran 150 mg RR 0.66; edoxaban 60 mg ITT HR 0.87), both verified against source. Pooled RR 0.805 (0.658-0.984). Pairwise subset of the DOAC-vs-warfarin evidence; matches the comparable comparator k=4. colchicine-recurrent-pericarditis 2 4 OVERLAPPING INFERRED overlapping -- neither trial set contains the other Comparator (Imazio 2012) comparable k=4. Decomposed: 2 POOLED BY US (24694983, 21873705); of the gap trials, 0 are eligible-not-pooled recoverable misses. CORE (16186468) and COPE (16186437) are OPEN-LABEL (design-excluded: we require double-blind) — CORE is the exact recurrent-pericarditis outcome but open-label; Finkelstein (12574898) is postpericardiotomy-syndrome PREVENTION (scope-excluded). So every gap trial is design- or scope-excluded by the preregistered screen — the harness is more rigorous than the comparator, not missing trials. pcsk9-mace 2 12 DOMINANT_SUBSET INFERRED dominant-trial subset -- ours is contained in the comparator; carries 87% of comparator patients/events (source: parity reason text) 2/12 but our 2 (FOURIER+ODYSSEY) = ~87% of comparator patients; 10 gaps = non-prespecified MACE tallies iv-iron-hfref-hosp 2 3 OVERLAPPING INFERRED overlapping -- neither trial set contains the other 2/3. Gap = HEART-FID + AFFIRM-AHF, refused on estimand: CT.gov labels HEART-FID heart-failure hospitalizations as COUNT_OF_PARTICIPANTS (297/1532 vs 332/1533) but the publication says "297 hospitalizations" = RECURRENT EVENTS, not patients — pooling the CT.gov count as a binary would produce a wrong number, so the recurrent-event guard refuses it. FAIR-HF = no extractable data; EFFECT-HF = open-label (design-excluded). CONFIRM-HF recovered. omega3-cardiovascular-events 5 15 OVERLAPPING INFERRED overlapping -- neither trial set contains the other Comparator pool decomposed against our preregistered screen: 7 POOLED BY US (including SU.FOL.OM3, PMID 21115589, whose omega-3 arm we pool). OMEMI and OMEGA-REMODEL are eligible but NOT pooled (declared-absent: OMEMI primary publication not linked; OMEGA-REMODEL pending an exposure-duration rule). Of the comparator's remaining trials: 6 OPEN-LABEL design-excluded (DART, GISSI-Prevenzione, JELIS, THIS-DIET, Doi, HEARTS); 5 SCOPE-excluded arrhythmia/eye/mobility (SOFA, FORWARD, AFFORD, AREDS2, ENRGISE); and 4 double-blind hard-CV trials screened-in but with DIFFERING composite/population (Nilsen post-MI, GISSI-HF, DOIT, OMEGA post-MI) whose pooling would mix estimands, declined unless the composite matches. The k gap is DESIGN-BAR + SCOPE + estimand-identity, not a search miss. sglt2-ckd-progression 3 10 SUBSET INFERRED subset -- ours is contained in the comparator 3/10. Gap = 7 CV/HF SGLT2 trials that report a kidney composite as a SECONDARY endpoint. The MATCHING hard-kidney composite (sustained >=40% eGFR decline / ESKD / renal death) exists in the CANVAS/CREDENCE publications, but its per-arm data is IPD-only and is not in our committed cached abstract; the PMC full-text adapter did not run in this build, so full-text access was not established — CT.gov posts a DIFFERENT composite (CV-death-inclusive, or albuminuria-based) which is not our estimand. We decline what we cannot verify against a matching-definition committed source; the comparator pooled these via IPD. tranexamic-acid-pph 1 5 SUBSET INFERRED subset -- ours is contained in the comparator 1/5. Gap = WOMAN-2 / TRAAP / TRAAP-2 / TXA-MFMU. Reachable (all found in PubMed) but EXCLUDED BY SCOPE, not a search failure: every one tests PROPHYLACTIC tranexamic acid around delivery to PREVENT PPH, whereas this review pools TREATMENT of clinically diagnosed PPH (the WOMAN trial estimand). A prophylaxis-vs-treatment PICO mismatch; the comparator mixes the two. corticosteroids-covid19-mortality 1 5 OVERLAPPING INFERRED overlapping -- neither trial set contains the other 1/5. Comparator (WHO REACT prospective MA) used investigator-supplied 28-day mortality not in the trial publications. In our committed cached abstracts, only RECOVERY reports 28-day all-cause mortality counts; the other trials report it only in full text, which is not in our committed cache, and their CT.gov results post no mortality table. The PMC full-text adapter did not run in this build, so the refusal rests on absence from the committed abstract, not on a tested access barrier. statins-primary-prevention-elderly 2 0 COMPARATOR_INVALID comparator invalid -- not an RCT meta / not the same question comparator pools 12 OBSERVATIONAL studies, 0 RCTs = not an RCT-meta comparator [our_k = our full pooled k (2); comparator is observational-only, so no valid RCT-meta same-scope comparison exists]. denosumab-vertebral-fracture 1 NOT_ENUMERABLE not enumerable -- comparator trial list and k are not exposed comparator is a 55-node NMA; trial list only in supplement probiotics-aad-prevention 11 42 OVERLAPPING INFERRED overlapping -- neither trial set contains the other Comparator pool decomposed (Goodman ~42 adult AAD RCTs, classified against our screen): 9 POOLED BY US from its table + 6 more we pool (pediatric/newer, outside its adult table) = our 15. Of the other 33 rows: 14 NOT ELIGIBLE (H. pylori-eradication or C. difficile-only populations, or open-label/no-treatment control); 13 DEFINITION-MISMATCH (AAD defined as >=3 loose stools over >=2 DAYS, not the 24h standard our pool uses); 3 REACH (not in corpus); and and 3 flagged-but-on-verification-unrecoverable (Gao multi-arm, Ouwehand screen-excluded, Wright %-only). So 15 vs 42 is overwhelmingly ineligibility + definition-heterogeneity, not a search/extraction failure; 3 recoverable candidates are verification targets. (+1 this session: 39529939 recovered from full text.) [our_k = our full pooled k (16); the table decomposition above predates one later-added pooled trial]. semaglutide-obesity-weight 2 2 IDENTICAL_SET INFERRED arithmetic agreement -- same trials; overlapping inputs do not constitute an independent evidence set EXACT same-scope, same-timepoint parity. Our pool = STEP-1 (Wilding) + STEP-3 (Wadden), both once-weekly semaglutide 2.4 mg vs placebo at the pre-registered Week 68 primary; both are in the comparator's (PMID 42536519) pool too. The comparator's other 2 of 4 are out of our pre-registered scope: O'Neil-2018 is a phase-2 DAILY dose-ranging trial with a liraglutide arm, and Rubino/STEP-4 is a weight-loss-MAINTENANCE (randomised-withdrawal) estimand we exclude. We also RETRIEVED two regional 2.4 mg-vs-placebo trials (STEP-12 China, Korean STEP) but DECLARED THEM ABSENT for TIMEPOINT MISMATCH (Week 44 end-of-treatment, not the pre-registered Week 68) — a timepoint-consistency guard refusing to pad k by mixing follow-up durations. Pooled MD -11.84% (-25.13, 1.44), tau2=1.86; the wide CI is the honest k=2 HKSJ interval (t on 1 df), not a lowered bar. esketamine-trd-madrs 3 4 OVERLAPPING overlapping -- neither trial set contains the other Comparator (Front Psychiatry 2026, PMID 42490943) acute MADRS-change-from-baseline Day-28 primary pooled 4 RCTs (N=937, MD -2.99 [-5.10,-0.88]; verified in its own results table '937 (4 RCTs)'). The current review primary pool contains 4 effect objects, so parity.our_k is 4. Same-scope membership is represented by the parity_relation and outcome-membership objects; this row does not assert a separate gap-trial count. melatonin-primary-insomnia-sol 1 15 OVERLAPPING INFERRED overlapping -- neither trial set contains the other Comparator (PLoS One 2013, PMID 23691095) sleep-onset-latency pool = 15 RCTs (verified from its heterogeneity df: Q=31.9, df=14 => k=15; WMD 7.06 min [4.37,9.75]). We pool 1 (prolonged-release melatonin 2 mg, Wade 2011 / Circadin / NCT00397189, adult primary insomnia, per-arm mean/SD from CT.gov). The comparator's pool is deliberately BROADER in scope: of its 19 included studies, 4 are delayed-sleep-phase syndrome, 1 is REM sleep behaviour disorder, and >=3 are in CHILDREN (van Geijlswijk 2010, Smits 2003, Smits 2001) - all outside our adult-primary-insomnia scope - plus multiple cross-over designs and immediate-release doses from 0.05 mg/kg to 5 mg (a different formulation/estimand than our prolonged-release pool). The exact 15 SOL forest-plot trial identities are NOT in the comparator's cached OA full text (Figure 1 row labels absent), so the remaining per-trial split cannot be completed from source; several are pre-2000 cross-over trials with no accessible per-arm data. So this is a SCOPE (formulation/population/estimand) + partial REACH gap, honestly bounded - not a like-for-like shortfall. This is one of our narrowest pools and is shown as such.
```

Candidate 1 of 1; SHA-256 `bad473bb4bf26dddb2d44a6c12067c0073507bb8fd7122ca4563cb64e69bcdc6`:

```text
Parity with the published comparator (the finishing metric) For each same-scope topic: our pooled k vs the comparable comparator k (the comparator's pooled list, enumerated from its own references/full text, after removing trials that are out of scope, double-counted substudies, observational, or non-prespecified for the outcome). 3 of 21 topics with parity rows have an identical computed trial set; identical-set agreement is arithmetic replication, not independent corroboration. Every remaining relation has a named reason. This is a measurement snapshot (the enumeration is model-assisted; scope calls are assessments, and each pooled recovery was verified against source before it counted). Topic Our k Comparator k Computed relation Named reason for any difference finerenone-ckd-t2d-renal 2 2 IDENTICAL_SET arithmetic agreement -- same trials; overlapping inputs do not constitute an independent evidence set comparator renal-composite pool = FIDELIO+FIGARO = our exact pool glp1-ra-mace-t2d 7 7 OVERLAPPING overlapping -- neither trial set contains the other 8 pooled including SOUL (PMID 40162642, 2025, source-verified HR 0.86) which postdates the comparator meta (k=7); the remaining gap ELIXA is a 4-point MACE (estimand) correctly declared-absent sglt2-hfref-hosp-cvdeath 2 2 PARITY_REFUTED_BY_N participant-count refutation -- comparator n 9199 exceeds our shared-trial n 4744 by 4455; sets differ Pandey LVEF<=40 subgroup reports n=9199 in cached comparator text, while our shared DAPA-HF + EMPEROR-Reduced rows sum to n=8474; excess 725 indicates the comparator subgroup includes an additional reduced-EF subset outside our SGLT2-only HFrEF pool. balanced-crystalloids-vs-saline-mortality 2 5 OVERLAPPING INFERRED overlapping -- neither trial set contains the other Design-key update: primary mortality pool is now k=2 (PLUS + BaSICS). SMART, SALT, and SPLIT are cluster-crossover trials whose effects were reconstructed through the simple parallel-group path; they are refused unless an explicit design_adjustment is attached. Comparator mortality pool remains k=5, but the three refused trials are disclosed exclusions rather than pooled to preserve variance validity. ticagrelor-vs-clopidogrel-acs 2 1 SUPERSET INFERRED superset -- the comparator trial set is contained in ours comparator k=5 but 3 are a PLATO substudy(double-count)/observational/unindexed; 1 valid RCT (PLATO) = ours colchicine-postop-af 2 7 OVERLAPPING INFERRED overlapping -- neither trial set contains the other Comparator (Zhao 2022) pools 9; comparable same-scope k=7 (excludes 2 post-PVI-ablation trials). Decomposed: 4 POOLED BY US (COPPS-2 25172965, END-AF 27502857, END-AF-low-dose 32720823, and Post-CABG Arrhythmias RCT 42132185 recovered by the PREVENTION_TRIAL_TITLE_OMITS_OUTCOME screening fix — its title names 'Post-CABG Arrhythmias' not 'atrial fibrillation'; RR 0.37 verified against the abstract); Bessissow 29237033 NOT pooled (declared-absent); of the rest: 2 SCOPE-excluded (Deftereos x2, post-pulmonary-vein-isolation ablation recurrence, not post-surgery POAF); 1 MULTI-ARM (Zarpelon 27223641, pre+post-op dosing + late-admission single-dose subgroup, dose/timing ambiguity); 1 REACH (Sarzaeem 2014, no PMID/not in corpus); 2 flagged ELIGIBLE and now screened IN by the prevention fix but NOT cleanly poolable from the abstract (COPPS AF substudy 22090167 and COCS 36286314: real POAF percentages without exact per-arm N or a CI, declared-absent on ambiguity). So the k gap is scope + multi-arm + reach + percentage-only trials, not a search/extraction failure. spironolactone-hfref-mortality 1 2 SUBSET INFERRED subset -- ours is contained in the comparator 2/2 within PREREGISTERED scope: comparator HFrEF-mortality pool is RALES/EPHESUS/EMPHASIS, but EPHESUS is acute-post-MI LV dysfunction, which our population_none preregisters as excluded (chronic HFrEF only). RALES + EMPHASIS = our pool. EPHESUS is a named, preregistered scope difference, not a miss. noac-vs-warfarin-af-stroke 4 4 IDENTICAL_SET arithmetic agreement -- same trials; overlapping inputs do not constitute an independent evidence set CLOSED to parity: ENGAGE-AF added + RE-LY switched to the approved 150 mg dose, via a documented pre-specified approved-dose rule (dabigatran 150 mg RR 0.66; edoxaban 60 mg ITT HR 0.87), both verified against source. Pooled RR 0.805 (0.658-0.984). Pairwise subset of the DOAC-vs-warfarin evidence; matches the comparable comparator k=4. colchicine-recurrent-pericarditis 2 4 OVERLAPPING INFERRED overlapping -- neither trial set contains the other Comparator (Imazio 2012) comparable k=4. Decomposed: 2 POOLED BY US (24694983, 21873705); of the gap trials, 0 are eligible-not-pooled recoverable misses. CORE (16186468) and COPE (16186437) are OPEN-LABEL (design-excluded: we require double-blind) — CORE is the exact recurrent-pericarditis outcome but open-label; Finkelstein (12574898) is postpericardiotomy-syndrome PREVENTION (scope-excluded). So every gap trial is design- or scope-excluded by the preregistered screen — the harness is more rigorous than the comparator, not missing trials. pcsk9-mace 1 12 DOMINANT_SUBSET INFERRED dominant-trial subset -- ours is contained in the comparator; carries 87% of comparator patients/events (source: parity reason text) 2/12 but our 2 (FOURIER+ODYSSEY) = ~87% of comparator patients; 10 gaps = non-prespecified MACE tallies iv-iron-hfref-hosp 1 3 OVERLAPPING INFERRED overlapping -- neither trial set contains the other 2/3. Gap = HEART-FID + AFFIRM-AHF, refused on estimand: CT.gov labels HEART-FID heart-failure hospitalizations as COUNT_OF_PARTICIPANTS (297/1532 vs 332/1533) but the publication says "297 hospitalizations" = RECURRENT EVENTS, not patients — pooling the CT.gov count as a binary would produce a wrong number, so the recurrent-event guard refuses it. FAIR-HF = no extractable data; EFFECT-HF = open-label (design-excluded). CONFIRM-HF recovered. omega3-cardiovascular-events 1 15 OVERLAPPING INFERRED overlapping -- neither trial set contains the other Comparator pool decomposed against our preregistered screen: 7 POOLED BY US (including SU.FOL.OM3, PMID 21115589, whose omega-3 arm we pool). OMEMI and OMEGA-REMODEL are eligible but NOT pooled (declared-absent: OMEMI primary publication not linked; OMEGA-REMODEL pending an exposure-duration rule). Of the comparator's remaining trials: 6 OPEN-LABEL design-excluded (DART, GISSI-Prevenzione, JELIS, THIS-DIET, Doi, HEARTS); 5 SCOPE-excluded arrhythmia/eye/mobility (SOFA, FORWARD, AFFORD, AREDS2, ENRGISE); and 4 double-blind hard-CV trials screened-in but with DIFFERING composite/population (Nilsen post-MI, GISSI-HF, DOIT, OMEGA post-MI) whose pooling would mix estimands, declined unless the composite matches. The k gap is DESIGN-BAR + SCOPE + estimand-identity, not a search miss. sglt2-ckd-progression 3 10 SUBSET INFERRED subset -- ours is contained in the comparator 3/10. Gap = 7 CV/HF SGLT2 trials that report a kidney composite as a SECONDARY endpoint. The MATCHING hard-kidney composite (sustained >=40% eGFR decline / ESKD / renal death) exists in the CANVAS/CREDENCE publications, but its per-arm data is IPD-only and is not in our committed cached abstract; the PMC full-text adapter did not run in this build, so full-text access was not established — CT.gov posts a DIFFERENT composite (CV-death-inclusive, or albuminuria-based) which is not our estimand. We decline what we cannot verify against a matching-definition committed source; the comparator pooled these via IPD. tranexamic-acid-pph 1 5 SUBSET INFERRED subset -- ours is contained in the comparator 1/5. Gap = WOMAN-2 / TRAAP / TRAAP-2 / TXA-MFMU. Reachable (all found in PubMed) but EXCLUDED BY SCOPE, not a search failure: every one tests PROPHYLACTIC tranexamic acid around delivery to PREVENT PPH, whereas this review pools TREATMENT of clinically diagnosed PPH (the WOMAN trial estimand). A prophylaxis-vs-treatment PICO mismatch; the comparator mixes the two. corticosteroids-covid19-mortality 1 5 OVERLAPPING INFERRED overlapping -- neither trial set contains the other 1/5. Comparator (WHO REACT prospective MA) used investigator-supplied 28-day mortality not in the trial publications. In our committed cached abstracts, only RECOVERY reports 28-day all-cause mortality counts; the other trials report it only in full text, which is not in our committed cache, and their CT.gov results post no mortality table. The PMC full-text adapter did not run in this build, so the refusal rests on absence from the committed abstract, not on a tested access barrier. statins-primary-prevention-elderly 1 0 COMPARATOR_INVALID comparator invalid -- not an RCT meta / not the same question comparator pools 12 OBSERVATIONAL studies, 0 RCTs = not an RCT-meta comparator [our_k = our full pooled k (2); comparator is observational-only, so no valid RCT-meta same-scope comparison exists]. denosumab-vertebral-fracture 1 NOT_ENUMERABLE not enumerable -- comparator trial list and k are not exposed comparator is a 55-node NMA; trial list only in supplement probiotics-aad-prevention 16 42 OVERLAPPING INFERRED overlapping -- neither trial set contains the other Comparator pool decomposed (Goodman ~42 adult AAD RCTs, classified against our screen): 9 POOLED BY US from its table + 6 more we pool (pediatric/newer, outside its adult table) = our 15. Of the other 33 rows: 14 NOT ELIGIBLE (H. pylori-eradication or C. difficile-only populations, or open-label/no-treatment control); 13 DEFINITION-MISMATCH (AAD defined as >=3 loose stools over >=2 DAYS, not the 24h standard our pool uses); 3 REACH (not in corpus); and and 3 flagged-but-on-verification-unrecoverable (Gao multi-arm, Ouwehand screen-excluded, Wright %-only). So 15 vs 42 is overwhelmingly ineligibility + definition-heterogeneity, not a search/extraction failure; 3 recoverable candidates are verification targets. (+1 this session: 39529939 recovered from full text.) [our_k = our full pooled k (16); the table decomposition above predates one later-added pooled trial]. semaglutide-obesity-weight 2 2 IDENTICAL_SET INFERRED arithmetic agreement -- same trials; overlapping inputs do not constitute an independent evidence set EXACT same-scope, same-timepoint parity. Our pool = STEP-1 (Wilding) + STEP-3 (Wadden), both once-weekly semaglutide 2.4 mg vs placebo at the pre-registered Week 68 primary; both are in the comparator's (PMID 42536519) pool too. The comparator's other 2 of 4 are out of our pre-registered scope: O'Neil-2018 is a phase-2 DAILY dose-ranging trial with a liraglutide arm, and Rubino/STEP-4 is a weight-loss-MAINTENANCE (randomised-withdrawal) estimand we exclude. We also RETRIEVED two regional 2.4 mg-vs-placebo trials (STEP-12 China, Korean STEP) but DECLARED THEM ABSENT for TIMEPOINT MISMATCH (Week 44 end-of-treatment, not the pre-registered Week 68) — a timepoint-consistency guard refusing to pad k by mixing follow-up durations. Pooled MD -11.84% (-25.13, 1.44), tau2=1.86; the wide CI is the honest k=2 HKSJ interval (t on 1 df), not a lowered bar. esketamine-trd-madrs 1 4 OVERLAPPING overlapping -- neither trial set contains the other Comparator (Front Psychiatry 2026, PMID 42490943) acute MADRS-change-from-baseline Day-28 primary pooled 4 RCTs (N=937, MD -2.99 [-5.10,-0.88]; verified in its own results table '937 (4 RCTs)'). The current review primary pool contains 4 effect objects, so parity.our_k is 4. Same-scope membership is represented by the parity_relation and outcome-membership objects; this row does not assert a separate gap-trial count. melatonin-primary-insomnia-sol 1 15 OVERLAPPING INFERRED overlapping -- neither trial set contains the other Comparator (PLoS One 2013, PMID 23691095) sleep-onset-latency pool = 15 RCTs (verified from its heterogeneity df: Q=31.9, df=14 => k=15; WMD 7.06 min [4.37,9.75]). We pool 1 (prolonged-release melatonin 2 mg, Wade 2011 / Circadin / NCT00397189, adult primary insomnia, per-arm mean/SD from CT.gov). The comparator's pool is deliberately BROADER in scope: of its 19 included studies, 4 are delayed-sleep-phase syndrome, 1 is REM sleep behaviour disorder, and >=3 are in CHILDREN (van Geijlswijk 2010, Smits 2003, Smits 2001) - all outside our adult-primary-insomnia scope - plus multiple cross-over designs and immediate-release doses from 0.05 mg/kg to 5 mg (a different formulation/estimand than our prolonged-release pool). The exact 15 SOL forest-plot trial identities are NOT in the comparator's cached OA full text (Figure 1 row labels absent), so the remaining per-trial split cannot be completed from source; several are pre-2000 cross-over trials with no accessible per-arm data. So this is a SCOPE (formulation/population/estimand) + partial REACH gap, honestly bounded - not a like-for-like shortfall. This is one of our narrowest pools and is shown as such.
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 9 of 232 — docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `a8c15240f7c8c9c5182fb8e2bf7b366993a05486c249d79a3ced0e7cefc2985e`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. an in-scope trial was NEVER retrieved (absent from every identifier space): FISSH — invisible to screening/PRISMA/declared-absent; the search is demonstrably incomplete screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT02444988, NCT02345486, PMID:26444692, PMID:27604335, NCT01270854; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `4bf769660bb570f55ac99b04603ab9f79e6e24da506f8338b505de2c6a375ed4`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. an in-scope trial was NEVER retrieved (absent from every identifier space): FISSH — invisible to screening/PRISMA/declared-absent; the search is demonstrably incomplete screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT02721654, NCT02875873, NCT02444988, NCT02345486, PMID:26444692, PMID:27604335, and 1 more; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 10 of 232 — docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html — ENGINE_CANNOT_CONSUME design variance</summary>

Source ref: `38c04411`; lost SHA-256: `97bc5e82f2d4a35b3efa52e3a0a58092a2545c71f1ae1e8f33b4510d38ea8961`.

Lost full text:

```text
ENGINE_CANNOT_CONSUME design variance. Pool changed because a design refusal was added: reconstructed cluster, crossover, cluster-crossover, and stepped-wedge trials require a held design-adjusted effect or an ICC design-effect variance before this engine can consume them. Refused trial(s): SMART (CLUSTER_CROSSOVER); SALT (CLUSTER_CROSSOVER); SPLIT (CLUSTER_CROSSOVER). SMART: ENGINE_CANNOT_CONSUME missing design_adjusted_effect|ICC; SALT: ENGINE_CANNOT_CONSUME missing design_adjusted_effect|ICC; SPLIT: ENGINE_CANNOT_CONSUME missing design_adjusted_effect|ICC. The evidence is not absent; this engine cannot consume the row without a held design-adjusted effect or ICC design-effect variance.
```

No same-heading new candidate on this page.

Draft-selected replacement heading `DECLARED ABSENT`; SHA-256 `004b373d6745c3bceae9513a9cf6a310bcc0136ae4b973c898d1a7355e062a4b`:

```text
DECLARED ABSENT. DESIGN REFUSAL: after refusing reconstructed non-parallel designs without an explicit design adjustment, only k=0 trial(s) remain; no pooled number is rendered. Remaining and refused trials are named below.
```

</details>

<details><summary>Pair 11 of 232 — docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html — Registered pooled CI REFUSED at k=2</summary>

Source ref: `38c04411`; lost SHA-256: `abe7679264593e3bc2f7f1daf7ccfdf7133247cf2c37fcc83a6f4fbb9461b1d4`.

Lost full text:

```text
Registered pooled CI REFUSED at k=2. Registered PM/HKSJ uses t(1)=12.71 at k=2; the interval is not served as a pooled confidence interval because a single degree of freedom is not reliable here. The point estimate may be displayed, but no pooled significance/null-crossing claim is emitted.
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `b7d80d3c3a9f1e74c038f21e17b05a35b999b7dff1d3a0ee377dbfa9df0c9f20`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 35041780 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 34375394 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 12 of 232 — docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html — Unit-of-analysis/design caveat</summary>

Source ref: `38c04411`; lost SHA-256: `187218cede8a19de486ebe8f5ccbfbc4eb94a54238aae46662ee26a3cfd57155`.

Lost full text:

```text
Unit-of-analysis/design caveat (disclosed, not silently adjusted). 1 pooled trial(s) are individual-randomized factorial designs: PMID 34375394 (factorial). These are disclosed as marginal factorial contrasts; when a source-reported adjusted marginal estimate with acceptable interaction evidence is available, the design key records that estimator and labels it rather than using a raw reconstruction silently. This is a stated limitation and design-key disclosure, not silent simple-parallel pooling.
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `b7d80d3c3a9f1e74c038f21e17b05a35b999b7dff1d3a0ee377dbfa9df0c9f20`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 35041780 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 34375394 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 13 of 232 — docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html — UNRENDERABLE stale contrast block</summary>

Source ref: `38c04411`; lost SHA-256: `661d399a6ca76fd4160d97319b5fbd2dfe5ad52f2a5a2411b83c0fa6799535a9`.

Lost full text:

```text
UNRENDERABLE stale contrast block. cached arm-contrast membership named trials not in the current consumed pool; current pooled trial ids: 34375394, 35041780; suppressed stale ids: 26444692.
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 14 of 232 — docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html — Parser-confirmed contrast disclosure</summary>

Source ref: `38c04411`; lost SHA-256: `4697904d3b3ed4aeee81f9af43fe744c712552c6a4717d3fda374a2ba651e972`.

Lost full text:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 2 of 2 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 34375394 parser-confirmed contrast fast infusion speed; plasma-lyte; saline 0.9%; slow infusion speed 35041780 parser-confirmed contrast 0.9% sodium chloride; plasma-lyte 148®
```

Candidate 1 of 1; SHA-256 `4f721c7c3be6ffd9b512b01e8b289dce69b5e67e70690b26839285728f598ece`:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 2 of 3 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 34375394 parser-confirmed contrast fast infusion speed; plasma-lyte; saline 0.9%; slow infusion speed 35041780 parser-confirmed contrast 0.9% sodium chloride; plasma-lyte 148® 26444692 unverified_no_registry_match —
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 15 of 232 — docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `8d0d9076b592d9eb3389f6f3368d61f221a077670af1bf5acff7b165986e5b7f`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 0 of 1 known (6 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 35041780 public/non-profit — abstract abstract : (Funded by the National Health and Medical Research Council of Australia and the Health Research Council of New Zealand; PLUS ClinicalTrials.gov number, NCT02721654.). PMID 34375394 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 23732264 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 26444692 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 27604335 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 27749094 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 29485925 not stated (full text scanned) — full text full text :
```

Candidate 1 of 1; SHA-256 `1ada2cddb254aaf2618ded168c8fbce306cb6f33e4246688c404ccc15afc64b1`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 0 of 1 known (6 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 35041780 public/non-profit — abstract abstract : (Funded by the National Health and Medical Research Council of Australia and the Health Research Council of New Zealand; PLUS ClinicalTrials.gov number, NCT02721654.). PMID 23732264 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 26444692 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 27604335 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 27749094 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 29485925 not stated (full text scanned) — full text full text : PMID 34375394 not stated (abstract only - full text not retrieved) — abstract abstract :
```

</details>

<details><summary>Pair 16 of 232 — docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `26fc49f9685a5367bf10f03f5eb60d58d686febbe7d328013c48420be6ac1015`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=2 of 2)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `b7d80d3c3a9f1e74c038f21e17b05a35b999b7dff1d3a0ee377dbfa9df0c9f20`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 35041780 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 34375394 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 17 of 232 — docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `5f6ddfb37c13dc62349e029c2daa1bd0ef654395adb3e4e7223154b25c74928f`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision NOT_ASSESSABLE (NOT ASSESSED) 95% CI [None, None]; missing/insufficient: valid confidence interval; served pooled CI (refused); clinical threshold / MID with basis; information-size assessment with adequacy and basis | counted as ONE conservative downgrade pending human judgement (a check that could not run cannot raise certainty) Design-aware availability: k=2 of 5 eligible-with-outcome trial(s) were consumable; 3 trial(s) were evidence refused for want of a variance model (ENGINE_CANNOT_CONSUME, missing=design_adjusted_effect|ICC), distinct from evidence absent. Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (5 of ~16 completed unpublished, 31%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `b7d80d3c3a9f1e74c038f21e17b05a35b999b7dff1d3a0ee377dbfa9df0c9f20`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 35041780 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 34375394 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 18 of 232 — docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `c8f3185f15c1e19bf4bfa066b0334e6bea58d87578c7685affd49527119b4663`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: an in-scope trial was NEVER retrieved (absent from every identifier space): FISSH — invisible to screening/PRISMA/declared-absent; the search is demonstrably incomplete screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: 27604335, 23732264, CRUSADERS · NCT07189091; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `4bf769660bb570f55ac99b04603ab9f79e6e24da506f8338b505de2c6a375ed4`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. an in-scope trial was NEVER retrieved (absent from every identifier space): FISSH — invisible to screening/PRISMA/declared-absent; the search is demonstrably incomplete screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT02721654, NCT02875873, NCT02444988, NCT02345486, PMID:26444692, PMID:27604335, and 1 more; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 19 of 232 — docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html — Unit-of-analysis caveat</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `e53e6594078369028e17c6908139e0434ec8ba527517a2b168a075e275af46a9`.

Lost full text:

```text
Unit-of-analysis caveat (disclosed, not adjusted). 3 pooled trial(s) use a cluster-randomized or cluster-period (policy) crossover design: PMID 29485925 (cluster-randomized crossover); PMID 27749094 (cluster-randomized crossover); PMID 26444692 (cluster-randomized crossover). They are pooled from patient-level counts without applying a design effect (cluster ICC / cluster-period correlation), because that variance component is not reported in the source — these are CLUSTER-PERIOD policy crossovers, not within-person crossovers. Consequence: the true variance of these trials is larger than the patient-level calculation assumes, so their inverse-variance weight in the pool is OVERSTATED and the pooled confidence interval is too narrow (over-precise). The pooled point estimate is NOT invariant to this : inflating only these trials' variances re-pools (illustrative DL) from 0.9592 to 0.9738 (×1.25→0.9617; ×2→0.9662; ×4→0.9707; ×10→0.9738) — because changing a study's variance changes its inverse-variance weight, so both the estimate and its interval move. This is a stated limitation (a documented meta-analysis error class the harness flags but cannot correct without the missing variance component), not a silent simple-parallel pooling.
```

No same-heading new candidate on this page.

Draft-selected replacement heading `DECLARED ABSENT`; SHA-256 `004b373d6745c3bceae9513a9cf6a310bcc0136ae4b973c898d1a7355e062a4b`:

```text
DECLARED ABSENT. DESIGN REFUSAL: after refusing reconstructed non-parallel designs without an explicit design adjustment, only k=0 trial(s) remain; no pooled number is rendered. Remaining and refused trials are named below.
```

</details>

<details><summary>Pair 20 of 232 — docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html — Randomised-contrast disclosure</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `52cd04e3a915bdf5778422eb031e9852886b3c694807455f9b05173937be4eb6`.

Lost full text:

```text
Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 2 of 5 pooled trials have a registry-confirmed contrast (the intervention of interest differs across arms). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 27749094 contrast unverified (registry class label / dev code) 0.9% sodium chloride; physiologically balanced fluid 29485925 contrast unverified (registry class label / dev code) 0.9% saline; physiologically-balanced isotonic crystalloid 34375394 randomised contrast verified fast infusion speed; plasma-lyte; saline 0.9%; slow infusion speed 35041780 randomised contrast verified 0.9% sodium chloride; plasma-lyte 148® 26444692 unverified_no_registry_match —
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 21 of 232 — docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `3056ab225b9e210a00936fdcbfa361f8e934c4a3eae8501e77e4dce9dedb702c`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 0 of 1 known (4 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 3 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 35041780 public/non-profit abstract only with saline. (Funded by the National Health and Medical Research Council of Australia and the Health Research Council of New Zealand; PLUS ClinicalTrials.gov number, NCT02721654.). PMID 29485925 declared (source unclassified) abstract only se of saline. (Funded by the Vanderbilt Institute for Clinical and Translational Research and others; SMART-MED and SMART-SURG ClinicalTrials.gov numbers, NCT02444988 and NCT02547779 .). PMID 34375394 not stated (abstract only — full text not retrieved) abstract only PMID 27749094 not stated (abstract only — full text not retrieved) abstract only PMID 26444692 not stated (abstract only — full text not retrieved) abstract only
```

Candidate 1 of 1; SHA-256 `1ada2cddb254aaf2618ded168c8fbce306cb6f33e4246688c404ccc15afc64b1`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 0 of 1 known (6 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 35041780 public/non-profit — abstract abstract : (Funded by the National Health and Medical Research Council of Australia and the Health Research Council of New Zealand; PLUS ClinicalTrials.gov number, NCT02721654.). PMID 23732264 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 26444692 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 27604335 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 27749094 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 29485925 not stated (full text scanned) — full text full text : PMID 34375394 not stated (abstract only - full text not retrieved) — abstract abstract :
```

</details>

<details><summary>Pair 22 of 232 — docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `b8c4b60bd942a25aaaafc43a4cc63dc78c3e705961e0fbf0a49155bf75bfe08b`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 5 of 5 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=5, RR 0.9592 [0.8995, 1.0229] Low risk of bias only k=4, RR 0.9711 [0.8917, 1.0576]
```

Candidate 1 of 1; SHA-256 `f7f6eb8ef26dd186392711f9e4a855ef2943d9b059b983abfcf39544728ced99`:

```text
Does the result survive dropping the trials that are not low risk of bias? Not computed (PRIMARY_ABSENT): the primary outcome has no pooled result (present = False). The per-trial rows and their risk-of-bias ratings are shown above; the omission is recorded in the review object as rob_sensitivity_omitted , not left silent.
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `b7d80d3c3a9f1e74c038f21e17b05a35b999b7dff1d3a0ee377dbfa9df0c9f20`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 35041780 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 34375394 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 23 of 232 — docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `960be40ef77ff4a78df7696b5504db234eb1f8d843aa2fd6152fed50e4fd2b0d`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capped below high because D3 (missing outcome data), a required risk-of-bias domain, is NOT ASSESSED for any pooled trial (no outcome-missingness source) — high certainty cannot be certified on a structurally-incomplete bias assessment. PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 5 assessed trial(s) at high risk; fewer than half at 'some concerns' Inconsistency not downgraded tau^2=0.0 (no between-study heterogeneity detected) Imprecision not downgraded 95% CI [0.8995, 1.0229]; crosses the null but excludes an appreciable effect on BOTH sides (within 0.75-1.25) -> precise about the absence of an appreciable effect Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED registry census (5 of ~16 completed unpublished, 31%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `b7d80d3c3a9f1e74c038f21e17b05a35b999b7dff1d3a0ee377dbfa9df0c9f20`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 35041780 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 34375394 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 24 of 232 — docs/reviews/colchicine-postop-af/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `103b10e9909f12fd780dad4a6e1318afaf016827bb3286d0ca7bc62f309516e4`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (HAND_WRITTEN_KEYWORD_SEARCH): We retract any claim of a registry-first or systematic search for this topic. a trial identified as eligible under the registered PICO is not pooled (five audit-named trials) — the pooled result and completeness claim cannot be current screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT04224545, NCT07611019, NCT07287345; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `b61a216013edf75930df6316f82592d7593167da4fc5b34aafc21af8abbe933a`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (HAND_WRITTEN_KEYWORD_SEARCH): We retract any claim of a registry-first or systematic search for this topic. five audit-named trials: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed a trial identified as eligible under the registered PICO is not pooled (five audit-named trials) — the pooled result and completeness claim cannot be current screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:42132185, NCT04224545, NCT07611019, NCT07287345; the completeness claim cannot be current
```

</details>

<details><summary>Pair 25 of 232 — docs/reviews/colchicine-postop-af/index.html — UNRENDERABLE stale contrast block</summary>

Source ref: `38c04411`; lost SHA-256: `f01680fc3f2356d3cb722c312de31a0983c6d7cc7407ddab70e63207bf4a1b37`.

Lost full text:

```text
UNRENDERABLE stale contrast block. cached arm-contrast membership named trials not in the current consumed pool; current pooled trial ids: 25172965, 32720823, 42132185; suppressed stale ids: 27502857.
```

Candidate 1 of 1; SHA-256 `9f28b6dfe7479f693dd889585b9bd88ff0e4ffd8b357201848a31122a90dc29f`:

```text
UNRENDERABLE stale contrast block. cached arm-contrast membership named trials not in the current consumed pool; current pooled trial ids: 25172965, 32720823; suppressed stale ids: 27502857, 42132185.
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 26 of 232 — docs/reviews/colchicine-postop-af/index.html — Parser-confirmed contrast disclosure</summary>

Source ref: `38c04411`; lost SHA-256: `8fd46365e43c66e147f322bf6b9b663bcd71a03ecc57a9b51d4e6ab1ae5bc119`.

Lost full text:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 2 of 3 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 25172965 parser-confirmed contrast colchicine 32720823 parser-confirmed contrast colchicine 42132185 unverified_no_registry_match —
```

Candidate 1 of 1; SHA-256 `d33845f56a472528ae4a1f5013b17879a5e41ceba032b0987cc62335c2080bca`:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 2 of 2 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 25172965 parser-confirmed contrast colchicine 32720823 parser-confirmed contrast colchicine
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 27 of 232 — docs/reviews/colchicine-postop-af/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `a1b4b98244aa735bedf4761b4bce9ba076f4d393ee8214404b07126a112d3f95`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 0 of 0 known (6 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 42132185 not stated (full text scanned) — full text full text : PMID 32720823 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 25172965 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 36286314 not stated (abstract only - full text not retrieved) — abstract abstract : NCT07287345 source not retrieved — : NCT07611019 source not retrieved — :
```

Candidate 1 of 1; SHA-256 `931af987b25aaae7de61a693658dafe22c379fef2aebf99a6700023cce96cb3c`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 0 of 0 known (6 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 32720823 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 25172965 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 36286314 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 42132185 not stated (full text scanned) — full text full text : NCT07287345 source not retrieved — : NCT07611019 source not retrieved — :
```

</details>

<details><summary>Pair 28 of 232 — docs/reviews/colchicine-postop-af/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `1e2c5ba31fccc110a76db81a398149dc4a7581cd90b8388d9eae24f224259ba5`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=3 of 3)
```

Candidate 1 of 1; SHA-256 `26fc49f9685a5367bf10f03f5eb60d58d686febbe7d328013c48420be6ac1015`:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=2 of 2)
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `834cdc3eca491b643e55dc5ab7f3f95a6f94649dd95e771e0068b576272b29bd`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 2: admissible 0; migration state (unbound_legacy, pooled and counted separately) 2 [PMID 25172965, PMID 32720823]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 42132185 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 29 of 232 — docs/reviews/colchicine-postop-af/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `54622f6c6299e6cb20daf2d52c910ec332a36009ba0fb43c59bf9aeeefdf575c`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision ASSESSED: −1 95% CI [0.2063, 2.0538]; GRADE default appreciable-effect thresholds 0.75/1.25; no topic threshold registered; spans clinical decisions or inadequate information -> imprecise; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (1 of ~14 completed unpublished, 7%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

Candidate 1 of 1; SHA-256 `cd5d06e56e97504b0bbe823cb4596e252251f4a79475c13021979ed25e613376`:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision NOT_ASSESSABLE (NOT ASSESSED) 95% CI [None, None]; missing/insufficient: valid confidence interval; served pooled CI (refused); clinical threshold / MID with basis; information-size assessment with adequacy and basis | counted as ONE conservative downgrade pending human judgement (a check that could not run cannot raise certainty) Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (1 of ~14 completed unpublished, 7%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `834cdc3eca491b643e55dc5ab7f3f95a6f94649dd95e771e0068b576272b29bd`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 2: admissible 0; migration state (unbound_legacy, pooled and counted separately) 2 [PMID 25172965, PMID 32720823]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 42132185 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 30 of 232 — docs/reviews/colchicine-postop-af/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `f41f44dbb235d7e3ba6cd19e39d95764a53c743f412bd2c8d97e717b24be0d8d`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: a trial identified as eligible under the registered PICO is not pooled (five audit-named trials) — the pooled result and completeness claim cannot be current screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: 36286314, 22090167, NCT07611019, NCT07287345; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `b61a216013edf75930df6316f82592d7593167da4fc5b34aafc21af8abbe933a`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (HAND_WRITTEN_KEYWORD_SEARCH): We retract any claim of a registry-first or systematic search for this topic. five audit-named trials: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed a trial identified as eligible under the registered PICO is not pooled (five audit-named trials) — the pooled result and completeness claim cannot be current screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:42132185, NCT04224545, NCT07611019, NCT07287345; the completeness claim cannot be current
```

</details>

<details><summary>Pair 31 of 232 — docs/reviews/colchicine-postop-af/index.html — DECLARED ABSENT</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `c37a2ca56df8e47967377077be78ba1eb29ac6e9bb6d885d60e2ccb5bf4f13a2`.

Lost full text:

```text
DECLARED ABSENT. REPORTED but not extractable as a pooled value: 32720823, 25172965, 27502857 mention this outcome in the committed abstract, but without arm counts or an effect+CI in an extractable form (e.g. a bare percentage with no denominator). This outcome is NOT absent — it is reported-but-not-poolable from the committed source; full-text acquisition would recover the countable form.
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 32 of 232 — docs/reviews/colchicine-postop-af/index.html — Randomised-contrast disclosure</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `9b1884cdd73a6a0f9056e82edd34706a8f1982b178287effdf441da7649bbf9e`.

Lost full text:

```text
Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 2 of 4 pooled trials have a registry-confirmed contrast (the intervention of interest differs across arms). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 25172965 randomised contrast verified colchicine 32720823 randomised contrast verified colchicine 27502857 unverified_no_registry_match — 42132185 unverified_no_registry_match —
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 33 of 232 — docs/reviews/colchicine-postop-af/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `c6f55d3c41f28551439f475dcc2443401b255683274ce3f5a9decaf1af143876`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 0 of 0 known (4 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 4 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 42132185 not stated (abstract only — full text not retrieved) abstract only PMID 32720823 not stated (abstract only — full text not retrieved) abstract only PMID 25172965 not stated (abstract only — full text not retrieved) abstract only PMID 27502857 not stated (abstract only — full text not retrieved) abstract only
```

Candidate 1 of 1; SHA-256 `931af987b25aaae7de61a693658dafe22c379fef2aebf99a6700023cce96cb3c`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 0 of 0 known (6 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 32720823 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 25172965 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 36286314 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 42132185 not stated (full text scanned) — full text full text : NCT07287345 source not retrieved — : NCT07611019 source not retrieved — :
```

</details>

<details><summary>Pair 34 of 232 — docs/reviews/colchicine-postop-af/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `c3dab676c7cc4c4ed7c1430bc1f86f0463968a9ec0d1c2af796b6433c250b494`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 4 of 4 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=4, RR 0.6735 [0.376, 1.2067] Low risk of bias only k=4, RR 0.6735 [0.376, 1.2067] (fewer trials than the full pool — see coverage)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `834cdc3eca491b643e55dc5ab7f3f95a6f94649dd95e771e0068b576272b29bd`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 2: admissible 0; migration state (unbound_legacy, pooled and counted separately) 2 [PMID 25172965, PMID 32720823]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 42132185 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 35 of 232 — docs/reviews/colchicine-postop-af/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `8dfc2f4ddd13b517cfa67ebda9a6a3790c8a1fea50c7298b85e933bf628f1531`.

Lost full text:

```text
Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 4 assessed trial(s) at high risk; fewer than half at 'some concerns' Inconsistency −1 tau^2=0.07415; prediction interval [0.237, 1.9142] is >=2x the CI width -> real heterogeneity Imprecision −1 95% CI [0.376, 1.2067]; crosses the null AND is compatible with an appreciable benefit (<=0.75) -> imprecise (the estimate is consistent with both no effect and an appreciable effect) Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED registry census (1 of ~14 completed unpublished, 7%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `834cdc3eca491b643e55dc5ab7f3f95a6f94649dd95e771e0068b576272b29bd`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 2: admissible 0; migration state (unbound_legacy, pooled and counted separately) 2 [PMID 25172965, PMID 32720823]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 42132185 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 36 of 232 — docs/reviews/colchicine-secondary-cv-prevention/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `eca2d8df92fdab1fee19af1152d34ccdd07809c2cec8e9e01241496130486a0d`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT06342609, PMID:41605493, PMID:40263680, PMID:39189611, NCT04848857, PMID:39115262, and 15 more; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `6fd88a2736356ea5fb23d4e6e3050993f297f90ad91e673e2c08da1da961e502`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT06342609, PMID:41605493, PMID:40263680, PMID:39189611, NCT04848857, PMID:39115262, and 17 more; the completeness claim cannot be current
```

</details>

<details><summary>Pair 37 of 232 — docs/reviews/colchicine-secondary-cv-prevention/index.html — UNRENDERABLE stale contrast block</summary>

Source ref: `38c04411`; lost SHA-256: `63429f9bc38a1f11e585fb714326f6aa7f29d5f13a7dd5305b666cf7792cc608`.

Lost full text:

```text
UNRENDERABLE stale contrast block. cached arm-contrast membership named trials not in the current consumed pool; current pooled trial ids: 31733140, 32865380, 39555823; suppressed stale ids: 34876021.
```

Candidate 1 of 1; SHA-256 `28a9560a976721c635e36fd3bd1e2df125d7eac8db9e809dfc2b665ac86c032a`:

```text
UNRENDERABLE stale contrast block. cached arm-contrast membership named trials not in the current consumed pool; current pooled trial ids: 31733140, 39555823; suppressed stale ids: 32865380, 34876021.
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 38 of 232 — docs/reviews/colchicine-secondary-cv-prevention/index.html — Parser-confirmed contrast disclosure</summary>

Source ref: `38c04411`; lost SHA-256: `0e555e840fa3e686f38290f3b4947deea1fe3a2b620d293b493bef1d33008077`.

Lost full text:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 2 of 3 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 31733140 parser-confirmed contrast colchicine 39555823 parser-confirmed contrast colchicine; spironolactone 32865380 unverified_no_registry_match —
```

Candidate 1 of 1; SHA-256 `8a69af5016c23f681a26f607ede2cc642095c52abbf173813f6ccbc506b5d2d2`:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 2 of 2 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 31733140 parser-confirmed contrast colchicine 39555823 parser-confirmed contrast colchicine; spironolactone
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 39 of 232 — docs/reviews/colchicine-secondary-cv-prevention/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `ec00ff20ec701450965f24d34122641c9bcd5ed4cdd3a35f0d51476d2c1d2571`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 0 of 3 known (22 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 31733140 public/non-profit — abstract abstract : (Funded by the Government of Quebec and others; COLCOT ClinicalTrials.gov number, NCT02551094.). PMID 32865380 public/non-profit — abstract abstract : (Funded by the National Health Medical Research Council of Australia and others; LoDoCo2 Australian New Zealand Clinical Trials Registry number, ACTRN12614000093684.). PMID 39555823 public/non-profit — abstract abstract : (Funded by the Canadian Institutes of Health Research and others; CLEAR ClinicalTrials.gov number, NCT03048825.). PMID 34876021 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 1593057 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 23500260 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 26265659 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 31284074 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 32295417 not stated (full text scanned) — full text full text : PMID 32862667 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 34420373 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 39115262 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 39166327 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 39189611 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 40263680 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 41605493 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 41670023 not stated (abstract only - full text not retrieved) — abstract abstract : NCT00754819 source not retrieved — : NCT01709981 not stated (full text scanned) — linked full text PMID 32295417 linked full text PMID 32295417 : NCT02095522 source not retrieved — : NCT05739929 source not retrieved — : NCT05850091 source not retrieved — : NCT06215989 source not retrieved — : NCT07143136 source not retrieved — : NCT07704164 source not retrieved — :
```

Candidate 1 of 1; SHA-256 `f97690397e04594193d720c2a3e91cf22006e361498c9b4120d915bc6b7bcdba`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 0 of 3 known (22 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 31733140 public/non-profit — abstract abstract : (Funded by the Government of Quebec and others; COLCOT ClinicalTrials.gov number, NCT02551094.). PMID 39555823 public/non-profit — abstract abstract : (Funded by the Canadian Institutes of Health Research and others; CLEAR ClinicalTrials.gov number, NCT03048825.). PMID 32865380 public/non-profit — abstract abstract : (Funded by the National Health Medical Research Council of Australia and others; LoDoCo2 Australian New Zealand Clinical Trials Registry number, ACTRN12614000093684.). PMID 1593057 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 23500260 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 26265659 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 31284074 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 32295417 not stated (full text scanned) — full text full text : PMID 32862667 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 34420373 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 34876021 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 39115262 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 39166327 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 39189611 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 40263680 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 41605493 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 41670023 not stated (abstract only - full text not retrieved) — abstract abstract : NCT00754819 source not retrieved — : NCT01709981 not stated (full text scanned) — linked full text PMID 32295417 linked full text PMID 32295417 : NCT02095522 source not retrieved — : NCT05739929 source not retrieved — : NCT05850091 source not retrieved — : NCT06215989 source not retrieved — : NCT07143136 source not retrieved — : NCT07704164 source not retrieved — :
```

</details>

<details><summary>Pair 40 of 232 — docs/reviews/colchicine-secondary-cv-prevention/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `1e2c5ba31fccc110a76db81a398149dc4a7581cd90b8388d9eae24f224259ba5`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=3 of 3)
```

Candidate 1 of 1; SHA-256 `26fc49f9685a5367bf10f03f5eb60d58d686febbe7d328013c48420be6ac1015`:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=2 of 2)
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `466f1db7b57a03d6c2b50145512dc487964d09b9b002316c57869cd393301863`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 2: admissible 0; migration state (unbound_legacy, pooled and counted separately) 2 [PMID 31733140, PMID 39555823]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 32865380 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 41 of 232 — docs/reviews/colchicine-secondary-cv-prevention/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `37d15fe8574f02c0b2dd65386eb49cea20a52533fca128fb9f8ff51049162376`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (22 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision ASSESSED: −1 95% CI [0.5074, 1.3039]; GRADE default appreciable-effect thresholds 0.75/1.25; no topic threshold registered; spans clinical decisions or inadequate information -> imprecise; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (6 of ~33 completed unpublished, 18%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

Candidate 1 of 1; SHA-256 `7c27e37f174c6190659db2dff87cf7360500b837a6af97653e1865ab98076348`:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (23 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. | counted as ONE conservative downgrade pending human judgement (a check that could not run cannot raise certainty) Imprecision NOT_ASSESSABLE (NOT ASSESSED) 95% CI [None, None]; missing/insufficient: valid confidence interval; served pooled CI (refused); clinical threshold / MID with basis; information-size assessment with adequacy and basis | counted as ONE conservative downgrade pending human judgement (a check that could not run cannot raise certainty) Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (6 of ~33 completed unpublished, 18%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `466f1db7b57a03d6c2b50145512dc487964d09b9b002316c57869cd393301863`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 2: admissible 0; migration state (unbound_legacy, pooled and counted separately) 2 [PMID 31733140, PMID 39555823]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 32865380 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 42 of 232 — docs/reviews/colchicine-secondary-cv-prevention/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `006dfed6a52c884adfa0d494c058b30a9f00e399b9ccbdfaea15ce594896f7b6`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: 32407460, 41670023, 41605493, 40263680, 39189611, 39166327, and 19 more; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `6fd88a2736356ea5fb23d4e6e3050993f297f90ad91e673e2c08da1da961e502`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT06342609, PMID:41605493, PMID:40263680, PMID:39189611, NCT04848857, PMID:39115262, and 17 more; the completeness claim cannot be current
```

</details>

<details><summary>Pair 43 of 232 — docs/reviews/colchicine-secondary-cv-prevention/index.html — Randomised-contrast disclosure</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `2f35820b0771882ce825e008c91720427f3067b3757140fa18acd821b341b27b`.

Lost full text:

```text
Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 2 of 4 pooled trials have a registry-confirmed contrast (the intervention of interest differs across arms). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 31733140 randomised contrast verified colchicine 39555823 randomised contrast verified colchicine; spironolactone 32865380 unverified_no_registry_match — 34876021 unverified_no_registry_match —
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 44 of 232 — docs/reviews/colchicine-secondary-cv-prevention/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `f640e854cfd1e10d0a39cfad5f14c70825f998fef6c8ee76251e10eeee8d2e7e`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 0 of 3 known (1 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 1 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 31733140 public/non-profit abstract only than placebo. (Funded by the Government of Quebec and others; COLCOT ClinicalTrials.gov number, NCT02551094.). PMID 32865380 public/non-profit abstract only ived placebo. (Funded by the National Health Medical Research Council of Australia and others; LoDoCo2 Australian New Zealand Clinical Trials Registry number, ACTRN12614000093684.). PMID 39555823 public/non-profit abstract only ularization). (Funded by the Canadian Institutes of Health Research and others; CLEAR ClinicalTrials.gov number, NCT03048825.). PMID 34876021 not stated (abstract only — full text not retrieved) abstract only
```

Candidate 1 of 1; SHA-256 `f97690397e04594193d720c2a3e91cf22006e361498c9b4120d915bc6b7bcdba`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 0 of 3 known (22 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 31733140 public/non-profit — abstract abstract : (Funded by the Government of Quebec and others; COLCOT ClinicalTrials.gov number, NCT02551094.). PMID 39555823 public/non-profit — abstract abstract : (Funded by the Canadian Institutes of Health Research and others; CLEAR ClinicalTrials.gov number, NCT03048825.). PMID 32865380 public/non-profit — abstract abstract : (Funded by the National Health Medical Research Council of Australia and others; LoDoCo2 Australian New Zealand Clinical Trials Registry number, ACTRN12614000093684.). PMID 1593057 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 23500260 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 26265659 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 31284074 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 32295417 not stated (full text scanned) — full text full text : PMID 32862667 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 34420373 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 34876021 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 39115262 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 39166327 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 39189611 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 40263680 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 41605493 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 41670023 not stated (abstract only - full text not retrieved) — abstract abstract : NCT00754819 source not retrieved — : NCT01709981 not stated (full text scanned) — linked full text PMID 32295417 linked full text PMID 32295417 : NCT02095522 source not retrieved — : NCT05739929 source not retrieved — : NCT05850091 source not retrieved — : NCT06215989 source not retrieved — : NCT07143136 source not retrieved — : NCT07704164 source not retrieved — :
```

</details>

<details><summary>Pair 45 of 232 — docs/reviews/colchicine-secondary-cv-prevention/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `57205a3c80284c1aeff24226ff5968fc5934014af55e2b4724303c7a4e83c3af`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 2 of 3 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=3, HR 0.8134 [0.5074, 1.3039] Low risk of bias only k=2, HR 0.7215 [0.2824, 1.8432]
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `466f1db7b57a03d6c2b50145512dc487964d09b9b002316c57869cd393301863`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 2: admissible 0; migration state (unbound_legacy, pooled and counted separately) 2 [PMID 31733140, PMID 39555823]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 32865380 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 46 of 232 — docs/reviews/colchicine-secondary-cv-prevention/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `a54ecd524eced807f0962ba546cc1fda3db13f551f886144467a6f2ea0d59259`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 2 assessed trial(s) at high risk; fewer than half at 'some concerns'; risk-of-bias signal available for only 2 of 3 pooled trials (registry-derived), so the rating is capped Inconsistency not downgraded tau^2=0.02669; prediction interval not markedly wider than the CI Imprecision −1 95% CI [0.5074, 1.3039]; crosses the null AND is compatible with an appreciable benefit (<=0.75) and an appreciable harm (>=1.25) -> imprecise (the estimate is consistent with both no effect and an appreciable effect) Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED registry census (6 of ~33 completed unpublished, 18%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `466f1db7b57a03d6c2b50145512dc487964d09b9b002316c57869cd393301863`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 2: admissible 0; migration state (unbound_legacy, pooled and counted separately) 2 [PMID 31733140, PMID 39555823]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 32865380 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 47 of 232 — docs/reviews/corticosteroids-cap-mortality/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `d3eb35fd563bb5f2d6c302e570c6be46f1fb111eaaba27fddf6711f0177dd144`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (HAND_WRITTEN_KEYWORD_SEARCH): We retract any claim of a registry-first or systematic search for this topic. a trial identified as eligible under the registered PICO is not pooled (SONIA, McHardy, El-Ghamrawy, Mikami, Sabry, Nafae, and others) — the pooled result and completeness claim cannot be current an in-scope trial was NEVER retrieved (absent from every identifier space): NCT02552342 — invisible to screening/PRISMA/declared-absent; the search is demonstrably incomplete screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:15557131, PMID:8339624, NCT01283009, PMID:21406101; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `07cbf9ad8e43faf6419b8af1e664ecaf726e8f3f5a656e9042eaa48f4678a61c`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (HAND_WRITTEN_KEYWORD_SEARCH): We retract any claim of a registry-first or systematic search for this topic. SONIA: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed McHardy: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed El-Ghamrawy: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed Mikami: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed Sabry: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed Nafae: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed Snijders: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed a trial identified as eligible under the registered PICO is not pooled (SONIA, McHardy, El-Ghamrawy, Mikami, Sabry, Nafae, and others) — the pooled result and completeness claim cannot be current an in-scope trial was NEVER retrieved (absent from every identifier space): NCT02552342 — invisible to screening/PRISMA/declared-absent; the search is demonstrably incomplete screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:15557131, PMID:8339624, NCT01283009, PMID:21406101, NCT00973154, NCT00471640; the completeness claim cannot be current
```

</details>

<details><summary>Pair 48 of 232 — docs/reviews/corticosteroids-cap-mortality/index.html — Pooled result SUPPRESSED</summary>

Source ref: `38c04411`; lost SHA-256: `24ab9b70d1a41c551e04aa46747a47a7bcabdd1dc6b248105a988132f5de5991`.

Lost full text:

```text
Pooled result SUPPRESSED (estimand-incompatible). pooled effect SUPPRESSED: the trials mix incompatible estimand classes (ODDS_RATIO + RISK_RATIO) — these effect measures are not one quantity without an explicit, source-backed conversion, so no pooled effect, CI, heterogeneity or sensitivity is valid. The per-trial estimates are shown; pool each coherent strand separately. Estimand classes: ODDS_RATIO + RISK_RATIO; k = 4 trials, shown individually below, not pooled. Refusal is reversible and auditable — reason code INCOMPATIBLE_ESTIMANDS ; had these classes been pooled anyway the (INVALID) result would have been 2.13 (0.8–5.64) — shown only so the refusal is inspectable, never as a usable number.
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `3292bdf00fd5c78a3b2e6c091dd71568c98b7cc7ddff412e8a8d03db19c20b27`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 2: admissible 1; migration state (unbound_legacy, pooled and counted separately) 1 [PMID 25688779]; bound by a producer route the bundle's P8 does not name 1 [PMID 33446608]. Set aside on P5 (family eligibility) 2: PMID 25608756 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 21636122 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 49 of 232 — docs/reviews/corticosteroids-cap-mortality/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `6b889d0c117224b24292278df7f01c6c16d572a3441418e9312b1d9cc6dcc84e`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 1 of 2 known (7 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 25608756 mixed — abstract abstract : FUNDING: Swiss National Science Foundation, Viollier AG, Nora van Meeuwen Haefliger Stiftung, Julia und Gottfried Bangerter-Rhyner Stiftung. PMID 36942789 public/non-profit — abstract abstract : (Funded by the French Ministry of Health; CAPE COD ClinicalTrials.gov number, NCT02517489.). PMID 25688779 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 33446608 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 21636122 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 15557131 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 21406101 not stated (full text scanned) — full text full text : PMID 35723686 not stated (full text scanned) — full text full text : PMID 8339624 not stated (abstract only - full text not retrieved) — abstract abstract :
```

Candidate 1 of 1; SHA-256 `fde773efe4ff25b90e144ef550cb53b46d2f6a7bc3b6e6e8de916a37cc8a6e5f`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 1 of 2 known (7 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 25608756 mixed — abstract abstract : FUNDING: Swiss National Science Foundation, Viollier AG, Nora van Meeuwen Haefliger Stiftung, Julia und Gottfried Bangerter-Rhyner Stiftung. PMID 36942789 public/non-profit — abstract abstract : (Funded by the French Ministry of Health; CAPE COD ClinicalTrials.gov number, NCT02517489.). PMID 25688779 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 33446608 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 15557131 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 21406101 not stated (full text scanned) — full text full text : PMID 21636122 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 35723686 not stated (full text scanned) — full text full text : PMID 8339624 not stated (abstract only - full text not retrieved) — abstract abstract :
```

</details>

<details><summary>Pair 50 of 232 — docs/reviews/corticosteroids-cap-mortality/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `e0d0e516ac70ae587b84f97518ad9bae02ad83ac0e75aeefcd835dba72632573`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: a trial identified as eligible under the registered PICO is not pooled (SONIA, McHardy, El-Ghamrawy, Mikami, Sabry, Nafae, and others) — the pooled result and completeness claim cannot be current an in-scope trial was NEVER retrieved (absent from every identifier space): NCT02552342 — invisible to screening/PRISMA/declared-absent; the search is demonstrably incomplete screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: 15557131, 8339624, 35723686, 21406101, 33446608, 21636122; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `07cbf9ad8e43faf6419b8af1e664ecaf726e8f3f5a656e9042eaa48f4678a61c`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (HAND_WRITTEN_KEYWORD_SEARCH): We retract any claim of a registry-first or systematic search for this topic. SONIA: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed McHardy: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed El-Ghamrawy: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed Mikami: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed Sabry: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed Nafae: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed Snijders: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed a trial identified as eligible under the registered PICO is not pooled (SONIA, McHardy, El-Ghamrawy, Mikami, Sabry, Nafae, and others) — the pooled result and completeness claim cannot be current an in-scope trial was NEVER retrieved (absent from every identifier space): NCT02552342 — invisible to screening/PRISMA/declared-absent; the search is demonstrably incomplete screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:15557131, PMID:8339624, NCT01283009, PMID:21406101, NCT00973154, NCT00471640; the completeness claim cannot be current
```

</details>

<details><summary>Pair 51 of 232 — docs/reviews/corticosteroids-cap-mortality/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `09ed6ae25a015e0d8fa49dc6bbc1d5eaec199132b9199b61233147e1ef2af751`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 1 of 2 known (1 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 1 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 25608756 mixed abstract only nd efficiency. FUNDING: Swiss National Science Foundation, Viollier AG, Nora van Meeuwen Haefliger Stiftung, Julia und Gottfried Bangerter-Rhyner Stiftung. PMID 36942789 public/non-profit abstract only ived placebo. (Funded by the French Ministry of Health; CAPE COD ClinicalTrials.gov number, NCT02517489.). PMID 25688779 not stated (abstract only — full text not retrieved) abstract only
```

Candidate 1 of 1; SHA-256 `fde773efe4ff25b90e144ef550cb53b46d2f6a7bc3b6e6e8de916a37cc8a6e5f`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 1 of 2 known (7 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 25608756 mixed — abstract abstract : FUNDING: Swiss National Science Foundation, Viollier AG, Nora van Meeuwen Haefliger Stiftung, Julia und Gottfried Bangerter-Rhyner Stiftung. PMID 36942789 public/non-profit — abstract abstract : (Funded by the French Ministry of Health; CAPE COD ClinicalTrials.gov number, NCT02517489.). PMID 25688779 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 33446608 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 15557131 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 21406101 not stated (full text scanned) — full text full text : PMID 21636122 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 35723686 not stated (full text scanned) — full text full text : PMID 8339624 not stated (abstract only - full text not retrieved) — abstract abstract :
```

</details>

<details><summary>Pair 52 of 232 — docs/reviews/corticosteroids-covid19-mortality/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `2e30fe5f4b8b4dd9d0273967eff78a79d2723dd98f1b200a92b8ebfa2c0af2a9`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT02517489, NCT04343729, NCT04327401, NCT04344730; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `98b8c99015a2a1379c743aa45553bd2d69c6380ed415878b444a76d1f7269307`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT04348305, NCT02517489, NCT04343729, NCT04327401, NCT04344730; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 53 of 232 — docs/reviews/corticosteroids-covid19-mortality/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `8c3de14a823576464f20d085f99e55a542b1f37f94d91fa590b2b97935fab246`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 0 of 1 known (6 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 32678530 public/non-profit — full text full text : (Funded by the Medical Research Council and National Institute for Health Research and others; RECOVERY ClinicalTrials.gov number, <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://clinicaltrials.gov/show/NCT04381936" ext-link-type="uri">NCT04381936</ext-link>; ISRCTN number, <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://www.isrctn.com/ISRCTN50189673" ext-link-type="uri" PMID 34138478 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 32785710 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 32876689 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 32876695 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 32876697 not stated (abstract only - full text not retrieved) — abstract abstract : NCT04344730 source not retrieved — :
```

Candidate 1 of 1; SHA-256 `bdb571653d820bd4d56c20c6a51dadd638d6897568927b6672dfa5a55dd7d670`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 0 of 1 known (6 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 32678530 public/non-profit — full text full text : (Funded by the Medical Research Council and National Institute for Health Research and others; RECOVERY ClinicalTrials.gov number, <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://clinicaltrials.gov/show/NCT04381936" ext-link-type="uri">NCT04381936</ext-link>; ISRCTN number, <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://www.isrctn.com/ISRCTN50189673" ext-link-type="uri" PMID 32785710 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 32876689 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 32876695 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 32876697 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 34138478 not stated (abstract only - full text not retrieved) — abstract abstract : NCT04344730 source not retrieved — :
```

</details>

<details><summary>Pair 54 of 232 — docs/reviews/corticosteroids-covid19-mortality/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `907e96459f0676ed291eafe578d7ed148d3184fa1b8274d074077cc53eadf371`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=1 of 1)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `53f80e2f2617036e6c2f2050a284ca6bba89a26c5dac466b704b8df7337eecc5`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 32678530 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 55 of 232 — docs/reviews/corticosteroids-covid19-mortality/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `32611d2da4679b380f9d196c9f0781be4159ecca7dfb300c55bfedf37b26cd6d`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.75, 0.93]; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (27 of ~69 completed unpublished, 39%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `53f80e2f2617036e6c2f2050a284ca6bba89a26c5dac466b704b8df7337eecc5`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 32678530 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 56 of 232 — docs/reviews/corticosteroids-covid19-mortality/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `f636a22b7a91901bf2f4ede7427461e8d0d33a486535b2fc21538f753ba2f624`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: 34138478, 32876697, 32876689, 32785710, 32876695, COVIDICUS · NCT04344730, and 1 more; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `98b8c99015a2a1379c743aa45553bd2d69c6380ed415878b444a76d1f7269307`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT04348305, NCT02517489, NCT04343729, NCT04327401, NCT04344730; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 57 of 232 — docs/reviews/corticosteroids-covid19-mortality/index.html — DECLARED ABSENT</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `45bb4635fe128500a1ea7b4425bebd42c1abc364f092a64f7256b064807fe3be`.

Lost full text:

```text
DECLARED ABSENT. REPORTED but not extractable as a pooled value: 34138478 mention this outcome in the committed abstract, but without arm counts or an effect+CI in an extractable form (e.g. a bare percentage with no denominator). This outcome is NOT absent — it is reported-but-not-poolable from the committed source; full-text acquisition would recover the countable form.
```

Candidate 1 of 1; SHA-256 `ce1c80c44d299dc726fb9d8c2fd18ae80a82ceeb589c9a085aa45bbf0a98e0ab`:

```text
DECLARED ABSENT. no admitted trial: 1 candidate extraction(s) reached the pool and were set aside on admission (family eligibility not established by held evidence, P5); each stays listed below with the value it carried; no pooled result until eligibility is established
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 58 of 232 — docs/reviews/corticosteroids-covid19-mortality/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `3f98507b0cda3348baedbf46363de3908b89e1c5d408b2a0f35ef63fb04ffa14`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 0 of 1 known (0 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 32678530 public/non-profit abstract only tory support. (Funded by the Medical Research Council and National Institute for Health Research and others; RECOVERY ClinicalTrials.gov number, NCT04381936; ISRCTN number, 50189673.).
```

Candidate 1 of 1; SHA-256 `bdb571653d820bd4d56c20c6a51dadd638d6897568927b6672dfa5a55dd7d670`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 0 of 1 known (6 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 32678530 public/non-profit — full text full text : (Funded by the Medical Research Council and National Institute for Health Research and others; RECOVERY ClinicalTrials.gov number, <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://clinicaltrials.gov/show/NCT04381936" ext-link-type="uri">NCT04381936</ext-link>; ISRCTN number, <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://www.isrctn.com/ISRCTN50189673" ext-link-type="uri" PMID 32785710 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 32876689 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 32876695 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 32876697 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 34138478 not stated (abstract only - full text not retrieved) — abstract abstract : NCT04344730 source not retrieved — :
```

</details>

<details><summary>Pair 59 of 232 — docs/reviews/corticosteroids-covid19-mortality/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `460814ddc2ea0b454e2cc59e9a1ddbc97261099c24c7c68b7000dd33fc92a91d`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 1 of 1 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=1, RR 0.83 [0.7454, 0.9242] Low risk of bias only NOT ESTIMABLE — no pooled trial qualifies as low risk of bias, so this stratum has no trials to re-pool (an empty subgroup is not agreement with the full pool)
```

Candidate 1 of 1; SHA-256 `f7f6eb8ef26dd186392711f9e4a855ef2943d9b059b983abfcf39544728ced99`:

```text
Does the result survive dropping the trials that are not low risk of bias? Not computed (PRIMARY_ABSENT): the primary outcome has no pooled result (present = False). The per-trial rows and their risk-of-bias ratings are shown above; the omission is recorded in the review object as rob_sensitivity_omitted , not left silent.
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `53f80e2f2617036e6c2f2050a284ca6bba89a26c5dac466b704b8df7337eecc5`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 32678530 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 60 of 232 — docs/reviews/corticosteroids-covid19-mortality/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `f11df83d8cdcdf214dcb3553d8907cc6b8122266f3c059c96f4b9c6d1c37ee9a`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias −1 1 of 1 assessed trial(s) at 'some concerns' Inconsistency NOT ASSESSED single trial (k=1): between-study inconsistency is not estimable Imprecision not downgraded 95% CI [0.75, 0.93]; excludes the null with a reasonably tight interval -> precise; single trial — imprecision judged from the CI, not downgraded merely for k=1 Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED registry census (27 of ~69 completed unpublished, 39%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `53f80e2f2617036e6c2f2050a284ca6bba89a26c5dac466b704b8df7337eecc5`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 32678530 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 61 of 232 — docs/reviews/dapagliflozin-hfpef-hosp/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `982d3945ccd514a2b05b5551d61f0932867a661a39ebad75a25954573ab33f01`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (PMID_ENUMERATION_explicit): protocol Search section explicitly says UID-anchored queries for the named trials — known-item retrieval, cannot discover an unknown eligible trial. the primary outcome is reported by trials that could not be pooled (36027570, 34711976, 37534453) — the pooled k is known-incomplete screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT03619213, NCT04730947, NCT04475042, NCT03877224; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `f3e496947f6ab131aaf2d0a4ab8066c772ae77b5fb4338e134921dc9887ab46e`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (PMID_ENUMERATION_explicit): protocol Search section explicitly says UID-anchored queries for the named trials — known-item retrieval, cannot discover an unknown eligible trial. the primary outcome is reported by trials that could not be pooled (36027570, 34711976, 37534453) — the pooled k is known-incomplete screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT03619213, NCT03030235, NCT04730947, NCT04475042, NCT03877224; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 62 of 232 — docs/reviews/dapagliflozin-hfpef-hosp/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `f32f15a5ec6cd8aa058dbe6c632ab0ff726861eb6362c4146a97f034592a7503`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (PMID_ENUMERATION_explicit): protocol Search section explicitly says UID-anchored queries for the named trials — known-item retrieval, cannot discover an unknown eligible trial. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: 34711976, 37534453, STADIA-HFpEF · NCT04475042, NCT03877224; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `f3e496947f6ab131aaf2d0a4ab8066c772ae77b5fb4338e134921dc9887ab46e`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (PMID_ENUMERATION_explicit): protocol Search section explicitly says UID-anchored queries for the named trials — known-item retrieval, cannot discover an unknown eligible trial. the primary outcome is reported by trials that could not be pooled (36027570, 34711976, 37534453) — the pooled k is known-incomplete screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT03619213, NCT03030235, NCT04730947, NCT04475042, NCT03877224; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 63 of 232 — docs/reviews/denosumab-vertebral-fracture/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `71e4002ec9f8906c097fbff9ca975a30fafe8656bd556978858a78671ec131b5`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic.
```

Candidate 1 of 1; SHA-256 `a21a2674946ebe28416802ba51075957334ee20525901458931383fd3c10c83b`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT00089791; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 64 of 232 — docs/reviews/denosumab-vertebral-fracture/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `907e96459f0676ed291eafe578d7ed148d3184fa1b8274d074077cc53eadf371`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=1 of 1)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `16fc82a53a7e92f2ec4ab29c61b5660049364c5332e46cf50855d9ad75f967c6`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 19671655 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 65 of 232 — docs/reviews/denosumab-vertebral-fracture/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `5ca74e404a5a8e97711f713c7a379de65aa789f7270149f1033f7f2a9d8d5333`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) single trial (k=1): between-study inconsistency is not estimable Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.26, 0.41]; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (11 of ~79 completed unpublished, 14%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `16fc82a53a7e92f2ec4ab29c61b5660049364c5332e46cf50855d9ad75f967c6`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 19671655 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 66 of 232 — docs/reviews/denosumab-vertebral-fracture/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `cdf08119611dfcdf4ec945d9bea4e527ef45935a09f48e359cb9a83311f74e12`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 1 of 1 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=1, RR 0.32 [0.2548, 0.4018] Low risk of bias only k=1, RR 0.32 [0.2548, 0.4018] (fewer trials than the full pool — see coverage)
```

Candidate 1 of 1; SHA-256 `f7f6eb8ef26dd186392711f9e4a855ef2943d9b059b983abfcf39544728ced99`:

```text
Does the result survive dropping the trials that are not low risk of bias? Not computed (PRIMARY_ABSENT): the primary outcome has no pooled result (present = False). The per-trial rows and their risk-of-bias ratings are shown above; the omission is recorded in the review object as rob_sensitivity_omitted , not left silent.
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `16fc82a53a7e92f2ec4ab29c61b5660049364c5332e46cf50855d9ad75f967c6`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 19671655 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 67 of 232 — docs/reviews/denosumab-vertebral-fracture/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `ecc8ed947c95752e72c0a6cab09514ec7c5a34cdfc2717544a6d9011a28156f3`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 1 assessed trial(s) at high risk; fewer than half at 'some concerns' Inconsistency NOT ASSESSED single trial (k=1): between-study inconsistency is not estimable Imprecision not downgraded 95% CI [0.26, 0.41]; excludes the null with a reasonably tight interval -> precise; single trial — imprecision judged from the CI, not downgraded merely for k=1 Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED registry census (11 of ~79 completed unpublished, 14%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `16fc82a53a7e92f2ec4ab29c61b5660049364c5332e46cf50855d9ad75f967c6`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 19671655 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 68 of 232 — docs/reviews/doac-vte-recurrence/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `8d85d2e447f203ca3ca2c7a3a53ec299b5111450ad16acdfcddb56859f8db26c`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (RAN_ERROR_rendered_as_run): Registry-first (AACT) = RAN_ERROR; the source_status table shows it, but the search narrative still presents the topic as registry-first. RAN_ERROR must never be rendered as a completed search (extends the audit-22 NOT_RUN gate limb to RAN_ERROR).
```

Candidate 1 of 1; SHA-256 `7ed9d2bbc2c86e8386d9d15940168f4c3134a919c4303b58afd82657e18a240c`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (RAN_ERROR_rendered_as_run): Registry-first (AACT) = RAN_ERROR; the source_status table shows it, but the search narrative still presents the topic as registry-first. RAN_ERROR must never be rendered as a completed search (extends the audit-22 NOT_RUN gate limb to RAN_ERROR). screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT00291330, NCT00439777, NCT00440193, NCT00986154, NCT00643201; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 69 of 232 — docs/reviews/doac-vte-recurrence/index.html — Registered pooled CI REFUSED at k=2</summary>

Source ref: `38c04411`; lost SHA-256: `abe7679264593e3bc2f7f1daf7ccfdf7133247cf2c37fcc83a6f4fbb9461b1d4`.

Lost full text:

```text
Registered pooled CI REFUSED at k=2. Registered PM/HKSJ uses t(1)=12.71 at k=2; the interval is not served as a pooled confidence interval because a single degree of freedom is not reliable here. The point estimate may be displayed, but no pooled significance/null-crossing claim is emitted.
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `1f41216297452e2c021925bef1712ed14a3519b66f053fb3260b95f3b8230743`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 24344086 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 19966341 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 70 of 232 — docs/reviews/doac-vte-recurrence/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `2d9515b0195849dee425159a732d07f5a1342d930e4b021c09cb83bc54371d79`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 4 of 4 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 22449293 industry — abstract abstract : (Funded by Bayer HealthCare and Janssen Pharmaceuticals; EINSTEIN-PE ClinicalTrials.gov number, NCT00439777.). PMID 21128814 industry — abstract abstract : (Funded by Bayer Schering Pharma and Ortho-McNeil; ClinicalTrials.gov numbers, NCT00440193 and NCT00439725.). PMID 23991658 industry — abstract abstract : (Funded by Daiichi-Sankyo; Hokusai-VTE ClinicalTrials.gov number, NCT00986154.). PMID 23808982 industry — abstract abstract : CONCLUSIONS: A fixed-dose regimen of apixaban alone was noninferior to conventional therapy for the treatment of acute venous thromboembolism and was associated with significantly less bleeding (Funded by Pfizer and Bristol-Myers Squibb; ClinicalTrials.gov number, NCT00643201). PMID 24344086 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 19966341 not stated (abstract only - full text not retrieved) — abstract abstract :
```

Candidate 1 of 1; SHA-256 `e808bf7094ccf1b0d5d299e5e8e0b307e5af2c6184103b4f34a8b0d9284157f2`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 4 of 4 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 21128814 industry — abstract abstract : (Funded by Bayer Schering Pharma and Ortho-McNeil; ClinicalTrials.gov numbers, NCT00440193 and NCT00439725.). PMID 22449293 industry — abstract abstract : (Funded by Bayer HealthCare and Janssen Pharmaceuticals; EINSTEIN-PE ClinicalTrials.gov number, NCT00439777.). PMID 23808982 industry — abstract abstract : CONCLUSIONS: A fixed-dose regimen of apixaban alone was noninferior to conventional therapy for the treatment of acute venous thromboembolism and was associated with significantly less bleeding (Funded by Pfizer and Bristol-Myers Squibb; ClinicalTrials.gov number, NCT00643201). PMID 23991658 industry — abstract abstract : (Funded by Daiichi-Sankyo; Hokusai-VTE ClinicalTrials.gov number, NCT00986154.). PMID 19966341 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 24344086 not stated (abstract only - full text not retrieved) — abstract abstract :
```

</details>

<details><summary>Pair 71 of 232 — docs/reviews/doac-vte-recurrence/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `6dcbdc0a3f29671c6468db1698e380c066006340f4040c993b6353cbf86946e1`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=6 of 6)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `b19383aeef918e714c068d26909258bd7a1bd38bc41439a739b197274935fa54`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 6: PMID 24344086 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 19966341 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 22449293 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 21128814 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 23991658 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 23808982 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 72 of 232 — docs/reviews/doac-vte-recurrence/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `8ca08339ffcc6910fea14e94c0bbb53f77ea42ccd537944715fb10eff04176ef`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency ASSESSED: not downgraded tau^2=0.0 (no between-study heterogeneity detected) Imprecision ASSESSED: −1 95% CI [0.7479, 1.105]; GRADE default appreciable-effect thresholds 0.75/1.25; no topic threshold registered; spans clinical decisions or inadequate information -> imprecise; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) missing/invalid registry census inputs: enumerated, ongoing_or_recent, ghost_upper_bound, positive completed-trial denominator
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `b19383aeef918e714c068d26909258bd7a1bd38bc41439a739b197274935fa54`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 6: PMID 24344086 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 19966341 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 22449293 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 21128814 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 23991658 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 23808982 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 73 of 232 — docs/reviews/doac-vte-recurrence/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `d6cdc1b8f2806a8da5ff7e7b5fc45b009b2766c6ef431196a2cf408055a887fb`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 4 of 4 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 2 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 22449293 industry abstract only risk profile. (Funded by Bayer HealthCare and Janssen Pharmaceuticals; EINSTEIN-PE ClinicalTrials.gov number, NCT00439777.). PMID 21128814 industry abstract only icoagulation. (Funded by Bayer Schering Pharma and Ortho-McNeil; ClinicalTrials.gov numbers, NCT00440193 and NCT00439725.). PMID 23991658 industry abstract only ary embolism. (Funded by Daiichi-Sankyo; Hokusai-VTE ClinicalTrials.gov number, NCT00986154.). PMID 23808982 industry abstract only less bleeding (Funded by Pfizer and Bristol-Myers Squibb; ClinicalTrials.gov number, NCT00643201). PMID 24344086 not stated (abstract only — full text not retrieved) abstract only PMID 19966341 not stated (abstract only — full text not retrieved) abstract only
```

Candidate 1 of 1; SHA-256 `e808bf7094ccf1b0d5d299e5e8e0b307e5af2c6184103b4f34a8b0d9284157f2`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 4 of 4 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 21128814 industry — abstract abstract : (Funded by Bayer Schering Pharma and Ortho-McNeil; ClinicalTrials.gov numbers, NCT00440193 and NCT00439725.). PMID 22449293 industry — abstract abstract : (Funded by Bayer HealthCare and Janssen Pharmaceuticals; EINSTEIN-PE ClinicalTrials.gov number, NCT00439777.). PMID 23808982 industry — abstract abstract : CONCLUSIONS: A fixed-dose regimen of apixaban alone was noninferior to conventional therapy for the treatment of acute venous thromboembolism and was associated with significantly less bleeding (Funded by Pfizer and Bristol-Myers Squibb; ClinicalTrials.gov number, NCT00643201). PMID 23991658 industry — abstract abstract : (Funded by Daiichi-Sankyo; Hokusai-VTE ClinicalTrials.gov number, NCT00986154.). PMID 19966341 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 24344086 not stated (abstract only - full text not retrieved) — abstract abstract :
```

</details>

<details><summary>Pair 74 of 232 — docs/reviews/doac-vte-recurrence/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `da01b6ba519d765f1f7085f7413af2667584916e67a43fd872d8f391a72c3f51`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 6 of 6 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=6, HR 0.9092 [0.7478, 1.1054] Low risk of bias only k=4, HR 0.917 [0.6926, 1.2141]
```

Candidate 1 of 1; SHA-256 `f7f6eb8ef26dd186392711f9e4a855ef2943d9b059b983abfcf39544728ced99`:

```text
Does the result survive dropping the trials that are not low risk of bias? Not computed (PRIMARY_ABSENT): the primary outcome has no pooled result (present = False). The per-trial rows and their risk-of-bias ratings are shown above; the omission is recorded in the review object as rob_sensitivity_omitted , not left silent.
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `b19383aeef918e714c068d26909258bd7a1bd38bc41439a739b197274935fa54`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 6: PMID 24344086 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 19966341 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 22449293 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 21128814 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 23991658 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 23808982 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 75 of 232 — docs/reviews/doac-vte-recurrence/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `ac057cdbffb6d6ed529764ed96d02c9bdf085df5d37d7c6dd7ccb84bffb0c38c`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 6 assessed trial(s) at high risk; fewer than half at 'some concerns' Inconsistency not downgraded tau^2=0.0 (no between-study heterogeneity detected) Imprecision −1 95% CI [0.7478, 1.1054]; crosses the null AND is compatible with an appreciable benefit (<=0.75) -> imprecise (the estimate is consistent with both no effect and an appreciable effect) Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED no registry ghost census available for this topic
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `b19383aeef918e714c068d26909258bd7a1bd38bc41439a739b197274935fa54`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 6: PMID 24344086 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 19966341 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 22449293 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 21128814 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 23991658 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 23808982 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 76 of 232 — docs/reviews/dpp4-mace-t2d/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `5556434988f892f3345f109f0e90031b1a08be8f125d87b413d0fbb642f775de`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (RAN_ERROR_rendered_as_run): Registry-first (AACT) = RAN_ERROR; the source_status table shows it, but the search narrative still presents the topic as registry-first. RAN_ERROR must never be rendered as a completed search (extends the audit-22 NOT_RUN gate limb to RAN_ERROR). a trial identified as eligible under the registered PICO is not pooled (TECOS (3-point MACE from primary publication)) — the pooled result and completeness claim cannot be current screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT00968708; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `4a57a952e19d231b7de4166a6ef91496fcbf1189739307a4f2e5dfb61ffa740a`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (RAN_ERROR_rendered_as_run): Registry-first (AACT) = RAN_ERROR; the source_status table shows it, but the search narrative still presents the topic as registry-first. RAN_ERROR must never be rendered as a completed search (extends the audit-22 NOT_RUN gate limb to RAN_ERROR). TECOS (3-point MACE from primary publication): named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed a trial identified as eligible under the registered PICO is not pooled (TECOS (3-point MACE from primary publication)) — the pooled result and completeness claim cannot be current screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT00968708, NCT01897532, NCT01703208; the completeness claim cannot be current
```

</details>

<details><summary>Pair 77 of 232 — docs/reviews/dpp4-mace-t2d/index.html — Parser-confirmed contrast disclosure</summary>

Source ref: `38c04411`; lost SHA-256: `c8e991ff7092138805d92e3c7a5a1b962a338e0bca6863a11d59e4b10cf6c75e`.

Lost full text:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 2 of 3 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 28893244 contrast unverified (registry class label / dev code) omarigliptin 23992601 parser-confirmed contrast saxagliptin 30418475 parser-confirmed contrast linagliptin
```

Candidate 1 of 1; SHA-256 `2ff3417e55c1dcee3da128f90b365c2f04dcb6721486d8449dc50e5d0e671680`:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 1 of 1 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 23992601 parser-confirmed contrast saxagliptin
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 78 of 232 — docs/reviews/dpp4-mace-t2d/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `580d898a32bb391d40bffc52365a5115d212915e97cf162ce2eed944c76965d2`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 3 of 3 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 23992601 industry — abstract abstract : (Funded by AstraZeneca and Bristol-Myers Squibb; SAVOR-TIMI 53 ClinicalTrials.gov number, NCT01107886.). PMID 26052984 industry — abstract abstract : (Funded by Merck Sharp & Dohme; TECOS ClinicalTrials.gov number, NCT00790205.). PMID 23992602 industry — abstract abstract : (Funded by Takeda Development Center Americas; EXAMINE ClinicalTrials.gov number, NCT00968708.). PMID 30418475 not stated (full text scanned) — full text full text : PMID 28893244 not stated (abstract only - full text not retrieved) — abstract abstract :
```

Candidate 1 of 1; SHA-256 `f31308ba2d2fe5e85f4ab0ba7b97f6bf3f1b5a3a238c2cb1b980f4d92d78f2ec`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 3 of 3 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 23992601 industry — abstract abstract : (Funded by AstraZeneca and Bristol-Myers Squibb; SAVOR-TIMI 53 ClinicalTrials.gov number, NCT01107886.). PMID 26052984 industry — abstract abstract : (Funded by Merck Sharp & Dohme; TECOS ClinicalTrials.gov number, NCT00790205.). PMID 23992602 industry — abstract abstract : (Funded by Takeda Development Center Americas; EXAMINE ClinicalTrials.gov number, NCT00968708.). PMID 28893244 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 30418475 not stated (full text scanned) — full text full text :
```

</details>

<details><summary>Pair 79 of 232 — docs/reviews/dpp4-mace-t2d/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `1e2c5ba31fccc110a76db81a398149dc4a7581cd90b8388d9eae24f224259ba5`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=3 of 3)
```

Candidate 1 of 1; SHA-256 `907e96459f0676ed291eafe578d7ed148d3184fa1b8274d074077cc53eadf371`:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=1 of 1)
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `433a039922e4893e605b8022e51a49b452f3ad755a2d8789e1cc481a1ecb0c2f`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 30418475 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 28893244 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 80 of 232 — docs/reviews/dpp4-mace-t2d/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `4917ca183be86759552f6bcbd6f0e36569223763385dfedf6195dbfddfeed42e`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.8391, 1.2094]; within GRADE default thresholds 0.75/1.25; no mechanical downgrade; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) missing/invalid registry census inputs: enumerated, ongoing_or_recent, ghost_upper_bound, positive completed-trial denominator
```

Candidate 1 of 1; SHA-256 `91052882f9514e4427ed094108054aa3e37026a9bd1a19e1ffdfa4933b34cfe6`:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.89, 1.12]; within GRADE default thresholds 0.75/1.25; no mechanical downgrade; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) missing/invalid registry census inputs: enumerated, ongoing_or_recent, ghost_upper_bound, positive completed-trial denominator
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `433a039922e4893e605b8022e51a49b452f3ad755a2d8789e1cc481a1ecb0c2f`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 30418475 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 28893244 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 81 of 232 — docs/reviews/dpp4-mace-t2d/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `ca478999427457da8d80f523b9328f155916acdfbe6b063d1646697f7201875f`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (RAN_ERROR_rendered_as_run): Registry-first (AACT) = RAN_ERROR; the source_status table shows it, but the search narrative still presents the topic as registry-first. RAN_ERROR must never be rendered as a completed search (extends the audit-22 NOT_RUN gate limb to RAN_ERROR). a trial identified as eligible under the registered PICO is not pooled (TECOS (3-point MACE from primary publication)) — the pooled result and completeness claim cannot be current screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: 23992602, 26052984; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `4a57a952e19d231b7de4166a6ef91496fcbf1189739307a4f2e5dfb61ffa740a`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (RAN_ERROR_rendered_as_run): Registry-first (AACT) = RAN_ERROR; the source_status table shows it, but the search narrative still presents the topic as registry-first. RAN_ERROR must never be rendered as a completed search (extends the audit-22 NOT_RUN gate limb to RAN_ERROR). TECOS (3-point MACE from primary publication): named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed a trial identified as eligible under the registered PICO is not pooled (TECOS (3-point MACE from primary publication)) — the pooled result and completeness claim cannot be current screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT00968708, NCT01897532, NCT01703208; the completeness claim cannot be current
```

</details>

<details><summary>Pair 82 of 232 — docs/reviews/dpp4-mace-t2d/index.html — Randomised-contrast disclosure</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `66d6d9cbc227d9a699cdf986265b2b7c04a066c4b01de1cc8e8e380e0282a071`.

Lost full text:

```text
Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 2 of 3 pooled trials have a registry-confirmed contrast (the intervention of interest differs across arms). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 28893244 contrast unverified (registry class label / dev code) omarigliptin 23992601 randomised contrast verified saxagliptin 30418475 randomised contrast verified linagliptin
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 83 of 232 — docs/reviews/dpp4-mace-t2d/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `80050dda0a27c639679fbcbb44ad5c7a74c4ca8ac59d189adaf5c8c3756d86b0`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 1 of 1 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 2 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 23992601 industry abstract only ith diabetes. (Funded by AstraZeneca and Bristol-Myers Squibb; SAVOR-TIMI 53 ClinicalTrials.gov number, NCT01107886.). PMID 30418475 not stated (abstract only — full text not retrieved) abstract only PMID 28893244 not stated (abstract only — full text not retrieved) abstract only
```

Candidate 1 of 1; SHA-256 `f31308ba2d2fe5e85f4ab0ba7b97f6bf3f1b5a3a238c2cb1b980f4d92d78f2ec`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 3 of 3 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 23992601 industry — abstract abstract : (Funded by AstraZeneca and Bristol-Myers Squibb; SAVOR-TIMI 53 ClinicalTrials.gov number, NCT01107886.). PMID 26052984 industry — abstract abstract : (Funded by Merck Sharp & Dohme; TECOS ClinicalTrials.gov number, NCT00790205.). PMID 23992602 industry — abstract abstract : (Funded by Takeda Development Center Americas; EXAMINE ClinicalTrials.gov number, NCT00968708.). PMID 28893244 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 30418475 not stated (full text scanned) — full text full text :
```

</details>

<details><summary>Pair 84 of 232 — docs/reviews/dpp4-mace-t2d/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `91ec4628b63b3e86d9c7d2f143975fdc54e4c8782edea24d1fdb19b3fb96c48e`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 3 of 3 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=3, HR 1.0074 [0.8391, 1.2094] Low risk of bias only k=3, HR 1.0074 [0.8391, 1.2094] (fewer trials than the full pool — see coverage)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `433a039922e4893e605b8022e51a49b452f3ad755a2d8789e1cc481a1ecb0c2f`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 30418475 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 28893244 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 85 of 232 — docs/reviews/dpp4-mace-t2d/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `6fd4fe1fa9d7c27b9dae78df1aa0508709049363a38be5e9069ba7005c2476a2`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capped below high because D3 (missing outcome data), a required risk-of-bias domain, is NOT ASSESSED for any pooled trial (no outcome-missingness source) — high certainty cannot be certified on a structurally-incomplete bias assessment. PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 3 assessed trial(s) at high risk; fewer than half at 'some concerns' Inconsistency not downgraded tau^2=0.0 (no between-study heterogeneity detected) Imprecision not downgraded 95% CI [0.8391, 1.2094]; crosses the null but excludes an appreciable effect on BOTH sides (within 0.75-1.25) -> precise about the absence of an appreciable effect Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED no registry ghost census available for this topic
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `433a039922e4893e605b8022e51a49b452f3ad755a2d8789e1cc481a1ecb0c2f`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 30418475 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 28893244 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 86 of 232 — docs/reviews/empagliflozin-hfpef-hosp/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `cfc9568ea0f61a7c92a8223bd8f2ddf9558923c6bb7e601f015615107b97c911`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (PMID_ENUMERATION_explicit): protocol Search section explicitly says UID-anchored queries for the named trials — known-item retrieval, cannot discover an unknown eligible trial. a trial identified as eligible under the registered PICO is not pooled (EMPA-VISION) — the pooled result and completeness claim cannot be current the primary outcome is reported by trials that could not be pooled (34449189) — the pooled k is known-incomplete screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT03057951, NCT06249945, NCT03448406; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

Candidate 1 of 1; SHA-256 `a5a9c9cdd8ad516c8c44f824d93fa732975600a3ef4b3266e5cea886585a260e`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (PMID_ENUMERATION_explicit): protocol Search section explicitly says UID-anchored queries for the named trials — known-item retrieval, cannot discover an unknown eligible trial. EMPA-VISION: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed a trial identified as eligible under the registered PICO is not pooled (EMPA-VISION) — the pooled result and completeness claim cannot be current the primary outcome is reported by trials that could not be pooled (34449189) — the pooled k is known-incomplete screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT03057951, NCT06249945, NCT03448406; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 87 of 232 — docs/reviews/empagliflozin-hfpef-hosp/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `86248522ae252f46158fa0f19c9654208ea1a7a7ee7a08f74b56e40d8813e6be`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (PMID_ENUMERATION_explicit): protocol Search section explicitly says UID-anchored queries for the named trials — known-item retrieval, cannot discover an unknown eligible trial. a trial identified as eligible under the registered PICO is not pooled (EMPA-VISION) — the pooled result and completeness claim cannot be current screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: SAK · NCT05138575, EMPA-PRED · NCT06249945, NCT03448406; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `a5a9c9cdd8ad516c8c44f824d93fa732975600a3ef4b3266e5cea886585a260e`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (PMID_ENUMERATION_explicit): protocol Search section explicitly says UID-anchored queries for the named trials — known-item retrieval, cannot discover an unknown eligible trial. EMPA-VISION: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed a trial identified as eligible under the registered PICO is not pooled (EMPA-VISION) — the pooled result and completeness claim cannot be current the primary outcome is reported by trials that could not be pooled (34449189) — the pooled k is known-incomplete screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT03057951, NCT06249945, NCT03448406; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 88 of 232 — docs/reviews/esketamine-trd-madrs/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `01299cde55338a3588f4baa42d2a4695b75a1ac33ffd8b761abd1454ce9967e0`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (RAN_ERROR_rendered_as_run): Registry-first (AACT) = RAN_ERROR; the source_status table shows it, but the search narrative still presents the topic as registry-first. RAN_ERROR must never be rendered as a completed search (extends the audit-22 NOT_RUN gate limb to RAN_ERROR). screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT02417064; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `82d897f44348ef55b004762e07fc168436d3c45755abaf365d2e92565ebb03a7`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (RAN_ERROR_rendered_as_run): Registry-first (AACT) = RAN_ERROR; the source_status table shows it, but the search narrative still presents the topic as registry-first. RAN_ERROR must never be rendered as a completed search (extends the audit-22 NOT_RUN gate limb to RAN_ERROR). screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT03434041, NCT02422186, NCT02417064; the completeness claim cannot be current
```

</details>

<details><summary>Pair 89 of 232 — docs/reviews/esketamine-trd-madrs/index.html — UNRENDERABLE stale contrast block</summary>

Source ref: `38c04411`; lost SHA-256: `58032f853ca0b347b94e066b1c40fe7cac513f72f45358eefa1d2a22aa97b6e5`.

Lost full text:

```text
UNRENDERABLE stale contrast block. cached arm-contrast membership named trials not in the current consumed pool; current pooled trial ids: 31109201, 37025256, NCT02422186; suppressed stale ids: NCT02417064.
```

Candidate 1 of 1; SHA-256 `58f8e38cd11836a73585ecd83edc2b771137cb23fb3a08cb4dedf216980ef765`:

```text
UNRENDERABLE stale contrast block. cached arm-contrast membership named trials not in the current consumed pool; current pooled trial ids: 31109201; suppressed stale ids: 37025256, NCT02417064, NCT02422186.
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 90 of 232 — docs/reviews/esketamine-trd-madrs/index.html — Parser-confirmed contrast disclosure</summary>

Source ref: `38c04411`; lost SHA-256: `7ea6405431e1307edeb6b1f59602c892b65f1471af4af24a9dcf5312bdc440d2`.

Lost full text:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 3 of 3 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 31109201 parser-confirmed contrast esketamine 37025256 parser-confirmed contrast esketamine 56 mg; esketamine 84 mg NCT02422186 parser-confirmed contrast esketamine
```

Candidate 1 of 1; SHA-256 `aaa2b96c9c06de086d703d0d67a76d8425e373f8e654f172787d0373d7e71c5b`:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 1 of 1 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 31109201 parser-confirmed contrast esketamine
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 91 of 232 — docs/reviews/esketamine-trd-madrs/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `eb5eebabbb8cb30e2d43ba9cc1c5f8fc9124eb255d36ab3d762262dff94d1f16`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 2 of 2 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 37025256 industry — full text full text : </funding-source></award-group><funding-statement>The study was funded by Janssen Research & Development, LLC.</funding-statement></funding-group><counts><fig-count count="2"/><table-count count="4"/><ref-count count="35"/><page-count count="15"/></counts><custom-meta-group><custom-meta><meta-name>pmc-status-qastatus</meta-name><meta-value>0</meta-value></custom-meta><custom-meta><meta-name>pmc-status-live</meta-name><meta-value>yes</meta-value></custom-meta><custom-meta><met PMID 31109201 mixed — linked full text PMID 34293233 linked full text PMID 34293233 : Thase reports that The Perelman School of Medicine of the University of Pennsylvania received grants from Johnson & Johnson to conduct the research protocol described in this report at his site. NCT02422186 not stated (full text scanned) — linked full text PMID 34973081 linked full text PMID 34973081 : NCT02417064 not stated (full text scanned) — linked full text PMID 37019044 linked full text PMID 37019044 :
```

Candidate 1 of 1; SHA-256 `dfd8c1b82917e16064af027c359735259477163bafef2a3eedbe3a21b53e2fb1`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 2 of 2 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 37025256 industry — full text full text : </funding-source></award-group><funding-statement>The study was funded by Janssen Research & Development, LLC.</funding-statement></funding-group><counts><fig-count count="2"/><table-count count="4"/><ref-count count="35"/><page-count count="15"/></counts><custom-meta-group><custom-meta><meta-name>pmc-status-qastatus</meta-name><meta-value>0</meta-value></custom-meta><custom-meta><meta-name>pmc-status-live</meta-name><meta-value>yes</meta-value></custom-meta><custom-meta><met PMID 31109201 mixed — linked full text PMID 34293233 linked full text PMID 34293233 : Thase reports that The Perelman School of Medicine of the University of Pennsylvania received grants from Johnson & Johnson to conduct the research protocol described in this report at his site. NCT02417064 not stated (full text scanned) — linked full text PMID 37019044 linked full text PMID 37019044 : NCT02422186 not stated (full text scanned) — linked full text PMID 34973081 linked full text PMID 34973081 :
```

</details>

<details><summary>Pair 92 of 232 — docs/reviews/esketamine-trd-madrs/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `1e2c5ba31fccc110a76db81a398149dc4a7581cd90b8388d9eae24f224259ba5`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=3 of 3)
```

Candidate 1 of 1; SHA-256 `907e96459f0676ed291eafe578d7ed148d3184fa1b8274d074077cc53eadf371`:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=1 of 1)
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `2818743eb9ed2c056ca6f59f7c08963a5f04c3e351a84b7c5890b7bbfa07850b`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 0; migration state (unbound_legacy, pooled and counted separately) 1 [PMID 31109201]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 37025256 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); NCT02422186 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 93 of 232 — docs/reviews/esketamine-trd-madrs/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `09951e84e6d934e37bf8f3f632c9515704884084060958f6b41451fd96686d3b`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (1 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [-7.3323, 1.1315]; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) missing/invalid registry census inputs: enumerated, ongoing_or_recent, ghost_upper_bound, positive completed-trial denominator
```

Candidate 1 of 1; SHA-256 `e15254665ecf0f37460aae77c0d9dc88e757b9602d9c9bd1e99ce6a6138408b9`:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [-8.0296, -0.7704]; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) missing/invalid registry census inputs: enumerated, ongoing_or_recent, ghost_upper_bound, positive completed-trial denominator
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `2818743eb9ed2c056ca6f59f7c08963a5f04c3e351a84b7c5890b7bbfa07850b`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 0; migration state (unbound_legacy, pooled and counted separately) 1 [PMID 31109201]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 37025256 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); NCT02422186 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 94 of 232 — docs/reviews/esketamine-trd-madrs/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `c259836475d227609f048b27f7b6ba7edd984a56f49e84041d3c6d9b5e4776e1`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (RAN_ERROR_rendered_as_run): Registry-first (AACT) = RAN_ERROR; the source_status table shows it, but the search narrative still presents the topic as registry-first. RAN_ERROR must never be rendered as a completed search (extends the audit-22 NOT_RUN gate limb to RAN_ERROR). screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: 34696742, SYNAPSE · NCT01998958; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `82d897f44348ef55b004762e07fc168436d3c45755abaf365d2e92565ebb03a7`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (RAN_ERROR_rendered_as_run): Registry-first (AACT) = RAN_ERROR; the source_status table shows it, but the search narrative still presents the topic as registry-first. RAN_ERROR must never be rendered as a completed search (extends the audit-22 NOT_RUN gate limb to RAN_ERROR). screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT03434041, NCT02422186, NCT02417064; the completeness claim cannot be current
```

</details>

<details><summary>Pair 95 of 232 — docs/reviews/esketamine-trd-madrs/index.html — DECLARED ABSENT</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `4554b38e12246adb7ec988f9bb194fe41e7ef3abdf7fe3db1e2c31bfc5621cc9`.

Lost full text:

```text
DECLARED ABSENT. REPORTED but not extractable as a pooled value: 34696742, 31109201 mention this outcome in the committed abstract, but without arm counts or an effect+CI in an extractable form (e.g. a bare percentage with no denominator). This outcome is NOT absent — it is reported-but-not-poolable from the committed source; full-text acquisition would recover the countable form.
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 96 of 232 — docs/reviews/esketamine-trd-madrs/index.html — Randomised-contrast disclosure</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `4c29b75436df70dfc57dde8e4c0b7975089c3303c76a5d93c7c5d95c4e231a5c`.

Lost full text:

```text
Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 4 of 4 pooled trials have a registry-confirmed contrast (the intervention of interest differs across arms). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 31109201 randomised contrast verified esketamine 37025256 randomised contrast verified esketamine 56 mg; esketamine 84 mg NCT02417064 randomised contrast verified esketamine NCT02422186 randomised contrast verified esketamine
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 97 of 232 — docs/reviews/esketamine-trd-madrs/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `17c77c145420770141d32fd0d8156b182d450fd35b6287a5cf9b40e2aba0c827`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 0 of 0 known (4 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 2 with no funding statement in the full text (genuinely silent) and 2 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 37025256 not stated (full text scanned) full text PMID 31109201 not stated (full text scanned) full text NCT02422186 not stated (abstract only — full text not retrieved) abstract only NCT02417064 not stated (abstract only — full text not retrieved) abstract only
```

Candidate 1 of 1; SHA-256 `dfd8c1b82917e16064af027c359735259477163bafef2a3eedbe3a21b53e2fb1`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 2 of 2 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 37025256 industry — full text full text : </funding-source></award-group><funding-statement>The study was funded by Janssen Research & Development, LLC.</funding-statement></funding-group><counts><fig-count count="2"/><table-count count="4"/><ref-count count="35"/><page-count count="15"/></counts><custom-meta-group><custom-meta><meta-name>pmc-status-qastatus</meta-name><meta-value>0</meta-value></custom-meta><custom-meta><meta-name>pmc-status-live</meta-name><meta-value>yes</meta-value></custom-meta><custom-meta><met PMID 31109201 mixed — linked full text PMID 34293233 linked full text PMID 34293233 : Thase reports that The Perelman School of Medicine of the University of Pennsylvania received grants from Johnson & Johnson to conduct the research protocol described in this report at his site. NCT02417064 not stated (full text scanned) — linked full text PMID 37019044 linked full text PMID 37019044 : NCT02422186 not stated (full text scanned) — linked full text PMID 34973081 linked full text PMID 34973081 :
```

</details>

<details><summary>Pair 98 of 232 — docs/reviews/esketamine-trd-madrs/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `7058b2699c4ee2d0f8489f2cd13f365fa05dcf95e49011617b8ecdca765369fd`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 2 of 4 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=4, MD -3.3445 [-6.0701, -0.6189] Low risk of bias only NOT ESTIMABLE — no pooled trial qualifies as low risk of bias, so this stratum has no trials to re-pool (an empty subgroup is not agreement with the full pool)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `2818743eb9ed2c056ca6f59f7c08963a5f04c3e351a84b7c5890b7bbfa07850b`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 0; migration state (unbound_legacy, pooled and counted separately) 1 [PMID 31109201]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 37025256 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); NCT02422186 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 99 of 232 — docs/reviews/esketamine-trd-madrs/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `7a1b2f9d0aa30150320bb235576d215f3bc335d0d9a1f07ccb06f24c2efac169`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias −1 2 of 2 assessed trial(s) at 'some concerns'; risk-of-bias signal available for only 2 of 4 pooled trials (registry-derived), so the rating is capped Inconsistency not downgraded tau^2=0.0 (no between-study heterogeneity detected) Imprecision not downgraded 95% CI [-6.0701, -0.6189] Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED no registry ghost census available for this topic
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `2818743eb9ed2c056ca6f59f7c08963a5f04c3e351a84b7c5890b7bbfa07850b`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 0; migration state (unbound_legacy, pooled and counted separately) 1 [PMID 31109201]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 37025256 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); NCT02422186 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 100 of 232 — docs/reviews/glp1-ra-mace-t2d/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `907a0a87c6810684ddfac45e23f6d3e424d5576970e1b682c17e86eaa0e668c5`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (PMID_ENUMERATION_explicit): search.retrieval.enumeration_only=true; no discovery-capable concept source ran ELIXA: committed source held; extraction/adjudication pending; not pooled FREEDOM-CVO: committed source held; extraction/adjudication pending; not pooled FLOW: committed source held; extraction/adjudication pending; not pooled screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT01147250; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `1e498684fd46cb03e96738e5e7ee0546ef20637e597225d2c907ba8764db00a1`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (PMID_ENUMERATION_explicit): search.retrieval.enumeration_only=true; no discovery-capable concept source ran ELIXA: committed source held; extraction/adjudication pending; not pooled FREEDOM-CVO: committed source held; extraction/adjudication pending; not pooled FLOW: committed source held; extraction/adjudication pending; not pooled screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT02465515, NCT01147250; the completeness claim cannot be current
```

</details>

<details><summary>Pair 101 of 232 — docs/reviews/glp1-ra-mace-t2d/index.html — Parser-confirmed contrast disclosure</summary>

Source ref: `38c04411`; lost SHA-256: `2ec9bffdfb3fdf6c42ee5840880137a86083d73a01a8a56780cbeff8d53c27fb`.

Lost full text:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 8 of 8 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 27295427 parser-confirmed contrast liraglutide 27633186 parser-confirmed contrast semaglutide 28910237 parser-confirmed contrast exenatide once weekly 30291013 parser-confirmed contrast albiglutide 30 mg; albiglutide 50 mg 31185157 parser-confirmed contrast semaglutide 31189511 parser-confirmed contrast dulaglutide 34215025 parser-confirmed contrast efpeglenatide (sar439977) 40162642 parser-confirmed contrast semaglutide
```

Candidate 1 of 1; SHA-256 `fd5611cf53d0abf279a15e28fe18eed2f32d7ae5c8be7cf2772f4334c7b2fe20`:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 7 of 7 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 27295427 parser-confirmed contrast liraglutide 27633186 parser-confirmed contrast semaglutide 28910237 parser-confirmed contrast exenatide once weekly 31185157 parser-confirmed contrast semaglutide 31189511 parser-confirmed contrast dulaglutide 34215025 parser-confirmed contrast efpeglenatide (sar439977) 40162642 parser-confirmed contrast semaglutide
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 102 of 232 — docs/reviews/glp1-ra-mace-t2d/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `90a9192933d9a43064a8eff14b36abeab53d9fb39698fc154f86f02e2e6005e7`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 9 of 9 known (0 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 31185157 industry — abstract abstract : (Funded by Novo Nordisk; PIONEER 6 ClinicalTrials.gov number, NCT02692716.). PMID 27633186 industry — abstract abstract : (Funded by Novo Nordisk; SUSTAIN-6 ClinicalTrials.gov number, NCT01720446 .). PMID 34215025 industry — abstract abstract : (Funded by Sanofi; AMPLITUDE-O ClinicalTrials.gov number, NCT03496298.). PMID 31189511 industry — abstract abstract : FUNDING: Eli Lilly and Company. PMID 30291013 industry — abstract abstract : FUNDING: GlaxoSmithKline. PMID 28910237 industry — full text full text : (Funded by Amylin Pharmaceuticals; EXSCEL <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://ClinicalTrials.gov" ext-link-type="uri">ClinicalTrials.gov</ext-link> number, <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="https://clinicaltrials.gov/ct2/show/NCT0144338" ext-link-type="uri">NCT0144338</ext-link>.)</p></sec></abstract><custom-meta-group><custom-meta><meta-name>pmc-statu PMID 40162642 industry — abstract abstract : (Funded by Novo Nordisk; SOUL ClinicalTrials.gov number, NCT03914326.). PMID 26630143 industry — abstract abstract : (Funded by Sanofi; ELIXA ClinicalTrials.gov number, NCT01147250.). PMID 27295427 mixed — full text full text : (Funded by Novo Nordisk and the National Institutes of Health; LEADER ClinicalTrials.gov number, <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" ext-link-type="pmc:clinical-trial" xlink:href="NCT01179048">NCT01179048</ext-link>.)</p></sec></abstract><custom-meta-group><custom-meta><meta-name>pmc-status-qastatus</meta-name><meta-value>0</meta-value></custom-meta><custom-meta><meta-name>pmc-status-live</meta-name><
```

Candidate 1 of 1; SHA-256 `f5424b0f1335bc705967ff505c5127d8ca936be2a53b24888dcdf91caf5db0d8`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 9 of 9 known (0 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 31185157 industry — abstract abstract : (Funded by Novo Nordisk; PIONEER 6 ClinicalTrials.gov number, NCT02692716.). PMID 27633186 industry — abstract abstract : (Funded by Novo Nordisk; SUSTAIN-6 ClinicalTrials.gov number, NCT01720446 .). PMID 34215025 industry — abstract abstract : (Funded by Sanofi; AMPLITUDE-O ClinicalTrials.gov number, NCT03496298.). PMID 31189511 industry — abstract abstract : FUNDING: Eli Lilly and Company. PMID 28910237 industry — full text full text : (Funded by Amylin Pharmaceuticals; EXSCEL <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://ClinicalTrials.gov" ext-link-type="uri">ClinicalTrials.gov</ext-link> number, <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="https://clinicaltrials.gov/ct2/show/NCT0144338" ext-link-type="uri">NCT0144338</ext-link>.)</p></sec></abstract><custom-meta-group><custom-meta><meta-name>pmc-statu PMID 40162642 industry — abstract abstract : (Funded by Novo Nordisk; SOUL ClinicalTrials.gov number, NCT03914326.). PMID 26630143 industry — abstract abstract : (Funded by Sanofi; ELIXA ClinicalTrials.gov number, NCT01147250.). PMID 30291013 industry — abstract abstract : FUNDING: GlaxoSmithKline. PMID 27295427 mixed — full text full text : (Funded by Novo Nordisk and the National Institutes of Health; LEADER ClinicalTrials.gov number, <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" ext-link-type="pmc:clinical-trial" xlink:href="NCT01179048">NCT01179048</ext-link>.)</p></sec></abstract><custom-meta-group><custom-meta><meta-name>pmc-status-qastatus</meta-name><meta-value>0</meta-value></custom-meta><custom-meta><meta-name>pmc-status-live</meta-name><
```

</details>

<details><summary>Pair 103 of 232 — docs/reviews/glp1-ra-mace-t2d/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `be6b448a81c25e2c18c65cf72bba79948cf28832de3c20f787dfcce5b33d0acd`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=8 of 8)
```

Candidate 1 of 1; SHA-256 `db43a32b53c490cce46ec2ab1216b8bcf25d49532c5728adb77b242c0cd75b17`:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=7 of 7)
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `b57491cebd163ecc2920ebaac311e2b3f12db6fe680fff315c4d97ac0a417201`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 7: admissible 7; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 30291013 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 104 of 232 — docs/reviews/glp1-ra-mace-t2d/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `633ecc11e57fd7397a82f0d46715cf75e825a5b0d8a3f4e5b53ae55763af7d32`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.8086, 0.9061]; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (118 of ~577 completed unpublished, 20%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

Candidate 1 of 1; SHA-256 `34712bd36c91fe113d28e570890cadea6c5a279a418aa86dedad576042819f7c`:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.8142, 0.9218]; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (118 of ~577 completed unpublished, 20%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `b57491cebd163ecc2920ebaac311e2b3f12db6fe680fff315c4d97ac0a417201`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 7: admissible 7; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 30291013 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 105 of 232 — docs/reviews/glp1-ra-mace-t2d/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `74ef9f624c5845659feef24079fb873482531098515959d4a9a1c20473b27570`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: a trial identified as eligible under the registered PICO is not pooled (FLOW, FREEDOM-CVO) — the pooled result and completeness claim cannot be current screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: 26630143; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `1e498684fd46cb03e96738e5e7ee0546ef20637e597225d2c907ba8764db00a1`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (PMID_ENUMERATION_explicit): search.retrieval.enumeration_only=true; no discovery-capable concept source ran ELIXA: committed source held; extraction/adjudication pending; not pooled FREEDOM-CVO: committed source held; extraction/adjudication pending; not pooled FLOW: committed source held; extraction/adjudication pending; not pooled screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT02465515, NCT01147250; the completeness claim cannot be current
```

</details>

<details><summary>Pair 106 of 232 — docs/reviews/glp1-ra-mace-t2d/index.html — DECLARED ABSENT</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `f3641fa7e56d8d396bc0f8e0e7938987d10f402964ce66d602c13133ff3df1fd`.

Lost full text:

```text
DECLARED ABSENT. REPORTED but not extractable as a pooled value: 31185157, 27295427, 34215025 mention this outcome in the committed abstract, but without arm counts or an effect+CI in an extractable form (e.g. a bare percentage with no denominator). This outcome is NOT absent — it is reported-but-not-poolable from the committed source; full-text acquisition would recover the countable form.
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 107 of 232 — docs/reviews/glp1-ra-mace-t2d/index.html — DECLARED ABSENT</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `181eb2cc7da5cb8589a7ebe140194b85594aa6dbd6f5994ce6e9d7f982d8e2b8`.

Lost full text:

```text
DECLARED ABSENT. REPORTED but not extractable as a pooled value: 31185157, 27633186, 27295427, 30291013 mention this outcome in the committed abstract, but without arm counts or an effect+CI in an extractable form (e.g. a bare percentage with no denominator). This outcome is NOT absent — it is reported-but-not-poolable from the committed source; full-text acquisition would recover the countable form.
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 108 of 232 — docs/reviews/glp1-ra-mace-t2d/index.html — Randomised-contrast disclosure</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `3b5fcb2c43c291d46f0928d1f6dd4f574eb1adc1d212f1113207d41844af8c41`.

Lost full text:

```text
Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 0 of 8 pooled trials have a registry-confirmed contrast (the intervention of interest differs across arms). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 27295427 contrast unverified (registry class label / dev code) liraglutide 27633186 contrast unverified (registry class label / dev code) semaglutide 28910237 contrast unverified (registry class label / dev code) exenatide once weekly 30291013 contrast unverified (registry class label / dev code) albiglutide 30 mg; albiglutide 50 mg 31185157 contrast unverified (registry class label / dev code) semaglutide 31189511 contrast unverified (registry class label / dev code) dulaglutide 34215025 contrast unverified (registry class label / dev code) efpeglenatide (sar439977) 40162642 contrast unverified (registry class label / dev code) semaglutide
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 109 of 232 — docs/reviews/glp1-ra-mace-t2d/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `ade5009855456019293990bec265c1e0ddea1fda4d155316b7f6728b27fef7eb`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 8 of 8 known (0 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 31185157 industry abstract only t of placebo. (Funded by Novo Nordisk; PIONEER 6 ClinicalTrials.gov number, NCT02692716.). PMID 27633186 industry abstract only semaglutide. (Funded by Novo Nordisk; SUSTAIN-6 ClinicalTrials.gov number, NCT01720446 .). PMID 34215025 industry abstract only ived placebo. (Funded by Sanofi; AMPLITUDE-O ClinicalTrials.gov number, NCT03496298.). PMID 31189511 industry abstract only risk factors. FUNDING: Eli Lilly and Company. PMID 30291013 industry abstract only pe 2 diabetes. FUNDING: GlaxoSmithKline. PMID 28910237 industry abstract only ived placebo. (Funded by Amylin Pharmaceuticals; EXSCEL ClinicalTrials.gov number, NCT01144338 .). PMID 40162642 industry abstract only than placebo. (Funded by Novo Nordisk; SOUL ClinicalTrials.gov number, NCT03914326.). PMID 27295427 mixed abstract only with placebo. (Funded by Novo Nordisk and the National Institutes of Health; LEADER ClinicalTrials.gov number, NCT01179048.).
```

Candidate 1 of 1; SHA-256 `f5424b0f1335bc705967ff505c5127d8ca936be2a53b24888dcdf91caf5db0d8`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 9 of 9 known (0 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 31185157 industry — abstract abstract : (Funded by Novo Nordisk; PIONEER 6 ClinicalTrials.gov number, NCT02692716.). PMID 27633186 industry — abstract abstract : (Funded by Novo Nordisk; SUSTAIN-6 ClinicalTrials.gov number, NCT01720446 .). PMID 34215025 industry — abstract abstract : (Funded by Sanofi; AMPLITUDE-O ClinicalTrials.gov number, NCT03496298.). PMID 31189511 industry — abstract abstract : FUNDING: Eli Lilly and Company. PMID 28910237 industry — full text full text : (Funded by Amylin Pharmaceuticals; EXSCEL <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://ClinicalTrials.gov" ext-link-type="uri">ClinicalTrials.gov</ext-link> number, <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="https://clinicaltrials.gov/ct2/show/NCT0144338" ext-link-type="uri">NCT0144338</ext-link>.)</p></sec></abstract><custom-meta-group><custom-meta><meta-name>pmc-statu PMID 40162642 industry — abstract abstract : (Funded by Novo Nordisk; SOUL ClinicalTrials.gov number, NCT03914326.). PMID 26630143 industry — abstract abstract : (Funded by Sanofi; ELIXA ClinicalTrials.gov number, NCT01147250.). PMID 30291013 industry — abstract abstract : FUNDING: GlaxoSmithKline. PMID 27295427 mixed — full text full text : (Funded by Novo Nordisk and the National Institutes of Health; LEADER ClinicalTrials.gov number, <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" ext-link-type="pmc:clinical-trial" xlink:href="NCT01179048">NCT01179048</ext-link>.)</p></sec></abstract><custom-meta-group><custom-meta><meta-name>pmc-status-qastatus</meta-name><meta-value>0</meta-value></custom-meta><custom-meta><meta-name>pmc-status-live</meta-name><
```

</details>

<details><summary>Pair 110 of 232 — docs/reviews/glp1-ra-mace-t2d/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `118737e7052fbdd570b2bb1df218c74b838fe181282b54f53fae236363d15295`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 7 of 8 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=8, HR 0.856 [0.8086, 0.9061] Low risk of bias only k=6, HR 0.8321 [0.7668, 0.9029]
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `b57491cebd163ecc2920ebaac311e2b3f12db6fe680fff315c4d97ac0a417201`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 7: admissible 7; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 30291013 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 111 of 232 — docs/reviews/glp1-ra-mace-t2d/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `04a2e41c88e8930b16c4783a824d69b3411af2e0f716308888eb7504faec9d34`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capped below high because risk of bias is not assessed for every pooled trial. PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 7 assessed trial(s) at high risk; fewer than half at 'some concerns'; risk-of-bias signal available for only 7 of 8 pooled trials (registry-derived), so the rating is capped Inconsistency not downgraded tau^2=4e-05; prediction interval not markedly wider than the CI Imprecision not downgraded 95% CI [0.8086, 0.9061]; excludes the null with a reasonably tight interval -> precise Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED registry census (118 of ~577 completed unpublished, 20%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `b57491cebd163ecc2920ebaac311e2b3f12db6fe680fff315c4d97ac0a417201`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 7: admissible 7; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 30291013 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 112 of 232 — docs/reviews/iv-iron-hfref-hosp/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `236daf6a2f0ee8c342526cfc66c3dddb25f954db03abd2568f7ea9ac17d0e72f`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. a trial identified as eligible under the registered PICO is not pooled (Toblli 2007, IRON-HF) — the pooled result and completeness claim cannot be current screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT03037931, PMID:34080008, NCT01394562, NCT00520780, NCT00125996; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `fbe403aa6e7530bd99dbcded8a6aba0f0b736b186c514f1b2b245aec6269af2c`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. Toblli 2007: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed IRON-HF: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed a trial identified as eligible under the registered PICO is not pooled (Toblli 2007, IRON-HF) — the pooled result and completeness claim cannot be current screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT03037931, PMID:34080008, NCT01394562, NCT00520780, NCT00125996; the completeness claim cannot be current
```

</details>

<details><summary>Pair 113 of 232 — docs/reviews/iv-iron-hfref-hosp/index.html — Pooled result SUPPRESSED</summary>

Source ref: `38c04411`; lost SHA-256: `07604e61937c4f367b1179f1768be53cc9b7db1b16e48d2aefe90bf2a6254096`.

Lost full text:

```text
Pooled result SUPPRESSED (estimand-incompatible). pooled effect SUPPRESSED: the trials mix incompatible estimand classes (HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO) — these effect measures are not one quantity without an explicit, source-backed conversion, so no pooled effect, CI, heterogeneity or sensitivity is valid. The per-trial estimates are shown; pool each coherent strand separately. Estimand classes: HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO; the 2 eligible trials are shown individually in Results, not pooled.
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `90253e8c344aabbf92aecd9cae73561570c98c1c78294d1f2792f758a7be53b0`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 1 [PMID 25176939]. Set aside on P5 (family eligibility) 1: PMID 40159390 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 114 of 232 — docs/reviews/iv-iron-hfref-hosp/index.html — Declared strands</summary>

Source ref: `38c04411`; lost SHA-256: `8c1056e4ccd044af03d9589b7fe844ae3255053da184a3118df8f04102ea0766`.

Lost full text:

```text
Declared strands (the single pool is suppressed; these are the endpoint-clean decompositions) Strands A and B measure the SAME endpoint (HF hospitalisation) two incompatible ways -- first-event HR (CONFIRM-HF) vs recurrent rate ratio (AFFIRM-AHF + FAIR-HF2). A hazard ratio of the first event and a rate ratio of all events are not the same quantity and cannot be pooled; the single-pool primary is therefore correctly suppressed. The strands below are the honest decomposition. Strand A — First-event hazard ratio (time to first HF hospitalisation) [ FIRST_EVENT_RATIO ]: CONFIRM-HF 0.39 (HR), k=1 (single trial) Strand B — Recurrent-event rate ratio, HF hospitalisation ALONE [ RATE ]: pooled 0.765 (0.232–2.522), k=2, HKSJ/PM τ²=0.0, crosses null [common-effect sensitivity 0.765 (0.636–0.919), NOT the registered result] Strand C — Recurrent-event rate ratio, HF hospitalisation + CV death COMPOSITE [ RATE ]: pooled 0.807 (0.281–2.312), k=2, HKSJ/PM τ²=0.0, crosses null [common-effect sensitivity 0.807 (0.686–0.949), NOT the registered result] Strand D — Participant-level risk (patients with >=1 HF hospitalisation) [ PARTICIPANT_RISK ]: CONFIRM-HF 0.39 (RR (crude)), k=1 (single trial) Refused cross-endpoint pool: The recurrent-event rate ratios do NOT form one pool. A pool of AFFIRM-AHF's HF-hosp-ALONE rate (0.74) with IRONMAN's HF-hosp+CV-death COMPOSITE rate (0.82) crosses the endpoint dimension of the compatibility key. If forced it would be 0.783 (0.275-2.233) -- this is the 0.783 figure previously treated as the recurrent strand; it mixes endpoints and is refused, not published. — REFUSED -- endpoint mismatch (HF-hosp alone vs composite) . Every effect source-verified; intervals from the canonical engine. The compatibility key keeps strands apart; a cross-strand pool is refused, not computed.
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 115 of 232 — docs/reviews/iv-iron-hfref-hosp/index.html — Pooled result SUPPRESSED</summary>

Source ref: `38c04411`; lost SHA-256: `3a6e02c51b5f1cf3e290bd9574b61b2dcc71f88ce36f9e3fb55d5f501945d8f5`.

Lost full text:

```text
Pooled result SUPPRESSED (estimand-incompatible). pooled effect SUPPRESSED: the trials mix incompatible estimand classes (HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO) — these effect measures are not one quantity without an explicit, source-backed conversion, so no pooled effect, CI, heterogeneity or sensitivity is valid. The per-trial estimates are shown; pool each coherent strand separately. Estimand classes: HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO; k = 2 trials, shown individually below, not pooled. Refusal is reversible and auditable — reason code INCOMPATIBLE_ESTIMANDS ; had these classes been pooled anyway the (INVALID) result would have been 0.61 (0.01–51.59) — shown only so the refusal is inspectable, never as a usable number.
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `90253e8c344aabbf92aecd9cae73561570c98c1c78294d1f2792f758a7be53b0`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 1 [PMID 25176939]. Set aside on P5 (family eligibility) 1: PMID 40159390 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 116 of 232 — docs/reviews/iv-iron-hfref-hosp/index.html — Parser-confirmed contrast disclosure</summary>

Source ref: `38c04411`; lost SHA-256: `08a88d380770ccaa450c7181aa6b6b6cd8b6db6fa4d51e5cd778795560e4f6fc`.

Lost full text:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 2 of 2 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 25176939 parser-confirmed contrast ferinject (ferric carboxymaltose) 40159390 parser-confirmed contrast iron; saline
```

Candidate 1 of 1; SHA-256 `d786f30773afef549ed54b376393dbcf06e2772b4a5a7553325fa8f75e059cb5`:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 1 of 1 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 25176939 parser-confirmed contrast ferinject (ferric carboxymaltose)
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 117 of 232 — docs/reviews/iv-iron-hfref-hosp/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `56f7c026e5619fda27a0e3987f9b0f0b19d08ee2c092814a580b5fa807e1de4f`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 5 of 6 known (3 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 25176939 industry — full text full text : </ext-link></p></sec><sec id="s6"><title>Funding</title><p>This work was supported by Vifor Pharma Ltd., Glattbrugg, Switzerland.</p><p><bold>Conflict of interest:</bold> P.P. received honoraria from Vifor Pharma Ltd. as member of the CONFIRM-HF Steering Committee, is a consultant and has received honoraria for speaking from Vifor Pharma Ltd. and Amgen, Inc. PMID 28701470 industry — full text full text : </p></sec><sec><title>Sources of Funding</title><p>The study was sponsored by Vifor Pharma, Switzerland. PMID 33197395 industry — abstract abstract : FUNDING: Vifor Pharma. PMID 34080008 industry — full text full text : </p></caption></media></supplementary-material></sec></body><back><ack id="ack1"><title>Acknowledgements</title><p>We are grateful to the patients, their families, and the investigators for their participation in this study; Dr Teba Haboubi, Dr Emanuele Noseda, and the respective study teams for study monitoring and management; and Dr Bridget-Anne Kirwan, Ms Caroline Gombault, Mr Robin Wegmüller (SOCAR Research), and Ms Helen Sims (AXON Communications) who provided editorial assistance with the preparation of the tables and figures, funded by Vifor Pharma.</p><sec><title>Funding</title><p>The AFFIRM-AHF trial was funded by Vifor Pharma.</p><p> <bold>Conflict of interest:</bold> E.A.J. has received research grants and personal fees from Vifor Pharma (co-PI of the AFFIRM trial); personal fees from Bayer, Novartis, Abbott, Boehringer Ingelheim, Pfizer, Servier, AstraZeneca, Berlin Chemie, Cardiac Dimensions, Fresenius, and Gedeon Richter. PMID 37632463 industry — abstract abstract : (Funded by American Regent, a Daiichi Sankyo Group company; HEART-FID ClinicalTrials.gov number, NCT03037931.). PMID 36347265 public/non-profit — abstract abstract : FUNDING: British Heart Foundation and Pharmacosmos. PMID 40159390 not stated (full text scanned) — full text full text : PMID 18191732 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 19920054 not stated (abstract only - full text not retrieved) — abstract abstract :
```

Candidate 1 of 1; SHA-256 `042957ed7c4cfac7a065ba8f51ad4ef6a9bd9b4b68dc60a60210074fc8684a9f`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 5 of 6 known (3 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 25176939 industry — full text full text : </ext-link></p></sec><sec id="s6"><title>Funding</title><p>This work was supported by Vifor Pharma Ltd., Glattbrugg, Switzerland.</p><p><bold>Conflict of interest:</bold> P.P. received honoraria from Vifor Pharma Ltd. as member of the CONFIRM-HF Steering Committee, is a consultant and has received honoraria for speaking from Vifor Pharma Ltd. and Amgen, Inc. PMID 28701470 industry — full text full text : </p></sec><sec><title>Sources of Funding</title><p>The study was sponsored by Vifor Pharma, Switzerland. PMID 33197395 industry — abstract abstract : FUNDING: Vifor Pharma. PMID 34080008 industry — full text full text : </p></caption></media></supplementary-material></sec></body><back><ack id="ack1"><title>Acknowledgements</title><p>We are grateful to the patients, their families, and the investigators for their participation in this study; Dr Teba Haboubi, Dr Emanuele Noseda, and the respective study teams for study monitoring and management; and Dr Bridget-Anne Kirwan, Ms Caroline Gombault, Mr Robin Wegmüller (SOCAR Research), and Ms Helen Sims (AXON Communications) who provided editorial assistance with the preparation of the tables and figures, funded by Vifor Pharma.</p><sec><title>Funding</title><p>The AFFIRM-AHF trial was funded by Vifor Pharma.</p><p> <bold>Conflict of interest:</bold> E.A.J. has received research grants and personal fees from Vifor Pharma (co-PI of the AFFIRM trial); personal fees from Bayer, Novartis, Abbott, Boehringer Ingelheim, Pfizer, Servier, AstraZeneca, Berlin Chemie, Cardiac Dimensions, Fresenius, and Gedeon Richter. PMID 37632463 industry — abstract abstract : (Funded by American Regent, a Daiichi Sankyo Group company; HEART-FID ClinicalTrials.gov number, NCT03037931.). PMID 36347265 public/non-profit — abstract abstract : FUNDING: British Heart Foundation and Pharmacosmos. PMID 18191732 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 19920054 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 40159390 not stated (full text scanned) — full text full text :
```

</details>

<details><summary>Pair 118 of 232 — docs/reviews/iv-iron-hfref-hosp/index.html — Does the result survive dropping the tri</summary>

Source ref: `38c04411`; lost SHA-256: `b9a5b7a31a1a4767d89870f7ffb31059c7bd95c7903dd7cdc7bccb986fcfeac1`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? Not computed (PRIMARY_POOL_SUPPRESSED_INCOMPATIBLE): the primary pool is SUPPRESSED as incompatible estimands; re-pooling incompatible estimands by risk-of-bias stratum would be as invalid as the primary pool itself (declared scales: INCOMPATIBLE (HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO)). The per-trial rows and their risk-of-bias ratings are shown above; the omission is recorded in the review object as rob_sensitivity_omitted , not left silent.
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `90253e8c344aabbf92aecd9cae73561570c98c1c78294d1f2792f758a7be53b0`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 1 [PMID 25176939]. Set aside on P5 (family eligibility) 1: PMID 40159390 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 119 of 232 — docs/reviews/iv-iron-hfref-hosp/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `406d0d6214d0570fa04fc66cd501970e84dbc8bf7637fe8fed29be976c905aa0`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. the primary pool mixes INCOMPATIBLE estimand classes (HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO); an overall certainty cannot be produced from an incoherent effect object — the domain signals are shown, the overall is suppressed until the estimand is made coherent (harmonise the measure or split the outcome) Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (9 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision NOT_ASSESSABLE (NOT ASSESSED) 95% CI [None, None]; missing/insufficient: valid confidence interval; supported effect scale; clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) not auto-rated (human judgement) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) missing/invalid registry census inputs: enumerated, ongoing_or_recent, ghost_upper_bound, positive completed-trial denominator
```

Candidate 1 of 1; SHA-256 `452314efd38ed7f5aa5214317061058f4ea3829abb53ad73b9aeb30eddaa91bc`:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (9 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.19, 0.82]; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) missing/invalid registry census inputs: enumerated, ongoing_or_recent, ghost_upper_bound, positive completed-trial denominator
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `90253e8c344aabbf92aecd9cae73561570c98c1c78294d1f2792f758a7be53b0`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 1 [PMID 25176939]. Set aside on P5 (family eligibility) 1: PMID 40159390 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 120 of 232 — docs/reviews/iv-iron-hfref-hosp/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `4429a1130a26e3d890956b1049a1307ada42cc13bb0211ce7d39890df1960a18`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: a trial identified as eligible under the registered PICO is not pooled (Toblli 2007, IRON-HF) — the pooled result and completeness claim cannot be current screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: 33197395, 36347265, 37632463, 34080008, 28701470, 19920054, and 1 more; the completeness claim cannot be current no outcome produced a pooled claim (Claims checked: 0) — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

Candidate 1 of 1; SHA-256 `fbe403aa6e7530bd99dbcded8a6aba0f0b736b186c514f1b2b245aec6269af2c`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate. See the known-missing sensitivity panel . no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. Toblli 2007: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed IRON-HF: named eligible by an audit, but not admitted on this page (INADMISSIBLE_ON_ADMISSION, no family); not re-pooled; the audit's eligibility claim and the structural screen disagree -- adjudication owed a trial identified as eligible under the registered PICO is not pooled (Toblli 2007, IRON-HF) — the pooled result and completeness claim cannot be current screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT03037931, PMID:34080008, NCT01394562, NCT00520780, NCT00125996; the completeness claim cannot be current
```

</details>

<details><summary>Pair 121 of 232 — docs/reviews/iv-iron-hfref-hosp/index.html — Pooled result SUPPRESSED</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `06fd26217042d4d16e030bb836f29e30203fb4c94b622eb2177b70dcd8d72a94`.

Lost full text:

```text
Pooled result SUPPRESSED (estimand-incompatible). pooled effect SUPPRESSED: the trials mix incompatible estimand classes (HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO) — a recurrent-event/rate ratio and a first-event ratio are not one quantity, so no pooled effect, CI, heterogeneity or sensitivity is valid. The per-trial estimates are shown; pool each coherent strand separately. Estimand classes: HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO; the 2 eligible trials are shown individually in Results, not pooled.
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `90253e8c344aabbf92aecd9cae73561570c98c1c78294d1f2792f758a7be53b0`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 1 [PMID 25176939]. Set aside on P5 (family eligibility) 1: PMID 40159390 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 122 of 232 — docs/reviews/iv-iron-hfref-hosp/index.html — Pooled result SUPPRESSED</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `61fa684e92843fbe047623661c300be695b368dab6ba62da8bcd28bbfa451800`.

Lost full text:

```text
Pooled result SUPPRESSED (estimand-incompatible). pooled effect SUPPRESSED: the trials mix incompatible estimand classes (HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO) — a recurrent-event/rate ratio and a first-event ratio are not one quantity, so no pooled effect, CI, heterogeneity or sensitivity is valid. The per-trial estimates are shown; pool each coherent strand separately. Estimand classes: HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO; k = 2 trials, shown individually below, not pooled. Refusal is reversible and auditable — reason code INCOMPATIBLE_ESTIMANDS ; had these classes been pooled anyway the (INVALID) result would have been 0.61 (0.01–51.59) — shown only so the refusal is inspectable, never as a usable number.
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `90253e8c344aabbf92aecd9cae73561570c98c1c78294d1f2792f758a7be53b0`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 1 [PMID 25176939]. Set aside on P5 (family eligibility) 1: PMID 40159390 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 123 of 232 — docs/reviews/iv-iron-hfref-hosp/index.html — Randomised-contrast disclosure</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `e33d3ad545e807ab7ed52a5479a3bf8255f04c8ae05e898287e51cddca0953aa`.

Lost full text:

```text
Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 2 of 2 pooled trials have a registry-confirmed contrast (the intervention of interest differs across arms). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 25176939 randomised contrast verified ferinject (ferric carboxymaltose) 40159390 randomised contrast verified iron; saline
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 124 of 232 — docs/reviews/iv-iron-hfref-hosp/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `95985cd84fbf919935f5099fffc4c42de010543b74fc4555a113a263a177c7ec`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 0 of 0 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 2 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 40159390 not stated (abstract only — full text not retrieved) abstract only PMID 25176939 not stated (abstract only — full text not retrieved) abstract only
```

Candidate 1 of 1; SHA-256 `042957ed7c4cfac7a065ba8f51ad4ef6a9bd9b4b68dc60a60210074fc8684a9f`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 5 of 6 known (3 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 25176939 industry — full text full text : </ext-link></p></sec><sec id="s6"><title>Funding</title><p>This work was supported by Vifor Pharma Ltd., Glattbrugg, Switzerland.</p><p><bold>Conflict of interest:</bold> P.P. received honoraria from Vifor Pharma Ltd. as member of the CONFIRM-HF Steering Committee, is a consultant and has received honoraria for speaking from Vifor Pharma Ltd. and Amgen, Inc. PMID 28701470 industry — full text full text : </p></sec><sec><title>Sources of Funding</title><p>The study was sponsored by Vifor Pharma, Switzerland. PMID 33197395 industry — abstract abstract : FUNDING: Vifor Pharma. PMID 34080008 industry — full text full text : </p></caption></media></supplementary-material></sec></body><back><ack id="ack1"><title>Acknowledgements</title><p>We are grateful to the patients, their families, and the investigators for their participation in this study; Dr Teba Haboubi, Dr Emanuele Noseda, and the respective study teams for study monitoring and management; and Dr Bridget-Anne Kirwan, Ms Caroline Gombault, Mr Robin Wegmüller (SOCAR Research), and Ms Helen Sims (AXON Communications) who provided editorial assistance with the preparation of the tables and figures, funded by Vifor Pharma.</p><sec><title>Funding</title><p>The AFFIRM-AHF trial was funded by Vifor Pharma.</p><p> <bold>Conflict of interest:</bold> E.A.J. has received research grants and personal fees from Vifor Pharma (co-PI of the AFFIRM trial); personal fees from Bayer, Novartis, Abbott, Boehringer Ingelheim, Pfizer, Servier, AstraZeneca, Berlin Chemie, Cardiac Dimensions, Fresenius, and Gedeon Richter. PMID 37632463 industry — abstract abstract : (Funded by American Regent, a Daiichi Sankyo Group company; HEART-FID ClinicalTrials.gov number, NCT03037931.). PMID 36347265 public/non-profit — abstract abstract : FUNDING: British Heart Foundation and Pharmacosmos. PMID 18191732 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 19920054 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 40159390 not stated (full text scanned) — full text full text :
```

</details>

<details><summary>Pair 125 of 232 — docs/reviews/iv-iron-hfref-hosp/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `19e48f45872f041e87da3e5d30365a431e76d3d07e43ea7a5ab24ab068b59b73`.

Lost full text:

```text
Overall certainty: not rateable. the primary pool mixes INCOMPATIBLE estimand classes (HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO); an overall certainty cannot be produced from an incoherent effect object — the domain signals are shown, the overall is suppressed until the estimand is made coherent (harmonise the measure or split the outcome). The individual domain signals are shown below, but no overall certainty category is emitted — a partial or incoherent evidence object cannot produce one, and ‘provisional’ would soften the language without repairing the logic. Domain Signal Basis Risk of bias −1 1 of 2 assessed trial(s) at 'some concerns' Inconsistency not downgraded tau^2=None Imprecision NOT ASSESSED no confidence interval available Indirectness human judgement not auto-rated (human judgement) Publication bias (registry-based) NOT ASSESSED no registry ghost census available for this topic
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `90253e8c344aabbf92aecd9cae73561570c98c1c78294d1f2792f758a7be53b0`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 1 [PMID 25176939]. Set aside on P5 (family eligibility) 1: PMID 40159390 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 126 of 232 — docs/reviews/iv-iron-hfref-hosp/index.html — No checkable pooled claim</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `4e655fe3ed1a86b2fbbb60e04236c8591d430c63637eab4156e3da1157a1f6ce`.

Lost full text:

```text
No checkable pooled claim (Claims checked: 0). Nothing was pooled on this page, so the canonical-claim contradiction gate has nothing to check here — this is a limitation, not a clean result.
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `90253e8c344aabbf92aecd9cae73561570c98c1c78294d1f2792f758a7be53b0`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 1 [PMID 25176939]. Set aside on P5 (family eligibility) 1: PMID 40159390 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 127 of 232 — docs/reviews/metformin-pcos-ovulation/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `3578163b4015a9de777894bb2dfce16440790c50abe394972d79ecdc14a33d0e`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:22419702, PMID:19552097, PMID:11994052, PMID:11473953; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `580ce00c65aad59e50558e2cfbbfa48613824665204ec34833f0d65c6bc04103`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:22419702, PMID:19552097, PMID:19522426, PMID:16769748, PMID:11994052, PMID:11473953, and 1 more; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 128 of 232 — docs/reviews/metformin-pcos-ovulation/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `da5d8c1bebbd07a55a7855c1247a54176f7df8a6b62e553b70c1d1118d2ab968`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 1 of 1 known (6 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 16769748 industry — full text full text : </p></fn><fn><p>Funding: Merck Santé France provided the metformin and placebo. PMID 19522426 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 11172832 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 11473953 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 11994052 not stated (full text scanned) — full text full text : PMID 19552097 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 22419702 not stated (abstract only - full text not retrieved) — abstract abstract :
```

Candidate 1 of 1; SHA-256 `99f34ee0a00d5760499a1c411606f89e43301fe83eb5f4494251197788334497`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 1 of 1 known (6 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 16769748 industry — full text full text : </p></fn><fn><p>Funding: Merck Santé France provided the metformin and placebo. PMID 11172832 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 11473953 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 11994052 not stated (full text scanned) — full text full text : PMID 19522426 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 19552097 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 22419702 not stated (abstract only - full text not retrieved) — abstract abstract :
```

</details>

<details><summary>Pair 129 of 232 — docs/reviews/metformin-pcos-ovulation/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `5ebf3921cd1d00d113071fff60d81dffc7ae147d66bb6ce82602e541f414570f`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `089a6aef316a01924e57b8716b03493854a16856ef82a4fee08edc34e0a36749`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 3: PMID 19522426 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 16769748 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE); PMID 11172832 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 130 of 232 — docs/reviews/metformin-pcos-ovulation/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `336da4bb397eaaec4cd68f0bf11d2b4a760f0aa73b061760c31601b79d2d2e28`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision ASSESSED: −1 95% CI [0.0922, 46.6008]; GRADE default appreciable-effect thresholds 0.75/1.25; no topic threshold registered; spans clinical decisions or inadequate information -> imprecise; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) missing/invalid registry census inputs: enumerated, ongoing_or_recent, ghost_upper_bound, positive completed-trial denominator
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `089a6aef316a01924e57b8716b03493854a16856ef82a4fee08edc34e0a36749`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 3: PMID 19522426 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 16769748 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE); PMID 11172832 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 131 of 232 — docs/reviews/metformin-pcos-ovulation/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `b2070d2574fe0876cc517b1de106056ca6efb46bb95750887f632b34a2154ccb`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: 22419702, 20925997, 19692630, 16827766, 11994052, 11473953; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `580ce00c65aad59e50558e2cfbbfa48613824665204ec34833f0d65c6bc04103`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:22419702, PMID:19552097, PMID:19522426, PMID:16769748, PMID:11994052, PMID:11473953, and 1 more; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 132 of 232 — docs/reviews/metformin-pcos-ovulation/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `16264cc27213b813e1aeafd53e66948603ccb01474997893fe6c53f1a37a022e`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 0 of 0 known (3 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 3 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 19522426 not stated (abstract only — full text not retrieved) abstract only PMID 16769748 not stated (abstract only — full text not retrieved) abstract only PMID 11172832 not stated (abstract only — full text not retrieved) abstract only
```

Candidate 1 of 1; SHA-256 `99f34ee0a00d5760499a1c411606f89e43301fe83eb5f4494251197788334497`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 1 of 1 known (6 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 16769748 industry — full text full text : </p></fn><fn><p>Funding: Merck Santé France provided the metformin and placebo. PMID 11172832 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 11473953 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 11994052 not stated (full text scanned) — full text full text : PMID 19522426 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 19552097 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 22419702 not stated (abstract only - full text not retrieved) — abstract abstract :
```

</details>

<details><summary>Pair 133 of 232 — docs/reviews/metformin-pcos-ovulation/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `72db58add18abd2662f0e8b4798ff2ee589a750ad3328d91563734f69747b695`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 3 of 3 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=3, OR 2.0733 [0.0922, 46.6008] Low risk of bias only k=2, OR 4.3142 [0.0033, 5557.8501]
```

Candidate 1 of 1; SHA-256 `f7f6eb8ef26dd186392711f9e4a855ef2943d9b059b983abfcf39544728ced99`:

```text
Does the result survive dropping the trials that are not low risk of bias? Not computed (PRIMARY_ABSENT): the primary outcome has no pooled result (present = False). The per-trial rows and their risk-of-bias ratings are shown above; the omission is recorded in the review object as rob_sensitivity_omitted , not left silent.
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `089a6aef316a01924e57b8716b03493854a16856ef82a4fee08edc34e0a36749`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 3: PMID 19522426 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 16769748 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE); PMID 11172832 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 134 of 232 — docs/reviews/metformin-pcos-ovulation/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `8e8301343df98222cfe40b761ee7ec58afc1206c5534fee72f5d709f163834e3`.

Lost full text:

```text
Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 3 assessed trial(s) at high risk; fewer than half at 'some concerns' Inconsistency −1 tau^2=1.15872; prediction interval [0.0078, 549.6907] is >=2x the CI width -> real heterogeneity Imprecision −1 95% CI [0.0922, 46.6008]; crosses the null AND is compatible with an appreciable benefit (<=0.75) and an appreciable harm (>=1.25) -> imprecise (the estimate is consistent with both no effect and an appreciable effect) Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED no registry ghost census available for this topic
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `089a6aef316a01924e57b8716b03493854a16856ef82a4fee08edc34e0a36749`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 3: PMID 19522426 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 16769748 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE); PMID 11172832 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 135 of 232 — docs/reviews/noac-vs-warfarin-af-stroke/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `61921fa166c4df0013f8f12918cdccbfc468cf5a6641a66b9c523c92a19288a3`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (PMID_ENUMERATION_explicit): search.retrieval.enumeration_only=true; no discovery-capable concept source ran screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT00504556, NCT00806624, NCT00829933; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `16ef3c199efeb7d2e9019713fe5f050425cb34f66ccc820e4dd4f2d3afe64d3a`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (PMID_ENUMERATION_explicit): search.retrieval.enumeration_only=true; no discovery-capable concept source ran screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT00403767, NCT00262600, NCT00781391, NCT00412984, NCT00504556, NCT00806624, and 1 more; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 136 of 232 — docs/reviews/noac-vs-warfarin-af-stroke/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `aa20807f2816da64b56f9c4a03936a3dd5b80b730d977564d31aeca392b4c2d6`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 3 of 3 known (4 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 21830957 industry — abstract abstract : (Funded by Johnson & Johnson and Bayer; ROCKET AF ClinicalTrials.gov number, NCT00403767.). PMID 24251359 industry — abstract abstract : (Funded by Daiichi Sankyo Pharma Development; ENGAGE AF-TIMI 48 ClinicalTrials.gov number, NCT00781391.). PMID 21870978 industry — abstract abstract : (Funded by Bristol-Myers Squibb and Pfizer; ARISTOTLE ClinicalTrials.gov number, NCT00412984.). PMID 19717844 not stated (abstract only - full text not retrieved) — abstract abstract : NCT00504556 source not retrieved — : NCT00806624 source not retrieved — : NCT00829933 source not retrieved — :
```

Candidate 1 of 1; SHA-256 `80d9f34ad753394fd3bc395461f58ff2ebe1fc4b2738c56e847c6a58c006bef7`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 3 of 3 known (4 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 21830957 industry — abstract abstract : (Funded by Johnson & Johnson and Bayer; ROCKET AF ClinicalTrials.gov number, NCT00403767.). PMID 21870978 industry — abstract abstract : (Funded by Bristol-Myers Squibb and Pfizer; ARISTOTLE ClinicalTrials.gov number, NCT00412984.). PMID 24251359 industry — abstract abstract : (Funded by Daiichi Sankyo Pharma Development; ENGAGE AF-TIMI 48 ClinicalTrials.gov number, NCT00781391.). PMID 19717844 not stated (abstract only - full text not retrieved) — abstract abstract : NCT00504556 source not retrieved — : NCT00806624 source not retrieved — : NCT00829933 source not retrieved — :
```

</details>

<details><summary>Pair 137 of 232 — docs/reviews/noac-vs-warfarin-af-stroke/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `6eb54f34bd0ecab4eab0444b6b50e9486de86f533a5f112f21e44bb7d2c6e4af`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=4 of 4)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `5c467d3af04a2d46fb684247ffb791f0afff3bb5aa10e5b4a549c27cb156ae61`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 4: PMID 21830957 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 19717844 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 24251359 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 21870978 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 138 of 232 — docs/reviews/noac-vs-warfarin-af-stroke/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `6f59571f3a4b3a883bf6d3d4e3eee61a732aea034146000261247ac246df1134`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.6611, 0.985]; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (83 of ~227 completed unpublished, 37%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `5c467d3af04a2d46fb684247ffb791f0afff3bb5aa10e5b4a549c27cb156ae61`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 4: PMID 21830957 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 19717844 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 24251359 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 21870978 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 139 of 232 — docs/reviews/noac-vs-warfarin-af-stroke/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `bc9d516edca0700eb472fee2cf9030ae8a03fa19908bb5394750757912d6745e`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT00504556, ORGANON · NCT02935855, NCT00806624, NCT05006287, NCT00829933; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `16ef3c199efeb7d2e9019713fe5f050425cb34f66ccc820e4dd4f2d3afe64d3a`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (PMID_ENUMERATION_explicit): search.retrieval.enumeration_only=true; no discovery-capable concept source ran screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT00403767, NCT00262600, NCT00781391, NCT00412984, NCT00504556, NCT00806624, and 1 more; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 140 of 232 — docs/reviews/noac-vs-warfarin-af-stroke/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `e265d763c956988c33d33de18e544f09e182e98528af44246fb987cc65a5c2dc`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 3 of 3 known (1 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 1 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 21830957 industry abstract only oxaban group. (Funded by Johnson & Johnson and Bayer; ROCKET AF ClinicalTrials.gov number, NCT00403767.). PMID 24251359 industry abstract only cular causes. (Funded by Daiichi Sankyo Pharma Development; ENGAGE AF-TIMI 48 ClinicalTrials.gov number, NCT00781391.). PMID 21870978 industry abstract only er mortality. (Funded by Bristol-Myers Squibb and Pfizer; ARISTOTLE ClinicalTrials.gov number, NCT00412984.). PMID 19717844 not stated (abstract only — full text not retrieved) abstract only
```

Candidate 1 of 1; SHA-256 `80d9f34ad753394fd3bc395461f58ff2ebe1fc4b2738c56e847c6a58c006bef7`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 3 of 3 known (4 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 21830957 industry — abstract abstract : (Funded by Johnson & Johnson and Bayer; ROCKET AF ClinicalTrials.gov number, NCT00403767.). PMID 21870978 industry — abstract abstract : (Funded by Bristol-Myers Squibb and Pfizer; ARISTOTLE ClinicalTrials.gov number, NCT00412984.). PMID 24251359 industry — abstract abstract : (Funded by Daiichi Sankyo Pharma Development; ENGAGE AF-TIMI 48 ClinicalTrials.gov number, NCT00781391.). PMID 19717844 not stated (abstract only - full text not retrieved) — abstract abstract : NCT00504556 source not retrieved — : NCT00806624 source not retrieved — : NCT00829933 source not retrieved — :
```

</details>

<details><summary>Pair 141 of 232 — docs/reviews/noac-vs-warfarin-af-stroke/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `496a7c240788f4917387ccc389f17c25551a2842b80391e40c0a7353dfcd57b3`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 4 of 4 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=4, HR 0.8069 [0.6611, 0.985] Low risk of bias only k=4, HR 0.8069 [0.6611, 0.985] (fewer trials than the full pool — see coverage)
```

Candidate 1 of 1; SHA-256 `f7f6eb8ef26dd186392711f9e4a855ef2943d9b059b983abfcf39544728ced99`:

```text
Does the result survive dropping the trials that are not low risk of bias? Not computed (PRIMARY_ABSENT): the primary outcome has no pooled result (present = False). The per-trial rows and their risk-of-bias ratings are shown above; the omission is recorded in the review object as rob_sensitivity_omitted , not left silent.
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `5c467d3af04a2d46fb684247ffb791f0afff3bb5aa10e5b4a549c27cb156ae61`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 4: PMID 21830957 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 19717844 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 24251359 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 21870978 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 142 of 232 — docs/reviews/noac-vs-warfarin-af-stroke/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `baea49ebb9e814194adc1b2736d663afc71255af1fa6cccb8d6d0d1589f72307`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capped below high because D3 (missing outcome data), a required risk-of-bias domain, is NOT ASSESSED for any pooled trial (no outcome-missingness source) — high certainty cannot be certified on a structurally-incomplete bias assessment. PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 4 assessed trial(s) at high risk; fewer than half at 'some concerns' Inconsistency not downgraded tau^2=0.00741; prediction interval not markedly wider than the CI Imprecision not downgraded 95% CI [0.6611, 0.985]; excludes the null with a reasonably tight interval -> precise Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED registry census (83 of ~227 completed unpublished, 37%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `5c467d3af04a2d46fb684247ffb791f0afff3bb5aa10e5b4a549c27cb156ae61`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 4: PMID 21830957 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 19717844 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 24251359 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 21870978 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 143 of 232 — docs/reviews/omega3-cardiovascular-events/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `a4f7285d4fec5a171b69a89b531c9dc0c49e8e27008db32627a29e8b0d5e0d5c`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:23839902, NCT00317707, PMID:23351824, NCT00069784, PMID:20146881, NCT00336336, and 8 more; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `0b34f67c72200eef1a482188c16d118e48de6ed57e602752995e95157a67e6fd`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT02104817, NCT01492361, PMID:23839902, NCT00317707, PMID:23351824, NCT00069784, and 12 more; the completeness claim cannot be current
```

</details>

<details><summary>Pair 144 of 232 — docs/reviews/omega3-cardiovascular-events/index.html — Unit-of-analysis/design caveat</summary>

Source ref: `38c04411`; lost SHA-256: `42d8893ff182dda200547b6067fcd4888de63b57e3851a998819a503a5248256`.

Lost full text:

```text
Unit-of-analysis/design caveat (disclosed, not silently adjusted). 3 pooled trial(s) are individual-randomized factorial designs: PMID 30415637 (factorial); PMID 20929341 (factorial); PMID 21115589 (factorial). These are disclosed as marginal factorial contrasts; when a source-reported adjusted marginal estimate with acceptable interaction evidence is available, the design key records that estimator and labels it rather than using a raw reconstruction silently. This is a stated limitation and design-key disclosure, not silent simple-parallel pooling.
```

Candidate 1 of 1; SHA-256 `98cc792df28871869dad5c6add06e42d9d2202f4ab5736c62cfa6a6a4f21bf40`:

```text
Unit-of-analysis/design caveat (disclosed, not silently adjusted). 1 pooled trial(s) are individual-randomized factorial designs: PMID 30415637 (factorial). These are disclosed as marginal factorial contrasts; when a source-reported adjusted marginal estimate with acceptable interaction evidence is available, the design key records that estimator and labels it rather than using a raw reconstruction silently. This is a stated limitation and design-key disclosure, not silent simple-parallel pooling.
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `6b42a03892373eab9da4591d3864425f5146be5d99e91370e27d578965b2557a`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 4: PMID 33190147 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 30415628 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 20929341 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 21115589 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 145 of 232 — docs/reviews/omega3-cardiovascular-events/index.html — UNRENDERABLE stale contrast block</summary>

Source ref: `38c04411`; lost SHA-256: `06dc018c1cd484d1e2f06ac24b5e3dd5fd78059ba68d01cd5465e72040765c4d`.

Lost full text:

```text
UNRENDERABLE stale contrast block. cached arm-contrast membership named trials not in the current consumed pool; current pooled trial ids: 20929341, 21115589, 30415628, 30415637, 33190147; suppressed stale ids: 22686415, 30146932.
```

Candidate 1 of 1; SHA-256 `fa22e4209e1278299323af00ff697e1423756774b09eed358164f3753b9c2c65`:

```text
UNRENDERABLE stale contrast block. cached arm-contrast membership named trials not in the current consumed pool; current pooled trial ids: 30415637; suppressed stale ids: 20929341, 21115589, 22686415, 30146932, 30415628, 33190147.
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 146 of 232 — docs/reviews/omega3-cardiovascular-events/index.html — Parser-confirmed contrast disclosure</summary>

Source ref: `38c04411`; lost SHA-256: `e92e1ed85db8461f19d39bbb7b2ef80d55a174c9e68e4218842b7b080ae9e310`.

Lost full text:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 2 of 5 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 20929341 contrast unverified (no arm-level contrast coded) — 30415628 contrast unverified (registry class label / dev code) amr101 30415637 parser-confirmed contrast omega-3 fatty acids (fish oil); vitamin d3 33190147 parser-confirmed contrast corn oil control; epanova® (omega-3 carboxylic acids) 21115589 unverified_no_registry_match —
```

Candidate 1 of 1; SHA-256 `1c2ac405b7acac7b0d70826ba447f013b435e2c536c5f574a4029c8ef6bcda3e`:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 1 of 1 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 30415637 parser-confirmed contrast omega-3 fatty acids (fish oil); vitamin d3
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 147 of 232 — docs/reviews/omega3-cardiovascular-events/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `fc067b4dd019cf86cd1a9ffaf653bf5851ef76f34f2be94cffb2de96c0af61b4`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 4 of 7 known (13 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 30415637 industry — full text full text : The ancillary studies are supported by grants from multiple Institutes, including the National Heart, Lung and Blood Institute; the National Institute of Diabetes and Digestive and Kidney Diseases; the National Institute on Aging; the National Institute of Arthritis and Musculoskeletal and Skin Diseases; the National Institute of Mental Health; and others.</p><p id="P32">Pharmavite LLC of Northridge, California (vitamin D) and Pronova BioPharma of Norway PMID 30415628 industry — abstract abstract : (Funded by Amarin Pharma; REDUCE-IT ClinicalTrials.gov number, NCT01492361 .). PMID 22686415 industry — abstract abstract : (Funded by Sanofi; ORIGIN ClinicalTrials.gov number, NCT00069784.). PMID 21115589 mixed — full text full text : </p></fn><fn fn-type="financial-disclosure"><p>Funding: The SU.FOL.OM3 trial was supported by the French Ministry of Research (R02010JJ), Ministry of Health (DGS), Sodexo, Candia, Unilever, Danone, Roche Laboratory, Merck EPROVA GS, and Pierre Fabre Laboratory.</p></fn><fn fn-type="conflict"><p>Competing interests: All authors have completed the Unified Competing Interest form at <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" ext-link-type="uri" xlink:href= PMID 20929341 public/non-profit — abstract abstract : (Funded by the Netherlands Heart Foundation and others; ClinicalTrials.gov number, NCT00127452.). PMID 30146932 public/non-profit — abstract abstract : (Funded by the British Heart Foundation and others; Current Controlled Trials number, ISRCTN60635500 ; ClinicalTrials.gov number, NCT00135226 .). PMID 38199870 public/non-profit — full text full text : </p></sec><sec id="sec0070"><title>Funding</title><p id="par0125">The study was funded by the Seventh Framework Program of the <funding-source id="gs0005"><institution-wrap><institution-id institution-id-type="doi">10.13039/501100000780</institution-id><institution>European Commission</institution></institution-wrap></funding-source>(grant agreement 278588; Principal Investigator: Heike A. PMID 33190147 not stated (full text scanned) — full text full text : PMID 11451717 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 18757090 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 20146881 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 20389249 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 21060071 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 23351824 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 23656645 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 23839902 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 38184150 not stated (abstract only - full text not retrieved) — abstract abstract : NCT01048502 source not retrieved — : NCT01841944 source not retrieved — : NCT06720662 source not retrieved — :
```

Candidate 1 of 1; SHA-256 `50f2fb8c88308536457cb3e77792530917bb2953291dafbd17fa22435d2d64b8`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 4 of 7 known (13 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 30415637 industry — full text full text : The ancillary studies are supported by grants from multiple Institutes, including the National Heart, Lung and Blood Institute; the National Institute of Diabetes and Digestive and Kidney Diseases; the National Institute on Aging; the National Institute of Arthritis and Musculoskeletal and Skin Diseases; the National Institute of Mental Health; and others.</p><p id="P32">Pharmavite LLC of Northridge, California (vitamin D) and Pronova BioPharma of Norway PMID 22686415 industry — abstract abstract : (Funded by Sanofi; ORIGIN ClinicalTrials.gov number, NCT00069784.). PMID 30415628 industry — abstract abstract : (Funded by Amarin Pharma; REDUCE-IT ClinicalTrials.gov number, NCT01492361 .). PMID 21115589 mixed — full text full text : </p></fn><fn fn-type="financial-disclosure"><p>Funding: The SU.FOL.OM3 trial was supported by the French Ministry of Research (R02010JJ), Ministry of Health (DGS), Sodexo, Candia, Unilever, Danone, Roche Laboratory, Merck EPROVA GS, and Pierre Fabre Laboratory.</p></fn><fn fn-type="conflict"><p>Competing interests: All authors have completed the Unified Competing Interest form at <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" ext-link-type="uri" xlink:href= PMID 30146932 public/non-profit — abstract abstract : (Funded by the British Heart Foundation and others; Current Controlled Trials number, ISRCTN60635500 ; ClinicalTrials.gov number, NCT00135226 .). PMID 20929341 public/non-profit — abstract abstract : (Funded by the Netherlands Heart Foundation and others; ClinicalTrials.gov number, NCT00127452.). PMID 38199870 public/non-profit — full text full text : </p></sec><sec id="sec0070"><title>Funding</title><p id="par0125">The study was funded by the Seventh Framework Program of the <funding-source id="gs0005"><institution-wrap><institution-id institution-id-type="doi">10.13039/501100000780</institution-id><institution>European Commission</institution></institution-wrap></funding-source>(grant agreement 278588; Principal Investigator: Heike A. PMID 11451717 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 18757090 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 20146881 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 20389249 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 21060071 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 23351824 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 23656645 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 23839902 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 33190147 not stated (full text scanned) — full text full text : PMID 38184150 not stated (abstract only - full text not retrieved) — abstract abstract : NCT01048502 source not retrieved — : NCT01841944 source not retrieved — : NCT06720662 source not retrieved — :
```

</details>

<details><summary>Pair 148 of 232 — docs/reviews/omega3-cardiovascular-events/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `5ebf3921cd1d00d113071fff60d81dffc7ae147d66bb6ce82602e541f414570f`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed
```

Candidate 1 of 1; SHA-256 `907e96459f0676ed291eafe578d7ed148d3184fa1b8274d074077cc53eadf371`:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=1 of 1)
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `6b42a03892373eab9da4591d3864425f5146be5d99e91370e27d578965b2557a`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 4: PMID 33190147 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 30415628 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 20929341 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 21115589 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 149 of 232 — docs/reviews/omega3-cardiovascular-events/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `dd4b084cd744c28dac317617364f18b936966fe22d06a6e26076e9f36b4e7c25`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (15 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.7726, 1.1364]; within GRADE default thresholds 0.75/1.25; no mechanical downgrade; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (144 of ~440 completed unpublished, 33%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

Candidate 1 of 1; SHA-256 `f63853db70db0b1c44180c166b860bb60ca9b7a236ad5d95354d6c527a885dcd`:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (19 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.8, 1.06]; within GRADE default thresholds 0.75/1.25; no mechanical downgrade; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (144 of ~440 completed unpublished, 33%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `6b42a03892373eab9da4591d3864425f5146be5d99e91370e27d578965b2557a`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 4: PMID 33190147 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 30415628 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 20929341 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 21115589 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 150 of 232 — docs/reviews/omega3-cardiovascular-events/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `f654ce73d6605a5ed5802fa1c03a703e47110d3e83e41c87cc5bac4e01b06fdb`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: 23839902, 23656645, 23351824, 20952767, 20146881, 18757090, and 9 more; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `0b34f67c72200eef1a482188c16d118e48de6ed57e602752995e95157a67e6fd`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT02104817, NCT01492361, PMID:23839902, NCT00317707, PMID:23351824, NCT00069784, and 12 more; the completeness claim cannot be current
```

</details>

<details><summary>Pair 151 of 232 — docs/reviews/omega3-cardiovascular-events/index.html — Randomised-contrast disclosure</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `4bfa9e524f3089c4c5cd06a844cdae1489c43898c25d569c14d17005e0dc3af1`.

Lost full text:

```text
Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 4 of 7 pooled trials have a registry-confirmed contrast (the intervention of interest differs across arms). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 20929341 contrast unverified (no arm-level contrast coded) — 30415628 contrast unverified (registry class label / dev code) amr101 22686415 randomised contrast verified insulin glargine (hoe901); omega-3 polyunsaturated fatty acids (pufa); reusable pen device for insulin injection 30146932 randomised contrast verified aspirin; omega-3 ethyl esters 30415637 randomised contrast verified omega-3 fatty acids (fish oil); vitamin d3 33190147 randomised contrast verified corn oil control; epanova® (omega-3 carboxylic acids) 21115589 unverified_no_registry_match —
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 152 of 232 — docs/reviews/omega3-cardiovascular-events/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `fc29991097b4dc217d3f023445f76cbffa5c22b6bf494127a23f390975d8369c`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 2 of 5 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 2 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 30415628 industry abstract only ived placebo. (Funded by Amarin Pharma; REDUCE-IT ClinicalTrials.gov number, NCT01492361 .). PMID 22686415 industry abstract only cular events. (Funded by Sanofi; ORIGIN ClinicalTrials.gov number, NCT00069784.). PMID 30415637 public/non-profit abstract only than placebo. (Funded by the National Institutes of Health and others; VITAL ClinicalTrials.gov number, NCT01169259 .). PMID 30146932 public/non-profit abstract only eive placebo. (Funded by the British Heart Foundation and others; Current Controlled Trials number, ISRCTN60635500 ; ClinicalTrials.gov number, NCT00135226 .). PMID 20929341 public/non-profit abstract only ying therapy. (Funded by the Netherlands Heart Foundation and others; ClinicalTrials.gov number, NCT00127452.). PMID 33190147 not stated (abstract only — full text not retrieved) abstract only PMID 21115589 not stated (abstract only — full text not retrieved) abstract only
```

Candidate 1 of 1; SHA-256 `50f2fb8c88308536457cb3e77792530917bb2953291dafbd17fa22435d2d64b8`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 4 of 7 known (13 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 30415637 industry — full text full text : The ancillary studies are supported by grants from multiple Institutes, including the National Heart, Lung and Blood Institute; the National Institute of Diabetes and Digestive and Kidney Diseases; the National Institute on Aging; the National Institute of Arthritis and Musculoskeletal and Skin Diseases; the National Institute of Mental Health; and others.</p><p id="P32">Pharmavite LLC of Northridge, California (vitamin D) and Pronova BioPharma of Norway PMID 22686415 industry — abstract abstract : (Funded by Sanofi; ORIGIN ClinicalTrials.gov number, NCT00069784.). PMID 30415628 industry — abstract abstract : (Funded by Amarin Pharma; REDUCE-IT ClinicalTrials.gov number, NCT01492361 .). PMID 21115589 mixed — full text full text : </p></fn><fn fn-type="financial-disclosure"><p>Funding: The SU.FOL.OM3 trial was supported by the French Ministry of Research (R02010JJ), Ministry of Health (DGS), Sodexo, Candia, Unilever, Danone, Roche Laboratory, Merck EPROVA GS, and Pierre Fabre Laboratory.</p></fn><fn fn-type="conflict"><p>Competing interests: All authors have completed the Unified Competing Interest form at <ext-link xmlns:xlink="http://www.w3.org/1999/xlink" ext-link-type="uri" xlink:href= PMID 30146932 public/non-profit — abstract abstract : (Funded by the British Heart Foundation and others; Current Controlled Trials number, ISRCTN60635500 ; ClinicalTrials.gov number, NCT00135226 .). PMID 20929341 public/non-profit — abstract abstract : (Funded by the Netherlands Heart Foundation and others; ClinicalTrials.gov number, NCT00127452.). PMID 38199870 public/non-profit — full text full text : </p></sec><sec id="sec0070"><title>Funding</title><p id="par0125">The study was funded by the Seventh Framework Program of the <funding-source id="gs0005"><institution-wrap><institution-id institution-id-type="doi">10.13039/501100000780</institution-id><institution>European Commission</institution></institution-wrap></funding-source>(grant agreement 278588; Principal Investigator: Heike A. PMID 11451717 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 18757090 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 20146881 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 20389249 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 21060071 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 23351824 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 23656645 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 23839902 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 33190147 not stated (full text scanned) — full text full text : PMID 38184150 not stated (abstract only - full text not retrieved) — abstract abstract : NCT01048502 source not retrieved — : NCT01841944 source not retrieved — : NCT06720662 source not retrieved — :
```

</details>

<details><summary>Pair 153 of 232 — docs/reviews/omega3-cardiovascular-events/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `6398132dae3a1a7108a74c25d54c80f3a739512df47772bc155502751c36b41d`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 7 of 7 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=7, RR 0.943 [0.846, 1.051] Low risk of bias only k=5, RR 0.9775 [0.9018, 1.0595]
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `6b42a03892373eab9da4591d3864425f5146be5d99e91370e27d578965b2557a`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 4: PMID 33190147 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 30415628 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 20929341 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 21115589 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 154 of 232 — docs/reviews/omega3-cardiovascular-events/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `c77ef0e830e5d74310099c90ef651caad9e1ee2aff8dd7d8de391e991afc6962`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 7 assessed trial(s) at high risk; fewer than half at 'some concerns' Inconsistency −1 tau^2=0.00925; prediction interval [0.7277, 1.2218] is >=2x the CI width -> real heterogeneity Imprecision not downgraded 95% CI [0.846, 1.051]; crosses the null but excludes an appreciable effect on BOTH sides (within 0.75-1.25) -> precise about the absence of an appreciable effect Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED registry census (144 of ~440 completed unpublished, 33%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `6b42a03892373eab9da4591d3864425f5146be5d99e91370e27d578965b2557a`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 4: PMID 33190147 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 30415628 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 20929341 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 21115589 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 155 of 232 — docs/reviews/pcsk9-mace/index.html — Registered pooled CI REFUSED at k=2</summary>

Source ref: `38c04411`; lost SHA-256: `abe7679264593e3bc2f7f1daf7ccfdf7133247cf2c37fcc83a6f4fbb9461b1d4`.

Lost full text:

```text
Registered pooled CI REFUSED at k=2. Registered PM/HKSJ uses t(1)=12.71 at k=2; the interval is not served as a pooled confidence interval because a single degree of freedom is not reliable here. The point estimate may be displayed, but no pooled significance/null-crossing claim is emitted.
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `d6482e610299ab61d4643c18ecab8c0e7c553d4241aa012f37053067b54ce430`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 28304224 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 156 of 232 — docs/reviews/pcsk9-mace/index.html — UNRENDERABLE stale contrast block</summary>

Source ref: `38c04411`; lost SHA-256: `fdca11d8a769582367028487349f79b49a14b764e094d84c88cf4a01946b3ecf`.

Lost full text:

```text
UNRENDERABLE stale contrast block. cached arm-contrast membership named trials not in the current consumed pool; current pooled trial ids: 28304224, 30403574; suppressed stale ids: 41211925.
```

Candidate 1 of 1; SHA-256 `bc62f2c9671142508ecd8696d5fcee9820bc06708064489fa84096584f9b5bad`:

```text
UNRENDERABLE stale contrast block. cached arm-contrast membership named trials not in the current consumed pool; current pooled trial ids: 30403574; suppressed stale ids: 28304224, 41211925.
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 157 of 232 — docs/reviews/pcsk9-mace/index.html — Parser-confirmed contrast disclosure</summary>

Source ref: `38c04411`; lost SHA-256: `6b1015ba015124a05d3b28bdd01a8829f633da98dd366871940c3fe6fd13aada`.

Lost full text:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 2 of 2 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 28304224 parser-confirmed contrast evolocumab 30403574 parser-confirmed contrast alirocumab
```

Candidate 1 of 1; SHA-256 `34e334ce6960d23eb9647b270b2c9cca5b75590e5fc516078e20b1d8b190f54c`:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 1 of 1 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 30403574 parser-confirmed contrast alirocumab
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 158 of 232 — docs/reviews/pcsk9-mace/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `d9291e533c7957c2a9011b25d7c3c6865685f9c9a3d449da02a8a59c69762871`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 4 of 4 known (1 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 28304224 industry — abstract abstract : (Funded by Amgen; FOURIER ClinicalTrials.gov number, NCT01764633 .). PMID 30403574 industry — abstract abstract : (Funded by Sanofi and Regeneron Pharmaceuticals; ODYSSEY OUTCOMES ClinicalTrials.gov number, NCT01663402 .). PMID 25773378 industry — abstract abstract : (Funded by Sanofi and Regeneron Pharmaceuticals; ODYSSEY LONG TERM ClinicalTrials.gov number, NCT01507831.). PMID 41211925 industry — abstract abstract : (Funded by Amgen; VESALIUS-CV ClinicalTrials.gov number, NCT03872401.). PMID 27846344 not stated (abstract only - full text not retrieved) — abstract abstract :
```

Candidate 1 of 1; SHA-256 `9eb20a926fbfa02e69605f5e19b094987f3fc8c0d85f203509018222b1fc0875`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 4 of 4 known (1 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 30403574 industry — abstract abstract : (Funded by Sanofi and Regeneron Pharmaceuticals; ODYSSEY OUTCOMES ClinicalTrials.gov number, NCT01663402 .). PMID 25773378 industry — abstract abstract : (Funded by Sanofi and Regeneron Pharmaceuticals; ODYSSEY LONG TERM ClinicalTrials.gov number, NCT01507831.). PMID 28304224 industry — abstract abstract : (Funded by Amgen; FOURIER ClinicalTrials.gov number, NCT01764633 .). PMID 41211925 industry — abstract abstract : (Funded by Amgen; VESALIUS-CV ClinicalTrials.gov number, NCT03872401.). PMID 27846344 not stated (abstract only - full text not retrieved) — abstract abstract :
```

</details>

<details><summary>Pair 159 of 232 — docs/reviews/pcsk9-mace/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `26fc49f9685a5367bf10f03f5eb60d58d686febbe7d328013c48420be6ac1015`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=2 of 2)
```

Candidate 1 of 1; SHA-256 `907e96459f0676ed291eafe578d7ed148d3184fa1b8274d074077cc53eadf371`:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=1 of 1)
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `d6482e610299ab61d4643c18ecab8c0e7c553d4241aa012f37053067b54ce430`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 28304224 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 160 of 232 — docs/reviews/pcsk9-mace/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `fcc31dc5745340de88d5fa0018c7ce9fc658a07c652fa6160a5541339cbe54c6`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision NOT_ASSESSABLE (NOT ASSESSED) 95% CI [None, None]; missing/insufficient: valid confidence interval; served pooled CI (refused); clinical threshold / MID with basis; information-size assessment with adequacy and basis | counted as ONE conservative downgrade pending human judgement (a check that could not run cannot raise certainty) Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (4 of ~32 completed unpublished, 12%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

Candidate 1 of 1; SHA-256 `8b615f74d8fc1e8fcfac7a60220327ccfc8f3f50837621f4fb52829b0eea70a2`:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.78, 0.93]; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (4 of ~32 completed unpublished, 12%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `d6482e610299ab61d4643c18ecab8c0e7c553d4241aa012f37053067b54ce430`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 28304224 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 161 of 232 — docs/reviews/pcsk9-mace/index.html — Randomised-contrast disclosure</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `d045eb82cc2e52801ad1f457995308936bee1d9e633f4b9709cdc1787504729b`.

Lost full text:

```text
Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 2 of 2 pooled trials have a registry-confirmed contrast (the intervention of interest differs across arms). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 28304224 randomised contrast verified evolocumab 30403574 randomised contrast verified alirocumab
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 162 of 232 — docs/reviews/pcsk9-mace/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `cdae34e1a6433db309ca24da20a1250284f651795828d207d569bccb725d3390`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 2 of 2 known (0 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 28304224 industry abstract only rent targets. (Funded by Amgen; FOURIER ClinicalTrials.gov number, NCT01764633 .). PMID 30403574 industry abstract only ived placebo. (Funded by Sanofi and Regeneron Pharmaceuticals; ODYSSEY OUTCOMES ClinicalTrials.gov number, NCT01663402 .).
```

Candidate 1 of 1; SHA-256 `9eb20a926fbfa02e69605f5e19b094987f3fc8c0d85f203509018222b1fc0875`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 4 of 4 known (1 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 30403574 industry — abstract abstract : (Funded by Sanofi and Regeneron Pharmaceuticals; ODYSSEY OUTCOMES ClinicalTrials.gov number, NCT01663402 .). PMID 25773378 industry — abstract abstract : (Funded by Sanofi and Regeneron Pharmaceuticals; ODYSSEY LONG TERM ClinicalTrials.gov number, NCT01507831.). PMID 28304224 industry — abstract abstract : (Funded by Amgen; FOURIER ClinicalTrials.gov number, NCT01764633 .). PMID 41211925 industry — abstract abstract : (Funded by Amgen; VESALIUS-CV ClinicalTrials.gov number, NCT03872401.). PMID 27846344 not stated (abstract only - full text not retrieved) — abstract abstract :
```

</details>

<details><summary>Pair 163 of 232 — docs/reviews/pcsk9-mace/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `7b2d1674478f8315cbef7e6285dad3f45e0a93bc14acce314da847954a6bcbb9`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 2 of 2 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=2, HR 0.85 [0.5852, 1.2346] Low risk of bias only k=2, HR 0.85 [0.5852, 1.2346] (fewer trials than the full pool — see coverage)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `d6482e610299ab61d4643c18ecab8c0e7c553d4241aa012f37053067b54ce430`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 28304224 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 164 of 232 — docs/reviews/pcsk9-mace/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `9fb655c4cc64424164f8dee8b10bed1f52ddf44da88fa836084f5ea54e5ed034`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 2 assessed trial(s) at high risk; fewer than half at 'some concerns' Inconsistency not downgraded tau^2=0.0 (no between-study heterogeneity detected) Imprecision −1 95% CI [0.5852, 1.2346]; crosses the null AND is compatible with an appreciable benefit (<=0.75) -> imprecise (the estimate is consistent with both no effect and an appreciable effect) Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED registry census (4 of ~32 completed unpublished, 12%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `d6482e610299ab61d4643c18ecab8c0e7c553d4241aa012f37053067b54ce430`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 28304224 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 165 of 232 — docs/reviews/probiotics-aad-prevention/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `b4bdc203ce6067210a64234c491b6dcb461b1c0b396cf672349d6fe0f606243c`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (HAND_WRITTEN_KEYWORD_SEARCH): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:42608299, PMID:40716758, NCT05974657, NCT02765217, PMID:39935568, PMID:39497860, and 37 more; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `5acbd6cfa500a6745873773bf3e91f8a9ad6b55078ea63278b4851315f229042`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (HAND_WRITTEN_KEYWORD_SEARCH): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:42608299, PMID:41699149, PMID:40716758, NCT05974657, NCT02765217, PMID:39935568, and 51 more; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 166 of 232 — docs/reviews/probiotics-aad-prevention/index.html — UNRENDERABLE stale contrast block</summary>

Source ref: `38c04411`; lost SHA-256: `77f3cbdb52b51addfcc9892154cbd26a803b52d90e232b746469d0fc10f9e6db`.

Lost full text:

```text
UNRENDERABLE stale contrast block. cached arm-contrast membership named trials not in the current consumed pool; current pooled trial ids: 11560298, 15740542, 18026577, 18410562, 18701826, 21165295, 23932219, 24772726, 32035998, 35727573, 7872284; suppressed stale ids: 24456384, 26973849, 34541475, 39529939, 40488914.
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 167 of 232 — docs/reviews/probiotics-aad-prevention/index.html — Parser-confirmed contrast disclosure</summary>

Source ref: `38c04411`; lost SHA-256: `a4202f29dee64d773c60cc3cdff23f3359d13c1efa0d7727e10490fa847b1d26`.

Lost full text:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 1 of 11 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 35727573 parser-confirmed contrast multispecies probiotic 11560298 unverified_no_registry_match — 15740542 unverified_no_registry_match — 18026577 unverified_no_registry_match — 18410562 unverified_no_registry_match — 18701826 unverified_no_registry_match — 21165295 unverified_no_registry_match — 23932219 unverified_no_registry_match — 24772726 unverified_no_registry_match — 32035998 unverified_no_registry_match — 7872284 unverified_no_registry_match —
```

Candidate 1 of 1; SHA-256 `315391e120cdc66db834dfc17883bc349c14bcc6939259de0acf7ff78b2758e7`:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 3 of 16 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 39529939 contrast unverified (registry class label / dev code) sinquanon 26973849 parser-confirmed contrast saccharomyces boulardii 35727573 parser-confirmed contrast multispecies probiotic 40488914 parser-confirmed contrast lactobacillus reuteri dsm 17938 11560298 unverified_no_registry_match — 15740542 unverified_no_registry_match — 18026577 unverified_no_registry_match — 18410562 unverified_no_registry_match — 18701826 unverified_no_registry_match — 21165295 unverified_no_registry_match — 23932219 unverified_no_registry_match — 24456384 unverified_no_registry_match — 24772726 unverified_no_registry_match — 32035998 unverified_no_registry_match — 34541475 unverified_no_registry_match — 7872284 unverified_no_registry_match —
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 168 of 232 — docs/reviews/probiotics-aad-prevention/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `87663c208c957338286858cb320c97a709c09ca5d787df8b23a36bbe0b650098`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 2 of 5 known (52 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 39529939 industry — full text full text : <italic toggle="yes">Financial support</italic>.</bold> This work was supported by Neopharm Bulgaria Ltd. PMID 34541475 industry — abstract abstract : FUNDING: Yakult Honsha Co., Ltd. PMID 23932219 public/non-profit — abstract abstract : FUNDING: Health Technology Assessment programme; National Institute for Health Research, UK. PMID 26973849 public/non-profit — full text full text : </p><p><bold><italic toggle="yes">Financial support</italic>. </bold>This investigator-initiated trial was funded by the <funding-source>German Federal Ministry of Education and Research</funding-source> (Bundesministerium fur Bildung und Forschung; reference <award-id>01KG0902</award-id>) and received institutional funding by the <funding-source>Bernhard Nocht Institute for Tropical Medicine and the University Medical Center Hamburg-Eppendorf</fundi PMID 40548185 public/non-profit — full text full text : <bold>Funding:</bold> The authors received no specific funding for this work.</p></fn></fn-group></notes></front><body id="fsn370490-body-0001"><sec id="fsn370490-sec-0001"><label>1</label><title>Introduction</title><p>Antibiotic‐associated diarrhea (AAD), defined as unexplained diarrhea linked to antibiotic administration, is a common clinical complication with incidence rates varying from 5% to 35%, influenced by antibio PMID 35727573 not stated (full text scanned) — full text full text : PMID 32035998 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 24772726 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 18701826 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 18410562 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 15740542 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 11560298 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 7872284 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 21165295 not stated (full text scanned) — full text full text : PMID 18026577 not stated (full text scanned) — full text full text : PMID 41699149 not stated (full text scanned) — full text full text : PMID 10545590 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 10547243 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 14627358 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 16292090 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 16572062 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 17356555 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 18949181 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 19138244 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 20145608 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 21552138 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 2184848 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 21871144 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 22371721 not stated (full text scanned) — full text full text : PMID 22472744 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 23618760 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 24044687 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 24456384 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 27169634 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 28871492 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 30149135 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 30439760 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 30912409 not stated (full text scanned) — full text full text : PMID 33032474 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 38258024 not stated (full text scanned) — full text full text : PMID 39429834 not stated (full text scanned) — full text full text : PMID 39467682 not stated (full text scanned) — full text full text : PMID 39497860 not stated (full text scanned) — full text full text : PMID 39935568 not stated (full text scanned) — full text full text : PMID 40488914 not stated (full text scanned) — full text full text : PMID 40716758 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 42608299 not stated (full text scanned) — full text full text : PMID 9570649 not stated (abstract only - full text not retrieved) — abstract abstract : NCT02589964 source not retrieved — : NCT02722993 source not retrieved — : NCT02993419 source not retrieved — : NCT03516409 source not retrieved — : NCT03755765 source not retrieved — : NCT04529980 source not retrieved — : NCT05845073 source not retrieved — : NCT06990568 source not retrieved — : NCT07234448 source not retrieved — :
```

Candidate 1 of 1; SHA-256 `24aae4e08de63e04692b91ed44843de5c59bcec5fd5dfdd6e60f918be0ef658e`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 2 of 5 known (52 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 34541475 industry — abstract abstract : FUNDING: Yakult Honsha Co., Ltd. PMID 39529939 industry — full text full text : <italic toggle="yes">Financial support</italic>.</bold> This work was supported by Neopharm Bulgaria Ltd. PMID 23932219 public/non-profit — abstract abstract : FUNDING: Health Technology Assessment programme; National Institute for Health Research, UK. PMID 26973849 public/non-profit — full text full text : </p><p><bold><italic toggle="yes">Financial support</italic>. </bold>This investigator-initiated trial was funded by the <funding-source>German Federal Ministry of Education and Research</funding-source> (Bundesministerium fur Bildung und Forschung; reference <award-id>01KG0902</award-id>) and received institutional funding by the <funding-source>Bernhard Nocht Institute for Tropical Medicine and the University Medical Center Hamburg-Eppendorf</fundi PMID 40548185 public/non-profit — full text full text : <bold>Funding:</bold> The authors received no specific funding for this work.</p></fn></fn-group></notes></front><body id="fsn370490-body-0001"><sec id="fsn370490-sec-0001"><label>1</label><title>Introduction</title><p>Antibiotic‐associated diarrhea (AAD), defined as unexplained diarrhea linked to antibiotic administration, is a common clinical complication with incidence rates varying from 5% to 35%, influenced by antibio PMID 10545590 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 10547243 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 11560298 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 14627358 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 15740542 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 16292090 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 16572062 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 17356555 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 18026577 not stated (full text scanned) — full text full text : PMID 18410562 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 18701826 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 18949181 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 19138244 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 20145608 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 21165295 not stated (full text scanned) — full text full text : PMID 21552138 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 2184848 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 21871144 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 22371721 not stated (full text scanned) — full text full text : PMID 22472744 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 23618760 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 24044687 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 24456384 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 24772726 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 27169634 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 28871492 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 30149135 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 30439760 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 30912409 not stated (full text scanned) — full text full text : PMID 32035998 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 33032474 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 35727573 not stated (full text scanned) — full text full text : PMID 38258024 not stated (full text scanned) — full text full text : PMID 39429834 not stated (full text scanned) — full text full text : PMID 39467682 not stated (full text scanned) — full text full text : PMID 39497860 not stated (full text scanned) — full text full text : PMID 39935568 not stated (full text scanned) — full text full text : PMID 40488914 not stated (full text scanned) — full text full text : PMID 40716758 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 41699149 not stated (full text scanned) — full text full text : PMID 42608299 not stated (full text scanned) — full text full text : PMID 7872284 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 9570649 not stated (abstract only - full text not retrieved) — abstract abstract : NCT02589964 source not retrieved — : NCT02722993 source not retrieved — : NCT02993419 source not retrieved — : NCT03516409 source not retrieved — : NCT03755765 source not retrieved — : NCT04529980 source not retrieved — : NCT05845073 source not retrieved — : NCT06990568 source not retrieved — : NCT07234448 source not retrieved — :
```

</details>

<details><summary>Pair 169 of 232 — docs/reviews/probiotics-aad-prevention/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `412923805bc9b8e369cb8971aee830708c17d48ad3860eac454675880b54c337`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=11 of 11)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `34dc7447eb86ca1fbb5b58e7a57f363e9ea909847105fb23add856a139d800c8`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 11: PMID 35727573 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 32035998 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 24772726 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 23932219 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE); PMID 18701826 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 18410562 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 15740542 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 11560298 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 7872284 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 21165295 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 18026577 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 170 of 232 — docs/reviews/probiotics-aad-prevention/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `9a7a95e72f9798610320efd986c3e2e045ca4137460f673b9f8c9e31bdf7c123`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (46 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.4803, 0.9839]; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (10 of ~20 completed unpublished, 50%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `34dc7447eb86ca1fbb5b58e7a57f363e9ea909847105fb23add856a139d800c8`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 11: PMID 35727573 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 32035998 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 24772726 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 23932219 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE); PMID 18701826 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 18410562 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 15740542 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 11560298 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 7872284 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 21165295 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 18026577 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 171 of 232 — docs/reviews/probiotics-aad-prevention/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `9458afdf56d6a319889db473ad3764ace2419c1f8421160b39c75ed881b3e313`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: 42608299, 41699149, 40716758, 40548185, 39935568, 39497860, and 38 more; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `5acbd6cfa500a6745873773bf3e91f8a9ad6b55078ea63278b4851315f229042`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (HAND_WRITTEN_KEYWORD_SEARCH): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:42608299, PMID:41699149, PMID:40716758, NCT05974657, NCT02765217, PMID:39935568, and 51 more; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 172 of 232 — docs/reviews/probiotics-aad-prevention/index.html — DECLARED ABSENT</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `34a8823b0bad217626b851828dc856654dbbae42bf5964fcb712262cb30490a3`.

Lost full text:

```text
DECLARED ABSENT. REPORTED but not extractable as a pooled value: 42608299, 41699149, 40716758, 40548185, 40488914, 39935568 and others mention this outcome in the committed abstract, but without arm counts or an effect+CI in an extractable form (e.g. a bare percentage with no denominator). This outcome is NOT absent — it is reported-but-not-poolable from the committed source; full-text acquisition would recover the countable form.
```

Candidate 1 of 1; SHA-256 `fe75df27782f7976276f190902224de34ae663ef59b4b17aff94b8b642edbee5`:

```text
DECLARED ABSENT. no admitted trial: 11 candidate extraction(s) reached the pool and were set aside on admission (family eligibility not established by held evidence, P5); each stays listed below with the value it carried; no pooled result until eligibility is established
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 173 of 232 — docs/reviews/probiotics-aad-prevention/index.html — DECLARED ABSENT</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `6ecb01b65a6288b3037ae6e2f1019cda43b2ae320ca660365fa61d46a93210f5`.

Lost full text:

```text
DECLARED ABSENT. REPORTED but not extractable as a pooled value: 40548185, 26973849, 23932219, 19138244 mention this outcome in the committed abstract, but without arm counts or an effect+CI in an extractable form (e.g. a bare percentage with no denominator). This outcome is NOT absent — it is reported-but-not-poolable from the committed source; full-text acquisition would recover the countable form.
```

Candidate 1 of 1; SHA-256 `fe75df27782f7976276f190902224de34ae663ef59b4b17aff94b8b642edbee5`:

```text
DECLARED ABSENT. no admitted trial: 11 candidate extraction(s) reached the pool and were set aside on admission (family eligibility not established by held evidence, P5); each stays listed below with the value it carried; no pooled result until eligibility is established
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 174 of 232 — docs/reviews/probiotics-aad-prevention/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `4b252317efdebe6963ef01a013fe5eb43646c12497849c9063636b005ef2cfc9`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 1 of 2 known (14 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 14 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 34541475 industry abstract only ical outcomes. FUNDING: Yakult Honsha Co., Ltd. PMID 23932219 public/non-profit abstract only uture studies. FUNDING: Health Technology Assessment programme; National Institute for Health Research, UK. PMID 40488914 not stated (abstract only — full text not retrieved) abstract only PMID 39529939 not stated (abstract only — full text not retrieved) abstract only PMID 35727573 not stated (abstract only — full text not retrieved) abstract only PMID 32035998 not stated (abstract only — full text not retrieved) abstract only PMID 26973849 not stated (abstract only — full text not retrieved) abstract only PMID 24772726 not stated (abstract only — full text not retrieved) abstract only PMID 18701826 not stated (abstract only — full text not retrieved) abstract only PMID 18410562 not stated (abstract only — full text not retrieved) abstract only PMID 15740542 not stated (abstract only — full text not retrieved) abstract only PMID 11560298 not stated (abstract only — full text not retrieved) abstract only PMID 7872284 not stated (abstract only — full text not retrieved) abstract only PMID 24456384 not stated (abstract only — full text not retrieved) abstract only PMID 21165295 not stated (abstract only — full text not retrieved) abstract only PMID 18026577 not stated (abstract only — full text not retrieved) abstract only
```

Candidate 1 of 1; SHA-256 `24aae4e08de63e04692b91ed44843de5c59bcec5fd5dfdd6e60f918be0ef658e`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 2 of 5 known (52 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 34541475 industry — abstract abstract : FUNDING: Yakult Honsha Co., Ltd. PMID 39529939 industry — full text full text : <italic toggle="yes">Financial support</italic>.</bold> This work was supported by Neopharm Bulgaria Ltd. PMID 23932219 public/non-profit — abstract abstract : FUNDING: Health Technology Assessment programme; National Institute for Health Research, UK. PMID 26973849 public/non-profit — full text full text : </p><p><bold><italic toggle="yes">Financial support</italic>. </bold>This investigator-initiated trial was funded by the <funding-source>German Federal Ministry of Education and Research</funding-source> (Bundesministerium fur Bildung und Forschung; reference <award-id>01KG0902</award-id>) and received institutional funding by the <funding-source>Bernhard Nocht Institute for Tropical Medicine and the University Medical Center Hamburg-Eppendorf</fundi PMID 40548185 public/non-profit — full text full text : <bold>Funding:</bold> The authors received no specific funding for this work.</p></fn></fn-group></notes></front><body id="fsn370490-body-0001"><sec id="fsn370490-sec-0001"><label>1</label><title>Introduction</title><p>Antibiotic‐associated diarrhea (AAD), defined as unexplained diarrhea linked to antibiotic administration, is a common clinical complication with incidence rates varying from 5% to 35%, influenced by antibio PMID 10545590 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 10547243 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 11560298 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 14627358 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 15740542 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 16292090 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 16572062 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 17356555 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 18026577 not stated (full text scanned) — full text full text : PMID 18410562 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 18701826 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 18949181 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 19138244 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 20145608 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 21165295 not stated (full text scanned) — full text full text : PMID 21552138 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 2184848 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 21871144 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 22371721 not stated (full text scanned) — full text full text : PMID 22472744 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 23618760 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 24044687 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 24456384 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 24772726 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 27169634 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 28871492 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 30149135 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 30439760 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 30912409 not stated (full text scanned) — full text full text : PMID 32035998 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 33032474 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 35727573 not stated (full text scanned) — full text full text : PMID 38258024 not stated (full text scanned) — full text full text : PMID 39429834 not stated (full text scanned) — full text full text : PMID 39467682 not stated (full text scanned) — full text full text : PMID 39497860 not stated (full text scanned) — full text full text : PMID 39935568 not stated (full text scanned) — full text full text : PMID 40488914 not stated (full text scanned) — full text full text : PMID 40716758 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 41699149 not stated (full text scanned) — full text full text : PMID 42608299 not stated (full text scanned) — full text full text : PMID 7872284 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 9570649 not stated (abstract only - full text not retrieved) — abstract abstract : NCT02589964 source not retrieved — : NCT02722993 source not retrieved — : NCT02993419 source not retrieved — : NCT03516409 source not retrieved — : NCT03755765 source not retrieved — : NCT04529980 source not retrieved — : NCT05845073 source not retrieved — : NCT06990568 source not retrieved — : NCT07234448 source not retrieved — :
```

</details>

<details><summary>Pair 175 of 232 — docs/reviews/probiotics-aad-prevention/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `3690b1ad41faf51a261928ebca1cf523e09cb400f4cc759e307d156697580e8b`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 16 of 16 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=16, RR 0.702 [0.5352, 0.921] Low risk of bias only k=16, RR 0.702 [0.5352, 0.921] (fewer trials than the full pool — see coverage)
```

Candidate 1 of 1; SHA-256 `f7f6eb8ef26dd186392711f9e4a855ef2943d9b059b983abfcf39544728ced99`:

```text
Does the result survive dropping the trials that are not low risk of bias? Not computed (PRIMARY_ABSENT): the primary outcome has no pooled result (present = False). The per-trial rows and their risk-of-bias ratings are shown above; the omission is recorded in the review object as rob_sensitivity_omitted , not left silent.
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `34dc7447eb86ca1fbb5b58e7a57f363e9ea909847105fb23add856a139d800c8`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 11: PMID 35727573 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 32035998 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 24772726 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 23932219 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE); PMID 18701826 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 18410562 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 15740542 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 11560298 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 7872284 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 21165295 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 18026577 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 176 of 232 — docs/reviews/probiotics-aad-prevention/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `99becb418875e3d7ddd6dbda49c73006d7252e22eef6dc35199ff53c62376365`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 16 assessed trial(s) at high risk; fewer than half at 'some concerns' Inconsistency −1 tau^2=0.15045; prediction interval [0.2941, 1.676] is >=2x the CI width -> real heterogeneity Imprecision not downgraded 95% CI [0.5352, 0.921]; excludes the null with a reasonably tight interval -> precise Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED registry census (10 of ~20 completed unpublished, 50%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `34dc7447eb86ca1fbb5b58e7a57f363e9ea909847105fb23add856a139d800c8`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 11: PMID 35727573 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 32035998 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 24772726 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 23932219 UNKNOWN (INSUFFICIENT_PICD_EVIDENCE); PMID 18701826 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 18410562 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 15740542 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 11560298 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 7872284 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 21165295 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 18026577 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 177 of 232 — docs/reviews/sacubitril-valsartan-hfref/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `c3bf8041ee6fdf88965ae5f6fdae0fc99ff1ba543dba459715fe85bfabc01b38`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT02874794, NCT02900378, NCT04853758, NCT05487261, NCT02554890; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

Candidate 1 of 1; SHA-256 `b51833a4bd9acaf3327045b45d8d00c406e8322fe91c8375289f7b5aaee75f64`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT01035255, NCT02874794, NCT02900378, NCT04853758, NCT05487261, NCT02468232, and 1 more; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 178 of 232 — docs/reviews/sacubitril-valsartan-hfref/index.html — Pooled result REFUSED</summary>

Source ref: `38c04411`; lost SHA-256: `25b815a26c41df23f4e34d365ac51b9b1a07414d28670c55b65a73c2273adf04`.

Lost full text:

```text
Pooled result REFUSED (k=2 direction conflict). k=2 pooled row refused because point estimates are on opposite sides of the null At k=2, if point estimates are on opposite sides of the null or trial CIs do not overlap, no pooled row is served. A k=1 anchor is shown only when it is explicitly pre-named in the topic configuration/protocol metadata; otherwise both trials are shown only as named individual results. The invalid pooled row is quarantined for audit only: 0.84 (0.21-3.32), tau^2=0.01177, I^2=24.9%. STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `03937154481c229d694964b8d8daee2d470db684f750e28ab211fb058d198377`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 25176015 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); NCT02468232 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 179 of 232 — docs/reviews/sacubitril-valsartan-hfref/index.html — Does the result survive dropping the tri</summary>

Source ref: `38c04411`; lost SHA-256: `fd5d9339e4cec272f0d19d808c4ff57719dceaacda50c2fe63752a188ee7f460`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? Not computed: the primary pooled row is REFUSED (DIRECTION_CONFLICT_K2), so there is no pooled estimate to re-pool by risk-of-bias stratum. The per-trial rows and their risk-of-bias ratings are shown above; a stratified re-pool of a refused pool would be a number about nothing.
```

Candidate 1 of 1; SHA-256 `f7f6eb8ef26dd186392711f9e4a855ef2943d9b059b983abfcf39544728ced99`:

```text
Does the result survive dropping the trials that are not low risk of bias? Not computed (PRIMARY_ABSENT): the primary outcome has no pooled result (present = False). The per-trial rows and their risk-of-bias ratings are shown above; the omission is recorded in the review object as rob_sensitivity_omitted , not left silent.
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `03937154481c229d694964b8d8daee2d470db684f750e28ab211fb058d198377`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 25176015 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); NCT02468232 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 180 of 232 — docs/reviews/sacubitril-valsartan-hfref/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `4456aa150a2c2a2fc0ea67e7fece84b917f22c57c060b373961e706e72465f31`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. | counted as ONE conservative downgrade pending human judgement (a check that could not run cannot raise certainty) Imprecision NOT_ASSESSABLE (NOT ASSESSED) 95% CI [None, None]; missing/insufficient: valid confidence interval; served pooled CI (refused); clinical threshold / MID with basis; information-size assessment with adequacy and basis | counted as ONE conservative downgrade pending human judgement (a check that could not run cannot raise certainty) Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) missing/invalid registry census inputs: enumerated, ongoing_or_recent, ghost_upper_bound, positive completed-trial denominator
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `03937154481c229d694964b8d8daee2d470db684f750e28ab211fb058d198377`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 25176015 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); NCT02468232 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 181 of 232 — docs/reviews/sacubitril-valsartan-hfref/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `5fcfa0cc7dab8f958eee34b36da3422676a0eca3d6c4b0ee945e8d72b965e229`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: EVALUATE-HF · NCT02874794, OUTSTEP-HF · NCT02900378, ANSWER-HF · NCT04853758, PRESENT-HF · NCT05487261, PARALLEL-HF · NCT02468232, PIONEER-HF · NCT02554890; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `b51833a4bd9acaf3327045b45d8d00c406e8322fe91c8375289f7b5aaee75f64`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT01035255, NCT02874794, NCT02900378, NCT04853758, NCT05487261, NCT02468232, and 1 more; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 182 of 232 — docs/reviews/sacubitril-valsartan-hfref/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `072a75e8e15be99b57cc84e267fcc385e25589124b7fc7b60d3203a4a6083bbf`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 1 of 1 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=1, HR 0.8 [0.7328, 0.8733] Low risk of bias only k=1, HR 0.8 [0.7328, 0.8733] (fewer trials than the full pool — see coverage)
```

Candidate 1 of 1; SHA-256 `f7f6eb8ef26dd186392711f9e4a855ef2943d9b059b983abfcf39544728ced99`:

```text
Does the result survive dropping the trials that are not low risk of bias? Not computed (PRIMARY_ABSENT): the primary outcome has no pooled result (present = False). The per-trial rows and their risk-of-bias ratings are shown above; the omission is recorded in the review object as rob_sensitivity_omitted , not left silent.
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `03937154481c229d694964b8d8daee2d470db684f750e28ab211fb058d198377`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 25176015 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); NCT02468232 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 183 of 232 — docs/reviews/sacubitril-valsartan-hfref/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `09ed94fe6e8360cfecf6ad69db79fcb7ca77b505565936768935dc6b62adcb67`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 1 assessed trial(s) at high risk; fewer than half at 'some concerns' Inconsistency NOT ASSESSED single trial (k=1): between-study inconsistency is not estimable Imprecision not downgraded 95% CI [0.73, 0.87]; excludes the null with a reasonably tight interval -> precise; single trial — imprecision judged from the CI, not downgraded merely for k=1 Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED no registry ghost census available for this topic
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `03937154481c229d694964b8d8daee2d470db684f750e28ab211fb058d198377`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 25176015 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); NCT02468232 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 184 of 232 — docs/reviews/semaglutide-obesity-mace/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `71e4002ec9f8906c097fbff9ca975a30fafe8656bd556978858a78671ec131b5`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic.
```

Candidate 1 of 1; SHA-256 `056661be86199ed100fa8795e0eab9f56a9d641075d37fe62e01e212ca9c8908`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT03574597; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 185 of 232 — docs/reviews/semaglutide-obesity-mace/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `907e96459f0676ed291eafe578d7ed148d3184fa1b8274d074077cc53eadf371`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=1 of 1)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `93e15d094f2573f8db2412b895bb2f7625442ef47453570d1a9a97607c6b1cd4`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 37952131 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 186 of 232 — docs/reviews/semaglutide-obesity-mace/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `7297945722c8a4bc981a87ab4d2cae9c0dfcc484abfbc2db01bc3a2216ebaf3e`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) single trial (k=1): between-study inconsistency is not estimable Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.72, 0.9]; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (18 of ~78 completed unpublished, 23%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `93e15d094f2573f8db2412b895bb2f7625442ef47453570d1a9a97607c6b1cd4`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 37952131 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 187 of 232 — docs/reviews/semaglutide-obesity-mace/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `26ab09f2b6cbce2e1e158fb630fa57a0c0186f3db7491523f7fa2adf79d4fcbc`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 1 of 1 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=1, HR 0.8 [0.7155, 0.8944] Low risk of bias only NOT ESTIMABLE — no pooled trial qualifies as low risk of bias, so this stratum has no trials to re-pool (an empty subgroup is not agreement with the full pool)
```

Candidate 1 of 1; SHA-256 `f7f6eb8ef26dd186392711f9e4a855ef2943d9b059b983abfcf39544728ced99`:

```text
Does the result survive dropping the trials that are not low risk of bias? Not computed (PRIMARY_ABSENT): the primary outcome has no pooled result (present = False). The per-trial rows and their risk-of-bias ratings are shown above; the omission is recorded in the review object as rob_sensitivity_omitted , not left silent.
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `93e15d094f2573f8db2412b895bb2f7625442ef47453570d1a9a97607c6b1cd4`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 37952131 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 188 of 232 — docs/reviews/semaglutide-obesity-mace/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `3fe49f850a635eb2189b79baa4f679f142e19bce8eacd03224e40f2a3feee68c`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias −1 1 of 1 assessed trial(s) at 'some concerns' Inconsistency NOT ASSESSED single trial (k=1): between-study inconsistency is not estimable Imprecision not downgraded 95% CI [0.72, 0.9]; excludes the null with a reasonably tight interval -> precise; single trial — imprecision judged from the CI, not downgraded merely for k=1 Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED registry census (18 of ~78 completed unpublished, 23%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `93e15d094f2573f8db2412b895bb2f7625442ef47453570d1a9a97607c6b1cd4`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 37952131 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 189 of 232 — docs/reviews/sglt2-primary-prevention-hf/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `26c9b8a85ba34b20b599a11e177f6157a5e1eaf7e9a9e3b7014cde829a457f3a`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (RAN_ERROR_rendered_as_run): Registry-first (AACT) = RAN_ERROR; the source_status table shows it, but the search narrative still presents the topic as registry-first. RAN_ERROR must never be rendered as a completed search (extends the audit-22 NOT_RUN gate limb to RAN_ERROR). screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT03151343, NCT02998970; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `0c125a17f0488814fb35e2b8f8b572fa9f7121a881716c2860554f6b33d080b7`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (RAN_ERROR_rendered_as_run): Registry-first (AACT) = RAN_ERROR; the source_status table shows it, but the search narrative still presents the topic as registry-first. RAN_ERROR must never be rendered as a completed search (extends the audit-22 NOT_RUN gate limb to RAN_ERROR). screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT01032629, NCT01131676, NCT01730534, NCT03151343, NCT02998970; the completeness claim cannot be current
```

</details>

<details><summary>Pair 190 of 232 — docs/reviews/sglt2-primary-prevention-hf/index.html — Parser-confirmed contrast disclosure</summary>

Source ref: `38c04411`; lost SHA-256: `9e50c83d5041acf5fff3543c858741f3b0110263f5b577ef7cf23e7dacad57a5`.

Lost full text:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 3 of 4 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 26378978 contrast unverified (registry class label / dev code) bi 10773 high dose; bi 10773 low dose 28605608 parser-confirmed contrast canagliflozin (jnj-28431754) 100 mg; canagliflozin (jnj-28431754) 300 mg 30415602 parser-confirmed contrast dapagliflozin 10 mg 32966714 parser-confirmed contrast ertugliflozin
```

Candidate 1 of 1; SHA-256 `a41ca71bea5027d867543ebde6b5c0e9554b7d08f1e9da2ed5f3987e62c03cea`:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 1 of 1 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 32966714 parser-confirmed contrast ertugliflozin
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 191 of 232 — docs/reviews/sglt2-primary-prevention-hf/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `8e39c5bb4d288d58bac9867a3af20d4648177c1043d7e149c038588ac7c3d818`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 4 of 4 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 28605608 industry — abstract abstract : (Funded by Janssen Research and Development; CANVAS and CANVAS-R ClinicalTrials.gov numbers, NCT01032629 and NCT01989754 , respectively.). PMID 26378978 industry — abstract abstract : (Funded by Boehringer Ingelheim and Eli Lilly; EMPA-REG OUTCOME ClinicalTrials.gov number, NCT01131676.). PMID 32966714 industry — abstract abstract : (Funded by Merck Sharp & Dohme and Pfizer; VERTIS CV ClinicalTrials.gov number, NCT01986881.). PMID 30415602 industry — abstract abstract : (Funded by AstraZeneca; DECLARE-TIMI 58 ClinicalTrials.gov number, NCT01730534 .). PMID 31434508 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 35061894 not stated (abstract only - full text not retrieved) — abstract abstract :
```

Candidate 1 of 1; SHA-256 `3ed7c7ff18887949733a8a0ab494bc3ced36d5a9fc569825225213a83acf5e05`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 4 of 4 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 32966714 industry — abstract abstract : (Funded by Merck Sharp & Dohme and Pfizer; VERTIS CV ClinicalTrials.gov number, NCT01986881.). PMID 26378978 industry — abstract abstract : (Funded by Boehringer Ingelheim and Eli Lilly; EMPA-REG OUTCOME ClinicalTrials.gov number, NCT01131676.). PMID 28605608 industry — abstract abstract : (Funded by Janssen Research and Development; CANVAS and CANVAS-R ClinicalTrials.gov numbers, NCT01032629 and NCT01989754 , respectively.). PMID 30415602 industry — abstract abstract : (Funded by AstraZeneca; DECLARE-TIMI 58 ClinicalTrials.gov number, NCT01730534 .). PMID 31434508 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 35061894 not stated (abstract only - full text not retrieved) — abstract abstract :
```

</details>

<details><summary>Pair 192 of 232 — docs/reviews/sglt2-primary-prevention-hf/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `5ebf3921cd1d00d113071fff60d81dffc7ae147d66bb6ce82602e541f414570f`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed
```

Candidate 1 of 1; SHA-256 `907e96459f0676ed291eafe578d7ed148d3184fa1b8274d074077cc53eadf371`:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=1 of 1)
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `0c7596022dc457a74efc5beedb95829b79525c7bc9515c7fbb4365155d04adcf`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 1 [PMID 32966714]. Set aside on P5 (family eligibility) 3: PMID 28605608 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 26378978 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 30415602 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 193 of 232 — docs/reviews/sglt2-primary-prevention-hf/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `cc866a15d4e5120a30f659822931c9b0f66aa49c9d5f515a55240e1e488b666b`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.5763, 0.8397]; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) missing/invalid registry census inputs: enumerated, ongoing_or_recent, ghost_upper_bound, positive completed-trial denominator
```

Candidate 1 of 1; SHA-256 `1dbd8c7162b6336de0764b5791caa77da1fa3b11f3a4a813937d98ee344acfca`:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.54, 0.9]; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) missing/invalid registry census inputs: enumerated, ongoing_or_recent, ghost_upper_bound, positive completed-trial denominator
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `0c7596022dc457a74efc5beedb95829b79525c7bc9515c7fbb4365155d04adcf`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 1 [PMID 32966714]. Set aside on P5 (family eligibility) 3: PMID 28605608 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 26378978 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 30415602 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 194 of 232 — docs/reviews/sglt2-primary-prevention-hf/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `d4a66e208cfb54fbe42b8454092b39b1f045d6ee3dbdba80489d55540ec70baa`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (RAN_ERROR_rendered_as_run): Registry-first (AACT) = RAN_ERROR; the source_status table shows it, but the search narrative still presents the topic as registry-first. RAN_ERROR must never be rendered as a completed search (extends the audit-22 NOT_RUN gate limb to RAN_ERROR). screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: 22431673, 27651331, 39843293, 35061894, 31984646, 34132018, and 10 more; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `0c125a17f0488814fb35e2b8f8b572fa9f7121a881716c2860554f6b33d080b7`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (RAN_ERROR_rendered_as_run): Registry-first (AACT) = RAN_ERROR; the source_status table shows it, but the search narrative still presents the topic as registry-first. RAN_ERROR must never be rendered as a completed search (extends the audit-22 NOT_RUN gate limb to RAN_ERROR). screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT01032629, NCT01131676, NCT01730534, NCT03151343, NCT02998970; the completeness claim cannot be current
```

</details>

<details><summary>Pair 195 of 232 — docs/reviews/sglt2-primary-prevention-hf/index.html — Randomised-contrast disclosure</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `1dbb0dc87beac85c77ac53fc9f52406d3eddd62cb4ccfc74ca034f7b0ed71e21`.

Lost full text:

```text
Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 3 of 4 pooled trials have a registry-confirmed contrast (the intervention of interest differs across arms). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 26378978 contrast unverified (registry class label / dev code) bi 10773 high dose; bi 10773 low dose 28605608 randomised contrast verified canagliflozin (jnj-28431754) 100 mg; canagliflozin (jnj-28431754) 300 mg 30415602 randomised contrast verified dapagliflozin 10 mg 32966714 randomised contrast verified ertugliflozin
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 196 of 232 — docs/reviews/sglt2-primary-prevention-hf/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `bc8f2f2191b9b07735e8a5c8399a6fa9d72f51df88021e62676d49dc665aea26`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 4 of 4 known (0 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 28605608 industry abstract only r metatarsal. (Funded by Janssen Research and Development; CANVAS and CANVAS-R ClinicalTrials.gov numbers, NCT01032629 and NCT01989754 , respectively.). PMID 26378978 industry abstract only tandard care. (Funded by Boehringer Ingelheim and Eli Lilly; EMPA-REG OUTCOME ClinicalTrials.gov number, NCT01131676.). PMID 32966714 industry abstract only cular events. (Funded by Merck Sharp & Dohme and Pfizer; VERTIS CV ClinicalTrials.gov number, NCT01986881.). PMID 30415602 industry abstract only eart failure. (Funded by AstraZeneca; DECLARE-TIMI 58 ClinicalTrials.gov number, NCT01730534 .).
```

Candidate 1 of 1; SHA-256 `3ed7c7ff18887949733a8a0ab494bc3ced36d5a9fc569825225213a83acf5e05`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 4 of 4 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 32966714 industry — abstract abstract : (Funded by Merck Sharp & Dohme and Pfizer; VERTIS CV ClinicalTrials.gov number, NCT01986881.). PMID 26378978 industry — abstract abstract : (Funded by Boehringer Ingelheim and Eli Lilly; EMPA-REG OUTCOME ClinicalTrials.gov number, NCT01131676.). PMID 28605608 industry — abstract abstract : (Funded by Janssen Research and Development; CANVAS and CANVAS-R ClinicalTrials.gov numbers, NCT01032629 and NCT01989754 , respectively.). PMID 30415602 industry — abstract abstract : (Funded by AstraZeneca; DECLARE-TIMI 58 ClinicalTrials.gov number, NCT01730534 .). PMID 31434508 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 35061894 not stated (abstract only - full text not retrieved) — abstract abstract :
```

</details>

<details><summary>Pair 197 of 232 — docs/reviews/sglt2-primary-prevention-hf/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `8d61bf47c06063dec14f2d4656e683b5c5445128098b53a4545d6f790bf52db7`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 4 of 4 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=4, HR 0.6956 [0.5763, 0.8397] Low risk of bias only k=3, HR 0.7023 [0.5281, 0.934]
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `0c7596022dc457a74efc5beedb95829b79525c7bc9515c7fbb4365155d04adcf`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 1 [PMID 32966714]. Set aside on P5 (family eligibility) 3: PMID 28605608 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 26378978 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 30415602 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 198 of 232 — docs/reviews/sglt2-primary-prevention-hf/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `a88aa38b82f42e250de2a7b237f6026ce62106c4c5a06c14521eef07aba1cf69`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capped below high because D3 (missing outcome data), a required risk-of-bias domain, is NOT ASSESSED for any pooled trial (no outcome-missingness source) — high certainty cannot be certified on a structurally-incomplete bias assessment. PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 4 assessed trial(s) at high risk; fewer than half at 'some concerns' Inconsistency not downgraded tau^2=0.0 (no between-study heterogeneity detected) Imprecision not downgraded 95% CI [0.5763, 0.8397]; excludes the null with a reasonably tight interval -> precise Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED no registry ghost census available for this topic
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `0c7596022dc457a74efc5beedb95829b79525c7bc9515c7fbb4365155d04adcf`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 1; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 1 [PMID 32966714]. Set aside on P5 (family eligibility) 3: PMID 28605608 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 26378978 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED); PMID 30415602 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 199 of 232 — docs/reviews/spironolactone-hfref-mortality/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `47f25de516e8331c1685db66a4ac6a6bf5c69c58da28055a70125e5026b92486`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (PMID_ENUMERATION_explicit): protocol Search section explicitly says UID-anchored queries for the named trials — known-item retrieval, cannot discover an unknown eligible trial.
```

Candidate 1 of 1; SHA-256 `aed2f4e6aea9371d9233f82b8c3abcd7ccbd5a1a22930f043ced6fbc79a34d19`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (PMID_ENUMERATION_explicit): protocol Search section explicitly says UID-anchored queries for the named trials — known-item retrieval, cannot discover an unknown eligible trial. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:10471456, NCT00232180; the completeness claim cannot be current
```

</details>

<details><summary>Pair 200 of 232 — docs/reviews/spironolactone-hfref-mortality/index.html — Parser-confirmed contrast disclosure</summary>

Source ref: `38c04411`; lost SHA-256: `14ee8dac6bdc9da7f3d1b1c60075490792031622e14e5d2c9227cbd21c410707`.

Lost full text:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 1 of 3 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 21073363 contrast unverified — no registry arm data — 28824029 parser-confirmed contrast eplerenone 10471456 unverified_no_registry_match —
```

Candidate 1 of 1; SHA-256 `88c01280ad10cdfa70dc1abc9750d3e3eccef686e5534e6a50c1e3a7b1002b38`:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 1 of 1 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 28824029 parser-confirmed contrast eplerenone
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 201 of 232 — docs/reviews/spironolactone-hfref-mortality/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `8f716b4a17203bdc48be922491dc4e00c40c6d472b1b14453dec54523e9ef0ea`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 1 of 1 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 21073363 industry — abstract abstract : (Funded by Pfizer; ClinicalTrials.gov number, NCT00232180.). PMID 10471456 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 28824029 not stated (abstract only - full text not retrieved) — abstract abstract :
```

Candidate 1 of 1; SHA-256 `8ef438c31875addb16df0f843a7de52e27eb676a741c8bf02e5c28949404921f`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 1 of 1 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 21073363 industry — abstract abstract : (Funded by Pfizer; ClinicalTrials.gov number, NCT00232180.). PMID 28824029 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 10471456 not stated (abstract only - full text not retrieved) — abstract abstract :
```

</details>

<details><summary>Pair 202 of 232 — docs/reviews/spironolactone-hfref-mortality/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `64e139033bbf16cc59dcfc2119ac644685e062f9772edcc481e8de6ba2e4505b`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency ASSESSED: not downgraded tau^2=0.0 (no between-study heterogeneity detected) Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.5609, 0.9486]; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (13 of ~43 completed unpublished, 30%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

Candidate 1 of 1; SHA-256 `3f2305257fd0b666cd44ee671d33c6ded1887f19681c3665d9ff0c99439295fe`:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision ASSESSED: −1 95% CI [0.53, 1.36]; GRADE default appreciable-effect thresholds 0.75/1.25; no topic threshold registered; spans clinical decisions or inadequate information -> imprecise; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (13 of ~43 completed unpublished, 30%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `5a138c6f7d212e00800cd026313528ce25cd7d824fc7eb31d8f3c29834552067`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 0; migration state (unbound_legacy, pooled and counted separately) 1 [PMID 28824029]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 10471456 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 21073363 INELIGIBLE. in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 203 of 232 — docs/reviews/spironolactone-hfref-mortality/index.html — DECLARED ABSENT</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `ec9fd7c4d2ac80fd976612d3b03f8ffdcb61d1f46cb8375d2f3bd6c7cff3ae4b`.

Lost full text:

```text
DECLARED ABSENT. REPORTED but not extractable as a pooled value: 10471456, 21073363, 28824029 mention this outcome in the committed abstract, but without arm counts or an effect+CI in an extractable form (e.g. a bare percentage with no denominator). This outcome is NOT absent — it is reported-but-not-poolable from the committed source; full-text acquisition would recover the countable form.
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 204 of 232 — docs/reviews/spironolactone-hfref-mortality/index.html — DECLARED ABSENT</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `8124911ae094726bb85f9fe8d1f2efb2a69ffccc1951b6caa3e030a638175182`.

Lost full text:

```text
DECLARED ABSENT. REPORTED but not extractable as a pooled value: 10471456 mention this outcome in the committed abstract, but without arm counts or an effect+CI in an extractable form (e.g. a bare percentage with no denominator). This outcome is NOT absent — it is reported-but-not-poolable from the committed source; full-text acquisition would recover the countable form.
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 205 of 232 — docs/reviews/spironolactone-hfref-mortality/index.html — Randomised-contrast disclosure</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `6fb533d581f68da392afcc89bcaf1ec0b6f1ebdcb59a421d831aebae1c466f92`.

Lost full text:

```text
Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 1 of 3 pooled trials have a registry-confirmed contrast (the intervention of interest differs across arms). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 21073363 contrast unverified — no registry arm data — 28824029 randomised contrast verified eplerenone 10471456 unverified_no_registry_match —
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 206 of 232 — docs/reviews/spironolactone-hfref-mortality/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `1557cc75bdd3c3e88e8efdcdfc7172ccce312164d8db9240c5a5240b75bdf0e5`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 1 of 1 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 2 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 21073363 industry abstract only ild symptoms. (Funded by Pfizer; ClinicalTrials.gov number, NCT00232180.). PMID 10471456 not stated (abstract only — full text not retrieved) abstract only PMID 28824029 not stated (abstract only — full text not retrieved) abstract only
```

Candidate 1 of 1; SHA-256 `8ef438c31875addb16df0f843a7de52e27eb676a741c8bf02e5c28949404921f`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 1 of 1 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 21073363 industry — abstract abstract : (Funded by Pfizer; ClinicalTrials.gov number, NCT00232180.). PMID 28824029 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 10471456 not stated (abstract only - full text not retrieved) — abstract abstract :
```

</details>

<details><summary>Pair 207 of 232 — docs/reviews/spironolactone-hfref-mortality/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `a20410a071d279f8c5f0d4f2524c309a86be39ca53864329abebb24238d6d882`.

Lost full text:

```text
Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 2 assessed trial(s) at high risk; fewer than half at 'some concerns'; risk-of-bias signal available for only 2 of 3 pooled trials (registry-derived), so the rating is capped Inconsistency −1 tau^2=0.13998; prediction interval [0.1276, 5.9118] is >=2x the CI width -> real heterogeneity Imprecision −1 95% CI [0.3062, 2.4635]; crosses the null AND is compatible with an appreciable benefit (<=0.75) and an appreciable harm (>=1.25) -> imprecise (the estimate is consistent with both no effect and an appreciable effect) Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED registry census (13 of ~43 completed unpublished, 30%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `5a138c6f7d212e00800cd026313528ce25cd7d824fc7eb31d8f3c29834552067`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 0; migration state (unbound_legacy, pooled and counted separately) 1 [PMID 28824029]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 10471456 UNKNOWN (REGISTRY_PARENT_UNRESOLVED); PMID 21073363 INELIGIBLE. in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 208 of 232 — docs/reviews/statins-primary-prevention-elderly/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `c7908c00581b2df72f9c8d1fca625d2e52fb5dcc4935a93923f4d8f461e641b8`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:30251369, NCT00000542; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `3d9922802fda9e7c6b687893a4b6a87e4cd901518b238fe183efca753f13fce2`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:20404379, PMID:30251369, NCT00000542; the completeness claim cannot be current
```

</details>

<details><summary>Pair 209 of 232 — docs/reviews/statins-primary-prevention-elderly/index.html — Registered pooled CI REFUSED at k=2</summary>

Source ref: `38c04411`; lost SHA-256: `abe7679264593e3bc2f7f1daf7ccfdf7133247cf2c37fcc83a6f4fbb9461b1d4`.

Lost full text:

```text
Registered pooled CI REFUSED at k=2. Registered PM/HKSJ uses t(1)=12.71 at k=2; the interval is not served as a pooled confidence interval because a single degree of freedom is not reliable here. The point estimate may be displayed, but no pooled significance/null-crossing claim is emitted.
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `4a252747ba3444e0c69453cc5c3635a9dae1b8811675db665a4b3c2b38cccd05`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 0; migration state (unbound_legacy, pooled and counted separately) 1 [PMID 42670961]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 20404379 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 210 of 232 — docs/reviews/statins-primary-prevention-elderly/index.html — Parser-confirmed contrast disclosure</summary>

Source ref: `38c04411`; lost SHA-256: `5aea12d118ec4c38f5d96489133eb6d5e686086e86b8e483de463862fdef63f6`.

Lost full text:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 1 of 2 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 42670961 parser-confirmed contrast atorvastatin 20404379 unverified_no_registry_match —
```

Candidate 1 of 1; SHA-256 `a76935811b5d09344e5abd0978dd565fa178435ac137cc25cb99e597edb85404`:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 1 of 1 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 42670961 parser-confirmed contrast atorvastatin
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 211 of 232 — docs/reviews/statins-primary-prevention-elderly/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `26fc49f9685a5367bf10f03f5eb60d58d686febbe7d328013c48420be6ac1015`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=2 of 2)
```

Candidate 1 of 1; SHA-256 `907e96459f0676ed291eafe578d7ed148d3184fa1b8274d074077cc53eadf371`:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=1 of 1)
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `4a252747ba3444e0c69453cc5c3635a9dae1b8811675db665a4b3c2b38cccd05`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 0; migration state (unbound_legacy, pooled and counted separately) 1 [PMID 42670961]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 20404379 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 212 of 232 — docs/reviews/statins-primary-prevention-elderly/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `884241f5d2e996f74bd0ea65421dcc23def676a1b707f9ac6294932556f07fa8`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision NOT_ASSESSABLE (NOT ASSESSED) 95% CI [None, None]; missing/insufficient: valid confidence interval; served pooled CI (refused); clinical threshold / MID with basis; information-size assessment with adequacy and basis | counted as ONE conservative downgrade pending human judgement (a check that could not run cannot raise certainty) Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (33 of ~97 completed unpublished, 34%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

Candidate 1 of 1; SHA-256 `b4091a91fd3f7c9d96a3d6e5b41232df9a21ff7ca20698828cc4b28f7defeb22`:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.61, 0.82]; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (33 of ~97 completed unpublished, 34%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `4a252747ba3444e0c69453cc5c3635a9dae1b8811675db665a4b3c2b38cccd05`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 0; migration state (unbound_legacy, pooled and counted separately) 1 [PMID 42670961]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 20404379 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 213 of 232 — docs/reviews/statins-primary-prevention-elderly/index.html — No checkable pooled claim</summary>

Source ref: `38c04411`; lost SHA-256: `4e655fe3ed1a86b2fbbb60e04236c8591d430c63637eab4156e3da1157a1f6ce`.

Lost full text:

```text
No checkable pooled claim (Claims checked: 0). Nothing was pooled on this page, so the canonical-claim contradiction gate has nothing to check here — this is a limitation, not a clean result.
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `4a252747ba3444e0c69453cc5c3635a9dae1b8811675db665a4b3c2b38cccd05`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 0; migration state (unbound_legacy, pooled and counted separately) 1 [PMID 42670961]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 20404379 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 214 of 232 — docs/reviews/statins-primary-prevention-elderly/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `b4ea3cbda3f23aa8f384a090de5c3193b13727382d37ca785147deaf6fb97c2d`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: 30251369, 28531241, NIA-Plaque · NCT00127218; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `3d9922802fda9e7c6b687893a4b6a87e4cd901518b238fe183efca753f13fce2`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (TITLE_SEEDED_RETRIEVAL): We retract any claim of a registry-first or systematic search for this topic. screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:20404379, PMID:30251369, NCT00000542; the completeness claim cannot be current
```

</details>

<details><summary>Pair 215 of 232 — docs/reviews/statins-primary-prevention-elderly/index.html — Randomised-contrast disclosure</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `c04bac3cfdc3fac6d7b3272a1dd7a2929d8447bc1a0852c2a38da02eeba7dd5b`.

Lost full text:

```text
Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 1 of 2 pooled trials have a registry-confirmed contrast (the intervention of interest differs across arms). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 42670961 randomised contrast verified atorvastatin 20404379 unverified_no_registry_match —
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 216 of 232 — docs/reviews/statins-primary-prevention-elderly/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `1b61824a331cba7ed7af28c78c2e1e32f08a54957ed61b788a77d0ea6495dbb8`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 2 of 2 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=2, HR 0.6803 [0.2897, 1.5975] Low risk of bias only k=2, HR 0.6803 [0.2897, 1.5975] (fewer trials than the full pool — see coverage)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `4a252747ba3444e0c69453cc5c3635a9dae1b8811675db665a4b3c2b38cccd05`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 0; migration state (unbound_legacy, pooled and counted separately) 1 [PMID 42670961]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 20404379 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 217 of 232 — docs/reviews/statins-primary-prevention-elderly/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `e49ac2b8042d3c0330eac88d67e2accc7128131e64a79ea69ad81323e3b054d1`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 2 assessed trial(s) at high risk; fewer than half at 'some concerns' Inconsistency not downgraded tau^2=0.0 (no between-study heterogeneity detected) Imprecision −1 95% CI [0.2897, 1.5975]; crosses the null AND is compatible with an appreciable benefit (<=0.75) and an appreciable harm (>=1.25) -> imprecise (the estimate is consistent with both no effect and an appreciable effect) Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED registry census (33 of ~97 completed unpublished, 34%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `4a252747ba3444e0c69453cc5c3635a9dae1b8811675db665a4b3c2b38cccd05`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 1: admissible 0; migration state (unbound_legacy, pooled and counted separately) 1 [PMID 42670961]; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 20404379 UNKNOWN (REGISTRY_PARENT_UNRESOLVED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 218 of 232 — docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html — STALE</summary>

Source ref: `38c04411`; lost SHA-256: `f80c42fa98810d722188b57916e308dc08e0ca6424be5f7a0e0f33c26ea64119`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (PMID_ENUMERATION_explicit): search.retrieval.enumeration_only=true; no discovery-capable concept source ran screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: PMID:17980250; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `a5cb7d472e4daea2c7c5ba6e7e07efd457812a4ababa0d0ad06962538bed0d6d`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (PMID_ENUMERATION_explicit): search.retrieval.enumeration_only=true; no discovery-capable concept source ran screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT00391872, PMID:17980250, PHILO; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 219 of 232 — docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html — Pooled result REFUSED</summary>

Source ref: `38c04411`; lost SHA-256: `9ef69e69751e9204228540e8ceb321bcbb060cbc3e600e93d328ad34faddf773`.

Lost full text:

```text
Pooled result REFUSED (k=2 direction conflict). k=2 pooled row refused because point estimates are on opposite sides of the null At k=2, if point estimates are on opposite sides of the null or trial CIs do not overlap, no pooled row is served. A k=1 anchor is shown only when it is explicitly pre-named in the topic configuration/protocol metadata; otherwise both trials are shown only as named individual results. The invalid pooled row is quarantined for audit only: 1.05 (0.03-33.89), tau^2=0.12171, I^2=77.7%. STALE: pooled membership known incomplete (1 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Honest k=1 anchor: PLATO HR 0.84 (95% CI 0.77-0.92). Protocol metadata pre-names PLATO (PMID 19717846) as the anchor publication; the k=2 direction-conflict rule does not choose an anchor by effect size. Named remainder(s), not pooled: PHILO: HR 1.47 (95% CI 0.88-2.44)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `c3bf077f7674e786956bf59ce3ef8725eb1e8e21e82c40f8740089f4f486917e`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 19717846 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 26376600 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 220 of 232 — docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `38c04411`; lost SHA-256: `32121c743ebc6795e5e537214229b3c77b608310e15ef5481f21b9130b54e57d`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 0 of 0 known (3 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 19717846 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 26376600 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 17980250 not stated (abstract only - full text not retrieved) — abstract abstract :
```

Candidate 1 of 1; SHA-256 `638dd0cd80803fb43ef180f43110a20eb7d9244f202b5a33ad9b561329ba02f7`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 0 of 0 known (3 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 17980250 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 19717846 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 26376600 not stated (abstract only - full text not retrieved) — abstract abstract :
```

</details>

<details><summary>Pair 221 of 232 — docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html — Does the result survive dropping the tri</summary>

Source ref: `38c04411`; lost SHA-256: `fd5d9339e4cec272f0d19d808c4ff57719dceaacda50c2fe63752a188ee7f460`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? Not computed: the primary pooled row is REFUSED (DIRECTION_CONFLICT_K2), so there is no pooled estimate to re-pool by risk-of-bias stratum. The per-trial rows and their risk-of-bias ratings are shown above; a stratified re-pool of a refused pool would be a number about nothing.
```

Candidate 1 of 1; SHA-256 `f7f6eb8ef26dd186392711f9e4a855ef2943d9b059b983abfcf39544728ced99`:

```text
Does the result survive dropping the trials that are not low risk of bias? Not computed (PRIMARY_ABSENT): the primary outcome has no pooled result (present = False). The per-trial rows and their risk-of-bias ratings are shown above; the omission is recorded in the review object as rob_sensitivity_omitted , not left silent.
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `c3bf077f7674e786956bf59ce3ef8725eb1e8e21e82c40f8740089f4f486917e`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 19717846 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 26376600 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 222 of 232 — docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `3f0fb65c7c5c69d0d006468ae8848cdc32f71f13b20d38c27cbbf7230f7e8b63`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (1 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. | counted as ONE conservative downgrade pending human judgement (a check that could not run cannot raise certainty) Imprecision NOT_ASSESSABLE (NOT ASSESSED) 95% CI [None, None]; missing/insufficient: valid confidence interval; served pooled CI (refused); clinical threshold / MID with basis; information-size assessment with adequacy and basis | counted as ONE conservative downgrade pending human judgement (a check that could not run cannot raise certainty) Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (25 of ~99 completed unpublished, 25%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `c3bf077f7674e786956bf59ce3ef8725eb1e8e21e82c40f8740089f4f486917e`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 19717846 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 26376600 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 223 of 232 — docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html — STALE</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `f7e568ab1db57539ab2f705d224dda0ddc35edad6073035581c7d957b83b0600`.

Lost full text:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: 17980250; the completeness claim cannot be current
```

Candidate 1 of 1; SHA-256 `a5cb7d472e4daea2c7c5ba6e7e07efd457812a4ababa0d0ad06962538bed0d6d`:

```text
STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate: no genuine executed concept search (PMID_ENUMERATION_explicit): search.retrieval.enumeration_only=true; no discovery-capable concept source ran screened-in (decision=include) but not pooled in any outcome — eligible trials the pool does not contain: NCT00391872, PMID:17980250, PHILO; the completeness claim cannot be current no outcome or declared strand produced a pooled claim — the canonical-claim gate cannot fire here, so a page with the weakest evidence would otherwise show the cleanest gate output; treated as a limitation, not a pass
```

</details>

<details><summary>Pair 224 of 232 — docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html — Funding / conflict-of-interest disclosur</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `4b332ea83fea8621ad8f08b843ffcfb5a6456a1539827fc5f4700d9e4ea2df4f`.

Lost full text:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from a verbatim statement in the committed source (full text preferred, abstract fallback), including an industry drug-supply tie in an otherwise independently funded trial: 0 of 0 known (2 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 2 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Scanned Verbatim statement PMID 19717846 not stated (abstract only — full text not retrieved) abstract only PMID 26376600 not stated (abstract only — full text not retrieved) abstract only
```

Candidate 1 of 1; SHA-256 `638dd0cd80803fb43ef180f43110a20eb7d9244f202b5a33ad9b561329ba02f7`:

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 0 of 0 known (3 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred. Trial Funding Sponsors / roles Scanned Source evidence PMID 17980250 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 19717846 not stated (abstract only - full text not retrieved) — abstract abstract : PMID 26376600 not stated (abstract only - full text not retrieved) — abstract abstract :
```

</details>

<details><summary>Pair 225 of 232 — docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `35299e230bcbee6aee55bf7259d56deae3c7966fbcf86977f1661a0a378cc2a9`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 1 of 2 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=2, HR 1.0479 [0.0324, 33.8921] Low risk of bias only k=1, HR 0.84 [0.7685, 0.9182]
```

Candidate 1 of 1; SHA-256 `f7f6eb8ef26dd186392711f9e4a855ef2943d9b059b983abfcf39544728ced99`:

```text
Does the result survive dropping the trials that are not low risk of bias? Not computed (PRIMARY_ABSENT): the primary outcome has no pooled result (present = False). The per-trial rows and their risk-of-bias ratings are shown above; the omission is recorded in the review object as rob_sensitivity_omitted , not left silent.
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `c3bf077f7674e786956bf59ce3ef8725eb1e8e21e82c40f8740089f4f486917e`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 19717846 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 26376600 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 226 of 232 — docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `c3fd688cd9c199c13ff366e0812df59617cd1cd51a0c62f409f3ee3598b7f98e`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias not downgraded none of the 1 assessed trial(s) at high risk; fewer than half at 'some concerns'; risk-of-bias signal available for only 1 of 2 pooled trials (registry-derived), so the rating is capped Inconsistency not downgraded tau^2=0.12171 Imprecision −1 95% CI [0.0324, 33.8921]; crosses the null AND is compatible with an appreciable benefit (<=0.75) and an appreciable harm (>=1.25) -> imprecise (the estimate is consistent with both no effect and an appreciable effect) Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED registry census (25 of ~99 completed unpublished, 25%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `c3bf077f7674e786956bf59ce3ef8725eb1e8e21e82c40f8740089f4f486917e`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 2: PMID 19717846 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN); PMID 26376600 UNKNOWN (INTERVENTION_CONTRAST_NOT_PROVEN). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 227 of 232 — docs/reviews/tocilizumab-covid19-mortality/index.html — UNRENDERABLE stale contrast block</summary>

Source ref: `38c04411`; lost SHA-256: `592b5dcaca3ecf4fdd19dace2b181f2c7a471a047350e1717621c2826b31c4ff`.

Lost full text:

```text
UNRENDERABLE stale contrast block. cached arm-contrast membership named trials not in the current consumed pool; current pooled trial ids: 33933206; suppressed stale ids: 33332779, 33631066.
```

No same-heading new candidate on this page.

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 228 of 232 — docs/reviews/tocilizumab-covid19-mortality/index.html — Parser-confirmed contrast disclosure</summary>

Source ref: `38c04411`; lost SHA-256: `014e5a108bc7fb6f69af37cf3afb54fdcabb0beecbbf8753e139d89cd6a513d2`.

Lost full text:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 1 of 1 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 33933206 parser-confirmed contrast anakinra; aspirin; azithromycin; baloxavir marboxil; baricitinib; colchicine; convalescent plasma; corticosteroid; corticosteroids (dexamethasone); dimethyl fumarate; empagliflozin; high dose corticosteroid; hydroxychloroquine; immunoglobulin; lopinavir-ritonavir; molnupiravir; oseltamivir; paxlovid; sotrovimab; synthetic neutralising antibodies; tocilizumab
```

Candidate 1 of 1; SHA-256 `63d940b63d0cfa31ffc7c78de20585bdb79e5268e09b742a3d5ade69c2db7b70`:

```text
Parser-confirmed contrast disclosure (per pooled trial, from the AACT arm-label parser - disclosed, not an adjustment). This measures the parser, not the trial. Eligibility should test what actually DIFFERS between the randomised arms, not the mere presence of the drug word: a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same agent, randomising a different drug) is not a randomised comparison of it. For each pooled trial the randomised contrast is reconstructed from AACT design_groups + interventions : 3 of 3 pooled trials have a parser-confirmed contrast (the intervention of interest matched a differing coded arm). A trial with no registry arm data, or coded under a class label / development code we cannot machine-match, is shown as contrast unverified — a VISIBLE fail-open state, never silently treated as verified. Trial Contrast status Randomised difference 33332779 parser-confirmed contrast tocilizumab 33631066 parser-confirmed contrast tocilizumab (tcz) 33933206 parser-confirmed contrast anakinra; aspirin; azithromycin; baloxavir marboxil; baricitinib; colchicine; convalescent plasma; corticosteroid; corticosteroids (dexamethasone); dimethyl fumarate; empagliflozin; high dose corticosteroid; hydroxychloroquine; immunoglobulin; lopinavir-ritonavir; molnupiravir; oseltamivir; paxlovid; sotrovimab; synthetic neutralising antibodies; tocilizumab
```

UNEXPLAINED for class-wide acknowledgement; no replacement is authorized by this draft.

</details>

<details><summary>Pair 229 of 232 — docs/reviews/tocilizumab-covid19-mortality/index.html — RoB-restricted re-pool suppressed</summary>

Source ref: `38c04411`; lost SHA-256: `907e96459f0676ed291eafe578d7ed148d3184fa1b8274d074077cc53eadf371`.

Lost full text:

```text
RoB-restricted re-pool suppressed: formal RoB 2 not yet assessed; the machine-signal low-only set equals the full pool (k=1 of 1)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `8bb80dd1064b3bc70d8cb80cb635bbc9fac118e32382f01f738b7284a7e5429d`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 33933206 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 230 of 232 — docs/reviews/tocilizumab-covid19-mortality/index.html — GRADE provisional -- not yet fully asses</summary>

Source ref: `38c04411`; lost SHA-256: `4cdd86cf73df1e5da9bfa173b9d79d5670e4c5fcb035482ec19a47ed78fb6fbf`.

Lost full text:

```text
GRADE provisional -- not yet fully assessable (downgrade arithmetic not stated while a domain is unassessed). Unassessed domains: risk_of_bias, inconsistency, imprecision, publication_bias, indirectness; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias NOT_ASSESSABLE (NOT ASSESSED) FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below Inconsistency NOT_ASSESSABLE (NOT ASSESSED) not assessable: STALE: pooled membership known incomplete (11 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. Imprecision REQUIRES_JUDGEMENT (NOT ASSESSED) 95% CI [0.76, 0.94]; missing/insufficient: clinical threshold / MID with basis; information-size assessment with adequacy and basis Indirectness REQUIRES_JUDGEMENT (NOT ASSESSED) directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT_ASSESSABLE (NOT ASSESSED) registry census (20 of ~38 completed unpublished, 53%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `8bb80dd1064b3bc70d8cb80cb635bbc9fac118e32382f01f738b7284a7e5429d`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 33933206 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 231 of 232 — docs/reviews/tocilizumab-covid19-mortality/index.html — Does the result survive dropping the tri</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `f16e90d7d6310cdb9d636170fa9b5160948b9ed4d0d5fc380801531bb72dc82d`.

Lost full text:

```text
Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-bias stratum with the identical estimator. 1 of 1 pooled trials have a risk-of-bias rating; no pooled trial is rated high risk (the registry-derived assessment does not reach 'high'), so the standard drop-high sensitivity is inert and the informative stratum is low-only . An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials than the full pool reflects both risk of bias and assessment coverage — read the widened interval with that caveat, not as instability of the effect. Stratum Re-pooled estimate Full pool (all pooled trials) k=1, OR 0.83 [0.7285, 0.9456] Low risk of bias only NOT ESTIMABLE — no pooled trial qualifies as low risk of bias, so this stratum has no trials to re-pool (an empty subgroup is not agreement with the full pool)
```

Candidate 1 of 1; SHA-256 `f7f6eb8ef26dd186392711f9e4a855ef2943d9b059b983abfcf39544728ced99`:

```text
Does the result survive dropping the trials that are not low risk of bias? Not computed (PRIMARY_ABSENT): the primary outcome has no pooled result (present = False). The per-trial rows and their risk-of-bias ratings are shown above; the omission is recorded in the review object as rob_sensitivity_omitted , not left silent.
```

Draft-selected replacement heading `Admission at pooling`; SHA-256 `8bb80dd1064b3bc70d8cb80cb635bbc9fac118e32382f01f738b7284a7e5429d`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 33933206 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>

<details><summary>Pair 232 of 232 — docs/reviews/tocilizumab-covid19-mortality/index.html — Overall certainty</summary>

Source ref: `50f5a67b4fb19ada4716a0df6e6b68c2e4618304`; lost SHA-256: `f5fafd4d2f6b2c4d7c6cd44bed380029eed96d2f06707b0b8321289ed32b242c`.

Lost full text:

```text
Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this is a machine-derived certainty — risk of bias uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, so a formal human GRADE assessment may differ. Risk of bias, inconsistency, imprecision and publication bias are computed from committed fields; publication bias is assessed from the registry ghost census, not funnel-plot asymmetry (which is unreliable at our small k). Indirectness is left to human judgement (the PICO scope note states the directness) — this is a partial GRADE, honestly labelled. Domain Effect on certainty Basis Risk of bias −1 1 of 1 assessed trial(s) at 'some concerns' Inconsistency NOT ASSESSED single trial (k=1): between-study inconsistency is not estimable Imprecision not downgraded 95% CI [0.7285, 0.9456]; excludes the null with a reasonably tight interval -> precise; single trial — imprecision judged from the CI, not downgraded merely for k=1 Indirectness human judgement directness of population/intervention/comparator/outcome is a human judgement; not auto-rated (the scope note on the page states the PICO) Publication bias (registry-based) NOT ASSESSED registry census (20 of ~38 completed unpublished, 53%) was enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a contaminated denominator cannot be this PICO's publication-bias rate, so publication bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)
```

No same-heading new candidate on this page.

Draft-selected replacement heading `Admission at pooling`; SHA-256 `8bb80dd1064b3bc70d8cb80cb635bbc9fac118e32382f01f738b7284a7e5429d`:

```text
Admission at pooling (P5_family_eligible, P8_endpoint_bound). Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 0: admissible 0; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 1: PMID 33933206 UNKNOWN (ENTRY_POPULATION_NOT_ESTABLISHED). in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
```

</details>
