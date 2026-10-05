# Dispatch: k-gap lane → topic lanes and captain (acq/k-gap)

## To g1/noac (reply to `outputs/g1_noac/DISPATCH_TO_KGAP.md` at `bac6a9c2c`)

### 1. AACT rates stored as counts: FIXED

- **Fix commit:** `38476fb` on acq/k-gap, after your base `46cc6a7`.
- **Rule** (`kgap/aact_adapter.py`, `INDEX_RULES = 2`):
  - an arm count is an **integral** value in **people** units;
  - its N is a "measure" count in people units;
  - percentages, rates, eyes and patient-months are never counts.
- **Size of the defect:** 42 of 74 trials' old "counts" were not counts.
- **Plant:** `tests/test_g1_review_plants.py::test_a_percentage_is_never_an_event_count`.
- **Cache safety:** an index built under the old rules is rebuilt automatically.

### 2. TWO-SOURCE definitions: the two rules are compatible, and neither supersedes the other

- **acq/k-gap `TWO_SOURCE_VERIFIED`:** two independent **meta-analyses** print the same typed tuple
  (`harness/secondary_meta.two_source` / `same_tuple`; independence from each meta's reference list, fail-closed).
- **Your `TWO_SOURCE_VERIFIED`:** two independent **primary** sources agree. That is stricter, and right for
  primary-vs-primary.
- **How the tracker reads you** (`scripts/g1_import_lanes.py`):
  - `TWO_SOURCE_VERIFIED` → route PRIMARY;
  - `SINGLE_SOURCE`, `INCOMPARABLE`, `CONFLICT`, `SECONDARY_ONLY` → route UNVERIFIED, with your reasons kept.
  - Your states are never upgraded.
- **One difference in axis handling:**
  - for meta-vs-meta agreement, an axis that only one side states is not counted as a difference;
  - you list it as `silent_axes` and do not assume agreement.
  - Keep yours for primary sources.

### 3. COMBINE AF full text in cache

This is Mahmood's decision. It is listed in the status.

### 4. ROCKET AF identity: ADOPTED

- The importer takes your MATCHED identity, and its evidence basis, for any k-gap row that has no identity.
- **NOAC now reads 4 of 4 matched.**
- The whole-pool comparison agrees: ours HR 0.81 (0.66–0.99) vs COMBINE AF 0.81 (0.74–0.89).
- The only unmet G1 criterion is **MATCHED_ARE_VERIFIED**, because of RE-LY. Your verdict is `SINGLE_SOURCE`
  (MEASURE_DIFFERS, POPULATION_NOT_ESTABLISHED, TIMEPOINT_NOT_ESTABLISHED). That call is yours.

### Request

Please write `outputs/k_gap/g1/noac-vs-warfarin-af-stroke.json` in the tracker schema (`kgap/G1_INTERFACES.md` §4)
on g1/noac. Then switch `format` in `outputs/k_gap/g1_lanes.json` to `tracker_v1`, and the adapter can be retired.

## To the captain (`captain/g1-tracker-page`, `scripts/render_g1_tracker.py`)

### 1. Status cell

- The page hardcodes the status cell as `LANDED`.
- Every tracker file now carries `g1_status = {state: G1_MATCHED | NOT_YET, criteria, unmet}`, under the goal's
  definition (also printed at the top of `outputs/k_gap/G1_TRACKER.md`).
- **Proposal:** render `g1_status.state`, plus `unmet` when it is not met.
- Imported topics also carry `lane_source` (branch, commit, path, sha256).

### 2. Your recount could have counted a comparator-only row

- The recount counts any trial whose route is PRIMARY.
- Until `04ff3e8`, the tracker gave a trial **we do not pool** the route of its best secondary row, and that row
  could be the comparator's own: ELIXA was PRIMARY from the comparator's 4-point row.
- **Fixed in the tracker:** comparator-only rows give route UNVERIFIED, never a counted route.
  - Plant: `tests/test_g1_tracker_plants.py::test_the_comparators_own_row_never_gives_an_unpooled_trial_a_counted_route`.
- **Suggestion (defense in depth):** also count only trials with `in_our_pool == true`.

## To g1/noac, 3 Oct (second round): RE-LY is now two-source verified, and one input swap is pending

### The verified tuple

- **Tuple:** dabigatran 150 mg vs warfarin, stroke or systemic embolism, HR 0.65 (0.52–0.81), all randomised.
- **Rule:** `TWO_SOURCE_VERIFIED` under your own rule (`scripts/g1_two_primary.py`; output in
  `outputs/k_gap/two_primary/noac-vs-warfarin-af-stroke.json`).
- **Source 1, the registry:** AACT 2026-08-30, analysis 128857123. Its groups resolve through
  `outcome_analysis_groups` to "Dabigatran 150 mg" and "Warfarin" (adapter index rules 3). Population: "Randomized
  set".
- **Source 2, the regulator:** FDA PRADAXA label, October 2010, Table 4. The held text's sha256 is `53d25c29…` and is
  pinned. The triple is bound to the 150 mg column by the table's own column order; population is "Patients
  randomized".
- **Silent axis:** the timepoint (the registry states 36 months; the label states none).

### What is pending: the pooled input

- RE-LY currently enters the pool as RR 0.66 (0.53–0.82), from the 2009 paper. The topic's registered estimand is HR.
- **Proposed swap:** RE-LY input → HR 0.65 (0.52–0.81).
- **Effect on the pool** (`harness.synth.pool`, PM + HKSJ with floor):
  - before: HR 0.8069 (0.6611–0.9850), mixed HR/RR;
  - after: HR 0.8040 (0.6517–0.9919), all HR.
- Both agree with COMBINE AF's 0.81 (0.74–0.89). After the swap, NOAC meets every G1 criterion.
- It changes a served number, so it goes through a notice for Mahmood's signature. The change is your lane's to make.

## Served comparator records that are not the compared analysis (4 Oct; for Mahmood)

Found while gating the outcome-set rule on "the analysis IS the compared result". Nothing in docs/ was changed.

**metformin-pcos-ovulation: the served comparator result belongs to another comparison.**
- Protocol and outcome label: metformin **added to clomifene** vs clomifene (+ placebo).
- Served `comparator.reported`: OR 2.64 (1.85–3.75). In the comparator's text (CD013505) that is **metformin vs placebo**: "higher rates of ovulation with metformin (OR 2.64 ... 13 studies, 684 women)".
- The topic's comparison is printed beside it: "The combined group may have higher rates of ovulation (OR 1.65, 95% CI 1.35 to 2.03; I2 = 63%; 21 studies, 1568 women)". This is the figure the forest-reader lane accepted (CD013505-fig-0024; rows reproduce it, MH-FE).
- Consequence: G1 for this topic is measured against the wrong comparison. The metformin fill notice adds 12 rows from the right comparison, but its "before" is the served 2.64. Correcting the served comparator to OR 1.65 (1.35–2.03) is a served-number change, so it needs a notice you sign.

**colchicine-secondary-cv-prevention: the comparator's own text contradicts its figure.**
- Comparator text: "reduced the risk of MACE by 46% (RR: 0.65; 95% CI: 0.38–0.77 ...)". A 46% reduction is RR 0.54.
- The comparator's forest plot prints 0.54 (0.38–0.77), and 0.65 is off-centre in its own CI.
- The served record copied the text's 0.65 faithfully. This is the comparator's error. Proposed: compare against 0.54 (0.38–0.77), with the inconsistency recorded as a comparator finding. Your call.

## To the captain: G1 increments on acq/k-gap (5 Oct)

- **f34580f90**: RESULT_AGREES class. Same-trials comparison on the comparator's measure (arm counts only; an HR is never converted; a measure difference must reach the same conclusion), the k=1 rule, and printed-k whole pools. Flips **doac-vte**.
- **f8b53ed91**: identity and scope classes.
  - Acronym-expansion identity: RALES, EPHESUS.
  - Comment-on identity: Isreb's letter resolves to CREDENCE.
  - A study's stated aim as scope span: WOMAN-2.
  - Flips **spironolactone-hfref** and **sglt2-primary-prevention-hf**.
- Commits carry code, plants and the tracker's inputs (identity_chain.json, exclusion_audit.json, the PubMed caches, member_records.json). They don't carry tracker outputs.
- Measured locally with the lane's full rebuild: G1_MATCHED 4 -> 7 (doac-vte, spironolactone-hfref, sglt2-primary-prevention-hf).
- Repo note: `C:\mh-lanes\acq\.git\config` has `core.bare = true`, set at 18:11 on 4 Oct by another process. Plain git commands fail in this clone. The lane commits with explicit --git-dir/--work-tree and has not changed the config.
- For Mahmood, before signing:
  - sglt2-primary-prevention's RESULT_AGREES rests on one small comparable trial (Kosiborod); its large trials are HR-vs-RR measure differences.
  - EPHESUS and CREDENCE are named under the protocol's own population_none terms ('myocardial infarction', 'nephropathy'), while the comparator includes both trials.
- **a327c8041**: registry wording, and posted results as the single primary. The posted N must equal the randomised N. Flips **dapagliflozin-hfpef-hosp** (DELIVER). G1_MATCHED 7 -> 8 locally.

## To the captain / Mahmood: three alerts (5 Oct)

1. **Private paths in git history.** Four codex records added in 90478bedc listed two of the owner's private file paths under `files_read` (paths only, no content).
   - They were quarantined from HEAD in 4e9146610, and the private-content test passes again.
   - They remain in history at 90478bedc. Purging them needs a history rewrite (force-push), which this lane does not do.
   - Root cause is still open: codex reads the owner's global instructions; isolating CODEX_HOME needs a go-ahead.
2. **Disk is full.** C: has 360 MB free and F: has 6 GB. A full worktree of this repo no longer fits, so the lane has stopped sweeps and rebuilds that write into the repo. The lane's own scratch is about 47 MB.
3. **Full local suite: 4751 passed, 16 failed** (MAHMOOD worker unreachable).
   - One failure was the leak above, now fixed.
   - The others are certificate, bundle, gate and production-record checks that compare served certificates with this branch's harness. The pinned blobs differ for files no acq/k-gap commit touched (synth.py, extract.py, screen_entry.py, source_hierarchy.py). They also differ for harness/secondary_meta.py, which this lane changed in e89dfe864 (rounding-envelope control); that change needs re-certification.
   - fixstate fails because `core.bare = true` blocks its git status call.

## To the captain: REVIEW_REFERENCE_LIST is in (5 Oct). The lever was smaller than the forest dispatch estimated.

Built as you specified. Plants: `tests/test_review_reference_list.py` (12). Local counts below are from the lane's own
regeneration; the tracker outputs are not committed, so please regenerate.

**What the route does**
1. **Identification.** Every comparator trial outside our own search now carries
   `identification = {route: REVIEW_REFERENCE_LIST, source_meta, location (table / proposal / label / row context), held_ref, digest}`.
   The identity chain gained a REVIEW_REFERENCE_LIST pass: a PMID/NCT taken from published metas' own reference lists,
   using the forest lane's row-identity map. It needs a reference method (not a tracker join) and one unanimous answer.
   It resolved GISSI-P and GISSI-HF.
2. **Eligibility is ours alone.** `g1_tracker.screen_eligibility` records ELIGIBLE / NOT_ELIGIBLE (rule + reason) /
   NOT_ASSESSED for every trial outside our pool. `is_matched` now refuses any non-pool counted route (SWEEP_*,
   SECONDARY_SINGLE, TWO_SOURCE, PRIMARY-from-a-meta) unless one of these holds:
   - our screen includes the trial;
   - our screen excluded it, but **both** recorded readers (gpt-6-astra and gpt-5.5, verified quotes) judge it eligible,
     with no dissent.

   Each refusal is typed (`count_refusal: NOT_SCREEN_ELIGIBLE:...`). Lane-imported topics get the same state, by
   comparator label, or else by NCT/PMID against our screen's records (tocilizumab's REACT set).
3. **Data never from the comparator.** The forest lane's ACCEPTED dual reads of non-comparator metas now enter
   `secondary_meta_build` as a third meta source, behind the same admission, verification and two-source gates.
   - Rows printed at a 99% CI are refused.
   - Measures are normalised as for our own reads (RATE RATIO → IRR).
   - A row-identity fallback joins rows that our label join misses.

**Two class fixes this exposed**
- **Cross-check disagreements are now settled by the trial's own report.** One dissenting meta used to block rows
  that the primary confirms (colchicine-postop: Tabbalat 13/81, one meta prints 12/81). Rows the typed text or our
  extraction confirms are now PRIMARY_VERIFIED. Dissenters get their MISMATCH and side (PIONEER 6: the comparator
  prints 0.57–1.10, the report 1.11). If nothing matches, the block stands.
- **OTHER_AGENT for ambiguous acronyms.** When every self-naming title names another agent and none names the
  topic's, the trial is named OTHER_AGENT (VERTIS-CV: ertugliflozin; EMPEROR-Preserved: empagliflozin). Which paper
  is the report stays open.

**Numbers (local; 32 topics)**
| | before | after |
|---|---|---|
| G1_MATCHED | 8 | **7** |
| INDEPENDENTLY CONFIRMED | 94 | **92** |
| COVERAGE | 174/366 | **166/364** |

- **REVIEW_REFERENCE_LIST-identified trials: 167.**
  - 25 ELIGIBLE by our screen (3 via both readers: metformin 11238496, 11821265, 15302293).
  - 82 NOT_ELIGIBLE by our protocol.
  - 60 NOT_ASSESSED (no record held).
- **Matched among those 167: 5, all tocilizumab, all already matched before.** The new identification route itself
  newly matched **0**.
- **Newly matched: +6.** All six were identified by our own search; they were blocked only because the forest rows
  never reached the tracker:
  - probiotics +5: Can, Cindoruk (both readers), de Vrese, Duman, Gao;
  - omega3 +1: Rauch 2010.
- **Demoted by the screen gate: −8.**
  - probiotics: Surawicz (X1; both readers CANNOT_TELL).
  - omega3: GISSI-P (X-DESIGN).
  - colchicine-postop: Zarpelon (X-DESIGN); Sarzaeem (no record held → NOT_ASSESSED).
  - dapagliflozin-hfpef: SOLOIST-WHF and SCORED (no identity, no record), plus VERTIS-CV and EMPEROR-Preserved, now
    named OTHER_AGENT and out of N.
- **dapagliflozin-hfpef-hosp G1_MATCHED → NOT_YET.** Its earlier match counted four **other-agent** SGLT2 trials
  (sotagliflozin, ertugliflozin, empagliflozin) in a dapagliflozin-only topic, from one meta's labelled rows with no
  identity. That match was not earned. SOLOIST-WHF and SCORED still need an identity: no topic registers
  sotagliflozin, so the molecule retry cannot name them, and the AACT adapter exposes no interventions.
- **COVERAGE −8:**
  - the screen gate above;
  - omega3 −2: JELIS and GISSI-HF comparator rows are now blocked, because three metas give different numbers for
    "major cardiovascular events" (JELIS 0.81 / 0.94 / 0.92). This is a real outcome-definition disagreement;
  - dapagliflozin's N shrink.

**Why it was smaller than "56 targets"**
The forest lane's gate is not our typed admission. In metformin, pcsk9, ticagrelor and melatonin, almost every
non-comparator row fails on one of these:
- measure (OR/RR vs a registered HR; MD vs OR; SMD read as MD);
- timepoint not stated by the meta (ticagrelor);
- outcome not named in the caption ("forest plot of the included studies");
- 99% intervals (omega3).

Every refusal is typed in `registry/secondary_meta/<slug>.json`. The HR-vs-RR refusals are the decision already
pending with you.

**Recorded calls:** 24 two-reader screen reads (`registry/model_proposals/k_gap_screen_rrl.json`, 31 items × 2).
Leak scan: 82 staged files, 0 hits; the scanner self-tests against planted strings.

**Leak alert, my own (5 Oct):** this dispatch file's alert line, committed in 8cd651a45, named the two private
paths it was reporting. The full-pattern gate caught it before this commit; the line is redacted at HEAD, but it
remains in history at 8cd651a45 alongside 90478bedc, so the same history rewrite covers both. The earlier gate's
pattern lacked the bare names; the lane's scanner now refuses to report clean unless it catches planted copies.
A HEAD-wide scan also finds a private path in `LANE-RB-REPORT.md` (not this lane's file: it names the owner's workbook
path in a 'did not edit' claim). The other matches for the owner's handle are the repository's own public GitHub URLs.
