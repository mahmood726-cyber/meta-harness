# Analysis-set reading brief (one span)

You get one quoted sentence from a trial report or registry (SPAN) and the analysis set a meta-analysis page claims
for the served estimate (SERVED_LABEL). Classify what the SPAN states about the analysis set:

- ITT_STATED: intention-to-treat / all randomised participants analysed as randomised, with NO restriction
- OTHER_SET_STATED: a different or restricted set (modified ITT, at least one dose, available / non-missing data,
  per-protocol, safety population, treated set, a full analysis set with exclusions, or a set named without a
  definition such as a bare 'Full analysis set')
- NOT_STATED: the span does not state an analysis set at all

Output ONLY: {"key": "...", "reading": "ITT_STATED|OTHER_SET_STATED|NOT_STATED", "why": "..."}
