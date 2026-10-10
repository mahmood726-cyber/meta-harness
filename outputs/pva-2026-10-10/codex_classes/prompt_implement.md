You are implementing ONE generated-text fix in a reproducible meta-analysis harness. This directory is a git repository
holding the harness code (`harness/`), its tests (`tests/`), protocol configs (`topics/`) and the 32 served review objects
and pages (`docs/reviews/<slug>/review.json`, `index.html`). Most tests need data that is NOT here; do not try to make
them run. You may run small Python snippets that import `harness` and read `docs/reviews/*/review.json`.

## The class: {CLASS_ID}, {CLASS_NAME}
**Rule.** {CLASS_RULE}

`CLASS_REPORT.json` is an earlier read-only investigation of this class: its generators, every instance across the 32
pages (verbatim), the proposed fix and a plant. Use it, but verify against the code: it may be wrong.

## What to do
1. Fix the GENERATOR (the code that produces the text), not individual pages. Keep the change minimal and in the style
   of the surrounding code.
2. **Do not change any served number.** Do not change any estimate, CI, count, k, trial membership or pooling decision,
   and do not add new numeric results. The change is to wording, labels and the derivation of verdicts only. If the rule
   cannot be met without a number change, implement only the wording part, and say so in `not_done`.
3. Add ONE new test file `tests/test_class_{CLASS_ID}.py` with:
   - a PLANT: a small constructed input (build the dict inline) on which today's code emits the bad text and the fixed
     code does not. Assert the property, not a whole sentence.
   - a SWEEP: for every `docs/reviews/*/review.json`, render the relevant text with the fixed code and assert that no
     instance of the class remains. Assert the denominator (the number of reviews checked) so the sweep cannot pass by
     checking nothing.
4. Run your new test file with `python -m pytest -q tests/test_class_{CLASS_ID}.py` and report the result.
5. Summarise the change as JSON per the schema: the files changed, what the generator now reads, the sweep result
   (instances before → after, out of how many reviews), and anything not done.
