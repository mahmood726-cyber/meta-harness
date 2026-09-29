# Lane NR, V1.0.1: second batch (session 2026-09-27)

Branch `nr/v101-regex`, on top of `22558dbd`. Codex (another model family) wrote adversarial counterexamples and patches;
the lane verified every artefact before applying it, dropped or reworked what was wrong, and planted every accepted case.
The calls are logged in `C:/mh-lanes/nr/codex/CALL_LOG.jsonl` (NR-C03 … NR-C17).

## How it was measured
- **Pages:** all 32 topics rebuilt with `scripts/build_topic_recorded.py <slug> --now 2026-09-11`.
- **Baselines:**
  - LIVE: the served V1.0 pages. `22558dbd` committed no pages, so the committed pages are those of `3876a62d`.
  - X8: the `22558dbd` rebuild, for this batch alone.
  - X3: the head-sources rebuild, for V1.0.1 in total.
- **Plants:** every new plant was run on the `22558dbd` sources. All defect plants fail there. The ones that pass are
  controls and regression guards: the metadata already correct at HEAD, the metformin and COPPS-2 served rows, and the
  C14 cases an intermediate round of mine broke. The event-process plant file cannot be collected on HEAD, because the
  identity does not exist there.

## Served numbers: 6 outcome results change against the live pages, 6 of 797 rows flip. Every one has a notice (all OPEN)

| page / outcome | live → V1.0.1 | notice |
|---|---|---|
| colchicine-postop-af / postoperative AF | COCS enters: k 3 → 4, 0.65 (0.21–2.05) → 0.65 (0.36–1.16) | `NOTICE_TO_APPEND.json` |
| colchicine-secondary-cv / GI adverse effects | Akrami leaves (COUNT_PCT_CONFLICT): RR 5.38 → no pooled result | `items/NOTICES_TO_APPEND_V101_B.json` |
| dapagliflozin HFpEF / primary composite | DELIVER restored: withheld → HR 0.82 (0.73–0.92), k 1 | `items/NOTICES_TO_APPEND_V101_B.json` |
| empagliflozin HFpEF / primary composite | EMPEROR-Preserved restored: withheld → HR 0.79 (**95.03%** CI 0.69–0.90), k 1 | `items/NOTICES_TO_APPEND_V101_C.json` |
| dpp4 / HF hospitalisation | SAVOR-TIMI 53 enters: k 1 → 2, pooled HR 1.13 (no RE interval at k = 2; common-effect sensitivity 1.00–1.29, I² 71%) | `items/NOTICES_TO_APPEND_V101_D.json` |
| pcsk9 / MACE | VESALIUS-CV enters (3-point co-primary 0.75): k 2 (no interval served) → 3, HR 0.8106 (0.7032–0.9344); imprecision downgrade no longer earned | `items/NOTICES_TO_APPEND_V101_E.json` |

- **Relative to X8 (this batch alone):** 3 of 797 rows flip: EMPEROR-Preserved, SAVOR and VESALIUS.
- **Protocol decision for Mahmood (in notice C).** The empagliflozin composite is declared from the protocol:
  - CV death and HF hospitalisation are required.
  - The urgent HF visit is `optional_components`, because the protocol says worsening HF includes it "as defined by the
    trial".
  - Mahmood may reverse this.

## What changed, by item

### Event process is part of endpoint identity (empagliflozin review 56710eb5)
- **The identity** is {FIRST_EVENT, TOTAL_EVENTS} × {PATIENTS_WITH_EVENT, EVENT_COUNT}, read from explicit statements only.
- **The refusal:** a stated mismatch with the target is `EVENT_PROCESS_MISMATCH`.
- **The estimate's own analysis method decides.** Cox means a first event. Joint frailty, negative binomial, Lin–Wei,
  Andersen–Gill or a recurrent-event model means total events.
- **Where it is read:** from the definition *and* the row's result span. PARALLEL-HF's Cox HR was refused when only its
  descriptive "n = total number of events" was read; the rebuild diff caught it, and it is fixed and planted.
- **EMPEROR's total HHF result** (407 vs 541 events, HR 0.73) fails both a first-event target and the composite. The 0.79
  composite passes.
- **Adversarial round:** NR-C12 found 15 counterexamples; all are fixed and planted.

### The 95.03% level travels with the analysis
- `Study.ci_pct`: the SE is derived at z(ci_pct). A missing level means 95%, unchanged.
- `harness/registry_ci.py` types the level from the held registry analysis that reports the same tuple. Matching is exact
  decimal equality at the printed precision, and disagreeing levels mean no level (never a guess). A level of 95 changes
  nothing.
- **Verifier P12** (both copies) re-derives the registry level from the bundled record. It returns MATCH with basis
  STATED_IN_REGISTRY_ANALYSIS only when the level and the SE agree. A forged basis, missing registry data, or a
  95%-derived SE fail closed.
- The page renders the typed level: "0.79 (HR), 95.03% CI 0.69–0.9", and the k = 1 note says 95.03%.
- No currently served row carried a `ci_pct`, so no served SE moved.

### Thresholds are typed parameters of a component (finerenone review 00a2b7e4)
- **The module** `harness/component_identity.py` represents a component as, for example,
  `EGFR_DECLINE {threshold_pct, threshold_op, sustained, sustained_days}`, `EGFR_BELOW {threshold_ml_min}`, or
  `KIDNEY_FAILURE {egfr_below_ml_min, includes_dialysis, includes_transplant}` when a definition is given. It never uses
  a string suffix.
- **Where a threshold is read:** only where it is attached to the eGFR decline. A threshold a component phrase lost is
  read from that trial's own definition sentence.
- **Comparison:** a parameter only one side states is unresolved, not a difference.
- **Both consumers** (`endpoint_canonical`, and the `compat_direction` typed match) use it.
- **Corpus:** FIDELIO vs FIGARO goes HETEROGENEOUS → HOMOGENEOUS (EGFR_DECLINE {40, ge, sustained}). A real 40 vs 57
  still fires. The canonical status changes on 1 of 32 pooled outcomes, and the direction audit on 0 of 32.
- **Adversarial round:** NR-C16 found 13 counterexamples, mostly hidden differences; all are fixed and planted.

### Arm assignment and three-arm results (NR-C06, NR-C10, NR-C15)
- **Arm labels:** each count goes to its nearest arm label. "…respectively" is positional, including lists with "group".
- **Refusals:** two counts claiming one arm are refused.
- **Third arm:** counts stay in one result unless a statistic or an outcome verb separates them. More than two counts in
  one result is a third arm and is refused, whatever it is called (e.g. "adalimumab", "usual care", "high-dose"). The
  paired layout "A vs B and C vs D, respectively" keeps its first pair.
- **Rescues forbidden:** a failed identity pairing is never rescued by swapping arm sizes.
- **Denominators:** a denominator stated in the sentence wins. "1,200" is read as a count while the stored source keeps
  the text as written.
- **Radius:** the served metformin and COPPS-2 rows are kept. Three unserved semaglutide three-arm sentences are now
  refused; they had been comparing two doses.

### Registry match, composite titles, exclusion scope (NR-C05, NR-C07, NR-C09, rebuild diff)
- **Timepoints:**
  - "Month 6" is the same as 6 months.
  - A target range starting above 0 ("28-90 day or in-hospital") accepts any timepoint inside it. A range from 0 is one
    cumulative window.
  - Discharge-anchored is not in-hospital.
- **Outcomes:** death composites (including "death and dependence") are not all-cause mortality.
- **Negation:** "neither/nor" is read, and its scope ends at "and with" / "but".
- **Composite titles:** every top-level part must be accounted for. An unread part is decided per row, reading stems and
  abbreviations ("Stroke/SEE").
- **Exclusions:** "with the exception of" is an exclusion cue. A population object after an exclusion cue (with "all" /
  "any") is a population exclusion.

### Result-owned metadata (field link), rounds 2–4 (NR-C04, NR-C07, NR-C14 and three corpus radii)
- **Sentence ranking:** candidate sentences are ranked, from the full outcome name, then head noun plus modifiers, then
  head noun, down to a trial-wide statement. A conflicting modifier ("Minor bleeding" for major bleeding, "Cardiovascular
  death" for death from any cause) belongs to another outcome.
- **Within a row's own span:** the attached result group whose effect is the row's estimate owns the window; otherwise
  the clause holding the estimate does.
- **Absent rows** with no estimate count only their own sentences.
- **Excluded windows:** PRIOR windows ("within 30 days before randomization") and regimens ("continued for 1 month after
  surgery") are never follow-up.
- **Known limitation:** this text fallback is still a ranked heuristic. Replace it with structured ownership in V1.1.
  Two NR-C14 cases sit in the legacy eligibility catalogue (`eligibility_chain._follow_up_value`: fixed windows, no row
  gating, unchanged since HEAD) and are recorded as strict xfails.

## n of N (final rebuild, all 32 topics)
- **Served rows flipping:** 6 of 797 against the live pages, 3 of 797 against X8.
- **Metadata fields rebound:** 68 of 640 against X8, and **330 of 746** for V1.0.1 in total (X3).
- **Analysis-set labels changed** (ROCKET fixture rule): **3 of 797** rows. ROCKET-AF per-protocol → ITT; melatonin
  20712869 completers → ITT (its own span says ITT); ENGAGE AF major bleeding: an efficacy sentence's ITT label is
  unlinked (now unresolved).
- **Registry EXACT_TARGET labels downgraded:** 78 of 1007 against X8, and **281 of 1209** in total (X3; 260 conflicts,
  21 unconfirmed). All reviewed. The bulk of this batch's 78:
  - 43 NOAC stroke-only or descriptive measures
  - 13 semaglutide comparisons or responder counts
  - 11 recurrent-event measures
  - 6 death-or-X composites
- **ENDPOINT_UNBOUND rows whose own span names the target:** 13 of 15, was 14 of 16; SAVOR now binds.
- **Extraction radius** (10,520 calls): 0 served values change. 3 unserved semaglutide three-arm sentences become refusals.

### Analysis set binds to the selected analysis's own sentence (NOAC-AF review)
- **The fixture:** ROCKET-AF's ITT HR 0.88 carried "per-protocol" from the per-protocol analysis sentence (HR 0.79).
- **The rule:** the analysis set is read from the row's own result sentence first. Elsewhere in the text, a statement
  that reports a different estimate never labels the row. A population statement (EMPACTA's "the modified
  intention-to-treat population included 249 …") stands on its own.
- **Result:** all four NOAC trials read ITT. The numbers do not change.

### Endpoint definitions bind only to definition-bearing sentences (PCSK9 review f7132bc2)
- **The fixture:** VESALIUS-CV's HR 0.75 had been bound to a BACKGROUND sentence, whose population qualifier ("without a
  previous MI or stroke") was read as its components, and was refused.
- **The rule:** background, introduction, conclusion and "is unknown / has been shown" sentences never define an
  endpoint. A sentence defining several labelled composites ("(3-point MACE)", "(4-point MACE)") yields one definition
  per label, and a result naming a label binds to that label's segment.
- **Visible judgments:** CHD death for CV death, and ischaemic stroke for stroke of any type, are shown on the row and
  the page with their basis, instead of being silent equalities.
- **Spelling:** American "revascularization" is now read like British "revascularisation", so 4-point MACE has its
  fourth component.
- **Corpus:** 72 of 338 former "definition" sentences no longer count; they were reviewed as conclusions, background,
  methods of meta-analyses and results sentences. One loss is recorded: a cohort-study bracket nesting "(CVD)".

### Other fixes found by the rebuild diffs
- **Event process from the analysis method:** it is read from the definition *and* the result span, so PARALLEL-HF's
  Cox HR is first-event, not total events.
- **Timepoint ranges:** a target range above zero ("28-90 day or in-hospital") accepts any timepoint inside it.
- **Abbreviations:** a title part written as its abbreviation ("Stroke/SEE") is named.
- **Mortality qualifiers:** settings and qualifiers ("ICU and hospital mortality", "cardiac and non-cardiac mortality")
  are not a second event.
- **Typed levels:** EMPEROR-Reduced's registry states 95.04%, and that level is now carried. The unserved k = 2 audit
  interval moves 1.4052 → 1.4044; the served numbers do not change.

### Tests changed (each with its reason, in the test)
- **`test_result_withdrawn`:** the withdrawal MECHANISM now runs on the V1.0 withdrawn pages, frozen in
  `tests/fixtures/result_withdrawn/`. A new test checks that the restored pages pool their result and keep
  `withdrawal_history`.
- **`test_grade_missing_is_not_favourable`:** a restored result gains a rating and is not a loss. pcsk9's imprecision
  change is acknowledged under notice E.
- **`test_r4_ambiguity`:** `arm_pairs` leaves HELD. The cluster rule refuses the plant with 0 served extraction
  changes.
- **`test_source_hierarchy_regression`:** the audit interval moves with the typed 95.04% level.
- **Regex layer:** 84 new owned sites are planted (NR-C17), which found and fixed a "p = 0.04" boundary bug. One
  runtime-built pattern is replaced by plain string matching. Two line-keyed sites are re-keyed:
  `honest_ratchet.py:L53` → `L54` (moved by `22558dbd`), and `target_endpoint.py:L891` → `L904`.
- **Derived artefacts** regenerated by the repo's scripts:
  - `cache/colchicine-postop-af/rob2.json` and `arm_contrast.json` gain COCS. The builders also dropped 27502857's
    entries; those were restored verbatim.
  - The error-rate census: 131 pooled rows, 26 NOT_INDEPENDENTLY_RECHECKED.
  - The fix ledger and the README fix-state lines.

### Event process: DAPA-HF's identical 0.75 (SGLT2-HFrEF review), follow-up commit
- **The fixture:** DAPA-HF's registry holds two results with the same point estimate.
  - First-event: 'Subjects Included in the Composite Endpoint of CV Death or Hospitalization Due to Heart Failure', HR 0.75
    (0.65-0.85), Cox. This is the pooled input.
  - Total-event: 'Events Included in the Composite Endpoint of Recurrent Hospitalizations Due to Heart Failure and CV
    Death', 567 vs 742 events, rate ratio 0.75 (0.65-0.88), LWYY proportional rates model.
  - The live page listed the total-event result as an EXACT_TARGET alternative.
- **Result:** it is refused (`EVENT_PROCESS_MISMATCH`), and the refusal holds even without the word 'recurrent'.
- **Signals:** the rate models (LWYY, proportional rates, semiparametric, Ghosh-Lin) and the registry's own event-count
  label ('Events Included in', paired with 'Subjects Included in') are now total-event evidence.
- **Not a signal on its own:** a 'Rate Ratio' parameter type. ASCEND's registry uses it for first-occurrence results, so
  the 'Rate Ratio (RR)' scale reading is left unchanged.
- **Radius** (this change alone, against the batch-2 rebuild):
  - 0 of 797 served rows change.
  - 0 of 652 metadata fields rebound.
  - 2 of 939 registry EXACT labels downgraded: sacubitril-valsartan's 'Events Included in the Composite Endpoint of CV
    Death or Recurrent Heart Failure Event ...', a total-events measure the previous phrasing missed.
- **Tests:** full suite 4249 passed; the same 19 failed / 12 errors as batch 2, 0 new.
- **Regex inventory:** the 'worsening heart failure' title pattern is now named (`_WORSENING_HF`), because its line-number
  key broke whenever lines were added above it.
- **Note for lane oc:** `NOTE_TO_OC_sglt2_dapa_hf.md`. The compatibility narrative (`docs/definition_audit.json`, and the
  topic's `trial_annotations` for 31535829) still describes DAPA-HF's broader primary, including urgent HF visits, while
  the pooled input is the first-event CV death/HHF secondary. Keep the input and fix the narrative; no number changes.

### Subgroup provenance: JUPITER >=70 (statins-older-adults review), follow-up commit
- **The fixture:** the page called JUPITER's >=70-years subgroup (PMID 20404379, HR 0.61) 'pre-specified' because the
  topic asserted `evidence_unit: prespecified_subgroup`. The held abstract's LIMITATION says the age cut-point was chosen
  after trial completion.
- **The field:** `harness/subgroup_provenance.py` derives `subgroup_provenance` in {whole_trial, prespecified_subgroup,
  post_hoc_subgroup} from a quoted source span (held abstract, then full text, then row source). It is never asserted.
  - A topic now declares only THAT a row is a subgroup (`evidence_unit: subgroup`).
  - Not stated resolves to UNRESOLVED (`subgroup_unresolved`), never to pre-specified.
  - Post-hoc evidence beats a general pre-specification. A bare 'post hoc' counts only in the same clause as a subgroup
    cue, and negated statements are ignored.
- **RoB, not exclusion:** a post_hoc_subgroup raises D5 (selection of the reported result) from low or not-assessable to
  some concerns (`rob2.apply_subgroup_provenance`, rule `...+subgroup_provenance_v1`). The provenance is stored in D5's
  inputs, so `rederive_domain` reproduces it; the gate check passes. The row stays pooled.
- **Topics:**
  - statins: annotation set to `subgroup`; 'pre-specified' removed from the question and population prose.
  - melatonin-primary-insomnia-sol also asserted a 'pre-specified age 65-80 subgroup' (PMID 20712869). The held abstract
    does not state it, so it is now UNRESOLVED and labelled 'subgroup (pre-specification not stated in the source)'.
- **A test that defended the defect:** `test_estimand_naming::test_statins_subgroup_evidence_unit_plant` pinned
  `prespecified_subgroup` and the page string 'pre-specified subgroup of JUPITER'. It now asserts post_hoc_subgroup and the
  absence of the old wording.
- **Codex NR-C18 (adversarial, slot 1, logged):** 17 sentences. All 14 claimed misclassifications reproduced by
  execution before the fix, including 4 false post-hoc results that would have wrongly raised D5 ('were not post hoc',
  'prespecified, not post hoc', 'not selected after trial completion', a post-hoc sensitivity clause after ';'). Fixed,
  and planted with 3 ambiguous controls that stay UNRESOLVED. Codex's narrow 'defined before unblinding + protocol'
  branch was not taken: UNRESOLVED is the conservative answer there.
- **Radius** (32 topics, against the batch-2 rebuild build_G):
  - 0 of 797 served rows, 0 of 652 metadata fields, 0 of 937 registry labels change.
  - Provenance over pooled rows: 129 whole_trial, 1 post_hoc_subgroup (JUPITER), 1 unresolved (melatonin).
  - RoB: 1 trial changes (JUPITER D5 not assessable -> some concerns; machine-signal overall low -> some concerns).
  - Knock-ons in statins: GRADE certainty stays provisional; its internal RoB downgrade count goes 0 -> 1, total 1 -> 2,
    and is not rendered while domains are unassessed. The RoB-restricted re-pool (low-only k=1, 0.70) stays suppressed
    because formal RoB 2 is not assessed.
- **Notice for Mahmood:** `items/NOTICES_TO_APPEND_V101_F.json`, a served RoB judgment and label change with no number
  change (OPEN).
- **Build hazard found on the way:** stopping a background rebuild with TaskStop left its inner loop running. Two
  docs-restoring loops in one worktree clobbered 14 saved copies, which were byte-identical to the committed pages, and
  the diff then showed 3 false 'served changes' (the batch-2 changes reverting). Rebuilt serially with no loop running,
  that radius is 0. Check any rebuild for copies byte-equal to `HEAD:docs/reviews/<slug>/review.json`.
- **Tests:**
  - Plants: `tests/test_nr_v101_subgroup_provenance.py` (14, including 16 adversarial sentences). The regex-inventory and
    RoB tests pass.
  - Full suite: 4262 passed, 71 xfailed, 20 failed, 12 errors (56 min; the old 50-min `timeout` now cuts it off).
  - All 12 failures that differ from the batch-2 list fail identically at HEAD with this change stashed (certificate
    ×6, gate full-reproduction, fixstate, aact_cache replay, result_withdrawn ×2, sglt2 source-hierarchy). They depend
    on the docs state: this run used the committed V1.0 pages, and the batch-2 run used rebuilt pages. Conversely, 11
    bundle/execution-record/page-verifier failures from that run now pass. Integration state; the captain's
    regeneration decides both sets.
  - Run the suite with `--continue-on-collection-errors`, or `test_site_detects`' collection error aborts it.

### Label fixes as harness code: statins addendum, ticagrelor, tocilizumab (Mahmood: "fix all in harness")
- **No hand-edits.** The statins and melatonin topic edits from the subgroup commit are REVERTED (topics equal
  6d3b41ad). The harness now serves the derived value and corrects asserted 'pre-specified … subgroup' prose itself
  (`subgroup_provenance.correct_review_prose`), recording each correction in `served_prose_corrections`.
- **What is harness code now (each with plants and regex-layer specs):**
  - `harness/composite_label.py`: a pooled composite's label is derived from its inputs' typed component sets
    (IDENTICAL_3P / IDENTICAL / DIFFER / UNTYPED); a MACE or 3-point name is served qualified unless the inputs earn it;
    ischaemic vs all stroke stays visible. Gate: `check_composite_label`.
  - `harness/k2.py`: the k=2 registered interval and the direction-conflict pooled row are "computed, withheld by
    presentation/display policy", derived from whether they were computed (`state`), on every surface (page,
    limitations, manuscript, GRADE imprecision, RoB-sensitivity reason, index). PLATO is shown "alone … not the
    review-wide conclusion". Guards: `check_common_effect_not_promoted`, `check_direction_conflict_claims` (no
    region/ethnicity explanation, no equivalence / no-benefit reading; negation- and scope-aware).
  - `harness/rob2.py`: the D5 IDENTITY CHECK. Order-independent: identity anywhere (typed component equality with
    complete typing, or token-containment text identity) gives low; else a signal resting on a similarity-only or
    identity-undecidable comparison (an untyped 'death from vascular causes') is WITHDRAWN (treated as not assessed);
    only a decidable no-match gives some concerns. The build overlay re-derives D5 with the gate's matcher
    (`rob2.canonical_matcher`), so stored = re-derived. RX-OL1..8 (located defects in regex_layer/defects.py) fixed as
    named compiles; 10 strict xfails now pass.
  - `harness/population_qualifier.py`: a k=1 result is "the trial's own result (one trial; not a synthesis)", with the
    trial's own population derived from its eligibility and co-treatment sentences (RECOVERY-tocilizumab: hypoxia AND
    systemic inflammation, 82% on systemic corticosteroids); the review's intervention is never a 'co-treatment'.
    Gate: `check_single_trial_presentation`. The tocilizumab SAE pool stays K2_SINGLE_DF-withheld.
- **Corpus n of N** (`scripts/nr_v101_label_audit.py`; detectors derive from rows and held records, not from the
  fields the fixes add). Live pages (HEAD) → rebuild build_K:

  | | pre-fix (live) | post-fix |
  |---|---|---|
  | A post-hoc subgroup served as pre-specified | 1 of 32 pages (+1 unresolved: melatonin) | 0 |
  | B pooled composite with an unqualified MACE/3-point label | 3 of 24 (pcsk9, statins, ticagrelor) | 0 of 25 |
  | C k=2 computed interval worded as a refusal | 11 of 12 | 0 of 12 |
  | D common-effect CI served as primary | 0 of 12 | 0 of 12 |
  | E direction conflict: refusal wording / anchor as conclusion / explanatory-equivalence | 2 / 1 / 0 of 2 | 0 / 0 / 0 |
  | F D5 signal failing the identity check, shown | 9 of 99 | 0 of 100 |
  | G primary k=1 served as synthesis or without its population | 6 of 6 pages (7) | 0 of 8 |

  Denominators differ where this lane's build already carries the pending batch-2 changes (DELIVER, EMPEROR k=1).
- **Radius vs build_H:** 0 of 797 served rows, 0 of 652 metadata fields, 0 of 937 registry labels. RoB: 10 D5 signals
  (9 withdrawn, PARADIGM-HF corrected to low by the 'heart-failure' typing fix) on 8 topics; two overalls move from
  some concerns to low on the assessed domains (omega-3 30146932, PHILO) because the withdrawn D5 was their only
  concern. GRADE stays conservative: a trial whose D5 was WITHDRAWN counts as 'some concerns' for the RoB downgrade
  (`n_withdrawn_counted_as_some_concerns`; missing is not favourable), so ticagrelor keeps its downgrade; only
  sacubitril's RoB downgrade goes, on POSITIVE evidence (PARADIGM-HF's registered primary now correctly identified),
  acknowledged in `test_grade_missing_is_not_favourable` with its notice. Certainty stays provisional. Notices:
  `items/NOTICES_TO_APPEND_V101_G.json` (8 RoB) and `…_H_LABELS.json` (17 pages, labels only).
- **Pre-fix firing:** `items/LABELS_PLANTS_PRE_FIX.txt` — 22 of 27 plants fail on the pre-fix pipeline + pages; the 5
  that pass are unit plants of the two new modules (no pre-fix counterpart; without the modules they fail to import).
- **Codex:** NR-C18 (subgroup provenance, 14 cases) and NR-C19 (conflict guard + D5 identity, 21 cases): every claimed
  case reproduced by execution before a fix; all planted. Taken beyond the ticagrelor case: similarity-only matches
  between two UNTYPED outcomes are withdrawn too (measured on the corpus: several were false, e.g. 'Recurrent
  pericarditis' ~ 'Symptom persistence at 72 hours'). Not taken: a narrow 'defined before unblinding'
  pre-specification branch (UNRESOLVED is the honest answer there).
- **Open, for the owners:** the melatonin PROTOCOL states Wade et al.'s age 65-80 population is "pre-defined … a
  co-primary analysis"; the held abstract does not, so the harness serves it UNRESOLVED and does not edit the
  protocol. A source span (the full paper) would settle it.
- **Bulk-signing packet:** `bulk_signing/` (see its README lines in the packet): every pending notice across lanes,
  nothing signed.
- **Gate scorecard:** the 4 new gate checks are registered in `registry/gate_scorecard.json` (PLANT events citing the
  plant files, adjudicated internal; production UNRESOLVED), not validated in production.
- **Tests:** plants and regex suites pass (regex: 2402 passed, 50 xfailed -- 10 former strict xfails fixed). The full
  suite (temp moved to F:, C: was 99% full and the first run failed on temp-dir creation) was classified test by
  test: every failure outside the batch-2 list fails identically with this lane's harness changes stashed, or is
  docs-state (pre-fix committed pages read by the current renderer: `test_limitations_legacy_compare`, bundle,
  certificate, page-verifier) that clears when the captain regenerates the pages. The 4 that failed only with these
  changes were fixed at their cause: scorecard entries; GRADE counting a withdrawn signal as a concern; the
  `test_hrm_gating` assertion pinned the old 'Single-trial effect' wording; one acknowledged downgrade change.
- **Incident:** stopping my build loop I killed every PID matching the script name, which also killed lane evid2's
  rebuild (`/c/mh-lanes/evid2-v101`, stopped after 6/32) and restarted lane screen's from its first topic. Not
  relaunched by me (their worktrees). Kill only PIDs whose cwd/argument is your own worktree.

## Tests (full suite, sequential, temp on C:)
- **Result:** 4237 passed, 71 xfailed, 19 failed, 12 errors, all accounted for.
- **Environment:**
  - 11 files cannot import `reproducible_ai` (not in the sparse checkout).
  - `test_regex_measure`: the same module.
  - `test_production_record_deploy_target`: needs `.github/`, which the sparse checkout lacks.
- **Integration state:** clears when the release captain regenerates the bundle and certificates (`test_bundle` ×7,
  `test_bundle_verifier` ×2, `test_execution_record` ×2, `test_page_verifier` ×3).
- **Failing at HEAD too:**
  - `test_hm2_contract` and `test_hm2_ui`.
  - `test_no_model_call_in_pinned_path` (`verify_bundle.py` imports `urllib` at HEAD).
  - `test_site_detects`: now a collection error, because the 84 newly planted sites also need DETECTS entries (see
    Open).

## Open
1. **Superset not detected:** "Stroke/SEE/All Cause Death" is EXACT for the NOAC target, because all-cause death is not
   read as an extra component there. It is the same at X8.
2. **V1.1:** replace the follow-up text fallback and the legacy eligibility catalogue with structured ownership.
3. **`regex_layer/site_detects.py`:** needs DETECTS entries for the 84 newly planted sites; this test already failed
   at HEAD.
4. **Disk:** F: filled mid-rebuild (another lane's usage). 22 topics failed with ENOSPC and were rebuilt under a
   free-space guard; no collateral file damage was found. Keep pytest temp dirs on C:.
