# k-gap phase 3 (open sources), second scope: REGISTERED trials not filled by phases 1-2 (13 Oct 2026)

The source ladder's phase 3 covers every trial still missing, not only the identity-less. This scope covers the
registered trials (an NCT) that phases 1-2 did not fill and that carry a PMID: **42**. Census:
`scripts/g1_open_census.py --registered` -> `PHASE3_OPEN_CENSUS_REGISTERED.json`. Runner:
`scripts/g1_open_fill.py run ... --registered [--model]` -> `phase3_registered/<slug>.json`.

Pilot: pcsk9, omega3, corticosteroids-covid (the most open copies, one active G1 topic); then the other 9 topics.

| topic | registered trials, PMID, not filled | open copy | not eligibility-blocked | text held | typed find | model read (CC BY/CC0) | admissible |
|---|---|---|---|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | 2 | 1 | 1 | 1 | 1 | 0 | 0 |
| colchicine-postop-af | 1 | 1 | 1 | 0 | 0 | 0 | 0 |
| colchicine-secondary-cv-prevention | 2 | 2 | 2 | 1 | 0 | 0 | 0 |
| corticosteroids-cap-mortality | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| corticosteroids-covid19-mortality | 4 | 4 | 4 | 4 | 0 | 0 | 0 |
| iv-iron-hfref-hosp | 2 | 2 | 2 | 2 | 0 | 1 | 0 |
| metformin-pcos-ovulation | 2 | 1 | 0 | 0 | 0 | 0 | 0 |
| omega3-cardiovascular-events | 10 | 8 | 3 | 2 | 0 | 0 | 0 |
| pcsk9-mace | 8 | 7 | 5 | 3 | 0 | 0 | 0 |
| probiotics-aad-prevention | 2 | 1 | 1 | 1 | 0 | 0 | 0 |
| statins-primary-prevention-elderly | 3 | 2 | 2 | 1 | 0 | 0 | 0 |
| ticagrelor-vs-clopidogrel-acs | 3 | 2 | 0 | 0 | 0 | 0 | 0 |
| **total** | 42 | 31 | 21 | 15 | 1 | 1 | 0 |

**Funnel:** 42 -> open copy 31 -> not eligibility-blocked 21 -> text held 15 -> typed find 1 -> model read 1 -> **admissible 0**.

**Decisions by count:** {"TYPED_FOUND_REFUSED_UNIT_OF_ANALYSIS": 1, "NOT_OPEN": 11, "NO_TEXT_LAYER_OR_NOT_FETCHED": 6, "TYPED_NONE_NOT_MODEL_LICENSED": 12, "MODEL_NOT_SHOWN:HELD_NOT_OPEN_LICENSED": 1, "MODEL_NOT_ADMITTED_NO_GATED_READING": 1, "ELIGIBILITY_BLOCKED_QUEUED_TO_SCREENING": 10}

**The finds and the model reads:**
- **SMART (balanced-crystalloids):** the whole-trial count, read deterministically from the PMC author manuscript (its
  totals equal the 15,802 randomised). It is **refused on unit of analysis**: SMART is cluster-crossover, and the
  tracker refuses unadjusted counts from a cluster design (`g1_tracker.acquired_merge`,
  UNIT_OF_ANALYSIS_ADJUSTMENT_UNAVAILABLE). The runner now applies the same rule (planted).
- **EFFECT-HF (iv-iron, ACTIVE topic):** CC BY PMC text; the typed step found nothing, so codex + agy read it. Both
  readers refused (SOURCE_ABSENT): HF hospitalisations are given as patients per arm, in the **safety set**, with no
  HR. The earlier acquisition read had **no text** ("full text is withheld"); this read had it. A windowing check
  confirms the decisive sentence was in the shown evidence.
- **REMAP-CAP hydrocortisone (corticosteroids-covid, ACTIVE):** CC BY by Unpaywall, but the held copy is a university
  repository landing page. The harness does not show it (`HELD_NOT_OPEN_LICENSED`), so there was no model read.
- **CoDEX, CAPE COVID, Metcovid (corticosteroids-covid, ACTIVE):** open copies with no licence. For CoDEX and CAPE COVID
  the Unpaywall copy is the PMC article web page (an emergency-licence PMC copy outside the OA subset), collapsed to a
  single line by the HTML-to-text step, so the line-based typed reader cannot see their tables. Any find there would be
  PENDING_RULING (no licence) in any case. They had been "NO_OPEN_SOURCE" in the acquisition lane through the DOI lookup
  gap.

**Phase 3, second scope: 0 admissible.**
