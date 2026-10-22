# How the harness works (as it now stands)

A plain-language account of the machine for someone who has not been in the build. Snapshot of the
current state; live counts (topics, verified numbers, coverage) should be checked against
the published index and the committed verification ledger. The repository currently defines
**15 verification limbs** in `scripts/verify_all.py`; these are distinct from the
**two-limb publication gate** in `harness/gate.py`. Neither is independent clinical validation.

Two ideas run through everything:
- **The model locates; deterministic code parses; a round-trip decides; a number never comes from a model.**
  Where a model is used, it points at a verbatim span in a committed source; code extracts the digits and
  recomputes the effect, and the trial is refused if that recomputation does not reconcile with the source.
- **A landing is not landed until it reproduces from a fresh clone and the live URL has been read back.**

## 1. The one command, end to end

    python scripts/build_topic.py <slug>

1. **Protocol (intended prospective workflow).** `protocols/<slug>.md` declares the planned PICO and
   analysis before retrieval in a prospective run. **This condition was not met by the 32 legacy
   examples:** their protocols were first committed during a build, not in protocol-only registration
   commits. Their protocol SHAs are not evidence of prospective registration.
2. **Retrieval and replay.** Live collection can consult PubMed, Europe PMC, registries and citation
   networks, then commit `cache/<slug>/records.json` for offline replay. For the *served legacy corpus*,
   the search census is **11 known-item, 17 title-seeded, 4 hand-written keyword, 0 registered
   concept searches**. Thus a cached trial list demonstrates replayability, not prospective search
   recall or completeness. Raw live retrieval and committed offline replay are separate operations.
3. **Rule screening and disagreement records.** Two coded screening routes can be compared and
   disagreements logged. One route resolving the other route's disagreement is **not independent,
   blinded human adjudication**. Rule IDs and cited spans make decisions inspectable; they do not
   establish that eligibility judgements are correct.
4. **Extraction down the source ladder** (section 2) — per trial, per outcome.
5. **Synthesis.** A regression-tested statistical core pools available compatible data under the
   declared method (including PM/REML and HKSJ when applicable). A method-matched external R
   comparison is still needed for publication. Wrong endpoints, populations and study sets can
   produce reproducible but scientifically wrong estimates.
6. **Tabbed page** rendered (`docs/reviews/<slug>/`) plus a neutral blind pair for judging.
7. **Gates.** The two-limb publication gate checks each review (section 3). The local hook and CI
   run `python scripts/verify_all.py`, the same **15-limb** verification suite; a refusal blocks
   the verified deployment path. The checks protect internal consistency, not independent accuracy.
8. **Published URL** (GitHub Pages, `/docs` on `main`) after push.
9. **Fresh-clone replay:** current pages re-derive from the *committed analysis inputs and cache*
   and are byte-compared against the served artifacts. **Re-running from a legacy protocol SHA alone
   does not regenerate the served bytes**: that SHA does not pin the later cache and build state.
   This is computational replay, not registration-time reproduction or independent correctness.

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

## 3. Publication gate and verification (`harness/gate.py`; `scripts/verify_all.py`)

**Limb 1 — reproducibility & integrity:**
- `check_reproduction` — offline replay must regenerate the committed numbers and page byte-for-byte.
- `check_cache_tracked` — the committed cache must be git-tracked (else a fresh clone cannot reproduce).
- `check_primary_result` — the primary outcome must actually carry a result (k, estimate).
- `check_pooled_verified` — every pooled number's digits must be located in its committed source span.
- `check_manuscript_numbers` — the generated manuscript may not state a number the object does not carry
  (every manuscript numeral must be object-derived; proven to refuse a fabricated number).
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

These examples are not a complete enumerated gate inventory. `scripts/verify_all.py`
executes **15 fail-closed limbs**, including unit tests, full offline replay, the gate on each served
review, index currency, provenance, held-out leakage and independent-recompute *code paths*.
The independent-recompute limb is an internal implementation check; it is not an external
blinded clinical adjudication. See the current code and verified CI ledger for the live state.

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

## 5. Internal coverage of the meta-analysis error library (33 classes)

`harness/error_library.py` catalogues 33 documented meta-analysis mistake classes; internal
coverage does **not** show that all mistakes have been externally detected or prevented. Each
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
  Coverage is now measured and shown (a minority of pooled trials carry a rating; no trial reaches "high"
  on the registry-derived assessment), and each primary outcome carries a RoB-stratified sensitivity
  re-pool (low-risk-only) with the coverage caveat stated.
- **The continuous-outcome tier is small (three pages)** and bar-limited — most drug/outcome pairs fail the
  raw-mean±SD / single-dose / common-timepoint alignment.
- **GRADE is partial.** A machine-computable certainty is now rendered (risk-of-bias, inconsistency,
  imprecision, and publication bias assessed from the registry ghost census rather than funnel asymmetry);
  indirectness is left to human judgement. A **specification curve is still not built.**
- **We measured internal extraction agreement.** A within-project census re-extracted pooled numbers from
  committed source by a checker blind to the stored value; of the numbers independently re-checkable, the
  confirmed residual error after internal adjudication was zero *among recheckable records*, and the
  census surfaced (and we fixed) a wrong-endpoint value that had passed every gate. These are internal
  measurements, not an independent estimate of the end-to-end real-world error rate.
- **The gate proves "still reproducible", not "still right".** Re-audit old artifacts whenever the checks
  strengthen — wrong numbers have clustered in pages built before the relevant guards existed.
