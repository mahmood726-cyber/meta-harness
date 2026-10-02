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
