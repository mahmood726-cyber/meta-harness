# Scorecard refusal plants

Base commit: 3aedba0ecef0969551c761c8e91e29dccec88124

These are the executable plants added around schema v2. They are intentionally small mutations of the registry or renderer contract.

| test | plant | expected refusal |
| --- | --- | --- |
| `test_event_without_adjudication_object_refuses` | delete `adjudication` from an event | checker refuses: every event needs an adjudication object |
| `test_verdict_outside_allowed_refuses` | set verdict to `MAYBE` | checker refuses verdict outside TRUE_POSITIVE/FALSE_POSITIVE/UNRESOLVED for refusals |
| `test_resolved_verdict_without_adjudicator_kind_refuses` | set TRUE_POSITIVE adjudicated_by.kind to null | checker refuses resolved verdict with null adjudicator kind |
| `test_resolved_verdict_without_adjudication_evidence_refuses` | remove adjudication evidence from TRUE_POSITIVE | checker refuses resolved verdict with no adjudication evidence |
| `test_stored_precision_or_coverage_refuses` | store `adjudicated_precision` in registry | checker refuses stored precision/coverage numbers |
| `test_unresolved_counted_as_tp_refuses` | mark an UNRESOLVED event with counts_as=TP | checker refuses unresolved events counted into TP/FP |
| `test_plant_counted_as_production_refuses` | mark a PLANT event with counts_as_production=true | checker refuses a PLANT event counted as PRODUCTION |
| `test_renderer_refuses_precision_without_coverage` | render precision without coverage | renderer refuses split precision |
| `test_compute_uses_only_adjudicated_production_refusals` | mix TP, FP, UNRESOLVED, PLANT, and MISS events | compute excludes plants, misses, and unresolved from TP/FP precision |
| `test_migration_preserves_unresolved_when_no_adjudicator_and_author_when_named` | migrate v1 rows with and without adjudicators | migration keeps unadjudicated rows UNRESOLVED and author-adjudicated rows resolved |
