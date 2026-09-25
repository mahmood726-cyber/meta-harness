from pathlib import Path

p = Path(r"C:/mh-lanes/nr/wt/outputs/handover/lanes/NR_DECISIONS.md")
s = p.read_text(encoding="utf-8")
add = """- **E15. Notice wording, and the hand-off on main.**
  - **W1/W2 patch** (`p5-fix/notice_wording_W1_W2.patch`): proven with the real modules, it changes exactly 5 of
    the 54 ledger hashes (N28, N30, N32, N38, N39). It changes none of the 17 to-sign, the 2 ruling or the 13
    already-signed notices.
  - **W3** (a notice prints a pooled number its page withholds) is a decision, not a patch. It is live on main in
    three notices signed on 21 Sep (ledger 2, 10 and 11), and fixing it re-opens those signatures.
  - **Why a pointer on main:** the release captain works from main, and pva's lane lands docs-only handovers
    there. So the pointer `outputs/handover/lanes/NR_TO_RELEASE_CAPTAIN_2026-09-25.md` and the two patches went
    to main through a branch cut from `origin/main`. It fast-forwards only after the required `verify` check
    passes on that exact SHA. It is docs only: no code, page, registry or ledger change.
  - **`scripts/verify_notice_signatures.py`** checks a pushed signing branch from committed bytes and never
    writes. Its verdicts are VALID, STALE (superseded hash or judgement: redo, never re-point), REFUSED (the gate,
    the anchor guard, or a delegated basis) and MISSING.

"""
s = s.replace("## Measured facts", add + "## Measured facts", 1)
p.write_bytes(s.encode("utf-8"))
print("ok")
