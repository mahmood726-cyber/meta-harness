**Blockers**
- Codex is at 2% until it resets. On the orchestrator's instruction, no codex jobs have run since then (Claude only). A cross-family second opinion on the M rows is therefore missing; the M second reads are Claude, blind or adversarial, and the report states it.
- The TECOS and TRANSFORM-2 errata texts are behind publisher bot checks, which are not bypassed. A human can read them directly.
- Nothing that changes a served number can land without Mahmood's signature. 5 changes are queued in `evidence/SIGNATURE_QUEUE.md`, 11 open questions sit in `evidence/OPEN_QUESTIONS.md`, and the label and citation corrections are queued in `evidence/LABEL_CORRECTIONS.md` and `evidence/CITATION_CORRECTIONS.md`.

**Next**
- After every main landing, rerun `stale_check.py`, which is now part of the lane gate. A ruling on a served number that has changed is re-read, not carried forward.
- When codex resets: run a cross-family, blind second read of the M citation and timepoint labels. Then one retest, extracting M-02 to M-15 with codex, to put a different model family on the extractions Claude made while codex was out.
- Final report at Sat 2026-09-26 15:00, then stop.

*Decided by the lane under delegated authority, 2026-09-25:* REPORT_2026-09-25.md is refreshed in place (the 03:34 version is preserved at commit 798a93ce) rather than written as a second file for the same date.
