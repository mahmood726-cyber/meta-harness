# V1 notice runbook (lane NR): from the freeze (Sat 09:00) to Mahmood's verified signatures (before 15:00)

The re-derivation tools are on `nr/notice-anchors`: `scripts/rederive_notices.py`, `v1_notice_registry.py`,
`v1_sign_branch.py`, `notice_rejudge.py`, `notice_signing_list.py`, `v1_final_list.py` and
`verify_notice_signatures.py`.

The whole pipeline was rehearsed on 25 Sep on a synthetic candidate (see `v1-rehearsal/`). In that candidate N28
changed from 0.85 to 0.84.
- The re-derivation found 41 changes, all noticed, with N28 marked CHANGED.
- The registry kept 40 rows unchanged and replaced N28 with V1-01.
- The sign branch reported 2 diverged tool files.
- Packets: 41 of 41 passed the mechanical checks. B3 was appended.
- The walker presented V1-01, and the signing list built all 41.
- All 41 commands were replayed into a temporary ledger, and the verifier reported 41 VALID.
- The old N28 command (the B2 hash) was **refused**. The repository ledger stayed unchanged.
- The re-derivation's controls and plants: the real pair gives 41, 0, 0; a dropped notice gives UNNOTICED and exit
  1; a fake notice gives ORPHAN.

**Disk rule, learned the hard way on 25 Sep.** Every worktree is created `--no-checkout`, its sparse patterns are
written first, and only then is it checked out with `MSYS_NO_PATHCONV=1`. A plain `git worktree add` checked out
1.8 GB and took C: down to 103 MB for about a minute.

## T0: the candidate is announced
1. `git fetch origin`. Record `<CAND>` as the main lane announces it. Record `<PREV>` as the commit of the newest
   `production record ...: ATTESTED` (it is what readers are served; pva's `--prev auto` finds the same).
2. **Is the fix in?**
   - `git show <CAND>:harness/trial_family.py | grep -c "def population_matches\|comparators=()"` must give 2
     (the P5 matching fix and the arm-contrast fix, `p5-fix/trial_family.patch`).
   - `git merge-base --is-ancestor origin/oc/V1-READY-p10-p11 <CAND>` is recorded as well (oc's P10/P11
     contrast work), and reported, not assumed.
   - If the P5 fix is absent, say so at once: the 11 "vanish" notices are then still in the candidate, and are
     listed to hold, never to sign.
3. **Re-derive** in `C:\mh-lanes\nr\wt`:
   `python scripts/rederive_notices.py --prev <PREV> --cand <CAND> --out C:\mh-lanes\nr\v1\rd`
   - Exit 1 means UNNOTICED, AMBIGUOUS or ORPHAN. That is a V1 blocker, and goes to the main lane with the named
     outcomes. Stop there: nothing is signable until the candidate's ledger covers every served-number change.
4. **Registry:** `python scripts/v1_notice_registry.py --rederived C:\mh-lanes\nr\v1\rd\rederived.json --out C:\mh-lanes\nr\v1\registry.json`
5. **Sign branch** (plumbing, no checkout):
   `python scripts/v1_sign_branch.py --cand <CAND> --registry C:\mh-lanes\nr\v1\registry.json --branch nr/v1-sign-<c12>`
   - Read every `DIVERGED` line. If the candidate's `countersign_result_change.py` or `sign_walk.py` carries a
     change from main that ours lacks, merge it by hand before going on. On 25 Sep the only divergence was the
     gate's pre-B copies.
6. **Sparse worktree at the sign branch**, created as the disk rule above says. Then:
   `python scripts/rederive_notices.py --prev <PREV> --out ..\v1\rd2`
   - This recomputes the digests with the candidate's own renderer; it must exit 0.
   - Then: `python scripts/notice_rejudge.py packets --served <PREV> --proposed <CAND> --out ..\v1\packets`
7. **Judgement B3.**
   - **Bulk comparison: Claude subagents.** Codex is out until 26 Sep 18:09, after go-live. Use at most 2 or 3 in
     parallel, each given packets only, blind.
   - **The lane's hostile read.** Every CHANGED or new V1-NN notice, and every notice with a wording defect, is
     read in full. Carried notices inherit B2's findings.
   - Build the verdicts file bound to the pinned anchors; `make_verdicts.py` shows the shape. Then run
     `notice_rejudge.py append --served <PREV> --proposed <CAND> --verdicts ... --judgement-prefix B3 --judged-by "..."`
     and commit.
8. **Push** `nr/v1-sign-<c12>` and verify it from fetched bytes. Run `notice_signing_list.py`, then
   `v1_final_list.py --decisions <hold/ruling JSON> --branch nr/v1-sign-<c12>`.
   - **Replay every command into a temporary ledger** (`v1-rehearsal/rehearsal_signloop.py` shows how). Nothing is
     published before this reports ALL VALID.
9. **Deliver** the list to Mahmood, and to the main lane as a PR or pointer. The list is phone-readable, gives the
   clone `C:\mh-sign-v1` and the branch `sign/mahmood-v1`, and ends with the push command.

## After he pushes
10. `python scripts/verify_notice_signatures.py --ref origin/sign/mahmood-v1 --base origin/nr/v1-sign-<c12>`
    - Report the counts `VALID / STALE / REFUSED / MISSING` and any file changed besides the ledger.
    - Hand **only the VALID set** to the main lane. The main lane merges `docs/result_changes.json` from his branch
      into the candidate and rebuilds, so each page renders its signature line; the anchor guard tolerates that
      churn. Then pva's acceptance probe E must show 0 unsigned.
11. If anything is STALE (signed against a superseded hash), say so plainly. It is redone against the current
    notice and never re-pointed.
