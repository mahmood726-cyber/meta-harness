# Findings, 2026-09-22 — measured on branch `enforcement-gate` = b25027e3 (landed 2026-09-21, RED by design, NOT on main)

Served site and `main` are still `38c04411`. Nothing here is landed, fixed or published. Every number was measured on the
commit named beside it; where a figure was later corrected, the correction is marked **CORRECTION** in place in the file,
with the superseded value and the lane that produced the correction — figures relayed to Mahmood during the day are
retracted explicitly, never silently updated.

## Findings

| File | What it says | Severity |
|---|---|---|
| [HAZARD_exhaustive_claim_over_incomplete_representation.md](HAZARD_exhaustive_claim_over_incomplete_representation.md) | Four instances in one session of an exhaustive claim ("0 of N", "all held documents", "no families") made over a view that did not carry the data. Cure: **an exhaustive claim needs a positive control that would have fired, or it is not an exhaustive claim.** | Standing hazard — the transferable one |
| [FINDING_bound_verified_wrong_span.md](FINDING_bound_verified_wrong_span.md) | Bindings that are LOCATED, verified and point at the wrong span. Prevalence (lane WS): **12 of 46 served trial-outcome rows on 7 of 32 pages**, lower bound. Severe case: `spironolactone-hfref-mortality` serves All-cause mortality HR 0.85 (0.53–1.36) k=1 from J-EMPHASIS-HF, where the held abstract assigns that HR to the primary **composite** and reports deaths 17/111 vs 10/110. Denominator: only **23 of 46** served rows carry a locatable source at all; on the other 23 the class is unassessable, not absent. | Served number wrong on main |
| [FINDING_design_masking_andor.md](FINDING_design_masking_andor.md) | `screen.py:_double_blind` accepts the word "placebo" as proof of masking. On 38c04411 it is the only in-screen blinding evidence for **11 of 35** pooled rows on the 14 AND-protocol pages and **30 of 135** included records. Errs both ways (**2 of 15** blinding refusals false). **Zhao 2009 (PMID 20146881) is the first nameable wrong admission on the served site** — single-blind per two independent public reviews; included, unextracted, 0 of 3 pools. Lane Z25: 25 of 25 others confirmed double-blind against public sources, so **1 of 26** survives a full public check. | Wrong admission on main |
| [CONVERGENCE_recovery_comparator.md](CONVERGENCE_recovery_comparator.md) | The RECOVERY comparator conflict reached independently by F1 (protocol contract) and B53 (eligibility screen). Also records that RECOVERY rows 5 and 53 sit in **two** findings at once (comparator conflict AND registry epoch mismatch) — neither may be closed alone. | Convergence + double membership |
| [NOTES_for_next_landings.md](NOTES_for_next_landings.md) | F5's served-site coverage line (independent screener on 5 of 32 pages, 53 of 269 included rows); F2 branch costs; pointers to the plants already observed pre-fix. | Landing inputs |

## Lane reports (`lane-reports/`, one directory per lane: report + artefact JSON + full `lane.log`; briefs as `BRIEF_*.md`)

All lanes ran `codex exec -c model_reasoning_effort=xhigh` in a fresh sparse clone at `b25027e3`; none committed; each tree
was verified clean of tracked modifications after exit.

| Lane | Tokens | Result |
|---|---|---|
| F1 | 331,220 | Protocol-contract design + measurement. 35 divergences on 18 of 32 pages; chain 49 hard violations on 24 of 32; unconditional contract would cost **15 of 19** numeric primaries — but 14 of those pages are one `design_masking` AND/OR class. Plant: finerenone HR→OR, pool and gate unchanged. |
| E | 387,605 | Empty-container sweep: 17 confirmed findings; **12 of 17 need a container other than a pool to empty**; 31 of 768 inventory rows CONFIRMED, 698 UNTESTED. |
| E2b | 221,509 | Adversarial adjudication of E's 17: reproduced 17 of 17, **refuted 1, downgraded 9**; REACHABLE_FRESH_BUILD **7 of 17**, needs stale saved result 5, not reachable 5. Confirms **E-CERTIFIED-FAMILIES**: the real writer emits `{"families": []}`, `gate.py:1354`'s truthiness guard disables the certified-vs-page comparison, and the full gate PASSES a page its non-empty control refuses — a bypass inside the landed gate. |
| B53 | 205,046 | The 53 P5 set-asides: 48 of 53 INFERRED bindable from held documents; 238 of 238 spans located (verified independently). |
| B53X | 252,187 | Adversarial re-read of B53: **36 of 53** strictly (48→36); 11 → PARTIAL, 1 → CONTRADICTED (JUPITER age subgroup read as entry population); probiotics config lists the *outcome* as the entry population (11 of 11 rows); emptied pools at k≥2 **5 of 11**, not 7. Contrast-algorithm failure on 5 rows is a **rule defect**, not an evidence gap. |
| F2 | 248,184 | Compatibility cleared by relabelling: 35 pre-fix records on 17 of 32 pages → 0 post-fix; 10 of 35 INHERITED (analysis population supplied by the config it is checked against); hard-sourced branch would refuse **18 of 19** primaries. Found F2-V007 and F2-V019 — the two wrong-span positives. |
| F5 | 184,449 | Screener disagreement: 5 of 3,146 rows disagree, **0 of 5 pooled**; **216 of 269** included rows have no adjudicator judgment (absence never counted as agreement). |
| PH | 225,865 | Registry phase-scope: class observed on **6 of 634** design-held families (3 treatment/follow-up, 3 RECOVERY epoch), **0 of 39** pooled rows; 1,664 of 2,298 families have no design row and are unassessable. My own 7-candidate nomination was 1 of 7 precise. |
| DB | 196,802 | Placebo-as-blinding, full evidence + pre-fix plant (synthetic open-label record with "placebo run-in" is INCLUDED; the "lead-in period" control is excluded). Corrected four of my figures. |
| U5 | 209,806 | The five unproven admissions against public sources: **4 OBTAINABLE_FETCHED, 1 CONTRADICTED (Zhao)**, 0 unprovable. Overturned DB on melatonin via a held full text DB had not read. |
| Z25 | 226,453 | The other 25 against public sources, positive control on Zhao run and recorded first: **25 of 25 confirmed**; "1 of 26 contradicted" survives; independent review table readable for 23 of 25. |
| WS | 258,261 | Wrong-span prevalence, both controls fired on every method version: **12 of 46** served rows affected; 143,161 occurrences → 137,123 contexts inventoried; J-EMPHASIS-HF found. |
| E2 | 335,080 | Superseded by E2b (died at a vendor "model at capacity" error after reproducing 17 of 17, before any reachability work). Kept for signal only. |

## Decisions these findings put to Mahmood (nothing here builds them)

1. The 41 OPEN result-change notices and the 11 emptied primary pools — the two causes of the publication gate refusing 24 of 32 pages.
2. Analysis set: HARD sourced dimension (18 of 19 primaries refuse until 27 of 33 trials have a full text fetched) or declared assumption (nothing moves, 14 of 97 outcomes gain a disclosure). Lane AS is costing this.
3. Evidence rank for a hand eligibility route: abstract text at registry rank carries 28–32 of B53X's 36 retained rows.
4. The probiotics entry-population rule (config names the outcome, not the entry condition) — a rule repair, not an evidence question.
5. Zhao: remove from the eligible denominator with the public evidence cited.
6. The certified-families gate bypass, the comparator conflict, the phase-scope resolver, the contrast-algorithm fix — each its own landing.
