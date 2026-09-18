# RESUME_STATE — meta-harness glp1 programme (refreshed 2026-09-18 03:40 local; refresh on every landing or lane finish)

Every claim is marked MEASURED (read from git/ls-remote/disk at the time stamp), INFERRED, or CLAIMED. A restarting session should trust `git ls-remote https://github.com/mahmood726-cyber/meta-harness.git <ref>` over anything here.

## 00. How to read the SERVED state (the only verification path; two observers got this wrong on 17 Sep)
- `curl -s https://mahmood726-cyber.github.io/meta-harness/_production/manifest.json` → `commit_sha` (which commit built the site — a CONTAINER property).
- `curl -s https://mahmood726-cyber.github.io/meta-harness/reviews/<slug>/manifest.json` → `review_sha256` (the review OBJECT), `html_sha256` (the page bytes), `protocol_sha` (the registration). A landing that claims to change a review must move `review_sha256`; the manifest `commit_sha` alone proves nothing about the reader's page.
- Fetch with a non-caching client (`curl`, a browser with cache disabled). Tool fetchers that deduplicate (some cache for an hour) return old bytes as if fresh — a constant byte length across repeated fetches is the tell.
- NEVER read `C:\meta-harness\docs` as the corpus: that clone sits on `search-v2-engine` at aa8ed28a (16 Sep) and is only the object store lane clones are cut from. Read `F:\claude-temp\mh-clean` after `git fetch origin main && git checkout --detach origin/main`, or a fresh clone of main.
- Compare served bytes to the clone: `sha256sum docs/reviews/<slug>/index.html` in the clean clone vs `curl … | sha256sum`.

## 0. Layout — NOT linked worktrees (MEASURED)
`C:\meta-harness` (branch `search-v2-engine`, HEAD aa8ed28a, its `refs/remotes/origin/main` is STALE) is only the shared object store lane clones are made from (`git clone -s`); nobody edits it. The active clones (each a separate `.git`, all with `origin` = the GitHub URL — check `git remote -v`, four clones today had `origin` = a local path):
- `C:\mh-int` — INTEGRATION clone, branch `fix/phase1-integration`, hooksPath `.githooks` (the pre-commit hook = `scripts/verify_all.py`, 40–75 min). HEAD 3f8add72 = origin/main. Landings are committed here, pushed, CI-by-SHA, then `<sha>:main`.
- `C:\mh-base` — HANDOVER clone, branch `handover-2026-09-16` (875ac4ef pushed). Holds `outputs/handover/*` (briefs, lane reports, adjudications, held FDA PDFs, sealed Gemini run, review pack, proof board `outputs/handover/lanes/GLP1_PROOF.md`), and THIS file.
- `C:\mh-wip` — scratch clone for composing WIP lane bases (detached; HEAD 3cf73885).
- `F:\claude-temp\mh-clean` — clean clone of origin/main used for landing proofs (served bytes vs clone bytes).
- `C:\mh-r-<LANE>` — one clone per Codex lane, made by `sh C:/mh-int/scripts/codex_lane.sh <LANE> <base_sha> <brief.md> "outputs/handover"` (uses `< /dev/null`; sparse; ~450 MB each). Lanes never commit; their working trees are harvested by FILE COPY (their diffs proved unreliable).
- Lane manager: `F:\claude-temp\claude\C--meta-harness\ba56f4ae-2153-4cbd-9f73-1dab4f1d2c65\scratchpad\wave5.sh` (`sh wave5.sh "<running lanes>"`, queue in `wave5.queue`, events in `wave5.log`, hang = no log growth across two 5-min checks → taskkill by the lane's own `lane.winpid`).

## 1. Refs on GitHub (MEASURED by URL ls-remote 20:31)
| ref | sha | meaning |
|---|---|---|
| main | 3f8add72 | H = harms synthesis suppressed while incomplete (ledgers kept) + adjustment labels UNRESOLVED + landing hash check, on top of E/F/G; served 03:36 (manifest 3f8add72; glp1 review_sha256 edaf5f6b, html_sha256 efbc3c28 = clean clone; protocol_sha b10c53d3) |
| fix/phase1-integration | 3f8add72 | integration branch |
| handover-2026-09-16 | 875ac4ef | all handover artefacts |
| refs/lanes/landing3-wip | f6f7b14c | pre-landing-3 merged tree (hook-refused) |
| refs/lanes/landing3-wip-in2 | f5f81800 | + IN2 |
| refs/lanes/landing3-wip-cgx | dcde90b1 | + CGX |
| refs/lanes/landing3-wip-cgx-ty | e3b70bfa | + TY |
| refs/lanes/landing4-wip | c57e8727 | + GL + CGX2 |
| refs/lanes/landing4-wip-ty2 | cf270cd9 | + TY2 |
| refs/lanes/landing4-wip-typg | 443d8a64 | + TYPG + parity correction |
| refs/lanes/landing4-wip-str | bf99a916 | + STR (glp1 builds: k=7 0.8884) |
| refs/lanes/landing4-wip-pm | 2f8705a8 | + PM (CGX3A/B/C merged) |
| refs/lanes/landing4-candidate | 60c5cd67 | IN4 attempt 3 on top of main; standard 7/11 refused |
Local-only SHAs at 20:31: NONE that matter (every WIP base above is on GitHub). Superseded local refs (250926f8, 8c168beb) are dead by construction and unpushed on purpose.

## 2. Protocol registration (MEASURED)
`protocols/glp1-ra-mace-t2d.md` B-prime amendment, labelled RETROSPECTIVE, registered at commit `b10c53d3` (the commit that changed the file); reproducible page at `4ee33453` (commit B); both on main. A further dated clarification (17 Sep, executable binding axes: endpoint components / HR / end-of-study censoring) exists on the landing-4 candidate only.

## 3. The nine items (state 20:35)
| # | item | state | where |
|---|---|---|---|
| 1 | trial-family node | DONE as machinery (FN 327,201 tok; FNC compaction 232,838: 178.6 MB→14.7 MB, 67,785 rows hash-verified) — NOT SERVED | landing4-candidate |
| 2 | claim graph over the whole page | BUILT (CGX; CGX2/3A/3B/3C/4; PM merge): glp1 848 of 2,749 units registered on the merged renderer — NOT SERVED | landing4-candidate |
| 3 | estimand/compat type system | BUILT (TY; TY2 binding from protocol; TYPG glp1 axes; TYP1–3 corpus provenance) — NOT SERVED | landing4-candidate |
| 4 | FACT objects with proof; plant fired PRE-fix | BUILT; plant fired pre-fix (verbatim in LANE-CGX-REPORT.md); FACT 7 of 135 rows corpus-wide on the candidate (legacy rows lack a UTC retrieval instant — DECISION for Mahmood) | landing4-candidate |
| 5 | source ladder (OUTCOME_NOT_IN_SOURCE not terminal) | PARTIAL: harms items climbed (153/153 resolved, on main); ELIXA 3-point recovered from the held FDA StatR (level 2) on the candidate; FLOW/AMPLITUDE-O/Harmony refused on typed axes (censoring/components not in held text) | main (harms) / candidate (ELIXA) |
| 6 | dark-evidence ledger | BUILT in FN (714 cells, 14 known) — NOT SERVED | landing4-candidate |
| 7 | robustness envelope / fragility / decomposer | BUILT (GS 193,839) — computes on the candidate; NOT SERVED | landing4-candidate |
| 8 | evidence certificate (release hash bundle) | DONE AND SERVED (commit F/G on main): CERTIFICATE.json per page, release_sha256 recomputed by reproduce and refused on mismatch; plants pre-fix | main 405cb80b |
| 9 | every defect → regression test proven pre-fix | DONE for: FACT plant, HM plants, FIX1's nine audit findings, STR, TY2, TYPG; weak (module-absent) for TY/GS/FN(partial) | candidate |
Served-page corrections (GRADE provisional; RoB NOT ASSESSED + low-only re-pool suppressed; heterogeneity STALE): FIX2 DONE (200,126 tok; plants fired pre-fix; 10/11 on its tree), integrated into C:\mh-int with 125 ratchet acks signed; commit E `0f98038c` ON MAIN AND SERVED (CI 35278779923 success; served manifest 0f98038c; measured on fetched bytes: 'moderate' 0, 'GRADE provisional' 6, low-only row 0, 'RoB-restricted re-pool suppressed' 2, STALE marks 12; review_sha256 63f1acef). This lands FIRST, as its own commit; acceptance = glp1 review_sha256 ≠ ab6707c202c8ab5c and the three defects gone on FETCHED bytes.

## 4. Lanes (tokens from each lane's `lane.log` tail; artefact = `C:\mh-r-<LANE>\LANE-<LANE>-REPORT.md`; MEASURED)
IN 1,844,025 (18:37→00:17) · ST 546,003 · HM1 287,557 · HM2 261,333 · HM3 243,729 · CGX 159,012 · TY 142,503 · IN2 361,450 · GL 568,507 (09:57→11:00) · FN 327,201 · TYP1 198,920 · CGX2 170,723 · TY2 158,240 · TYP2 320,986 · TYP3 192,807 · IN3 326,123 (bad-base attempt 163,365 discarded) · TYPG 163,054 · GS 193,839 · CGX3A 182,766 · CGX3B 242,627 · CGX3C 252,346 · STR 213,980 · FNC 232,838 · PM 399,662 · CGX4 246,482 · AUD 160,867 (hostile audit: 9 confirmed) · FIX1 327,539 · IN5 182,865 · IN4 a1 80,159 / a2 168,647 (my over-strict rules) / a3 517,683 (18:39→20:22). Total ≈ 9.84 M.
IN FLIGHT: **IN6** (`C:\mh-r-IN6`, base 60c5cd67, brief `outputs/handover/lanes/LANE-IN6.md`) — landing-4 candidate: every integration-caused refusal, leaving the retrieved_utc decision untouched. FIX2 and CERT finished (harvested; clones kept until served). Retry clones IN4.attempt1/2, CGX3B.badbase, CGX3A.old/.badbase, IN3.badbase, TY2.badbase reaped 21:10 (their two never-pushed SHAs preserved as refs/lanes/superseded/*).
Relaunch (from any shell, after removing/renaming the old clone): `sh C:/mh-int/scripts/codex_lane.sh IN6 60c5cd67074beff328a745952ab31a17c0195ba7 <scratchpad>/lanes/LANE-IN6.launch.md "outputs/handover"` and `sh C:/mh-int/scripts/codex_lane.sh FIX2 3cf73885ffc83f6fcc4db273c6510a5416cdcde0 <scratchpad>/lanes/LANE-FIX2.launch.md "outputs/handover"` — the launcher runs `codex exec … < /dev/null`.
Harvest a finished lane: `cd C:\mh-r-<L>; git status --short --untracked-files=all` → copy each listed file into the target clone; verify by FILE COUNT and named key files; never trust `git apply` "0 conflicts".

## 5. Decided-but-unapplied / owed
- ADJUDICATIONS.json (`outputs/handover/glp1_reviewerB/`): ELIXA ELIGIBLE, PRIMARY_POOL blocked pending exact 3P HR (the FDA StatR row IS the exact 3P: HR 1.02 (0.887–1.172) — the candidate pools it); FLOW include conditional on censoring span (NOT met in held text → refused); FREEDOM-CVO any-delivery only, end-of-study row, conditional on censoring/analysis-set typing (met from the FDA text → pooled on the candidate). **Mahmood's countersignature owed on the adjudication objects.** Dispatch relayed his signatures on the five numbered decisions 17 Sep; encoded as conditions on the candidate.
- DECISION for Mahmood: FACT contract requires a UTC retrieval *instant*; legacy records carry a *date* → 25 pages' rows UNVERIFIED_FACT under the candidate. Recommended: typed `retrieved_utc_precision: date`, disclosed. Not decided by me.
- HELD for Mahmood: corpus-wide fail-closed typing (85 of 112 rows lack a stated analysis set/censoring).
- pcsk9 acknowledgements signed by Mahmood (16 Sep) — applied.

## 6. Hazards a restart would rediscover (all MEASURED today)
- `refs/remotes/origin/main` inside any clone can be stale (C:\meta-harness read aa8ed28a while main was 4ee33453). Prove with `git ls-remote https://github.com/mahmood726-cyber/meta-harness.git <ref>` BY URL; a clone's `origin` may be a local path (four were).
- A backgrounded `codex exec` without `< /dev/null` hangs on stdin and looks alive. Judge lanes by log growth + `tokens used` in the log TAIL (patch contents also contain that phrase) + the report file.
- The local hook is NOT the standard when the machine holds off-tree data: CI has no `F:\AACT-storage`. Simulate: `mkdir /tmp/empty_aact; AACT_DIR=/tmp/empty_aact python scripts/reproduce_review.py` (the dir must EXIST or the env var silently falls back).
- Protocol-anchor class: a commit touching `protocols/<slug>.md` cannot reproduce its own page → two commits (A amend+rebuild passes the hook; CI refuses A; B rebuilds → main). Lane-amended protocols hit this too (8 pages in landing 3).
- Regeneration must not erase retractions: run `scripts/retraction_survival.py <base>` (on main since 3cf73885) BEFORE every hook — 32 of 32 required; ARNI = `sacubitril-valsartan-hfref` (its comparator is an HFrEF network meta-analysis, a stated scope mismatch); there is no NMA page in this corpus.
- Never two lanes on one worktree; never kill by pattern (taskkill by `lane.winpid`).
- `git apply --3way` "0 conflicts" is NOT success — verify by file count; transplant working trees by copy.
- A landing that claims to change a review must show the review_sha256 changed (manifest commit_sha is a container property).
- Disk (MEASURED 21:10): C: 24 GB free; ~450 MB per lane clone; reap `*.badbase`/`*.attempt*`/`*.old` clones after checking their SHAs by URL.

## 7. Timing (MEASURED durations; INFERRED estimate)
MEASURED: lanes take 45–105 min wall-clock (GL 63 min; FIX1 62; IN4 a3 103; HM lanes ~50; IN 5 h 40 was the 19-lane integration). A hook run = 40–75 min; CI = 8–15 min; Pages deploy = 12 min; one landing ≈ 1.5–2 h from commit to served bytes.
INFERRED: (a) served-page corrections (FIX2 → my integration + ratchet acks → hook → CI → deploy): ~3 h from 20:30 → ~23:30 tonight if the hook passes first time. (b) Reviewable glp1 URL (candidate landed: all 11 limbs, FACT provenance on the page, strands, prose objects) — NOT tonight: blocked on the retrieved_utc contract decision + IN6's remaining refusals + ratchet signatures; realistic 18 Sep afternoon if the decision comes in the morning. Long pole: item 2/4 prose+FACT migration corpus-wide (the gate is live on every page).

## 8. 23:15 additions
- CMP (331,954 tok, `C:\mh-r-CMP`, 282 files): comparator panels + live overlap + 'independent corroboration' gate; PASS on its tree; to integrate onto E with CERT.
- HRM (301,473 tok): item 10/12 shape right but re-labelled typed refusals as unresolved (27 pages refused) — NOT integrated; HRM2 running on 3cf73885 to redo without the semantic change.
- IN6 still running on the landing-4 candidate (log 70+ MB).
- Next landing (F): CERT + CMP (+ HRM2 when green) onto 0f98038c via transplant, retraction proof, ratchet acks, hook, chain.

## 9. 00:02 additions
- Commit F (CERT + CMP onto E; gate scorecard registry merged by gate_id; ratchet 9 acks) IN THE HOOK since 00:00 (`scratchpad/commit13.log`, chain `land10.sh`). Attempt 1 refused on the scorecard registry (CMP's copy lacked E's and CERT's entries) — fixed at source.
- HRM2 DONE (114,420 tok; `C:\mh-r-HRM2`, 204 files): harms synthesis suppressed 46 of 61 with ledgers kept, adjustment labels UNRESOLVED 95/95, gate 32/32 incl. check_harms_complete → commit G after F.
- IN6 still running on the landing-4 candidate (log 114 MB, report being written).
- C: free 24 GB.

## 10. 01:16 additions
- Commit F `432294db` (CERT + CMP) hook 11/11 (attempt 3; attempts 1–2: scorecard registry merge, re-rendered index banner ack); pushed (ls-remote branch 432294db); CI 35289342303 REFUSED on one import: CERT's Playwright test lacked the visible skip. Commit G (skip + ephemeral port) IN THE HOOK since 01:14 (`commit14.log`, chain `land11.sh`) → main.
- IN6 attempt 1 (`C:\mh-r-IN6`, report 586 KB): landing-4 candidate post-fix standard 4 of 11 refused — unit (2 tests: CGX3B owned-section units after the merge; glp1 UI test expects 0 UNVERIFIED_FACT, 4 remain = date-stamped harm rows), gate (retrieved_utc decision), search completeness (search_v2 engine hash changed → `scripts/search_v2_run.py` must be re-run with network by the integrator), ratchet. My hang detector killed it at the end of an essentially finished run (10-min window < a silent verify_all); relaunch killed; window widened to 30 min.
- HRM3 running on 432294db (merge HRM2 onto F).

## 11. 02:10 — state at the end of the autonomous run
- MAIN = 405cb80b, served and byte-proved 32/32. On the served glp1 page (fetched): certificate block (release_sha256 1603ceef…, protocol_sha b10c53d3), comparator panel with live Jaccard overlap and no 'independent corroboration' phrase, GRADE provisional, RoB NOT ASSESSED + low-only re-pool suppressed, heterogeneity STALE; primary still the legacy k=8 pool (0.856); FDA values not on the page.
- HRM3 running (`C:\mh-r-HRM3`, base 432294db): merge HRM2 (harms synthesis suppression + adjustment labels) onto F → commit H in the morning.
- Landing 4 (glp1 strands k=7/k=8 with FACT provenance, families, typed axes, prose objects, envelope): candidate 60c5cd67 + IN6 attempt-1 tree (`C:\mh-r-IN6`, 4 of 11 refused). BLOCKED on: (1) Mahmood's decision on date-precision retrieval stamps vs re-retrieval (FACT contract); (2) integrator re-run of `scripts/search_v2_run.py` with network (engine hash changed); (3) two unit tests; (4) ratchet acks. Then IN7 on top of main.
- Never do again: hang-kill a lane inside a silent verify_all (window now 30 min); judge patch application by conflicts (file count + working-tree transplant); copy a lane's registry/scorecard over another's (merge by gate_id).

## 12. 02:30 — served state re-verified by the outside observer through a browser (review_sha256 d67a3615, html_sha256 28d5b5bc, protocol b10c53d3; the three corrections present). Two observer errors recorded as defect classes: a deduplicating fetch tool read as the origin; the stale `C:\meta-harness` tree grepped as the corpus. Still owed: the review-hash-changed landing gate (goes in with HRM3's commit H).

## 13. 02:26 — commit H IN THE HOOK (`commit15.log`, chain `land12.sh` which now runs `scripts/landing_hash_check.py <prev> <new>` before pushing main and refuses if a touched review's review_sha256/html_sha256 did not move): HRM2 merged by HRM3 (199,905 tok) — harms synthesis suppressed 46/61 with ledgers, adjustment labels UNRESOLVED 95/95; 51 ratchet acks signed (the one 'retraction'-marker decrease is two duplicate renderings of a protocol sentence containing 'withdrawn' — measured; retraction_survival 32/32). Codex idle after H; remaining work is landing 4 (blocked on the retrieved_utc decision + search re-run) and the independent search.

## 14. 03:40 — commit H `3f8add72` ON MAIN AND SERVED (CI 35298586402; landing hash check printed glp1 review_sha256 d67a3615 → edaf5f6b MOVED before the main push; served manifest 3f8add72; page bytes = clean clone). Fetched glp1: 'HARMS EXTRACTION INCOMPLETE — no class-level quantitative safety conclusion issued' ×2 with the ledger, adjustment_status UNRESOLVED ×10 (the one remaining 'PUBLISHED_UNADJUSTED' string is the sweep's own explanatory label), GRADE provisional ×6, certificate, comparator panel. No lanes running. Next: landing 4 (needs Mahmood's retrieved_utc decision + integrator's network re-run of scripts/search_v2_run.py), then the independent concept search.
