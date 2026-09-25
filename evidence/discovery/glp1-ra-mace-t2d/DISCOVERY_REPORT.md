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
