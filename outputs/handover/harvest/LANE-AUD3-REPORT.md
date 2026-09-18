# LANE AUD3 — measured implementation and remaining blockers

HEAD: `3f8add72d50b84eae2000625387e3194137a06ea`. No commit, reset, checkout, stash, push, deployment or network.
This is **not a completed AUD3 acceptance / release PASS**. The canonical RR/HR
admission defect remains open, and the build/gate evidence below is authoritative.
Existing integration-tree changes were preserved. No portfolio/submission status changed.

## MEASURED changes

- Protocol clauses compile to `registry/protocol_constraints/glp1-ra-mace-t2d.json`.
  `registration.protocol_sha` generates the file before the build. Clause spans are
  verbatim protocol substrings, tested as such. Status counts: {'IMPLEMENTED': 4, 'REQUIRES_ADJUDICATION': 4, 'UNIMPLEMENTED': 16} out of
  24 clauses. Unmapped amendment clauses remain UNIMPLEMENTED.
- `screen.run` reads the declaration, searches population in held fields beyond
  the title, and retains missing ascertainment evidence as UNRESOLVED with an OPEN
  obligation. A retain decision is not included in the pipeline's pool candidates.
  Positive ascertainment requires explicit held methods/design wording or a
  structured evidence span present in the record. Missing evidence is not inferred
  from a trial acronym, favorable result, or protocol target.
- `strands.declarations` compares configured membership with the protocol's explicit
  primary/exclusion declarations and fails on divergence.
- The only added `page.py` hook is the call to
  `harness.protocol_compiler.render_conformance(r)` immediately after the existing
  Protocol comparison block. It renders every clause's status, including UNIMPLEMENTED.
- `claimgraph.input_set_version` includes scientific meaning and held provenance
  fields through `identity.scientific_inputs`. `_scan_dependents` recomputes current
  stamps from outcome rows; strand stamps are recomputed from strand members.
  Membership hashes are recomputed with the membership module's own input contract,
  not compared with a numeric-input hash. Dependency metadata is not a dependent.
- The manuscript result dependency and new dependency-certificate receipt cover
  all outcome input versions, so GI changes invalidate both as well as the GI pool.
  This receipt uses existing `depends_on` machinery; it is not a replacement for
  the release CERTIFICATE.json or proof that the issued certificate passed.
- `invalidation.assess` propagates stale dependents. RV2's existing heterogeneity
  logic and RV1's claim state/scope/permitted-use schema were not rewritten.
- The old-label test now changes an actual event count. New tests cover 7 of 7
  meaning changes: censoring, population, endpoint, design, estimator, span, adjudication.
- `regulatory_fact` accepts the held manifest's top-level repository-relative
  `extracted_text_path` / `document_path` as well as the older nested held fields.
  Path containment checks remain active; no absolute-path bypass was added.

## Plants and coverage boundaries

The pre-fix measurements were taken before product edits. Scratch objects are
deep copies of the real topic config and held review; planted records and mutations
are explicitly synthetic audit inputs. They are not research findings.
The screen and type plants call the production `screen.run` and
`effect_type.type_rows` routes; the dependency plants call production `check()`.
They do **not** establish a full scratch-topic end-to-end production acceptance.

Pre-fix GI event mutation: hash changed, `check() == []`. Post-fix clean scratch
baseline: `check() == []`; the same mutation flags 3 of 3 requested dependent kinds
(outcome_result, manuscript_result_sentence, certificate), plus membership states.
The censoring-only mutation flags the consumed outcome result without changing numbers.
Post measurements explicitly discard old hash-schema receipts on the scratch copy
and stamp the unchanged baseline before mutation; `check()` never refreshes stamps.

Plant (a): include -> retain / OUTCOME_ASCERTAINMENT_UNRESOLVED / OPEN obligation.
Plant (b): include -> include; this snapshot already has `title_independent: true`,
so the earlier audit's title-only failure was not reproduced here.
Initial plant (c) changed the numeric row scale to RR and was refused both before
and after for missing censoring evidence. The stricter canonical-estimand plant
preserves the HR row and changes `effect_object.canonical_estimand` to RISK_RATIO
while `study_effect.estimand` stays HR: **1 of 1 accepted, 0 of 1 refused**.
That stricter plant was measured after the edits; there is no fabricated pre-fix
capture for it. Effect-type admission code was not changed in this lane.

## Remaining work / INFERRED integration blockers

1. The requested AUD1 admissibility verdict API was not found in this snapshot.
   The existing effect-type route ignores the canonical-estimand contradiction.
   Integrate the AUD1 verdict and enforce the primary HR constraint there; no
   parallel verdict was invented. Until then the binding clause is not marked IMPLEMENTED.
2. The generic clause inventory is deliberately conservative. Unmapped material
   clauses are UNIMPLEMENTED and several clinical axes require adjudication;
   absence of config contradictions is not proof of implementation.
3. Real records without explicit ascertainment evidence are retained and withheld.
   Their held registry/protocol/methods evidence still needs adjudication and
   integration. No favorable pool size was preserved by assuming eligibility.
4. The two bounded build/gate attempts and their failures are recorded below.
   An unsuccessful rebuild cannot establish that the served page has the new table
   or that the issued release certificate is current. The old served artefacts
   must not be described as passing this lane.

## Static versus dynamic disclosure

| Item | Static | Dynamic / source |
|---|---|---|
| Protocol | Supported syntax, axis operators, status vocabulary | Held protocol text and config; verbatim spans |
| Delivery | Parser for explicit declaration syntax | Protocol IDs and configured membership rules |
| Dependency | SHA-256 canonicalization, scientific field names | Rows, source spans, provenance, adjudications, axis values |
| Plants | Synthetic record wording and deliberate mutations | Copies of actual topic/review; no invented research output |
| Results | No hardcoded HRs, Ns, p-values or rankings added | Existing source-backed inputs and production computations |

## Final requested test run — MEASURED

Command: `python tests/aud3_suite.py` (expands all requested test file patterns).

```text
........................................................................ [ 73%]
..........................                                               [100%]
98 passed in 39.71s
```

## Pre-fix plants — verbatim JSON

```json
{
  "a": [
    {
      "id": "AUD3-SYNTHETIC",
      "id_type": "pmid",
      "label": "",
      "decision": "include",
      "rule_id": "INCLUDE",
      "reason": "eligible randomised controlled trial: intervention semaglutide, comparator placebo, population type 2 diabetes — P/I/C/design met.",
      "span": "population “Semaglutide in type 2 diabetes An open-label randomize…”; comparator “…l of semaglutide versus placebo. HbA1c only. Randomized…”",
      "matched_intervention": "semaglutide"
    }
  ],
  "b": [
    {
      "id": "AUD3-SYNTHETIC",
      "id_type": "pmid",
      "label": "",
      "decision": "include",
      "rule_id": "INCLUDE",
      "reason": "eligible randomised controlled trial: intervention semaglutide, comparator placebo, population type 2 diabetes — P/I/C/design met.",
      "span": "population “…evaluation Adults with type 2 diabetes randomly assigned semag…”; comparator “…assigned semaglutide or placebo, double-blind. 3-point…”",
      "matched_intervention": "semaglutide"
    }
  ],
  "comparison": [],
  "gi_name": "Gastrointestinal adverse events",
  "gi_hash_changed": true,
  "gi_check": [],
  "censoring_check": [],
  "c": {
    "kept": 0,
    "refused": 1,
    "reason": [
      "UNTYPED — axis 8 unknown: NO_ROW_EVIDENCE"
    ]
  }
}
```

## Post-fix plants — verbatim JSON

```json
{
  "a": [
    {
      "id": "AUD3-SYNTHETIC",
      "id_type": "pmid",
      "label": "",
      "decision": "retain",
      "rule_id": "OUTCOME_ASCERTAINMENT_UNRESOLVED",
      "reason": "RETAINED: OUTCOME_ASCERTAINMENT UNRESOLVED; OPEN obligation: Locate held registry design outcomes, protocol/SAP or publication methods evidence.",
      "span": "population “Semaglutide in type 2 diabetes An open-label randomize…”; comparator “…l of semaglutide versus placebo. HbA1c only. Randomized…”",
      "eligibility_axes": {
        "OUTCOME_ASCERTAINMENT": {
          "status": "UNRESOLVED",
          "span": "",
          "obligation": {
            "status": "OPEN",
            "axis": "OUTCOME_ASCERTAINMENT",
            "action": "Locate held registry design outcomes, protocol/SAP or publication methods evidence."
          }
        }
      },
      "open_obligations": [
        {
          "status": "OPEN",
          "axis": "OUTCOME_ASCERTAINMENT",
          "action": "Locate held registry design outcomes, protocol/SAP or publication methods evidence."
        }
      ],
      "matched_intervention": "semaglutide"
    }
  ],
  "b": [
    {
      "id": "AUD3-SYNTHETIC",
      "id_type": "pmid",
      "label": "",
      "decision": "include",
      "rule_id": "INCLUDE",
      "reason": "eligible randomised controlled trial: intervention semaglutide, comparator placebo, population type 2 diabetes — P/I/C/design met.",
      "span": "population “…evaluation Adults with type 2 diabetes randomly assigned semag…”; comparator “…assigned semaglutide or placebo, double-blind. 3-point…”",
      "eligibility_axes": {
        "OUTCOME_ASCERTAINMENT": {
          "status": "ESTABLISHED",
          "span": "Adults with type 2 diabetes randomly assigned semaglutide or placebo, double-blind. 3-point MACE was prospectively specified and systematically ascertained."
        }
      },
      "matched_intervention": "semaglutide"
    }
  ],
  "comparison": [
    {
      "code": "OUTCOME_ASCERTAINMENT_DIVERGENCE",
      "dimension": "eligibility",
      "prose": "Outcome ascertainment is an eligibility axis; outcome result availability is not.",
      "config": "RCT; adults with type 2 diabetes by title/registry conditions; GLP-1 receptor agonist vs placebo; double-blind placebo-controlled CV outcome trial. P/I/C/design only."
    }
  ],
  "baseline_check": [],
  "gi_name": "Gastrointestinal adverse events",
  "gi_hash_changed": true,
  "gi_check": [
    {
      "code": "STALE_DEPENDENT",
      "kind": "membership_state",
      "claim_id": "8fb160e6ea815d47",
      "detail": "/outcomes/1/declared_absent_trials/0 depends on be825178380911cdb48d2e0dc315da69a03af6cb13a7d4b70913f1fd0fde8941, current input_set_version is 2951b7ab94ac841559265f40209b3a63154ab3bd669c873f160562da1d478ab5",
      "object_path": "/outcomes/1/declared_absent_trials/0"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "membership_state",
      "claim_id": "8fb160e6ea815d47",
      "detail": "/outcomes/1/declared_absent_trials/1 depends on be825178380911cdb48d2e0dc315da69a03af6cb13a7d4b70913f1fd0fde8941, current input_set_version is 2951b7ab94ac841559265f40209b3a63154ab3bd669c873f160562da1d478ab5",
      "object_path": "/outcomes/1/declared_absent_trials/1"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "membership_state",
      "claim_id": "8fb160e6ea815d47",
      "detail": "/outcomes/1/declared_absent_trials/2 depends on be825178380911cdb48d2e0dc315da69a03af6cb13a7d4b70913f1fd0fde8941, current input_set_version is 2951b7ab94ac841559265f40209b3a63154ab3bd669c873f160562da1d478ab5",
      "object_path": "/outcomes/1/declared_absent_trials/2"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "membership_state",
      "claim_id": "8fb160e6ea815d47",
      "detail": "/outcomes/1/declared_absent_trials/3 depends on be825178380911cdb48d2e0dc315da69a03af6cb13a7d4b70913f1fd0fde8941, current input_set_version is 2951b7ab94ac841559265f40209b3a63154ab3bd669c873f160562da1d478ab5",
      "object_path": "/outcomes/1/declared_absent_trials/3"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "membership_state",
      "claim_id": "8fb160e6ea815d47",
      "detail": "/outcomes/1/declared_absent_trials/4 depends on be825178380911cdb48d2e0dc315da69a03af6cb13a7d4b70913f1fd0fde8941, current input_set_version is 2951b7ab94ac841559265f40209b3a63154ab3bd669c873f160562da1d478ab5",
      "object_path": "/outcomes/1/declared_absent_trials/4"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "membership_state",
      "claim_id": "8fb160e6ea815d47",
      "detail": "/outcomes/1/declared_absent_trials/5 depends on be825178380911cdb48d2e0dc315da69a03af6cb13a7d4b70913f1fd0fde8941, current input_set_version is 2951b7ab94ac841559265f40209b3a63154ab3bd669c873f160562da1d478ab5",
      "object_path": "/outcomes/1/declared_absent_trials/5"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "membership_state",
      "claim_id": "8fb160e6ea815d47",
      "detail": "/outcomes/1/declared_absent_trials/6 depends on be825178380911cdb48d2e0dc315da69a03af6cb13a7d4b70913f1fd0fde8941, current input_set_version is 2951b7ab94ac841559265f40209b3a63154ab3bd669c873f160562da1d478ab5",
      "object_path": "/outcomes/1/declared_absent_trials/6"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "membership_state",
      "claim_id": "8fb160e6ea815d47",
      "detail": "/outcomes/1/declared_absent_trials/7 depends on be825178380911cdb48d2e0dc315da69a03af6cb13a7d4b70913f1fd0fde8941, current input_set_version is 2951b7ab94ac841559265f40209b3a63154ab3bd669c873f160562da1d478ab5",
      "object_path": "/outcomes/1/declared_absent_trials/7"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "membership_state",
      "claim_id": "8fb160e6ea815d47",
      "detail": "/outcomes/1/declared_absent_trials/8 depends on be825178380911cdb48d2e0dc315da69a03af6cb13a7d4b70913f1fd0fde8941, current input_set_version is 2951b7ab94ac841559265f40209b3a63154ab3bd669c873f160562da1d478ab5",
      "object_path": "/outcomes/1/declared_absent_trials/8"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "membership_state",
      "claim_id": "8fb160e6ea815d47",
      "detail": "/outcomes/1/declared_absent_trials/9 depends on be825178380911cdb48d2e0dc315da69a03af6cb13a7d4b70913f1fd0fde8941, current input_set_version is 2951b7ab94ac841559265f40209b3a63154ab3bd669c873f160562da1d478ab5",
      "object_path": "/outcomes/1/declared_absent_trials/9"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "outcome_result",
      "claim_id": "b0e4b67c2084a7e4",
      "detail": "/outcomes/1/result depends on be825178380911cdb48d2e0dc315da69a03af6cb13a7d4b70913f1fd0fde8941, current input_set_version is 2951b7ab94ac841559265f40209b3a63154ab3bd669c873f160562da1d478ab5",
      "object_path": "/outcomes/1/result"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "manuscript_result_sentence",
      "claim_id": "b7f47f6d437b711d",
      "detail": "/claimgraph/objects/1 depends on 029ee579a3930601ba3c38bb45c43356653def4e283d8a4bf8a7dad83b787304, current input_set_version is fd33e963b3da91b0e42b1d43f36ddb9f051010a8804f73fa78c3583a92d0b93f",
      "object_path": "/claimgraph/objects/1"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "certificate",
      "claim_id": "88f84473920899c7",
      "detail": "/dependency_certificate depends on 029ee579a3930601ba3c38bb45c43356653def4e283d8a4bf8a7dad83b787304, current input_set_version is fd33e963b3da91b0e42b1d43f36ddb9f051010a8804f73fa78c3583a92d0b93f",
      "object_path": "/dependency_certificate"
    }
  ],
  "censoring_check": [
    {
      "code": "STALE_DEPENDENT",
      "kind": "membership_state",
      "claim_id": "a1ee786b50c27592",
      "detail": "/outcomes/0/declared_absent_trials/0 depends on 41d30a3457b4686ae12a744442ec8d11aacf1c43c6354b3c1c0a93de67f351e3, current input_set_version is e01f12ea81ed88800eac8cd56431b509a0e5e35bc708073ee205e9a53cae752d",
      "object_path": "/outcomes/0/declared_absent_trials/0"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "membership_state",
      "claim_id": "a1ee786b50c27592",
      "detail": "/outcomes/0/declared_absent_trials/1 depends on 41d30a3457b4686ae12a744442ec8d11aacf1c43c6354b3c1c0a93de67f351e3, current input_set_version is e01f12ea81ed88800eac8cd56431b509a0e5e35bc708073ee205e9a53cae752d",
      "object_path": "/outcomes/0/declared_absent_trials/1"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "membership_state",
      "claim_id": "a1ee786b50c27592",
      "detail": "/outcomes/0/declared_absent_trials/2 depends on 41d30a3457b4686ae12a744442ec8d11aacf1c43c6354b3c1c0a93de67f351e3, current input_set_version is e01f12ea81ed88800eac8cd56431b509a0e5e35bc708073ee205e9a53cae752d",
      "object_path": "/outcomes/0/declared_absent_trials/2"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "outcome_result",
      "claim_id": "a8896b828feef4b9",
      "detail": "/outcomes/0/result depends on 41d30a3457b4686ae12a744442ec8d11aacf1c43c6354b3c1c0a93de67f351e3, current input_set_version is e01f12ea81ed88800eac8cd56431b509a0e5e35bc708073ee205e9a53cae752d",
      "object_path": "/outcomes/0/result"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "rob_sensitivity.full",
      "claim_id": "1aa03085f4b53de8",
      "detail": "/rob_sensitivity/full depends on 41d30a3457b4686ae12a744442ec8d11aacf1c43c6354b3c1c0a93de67f351e3, current input_set_version is e01f12ea81ed88800eac8cd56431b509a0e5e35bc708073ee205e9a53cae752d",
      "object_path": "/rob_sensitivity/full"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "rob_sensitivity.drop_high",
      "claim_id": "134286a6ea177bf5",
      "detail": "/rob_sensitivity/drop_high depends on 41d30a3457b4686ae12a744442ec8d11aacf1c43c6354b3c1c0a93de67f351e3, current input_set_version is e01f12ea81ed88800eac8cd56431b509a0e5e35bc708073ee205e9a53cae752d",
      "object_path": "/rob_sensitivity/drop_high"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "rob_sensitivity.low_only",
      "claim_id": "082daf3be03022e1",
      "detail": "/rob_sensitivity/low_only depends on 41d30a3457b4686ae12a744442ec8d11aacf1c43c6354b3c1c0a93de67f351e3, current input_set_version is e01f12ea81ed88800eac8cd56431b509a0e5e35bc708073ee205e9a53cae752d",
      "object_path": "/rob_sensitivity/low_only"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "grade",
      "claim_id": "7b44c30c819b82ac",
      "detail": "/grade depends on 41d30a3457b4686ae12a744442ec8d11aacf1c43c6354b3c1c0a93de67f351e3, current input_set_version is e01f12ea81ed88800eac8cd56431b509a0e5e35bc708073ee205e9a53cae752d",
      "object_path": "/grade"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "rob_sensitivity_prose",
      "claim_id": "cbf433ef478d859f",
      "detail": "/claimgraph/objects/0 depends on 41d30a3457b4686ae12a744442ec8d11aacf1c43c6354b3c1c0a93de67f351e3, current input_set_version is e01f12ea81ed88800eac8cd56431b509a0e5e35bc708073ee205e9a53cae752d",
      "object_path": "/claimgraph/objects/0"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "manuscript_result_sentence",
      "claim_id": "b7f47f6d437b711d",
      "detail": "/claimgraph/objects/1 depends on 029ee579a3930601ba3c38bb45c43356653def4e283d8a4bf8a7dad83b787304, current input_set_version is 0cc916998eeabbc730d60880db26360e12e28f58a35f6770d79824e7ce90bb1a",
      "object_path": "/claimgraph/objects/1"
    },
    {
      "code": "STALE_DEPENDENT",
      "kind": "certificate",
      "claim_id": "88f84473920899c7",
      "detail": "/dependency_certificate depends on 029ee579a3930601ba3c38bb45c43356653def4e283d8a4bf8a7dad83b787304, current input_set_version is 0cc916998eeabbc730d60880db26360e12e28f58a35f6770d79824e7ce90bb1a",
      "object_path": "/dependency_certificate"
    }
  ],
  "c": {
    "kept": 0,
    "refused": 1,
    "reason": [
      "UNTYPED — axis 8 unknown: NO_ROW_EVIDENCE"
    ]
  },
  "c_canonical_mismatch": {
    "kept": 1,
    "refused": 0,
    "reason": []
  }
}
```

## Second offline build and gate — verbatim output

Command: `python tests/aud3_verify.py`, invoking production
`build_topic.main('glp1-ra-mace-t2d', '2026-09-11')` and `gate_page` with sockets blocked.
First attempt: `.tmp/aud3-build-gate-attempt1.txt`.

```text
Traceback (most recent call last):
  File "C:\mh-r-AUD3\tests\aud3_verify.py", line 24, in <module>
    main('glp1-ra-mace-t2d', '2026-09-11')
    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\mh-r-AUD3\scripts\build_topic.py", line 68, in main
    manifest = build_review_dir(core, manifest_meta, review_dir, protocol_sha, from_cache=True, certify=True)
  File "C:\mh-r-AUD3\harness\census.py", line 198, in build_review_dir
    _pa = membership.annotate_parity(_parity_row(_root, manifest_meta.get("slug", ""), review_core_obj), review_core_obj)
                                     ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\mh-r-AUD3\harness\census.py", line 115, in _parity_row
    return parity_relation.enrich(row, review_core_obj)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "C:\mh-r-AUD3\harness\parity_relation.py", line 239, in enrich
    raise ValueError(
    ...<3 lines>...
    )
ValueError: PARITY-RELATION REFUSED: hand status 'OVERLAPPING' disagrees with computed relation DISTINCT for glp1-ra-mace-t2d
BUILD_EXIT=1
GATE {
  "pass": false,
  "reasons": [
    "L1: live census reproduced 2 failure(s): served index.html byte-matches re-render of review.json; typed claim registry covers served prose and validates its objects",
    "CERTIFICATE.json release_sha256 mismatch: recomputed d4500d8d6b1fa9d9985c2c7e8990e8b3aec91328b15111a5a78ddd2e51858654 vs saved 9c9edd5cd8fcdd6ad5a0f48150aa4fbcef93b7c4cd3b178f8e02523f553aa40f",
    "L1: offline replay does NOT regenerate the committed numbers (replay 1094f85903734bce22807ac34fe3a5f73ca9861b11a49f1530d7c6c0ec36bab5 vs committed 53eabecbfa8e42355e0777fa8a461355e3a23b8c3241225ef587258e0cb60c9b)",
    "GS: statistical layer objects missing or not re-derivable",
    "GS: REFUSED envelope/fragility rendering not generated from re-derived objects",
    "GS: REFUSED unbound envelope/fragility sentence outside object rendering",
    "GS: envelope cache missing or differs from re-derived object",
    "GS: fragility cache missing or differs from re-derived object",
    "GS: decomposer cache missing or differs from re-derived object",
    "L1: claimgraph violations remain (stale dependent result-bearing object): [{\"code\": \"STALE_DEPENDENT\", \"kind\": \"membership_state\", \"claim_id\": \"da1d3407c129708f\", \"detail\": \"/outcomes/0/declared_absent_trials/0 depends on 08571245581e61bd47ef44b859d7e75276157a8c7280f8cbab3235616dabfc18, current input_set_version is 41d30a3457b4686ae12a744442ec8d11aacf1c43c6354b3c1c0a93de67f351e3\", \"object_path\": \"/outcomes/0/declared_absent_trials/0\"}, {\"code\": \"STALE_DEPENDENT\", \"kind\": \"membership_state\", \"claim_id\": \"da1d3407c129708f\", \"detail\": \"/outcomes/0/declared_absent_trials/1 depends on 08571245581e61bd47ef44b859d7e75276157a8c7280f8cbab3235616dabfc18, current input_set_version is 41d30a3457b4686ae12a744442ec8d11aacf1c43c6354b3c1c0a93de67f351e3\", \"object_path\": \"/outcomes/0/declared_absent_trials/1\"}, {\"code\": \"STALE_DEPENDENT\", \"kind\": \"membership_state\", \"claim_id\": \"da1d3407c129708f\", \"detail\": \"/outcomes/0/declared_absent_trials/2 depends on 08571245581e61bd47ef44b859d7e75276157a8c7280f8cbab3235616dabfc18, current input_set_version is 41d30a3457b4686ae12a744442ec8d11aacf1c43c6354b3c1c0a93de67f351e3\", \"object_path\": \"/outcomes/0/declared_absent_trials/2\"}, {\"code\": \"STALE_DEPENDENT\", \"kind\": \"membership_state\", \"claim_id\": \"da1d3407c129708f\", \"detail\": \"/outcomes/0/effect_type_refusals/0 depends on 08571245581e61bd47ef44b859d7e75276157a8c7280f8cbab3235616dabfc18, current input_set_version is 41d30a3457b4686ae12a744442ec8d11aacf1c43c6354b3c1c0a93de67f351e3\", \"object_path\": \"/outcomes/0/effect_type_refusals/0\"}, {\"code\": \"STALE_DEPENDENT\", \"kind\": \"membership_state\", \"claim_id\": \"da1d3407c129708f\", \"detail\": \"/outcomes/0/effect_type_refusals/1 depends on 08571245581e61bd47ef44b859d7e75276157a8c7280f8cbab3235616dabfc18, current input_set_version is 41d30a3457b4686ae12a744442ec8d11aacf1c43c6354b3c1c0a93de67f351e3\", \"object_path\": \"/outcomes/0/effect_type_refusals/1\"}, {\"code\": \"STALE_DEPENDENT\", \"kind\": \"membership_state\", \"claim_id\": \"da1d3407c129708f\", \"detail\": \"/outcomes/0/effect_type_refusals/2 depends on 08571245581e61bd47ef44b859d7e75276157a8c7280f8cbab3235616dabfc18, current input_set_version is 41d30a3457b4686ae12a744442ec8d11aacf1c43c6354b3c1c0a93de67f351e3\", \"object_path\": \"/outcomes/0/effect_type_refusals/2\"}]",
    "L1: TRANSFORMATION_MISMATCH outcome-pool-fa86d769130b8e1d1f74: ",
    "L1: TRANSFORMATION_MISMATCH outcome-pool-a9128e6d180a88bc2c08: "
  ]
}
```

CLAIMED: no release-ready, whole-protocol-implemented, all-plants-passed, or gate-PASS claim.
