# Pre-registration: extractor test-retest agreement (written and committed BEFORE the sample is drawn)

Question: when codex extracts the same row twice, blind to its first answer, how often do the two extractions agree?
This measures the extraction INSTRUMENT, not the trials.

- Population: the 76 worklist rows (53 P5 + 23 U23). Sample: n = 20, drawn with `random.Random(20260924).sample(sorted(keys), 20)`.
- Procedure: the same EXTRACTION_BRIEF.md and the CURRENT packet; output to evidence/extractions/retest/<KEY>.json;
  the first extraction is not visible to the second (a different output path; the brief never mentions it).
- Primary measure: agreement on the BOUND NUMBERS (estimate, ci_low, ci_high, or the full count / mean set), as
  numbers (0.6 == 0.60); agree / disagree / not comparable (either side unbound), reported n of 20.
- Secondary: verdict agreement (BOUND vs SET_ASIDE); entry-population reading agreement; verbatim-span verification
  rate of the retest under the same gate.
- Stopping rule: one pass of 20; no re-draw; no tuning of the brief against this sample (it is burned once scored).
- Interpretation limits: packets changed between the two passes for some rows (companions added), so a disagreement
  may reflect new evidence rather than instrument noise; such rows are reported separately, by name.
