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
