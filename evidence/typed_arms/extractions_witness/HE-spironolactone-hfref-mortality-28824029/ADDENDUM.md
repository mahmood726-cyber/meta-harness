# ADDENDUM (v1.1) -- the schema owner's rule S2 (2026-09-25)

The registry result for this outcome prints only disjoint time-window components. The schema owner's rule: if the
TOTAL for each arm is printed in the trial's own prose, the prose total is the reported value.
- Witness each arm's EVENT count from the prose total (the abstract/text sentence that states how many died in each
  group), and each arm's DENOMINATOR where it is printed as a number (prose, or the registry's own per-group
  denominator for this measure). Set `ownership_source` to "REGISTRY_GROUPS" only if the counts come from the
  registry; here they come from prose, so use "PROSE_OR_TABLE", but still put the arm's registry `group_id` (the id
  of that arm's group in THIS outcome measure) in `group_id`.
- Add, per arm, `"component_corroboration": [{"group_id": ..., "class_title": "<verbatim>", "value": <int>,
  "witness": W}, ...]` -- one entry per registry component for that arm's group in this measure, each with its own
  token witness in doc_registry_*.json. Do NOT sum them; the checker compares.
Everything else in BRIEF.md applies (token-level witnesses, one occurrence per field).
