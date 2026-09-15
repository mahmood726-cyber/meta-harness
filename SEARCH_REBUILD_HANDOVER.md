# Search-rebuild handover — open this cold, build nothing until you've read it

## STATUS (updated 2026-09-15, run r2 landed) -- the four owed items, each with its state and its number

Everything below is MEASURED unless marked; the numbers live in `docs/evidence/search-v2-measurement-2026-09-15`
(run 1 = lane S3, captures 01-05; run r2 = captures 06-12) and `docs/evidence/search-v2-guard-2026-09-15`.

- **(1) Concept query wired into FETCH -- DONE as a shadow corpus, NOT as the served pool.** `harness/search_v2.py`
  builds P/I/C concept queries (PubMed, Europe PMC, CT.gov; Cochrane RCT filter; full pagination), cross-links
  NCT<->PMID, chases citations, and writes dated snapshot generations beside the pinned caches
  (`cache/<slug>/snapshots/2026-09-15r2-search_v2`, all 32 topics, one engine blob 9cf898d0, raw bodies on GitHub
  release `raw-archive-2026-09-15r2-search_v2` with the tar sha256 in each ARCHIVE.json). `search_v2.pin()` is the
  one call that would move a served pool onto it and it has NOT been called: the 32-topic before/after
  (`11-before-after-32-r2.txt`) reads records 1873 -> 116484 and automated screen includes 189 -> 2140 on the 21
  MEASUREMENT topics (1270 -> 53389 and 129 -> 1273 on the 11 DEVELOPMENT topics); every one of those ~2000 extra
  includes would need source verification before it pools. That decision is Mahmood's, with the numbers in front of him.
  On the sealed benchmark: run 1 pooled-or-declared 120 of 135 with 5 of 21 topics RAN_ERROR; run r2 135 of 135 with
  21 of 21 topics run (all RAN_OK_WITH_SOURCE_ERRORS, see (2)); audit-found 1 of 12 in both runs -- 11 of the 12 are
  NAME_ONLY (author surname / acronym, no identifier) which the title scorer cannot match for any engine, a limit of
  the benchmark, stated in `07-recall-21-r2.txt`.
  The 5 RAN_ERROR topics were the engine's own name-seeding guard refusing registered vocabulary (CABG, BAY94-8862,
  PCSK9, LCZ696, NSTE-ACS); fixed by a RETROSPECTIVE protocol (sealed-vocabulary exemption by provenance, 8 of 8
  plants fired pre-fix and still fire), not by growing the allowlist.
- **(2) Reference-list seeding -- RE-ENABLED and MEASURED: 0 of 136 unique.** Both backward-citation adapters ran on
  every topic. Europe PMC `/references` answered 503 "temporarily unavailable due to maintenance" on every call of
  both runs (265 of 299 run-1 source errors; 163 of 837 run-r2 sources), so a PubMed elink `pubmed_pubmed_refs`
  adapter was added beside it (`PUBMED_ELINK_BACKWARD_CITATION`, `COMPARATOR_REFERENCE_LIST_PUBMED`). Its added recall
  on the sealed benchmark is 0 of 136 positives found only by that route (`08-routes-r2.txt`): every positive it
  reached, the concept queries also reached. It adds candidates outside the benchmark (`10-reverse-direction-r2.txt`).
- **(3) International registries -- ISRCTN DONE and MEASURED (Codex lanes R2 + R4); WHO ICTRP still NOT DONE.**
  `harness/search_v2.py` gained an ISRCTN adapter (`ISRCTN_CONDITION_INTERVENTION`, XML query API, grammar verified
  against the API, behind `refresh_topic(registries=...)`); engine v3 = r2 + ISRCTN was run on all 32 topics as run r3
  (`cache/<slug>/snapshots/2026-09-15r3-search_v2`, engine blob a57dc45d, raw bodies on release
  `raw-archive-2026-09-15r3-search_v2`, 32 of 32 verified by size and re-hash). ISRCTN source RAN_OK on 25 of 32
  topics, RAN_ZERO on 7, 900 registry records in total, benchmark positives unchanged 136 of 147 (r2 136 of 147): a
  registry adds registrations, not the publications the benchmark is made of. Register on search_v2 (r3): whole engine
  20 of 20; within kind 15 of 16 over 4 of 5 topics -- the statins PubMed concept source was RAN_ERROR in r3 (truncated
  efetch XML) and stays RAN_ERROR, not scored. WHO ICTRP has no API (`12-international-registries-probe.txt`); not done.
- **(4) Search completeness as its own gated stage -- DONE.** `harness/search_completeness.py` +
  `scripts/verify_all.py:limb_search_completeness` (GAP-054, scorecard entry): refuses unless the registered
  search_v2 measurement (`registry/search_completeness.json`) is current for the engine blob, every MEASUREMENT topic
  and every source carries an explicit state (RAN_OK / RAN_OK_WITH_SOURCE_ERRORS / RAN_ZERO / RAN_ERROR / NOT_RUN,
  counted separately), a RAN_OK source has records, and the register and README name the same engine. It cannot go
  green on an exit code: 9 plants in `tests/test_search_completeness.py`.
- **Sealed register, compared within kind:** LEGACY engine 18 of 20; search_v2 PubMed concept-query source alone
  19 of 20; search_v2 whole engine 20 of 20 (`09-register-search-v2-r2.txt`, `docs/search_recall_regression_corpus_search_v2.json`).
- **Vocabulary layer** as before (DONE; abbreviations still held out of extraction).

## STATUS (2026-09-14, superseded above)
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
