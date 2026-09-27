# Acquisition cascade report: colchicine-recurrent-pericarditis fixtures

346 recorded attempts; 146 held open-access documents ({'PRIMARY': 26, None: 1, 'SECONDARY_SOURCE': 119}). Legitimate open routes only; every attempt is in `ATTEMPTS.jsonl` with URL, time, status and sha256.

| Trial | Target | Status | Tier served | Counts | Conflict | Reviewer expected |
|---|---|---|---|---|---|---|
| ICAP | Recurrent pericarditis | **NOT_FOUND** | — | — | — | 11/120 vs 25/120 (recurrent course, NEJM Table 2) |
| ICAP | Adverse events (gastrointestinal) | **NOT_FOUND** | — | — | — | 11 vs 10 |
| ICAP | Treatment discontinuation | **NOT_FOUND** | — | — | — | 14 vs 10 (Table 3) / 14 vs 12 (flow diagram): endpoint-scoped SOURCE_INTERNALLY_INCONSISTENT |
| CORP | Adverse events (gastrointestinal) | **NOT_FOUND** | — | — | — | 4/60 vs 3/60 |
| CORP | Treatment discontinuation | **NOT_FOUND** | — | — | — | 5/60 vs 4/60 |
| CORP-2 | Recurrent pericarditis | **FOUND_PRIMARY** | PRIMARY | [[26, 120], [51, 120]] | — | 26/120 vs 51/120, and what its '0.49' is |

## Per target

### ICAP — Recurrent pericarditis: NOT_FOUND
- refused: `_secondary/PMC6720402.xml` — row label does not name the target endpoint /recurren/
- refused: `_secondary/PMC9531702.xml` — its value [16.7] equals the excluded endpoint's percentage [16.7, 37.5] (the row is mislabelled)

### ICAP — Adverse events (gastrointestinal): NOT_FOUND
- refused: `_secondary/PMC6720402.xml` — row label does not name the target endpoint /gastrointestinal/
- refused: `_secondary/PMC9531702.xml` — row label does not name the target endpoint /gastrointestinal/

### ICAP — Treatment discontinuation: NOT_FOUND
- refused: `_secondary/PMC6720402.xml` — row label does not name the target endpoint /discontinu|withdraw/
- refused: `_secondary/PMC9531702.xml` — row label does not name the target endpoint /discontinu|withdraw/

### CORP — Adverse events (gastrointestinal): NOT_FOUND
- refused: `_secondary/PMC6720402.xml` — row label does not name the target endpoint /gastrointestinal/
- refused: `_secondary/PMC8886190.xml` — row label does not name the target endpoint /gastrointestinal/
- refused: `_secondary/PMC9531702.xml` — row label does not name the target endpoint /gastrointestinal/

### CORP — Treatment discontinuation: NOT_FOUND
- refused: `_secondary/PMC6720402.xml` — row label does not name the target endpoint /withdraw|discontinu/
- refused: `_secondary/PMC8886190.xml` — row label does not name the target endpoint /withdraw|discontinu/
- refused: `_secondary/PMC9531702.xml` — row label does not name the target endpoint /withdraw|discontinu/

### CORP-2 — Recurrent pericarditis: FOUND_PRIMARY
- PRIMARY `cache/colchicine-recurrent-pericarditis/records.json#PMID-24694983` sha256 `69b0f26fee0d411d…` “The proportion of patients who had recurrent pericarditis was 26 (21·6%) of 120 in the colchicine group and 51 (42·5%) of 120 in the placebo group (relative risk 0·49;” → [[26, 120], [51, 120]]
- corroboration only (percentages, no counts): SECONDARY_SOURCE `_secondary/PMC6720402.xml` Table 1 row ['08', 'Imazio M. et al., CORP-2 (10)', '2014', 'Multicenter, randomized, double blind', 'PER recurrence', '240', '50', '48.8', '6', '20'] → [8.0, 50.0, 48.8, 6.0, 20.0]
- corroboration only (percentages, no counts): SECONDARY_SOURCE `_secondary/PMC9531702.xml` Table 1 row ['Efficacy and Safety of Colchicine for Treatment of Multiple Recurrences of Pericarditis [ 11 ]', 'CORP-2', '2014', '240', '21.6'] → [21.6]

## What CORP-2's '0.49' is

The abstract prints 'relative risk 0.49; 95% CI 0.24-0.65' beside 26/120 vs 51/120. The counts give RR 0.510 (95% CI 0.342-0.760). Read as a relative risk the printed figure is 0.5501 log-units away; read as a relative risk REDUCTION (1 - RR, interval flipped) it is 0.0236 away. Verdict: **MISLABELLED_RRR**: 0.49 is the relative risk reduction under the label 'relative risk'.

## Routes attempted, per trial

- ICAP: ema_search:BLOCKED_HTTP_401 ×2; europepmc_fulltext:NOT_OPEN_ACCESS ×2; europepmc_record:200 ×2; fda_label_search:404 ×2; nice_search:200 ×2; registry_results:NO_POSTED_RESULTS ×2; secondary_fulltext:200 ×159; secondary_search:200 ×5; unpaywall:200 ×2; unpaywall_location:BLOCKED_HTTP_403 ×4
- CORP: ema_search:BLOCKED_HTTP_401 ×2; europepmc_fulltext:NOT_OPEN_ACCESS ×2; europepmc_record:200 ×2; fda_label_search:404 ×2; nice_search:200 ×2; registry_results:NO_POSTED_RESULTS ×2; secondary_search:200 ×5; unpaywall:200 ×2; unpaywall_location:BLOCKED_HTTP_403 ×4
- CORP-2: ema_search:BLOCKED_HTTP_401 ×2; europepmc_fulltext:NOT_OPEN_ACCESS ×2; europepmc_record:200 ×2; fda_label_search:404 ×2; nice_search:200 ×2; registry_results:NO_POSTED_RESULTS ×2; secondary_search:200 ×5; unpaywall:200 ×2
- COPS: europepmc_fulltext:NOT_OPEN_ACCESS ×1; europepmc_record:200 ×1; unpaywall:200 ×1; unpaywall_location:BLOCKED_HTTP_403 ×2
- COPS#24m: europepmc_fulltext:NOT_OPEN_ACCESS ×1; europepmc_record:200 ×1; figshare_api:200 ×1; unpaywall:200 ×1; unpaywall_location:202 ×1; unpaywall_location:BLOCKED_HTTP_403 ×2
- Akrami: europepmc_figure:BLOCKED_HTTP_403 ×1; europepmc_fulltext:200 ×1; europepmc_record:200 ×1; publisher_figure:200 ×1; unpaywall:200 ×1; unpaywall_location:200 ×5; unpaywall_location:202 ×2; unpaywall_location:BLOCKED_HTTP_403 ×1
- REMAP-CAP-corticosteroid-domain: discover:200 ×5; europepmc_fulltext:200 ×1; europepmc_record:200 ×1; registry_results:NO_POSTED_RESULTS ×3; supplements:200 ×1; unpaywall:200 ×1; unpaywall_location:200 ×6
- SONIA: europepmc_fulltext:200 ×1; europepmc_record:200 ×1
- COVIDICUS: discover:200 ×3; europepmc_fulltext:NOT_OPEN_ACCESS ×1; europepmc_record:200 ×1; pmc_bin_supplement:200 ×5; registry_results:NO_POSTED_RESULTS ×3; unpaywall:200 ×1; unpaywall_location:200 ×1; unpaywall_location:500 ×1; unpaywall_location:BLOCKED_HTTP_403 ×2
- METCOVID: europepmc_fulltext:500 ×2; europepmc_record:200 ×3; pmc_pdf:BLOCKED_CHALLENGE_PAGE ×1; repository_pdf:ERROR URLError ×2; supplements:200 ×2; unpaywall:200 ×2; unpaywall_location:200 ×6; unpaywall_location:BLOCKED_HTTP_403 ×4
- CoDEX: europepmc_fulltext:NOT_OPEN_ACCESS ×2; europepmc_record:200 ×2; pmc_bin_supplement:200 ×4; unpaywall:200 ×1; unpaywall_location:200 ×1; unpaywall_location:BLOCKED_HTTP_403 ×2
- CAPE-COVID: europepmc_fulltext:NOT_OPEN_ACCESS ×2; europepmc_record:200 ×2; unpaywall:200 ×1; unpaywall_location:BLOCKED_CHALLENGE_PAGE ×1; unpaywall_location:BLOCKED_HTTP_403 ×2
- COVIDICUS#bayes-reanalysis: europepmc_fulltext:200 ×1; europepmc_record:200 ×1; unpaywall:200 ×1; unpaywall_location:200 ×3
- REMAP-CAP-COVID-corticosteroid-domain: europepmc_fulltext:NOT_OPEN_ACCESS ×1; europepmc_record:200 ×1; registry_results:NO_POSTED_RESULTS ×1; repository_pdf:BLOCKED_HTTP_403 ×2; unpaywall:200 ×1; unpaywall_location:200 ×3; unpaywall_location:BLOCKED_HTTP_403 ×2
