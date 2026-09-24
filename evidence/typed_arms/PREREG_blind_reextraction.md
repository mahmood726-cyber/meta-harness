# Pre-registration: blind re-extraction of the 35 served count rows (evid2, 2026-09-24, before any blind output exists)

## Why
The first extraction's packet (`row.json`) carried the served F4B slots (`ai, n1i, ci, n2i`), the served `source` string
and the served `endpoint_result_span`. An extractor shown the answer can anchor on it: the gate proves every bound
number is printed in the held bytes and owned by its arm, but it cannot show that the extractor would have chosen the
same outcome, the same timepoint or the same analysis set without being told what was served. A blind re-extraction
measures that.

## Design (fixed now)
- Same model and settings as the first pass (`gpt-6-astra`, reasoning medium, workspace-write, one isolated job dir per
  row with LANE_CONTEXT.md), 2 codex slots.
- Blind packet: identical held documents; `row.json` WITHOUT `served`, `source`, `endpoint_result_span`,
  `analysis_set`, `follow_up_window`; it keeps the outcome NAME, the review's population/timepoint wording, the trial id
  and the registry arms. BRIEF_BLIND.md is BRIEF.md with the served-number sentences removed.
- The blind output is run through the SAME gate (G1-G3, G5-G7) against the same bytes; G4/G6 are not applied to it
  (they read served slots).

## Primary measure
Per ARM, over every arm of the 35 rows: does the blind extraction report the same (events, total) as the first
extraction, for the arm with the same arm_id? Reported as `n of N` arms, N = arms extracted by the first pass.
Secondary: per ROW, both arms agree; and the count of rows where the blind pass sets aside what the first pass bound
(and the reverse).

## What a disagreement does
Nothing automatically. Every disagreeing arm is read by eye against the held span of each pass and classified:
`FIRST_PASS_ANCHORED` (the first pass took the served number where the source supports another reading for the named
outcome), `BLIND_PASS_WRONG_OUTCOME` (the blind pass read a different outcome/timepoint/set than the served outcome
name), or `BOTH_DEFENSIBLE` (the source prints two readings for this outcome name). A `FIRST_PASS_ANCHORED` row loses
its BOUND state and goes to SET_ASIDE with that reason; if the other reading differs from the served number, it is
queued for Mahmood's signature -- never landed.

## Limits stated in advance
- Same model family as the first pass: this measures anchoring, not model-family independence.
- Agreement does not prove correctness; it shows the result does not depend on showing the extractor the answer.

## Addendum A (2026-09-24 ~23:45, before any blind output for these entries exists)
Extends the same design, measure and classification, unchanged, to the 18 HELD count entries extracted for the F4
schema (`extractions_held/`), whose packets likewise showed the extractor the held tuple. Blind packets drop `served`
and `source` from `row.json`. Primary: per arm, same arm_id (after `source_label_id` normalisation) and same
(events, total) as the first pass, `n of N` arms over the 18 entries' arms. A FIRST_PASS_ANCHORED entry loses its
direction and observations in `F4B_DATA.json`.

## Addendum B (2026-09-25, before any blind WITNESS output exists)
The witness packets (`extractions_witness/`) also showed the extractor the held tuple. A blind witness pass drops
`served` and `source` from `row.json` (same documents, same WITNESS_BRIEF with the served-number sentences removed).
Primary: per arm FIELD (events, total), does the blind pass cite a token with the same VALUE, and is it the same
occurrence (file, start, end)? Reported as n of N fields for value and, separately, for occurrence. A value
disagreement on a WITNESSED entry is read by eye and classified as in the main design; an occurrence-only disagreement
(same value, different printed place) is reported, not treated as an error.
