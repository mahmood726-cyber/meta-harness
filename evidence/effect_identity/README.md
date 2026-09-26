# Effect identity before source preference (branch only; served changes are notices for Mahmood)

External review of colchicine-recurrent-pericarditis (hash f42a3bf5...), 2026-09-26.

## (1) SOURCE_EFFECT_CONFLICT: a published ratio that disagrees with its own counts

- **CORP-2 (PMID 24694983).** The served value is RR 0.49 (0.24-0.65), `PUBLISHED_EFFECT_TARGET_CLASS`. It was preferred over its own
  counts, 26/120 vs 51/120, which give RR **0.5098 (0.3421-0.7596)**, the review's 0.342-0.760.
- **The source mislabels it.** The held abstract itself says "relative risk 0.49; 95% CI 0.24-0.65": the mislabel is in the
  source, not the extractor. 1 - 0.5098 = 0.490, and 1 - the count CI = 0.240-0.658, so the published number is the relative risk
  REDUCTION.

`harness/effect_identity.conflict_check()` runs after source-hierarchy selection:
- It recomputes the count-implied RR (Katz) and OR (Woolf).
- It tests named hypotheses against the point AND both CI ends, within the published rounding plus a 0.006 method slack:
  AS_LABELLED, RRR_AS_RR (1-x, ends swapped), OR_AS_RR / RR_AS_OR, RECIPROCAL.
- A mismatch emits `SOURCE_EFFECT_CONFLICT` with the hypotheses that match. **Nothing is relabelled.**
- The row is **HELD**: moved out of the pool, visible with its tuple, counts and every hypothesis.
- The one exception: its own quotation documents an adjusted model (covariate adjustment only, e.g. "adjusted relative risk",
  "age-adjusted"; not "multiplicity-" or "dose-adjusted"). Then the published effect is kept and the conflict disclosed.
- An HR is recorded NOT_COMPARABLE, since it is not the crude ratio of its counts. A zero cell is never corrected into a number.

## (2) Transformation provenance

CORP (PMID 21873705) reports "relative risk reduction, 0.56 [CI, 0.27 to 0.73]" (recurrence) and "0.56 [CI, 0.27 to 0.74]"
(symptoms). `extract` correctly converts these to RR 0.44 (0.27-0.73) and 0.44 (0.26-0.73), but the rows said
`KEEP_REPORTED_EFFECT` with `reported_label` RR.
- `transform_provenance()` now records {reported_measure RRR, the reported values, transform "RR = 1 - RRR; CI endpoints swapped",
  derived RR}. It reads the row's quotation, then the held abstract (the recurrence quotation is cut mid-CI).
- A transform is accepted only if it reproduces the served tuple exactly.
- The rule becomes `KEEP_REPORTED_EFFECT_TRANSFORMED`, and `effect_object.reported_label` becomes RRR. The canonical estimand stays
  RR, so compatibility is unchanged.
- The recurrence record carries a note that its interval is symmetric about 0.5 (0.27 + 0.73 = 1). That is why the transform is
  invisible in the numbers, and why it must be recorded.

## A hold must reach the reader (found in the real build, fixed)

`absence.classify_reason` re-classified the held row as **EXTRACTION_NOT_PERFORMED**, so the hold read as "not extracted". It now
keeps HELD_SOURCE_EFFECT_CONFLICT, like the RESULT_INCOMPATIBLE / ENDPOINT_UNBOUND codes it already preserved. The plant is the
pre-fix absence layer, which returns EXTRACTION_NOT_PERFORMED.

## Corpus-wide at v1/candidate 3876a62d (`measure_effect_identity.py`, which uses the module's own functions)

**Conflicts.** 127 served pooled rows; 86 carry a reported effect; 6 have counts for the same result; 4 of those are comparable
(RR/OR; 2 are HR). **3 of 4 comparable rows conflict:**

| topic | trial | published | count-implied RR | hypothesis | resolution |
|---|---|---|---|---|---|
| colchicine-recurrent-pericarditis | CORP-2 24694983 | RR 0.49 (0.24-0.65) | 0.5098 (0.342-0.760) | **RRR_AS_RR** | HOLD |
| probiotics-aad-prevention | 7872284 | RR 0.29 (0.08-0.98) | 0.4948 (0.209-1.172) | none | KEEP_DISCLOSED (a documented multivariate-adjusted RR) |
| tocilizumab-covid19-mortality | RECOVERY 33933206 | "RR" 0.85 (0.76-0.94) | 0.8822 (0.808-0.963) | none | HOLD. The held abstract says "rate ratio" and documents no model; the age adjustment is only in the full paper, which is not held. This is the same row the ordered-contrast census flagged as a rate ratio labelled RR |

**Provenance.** **2 of 86** reported rows are transforms served without a record: CORP recurrence and CORP symptoms. Both are
RRR->RR, `KEEP_REPORTED_EFFECT`, labelled RR.

## Notices if landed (for Mahmood)

| topic | pool | served now | after |
|---|---|---|---|
| colchicine-recurrent-pericarditis | primary | 0.4643 (k=2) | 0.44 (0.27-0.73), k=1 (CORP only); CORP-2 held with RRR_AS_RR. Verified with a real build_topic |
| tocilizumab-covid19-mortality | primary | 0.85 (0.76-0.94), k=1 | withdrawn: RECOVERY held (unexplained conflict with its counts) |
| colchicine-recurrent-pericarditis | 2 CORP rows | labelled a reported RR | labelled a transformed RRR (no number moves) |

A reviewer's typed resolution (which number the source means, with evidence) releases a held row. For RECOVERY, holding the full
text that documents the age-adjusted model would resolve it as KEEP_DISCLOSED.
