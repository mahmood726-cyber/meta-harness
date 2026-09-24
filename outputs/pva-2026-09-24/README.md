# PVA lane evidence, 2026-09-24 — every served review page names its verifier

| file | what it shows |
|---|---|
| `01-plant-fires-before-rebuild.txt` | `tests/test_page_verifier.py::test_every_served_review_page_names_a_verifier_that_matches_the_served_bytes` RED on the pre-rebuild served pages (0 verifier blocks on 32 of 32) -- the property test fires before the fix it guards |
| `02-rebuild-invariance-raw.{txt,json}` | `scripts/rebuild_invariance.py --base origin/main (b127522d) --expect-added 0` on the rebuilt pages: 0 of 32 PASS, and on every page the ONLY reason is `1 other text change(s)`, one insert beginning `Check this page yourself.` -- "One program checks this page" on 31, "Two programs" on glp1-ra-mace-t2d. The block is deliberately NOT a tracked (absent/banner) block, so no tracked block is added |
| `03-rebuild-invariance-verifier-divs-removed.{txt,json}` | the same run with only the verifier box and its digest div removed from each new page (`C:\mh-lanes\tmp-pva\strip_digests.py`: exactly one removal on 32 of 32): **32 of 32 PASS** -- ratchet=0, lost=0, added=0, other=0, outcomes_moved=0 on every page, primary k and withdrawn state unchanged; named pages sacubitril-valsartan-hfref, dapagliflozin-hfpef-hosp, empagliflozin-hfpef-hosp, glp1-ra-mace-t2d PASS |

Taken together: the rebuilt pages differ from main's by exactly the verifier box, its digest line, and the digest tokens
that must move when a pinned module (harness/page.py) changes. No outcome's k, estimate or refusal state moved on any page.

Generator: `python scripts/build_topic.py <slug> --now 2026-09-11` for all 32, sequentially, on a clean tree at ec139652
(every EXECUTION_RECORD says `CLEAN_EXCEPT_OWN_OUTPUTS`, generating_commit ec139652).

History of this item on the branch, all recorded rather than rewritten:
- rebuild at 946a679f discarded before commit: 25 of 32 records DIRTY (files added to the worktree mid-run);
- rebuild at 20bdd23e committed (f5a2ce2e) with the block as a tracked `banner`; CI refused db59eea3 and 92c5ce68 at
  `tests/test_limitations_legacy_compare.py` (a tracked block on a page must be a limitation object) and at the fix-state
  limb (`docs/fix_ledger.json` stale: fix M2 depends on harness/page.py);
- rebuild at ec139652 (this evidence): the block has its own class; the fix ledger is re-rendered (M2 -> STALE, a true
  statement: its dependency changed).
