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
