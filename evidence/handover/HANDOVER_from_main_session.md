# Handover: the 53 P5 populations and the rows with no locatable source — this lane owns both from 2026-09-23 21:4x

From the main session (C:\meta-harness, branch `enforcement-gate`). Both pieces of evidence work are yours. **Two lanes
already ran on them tonight and their outputs are inputs for you, not conclusions** — review them hostilely before
building on them (did the plant fire before the fix; is each test asserting a property rather than a number; is
anything accepted on an exit code?).

## Artefacts to read first (all complete, none committed)
| what | where |
|---|---|
| EV53 — per-trial held evidence for all 53 | `F:\mh-g-EV53\EV53_REPORT.md`, `ev53.json` |
| SRC — the 23 rows with no locatable numerical source | `F:\mh-g-SRC\SRC_REPORT.md`, `src.json` |
| RLX — the relaxation chains that say how DEEP each row's problems go | `C:\meta-harness\outputs\findings-2026-09-22\lane-reports\RLX\` |
| B53 / B53X — the original bindability estimate and its strict re-read | same directory, `B53\`, `B53X\` |
| UA — why 23 of 46 served rows have no locatable source | same directory, `UA\` |
| the method for any recovery claim | `outputs/findings-2026-09-22/METHOD_recovery_claims_by_relaxation.md` |

## What is settled, with numbers you can use (don't re-derive)
- **The 53.** Each row's recorded `absence_code` IS its first failing check (`screen_family` returns at its first
  failure). RLX measured the ordered chain by relaxation: **33 of 53 clear the screen** (22 at depth 1, 8 at depth 2,
  2 at depth 3, 1 at depth 4); **20 of 53 excluded** because no faithful relaxation could be built.
- **Held evidence for those blockers (EV53):** 36 of 53 have held evidence for EVERY blocker, 16 PARTIAL, 1 NONE. Cut by
  depth: depth 1 → 21 of 22 complete; depth 2 → 8 of 8; depth 3 → 0 of 2 (both RECOVERY rows: COVID entry and the
  randomised comparison are held, but the assigned control is usual care, not placebo); depth 4 → 1 of 1 (EMPHASIS-HF,
  primary-report evidence for all four blockers; its registry design describes the other phase).
- **The 20 RLX exclusions are mostly not evidence gaps:** 5 are pure instrument limits (rows 3, 4, 10, 20, 29), 3 have a
  parent-identifier gap, **10 are probiotics rows whose configured entry rule mismatches the held prevention PICD** (the
  config names the OUTCOME as the entry population — a defect, not a judgement), 1 is a family-cardinality limit
  (CANVAS: both parents held, integrated report must be split), 1 is JUPITER's post-hoc entry mismatch.
- **The 23 rows with no locatable source (SRC):** all 23 are now locatable — 9 by a located span/cell, 14 by their full
  input set — and **all 23 replay EXACTLY** through the harness's own function, standard errors included. Causes: 14
  NEVER_HAD_A_SOURCE (computed), 8 SOURCE_EXISTS_NOT_RECORDED (stored as a prefixed/truncated/normalised string), 1
  registry-cell read. **Source location is closed; scientific attribution is not** — SRC flagged four conflicts that
  numerical replay does not cure: UA-042 (J-EMPHASIS-HF: a composite HR located under an all-cause-mortality row),
  UA-032/UA-033 (semaglutide: located but incompatible overall vs class-specific denominators), UA-004/UA-005 (RRR
  complement rounded; pre-round 0.43999999999999995 served as 0.44), UA-039 (DAPA-HF one-group selector ambiguity).

## The planning statement to build against
**22 rows are one repair from eligible; 11 need two or more; 20 cannot be assessed without new material.** Three kinds of
work, three confidence levels — resource them separately. A depth-3 or depth-4 row needs a chain of assumptions to hold
simultaneously and is rarely worth attempting.

## What is NOT yours to decide
The hand-eligibility route does not exist, and whether abstract text may stand at registry rank is **Mahmood's decision
D04**, not an engineering call. Evidence gathering, span location and format design are yours; adopting a route that
admits rows is not. Anything that changes a served number needs his signature — the 41 OPEN notices already need 33
individual ones.

## Hard rules inherited
Build in a worktree; land from a clean clone at origin/main; push every commit; prove a landing by FETCHED BYTES, never
an exit code. `main` is `38c04411`, unchanged and served; branch tip `9ff4c6b0`. Global codex cap is 3 slots: you get 1.
