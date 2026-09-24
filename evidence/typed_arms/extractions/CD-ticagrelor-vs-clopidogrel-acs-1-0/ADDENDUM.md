# ADDENDUM (v1.1) -- registry results JSON

The previous extraction for this row quoted an arm's label or denominator from a DIFFERENT outcome measure than the
events. In `doc_ctgov_results_*.json`, group ids ("OG000", "OG001") are defined separately inside EACH outcome measure
and can mean different arms in different measures. For this row:
- find the ONE outcome measure object whose "title" matches `row.json.outcome_name`;
- quote `arm_label_span` from that measure's own "groups" list (the `"id": "OG00x", "title": "..."` text);
- quote `total_span` from that measure's own "denoms" and `events_span` from that measure's own "measurements";
- every span for this row must lie inside that one measure object.
Everything else in BRIEF.md still applies.
