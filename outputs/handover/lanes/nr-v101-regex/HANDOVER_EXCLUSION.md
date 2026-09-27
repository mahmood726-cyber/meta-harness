# Lane NR, V1.0.1: exclusion polarity in the producer (M2 W4a/W4b)

Branch `nr/v101-regex`, on top of the V1.0.1 regex commits. Done in Claude directly; codex was allowed but not used. The
change touches both copies of the verifier's semantics, and every radius row had to be read by hand.

## The defect
`harness/target_endpoint._components_from_text` added "stroke" (etc.) whenever the word appeared, and `_classify` compared
that positive set with 3-point MACE. So "cardiovascular death or nonfatal MI; nonfatal stroke was excluded from the
primary outcome" was EXACT_TARGET. That is M2 W4a (SOUL, hand row) and W4b (SUSTAIN-6, abstract row): WRONG_ADMISSION.
The same reader also refused "3-point MACE excluding unstable angina" as NEAR_MATCH, because it read the excluded
component as an extra one.

## The fix: typed relations, one semantic module
- `target_endpoint.endpoint_relations(text, context)` returns `INCLUDES(x)` / `EXCLUDES(x)`:
  - EXCLUDES comes from exclusion scopes and exclusion statements, in the span and in its document neighbourhood (±400).
  - INCLUDES is read after cutting those scopes and statements.
  - `_components_from_text` is now INCLUDES only. The old word reader is `_mentions_from_text`, the vocabulary only.
- `_classify`: an excluded **target** component → **`ENDPOINT_COMPONENT_EXCLUDED`**, refused by `_class_verdict` and
  `admissibility` under that code.
- Every binding route carries EXCLUDES: `bind_result_span` (both halves, with neighbourhood), `_definition_sentences`,
  `classify_bound`, `bind_verified_row`, and the hand binder's own-clause, definition and table-label paths.
- **Shared, not duplicated.** The relation functions are the verifier's own (`split_exclusions`, `analysis_exclusions`,
  `document_neighbourhood` in `scripts/verify_bundle.py`). The producer imports them (`from scripts import
  verify_bundle`) and passes its own vocabulary through a new `namer=` parameter.
  - The direction is forced. The verifier must import nothing from the repository (`tests/test_bundle_verifier.py::
    test_verifier_imports_nothing_from_the_repository`), so the one module lives verifier-side.
  - The certificate's import closure follows `scripts/` imports, so every certificate now pins `verify_bundle.py`'s bytes.
  - `build_bundle.py` keeps its byte-identical copy of the block, as `test_both_copies_of_the_binding_block_are_the_same_code`
    requires; I mirrored every edit.

## Changes to the shared semantics (so the verifier changed too; each is pinned by a plant)
1. `', or'` ends an exclusion scope. "nonfatal MI excluding silent infarction, or nonfatal stroke" used to cut the stroke
   **in the verifier too**: a false refusal on both sides.
2. A cue that scopes the POPULATION cuts nothing: right after a population noun, or with one earlier in the cue's own
   clause ("in patients … but without diabetes, …"). This was a verifier false refusal too.
3. "with or/and without X" excludes nothing.
4. "without (any significant) difference / increase in X" and "without knowledge of X" exclude nothing.
5. "except" / "but not" / "without" scopes end at their own comma.
6. A short-cue scope followed by its own result tuple is a results contrast ("but not stroke (RR, 0.86; …)").
7. A time window is not an event: "excluding first 2 years of follow-up", from VITAL registry measure #12. The full
   rebuild caught this as a false ENDPOINT_COMPONENT_EXCLUDED of a genuine MACE measure.
8. A scope never runs past its own sentence.

Items 2–8 were found by reading the corpus radius row by row. Each was a latent misreading; none moved a served row.

## Tests
- `tests/test_nr_v101_exclusion.py`, 21 cases, all passing:
  - the W4 wordings (statement and scope forms);
  - the neighbour-sentence footnote;
  - the verdict code;
  - the three requested meaning-preserving controls, plus a parenthetical qualifier and a population "without";
  - verifier parity on the controls;
  - the 7 radius-found cue forms;
  - the temporal-window case.

  On the unmodified candidate, **9 of the first 13 failed** (`EXCL_PLANTS_PRE_FIX.txt`). The 4 that passed are controls
  the old reader happened to get right. The 8 cases added later each failed on the version before their fix.
- **W4a and W4b are no longer xfail.** They now run the battery's full paired shape: control admits → the definition
  excludes nonfatal stroke → refused as `ENDPOINT_COMPONENT_EXCLUDED` with the trial visible → restored inputs give the
  control's pool.
  - On the candidate code both fail with "an excluded component was treated as included (POOLED)" (`W4_PRE_FIX.txt`).
  - W4b's fixture had to keep the lane consistent. SUSTAIN-6's refused GI entry quotes the whole abstract as its
    `source_span`, so the quote changes with the sentence. Otherwise the loader refuses at LOAD (the W2a/W5b class) and
    the test can never reach the classifier.
- M2 battery: 27 passed, 2 xfailed (W2a/W5b, unrelated). E1–E10 on both copies, and all 125 verifier logic tests, pass.

## Corpus-wide radius
| measure | result |
|---|---|
| **served rows that flip**: all 32 topics rebuilt with `scripts/build_topic_recorded.py <slug> --now 2026-09-11`, head without vs with this change (hand rows included) | **0 of 797**; 0 pooled results change (`SERVED_X2_vs_R.json`) |
| served rows, both V1.0.1 changes vs candidate 3876a62d | 1 of 797: COCS enters colchicine-POAF, the regex change (`SERVED_X2_vs_CAND.json`) |
| abstract-route classification of served rows with a source sentence | 0 of 330 change |
| definition sentences (every cached record) | 1 of 3,330: 42567173 "narrower secondary kidney composite (excluding cardiovascular-related death …)" now EXCLUDES CV death. Correct. |
| component reads, every abstract sentence | 1 of 37,472: the same sentence |

Page content besides numbers:
- Every certificate's `analysis_code_blobs` now names `scripts/verify_bundle.py`, plus the changed harness blobs.
- omega-3's unselected `target_endpoint_alternatives` list for VITAL changes because of (7) above. The selected row is
  unchanged.

## For the release captain at V1.0.1 integration
- Regenerate all 32 topics **and the bundle**. The served verifier mirrors (`docs/scripts/verify_bundle.py` and the page
  verifiers) must equal the new source. `test_verifier_is_served_byte_identical…` /
  `test_each_served_verifier_is_byte_identical_to_its_source` fail until then, by design, as do the certificate-closure
  tests (already stale since the regex commit).
- `test_bundle_is_current` already fails on the unmodified candidate.
- No new result-change notice: no served number moves from this change.
- New reason code on refused rows: `ENDPOINT_COMPONENT_EXCLUDED` (`reason_code` / `endpoint_admissibility`). No served
  row carries it today.
