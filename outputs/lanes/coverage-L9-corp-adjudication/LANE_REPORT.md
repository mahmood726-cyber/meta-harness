# L9: recorded A7 count adjudication

Implemented the value-bound decision requested in LANE_PROMPT.md. No commit, push, network request, cache edit, or portfolio/submission-status update was performed. Only the five named implementation/test files and the two requested deliverables were written. Pre-existing untracked LANE_PROMPT.md and lane.log were left alone.

## Plants before implementation

Created tests/test_a7_adjudication.py before adding production code or registry data, then ran:

```text
python -m pytest -q -p no:cacheprovider tests/test_a7_adjudication.py
FFFFFFFFFFFFFFFFFFFF [100%]
ModuleNotFoundError: No module named 'harness.a7_adjudication'
FAILED tests/test_a7_adjudication.py::test_registry_exact_entry - FileNotFoun...
FAILED tests/test_a7_adjudication.py::test_page_discloses_and_escapes_adjudication
20 failed in 10.99s
```

The original plants cover matching counts and provenance on both routes, changes to each of the eight bound fields, missing adjudication, unknown decision, the exact registry entry, visible escaped disclosure, and synthetic pipeline admission/refusal on both routes. Missing resolver failures prevented the pipeline plants from reaching their deeper assertions in this initial run.

The first implementation passed the requested suite (3347 passed in 34.87s). Source review then identified that automatic estimator preference could replace adjudicated counts. Added six pipeline cases using an explicitly synthetic alternative upper CI of 0.90 and an injected reported-effect candidate; the real registry remained unchanged. Before the selection fix:

```text
python -m pytest -q -p no:cacheprovider tests/test_a7_adjudication.py
FAILED tests/test_a7_adjudication.py::test_pipeline_routes[0.9-match-abstract]
FAILED tests/test_a7_adjudication.py::test_pipeline_routes[0.9-match-pmc_fulltext]
E KeyError: 'ai'
2 failed, 24 passed in 21.88s
```

The 0.65 cases alone did not expose this because the existing reflected-risk-reduction check retained their counts. The 0.90 cases prove preservation of the adjudication independently of that numerical coincidence.

## Change

- registry/a7_adjudications.json records exactly the requested topic/outcome/PMID entry, author, decision date, reported numbers, counts and basis. It contains no other adjudications.
- harness/a7_adjudication.py loads JSON locally and resolves exact value equality. Missing decisions leave the existing refusal unchanged; stale values return A7_ADJUDICATION_STALE; unknown decision values raise ValueError. Admitted rows carry current count values and source span, route provenance, and both current extraction records with decision metadata.
- harness/pipeline.py resolves terminal A7 states on both abstract and full-text routes using the already-available slug. Stale refusals carry a7_adjudication: STALE. Admitted counts continue through existing source-mismatch, endpoint, eligibility, estimand and design gates. Automatic reported-effect preference and adjusted-effect substitution cannot undo the explicit count choice; design refusal still applies. No topic, PMID or numeric special case was added to Python code.
- harness/page.py renders an escaped, visible source-cell line containing reported effect/CI, counts, derived effect to three decimals, adjudication, decision author and date.

## Final verification

```text
python -m pytest -q -p no:cacheprovider tests/test_a7_adjudication.py tests/test_reported_vs_derived.py tests/test_a7_oracle.py
3353 passed in 54.42s

git diff --check
exit 0 (no diagnostics)
```

Additional isolation check: ran the 26 new tests through pytest.main with builtins.open and io.open wrapped to raise AssertionError for any path containing a cache directory component:

```text
26 passed in 15.46s
```

Pipeline tests call the real _build_outcome, not an introduced replacement seam. They inject synthetic extraction results and source-hierarchy candidates, and disable unrelated signed additions/contracts. Remaining pipeline admission and rendering logic executes normally. The source-cell rendering/escaping test is the scoped UI contract; no browser was launched.

Second-pass review checked the registry key, date, author and all eight bound values against the task's recorded decision and its exact-entry test. The displayed 0.510 comes from extractor computation, (26/120)/(51/120), rather than a hardcoded display value. Tests and module contain no reproducible_ai dependency.

## Static versus dynamic disclosure

| Item | Static or dynamic | Evidence / scope |
| --- | --- | --- |
| Human decision, identifying key, date, reported values and counts | Static registry record | Exact transcription of the user-authorized lane prompt; tested for equality |
| Admission or stale refusal | Dynamic | Exact comparison with the current extractor output, including all reported CI and count fields |
| Count source, route and discrepancy record | Dynamic | Copied from current extraction; metadata comes from the registry |
| Derived effect and display | Dynamic | Extractor computes count effect; page formats it to three decimals |
| Test examples and injected candidates | Static synthetic fixtures | Explicitly synthetic, including the 0.90 upper-CI regression case; never production research output |

## Limits / not run

All requested test commands ran successfully. No live topic rebuild, cache-backed clinical source validation, network source retrieval, browser E2E suite, Overmind release certification, or deployment was run; this lane requires synthetic tests and no network. This report establishes implementation behavior and transcription of the recorded decision, not independent clinical verification or release readiness. LIVE_CONTEXT.md was absent in this checkout; the required F: index and workbook were accessible and checked without editing either.

lane.patch includes the two tracked Python diffs plus new resolver, registry, tests and this report, using git diff --no-index for new files. It excludes itself and the pre-existing prompt/log.
