# BRIEF — which arm is the numerator of the reported ratio?

For every item in `items.json`, read the sentence and decide, from the WORDS of the sentence alone:

1. `numerator`: the arm whose risk/rate/odds is the NUMERATOR of the reported ratio (the ratio is numerator / reference).
   Use the arm name as written (e.g. "liraglutide", "placebo"). If the sentence does not let you tell which arm is the
   numerator, write `null` — do NOT guess from what is clinically plausible, and do NOT use the number's size
   (a ratio below 1 does not by itself tell you the drug is the numerator).
2. `reference`: the other arm (the denominator), as written, or `null` if not named / not determinable.
3. `measure`: "HR", "OR", "RR", "IRR", or "UNSTATED" — the ratio measure the sentence itself names.
4. `basis`: one short phrase quoting the words that decided it (e.g. "than in the placebo group", "for placebo versus
   liraglutide", "first-named group"), or why it cannot be decided.
5. `confidence`: "high" or "low".

The `arm_vocabulary` in `items.json` says which names are the intervention of interest and which the comparator.
Some sentences are deliberately ambiguous; `null` is a correct answer when the words do not settle it.

Write `out.json` as: {"answers": [{"id": "C01", "numerator": ..., "reference": ..., "measure": ..., "basis": ..., "confidence": ...}, ...]}
with exactly one answer per item id, nothing else.
