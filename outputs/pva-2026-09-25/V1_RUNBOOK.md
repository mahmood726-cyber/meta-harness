# V1 runbook -- page-verifier and archive lane (Sat 26 Sep 2026)

Plan (Mahmood): integration freezes **09:00**; main lane regenerates and deploys by **15:00**; V1 goes live only if no
served number moves unsigned. This lane: hostile acceptance of the candidate against checklist 18 (A-E; §F unpublished)
and every probe, re-run on the SERVED bytes after deploy; the frozen V1 archive; page.py naming its verifier; the
independent "what V1 proves / does not" section.

Tools (branch `pva/v1-acceptance`, pushed):
- `outputs/pva-2026-09-25/v1_accept.py` (local working copy: `C:\mh-lanes\pva\v1\v1_accept.py`)
- `scripts/release_archive.py build-release` (D11 whole-release archive)
- `outputs/pva-2026-09-25/V1_RELEASE_NOTE_independent_section.md` (DRAFT)
Work dirs: F:\claude-temp\claude\C--rmfw\8b65f96e-4468-481b-b9d4-307b02c07609\scratchpad\ (C: is near full).

## T0 = freeze (09:00): candidate sha announced by the main lane
1. `git fetch origin`; identify the candidate commit `<V1>` and the previous served release `<PREV>` (the last commit with an
   ATTESTED production record before V1).
2. Rehearsal on git bytes (not acceptance):
   `python v1\v1_accept.py --release <V1> --prev <PREV> --work <F:>\v1cand --source git`
   Blockers to raise at once, in AUDIT + REPORT: P2 != 32/32, P3 FAIL (a page names a stale verifier -- rebuild), P4 any
   UNSIGNED, P5 baseline not PASS, P6 regressions vs the rehearsal table, P5b missing (checklist B4 not met).
3. Build the archive from the candidate (git bytes; no deploy needed):
   `python scripts\release_archive.py build-release --commit <V1> --out <F:>\arch_v1` then `check` it.
3b. Producer leg (B3/D1): `git -C <F:>\scratchpad\prodwt checkout --detach <V1>` then
   `python v1\producer_probe.py <F:>\scratchpad\prodwt` -- a planted row must be refused AND leave the pool.
4. Mechanical checks on the candidate: served numbers vs PREV (P4 detail) cross-checked with
   `served_numbers_diff.py <PREV> <V1>`; notice signatures listed; nothing signed by this lane, ever.

## T1 = deploy (by 15:00): production record for <V1>
5. Wait for `production record <V1[:12]>: ATTESTED (n/n ...)` on origin/production-records.
6. Wait 11 min after the record (CDN max-age 600 s), then the ACCEPTANCE run on SERVED bytes:
   `python v1\v1_accept.py --release <V1> --prev <PREV> --work <F:>\v1served --source served`
   P1 mismatches are retried once after max-age; any that remain are named.
7. Independent re-run of the four-file command on all 32 live pages (prove_recert4.sh logic) as a second instrument.
8. Rebuild the archive with the served scorecard + production record:
   `build-release --commit <V1> --acceptance <F:>\v1served\scorecard.json --out docs\releases` on a branch from <V1>;
   commit `docs/releases/v1/<V1[:12]>/`, CI green on the exact sha, fast-forward to main, prove the zip live by fetch
   (sha256 == SHA256SUMS) and replay it from a fresh directory.
9. Finalise the release-note section from the served scorecard: fill every "V1:" line or delete it; no line without a
   served-bytes result. Deliver to the main lane (commit on this lane's branch; path in REPORT).

## If time runs out
The archive and scorecard are built from git bytes at T0, so a late deploy leaves only steps 5-9, about 25 minutes of
wall clock (11 of them waiting on the CDN). If the deploy lands after 15:00, report the served audit as NOT RUN rather
than extrapolating from the rehearsal.
