# V1.0.1 integrated candidate (evid2/v101-integrated), 27 Sep 2026

This branch supersedes `evid2/v101-overlap`, `evid2/v101-colchicine` and `evid2/v101-population`. It carries their
work together with the fixtures from the colchicine-secondary, CAP, COVID-corticosteroids, dapagliflozin, denosumab and
DOAC-VTE reviews. All counts below are measured against V1 (`9eacfe09`) on a full 32-page rebuild; the JSON beside this
file holds the rows.

## Result-level

- **Pooled results moved: none** (`LABEL_CHANGES.json`). No pooled estimate, interval or pooled trial set changed on
  any page.
- Computed comparator overlap relation served on 32 of 32 pages: DISJOINT 2, IDENTICAL_SET 1, NOT_ENUMERABLE 19,
  OVERLAPPING 6, SUBSET 3, SUPERSET 1.

## Label changes, n of N

| Change | n of N | File |
|---|---|---|
| Funding labels (typed funders / material support / funder-role statement) | 171 of 273 rows, 31 topics | `FUNDING_LABEL_CHANGES.json` |
| X2 comorbidity exclusions that flip | 6 of 539 (2 now included, 4 now excluded on X3, the comparator axis) | `COUNTS.json` |
| Registry IDs resolved to a publication before any results-only / ghost label | 59 NCTs in 13 topics | `COUNTS.json` |
| Comparator full texts refused (a citing article held under the comparator's PMID) | 3 of 32 | `COUNTS.json` |

- **Funding.** Against V1, no row whose V1 label was industry loses its tie. 126 rows carry an established tie, and no
  row is labelled "no industry tie": a public funder named "and others" never establishes absence.
- **Funding audit** (`FUNDING_AUDIT.json`). Four codex lanes read the funding evidence independently. Every quote
  was located, and every disagreement was traced to a root cause.
  - On the 61 held full texts, 11 of 12 missed industry ties are recovered. The misses came from a reach cap, the
    sentence splitter, RX-OL9, author-contribution lines, and missing statement and supply phrasings. The twelfth
    (a branded product named in the methods) is not a tie, by decision.
  - One served row goes from PRESENT to NOT_ESTABLISHED: tocilizumab PMID 33472855. Its PRESENT rested only on
    author disclosures read as funders.
  - Author disclosures now stay out of funder lists. An author's company directorship blocks "no industry tie".
  - On the 222 rows without full text, a registry non-industry class now outranks a bare company suffix
    (TriHealth Inc. is a non-profit hospital system).
  - Open question for the captain: the Novo Nordisk Foundation is classed as industry by name (semaglutide PMID
    42070571).
- **ARTS-DN Japan harms.** Linking Katayama 2017 exposed its hyperkalaemia statement to the harm panel: "no patients
  developed hyperkalemia", across seven doses and a shared placebo. It is recorded as a sourced typed refusal
  (RETRIEVED_INCOMPATIBLE_STRUCTURE, as for ARTS-DN), not as an open HARMS_INCOMPLETE.
- **X2 flips.** CARDIA-STIFF (NCT04739215, dapagliflozin) and NCT05057806 (empagliflozin) are included at screening;
  neither is pooled.
- **Colchicine-secondary: flip deferred.** The comorbidity rule is checked there, and Raju 2012 would be included.
  But Raju reports an excess of diarrhoea with no arm counts in any held source, and the harms gate refuses such a
  page. The topic keeps its V1 screening; see `registry/population_witness_topics.json`.
- **Registry relinks.** A relink changes the GRADE publication-bias census wording. That domain is NOT_ASSESSED on
  every affected page, so no certainty rating moves. Example: tocilizumab 20 of ~38 → 18 of ~38 completed
  unpublished.

## Comparator full texts refused

`records.json` `comparator_fulltext` for van Es 2014 (doac-vte-recurrence), Imazio 2012
(colchicine-recurrent-pericarditis) and Cheema 2024 (corticosteroids-cap-mortality) were citing articles. They were
fetched before the same-article PMC link rule (f32c307a). `harness/held_text_identity.py` refuses them using
`cache/<slug>/pmc_links.json`.

- No served value came from those bytes.
- The DOAC and CAP comparator panels, which had certified the bytes as their held document, are now NOT HELD.
- The 61 held trial full texts were re-checked: each is the right article.

## GLP-1: the B-prime outcome-ascertainment clause is executed

The amendment admits a trial only if "3-point MACE, or its exact three components, was prospectively specified and
systematically ascertained". `screen_family` had skipped that half, so "145 eligible" counted STRUCTURAL passes.

- **Three states** (`harness/ascertainment.py`, `cache/glp1-ra-mace-t2d/ascertainment_evidence.json`):
  - STRUCTURAL_PASS 145.
  - FULL_ELIGIBLE 9: both halves evidenced from held bytes, the prospective source dated before the results.
  - PENDING 136: never eligible, never excluded; each carries a retrieval task for its protocol, SAP or supplement.
  - ADMISSIBLE_RESULT per analysis: MACE 7 of the 8 pooled.
- **SUSTAIN-6 is pooled but PENDING.** Its EU register record names MACE, but the register shows the current
  protocol version, so the date doesn't date that text. The pooled result is rendered as conditional on it; it is not
  removed.
- **Date tiers.** Harmony Outcomes' and PIONEER 6's design papers post-date trial completion but precede the results.
  They are marked DATED_BEFORE_RESULTS_ONLY, so the stricter reading stays visible.
- **Programme evidence.** Husain 2020 states that the SUSTAIN 1–5 and PIONEER 1–5, 7–10 glycaemic trials recorded
  MACE as adjudicated events. That supports ascertainment only. Their prospective specification needs each protocol,
  and the post-hoc pooled estimate never enters a pool.
- **PIONEER 8** (NCT03021187) is linked to Zinman 2019, PMID 31530667, by the token "PIONEER 8" printed in the
  registry acronym and the paper. Its two harm statements are sourced typed refusals.
- **Search execution records** (`harness/search_execution.py`): one row per declared source.
  - CENTRAL and ICTRP: NOT_EXECUTED.
  - PubMed, Europe PMC and citation chasing: EXECUTED_IDS_NOT_HELD. The 15 Sep search_v2 run's funnels and queries
    are recorded, its response bodies are not, and it is not this page's retrieval.
  - ISRCTN: CALLED_NO_RESULT_RECORD.
  - AACT: EXECUTED.
  - Trial-family assembly: MANUAL_ONLY.
  - Seeded, manual and legacy rows are rendered distinct. The source-status table's "Europe PMC: RAN_OK" was
    inferred from merged records, not a recorded execution.
- **Pooled results unchanged** (MACE HR 0.856, 0.8086–0.9061, k 8).

## Melatonin (Ferracioli-Oda 2013)

- **Scope, in its own words:** 19 studies in adults and children with primary sleep disorders (14 insomnia, 4
  delayed sleep phase, 1 REM sleep behaviour), 15 in the latency plot. "19 vs 1" is not 18 missing trials.
  - The stated count had been read as "not stated": the extractor knew only "trials"/"RCTs". `_K_STUDIES` now reads
    "N studies … were included".
  - A pre-existing off-by-one that cut the first letter of a quote at text start is fixed.
- **only_ours** comes from the pooled set (empty). Live main still lists the screened Xu and cancer studies.
- **Wade:** one trial at identity level (NCT00397189). Its inputs differ: all adults with PSQI-Q2 (reported by the
  review, not held) versus our 65–80 diary SOL (registry-held).
- **Display vs calculation** (`harness/comparator_display.py`; figure image held with sha256):
  - COMPARATOR_DISPLAY_ERROR for the swapped weights (Smits 2003 printed 3.97 vs 0.29 reconstructed; Almeida Montes
    printed 0.28 vs 3.94).
  - COMPARATOR_DISPLAY_ERROR for the objective-subgroup interval: 7.81 in the figure, 8.71 in the text and the
    reconstruction.
  - The pooled calculation reproduces: FE 7.0606 (4.3765–9.7448) vs published 7.06 (4.37–9.75). It is a positive
    control of our engine (`registry/positive_controls.json`).
- **Search:** "melatonin"[Title] is a title-restricted concept query, not seeding.
- **Cancer-insomnia study (27559258):** it enrolled DSM-IV primary insomnia, and "cancer" never excludes it. Its
  Athens Insomnia Scale is never converted to minutes; that is recorded as a sourced typed refusal.

## DOAC-VTE (van Es 2014)

- 6 trials shared by name: 5 input-identical, 1 with different inputs. Hokusai-VTE enters van Es with on-treatment
  counts and ours with the overall-study result; its window and analysis set differ.
- Positive control, reproduced by our engine: RR 0.901688 (0.766115-1.061252), tau2 0, Q 4.155222. The result is
  conditional on the one row not held (Hokusai on-treatment 66/4,118 vs 80/4,122).
- With our held Hokusai row the same pool is 0.913907 (0.78938-1.05808).
- The comparator's phase-3 scope is recorded as the comparator's; our screening has no phase rule.
