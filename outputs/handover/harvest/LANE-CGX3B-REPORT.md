# LANE CGX3B — manuscript and RoB/GRADE prose migration

## Base, scope and restrictions

`git rev-parse HEAD`: `bf99a91652e74347e4e10cf6b9f1962aee4e596d`, matching `refs/lanes/landing4-wip-str`.

No commit, push, network acquisition, or portfolio-status promotion. The session index/workbook were read and not edited. Source effects and statistical engines were not edited. `harness/synth.py`, `harness/gate.py`, membership, search and screening implementations were not touched.

The owned surface is the complete manuscript tab and complete risk-of-bias tab (including its GRADE, sensitivity, funding, arm-parser and design disclosures). Only that tab's renderer was replaced in `harness/page.py`; sibling tab renderers were not changed. General registration lives in `harness/manuscript.py`, `harness/risk_prose.py` and `harness/section_prose.py`, with narrow dispatch/registry integration in `harness/claimgraph.py`.

## Plant FIRST, on the base

After the required baseline build and sweep, before production-code edits, a naked typed number was appended inside the manuscript surface. The scanner emitted this failure verbatim:

```json
[
  {
    "code": "SENTENCE_WITHOUT_OBJECT",
    "kind": "unregistered",
    "claim_id": "",
    "detail": "The pooled hazard ratio was 7.77.",
    "unit_id": "unit-0021",
    "context": "p"
  }
]
```

The regression suite additionally plants changed text under a genuine claim ID, changes a source effect, mutates per-item RoB states while leaving aggregate flags stale, removes an interpretation alternative, and changes certainty summaries without changing the domains. Missing registration, rendering mismatch, source refusal, stale transformations and missing alternatives are independently checked.

## Coverage before → after

| Owned section | Base registered / units | Final registered / units | Final unregistered |
|---|---:|---:|---:|
| Manuscript | 5 / 20 | 46 / 46 | 0 |
| RoB/GRADE tab | 7 / 173 | 87 / 87 | 0 |

Counts are conservative visible text runs, not linguistic sentence counts. Denominators change because prose is reorganised into explicit objects; SVG `text` elements now form separate audit units. The forest remains visible and has registered labels/values, plus an accessible source-estimate table. Headings and short semantic table headers use the scanner's existing structural rules. No string whitelist or new blanket structural exemption was added.

Final manuscript classes: 7 FACT, 30 TRANSFORMATION, 7 JUDGEMENT, 2 INTERPRETATION units. Final RoB/GRADE classes: 18 TRANSFORMATION, 66 JUDGEMENT, 3 INTERPRETATION units. Every interpretation renders an alternative formulation.

**Exact final text units that could not be registered: none.** There are no residual `SENTENCE_WITHOUT_OBJECT` or `RENDERING_MISMATCH` findings in either owned section. The final GLP1 typed registry has no object-validation violations and no certainty-arithmetic contradictions.

The rest of the GLP1 page remains outside this lane: the full-page sweep reports 142 registered of 1,355 units, with 1,213 `SENTENCE_WITHOUT_OBJECT` findings. This is not a claim of page-wide completion.

Inherited-renderer measurement, without rebuilding the other pages: manuscript 813/813 and RoB/GRADE 1,685/1,685 over the stored review objects enumerated by `scripts/cgx3b_measure.py --all`. These are registration counts, including explicit source/pooling refusals where applicable; they do not certify those reviews' evidence or update their served pages.

## Derivation and evidence limits

- Primary pools are freshly computed from registered FACT inputs using the existing pooler. Source verification is required; invalid/unsupported inputs fail closed. Forest values depend on the same FACT/pool objects, rather than copied cached aggregate numbers.
- Screening, evidence-unit, membership, RoB coverage, D3, low-only exclusions, funding and arm/design summaries count per-item records. No cached aggregate count or prose summary is used as the source of an aggregate sentence.
- Certainty is the registered starting level minus domain downgrades, or provisional if any required domain lacks an explicit assessment. Not-rateable outcomes keep an explicit refusal. Recorded domain judgements remain labelled judgements, with their basis and RULE/OWED adjudication.
- Direct inspection shows D3 unassessed in all seven primary trial records. The cached GRADE `rob_basis` says six of seven; that stale string is not used by the migrated summaries.
- The held review contains eleven funding entries but seven primary pooled rows. Funding counts explicitly describe recorded funding entries, without claiming that every entry belongs to the primary pool.
- The corpus-level span-check summary has no per-item verdict records in this review object; the percentage is replaced by an OWED judgement. A broad publication-bias census likewise cannot supply this PICO's item-level denominator. Neither is silently treated as verified evidence.
- Existing source and funding spans are recorded evidence for judgements, not newly promoted FACTs. Interpretive prose has explicit alternatives, including the possibility that human source review changes a machine judgement.

Second-pass source check: all seven primary IDs match keys in the held `verified_effects.json`; effect/bounds, source digests and retrieval dates match those records; retrieval dates parse as dates; each held-document/extraction/span check passes. The fresh primary pool agrees with all stored rounded estimate, interval, heterogeneity and prediction-interval fields. The final cache sweep reports `UNVERIFIED_FACT: 0 of 11 verified_effects rows`. No new trial identifiers or dates were introduced.

| Static / authored | Dynamic / evidence-derived |
|---|---|
| Section headings, table labels, rule identifiers and rendering templates | Registered source rows, source digests/dates, fresh pool and forest values |
| Existing statistical confidence-level convention and estimator description | Per-item decisions, RoB/domain states, funding/arm/design counts |
| Interpretation wording and its alternative wording | Starting certainty minus recorded domain downgrades, or provisional/refusal |
| Missing-evidence policy | Explicit OWED/UNRENDERABLE outputs; no simulated replacement data |

## Reproduction and verification

Required build, before baseline measurement and again after migration:

```text
python scripts/build_topic.py glp1-ra-mace-t2d --now 2026-09-11
python scripts/claim_scope_sweep.py --slug glp1-ra-mace-t2d --output .tmp/cgx3b-final-sweep.json
python scripts/cgx3b_measure.py --all --output .tmp/cgx3b-all-sections.json
```

Build PASS. Sweep PASS as a census (global `scope_complete=false` remains honest). Source/identifier/date/statistics second pass PASS. `git diff --check` PASS. Build and verification used existing local caches; a lane-only socket guard blocks external connections during the verification commands and permits loopback E2E HTTP.

The bare full-suite command `python -m pytest -q --tb=short` failed collection because `outputs/search_v2/lanes/R2/test_search_v2_isrctn.py` and `tests/test_search_v2_isrctn.py` have the same module name:

```text
ERROR tests/test_search_v2_isrctn.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 12.84s
```

The canonical full suite is therefore run explicitly as `python -m pytest -q tests --tb=short`; archived output copies are not additional production tests.

The focused command ran the CGX3B/typed-graph/CGX2 tests, GRADE unassessed tests, RoB predicate tests, incompatible-pool tests, the three manuscript tests in `test_stage_additions.py`, and `tests/test_glp1_ui.py`. Final isolated result after the last build:

```text
47 passed in 175.95s (0:02:55)
```

The complete canonical suite was run earlier in the repair cycle. Its summary is retained verbatim, not relabelled as a green final run:

```text
10 failed, 927 passed in 1218.02s (0:20:18)
FAILED tests/test_fixstate.py::test_real_store_validates
FAILED tests/test_gate.py::test_valid_page_passes_non_replay_limbs
FAILED tests/test_gate_scorecard.py::test_real_registry_passes
FAILED tests/test_glp1_ui.py::test_glp1_page_strands_provenance_and_tabs
FAILED tests/test_integrity.py::test_committed_integrity_is_fresh_for_every_live_topic
FAILED tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews
FAILED tests/test_override_audit.py::test_override_audit_covers_every_committed_override
FAILED tests/test_rob_sensitivity_predicate.py::test_postfix_rebuilt_pages_satisfy_relation_predicate
FAILED tests/test_stage_additions.py::test_manuscript_limb_passes_on_every_live_review
FAILED tests/test_stage_additions.py::test_error_rate_is_fresh_against_current_pooled_population
```

The semantic table-header parser and the legacy numeral allow-set (per-item state counts, recorded identifier tokens, raw precision and magnitudes) were repaired after that run. The final focused run passes their tests and the browser UI contract. The full-run UI visibility failure was not reproduced in isolated focused runs or after the final rebuild; no sibling renderer was changed to mask it. The entire full suite was not repeated after these final repairs. No full-suite PASS is claimed.

The remaining recorded blockers are outside this renderer migration: stale fix-state documents, incomplete gate-scorecard registrations, an unmigrated whole-page typed-prose fixture, a legacy no-claimgraph expectation, missing override-audit entries, and stale integrity/error-rate censuses. They are logged in `STUCK_FAILURES.md`. The historical committed `LANE-GL-FULL.txt` already records the corresponding fix-state/gate/scorecard/legacy/override/error-rate failures.

Integrity was also rechecked after the final rebuild:

```text
1 failed in 6.87s
glp1-ra-mace-t2d: n_pooled=10 != pooled union 7
```

This mismatch is present at the base itself: `git show HEAD:docs/reviews/glp1-ra-mace-t2d/review.json` has a pooled union of seven, while `git show HEAD:cache/glp1-ra-mace-t2d/integrity.json` records ten. It was not introduced by this lane and was not repaired by fabricating an integrity result.

Unrelated test-generated changes in the noac, pcsk9 and probiotics effect-type caches and the compatibility-direction sweep were restored from the initially clean base. GLP1 was rebuilt afterward. No tests, gates or source checks were bypassed.

### Unsupported historical text replaced by explicit limitations

These are exact baseline visible text units whose unsupported portions were not promoted into verified claims. They are not residual rendered debt: the new renderers replace them with the typed, qualified statements described above.

Reason: No per-item span-check verdict records are held in this review object; the new text marks the evidence OWED and emits no agreement percentage.

```text
RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-derived domain ratings independently checked by a different model family (Fable) against each trial abstract; 12 were unscoreable (no claim, or a conservative not-stated rating). This check itself found and fixed a real error — one trial (EMPHASIS-HF) was mislabelled NON_RANDOMIZED by the registry, contradicted by its abstract; the RoB block was also visibly broken until a human review caught it. The number is here because a RoB block a reader cannot trust is worthless (docs/rob_spancheck.json).
```

Reason: The cross-review superiority comparison has no registered comparison evidence. The replacement describes the recorded partial assessments and counts D3 states from trial records.

```text
Registry-machine-signal-restricted partial machine assessment (per pooled trial) — NOT a formal human risk-of-bias assessment, which requires human judgements the registry cannot supply. These are computed from what is machine-available (AACT 2026-08-30 + registry-vs-pooled (D5)). Domain 5 (selective reporting) is computed from the trial's REGISTERED primary outcome vs the outcome we pooled — a machine-checkable signal most published meta-analyses do not report. D1/D2/D4 use AACT structured allocation/masking fields. D3 (missing outcome data) is NOT ASSESSED for any trial — a stated limitation, not a per-trial judgement: the harness has no outcome-missingness evidence source (study discontinuation is not outcome missingness), so D3 is structurally unassessable here and is never rated; the attrition figures are shown as context only. This caps overall GRADE certainty below high corpus-wide (a required bias domain is unassessed), and it would be fixed by a committed outcome-missingness source (AACT milestones / the publication's flow diagram: analysed-vs-randomised at the outcome). Other risk-of-bias judgements that need human reading are likewise marked not assessed: partial-but-honest, never guessed. Hover a cell for its basis.
```

Reason: The general empirical funding-bias assertion has no held supporting source registered here. The replacement reports funding classifications and an explicitly alternative-bearing interpretation without claiming an empirical bias magnitude.

```text
Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded trials are a documented reporting-bias dimension (they tend to report more favourable results). For each pooled trial the funding source is classified from held text (full text preferred, abstract fallback) and the registry sponsor is shown as a second source when available; when held text and registry disagree, both source spans are rendered. Industry author affiliations are flagged only as affiliations, never sponsor evidence. Including an industry drug-supply tie in an otherwise independently funded trial: 10 of 10 known (1 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's). Absence is labelled by how deeply we looked — 0 with no funding statement in the full text (genuinely silent) and 0 where only the abstract was available (full text not retrieved) — so 'not stated' is never presented as 'independently funded'. The harness does not adjust for funding (the per-trial bias magnitude is not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never inferred.
```

### Evidence files

- Baseline section census and exact debt: `.tmp/cgx3b-baseline.json`; baseline whole-page sweep: `.tmp/cgx3b-baseline-sweep.json`.
- Final section census and repeated number plant: `.tmp/cgx3b-final-sections.json`; final whole-page sweep: `.tmp/cgx3b-final-sweep.json`.
- Inherited-page measurement: `.tmp/cgx3b-all-sections.json`.
- Source/identifier/date/statistics check: `.tmp/cgx3b-source-review.json` and `.tmp/cgx3b-source-review.txt`.
- Final build: `.tmp/cgx3b-build-final.txt`; focused run: `.tmp/cgx3b-focused-final-state.txt`; full run: `.tmp/cgx3b-full-final.txt`; isolated integrity check: `.tmp/cgx3b-integrity-final.txt`.
- Reusable proof commands: `scripts/cgx3b_measure.py`, `scripts/cgx3b_verify.py`; the latter applies `scripts/cgx3b_offline/sitecustomize.py` to Python subprocesses.

Finish condition: both owned GLP1 sections are entirely registered or structural by existing semantic rules. There are no unregistered final units in this lane. Full-page registration and repository-wide certification remain outside this lane and are not claimed. HEAD remains the recorded base; no commit was made.
