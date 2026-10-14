# Lane L5 — fix one review finding in scripts/reacquire_stub_fulltexts.py (plant FIRST)

Recorded codex review stub-r2 (mc-84354e92), P1 in `assess`: the author-manuscript gate searches the ENTIRE serialized
article, including the reference list, so a published research article whose <back><ref-list> cites a title containing
"author manuscript" is rejected as AUTHOR_MANUSCRIPT.

The gate must read only the article's OWN manuscript markers: the enclosing <article>'s attributes (article-type),
its own <front> (article-meta: e.g. custom-meta / notes / permissions statements that say it is an author manuscript,
the NIHPA / "Author manuscript" front matter of a PMC author manuscript), never <back>, <ref-list>, <body> prose, or a
nested <sub-article>/<response>.

## Do
1. Add a test to `tests/test_reacquire_stub_fulltexts.py` (synthetic bytes): a CC BY research article with a reference
   titled "... author manuscript ..." must be ACCEPTED; run it and SEE IT FAIL. Keep (or add) the opposite plant: a real
   author manuscript (marker in its own front matter) is still rejected AUTHOR_MANUSCRIPT. Also: the marker inside a
   nested <sub-article> front must not reject the enclosing article.
2. Fix `assess`; see the new tests pass and every existing test still pass:
   `python -m pytest -q tests/test_reacquire_stub_fulltexts.py -p no:cacheprovider`.
3. Do not touch any other file. No network.

## Finish condition / artefact
`LANE_REPORT.md` (the plants, their failing output, the fix, the passing output) and `lane.patch`. Do not commit or push.
