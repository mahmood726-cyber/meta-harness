# CGX lane report

Base HEAD: `f6f7b14c820bdadd258122ac0bb54c7e4d2a989a` (matches the prompt; separate LANE_BASE.txt absent).
No commit, network, synthesis, membership, screening or search changes.

## Plant fired pre-fix

Command: `python -m pytest tests/test_fact_provenance.py -q --color=no`
The existing publication gate's `check_pooled_verified` limb was called directly, isolating this fail-open from unrelated publication refusals. No harness file had been modified.

```text
F                                                                        [100%]
================================== FAILURES ===================================
________________ test_typed_number_without_document_is_refused ________________

tmp_path = WindowsPath('C:/mh-r-CGX/.tmp/pytest-of-mahmo/pytest-0/test_typed_number_without_docu0')

    def test_typed_number_without_document_is_refused(tmp_path):
        root = tmp_path
        cache = root / 'cache' / '__plant_cgx__'
        cache.mkdir(parents=True)
        row = {'effect': 0.87, 'ci_low': 0.78, 'ci_high': 0.97,
               'scale': 'HR', 'source': 'Plant trial reported HR 0.87 (0.78-0.97).',
               'verified': 'verified'}
        (cache / 'verified_effects.json').write_text(json.dumps({'plant-row': row}), encoding='utf-8')
        page = root / 'docs' / 'reviews' / '__plant_cgx__'
        page.mkdir(parents=True)
        review = {'slug': '__plant_cgx__', 'outcomes': [{'name': 'Plant outcome',
                  'trials': [dict(row, id='plant-row')]}]}
        (page / 'review.json').write_text(json.dumps(review), encoding='utf-8')
        reasons = check_pooled_verified(str(page))
>       assert any('UNVERIFIED_FACT' in reason and 'plant-row' in reason for reason in reasons), (
            f'gate pooled-number limb let typed plant-row through: {reasons}')
E       AssertionError: gate pooled-number limb let typed plant-row through: []
E       assert False
E        +  where False = any(<generator object test_typed_number_without_document_is_refused.<locals>.<genexpr> at 0x0000017D64A23850>)

tests\test_fact_provenance.py:22: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_fact_provenance.py::test_typed_number_without_document_is_refused
1 failed in 3.74s
```

## Static versus dynamic disclosure

| Component | Static | Dynamic evidence |
|---|---|---|
| FACT validation | Required fields, allowed held roots, digest algorithm | Actual document bytes, extracted-text digest, exact located span |
| Plant | Explicit synthetic test-only row | Base gate result above |
| Positive control | ELIXA source-record selection | Held FDA document and extracted text, checked at test runtime |
| Sweep | Counting/scanning contract | Local cache rows and rendered page bytes |

## Result: partial implementation; full lane NOT accepted

The FACT fail-open is closed and tested. The requested universal prose migration and all seven pre-fix plants are not complete. This is not a release-ready lane. Existing served HTML and manifests were not regenerated or promoted. The new census/gate deliberately refuses those pages because their prose is not registered and their source numbers lack the required provenance.

### Plant passes post-fix

Command: `python -m pytest tests/test_fact_provenance.py -q --color=no`

```text
....                                                                     [100%]
4 passed in 3.24s
```

The positive control uses the real ELIXA StatR source/decision object from `outputs/handover/glp1_regulatory/regulatory_sources_glp1.json`. The held document SHA is `cf2b3ef92247b85e7be7c3b56c3cc4fc0af007b3950acee95eea9c995653db38`. Both held document and extraction must match HEAD bytes; the extraction must also match its recorded SHA. The JSON quote has normalized whitespace, so the adapter locates it without changing punctuation/digits and retains the exact original extraction slice, including CRLF. That exact slice is then checked literally. No cache row received an invented digest.

The first positive-control run exposed CRLF translation in the adapter, and the next exposed a numeric-token regex that incorrectly rejected a number followed by a sentence-ending period. Both were fixed; the positive control then passed. The copied-graph mutation test now tampers with the cached span before invalidating its document SHA. Exactly `trial`, `pool`, and `claim` invalidate; the independent transformation and original graph do not.

### Implemented

- Extended `harness/claimgraph.py`, retaining existing claim IDs, input versions, graph checks and signed-dispute machinery. Added four typed classes, exact held-document provenance validation, visible rendering marks, registered-text comparison, duplicate/missing/cyclic dependency refusal and transitive document invalidation.
- Gate's existing `check_pooled_verified` rejects each unverified row by ID. A new served-text limb refuses unregistered text, forged claim markers/text and invalid typed objects. Census verifies this contract too.
- Trial input rendering shows values with `UNVERIFIED_FACT` and no longer promotes legacy `verified`/`verified_handchecked` labels to source-proof badges.
- Deterministic operations currently supported: count, sum, log, state counts, source-provenance coverage and GRADE arithmetic. The pooled-result/heterogeneity/PI transformations have NOT yet been migrated to this typed API.
- GLP-1 certainty renders `provisional` in page, manuscript and limitation output. Stored `moderate / 0 downgrades` is flagged; stored scientific inputs were not rewritten.
- Manuscript aggregate absence sentences now render per-item state counts. The index's pooled-number verification section derives counts through the graph instead of counting legacy badges. Unsupported blanket verification prose was removed from the index introduction and manuscript.
- Added offline `scripts/claim_scope_sweep.py` and wrote `docs/claim_scope_sweep.json`.

### Measured scope, not a universal-coverage claim

The sweep found **28 UNVERIFIED_FACT of 28 rows** across all `cache/*/verified_effects.json` files. It scanned **32 review pages**. These are task-local disk counts, not portfolio/submission counts.

On GLP-1 the migrated registry has **13 propositions: 8 FACT objects (unverified) and 5 TRANSFORMATION objects**. GRADE arithmetic catches **1 contradiction of these 13 propositions**; this denominator does not include the unmigrated legacy prose. The served page has **0 of 1,055** registered visible text units; the fresh renderer has **13 of 1,064**. Across fresh topic renderings it is **272 of 54,843** units. Units are conservative visible prose/table text runs, including labels, NOT an exact linguistic factual-sentence census. This distinction is recorded in the JSON and is an unmet acceptance requirement, not hidden behind a coverage percentage.

There are **0 migrated GLP-1 JUDGEMENT objects** in each adjudication category and **0 migrated INTERPRETATION objects**. This does NOT mean the manuscript has no judgements or interpretations. Its actual interpretation-sentence count and reasonable alternative formulations are still owed. The generic interpretation API checks alternatives; it cannot deterministically verify an interpretation's truth. Model-judgement support checks required metadata, not the full pinned-model/cache replay contract.

### Named plant audit against the actual base

| Requested plant | Observed base / result |
|---|---|
| GLP-1 BEFORE versus no prospective precedence | Both statements occur in the base HTML. Universal registration-proposition migration is still owed. |
| GLP-1 publication bias assessed versus not assessed | Not reproduced as described: this base manuscript already says “publication bias not assessed automatically”. No fabricated pre-fix failure claimed. |
| GLP-1 moderate, zero downgrades | Present; arithmetic check fires and fresh certainty renders provisional. |
| Ticagrelor 2 of 2 versus 1 of 2 rated | Not reproduced as described: base has two RoB trial rows; the visible “1 of 2” wording concerns D3 being unassessed and one trial at some concerns. Full RoB-object migration remains owed. |
| CAP seven absent versus 5/1/1; Torres refusal | Base states are 5 OUTCOME_NOT_IN_SOURCE, 1 EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH, 1 COUNTS_PRESENT_NOT_CORROBORATED. Blanket absence plant fires; fresh manuscript renders those states. Torres is already pooled in this base; the described Torres refusal was not reproduced. |
| Colchicine 26 absent versus none | Actual base says 22 families, with 12 OUTCOME_NOT_IN_SOURCE, 2 EXTRACTION_DEBT, 8 SOURCE_NOT_RETRIEVED. Blanket absence plant fires for this actual mismatch; no claim to have reproduced 26-versus-none. |
| COPS self-inconsistent refusal | Refusal row exists; independent source-backed adjudication of its semantic contradiction remains owed. |

The broad specification cannot honestly be declared accepted with these missing migrations and mismatched historical plant descriptions. `STUCK_FAILURES.md` records the remaining work.

### Verification

Final scoped command:

`python -m pytest tests/test_fact_provenance.py tests/test_claimgraph_typed.py tests/test_claimgraph.py tests/test_claimgraph_dispute.py tests/test_page.py tests/test_limitations.py tests/test_consumer_consistency.py -q --color=no`

```text
......................................................                   [100%]
54 passed in 4.32s
```

`git diff --check`: PASS (Git printed an index.py CRLF-to-LF normalization warning). `python -m compileall -q` on the eight modified/new production Python modules: PASS. New tests exercise renderer-to-registry-to-gate contracts, forged text/marks, real held provenance, tampering, copied-DAG invalidation, four class marks, missing basis/alternatives, certainty arithmetic, base absence contradictions and fresh consumers. No interactive browser test or full repository test suite was run. Existing legacy pages cannot pass the newly tightened gate; this is exposed, not waived.

Second pass checked source-record identifiers/digest, exact span bytes, numeric token matching, statement denominators, evidence-free rows, and protected-file scope. No changes to synth.py, membership, screening, search, source caches, protocols or served review artifacts. No network, commit, push, deployment, or project/submission-state updates.
