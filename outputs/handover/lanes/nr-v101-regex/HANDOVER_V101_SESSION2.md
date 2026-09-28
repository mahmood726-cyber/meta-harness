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
