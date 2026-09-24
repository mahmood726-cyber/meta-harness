# BRIEF (BLIND) — typed per-arm observations for one count row

Read `LANE_CONTEXT.md`, then `row.json`, then every `doc_*` file listed in `row.json.documents`.

`row.json` names a trial, an outcome (`outcome_name`) and the review's population/timepoint wording. Your job is to
find, in the held documents only, what each randomised arm observed for that outcome, and to quote the exact text
that states it. You are NOT told any number the review uses; do not look for one.

Write `out.json` with exactly this shape (JSON, UTF-8, no comments):

```
{
 "row_id": "<row.json.row_id>",
 "arms": [
  {
   "arm_label": "<the arm's name as the document states it, verbatim>",
   "arm_label_span": {"file": "<doc file>", "text": "<verbatim substring that names the arm>"},
   "registry_arm_id": "<arm_id from row.json.registry_arms that is this arm, or null if none or no registry arms>",
   "registry_arm_basis": "<one sentence: which intervention words match, or why null>",
   "events": <integer or null>,
   "events_span": {"file": "...", "text": "<verbatim substring containing the event count for THIS arm>"} or null,
   "total": <integer or null>,
   "total_span": {"file": "...", "text": "<verbatim substring that STATES this arm's denominator as a number>"} or null,
   "total_basis": "RANDOMISED" | "ANALYSED" | "SAFETY_TREATED" | "STATED_UNQUALIFIED" | "NOT_STATED",
   "percentage_text": "<the percentage the document prints for this arm, verbatim, or null>"
  }
 ],
 "outcome": {"text": "<verbatim outcome wording>", "span": {"file": "...", "text": "..."}},
 "population": {"text": "<verbatim: who was randomised/analysed>", "span": {"file": "...", "text": "..."}} or null,
 "window": {"text": "<verbatim follow-up / assessment window>", "span": {"file": "...", "text": "..."}} or null,
 "notes": "<anything a reviewer must know: a count that is episodes not participants, arms merged, etc.>",
 "not_found": ["<field names you could not find in the held documents>"]
}
```

Hard rules:
1. Every `text` inside a span must be copied EXACTLY (character for character, including punctuation and spacing)
   from the named `doc_*` file, so that a program can find it with a plain substring search. Keep spans short
   (under 300 characters) but long enough to contain the number AND the words that tie it to the arm.
2. A DENOMINATOR must be stated as a number in the text (e.g. "(n = 4949)", "4949 were assigned to", "of 133 patients").
   A percentage NEVER stands in for a denominator: do not compute a total from events and a percentage. If only a
   percentage is printed, set `total` null, `total_basis` "NOT_STATED", and put the percentage in `percentage_text`.
3. Do not compute, round or infer any number. Report what is printed. If the documents print more than one
   candidate (e.g. two timepoints or two analysis sets), report the one that best matches `outcome_name` and list
   the others in `notes`.
4. List one entry per randomised arm that the trial compares for this outcome (normally two). If the source
   reports more arms (e.g. two doses) say which ones in `notes`.
5. A table row may be linearised with " | " or tabs; quote the exact bytes as they appear in the file.
6. Output only the JSON object into `out.json`. Do not read anything outside this directory.
