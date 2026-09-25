# Mahmood: sign everything in one sitting

**On your laptop, in the clone `C:\mh-sign`, in Windows PowerShell.** It takes about 30 to 45 minutes. You can stop
at any time: what you've signed so far is kept.

## 1. Set up the clone (once)
```
git clone --filter=blob:none --no-checkout --branch nr/notice-anchors https://github.com/mahmood726-cyber/meta-harness.git C:\mh-sign
cd C:\mh-sign
git sparse-checkout set --no-cone '/*' '!/*/' '/harness/' '/scripts/' '/tests/' '/registry/' '/topics/' '/protocols/' '/docs/result_changes.json' '/docs/reviews/*/review.json' '/docs/reviews/*/index.html' '/cache/spironolactone-hfref-mortality/records.json' '/signatures/'
git checkout nr/notice-anchors
git switch -c sign/mahmood-2026-09-25
python -m pip install -r requirements.txt
```

## 2. Run the sitting (one command)
```
python scripts/sign_session.py --plan registry/sign_session_plan.json --by "Mahmood" --push-branch sign/mahmood-2026-09-25
```
- It asks you **once**, in your own words, how these items reached you and what you read. That is recorded as
  `how_it_reached_the_reviewer`. At any item, press Enter to reuse it or type something new.
- Each item is shown with its plain before → after. Answer **y** to sign it, **n** to skip it, **r** to read the
  full notice, or **q** to stop. **Nothing is signed without your y.**
- Each signature runs the guarded sign command. It refuses, writing nothing, if the item's hash or version anchor
  has moved. A signature is only confirmed once it is found in the ledger bytes.
- At the end it commits once and shows the verifier's count. It pushes only after one final **y**, and it proves the
  push landed.

## 3. What is in the sitting (23 items, in this order)
- **19 result-change notices:**
  - 17 unchanged by the V1 fix: N02, N03, N04, N05, N07, N10, N11, N12, N16, N22, N24, N31, N33, N34, N36, N37, N41.
  - Then 2 that hinge on your ruling about registry coding: **N08** (the saline control is registered as an active
    drug) and **N23** (the FCM arm is registered as plain "iron"). Sign them only if you accept that reading.
- **1 bundle: the GLP-1 MACE request.** FLOW and ELIXA enter the primary pool: HR 0.856 → 0.861, still significant,
  with more heterogeneity. FREEDOM-CVO enters only the any-delivery strand. **Bundle sha256 `170c6922…`.** It is
  recomputed from the committed bytes before your signature is recorded, and a stale bundle refuses.
- **3 rulings (protocol scope), each a yes/no:**
  - **DELIVER first:** does "Chronic Heart Failure With Preserved Systolic Function" name this review's population?
  - The esketamine trials' "Depressive Disorder, Treatment-Resistant".
  - Omarigliptin in the DPP-4 review.
  Each ruling shows exactly what yes and no change.

**Not in the sitting:**
- **4 held** for wording: N06, N27, N28, N38.
- **18 the V1 fix removes or changes.** They are not signable now; if the candidate lands they are regenerated and
  re-judged.

If the V1 candidate lands before you sit down, lane NR regenerates the plan on the V1 sign branch. You then run the
same command, with the clone and branch names that plan gives.

## 4. Afterwards
Say "pushed". Lane NR re-verifies every signature from the pushed bytes, counting VALID, STALE, REFUSED and MISSING,
and hands the valid set to the main lane.

*Tested end to end on 25 Sep in a throwaway clone with a TEST identity (never yours), pushing to a local repository,
never to GitHub.*
- **Signing:** 16 notices signed and confirmed VALID by the verifier on the pushed bytes. A planted stale hash on
  N41 was refused.
- **Records:** the GLP-1 bundle was recomputed and recorded; the rulings were recorded as answered; the typed words
  were recorded per notice.
- **Push:** proven by sha and ledger bytes.
- **Refusals:** the script refused a TEST run under your name, a TEST push to GitHub, a TEST identity outside test
  mode, and the wrong branch.
- **Bug found and fixed:** a sparse clone refused `signatures/` until `/signatures/` was added.

See `TEST_RUN_*`.
