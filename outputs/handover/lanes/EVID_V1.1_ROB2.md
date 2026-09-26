# V1.1 (not for the freeze): outcome-specific RoB 2 PROPOSALS, GLP-1 RA 3-point MACE

Branch `evid/v1.1-rob2` only. Nothing here is on main and nothing here is final.

**What it is.** For each of the 10 trials in the GLP-1 MACE pool (the 8 served, plus FLOW and ELIXA, which are pending signature), a RoB 2 judgement is proposed for each of the five domains. The result assessed is the 3-point MACE HR, effect of assignment. Every proposal carries witness spans cut from sha256-pinned held documents (protocol/SAP, main or design paper, registry, FDA review). `build_rob2.py` refuses to build if any span does not reproduce verbatim.

**Count.** Held evidence covers **50 of 50** domains (N = 10 trials x 5 domains). The proposals are low 47 and some_concerns 3 (LEADER D1, EXSCEL D5, ELIXA D5). There is no `NO_EVIDENCE_HELD` domain, and none was relabelled high.

**Where to review.** `evidence/rob2_glp1/REVIEW_SHEET.md` has one table per trial and an empty reviewer column. The spans are in the per-trial JSON.

**Guards kept** (rules R1-R5 in `build_rob2.py`, tests in `test_rob2_rules.py`):
- Stopped treatment is recorded separately (`D2_treatment_discontinuation`) and is never used as D3 missing outcome data.
- A registry entry alone is never taken as prespecification.
- A D5 low requires a plan finalised before unblinding; an outcome definition alone is not enough.

**What the reviewer should weigh first:**
1. **Direction.** Six domains changed after a blind read, and all six moved toward low (SOUL D5, AMPLITUDE-O D5, HARMONY D5, SOUL D2, SUSTAIN-6 D1, ELIXA D1). Each rests on a newly bound span.
2. **Blind reads** are Claude subagents. They are blind but not independent, and they saw spans only.

   | Read | Scope | Agreement | Note |
   |---|---|---|---|
   | 1 | 50 domains, earlier spans | 39 of 50 | |
   | 2 | 50 domains, current spans | 46 of 50 | supported all 5 moves made after read 1 |
   | 3 | 5 domains changed or gaining evidence after read 2 | 3 of 5 | supports SOUL D5 |

   Read 3 would move LEADER D1 and EXSCEL D5 to low. The lane did not follow, because those calls rest on an inference from a code-break footnote and on a deviations-review sentence.
3. **ELIXA D5.** The prespecification dispute is quoted from three sources: the FDA statistical review, the FDA summary review, and the registry.
4. **AMPLITUDE-O D3.** The per-arm split of the 3.3% with unknown primary-outcome status is only in the paper's Supplementary Appendix, which is not held.

**Local-only sources** (FDA packages, PMC-free HTML, sponsor SAPs) sit in `evidence/held_local` (gitignored). Their ledger is `evidence/LOCAL_ACQUISITIONS.json`, and `STORAGE_NOTE.md` says where the bytes live.
