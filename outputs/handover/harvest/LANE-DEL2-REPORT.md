# LANE DEL2 report

**MEASURED:** HEAD `237e90946f5b257265b0a3b1c986a8907d12eded` matches the requested base. No project commit, reset, checkout, stash, push, deployment, or research-input edit. The initial tracked tree was clean; initial untracked lane files remain. Production changes are confined to **58 added lines in harness/certificate.py**, in two new check functions and their call sites. No other lane's implementation was copied or edited.

**MEASURED:** 10 of 10 constructed source-support plants now hold. Six exposed gaps on the untouched base; four controls already refused. Two of 32 committed review topics are exercised: GLP-1 and colchicine recurrent pericarditis. Adjudication deletion/alteration is **NOT_CONSTRUCTIBLE**: 0 of 32 reviews cite an ADJ id. No synthetic adjudication was grafted onto a real review.

## Route, ingredients and pre-fix findings

The read-only DEL test/report and AUD2 design were read first. Tests use committed topic configuration and records -> `pipeline.build_review_core` -> a deep copy at `census.build_review_dir(..., from_cache=True, certify=True)`. Metadata follows the production builder, including its build date and protocol anchor. Cache mutations redirect only the verified-input loader to a scratch copy. Certificate inputs and held documents are also copied and certificate.ROOT is redirected to that tree. Baseline production builds precede every mutation.

`AACT_DIR` resolves to the existing empty `.tmp/empty_aact`. No fetch/acquisition command was requested. Python external connections and DNS are denied by the scratch runner; browser requests outside loopback are aborted. All rebuilds remain under `.tmp/del2/`, never docs/.

The selected source identities, outcome names, document digests, committed row states, and source-record titles were checked against both committed reviews and held records in `.tmp/del2/evidence.json`. Both selected pooled rows are `verified`; both selected refusal rows are `REFUSED_ON_EVIDENCE`. Selection is from actual input entries, not fabricated research data. The GLP-1 text control additionally cites the real `ft_27295427.txt` digest.

The retained pre-fix rebuilt rows were also inspected directly (`pre-surviving-rows.json`): both pooled rows remained verified and both refusal rows remained REFUSED_ON_EVIDENCE after their document_sha256 became null/absent. This confirms survival of the unsupported row state, in addition to the unchanged aggregate/certificate diagnostics in the table.

**MEASURED source inspection:** neither `verify.verify_pooled` nor `integrity.py` reads document_sha256 on this base. The existing input loader validates source-span presence, not that field. Certificates bind held text bytes, but canonical hashing of records.json excludes whitespace. Therefore deleting the digest field from a pooled/refused input still rebuilt and certified, and a one-byte whitespace substitution in records.json was invisible. Existing held-text deletion and corruption checks already refused; these are controls, not claimed new pre-fix defects.

## Case table

The pre/post cells below are verbatim retained output. Scratch directory names in the pre-fix missing-JSON exception are part of the actual measurement.

| Object | Topic | Construction | Pre-fix (verbatim) | Catch point | Post-fix (verbatim) | Status |
|---|---|---|---|---|---|---|
| Delete document_sha256: extracted_counts, PMID 31189511 | glp1-ra-mace-t2d | real copied cache | `glp1-ra-mace-t2d/extracted_counts: SURVIVED; k=[8, 1, 1]; grade_equal=True; gate_equal=True; certificate=[]` | certificate.compute -> _require_retained_document_digests | `glp1-ra-mace-t2d/extracted_counts: REFUSED: MISSING_DOCUMENT_SHA256: cache/glp1-ra-mace-t2d/verified_arms.json/31189511/Gastrointestinal adverse events` | READY |
| Delete document_sha256: extracted_counts, PMID 24694983 | colchicine-recurrent-pericarditis | real copied cache | `colchicine-recurrent-pericarditis/extracted_counts: SURVIVED; k=[2, 1, None, 1, None]; grade_equal=True; gate_equal=True; certificate=[]` | certificate.compute -> _require_retained_document_digests | `colchicine-recurrent-pericarditis/extracted_counts: REFUSED: MISSING_DOCUMENT_SHA256: cache/colchicine-recurrent-pericarditis/verified_arms.json/24694983/Adverse events (gastrointestinal)` | READY |
| Delete document_sha256: typed_refusal, PMID 31185157 | glp1-ra-mace-t2d | real copied cache | `glp1-ra-mace-t2d/typed_refusal: SURVIVED; k=[8, 1, 1]; grade_equal=True; gate_equal=True; certificate=[]` | certificate.compute -> _require_retained_document_digests | `glp1-ra-mace-t2d/typed_refusal: REFUSED: MISSING_DOCUMENT_SHA256: cache/glp1-ra-mace-t2d/verified_effects.json/31185157/Gastrointestinal adverse events` | READY |
| Delete document_sha256: typed_refusal, PMID 23992557 | colchicine-recurrent-pericarditis | real copied cache | `colchicine-recurrent-pericarditis/typed_refusal: SURVIVED; k=[2, 1, None, 1, None]; grade_equal=True; gate_equal=True; certificate=[]` | certificate.compute -> _require_retained_document_digests | `colchicine-recurrent-pericarditis/typed_refusal: REFUSED: MISSING_DOCUMENT_SHA256: cache/colchicine-recurrent-pericarditis/verified_effects.json/23992557/Adverse events (gastrointestinal)` | READY |
| delete held records.json | glp1-ra-mace-t2d | real copied held tree | `glp1-ra-mace-t2d/delete: ["CERTIFICATE.json release_sha256 could not be verified: [Errno 2] No such file or directory: 'C:\\\\mh-w-DEL2\\\\.tmp\\\\del2\\\\pre2\\\\test_held_document_delete_glp10\\\\cache\\\\glp1-ra-mace-t2d\\\\records.json'"]` | certificate.verify -> _verify_document_bindings | `glp1-ra-mace-t2d/records.json/delete: ['CERTIFICATE.json release_sha256 could not be verified: HELD_DOCUMENT_MISSING: cache/glp1-ra-mace-t2d/records.json']` | READY |
| corrupt held records.json | glp1-ra-mace-t2d | real copied held tree | `glp1-ra-mace-t2d/corrupt: []` | certificate.verify -> _verify_document_bindings | `glp1-ra-mace-t2d/records.json/corrupt: ['CERTIFICATE.json release_sha256 could not be verified: DOCUMENT_SHA256_MISMATCH: cache/glp1-ra-mace-t2d/records.json']` | READY |
| delete held records.json | colchicine-recurrent-pericarditis | real copied held tree | `colchicine-recurrent-pericarditis/delete: ["CERTIFICATE.json release_sha256 could not be verified: [Errno 2] No such file or directory: 'C:\\\\mh-w-DEL2\\\\.tmp\\\\del2\\\\pre2\\\\test_held_document_delete_colc0\\\\cache\\\\colchicine-recurrent-pericarditis\\\\records.json'"]` | certificate.verify -> _verify_document_bindings | `colchicine-recurrent-pericarditis/records.json/delete: ['CERTIFICATE.json release_sha256 could not be verified: HELD_DOCUMENT_MISSING: cache/colchicine-recurrent-pericarditis/records.json']` | READY |
| corrupt held records.json | colchicine-recurrent-pericarditis | real copied held tree | `colchicine-recurrent-pericarditis/corrupt: []` | certificate.verify -> _verify_document_bindings | `colchicine-recurrent-pericarditis/records.json/corrupt: ['CERTIFICATE.json release_sha256 could not be verified: DOCUMENT_SHA256_MISMATCH: cache/colchicine-recurrent-pericarditis/records.json']` | READY |
| delete held ft_27295427.txt | glp1-ra-mace-t2d | real copied held tree | `glp1-ra-mace-t2d/ft_27295427.txt/delete: ['CERTIFICATE.json release_sha256 could not be verified: held document missing: cache/glp1-ra-mace-t2d/ft_27295427.txt']` | certificate.verify -> _verify_document_bindings | `glp1-ra-mace-t2d/ft_27295427.txt/delete: ['CERTIFICATE.json release_sha256 could not be verified: HELD_DOCUMENT_MISSING: cache/glp1-ra-mace-t2d/ft_27295427.txt']` | READY |
| corrupt held ft_27295427.txt | glp1-ra-mace-t2d | real copied held tree | `glp1-ra-mace-t2d/ft_27295427.txt/corrupt: ['CERTIFICATE.json release_sha256 mismatch: recomputed 488a2ce1fa5ff6bacad51e7d09da7f421fa60b5570f6b7a52114cacef9e49504 vs saved db4238e4abf61292c8955df5666e7b625323d12f7bf7bf8873d5db8dec56144a']` | certificate.verify -> _verify_document_bindings | `glp1-ra-mace-t2d/ft_27295427.txt/corrupt: ['CERTIFICATE.json release_sha256 could not be verified: DOCUMENT_SHA256_MISMATCH: cache/glp1-ra-mace-t2d/ft_27295427.txt']` | READY |
| Delete / alter cited ADJ record | all committed reviews | no citing row to mutate | `ADJ citations: 0 of 32 reviews; 0 of 555 cache JSON files; handover records present` | working-tree scan plus git grep HEAD | `0 of 32 reviews; 0 of 933 tracked cache JSON files` | NOT_CONSTRUCTIBLE |

## Checks and monotonicity

`_require_retained_document_digests` compares each existing input row's PMID/outcome identity with its committed HEAD entry. If that entry carried a digest, an absent/empty field now refuses the build with `MISSING_DOCUMENT_SHA256`, before a replacement HTML page or certificate is written. Missing/unreadable tracked snapshot evidence refuses with `DOCUMENT_DIGEST_SNAPSHOT_UNAVAILABLE`. Previously unbound legacy entries are not silently reclassified as bound; new untracked input files have no historical deletion anchor.

`_verify_document_bindings` validates exact file bytes against saved held-document bindings and the input's declared digest. It checks records.json bytes as well as held text/JSON. For regulatory PDF/text pairs it uses the explicit extracted_text_sha256 for the text reference; the saved held-document list separately protects the held PDF. Missing documents and mismatches have deterministic, file-specific refusal codes.

Every constructed case compares gate reasons, the complete GRADE object, pooled k for every outcome, and certificate state. For file plants the gate reason set must be a superset, GRADE and k must remain equal, and a previously valid certificate must refuse with the exact named reason. For digest-field plants the accepted result is the exact build refusal and no replacement page/certificate. This is the explicitly permitted refusal branch, not a claim that k numerically decreases. Complete compared snapshots are retained as `DEL2_STATES.jsonl` under `.tmp/del2/final/`.

## Adjudication evidence

Disk scan: **0 of 32 reviews**, **0 of 555 present cache JSON files** contain ADJ-. The sparse checkout omits some historical files, so `git grep -n ADJ- HEAD -- cache docs/reviews/*/review.json` also inspected the committed snapshot and returned exit 1/no matches: **0 of 32 reviews and 0 of 933 tracked cache JSON files**. Both denominators are reported separately.

`outputs/handover/glp1_reviewerB/ADJUDICATIONS.json` contains `ADJ-GLP1-001` and `ADJ-GLP1-002`. Both records explicitly have applied_to_served_page=false and the handover signature is OWED. Since no citing row exists, deleting/changing these records cannot be presented as a real citing-row deletion plant. No adjudication_sha256 field was invented on unciting objects. The inventory test skips with a named NOT_CONSTRUCTIBLE reason and will fail if citations appear without adding the required plants.

## Verification

Verbatim summary lines:

```text
# Untouched production code, corrected test setup: .tmp/del2/pre-fixed-setup.txt
6 failed, 2 passed, 1 skipped in 211.30s (0:03:31)
# Additional untouched held-text controls: .tmp/del2/pre-text.txt
2 passed, 9 deselected in 73.10s (0:01:13)
# Post-fix diagnostics: .tmp/del2/post.txt
10 passed, 1 skipped in 241.85s (0:04:01)
# Final lane command: .tmp/del2/final.txt
10 passed, 1 skipped in 286.91s (0:04:46)
# Full suite: .tmp/del2/full-suite-offline.txt
2 failed, 982 passed, 1 skipped in 1399.88s (0:23:19)
```

Final lane command: `python -X utf8 -m pytest tests/test_deletion_invariant_digest_adjudication.py -q -p no:cacheprovider --basetemp=.tmp/del2/final`. Full suite uses `tests -q -p no:cacheprovider --basetemp=.tmp/del2/full-offline`. The scratch runner only sets the offline/empty-AACT environment and captures UTF-8 output. The earlier full-suite attempt was interrupted while tightening DNS denial and is not counted as a complete result.

The initial construction run (`pre.txt`) had two setup errors: optional effect_type.py is deliberately NOT_PRESENT, and the refusal collection is declared_absent_trials. Both were corrected before any production change. The authoritative pre-fix runs above exclude those setup failures. There was one production implementation pass; final tests additionally retain complete state snapshots and assert exact file-specific reasons.

Scratch rebuild and browser E2E (`.tmp/del2/rebuild-ui.txt`):

```text
SCRATCH BUILD AND CERTIFICATE PASS: C:\mh-w-DEL2\.tmp\del2\rebuild\glp1-ra-mace-t2d
SCRATCH UI PASS: HTTP 200, visible certificate, equal download, no page errors
```

The browser ran only at `http://127.0.0.1:8000/`, checked served certificate visibility and downloadable equality, and closed its own browser/server. No existing browser was killed.

Full-suite failure list (verbatim):

```text
FAILED tests/test_certificate.py::test_all_certificate_inputs_and_manuscript_match
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
```

The certificate test fails on the exact PCSK9 source mismatch documented below. The other failure says `docs/fix_ledger.json is stale; run python scripts/render_fix_ledger.py`. That governance document is outside DEL2 ownership and was not regenerated; its pre-lane test verdict was not measured. The existing suite also rewrote only line endings in docs/compat_direction_sweep.json; after verifying normalized content equalled HEAD, the file was restored to exact HEAD bytes without checkout/reset. Final `git diff --check` passes.

## Existing source mismatch and limits

The second-pass source audit found **8 of 9 distinct digest/reference bindings matching**, with one pre-existing mismatch: `cache/pcsk9-mace/harms_aact_held.json` declares `108efeb5ed7e6b9bbdb64f290fd18eca5d2ca4a2a4c2144dfa9b7359a272fb28`, while its exact bytes hash to `142c68c1dd5adc238dc7ba0d6fba4d55e3f926752fb6f67ba3e3b176690c2762`. `git show HEAD:<ref>` has the same bytes/hash as the working file (`pcsk9-head-audit.json`), proving this was not introduced by the lane. The old verifier returned `[]`; the new verifier correctly refuses that binding (`pcsk9-verdict.json`). This is a newly enforced refusal of an existing source mismatch, not a claim that the old suite already failed. Its research source/declared digest is outside this lane's edit ownership, so neither was silently rewritten. Unresolved suite findings are retained in `.tmp/del2/STUCK_FAILURES.md`.

**INFERRED:** under this fixed HEAD and these production paths, the constructed deletions cannot retain a valid replacement certificate, and the tested exact-byte corruption cannot verify. The HEAD comparison is a deletion anchor, not historical approval: a future commit changes that anchor. Entire-row/file removal belongs to the other deletion family; this lane does not claim to solve it. Direct calls to verify_pooled alone still do not enforce document custody; the certified production build/gate does. The existing certificate code-hash list omits certificate.py; this lane does not expand that separate coverage claim. No universal deletion theorem, all-topic validity, clinical efficacy result, Overmind PASS, release certification, or independent reviewer approval is claimed.

## Static versus dynamic disclosure

| Item | Static / dynamic | Disclosure |
|---|---|---|
| Topic slugs, mutation kinds, provenance kinds, source filename selector | Static test choices | Selected after inspecting real committed inputs |
| Trial IDs, outcome names, digests, source records, certificate bindings | Dynamic | Read and cross-checked from disk/HEAD; no invented research values |
| GRADE, k, gate reasons, certificate verdicts, rendered page | Dynamic | Actual production builders/verifiers |
| Expected deletion anchor | Dynamic HEAD read | No hardcoded membership list or machine path in production code |
| Refusal codes and no-improvement contract | Static policy | Exact named refusal or conservative equality/superset assertions |
| Synthetic clinical/adjudication data | None | NOT_CONSTRUCTIBLE is explicit |

**CLAIMED coverage is limited to the measured cases above.** No index/workbook/submission status was promoted or edited.
