# Response to the external audits (2026-09-12)

Five independent, human-directed external audits (ChatGPT/other-family, reconstructing from FULL
TEXTS) were run against colchicine-pericarditis, dpp4-mace, glp1-ra-mace, probiotics-aad, and
omega3. **Their unanimous, correct verdict: the statistical engine is right (all five reproduced our
pooled estimates, PM τ², HKSJ, and prediction intervals digit-for-digit); every defect is upstream —
search, screening, extraction, metadata.** As one auditor put it: *"Deterministic reproducibility
gives same-inputs→same-answer; it cannot protect against systematically wrong screening inputs."*

Each claim is verified against source before any change (the audit is another model's reading; same
discipline applies to it as to ours). Status legend: **CONFIRMED** (verified against source, fixed),
**CONFIRMED-OPEN** (verified, fix in progress / larger), **PARTIAL**, **REJECTED** (with reason).

---

## FIXED (verified + shipped, with regression tests)

### C-SCREEN-1 · Token-boundary screening — CONFIRMED, fixed (commit d78d51c)
`screen._has` did bare-substring matching, so the animal population_none term `rat` matched inside
`prepaRATion` / `administRATion` and excluded three human RCTs as animal studies
(probiotics 17604300, 11148433, 21871144). This falsified our claim that every exclusion reason is
true of the record. Fixed: token-boundary matching with an explicit `*` stem convention; configs'
intentional stems updated (`…diarr*`, `cold*`) and the missing `antibiotic-related diarr*` synonym
added (recovers 9570649). Corpus sweep: 12 exclude→include recovered, 4 include→exclude now honest
X3; **no pooled number moved on any topic**. Regression tests in `tests/test_screen_span.py`.

### C-SCREEN-2 · Templated INCLUDE reason — CONFIRMED, fixed (commit 4f70674)
The INCLUDE reason hard-coded `intervention_any[0]` (every DPP-4 inclusion read "RCT of sitagliptin",
including alogliptin/saxagliptin/linagliptin trials) and always claimed "double-blind
placebo-controlled" even for non-blindable interventions (prone positioning). Fixed: reason names the
intervention THIS record matched (EXAMINE→alogliptin, SAVOR→saxagliptin, CARMELINA→linagliptin), the
matched comparator/population, and a design clause reflecting the config. No decision/number change.
Regression tests added.

---

### C-GRADE-1 · Mechanical imprecision — CONFIRMED, fixed (commit 733647a)
Imprecision downgraded whenever the CI crossed the null, so a precise interval around no-effect
(RR 0.91–1.08) was wrongly penalised. Fixed: on a ratio scale, downgrade only when the CI crosses the
null AND reaches an appreciable effect (≤0.75 or ≥1.25); a CI within those bounds is precision about
the absence of an appreciable effect. Verified live (dpp4 imprecision basis now reasons from the
thresholds). Regression test added; the prior test that defended the mechanical rule was rewritten.

### C-ROB-1 · Zero-assessed RoB gave a clean bill — CONFIRMED, fixed (commit 733647a)
With no trial RoB-assessed, the domain returned downgrade=0 basis "no assessed trial at high risk".
Fixed: coverage gates the judgement — no machine-derived RoB signal for ANY pooled trial → downgrade
for unknown study limitations, with honest basis ("risk of bias NOT ASSESSED for any of the N pooled
trials"). Verified live (dpp4 → low, RoB basis correct). 15 certainty ratings changed corpus-wide
(down where RoB unassessed, up where a tight-null CI was wrongly downgraded); no pooled number moved.

### doac-vte-recurrence · shipped as the 32nd live topic (commit 4fc26ad)
Built by a Codex lane in an isolated worktree, rebuilt on main with post-audit-fix code, independently
re-verified (my PubMed extraction of all six trials + a hand-computed IV pool 0.909 + the OA comparator
van Es 2014 0.90). k=6, mixed HR/RR 0.91 (0.75–1.11); EINSTEIN placebo-extension excluded; DANNOAC
declared absent; estimand heterogeneity disclosed. Verified live. Also landed a corpus-safe
multi-registration NCT-selection fix (`fetch._select_nct`) with a regression test.

## CONFIRMED-OPEN (verified against source; fix is larger / in progress)

### C-DEDUP-1 · Companion/design/secondary papers counted as trials — CONFIRMED (verified this cycle)
colchicine-recurrent-pericarditis includes 17885522 ("CORP and CORP-2 trials — two randomized…", a
description paper), 22430920 (a secondary report of CORP), and 17667033 (ICAP) as separate eligible
RCTs. Fix (queued): link companion/design/secondary reports to their parent trial; sweep the corpus.

### C-SEARCH-1 · Search is enumeration, not discovery — CONFIRMED (measurement below)
**10 of 37 topics have PMID-seeded PubMed queries** (the PubMed channel is a pure PMID enumeration,
no term-driven search that could discover an unknown trial):
`dapagliflozin-hfpef-hosp, dpp4-mace-t2d, empagliflozin-hfpef-hosp, glp1-ra-mace-t2d,
noac-vs-warfarin-af-stroke, sglt2-ckd-progression, sglt2-hfref-hosp-cvdeath,
sglt2-primary-prevention-hf, spironolactone-hfref-mortality, ticagrelor-vs-clopidogrel-acs`.
All 10 also carry `registry_first` (AACT cond/intr discovery), so they are not *blind* enumeration —
but the auditor's point stands: a PubMed search of five known PMIDs cannot find a sixth trial, and
**recall measured on such a topic is circular.** Confirmed misses: DPP-4 missed OMNeON (omarigliptin);
GLP-1 missed FLOW (2024) and SOUL (2025). Fix (in progress): rebuild these as genuine
intervention/outcome queries and re-measure recall; re-verify any newly discovered trial against
source before it can enter a pool. This is the `a fetch of a named identifier is not a search` rule,
violated in practice.

### C-EXTRACT-1 · "Declared absent" when full text exists / retrieval not run — CONFIRMED (dpp4 headline)
Verified: dpp4 TECOS declared "outcome absent" for 3-point MACE while the page itself records the PMC
full-text adapter as NOT_RUN — an extraction failure mislabelled as outcome absence. Rule to adopt:
never write "outcome absent" when full-text retrieval was not executed; the honest label is
"not extracted: full-text retrieval not run". Fix (in progress): (1) wording/status split;
(2) full-text fallback mandatory before any absent (esp. harms/secondary); (3) corpus sweep of every
declared-absent row where the full-text adapter did not run. Network-dependent verification of the
specific recovered numbers (TECOS 745/746 HR 0.99; EXAMINE 305/316 HR 0.96 at 98% CI) pending.

### C-STATS-1 · Non-95% CI handling — CONFIRMED-OPEN
EXAMINE reports a 98% CI (0.80–1.16). Add a prespecified rule: for an HR/CI at a confidence level
other than 95%, recover the log-scale SE using the STATED level before pooling.

### C-META-1 · Funding classification from full text — CONFIRMED-OPEN
Where full text was not fetched, funding is under-counted (colchicine CORP: Acarpia unrestricted grant
= industry-tied; dpp4 all 5 industry; probiotics ≥3/13; omega3 STRENGTH AstraZeneca). Re-run funding
on full text corpus-wide.

### C-DEDUP-1 · Companion/design/secondary reports counted as trials — CONFIRMED-OPEN
colchicine: 17885522 (CORP/CORP-2 design paper), 17667033 (ICAP design), 22430920 (CORP secondary,
same 120 patients) counted as separate eligible records. Link companion/design/secondary reports to
their parent trial; sweep the corpus.

### C-COLCH-1 · Protocol/analysis contradiction — CONFIRMED-OPEN (most consequential single page)
Registered PICO is "acute first episode OR recurrent", but Results refuses ICAP for enrolling
first-attack patients — the two cannot both hold. Resolve explicitly: either narrow the protocol
prospectively to recurrent-only (k=2, CORP+CORP-2) or keep the broad PICO and include ICAP's pure
recurrence component (11/120 vs 25/120, per full text — not the 20/120 vs 45/120 composite). k=3 then
gives HKSJ 0.255–0.879 (excludes 1), versus our k=2 0.06–3.62.

---

## REMAINING CLASSES (verified pattern, queued)

- **C-ROB-2** (rename, still to do) Call the machine-derived ratings "machine-derived risk-of-bias
  signals" on the page, not RoB2 (formal RoB2 needs judgements registry fields cannot supply).
- **C-GRADE-2** Publication-bias logic (omega3): the search section calls the 144 registry records an
  inflated upper bound "not a publication-bias claim", then GRADE downgrades on ~that number. Our own
  caveat must bind our own rating.
- **C-STATS-2** HKSJ at k≤2 (t=12.71, 1 df): render the conventional/common-effect CI alongside HKSJ
  as a standing rule; do not present a k=2 HKSJ interval as if the trials conflict when I²=0%.
- **C-CONSIST-1** Cross-section consistency gate: the same fact must not differ between page blocks
  (τ² 0 vs 0.00092; k=13 vs k=15; D3 "not assessed" vs every trial rated).
- **C-COMP-1** Comparator matching on P/I/C/**O** and population-subset (Patoulias never pooled
  3-point MACE; Goodman is adults-only); check every asserted comparator `k` against source (omega3
  "k=8" vs "22 RCTs").
- **C-HARMS-1** Harms declared absent that exist in full text (CORP/CORP-2 hospitalisation etc.;
  REWIND GI 2347/4949 vs 1687/4952; SAVOR HF-hosp HR 1.27; omega3 AF). Same root cause as
  C-EXTRACT-1; re-run harms across all topics after full-text fallback.
- **C-SCI-1** (omega3, a scientific finding we missed) EPA-only vs EPA+DHA: removing REDUCE-IT gives
  0.9855 with τ²=0 — the ~80% I² is *explained* by formulation, not unexplained heterogeneity. Add a
  prespecified EPA-only vs EPA+DHA stratification; make harmonised 3-point MACE the primary with
  broader trial-defined MACE as sensitivity.
- **C-QUEUE-1** Work the "served exclude, model include" disagreement queue (omega3 PISCES 41201837,
  a recurrent-event trial needing separate handling).
- **C-PROTO-1** (probiotics) Remove/register-prospectively the post-hoc "24-hour AAD" definition;
  state the ITT rule as trial-reported ITT/mITT with a sensitivity analysis and apply it uniformly.

## CONFIRMED CORRECT (keep, and say so on the pages)
ELIXA correctly excluded from the strict 3-point pool; CORP survival-derived rates correctly not
turned into 2×2 counts; CORP-2 "0.49" correctly handled as a relative-risk *reduction* (flag this on
the page). And: **adding the missing trials never overturned a conclusion** — GLP-1 stays ~0.85,
DPP-4 neutral, probiotics ~0.63, omega3 ~0.94. Effects are right; evidence bases and metadata are not.
