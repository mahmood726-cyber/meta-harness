# Source notes

Repository sources are all at commit 0730234d0b4f unless otherwise stated.

## Repository inspection

* docs/reviews/colchicine-secondary-cv-prevention/index.html
  https://github.com/mahmood726-cyber/meta-harness/blob/0730234d0b4f/docs/reviews/colchicine-secondary-cv-prevention/index.html
* docs/reviews/colchicine-secondary-cv-prevention/CERTIFICATE.json
* topics/colchicine-secondary-cv-prevention.json
* cache/colchicine-secondary-cv-prevention/rob2.json
  Connector-reported original blob: 6c164e5e47e835d2b7bcdbb078e0fdf13d545852.
* harness/rob2.py
  Connector-reported original blob: 0b66b00267ac6c2b138174cc38644b3bf7a955d9.
* cache/colchicine-secondary-cv-prevention/verified_effects.json
* scripts/build_auditor_md.py: confirmed sampling uses sorted random.sample
  on the ordered screening record list, with seed 20261008:<slug>:screen.
* registry/g1_abandoned.json: status unchanged.

## Original clinical sources read

1. COLCOT, PMID 31733140, DOI 10.1056/NEJMoa1912388.
   https://pubmed.ncbi.nlm.nih.gov/31733140/
   Primary composite includes urgent angina hospitalization leading to
   revascularization. HR 0.77 (0.61–0.96).
2. LoDoCo2, PMID 32865380, DOI 10.1056/NEJMoa2021372.
   https://pubmed.ncbi.nlm.nih.gov/32865380/
   Primary HR 0.69 (0.57–0.83); non-CV-death HR 1.51 (0.99–2.31).
3. CLEAR colchicine comparison, PMID 39555823, DOI 10.1056/NEJMoa2405922.
   https://pubmed.ncbi.nlm.nih.gov/39555823/
   HR 0.99 (0.85–1.16); primary composite contains revascularization, not HF.
4. CLEAR spironolactone comparison, PMID 39555814, DOI 10.1056/NEJMoa2405923.
   https://pubmed.ncbi.nlm.nih.gov/39555814/
   Confirms the HF-containing co-primary endpoint belongs to spironolactone.
5. COPS, PMID 32862667, DOI 10.1161/CIRCULATIONAHA.120.050771.
   https://pubmed.ncbi.nlm.nih.gov/32862667/
   Distinguishes efficacy events, total deaths, non-CV deaths and GI symptoms.
6. Matching DRC-04 original UMIN record, UMIN000029170, receipt R000033349.
   https://center6.umin.ac.jp/cgi-open-bin/ctr_e/ctr_view.cgi?recptno=R000033349
   Three arms, 0.5 mg/0.25 mg/placebo; randomized, individual, double blind;
   coronary disease with type 2 diabetes. Secondary institutional ID 1195.
   This is an external identity cross-check, not a signed repository family join.
7. MACT original article, PMID 37587591, DOI 10.1016/j.jcin.2023.05.035.
   https://www.jacc.org/doi/10.1016/j.jcin.2023.05.035
   Single-arm open-label design supports exclusion of NCT04949516 as non-RCT.
8. PMID 40988201: case reports/literature review, not an original RCT.
   https://pubmed.ncbi.nlm.nih.gov/40988201/
9. PMID 32407460: COLCOT economic analysis, not an independent trial.
   https://pubmed.ncbi.nlm.nih.gov/32407460/

## Screening sample limits

Manual 120-record order yielded indices [3,11,96,99,109], IDs
40988201,32407460,NCT05739929,NCT02162303,NCT04949516.
The first, second and fifth decisions have primary-source support. Complete
registry content for the third and fourth was not independently obtained; no
final external sign-off of those decisions is asserted. Third-party registry
mirrors were encountered during discovery but are not used to certify those
sample decisions.
