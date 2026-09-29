# acq/k-gap — STEP 1 report: the k-gap table (2026-09-29)

> **CORRECTION (later on 2026-09-29) — current figures.** An independent second reader found 4 of 40 identities
> wrong, all in omega-3. That comparator's own table is numbered one off from its reference list, and the resolver
> followed the links faithfully. Citation links are now followed only when the row's label does not contradict
> them, and a systematically shifted table is distrusted as a whole (see `IDENTITY_AUDIT.md`). Rebuilt table:
> confirmed-set trials **233** (was 239); pooled **54** (was 53); missing **179** (was 186).
>
> - Missing by class: identification 70, screen/eligibility 48, acquisition 16, extraction 13, measure 6, scope 11,
>   unavailable 15.
> - Of the 162 non-refused: AACT 7, PMC OA 32, Unpaywall 49, abstract 8, none 66.
> - Open-source ceiling **150 of 233**.
>
> The body below keeps the original figures as first reported. Every conclusion stands; the step-2 counterfactuals
> were rerun on the corrected table with the same results.

Branch `acq/k-gap`. Artefacts: `outputs/k_gap/k_gap_table.{json,csv}`, `SUMMARY.md`, `IDENTITY_AUDIT.md`.
Rebuild: `python scripts/k_gap_table.py && python scripts/k_gap_summary.py` (`--offline` replays the caches).

## 10-line summary

1. **32** topics with a comparator meta. Comparator trial set **confirmed for 24**: 20 from the comparator's own
   JATS included-studies table (cells cite the reference list -> PMIDs, parsed, no model); 4 from a recorded,
   gated model proposal (verbatim quote in the whole held text). 7 more only as **candidates** from the
   comparator's open reference list; 1 not enumerable from open sources (denosumab NMA).
2. **2 of 32 held comparator texts are a different article** than the cited comparator (doac-vte-recurrence,
   corticosteroids-cap-mortality): 0 shared abstract 6-shingles vs 22-874 for the other 30. Any comparator check
   run on them checked the wrong paper.
3. Confirmed set: **239** drug-specific trial families. **We pool 53 (22%)**; missing **186**.
4. Missing by class: identification **71**, screen/eligibility 50, acquisition 18, extraction-from-table 14,
   deliberate refusals 18 (measure mismatch 7, comparator-scope 11), genuinely unavailable (open) 15.
5. Of the 168 missing that are not deliberate refusals, an open source that could supply a typed result:
   AACT posted results **7**, PMC OA full text **35**, Unpaywall OA copy **49**, PubMed abstract (not-yet-extracted
   trials only) **8**; **none found 69**.
6. Identification (71) is the largest class and the cheapest: 69 of 71 already resolve to a PMID. For those
   71: PMC OA 20, Unpaywall 16, abstract 5, AACT 2, none 28.
7. AACT is a small lever here (7 of 168), and 5 of those 7 are hazard/rate/mean results, not 2x2 counts.
8. Largest gaps (confirmed set): probiotics 29/36, omega-3 25/28, metformin-PCOS 21/23, melatonin 18/19,
   statins-elderly 12/12, colchicine-secondary 11/15.
9. Not probed yet: Drugs@FDA reviews, EMA EPARs, NICE committee papers, OA supplements.
10. Identity instrument: 24 of 25 seeded rows confirmed, 1 unverifiable (`IDENTITY_AUDIT.md`; the labeller is
    the resolver's author).

## "How long?" — the data-based answer

- **Ceiling with open sources as probed today: 53 + 99 = 152 of 239 (64%)** of the comparators' drug-specific
  trials. The other 69 have no open source among AACT / PMC / Unpaywall / abstract. That is before screening
  and eligibility: many of the 50 screen/eligibility gaps are correct exclusions under our registered PICO
  (H. pylori regimens in probiotics, TXA prophylaxis vs treatment), and those do not close.
- **Order by yield, per the table:**
  1. **Identification (71; 69 with PMID).** A search/config change feeding the existing fetch + identity chain
     (comparator-reference seeding already exists in `harness/fetch.py`, but is off or missing for these). Hours
     of work. It closes *identification*, not k: each trial still has to pass the admission gate.
  2. **OA full-text tables: PMC 35 + Unpaywall 49.** PMC JATS tables parse deterministically (the step-1 code
     already does it). Unpaywall copies are mostly publisher PDFs, which need PDF table extraction, so they are
     slower. Days.
  3. **AACT results: 7.** Small, mostly HR/rate.
- **A time in days cannot honestly be given for k until the first adapter reports its conversion rate**
  (identified -> admitted). Step 2 measures exactly that, topic by topic, after each adapter.
