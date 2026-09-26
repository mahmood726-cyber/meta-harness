# evid2's 35 and my 34 are different populations — and the overlap is only 19

Measured 2026-09-24 against `origin/main` (`1aaeb80c`, the ref evid2 pinned) and
`F:\claude-temp\TYPED_ARMS.json` (`61d11b7e`). Nothing landed.

## The disagreement, and it is not an off-by-one

    my population   (held cache/*/verified_arms.json entries, all four count fields)  : 34
    evid2's         (served count rows, 32 bound + 3 set aside)                       : 35

    in BOTH          : 19
    only mine        : 15
    only evid2's     : 16

Two numbers that look one apart describe **substantially different sets**. Tested rather than assumed:
`balanced-crystalloids-vs-saline-mortality` PMID 35041780, `colchicine-postop-af` PMID 25172965 and
`tocilizumab-covid19-mortality` PMID 33332779 are all in evid2's set and **absent from
`verified_arms.json`** entirely. Conversely PMID 29485925 is the only entry in that topic's
`verified_arms.json` and is not a served row.

    git show 1aaeb80c:docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json
      Mortality                      PMID 35041780  ai=530 n1i=2433 ci=530 n2i=2413
      New renal-replacement therapy  PMID 35041780  ai=306 n1i=2403 ci=310 n2i=2394

## Which denominator is the right one depends on the question

- **evid2's served rows are the gate's population.** `check_count_arm_ownership` walks the served
  `review.json` rows, so `COUNT_ARM_OBJECTS_MISSING` is counted over *those*. For the gate, evid2's 35 is
  the denominator.
- **My 34 held entries are the hand-binding population.** The `_tuple_in` percentage-wildcard and
  non-injective-witness defects live on the hand route, and 26 of 34 of those are digit-checked against a
  source span rather than the abstract.
- The 16 served-only rows reached the page by another route — CT.gov / AACT — which is exactly the
  architecture the second auditor pass identified: `target_endpoint.py:875` projects
  `endpoint_counts` down to bare `ai/n1i/ci/n2i` and discards the groupIds it just classified.

**Neither number was wrong; both were reported without naming the population they ranged over.** This is
the `lessons.md` trigger at cross-lane scale — a count is a reach figure until its denominator is named,
and two lanes can each be internally correct while their headline numbers cannot be compared.

`SCHEMA-count-observations-v2.md` has been corrected to state both populations explicitly rather than
implying one.

## A real case (d), in live served data

The new regression set requires: *two genuinely equal arm values with distinct witnesses -> PASS*, so
that the repair cannot degenerate into "the two numbers must differ". That case is not hypothetical:

    PMID 35041780, Mortality:  ai = 530, ci = 530

Equal event counts in both arms, with different denominators (2433 vs 2413), on a served page. A repair
that refuses equal values would refuse this authentic row. It should be used as a **real** case (d)
alongside the synthetic one.

## What evid2 already has, and what v2 adds

Their export is well built: `served_ref` pinned to a commit, `served_row_sha256` per row, registry arm
ids (`NCT02721654:433771710`), and an `arm_id_basis` naming how each role was matched. Their own note
says the main lane's schema *"was on no pushed branch when this was built"* — correct, and my fault: I
stopped the commit that carried it to free disk, so it reached them only as a file copy.

What v2 adds on top of what they have:

1. **Per-field, role-specific witnesses** (`event_witness`, `total_witness`) with coordinates, and the
   injectivity rule that four role-specific witnesses must yield four distinct coordinates. Their current
   export binds a row, not each field, so the non-injective attack is not yet excluded by their data.
2. **`group_id` as the authority for role**, which they already derive — v2 just fixes the field name so
   `observation_mismatch` can compare by name.

Their three set-aside rows are `dapagliflozin-hfpef-hosp` PMID 34711976 (the row whose denominator I
wrongly called fabricated and retracted) and the two `metformin-pcos-ovulation` `published_rate` rows.
