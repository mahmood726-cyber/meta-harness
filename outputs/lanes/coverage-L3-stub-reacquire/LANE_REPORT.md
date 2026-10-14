# L3 acquisition tool report

Implemented `scripts/reacquire_stub_fulltexts.py` and synthetic, mocked-urllib tests in
`tests/test_reacquire_stub_fulltexts.py`. No network acquisition, commit, push, or cache modification occurred.

## Behavior

- Reads both the actual path-keyed `documents` registry and the list form described in the brief.
  Selects STUB/METADATA records with typed identifiers. For the actual registry, identifiers can be
  read from explicit `ft_<PMID>` or `cache/comparators/<PMID>/` path components. Unidentified comparator
  files are excluded, not assigned guessed identifiers. `--slug`, `--pmids`, and `--dry-run` are supported.
- Resolves PMIDs through the specified Europe PMC core search, validates the returned PMID/source/PMCID,
  and records `isOpenAccess` and `license` without treating those metadata as permission to store a body.
  Tries Europe PMC JATS, then the NCBI OA service and its official HTTPS OA package link. PMCID-only
  inputs skip PMID resolution and use the PMCID as the output filename.
- Captures immutable response bytes in memory before interpretation, with SHA-256, requested/final URLs,
  UTC start/end times, HTTP status, content type, XML encoding declaration, declared length, and truncation.
  Rejected response bodies and downloaded archives are not persisted. Archive members are read in memory,
  never extracted by their paths. The selected JATS member has its own digest and package provenance.
- Uses `harness.copy_licence.classify_permissions` and `harness.source_coverage.label_document` directly.
  Storage additionally requires parseable XML and matching article identifiers; manuscripts are rejected.
  Permissions elements are normalized for the existing reader; there is no parallel licence vocabulary.
- At most three attempts per request, with exponential backoff only for 429/5xx and at least 0.5 seconds
  between request starts. A 403 or HTML/challenge result stops that document. Redirects are recorded rather
  than followed. All requested URLs are confined to the named service/download hosts.
- Writes only eligible XML and `manifest.json` under dated acquisition directories. The manifest contains
  one entry per attempted source document and every route/retry outcome, including rejected-body digests.
  Exclusive file creation accepts identical existing bytes and refuses differences. Existing dated manifests
  are refused before network access; a later run needs a new date. Duplicate source records remain separate
  manifest entries and cannot silently replace differing bytes under a shared identifier.

## Static versus dynamic disclosure

| Item | Static or dynamic | Basis |
| --- | --- | --- |
| Endpoint templates, HTTPS host allowlist, 0.5-second interval, three attempts, 64 MiB capture/member limit | Static policy | Brief plus bounded resource/route safeguards |
| Licence vocabulary and FULLTEXT label | Existing shared implementation | Imported canonical functions, not copied rules |
| Selected identifiers and slugs | Dynamic | Registry fields or explicitly typed registry path components |
| Search identifiers, OA flags, licence metadata, returned article identifiers | Dynamic | Acquired service/JATS responses; match checked before storage |
| Digests, transport metadata, outcomes, stored bodies | Dynamic | Actual received bytes and validation results |
| Dates/timestamps | Dynamic | UTC runtime clock; tests supply a fixed directory date |
| Test articles, identifiers, package and error responses | Static synthetic fixtures | Test-only, mocked urllib; no research claims |

## Tests and what each pins

All names below are in `tests/test_reacquire_stub_fulltexts.py`; parameterization produces 30 passing cases.

| Test | Contract |
| --- | --- |
| `test_cc_by_fulltext_stored_with_provenance` | Exact accepted bytes, digest, headers, encoding, timestamps, route short-circuit and pacing |
| `test_restricted_never_stored` (3) | NC, ND and SA produce CC_RESTRICTED and no XML file |
| `test_stub_and_html_never_stored` (3) | Missing body, PMC no-download response and HTTP-200 HTML error are not replacements |
| `test_append_only_different_bytes_refused` | Different existing XML is refused; identical writes are harmless |
| `test_existing_manifest_refused_before_network` | An existing dated manifest is never overwritten |
| `test_429_then_success` | urllib HTTPError body/status retained, bounded retry succeeds and records backoff |
| `test_retry_budget` (3) | 429, 500 and 503 exhaust exactly three attempts |
| `test_denial_and_challenge_stop_without_route_around` (2) | Neither 403 nor a challenge triggers retries or fallback routes |
| `test_truncation_refused` | Content-Length mismatch prevents storage |
| `test_dry_run_no_writes_or_http` | Dry run lists identifiers and performs neither HTTP nor writes |
| `test_filters_and_real_registry_shape` | Path-keyed registry, label selection, typed paths, slug/PMID filtering and unknown-ID exclusion |
| `test_unread_terms_manuscript_and_wrong_identifier` | Closed/unread terms, author manuscripts and mismatched article IDs are rejected |
| `test_oa_fallback_package_checked_without_extracting_paths` | Route order, official FTP-to-HTTPS mapping, JATS member validation and no path extraction |
| `test_pmcid_only` | PMCID-only input is supported and uses its identifier as filename |
| `test_search_identity_mismatch_fails_closed` | An unrelated search result cannot supply the requested article's PMCID |
| `test_redirect_not_followed_and_host_allowlist` | Redirects, publisher hosts, plaintext HTTP and userinfo-host confusion cannot expand routes |
| `test_network_error_not_retried` | Transport errors are recorded without unsupported retries |
| `test_invalid_slug_refused` | Output traversal through a registry slug is refused |
| `test_cc0_public_domain_stored` (2) | Shared classifier accepts CC0 and public-domain permissions |
| `test_malformed_fulltext_never_stored` | A superficially complete body inside malformed XML is rejected |
| `test_incomplete_read_captured_before_rejection` | Partial bytes are hashed, marked incomplete and never stored |
| `test_oa_link_cannot_target_publisher` | An OA service link cannot authorize publisher scraping |

## Verification and unmet finish condition

The exact requested command was run:

```text
python -m pytest -q tests/test_reacquire_stub_fulltexts.py tests/test_source_coverage.py -p no:cacheprovider
```

Initial result: 43 passed, 8 failed (25 new acquisition cases passed). After adding five additional
acquisition cases and summary fields, the same combined selection with `--tb=no` reported
**48 passed, 8 failed** (30 acquisition cases and 18 existing coverage cases passed).

All eight failures are existing coverage tests raising `FileNotFoundError` because this checkout has no
`cache/` directory. A directory check and repository filename search confirmed the required held fixtures
are absent; related typed-arm witnesses are not substitutes for the source bytes. The affected tests are:

- `test_PLANT_pmc_no_download_responses_are_stubs`
- `test_PLANT_a_portal_page_is_metadata_not_a_comparator_full_text`
- `test_a_self_declared_excerpt_keeps_its_own_label`
- `test_real_full_texts_stay_full_texts`
- `test_PLANT_the_census_abridgements_are_excerpts`
- `test_unicode_spaces_in_a_pubmed_label_are_whitespace_not_missing_text`
- `test_a_revised_pubmed_record_is_a_complete_earlier_version_not_an_abridgement`
- `test_PLANT_a_saved_http_error_page_is_a_stub`

The required all-green finish condition is therefore **not met**. No fixtures were fabricated, coverage tests
weakened, or cache populated: the brief explicitly says never to touch `cache/`. The coverage lane must run
the required command in its fixture-equipped checkout. The blocker is also recorded in `STUCK_FAILURES.md`.
Live HTTP compatibility is deliberately unverified because network execution is forbidden for this lane.
No project submission/release status was promoted or portfolio records changed.

Deliverable patch: `lane.patch`, containing only the tool, tests, this report and blocker log.
The requested `git add -N` was attempted but failed: Git could not create `.git/index.lock` (permission denied).
The workspace permits reading Git metadata but denies index writes. An equivalent Git new-file patch was
generated using `git diff --no-index -- /dev/null <file>` for each deliverable, preserving UTF-8 without BOM.
`git apply --reverse --check lane.patch` verifies that the patch matches the current files without changing them.
The pre-existing untracked `LANE_PROMPT.md` and `lane.log` are excluded. No commit or push was made.
