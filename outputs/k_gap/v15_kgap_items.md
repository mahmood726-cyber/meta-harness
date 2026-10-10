# V15 staging -- k-gap items (10 Oct evening; NOTHING APPLIED)

V14 was presented and signed, so it is frozen. Every item below is a V15 candidate, with its G1 effect stated BEFORE anything is applied.
Writer: k-gap lane. Sources:
- typed CT.gov API v2 responses (sha256 prefixes recorded);
- recorded model calls in evidence/model_calls/dual_screen;
- ledgers in outputs/k_gap/concept/ and outputs/k_gap/rescreen/.

## K-1. Third-reader sensitivity on the 69 DISAGREE records (Captain ruling 4)

- **Reader:** agy routed to Gemini, run as a NON-DECIDING third reader.
- **Liveness, proven first:** `agy --print` answered "OK, Gemini 3.1 Pro, Gemini". Every record reports `Gemini 3.1 Pro (High)` (pin holds).
- **Prompt:** the same verbatim-protocol prompt, plus the output schema stated in the prompt (agy does not receive codex's --output-schema).
- **Calls:** 69 recorded agy calls, 0 failures.
- **Defect found and fixed on the way: PR #61.** Every real agy call raised KeyError in `log_call` after the model answered, so no record was written. This was on main too.

**Pre-registered rule unchanged:** a split is NOT eligible. The 2-of-3 counts are a sensitivity only.

| ledger | DISAGREE | 2-of-3 ELIGIBLE | 2-of-3 EXCLUDED | still SPLIT | agy C decisions |
|---|---|---|---|---|---|
| doac (+esketamine) | 23 | 10 | 0 | 13 | INCLUDE 20, UNCLEAR 2, EXCLUDE 1 |
| sema-weight | 25 | 0 | 4 | 21 | UNCLEAR 19, EXCLUDE 4, INCLUDE 1, UNGATED 1 |
| melatonin | 6 | 1 | 0 | 5 | INCLUDE 5, EXCLUDE 1 |
| noac (held as (b)) | 9 | 4 | 4 | 1 | INCLUDE 4, EXCLUDE 4, UNGATED 1 |
| tranexamic | 2 | 0 | 1 | 1 | EXCLUDE 1, INCLUDE 1 |
| re-screen flips (verbatim) | 4 | 1 | 0 | 3 | INCLUDE 2, UNCLEAR 2 |
| **total** | **69** | **16** | **9** | **44** | |

**agy is the most inclusive reader.** It included 20 of 23 doac splits; on sema-weight it mostly answered UNCLEAR.

**doac 2-of-3 ELIGIBLE, by TRIAL.** Typed phase is from CT.gov.

| record(s) | trial | phase (typed) | held? |
|---|---|---|---|
| 17576867 | ODIXa-DVT, rivaroxaban dose-ranging (2007) | no registration in the record | new |
| 18621928 = NCT00395772 | Einstein-DVT dose-ranging | PHASE2 | new (1 trial, 2 records) |
| 25717286 (NCT01516814, NCT01516840) | J-EINSTEIN DVT + PE programmes | PHASE3 | new; **known recall miss** |
| 25912695 = NCT01780987 | AMPLIFY-J | PHASE3 | new (1 trial, 2 records) |
| 27155586 | rivaroxaban v genotype-adjusted warfarin | not stated | new |
| 27165711 (NCT01662908) | edoxaban MRV thrombus resolution | PHASE2 | new |
| 31277885 | recanalisation / post-thrombotic syndrome | not stated | new |
| 24298731 | Hokusai-VTE summary (Rev Med Liege) | -- | report of a HELD trial: inherits, not new |

**G1 effect (doac, G1_MATCHED 5/5 today):**
- Under the pre-registered rule, the DISAGREE records add no eligible trial.
- If 2-of-3 were adopted, 7 trials would be eligible and outside comparator 29795629 (phase-3-only).
  - PHASE_3_ONLY could name only the 3 typed non-phase-3 trials (Einstein dose-ranging, NCT01662908, plus ODIXa-DVT if its phase is typed from the abstract).
  - **J-EINSTEIN and AMPLIFY-J are PHASE3**, so a phase rule cannot name them.
  - doac would therefore leave G1_MATCHED under 2-of-3 unless another typed reason is found. Candidate reason: the comparator's own scope may exclude Japan-only bridging studies; its text has to be checked.

**Other 2-of-3 ELIGIBLE:**
- melatonin NCT07695246 (CBT-I + adjuvant melatonin). melatonin is already NOT_YET, so no status change.
- re-screen NCT02792400 (dpp4 glucagon mechanistic). dpp4 is held as (b); no change.
- noac (held as (b)): 21438804 (a RE-LY report: held trial, inherits), NCT00973245 (rivaroxaban phase 2, Japan), NCT01994265 (cognition), NCT03987711 (SAFE-D, dialysis).

**Question for the Captain:** adopt 2-of-3 going forward? Recommendation: NO for deciding eligibility.
- agy's inclusion rate is out of line with the two codex readers (doac 20/23 INCLUDE).
- 2-of-3 would turn a one-reader inclusion plus one UNCLEAR into an eligible trial.
- Keep it as a stated sensitivity.

## K-2. Names (Captain ruling 3). Drafts only.

**(a) doac's 3 newly eligible trials (2-reader rule):**
- BOTTICELLI 18541000: dose-ranging (abstract: "dose-ranging"); no registration in the record, so its phase is typed from the abstract wording only.
- 31455473: no registration, no stated phase, so **NOT_IN_COMPARATOR_SCOPE:PHASE_3_ONLY cannot be typed for it**.
- XENITH NCT02506985: PHASE4 (typed). Its posted PRIMARY outcomes are NETosis markers at 12/24/48 h, so OUTCOME_NOT_MEASURED is the stronger name.

G1 before/after:
- Before: doac G1_MATCHED.
- With BOTTICELLI (PHASE_3_ONLY) and XENITH (OUTCOME_NOT_MEASURED) named, 31455473 is still unnamed, so doac would be NOT_YET (ALL_ELIGIBLE_MATCHED unmet).
- Options:
  - (i) a typed rule for an unregistered single-centre trial;
  - (ii) accept NOT_YET;
  - (iii) read 31455473's full text for its phase. J Coll Physicians Surg Pak is open access; licence to be checked under D8.

**(b) STEP 5 (36216945 / NCT03693430): OUTCOME_ABSENT_AT_PROTOCOL_TIMEPOINT.**
- Basis: protocol line 18. Posted primary: "Percentage Change From Baseline (Week 0) to Week 104 in Body Weight".
- G1 before/after: sema-weight G1_MATCHED stays G1_MATCHED with the name; it becomes NOT_YET without it. No pooled number moves.

**(c) WITHDRAWN_NO_PARTICIPANTS, typed** (registry/withdrawn_no_participants.json: overall_status=WITHDRAWN AND enrollment 0 ACTUAL):
- NCT03852160 (esketamine, PHASE3): G1_MATCHED stays matched with the name.
- NCT04360876 (cortico-covid, PHASE2): cortico-covid is already NOT_YET; no change.

## K-3. SAK NCT05138575 (Captain ruling 5)

The contrast is valid per the ruling: empagliflozin + KCl v placebo-for-empagliflozin + KCl. The remaining criteria, quoted from protocols/empagliflozin-hfpef-hosp.md, against CT.gov (response sha256 b199b69f…):
- **I** "Empagliflozin 10 mg daily": registered "Empagliflozin (10 mg daily) + Potassium Chloride (6 mmol three times daily)". MET.
- **P** "adult HFmrEF/HFpEF ... LVEF >40%": registered "Left ventricular ejection fraction >= 50%", NYHA II-III. MET.
- **Design** "randomized, double-blind, placebo-controlled trial": registered RANDOMIZED, QUADRUPLE masking, PLACEBO_COMPARATOR arm. MET.
  - interventionModel = **CROSSOVER**: "3 interventions will be randomized", 6-week periods with a 2-week washout.
  - The protocol's design rule does not exclude crossover.
  - Per the ruling, crossover periods are never pooled naively.
- **Verdict:** ELIGIBLE on the protocol text.
- **Target outcome:** primary "Submaximal Exercise Endurance | Week 6"; status RECRUITING; no posted results. So it is "kept as target-result absent, not excluded" (the protocol's own line).

**G1 effect:**
- empagliflozin-hfpef is G1_MATCHED today (N 2, eligible 1, k 1).
- SAK eligible and outside comparator 37773799 makes ALL_ELIGIBLE_MATCHED fail unless it is named.
- Proposed name: TARGET_RESULT_ABSENT (recruiting, no results, primary is exercise endurance at 6 weeks). With the name, the topic stays G1_MATCHED. No pooled number moves.

## K-4. Acquisitions: STEP 3/8, PROSPER subgroup, EMPHASIS-HF lab K, JUPITER >=70 muscle, COPPS Table 3 (typed; D8)

**Method.** Ledger: outputs/k_gap/v15_acquisitions_agent.json (26 spans). Every span was re-verified by code as an exact substring of the fetched bytes it cites: 26/26 OK. Raw fetches are held with their sha256 in the ledger. Only open sources were read: PubMed, CT.gov, CC BY PMC, FDA. No paywalled primary paper was read.

**Results by target:**

- **STEP 3 (NCT03611582): FOUND, CT.gov posted MEAN (SD), "Baseline (week 0) to week 68".** Analysis sets: FAS 407 v 204.

  | period | semaglutide 2.4 mg | placebo |
  |---|---|---|
  | in-trial | n 373, -16.5 (10.1) | n 189, -5.8 (7.7) |
  | on-treatment | n 334, -17.6 (9.6) | n 164, -6.1 (7.6) |

  STEP 3 is Wadden 2021, already matched for sema-weight. The question is whether the served row uses the in-trial (treatment-policy) period.
- **STEP 8 (NCT04074161): FOUND, but only "Pooled Placebo".** Semaglutide 2.4 mg n 117, -16.4 (10.5); pooled placebo n 78, -1.6 (8.6); liraglutide n 117, -6.4 (7.7). The pool combines the semaglutide-matched and liraglutide-matched placebos, so no semaglutide-placebo-only result is posted.
  - Question: is the pooled placebo an admissible comparator for sema v placebo?
  - G1 effect if eligible: STEP 8 is outside comparator 42536519's set, so it needs a name or match.
- **PROSPER predefined no-prior-vascular-disease subgroup: PARTIAL.**
  - The primary abstract has the whole trial only: HR 0.85 (0.74-0.97).
  - HR 0.94 (0.77-1.15) appears only in two third-party CC BY reviews (PMC8667269, PMC11588824).
  - No open primary source shows the subgroup was PREDEFINED. The only "pre-defined subgroups" span is the PROSPER group's 2013 extended follow-up (a different analysis).
  - Recommendation: labelled sensitivity at most; not admissible as a primary-sourced row.
- **EMPHASIS-HF lab K > 5.5: claimed counts 158/1336 v 96/1340 NOT FOUND in any open source.** The abstract has percentages only: 11.8% v 7.2%.
  - CT.gov has investigator-reported AE "Hyperkalaemia": non-serious 95/1360 v 43/1369 (May 2010 cut-off), serious 16/1360 v 7/1369. These are a different endpoint, not lab-measured.
  - Proposal: SOURCE_ABSENT for lab K counts. The AE rows are only admissible as investigator-reported hyperkalaemia, labelled as such.
- **JUPITER >=70 muscle symptoms: SOURCE_ABSENT.**
  - The brief's PMID 20733113 is wrong; the Glynn paper is PMID 20404379.
  - Its abstract has no muscle data. The PMC copy is not CC. CT.gov AEs are not age-stratified.
  - The FDA S-016 Medical Review is a scanned PDF. OCR is the one remaining lead.
- **COPPS POAF (22090167) Table 3: SOURCE_ABSENT for primary per-arm counts.**
  - The abstract has 336 patients and 12.0% v 22.0% only.
  - The harness's inferred 20/169 v 37/167 gives **11.8% and 22.2%, which do NOT round to the abstract's 12.0% and 22.0%**. The inferred split is inconsistent with its own source, which supports binding's "refuse" option (review 24).
  - One third-party CC BY meta-analysis table (PMC9937735) prints 20/169 v 37/167. That is not independent of the same inference.
  - The auditor's 35 placebo events are in no open source.

## K-5. Family-eligibility reconcile count (reviews 7, 12, 13; outputs/k_gap/family_reconcile.md; source = served review.json on main 630e622bf)

**Rule:** ELIGIBLE iff at least 1 family record is INCLUDED by the record-level screen AND the structural family screen says ELIGIBLE.

**Reproduces the reviewers' figures where checked:**
- noac 12 -> 7;
- tranexamic 5 -> 2.

**Melatonin 3 -> 1, not the reviewer's 2.** The difference is Circadin NCT00816673: it is structurally ELIGIBLE, but its record is X3'd by the placebo-of-X screen defect. After the screen.py fix (K-gap item 1) it becomes 2, matching the reviewer. empagliflozin SAK NCT05138575 behaves the same way.

**Large drops:**
- glp1 145 -> 8: structural-only families with no included record (the B-prime universe);
- sema-weight 20 -> 6;
- sacubitril 7 -> 1;
- sglt2-pp 7 -> 2;
- dpp4 7 -> 4.

**Open rule question:** families with an included record but structural state UNKNOWN (e.g. EMPEROR-Preserved NCT03057951) are counted NOT eligible by this rule. The alternative, "eligible unless a trial-level exclusion is PROVEN", would count them. The Captain picks the rule; the per-family table carries both.

**G1 effect:** G1 compares trial units, not family counts, so this count moves no G1 status by itself. It changes the disclosed "eligible families" figure on every page (a wording/served-count change for V15).

## K-6. Comparator N from the INCLUDED set (review 17) -- PR #64 (code + plant; nothing applied)
- Fix: `seed_candidate_n()` in scripts/g1_tracker.py.
  - In REFERENCE_SEED_CANDIDATES state, the seeds are disclosed as N_candidates.
  - N = the comparator's OWN stated k when that is lower than the candidates (basis COMPARATOR_STATED_K).
  - Finding COMPARATOR_STATED_K_BELOW_SEED_CANDIDATES.
- Sweep over 32 (outputs/k_gap/comparator_n_sweep.md): **one N moves, sglt2-ckd 12 -> 10.** The comparator abstract says "10 randomized trials".
  - Which 2 seeds fall outside (the reviewer says DAPA-MI and EMPACT-MI) is NOT typed: comparator 41203232's text has no CC licence (Europe PMC licence None), so it is not read under D8.
  - **No G1 status changes** (sglt2-ckd stays NOT_YET).
- cortico-covid is the other seed-state topic: 5 seeds against "7 randomized clinical trials". It is under-enumerated, not over. The existing COMPARATOR_STATED_K_ABOVE_ENUMERATED_N finding covers it, and N is never inflated.

## K-7. Report-to-trial linking with INHERITED eligibility (review 15) -- sweep (outputs/k_gap/report_link_sweep.md); nothing applied
- **Rule.** A record excluded X2 is a REPORT of a trial family when a TYPED link exists:
  - PubMed DataBank NCT;
  - NCT stated in the abstract;
  - the title names the family's registry acronym as an exact UPPER-case token of 4+ letters, unique in the topic.
  - A linked report inherits the family's eligibility; an unlinked record is untouched.
- **Flips by reading of "eligible family"** (the same open rule as K-5):
  - STRICT, structural ELIGIBLE: 15 across 32 topics.
    - Active topics: sema-weight 6, sglt2-pp 2, doac 1, sacubitril 1 (40353367 -> NCT01035255 by acronym), tranexamic 1.
    - Abandoned topics: metformin 2, probiotics 1.
  - RECONCILED (included record, not INELIGIBLE): +1, **SELECT 38907684 -> NCT03574597 in sema-MACE** ("... Without Diabetes in SELECT."; no DataBank, no NCT in the record: the acronym is the only typed link). This is the reviewer's case.
- **G1 effect:** none. Every flip is a REPORT of a family already counted, so no trial unit is added and no G1 status changes. The served screening-record counts change (V15 wording/count).
- **Caveat:** sglt2-pp 33004472 -> NCT02792400 (a glucagon mechanistic study) inherits only because that family's structural screen calls it ELIGIBLE. The inheritance is only as sound as the family verdict.
- **Next:** the harness fix (inherit at screen time, with the SELECT plant and an unlinked same-phrase control) as its own PR.

## K-8. GLP-1 under the operating reading (ii) (Captain ruling 1; V14-07 signed: line 79) -- nothing applied

**Prompt.** The verbatim protocol including B-prime lines 78-79, plus the Captain's operating reading: MACE prespecified as a primary or key-secondary EFFICACY endpoint. A record that meets everything except that MACE was only safety-adjudicated is tagged LITERAL_ONLY.

**Regex first** (scripts/g1_glp1_mace_prefilter.py, typed):
- 615 concept records not already held (trial-identity dedup).
- 585 never mention MACE or any of its components in title + abstract: NO_MACE_MENTION, no model asked.
  - Audit of the dropped records that mention anything cardiovascular: risk factors, blood pressure, heart rate, QT; none is a MACE endpoint.
- 30 records went to the readers: codex A + B, with agy C as a non-deciding third reader. 90 recorded calls, 0 failures.

**Result under reading (ii), pre-registered 2-reader rule:**
- ELIGIBLE 0.
- EXCLUDED 16.
- DISAGREE 14. Mostly all three readers UNCLEAR / NOT_DECIDABLE_FROM_RECORD: the abstract does not say how MACE was specified.
- 2-of-3 sensitivity: EXCLUDED 17, SPLIT 13, ELIGIBLE 0.

**LITERAL_ONLY** was tagged by one reader (B) on 5 records: 21251180 (dulaglutide dose-finding), 26512041, 34873344, 41705420, NCT00747968. No record is LITERAL_ONLY by both readers.

**Reading (i), literal line 78: the universe is NOT countable from records.**
- Safety-adjudicated MACE (FDA 2008 programme adjudication) is rarely stated in an abstract or registration.
- So the 585 NO_MACE_MENTION records are not settled under (i).
- Counting (i) would need each trial's protocol or CSR. Under (i) the literal universe is up to the 615 regex-included records: the "flood" B-prime was written to prevent.

**G1 effect:**
- Under (ii), none: no new eligible trial; GLP-1 stays G1_MATCHED.
- Under (i), uncountable from open records; it would at least add the LITERAL_ONLY-tagged trials outside comparator 34526024. GLP-1 would leave G1_MATCHED unless every one is named.
- Recommendation: (ii), as already operated.

## K-9. screen.py placebo-of-X + structural-False fix -- PR #65 (code + plants + 32-topic sweep; nothing applied)

**Sweep** (served screen re-run on each topic's own inputs): 5 decisions change, all X-CONTRAST -> INCLUDE. Table: outputs/k_gap/screen_placebo_of_x_sweep.md.

**G1 effect of each**, stated before applying:

| topic | trial | G1 effect |
|---|---|---|
| finerenone | ARTS-DN Japan NCT01968668 | None: already named NOT_IN_COMPARATOR_OUTCOME_ANALYSIS. |
| melatonin | Circadin NCT00816673 | None: topic is NOT_YET. Reconcile count 1 -> 2 (= review 12). |
| colchicine-secondary | NCT03376698 | None: abandoned topic. |
| empagliflozin-hfpef | SAK NCT05138575 | AT RISK unless named TARGET_RESULT_ABSENT (K-3). |
| esketamine | NCT01998958 (intranasal esketamine dose-finding) | RESOLVED BY A TYPED SPAN (below): excluded; esketamine stays G1_MATCHED. |

**esketamine NCT01998958, the span:**
- Source: the primary report PubMed 29282469, linked to NCT01998958 by its PubMed Secondary Source ID (esearch NCT01998958[si] -> 33128208, 29282469); abstract record sha256 14c14d56a0fb…
- It states: "Participants continued their existing antidepressant treatment during the study."
- The protocol requires "intranasal esketamine, added to a newly-initiated oral antidepressant" (protocols/esketamine-trd-madrs.md line 5; line 12: "The randomized intervention is intranasal esketamine plus an oral antidepressant").
- So the trial fails the intervention criterion: X3, wrong intervention context, with that span.
- With the exclusion recorded, esketamine stays G1_MATCHED (3/3). Without it, the fix alone would admit the trial and esketamine would leave G1_MATCHED.
- The CT.gov registration (sha256 d8fdc435…) says only "Adjunctive to Oral Antidepressant Therapy", which is not decisive by itself.
