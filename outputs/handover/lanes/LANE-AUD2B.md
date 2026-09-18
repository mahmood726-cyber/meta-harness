# LANE AUD2B — nine candidate violations of the deletion invariant found by an independent (Gemini) read of AUD2's tree: run each one-line mutation through the production route; every one that leaves assurance unchanged or better is closed; every one refuted is recorded as refuted with the code path.

Report file: `LANE-AUD2B-REPORT.md`. This clone is lane AUD2's finished worktree (read `LANE-AUD2-REPORT.md`; the family is `tests/test_deletion_invariant.py`). Never reset/checkout/stash. No commit. No network. Same ownership as AUD2 (`census.py`, `certificate.py`, `grade.py` assessability, `search_completeness.py`, `consumer_consistency.py`, `gate.py` new checks, `scripts/verify_all.py`, your tests). Do not weaken any existing check.

The candidates, verbatim (file:function:line as read on this tree; each with the one-line mutation that would prove it):
1. `census.py:support_violations:89` — deleting `core["reproduction"]["claim_check"]` skips `_claim_check` entirely (`if cc`); mutation: `del core["reproduction"]["claim_check"]; assert not census.support_violations(core)`. HIGH.
2. `census.py:support_violations:85` — deleting `core["reproduction"]["certificate"]["rendered_evidence_sha256"]` skips the seal check; the reproduction block is outside the core hash. HIGH.
3. `search_completeness.py:_check:1261` — deleting `split["assignments"][slug]["set"]` drops a failing topic from the MEASUREMENT loop → the gate passes. HIGH.
4. `grade.py:_inconsistency_domain:884` — deleting `res["pi_low"]`/`pi_high` skips the PI-vs-CI width comparison while the domain stays "assessed" with downgrade 0. HIGH.
5. `grade.py:membership_incomplete:749` — deleting `outcome["known_missing_sensitivity"]` makes membership read complete → the STALE penalty disappears. HIGH.
6. `grade.py:_domain_assessment:1026` — deleting a trial's `rob2.trials[id].domains` hides its unassessed domains from the certainty arithmetic. MEDIUM.
7. `census.py:_claim_check:190` — deleting `outcome["primary"]` skips the overview/manuscript significance scan. MEDIUM.
8. `certificate.py:compute:620` — deleting `cache/<slug>/families.json` binds the string `NOT_PRESENT` and the certificate verifies cleanly (landing 4 makes the family map a determinant of inclusion: its absence must now REFUSE, not stringify). MEDIUM.
9. `census.py:support_violations:66` — deleting `core["grade"]` skips `validate_arithmetic` (broken arithmetic becomes "not assessed"). LOW.

## Rules
- For each: run the mutation on a scratch copy of a real committed review (glp1 and iv-iron) through the production entry (`census.verify`/`build_review_dir`/`gate`/`certificate.compute`/`search_completeness.check`), paste the pre-fix result; if the verdict is unchanged or better → close it so the verdict DEGRADES (a missing required object is a refusal with its name; a missing optional object must be declared optional in code with the reason — and "optional" is never a support object); add the case to `tests/test_deletion_invariant.py`; paste the post-fix result. If the mutation already degrades the verdict → record REFUTED with the code path that catches it (the audit finding is then wrong for that item; say so).
- No default-valued read (`.get(..., {})`, `or {}`) on a required-support path may remain silent: list every such read you changed.
- Rebuild glp1 and iv-iron (`--now 2026-09-11`; if a rebuild blocker is outside your ownership, name it exactly), run `tests/test_deletion_invariant.py` and the AUD2 suite. `n closed / n refuted of 9`.

MEASURED / INFERRED / CLAIMED. Never a backslash escape through a heredoc; write regexes to files. No commit.
