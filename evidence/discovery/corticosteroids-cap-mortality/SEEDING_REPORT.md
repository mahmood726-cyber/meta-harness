# V1.1 discovery -- can comparator-reference seeding be re-enabled for corticosteroids-cap-mortality?

**Why it was disabled.** The topic protocol turns seeding off because "the fixed NCT deduplication rule can let later
secondary/subgroup reports replace the original trial report", and checks recall with named positive controls
instead. This note tests that worry on this topic. The code is `seeding_test.py`, the raw results are in `run/`, and
the plants are `tests/test_discovery_cap_seeding.py`. Nothing here changes a served page or the topic config.

## What seeding would add
1. **The production adapter adds nothing here.** `harness.fetch._refs` (PubMed elink pubmed_pubmed_refs) returns
   **0 PMIDs** for the comparator PMID 38128217, because PubMed holds no reference links for this Elsevier article.
   The same call returns the GLP-1 comparator's list. So flipping `seed_comparator_refs` to true would add no record
   to this topic.
2. **A candidate V1.1 source does add records:** the comparator's reference list as deposited with Crossref (45
   references, 32 with a DOI). DOIs were resolved to PMIDs by PubMed esearch `[doi]`.
   - 30 PMIDs resolved and fetched with `harness.fetch._efetch`, of which **21 are new** to the topic's records.
   - References without a DOI are listed and not guessed.

## Result on that seed set (run/SEEDING_RESULT_crossref.json)
The watched reports are every pooled trial plus the positive controls: CAPE COD 36942789, Torres 25688779,
STEP 25608756, and 21636122, 33446608.

| grouping | watched reports displaced / moved | verdict |
|---|---|---|
| A. production dedup (`pipeline._dedup`: one record per NCT; pivotal, primacy, EARLIEST year) | 0 | no displacement on this seed set |
| B. V1.1 family linking (discovery `screen.trials`: one-NCT linking, hub guard) | 0 | seeding safe |

## The plants (so a null is not a blind spot)
Each plant uses the real CAPE COD record with a synthetic same-NCT report:
- **A later subgroup report** (2025) no longer replaces the primary under the current dedup. The earliest-year
  tie-break fixed the case the protocol names, so the protocol's stated reason is out of date.
- **An earlier same-NCT RCT-typed report** (2021) still displaces the primary under one-record-per-NCT. That is the
  residual defect. Under family linking both reports stay in one family (NCT02517489) and nothing is replaced.

## Recommendation for the captain
- **Seeding can be re-enabled safely once screening uses family linking** rather than one-record-per-NCT. Until then,
  a pivotal pin (`pivotal_trials`) protects the pooled reports.
- **Re-enabling must be a labelled protocol amendment**, not a config flip. The protocol text states the exclusion,
  so flipping the config alone would be a PROTOCOL_CONFIG_DIVERGENCE.
- **On this topic it only pays with a reference source other than PubMed elink** (e.g. the Crossref list above),
  because the production adapter returns nothing for this comparator.
