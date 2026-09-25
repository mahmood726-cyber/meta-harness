# Mahmood: sign everything in one sitting

**On your laptop, in the clone lane NR names for the candidate, in Windows PowerShell.** Until the V1 candidate
lands, that clone is `C:\mh-sign` on branch `sign/mahmood-2026-09-25`. Once it lands, lane NR sends the V1 clone
and branch names; the command is the same. You can stop at any time, and what you've signed so far is kept.

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
- Each item shows its plain before → after. Answer **y** to sign, **n** to skip, **r** to read the full notice, or
  **q** to stop. **Nothing is signed without your y.** Information items only need Enter.
- Each signature goes through the guarded sign command. It refuses, writing nothing, if the hash or version anchor
  has moved. A signature is only confirmed once it is found in the ledger bytes.
- At the end it commits once and shows the verifier's count. It pushes only after one final **y**, and it proves the
  push landed.

## 3. What is in the sitting, in this order
1. **GLP-1 MACE primary, k = 10 (FLOW + ELIXA), with the previous k = 8 result on the same page.**
   - HR 0.856 → 0.861, still significant, with more heterogeneity.
   - You approved this in chat ("ten trials please with old k on same page"). That is recorded as your intent; this
     item asks you to sign it.
   - **The ELIXA dispute is stated in its line:** the FDA statistical review calls its 3-point MACE prespecified,
     the FDA summary review calls it a sensitivity analysis, and the registry lists it as neither.
   - Bundle sha256 `170c6922…` is recomputed before your signature is recorded.
2. **The re-derived result-change notices,** from the candidate: those **as-is** first, then those **re-issued**
   (each says which notice it replaces), then any that hinge on a registry-coding ruling. Withdrawn notices
   (e.g. **N29**) are shown as information only, because there is nothing to sign.
3. **evid2's two derived notices:**
   - **EMPA-KIDNEY diabetic ketoacidosis, 5 vs 1** (the registry's diabetic-only count; it was 6 vs 1).
   - **COVID STEROID removed from the serious-adverse-events pool** (its count is a composite of serious adverse
     reactions at day 14).
   If the candidate doesn't carry one of them yet, it is shown as information only and cannot be signed.
4. **PRESERVED-HF: the wording ruling, then its consequence.**
   - The ruling: does "Chronic Heart Failure With Preserved Systolic Function" (PRESERVED-HF, NCT03030235, PMID
     34711976) mean "preserved ejection fraction" here? Your ruling on this wording was relayed. Lane NR first
     mislabelled it DELIVER, which is a different trial (NCT03619213); the ruling stands and is attributed to
     PRESERVED-HF. You confirm it here.
   - Then its consequence on dapagliflozin HFpEF adverse events.

**Not in the sitting:** the notices held for wording (N06, N27, N28, N38), until they are re-worded and re-judged.

## 4. Afterwards
Say "pushed". Lane NR re-verifies every signature from the pushed bytes, counting VALID, STALE, REFUSED and MISSING,
and hands the valid set to the main lane.
