# Comparator panel lane

Base / HEAD at start: `3cf73885ffc83f6fcc4db273c6510a5416cdcde0`.
No commit, staging, push, or external network retrieval performed.

## Implemented

Source panels live at `cache/<slug>/comparators.json`. The pipeline validates document hashes and locatable character spans, attaches the panel, and derives family overlap from the current outcome/strand rows. The publication gate refuses prohibited independence wording for Jaccard > 0.5 or containment of the entire nonempty pool, stale derived overlap snapshots, source-panel drift, and missing/changed evidence. Source panels may not store overlap snapshots at all.

The served panel replaces legacy comparator-number/overlap rendering. Existing scope disclosures remain. Legacy parity numbers are suppressed when a panel exists. Unknown endpoint compatibility remains unknown, and a refused primary pool does not become a pooled set merely because it retains input rows. The source alias binding connects each Giugliano trial name to its PMID in the held original trial record.

The exact adjudicated negative sentence is exempt from the `replicat` stem prohibition; arbitrary negations are not exempt. This resolves the lane's otherwise contradictory requirement to forbid that stem while rendering “not independent replication.”

## Plants FIRST on the base

Before changing implementation, `python -m pytest tests/test_comparator_panel.py -q` produced:

```text
FF                                                                       [100%]
FAILED tests/test_comparator_panel.py::test_equal_pool_independent_corroboration_refused
FAILED tests/test_comparator_panel.py::test_stored_overlap_drift_refused
E AttributeError: module 'harness.gate' has no attribute 'check_no_independent_corroboration_claim'
2 failed in 4.39s
```

The first plant supplied identical two-family comparator/pool sets and page text “independent corroboration.” The second supplied a stored shared list `['WRONG']` against live `['A', 'B']`. **MEASURED:** the base lacks the semantic check; these are red tests for missing protection, not a claim that a hash-invalid page passed every existing publication gate. Both plants now return refusal reasons. Additional controls cover synonyms, the strict 0.5 boundary, containment below that boundary, live membership changes, distinct strands, unknown endpoints, source tampering, absent held facts, and source overlap prohibition.

## Evidence and coverage

**MEASURED:** 32 source panels, 36 comparator entries, 32 entries with held documents (not a count of unique publications across topics). Three full texts are embedded in `records.json#comparator_fulltext`; an empty standalone file is not evidence of absence. The remaining four entries are the lane-supplied Sattar 2021, Hasebe 2025, Lee 2025, and Abdalla 2026 identities. They render **NOT HELD — identity only**, with no statistical fields. Full bibliographic identity for those four is not held and was not invented.

**MEASURED:** Giugliano's held Table 2 span supports k=8, HR=0.86, CI 0.79–0.94, and I²=50.0. Its methods paragraph supports Paule–Mandel / Hartung–Knapp. No prediction interval was extracted. Trial membership and endpoint definitions have separate located spans. The live primary pool shares AMPLITUDE-O, EXSCEL, HARMONY Outcomes, LEADER, PIONEER 6, REWIND, and SUSTAIN-6. Harness-only is PMID 40162642 (SOUL); comparator-only is ELIXA. Jaccard is 7/9 = 0.7777777777777778. Seven shared families have compatible three-point MACE definitions; ELIXA's four-point definition is explicitly distinct.

**Coverage limit:** only Giugliano has a completely curated family set in this new panel schema. The other held documents are disclosed as held but their unextracted statistics and memberships remain unknown. Thus **1 of 36** comparators has a measured Jaccard > 0.5, **1 of 1 enumerable**; this is not a claim that the other 35 have low overlap. General machinery handles all outcomes and strands; it does not infer unextracted trial lists from an abstract count or a stored overlap list.

`docs/comparator_panel_sweep.json` measures literal prohibited stems on **6/32 → 2/32** pages, excluding only the mandated adjudicated sentence. The remaining two are denosumab and omega-3 trial-level CT.gov structured-result checks, not comparator-independence statements. The four removed cases were legacy negative arithmetic-agreement labels. No positive comparator-independence claim was observed on the base GLP-1 page; the adversarial plant demonstrates the missing protection.

**INFERRED / adjudicated:** mapping the source's endpoint prose to the declared three-point-MACE outcome is a curated semantic judgment, not an NLP-derived fact. The requested robustness/heterogeneity sentence is adjudicated interpretation with its numerical value read from the source object.

**CLAIMED only:** author/year identities of the four unheld additional comparators come from the lane prompt. Their k, effects, intervals, heterogeneity, methods, trial lists, and publication identifiers are not asserted.

## Static versus dynamic disclosure

| Component | Static, source-bound input | Dynamic computation |
|---|---|---|
| Identity and facts | Local citation metadata, curated Giugliano Table 2/method spans | Hash, span and value-presence validation |
| Family identity | Source-backed family/PMID bindings | Live rows resolved to families; set differences and Jaccard |
| Endpoint overlap | Located endpoint definitions and curated outcome key | Shared compatible families; unknowns reported separately |
| Claim wording | Lane's adjudicated sentence and prohibited stems | Held effect interpolation, live-overlap claim refusal |
| Sweep | Explicit base commit | Corpus counts and base/current phrase scan |

## Validation

Initial complete corpus build: **32/32 PASS**. Final corpus build and targeted embedded-document corrections completed. Empty-AACT replay, retraction survival, focused/browser tests, and the full verifier table are appended below from the final checks. A prior focused/browser run passed **30 tests**, including opening and exercising the Comparator tab on all 32 pages with external requests blocked. The new gate is registered with no production adjudication events and is therefore not claimed production-validated.

Replay is working-tree offline mode, not a fresh-clone release claim; the new panels remain uncommitted as instructed. The first full verification exposed a legacy gate's required absence strings, an outdated numeric-parity UI assertion, and a stale generated fix ledger. The absence disclosures were restored without restoring unsupported numbers; the assertion now checks the explicit unenumerated panel while retaining the existing four-trial membership assertions. The ledger was regenerated. The isolated HM1 browser rerun passed (1 test), and the integration follow-up passed 37 tests. The first full run is retained in `outputs/comparator-lane/verify-all-first.txt`.

The second full run passed the publication gates on all pages and the fix ledger, but one browser test received a 404 from a competing localhost listener; its captured server log included requests from a different page test. The Windows UI fixture now uses `SO_EXCLUSIVEADDRUSE`, keeps `127.0.0.1:8000`, and waits at most 90 seconds for an occupied listener rather than sharing the port. It does not terminate other processes. All four browser contracts then passed together (4 passed in 36.81s). The second full table is retained in `outputs/comparator-lane/verify-all-second.txt`. The complete verifier was run a third time after that repair, within the three-run cap.

Final checks: build **32/32**, empty-AACT byte replay **32/32**, retraction survival against the specified base **32/32**. All 36 source entries validated, and the comparator gate passes **32/32**. The live pool/strand adapter also executed successfully against all 32 current reviews. `git diff --check` passes. HEAD remains the specified base; nothing was committed. The full verifier remains refused only by the honest-state ratchet; no release certification is claimed.

## Final full verification output

```text
TARGET verify_all: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:217 files files=1 scripts/verify_all.py
VERIFY-ALL: 11 limbs, all run, fail-closed. root=C:\mh-r-CMP
  [             PASS] unit tests (pytest tests/)  (246s)
        TARGET verify_all.limb_unit_tests: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:217 files files=149 tests/conftest.py tests/test_aact_cache.py tests/test_aact_recurrent_guard.py ...
  [             PASS] offline reproduction (every live page replays from committed cache)  (54s)
        TARGET verify_all.limb_reproduction: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:217 files files=33 scripts/reproduce_review.py docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json docs/reviews/colchicine-postop-af/review.json ...
  [             PASS] publication gate on every live review page  (53s)
        TARGET verify_all.limb_gate_every_page: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:217 files files=32 docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json docs/reviews/colchicine-postop-af/review.json docs/reviews/colchicine-recurrent-pericarditis/review.json ...
  [             PASS] index currency (generated == committed docs/index.html)  (2s)
        TARGET verify_all.limb_index_currency: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:217 files files=696 docs/index.html docs/evidence/CAPTIONS.json docs/evidence/CAPTIONS.json ...
  [             PASS] served-artefact leak scan (docs/*.json)  (0s)
        TARGET verify_all.limb_leak_scan: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:217 files files=117 docs/arm_object_sweep.json docs/class_discovery.json docs/cochrane_headtohead.json ...
  [             PASS] held-out leak detector (registry/heldout_sealed.json)  (332s)
        TARGET verify_all.limb_heldout: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:217 files files=3 registry/heldout_sealed.json docs/search_recall_regression_corpus.json harness/acquisition.py
  [             PASS] search completeness (search_v2 measurement current; every state explicit; no zero from an exit code)  (2s)
        TARGET verify_all.limb_search_completeness: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:217 files files=3 registry/search_completeness.json harness/search_v2.py harness/search_completeness.py
  [             PASS] fix-state discipline (registry/fixes.json)  (81s)
        TARGET verify_all.limb_fixstate: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:217 files files=3 registry/fixes.json docs/fix_ledger.json scripts/render_fix_ledger.py
  [          REFUSED] honest-state ratchet (no page may get quieter)  (15s)
        TARGET verify_all.limb_honest_ratchet: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:217 files files=34 docs/index.html docs/ratchet_acknowledgements.json docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html ...
        TARGET honest_ratchet: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=2304824034b4ba8677da2d2d2453352711ed2a9b tree=dirty:217 files files=34 docs/index.html docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html docs/reviews/colchicine-postop-af/index.html ... base_resolution=merge-base origin/main pages=33 block_floor_refs=2304824034b4ba8677da2d2d2453352711ed2a9b,50f5a67b4fb19ada4716a0df6e6b68c2e4618304
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: not_assessed: base count 10, new count 6
        docs/reviews/esketamine-trd-madrs/index.html: declared_absent: base count 12, new count 11
        docs/reviews/metformin-pcos-ovulation/index.html: not_assessed: base count 14, new count 13
        docs/reviews/probiotics-aad-prevention/index.html: not_assessed: base count 34, new count 24
        docs/index.html: lost banner block 2c1c3da7038bd131e062ff9854e52955fbfc9f879c8cda1c38a211b17e690ec9: Gate scorecard: plant validations and production refusals Adjudication coverage first, so the unresolved cannot disappea
        docs/index.html: lost banner block 14d82d4fda711fe9fe91721913d27f94c8af2fd442ab1832769897c57d897bbd: Parity with the published comparator (the finishing metric) For each same-scope topic: our pooled k vs the comparable co
  [             PASS] gate scorecard (every gate accounted for)  (1s)
        TARGET verify_all.limb_gate_scorecard: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:217 files files=3 registry/gate_scorecard.json docs/gate_scorecard.json harness/gate_scorecard.py
        TARGET gate_scorecard: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:217 files files=6 registry/gate_scorecard.json docs/gate_scorecard.json scripts/verify_all.py ...
  [             PASS] gate gaps table (sealed what-it-would-not-stop rows)  (7s)
VERIFY-ALL: REFUSED -- 1 of 11 limbs not PASS. Fix the harness, never the gate.
```

The ratchet uses its own historical floor refs, rather than only this lane's specified base. Its remaining marker/banner refusals are preserved below and in `STUCK_FAILURES.md`; no acknowledgements or gate bypasses were added. The separate requested retraction comparison against `3cf73885ffc83f6fcc4db273c6510a5416cdcde0` passes for every page.
