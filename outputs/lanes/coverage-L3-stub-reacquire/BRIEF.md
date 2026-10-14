# Lane L3 — re-acquisition tool for STUB full texts (meta-harness, coverage lane, register E1)

E1 found 28 held "full text" objects that are STUBS (a PMC "publisher does not allow downloading" response, an XML with
no body, a saved HTTP error page, an empty file) and 5 METADATA portal pages. Their labels are in
`registry/source_coverage.json` (documents[] with label STUB / METADATA, slug, path, pmid where known). Write the TOOL that
looks for a genuinely open, legitimately licensed replacement for each, with tests. You have NO network: every HTTP call
in tests is mocked. The coverage lane runs the tool against the network afterwards.

## Read first
- `scripts/acquire_bundle_evidence.py` — the acquisition-object pattern to FOLLOW: immutable capture before parsing
  (payload, sha256, requested + final URL, time, content type, status, declared encoding, Content-Length truncation
  check), append-only store (`_write_once` refuses different bytes), dated version directory, a manifest.
- `harness/copy_licence.py` — THE licence vocabulary (do not write a parallel one): `classify_permissions`,
  `names_creative_commons`, `_RESTRICTED_RE`, `upw_open`. Only CC BY / CC0 / public domain is open here; NC / ND / SA is
  CC_RESTRICTED.
- `harness/source_coverage.py` — `label_document(raw)`: a replacement must itself label FULLTEXT, or it is not one.

## Write `scripts/reacquire_stub_fulltexts.py`
- Input: `registry/source_coverage.json`; select documents labelled STUB or METADATA that have a PMID (or PMCID).
- For each, try legitimate open routes in order, stopping at the first FULLTEXT: (1) Europe PMC REST
  `https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML` (PMCID via the Europe PMC search API
  `.../rest/search?query=EXT_ID:<pmid>%20AND%20SRC:MED&format=json&resultType=core`, which also gives isOpenAccess and
  license); (2) NCBI PMC OA web service `https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=<PMCID>`. No scraping of
  publisher sites, no paywall circumvention, no CAPTCHA/bot-challenge handling: a challenge page or 403 is recorded as
  the outcome, never retried around.
- Licence: read it from the acquired JATS `<permissions>` with `harness.copy_licence.classify_permissions`. Store the
  bytes ONLY when the licence is open (CC BY / CC0 / public domain) AND `label_document(bytes)` is FULLTEXT. A
  CC_RESTRICTED, author-manuscript, unread-terms or not-FULLTEXT response is recorded in the manifest (status, licence,
  label, sha256 of what was received) WITHOUT storing its bytes.
- Store: `registry/source_acquisitions/<slug>/fulltext_<YYYY-MM-DD>/<pmid>.xml` + `manifest.json` (one entry per
  document attempted: route tried, outcome, licence, label, sha256, bytes stored or not and why). Append-only.
- Rate limit: >= 0.5 s between requests; bounded retries (3, backoff) only for 429/5xx; HTML error payloads are an
  outcome, never data. `--dry-run` lists what would be tried. `--slug` / `--pmids` narrow the run.
- Never touch `cache/` (the served cache is not rewritten; a replacement is a separate object).

## Tests: `tests/test_reacquire_stub_fulltexts.py` (mock urllib; synthetic payloads only)
Plants that must each fail against a naive implementation: a CC BY JATS with a body is stored; a CC BY-NC one is NOT
stored (manifest says CC_RESTRICTED); a JATS with no <body> is not stored (label STUB); a "publisher does not allow
downloading" response is not stored; an HTML error page with HTTP 200 is not stored; an existing acquisition with
different bytes is refused (append-only); a 429 then 200 is retried and stored; a 403 / challenge page is recorded and
not retried; truncation (Content-Length larger than received) is refused; dry-run writes nothing.

## Finish condition / artefact
Run `python -m pytest -q tests/test_reacquire_stub_fulltexts.py tests/test_source_coverage.py -p no:cacheprovider`
(both must pass). Write `LANE_REPORT.md` (what you built, every test and what it pins, anything in the brief you could
not do and why) and `git add -N` the new files then `git diff > lane.patch`. Do not commit, do not push, do not run the
tool against the network (you have none).
