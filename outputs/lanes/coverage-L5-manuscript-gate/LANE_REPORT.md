# Lane L5 report

Implemented the scoped author-manuscript gate repair. No network, commit, or push.

## Plants before the fix

Added synthetic CC BY research-article tests with author-manuscript markers in a reference title, body prose, sub-article front, response front, and a nested sub-article inside the enclosing front. Each runs with and without a default XML namespace and must be ACCEPTED.

Opposite controls require AUTHOR_MANUSCRIPT for the enclosing article type and its own front custom metadata, notes, permissions, NIHMS identifier, and NIHPA marker. These are synthetic fixtures, not claims about real source records.

Command (bytecode writes disabled through PYTHONDONTWRITEBYTECODE=1):

```text
python -m pytest -q tests/test_reacquire_stub_fulltexts.py -p no:cacheprovider
```

Observed failing output excerpts, before changing implementation:

```text
FFFFFFFFFF....F............................................              [100%]
___ test_foreign_manuscript_marker_does_not_reject_parent[reference-False] ____
>       assert r.assess(raw, {"pmid": "123"}, "PMC456", meta), meta
E       AssertionError: {'label': 'FULLTEXT', 'licence': 'CC', 'licence_statement': 'Creative Commons Creative Commons', 'outcome': 'AUTHOR_MANUSCRIPT', ...}
E       assert False
```

All ten foreign-marker cases failed with AUTHOR_MANUSCRIPT instead of ACCEPTED. The own-front NIHPA case also failed because it was incorrectly accepted. The other own-front controls and article-type control passed.

```text
11 failed, 48 passed in 5.52s
```

## Fix

`assess` now searches only copies of the enclosing article's direct front elements, pruning back, ref-list, body, sub-article, and response subtrees. Namespace-aware selection retains namespaced JATS support. Front tails are excluded. The enclosing article-type check is retained and NIHPA joins the existing author-manuscript and NIHMS markers. Licensing, identifiers, and fulltext gates are otherwise unchanged.

## Verification

Same command after the fix:

```text
...........................................................              [100%]
59 passed in 3.70s
```

All 43 pre-existing cases and 16 new cases pass. `lane.patch` contains only the script and test changes. Pre-existing untracked LANE_PROMPT.md and lane.log are excluded.
