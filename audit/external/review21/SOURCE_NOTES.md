# Source notes
## Original research
- JUPITER older subgroup: Glynn et al., PMID 20404379.
  https://pubmed.ncbi.nlm.nih.gov/20404379/
  https://pmc.ncbi.nlm.nih.gov/articles/PMC2946369/
  Methods: cutpoint >=70 chosen after trial completion but before these analyses.
  Table 2: primary HR 0.61 (0.46–0.82).
  Table 3: muscle weakness/stiffness/pain HR 1.04 (0.92–1.19), 494 vs 467 events.
  Original HTML text mirror also read:
  https://www.natap.org/2010/HIV/042610_02.htm

- STAREE: PMID 42670961, DOI 10.1056/NEJMoa2607314.
  https://pubmed.ncbi.nlm.nih.gov/42670961/
  https://www.nejm.org/doi/full/10.1056/NEJMoa2607314
  The indexed original abstract supports N=9971, HR0.70 (0.61–0.82), median5.9years.
  Direct PubMed opens sometimes returned an empty shell; indexed original record
  and publisher abstract searches returned the full relevant abstract.
  Original trial-investigator congress disclosure:
  https://www.escardio.org/news/press/press-releases/cholesterol-lowering-medication-reduces-major-cardiovascular-events-by-30-per-cent-in-older-people-without-known-cardiovascular-disease/

- PROSPER: Shepherd et al., Lancet2002;360:1623–1630. PMID12457784.
  DOI10.1016/S0140-6736(02)11600-X.
  Original article text, including Table3:
  https://www.researchgate.net/publication/11012058_Pravastatin_in_elderly_individuals_at_risk_of_vascular_disease_PROSPER_a_randomised_controlled_trial
  Table3 row with no previous vascular disease: placebo1654 with200 events,
  pravastatin1585 with181 events; HR0.94 (0.77–1.15).
  The table's p0.19 is an INTERACTION p-value, not the subgroup treatment p-value.
  Primary outcome: coronary death, nonfatalMI, fatal or nonfatalstroke.
  The whole-trial HR0.85 and secondary-prevention HR0.78 are NOT inputs to this audit's
  candidate sensitivity.

## Repository records (all at ref 0730234d0b4f)
Base: https://github.com/mahmood726-cyber/meta-harness/blob/0730234d0b4f/
- docs/reviews/statins-primary-prevention-elderly/CERTIFICATE.json
- docs/reviews/statins-primary-prevention-elderly/index.html
- topics/statins-primary-prevention-elderly.json
- cache/statins-primary-prevention-elderly/records.json
- cache/statins-primary-prevention-elderly/verified_effects.json
- outputs/k_gap/g1/statins-primary-prevention-elderly.json
The complete review.json and every HTML tab were not successfully acquired.

## Screening sample coverage
PMID20404379 and PMID42670961: original-publication checks support inclusion.
NCT01304641: held cache says OBSERVATIONAL; consistent with X1.
NCT04111419: held cache explicitly includes atrial fibrillation; consistent with X2.
NCT05361421: held title is an LDL-target trial in patients with cardiovascular disease.
Its sparse cached title/intervention labels do not identify the precise statin contrast.
The final exclusion is supported by the non-primary-prevention scope; its stated
title-based X3 reason was not independently established as a factual description
of the complete intervention protocol.
