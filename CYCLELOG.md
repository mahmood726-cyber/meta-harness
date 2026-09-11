# Improvement-loop cycle log

Format: cycle n · deficit targeted · fix (general?) · k delta · regressions · cost/outcome.
Rule: a cycle that moves no measured deficit is a FAILED cycle, recorded as such. No check loosened.
Every added trial verified true against source before it pools.

## Cycle 1 — MEASURE: build the deficit table + probe the AACT extraction lever
- BUILT scripts/deficit.py (reusable MEASURE): per topic our_k vs same-scope comparator k; each
  declared-absent PRIMARY trial classified AACT_COUNT_AVAILABLE / AACT_RATE_OR_COMPOSITE /
  NO_OUTCOME_ROW / NO_NCT_RESULTS by probing AACT outcome_measurements directly (identity-gated by
  embedding, recurrent-event guarded). Writes docs/deficit.json.
- RESULT: across ALL declared-absent primary trials — 126 NO_NCT_RESULTS, 21 NO_OUTCOME_ROW,
  3 AACT_RATE_OR_COMPOSITE, **0 AACT_COUNT_AVAILABLE**. Validated not a false zero: classifier
  correctly caught HEART-FID (recurrent, score 0.796) and AFFIRM-AHF (composite); embedding works
  offline (real non-zero scores); IRONMAN/FERRIC genuinely have 0 AACT outcome rows.
- FINDING: the AACT outcome_measurements extraction lever (the named "dominant path") is EXHAUSTED —
  no declared-absent trial has a clean, identity-matched, non-recurrent participant count we are
  failing to pool. The k gaps are NOT a parser problem. They are (a) reach/unpublished/ongoing
  (126 NO_NCT_RESULTS) and (b) the field's wall (recurrent/composite/rate-only).
- k delta: 0 (this is a MEASURE cycle; it redirects the loop away from AACT-parsing toward reach +
  OA full-text, and rules out a whole class of wasted cycles). Not a failed cycle — it is the
  measurement that tells us which levers are dead. cost: ~1 deficit scan.

## Cycle 2 — PICK: OA full-text extraction lever (candidate) → tested, EXHAUSTED
- Found fulltext_by_pmid empty for all gap topics (fetch gates it behind config.fulltext + first-40).
- Tested empirically on omega3 (15 declared-absent, several large OA CVD trials): fetched PMC full
  text (19k-40k chars) and ran the EXISTING guarded extractor on each. Result: 0 clean poolable
  counts — the factorial-design guard correctly refuses VITAL/ASCEND-type trials; the rest report
  no percentage-corroborated MACE arm count in extractable form; several non-OA/NCT-only.
- FINDING: full-text extraction adds 0 poolable trials for omega3. Combined with cycle 1 (AACT 0),
  both machine-reachable extraction levers are EXHAUSTED for the in-hand declared-absent trials.
- k delta: 0. FAILED cycle for k, but a decisive MEASURE: rules out full-text as a k lever and
  confirms the same-scope gaps are the field's wall (composite/recurrent/factorial/paywalled), not
  a parser gap. cost: ~10 PMC fetches.

## Cycle 3 — PICK: build the 9 unbuilt topics (k/breadth) → 0 publishable, 1 gate GAP found
- Built all 9 unbuilt topics (all cached, offline). Gate: 4 PASS, 5 REFUSE (k=0, correct declines:
  azithromycin-copd, corticosteroids-cap, metformin-pcos, sacubitril-valsartan, zinc-cold).
- VERIFIED the 4 gate-pass against source — 3 pool WRONG numbers the gate did NOT catch:
  * antibiotics-appendicitis: primary "treatment failure/complication at 1 YEAR" but pooled ctgov
    "Resolution of Appendicitis Symptoms at 30 DAYS" 462/676 — wrong endpoint AND wrong direction
    (resolution=success, not failure).
  * vitamin-d-ARI: primary "at least one ARI" but pooled abstract "Influenza A occurred in 18 of
    167" — wrong endpoint.
  * prone-ARDS-mortality: pooled a 90-day HR (0.44) + a 28-day RR (0.97) + ICU-mortality counts as
    one RR — mixed timepoints AND mixed scales.
  * hfnc-reintubation (k=1): VERIFIED CORRECT (72h reintubation OR 1.26 [0.70-2.26], n=492) — but
    incomplete-evidence k=1 (many HFNC reintubation RCTs exist); publish deferred pending full-page
    (harms/screening/RoB) verification, not rushed.
- ALL 9 built dirs REMOVED (declines carry no page); index.html + blind_map.json reverted. Nothing
  wrong committed.
- k delta: 0 publishable. FAILED cycle for k, BUT surfaced a real GATE GAP: wrong-endpoint /
  mixed-estimand pools pass the gate because outcome-identity gating is opt-in per topic. The prior
  sessions caught these MANUALLY (left unbuilt); the harness should refuse them structurally.
  -> motivates cycle 4 (a general outcome-identity + estimand-compatibility guard).

## Cycle 4 — TRANSPARENCY to best-of-any-system, with the countable test (target #4)
- BUILT scripts/transparency_score.py: per topic, counts every numerical claim and whether it carries
  a one-click resolvable source pointer a reader can open (pooled number -> PMID/NCT + verbatim span +
  extractor; declared-absent -> PMID + reason; RoB domain -> the AACT field basis; reproduction ->
  protocol SHA + replay). Writes docs/transparency.json.
- Scorer VALIDATED not-vacuous: first run flagged 69 gaps due to WRONG field paths (rob2.domains[x].basis,
  reproduction.protocol_sha/failures) -> corrected after reading the real structure -> 0 gaps.
- RESULT: **100% coverage, 0 gaps across all 23 topics** — every rendered number is independently
  checkable. Countable ours-vs-comparator: our pages expose ~740 checkable claims (probiotics 168,
  colchicine-secondary 89, omega3 76, tocilizumab 44...) vs comparators exposing only their 1-3
  reported estimates each (single citation, no per-trial pointers; per-trial data not machine-exposed).
- FIX (general, render-only): page.py _transparency_counts + a compact one-line overview section,
  headline-adjacent (estimate still first, per "transparency != volume"). Applies to every topic.
- REGRESS: rebuilt all 23; 23/23 reproduce (review_sha256 unchanged => NO estimate moved), 98 tests,
  gate all PASS. deficit=transparency: moved from unmeasured to a measured, rendered 100%/0-gap score
  and a countable ~740-vs-~35 claim advantage — the one axis we are unambiguously ahead on. SUCCESS.

## Cycle 5 — PICK: hfnc k=1 → real extraction gap found, fix ATTEMPTED, REVERTED (would ship wrong denominators)
- hfnc reintubation has 12 declared-absent, incl. Hernández 2016 JAMA (26975498): "Reintubation
  within 72h... high-flow group (13 patients [4.9%] vs 32 [12.2%])" with arm sizes "264 received
  high-flow... 263 conventional". A clean percentage-corroborated 2x2 the extractor MISSED because
  denom candidates came only from "(n=X)" / "assigned to each", and Hernández states arm sizes as
  prose. GENUINE extraction gap, not the wall.
- FIX attempted (general): _arm_size_candidates() adds denominators from "N received/assigned/
  randomized" and "N <arm-term>", merged into denom_each (corroboration + round-trip gates validate).
  Hernández then extracted EXACTLY: ai=13/264, ci=32/263 (verified true against source). hfnc k 1->2.
- REGRESS caught the problem: 4 topics changed; source-verification found TWO WRONG denominators the
  gate did NOT catch:
  * LoDoCo2 (32865380): source "2762 colchicine and 2760 placebo" — fix paired placebo's 264 with
    2762 (the colchicine arm size). n2=2762 WRONG (true 2760).
  * SELECT (37952131): source "8803 semaglutide and 8801 placebo" — fix used 8803 for the placebo
    AE count. WRONG (true 8801).
  Root cause: when the two arms are near-equal (2762 vs 2760, 8803 vs 8801), percentage-corroboration
  (1.0pp) cannot distinguish them, so the count is paired with the WRONG arm's denominator. (Two other
  changes were correct: RECOVERY counts 621/2022+729/2094 -> OR 0.83, a genuine improvement over the
  mislabeled IRR 0.85; colchicine-postop diarrhoea 134/1608+38/1601, correct because arms differ.)
- ACTION: REVERTED harness/extract.py (a wrong number that gate-passes is THE failure mode; off-by-2
  is still not true against source). 23 reviews restored byte-identical; hfnc removed.
- k delta: 0 (reverted). FAILED cycle for committed k, but high value: found a real recoverable gap
  AND the exact reason the naive fix is unsafe. The CORRECT fix is per-arm denominator IDENTITY
  (pair intervention-count with n_i, comparator-count with n_c, by arm label) so near-equal arms
  can't cross — a larger careful change queued as cycle 6, to be REGRESS-verified per change.

## Cycle 6 — FIX (general): arm-IDENTITY inferred denominators — the SAFE version of cycle 5
- Root cause of cycle 5's off-by-2: the inferred-denominator count path picked "best-corroborating"
  from a flat candidate pool, so with near-equal arms (2762/2760, 8803/8801) a count crossed to the
  wrong arm's size. FIX: pair each count with its OWN arm's size via (a) _arm_ns extended to read
  prose arm sizes WITH arm identity ("264 received high-flow", "2760 to the placebo", bare "263
  conventional"); (b) READING-ORDER pairing (first-mentioned arm's count -> its own size), robust to
  whether the arm label precedes or follows its count; (c) each still must corroborate its own % — a
  wrong per-arm size just fails and the count is declared absent, never mispooled.
- REGRESS (every change verified TRUE against source, per the bar):
  * colchicine-postop POAF 29237033: 5/49 + 7/51 (source: "49 to colchicine and 51 to placebo... 5
    (10.2%)... 7 (13.7%)") — count provenance replaces HR 0.69; est 0.8341->0.8348. VERIFIED.
  * colchicine-postop +diarrhoea 37640035: 134/1608 + 38/1601. VERIFIED (harm k 1->2).
  * colchicine-secondary MACE LoDoCo2 32865380: 187/2762 + 264/2760 (placebo 2760, NOT the 2762 the
    naive fix produced). est 0.7215->0.7312. VERIFIED.
  * colchicine-secondary +GI 34876021: 15/120 + 3/129 (placebo 129, NOT the 3/120 cycle 5 got wrong).
    VERIFIED (harm k None->1).
  * tocilizumab RECOVERY 33933206: 621/2022 + 729/2094 -> OR 0.83 (topic's declared estimand),
    replacing the mislabeled IRR 0.85. VERIFIED (source 31%/35%, counts exact).
  * SELECT AE-discontinuation: correctly ABSENT now (arm sizes not identity-caught) — no wrong 8803.
- GENERALITY: the same fix recovers Hernandez 2016 for hfnc (13/264 + 32/263, verified) — a different
  topic clears unaided. 98 tests pass, 23/23 reproduce, gate all PASS.
- k delta: primary-outcome k unchanged; +2 harm outcomes pooled; 3 trials upgraded to exact count
  provenance; near-equal-arm crossing eliminated. SUCCESS (safe, general, every number verified).

## Cycle 7 — PICK: publish hfnc (now k=2 via cycle 6)? NO — the pool is not credible
- With cycle 6, hfnc reintubation extracts k=2: Hernandez 13/264+32/263 (count-derived RR ~0.40) and
  35849787 OR 1.26. Gate PASSES. BUT the pooled result is RR 0.72 with CI 0.0005-975.6 — a degenerate
  interval: the two trials mix estimands (a 2x2 RR vs an effect-only OR) in opposite directions, and
  HKSJ at k=2 with divergent estimates inflates the CI across ~6 orders of magnitude.
- Each number is verified true against source, but POOLING them yields a meaningless estimate.
  Honest k over an inflated/garbage pool: hfnc NOT published (removed).
- FINDING (candidate guard, not built — would risk the 23): the harness can pool a count-derived RR
  with an effect-only OR (different estimands) and emit a degenerate CI at small k. A pooled CI
  spanning multiple orders of magnitude, or a count-RR pooled with an effect-OR, should be flagged.
  Deferred as a careful future cycle (needs per-topic REGRESS to confirm none of the 23 rely on such
  a mix — spironolactone already pools mixed RR/HR by design with a visible caveat).
- k delta: 0 published. Correct refusal, not a failure of extraction — the extraction (cycle 6) is
  sound; the POOL of these two specific trials is not a credible meta-analysis.

## Cycle 8 — TRANSPARENCY added to the PRISMA/AMSTAR-2 domain comparison (target #4, as requested)
- prisma_compare.py now emits a per-topic "transparency" dimension (ours_checkable / coverage /
  comparator_checkable) from docs/transparency.json; merged into docs/prisma_compare.json for all 23
  without re-fetching (comparator OA flags preserved).
- RESULT: the "are we better" scorecard now carries the countable transparency axis — **ours 749
  independently-checkable claims vs comparators 35; coverage 100% on every topic**. This is the axis
  we are unambiguously ahead on, now part of the domain comparison rather than a standalone.
- Render: the compact transparency line already sits headline-adjacent on every overview (cycle 4);
  not duplicated into the reporting tab (transparency != volume).
- No page bytes changed (artifact-only); 98 tests unaffected. deficit=transparency-integration moved
  from "standalone score" to "in the domain scorecard". SUCCESS.

## Cycle 9 — TEST: does the cycle-6 fix unlock any k=0 decline? NO (declines confirmed genuine)
- Rebuilt the 5 k=0 gate-refused topics (azithromycin-copd, corticosteroids-cap, metformin-pcos,
  sacubitril-valsartan, zinc-cold) with the cycle-6 arm-identity extractor. All 5 still primary-k=0,
  gate refuses. Their declines are NOT the denominator gap — genuinely no extractable primary-outcome
  binomial (composite primary / wrong-endpoint / no percentage-corroborated counts).
- Dirs removed (declines carry no page). k delta: 0. FAILED cycle for k, but it CONFIRMS the 5
  declines are real data-absence, not an extraction bug the general fix could reach — closing them as
  verified declines rather than leaving them as suspected extraction gaps.

## Cycle 10 — TRANSPARENCY: four-state source status rendered (target #4: "which adapters ran")
- Added pipeline._source_status: RAN_OK / RAN_ZERO / RAN_ERROR / NOT_RUN per source (PubMed, Europe
  PMC, ClinicalTrials.gov, Citation chase, Registry-first AACT, PMC full text), preferring the status
  fetch recorded and filling the rest DETERMINISTICALLY from committed artifacts (recall.json,
  fulltext_by_pmid, ctgov presence) — replay-safe, process-metadata only. Rendered compactly on the
  Search tab so process coverage is visible, not assumed.
- The deterministic-render census check CAUGHT a dict-order non-determinism in my first render
  (items() insertion order vs canonical_json sorted keys — the exact RoB2 bug class); fixed with
  sorted() iteration. That check earning its keep on a real bug is why the limb exists.
- REGRESS: 0 outcome estimates moved (process-metadata only); 98 tests, 23/23 reproduce, gate PASS.
  deficit=transparency: "which adapters ran" moved from invisible to a rendered four-state panel on
  every page. SUCCESS.

## Cycle 11 — WEAKNESS SURVEY as a harness artefact + BACKWARD-VERIFICATION of all 23 live topics
- BUILT scripts/weakness_survey.py -> docs/weakness_survey.json (committed) + docs/weakness_survey.html
  (rendered report: each weakness = measurement, value, target, status). Regenerable from the review
  objects; measured, not recalled.
- ⭐ BACKWARD-VERIFICATION (dimension 3, the centrepiece): every pooled trial-outcome number re-checked
  that its digits are present in the COMMITTED source (full abstract / ctgov structured / hand-verified
  cross-check). RESULT after validating the checker: **84 pooled pairs -> 83 verified_span + 1
  verified_handchecked + 0 UNVERIFIED**. The live set's numbers all trace to source.
- The checker itself was validated THREE times before trusting it (the "verify against the bytes you
  showed" lesson): first flagged 24 (artifact: checked the truncated 200-char display span, not the
  full abstract — the arm-identity fix legitimately pairs a count from one sentence with a denominator
  from another); then 8 (artifact: middle-dot Lancet decimals 0.88 vs 0.88, and RRR->RR conversion
  0.56->0.44); fixed both -> 0 genuine unverified. A scary number from an unvalidated instrument is
  not a finding.
- OUTCOME-IDENTITY on the 4 ctgov_results pairs (digit-verify does not cover wrong-endpoint): crystalloids
  'In-hospital Mortality' ✓, omega3 'Atrial Fibrillation (Omega-3 only)' ✓, ticagrelor 'Any Major
  Bleeding' ✓ — 3 clean; spironolactone flags one BORDERLINE: declared "Hyperkalemia" but ctgov gave
  "Hospitalization Due to Hyperkalemia" (4/1367, EMPHASIS-HF eplerenone) — a narrower endpoint on a
  harm outcome, recorded for review (not an egregious wrong-endpoint like the 3 unbuilt topics).
- 2 PROVENANCE MIX: abstract 79, registry 4, full-text 0, hand-verified 1 of 84. The "95% regex"
  concern re-measured: the number FOUND by the harness is the abstract/registry extractor; hand-verified
  is 1/84 (1.2%) and must reach 0. 8 FRAGILITY: 19/23 topics k<=2 or tau2=0 (small-k dominant, as
  expected). 8b MIXED-SCALE POOLS: 6 (next cycle). 9 TRANSPARENCY: 0 gaps.
- SUCCESS: the survey is a committed, rendered, regenerable artefact and the live set is verified clean.

## Cycle 12 — ESTIMAND HOMOGENEITY: honest mixed-scale label + arm-identity regression tests
- Survey dim 8b found 6 pools mixing ratio scales. VERIFIED each: none egregious — all same-direction,
  close-valued RR/HR mixes (colchicine-secondary 0.71/0.77, noac 0.79-0.91, sglt2-ckd 0.63-0.77,
  spironolactone 0.70/0.76, omega3 ~null, probiotics 1 OR among 12 RR). NOT the opposite-direction
  hfnc case nor a Peto-OR+Cox-HR masquerade. A blanket refuse would wrongly gut 5 primary outcomes.
- The real defect is the LABEL: 5 of 6 were shown as a single clean scale ("HR"/"RR") while mixing —
  the "calling it an HR" lie. FIX (general, label-only): a pooled result whose trials do not share one
  ratio estimand is now labelled "mixed (X/Y)" (e.g. colchicine-secondary "mixed (HR/RR)", omega3
  "mixed (HR/IRR/RR)"), with a scale_mixed flag. Pooling math unchanged.
- REGRESS: rebuilt all 23; **0 estimates moved**; only the 6 mixed pools' SCALE LABELS changed to
  honest. 102 tests, 23/23 reproduce, gate PASS.
- Added tests/test_arm_identity.py (4 permanent cases, per Mahmood): Hernandez 13/264+32/263;
  LoDoCo2 comparator = 2760 NOT 2762 (the off-by-2 anti-regression); factorial trial refused; mixed
  pool labelled "mixed (...)". Locks the quietest failure class (wrong-arm binding).
- SUCCESS: the "calling it an HR when mixed" class is killed corpus-wide (honest label), and the
  arm-identity win is now regression-protected. deficit 8b: mislabeled pools 5 -> 0.

## Cycle 13 — verified_arms.json AUDIT: the hand-verified tier made HARNESS-AUDITABLE
- The ONE hand-verified entry (SMART crystalloids mortality) is the last "reproducible-given-my-
  judgement" number. It sums 30-day in-hospital mortality across SMART's TWO registrations
  (NCT02444988 + NCT02547779); the abstract gives only percentages, and the record's nct field names
  just one registration — so the single-registration AACT path would pool a WRONG partial number.
- BUILT scripts/verify_verified_arms.py: re-derives every verified_arms entry from the committed AACT
  snapshot — per-arm counts aligned by result-group TITLE (intervention vs comparator), summed over
  registrations, with a both-arms IDENTITY GUARD that excludes the co-citing NCT04507672 (a different
  trial). Cross-checks the derived counts against the entry AND the published abstract %.
- The auditor itself was validated (the recurring lesson): first pass MISMATCHED on denominators
  because it aligned arms by MAGNITUDE (balanced is the larger arm in one registration, smaller in the
  other) — fixed to align by result-group title -> AACT_DERIVED_MATCH: 818/7942, 875/7860 == entry ==
  published 10.3%/11.1%. This is also why blind auto-summing is unsafe (arm alignment is non-trivial).
- The entry now records harness_audit; docs/verified_arms_audit.json committed. The hand number is now
  a CHECK on the harness's AACT re-derivation, not a substitute — a stranger with the AACT snapshot
  regenerates the same numbers. 102 tests, reproduces, gate PASS.
- SUCCESS: verified_arms is 1 entry, and it is now harness-auditable/re-derivable rather than typed
  judgement. Fresh-clone still replays the committed cache (AACT is not in-clone); the auditor proves
  the committed number is AACT-derivable.

## Cycle 14 — MEASURE the locate-parse-round-trip model-extractor opportunity → measured wall
- Before a multi-hour Fable locate-parse-round-trip build, MEASURED the recoverable opportunity: 67
  declared-absent PMID trials have >=2 outcome-value tokens the deterministic extractor didn't take.
  But that is a LOOSE upper bound — inspection shows the tokens are overwhelmingly P-values, enrollment
  Ns, design/rationale papers, composite components, different outcomes, or the known paywalled COPPS.
- Tested the most promising (34876021 MACE): "36 MACE ... 8 events colchicine vs 28 events placebo
  ... experiencing the event (P=0.001)", arms 120/129. NOT safely poolable: (a) events-vs-patients
  ambiguous, (b) NON-STANDARD MACE definition ("decompensated HF, ACS, stroke AND survival rate"),
  (c) NO reported effect (HR/RR) to round-trip against — only a P value. Refuse on ambiguity.
- CONCLUSION: the locate-parse-round-trip model is the right ARCHITECTURE (model locates a verbatim
  span + identity, harness parses, round-trip decides, cached+rendered model-derived) but its payoff
  on THIS corpus is ~0 — the candidates lack round-trip anchors / have ambiguous identity, so a model
  would (correctly) refuse them or risk a wrong number. Extraction is now measured-exhausted a THIRD
  way (AACT cycle 1, full-text cycle 2, model-locatable cycle 14). Recorded as a measured wall, not a
  speculative build — a cycle that moves no verified deficit is a failed cycle for k.
- The architecture stays documented as the correct next build for a FUTURE genuine unusual-phrasing
  case WITH a round-trip anchor; it is not built speculatively under an expiring budget.

## Cycle 15 — verified_arms.json → STRUCTURED / HARNESS-DERIVED (front 2; the hand tier shrinks)
- Generalised cycle 13's arm-identity mechanism into harness/aact.py::summed_arms(pmid, interv, comp,
  outcome_terms): discovers a trial's registrations from study_references (own-pub link to the PMID),
  aligns arms by RESULT-GROUP TITLE (intervention vs comparator terms), sums per arm over registrations
  reporting BOTH arms (identity gate excludes co-citing NCTs), refuses recurrent-event titles. Only
  inputs are the committed PMID + topic terms — no NCT list, no typed number.
- scripts/build_aact_arms.py regenerates cache/<slug>/verified_arms.json from the committed
  `aact_arm_trials` spec (pmid + outcome terms = a committed query): summed_arms + abstract-% cross-check
  (round-trip) + recurrent guard; writes an entry ONLY if it reconciles with the published %.
- RESULT: SMART regenerated to the SAME numbers (818/7942, 875/7860) but now HARNESS-GENERATED from
  committed AACT and cross-checked, not typed. **0 estimates moved.** verify_verified_arms audit still
  MATCH; 102 tests; reproduces; gate PASS. The hand-verified tier is now a DERIVED+AUDITED tier — a
  stranger with the AACT snapshot re-runs build_aact_arms.py and regenerates the identical file.
- Also wrote BURN_PLAN.md (rate target + sequence; standards unchanged).
- SUCCESS: the last "reproducible-given-my-judgement" number is now produced by committed code from
  committed AACT via a committed query — committed query -> committed cache -> replay -> gate.

## Cycle 16 — Front 6 CLOSED: valid comparators for the 4 invalidated topics -> none exists (re-judge resolved)
- Searched PubMed for a valid same-scope comparator for tocilizumab (the one of the 4 I had flagged as
  possibly having one). Result: no clean tocilizumab-ONLY COVID-mortality meta exists — the literature
  synthesizes tocilizumab within IL-6/monoclonal-antibody CLASS metas, or reports it only as a SUBGROUP
  (RR ~0.95 placebo-controlled, ~0.90 severe-critical). So even tocilizumab has no like-for-like
  standalone comparator; the 3 single-pivotal-trial drugs never could.
- Updated tocilizumab comparator_scope_note (surgical 1-line edit; no config reformat) to state this.
  JUDGELOG front-6 closure: all 4 -> "no valid same-scope comparator exists"; blind record is 15 clean
  wins + 4 SET ASIDE, not 19-0. The re-judge is resolved by finding there is nothing valid to judge
  against — itself the honest finding.
- k delta: 0 (a documentation/closure cycle, not a k move). Recorded honestly. Rebuilt tocilizumab,
  renders, JSON valid.

## Cycle 17 — Front 8 RoB2 coverage MEASURED into the survey
- Added RoB2 domain coverage (dimension 5) to weakness_survey: across 46 pooled trials, D1
  randomisation 46/46 assessed, D5 selective-reporting (free-from-outcome-switching) 46/46 assessed
  (29 low, 17 some-concerns = the outcome-switching flags); D2/D4 blinding 39/46 (7 missing AACT
  masking fields); D3 missing-outcome-data 0/46 (correctly "not assessed — needs human judgement").
- The two machine-checkable domains most published metas omit — D1 and especially D5 — are at FULL
  coverage; the gaps (D2/D4) are honest metadata-absence, and D3 is honestly not-automated.
- Survey json + html regenerated. 102 tests. No page bytes / estimates changed (artefact-only).
- SUCCESS: front 8 now measured and rendered in the survey, not asserted.

## Cycle 18 — Front 9 + new-topic candidate: preregistration discipline HELD (not padded)
- Front 9 (the preregistered unbuilt topics) is complete: 9 unbuilt configs, all attempted (cycle 3) —
  5 correct k=0 gate-declines, 3 wrong-endpoint (removed), 1 not-credible pool (hfnc). Recorded.
- Evaluated a NEW topic candidate (bempedoic acid MACE, CLEAR Outcomes / Nissen 2023 NEJM): data is
  clean and verifiable (bempedoic 819/6992 [11.7%] vs placebo 927/6978 [13.3%], HR 0.87). But it is
  NOT in the 30-topic preregistration, and it is a k=1 single-pivotal-trial topic that would need a
  class-level comparator (a 5th scope-mismatch). Adding ad-hoc topics to raise the count would VIOLATE
  the preregistration discipline that is part of the harness's integrity, and would be padding, not a
  deficit-move. NOT added — the straight path is to hold the preregistered set, not inflate it.
- k delta: 0. Recorded as a principled decline, not dressed up. (Source: PubMed, CLEAR Outcomes,
  DOI 10.1056/NEJMoa2215024.)

## Cycle 19 — Item 2 (HIGHEST PRIORITY): `verified` is now a RENDERED per-trial field
- New harness/verify.py (single source of truth): verify_pooled(trial, abstract) checks each pooled
  number's digits are present in the COMMITTED source (full abstract for abstract/full-text; ctgov
  structured source string; AACT-derived cross-check for aact_verified). Middle-dot decimals + RRR->RR
  complement handled (the checker-artifacts learned in cycle 11).
- pipeline._build_outcome computes t["verified"] + t["verify_basis"] for every pooled trial at build.
  page.py renders a per-trial badge: "verified against source" / "verified (AACT-derived)" / "NOT YET
  verified". Status is now VISIBLE, not assumed.
- RESULT across all 23: 83 verified + 1 verified_handchecked, **0 not-yet** — matches the survey's
  independent backward-verification (two implementations agree = cross-check). 102 tests, 23/23
  reproduce, gate PASS.
- SUCCESS: item 2 done. The single highest-priority flaw (unverified-as-assumed) is closed —
  verified/not-yet is a rendered per-trial state a reader can see.

## Cycle 20 — Item 1: replay-vs-repeatability DISCLOSURE + RE-SEARCH MODE
- (a) DISCLOSURE on every Reproducibility tab: states plainly that the reproduction claim covers
  DETERMINISTIC REPLAY (re-run from SHA on a fresh clone -> byte-identical page) and does NOT claim
  independent REPEATABILITY (a fresh search today returning the same trial set) — databases drift; the
  committed queries are printed verbatim to re-run; re-search mode measures the drift. The honest form
  of "living, not frozen": the analysis is frozen and auditable, the literature is not.
- (b) RE-SEARCH MODE: scripts/research_diff.py re-runs a topic's COMMITTED PubMed/EPMC/CT.gov queries
  LIVE and diffs the retrieved id set vs the committed cache; writes cache/<slug>/research_diff.json,
  rendered on the Reproducibility tab. Demonstrated: pcsk9-mace 4 live vs 6 committed (2 no longer
  returned); colchicine-recurrent-pericarditis 122 live vs 50 committed (72 NEW) — real literature
  drift, now MEASURED not assumed. (New records are the literature moving, not a defect; whether any
  are poolable RCTs is a separate screen.)
- REPRODUCTION-SAFE: research_diff lives in the reproduction block (outside the core hash) and BOTH
  build (census) and replay (reproduce_review) load the same committed research_diff.json, so the
  page byte-matches on replay. Fixed reproduce_review to load it (caught a byte-mismatch first).
- 102 tests, 23/23 reproduce, gate PASS. SUCCESS: item 1 converted from limitation to measurement +
  explicit disclosure.

## Cycle 21 — Items 7,8,9,10 DISCLOSED (disclosure is the differentiator; no comparator does it)
- Per-page Stated limitations extended: (8) registry snapshot is dated — trials/results after the AACT
  snapshot are invisible to recall/ghost/RoB2; re-search mode measures the drift. (7) dual screening
  not fully independent (shared author; model adjudicator on disagreements). (10) the blind comparison
  is judged by an AI and transparency is what we optimise for — partly circular; the PRISMA/AMSTAR-2
  instrument comparison is the cross-check, and auditability is the axis we claim, not superior evidence.
- INDEX (item 9): a "Selection effect (stated, not hidden)" banner — built N of M preregistered topics;
  the unbuilt were disproportionately the HARD cases (continuous/recurrent/composite/paywalled/
  unregistered) which the harness correctly declined, so the build success rate flatters us; the set is
  preregistered and declines recorded, so the selection is visible not silent.
- Rebuilt all 23 + index; 102 tests, 23/23 reproduce, gate PASS. Limitations text is render-only (no
  estimate/core-sha change). All queue items 3,6,7,8,9,10 are now disclosed on the pages/index.
- SUCCESS: every disclosed-limitation item is now actually rendered — the differentiator no published
  comparator offers.

## Cycle 22 — Item 5 (model extractor) RE-EXAMINED with evidence → wall confirmed a 4th way
- Tested (not asserted) the claim "declared-absent trials have no round-trip anchor": REFUTED — 11 of
  392 declared-absent PMID trials DO carry a reported effect (RR/OR/HR+CI) an anchor could use.
- Examined them: ALL are correctly declined by EXISTING deterministic guards, so a locate-parse-
  round-trip model would reach the same refusal and recover 0 verified new trials:
  * 34446156 (colchicine-secondary MACE): a LoDoCo2 SUBGROUP effect ("no prior ACS", HR 0.81) — subgroup
    guard correctly refuses (not the trial's overall poolable effect).
  * 36347265 (IRONMAN, iv-iron): COMPOSITE/recurrent-event rate ratio — composite/recurrent guard refuses.
  * 29237033 / 21873705: FALSE anchors — the POAF HR / recurrence RR mis-attributed to
    "discontinuation"/"disease-related hospitalisation" by keyword overlap; wrong-outcome, correctly absent.
- CONCLUSION: the model extractor's identity-judgment would classify these exactly as the guards do
  (subgroup / composite / recurrent / wrong-outcome). Its payoff on THIS corpus is ~0 — confirmed a 4th
  independent way (AACT c1, full-text c2, model-locatable c14, anchored-declared-absent c22). The
  architecture stays documented for a FUTURE genuinely-anchored unusual-phrasing case; not built to
  recover 0. k delta 0, recorded as a measured wall (not dressed up).
- ALL 10 flaw-queue items now addressed: 1,2 built; 4 closed; 3,6,7,8,9,10 disclosed; 5 measured wall.
