# DOAC-VTE: a protocol-permitted mixture is labelled as one; narrative rules for generated text (branch only)

## (1) The label

The primary pool mixes 5 HRs with AMPLIFY's RR under the label "HR" (`scale_mixed: [HR, RR]`).
- The protocol permits the mixture ("this mixed HR/RR pool is declared ..."). That exact declaration is now the topic's
  `measure_mixture_policy` with `basis: protocol`.
- The label derives as **"mixed ratio (HR+RR, approximation per protocol)"**. A sensitivity analysis restricted to the majority
  measure is computed and shown on the page.
- Numbers, reproduced with `synth.pool`: mixed **0.909108 (0.747947-1.104993)**, k=6; HR-only **0.926524 (0.732709-1.171606)**,
  k=5. Both match the review.
- **Registration caveat, recorded in the policy.** The protocol sentence was committed in 4fc26ade (2026-09-12) together with the
  topic build: a build commit, so the mixture is per protocol but NOT demonstrably prespecified before the data were seen.

## (2) Narrative rules (`harness/narrative_rules.py`; publication gate `check_narrative_no_ni_inference`)

- **No NI / equivalence inference.** A page sentence making a noninferiority / equivalence / comparable-efficacy CLAIM passes only
  as a verbatim quotation of held source text (abstracts and titles; the source text on either side of the phrase must match, so a
  truncated quotation still counts). Otherwise the gate refuses the page.
  - The first version flagged 15 false positives on 9 served pages ("not equivalent to", "Embase-equivalent", "equivalent doses",
    quoted titles, a truncated quotation). It was fixed to claim constructions only, with negation exempt.
  - Now 0 of 32 served pages are flagged, and the three planted inferences are refused.
- **Strategies, not bare drugs.** `strategy_label()` reads the held abstract:
  - RE-COVER ("initially given parenteral anticoagulation") and RE-COVER II ("treated with LMW or unfractionated heparin for 5 to
    11 days") -> **parenteral lead-in then dabigatran**;
  - Hokusai -> **parenteral lead-in then edoxaban**;
  - EINSTEIN-DVT / EINSTEIN-PE -> **rivaroxaban alone**; AMPLIFY -> **apixaban alone**. AMPLIFY is read from "apixaban alone", not
    from "major bleeding alone".
  - Stated as NOT_STATED_IN_HELD_TEXT otherwise, never guessed. Each pooled row carries `treatment_strategy`.
- **Populations literally.** `populations_stated()` records only what the held abstract states. AMPLIFY's abstract states none: its
  efficacy population (patients with documented 6-month status) and on-treatment safety set are in the full text, which is not held.
  The derived label already refuses to assert an unstated "intention-to-treat".

Not built end to end: both drives are below the 3 GB regeneration floor.
