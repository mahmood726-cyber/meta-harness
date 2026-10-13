# k-gap phase 4: published metas, SECONDARY (13 Oct 2026)

Engine: `scripts/g1_two_source_sweep.py --run` over the 14 gap topics, refreshed 13 Oct.
- 154 sweep targets.
- 11 new recorded forest-plot reads (codex, recorded; `evidence/model_calls/secondary`); 92 held.
- The comparator meta is never a source (excluded under every id).

The refreshed verdicts are kept in `phase4_sweep_refresh/`. **The committed `outputs/k_gap/sweep/` is left unchanged**
(see "Stale sweep" below). Rule (Mahmood 13 Oct): meta rows are SECONDARY, provisional and queued for primary
verification; **G1 counts only PRIMARY_VERIFIED**.

Population: the k-gap's 141 trials.

| class | trials of 141 |
|---|---|
| NO META ROW | 84 |
| META ROWS, ALL REFUSED / CROSS-CHECK FAILED | 29 |
| NO IDENTITY TO SEARCH | 19 |
| SECONDARY_PROVISIONAL (1 meta) | 3 |
| NOT_IN_SWEEP | 2 |
| NO META FOUND | 2 |
| REGISTRY ONLY, NOT COUNTED | 1 |
| SECONDARY_PROVISIONAL (2 independent metas) | 1 |

**Queued for primary verification (4): SECONDARY, provisional, not counted:**

| topic | trial | sweep verdict | metas found |
|---|---|---|---|
| colchicine-postop-af | Sarzaeem [23] | SWEEP_TWO_INDEPENDENT_METAS | 0 |
| probiotics-aad-prevention | Gotz et al51 | SWEEP_SECONDARY_SINGLE | 3 |
| probiotics-aad-prevention | Lewis et al57 | SWEEP_SECONDARY_SINGLE | 4 |
| probiotics-aad-prevention | Surawicz et al70 | SWEEP_SECONDARY_SINGLE | 4 |

**PRIMARY_VERIFIED through a meta row found in the trial's own text:** 0
(none). It still goes through the tracker merge (unit of
analysis, scope) before it counts.

**Why meta rows were refused** (all rows of the 141 trials):

| refusal reason (meta rows) | rows |
|---|---|
| MEASURE_RR_IS_NOT_ESTIMAND_HR | 27 |
| OUTCOME_NOT_THE_TOPICS | 25 |
| TIMEPOINT_NOT_STATED_BY_META | 20 |
| MEASURE_OR_IS_NOT_ESTIMAND_HR | 6 |
| MEASURE_RR_IS_NOT_ESTIMAND_OR | 4 |
| TIMEPOINT_30 days_NE_28 days | 4 |
| CROSSCHECK_DISAGREES | 3 |
| MEASURE_OR_IS_NOT_ESTIMAND_RR | 3 |

## Stale sweep: a finding for the Captain (G1-relevant)

The committed sweep outputs (6-10 Oct) predate gates now on main. Re-run under main's current code, **5 trials leave a
counted route:**

| trial | committed (main) | refreshed |
|---|---|---|
| **HEART-FID (iv-iron, ACTIVE)** | SWEEP_AACT_PRIMARY | AACT_ONLY_SINGLE_SOURCE, `NO_POSTED_ANALYSIS_ON_THE_ESTIMAND` (HR topic; posted counts only) |
| GISSI-P (omega3) | SWEEP_SECONDARY_SINGLE (RR) | ROWS_NOT_VERIFIED, `MEASURE_RR_IS_NOT_ESTIMAND_HR` |
| Nilsen 2001 (omega3) | SWEEP_SECONDARY_SINGLE (RR) | ROWS_NOT_VERIFIED, `MEASURE_RR_IS_NOT_ESTIMAND_HR` |
| Einvik 2010 (omega3) | SWEEP_SECONDARY_SINGLE (RR) | ROWS_NOT_VERIFIED, `MEASURE_RR_IS_NOT_ESTIMAND_HR` |
| Risk & Prevention 2013 (omega3) | SWEEP_SECONDARY_SINGLE (RR) | ROWS_NOT_VERIFIED, `MEASURE_RR_IS_NOT_ESTIMAND_HR` |

If the served G1 is computed from the committed sweep, it counts HEART-FID through a route main's own code no longer
produces: **G1 -1 on an active topic** when regenerated. The lane did not commit the refreshed sweep; regeneration and
the signing packet are the Captain's. 20 other verdict changes are relabels between non-counted states.
