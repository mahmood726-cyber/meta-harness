# Handover to the main lane — regex layer findings in files this lane does not own (2026-09-25)

This lane planted every regex site its inventory can see in `harness/`: 407 of the 407 sites `regex_layer.inventory`
finds. There are 19 run-time-built patterns outside the inventory and unplanted: 9 built by concatenation, including
`hand_binding._present`, which reads number fragments. The full list is in
`outputs/handover/lanes/RAI_RELEASE_NOTE_2026-09-25.md` under "R3 coverage, exactly". This lane edits only the files it owns
(`regex_layer/OWNERSHIP.md`). Everything below is in the main lane's files; the fix is yours. Each is a strict xfail in
`regex_layer/defects.py`, so your fix flips it to a pass and its entry must be removed then. Plants in your files are
never a gate on your commits: a pattern you change is skipped as STALE (`regex_layer/lanes.py`).

## Served now, and wrong
1. **The blind comparator page serves the auto trial count even where a source-verified one exists.**
   `harness/pipeline.py` `build_comparator_core` (≈ line 2286) has no `comparator_k` override path. The review page
   honours `comparator_k`; the blind page does not.
   - omega3-cardiovascular-events: the blind page shows **8**, where the verified count is **28**.
   - Measured in `outputs/regex_layer/RADIUS_fix_k.json`.
2. **16 review pages print "theirs_k: not stated in the comparator abstract/full text"**, although every comparator
   abstract states the count. The cause is `extract._parse_k`, which takes only the FIRST `_K` match (RX-X6).
   - A better regex is **not** the fix. The candidate `_K` agrees with the recorded proposals on most topics but not
     all: colchicine-secondary 3 vs 15, statins 40 vs 12.
   - The source-verified path exists: recorded proposals, 4 of 4 controls agree
     (`outputs/model_source/COMPARATOR_K.md`), signed into `comparator_k`. That needs Mahmood's individual signature.

## Reachable and consequential (effect on a served row not measured unless stated)
| id | file | defect |
|---|---|---|
| RX-OL23 | absence.py | `_ESTIMAND_SUFFIX` strips the conjunction 'or' from 41 outcome keywords; 25 held sentences dropped |
| RX-OL31 | reason_audit.py | 'N patients were randomly assigned to' gives no per-arm denominator (43 records) |
| RX-OL38 | arm_object.py | '`N weeks`' has no plural; 210 records get no timepoint |
| RX-OL39 | design_key.py | the NEJM 'hazard ratio, 0.60; 95% CI' form is unread in 28 pooled rows |
| RX-OL40 | arm_object.py | semaglutide 0.5 mg / 7.2 mg not recognised (22 records) |
| RX-OL41 | trial_family.py | ChiCTR / IRCT / CTRI / UMIN / DRKS / PACTR ids are not registry ids (40 pairs) |
| RX-OL15 | funding.py | sponsor split on '&' ('Johnson & Johnson' becomes two sponsors; 9 lists) |
| RX-OL17 | hand_binding.py | table rows with attributes dropped (17 rows) |
| RX-OL32 | consumer_consistency.py | abbreviated 'OR 0.34, 95% CI' not counted as a published effect |
| RX-OL9 | funding.py | 'Inc.' before a space never matches; 2 documents change class |

The full list, including the latent ones, is in `regex_layer/defects.py` (every RX-OL entry says latent or
reachable).

## What this lane landed in its own files
- R1 typed values, R4 number-fragment refusal, `_NEQ` boundary and RX-D1 fixed (`c82e86bd`).
- Next pinned landing (being re-certified):
  - R1 in screen.py / eligibility_chain.py;
  - owned defects RX-TE1..3, RX-EC1..3 (RX-EC2: colchicine-recurrent-pericarditis gains its follow-up-window
    criterion);
  - four zero-radius R4 fixes (_ANCHOR_RX plural, _SUBGROUP, _RECURRENT_PERSONTIME, the U+2007/U+2008 separators).
