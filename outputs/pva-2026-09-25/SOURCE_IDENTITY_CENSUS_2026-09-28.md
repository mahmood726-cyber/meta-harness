# Source-identity chain census -- do all of a citation's identifiers name the same publication? (pva, 28 Sep 2026)

**To: the evidence lane (evid) and the release captain, for the harness check. Report only; nothing in the repository was changed.**

## Question
The SGLT2-CKD external review (page hash 901f0ed6) found EMPA-KIDNEY's ketoacidosis extraction citing "PMID 36331190, PMC9761906";
PMC9761906 is a starfish-regeneration methods chapter. Across all 32 topics: do the PMID, PMCID, DOI and NCT that the project
cites together name one publication, and does the cited text occur in it?

## Method (V1 = main 9eacfe09)
- **Harvest** (streamed from git objects; no checkout): 8,958 files under docs/reviews, cache (not the search snapshots),
  evidence, registry and docs/m. A citation is one place where identifiers are asserted together: a text string naming a
  PMID with a PMCID and/or DOI, or a JSON object carrying pmid with pmcid/doi. **10,557 citation instances** (255 in text,
  10,302 in structured fields), plus the embedded article-ids of all **61** held full texts, plus **361** trial-family links
  (report PMID -> registry NCT). Positive control: the known EMPA-KIDNEY citation is harvested in all 12 places it occurs.
- **Resolve**: NCBI E-utilities esummary (3,501 PMIDs: title, DOI, PMCID) and the NCBI ID converter (450 PMCIDs). 24 raw
  responses kept gzipped with sha256 and UTC time (`idcensus/raw`, `resolved.json`). Registry checks: ClinicalTrials.gov API v2,
  18 raw responses likewise.
- **Compare**: every PMCID must resolve to a PMID cited with it; every DOI must be PubMed's DOI for the cited PMID; every held
  full text's embedded pmid/pmcid/doi must agree with the PMID it is filed under; every quoted passage must occur in the held
  text of the cited PMID; every family report's own PubMed record (or, failing that, the registry's reference list) must name
  the family's NCT.
- **Verify**: every candidate was read in context by this lane. Codex was not needed: the comparison is exact identifier
  matching, done deterministically, and a harvest artefact is recognisable only by reading its context.

## Result

### PMID / PMCID / DOI: **29 of 10,557 citation instances** carry a wrong identifier = **10 distinct defects (1 PMCID + 9 DOI)**

(69 instances were flagged; 29 are verified real -- 12 for the PMCID, 17 for eight of the DOIs -- and 40 are artefacts. The ninth
DOI record, 30912409, was not flagged by the comparison at all, because PubMed records no DOI for it and "not PubMed's DOI"
cannot fire; it was found by the root-cause census below, which is how that gap in the comparison was noticed.)

| | candidates (instances / distinct) | verified real (distinct) | artefacts, and why |
|---|---|---|---|
| PMCID names another PMID | 41 / 16 | **1** (12 instances) | 15: co-occurrence inside codex transcripts (registry/model_calls/lane_log/rai.jsonl, 9), process notes (LABEL_CORRECTIONS.md, SIGNATURE_QUEUE.md), and one served table row my HTML splitter merged (probiotics PMC11551610 = PMID 39529939, correctly cited) |
| DOI is not PubMed's DOI for the PMID | 61 / 28 | **9** (held records) | 19: transcripts; funder-registry ids (10.13039/...) that are not publication DOIs; DOIs my regex cut at a parenthesis; a comparator's DOI near trial PMIDs; a PLOS table DOI owned by PMID 38157348, correctly |
| quote not in the cited source | 2 / 1 | 0 | the same merged probiotics row |
| held full text self-ids disagree | 0 of 61 | 0 | -- |
| cited PMID does not resolve | 0 of 3,501 | 0 | -- |

**1. The EMPA-KIDNEY PMCID (the reviewer's case), 12 instances.**
Cited: `PMID 36331190, PMC9761906`. PMC9761906 = PMID 35359313, "Studying Echinodermata Arm Explant Regeneration Using Echinaster
sepositus" (Methods Mol Biol). **Correct: PMID 36331190 = PMC7614055 = DOI 10.1056/NEJMoa2204233** ("Empagliflozin in Patients with
Chronic Kidney Disease"), which is also what the held full text (cache/sglt2-ckd-progression/ft_36331190.txt) states about itself.
The quoted text ("Ketoacidosis occurred in 6 patients ...") IS in that held full text: the counts are right, the identifier is wrong.
Served in docs/reviews/sglt2-ckd-progression/review.json (3) and index.html (2) and docs/m/me17c0a34/index.html (2); held in
cache/sglt2-ckd-progression/verified_arms.json and evidence/typed_arms (4 rows). It entered with the typed-arm extraction
(evidence/typed_arms/extractions/CD-sglt2-ckd-progression-1-0) and propagated from there. No other PMCID in the corpus is wrong.

**2. Nine held records carry a CITED REFERENCE's DOI instead of their own -- a harness defect, proven by reproduction.**
`harness/fetch.py::_efetch` (lines 111-118 at 9eacfe09) takes the ELocationID DOI, and otherwise loops over **every** `.//ArticleId`
of the article **without a break**, so it keeps the **last** DOI in the record -- in PubMed XML, the last cited reference's.
Applied to today's efetch XML, that exact logic yields a reference's DOI for exactly these 9 records, and for no other of 3,330:

| topic | PMID | held DOI (a reference's) | correct (PubMed's own) |
|---|---|---|---|
| azithromycin-copd-exacerbation | 24159237 | 10.1056/nejmoa1300799 | 10.4212/cjhp.v66i5.1292 |
| doac-vte-recurrence | 12777182 | 10.1002/1529-0131(199906)12:3<172::aid-art4>... | 10.1186/1471-2474-4-10 |
| omega3-cardiovascular-events | 27749986 | 10.1002/14651858.cd012151 (earlier version) | 10.1002/14651858.CD012151.pub2 |
| probiotics-aad-prevention | 30912409 | 10.1099/jmm.0.47615-0 | none (PubMed records no DOI) |
| probiotics-aad-prevention | 27790616 | 10.1007/bf01308616 | 10.3389/fmed.2016.00044 |
| probiotics-aad-prevention | 22559011 | 10.3945/jn.109.113779 | 10.1186/1471-2334-12-108 |
| vitamin-d-acute-respiratory-infection | 27737646 | 10.2307/2533164 | 10.1186/s12884-016-1103-9 |
| vitamin-d-acute-respiratory-infection | 27826955 | 10.1002/14651858.cd008824 (earlier version) | 10.1002/14651858.CD008824.pub2 |
| zinc-common-cold-duration | 15499830 | 10.1016/s0008-6215(00)80664-3 | 10.1023/b:bire.0000037754.71063.41 |

Served: doac-vte-recurrence/review.json (12777182) and probiotics-aad-prevention/review.json (30912409, 27790616, 22559011).
The others are held but not rendered. (Two of the nine name the same Cochrane review, earlier version.)

### NCT: **4 of 361** trial-family links name a registration the report does not belong to
340 are confirmed by the report's own PubMed record, 10 more by ClinicalTrials.gov's reference list, 1 is consistent by title
(PHILO, 26376600 / NCT01294462), and 5 cannot be checked (4 registry-only families; 1 report not held). Control: the known
tranexamic-acid mislink is reached and classified.

| topic | family | report | registry id served | why it is not that registration | correct registry id |
|---|---|---|---|---|---|
| colchicine-postop-af | 7 | 29186389 (COP-AF pilot pleural substudy) | NCT03310125 | NCT03310125 is the definitive COP-AF trial, first submitted 2017-10-10, start 2018-02-14, n 3,209; the report is the 2014-2015 pilot (n 100) | not established from these sources |
| colchicine-postop-af | 7 | 29237033 (COP-AF pilot) | NCT03310125 | same | not established |
| doac-vte-recurrence | 51 | 30859608 (Myelaxat: apixaban PROPHYLAXIS in myeloma, phase 2) | NCT04462003 | NCT04462003 = apixaban for acute DVT in active malignancy | not established |
| tranexamic-acid-pph | 12 | 42540384 (300-participant single-centre Indian trial, 2024-25) | NCT03364491 | NCT03364491 = the US 31-hospital caesarean trial (PMID 37043652) | none in its PubMed record |

## Correction to this lane's own audit (27 Sep)
In the internal topic audit, finding sglt2-ckd-progression #4 (codex: "provenance cites PMC9761906; the held article is
PMC7614055") was downgraded by me to "identifier inconsistency only, not shown to be a different document". **That was wrong**:
PMC9761906 is a different publication. It is re-entered in the addendum as C5, accepted as written.

## Proposed harness checks (for evid and the captain; each needs a plant that fires before the fix)
1. **PMCID binding.** Any served or held citation naming `PMID p, PMCx` must satisfy PMCx == the pmcid recorded for p (the held
   full text's `<article-id pub-id-type="pmcid">`, or the ID-converter ledger). Plant: EMPA-KIDNEY's row as it is today -> refuse.
2. **DOI from the article only.** `_efetch` must take `./PubmedData/ArticleIdList/ArticleId[@IdType="doi"]` (or ELocationID), never
   a `.//ArticleId` that sits under `ReferenceList`, and never "last wins". Plant: an efetch record with no ELocationID, its own
   DOI, and a reference list whose last entry has a DOI -> must return the article's own DOI (today it returns the reference's).
   The 9 held records must be refreshed through the fixed code (a derived notice for any served change).
3. **Family NCT evidence.** A report may join a family's NCT only on positive evidence: its PubMed record names the NCT, or the
   registry lists the PMID; otherwise the link is UNVERIFIED, never asserted. A report whose study period precedes the
   registration's start (COP-AF pilot) must be refused outright.
4. **Harvest scope for any re-run.** Model-call transcripts and process notes are not citations; restrict to served pages,
   held records and extraction rows, and pair identifiers inside one citation, not one table row.

## Artefacts
`source_identity_census/`: harvest.json.gz, resolved.json, compare.json, doi_lastref.json, nct_families.json, nct_ctgov.json,
raw NCBI and ClinicalTrials.gov responses (gz, with sha256/UTC ledgers), and the scripts idchain_harvest.py, idchain_resolve.py,
idchain_compare.py, doi_lastref_census.py, idchain_nct.py, idchain_nct_ctgov.py.
