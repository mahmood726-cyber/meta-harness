# Decisions of 2026-09-25: candidate release, archive-and-revert, reciprocal reversal

Recorded by the F4 lane. **Relayed by Dispatch under Mahmood's delegation, 25 September 2026.** These are
engineering decisions taken under that delegation; the 41 result-change signatures remain Mahmood's and
are not covered by it.

## 1. Regeneration — AUTHORISED, as a CANDIDATE

Integrate the repairs, cut a **new release identity**, regenerate **all 32 topics** on a branch or
staging target, and run every probe plus the §F.6 suite against those **candidate bytes**. Then compute a
**derived diff of every served number and verdict** against the current live release.

    if NO served number changes  -> deploy, then re-run the probes on the SERVED bytes (§B.5)
    if ANY served number changes -> deploy NOTHING; send the per-topic before -> after list with
                                    notices and hashes, for Mahmood to sign

Coordinate integration with `oc`, `evid2` and `rai`. **Do not wait for `oc`**: repairs that are ready go
in candidate 1, `oc`'s follow in candidate 2.

## 2. `F:\mh-gate`'s half-finished 260-file rebuild — ARCHIVE then REVERT

Copy the tree to an archive location, **verify sha256 at the destination**, record what it contained and
why it was abandoned, then revert so `verify_all` is unblocked. **Nothing is deleted that has not been
archived and verified.**

## 3. Declared reciprocal reversal — PERMITTED

A reversed contrast may publish **only** when the reversal is explicitly declared, the estimate and CI
are transformed (HR -> 1/HR, CI -> [1/hi, 1/lo]), the arm roles are swapped consistently, and the page
discloses it. **A silent reversal stays refused.** This **supersedes lane F4D's reject-by-policy
choice**, and `oc` has been told.

## 4. Codex trust entries — SKIPPED

Codex is exhausted until the reset; no new codex jobs. All remaining work is done in Claude.

---

## What the archive contained, and why it was abandoned

The tree carried **262 dirty entries, 154.5 MB**, of two quite different kinds, which is why the revert
was surgical rather than a blanket `git checkout`:

- **The abandoned rebuild** — 237 tracked files modified 2026-09-24 **09:03–11:32**: 193 served review
  pages under `docs/reviews`, 26 under `docs/m`, 5 in the served harness mirror `docs/harness`,
  `scripts/build_bundle.py`, `scripts/verify_bundle.py` and four test files; plus 4 untracked files
  (`docs/harness/follow_up.py`, `harness/follow_up.py`, `tests/fixtures/rx3_zero_spans.json`,
  `tests/test_rx3_zero.py`). It is a **partial regeneration**: the honest-state ratchet reported *lost
  absent blocks* on `docs/reviews/pcsk9-mace/index.html`, which is what a half-finished page rebuild
  looks like from the outside.
- **This session's evidence** — 19 untracked records in
  `docs/evidence/enforcement-gate-2026-09-21/` (files 20–36 and the two schema versions), plus **my own
  edits** to `18-release-acceptance-checklist.md` (17:47) and `README.md` (13:47). These were set aside
  before the revert and restored after it.

Why it blocked everything: `verify_all` evaluates the **whole tree**, not the staged set, so any commit
from that tree refused — 4 of 11 limbs (unit tests, publication gate on every live review page, index
currency, honest-state ratchet). That is the gate behaving correctly on an inconsistent tree, and it is
the reason a docs-only evidence commit could not land for most of a day.

Archive: `C:\mh-archive\mh-gate-abandoned-rebuild-2026-09-24\` with `files/`, `MANIFEST.sha256`,
`git-status.txt` and `verify.txt`. The revert proceeds only if every archived file verifies at the
destination.
