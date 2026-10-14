# Lane L6 report

Completed the two findings with tests planted before implementation changes. No network, commit, or push was performed. Only the specified script and test file were edited, plus the two required delivery artifacts.

## Plants and failing output

Added synthetic, mocked regressions in `tests/test_reacquire_stub_fulltexts.py`:

- Manuscript mentions in abstract, trans-abstract, title-group, kwd-group, and ordinary front prose must not reject a research article, with and without namespaces.
- A manuscript-typed article ID must reject even without an NIHMS value; an NIHMS ID remains a rejection signal.
- BadStatusLine, IncompleteRead, and RemoteDisconnected at open/read stages must preserve the batch manifest, record the error, avoid retries, and allow a second document to succeed.

Before changing the script, ran:

```text
python -m pytest -q tests/test_reacquire_stub_fulltexts.py -p no:cacheprovider --tb=line
14 failed, 63 passed in 3.40s
```

Failure excerpts:

```text
test_front_prose_manuscript_mentions_are_not_status: AssertionError
  outcome: AUTHOR_MANUSCRIPT (expected ACCEPTED; all ten cases failed)
test_structured_manuscript_identifier_rejected: assert not True
  manuscript ID accepted-version was accepted
test_http_exception_preserves_batch_manifest[BadStatusLine-open]
  http.client.BadStatusLine: b'partial'
test_http_exception_preserves_batch_manifest[BadStatusLine-read]
  http.client.BadStatusLine: b'partial'
test_http_exception_preserves_batch_manifest[IncompleteRead-open]
  http.client.IncompleteRead: IncompleteRead(7 bytes read)
```

RemoteDisconnected was already caught through OSError inheritance; IncompleteRead during read already preserved partial bytes. These passing controls remain covered.

## Fix

Manuscript detection now selects the enclosing article's article-type and direct article-meta status fields: article IDs, custom-meta (including custom-meta-group), notes, and permissions. It ignores unrelated front matter and excludes nested article/prose regions from selected fields. Manuscript-typed IDs are detected explicitly. Existing direct custom-meta text compatibility is preserved.

Client.fetch now also catches http.client.HTTPException in its outer transport handler. Attempts retain the exception class name and existing retry rules. The special partial-byte IncompleteRead handler remains unchanged.

## Passing output

```text
python -m pytest -q tests/test_reacquire_stub_fulltexts.py -p no:cacheprovider
........................................................................ [ 93%]
.....                                                                    [100%]
77 passed in 3.69s
```

`git diff --check` passed with no output. All original tests passed. Source review confirmed the new identifiers are synthetic fixture values, not research claims or source records.

## Static versus dynamic disclosure

| Item | Kind | Evidence / use |
| --- | --- | --- |
| Fixture IDs, dates, XML, and exception payloads | Static synthetic | Mock-only regression inputs; no real acquisition claims |
| Allowed status-field paths and exception class | Static implementation rules | Required by the lane findings |
| Test counts and outcomes | Dynamic | Observed local pytest runs above |
| Manifest and second-document results | Dynamic | Generated in pytest temporary directories and asserted by regression tests |

`lane.patch` contains the source and test diff. Pre-existing untracked `LANE_PROMPT.md` and `lane.log` were left untouched.
