# PRE-REGISTRATION: G1/G2 benchmark set v1 — open-access metas whose included trials are ALL recent and prospectively registered

- Registered by the captain on 2026-10-15, on Mahmood's decisions of 15 Oct 2026 (G1 strategy (3), tightened in (b),
  "done" bar = G1 and G2 strict). This file is committed and pushed **before any candidate is screened**; the screened
  candidate list is a separate, later commit (`candidates_v1.json`) pushed **before any topic is built or scored**.
- Nothing below may change after this commit. A change is a new version (v2) with its own pushed commit, made before
  any re-screening, and the v1 results stay reported.

## Scope sentence (mandatory on every claim from this set)
**"Open-access meta-analyses whose included trials are all recent (started 2010 or later) and prospectively
registered."** No result from this set is generalised to older, unregistered or paywalled evidence bases.

## 1. Candidate source (one deterministic query)
- Europe PMC REST search, `resultType=core`, `format=json`, cursor paging, run once; the run date and the raw hit list
  (ids in returned order) are committed with the candidate list.
- Query string (verbatim; its sha256 seeds the ordering):

      (TITLE:"meta-analysis" OR TITLE:"meta analysis" OR TITLE:"metaanalysis") AND (ABSTRACT:"randomized" OR ABSTRACT:"randomised") AND OPEN_ACCESS:y AND (LICENSE:"cc by" OR LICENSE:"cc0") AND (FIRST_PDATE:[2020-01-01 TO 2026-09-30]) AND SRC:MED

- Licence accepted: exactly CC BY (any version) or CC0, per Europe PMC's `license` field. CC BY-NC / -ND / -SA are
  excluded (D8: a model may read the meta).

## 2. Ordering and screening budget (so nothing is cherry-picked)
- Hits sorted by Europe PMC `id` ascending (numeric), then shuffled with Python `random.Random(seed).shuffle`, where
  `seed = int(sha256(query_string_utf8).hexdigest()[:8], 16)`.
- Screened strictly in that order. Stop when **20** candidates qualify, or after **800** screened, whichever comes
  first. The count screened, the count qualifying and every verdict are reported.
- Every screened candidate is recorded with: id, pmid, pmcid, title, licence, verdict (QUALIFIES / EXCLUDED), the
  first criterion it failed, and the evidence for that criterion (span, registry id, dates).

## 3. Inclusion criteria (all must hold; checked in this order; the first failure is recorded)
- **C1. Open full text.** Europe PMC holds the article's full-text XML (fullTextXML endpoint), licence as in §1.
- **C2. Design.** The article reports a pairwise meta-analysis of randomised controlled trials: the abstract states
  "randomized/randomised (controlled) trial(s)" as the included design, and the text does not describe itself as a
  network meta-analysis only, an individual-participant-data meta-analysis only, a diagnostic-accuracy review, an
  umbrella review, or a review of observational studies. Retracted (Europe PMC `pubType` contains "Retracted
  Publication" or a retraction notice) → excluded.
- **C3. Size.** The number of included RCTs, k, read from the abstract or results ("k RCTs", "k trials", "k studies"
  with randomised design) is 3 ≤ k ≤ 25. Not stated or ambiguous → excluded (fail closed).
- **C4. Every included trial identified by a registry id.** The full text (body, tables, supplementary table text if in
  the XML) gives a registry identifier (NCT, EudraCT, CTIS, ISRCTN, ACTRN, ChiCTR, CTRI, JPRN/UMIN/jRCT, DRKS, IRCT,
  NTR, PACTR, KCT, other WHO primary registry) for each included trial, and the number of distinct ids attributable
  to included trials equals k. Fewer → excluded ("not every included trial carries a registry id in the meta").
- **C5. ALL trials recent.** For every included trial, its registry record gives a study start date on or after
  **2010-01-01**. Read from the registry, never from the meta.
- **C6. ALL trials prospectively registered.** For every included trial, the registry's first-registration
  (first-submitted / first-posted / date of registration) is on or before its start date, compared at month
  precision (same month counts as prospective). A registry record whose dates cannot be read → excluded.
- **C7. Per-trial rows printed.** The article's own XML contains a table with one row per included trial for a pooled
  outcome, or a forest-plot figure whose caption names the pooled outcome (rows readable as a figure later). Neither
  → excluded.
- **C8. No overlap with the 32 existing topics.** Excluded when the candidate's intervention AND primary outcome both
  match an existing topic (`topics/*.json` intervention terms and outcome terms; the overlap check is code, recorded
  with the matching terms).
- **C9. Spread.** At most 3 qualifying candidates per therapeutic area. Area = the first matching entry in this fixed
  list, from the article's MeSH major headings or, absent MeSH, its title: cardiovascular; endocrine/metabolic;
  infectious disease; oncology; psychiatry; neurology; respiratory; gastroenterology/hepatology; renal/urology;
  obstetrics/gynaecology; musculoskeletal/rheumatology; critical care/anaesthesia/surgery; other. A 4th qualifying
  candidate in an area is recorded as EXCLUDED_AREA_CAP (it would otherwise qualify).

## 4. After the candidate list is pushed (not part of screening)
- **Forecast (before any build):** for each qualifying candidate, per included trial, whether an open per-arm source
  is already reachable by the harness's adapters — CT.gov posted results, EU CTR / EudraCT results, EMA clinical
  data / Health Canada clinical information, FDA reviews, an open-access trial report (Europe PMC OA flag + licence).
  Reported as n of N per candidate, labelled FORECAST (a reachable source, not a verified extraction).
- **Build:** each qualifying candidate becomes a topic through the standard workflow only — protocol (PICO from the
  meta's own stated question) committed with its own sha before any search; recorded search → screen → extract
  (typed extractors or recorded two-reader model calls; 0 HAND_ENTERED, 0 HAND_NAMED) → synthesise → build.
- **Score:** G1 (every comparator trial MATCHED or DIVERGENT_NAMED; 0 UNEXPLAINED and 0 NO_OPEN_SOURCE among the
  meta's pooled trials; RESULT_AGREES on the shared trials) and G2 strict (fresh anonymous clone, network cut,
  release content byte-identical). **DONE = G1 pass AND G2 strict pass.** Reported as "DONE n of M started", every
  topic listed, failures included, each with the scope sentence.
