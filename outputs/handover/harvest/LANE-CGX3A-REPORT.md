# CGX3A report — INCOMPLETE / NOT READY

HEAD: `c57e8727afe8a7cce757b879fea76cec337c4298` (expected base `refs/lanes/landing4-wip`). No commit or push.

The lane finish condition is **not met**. The renderer migration is partial and
the required rebuild fails both before and after edits. This report does not
equate a registered judgement with verified evidence or fresh rendering with a
successful rebuild.

## Baseline and build blocker

The required initial command, before implementation changes, was
`python scripts/build_topic.py glp1-ra-mace-t2d --now 2026-09-11`.
It failed with `ValueError: no studies to pool`, in `glp1.strands` after the
primary trial list became empty. The same post-edit command failed identically.
The generated refusal records in `LANE-CGX3A-BUILD-BLOCKER.json` show six
analysis-set unknowns, two censoring unknowns and two endpoint-component
mismatches. These existing fail-closed decisions were not overridden.
Membership, screening, synthesis and gate were left untouched; no artificial
input was injected. See `LANE-CGX3A-REBUILD.txt` for the traceback.

Consequently the baseline was regenerated using `scripts/claim_scope_sweep.py`
against the existing committed review and served HTML, followed by a scoped
fresh-renderer census on that same snapshot. It is **not** a successful rebuilt
baseline. The served canonical page was not overwritten with a preview.

## Numeric plant, first on base

`CGX3A_PLANT_FAIL=1 python -m pytest -q tests/test_cgx3a_plant.py --tb=short`
appended a typed number to the actual base overview fragment, not an object.
Failing output (verbatim):

```text
F                                                                        [100%]
================================== FAILURES ===================================
______________________ test_unregistered_overview_number ______________________
tests\test_cgx3a_plant.py:15: in test_unregistered_overview_number
    assert not planted, json.dumps(planted, indent=2)
E   AssertionError: [
E       {
E         "code": "SENTENCE_WITHOUT_OBJECT",
E         "kind": "unregistered",
E         "claim_id": "",
E         "detail": "There were 987654 pooled trials.",
E         "unit_id": "unit-0104",
E         "context": "p"
E       }
E     ]
E   assert not [{'claim_id': '', 'code': 'SENTENCE_WITHOUT_OBJECT', 'context': 'p', 'detail': 'There were 987654 pooled trials.', ...}]
=========================== short test summary info ===========================
FAILED tests/test_cgx3a_plant.py::test_unregistered_overview_number - Asserti...
1 failed in 8.23s
```

The normal form of this test asserts that this violation is present. No scanner
exemption or string whitelist was added.

## Fresh-renderer census

Scope: overview, efficacy outcome blocks (including their input/type text),
strands, known-missing panel, and the B-prime provenance table. The harms tab,
eligibility table and other sibling sections are excluded. Units are visible
prose/table text runs, not linguistic sentences; semantic table-header rules
are inherited from the existing scanner.

| Section | Base registered / units | After registered / units |
|---|---:|---:|
| overview | 0 / 89 | 1 / 88 |
| outcome blocks | 10 / 145 | 11 / 146 |
| strands | 2 / 2 | 2 / 2 |
| known-missing panel | 0 / 0 | 0 / 0 |
| provenance table | 0 / 88 | 33 / 33 |
| Total | 12 / 324 | 47 / 269 |

The denominator changed because eight unregistered provenance cells per member
became three complete typed units, and legacy aggregate prose was replaced.
The source fields remain visible. No known-missing panel exists in this GLP-1
snapshot: 0/0 is absence of a rendered panel, not proof its general renderer
has been migrated. Strands were already 2/2 on base.

## Changes and limits

- `harness/claimgraph.py`: reusable per-item state transformation and located
  provenance transformation; registry integration; source classifications remain
  JUDGEMENT/OWED with recorded basis. Source locations fail closed when source
  verification fails. Offsets are recomputed from held text, not trusted from a
  stored offset. The provenance table unions all strand members rather than
  assuming the last strand contains every member.
- `harness/page.py`: overview/outcome aggregate counts derive from actual item
  states; suppressed or refused input rows are labelled Candidate. Removed
  duplicated unregistered numeric renderings where no additional endpoint-count
  data would be lost. Legacy prose still outside typed contracts remains debt.
- `harness/glp1.py`: only the owned provenance-table renderer changed; membership
  and other sibling renderer sections were not rewritten.
- No new INTERPRETATION objects were added. The existing FLOW interpretation
  retains its rendered alternative; the browser contract checks it. Certainty
  still recomputes from start and domain downgrades, with missing assessments
  producing provisional. There is no new string-based STRUCTURAL classifier.

The scoped after count describes the fresh renderer on committed review.json.
Served HTML remains the base page, because the build failed. Full before/after
scanner records are in `LANE-CGX3A-BASELINE-SWEEP.json` and
`LANE-CGX3A-AFTER-SWEEP.json`; scoped records are in the corresponding BASELINE
and AFTER JSON files. Complete migration is independent unfinished work, not
proved impossible merely because rebuilding is blocked.

## Static versus dynamic disclosure

| Component | Static | Dynamic / evidence |
|---|---|---|
| Labels and operation names | Renderer templates | No research values |
| Counts and predicates | Formatting and refusal policy | Per-item input rows, result state and absence/refusal states |
| Provenance locations | Allowed-path policy inherited | Held bytes, committed-byte verification, digest and located span |
| Source hierarchy / censoring / analysis / timepoint | OWED adjudication policy | Recorded member fields; independent adjudication not claimed |
| Effect sizes and intervals | None introduced | Existing FACT rows and source spans |
| Certainty | Existing ordinal scale and domain arithmetic | Domain assessments and downgrades; provisional when incomplete |

## Source and UI review

`LANE-CGX3A-SECOND-PASS.json` records checks on 11 member identifiers against
held records, source spans containing effect/CI values, matching committed bytes
and digests, and parseable recorded retrieval dates. No new publication dates or
research identifiers were authored. Recorded retrieval dates are not independently
established fetch timestamps. The graph check returned zero violations; certainty
recomputed to provisional. The fresh-renderer browser contract uses an absolute
127.0.0.1:8000 URL, checks typed provenance, interpretation alternative, aggregate
count, all tabs and absence of JavaScript errors, and blocks nonlocal requests.

## Test summaries

Focused command:
`python -m pytest -q tests/test_cgx3a_plant.py tests/test_cgx3a_prose.py tests/test_page.py tests/test_claimgraph_typed.py tests/test_claimgraph.py tests/test_claimgraph_dispute.py`

```text
............................................                             [100%]

44 passed in 43.69s
```

Default full suite: `python -m pytest -q`

```text
=================================== ERRORS ====================================

_______________ ERROR collecting tests/test_search_v2_isrctn.py _______________

import file mismatch:

imported module 'test_search_v2_isrctn' has this __file__ attribute:

  C:\mh-r-CGX3A\outputs\search_v2\lanes\R2\test_search_v2_isrctn.py

which is not the same as the test file we want to collect:

  C:\mh-r-CGX3A\tests\test_search_v2_isrctn.py

HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules

=========================== short test summary info ===========================

ERROR tests/test_search_v2_isrctn.py

!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!

1 error in 9.43s
```

Full-suite retry: `python -m pytest -q --import-mode=importlib`
The runner refuses outbound Python socket connections and allows local UI hosts.
This full run finished with 23 failures and 899 passes before the final
label/contract correction. Four failed page-contract assertions were revised
to check state-derived counts, named inputs and typed scale renderings; those
tests are included in the final focused run above. The other 19 failed tests
remain unresolved. A green final full suite is not claimed, and the full suite
was not rerun after the final focused corrections. The remaining failures have
not all been independently demonstrated on an untouched baseline.

```text
=========================== short test summary info ===========================
FAILED tests/test_cross_source_endpoint.py::test_rebuilt_fourier_row_is_different_measure_not_corroboration
FAILED tests/test_effect_type.py::test_current_glp1_baseline_plant - Assertio...
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
FAILED tests/test_gate.py::test_valid_page_passes_non_replay_limbs - Assertio...
FAILED tests/test_gate_scorecard.py::test_real_registry_passes - AssertionErr...
FAILED tests/test_glp1_lane.py::test_glp1_elixa_located_and_primary_membership
FAILED tests/test_glp1_lane.py::test_glp1_freedom_sensitivity_never_pooled - ...
FAILED tests/test_harms_recovery.py::test_postfix_noac_major_bleeding_recovers_four_trials
FAILED tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews
FAILED tests/test_override_audit.py::test_override_audit_covers_every_committed_override
FAILED tests/test_page.py::test_overview_names_the_pooled_trials - assert 'Tr...
FAILED tests/test_page.py::test_mixed_scale_pool_labelled_mixed_not_a_single_clean_scale
FAILED tests/test_page.py::test_reconciliation_when_included_exceeds_pooled
FAILED tests/test_page.py::test_all_pooled_equals_screened_states_so - assert...
FAILED tests/test_second_source_identity.py::test_postfix_pcsk9_second_source_rows_are_different_measure_not_corroboration
FAILED tests/test_second_source_identity.py::test_served_fourier_0666_is_value_not_reproducible_from_current_cache
FAILED tests/test_stage_additions.py::test_manuscript_limb_passes_on_every_live_review
FAILED tests/test_stage_additions.py::test_error_rate_is_fresh_against_current_pooled_population
FAILED tests/test_verified_effects.py::test_verified_effect_pooled_and_verified
FAILED tests/test_verified_effects.py::test_dose_selection_overrides_abstract_dose_and_verifies
FAILED tests/test_verified_override.py::test_without_override_abstract_selects_the_wrong_endpoint
FAILED tests/test_verified_override.py::test_override_corrects_to_major_vascular_events
FAILED tests/test_verified_override.py::test_unflagged_verified_effect_does_not_override
23 failed, 899 passed in 766.30s (0:12:46)
```

## Corpus measurement (no repairs outside the lane)

`python scripts/claim_scope_sweep.py --output LANE-CGX3A-CORPUS-SWEEP.json`

| Page | Served registered / units | Fresh registered / units |
|---|---:|---:|
| balanced-crystalloids-vs-saline-mortality | 0 / 931 | 19 / 932 |
| colchicine-postop-af | 0 / 1469 | 21 / 1470 |
| colchicine-recurrent-pericarditis | 0 / 1075 | 21 / 1078 |
| colchicine-secondary-cv-prevention | 0 / 2465 | 21 / 2465 |
| corticosteroids-cap-mortality | 0 / 1929 | 20 / 1930 |
| corticosteroids-covid19-mortality | 0 / 1026 | 16 / 1027 |
| dapagliflozin-hfpef-hosp | 0 / 1267 | 15 / 1267 |
| denosumab-vertebral-fracture | 0 / 1021 | 20 / 1025 |
| doac-vte-recurrence | 0 / 2584 | 19 / 2584 |
| dpp4-mace-t2d | 0 / 799 | 17 / 799 |
| empagliflozin-hfpef-hosp | 0 / 1298 | 15 / 1298 |
| esketamine-trd-madrs | 0 / 1685 | 18 / 1686 |
| finerenone-ckd-t2d-renal | 0 / 772 | 18 / 774 |
| glp1-ra-mace-t2d | 27 / 1129 | 64 / 1076 |
| iv-iron-hfref-hosp | 0 / 1028 | 13 / 1025 |
| melatonin-primary-insomnia-sol | 0 / 1658 | 16 / 1659 |
| metformin-pcos-ovulation | 0 / 1995 | 19 / 1997 |
| noac-vs-warfarin-af-stroke | 0 / 882 | 23 / 882 |
| omega3-cardiovascular-events | 0 / 2301 | 24 / 2302 |
| pcsk9-mace | 0 / 678 | 19 / 680 |
| probiotics-aad-prevention | 0 / 7118 | 32 / 7120 |
| sacubitril-valsartan-hfref | 0 / 1138 | 15 / 1139 |
| semaglutide-obesity-mace | 0 / 947 | 17 / 949 |
| semaglutide-obesity-weight | 0 / 1852 | 17 / 1853 |
| sglt2-ckd-progression | 0 / 1113 | 20 / 1114 |
| sglt2-hfref-hosp-cvdeath | 0 / 749 | 18 / 751 |
| sglt2-primary-prevention-hf | 0 / 3080 | 18 / 3080 |
| spironolactone-hfref-mortality | 0 / 2490 | 18 / 2492 |
| statins-primary-prevention-elderly | 0 / 773 | 18 / 775 |
| ticagrelor-vs-clopidogrel-acs | 0 / 686 | 18 / 688 |
| tocilizumab-covid19-mortality | 0 / 1295 | 19 / 1296 |
| tranexamic-acid-pph | 0 / 1169 | 18 / 1170 |

## Exact residual units and reasons

Every residual occurrence is listed below; repeated text is not deduplicated.
These are unfinished migrations, not claims that source-backed registration is
impossible. The existing scanner continues to reject them.

### overview

- `unit-0001` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "In adults with type 2 diabetes, do GLP-1 receptor agonists reduce 3-point major adverse cardiovascular events versus placebo? (Double-blind placebo-controlled RCTs.)"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0002` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, superseded, or unproven, so the result must not be read as a settled current estimate:"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0003` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "no genuine executed concept search (PMID_ENUMERATION_explicit): search.retrieval.enumeration_only=true; no discovery-capable concept source ran"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0004` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Identifier scope: identifier leading token matches class term GLP-1RA. Verdict: NOT_APPLICABLE."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0005` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this topic. an auditable screening ledger attached to an unauditable retrieval process. 4 PMID-enumeration queries; 0 title/name-seeded queries; 0 free-text keyword queries."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0006` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Scope identity mismatch. Eligibility is open P/I/C/design, but retrieval is a pre-identified set. eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL)."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0007` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "This page offers greater auditability, not stronger evidence: every number traces to a committed source, every absence is declared, and any hand-edit breaks the reproduction census."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0008` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "These limitation objects are deliberately UNWIRED: no executable gate changes on the named state, so publication is allowed only because the reviewed acknowledgement is carried on the object."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0014` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "topic:glp1-ra-mace-t2d:overview:auditability-scope"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0015` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "AUDITABILITY_SCOPE"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0016` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "RECORDED"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0017` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "NOTE"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0018` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Auditability scope is a page-level provenance disclosure; no analytic gate changes its verdict when this recorded note is present."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0019` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Codex lane AD"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0020` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "2026-09-15"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0021` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "TRANCHE-hazard-consumers"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0022` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "topic:glp1-ra-mace-t2d:search:retrieval-snapshot"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0023` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "RETRIEVAL_SNAPSHOT"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0024` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "UNRECORDED"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0025` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "NOTE"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0026` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "The legacy retrieval snapshot records a replay boundary; by itself it does not constrain the pooled analytic claim."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0027` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Codex lane AD"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0028` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "2026-09-15"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0029` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "TRANCHE-hazard-consumers"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0030` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "topic:glp1-ra-mace-t2d:riskofbias:rob-spancheck"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0031` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "ROB_SPANCHECK"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0032` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "RECORDED"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0033` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "NOTE"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0034` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "RoB span-check is a reliability disclosure; no executable analytic gate changes on the recorded state."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0035` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Codex lane AD"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0036` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "2026-09-15"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0037` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "TRANCHE-hazard-consumers"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0038` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "topic:glp1-ra-mace-t2d:riskofbias:funding-coi"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0039` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "FUNDING_COI"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0040` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "PARTIAL"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0041` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "QUALIFIES_CLAIM"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0042` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Funding and conflict-of-interest are disclosed for interpretation; the harness does not estimate a per-trial funding adjustment and no analytic gate consumes the partial state."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0043` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Codex lane AD"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0044` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "2026-09-15"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0045` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "TRANCHE-hazard-consumers"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0046` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "topic:glp1-ra-mace-t2d:riskofbias:rob-sensitivity"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0047` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "ROB_SENSITIVITY"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0048` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "PARTIAL"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0049` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "QUALIFIES_CLAIM"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0050` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Risk-of-bias sensitivity is rendered as an interpretive disclosure; no executable analytic gate changes on the partial state. Integrator note: a sensitivity re-pool that moves the estimate across the null is a validity signal, not only an interpretive disclosure; a consumer is owed (GATE_GAPS)."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0051` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Codex lane AD"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0052` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "2026-09-15"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0053` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "TRANCHE-hazard-consumers"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0054` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "topic:glp1-ra-mace-t2d:riskofbias:grade-certainty"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0055` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "GRADE_CERTAINTY"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0056` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "PROVISIONAL"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0057` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "QUALIFIES_CLAIM"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0058` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "GRADE certainty is a downstream label rather than a publication gate; no executable analytic gate changes on the provisional certainty state."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0059` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Codex lane AD"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0060` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "2026-09-15"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0061` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "TRANCHE-hazard-consumers"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0062` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "topic:glp1-ra-mace-t2d:manuscript:generated-object-banner"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0063` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "AUDITABILITY_SCOPE"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0064` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "RECORDED"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0065` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "NOTE"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0066` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Auditability scope is a page-level provenance disclosure; no analytic gate changes its verdict when this recorded note is present."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0067` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Codex lane AD"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0068` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "2026-09-15"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0069` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "TRANCHE-hazard-consumers"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0070` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "topic:glp1-ra-mace-t2d:reproduction:round-2-retraction"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0071` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "REPRODUCTION_RETRACTION"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0072` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "RETRACTED"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0073` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "BLOCKS_CLAIM"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0074` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "The old byte-for-byte reproduction claim is visibly withdrawn; no current analytic gate consumes the withdrawn historical claim."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0075` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Codex lane AD"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0076` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "2026-09-15"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0077` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "TRANCHE-hazard-consumers"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0079` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "3-point major adverse cardiovascular events"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0081` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "HR"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0083` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "time_to_first_event: prefer published HR; keep reconstruction only when no HR exists Target scale HR; declared HR."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0087` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "0.86 (HR), 95% CI 0.81–0.92"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0089` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "0.75–0.99"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0091` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "0.0027 (non-zero; not 0)"

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0093` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Random-effects inverse-variance on the log ratio (log RR/OR/HR/IRR as configured for the outcome); Paule-Mandel tau^2; HKSJ 95% CI on t_{k-1} (variance floor max(1,Q/(k-1))); prediction interval mu +/- t_{k-1}*sqrt(tau2+se^2). Validated vs metafor 5.0.1 (this canonical code path; every rendered interval is gate-checked to originate here)."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0094` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "45 of 45 numerical claims on this page (100%) carry a source IDENTIFIER (a PMID/NCT/span/field). RETRACTED claim (round-2): we previously called these 'one-click sources' a reader can open — that is not verified: the identifiers are NOT rendered as resolving hyperlinks, and at least one PMCID was found to point to an unrelated article. Until every identifier is fetched and confirmed to resolve to the cited work, this is a count of identifiers present, not of sources that resolve. Each pooled number carries its PMID/NCT and verbatim span; each declared-absent trial its reason; each risk-of-bias domain the field it read; the reproduction its protocol SHA and replay. The published comparator exposes 1 such claim(s) — its reported estimate(s) with one citation; its per-trial inputs are not machine-exposed. Score: scripts/transparency_score.py (committed docs/transparency.json)."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0095` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Small k on many topics. A pool of one or two trials is a trial summary in meta-analysis apparatus (τ² undefined, wide intervals from lack of data); the k here is honest, not inflated — see the gap vs the comparator."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0096` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Open-access comparator only. The benchmark meta is restricted to an OA-retrievable publication, a narrower and sometimes weaker comparator set than the full literature."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0097` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Favourable topic sample. Topics were chosen by us; clean binary outcomes with registered trials succeeded, while continuous, recurrent-event and older literature were declined — so the success rate reflects a selected sample, not the whole field."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0098` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Risk of bias is partial. Registry-machine-signal-restricted domains are computed from machine-available registry fields; domains needing human reading are marked not-assessed."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0099` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Registry snapshot is dated. AACT is a fixed local snapshot; trials registered, or results posted, after it are invisible to the registry-first recall, ghost and registry-machine-signal-restricted signals (the snapshot date is shown on those blocks). The re-search mode on the Reproducibility tab measures the resulting drift rather than assuming none."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0100` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Dual screening is not fully independent. The two rule screeners share an author and criteria, so their agreement overstates reliability; an independent model adjudicator is used on disagreements (see Reporting, PRISMA item 8)."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.

- `unit-0101` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "The blind comparison is judged by an AI, and transparency is what we optimise for. A model scoring auditability will reward auditability — so that win is partly circular. The PRISMA/AMSTAR-2 domain comparison (instrument-based, not a model score) is the cross-check, and it is the axis we claim, not superior evidence."

  Reason: Legacy overview prose/recorded metadata has not been mapped to explicit typed inputs and adjudication or alternatives; no structural exemption is justified.


### outcome blocks

- `unit-0002` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "HR"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0004` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "time_to_first_event: prefer published HR; keep reconstruction only when no HR exists Target scale HR; declared HR."

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0006` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "intention-to-treat"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0008` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0010` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Random-effects inverse-variance on the log ratio (log RR/OR/HR/IRR as configured for the outcome); Paule-Mandel tau^2; HKSJ 95% CI on t_{k-1} (variance floor max(1,Q/(k-1))); prediction interval mu +/- t_{k-1}*sqrt(tau2+se^2). Validated vs metafor 5.0.1 (this canonical code path; every rendered interval is gate-checked to originate here)."

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0012` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "10"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0014` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "0.86 (HR), 95% CI 0.81–0.92"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0016` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "0.75–0.99"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0018` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "0.0027 (non-zero; not 0)"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0020` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "pooled trials use each trial's OWN primary composite; component sets differ across trials (varying extra components across trials: unstable angina) — the pooled estimate mixes composite definitions (disclosed, not adjusted)"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0022` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "estimate ranges 0.85–0.87 across single-trial drops; most influential: 30291013. each row drops one trial and re-pools; a stable estimate across drops = no single trial drives it."

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0024` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "FIRST_EVENT_RATIO"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0028` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "TRIAL_DEFINED_MAJOR_CORONARY_CARDIOVASCULAR_COMPOSITE"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0030` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "HOMOGENEOUS"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0032` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "CARDIOVASCULAR_DEATH; MYOCARDIAL_INFARCTION; STROKE"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0034` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial-defined (per trial listed)"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0036` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "intention-to-treat"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0039` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "follow_up_window [COMPAT_DIMENSION_HETEROGENEOUS]"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0041` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "8 of 10 pooled trials"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0046` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "follow_up_window"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0047` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "31185157"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0048` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0049` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0050` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "follow_up_window"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0051` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "27633186"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0052` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0053` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0054` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "follow_up_window"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0055` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "27295427"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0056` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0057` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0058` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "follow_up_window"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0059` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "34215025"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0060` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "1.81 years"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0061` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "participants were enrolled; 2717 were assigned to receive efpeglenatide and 1359 to receive placebo. During a median follow-up of 1.81 years, an incident MACE occurred in 189 participants (7.0%) assigned to receive efpeglenatide (3.9 events per 100 p"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0062` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "follow_up_window"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0063` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "31189511"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0064` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0065` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0066` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "follow_up_window"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0067` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "30291013"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0068` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0069` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0070` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "follow_up_window"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0071` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "28910237"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0072` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "3.2 years"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0073` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "efficacy. RESULTS: In all, 14,752 patients (of whom 10,782 [73.1%] had previous cardiovascular disease) were followed for a median of 3.2 years (interquartile range, 2.2 to 4.4). A primary composite outcome event occurred in 839 of 7356 patients (11.4%;"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0074` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "follow_up_window"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0075` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "26630143"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0076` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0077` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0078` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "follow_up_window"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0079` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "40162642"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0080` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0081` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0082` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "follow_up_window"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0083` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "38785209"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0084` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0085` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "trial end"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0089` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Endpoint definition"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0090` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "NOT_DERIVABLE"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0091` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "CV_DEATH | MI | STROKE, DEATH_FROM_CARDIOVASCULAR_CAUSES | MI | STROKE, MI | STROKE | DEATH_FROM_CARDIOVASCULAR_CAUSES_INCLUDING_UNKNOWN_CAUSES, MI | STROKE | DEATH_FROM_CARDIOVASCULAR_OR_UNDETERMINED_CAUSES"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0092` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "Analysis set"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0093` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "ASSERTED_HOMOGENEOUS_UNDERLYING_HETEROGENEOUS"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0094` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "ITT, UNKNOWN"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0100` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "31185157"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0101` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "PMID 31185157"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0103` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "· source-reported · KEEP_REPORTED_EFFECT"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0104` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "✓ verified against source"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0105` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "BACKGROUND: Establishing cardiovascular safety of new therapies for type 2 diabetes is important. Safety data are available for the subcutaneous form of the glucagon-like peptide-1 receptor agonist semaglutide but are needed for oral semaglutide. METHODS: We assessed cardiovascular outcomes of once-daily oral semaglutide in an event-driven, randomized, double-blind, placebo-controlled trial involving patients at high cardiovascular risk (age of ≥50 years with established cardiovascular or chronic kidney disease, or age of ≥60 years with cardiovascular risk factors only). The primary outcome in a time-to-event analysis was the first occurrence of a major adverse cardiovascular event (death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke). The trial was designed to rule out 80% excess cardiovascular risk as compared with placebo (noninferiority margin of 1.8 for the upper boundary of the 95% confidence interval for the hazard ratio for the primary outcome). RESULTS: A total of 3183 patients were randomly assigned to receive oral semaglutide or placebo. The mean age of the patients was 66 years; 2695 patients (84.7%) were 50 years of age or older and had cardiovascular or chronic kidney disease. The median time in the trial was 15.9 months. Major adverse cardiovascular events occurred in 61 of 1591 patients (3.8%) in the oral semaglutide group and 76 of 1592 (4.8%) in the placebo group (hazard ratio, 0.79; 95% confidence interval [CI], 0.57 to 1.11; P<0.001 for noninferiority). Results for components of the primary outcome were as follows: death from cardiovascular causes, 15 of 1591 patients (0.9%) in the oral semaglutide group and 30 of 1592 (1.9%) in the placebo group (hazard ratio, 0.49; 95% CI, 0.27 to 0.92); nonfatal myocardial infarction, 37 of 1591 patients (2.3%) and 31 of 1592 (1.9%), respectively (hazard ratio, 1.18; 95% CI, 0.73 to 1.90); and nonfatal stroke, 12 of 1591 patients (0.8%) and 16 of 1592 (1.0%), respectively (hazard ratio, 0.74; 95% CI, 0.35 to 1.57). Death from any cause occurred in 23 of 1591 patients (1.4%) in the oral semaglutide group and 45 of 1592 (2.8%) in the placebo group (hazard ratio, 0.51; 95% CI, 0.31 to 0.84). Gastrointestinal adverse events leading to discontinuation of oral semaglutide or placebo were more common with oral semaglutide. CONCLUSIONS: In this trial involving patients with type 2 diabetes, the cardiovascular risk profile of oral semaglutide was not inferior to that of placebo. (Funded by Novo Nordisk; PIONEER 6 ClinicalTrials.gov number, NCT02692716.)."

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0106` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "design key: UNPROVEN / unit UNKNOWN; estimator PUBLISHED_UNADJUSTED; correlation handling none; action DESIGN_UNPROVEN PARALLEL"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0107` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "compatibility row fields: endpoint definition: 3-point major adverse cardiovascular events; follow-up window: trial end; analysis set: intention-to-treat; components: death from cardiovascular causes; nonfatal myocardial infarction; nonfatal stroke"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0108` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "27633186"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0109` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "PMID 27633186"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0111` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "· source-reported · KEEP_REPORTED_EFFECT"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0112` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "✓ verified against source"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0113` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "BACKGROUND: Regulatory guidance specifies the need to establish cardiovascular safety of new diabetes therapies in patients with type 2 diabetes in order to rule out excess cardiovascular risk. The cardiovascular effects of semaglutide, a glucagon-like peptide 1 analogue with an extended half-life of approximately 1 week, in type 2 diabetes are unknown. METHODS: We randomly assigned 3297 patients with type 2 diabetes who were on a standard-care regimen to receive once-weekly semaglutide (0.5 mg or 1.0 mg) or placebo for 104 weeks. The primary composite outcome was the first occurrence of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke. We hypothesized that semaglutide would be noninferior to placebo for the primary outcome. The noninferiority margin was 1.8 for the upper boundary of the 95% confidence interval of the hazard ratio. RESULTS: At baseline, 2735 of the patients (83.0%) had established cardiovascular disease, chronic kidney disease, or both. The primary outcome occurred in 108 of 1648 patients (6.6%) in the semaglutide group and in 146 of 1649 patients (8.9%) in the placebo group (hazard ratio, 0.74; 95% confidence interval [CI], 0.58 to 0.95; P<0.001 for noninferiority). Nonfatal myocardial infarction occurred in 2.9% of the patients receiving semaglutide and in 3.9% of those receiving placebo (hazard ratio, 0.74; 95% CI, 0.51 to 1.08; P=0.12); nonfatal stroke occurred in 1.6% and 2.7%, respectively (hazard ratio, 0.61; 95% CI, 0.38 to 0.99; P=0.04). Rates of death from cardiovascular causes were similar in the two groups. Rates of new or worsening nephropathy were lower in the semaglutide group, but rates of retinopathy complications (vitreous hemorrhage, blindness, or conditions requiring treatment with an intravitreal agent or photocoagulation) were significantly higher (hazard ratio, 1.76; 95% CI, 1.11 to 2.78; P=0.02). Fewer serious adverse events occurred in the semaglutide group, although more patients discontinued treatment because of adverse events, mainly gastrointestinal. CONCLUSIONS: In patients with type 2 diabetes who were at high cardiovascular risk, the rate of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke was significantly lower among patients receiving semaglutide than among those receiving placebo, an outcome that confirmed the noninferiority of semaglutide. (Funded by Novo Nordisk; SUSTAIN-6 ClinicalTrials.gov number, NCT01720446 .)."

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0114` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "design key: UNPROVEN / unit UNKNOWN; estimator PUBLISHED_UNADJUSTED; correlation handling none; action DESIGN_UNPROVEN PARALLEL"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0115` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "compatibility row fields: endpoint definition: 3-point major adverse cardiovascular events; follow-up window: trial end; analysis set: intention-to-treat; components: cardiovascular death; nonfatal myocardial infarction; nonfatal stroke"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0116` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "27295427"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0117` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "PMID 27295427"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0119` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "· source-reported · KEEP_REPORTED_EFFECT"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0120` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "✓ verified against source"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0121` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "BACKGROUND: The cardiovascular effect of liraglutide, a glucagon-like peptide 1 analogue, when added to standard care in patients with type 2 diabetes, remains unknown. METHODS: In this double-blind trial, we randomly assigned patients with type 2 diabetes and high cardiovascular risk to receive liraglutide or placebo. The primary composite outcome in the time-to-event analysis was the first occurrence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke. The primary hypothesis was that liraglutide would be noninferior to placebo with regard to the primary outcome, with a margin of 1.30 for the upper boundary of the 95% confidence interval of the hazard ratio. No adjustments for multiplicity were performed for the prespecified exploratory outcomes. RESULTS: A total of 9340 patients underwent randomization. The median follow-up was 3.8 years. The primary outcome occurred in significantly fewer patients in the liraglutide group (608 of 4668 patients [13.0%]) than in the placebo group (694 of 4672 [14.9%]) (hazard ratio, 0.87; 95% confidence interval [CI], 0.78 to 0.97; P<0.001 for noninferiority; P=0.01 for superiority). Fewer patients died from cardiovascular causes in the liraglutide group (219 patients [4.7%]) than in the placebo group (278 [6.0%]) (hazard ratio, 0.78; 95% CI, 0.66 to 0.93; P=0.007). The rate of death from any cause was lower in the liraglutide group (381 patients [8.2%]) than in the placebo group (447 [9.6%]) (hazard ratio, 0.85; 95% CI, 0.74 to 0.97; P=0.02). The rates of nonfatal myocardial infarction, nonfatal stroke, and hospitalization for heart failure were nonsignificantly lower in the liraglutide group than in the placebo group. The most common adverse events leading to the discontinuation of liraglutide were gastrointestinal events. The incidence of pancreatitis was nonsignificantly lower in the liraglutide group than in the placebo group. CONCLUSIONS: In the time-to-event analysis, the rate of the first occurrence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke among patients with type 2 diabetes mellitus was lower with liraglutide than with placebo. (Funded by Novo Nordisk and the National Institutes of Health; LEADER ClinicalTrials.gov number, NCT01179048.)."

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0122` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "design key: UNPROVEN / unit UNKNOWN; estimator PUBLISHED_ADJUSTED; correlation handling published_model; action DESIGN_UNPROVEN PARALLEL"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0123` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "compatibility row fields: endpoint definition: 3-point major adverse cardiovascular events; follow-up window: trial end; analysis set: intention-to-treat; components: death from cardiovascular causes; nonfatal myocardial infarction; nonfatal stroke"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0124` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "34215025"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0125` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "PMID 34215025"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0127` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "· source-reported · KEEP_REPORTED_EFFECT"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0128` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "✓ verified against source"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0129` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "BACKGROUND: Four glucagon-like peptide-1 (GLP-1) receptor agonists that are structurally similar to human GLP-1 have been shown to reduce the risk of adverse cardiovascular events among persons with type 2 diabetes. The effect of an exendin-based GLP-1 receptor agonist, efpeglenatide, on cardiovascular and renal outcomes in patients with type 2 diabetes who are also at high risk for adverse cardiovascular events is uncertain. METHODS: In this randomized, placebo-controlled trial conducted at 344 sites across 28 countries, we evaluated efpeglenatide in participants with type 2 diabetes and either a history of cardiovascular disease or current kidney disease (defined as an estimated glomerular filtration rate of 25.0 to 59.9 ml per minute per 1.73 m2 of body-surface area) plus at least one other cardiovascular risk factor. Participants were randomly assigned in a 1:1:1 ratio to receive weekly subcutaneous injections of efpeglenatide at a dose of 4 or 6 mg or placebo. Randomization was stratified according to use of sodium-glucose cotransporter 2 inhibitors. The primary outcome was the first major adverse cardiovascular event (MACE; a composite of nonfatal myocardial infarction, nonfatal stroke, or death from cardiovascular or undetermined causes). RESULTS: A total of 4076 participants were enrolled; 2717 were assigned to receive efpeglenatide and 1359 to receive placebo. During a median follow-up of 1.81 years, an incident MACE occurred in 189 participants (7.0%) assigned to receive efpeglenatide (3.9 events per 100 person-years) and 125 participants (9.2%) assigned to receive placebo (5.3 events per 100 person-years) (hazard ratio, 0.73; 95% confidence interval [CI], 0.58 to 0.92; P<0.001 for noninferiority; P = 0.007 for superiority). A composite renal outcome event (a decrease in kidney function or macroalbuminuria) occurred in 353 participants (13.0%) assigned to receive efpeglenatide and in 250 participants (18.4%) assigned to receive placebo (hazard ratio, 0.68; 95% CI, 0.57 to 0.79; P<0.001). Diarrhea, constipation, nausea, vomiting, or bloating occurred more frequently with efpeglenatide than with placebo. CONCLUSIONS: In this trial involving participants with type 2 diabetes who had either a history of cardiovascular disease or current kidney disease plus at least one other cardiovascular risk factor, the risk of cardiovascular events was lower among those who received weekly subcutaneous injections of efpeglenatide at a dose of 4 or 6 mg than among those who received placebo. (Funded by Sanofi; AMPLITUDE-O ClinicalTrials.gov number, NCT03496298.)."

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0130` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "design key: UNPROVEN / unit UNKNOWN; estimator PUBLISHED_UNADJUSTED; correlation handling none; action DESIGN_UNPROVEN PARALLEL"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0131` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "compatibility row fields: endpoint definition: primary outcome was the first major adverse cardiovascular event (MACE; a composite of nonfatal myocardial infarction, nonfatal stroke, or death from cardiovascular or undetermined causes); follow-up window: 1.81 years; analysis set: intention-to-treat; components: nonfatal myocardial infarction; nonfatal stroke; death from cardiovascular or undetermined causes"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0132` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "31189511"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0133` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "PMID 31189511"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0135` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "· source-reported · KEEP_REPORTED_EFFECT"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0136` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "✓ verified against source"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0137` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "BACKGROUND: Three different glucagon-like peptide-1 (GLP-1) receptor agonists reduce cardiovascular outcomes in people with type 2 diabetes at high cardiovascular risk with high glycated haemoglobin A1c (HbA1c) concentrations. We assessed the effect of the GLP-1 receptor agonist dulaglutide on major adverse cardiovascular events when added to the existing antihyperglycaemic regimens of individuals with type 2 diabetes with and without previous cardiovascular disease and a wide range of glycaemic control. METHODS: This multicentre, randomised, double-blind, placebo-controlled trial was done at 371 sites in 24 countries. Men and women aged at least 50 years with type 2 diabetes who had either a previous cardiovascular event or cardiovascular risk factors were randomly assigned (1:1) to either weekly subcutaneous injection of dulaglutide (1·5 mg) or placebo. Randomisation was done by a computer-generated random code with stratification by site. All investigators and participants were masked to treatment assignment. Participants were followed up at least every 6 months for incident cardiovascular and other serious clinical outcomes. The primary outcome was the first occurrence of the composite endpoint of non-fatal myocardial infarction, non-fatal stroke, or death from cardiovascular causes (including unknown causes), which was assessed in the intention-to-treat population. This study is registered with ClinicalTrials.gov, number NCT01394952. FINDINGS: Between Aug 18, 2011, and Aug 14, 2013, 9901 participants (mean age 66·2 years [SD 6·5], median HbA1c 7·2% [IQR 6·6-8·1], 4589 [46·3%] women) were enrolled and randomly assigned to receive dulaglutide (n=4949) or placebo (n=4952). During a median follow-up of 5·4 years (IQR 5·1-5·9), the primary composite outcome occurred in 594 (12·0%) participants at an incidence rate of 2·4 per 100 person-years in the dulaglutide group and in 663 (13·4%) participants at an incidence rate of 2·7 per 100 person-years in the placebo group (hazard ratio [HR] 0·88, 95% CI 0·79-0·99; p=0·026). All-cause mortality did not differ between groups (536 [10·8%] in the dulaglutide group vs 592 [12·0%] in the placebo group; HR 0·90, 95% CI 0·80-1·01; p=0·067). 2347 (47·4%) participants assigned to dulaglutide reported a gastrointestinal adverse event during follow-up compared with 1687 (34·1%) participants assigned to placebo (p<0·0001). INTERPRETATION: Dulaglutide could be considered for the management of glycaemic control in middle-aged and older people with type 2 diabetes with either previous cardiovascular disease or cardiovascular risk factors. FUNDING: Eli Lilly and Company."

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0138` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "design key: UNPROVEN / unit UNKNOWN; estimator PUBLISHED_UNADJUSTED; correlation handling none; action DESIGN_UNPROVEN PARALLEL"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0139` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "compatibility row fields: endpoint definition: primary outcome was the first occurrence of the composite endpoint of non-fatal myocardial infarction, non-fatal stroke, or death from cardiovascular causes (including unknown causes), which was assessed in the intention-to-treat population; follow-up window: trial end; analysis set: intention-to-treat; components: non-fatal myocardial infarction; non-fatal stroke; death from cardiovascular causes including unknown causes"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0140` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "30291013"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0141` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "PMID 30291013"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0143` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "· source-reported · KEEP_REPORTED_EFFECT"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0144` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "✓ verified against source"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0145` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "BACKGROUND: Glucagon-like peptide 1 receptor agonists differ in chemical structure, duration of action, and in their effects on clinical outcomes. The cardiovascular effects of once-weekly albiglutide in type 2 diabetes are unknown. We aimed to determine the safety and efficacy of albiglutide in preventing cardiovascular death, myocardial infarction, or stroke. METHODS: We did a double-blind, randomised, placebo-controlled trial in 610 sites across 28 countries. We randomly assigned patients aged 40 years and older with type 2 diabetes and cardiovascular disease (at a 1:1 ratio) to groups that either received a subcutaneous injection of albiglutide (30-50 mg, based on glycaemic response and tolerability) or of a matched volume of placebo once a week, in addition to their standard care. Investigators used an interactive voice or web response system to obtain treatment assignment, and patients and all study investigators were masked to their treatment allocation. We hypothesised that albiglutide would be non-inferior to placebo for the primary outcome of the first occurrence of cardiovascular death, myocardial infarction, or stroke, which was assessed in the intention-to-treat population. If non-inferiority was confirmed by an upper limit of the 95% CI for a hazard ratio of less than 1·30, closed testing for superiority was prespecified. This study is registered with ClinicalTrials.gov, number NCT02465515. FINDINGS: Patients were screened between July 1, 2015, and Nov 24, 2016. 10 793 patients were screened and 9463 participants were enrolled and randomly assigned to groups: 4731 patients were assigned to receive albiglutide and 4732 patients to receive placebo. On Nov 8, 2017, it was determined that 611 primary endpoints and a median follow-up of at least 1·5 years had accrued, and participants returned for a final visit and discontinuation from study treatment; the last patient visit was on March 12, 2018. These 9463 patients, the intention-to-treat population, were evaluated for a median duration of 1·6 years and were assessed for the primary outcome. The primary composite outcome occurred in 338 (7%) of 4731 patients at an incidence rate of 4·6 events per 100 person-years in the albiglutide group and in 428 (9%) of 4732 patients at an incidence rate of 5·9 events per 100 person-years in the placebo group (hazard ratio 0·78, 95% CI 0·68-0·90), which indicated that albiglutide was superior to placebo (p<0·0001 for non-inferiority; p=0·0006 for superiority). The incidence of acute pancreatitis (ten patients in the albiglutide group and seven patients in the placebo group), pancreatic cancer (six patients in the albiglutide group and five patients in the placebo group), medullary thyroid carcinoma (zero patients in both groups), and other serious adverse events did not differ between the two groups. There were three (<1%) deaths in the placebo group that were assessed by investigators, who were masked to study drug assignment, to be treatment-related and two (<1%) deaths in the albiglutide group. INTERPRETATION: In patients with type 2 diabetes and cardiovascular disease, albiglutide was superior to placebo with respect to major adverse cardiovascular events. Evidence-based glucagon-like peptide 1 receptor agonists should therefore be considered as part of a comprehensive strategy to reduce the risk of cardiovascular events in patients with type 2 diabetes. FUNDING: GlaxoSmithKline."

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0146` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "design key: UNPROVEN / unit UNKNOWN; estimator PUBLISHED_UNADJUSTED; correlation handling none; action DESIGN_UNPROVEN PARALLEL"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0147` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "compatibility row fields: endpoint definition: 3-point major adverse cardiovascular events; follow-up window: trial end; analysis set: intention-to-treat; components: cardiovascular death; myocardial infarction; stroke"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0148` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "28910237"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0149` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "PMID 28910237"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0151` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "· source-reported · KEEP_REPORTED_EFFECT"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0152` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "✓ verified against source"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0153` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "BACKGROUND: The cardiovascular effects of adding once-weekly treatment with exenatide to usual care in patients with type 2 diabetes are unknown. METHODS: We randomly assigned patients with type 2 diabetes, with or without previous cardiovascular disease, to receive subcutaneous injections of extended-release exenatide at a dose of 2 mg or matching placebo once weekly. The primary composite outcome was the first occurrence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke. The coprimary hypotheses were that exenatide, administered once weekly, would be noninferior to placebo with respect to safety and superior to placebo with respect to efficacy. RESULTS: In all, 14,752 patients (of whom 10,782 [73.1%] had previous cardiovascular disease) were followed for a median of 3.2 years (interquartile range, 2.2 to 4.4). A primary composite outcome event occurred in 839 of 7356 patients (11.4%; 3.7 events per 100 person-years) in the exenatide group and in 905 of 7396 patients (12.2%; 4.0 events per 100 person-years) in the placebo group (hazard ratio, 0.91; 95% confidence interval [CI], 0.83 to 1.00), with the intention-to-treat analysis indicating that exenatide, administered once weekly, was noninferior to placebo with respect to safety (P<0.001 for noninferiority) but was not superior to placebo with respect to efficacy (P=0.06 for superiority). The rates of death from cardiovascular causes, fatal or nonfatal myocardial infarction, fatal or nonfatal stroke, hospitalization for heart failure, and hospitalization for acute coronary syndrome, and the incidence of acute pancreatitis, pancreatic cancer, medullary thyroid carcinoma, and serious adverse events did not differ significantly between the two groups. CONCLUSIONS: Among patients with type 2 diabetes with or without previous cardiovascular disease, the incidence of major adverse cardiovascular events did not differ significantly between patients who received exenatide and those who received placebo. (Funded by Amylin Pharmaceuticals; EXSCEL ClinicalTrials.gov number, NCT01144338 .)."

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0154` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "design key: UNPROVEN / unit UNKNOWN; estimator PUBLISHED_UNADJUSTED; correlation handling none; action DESIGN_UNPROVEN PARALLEL"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0155` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "compatibility row fields: endpoint definition: 3-point major adverse cardiovascular events; follow-up window: 3.2 years; analysis set: intention-to-treat; components: death from cardiovascular causes; nonfatal myocardial infarction; nonfatal stroke"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0156` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "26630143"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0157` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "PMID 26630143"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0159` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "· source-reported · KEEP_REPORTED_EFFECT"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0160` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "✓ verified against source"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0161` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "ITT analyses (on-study and on-treatment) of MACE, defined as cardiovascular death, non-fatal MI, and non-fatal stroke, are consistent with those of MACE+ (Table 8). The reason for the similarity is that only 0.3% of subjects in the ITT population experienced hospitalization for unstable angina. For ITT analysis 792 MACE events were observed, 392 and 400 in placebo and lixisenatide group, respectively. The 95% confidence interval for the hazard ratio is (0.887, 1.172) with a point estimate of 1.02."

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0162` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "design key: UNPROVEN / unit UNKNOWN; estimator PUBLISHED_UNADJUSTED; correlation handling none; action DESIGN_UNPROVEN PARALLEL"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0163` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "compatibility row fields: endpoint definition: 3-point major adverse cardiovascular events; follow-up window: trial end; analysis set: intention-to-treat"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0164` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "SOUL"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0165` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "PMID 40162642"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0167` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "· source-reported · KEEP_REPORTED_EFFECT"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0168` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "✓ verified against source"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0169` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "In this double-blind, placebo-controlled, event-driven, superiority trial, we randomly assigned participants who were 50 years of age or older, had type 2 diabetes, and had known atherosclerotic cardiovascular disease, chronic kidney disease, or both to receive either once-daily oral semaglutide (maximal dose, 14 mg) or placebo, in addition to standard care. The primary outcome was major adverse cardiovascular events (a composite of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke), assessed in a time-to-first-event analysis. Among the 9650 participants who had undergone randomization, a primary-outcome event occurred in 579 of the 4825 participants (12.0%) in the oral semaglutide group, as compared with 668 of the 4825 participants (13.8%) in the placebo group (hazard ratio, 0.86; 95% confidence interval, 0.77 to 0.96; P = 0.006). Among persons with type 2 diabetes and atherosclerotic cardiovascular disease, chronic kidney disease, or both, oral semaglutide was associated with a significantly lower risk of major adverse cardiovascular events than placebo. (Funded by Novo Nordisk; SOUL ClinicalTrials.gov number, NCT03914326.)."

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0170` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "design key: UNPROVEN / unit UNKNOWN; estimator PUBLISHED_UNADJUSTED; correlation handling none; action DESIGN_UNPROVEN PARALLEL"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0171` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "compatibility row fields: endpoint definition: primary outcome was major adverse cardiovascular events (a composite of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke), assessed in a time-to-first-event analysis; follow-up window: trial end; analysis set: intention-to-treat; components: death from cardiovascular causes; nonfatal myocardial infarction; nonfatal stroke"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0172` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "FLOW"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0173` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "PMID 38785209"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0175` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "· source-reported · KEEP_REPORTED_EFFECT"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0176` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "✓ verified against source"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0177` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "the risk of major cardiovascular events 18% lower (hazard ratio, 0.82; 95% CI, 0.68 to 0.98; P&#x2009;=&#x2009;0.029)"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0178` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "design key: UNPROVEN / unit UNKNOWN; estimator PUBLISHED_UNADJUSTED; correlation handling none; action DESIGN_UNPROVEN"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.

- `unit-0179` / `SENTENCE_WITHOUT_OBJECT`

  Exact text: "compatibility row fields: endpoint definition: primary outcome was major kidney disease events, a composite of the onset of kidney failure (dialysis, transplantation, or an eGFR of <15 ml per minute per 1; follow-up window: trial end; analysis set: intention-to-treat"

  Reason: Legacy outcome/input/type prose has not been mapped to a typed source or transformation contract; source verification of neighbouring FACTs does not validate this text.


## Remaining finish work

Resolve the pre-existing empty-primary rebuild failure in the appropriate lane,
then complete explicit typed contracts for the residual overview and outcome
units and the general known-missing panel. Rebuild and rerun the scoped census
and full suite. Do not promote this partial migration to complete or shipped.
