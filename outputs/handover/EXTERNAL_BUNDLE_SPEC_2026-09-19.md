# External verification bundle — specification (workshop, 2026-09-19; ready for the chain)

Goal: an outsider follows **held bytes -> span -> value -> pooled result** for any review without importing the harness,
using only HTTPS fetches and a standard library. Measured today (scratchpad `outsider_follow.py`, stdlib only):
every object below is reachable; what is missing is the *index* that tells the outsider where and how.

## What is reachable now (glp1-ra-mace-t2d, served commit 0dd5df02)
| object | URL | status |
|---|---|---|
| served commit | `<site>/_production/manifest.json` -> `commit_sha` | 200 |
| review object | `<site>/reviews/<slug>/review.json` | 200 (742 KB) |
| manifest / certificate / reproduction | `<site>/reviews/<slug>/{manifest,CERTIFICATE,REPRODUCTION}.json` | 200 |
| held bytes (cache, handover) | `https://raw.githubusercontent.com/<owner>/<repo>/<commit_sha>/<document_ref>` | 200 (repo is PUBLIC) |
| held bytes via the Pages site | `<site>/cache/...` | 404 (docs/ only is served) |
| off-tree originals (e.g. MedR PDF) | declared `original_pdf_held: false` | not reachable, declared |

Outsider results: review_sha256 recomputed == manifest; 6/8 primary spans verbatim in held abstract (2 differ only by
Lancet middle-dot decimals, see rule S2); 8/8 digits-in-span; DL re-pool 0.8560 vs served 0.856; 12/12 certificate
held-document digests match raw bytes.

## BUNDLE.json (one per review, written by the build beside manifest.json)
```
{
 "object": "EXTERNAL_BUNDLE", "schema_version": 1,
 "slug": "...", "commit_sha": "<40 hex of the commit the page was built from>",
 "raw_base": "https://raw.githubusercontent.com/<owner>/<repo>/<commit_sha>/",
 "site_base": "https://<owner>.github.io/<repo>/",
 "canonicalisation": {
   "R1_review_sha256": "sha256(utf8(json.dumps(review_without_key('reproduction'), sort_keys=true, ensure_ascii=false, separators=[',',':'])))",
   "R2_html_sha256":   "sha256(bytes of index.html as served)",
   "R3_file_sha256":   "sha256(raw bytes at raw_base + path; line endings exactly as committed, never re-normalised)",
   "S1_span_whitespace": "collapse runs of whitespace to one space on both sides before matching",
   "S2_span_decimal":    "replace U+00B7, U+2027, U+2219 with '.' on both sides before matching (Lancet decimals)",
   "S3_span_html":       "for records.json abstracts and ft_*.txt, match against the raw text; tags are part of the bytes",
   "N1_digits":          "effect, ci_low, ci_high as printed in the row must occur as substrings of the matched span",
   "P1_pooling":         "yi = ln(effect); vi = ((ln(ci_high) - ln(ci_low)) / (2*1.959964))^2 for effect+CI rows; 2x2 rows: yi = ln((ai/n1i)/(ci/n2i)), vi = 1/ai - 1/n1i + 1/ci - 1/n2i (0.5 added to every cell only if any cell is 0)",
   "P2_registered_ci":   "Paule-Mandel tau2, Hartung-Knapp-Sidik-Jonkman interval with t(k-1); refused at k=2 (K2_SINGLE_DF) -- the served point estimate must equal the outsider's RE estimate to 4 dp; the interval is registered, not re-derivable by DL"
 },
 "expected": { "review_sha256": "...", "html_sha256": "...", "protocol_sha": "...", "certificate_sha256": "sha256 of CERTIFICATE.json bytes" },
 "held_documents": [ {"path": "cache/<slug>/records.json", "sha256": "...", "bytes": 50567}, ... ],   // = CERTIFICATE.held_documents + every document_ref cited by a served row
 "rows": [
   {"outcome": "...", "trial_id": "PMID 27295427", "document_ref": "cache/<slug>/records.json#PMID-27295427",
    "document_sha256": "...", "span_field": "endpoint_result_span", "span_sha256": "sha256(utf8(span after S1,S2))",
    "values": {"effect": 0.87, "ci_low": 0.78, "ci_high": 0.97, "scale": "HR"}, "yi": -0.1393, "vi": 0.003118,
    "endpoint_binding": "named_endpoint_resolved_to_definition_span | numbers_only | unbound_legacy | registry_outcome_measure",
    "definition_span_sha256": "... or null"}
 ],
 "pooled": [ {"outcome": "...", "k": 8, "estimate": 0.856, "scale": "HR", "method": "PM/HKSJ", "ci_state": "SERVED|REFUSED_K2"} ],
 "not_reachable": [ {"path": "...", "why": "original_pdf_held: false; off-tree archive"} ]
}
```
Rules the generator must obey: every value in `rows` is copied from the review object (no retyping); `span_sha256`
and `yi/vi` are derived by the stated formulas; the bundle is written AFTER review_sha256 is fixed and is itself
digested into manifest.json as `bundle_sha256`; `verify_all` gains a limb that replays the outsider walk from the
bundle alone (stdlib), fail-closed.

## Outsider procedure (what BUNDLE.json lets a stranger do, in order)
1. GET site_base/_production/manifest.json; check `commit_sha` == bundle.commit_sha.
2. GET review.json; apply R1; compare to expected.review_sha256.
3. For each row: GET raw_base + document_ref path (before '#'); R3 digest == document_sha256; locate span under S1/S2
   (for records.json, inside the record whose id follows '#'); N1 digits; recompute yi/vi under P1; compare.
4. Re-pool under P2 (or DL as a sanity check of the point estimate); compare to `pooled`.
5. Anything in `not_reachable` is a declared gap, not a failure; anything else that fails to fetch or match IS a failure.

## What this does NOT prove (state on the page)
The bundle proves the served numbers are what the held bytes say. It does not prove the held bytes are the source's
bytes: today 100/100 pooled records are `retrieval_ledger: legacy_unrecorded` (typed, not fetched), and 2 of them
(SOUL 40162642, omarigliptin 28893244) are condensed versions of the PubMed abstract. The bundle should carry, per
record, `held_text_provenance: FETCHED(body_sha256) | UNRECORDED` so the outsider knows which link is missing.
