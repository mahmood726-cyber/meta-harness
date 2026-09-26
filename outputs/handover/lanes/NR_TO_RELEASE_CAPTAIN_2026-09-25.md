# Lane NR → release captain: the 41 result-change notices, for the V1 freeze (Sat 09:00)

This file lives on main so the release captain has it. Everything it cites is on branch `nr/notice-anchors`, under
`outputs/handover/lanes/nr-2026-09-25/`. The full handover is `HANDOVER_MAIN_LANE_P5_FIX.md` there.

## 1. Signatures: 0 of 41, so nothing is clear to land
Mahmood said he had signed, and I verified it rather than assuming. No signature exists on any of the 41:
- on any branch, after a fresh fetch;
- in any local clone on C: (read-only), including the main lane's refs and stash;
- in any commit since 24 Sep 12:00;
- in any recently modified file.

The valid set is **empty**. That is consistent with pva's V1 rehearsal (checklist E: "122 changed values, 0
signed" against `enforcement-gate`).

To re-check at any time:
`python scripts/verify_notice_signatures.py --ref origin/sign/mahmood-2026-09-25` (on `nr/notice-anchors`). It
prints VALID, STALE, REFUSED or MISSING per notice. It never writes.

## 2. The P5 defect behind 13 notices (`harness/trial_family.py` at `1fa77f2c`)
- **D1, line 99, `randomised_contrasts`:** a contrast counts only when two arms differ by the agent alone. No
  drug-vs-active-drug trial can pass, so RE-LY, ROCKET AF, ARISTOTLE, ENGAGE AF, PLATO, PARADIGM-HF and the
  DOAC-vs-VKA trials are all set aside. The protocols' declared `comparator_any` is never passed in (line 171).
- **D2, line 345, `screen_family`:** a literal substring test on the registry conditions, with no `lexicon.fold`
  (screening folds). A `*` truncation is read literally (`antibiotic-associated diarr*`), and MeSH-inverted
  conditions are missed ('Diabetes Mellitus, Type 2').
- **D3:** three protocol synonyms, which are Mahmood's call.

**Patch:** `nr-2026-09-25/p5-fix/trial_family.patch`, sha256 `dbe96e0d9069f973795ccdf6006b0ebe9e054a613c8e12fd988be61ce3f730c6`,
+51/−3. It is not applied anywhere; it needs your re-certification. It was executed against the held pages:
- it matches the in-memory sweep on 2,393 of 2,393 families, and the control shows 0 mismatches;
- it is monotone: no eligible family loses eligibility;
- the repo's own tests show 0 new failures;
- every readmitted trial is pooled (P8 `unbound_legacy`, `admission.py:100`);
- `git apply` is clean.

**Effect on the 41:**
- **11 vanish** (the pool returns to what main serves): N09, N15, N17, N18, N19, N20, N21, N25, N32, N39, N40.
- **7 change** (regenerate, then re-judge with `scripts/notice_rejudge.py`): N01, N13, N14, N26, N29, N30, N35.
- **23 are unchanged.**
- **1 new notice:** `noac-vs-warfarin-af-stroke / Major bleeding`, where ENGAGE AF and ARISTOTLE re-enter.

**Note:** main's `trial_family.py` differs from the gate's (+7/−24), so apply the patch on the lineage you release.

## 3. Notice wording
- **`nr-2026-09-25/p5-fix/notice_wording_W1_W2.patch`**, sha256
  `88e4c4459b8dd1976525cb8cc594b1b43de1c4428fda3883329f40057175d048`, against `result_changes.py` and `page.py`.
  - It fixes "Conclusion withdrawn" where no estimate was ever served (N30, N32, N39).
  - It fixes "direction unchanged" where a new interval now excludes the null (N28, N38).
  - It changes exactly 5 of the 54 ledger hashes, and none that is signed or on the to-sign list (proven with the
    real modules).
- **W3, a decision rather than a patch.** A notice prints a pooled number its page withholds (HARMS_INCOMPLETE).
  **This is live on main** in three notices Mahmood signed on 21 Sep:
  - ledger 2, dpp4 heart-failure hospitalisation;
  - ledger 10, probiotics serious adverse events;
  - ledger 11, tocilizumab serious adverse events.
  Fixing the rendering changes those hashes, so they would need re-signing.

## 4. What Mahmood signs (`nr-2026-09-25/FINAL_SIGNING_LIST.md`)
He signs on his laptop, in the clone `C:\mh-sign`, on branch `sign/mahmood-2026-09-25`, then pushes.
- **17 to sign:** N02, N03, N04, N05, N07, N10, N11, N12, N16, N22, N24, N31, N33, N34, N36, N37, N41. The P5 fix
  leaves all 17 unchanged, so their signatures survive your rebuild. `notice_anchor.guard` tolerates page churn
  and refuses a moved number.
- **4 on hold for wording:** N06, N27, N28, N38.
- **2 for his ruling on registry coding:** N08, N23.

All 19 sign commands were replayed exactly as printed, with a test signer and a temporary ledger copy. All 19 write
a signature the gate accepts.

When he pushes, lane NR verifies from the fetched bytes and hands you the valid set.

## 5. At the freeze (Sat 09:00), what lane NR needs from the candidate
The runbook is `nr-2026-09-25/rederive/V1_NOTICE_RUNBOOK.md` on `nr/notice-anchors`. It was rehearsed end to end on
25 Sep: a synthetic candidate went through re-derivation, registry, sign branch and judgement; all 41 commands were
replayed and gave 41 VALID; and a superseded signing command was refused.
1. **Announce the candidate sha.** Lane NR re-derives every served-number change from its pages against the last
   attested release (`scripts/rederive_notices.py`).
2. **The candidate's ledger must cover every served-number change exactly.**
   - Withdraw the 11 notices the P5 fix removes.
   - Regenerate the 7 it changes.
   - Add the NOAC Major bleeding notice.
   A change with no notice, or a notice whose change doesn't happen, is reported as a V1 blocker, and nothing
   is signable until it is fixed.
3. **Include `nr-p5-fix/trial_family.patch`** (P5 matching plus the arm-contrast rule) and, if you accept it,
   **`notice_wording_W1_W2.patch`**. Without the P5 fix, the 11 notices it removes stay in V1 and are listed to hold,
   not to sign.
4. **Lane NR then builds the sign branch.** That is `nr/v1-sign-<c12>`: your candidate plus the signing tools plus
   the audit registry. It judges every notice against your pages and gives Mahmood the final list, with his clone
   `C:\mh-sign-v1` and his branch `sign/mahmood-v1`. After he pushes, you get the VALID set; merge only
   `docs/result_changes.json` from his branch and rebuild.

## 6. Blocker check on evid2's Q1/Q3 pages (26 Sep 08:10)
`scripts/rederive_notices.py --prev origin/main --cand origin/evid2/q-decisions` exits 1 with **3 unnoticed
served-number changes**:
- corticosteroids-covid19 **SAE**: OR 2.81 → no pooled result;
- the **new outcome** "Serious adverse reactions (septic shock, invasive fungal infection, GI bleeding, anaphylaxis;
  day 14)" appears with its own served result;
- sglt2-ckd **DKA**: RR 6.00 → 5.00.

evid2's branch rebuilt the pages but added no ledger notice for any of them. **If those pages go into the V1
candidate, the candidate's ledger must carry a notice for each of the three**; otherwise pva's probe E and lane NR's
re-derivation both refuse. The signing session already has items for all three, as evid2 D-Q1, D-Q3 and D-Q3b.

## 7. UPDATE 26 Sep ~09:00: evid2 still has one UNNOTICED served change (a V1 blocker if merged as is)
Re-derived `origin/main` 2a45f0cb → `origin/evid2/q-decisions` e1c3125e (`scripts/rederive_notices.py`, exit 1):
- NOTICED (ledger 13): sglt2-ckd-progression / Diabetic ketoacidosis, RR 6.00 (0.72–49.83) → 5.00 (0.58–42.79).
- NOTICED (ledger 14): corticosteroids-covid19-mortality / Serious adverse events, OR 2.81 (0.11–74.56) k=1 → no pooled result.
- **UNNOTICED:** corticosteroids-covid19-mortality / **Serious adverse reactions (septic shock, invasive fungal
  infection, GI bleeding, anaphylaxis; day 14)**: no outcome → **OR 2.81 (0.11–74.56), k=1**. A new served number
  with no result-change notice.
Needed from evid2 before the candidate: a third OPEN notice for that new outcome (or the outcome withheld). The
signing script already carries it as item D-Q3b and turns it from information into a signable item once it exists.
