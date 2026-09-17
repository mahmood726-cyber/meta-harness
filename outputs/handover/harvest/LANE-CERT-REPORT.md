# LANE CERT report

Base / measured HEAD: `3cf73885ffc83f6fcc4db273c6510a5416cdcde0`.
No commit and no network. Implementation and requested verification completed; measured results follow below.

## Plants FIRST on the base — MEASURED

`python -m pytest tests/test_certificate.py -q --tb=short` exited 1 before implementation:

```text
FF                                                                       [100%]
================================== FAILURES ===================================
__________________ test_held_document_byte_mutation_refuses ___________________
tests\test_certificate.py:29: in test_held_document_byte_mutation_refuses
    assert not ok and any("release_sha256" in r for r in reasons), (
E   AssertionError: held text changed by one byte but reproduce returned True: []
E   assert (not True)
____________________ test_missing_certificate_gate_refuses ____________________
tests\test_certificate.py:38: in test_missing_certificate_gate_refuses
    assert not ok and any("CERTIFICATE.json" in r for r in reasons), (
E   AssertionError: missing certificate has no certificate refusal: []
E   assert (not True)
=========================== short test summary info ===========================
FAILED tests/test_certificate.py::test_held_document_byte_mutation_refuses - ...
FAILED tests/test_certificate.py::test_missing_certificate_gate_refuses - Ass...
2 failed in 14.89s
```

The text plant changes one byte in a copied held regulatory text. Certificate reads use the copied inputs; statistical replay retains the original cache. The missing-object plant copies the page directory and removes CERTIFICATE.json.

## Static versus dynamic disclosure

| Item | Kind | Source / transformation |
|---|---|---|
| Certificate schema, canonicalization, listed code paths | Static contract | SHA-256 canonical JSON; exact bytes for held documents; LF-normalized Git blob identities for source code |
| Protocol commit | Dynamic identity | Existing registration/build anchor; not a new prospective-registration claim |
| Corpus, queries, extraction, screening, bias, config, manuscript | Dynamic | Loaded from the actual topic bundle and replayed review |
| Held source inventory | Dynamic | Topic ft_*.txt/aact_*.json and source refs, following regulatory source manifests to held PDF/text pairs |
| Missing optional family map or effect-type module | Explicit absence | NOT_PRESENT, not a fabricated digest |
| Numerical research outputs | Unchanged | Existing pipeline; no new research findings or identifiers authored |

MEASURED schema clarification: `retrieval_ledger.snapshot.records_sha256` hashes `records.json['records']`, not the entire envelope. The certificate preserves that equality and separately hashes the complete canonical file as `records_file_sha256`. `analysis_code_sha256` hashes the displayed Git blob map; individual Git blob identifiers and the protocol commit are SHA-1 identities, explicitly labelled.

Initial read-only `harness/synth.py` SHA-256: `fc1fa657fad5e5a88d0d7f290bf690287273e4304d69887377742889fd6dacc4`.

## Execution results — MEASURED

All commands used the repository socket guard; replay and full verification used an absolute, empty `.tmp/empty_aact` directory as `AACT_DIR`. Build runner called `build_topic.main(slug, "2026-09-11")` for each existing review.

| Step (execution order) | Exit code |
|---|---|
| `build` | 0 |
| `render_fix_ledger` | 0 |
| `rewrite_fixstate_lines` | 0 |
| `build_evidence_index` | 0 |
| `render_gate_gaps` | 0 |
| `render_gate_scorecard` | 0 |
| `external_agreement` | 0 |
| `index` | 0 |
| `reproduce` | 0 |
| `survival` | 0 |
| `verify_all` | 1 |

Ordered renderers: render_fix_ledger, rewrite_fixstate_lines, build_evidence_index, render_gate_gaps, render_gate_scorecard, external_agreement, then harness.index. The rebuild's incidental last-topic blind-map change and external-agreement newline-only change were restored to base.

### reproduce: verbatim output

```text
  OK  balanced-crystalloids-vs-saline-mortality
  OK  colchicine-postop-af
  OK  colchicine-recurrent-pericarditis
  OK  colchicine-secondary-cv-prevention
  OK  corticosteroids-cap-mortality
  OK  corticosteroids-covid19-mortality
  OK  dapagliflozin-hfpef-hosp
  OK  denosumab-vertebral-fracture
  OK  doac-vte-recurrence
  OK  dpp4-mace-t2d
  OK  empagliflozin-hfpef-hosp
  OK  esketamine-trd-madrs
  OK  finerenone-ckd-t2d-renal
  OK  glp1-ra-mace-t2d
  OK  iv-iron-hfref-hosp
  OK  melatonin-primary-insomnia-sol
  OK  metformin-pcos-ovulation
  OK  noac-vs-warfarin-af-stroke
  OK  omega3-cardiovascular-events
  OK  pcsk9-mace
  OK  probiotics-aad-prevention
  OK  sacubitril-valsartan-hfref
  OK  semaglutide-obesity-mace
  OK  semaglutide-obesity-weight
  OK  sglt2-ckd-progression
  OK  sglt2-hfref-hosp-cvdeath
  OK  sglt2-primary-prevention-hf
  OK  spironolactone-hfref-mortality
  OK  statins-primary-prevention-elderly
  OK  ticagrelor-vs-clopidogrel-acs
  OK  tocilizumab-covid19-mortality
  OK  tranexamic-acid-pph

32/32 reproduce (all reproducible)

```

### survival: verbatim output

```text
pages with every marking kept (count >= base): 32 of 32

```

Final certificate-focused checks: `python -m pytest tests/test_certificate.py -q --tb=short` → **9 passed in 11.64s**. Earlier combined integrity/browser run → **5 passed in 42.41s**, including the all-32-page browser E2E. Additional malformed-object/type-change and fresh-clone-path tests increased the certificate-only count from 4 to 9. The fresh-clone path now refuses a missing certificate even when original and rebuilt HTML match.

The browser test opens every page on `127.0.0.1:8000`, verifies the visible release hash comes first, compares all displayed certificate fields, clicks CERTIFICATE.json, and compares the downloaded JSON to disk. Browser closed and server shut down in finally blocks.

Passing one-byte plant output (verbatim):

```text
one-byte plant: saved release_sha256=16a653da387345966014f01ba8174e0b1369c17e395d12ed8d2ec899591162e8; recomputed=80c7dbcd14293b818bc34bdd09da9e86a3b469b47ead89b8fa62e1606b9d1d41
held-document reproduction: ok=False; reasons=['CERTIFICATE.json release_sha256 mismatch: recomputed 80c7dbcd14293b818bc34bdd09da9e86a3b469b47ead89b8fa62e1606b9d1d41 vs saved 16a653da387345966014f01ba8174e0b1369c17e395d12ed8d2ec899591162e8', 'served index.html does not byte-match a re-render from the replayed core']
```

## Full verify_all table — verbatim

```text
TARGET verify_all: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:179 files files=1 scripts/verify_all.py
VERIFY-ALL: 11 limbs, all run, fail-closed. root=C:\mh-r-CERT
  [             PASS] unit tests (pytest tests/)  (359s)
        TARGET verify_all.limb_unit_tests: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:179 files files=148 tests/test_aact_cache.py tests/test_aact_recurrent_guard.py tests/test_absence_ontology.py ...
  [             PASS] offline reproduction (every live page replays from committed cache)  (69s)
        TARGET verify_all.limb_reproduction: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:178 files files=33 scripts/reproduce_review.py docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json docs/reviews/colchicine-postop-af/review.json ...
  [             PASS] publication gate on every live review page  (56s)
        TARGET verify_all.limb_gate_every_page: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:178 files files=32 docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json docs/reviews/colchicine-postop-af/review.json docs/reviews/colchicine-recurrent-pericarditis/review.json ...
  [             PASS] index currency (generated == committed docs/index.html)  (2s)
        TARGET verify_all.limb_index_currency: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:178 files files=696 docs/index.html docs/evidence/CAPTIONS.json docs/evidence/CAPTIONS.json ...
  [             PASS] served-artefact leak scan (docs/*.json)  (1s)
        TARGET verify_all.limb_leak_scan: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:178 files files=116 docs/arm_object_sweep.json docs/class_discovery.json docs/cochrane_headtohead.json ...
  [             PASS] held-out leak detector (registry/heldout_sealed.json)  (298s)
        TARGET verify_all.limb_heldout: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:178 files files=3 registry/heldout_sealed.json docs/search_recall_regression_corpus.json harness/acquisition.py
  [             PASS] search completeness (search_v2 measurement current; every state explicit; no zero from an exit code)  (2s)
        TARGET verify_all.limb_search_completeness: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:178 files files=3 registry/search_completeness.json harness/search_v2.py harness/search_completeness.py
  [             PASS] fix-state discipline (registry/fixes.json)  (76s)
        TARGET verify_all.limb_fixstate: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:178 files files=3 registry/fixes.json docs/fix_ledger.json scripts/render_fix_ledger.py
  [          REFUSED] honest-state ratchet (no page may get quieter)  (11s)
        TARGET verify_all.limb_honest_ratchet: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:178 files files=34 docs/index.html docs/ratchet_acknowledgements.json docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html ...
        TARGET honest_ratchet: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=2304824034b4ba8677da2d2d2453352711ed2a9b tree=dirty:178 files files=34 docs/index.html docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html docs/reviews/colchicine-postop-af/index.html ... base_resolution=merge-base origin/main pages=33 block_floor_refs=2304824034b4ba8677da2d2d2453352711ed2a9b,50f5a67b4fb19ada4716a0df6e6b68c2e4618304
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: not_assessed: base count 10, new count 6
        docs/reviews/esketamine-trd-madrs/index.html: declared_absent: base count 12, new count 11
        docs/reviews/probiotics-aad-prevention/index.html: not_assessed: base count 34, new count 24
        docs/index.html: lost banner block 2c1c3da7038bd131e062ff9854e52955fbfc9f879c8cda1c38a211b17e690ec9: Gate scorecard: plant validations and production refusals Adjudication coverage first, so the unresolved cannot disappea
  [             PASS] gate scorecard (every gate accounted for)  (1s)
        TARGET verify_all.limb_gate_scorecard: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:178 files files=3 registry/gate_scorecard.json docs/gate_scorecard.json harness/gate_scorecard.py
        TARGET gate_scorecard: head=3cf73885ffc83f6fcc4db273c6510a5416cdcde0 base=none tree=dirty:178 files files=6 registry/gate_scorecard.json docs/gate_scorecard.json scripts/verify_all.py ...
  [             PASS] gate gaps table (sealed what-it-would-not-stop rows)  (5s)
VERIFY-ALL: REFUSED -- 1 of 11 limbs not PASS. Fix the harness, never the gate.

```

## Second-pass review — MEASURED

Full verification result: **10 of 11 limbs PASS; honest-state ratchet REFUSED; exit 1**. No ratchet rules or acknowledgements were changed. The ratchet resolved its baseline to the older merge-base `2304824034b4ba8677da2d2d2453352711ed2a9b`, not the lane's `3cf73885` base. Its three review-marker refusals are already present at the lane base: balanced-crystalloids `not_assessed` is 6 → 6, esketamine `declared_absent` is 11 → 11, probiotics `not_assessed` is 24 → 24. The changed index gate-scorecard banner also triggers block preservation. The report preserves the actual refusal rather than claiming a green full gate or attributing all refusals to the new certificate block.

- All 32 review-core hashes equal the base; identifiers, dates, screening and statistical outputs are unchanged. Existing source-backed records supply the hashes; no scientific numeric claim was introduced.
- Every pre-existing `check_*` gate function is AST-identical to base. `check_certificate` is additive. The new gate has an explicit scorecard entry with no claimed adjudicated production events.
- All held-document references across the certificates are Git-tracked inputs. GLP-1 analysis-code blob IDs independently match `git hash-object`. Missing optional effect-type module and family map are explicitly NOT_PRESENT.
- The certificate uses exact held-file bytes and canonical JSON; JSON object key order/whitespace do not change canonical identities. A changed field with an unchanged claimed release hash is refused, including JSON true-versus-1 substitution.
- No membership, search, screening, cache, topic or protocol source edits. No staging and no commits. Saved certificates are working-tree artifacts, not newly committed objects.
- Final synth.py SHA-256: `fc1fa657fad5e5a88d0d7f290bf690287273e4304d69887377742889fd6dacc4`.

INFERRED: the certificate binds the listed held inputs and rendered manuscript to a release identity. It does not establish that the scientific claims are true or that the registration was prospective. CLAIMED: no deployment, independent validation, or publication readiness is claimed.

## GLP-1 certificate — verbatim

```json
{
  "schema_version": 1,
  "slug": "glp1-ra-mace-t2d",
  "protocol_sha": "b10c53d3783facb7e630219f0bb447fe6e22843e",
  "protocol_text_sha256": "d7208503c823d1b4f10fb8e356b69d30b3f25874420a8b678d25319811a7ae4c",
  "search_query_sha256": "9f52de6e7a980ca5e2fbf5fb546eb624b88d9502f8e6fee11cf5d89901b91e29",
  "retrieved_corpus_sha256": "1e0282f50c1503c213da9b4ec3a608ac22d639a17f8bffacc5c7474b43c1056e",
  "records_file_sha256": "1f575452770dd41d7a869da195ba681639360a8e4e17765fb407f92e272ce1d7",
  "retrieval_ledger_sha256": "086d3d2a49915105d185efb1b2b19131747af65bcf5ed0920edd1a6516a8294d",
  "screening_ledger_sha256": "5442bceaa544505a9813148c5a28e15b68ec0d4b1f88c1eb15a7ed7ea93dfd91",
  "extraction_objects_sha256": "8b5e7c2ca73e1178484f064f8640de1d7cf4d45c9f4997a90a5c9e48e7661279",
  "trial_family_map_sha256": "NOT_PRESENT",
  "rob_object_sha256": "9fa7cca178c82dbae7d8926d98d4d1fa7fb6d5204373c448c97120fd7bc5da23",
  "held_documents": [
    {
      "ref": "cache/glp1-ra-mace-t2d/aact_inputs.json",
      "sha256": "8aec1c466649588c71e7728572abefd8cc218c7303d6c6b0b6bef9e1b5e4ffd5"
    },
    {
      "ref": "cache/glp1-ra-mace-t2d/ft_27295427.txt",
      "sha256": "ded4c69e559446cef815ae8e2362600a39121c758bead7aefc9babd9f779f7db"
    },
    {
      "ref": "cache/glp1-ra-mace-t2d/ft_28910237.txt",
      "sha256": "9f474e106015e4baf4c65922739d6dc0075de967ee80e43665106db06ad01563"
    },
    {
      "ref": "outputs/handover/glp1_regulatory/208471Orig1s000MedR.pdf.txt",
      "sha256": "448150daf6667013259e6e4c741aba8a60153af651d5d04886455d3b8e595c22"
    },
    {
      "ref": "outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt",
      "sha256": "952b8088e14b457d97364f13bb0f9407803bf875faed5fa30d995972e2687a26"
    },
    {
      "ref": "outputs/handover/glp1_regulatory/fda_media_172242_ITCA650.pdf.txt",
      "sha256": "e27b9985959e139b9c84f15b7e364d3c82a2fed861819e2b777f6b3f5aef963e"
    },
    {
      "ref": "outputs/handover/glp1_regulatory/held/208471Orig1s000StatR.pdf",
      "sha256": "cf2b3ef92247b85e7be7c3b56c3cc4fc0af007b3950acee95eea9c995653db38"
    },
    {
      "ref": "outputs/handover/glp1_regulatory/held/fda_media_172242_ITCA650.pdf",
      "sha256": "719362393b2029c2d4a081ab1bc69647034b2168efe686808d419f16177f0103"
    },
    {
      "ref": "outputs/handover/glp1_regulatory/regulatory_sources_glp1.json",
      "sha256": "ff90e76642daa226977af17b22dfdd6a20a8d3e0d6a58fab5503073da6830811"
    }
  ],
  "config_sha256": "4682a204621b79916bea4ec8872b447500c5ef1350cfeef06f38269e7db04875",
  "analysis_code_sha256": "0682d01c7a2937ca82189130185448a39544c79d76d5a790de2f22ec2fccbeb4",
  "analysis_code_blobs": {
    "harness/synth.py": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
    "harness/pipeline.py": "e3e732635c43f0e27d3b0380966021c07cb208bd",
    "harness/grade.py": "d88f75ec0ba2043b5280ca8a76992dcbc369c78d",
    "harness/effect_type.py": "NOT_PRESENT",
    "scripts/build_topic.py": "bfd51ffd7d2d8c5296c501cade1a4f6bd19ef896"
  },
  "manuscript_sha256": "cbd10e8203d79337ce32992773b24571a8c6759c7eba7cd045bbaca74b994dd6",
  "review_sha256": "c51114c17077413cdd3aef2b430a751a07c6ad392164fd2ca2b3ce37df0403ca",
  "hash_inputs": {
    "protocol_sha": "registration/build anchor Git commit (SHA-1, not a SHA-256 or prospective-registration claim)",
    "protocol_text_sha256": "protocols/glp1-ra-mace-t2d.md UTF-8 text, universal newlines",
    "search_query_sha256": "canonical ordered [{source_id, query}] from retrieval_ledger.json; query strings verbatim",
    "retrieved_corpus_sha256": "canonical records.json['records']; equals retrieval_ledger.json snapshot.records_sha256",
    "records_file_sha256": "canonical entire cache/<slug>/records.json",
    "retrieval_ledger_sha256": "canonical entire retrieval_ledger.json (including any raw-index digest)",
    "screening_ledger_sha256": "canonical review.json['screening']",
    "extraction_objects_sha256": "canonical ref-to-JSON map: cache/glp1-ra-mace-t2d/verified_arms.json, cache/glp1-ra-mace-t2d/verified_effects.json",
    "trial_family_map_sha256": "cache/glp1-ra-mace-t2d/families.json canonical JSON, else NOT_PRESENT",
    "rob_object_sha256": "cache/glp1-ra-mace-t2d/rob2.json canonical JSON",
    "held_documents": "SHA-256 of exact file bytes at each bundle-relative ref; all topic ft_*.txt/aact_*.json plus referenced held documents and source-manifest PDF/text pairs",
    "config_sha256": "canonical topics/<slug>.json",
    "analysis_code_sha256": "canonical analysis_code_blobs map; values are Git SHA-1 blob identities of LF-normalized working source, optional missing file = NOT_PRESENT",
    "manuscript_sha256": "UTF-8 bytes of harness.manuscript.render(review), including its reproduction context",
    "review_sha256": "canonical review core (excludes reproduction)",
    "release_sha256": "canonical entire certificate excluding only release_sha256"
  },
  "release_sha256": "16a653da387345966014f01ba8174e0b1369c17e395d12ed8d2ec899591162e8"
}
```
