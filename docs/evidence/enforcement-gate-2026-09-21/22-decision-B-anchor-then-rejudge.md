# Decision B: anchor every notice to the version it judged, then re-judge the 41 once

**Decided by:** Dispatch, under Mahmood's delegation.
**Date:** 2026-09-24.
**Scope of the delegation:** engineering decisions. **Signatures on result-change notices remain Mahmood's.**
The bulk acceptance Mahmood gave covers the **AI screening proposals only — NOT result-change notices.**

## The question that was answered
41 result-change notices await signature. Each records a judgement made against one specific version of a
review page. `scripts/sign_walk.py:101` pins a sha256 per page and refuses to present a notice whose bytes
have moved — so a rebuild detaches them. Today's rebuild detached all 41. Measured: **51 of 78 pinned source
paths changed; 41 of 41 notices had their own evidence page change; the 27 that survived are exactly the
commit-pinned `git:<sha>:<path>` entries.**

The refusal is correct behaviour, not an obstacle: re-pointing a notice at a new page would put a signature on
a judgement of bytes nobody examined. *The reference standard would not be wrong, it would be LATER* — which
looks exactly like a correct one.

## The decision
**Option B.** Convert every notice's page evidence to a commit-pinned reference, so each adjudication states
WHICH VERSION it judged, then redo the 41 judgements once against a named commit.

Rejected: Option A (re-judge now against today's pages, leaving working-tree anchors). Same cost today
(8-12 lane-hours either way) but it recurs on every landing that rebuilds pages, and every future landing that
touches a pinned module rebuilds pages.

## Consequences for sequencing, as directed
- **Do not hold finished patches behind B unless the landing genuinely has to rebuild pages.**
  - `REGSPAN.patch` — tests only, touches no pinned module, changes nothing served -> **lands now**, proven by
    fetched bytes.
  - `MASKING.patch` (`harness/screen.py`), `ARM.patch` (`harness/pipeline.py`), `POOL+F2+F3`
    (`harness/gate.py`) — each edits a module pinned in `analysis_code_blobs`, so each re-derives all 32
    certificates and rebuilds pages -> **sequenced after B**.
- `BND1` and `POOL` both edit `harness/gate.py` and `scripts/verify_bundle.py` and conflict textually; they are
  to be **merged properly**, not re-applied over one another.
- When the 41 are re-judged: each one's **before -> after line and rendered hash** goes to Mahmood for
  signature. Nothing is signed by the system or on his behalf.

## The property the re-judging must preserve
An adjudication is only worth the version it names. Every re-judged notice must record the commit it judged,
and the walker must refuse any notice whose recorded version is absent — a convention that relies on someone
remembering will be broken by the next person in a hurry, and it fails silently.
