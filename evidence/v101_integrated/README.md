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
| Funding labels (typed funders / material support / funder-role statement) | 167 of 272 rows, 31 topics | `FUNDING_LABEL_CHANGES.json` |
| X2 comorbidity exclusions that flip | 6 of 539 (2 now included, 4 now excluded on X3, the comparator axis) | `COUNTS.json` |
| Registry IDs resolved to a publication before any results-only / ghost label | 59 NCTs in 13 topics | `COUNTS.json` |
| Comparator full texts refused (a citing article held under the comparator's PMID) | 3 of 32 | `COUNTS.json` |

- **Funding.** No row loses an industry tie. 121 rows carry an established tie, and no row is labelled "no industry
  tie": a public funder named "and others" never establishes absence.
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

## DOAC-VTE (van Es 2014)

- 6 trials shared by name: 5 input-identical, 1 with different inputs. Hokusai-VTE enters van Es with on-treatment
  counts and ours with the overall-study result; its window and analysis set differ.
- Positive control, reproduced by our engine: RR 0.901688 (0.766115-1.061252), tau2 0, Q 4.155222. The result is
  conditional on the one row not held (Hokusai on-treatment 66/4,118 vs 80/4,122).
- With our held Hokusai row the same pool is 0.913907 (0.78938-1.05808).
- The comparator's phase-3 scope is recorded as the comparator's; our screening has no phase rule.
