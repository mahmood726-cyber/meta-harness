# PVA lane evidence, 2026-09-24 — every served review page names its verifier

| file | what it shows |
|---|---|
| `01-plant-fires-before-rebuild.txt` | `tests/test_page_verifier.py::test_every_served_review_page_names_a_verifier_that_matches_the_served_bytes` RED on the pre-rebuild served pages (0 verifier blocks on 32 of 32) -- the property test fires before the fix it guards |
| `02-rebuild-invariance-raw.{txt,json}` | `scripts/rebuild_invariance.py --base origin/main (9fc4518a) --expect-added 1 --added-text "Check this page yourself." --added-marker "data-page-verifier="` on the rebuilt pages: 0 of 32 PASS, and on every page the ONLY reason is `1 other text change(s)`, the insert `sha256 of each served verifier, as served with this page...` -- the digest line, placed outside the tracked banner on purpose (see harness/page.py) |
| `03-rebuild-invariance-digest-div-removed.{txt,json}` | the same run with only that digest div removed from each new page (`C:\mh-lanes\tmp-pva\strip_digests.py`: exactly one div removed on 32 of 32): **32 of 32 PASS** -- ratchet=0, lost=0, added=1 (the banner, beginning "Check this page yourself."), other=0, outcomes_moved=0, primary k and withdrawn state unchanged on every page; named pages sacubitril-valsartan-hfref, dapagliflozin-hfpef-hosp, empagliflozin-hfpef-hosp, glp1-ra-mace-t2d PASS |

Taken together: the rebuilt pages differ from main's by exactly the added banner, the digest line, and the digest tokens
that must move when a pinned module (harness/page.py) changes. No outcome's k, estimate or refusal state moved on any page.

Generator: `python scripts/build_topic.py <slug> --now 2026-09-11` for all 32, sequentially, on a clean tree at 20bdd23e
(every EXECUTION_RECORD says `CLEAN_EXCEPT_OWN_OUTPUTS`, generating_commit 20bdd23e). A first rebuild at 946a679f was
discarded because 25 of its 32 records said DIRTY (files had been added to the worktree while it ran).
