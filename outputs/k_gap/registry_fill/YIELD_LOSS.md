# Where the k-gap yield is lost: the 141 missing comparator trials, through all four phases (13 Oct 2026)

**Result: 0 of 141 counted.** One trial (SALT) passed the acquisition gates and was refused at merge on unit of
analysis. Every other trial stops at a typed reason. The losses, largest first:

| # | where the trial stops | trials | kind of loss | lever |
|---|---|---|---|---|
| 1 | **no identity**: no NCT and no PMID, or no registration stated | 83 have no NCT (61 with a PMID, 22 with neither) | identification | citation chase / Crossref (IDENTIFICATION_QUEUE.md); open-text census by PMID (phase 3) |
| 2 | **registered, nothing posted** on CT.gov | 36 | source does not exist | none in the registry; later phases |
| 3 | **no open copy** of the report (phase 3) | 38 of 61 identity-less; 11 of 42 registered | paywall | none (no paywall is circumvented) |
| 4 | **blocked at SCREENING, not text** (phase 3) | 9 + 10 | eligibility | screening lane; the open copies are queued with pointers |
| 5 | **posted, but no outcome binds** (phase 1) | 18 | outcome not posted, or posted as % / rate | see the breakdown below |
| 6 | **meta rows refused on the effect MEASURE** (phase 4) | 40 rows (RR/OR v an HR estimand, or v the reverse) | estimand policy | ruling: which measures may stand in for the topic's estimand |
| 7 | **meta rows on another outcome / no stated timepoint** (phase 4) | 25 + 20 rows | definition | none (correct refusals) |
| 8 | **regulator documents**: named, but no per-trial result on the protocol estimand / population | FDA 11, EMA 8, G-BA 13, NICE 21 named; 0 typed | estimand / population / definition | none (G-BA pcsk9 Table 4-52: safety set + RR + broader composite) |
| 9 | **unit of analysis**: cluster designs give unadjusted counts | 2 (SALT, SMART) | design | a cluster-adjusted effect source |
| 10 | **unlicensed open copy**: a deterministic find awaits the ruling | 1 (CoDEX, ACTIVE topic) | licence policy | dispatch decision 1 |
| 11 | **landing pages / no text layer** where the copy is listed as open | 8 + 6 | retrieval | none deterministic (JS pages) |

## The 18 posted-result trials that did not match the outcome (phase 1), by count

| furthest gate | trials | which |
|---|---|---|
| OUTCOME_NOT_NAMED: nothing in the outcome family posted | 7 | Pahor, Gao, ODYSSEY COMBO I, FH I, FH II, HIGH FH, DESCARTES, GLAGOV (lipid / atheroma outcomes only; FH I and FH II share one NCT pair) |
| OUTCOME_NOT_NAMED: a family title IS posted, but it is not the protocol outcome | 7 | BACC-Bay (KM %, mITT), CORIMUNO-TOCI-1 and -ICU (survival % + per-stratum HR), COV-AID (time-to-composite), COVIDOSE2 (30-day survivors, low-dose arms), ORIGIN (the glargine factor; omega-3 not posted) |
| ARMS: outcome named, posted only as a rate or % (no event counts) | 4 | ODYSSEY LONG TERM, EMPACTA, REMDACTA, Ehrhardt |
| ESTIMAND: named, refused on timepoint / definition | 0 | -- |

**No named-divergence admission is possible among the 18 without coercion** (counts from percentages, death as the
complement of survival, another factor's arms).

## What would move the number (each needs a ruling, none is the lane's)

1. **Unlicensed-copy deterministic tables** (dispatch decision 1): +1 candidate on an active topic (CoDEX), through a
   signing packet.
2. **The effect-measure policy for meta rows** (40 rows refused on measure alone): the largest single phase-4 lever.
   It is a methods decision (RR for HR is not an equivalence).
3. **Screening-lane resolution** of the 19 eligibility-blocked trials that have open copies.
4. **Identification** of the 22 with no PMID (19 have a known non-PubMed reference).

**Also for the Captain:** the committed sweep is stale against main's current estimand gates (PHASE4_SECONDARY.md).
HEART-FID would leave a counted route on regeneration.
