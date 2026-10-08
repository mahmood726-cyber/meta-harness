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

## To the captain: the six 5 Oct decisions, applied (typed rules + plants in `tests/test_decisions_5oct.py`)

REVIEW_REFERENCE_LIST was already live (fe689f080, see the section above); these sit on top of it.

1. **HR vs RR.** Already in code and planted (`tests/test_result_agrees_class.py`): a pair-level DIFFERENT_CONCLUSION
   makes RESULT_AGREES false. Nothing changed.
2. **O'Neil 2018 → PROTOCOL_SCOPE_DIFFERENCE by the protocol's own text.**
   - Our screen INCLUDED it; its rule doesn't check dose.
   - `protocols/semaglutide-obesity-weight.md` requires "once-weekly semaglutide 2.4 mg" and excludes "a different
     semaglutide dose … as the randomized arm". The trial's abstract: "All treatment doses were delivered once-daily".
   - AACT NCT02453711 does have posted results: arms Sema 0.05–0.4 mg **daily**, primary outcome at **Week 52**
     (protocol: Week 68). Recorded as a registry note.
   - The mechanism: `registry/scope_adjudications.json`. Every protocol span is verified verbatim against the
     registered protocol, and the trial span against its held record, at every build; a failed span leaves the trial
     eligible.
   - **semaglutide-obesity-weight → G1_MATCHED.**
3. **sglt2-ckd.** Every non-CKD trial is named with both spans.
   - The 6 heart-failure/MI trials now also quote the protocol's X2 bullet (`protocol_span`, a class change: every
     screen-named difference in every topic quotes its rule's protocol bullet).
   - DECLARE, CANVAS and EMPA-REG are newly named. They quote the protocol's I2/X2 population span and their own
     "patients with type 2 diabetes … cardiovascular risk" sentence.
   - N_eligible 6 → 3, all matched. RESULT_AGREES stays unmet: the comparator prints no per-trial rows, and its pooled
     HR covers 12 trials (9 of them non-CKD), so neither comparison is possible.
4. **ELIGIBILITY_UNVERIFIABLE.** Applied when the protocol requires double-blind, the screen excluded on design, the
   audit says BLINDING_NOT_STATED, and the full-text pass didn't establish it. Not counted, not named, stays an open gap.
   - Tsutsui is typed this way, plus 5 more: Zarpelon, Eritsland, JELIS, ticagrelor units 6 and 18.
   - I kept it to blinding as decided. 14 DESIGN_NOT_ESTABLISHED and 18 POPULATION_NOT_STATED records are candidates
     for the same fail-closed state, which is your call.
5. **A comparator row contradicted by the trial's report is compared on the trial's own values**
   (`g1_tracker.trial_report_in_place_of`). It applies only to a verified MISMATCH whose evidence points at the
   comparator; another measure is never converted. The finding stays.
   - **colchicine-postop-af:** Imazio [18] enters on 61/180 vs 75/180 (comparator printed RR 0.66). The same-trials
     result is then **AGREE**: ours RR 0.7055 (0.593–0.839) vs theirs 0.7059 (0.594–0.840).
   - That replaces SAME_CONCLUSION_DIFFERENT_ESTIMATE. Not DIFFERENT_CONCLUSION: that is what the numbers say.
     RESULT_AGREES is now met; the topic is NOT_YET only on ALL_ELIGIBLE_MATCHED.
6. **Licence.**
   - The 9 records are removed from acq/k-gap at HEAD. Their ledger entries are marked QUARANTINED_LICENCE, and
     `registry/record_licence_exceptions.json` has shrunk to 0, with each record listed under `resolved`.
   - The guard (`reproducible_ai/record_licence.py` + `tests/test_record_licence.py`) is brought over from
     g1/finish-line, with finish-line's copy_licence determinations merged into this lane's full-text index (9 PMIDs,
     licence fields only).
   - **At the source:** a model prompt now carries a full text only when its copy is marked CC
     (`secondary_meta_build.prompt_fulltext`, used by the locator and by the exclusion full-text reader); otherwise
     title + abstract. A replay uses only a record made from the identical prompt, so a quarantined record can never
     stand in.
   - **Re-derived or refused:**
     - omega3: VITAL's comparator row loses PRIMARY_VERIFIED (now MEASURE_DIFFERS/unverified). VITAL itself stays
       matched (it is in our pool).
     - Exclusion full text: 36216945 and 31509682 go TRUE_SCOPE_DIFFERENCE → INSUFFICIENT_RECORD (reader refused).
       33625476 is now SCREENER_ERROR by regex on the held copy. No tracker row reads that file.
   - **For consolidation:** the 9 records are still in acq/k-gap's history (30 Sep – 1 Oct). A plain merge carries
     them to main. Keeping them off main needs a tree-level consolidation (squash or curated tree) or a history
     rewrite, which is Mahmood's decision; nothing was rewritten.
   - **Fixed in passing:** `k_gap_exclusion_fulltext.py` crashed on an item with no held record (KeyError 'id_type');
     such items are now typed NO_RECORD_HELD.

**Totals (local, 32 topics):**
| | before | after |
|---|---|---|
| G1_MATCHED | 7 | **8** (+ semaglutide-obesity-weight) |
| INDEPENDENT | 92 | 92 |
| COVERAGE | 166 | 166 |
| eligible | 249 | 245 |

**Full suite on fe689f080's code:** 11 failed, 4772 passed, 72 xfailed (1 h 13 min; temp on C:). All 11 are the
known classes: served CERTIFICATE.json release_sha256, bundle and code-closure pins, and fixstate under core.bare.
`tests/test_architecture_identity.py` was NOT run: it copies the whole registry per test and stalled for over 20
minutes on its second test on this box. It needs the worker or a longer window.

## ACTION REQUIRED, captain and forest lane: acq/k-gap history was rewritten (5 Oct, approved by Mahmood)

**What happened**
- Old tip `d92d07bf4` → new tip `a424d32f7`; force-pushed with `--force-with-lease`.
- The **tip tree is byte-identical** (`247cfc0ad` before and after; `git diff --stat` is empty).
- Only the 121 commits in `origin/main..acq/k-gap` were rewritten. main and everything reachable from main are
  untouched (same merge-base).

**What was removed or changed** (`git filter-branch`, index + message + identity filters; no prune or gc was run)
- **15 files dropped from every commit:**
  - the 9 non-open full-text records (`registry/record_licence_exceptions.json` → `resolved`);
  - 6 records whose codex `client_evidence.files_read` named the owner's private files: the 4 quarantined in
    4e9146610, `registry/model_calls/mc-0125ce41…`, and `evidence/model_calls/secondary/mc-b90b18e8…`.
- **Private paths redacted** to `<private path removed>`:
  - in the historical versions of `registry/model_calls/lane_log/unattributed.jsonl` and of this dispatch file
    (both tip versions were already clean);
  - in 5 commit messages.
- **Authorship:** the 53 "Heldout Test" commits are now the normal identity.

**Verified** (scripts kept locally)
- No dropped path in any commit.
- No private path in any of the 3,006 blobs or 121 messages of the new range.
- All 566 model-call record blobs pass the licence guard (`tests/test_record_licence.py`'s per-record check at every
  commit).
- Commits map 1:1, dates preserved.
- The same check run on the old range FAILS (36 / 13 / 9 hits), so it can detect what it claims to.

**You must re-sync**
- Worktrees on old SHAs: `git fetch origin && git rebase --onto origin/acq/k-gap d92d07bf4 <your-branch>`, or reset a
  pure tracking clone to `origin/acq/k-gap`. Don't merge the old tip back; that reintroduces the files.
- **19 remote branches still reach the old commits, and with them the removed files:** g1/forest-reader,
  g1/finish-line, g1/binding-4topics, consolidate/g1-on-main-2026-10-04, consolidate/g1-2026-10-04,
  captain/cascade-batch, captain/screen-consensus-2026-10-03, g1/colchicine-postop-af, g1/confirm-unverified,
  g1/doac-vte-recurrence, g1/identity, g1/noac, g1/repro-ai-audit, g1/sglt2-primary-prevention-hf, g1/tocilizumab,
  g1/tocilizumab-finish, integrate/g1-identity-2026-10-03, integrate/k-gap-2026-10-02, integrate/k-gap-2026-10-03.
- Until each is rebased onto the new acq/k-gap or deleted, GitHub keeps serving those files through them. This lane
  touched none of them.
- **consolidate/g1-on-main-2026-10-04 in particular must not be merged to main as-is.**
- **main** has one commit message (4e72f7a14) quoting a private-looking path. main was not touched, per instruction.
- GitHub may also keep the unreachable old commits cached until a support purge request; Mahmood can file one.

## To the captain: your 4-item list (5 Oct, evening) — acq/k-gap e99085dd4, fb09edc3b, 71f711eb6

**1. dpp4 (comparator 31462224): 3 of 4 matched. NOT a flip.**
- The comparator switch was ported byte-identical from g1/binding-4topics (topic config, comparators.json, cached
  JATS). `k_gap_table --only=dpp4-mace-t2d` rebuilt only its rows.
- Units: SAVOR-TIMI 53, EXAMINE, TECOS, CARMELINA (+ 9 GLP-1 RA / SGLT2 trials as other agents). A section-header row
  ("GLP-1 RA vs. placebo") had been parsed as a trial and is now never a unit; this was the only such row corpus-wide.
- TECOS: PRIMARY via finish-line's admitted acquisition (posted ITT 3-point MACE HR 0.99, 0.89–1.10, two-sided).
  - **Ported by content, not merged:** g1/finish-line branched from acq/k-gap's pre-rewrite history, so merging it
    would bring back the purged files.
  - aadce1d7a is cherry-picked; `acquired_merge` is ported and now finds an admission by identity, because the new
    comparator renames the units.
- **EXAMINE is blocked, and I did not loosen the gate.**
  - AACT posts HR 0.962 with a one-sided bound only. The ratified rule refuses that ("no two-sided CI"), and your
    finish-line acquisition already named it.
  - Codex sweep over all 10 open metas citing it: 1 forest read (27844335 Fig 2) refused by its positive control; the
    other 9 have no admissible MACE figure.
  - Our screen includes EXAMINE. It is now found by NCT: the comparator cites 25765696, our screen holds 23992602.
- The comparator's own result: **OR 1.00 (0.93–1.07)**, DPP-4 inhibitor vs placebo, from its Table 2 league table.
  - The orientation comes from its footnote and is confirmed against its abstract: the same reading gives GLP-1 RA
    0.87 (0.82–0.93), which the abstract prints.
  - Recorded in `registry/comparator_results.json`. The tracker uses it only because the served page still carries the
    previous comparator (34754403).
- RESULT_AGREES: unmet.
  - The comparator prints per-trial HRs only (Table 1) and pools ORs.
  - Our verified values are HRs, with counts only for SAVOR (AACT 613/8280 vs 609/8212).
  - On the strict reading no comparison on its measure is possible yet.
- **The served page needs the comparator switch as a served change** (it shows 34754403). That's a notice.

**2. omega3 Rauch 2010: not dropped by a rule.** It is matched SECONDARY_SINGLE on acq/k-gap from meta 37031750's
"OMEGA" row (dual-model read, the meta reproduces its own pool). Main's regeneration ran on inputs from before
fe689f080 (the forest lane's non-comparator rows joining the secondary tier). Regenerating from the current tip
restores it, provided the consolidation carries `registry/secondary_meta/*` and the run can reach the forest lane's
branch (the build pins its commit).

**3. tocilizumab RECOVERY: fixed.** Lane files leave `in_our_pool` unset, and our pool keys RECOVERY by its report
(PMID 33933206, trial family NCT04381936).
- `g1_import_lanes.attach_pool_membership` now decides membership by identity (NCT or PMID) against our held-source
  build. An explicit lane value is kept; a disagreement is recorded. Planted.
- RECOVERY is now `in_our_pool: true` (pool row PMID 33933206). The k count is unchanged (it was already counted).

**4. sacubitril Tsutsui: screener error, fixed with a registry span.**
- The record and held full text don't state blinding (no open full text; no PMCID).
- Its registration does: PMID 33731544 → NCT02468232, linked by the title's acronym PARALLEL-HF, which is unique in
  AACT (AACT's study references don't cite the paper). Registered RANDOMIZED, masking QUADRUPLE, official title
  "…Randomized, Double-blind … Active-controlled…". Now ELIGIBLE, with basis
  SCREENER_ERROR:REGISTRY_STATES_BLINDING.
- **Class:** `scripts/aact_designs.py` records the registered design of every blinding-silent exclusion. Registered
  open-label or single-blind → the exclusion stands, with the span (JELIS: NONE; NCT01360437: SINGLE). No unique
  registration → still fails closed (decision 4 unchanged).
- **But Tsutsui has no verified value from an open source.** PARALLEL-HF's own primary composite is posted with HR
  1.088 (0.650–1.821), under a title that never names the outcome ("CEC Confirmed Composite Endpoints"), so it's refused.
- **A gate defect, found and fixed:** the posted "First **Triple** Composite (CV death, HF hospitalization, or worsening
  of HF in outpatients)" was BINDABLE against our two-component outcome. A composite that declares more components than
  the protocol's now never binds.

**Recount (local, 32 topics):**
| | before | after |
|---|---|---|
| G1_MATCHED | 9 | 9 |
| INDEPENDENT | 91 | 91 |
| COVERAGE | 165/362 | 165/361 |
| eligible | 241 | 240 |

None of the four items flips a topic under the strict definition.
- **Codex:** 1 forest read this round. The other routes were decided by typed sources (registry, PubMed metadata, the
  comparator's JATS).
- **Worker:** unreachable (SSH and Tailscale ping time out).

## To the captain: Tier B codex fan-out + REGULATORY route (5 Oct, night) — acq/k-gap 67978d5d7, f2f3b8df9

**Headline (local recount, 32 topics):** G1_MATCHED 9 (unchanged), INDEPENDENT 92/361 (+1), COVERAGE 164/361 (−1),
eligible 239 (−1). Please regenerate the served tracker from the tip; this lane does not commit tracker outputs.

**Fan-out.** One codex job per NO_ROW / UNVERIFIED / SECONDARY_SINGLE trial in the 7 Tier B topics:
- 60 targets → 32 recorded calls (gpt-6-astra, concurrency 3) + 28 with no open source (no call made).
- The commit message for f2f3b8df9 says "45 calls / 15 no source". That is a miscount; **32 / 28** is right, counted from the run logs.
- Worker still unreachable. Codex liveness was checked by a real exec, not a status page.

| topic | targets | admitted | outcome |
|---|---|---|---|
| iv-iron-hfref-hosp | 4 | 2 | **HEART-FID → PRIMARY** (AACT ITT 297/1532 vs 332/1533); matched 1→2 of 5. **AFFIRM-AHF** admitted (AACT HF hospitalisations 142/558 vs 178/550) but now NAMED `ESTIMAND_DIFFERENCE`: the comparator pooled *HF hospitalisation + CV death* (217/558 vs 294/550). A named row is never merged. |
| pcsk9-mace | 9 | 0 | Lipid trials post no MACE; HIGH FH 6/72 vs 0/35 refused (`TYPED_MATCH_NOT_FOUND`); ODYSSEY trials are named only in the EMA EPAR (held, never shown) |
| tocilizumab-covid19-mortality | 16 | 0 | Posted outcomes without counts; CORIMUNO HRs without group labels → UNSURE; REMDACTA HR refused `AACT_OUTCOME_NOT_NAMED` |
| corticosteroids-cap / -covid19 | 7 / 3 | 0 | No posted results and no CC full text |
| colchicine-secondary | 8 | 0 | Same; Shah refused because AACT posts a stent subset only |
| omega3 | 13 | 0 | 12 have no open source; Pahor's AACT outcome is mobility disability |

**REGULATORY route (new, PRIMARY-grade).**
- *Source records:* drugs@FDA NDA/BLA reviews and EMA EPARs, held as typed records (`registry/regulatory_sources.json`):
  - agency and licence come from the url host only;
  - each record carries the PDF sha256 and the text sha256.
- *Gate:* a regulatory value is admitted only if all of these hold:
  - the quote is verbatim in the **whole** document;
  - every number is in the quote;
  - the trial is named near the quote (another study's row is refused);
  - the typed tuple sits beside the outcome terms.
- *Licence guard:* only FDA windows may enter a prompt. A prompt's own licence claim counts for nothing.
- *EMA (for Mahmood):* the licence is "reproduction authorised with acknowledgement", which is not marked open, so EMA documents are held but never shown. Decide whether EMA may enter prompts.
- *Yield so far:* 30 FDA and 13 EMA texts are held. No prompt-open document names a target trial beside its outcome terms, so this round had no regulatory admissions. Actemra's COVID-19 sBLA review is missing from openFDA's application_docs.

**Defects fixed (root cause, with plants):**
- The tracker table crashed on full regeneration. The 5 Oct PROTOCOL_TEXT adjudication record lacked `screen_reason`, and `SAME_TRIAL_AS_ANOTHER_UNIT` fell into the registry-gate branch.
- Fix: one renderer per kind, with a plant that checks it over every real per-topic record.
- Note: `python scripts/g1_tracker.py` with no slugs only re-renders the existing files. Pass the slugs to regenerate.

### Follow-up (same night): two-source sweep on Tier B — 83c701809, af2c6bfb0

**Run.** `g1_two_source_sweep --run --need=4` over the 7 topics:
- 4 new recorded forest reads. The planner found few unread candidate figures.
- **GISSI-P 1999 → SWEEP_SECONDARY_SINGLE** (meta 23335472 Fig 2, RR 0.98 (0.88–1.09)). It is not matched: our screen excludes it on design (`X-DESIGN`).
- The headline is unchanged: G1_MATCHED 9, INDEPENDENT 92/361, COVERAGE 164/361.

**Regression found and fixed (with a plant).** The sweep counted forest rows only from the *current run's* read plan.
- A re-run with another `--need` dropped Nilsen 2001's verified row (meta 39639295, a held read), and omega3 fell from 6 to 5 matched.
- Now the plan decides what is read; every held, gated read is counted.
- Held reads also surface 16 more candidate rows (ROWS_NOT_VERIFIED 13 → 29). None is verified yet; these are second-source targets.
- **Captain:** if you re-sweep from main before consolidating, take `metas_to_count` with it, or omega3 drops a match.

**Ordering note.** Run `g1_tracker <slugs> --no-table` → `g1_import_lanes` → `g1_tracker --table`.
- Rendering the table before the import shows noac, tocilizumab and sglt2-hfref from our own pipeline instead of their lanes.
- That ordering briefly read N=348 and G1_MATCHED 7 here; it was not a data change.

**Leak hygiene (for Mahmood).**
1. *Lane-log writer.* The lane-log writer (`reproducible_ai/model_call_live.transcript_facts`) redacted only the work dir.
   - A forest read's client, steered by its own global AGENTS.md, ran commands naming private local files. Every command was rejected by the sandbox.
   - Those paths reached the uncommitted lane log. The leak scan caught them, and the line was redacted before commit.
   - The writer now keeps `<local-path>/<file name>` only. There is a plant for it.
2. *Fixture on main.* `tests/test_codex_call_log.py` carried a real home-directory path in a fixture. It came from c82e86bd7 and **is on main**.
   - Neutralised on this lane (af2c6bfb0), so it drops out at the next consolidation.
   - main itself is untouched by this lane.

### Follow-up 2 (same night): counts re-reads and call-log privacy (5b765b8be)

**Counts re-reads.** The per-arm counts re-read now also runs for planned (caption-selected) forest figures, with gates unchanged.
- 9 recorded reads.
- In corticosteroids-cap, meta 23112872's counts attach to 4 of 8 rows. Only counts that reproduce the printed OR attach.
- Those rows now pass the measure gate. They stop at `TIMEPOINT_NOT_STATED_BY_META`: the meta never states the mortality timepoint.
- No count moved.

**Where Tier B stands after tonight.** Under unchanged gates, Tier B is exhausted:
- 60 acquisition calls and 3 sweeps: the open-meta pool is fully read (67 held forest reads; the remaining planned metas have no readable figure).
- Every unmatched row is now one of:
  - (a) no open primary source;
  - (b) refused by a measure gate (meta RR vs topic OR/HR: 26 of 31 candidate rows);
  - (c) refused by a timepoint gate;
  - (d) screen-excluded (GISSI-P, design).
- tocilizumab is served from the g1/tocilizumab lane import, so this lane's tocilizumab reads don't move the served row.

**Decisions only Mahmood can make (none taken here):**
1. **EMA EPAR text in prompts.** The licence is "reproduction authorised with acknowledgement". It is held, never shown. Allowing it would open the ODYSSEY rows (pcsk9) to the regulatory route.
2. **Meta with no stated timepoint.** Should a meta that states no timepoint be admissible when the trial's own report states one? This is the cortico-CAP rows' only remaining refusal.
3. **Codex client reading private files.** Codex's client reads its user-level AGENTS.md and acts on it inside harness calls:
   - 5 Oct: it read a private workbook during a forest read (read-only sandboxes allow reads).
   - Committed logs no longer keep tool output (fixed and planted).
   - The calls themselves should run with user-level client instructions disabled, or in a sandbox with no access outside the work dir. That is a harness-wide setting, so it is not changed by this lane.

## To the captain / Mahmood: full-cascade burn, round 1 (6 Oct) — acq/k-gap 72f4c40c1 … 325049569

### Licence finding (needs Mahmood): 44 committed records carry non-CC full text — none on main

The guard missed a prompt shape: whole-text `<<<TEXT … TEXT>>>` blocks.
- These come from 4 scripts: `k_gap_upw_locate` 13, `g1_table_locator` 19, `k_gap_propose_members` 9, `k_gap_result_agreement` 3.
- The texts are NEJM, JAMA and other non-CC copies; 7 of 8 unrecorded PMC licences resolved to NOT_OPEN.
- All 44 are listed in `registry/record_licence_exceptions.json`, so consolidation excludes them.
- 12 of them fed comparator-membership identification and result agreement. Those are derived facts, not copied numbers, so the rows are kept.
- **Quarantine or a history rewrite is Mahmood's call.**

**Prevention.** `model_call_live.call` now runs the licence guard on the would-be record before sending (`LicenceRefused`). The guard resolves every declared source to a licence from held data.

### What the cascade now does

**Order:** AACT → PMC → Unpaywall (shown only if CC) → FDA reviews and labels → EMA (shown with an acknowledgement, on Mahmood's word) → NICE → independent metas (the two-source sweep).

**NICE:**
- Typed discovery:
  - TA: committee papers (ERG/EAG) and the FAD;
  - NG/CG: evidence reviews.
- Every NICE document held so far states notice-of-rights, not OGL/CC (215 texts). They are read only by the typed extractor and never shown to a model.

**Typed first:** a model is called only where typed extraction finds nothing.
- The trial's own open held text: its outcome-table row.
- A regulator's counts: one trial-named line with two percent-corroborated `e/N (p%)` cells, arms taken from a header naming both.

**Regulator gate:** a figure must match the estimand, population and timepoint, be verbatim, and carry the trial's randomised N; a subpopulation is refused.

### Round 1 run

**Scope:** all 32 topics, 5 workers. The worker box has no codex CLI and no credentials, so it is idle; giving it codex needs Mahmood.

**Trials:** 157 → 50 recorded calls (10 carried FDA/EMA windows) + 107 with no open source.
- Of the 107: 62 have a PMID but are paywalled, with no posted results and no open copy; 45 have no PMID.

**Admitted:** 3.
- HEART-FID and AFFIRM-AHF, as before.
- SALT (balanced crystalloids), from posted counts. The ratified unit-of-analysis gate then refuses it: cluster-crossover, unadjusted.

**Defect fixed (with a plant):** replay rewrote acquired files from this lane's proposals alone. That dropped TECOS (dpp4), and INDEPENDENT read 91 until it was fixed.

**Recount** (tracker → lane import → table): G1_MATCHED 9, INDEPENDENT 92/361, COVERAGE 164/361, eligible 239.

**In progress:**
- the all-topic two-source sweep (5-wide, up to 200 forest reads);
- regulatory holding for every topic;
- then round 2, which re-asks every trial whose evidence changed.

### Full-cascade burn, rounds 2–3 (6 Oct, night) — acq/k-gap 7909cd618 … a5776a029

**Denominator fix.** statins-elderly had 15 QRISK strata rows from one cohort study, each parsed as a trial unit.
- Corpus N goes from 361 to **346**, and eligible from 239 to **224**.
- A plant guards it.
- statins-elderly now has 12 units, all named scope differences. Its state still reads ALL_ELIGIBLE_MATCHED unmet with 0 eligible. That's the tracker's state rule, which I haven't changed; it's yours to decide.

**Regulatory holding.** All 32 topics: 1,250+ typed source records (FDA reviews and labels, EMA EPARs, NICE). Every NICE document states notice-of-rights.

**Codex calls.**
- Totals: round 1 had 50 calls, round 2 had 13, round 3 had 9, and the all-topic sweep made 6 forest reads (the open-meta pool is exhausted).
- Unchanged evidence was never re-asked.
- No call was made for a trial with no open source.

**The regulator route reaches the trials; the gates hold.**
- EMPACTA and REMDACTA: FDA gives mortality for the treated mITT subset only, so it is refused.
- EXAMINE: FDA gives a 98% CI, not a two-sided 95%, so it is refused.
- ASCEND: the EMA window gives no number.
- No typed (no-model) regulator admission anywhere in the corpus.

**Recount.** G1_MATCHED 9, INDEPENDENT 92/346, COVERAGE 164/346, eligible 224.

Per topic: tocilizumab-covid19-mortality NOT_YET indep 5/19 matched 5/19; balanced-crystalloids-vs-saline-mortality NOT_YET indep 0/6 matched 0/5; colchicine-postop-af NOT_YET indep 2/9 matched 2/5; colchicine-recurrent-pericarditis NOT_YET indep 1/5 matched 1/1; colchicine-secondary-cv-prevention NOT_YET indep 2/15 matched 2/10; corticosteroids-cap-mortality NOT_YET indep 3/11 matched 3/10; corticosteroids-covid19-mortality NOT_YET indep 2/5 matched 2/5; denosumab-vertebral-fracture COMPARATOR_NOT_ENUMERATED indep 0/0 matched 0/0; dpp4-mace-t2d NOT_YET indep 3/4 matched 3/4; empagliflozin-hfpef-hosp NOT_YET indep 0/3 matched 0/2; esketamine-trd-madrs NOT_YET indep 3/6 matched 3/5; iv-iron-hfref-hosp NOT_YET indep 2/5 matched 2/4; melatonin-primary-insomnia-sol NOT_YET indep 1/19 matched 1/9; metformin-pcos-ovulation NOT_YET indep 3/41 matched 3/33; omega3-cardiovascular-events NOT_YET indep 6/28 matched 6/18; pcsk9-mace NOT_YET indep 2/12 matched 2/11; probiotics-aad-prevention NOT_YET indep 19/41 matched 19/41; sacubitril-valsartan-hfref NOT_YET indep 1/9 matched 1/2; semaglutide-obesity-mace NOT_YET indep 1/10 matched 1/2; sglt2-ckd-progression NOT_YET indep 3/12 matched 3/3; statins-primary-prevention-elderly NOT_YET indep 0/12 matched 0/0; ticagrelor-vs-clopidogrel-acs NOT_YET indep 1/22 matched 1/3; tranexamic-acid-pph NOT_YET indep 1/5 matched 1/1

**Where codex can't help without your call:**
- 107 trials have no open primary source: 62 are paywalled with a PMID, the rest have no PMID.
- 26 of 31 sweep candidate rows are refused because the meta's measure differs from ours.
- Timepoint-silent metas (cortico-CAP) are refused.
- 2 scope candidates have verbatim spans but no consumer yet: Zarpelon [20] in colchicine-postop-af ("prospective, randomized, open"; the protocol requires double-blind), and esketamine Trial B.
- Four topics have every eligible trial matched and fail only RESULT_AGREES: colchicine-recurrent-pericarditis 1/1, sglt2-ckd 3/3, tranexamic 1/1, dpp4 3/4. That is a result-agreement question, not acquisition.

### 6 Oct, evening: rebase, worker slots, second readers — acq/k-gap 2b5b344bc … 47762a20

- **Rebase.** `git fetch` showed that origin/acq/k-gap had **not** been rewritten (it equalled the local HEAD c9a757e0b).
  - Uncommitted lane files were committed and pushed first (2b5b344bc); the tracker outputs were saved as a local patch.
  - Then I ran `reset --hard origin/acq/k-gap`. A local backup ref exists: `backup/acq-k-gap-pre-reset-2026-10-06`.
- **Worker.** Codex is now installed and authenticated on the worker, and `reproducible_ai/model_call_remote.RemoteCodexRunner` runs calls there.
  - The call itself is identical and sandboxed.
  - Prompts, the licence guard, the gates and the records all stay on this box.
  - Each record names `codex@worker`, the worker's codex version and the worker's AGENTS.md digest.
  - Runs used 5 local slots and 5 worker slots.
- **Second independent reader.** gpt-5.5 reads every row that would bind.
  - A row binds only when both readers pass the gate with the same tuple. A split gets one retry from reader 1.
  - Readers ran on every sourced run: 52 reads, 23 of them on the worker.
  - **There were 0 splits.** Reader 2 never found a bindable tuple that reader 1 had missed.
  - HEART-FID binds with two agreeing readers.
  - AFFIRM-AHF is refused by reader 2. It was already named as an estimand difference.
- **Defect fixed (with a plant).** At 10 workers, `fulltext_index.json` was being read while only half written, and concurrent writers were losing each other's updates. Index writes are now locked, atomic and per key; evidence building is serialised.
- **Recount.** G1_MATCHED 9, INDEPENDENT 92/346, COVERAGE 164/346, eligible 224. Unchanged.
- **Spend.** Codex use is limited by evidence, not by capacity.
  - This round made 58 calls; tonight's total is about 150.
  - The no-source trials (107) and the measure- and timepoint-gated rows can't move without a decision from the captain or Mahmood. The decisions are listed in the earlier sections.

## 2026-10-07 -- extractor misattribution fixed (held for Mahmood); acquisition on the adopted comparators

**Job 1: extractor misattribution (93e40ef41).**
- This is one batched change to `harness/extract.py`, which is PINNED.
  - It re-certifies every page.
  - Where it moves a served number, it is held for a notice that Mahmood signs.
- It also touches `harness/pipeline.py`, a **main-lane file**. The only edit passes `outcome_name=spec["name"]` into the extractor.
- **Fixes, each planted on the real adjudicated sentence** (`tests/test_extract_misattribution.py`, 11 tests; all fail on the old extractor and pass on the new):
  - **First-HR-in-sentence.** The effect is now read from the clause that names the outcome; doac 19966341 "any bleeding" reads 0.71 (was 0.82).
    - Measure words such as "hazard ratio" never decide which clause is chosen.
    - With no outcome clause, the one clause naming our intervention wins.
    - If neither applies, the first effect is kept, as before.
  - **Broader outcome.** Sentences that carry the outcome name are read first, and that reading is kept only if it yields a value. Probiotics 15740542 AAD reads 4/119 vs 22/127.
  - **Total-as-arm.** A group equal to the sum of the other two is dropped. Probiotics 39529939 reads 7/285 vs 3/279, never the 10/564 total.
  - **Factorial trials and bare CIs.** Omega3 21115589 (SU.FOL.OM3) reads HR 1.08 (0.79–1.47) for the omega-3 factor; a clause about the co-randomised factor never counts.
  - **Also fixed:** number-word counts ("seven of 44"), slash composites (HHF/CV death), and a single outcome inside a composite sentence (CANVAS 0.67).
- **Radius.** 85 of 10,098 extractions change (76 without the name).
  - **7 served values would move**, and every one equals the adjudicated value:
    - doac 19966341: 0.82 → 0.71;
    - omega3 21115589: refused → 1.08;
    - probiotics 15740542: → 4/119 vs 22/127;
    - probiotics 18026577: → 7/44 vs 16/45;
    - tocilizumab 33631066 SAE: → 103/295 vs 55/143.
  - **Not applied to served pages; needs Mahmood's notice.** Report: `outputs/regex_layer/RADIUS_misattribution_2026-10-07.json`.
  - **Caveat.** The radius tool reads raw JATS where the producer reads the converted text. The one no-name difference that comes from this (omega3 0.88 on raw XML) is a radius-tool artefact, not a served move.
- **Burn-down.** 5 of 15 hand-entered values are now reproduced by the extractor from a held document; the read, its sha and its span are in `registry/provenance_extractor_reads.json`.
  - Retired: probiotics 39529939 AEs; CANVAS 28605608 (0.67); VERTIS 32966714 (0.70); tracker rows Radholm (9) and Cannon (11).
  - Not retired (10):
    - EMPA-REG 26378978: its sentence runs on past a citation, so it is read as a subgroup sentence and picks loop diuretics 0.62. Fixing that would mean another change to the pinned extractor; I have not made one.
    - The adverse-event count rows: no single extractable span.

**Job 2: full-cascade acquisition on the adopted comparators (27e74015d).**
- Comparators covered: denosumab 32492050, melatonin 35691474, statins 32529863.
  - doac-vte-recurrence 29795629 is picked but not adopted yet, so it was not run.
  - dpp4 and esketamine adoptions are outside the 12 active topics.
- **8 target trials** (the population comes from the v8 tracker files):
  - **4 had an open source.** Each got reader 1 and reader 2 (8 calls, 5 local + 5 worker slots); all came back SOURCE_ABSENT:
    - Bone 2008: AACT posts bone density only;
    - CARDS aged 65-75 and ASCOT-LLA older: regulator text covers the whole trial, not the older subgroup;
    - ALLHAT-LLT older: no open source.
  - **4 had no open source** (no call made): Dawson 1998, James 1990, HPS diabetes, MEGA older.
- 0 rows admitted. Licence: 0 problems. Leak gate: clean.
- **Recount unchanged:** G1_MATCHED 9, INDEPENDENT 92/346, COVERAGE 164/346.
- **Watching.** The binding lane is re-screening statins, melatonin and denosumab (`@r2`). I will run the cascade on any new adoption, and on doac when its adoption lands.

**doac-vte-recurrence adoption (comparator 29795629, ed5be6dc4).** No acquisition was needed.
- All 5 trials in its set are already bound PRIMARY in our pool: RE-COVER, RE-COVER II, Hokusai-VTE, AMPLIFY and EINSTEIN-DVT.
- So there were 0 targets and 0 calls.
- Its G1 standing now depends only on the tracker being regenerated against 29795629, which is the captain's step.

## 2026-10-07 -- open-source routes (Mahmood: "any other open access sources but use in reproducible ai") (be45bfb45)

**Method.** The population is the 16 open-gap trials across the 12 active topics, taken from the v8 trackers.
- I probed every candidate route against each of those trials before building anything.
- I built only the routes that had candidates.
- Each route has a typed source record, deterministic reading first, the licence guard, and a plant (`tests/test_open_sources.py`, 13 plants).

**Admitted n per route:**

| Route | Admitted | Notes |
|---|---|---|
| OPEN_LOCATION (OpenAlex / Semantic Scholar) | 0 | No new CC copy. The licence of record is read from the host page's own licence tag, never from the index field: OpenAlex calls REMAP-CAP's JAMA copy cc-by, and JAMA answers with a bot challenge. 4 bot challenges recorded, none solved. |
| Regex first: the pinned extractor on held CC text, through `gate()` exactly like a model answer | **1** | Tsutsui 2021 (PARALLEL-HF), HR 1.09 (0.65–1.82), from a CC BY-NC-ND copy. |
| Stated registration (the one NCT a report prints) → AACT | 0 | Added NCT02468232 (posted results). |
| EUCTR (typed only) | 0 | 3 result pages held: EFFECT-HF (HF hospitalisation posted as percentages only; the time-to-event result is a composite), semaglutide phase 2 (no MACE), AFFIRM-AHF. |
| CTIS | 0 | REMAP-CAP has no results posted. |

**Decision needed.** Tsutsui is admitted by the gates, but reader 1 had refused it on population grounds.
- Its result is on the FAS, 223 of the 225 randomised. The other 2 were randomised by mistake and never treated.
- The text gate has no population rule for effects, and 223/225 sits well inside the 10% randomised-N tolerance used elsewhere.
- Please adjudicate: keep it, or name it as a population difference.

**EU CTR licence.** The register defers to EMA's legal notice, and that notice's permission "does not apply to content supplied by third parties". Results are entered by the sponsor.
- So EU CTR content is THIRD_PARTY_SPONSOR: it is read by the typed parser only and never shown to a model.
- The parser maps results into the AACT registry shape. They pass through `registry_gate`, which is the AACT branch factored out with unchanged behaviour.
- The EU CTR search does not index NCT numbers, so that fallback finds nothing. Discovery is by the EudraCT numbers in AACT.

**Probed but not built (0 candidates among the 16):**
- Europe PMC full text duplicates PMC.
- No medRxiv or other preprints exist for these trials.
- Zenodo, Dryad, Figshare and OSF (via DataCite) have nothing relevant.
- ISRCTN has no numeric results for these trials.
- PMDA has no Entresto review; its Prolia and Wegovy reviews don't cover our outcomes.
- I found no IQWiG, ICER or FDA advisory-committee document covering these trials.
- TGA timed out.
- CADTH answered with a bot challenge.
- Sponsor pages would duplicate AACT or the paper.

**Excluded because they need an account or a data-use agreement** (listed for Mahmood, not used): Health Canada PRCI, the EMA clinical data portal, YODA, Vivli, CSDR, Project Data Sphere, the CORE API (needs a key), and the WHO ICTRP web service (partner-only).

**Other changes:**
- `record_licence` checks an open-location copy against that copy's own record, never against the DOI.
- Admitted text rows now name the copy the text came from. Before this, an Unpaywall copy was labelled "PMC OA". Replays will rewrite those labels; no values change.

**Calls:** 2 (CoDEX, readers 1 and 2: SOURCE_ABSENT). Licence: 0 problems. Leak gate: clean.

**Recount:**
- COVERAGE 165/346 (+1); INDEPENDENT 93/346 (+1); G1_MATCHED 9.
- sacubitril-valsartan-hfref is now 2/9 matched, which meets ALL_ELIGIBLE_MATCHED. RESULT_AGREES stays open because the comparator prints no row for PARALLEL-HF.

**What remains.** The other 15 gap trials have no open source on any route: the older-subgroup statin papers, the 1990s melatonin trials, and the COVID steroid trials, whose texts sit under the emergency licence, which is not CC.

## 2026-10-08 -- gap-list share: D8 + quarantine, sacubitril identity join, routes ledger, V10 proposals

**V10, flip-ready on one decision: denosumab-vertebral-fracture / Bone 2008 (PMID 18381571).** Add the drafted entry to `registry/scope_adjudications.json`. It is in `outputs/k_gap/notices/V10_SCOPE_ADJUDICATIONS_2026-10-08.json`, spans verified against main.
- **The spans.**
  - Protocol: "postmenopausal women with osteoporosis."
  - Held abstract: "Subjects included 332 postmenopausal women with lumbar spine BMD T-scores between -1.0 and -2.5."
  - That band is osteopenia. The Prolia EPAR describes study 20040132 identically and calls it a prevention study.
- **Effect.** RESULT_AGREES is already met (FREEDOM). Eligible becomes 1/1 and the divergence is named, so **denosumab flips** (11 of 22 active).
- **Why there is no count route.** Every open route is recorded, none with a count: AACT is BMD only; the EPAR names 20040132 seven times with no fracture count; PMDA has only the 2017 RA review. The OA copy and ANZCTR/CADTH answered with bot challenges, jRCT refused TLS, TGA was unreachable, and CORE needs an account.

**V10, not flip-ready alone: semaglutide-obesity-mace / O'Neil 2018.**
- **Correction to CLOSE-4.** No dated amendment is needed. The registered protocol's I line already says "once-weekly subcutaneous semaglutide 2.4 mg added to standard care." Against O'Neil's "All treatment doses were delivered once-daily via subcutaneous injections.", this is the same decision-2 protocol-text route that semaglutide-obesity-weight uses. The draft entry is in the same file.
- **Caveat.** The MACE protocol's exclusion list, unlike weight's, doesn't name "a different semaglutide dose". The entry rests on the I line alone; your call.
- **What is still missing.** RESULT_AGREES needs SELECT counts (binding) plus D12.

**sacubitril-valsartan-hfref: identity join done (125802eb5).** `registry/identity_links.json` links PMID 33731544 to NCT02468232 on two typed facts, each with span and digest:
- the report's own open text states exactly one NCT, "...Japanese HFrEF Patients (NCT02468232)...";
- the title acronym PARALLEL-HF equals the CT.gov acronym.

`scripts/g1_identity_links.join()` joins only to a registration already pooled. The tracker change is a 2-line hook after the SCREENED_VIA_OTHER_REPORT loop; **please port it to main's g1_tracker** (my lane's tracker is older).
- **Result.** Tsutsui becomes PRIMARY through the served row, HR 1.0881 (0.6501–1.8212). ours_not_in_comparator becomes empty.
- **Still not flip-ready.** RESULT_AGREES stays unmet: the comparator is an NMA with no per-trial rows. The unsigned PARALLEL-HF screen notice is no longer needed for the match, because the join goes through the registration we already pool.

**D8 in acquisition (1162f4121).**
- **Prompt side.** `g1_licence.py` (ported unchanged): CC BY / CC0 article, open copy, unknown counted as closed.
- **Reader side.** Unchanged: a CC copy or a PMC author manuscript, never bronze. D8's text is "no paywalled text, even by a regex reader".
- **Audit of all 5484 tracked records.** 12 carried full text of non-CC-BY/CC0 articles: ODYSSEY FH I/II (CC BY-NC), TRANSFORM-1 (CC BY-NC) and PARALLEL-HF (no licence).
  - All 12 are removed from acq/k-gap, and their ledger entries are marked QUARANTINED_LICENCE. No admitted row rested on them.
  - **Two of them are on main: mc-2249c745cf51bbc0, mc-3c1d4445e0c6a231. Please quarantine them there.**
- **Standing plant.** `tests/test_d8_records.py`: every tracked record, offline, with an uncached licence counting as closed.

**Fetch fix, cascade, cortico re-fetch.** You had already done all three (ea493ea5d / fd4901b76). I stopped my duplicate and committed none of it.

**Routes ledger (a13479fa5).** `cache/<slug>/routes_ledger.json` covers all 12 topics, 17 unmatched trials, with one recorded attempt per host (`registry/route_attempts.json`):
- ANZCTR: BOT_CHALLENGE (a Cloudflare managed challenge);
- jRCT and RCT portal: TLS_REFUSED (both TLS stacks);
- TGA: UNREACHABLE after backoff;
- CADTH: BOT_CHALLENGE;
- CORE: account only.

0 admitted.

**Codex.** 0 calls this round: no new route produced a text a prompt may carry. The local level would be 2 (2.6 GB RAM free, C: 7.7 GB); the worker is offline.

## 2026-10-08 ~21:00 -- "use codex hard": ENGAGE CI FOUND; cortico final; sglt2-ckd queued behind the disk floor

**ENGAGE D16 C: FOUND** (`outputs/k_gap/engage_ci_search.json`). Regex first over held, digest-checked texts; no model call was needed.
- **Source.** EMA Lixiana EPAR, EMA/321083/2015 pp. 67–68, held under EMA reuse with acknowledgement. Text sha256 e1053560fe5a573e38bc9f8f8a7d8b9e21f93be1b019ec14a6a6d21449d9c0df; doc sha256 e760300757ee0087….
- **Heading:** "c) Stroke and SEE - Superiority, ITT, overall study period (study protocol):"
- **Span:** "In the ITT population (Overall Study Period), f ewer subjects in the edoxa ban 60 mg group experienced stroke or SEE than the warfarin group (1.57% and 1.80% per year, respectively), with an HR of 0.87 (99% CI: 0.709, 1.068, 95% CI: 0.744, 1.017) but the p-value (p=0.0807)"
- **Same arm, analysis and outcome.** Edoxaban 60 mg (the high-dose regimen) v warfarin; ITT; stroke or SEE. The paper's ITT superiority analysis is itself the overall-study-period analysis: same HR 0.87, P=0.08 v p=0.0807. So the dispatch's "overall-period" refusal example does not apply here; please confirm.
- **Bounds 0.744–1.017.** Our served conversion is 0.745–1.016, a rounding difference only.
- **Corroboration.** The Savaysa 2023 label (s020) subgroup figure prints "Hazard Ratio and 95% CI … Overall 296/7035 (1.57) 337/7036 (1.80) 0.87 (0.74, 1.02)". Its text layer is damaged, so it serves as corroboration only.
- **Refused:** the labels' overall "HR (99% CI): 0.87 (0.71, 1.07)" and NICE's network estimates.
- **Not reached / not open:** PMC (none); the repository copy (no licence); the FDA reviews (not held; not needed).
- **Next.** Yours: a before/after notice for Mahmood.

**cortico re-run** (CAPE COVID 32876689, REMAP-CAP hydrocortisone 32876697, Metcovid 32785710): **NO_OPEN_TEXT, final** (`outputs/k_gap/cortico_cascade_rerun_2026-10-08.json`).
- The Europe PMC 500 is article-specific: the control PMC5642327 answers 200.
- PMC has no body for any of the three, Europe PMC records no licence, and the publisher PDFs answer 403.
- D8 would close any copy anyway.

**sglt2-ckd CC BY alternative: queued, not run.**
- **What's left.** In `registry/comparator_selection/sglt2-ckd-progression.selection.json`, 39 candidates pass C1 (a CC BY Unpaywall location) and fail nothing. They were never read: C2–C6 are "not read: no open JATS", because they have no PMC copy.
- **The job.** Hold each CC BY copy (host-page licence; D8 prompt rule CC BY / CC0), then run one recorded codex read per candidate on the pre-registered rule at concurrency 8, every PASS gated on a verbatim quote, then the deterministic select.
- **BLOCKED:** C: has 3.7 GB free, under the 5 GB stop line; RAM is 1.8–2.1 GB and the worker is offline. My lane holds about 0.5 GB on C:, so I can't clear it. C:\mh-tmp\captain holds 9.8 GB. **Can you free C: to at least 5 GB (ideally 10 GB, for the ceiling of 8)?** I start the moment it is clear.
