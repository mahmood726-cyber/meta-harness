# LANE MU — production mutation report

HEAD measured with `git rev-parse HEAD`: `237e90946f5b257265b0a3b1c986a8907d12eded` (required base). No commit, staging, reset, checkout, stash, network acquisition or committed-page regeneration. No project/submission promotion; central index and workbook are unchanged.

**MEASURED: 6 of 6 mutation classes exercised through real production build boundaries; 5 of 6 READY, 1 of 6 READY-BEHIND-ELX.** There are 8 mutation test cases plus 1 baseline contract (two duplicate topics and two support deletions). Two baseline reviews built, rendered, certified and passed the real gate (2 of 2). The count-based topic is `colchicine-postop-af`: its real primary pool includes two arm-count rows and one reported-effect row; the duplicate selects the count row PMID 32720823.

The precise pre-fix result is **4 failed, 5 passed**. This is not four successful public-release attacks. Three failures show publication/certificate acceptance without the requested typed refusal, but the existing offline-replay gate already refused the edited intermediate core. The fourth is an incomplete stale-consumer diagnostic: publication already stopped, yet pool and GRADE were omitted. Duplicate, component and checker-crash cases HELD-PRE-FIX. No mutation is represented as bypassing a gate that actually refused it.

## Production route and reuse

Reused DEL's `core` / `publish` boundary and metadata construction from `C:/mh-r-DEL/tests/test_deletion_invariant.py`: real committed records → `pipeline.build_review_core` → deep-copy mutation → `census.build_review_dir(from_cache=True, certify=True)` → renderer/checkers/certificate/manifest → `gate.gate_page`, stopping at a genuine production refusal when it occurs. The original MUT report and test harness were read; its reduced `_build_outcome` pool and fallback renderer were not reused. No extractor, pooler, renderer, gate or evidence verifier is replaced. A wrapper records actual endpoint-admission returns unchanged. The crash test deliberately replaces only the specified checker.

AACT_DIR is an existing empty `.tmp/mut/empty_aact` directory. The output leaf is the topic slug, as required by the production comparator gate's cache lookup. Baseline gates PASS. Both input mutations load edited records from scratch JSON into the real builder's records argument; other inputs remain real committed files. Intermediate mutations deep-copy the real core. Each case clears only its own checked scratch output directory before publishing, so refusal cannot be confused with an older certificate. Network connections are prohibited by the mutation fixture.

## Mutation table

Verbatim refusal strings and measured counts follow. Full pre-fix JSON observations and stdout are retained under `.tmp/mut/pre-fix/`; the snippets below are copied from those observations. All table rows change the permanent test file; only rows 3 and 4 add production checks.

| Mutation | Topic | Pre-fix behaviour (verbatim) | Catch point (file:function) | Post-fix refusal/behaviour (verbatim) | Files changed | State |
|---|---|---|---|---|---|---|
| 1. Duplicate publication | glp1-ra-mace-t2d | {"after": {"families": 11, "k": 8, "screening": 11}, "before": {"families": 11, "k": 8, "screening": 11}, "gate_reasons": []} | harness/pipeline.py:_dedup | {"after": {"families": 11, "k": 8, "screening": 11}, "before": {"families": 11, "k": 8, "screening": 11}, "gate_reasons": []} | tests/test_mutation_production.py | READY |
| 1. Duplicate publication (count-based topic) | colchicine-postop-af | {"after": {"families": 67, "k": 3, "screening": 67}, "before": {"families": 67, "k": 3, "screening": 67}, "gate_reasons": []} | harness/pipeline.py:_dedup | {"after": {"families": 67, "k": 3, "screening": 67}, "before": {"families": 67, "k": 3, "screening": 67}, "gate_reasons": []} | tests/test_mutation_production.py | READY |
| 2. Component endpoint | glp1-ra-mace-t2d | RESULT_INCOMPATIBLE: the bound endpoint span lacks component(s) of the declared composite (myocardial infarction, stroke): a component or subset result is not the composite '3-point major adverse cardiovascular events'; refused rather than pooled under the composite label; PARITY-RELATION REFUSED: hand status 'SUPERSET' disagrees with computed relation OVERLAPPING for glp1-ra-mace-t2d | harness/target_endpoint.py:admissibility; census.build_review_dir parity refusal | RESULT_INCOMPATIBLE: the bound endpoint span lacks component(s) of the declared composite (myocardial infarction, stroke): a component or subset result is not the composite '3-point major adverse cardiovascular events'; refused rather than pooled under the composite label; PARITY-RELATION REFUSED: hand status 'SUPERSET' disagrees with computed relation OVERLAPPING for glp1-ra-mace-t2d | tests/test_mutation_production.py | READY |
| 3. Analysis set | glp1-ra-mace-t2d | L1: offline replay does NOT regenerate the committed numbers (replay 98726cc125e9fcc749601459bce442a9b581ef4cce81c60cf891fa6d643917f7 vs committed b4a1bb48aeea9ffe06a09eb120eae37b70db0be611ad9a74992d35f6c5213d16) | harness/compat_check.py:analysis_set_refusals; certificate.compute; gate.check_compat_key_underlying | ANALYSIS_SET_MISMATCH: PMID 31189511: per-protocol differs from declared intention-to-treat | tests/test_mutation_production.py; harness/{compat_check,certificate,gate}.py | READY |
| 4a. Definition deletion | glp1-ra-mace-t2d | L1: offline replay does NOT regenerate the committed numbers (replay 98726cc125e9fcc749601459bce442a9b581ef4cce81c60cf891fa6d643917f7 vs committed 792189e633d15f684ebe3a79b397042045095abc4030b4d99883c8916ff6fece) | harness/target_endpoint.py:required_support_refusals; certificate.compute; gate.check_compat_key_underlying | MISSING_ENDPOINT_SUPPORT: endpoint_definition_span: PMID 31185157 | tests/test_mutation_production.py; harness/{target_endpoint,certificate,gate}.py | READY |
| 4b. Source deletion | glp1-ra-mace-t2d | L1: offline replay does NOT regenerate the committed numbers (replay 98726cc125e9fcc749601459bce442a9b581ef4cce81c60cf891fa6d643917f7 vs committed 023c99618dae6d8a33ae2a4a939df800ee41c0b0ad3f3ccb8ddadb01e8733582) | harness/target_endpoint.py:required_support_refusals; certificate.compute; gate.check_compat_key_underlying | MISSING_ENDPOINT_SUPPORT: source: PMID 31185157 | tests/test_mutation_production.py; harness/{target_endpoint,certificate,gate}.py | READY |
| 5. Checker crash | colchicine-postop-af | RuntimeError: SYNTHETIC MU significance checker crash | harness/census.py:_claim_check (exception propagates) | RuntimeError: SYNTHETIC MU significance checker crash | tests/test_mutation_production.py | READY |
| 6. CI assertion/dependants | glp1-ra-mace-t2d | CLAIMGRAPH CONTRADICTION (build refused): [{"code": "STALE_DEPENDENT", "kind": "dependent", "claim_id": "glp1-ra-mace-t2d::primary::known_missing_sensitivity", "detail": "/outcomes/0/known_missing_sensitivity depends on d4c04cf5cb5e8b71f722882cb64450765151665d15f73b94386c57184f78d86f, current input_set_version is 132eee1c66f1a352d9a6baba6f90327fbe90ec44ff43c857a9873ad46c0ee40a", "object_path": "/outcomes/0/known_missing_sensitivity"}, {"code": "STALE_DEPENDENT", "kind": "rob_sensitivity_prose", "claim_id": "d2d055eeeffa83a3", "detail": "/claimgraph/objects/0 depends on d4c04cf5cb5e8b71f722882cb64450765151665d15f73b94386c57184f78d86f, current input_set_version is 132eee1c66f1a352d9a6baba6f90327fbe90ec44ff43c857a9873ad46c0ee40a", "object_path": "/claimgraph/objects/0"}, {"code": "STALE_DEPENDENT", "kind": "manuscript_result_sentence", "claim_id": "5aa9ada7ddc5b480", "detail": "/claimgraph/objects/1 depends on d4c04cf5cb5e8b71f722882cb64450765151665d15f73b94386c57184f78d86f, current input_set_version is 132eee1c66f1a352d9a6baba6f90327fbe90ec44ff43c857a9873ad46c0ee40a", "object_path": "/claimgraph/objects/1"}] | harness/claimgraph.py:_scan_dependents | Proposed patch, validated in memory only: CLAIMGRAPH CONTRADICTION (build refused): [{"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "9f9a116aa515dbed", "detail": "/outcomes/0/declared_absent_trials/0 depends on d4c04cf5cb5e8b71f722882cb64450765151665d15f73b94386c57184f78d86f, current input_set_version is 132eee1c66f1a352d9a6baba6f90327fbe90ec44ff43c857a9873ad46c0ee40a", "object_path": "/outcomes/0/declared_absent_trials/0"}, {"code": "STALE_DEPENDENT", "kind": "outcome_result", "claim_id": "4eb11c2f86fc3b6d", "detail": "/outcomes/0/result depends on d4c04cf5cb5e8b71f722882cb64450765151665d15f73b94386c57184f78d86f, current input_set_version is 132eee1c66f1a352d9a6baba6f90327fbe90ec44ff43c857a9873ad46c0ee40a", "object_path": "/outcomes/0/result"}, {"code": "STALE_DEPENDENT", "kind": "dependent", "claim_id": "glp1-ra-mace-t2d::primary::known_missing_sensitivity", "detail": "/outcomes/0/known_missing_sensitivity depends on d4c04cf5cb5e8b71f722882cb64450765151665d15f73b94386c57184f78d86f, current input_set_version is 132eee1c66f1a352d9a6baba6f90327fbe90ec44ff43c857a9873ad46c0ee40a", "object_path": "/outcomes/0/known_missing_sensitivity"}, {"code": "STALE_DEPENDENT", "kind": "rob_sensitivity.full", "claim_id": "70ddee3eebdc2787", "detail": "/rob_sensitivity/full depends on d4c04cf5cb5e8b71f722882cb64450765151665d15f73b94386c57184f78d86f, current input_set_version is 132eee1c66f1a352d9a6baba6f90327fbe90ec44ff43c857a9873ad46c0ee40a", "object_path": "/rob_sensitivity/full"}, {"code": "STALE_DEPENDENT", "kind": "rob_sensitivity.drop_high", "claim_id": "d42d6fa0d4c18b75", "detail": "/rob_sensitivity/drop_high depends on d4c04cf5cb5e8b71f722882cb64450765151665d15f73b94386c57184f78d86f, current input_set_version is 132eee1c66f1a352d9a6baba6f90327fbe90ec44ff43c857a9873ad46c0ee40a", "object_path": "/rob_sensitivity/drop_high"}, {"code": "STALE_DEPENDENT", "kind": "rob_sensitivity.low_only", "claim_id": "ac4eeed281c97ce6", "detail": "/rob_sensitivity/low_only depends on d4c04cf5cb5e8b71f722882cb64450765151665d15f73b94386c57184f78d86f, current input_set_version is 132eee1c66f1a352d9a6baba6f90327fbe90ec44ff43c857a9873ad46c0ee40a", "object_path": "/rob_sensitivity/low_only"}, {"code": "STALE_DEPENDENT", "kind": "grade", "claim_id": "21b78426ef9a7f37", "detail": "/grade depends on d4c04cf5cb5e8b71f722882cb64450765151665d15f73b94386c57184f78d86f, current input_set_version is 132eee1c66f1a352d9a6baba6f90327fbe90ec44ff43c857a9873ad46c0ee40a", "object_path": "/grade"}, {"code": "STALE_DEPENDENT", "kind": "rob_sensitivity_prose", "claim_id": "d2d055eeeffa83a3", "detail": "/claimgraph/objects/0 depends on d4c04cf5cb5e8b71f722882cb64450765151665d15f73b94386c57184f78d86f, current input_set_version is 132eee1c66f1a352d9a6baba6f90327fbe90ec44ff43c857a9873ad46c0ee40a", "object_path": "/claimgraph/objects/0"}, {"code": "STALE_DEPENDENT", "kind": "manuscript_result_sentence", "claim_id": "5aa9ada7ddc5b480", "detail": "/claimgraph/objects/1 depends on d4c04cf5cb5e8b71f722882cb64450765151665d15f73b94386c57184f78d86f, current input_set_version is 132eee1c66f1a352d9a6baba6f90327fbe90ec44ff43c857a9873ad46c0ee40a", "object_path": "/claimgraph/objects/1"}] | tests/test_mutation_production.py; .tmp/patches/source-dependants.diff (not applied) | READY-BEHIND-ELX |

## Source-dependency inventory

The synthetic edit changes PMID 31185157's real core `ci_high` from 1.11 to 1.12 (one unit of the last displayed decimal). Neither value is presented as a new scientific finding. The stale core is not safe to recompute by merely restamping derived objects. A refused build must issue neither a new certificate nor a new manifest. The following is the exact pre-fix inventory:

```json
{
  "row": "PMID 31185157",
  "before_ci_high": "1.11",
  "after_ci_high": 1.12,
  "dependants": {
    "source.input_set_version": "CHANGED",
    "pool.input_set_version": "UNCHANGED",
    "pool.claim_id": "UNCHANGED",
    "pool.result": "UNCHANGED",
    "grade.input_set_version": "UNCHANGED",
    "grade.imprecision": "UNCHANGED",
    "claim_objects": "UNCHANGED",
    "certificate.release_sha256": "NOT_ISSUED",
    "manifest.review_sha256": "NOT_ISSUED"
  },
  "refusal": "CLAIMGRAPH CONTRADICTION (build refused): [{\"code\": \"STALE_DEPENDENT\", \"kind\": \"dependent\", \"claim_id\": \"glp1-ra-mace-t2d::primary::known_missing_sensitivity\", \"detail\": \"/outcomes/0/known_missing_sensitivity depends on d4c04cf5cb5e8b71f722882cb64450765151665d15f73b94386c57184f78d86f, current input_set_version is 132eee1c66f1a352d9a6baba6f90327fbe90ec44ff43c857a9873ad46c0ee40a\", \"object_path\": \"/outcomes/0/known_missing_sensitivity\"}, {\"code\": \"STALE_DEPENDENT\", \"kind\": \"rob_sensitivity_prose\", \"claim_id\": \"d2d055eeeffa83a3\", \"detail\": \"/claimgraph/objects/0 depends on d4c04cf5cb5e8b71f722882cb64450765151665d15f73b94386c57184f78d86f, current input_set_version is 132eee1c66f1a352d9a6baba6f90327fbe90ec44ff43c857a9873ad46c0ee40a\", \"object_path\": \"/claimgraph/objects/0\"}, {\"code\": \"STALE_DEPENDENT\", \"kind\": \"manuscript_result_sentence\", \"claim_id\": \"5aa9ada7ddc5b480\", \"detail\": \"/claimgraph/objects/1 depends on d4c04cf5cb5e8b71f722882cb64450765151665d15f73b94386c57184f78d86f, current input_set_version is 132eee1c66f1a352d9a6baba6f90327fbe90ec44ff43c857a9873ad46c0ee40a\", \"object_path\": \"/claimgraph/objects/1\"}]",
  "gate_reasons": null
}
```

The existing check refuses through known-missing sensitivity and two claimgraph prose objects, while trusting an object's own cached `input_set_version` as its current version. That self-comparison misses `/outcomes/0/result`, `/grade` (including imprecision), and the three RoB sensitivity objects. The ELX patch compares these to independently recomputed source versions. With the proposed patch loaded into the production module in memory, the same full production tests pass with `--runxfail`; the protected source file is untouched. The strict xfail remains on disk, names `.tmp/patches/source-dependants.diff`, and requires explicit stale refusals for both the result and GRADE plus both claim objects. It cannot pass just because a sibling object happened to stop the build.

**Contract boundary:** the intermediate-core mutation is refused before certificate/manifest issuance; it does not produce refreshed estimates, GRADE or claim identities. The prompt's requested “each changed” success condition is therefore not claimed. For this already-refused source edit the permanent contract accepts explicit invalidation of each dependant; successful re-analysis from revised validated source records is outside this mutation. The patch fixes diagnostic coverage, not an observed stale public release. This is why mutation 6 remains behind ELX rather than being called READY.

## Real versus synthetic inputs / static versus dynamic disclosure

| Case / item | Static or synthetic | Real/dynamic evidence |
|---|---|---|
| Duplicate | New test-only publication ID 99999998; no synthetic NCT or effect | Whole committed report copied, same real NCT, title, dates and numbers; production dedup and family/screening counts measured |
| Component | Replace only `The primary outcome` by `Cardiovascular death` in one abstract result sentence | PMID 27633186's held abstract; HR and CI tokens unchanged; actual admission refusal and k measured |
| Analysis | Replace ITT by per-protocol in the stored source span and its analysis-set scalars | PMID 31189511's real REWIND span and outcome's declared ITT population |
| Support | Delete one key at a time | PMID 31185157's existing source/definition span; remaining core unchanged |
| Crash | RuntimeError text and injected raising function | Real count-topic core and production significance-check call; one call then build refusal |
| CI assertion | +1 last-decimal unit computed with Decimal | Real pooled row, existing versions/claims, generated refusal objects; no made-up numeric output |
| Production policy | Named refusal codes, supported binding kinds, explicit ITT/per-protocol conflict rule | Checks read every published row; no precomputed topic findings |
| Test date/selection | Frozen build date 2026-09-11; topic and record selectors | Source records loaded from disk; identifiers and NCT links checked against those records |

The pre-fix full run used span plus scalar edits for analysis. A supplementary post-fix run changed the span alone while retaining the old ITT scalar and also refused; the final permanent case preserves the original pre-fix plant. Unknown or modified-ITT populations are not newly generalized into a strict equality policy.

## Scope effects and verification

There are no extraction, pooling or numeric-transformation changes. The final support and analysis checks passed on 32 of 32 committed reviews. The first analysis-check implementation was too strict about two already-disclosed mixed populations and produced these refusals during the first full suite:

```text
ANALYSIS_SET_MISMATCH: PMID 21830957: per-protocol differs from declared intention-to-treat
ANALYSIS_SET_MISMATCH: PMID 32035998: per-protocol differs from declared intention-to-treat
```

These belong respectively to `noac-vs-warfarin-af-stroke` and `probiotics-aad-prevention`. Both already declare mixed analysis populations with `dimension_matches.analysis_set=false` and `COMPAT_DIMENSION_HETEROGENEOUS`. The final new check respects this explicit degradation only when the rendered mix exactly matches the current row counts and the row scalar agrees with its axis. A silently altered GLP-1 span still refuses under its uniform ITT declaration. No pre-existing gate was weakened. Source-level second-pass review also found that the ROCKET selected result span explicitly says ITT while its compatibility axis points to a separate PP analysis, and the probiotic axis derives PP from “followed up as per protocol”; neither should be treated as proof that the selected estimate truly uses PP. The source metadata were not rewritten.

The 32-review scan is not a 32-page regeneration or a claim of 32 fresh gate passes. No committed page numbers moved, and no full-corpus certification is claimed. The base did not contain the advertised DEL `MISSING_ENDPOINT_SUPPORT` check (`rg` across harness found no occurrence before edits); the minimal shared check is consequently included here rather than assuming the advertised landing.

The proposed ELX patch additionally preserves strand-local source versions. A second-pass comparison of `_scan_dependents` on all 32 committed review objects found zero newly introduced refusals after that correction (`.tmp/mut/patch-corpus.json` is `[]`). This is diagnostic coverage, not a 32-topic rebuild.

Production changes: `harness/target_endpoint.py`, `harness/compat_check.py`, `harness/certificate.py`, `harness/gate.py`. New refusal checks only; no existing gate weakened. ELX/CHK-owned files untouched. Scratch reports, logs and proposed patch are local evidence artifacts. Tests write no committed docs/cache inputs.


`pre-fix/pytest` summary (verbatim):

```text
4 failed, 5 passed in 53.00s
```


`focused` summary (verbatim):

```text
8 passed, 1 xfailed in 43.07s
```


`patch-run` summary (verbatim):

```text
9 passed in 86.84s (0:01:26)
```


`full` summary (verbatim):

```text
4 failed, 978 passed, 1 xfailed in 949.72s (0:15:49)
```

```text
FAILED tests/test_certificate.py::test_all_certificate_inputs_and_manuscript_match
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
FAILED tests/test_gate.py::test_real_review_reproduces_and_passes_full_gate
FAILED tests/test_gate_scorecard.py::test_real_registry_passes - AssertionErr...
```


`base-failures-run` summary (verbatim):

```text
1 failed, 3 passed in 233.35s (0:03:53)
```

```text
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
```


`post-full-targeted` summary (verbatim):

```text
11 passed, 1 xfailed in 107.32s (0:01:47)
```


`final-focused` summary (verbatim):

```text
8 passed, 1 xfailed in 89.45s (0:01:29)
```


The complete suite was run once. Its four-failure summary is retained verbatim above, including the initial over-strict analysis declarations and the initially unregistered new gate entry point. The added checks now run within the existing registered compatibility gate. The affected certificate/gate/scorecard tests were rerun after correction; their actual result is recorded separately, not represented as a second complete suite. One remaining full-suite blocker is `tests/test_fixstate.py::test_real_store_validates`: `docs/fix_ledger.json is stale; run python scripts/render_fix_ledger.py`. It persists with base implementations loaded in memory, but that does not restore disk dependencies and is not proof of a clean-base failure. See STUCK_FAILURES.md. No registry/ledger assurance state was regenerated or promoted outside lane ownership.

The exact required focused command is `python -X utf8 -m pytest tests/test_mutation_production.py -q -p no:cacheprovider`. Python compilation and scoped `git diff --check` pass. `git diff --quiet -- docs cache` and the same check for all seven protected production files both return 0; an existing test rewrote the compatibility audit JSON with different line endings, but its Git-normalized content is unchanged. No committed review page was regenerated. The final diff is confined to the four owned production modules, the permanent test and local report/blocker artifacts.

MEASURED means the logged production executions, source-loaded fields, actual gate reasons and on-disk diff. INFERRED means the generic checks should cover analogous rows; no untested route is certified. CLAIMED means the scoped local checks and strict ELX handoff only, not SHIP, Overmind PASS, a clean full corpus or refreshed scientific results. No commit.
