# Task: for each of 78 trial memberships, say what ACTUALLY caused an eligibility check to fail

A meta-analysis site removed trials from pooled results because a structural eligibility check ("P5") returned a
code. `p5_source.py` is the check's source, verbatim. `packet.json` has, per item, the code the check returned
(`gate_code`) and the held registry rows it read (`registry_design`, `registry_conditions`, `arms` with
`active_interventions` and `linkage_complete`, `randomised_contrasts_derived`, `family_identity_registry_ids`), and per
review (`topics`) the terms the check searched for (`intervention_agents_searched`, `population_any_terms`).

The question for each item is NOT "is the trial eligible?". It is: **does the returned code reflect evidence that is
genuinely absent from the held rows, or does the check fail for a reason in how it reads those rows?** Read the
source and apply it to the rows yourself. Where it is cheap, re-run the logic in python on the item's rows.

Classify each item into exactly one of:
- ACTIVE_COMPARATOR: the contrast check cannot represent a drug-vs-other-active-treatment comparison (read
  `randomised_contrasts`: it needs the arms to differ by the agent alone).
- CONTROL_CODED_AS_ACTIVE: the control (placebo, saline, vehicle) appears as an active intervention in the arm
  rows, so the arms differ by more than the agent.
- LEXICON_GAP: the trial's intervention is plausibly the review's intervention class but its name is not among
  `intervention_agents_searched`.
- NOT_DERIVABLE_FROM_ARMS: the arm rows do not carry the contrast at all.
- WILDCARD_NOT_HONOURED: a population term uses a wildcard (*) that the substring test treats literally.
- TERM_FORM_MISMATCH: the registry condition names the review population but in a word form or synonym the
  substring test misses (e.g. inverted MeSH order).
- CONDITIONS_TOO_GENERAL: the registry condition is a broader category than the review population.
- CONDITIONS_DIFFER: the registry condition names something other than the review population.
- NO_REGISTRY_PARENT_LINKED: no registry record is linked (`family_identity_registry_ids` empty).
- NON_CTGOV_REGISTRY: the family is anchored to a non-ClinicalTrials.gov registry and the check has no design /
  conditions / arms rows for it.
- INELIGIBLE_ON_HELD_EVIDENCE: the check returned INELIGIBLE on the rows it read.
- OTHER: none of the above (explain).

Also give `genuinely_absent`: true when the held rows really lack what the check needs, false when they contain
it and the check misses it, "partly" when mixed.

Answer with ONLY this JSON (no prose, no code fence), 78 entries in item order:
{"items": [{"item": "M01", "class": "...", "genuinely_absent": true, "basis": "one sentence naming the rows"}, ...]}
