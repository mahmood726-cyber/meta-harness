# Expansion build queue — verified ingredients per topic

Working notes for the preregistered expansion tier (`PREREGISTRATION_v2.md`). Each topic's trial
identifiers and primary-outcome numbers are **verified against source (PubMed E-utilities / CT.gov)
before any config is authored** — the standing typed-identifier rule (a PMID/NCT is a typed field,
verified, never recalled). Recorded here so the verification survives and lanes are handed real
identifiers rather than inventing them.

Discipline reminders that fired while compiling this queue:
- **Recall is not a source.** A recalled "SWIFT PRIME" PMID (26061835) resolved to a Swedish
  out-of-hospital-CPR study, not the thrombectomy trial — caught only by verifying against PubMed.
- **A clean binary primary is not enough — the comparator must exist too.** A topic needs a
  scope-matched *open-access* comparator meta to benchmark against; that is a real gate (see DOAC-VTE).
- **Estimand identity is part of "verified."** Where trials report different composites or effect
  measures (HR vs RR, ± related deaths), that heterogeneity must be disclosed, not hidden.

---

## doac-vte-recurrence  (PREREG #5)  — trials VERIFIED; comparator OPEN
**Question.** In adults with acute symptomatic VTE, do DOACs vs warfarin/VKA change recurrent VTE?
**Estimand.** Recurrent (symptomatic, objectively confirmed) VTE; trial-reported ratio, pooled on the
log scale. **Effect-measure heterogeneity to disclose:** 5 trials report HR, AMPLIFY reports RR
(RR≈HR at ~2–3% event rates). **Composite heterogeneity to disclose:** RE-COVER/RE-COVER II and
AMPLIFY include VTE-related death in the primary; EINSTEIN/Hokusai count recurrent VTE.

Verified pivotal trials (PubMed):

| Trial | PMID | NCT | Drug | Recurrent VTE (DOAC vs VKA) | Reported effect |
|---|---|---|---|---|---|
| RE-COVER | 19966341 | NCT00291330 | dabigatran | 30/1274 vs 27/1265 | HR 1.10 (0.65–1.84) |
| RE-COVER II | 24344086 | NCT00680186 | dabigatran | 30/1279 vs 28/1289 | HR 1.08 (0.64–1.80) |
| EINSTEIN-DVT | 21128814 | NCT00440193 | rivaroxaban | 36/1731 vs 51/1718 | HR 0.68 (0.44–1.04) |
| EINSTEIN-PE | 22449293 | NCT00439777 | rivaroxaban | 50/2419 vs 44/2413 | HR 1.12 (0.75–1.68) |
| AMPLIFY | 23808982 | NCT00643201 | apixaban | 59/2609 vs 71/2635 | RR 0.84 (0.60–1.18) |
| Hokusai-VTE | 23991658 | NCT00986154 | edoxaban | 130 vs 146 (3.2% vs 3.5%) | HR 0.89 (0.70–1.13) |

**Exclude within EINSTEIN-DVT publication:** its continued-treatment sub-study is rivaroxaban vs
**placebo** (8/602 vs 42/594) — wrong comparator, must not enter the DOAC-vs-VKA pool.

**Comparator status — OPEN (gate).** Free-full-text DOAC-VTE metas found so far are specialized
populations, not scope-matched all-comers:
- cancer-associated: PMID 30897142 (PLoS One, OA)
- thrombophilia: PMID 30690830 (JTH) — reports a *non-thrombophilia* subgroup RR 1.02 (0.80–1.30)
- Japanese subgroup: PMID 27502316
- extended/secondary prevention (vs placebo/aspirin): PMID 30933993 (PLoS One, OA) — wrong scope
The canonical all-comers acute-treatment meta (van der Hulle 2014, JTH) needs OA confirmation.
**Do not ship without a legitimate scope-matched OA comparator** (every live topic has one).

---

## thrombectomy-acute-stroke-outcome  (PREREG #7) — trials VERIFIED; ESTIMAND CAUTION
HERMES set. Primary is the **ordinal-shift common OR** over the mRS distribution, NOT a clean binary
RR of functional independence — pooling mRS 0–2 as a binary RR is a *different estimand* than the
trials' headline cOR. Handle as an estimand-identity decision, not a default binary pool.

Verified pivotal trials (PubMed): MR CLEAN 25517348 (ISRCTN10888758/NTR1804 — no NCT),
ESCAPE 25671798 (NCT01778335), EXTEND-IA 25671797 (NCT01492725), REVASCAT 25882510 (NCT01692379),
SWIFT PRIME — **PMID to be re-verified** (recalled value was wrong). HERMES IPD metas:
Goyal 2016 Lancet (26898852) and Saver 2016 JAMA time-to-treatment (27673305).
