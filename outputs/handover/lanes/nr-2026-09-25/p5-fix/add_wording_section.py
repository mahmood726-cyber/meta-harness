from pathlib import Path

section = """
## 4. The notice-wording defects (the 4 held notices, and 3 live on main)
The rendered text of some notices misstates the change, and signing would put Mahmood's name on those words.

**W1 and W2: `p5-fix/notice_wording_W1_W2.patch`** (38 lines, against `harness/result_changes.py` and
`harness/page.py` at `1fa77f2c`; not applied here).
- **W1:** `conclusion_changed` says "the outcome no longer has a pooled estimate" whenever `before.k` is set and
  `after.k` isn't, even when **no estimate was served before** (N30, N32, N39). With the fix, the block says "No
  pooled estimate was served before and none is served now; only the candidate trials changed, and no conclusion
  is withdrawn."
- **W2:** when no interval was served before, `significance(before)` is None. A new interval that excludes the null
  therefore produces no sentence, and the block says "The direction of the estimate is unchanged" (N28, N38).
  With the fix it says "an interval is now served and it excludes the null: a difference is now claimed; no
  interval was served before."
- **Proven with the real modules**, patched in a worktree and restored: exactly **5 of 54** ledger notices change
  rendered hash (N28, N30, N32, N38, N39). **None** of the 17 to-sign notices, the 2 ruling notices or the 13
  signed before 24 Sep changes, so the patch invalidates no signature.
- After V1, N28 and N38 get new hashes. Re-judge them (`notice_rejudge.py`); they then become signable. N32 and N39
  vanish with the P5 fix anyway, and N30 changes anyway.

**W3 is a decision, not a patch.** A notice prints the pooled number even where the outcome withholds it
(HARMS_INCOMPLETE: "no quantitative safety conclusion while source-reporting trials remain unresolved"). This is
why N06 and N27 are on hold. **It is already live on main** in three notices Mahmood signed on 21 Sep:
- ledger 2, dpp4 heart-failure hospitalisation, HR 1.00 (0.83 to 1.20);
- ledger 10, probiotics serious adverse events, RR 0.66 (0.19 to 2.28);
- ledger 11, tocilizumab serious adverse events, 0.81.

On main those pages withhold the number in the outcome section while the signed notice prints it. Fixing the
rendering (tested in memory: "a pooled number is computed (k = N) but this page withholds it") changes those three
signed notices' hashes. They would have to be re-signed, which is a call for Mahmood. Until then, N06 and N27 stay
on hold.
"""
for p in (Path(r"C:/mh-lanes/nr/wt/outputs/handover/lanes/nr-2026-09-25/HANDOVER_MAIN_LANE_P5_FIX.md"),
          Path(r"C:/mh-lanes/nr/HANDOVER_MAIN_LANE_P5_FIX.md")):
    s = p.read_text(encoding="utf-8")
    s = s.replace("\n## 3. What to do for V1", section + "\n## 5. What to do for V1")
    s = s.replace("2. Re-certify and rebuild.", "2. Apply `p5-fix/notice_wording_W1_W2.patch` (see §4). Re-certify and rebuild.")
    assert "## 4. The notice-wording defects" in s
    p.write_bytes(s.encode("utf-8"))

hold_note = ("\n> **What happens to B.** N28 and N38 become signable after the V1 wording fix (W1/W2) re-renders them and "
             "they are re-judged. N06 and N27 wait on your decision about W3, which would also mean re-signing three "
             "notices you signed on 21 Sep (see the handover, section 4).\n")
for p in (Path(r"C:/mh-lanes/nr/wt/outputs/handover/lanes/nr-2026-09-25/FINAL_SIGNING_LIST.md"),
          Path(r"C:/mh-lanes/nr/FINAL_SIGNING_LIST_2026-09-25.md")):
    s = p.read_text(encoding="utf-8")
    marker = "## C. Your ruling first"
    s = s.replace(marker, hold_note + "\n" + marker, 1)
    p.write_bytes(s.encode("utf-8"))
print("ok")
