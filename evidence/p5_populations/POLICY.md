# P5 population evidence -- resolution policy (declared before any new search; evid2, 2026-09-24)

**Status: DECLARED.** Committed before evid2 ran any new search or acquisition for the 53 P5-unestablished pooled rows.
Disclosed honestly: when this was written, the predecessor lanes' states were already known to evid2 (EV53 completeness
36 / 16 PARTIAL / 1 NONE; evid's entry rulings ESTABLISHED 49, PARTLY 3, NOT_ESTABLISHED 1). The policy was therefore
not blind to those states; it is binding on everything evid2 does from here, and no rule below may be changed after a
result is seen without a new dated section that says what changed and why.

This is an **engineering decision delegated to evid2** (the brief: "decide and record"). It decides how evidence is
*recorded*. It does **not** admit any row: admission, and whether abstract text may stand at registry rank, is
Mahmood's decision D04.

## Unit
One record per (row, fact) where the facts are the ones EV53 derived from each row's ordered P5 blocker chain
(`entry_population`, `randomized_contrast`, `registry_parent`, `placebo_control`, `blinding`, `adult_age`,
`parallel_design`, ...). N = 53 rows, fixed at the population frozen in `evidence/inputs/the53.json`; the denominator
never shrinks.

## States (exactly one per record)
| state | meaning |
|---|---|
| `RECOVERED` | a span in a document of the SAME trial (its own report, registry record, protocol or SAP) states the fact, and the span is re-found verbatim in bytes whose sha256 is recorded -- re-checked by evid2's script, not copied from a predecessor's `verified: true` |
| `ESTABLISHED_ABSENT` | a span of the same trial states the OPPOSITE of what the screen requires (e.g. the comparator is usual care, not placebo). This is evidence, not a gap; the row stays in the population and the screen's refusal is correct |
| `UNRESOLVED` | after the search below, no span states it. The record names the missing element, every search performed (query, source, date, result count) and why the result does not state it |

## What never counts as evidence
- An inference from the outcome's name (e.g. "antibiotic-associated diarrhoea" does not establish that participants
  entered on antibiotics), from the disease (a disease does not establish an age floor), or from the era.
- A predecessor lane's `verified` flag without a fresh span re-location in the held bytes.
- A model's statement without a verbatim span; a search-engine summary; a secondary review describing the trial.
- A span from a DIFFERENT trial (a pilot, an extension, a pooled analysis) -- recorded as context, never as the fact.

## Search (stopping rule, per UNRESOLVED candidate fact)
1. Every document already held in the repo for the trial (cache/<slug>/, evidence/held/, evidence/packets/).
2. The trial's registry record(s) where an identifier is known (ClinicalTrials.gov, ISRCTN, ANZCTR, EU CTR).
3. Open-access full text of the trial's own report(s) via Europe PMC (PMCID resolution) -- and, for `registry_parent`,
   a verbatim search of that full text for a registration identifier.
4. At most two further documented Europe PMC queries for a same-trial protocol / design / baseline paper.
Anything acquired is recorded with URL, retrieval time and sha256; a document that may not be redistributed is held
local-only and listed in the ledger, never committed.
If the stopping rule is reached without a span, the fact is `UNRESOLVED`. A registry parent for a trial reported before
registration was customary is `UNRESOLVED` with the reason `NO_REGISTRATION_FOUND` -- not "does not exist", which no
search can show.

## Invariants
- **No trial is dropped.** Every one of the 53 rows appears in the output with every fact of its chain. A row whose
  facts are UNRESOLVED stays in the population, carries its served value unchanged, and is reported as such. Turning a
  check green by removing a trial is forbidden.
- Nothing here changes a served number. If a search surfaces a served-number defect, it is queued for Mahmood's
  hash-bound signature with a derived notice, never landed.
- Counts are reported as `n of 53` (rows) and `n of F` (facts), with the kinds of item enumerated before the number.
