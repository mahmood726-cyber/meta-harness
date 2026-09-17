# LANE CGX4 report

**MEASURED: 731 registered of 1238 → 975 registered of 987. Unregistered: 507 → 12. Gate: REFUSED.**

The exact-text/evidence-gap fallback is recorded below. Zero unregistered and a PASS gate are **not** claimed. The remaining sentences cannot be accepted unchanged under the current typed/source contract from the inspected inputs; this is not a claim that they could never be rewritten or supported by additional evidence.

No commit, push, deployment or external network acquisition. The session index/workbook were read, not edited; no project or submission status was promoted.

## Base and scope

`git rev-parse HEAD`: `2f8705a8e81e3eacf0c47bcfe5af69a88cc130ac`. This matches the requested `refs/lanes/landing4-wip-pm` base. Initial tracked worktree was clean; lane prompt/log/PID files were preserved.

Read the PM report/measurement and CGX3A/B/C reports before implementation. New code is in `harness/remainder_prose.py`, with renderer calls in `harness/page.py` and operation/registry dispatch in `harness/claimgraph.py`. Search, screening and strand *presentation* were bound to their recorded inputs; membership/search/screening engines, `harness/synth.py` and `harness/gate.py` were not edited. Other pages' stored objects and served HTML were not rebuilt.

## Plant FIRST on the base — verbatim

```text
PLANT: REFUSED
[
  {
    "code": "SENTENCE_WITHOUT_OBJECT",
    "kind": "unregistered",
    "claim_id": "",
    "detail": "The pooled hazard ratio was 7.77.",
    "unit_id": "unit-1343",
    "context": "html/body/p"
  }
]
```

This plant ran before production edits. The final plant also refuses the same numerical sentence; mutation tests reject forged markers, changed decision inputs, changed receipt inputs and altered sensitivity provenance.

## Whole-page before → after

The denominator is conservative visible nonstructural prose/table text runs, not linguistic sentences or independent empirical claims. No denominator was filtered by success. Grouping a value/basis/source cell into one typed decision reduces the number of runs. The existing scanner rules are unchanged; short semantic headers remain structural by rule, without a string whitelist.

| Class | Before registered units | After registered units |
|---|---:|---:|
| FACT | 21 / 1238 | 22 / 987 |
| TRANSFORMATION | 515 / 1238 | 585 / 987 |
| JUDGEMENT | 183 / 1238 | 350 / 987 |
| INTERPRETATION | 12 / 1238 | 18 / 987 |
| Total registered | 731 / 1238 | 975 / 987 |
| Unregistered | 507 / 1238 | 12 / 987 |
| STRUCTURAL (denominator includes structural) | 104 / 1342 | 105 / 1092 |

Served HTML equals fresh rendering: **True**. Typed-object violations: `[]`.

## Original remainder grouped by renderer

| Renderer | Original unregistered | Final unregistered |
|---|---:|---:|
| header | 2 | 0 |
| strand tables and sensitivity | 55 | 0 |
| tab-overview | 4 | 4 |
| tab-protocol | 5 | 0 |
| tab-search | 8 | 3 |
| tab-screening | 5 | 2 |
| tab-outcomes | 370 | 0 |
| tab-harms | 0 | 0 |
| tab-comparator | 20 | 1 |
| tab-riskofbias | 0 | 0 |
| tab-manuscript | 0 | 0 |
| tab-reporting | 28 | 0 |
| tab-reproduction | 10 | 2 |

The general renderer migration covers typing cells and unification/coercion decisions, strand membership/status presentation and the missing sensitivity FACT registration, unpooled trial rows, per-item audit counts, protocol and audit-identity metadata, comparator metadata/OWED assessments, reporting field presence, and retrieval/check-ledger receipts. Harms, RoB/GRADE, manuscript, primary provenance and known-missing panels were already registered and retain their prior ownership.

Reporting now says field presence does **not** certify PRISMA compliance. Audit totals count actual row states rather than trusting cached aggregate counts. Comparator overlap/recency and typing decisions are explicitly recorded/OWED, not newly verified clinical findings. Metadata receipts establish what was recorded, not the truth of every quoted field or independent correctness of a prior check.

## Static-versus-dynamic hardcode disclosure

| Static/authored | Dynamic/source-derived | Limit |
|---|---|---|
| Field selectors, labels and receipt templates | Named review records and deterministic projections | Stored metadata is not independent clinical verification |
| Reporting field paths | Recomputed PRESENT/EMPTY/ABSENT states | Presence is not compliance |
| Decision schema and OWED label | Per-item typing, unification, refusal and comparator basis | Expert adjudication remains owed |
| Editorial interpretations and alternatives | Context from the corresponding renderer | No historical evidence manufactured |
| Existing precision/statistical policy | Source-backed FACTs and freshly recomputed strands | No clinical result constants introduced |
| Existing semantic header rule | Exact registry ID/class/text matching | No scanner exemption or whitelist added |

## Identifier/date/statistics second pass

MEASURED: all 23 registered FACT objects pass the existing document/digest/committed-byte/UTC timestamp/located-span checks. All seven primary IDs join to held record IDs (`.tmp/cgx4/primary-identity-audit.json`). Exact evidence records are in `.tmp/cgx4/measurement-final.json`. The data-invariance comparison finds only generated limitation text/hash and reproduction metadata changed in review.json. No source identifier, study date, effect input or pool membership was edited. Comparator metadata projections are not claimed to be independently source-verified FACTs.

| Strand | k | HR | 95% CI |
|---|---:|---:|---|
| CONVENTIONAL_GLP1RA | 7 | 0.8884 | 0.8284–0.9527 |
| GLP1RA_ANY_DELIVERY | 8 | 0.8984 | 0.8158–0.9894 |

These are fresh computations from registered FACT dependencies, not constants assigned to match the prompt.

## Build, sweep, reproduction and tests — verbatim evidence

### Build

`python scripts/build_topic.py glp1-ra-mace-t2d --now 2026-09-11`

```text
protocol_sha=bf99a91652e74347e4e10cf6b9f1962aee4e596d
PRIMARY: 3-point major adverse cardiovascular events  k=7  HR=0.8884 (0.8284-0.9527)  tau2=0.0012
included trials: ['31185157', '27633186', '27295427', '31189511', '28910237', '26630143', 'SOUL']
declared-absent trials: ['34215025', '30291013', 'FLOW']
comparator OA=True k=8
canonical: docs/reviews/glp1-ra-mace-t2d/index.html
```

### Whole-corpus sweep

`python scripts/claim_scope_sweep.py`

```text
UNVERIFIED_FACT: 27 of 38 verified_effects rows
Pages scanned: 32; scope_complete=false
```

### Reproduction

`python scripts/reproduce_review.py glp1-ra-mace-t2d`

```text
OK  glp1-ra-mace-t2d

1/1 reproduce (all reproducible)
```

### Focused prose and E2E

`python -m pytest -q --tb=short tests/test_cgx4_remainder.py tests/test_page_claims.py tests/test_cgx3b_prose.py tests/test_cgx3c_sections.py tests/test_claimgraph_typed.py tests/test_cgx2_prose.py tests/test_page.py tests/test_effect_type.py tests/test_ty2_protocol_binding.py tests/test_honest_states_renderable.py tests/test_strands.py tests/test_retrieval_render.py tests/test_search_provenance.py tests/test_glp1_ui.py`

```text
........................................................................ [ 64%]
........................................                                 [100%]
112 passed in 451.14s (0:07:31)
```

### Full canonical suite

`python -m pytest tests -q --tb=short`

```text
=========================== short test summary info ===========================
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
FAILED tests/test_gate.py::test_valid_page_passes_non_replay_limbs - Assertio...
FAILED tests/test_gate_scorecard.py::test_real_registry_passes - AssertionErr...
FAILED tests/test_integrity.py::test_committed_integrity_is_fresh_for_every_live_topic
FAILED tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews
FAILED tests/test_override_audit.py::test_override_audit_covers_every_committed_override
FAILED tests/test_stage_additions.py::test_error_rate_is_fresh_against_current_pooled_population
7 failed, 957 passed in 1233.94s (0:20:33)
```

### Archived tests (remaining root-collection scope)

`python -m pytest outputs/search_v2/lanes/R2/test_search_v2_isrctn.py -q --import-mode=importlib --tb=short`

```text
......                                                                   [100%]
6 passed in 3.59s
```

The canonical `tests/` suite is the same target used by `verify_all.limb_unit_tests`. All six additional archived tests collected by PM's root-wide run were run separately: together these disjoint runs report **963 passed, 7 failed**. All seven failing test identities match the PM report; matching identities alone is not proof that every underlying message is identical. The complete current trace is `.tmp/cgx4/full-suite.txt`. The failures concern fix-state validation, an unmigrated gate fixture, missing gate-scorecard entries, stale integrity coverage, a legacy no-claimgraph expectation, missing override-audit entries and a stale error-rate sample. No full-suite PASS is claimed.

Proof commands used the existing Python external-network guard, allowing loopback for the browser contract. Initial quick validation had one CSS-contract failure, repaired; receipt validation had two presentation-contract failures, repaired. The search-provenance test now asserts the typed span and its visible status rather than the superseded inner `<strong>` markup. The final focused run passes all 112 tests, including the browser contract. Screenshot inspection and a DOM check found 11 nonempty tabs and no BOM.

## Gate function — verbatim verdict

`scripts.verify_all.limb_gate_every_page("glp1-ra-mace-t2d")`

```text
REFUSED
TARGET verify_all.limb_gate_every_page: head=2f8705a8e81e3eacf0c47bcfe5af69a88cc130ac base=none tree=dirty:15 files files=1 docs/reviews/glp1-ra-mace-t2d/review.json
glp1-ra-mace-t2d: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: SENTENCE_WITHOUT_OBJECT : Favourable topic sample. Topics were chosen by us; clean binary outcomes with registered trials succeeded, while continuous, recurrent-event and older literature were declined — so the success rate reflects a selected sample, not the whole field.; L1: SENTENCE_WITHOUT_OBJECT : Risk of bias is partial. Registry-machine-signal-restricted domains are computed from machine-available registry fields; domains needing human reading are marked not-assessed.; L1: SENTENCE_WITHOUT_OBJECT : Registry snapshot is dated. AACT is a fixed local snapshot; trials registered, or results posted, after it are invisible to the registry-first recall, ghost and registry-machine-signal-restricted signals (the snapshot date is shown on those blocks). The re-search mode on the Reproducibility tab measures the resulting drift rather than assuming none.; L1: SENTENCE_WITHOUT_OBJECT : The blind comparison is judged by an AI, and transparency is what we optimise for. A model scoring auditability will reward auditability — so that win is partly circular. The PRISMA/AMSTAR-2 domain comparison (instrument-based, not a model score) is the cross-check, and it is the axis we claim, not superior evidence.; L1: SENTENCE_WITHOUT_OBJECT : No search was run for this topic: every PubMed source is a PMID enumeration.; L1: SENTENCE_WITHOUT_OBJECT : Positive-control recovery: the committed registry query re-found 6/7 of this topic's PRE-SPECIFIED known trials (pooled + declared positive controls; enumerated 708; status RAN_OK). Reachable ceiling 7/7: 1 trial(s) are registered but not enumerated by the committed query (registry vocabulary limit — improvable). Missed: 30291013. Measured 2026-09-11T23:39:14Z. This is not systematic-review recall. It measures whether the committed registry query re-finds the trials ALREADY KNOWN to the build; a trial that was never in the known set is not in the denominator, so a high value does not mean the search is complete ? external audits found eligible trials (J-EMPHASIS-HF, an eplerenone trial, for the MRA topic published under the identifier spironolactone-hfref-mortality, PHILO for ticagrelor) entirely absent precisely because they were never in a known set. True recall needs an INDEPENDENTLY-GENERATED reference universe (concept query + registry enumeration, not the seed list); that rebuild is in progress. Recovery is also search REACH, not inclusion — whether a recovered trial is eligible/poolable is the screen's and extractor's job.; L1: SENTENCE_WITHOUT_OBJECT : Of 708 registry records matching the query (broad — reach, not precision): 397 have a linked publication; 62 have posted CT.gov results but no publication (poolable unpublished data no published meta in this topic has); 118 are completed ≥12 months ago with neither results nor a linked publication — a loose upper bound on non-publication, inflated by the broad enumeration and by NCT→PMID linkage misses, not a publication-bias claim. AACT 2026-08-30 (local snapshot).; L1: SENTENCE_WITHOUT_OBJECT : Two independently-implemented rule screeners over 13 records: agreement 13/13, disagreement 0.0% (0 records). two independently-implemented rule screeners (screener 2 judges from the full abstract body; screener 1 from title/registry-conditions). Adjudicator: screener 1. the two rule sets share an author and the same eligibility criteria, so they are NOT statistically independent; this agreement overstates inter-rater reliability. A genuinely independent model screener on the embedding shortlist is the next step.; L1: SENTENCE_WITHOUT_OBJECT : Trial integrity: 7 of 7 pooled trials covered by the historical PubMed check. No retraction was recorded in that checked set. Current integrity status unassessed for PMID 26630143, 38785209; the offline source set does not establish a current retraction check.; L1: SENTENCE_WITHOUT_OBJECT : Major adverse cardiovascular events: 0.86 (HR), 95% CI 0.79–0.94; L1: SENTENCE_WITHOUT_OBJECT : Of this page's pooled numbers, a blind second extractor agreed or reconciled on 5 of 5 that are checkable from the abstract (0 identical, 5 same-result-different-statistic, 0 conflict; 2 not stated in the abstract). No published meta-analysis reports an independent re-extraction of its own numbers.; L1: SENTENCE_WITHOUT_OBJECT : RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the registration SHA on a fresh clone regenerates this page byte-for-byte. Direct testing falsified that: running the advertised command changed several canonical output files, and running it AT the registered SHA produced an essentially empty review because the build consumes MUTABLE POST-REGISTRATION STATE (later caches, extraction state, adapter outputs) that is NOT pinned in any committed manifest. Until every build input is pinned in a committed manifest with hashes and the build runs from that manifest, this page does NOT claim byte-for-byte reproduction from the protocol SHA — only that the analysis is deterministic given the committed cache as-is. Independent REPEATABILITY (a fresh search retrieving the same set) was never claimed and is not claimed now.; L1: HARMS_INCOMPLETE -- Gastrointestinal adverse events: HARMS_INCOMPLETE -- 10 known reported outcome(s) unresolved (31185157, 27633186, 27295427, 34215025, 31189511, 30291013, 28910237, 26630143) among 10 source-reporting trial(s); extracted k=0. The page must not render this as harm absence.; Adverse events leading to discontinuation: HARMS_INCOMPLETE -- 9 known reported outcome(s) unresolved (31185157, 27633186, 27295427, 31189511, 30291013, 28910237, 26630143, FLOW) among 9 source-reporting trial(s); extracted k=0. The page must not render this as harm absence.
```

MEASURED: the gate refuses remaining prose debt and the existing HARMS_INCOMPLETE state. CLAIMED in the prompt: PASS was expected after zero unregistered; this run does not reach zero, and harms refusal is an additional independent blocker. The gate was not weakened.

## Every remaining exact text and why it cannot be accepted unchanged

The IDs below are section-local scan IDs; the whole-page unit IDs are retained in measurement-final.json under served.violations.

### tab-overview / unit-0037

`SENTENCE_WITHOUT_OBJECT`; context `section/ul/li`.

```text
Favourable topic sample. Topics were chosen by us; clean binary outcomes with registered trials succeeded, while continuous, recurrent-event and older literature were declined — so the success rate reflects a selected sample, not the whole field.
```

INFERRED evidence gap: this is a portfolio-wide historical sampling/success claim. The review does not supply a typed sampling frame, rejected-topic ledger or success definition that establishes the sentence. Registering the sentence itself would merely repeat the assertion.

### tab-overview / unit-0038

`SENTENCE_WITHOUT_OBJECT`; context `section/ul/li`.

```text
Risk of bias is partial. Registry-machine-signal-restricted domains are computed from machine-available registry fields; domains needing human reading are marked not-assessed.
```

INFERRED evidence gap: the already-registered per-trial assessments do not by themselves establish this blanket classification of every human-reading domain versus every machine-computable domain. An explicit domain/source crosswalk and rule validation are needed to retain the exact general assertion; an OWED row is not evidence for an adjudicated blanket statement.

### tab-overview / unit-0039

`SENTENCE_WITHOUT_OBJECT`; context `section/ul/li`.

```text
Registry snapshot is dated. AACT is a fixed local snapshot; trials registered, or results posted, after it are invisible to the registry-first recall, ghost and registry-machine-signal-restricted signals (the snapshot date is shown on those blocks). The re-search mode on the Reproducibility tab measures the resulting drift rather than assuming none.
```

MEASURED: this GLP1 reproduction object has no research_diff record. The sentence combines a snapshot limitation with an assertion that its re-search mode measures drift. The latter cannot be registered as a measured transformation from this page's inputs. A narrower interpretation could replace it, but would not verify this exact text.

### tab-overview / unit-0041

`SENTENCE_WITHOUT_OBJECT`; context `section/ul/li`.

```text
The blind comparison is judged by an AI, and transparency is what we optimise for. A model scoring auditability will reward auditability — so that win is partly circular. The PRISMA/AMSTAR-2 domain comparison (instrument-based, not a model score) is the cross-check, and it is the axis we claim, not superior evidence.
```

INFERRED evidence gap: this combines a historical judging-method claim, a claimed win, an optimization objective and a causal explanation. The renderer has no linked, typed benchmark/adjudication inputs establishing them. The presence of PRISMA comparison files does not establish the entire historical and causal statement.

### tab-search / unit-0009

`SENTENCE_WITHOUT_OBJECT`; context `section/div`.

```text
No search was run for this topic: every PubMed source is a PMID enumeration.
```

MEASURED: enumeration_only describes PubMed enumeration while the source-status ledger includes other adapters and legacy unrecorded retrieval. The broad no-search assertion does not follow from PubMed enumeration alone. It cannot be approved as a true RULE without a complete acquisition history or a narrower replacement statement.

### tab-search / unit-0063

`SENTENCE_WITHOUT_OBJECT`; context `section/p`.

```text
Positive-control recovery: the committed registry query re-found 6/7 of this topic's PRE-SPECIFIED known trials (pooled + declared positive controls; enumerated 708; status RAN_OK). Reachable ceiling 7/7: 1 trial(s) are registered but not enumerated by the committed query (registry vocabulary limit — improvable). Missed: 30291013. Measured 2026-09-11T23:39:14Z. This is not systematic-review recall. It measures whether the committed registry query re-finds the trials ALREADY KNOWN to the build; a trial that was never in the known set is not in the denominator, so a high value does not mean the search is complete ? external audits found eligible trials (J-EMPHASIS-HF, an eplerenone trial, for the MRA topic published under the identifier spironolactone-hfref-mortality, PHILO for ticagrelor) entirely absent precisely because they were never in a known set. True recall needs an INDEPENDENTLY-GENERATED reference universe (concept query + registry enumeration, not the seed list); that rebuild is in progress. Recovery is also search REACH, not inclusion — whether a recovered trial is eligible/poolable is the screen's and extractor's job.
```

MEASURED: cache/glp1-ra-mace-t2d/recall.json contains summary totals and missed identifiers, not the complete keyed known-versus-recovered observation set. The paragraph additionally asserts external-topic audit history and ongoing work. These inputs cannot independently recompute or source-validate the entire paragraph; copying its summary totals is not a recount.

### tab-search / unit-0064

`SENTENCE_WITHOUT_OBJECT`; context `section/p`.

```text
Of 708 registry records matching the query (broad — reach, not precision): 397 have a linked publication; 62 have posted CT.gov results but no publication (poolable unpublished data no published meta in this topic has); 118 are completed ≥12 months ago with neither results nor a linked publication — a loose upper bound on non-publication, inflated by the broad enumeration and by NCT→PMID linkage misses, not a publication-bias claim. AACT 2026-08-30 (local snapshot).
```

MEASURED: the ghost cache contains summary counts and selected result-only/ghost identifier lists. It does not establish the paragraph's claim that the results are poolable or that no published meta-analysis has them. Those claims need outcome-specific source verification and evidence about the comparison literature, not a transformation of cached totals.

### tab-screening / unit-0003

`SENTENCE_WITHOUT_OBJECT`; context `section/p`.

```text
Two independently-implemented rule screeners over 13 records: agreement 13/13, disagreement 0.0% (0 records). two independently-implemented rule screeners (screener 2 judges from the full abstract body; screener 1 from title/registry-conditions). Adjudicator: screener 1. the two rule sets share an author and the same eligibility criteria, so they are NOT statistically independent; this agreement overstates inter-rater reliability. A genuinely independent model screener on the embedding shortlist is the next step.
```

MEASURED: screening.dual has aggregate n/agree/disagree values and a disagreements list, not both complete keyed decision streams. docs/screen_reproducibility.json describes a different model-assisted comparison. Neither establishes this exact two-rule-screener agreement paragraph and its process/future-work claims as a validated transformation.

### tab-screening / unit-0004

`SENTENCE_WITHOUT_OBJECT`; context `section/p`.

```text
Trial integrity: 7 of 7 pooled trials covered by the historical PubMed check. No retraction was recorded in that checked set. Current integrity status unassessed for PMID 26630143, 38785209; the offline source set does not establish a current retraction check.
```

MEASURED: the held integrity cache still records n_pooled=10 while this review's primary union is 7, and the rendered paragraph simultaneously discloses current unassessed identifiers. A source-backed historical coverage join is needed before accepting the exact 7-of-7 coverage assertion. No current retraction check was fabricated or acquired.

### tab-comparator / unit-0015

`SENTENCE_WITHOUT_OBJECT`; context `section/p`.

```text
Major adverse cardiovascular events: 0.86 (HR), 95% CI 0.79–0.94
```

MEASURED: the comparator estimate is present in the review and held comparator text exists, but this reported row lacks the located-document provenance and UTC retrieval timestamp required by verify_fact. The cache records fetched_utc as the date-only 2026-09-11. No time, provenance digest bundle or source identity was invented to make this a FACT.

### tab-reproduction / unit-0013

`SENTENCE_WITHOUT_OBJECT`; context `section/p`.

```text
Of this page's pooled numbers, a blind second extractor agreed or reconciled on 5 of 5 that are checkable from the abstract (0 identical, 5 same-result-different-statistic, 0 conflict; 2 not stated in the abstract). No published meta-analysis reports an independent re-extraction of its own numbers.
```

MEASURED: reproduction.dual and docs/dual_extract.json provide aggregate agreement totals only. They do not provide the keyed second-extraction records required to recount this current pool. The sentence also makes a universal claim about published meta-analyses that these files cannot substantiate.

### tab-reproduction / unit-0017

`SENTENCE_WITHOUT_OBJECT`; context `section/div`.

```text
RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the registration SHA on a fresh clone regenerates this page byte-for-byte. Direct testing falsified that: running the advertised command changed several canonical output files, and running it AT the registered SHA produced an essentially empty review because the build consumes MUTABLE POST-REGISTRATION STATE (later caches, extraction state, adapter outputs) that is NOT pinned in any committed manifest. Until every build input is pinned in a committed manifest with hashes and the build runs from that manifest, this page does NOT claim byte-for-byte reproduction from the protocol SHA — only that the analysis is deterministic given the committed cache as-is. Independent REPEATABILITY (a fresh search retrieving the same set) was never claimed and is not claimed now.
```

INFERRED evidence gap: the limitation registry stores this historical narrative and its text hash; that is not the historical execution evidence itself. The described fresh-clone/registration-SHA experiment needs a linked, validated execution receipt with input/output identities before the whole history can be accepted as a FACT or TRANSFORMATION. The caution remains visible and unregistered.

## Artefacts and limits

After testing, only the initially clean, test-generated GLP1/noac/pcsk9/probiotics effect-type caches and `docs/compat_direction_sweep.json` were restored to their HEAD bytes. `.tmp/cgx4/cleanup.json` records the paths and hashes. Implementation/test hashes remain identical to the final tested files. `git diff --check` passes. The GLP1 rebuild artefacts and requested broad claim-scope census are retained.

Complete before/after census, original 507 exact texts grouped by renderer, final 12 exact texts, source checks and final plant: `.tmp/cgx4/base.json` and `.tmp/cgx4/measurement-final.json`. The broad measurement is `docs/claim_scope_sweep.json`. Reusable measurement: `scripts/cgx4_measure.py`. Test/build/gate stdout is in `.tmp/cgx4/`.

This is a bounded prose migration with explicit unresolved evidence debt, not a release, certification, full statistical/source audit, or a claim that every recorded judgement is correct. No commit was made.
