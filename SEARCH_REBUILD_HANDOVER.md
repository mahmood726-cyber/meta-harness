# Search-rebuild handover — open this cold, build nothing until you've read it

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
