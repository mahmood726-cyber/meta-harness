# Source and verification notes

## Pinned repository records inspected

Base: https://github.com/mahmood726-cyber/meta-harness/blob/0730234d0b4f/

- docs/reviews/pcsk9-mace/CERTIFICATE.json (identity read, not regenerated)
- docs/reviews/pcsk9-mace/index.html (long sections recovered with connector search)
- topics/pcsk9-mace.json
- cache/pcsk9-mace/rob2.json, especially ODYSSEY D5 input/comparison fields
- harness/rob2.py (component matcher and fallback excerpt)
- cache/pcsk9-mace/records.json
- registry/g1_abandoned.json

Connector-reported blob for cache/pcsk9-mace/rob2.json:
7d16d983d63dad3673b990be12af97be0144fcef

The attempted scripts/refresh_rob2.py fetch at the pin returned 404. Directory
search/discovery did not establish an executable production callback at this pin.
No actual callback identity is claimed in the tests.

## Original clinical sources

FOURIER, Sabatine et al. 2017:
https://www.nejm.org/doi/abs/10.1056/NEJMoa1615664
PMID 28304224. The key secondary 3-point HR is 0.80 (0.73–0.88); the primary
five-component result differs. Original abstract/HTML result checked.

ODYSSEY OUTCOMES, Schwartz et al. 2018:
https://pubmed.ncbi.nlm.nih.gov/30403574/
https://www.nejm.org/doi/full/10.1056/NEJMoa1801174
Primary four-component result HR 0.85 (0.78–0.93). Original abstract checked.

VESALIUS-CV:
https://pubmed.ncbi.nlm.nih.gov/41211925/
DOI 10.1056/NEJMoa2514428. Epub 2025-11-08; print 2026-01-08.
Original report distinguishes three-point HR 0.75 (0.65–0.86) from four-point
HR 0.81 (0.73–0.89), adding ischemia-driven arterial revascularization.
These represent one trial and are alternatives, not independent studies.

ODYSSEY LONG TERM:
https://pubmed.ncbi.nlm.nih.gov/25773378/
DOI 10.1056/NEJMoa1501031. The MACE analysis is explicitly post hoc. Abstract
reports injection-site-reaction percentages. Exact historic reaction counts were
NOT independently table-verified by this audit and are not reinstated.

Seeded-screening sources:
https://pubmed.ncbi.nlm.nih.gov/28504611/ (indexed Comment)
https://journals.sagepub.com/doi/full/10.1177/0004563217705053
https://pubmed.ncbi.nlm.nih.gov/30403574/ (original ODYSSEY trial)
https://pubmed.ncbi.nlm.nih.gov/33264825/ (FIDELIO, finerenone not PCSK9)
https://pubmed.ncbi.nlm.nih.gov/36531722/ (comparator meta-analysis)
https://pubmed.ncbi.nlm.nih.gov/41211925/ (original VESALIUS trial)

Some direct PubMed opens returned CAPTCHA shells. Search-indexed primary-source
records and original publisher abstract/HTML content supplied the successful
checks; no successful download of every direct page is claimed.

No full journal articles, PDFs, font files, or credentials are bundled.
