# LANE CGX3A report

Owned-section migration: **9 registered of 264 → 153 registered of 153**. Final owned unregistered/mismatched unit count: **0**. Full-suite status is **not green**; see the exact summaries below. No commit, push, deployment, network acquisition, or portfolio-status update was performed.

## Base and scope

`git rev-parse HEAD`: `bf99a91652e74347e4e10cf6b9f1962aee4e596d`; matches `refs/lanes/landing4-wip-str` from the lane prompt. Initial tracked worktree was clean; existing untracked lane prompt/process logs were preserved. Required F-drive index/workbook context was read, not edited.

The initial build and `scripts/claim_scope_sweep.py` regenerated the missing CGX2 census before implementation. The baseline numeric plant ran before production-code edits. `LANE-CGX3A-BASE-SCOPE.json` retains the original broad container census; `BASE-OWNED-SCOPE.json` uses the HEAD renderer replay to make ownership boundaries explicit.

The owned boundary is overview, outcome summary/compatibility prose, known-missing panel, declared-strand pool summary, and pooled trial provenance rows. Existing absent-trial membership rows, `typed-effects` sections, other tabs and page chrome are measured separately. Their renderers were not migrated or silently counted as structural. `_trial_inputs` changed only its pooled-provenance branch; the absent-membership branch is untouched. `harness/synth.py`, `harness/gate.py`, search and screening implementations are untouched.

Audit units are conservative visible prose/table text runs, not linguistic sentences or independent empirical claims. The denominator changes because duplicate numerical prose and blanket assertions are replaced with grouped typed summaries. A question is now a semantic heading. The existing tag-based heading/navigation rule and short-semantic-table-header rule remain the structural rules; there is no string whitelist.

| Owned surface | Base registered / total | Final registered / total |
|---|---:|---:|
| overview | 0 / 121 | 34 / 34 |
| outcome-0-summary | 0 / 83 | 35 / 35 |
| provenance-0 | 7 / 56 | 76 / 76 |
| outcome-1-summary | 0 / 1 | 3 / 3 |
| outcome-2-summary | 0 / 1 | 3 / 3 |
| strands | 2 / 2 | 2 / 2 |
| **Total** | **9 / 264** | **153 / 153** |

## Base plant — verbatim

```text
BASE PLANT: FAIL (expected rejection)
{
  "code": "SENTENCE_WITHOUT_OBJECT",
  "kind": "unregistered",
  "claim_id": "",
  "detail": "The pooled hazard ratio is 0.123456.",
  "unit_id": "unit-0143",
  "context": "p"
}
```

The final mutation tests also reject an inserted naked number and a changed number inside a real claim marker. An altered stored pooled estimate produces `TRANSFORMATION_MISMATCH`; a changed evidence digest produces `UNVERIFIED_FACT`.

## Implementation and evidence

`harness/page_claims.py` builds a registry from identified review fields before rendering. `claimgraph.review_graph` uses the same builder for independent scans. Registry IDs are derived from canonical object content; text is never scraped into the registry. Dictionary-key order is canonicalised, and the JSON-roundtrip determinism regression passes.

Reported-effect pools and leave-one-out rows are recomputed from source FACT dependencies. Display precision matches the pipeline's four-decimal stored result. Missing-evidence, parser-contrast, pooled/unpooled and compatibility summaries derive counts from item states. Stored blanket compatibility verdicts and the stale known-missing headline are not reused as aggregate evidence. Unsupported sensitivity schemas receive an explicit owed-recomputation judgement rather than an asserted numeric result. Other unsupported pool schemas retain explicit sweep debt; this is not a universal engine migration.

Recorded analytical decisions carry their source-field record and remain `JUDGEMENT` / `OWED` unless an executable rendering rule supports the classification. Registration does not mean expert adjudication. Each `INTERPRETATION` renders at least one alternative. Certainty is the existing `start − sum(downgrades)` transformation, with **provisional** whenever any required domain is unassessed.

Pooled provenance now renders verified numbers and the held document path, digest, retrieval timestamp and located span. The second-pass audit found all 7 primary source IDs in the cached records and verified their held evidence, timestamps and numeric spans. Typed-object violations: `[]`. Recomputed primary: `{'k': 7, 'estimate': 0.8884, 'ci_low': 0.8284, 'ci_high': 0.9527, 'tau2': 0.0012, 'pi_low': 0.7959, 'pi_high': 0.9916}`. Source IDs, source dates, pool membership and source numeric inputs were not edited. Canonical-review changes are rebuild protocol/reproduction metadata.

| Static configuration/templates | Dynamic source-derived content |
|---|---|
| Rendering labels, editorial alternatives and semantic scope boundaries | FACT validation against committed source bytes and located spans |
| Four-decimal primary display precision; existing strand display policy | Pool estimates, intervals, tau squared and leave-one-out recomputation |
| Existing certainty category ordering and required domains | Certainty arithmetic and provisional state |
| Explicit schema support/fallback rules; no topic-specific result constants | Item-state counts and source-field judgement records |

## Exact unregistered text and corpus measurement

Final owned-unit debt: `[]`. Thus there are no remaining owned strings to list as unregistered. `LANE-CGX3A-BASE-TEXT-LEDGER.json` preserves every original unregistered literal, with exact text, section, context and its retirement/replacement rationale; it is not an allowlist.

The whole final page remains only **165 registered of 1303** in the broader sweep. Every remaining exact text unit and its outside-ownership reason is listed in `LANE-CGX3A-UNREGISTERED.json`. See `AFTER-SWEEP.json` for served versus fresh coverage, and `CORPUS-SWEEP.json` for all 32 measured pages. Other pages were measured, not rebuilt or chased. These are measured sweep counts, not a portfolio/submission claim.

## Verification summaries — verbatim

Build command: `python scripts/build_topic.py glp1-ra-mace-t2d --now 2026-09-11` (offline committed cache). The final reproduction census reports `render is deterministic: true`; the focused test also checks that served owned fragments equal their fresh rendering, allowing the existing FDA CRLF-to-LF HTML normalization. Exact build output is in `LANE-CGX3A-BUILD.txt`.

Focused command: `python -m pytest tests/test_page_claims.py tests/test_claimgraph_typed.py tests/test_page.py tests/test_claimgraph.py tests/test_claimgraph_dispute.py -q --tb=short`.

```text
............................................                             [100%]

44 passed in 120.01s (0:02:00)
```

Full command: `python -m pytest tests -q --tb=short`.

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
9 failed, 921 passed in 1131.09s (0:18:51)
```

Full-suite output is preserved in `LANE-CGX3A-FULL.txt`. These repository-wide failures were also replayed using HEAD's renderer and claimgraph loaded in memory, without checking out or modifying source files. This is a base-source replay against the current on-disk evidence/artifacts, not a second isolated whole-checkout run:

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
9 failed in 181.19s (0:03:01)
```

The first root-wide `python -m pytest -q --tb=short` attempt failed collection because `outputs/search_v2/lanes/R2/test_search_v2_isrctn.py` and `tests/test_search_v2_isrctn.py` share a module name: `1 error in 9.95s`. The complete canonical `tests/` suite above avoids collecting the archived lane copy. No unrelated archive was renamed.

The initial intermediate focused failures (one legacy scale-label fallback, then a raw FDA line-ending comparison) and the deterministic-build failure were corrected and retested. Broad repository blockers are recorded in `STUCK_FAILURES.md`; no gate was bypassed. Test-generated unrelated cache/sweep changes were restored to their clean session-start bytes. `git diff --check` is recorded in `LANE-CGX3A-DIFF-CHECK.txt`.

No SHIP/CERTIFIED/Submission-ready claim is made. The scoped migration and its evidence are the deliverable; the broader suite remains blocked as disclosed.
