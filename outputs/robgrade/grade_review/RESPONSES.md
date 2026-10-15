# Review of the GRADE preview source tiers (scripts/grade_formal_build.py), 14-15 Oct 2026

Mahmood (via Dispatch, 14 Oct): codex and agy implement, test and cross-review overnight; Claude judges and adjudicates.
agy is out of quota ("Individual quota reached ... Resets in 58h26m", real probe 14 Oct ~19:30 UTC), so the
cross-review is by a SEPARATE codex session (read-only), not the implementing one. agy's review is PENDING and is to be
done when agy returns.

| round | reviewer | verdict | findings | response |
|---|---|---|---|---|
| 1 | codex (read-only, fresh) | REVISE | 2 MAJOR, 2 MINOR (round1_codex.txt) | all 4 ACCEPTED, each fixed with a failing-first test: (1) an object of ANOTHER outcome is never used (object outcome as well as file outcome); (2) an object of ANOTHER trial is never attributed (object trial vs key); (3) sources recorded for POOLED trials only; (4) the production tier order is pinned by a contract test. |
| 2 | codex (read-only, fresh) | ACCEPT | none (round2_codex.txt) | -- |

Claude's adjudication: finding 1 was a regression the implementer's brief (written by Claude) introduced -- the old
code checked each object's outcome; the brief specified only the file's. It was held back from the reviewer to keep
the review independent, and the reviewer found it.

Verified independently by Claude: 63 GRADE tests pass. The GRADE previews are NOT regenerated in this change: the
current code's replay does not reproduce 12 of the 69 committed v3.1 objects, and the previews would use some of them
(diagnosis in progress).

## Rounds 3-4 (15 Oct): GRADE draws only on objects the CURRENT code produces

Claude's decision (adjudication): outputs/robgrade/V31_REPRODUCIBILITY.md shows the current code reproduces only 57 of
69 committed v3.1 objects (metformin and DEV objects predate the v3.1 engine). So the GRADE preview reads served A3 >
A3 > a CURRENT REPLAY of the v3.1 store (new scripts/rob2_current.py, no model call, refusing unless both source
settings are exactly "1"); the committed v3.1 tiers are dropped (those files stay frozen and untouched).

| round | verdict | findings | response |
|---|---|---|---|
| 3 | REVISE | 2 HIGH (round3_codex.txt) | both ACCEPTED. (1) Quotations from non-CC full texts survived in typed_conflicts spans: the FROZEN redactor misses them, and the committed, pushed v3.1 objects carry six such spans (reference-list titles, author names, XML; PMIDs 29485925, 26376600 in frozen TEST-topic files; 16769748 in the metformin file). rob2_current now redacts them (any string, any length); a leak check over every string finds none. The committed files need Mahmood's signature to change. (2) Melatonin's "provisional -> moderate" was arithmetic, not a rating: certainty stays provisional while a domain is PARTIAL or a judgement flag is unresolved; the arithmetic stays in certainty_from_assessed_domains_only. |
| 4 | ACCEPT | none (round4_codex.txt) | -- |

Claude's adjudication of a legacy test: test_certainty_is_provisional_while_a_domain_is_unassessed asserted "high"
for a fixture with no arm counts, where imprecision is only PARTIAL. Its requirement stands (rated once every domain
is assessed); its fixture now passes arm counts, so imprecision is genuinely ASSESSED and "high" is earned. 87 GRADE
tests pass (verified by Claude). agy's review is pending (out of quota).
