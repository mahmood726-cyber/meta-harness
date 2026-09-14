# Harvested refusal events

Base commit: 3aedba0ecef0969551c761c8e91e29dccec88124

Offline harvest sources: local evidence captures, the run IDs named in LANE_PROMPT.md, and `git log --grep=REFUS -i`. No network or `gh` call was used.

| run id | gate | event id in registry | kind | commit | when UTC | status | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 34880195507 | `verify_all.limb_index_currency` | `verify-all-limb-index-currency-v1-true-refusals-2` | PRODUCTION | `7d5cda77` | 2026-09-14T18:32:09Z | enriched existing event `verify-all-limb-index-currency-v1-true-refusals-2` | commit:17a75f75, github-actions-run:34880195507 |
| 34854763935 | `verify_all.limb_unit_tests` | `verify-all-limb-unit-tests-harvest-34854763935` | PLANT | `a74b5c42` | 2026-09-14T14:19:20Z | added as explicit harvested event | docs/evidence/gate-authority-2026-09-14/03-refusal-plant-failing-test-not-deployed.txt, github-actions-run:34854763935 |
| 34855242632 | `ruleset.required_verify` | `ruleset-required-verify-harvest-34855242632` | PLANT | `bd57e490` | 2026-09-14T14:23:45Z | added as explicit harvested event | docs/evidence/gate-authority-2026-09-14/07-refusal-branch-route-red-check.txt, github-actions-run:34855242632 |
| 34856706877 | `verify_all.limb_index_currency` | `verify-all-limb-index-currency-harvest-34856706877` | PLANT | `c022cf46` | 2026-09-14T14:37:49Z | added as explicit harvested event | docs/evidence/gate-authority-2026-09-14/11-postfix-ci-refuses-hand-edited-index.txt, github-actions-run:34856706877 |
| 34871203144 | `verify_all.limb_heldout` | `verify-all-limb-heldout-harvest-34871203144` | PLANT | `fe8252cd` | 2026-09-14T16:52:59Z | added as explicit harvested event | docs/evidence/search-states-2026-09-14/04-ci-refuses-sealed-leak-and-missing-fixstate.txt, github-actions-run:34871203144 |
| 34871203144 | `verify_all.limb_fixstate` | `verify-all-limb-fixstate-harvest-34871203144` | PLANT | `fe8252cd` | 2026-09-14T16:52:59Z | added as explicit harvested event | docs/evidence/search-states-2026-09-14/04-ci-refuses-sealed-leak-and-missing-fixstate.txt, github-actions-run:34871203144 |

## Commit-message scan

`git log --grep=REFUS -i` returned 128 subjects. The scorecard harvest used entries that corresponded to failed verify/gate runs; recovery-log source refusals and historical gate-creation subjects were not added as gate-output events.
- `a3872489b684` 2026-09-14T21:57:39+01:00: Five-state ladder with verifier identity and assurance staleness; limitations-as-objects design + softening read; scorecard corrections
- `005f2fd27cb8` 2026-09-14T21:11:07+01:00: Block-level honest-state ratchet with adjudicated acknowledgements; structural query classes (a third state on 4 topics); the retraction sentence restored from the object on 32 of 32; a second non-author re-demonstration
- `1f6f8b67cbb4` 2026-09-14T20:42:14+01:00: Every evidence capture served as an HTML rendering beside the raw file; the bundle linked first from the served index
- `40e464a2069b` 2026-09-14T20:29:36+01:00: Fix state is a structured object; every gate has a measured scorecard (34 of 39 UNVALIDATED in production); regeneration accounted hunk by hunk: 15 pages lost a block
- `58909dbbf125` 2026-09-14T19:40:38+01:00: Fix ladder over the 40 existing claims: 28 VERIFIED by re-fetch, 12 downgraded to REPORTED (mechanism absent); prospective controls built; GATE_GAPS re-checked
- `17a75f751dca` 2026-09-14T19:32:09+01:00: Evidence index digests are of the SERVED bytes (LF-normalised as git commits them), not the working-tree bytes
- `7d5cda77d45e` 2026-09-14T19:18:23+01:00: Evidence entry pages in every evidence directory, generated from captions, with full URL and SHA-256 per capture
- `c6e1cdef73b3` 2026-09-14T19:02:57+01:00: Independent re-demonstration of today's claims (Codex lane G, fresh clone) + architecture identity as a computed value (lane H)
- `f928a536156d` 2026-09-14T18:49:56+01:00: Raw external inputs preserved in the retrieval ledger; explicit LEGACY_UNRECORDED ledgers for all 32 topics; pages rebuilt
- `6b1039cdb73d` 2026-09-14T18:26:40+01:00: Fix-state checker keys on STRUCTURE, not subject words; the prospective-validation freeze requirements recorded as spec
- `f156f89bc51d` 2026-09-14T18:13:23+01:00: Serve the evidence bundle from the Pages site: git mv evidence/ -> docs/evidence/ (same blobs), plus a cold-start index
- `b8925e043613` 2026-09-14T17:42:59+01:00: Retrieval class is an OBJECT state on all 32 pages; content hash labelled; honest-state RATCHET; artifact-identity closed
- `50f5a67b4fb1` 2026-09-14T17:40:21+01:00: Held-out register moves OUTSIDE the repo; the tree keeps a leak detector with a live canary. Fix-state trailers enforced.
- `d71959a24b3c` 2026-09-14T16:58:57+01:00: Artifact identity: build once, verify that artifact, deploy exactly it, fetch it back -- one chained record
- `73e9e5517598` 2026-09-14T16:39:11+01:00: Acquisition 5: the concept query RUNS on every fetch, first; no default record cap; first ledger-backed snapshot
- `a08ef8b4af1c` 2026-09-14T16:30:13+01:00: Acquisition 4: held-out recall measured and PUBLISHED (18 of 20); enforcement activated; the 6/6 demoted
- `312575022254` 2026-09-14T16:28:39+01:00: Acquisition 3: the held-out set as a MECHANISM (Codex lane B)
- `e1cd11ab663e` 2026-09-14T15:38:27+01:00: Gate authority: proof ledger (11 captures) + post-fix CI refusal of the hand-edited index
- `09c5c81b8fd0` 2026-09-14T15:33:11+01:00: Gate authority 3: one standard -- hook and CI both run scripts/verify_all.py
- `3541540f514e` 2026-09-14T15:24:28+01:00: Gate authority 2: main accepts a push only if `verify` passed on that SHA (ruleset, no bypass)
- ... 108 additional REFUS subjects reviewed but not scorecard gate-output events.
