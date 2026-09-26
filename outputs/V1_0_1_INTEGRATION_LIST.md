# V1.0.1 integration list — oc + POOL + FLOW/ELIXA k=10, as one scripted rerun

V1.0 ships **frozen main + P5 + D3**. Three repair sets are built and tested on branches but are not
in it. This is the ordered list for landing them as a rerun, with the reason each was deferred and
the specific thing that must be fixed first — so V1.0.1 is not a rediscovery exercise.

**Order matters.** oc's `verify_bundle.py` / `build_bundle.py` changes alter generated output, and the
k=10 admission changes the pool. Land code first, then the admission, then regenerate once.

---

## 1. oc — ordered contrast and estimator value checks (`oc/ordered-contrast`, 23642e0d)

**What it is:** the verifier recomputes which arm is the numerator from the tuple's own clause, the
pool refuses mixed or unidentified measures before any log, and a reversal passes only as a declared
reciprocal. 9 files, 1886 insertions, CI-green on its own branch.

**Why it is not in V1.0:** on the V1.0 tree, 8 of its plant tests fail — **and the verifier is not at
fault**. The failing assertion is the test's own positive control:

    assert base_then["verdict"] == "PASS", ("the pre-fix baseline itself must pass", ...)

`_prefix_state()` reconstructs the pre-oc served state from a pinned commit
(`PREFIX_BASE = c9d665e0`, main when oc branched) by restoring an **enumerated list** of six files.
That list is incomplete, and incomplete in kind rather than by accident:

    restore 6 files only          -> ARTEFACT_DIGEST_MISMATCH harness/compat_check.py, harness/screen.py
                                     (the old BUNDLE declares digests for the served harness MIRROR,
                                      which was left at the current revision)
    + restore the whole mirror    -> CERTIFICATE_MISMATCH file_sha256_matches_bundle
                                     EXECUTION_RECORD_MISMATCH release_ok=False
                                     (CERTIFICATE.json was not in the list either)
    + restore the whole review
      directory and the mirror    -> ARTEFACT_DIGEST_MISMATCH returns under a different assertion

Three fixes, three new problems: that is a wrong-architecture signal, so file-chasing stopped.
Confirmed the underlying divergence is real, not imagined:

    docs/harness/compat_check.py   at PREFIX_BASE 5b4458feebb5   at V1.0 dd3ce03369fe   DIFFER
    docs/harness/screen.py         at PREFIX_BASE 551b1cb27b2c   at V1.0 4f36292d5b47   DIFFER

It passed on oc's branch only because those mirror bytes happened to match the pinned commit. Frozen
main changed both modules, so the baseline stopped being self-consistent.

**What must be fixed before landing:** the pre-fix baseline must be reconstructed as a *whole tree
state*, not a file list. Two viable designs, both for oc to choose:

- build the baseline in a **worktree at `PREFIX_BASE`** (`git worktree add <tmp> PREFIX_BASE`) and run
  the old verifier there, so the state is consistent by construction and no enumeration exists to
  fall out of date; or
- **re-pin `PREFIX_BASE`** to the commit the V1.0 release actually descends from, and add a test that
  fails loudly when the pinned commit is no longer an ancestor of `HEAD` — so the next drift is
  reported as a stale pin rather than as eight plant failures.

The second is cheaper; the first cannot rot. Either way the fixture should assert its own
completeness rather than rely on a list.

## 2. POOL — five verdicts, selected set, pooled-input linkage

**What it is:** the five independent verdicts
(`artifact_integrity | state_reproduction | input_linkage | scientific_admission |
publication_eligibility`), the named selected set with its declared multiplicity rule, and
`check_pool_contract` / `POOL_CONTRAST_MISMATCH`.

**Why it is not in V1.0:** it and oc touch **disjoint features of the same file**:

    oc's verify_bundle : pool_measure_guard (4 occurrences), no verdicts
    POOL's verify_bundle: verdicts (27), check_pool_contract, POOL_CONTRAST_MISMATCH

    git apply --check        -> patch failed at scripts/verify_bundle.py:1728
    git apply --3way --check -> "Applied patch with conflicts"  (leaves conflict markers)

A 3-way that lands conflict markers is hand-guessing inside the admission file, which was ruled out.

**Parked at** `C:/mh-artefacts/parked-tests-2026-09-26/` — `test_pool_binding.py`,
`test_f6_harness.py`, `test_freedom2.py` — and the full diff is in
`C:/mh-artefacts/candidate-2026-09-25/code.patch`.

**What must be fixed before landing:** POOL must be rebased onto oc's `verify_bundle.py` **by
whoever owns the merge semantics**, not reconstructed from a patch against an older base. Note
`test_freedom2.py` could not even collect on V1.0 (`ModuleNotFoundError: contrast_order`) — that
module arrives with oc, so POOL's tests are only meaningful **after** step 1. Hence this order.

## 3. FLOW + ELIXA — the k=10 primary

**What it is:** two trials adjudicated protocol-eligible with source-bound 3-point MACE results,
moving the primary pool from k=8 to k=10.

    V1.0 serves     k=8   HR 0.856  (0.8086-0.9061)  PI 0.8069-0.9081  tau^2 4e-05
    V1.0.1 adopts   k=10  HR 0.8613 (0.8069-0.9194)  PI 0.7531-0.9852  tau^2 0.0027

**Why it is not in V1.0:** no branch changes anything the build reads
(`topics/`, `registry/`, `harness/` are untouched on every evid branch), so **nothing admits them** —
and the signature request says so in terms: *"NOT LANDED … unsigned: this request lands nothing."*
Mahmood approved the intent ("ten trials please with old k on same page", Dispatch chat relay); that
is not the hash-bound signature. Publishing a served-number change on approval-of-intent would defeat
the binding.

**What must exist before landing:**

1. the **admission mechanism** (evid lane) — something the build reads, not a decision document;
2. a **"pending result change" → adopted** transition on the page. `scripts/refresh_result_change_notices.py`
   will not generate this on its own: it notices outcomes whose served result *has* moved, and k=10
   deliberately has not. Either extend it or use a `reason_locked` hand-written notice, and say on the
   page which it is;
3. the signature **regenerated against the V1.0 SHA**. The bundle binds
   `docs/reviews/glp1-ra-mace-t2d/review.json` by content hash and has already moved three times
   (`3809ce76` → `170c6922` → `4bf8ec33`), each time because a main landing changed the reproduction
   block. A hash bound to bytes we do not serve is the exact failure this mechanism exists to catch.

Step-by-step execution, with the artefact that proves each step:
**`outputs/V1_0_1_RERUN_RUNBOOK.md`**.

---

## Wording for the V1.0 page

> The direction/ratio-type value checks and the pooled-input linkage repairs are built and tested on
> branches but are not in this release. The FLOW and ELIXA trials are adjudicated eligible and their
> inclusion (k=10) is pending signature, shown here as pending, not adopted. See V1.0.1.

## Also carried to V1.0.1 or later

    tag stripping `<[^>]+>`          84 of 892 held text fields damaged; 0 of 433 declared-absent
                                     entries affected, so no wrong served number. Fix:
                                     `<!--.*?-->|<\?.*?\?>|<![A-Za-z\[][^<>]*>|</?[A-Za-z][A-Za-z0-9:_-]*(?:\s[^<>]*)?/?>`
    gitblob per-file fallback        938 `git hash-object` spawns where `--stdin-paths` (which works
                                     outside a repository) would use 2.
    ordered-contrast prose equality  a guard compares a long sentence by exact match, so it cannot
                                     tell a wrong direction from a reworded one. Compare a typed
                                     direction token.
    verify_all buffered stdout       a killed hook leaves no trace; rai found this independently.
    evid2 Q1/Q3 notices              if they did not make the V1.0 cut.
