# Convergence: the RECOVERY comparator conflict was reached by two lanes from opposite ends (2026-09-22)

- Lane F1 (protocol-contract design, from the prose/config side): the eligibility chain's `comparator` dimension and the
  compiler's contract both treat a config `comparator_any` that lists "placebo" beside "usual care" as a screen rule;
  F1's design names `comparator` as a contract dimension with the prose value from the protocol's C-line.
- Lane B53 (eligibility screen, from the trial side): rows 5 and 53 (corticosteroids-covid19 / tocilizumab-covid19, both
  RECOVERY) are PARTIAL because `screen_family` demands a literal placebo arm whenever "placebo" appears among the comparator
  alternatives, while the protocol permits usual care and the held methods say usual care alone.
Same cell: protocol says {placebo | usual care}; executable screen says placebo required. Two methods, two populations
(pages vs rows), one defect -- evidence it is real and not an artefact of either method. One fix (the contract's
comparator cell consumed by `screen_family`) clears F1's comparator HARD cells AND the two B53 remainder rows (48 -> 50 of
53 bindable; 9 -> 11 of 11 emptied pools at k>=1).

## Double membership (2026-09-22, lane PH): the two RECOVERY rows are in TWO findings at once
Rows 5 and 53 (corticosteroids-covid19 / tocilizumab-covid19, RECOVERY NCT04381936) are (a) PARTIAL in B53 because of the
comparator rule conflict above, AND (b) in lane PH's eligibility-epoch mismatch class: the held registry criteria for the NCT
now describe a later influenza/CAP recruitment epoch while every linked report is the COVID-19 randomisation. Resolving the
comparator conflict does NOT resolve the epoch mismatch, and vice versa. Neither finding may be closed as "row 5/53 resolved"
on its own; each write-up must carry this line.
