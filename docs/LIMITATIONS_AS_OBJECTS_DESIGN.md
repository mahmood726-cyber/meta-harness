# Limitations as Structured Objects

Purpose: replace prose-only honest-state blocks with canonical limitation objects, so a softened limitation requires a visible object-state change and the ratchet can refuse it.

Scope read for this design: `harness/page.py`, `harness/honest_ratchet.py`, `harness/pipeline.py`, `docs/evidence/regeneration-accounting-2026-09-14/README.md`, `docs/ratchet_acknowledgements.json`, and `docs/PROSPECTIVE_VALIDATION_SPEC.md`. No harness code is changed in this lane.

## Inventory

The auditor's literal search terms, `class='absent'` and `class='banner'`, find 19 single-quoted emitters in `harness/page.py`. Two additional page-level block emitters matter for the same ratchet surface: `_absent_block()` emits `class="absent"` at line 76, and `_retrieval_class_html()` emits `class='{block_class}'` at line 239, where the object can choose `absent` or `banner`. I therefore count 21 page-level absent/banner block emitters. Table excludes `absent-cell` table cells because `harness.honest_ratchet.BLOCK_CLASSES` tracks only full `div.absent` and `div.banner` blocks.

| file:line | block | state read | prose written | prose source |
| --- | --- | --- | --- | --- |
| `harness/page.py:76` | absent helper | any `{"present": false, "reason": ...}` section/result, harms-empty, risk-of-bias-empty | `DECLARED ABSENT.` plus the supplied reason | free reason string, shared helper |
| `harness/page.py:166` | banner | `search.retrieval.snapshot.{records_sha256,retrieved_utc,mode}` | Retrieval snapshot, replay statement, dated live re-search boundary | templated |
| `harness/page.py:183` | absent | `search.retrieval.enumeration_only` | No search was run; every PubMed source is a PMID enumeration | fixed |
| `harness/page.py:222` | absent | `search.retrieval_class.{label,retraction,distinction,basis}` | Retrieval class overview with query-kind counts | templated |
| `harness/page.py:239` | absent or banner | `search.retrieval_class.{retrieval_auditable,label,retraction,distinction}` | Search-tab retrieval class block | templated |
| `harness/page.py:322` | banner | `strands.{why_topic_is_suppressed,refused_cross_endpoint_pool,members,pool}` | Declared endpoint-clean strands and refused cross-endpoint pool | free per-topic strands object |
| `harness/page.py:338` | absent | `invalidation.{stale,reasons[*].detail}` | STALE topic result not current, with named reasons | templated from invalidation object |
| `harness/page.py:346` | banner | `neutral` flag | Auditability is not stronger evidence | fixed |
| `harness/page.py:358` | absent | primary `result.{suppressed_incompatible,suppressed_reason,estmeasure.canonicals,k}` | Overview primary pool suppressed for estimand incompatibility | templated |
| `harness/page.py:607` | absent | `integrity.retracted` | Retracted trial pooled; page must not stand | templated |
| `harness/page.py:775` | absent | outcome `result.{suppressed_incompatible,suppressed_reason,estmeasure.canonicals,k,counterfactual}` | Results-tab pool suppressed for estimand incompatibility | templated |
| `harness/page.py:881` | absent | `definition_audit[*].{detail,resolution,both_families}` | Cross-family definition audit findings and resolutions | free per-topic/model-read object |
| `harness/page.py:1090` | absent | `reproduction.claim_check.claims_checked == 0` | No checkable pooled claim; claim gate cannot fire | fixed |
| `harness/page.py:1144` | absent | always in reproduction tab | Round-2 retraction of byte-for-byte reproducibility claim | fixed |
| `harness/page.py:1359` | absent | `unit_of_analysis[*]`, derived `_uoa_sensitivity()` | Unit-of-analysis caveat, no design-effect adjustment, variance/weight consequences | templated |
| `harness/page.py:1404` | absent | `funding[*].{type,note,scanned,source,span}` | Funding/COI disclosure, known/unknown denominator, no adjustment | templated |
| `harness/page.py:1443` | absent | `arm_contrast.trials[*].{status,basis,differing}` | Randomised-contrast disclosure, verified/background/unverified states | templated |
| `harness/page.py:1481` | absent | `rob_sensitivity.{full,drop_high,low_only,n_rob_rated,n_trials,any_high}` | Risk-of-bias sensitivity re-pool and coverage caveat | templated |
| `harness/page.py:1525` | absent | `grade.{certainty,not_rateable_reason,domains}` | GRADE not rateable; no overall category emitted | templated |
| `harness/page.py:1534` | absent | `grade.{certainty,downgrades,domains,certainty_capped_*}` | Provisional partial GRADE certainty and caps | templated |
| `harness/page.py:1551` | banner | `rob_spancheck.{agreement_rate,supported,not_supported,n_sampled,unclear}` | Cross-family RoB span-check result | templated |

Count: 21 page-level block emitters. Fixed or templated from structured fields: 18 of 21. Free/hand-written per-topic object prose: 3 of 21 (`_absent_block()` reasons, `render_strands_section()`, `_definition_audit_block()`). Those three are the highest softening risk because prose force can move while marker counts remain stable.

Delegated note: `harness/manuscript.py:338` also emits a `div.banner`, but it is outside this lane's explicit `page.py` inventory. It should be swept by the same object rule before claiming full site coverage.

## Object

Every page limitation block should be rendered only from an object with this shape:

```json
{
  "limitation_id": "topic:<slug>:retrieval_class:overview",
  "kind": "RETRIEVAL_CLASS",
  "severity": "BLOCKS_CLAIM",
  "claim_affected": "search completeness / systematic-search claim",
  "evidence_state": "UNRECORDED",
  "source_fields": [
    "/search/retrieval_class/class",
    "/search/retrieval_class/retrieval_auditable",
    "/search/retrieval_class/basis"
  ],
  "rendered_text": "KNOWN-ITEM RETRIEVAL ...",
  "text_sha256": "<sha256(rendered_text)>"
}
```

`kind` enum derived from the inventory:

`DECLARED_ABSENT_SECTION`, `RETRIEVAL_SNAPSHOT`, `SEARCH_ENUMERATION_ONLY`, `RETRIEVAL_CLASS`, `DECLARED_STRANDS`, `STALE_TOPIC`, `AUDITABILITY_SCOPE`, `SUPPRESSED_POOL`, `RETRACTED_TRIAL_POOLED`, `DEFINITION_AUDIT`, `CLAIM_CHECK_ZERO`, `REPRODUCTION_RETRACTION`, `UNIT_OF_ANALYSIS`, `FUNDING_COI`, `RANDOMISED_CONTRAST`, `ROB_SENSITIVITY`, `GRADE_CERTAINTY`, `ROB_SPANCHECK`.

Severity enum:

| severity | meaning | examples |
| --- | --- | --- |
| `BLOCKS_CLAIM` | The affected claim must not be made as current/valid/completed. | `STALE_TOPIC`, `SUPPRESSED_POOL`, `RETRACTED_TRIAL_POOLED`, `CLAIM_CHECK_ZERO`, `REPRODUCTION_RETRACTION` |
| `QUALIFIES_CLAIM` | The claim may be read only with the stated limitation. | `RETRIEVAL_CLASS`, `UNIT_OF_ANALYSIS`, `FUNDING_COI`, `RANDOMISED_CONTRAST`, `ROB_SENSITIVITY`, `GRADE_CERTAINTY` |
| `NOTE` | Audit context that should remain visible but does not itself block a claim. | `RETRIEVAL_SNAPSHOT`, `AUDITABILITY_SCOPE`, `ROB_SPANCHECK` |

Evidence-state enum, initially:

`DECLARED_ABSENT`, `NOT_ASSESSED`, `SUPPRESSED`, `STALE`, `UNRECORDED`, `RETRACTED`, `RAN_ERROR`, `NOT_RUN`, `SOURCE_NOT_RETRIEVED`, `EXTRACTION_NOT_PERFORMED`, `REFUSED_ON_EVIDENCE`, `PROVISIONAL`, `PARTIAL`, `UNKNOWN`, `RECORDED`.

The ratchet compares each `limitation_id` across builds on `(kind, severity, evidence_state, claim_affected)`. It refuses:

- removed limitation IDs unless a reviewed acknowledgement maps the old object to replacement object IDs;
- severity movement toward less limitation, e.g. `BLOCKS_CLAIM -> QUALIFIES_CLAIM -> NOTE`;
- evidence-state movement toward less limitation, e.g. `RETRACTED/STALE/SUPPRESSED/RAN_ERROR/NOT_RUN/UNRECORDED/NOT_ASSESSED -> RECORDED` without acknowledgement;
- changed `rendered_text` when `(severity, evidence_state)` is unchanged but `text_sha256` changed and no matching renderer-golden update is acknowledged.

`rendered_text` is generated from the object by a single renderer. A prose change therefore has one of two causes: an object-state change, which the ratchet can inspect, or a renderer change, which golden tests and `text_sha256` changes expose.

## Pipeline And Page Changes

Add a new pure builder, e.g. `harness/limitations.py`, and attach `review["limitations"]` in `harness/pipeline.py` beside the state it already computes.

| emitter group | pipeline.py change | page.py change | tests | ratchet comparison |
| --- | --- | --- | --- | --- |
| `_absent_block()` helper | Replace raw `present:false/reason` rendering inputs with `DECLARED_ABSENT_SECTION` objects carrying reason provenance and state where available. | `render_absent(section)` looks up/render object; legacy path kept until byte-identical. | Unit tests for each `present:false` caller; corpus test that helper objects cover all helper blocks. | ID presence, `evidence_state`, `text_sha256`. |
| Retrieval snapshot/enumeration/retrieval class | Use `classify_retrieval()` and `_retrieval_summary()` to emit `RETRIEVAL_SNAPSHOT`, `SEARCH_ENUMERATION_ONLY`, `RETRIEVAL_CLASS`. | Replace `_retrieval_html()`, `_retrieval_class_overview()`, `_retrieval_class_html()` prose with object renderer. | Golden block text for all 32 pages; plant `UNRECORDED -> RECORDED` without ack. | `UNRECORDED`, `NOT_RUN`, `RAN_ERROR`, `RECORDED`; severity for unauditable retrieval. |
| Declared strands and suppressed pools | Emit `SUPPRESSED_POOL` and `DECLARED_STRANDS` from `result.suppressed_incompatible`, `counterfactual`, and `strands`. | Both overview and Results use the same object IDs for the same suppression state. | Test no suppressed result renders pooled estimate; test overview/results share object state. | Blocks weakening from `BLOCKS_CLAIM` refused. |
| STALE invalidation | `invalidation.assess()` returns reason objects with stable codes and source fields, not only detail prose. | STALE block is generated from `STALE_TOPIC` object. | Plant reason prose softening while code/state unchanged; expect text-hash/golden diff. | `STALE -> RECORDED/UNKNOWN` refused unless acked. |
| Integrity, UOA, funding, arm contrast | Existing scan outputs become source fields for `RETRACTED_TRIAL_POOLED`, `UNIT_OF_ANALYSIS`, `FUNDING_COI`, `RANDOMISED_CONTRAST`. | Render tables through object renderer; keep current table bytes first. | Per-object source-field existence; known/unknown denominators; status-order tests. | State movement from retracted/unverified/unknown toward clean refused. |
| Definition audit | Convert each finding to `DEFINITION_AUDIT` with stable resolution enum plus quoted detail as evidence. | Render from objects; per-topic free text becomes `source_fields`/evidence text, not severity authority. | Corpus coverage test for every `docs/definition_audit` row; softening plant on resolution enum. | Resolution/evidence state movement refused. |
| Claim check and reproduction retraction | Attach `CLAIM_CHECK_ZERO` and `REPRODUCTION_RETRACTION` from `reproduction.claim_check` and the current reproduction limitation. | Fixed object-rendered blocks. | Claims-checked-zero plant; retraction block removal plant. | Removal or `BLOCKS_CLAIM -> NOTE` refused. |
| RoB sensitivity, GRADE, RoB span-check | `rob_sensitivity`, `grade`, `rob_spancheck` outputs become limitation objects with domain states. | Render certainty/sensitivity/spancheck from object renderer. | NOT_ASSESSED cannot render as not-downgraded; provisional/not-rateable goldens. | `NOT_ASSESSED/PARTIAL/PROVISIONAL -> RECORDED` refused without ack. |

## Migration Order

1. Add `harness/limitations.py` and a `review["limitations"]` builder, but keep `page.py` on legacy rendering. Test that every legacy block has exactly one candidate object and that object `rendered_text` equals the legacy block text after HTML rendering.
2. Add `render_limitations="legacy-compare"`: render legacy blocks, render object blocks off to the side in tests, compare text and SHA-256 for all 32 pages. No served byte moves.
3. Move fixed/templated emitters first: retrieval class, retrieval snapshot, suppressed pools, STALE, claim-check zero, reproduction retraction. These are mostly field-to-prose templates and should keep pages byte-identical.
4. Move source-table disclosures next: integrity, unit of analysis, funding, arm contrast, RoB sensitivity, GRADE, RoB span-check. Keep table ordering and escaping byte-identical.
5. Move hand-written per-topic emitters last: `_absent_block()` reasons, declared strands, definition audit. For these, add enum states before switching prose, because this is where a softened sentence can hide.
6. Only after byte-identical object rendering is green on all 32 pages, change `harness.honest_ratchet.compare_blocks()` to compare limitation object sets first and use block text comparison as a secondary renderer guard.
7. Expand `docs/ratchet_acknowledgements.json` entries to include `lost_limitation_id`, old/new severity, old/new evidence_state, reviewer, reason, and replacement IDs; keep legacy SHA acknowledgements during the transition.

This mirrors the retrieval-ledger migration: add state, render conditionally, prove no scientific bytes move, then switch the authority.

## Cost And Risk

Estimated effort: 24 to 36 lane-hours.

| work | estimate |
| --- | ---: |
| Object schema, enum ordering, renderer skeleton | 3-4 |
| Pipeline attachment for 21 page emitters | 7-10 |
| Byte-identical legacy/object comparison harness | 4-6 |
| Ratchet object comparison and acknowledgement schema | 4-6 |
| Per-emitter tests and plants | 4-6 |
| Hand-written prose migration/adjudication | 2-4 |

Highest-risk emitters whose prose is hand-written or can carry hand-written per-topic force:

- `harness/page.py:76` `_absent_block()`: arbitrary `reason` strings from section/result objects, including declared absence and reported-but-not-poolable explanations.
- `harness/page.py:322` `render_strands_section()`: per-topic strand descriptions and refused-pool explanation from `docs/*_strands.json`.
- `harness/page.py:881` `_definition_audit_block()`: per-topic/model-read findings and resolutions.

Medium-risk emitters: `STALE_TOPIC` reason details and GRADE/domain basis strings, because their surface is templated but their basis can include prose from sidecar evidence objects.

## Static-vs-dynamic hardcode disclosure

| item | static/hardcoded | dynamic/source-backed | disclosure |
| --- | --- | --- | --- |
| Severity ordering | static enum | none | Intended hardcode; the ratchet needs a stable order. |
| Evidence-state ordering | static enum | object state values from pipeline | Intended hardcode; transitions toward less limitation require acknowledgement. |
| Limitation IDs | deterministic strings | slug/outcome/source path components | IDs must be stable and generated, not authored ad hoc. |
| Rendered prose | fixed templates | source fields listed in each object | Prose must be generated; hand prose becomes evidence text, not severity authority. |
| Source fields | none | JSON pointer paths into review/search/reproduction/docs objects | Missing source fields fail closed. |
| Text SHA | none | SHA-256 of generated rendered_text | Guards renderer drift after object state is stable. |
| Cost estimate | human estimate | none | Planning estimate only, not implementation evidence. |
