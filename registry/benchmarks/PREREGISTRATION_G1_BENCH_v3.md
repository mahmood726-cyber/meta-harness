# PRE-REGISTRATION v3: G1/G2 benchmark set — open-access metas whose included trials all have CT.gov posted results

- Registered by the captain on 2026-10-16. The selection axis is Mahmood's input, relayed by Dispatch on 16 Oct:
  "metas where all the included trials have posted results on CT.gov will qualify".
  Committed and pushed **before any v3 query is run or any candidate is screened**.
- **v1 and v2 stay on the record unchanged.**
  - v1: pre-registration 4adf8793ab88. v1.1: re-screen and validation, b4842f04d8b8 (2 of 800).
  - v2: pre-registration 1ff6f927f4ff, candidate screen 0eec757bb8. 2 of 800 qualify, a lower bound: 314 need
    inspection and 67 were C4 errors, unresolved.
  - The two v1 qualifiers, daratumumab (PMID 37747011) and HCQ prophylaxis (PMID 33406138), keep being built and
    scored as v1 qualifiers. They are not v3 results.
- **Why v3.** The v1/v2 axis ("all trials recent and prospectively registered") leaves G1 to depend on how each trial
  reported. The v3 axis selects metas where every included trial has a public-domain, per-arm, primary source for
  the meta's own outcome: the trial's ClinicalTrials.gov posted results. That is the source the harness binds
  without licence restrictions (D8: registry results are public-domain data).

## Scope sentence (mandatory, verbatim, on every claim)
**"open-access metas whose included trials all have CT.gov posted results"**

## 1. Source: fixed queries, run once, hit list frozen
- **Service:** Europe PMC REST search (`https://www.ebi.ac.uk/europepmc/webservices/rest/search`, `resultType=lite`,
  `format=json`, cursorMark paging, every page saved with its sha256).
- **Common filter F**, applied to every class query:
  `(TITLE:"meta-analysis" OR TITLE:"meta analysis" OR TITLE:"metaanalysis") AND (ABSTRACT:"randomized" OR
  ABSTRACT:"randomised") AND OPEN_ACCESS:y AND (LICENSE:"cc by" OR LICENSE:"cc0") AND
  (FIRST_PDATE:[2015-01-01 TO 2026-09-30]) AND SRC:MED`
- **Class queries.** Each is `F AND (<terms>)`, with the terms searched in title/abstract. They are seeded from drug
  classes introduced after about 2005–2010:

| id | class | terms |
|---|---|---|
| Q01 | SGLT2 inhibitors | empagliflozin OR dapagliflozin OR canagliflozin OR ertugliflozin OR sotagliflozin OR "SGLT2" OR "SGLT-2" |
| Q02 | GLP-1 / GIP-GLP-1 agonists | semaglutide OR dulaglutide OR liraglutide OR tirzepatide OR efpeglenatide OR albiglutide OR exenatide OR lixisenatide |
| Q03 | PCSK9 and inclisiran | evolocumab OR alirocumab OR inclisiran OR "PCSK9" |
| Q04 | Non-steroidal MRA | finerenone |
| Q05 | DOACs | apixaban OR rivaroxaban OR edoxaban OR dabigatran |
| Q06 | CGRP pathway | erenumab OR fremanezumab OR galcanezumab OR eptinezumab OR rimegepant OR atogepant OR ubrogepant |
| Q07 | JAK inhibitors | tofacitinib OR baricitinib OR upadacitinib OR filgotinib OR abrocitinib OR ruxolitinib |
| Q08 | IL-17 / IL-23 / IL-12/23 | secukinumab OR ixekizumab OR brodalumab OR bimekizumab OR guselkumab OR risankizumab OR tildrakizumab OR ustekinumab OR mirikizumab |
| Q09 | IL-4/13 and IL-5 pathway | dupilumab OR tralokinumab OR lebrikizumab OR mepolizumab OR benralizumab OR reslizumab OR tezepelumab |
| Q10 | Newer oncology agents | pembrolizumab OR nivolumab OR atezolizumab OR durvalumab OR cemiplimab OR osimertinib OR palbociclib OR ribociclib OR abemaciclib OR olaparib OR niraparib OR enzalutamide OR apalutamide OR darolutamide |

- **Hit list.** The union of the ten queries, deduplicated by PMID. Each hit records every class id that returned it.
  The ordered list is committed as `hits_v3_ids.json` with the query strings, the run time, and the sha256 of every
  response page. It is not re-run.
- **Order.** By `sha256("20261016:" + PMID)`, ascending. The seed 20261016 is fixed in this file.
- **Budget.** Screen in that order. Stop at **25 QUALIFIES**, or **1,000 screened**, or the end of the list, whichever
  comes first. Every verdict is recorded with its evidence.

## 2. Criteria (all must pass; the first failure is recorded)
- **C1. Licence.** The article's own full-text XML from Europe PMC carries a CC BY or CC0 licence statement. NC/ND/SA
  variants fail. The verbatim statement and the XML sha256 are recorded. This is D8: only CC BY / CC0 text enters a
  model prompt. Metas that are open access but not CC BY/CC0 are counted and reported, never read.
- **C2. Design and size.** The meta is a pairwise meta-analysis of randomised controlled trials, with 3 ≤ k ≤ 25
  randomised trials in the meta's primary pooled analysis.
  - Excluded: NMA-only, IPD-only, DTA, umbrella and observational-only reviews. A pairwise synthesis alongside an
    NMA counts as pairwise.
  - Recorded two-reader model reads, as in v2 §3: reader A is Codex, reader B is a Claude Sonnet reader, and
    disagreements are adjudicated by a recorded Claude Opus call. Every answer quotes a verbatim span found in the
    cached XML.
- **C3. The meta's outcome.** The meta's PRIMARY outcome, as the meta names it.
  - If none is named, the first pooled efficacy outcome reported in the abstract's results.
  - It is fixed by the same two-reader procedure, with a verbatim span, before any registry lookup.
  - The list of trials pooled for that outcome is extracted the same way, from the forest plot, table or text, with
    spans.
- **C4. Every included trial resolves to an NCT id from the trial's OWN records.** The routes, in order:
  1. an NCT id printed in the meta for that trial;
  2. the trial report's own PubMed record (`DataBankList`);
  3. the trial report's own open full text: a registration statement;
  4. a ClinicalTrials.gov API v2 search by acronym or title, accepted only when exactly one record matches the
     trial's intervention, comparator, sponsor and start year.

  Zero or several matches fail. A trial registered only outside ClinicalTrials.gov (ISRCTN, EudraCT, ChiCTR, …)
  fails, because it cannot have CT.gov posted results. Each resolution records its route, URL, response sha256 and
  the verbatim facts.
- **C5. Every included trial has CT.gov posted results for the meta's outcome, checked against AACT.**
  - **Snapshot:** the AACT flat files dated 2026-08-30 (local, fixed). A result first posted after that date counts as
    not posted, and this is stated.
  - **For each NCT:**
    1. `studies.results_first_posted_date` is not null;
    2. some row in `outcomes` measures the meta's C3 outcome;
    3. per-arm data for that outcome exists in `outcome_measurements` or `outcome_counts`, for at least the two
       compared groups.
  - **Outcome match.** Judged by the two-reader procedure over the AACT outcome title, description and time frame
    against the C3 span. The answers are SAME_OUTCOME, SAME_OUTCOME_DIFFERENT_TIMEPOINT, or DIFFERENT.
    SAME_OUTCOME_DIFFERENT_TIMEPOINT passes C5 and is recorded as a forecast G1 risk (TIMEPOINT).
  - The AACT rows used are recorded by table, id and file sha256.
- **C6. No overlap.** Excluded when the candidate's intervention class AND primary outcome both match one of the 32
  existing topics or one of the two v1 benchmark topics. The match is recorded with the topic slug.
- **C7. Spread for building.** All qualifiers are recorded and counted. At most 3 per class id (Q01–Q10) go forward to
  build, taken in screening order. A hit returned by several classes counts under its lowest class id.

## 3. Validation before the v3 result is used
- **Sample.** Before any v3 build, a sample of 40 v3 verdicts is drawn with seed 20261018: 20 EXCLUDED, 20 random,
  and every QUALIFIES. It is re-checked independently by a reader that did not produce the verdict.
- **Error rates.** Reported per criterion next to the v3 count. The v1, v1.1 and v2 samples are burned and are not
  drawn.

## 4. After the v3 candidate list is pushed
- **FORECAST per qualifier, written before its build.**
  - n of N trials with CT.gov per-arm results for the outcome. By construction this is N of N, so the forecast
    states the RISKS instead: timepoint, analysis set, outcome definition, the meta using a publication rather than
    the registry result, and arm combination.
  - A predicted G1 state for each trial.
- **Builds** go only through the standard workflow: protocol sha first, then a bootstrap draft, then the gate.
- **Scoring.** G1 (matched or explained, plus result agreement) and G2 strict. **DONE = G1 pass AND G2 strict pass.**
  Reported as "DONE n of M started", with every topic listed and the scope sentence on every claim.

## 5. What would change this pre-registration
Nothing after the first query is run. Any change is a new version (v3.1 or later) with its own commit, and v3 stays
on the record.
