# Notice for Mahmood: three held "comparator full texts" are other papers

Lane G1 (g1/doac-vte-recurrence), 2026-10-03. **A notice only, not a change:** nothing served was edited (MAIN is
frozen), and nothing here is signed. A lane never signs on your behalf.

## What is wrong

`cache/<slug>/records.json#comparator_fulltext` holds a different article's PMC text for 3 of 32 topics:

| topic | comparator PMID | own PMCID? | what the held text actually is |
|---|---|---|---|
| doac-vte-recurrence | 24963045 (van Es 2014, Blood) | none | a review of thrombophilia testing / DOAC interference with protein C assays |
| colchicine-recurrent-pericarditis | 22442198 (2012 meta-analysis) | none | a later pericarditis paper naming AIRTRIP and MAVERIC, which the 2012 comparator could not cite |
| corticosteroids-cap-mortality | 38128217 | none | a different CAP article (k_gap_table already flags it: 0 shared abstract shingles) |

The PMCIDs come from NCBI ID conversion of all 32 comparator PMIDs on 2026-10-03, run through the PubMed tool. 29 of
the 32 have their own PMCID. These 3 have none, so any PMC text held under their PMID belongs to a different paper.

## Root cause

Before `f32c307a` (2026-09-12 23:07), `harness/fetch.py::_pmc_fulltext` took the first PMC link from elink. When the
article is not itself in PMC, that first link is `pubmed_pmc_refs`, i.e. a paper that cites it. The doac-vte cache
was fetched at 20:32 that same day, before the fix. The other two were fetched on 2026-09-11. None of the three caches
was ever re-fetched, and nothing that reads the field checks whose text it is.

## Measured impact

- **G1 tracker:** none. No comparator per-trial row for any of the 3 topics comes from these texts. doac-vte's
  pooled comparator result (RR 0.90, 0.77-1.06) is read from the real abstract.
- **Served build, `pipeline.py` comparator effect + comparator k:** none. Re-extracted for all 5 comparator outcomes
  across the 3 topics, abstract only versus abstract plus held text: 5 of 5 identical, and k identical on all 3 topics.
- **Not verified:** the other consumers of the field:
  - `harness/comparator_second_pass.py` (`comparator_text` -> `parse_trial_set`)
  - `harness/comparator_truth.py`
  - `scripts/r4_ambiguity_count.py`
  - `scripts/radius_r4_comparator.py`
  - `scripts/seed_comparator_panels.py`

  Any served comparator trial list or panel for these 3 topics that was built from the held text needs checking.

## Proposed fix (for the owner of the fetch/serve path; not done here)

1. Re-fetch these 3 caches with the current fetcher. All 3 have no own PMC copy, so their comparator full text
   becomes `""`, which sends them down the abstract path.
2. Add a read-time gate: refuse `comparator_fulltext` unless `k_gap.held_text_identity()` reads `NAMED_ARTICLE`.
   The check already exists and already flags doac-vte and corticosteroids-CAP.
3. Plant: a held text that shares no shingles with the comparator's abstract must be refused.
