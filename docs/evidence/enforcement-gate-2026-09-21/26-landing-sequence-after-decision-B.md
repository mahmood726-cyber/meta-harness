# Landing sequence after Decision B, and the one test POOL must pass first

Written 2026-09-24. Nothing in this file has landed. Every tree is named beside every number.

## Ground truth, measured not assumed

    GitHub origin/main            41f3e2d0   (2026-09-24 18:24Z)
    newest commit consistent with
      the SERVED bytes            752e9c1f   (2026-09-24 18:05Z)
    enforcement-gate (branch)     1fa77f2c   — NOT on main; this is the judged_commit
    the four patches were built on a4e556e3, which IS an ancestor of main

`d10b0d24` and `41f3e2d0` are on GitHub and **not live**. See the release-identity correction in
`20-auditor-reply-second-assessment.md`, proven on two artefacts by fetched bytes.

## The sequence

**1. REGSPAN — ready, moves nothing served.** One file,
`tests/test_registry_result_span_carries_the_number.py`, whose blob is byte-identical on `a4e556e3` and on
current main (`dc178b19`), so it applies to the tip unchanged. It replaces a bare-substring check with a
digit-bounded one, records that the branch it guards is UNEXERCISED on this corpus, and uses a constructed
row because no corpus row can reach it. Tests only — no served number can move.
**Blocked only by disk** (the first attempt died with `No space left on device` mid-checkout).

**2. POOL — evidenced, but NOT yet cleared to land.** The F6 pre-fix run shows five pool-linkage attacks
reaching publication with `first_refusal: null` and `GATE PASS`, and the patch's codes map onto all five
(verified against the patch text, not a summary). F6B is now measuring the post-fix half.

> **The gate POOL must pass before it lands, and it has NOT been run:** POOL adds refusals. A refusal that
> fires on a currently-served pool is a served-number change, which is Mahmood's signature, not mine.
> F6's baseline PASSes only establish this for **1 of 32 topics** (`glp1-ra-mace-t2d`). The corpus-wide
> question — does `check_pool_contract` refuse any of the 32 served topics as they stand? — is
> **UNMEASURED**. Until it is measured, "POOL moves nothing served" is an assumption, and this file
> records it as one rather than letting it pass as a finding.

**3. ARM_final — measured as moving nothing served**: over all 35 held pair-entries, 11 BOUND,
24 NO_ARM_EVIDENCE, **0 CONTRADICTED**, so switching the refusal on moves no served number today. Same
corpus-wide caveat applies in weaker form: the measurement is over held entries, which is the population
that can move.

**4. MASKING — must not land in its current form.** Ruled in `21-decision-estimand-repair-under-F5.md`:
abstaining on a registry/abstract disagreement turns an evidence-state uncertainty into a scientific
exclusion, which §F.5 forbids. Restructure to adjudication under a predeclared policy first.

**5. F4B (denominator) — moves served numbers by construction.** 4 of the 7 exposed rows refuse after the
repair. Goes to Mahmood, not to a landing decision of mine.

**6. Page-rebuilding landings — after B**, per Decision B. B is now verified
(`25-hostile-check-of-lane-B.md`); the 41 notices carry their signing hashes in
`24-the-41-notices-for-signature.md` and are anchored to `1fa77f2c`, so a rebuild no longer detaches them.

## BND1 and POOL

`23-finding-BND1-and-POOL-have-different-baselines.md` recommends rebasing POOL onto `enforcement-gate`.
The F6 evidence changes the weighting: the linkage gap is demonstrated **on main**, and POOL repairs it
**on main**, so landing POOL to main directly is the better-evidenced route and does not require the
branch. BND1 stays on the branch, where it must have the §F.5 restructure applied before any merge —
merging and landing in one step would reimport the corpus-emptying behaviour.

## Disk, because it is currently the binding constraint

`F:` is a 466 GB volume at 100%. I reclaimed 1.8 GB by deleting `/f/mh-land-rs`, which is reconstructible
from main plus the four patches (all secured on `C:\mh-artefacts\patches`). The sixteen `mh-g-*` lane
directories were already emptied in an earlier pass — each now holds only a locked `.tmp` — so there is
nothing further to reclaim there; an attempt to delete them freed 0.00 GB. The remaining space is the
user's own portfolio and is not mine to remove.
