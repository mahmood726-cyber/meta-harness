# LANE RV1 report

Verification completed; see measured refusals below.

## Final measured result

VERIFY-ALL: REFUSED -- 4 of 11 limbs not PASS. Fix the harness, never the gate.

| Check | Measured result and denominator |
|---|---|
| Full builds with `--now 2026-09-11` | 32 of 32 live reviews completed |
| Final canonical renderer/certificate refresh | 32 of 32 live reviews completed |
| RV1 and eligibility regression suite | 21 of 21 tests passed |
| Subsequent fixed-decimal numeral regression | 1 of 1 test passed |
| Full unit-test stage | 1181 of 1183 tests passed; the two failed wording assertions were then corrected and both passed a targeted rerun |
| Live-browser follow-up | Chrome E2E passed; screenshot inspected at `.tmp/fn-family-ui.png` |
| Retraction survival against `3f8add72` | 32 of 32 pages retained every marking |
| Empty-AACT replay | 32 of 32 live reviews reproduced |
| GLP1 served claim census | 2975 registered of 2975 rendered units; zero typed-object, precision or surface violations |
| GLP1 page gate | PASS, zero refusal reasons |
| All-page gates | 12 of 32 review pages passed |
| Full verification | 7 of 11 limbs passed |

The gate and full-verification refusals below remain unresolved. They are not
represented as a release-ready result. `STUCK_FAILURES.md` records measured
examples; `outputs/handover/rv1/gates.json` holds every page's reasons. No claim
is made that these broader failures were present in the initial dirty tree:
that baseline comparison was not measured.

The search-completeness refusal says the published measurement's engine identity
does not match the current engine. No new search measurement was performed in
this no-network lane. The honest-state ratchet uses merge-base
`2304824034b4ba8677da2d2d2453352711ed2a9b` and its additional block floors; it
reports decreased markers and missing exact blocks, including on GLP1. This is
a different comparison from the requested retraction-survival check against
`3f8add72`, which passed 32 of 32 pages. The ratchet refusal remains unresolved;
no acknowledgement or bypass was added to suppress it.

### Verification table

| Limb | Verdict | Seconds |
|---|---|---:|
| unit tests (pytest tests/) | REFUSED | 2915 |
| offline reproduction (every live page replays from committed cache) | PASS | 1072 |
| publication gate on every live review page | REFUSED | 1795 |
| index currency (generated == committed docs/index.html) | PASS | 14 |
| served-artefact leak scan (docs/*.json) | PASS | 2 |
| held-out leak detector (registry/heldout_sealed.json) | PASS | 361 |
| search completeness (search_v2 measurement current; every state explicit; no zero from an exit code) | REFUSED | 2 |
| fix-state discipline (registry/fixes.json) | PASS | 139 |
| honest-state ratchet (no page may get quieter) | REFUSED | 31 |
| gate scorecard (every gate accounted for) | PASS | 3 |
| gate gaps table (sealed what-it-would-not-stop rows) | PASS | 10 |

### Verification repairs and limits

The final refresh repaired stale rendered pages/certificates identified during
an interrupted replay. Earlier interrupted runs are not counted as completed.
Single-contributor outcomes with explicitly unavailable heterogeneity retain
null tau2/PI in their registered projection; the recomputation enforces exactly
one contributor. Audit formatting now uses the object's declared precision.
Both changes have regression coverage in the 21-test passing run.

The later numeral compatibility correction accepts the two-decimal rendering
of an actual numeric field (for example, magnitude 17.40 from -17.4), and still
rejects an unrelated value. It changes only `object_numerals`, not the rendered
manuscript or any source value. The all-page gate process had already imported
the earlier function; its melatonin numeral reason is historical. The subsequent
full `verify_all.py` run uses the correction and supplies the final verdict.

Additional regression outputs, verbatim:

The full unit-test stage found two remaining assertions for wording
that this lane was explicitly required to replace. After that stage, those
assertions were updated to demand formal RoB not assessed / qualified machine
signals and the open-scope family universe label. Their exact failures and the
targeted rerun appear below. The complete unit suite was not rerun after these
test-only corrections; the verification table preserves its original verdict.

#### headline-numeral-test

```text
.                                                                        [100%]
1 passed in 5.50s
```

#### updated-contract-tests

```text
...                                                                      [100%]
3 passed in 68.96s (0:01:08)
```

#### dependency-state-test

```text
.                                                                        [100%]
1 passed in 4.34s
```

#### harms-empty-ledger-test

```text
.                                                                        [100%]
1 passed in 4.04s
```

#### final-glp1-gate

```text
True []
```

#### remaining-contract-pre-fix

```text
FF                                                                       [100%]
================================== FAILURES ===================================
_____ test_page_uses_per_item_states_instead_of_stale_sensitivity_totals ______
tests\test_rob_sensitivity_predicate.py:250: in test_page_uses_per_item_states_instead_of_stale_sensitivity_totals
    assert '1 of 1 rows retained' in rendered
E   assert '1 of 1 rows retained' in '<p><span data-claim-id="risk-overall-states" data-claim-class="TRANSFORMATION"><strong>[TRANSFORMATION]</strong> Cove...thmetic_rule":null,"imprecision_basis":null,"unassessed_domains":null,"upgrades":null} [adjudication: OWED]</span></p>'
______________________ test_family_table_in_live_browser ______________________
tests\test_trial_family_ui.py:49: in test_family_table_in_live_browser
    assert table.locator('.family-count-chain').inner_text()=='[TRANSFORMATION] '+trial_family.count_sentence(review['family_count_chain'])
E   AssertionError: assert '[TRANSFORMAT...is preserved.' == '[TRANSFORMAT...is preserved.'
E     
E     - [TRANSFORMATION] 13 publications screened + 234 registry records → 238 trial families → 143 eligible families → 7 contributing families. 143 trials met eligibility. 84 families have unresolved structural eligibility; existing pooling membership is preserved.
E     + [TRANSFORMATION] Open-scope family assembly: 13 publications screened + 234 registry records → 238 trial families → 143 eligible families → 7 contributing families. 143 trials met eligibility. 84 families have unresolved structural eligibility; existing pooling membership is preserved.
E     ?                  ++++++++++++++++++++++++++++
=========================== short test summary info ===========================
FAILED tests/test_rob_sensitivity_predicate.py::test_page_uses_per_item_states_instead_of_stale_sensitivity_totals
FAILED tests/test_trial_family_ui.py::test_family_table_in_live_browser - Ass...
2 failed in 31.77s
```

#### remaining-contract-post-fix

```text
..                                                                       [100%]
2 passed in 47.26s
```


## Scope and provenance

MEASURED: starting HEAD `3f8add72d50b84eae2000625387e3194137a06ea`; 729 changed paths at entry.
Current HEAD `3f8add72d50b84eae2000625387e3194137a06ea`; 735 changed paths. No commit, reset, checkout, stash or network retrieval.
The required ProjectIndex and rewrite workbook were read from F:. Neither was edited; no portfolio/submission status was promoted.

The existing ClaimGraph, its transformations, source verification, census, certificate builder and gate were extended.
There is no parallel evidence graph or separate persisted claim-state cache. RV2-owned modules were not edited.
Necessary adjacent renderer edits: `risk_prose.py`, `remainder_prose.py`, and `integration_display.py`.
The requested gate is in `gate.py`, with an inventory entry in `registry/gate_scorecard.json`.
Its production event list remains empty: no independent or production validation is claimed.

| Component | Static policy / presentation | Dynamic evidence |
|---|---|---|
| Claim scope | Typed use tokens, state rules, row labels | Membership, count chain, retrieval class, RoB/GRADE/harms objects and release certificate |
| Arithmetic | Existing canonical pool and FACT verifier | Held effect/count inputs, source digests and located spans |
| Headline / counts | Named universes; subset qualifier | Current pool estimates and contributor set; absent/refused sets; funding-table entries |
| Eligibility | Existing executable protocol compiler; retained unresolved obligations | Protocol block, held registry outcome rows, verified axis evidence, publication spans |
| Audit display | Suppression outside expandable provenance views | Stored τ²/I²/PI; recomputed pool audit values |
| Tests | Adversarial mutations and test-only fixtures | Current integration-tree objects and held source records |

## Implemented behavior

- A: claim objects carry state, scope, dependencies, permitted and prohibited typed uses. The top ten-row evidence panel is an object view. A fresh-render gate rejects missing, added or altered rows. Arithmetic is checked through the existing verified-input pool.
- B/J: the headline derives its estimate, CI, k and absent/refused counts. It identifies the pre-identified universe. Stale heterogeneity numbers appear only in expandable audit/reproduction views, including a stored I² audit value.
- C/H2: formal RoB remains not assessed; machine signals are explicitly qualified. Coverage counts machine signals and does not promote them to formal overall ratings.
- D: provisional GRADE does not present a total downgrade count or starting-category arithmetic. Domain evidence remains visible.
- E: PRISMA is labelled reporting-item presence; executed search-method validity is a separate retrieval-class-derived object.
- F: funding coverage names its actual pre-identified table universe and changes when its input set changes. Manuscript absent and subsequently identified counts use current object sets.
- H1/H3/H4/H5: strand refusals and rule exclusions partition the dropped set; pre-identified screening and open-scope family assembly have separate labels; strand heterogeneity is suppressed outside audit; protocol declaration is distinguished from executed search.
- I: both manuscript and screening render the compiler-derived eligibility rule. Topics without a block say axes are not declared executably. Per-record ascertainment reasons retain unresolved records with an open obligation and identify held evidence when established.

MEASURED on this tree: the initial GLP1 pool has 7 contributors, 3 typed-effect refusals, and 11 funding-table entries.
The supplied served-page examples (k=8; funding 9; historical absence split 1+2; PI text 0.81 to 0.91) were not copied into the implementation.
The current declared-unpooled set contains the three refused families; the current known-missing set adds no family outside it.
INFERRED scope boundary: those pre-identified counts do not enumerate the open-scope family assembly's larger eligible universe.
The retrospective protocol's quotation of the retired rule remains in the source file; a typed declaration projection renders the executable amendment instead of that historical commentary.

## Verification ledger

MEASURED: 32 of 32 unique review-build commands recorded so far; required denominator is all 32 live reviews.
Full commands and exit codes: `outputs/handover/rv1/commands.json`.
Early pages were refreshed through `harness.census.build_review_dir` after display changes; the empty-AACT replay independently checks the final core and served bytes.

| Command / stage | Latest exit code |
|---|---:|
| post-fix | 0 |
| updated-contract-tests | 0 |
| second-pass | 0 |
| renderer-refresh | 0 |
| retraction-survival | 0 |
| empty-aact-replay | 0 |
| claim-scope | 0 |
| gates | 1 |
| verify-all | 1 |

## Pre-fix failures — verbatim

```text
FFFFFFFFFFF.F.                                                           [100%]
================================== FAILURES ===================================
_____________________ test_evidence_panel_is_object_view ______________________
tests\test_rv1_rendering.py:23: in test_evidence_panel_is_object_view
    assert panel is not None, 'Missing object-backed evidence-state panel'
E   AssertionError: Missing object-backed evidence-state panel
E   assert None is not None
________________ test_abstract_suppresses_stale_heterogeneity _________________
tests\test_rv1_rendering.py:37: in test_abstract_suppresses_stale_heterogeneity
    assert 'HKSJ/PM tau squared=' not in text
E   AssertionError: assert 'HKSJ/PM tau squared=' not in '[JUDGEMENT]...so required.'
E     
E     'HKSJ/PM tau squared=' is contained here:
E       95); k=7; HKSJ/PM tau squared=0; prediction interval 0.8 to 0.99. [TRANSFORMATION] Unpooled per-item states: {'EFFECT_TYPE_REFUSED': 3}. Certainty [JUDGEMENT] STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. [adjudication: RULE] GRADE provisional -- not yet fully assessable [TRANSFORMATION] Recorded domain downgrades: 0. Methods [JUDGEMENT] The reported-effect transformation uses random effects (Paule-Mandel with a Hartung-...
E     
E     ...Full output truncated (2 lines hidden), use '-vv' to show
_____________________ test_rob_cells_are_machine_signals ______________________
tests\test_rv1_rendering.py:42: in test_rob_cells_are_machine_signals
    assert 'Recorded overall rating on assessed domains: low' not in text
E   AssertionError: assert 'Recorded ov...domains: low' not in '[TRANSFORMA...ation: RULE]'
E     
E     'Recorded overall r...sessed domains: low' is contained here:
E       UDGEMENT] Recorded overall rating on assessed domains: low (on assessed domains; some domains require human judgement) [adjudication: RULE] [JUDGEMENT] Randomisation: low. Recorded basis: AACT allocation = RANDOMIZED [adjudication: RULE] [JUDGEMENT] Deviations/blinding: low. Recorded basis: trial masking = Double (blinded); overrides per-role Booleans subject_masked=True/caregiver_masked=False (FLAGGED registry-vs-trial disagreement) [adjudication: RULE] [JUDGEMENT] Missing outcome data: not assessed. Record...
E     
E     ...Full output truncated (2 lines hidden), use '-vv' to show
_________________________ test_grade_residue_removed __________________________
tests\test_rv1_rendering.py:49: in test_grade_residue_removed
    assert 'downgrade(s)' not in text
E   AssertionError: assert 'downgrade(s)' not in 'GRADE provi...ation: RULE]'
E     
E     'downgrade(s)' is contained here:
E       ssable (0 downgrade(s); starting arithmetic: high for randomized trials). Unassessed domains: inconsistency, indirectness, publication_bias, risk_of_bias, risk_of_bias: D2_deviations, risk_of_bias: D3_missing_outcome_data, risk_of_bias: D4_outcome_measurement, risk_of_bias: D5_selective_reporting; unassessed never counts as favourable. Registry-machine-signal-restricted signals are not a formal human RoB 2 assessment. Domain Effect on certainty Basis Risk of bias [JUDGEMENT] risk of bias: NOT ASSESSED; judgement owed. Recorded basis: FORMAL RoB 2 NO...
E     
E     ...Full output truncated (2 lines hidden), use '-vv' to show
____________________ test_reporting_validity_tracks_class _____________________
tests\test_rv1_rendering.py:54: in test_reporting_validity_tracks_class
    assert 'PRISMA reporting-item presence' in plain(page._reporting(review, False))
E   assert 'PRISMA reporting-item presence' in 'GRADE provisional -- not yet fully assessable [INTERPRETATION] This table checks whether reporting fields are present...ds. 24 Registration and protocol [TRANSFORMATION] 24 Registration and protocol: PRESENT: reproduction.preregistration.'
E    +  where 'GRADE provisional -- not yet fully assessable [INTERPRETATION] This table checks whether reporting fields are present...ds. 24 Registration and protocol [TRANSFORMATION] 24 Registration and protocol: PRESENT: reproduction.preregistration.' = plain('<p><span data-claim-id="grade-certainty" data-claim-class="TRANSFORMATION" data-grade-certainty="true">GRADE provisio...TRANSFORMATION]</strong> 24 Registration and protocol: PRESENT: reproduction.preregistration.</span></td></tr></table>')
E    +    where '<p><span data-claim-id="grade-certainty" data-claim-class="TRANSFORMATION" data-grade-certainty="true">GRADE provisio...TRANSFORMATION]</strong> 24 Registration and protocol: PRESENT: reproduction.preregistration.</span></td></tr></table>' = <function _reporting at 0x000001D27EBC58A0>({'arm_contrast': {'current_pooled_trial_ids': ['26630143', '27295427', '27633186', '28910237', '31185157', '31189511',...supplied by lane adjudication; complete citation not held)', 'document_ref': None, 'document_sha256': None, ...}], ...}, False)
E    +      where <function _reporting at 0x000001D27EBC58A0> = page._reporting
_________________ test_funding_denominator_names_covered_set __________________
tests\test_rv1_rendering.py:61: in test_funding_denominator_names_covered_set
    assert f"{len(review['funding'])} pre-identified funding-table families" in text
E   AssertionError: assert '11 pre-identified funding-table families' in 'Recorded funding entries: 10 of 10 known (1 unknown) are classified as industry-funded or industry-tied. Unknown funding is not counted as independently funded.'
________________________ test_absence_universes_named _________________________
tests\test_rv1_rendering.py:67: in test_absence_universes_named
    assert 'declared absent within the pre-identified screening universe' in text
E   AssertionError: assert 'declared absent within the pre-identified screening universe' in '[JUDGEMENT] This manuscript is generated from the review object. Registered transformations and recorded judgements a...(round-2): Protocol-SHA byte-for-byte reproduction is not claimed; mutable post-registration inputs are also required.'
____________________ test_strand_dropped_states_partition _____________________
tests\test_rv1_rendering.py:72: in test_strand_dropped_states_partition
    cid, obj = cg.strand_membership_object(strand)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: module 'harness.claimgraph' has no attribute 'strand_membership_object'. Did you mean: 'membership_object'?
__________________ test_protocol_declared_execution_separate __________________
tests\test_rv1_rendering.py:78: in test_protocol_declared_execution_separate
    assert 'declared, not yet executed: search class KNOWN_ITEM_RETRIEVAL' in text
E   assert 'declared, not yet executed: search class KNOWN_ITEM_RETRIEVAL' in 'sha [TRANSFORMATION] Recorded sha: b10c53d3783facb7e630219f0bb447fe6e22843e committed utc [TRANSFORMATION] Recorded c...     "NONFATAL_STROKE"\n      ],\n      "effect_measure": "HR",\n      "censoring": "end-of-study"\n    }\n  }\n}\n```'
_____________ test_eligibility_compiler_rendered_in_both_sections _____________
tests\test_rv1_rendering.py:84: in test_eligibility_compiler_rendered_in_both_sections
    assert sentence in plain(manuscript.render(review))
E   assert 'Outcome ascertainment is an eligibility axis; outcome result availability is not.' in '[JUDGEMENT] This manuscript is generated from the review object. Registered transformations and recorded judgements a...(round-2): Protocol-SHA byte-for-byte reproduction is not claimed; mutable post-registration inputs are also required.'
E    +  where '[JUDGEMENT] This manuscript is generated from the review object. Registered transformations and recorded judgements a...(round-2): Protocol-SHA byte-for-byte reproduction is not claimed; mutable post-registration inputs are also required.' = plain('<p><span data-claim-id="manuscript-generation" data-claim-class="JUDGEMENT"><strong>[JUDGEMENT]</strong> This manuscr...Protocol-SHA byte-for-byte reproduction is not claimed; mutable post-registration inputs are also required.</span></p>')
E    +    where '<p><span data-claim-id="manuscript-generation" data-claim-class="JUDGEMENT"><strong>[JUDGEMENT]</strong> This manuscr...Protocol-SHA byte-for-byte reproduction is not claimed; mutable post-registration inputs are also required.</span></p>' = <function render at 0x000001D26D2E40E0>({'arm_contrast': {'current_pooled_trial_ids': ['26630143', '27295427', '27633186', '28910237', '31185157', '31189511',...supplied by lane adjudication; complete citation not held)', 'document_ref': None, 'document_sha256': None, ...}], ...})
E    +      where <function render at 0x000001D26D2E40E0> = manuscript.render
________________ test_screen_ascertainment_unresolved_retained ________________
tests\test_rv1_rendering.py:95: in test_screen_ascertainment_unresolved_retained
    assert 'outcome ascertainment: UNRESOLVED (retained; open obligation)' in decision[2]
E   AssertionError: assert 'outcome ascertainment: UNRESOLVED (retained; open obligation)' in 'eligible randomised controlled trial: intervention (as configured), comparator (as configured), population the target population — P/I/C/design met.'
_______________ test_served_rule_sentence_never_renders_on_glp1 _______________
tests\test_eligibility_axes.py:40: in test_served_rule_sentence_never_renders_on_glp1
    assert "Outcome ascertainment is an eligibility axis; outcome result availability is not." in plain
E   assert 'Outcome ascertainment is an eligibility axis; outcome result availability is not.' in "      GLP-1 receptor agonists vs placebo for 3-point MACE in type 2 diabetes  \n*{box-sizing:border-box}body{font:15p...'active',b.dataset.t===id)});}\n(function(){var f=document.querySelector('nav button');if(f)show(f.dataset.t);})();   "
=========================== short test summary info ===========================
FAILED tests/test_rv1_rendering.py::test_evidence_panel_is_object_view - Asse...
FAILED tests/test_rv1_rendering.py::test_abstract_suppresses_stale_heterogeneity
FAILED tests/test_rv1_rendering.py::test_rob_cells_are_machine_signals - Asse...
FAILED tests/test_rv1_rendering.py::test_grade_residue_removed - AssertionErr...
FAILED tests/test_rv1_rendering.py::test_reporting_validity_tracks_class - as...
FAILED tests/test_rv1_rendering.py::test_funding_denominator_names_covered_set
FAILED tests/test_rv1_rendering.py::test_absence_universes_named - AssertionE...
FAILED tests/test_rv1_rendering.py::test_strand_dropped_states_partition - At...
FAILED tests/test_rv1_rendering.py::test_protocol_declared_execution_separate
FAILED tests/test_rv1_rendering.py::test_eligibility_compiler_rendered_in_both_sections
FAILED tests/test_rv1_rendering.py::test_screen_ascertainment_unresolved_retained
FAILED tests/test_eligibility_axes.py::test_served_rule_sentence_never_renders_on_glp1
12 failed, 2 passed in 94.28s (0:01:34)
```

The additional universe test was added after implementation. Its failure below reconstructs the inspected pre-fix display rule in memory only (`count_sentence` without a universe prefix); it is not represented as a replay of the entire initial integration tree.

```text
F                                                                        [100%]
================================== FAILURES ===================================
_____________ test_screening_and_open_family_universes_are_named ______________
tests\test_rv1_rendering.py:136: in test_screening_and_open_family_universes_are_named
    assert chain.startswith('Open-scope family assembly: ')
E   AssertionError: assert False
E    +  where False = <built-in method startswith of str object at 0x000001CFF964AB50>('Open-scope family assembly: ')
E    +    where <built-in method startswith of str object at 0x000001CFF964AB50> = '13 publications screened + 234 registry records → 238 trial families → 143 eligible families → 7 contributing familie... trials met eligibility. 84 families have unresolved structural eligibility; existing pooling membership is preserved.'.startswith
=========================== short test summary info ===========================
FAILED tests/test_rv1_rendering.py::test_screening_and_open_family_universes_are_named
1 failed in 7.70s
```

## Post-fix regression run — verbatim

```text
.....................                                                    [100%]
21 passed in 110.25s (0:01:50)
```

## Required verification outputs

### second-pass

```text
11 of 11 held GLP1 candidate-source rows passed held identifier/bridge, located-number and retrieval-date checks; see per-row identity basis
[
  {
    "strand": "CONVENTIONAL_GLP1RA",
    "counts": {
      "EFFECT_TYPE_REFUSED": 3,
      "STRAND_RULE_EXCLUDED": 1
    },
    "dropped_source_ids": [
      "30291013",
      "34215025",
      "34873344",
      "38785209"
    ]
  },
  {
    "strand": "GLP1RA_ANY_DELIVERY",
    "counts": {
      "EFFECT_TYPE_REFUSED": 3
    },
    "dropped_source_ids": [
      "30291013",
      "34215025",
      "38785209"
    ]
  }
]
```

### retraction-survival

```text
pages with every marking kept (count >= base): 32 of 32
```

### empty-aact-replay

```text
  OK  balanced-crystalloids-vs-saline-mortality
  OK  colchicine-postop-af
  OK  colchicine-recurrent-pericarditis
  OK  colchicine-secondary-cv-prevention
  OK  corticosteroids-cap-mortality
  OK  corticosteroids-covid19-mortality
  OK  dapagliflozin-hfpef-hosp
  OK  denosumab-vertebral-fracture
  OK  doac-vte-recurrence
  OK  dpp4-mace-t2d
  OK  empagliflozin-hfpef-hosp
  OK  esketamine-trd-madrs
  OK  finerenone-ckd-t2d-renal
  OK  glp1-ra-mace-t2d
  OK  iv-iron-hfref-hosp
  OK  melatonin-primary-insomnia-sol
  OK  metformin-pcos-ovulation
  OK  noac-vs-warfarin-af-stroke
  OK  omega3-cardiovascular-events
  OK  pcsk9-mace
  OK  probiotics-aad-prevention
  OK  sacubitril-valsartan-hfref
  OK  semaglutide-obesity-mace
  OK  semaglutide-obesity-weight
  OK  sglt2-ckd-progression
  OK  sglt2-hfref-hosp-cvdeath
  OK  sglt2-primary-prevention-hf
  OK  spironolactone-hfref-mortality
  OK  statins-primary-prevention-elderly
  OK  ticagrelor-vs-clopidogrel-acs
  OK  tocilizumab-covid19-mortality
  OK  tranexamic-acid-pph

32/32 reproduce (all reproducible)
```

### claim-scope

```text
UNVERIFIED_FACT: 170 of 181 verified_effects rows
Pages scanned: 32; scope_complete=false
```

### gates

```text
balanced-crystalloids-vs-saline-mortality PASS []
colchicine-postop-af FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', 'L1: TRANSFORMATION_MISMATCH outcome-pool-4a9743816e814e344bbc: ', 'L1: UNRECOMPUTABLE_TRANSFORMATION manuscript-result: ']
colchicine-recurrent-pericarditis FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', "L1: UNVERIFIED_FACT PMID 21873705 in 'Recurrent pericarditis': effect=0.44 is not in located span", "L1: UNVERIFIED_FACT PMID 21873705 in 'Symptom persistence at 72 hours': effect=0.44 is not in located span", "L1: UNVERIFIED_FACT PMID 24694983 in 'Adverse events (gastrointestinal)': ai=9 is not in located span", 'L1: UNVERIFIED_FACT fact-678afdb7b136dacf: effect=0.44 is not in located span', 'L1: UNVERIFIED_FACT fact-4226ef6ef8d40885: effect=0.44 is not in located span', 'L1: UNVERIFIED_FACT fact-298ce178cac69326: ai=9 is not in located span', 'L1: UNVERIFIED_FACT page-493710a08974e1c59def: effect=0.44 is not in located span', 'L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-ac7ee46f610d331f9d5f: ', 'L1: UNVERIFIED_FACT page-6932aa82a2dd1d6a8809: effect=0.44 is not in located span', 'L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-c9d6c3d3ac2041d7c302: ', 'L1: UNVERIFIED_FACT page-e1b7028299bc2d2ebb72: ai=9 is not in located span']
colchicine-secondary-cv-prevention FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', 'L1: TRANSFORMATION_MISMATCH outcome-pool-59e7df86c97523ccb0a5: ', 'L1: TRANSFORMATION_MISMATCH outcome-pool-1edb4b19950ca26177b7: ']
corticosteroids-cap-mortality PASS []
corticosteroids-covid19-mortality FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', 'L1: TRANSFORMATION_MISMATCH outcome-pool-43f6fac9345263e2b1ca: ']
dapagliflozin-hfpef-hosp FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', "L1: UNVERIFIED_FACT PMID 34711976 in 'Adverse events': n1i=162 is not in located span", 'L1: TRANSFORMATION_MISMATCH outcome-pool-025d02a82699294a1475: ', 'L1: UNVERIFIED_FACT fact-c2a69348550d52a1: n1i=162 is not in located span', 'L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-2083180cd46e8a975272: ', 'L1: UNVERIFIED_FACT page-b003fc0193d848e6101a: n1i=162 is not in located span']
denosumab-vertebral-fracture FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', 'L1: TRANSFORMATION_MISMATCH outcome-pool-2cdedfa06a742ac92b05: ', 'L1: TRANSFORMATION_MISMATCH outcome-pool-79693729b8e287c11d44: ', 'L1: TRANSFORMATION_MISMATCH outcome-pool-097a2ee803b56f631fa5: ']
doac-vte-recurrence FAIL ["PAPER: manuscript prose contains numerals not derived from the review object: ['1.10'] (every manuscript number must be object-derived — see manuscript.object_numerals)"]
dpp4-mace-t2d PASS []
empagliflozin-hfpef-hosp FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', 'L1: TRANSFORMATION_MISMATCH outcome-pool-210e3e41a4ecc84c1ede: ']
esketamine-trd-madrs FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', "L1: UNVERIFIED_FACT NCT02417064 in 'Observed-case Day-28 raw change-score MADRS MD': missing full document_sha256", 'L1: UNVERIFIED_FACT fact-f3ea8b421ed7073f: missing full document_sha256', 'L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-3eb6be4b0ded31dbbc50: ', 'L1: UNRECOMPUTABLE_TRANSFORMATION page-b2a42c00a08ef789422c: ', 'L1: UNVERIFIED_FACT page-285d4286effb168c9e5b: missing full document_sha256', 'L1: UNRECOMPUTABLE_TRANSFORMATION manuscript-result: ']
finerenone-ckd-t2d-renal PASS []
glp1-ra-mace-t2d PASS []
iv-iron-hfref-hosp PASS []
melatonin-primary-insomnia-sol FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', "PAPER: manuscript prose contains numerals not derived from the review object: ['17.40'] (every manuscript number must be object-derived — see manuscript.object_numerals)", 'L1: UNRECOMPUTABLE_TRANSFORMATION manuscript-result: ']
metformin-pcos-ovulation FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', "L1: UNVERIFIED_FACT PMID 19522426 in 'Ovulation with metformin added to clomifene': missing full document_sha256", "L1: UNVERIFIED_FACT PMID 16769748 in 'Ovulation with metformin added to clomifene': missing full document_sha256", 'L1: UNVERIFIED_FACT fact-4abcc706d557487b: missing full document_sha256', 'L1: UNVERIFIED_FACT fact-f21cf6595fa2313b: missing full document_sha256', 'L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-f13021c9b8fc61d86407: ', 'L1: UNRECOMPUTABLE_TRANSFORMATION page-8aef831dd12625bebc6c: ', 'L1: UNVERIFIED_FACT page-3ca966bc53d9ab93547d: missing full document_sha256', 'L1: UNVERIFIED_FACT page-6d432e180c2d2cf1c317: missing full document_sha256', 'L1: UNRECOMPUTABLE_TRANSFORMATION manuscript-result: ']
noac-vs-warfarin-af-stroke FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', "L1: UNVERIFIED_FACT PMID 24251359 in 'Stroke or systemic embolism': missing full document_sha256", "L1: UNVERIFIED_FACT PMID 21830957 in 'Major bleeding': missing full document_sha256", "L1: UNVERIFIED_FACT PMID 19717844 in 'Major bleeding': missing full document_sha256", 'L1: UNVERIFIED_FACT fact-82b0df5cb74840e5: missing full document_sha256', 'L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-07f1001291554d2d8c5c: ', 'L1: UNVERIFIED_FACT fact-986328e5d54e9145: missing full document_sha256', 'L1: UNVERIFIED_FACT fact-879cb8e5d9a962f0: missing full document_sha256', 'L1: UNRECOMPUTABLE_TRANSFORMATION page-8686899c5ae8c4b3f434: ', 'L1: UNVERIFIED_FACT page-3d0b63fc5a778a6caeb2: missing full document_sha256', 'L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-fd270d8b9958ec3eb287: ', 'L1: UNRECOMPUTABLE_TRANSFORMATION page-894cc44434fb0f1419dc: ', 'L1: UNVERIFIED_FACT page-33490edffca0a5b81638: missing full document_sha256', 'L1: UNVERIFIED_FACT page-02c9dbc277b7995ca941: missing full document_sha256', 'L1: UNRECOMPUTABLE_TRANSFORMATION manuscript-result: ']
omega3-cardiovascular-events FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', 'L1: TRANSFORMATION_MISMATCH outcome-pool-d2675cff2a98c4b81a8b: ']
pcsk9-mace FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', "L1: UNVERIFIED_FACT PMID 28304224 in 'Major adverse cardiovascular events': missing full document_sha256", "L1: UNVERIFIED_FACT PMID 30403574 in 'Major adverse cardiovascular events': record and ledger retrieval disagree", "L1: UNVERIFIED_FACT PMID 41211925 in 'Major adverse cardiovascular events': record and ledger retrieval disagree", "L1: UNVERIFIED_FACT PMID 25773378 in 'Injection-site reactions': record and ledger retrieval disagree", 'L1: UNVERIFIED_FACT fact-6d8c2d3c732243fd: missing full document_sha256', 'L1: UNVERIFIED_FACT fact-3019ccafd5c4a834: record and ledger retrieval disagree', 'L1: UNVERIFIED_FACT fact-78fea5229ed0e669: record and ledger retrieval disagree', 'L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-8c7f9b363709dd982af5: ', 'L1: UNVERIFIED_FACT fact-0d934054c0d13556: record and ledger retrieval disagree', 'L1: UNRECOMPUTABLE_TRANSFORMATION page-57427829c244a2aba02a: ', 'L1: UNVERIFIED_FACT page-250e11a870abc28a8239: missing full document_sha256', 'L1: UNVERIFIED_FACT page-a65ebf42649f97d8a3d4: record and ledger retrieval disagree', 'L1: UNVERIFIED_FACT page-2eada5be437b29631b0f: record and ledger retrieval disagree', 'L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-2a6d6f1fdc817a38733c: ', 'L1: UNVERIFIED_FACT page-35fc6e6e8c567872601a: record and ledger retrieval disagree', 'L1: UNRECOMPUTABLE_TRANSFORMATION manuscript-result: ']
probiotics-aad-prevention FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', "L1: UNVERIFIED_FACT PMID 26973849 in 'Antibiotic-associated diarrhoea': missing full document_sha256", "L1: UNVERIFIED_FACT PMID 15740542 in 'Antibiotic-associated diarrhoea': missing full document_sha256", "L1: UNVERIFIED_FACT PMID 18026577 in 'Antibiotic-associated diarrhoea': missing full document_sha256", "L1: UNVERIFIED_FACT PMID 26973849 in 'Any adverse events': ai=18 is not in located span", 'L1: UNVERIFIED_FACT fact-99476a70e4d3826c: missing full document_sha256', 'L1: UNVERIFIED_FACT fact-e575d41b98d5c254: missing full document_sha256', 'L1: UNVERIFIED_FACT fact-fdb4e81c0af8e452: missing full document_sha256', 'L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-aa9f49e0993873869a06: ', 'L1: UNVERIFIED_FACT fact-57fb69375d564852: ai=18 is not in located span', 'L1: UNRECOMPUTABLE_TRANSFORMATION page-0c997966487600743917: ', 'L1: UNVERIFIED_FACT page-0238367691688a44a31d: missing full document_sha256', 'L1: UNVERIFIED_FACT page-b4a2cf45e15d1637040f: missing full document_sha256', 'L1: UNVERIFIED_FACT page-dce98fb5f874269a8d4e: missing full document_sha256', 'L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-0a40f3bcea3313b67b27: ', 'L1: UNRECOMPUTABLE_TRANSFORMATION page-3c93b8af62e0872e2684: ', 'L1: UNVERIFIED_FACT page-4cd9eef41d505015ab71: ai=18 is not in located span', 'L1: UNRECOMPUTABLE_TRANSFORMATION manuscript-result: ']
sacubitril-valsartan-hfref PASS []
semaglutide-obesity-mace FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', 'L1: TRANSFORMATION_MISMATCH outcome-pool-6cd355069e45994ab7f6: ']
semaglutide-obesity-weight PASS []
sglt2-ckd-progression FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', 'L1: TRANSFORMATION_MISMATCH outcome-pool-652527d3e18b83b0fc47: ', 'L1: TRANSFORMATION_MISMATCH outcome-pool-645faa70dc6c2636efc2: ']
sglt2-hfref-hosp-cvdeath PASS []
sglt2-primary-prevention-hf FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', "L1: UNVERIFIED_FACT PMID 28605608 in 'Hospitalization for heart failure': missing full document_sha256", "L1: UNVERIFIED_FACT PMID 26378978 in 'Hospitalization for heart failure': missing full document_sha256", "L1: UNVERIFIED_FACT PMID 32966714 in 'Hospitalization for heart failure': missing full document_sha256", 'L1: UNVERIFIED_FACT fact-8d85b8b8ad75a1bd: missing full document_sha256', 'L1: UNVERIFIED_FACT fact-b415d8fd10219f2b: missing full document_sha256', 'L1: UNVERIFIED_FACT fact-bb908d09d124bd12: missing full document_sha256', 'L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-4cb89175869c755ddca4: ', 'L1: UNRECOMPUTABLE_TRANSFORMATION page-b7b5e497f293b6b5f3f2: ', 'L1: UNVERIFIED_FACT page-f1a6842a74022c4d5f46: missing full document_sha256', 'L1: UNVERIFIED_FACT page-187f49861a6df13897de: missing full document_sha256', 'L1: UNVERIFIED_FACT page-3b551ce7f70f80b54eb0: missing full document_sha256', 'L1: TRANSFORMATION_MISMATCH outcome-pool-4d42d7bc428c1b335ac0: ', 'L1: UNRECOMPUTABLE_TRANSFORMATION manuscript-result: ']
spironolactone-hfref-mortality PASS []
statins-primary-prevention-elderly PASS []
ticagrelor-vs-clopidogrel-acs PASS []
tocilizumab-covid19-mortality FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', 'L1: TRANSFORMATION_MISMATCH outcome-pool-27c3e0075cd58b0328f2: ']
tranexamic-acid-pph FAIL ['L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects', "L1: UNVERIFIED_FACT PMID 28456509 in 'Thromboembolic events': missing full document_sha256", 'L1: TRANSFORMATION_MISMATCH outcome-pool-7b62ae2efa1b63fe1310: ', 'L1: UNVERIFIED_FACT fact-cb44860f6f3ca2b3: missing full document_sha256', 'L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-ca0eee51a5dee0b2afb5: ', 'L1: UNVERIFIED_FACT page-48b12cee6170f4ef4a93: missing full document_sha256']
12 of 32 review pages passed
```

### verify-all

```text
TARGET verify_all: head=3f8add72d50b84eae2000625387e3194137a06ea base=none tree=dirty:735 files files=1 scripts/verify_all.py
VERIFY-ALL: 11 limbs, all run, fail-closed. root=C:\mh-r-RV1
  [          REFUSED] unit tests (pytest tests/)  (2915s)
        TARGET verify_all.limb_unit_tests: head=3f8add72d50b84eae2000625387e3194137a06ea base=none tree=dirty:735 files files=180 tests/conftest.py tests/test_aact_cache.py tests/test_aact_recurrent_guard.py ...
                            assert table.locator('tbody tr').count()==len(fs)
                            assert table.locator('th').all_text_contents()==[
                                'Family ID','Acronym','Reports by role','Arms','Contrasts','Eligibility','Lifecycle','Per-outcome status']
        >                   assert table.locator('.family-count-chain').inner_text()=='[TRANSFORMATION] '+trial_family.count_sentence(review['family_count_chain'])
        E                   AssertionError: assert '[TRANSFORMAT...is preserved.' == '[TRANSFORMAT...is preserved.'
        E                     
        E                     - [TRANSFORMATION] 13 publications screened + 234 registry records → 238 trial families → 143 eligible families → 7 contributing families. 143 trials met eligibility. 84 families have unresolved structural eligibility; existing pooling membership is preserved.
        E                     + [TRANSFORMATION] Open-scope family assembly: 13 publications screened + 234 registry records → 238 trial families → 143 eligible families → 7 contributing families. 143 trials met eligibility. 84 families have unresolved structural eligibility; existing pooling membership is preserved.
        E                     ?                  ++++++++++++++++++++++++++++
        
        tests\test_trial_family_ui.py:49: AssertionError
        =========================== short test summary info ===========================
        FAILED tests/test_rob_sensitivity_predicate.py::test_page_uses_per_item_states_instead_of_stale_sensitivity_totals
        FAILED tests/test_trial_family_ui.py::test_family_table_in_live_browser - Ass...
        2 failed, 1181 passed in 2911.26s (0:48:31)
  [             PASS] offline reproduction (every live page replays from committed cache)  (1072s)
        TARGET verify_all.limb_reproduction: head=3f8add72d50b84eae2000625387e3194137a06ea base=none tree=dirty:735 files files=33 scripts/reproduce_review.py docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json docs/reviews/colchicine-postop-af/review.json ...
  [          REFUSED] publication gate on every live review page  (1795s)
        TARGET verify_all.limb_gate_every_page: head=3f8add72d50b84eae2000625387e3194137a06ea base=none tree=dirty:735 files files=32 docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json docs/reviews/colchicine-postop-af/review.json docs/reviews/colchicine-recurrent-pericarditis/review.json ...
        colchicine-postop-af: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: TRANSFORMATION_MISMATCH outcome-pool-4a9743816e814e344bbc: ; L1: UNRECOMPUTABLE_TRANSFORMATION manuscript-result: 
        colchicine-recurrent-pericarditis: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: UNVERIFIED_FACT PMID 21873705 in 'Recurrent pericarditis': effect=0.44 is not in located span; L1: UNVERIFIED_FACT PMID 21873705 in 'Symptom persistence at 72 hours': effect=0.44 is not in located span; L1: UNVERIFIED_FACT PMID 24694983 in 'Adverse events (gastrointestinal)': ai=9 is not in located span; L1: UNVERIFIED_FACT fact-678afdb7b136dacf: effect=0.44 is not in located span; L1: UNVERIFIED_FACT fact-4226ef6ef8d40885: effect=0.44 is not in located span; L1: UNVERIFIED_FACT fact-298ce178cac69326: ai=9 is not in located span; L1: UNVERIFIED_FACT page-493710a08974e1c59def: effect=0.44 is not in located span; L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-ac7ee46f610d331f9d5f: ; L1: UNVERIFIED_FACT page-6932aa82a2dd1d6a8809: effect=0.44 is not in located span; L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-c9d6c3d3ac2041d7c302: ; L1: UNVERIFIED_FACT page-e1b7028299bc2d2ebb72: ai=9 is not in located span
        colchicine-secondary-cv-prevention: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: TRANSFORMATION_MISMATCH outcome-pool-59e7df86c97523ccb0a5: ; L1: TRANSFORMATION_MISMATCH outcome-pool-1edb4b19950ca26177b7: 
        corticosteroids-covid19-mortality: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: TRANSFORMATION_MISMATCH outcome-pool-43f6fac9345263e2b1ca: 
        dapagliflozin-hfpef-hosp: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: UNVERIFIED_FACT PMID 34711976 in 'Adverse events': n1i=162 is not in located span; L1: TRANSFORMATION_MISMATCH outcome-pool-025d02a82699294a1475: ; L1: UNVERIFIED_FACT fact-c2a69348550d52a1: n1i=162 is not in located span; L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-2083180cd46e8a975272: ; L1: UNVERIFIED_FACT page-b003fc0193d848e6101a: n1i=162 is not in located span
        denosumab-vertebral-fracture: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: TRANSFORMATION_MISMATCH outcome-pool-2cdedfa06a742ac92b05: ; L1: TRANSFORMATION_MISMATCH outcome-pool-79693729b8e287c11d44: ; L1: TRANSFORMATION_MISMATCH outcome-pool-097a2ee803b56f631fa5: 
        empagliflozin-hfpef-hosp: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: TRANSFORMATION_MISMATCH outcome-pool-210e3e41a4ecc84c1ede: 
        esketamine-trd-madrs: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: UNVERIFIED_FACT NCT02417064 in 'Observed-case Day-28 raw change-score MADRS MD': missing full document_sha256; L1: UNVERIFIED_FACT fact-f3ea8b421ed7073f: missing full document_sha256; L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-3eb6be4b0ded31dbbc50: ; L1: UNRECOMPUTABLE_TRANSFORMATION page-b2a42c00a08ef789422c: ; L1: UNVERIFIED_FACT page-285d4286effb168c9e5b: missing full document_sha256; L1: UNRECOMPUTABLE_TRANSFORMATION manuscript-result: 
        melatonin-primary-insomnia-sol: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: UNRECOMPUTABLE_TRANSFORMATION manuscript-result: 
        metformin-pcos-ovulation: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: UNVERIFIED_FACT PMID 19522426 in 'Ovulation with metformin added to clomifene': missing full document_sha256; L1: UNVERIFIED_FACT PMID 16769748 in 'Ovulation with metformin added to clomifene': missing full document_sha256; L1: UNVERIFIED_FACT fact-4abcc706d557487b: missing full document_sha256; L1: UNVERIFIED_FACT fact-f21cf6595fa2313b: missing full document_sha256; L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-f13021c9b8fc61d86407: ; L1: UNRECOMPUTABLE_TRANSFORMATION page-8aef831dd12625bebc6c: ; L1: UNVERIFIED_FACT page-3ca966bc53d9ab93547d: missing full document_sha256; L1: UNVERIFIED_FACT page-6d432e180c2d2cf1c317: missing full document_sha256; L1: UNRECOMPUTABLE_TRANSFORMATION manuscript-result: 
        noac-vs-warfarin-af-stroke: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: UNVERIFIED_FACT PMID 24251359 in 'Stroke or systemic embolism': missing full document_sha256; L1: UNVERIFIED_FACT PMID 21830957 in 'Major bleeding': missing full document_sha256; L1: UNVERIFIED_FACT PMID 19717844 in 'Major bleeding': missing full document_sha256; L1: UNVERIFIED_FACT fact-82b0df5cb74840e5: missing full document_sha256; L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-07f1001291554d2d8c5c: ; L1: UNVERIFIED_FACT fact-986328e5d54e9145: missing full document_sha256; L1: UNVERIFIED_FACT fact-879cb8e5d9a962f0: missing full document_sha256; L1: UNRECOMPUTABLE_TRANSFORMATION page-8686899c5ae8c4b3f434: ; L1: UNVERIFIED_FACT page-3d0b63fc5a778a6caeb2: missing full document_sha256; L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-fd270d8b9958ec3eb287: ; L1: UNRECOMPUTABLE_TRANSFORMATION page-894cc44434fb0f1419dc: ; L1: UNVERIFIED_FACT page-33490edffca0a5b81638: missing full document_sha256; L1: UNVERIFIED_FACT page-02c9dbc277b7995ca941: missing full document_sha256; L1: UNRECOMPUTABLE_TRANSFORMATION manuscript-result: 
        omega3-cardiovascular-events: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: TRANSFORMATION_MISMATCH outcome-pool-d2675cff2a98c4b81a8b: 
        pcsk9-mace: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: UNVERIFIED_FACT PMID 28304224 in 'Major adverse cardiovascular events': missing full document_sha256; L1: UNVERIFIED_FACT PMID 30403574 in 'Major adverse cardiovascular events': record and ledger retrieval disagree; L1: UNVERIFIED_FACT PMID 41211925 in 'Major adverse cardiovascular events': record and ledger retrieval disagree; L1: UNVERIFIED_FACT PMID 25773378 in 'Injection-site reactions': record and ledger retrieval disagree; L1: UNVERIFIED_FACT fact-6d8c2d3c732243fd: missing full document_sha256; L1: UNVERIFIED_FACT fact-3019ccafd5c4a834: record and ledger retrieval disagree; L1: UNVERIFIED_FACT fact-78fea5229ed0e669: record and ledger retrieval disagree; L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-8c7f9b363709dd982af5: ; L1: UNVERIFIED_FACT fact-0d934054c0d13556: record and ledger retrieval disagree; L1: UNRECOMPUTABLE_TRANSFORMATION page-57427829c244a2aba02a: ; L1: UNVERIFIED_FACT page-250e11a870abc28a8239: missing full document_sha256; L1: UNVERIFIED_FACT page-a65ebf42649f97d8a3d4: record and ledger retrieval disagree; L1: UNVERIFIED_FACT page-2eada5be437b29631b0f: record and ledger retrieval disagree; L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-2a6d6f1fdc817a38733c: ; L1: UNVERIFIED_FACT page-35fc6e6e8c567872601a: record and ledger retrieval disagree; L1: UNRECOMPUTABLE_TRANSFORMATION manuscript-result: 
        probiotics-aad-prevention: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: UNVERIFIED_FACT PMID 26973849 in 'Antibiotic-associated diarrhoea': missing full document_sha256; L1: UNVERIFIED_FACT PMID 15740542 in 'Antibiotic-associated diarrhoea': missing full document_sha256; L1: UNVERIFIED_FACT PMID 18026577 in 'Antibiotic-associated diarrhoea': missing full document_sha256; L1: UNVERIFIED_FACT PMID 26973849 in 'Any adverse events': ai=18 is not in located span; L1: UNVERIFIED_FACT fact-99476a70e4d3826c: missing full document_sha256; L1: UNVERIFIED_FACT fact-e575d41b98d5c254: missing full document_sha256; L1: UNVERIFIED_FACT fact-fdb4e81c0af8e452: missing full document_sha256; L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-aa9f49e0993873869a06: ; L1: UNVERIFIED_FACT fact-57fb69375d564852: ai=18 is not in located span; L1: UNRECOMPUTABLE_TRANSFORMATION page-0c997966487600743917: ; L1: UNVERIFIED_FACT page-0238367691688a44a31d: missing full document_sha256; L1: UNVERIFIED_FACT page-b4a2cf45e15d1637040f: missing full document_sha256; L1: UNVERIFIED_FACT page-dce98fb5f874269a8d4e: missing full document_sha256; L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-0a40f3bcea3313b67b27: ; L1: UNRECOMPUTABLE_TRANSFORMATION page-3c93b8af62e0872e2684: ; L1: UNVERIFIED_FACT page-4cd9eef41d505015ab71: ai=18 is not in located span; L1: UNRECOMPUTABLE_TRANSFORMATION manuscript-result: 
        semaglutide-obesity-mace: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: TRANSFORMATION_MISMATCH outcome-pool-6cd355069e45994ab7f6: 
        sglt2-ckd-progression: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: TRANSFORMATION_MISMATCH outcome-pool-652527d3e18b83b0fc47: ; L1: TRANSFORMATION_MISMATCH outcome-pool-645faa70dc6c2636efc2: 
        sglt2-primary-prevention-hf: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: UNVERIFIED_FACT PMID 28605608 in 'Hospitalization for heart failure': missing full document_sha256; L1: UNVERIFIED_FACT PMID 26378978 in 'Hospitalization for heart failure': missing full document_sha256; L1: UNVERIFIED_FACT PMID 32966714 in 'Hospitalization for heart failure': missing full document_sha256; L1: UNVERIFIED_FACT fact-8d85b8b8ad75a1bd: missing full document_sha256; L1: UNVERIFIED_FACT fact-b415d8fd10219f2b: missing full document_sha256; L1: UNVERIFIED_FACT fact-bb908d09d124bd12: missing full document_sha256; L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-4cb89175869c755ddca4: ; L1: UNRECOMPUTABLE_TRANSFORMATION page-b7b5e497f293b6b5f3f2: ; L1: UNVERIFIED_FACT page-f1a6842a74022c4d5f46: missing full document_sha256; L1: UNVERIFIED_FACT page-187f49861a6df13897de: missing full document_sha256; L1: UNVERIFIED_FACT page-3b551ce7f70f80b54eb0: missing full document_sha256; L1: TRANSFORMATION_MISMATCH outcome-pool-4d42d7bc428c1b335ac0: ; L1: UNRECOMPUTABLE_TRANSFORMATION manuscript-result: 
        tocilizumab-covid19-mortality: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: TRANSFORMATION_MISMATCH outcome-pool-27c3e0075cd58b0328f2: 
        tranexamic-acid-pph: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: UNVERIFIED_FACT PMID 28456509 in 'Thromboembolic events': missing full document_sha256; L1: TRANSFORMATION_MISMATCH outcome-pool-7b62ae2efa1b63fe1310: ; L1: UNVERIFIED_FACT fact-cb44860f6f3ca2b3: missing full document_sha256; L1: UNRECOMPUTABLE_TRANSFORMATION outcome-pool-ca0eee51a5dee0b2afb5: ; L1: UNVERIFIED_FACT page-48b12cee6170f4ef4a93: missing full document_sha256
  [             PASS] index currency (generated == committed docs/index.html)  (14s)
        TARGET verify_all.limb_index_currency: head=3f8add72d50b84eae2000625387e3194137a06ea base=none tree=dirty:735 files files=696 docs/index.html docs/evidence/CAPTIONS.json docs/evidence/CAPTIONS.json ...
  [             PASS] served-artefact leak scan (docs/*.json)  (2s)
        TARGET verify_all.limb_leak_scan: head=3f8add72d50b84eae2000625387e3194137a06ea base=none tree=dirty:735 files files=132 docs/adjustment_label_sweep.json docs/arm_object_sweep.json docs/claim_scope_sweep.json ...
  [             PASS] held-out leak detector (registry/heldout_sealed.json)  (361s)
        TARGET verify_all.limb_heldout: head=3f8add72d50b84eae2000625387e3194137a06ea base=none tree=dirty:735 files files=3 registry/heldout_sealed.json docs/search_recall_regression_corpus.json harness/acquisition.py
  [          REFUSED] search completeness (search_v2 measurement current; every state explicit; no zero from an exit code)  (2s)
        TARGET verify_all.limb_search_completeness: head=3f8add72d50b84eae2000625387e3194137a06ea base=none tree=dirty:735 files files=3 registry/search_completeness.json harness/search_v2.py harness/search_completeness.py
        search completeness REFUSED: engine changed since the published search_v2 measurement (a57dc45d6824 -> d278c2f7f852); re-run scripts/search_v2_run.py and re-publish before landing || states: RAN_OK 0 of 21; RAN_OK_WITH_SOURCE_ERRORS 21 of 21; RAN_ZERO 0 of 21; RAN_ERROR 0 of 21; NOT_RUN 0 of 21
  [             PASS] fix-state discipline (registry/fixes.json)  (139s)
        TARGET verify_all.limb_fixstate: head=3f8add72d50b84eae2000625387e3194137a06ea base=none tree=dirty:735 files files=3 registry/fixes.json docs/fix_ledger.json scripts/render_fix_ledger.py
  [          REFUSED] honest-state ratchet (no page may get quieter)  (31s)
        TARGET verify_all.limb_honest_ratchet: head=3f8add72d50b84eae2000625387e3194137a06ea base=none tree=dirty:735 files files=34 docs/index.html docs/ratchet_acknowledgements.json docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html ...
        TARGET honest_ratchet: head=3f8add72d50b84eae2000625387e3194137a06ea base=2304824034b4ba8677da2d2d2453352711ed2a9b tree=dirty:735 files files=34 docs/index.html docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html docs/reviews/colchicine-postop-af/index.html ... base_resolution=merge-base origin/main pages=33 block_floor_refs=2304824034b4ba8677da2d2d2453352711ed2a9b,50f5a67b4fb19ada4716a0df6e6b68c2e4618304
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: never_considered: base count 1, new count 0
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/colchicine-postop-af/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/colchicine-recurrent-pericarditis/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/colchicine-secondary-cv-prevention/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/corticosteroids-cap-mortality/index.html: never_considered: base count 1, new count 0
        docs/reviews/corticosteroids-cap-mortality/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/corticosteroids-covid19-mortality/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/denosumab-vertebral-fracture/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/denosumab-vertebral-fracture/index.html: declared_absent: base count 8, new count 7
        docs/reviews/doac-vte-recurrence/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/dpp4-mace-t2d/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/empagliflozin-hfpef-hosp/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/esketamine-trd-madrs/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/finerenone-ckd-t2d-renal/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/glp1-ra-mace-t2d/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/iv-iron-hfref-hosp/index.html: refusal_counterfactual: base count 2, new count 0
        docs/reviews/iv-iron-hfref-hosp/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/iv-iron-hfref-hosp/index.html: suppressed_pool: base count 2, new count 0
        docs/reviews/melatonin-primary-insomnia-sol/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/metformin-pcos-ovulation/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/omega3-cardiovascular-events/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/pcsk9-mace/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/probiotics-aad-prevention/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/sacubitril-valsartan-hfref/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/semaglutide-obesity-mace/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/semaglutide-obesity-mace/index.html: declared_absent: base count 5, new count 1
        docs/reviews/semaglutide-obesity-weight/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/sglt2-ckd-progression/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/sglt2-primary-prevention-hf/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/spironolactone-hfref-mortality/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/statins-primary-prevention-elderly/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/tocilizumab-covid19-mortality/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/tranexamic-acid-pph/index.html: retrieval_class: base count 4, new count 2
        docs/index.html: lost banner block b6f0ec4ee42a22f99043b2d7d326c38eae34e7e26e01545b2b91a66f891d3eb6: What this is A reproducible harness that builds meta-analyses from a committed protocol, and publishes each as a tabbed,
        docs/index.html: lost banner block 464c8c9c75a2f31ac87977d08168f299b98c0a7bf90b0b4be670e95711b276d6: We measured our own error rate (no meta-analysis reports this about itself) Measured on 2026-09-12 against the 99 pooled
        docs/index.html: lost banner block f2b41f2edf033ecc02ec2067a325e375105a02d046a87022eff31c6db61cc53d: Every pooled number is verified against its source (gate-enforced) All 115 of 115 pooled trial-outcome numbers across th
        docs/index.html: lost banner block 2c1c3da7038bd131e062ff9854e52955fbfc9f879c8cda1c38a211b17e690ec9: Gate scorecard: plant validations and production refusals Adjudication coverage first, so the unresolved cannot disappea
        docs/index.html: lost banner block 14d82d4fda711fe9fe91721913d27f94c8af2fd442ab1832769897c57d897bbd: Parity with the published comparator (the finishing metric) For each same-scope topic: our pooled k vs the comparable co
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 4b7727eef8d232f0da19e70aaa6c4a3ba0c0ceb3cc4ffd0ed58f8cbf0871e23e: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 99736327bb6305c2a8b554c3cd07e1c1829ed74d3571b250e4547ce947ac13cb: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost banner block 983558e05e4bde77fc9f1394d2730329176e5f9c1a38a74fbd4a55e73f4d7b64: Snapshot: records_sha256 42df5c5c ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block f0dfdb69520b2088813d9a3c61c5790ab82f3b6dda10e8396569e3f5337f6724: Pool changed because a design refusal was added. Pool changed because a design refusal was added: reconstructed cluster,
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 004b373d6745c3bceae9513a9cf6a310bcc0136ae4b973c898d1a7355e062a4b: DECLARED ABSENT. DESIGN REFUSAL: after refusing reconstructed non-parallel designs without an explicit design adjustment
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 1158f8935c9c47a2685dad719ef8d411cf1af64a0f89cad4447f3d3543c09ed4: DECLARED ABSENT. DESIGN REFUSAL: after refusing reconstructed non-parallel designs without an explicit design adjustment
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 187218cede8a19de486ebe8f5ccbfbc4eb94a54238aae46662ee26a3cfd57155: Unit-of-analysis/design caveat (disclosed, not silently adjusted). 1 pooled trial(s) are individual-randomized factorial
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 52cd04e3a915bdf5778422eb031e9852886b3c694807455f9b05173937be4eb6: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 2c19afc5ad0d30515b877f866f1642b96a8121d5e7bad11f30471f93c7ee7ba9: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block f85a78807d31d85343a73c78d55902375bf1265142747d58d473e433855e41b4: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 7d49f76d89a220055f1ad2c49e47c1e9533f5eeb0458e5ccb74126a0080713a6: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/colchicine-postop-af/index.html: lost absent block 716b0cfa558da9c9cf0b73b9c00fff61fb366d1c1922fbde3c924889e43376e9: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/colchicine-postop-af/index.html: lost absent block d62cdb5282485d50fb39ea3f2220dc3759b5fd1cf68001aefb83f7027fd354bd: HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH We retract any claim of a registr
        docs/reviews/colchicine-postop-af/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/colchicine-postop-af/index.html: lost banner block 67757344ee670d1fcf41cf97cb423c0106fadab6c8cbeb3fca2968bdc4906419: Snapshot: records_sha256 474eff90 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/colchicine-postop-af/index.html: lost absent block c05a643044807856d475f2cbb9760c9bec2c21afb0d8bc0b755ef3e4ed55acef: HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH We retract any claim of a registr
        docs/reviews/colchicine-postop-af/index.html: lost absent block 09bdb49b28d751b80a19a5156efc48af5a3d03b86e50c38f917ab02f3c739977: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/colchicine-postop-af/index.html: lost absent block 495235b1876947f1d9a30a5c8ea500210e934af0435b75583c677fb079a6e5d2: Cross-family definition audit. Two independent model families (Gemini via AGY, and Fable) re-read every pooled row and c
        docs/reviews/colchicine-postop-af/index.html: lost absent block c37a2ca56df8e47967377077be78ba1eb29ac6e9bb6d885d60e2ccb5bf4f13a2: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 32720823, 25172965, 27502857 mention this outcome in th
        docs/reviews/colchicine-postop-af/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/colchicine-postop-af/index.html: lost absent block 9b1884cdd73a6a0f9056e82edd34706a8f1982b178287effdf441da7649bbf9e: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/colchicine-postop-af/index.html: lost absent block c6f55d3c41f28551439f475dcc2443401b255683274ce3f5a9decaf1af143876: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/colchicine-postop-af/index.html: lost absent block c3dab676c7cc4c4ed7c1430bc1f86f0463968a9ec0d1c2af796b6433c250b494: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/colchicine-postop-af/index.html: lost absent block 8dfc2f4ddd13b517cfa67ebda9a6a3790c8a1fea50c7298b85e933bf628f1531: Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a 
        docs/reviews/colchicine-postop-af/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/colchicine-postop-af/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 7e10b18d2269e7ef99c4d7d65d4d91eaa4dc91af811071f6337c230bc0dc27ce: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block d62cdb5282485d50fb39ea3f2220dc3759b5fd1cf68001aefb83f7027fd354bd: HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH We retract any claim of a registr
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost banner block cb451432c3ac88913aa5c78c93cb9a26e55e78e46ea019031e32740e2d51e33f: Snapshot: records_sha256 570a1143 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block c05a643044807856d475f2cbb9760c9bec2c21afb0d8bc0b755ef3e4ed55acef: HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH We retract any claim of a registr
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 09bdb49b28d751b80a19a5156efc48af5a3d03b86e50c38f917ab02f3c739977: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 35796885b3d2c2e5be64620d349b207156e46180364251814e44b2cfaa950554: Cross-family definition audit. Two independent model families (Gemini via AGY, and Fable) re-read every pooled row and c
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 3e4ff9baf43748afb1a0433905ca82c6b9cff459a9e70e9781ff900d7e0ed1c8: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 23992557, 21873705 mention this outcome in the committe
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 35058ebae3177e56f4a895db383c9b55873db12d137ac96aee2284d7619ddabb: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 24694983, 23992557, 21873705 mention this outcome in th
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 90d0d6414efc79f07b43707db054bcefac42ac266537d38d442fc53fb0773481: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block ca87b29f09498e773e1db7567bea84ec257efbd15950522c003e127d73e1d04a: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block d581286a505b55582c586d2d6eab2fb7c1fff552d507c802bb801d50765ab395: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 275b80a153f01f0d7930a7adecfb86ba9b0eee0b0a7cd982a26748a3c8ac4f41: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block b12bce01293f2848ebd9749b1d5706ad4943a114e91f2fa9e805851371da97e3: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 711dff193570d7221b8353f38c88cd4a7d9aeac2516f97b46ac0e744fe7c5615: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost banner block 9c45871f77ef0834e639a21ece88d52b77c3763fbeed9748b6aaba8d9a8127a6: Snapshot: records_sha256 2d3b2a35 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 92244e65e9109ddd8af1d58dd125658b64f23996fd2961b60fa1678335cfd439: Cross-family definition audit. Two independent model families (Gemini via AGY, and Fable) re-read every pooled row and c
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 79e8530721620a41dd9245d709864502413f259d5443c1347b5939ae65fa0292: Unit-of-analysis/design caveat (disclosed, not silently adjusted). 1 pooled trial(s) are individual-randomized factorial
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 2f35820b0771882ce825e008c91720427f3067b3757140fa18acd821b341b27b: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block f640e854cfd1e10d0a39cfad5f14c70825f998fef6c8ee76251e10eeee8d2e7e: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 57205a3c80284c1aeff24226ff5968fc5934014af55e2b4724303c7a4e83c3af: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block a54ecd524eced807f0962ba546cc1fda3db13f551f886144467a6f2ea0d59259: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 0b593a081534693db547d22eb75a3d89a87c235bd8c5807d225902089abd92b7: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 0988c08ad2471bb591e7066f422bb5aefd81c6b090f38af9ada72d821425a209: HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH We retract any claim of a registr
        docs/reviews/corticosteroids-cap-mortality/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/corticosteroids-cap-mortality/index.html: lost banner block 5b90e3f99e5cf7684a31cc3f874cf7bde5f31e413a1fd13ece8f1878718a0ca8: Snapshot: records_sha256 b8a5cc47 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block c05a643044807856d475f2cbb9760c9bec2c21afb0d8bc0b755ef3e4ed55acef: HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH We retract any claim of a registr
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block acb80753fadc32acfe3f94ec93708a4f5dee73845e867d7b3965c10e2eddd08c: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RU
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 35644fab221e8ee190a797369cdd07caaa258b33acf5ea87a0b64a007c780798: Cross-family definition audit. Two independent model families (Gemini via AGY, and Fable) re-read every pooled row and c
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block af1be9f121930cc61ce27b462dd1d544ef8632b057ea2e5143bda3d9514ecf30: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 36942789 mention this outcome in the committed abstract
        docs/reviews/corticosteroids-cap-mortality/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 3d1c9ccfea5434242443d86ca404fbfe5d536dd2daffe26d0e761f2e22b8cc6d: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 09ed6ae25a015e0d8fa49dc6bbc1d5eaec199132b9199b61233147e1ef2af751: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 0f41b767cdeb7f3ac49137913e0bed645a03257d18decfe627336a69244089a4: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 16a31a620c341edc50358ed3a3849f254b021b872920a6a62340b100b4844dff: Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a 
        docs/reviews/corticosteroids-cap-mortality/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block e389e575823a26d0cb6382065905ccd0fa414e0d8811e697382a6b157b191007: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 52c2424e174f4adf5d84862d5486a45cded25f4158f21bd3fab93962a7cc5bc0: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost banner block 7fc5fbe2329e78b3b2f54b921ebeca0bdf21436b44540ef7bf8e6be658cfd276: Snapshot: records_sha256 78f98d29 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 45bb4635fe128500a1ea7b4425bebd42c1abc364f092a64f7256b064807fe3be: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 34138478 mention this outcome in the committed abstract
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 654a8891121ff1083f93b4a07709fc795f187efc842043c4a52afc19586e34b6: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 3f98507b0cda3348baedbf46363de3908b89e1c5d408b2a0f35ef63fb04ffa14: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 460814ddc2ea0b454e2cc59e9a1ddbc97261099c24c7c68b7000dd33fc92a91d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block f11df83d8cdcdf214dcb3553d8907cc6b8122266f3c059c96f4b9c6d1c37ee9a: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block f32f15a5ec6cd8aa058dbe6c632ab0ff726861eb6362c4146a97f034592a7503: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 4a266aa0f9d335743a4f9107c0fc651306d41303071fe7cabdf23eb83387b40e: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost banner block daeb0ac407986902bd35c7ba1addbede483d6e9ef071486d0515468f507fc9d2: Snapshot: records_sha256 91f71997 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block f78c512047bc0437de0926a52df7805b797214433f9feb56344ab2c29eb00219: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 727f47affcd9fbb34f44495c3052b8fe9f36966fcc90f141f6a9d9000cbc3e47: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 51e3022be2a1b8158448c09e50f13e9a095573c315136cb19b22b6400b97028d: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block c2bcf0acd104ff21660b73692747af61dbce3defbf18f5b3c80e1517ca389639: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 78460b7fd842a6407ad20cbdb5d6c465db843d3322956bee461b6900e54a2c20: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block 71e4002ec9f8906c097fbff9ca975a30fafe8656bd556978858a78671ec131b5: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block d76cb0919d2122087bf7c6782ac5a9e2b6e4b2c7d65ed724b7a14fd707b8c0aa: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/denosumab-vertebral-fracture/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/denosumab-vertebral-fracture/index.html: lost banner block 44f777950850cb0d700b1cdd8100689bfd9839e9e43d815d18947aa079767dcc: Snapshot: records_sha256 32165834 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block f1b0d7b429050cfec3a688bdb1df0579012084709efdc927e62da0888bd6fca4: DECLARED ABSENT. no included trial reported this outcome with a percentage-corroborated count or an effect+CI in its abs
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block dbbbd408ec262767dde20079bb7b4a012975f768bb21d8062298b136d4f3eb59: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 19671655 mention this outcome in the committed abstract
        docs/reviews/denosumab-vertebral-fracture/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block 01bcc626a75fd06d2d919c298b41dd968bcb0cf78e30a345fb12d69dad59c5e5: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block ab51bd420fb4b28762145e7f3ea285673ca016cbec97b409d54b532925a03a36: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block cdf08119611dfcdf4ec945d9bea4e527ef45935a09f48e359cb9a83311f74e12: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block ecc8ed947c95752e72c0a6cab09514ec7c5a34cdfc2717544a6d9011a28156f3: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
        docs/reviews/denosumab-vertebral-fracture/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/doac-vte-recurrence/index.html: lost absent block 8d85d2e447f203ca3ca2c7a3a53ec299b5111450ad16acdfcddb56859f8db26c: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/doac-vte-recurrence/index.html: lost absent block 4a266aa0f9d335743a4f9107c0fc651306d41303071fe7cabdf23eb83387b40e: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/doac-vte-recurrence/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/doac-vte-recurrence/index.html: lost banner block 410b0ec6430a9737f71d7faa044221a0bd71653fc1aec9ddfd09f1aad7d0bda1: Snapshot: records_sha256 ef5c1c6b ; retrieved_utc 2026-09-12; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/doac-vte-recurrence/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/doac-vte-recurrence/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/doac-vte-recurrence/index.html: lost absent block 3a81c264385ba5a6575ae6d74cf249ed9936629b836206359bafa3048a74c7a5: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_ER
        docs/reviews/doac-vte-recurrence/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
        docs/reviews/doac-vte-recurrence/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/doac-vte-recurrence/index.html: lost absent block c7f018104f5e77d148ef76b22779d0fc51ae5c32eab1c6266773a42c9e0c5ed7: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/doac-vte-recurrence/index.html: lost absent block d6cdc1b8f2806a8da5ff7e7b5fc45b009b2766c6ef431196a2cf408055a887fb: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/doac-vte-recurrence/index.html: lost absent block da01b6ba519d765f1f7085f7413af2667584916e67a43fd872d8f391a72c3f51: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/doac-vte-recurrence/index.html: lost absent block ac057cdbffb6d6ed529764ed96d02c9bdf085df5d37d7c6dd7ccb84bffb0c38c: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/doac-vte-recurrence/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/doac-vte-recurrence/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block ca478999427457da8d80f523b9328f155916acdfbe6b063d1646697f7201875f: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 4a266aa0f9d335743a4f9107c0fc651306d41303071fe7cabdf23eb83387b40e: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/dpp4-mace-t2d/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/dpp4-mace-t2d/index.html: lost banner block e29da437f91714ae26b2d5f0da715141a26ce67145fa4817cdf7036eb0a353f4: Snapshot: records_sha256 81256a4a ; retrieved_utc 2026-09-12; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 3a81c264385ba5a6575ae6d74cf249ed9936629b836206359bafa3048a74c7a5: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_ER
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
        docs/reviews/dpp4-mace-t2d/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 66d6d9cbc227d9a699cdf986265b2b7c04a066c4b01de1cc8e8e380e0282a071: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 80050dda0a27c639679fbcbb44ad5c7a74c4ca8ac59d189adaf5c8c3756d86b0: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 91ec4628b63b3e86d9c7d2f143975fdc54e4c8782edea24d1fdb19b3fb96c48e: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 6fd4fe1fa9d7c27b9dae78df1aa0508709049363a38be5e9069ba7005c2476a2: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/dpp4-mace-t2d/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block 86248522ae252f46158fa0f19c9654208ea1a7a7ee7a08f74b56e40d8813e6be: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block 104e6394f74782c843c263e25c931c2e4febf1d149fad7db913542eab225e4f2: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost banner block 303b53251c8bad5d3da89eeaf6b9f6db72c408f70f6e3677adf1edd3403438d5: Snapshot: records_sha256 5ef3f171 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block f78c512047bc0437de0926a52df7805b797214433f9feb56344ab2c29eb00219: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block 847f8f1de6a7ebb1a0d274e0afd4eb4acc5ca6c6651bef7dc6127fac5eb92051: Cross-family definition audit. Two independent model families (Gemini via AGY, and Fable) re-read every pooled row and c
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block ecdd529cdb73661a1dc8534de5961bd2c81af1f89d690027dc9ff886a5ba6edf: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block dd19678a5c1c87e7219abc7156beab32777aa31eb791b6ed4e2ce0e301c8acce: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block 90d9054f250f3f8c546865b94358f617dfe8d76608f9e5870ebc508f90c91590: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block 6b24891820614ead5920ab05217a096376de6f5eb595bc20bfa5e723ed576f82: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block c259836475d227609f048b27f7b6ba7edd984a56f49e84041d3c6d9b5e4776e1: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 711dff193570d7221b8353f38c88cd4a7d9aeac2516f97b46ac0e744fe7c5615: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/esketamine-trd-madrs/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/esketamine-trd-madrs/index.html: lost banner block 5db3239db27b959c8a192465d36e1f3a88a928fd9365d0c5e4934a9328852cda: Snapshot: records_sha256 a09370ee ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 51984e7bede57d9bf3873159b06be81aa191c14d5289e9eb38532fa57bca1e01: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_ER
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 4554b38e12246adb7ec988f9bb194fe41e7ef3abdf7fe3db1e2c31bfc5621cc9: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 34696742, 31109201 mention this outcome in the committe
        docs/reviews/esketamine-trd-madrs/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 4c29b75436df70dfc57dde8e4c0b7975089c3303c76a5d93c7c5d95c4e231a5c: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 17c77c145420770141d32fd0d8156b182d450fd35b6287a5cf9b40e2aba0c827: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 7058b2699c4ee2d0f8489f2cd13f365fa05dcf95e49011617b8ecdca765369fd: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 7a1b2f9d0aa30150320bb235576d215f3bc335d0d9a1f07ccb06f24c2efac169: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/esketamine-trd-madrs/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block a3b0bda23d79f8155aa381ec56c8eacfd4f507fec83c11980ad24f3a35194701: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 99736327bb6305c2a8b554c3cd07e1c1829ed74d3571b250e4547ce947ac13cb: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost banner block 5be8b8344e22c6ce007c14827eb881142fd7c71a84282cbd3ba30f865639a7fc: Snapshot: records_sha256 4e838bbb ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 63c17a3b1a6ff026e3216b53bd3c6078e2df601534271776decdd9f03b2480f6: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 33264825, 34449181, 26325557 mention this outcome in th
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block e9b6c91404265dda6919cfe2280db8b34008d4f2ef350e80418e013bd2ccac3d: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 48baaf8c4c6a15bff29b9fe93538aeb4badbc9faaee9c82198b417b94ba1138c: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block cdd5838e9ddf4722e73df01da34e5b8d82b6da2209bfc80e58b07b824f91f06d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 2f96569c95ff0621bf07097dce733e6e727a8f2aa663c83fbc36d42a2ae93a58: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 0606da3be98c8d40045f716df24fd8af88b2ce8b7b3f56953420acfc386da74e: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 4a266aa0f9d335743a4f9107c0fc651306d41303071fe7cabdf23eb83387b40e: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/glp1-ra-mace-t2d/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/glp1-ra-mace-t2d/index.html: lost banner block 1c7e24dd1b2e31a6b2c42983b46322e0b978064c7e0f1784f628645f6bce823a: Snapshot: records_sha256 1e0282f5 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block f78c512047bc0437de0926a52df7805b797214433f9feb56344ab2c29eb00219: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block f3641fa7e56d8d396bc0f8e0e7938987d10f402964ce66d602c13133ff3df1fd: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 31185157, 27295427, 34215025 mention this outcome in th
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 181eb2cc7da5cb8589a7ebe140194b85594aa6dbd6f5994ce6e9d7f982d8e2b8: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 31185157, 27633186, 27295427, 30291013 mention this out
        docs/reviews/glp1-ra-mace-t2d/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 3b5fcb2c43c291d46f0928d1f6dd4f574eb1adc1d212f1113207d41844af8c41: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block ade5009855456019293990bec265c1e0ddea1fda4d155316b7f6728b27fef7eb: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 118737e7052fbdd570b2bb1df218c74b838fe181282b54f53fae236363d15295: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 04a2e41c88e8930b16c4783a824d69b3411af2e0f716308888eb7504faec9d34: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/glp1-ra-mace-t2d/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block ba08811ad90475fc0030bb3737a2a3e82f7973e48c1c61150c5885f7e005e40f: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 99736327bb6305c2a8b554c3cd07e1c1829ed74d3571b250e4547ce947ac13cb: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/iv-iron-hfref-hosp/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 06fd26217042d4d16e030bb836f29e30203fb4c94b622eb2177b70dcd8d72a94: Pooled result SUPPRESSED (estimand-incompatible). pooled effect SUPPRESSED: the trials mix incompatible estimand classes
        docs/reviews/iv-iron-hfref-hosp/index.html: lost banner block 8c1056e4ccd044af03d9589b7fe844ae3255053da184a3118df8f04102ea0766: Declared strands (the single pool is suppressed; these are the endpoint-clean decompositions) Strands A and B measure th
        docs/reviews/iv-iron-hfref-hosp/index.html: lost banner block 922bc57e32d805488dc7cc0e69b76a126750ace0f40a98d4af5c58eae3e15e83: Snapshot: records_sha256 242ba998 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 31c8e387bf859660214caa9bf45f71bca44e80baed46a0320cd5420051ff48de: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RU
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block d6a931e9775c1ed363dafadd6f6bd03aface256ef70d9569f5bbaa21f7c0a245: Cross-family definition audit. Two independent model families (Gemini via AGY, and Fable) re-read every pooled row and c
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 61fa684e92843fbe047623661c300be695b368dab6ba62da8bcd28bbfa451800: Pooled result SUPPRESSED (estimand-incompatible). pooled effect SUPPRESSED: the trials mix incompatible estimand classes
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block f1b0d7b429050cfec3a688bdb1df0579012084709efdc927e62da0888bd6fca4: DECLARED ABSENT. no included trial reported this outcome with a percentage-corroborated count or an effect+CI in its abs
        docs/reviews/iv-iron-hfref-hosp/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block e33d3ad545e807ab7ed52a5479a3bf8255f04c8ae05e898287e51cddca0953aa: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 95985cd84fbf919935f5099fffc4c42de010543b74fc4555a113a263a177c7ec: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 19e48f45872f041e87da3e5d30365a431e76d3d07e43ea7a5ab24ab068b59b73: Overall certainty: not rateable. the primary pool mixes INCOMPATIBLE estimand classes (HAZARD_RATIO_FIRST_EVENT + INCIDE
        docs/reviews/iv-iron-hfref-hosp/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 4e655fe3ed1a86b2fbbb60e04236c8591d430c63637eab4156e3da1157a1f6ce: No checkable pooled claim (Claims checked: 0). Nothing was pooled on this page, so the canonical-claim contradiction gat
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 6d1920e6e97f6344014a5ce73e39302e8d2931487d7d0cb39c0792df68c64113: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 711dff193570d7221b8353f38c88cd4a7d9aeac2516f97b46ac0e744fe7c5615: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost banner block d133296791325516a27f5024c7c6b57db9a7aeabb5bd79cdec0dd93fb46af616: Snapshot: records_sha256 159e5415 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 51984e7bede57d9bf3873159b06be81aa191c14d5289e9eb38532fa57bca1e01: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_ER
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 91dac062739163f3174e34a42c2f5614d4b027350a5be3eef12b628a8802cb63: Cross-family definition audit. Two independent model families (Gemini via AGY, and Fable) re-read every pooled row and c
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block a16a18bef1a7af5809468fe78f126b2a3dd5d4385f5b503bf9976f62ef5f26da: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 33157425, 22346363, 20712869, 18036082, 12790159 mentio
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block cbbd6a73cc0d27b1e77534aa7ff16ad6424ee9b025379a7f32e29e17c50bbbda: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 4972766020294b0566a4fc26feccd2e0da568e0e677638429fac1ac3d4a63d6b: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 7b4225b798a5ed89e4d0e8a324f0b622166dcaac88512b73d4dfc3f114f60faf: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 6b77e526173bc21f8c36fc9bb3eeea0c9902d81540ad387fc201c38cb209a983: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 70fc239ceb3647c957e6e38e3c1da54fb0068ef51f470654f60f5d99ce6371eb: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 99736327bb6305c2a8b554c3cd07e1c1829ed74d3571b250e4547ce947ac13cb: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/metformin-pcos-ovulation/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/metformin-pcos-ovulation/index.html: lost banner block ef76770b0dd933fd73a963b6c0d2cf74b9a72b663ff9445df51dce532cc247ce: Snapshot: records_sha256 1fdb53f8 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 31c8e387bf859660214caa9bf45f71bca44e80baed46a0320cd5420051ff48de: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RU
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block dd1dead6c2560a93ff01a5324a76c288e758fc97cb2a645c790180163e821248: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 16769748 mention this outcome in the committed abstract
        docs/reviews/metformin-pcos-ovulation/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 6ee988ab9970f78e22c815d201785b6d167c938e6e699da61186de8cacfd6312: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 16264cc27213b813e1aeafd53e66948603ccb01474997893fe6c53f1a37a022e: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 72db58add18abd2662f0e8b4798ff2ee589a750ad3328d91563734f69747b695: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 8e8301343df98222cfe40b761ee7ec58afc1206c5534fee72f5d709f163834e3: Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a 
        docs/reviews/metformin-pcos-ovulation/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block f0bcaed7a72b0d0bde2e67431d27c986bf15982f914d06a3ba0c5b4c002b3d37: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block cc09531f8b7015ed1c6ba7ded759124aa5e808319e90b729f53d395df2bf0706: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost banner block cb663900acaec0589ce8453f2f0fab07a582c6aacb8ccbdf4e5ed2be47c4eebb: Snapshot: records_sha256 dfacf3bf ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block f78c512047bc0437de0926a52df7805b797214433f9feb56344ab2c29eb00219: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block b0828b821327892706ca39221ca0550a0b0043e8506a2868c6223cd5999b8503: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block e265d763c956988c33d33de18e544f09e182e98528af44246fb987cc65a5c2dc: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block 496a7c240788f4917387ccc389f17c25551a2842b80391e40c0a7353dfcd57b3: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block baea49ebb9e814194adc1b2736d663afc71255af1fa6cccb8d6d0d1589f72307: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 63008764ab6625862648593588cd46cd1a0f37cced68bbd89f94a061833034c5: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 07c799f3a31060c1ac34289a2faecbd80027bbc1e6565c5e8a3edd2945a0659e: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/omega3-cardiovascular-events/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/omega3-cardiovascular-events/index.html: lost banner block c1c5b55299c91132cf6c146defaa2d13962b48c20880d790b36bc8c4360d0823: Snapshot: records_sha256 f40d3169 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 43a969feab22c9736ff48136e6ffe085d804b5301181976258b1bd1b609cf59f: Cross-family definition audit. Two independent model families (Gemini via AGY, and Fable) re-read every pooled row and c
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 7d2411912d3b55496a33fe9a0905f6480d10aec4d43fb37141f183cb736add53: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 30415637, 30415628, 30146932 mention this outcome in th
        docs/reviews/omega3-cardiovascular-events/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 2e52a207b30781148639e2ca6263bbfc5ea5d11d8d7ca9655303821d3b52ddfe: Unit-of-analysis/design caveat (disclosed, not silently adjusted). 3 pooled trial(s) are individual-randomized factorial
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 4bfa9e524f3089c4c5cd06a844cdae1489c43898c25d569c14d17005e0dc3af1: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block fc29991097b4dc217d3f023445f76cbffa5c22b6bf494127a23f390975d8369c: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 6398132dae3a1a7108a74c25d54c80f3a739512df47772bc155502751c36b41d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block c77ef0e830e5d74310099c90ef651caad9e1ee2aff8dd7d8de391e991afc6962: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/omega3-cardiovascular-events/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/pcsk9-mace/index.html: lost absent block 71e4002ec9f8906c097fbff9ca975a30fafe8656bd556978858a78671ec131b5: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/pcsk9-mace/index.html: lost absent block 07c799f3a31060c1ac34289a2faecbd80027bbc1e6565c5e8a3edd2945a0659e: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/pcsk9-mace/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/pcsk9-mace/index.html: lost banner block c05e20e7a9b7ea8d4b39012a216008d917651e6080af654d0d819c92e96864a8: Snapshot: records_sha256 b1ef6c11 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/pcsk9-mace/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/pcsk9-mace/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/pcsk9-mace/index.html: lost absent block a12c39c7a06b5ad8d7283870c3833d72d4d7ae78c707578d9fcd31f19e79a09c: Cross-family definition audit. Two independent model families (Gemini via AGY, and Fable) re-read every pooled row and c
        docs/reviews/pcsk9-mace/index.html: lost absent block 61163e4e61d3b0c8976d05a3c2402af897356d709003c3ea8a7b34991e38813e: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 28304224, 30403574 mention this outcome in the committe
        docs/reviews/pcsk9-mace/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/pcsk9-mace/index.html: lost absent block d045eb82cc2e52801ad1f457995308936bee1d9e633f4b9709cdc1787504729b: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/pcsk9-mace/index.html: lost absent block cdae34e1a6433db309ca24da20a1250284f651795828d207d569bccb725d3390: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/pcsk9-mace/index.html: lost absent block 7b2d1674478f8315cbef7e6285dad3f45e0a93bc14acce314da847954a6bcbb9: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/pcsk9-mace/index.html: lost absent block 9fb655c4cc64424164f8dee8b10bed1f52ddf44da88fa836084f5ea54e5ed034: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/pcsk9-mace/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/pcsk9-mace/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block f78020e01c6f36e1b905d8e6dd6e8e0872ca85844ebfba0d33e1ca0fef0c5318: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 0988c08ad2471bb591e7066f422bb5aefd81c6b090f38af9ada72d821425a209: HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH We retract any claim of a registr
        docs/reviews/probiotics-aad-prevention/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/probiotics-aad-prevention/index.html: lost banner block 6f6f96af69410d2951ffc9c54eb72005a31d84db761045cdf01c8b315b1f9e51: Snapshot: records_sha256 a832babc ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block c05a643044807856d475f2cbb9760c9bec2c21afb0d8bc0b755ef3e4ed55acef: HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH We retract any claim of a registr
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 09bdb49b28d751b80a19a5156efc48af5a3d03b86e50c38f917ab02f3c739977: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 7e35d3e843f8b62b19b772f54383c602b2549ed9f62ed23a3f93af8526eb455b: Cross-family definition audit. Two independent model families (Gemini via AGY, and Fable) re-read every pooled row and c
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 34a8823b0bad217626b851828dc856654dbbae42bf5964fcb712262cb30490a3: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 42608299, 41699149, 40716758, 40548185, 40488914, 39935
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 6ecb01b65a6288b3037ae6e2f1019cda43b2ae320ca660365fa61d46a93210f5: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 40548185, 26973849, 23932219, 19138244 mention this out
        docs/reviews/probiotics-aad-prevention/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block fe5a5a96506acf422872e59e045b9257d911a403ba1f6876ea2e418cab3cc71d: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 4b252317efdebe6963ef01a013fe5eb43646c12497849c9063636b005ef2cfc9: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 3690b1ad41faf51a261928ebca1cf523e09cb400f4cc759e307d156697580e8b: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 99becb418875e3d7ddd6dbda49c73006d7252e22eef6dc35199ff53c62376365: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/probiotics-aad-prevention/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 5c5f21c12313b29cf69cddc6aeeefa14ec2e1f100e4e194b3fd9b29df91f90c7: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 19b10db5b90d9f701b21c668636f146972a47ee85175593d9ad8d0afdd2fb1d2: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost banner block c9570bd907f9397433ca1c5632a5f1da74fb5e63c24a3c44c2ae34995363a023: Snapshot: records_sha256 58f1709c ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 31c8e387bf859660214caa9bf45f71bca44e80baed46a0320cd5420051ff48de: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RU
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block bff5f3115693b0718df1df746a4fe566271c472ab11819b1fc25688a085945b4: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 7f05f40e226c430ba2d04aeaa23acc772e6f906aa65d61f5f2e75d2e9450aae4: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 072a75e8e15be99b57cc84e267fcc385e25589124b7fc7b60d3203a4a6083bbf: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 09ed94fe6e8360cfecf6ad69db79fcb7ca77b505565936768935dc6b62adcb67: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 71e4002ec9f8906c097fbff9ca975a30fafe8656bd556978858a78671ec131b5: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 19b10db5b90d9f701b21c668636f146972a47ee85175593d9ad8d0afdd2fb1d2: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/semaglutide-obesity-mace/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/semaglutide-obesity-mace/index.html: lost banner block c277dc7a9439b0e4d0bd6b1430ab5c6dfa3209e7bf1bc676437ba5728f0a9c6e: Snapshot: records_sha256 ac910156 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block f1b0d7b429050cfec3a688bdb1df0579012084709efdc927e62da0888bd6fca4: DECLARED ABSENT. no included trial reported this outcome with a percentage-corroborated count or an effect+CI in its abs
        docs/reviews/semaglutide-obesity-mace/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 36f1272cbafe5ab6d098d3764690890c7867b73c4376e443fc505ff44cfb3af2: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 08680a96bfa69c446138ef1efe16db7a39a864723beb64f70be4bdb32978fb19: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 26ab09f2b6cbce2e1e158fb630fa57a0c0186f3db7491523f7fa2adf79d4fcbc: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 3fe49f850a635eb2189b79baa4f679f142e19bce8eacd03224e40f2a3feee68c: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/semaglutide-obesity-mace/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 27fa861143525ed8ef7e438c823698c9ac2cc660f10eb72e44c3bc2ac46edecb: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 52c2424e174f4adf5d84862d5486a45cded25f4158f21bd3fab93962a7cc5bc0: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/semaglutide-obesity-weight/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/semaglutide-obesity-weight/index.html: lost banner block 32d0ad299559b616aeb37b8f28c79e07e42eec3c0e395336073c09c51961c98c: Snapshot: records_sha256 195d48c1 ; retrieved_utc 2026-09-12; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 51984e7bede57d9bf3873159b06be81aa191c14d5289e9eb38532fa57bca1e01: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_ER
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 9d050184453a3cd6148057e7e5201cfbe7dbd3fa50a333fc79aea2d2fb1bdda8: Cross-family definition audit. Two independent model families (Gemini via AGY, and Fable) re-read every pooled row and c
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 7d054e36a29c628d0807fc18fe5eb817c1df0f3006068c0564e198eadb2d52d0: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 42575111, 42070571, 40825340, 40629530, 40069849, 33625
        docs/reviews/semaglutide-obesity-weight/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block f8a5707ab64fbc8f436f190921d8e79e893e813b8ba9921fb19fcc5f136c4238: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 0b94e470e01c548721077e31502ffec1a5fe3b47eedc2f8626b46dfe78d46835: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 45446b368a9c9346efd1ba26dd96de014ee501bb6caa900c82360c75634ad0af: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 0f8ad79d9c66fae246cde2257ffe2107813ab8e139bc575a8052b607ce492c12: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/semaglutide-obesity-weight/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block 5c85cc5c5af3c0e51e6035de15abfa2dad8f15a92c13ff64b9ddb331c977dff4: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block 4a266aa0f9d335743a4f9107c0fc651306d41303071fe7cabdf23eb83387b40e: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/sglt2-ckd-progression/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/sglt2-ckd-progression/index.html: lost banner block 24e1177446fd6c46b8db81088cbbf589701abd7ebab1e6527117586423b11213: Snapshot: records_sha256 4a7478c2 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block f78c512047bc0437de0926a52df7805b797214433f9feb56344ab2c29eb00219: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block d8a1df57fa5e78b1bf714be035e5cc030366f592f9fabc4b4e2120a9afda2492: Cross-family definition audit. Two independent model families (Gemini via AGY, and Fable) re-read every pooled row and c
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block 7f784e67f837798409405c149567f7c89159a67591406edeadbd6edec156d5f2: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 30990260 mention this outcome in the committed abstract
        docs/reviews/sglt2-ckd-progression/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block 40092b16403db4c15aa693020e60b837701335ea440baef9f774b981fd620cd1: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block 0320760e6bcdb6581320126e7dee63b5506c7a8c25303f9f617e514acc4f2ea3: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block eb69309ac2fbd67743b0ded82a6daaa5e7316e38145aaa3f3a29d30223c4c4fc: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block db4655aa165a114b729706357dc701b5b8bcd0a7e9d9d21aa8ff9d9cd969266b: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/sglt2-ckd-progression/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block 66bb3035fd6170dc2e318b20831e6ce39ffdb0426200b93f99873f5f77d0d56f: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block 4a266aa0f9d335743a4f9107c0fc651306d41303071fe7cabdf23eb83387b40e: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost banner block c2e448a7a5ee87b14750d6172d418143869d71d8d2f7568e059605593ec9de12: Snapshot: records_sha256 056f66b4 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block f78c512047bc0437de0926a52df7805b797214433f9feb56344ab2c29eb00219: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block 86e0b4488e02f0870bde261bbecd48a6806da239ba9126453b2828279d0295db: Cross-family definition audit. Two independent model families (Gemini via AGY, and Fable) re-read every pooled row and c
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block c839630e932144f699429abbe2e861a0bd987344d8372c0a5b2ce106b59be677: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 31535829 mention this outcome in the committed abstract
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block 2565ad7a1e882c7ccf2a45c20448223b484335ea10a53179b9a43dd950dded83: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block 1e64c354919293b51d17319223237128f234c225cc3762b3b91f859a4f21a893: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block 965250ce4cfd0308b296c784661c49b482f248ddcf01136bde7f1c17d3e77525: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block be6ab27c20f82912a45e9cbf09be8802e97350ee49be185e8851e97a2440fe15: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block d4a66e208cfb54fbe42b8454092b39b1f045d6ee3dbdba80489d55540ec70baa: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block 4a266aa0f9d335743a4f9107c0fc651306d41303071fe7cabdf23eb83387b40e: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost banner block b4d94a4d81dddc0e854ad5f61d850d781bf6f664a87fa4c217d60927dc72e105: Snapshot: records_sha256 ba5c49e2 ; retrieved_utc 2026-09-12; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block 3a81c264385ba5a6575ae6d74cf249ed9936629b836206359bafa3048a74c7a5: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_ER
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block 1dbb0dc87beac85c77ac53fc9f52406d3eddd62cb4ccfc74ca034f7b0ed71e21: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block bc8f2f2191b9b07735e8a5c8399a6fa9d72f51df88021e62676d49dc665aea26: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block 8d61bf47c06063dec14f2d4656e683b5c5445128098b53a4545d6f790bf52db7: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block a88aa38b82f42e250de2a7b237f6026ce62106c4c5a06c14521eef07aba1cf69: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 8ec8dd8d80d12ea6c1d7973c7de96834f4a6b22733a303e9511e60a838a8f12b: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 797a2807c925510e5aa3f6616d9fe6a8e04614b27e7084eca01dc8658ebce42a: Identifier scope failure. the identifier names spironolactone but the pool is class-level (10471456=spironolactone, 2107
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 4a266aa0f9d335743a4f9107c0fc651306d41303071fe7cabdf23eb83387b40e: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/spironolactone-hfref-mortality/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/spironolactone-hfref-mortality/index.html: lost banner block ed7a148966f33ebbf44e717e74b3bb5cba442fd27698ceb915ae71b46dba2971: Snapshot: records_sha256 8352ca95 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block f78c512047bc0437de0926a52df7805b797214433f9feb56344ab2c29eb00219: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block ec9fd7c4d2ac80fd976612d3b03f8ffdcb61d1f46cb8375d2f3bd6c7cff3ae4b: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 10471456, 21073363, 28824029 mention this outcome in th
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 8124911ae094726bb85f9fe8d1f2efb2a69ffccc1951b6caa3e030a638175182: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 10471456 mention this outcome in the committed abstract
        docs/reviews/spironolactone-hfref-mortality/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 6fb533d581f68da392afcc89bcaf1ec0b6f1ebdcb59a421d831aebae1c466f92: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 1557cc75bdd3c3e88e8efdcdfc7172ccce312164d8db9240c5a5240b75bdf0e5: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 4bfc6a1f39b6524082d059f894fe1d3440e3725de7a19ed581edc014ad0c276d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block a20410a071d279f8c5f0d4f2524c309a86be39ca53864329abebb24238d6d882: Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a 
        docs/reviews/spironolactone-hfref-mortality/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 6970392f417c379d24f62694c5f02bf0a46b8f0c5e4f152e674058c9b44470cd: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 99736327bb6305c2a8b554c3cd07e1c1829ed74d3571b250e4547ce947ac13cb: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/statins-primary-prevention-elderly/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/statins-primary-prevention-elderly/index.html: lost banner block dff1b4824f648a4dda451026e0025d13c2be7fdb2712006ca3ebead3d3f35927: Snapshot: records_sha256 7170920d ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 13416bf19a399d4808be161597f2aefc10c3cc502897cd2dad3e02aca1834fcb: Cross-family definition audit. Two independent model families (Gemini via AGY, and Fable) re-read every pooled row and c
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 7c17773d7ee68a33cf2378a420020f88a59523b40af38f32bd6b4e6cda18f6d1: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 42670961 mention this outcome in the committed abstract
        docs/reviews/statins-primary-prevention-elderly/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block c04bac3cfdc3fac6d7b3272a1dd7a2929d8447bc1a0852c2a38da02eeba7dd5b: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 25845d7b8f6c2c99a73579fec6eb96610e926af016e6fb5374d54b0bafa09bc5: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 1b61824a331cba7ed7af28c78c2e1e32f08a54957ed61b788a77d0ea6495dbb8: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block e49ac2b8042d3c0330eac88d67e2accc7128131e64a79ea69ad81323e3b054d1: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/statins-primary-prevention-elderly/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block 041c48be57cb207dabbd97a2e99c20271f2bd7131ff9e4c0c26b5d432b5dfabe: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block cc09531f8b7015ed1c6ba7ded759124aa5e808319e90b729f53d395df2bf0706: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost banner block 831ac718dba9f4b8248b7d0fe1f68b0955dc8380906cf4beb71a6eb2827a7da9: Snapshot: records_sha256 a6e860ba ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block f78c512047bc0437de0926a52df7805b797214433f9feb56344ab2c29eb00219: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block f1b0d7b429050cfec3a688bdb1df0579012084709efdc927e62da0888bd6fca4: DECLARED ABSENT. no included trial reported this outcome with a percentage-corroborated count or an effect+CI in its abs
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block 1df51e83141f9980943f1060bc10a23ed3c4fe9cc765c409f42475d6a7e50a63: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block 4b332ea83fea8621ad8f08b843ffcfb5a6456a1539827fc5f4700d9e4ea2df4f: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block 35299e230bcbee6aee55bf7259d56deae3c7966fbcf86977f1661a0a378cc2a9: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block c3fd688cd9c199c13ff366e0812df59617cd1cd51a0c62f409f3ee3598b7f98e: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block d7208f15be1e5d4a6ca831e2e4a8fbfc1cfb97f90211508f40bb1e7803ff4c4e: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block 99736327bb6305c2a8b554c3cd07e1c1829ed74d3571b250e4547ce947ac13cb: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost banner block bfb757f80a5cfe9a8887c7540779e13369f2d30064eb08389752ec46201c6afc: Snapshot: records_sha256 a6b727dd ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block f1b0d7b429050cfec3a688bdb1df0579012084709efdc927e62da0888bd6fca4: DECLARED ABSENT. no included trial reported this outcome with a percentage-corroborated count or an effect+CI in its abs
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block bd14f8a89b0544ae6a4315d2ae4bcbae9a47bcb4256ae8696a27d2332454058b: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block 20c3e04e68c4397a8e7994d28ed9034c4a2360a8397263fa23fc49d9c04c35f2: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block f16e90d7d6310cdb9d636170fa9b5160948b9ed4d0d5fc380801531bb72dc82d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block f5fafd4d2f6b2c4d7c6cd44bed380029eed96d2f06707b0b8321289ed32b242c: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block d4c06b5750a454a2b86e6ba121013a5a865b5838b8984c3948a3051dd2deceb2: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block 52c2424e174f4adf5d84862d5486a45cded25f4158f21bd3fab93962a7cc5bc0: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/tranexamic-acid-pph/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/tranexamic-acid-pph/index.html: lost banner block 65e66ffb5fccf2333acbe2451d28a7cb4da497e3f13c3a1d38e564a90ba9d69b: Snapshot: records_sha256 940022e2 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block 2fa2d4dace9c41b26842a79ecfc052d4b3989c4f92b563556bcb23cf18345d33: Cross-family definition audit. Two independent model families (Gemini via AGY, and Fable) re-read every pooled row and c
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block f425710ed75286f7ad4624bb8b617912fb9609feda3e5da59b90fa0e879c3f91: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 32143721, 28456509 mention this outcome in the committe
        docs/reviews/tranexamic-acid-pph/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block 715b9f50c00c6b3491cb174de95bd3713812364b2d43a2da906264dbac4e63a9: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block d161053ef44d71264c34d6d71613938e2fd0828724e11a79add0d67ab150174f: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block 295a768c15eeb1c46a8cda92832439fa2eb6fb6b500a8f11b2b737f4f9b6bc0d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block ac7d9964082a37db27b76419258d0d324859f0857bdc0357035d21ff2c999a37: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/tranexamic-acid-pph/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block c8f3185f15c1e19bf4bfa066b0334e6bea58d87578c7685affd49527119b4663: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block e53e6594078369028e17c6908139e0434ec8ba527517a2b168a075e275af46a9: Unit-of-analysis caveat (disclosed, not adjusted). 3 pooled trial(s) use a cluster-randomized or cluster-period (policy)
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 3056ab225b9e210a00936fdcbfa361f8e934c4a3eae8501e77e4dce9dedb702c: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block b8c4b60bd942a25aaaafc43a4cc63dc78c3e705961e0fbf0a49155bf75bfe08b: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 960be40ef77ff4a78df7696b5504db234eb1f8d843aa2fd6152fed50e4fd2b0d: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/colchicine-postop-af/index.html: lost absent block f41f44dbb235d7e3ba6cd19e39d95764a53c743f412bd2c8d97e717b24be0d8d: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block db6718c7fc98f15b7860eaa39addaaf5b504627f938775d838642d28018b0dbf: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 006dfed6a52c884adfa0d494c058b30a9f00e399b9ccbdfaea15ce594896f7b6: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block e0d0e516ac70ae587b84f97518ad9bae02ad83ac0e75aeefcd835dba72632573: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block cddb1803ec14752dd0493121fd4b4e207d85fcb8619befe47a83d24f995c9316: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RU
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block f636a22b7a91901bf2f4ede7427461e8d0d33a486535b2fc21538f753ba2f624: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 3a81c264385ba5a6575ae6d74cf249ed9936629b836206359bafa3048a74c7a5: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_ER
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 8ceaf15588f25756c9d9c8bc12c198d0cb50b4247c169f8a5e67014d6a631dab: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 74ef9f624c5845659feef24079fb873482531098515959d4a9a1c20473b27570: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 4429a1130a26e3d890956b1049a1307ada42cc13bb0211ce7d39890df1960a18: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block cddb1803ec14752dd0493121fd4b4e207d85fcb8619befe47a83d24f995c9316: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RU
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 3a81c264385ba5a6575ae6d74cf249ed9936629b836206359bafa3048a74c7a5: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_ER
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block b2070d2574fe0876cc517b1de106056ca6efb46bb95750887f632b34a2154ccb: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block cddb1803ec14752dd0493121fd4b4e207d85fcb8619befe47a83d24f995c9316: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RU
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block bc9d516edca0700eb472fee2cf9030ae8a03fa19908bb5394750757912d6745e: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block f654ce73d6605a5ed5802fa1c03a703e47110d3e83e41c87cc5bac4e01b06fdb: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 9458afdf56d6a319889db473ad3764ace2419c1f8421160b39c75ed881b3e313: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 5fcfa0cc7dab8f958eee34b36da3422676a0eca3d6c4b0ee945e8d72b965e229: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block cddb1803ec14752dd0493121fd4b4e207d85fcb8619befe47a83d24f995c9316: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RU
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 3a81c264385ba5a6575ae6d74cf249ed9936629b836206359bafa3048a74c7a5: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_ER
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 47f25de516e8331c1685db66a4ac6a6bf5c69c58da28055a70125e5026b92486: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block b4ea3cbda3f23aa8f384a090de5c3193b13727382d37ca785147deaf6fb97c2d: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block f7e568ab1db57539ab2f705d224dda0ddc35edad6073035581c7d957b83b0600: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block cba2d0f5429c6ceb02ab0a28fafca924ff04660c8096ac5768f2113627a7f0a5: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block 0ccca9c7d9390142204b23e528f6378d22473fab6debab6dbceebe98fa1c2efb: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
  [             PASS] gate scorecard (every gate accounted for)  (3s)
        TARGET verify_all.limb_gate_scorecard: head=3f8add72d50b84eae2000625387e3194137a06ea base=none tree=dirty:735 files files=3 registry/gate_scorecard.json docs/gate_scorecard.json harness/gate_scorecard.py
        TARGET gate_scorecard: head=3f8add72d50b84eae2000625387e3194137a06ea base=none tree=dirty:735 files files=6 registry/gate_scorecard.json docs/gate_scorecard.json scripts/verify_all.py ...
  [             PASS] gate gaps table (sealed what-it-would-not-stop rows)  (10s)
VERIFY-ALL: REFUSED -- 4 of 11 limbs not PASS. Fix the harness, never the gate.
```

Final GLP1 census record (MEASURED):

```json
[
  {
    "slug": "glp1-ra-mace-t2d",
    "fact_summary": {
      "FACT": 9,
      "UNVERIFIED_FACT": 0,
      "total": 9,
      "fact_precision": {
        "instant": 1,
        "date": 8,
        "unverified": 0
      }
    },
    "precision_surface_violations": [],
    "served": {
      "rendered_units": 2975,
      "with_object": 2975,
      "with_object_by_class": {
        "INTERPRETATION": 33,
        "TRANSFORMATION": 2481,
        "JUDGEMENT": 435,
        "FACT": 26
      },
      "structural_units": [
        {
          "unit_id": "unit-0023",
          "text": "Trial",
          "context": "html/body/main/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0024",
          "text": "Recorded membership decision",
          "context": "html/body/main/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0045",
          "text": "Trial",
          "context": "html/body/main/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0046",
          "text": "Recorded membership decision",
          "context": "html/body/main/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0123",
          "text": "sha",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0125",
          "text": "committed utc",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0127",
          "text": "method declared",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0129",
          "text": "eligibility",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0132",
          "text": "databases",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0134",
          "text": "cache ref",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0136",
          "text": "run utc",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0141",
          "text": "Kind",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0142",
          "text": "Query",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0143",
          "text": "Run date",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0144",
          "text": "State",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0145",
          "text": "hits -> fetched -> retained",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0146",
          "text": "Cap",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0147",
          "text": "Discovery-capable",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0178",
          "text": "Verbatim query",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0179",
          "text": "Kind",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0180",
          "text": "Features fired",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0207",
          "text": "Family ID",
          "context": "html/body/main/section/section/div/table/thead/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0208",
          "text": "Acronym",
          "context": "html/body/main/section/section/div/table/thead/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0209",
          "text": "Reports by role",
          "context": "html/body/main/section/section/div/table/thead/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0210",
          "text": "Arms",
          "context": "html/body/main/section/section/div/table/thead/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0211",
          "text": "Contrasts",
          "context": "html/body/main/section/section/div/table/thead/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0212",
          "text": "Eligibility",
          "context": "html/body/main/section/section/div/table/thead/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0213",
          "text": "Lifecycle",
          "context": "html/body/main/section/section/div/table/thead/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0214",
          "text": "Per-outcome status",
          "context": "html/body/main/section/section/div/table/thead/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2123",
          "text": "Id",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2124",
          "text": "Id type",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2125",
          "text": "Decision",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2126",
          "text": "Rule id",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2127",
          "text": "Found by",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2128",
          "text": "Trial family id",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2129",
          "text": "Publication role",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2130",
          "text": "Completeness state",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2131",
          "text": "Reason",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2132",
          "text": "Span",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2267",
          "text": "Trial",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2268",
          "text": "Outcome",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2269",
          "text": "Recorded assessment",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2340",
          "text": "Trial",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2341",
          "text": "Id",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2342",
          "text": "Input",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2343",
          "text": "Source",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2428",
          "text": "Axis",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2429",
          "text": "PMID 31185157",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2430",
          "text": "PMID 27633186",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2431",
          "text": "PMID 27295427",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2432",
          "text": "PMID 34215025",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2433",
          "text": "PMID 31189511",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2434",
          "text": "PMID 30291013",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2435",
          "text": "PMID 28910237",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2436",
          "text": "PMID 26630143",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2437",
          "text": "PMID 40162642",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2438",
          "text": "PMID 38785209",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2439",
          "text": "population",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2450",
          "text": "randomised_contrast",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2461",
          "text": "analysis_set",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2472",
          "text": "endpoint_components",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2483",
          "text": "first_or_recurrent",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2494",
          "text": "time_origin",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2505",
          "text": "follow_up",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2516",
          "text": "censoring",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2527",
          "text": "effect_measure",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2538",
          "text": "adjustment",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2549",
          "text": "estimator",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2560",
          "text": "report",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2583",
          "text": "Reporting trial",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2584",
          "text": "Extraction state / refusal reason",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2585",
          "text": "Located span",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2586",
          "text": "Source-ladder obligations",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2623",
          "text": "Trial",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2624",
          "text": "Id",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2625",
          "text": "Input",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2626",
          "text": "Source",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2657",
          "text": "Reporting trial",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2658",
          "text": "Extraction state / refusal reason",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2659",
          "text": "Located span",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2660",
          "text": "Source-ladder obligations",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2689",
          "text": "Trial",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2690",
          "text": "Id",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2691",
          "text": "Input",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2692",
          "text": "Source",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2734",
          "text": "Pool / strand",
          "context": "html/body/main/section/article/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2735",
          "text": "Shared",
          "context": "html/body/main/section/article/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2736",
          "text": "Harness-only",
          "context": "html/body/main/section/article/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2737",
          "text": "Comparator-only",
          "context": "html/body/main/section/article/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2738",
          "text": "Jaccard",
          "context": "html/body/main/section/article/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2739",
          "text": "Endpoint-compatible overlap",
          "context": "html/body/main/section/article/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2740",
          "text": "Endpoint unknown",
          "context": "html/body/main/section/article/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2784",
          "text": "name",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2786",
          "text": "year",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2788",
          "text": "journal",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2790",
          "text": "pmid",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2792",
          "text": "doi",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2794",
          "text": "open access",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2796",
          "text": "url",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2809",
          "text": "Trial",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2810",
          "text": "Overall",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2811",
          "text": "Randomisation",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2812",
          "text": "Deviations/blinding",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2813",
          "text": "Missing outcome data",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2814",
          "text": "Outcome measurement",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2815",
          "text": "Selective reporting",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2931",
          "text": "Source estimate",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2951",
          "text": "Reporting item",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2952",
          "text": "Field presence rule",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2953",
          "text": "5 Eligibility criteria",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2955",
          "text": "6 Information sources and dates",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2957",
          "text": "7 Search strategy",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2959",
          "text": "8 Selection process",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2961",
          "text": "9 Data collection",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2963",
          "text": "15 Certainty assessment",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2965",
          "text": "16a Selection flow",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2967",
          "text": "16b Exclusions",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2969",
          "text": "24 Registration and protocol",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2972",
          "text": "failures",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2974",
          "text": "preregistration",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2976",
          "text": "protocol sha",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2978",
          "text": "review sha256",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2980",
          "text": "from cache",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2991",
          "text": "Specification",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2992",
          "text": "Choice",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2993",
          "text": "Result (tau2 beside I2)",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-3046",
          "text": "Single change",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-3047",
          "text": "Result",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-3088",
          "text": "Replay step",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-3089",
          "text": "Attribution",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-3090",
          "text": "Result",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-3091",
          "text": "Delta log effect (null = unidentified)",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        }
      ],
      "structural_count": 132,
      "visible_units_before_structural_rules": 3107,
      "unit_contract": "conservative visible prose/table text runs; not an exact linguistic sentence count",
      "violation_counts": {},
      "violation_examples": [],
      "examples_of_violations": 0
    },
    "fresh_renderer": {
      "rendered_units": 2975,
      "with_object": 2975,
      "with_object_by_class": {
        "INTERPRETATION": 33,
        "TRANSFORMATION": 2481,
        "JUDGEMENT": 435,
        "FACT": 26
      },
      "structural_units": [
        {
          "unit_id": "unit-0023",
          "text": "Trial",
          "context": "html/body/main/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0024",
          "text": "Recorded membership decision",
          "context": "html/body/main/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0045",
          "text": "Trial",
          "context": "html/body/main/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0046",
          "text": "Recorded membership decision",
          "context": "html/body/main/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0123",
          "text": "sha",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0125",
          "text": "committed utc",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0127",
          "text": "method declared",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0129",
          "text": "eligibility",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0132",
          "text": "databases",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0134",
          "text": "cache ref",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0136",
          "text": "run utc",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0141",
          "text": "Kind",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0142",
          "text": "Query",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0143",
          "text": "Run date",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0144",
          "text": "State",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0145",
          "text": "hits -> fetched -> retained",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0146",
          "text": "Cap",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0147",
          "text": "Discovery-capable",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0178",
          "text": "Verbatim query",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0179",
          "text": "Kind",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0180",
          "text": "Features fired",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0207",
          "text": "Family ID",
          "context": "html/body/main/section/section/div/table/thead/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0208",
          "text": "Acronym",
          "context": "html/body/main/section/section/div/table/thead/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0209",
          "text": "Reports by role",
          "context": "html/body/main/section/section/div/table/thead/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0210",
          "text": "Arms",
          "context": "html/body/main/section/section/div/table/thead/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0211",
          "text": "Contrasts",
          "context": "html/body/main/section/section/div/table/thead/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0212",
          "text": "Eligibility",
          "context": "html/body/main/section/section/div/table/thead/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0213",
          "text": "Lifecycle",
          "context": "html/body/main/section/section/div/table/thead/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-0214",
          "text": "Per-outcome status",
          "context": "html/body/main/section/section/div/table/thead/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2123",
          "text": "Id",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2124",
          "text": "Id type",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2125",
          "text": "Decision",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2126",
          "text": "Rule id",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2127",
          "text": "Found by",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2128",
          "text": "Trial family id",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2129",
          "text": "Publication role",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2130",
          "text": "Completeness state",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2131",
          "text": "Reason",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2132",
          "text": "Span",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2267",
          "text": "Trial",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2268",
          "text": "Outcome",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2269",
          "text": "Recorded assessment",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2340",
          "text": "Trial",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2341",
          "text": "Id",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2342",
          "text": "Input",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2343",
          "text": "Source",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2428",
          "text": "Axis",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2429",
          "text": "PMID 31185157",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2430",
          "text": "PMID 27633186",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2431",
          "text": "PMID 27295427",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2432",
          "text": "PMID 34215025",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2433",
          "text": "PMID 31189511",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2434",
          "text": "PMID 30291013",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2435",
          "text": "PMID 28910237",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2436",
          "text": "PMID 26630143",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2437",
          "text": "PMID 40162642",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2438",
          "text": "PMID 38785209",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2439",
          "text": "population",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2450",
          "text": "randomised_contrast",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2461",
          "text": "analysis_set",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2472",
          "text": "endpoint_components",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2483",
          "text": "first_or_recurrent",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2494",
          "text": "time_origin",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2505",
          "text": "follow_up",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2516",
          "text": "censoring",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2527",
          "text": "effect_measure",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2538",
          "text": "adjustment",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2549",
          "text": "estimator",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2560",
          "text": "report",
          "context": "html/body/main/section/div/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2583",
          "text": "Reporting trial",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2584",
          "text": "Extraction state / refusal reason",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2585",
          "text": "Located span",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2586",
          "text": "Source-ladder obligations",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2623",
          "text": "Trial",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2624",
          "text": "Id",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2625",
          "text": "Input",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2626",
          "text": "Source",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2657",
          "text": "Reporting trial",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2658",
          "text": "Extraction state / refusal reason",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2659",
          "text": "Located span",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2660",
          "text": "Source-ladder obligations",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2689",
          "text": "Trial",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2690",
          "text": "Id",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2691",
          "text": "Input",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2692",
          "text": "Source",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2734",
          "text": "Pool / strand",
          "context": "html/body/main/section/article/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2735",
          "text": "Shared",
          "context": "html/body/main/section/article/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2736",
          "text": "Harness-only",
          "context": "html/body/main/section/article/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2737",
          "text": "Comparator-only",
          "context": "html/body/main/section/article/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2738",
          "text": "Jaccard",
          "context": "html/body/main/section/article/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2739",
          "text": "Endpoint-compatible overlap",
          "context": "html/body/main/section/article/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2740",
          "text": "Endpoint unknown",
          "context": "html/body/main/section/article/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2784",
          "text": "name",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2786",
          "text": "year",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2788",
          "text": "journal",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2790",
          "text": "pmid",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2792",
          "text": "doi",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2794",
          "text": "open access",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2796",
          "text": "url",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2809",
          "text": "Trial",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2810",
          "text": "Overall",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2811",
          "text": "Randomisation",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2812",
          "text": "Deviations/blinding",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2813",
          "text": "Missing outcome data",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2814",
          "text": "Outcome measurement",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2815",
          "text": "Selective reporting",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2931",
          "text": "Source estimate",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2951",
          "text": "Reporting item",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2952",
          "text": "Field presence rule",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2953",
          "text": "5 Eligibility criteria",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2955",
          "text": "6 Information sources and dates",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2957",
          "text": "7 Search strategy",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2959",
          "text": "8 Selection process",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2961",
          "text": "9 Data collection",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2963",
          "text": "15 Certainty assessment",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2965",
          "text": "16a Selection flow",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2967",
          "text": "16b Exclusions",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2969",
          "text": "24 Registration and protocol",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2972",
          "text": "failures",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2974",
          "text": "preregistration",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2976",
          "text": "protocol sha",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2978",
          "text": "review sha256",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2980",
          "text": "from cache",
          "context": "html/body/main/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2991",
          "text": "Specification",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2992",
          "text": "Choice",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-2993",
          "text": "Result (tau2 beside I2)",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-3046",
          "text": "Single change",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-3047",
          "text": "Result",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-3088",
          "text": "Replay step",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-3089",
          "text": "Attribution",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-3090",
          "text": "Result",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        },
        {
          "unit_id": "unit-3091",
          "text": "Delta log effect (null = unidentified)",
          "context": "html/body/main/div/section/table/tr/th",
          "rule": "short-semantic-table-header"
        }
      ],
      "structural_count": 132,
      "visible_units_before_structural_rules": 3107,
      "unit_contract": "conservative visible prose/table text runs; not an exact linguistic sentence count",
      "violation_counts": {},
      "violation_examples": [],
      "examples_of_violations": 0
    },
    "propositions_by_class": {
      "FACT": 27,
      "TRANSFORMATION": 2679,
      "JUDGEMENT": 388,
      "INTERPRETATION": 33
    },
    "contradictions_caught": 0,
    "of_propositions": 3127,
    "contradictions_by_class": {},
    "contradiction_scope": "GRADE arithmetic over the migrated typed registry; legacy predicates reported separately; coverage is not universal",
    "contradictions": [],
    "legacy_predicate_violations": [],
    "typed_object_violations": [],
    "existing_proposition_audit": {
      "checked": true,
      "scope_counts": {
        "publication_bias_state": 1,
        "declared_equals_enforced": 1,
        "byte_reproducible": 1,
        "pooled_count": 1,
        "rated_count": 1,
        "retracted_count": 1,
        "search_found": 0,
        "state_collapsed": 0
      },
      "scope": {
        "scope_counts": {
          "publication_bias_state": 1,
          "declared_equals_enforced": 1,
          "byte_reproducible": 1,
          "pooled_count": 1,
          "rated_count": 1,
          "retracted_count": 1,
          "search_found": 0,
          "state_collapsed": 0
        },
        "not_in_scope": [
          "verbatim source quotations",
          "external comparator prose without a committed object row"
        ]
      },
      "contradictions": []
    },
    "judgements": {
      "RULE": 60,
      "MODEL_SPAN_VERIFIED": 0,
      "HUMAN": 0,
      "OWED": 328
    },
    "interpretation_objects": 33,
    "interpretation_scope_complete": false
  }
]
```

## Claim limits

CLAIMED only to the extent supported by the measured logs above. A reproducible subset is not a finalized systematic review, discovery-search completeness, a formal RoB 2 assessment, a GRADE category, or independent replication. No SHIP/Overmind/portfolio certification is claimed.
