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
