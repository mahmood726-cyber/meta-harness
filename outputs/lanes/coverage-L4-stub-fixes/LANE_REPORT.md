# Lane L4 report

Implemented the three requested findings. No network requests, commits, or pushes were made. Only the script, its test file, and the two requested delivery artifacts were written. Pre-existing LANE_PROMPT.md and lane.log were left alone.

## Static versus dynamic disclosure

| Item | Source / behavior |
| --- | --- |
| Test identifiers, dates, titles, and XML | Explicit synthetic fixtures only; no research claims |
| HTTP responses | Mocked in memory; no network |
| Production identity and manifests | Derived from received response bytes and validated front matter |
| Challenge rules | Static HTML media type / document-signature checks |

All three plants were added and run against the original implementation before any production fixes. Targeted runs used `python -B -m pytest -q tests/test_reacquire_stub_fulltexts.py -p no:cacheprovider -k SELECTOR --tb=short`.

## 1. Ordinary challenge words

Plant: JSON search titles and XML article prose contain CAPTCHA, cf-chl-, and verify you are human; both must still store valid full text.

Selector: `challenge_words`

Failing output (exit 1):

```text
FF                                                                       [100%]
================================== FAILURES ===================================
________________ test_challenge_words_in_data_are_usable[json] ________________
tests\test_reacquire_stub_fulltexts.py:264: in test_challenge_words_in_data_are_usable
    assert r.run(REGISTRY, tmp_path)[0]["stored"]
E   assert False
________________ test_challenge_words_in_data_are_usable[xml] _________________
tests\test_reacquire_stub_fulltexts.py:264: in test_challenge_words_in_data_are_usable
    assert r.run(REGISTRY, tmp_path)[0]["stored"]
E   assert False
=========================== short test summary info ===========================
FAILED tests/test_reacquire_stub_fulltexts.py::test_challenge_words_in_data_are_usable[json]
FAILED tests/test_reacquire_stub_fulltexts.py::test_challenge_words_in_data_are_usable[xml]
2 failed, 38 deselected in 3.09s
```

Fix: Recognize text/html (including parameters) or an HTML document signature, allowing an XML declaration and leading comments. Do not scan arbitrary data for challenge words.

Passing output (exit 0):

```text
..                                                                       [100%]
2 passed, 38 deselected in 1.95s
```

## 2. Enclosing article identity

Plant: Remove parent IDs and place matching IDs in sub-article or response front matter; check both PMID and PMCID-only matching.

Selector: `nested_identifiers`

Failing output (exit 1):

```text
FFFF                                                                     [100%]
================================== FAILURES ===================================
______ test_nested_identifiers_cannot_identify_parent[True-sub-article] _______
tests\test_reacquire_stub_fulltexts.py:280: in test_nested_identifiers_cannot_identify_parent
    assert not r.assess(raw, {"pmid": "123" if pmid_only else ""}, "PMC456", meta)
E   assert not True
E    +  where True = <function assess at 0x0000020D78E78F40>(b'<?xml version="1.0" encoding="UTF-8"?><article><front><article-meta><permissions><license><ext-link href="https://cr...pmid">123</article-id><article-id pub-id-type="pmc">PMC456</article-id></article-meta></front></sub-article></article>', {'pmid': '123'}, 'PMC456', {'label': 'FULLTEXT', 'licence': 'CC', 'licence_statement': 'Creative Commons Creative Commons', 'outcome': 'ACCEPTED', ...})
E    +    where <function assess at 0x0000020D78E78F40> = r.assess
________ test_nested_identifiers_cannot_identify_parent[True-response] ________
tests\test_reacquire_stub_fulltexts.py:280: in test_nested_identifiers_cannot_identify_parent
    assert not r.assess(raw, {"pmid": "123" if pmid_only else ""}, "PMC456", meta)
E   assert not True
E    +  where True = <function assess at 0x0000020D78E78F40>(b'<?xml version="1.0" encoding="UTF-8"?><article><front><article-meta><permissions><license><ext-link href="https://cr...e="pmid">123</article-id><article-id pub-id-type="pmc">PMC456</article-id></article-meta></front></response></article>', {'pmid': '123'}, 'PMC456', {'label': 'FULLTEXT', 'licence': 'CC', 'licence_statement': 'Creative Commons Creative Commons', 'outcome': 'ACCEPTED', ...})
E    +    where <function assess at 0x0000020D78E78F40> = r.assess
______ test_nested_identifiers_cannot_identify_parent[False-sub-article] ______
tests\test_reacquire_stub_fulltexts.py:280: in test_nested_identifiers_cannot_identify_parent
    assert not r.assess(raw, {"pmid": "123" if pmid_only else ""}, "PMC456", meta)
E   assert not True
E    +  where True = <function assess at 0x0000020D78E78F40>(b'<?xml version="1.0" encoding="UTF-8"?><article><front><article-meta><permissions><license><ext-link href="https://cr...pmid">123</article-id><article-id pub-id-type="pmc">PMC456</article-id></article-meta></front></sub-article></article>', {'pmid': ''}, 'PMC456', {'label': 'FULLTEXT', 'licence': 'CC', 'licence_statement': 'Creative Commons Creative Commons', 'outcome': 'ACCEPTED', ...})
E    +    where <function assess at 0x0000020D78E78F40> = r.assess
_______ test_nested_identifiers_cannot_identify_parent[False-response] ________
tests\test_reacquire_stub_fulltexts.py:280: in test_nested_identifiers_cannot_identify_parent
    assert not r.assess(raw, {"pmid": "123" if pmid_only else ""}, "PMC456", meta)
E   assert not True
E    +  where True = <function assess at 0x0000020D78E78F40>(b'<?xml version="1.0" encoding="UTF-8"?><article><front><article-meta><permissions><license><ext-link href="https://cr...e="pmid">123</article-id><article-id pub-id-type="pmc">PMC456</article-id></article-meta></front></response></article>', {'pmid': ''}, 'PMC456', {'label': 'FULLTEXT', 'licence': 'CC', 'licence_statement': 'Creative Commons Creative Commons', 'outcome': 'ACCEPTED', ...})
E    +    where <function assess at 0x0000020D78E78F40> = r.assess
=========================== short test summary info ===========================
FAILED tests/test_reacquire_stub_fulltexts.py::test_nested_identifiers_cannot_identify_parent[True-sub-article]
FAILED tests/test_reacquire_stub_fulltexts.py::test_nested_identifiers_cannot_identify_parent[True-response]
FAILED tests/test_reacquire_stub_fulltexts.py::test_nested_identifiers_cannot_identify_parent[False-sub-article]
FAILED tests/test_reacquire_stub_fulltexts.py::test_nested_identifiers_cannot_identify_parent[False-response]
4 failed, 36 deselected in 2.87s
```

Fix: Collect only direct article/front/article-meta/article-id elements using namespace-aware wildcards. Require the enclosing root to be article.

Passing output (exit 0):

```text
....                                                                     [100%]
4 passed, 36 deselected in 1.79s
```

## 3. Malformed search entries

Plant: Use null, integer, string, and list entries followed by a valid document in the same batch; require both manifest entries and successful continuation.

Selector: `nonobject_search`

Failing output (exit 1):

```text
FFFF                                                                     [100%]
================================== FAILURES ===================================
_________ test_nonobject_search_record_preserves_batch_manifest[None] _________
tests\test_reacquire_stub_fulltexts.py:294: in test_nonobject_search_record_preserves_batch_manifest
    entries = r.run(registry, tmp_path, date="2026-10-14")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
scripts\reacquire_stub_fulltexts.py:296: in run
    entry, raw = acquire(doc, client)
                 ^^^^^^^^^^^^^^^^^^^^
scripts\reacquire_stub_fulltexts.py:223: in acquire
    matches = [r for r in results if str(r.get("id")) == doc["pmid"] and r.get("source") == "MED"]
                                         ^^^^^
E   AttributeError: 'NoneType' object has no attribute 'get'
__________ test_nonobject_search_record_preserves_batch_manifest[7] ___________
tests\test_reacquire_stub_fulltexts.py:294: in test_nonobject_search_record_preserves_batch_manifest
    entries = r.run(registry, tmp_path, date="2026-10-14")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
scripts\reacquire_stub_fulltexts.py:296: in run
    entry, raw = acquire(doc, client)
                 ^^^^^^^^^^^^^^^^^^^^
scripts\reacquire_stub_fulltexts.py:223: in acquire
    matches = [r for r in results if str(r.get("id")) == doc["pmid"] and r.get("source") == "MED"]
                                         ^^^^^
E   AttributeError: 'int' object has no attribute 'get'
_________ test_nonobject_search_record_preserves_batch_manifest[bad] __________
tests\test_reacquire_stub_fulltexts.py:294: in test_nonobject_search_record_preserves_batch_manifest
    entries = r.run(registry, tmp_path, date="2026-10-14")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
scripts\reacquire_stub_fulltexts.py:296: in run
    entry, raw = acquire(doc, client)
                 ^^^^^^^^^^^^^^^^^^^^
scripts\reacquire_stub_fulltexts.py:223: in acquire
    matches = [r for r in results if str(r.get("id")) == doc["pmid"] and r.get("source") == "MED"]
                                         ^^^^^
E   AttributeError: 'str' object has no attribute 'get'
_____ test_nonobject_search_record_preserves_batch_manifest[bad_record3] ______
tests\test_reacquire_stub_fulltexts.py:294: in test_nonobject_search_record_preserves_batch_manifest
    entries = r.run(registry, tmp_path, date="2026-10-14")
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
scripts\reacquire_stub_fulltexts.py:296: in run
    entry, raw = acquire(doc, client)
                 ^^^^^^^^^^^^^^^^^^^^
scripts\reacquire_stub_fulltexts.py:223: in acquire
    matches = [r for r in results if str(r.get("id")) == doc["pmid"] and r.get("source") == "MED"]
                                         ^^^^^
E   AttributeError: 'list' object has no attribute 'get'
=========================== short test summary info ===========================
FAILED tests/test_reacquire_stub_fulltexts.py::test_nonobject_search_record_preserves_batch_manifest[None]
FAILED tests/test_reacquire_stub_fulltexts.py::test_nonobject_search_record_preserves_batch_manifest[7]
FAILED tests/test_reacquire_stub_fulltexts.py::test_nonobject_search_record_preserves_batch_manifest[bad]
FAILED tests/test_reacquire_stub_fulltexts.py::test_nonobject_search_record_preserves_batch_manifest[bad_record3]
4 failed, 36 deselected in 2.96s
```

Fix: Validate a list of objects before accessing record fields. Raise ValueError for bad shapes, handled by the existing narrow exception clause as UNRESOLVED_IDENTIFIER.

Passing output (exit 0):

```text
....                                                                     [100%]
4 passed, 36 deselected in 1.93s
```

## Final verification

Additional controls cover text/html challenge responses, an HTML document with a leading comment, and a namespaced parent whose nested article has conflicting IDs. Existing tests remain unchanged.

`python -m pytest -q tests/test_reacquire_stub_fulltexts.py -p no:cacheprovider`

```text
43 passed
```

`git diff --check`: PASS. Final source review confirmed identity fields come only from the enclosing front matter and malformed entries cannot abort manifest generation. Synthetic IDs/dates are test inputs, not externally verified research records. No harness files were edited.

`lane.patch` contains the script and test changes relative to HEAD. No project status or submission state was changed.

