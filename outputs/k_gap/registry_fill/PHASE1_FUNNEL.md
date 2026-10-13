# Phase 1 (CT.gov / AACT): k-gap fill funnel -- all 32 topics (AACT snapshot 2026-08-30; CT.gov API v2 freshness)

Population: every comparator trial we do not pool that is not named out of scope (g1_trial_acquire.targets): 141.

| stage | n of N | lost at this stage (typed reason) |
|---|---|---|
| comparator trials missing | 141 | -- |
| NCT resolved | 58 of 141 | 59 PMID but no registration stated (PubMed databank / abstract / label / k-gap table / registry RESULT ref); 22 no PMID and no registration; 2 registered OUTSIDE CT.gov (ANZCTR: Young, Tong) |
| results posted (AACT) | 21 of 58 | 37 registered, no posted results (CT.gov v2 agrees: none posted after the snapshot) |
| outcome matched (typed binding) | 3 of 21 | 18 posted, but no posted outcome binds to the protocol outcome (pcsk9 lipid trials post LDL / atheroma, not MACE; tocilizumab trials post ventilation-or-death composites / WHO scale) |
| admitted (codex + agy + adjudicator) | pending | stage 4 pilot on the 3 |

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
