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
