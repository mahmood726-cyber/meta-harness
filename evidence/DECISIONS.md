# Lane decisions

| date (UTC) | decision | who | basis |
|---|---|---|---|
| 2026-09-24 ~21:10 | Purge 15 leaked codex transcripts from the history of the public branch `evid/evidence-records` (filter-branch; force-push with lease on this branch only) | Mahmood answered the lane's question: the recommended option | a data leak of private workspace content; main never contained it |
| 2026-09-24 ~22:20 | Stop this lane's work on the 53 P5 populations and the count rows; hand off to Evidence lane two (`evidence/handover/EVID2_HANDOFF.md`) | owner instruction relayed by the main lane | avoid duplication |
| 2026-09-24 ~22:20 | Codex runs only in minimal job trees (`LANE_CONTEXT.md`, `-s workspace-write`, `-C <job dir>`); transcripts never enter the repo; every call is logged in `evidence/CODEX_CALLS.jsonl` with counts of private-file mentions | decided by the lane under delegated authority, 2026-09-24 | the main lane's hygiene report, plus this lane's leak |
| 2026-09-24 ~22:20 | The separate landing clone was deleted (2.3 GB; C: had 1.5 GB free); landings run from the worktree | decided by the lane under delegated authority, 2026-09-24 | disk |

From 2026-09-24 the lane asks no questions: every decision is taken on its own recommended default and recorded here as "decided by the lane under delegated authority, <date>". The one exception is any change to a served number, which is queued for Mahmood's hash-bound signature and never landed.
