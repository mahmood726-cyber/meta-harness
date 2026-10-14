# Lane L4 — fix three review findings in scripts/reacquire_stub_fulltexts.py (plants FIRST)

A recorded codex review (stub-r1, mc-a10e1eeb) of `scripts/reacquire_stub_fulltexts.py` found:
1. P1 `usable`: the challenge detector searches ordinary response content for 'captcha', so a legitimate JSON search
   result whose title contains "CAPTCHA" is rejected as HTML_OR_CHALLENGE. A challenge is an HTML/challenge PAGE
   (content type text/html, or the known challenge markers in an HTML document) -- never a word inside a JSON/XML body.
2. P1 `assess`: identity validation collects article-id elements from EVERY descendant, so a nested <sub-article>
   (or <response>) can supply the requested PMID/PMCID when the enclosing article's own <front>/<article-meta> does not
   carry it. Identity must come from the enclosing article's own front matter only.
3. P2 `acquire`: a non-object search result entry (e.g. `{"resultList":{"result":[null]}}`) raises AttributeError and
   aborts the whole batch before manifests are written. It must be recorded as UNRESOLVED_IDENTIFIER and the batch
   must continue (catch the shape error, never a bare `except Exception`).

## Do
- For EACH finding first add a test to `tests/test_reacquire_stub_fulltexts.py` (mocked; synthetic bytes only) and run it
  to SEE IT FAIL; then fix the code; then see it pass. Record the fail-then-pass output for each in the report.
- Keep every existing test passing. Do not touch harness/ or any other file. No network.
- Run `python -m pytest -q tests/test_reacquire_stub_fulltexts.py -p no:cacheprovider`.

## Finish condition / artefact
`LANE_REPORT.md` (each finding: the plant, its failing output, the fix, the passing output) and `lane.patch`
(`git diff --no-index` per changed file is fine if the index is read-only). Do not commit, do not push.
