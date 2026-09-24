# BRIEF (WITNESS) -- token-level source witnesses for one held count entry

Read `LANE_CONTEXT.md`, then `row.json`, then the `doc_*` files it lists. `row.json.served` holds the entry's claimed
counts: `ai` events / `n1i` total for the INTERVENTION arm, `ci` / `n2i` for the COMPARATOR arm, for the outcome
`row.json.outcome_name`.

Your job: for each arm, find where the source states its event count and its denominator, and give the EXACT
coordinates of each NUMBER TOKEN.

## Where ownership must come from
- If `row.json.registry_results` lists a `doc_registry_*.json` file (a ClinicalTrials.gov record with posted results)
  AND that record's results contain this outcome (an `outcomeMeasuresModule` measure, or an `adverseEventsModule`
  event/term or the module's all-cause/serious totals that IS this outcome), the counts and arm ownership MUST come
  from that structure: the arm is the registry group (`groupId` such as "OG000" or "EG001"); its name is that group's
  `title`; events are the measurement / `numAffected` for that groupId; the total is the denominator for that groupId
  (`denoms` counts, or `numAtRisk`). Set `group_id` to that groupId.
- Otherwise use the prose or tables of the other documents and set `group_id` to null.
- If the registry has results but not for this outcome, say so in `notes` (name what you searched) and use prose.

## Output: write `out.json`
```
{
 "held_key": "<row.json.held_key>",
 "ownership_source": "REGISTRY_GROUPS" | "PROSE_OR_TABLE",
 "registry": {"file": "<doc_registry_*.json>", "module": "<module name>", "item_title": "<verbatim title of the measure or event>",
              "item_title_witness": W} or null,
 "arms": [
  {"role": "intervention" | "comparator",
   "group_id": "<registry groupId or null>",
   "arm_name": "<the arm's name exactly as the source prints it>", "arm_name_witness": W,
   "events": <int>, "event_witness": W,
   "total": <int>, "total_witness": W}
 ],
 "notes": "...", "not_found": ["..."]
}
```
`W` is `{"file": "<doc file>", "start": <int>, "end": <int>, "text": "<exactly the characters file[start:end]>"}` where
start/end are 0-based CHARACTER offsets into the file read as UTF-8 text (Python `open(f, encoding="utf-8").read()`).
For an event or total witness, `text` is ONLY the number token as printed ("2347", "4,949", "four", "91") -- not the
sentence, not the quotes around a JSON value.

## Hard rules
1. Compute every offset with a script and check `text == content[start:end]` before writing. Do not guess offsets.
2. ONE source occurrence may witness only ONE arm field. If both arms have the same number (e.g. 9 and 9), give two
   DIFFERENT occurrences (different start offsets), each one that belongs to its own arm. If the source prints the
   number once for both arms ("one patient in each group"), you cannot witness both: set that arm's field to null,
   explain in `notes`.
3. A percentage never stands in for a count or a denominator. Do not compute, sum or round. If a number is not printed,
   set it null and list it in `not_found`.
4. If a printed number differs from `row.json.served`, report the printed one and say so in `notes`.
5. Read only files in this directory; write only `out.json`.
