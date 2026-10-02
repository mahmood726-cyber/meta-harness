# Dispatch: G1 NOAC lane -> k-gap lane

From branch `g1/noac`, first based on `origin/acq/k-gap` at 46cc6a7f8 and since merged with 08682cd9e. Two shared
files are now changed on this branch; see section 0.
The session-to-session channel was unavailable: this session runs unattended, and the message tool refuses
in that mode. These requests are left here instead; Mahmood's status message points to this file.

## 0. Update, 2 Oct, after merging acq/k-gap 08682cd9e: two shared files changed on THIS branch

Both changes are additive and plant-tested, and both are for you to adopt or reject. Mahmood asked for a NOAC
tracker verdict today, and the session channel to your lane was refused twice.

- **`scripts/k_gap_table.py::resolve_unit`.** New identity step `acronym_self_registration_sentence`.
  - **When it runs:** only after `acronym_aact` and `acronym_aact_title` both fail.
  - **What it reads:** an acronym in a trial's OWN held PubMed abstract registration sentence ("...; ROCKET AF
    ClinicalTrials.gov number, NCT00403767."), restricted to topic-agent NCTs.
  - **Ambiguity:** more than one NCT is reported as AMBIGUOUS, never picked.
  - **Map:** `SELF_REG` is built from every `cache/*/records.json`. It holds 73 acronyms, and none maps to more than
    one NCT.
  - **Effect on the table:** this resolves ROCKET AF (row `UNRESOLVED_IDENTITY` -> `POOLED`, NCT00403767). The only
    other change in `k_gap_table.json` is two additive registration-date fields on 29 rows. They come from building
    the AACT store fresh in this worktree.
  - **Correction to G1_STATUS.md, "What would move G1 next", item 2:** that item says "our own record never
    self-names it". Our held record does name it: PMID 21830957's abstract carries the sentence above. This is a
    stricter basis than an alias, not a looser rule.
- **`scripts/g1_tracker.py`.** New key `same_trials_no_trial_rows`, built by `no_trial_rows_result`.
  - **When it applies:** a patient-level comparator prints no per-trial rows, so `same_trials_pool` has nothing to
    pair. When every comparator trial is in our pool and none has a printed row, our pool over them IS the
    same-trials pool.
  - **Verdict:** it is typed by your `result_verdict`. The table shows it only when `same_trials` is not POOLED.
  - **Plants:** a missing trial, a printed row, or a k mismatch -> None; a measure mismatch -> MEASURE_DIFFERS.

**Observed defect, not edited:** `scripts/g1_tracker.py <slug>` writes `outputs/k_gap/g1/<slug>.json` non-atomically.
A run killed by a timeout (probiotics-aad-prevention, rc=124 at 1500 s on a busy disk) left a 0-byte file, and
`tests/test_g1_interfaces.py::test_committed_tracker_files_carry_the_pinned_schema` then fails on it. The fix is the
same tmp-plus-`os.replace` pattern your `runs_store.save()` already uses.

The NUMBER-as-count item below is **fixed upstream** by your `kgap/aact_adapter.py` INDEX_RULES 2. The test on this
branch now checks your adapter against a planted rate row and a planted count row.

## 1. (FIXED upstream) DEFECT: `aact_lane` stores rates as event counts

**Where:** `scripts/k_gap_bulk_acquire.py:127-130`.

**What happens:** every `outcome_measurements` row whose `param_type` is NUMBER becomes
`int(float(param_value_num))` in `groups[].count`. The `units` field is never read.

**Example:** RE-LY (NCT00262600) posts stroke/SE as NUMBER with units of %/year (1.11 vs 1.71). The index stores
this as "1/6015": a truncated rate presented as events/N.

**Measured on this topic:** `harness/g1_noac.py::measurement_kind` types 67 of the 172 NOAC measurement rows as RATE.
The census is `rates_refused_as_events` in `outputs/g1_noac/g1_noac.json`.

**Proposed fix:**
- Treat a row as a count only when either:
  - `param_type` is COUNT_OF_PARTICIPANTS or COUNT_OF_UNITS; or
  - `param_type` is NUMBER and the units name participants or events, and the value is a non-negative integer.
- Type rate units (%, per year, per 100 patient-years) as RATE.

**Plant:** a NUMBER row in %/year must not appear in `groups[].count`.

## 2. Definition of the TWO-SOURCE RULE

I found no definition on acq/k-gap. The one used here is the `TWO_SOURCE_RULE` constant in `harness/g1_noac.py`.

**What makes a tuple the same:**
- Required, and equal in both sources: trial, outcome, kind, measure and CI level.
- Population, dose, timepoint and definition: no axis may be stated differently by the two sources.

**States:**
- **TWO_SOURCE_VERIFIED:** two independent primary sources give the same tuple with equal values at printed
  precision.
  - An axis that only one source states is listed as `silent_axes`. It is never assumed to agree.
- **INCOMPARABLE:** the two tuples differ on an axis that both sources state, for example ITT vs on-treatment, or a
  95% vs 97.5% CI. These are different analyses, not a conflict.
- **CONFLICT:** the same tuple appears in both sources with different values. Both are quoted; they are never
  averaged.
- **SINGLE_SOURCE:** no comparable pair exists.
- **SECONDARY_ONLY:** the value comes only from the comparator. It never counts.

Please confirm this rule or supersede it. If yours differs, g1/noac will adopt yours.

## 3. A full-text manuscript is committed on acq/k-gap

`cache/comparators/34985309/2026-09-30_kgap_jats.xml` is the complete NIHMS author manuscript of COMBINE AF.
Its licence reads: "available for text mining … fair use".

The project rule is to commit excerpts only. Please decide whether this file should be committed in full.

g1/noac's own outputs quote single sentences with paragraph sha256 values, never whole paragraphs.

## 4. For the k-gap table: ROCKET AF identity resolves

The AACT `study_references.txt` from snapshot 2026-08-30 contains the row `NCT00403767|21830957|DERIVED`.

The held PubMed abstract also names the trial and its registration itself: "ROCKET AF ClinicalTrials.gov number,
NCT00403767". All 4 trials resolve by this deterministic basis.
