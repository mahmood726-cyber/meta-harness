# Scorecard adjudication 2026-09-14

Base commit: 3aedba0ecef0969551c761c8e91e29dccec88124

This tranche records the schema v2 correction for the gate scorecard: every refusal is an event with an adjudication object; UNRESOLVED is first-class; precision is computed only from adjudicated production refusal events and is always reported beside coverage.

Counts: 84 v1 rows before -> 89 v2 events after; UNRESOLVED 36 before -> 56 after; harvest added 5 events and enriched 1 existing event.

External-auditor adjudications: 0. adjudicator_independence is the share of adjudications made by an external_auditor; today it is expected to be 0 because no external-auditor adjudication is recorded.

| file | what it proves |
| --- | --- |
| `01-before-after-per-gate-table.md` | Per-gate v1 status and v2 computed events/TP/FP/UNRESOLVED/precision/coverage table, plus gates that lost apparent precision. |
| `02-refusal-plants.md` | Executable checker and renderer plants for the v2 refusal rules. |
| `03-harvested-events.md` | Offline harvest ledger for the named failed verify workflow runs and the local REFUS commit-message scan. |

Gates that lost apparent precision because the v1 rows named no adjudicator object:
- `hook.commit_msg`
- `ruleset.required_verify`
- `verify_all.limb_fixstate`
- `verify_all.limb_heldout`
- `verify_all.limb_index_currency`
