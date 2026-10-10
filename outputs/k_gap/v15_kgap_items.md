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
