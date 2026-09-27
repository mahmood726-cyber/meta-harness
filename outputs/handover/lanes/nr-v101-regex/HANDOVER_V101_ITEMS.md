# Lane NR, V1.0.1: percentage corroboration (both ways), result-owned metadata, registry match, composite declaration

Branch `nr/v101-regex`, on top of `a8ac28de` (exclusion polarity + umbrella override). Everything below was verified with
the same method:
- **BEFORE** = the head's own sources. **AFTER** = this commit.
- **Plants:** 54 of 62 fail on the head sources (`ITEMS_PLANTS_PRE_FIX_FINAL.txt`). The 8 that pass are the
  meaning-preserving controls, which must hold both before and after.
- **Regression:** the 93 test files that touch the changed modules: 11 failed, 3,558 passed after; the same 11 fail on the head sources, 0 new
  (`tests_items_before.txt` / `tests_items_after.txt`).
- **Rebuild:** all 32 topics with `scripts/build_topic_recorded.py <slug> --now 2026-09-11`, diffed against the head
  rebuild.

## 1. Percentage corroboration fails in BOTH directions (colchicine-secondary-CV review 3eb69ba7)
- **The false acceptance.** Akrami (34876021), GI adverse effects: "15 (12.5%) … 3 (2.5%)", arm sizes 120/129. 3/129 is
  2.33%, i.e. 2.3%, not 2.5%. It was served as "percentage-corroborated" because the old check accepted anything within
  1.0–1.5 points.
- **The rule** (`extract.pct_consistent`). The stated % must equal count/denominator **rounded (half-up or half-even),
  truncated, or double-rounded** at its stated precision. Double rounding (13/81 = 16.049 → 16.05 → "16.1") is a reporting
  artefact, not a disagreement; the first strict version refused two such genuine rows.
- **The two failure states:**
  - a near-miss that none of those explains (within the old window) is a `COUNT_PCT_CONFLICT`;
  - a gross mismatch is "not corroborated", as before. It is usually a wrongly inferred denominator ("32 patients (13%)"
    against a total of 492), not a conflict in the source.
- **A conflict is never a success.** The trial is refused for that outcome and the conflict is kept: stamped as a typed
  code when the row is created (`pipeline`). `consumer_consistency.annotate_review` no longer relabels a typed finding as
  "not yet extracted".
  - The first rebuild caught that relabel. It also caught the same layer showing the **MACE** counts (8/120 vs 28/129) as
    Akrami's GI value, a wrong-outcome candidate binding. That binding is pre-existing and **not fixed here** (see open
    items); the guard keeps it off typed rows.
- **Corpus:** `extract_trial` over every record × outcome changes **2 of 10,520**, both value → `COUNT_PCT_CONFLICT`:
  Akrami (served) and 62/180 = 34.44% stated 34.8% (38184150, unserved). The double-rounding rows stay corroborated.
  **Rows currently marked corroborated that are not: 1 of the served pooled count rows** (Akrami).

## 2. Result-owned metadata (field-link: CAP corticosteroids, denosumab)
- **Rule.** An estimate's timepoint and definition bind to the sentence that OWNS that result
  (`compat_check._result_span`, `window_evidence.result_window`).
  - A primary-endpoint paragraph defines only the result it names (`_defines_this_row`).
  - Elsewhere in the text, only a trial-wide follow-up statement binds, never a regimen.
  - The review's declared timepoint no longer stands in for a trial's statement.
- **Fixtures:**
  - CAPE COD → **28 days** ("By day 28, death had occurred …"), not the 14-day tapering regimen.
  - Torres → **in-hospital**, and no longer "defined" by the primary treatment-failure paragraph.
  - FREEDOM nonvertebral/hip fracture → no longer "defined" as "primary end point was new vertebral fracture"; the
    vertebral-fracture estimate keeps its definition.
  - An adjustment model is never borrowed from another estimate. The adjustment reader was already strict, and FREEDOM's
    models are UNRESOLVED because nothing held states them.
- **More regimen misreadings found:** probiotic regimens served as 14-day windows ("randomized to receive Lactobacillus GG,
  20 × 10⁹ CFU/d, or placebo for 14 days"). Dosing cues were added: receive, CFU, sachet, taper, intravenous, orally.
- **Compat check.** An underivable row no longer hides a heterogeneous one: both findings are reported.
- **Corpus:**
  - **Metadata fields rebound: 335 of 740 present** across the 797 served rows: follow-up windows 78 rows (value) / 79
    (source); endpoint definitions 32 / 34; admission follow-up 2.
  - Most follow-up rebinds are "review timepoint → underivable": rows whose own text states no window, now disclosed as
    `COMPAT_DIMENSION_UNDERIVABLE` instead of carrying the review's promise.
  - Reader level: compat follow-up 334 of 797, admission follow-up 48 of 797.

## 3. Registry match: RECOVERY's influenza "discharge alive" is not COVID-19 mortality
- **`target_endpoint.registry_outcome_match`.** EXACT_TARGET requires agreement on four things:
  - **population:** no `population_none` population named by the title label or AACT's population field;
  - **comparison:** a named comparison must be the topic's intervention;
  - **outcome:** a mortality target (by its name, not a composite) only by a death outcome, never "discharge alive";
  - **timepoint:** the target window overlaps the row's AACT time frame (28/30-day ±10%). Open-ended targets demand
    nothing; in-hospital against numeric is UNCONFIRMED.
- **Outcomes:** a conflict gives DIFFERENT_OUTCOME; an unconfirmed dimension gives NEAR_MATCH.
- **Where it applies:** `trial_family` (registered-outcome candidates and registry results) and the pooled-row registry
  route.
- **AACT time_frame** (approved fetch, `scripts/fetch_design_outcome_timeframes.py`). Written to
  `cache/<slug>/design_outcome_timeframes.json`:
  - local snapshot 2026-08-30 (data current to 2026-08-27);
  - design_outcomes: 17,995 of 17,995 held rows found, sha256 `8ce288a0…`;
  - outcomes: 6,161 of 6,161, sha256 `0c810b67…`;
  - 0 id drift; read at 2026-09-27T10:57:40Z.
- **Corpus: registry EXACT_TARGET labels downgraded, 207 of 1,209.**
  - **173 conflicts → DIFFERENT_OUTCOME:**
    - timepoint 142: mortality at 6 months / 90 days against 28–30 days; denosumab 12–24 months against 36;
      esketamine day 2–15 against day 28; semaglutide week 44/104/3 years against week 68;
    - outcome 17: ICU-free days, MINS, TXA fibrinolysis/PPH prevention against death;
    - comparison 9: CagriSema against semaglutide;
    - population 5: RECOVERY's influenza and CAP strata, 2 of them also discharge-alive.
  - **27 unconfirmed → NEAR_MATCH:** an in-hospital target against a numeric frame (POAF, TXA).
  - **7 component-based:** DELIVER's 3 CV-death-only measures are now NEAR_MATCH, and empagliflozin's 4 are blocked
    by its undeclared composite.
  - Every class was read against its rows. Two false-downgrade defects found this way are fixed and planted: AACT's
    analysis-population field read as a disease label, and MACE keywords read as a mortality target.

## 4. Composite declaration: DELIVER restored through the endpoint module (dapagliflozin HFpEF review 02f77767)
- **The invariant** (`composite_declaration_problem`). A composite's components (declared, or read from its title) must
  account for every component its title names. Otherwise its rows are refused as `COMPOSITE_DECLARATION_INCOMPLETE`
  (fail closed).
  - Declared components are read item by item: "urgent heart failure visit" silently vanished when the list was read
    joined.
  - "Worsening heart failure" = HF hospitalisation or urgent HF visit, in the title vocabulary only.
- **Corpus:** 2 outcomes fail the invariant.
  - dapagliflozin-hfpef-hosp: declared per its protocol ("worsening heart failure includes hospitalization or urgent
    visit").
  - empagliflozin-hfpef-hosp: **not declared** (see open items).
- **DELIVER** (`topics/dapagliflozin-hfpef-hosp.json`: `components`, and `withdrawn` → `withdrawal_history`):
  - primary k 0 → 1, **HR 0.82 (0.73–0.92)**, from the abstract's all-patient primary sentence bound to its definition;
  - the CV-death component (0.88) fails the composite;
  - no EF subgroup is used;
  - single trial, no random-effects pooling.

## Served numbers (all 32 topics): 2 outcome results change, 3 of 797 rows flip
| page / outcome | before → after | notice |
|---|---|---|
| dapagliflozin-hfpef-hosp / primary composite | withheld (k 0) → **HR 0.82 (0.73–0.92), k 1** | `NOTICES_TO_APPEND_V101_B.json` |
| colchicine-secondary-cv-prevention / GI adverse effects | RR 5.38 (1.60–18.10), k 1 → no pooled result | `NOTICES_TO_APPEND_V101_B.json` |
| empagliflozin-hfpef-hosp / primary: EMPEROR-Preserved row | EXTRACTION_NOT_PERFORMED → COMPOSITE_DECLARATION_INCOMPLETE (not pooled either way) | none (no number) |

The two notices were built by the repo's refresher from the rebuilt pages, run on a copy of the ledger. Their reasons are
rewritten from the evidence and `reason_locked`: the generated reason was the refresher's canned "hand-row binder" sentence,
false for both. Both are OPEN, for Mahmood.

## Open (not done here)
1. **empagliflozin-hfpef-hosp** needs its composite declared, which is a protocol decision. Its protocol reads "worsening
   heart failure includes hospitalization or urgent visit … as defined by the trial". Declaring
   {CV death, HF hospitalisation} with the urgent visit optional would admit EMPEROR-Preserved: a served change, and a
   notice.
2. The same "as defined by the trial" wording implies DELIVER's urgent-visit component is optional once a second trial is
   added.
3. `consumer_consistency.outcome_source_candidate` binds counts from a different outcome's sentence (MACE counts shown for
   a GI row). This is guarded for typed rows here; the binding itself still needs a fix.
4. **SAVOR-TIMI 53 false ENDPOINT_UNBOUND** (DPP-4 review): in progress. Codex NR-C03 is drafting the patch; its plants are
   strict xfails in `tests/test_nr_v101_composite_declaration.py`.
   - **Unbound rows whose own span names the target: 14 of 16** (`UNBOUND_AUDIT_X8.json`). Only **1** of them (SAVOR) is
     an endpoint-reading failure.
   - 1 is unbound by design: ORIGIN "major vascular events", named without a definition.
   - 12 fail on LOCATION, not reading: the number is not found in the held document, or found in several places.
5. At integration, regenerate all 32 topics and the bundle. Certificates and served verifier mirrors are stale by design
   since the first V1.0.1 commit.
