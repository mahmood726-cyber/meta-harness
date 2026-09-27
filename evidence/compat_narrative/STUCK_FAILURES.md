# Unresolved verification failures

No release or ship claim. Only the requested new file and existing tests for changed modules were run.

| Test | Fails without change? | Reason |
|---|---|---|
| `tests.test_compat_underlying::test_post_fix_probiotics_key_is_mixed_and_no_asserted_violation` | Yes | FileNotFoundError: [Errno 2] No such file or directory: 'docs/reviews/probiotics-aad-prevention/review.json' |
| `tests.test_compat_underlying::test_pre_fix_probiotics_key_fires_on_underlying_trial_rows` | No | AssertionError: assert {'analysis_se...ow_up_window'} <= {'analysis_set', 'endpoint'}      Extra items in the left set:   'follow_up_window' |
| `tests.test_compat_underlying::test_risk_and_prevention_endpoint_refusal_persists` | Yes | FileNotFoundError: [Errno 2] No such file or directory: 'docs/reviews/omega3-cardiovascular-events/review.json' |
| `tests.test_grade_residue_not_rendered::test_fully_assessed_grade_keeps_its_arithmetic` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\reviews\\glp1-ra-mace-t2d\\review.json' |
| `tests.test_grade_residue_not_rendered::test_glp1_provisional_grade_renders_no_arithmetic_residue` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\reviews\\glp1-ra-mace-t2d\\review.json' |
| `tests.test_hm3_pages::test_primary_trial_values_and_membership_are_unchanged` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\evidence\\hm3-held-source-audit\\baseline-debt.json' |
| `tests.test_hm3_pages::test_rebuilt_pages_account_for_every_baseline_harm` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\evidence\\hm3-held-source-audit\\decisions.json' |
| `tests.test_hm3_pages::test_retained_aact_rows_match_audit_hashes` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\evidence\\hm3-held-source-audit\\aact\\manifest.json' |
| `tests.test_page_tabs_layout::test_plant_a_click_that_does_not_scroll_is_named` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\reviews\\glp1-ra-mace-t2d\\index.html' |
| `tests.test_page_tabs_layout::test_plant_a_hidden_tab_heading_is_named` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\reviews\\glp1-ra-mace-t2d\\index.html' |
| `tests.test_page_tabs_layout::test_plant_a_verifier_line_naming_other_bytes_is_named` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\reviews\\glp1-ra-mace-t2d\\index.html' |
| `tests.test_page_tabs_layout::test_plant_the_family_ledger_outside_screening_is_named` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\reviews\\glp1-ra-mace-t2d\\index.html' |
| `tests.test_page_tabs_layout::test_plant_the_old_layout_certificate_above_the_tabs_is_named` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\reviews\\glp1-ra-mace-t2d\\index.html' |
| `tests.test_page_tabs_layout::test_there_are_served_pages` | Yes | assert 0 >= 32  +  where 0 = len([])  +    where [] = _pages() |
| `tests.test_page_verifier::test_auditor_limit_a_page_and_manifest_changed_together_still_pass` | Yes | failed on setup with "FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\scripts\\audit_certificate_stdlib.py'" |
| `tests.test_page_verifier::test_auditor_reads_the_certificate_its_three_siblings_and_the_pinned_code_and_nothing_else` | Yes | failed on setup with "FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\scripts\\audit_certificate_stdlib.py'" |
| `tests.test_page_verifier::test_auditor_refuses_a_changed_pinned_module_but_not_a_correct_looking_wrong_one` | Yes | failed on setup with "FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\scripts\\audit_certificate_stdlib.py'" |
| `tests.test_page_verifier::test_auditor_refuses_each_broken_link_beside_the_certificate[embedded_certificate]` | Yes | failed on setup with "FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\scripts\\audit_certificate_stdlib.py'" |
| `tests.test_page_verifier::test_auditor_refuses_each_broken_link_beside_the_certificate[forged_certificate]` | Yes | failed on setup with "FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\scripts\\audit_certificate_stdlib.py'" |
| `tests.test_page_verifier::test_auditor_refuses_each_broken_link_beside_the_certificate[manifest_review]` | Yes | failed on setup with "FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\scripts\\audit_certificate_stdlib.py'" |
| `tests.test_page_verifier::test_auditor_refuses_each_broken_link_beside_the_certificate[page_byte]` | Yes | failed on setup with "FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\scripts\\audit_certificate_stdlib.py'" |
| `tests.test_page_verifier::test_auditor_refuses_each_broken_link_beside_the_certificate[page_prints_other_release]` | Yes | failed on setup with "FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\scripts\\audit_certificate_stdlib.py'" |
| `tests.test_page_verifier::test_auditor_refuses_each_broken_link_beside_the_certificate[served_number]` | Yes | failed on setup with "FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\scripts\\audit_certificate_stdlib.py'" |
| `tests.test_page_verifier::test_auditor_without_the_siblings_says_the_links_were_not_checked` | Yes | failed on setup with "FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\scripts\\audit_certificate_stdlib.py'" |
| `tests.test_page_verifier::test_blind_pages_do_not_name_a_verifier` | Yes | AssertionError: no blind pages found -- the check would be vacuous assert [] |
| `tests.test_page_verifier::test_bundle_verifier_never_reads_the_page_and_recomputes_only_the_primary_pool` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\scripts\\verify_bundle.py' |
| `tests.test_page_verifier::test_each_served_verifier_is_byte_identical_to_its_source` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\scripts\\audit_certificate_stdlib.py' |
| `tests.test_page_verifier::test_every_served_review_page_names_a_verifier_that_matches_the_served_bytes` | Yes | FileNotFoundError: [WinError 3] The system cannot find the path specified: '<worktree>\\docs\\reviews' |
| `tests.test_page_verifier::test_loading_a_served_verifier_writes_nothing_under_docs` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\scripts\\audit_certificate_stdlib.py' |
| `tests.test_page_verifier::test_plant_a_changed_verifier_byte_changes_the_page` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\scripts\\audit_certificate_stdlib.py' |
| `tests.test_page_verifier::test_plant_a_page_with_no_certificate_says_no_verifier_is_named` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\reviews\\pcsk9-mace\\review.json' |
| `tests.test_page_verifier::test_plant_a_verifier_with_no_stated_limits_is_named_as_a_problem` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\scripts\\audit_certificate_stdlib.py' |
| `tests.test_page_verifier::test_plant_an_unserved_verifier_is_named_as_a_problem` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\reviews\\pcsk9-mace\\review.json' |
| `tests.test_page_verifier::test_the_verifier_block_is_not_a_tracked_limitation_block` | Yes | FileNotFoundError: [Errno 2] No such file or directory: '<worktree>\\docs\\reviews\\glp1-ra-mace-t2d\\review.json' |
| `tests.test_page_verifier::test_there_are_served_pages_to_check` | Yes | FileNotFoundError: [WinError 3] The system cannot find the path specified: '<worktree>\\docs\\reviews' |

The added legacy failure is `test_pre_fix_probiotics_key_fires_on_underlying_trial_rows`: it expects broad abstract/audit-derived follow-up and endpoint prose. That fallback is intentionally removed; unbound values are now reported as underivable. The test also expects the audit annotation wording `otherwise-unexplained`, rather than an input-bound description. Existing tests were left unchanged.

Baseline failures concern absent served pages/review/evidence artifacts and verifier fixture permissions in this worktree. They were reproduced before the change. See verification.json for all case-level statuses.
