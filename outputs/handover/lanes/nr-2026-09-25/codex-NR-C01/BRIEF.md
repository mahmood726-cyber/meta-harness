# Task: independently re-judge 41 result-change notices (bulk comparison)

Each packets/NXX.json holds one OPEN result-change notice from a meta-analysis site and the data to check it:
- `ledger_notice`: the notice as recorded -- `before` and `after` result tuples (k, estimate, ci_low, ci_high),
  `left_pool` / `entered_pool` trial ids, `reason`.
- `served.outcome`: the outcome as the page CURRENTLY SERVED to readers shows it (`result`, `membership.pooled`,
  `pooled_trials`, `set_aside_or_absent`).
- `proposed.outcome`: the outcome as the page that carries the notice shows it.
- `rendered_block_text`: the notice text exactly as the reader will see it.
- `audit_claims`: what an earlier audit claimed (direction, mechanism, departing trials, recommendation).
- `direction_policy` and `orientation`: how to classify direction.

Do NOT trust `audit_claims` or the notice: check them against the page data. Compare numbers exactly
(no rounding) except where the rendered text rounds to 2 decimals.

For EVERY packet (41 of 41, none skipped) determine:
1. before_matches_served: ledger before == served.outcome.result (k, estimate, ci_low, ci_high; null == null).
2. after_matches_proposed: ledger after == proposed.outcome.result.
3. left_pool_exact: set(left_pool) == set(served pooled) - set(proposed pooled).
4. entered_pool_exact: set(entered_pool) == set(proposed pooled) - set(served pooled).
5. departing_reasons_ok: every left_pool id appears in proposed.outcome.set_aside_or_absent with a reason naming
   P5_family_eligible, and the reason's family-eligibility code agrees with audit_claims.mechanism_detail.
6. block_text_consistent: rendered_block_text states the same before and after (to its 2-decimal rounding), the same
   left/entered ids, and a conclusion sentence that is true of the change.
7. direction: your own classification under direction_policy and orientation (RESULT_REMOVED, RESULT_ADDED,
   NO_DIRECTION, AWAY_FROM_NULL, TOWARD_NULL, MEMBERSHIP_ONLY), and whether it equals audit_claims.direction.
8. before_after: ONE line a clinician can read, e.g.
   "HR 0.85 (0.78 to 0.93), k=3 -> no pooled estimate (k=0); left: PMID 1, PMID 2 (P5: population not established)".
   Use the scale from the outcome result; say "interval not served" where a CI is null.
9. verdict: "HOLDS" if 1-6 are all true and your direction equals the audit's; otherwise "DIFFERS" with reasons.
10. concerns: anything a hostile reviewer should look at (empty list if none). Be specific.

Answer with ONLY this JSON (no prose, no code fence):
{"verdicts": [{"audit_id": "N01", "before_matches_served": true, "after_matches_proposed": true,
  "left_pool_exact": true, "entered_pool_exact": true, "departing_reasons_ok": true, "block_text_consistent": true,
  "direction": "RESULT_REMOVED", "direction_matches_audit": true, "before_after": "...", "verdict": "HOLDS",
  "reasons": [], "concerns": []}, ...41 entries in N01..N41 order]}
