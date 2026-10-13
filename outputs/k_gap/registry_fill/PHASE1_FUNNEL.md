# Phase 1 (CT.gov / AACT): k-gap fill funnel -- all 32 topics (AACT snapshot 2026-08-30; CT.gov API v2 freshness)

Population: every comparator trial we do not pool that is not named out of scope (g1_trial_acquire.targets): 141.

| stage | n of N | lost at this stage (typed reason) |
|---|---|---|
| comparator trials missing | 141 | -- |
| NCT resolved | 58 of 141 | 59 PMID but no registration stated (PubMed databank / abstract / label / k-gap table / registry RESULT ref); 22 no PMID and no registration; 2 registered OUTSIDE CT.gov (ANZCTR: Young, Tong) |
| results posted (AACT) | 21 of 58 | 37 registered, no posted results (CT.gov v2 agrees: none posted after the snapshot) |
| outcome matched (typed binding) | 3 of 21 | 18 posted, but no posted outcome binds to the protocol outcome (pcsk9 lipid trials post LDL / atheroma, not MACE; tocilizumab trials post ventilation-or-death composites / WHO scale) |
| admitted (codex + agy + adjudicator) | **1 of 3** | SMART: both readers REFUSED (posted N is the medical-ICU subpopulation); ASCEND: no gated omega-3 reading (reader B took the ASPIRIN factorial pair twice -- refused by the arm gate; reader A UNSURE) |

**Active (G1) topics: 0 trials reach "outcome matched".**
- Active open gaps: 12 (+1 secondary-only).
- iv-iron 2: NCT, no posted results. cortico-covid 4: NCT, no posted results. melatonin 2: no registration. statins 5: 3 NCT, no posted results.
- **Phase 1 cannot move G1 under the current binding gates.**

## Binding-gate question for the Captain (gate change: NOT made by the lane)

Two posted outcomes are refused only because the naming check reads the outcome TITLE alone:

1. **BACC-Bay (tocilizumab, NCT04356937), outcome "Mortality", time frame "28 days".**
   - The title plus the time frame name the protocol's 28-day all-cause mortality.
   - Proposed typed rule: the time frame may supply the timepoint the title omits, when the title names the event exactly.
2. **ORIGIN (omega3, NCT00069784), primary "Composite of the First Occurrence of Cardiovascular (CV) Death, Nonfatal Myocardial Infarction ...".**
   - This is 3-point MACE named by its exact components.
   - Proposed typed rule: a composite whose components are exactly the protocol composite's components names it (extract.composite_component_mismatch already compares component sets).

**Correctly refused (not proposed):**
- COVIDOSE2: 30-day overall survival (wrong timepoint).
- CORIMUNO: survival posted for 14 / 28 / 90 days in ONE outcome (multiple time frames).
- REMDACTA: "Time to Death up to Day 28" (a time-to-event estimand; the protocol is OR).

**G1 effect of the two proposed rules: none.** Both topics are abandoned. They would add k-gap rows only.

## Stage 4 pilot (the 3 bound trials) -- recorded calls in evidence/model_calls/registry_fill

| trial | reader A (codex gpt-6-astra) | reader B (agy, Gemini 3.8 Flash) | adjudicator (codex gpt-5.5) | decision |
|---|---|---|---|---|
| SALT NCT02345486 (balanced-crystalloids) | UNSURE | ADMITTED: 72/520 v 68/454, outcome 258389389 "In-hospital Mortality", 30 days | ADMITTED, agrees with B | **ADMITTED.** Population: ALL_RANDOMISED (typed: 520 + 454 = 974 = actual enrollment, CT.gov v2). Phase 1_REGISTRY:AACT |
| ASCEND NCT00135226 (omega3) | UNSURE | took the ASPIRIN pair 658/7740 v 743/7740 -> REFUSED by the arm gate | not run (no gated reading) | NOT ADMITTED. The correct omega-3 pair (689/7740 v 712/7740) is posted under the same outcome; neither reader returned it. |
| SMART NCT02444988 (balanced-crystalloids) | REFUSED: POSTED_N_IS_A_SUBPOPULATION | REFUSED: same | -- | NOT ADMITTED |

**Defects found and fixed during the pilot (each planted, tests/test_registry_fill.py):**
1. **Arm identity.** The AACT gate checked the OUTCOME, never the ARMS: two readers admitted ASCEND's aspirin comparison for the omega-3 topic. New gate: the experimental arm's title carries a distinctive intervention token; the control is not the intervention unless it is its placebo; never another agent's placebo; ambiguous groups refused.
2. **Analysis population.** The registry's population field is blank for about 1 in 4 posted outcomes. Mahmood's rule ("must be named") is kept. The only typed naming is the exact equality analysed total = ACTUAL enrollment; anything else is refused. **For the Captain to confirm.**
3. **agy client.** The prompt travels as the --print argument (Windows ~32k cap). Evidence is typed-narrowed (bound outcomes in full, others by title), and a prompt that is still too long is a typed reader-unavailable state, not a crash.
4. **agy answer.** Prose precedes the JSON ("I have launched the test command" -- the record shows 0 tool calls, 1 turn). The parser takes the last complete JSON object; the gate verifies every number.

**G1 effect: NONE.** SALT is on an abandoned topic. **Served numbers: none move.**

**Phase 1 is MAXED** under the current gates: 1 of 141. The two near-misses (BACC-Bay title + time frame; ORIGIN component-named MACE) wait on the Captain's binding-gate ruling. ASCEND waits on a deterministic arm picker (Phase 2 method: deterministic first) or a re-read.
