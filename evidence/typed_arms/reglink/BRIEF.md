# BRIEF — link written arms to registry group objects; search the registry for the row's outcome (evid2)

`rows.json` lists rows of one trial. Each row has an `outcome` and two arms (`role`, `arm_name`, `events`, `total`)
that were read from the trial's publication. Using `registry_<NCT>.json` ONLY (you may parse it with a script):

A. **Arm links.** For every arm, list EVERY registry group object that represents that same randomized arm, in every
   results module where groups are defined (`participantFlowModule`, `baselineCharacteristicsModule`, each
   `outcomeMeasures[i]`, `adverseEventsModule.eventGroups`). Give each as an RFC-6901 JSON pointer to the group object
   itself (e.g. `/resultsSection/baselineCharacteristicsModule/groups/1`), with its `id` and `title` copied exactly.
   Skip a group that is a total/overall column or a pooled/combined group; list it under `not_linked` with why.
   If the registry's arms do not correspond one-to-one to the row's two arms (e.g. several doses, a different
   comparator), say so in `arm_correspondence` and link nothing you are not sure of.

B. **Outcome search.** Look through every `outcomeMeasures[i]` and every adverse-event term (serious and other) for a
   measure of the row's `outcome` in the same randomized population. For each candidate give the pointer to the
   measure (or AE term), its title/term exactly, whether it measures the SAME outcome (`same_outcome`: true/false and
   one sentence why), and the per-group numbers it prints: `{"group_id", "value", "denominator"}` copied exactly, with
   pointers to the measurement and to the denominator count. Report candidates even when the numbers differ from
   the row's; never adjust a number. If nothing measures it, `outcome_candidates` is empty.

Write `out.json`:
```json
{"nct": "...",
 "rows": [{"row_key": "...",
           "arm_correspondence": "ONE_TO_ONE | NOT_ONE_TO_ONE: <why>",
           "arms": [{"role": "...", "arm_name": "...",
                     "links": [{"pointer": "...", "id": "...", "title": "..."}]}],
           "not_linked": [{"pointer": "...", "id": "...", "title": "...", "why": "..."}],
           "outcome_candidates": [{"pointer": "...", "title": "...", "same_outcome": true, "why": "...",
                                   "per_group": [{"group_id": "...", "value": "...", "value_pointer": "...",
                                                  "denominator": "...", "denominator_pointer": "..."}]}]}]}
```
Every row of `rows.json`, in order. Pointers must resolve in `registry_<NCT>.json` exactly.
