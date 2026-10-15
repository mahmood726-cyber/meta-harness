# FORECAST: reachable source, not verified extraction

Open-access meta-analyses whose included trials are all recent (started 2010 or later) and prospectively registered.

Reused .codex_logs/forecast_probe.py HTTP evidence helper and v1 source-flag counting algorithm. Live CT.gov checked for all nine trials. Prior same-day regulatory/OA evidence reused for original qualifier; new qualifier source checks stop once an affirmative source is established.

For new qualifier, CT.gov checked for all four trials; EU CTR and registry-linked primary OA report checked for the trial without posted CT.gov results. Other source families are not assessed after an affirmative source; no NOT_FOUND claim is made for unchecked sources.

## PMID 37747011: Efficacy and safety of daratumumab in the treatment of relapsed/refractory multiple myeloma: A meta-analysis of randomized controlled trials.

FORECAST: **4 of 5 trials** with at least one OPEN per-arm source.

| Trial registry ID | Counted | Affirmative sources |
|---|---|---|
| NCT02076009 | Yes | [ClinicalTrials.gov](https://clinicaltrials.gov/api/v2/studies/NCT02076009); [EU CTR](https://www.clinicaltrialsregister.eu/ctr-search/trial/2013-005525-23/results); [OA trial report](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7326710/fullTextXML) |
| NCT02136134 | Yes | [ClinicalTrials.gov](https://clinicaltrials.gov/api/v2/studies/NCT02136134); [EU CTR](https://www.clinicaltrialsregister.eu/ctr-search/trial/2014-000255-85/results); [OA trial report](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10022857/fullTextXML) |
| NCT03158688 | Yes | [ClinicalTrials.gov](https://clinicaltrials.gov/api/v2/studies/NCT03158688); [EU CTR](https://www.clinicaltrialsregister.eu/ctr-search/trial/2016-003554-33/results); [OA trial report](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10368773/fullTextXML) |
| NCT03180736 | Yes | [ClinicalTrials.gov](https://clinicaltrials.gov/api/v2/studies/NCT03180736) |
| NCT03234972 | No | None established |

## PMID 33406138: The efficacy and safety of hydroxychloroquine for COVID-19 prophylaxis: A systematic review and meta-analysis of randomized trials.

FORECAST: **4 of 4 trials** with at least one OPEN per-arm source.

| Trial registry ID | Counted | Affirmative sources |
|---|---|---|
| NCT04304053 | Yes | [OA trial report](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7722693/fullTextXML) |
| NCT04308668 | Yes | [ClinicalTrials.gov](https://clinicaltrials.gov/api/v2/studies/NCT04308668) |
| NCT04328467 | Yes | [ClinicalTrials.gov](https://clinicaltrials.gov/api/v2/studies/NCT04328467) |
| NCT04329923 | Yes | [ClinicalTrials.gov](https://clinicaltrials.gov/api/v2/studies/NCT04329923) |

The hydroxychloroquine primary report (PMID 33289973) has an empty Europe PMC licence field but explicit open-reuse permission in its reachable XML. This is counted on that permission plus trial identity and full-text reachability, not the OA flag alone. Source acknowledgement: Mitja et al., NEJM.

## Limitations

- FORECAST concerns source reachability, not verified extraction, outcome agreement, or efficacy.
- The original qualifier retains dated same-day EU/EMA/FDA/OA/Health Canada evidence from forecast_v1.json; CT.gov was refreshed.
- For the added qualifier, confirmed positive sources make further source-family checks unnecessary for n of N. Unchecked sources are not asserted absent.
- LEPUS remains unresolved after prior source checks; no source is counted solely from an OA flag, licence, drug listing, or DOI redirect.

## Static versus dynamic disclosure

| Item | Type | Evidence |
|---|---|---|
| Source eligibility and any-OPEN counting rule | static | Frozen forecast definition; v1 implementation reused. |
| Candidate/trial sets, CT.gov results flags, source licences, hashes, numerator | dynamic | v1.1 candidate file; timestamped source evidence. |
| Registry-linked primary publication selection | manual source-backed | CT.gov references and Europe PMC matching title/PMID/NCT; no outcome data hand entered. |
