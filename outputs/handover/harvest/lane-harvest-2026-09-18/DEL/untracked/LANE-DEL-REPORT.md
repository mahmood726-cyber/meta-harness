# Deletion-invariant increment

**MEASURED:** HEAD `237e90946f5b257265b0a3b1c986a8907d12eded`. No commit, reset, checkout, stash, push, or external network request. Initial tracked worktree was clean. Existing untracked lane files were left alone. No committed research input was edited. No project/submission status was promoted.

**MEASURED:** 10 of 12 production-boundary cases were constructed and fired before the fix; all 10 now hold. The other 2 of 12 are NOT_CONSTRUCTIBLE in the topic builder's function chain: search completeness is a separate release gate. Both corresponding real standalone deletions already held. These are not reported as 12 passing production cases.

## Production route and ingredient proof

Topics: `glp1-ra-mace-t2d` (G) and `sacubitril-valsartan-hfref` (S).

The test uses the actual builder functions: committed `topics/<slug>.json` and `cache/<slug>/records.json` -> `pipeline.build_review_core` -> `census.build_review_dir(..., from_cache=True, certify=True)` -> production page renderer, claim checks, certificate and manifest. Metadata matches `scripts/build_topic.py`, including `build_utc=2026-09-11`, declared/served methods, comparator fields and `registration.protocol_sha`. Reading the existing records directly avoids the fetch function's network fallback. Scratch publication directories are below `.tmp/del/`.

The binding fields on this tree are named `endpoint_definition_span` and `endpoint_result_span`, not bare `definition_span` and `result_span`. Verified on real generated rows: G selects `PMID 31185157`; S selects `NCT02468232`. The committed source records and production extraction provide their identities and spans; the test invents neither. The real intermediate GRADE object has all five domains, including indirectness, for both topics.

The verified-effect cache files actually read are `cache/glp1-ra-mace-t2d/verified_effects.json` and `cache/sacubitril-valsartan-hfref/verified_effects.json`. Deleted keys are respectively `40162642` and `25176015`, verified present before deletion. Each entire topic cache is copied; external `document_ref` files are also copied. Only the verified-input loader is redirected to those scratch inputs; other production inputs stay fixed. There is no substitute extractor or pooler.

Search registration is `registry/search_completeness.json`; its actual candidate file is `outputs/search_v2/candidates-2026-09-15r3-all.json`. Both exist. The separate `search_completeness.check` consumes these; `build_topic.py` does not. The supplemental test copies and deletes the actual registered candidate file and checks its exact refusal before recording the production-route skip.

The reproduction retraction is generated in `harness/limitations.py::build_limitations`, with kind `REPRODUCTION_RETRACTION` and topic-prefixed ID ending `reproduction:round-2-retraction`. Its object is consumed downstream in publication. Both topics have it. The test deletes that real generated input object, not the policy's Python source. The separate retrieval withdrawal, “We retract”, comes from `pipeline.RETRIEVAL_RETRACTION` and search-provenance rendering; it is included in the marking-count check but its source is not separately deleted here.

## Twelve-case table

Real intermediate means deletion from a deep scratch copy of the actual production core immediately before the production publication function. It is not a synthetic clinical fixture. Real cache means deletion from copied on-disk inputs before production extraction. No synthetic clinical supplement was used.

| Topic | Deleted object / construction | Pre-fix | Post-fix | Exact assertion / observed outcome |
|---|---|---|---|---|
| G | `PMID 31185157.endpoint_definition_span`; real intermediate | FIRED | HELD, typed refusal | `ValueError` exactly `MISSING_ENDPOINT_SUPPORT: endpoint_definition_span: PMID 31185157`; otherwise no `EXACT_TARGET` trial may lack that span. Pre-fix retained EXACT_TARGET. |
| S | `NCT02468232.endpoint_definition_span`; real intermediate | FIRED | HELD, typed refusal | Exactly `MISSING_ENDPOINT_SUPPORT: endpoint_definition_span: NCT02468232`; same surviving-EXACT_TARGET assertion. |
| G | `PMID 31185157.endpoint_result_span`; real intermediate | FIRED | HELD, typed refusal | Exactly `MISSING_ENDPOINT_SUPPORT: endpoint_result_span: PMID 31185157`; otherwise no EXACT_TARGET trial may lack that span. |
| S | `NCT02468232.endpoint_result_span`; real intermediate | FIRED | HELD, typed refusal | Exactly `MISSING_ENDPOINT_SUPPORT: endpoint_result_span: NCT02468232`; same surviving-EXACT_TARGET assertion. |
| G | `grade.domains.indirectness`; real intermediate | FIRED | HELD, typed refusal | Exactly `MISSING_GRADE_DOMAIN: indirectness`; otherwise indirectness must still be present in the published GRADE domains. Pre-fix silently published the incomplete domain object. |
| S | `grade.domains.indirectness`; real intermediate | FIRED | HELD, typed refusal | Same exact refusal and assertion. No claim that this zero-downgrade domain deletion increased numerical certainty. |
| G | Verified-effects key `40162642`; real cache | FIRED, unrelated refusal | HELD, typed refusal | Exactly `MISSING_VERIFIED_EFFECT: glp1-ra-mace-t2d/40162642`; otherwise primary `k_after < k_before`. Pre-fix produced `PARITY-RELATION REFUSED: hand status 'SUPERSET' disagrees with computed relation OVERLAPPING for glp1-ra-mace-t2d`, which does not name the missing support and is not accepted. |
| S | Verified-effects key `25176015`; real cache | FIRED | HELD, typed refusal | Exactly `MISSING_VERIFIED_EFFECT: sacubitril-valsartan-hfref/25176015`; otherwise primary `k_after < k_before`. Pre-fix kept k=2 after deletion (2 is a measured pipeline value, not a fixture). |
| G | Registered candidate file; real standalone supplement | NOT_CONSTRUCTIBLE in topic route; standalone HELD | Same | `ok == False` and reason exactly `COULD-NOT-EXECUTE: registered file missing: outputs/search_v2/candidates-2026-09-15r3-all.json`; then explicit pytest skip. |
| S | Same global candidate file; repeated under second topic | NOT_CONSTRUCTIBLE in topic route; standalone HELD | Same | Same exact assertion. These are two table positions, not two independent candidate datasets. |
| G | `REPRODUCTION_RETRACTION` limitation; real intermediate | FIRED | HELD, marking restored | Every `scripts/retraction_survival.MARKS` count after stripping HTML must be >= baseline; structured outcomes/GRADE/claimgraph and reproduction claim/proposition/claimgraph checks must equal baseline. Pre-fix lost a RETRACTED marking. |
| S | Same limitation kind; real intermediate | FIRED | HELD, marking restored | Same marking and structured-assurance assertions. Pre-fix lost a RETRACTED marking. |

For the 2 of 10 constructed cases that complete instead of refusing, an additional inspection found both `review_sha256` and `html_sha256` identical to their respective unmutated scratch baselines. Thus their published review/manifest content and HTML assurance surfaces are unchanged, not merely selected numeric fields. The test's equality checks are a conservative contract, not a general implementation of a partial ordering over arbitrary verdicts or arbitrary changing pools. The other 8 of 10 use exact named refusals; unrelated exceptions fail the tests.

## Fix and bounded verification

Final harness diff: **2 files, +44/-0 lines**.

| File | +/- | Decision owned |
|---|---:|---|
| `harness/census.py` | +21/-0 | Before publication, refuse classified pooled rows without binding spans and incomplete supplied GRADE domain maps. Restore the standing reproduction withdrawal before hashing/rendering if its limitation object was deleted. |
| `harness/verified_inputs.py` | +23/-0 | Compare loaded verified-effect trial/outcome identities with the same file in the fixed committed HEAD snapshot. Refuse deleted identities before fallback extraction can reactivate. No new module. |

Reason codes are `MISSING_ENDPOINT_SUPPORT`, `MISSING_GRADE_DOMAIN`, `MISSING_VERIFIED_EFFECT`, and `VERIFIED_SNAPSHOT_UNAVAILABLE`. They are typed reason prefixes in `ValueError`, not new exception classes. The last code covers failure to read the Git snapshot and is not one of the planted deletion outcomes. New untracked topics have no prior tracked snapshot to compare. A deleted tracked file or deleted tracked trial/outcome entry does not silently become an empty fallback cache.

The first construction run found two setup mistakes, not extra harness defects: the limitation ID is topic-prefixed, and one copied GLP-1 cache references a held document under `outputs/`. Those were corrected while all harness code was still untouched. Its output is preserved in `.tmp/del/prefix_construction_errors.txt`. The authoritative pre-fix run follows those corrections. Assertions were not loosened after the fix.

The first harness attempt put the snapshot check in `pipeline.py`. Broader verification correctly failed because that file is in the existing certificate code-hash list, invalidating untouched topics' certificates. The check was moved to its existing input-loader owner; `pipeline.py` has no final diff. Failed attempts remain in `.tmp/del/unit_attempt1.txt` and `.tmp/del/custody_attempt1.txt`. Two implementation verification attempts were used, within a cap of three; no failure remains unresolved in the checks below.

Verbatim pytest tail lines:

```text
# .tmp/del/prefix_pytest.txt, untouched harness
======================= 10 failed, 2 skipped in 25.31s ========================
# .tmp/del/postfix_pytest.txt, first implementation family run
======================= 10 passed, 2 skipped in 28.40s ========================
# .tmp/del/final_pytest.txt, final implementation family run
================== 10 passed, 2 skipped in 61.09s (0:01:01) ===================
# .tmp/del/unit_pytest.txt
177 passed, 2 skipped, 807 deselected in 130.59s (0:02:10)
# .tmp/del/custody_pytest.txt
26 passed in 28.43s
```

The selected-suite command was `python -m pytest tests -q -x -p no:cacheprovider -k "endpoint or grade or pipeline or page or gate or deletion"`, with a workspace scratch `--basetemp`. Additional coverage ran `test_certificate.py`, `test_in2_verified_inputs.py`, `test_verified_effects.py`, and `test_verified_override.py`. These counts overlap and must not be added as distinct tests. Imports, real input files, baseline builds and output targets were checked before mutation. `git diff --check` passes.

Local browser E2E: **2 of 2** rebuilt topics passed at `127.0.0.1:8000`, with external requests blocked. Checked HTTP success, visible certificate, certificate object equality, download equality, retained round-2 withdrawal, and no page errors. Browser and server were closed individually. Evidence: `.tmp/del/ui_check.py` and `.tmp/del/ui_check.txt`.

## Rebuild and served marking survival

**MEASURED:** rebuilt ONLY the two requested real output directories using the same production function chain, with `2026-09-11` metadata. Neither review nor HTML hash moved (0 of 4 hash fields moved). The generated artifacts have no Git diff. No remote deployment was attempted or claimed.

| Topic | `review_sha256`, before = after | `html_sha256`, before = after |
|---|---|---|
| G | `98726cc125e9fcc749601459bce442a9b581ef4cce81c60cf891fa6d643917f7` | `fede8d293caffb87dfc915f1540baad49ce59c0f67b03ec688cfd0555bbc6725` |
| S | `04b07291943df879080bdfd052eaa56560a659a9cba5a849d614ebc95b79a9e1` | `416d34d4a7a3eb5e5c511272bffc30255e06c28d0ad2f25574fa21b5087f71d3` |

Evidence: `.tmp/del/rebuild.py`, `.tmp/del/rebuild_hashes.json`.

`python scripts/retraction_survival.py 237e9094` exited 0 and printed:

```text
pages with every marking kept (count >= base): 32 of 32
```

Evidence: `.tmp/del/retraction_survival.txt`. The STOP condition did not trigger.

## Static versus dynamic disclosure and limits

| Item | Static or dynamic | Disclosure |
|---|---|---|
| Test topics, IDs, field names, date and refusal strings | Static test selection | All selected objects were verified in real committed inputs or real generated intermediates. No fabricated effect, date or study identifier. |
| Pooled estimates, k, grades, claims, certificates, hashes and HTML | Dynamic | Read or produced by the production functions from held inputs. |
| Reproduction withdrawal | Static policy, dynamically rendered | Existing policy in `limitations.py`; this fix preserves it rather than inventing a clinical conclusion. |
| Expected verified membership | Dynamic Git read | Compared against HEAD's tracked file; no hardcoded row list or local machine path in harness code. |

**INFERRED from these measurements:** the tested deletions cannot silently preserve the unsupported span/domain publications, reactivate the tested fallback paths, or remove the tested reproduction marking under this fixed snapshot. The original normal inputs remain byte-stable.

**NOT ESTABLISHED / NOT CLAIMED:** a universal deletion theorem; coverage of every trial/domain/topic; deletion of entire GRADE/limitations blocks; tampered rather than missing spans; re-binding semantic validity; deletion of the Python policy itself; all search denominators integrated into topic publication; monotonicity across changed protocols or newly committed snapshots. The Git guard anchors HEAD, so committing a deletion changes that anchor; it is not a historical registry or an approval mechanism. It requires readable Git metadata for tracked snapshots. The existing certificate's code list omits the two changed modules; this increment does not expand that pre-existing code-coverage claim. No new clinical efficacy claim, complete-suite PASS, Overmind certification, release, or remote hash movement is claimed.
