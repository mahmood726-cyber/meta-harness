# Lane L6 — final two review findings in scripts/reacquire_stub_fulltexts.py (plants FIRST)

Recorded codex review stub-r3 (mc-bdaa5bbf), the LAST round:
1. P1 `assess`: the manuscript gate still reads any front-matter TEXT, so an <abstract> saying "the separate protocol is
   available as an author manuscript" rejects a research article. Read manuscript status ONLY from structured fields
   of the enclosing article: its article-type attribute; <article-id pub-id-type="manuscript"> / an NIHMS id;
   <custom-meta> (meta-name / meta-value); <notes> in article-meta; <permissions> statements. Never <abstract>,
   <trans-abstract>, <title-group>, <kwd-group>, or prose.
2. P2 `Client.fetch`: `http.client.HTTPException` subclasses (BadStatusLine, IncompleteRead, RemoteDisconnected ...)
   escape the caught transport exceptions, so one malformed response aborts the batch before manifests are written.
   Record it as a transport error attempt (no retry beyond the existing rules) and let the batch continue.

## Do
For each: add the test to `tests/test_reacquire_stub_fulltexts.py` (synthetic, mocked), SEE IT FAIL, fix, see it pass;
keep every existing test passing (`python -m pytest -q tests/test_reacquire_stub_fulltexts.py -p no:cacheprovider`).
Touch no other file. No network.

## Finish condition / artefact
`LANE_REPORT.md` (plants, failing output, fix, passing output) and `lane.patch`. Do not commit or push.
