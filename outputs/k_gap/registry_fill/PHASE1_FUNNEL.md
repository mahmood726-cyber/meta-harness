# Phase 1 (CT.gov / AACT): k-gap fill funnel -- all 32 topics (AACT snapshot 2026-08-30; CT.gov API v2 freshness)

Population: every comparator trial we do not pool that is not named out of scope (g1_trial_acquire.targets): 141.

| stage | n of N | lost at this stage (typed reason) |
|---|---|---|
| comparator trials missing | 141 | -- |
| NCT resolved | 57 of 141 | 58 PMID but no registration stated (each PubMed abstract FETCHED and read: PR #100 r1 records abstract_fetch per row; 0 fetch failures this run); 1 PMID whose PubMed record has NO abstract (typed NO_ABSTRACT_TO_READ, was counted as 'no registration'); 22 no PMID and no registration; 2 registered OUTSIDE CT.gov (ANZCTR: Young, Tong); 1 label NCT the registry does not hold (ODYSSEY JAPAN 'NCT02017898': CT.gov answers 404; the trial is NCT02107898 -- a transposition in the comparator label, reported to the Captain, not substituted by the lane) |
| results posted (AACT) | 21 of 57 | 36 registered, no posted results, and CT.gov v2 ANSWERED for every NCT that none is posted after the snapshot (r1: 'no posted results' now needs a source that answered) |
| outcome matched (typed binding) | 3 of 21 | 18 posted, no posted outcome binds: furthest gate reached OUTCOME_NOT_NAMED 14, ARMS 4, ESTIMAND 0 (breakdown below) |
| admitted (codex + agy + adjudicator) | **1 of 3** | SMART: both readers REFUSED (posted N is the medical-ICU subpopulation); ASCEND: no gated omega-3 reading (reader B took the ASPIRIN factorial pair twice -- refused by the arm gate; reader A UNSURE) |

**Active (G1) topics: 0 trials reach "outcome matched".**
- Active open gaps: 12 (+1 secondary-only).
- iv-iron 2: NCT, no posted results. cortico-covid 4: NCT, no posted results. melatonin 2: no registration. statins 5: 3 NCT, no posted results.
- **Phase 1 cannot move G1 under the current binding gates.**

## The 18 posted-but-not-bound trials, by reason (13 Oct; every posted outcome through g1_tracker.binding_verdict)

| furthest gate | trials | which |
|---|---|---|
| ARMS (outcome named, posted as a rate or %, no event counts) | 4 | ODYSSEY LONG TERM ('Percentage of participants ... MACE'), EMPACTA ('Mortality Rate by Day 28'), REMDACTA ('Difference in Mortality'), Ehrhardt (AAD episode totals / incidence density) |
| OUTCOME_NOT_NAMED, no outcome-family title posted at all | 7 | Pahor, Gao, ODYSSEY COMBO I / FH I / FH II / HIGH FH, DESCARTES, GLAGOV (lipid / atheroma outcomes only) |
| OUTCOME_NOT_NAMED, an outcome-family title IS posted | 7 | BACC-Bay, CORIMUNO-TOCI-1, CORIMUNO-TOCI-ICU, COV-AID, COVIDOSE2, ORIGIN (and FH-I/FH-II share one NCT pair) |
| ESTIMAND (named, refused on timepoint / definition) | 0 | -- |

**Named-divergence candidates: none is admissible without coercion.** Each family-titled outcome was read in full:
- BACC-Bay 'Mortality, 28 days': posted as Kaplan-Meier **percentages** in the mITT (242 of 243), with no event counts.
- CORIMUNO-TOCI: survival **percentages** at 14/28/90 days in one outcome, plus per-stratum **HRs** (the topic's estimand is not HR).
- COVIDOSE2: survivors at **30 days** as counts, in a 3-arm sub-study (SoC 24/26; tocilizumab **40 mg** 22/25, **120 mg** 25/25). Admitting it needs three divergences at once: death as the complement of survival, 30 v 28 days, and pooling two LOW-dose arms. **Not proposed.**
- COV-AID: a time-to-oxygen / ventilation / death composite. This is not mortality.
- **ORIGIN: the posted results are the insulin glargine v standard-care factor of the 2x2 factorial.** The omega-3 comparison is not posted. The earlier binding-gate request for ORIGIN's MACE composite is **withdrawn**: binding it would admit the wrong factor (the ASCEND class).

**Binding-gate question still open for the Captain:** BACC-Bay title + time frame. **It cannot move a number in any case:** the posting holds only Kaplan-Meier percentages.

## Stage 4 pilot (the 3 bound trials) -- recorded calls in evidence/model_calls/registry_fill

| trial | reader A (codex gpt-6-astra) | reader B (agy, Gemini 3.8 Flash) | adjudicator (codex gpt-5.5) | decision |
|---|---|---|---|---|
| SALT NCT02345486 (balanced-crystalloids) | UNSURE | ADMITTED: 72/520 v 68/454, outcome 258389389 "In-hospital Mortality", 30 days | ADMITTED, agrees with B | **ADMITTED.** Population: ALL_RANDOMISED (typed: 520 + 454 = 974 = actual enrollment, CT.gov v2). Phase 1_REGISTRY:AACT |
| ASCEND NCT00135226 (omega3) | UNSURE | took the ASPIRIN pair 658/7740 v 743/7740 -> REFUSED by the arm gate | not run (no gated reading) | NOT ADMITTED. The correct omega-3 pair (689/7740 v 712/7740) is posted under the same outcome; neither reader returned it. |
| SMART NCT02444988 (balanced-crystalloids) | REFUSED: POSTED_N_IS_A_SUBPOPULATION | REFUSED: same | -- | NOT ADMITTED |

**Defects found and fixed during the pilot (each planted, tests/test_registry_fill.py):**
1. **Arm identity.** The AACT gate checked the OUTCOME, never the ARMS: two readers admitted ASCEND's aspirin comparison for the omega-3 topic. New gate (tightened by PR #100 r1): the experimental arm's title carries EVERY distinctive token of one intervention term; the control is a comparator_any term or this intervention's own placebo (never an active factorial arm, never another agent's placebo); ambiguous groups refused.
2. **Analysis population.** The registry's population field is blank for about 1 in 4 posted outcomes. Mahmood's rule ("must be named") is kept. The only typed naming is the exact equality analysed total = ACTUAL enrollment; anything else is refused. **For the Captain to confirm.**
3. **agy client.** The prompt travels as the --print argument (Windows ~32k cap). Evidence is typed-narrowed (bound outcomes in full, others by title), and a prompt that is still too long is a typed reader-unavailable state, not a crash.
4. **agy answer.** Prose precedes the JSON ("I have launched the test command" -- the record shows 0 tool calls, 1 turn). The parser takes the last complete JSON object; the gate verifies every number.

**G1 effect: NONE.** SALT is on an abandoned topic. **Served numbers: none move.**

**Phase 1 is MAXED** under the current gates: 1 of 141. BACC-Bay's binding ruling cannot add a count (KM % only); ORIGIN's is withdrawn (glargine factor). ASCEND waits on a deterministic arm picker (Phase 2 method: deterministic first) or a re-read.
