# Discovery performance -- GLP-1 RA / 3-point MACE in T2D (V1.1, NOT in V1)

Registration `7f401ded` (strategy + queries, pushed before running) -> search `7c0b6367` -> deterministic screen
`e28c09c9` -> AI proposals `d3c7bb6a` -> reference set read, this report. Numbers: `run/PERFORMANCE.json`.

## Retrieved and retained
PubMed 4,368 (4,354 articles + 14 book records, amendment 1); ClinicalTrials.gov 114; Europe PMC non-MEDLINE 42.
4,524 records, all retained. Deduplicated to 4,362 trials (amendment 3; 4,323 as registered).

## The 10 known eligible trials: 10 of 10 found, 10 of 10 included by the deterministic screen
Reference set = the served review's conventional-GLP-1-RA primary pool: `cache/glp1-ra-mace-t2d/records.json`
(its eligible entries) + FLOW (`evidence/glp1_adjudication/FLOW.json`).

| Trial | PubMed | CT.gov | Dedup | Primary report: screen / AI | Registration: screen / AI |
|---|---|---|---|---|---|
| ELIXA | yes | yes | one trial | include / exclude (design unclear) | include / include |
| LEADER | yes | yes | one trial | include / include | include / include |
| SUSTAIN-6 | yes | yes | one trial | include / exclude (design unclear) | include / include |
| EXSCEL | yes | yes | one trial | include / exclude (design unclear) | include / include |
| Harmony Outcomes | yes | yes | one trial | include / include | include / include |
| REWIND | yes | yes | one trial | include / include | include / include |
| PIONEER 6 | yes | yes | one trial | include / include | include / include |
| AMPLITUDE-O | yes | yes | one trial | include / exclude (design unclear) | include / include |
| FLOW | yes | yes | one trial | include / exclude (design unclear) | include / include |
| SOUL | yes | yes | one trial | include / include | include / include |

- Under the as-registered grouping, all 10 were found and included at the record level, but all 10 sat inside ONE
  25-NCT cluster (T00072). As a trial list, the registered pipeline would have reported one "trial" for them. Only
  after amendment 3 does each resolve to one trial of its own.
- Europe PMC non-MEDLINE contributed none of the 10.
- Where the AI proposed exclude for a primary report, the only reason was that its abstract does not say
  "double-blind". The AI proposed include for each trial's registration (masking field). No reference trial would
  have been lost on the AI's proposals at trial level.
- FREEDOM-CVO (ITCA 650; eligible only for the any-delivery strand) was also found and included. Its publication was
  included; its registration was excluded by X3, because ITCA 650 is not in the topic's intervention list.

## What else was found: 80 other included trials
- **One new candidate:** NCT05441267 **ASCEND PLUS**, oral semaglutide vs placebo, T2D, quadruple-masked, MACE
  primary. It has no results posted (`has_results: false`), so it cannot contribute counts yet. It is not in the
  served review and is the one genuine discovery. It should enter the review's watch list.
- **8 secondary reports of known trials** that did not link to their parent: post hoc or subgroup papers (FLOW by
  CKD severity, EXSCEL by ejection fraction, Harmony MI/AF, EXSCEL sex differences, exenatide integrated safety, a
  LEADER+SUSTAIN pooled analysis, a commentary). None names an NCT in its abstract, so deduplication kept them
  apart. The AI proposed exclude (secondary) for every one of them. This is under-merging, not a new trial.
- **71 others:** small placebo-controlled GLP-1 RA trials with glycaemic, weight or mechanistic outcomes that
  satisfy P/I/C/design. By the screen's own contract, whether a trial reports MACE is not decided at screening. The
  AI proposed include for 35 of them (all with reports_mace = no or unclear) and exclude for 41 (mostly secondary,
  single-blind or active-comparator); 4 had mixed proposals across their records.

## Screened out and why (records; the deterministic screen)
- **X1** not a randomised controlled trial: 3,948
- **X2** population not on topic: 196. Of these, 189 do not mention type 2 diabetes in title or conditions, and 4
  are "without diabetes" trials such as SELECT.
- **X3** intervention or comparator: 250. Of these, 154 have a randomised intervention outside the topic's 7-drug
  list (tirzepatide, other agonists, ITCA 650, non-GLP-1 drugs), and 96 have no placebo comparator.
- **Not screened:** 122 NCTs named by a publication but not retrieved by the registry search (amendment 2). Their
  publications were screened.

## AI proposals vs the deterministic screen (329 records read; 1 text-less NCT not read)
- Agree: 198 exclude/exclude and 56 include/include.
- Disagree, 75 in total:
  - 74 records where the screen said include and the AI said exclude. These are mostly secondary analyses, or
    abstracts that don't state "double-blind"; the screen does not test for blinding (`design_double_blind: false`).
  - 1 record where the screen said exclude and the AI said include: PMID 21251180, a dulaglutide trial named only
    by its code LY2189265 in the title. X3 is a false exclusion here, because the code isn't in the drug list.
- The disagreements are listed in `run/AI_PROPOSALS.json` and are not resolved by the AI. Reader: three Claude Opus
  5.5 subagents, one per shuffled batch; quotes checked verbatim.

## Limits (stated, not tuned)
- The designer is a language model with background knowledge of these trials. The queries contain no trial names,
  PMIDs or NCTs, but concept choice cannot be proven independent of that knowledge.
- WHO ICTRP, Embase and CENTRAL were not searched.
- The recall denominator is 10, set by the served review; it measures agreement with that review, not completeness.
- Amendment 3 was made after the reference set was read. Recall is unchanged by it.

# Part 2 -- registry-first pass (registered 0bc059f8 before it ran)
ClinicalTrials.gov, with no condition or status filter, returned 116 interventional GLP-1 RA studies naming a
cardiovascular outcome. All are retained (`run/records_registry_pass.json.gz`). 14 pass the registered CVOT filter.
Numbers: `run/REGISTRY_PASS_REPORT.json`.

## Would the text search have missed any known-eligible trial? No: 0 of 10
- **Text searches:** PubMed alone found all 10 reference trials. Europe PMC non-MEDLINE found none of them (it is
  there for non-MEDLINE records).
- **Registry-first pass:** it retrieved all 10. 8 of 10 pass its CVOT filter. The other two miss only the
  primary-outcome criterion, and correctly so: ELIXA's primary is a 4-point composite that adds unstable angina, and
  FLOW's primary is a kidney composite.
- So neither route alone lost a reference trial at retrieval, and the registry route adds an independent second
  path to every one of them.

## Finished trials with a cardiovascular primary outcome and NO posted results (the question asked)
Across all 116 retrieved, whatever the other criteria say:
- **NCT01455896 FREEDOM-CVO** (ITCA 650, an implanted exenatide pump, vs placebo; T2D; 4,156 randomised): COMPLETED,
  no posted results. The filter missed it only on I_glp1: the registration names the drug "ITCA 650", never
  "exenatide". Its publication (PMID 34873344) exists, and it is in the served review's any-delivery strand only.
  The registry pass surfaces it by status even though the filter misses it.
- **NCT05803421 ACHIEVE-4** (orforglipron vs insulin glargine): COMPLETED, no posted results. Active comparator,
  outside this review's placebo contrast.
- **NCT06077864** (survodutide cardiovascular safety, obesity): COMPLETED, no posted results. Population not T2D.
- **No completed or terminated placebo-controlled GLP-1 RA CVOT in T2D is missing from the served review.**

## The 14 filter candidates
- **In the reference set (8):** EXSCEL, LEADER, REWIND, SUSTAIN-6, Harmony Outcomes, PIONEER 6, AMPLITUDE-O, SOUL.
  All are finished with results posted.
- **Ongoing, no results (4):**
  - **ASCEND PLUS NCT05441267.** Oral semaglutide vs placebo, T2D only (inclusion), MACE primary, 21,296 planned.
    The clean candidate, already found by Part 1.
  - **REDEFINE 3 NCT05669755.** CagriSema (cagrilintide + semaglutide) vs placebo in cardiovascular disease, with or
    without T2D (T2D has its own inclusion criteria), 3-point MACE primary. NOT found by Part 1: its condition is
    "Cardiovascular Disease" and Part 1 required T2D as the condition. It is a combination product and a mixed
    population, so eligibility would rest on a T2D subgroup; it is a watch-list candidate.
  - **NCT06383390** retatrutide CV and kidney outcomes. ASCVD/CKD with or without T2D, triple agonist. Part 1 found
    it. Watch list, with the same subgroup caveat.
  - **NCT07391267.** Oral semaglutide in T2D with CKD/MAFLD, 90 participants, kidney-led composite primary. Not a
    CVOT. Its primary composite names cardiovascular death, so the filter passed it. Not found by Part 1.
- **Population false positives (2):** SELECT NCT03574597 and SURMOUNT-MMO NCT05556512 mention type 2 diabetes only
  as an EXCLUSION criterion. The registered P test reads the whole eligibility text and cannot tell inclusion from
  exclusion. That is a defect of the filter, disclosed here and not re-tuned; the report records, per candidate,
  which side the mention sits on.

## Near misses worth naming (4 of 5 criteria)
- **NCT07241390:** orforglipron CVOT in ASCVD/CKD. Recruiting, and T2D is not named.
- **NCT04255433 SURPASS-CVOT:** tirzepatide vs dulaglutide, an active comparator.
- **NCT05390892 PRECIDENTD:** GLP-1 RA vs SGLT2 inhibitor, an active comparator.
The full list is in the report JSON.

## What Part 2 changes
Watch list for the served review: ASCEND PLUS, REDEFINE 3 and the retatrutide CVOT, all without results.
- FREEDOM-CVO remains the one finished trial whose results exist only in its paper.
- The main Part 1 recall gap Part 2 exposes is a CONDITION gap: a CVOT registered under "cardiovascular disease"
  rather than T2D (REDEFINE 3) is invisible to a T2D-condition registry search.
- **Limits:** only ClinicalTrials.gov; WHO ICTRP was not reachable, so trials registered only in EU CTR, ChiCTR or
  JPRN are not covered. The P test is known to be inclusion/exclusion-blind.
