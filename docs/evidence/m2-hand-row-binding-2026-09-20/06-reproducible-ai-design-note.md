# Reproducible AI: every model call in the pinned path, counted (2026-09-21)

Standing instruction (Mahmood): everything runs in the reproducible harness -- regex and reproducible AI -- as
pinned modules, never as scratch scripts. This note states, by measurement rather than assumption, where a model
is called on the path that produces a served number, and where model-authored text enters the record.

## What was measured

The pinned path is the certificate's code closure: `CERTIFICATE.json#analysis_code_blobs` on the landing tree
lists **83 paths, 82 present** (81 `harness/*.py`, `scripts/build_topic.py`, `scripts/reproduce_review.py`; the
listed `harness/effect_type.py` is a recorded NOT_PRESENT entry). `scripts/audit_model_calls.py` parses every
present file (AST, not grep) for (a) an import of a model client (`anthropic`, `openai`, `google.generativeai`,
`google.genai`, `vertexai`, `cohere`, `mistralai`, `groq`, `litellm`, `langchain`, `transformers`, `ollama`) or of an
HTTP library, (b) every `subprocess` invocation and the program it runs, (c) dynamic imports, and (d) model words
(`anthropic|openai|claude|gpt|gemini|codex|llm|messages.create|chat.completions|model_call`).

## Result: model calls in the pinned path -- 0 of 82

- **Imports.** The only network client in the closure is `harness/http.py` (stdlib `urllib`), used by
  `harness/fetch.py` and `harness/acquisition.py` to reach PubMed / ClinicalTrials.gov -- data sources, not
  models -- and the build itself runs under `aact_cache.cache_only_build` (`build_review_core` is decorated), so a
  regeneration reads the committed cache and calls nothing. No model client is imported anywhere in the closure.
- **Subprocesses: 22 sites in 11 modules; programs `git` and `python`** (`git hash-object` / `show` /
  `ls-files` / `ls-tree` / `rev-parse`; `python` = `scripts/reproduce_review.py` running `build_topic.py`). None
  invokes a model CLI.
- **Dynamic imports: 3, none a model** -- `harness/acquisition.py:164-166` resolves a fetch adapter's `__file__`
  to hash it for provenance; `harness/architecture_identity.py:13` is `importlib.metadata` (package versions).
- **Model words: 24 lines, none a call.** They are (1) the acquisition-ledger vocabulary `MODEL_CALL` in
  `harness/acquisition.py:128` and its label in `harness/pipeline.py:1728` -- a provenance *kind* for a record a
  model was once asked to find, with the verbatim prompt as the query; **0 records in `cache/*/records.json` and
  0 rows in `docs/reviews/*/review.json` carry it**; (2) `harness/index.py` and `harness/page.py` rendering
  `docs/crossfamily.json`, the committed outputs of the cross-family checks (Gemini via AGY, Fable, a GPT-5
  checker) -- "a model call is treated as a source; the outputs are committed, so this regenerates without
  re-calling the model" (`harness/index.py:640-641`); (3) regex `fullmatch` / enrollment-floor lines caught by the
  pattern, unrelated.

So: **none in the pinned path** -- stated from the sweep above, not assumed. Said plainly: **there is no AI in
the path that produces a served number, so there is nothing in that path to make reproducible.** The
'reproducible AI' requirement therefore binds the places listed below where a model's WORDS enter the record
(each named with its author and, for a signature, its basis), and any future model call, which this audit
would count on the tree it lands in.

## The M2 landing specifically

Every module and script this landing adds or edits is regex and arithmetic only:
`harness/hand_binding.py`, `harness/target_endpoint.py` (endpoint-reference resolution), `harness/parity_relation.py`,
`harness/result_changes.py`, `harness/honest_ratchet.py`, `harness/rob_sensitivity.py`, `harness/page.py`,
`harness/pipeline.py`, `scripts/m2_battery.py`, `scripts/m2_row_census.py`, `scripts/endpoint_reference_sweep.py`,
`scripts/refresh_result_change_notices.py`, `scripts/countersign_result_change.py`. **0 of 13 call a model.**
The battery (`tests/test_m2_battery.py`, 28 cases) and the census run the same code the build runs.

## Where a model's words DO enter the record, and how they are marked

A model never supplies a number here. Model-authored text enters in three places, each recorded with its author:

1. **Result-change notice reasons** (`docs/result_changes.json`): built mechanically by
   `refresh_result_change_notices.py` from the set-aside records (specific reason, mechanism sentence,
   surviving sentence); two carry a hand-written reason (`reason_locked`: esketamine, pcsk9 injection-site)
   authored by the lane (Claude Opus 5) and named in `by`. The reviewer's countersignature names the sha256 of
   the rendered block and `how_it_reached_the_reviewer`.
2. **Parity acknowledgement** (`docs/ratchet_acknowledgements.json`): `by` = the lane, countersignature owed.
3. **Fix-ledger entry, evidence README and this note**: authored by the lane, `author` field named.

None of these is consumed by the build to produce a served number; each is rendered as text with its author.

## Limits of this measurement

- The closure is the certificate's list; a module imported dynamically (by string) would not be in it. The
  three dynamic imports in the closure are listed above with what they resolve.
- The client list is the one above; a client not in it would be missed by (a) but not by the cache-only guard
  and the subprocess-program check, which is why all four were run and reported.
- Measured on the landing tree (F:\mh-bind2, base 8b1fb37d); the sweep is `scripts/audit_model_calls.py`, run
  by the gate as `tests/test_no_model_call_in_pinned_path.py`, so the count is re-derived on every tree.
