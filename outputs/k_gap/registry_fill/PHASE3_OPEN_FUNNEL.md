# k-gap phase 3 (open sources): started 13 Oct 2026, availability census

Scope: the phase-1 funnel's identity-less missing trials (no NCT). There are 83: **61 with a PMID**, which this phase covers, and **22 with no PMID**, which go to IDENTIFICATION_QUEUE.md.

Census: `scripts/g1_open_census.py` produces `PHASE3_OPEN_CENSUS.json`, retrieved 13 Oct. It queries Europe PMC REST (core) by PMID and Unpaywall v2 by the Europe PMC DOI, and compares the result with the PMC index the acquisition lane reads (`outputs/k_gap/fulltext_index.json`).

| class | n of 61 | what may be done (D8 and current gates) |
|---|---|---|
| OPEN_CC_MODEL_READABLE (CC BY / CC0) | 1 | typed first, then codex + agy (Wu et al31, probiotics) |
| OPEN_CC_OTHER_REGEX_ONLY (CC BY-NC / -ND) | 3 | typed only (Verma, Plomer, Shimbo) |
| OPEN_NO_LICENCE_REGEX_ONLY (bronze / green, no licence) | 19 | **none under the current gate** (see below) |
| NOT_OPEN | 38 | nothing open; phase 4 (published metas, SECONDARY) |
| LOOKUP_FAILED | 0 | -- |

**Why the 23 open copies are not 23 reads:**
- **Eligibility, not text (9).** Hoeger, Nestler and ticagrelor 6[25] have an insufficient record (blinding or design not stated). Palomba 2004, Palomba 2005a and Yarali have screener errors. Plomer, Shimbo and Wu have population-vocabulary or unaudited screen-outs. A full text may settle those facts, but that is a **screening** decision, so they are queued for the screening lane with their open-copy pointers, not acquired here.
- **The gate on uncertified copies (19).** `g1_trial_acquire.typed_first` reads a held copy deterministically only when it is legitimately open: a PMC copy under CC or a PMC author manuscript (`OPEN_COPY`), or an Unpaywall copy whose licence starts with 'cc'. Mahmood's ladder says "other OA text is regex-only", which implies bronze and green copies may be read deterministically. Admitting them would **loosen** that gate, so it is **proposed to the Captain, not made**.
- **CC copies.** Of the 4:
  - Verma: the acquisition target. Its CC BY-NC-ND copy has an Elsevier DOI that resolves to a JavaScript landing page with no text layer (`NO_OA_TEXT`), so there is nothing to read.
  - Plomer, Shimbo and Wu: all screening-blocked.
- **A cause found.** The acquisition route gets a DOI only from held records (`record_licence.pmid_doi`). For Verma none was held, so the lane never asked Unpaywall, and its "NO_OPEN_SOURCE" was a lookup gap, not an absence. Europe PMC supplies DOIs for these PMIDs. Feeding those in is a small typed change to propose with the census.

**Phase 3 yield so far: 0 admitted.** The next steps depend on the Captain:
1. a ruling on deterministic reading of bronze and green copies (19 trials);
2. the screening lane taking the 9 eligibility-blocked trials with their open copies.

The 38 not-open trials move to phase 4.
