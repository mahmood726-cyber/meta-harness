# Method: how to answer a recovery claim ("fix X and N rows return")

The positive counterpart to the two hazard files. Every recovery question on 2026-09-22 was answered by inference until
lane RLX did it properly; this is that lane's shape, generalised. Use it whenever an arrow appears between two counts.

## The question it answers
A row is blocked by a check. Someone proposes fixing that check and asks how many rows come back. The naive answer counts
rows whose RECORDED blocker is that check. That answer is wrong whenever another check fires first, later, or instead --
which is the *reported reason is not the binding constraint* hazard. A function that returns at its first failure records
the binding constraint at that moment and says nothing about what is behind it.

## The method
1. **Read the decision function completely and write down its real check order** and each check's precondition, with
   file:line. The sequence you report must be the function's order, not an assumed one. (`screen_family` has ten checks;
   RLX listed them all before touching anything.)
2. **Define a relaxation per blocker type, and justify each in one sentence**: the minimal, faithful change that makes
   exactly that check pass and touches nothing else. State per type what it does and does NOT touch.
   **A relaxation that does more than satisfy its own check is a broken instrument.**
3. **Freeze controls in BOTH directions before the sweep, and record them:**
   - a NEGATIVE control -- a row you know should still stop at a later check. If it clears, the relaxation is too
     generous.
   - a POSITIVE control -- a row you know should clear once its single blocker is relaxed. If it does not, the relaxation
     is too weak.
   Either failure **voids that instrument version**. Record every version tried and why it was replaced. RLX's v1 passed
   its controls but had a coverage limitation; v2 added a third positive control and re-ran the whole sweep. Revising for
   coverage is legitimate; revising because you disliked the answer is not, and the difference is visible only if both
   versions are kept.
4. **Iterate and record the ORDERED chain per row**, e.g.
   `ALLOCATION_NOT_RANDOMIZED -> INTERVENTION_CONTRAST_NOT_PROVEN -> BLINDING_NOT_PROVEN -> PLACEBO_CONTROL_NOT_PROVEN -> ELIGIBLE`,
   with a **depth** = the number of distinct blockers relaxed.
5. **Report depth, not just clearance.** Depth 1 and depth 4 are different propositions: one repair versus a chain of
   assumptions. A count that merges them hides the only planning-relevant distinction.
6. **Exclude, by name and with a reason, every row whose relaxation cannot be built faithfully** -- never guess one to
   keep the row in the numerator. RLX excluded 20 of 53 because supplying the missing PICD bundle "would clear other
   predicates too". Those exclusions are the instrument working, not a coverage failure.
7. **Stamp the downstream boundary on every count.** A screen-only result is not "these rows return": binding,
   extraction, variance model and compatibility all sit after it, and any of them can refuse. Repeat the boundary in the
   summary line, not only in a footnote.

## What it produced (2026-09-22, the 53 P5 set-asides)
B53's inferred "48 of 53 bindable" and "7 of 11 pools at k>=2" became, measured: **33 of 53 clear the screen (22 at depth
1, 8 at depth 2, 2 at depth 3, 1 at depth 4), 20 of 53 excluded by name; pools with >=2 clear rows: 4 of 11 at depth 1,
5 of 11 at any depth** -- and two pools (metformin-pcos, probiotics-aad) are effectively unreachable. Both original
figures were upper bounds and both moved down.

## The planning statement the depth distribution supports
**22 rows are one repair from eligible; 11 need two or more; 20 cannot be assessed without new material.** Those are three
different kinds of work with three different confidence levels, and they should be resourced separately. A route justified
by the depth-1 group is a different proposal from one justified by the whole 33 -- and the depth-3 and depth-4 rows (both
RECOVERY rows at 3; EMPHASIS-HF at 4) each need a chain of assumptions to hold simultaneously, which is rarely worth
attempting and never worth quoting as recovery.

## Trigger
Any arrow between two counts, any "would come back", any "fix X and N return". Run this, or label the number an upper
bound and name what it assumes.
