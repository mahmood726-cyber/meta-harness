# Scorecard adjudication before/after per gate

Base commit: 3aedba0ecef0969551c761c8e91e29dccec88124

If the same environment labels its own gate outputs true or false, that is: system produces output -> system labels its own output correct -> agreement read as validation (the 6/6 recall shape). So every refusal is an EVENT with an ADJUDICATION OBJECT, and a gate's numbers are computed only from those objects.

Migration counts: 84 v1 rows before, 89 v2 events after; UNRESOLVED 36 before, 56 after; harvest added 5 and enriched 1.

| gate | v1 status | events | TP | FP | UNRESOLVED | precision | coverage |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| `census.claim_check` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `census.compatibility_check` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `census.interval_provenance` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `census.proposition_check` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `deploy.attest` | NO_VALIDATION/UNVALIDATED/precision=null | 2 | 0 | 0 | 2 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `deploy.check_artifact` | PLANT_ONLY/UNVALIDATED/precision=null | 3 | 0 | 0 | 2 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `evidence_index.check` | NO_VALIDATION/UNVALIDATED/precision=null | 1 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_access_claim_supported` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_cache_tracked` | NO_VALIDATION/UNVALIDATED/precision=null | 1 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_controls` | PLANT_ONLY/UNVALIDATED/precision=null | 3 | 0 | 0 | 2 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_cross_source` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_duplicate_publication` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_fetch_complete` | PLANT_ONLY/UNVALIDATED/precision=null | 3 | 0 | 0 | 2 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_limb1` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_limb2` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_manuscript_numbers` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_method_matches_scale` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_no_double_counted_trial` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_parity_our_k` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_pivotal_present` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_pooled_verified` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_population_identity` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_preregistration_not_build` | NO_VALIDATION/UNVALIDATED/precision=null | 1 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_prespecification_in_protocol` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_primary_result` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_reproduction` | NO_VALIDATION/UNVALIDATED/precision=null | 1 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `gate.check_retraction` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `honest_ratchet.compare_blocks` | PLANT_ONLY/UNVALIDATED/precision=null | 3 | 0 | 0 | 2 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `hook.commit_msg` | PRODUCTION/EXERCISED/precision=1.0 | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `hook.pre_commit` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `pipeline.structural_query_classifier` | PLANT_ONLY/UNVALIDATED/precision=null | 3 | 0 | 0 | 2 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `ruleset.required_verify` | PRODUCTION/EXERCISED/precision=1.0 | 3 | 0 | 0 | 3 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `verify_all.limb_fixstate` | PRODUCTION/EXERCISED/precision=0.5 | 5 | 0 | 0 | 4 | null: no adjudicated production refusal - UNVALIDATED, not green | 0.000 |
| `verify_all.limb_gate_every_page` | NO_VALIDATION/UNVALIDATED/precision=null | 1 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `verify_all.limb_gate_scorecard` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `verify_all.limb_heldout` | PRODUCTION/EXERCISED/precision=1.0 | 3 | 0 | 0 | 2 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `verify_all.limb_honest_ratchet` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `verify_all.limb_index_currency` | PRODUCTION/EXERCISED/precision=1.0 | 4 | 0 | 0 | 3 | null: no adjudicated production refusal - UNVALIDATED, not green | 0.000 |
| `verify_all.limb_leak_scan` | PLANT_ONLY/UNVALIDATED/precision=null | 2 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `verify_all.limb_reproduction` | NO_VALIDATION/UNVALIDATED/precision=null | 1 | 0 | 0 | 1 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |
| `verify_all.limb_unit_tests` | PLANT_ONLY/UNVALIDATED/precision=null | 3 | 0 | 0 | 2 | null: no adjudicated production refusal - UNVALIDATED, not green | null: no production refusals |

Gates that lost apparent precision because the v1 rows named no adjudicator object:
- `hook.commit_msg`
- `ruleset.required_verify`
- `verify_all.limb_fixstate`
- `verify_all.limb_heldout`
- `verify_all.limb_index_currency`
