# Decision brief: the two OR admissions that suppress RR pools (2026-09-29)

Both are **right numbers in the wrong measure**. Admitting either as reported suppresses its topic's RR pool
(INCOMPATIBLE estimands; `counterfactual_all.json`: colchicine-postop-af valid k 3 -> 0, CAP 2 -> 0). They are
held out of every "landable" count in `REPORT_STEP2.md`. This brief sets out the facts; it does not decide.

## CAP — PMID 35723686 (methylprednisolone vs placebo), topic `corticosteroids-cap-mortality` (RR pool)

- The full text (PMC OA) reports the OR in prose: 60-day mortality OR 0.89 (0.58, 1.38).
- The same full text's **Table 2** holds arm counts with denominators:
  `Died on or prior to study day 60 — no./total no. (%) | 47/286 (16) | 50/277 (18) | 0.89 (0.58, 1.38)`.
  That implies **RR = (47/286)/(50/277) = 0.91**.
- Why the rung does not take it: the row names no arm. The arm names ("Methylprednisolone (n = 297)",
  "Placebo (n = 287)") are only in the table header. A row-plus-header extractor would read it. That is a new
  typed adapter, not a patch.
- **Open question before any use:** the registered timepoint. Table 2 gives day 60, day 180 and 1 year.

## COCS — PMID 36286314 (colchicine vs placebo), topic `colchicine-postop-af` (RR pool)

- The full text reports POAF as "21 (18.6%) ... vs. 39 (30.7%)" with no written denominators, and OR 0.515
  (0.281-0.943).
- The denominators are **inferable**: 21/0.186 = 113 and 39/0.307 = 127. They sum to the stated 240 analysed
  (267 randomised, 27 dropped out). The implied RR is (21/113)/(39/127) = 0.61.
- The harness refuses this today by design: COUNTS_PRESENT_NOT_CORROBORATED — no count is taken without a
  corroborated denominator.

## The decision (not this lane's)

1. Keep refusing both (status quo; the pools stay valid, k unchanged).
2. Build a row-plus-header table extractor, which would take CAP's written 47/286 vs 50/277. That is a typed
   structural source with no inference, subject to the timepoint check.
3. Allow percentage-inferred denominators when they reconcile exactly with a stated analysed total, which would
   take COCS. This changes a standing extraction rule.

Either admission, taken as an RR, adds +1 valid k to its topic instead of suppressing the pool.
