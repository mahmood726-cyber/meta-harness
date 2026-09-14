# Fix Ladder Evidence - 2026-09-14

**Fix state (orthogonal fields rule): LANDED / INTERNAL / INSTANCE / STALE** - generated from TRANCHE-fix-state-ladder; verified by Codex lane R (non-author) (internal_agent); evidence: docs/evidence/independent-verification-2-2026-09-14/01-fix-state-object-transitions.txt, docs/evidence/independent-verification-2-2026-09-14/README.md; stale dependencies: harness/fixstate.py, scripts/render_fix_ledger.py, tests/test_fixstate.py

| Entry # | Class | Proposed fix_state | File |
|---:|---|---|---|
| 1 | preregistration-vs-build-SHA + gate limb + 32-topic SHA audit + one-state across renderers | VERIFIED | [01-prereg-sha-state.txt](01-prereg-sha-state.txt) |
| 2 | substudy identifier carried through extraction/RoB/funding/GRADE | REPORTED | [02-substudy-carrier.txt](02-substudy-carrier.txt) |
| 3 | D3 not-assessed default + GRADE cap-below-high + low-risk NOT-ESTIMABLE + disclosure | VERIFIED | [03-d3-grade-cap.txt](03-d3-grade-cap.txt) |
| 4 | D5 semantic reconciliation | REPORTED | [04-d5-reconcile.txt](04-d5-reconcile.txt) |
| 5 | registered-estimand-wins-over-source | VERIFIED | [05-registered-estimand.txt](05-registered-estimand.txt) |
| 6 | IRR-mistyping (first-event/mortality rate ratio typed as person-time IRR) | VERIFIED | [06-irr-mistyping.txt](06-irr-mistyping.txt) |
| 7 | NOT_RUN may not justify an inaccessibility/paywall claim + gate limb | VERIFIED | [07-not-run-wording.txt](07-not-run-wording.txt) |
| 8 | INCOMPATIBLE fails closed + suppression-at-source + 224-artefact leak scan | VERIFIED | [08-incompatible-failclosed.txt](08-incompatible-failclosed.txt) |
| 9 | unknown never counted in a proportion denominator (funding) | VERIFIED | [09-unknown-denominator.txt](09-unknown-denominator.txt) |
| 10 | cross-module single source-state + no-two-modules-disagree gate limb | REPORTED | [10-cross-module-state.txt](10-cross-module-state.txt) |
| 11 | comparator-scope re-run across 32 | VERIFIED | [11-comparator-scope.txt](11-comparator-scope.txt) |
| 12 | effect-measure three-field type system | VERIFIED | [12-effect-measure.txt](12-effect-measure.txt) |
| 13 | atomic comparator extraction (COMPARATOR_RESULT_CONTEXT_MISMATCH) | VERIFIED | [13-atomic-comparator.txt](13-atomic-comparator.txt) |
| 14 | arm-contrast parser + randomised-contrast disclosure | VERIFIED | [14-arm-contrast.txt](14-arm-contrast.txt) |
| 15 | harms decoupled from extraction format + zero-event-is-data | VERIFIED | [15-harms-zero-event.txt](15-harms-zero-event.txt) |
| 16 | NCT->publication link layer + PUBLICATION_FOUND_NOT_EXTRACTED gate + verified subset of 33/67 | REPORTED | [16-nct-publication-layer.txt](16-nct-publication-layer.txt) |
| 17 | no exclusion on interval width or trial size | VERIFIED | [17-no-width-size-exclusion.txt](17-no-width-size-exclusion.txt) |
| 18 | claimed-entity-derived-from-pooled (outcome/intervention/population/drug-class) | REPORTED | [18-claimed-entity-derived.txt](18-claimed-entity-derived.txt) |
| 19 | heterogeneity narratives derived, not authored | VERIFIED | [19-heterogeneity-derived.txt](19-heterogeneity-derived.txt) |
| 20 | GRADE 'not rateable' extended to 'deferred to human' (not only 'missing') | VERIFIED | [20-grade-human-deferral.txt](20-grade-human-deferral.txt) |
| 21 | unit-of-analysis for cluster/crossover folded into suppression-at-source | VERIFIED | [21-unit-of-analysis.txt](21-unit-of-analysis.txt) |
| 22 | computational verification of every 'would not change' reassurance | REPORTED | [22-reassurance-verified.txt](22-reassurance-verified.txt) |
| 23 | why the reproduction census missed the BaSICS expected-failure | REPORTED | [23-basics-census.txt](23-basics-census.txt) |
| 24 | timepoint hierarchy + multi-window sweep | VERIFIED | [24-timepoint-window.txt](24-timepoint-window.txt) |
| 25 | comparator-predates-our-included-trials rule + sweep | REPORTED | [25-comparator-predates.txt](25-comparator-predates.txt) |
| 26 | domain-level screening + poison-token sweep + platform-trial census | REPORTED | [26-poison-platform.txt](26-poison-platform.txt) |
| 27 | exclusion_symmetry self-check | REPORTED | [27-exclusion-symmetry.txt](27-exclusion-symmetry.txt) |
| 28 | UNREGISTERED_EXCLUSION_CRITERION | REPORTED | [28-unregistered-exclusion.txt](28-unregistered-exclusion.txt) |
| 29 | PMID 40261382 (REMAP-CAP CAP report) into the search-rebuild test set as a confirmed true miss | REPORTED | [29-pmid-40261382.txt](29-pmid-40261382.txt) |
| 30 | new-classes-per-audit trend artefact | VERIFIED | [30-class-discovery.txt](30-class-discovery.txt) |
| 31 | OUTCOME_KEYWORD_SYNONYM_GAP (mortality<->death) silently drops an eligible trial | VERIFIED | [31-mortality-synonym.txt](31-mortality-synonym.txt) |
| 32 | ARM_DENOMINATOR_MISBINDING (near-equal arms) -- OWED denominator audit | VERIFIED | [32-arm-denominator.txt](32-arm-denominator.txt) |
| 33 | CANONICAL_CLAIM_OBJECT — one significance/null-crossing derivation per result; build fails on cross-surface contradiction | VERIFIED | [33-canonical-claim.txt](33-canonical-claim.txt) |
| 34 | INVALIDATION_PROPAGATION — one per-topic STALE flag from committed signals poisons every dependent output; corpus reports n of 32 STALE | VERIFIED | [34-invalidation.txt](34-invalidation.txt) |
| 35 | POOLING_COMPATIBILITY_KEY — explicit 6-dimension pooling contract per outcome + fail-closed backstop; unifies scattered guards | VERIFIED | [35-compatibility-key.txt](35-compatibility-key.txt) |
| 36 | ARMCONTRAST_INTO_SCREENING — randomised-contrast check moved from post-pool to eligibility; confirmed non-contrasts evicted (X-CONTRAST) | VERIFIED | [36-armcontrast-screening.txt](36-armcontrast-screening.txt) |
| 37 | TRIAL<->REPORT ENTITY MODEL — collapse secondary/duplicate reports to parent before counting (records != trials) | VERIFIED | [37-trial-report-model.txt](37-trial-report-model.txt) |
| 38 | PROTOCOL_COMPILER + CONFIG_EQUALITY — prose protocol vs executable config as TWO INDEPENDENT sources (defeats self-certification) | VERIFIED | [38-protocol-compiler.txt](38-protocol-compiler.txt) |
| 39 | OBJECT-DERIVED eligible_declared_absent predicate + no_checkable_claim + NEVER_CONSIDERED + identity crosswalk | VERIFIED | [39-object-derived-states.txt](39-object-derived-states.txt) |
| 40 | REPORTED vs HARNESS-RECONSTRUCTED derivation provenance on every pooled number | VERIFIED | [40-derivation-provenance.txt](40-derivation-provenance.txt) |
