# Search-rebuild handover — open this cold, build nothing until you've read it

## STATUS (updated 2026-09-14) — engine built + measured, pipeline integration NOT yet done
- **Vocabulary layer DONE** (`harness/lexicon.py`, the one shared fold for all consumers): British↔American
  spelling fold, Greek-letter fold (ω-3→omega-3), mortality↔death, a match-time NESTING GUARD
  (bare 'mortality'/'death'/'stroke' won't bind a qualified subtype), and PREVENTION_TRIAL_TITLE_OMITS_OUTCOME
  screening (population from structured fields/abstract for prevention topics). Each shipped with a
  corpus-wide before/after and a plant. **Abbreviations (CV↔cardiovascular, MI↔MI, HF↔…) are BUILT but
  HELD OUT of extraction** — wiring them moved colchicine-postop-af 0.67→0.77 via an 'af' mis-bind
  (END-AF's 63-patient total bound as an arm), the ELIXA class. `lexicon.abbrev_variants` is available
  for query-building (recall net, no number bound); re-enable in extraction only behind a per-abbrev before/after.
- **Concept-query engine BUILT + MEASURED**: `scripts/search_rebuild.py` builds from registered
  P/I/C/design, expands drug classes to members, paginates the full boolean set (no top-N). **Unaided
  recall 6 of 6 vs the 0/6 baseline** (rendered on the index, `docs/search_recall.json`).
- **STILL TO DO (the delicate corpus-moving step — do it behind a full 32-topic before/after):**
  (1) wire the concept query into the pipeline FETCH replacing the enumerated `<uid>[uid]` lists, and
  source-verify EVERY newly-retrieved trial before it pools (representativeness, not just per-number);
  (2) reference-list seeding re-enabled and its added recall MEASURED; (3) WHO ICTRP + international
  registries adapters; (4) search-completeness as its own gated stage that cannot go green on adapter
  exit codes. The engine and the metric exist; the corpus has NOT been re-fetched.

---


This is one of the **two HELD items** (the other is the broad screening-vocabulary fix). It is
held on purpose: it moves the whole corpus, so it needs a fresh budget and a careful corpus-wide
before/after — not a deadline rush. The ELIXA regression (a one-line hyphen change silently pooled
a 4-point composite as 3-point MACE) is the standing proof that a matching/retrieval change must be
measured, never trusted. **Do not start until you can run a full 32-topic before/after.**

## The one-line trap that governs everything
**A better query pointed at the wrong eligibility universe is still the wrong universe.** Retrieval
quality and scope correctness are independent. The current failure is NOT that queries are weak; it
is that the search was run by enumeration / errored out (RAN_ERROR), so nothing was retrieved to
judge. Fixing retrieval without re-checking scope just produces confident wrong inclusions.

## The metric and the honest baseline (already banked — do not recompute loosely)
- **Test set:** `docs/search_test_set.json` — 27 trials, each `{topic, trial, mechanism,
  reason_missed, verification_state}`. **The test set itself contains errors** (DIAMOND was on it
  but is out-of-scope; REMAP-CAP was mis-filed; Udelson, ZODIAC). That is why:
- **`verification_state` is mandatory per entry.** Current distribution: 16 UNVERIFIED,
  6 SOURCE_VERIFIED_ELIGIBLE, 3 SOURCE_VERIFIED_INELIGIBLE, 2 SOURCE_VERIFIED_ELIGIBLE_SCOPE_PENDING.
- **Headline metric:** `unaided_recall = (test-set trials the rebuilt search retrieves WITHOUT being
  told the PMID) / denominator`, computed **ONLY against the 6 SOURCE_VERIFIED_ELIGIBLE** entries
  (PHILO, J-EMPHASIS-HF, CLEAR SYNERGY/OASIS-9, TECOS 3-point-MACE-from-primary, omarigliptin CV
  trial, SOUL). Measuring against the unverified list reproduces the failure we document.
- **Baseline unaided recall = 0 of 6.** Every source-verified-eligible entry is a CONFIRMED MISS of
  the current search. This is the zero from which improvement is measured. Keep correcting the test
  set as verification lands, and recompute the denominator from `verification_state`, never by hand.

## The rebuild spec (what the search must become)
1. **Concept queries derived from the registered P/I/C/design ONLY** — not from the trials you hope
   to find. Build the query from the topic's protocol (population, intervention, comparator, design),
   so discovery is unaided. (Validated earlier: concept queries found PHILO and J-EMPHASIS unaided.)
2. **Generic class-term expansion** — expand intervention/comparator to drug-class and mechanism
   synonyms (the SGLT2/GLP-1/MRA class terms), not just the named molecule.
3. **Reference-list seeding RE-ENABLED and MEASURED** — snowball from included trials' reference
   lists, but treat every seeded hit as a candidate to screen, and measure how many eligible trials
   seeding adds over concept queries alone. Do not let seeding silently widen scope.
4. **WHO ICTRP + international registries** — CT.gov alone misses non-US/older trials (22 of 101
   pooled trials have no NCT at all; see `docs/participant_flow.json`). Query ICTRP, EU-CTR, ISRCTN,
   jRCT, etc. Adapters exist for ISRCTN/PACTR ([[isrctn-pactr-adapters-verdict]] in memory).
5. **Pagination or structured-field queries — NEVER top-N relevance.** A relevance-ranked top-N
   silently truncates the population (the denominator trap). Enumerate the full result set via
   pagination or structured field filters, and report `n_retrieved / n_expected` with any cap named.

## Non-negotiable gates for the rebuild (all must be able to FAIL)
- The rebuild is a machinery change → **all 32 pages must reproduce byte-for-byte** after it, and any
  moved estimate gets an explicit before/after. A new inclusion is a corpus change, not a free win.
- **Every newly-retrieved trial is source-verified before integration** (audit/relevance is a
  hypothesis; source-verified + landed is a result). See [[recovery-must-be-representative]]: a
  conclusion-changing set of additions must be checked for representativeness, not just per-number.
- **A gate you add must be able to pass on today's correct corpus** ([[gate-must-be-able-to-pass]]).

## Files
- Test set: `docs/search_test_set.json` (metric, denominator, verification_state per entry).
- Recovery scoreboard / provenance rules: `docs/recovery_log.json`.
- No `harness/search*.py` exists yet — this is greenfield. Build it behind the same gate discipline
  as every other module (regression test with a plant, then wire, then reproduce-all).

## Why held (say this to yourself before you touch it)
Both held items move the corpus and the measurements are already banked. They were held to protect a
careful before/after, not out of fatigue. If you cannot run the full 32-topic before/after this
session, keep them held and say so — that refusal is the reason the rest is trustworthy.
