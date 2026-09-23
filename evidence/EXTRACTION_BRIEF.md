# Evidence extraction brief (one row)

You are given ONE packet (JSON) for ONE trial row served by a meta-analysis page. Every source the lane holds for
the trial is inside the packet as `sources[i].text`, already rendered to the exact text a span will be checked
against. Do NOT use any other knowledge of the trial as evidence. Do not run tools other than reading the packet.

Goal: for the served outcome (`served_outcome`) and this trial, bind SEPARATE verbatim spans for:

| field | what the span must state |
|---|---|
| population | who was randomised / entry criteria (the trial's entry population, NOT a subgroup, NOT background) |
| endpoint | the definition or name of the endpoint whose estimate is reported, matching `served_outcome` |
| estimate | the point estimate of the between-arm effect for that endpoint (or the per-arm counts / means it is computed from) |
| ci | the confidence interval of that estimate (may be the same sentence as estimate; copy it again) |
| analysis_set | the analysis population the estimate was computed in (ITT / mITT / per-protocol / safety set / "all randomised") |
| treatment_strategy | the assigned intervention and comparator AS RANDOMISED (dose / regimen / background therapy) |
| follow_up | the follow-up duration / timepoint at which the estimate applies |

Rules
1. A span is copied CHARACTER FOR CHARACTER from one `sources[i].text` (name that source by its `ref`). Minimal
   (<= 350 chars), but long enough to be unique in that text. Never paraphrase, never join two places with "...".
2. Prefer, in order: full text (`.xml`, `ft_*.txt`) > abstract (`records.json#...`, `europepmc_core.json`) > registry (`registry/NCT*.json`).
   A registry span is acceptable; say so.
3. If a field is not stated in ANY source, set it to null and give `absent_reason`. Do not infer.
4. Report the numbers you bound in `bound_values` (scale HR/RR/OR/MD/RD, estimate, ci_low, ci_high, ci_level, or
   counts `events_t,n_t,events_c,n_c`, or `mean_t,sd_t,n_t,mean_c,sd_c,n_c`) EXACTLY as printed in the span.
5. Compare with `served_row`. If the served number is not what the source states for this endpoint (wrong
   endpoint, wrong arm, wrong population/analysis set, component vs composite, different timepoint), say so in
   `served_mismatch` with the reason. REJECT THE CANDIDATE EXTRACTION, NOT THE TRIAL: if a correct span exists
   for a different number, bind the correct span and record the served candidate under `candidate_rejections`.
6. `verdict`: "BOUND" when population, endpoint, estimate and ci all have spans; otherwise "SET_ASIDE" with
   `set_aside_reason` from: SOURCE_NOT_HELD (only abstract/registry lacking the number), ENDPOINT_NOT_REPORTED,
   POPULATION_NOT_STATED, ESTIMATE_NOT_REPORTED, AMBIGUOUS_MULTIPLE_CANDIDATES, WRONG_TRIAL_DOCUMENT, OTHER (explain).
7. Also answer, with a span when possible, `entry_population_matches_question`: does the trial's entry population
   fall within `question`/`served_outcome.population`? values YES / NO / PARTLY / NOT_STATED, plus a one-line why.

Output ONLY this JSON object (no prose, no fences):
{"key": "...", "verdict": "...", "set_aside_reason": null,
 "fields": {"population": {"ref": "...", "span": "..."} | null, "endpoint": ..., "estimate": ..., "ci": ...,
            "analysis_set": ..., "treatment_strategy": ..., "follow_up": ...},
 "absent_reason": {"<field>": "..."},
 "bound_values": {...},
 "served_mismatch": null | "...",
 "candidate_rejections": [{"ref": "...", "span": "...", "why": "..."}],
 "entry_population_matches_question": {"value": "...", "why": "...", "ref": "...", "span": "..."},
 "notes": "..."}
