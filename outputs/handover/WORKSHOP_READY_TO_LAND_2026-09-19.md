# Workshop register — 2026-09-19 ~02:30 (all branches off main 237e9094, pushed to the GitHub URL by name; the workshop landed nothing)

Codex usage limit was reached at ~01:50 (vendor message in the lane logs: "try again at Sep 23rd"). Lane AFF died at launch; TF's
process ended with its report written and its full standard unfinished (being run here). agy (Gemini) remains available.

Landing order. Every branch: plants proven pre-fix, tests green in the staging tree, 32 pages rebuilt where the harness changed,
review dirs whose object did not move restored to base bytes, ratchet 0 (acks signed after reading the diff, noted), retraction 32/32.
Under ws/HASHGATE the chain names `--allow-wrapper-only` the reviews whose only movement is the certificate re-binding analysis code.

| # | branch | sha | increment | objects moved |
|---|---|---|---|---|
| 1 | ws/HASHGATE | f8dcbdd5 | corrected landing hash gate (per-review review_sha256 named; html informational; wrapper-only must be declared); plant from the pre-fix script; re-check: 3f8add72->237e9094 PASS, 237e9094->75cc9a46 REFUSED 32/32 | 0 |
| 2 | ws/STRENGTHFIX | 68431b7f | CORRECTION of increment 1: STRENGTH (omega3) 5-point primary served as EXACT 3-point (binder fallback + "measure" gap); now registry 3-point 1.05 [0.93,1.19]; 0.9408 -> 0.9505 | 1 (omega3) |
| 3 | ws/FX | 4f5bfcc1 | item 1: FREEDOM-CVO LOCATED (Table 19); ELIXA CONFLICT (Table 8 vs text, both spans); FLOW located but REFUSED for admission (no retrieval record) | 0 |
| 4 | ws/DEL2 | 5de6894a | item 2: source-digest deletion invariant (6 gaps pre-fix); adjudication object NOT_CONSTRUCTIBLE (0/32 cite an ADJ id); 2 live digest defects corrected (pcsk9 CRLF digest; glp1 MedR rows) | 2 (glp1, pcsk9) |
| 5 | ws/MU | ba914b0b | item 3: mutation suite through the production route, 6/6 classes; 5 READY, 1 behind ELX | 0 |
| 6 | ws/RG | ffdfac6d | item 4: regression test per defect (AUD 1/2/3/4/7/8/9, pub-bias literal, generated_on, RUN_DATE x2, scorecard collision, CRLF custody); pinned pre-fix copies committed as fixtures; 1016 passed / 1 xfail (behind MU) | 24 |
| 7 | ws/NDCOUNT | b033fbbd | legend "(0 here)" counted the legacy spelling only | 21 |
| 8 | ws/D3COUNT | 32aff4a3 | grade D3 count missed label-keyed / absent records (glp1 7/8 -> 8/8, +5 pages); recount 32/32 | 6 |
| 9 | ws/ASC | fd635e84 | per-record ascertainment state (11/11) + funding denominator named (stale ELIXA row was counted: "9 of 9" -> 8 of 8) | 32 |
| 10 | ws/CD | ac150c30 | "checked dimensions: none" -> declared==enforced NOT_ESTABLISHED/ESTABLISHED/DIVERGENT from compared dimensions (14 ESTABLISHED, 18 DIVERGENT) | 32 |
| 11 | ws/CNT | 99a3fb2e | 1-vs-3 count: one membership object feeds every count surface incl. the gate's reference string; consistency check refuses disagreement | 32 |
| 12 | ws/LEG2 | 1be03497 (stacked on ws/STRENGTHFIX) | hand-verified rows bound to held bytes: 71 legacy rows -> 34 located (20 EXACT, 14 admitted+labelled), 37 unlocated (admitted+labelled), 0 refused; labels only | 0 numbers |
| 13 | ws/TF | cb04c75a | item 6: trial-family ledger transplant (FN/FNC) -- eligibility/strand/sources/conflicts/poolability; screening counts, missing-evidence panel, analysis membership derived; numerical preservation 32/32; caches regenerate byte-identically; FULL STANDARD ON THIS TREE: VERIFY-ALL 11/11 PASS (ledger committed) after one staging fix (comparator-panel alias resolution: TF keyed rows by family id and the glp1-vs-Giugliano overlap read Jaccard 0.0 -- the UI test caught it); caches 163 MB (chain decides on compaction) | 32 |
| 14 | ws/LITX | 93098a63 | LITX+IDX: assertion-literal sweep/registry/limb; 25 TRUE-DEFECT literals rewritten; index derived from objects (5 of 7 Gemini candidates confirmed) -- READY-BEHIND-CHK; ratchet pairing table UNSIGNED (131) in outputs/handover/ratchet_pairs_LITX.json | 32 + index |

## Not workshop-able / owed
- FLOW retrieval record in regulatory_sources_glp1.json (retriever); ADJ countersignatures (ELX); AFFIRM-AHF parity/refusal re-adjudication (lane AFF never ran -- brief at scratchpad/lanes/LANE-AFF.md, ready to launch when Codex returns).
- DEL3 (failed-check receipt deletion) waits on CHK landing.

## agy findings not in a branch
- LITX-staged index residue: 2 REFUTED by IDX with the object quoted; the rest fixed in IDX.
- TF-staged glp1 page (33 sections, 50 quotes): re-finds defects already staged (funding 9-of-9 -> ASC; legend -> NDCOUNT), plus for the chain: (a) the family count chain (238 families incl. registry-only) and screening.records (11 publication records) are two populations the page should name as such; (b) the family ledger's registry-based eligibility UNKNOWN beside the publication screen's include (FN's contributing_without_structural_eligibility) reads as a disagreement unless labelled as two instruments; (c) the served eligibility clause promises "an OPEN recovery obligation rendered until [the result] is held" while ELIXA's row carries no obligation object (machine_absent) -- belongs with ELX's SOURCE_RETRIEVED_NOT_EXTRACTED state.
