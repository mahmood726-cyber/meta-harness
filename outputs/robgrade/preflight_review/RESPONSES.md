# Served-run preflight (scripts/rob2_served_preflight.py) -- second review, codex + Claude Sonnet

agy (Gemini) out of quota until ~06:00 UTC 17 Oct: the Gemini pass on every round below is OWED.
Non-model tool: predicts what `scripts/rob2_served.py --run` will do, without calling a model or writing a store.
Written by codex (16 Oct, night); every fix test-first (failing first). Codex reviewed with the code inline (its
read-only sandbox could not start processes); Sonnet reviewed by execution in a scratch copy.

| round | codex | Sonnet | Claude's adjudication |
|---|---|---|---|
| 1 | REVISE 4 | ACCEPT + 2 notes | ALL ACCEPTED: atomic --out (hard-link safe); any validation refusal -> REFUSED, every slot UNVERIFIED, no REUSE; explicit adjudicator states; real CLI check; REFUSED still writes its report; AACT snapshot + FT root recorded, STALE warning. |
| 2 | REVISE 2 | REVISE 3 | codex 1 PARTLY (blocked trials get no REUSE/CALL; a D8-violating record refuses all); codex 2 PARTLY (refuse --out inside any git work tree; DECLINED a hardcoded allowlist of this PC's paths). Sonnet 1-3 ACCEPTED: the preflight must PREDICT the driver: stale reader -> STALE + WOULD_REFUSE (driver re-calls, then accounting refuses), held adjudicator with agreeing readers -> CONFLICT, early refusal -> totals null. |
| 3 | REVISE (first pass lacked the driver source -- Claude's packet gap; rerun with it: 2 parity gaps) | ACCEPT | ACCEPTED: unreadable held reader -> QUARANTINE (adjudicator SKIPPED); RAN_OK entry with no held record -> WOULD_REFUSE, never CALL. |
| 4 | REVISE 1 (both round-3 fixes confirmed) | ACCEPT | ACCEPTED narrow: RAN_OK entry missing record_id or prompt_sha256 -> WOULD_REFUSE. |
| 5 | ACCEPT | ACCEPT (3 low) | lows recorded below, not changed. |

Unit tests are environment-independent (planted REUSE/STALE records; 48 passed with AACT_DIR, ROBGRADE_LOCAL_FT, ROBGRADE_DEV_OPEN_CC and ROBGRADE_FT_STORE unset, as in the gate; a broken copy fails 7).

Rounds 6-10 (tests only, after Claude found 7 tests failing with the gate's environment unset):

| round | codex | Sonnet | Claude's adjudication |
|---|---|---|---|
| 6 | REVISE (template from real store; inputs real) | REVISE 4 | ALL ACCEPTED: synthesize planted records with the driver's builders; ROBGRADE_FT_STORE -> empty temp dir; every private store starts empty; reports under tmp_path. (The hardcoded F: default in scripts/rob2_fulltext_acquire.py is flagged as a separate task.) |
| 7 | ACCEPT | ACCEPT + LOW (import-time STORE binding) | ACCEPTED: also patch acquire.STORE / UPW_CACHE / UPW_INDEX (failed first: preflight used the default F: store). |
| 8 | REVISE (session fixture leaks its patches into later tests) | -- | ACCEPTED: session collection closes its patch context before yield; consumers re-apply function-scoped (failed first: 2 leak checks). |
| 9 | ACCEPT | REVISE (driver module caches filled under the stub outlive the fixture) | ACCEPTED: snapshot/restore rob2_dual._AACT_REF, _AACT_DESIGNS, _REG_TEXT, _DEV, prompt_licence._TRACKED; checks cover every driver ROBGRADE_* name (failed first: _AACT_REF None -> {}). |
| 10 | REVISE (sys.path insert never undone) | -- | DECLINED: 230 of the repo's 431 test files insert into sys.path the same way (house pattern; Sonnet round 9: harmless). |

Verified by Claude/codex: 48 passed with the env unset and with it set; 83 passed with neighbouring rob2 test files in gate
order and in reverse order (dev-switch after the preflight); a broken implementation fails 7.

Real data (AACT 2026-08-30, LOCAL_FT=1, DEV_OPEN_CC=1): PASS -- 32 topics / 91 primary pairs / 65 todo; codex 56 REUSE /
0 STALE / 9 CALL; agy 65 CALL; adjudicators 65 UNKNOWN (depend on agy readings); D8: all 65 abstract-only, 0 blocked.
AACT 2026-04-12: WOULD_REFUSE -- corticosteroids-covid19-mortality::32678530 codex STALE, with the snapshot warning
(the held records were made with 2026-08-30; the live run must use that snapshot).

RESIDUAL (stated, not claimed away): the preflight RE-DERIVES the driver's decisions. Parity is tested for the cases
listed in its docstring; four review rounds each found a new edge case, so parity elsewhere is not proven. The
structural fix is a driver-level dry run (the driver's own code path with the model-call boundary stubbed to record
WOULD_CALL) -- on the register. Sonnet round-5 lows: a missing record_id with a stale hash is predicted WOULD_REFUSE
where the driver would re-call (cautious side); a redundant guard path already refused by check_manifest_records;
a non-dict manifest entry raises instead of a named refusal.
