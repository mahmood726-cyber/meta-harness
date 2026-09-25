# Discovery search -- GLP-1 receptor agonists and 3-point MACE in type 2 diabetes (V1.1)

**Registration.** This file and `search.py` / `screen.py` beside it are committed and pushed BEFORE any query is run;
the commit SHA is the registration. Nothing below may change after a result is seen without a new dated section
saying what changed and why. Author: evid2 (Claude), 2026-09-25. Branch `evid2/v11-discovery-glp1`, NOT for V1.

## Why
The served review's PubMed "queries" are lists of known PMIDs (`topics/glp1-ra-mace-t2d.json` `pubmed_queries`:
`...[uid] OR ...[uid]`). That retrieves the trials already known; it cannot discover one. This search starts from the
review QUESTION only.

## What the designer knew (disclosed)
The strategy was written from the topic's question and eligibility criteria (`question`, `include`, `primary_outcome`
keywords) without opening the review's included-trial list, its positive/negative control PMIDs, seed references or
companion/eviction lists. The designer (a language model) nevertheless has general background knowledge that
cardiovascular outcome trials of GLP-1 receptor agonists exist; to keep that knowledge out of the search, **no trial
name, acronym, PMID, NCT number, sponsor or author appears in any query** -- only concepts, the pharmacological class,
and its member substances (a substance list is a concept, not a trial list).

## Question (from the topic config)
Adults with type 2 diabetes (P); a GLP-1 receptor agonist (I); placebo (C); 3-point MACE (O); double-blind
placebo-controlled randomised trials (design).

## Concept blocks
- **I (class + members).** Class terms, MeSH, and every GLP-1 receptor agonist substance approved or in phase 3 as of
  2026, including multi-receptor agonists with GLP-1 activity (they are candidates; eligibility decides whether a dual
  agonist counts): exenatide, liraglutide, lixisenatide, dulaglutide, albiglutide, semaglutide, efpeglenatide,
  taspoglutide, beinaglutide, loxenatide (PEG-loxenatide), tirzepatide, orforglipron, danuglipron, retatrutide,
  survodutide, cotadutide, mazdutide, efinopegdutide, ecnoglutide, supaglutide.
- **O (cardiovascular outcomes).** MACE, cardiovascular events/outcomes/death, myocardial infarction, stroke, and the
  "cardiovascular outcome trial / cardiovascular safety" phrasing.
- **P (type 2 diabetes).** MeSH and free text.
- **Design (RCT).** The Cochrane Highly Sensitive Search Strategy for randomised trials (sensitivity-maximising, 2008
  revision, PubMed format) -- a published filter, not a tuned one.

## Sources and exact queries (run by `search.py`; every request logged with URL, time, status, bytes, sha256)
1. **PubMed** (E-utilities `esearch` with history, all hits paged; `efetch` XML in batches for every PMID):
   `(I) AND (O) AND (P) AND (RCT filter)`, no date limit, no language limit. The exact string is `PUBMED_QUERY` in
   `search.py`.
2. **ClinicalTrials.gov** (API v2, all pages): interventional studies with condition "type 2 diabetes", an
   intervention matching the I block, and an outcome mentioning cardiovascular / MACE / myocardial infarction /
   stroke (`CTGOV_PARAMS` in `search.py`). Every study record is retained whole.
3. **Europe PMC** (REST, cursor-paged): the same I AND O AND P concepts plus `randomi*` for non-MEDLINE sources
   (preprints, other indexes); records already in PubMed are merged by PMID at deduplication.
Not searched, and said so: WHO ICTRP (no stable open API reachable here), Embase and CENTRAL (not licensed here).

## Retention and deduplication
Every retrieved record is retained (committed as compact gzipped JSON; raw responses held local-only with sha256).
Deduplication: publications by PMID (Europe PMC `MED` records map to their PMID); a registry record and a publication
are linked into one TRIAL when the publication prints the NCT number (abstract, secondary-id/databank field) or the
registry record lists the PMID among its references. The unit of the discovery report is the trial.

## Screening (recorded; the deterministic screen decides, AI only proposes)
1. **Deterministic:** the pipeline's own `harness/screen.py` `run()` on every publication and registry record, with
   a DISCOVERY config = the topic config with every curated, trial-specific list removed (`positive_control_pmids`,
   `negative_control_pmids`, `pubmed_queries`, `seed_comparator_refs`, `comparator_pmid`, `companion_reports`,
   `contrast_evictions`, `include.screen_overrides`) -- only the generic P/I/C/design criteria remain. Its decision and
   rule id are recorded per record. (By the screen's own contract, whether a trial REPORTS MACE is not decided here.)
2. **AI proposals (recorded, never decisive):** every record the deterministic screen includes, and a random sample
   (seed 20260925) of 200 it excludes, is read by an AI screener that proposes include/exclude for P, I, C, design and
   "reports 3-point MACE", with a quote for each; stored verbatim with the reader's identity. Disagreements with the
   deterministic screen are listed, not resolved by the AI.

## Performance report (computed only AFTER screening is committed)
The reference set is **the 10 known eligible trials** of the served review, read from the repository only after the
screening commit exists. For each: found by the search (which source), survived deduplication, deterministic screen
decision and rule, AI proposal. Also: every other trial the deterministic screen includes (with reasons), and the
counts screened out by rule id. Recall is reported as `n of 10`; no precision claim beyond the counts.

## Amendment 1 -- 2026-09-25, after the search ran (disclosed as such)
`search.py` parsed only `PubmedArticle` elements, so 14 of the 4,368 PubMed hits -- all `PubmedBookArticle` records
(drug-class reviews, textbook chapters, HTA reports) -- were retrieved but not parsed. No query changes: `retain_books.py`
re-fetches exactly those 14 PMIDs and parses them as book records (title, abstract, publication type "Book"), and they
join `records_pubmed` so that every hit is retained. They are not trial reports; the deterministic screen decides them.

## Amendment 2 -- 2026-09-25, after the search ran (a code fix, disclosed)
`screen.py` crashed on an NCT that a publication names but that the registry search did not retrieve (a trial member
with no record). It now keeps that NCT in the trial, marked "not retrieved by the registry search", with no screen
decision. No criterion, query or sample changes.
