# LANE HD2 — rebase the heredoc-escape guard (lane HD, built on 2a5e0ee9) onto the served harness (base 75cc9a46) as one landable increment; plant proven pre-fix on THIS base; nothing loosened.

Report file: `LANE-HD2-REPORT.md`. Fresh checkout of main at 75cc9a46. Record `git rev-parse HEAD`. Never reset/checkout/stash.
No commit. No network.

## Source
Lane HD's finished tree is parked at `F:\claude-temp\lanes-parked\mh-r-HD` (base 2a5e0ee9; read its `LANE-HD-REPORT.md` and
`STUCK_FAILURES.md` first). Its deliverables: `harness/safe_write.py` (verified byte/text writes: round-trip sha256 assertion at
writing; `WriteRoundTripError`), `scripts/write_file_verified.py` (the ONE sanctioned copy path), `scripts/lint_heredoc_escapes.py`
(refuses escape-bearing shell heredocs anywhere in the tree, including archived evidence; artefact `outputs/heredoc-escape-lint.json`),
the `safe_regex_scan` receipt (`UNVERIFIED_INSTRUMENT` when a pattern's bytes were not verified -- a zero-match from a broken pattern
is distinguishable from a correct zero), tests `tests/test_heredoc_roundtrip.py` and `tests/test_lint_heredoc_escapes.py`, a
verify_all limb that reads the lint artefact, `.github/workflows/verify.yml` (+1 line), and ~75 scripts whose `open(..., "w")`
writes were routed through `verified_text_open` (mechanical, 2-4 lines each).

## Work
1. `git diff` of the parked tree against 2a5e0ee9 (`git -C F:\claude-temp\lanes-parked\mh-r-HD diff`) plus its untracked files
   = the patch. Apply it to THIS tree with `git apply --3way`; exactly one known conflict (`scripts/refresh_error_rate_census.py`,
   touched by e3014d02) -- resolve by hand keeping both changes; list every other hunk that did not apply and what you did.
2. Plant FIRST on the untouched base (before applying anything): reproduce HD's historical plant on 75cc9a46 -- a `cat <<EOF`
   heredoc carrying `[/\\]` produces bytes that differ from the intended pattern; the base tree has no instrument that refuses
   the write, and a regex scan with the corrupted pattern either raises or returns a zero that is indistinguishable from a
   correct zero. Save the exact bytes (hex) and the outcome to `.tmp/hd2/prefix_plant.txt`. After applying: the round-trip write
   refuses (`WriteRoundTripError`), the lint refuses the heredoc, the scan receipt reads `UNVERIFIED_INSTRUMENT`; the fixed
   write (through `scripts/write_file_verified.py` or the Write tool path) reads `OK, matches: 1, pattern_sha256_verified: true`.
3. `python scripts/lint_heredoc_escapes.py --root . --artifact outputs/heredoc-escape-lint.json` => findings on THIS tree (expect
   0; if not 0, list them -- they are real defects, not to be silenced). Then `python -m pytest tests -q -p no:cacheprovider -x
   -k "heredoc or safe_write or roundtrip or lint"`, then the full unit suite (`python -m pytest tests -q -p no:cacheprovider`,
   counts verbatim).
4. Rebuild all 32 (`--now 2026-09-11`) -- the routed writes must produce byte-identical pages: report how many of 32
   `review_sha256` / `html_sha256` values changed (expected 0; any change is a defect in the routing -- name it, do not ship it).
5. `python scripts/retraction_survival.py 75cc9a46` => 32 of 32 or STOP. `python scripts/verify_all.py` if time allows.

## Report (MEASURED / INFERRED / CLAIMED; `n of N`)
The plant bytes and outcomes pre/post; the apply table (clean / 3-way / conflict-resolved / dropped, per file); lint findings;
pytest counts; the 32-page hash movement count; what this increment does NOT establish. Never a backslash escape through a
heredoc (use the Write tool or `scripts/write_file_verified.py` once it exists on the tree). No commit.
