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

## Item 2 -- frozen GLP-1 release archive (`docs/releases/glp1-ra-mace-t2d/1b3b0b8dcf3d/`)

| file | what it shows |
|---|---|
| `04-archive-test-red-without-archive.txt` | `tests/test_release_archive.py` with `docs/releases/` moved aside: `test_there_is_a_frozen_glp1_archive` FAILS and the three per-archive tests skip -- the denominator check fires, so an absent archive cannot pass as an empty green |
| `05-outsider-replay-fresh-dir-no-network.txt` | the README's commands, verbatim, in a fresh directory outside any repository, network blocked (proxies to a closed local port), PYTHONPATH empty: 131/131 files match SHA256SUMS; `verdict PASS`; `RESULT REPRODUCED` with release_sha256 6a04a3df... equal to the value printed on the archived page; `plant_control.py` -> `CONTROL FIRED` (damaged copy FAIL, untouched PASS); the two traps shown as measured (`--corrupt` stays PASS; `--anchor live` PASS with 0 of 11 fetched); `--url` REFUSED ARTEFACT_UNREACHABLE |

The archive freezes release 1b3b0b8d (landed and attested: `production record 1b3b0b8dcf3d: ATTESTED (1188/1188 served
files equal)`, copied into the archive as `production_record.json`). It is labelled PRE-RELEASE, never v1.
