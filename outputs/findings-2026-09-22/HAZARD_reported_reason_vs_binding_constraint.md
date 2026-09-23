# Standing hazard: the reported reason is not the binding constraint

A lane reports the reason it was looking for. The build stops at the reason it hits FIRST. When those differ, every
"fix X and N rows return" claim derived from the lane is an estimate, and it will be quoted as a plan.

## The instance (2026-09-22)
Lane B53 diagnosed the two RECOVERY rows (corticosteroids-covid19 PMID 32678530, tocilizumab-covid19 PMID 33933206) as
blocked by the comparator rule: `screen_family` demands a literal placebo arm whenever "placebo" appears among the
permitted comparators, while both trials' held methods say usual care alone and both protocols permit it. B53X agreed.
From that, the counterfactual 48 -> 50 of 53 bindable and 9 -> 11 of 11 emptied pools at k>=1 was derived, relayed to
Mahmood, and held by him as a plan.
Lane CMP then implemented the comparator fix (plant observed failing pre-fix; control unmoved) and **ran the real build**:
both rows fail `ENTRY_POPULATION_NOT_ESTABLISHED` BEFORE the comparator test is reached. Both pools stay at k=0, both
pages still render UNKNOWN, both gates still REFUSE. The fix is correct and changes nothing for those rows. Measured
effect across 3,489 family entries: 10 eligibility cells change in 7 topics, and **0 of 6** baseline
PLACEBO_CONTROL_NOT_PROVEN families become ELIGIBLE -- the fix is net STRICTER (four unmatched-comparator families move
from unchecked to UNKNOWN).

## Why it is its own hazard, not the incomplete-representation one
The incomplete-representation hazard is about a search that found nothing because it looked in the wrong place. This one
is about a diagnosis that is CORRECT about its own subject and irrelevant to the outcome, because the code under test
short-circuits earlier. Both produce a confident number; only this one survives a re-read of the same evidence, because
the evidence really does say what the lane said it says.

## The cure, operationally
**A recovery claim ("fix X and N rows/pools return") is UNPROVEN until the real build is run and the FIRST failing check
is observed for each named row.** Concretely:
1. For every row in a recovery claim, print the check that actually fires in a real build, before and after the change.
2. Prefer the row's own recorded state to a lane's narrative: a function that returns at its first failure records the
   BINDING constraint, so `absence_code` beats any prose diagnosis about the same row. Where a lane's "what is needed"
   names a different constraint than the row's recorded code, that mismatch is the tell -- check it before quoting.
3. Say "upper bound" out loud whenever a counterfactual holds one check constant and assumes the rest pass. An
   eligibility-only counterfactual is an upper bound on eligibility grounds alone; it says nothing about the endpoint
   binding (P8), the effect extraction, the variance model or compatibility, each of which can fire later.
4. Quote a recovery number only with the check sequence it assumes, e.g. "k>=2 on eligibility grounds; P8 and extraction
   not evaluated".

## Trigger, syntactic
You are about to write "fix X and N return", "would come back at k>=", "takes A to B", or any arrow between two counts.
Name the check that fires first for each row, from a real build, or label the number an upper bound and say what it
assumes.
