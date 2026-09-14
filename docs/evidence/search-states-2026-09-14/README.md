# Retrieval class as an object state; honest-state ratchet; regeneration of the 32 pages (2026-09-14)

**Fix state (four-state rule): VERIFIED** - the served labels and the ratchet refusal re-demonstrated by a non-author agent from a fresh clone (`docs/evidence/independent-verification-2026-09-14/09-*`, `11-*`). Not GENERALIZED. Independent verification here means a second agent, not an external human party.

| file | what it is |
|---|---|
| `01-prefix-hedge-not-state.txt` | before: 17 of 32 pages rendered a hedge ("has not been verified as a concept search vs known-item retrieval… pending that check") read from a side file at render time; no object carried a retrieval class |
| `02-regeneration-scientific-content-unchanged.txt` | after regenerating all 32 pages offline: every review object canonically identical to its predecessor once `search.retrieval_class` is stripped; no primary result moved |
| `03-ratchet-and-states-on-regenerated-pages.txt` | ratchet PASS against origin/main; 11 pages KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH, 21 TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH, the distinction sentence on 32, hedge on 0, labelled content hash on 32; a planted STALE drop → ratchet REFUSED |
