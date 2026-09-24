# Token-level witnesses for the 34 held count entries -- result and eye review (evid2, 2026-09-25)

Source work for the per-arm witness schema `{group_id, arm_name, events, total, event_witness, total_witness}`.
**Written to schema v2 (the main lane's final schema) in ../v2/ -- see the served section at the end; these are the witnesses it is
written from. Every witness is a character span of ONE number token in sha256-pinned bytes, checked mechanically
(`check_witness.py`: T1 offsets, T2 value, T3 whole token, T4 no occurrence witnesses two arm fields, T5 registry
groupId ownership). Registry records: 22 acquired ClinicalTrials.gov v2 records (`../registry/`), 15 with posted results.

## Counts (of 34): WITNESSED 22, DIFFERS 5, INCOMPLETE 7
- Ownership from registry groupIds: used wherever the registry's posted results carry the outcome.
- Prose/table used although posted results exist: 8 entries -- every one read by eye below; in all 8 the extractor
  searched the registry results and the outcome is NOT there as the served aggregate (only individual AE terms,
  serious/other categories with reporting thresholds, or no such measure). Accepted as REGISTRY_SEARCHED_OUTCOME_ABSENT.

## DIFFERS (all five read by eye; none is a transcription error in the witness)
| entry | printed (witnessed) | held | classification |
|---|---|---|---|
| balanced-crystalloids / SMART 29485925 | NCT02444988 418/2735 vs 467/2646 | 818/7942 vs 875/7860 | TWO_REGISTRATIONS: the held numbers are exactly the sum of NCT02444988 and NCT02547779 (418+400, 2735+5207; 467+408, 2646+5214). A single group_id per arm cannot express it -- SCHEMA QUESTION S1 |
| dpp4 / CARMELINA hypoglycaemia | registry otherEvents 1022 vs 1003 | 1036 vs 1024 (abstract: "1 or more episodes of hypoglycemia") | DIFFERENT_QUANTITY: the registry term is non-serious AEs above a 5% threshold, not all hypoglycaemia; the held number stands |
| probiotics 26973849/0 | registry primary outcome 21 vs 19 EPISODES | 21 vs 17 participants | DIFFERENT_QUANTITY (unit "Episodes"); already set aside by evid2 ruling |
| sglt2-ckd / EMPA-KIDNEY DKA | registry "Diabetic ketoacidosis" 5/3304 vs 1/3305 | 6/3304 vs 1/3305 (full text: "Ketoacidosis") | LABEL_VS_NUMBER: served label is DKA, served number is all ketoacidosis (registry: DKA 5+1 + ketoacidosis 1+0). SERVED ROW -> signature queue Q1 (`SIGNATURE_QUEUE.md`), not landed |
| tocilizumab / BACC Bay 33085857 | registry serious AEs 19/161 vs 8/82 | 28/161 vs 12/82 (article: "36 serious adverse events ... in a total of 28 patients") | REGISTRY_VS_PUBLICATION: different counts for the same named outcome; held-only entry (not served) -> recorded for the owner, no queue item |

## INCOMPLETE (7)
- dapagliflozin 34711976, metformin 16769748 and 19522426, probiotics 24456384: numbers not printed as counts (as before).
- colchicine-postop-af 32720823: "one patient in each group" -- ONE printed token for both arms; under the new rule it
  can witness only one arm field, so the comparator's events are null. Recorded as the rule intends.
- spironolactone / J-EMPHASIS-HF 28824029: registry measure prints only three time-window classes (6+1+10 = 17 and
  5+1+4 = 10) that sum exactly to the abstract's 17 vs 10; summing is not allowed and the abstract prose may not
  override the registry, so events are null -- SCHEMA QUESTION S2.
- tranexamic-acid / WOMAN 28456509: only the abstract is held; no arm counts for thromboembolic events; its analysis
  population prints 10036 (held n1i 10033).

## Schema questions for the main lane (not decided by evid2)
- S1: a trial published as ONE analysis of TWO registrations (SMART; CANVAS is the same shape) -- one arm observation
  per registration, or an arm with several group_ids?
- S2: where the registry's posted result for the outcome is printed only as disjoint components, may the prose total
  (which equals their sum) be witnessed, with the registry components as corroboration?
- S3: "genuinely equal values need distinct witnesses" -- a distributive statement ("in each group") has one token;
  is such an arm field null (as done here) or a declared shared witness?

## Served rows (schema v2's primary population, added 2026-09-25)
35 served count rows, 13 with registry posted results (30 registry records acquired in all, 19 with results).
Checked the same way: **WITNESSED 30, DIFFERS 2, INCOMPLETE 3** -> v2 observations written for **30 of 35**
(`../v2/OBSERVATIONS_served.json`: 27 owned from prose/tables where the registry does not carry the outcome, 3 from
registry groupIds). Not written: dapagliflozin AEs and two metformin rows (counts not printed), and the two rows
queued for Mahmood: Q1 EMPA-KIDNEY (label/number) and **Q2 COVACTA** (registry 116/295 vs 64/143 serious-AE patients
over 60 days; publication 103 vs 55; same denominators; reason not established) -- `SIGNATURE_QUEUE.md`.
Two checker defects found on the served run and fixed with plants: registry counts carried on an eventGroups object,
and group ids resolved file-wide instead of inside their own outcome measure (ASCEND's OG000 is 'Aspirin' in one
measure and 'Omega-3' in the AF measure) -- now the innermost object defining groups around the witness.
CARMELINA hypoglycaemia (served and held): the first witness took the registry's thresholded non-serious term; re-run
with a logged addendum, now witnessed from the trial report (1036/3494 vs 1024/3485 -- the served numbers).
Held population after the same re-run: WITNESSED 23 -> v2 written for 23 of 34.
