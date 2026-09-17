# LANE IN4 — integration and verification

**MEASURED: all 32 pages rebuilt and the full standard executed. The standard refuses; this is not a completed green landing. No check was weakened and no commit was made.**

MEASURED starting HEAD: `55b457f5b17f0959f3aa37d9ce6c6e29c45b678d`. No commit, staging, external network retrieval, push, or deployment. The session index/workbook were read and not edited; no submission/project status was promoted.

## Integration evidence

The requested `f6f7b14c..2f8705a8` binary delta was generated through Python subprocess bytes (avoiding PowerShell encoding damage), then applied with `git apply --3way`. The read-only real git index/object store was not changed: application used `.tmp/integration.index` and `.tmp/git-objects`, with the real object store as an alternate. Evidence: `.tmp/wip9.patch`, `.tmp/apply.log`, `.tmp/step1-conflicts.json`.

Before later-lane imports, **186 of 186 delta paths existed; 176 of 186 were byte-identical to `git show 2f8705a8:<path>`**. The 10 exceptions were measured by exact byte comparison in `.tmp/step1-byte-exceptions.json`. Changed-file counts were not used as the application gate.

| Byte exception | Landing-3 content retained | Incoming content / resolution |
|---|---|---|
| `cache/glp1-ra-mace-t2d/verified_effects.json` | Outcome-specific harm rows and typed refusals | Document-backed primary effects, merged by source and outcome |
| `docs/evidence/hm3-held-source-audit/aact/manifest.json` | Corrected LF table digests and encoding declaration | Obsolete CRLF digests superseded, not combined |
| `docs/evidence/override-audit-2026-09-14/overrides.json` | Entries absent from incoming audit | Merge on topic/file/trial/outcome |
| `harness/eligibility_chain.py` | `COMPAT_AXES` and compatibility findings | Topic identifier import and incoming logic |
| `harness/index.py` | Historical-only error-audit explanation and current-unrechecked count | Incoming provenance/index changes |
| `harness/manuscript.py` | Admission follow-up and endpoint evidence | Trial ID/label evidence |
| `harness/page.py` | `AACT_NOT_MEASURED` warning | Append declared strands without replacing the warning |
| `harness/pipeline.py` | Eligibility contract, outcome-specific verified inputs, source imports, cache-only build decorator | Typed-effect targets/coercions and declared strands |
| `harness/verify.py` | Spelled-integer normalization through nineteen | Incoming numeral matching |
| `tests/test_gate.py` | Deterministic harms-refusal plant | Incoming typed-effect plants |

The application produced 11 conflict paths; four were generated GLP-1 review files, resolved provisionally to incoming bytes and subsequently rebuilt. The other seven required source/evidence reconciliation. Three additional clean three-way merges account for the ten final byte exceptions above.

Later inputs were taken in the required order, from working-tree status inventories, excluding the specified runtime/prompt/temp paths. FIX1 and GS both have completed `tokens used` blocks followed by final responses. Neither was skipped.

| Lane | Accounted paths of eligible status paths | Evidence |
|---|---:|---|
| CGX4 | 13 of 13 | `.tmp/CGX4/inventory.json` |
| FIX1 | 23 of 23 | `.tmp/FIX1/inventory.json` |
| FNC | 190 of 190 | `.tmp/FNC/inventory.json` |
| GS | 244 of 244 | `.tmp/GS/inventory.json` |

The inspected attempt2 resolutions were reused; their exact file hashes are in `.tmp/reused-resolutions.json`. Their earlier results were not treated as current verification. Resolutions retain landing-3 absence-span validation, registered CGX4 prose, FNC family records, GS arithmetic/validation, and current typed risk prose. FNC `_report_keys` was ported into `harness/strands.py`; the deleted page-named module was not restored. Source IDs remain distinct from family IDs in publication/screening joins. The pipeline flattens dict/list verified effects by outcome, attaches actual family IDs, and persists recomputed statistical-layer cache objects.

## Integration defects reproduced and repaired

1. **Colchicine build refusal.** The exact reproduced refusal was:

```text
ValueError: CLAIM-OBJECT CONTRADICTION (build refused): a rendered surface asserts a significance opposite to the canonical claim object -> [{"outcome": "Postoperative atrial fibrillation", "surface": "outcome block", "canonical": "not significant (neither the HKSJ nor the common-effect interval excludes the null)", "found": "asserts significant / excludes null"}]
```

MEASURED cause: the typed-effect evidence table included an individual trial's quoted “significantly lower” statement in the pooled-significance surface. The canonical claim itself correctly derives from the primary result. Typed source tables now obey the existing `show_inputs` boundary, like the pre-existing verbatim trial-input table. The full page retains the quotation. The regression test confirms that an injected false pooled-significance assertion still refuses; the significance gate was not edited.

The held protocol differs from the prompt's historical k=4/k=1 expectation: its final amendment explicitly records compatibility k=3 versus strict k=0 after excluding open-label END-AF (PMID 27502857) under the retained design/masking rule. The rebuilt primary is k=3, RR 0.6509 [0.2063, 2.0538]; strict k=0 remains a sensitivity with no pooled result. Forcing k=4 would change the existing eligibility rule. No such change was made.

2. **PCSK9 envelope schema mismatch.** Initial build refused with `KeyError: 'strand'` in `harness/envelope.py`. Legacy supplementary strands use `id`; newer declared strands use `strand`. The envelope now accepts either actual identifier and fails closed when neither exists. A plant confirms an unsourced legacy member remains NOT_COMPUTABLE. PCSK9 subsequently rebuilt successfully.

3. **Retraction wording loss.** The first unchanged survival check reported `0 of 32`: typed prose had lost explicit `RETRACTED`, `is retracted`, and some search-withdrawal markers. The original claims were inspected in the base HTML. Reproduction and traceability withdrawals were restored in their typed renderers, historical integrity scope made explicit, and the manuscript retains the search withdrawal. No survival/ratchet checker or acknowledgement was changed.

4. **GS integration tests.** Its numerical positive control referred to its old k=8 primary and absent provenance. It now checks the actual seven-member primary, unchanged 1e-6 engine agreement, stored-page rounding, source-gated computability, and the seven-trial D3 denominator. The mutation plant now demonstrably changes the statistical-layer heading even when fragility is computable; both exact-render mismatch and injected unbound-sentence refusals remain required. The risk renderer exposes named unassessed domains for its HTTP contract.

## Prose migration and honest ratchet

The 12 CGX4 remainder units were inspected and the attempt2 explicit migration reused in `harness/integration_prose.py`. Limitations retain alternative formulations. Recorded ledger quantities remain recorded judgements, not newly verified FACTs. No arbitrary HTML/text ingestion, scanner whitelist, or gate exemption was added.

Unsupported wording removed includes the full AI-judged-win unit; “poolable unpublished data no published meta in this topic has”; and “No published meta-analysis reports an independent re-extraction of its own numbers.” The exact old units are appended in the completed report for integrator review. No ratchet acknowledgement was signed by this lane.

## Family preservation

MEASURED: `python scripts/verify_family_preservation.py --compare-dir C:/mh-r-FN` passed: **32 of 32 compact topic registries reconstructed exactly to the FN reference; 67,785 source-row references verified**. `docs/trial_family_preservation.json` records per-registry regenerated hashes. The compact files retain the fields the page renders; the offline regeneration script and altered-hash/snapshot/row/inline-value refusal tests remain in place.

## Static-versus-dynamic hardcode disclosure

| Static input/policy | Dynamic measurement | Limit |
|---|---|---|
| Prompt commit references and lane order | Git bytes, working-tree inventories, merge results | No count-equality substitution |
| Protocol and existing gate rules | Rebuilt membership, estimates, typed refusals | Expected prompt estimates were never assigned as outputs |
| Explicit limitation and alternative wording | Stored ledgers and source records | Interpretation is not new empirical evidence |
| Family reference schema | Held AACT rows, hashes, exact regeneration | No invented registry rows |
| Named statistical specifications | Source-gated pools and single-change sensitivity computations | One-axis-at-a-time scope; unheld values stay NOT_COMPUTABLE |
| FACT provenance contract | Held bytes, spans, hashes and metadata | Missing UTC retrieval metadata is not invented |

## Verification and finish condition

All 32 requested pages were rebuilt with `python scripts/build_topic.py <slug> --now 2026-09-11`. A transient Windows file-write error on metformin's blind page passed on one rerun; no code/data change was made for it. The ordered renderer sequence ran: render_fix_ledger, rewrite_fixstate_lines, build_evidence_index, render_gate_gaps, render_gate_scorecard, external_agreement, and `python -m harness.index docs`. Logs are in `.tmp/standard-final/`.

The complete standard was invoked as `python scripts/verify_all.py`, without limb filtering. The integrated script's optional slug argument is not used by this run. The synthesis engine, retraction-survival check and honest-state ratchet were not weakened. All external Python networking was blocked through the existing offline guard; loopback remains available for UI contracts.

Focused verification: **19 of 19 integration/strand/compaction tests passed**; **13 of 13 rebuilt GLP-1 FIX1/numerical/HTTP checks passed**. The full-suite result below supersedes any narrower PASS. The six early FIX1 failures all passed after the imported stale GLP-1 artifact was rebuilt. The superseded partial standard run is excluded. The full table below predates the bounded repairs documented at the end; it is not a claim that the final tree passed the full suite. The full suite was not repeated after those repairs.

### Complete standard run before the final bounded repairs — verbatim

```text
  [          REFUSED] unit tests (pytest tests/)  (1830s)
  [          REFUSED] offline reproduction (every live page replays from committed cache)  (145s)
  [COULD-NOT-EXECUTE] publication gate on every live review page  (167s)
  [             PASS] index currency (generated == committed docs/index.html)  (8s)
  [          REFUSED] served-artefact leak scan (docs/*.json)  (2s)
  [             PASS] held-out leak detector (registry/heldout_sealed.json)  (322s)
  [          REFUSED] search completeness (search_v2 measurement current; every state explicit; no zero from an exit code)  (2s)
  [             PASS] fix-state discipline (registry/fixes.json)  (60s)
  [          REFUSED] honest-state ratchet (no page may get quieter)  (13s)
  [          REFUSED] gate scorecard (every gate accounted for)  (1s)
  [             PASS] gate gaps table (sealed what-it-would-not-stop rows)  (4s)
VERIFY-ALL: REFUSED -- 7 of 11 limbs not PASS. Fix the harness, never the gate.
```

The full unabridged transcript, including every page refusal and test-summary line, is [verify_all.txt](.tmp/standard-final/verify_all.txt).

### Retraction survival — verbatim

```text
pages with every marking kept (count >= base): 32 of 32
```

### Ratchet output — verbatim

```text
  [          REFUSED] honest-state ratchet (no page may get quieter)  (13s)
        TARGET verify_all.limb_honest_ratchet: head=55b457f5b17f0959f3aa37d9ce6c6e29c45b678d base=none tree=dirty:646 files files=34 docs/index.html docs/ratchet_acknowledgements.json docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html ...
        TARGET honest_ratchet: head=55b457f5b17f0959f3aa37d9ce6c6e29c45b678d base=2304824034b4ba8677da2d2d2453352711ed2a9b tree=dirty:646 files files=34 docs/index.html docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html docs/reviews/colchicine-postop-af/index.html ... base_resolution=merge-base origin/main pages=33 block_floor_refs=2304824034b4ba8677da2d2d2453352711ed2a9b,50f5a67b4fb19ada4716a0df6e6b68c2e4618304
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: not_assessed: base count 10, new count 3
        docs/reviews/colchicine-postop-af/index.html: not_assessed: base count 10, new count 4
        docs/reviews/esketamine-trd-madrs/index.html: not_assessed: base count 6, new count 4
        docs/reviews/glp1-ra-mace-t2d/index.html: retrieval_class: base count 4, new count 2
        docs/reviews/iv-iron-hfref-hosp/index.html: not_assessed: base count 4, new count 3
        docs/reviews/melatonin-primary-insomnia-sol/index.html: not_assessed: base count 2, new count 1
        docs/reviews/probiotics-aad-prevention/index.html: not_assessed: base count 34, new count 24
        docs/reviews/semaglutide-obesity-mace/index.html: declared_absent: base count 5, new count 2
        docs/reviews/statins-primary-prevention-elderly/index.html: not_assessed: base count 4, new count 3
        docs/reviews/tranexamic-acid-pph/index.html: not_assessed: base count 2, new count 1
        docs/index.html: lost banner block b6f0ec4ee42a22f99043b2d7d326c38eae34e7e26e01545b2b91a66f891d3eb6: What this is A reproducible harness that builds meta-analyses from a committed protocol, and publishes each as a tabbed,
        docs/index.html: lost banner block f2b41f2edf033ecc02ec2067a325e375105a02d046a87022eff31c6db61cc53d: Every pooled number is verified against its source (gate-enforced) All 115 of 115 pooled trial-outcome numbers across th
        docs/index.html: lost banner block 14d82d4fda711fe9fe91721913d27f94c8af2fd442ab1832769897c57d897bbd: Parity with the published comparator (the finishing metric) For each same-scope topic: our pooled k vs the comparable co
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost banner block 983558e05e4bde77fc9f1394d2730329176e5f9c1a38a74fbd4a55e73f4d7b64: Snapshot: records_sha256 42df5c5c ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 004b373d6745c3bceae9513a9cf6a310bcc0136ae4b973c898d1a7355e062a4b: DECLARED ABSENT. DESIGN REFUSAL: after refusing reconstructed non-parallel designs without an explicit design adjustment
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 187218cede8a19de486ebe8f5ccbfbc4eb94a54238aae46662ee26a3cfd57155: Unit-of-analysis/design caveat (disclosed, not silently adjusted). 1 pooled trial(s) are individual-randomized factorial
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 52cd04e3a915bdf5778422eb031e9852886b3c694807455f9b05173937be4eb6: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 2c19afc5ad0d30515b877f866f1642b96a8121d5e7bad11f30471f93c7ee7ba9: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block f85a78807d31d85343a73c78d55902375bf1265142747d58d473e433855e41b4: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 7d49f76d89a220055f1ad2c49e47c1e9533f5eeb0458e5ccb74126a0080713a6: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/colchicine-postop-af/index.html: lost banner block 67757344ee670d1fcf41cf97cb423c0106fadab6c8cbeb3fca2968bdc4906419: Snapshot: records_sha256 474eff90 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/colchicine-postop-af/index.html: lost absent block c05a643044807856d475f2cbb9760c9bec2c21afb0d8bc0b755ef3e4ed55acef: HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH We retract any claim of a registr
        docs/reviews/colchicine-postop-af/index.html: lost absent block 09bdb49b28d751b80a19a5156efc48af5a3d03b86e50c38f917ab02f3c739977: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/colchicine-postop-af/index.html: lost absent block c37a2ca56df8e47967377077be78ba1eb29ac6e9bb6d885d60e2ccb5bf4f13a2: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 32720823, 25172965, 27502857 mention this outcome in th
        docs/reviews/colchicine-postop-af/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/colchicine-postop-af/index.html: lost absent block 9b1884cdd73a6a0f9056e82edd34706a8f1982b178287effdf441da7649bbf9e: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/colchicine-postop-af/index.html: lost absent block c6f55d3c41f28551439f475dcc2443401b255683274ce3f5a9decaf1af143876: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/colchicine-postop-af/index.html: lost absent block c3dab676c7cc4c4ed7c1430bc1f86f0463968a9ec0d1c2af796b6433c250b494: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/colchicine-postop-af/index.html: lost absent block 8dfc2f4ddd13b517cfa67ebda9a6a3790c8a1fea50c7298b85e933bf628f1531: Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a 
        docs/reviews/colchicine-postop-af/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/colchicine-postop-af/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost banner block cb451432c3ac88913aa5c78c93cb9a26e55e78e46ea019031e32740e2d51e33f: Snapshot: records_sha256 570a1143 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block c05a643044807856d475f2cbb9760c9bec2c21afb0d8bc0b755ef3e4ed55acef: HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH We retract any claim of a registr
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 09bdb49b28d751b80a19a5156efc48af5a3d03b86e50c38f917ab02f3c739977: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 35058ebae3177e56f4a895db383c9b55873db12d137ac96aee2284d7619ddabb: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 24694983, 23992557, 21873705 mention this outcome in th
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 90d0d6414efc79f07b43707db054bcefac42ac266537d38d442fc53fb0773481: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block ca87b29f09498e773e1db7567bea84ec257efbd15950522c003e127d73e1d04a: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block d581286a505b55582c586d2d6eab2fb7c1fff552d507c802bb801d50765ab395: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 275b80a153f01f0d7930a7adecfb86ba9b0eee0b0a7cd982a26748a3c8ac4f41: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost banner block 9c45871f77ef0834e639a21ece88d52b77c3763fbeed9748b6aaba8d9a8127a6: Snapshot: records_sha256 2d3b2a35 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 79e8530721620a41dd9245d709864502413f259d5443c1347b5939ae65fa0292: Unit-of-analysis/design caveat (disclosed, not silently adjusted). 1 pooled trial(s) are individual-randomized factorial
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 2f35820b0771882ce825e008c91720427f3067b3757140fa18acd821b341b27b: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block f640e854cfd1e10d0a39cfad5f14c70825f998fef6c8ee76251e10eeee8d2e7e: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 57205a3c80284c1aeff24226ff5968fc5934014af55e2b4724303c7a4e83c3af: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block a54ecd524eced807f0962ba546cc1fda3db13f551f886144467a6f2ea0d59259: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/corticosteroids-cap-mortality/index.html: lost banner block 5b90e3f99e5cf7684a31cc3f874cf7bde5f31e413a1fd13ece8f1878718a0ca8: Snapshot: records_sha256 b8a5cc47 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block c05a643044807856d475f2cbb9760c9bec2c21afb0d8bc0b755ef3e4ed55acef: HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH We retract any claim of a registr
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block acb80753fadc32acfe3f94ec93708a4f5dee73845e867d7b3965c10e2eddd08c: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RU
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block af1be9f121930cc61ce27b462dd1d544ef8632b057ea2e5143bda3d9514ecf30: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 36942789 mention this outcome in the committed abstract
        docs/reviews/corticosteroids-cap-mortality/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 3d1c9ccfea5434242443d86ca404fbfe5d536dd2daffe26d0e761f2e22b8cc6d: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 09ed6ae25a015e0d8fa49dc6bbc1d5eaec199132b9199b61233147e1ef2af751: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 0f41b767cdeb7f3ac49137913e0bed645a03257d18decfe627336a69244089a4: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 16a31a620c341edc50358ed3a3849f254b021b872920a6a62340b100b4844dff: Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a 
        docs/reviews/corticosteroids-cap-mortality/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost banner block 7fc5fbe2329e78b3b2f54b921ebeca0bdf21436b44540ef7bf8e6be658cfd276: Snapshot: records_sha256 78f98d29 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 45bb4635fe128500a1ea7b4425bebd42c1abc364f092a64f7256b064807fe3be: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 34138478 mention this outcome in the committed abstract
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 654a8891121ff1083f93b4a07709fc795f187efc842043c4a52afc19586e34b6: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 3f98507b0cda3348baedbf46363de3908b89e1c5d408b2a0f35ef63fb04ffa14: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 460814ddc2ea0b454e2cc59e9a1ddbc97261099c24c7c68b7000dd33fc92a91d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block f11df83d8cdcdf214dcb3553d8907cc6b8122266f3c059c96f4b9c6d1c37ee9a: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost banner block daeb0ac407986902bd35c7ba1addbede483d6e9ef071486d0515468f507fc9d2: Snapshot: records_sha256 91f71997 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 727f47affcd9fbb34f44495c3052b8fe9f36966fcc90f141f6a9d9000cbc3e47: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 51e3022be2a1b8158448c09e50f13e9a095573c315136cb19b22b6400b97028d: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block c2bcf0acd104ff21660b73692747af61dbce3defbf18f5b3c80e1517ca389639: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 78460b7fd842a6407ad20cbdb5d6c465db843d3322956bee461b6900e54a2c20: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/denosumab-vertebral-fracture/index.html: lost banner block 44f777950850cb0d700b1cdd8100689bfd9839e9e43d815d18947aa079767dcc: Snapshot: records_sha256 32165834 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block f1b0d7b429050cfec3a688bdb1df0579012084709efdc927e62da0888bd6fca4: DECLARED ABSENT. no included trial reported this outcome with a percentage-corroborated count or an effect+CI in its abs
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block dbbbd408ec262767dde20079bb7b4a012975f768bb21d8062298b136d4f3eb59: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 19671655 mention this outcome in the committed abstract
        docs/reviews/denosumab-vertebral-fracture/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block 01bcc626a75fd06d2d919c298b41dd968bcb0cf78e30a345fb12d69dad59c5e5: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block ab51bd420fb4b28762145e7f3ea285673ca016cbec97b409d54b532925a03a36: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block cdf08119611dfcdf4ec945d9bea4e527ef45935a09f48e359cb9a83311f74e12: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block ecc8ed947c95752e72c0a6cab09514ec7c5a34cdfc2717544a6d9011a28156f3: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
        docs/reviews/denosumab-vertebral-fracture/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/doac-vte-recurrence/index.html: lost banner block 410b0ec6430a9737f71d7faa044221a0bd71653fc1aec9ddfd09f1aad7d0bda1: Snapshot: records_sha256 ef5c1c6b ; retrieved_utc 2026-09-12; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/doac-vte-recurrence/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/doac-vte-recurrence/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/doac-vte-recurrence/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
        docs/reviews/doac-vte-recurrence/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/doac-vte-recurrence/index.html: lost absent block c7f018104f5e77d148ef76b22779d0fc51ae5c32eab1c6266773a42c9e0c5ed7: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/doac-vte-recurrence/index.html: lost absent block d6cdc1b8f2806a8da5ff7e7b5fc45b009b2766c6ef431196a2cf408055a887fb: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/doac-vte-recurrence/index.html: lost absent block da01b6ba519d765f1f7085f7413af2667584916e67a43fd872d8f391a72c3f51: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/doac-vte-recurrence/index.html: lost absent block ac057cdbffb6d6ed529764ed96d02c9bdf085df5d37d7c6dd7ccb84bffb0c38c: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/doac-vte-recurrence/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/doac-vte-recurrence/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/dpp4-mace-t2d/index.html: lost banner block e29da437f91714ae26b2d5f0da715141a26ce67145fa4817cdf7036eb0a353f4: Snapshot: records_sha256 81256a4a ; retrieved_utc 2026-09-12; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
        docs/reviews/dpp4-mace-t2d/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 66d6d9cbc227d9a699cdf986265b2b7c04a066c4b01de1cc8e8e380e0282a071: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 80050dda0a27c639679fbcbb44ad5c7a74c4ca8ac59d189adaf5c8c3756d86b0: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 91ec4628b63b3e86d9c7d2f143975fdc54e4c8782edea24d1fdb19b3fb96c48e: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 6fd4fe1fa9d7c27b9dae78df1aa0508709049363a38be5e9069ba7005c2476a2: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/dpp4-mace-t2d/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/dpp4-mace-t2d/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost banner block 303b53251c8bad5d3da89eeaf6b9f6db72c408f70f6e3677adf1edd3403438d5: Snapshot: records_sha256 5ef3f171 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block ecdd529cdb73661a1dc8534de5961bd2c81af1f89d690027dc9ff886a5ba6edf: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block dd19678a5c1c87e7219abc7156beab32777aa31eb791b6ed4e2ce0e301c8acce: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block 90d9054f250f3f8c546865b94358f617dfe8d76608f9e5870ebc508f90c91590: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block 6b24891820614ead5920ab05217a096376de6f5eb595bc20bfa5e723ed576f82: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/esketamine-trd-madrs/index.html: lost banner block 5db3239db27b959c8a192465d36e1f3a88a928fd9365d0c5e4934a9328852cda: Snapshot: records_sha256 a09370ee ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 51984e7bede57d9bf3873159b06be81aa191c14d5289e9eb38532fa57bca1e01: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_ER
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 4554b38e12246adb7ec988f9bb194fe41e7ef3abdf7fe3db1e2c31bfc5621cc9: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 34696742, 31109201 mention this outcome in the committe
        docs/reviews/esketamine-trd-madrs/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 4c29b75436df70dfc57dde8e4c0b7975089c3303c76a5d93c7c5d95c4e231a5c: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 17c77c145420770141d32fd0d8156b182d450fd35b6287a5cf9b40e2aba0c827: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 7058b2699c4ee2d0f8489f2cd13f365fa05dcf95e49011617b8ecdca765369fd: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 7a1b2f9d0aa30150320bb235576d215f3bc335d0d9a1f07ccb06f24c2efac169: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/esketamine-trd-madrs/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/esketamine-trd-madrs/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost banner block 5be8b8344e22c6ce007c14827eb881142fd7c71a84282cbd3ba30f865639a7fc: Snapshot: records_sha256 4e838bbb ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 63c17a3b1a6ff026e3216b53bd3c6078e2df601534271776decdd9f03b2480f6: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 33264825, 34449181, 26325557 mention this outcome in th
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block e9b6c91404265dda6919cfe2280db8b34008d4f2ef350e80418e013bd2ccac3d: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 48baaf8c4c6a15bff29b9fe93538aeb4badbc9faaee9c82198b417b94ba1138c: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block cdd5838e9ddf4722e73df01da34e5b8d82b6da2209bfc80e58b07b824f91f06d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 2f96569c95ff0621bf07097dce733e6e727a8f2aa663c83fbc36d42a2ae93a58: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 0606da3be98c8d40045f716df24fd8af88b2ce8b7b3f56953420acfc386da74e: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 4a266aa0f9d335743a4f9107c0fc651306d41303071fe7cabdf23eb83387b40e: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/glp1-ra-mace-t2d/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
        docs/reviews/glp1-ra-mace-t2d/index.html: lost banner block 1c7e24dd1b2e31a6b2c42983b46322e0b978064c7e0f1784f628645f6bce823a: Snapshot: records_sha256 1e0282f5 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block f78c512047bc0437de0926a52df7805b797214433f9feb56344ab2c29eb00219: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block f3641fa7e56d8d396bc0f8e0e7938987d10f402964ce66d602c13133ff3df1fd: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 31185157, 27295427, 34215025 mention this outcome in th
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 181eb2cc7da5cb8589a7ebe140194b85594aa6dbd6f5994ce6e9d7f982d8e2b8: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 31185157, 27633186, 27295427, 30291013 mention this out
        docs/reviews/glp1-ra-mace-t2d/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 3b5fcb2c43c291d46f0928d1f6dd4f574eb1adc1d212f1113207d41844af8c41: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block ade5009855456019293990bec265c1e0ddea1fda4d155316b7f6728b27fef7eb: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 118737e7052fbdd570b2bb1df218c74b838fe181282b54f53fae236363d15295: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 04a2e41c88e8930b16c4783a824d69b3411af2e0f716308888eb7504faec9d34: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/glp1-ra-mace-t2d/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/iv-iron-hfref-hosp/index.html: lost banner block 922bc57e32d805488dc7cc0e69b76a126750ace0f40a98d4af5c58eae3e15e83: Snapshot: records_sha256 242ba998 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 31c8e387bf859660214caa9bf45f71bca44e80baed46a0320cd5420051ff48de: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RU
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block f1b0d7b429050cfec3a688bdb1df0579012084709efdc927e62da0888bd6fca4: DECLARED ABSENT. no included trial reported this outcome with a percentage-corroborated count or an effect+CI in its abs
        docs/reviews/iv-iron-hfref-hosp/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block e33d3ad545e807ab7ed52a5479a3bf8255f04c8ae05e898287e51cddca0953aa: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 95985cd84fbf919935f5099fffc4c42de010543b74fc4555a113a263a177c7ec: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 19e48f45872f041e87da3e5d30365a431e76d3d07e43ea7a5ab24ab068b59b73: Overall certainty: not rateable. the primary pool mixes INCOMPATIBLE estimand classes (HAZARD_RATIO_FIRST_EVENT + INCIDE
        docs/reviews/iv-iron-hfref-hosp/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost banner block d133296791325516a27f5024c7c6b57db9a7aeabb5bd79cdec0dd93fb46af616: Snapshot: records_sha256 159e5415 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 51984e7bede57d9bf3873159b06be81aa191c14d5289e9eb38532fa57bca1e01: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_ER
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block a16a18bef1a7af5809468fe78f126b2a3dd5d4385f5b503bf9976f62ef5f26da: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 33157425, 22346363, 20712869, 18036082, 12790159 mentio
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block cbbd6a73cc0d27b1e77534aa7ff16ad6424ee9b025379a7f32e29e17c50bbbda: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 4972766020294b0566a4fc26feccd2e0da568e0e677638429fac1ac3d4a63d6b: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 7b4225b798a5ed89e4d0e8a324f0b622166dcaac88512b73d4dfc3f114f60faf: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 6b77e526173bc21f8c36fc9bb3eeea0c9902d81540ad387fc201c38cb209a983: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/metformin-pcos-ovulation/index.html: lost banner block ef76770b0dd933fd73a963b6c0d2cf74b9a72b663ff9445df51dce532cc247ce: Snapshot: records_sha256 1fdb53f8 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 31c8e387bf859660214caa9bf45f71bca44e80baed46a0320cd5420051ff48de: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RU
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block dd1dead6c2560a93ff01a5324a76c288e758fc97cb2a645c790180163e821248: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 16769748 mention this outcome in the committed abstract
        docs/reviews/metformin-pcos-ovulation/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 6ee988ab9970f78e22c815d201785b6d167c938e6e699da61186de8cacfd6312: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 16264cc27213b813e1aeafd53e66948603ccb01474997893fe6c53f1a37a022e: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 72db58add18abd2662f0e8b4798ff2ee589a750ad3328d91563734f69747b695: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 8e8301343df98222cfe40b761ee7ec58afc1206c5534fee72f5d709f163834e3: Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a 
        docs/reviews/metformin-pcos-ovulation/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost banner block cb663900acaec0589ce8453f2f0fab07a582c6aacb8ccbdf4e5ed2be47c4eebb: Snapshot: records_sha256 dfacf3bf ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block f78c512047bc0437de0926a52df7805b797214433f9feb56344ab2c29eb00219: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block b0828b821327892706ca39221ca0550a0b0043e8506a2868c6223cd5999b8503: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block e265d763c956988c33d33de18e544f09e182e98528af44246fb987cc65a5c2dc: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block 496a7c240788f4917387ccc389f17c25551a2842b80391e40c0a7353dfcd57b3: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block baea49ebb9e814194adc1b2736d663afc71255af1fa6cccb8d6d0d1589f72307: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/omega3-cardiovascular-events/index.html: lost banner block c1c5b55299c91132cf6c146defaa2d13962b48c20880d790b36bc8c4360d0823: Snapshot: records_sha256 f40d3169 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 7d2411912d3b55496a33fe9a0905f6480d10aec4d43fb37141f183cb736add53: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 30415637, 30415628, 30146932 mention this outcome in th
        docs/reviews/omega3-cardiovascular-events/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 2e52a207b30781148639e2ca6263bbfc5ea5d11d8d7ca9655303821d3b52ddfe: Unit-of-analysis/design caveat (disclosed, not silently adjusted). 3 pooled trial(s) are individual-randomized factorial
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 4bfa9e524f3089c4c5cd06a844cdae1489c43898c25d569c14d17005e0dc3af1: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block fc29991097b4dc217d3f023445f76cbffa5c22b6bf494127a23f390975d8369c: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 6398132dae3a1a7108a74c25d54c80f3a739512df47772bc155502751c36b41d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block c77ef0e830e5d74310099c90ef651caad9e1ee2aff8dd7d8de391e991afc6962: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/omega3-cardiovascular-events/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/pcsk9-mace/index.html: lost banner block c05e20e7a9b7ea8d4b39012a216008d917651e6080af654d0d819c92e96864a8: Snapshot: records_sha256 b1ef6c11 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/pcsk9-mace/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/pcsk9-mace/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/pcsk9-mace/index.html: lost absent block 61163e4e61d3b0c8976d05a3c2402af897356d709003c3ea8a7b34991e38813e: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 28304224, 30403574 mention this outcome in the committe
        docs/reviews/pcsk9-mace/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/pcsk9-mace/index.html: lost absent block d045eb82cc2e52801ad1f457995308936bee1d9e633f4b9709cdc1787504729b: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/pcsk9-mace/index.html: lost absent block cdae34e1a6433db309ca24da20a1250284f651795828d207d569bccb725d3390: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/pcsk9-mace/index.html: lost absent block 7b2d1674478f8315cbef7e6285dad3f45e0a93bc14acce314da847954a6bcbb9: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/pcsk9-mace/index.html: lost absent block 9fb655c4cc64424164f8dee8b10bed1f52ddf44da88fa836084f5ea54e5ed034: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/pcsk9-mace/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/pcsk9-mace/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/probiotics-aad-prevention/index.html: lost banner block 6f6f96af69410d2951ffc9c54eb72005a31d84db761045cdf01c8b315b1f9e51: Snapshot: records_sha256 a832babc ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block c05a643044807856d475f2cbb9760c9bec2c21afb0d8bc0b755ef3e4ed55acef: HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH We retract any claim of a registr
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 09bdb49b28d751b80a19a5156efc48af5a3d03b86e50c38f917ab02f3c739977: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 34a8823b0bad217626b851828dc856654dbbae42bf5964fcb712262cb30490a3: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 42608299, 41699149, 40716758, 40548185, 40488914, 39935
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 6ecb01b65a6288b3037ae6e2f1019cda43b2ae320ca660365fa61d46a93210f5: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 40548185, 26973849, 23932219, 19138244 mention this out
        docs/reviews/probiotics-aad-prevention/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block fe5a5a96506acf422872e59e045b9257d911a403ba1f6876ea2e418cab3cc71d: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 4b252317efdebe6963ef01a013fe5eb43646c12497849c9063636b005ef2cfc9: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 3690b1ad41faf51a261928ebca1cf523e09cb400f4cc759e307d156697580e8b: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 99becb418875e3d7ddd6dbda49c73006d7252e22eef6dc35199ff53c62376365: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/probiotics-aad-prevention/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/probiotics-aad-prevention/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost banner block c9570bd907f9397433ca1c5632a5f1da74fb5e63c24a3c44c2ae34995363a023: Snapshot: records_sha256 58f1709c ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 31c8e387bf859660214caa9bf45f71bca44e80baed46a0320cd5420051ff48de: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RU
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block bff5f3115693b0718df1df746a4fe566271c472ab11819b1fc25688a085945b4: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 7f05f40e226c430ba2d04aeaa23acc772e6f906aa65d61f5f2e75d2e9450aae4: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 072a75e8e15be99b57cc84e267fcc385e25589124b7fc7b60d3203a4a6083bbf: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 09ed94fe6e8360cfecf6ad69db79fcb7ca77b505565936768935dc6b62adcb67: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/semaglutide-obesity-mace/index.html: lost banner block c277dc7a9439b0e4d0bd6b1430ab5c6dfa3209e7bf1bc676437ba5728f0a9c6e: Snapshot: records_sha256 ac910156 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block f1b0d7b429050cfec3a688bdb1df0579012084709efdc927e62da0888bd6fca4: DECLARED ABSENT. no included trial reported this outcome with a percentage-corroborated count or an effect+CI in its abs
        docs/reviews/semaglutide-obesity-mace/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 36f1272cbafe5ab6d098d3764690890c7867b73c4376e443fc505ff44cfb3af2: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 08680a96bfa69c446138ef1efe16db7a39a864723beb64f70be4bdb32978fb19: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 26ab09f2b6cbce2e1e158fb630fa57a0c0186f3db7491523f7fa2adf79d4fcbc: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 3fe49f850a635eb2189b79baa4f679f142e19bce8eacd03224e40f2a3feee68c: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/semaglutide-obesity-mace/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/semaglutide-obesity-weight/index.html: lost banner block 32d0ad299559b616aeb37b8f28c79e07e42eec3c0e395336073c09c51961c98c: Snapshot: records_sha256 195d48c1 ; retrieved_utc 2026-09-12; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 51984e7bede57d9bf3873159b06be81aa191c14d5289e9eb38532fa57bca1e01: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_ER
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 7d054e36a29c628d0807fc18fe5eb817c1df0f3006068c0564e198eadb2d52d0: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 42575111, 42070571, 40825340, 40629530, 40069849, 33625
        docs/reviews/semaglutide-obesity-weight/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block f8a5707ab64fbc8f436f190921d8e79e893e813b8ba9921fb19fcc5f136c4238: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 0b94e470e01c548721077e31502ffec1a5fe3b47eedc2f8626b46dfe78d46835: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 45446b368a9c9346efd1ba26dd96de014ee501bb6caa900c82360c75634ad0af: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 0f8ad79d9c66fae246cde2257ffe2107813ab8e139bc575a8052b607ce492c12: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/semaglutide-obesity-weight/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/sglt2-ckd-progression/index.html: lost banner block 24e1177446fd6c46b8db81088cbbf589701abd7ebab1e6527117586423b11213: Snapshot: records_sha256 4a7478c2 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block 7f784e67f837798409405c149567f7c89159a67591406edeadbd6edec156d5f2: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 30990260 mention this outcome in the committed abstract
        docs/reviews/sglt2-ckd-progression/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block 40092b16403db4c15aa693020e60b837701335ea440baef9f774b981fd620cd1: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block 0320760e6bcdb6581320126e7dee63b5506c7a8c25303f9f617e514acc4f2ea3: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block eb69309ac2fbd67743b0ded82a6daaa5e7316e38145aaa3f3a29d30223c4c4fc: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block db4655aa165a114b729706357dc701b5b8bcd0a7e9d9d21aa8ff9d9cd969266b: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/sglt2-ckd-progression/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/sglt2-ckd-progression/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost banner block c2e448a7a5ee87b14750d6172d418143869d71d8d2f7568e059605593ec9de12: Snapshot: records_sha256 056f66b4 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block c839630e932144f699429abbe2e861a0bd987344d8372c0a5b2ce106b59be677: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 31535829 mention this outcome in the committed abstract
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block 2565ad7a1e882c7ccf2a45c20448223b484335ea10a53179b9a43dd950dded83: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block 1e64c354919293b51d17319223237128f234c225cc3762b3b91f859a4f21a893: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block 965250ce4cfd0308b296c784661c49b482f248ddcf01136bde7f1c17d3e77525: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block be6ab27c20f82912a45e9cbf09be8802e97350ee49be185e8851e97a2440fe15: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost banner block b4d94a4d81dddc0e854ad5f61d850d781bf6f664a87fa4c217d60927dc72e105: Snapshot: records_sha256 ba5c49e2 ; retrieved_utc 2026-09-12; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block 1dbb0dc87beac85c77ac53fc9f52406d3eddd62cb4ccfc74ca034f7b0ed71e21: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block bc8f2f2191b9b07735e8a5c8399a6fa9d72f51df88021e62676d49dc665aea26: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block 8d61bf47c06063dec14f2d4656e683b5c5445128098b53a4545d6f790bf52db7: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block a88aa38b82f42e250de2a7b237f6026ce62106c4c5a06c14521eef07aba1cf69: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/spironolactone-hfref-mortality/index.html: lost banner block ed7a148966f33ebbf44e717e74b3bb5cba442fd27698ceb915ae71b46dba2971: Snapshot: records_sha256 8352ca95 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block ec9fd7c4d2ac80fd976612d3b03f8ffdcb61d1f46cb8375d2f3bd6c7cff3ae4b: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 10471456, 21073363, 28824029 mention this outcome in th
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 8124911ae094726bb85f9fe8d1f2efb2a69ffccc1951b6caa3e030a638175182: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 10471456 mention this outcome in the committed abstract
        docs/reviews/spironolactone-hfref-mortality/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 6fb533d581f68da392afcc89bcaf1ec0b6f1ebdcb59a421d831aebae1c466f92: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 1557cc75bdd3c3e88e8efdcdfc7172ccce312164d8db9240c5a5240b75bdf0e5: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 4bfc6a1f39b6524082d059f894fe1d3440e3725de7a19ed581edc014ad0c276d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block a20410a071d279f8c5f0d4f2524c309a86be39ca53864329abebb24238d6d882: Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a 
        docs/reviews/spironolactone-hfref-mortality/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/statins-primary-prevention-elderly/index.html: lost banner block dff1b4824f648a4dda451026e0025d13c2be7fdb2712006ca3ebead3d3f35927: Snapshot: records_sha256 7170920d ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 7c17773d7ee68a33cf2378a420020f88a59523b40af38f32bd6b4e6cda18f6d1: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 42670961 mention this outcome in the committed abstract
        docs/reviews/statins-primary-prevention-elderly/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block c04bac3cfdc3fac6d7b3272a1dd7a2929d8447bc1a0852c2a38da02eeba7dd5b: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 25845d7b8f6c2c99a73579fec6eb96610e926af016e6fb5374d54b0bafa09bc5: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 1b61824a331cba7ed7af28c78c2e1e32f08a54957ed61b788a77d0ea6495dbb8: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block e49ac2b8042d3c0330eac88d67e2accc7128131e64a79ea69ad81323e3b054d1: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/statins-primary-prevention-elderly/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost banner block 831ac718dba9f4b8248b7d0fe1f68b0955dc8380906cf4beb71a6eb2827a7da9: Snapshot: records_sha256 a6e860ba ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block f78c512047bc0437de0926a52df7805b797214433f9feb56344ab2c29eb00219: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block f1b0d7b429050cfec3a688bdb1df0579012084709efdc927e62da0888bd6fca4: DECLARED ABSENT. no included trial reported this outcome with a percentage-corroborated count or an effect+CI in its abs
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block 1df51e83141f9980943f1060bc10a23ed3c4fe9cc765c409f42475d6a7e50a63: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block 4b332ea83fea8621ad8f08b843ffcfb5a6456a1539827fc5f4700d9e4ea2df4f: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block 35299e230bcbee6aee55bf7259d56deae3c7966fbcf86977f1661a0a378cc2a9: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block c3fd688cd9c199c13ff366e0812df59617cd1cd51a0c62f409f3ee3598b7f98e: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost banner block bfb757f80a5cfe9a8887c7540779e13369f2d30064eb08389752ec46201c6afc: Snapshot: records_sha256 a6b727dd ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block f1b0d7b429050cfec3a688bdb1df0579012084709efdc927e62da0888bd6fca4: DECLARED ABSENT. no included trial reported this outcome with a percentage-corroborated count or an effect+CI in its abs
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block bd14f8a89b0544ae6a4315d2ae4bcbae9a47bcb4256ae8696a27d2332454058b: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block 20c3e04e68c4397a8e7994d28ed9034c4a2360a8397263fa23fc49d9c04c35f2: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block f16e90d7d6310cdb9d636170fa9b5160948b9ed4d0d5fc380801531bb72dc82d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block f5fafd4d2f6b2c4d7c6cd44bed380029eed96d2f06707b0b8321289ed32b242c: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/tranexamic-acid-pph/index.html: lost banner block 65e66ffb5fccf2333acbe2451d28a7cb4da497e3f13c3a1d38e564a90ba9d69b: Snapshot: records_sha256 940022e2 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block f425710ed75286f7ad4624bb8b617912fb9609feda3e5da59b90fa0e879c3f91: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 32143721, 28456509 mention this outcome in the committe
        docs/reviews/tranexamic-acid-pph/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block 715b9f50c00c6b3491cb174de95bd3713812364b2d43a2da906264dbac4e63a9: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block d161053ef44d71264c34d6d71613938e2fd0828724e11a79add0d67ab150174f: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block 295a768c15eeb1c46a8cda92832439fa2eb6fb6b500a8f11b2b737f4f9b6bc0d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block ac7d9964082a37db27b76419258d0d324859f0857bdc0357035d21ff2c999a37: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
        docs/reviews/tranexamic-acid-pph/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
        docs/reviews/tranexamic-acid-pph/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 3056ab225b9e210a00936fdcbfa361f8e934c4a3eae8501e77e4dce9dedb702c: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block b8c4b60bd942a25aaaafc43a4cc63dc78c3e705961e0fbf0a49155bf75bfe08b: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
        docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 960be40ef77ff4a78df7696b5504db234eb1f8d843aa2fd6152fed50e4fd2b0d: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
        docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 74ef9f624c5845659feef24079fb873482531098515959d4a9a1c20473b27570: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
```

No integrator signature or acknowledgement was supplied by this lane.

### Full-suite failure summary — verbatim

```text
TARGET verify_all: head=55b457f5b17f0959f3aa37d9ce6c6e29c45b678d base=none tree=dirty:645 files files=1 scripts/verify_all.py
VERIFY-ALL: 11 limbs, all run, fail-closed. root=C:\mh-r-IN4
  [          REFUSED] unit tests (pytest tests/)  (1830s)
        TARGET verify_all.limb_unit_tests: head=55b457f5b17f0959f3aa37d9ce6c6e29c45b678d base=none tree=dirty:645 files files=166 tests/test_aact_cache.py tests/test_aact_recurrent_guard.py tests/test_absence_ontology.py ...
        FAILED tests/test_hm3_pages.py::test_rebuilt_pages_account_for_every_baseline_harm
        FAILED tests/test_hm3_pages.py::test_primary_trial_values_and_membership_are_unchanged
        FAILED tests/test_in3_contract.py::test_typed_harm_incompatibility_resolves_debt_only_with_valid_span
        FAILED tests/test_in3_ui.py::test_in3_pages_render_resolved_harms_scope_and_offline_integrity
        FAILED tests/test_leakscan.py::test_shipped_corpus_has_no_suppressed_leak - A...
        FAILED tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews
        FAILED tests/test_membership_consistency.py::test_rebuilt_esketamine_membership_is_consistent_and_parity_row_current
        FAILED tests/test_override_audit.py::test_override_audit_covers_every_committed_override
        FAILED tests/test_page_claims.py::test_owned_sections_have_no_unregistered_or_mismatched_units
        FAILED tests/test_page_claims.py::test_canonical_json_key_order_does_not_change_html
        FAILED tests/test_pm_merge.py::test_migrated_overview_keeps_limitations_and_all_boundary_objects
        FAILED tests/test_retrieval_render.py::test_enumeration_only_block_only_for_all_enumeration_sources
        FAILED tests/test_rob_sensitivity_predicate.py::test_postfix_rebuilt_pages_satisfy_relation_predicate
        FAILED tests/test_stage_additions.py::test_error_rate_is_fresh_against_current_pooled_population
        26 failed, 1048 passed in 1827.35s (0:30:27)
```

## Remaining fail-closed refusals

The stricter FACT/prose gates from CGX are live on every page. The requested protocol-binding behavior also remains live: legacy rows can retain an UNVERIFIED_FACT mark and pool where no binding axes are declared. That build behavior does **not** satisfy the independent publication FACT gate. Making those pages PASS by exempting legacy rows, suppressing unresolved harm reporting, or classifying arbitrary unregistered prose as structural would weaken checks. No such change was made.

The source review found only date-level `2026-09-11` retrieval metadata for the relevant legacy harm inputs in `records.json` and `retrieval_ledger.json`; an exact UTC retrieval instant was not fabricated. Provenance recovery and full typed-prose migration remain incomplete. In particular, the family/statistical-layer prose registry debt is acknowledged as integration debt; it is not called an upstream PASS or hidden by a coverage exception.

Representative verbatim unchanged gate refusals:

```text
L1: UNVERIFIED_FACT PMID 31189511 in 'Gastrointestinal adverse events': missing retrieved_utc in UTC
L1: UNVERIFIED_FACT PMID 27295427 in 'Adverse events leading to discontinuation': missing retrieved_utc in UTC
L1: HARMS_INCOMPLETE -- Gastrointestinal adverse events: HARMS_INCOMPLETE -- 1 known reported outcome(s) unresolved (FREEDOM-CVO) among 9 source-reporting trial(s); extracted k=1. The page must not render this as harm absence.
```

These blockers are recorded in `STUCK_FAILURES.md`. No Overmind PASS, certification, submission readiness or green landing is claimed.

## Per-page FACT and publication-gate measurements

N is the number of pooled outcome rows across all outcomes on each review page, not unique trials or all strand/sensitivity candidates. FACT means `claimgraph.verify_fact` passed against held bytes and the current committed evidence contract.

| Page | FACT n of N rows |
|---|---|
| balanced-crystalloids-vs-saline-mortality | FACT 0 of 3 rows |
| colchicine-postop-af | FACT 0 of 4 rows |
| colchicine-recurrent-pericarditis | FACT 0 of 4 rows |
| colchicine-secondary-cv-prevention | FACT 0 of 5 rows |
| corticosteroids-cap-mortality | FACT 0 of 6 rows |
| corticosteroids-covid19-mortality | FACT 0 of 2 rows |
| dapagliflozin-hfpef-hosp | FACT 0 of 2 rows |
| denosumab-vertebral-fracture | FACT 0 of 3 rows |
| doac-vte-recurrence | FACT 0 of 6 rows |
| dpp4-mace-t2d | FACT 0 of 5 rows |
| empagliflozin-hfpef-hosp | FACT 0 of 1 rows |
| esketamine-trd-madrs | FACT 0 of 5 rows |
| finerenone-ckd-t2d-renal | FACT 0 of 2 rows |
| glp1-ra-mace-t2d | FACT 7 of 9 rows |
| iv-iron-hfref-hosp | FACT 0 of 2 rows |
| melatonin-primary-insomnia-sol | FACT 0 of 2 rows |
| metformin-pcos-ovulation | FACT 0 of 3 rows |
| noac-vs-warfarin-af-stroke | FACT 0 of 8 rows |
| omega3-cardiovascular-events | FACT 0 of 8 rows |
| pcsk9-mace | FACT 0 of 4 rows |
| probiotics-aad-prevention | FACT 0 of 21 rows |
| sacubitril-valsartan-hfref | FACT 0 of 2 rows |
| semaglutide-obesity-mace | FACT 0 of 2 rows |
| semaglutide-obesity-weight | FACT 0 of 2 rows |
| sglt2-ckd-progression | FACT 0 of 4 rows |
| sglt2-hfref-hosp-cvdeath | FACT 0 of 2 rows |
| sglt2-primary-prevention-hf | FACT 0 of 4 rows |
| spironolactone-hfref-mortality | FACT 0 of 3 rows |
| statins-primary-prevention-elderly | FACT 0 of 2 rows |
| ticagrelor-vs-clopidogrel-acs | FACT 0 of 3 rows |
| tocilizumab-covid19-mortality | FACT 0 of 4 rows |
| tranexamic-acid-pph | FACT 0 of 2 rows |

Total: **7 of 135 pooled outcome rows** across 32 pages. Every page has at least one required FACT refusal, so the measured necessary-condition count is **0 eligible to pass of 32 pages**. The complete standard's every-page limb also hit a legacy strand exception; the subsequent every-page follow-up below reports actual gate execution after that source fix.

## GLP-1 measured strands and envelope

| Strand | k | HR | 95% CI | tau² | PI |
|---|---:|---:|---|---:|---|
| CONVENTIONAL_GLP1RA | 7 | 0.88839568 | 0.82839280–0.95274475 | 0.00120019 | 0.79594142–0.99158916 |
| GLP1RA_ANY_DELIVERY | 8 | 0.89840832 | 0.81582303–0.98935368 | 0.00672622 | 0.72345850–1.11566527 |

These reproduce the requested values to the shown precision. Primary PMID/family joins were independently checked against the held records: 7 of 7 match (`.tmp/identifier-review.json`). Numerical reproduction is not independent clinical validation.

- Refused PMID 34215025: axis `censoring`; UNTYPED â€” axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD.
- Refused PMID 30291013: axis `endpoint_components`; axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion.
- Refused PMID 38785209: axis `censoring`; UNTYPED â€” axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR.

FREEDOM-CVO end-of-treatment remains sensitivity-only and never enters either primary strand.

- `all-candidates-CONVENTIONAL_GLP1RA`: k=10, HR 0.86133751; label: **CONVENTIONAL_GLP1RA: all candidates; censoring unverified; endpoint compatibility unverified**.
- `all-candidates-GLP1RA_ANY_DELIVERY`: k=11, HR 0.86728781; label: **GLP1RA_ANY_DELIVERY: all candidates; censoring unverified; endpoint compatibility unverified**.

Specifications without held inputs remain NOT_COMPUTABLE.

## GLP-1 claim_scope_sweep

MEASURED: **848 registered of 2749 visible nonstructural units**; {'SENTENCE_WITHOUT_OBJECT': 1901}. N is the scanner's conservative visible prose/table text-run denominator, not linguistic sentences. The 12 named CGX4 legacy units were migrated or removed explicitly; new family/statistical-layer and remaining legacy rendering expand the current denominator. This is not a zero-debt claim. Exact units and fresh-render comparison: `.tmp/final-glp1-scope.json`.

## Verbatim old prose units replaced / removed

### tab-overview / unit-0037

```text
Favourable topic sample. Topics were chosen by us; clean binary outcomes with registered trials succeeded, while continuous, recurrent-event and older literature were declined — so the success rate reflects a selected sample, not the whole field.
```

### tab-overview / unit-0038

```text
Risk of bias is partial. Registry-machine-signal-restricted domains are computed from machine-available registry fields; domains needing human reading are marked not-assessed.
```

### tab-overview / unit-0039

```text
Registry snapshot is dated. AACT is a fixed local snapshot; trials registered, or results posted, after it are invisible to the registry-first recall, ghost and registry-machine-signal-restricted signals (the snapshot date is shown on those blocks). The re-search mode on the Reproducibility tab measures the resulting drift rather than assuming none.
```

### tab-overview / unit-0041

```text
The blind comparison is judged by an AI, and transparency is what we optimise for. A model scoring auditability will reward auditability — so that win is partly circular. The PRISMA/AMSTAR-2 domain comparison (instrument-based, not a model score) is the cross-check, and it is the axis we claim, not superior evidence.
```

### tab-search / unit-0009

```text
No search was run for this topic: every PubMed source is a PMID enumeration.
```

### tab-search / unit-0063

```text
Positive-control recovery: the committed registry query re-found 6/7 of this topic's PRE-SPECIFIED known trials (pooled + declared positive controls; enumerated 708; status RAN_OK). Reachable ceiling 7/7: 1 trial(s) are registered but not enumerated by the committed query (registry vocabulary limit — improvable). Missed: 30291013. Measured 2026-09-11T23:39:14Z. This is not systematic-review recall. It measures whether the committed registry query re-finds the trials ALREADY KNOWN to the build; a trial that was never in the known set is not in the denominator, so a high value does not mean the search is complete ? external audits found eligible trials (J-EMPHASIS-HF, an eplerenone trial, for the MRA topic published under the identifier spironolactone-hfref-mortality, PHILO for ticagrelor) entirely absent precisely because they were never in a known set. True recall needs an INDEPENDENTLY-GENERATED reference universe (concept query + registry enumeration, not the seed list); that rebuild is in progress. Recovery is also search REACH, not inclusion — whether a recovered trial is eligible/poolable is the screen's and extractor's job.
```

### tab-search / unit-0064

```text
Of 708 registry records matching the query (broad — reach, not precision): 397 have a linked publication; 62 have posted CT.gov results but no publication (poolable unpublished data no published meta in this topic has); 118 are completed ≥12 months ago with neither results nor a linked publication — a loose upper bound on non-publication, inflated by the broad enumeration and by NCT→PMID linkage misses, not a publication-bias claim. AACT 2026-08-30 (local snapshot).
```

### tab-screening / unit-0003

```text
Two independently-implemented rule screeners over 13 records: agreement 13/13, disagreement 0.0% (0 records). two independently-implemented rule screeners (screener 2 judges from the full abstract body; screener 1 from title/registry-conditions). Adjudicator: screener 1. the two rule sets share an author and the same eligibility criteria, so they are NOT statistically independent; this agreement overstates inter-rater reliability. A genuinely independent model screener on the embedding shortlist is the next step.
```

### tab-screening / unit-0004

```text
Trial integrity: 7 of 7 pooled trials covered by the historical PubMed check. No retraction was recorded in that checked set. Current integrity status unassessed for PMID 26630143, 38785209; the offline source set does not establish a current retraction check.
```

### tab-comparator / unit-0015

```text
Major adverse cardiovascular events: 0.86 (HR), 95% CI 0.79–0.94
```

### tab-reproduction / unit-0013

```text
Of this page's pooled numbers, a blind second extractor agreed or reconciled on 5 of 5 that are checkable from the abstract (0 identical, 5 same-result-different-statistic, 0 conflict; 2 not stated in the abstract). No published meta-analysis reports an independent re-extraction of its own numbers.
```

### tab-reproduction / unit-0017

```text
RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the registration SHA on a fresh clone regenerates this page byte-for-byte. Direct testing falsified that: running the advertised command changed several canonical output files, and running it AT the registered SHA produced an essentially empty review because the build consumes MUTABLE POST-REGISTRATION STATE (later caches, extraction state, adapter outputs) that is NOT pinned in any committed manifest. Until every build input is pinned in a committed manifest with hashes and the build runs from that manifest, this page does NOT claim byte-for-byte reproduction from the protocol SHA — only that the analysis is deterministic given the committed cache as-is. Independent REPEATABILITY (a fresh search retrieving the same set) was never claimed and is not claimed now.
```

## Final repository state

HEAD remains `55b457f5b17f0959f3aa37d9ce6c6e29c45b678d`. The real index is unstaged. `PROGRESS.md` remains ignored. No commit or network retrieval was made.

## Bounded repairs after the complete standard run

The full 11-limb table above is preserved exactly. The following changes were made afterward and verified separately; this is not a second full-suite PASS.

| Observed refusal | Source fix | Validation |
|---|---|---|
| All 32 replay pages differed; canonical-key-order test failed | Sort family lifecycle keys and JSON keys in all three GS renderers. The nondeterministic self-check had correctly set reproduction failures; no replay check or failure counter was relaxed. | Existing canonical-key-order regression and fresh replay limb below |
| Publication-gate limb raised `KeyError: 'strand'` | Effect gate accepts the existing `id` / `pool.k` strand schema and validates its members; untyped members still refuse. | New legacy-strand refusal plant and every-page limb below |
| GRADE audit published `i2=69.0` for an incompatible pool | Audit generator omits refused derived fields, retains their names and suppression reason, and pins the original baseline commit. It does not alter the historical object or the leak detector. | New immutability/suppression regression and leak limb below |
| Three newly enumerated gates missing from scorecard | Add the actual enumerated gate descriptors with empty event histories. No event, adjudicator, validation or PASS was invented. | Scorecard limb below; these gates remain UNVALIDATED |

All 32 builds now have exit code 0 in `.tmp/final-build-results.json`. The early builds that overlapped the final renderer edit were rerun, followed by the prescribed ordered renderers. Melatonin's transient `OSError: [Errno 22] Invalid argument: ...docs/index.html` passed one ordinary rebuild; no data or gate change was used to resolve it.

### Final targeted tests — verbatim

```text
.................                                                        [100%]
17 passed in 136.54s (0:02:16)
```

### Final retraction survival — verbatim

```text
pages with every marking kept (count >= base): 32 of 32
```

### Affected-limb follow-up (seven limbs, not a full standard)

| Limb | Verdict |
|---|---|
| offline reproduction (every live page replays from committed cache) | PASS |
| publication gate on every live review page | REFUSED |
| index currency (generated == committed docs/index.html) | PASS |
| served-artefact leak scan (docs/*.json) | PASS |
| search completeness (search_v2 measurement current; every state explicit; no zero from an exit code) | REFUSED |
| honest-state ratchet (no page may get quieter) | REFUSED |
| gate scorecard (every gate accounted for) | PASS |

Fresh final measurements: FACT **7 of 135 pooled outcome rows**; GLP-1 scope **848 registered of 2749 visible nonstructural units**, {'SENTENCE_WITHOUT_OBJECT': 1901}.

Full details: [.tmp/followup-final/limbs.txt](.tmp/followup-final/limbs.txt). The full suite, held-out detector, fix-state and gate-gaps limbs were not repeated in this follow-up. The earlier full suite remains **1048 passed, 26 failed**; targeted passes do not erase its unresolved failures. The standard itself captures only the final 15 lines of pytest output, so its pasted failure-name list is not an enumeration of all 26 failed tests.

MEASURED final publication gate: **0 pages passing of 32 pages**. Every page was executed; no exception substituted for a verdict.

### Unchanged search-currency refusal — verbatim

```text
TARGET verify_all.limb_search_completeness: head=55b457f5b17f0959f3aa37d9ce6c6e29c45b678d base=none tree=dirty:648 files files=3 registry/search_completeness.json harness/search_v2.py harness/search_completeness.py
search completeness REFUSED: engine changed since the published search_v2 measurement (a57dc45d6824 -> d278c2f7f852); re-run scripts/search_v2_run.py and re-publish before landing || states: RAN_OK 0 of 21; RAN_OK_WITH_SOURCE_ERRORS 21 of 21; RAN_ZERO 0 of 21; RAN_ERROR 0 of 21; NOT_RUN 0 of 21
```

### Final ratchet output — verbatim

```text
TARGET verify_all.limb_honest_ratchet: head=55b457f5b17f0959f3aa37d9ce6c6e29c45b678d base=none tree=dirty:648 files files=34 docs/index.html docs/ratchet_acknowledgements.json docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html ...
TARGET honest_ratchet: head=55b457f5b17f0959f3aa37d9ce6c6e29c45b678d base=2304824034b4ba8677da2d2d2453352711ed2a9b tree=dirty:648 files files=34 docs/index.html docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html docs/reviews/colchicine-postop-af/index.html ... base_resolution=merge-base origin/main pages=33 block_floor_refs=2304824034b4ba8677da2d2d2453352711ed2a9b,50f5a67b4fb19ada4716a0df6e6b68c2e4618304
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: not_assessed: base count 10, new count 3
docs/reviews/colchicine-postop-af/index.html: not_assessed: base count 10, new count 4
docs/reviews/esketamine-trd-madrs/index.html: not_assessed: base count 6, new count 4
docs/reviews/glp1-ra-mace-t2d/index.html: retrieval_class: base count 4, new count 2
docs/reviews/iv-iron-hfref-hosp/index.html: not_assessed: base count 4, new count 3
docs/reviews/melatonin-primary-insomnia-sol/index.html: not_assessed: base count 2, new count 1
docs/reviews/probiotics-aad-prevention/index.html: not_assessed: base count 34, new count 24
docs/reviews/semaglutide-obesity-mace/index.html: declared_absent: base count 5, new count 2
docs/reviews/statins-primary-prevention-elderly/index.html: not_assessed: base count 4, new count 3
docs/reviews/tranexamic-acid-pph/index.html: not_assessed: base count 2, new count 1
docs/index.html: lost banner block b6f0ec4ee42a22f99043b2d7d326c38eae34e7e26e01545b2b91a66f891d3eb6: What this is A reproducible harness that builds meta-analyses from a committed protocol, and publishes each as a tabbed,
docs/index.html: lost banner block f2b41f2edf033ecc02ec2067a325e375105a02d046a87022eff31c6db61cc53d: Every pooled number is verified against its source (gate-enforced) All 115 of 115 pooled trial-outcome numbers across th
docs/index.html: lost banner block 2c1c3da7038bd131e062ff9854e52955fbfc9f879c8cda1c38a211b17e690ec9: Gate scorecard: plant validations and production refusals Adjudication coverage first, so the unresolved cannot disappea
docs/index.html: lost banner block 14d82d4fda711fe9fe91721913d27f94c8af2fd442ab1832769897c57d897bbd: Parity with the published comparator (the finishing metric) For each same-scope topic: our pooled k vs the comparable co
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost banner block 983558e05e4bde77fc9f1394d2730329176e5f9c1a38a74fbd4a55e73f4d7b64: Snapshot: records_sha256 42df5c5c ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 004b373d6745c3bceae9513a9cf6a310bcc0136ae4b973c898d1a7355e062a4b: DECLARED ABSENT. DESIGN REFUSAL: after refusing reconstructed non-parallel designs without an explicit design adjustment
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 187218cede8a19de486ebe8f5ccbfbc4eb94a54238aae46662ee26a3cfd57155: Unit-of-analysis/design caveat (disclosed, not silently adjusted). 1 pooled trial(s) are individual-randomized factorial
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 52cd04e3a915bdf5778422eb031e9852886b3c694807455f9b05173937be4eb6: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 2c19afc5ad0d30515b877f866f1642b96a8121d5e7bad11f30471f93c7ee7ba9: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block f85a78807d31d85343a73c78d55902375bf1265142747d58d473e433855e41b4: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 7d49f76d89a220055f1ad2c49e47c1e9533f5eeb0458e5ccb74126a0080713a6: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/colchicine-postop-af/index.html: lost banner block 67757344ee670d1fcf41cf97cb423c0106fadab6c8cbeb3fca2968bdc4906419: Snapshot: records_sha256 474eff90 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/colchicine-postop-af/index.html: lost absent block c05a643044807856d475f2cbb9760c9bec2c21afb0d8bc0b755ef3e4ed55acef: HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH We retract any claim of a registr
docs/reviews/colchicine-postop-af/index.html: lost absent block 09bdb49b28d751b80a19a5156efc48af5a3d03b86e50c38f917ab02f3c739977: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/colchicine-postop-af/index.html: lost absent block c37a2ca56df8e47967377077be78ba1eb29ac6e9bb6d885d60e2ccb5bf4f13a2: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 32720823, 25172965, 27502857 mention this outcome in th
docs/reviews/colchicine-postop-af/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/colchicine-postop-af/index.html: lost absent block 9b1884cdd73a6a0f9056e82edd34706a8f1982b178287effdf441da7649bbf9e: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/colchicine-postop-af/index.html: lost absent block c6f55d3c41f28551439f475dcc2443401b255683274ce3f5a9decaf1af143876: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/colchicine-postop-af/index.html: lost absent block c3dab676c7cc4c4ed7c1430bc1f86f0463968a9ec0d1c2af796b6433c250b494: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/colchicine-postop-af/index.html: lost absent block 8dfc2f4ddd13b517cfa67ebda9a6a3790c8a1fea50c7298b85e933bf628f1531: Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a 
docs/reviews/colchicine-postop-af/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/colchicine-postop-af/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/colchicine-recurrent-pericarditis/index.html: lost banner block cb451432c3ac88913aa5c78c93cb9a26e55e78e46ea019031e32740e2d51e33f: Snapshot: records_sha256 570a1143 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block c05a643044807856d475f2cbb9760c9bec2c21afb0d8bc0b755ef3e4ed55acef: HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH We retract any claim of a registr
docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 09bdb49b28d751b80a19a5156efc48af5a3d03b86e50c38f917ab02f3c739977: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 35058ebae3177e56f4a895db383c9b55873db12d137ac96aee2284d7619ddabb: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 24694983, 23992557, 21873705 mention this outcome in th
docs/reviews/colchicine-recurrent-pericarditis/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 90d0d6414efc79f07b43707db054bcefac42ac266537d38d442fc53fb0773481: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block ca87b29f09498e773e1db7567bea84ec257efbd15950522c003e127d73e1d04a: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block d581286a505b55582c586d2d6eab2fb7c1fff552d507c802bb801d50765ab395: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 275b80a153f01f0d7930a7adecfb86ba9b0eee0b0a7cd982a26748a3c8ac4f41: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/colchicine-recurrent-pericarditis/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/colchicine-recurrent-pericarditis/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/colchicine-secondary-cv-prevention/index.html: lost banner block 9c45871f77ef0834e639a21ece88d52b77c3763fbeed9748b6aaba8d9a8127a6: Snapshot: records_sha256 2d3b2a35 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/colchicine-secondary-cv-prevention/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 79e8530721620a41dd9245d709864502413f259d5443c1347b5939ae65fa0292: Unit-of-analysis/design caveat (disclosed, not silently adjusted). 1 pooled trial(s) are individual-randomized factorial
docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 2f35820b0771882ce825e008c91720427f3067b3757140fa18acd821b341b27b: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block f640e854cfd1e10d0a39cfad5f14c70825f998fef6c8ee76251e10eeee8d2e7e: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 57205a3c80284c1aeff24226ff5968fc5934014af55e2b4724303c7a4e83c3af: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block a54ecd524eced807f0962ba546cc1fda3db13f551f886144467a6f2ea0d59259: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/colchicine-secondary-cv-prevention/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/colchicine-secondary-cv-prevention/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/corticosteroids-cap-mortality/index.html: lost banner block 5b90e3f99e5cf7684a31cc3f874cf7bde5f31e413a1fd13ece8f1878718a0ca8: Snapshot: records_sha256 b8a5cc47 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block c05a643044807856d475f2cbb9760c9bec2c21afb0d8bc0b755ef3e4ed55acef: HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH We retract any claim of a registr
docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block acb80753fadc32acfe3f94ec93708a4f5dee73845e867d7b3965c10e2eddd08c: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RU
docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block af1be9f121930cc61ce27b462dd1d544ef8632b057ea2e5143bda3d9514ecf30: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 36942789 mention this outcome in the committed abstract
docs/reviews/corticosteroids-cap-mortality/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 3d1c9ccfea5434242443d86ca404fbfe5d536dd2daffe26d0e761f2e22b8cc6d: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 09ed6ae25a015e0d8fa49dc6bbc1d5eaec199132b9199b61233147e1ef2af751: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 0f41b767cdeb7f3ac49137913e0bed645a03257d18decfe627336a69244089a4: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 16a31a620c341edc50358ed3a3849f254b021b872920a6a62340b100b4844dff: Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a 
docs/reviews/corticosteroids-cap-mortality/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/corticosteroids-cap-mortality/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/corticosteroids-covid19-mortality/index.html: lost banner block 7fc5fbe2329e78b3b2f54b921ebeca0bdf21436b44540ef7bf8e6be658cfd276: Snapshot: records_sha256 78f98d29 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 45bb4635fe128500a1ea7b4425bebd42c1abc364f092a64f7256b064807fe3be: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 34138478 mention this outcome in the committed abstract
docs/reviews/corticosteroids-covid19-mortality/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 654a8891121ff1083f93b4a07709fc795f187efc842043c4a52afc19586e34b6: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 3f98507b0cda3348baedbf46363de3908b89e1c5d408b2a0f35ef63fb04ffa14: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 460814ddc2ea0b454e2cc59e9a1ddbc97261099c24c7c68b7000dd33fc92a91d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block f11df83d8cdcdf214dcb3553d8907cc6b8122266f3c059c96f4b9c6d1c37ee9a: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/corticosteroids-covid19-mortality/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/corticosteroids-covid19-mortality/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost banner block daeb0ac407986902bd35c7ba1addbede483d6e9ef071486d0515468f507fc9d2: Snapshot: records_sha256 91f71997 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 727f47affcd9fbb34f44495c3052b8fe9f36966fcc90f141f6a9d9000cbc3e47: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 51e3022be2a1b8158448c09e50f13e9a095573c315136cb19b22b6400b97028d: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block c2bcf0acd104ff21660b73692747af61dbce3defbf18f5b3c80e1517ca389639: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 78460b7fd842a6407ad20cbdb5d6c465db843d3322956bee461b6900e54a2c20: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/dapagliflozin-hfpef-hosp/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/denosumab-vertebral-fracture/index.html: lost banner block 44f777950850cb0d700b1cdd8100689bfd9839e9e43d815d18947aa079767dcc: Snapshot: records_sha256 32165834 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block f1b0d7b429050cfec3a688bdb1df0579012084709efdc927e62da0888bd6fca4: DECLARED ABSENT. no included trial reported this outcome with a percentage-corroborated count or an effect+CI in its abs
docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block dbbbd408ec262767dde20079bb7b4a012975f768bb21d8062298b136d4f3eb59: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 19671655 mention this outcome in the committed abstract
docs/reviews/denosumab-vertebral-fracture/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block 01bcc626a75fd06d2d919c298b41dd968bcb0cf78e30a345fb12d69dad59c5e5: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block ab51bd420fb4b28762145e7f3ea285673ca016cbec97b409d54b532925a03a36: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block cdf08119611dfcdf4ec945d9bea4e527ef45935a09f48e359cb9a83311f74e12: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block ecc8ed947c95752e72c0a6cab09514ec7c5a34cdfc2717544a6d9011a28156f3: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
docs/reviews/denosumab-vertebral-fracture/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/denosumab-vertebral-fracture/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/doac-vte-recurrence/index.html: lost banner block 410b0ec6430a9737f71d7faa044221a0bd71653fc1aec9ddfd09f1aad7d0bda1: Snapshot: records_sha256 ef5c1c6b ; retrieved_utc 2026-09-12; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/doac-vte-recurrence/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
docs/reviews/doac-vte-recurrence/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
docs/reviews/doac-vte-recurrence/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
docs/reviews/doac-vte-recurrence/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/doac-vte-recurrence/index.html: lost absent block c7f018104f5e77d148ef76b22779d0fc51ae5c32eab1c6266773a42c9e0c5ed7: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/doac-vte-recurrence/index.html: lost absent block d6cdc1b8f2806a8da5ff7e7b5fc45b009b2766c6ef431196a2cf408055a887fb: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/doac-vte-recurrence/index.html: lost absent block da01b6ba519d765f1f7085f7413af2667584916e67a43fd872d8f391a72c3f51: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/doac-vte-recurrence/index.html: lost absent block ac057cdbffb6d6ed529764ed96d02c9bdf085df5d37d7c6dd7ccb84bffb0c38c: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/doac-vte-recurrence/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/doac-vte-recurrence/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/dpp4-mace-t2d/index.html: lost banner block e29da437f91714ae26b2d5f0da715141a26ce67145fa4817cdf7036eb0a353f4: Snapshot: records_sha256 81256a4a ; retrieved_utc 2026-09-12; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/dpp4-mace-t2d/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
docs/reviews/dpp4-mace-t2d/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
docs/reviews/dpp4-mace-t2d/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
docs/reviews/dpp4-mace-t2d/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/dpp4-mace-t2d/index.html: lost absent block 66d6d9cbc227d9a699cdf986265b2b7c04a066c4b01de1cc8e8e380e0282a071: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/dpp4-mace-t2d/index.html: lost absent block 80050dda0a27c639679fbcbb44ad5c7a74c4ca8ac59d189adaf5c8c3756d86b0: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/dpp4-mace-t2d/index.html: lost absent block 91ec4628b63b3e86d9c7d2f143975fdc54e4c8782edea24d1fdb19b3fb96c48e: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/dpp4-mace-t2d/index.html: lost absent block 6fd4fe1fa9d7c27b9dae78df1aa0508709049363a38be5e9069ba7005c2476a2: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
docs/reviews/dpp4-mace-t2d/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/dpp4-mace-t2d/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/empagliflozin-hfpef-hosp/index.html: lost banner block 303b53251c8bad5d3da89eeaf6b9f6db72c408f70f6e3677adf1edd3403438d5: Snapshot: records_sha256 5ef3f171 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
docs/reviews/empagliflozin-hfpef-hosp/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block ecdd529cdb73661a1dc8534de5961bd2c81af1f89d690027dc9ff886a5ba6edf: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block dd19678a5c1c87e7219abc7156beab32777aa31eb791b6ed4e2ce0e301c8acce: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block 90d9054f250f3f8c546865b94358f617dfe8d76608f9e5870ebc508f90c91590: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block 6b24891820614ead5920ab05217a096376de6f5eb595bc20bfa5e723ed576f82: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
docs/reviews/empagliflozin-hfpef-hosp/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/empagliflozin-hfpef-hosp/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/esketamine-trd-madrs/index.html: lost banner block 5db3239db27b959c8a192465d36e1f3a88a928fd9365d0c5e4934a9328852cda: Snapshot: records_sha256 a09370ee ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/esketamine-trd-madrs/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/esketamine-trd-madrs/index.html: lost absent block 51984e7bede57d9bf3873159b06be81aa191c14d5289e9eb38532fa57bca1e01: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_ER
docs/reviews/esketamine-trd-madrs/index.html: lost absent block 4554b38e12246adb7ec988f9bb194fe41e7ef3abdf7fe3db1e2c31bfc5621cc9: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 34696742, 31109201 mention this outcome in the committe
docs/reviews/esketamine-trd-madrs/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/esketamine-trd-madrs/index.html: lost absent block 4c29b75436df70dfc57dde8e4c0b7975089c3303c76a5d93c7c5d95c4e231a5c: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/esketamine-trd-madrs/index.html: lost absent block 17c77c145420770141d32fd0d8156b182d450fd35b6287a5cf9b40e2aba0c827: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/esketamine-trd-madrs/index.html: lost absent block 7058b2699c4ee2d0f8489f2cd13f365fa05dcf95e49011617b8ecdca765369fd: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/esketamine-trd-madrs/index.html: lost absent block 7a1b2f9d0aa30150320bb235576d215f3bc335d0d9a1f07ccb06f24c2efac169: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/esketamine-trd-madrs/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/esketamine-trd-madrs/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/finerenone-ckd-t2d-renal/index.html: lost banner block 5be8b8344e22c6ce007c14827eb881142fd7c71a84282cbd3ba30f865639a7fc: Snapshot: records_sha256 4e838bbb ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 63c17a3b1a6ff026e3216b53bd3c6078e2df601534271776decdd9f03b2480f6: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 33264825, 34449181, 26325557 mention this outcome in th
docs/reviews/finerenone-ckd-t2d-renal/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block e9b6c91404265dda6919cfe2280db8b34008d4f2ef350e80418e013bd2ccac3d: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 48baaf8c4c6a15bff29b9fe93538aeb4badbc9faaee9c82198b417b94ba1138c: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block cdd5838e9ddf4722e73df01da34e5b8d82b6da2209bfc80e58b07b824f91f06d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 2f96569c95ff0621bf07097dce733e6e727a8f2aa663c83fbc36d42a2ae93a58: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/finerenone-ckd-t2d-renal/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/finerenone-ckd-t2d-renal/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 0606da3be98c8d40045f716df24fd8af88b2ce8b7b3f56953420acfc386da74e: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 4a266aa0f9d335743a4f9107c0fc651306d41303071fe7cabdf23eb83387b40e: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
docs/reviews/glp1-ra-mace-t2d/index.html: lost banner block 5fc60b3e0fa0e391c90848520ff1dcdb441ba4bd43dac818f96ff636bca44940: This page offers greater auditability, not stronger evidence : every number traces to a committed source, every absence 
docs/reviews/glp1-ra-mace-t2d/index.html: lost banner block 1c7e24dd1b2e31a6b2c42983b46322e0b978064c7e0f1784f628645f6bce823a: Snapshot: records_sha256 1e0282f5 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block f78c512047bc0437de0926a52df7805b797214433f9feb56344ab2c29eb00219: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block f3641fa7e56d8d396bc0f8e0e7938987d10f402964ce66d602c13133ff3df1fd: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 31185157, 27295427, 34215025 mention this outcome in th
docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 181eb2cc7da5cb8589a7ebe140194b85594aa6dbd6f5994ce6e9d7f982d8e2b8: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 31185157, 27633186, 27295427, 30291013 mention this out
docs/reviews/glp1-ra-mace-t2d/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 3b5fcb2c43c291d46f0928d1f6dd4f574eb1adc1d212f1113207d41844af8c41: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block ade5009855456019293990bec265c1e0ddea1fda4d155316b7f6728b27fef7eb: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 118737e7052fbdd570b2bb1df218c74b838fe181282b54f53fae236363d15295: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 04a2e41c88e8930b16c4783a824d69b3411af2e0f716308888eb7504faec9d34: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
docs/reviews/glp1-ra-mace-t2d/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/iv-iron-hfref-hosp/index.html: lost banner block 922bc57e32d805488dc7cc0e69b76a126750ace0f40a98d4af5c58eae3e15e83: Snapshot: records_sha256 242ba998 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 31c8e387bf859660214caa9bf45f71bca44e80baed46a0320cd5420051ff48de: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RU
docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block f1b0d7b429050cfec3a688bdb1df0579012084709efdc927e62da0888bd6fca4: DECLARED ABSENT. no included trial reported this outcome with a percentage-corroborated count or an effect+CI in its abs
docs/reviews/iv-iron-hfref-hosp/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block e33d3ad545e807ab7ed52a5479a3bf8255f04c8ae05e898287e51cddca0953aa: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 95985cd84fbf919935f5099fffc4c42de010543b74fc4555a113a263a177c7ec: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 19e48f45872f041e87da3e5d30365a431e76d3d07e43ea7a5ab24ab068b59b73: Overall certainty: not rateable. the primary pool mixes INCOMPATIBLE estimand classes (HAZARD_RATIO_FIRST_EVENT + INCIDE
docs/reviews/iv-iron-hfref-hosp/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/iv-iron-hfref-hosp/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/melatonin-primary-insomnia-sol/index.html: lost banner block d133296791325516a27f5024c7c6b57db9a7aeabb5bd79cdec0dd93fb46af616: Snapshot: records_sha256 159e5415 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 51984e7bede57d9bf3873159b06be81aa191c14d5289e9eb38532fa57bca1e01: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_ER
docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block a16a18bef1a7af5809468fe78f126b2a3dd5d4385f5b503bf9976f62ef5f26da: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 33157425, 22346363, 20712869, 18036082, 12790159 mentio
docs/reviews/melatonin-primary-insomnia-sol/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block cbbd6a73cc0d27b1e77534aa7ff16ad6424ee9b025379a7f32e29e17c50bbbda: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 4972766020294b0566a4fc26feccd2e0da568e0e677638429fac1ac3d4a63d6b: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 7b4225b798a5ed89e4d0e8a324f0b622166dcaac88512b73d4dfc3f114f60faf: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 6b77e526173bc21f8c36fc9bb3eeea0c9902d81540ad387fc201c38cb209a983: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
docs/reviews/melatonin-primary-insomnia-sol/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/melatonin-primary-insomnia-sol/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/metformin-pcos-ovulation/index.html: lost banner block ef76770b0dd933fd73a963b6c0d2cf74b9a72b663ff9445df51dce532cc247ce: Snapshot: records_sha256 1fdb53f8 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 31c8e387bf859660214caa9bf45f71bca44e80baed46a0320cd5420051ff48de: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RU
docs/reviews/metformin-pcos-ovulation/index.html: lost absent block dd1dead6c2560a93ff01a5324a76c288e758fc97cb2a645c790180163e821248: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 16769748 mention this outcome in the committed abstract
docs/reviews/metformin-pcos-ovulation/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 6ee988ab9970f78e22c815d201785b6d167c938e6e699da61186de8cacfd6312: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 16264cc27213b813e1aeafd53e66948603ccb01474997893fe6c53f1a37a022e: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 72db58add18abd2662f0e8b4798ff2ee589a750ad3328d91563734f69747b695: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 8e8301343df98222cfe40b761ee7ec58afc1206c5534fee72f5d709f163834e3: Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a 
docs/reviews/metformin-pcos-ovulation/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/metformin-pcos-ovulation/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost banner block cb663900acaec0589ce8453f2f0fab07a582c6aacb8ccbdf4e5ed2be47c4eebb: Snapshot: records_sha256 dfacf3bf ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block f78c512047bc0437de0926a52df7805b797214433f9feb56344ab2c29eb00219: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block b0828b821327892706ca39221ca0550a0b0043e8506a2868c6223cd5999b8503: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block e265d763c956988c33d33de18e544f09e182e98528af44246fb987cc65a5c2dc: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block 496a7c240788f4917387ccc389f17c25551a2842b80391e40c0a7353dfcd57b3: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block baea49ebb9e814194adc1b2736d663afc71255af1fa6cccb8d6d0d1589f72307: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/noac-vs-warfarin-af-stroke/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/omega3-cardiovascular-events/index.html: lost banner block c1c5b55299c91132cf6c146defaa2d13962b48c20880d790b36bc8c4360d0823: Snapshot: records_sha256 f40d3169 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/omega3-cardiovascular-events/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 7d2411912d3b55496a33fe9a0905f6480d10aec4d43fb37141f183cb736add53: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 30415637, 30415628, 30146932 mention this outcome in th
docs/reviews/omega3-cardiovascular-events/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 2e52a207b30781148639e2ca6263bbfc5ea5d11d8d7ca9655303821d3b52ddfe: Unit-of-analysis/design caveat (disclosed, not silently adjusted). 3 pooled trial(s) are individual-randomized factorial
docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 4bfa9e524f3089c4c5cd06a844cdae1489c43898c25d569c14d17005e0dc3af1: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/omega3-cardiovascular-events/index.html: lost absent block fc29991097b4dc217d3f023445f76cbffa5c22b6bf494127a23f390975d8369c: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 6398132dae3a1a7108a74c25d54c80f3a739512df47772bc155502751c36b41d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/omega3-cardiovascular-events/index.html: lost absent block c77ef0e830e5d74310099c90ef651caad9e1ee2aff8dd7d8de391e991afc6962: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/omega3-cardiovascular-events/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/omega3-cardiovascular-events/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/pcsk9-mace/index.html: lost banner block c05e20e7a9b7ea8d4b39012a216008d917651e6080af654d0d819c92e96864a8: Snapshot: records_sha256 b1ef6c11 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/pcsk9-mace/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/pcsk9-mace/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/pcsk9-mace/index.html: lost absent block 61163e4e61d3b0c8976d05a3c2402af897356d709003c3ea8a7b34991e38813e: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 28304224, 30403574 mention this outcome in the committe
docs/reviews/pcsk9-mace/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/pcsk9-mace/index.html: lost absent block d045eb82cc2e52801ad1f457995308936bee1d9e633f4b9709cdc1787504729b: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/pcsk9-mace/index.html: lost absent block cdae34e1a6433db309ca24da20a1250284f651795828d207d569bccb725d3390: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/pcsk9-mace/index.html: lost absent block 7b2d1674478f8315cbef7e6285dad3f45e0a93bc14acce314da847954a6bcbb9: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/pcsk9-mace/index.html: lost absent block 9fb655c4cc64424164f8dee8b10bed1f52ddf44da88fa836084f5ea54e5ed034: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/pcsk9-mace/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/pcsk9-mace/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/probiotics-aad-prevention/index.html: lost banner block 6f6f96af69410d2951ffc9c54eb72005a31d84db761045cdf01c8b315b1f9e51: Snapshot: records_sha256 a832babc ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/probiotics-aad-prevention/index.html: lost absent block c05a643044807856d475f2cbb9760c9bec2c21afb0d8bc0b755ef3e4ed55acef: HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH We retract any claim of a registr
docs/reviews/probiotics-aad-prevention/index.html: lost absent block 09bdb49b28d751b80a19a5156efc48af5a3d03b86e50c38f917ab02f3c739977: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/probiotics-aad-prevention/index.html: lost absent block 34a8823b0bad217626b851828dc856654dbbae42bf5964fcb712262cb30490a3: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 42608299, 41699149, 40716758, 40548185, 40488914, 39935
docs/reviews/probiotics-aad-prevention/index.html: lost absent block 6ecb01b65a6288b3037ae6e2f1019cda43b2ae320ca660365fa61d46a93210f5: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 40548185, 26973849, 23932219, 19138244 mention this out
docs/reviews/probiotics-aad-prevention/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/probiotics-aad-prevention/index.html: lost absent block fe5a5a96506acf422872e59e045b9257d911a403ba1f6876ea2e418cab3cc71d: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/probiotics-aad-prevention/index.html: lost absent block 4b252317efdebe6963ef01a013fe5eb43646c12497849c9063636b005ef2cfc9: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/probiotics-aad-prevention/index.html: lost absent block 3690b1ad41faf51a261928ebca1cf523e09cb400f4cc759e307d156697580e8b: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/probiotics-aad-prevention/index.html: lost absent block 99becb418875e3d7ddd6dbda49c73006d7252e22eef6dc35199ff53c62376365: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/probiotics-aad-prevention/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/probiotics-aad-prevention/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/sacubitril-valsartan-hfref/index.html: lost banner block c9570bd907f9397433ca1c5632a5f1da74fb5e63c24a3c44c2ae34995363a023: Snapshot: records_sha256 58f1709c ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 31c8e387bf859660214caa9bf45f71bca44e80baed46a0320cd5420051ff48de: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is NOT_RU
docs/reviews/sacubitril-valsartan-hfref/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block bff5f3115693b0718df1df746a4fe566271c472ab11819b1fc25688a085945b4: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 7f05f40e226c430ba2d04aeaa23acc772e6f906aa65d61f5f2e75d2e9450aae4: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 072a75e8e15be99b57cc84e267fcc385e25589124b7fc7b60d3203a4a6083bbf: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 09ed94fe6e8360cfecf6ad69db79fcb7ca77b505565936768935dc6b62adcb67: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). PROVISIONAL: this 
docs/reviews/sacubitril-valsartan-hfref/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/sacubitril-valsartan-hfref/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/semaglutide-obesity-mace/index.html: lost banner block c277dc7a9439b0e4d0bd6b1430ab5c6dfa3209e7bf1bc676437ba5728f0a9c6e: Snapshot: records_sha256 ac910156 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/semaglutide-obesity-mace/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/semaglutide-obesity-mace/index.html: lost absent block f1b0d7b429050cfec3a688bdb1df0579012084709efdc927e62da0888bd6fca4: DECLARED ABSENT. no included trial reported this outcome with a percentage-corroborated count or an effect+CI in its abs
docs/reviews/semaglutide-obesity-mace/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 36f1272cbafe5ab6d098d3764690890c7867b73c4376e443fc505ff44cfb3af2: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 08680a96bfa69c446138ef1efe16db7a39a864723beb64f70be4bdb32978fb19: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 26ab09f2b6cbce2e1e158fb630fa57a0c0186f3db7491523f7fa2adf79d4fcbc: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 3fe49f850a635eb2189b79baa4f679f142e19bce8eacd03224e40f2a3feee68c: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/semaglutide-obesity-mace/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/semaglutide-obesity-mace/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/semaglutide-obesity-weight/index.html: lost banner block 32d0ad299559b616aeb37b8f28c79e07e42eec3c0e395336073c09c51961c98c: Snapshot: records_sha256 195d48c1 ; retrieved_utc 2026-09-12; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 51984e7bede57d9bf3873159b06be81aa191c14d5289e9eb38532fa57bca1e01: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_ER
docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 7d054e36a29c628d0807fc18fe5eb817c1df0f3006068c0564e198eadb2d52d0: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 42575111, 42070571, 40825340, 40629530, 40069849, 33625
docs/reviews/semaglutide-obesity-weight/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/semaglutide-obesity-weight/index.html: lost absent block f8a5707ab64fbc8f436f190921d8e79e893e813b8ba9921fb19fcc5f136c4238: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 0b94e470e01c548721077e31502ffec1a5fe3b47eedc2f8626b46dfe78d46835: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 45446b368a9c9346efd1ba26dd96de014ee501bb6caa900c82360c75634ad0af: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 0f8ad79d9c66fae246cde2257ffe2107813ab8e139bc575a8052b607ce492c12: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/semaglutide-obesity-weight/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/semaglutide-obesity-weight/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/sglt2-ckd-progression/index.html: lost banner block 24e1177446fd6c46b8db81088cbbf589701abd7ebab1e6527117586423b11213: Snapshot: records_sha256 4a7478c2 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/sglt2-ckd-progression/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
docs/reviews/sglt2-ckd-progression/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
docs/reviews/sglt2-ckd-progression/index.html: lost absent block 7f784e67f837798409405c149567f7c89159a67591406edeadbd6edec156d5f2: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 30990260 mention this outcome in the committed abstract
docs/reviews/sglt2-ckd-progression/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/sglt2-ckd-progression/index.html: lost absent block 40092b16403db4c15aa693020e60b837701335ea440baef9f774b981fd620cd1: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/sglt2-ckd-progression/index.html: lost absent block 0320760e6bcdb6581320126e7dee63b5506c7a8c25303f9f617e514acc4f2ea3: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/sglt2-ckd-progression/index.html: lost absent block eb69309ac2fbd67743b0ded82a6daaa5e7316e38145aaa3f3a29d30223c4c4fc: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/sglt2-ckd-progression/index.html: lost absent block db4655aa165a114b729706357dc701b5b8bcd0a7e9d9d21aa8ff9d9cd969266b: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
docs/reviews/sglt2-ckd-progression/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/sglt2-ckd-progression/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost banner block c2e448a7a5ee87b14750d6172d418143869d71d8d2f7568e059605593ec9de12: Snapshot: records_sha256 056f66b4 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block c839630e932144f699429abbe2e861a0bd987344d8372c0a5b2ce106b59be677: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 31535829 mention this outcome in the committed abstract
docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block 2565ad7a1e882c7ccf2a45c20448223b484335ea10a53179b9a43dd950dded83: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block 1e64c354919293b51d17319223237128f234c225cc3762b3b91f859a4f21a893: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block 965250ce4cfd0308b296c784661c49b482f248ddcf01136bde7f1c17d3e77525: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block be6ab27c20f82912a45e9cbf09be8802e97350ee49be185e8851e97a2440fe15: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/sglt2-hfref-hosp-cvdeath/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/sglt2-primary-prevention-hf/index.html: lost banner block b4d94a4d81dddc0e854ad5f61d850d781bf6f664a87fa4c217d60927dc72e105: Snapshot: records_sha256 ba5c49e2 ; retrieved_utc 2026-09-12; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block 616358946837d4e700b07a8dc3b9fc71134a3160a28941ef8383a5dbf2aa0359: DECLARED ABSENT. no harms recorded
docs/reviews/sglt2-primary-prevention-hf/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block 1dbb0dc87beac85c77ac53fc9f52406d3eddd62cb4ccfc74ca034f7b0ed71e21: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block bc8f2f2191b9b07735e8a5c8399a6fa9d72f51df88021e62676d49dc665aea26: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block 8d61bf47c06063dec14f2d4656e683b5c5445128098b53a4545d6f790bf52db7: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block a88aa38b82f42e250de2a7b237f6026ce62106c4c5a06c14521eef07aba1cf69: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
docs/reviews/sglt2-primary-prevention-hf/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/sglt2-primary-prevention-hf/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/spironolactone-hfref-mortality/index.html: lost banner block ed7a148966f33ebbf44e717e74b3bb5cba442fd27698ceb915ae71b46dba2971: Snapshot: records_sha256 8352ca95 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block ec9fd7c4d2ac80fd976612d3b03f8ffdcb61d1f46cb8375d2f3bd6c7cff3ae4b: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 10471456, 21073363, 28824029 mention this outcome in th
docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 8124911ae094726bb85f9fe8d1f2efb2a69ffccc1951b6caa3e030a638175182: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 10471456 mention this outcome in the committed abstract
docs/reviews/spironolactone-hfref-mortality/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 6fb533d581f68da392afcc89bcaf1ec0b6f1ebdcb59a421d831aebae1c466f92: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 1557cc75bdd3c3e88e8efdcdfc7172ccce312164d8db9240c5a5240b75bdf0e5: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 4bfc6a1f39b6524082d059f894fe1d3440e3725de7a19ed581edc014ad0c276d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block a20410a071d279f8c5f0d4f2524c309a86be39ca53864329abebb24238d6d882: Overall certainty (provisional): low (starting from high for randomized trials, 2 downgrade(s)). PROVISIONAL: this is a 
docs/reviews/spironolactone-hfref-mortality/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/spironolactone-hfref-mortality/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/statins-primary-prevention-elderly/index.html: lost banner block dff1b4824f648a4dda451026e0025d13c2be7fdb2712006ca3ebead3d3f35927: Snapshot: records_sha256 7170920d ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 7c17773d7ee68a33cf2378a420020f88a59523b40af38f32bd6b4e6cda18f6d1: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 42670961 mention this outcome in the committed abstract
docs/reviews/statins-primary-prevention-elderly/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block c04bac3cfdc3fac6d7b3272a1dd7a2929d8447bc1a0852c2a38da02eeba7dd5b: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 25845d7b8f6c2c99a73579fec6eb96610e926af016e6fb5374d54b0bafa09bc5: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 1b61824a331cba7ed7af28c78c2e1e32f08a54957ed61b788a77d0ea6495dbb8: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block e49ac2b8042d3c0330eac88d67e2accc7128131e64a79ea69ad81323e3b054d1: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/statins-primary-prevention-elderly/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/statins-primary-prevention-elderly/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost banner block 831ac718dba9f4b8248b7d0fe1f68b0955dc8380906cf4beb71a6eb2827a7da9: Snapshot: records_sha256 a6e860ba ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block f5da8f081b48676ae6efe5fa971e81cf7e09369b1de95c0b56d639dd3c9b8cc2: No search was run for this topic: every PubMed source is a PMID enumeration.
docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block fb0eaa210bf1f482bec96fa544cc3c703fd7e059f4126a350f066f629ffd5486: KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this to
docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block f78c512047bc0437de0926a52df7805b797214433f9feb56344ab2c29eb00219: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block f1b0d7b429050cfec3a688bdb1df0579012084709efdc927e62da0888bd6fca4: DECLARED ABSENT. no included trial reported this outcome with a percentage-corroborated count or an effect+CI in its abs
docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block 1df51e83141f9980943f1060bc10a23ed3c4fe9cc765c409f42475d6a7e50a63: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block 4b332ea83fea8621ad8f08b843ffcfb5a6456a1539827fc5f4700d9e4ea2df4f: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block 35299e230bcbee6aee55bf7259d56deae3c7966fbcf86977f1661a0a378cc2a9: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block c3fd688cd9c199c13ff366e0812df59617cd1cd51a0c62f409f3ee3598b7f98e: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/ticagrelor-vs-clopidogrel-acs/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/tocilizumab-covid19-mortality/index.html: lost banner block bfb757f80a5cfe9a8887c7540779e13369f2d30064eb08389752ec46201c6afc: Snapshot: records_sha256 a6b727dd ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block f1b0d7b429050cfec3a688bdb1df0579012084709efdc927e62da0888bd6fca4: DECLARED ABSENT. no included trial reported this outcome with a percentage-corroborated count or an effect+CI in its abs
docs/reviews/tocilizumab-covid19-mortality/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block bd14f8a89b0544ae6a4315d2ae4bcbae9a47bcb4256ae8696a27d2332454058b: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block 20c3e04e68c4397a8e7994d28ed9034c4a2360a8397263fa23fc49d9c04c35f2: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block f16e90d7d6310cdb9d636170fa9b5160948b9ed4d0d5fc380801531bb72dc82d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block f5fafd4d2f6b2c4d7c6cd44bed380029eed96d2f06707b0b8321289ed32b242c: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/tocilizumab-covid19-mortality/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/tocilizumab-covid19-mortality/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/tranexamic-acid-pph/index.html: lost banner block 65e66ffb5fccf2333acbe2451d28a7cb4da497e3f13c3a1d38e564a90ba9d69b: Snapshot: records_sha256 940022e2 ; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query re
docs/reviews/tranexamic-acid-pph/index.html: lost absent block 4f936a303e59e57fa26f1ab2315e049751241c822b46df14750f890fd7ee0b4b: TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systemati
docs/reviews/tranexamic-acid-pph/index.html: lost absent block c708203679d2b7f8fa3b78ddb78d7cd6bd8d9a4c51d747b70138a2456a5d1594: Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK
docs/reviews/tranexamic-acid-pph/index.html: lost absent block f425710ed75286f7ad4624bb8b617912fb9609feda3e5da59b90fa0e879c3f91: DECLARED ABSENT. REPORTED but not extractable as a pooled value: 32143721, 28456509 mention this outcome in the committe
docs/reviews/tranexamic-acid-pph/index.html: lost banner block 35f80836a0a6ca5e08da22ff8a64f948cdcb604ff9825b0511197e4e7f531f97: RoB spans span-checked (cross-family): 97% agreement (32 of 33 scoreable), from a seeded sample of 45 model/registry-der
docs/reviews/tranexamic-acid-pph/index.html: lost absent block 715b9f50c00c6b3491cb174de95bd3713812364b2d43a2da906264dbac4e63a9: Randomised-contrast disclosure (per pooled trial, from the registry arm structure — disclosed, not an adjustment). Eligi
docs/reviews/tranexamic-acid-pph/index.html: lost absent block d161053ef44d71264c34d6d71613938e2fd0828724e11a79add0d67ab150174f: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/tranexamic-acid-pph/index.html: lost absent block 295a768c15eeb1c46a8cda92832439fa2eb6fb6b500a8f11b2b737f4f9b6bc0d: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/tranexamic-acid-pph/index.html: lost absent block ac7d9964082a37db27b76419258d0d324859f0857bdc0357035d21ff2c999a37: Overall certainty (provisional): moderate (starting from high for randomized trials, 1 downgrade(s)). PROVISIONAL: this 
docs/reviews/tranexamic-acid-pph/index.html: lost banner block 653be54eceb4c296c8a80596ff7a14771fc47e48f8694d6165137e37ba6304f3: This manuscript is generated from the review object — every number is interpolated from a committed field, and a gate li
docs/reviews/tranexamic-acid-pph/index.html: lost absent block 2742ee7dbe97def1b7f26e017065aaf15792f04aaaef1e0a7587ddb8183941ac: RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the regis
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 3056ab225b9e210a00936fdcbfa361f8e934c4a3eae8501e77e4dce9dedb702c: Funding / conflict-of-interest disclosure (per pooled trial, from source — disclosed, not adjusted). Industry-funded tri
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block b8c4b60bd942a25aaaafc43a4cc63dc78c3e705961e0fbf0a49155bf75bfe08b: Does the result survive dropping the trials that are not low risk of bias? The primary outcome is re-pooled by risk-of-b
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: lost absent block 960be40ef77ff4a78df7696b5504db234eb1f8d843aa2fd6152fed50e4fd2b0d: Overall certainty (provisional): moderate (starting from high for randomized trials, 0 downgrade(s)). The rating is capp
docs/reviews/glp1-ra-mace-t2d/index.html: lost absent block 74ef9f624c5845659feef24079fb873482531098515959d4a9a1c20473b27570: STALE — this topic's result is not current. One or more dependent outputs on this page are known to be incomplete, super
```

### Stop condition and remaining work

Stopped under the prompt's fail-closed clause. The held harm source records provide only a retrieval date, not the UTC instant required by the unchanged FACT gate. Passing that refusal with the available evidence would require inventing metadata or relaxing the contract. The changed search engine also requires a new measured run; relabelling the old engine's results is not a measurement, and this lane is explicitly offline. Neither shortcut was taken.

The all-PASS-except-ratchet finish condition was **not attained**. Separate integration debt remains: unregistered family/statistical-layer/legacy prose, the other full-suite contract failures, unresolved harm extraction, and integrator-owned ratchet acknowledgement. Those are not all declared inherently unfixable. They are listed openly rather than hidden by a structural exemption or a changed baseline. No commit, staging, network retrieval, gate weakening, or ratchet signature was made.
