# Evidence provenance and agent handoff contract (proposal)

Status: research-stage specification. This document does not establish independent scientific validation or certify any clinical output.

## Design influences
Hermes Synthesis: verbatim-first extraction, local resumability, durable decisions, distinct access and eligibility states.
EvidenceForge: small agent contracts, deterministic validators, explicit human decisions.
These are design inspirations, not imported source code or assertions of external accuracy.

## Required evidence fields
Every candidate extraction should carry `review_id`, `study_id`, `document_sha256`, `source_uri`, `source_page_or_locator`, `verbatim_passage`, `field_name`, `raw_value`, `normalised_value`, `unit`, `population`, `outcome`, `time_point`, `effect_measure`, `extractor_identity`, `extracted_at_utc`, and `status`. Unknown values remain null with explicit reasons; never invent a quotation or page.

The source passage and document digest must be validated against archived bytes before an extraction is promoted to `SOURCE_CHECKED`. A passage match alone cannot prove the population, outcome, denominator or estimand is correct. Ambiguous tables, inaccessible PDFs and inconsistent outcomes require `MANUAL_REVIEW` or `REFUSE`.

## Separate state machines
Retrieval: `NOT_ATTEMPTED | FETCHED | FAILED | CAPPED | INCOMPLETE`.
Full-text access: `AVAILABLE | UNAVAILABLE | PARTIAL`.
Eligibility: `UNASSESSED | INCLUDE | EXCLUDE | UNRESOLVED`.
Extraction: `UNASSESSED | PROPOSED | SOURCE_CHECKED | ADJUDICATED | REFUSED`.
Validation: `INTERNAL_REPLAY | INTERNAL_TEST | EXTERNAL_BLINDED | NOT_VALIDATED`.

Never map `UNAVAILABLE` to `EXCLUDE`, `INCOMPLETE` to comprehensive discovery, or `INTERNAL_REPLAY` to `EXTERNAL_BLINDED`.

## Append-only decisions
Write newline-delimited records containing `event_id`, `previous_event_sha256`, `event_sha256`, `timestamp_utc`, `actor_type`, `actor_id`, `action`, `study_id`, `source_digest`, `reason` and `supersedes_event_id`. Compute each digest from a canonical serialisation of the event excluding its own digest. Corrections append a new event; never delete or mutate the old decision. A digest chain detects tampering but is not proof of independent adjudication; signing and trusted storage are separate requirements.

## Agent handoffs
SEARCH receives a frozen protocol and emits a raw-response index plus completeness/refusal status. SCREEN receives immutable retrieved records and emits decisions with source links. EXTRACT receives archived full text and emits source-backed proposed fields. SYNTHESISE accepts only compatible, validated fields and must preserve `REFUSE` and `MANUAL_REVIEW` rather than silently pooling. HUMAN_ADJUDICATE requires recorded actual reviewer identity, independent source access and adjudication decisions; an LLM role-play is never human review.

## Required negative tests
1. Missing or altered source bytes fail provenance checks.
2. Missing quotation/page cannot become source-checked.
3. `FULLTEXT_UNAVAILABLE` never becomes an exclusion.
4. Capped or failed retrieval never becomes complete.
5. Conflicting outcome/population/estimand fields block pooling.
6. Editing or removing a decision breaks journal verification.
7. A self-reviewed model output never becomes externally validated.
8. Resume after interruption preserves all previous decisions and their original timestamps.

## Integration boundary
Keep this evidence contract separate from statistical engine logic and from e156 publication certification. Export only versioned records with explicit uncertainty; use the existing review-exchange schema when it is integrated. Do not assume the proposed fields are already implemented in code.

## Implementation boundary: unverified status promotion

The current `harness.evidence_provenance.validate_extraction` primitive is a
*source-byte check*, not a blinded human adjudication service. Its boolean
success is restricted to `SOURCE_CHECKED` evidence with a matching archived
digest and verbatim passage. `PROPOSED` and `REFUSED` cannot pass as verified
evidence. `ADJUDICATED` is refused until an independently authenticated
human-adjudication receipt verifier exists; adding `blinded: true` or a
self-declared reviewer ID is not sufficient. No human-review accuracy or
independence is asserted by these unit tests. These checks are not yet wired
into all actual synthesis entry points.
