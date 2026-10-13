# k-gap phase 3 (open sources): pilot + scale, 13 Oct 2026

Scope: the phase-1 funnel's identity-less missing trials that carry a PMID, **61**. The "59" in the instruction is the
pre-#100 count of "no registration stated". After #100 r1 that is 58, plus 1 PubMed record with no abstract, plus 2
trials registered outside CT.gov (ANZCTR), all included here. Census: `scripts/g1_open_census.py` ->
`PHASE3_OPEN_CENSUS.json` (Europe PMC + Unpaywall, retrieved 13 Oct). Runner: `scripts/g1_open_fill.py` ->
`phase3/<slug>.json`. Tests: `tests/test_open_fill.py`, 4 passed.

**Method:**
- Deterministic first. PMC tables go through `g1_trial_acquire.table_tuple`; prose (PDF / HTML) goes through
  `g1_regulatory_source.typed_counts`, which needs one outcome line with two percent-corroborated e/N cells and an arm
  header naming both.
- A find is admissible only from a copy the existing gate accepts (`OPEN_COPY`: PMC CC / author manuscript; an
  Unpaywall copy under a 'cc' licence). A find from an unlicensed (bronze / green) copy would be
  `TYPED_FOUND_PENDING_RULING`.
- Only CC BY / CC0 text may go to a model (D8).

Pilot: metformin, probiotics, colchicine-secondary (the 3 topics with the most open copies). Then scaled to the other 6
topics with scope.

| topic | trials (PMID, no registration) | open copy | not eligibility-blocked | text held | typed find | admissible | model-eligible (CC BY / CC0) |
|---|---|---|---|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | 2 | 1 | 1 | 0 | 0 | 0 | 0 |
| colchicine-secondary-cv-prevention | 4 | 4 | 4 | 1 | 0 | 0 | 0 |
| corticosteroids-cap-mortality | 4 | 1 | 1 | 0 | 0 | 0 | 0 |
| melatonin-primary-insomnia-sol | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| metformin-pcos-ovulation | 21 | 7 | 2 | 1 | 0 | 0 | 0 |
| omega3-cardiovascular-events | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| probiotics-aad-prevention | 20 | 8 | 5 | 4 | 0 | 0 | 0 |
| statins-primary-prevention-elderly | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| ticagrelor-vs-clopidogrel-acs | 4 | 2 | 1 | 0 | 0 | 0 | 0 |
| **total** | 61 | 23 | 14 | 6 | 0 | 0 | 0 |

**Funnel (all 61):** 61 -> open copy 23 -> not eligibility-blocked 14 -> text held 6 -> typed find 0 -> **admitted 0**. Model-eligible: 0.
**The 58 'no registration stated' trials** (the instruction's 59 minus the 1 that #100 r1 retyped as a PubMed record with no abstract; the 2 registered outside CT.gov are also excluded): 58 -> open 22 -> not eligibility-blocked 13 -> text 6 -> typed 0 -> admitted 0.

**Decisions by count:** {"NOT_OPEN": 38, "NO_TEXT_LAYER_OR_NOT_FETCHED": 8, "TYPED_NONE_NOT_MODEL_LICENSED": 6, "ELIGIBILITY_BLOCKED_QUEUED_TO_SCREENING": 9}

**Why nothing was found (each text read by hand for the instrument check, not for numbers):**
- **NOT_OPEN (38):** no open copy at Europe PMC or Unpaywall. They go to phase 4 (published metas, SECONDARY).
- **Eligibility-blocked (9):** screener error, unaudited screen-out, or record insufficient on blinding or design. They
  are queued for the screening lane with their open-copy pointers (Wu, the only CC BY copy, is one of them).
- **No text (8):** Unpaywall lists the copy, but its location is a JavaScript landing page (11 chars of text) or none
  resolves.
- **Text held but not the article (3):** Sturrock's PMC page for a scanned article, and the Koning and Hennessy
  repository landing pages.
- **Article text, no deterministic tuple (3):**
  - Velasco reports percentages and an OR only; counts from percentages would be coercion.
  - Wong reports percentages; its RR line is a citation in the introduction.
  - Evans's result tables are "n (%)" with the N in the column header, a format `typed_counts` does not read.
- **Instrument limit, measured on this pilot:** the prose reader needs e/N (p%) cells. Tables written as n (%) under an
  (n = N) header are missed. Widening it is a reader change. It would also only matter for unlicensed copies, whose
  finds wait on the ruling anyway.

**Phase 3 yield: 0 of 61.** The live levers are:
1. the screening lane's 9;
2. the Captain's ruling on reading bronze / green copies, which so far has 0 finds to unlock;
3. phase 4 for the 38 not open.

The model stage (codex + agy + adjudicator, CC BY / CC0 only) had **0 eligible trials**: the only CC BY copy (Wu) is
eligibility-blocked.
