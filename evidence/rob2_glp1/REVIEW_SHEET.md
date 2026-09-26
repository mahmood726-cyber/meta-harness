# RoB 2 (outcome-specific) -- GLP-1 RA 3-point MACE: PROPOSALS awaiting human review

**Status: every judgement below is a PROPOSAL (`PROPOSAL_AWAITING_HUMAN_REVIEW`). None is final; the reviewer line is empty on purpose.**
Result assessed: 3-point MACE hazard ratio, effect of assignment (ITT). Domains with held evidence: **50 of 50** (trials in the GLP-1 MACE pool (8 served + FLOW + ELIXA) x 5 RoB 2 domains).
Proposals: low 47, some_concerns 3. `NO_EVIDENCE_HELD` means no held source speaks to the domain -- it is NOT a risk level and is never relabelled high.
Stopped treatment is recorded separately (D2 context) and never used as missing outcome data (D3). A registry entry alone is never taken as proof of prespecification (D5).

**Blind second read** (same model family -- blind, not independent; spans only): agreement 39 of 50 before reconciliation, 38 of 50 after. Disagreements KEPT for you to decide (6):

- PIONEER 6 D5_selection_of_reported_result: lane **low**, blind **some_concerns** -- blind's reason: The protocol span defines the MACE primary endpoint, and the SAP span says blinding lasts until database release, but neither shows the analysis plan was finalised before unblinding (5.1 NI).
- SOUL D3_missing_outcome_data: lane **low**, blind **some_concerns** -- blind's reason: Registry spans: completers 4755/4740, with 61 withdrawals and 94 lost to follow-up (roughly balanced), but no randomized denominator or vital-status ascertainment is given (3.1 NI).
- REWIND D3_missing_outcome_data: lane **low**, blind **some_concerns** -- blind's reason: Registry spans give completers (4935 placebo, 4932 dulaglutide) with no randomized denominator, and the protocol span states only a requirement, not what was achieved (3.1 NI).
- REWIND D4_outcome_measurement: lane **low**, blind **some_concerns** -- blind's reason: Protocol span: an independent CEC adjudicates all primary events, but no span states the CEC was blinded to assignment (4.3 NI).
- EXSCEL D3_missing_outcome_data: lane **low**, blind **some_concerns** -- blind's reason: Paper span: 96.2% completed the trial and vital status was obtained for 98.8%, below the 99% level, with no per-arm balance or sensitivity analysis reported.
- FLOW D3_missing_outcome_data: lane **low**, blind **some_concerns** -- blind's reason: Paper span: vital status known in 98.6% only, below the 99% level, with no primary-outcome completeness or per-arm balance reported.

**Direction warning:** 6 domains changed AFTER the blind read on newly bound evidence, and all 6 moved toward *low*: SOUL D5, AMPLITUDE-O D5, HARMONY Outcomes D5, SOUL D2, SUSTAIN-6 D1, ELIXA D1. Each rests on a new span, but a one-directional pattern after a second opinion is exactly what a reviewer should weigh -- SUSTAIN-6 and ELIXA D1 in particular stand on incidental IV/WRS mentions.

**Second blind read on the CURRENT spans** (run to test that warning; same family, blind): agreement **46 of 50**; the post-blind moves were supported in **5 of 5**. Remaining disagreements, kept for you:

- LEADER D3_missing_outcome_data: lane **low**, second reader **some_concerns** -- Paper spans: vital status 99.7% but only 96.8% completed a final visit, died or had a primary outcome, leaving about 3% with incomplete MACE ascertainment and no balance/sensitivity information. **[answered after the read: per-arm vital status bound AFTER this read: unavailable 12 (0.25%) vs 17 (0.36%) (FDA review of NDA 022341/S-027)]**
- AMPLITUDE-O D3_missing_outcome_data: lane **low**, second reader **some_concerns** -- Paper span: primary-outcome status known for only 3941/4076 (96.7%) though vital status 99.9%; the 3.3% with unknown MACE status has no by-arm balance or sensitivity analysis in the spans, so 'nearly all' cannot be confirmed and missingness could plausibly relate to events. **[answered after the read: NOT answered: the registry's COMPLETED milestone (42/36/23) reflects sponsor termination, not outcome ascertainment, so no held source gives per-arm primary-outcome status; the per-arm split is in the paper's Supplementary Appendix, which is not held]**
- REWIND D4_outcome_measurement: lane **low**, second reader **some_concerns** -- Protocol span: independent CEC adjudicates all primary events, but no span states the adjudicators were blinded (4.3 NI) and MI/stroke adjudication involves judgement. **[answered after the read: committee blinding bound AFTER this read: 'adjudicated by an independent committee of physicians blinded to the study medication' (PMC7690176)]**
- EXSCEL D3_missing_outcome_data: lane **low**, second reader **some_concerns** -- Paper span: only 96.2% completed the trial (vital status 98.8%), so MACE status is incomplete for about 3.8% with no balance or sensitivity information in the spans. **[answered after the read: per-arm completion bound AFTER this read: not completed 303/7396 (4.1%) placebo vs 262/7356 (3.6%) exenatide (registry participant flow; completers sum to the paper's 14,187)]**
- (the second reader itself flagged that its D3 calls penalise trials that report MORE: those giving a ~96-97% primary-outcome completeness figure were rated some_concerns while trials reporting only vital status >=98.6% were rated low)

## AMPLITUDE-O (PMID 34215025, NCT03496298) -- overall proposal: low

| domain | proposal | why | witness sources | reviewer decision |
|---|---|---|---|---|
| D1 randomisation | **low** | Central IRT with a permuted-block schedule (sequence + concealment). | sap: `NCT03496298/SAP_001.pdf` | ______ |
| D2 deviations (assignment) | **low** | Identically appearing blinded syringes; efficacy analysis in the ITT population. | paper: `34215025/enlighten_246785.pdf`; sap: `NCT03496298/SAP_001.pdf` | ______ |
| D3 missing outcome data | **low** | Vital status known for 99.9%; primary-outcome status known for 96.7% (the 3.3% gap is noted for the reviewer). | paper: `34215025/enlighten_246785.pdf` | ______ |
| D4 outcome measurement | **low** | Independent end-point committee unaware of trial-group assignments. | paper: `34215025/enlighten_246785.pdf` | ______ |
| D5 selection of reported result | **low** | [low on NEW evidence bound after the blind read] The paper states the analyses followed two prespecified plans 'finalized before any unblinding occurred' (RoB 2 5.1 = Y); the protocol amendment (approved 30 July 2018) defines the adjudicated MACE outcome. | paper: `34215025/enlighten_246785.pdf`; protocol: `NCT03496298/Prot_000.pdf`; protocol: `NCT03496298/Prot_000.pdf` | ______ |

Stopped treatment (D2 context, not missing data): exposure 88.9% vs 91.1% of follow-up time; followed to trial end regardless of adherence

## ELIXA (PMID 26630143, NCT01147250) -- overall proposal: some_concerns

| domain | proposal | why | witness sources | reviewer decision |
|---|---|---|---|---|
| D1 randomisation | **low** | [low on NEW evidence bound after the blind read] Patients were randomised in the central Interactive Voice Response System (1.1/1.2 = PY, the same basis as SUSTAIN-6); baseline characteristics generally similar. The IVRS mention is incidental (a patient narrative) -- reviewer to confirm. | regulator: `FDA_208471/MedR.pdf`; regulator: `FDA_208471/MedR.pdf` | ______ |
| D2 deviations (assignment) | **low** | Double-blind; MACE analyses in the ITT, all-as-randomised population. | regulator: `FDA_208471/MedR.pdf`; regulator: `FDA_208471/MedR.pdf` | ______ |
| D3 missing outcome data | **low** | Vital status available for 99%; 71 lacked vital-status follow-up (42 placebo vs 29 lixisenatide). | regulator: `held/208471Orig1s000StatR.pdf` | ______ |
| D4 outcome measurement | **low** | Cardiovascular adjudication committee blinded to treatment assignment. | regulator: `FDA_208471/MedR.pdf` | ______ |
| D5 selection of reported result | **some_concerns** | PRESPECIFICATION DISPUTE, three sources quoted: (1) the FDA STATISTICAL review lists 'time to first secondary MACE event (CV death, non-fatal MI and non-fatal stroke)' as one of two secondary endpoints and calls its Cox analysis 'pre-specified'; (2) the FDA SUMMARY review of the same NDA calls the three-component MACE a SENSITIVITY analysis; (3) the REGISTRY (NCT01147250) registers the 4-point MACE+ as primary and, as secondary outcomes, only a 5-point composite (+HF hospitalisation), a 6-point composite (+revascularisation) and UACR -- the 3-point composite is registered as neither. No dated SAP is held. The sources disagree on whether the reported 3-point result was a prespecified endpoint, so 5.1 cannot be answered yes. (Eligibility for the pool is unaffected: B-prime admits the exact three components, prospectively adjudicated.) | regulator: `held/208471Orig1s000StatR.pdf`; regulator: `held/208471Orig1s000StatR.pdf`; regulator: `FDA_208471/SumR.pdf`; registry: `registry/NCT01147250.json`; registry: `registry/NCT01147250.json`; registry: `registry/NCT01147250.json`; registry: `registry/NCT01147250.json` | ______ |

Stopped treatment (D2 context, not missing data): more discontinued lixisenatide early; exposures overall balanced

## EXSCEL (PMID 28910237, NCT01144338) -- overall proposal: some_concerns

| domain | proposal | why | witness sources | reviewer decision |
|---|---|---|---|---|
| D1 randomisation | **low** | IVRS, computer-generated block randomisation within site, stratified; groups did not differ at baseline. | paper: `PMC9792409/efetch.xml`; paper: `PMC9792409/efetch.xml` | ______ |
| D2 deviations (assignment) | **low** | Double-blind, matching placebo; Cox analyses in the intention-to-treat population. | paper: `PMC9792409/efetch.xml`; paper: `PMC9792409/efetch.xml` | ______ |
| D3 missing outcome data | **low** | 96.2% completed; vital status obtained for 98.8%, including searches of health records for those lost or withdrawn. Per arm (registry participant flow, bound after the blind reads; its completers 7093 + 7094 = the paper's 14,187): not completed 303/7396 (4.1%) placebo vs 262/7356 (3.6%) exenatide -- small and balanced, answering the second reader's 'no balance information' point; the level was not moved. | paper: `PMC9792409/efetch.xml`; registry: `registry/NCT01144338.json` | ______ |
| D4 outcome measurement | **low** | Independent clinical events classification committee unaware of trial-group assignments. | paper: `PMC9792409/efetch.xml` | ______ |
| D5 selection of reported result | **some_concerns** | Evidence the plan was fixed while blinded, bound after the blind reads but NOT used to move the level (every post-blind move so far went toward low): the SAP's amendment history starts with an 'Initial Approved SAP' on 13 Oct 2010; Edition 4 is dated 23 Feb 2017; amendments followed 'blinded review'; major deviations were 'reviewed and finalized by the team in a blinded manner, prior to data base lock'. The design paper fixes the ITT superiority analysis. No span states the SAP was final before unblinding, so 5.1 is PY at best -- REVIEWER: this may justify low. | sap: `NCT01144338/SAP_001.pdf`; sap: `NCT01144338/SAP_001.pdf`; sap: `NCT01144338/SAP_001.pdf`; paper: `SPIRAL_exscel/design.pdf` | ______ |

Stopped treatment (D2 context, not missing data): premature discontinuation of the regimen, driven by patient decision, was a major limitation

## FLOW (PMID 38785209, NCT03819153) -- overall proposal: low

| domain | proposal | why | witness sources | reviewer decision |
|---|---|---|---|---|
| D1 randomisation | **low** | Central IWRS 1:1 with visually identical placebo, stratified by SGLT2i use; no major baseline imbalances. | paper: `PMC10469096/fullText.xml`; paper: `PMC11485243/fullText.xml` | ______ |
| D2 deviations (assignment) | **low** | Participants, investigators and trial personnel blinded; ITT estimand (irrespective of adherence), FAS = all randomised as assigned. | paper: `PMC10469096/fullText.xml`; sap: `NCT03819153/SAP_001.pdf` | ______ |
| D3 missing outcome data | **low** | Vital status known for 98.6%. | paper: `PMC11931213/fullText.xml` | ______ |
| D4 outcome measurement | **low** | External, independent, blinded EAC. | protocol: `NCT03819153/Prot_000.pdf` | ______ |
| D5 selection of reported result | **low** | Design paper (Jan 2023, before the Oct 2023 stop) and SAP v1.0 (07-Apr-2019) name 3-point MACE a confirmatory secondary endpoint analysed by stratified Cox. | paper: `PMC10469096/fullText.xml`; sap: `NCT03819153/SAP_001.pdf`; sap: `NCT03819153/SAP_001.pdf` | ______ |

Stopped treatment (D2 context, not missing data): permanent discontinuation 28.8% (pooled); protocol keeps discontinuers in follow-up

## HARMONY Outcomes (PMID 30291013, NCT02465515) -- overall proposal: low

| domain | proposal | why | witness sources | reviewer decision |
|---|---|---|---|---|
| D1 randomisation | **low** | Sequestered, fixed randomisation schedule (concealed), matching placebo, 1:1. | paper: `30291013/enlighten_170787.pdf` | ______ |
| D2 deviations (assignment) | **low** | All randomised patients analysed whether or not treatment was taken (ITT), matching placebo. | paper: `30291013/enlighten_170787.pdf` | ______ |
| D3 missing outcome data | **low** | Vital status unknown for 61 of 9463 (0.6%). | paper: `30291013/enlighten_170787.pdf` | ______ |
| D4 outcome measurement | **low** | Independent clinical events classification committee unaware of trial-group assignments. | paper: `30291013/enlighten_170787.pdf` | ______ |
| D5 selection of reported result | **low** | [low on NEW evidence bound after the blind read] The Reporting and Analysis Plan took effect 30-NOV-2017, while close-out visits (from 8 Nov 2017) ran to trial completion in March 2018, and the RAP fixes that planned analyses are performed after database freeze: the plan predates the unblinded data (RoB 2 5.1 = PY). The RAP specifies time to first MACE as the primary analysis. | sap: `NCT02465515/SAP_001.pdf`; sap: `NCT02465515/SAP_001.pdf`; paper: `30291013/enlighten_170787.pdf`; sap: `NCT02465515/SAP_001.pdf` | ______ |

Stopped treatment (D2 context, not missing data): 24% vs 27% discontinued study medication prematurely (not death)

## LEADER (PMID 27295427, NCT01179048) -- overall proposal: some_concerns

| domain | proposal | why | witness sources | reviewer decision |
|---|---|---|---|---|
| D1 randomisation | **some_concerns** | 1:1, stratified by eGFR. Bound after the blind reads from the FDA review of NDA 022341/S-027: baseline characteristics 'generally well-balanced' (1.3 = N), and emergency code breaks were recorded through the sponsor's IV/WRS (OCR 'IVNVRS'), i.e. allocation was held centrally. That is indirect for concealment (1.2 = PY at best) and says nothing on sequence generation (1.1 = NI); RoB 2's algorithm would allow low on 1.2 = PY, so REVIEWER: this may justify low. Not moved by the lane, because the concealment inference rests on a code-break footnote, not a statement about how patients were randomised. | paper: `PMC4985288/efetch.xml`; regulator: `FDA_022341_s027/review_package.pdf`; regulator: `FDA_022341_s027/review_package.pdf` | ______ |
| D2 deviations (assignment) | **low** | Double-blind, matching placebo; all randomised included in the primary analysis. | paper: `PMC4985288/efetch.xml`; paper: `PMC4985288/efetch.xml` | ______ |
| D3 missing outcome data | **low** | Vital status known for 99.7%; per arm, unavailable for 12 (0.25%) on liraglutide vs 17 (0.36%) on placebo (FDA review); 96.8% completed a final visit, died or had a primary outcome. | paper: `PMC4985288/efetch.xml`; regulator: `FDA_022341_s027/review_package.pdf`; paper: `PMC4985288/efetch.xml` | ______ |
| D4 outcome measurement | **low** | Adjudicated in a blinded fashion by an external independent committee. | paper: `PMC4985288/efetch.xml` | ______ |
| D5 selection of reported result | **low** | [low on NEW evidence: FDA review of NDA 022341/S-027] The FDA reviewer records the SAP changes made 'before breaking the blind' (three SAP versions) and that blinding was maintained until the code break on 02 February 2016, with database lock three days later (RoB 2 5.1 = Y). The 2013 design paper fixes 3-point MACE as the primary end point. | regulator: `FDA_022341_s027/review_package.pdf`; regulator: `FDA_022341_s027/review_package.pdf`; paper: `24176437/europepmc_core.json` | ______ |

Stopped treatment (D2 context, not missing data): time on regimen 84% vs 83%; more stopped liraglutide for adverse events

## PIONEER 6 (PMID 31185157, NCT02692716) -- overall proposal: low

| domain | proposal | why | witness sources | reviewer decision |
|---|---|---|---|---|
| D1 randomisation | **low** | Sequence by IV/WRS (central, concealed), stratified; baseline similar. | paper: `PMC6587508/fullText.xml`; paper: `31185157/radboud_208030.pdf` | ______ |
| D2 deviations (assignment) | **low** | Double-blind with matching placebo; all analyses in the full analysis set = all randomised (ITT, as randomised). | paper: `31185157/radboud_208030.pdf`; sap: `NCT02692716/SAP_001.pdf` | ______ |
| D3 missing outcome data | **low** | Vital status collected for the 11 non-completers: every randomised patient accounted for. | paper: `31185157/radboud_208030.pdf` | ______ |
| D4 outcome measurement | **low** | Events adjudicated by an independent external committee unaware of trial-group assignments. | paper: `31185157/radboud_208030.pdf` | ______ |
| D5 selection of reported result | **low** | Protocol (not registry) fixes 3-point MACE as the primary endpoint; the SAP keeps treatment blinding until database release (analysis plan fixed before unblinding). | protocol: `NCT02692716/Prot_000.pdf`; sap: `NCT02692716/SAP_001.pdf` | ______ |

Stopped treatment (D2 context, not missing data): more permanently discontinued oral semaglutide (11.6% vs 6.5%); follow-up continued

## REWIND (PMID 31189511, NCT01394952) -- overall proposal: low

| domain | proposal | why | witness sources | reviewer decision |
|---|---|---|---|---|
| D1 randomisation | **low** | Computer-generated random sequence via IVRS (concealed), 1:1, stratified by site. | protocol: `NCT01394952/Prot_000.pdf` | ______ |
| D2 deviations (assignment) | **low** | Double-blind treatment period; primary analyses by intent-to-treat. | protocol: `NCT01394952/Prot_000.pdf`; protocol: `NCT01394952/Prot_000.pdf` | ______ |
| D3 missing outcome data | **low** | Registry participant flow (rendered from V1.1): 'completers' include participants whose vital status was ascertained at close-out; completed 4935/4952 vs 4932/4949 (99.7% each arm); not completed 17 vs 17. The protocol required vital status for all randomised. | registry: `registry/NCT01394952.json`; registry: `registry/NCT01394952.json`; protocol: `NCT01394952/Prot_000.pdf` | ______ |
| D4 outcome measurement | **low** | Independent CEC adjudicates all primary endpoint events (protocol); a REWIND secondary paper states the events were adjudicated by an independent committee of physicians BLINDED to the study medication using pre-specified definitions. | protocol: `NCT01394952/Prot_000.pdf`; paper: `PMC7690176/fullText.xml` | ______ |
| D5 selection of reported result | **low** | SAP version 1 approved 21 Nov 2011 before the first unblinding; the protocol fixes the 3-point composite as the primary efficacy measure. | sap: `NCT01394952/SAP_001.pdf`; protocol: `NCT01394952/Prot_000.pdf` | ______ |

## SOUL (PMID 40162642, NCT03914326) -- overall proposal: low

| domain | proposal | why | witness sources | reviewer decision |
|---|---|---|---|---|
| D1 randomisation | **low** | Central IWRS randomisation 1:1 (sequence and concealment via the system); baseline balance not held (1.3 = NI, which RoB 2 allows at low). | paper: `UCL_10169247/soul_design.pdf` | ______ |
| D2 deviations (assignment) | **low** | [low on NEW evidence bound after the blind read] Blinded (visually identical tablets) and all analyses by intention-to-treat methods on the full analysis set of all unique randomised participants (2.6 = Y). | paper: `UCL_10169247/soul_design.pdf`; paper: `UCL_10169247/soul_design.pdf` | ______ |
| D3 missing outcome data | **low** | Registry participant flow (rendered from V1.1): completed 4755/4825 vs 4740/4826 (98.5% vs 98.2%); not completed 70 vs 86 -- lost to follow-up 43 vs 51, withdrew 27 vs 34: small and balanced. This is TRIAL COMPLETION, not a vital-status figure (the results paper, which would give vital status, is not held) -- weigh accordingly. | registry: `registry/NCT03914326.json`; registry: `registry/NCT03914326.json`; registry: `registry/NCT03914326.json` | ______ |
| D4 outcome measurement | **low** | Central adjudication by a masked external committee. | paper: `UCL_10169247/soul_design.pdf` | ______ |
| D5 selection of reported result | **low** | [low on NEW evidence bound after the blind reads; same basis as the PIONEER 6 precedent] The SAP is Version 2.0, Status Final, dated 14 December 2022, and states Novo Nordisk remains blinded to treatment allocations until database lock; the design paper (received 13 January 2023) still describes the trial as ongoing before database lock, so the final plan predates unblinding (RoB 2 5.1 = PY). The SAP fixes 3-point MACE as the primary endpoint; the 2023 design paper names the same outcome before the 2025 results. Another move toward low after a blind read -- reviewer to confirm. | sap: `NCT03914326/SAP_001.pdf`; sap: `NCT03914326/SAP_001.pdf`; sap: `NCT03914326/SAP_001.pdf`; paper: `UCL_10169247/soul_design.pdf`; paper: `UCL_10169247/soul_design.pdf`; paper: `UCL_10169247/soul_design.pdf` | ______ |

## SUSTAIN-6 (PMID 27633186, NCT01720446) -- overall proposal: low

| domain | proposal | why | witness sources | reviewer decision |
|---|---|---|---|---|
| D1 randomisation | **low** | [low on NEW evidence bound after the blind read] Randomisation registered in the central IV/WRS (sequence and concealment by the system: 1.1/1.2 = PY); baseline balanced. The stratification errors the FDA records were mis-entered strata, not a breach of concealment -- reviewer to confirm. | regulator: `FDA_209637/MedR.pdf`; regulator: `FDA_209637/StatR.pdf`; regulator: `FDA_209637/MedR.pdf` | ______ |
| D2 deviations (assignment) | **low** | Double-blind within dose group; FAS analysed by ITT as randomised. | regulator: `FDA_209637/StatR.pdf`; regulator: `FDA_209637/StatR.pdf` | ______ |
| D3 missing outcome data | **low** | Vital status for 99.6% of all randomised; 13 lacked it (6 vs 7). | regulator: `FDA_209637/StatR.pdf` | ______ |
| D4 outcome measurement | **low** | External independent EAC adjudicating in a blinded manner. | regulator: `FDA_209637/StatR.pdf` | ______ |
| D5 selection of reported result | **low** | The FDA statistical reviewer, reading the protocol/SAP, states the MACE time-to-first-event analysis was pre-specified; no dated SAP is held -- a human should weigh a regulator's statement vs a dated plan. | regulator: `FDA_209637/StatR.pdf`; regulator: `FDA_209637/StatR.pdf` | ______ |

Stopped treatment (D2 context, not missing data): more discontinued semaglutide for adverse events (abstract)
