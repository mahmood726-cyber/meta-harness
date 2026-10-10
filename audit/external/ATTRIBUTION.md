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


**Bundles received 9-10 Oct 2026 (reviews 10-21), each a folder kept byte-for-byte** (every file pinned in `SHA256SUMS`):

| folder | review | topic | what the limb checks against the served review |
|---|---|---|---|
| review10/ | 10 | glp1-ra-mace-t2d | 8-trial PM + modified HKSJ pool and CI |
| review12/ | 12 | melatonin-primary-insomnia-sol | k=1 mean difference and its 95% CI |
| review13/ | 13 | noac-vs-warfarin-af-stroke | primary pool and CI -- **superseded by V12-01** (signed after the audit pin; see superseded.json) |
| review14/ | 14 | sacubitril-valsartan-hfref | the auditor recomputes a pool the harness withholds: script and output reproduced, nothing served to compare |
| review15/ | 15 | semaglutide-obesity-mace | discontinuation RR reconstruction |
| review16/ | 16 | semaglutide-obesity-weight | PM pooled mean difference |
| review18/ | 18 | sglt2-hfref-hosp-cvdeath | pooled ratio |
| review19/ | 19 | sglt2-primary-prevention-hf | pooled HR and floored HKSJ CI |
| review20/ | 20 | spironolactone-hfref-mortality | PM + HKSJ pool and CI |
| review21/ | 21 | statins-primary-prevention-elderly | two-input pooled estimate |

Reviews 11, 17 and 22-25 were received as written reports only (no executable bundle); there is nothing to run.

The auditors state their own scope in each script: these are independent arithmetic and digest checks, not harness replays.

**How they are used:** `scripts/verify_external_audit.py`, a limb of `scripts/verify_all.py`:
1. Checks every file against `SHA256SUMS`.
2. Runs each script, which must exit 0, so the auditor's own assertions must hold.
3. Diffs the .py output against the auditor's .json where one exists.
4. Compares the auditor's recomputed pooled numbers with the **currently served** `docs/reviews/<slug>/review.json`.

If our served pool ever drifts from the auditor's independent arithmetic, the limb fails. After a **signed** served change,
the expected disagreement is listed in `audit/external/superseded.json` with the item that signed it, and is never silently
ignored.
