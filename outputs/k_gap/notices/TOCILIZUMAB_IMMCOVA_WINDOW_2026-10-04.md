# Notice for Mahmood: ImmCoVA is now read as a day-28 count (TIMEPOINT_EXCLUSIVE_BOUND)

Lane g1/tocilizumab-finish, 2026-10-04. **A notice only.** Nothing is signed, and nothing served changed. The tracker
was not regenerated.

**This supersedes question 1 of the 3 Oct notice.** That question was whether "day 29" may count as the day-28 window.
The new reading does not need that rule relaxed.

What ImmCoVA's open report states (PMID 38157348, PLoS One, CC BY 4.0, held):
- "There were 6 deaths up to day 29, two in each arm."
- "Two additional patients died on or after d29."
  - The S3 supplement places one of these deaths on d29, in the usual-care arm.
  - So the report itself counts the day-29 death OUTSIDE "up to day 29", and its window is days ≤ 28.
- Arm sizes: "27 to UC, 28 to anakinra and 22 to tocilizumab". A second sentence repeats the same sizes.

Result:
- The reading is 2/22 vs 2/27, randomised, which equals REACT's row.
- The route is PRIMARY: one bound primary that states the counts.

How the harness decides:
- `window_candidates` (g1/tocilizumab.py) applies the rule TIMEPOINT_EXCLUSIVE_BOUND, with plants W1–W7.
- It emits a day-28 row only when the report itself excludes the boundary day ("on or after d29") and that day minus
  one is 28. In addition, every arm-size statement must agree, and the per-arm deaths must add up to the total.
- "Up to day 29" with no such exclusion still stays "another day" (plant W2). Day 29 is now also refused by the
  sentence reader (plant T1).
- Radius: of the 16 held texts, only this paper produces a window row.

**To revert:** drop the `window_candidates` loop in `assess()`. ImmCoVA then goes back to NO_ROW, and n returns to 7.
