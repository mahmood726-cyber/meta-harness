# Decision on the POOL repair, and the codex lane ledger (CODEX-2)

Recorded 2026-09-24. Decision relayed by Dispatch under Mahmood's delegation. Nothing landed.

## Decision (Dispatch, under Mahmood's delegation)

1. **`publication_eligibility` must not collapse into `scientific_admission`.** Confirmed as the required
   repair for `POOL_F2_F3.patch`, per `28-POOL-breaks-every-control.md`.
2. **Do not special-case HARMONY.** PMID 30291013's status is handled under the **predeclared
   unresolved-evidence policy** and is **disclosed**, not suppressed and not routed around. This is the
   same §F.5 rule already applied to the masking screen and to BND1's `ESTIMAND_UNOBSERVED`: a checker
   disagreement is an evidence state, adjudicated under a policy declared in advance, never converted
   into a silent exclusion or a silent pass.
3. **The line-444 test must assert the PROPERTY, not the PMID.** The property is:
   - the five verdicts are **independent** — `publication_eligibility` is not a function of
     `scientific_admission`;
   - an inadmissible row is **disclosed**, and does **not silently pass** admission.
   The previous assertion named `POOL_PUBLICATION_INELIGIBLE` and `30291013` literally, which is a
   behaviour record rather than a requirement, and it defended the corpus-emptying defect.
4. **Keep F6C's conjunction bar**: 4 of 4 controls publishing AND 5 of 5 attacks refused with their exact
   intended first refusal. Neither half alone.
5. **Re-run F4D's end-to-end regression in a full tree** as soon as F6C releases one. F4D reported it
   NOT_REACHED because the tree it was given has no `scripts/` or `docs/`
   (`ModuleNotFoundError: No module named 'scripts.verify_bundle'`, `harness/gate.py:1295`) — a briefing
   fault of mine, not a lane failure. It correctly refused to substitute a gate stub.

**Note on lane F6C, already running when this decision arrived:** its brief says to rewrite the
assertion as "the requirement, plus the negative", which is close to but not identical with item 3. Its
output must be checked against item 3 as stated here, and amended if the rewritten assertion still names
the PMID or still couples the two verdicts.

## CODEX-2: a per-lane ledger of every codex call — adopted

Implemented at `F:/claude-temp/codex_lane_log.py`; ledger at `F:/claude-temp/CODEX_LANE_LEDGER.md`,
raw records at `codex_lane_ledger.json`. Per lane it records: workdir, model, provider, sandbox, session
id, tokens used, exec count, read-line count, the prompt's path, byte count and **sha256**, and every
filesystem path the transcript shows being read — partitioned into in-tree and out-of-tree.

**The headline field is out-of-tree reads**, because a lane reading outside its own tree is otherwise
invisible, and it has happened repeatedly on this project despite `LANE_CONTEXT.md`.

Retro-fitted across the six lanes run so far:

| lane | tokens | exec | read lines | wandered |
|---|---:|---:|---:|---:|
| F4 | 161,551 | 29 | 119 | **4** |
| F4B | 185,650 | 39 | 373 | 0 |
| F4C (stopped) | 69,956 | 10 | 83 | 0 |
| F4D | 96,851 | 23 | 108 | 0 |
| F6 | 485,667 | 90 | 2,515 | 0 |
| F6B | 151,242 | 86 | 191 | **2** |

**6 lanes, 1,150,917 tokens.**

Every out-of-tree read is one of the same four portfolio files:

    F4   -> f:/agents.md, f:/live_context.md, f:/projectindex/index.md, f:/e156/rewrite-workbook.txt
    F6B  -> f:/projectindex/index.md, f:/e156/rewrite-workbook.txt

### What this measures that we did not know

**`LANE_CONTEXT.md` does not prevent wandering.** F6B had it and still read the E156 workbook and the
portfolio index. That file was introduced *as* the mitigation for this exact behaviour; the ledger is the
first instrument that could show whether it works, and it says not on its own.

A second pattern, offered as a hypothesis and not as a finding: briefs whose **first six lines** carry an
explicit "Do not read or write outside it" wandered 0 of 3 (F4B, F4C, F4D); briefs without it wandered
2 of 3 (F4, F6, F6B). **The comparison is confounded** — all three opener briefs are later and all in
`F:\mh-f4`, so opener is entangled with both tree and time. Within `mh-f4` alone it is 1 of 1 without
versus 0 of 3 with. n = 6. That is a reason to put the opener in every brief, not a reason to believe the
effect size.

`BRIEF_F6C.md`, running now, has **no opener**. Its wandering should be checked when it finishes rather
than assumed either way.

### Deliberate exclusions, so the check is not muted

A check that cries wolf gets ignored, so these are filtered as noise rather than left to be eyeballed
away each run, and the exclusions are listed here so they can be disputed:

- the Python install tree (`.../python313/lib/pathlib/_local.py` etc.) — appears in every traceback;
- `c:/windows/system32/.../powershell.exe` — how the shell is invoked, not a read;
- `[a-z]:/n` — the path regex matching an escaped `\n` inside a quoted string;
- URLs inside the corpus documents (`https://` clipped to `s://`, and hostname-shaped first segments
  such as `/www.roche.com/...`) — document **content**, never a read;
- `F:/claude-temp/` and `/tmp/` — scratch directories lanes are given on purpose;
- a path written relative to the drive root that resolves to the lane's own tree (`/mh-f4/.tmp`).

The first three of those were false positives in the first version of this tool, found by running it and
reading the output rather than by trusting it.
