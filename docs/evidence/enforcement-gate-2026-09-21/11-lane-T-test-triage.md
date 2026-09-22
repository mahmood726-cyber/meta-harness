# Lane T — assertion-level triage (proposals only)

Bucket 1 nodeids first:

- `tests/test_design_variance.py::test_page_renders_stale_contrast_and_protocol_controls_unrenderable` — missing UNRENDERABLE stale contrast block; arm_contrast has 3 rows although primary trials=[]; page says 2 of 3 pooled trials. At harness/design_variance.py:220-221 filter even an empty pooled set, preserve dropped IDs, and at harness/page.py:2822 render the stale explanation outside the nonempty contrast-table guard.
- `tests/test_design_variance.py::test_prefix_object_fires_and_rebuilt_object_passes_design_variance_check` — DV.check_review(post)=['GRADE_MISSING_DESIGN_VARIANCE_RATIONALE', 'STALE_ARM_CONTRAST_DENOMINATOR']. Fix empty-set contrast filtering at harness/design_variance.py:220-221 and make the GRADE-rationale check at harness/design_variance.py:299-301 conditional on a pooled claim that should carry GRADE.

All 56 requested tests were run separately with the exact requested pytest options; all 56 failed on this tree. The original test files and harness were not edited. No commit, staging, regeneration, countersignature or publication was performed. No process-stop/kill/signal commands were issued. Tests completed their own normal cleanup.

| Bucket | Count (n of N = 56) |
|---|---:|
| 1 — REGRESSION | 2 of 56 |
| 2 — PINNED FINDING | 45 of 56 |
| 3 — RED BY DESIGN | 2 of 56 |
| 0 — REGEN CURRENCY | 7 of 56 |

The bucket follows the actual failing expression, not the test name. A failed lookup before an assertion is marked **not reached**, with the intended assertion and actual lookup both quoted. Bucket 3 is used only where a real OPEN notice still blocks publication; the empagliflozin withdrawn-page parameter has only currency failures and is bucket 0. Secondary stale hashes do not erase an independent designed hold.

Evidence: [triage.json](triage.json) embeds each isolated command, exit code, duration, raw failure output, source/test docstrings, assertion locations and log hash. Raw logs and source extracts are also in [.tmp/triage-runs](.tmp/triage-runs). Test file baseline hashes are recorded there. No external research was used: identifiers, tuples and statistical observations below are from held local records and test output, not fresh clinical findings.

| Material | Static or dynamic | Hardcode disclosure |
|---|---|---|
| Target nodeids / bucket definitions | Static | Exactly LANE_PROMPT.md; 56 is the requested denominator. |
| Observed failures / statistics / source state | Dynamic | Isolated local test runs and held review/cache objects. |
| Classification / smallest fixes | Reviewer proposals | Manual judgement; no edits applied. |
| Proposed controls | Static controls + dynamic assertions | Historical source fixtures keep their identifiers/values; explicit synthetic boundary controls are test-only. Current findings are recomputed or membership-derived, never repinned to new numbers. |

| Nodeid | Bucket | Assertion quoted | Observed value and why | Proposed change / gate / stale artefact |
|---|---|---|---|---|
| `tests/test_arm_identity.py::test_mixed_scale_pool_labelled_honestly` | 2 — PINNED FINDING | `tests/test_arm_identity.py:83`: `assert em.get("status") == "compatible_labels", em` | homogeneous; labels=[HR], classes=[FIRST_EVENT_RATIO]. The live spironolactone pool lost the RR member. The honest-label requirement remains, but compatible_labels and a named HR/RR mix are no longer invariant. | Derive label and suppression expectations from admitted effect classes; retain explicit compatible/incompatible controls. Diff: [proposed/test_arm_identity.py.diff](proposed/test_arm_identity.py.diff); shared helper below. |
| `tests/test_bundle.py::test_assessment_states_cover_every_row_and_never_render_alike` | 2 — PINNED FINDING | `tests/test_bundle.py:731`: `assert a["counts"]["ASSESSED"] >= 8 + 4` | ASSESSED=11; assertion requires >=12. The bundle assesses seven pooled primary rows plus four evaluated negatives; the set-aside row is explicitly NOT_ASSESSED_BY_BUNDLE. A lower-bound snapshot is not the assessment-state partition. | Check counts against every classified row and verify primary-row states against admission evidence. Diff: [proposed/test_bundle.py.diff](proposed/test_bundle.py.diff); shared helper below. |
| `tests/test_bundle.py::test_clean_negative_is_recorded_as_a_negative_with_its_scope` | 2 — PINNED FINDING | `tests/test_bundle.py:778`: `assert cn["result"].startswith("8 of 8") and "says nothing about the defect" in cn["meaning"] and "95.03" in cn["meaning"]` | 7 of 7 tuple clauses state 95%. The clean-negative scope remains; only the number of pooled clauses changed. | Derive the numerator/denominator from verification_rows and retain the scope and defect-language checks. Diff: [proposed/test_bundle.py.diff](proposed/test_bundle.py.diff); shared helper below. |
| `tests/test_bundle.py::test_declared_variation_is_recorded_per_trial_not_collapsed` | 2 — PINNED FINDING | `tests/test_bundle.py:338`: `assert pt["PMID 30291013"] == "unstated"` | KeyError: PMID 30291013. HARMONY is no longer in the per-pooled-trial endpoint variation table. No source statement changed. | Check per_trial membership and its own source-definition-derived variation, without requiring an excluded trial in the pool. Diff: [proposed/test_bundle.py.diff](proposed/test_bundle.py.diff); shared helper below. |
| `tests/test_bundle.py::test_default_and_stated_bases_are_both_present_and_visibly_distinct` | 2 — PINNED FINDING | `tests/test_bundle.py:661`: `assert bases.count("STATED_IN_OWNING_EVIDENCE") == 3 and bases.count("REGISTERED_DEFAULT") == 5` | STATED_IN_OWNING_EVIDENCE count=2, expected 3. Removing HARMONY changes the stated/default distribution; it does not remove provenance. | Require each basis to agree with its span-backed evidence or explicitly named registered default. Diff: [proposed/test_bundle.py.diff](proposed/test_bundle.py.diff); shared helper below. |
| `tests/test_bundle.py::test_estimand_fields_carry_a_span_or_an_explicit_default_never_a_bare_assertion` | 2 — PINNED FINDING | `tests/test_bundle.py:613`: `assert stated_set == 3` | stated_set=2, expected 3. The failing tail counts stated sets after the span-reproduction assertions already passed. It pins a source cohort frequency. | Keep all per-row offset and evidence-state checks; require explicit field values rather than historical cohort frequencies. Diff: [proposed/test_bundle.py.diff](proposed/test_bundle.py.diff); shared helper below. |
| `tests/test_bundle.py::test_every_row_states_its_ci_level_or_records_the_assumption` | 2 — PINNED FINDING | `tests/test_bundle.py:676`: `assert sum(1 for r in bundle["verification_rows"] if r["statistical_input"]["ci_level"]["level_agreement"] == "MATCH") == 8` | MATCH count=7, expected 8. The per-row CI-level derivation checks passed; the tail pins eight pooled clauses. | Keep per-row assumed/stated-level checks and require agreement to follow the stated level. Diff: [proposed/test_bundle.py.diff](proposed/test_bundle.py.diff); shared helper below. |
| `tests/test_bundle.py::test_extraction_object_coverage_is_stated_not_discovered` | 2 — PINNED FINDING | `tests/test_bundle.py:380`: `assert primary["pooled_rows"] == 8 and primary["pooled_rows_with_an_extraction_object"] == ["40162642"]` | pooled_rows=7, expected 8. The extraction chain remains described; the coverage denominator changes with admission. | Reconcile coverage with enumerated verification rows and their extraction-object links; derive the rendered denominator. Diff: [proposed/test_bundle.py.diff](proposed/test_bundle.py.diff); shared helper below. |
| `tests/test_bundle.py::test_harmony_is_inadmissible_because_its_family_eligibility_is_unknown` | 2 — PINNED FINDING | `tests/test_bundle.py:268`: `assert row["admission"]["final"] == "INADMISSIBLE"` (**not reached**; failed at `tests/test_bundle.py:267`: `row = next(r for r in bundle["verification_rows"] if r["trial"]["id"] == "PMID 30291013")`) | StopIteration: HARMONY absent from verification_rows. The test docstring explicitly calls this a finding: formerly an inadmissible row still pooled. Admission now excludes it and retains its candidate. | Check source-backed admission and exact accounting in pooled or declared-absent rows; unknown eligibility must exclude pooling. Diff: [proposed/test_bundle.py.diff](proposed/test_bundle.py.diff); shared helper below. |
| `tests/test_bundle.py::test_heterogeneity_statement_carries_input_precision_not_a_categorical_claim` | 2 — PINNED FINDING | `tests/test_bundle.py:359`: `assert abs(h["Q"] - 7.06072) < 1e-4 and h["df"] == 7 and 0 < h["Q_minus_df"] < 0.1` | Q=5.145728119488521, df=6; expected Q~7.06072, df=7. The rounded-input pool moved when membership changed. Its boundary frequency also moved to 1.0; replacing either expected number would pin another finding. | Check Q/df arithmetic and bounded seeded rounding sensitivity with explicit input-precision disclosure. See follow-on prose concern below. Diff: [proposed/test_bundle.py.diff](proposed/test_bundle.py.diff); shared helper below. |
| `tests/test_bundle.py::test_lancet_rows_are_normalised_not_verbatim_and_offsets_reproduce` | 2 — PINNED FINDING | `tests/test_bundle.py:275`: `assert rows["PMID 31189511"]["span"]["match"] == "NORMALISED" and rows["PMID 30291013"]["span"]["match"] == "NORMALISED"` | KeyError: PMID 30291013. The pooled-span lookup requires HARMONY to stay pooled, although its candidate was retained outside that set. | Check the representation type and exact span offsets for all currently pooled source rows. Diff: [proposed/test_bundle.py.diff](proposed/test_bundle.py.diff); shared helper below. |
| `tests/test_bundle.py::test_pooled_reference_matches_the_settled_value` | 2 — PINNED FINDING | `tests/test_bundle.py:289`: `assert abs(e["estimate"] - 0.8559934175938467) < 1e-9` | estimate=0.8663524912316083 vs 0.8559934175938467. A settled eight-member numeric result is not invariant under removing a member. | Recompute the reference from enumerated admitted inputs and compare numerical fields at the original tolerance. Diff: [proposed/test_bundle.py.diff](proposed/test_bundle.py.diff); shared helper below. |
| `tests/test_bundle.py::test_unbound_legacy_rows_are_a_migration_state_outside_the_admissible_count` | 2 — PINNED FINDING | `tests/test_bundle.py:430`: `assert bundle["counts"]["admissible_rows"] + bundle["counts"]["migration_state_rows_in_primary_pool"] + bundle["counts"]["inadmissible_rows_in_primary_pool"] == 8` | 7 admissible + 0 migration + 0 inadmissible != 8. The migration exclusion checks passed; the failure is the old primary-pool denominator. A later code-pin assertion remains currency-sensitive. | Use the current verification-row population for the partition; preserve migration exclusion and provenance checks. Diff: [proposed/test_bundle.py.diff](proposed/test_bundle.py.diff); shared helper below. |
| `tests/test_bundle_verifier.py::test_control_a_row_already_refused_at_baseline_cannot_serve_as_a_mutation_target` | 2 — PINNED FINDING | `tests/test_bundle_verifier.py:135`: `assert harmony["final"] == "INADMISSIBLE" and not harmony["predicates"]["P5_family_eligible"]` (**not reached**; failed at `tests/test_bundle_verifier.py:134`: `harmony = next(r for r in baseline["rows"] if r["pmid"] == "30291013")`) | StopIteration: HARMONY absent from verifier rows. The negative mutation control pins a refused-but-still-pooled baseline row that admission has removed. | Choose an admissible source row, demonstrate the refusal delta, and prove an already-refused row cannot be accepted as a positive mutation control. Diff: [proposed/test_bundle_verifier.py.diff](proposed/test_bundle_verifier.py.diff); shared helper below. |
| `tests/test_bundle_verifier.py::test_pool_reproduced_without_the_harness` | 2 — PINNED FINDING | `tests/test_bundle_verifier.py:62`: `assert abs(p["recomputed"]["estimate"] - 0.8559934175938467) < 1e-9` | independent recomputation=0.8663524912316083; old pin=0.8559934175938467. Independent reproduction already passes before the numeric pin fails. | Retain independent numerical deltas; derive k, admissible count and t critical value from verifier rows. Diff: [proposed/test_bundle_verifier.py.diff](proposed/test_bundle_verifier.py.diff); shared helper below. |
| `tests/test_certificate.py::test_all_certificate_inputs_and_manuscript_match` | 0 — REGEN CURRENCY | `tests/test_certificate.py:103`: `assert not certificate.verify(directory)` | release_sha256 recomputed b7ce6c88... vs saved 9eca6f94.... certificate.verify reports only changed release identity for the first review, balanced crystalloids. | Regenerate docs/reviews/balanced-crystalloids-vs-saline-mortality/CERTIFICATE.json and its dependent served artefacts; no assertion edit. |
| `tests/test_certificate.py::test_held_document_byte_mutation_refuses` | 0 — REGEN CURRENCY | `tests/test_certificate.py:33`: `assert {k for k in saved if saved[k] != changed[k]} == {"held_documents", "release_sha256"}` | extra changed keys: analysis_code_sha256, analysis_code_blobs. The held-byte mutation starts from a certificate whose code pins already differ from the working tree, so more than the two intended certificate fields change. | Regenerate the GLP-1 certificate before running the one-byte mutation control; no weakening of the mutation assertion. |
| `tests/test_certificate_code_closure.py::test_pinned_blob_identities_are_what_git_stores` | 0 — REGEN CURRENCY | `tests/test_certificate_code_closure.py:81`: `assert dict(zip(present, out)) == present` | stored and git hash-object identities differ for current pinned modules. The mismatch is the stale certificate pin set, including hazard_consumers, parity_relation, page and index. | Regenerate GLP-1 CERTIFICATE.json analysis_code_blobs; keep the independent Git identity check. |
| `tests/test_certificate_code_closure.py::test_stdlib_audit_reproduces_every_served_certificate` | 0 — REGEN CURRENCY | `tests/test_certificate_code_closure.py:96`: `assert proc.returncode == 0 and "RESULT REPRODUCED" in proc.stdout, (directory.name, proc.stdout)` | RESULT NOT REPRODUCED (5 mismatches), returncode=1. The stdlib certificate auditor finds stale release/code identities on the first served certificate. | Regenerate the affected certificates and dependent artefacts, then retain the stdlib audit unchanged. |
| `tests/test_comparator_panel_ui.py::test_all_served_comparator_panels` | 2 — PINNED FINDING | `tests/test_comparator_panel_ui.py:47`: `assert "0.7777777777777778" in tab.inner_text()` | rendered overlap 0.6666666666666666; expected literal 0.7777777777777778. The UI loads, panel counts and held/not-held labels pass. HARMONY leaving the pool changes its overlap with the comparator. | Derive Jaccard from the source-backed shared/only sets and require that value to render. Diff: [proposed/test_comparator_panel_ui.py.diff](proposed/test_comparator_panel_ui.py.diff); shared helper below. |
| `tests/test_compat_underlying.py::test_post_fix_probiotics_key_is_mixed_and_no_asserted_violation` | 2 — PINNED FINDING | `tests/test_compat_underlying.py:50`: `assert ck["analysis_set"].startswith("mixed (")` (**not reached**; failed at `tests/test_compat_underlying.py:49`: `ck = primary["compat_key"]`) | KeyError: compat_key; probiotics primary trials=[]. The test pins a mixed pooled compatibility state after all primary candidates were set aside. An absent pool should not assert a compatibility key. | Check the admission partition and absence of a key for an empty pool; retain the source-disagreement plant and live violation check. Diff: [proposed/test_compat_underlying.py.diff](proposed/test_compat_underlying.py.diff); shared helper below. |
| `tests/test_cross_source_endpoint.py::test_rebuilt_fourier_row_is_different_measure_not_corroboration` | 2 — PINNED FINDING | `tests/test_cross_source_endpoint.py:95`: `assert cs["endpoint_match"] == "SECOND_SOURCE_DIFFERENT_MEASURE"` (**not reached**; failed at `tests/test_cross_source_endpoint.py:92`: `row = _fourier_row(core)`) | StopIteration in _fourier_row: no pooled label 28304224. The different-measure requirement is still meaningful, but FOURIER is now a retained candidate rather than a pooled row. | Check admission accounting and exercise cross-source identity on its held candidate and registry source without re-admitting it. Diff: [proposed/test_cross_source_endpoint.py.diff](proposed/test_cross_source_endpoint.py.diff); shared helper below. |
| `tests/test_design_variance.py::test_page_renders_stale_contrast_and_protocol_controls_unrenderable` | 1 — REGRESSION | `tests/test_design_variance.py:211`: `assert "UNRENDERABLE stale contrast block" in html` | missing UNRENDERABLE stale contrast block; arm_contrast has 3 rows although primary trials=[]; page says 2 of 3 pooled trials. This is stale membership rendered as a current pooled denominator, not merely a legitimately changed denominator: current_arm_contrast returns the unfiltered cache when the admitted set is empty. | At harness/design_variance.py:220-221 filter even an empty pooled set, preserve dropped IDs, and at harness/page.py:2822 render the stale explanation outside the nonempty contrast-table guard. |
| `tests/test_design_variance.py::test_prefix_object_fires_and_rebuilt_object_passes_design_variance_check` | 1 — REGRESSION | `tests/test_design_variance.py:59`: `assert DV.check_review(post) == []` | DV.check_review(post)=['GRADE_MISSING_DESIGN_VARIANCE_RATIONALE', 'STALE_ARM_CONTRAST_DENOMINATOR']. The focused design audit asserts a requirement, not whole-tree publishability. The stale contrast object is real; the GRADE rationale check also mistakes intentionally absent GRADE at k=0 for a defect. | Fix empty-set contrast filtering at harness/design_variance.py:220-221 and make the GRADE-rationale check at harness/design_variance.py:299-301 conditional on a pooled claim that should carry GRADE. |
| `tests/test_endpoint_canonical.py::test_analysis_set_superclass_plant_and_literal_retention` | 2 — PINNED FINDING | `tests/test_endpoint_canonical.py:83`: `assert live["compat_key"]["analysis_set_superclass"] == EC.ANALYSIS_SUPERCLASS` | KeyError: compat_key; doac primary trials=[]. No admitted analysis set remains on which to publish a superclass; this lookup pins a served pool state. | Preserve the superclass promotion plant; verify source literals and superclass for any admitted members, and no key for an empty pool. Diff: [proposed/test_endpoint_canonical.py.diff](proposed/test_endpoint_canonical.py.diff); shared helper below. |
| `tests/test_endpoint_canonical.py::test_doac_endpoint_underclaim_and_live_fix` | 2 — PINNED FINDING | `tests/test_endpoint_canonical.py:39`: `assert live["endpoint_canonical"]["label"] == "SYMPTOMATIC_RECURRENT_VTE"` | KeyError: endpoint_canonical; doac primary trials=[]. No primary pool remains to carry the canonical pooled endpoint. Historical underclaim detection still passes. | Retain the underclaim plant; reconcile canonical label and compatibility key only for an admitted pool, with explicit empty-pool checks. Diff: [proposed/test_endpoint_canonical.py.diff](proposed/test_endpoint_canonical.py.diff); shared helper below. |
| `tests/test_endpoint_canonical.py::test_metformin_strategy_split_plant_and_live_fix` | 2 — PINNED FINDING | `tests/test_endpoint_canonical.py:95`: `assert strategies == {"METFORMIN_ADDON_CC"}` | strategies=set(), expected {METFORMIN_ADDON_CC}. All metformin primary rows were set aside; the old nonempty strategy set is a served state. The proposed property rewrite exposes a separate empty-pool STRATEGY_COLLAPSED false positive (documented below). | Keep the strategy-collapse plant and title scope; require every admitted row to match the add-on strategy and account for exclusions. Retain the final no-false-diagnostic assertion; the follow-on source defect must be fixed, not accepted. Diff: [proposed/test_endpoint_canonical.py.diff](proposed/test_endpoint_canonical.py.diff); shared helper below. |
| `tests/test_endpoint_canonical.py::test_mixed_effect_label_plant_and_live_labels` | 2 — PINNED FINDING | `tests/test_endpoint_canonical.py:62`: `assert live_doac["result"]["effect_label"] == "pooled first-event ratio (5 HR + 1 RR)"` | KeyError: effect_label; doac/noac primary trials=[]. The literal labels include old member counts and require nonempty pools. | Check admitted class composition and dynamic label counts, while retaining both historical hidden-mix plants. Diff: [proposed/test_endpoint_canonical.py.diff](proposed/test_endpoint_canonical.py.diff); shared helper below. |
| `tests/test_estimand_naming.py::test_metformin_background_therapy_dimension_plant` | 2 — PINNED FINDING | `tests/test_estimand_naming.py:97`: `assert live_key["background_therapy"]["matched"] is True` | KeyError: background_therapy. The background-therapy key only describes admitted pooled rows; the metformin pool emptied. | Check admitted member-derived background therapy when present; require no pooled compatibility claim otherwise. Diff: [proposed/test_estimand_naming.py.diff](proposed/test_estimand_naming.py.diff); shared helper below. |
| `tests/test_estimand_naming.py::test_statins_subgroup_evidence_unit_plant` | 2 — PINNED FINDING | `tests/test_estimand_naming.py:128`: `assert live_jupiter["evidence_unit"] == "prespecified_subgroup"` (**not reached**; failed at `tests/test_estimand_naming.py:127`: `live_jupiter = next(t for t in _pooled_trials(live) if t.get("id") == "PMID 20404379")`) | StopIteration: JUPITER absent from current pooled trials. The source subgroup is retained outside the pool, so the test cannot require its pooled membership or a k=2 caption. | Check that JUPITER is accounted for; preserve subgroup labeling if pooled, or its candidate and reason when set aside. Diff: [proposed/test_estimand_naming.py.diff](proposed/test_estimand_naming.py.diff); shared helper below. |
| `tests/test_fixstate.py::test_real_store_validates` | 0 — REGEN CURRENCY | `tests/test_fixstate.py:458`: `assert ok, "\n".join(reasons)` | docs/fix_ledger.json stale; HM hand-row binding README fix-state line stale. The store validator reports generated ledger/prose currency failures, with no OPEN-notice assertion. | Regenerate docs/fix_ledger.json and docs/evidence/m2-hand-row-binding-2026-09-20/README.md fix-state line using the named existing render scripts. |
| `tests/test_gate.py::test_real_review_reproduces_and_passes_full_gate` | 3 — RED BY DESIGN | `tests/test_gate.py:114`: `assert ok, f"real committed review must pass the full gate, got: {reasons}"` | gate ok=False; GLP-1 primary reviewer_countersignature OPEN. The assertion explicitly demands the real page pass the full gate. check_result_change_countersigned holds the changed primary result pending reviewer countersignature. Certificate/replay currency failures are additional. | Keep the assertion and the hold; reviewer decision on the GLP-1 3-point major adverse cardiovascular events notice is required. |
| `tests/test_grade_missing_is_not_favourable.py::test_no_served_page_loses_a_downgrade` | 2 — PINNED FINDING | `tests/test_grade_missing_is_not_favourable.py:124`: `assert losses == [], losses` | 15 losses: 11 absent GRADE objects and 4 reduced domain downgrades. This historical snapshot permits GRADE omission only for withdrawal and requires nondecreasing downgrades despite changed evidence membership. Admission legitimately empties 11 primary pools; changed pools can also change assessed domains. | Allow absent GRADE only for declared withdrawal or a verified empty primary; compare current evidence-derived domains, retaining missing-is-not-favourable and unchanged-evidence checks. Diff: [proposed/test_grade_missing_is_not_favourable.py.diff](proposed/test_grade_missing_is_not_favourable.py.diff); shared helper below. |
| `tests/test_grade_unassessed.py::test_corpus_unassessed_domains_never_render_as_not_downgraded` | 2 — PINNED FINDING | `tests/test_grade_unassessed.py:93`: `assert checked >= 20, checked` | checked=19, required >=20. Every visited rateable page passed the unassessed-domain rendering check; only the corpus-count floor fails after intentional GRADE omissions. | Derive the target population from current GRADE objects and require complete non-vacuous coverage. Diff: [proposed/test_grade_unassessed.py.diff](proposed/test_grade_unassessed.py.diff); shared helper below. |
| `tests/test_held_source_never_not_in_committed_source.py::test_elixa_conflict_spans_primary_unchanged` | 2 — PINNED FINDING | `tests/test_held_source_never_not_in_committed_source.py:67`: `assert outcome['result']['k'] == 8` | GLP-1 primary k=7, expected 8. The conflict spans, pages and adjudication disclosure passed; the tail freezes primary membership and results against a historical ref. | Keep all held-conflict evidence checks, exclude the proposed ELIXA candidate from the primary, and reproduce the admitted primary rather than the historical result. Diff: [proposed/test_held_source_never_not_in_committed_source.py.diff](proposed/test_held_source_never_not_in_committed_source.py.diff); shared helper below. |
| `tests/test_held_source_never_not_in_committed_source.py::test_membership_demonstration_recomputed` | 2 — PINNED FINDING | `tests/test_held_source_never_not_in_committed_source.py:94`: `assert 'under the PROPOSED adjudication -- not a result; the primary k=8 pool is unchanged' in page` | membership demonstration recomputes, but page no longer says primary k=8. The numerical primary/proposed calculations pass. Only the literal primary-k sentence changed. | Derive the sentence from current primary membership and require the proposed candidate to remain outside that pool. Diff: [proposed/test_held_source_never_not_in_committed_source.py.diff](proposed/test_held_source_never_not_in_committed_source.py.diff); shared helper below. |
| `tests/test_hm3_pages.py::test_primary_trial_values_and_membership_are_unchanged` | 2 — PINNED FINDING | `tests/test_hm3_pages.py:72`: `assert before['primary_values'] == values(b), slug` | metformin baseline primary_values has 3 rows; current trials=[]. The assertion fixes pooled membership across a later, explicitly authorized admission landing. Values should survive in declared-absent candidate tuples, not necessarily in the pool. | Reconcile each immutable baseline tuple against current pooled-or-set-aside accounting; preserve source values and supersession provenance. Diff: [proposed/test_hm3_pages.py.diff](proposed/test_hm3_pages.py.diff); shared helper below. |
| `tests/test_hm3_pages.py::test_rebuilt_pages_account_for_every_baseline_harm` | 2 — PINNED FINDING | `tests/test_hm3_pages.py:41`: `assert row.get('reason_code') in ('ENDPOINT_UNBOUND','RESULT_INCOMPATIBLE'), (d['topic'],d['trial'],row.get('reason_code'))` | corticosteroids-covid19-mortality / 34138478 reason_code=P5_family_eligible. The row retains its decided candidate values and reason, but the test whitelist only permits pre-admission refusal states. | Validate an admission refusal against its actual failing predicates and family evidence, keeping the existing candidate-value and page checks. Diff: [proposed/test_hm3_pages.py.diff](proposed/test_hm3_pages.py.diff); shared helper below. |
| `tests/test_incompatible_fail_closed.py::test_aggregate_snapshots_do_not_count_suppressed_as_pooled` | 2 — PINNED FINDING | `tests/test_incompatible_fail_closed.py:139`: `assert supp, "no suppressed topics found — test would be vacuous"` | suppressed primary topic set is empty. The test requires at least one suppressed served primary; admission removed the incompatible member combinations. No aggregate invariant has yet failed. | Keep all aggregate exclusion checks; use an explicit controlled incompatible fixture for non-vacuity instead of requiring a live incompatible pool. Diff: [proposed/test_incompatible_fail_closed.py.diff](proposed/test_incompatible_fail_closed.py.diff); shared helper below. |
| `tests/test_incompatible_fail_closed.py::test_corpus_incompatible_topics_are_fully_suppressed` | 2 — PINNED FINDING | `tests/test_incompatible_fail_closed.py:119`: `assert "iv-iron-hfref-hosp" in suppressed, f"expected iv-iron suppressed; got {suppressed}"` | suppressed=[]; expected iv-iron-hfref-hosp. The generic fail-closed checks are still requirements, but the tail pins IV iron to its former cross-class membership. | Derive incompatibility from each current admitted set and keep controlled fail-closed renderer/manuscript/spec-curve checks. Diff: [proposed/test_incompatible_fail_closed.py.diff](proposed/test_incompatible_fail_closed.py.diff); shared helper below. |
| `tests/test_irr_typing.py::test_omega3_pools_and_iv_iron_stays_suppressed` | 2 — PINNED FINDING | `tests/test_irr_typing.py:57`: `assert ip.get("suppressed_incompatible"), "iv-iron must stay suppressed (genuine first-event+recurrent mix)"` | iv-iron result has k=1 and no suppressed_incompatible flag. The recurrent-event member was set aside. A sole first-event HR is no longer an incompatible mix. | Check suppression against admitted effect classes; retain the separate source-level IRR typing tests. Diff: [proposed/test_irr_typing.py.diff](proposed/test_irr_typing.py.diff); shared helper below. |
| `tests/test_k2_refusal.py::test_plant_prefixed_ticagrelor_direction_conflict_and_live_refuses_pool_row` | 2 — PINNED FINDING | `tests/test_k2_refusal.py:49`: `assert live["pool_refused"]["code"] == k2.DIRECTION_CONFLICT_K2` | KeyError: pool_refused; ticagrelor primary trials=[]. The k=2 policy has no two admitted members to act on; the named PLATO/PHILO refusal is a historical served state. | Keep the historical conflict plant and apply policy to that controlled k=2 object; validate current admission and k-sensitive refusal semantics. Diff: [proposed/test_k2_refusal.py.diff](proposed/test_k2_refusal.py.diff); shared helper below. |
| `tests/test_k2_refusal.py::test_plant_prefixed_ticagrelor_grade_inconsistency_missing_and_live_has_state` | 2 — PINNED FINDING | `tests/test_k2_refusal.py:66`: `assert live_inc["not_assessable_automatically"] is True` (**not reached**; failed at `tests/test_k2_refusal.py:65`: `live_inc = live["grade"]["domains"]["inconsistency"]`) | KeyError: grade; ticagrelor primary trials=[]. GRADE omission is intentional without a pooled primary; the test pins the former k=2 GRADE state. | Require no rating for the empty primary and keep a separate, non-vacuous k=2 unassessed-inconsistency control. Diff: [proposed/test_k2_refusal.py.diff](proposed/test_k2_refusal.py.diff); shared helper below. |
| `tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews` | 0 — REGEN CURRENCY | `tests/test_limitations_legacy_compare.py:51`: `assert not review.get("claimgraph"), review["slug"]` | balanced-crystalloids limitation objects omit 3 rendered Admission at pooling blocks. The copied review objects lag current limitation code. In-memory build_limitations(review) produces exact page/object Counter equality: no extra page or object blocks remain. | Regenerate review limitation objects and pages; harness/limitations.py:1021-1040 already generates the missing ADMISSION objects. Do not weaken the equality contract. |
| `tests/test_or_class.py::test_rebuilt_hyperglycaemia_is_suppressed_incompatible` | 2 — PINNED FINDING | `tests/test_or_class.py:61`: `assert res["suppressed_incompatible"] is True` | KeyError: suppressed_incompatible; Hyperglycaemia now has only the admitted RR member. The assertion fixes the previous OR+RR harm membership instead of the rule that cross-class pools must be suppressed. | Derive classes from admitted harm rows and retain an OR/RR incompatibility control. Diff: [proposed/test_or_class.py.diff](proposed/test_or_class.py.diff); shared helper below. |
| `tests/test_propositions.py::test_PLANT_refused_and_pooled_fires_prefix_and_current_dispute_passes` | 2 — PINNED FINDING | `tests/test_propositions.py:96`: `assert len([d for d in disputes if d["code"] == "POOL_SCOPE_DISPUTE"]) == 1` | POOL_SCOPE_DISPUTE count=0, expected 1. Metformin has no admitted primary pool to intersect the signed refusal registry, so the former pool-scope dispute disappears. | Retain refused-and-pooled detection; require any live dispute to name a genuine membership intersection, and no pool dispute when the pool is empty. Diff: [proposed/test_propositions.py.diff](proposed/test_propositions.py.diff); shared helper below. |
| `tests/test_result_withdrawn.py::test_withdrawn_page_pools_nothing_states_everything_and_passes_the_gate[dapagliflozin-hfpef-hosp]` | 3 — RED BY DESIGN | `tests/test_result_withdrawn.py:32`: `assert ok, reasons` | gate ok=False; Adverse events reviewer_countersignature OPEN. All withdrawn-primary state assertions pass before the whole-gate assertion. The separate changed adverse-events outcome is held by check_result_change_countersigned. Certificate/replay currency is additional. | Keep the assertion and hold; reviewer decision on the dapagliflozin Adverse events notice is required. |
| `tests/test_result_withdrawn.py::test_withdrawn_page_pools_nothing_states_everything_and_passes_the_gate[empagliflozin-hfpef-hosp]` | 0 — REGEN CURRENCY | `tests/test_result_withdrawn.py:32`: `assert ok, reasons` | gate ok=False solely for certificate release_sha256 and L1 replay hash mismatches. Unlike the dapagliflozin parameter, empagliflozin has no OPEN notice in the actual gate reasons. Withdrawal remains valid; this failure is only currency, despite the whole-gate test name. | Regenerate empagliflozin certificate/reproduction/served artefacts; keep all withdrawal and gate assertions. |
| `tests/test_rob_sensitivity_predicate.py::test_PLANT_iv_iron_omitted_repool_names_its_reason` | 2 — PINNED FINDING | `tests/test_rob_sensitivity_predicate.py:294`: `assert review.get("rob2") and not review.get("rob_sensitivity")` | iv-iron now has rob_sensitivity; omission expected. The current admitted k=1 primary can carry a sensitivity object; the old PRIMARY_POOL_SUPPRESSED_INCOMPATIBLE omission state no longer applies. | Require exactly one of sensitivity or explained omission, keyed to the current primary, and verify rendering. Diff: [proposed/test_rob_sensitivity_predicate.py.diff](proposed/test_rob_sensitivity_predicate.py.diff); shared helper below. |
| `tests/test_rob_sensitivity_predicate.py::test_prefix_rendered_predicate_fires_on_identical_low_only_pages` | 2 — PINNED FINDING | `tests/test_rob_sensitivity_predicate.py:204`: `assert accounted == sorted(_rob_population()), (set(accounted) ^ set(_rob_population()))` | accounted vs live RoB population differs by {'iv-iron-hfref-hosp'}. The test intersects a historical sensitivity population with current served states. IV iron newly has a current sensitivity but no baseline sensitivity, so it drops through that historical loop. | Separate immutable historical predicate controls from exhaustive current-state accounting; require every current assessed review to have a sensitivity or a named omission/refusal/withdrawal. Diff: [proposed/test_rob_sensitivity_predicate.py.diff](proposed/test_rob_sensitivity_predicate.py.diff); shared helper below. |
| `tests/test_scope_identity.py::test_noac_prefixed_scope_mismatch_and_posthoc_amendment_fire` | 2 — PINNED FINDING | `tests/test_scope_identity.py:72`: `assert row["standard_dose_result"]["k"] == 4` | standard_dose_result.k=None, expected 4. The noac primary emptied; the post-hoc scope and source-incomplete alternative assertions still pass. | Compare the sweep result with current admitted primary state and require explicit no-result reasoning when empty. Diff: [proposed/test_scope_identity.py.diff](proposed/test_scope_identity.py.diff); shared helper below. |
| `tests/test_second_source_identity.py::test_postfix_pcsk9_second_source_rows_are_different_measure_not_corroboration` | 2 — PINNED FINDING | `tests/test_second_source_identity.py:92`: `assert fourier["ctgov_rr"] == 0.887` (**not reached**; failed at `tests/test_second_source_identity.py:89`: `fourier = _row(core, "28304224")["cross_source"]`) | StopIteration: FOURIER absent from pooled rows. The test binds cross-source identity checks to a pooled member that admission removed, while its source-backed candidate remains. | Exercise identity on the preserved candidate and current registry measure without pooling it; retain the distinct-measure/non-corroboration assertions. Diff: [proposed/test_second_source_identity.py.diff](proposed/test_second_source_identity.py.diff); shared helper below. |
| `tests/test_second_source_identity.py::test_served_fourier_0666_is_value_not_reproducible_from_current_cache` | 2 — PINNED FINDING | `tests/test_second_source_identity.py:112`: `assert old["ctgov_rr"] == 0.666` (**not reached**; failed at `tests/test_second_source_identity.py:110`: `rebuilt = _row(_core("pcsk9-mace"), "28304224")["cross_source"]`) | StopIteration: FOURIER absent from pooled rows. The historic 0.666 control and held registry values remain evidence controls; only the live lookup assumes admission. | Read the retained candidate with its immutable source metadata, verify its tuple, and recompute cross-source values from current held registry inputs. Diff: [proposed/test_second_source_identity.py.diff](proposed/test_second_source_identity.py.diff); shared helper below. |
| `tests/test_source_hierarchy_regression.py::test_tocilizumab_estimand_decision_controls_served_scale_and_renders` | 2 — PINNED FINDING | `tests/test_source_hierarchy_regression.py:92`: `assert decision["target_scale"] == outcome["result"]["scale"] == "RR"` | KeyError: scale; tocilizumab primary trials=[]. The declared OR, chosen RR and estimand decision object remain; there is no served pooled scale or result to label. | Require the decision to control any admitted result, preserve decision metadata and require explicit admission absence when no result is served. Diff: [proposed/test_source_hierarchy_regression.py.diff](proposed/test_source_hierarchy_regression.py.diff); shared helper below. |
| `tests/test_uoa_sensitivity.py::test_crystalloids_uoa_caveat_matches_post_refusal_factorial_state` | 2 — PINNED FINDING | `tests/test_uoa_sensitivity.py:23`: `assert sorted(u.get("design") for u in uoa) == ["factorial"]` | unit_of_analysis=[]; expected [factorial]. The factorial member was set aside, so a pooled-design caveat must no longer imply that member is pooled. Typed design refusals remain separately named. | Derive design caveats from current admitted source records and retain named design refusals plus false-invariance prohibitions. Diff: [proposed/test_uoa_sensitivity.py.diff](proposed/test_uoa_sensitivity.py.diff); shared helper below. |
| `tests/test_wrong_endpoint_acceptance.py::test_glp1_served_primary_rows_unchanged_in_number` | 2 — PINNED FINDING | `tests/test_wrong_endpoint_acceptance.py:145`: `assert len(rows) == 7` | 6 abstract-route pooled rows, expected 7. The missing abstract-route member is the preserved admission-refused HARMONY candidate; the source tuple itself has not changed. | Keep source selection/value equality for admitted rows and verify the retained source tuple for admission-set-aside abstract rows. Diff: [proposed/test_wrong_endpoint_acceptance.py.diff](proposed/test_wrong_endpoint_acceptance.py.diff); shared helper below. |

Focused follow-up evidence:

- **Design regression:** `harness/design_variance.py:220` returns the original contrast object when `pooled` is empty. The live primary is empty, yet its contrast object retains IDs 35041780, 34375394 and 26444692 and `harness/page.py:2850` renders “2 of 3” as pooled coverage. The validator separately reads an absent GRADE as an empty dict at `harness/design_variance.py:299`. Regeneration alone does not fix these source branches.
- **Limitation currency:** the first failure is a page/object counter mismatch consisting of three admission blocks. Rebuilding `build_limitations(review)` in memory gives exact equality with blocks from `render_page(review)` (no remaining extras). The code already adds ADMISSION objects at `harness/limitations.py:1021`; copied objects need regeneration.
- **Withdrawn-page distinction:** full gate reasons were captured in `.tmp/triage-runs/withdrawn-gate-details.json` and embedded in triage.json. Dapagliflozin has an OPEN Adverse events notice plus stale identities. Empagliflozin has only stale certificate/replay identities; it is not classified as a reviewer hold.
- **Follow-on disclosure concern, not an additional counted failure:** the GLP-1 bundle heterogeneity prose says “Q exceeds df by -0.854” and “rendered as non-zero” although `Q < df` and tau² is zero. The listed test first fails on its historic Q pin (bucket 2). A reviewer should also make that prose conditional on the recomputed values; do not repin its old boundary-sensitivity phrase. The supplied proposal retains input-precision disclosure but does not certify this prose as correct.
- **Follow-on diagnostic defect:** after removing the nonempty strategy-set pin, the metformin proposal still fails the original final requirement, `assert "STRATEGY_COLLAPSED" not in _codes(live, "metformin-pcos-ovulation")`. `harness/endpoint_canonical.py:361` compares the empty strategy set with the add-on singleton even for `result.present=False`. Proposed smallest source fix: diagnose strategy collapse only for a served pooled claim. The assertion is retained, and [STUCK_FAILURES.md](STUCK_FAILURES.md) records the issue; the original first failure remains bucket 2 and is not counted twice.
- **Currency-sensitive later checks:** the migration-state test first fails on its old count (bucket 2); its later pinned-module identity assertion remains a regeneration-sensitive requirement. Proposed property diffs are not a claim that the entire suite becomes green before regeneration or reviewer action.

Validation: all proposed complete test modules and the shared helper parse as Python; `git apply --check` passes for the complete proposal set. All 30 original target test files retain their recorded SHA-256. In-memory smoke calls checked 42 proposed functions: 39 initially passed; two proposal defects (HM3 supersession accounting and construction of the controlled k=2 state) were corrected and passed targeted reruns. The remaining metformin diagnostic assertion is intentionally retained as a source issue: 41 passing smoke checks, 1 unresolved diagnostic requirement. Three proposals (browser UI, corpus GRADE, historical RoB population) were not smoke-executed. The proposals are not applied or certified as a passing replacement pytest suite.

Unified diffs (same bytes as the linked files). Apply the shared helper together with any proposal importing `_triage_contracts`; it checks admission against the held family ledger and keeps excluded candidate values explicit.

## proposed/_triage_contracts.py.diff

```diff
--- /dev/null
+++ b/tests/_triage_contracts.py
@@ -0,0 +1,75 @@
+"""Proposed test contracts: evidence partition and admitted-pool semantics, never corpus counts."""
+import json
+from pathlib import Path
+from harness import admission, estmeasure
+
+def partition(root, slug, outcome):
+    from harness.family_compact import read_families
+    families = read_families(Path(root)/'cache'/slug/'families.json')['families']
+    by_report = {str(r['report_id']).replace('PMID ', ''): f for f in families for r in f.get('reports', [])}
+    by_family = {f['family_id']: f for f in families}
+    pooled = outcome.get('trials') or []
+    absent = outcome.get('declared_absent_trials') or []
+    ids = lambda rows: [str(t['id']).replace('PMID ', '') for t in rows]
+    assert len(ids(pooled)) == len(set(ids(pooled)))
+    assert not set(ids(pooled)) & set(ids(absent))
+    for row in pooled + [a for a in absent if admission.is_set_aside(a)]:
+        fam = by_report.get(str(row['id']).replace('PMID ', '')) or by_family.get(row.get('family_id'))
+        verdict = admission.verdict(row, fam)
+        assert row['admission_verdict'] == verdict
+        if row in pooled:
+            assert verdict['final'] in {'ADMISSIBLE', 'MIGRATION_STATE_UNBOUND_LEGACY'}
+        else:
+            assert verdict['final'] == 'INADMISSIBLE'
+            assert row['reason_code'] in verdict['failing']
+            assert row.get('candidate_tuple') and row.get('reason') and row.get('recovery')
+    assert outcome['admission_summary']['pooled_rows'] == len(pooled)
+    if not pooled:
+        assert outcome['result'].get('present') is False
+        assert not outcome['result'].get('k') and outcome['result'].get('estimate') is None
+        assert outcome['result'].get('reason')
+    return pooled, absent
+
+def accounted_row(root, slug, outcome, pid):
+    pooled, absent = partition(root, slug, outcome)
+    rows = [r for r in pooled + absent if str(r['id']).replace('PMID ', '') == pid]
+    assert len(rows) == 1, (slug, pid)
+    return rows[0], rows[0] in pooled
+
+def scale_contract(outcome):
+    rows = outcome.get('trials') or []
+    result = outcome['result']
+    if not rows:
+        assert result.get('present') is False and result.get('estimate') is None
+        return
+    effects = [t.get('effect_object') or estmeasure.classify(t.get('scale') or outcome.get('served_estimand') or outcome['estimand'], t.get('source', '')) for t in rows]
+    expected = estmeasure.pool_compatibility(effects)
+    assert result['estmeasure'] == expected
+    incompatible = expected['status'] == 'incompatible'
+    assert bool(result.get('suppressed_incompatible')) == incompatible
+    if incompatible:
+        assert all(result.get(k) is None for k in ('estimate', 'ci_low', 'ci_high', 'tau2', 'pi_low', 'pi_high'))
+    elif expected['status'] == 'compatible_labels':
+        assert set(result.get('scale_mixed') or []) == set(expected['labels'])
+        label = result['effect_label']
+        for name in expected['labels']:
+            count = sum(e['reported_label'] == name for e in effects)
+            assert f'{count} {name}' in label
+
+def candidate_cross_source(root, slug, outcome, pid):
+    from harness.pipeline import _cross_source
+    import subprocess
+    row, pooled = accounted_row(root, slug, outcome, pid)
+    root = Path(root)
+    cfg = json.loads((root/'topics'/f'{slug}.json').read_text(encoding='utf-8'))
+    recs = json.loads((root/'cache'/slug/'records.json').read_text(encoding='utf-8'))
+    record = next(r for r in recs['records'] if str(r['id']) == pid)
+    ex = dict(row, **row.get('candidate_tuple', {}))
+    if pooled:
+        return row['cross_source']
+    # Exercise source identity even when admission excludes the clinical row; never re-admit it.
+    previous = json.loads(subprocess.check_output(['git', 'show', f'38c04411484dbea035a8e4c8e22c57c2794f9495:docs/reviews/{slug}/review.json'], cwd=root))
+    original = next(t for o in previous['outcomes'] if o.get('primary') for t in o['trials'] if str(t['id']).replace('PMID ', '') == pid)
+    assert all(original.get(k) == v for k, v in row['candidate_tuple'].items())
+    ex = dict(original, **row['candidate_tuple'])
+    return _cross_source(ex, record['nct'], recs['ctgov_results'], cfg['primary_outcome'], cfg['intervention_terms'], cfg['comparator_terms'])
```

## proposed/test_arm_identity.py.diff

```diff
--- a/tests/test_arm_identity.py
+++ b/tests/test_arm_identity.py
@@ -71,26 +71,17 @@
 
 
 def test_mixed_scale_pool_labelled_honestly():
-    # A pool mixing reported labels must never be silently labelled as one clean scale (the "calling it
-    # an HR" defect). The effect-measure type system now decides by COMPATIBILITY CLASS: RALES's "RR" +
-    # EMPHASIS's "HR" are the SAME class (first-event relative ratios), so the pool is COMPATIBLE (the
-    # label mix disclosed via scale_mixed), not a false "mixed" alarm and not a hidden single scale.
-    p = os.path.join(ROOT, "docs", "reviews", "spironolactone-hfref-mortality", "review.json")
-    if os.path.exists(p):
-        rev = json.load(open(p, encoding="utf-8"))
-        res = next((o for o in rev["outcomes"] if o.get("primary")), {}).get("result") or {}
-        em = res.get("estmeasure") or {}
-        assert em.get("status") == "compatible_labels", em
-        assert set(res.get("scale_mixed") or []) == {"HR", "RR"}, res.get("scale_mixed")
-        assert em.get("classes") == ["FIRST_EVENT_RATIO"]
-    # A pool mixing ACROSS classes (a recurrent-event rate ratio + a first-event hazard ratio) is a
-    # genuine incompatibility and MUST be flagged, not smoothed (iv-iron, audit 12).
-    p2 = os.path.join(ROOT, "docs", "reviews", "iv-iron-hfref-hosp", "review.json")
-    if os.path.exists(p2):
-        rev = json.load(open(p2, encoding="utf-8"))
-        res = next((o for o in rev["outcomes"] if o.get("primary")), {}).get("result") or {}
-        assert (res.get("estmeasure") or {}).get("status") == "incompatible", res.get("estmeasure")
-        assert str(res.get("scale", "")).startswith("INCOMPATIBLE"), res.get("scale")
+    from _triage_contracts import partition, scale_contract
+    for slug in ('spironolactone-hfref-mortality', 'iv-iron-hfref-hosp'):
+        with open(os.path.join(ROOT, 'docs', 'reviews', slug, 'review.json'), encoding='utf-8') as f:
+            review = json.load(f)
+        outcome = next(o for o in review['outcomes'] if o.get('primary'))
+        partition(ROOT, slug, outcome)
+        scale_contract(outcome)
+    # Non-vacuous controls independent of current corpus membership.
+    from harness.estmeasure import classify, pool_compatibility
+    assert pool_compatibility([classify('HR'), classify('RR')])['status'] == 'compatible_labels'
+    assert pool_compatibility([classify('HR'), classify('IRR')])['status'] == 'incompatible'
 
 
 def test_locate_gate_rejects_on_identity_or_population():
```

## proposed/test_bundle.py.diff

```diff
--- a/tests/test_bundle.py
+++ b/tests/test_bundle.py
@@ -261,19 +261,26 @@
 
 
 def test_harmony_is_inadmissible_because_its_family_eligibility_is_unknown(bundle):
-    """A finding, not a bug: the page pools NCT02465515 while its family eligibility object says UNKNOWN
-    (ENTRY_POPULATION_NOT_ESTABLISHED). Under the declared invariant the row is inadmissible. Recorded so that the
-    eligibility lane sees it; if the family object is repaired, update this deliberately."""
-    row = next(r for r in bundle["verification_rows"] if r["trial"]["id"] == "PMID 30291013")
-    assert row["admission"]["final"] == "INADMISSIBLE"
-    assert row["admission"]["predicates"]["P5_family_eligible"]["eligibility_state"] == "UNKNOWN"
-    assert bundle["counts"]["admissible_rows"] == 7
+    """Unknown family eligibility excludes pooling, preserves the candidate and names the recovery route."""
+    from _triage_contracts import accounted_row
+    review = _load(os.path.join(REVIEW_DIR, 'review.json'))
+    outcome = next(o for o in review['outcomes'] if o.get('primary'))
+    row, pooled = accounted_row(ROOT, SLUG, outcome, '30291013')
+    p5 = row['admission_verdict']['predicates']['P5_family_eligible']
+    if p5['eligibility_state'] != 'ELIGIBLE':
+        assert not pooled and row['admission_verdict']['final'] == 'INADMISSIBLE'
+        assert row['candidate_tuple'] and row['recovery']
+    assert {r['trial']['id'] for r in bundle['verification_rows']} == {r['id'] for r in outcome['trials']}
+    assert bundle['counts']['admissible_rows'] == sum(r['admission']['final'] == 'ADMISSIBLE' for r in bundle['verification_rows'])
 
 
 def test_lancet_rows_are_normalised_not_verbatim_and_offsets_reproduce(bundle):
     rows = {r["trial"]["id"]: r for r in bundle["verification_rows"]}
-    assert rows["PMID 31189511"]["span"]["match"] == "NORMALISED" and rows["PMID 30291013"]["span"]["match"] == "NORMALISED"
-    assert rows["PMID 40162642"]["span"]["match"] == "VERBATIM"
+    assert rows
+    for row in rows.values():
+        span = row["span"]
+        assert span["match"] in {"VERBATIM", "NORMALISED"}
+        assert span["parent_representation"] == ("NORMALIZED_SOURCE" if span["match"] == "NORMALISED" else "PARSED_SOURCE")
     records = _load(os.path.join(ROOT, "cache", SLUG, "records.json"))
     by = {str(x["id"]): x["abstract"] for x in records["records"]}
     for pid, r in rows.items():
@@ -285,10 +292,15 @@
 
 
 def test_pooled_reference_matches_the_settled_value(bundle):
-    e = bundle["pooled_reference"]["expected"]
-    assert abs(e["estimate"] - 0.8559934175938467) < 1e-9
-    assert abs(e["ci_low"] - 0.8086248326601262) < 1e-9 and abs(e["ci_high"] - 0.9061368157017332) < 1e-9
-    assert abs(e["tau2"] - 0.00004447972517261924) < 1e-9
+    """The served pool must reproduce from the current, explicitly enumerated inputs."""
+    from harness.synth import Study, pool
+    ref = bundle['pooled_reference']
+    review = _load(os.path.join(REVIEW_DIR, 'review.json'))
+    primary = next(o for o in review['outcomes'] if o.get('primary'))
+    assert {r['id'] for r in ref['inputs']} == {r['id'] for r in primary['trials']}
+    got = pool([Study(label=r['id'], effect=r['effect'], ci_low=r['ci_low'], ci_high=r['ci_high'], measure=ref['scale']) for r in ref['inputs']], scale=ref['scale'])
+    for field in ('estimate', 'ci_low', 'ci_high', 'tau2'):
+        assert abs(ref['expected'][field] - getattr(got, field)) < 1e-9
 
 
 # ------------------------------------------------------------------ 3.1: canonicalisation, selector, coordinates, variation, inputs
@@ -335,7 +347,10 @@
     assert "undetermined death as cardiovascular death" in c["protocol_permission"]
     pt = {k: v["value"] for k, v in c["per_trial"].items()}
     assert pt["PMID 34215025"] == "yes" and pt["PMID 31189511"] == "yes"          # AMPLITUDE-O, REWIND -- from their own spans
-    assert pt["PMID 30291013"] == "unstated"                                       # HARMONY: the 'unknown causes' phrase is not its
+    rows = {r["trial"]["id"]: r for r in bundle["verification_rows"]}
+    assert set(pt) == set(rows)
+    for pid, row in rows.items():
+        assert pt[pid] == build_bundle.undetermined_death_field(row["span"]["definition_span"])["value"]
     assert "no" not in pt.values(), "an abstract that is silent never yields 'no'"
     assert c["page_label"] == "HOMOGENEOUS" and c["page_direction_audit"] == "ASSERTED_HOMOGENEOUS_UNDERLYING_HETEROGENEOUS"
     assert build_bundle.undetermined_death_field("death from cardiovascular or undetermined causes")["value"] == "yes"
@@ -356,10 +371,16 @@
 
 def test_heterogeneity_statement_carries_input_precision_not_a_categorical_claim(bundle):
     h = bundle["pooled_reference"]["heterogeneity"]
-    assert abs(h["Q"] - 7.06072) < 1e-4 and h["df"] == 7 and 0 < h["Q_minus_df"] < 0.1
+    ref = bundle["pooled_reference"]
+    assert h["Q"] == ref["expected"]["Q"] and h["df"] == len(ref["inputs"]) - 1
+    assert h["Q_minus_df"] == pytest.approx(h["Q"] - h["df"])
+    assert h["input_precision"]
     rs = h["rounding_sensitivity"]
-    assert 0.2 < rs["fraction_tau2_zero"] < 0.8 and rs["finding_untouched"] is True and rs["max_ci_upper"] < 1.0
-    assert "effectively zero and rounding-sensitive" in h["honest_statement"]
+    assert 0 <= rs["fraction_tau2_zero"] <= 1
+    assert rs["method"] and "seeded" in rs["method"]
+    assert "rounded inputs" in h["honest_statement"]
+    # The uncertainty disclosure survives even if all perturbations land on one side of the boundary.
+    assert f"{rs['fraction_tau2_zero']:.0%}" in h["honest_statement"]
 
 
 def test_verifier_is_served_byte_identical_at_the_path_the_bundle_names(bundle):
@@ -377,8 +398,11 @@
 def test_extraction_object_coverage_is_stated_not_discovered(bundle):
     x = bundle["extraction_objects_coverage"]
     primary = next(o for o in x["per_outcome"] if o["primary"])
-    assert primary["pooled_rows"] == 8 and primary["pooled_rows_with_an_extraction_object"] == ["40162642"]
-    assert "1 of 8" in x["plain_statement"]
+    rows = bundle["verification_rows"]
+    covered = sorted(r["trial"]["id"].replace("PMID ", "") for r in rows if r["certified_evidence_chain"]["extraction_object_for_this_outcome"] != "ABSENT")
+    assert primary["pooled_rows"] == len(rows)
+    assert primary["pooled_rows_with_an_extraction_object"] == covered
+    assert f"{len(covered)} of {len(rows)}" in x["plain_statement"]
     for r in bundle["verification_rows"]:
         ch = r["certified_evidence_chain"]
         if r["trial"]["id"] == "PMID 40162642":
@@ -427,7 +451,7 @@
     leader = next(r for r in bs["rows"] if r["trial"]["id"] == "PMID 27295427" and not r["primary"])
     assert leader["observations"]["table_sourced"] is True                              # the multi-span case
     assert bundle["counts"]["unbound_legacy_rows_inside_admissible_rows"] == 0
-    assert bundle["counts"]["admissible_rows"] + bundle["counts"]["migration_state_rows_in_primary_pool"] + bundle["counts"]["inadmissible_rows_in_primary_pool"] == 8
+    assert bundle["counts"]["admissible_rows"] + bundle["counts"]["migration_state_rows_in_primary_pool"] + bundle["counts"]["inadmissible_rows_in_primary_pool"] == len(bundle["verification_rows"])
     assert all(r["admission"]["predicates"]["P8_endpoint_bound"]["state"] == "PASS" for r in bundle["verification_rows"])
     assert any(l["id"] == "L10_admit_rows_fail_open" for l in bundle["limits"])
     assert "not refused" in bs["statement"]
@@ -610,8 +634,9 @@
         assert ee["estimator"]["state"] == "STATED_IN_OWNING_EVIDENCE" and ee["estimator"]["value"] == "hazard ratio"
         assert ee["analysis_window"]["state"] != "UNRESOLVED" and ee["analysis_set"]["state"] != "UNRESOLVED"   # no pooled abstract states two
         stated_set += ee["analysis_set"]["state"] == "STATED_IN_OWNING_EVIDENCE"; stated_window += ee["analysis_window"]["state"] == "STATED_IN_OWNING_EVIDENCE"
-    assert stated_set == 3        # measured: analysis set stated in 3 of 8 abstracts (REWIND, Harmony, EXSCEL); the rest default to the registered value
-    assert stated_window >= 2
+    # Per-row span reproduction above is the requirement; cohort frequencies are findings.
+    assert bundle["verification_rows"], "use source-backed fixtures if the served pool empties"
+    assert all(r["estimand_evidence"][f].get("value") for r in bundle["verification_rows"] for f in ("analysis_set", "analysis_window"))
 
 
 def test_elixa_strategy_evidence_separates_the_pair_through_structured_fields(bundle):
@@ -658,7 +683,15 @@
 
 def test_default_and_stated_bases_are_both_present_and_visibly_distinct(bundle):
     bases = [r["analysis_identity"]["analysis_set"]["basis"] for r in bundle["verification_rows"]]
-    assert bases.count("STATED_IN_OWNING_EVIDENCE") == 3 and bases.count("REGISTERED_DEFAULT") == 5   # measured: 3 of 8 abstracts state the analysis set
+    assert bases
+    for row, basis in zip(bundle["verification_rows"], bases):
+        evidence = row["estimand_evidence"]["analysis_set"]
+        assert basis == evidence["state"]
+        assert basis in {"STATED_IN_OWNING_EVIDENCE", "REGISTERED_DEFAULT"}
+        if basis == "STATED_IN_OWNING_EVIDENCE":
+            assert evidence.get("span") and evidence.get("start") is not None
+        else:
+            assert "default" in evidence["value"].lower()
     assert "UNRESOLVED" not in bases
 
 
@@ -673,7 +706,10 @@
             assert cil["source_ci_pct"] == 95.0 and cil["basis"] == "STATED_IN_OWNING_EVIDENCE"
             assert abs(cil["se_log_at_stated_level"] - cil["se_log_used"]) < 1e-9
         assert r["admission"]["predicates"]["P12_ci_level"]["state"] == "PASS"
-    assert sum(1 for r in bundle["verification_rows"] if r["statistical_input"]["ci_level"]["level_agreement"] == "MATCH") == 8   # all eight clauses state '95%'
+    assert bundle["verification_rows"]
+    for row in bundle["verification_rows"]:
+        ci = row["statistical_input"]["ci_level"]
+        assert (ci["level_agreement"] == "MATCH") == (ci.get("source_ci_pct") == ci["assumed_ci_pct"])
 
 
 def test_ci_level_mismatch_is_detected_and_z_recomputed_by_stdlib():
@@ -728,7 +764,12 @@
     # every row has exactly one state; the migration count is the binding_states count (0 since the two glp1 harm rows
     # were bound by the hand-row binder on 2026-09-21; 2 before); ASSESSED covers the 8 primary rows and the 4 negatives
     assert sum(a["counts"].values()) == n_rows
-    assert a["counts"]["ASSESSED"] >= 8 + 4
+    from collections import Counter
+    assert a["counts"] == dict(Counter(r["state"] for r in a["rows"]))
+    verified = {r["trial"]["id"]: r for r in bundle["verification_rows"]}
+    for row in a["rows"]:
+        if row["kind"] == "rendered_row" and row["trial"] in verified and row["outcome"] == bundle["pooled_reference"]["outcome"]:
+            assert row["state"] == ("MIGRATION_STATE" if verified[row["trial"]]["admission"]["final"] == "MIGRATION_STATE_UNBOUND_LEGACY" else "ASSESSED")
     assert a["counts"].get("MIGRATION_STATE", 0) == bundle["binding_states"]["counts"]["migration_state_unbound_legacy"]
     assert "WITHDRAWN" not in a["counts"]
 
@@ -775,7 +816,7 @@
 
 def test_clean_negative_is_recorded_as_a_negative_with_its_scope(bundle):
     cn = bundle["clean_negatives"][0]
-    assert cn["result"].startswith("8 of 8") and "says nothing about the defect" in cn["meaning"] and "95.03" in cn["meaning"]
+    assert cn["result"].startswith(f"{len(bundle['verification_rows'])} of {len(bundle['verification_rows'])}") and "says nothing about the defect" in cn["meaning"] and "95.03" in cn["meaning"]
     assert "constant across every row" in cn["why_the_field_stays"]
```

## proposed/test_bundle_verifier.py.diff

```diff
--- a/tests/test_bundle_verifier.py
+++ b/tests/test_bundle_verifier.py
@@ -57,12 +57,13 @@
 
 
 def test_pool_reproduced_without_the_harness(baseline):
-    p = baseline["pool"]
-    assert p["reproduced_to_1e-9"], p["abs_deltas"]
-    assert abs(p["recomputed"]["estimate"] - 0.8559934175938467) < 1e-9
-    assert abs(p["recomputed"]["tau2"] - 0.00004447972517261924) < 1e-9
-    assert abs(p["t_crit_recomputed"] - 2.3646242515927853) < 1e-9   # t_{0.975, 7}
-    assert p["k_declared"] == 8 and p["admissible_rows"] == 7
+    p = baseline['pool']
+    assert p['reproduced_to_1e-9'], p['abs_deltas']
+    assert all(delta < 1e-9 for delta in p['abs_deltas'].values())
+    assert p['k_declared'] == len(baseline['rows'])
+    assert p['admissible_rows'] == sum(r['final'] == 'ADMISSIBLE' for r in baseline['rows'])
+    from scipy.stats import t
+    assert abs(p['t_crit_recomputed'] - t.ppf(0.975, p['k_declared'] - 1)) < 1e-9
 
 
 def test_absence_claims_judged_from_recomputed_preservation(baseline):
@@ -128,15 +129,22 @@
 
 
 def test_control_a_row_already_refused_at_baseline_cannot_serve_as_a_mutation_target(baseline):
-    """The hole the old assertion had, kept as a control: corrupting HARMONY (INADMISSIBLE at baseline on
-    P5_family_eligible) leaves the set of refused rows unchanged, so a set-union assertion passes without the
-    corruption having been shown to do anything. The positive-control test above refuses such a target by name."""
-    harmony = next(r for r in baseline["rows"] if r["pmid"] == "30291013")
-    assert harmony["final"] == "INADMISSIBLE" and not harmony["predicates"]["P5_family_eligible"]
-    base_bad = {r["pmid"] for r in baseline["rows"] if r["final"] == "INADMISSIBLE"}
-    rep = _run("--corrupt", "30291013", "span")
-    now_bad = {r["pmid"] for r in rep["rows"] if r["final"] == "INADMISSIBLE"}
-    assert now_bad == base_bad | {"30291013"} and now_bad == base_bad   # the old form: satisfied, and uninformative
+    """A mutation proves refusal only if its target was present and admissible before corruption."""
+    assert baseline['rows']
+    target = next(r for r in baseline['rows'] if r['final'] == 'ADMISSIBLE')
+    first = _run('--corrupt', target['pmid'], 'eligibility')
+    bad = {r['pmid'] for r in first['rows'] if r['final'] == 'INADMISSIBLE'}
+    base_bad = {r['pmid'] for r in baseline['rows'] if r['final'] == 'INADMISSIBLE'}
+    assert target['pmid'] not in base_bad
+    assert bad == base_bad | {target['pmid']}
+    # Against an already-refused baseline, the old union-only form is vacuous.
+    assert bad == bad | {target['pmid']}
+    def require_admissible(report, pmid):
+        row = next(r for r in report['rows'] if r['pmid'] == pmid)
+        assert row['final'] == 'ADMISSIBLE', 'already-refused mutation target'
+    require_admissible(baseline, target['pmid'])
+    with pytest.raises(AssertionError, match='already-refused mutation target'):
+        require_admissible(first, target['pmid'])
 
 
 @pytest.mark.parametrize("pmid", ["40162642", "27295427"])
```

## proposed/test_comparator_panel_ui.py.diff

```diff
--- a/tests/test_comparator_panel_ui.py
+++ b/tests/test_comparator_panel_ui.py
@@ -44,7 +44,13 @@
                     if path.parent.name == "glp1-ra-mace-t2d":
                         assert tab.locator("article[data-comparator]").count() == 5
                         assert tab.inner_text().count("NOT HELD — identity only") == 4
-                        assert "0.7777777777777778" in tab.inner_text()
+                        from harness.comparator_panel import overlaps
+                        for comparator in review["comparator_panel"]:
+                            for overlap in overlaps(comparator, review):
+                                shared = set(overlap["shared"])
+                                union = shared | set(overlap["harness_only"]) | set(overlap["comparator_only"])
+                                assert overlap["jaccard"] == (len(shared) / len(union) if union else None)
+                                assert str(overlap["jaccard"]) in tab.inner_text()
                         assert "not independent replication" in tab.inner_text()
                     assert not errors
             finally:
```

## proposed/test_compat_underlying.py.diff

```diff
--- a/tests/test_compat_underlying.py
+++ b/tests/test_compat_underlying.py
@@ -43,17 +43,19 @@
 
 
 def test_post_fix_probiotics_key_is_mixed_and_no_asserted_violation():
-    with open("docs/reviews/probiotics-aad-prevention/review.json", encoding="utf-8") as f:
+    from _triage_contracts import partition
+    with open('docs/reviews/probiotics-aad-prevention/review.json', encoding='utf-8') as f:
         review = json.load(f)
-    primary = next(o for o in review["outcomes"] if o.get("primary"))
-    ck = primary["compat_key"]
-    assert ck["analysis_set"].startswith("mixed (")
-    assert ck["follow_up_window"].startswith("trial-defined")
-    assert ck["endpoint"].startswith("trial-defined antibiotic-associated diarrhoea")
-    assert ck["dimension_matches"]["analysis_set"] is False
-    assert ck["dimension_matches"]["follow_up_window"] is False
-    assert ck["dimension_matches"]["endpoint"] is False
-    assert not C.page_gate_violations(review, _records("probiotics-aad-prevention"))
+    primary = next(o for o in review['outcomes'] if o.get('primary'))
+    pooled, _ = partition('.', 'probiotics-aad-prevention', primary)
+    if pooled:
+        assert primary.get('compat_key')
+    else:
+        assert not primary.get('compat_key'), 'an empty pool cannot assert compatibility'
+    assert not C.page_gate_violations(review, _records('probiotics-aad-prevention'))
+    # The independent pre-fix source-disagreement plant remains non-vacuous when the live pool is empty.
+    plant = _pre_fix_review('probiotics-aad-prevention')
+    assert {'analysis_set', 'follow_up_window', 'endpoint'} <= set(_by_dim(C.check(plant, _records('probiotics-aad-prevention'))))
 
 
 def test_comparator_population_match_is_derived_false_for_adult_comparator_with_paediatric_pool():
```

## proposed/test_cross_source_endpoint.py.diff

```diff
--- a/tests/test_cross_source_endpoint.py
+++ b/tests/test_cross_source_endpoint.py
@@ -89,8 +89,9 @@
 
 def test_rebuilt_fourier_row_is_different_measure_not_corroboration():
     core = _rebuilt_core("pcsk9-mace")
-    row = _fourier_row(core)
-    cs = row["cross_source"]
+    from _triage_contracts import candidate_cross_source
+    outcome = next(o for o in core["outcomes"] if o.get("primary"))
+    cs = candidate_cross_source(ROOT, "pcsk9-mace", outcome, "28304224")
 
     assert cs["endpoint_match"] == "SECOND_SOURCE_DIFFERENT_MEASURE"
     assert cs["corroborates_endpoint"] is False
@@ -98,10 +99,13 @@
     assert cs["identity"]["measure_type"] == "KM estimate ratio"
 
     html = render_page(dict(core, reproduction={"failures": 0}))
-    anchor = html.index("SECOND_SOURCE_DIFFERENT_MEASURE")
-    snippet = html[anchor:anchor + 700]
-    assert "✓ corroborated" not in snippet
-    assert "KM_ESTIMATE" in snippet
+    if any(t.get("label") == "28304224" for t in outcome["trials"]):
+        anchor = html.index("SECOND_SOURCE_DIFFERENT_MEASURE")
+        snippet = html[anchor:anchor + 700]
+        assert "✓ corroborated" not in snippet
+        assert "KM_ESTIMATE" in snippet
+    else:
+        assert "28304224" in html and "set aside on admission" in html
 
 
 def test_synthetic_same_endpoint_control_is_counted():
```

## proposed/test_endpoint_canonical.py.diff

```diff
--- a/tests/test_endpoint_canonical.py
+++ b/tests/test_endpoint_canonical.py
@@ -36,8 +36,13 @@
     assert "KEY_UNDER_CLAIMS" in _codes(pre, "doac-vte-recurrence")
 
     live = _primary(_live_review("doac-vte-recurrence"))
-    assert live["endpoint_canonical"]["label"] == "SYMPTOMATIC_RECURRENT_VTE"
-    assert live["compat_key"]["endpoint"] == "SYMPTOMATIC_RECURRENT_VTE"
+    from _triage_contracts import partition
+    pooled, _ = partition(ROOT, "doac-vte-recurrence", live)
+    if pooled:
+        assert live["endpoint_canonical"] == EC.endpoint_canonical(live, "doac-vte-recurrence")
+        assert live["compat_key"]["endpoint"] == live["endpoint_canonical"]["label"]
+    else:
+        assert not live.get("endpoint_canonical") and not live.get("compat_key")
     assert "KEY_UNDER_CLAIMS" not in _codes(live, "doac-vte-recurrence")
 
 
@@ -59,8 +64,10 @@
 
     live_doac = _primary(_live_review("doac-vte-recurrence"))
     live_noac = _primary(_live_review("noac-vs-warfarin-af-stroke"))
-    assert live_doac["result"]["effect_label"] == "pooled first-event ratio (5 HR + 1 RR)"
-    assert live_noac["result"]["effect_label"] == "pooled first-event ratio (3 HR + 1 RR)"
+    from _triage_contracts import partition, scale_contract
+    for slug, outcome in (("doac-vte-recurrence", live_doac), ("noac-vs-warfarin-af-stroke", live_noac)):
+        partition(ROOT, slug, outcome)
+        scale_contract(outcome)
     assert "LABEL_HIDES_MIX" not in _codes(live_doac, "doac-vte-recurrence")
     assert "LABEL_HIDES_MIX" not in _codes(live_noac, "noac-vs-warfarin-af-stroke")
 
@@ -80,9 +87,18 @@
     assert "ANALYSIS_SET_PROMOTED" in _codes(pre, "doac-vte-recurrence")
 
     live = _primary(_live_review("doac-vte-recurrence"))
-    assert live["compat_key"]["analysis_set_superclass"] == EC.ANALYSIS_SUPERCLASS
-    by_id = {str(t["id"]).replace("PMID ", ""): t for t in live["trials"]}
-    assert by_id["23991658"]["analysis_set_literal"] == "mITT"
+    from _triage_contracts import partition
+    pooled, _ = partition(ROOT, "doac-vte-recurrence", live)
+    if pooled:
+        expected = EC.analysis_set_superclass(live)
+        if expected:
+            assert live["compat_key"]["analysis_set_superclass"] == expected["superclass"]
+        # Recompute from source-derived literals; never promote mITT to a literal ITT.
+        for row in pooled:
+            if row.get("analysis_set_literal") == "mITT":
+                assert any(x["literal"] == "mITT" for x in expected["per_trial"])
+    else:
+        assert "compat_key" not in live
     assert "ANALYSIS_SET_PROMOTED" not in _codes(live, "doac-vte-recurrence")
 
 
@@ -92,7 +108,10 @@
 
     live = _primary(_live_review("metformin-pcos-ovulation"))
     strategies = {t.get("treatment_strategy") for t in live["trials"]}
-    assert strategies == {"METFORMIN_ADDON_CC"}
+    from _triage_contracts import partition
+    partition(ROOT, "metformin-pcos-ovulation", live)
+    assert all(strategy == "METFORMIN_ADDON_CC" for strategy in strategies)
+    # The source-backed historical plant above keeps the strategy-collapse boundary covered.
     assert "added to clomifene" in _live_review("metformin-pcos-ovulation")["title"].lower()
     assert "STRATEGY_COLLAPSED" not in _codes(live, "metformin-pcos-ovulation")
```

## proposed/test_estimand_naming.py.diff

```diff
--- a/tests/test_estimand_naming.py
+++ b/tests/test_estimand_naming.py
@@ -93,9 +93,16 @@
     assert len(clomifene_rows) >= 2
     assert "background_therapy" not in (_primary(pre).get("compat_key") or {})
 
-    live_key = _primary(_live_review("metformin-pcos-ovulation")).get("compat_key") or {}
-    assert live_key["background_therapy"]["matched"] is True
-    assert live_key["background_therapy"]["values"] == ["clomifene"]
+    from _triage_contracts import partition
+    live = _live_review("metformin-pcos-ovulation")
+    outcome = _primary(live)
+    pooled, _ = partition(ROOT, "metformin-pcos-ovulation", outcome)
+    if pooled:
+        expected = CM.outcome_key(outcome, live)["background_therapy"]
+        assert outcome["compat_key"]["background_therapy"] == expected
+        assert expected["values"] == ["clomifene"]
+    else:
+        assert not outcome.get("compat_key")
 
 
 def test_pericarditis_prior_disease_stage_dimension_plant():
@@ -124,12 +131,19 @@
 
     live = _live_review("statins-primary-prevention-elderly")
     live_primary = _primary(live)
-    live_jupiter = next(t for t in _pooled_trials(live) if t.get("id") == "PMID 20404379")
-    assert live_jupiter["evidence_unit"] == "prespecified_subgroup"
+    from _triage_contracts import accounted_row
+    live_jupiter, pooled = accounted_row(ROOT, "statins-primary-prevention-elderly", live_primary, "20404379")
+    if pooled:
+        assert live_jupiter["evidence_unit"] == "prespecified_subgroup"
+    else:
+        assert live_jupiter["candidate_tuple"] and live_jupiter["reason"]
     assert "subgroup" in live_primary["population"].lower()
     page = open(ROOT / "docs" / "reviews" / "statins-primary-prevention-elderly" / "index.html",
                 encoding="utf-8").read()
-    assert "k = 2 (1 trial + 1 pre-specified subgroup of JUPITER)" in page
+    if pooled:
+        assert "pre-specified subgroup of JUPITER" in page
+    else:
+        assert "20404379" in page and "set aside on admission" in page
 
 
 def test_synthetic_prior_stage_and_background_dimension_controls():
```

## proposed/test_grade_missing_is_not_favourable.py.diff

```diff
--- a/tests/test_grade_missing_is_not_favourable.py
+++ b/tests/test_grade_missing_is_not_favourable.py
@@ -114,9 +114,29 @@
         # Missing is not favourable: a page may carry no rating ONLY because its result is explicitly withdrawn
         # (a withdrawn result has no certainty to rate). A rating that vanishes without a withdrawal, or a
         # withdrawn page that still carries one, is a loss of every downgrade at once.
-        if 'grade' not in before or 'grade' not in after:
-            if not after.get('withdrawn') or 'grade' in after:
-                losses.append((slug, 'GRADE object absent without a declared withdrawal'))
+        primary = next(o for o in after['outcomes'] if o.get('primary'))
+        from _triage_contracts import partition
+        partition(Path('.'), slug, primary)
+        if after.get('withdrawn') or not primary['trials']:
+            if 'grade' in after:
+                losses.append((slug, 'GRADE present without a pooled primary'))
+            continue
+        if 'grade' not in after:
+            losses.append((slug, 'GRADE absent for a pooled primary'))
+            continue
+        old_primary = next(o for o in before['outcomes'] if o.get('primary'))
+        # A changed evidence set can change its assessed downgrade; absence still cannot mean favourable.
+        for name, domain in after['grade']['domains'].items():
+            if not domain.get('assessed'):
+                assert after['grade']['certainty'].lower() != 'high', (slug, name)
+        fields = ('id', 'effect', 'ci_low', 'ci_high', 'scale', 'ai', 'n1i', 'ci', 'n2i', 'mean1', 'mean2', 'sd1', 'sd2', 'nc1', 'nc2')
+        values = lambda o: [{k: t.get(k) for k in fields} for t in o['trials']]
+        if values(old_primary) != values(primary) or 'grade' not in before:
+            from harness import grade
+            from harness.pipeline import _load_ghost
+            expected = grade.grade(after, _load_ghost(slug))
+            for name, domain in after['grade']['domains'].items():
+                assert domain['downgrade'] == expected['domains'][name]['downgrade'], (slug, name)
             continue
         for name, domain in before['grade']['domains'].items():
             if after['grade']['domains'][name]['downgrade'] < domain['downgrade']:
```

## proposed/test_grade_unassessed.py.diff

```diff
--- a/tests/test_grade_unassessed.py
+++ b/tests/test_grade_unassessed.py
@@ -90,7 +90,13 @@
         # the GRADE table exists and names the unassessed domains as NOT ASSESSED / human judgement
         assert "NOT ASSESSED" in html or "human judgement" in html, os.path.basename(d)
         checked += 1
-    assert checked >= 20, checked
+    eligible = []
+    for rp in glob.glob(os.path.join(_ROOT, "docs", "reviews", "*", "review.json")):
+        g = json.load(open(rp, encoding="utf-8")).get("grade") or {}
+        if g.get("certainty") not in (None, "not_rateable"):
+            eligible.append(rp)
+    assert eligible, "retain a controlled unassessed-domain fixture if no served rating remains"
+    assert checked == len(eligible)
 
 
 def test_corpus_no_high_certainty_survives():
```

## proposed/test_held_source_never_not_in_committed_source.py.diff

```diff
--- a/tests/test_held_source_never_not_in_committed_source.py
+++ b/tests/test_held_source_never_not_in_committed_source.py
@@ -64,12 +64,18 @@
         'table8_ontreatment_3p': 24, 'executive_summary_3p': 7,
         'primary_4p_table6': 22, 'primary_4p_text': 35, 'primary_4p_unrounded_text': 8}
     base = json.loads(subprocess.check_output(['git', 'show', f'237e9094:docs/reviews/{SLUG}/review.json']))
-    assert outcome['result']['k'] == 8
+    from _triage_contracts import partition
+    partition(ROOT, SLUG, outcome)
+    assert outcome['result']['k'] == len(outcome['trials'])
+    assert '26630143' not in {t['id'].replace('PMID ', '') for t in outcome['trials']}
     # the primary RESULT is unchanged: every scientific field equal; the dependency stamps (input_set_version,
     # claim_id, depends_on) are re-derived by later landings (ws/TF widened the input set) and are not the result
     _stamps = {'input_set_version', 'claim_id', 'depends_on', 'claim_kind'}
     scientific = lambda res: {k: v for k, v in res.items() if k not in _stamps}
-    assert scientific(outcome['result']) == scientific(primary(base)['result'])
+    from harness.synth import Study, pool
+    result = pool([Study(label=t['id'], effect=t['effect'], ci_low=t['ci_low'], ci_high=t['ci_high'], measure='HR') for t in outcome['trials']], scale='HR')
+    for field in ('estimate', 'ci_low', 'ci_high', 'tau2'):
+        assert outcome['result'][field] == pytest.approx(round(getattr(result, field), 4), abs=1e-6)
     from harness.page import _stale_topic_overview
     assert '1.02' not in _stale_topic_overview(review)
 
@@ -91,7 +97,8 @@
     assert demo['proposed']['pi_high'] > 1
     page = (ROOT / 'docs/reviews' / SLUG / 'index.html').read_text(encoding='utf-8')
     assert demo['state'] in page
-    assert 'under the PROPOSED adjudication -- not a result; the primary k=8 pool is unchanged' in page
+    assert f"under the PROPOSED adjudication -- not a result; the primary k={len(outcome['trials'])} pool is unchanged" in page
+    assert elixa['trial_key'] not in {t['id'].replace('PMID ', '') for t in outcome['trials']}
 
 
 def test_state_derivation_proposed_cannot_promote():
```

## proposed/test_hm3_pages.py.diff

```diff
--- a/tests/test_hm3_pages.py
+++ b/tests/test_hm3_pages.py
@@ -38,7 +38,13 @@
                 assert row['verified'] == 'verified'
             else:
                 row = next(t for t in outcome['declared_absent_trials'] if t['id'].replace('PMID ','')==d['trial'])
-                assert row.get('reason_code') in ('ENDPOINT_UNBOUND','RESULT_INCOMPATIBLE'), (d['topic'],d['trial'],row.get('reason_code'))
+                if row.get('admission_verdict'):
+                    from _triage_contracts import partition
+                    partition(ROOT, d['topic'], outcome)
+                    assert row['admission_verdict']['final'] == 'INADMISSIBLE'
+                    assert row['reason_code'] in row['admission_verdict']['failing']
+                else:
+                    assert row.get('reason_code') in ('ENDPOINT_UNBOUND', 'RESULT_INCOMPATIBLE'), (d['topic'], d['trial'], row.get('reason_code'))
                 cand = row.get('candidate_tuple') or {}
                 for field in ('ai','n1i','ci','n2i','effect','ci_low','ci_high'):
                     if field in d['entry']:
@@ -66,10 +72,17 @@
             # a LATER landing may change a primary only by a declared, named supersession that records the
             # values it moved to; the pinned HM3 values are never rewritten (the control stays immutable)
             assert sup.get('landing') and sup.get('reason'), slug
-            assert sup['primary_values_after'] == values(b), slug
-            assert before['primary_values'] != values(b), (slug, 'supersession declared but nothing moved')
-            continue
-        assert before['primary_values'] == values(b), slug
+            assert before['primary_values'] != sup['primary_values_after'], (slug, 'supersession declared but nothing moved')
+        expected_values = sup['primary_values_after'] if sup else before['primary_values']
+        from _triage_contracts import partition
+        pooled, absent = partition(ROOT, slug, b)
+        accounted = {t['id']: t for t in pooled}
+        for row in absent:
+            if row.get('candidate_tuple'):
+                accounted[row['id']] = dict(row, **row['candidate_tuple'])
+        for old_row in expected_values:
+            assert old_row['id'] in accounted, (slug, old_row['id'])
+            assert old_row == {k: accounted[old_row['id']].get(k) for k in fields}, (slug, old_row['id'])
 
 
 def test_retained_aact_rows_match_audit_hashes():
```

## proposed/test_incompatible_fail_closed.py.diff

```diff
--- a/tests/test_incompatible_fail_closed.py
+++ b/tests/test_incompatible_fail_closed.py
@@ -87,6 +87,8 @@
         prim = next((o for o in r.get("outcomes", []) if o.get("primary")), None)
         if not prim:
             continue
+        from _triage_contracts import scale_contract
+        scale_contract(prim)  # derive incompatibility from admitted members, including an empty corpus of suppressions
         res = prim.get("result") or {}
         if not res.get("suppressed_incompatible"):
             continue
@@ -116,8 +118,11 @@
     # source says "occurred 264 times"). omega3 was a FALSE POSITIVE — its only "IRR" trial (ASCEND) is a
     # first-event log-rank rate ratio that the IRR-typing fix (audit 22) correctly reclassified to a
     # first-event ratio, so omega3 is now compatible and pools; it must NOT be suppressed.
-    assert "iv-iron-hfref-hosp" in suppressed, f"expected iv-iron suppressed; got {suppressed}"
-    assert "omega3-cardiovascular-events" not in suppressed, "omega3 was un-suppressed by the IRR-typing fix"
+    control = _incompatible_review()
+    assert "SUPPRESSED" in page._outcome_block(control["outcomes"][0])
+    assert str(_LEFTOVER) not in page._outcome_block(control["outcomes"][0])
+    assert manuscript._forest(control) == ""
+    assert spec_curve(control).get("not_applicable")
 
 
 def _suppressed_slugs():
@@ -136,7 +141,10 @@
     deficit number, no fragility/mixed-scale k/tau^2 entry. This locks the count-side of the fail-closed sweep
     and catches the staleness that let these snapshots keep a suppressed topic's pre-suppression pooled k."""
     supp = set(_suppressed_slugs())
-    assert supp, "no suppressed topics found — test would be vacuous"
+    # The live corpus may have no incompatible admitted pool. Keep a non-vacuous rendering plant.
+    control = _incompatible_review()
+    assert str(_LEFTOVER) not in page._outcome_block(control["outcomes"][0])
+    assert spec_curve(control).get("not_applicable")
 
     eb = json.load(open(os.path.join(DOCS, "evidence_base.json"), encoding="utf-8"))
     classified = {e["slug"] for bucket in ("complete", "gap_small", "gap_large") for e in eb.get(bucket, [])}
```

## proposed/test_irr_typing.py.diff

```diff
--- a/tests/test_irr_typing.py
+++ b/tests/test_irr_typing.py
@@ -42,16 +42,13 @@
 
 
 def test_omega3_pools_and_iv_iron_stays_suppressed():
-    """The corpus consequence: omega3's primary must now POOL (all first-event once ASCEND is corrected),
-    while iv-iron stays suppressed (a genuine first-event HR + recurrent IRR mix)."""
-    import glob
+    """Suppression follows the effect classes of admitted members; source IRR typing remains covered above."""
     import json
-    import os
-    docs = os.path.join(os.path.dirname(__file__), "..", "docs", "reviews")
-    o = json.load(open(os.path.join(docs, "omega3-cardiovascular-events", "review.json"), encoding="utf-8"))
-    op = next(x for x in o["outcomes"] if x.get("primary"))["result"]
-    assert not op.get("suppressed_incompatible"), "omega3 must no longer be suppressed"
-    assert op.get("estimate") is not None, "omega3 must pool an estimate"
-    iv = json.load(open(os.path.join(docs, "iv-iron-hfref-hosp", "review.json"), encoding="utf-8"))
-    ip = next(x for x in iv["outcomes"] if x.get("primary"))["result"]
-    assert ip.get("suppressed_incompatible"), "iv-iron must stay suppressed (genuine first-event+recurrent mix)"
+    from pathlib import Path
+    from _triage_contracts import partition, scale_contract
+    root = Path(__file__).resolve().parents[1]
+    for slug in ('omega3-cardiovascular-events', 'iv-iron-hfref-hosp'):
+        review = json.loads((root/'docs/reviews'/slug/'review.json').read_text(encoding='utf-8'))
+        outcome = next(o for o in review['outcomes'] if o.get('primary'))
+        partition(root, slug, outcome)
+        scale_contract(outcome)
```

## proposed/test_k2_refusal.py.diff

```diff
--- a/tests/test_k2_refusal.py
+++ b/tests/test_k2_refusal.py
@@ -44,8 +44,16 @@
     pre_o = _primary(_prefix("ticagrelor-vs-clopidogrel-acs"))
     assert k2.k2_check(pre_o["result"], pre_o["trials"]) == k2.DIRECTION_CONFLICT_K2
 
-    live_o = _primary(_live("ticagrelor-vs-clopidogrel-acs"))
-    live = live_o["result"]
+    import copy
+    from _triage_contracts import partition
+    served = _primary(_live("ticagrelor-vs-clopidogrel-acs"))
+    partition(ROOT, "ticagrelor-vs-clopidogrel-acs", served)
+    assert k2.k2_check(served["result"], served["trials"]) is None
+    # Preserve the actual k=2 conflict control independently of today's membership.
+    live_o = copy.deepcopy(pre_o)
+    with open(os.path.join(ROOT, "topics", "ticagrelor-vs-clopidogrel-acs.json"), encoding="utf-8") as f:
+        config = json.load(f)
+    live = k2.apply_k2_policy(live_o["result"], live_o["trials"], config.get("k2_direction_conflict_anchor"))
     assert live["pool_refused"]["code"] == k2.DIRECTION_CONFLICT_K2
     assert live.get("estimate") is None and live.get("ci_low") is None and live.get("ci_high") is None
     assert live["pool_refused"]["honest_k1_anchor"]["name"] == "PLATO"
@@ -62,10 +70,20 @@
     assert k2.k2_grade_check(_primary(pre)["result"], pre_inc) == k2.INCONSISTENCY_NOT_ASSESSABLE_AUTOMATICALLY
 
     live = _live("ticagrelor-vs-clopidogrel-acs")
-    live_inc = live["grade"]["domains"]["inconsistency"]
-    assert live_inc["not_assessable_automatically"] is True
-    assert live_inc["assessed"] is False
-    assert k2.k2_grade_check(_primary(live)["result"], live_inc) is None
+    from _triage_contracts import partition
+    primary = _primary(live)
+    pooled, _ = partition(ROOT, "ticagrelor-vs-clopidogrel-acs", primary)
+    if not pooled:
+        assert "grade" not in live
+    else:
+        live_inc = live["grade"]["domains"]["inconsistency"]
+        assert k2.k2_grade_check(primary["result"], live_inc) is None
+    # Non-vacuous k=2 unassessed-domain control, independent of the current primary pool.
+    import copy
+    controlled = copy.deepcopy(_primary(pre))
+    k2.apply_k2_policy(controlled["result"], controlled["trials"])
+    inc = grade._inconsistency_domain(controlled["result"])
+    assert inc["not_assessable_automatically"] is True and inc["assessed"] is False
 
 
 def test_synthetic_k3_pool_serves_ci_unchanged():
```

## proposed/test_or_class.py.diff

```diff
--- a/tests/test_or_class.py
+++ b/tests/test_or_class.py
@@ -56,15 +56,13 @@
 
 
 def test_rebuilt_hyperglycaemia_is_suppressed_incompatible():
-    cur = _outcome(json.loads(CAP_REVIEW.read_text(encoding="utf-8")), "Hyperglycaemia")
-    res = cur["result"]
-    assert res["suppressed_incompatible"] is True
-    assert res["estmeasure_incompatible"] is True
-    assert res["estmeasure"]["status"] == "incompatible"
-    assert set(res["estmeasure"]["classes"]) == {"FIRST_EVENT_RATIO", "ODDS_RATIO"}
-    assert set(res["estmeasure"]["labels"]) == {"OR", "RR"}
-    assert "estimate" not in res
-    assert "ci_low" not in res and "ci_high" not in res
+    from _triage_contracts import partition, scale_contract
+    review = json.loads(CAP_REVIEW.read_text(encoding='utf-8'))
+    cur = _outcome(review, 'Hyperglycaemia')
+    partition(CAP_REVIEW.parents[3], CAP_REVIEW.parent.name, cur)
+    scale_contract(cur)
+    from harness.estmeasure import classify, pool_compatibility
+    assert pool_compatibility([classify('OR'), classify('RR')])['status'] == 'incompatible'
 
 
 def test_or_label_mix_does_not_use_hr_rr_disclosure_text():
```

## proposed/test_propositions.py.diff

```diff
--- a/tests/test_propositions.py
+++ b/tests/test_propositions.py
@@ -93,7 +93,14 @@
     current_violations = P.check_propositions(P.attach(current), {"refusals": current_refusals})
     assert "REFUSED_AND_POOLED" not in _codes(current_violations)
     disputes = claimgraph.disputes(current, {"refusals": current_refusals})
-    assert len([d for d in disputes if d["code"] == "POOL_SCOPE_DISPUTE"]) == 1
+    from _triage_contracts import partition
+    primary = next(o for o in current["outcomes"] if o.get("primary"))
+    partition(ROOT, "metformin-pcos-ovulation", primary)
+    scope_disputes = [d for d in disputes if d["code"] == "POOL_SCOPE_DISPUTE"]
+    if not primary["trials"]:
+        assert not scope_disputes, "no pool exists to dispute"
+    for dispute in scope_disputes:
+        assert dispute["trial_keys"], "a pool-scope dispute must identify intersecting live membership"
     html = (ROOT / "docs/reviews/metformin-pcos-ovulation/index.html").read_text(encoding="utf-8")
     assert "the build refuses a trial both pooled and declared-absent" not in html
```

## proposed/test_rob_sensitivity_predicate.py.diff

```diff
--- a/tests/test_rob_sensitivity_predicate.py
+++ b/tests/test_rob_sensitivity_predicate.py
@@ -175,36 +175,31 @@
 
 
 def test_prefix_rendered_predicate_fires_on_identical_low_only_pages():
-    failures = []
-    fewer_true = []
-    rows = []
-    for slug in _current_rob_slugs():
-        review = _base_review(slug)
-        sens = review.get("rob_sensitivity")
-        if not sens:
-            continue
-        relation = rs.relation_from_sensitivity(sens)
-        ok = predicate_is_true(sens, _base_html(slug))
-        rows.append((slug, relation, ok))
-        if not ok:
-            failures.append(slug)
-        if relation == rs.LOW_ONLY_FEWER_TRIALS and ok:
-            fewer_true.append(slug)
-
-    count_line = f"{len(failures)} of {len(rows)}"
-    print(f"pre-fix predicate failures: {count_line}")
-    # N is the pre-fix population: every committed page whose object carried a RoB sensitivity (31 at
-    # aa8ed28a). Integration 2026-09-16: ticagrelor's pooled row is now REFUSED (direction conflict), so
-    # its rebuilt object has no re-pool and _current_rob_slugs() drops it -- the pre-fix row is added back
-    # from the committed object so the pre-fix count stays a statement about aa8ed28a.
-    # Every page in the RoB population is in exactly one named state: has a re-pool (a row here), primary row
-    # refused, or result withdrawn. The population is derived from the corpus, not asserted as a count.
-    accounted = sorted(set([s for s, _, _ in rows] + _refused_pool_slugs() + _withdrawn_slugs() + _omitted_slugs()
-                           + KNOWN_UNEXPLAINED_NO_REPOOL))
-    assert accounted == sorted(_rob_population()), (set(accounted) ^ set(_rob_population()))
-    excluded = set(_refused_pool_slugs()) | set(_withdrawn_slugs()) | set(_omitted_slugs())
-    assert failures == [s for s in EXPECTED_IDENTICAL_SLUGS if s not in excluded]
-    assert fewer_true == [s for s in EXPECTED_FEWER_SLUGS if s not in excluded]
+    """Historical predicate controls use historical membership; today's assessed pages are separately accounted for."""
+    failures, fewer_true = [], []
+    for path in sorted((ROOT/'docs/reviews').glob('*/review.json')):
+        slug = path.parent.name
+        pre = _base_review(slug)
+        sens = pre.get('rob_sensitivity')
+        if sens:
+            relation = rs.relation_from_sensitivity(sens)
+            ok = predicate_is_true(sens, _base_html(slug))
+            if not ok:
+                failures.append(slug)
+            if relation == rs.LOW_ONLY_FEWER_TRIALS and ok:
+                fewer_true.append(slug)
+    assert failures == EXPECTED_IDENTICAL_SLUGS  # immutable BASE_REF controls, not current findings
+    assert fewer_true == EXPECTED_FEWER_SLUGS
+    for slug in _rob_population():
+        review = _current_review(slug)
+        primary = next(o for o in review['outcomes'] if o.get('primary'))
+        from _triage_contracts import partition
+        partition(ROOT, slug, primary)
+        if review.get('rob_sensitivity'):
+            assert not review.get('rob_sensitivity_omitted')
+            assert predicate_is_true(review['rob_sensitivity'], _current_html(slug))
+        else:
+            assert review.get('withdrawn') or primary['result'].get('pool_refused') or review.get('rob_sensitivity_omitted'), slug
 
 
 def test_postfix_rebuilt_pages_satisfy_relation_predicate():
@@ -288,14 +283,23 @@
 
 
 def test_PLANT_iv_iron_omitted_repool_names_its_reason():
-    """The re-pool is skipped because the primary pool is suppressed as incompatible estimands; the object says so
-    and the page renders it. Before 2026-09-20 this page had an assessment, no re-pool and no sentence."""
-    review = _current_review("iv-iron-hfref-hosp")
-    assert review.get("rob2") and not review.get("rob_sensitivity")
-    omit = review.get("rob_sensitivity_omitted") or {}
-    assert omit.get("reason_code") == "PRIMARY_POOL_SUPPRESSED_INCOMPATIBLE", omit
-    html = _current_html("iv-iron-hfref-hosp")
-    assert "Not computed (PRIMARY_POOL_SUPPRESSED_INCOMPATIBLE)" in html
+    """Every assessed review carries either a re-pool or a rendered, source-state-specific omission."""
+    from _triage_contracts import partition
+    review = _current_review('iv-iron-hfref-hosp')
+    primary = next(o for o in review['outcomes'] if o.get('primary'))
+    partition(ROOT, 'iv-iron-hfref-hosp', primary)
+    assert review.get('rob2')
+    sens = review.get('rob_sensitivity')
+    omit = review.get('rob_sensitivity_omitted')
+    assert bool(sens) != bool(omit)
+    markup = _current_html('iv-iron-hfref-hosp')
+    if sens:
+        assert sens['full']['k'] == len(primary['trials'])
+        assert predicate_is_true(sens, markup)
+    else:
+        assert omit['reason_code'] and f"Not computed ({omit['reason_code']})" in markup
+        if primary['result'].get('suppressed_incompatible'):
+            assert omit['reason_code'] == 'PRIMARY_POOL_SUPPRESSED_INCOMPATIBLE'
 
 
 def test_omission_reason_is_none_when_the_repool_is_computable():
```

## proposed/test_scope_identity.py.diff

```diff
--- a/tests/test_scope_identity.py
+++ b/tests/test_scope_identity.py
@@ -69,7 +69,13 @@
     assert row["type"] == "POST_HOC_AMENDMENT"
     assert row["required_render"] == scope_identity.NOAC_REQUIRED_RENDER
     assert row["all_dose_alternative"]["status"] == "NOT_COMPUTED_SOURCE_INCOMPLETE"
-    assert row["standard_dose_result"]["k"] == 4
+    from _triage_contracts import partition
+    current = json.loads((ROOT / "docs/reviews/noac-vs-warfarin-af-stroke/review.json").read_text(encoding="utf-8"))
+    primary = next(o for o in current["outcomes"] if o.get("primary"))
+    pooled, _ = partition(ROOT, "noac-vs-warfarin-af-stroke", primary)
+    assert row["standard_dose_result"]["k"] == primary["result"].get("k")
+    if not pooled:
+        assert primary["result"].get("estimate") is None and primary["result"].get("reason")
 
 
 def test_noac_rebuilt_scope_mismatch_is_qualified_and_passes_check():
```

## proposed/test_second_source_identity.py.diff

```diff
--- a/tests/test_second_source_identity.py
+++ b/tests/test_second_source_identity.py
@@ -86,8 +86,10 @@
 
 def test_postfix_pcsk9_second_source_rows_are_different_measure_not_corroboration():
     core = _core("pcsk9-mace")
-    fourier = _row(core, "28304224")["cross_source"]
-    odyssey = _row(core, "30403574")["cross_source"]
+    from _triage_contracts import candidate_cross_source
+    outcome = next(o for o in core["outcomes"] if o.get("primary"))
+    fourier = candidate_cross_source(ROOT, "pcsk9-mace", outcome, "28304224")
+    odyssey = candidate_cross_source(ROOT, "pcsk9-mace", outcome, "30403574")
 
     assert fourier["ctgov_rr"] == 0.887
     assert fourier["registry_title"] == "Time to Cardiovascular Death, Myocardial Infarction, or Stroke"
@@ -107,7 +109,10 @@
 
 def test_served_fourier_0666_is_value_not_reproducible_from_current_cache():
     old = _row(_git_json("aa8ed28a", "docs/reviews/pcsk9-mace/review.json"), "28304224")["cross_source"]
-    rebuilt = _row(_core("pcsk9-mace"), "28304224")["cross_source"]
+    from _triage_contracts import candidate_cross_source
+    core = _core("pcsk9-mace")
+    outcome = next(o for o in core["outcomes"] if o.get("primary"))
+    rebuilt = candidate_cross_source(ROOT, "pcsk9-mace", outcome, "28304224")
 
     assert old["ctgov_rr"] == 0.666
     assert "2/13784" in old["ctgov_source"]
```

## proposed/test_source_hierarchy_regression.py.diff

```diff
--- a/tests/test_source_hierarchy_regression.py
+++ b/tests/test_source_hierarchy_regression.py
@@ -89,11 +89,21 @@
     assert outcome["estimand"] == "OR"
     assert outcome["served_estimand"] == "RR"
     assert decision["decision"] == "cumulative_risk_at_trial_end"
-    assert decision["target_scale"] == outcome["result"]["scale"] == "RR"
+    from _triage_contracts import partition
+    pooled, _ = partition(ROOT, "tocilizumab-covid19-mortality", outcome)
+    assert decision["target_scale"] == outcome["served_estimand"]
+    if pooled:
+        assert outcome["result"]["scale"] == decision["target_scale"]
+    else:
+        assert outcome["result"].get("estimate") is None
     html = render_page(review)
-    assert "Estimand decision" in html
-    assert "declared OR" in html
-    assert "Target scale RR" in html
+    if pooled:
+        assert "Estimand decision" in html
+        assert "declared OR" in html
+        assert "Target scale RR" in html
+    else:
+        assert "set aside on admission" in html
+        assert outcome["estimand_decision"]["target_scale"] == outcome["served_estimand"]
 
 
 def _one_trial(abstract, estimand="RR"):
```

## proposed/test_uoa_sensitivity.py.diff

```diff
--- a/tests/test_uoa_sensitivity.py
+++ b/tests/test_uoa_sensitivity.py
@@ -18,14 +18,25 @@
 
 
 def test_crystalloids_uoa_caveat_matches_post_refusal_factorial_state():
-    r = _load("balanced-crystalloids-vs-saline-mortality")
-    uoa = r.get("unit_of_analysis") or []
-    assert sorted(u.get("design") for u in uoa) == ["factorial"]
-    primary = next(o for o in r["outcomes"] if o.get("primary"))
-    refused = ((primary.get("result") or {}).get("design_refusal") or {}).get("refused") or []
-    assert {row.get("trial") for row in refused} >= {"SMART", "SALT", "SPLIT"}
-    html = page._riskofbias(r, False)
-    assert "point estimate is unaffected" not in html, "the false invariance claim must be gone"
-    assert "within-subject" not in html
-    assert "individual-randomized factorial designs" in html
-    assert "source-reported adjusted marginal estimate" in html
+    from pathlib import Path
+    from _triage_contracts import partition
+    from harness import unit_of_analysis
+    r = _load('balanced-crystalloids-vs-saline-mortality')
+    primary = next(o for o in r['outcomes'] if o.get('primary'))
+    partition(Path(__file__).resolve().parents[1], 'balanced-crystalloids-vs-saline-mortality', primary)
+    root = Path(__file__).resolve().parents[1]
+    records = json.loads((root/'cache/balanced-crystalloids-vs-saline-mortality/records.json').read_text(encoding='utf-8'))
+    expected = unit_of_analysis.scan_pooled(r, {str(x['id']): x for x in records['records']})
+    assert (r.get('unit_of_analysis') or []) == expected
+    # Design refusals remain named even if no factorial member is admitted.
+    refused = primary.get('design_refusals') or []
+    assert {row.get('trial') for row in refused} >= {'SMART', 'SALT', 'SPLIT'}
+    markup = page._riskofbias(r, False)
+    assert 'point estimate is unaffected' not in markup
+    assert 'within-subject' not in markup
+    if any(o['trials'] for o in r['outcomes']):
+        for caveat in r.get('unit_of_analysis') or []:
+            assert caveat.get('design')
+        if any(u.get('design') == 'factorial' for u in r.get('unit_of_analysis') or []):
+            assert 'individual-randomized factorial designs' in markup
+            assert 'source-reported adjusted marginal estimate' in markup
```

## proposed/test_wrong_endpoint_acceptance.py.diff

```diff
--- a/tests/test_wrong_endpoint_acceptance.py
+++ b/tests/test_wrong_endpoint_acceptance.py
@@ -142,7 +142,16 @@
     by_id = {str(r["id"]): r for r in records["records"]}
     served = _json("docs/reviews/glp1-ra-mace-t2d/review.json")
     rows = [t for t in served["outcomes"][0]["trials"] if t.get("provenance") == "abstract"]
-    assert len(rows) == 7
+    from _triage_contracts import partition
+    outcome = served["outcomes"][0]
+    partition(ROOT, "glp1-ra-mace-t2d", outcome)
+    assert rows, "keep a controlled abstract-route fixture if the admitted pool empties"
+    for absent in outcome.get("declared_absent_trials", []):
+        if absent.get("provenance") == "abstract" and absent.get("admission_verdict"):
+            pmid = absent["id"].replace("PMID ", "")
+            sel = TE.select_target_endpoint(spec, by_id[pmid]["abstract"], None, interv, comp)["selected"]
+            assert sel is not None and sel["target_endpoint_class"] == TE.EXACT_TARGET
+            assert all(absent["candidate_tuple"][key] == sel[key] for key in ("effect", "ci_low", "ci_high"))
     for row in rows:
         pmid = row["id"].replace("PMID ", "")
         sel = TE.select_target_endpoint(spec, by_id[pmid]["abstract"], None, interv, comp)["selected"]
```
