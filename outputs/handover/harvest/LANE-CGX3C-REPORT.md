# LANE CGX3C report

HEAD: `bf99a91652e74347e4e10cf6b9f1962aee4e596d`. Requested base: `refs/lanes/landing4-wip-str` = `bf99a91652e74347e4e10cf6b9f1962aee4e596d`.
No commit or push. No network retrieval. Workbook and portfolio registry were read, not edited; no submission or project promotion occurred.

## Finish-condition status

**NOT MET:** the lane improved from **0 registered of 496** to **451 registered of 488**. There remain **37** visible unregistered units, listed verbatim below. This report is not a claim of complete migration or release readiness. The unregistered source/search/comparator prose remains scan debt; it has not been labelled STRUCTURAL, FACT, or adjudicated merely to raise coverage.

## Scope and counting contract

The selection script scans the Search, Screening, Comparator and Harms tab bodies; the Stated limitations list in Overview; and the Parity paragraph in Reproducibility. The trial-family table is the table inside Screening. Other Overview, Results, protocol, RoB/GRADE, manuscript and reproduction renderers are outside this lane. Counts use the existing conservative visible-text-run contract, not linguistic sentence counts. Short semantic table headers are STRUCTURAL by the existing syntactic rule; no string whitelist was added. Headings/navigation remain excluded by the existing scanner.

| Scope | Before | After | Structural before → after |
|---|---:|---:|---:|
| search | 0 / 53 | 47 / 55 | 14 → 13 |
| screening | 0 / 147 | 131 / 136 | 12 → 10 |
| comparator | 0 / 25 | 3 / 23 | 22 → 20 |
| harms | 0 / 263 | 266 / 266 | 8 → 8 |
| limitations | 0 / 7 | 3 / 7 | 0 → 0 |
| parity | 0 / 1 | 1 / 1 | 0 → 0 |

The denominator changes because a selection summary replaces multiple count cells and prose fragments, harms cells are emitted as individual registered fields, and comparator audit status/note fragments are combined. No denominator was filtered based on whether a sentence passed.

## Plant first, on the base renderer

Before renderer edits: rebuilt GLP1, ran the full-detail slug sweep, then inserted one unsupported numerical sentence into the limitations fragment in memory. No source or served page was permanently planted. The plant command exited 1. Verbatim output:

```text
search: 0 registered of 53; 14 structural
screening: 0 registered of 147; 12 structural
comparator: 0 registered of 25; 22 structural
harms: 0 registered of 263; 8 structural
limitations: 0 registered of 8; 0 structural
parity: 0 registered of 1; 0 structural
FAIL (expected plant): {"code": "SENTENCE_WITHOUT_OBJECT", "kind": "unregistered", "claim_id": "", "detail": "There were 987654 screened records.", "unit_id": "unit-0001", "context": "ul/li"}
```

Evidence: `LANE-CGX3C-BASELINE.json`, `LANE-CGX3C-BASELINE-SECTIONS.json`, `LANE-CGX3C-PLANT.json`. The reusable census/plant entrypoint is `scripts/claim_scope_cgx3c.py`.

## Implemented machinery and limits

- `harness/section_claims.py` registers exact internal-ledger projections, per-item selection/harms count transformations, comparator assessments labelled OWED, and interpretations with rendered alternatives. Both `page.py` and `claimgraph.review_graph` use the same builders.
- A ledger projection states **Recorded field: value**. It establishes what the review object records, not independent clinical truth. These objects are TRANSFORMATION, not FACT. Stored values are deep-copied so later nested mutations cannot silently mutate both the input and the expected output.
- Selection counts ignore cached `n_records` and pooled `k` totals, count actual records/families, break exclusions down by rule, and show both unpooled state counts and absence/refusal-kind counts. Duplicate record identifiers fail closed. The contradictory upstream pair `EXTRACTION_NOT_PERFORMED` / `refused_on_evidence` is preserved and exposed, not silently repaired in membership.
- Retrieval source cells use explicit field-format transformations over their source row. Query-classification basis cells and indexed query text are registered too. Removing a query or mutating a source state invalidates its rendering. Snapshot narratives and unsupported summary-level search claims remain debt.
- Registration is not equivalent to an independent recount: retrieval funnel cells format stored source-ledger figures. They do not reconstruct query yields from raw per-record states. This is an additional limit on the aggregate count-chain finish condition, even though the field-format transformation itself is registered and checked. Selection and harms summaries do recompute from their item lists.
- Unpooled harms tables use their per-report harms state. They keep recorded extraction-state and evidence-span fields visible, distinguish `KNOWN_REPORTED_NOT_YET_EXTRACTED`, and explicitly state that these ledger states do not establish harm absence. Other harms schemas retain the existing renderer and are not claimed migrated.
- Parity now counts the stored shared/only-ours labels and compares that enumeration with the current primary families. GLP1 has seven pooled families but eight distinct recorded overlap labels. The relation is withheld as UNRENDERABLE with adjudication OWED. Even reconciled counts do not establish identifier-level set equality.
- Three limitation interpretations render alternatives. Other historical limitations remain unregistered, rather than being laundered as adjudicated judgements.
- Existing GRADE arithmetic (start minus assessed per-domain downgrades, otherwise provisional) remains unchanged; the focused tests exercise it. This lane does not migrate the RoB/GRADE section.
- No edits to `harness/synth.py`, `harness/gate.py`, membership, acquisition/search, or screening-engine modules. Only their owned page rendering surfaces were changed.

## Static-versus-dynamic disclosure

| Component | Static | Dynamic / validation |
|---|---|---|
| Boundary interpretations | Editorial formulations and alternatives | Marked INTERPRETATION; alternative visibly rendered |
| Ledger fields | Field selectors, labels | Exact input-row projection, mismatch checks; not independent FACT validation |
| Selection and harms | Count/format rules | Per-item identities, decisions, states and refusal kinds |
| Comparator assessments | OWED label | Recorded assessment and basis; no human signature invented |
| Parity | Count consistency rule | Current families and explicit shared/only-ours label lists |
| Scientific estimates | No new constants or synthetic results | Existing source/pipeline outputs retained |

## Verification

Commands ran offline against existing cached data. Test subprocesses used a task-local guard against external socket connections, permitting localhost for the UI contract.

### Rebuild

`python scripts/build_topic.py glp1-ra-mace-t2d --now 2026-09-11`

Full output: `LANE-CGX3C-BUILD.txt`.

```text
protocol_sha=bf99a91652e74347e4e10cf6b9f1962aee4e596d
PRIMARY: 3-point major adverse cardiovascular events  k=7  HR=0.8884 (0.8284-0.9527)  tau2=0.0012
included trials: ['31185157', '27633186', '27295427', '31189511', '28910237', '26630143', 'SOUL']
declared-absent trials: ['34215025', '30291013', 'FLOW']
comparator OA=True k=8
canonical: docs/reviews/glp1-ra-mace-t2d/index.html
```

### Focused suite

`python -m pytest -q tests/test_cgx3c_sections.py tests/test_claimgraph_typed.py tests/test_cgx2_prose.py tests/test_page.py tests/test_retrieval_render.py tests/test_harms_recovery.py tests/test_parity_relation.py tests/test_limitations.py tests/test_glp1_lane.py --tb=short`

Full output: `LANE-CGX3C-FOCUSED-TESTS.txt`.

```text
........................................................................ [ 97%]
..                                                                       [100%]
74 passed in 250.20s (0:04:10)
```

### UI contract

`python -m pytest -q tests/test_glp1_ui.py --tb=short`

Full output: `LANE-CGX3C-UI-TEST.txt`.

```text
.                                                                        [100%]
1 passed in 38.76s
```

### Full suite (final source)

`python -m pytest -q --import-mode=importlib --tb=short`

Full output: `LANE-CGX3C-FINAL-FULL-TESTS.txt`.

```text
=========================== short test summary info ===========================
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
FAILED tests/test_gate.py::test_valid_page_passes_non_replay_limbs - Assertio...
FAILED tests/test_gate_scorecard.py::test_real_registry_passes - AssertionErr...
FAILED tests/test_integrity.py::test_committed_integrity_is_fresh_for_every_live_topic
FAILED tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews
FAILED tests/test_override_audit.py::test_override_audit_covers_every_committed_override
FAILED tests/test_stage_additions.py::test_manuscript_limb_passes_on_every_live_review
FAILED tests/test_stage_additions.py::test_manuscript_limb_REFUSES_a_fabricated_number
FAILED tests/test_stage_additions.py::test_error_rate_is_fresh_against_current_pooled_population
9 failed, 936 passed in 1040.48s (0:17:20)
```

Default `python -m pytest -q --tb=short` initially stopped at collection: `1 error in 10.09s`, because `outputs/search_v2/lanes/R2/test_search_v2_isrctn.py` and `tests/test_search_v2_isrctn.py` collide under default import mode. The full-suite rerun above uses importlib mode and includes both files.

The legacy limitation-snapshot failure on balanced-crystalloids also reproduces using the base `HEAD:harness/page.py` loaded in memory: `1 failed in 2.55s`. See `LANE-CGX3C-BASELINE-LEGACY-TEST.txt`. No unrelated page snapshots were repaired.

All nine failures from the first complete suite were replayed with both `HEAD:harness/page.py` and `HEAD:harness/claimgraph.py` loaded in memory against the same data tree. Result: **9 failed in 124.68s (0:02:04)**, with the same failure reasons. Full diagnostics: `LANE-CGX3C-BASELINE-FAILURES.txt`. This is a base-implementation comparison, not a separate pristine checkout. The earlier full run (before the final retrieval additions) was **9 failed, 934 passed in 1321.47s (0:22:01)**; its complete log is `LANE-CGX3C-FULL-TESTS.txt`.

Second-pass source review: all seven primary trial rows still pass `claimgraph.verify_fact` as FACT. SOUL, FLOW and FREEDOM-CVO are additions outside the original main records cache; their pre-existing held-source paths/provenance are retained. No trial identifiers, source dates, effect estimates or membership were edited by this lane. The required rebuild refreshed protocol/build hashes and attestations in generated JSON. The declared-state/refusal-kind and parity discrepancies described above prevent stronger claims.

Final cleanup restored only initially clean files generated by the tests/build: the GLP1, noac, pcsk9 and probiotics `effect_types.json` caches and `docs/compat_direction_sweep.json`. No sibling page was rebuilt. `git diff --check` passes. `LANE-CGX3C-SOURCE-HASHES.json` records implementation/test hashes; these remained unchanged through the final full-suite run.

The comparator magnitude was also checked offline: `cache/glp1-ra-mace-t2d/comparator_fulltext.txt` contains the MACE sentence with HR 0.86 and CI 0.79–0.94. Finding these digits does not itself supply the complete typed document/retrieval/locator contract, or validate the citation identifier and search-cutoff date; those renderer units remain explicit debt.

## Other pages: measured, not chased

`python scripts/claim_scope_sweep.py --output LANE-CGX3C-CORPUS-SWEEP.json` measures all pages; served bytes of other topics were not regenerated. The fresh-renderer column shows inheritance of this machinery. These are whole-page counts, not just lane counts.

| Page | Served registered / units | Fresh registered / units |
|---|---:|---:|
| balanced-crystalloids-vs-saline-mortality | 0 / 931 | 441 / 944 |
| colchicine-postop-af | 0 / 1469 | 824 / 1525 |
| colchicine-recurrent-pericarditis | 0 / 1075 | 659 / 1116 |
| colchicine-secondary-cv-prevention | 0 / 2465 | 1271 / 2552 |
| corticosteroids-cap-mortality | 0 / 1929 | 1316 / 2036 |
| corticosteroids-covid19-mortality | 0 / 1026 | 709 / 1070 |
| dapagliflozin-hfpef-hosp | 0 / 1267 | 1034 / 1349 |
| denosumab-vertebral-fracture | 0 / 1021 | 790 / 1080 |
| doac-vte-recurrence | 0 / 2584 | 2411 / 2798 |
| dpp4-mace-t2d | 0 / 799 | 446 / 822 |
| empagliflozin-hfpef-hosp | 0 / 1298 | 1042 / 1383 |
| esketamine-trd-madrs | 0 / 1685 | 1479 / 1809 |
| finerenone-ckd-t2d-renal | 0 / 772 | 417 / 788 |
| glp1-ra-mace-t2d | 472 / 1407 | 472 / 1407 |
| iv-iron-hfref-hosp | 0 / 1028 | 669 / 1060 |
| melatonin-primary-insomnia-sol | 0 / 1658 | 1421 / 1771 |
| metformin-pcos-ovulation | 0 / 1995 | 1779 / 2142 |
| noac-vs-warfarin-af-stroke | 0 / 882 | 414 / 896 |
| omega3-cardiovascular-events | 0 / 2301 | 1444 / 2403 |
| pcsk9-mace | 0 / 678 | 307 / 678 |
| probiotics-aad-prevention | 0 / 7118 | 6129 / 7597 |
| sacubitril-valsartan-hfref | 0 / 1138 | 875 / 1202 |
| semaglutide-obesity-mace | 0 / 947 | 737 / 1001 |
| semaglutide-obesity-weight | 0 / 1852 | 1580 / 1985 |
| sglt2-ckd-progression | 0 / 1113 | 529 / 1141 |
| sglt2-hfref-hosp-cvdeath | 0 / 749 | 367 / 766 |
| sglt2-primary-prevention-hf | 0 / 3080 | 3010 / 3356 |
| spironolactone-hfref-mortality | 0 / 2490 | 2399 / 2704 |
| statins-primary-prevention-elderly | 0 / 773 | 443 / 793 |
| ticagrelor-vs-clopidogrel-acs | 0 / 686 | 412 / 707 |
| tocilizumab-covid19-mortality | 0 / 1295 | 711 / 1337 |
| tranexamic-acid-pph | 0 / 1169 | 874 / 1235 |

## Every remaining unregistered unit, verbatim

Repeated text is listed separately when it is a separate visible unit. These entries are implementation/evidence debt, not an assertion that they are impossible to migrate in a future lane.

### search

Not migrated: the search/retrieval renderer still emits this unit directly. Metadata/query fields need registry bindings; recall/ghost aggregate claims additionally require an enumerated per-item universe rather than the stored summary totals. No source verification or completion of that migration is claimed.

- `unit-0007` — `SENTENCE_WITHOUT_OBJECT`; context `section/div/p`.

  Exact text: "Snapshot: records_sha256 1e0282f5; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query retrieved which record was not recorded; every record's found_by names this single source."

  Reason: Not migrated: the search/retrieval renderer still emits this unit directly. Metadata/query fields need registry bindings; recall/ghost aggregate claims additionally require an enumerated per-item universe rather than the stored summary totals. No source verification or completion of that migration is claimed.

- `unit-0008` — `SENTENCE_WITHOUT_OBJECT`; context `section/div/p`.

  Exact text: "This page replays the committed retrieval snapshot; it is not a claim that the protocol SHA alone regenerates the page byte-for-byte. A live re-search is a separate, dated event (see Re-search below if present)."

  Reason: Not migrated: the search/retrieval renderer still emits this unit directly. Metadata/query fields need registry bindings; recall/ghost aggregate claims additionally require an enumerated per-item universe rather than the stored summary totals. No source verification or completion of that migration is claimed.

- `unit-0009` — `SENTENCE_WITHOUT_OBJECT`; context `section/div`.

  Exact text: "No search was run for this topic: every PubMed source is a PMID enumeration."

  Reason: Not migrated: the search/retrieval renderer still emits this unit directly. Metadata/query fields need registry bindings; recall/ghost aggregate claims additionally require an enumerated per-item universe rather than the stored summary totals. No source verification or completion of that migration is claimed.

- `unit-0045` — `SENTENCE_WITHOUT_OBJECT`; context `section/p`.

  Exact text: "Citation chase: NOT_RUN · ClinicalTrials.gov: RAN_OK · Europe PMC (OA + metadata): RAN_OK · Legacy unrecorded retrieval: RAN_OK · PMC full text: NOT_RUN · PubMed: RAN_OK · Registry-first (AACT): RAN_OK — RAN_OK = ran and returned records; RAN_ZERO = ran, none matched; RAN_ERROR = attempted but failed; NOT_RUN = not attempted for this topic."

  Reason: Not migrated: the search/retrieval renderer still emits this unit directly. Metadata/query fields need registry bindings; recall/ghost aggregate claims additionally require an enumerated per-item universe rather than the stored summary totals. No source verification or completion of that migration is claimed.

- `unit-0046` — `SENTENCE_WITHOUT_OBJECT`; context `section/div/p`.

  Exact text: "KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this topic. an auditable screening ledger attached to an unauditable retrieval process."

  Reason: Not migrated: the search/retrieval renderer still emits this unit directly. Metadata/query fields need registry bindings; recall/ghost aggregate claims additionally require an enumerated per-item universe rather than the stored summary totals. No source verification or completion of that migration is claimed.

- `unit-0062` — `SENTENCE_WITHOUT_OBJECT`; context `section/div`.

  Exact text: "Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK; its evidence set was assembled by KNOWN-ITEM RETRIEVAL of named publications (UID/PMID-anchored queries for pre-identified trials), which cannot discover an unknown eligible trial. A fetch of named identifiers is not a systematic search. We retract any claim of a registry-first or systematic search for this topic."

  Reason: Not migrated: the search/retrieval renderer still emits this unit directly. Metadata/query fields need registry bindings; recall/ghost aggregate claims additionally require an enumerated per-item universe rather than the stored summary totals. No source verification or completion of that migration is claimed.

- `unit-0063` — `SENTENCE_WITHOUT_OBJECT`; context `section/p`.

  Exact text: "Positive-control recovery: the committed registry query re-found 6/7 of this topic's PRE-SPECIFIED known trials (pooled + declared positive controls; enumerated 708; status RAN_OK). Reachable ceiling 7/7: 1 trial(s) are registered but not enumerated by the committed query (registry vocabulary limit — improvable). Missed: 30291013. Measured 2026-09-11T23:39:14Z. This is not systematic-review recall. It measures whether the committed registry query re-finds the trials ALREADY KNOWN to the build; a trial that was never in the known set is not in the denominator, so a high value does not mean the search is complete ? external audits found eligible trials (J-EMPHASIS-HF, an eplerenone trial, for the MRA topic published under the identifier spironolactone-hfref-mortality, PHILO for ticagrelor) entirely absent precisely because they were never in a known set. True recall needs an INDEPENDENTLY-GENERATED reference universe (concept query + registry enumeration, not the seed list); that rebuild is in progress. Recovery is also search REACH, not inclusion — whether a recovered trial is eligible/poolable is the screen's and extractor's job."

  Reason: Not migrated: the search/retrieval renderer still emits this unit directly. Metadata/query fields need registry bindings; recall/ghost aggregate claims additionally require an enumerated per-item universe rather than the stored summary totals. No source verification or completion of that migration is claimed.

- `unit-0064` — `SENTENCE_WITHOUT_OBJECT`; context `section/p`.

  Exact text: "Of 708 registry records matching the query (broad — reach, not precision): 397 have a linked publication; 62 have posted CT.gov results but no publication (poolable unpublished data no published meta in this topic has); 118 are completed ≥12 months ago with neither results nor a linked publication — a loose upper bound on non-publication, inflated by the broad enumeration and by NCT→PMID linkage misses, not a publication-bias claim. AACT 2026-08-30 (local snapshot)."

  Reason: Not migrated: the search/retrieval renderer still emits this unit directly. Metadata/query fields need registry bindings; recall/ghost aggregate claims additionally require an enumerated per-item universe rather than the stored summary totals. No source verification or completion of that migration is claimed.

### screening

Not migrated: this surrounding scope/control/integrity/dual-screening prose is outside the migrated per-record table and count transform. It needs its own rule/evidence object; dual agreement and historical integrity totals cannot be promoted from summary fields alone.

- `unit-0001` — `SENTENCE_WITHOUT_OBJECT`; context `section/p`.

  Exact text: "Identifier scope: identifier leading token matches class term GLP-1RA. Verdict: NOT_APPLICABLE."

  Reason: Not migrated: this surrounding scope/control/integrity/dual-screening prose is outside the migrated per-record table and count transform. It needs its own rule/evidence object; dual agreement and historical integrity totals cannot be promoted from summary fields alone.

- `unit-0003` — `SENTENCE_WITHOUT_OBJECT`; context `section/p`.

  Exact text: "Two independently-implemented rule screeners over 13 records: agreement 13/13, disagreement 0.0% (0 records). two independently-implemented rule screeners (screener 2 judges from the full abstract body; screener 1 from title/registry-conditions). Adjudicator: screener 1. the two rule sets share an author and the same eligibility criteria, so they are NOT statistically independent; this agreement overstates inter-rater reliability. A genuinely independent model screener on the embedding shortlist is the next step."

  Reason: Not migrated: this surrounding scope/control/integrity/dual-screening prose is outside the migrated per-record table and count transform. It needs its own rule/evidence object; dual agreement and historical integrity totals cannot be promoted from summary fields alone.

- `unit-0004` — `SENTENCE_WITHOUT_OBJECT`; context `section/p`.

  Exact text: "Trial integrity: 7 of 7 pooled trials covered by the historical PubMed check. No retraction was recorded in that checked set. Current integrity status unassessed for PMID 26630143, 38785209; the offline source set does not establish a current retraction check."

  Reason: Not migrated: this surrounding scope/control/integrity/dual-screening prose is outside the migrated per-record table and count transform. It needs its own rule/evidence object; dual agreement and historical integrity totals cannot be promoted from summary fields alone.

- `unit-0145` — `SENTENCE_WITHOUT_OBJECT`; context `section/ul/li`.

  Exact text: "Positive: Recovered & included the canonical trials ['27295427', '27633186', '31189511'] that a comparator includes; none missed."

  Reason: Not migrated: this surrounding scope/control/integrity/dual-screening prose is outside the migrated per-record table and count transform. It needs its own rule/evidence object; dual agreement and historical integrity totals cannot be promoted from summary fields alone.

- `unit-0146` — `SENTENCE_WITHOUT_OBJECT`; context `section/ul/li`.

  Exact text: "Negative: Cross-topic trial(s) ['37952131'] recovered by the search and correctly EXCLUDED ['37952131'] by rule (same drug/design, wrong topic)."

  Reason: Not migrated: this surrounding scope/control/integrity/dual-screening prose is outside the migrated per-record table and count transform. It needs its own rule/evidence object; dual agreement and historical integrity totals cannot be promoted from summary fields alone.

### comparator

Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0002` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "GLP-1 receptor agonists and cardiorenal outcomes in type 2 diabetes: an updated meta-analysis of eight CVOTs. (2021), Cardiovasc Diabetol"

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0004` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "PMID 34526024"

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0006` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "True"

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0008` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "https://doi.org/10.1186/s12933-021-01366-8"

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0009` — `SENTENCE_WITHOUT_OBJECT`; context `section/p`.

  Exact text: "Major adverse cardiovascular events: 0.86 (HR), 95% CI 0.79–0.94"

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0010` — `SENTENCE_WITHOUT_OBJECT`; context `section/p`.

  Exact text: "✓ same question. Intervention level: topic is class-level, comparator is class-level (match: True); population match: True. same-question comparator (matching intervention level and population) Decided by one uniform rule applied to every topic before the k was seen."

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0012` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "7"

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0014` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "8"

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0016` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "6, EXSCEL, HARMONY Outcomes, REWIND, PIONEER 6 and AMPLITUDE-O was a three-point MACE, whereas ELIXA used a four-point MACE, including also hospital admission for unstable angina. Characteristics of trials and patients are reported, respectively, in Table 1 . The populations studied ranged in size from 3297 (SUSTAIN-6) to 14,752 (EXSCEL), were of similar age (mean age was 64.0 ± 1.97 years), 37,117 were mal"

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0018` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "7"

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0020` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "SOUL"

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0022` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "ELIXA"

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0024` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "cached comparator text trial-set enumeration"

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0026` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "Comparator trial set was measured from cached comparator abstract/full text."

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0028` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "MEASURED"

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0030` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "named table rows"

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0032` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "ELIXA, LEADER, SUSTAIN-6, EXSCEL, HARMONY Outcomes, REWIND, PIONEER 6, AMPLITUDE-O"

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0036` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "COMPARATOR_PREDATES_POOLED_TRIAL(SOUL)"

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0038` — `SENTENCE_WITHOUT_OBJECT`; context `section/table/tr/td`.

  Exact text: "Comparator search ran to 2021-06-30; SOUL is a 2025 pooled trial."

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

- `unit-0043` — `SENTENCE_WITHOUT_OBJECT`; context `section/p`.

  Exact text: "The comparator k above is auto-extracted from the comparator's own text and may reference a sub-analysis rather than its same-scope pooled total; the enumerated same-scope comparator k (scope-classified, the finishing metric) is the figure in the parity table, which governs where these differ."

  Reason: Not migrated: this comparator citation, source span, estimate, scope or overlap narrative still has no typed rendering binding. Clinical values require located source provenance; overlap statements also need reconciliation with current identities before being asserted as validated.

### limitations

Not migrated: this historical/methodological narrative has no typed evidence/adjudication object in this lane. It was not relabelled as a fact, a RULE judgement or structural furniture.

- `unit-0003` — `SENTENCE_WITHOUT_OBJECT`; context `ul/li`.

  Exact text: "Favourable topic sample. Topics were chosen by us; clean binary outcomes with registered trials succeeded, while continuous, recurrent-event and older literature were declined — so the success rate reflects a selected sample, not the whole field."

  Reason: Not migrated: this historical/methodological narrative has no typed evidence/adjudication object in this lane. It was not relabelled as a fact, a RULE judgement or structural furniture.

- `unit-0004` — `SENTENCE_WITHOUT_OBJECT`; context `ul/li`.

  Exact text: "Risk of bias is partial. Registry-machine-signal-restricted domains are computed from machine-available registry fields; domains needing human reading are marked not-assessed."

  Reason: Not migrated: this historical/methodological narrative has no typed evidence/adjudication object in this lane. It was not relabelled as a fact, a RULE judgement or structural furniture.

- `unit-0005` — `SENTENCE_WITHOUT_OBJECT`; context `ul/li`.

  Exact text: "Registry snapshot is dated. AACT is a fixed local snapshot; trials registered, or results posted, after it are invisible to the registry-first recall, ghost and registry-machine-signal-restricted signals (the snapshot date is shown on those blocks). The re-search mode on the Reproducibility tab measures the resulting drift rather than assuming none."

  Reason: Not migrated: this historical/methodological narrative has no typed evidence/adjudication object in this lane. It was not relabelled as a fact, a RULE judgement or structural furniture.

- `unit-0007` — `SENTENCE_WITHOUT_OBJECT`; context `ul/li`.

  Exact text: "The blind comparison is judged by an AI, and transparency is what we optimise for. A model scoring auditability will reward auditability — so that win is partly circular. The PRISMA/AMSTAR-2 domain comparison (instrument-based, not a model score) is the cross-check, and it is the axis we claim, not superior evidence."

  Reason: Not migrated: this historical/methodological narrative has no typed evidence/adjudication object in this lane. It was not relabelled as a fact, a RULE judgement or structural furniture.

## Unresolved blockers and handoff

See `STUCK_FAILURES.md`. Complete the remaining renderer bindings and source-backed aggregate migrations before claiming the lane finish condition. The focused plant tests should remain red for arbitrary added prose and forged markers. No commit was made.
