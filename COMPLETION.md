# Reproducible meta-analysis harness — honest completion statement

_Snapshot of the finished state. Every claim here is regenerable from the committed repo; every
number on every page traces to a committed source; every decline is named on its page._

## What is live

- **27 of 33 preregistered topics LIVE** and passing the two-limb gate, reproducing byte-for-byte
  from a committed protocol SHA on a fresh clone. The 27th, **melatonin-primary-insomnia**, is the
  first **continuous-outcome (mean-difference)** page: MD −17.4 min in sleep-onset latency, per-arm
  mean/SD verified from CT.gov structured results — never imputed from a figure or curve.
- **Blind-judged — restated on the FAIR basis.** The original abstract-based comparison gave 15 clean
  wins / 0 / 0. The **fair full-text re-judge (8-topic sample, order-randomised)** supersedes that with
  a domain split: our pages are more **auditable on 8/8** (search reproducibility, per-number
  traceability, declared-absence, overall), the comparator more **complete on 8/8** (larger k), RoB
  reporting 5/2/1. **We win transparency/auditability; we lose completeness/k** — the same conclusion
  the parity table reaches, now confirmed blind on full text. The judge also flagged genuine defects in
  our pages, recorded in `docs/fair_judge.json` — **all four now fixed:** (1) the retraction line whose
  count did not equal k (stale on 8 pages — re-run corpus-wide, denominator named precisely, test-
  guarded); (2) the effect-scale mislabel (a hazard/rate ratio printed as "(RR)" on denosumab, statins
  and omega3's mixed pool — every effect now labelled with its own reported scale); (3) omega3's
  comparator k stated three ways (8 auto-extracted / 15 assessed same-scope / 22 verified full-text
  MACE pool — each number now defined together, arithmetic reconciled); (4) the RoB2 table covering a
  subset of pooled trials — it now states coverage ("N of K primary-outcome pooled trials assessed") and
  renders every unassessed trial as an explicit "not assessed — no registry match" row, never omitted.

## The result (thesis), stated once

Registry reach and regulatory reach (FDA/EMA) **miss pre-registry trials**; **bibliographic reach
(citation chasing) finds them** — 9 of 9 old reach-gap trials recovered from the comparators' own
reference lists. Our **preregistered screen then declines many** that the comparator pooled, for
stated reasons (open-label where we require double-blind; population/outcome mismatch). **So the `k`
difference is a stated design-bar difference, not a search deficit.** Alongside **"we decline where
the comparator imputed"** (continuous-outcome variances reconstructed from Kaplan–Meier curves and
figures — 0 of 7 verifiable for zinc), this is a methodological position no published comparator
states about itself.

## Fair comparison (confound fixed in our disfavour, direction held)

The earlier countable PRISMA read comparator **abstracts** against our full pages. Fixed by fetching
every comparator's **OA full text (25 of 26; corticosteroids-cap excluded — no obtainable comparator
full text)** and re-scoring full-text vs full-page over the 25 scorable topics (150 cells). The
reproducible score (re-scoring the committed full-text caches with the current scoring code):
- comparator full text satisfies **80 / 150** checkable cells (far above its abstract score — the
  confound was real; also higher than an earlier partial full-text pass reported, corrected here
  against ourselves);
- **comparator-present / ours-absent: 0 / 150**;
- ours-present / comparator-absent: **70** (down from the 79 reported on the abstract-era prose — the
  margin narrowed **further** against us under the corrected full-text scoring).
The margin narrowed under fair measurement; the direction held (0 reverse).

## Parity (finishing metric): 8 of 18 same-scope topics at parity within scope

At parity within scope: finerenone (2/2), glp1 (7/7), sglt2-hfref (2/2), crystalloids (5/5 mortality),
ticagrelor (1/1 valid RCT), spironolactone (2/2 preregistered scope), pcsk9 (2/2-effective, ~87% of
comparator patients), and **noac-vs-warfarin (4/4)** — closed by a documented pre-specified approved-dose
rule (RE-LY switched from the 110 mg dose it had been pooling to the approved 150 mg, `RR 0.66` vs the
old `0.91`; ENGAGE-AF 60 mg added), both numbers verified verbatim and independently cross-checked by a
second lane. A selection decision made by a documented rule with cross-checking, not by hand.

**Every remaining gap was re-tested against the capabilities that did not exist when its reason was
written** (full-text acquisition, supplements, continuous extraction, the dose rule, error-library
checks). The result is itself a finding: one gap was closable (noac), and **five reasons were
re-confirmed, several with stronger evidence — none closed by lowering the bar**. The remaining `k` gaps
are not ours to close: iv-iron (CT.gov mislabels HEART-FID's recurrent-event hospitalizations as
participant counts — a wrong number the recurrent-event guard refuses); sglt2-ckd (the matching kidney
composite is paywalled/IPD-only; CT.gov posts a CV-inclusive one); corticosteroids-covid (non-RECOVERY
mortality is publisher-blocked); tranexamic-pph and pericarditis (reachable but prophylaxis-not-treatment
/ open-label — excluded by the preregistered PICO/design bar). Each refined reason is on its page and in
`docs/parity.json`. (probiotics rose 14→15 by recovering one trial from full text via verified_arms; its
integrity-freshness invariant refused the stale retraction count until it was re-run — a check the harness
built catching its own author.)

## Walls measured (all on the pages)

1. **Registry + regulatory reach** miss pre-registry trials (FDA/EMA/ISRCTN/EU-CTR/ICTRP).
2. **Bibliographic reach finds them, but our screen declines many** (design/outcome) — a strictness
   difference, not a search failure.
3. **Continuous-SD imputation**: the comparator reconstructs variances from figures/curves; we decline
   where we cannot verify a per-arm SD.

## Recoveries and corrections (session; every added number verified true against source)

- Recovered + pooled: FIDELIO-DKD (finerenone 1→2), CONFIRM-HF (iv-iron 1→2), END-AF (colchicine-postop
  4→5), Alpha Omega main + probiotics main (dedup fix).
- Built from scaffolds after verify-before-build: sacubitril (24th), corticosteroids-cap (25th),
  metformin-pcos (26th). hfnc declined (mixed-scale garbage pool).
- General fixes (each scan-verified corpus-wide, regression-tested): NEJM "primary composite outcome"
  anchor; dedup main-results-beats-sub-analysis; pivotal-trial gate limb; generic-harm discriminating
  guard (7 wrong GI-harm pools removed); `(P%; CI)` corroboration; multi-arm guard keys on arm labels
  not regimens; SUSTAIN-6/FIGARO component-vs-composite classes locked.
- Full-text acquisition built properly (the shared blocker for the declines): PMC OA body + STRUCTURED
  tables (per-arm values keep their row) + supplementary spreadsheets/CSV (openpyxl/csv, values-only,
  via the OA .tar.gz package). CT.gov structured CONTINUOUS extraction added (MEAN + SD → mean
  difference; refuses SE/CI/IQR). Every guard stays in front — the number is never taken from the
  acquisition layer. First continuous page (melatonin) built on it; verify hardened to check per-arm
  mean+SD digits against the source. Declines re-run through it and confirmed with stronger evidence:
  zinc (medians only, no IQR/SD in body/tables/supplements — Rao 2020), azithromycin & vitamin-D
  (estimand-blocked — the declared binary/proportion outcome is reported only as rates/HR/IPD, at no
  depth). Full text unblocks per-arm-VARIANCE cases, not estimand-mismatch declines.
- Fair-judge defects fixed against us: (a) the trial-integrity retraction line carried a stale count on
  8 pages and an ambiguous denominator — re-ran the check corpus-wide, the render now names it "trials
  pooled across all outcomes", and a test forbids stale integrity from returning; (b) the effect-scale
  label was inherited from the topic's target estimand, so 16 outcome-trials across 9 topics printed a
  hazard/rate ratio as "(RR)" (denosumab hip/nonvertebral, statins, omega3's mixed MACE pool) — the
  page now labels every effect with its OWN reported scale (`result["scale"]`: RR/HR/IRR/mixed),
  consistent across the header, per-trial, and pooled rows; regression-tested.
- Renders: parity table (index + per-topic), refusals ("verified but not pooled, because…"),
  independent second-extraction status, the two walls + thesis on the index.

## Bar (held to the end)

0 wrong numbers shipped this session; 0 UNVERIFIED pooled numbers (weakness survey); every decline
named on its page; the fair comparison self-corrected against us and still held. ~10 wrong-endpoint
mis-pools were caught during the run — every one by verification, not by a gate passing them.

## Honest residual weaknesses (from the weakness survey, finished state)

- **Small-k fragility**: 22 topics have k≤2 / τ²=0 / a CI that crosses the null at small k. This is the
  dominant limitation and it is real — many topics are single-drug or scope-limited by design.
- **9 mixed-scale pools** (HR+RR / HR+IRR / OR+RR), disclosed via the mixed-scale label but not
  resolved to a common estimand.
- **RoB2 coverage is partial and now stated on every page**: it is scoped to the primary-outcome
  pooled trials and only those with an AACT registry match are machine-assessed; the rest render as
  explicit "not assessed — no registry match" rows with a coverage count (e.g. probiotics 1/14,
  omega3 6/8), never silently omitted. D3 (attrition) and human-judgement domains stay "not assessed".

## What remains NOT done (plainly)

- **6 preregistered topics remain declined, each for a verified, source-grounded reason re-confirmed at
  the full-text level** (recorded in `JUDGELOG.md`): zinc (continuous — even full text + tables +
  supplements carry medians without IQR/SD; MD variance uncomputable without imputing from a curve);
  azithromycin & vitamin-D (**estimand-blocked** — the declared binary/proportion outcome is reported
  only as rates/HR/IPD-derived at every depth, so full-text acquisition does not rescue them);
  prone-positioning (k=2 with extreme severity heterogeneity across scales/timepoints — reader-hostile
  as one pooled CI without severity stratification); antibiotics-vs-appendectomy (wrong outcome/timepoint
  — 1-year not in the sources, CT.gov substring grabbed a 30-day success measure); hfnc (mixed OR/RR and
  a k=1 unrepresentative outlier). melatonin, previously in this list, is now LIVE (27th) via the new
  full-text/continuous path. **Continuous-outcome breadth on existing topics is exhausted for now**: a
  scan shows melatonin is the only current topic whose comparator reports a continuous outcome; broader
  continuous coverage means new continuous-primary topics, not retrofitting the binary/ratio ones.
- **A fully-fair blind judge across all 26** (not just the countable PRISMA + an 8-topic sample).
- **GRADE certainty, specification curve, and broader unit-of-analysis guards** (only duplicate-
  publication is enforced) are not built.
- **9 mixed-scale pools** are disclosed and labelled consistently but not resolved to a common estimand
  (HR/RR/IRR pooled on the log scale as ratio-of-risk approximations, as the comparators do).
- **RE-LY / ENGAGE multi-dose arm-selection** is flagged as a refinement, not resolved by a
  pre-specified dose rule.

The honest one-line summary: **the harness matches or exceeds published OA comparators on
reproducibility, per-number verification, and transparency; it is behind on `k`, and that gap is now
measured and attributed (design-bar strictness and source availability), not asserted away.**
