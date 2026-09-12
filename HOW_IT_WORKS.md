# How the harness works (as it now stands)

A plain-language account of the machine for someone who has not been in the build. Snapshot of the
current state; the live counts (topics, verified numbers, coverage) are **self-counted on the published
index** — read them there, not here, so this document cannot drift. Structural counts below (13 gate
limbs, 33 error classes) are derived from the code (`harness/gate.py`, `harness/error_library.py`).

Two ideas run through everything:
- **The model locates; deterministic code parses; a round-trip decides; a number never comes from a model.**
  Where a model is used, it points at a verbatim span in a committed source; code extracts the digits and
  recomputes the effect, and the trial is refused if that recomputation does not reconcile with the source.
- **A landing is not landed until it reproduces from a fresh clone and the live URL has been read back.**

## 1. The one command, end to end

    python scripts/build_topic.py <slug>

1. **Protocol committed first.** `protocols/<slug>.md` is committed *before* the build; its git commit
   SHA is the registration timestamp, recorded on the page. You cannot register after seeing results.
2. **Search (fetch-once → committed cache).** PubMed E-utilities + Europe PMC, **registry-first**
   enumeration (ClinicalTrials.gov/AACT by condition × intervention → resolve NCTs to PMIDs), and
   **citation chasing** (Europe PMC references/citations of the comparator and pivotal trials). Forced
   PMIDs (pivotals, controls, comparator) are protected from the size cap. The result is written to a
   committed `cache/<slug>/records.json`; the offline pipeline never touches the network again.
3. **Dual screening with adjudication.** Two independently-implemented rule screeners (one title/registry
   anchored, one full-abstract) run; disagreements are reported (PRISMA item 8); screener 1 adjudicates.
   Every include/exclude carries a rule id and a verbatim span.
4. **Extraction down the source ladder** (section 2) — per trial, per outcome.
5. **Synthesis.** metafor-validated pooling (REML/PM for small k; HKSJ with a t on k−1; log scale for
   ratios). Estimand homogeneity is enforced or the pool is labelled `mixed (X/Y)`.
6. **Tabbed page** rendered (`docs/reviews/<slug>/`) plus a neutral blind pair for judging.
7. **Two-limb gate** (section 3) runs in the pre-commit hook; a failure refuses the commit.
8. **Published URL** (GitHub Pages, `/docs` on `main`) after push.
9. **Fresh-clone reproduction:** `scripts/reproduce_review.py --fresh-clone` clones HEAD, rebuilds, and
   byte-compares every page. Re-running from the protocol SHA on a clean checkout regenerates the served
   bytes exactly.

## 2. The source ladder (priority order; higher wins)

1. **`override: true` tier** — a committed, hand-verified per-trial correction (`verified_effects` /
   `verified_arms` with the flag) for the rare case where the extractor picked a source-backed but WRONG
   number (wrong endpoint/scale/denominator). Beats everything for exactly that one trial+outcome; flag-
   gated so no other page is affected; regression-tested so the old bug reproduces without it.
2. **Pre-specified dose** — a documented approved-dose rule (e.g. RE-LY 150 mg, ENGAGE 60 mg).
3. **Abstract** — the authors' headline result for the declared outcome (unambiguous; the safe default).
4. **ClinicalTrials.gov / AACT structured results** — per-arm event counts or per-arm mean±SD tables.
5. **PMC full text and tables** — where the abstract omits per-arm SD / person-time / a rate+CI.
6. **Supplements** — spreadsheets/CSV in the PMC OA package.
7. **FDA/EMA and prior-meta tables** — reviewer analyses and comparator reference lists (reach, not
   primacy).
8. **Committed hand-verified arm/effect entries** — bottom fallback, used only when everything above
   yields nothing.

At every rung: the digits must appear in the cited committed span, the arms must be correctly assigned,
and the count-derived effect must reconcile with the effect the paper reports (**round-trip**), or the
trial is declared-absent — never guessed.

## 3. The two-limb gate (13 checks; `python -m harness.gate <dir>`)

**Limb 1 — reproducibility & integrity:**
- `check_reproduction` — offline replay must regenerate the committed numbers and page byte-for-byte.
- `check_cache_tracked` — the committed cache must be git-tracked (else a fresh clone cannot reproduce).
- `check_primary_result` — the primary outcome must actually carry a result (k, estimate).
- `check_pooled_verified` — every pooled number's digits must be located in its committed source span.
- `check_fetch_complete` — refuse if a CORE fetch source (PubMed / Europe PMC / ClinicalTrials.gov)
  recorded `RAN_ERROR` (a throttled/partial fetch silently degrades the cache).
- `check_pivotal_present` — a pre-registered pivotal/landmark trial must be in the cache.
- `check_no_double_counted_trial` — a trial id pooled more than once within an outcome is refused.
- `check_duplicate_publication` — the same trial pooled under two publications is refused.
- `check_retraction` — a pooled retracted trial is refused (expression-of-concern is surfaced).
- `check_cross_source` — a hard abstract-vs-registry discrepancy on the same number is refused.
- `check_controls` — a positive control must screen in; a negative control must not.
- `check_limb1` — the umbrella: reproduces with zero census failures AND served method == declared method.

**Limb 2 — honest comparison:**
- `check_limb2` — a published open-access comparator is named and the trial-set overlap is stated.

Two more global checks run in the hook: the generated **index must byte-match** a fresh `build_index`
(no hand-editing), and `_validate_prose_numbers` **refuses any un-accounted numeral** in the index's
prose banners (object-derived or whitelisted-static only — the "95 of 95 drifted stale" guard).

## 4. The guards, and the defect that created each

Each guard exists because a specific wrong number got through once:
- **Fetch-truncation protection** (`fetch._apply_cap`) — semaglutide's pivotal STEP-1/3 were dropped when
  the query filled `max_records` before the forced PMIDs were appended.
- **Multi-arm dose** (`extract._multi_dose_arms`) — a fixed-dose multi-arm trial (CANTOS / TRANSFORM-1)
  offers no single pre-specified arm; refuse rather than pick one.
- **Factorial** (`extract._is_factorial`) — pool the *marginal* comparison (VITAL, ORIGIN, BaSICS), never
  a single 2×2 cell.
- **Subgroup** (`extract._is_subgroup_sentence`) — an effect from a per-protocol/post-hoc/subgroup sentence
  (azithromycin "lowest in the HP+/AZ group") is not the ITT result.
- **Composite** (`extract._names_composite`) — a composite-endpoint number is the wrong endpoint for a
  single-component outcome (FAIR-HF2's "CV death or HF hospitalization" ≠ "HF hospitalization").
- **Null-result clause** (`extract._kw_only_in_null_result`) — COPPS-2 stated "discontinuation rates were
  similar" with the adjacent counts belonging to an *adverse-event* clause; refuse the co-located number.
- **Recurrent-event** — HEART-FID's CT.gov "hospitalizations" are events, not participants; refuse pooling
  them as a binomial count.
- **Wrong-arm / inversion** — a CT.gov HR is always experimental-vs-comparator; swap labels, never invert.
- **Timepoint consistency** (`ctgov_results.endpoint_weeks`) — semaglutide reports weight change at Week 68
  and Week 44; a trial off the declared timepoint is declared-absent (do not pool mixed follow-up).
- **Estimand tiebreak** (`ctgov_results._is_supplementary_estimand`) — a trial posting both an in-trial
  (treatment-policy) and an on-treatment estimand (Korean STEP) is resolved to treatment-policy, not by
  listing order.
- **Cluster / crossover** (`unit_of_analysis.detect`) — a cluster-randomised or crossover trial (SMART /
  SALT-ED / SPLIT) needs a design-effect the source rarely gives; disclosed, weight-caveated, not adjusted.

## 5. The meta-analysis error library (33 of 33)

`harness/error_library.py` catalogues 33 documented meta-analysis mistakes; **0 remain unchecked.** Each
is one of: a **gate limb** (9) that refuses a finished page, a **regression test** (12) with a plant that
fires before the fix, or a **rendered disclosure** (12) when it is a judgement the harness cannot make but
must show (mixed-scale label, unit-of-analysis caveat, retrospective-registration flag, small-k/GRADE
limitations, per-trial funding/COI). `scripts/error_coverage.py` writes the per-review coverage; every
live review is screened against 32–33 of the 33 (the 33rd, pivotal-present, is active only where a topic
declares a pivotal). A test forbids overclaiming: any entry that claims a gate limb must name a real
`gate.check_*` function.

## 6. What is measured, and where it renders

- **Parity** (`docs/parity.json` → index): our pooled k vs the comparable same-scope comparator k, with a
  named reason for every difference.
- **Recall** (`cache/<slug>/recall.json`): fraction of a topic's known trials the registry-first search
  recovered — reach distinguished from inclusion.
- **Fill matrix / dual-extraction agreement**: coverage of the trial×outcome grid and the two screeners'
  disagreement rate.
- **Trace / per-number verification**: every pooled number located in source; the exact count self-counted
  on the index and gate-enforced by `check_pooled_verified`.
- **PRISMA countable** (`docs/prisma_fair.json`): our full pages vs the comparator's **full text** on the
  checkable reporting items, over the scorable topics.
- **Blind judge per dimension** (`docs/fair_judge.json` → index): order-blinded, full-text-vs-full-page, on
  search reproducibility, per-number traceability, completeness, risk-of-bias reporting, declared-absence,
  overall auditability. The per-dimension margins are **derived** from the judgment record and re-checked
  by a test, not typed.

## 7. Standing refusals (we decline rather than guess)

- **LSM / SE** — a least-squares-mean with a standard error (ANCOVA) is not raw per-arm mean±SD; refused
  (FEV1, blood pressure, HbA1c efficacy endpoints commonly sit here).
- **Imputed variance** — an SD reconstructed from a Kaplan–Meier curve or a figure is refused.
- **Mixed timepoints** — a continuous outcome pooled across different follow-up lengths.
- **Mixed scales** — pooled HR/RR/OR/IRR are labelled `mixed (X/Y)`, never presented as one clean estimand.
- **Subgroup-as-total** — a subgroup number pooled as the whole trial.
- **Outcome-based eligibility** — a trial is included on P/I/C/design only, never on whether it reported
  the outcome (non-reporters are declared-absent, not screened out).

## 8. Known limits (plainly)

- **Fewer trials than the comparators**, by design — the k gaps are stated bars (open-label excluded,
  prophylaxis vs treatment, drug-class vs single agent, imputed variance declined), decomposed on each page.
- **Risk-of-bias reporting is our weakest dimension** — the blind judge puts it to the comparator: our
  RoB2 is computed from machine-available registry fields, theirs is hand-scored Cochrane across all trials.
- **The continuous-outcome tier is small (three pages)** and bar-limited — most drug/outcome pairs fail the
  raw-mean±SD / single-dose / common-timepoint alignment.
- **GRADE certainty and a specification curve are not built.**
- **The gate proves "still reproducible", not "still right".** A one-pass source re-audit of all topics
  found and fixed multiple wrong numbers that had passed every gate limb — they clustered in pages built
  before the relevant guards existed. Re-audit old artifacts whenever the checks strengthen.
