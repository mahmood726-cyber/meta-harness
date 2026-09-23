# Notes for the next landings (2026-09-22) -- things measured today that a landing must carry

## F5 landing: the coverage line is a served-site disclosure, independent of any disagreement
An independent screener judgment exists on 5 of 32 pages and covers 53 of 269 included rows (216 of 269 ADJUDICATOR_ABSENT;
3,063 of 3,146 screening rows). Absence must never be counted as agreement (lane F5 refused to). The page should carry
"independent screening: n of N included rows judged" per page, and the corpus line above, whether or not anything disagrees.
5 of 3,146 rows disagree; 0 of 5 are pooled.

## F2 decision -- cost of each branch, measured (regex over held abstracts/full texts: ITT / FAS / per-protocol / modified
## intention / all randomised / treatment-policy)
If analysis-set is a HARD sourced dimension: 18 of 19 numeric primaries are affected, carrying 33 pooled trial rows.
Full text held for 6 of 33 (all 6 state an analysis set). Abstracts state one for 0 of 33. So 27 of 33 rows need a full text
FETCHED and read before those primaries return -- not bounded by held material. If analysis-set is a declared assumption:
0 fetches; 14 of 97 outcomes render "analysis population: assumed from protocol (intention-to-treat), not sourced per trial".

## Bound-verified-wrong-span (FINDING_bound_verified_wrong_span.md): V007 and V019 are pre-fix plants already observed.

## design_masking / placebo-as-blinding (FINDING_design_masking_andor.md): 5 of 19 served rows load-bearing on 38c04411.

## RECOVERY rows 5 and 53 are in two findings (comparator conflict AND registry epoch mismatch) -- see CONVERGENCE note.
Closing either finding must not mark the row resolved; the row needs both.
