# External audit scripts — kept unmodified

These files were written by the **external auditor**, not by this project. They were received on 9 Oct 2026, relayed by Mahmood
through the captain lane, and are committed **byte-for-byte as received**. `SHA256SUMS` pins each file, and
`audit/external/** -text` in `.gitattributes` stops git from normalising them. Do not edit them. A disagreement with them is
reported to the reviewer before anything else is changed.

| file | author | review | what it checks |
|---|---|---|---|
| review05_recalculation.py | external auditor, 9 Oct 2026, review 5 | doac-vte-recurrence | PM + modified HKSJ on the 6 served inputs (asserts 0.9091, 0.7479-1.1050); HR-only sensitivity; 4-trial G1 count-OR check (IV normal, tau2=0) |
| review06_checks.py / review06_checks.json | external auditor, 9 Oct 2026, review 6 | dpp4-mace-t2d | MACE and HF pools (asserts 1.0007 and 1.1296); illustrative HF scenarios; 3 passage digests. The .json is the auditor's own output |
| review08_checks.py / review08_checks.json | external auditor, 9 Oct 2026, review 8 | esketamine-trd-madrs | MD pool (asserts -3.3436, -6.0691 to -0.6180); leave-one-out HKSJ intervals; 3 passage digests |
| review09_checks.py / review09_checks.json | external auditor, 9 Oct 2026, review 9 | finerenone-ckd-t2d-renal | 2-trial pool (asserts 0.8407, Q 0.3859); FDA-label hyperkalemia illustration; 2 passage digests |
| review09b_check_topic9.py | second, browser-based external auditor, 9 Oct 2026, review 9b | finerenone-ckd-t2d-renal | stdlib-only 2-row pool (0.84065; normal 0.7666-0.9218; HKSJ 0.4625-1.5281); 2 passage digests |

The auditors state their own scope in each script: these are independent arithmetic and digest checks, not harness replays.

**How they are used:** `scripts/verify_external_audit.py`, a limb of `scripts/verify_all.py`:
1. Checks every file against `SHA256SUMS`.
2. Runs each script, which must exit 0, so the auditor's own assertions must hold.
3. Diffs the .py output against the auditor's .json where one exists.
4. Compares the auditor's recomputed pooled numbers with the **currently served** `docs/reviews/<slug>/review.json`.

If our served pool ever drifts from the auditor's independent arithmetic, the limb fails. After a **signed** served change,
the expected disagreement is listed in `audit/external/superseded.json` with the item that signed it, and is never silently
ignored.
