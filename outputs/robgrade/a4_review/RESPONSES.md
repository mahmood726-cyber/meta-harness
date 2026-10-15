# Review of the A4 amendment REQUEST (not signed), 14-15 Oct 2026

Implemented by codex, cross-reviewed by SEPARATE read-only codex sessions; Claude adjudicated. agy is out of quota
(real probe 14 Oct ~19:30 UTC: "Resets in 58h26m"); its review is PENDING.

| round | verdict | findings | response |
|---|---|---|---|
| 1 | REVISE | 3 MAJOR, 2 MINOR (round1_codex.txt) | all ACCEPTED: tests mock the record-loading boundary with real records and cover codex, agy and the adjudicator in replay and live mode, with fresh-record controls; the impact is measured against REGENERATED current prompts; replay's broader defect is stated; strict xfail is described as a regression marker, not a signature guard. |
| 2 | REVISE | 1 MAJOR (round2_codex.txt) | ACCEPTED: scripts/a4_measure.py accepts each source variable only unset or exactly "1" (the frozen driver enables any non-empty value, "0" included) and prints the effective setting. Verified: "0" exits 1 before measuring; "1"/"1" reproduces the counts. |

Claude's adjudication of the measurement: the first revision's "29 stale entries" came from measuring DEV trials
without ROBGRADE_DEV_OPEN_CC=1, the setting their reads used. Under the right settings: 0 of 138 reader entries
stale, 8 of 65 adjudicator entries (7 from typed rules added later in 9aa0d65b5, 1 from amendment A2's parser), 0 of 56
in the served store. The frozen replay reads all 8 -- the defect A4 closes. It already ignores an adjudicator answer
on any question a typed answer settles, so the 7 typed cases cannot override a typed answer. The 12 committed v3.1
objects the current code does not reproduce are explained in outputs/robgrade/V31_REPRODUCIBILITY.md; no score
changes.

## Round 3 (15 Oct): Claude Sonnet second reviewer (agy out of quota until ~06:00 UTC 17 Oct; Gemini pass OWED)
Verdict ACCEPT with two wording fixes (round3_sonnet.txt); it reproduced both defects, the xfail evidence and every
number of the measurement. Claude's adjudication: 1 ACCEPTED -- the request now states that replaying the 8
stale-adjudication trials under A4 no longer reproduces their objects (still-disputed questions fall back to NI)
unless the 8 adjudications are re-made live, naming each key and its questions. 2 ACCEPTED -- STALE READER rule: a
reader whose held record does not answer the current prompt is treated as a missing reader (no agreement computed,
no adjudication of the gap); xfail-strict test added. 3 ACCEPTED -- any two different raw answers (Y vs PY included)
-> NI + AMBIGUOUS_CONFLICTING_ROWS; identical duplicates are fine; tests added. 4 ACCEPTED -- the review records are
linked. 5 ACCEPTED -- the request says the frozen live mode already re-calls a manifest-stale entry. 6 DECLINED --
runtime is not a defect. Text revised by codex; 17 passed, 14 xfailed (strict); --runxfail shows each new test
failing at its intended assertion and the identical-duplicate control passing.
