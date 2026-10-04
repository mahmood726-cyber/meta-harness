# Dispatch from g1/forest-reader to acq/k-gap

## 4 Oct: the seven RESULT_AGREES priority topics

The k-gap lane asked for comparator per-trial rows (dual-model, recorded, pooled-reconstruction gate) for seven
topics. Each was checked against acq/k-gap `016928fc`.

Outcome: no new figure can be read legitimately for any of the seven.

- Two already have accepted comparator rows, and both reproduce the printed pool. For one of them (esketamine), the
  tracker has no comparator pooled result.
- One is already G1_MATCHED.
- Four have no readable per-trial figure for the topic outcome.

### Already supplied (rows at `521ed499`; G1-R REPRODUCED)

**esketamine-trd-madrs** (PMID 42490943)
- **Figure:** f4, "Acute induction: MADRS change from baseline to day 28 (random-effects)".
- **Rows:** 4, labelled Trial A, B, C and "D (older adults)".
- **Pooled:** MD −2.99 (−5.10 to −0.89). This is printed in the comparator's own text (its summary table: 937
  participants, 4 RCTs). The figure's rows reproduce it under DL.
- **For you:** the tracker's `comparator` block is empty (estimate null). Use this pool as the compared result.
- **Uncovered trials:** Trial E and Trial F are not in f4, which lists Trials A–D only. f4 is the comparator's only
  per-trial MADRS day-28 plot; its supplement figure 5 is an age-subgroup pool. Trial D is in the rows under the label
  "Trial D (older adults)", so it is a join miss.

**iv-iron-hfref-hosp** (PMID 39727669)
- **Figure:** diseases-12-00339-f003, total HF hospitalizations.
- **Rows:** 5.
- **Pooled:** OR 0.59 (0.40–0.88), also printed in the comparator's text. It reproduces under DL and equals the served
  `comparator.reported`.
- **For you:** RESULT_AGREES fails on OUR side, where "ours" is INCOMPATIBLE (first-event HR + incidence-rate ratio).
  It is not a missing comparator row.

### Already matched

**noac-vs-warfarin-af-stroke** (PMID 34985309, COMBINE AF)
- **Status:** G1_MATCHED; RESULT_AGREES is already true.
- **Why no rows:** its only forest figure (F1) has outcome rows from a one-stage individual-patient model. It has no
  trial rows to read. It was read, and refused as NOT_RECONSTRUCTABLE.
- **Supplement:** NIHMS1764416-supplement is absent from the PMC OA bucket.

### Not readable from a legitimate open source (probe records under `cache/comparators/<pmid>/`)

| topic | PMID | every open location tried | result |
|---|---|---|---|
| doac-vte-recurrence | 24963045 | ASH publisher PDF (Unpaywall, OpenAlex); CORE holds only a Swepub metadata record | publisher Cloudflare challenge; CORE has no file |
| corticosteroids-cap-mortality | 38128217 | Elsevier landing (cc-by-nc); Cardiff ORCA PDF; CORE download 595560423 | landing is HTML only; ORCA and CORE are Cloudflare challenges; the CORE API has no full text |
| colchicine-recurrent-pericarditis | 22442198 | BMJ Heart PDF; Milan AIR repository; CORE download 195773452 | all Cloudflare challenges; the CORE API has no full text |

A challenge is recorded, never solved. Rows come only if Mahmood (or someone with legitimate access) places a copy
of these papers in the cache, for example by downloading them himself from the open publisher pages.

### No per-trial topic-outcome figure exists

**dpp4-mace-t2d** (PMID 34754403)
- The comparator has one forest figure (F1). Its panels A–F are MI, stroke, HF hospitalisation, unstable angina,
  revascularisation and CV mortality.
- It has no tables and no supplement.
- Its text never reports a pooled 3-point MACE.
- So there is no MACE row to read. RESULT_AGREES cannot be met against this comparator for a MACE estimand. The
  served MACE comparator value, if any, should be checked against the paper; MACE appears only in its background.

### Join misses (rows exist in accepted comparator figures, but your tracker leaves the trial uncovered)

| topic | your trial label | accepted row label |
|---|---|---|
| probiotics | Lönnermark | Lnnermark 2010 |
| colchicine-secondary | Akrami, Mewton | Mehdi Akrami–2012, Mewton N-2019 |
| corticosteroids-covid19 | hydrocortisone 21-day mortality trial | CAPE COVID |
| dapagliflozin-hfpef | SOLOIST-WHF, SCORED, EMPEROR-Preserved | combined SOLOIST-WHF/SCORED row; EMPEROR-P |
| empagliflozin-hfpef | EMPEROR-Preserved (your labels are titles) | EMPEROR Preserved 2021 |
| esketamine | Trial D | Trial D (older adults) |
| sglt2-hfref | EMPEROR-Reduced, SOLOIST-WHF | EMPEROR-Reduced †, SOLOIST-WHF ‡ |
| sglt2-primary-prevention | Zinman | Zinman 2016 |
| statins | Alpérovitch | Alperovitch et al 2015 |

### Rows you have not merged yet

`521ed499` adds two more comparator figures:

| figure | rows | pooled reproduces |
|---|---|---|
| colchicine-secondary F11 | Akodad 2017, Shah 2020 | 0.90 (0.54–1.51), MH |
| spironolactone F2 panel D | TOPCAT (+ 3 finerenone trials) | 0.91 (0.85–0.99), FE |

Both appear in `meta_results` with role `comparator` and key `<slug>::<pmid>::<fig>`. `accepted_rows(slug)` returns
them with `meta_pmid` set to the comparator's PMID.
