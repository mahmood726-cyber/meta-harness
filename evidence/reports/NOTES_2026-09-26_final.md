## Final notes, Saturday 2026-09-26 (evidence lane, stopping at 15:00)

**Main has been frozen since about 08:35.** One lane commit reached main after the freeze: at 09:01:49 +0100 a push moved origin/main to `6260e70c`, the 5-line archive note `evidence/ARCHIVE_2026-09-25.md`. It touches no served number and no bound file.
- **Correction:** I said earlier that nothing landed after the freeze. That was wrong. I had relied on having stopped the land loop, not on reading origin/main's reflog. Found at the 10:00 heartbeat.
- **Not reverted:** a revert would be a second push to main. The release captain decides.
- **Since then:** no push to main by this lane.

**GLP-1 adjudication (FLOW, ELIXA, FREEDOM-CVO).**
- The six files are on origin/main.
- The bound files are unchanged since `1494159a`, so the signature bundle `4bf8ec33` stands.
- Checked at every heartbeat 10:00–14:50:
  - stale_check: 107/107, STALE 0.
  - BEFORE still reproduces the served k=8 result, 0.856 (0.8086–0.9061).
  - verify_records was not re-run, because the cache is sparse-excluded to save C: disk. Its inputs (`cache/`, `verify_records.py`) are byte-unchanged since `1494159a`, where it passed.

**Admission mechanism for FLOW + ELIXA** (assigned about 11:30). Branch `evid/glp1-admission` @ `a988d278`, from frozen main `6260e70c`. **NOT LANDED**; it lands only after Mahmood's hash-bound signature, as V1.0.1.
- **How it admits:** `topics/glp1-ra-mace-t2d.json` declares `adjudicated_results`, and `harness/result_adjudication.py` checks each one at build time, failing closed:
  - the decision's sha256 matches its pin;
  - the eligibility is the exact primary strand;
  - every witness span is verbatim in held bytes whose sha256 is pinned (16 for FLOW, 10 for ELIXA);
  - the estimate and both bounds sit in one witnessed span;
  - a named definition witness gives exactly the three canonical components.
- **Where it is enforced:** the pipeline injects the rows, admissibility re-verifies them, and they leave the known-missing panel and the invalidation reasons.
- **Result, from the real build:** k=10, 0.8613 (0.8069–0.9194), PI 0.7531–0.9852, tau² 0.0027.
- **Result-change notice:** k 8 → 10, carrying the ELIXA prespecification dispute with three sources quoted. The reviewer countersignature is OPEN, so the gate refuses the page until it is signed.
- **Tests:** 13/13. Nine fired before the fix, on k=8 ≠ 10; that run is recorded. Three V1-state tests were rewritten to the new requirement.
- **Bundle:** 8 of 10 rows admissible.
  - ELIXA fails P5 (its family object says UNKNOWN), P9 (the unrounded tuple's clause does not name the endpoint) and P11.
  - The independent verifier is unchanged and refuses FDA-text rows under its limit L14.
- **Open for the captain and Mahmood:**
  - (A) lift L14?
  - (B) ELIXA: Table 8 rendering vs unrounded interval?
  - a site-wide certificate refresh (the harness code moved);
  - a rebase onto the V1 candidate;
  - the signature.
- **Handover:** `outputs/handover/lanes/EVID_GLP1_ADMISSION_V1.0.1.md` on that branch. The captain and nr could not be identified among the open sessions, so this is relayed through Mahmood.
- **Note on the report text:** the standard line "no route that admits a row exists or was created" refers to the entry-population evidence. An admission route for FLOW and ELIXA now exists, unlanded, on the branch above.

**V1.1 outcome-specific RoB 2 PROPOSALS** (branch `evid/v1.1-rob2` @ `ab286358`, not for the freeze).
- **Coverage:** 50 of 50 domains carry held evidence (10 trials × 5 domains).
- **Proposals:** 46 low, 4 some_concerns (LEADER D1, EXSCEL D5, ELIXA D5, PIONEER 6 D5). All are PROPOSAL_AWAITING_HUMAN_REVIEW; none is final, and none was relabelled high.
- **Consistency audit, all five domains:** it moved PIONEER 6 D5 from low to some_concerns. Its SAP line does not date the plan: v2.0 Final is dated 01 Nov 2018 and no held span dates the unblinding. This was the first move toward concerns.
- **Blind reads** (same model family, so blind but not independent):
  - read 1: 39/50 after reconciliation;
  - read 2: 46/50;
  - read 3: 3/5 on the domains that changed after read 2.
- **Direction warning:** six post-read changes moved toward low, and one moved toward concerns.
- **ELIXA D5** quotes the three sources of the prespecification dispute.
- **Handover:** `outputs/handover/lanes/EVID_V1.1_ROB2.md` on that branch.

**Disk and temp.**
- The scratchpad was archived to `F:\mh-archive\evid-scratch-2026-09-26.tar.gz` (109/109 verified), then emptied.
- The evid-wt `cache/` is sparse-excluded; undo with `git sparse-checkout disable`.
- The admission worktree sits at `F:\mh-lanes-wt\glp1-admit` (about 0.9 GB, sparse, GLP-1 cache only).
- C: about 6 GB free, F: about 3 GB free.
