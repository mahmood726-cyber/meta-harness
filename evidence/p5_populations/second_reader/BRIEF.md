# BRIEF — blind second reading of population facts (evid2)

`row.json` names ONE trial, the review's `topic_requirements`, and a list of `facts`. For EACH fact, decide from the
`doc*.txt` files in this directory ONLY whether a document of THIS trial states it.

Verdicts (exactly one per fact):
- `STATED` -- a sentence of this trial's own document states the fact.
- `STATED_OPPOSITE` -- a sentence of this trial's own document states the opposite of what the fact requires
  (e.g. the comparator was usual care, not placebo; participants were children when the review excludes children).
- `NOT_STATED` -- no document here states it either way.

Rules:
- Evidence is a VERBATIM quote copied character-for-character from one `doc*.txt` file (you may drop the leading
  `<pointer>: ` prefix of a line; never paraphrase, never join text from two lines, never fix typos). Keep each quote
  under 400 characters and include the words that carry the fact.
- Never infer: an outcome name does not establish who entered (e.g. "antibiotic-associated diarrhoea" does not prove
  participants received antibiotics); a disease does not establish an age; "randomized" alone does not establish
  WHICH arms were compared; "double-blind" establishes masking but not placebo.
- A sentence about a DIFFERENT trial (a pilot, an extension, a pooled analysis, a review describing other trials) is
  not evidence for this trial -- set `other_trial: true` if the only support is of that kind, and verdict NOT_STATED.
- For `registry_parent`, the quote must contain the registration identifier itself.
- If documents conflict, report the conflict in `note` and give the verdict of the trial's primary report.

Write `out.json`:
```json
{"key": "<row.json key>",
 "facts": [{"fact_id": "...", "verdict": "STATED|STATED_OPPOSITE|NOT_STATED",
            "quotes": [{"file": "doc00_....txt", "text": "<verbatim>"}],
            "other_trial": false, "note": "<one sentence, optional>"}]}
```
One entry for every fact in `row.json`, in the same order. `quotes` is empty for NOT_STATED.
