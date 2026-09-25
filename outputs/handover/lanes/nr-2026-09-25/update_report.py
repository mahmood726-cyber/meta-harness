"""Rebuild the lane report so it ends with the FINAL signing list (17 / 4 / 2), and records the afternoon's work:
the signature check (0 of 41), the P5 defect and its tested patch, and the scratch archive. Run from the repo root."""
from pathlib import Path

B = Path("outputs/handover/lanes/nr-2026-09-25")
report = (B / "REPORT_2026-09-25.md").read_text(encoding="utf-8")
final = (B / "FINAL_SIGNING_LIST.md").read_text(encoding="utf-8")
cut = [m for m in ("## 6. Afternoon", "## Signing list for Mahmood (41 OPEN") if m in report]
head = report[:report.index(cut[0])]  # idempotent: rebuild from the part before the afternoon section

afternoon = """## 6. Afternoon: signature check, the P5 defect and its fix, and the final list
**Signatures: 0 of 41.** Mahmood said "I have signed", so I checked rather than assumed. No signature on any of the
41 exists:
- on any branch on GitHub, after a fresh fetch;
- in any local clone on C:, read-only, including the main lane's refs and stash;
- in any commit since 24 Sep 12:00;
- in any recently modified file that mentions a countersignature.

None is valid, stale, or refused; all 41 are missing. The valid set handed to the main lane is **empty**.

**The check defect behind the 13 notices I advised against signing** is in `harness/trial_family.py` at `1fa77f2c`:
- **D1, line 99, `randomised_contrasts`:** a contrast counts only when the arms differ by the agent alone, so no
  drug-vs-active-drug trial can pass. The protocols' declared comparators are never passed in (line 171).
- **D2, line 345, `screen_family`:** a literal substring test on the registry conditions, with no fold. The `*`
  truncation is read literally and MeSH-inverted conditions are missed.
- **D3:** three protocol synonyms, which are Mahmood's call.

`p5-fix/trial_family.patch` (+51/−3) fixes D1 and D2. It is for the main lane to apply and re-certify; nothing is
applied here. What was checked against the held pages:
- The patched module matches the in-memory sweep on 2,393 of 2,393 families, and the control shows 0 mismatches.
- It is monotone: no eligible family loses eligibility.
- The repo's own tests show 0 new failures.
- Every readmitted trial is pooled.
- `git apply` is clean and reproduces the tested module byte-for-byte.

**Effect:**
- 11 notices vanish: N09, N15, N17, N18, N19, N20, N21, N25, N32, N39, N40.
- 7 change: N01, N13, N14, N26, N29, N30, N35.
- 23 are unchanged.
- One new notice appears: NOAC Major bleeding, where ENGAGE AF and ARISTOTLE re-enter.

N08 and N23 are not fixed by it; they are registry-coding questions for Mahmood.

**The final signing list below** holds only the 23 notices the fix leaves unchanged: 17 to sign, 4 held for
wording, 2 for his ruling. Every one of the 19 printed sign commands was replayed as printed, with a test signer,
against a temporary ledger copy. All 19 write a signature the gate accepts, bound to the named judgement and hash,
and the repository ledger stayed unchanged. The main-lane handover is `HANDOVER_MAIN_LANE_P5_FIX.md`.

**Disk.** The lane's scratch went into one archive, `scratch-archive/nr-scratch-2026-09-25.tar.gz` (sha256
849fc979…, 200 entries). It was committed, fetched back, its sha256 and listing matched, and only then was it
deleted from C:. The worktree was narrowed to the files the walker and tests need (227 → 157 MB).

"""
text = head + afternoon + "---\n\n" + final
for dest in (B / "REPORT_2026-09-25.md", Path(r"C:/mh-lanes/nr/REPORT_2026-09-25.md")):
    dest.write_bytes(text.encode("utf-8"))
print(len(text), text.count("countersign_result_change.py sign"))
