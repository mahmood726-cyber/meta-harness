# DELEGATED_BULK_ACCEPTANCE -- `screening`

**AI-proposed, accepted under delegated authority without individual human review.**

- authorised by: Mahmood Ahmad (2026-09-24)
- how it reached the reviewer: Dispatch chat relay; blanket instruction; no item-by-item review
- instruction text: "yes record as bulk acceptance"
- context: Reply to the offer of a truthful bulk-delegated record, made after Mahmood asked for the proposals to be "sign all for me" and signing in his name was declined.
- this is **not** a human countersignature and satisfies no predicate that requires one

Scope rule: accepted: the proposal passes the deterministic gate except for the human countersignature, a recorded re-ask of the identical prompt reached the same derived decision, and that decision is ELIGIBLE or INELIGIBLE. Not accepted: unstable on re-ask; never re-asked; gate refused; the model could not tell (a stable 'cannot tell' is not a decision, so there is nothing to accept -- the item stays UNRESOLVED).

**Accepted: 132 of 269** -- STABLE_ELIGIBLE 118, STABLE_INELIGIBLE 14
**Not accepted (UNRESOLVED): 137 of 269** -- NO_DECISION_TO_ACCEPT 128, UNSTABLE_ON_REASK 9

Every accepted item is bound to its proposal by record id, response sha256 and rendered-block sha256 (`registry/model_proposals/screening.delegated_acceptance.json`); `--check` reports any binding that no longer holds.

Accepted items whose decision differs from what the page serves (INELIGIBLE against a served inclusion) change nothing until their served impact has been shown to Mahmood: `outputs/model_source/DELEGATED_screening_SERVED_IMPACT.md`.
