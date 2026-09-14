# Retrieval class as an object state; honest-state ratchet; regeneration of the 32 pages (2026-09-14)

**Fix state (five-state rule): REPORTED** - detector proven to miss the property it exists to protect: at b8925e04 the phrase-inventory ratchet passed while 15 pages lost a 'Search provenance' honest-state block (docs/evidence/regeneration-accounting-2026-09-14); block-level comparison was added at 005f2fd2 and is a separate claim

| file | what it is |
|---|---|
| `01-prefix-hedge-not-state.txt` | before: 17 of 32 pages rendered a hedge ("has not been verified as a concept search vs known-item retrieval… pending that check") read from a side file at render time; no object carried a retrieval class |
| `02-regeneration-scientific-content-unchanged.txt` | after regenerating all 32 pages offline: every review object canonically identical to its predecessor once `search.retrieval_class` is stripped; no primary result moved |
| `03-ratchet-and-states-on-regenerated-pages.txt` | ratchet PASS against origin/main; 11 pages KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH, 21 TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH, the distinction sentence on 32, hedge on 0, labelled content hash on 32; a planted STALE drop → ratchet REFUSED |
