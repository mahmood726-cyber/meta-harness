# FORECAST: reachable source, not a verified extraction

Checked 2026-10-15T14:06:55Z. Registry SHA-256: `0821278b377f1a3e4ab949923bd1bdc0f502cc76d136a21f6b7362be0a78487f`.

## PMID 37747011: daratumumab RRMM

**FORECAST = 4 of 5 trials** with at least one qualifying OPEN per-arm source.

| Trial | CT.gov | EU CTR | EMA EPAR* | FDA review* | OA report | Counted |
|---|---|---|---|---|---|---|
| POLLUX NCT02076009 | OPEN | OPEN | OPEN | OPEN | OPEN | Yes |
| CASTOR NCT02136134 | OPEN | OPEN | OPEN | OPEN | OPEN | Yes |
| CANDOR NCT03158688 | OPEN | OPEN | NOT_FOUND | NOT_FOUND | OPEN | Yes |
| APOLLO NCT03180736 | OPEN | NOT_FOUND | OPEN | NOT_FOUND | NOT_OPEN | Yes |
| LEPUS NCT03234972 | NOT_FOUND | NOT_FOUND | NOT_FOUND | NOT_FOUND | NOT_OPEN | No |

*OPEN EPAR/review means a public document mentions the trial; it counts only if `qualifies_per_arm=true`. EPAR mentions are not CSRs. FDA table detection alone is not trial-specific verification.

### POLLUX - NCT02076009

- **ClinicalTrials.gov: OPEN** - [source](https://clinicaltrials.gov/api/v2/studies/NCT02076009?fields=hasResults,protocolSection.identificationModule). hasResults=true. Posted results flag used as forecast evidence; no extraction. Counted: yes.
- **EU CTR: OPEN** - [source](https://www.clinicaltrialsregister.eu/ctr-search/trial/2013-005525-23/results). EudraCT 2013-005525-23. Results link and trial-matched results page checked. Counted: yes.
- **EMA EPAR: OPEN** - [source](https://www.ema.europa.eu/en/documents/product-information/darzalex-epar-product-information_en.pdf). Trial identity matched by sponsor code. EPAR is not a CSR and is not counted. Counted: no.
- **EMA clinical data: NOT_FOUND** - [source](https://clinicaldata.ema.europa.eu/web/cdp/home). Public portal API searched by NCT and registry sponsor code. No matching trial-code CSR filename found; incidental document mentions are not a trial CSR. Counted: no.
- **FDA review: OPEN** - [source](https://www.accessdata.fda.gov/drugsatfda_docs/nda/2015/761036Orig1s000MedR.pdf). Public review mentions verified. Structural table flags are not trial-specific arm-number verification; not counted. Counted: no.
- **OA trial report: NOT_OPEN** - [source](https://doi.org/10.1056/nejmoa1607751). PMID 27705267 (original primary report); isOpenAccess=N; licence=not supplied. Primary report identified; Europe PMC reports isOpenAccess=N and no open licence. Counted: no.
- **OA trial report: OPEN** - [source](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7326710/fullTextXML). PMID 32001798 (included extended follow-up report); isOpenAccess=Y; licence=cc by. Whole-trial results report with live full-text reachability and licence metadata; no article text retained. Counted: yes.
- **Health Canada: NOT_FOUND** - [source](https://clinical-information.canada.ca/search/ci-rc). Product listed in indexed portal metadata; trial-specific CSR unresolved because live portal TLS verification failed. Not labelled not listed. Counted: no.

### CASTOR - NCT02136134

- **ClinicalTrials.gov: OPEN** - [source](https://clinicaltrials.gov/api/v2/studies/NCT02136134?fields=hasResults,protocolSection.identificationModule). hasResults=true. Posted results flag used as forecast evidence; no extraction. Counted: yes.
- **EU CTR: OPEN** - [source](https://www.clinicaltrialsregister.eu/ctr-search/trial/2014-000255-85/results). EudraCT 2014-000255-85. Results link and trial-matched results page checked. Counted: yes.
- **EMA EPAR: OPEN** - [source](https://www.ema.europa.eu/en/documents/product-information/darzalex-epar-product-information_en.pdf). Trial identity matched by sponsor code. EPAR is not a CSR and is not counted. Counted: no.
- **EMA clinical data: NOT_FOUND** - [source](https://clinicaldata.ema.europa.eu/web/cdp/home). Public portal API searched by NCT and registry sponsor code. No matching trial-code CSR filename found; incidental document mentions are not a trial CSR. Counted: no.
- **FDA review: OPEN** - [source](https://www.accessdata.fda.gov/drugsatfda_docs/nda/2015/761036Orig1s000MedR.pdf). Public review mentions verified. Structural table flags are not trial-specific arm-number verification; not counted. Counted: no.
- **OA trial report: NOT_OPEN** - [source](https://doi.org/10.1056/nejmoa1606038). PMID 27557302 (original primary report); isOpenAccess=N; licence=not supplied. Primary report identified; Europe PMC reports isOpenAccess=N and no open licence. Counted: no.
- **OA trial report: NOT_OPEN** - [source](https://doi.org/10.1016/j.clml.2019.09.623). PMID 32482541 (included three-year follow-up report); isOpenAccess=N; licence=cc by-nc-nd. Open licence metadata found, but qualifying full-text reachability not established in these checks. Counted: no.
- **OA trial report: OPEN** - [source](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10022857/fullTextXML). PMID 36413710 (later whole-trial survival report); isOpenAccess=Y; licence=cc by-nc-nd. Whole-trial results report with live full-text reachability and licence metadata; no article text retained. Counted: yes.
- **Health Canada: NOT_FOUND** - [source](https://clinical-information.canada.ca/search/ci-rc). Product listed in indexed portal metadata; trial-specific CSR unresolved because live portal TLS verification failed. Not labelled not listed. Counted: no.

### CANDOR - NCT03158688

- **ClinicalTrials.gov: OPEN** - [source](https://clinicaltrials.gov/api/v2/studies/NCT03158688?fields=hasResults,protocolSection.identificationModule). hasResults=true. Posted results flag used as forecast evidence; no extraction. Counted: yes.
- **EU CTR: OPEN** - [source](https://www.clinicaltrialsregister.eu/ctr-search/trial/2016-003554-33/results). EudraCT 2016-003554-33. Results link and trial-matched results page checked. Counted: yes.
- **EMA EPAR: NOT_FOUND** - [source](https://www.ema.europa.eu/en/medicines/human/EPAR/darzalex). No specific trial identifier match in the checked Darzalex EPAR documents; no CSR inferred. Counted: no.
- **EMA clinical data: NOT_FOUND** - [source](https://clinicaldata.ema.europa.eu/web/cdp/home). Public portal API searched by NCT and registry sponsor code. No matching trial-code CSR filename found; incidental document mentions are not a trial CSR. Counted: no.
- **FDA review: NOT_FOUND** - [source](https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=761036). No trial-specific mention in retrieved clinical reviews. Product indexes and openFDA discovery checked; labels are excluded from this FDA-review criterion. Counted: no.
- **OA trial report: NOT_OPEN** - [source](https://doi.org/10.1016/s0140-6736(20)30734-0). PMID 32682484 (included primary report); isOpenAccess=N; licence=not supplied. Primary report identified; Europe PMC reports isOpenAccess=N and no open licence. Counted: no.
- **OA trial report: OPEN** - [source](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10368773/fullTextXML). PMID 37163358 (later whole-trial final report); isOpenAccess=Y; licence=cc by-nc-nd. Whole-trial results report with live full-text reachability and licence metadata; no article text retained. Counted: yes.
- **Health Canada: NOT_FOUND** - [source](https://clinical-information.canada.ca/search/ci-rc). Product listed in indexed portal metadata; trial-specific CSR unresolved because live portal TLS verification failed. Not labelled not listed. Counted: no.

### APOLLO - NCT03180736

- **ClinicalTrials.gov: OPEN** - [source](https://clinicaltrials.gov/api/v2/studies/NCT03180736?fields=hasResults,protocolSection.identificationModule). hasResults=true. Posted results flag used as forecast evidence; no extraction. Counted: yes.
- **EU CTR: NOT_FOUND** - [source](https://clinicaltrials.gov/api/v2/studies/NCT03180736?fields=hasResults,protocolSection.identificationModule). No EudraCT number listed in CT.gov identification metadata; conditional EU query not applicable. Counted: no.
- **EMA EPAR: OPEN** - [source](https://www.ema.europa.eu/en/documents/product-information/darzalex-epar-product-information_en.pdf). Trial identity matched by sponsor code. EPAR is not a CSR and is not counted. Counted: no.
- **EMA clinical data: NOT_FOUND** - [source](https://clinicaldata.ema.europa.eu/web/cdp/home). Public portal API searched by NCT and registry sponsor code. No matching trial-code CSR filename found; incidental document mentions are not a trial CSR. Counted: no.
- **FDA review: NOT_FOUND** - [source](https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=761036). No trial-specific mention in retrieved clinical reviews. Product indexes and openFDA discovery checked; labels are excluded from this FDA-review criterion. Counted: no.
- **OA trial report: NOT_OPEN** - [source](https://doi.org/10.1016/s1470-2045(21)00128-5). PMID 34087126 (included primary report); isOpenAccess=N; licence=not supplied. Primary report identified; Europe PMC reports isOpenAccess=N and no open licence. Counted: no.
- **Health Canada: NOT_FOUND** - [source](https://clinical-information.canada.ca/search/ci-rc). Product listed in indexed portal metadata; trial-specific CSR unresolved because live portal TLS verification failed. Not labelled not listed. Counted: no.

### LEPUS - NCT03234972

- **ClinicalTrials.gov: NOT_FOUND** - [source](https://clinicaltrials.gov/api/v2/studies/NCT03234972?fields=hasResults,protocolSection.identificationModule). hasResults=false. Registry record reachable, hasResults=false. Counted: no.
- **EU CTR: NOT_FOUND** - [source](https://clinicaltrials.gov/api/v2/studies/NCT03234972?fields=hasResults,protocolSection.identificationModule). No EudraCT number listed in CT.gov identification metadata; conditional EU query not applicable. Counted: no.
- **EMA EPAR: NOT_FOUND** - [source](https://www.ema.europa.eu/en/medicines/human/EPAR/darzalex). No specific trial identifier match in the checked Darzalex EPAR documents; no CSR inferred. Counted: no.
- **EMA clinical data: NOT_FOUND** - [source](https://clinicaldata.ema.europa.eu/web/cdp/home). Public portal API searched by NCT and registry sponsor code. No matching trial-code CSR filename found; incidental document mentions are not a trial CSR. Counted: no.
- **FDA review: NOT_FOUND** - [source](https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=761036). No trial-specific mention in retrieved clinical reviews. Product indexes and openFDA discovery checked; labels are excluded from this FDA-review criterion. Counted: no.
- **OA trial report: NOT_OPEN** - [source](https://doi.org/10.1016/j.clml.2021.04.012). PMID 34108127 (included primary report); isOpenAccess=N; licence=cc by-nc-nd. Open licence metadata found, but qualifying full-text reachability not established in these checks. Counted: no.
- **OA trial report: NOT_OPEN** - [source](https://doi.org/10.1016/j.clml.2022.10.007). PMID 36402700 (later whole-trial updated report); isOpenAccess=N; licence=cc by-nc-nd. Open licence metadata found, but qualifying full-text reachability not established in these checks. Counted: no.
- **Health Canada: NOT_FOUND** - [source](https://clinical-information.canada.ca/search/ci-rc). Product listed in indexed portal metadata; trial-specific CSR unresolved because live portal TLS verification failed. Not labelled not listed. Counted: no.

## Interpretation and limitations

- Reachability is environment- and time-dependent. NOT_FOUND/NOT_OPEN with an access error is unresolved, not proof of absence.
- Follow-up reports can support a trial-level forecast without reproducing the meta-analysis timepoint or outcome.
- No per-arm effects, participant counts, or other statistical results were extracted or validated.
- Health Canada live portal requests failed TLS validation and web retrieval timed out. Indexed official portal metadata lists DARZALEX (submission 187648); no trial-matched CSR was verified.

LEPUS: the exact-NCT Europe PMC search missed the primary report; CT.gov-linked PMID 34108127 resolves it. Europe PMC reports `isOpenAccess=N`, but records CC BY-NC-ND and an external OA URL. Crossref confirms a CC BY-NC-ND version-of-record licence. The publisher metadata API returns HTTP 200 with `openaccess=1` and `openaccessType=Full`; its full-text view returns HTTP 401, while ScienceDirect and journal full-text routes return HTTP 403. LEPUS is therefore NOT_OPEN for demonstrated full-text reachability in this environment, not for absence of an open licence. A DOI redirect or licence alone is not counted.

The EMA clinical-data API was reachable and queried separately for each NCT and sponsor code; returned file metadata did not identify a matching trial-code CSR filename. No article or regulatory prose is reproduced in these reports.

## Static versus dynamic disclosure

| Item | Type | Evidence |
|---|---|---|
| Endpoints, status policy, publication selection | static | Task policy; publication IDs manually selected from saved live metadata and linked CT.gov references. |
| Candidate/trial set, availability, licences, URLs, hashes, forecast numerator | dynamic | Registry file and live HTTP/API evidence; numerator derived from source flags. |

All files written under `.codex_logs`; registry and repository code unchanged. No git status/diff, repository-wide scan, commit, or article-text quotation. Full per-request URLs, timestamps, hashes, paper metadata and access failures are in `forecast.json` and its companion evidence JSON files.
