# V1.0.1 — the post-signature rerun, scripted

**Purpose.** V1.0 serves **k=8** with FLOW and ELIXA disclosed as a *pending, not adopted* result
change. When Mahmood's hash-bound signature arrives, k=10 lands as a **rerun**, not a rebuild. Every
step below is a command plus the artefact that proves it worked — no step is complete because a
process exited 0.

**Why a rerun and not "apply the number":** the k=10 result must be **derived by this pipeline** from
the admitted trials. No number from `BEFORE_AFTER.json`, from the external reviewer, or from this
document is ever typed into served content. Their figures are a cross-check; the pipeline is the
source.

---

## Step 0 — Preconditions (all four, or stop)

    0a  The signature exists, naming a bundle hash, signed by Mahmood.
    0b  That bundle hash was regenerated AGAINST THE V1.0 CANDIDATE SHA, not against an older main.
    0c  The evid lane's admission mechanism is merged (it did not exist at V1.0 — no branch changed
        anything under topics/, registry/ or harness/).
    0d  Nothing has landed on main since the V1.0 cut, or if it has, main is re-frozen and re-merged
        FIRST and this runbook restarts from step 0.

**0b is the one that will be got wrong.** The bundle binds
`docs/reviews/glp1-ra-mace-t2d/review.json` by content hash, and regenerating the candidate changes
those bytes. A signature taken against main's `review.json` binds bytes V1.0 does not serve. Verify
before accepting the signature:

    python - <<'PY'
    import hashlib, pathlib
    want = "<the sha256 listed in the signature request for review.json>"
    got = hashlib.sha256(pathlib.Path("docs/reviews/glp1-ra-mace-t2d/review.json").read_bytes()).hexdigest()
    print("MATCH" if got == want else f"REFUSE: bound {want[:16]} but serving {got[:16]}")
    PY

If it prints REFUSE, the request is regenerated and re-signed. Do not proceed on a near-miss.

## Step 1 — Land the admission

    git merge <evid-branch>            # the mechanism, not the numbers
    git diff --stat HEAD@{1} -- topics/ registry/ harness/

The second command must show a non-empty change. If the admission touches nothing the build reads,
it cannot move the pool, and the merge has landed documentation rather than an admission.

## Step 2 — Regenerate, derived

    python scripts/build_topic.py glp1-ra-mace-t2d
    python scripts/build_bundle.py glp1-ra-mace-t2d

Expect `PRIMARY: ... k=10` on stdout. Measured cost at V1.0: ~30 s for the topic; peak extra disk
0.0 MB (builds rewrite in place).

## Step 3 — Confirm the derived result equals the adjudicated one

    python - <<'PY'
    import json, pathlib
    r = json.loads(pathlib.Path("docs/reviews/glp1-ra-mace-t2d/review.json").read_text(encoding="utf-8"))
    o = next(x for x in r["outcomes"] if x.get("primary"))
    got = o["result"]; mem = o.get("membership") or {}
    want = {"k": 10, "estimate": 0.8613, "ci_low": 0.8069, "ci_high": 0.9194,
            "pi_low": 0.7531, "pi_high": 0.9852, "tau2": 0.0027}
    for key, w in want.items():
        g = got.get(key)
        ok = g == w or (isinstance(g, float) and abs(g - w) < 5e-4)
        print(f"{key:10} served {g!r:12} adjudicated {w!r:10} {'OK' if ok else '*** DIFFERS ***'}")
    pooled = [str(x) for x in (mem.get("pooled") or [])]
    print("pooled k:", len(pooled))
    PY

**A difference here is a finding, not a nuisance.** The adjudicated figures were computed through the
same production path (`harness.known_missing` → `harness.synth.pool`), so a mismatch means the
admission is not admitting what was adjudicated. Investigate before deploying; do not adjust either
number to match the other.

Also assert what *should not* change: direction and significance stay, and **heterogeneity rises** —
τ² 4e-05 → 0.0027, prediction interval 0.8069–0.9081 → 0.7531–0.9852. If τ² is still ~0, FLOW and
ELIXA did not really enter the pool.

## Step 4 — Page content: pending becomes adopted

Three edits, all of which must be visible on the rendered page, not just in JSON:

    1. REMOVE the "pending result change" block (FLOW/ELIXA awaiting sign-off).
    2. The primary result reads k=10, with "previous result (k=8): HR 0.856 (0.809-0.906)" beside or
       below it, per Mahmood: "ten trials please with old k on same page".
    3. The derived notice states: FLOW and ELIXA added after adjudication; direction and
       significance unchanged; heterogeneity NO LONGER ~0, prediction interval widened.

Verify against **rendered** text, never the source — a sentence a reader sees as one string is often
several in the file, split by inline markup, so a source search for it returns nothing and a
"did the edit land?" check silently reports success:

    python - <<'PY'
    import re, html, pathlib
    t = pathlib.Path("docs/reviews/glp1-ra-mace-t2d/index.html").read_text(encoding="utf-8", errors="replace")
    t = html.unescape(re.sub(r"<[^>]+>", " ", t)); t = " ".join(t.split())
    for phrase in ("previous result", "0.856", "awaiting sign-off", "pending"):
        print(f"{phrase!r:22} present: {phrase.lower() in t.lower()}")
    PY

`awaiting sign-off` must now be **False**; `previous result` and `0.856` **True**.

## Step 5 — Derived served diff against V1.0

    python F:/claude-temp/served_diff.py <V1.0-SHA>

**Expected:** GLP-1's primary moves (k, estimate, ci, pi, tau2, i2, pooled membership) and
**nothing else anywhere**. Any other topic moving means the admission reached beyond its scope —
stop and investigate. The base must be the V1.0 SHA, not `HEAD`: diffing against HEAD answers
"what did I change since my last commit", not "what does a deploy move".

## Step 6 — The full gate, once

    python scripts/verify_all.py

All 11 limbs. Budget **~1.5 h** (limb 1 is the whole pytest suite, ~67 min; limb 6 the held-out leak
detector, ~27 min). Shorten iteration by running only the failing limbs locally first
(`F:/claude-temp/run_limbs.py <limb> ...`) and spending the full run on a tree already expected to
pass. **Never weaken or bypass a limb.** A limb that cannot execute is not a pass.

Known trap, already paid for once: adding any file under `docs/evidence/<dir>/` refuses limb 4 until
the directory has a block in `docs/evidence/CAPTIONS.json` **and** the entry pages are regenerated:

    python scripts/build_evidence_index.py

## Step 7 — Deploy, then verify on the SERVED bytes

Deploy is a separate job from the push and has failed silently before — 14 consecutive main deploys
died before any check ran. So:

    - confirm the deploy job ran, and check the STEP's conclusion, not the run's: a green run can
      contain a skipped step;
    - re-run the probes and F.6 acceptance against the bytes actually served, fetched from the live
      URL, not against the local tree;
    - confirm the served page's own digest matches what the page claims.

**"Pushed" is not "deployed", and "green" is not "ran".**

## Step 8 — Records

    - update outputs/RELEASE_NOTE_V1.md: k=10 adopted, the signature and its bundle hash, the date.
    - record the signature in the decisions record with decided_by / decided_on /
      how_it_reached_the_reviewer.
    - the k=8 result stays on the page as the previous published result. It is not deleted; a
      superseded served number that vanishes cannot be audited.

---

## Carried into V1.0.1 or later, not fixed at V1.0

    POOL / five-verdicts / selected-set   oc's verify_bundle and POOL touch disjoint features of the
                                         same file; a 3-way apply lands conflict markers, and the
                                         admission file is not a place to hand-guess. Parked at
                                         C:/mh-artefacts/parked-tests-2026-09-26 with its tests.
    tag stripping `<[^>]+>`              84 of 892 held text fields damaged; 0 of 433 declared-absent
                                         entries affected, so no wrong served number.
    gitblob per-file fallback            938 process spawns where --stdin-paths would use 2.
    ordered-contrast prose equality      a guard compares a long sentence by exact match; it cannot
                                         tell a wrong direction from a reworded one.
    evid2 Q1/Q3 notices                  if they did not make the V1.0 cut.
