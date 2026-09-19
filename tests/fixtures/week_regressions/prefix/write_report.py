from pathlib import Path
import subprocess
import hashlib
import json

root = Path.cwd()
evidence = root / '.tmp/prefix'
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()

def read(name):
    p = evidence / name
    return p.read_text(encoding='utf-8') if p.exists() else 'PENDING: ' + name

def summary(name):
    lines = read(name).splitlines()
    return next((line for line in reversed(lines) if ' passed' in line or ' failed' in line), 'PENDING')

def counts(name):
    tokens = summary(name).replace(',', '').split()
    measured = {tokens[i + 1]: int(word) for i, word in enumerate(tokens[:-1]) if word.isdigit() and tokens[i + 1] in {'passed', 'failed', 'xfailed', 'skipped'}}
    total = sum(measured.values())
    return '; '.join(f'{count} of {total} {state}' for state, count in measured.items()) or 'PENDING'

rows = [
('AUD 1: harm endpoint specificity', 'harness/harms.py:reporting_signal', 'UNFIXED', 'harms::test_generic_adverse_events_do_not_prove_specific_harm', "AssertionError: assert {'kind': 'term_signal', 'reported': True, 'span': 'Serious adverse events were similar between the two groups.'} is None", 'strict xfail; patched-copy PASS', '.tmp/patches/harm-endpoint.diff'),
('AUD 2: family/report collision', 'harness/known_missing.py:_missing_candidates', 'UNFIXED', 'missing::test_missing_candidates_merge_family_and_report_identity', 'AssertionError: one family must not be counted twice', 'strict xfail; patched-copy PASS', '.tmp/patches/missing-family.diff'),
('AUD 3: stale comparator overlap', 'harness/comparator_second_pass.py:parse_trial_set/apply', 'UNFIXED', 'overlap::test_comparator_only_text_cannot_establish_current_pool_overlap', 'AssertionError: current pool is not an input to this parser', 'strict xfail; patched-copy PASS', '.tmp/patches/comparator-overlap.diff'),
('AUD 4: title omission becomes ineligibility', 'harness/screen.py:screen_record', 'UNFIXED', 'screening::test_title_omission_requires_review_not_ineligibility', "assert 'exclude' != 'exclude'", 'strict xfail; patched-copy PASS', '.tmp/patches/screen-title.diff'),
('AUD 5: substring adjustment labels', 'harness/design_key.py:key_for_trial', 'FIXED@3f8add72', 'adjustment::test_adjustment_plant_fires_on_pinned_parent / test_adjustment_labels_require_estimator_evidence', 'AssertionError', 'pinned-parent fires; live PASS', 'tests + .tmp/prefix/adjustment/design_key.py'),
('AUD 6: unlocated effect-type binding', 'harness/effect_type.py:check_review', 'NOT PRESENT ON BASE', 'none', 'No such module on this checkout', 'NOT CLAIMED', 'none'),
('AUD 7: different endpoint used as held MACE evidence', 'harness/reason_audit.py:find_value_in_sources', 'UNFIXED', 'reason::test_kidney_and_cv_death_values_do_not_prove_mace_value', 'AssertionError (complete output in owner-before appendix)', 'strict xfail; patched-copy PASS', '.tmp/patches/reason-endpoint.diff'),
('AUD 8: cached query contract', 'harness/fetch.py:ensure', 'UNFIXED; bounded subcase', 'search_contract::test_cached_queries_must_match_requested_contract', "Failed: DID NOT RAISE <class 'ValueError'>", 'strict xfail; patched-copy PASS', '.tmp/patches/search-contract.diff'),
('AUD 9: composite disclosure uses unselected abstract', 'harness/pipeline.py:composite disclosure block', 'UNFIXED', 'composite::test_selected_endpoint_controls_composite_warning', 'AssertionError (complete output in owner-before appendix)', 'strict xfail; patched-copy PASS', '.tmp/patches/composite-selection.diff'),
('Publication-bias assertion literal', 'harness/manuscript.py:render', 'FIXED@04902ecf', 'publication_bias::test_publication_bias_plant_fires_on_pinned_parent / test_missing_publication_bias_object_cannot_be_claimed_assessed', 'AssertionError', 'pinned-parent fires; live PASS', 'tests + .tmp/prefix/publication/manuscript.py'),
('Unconditional compatibility success', 'harness/compat_check.py:enrich', 'UNFIXED', 'assertion_status::test_compatibility_status_reflects_remaining_violations', 'assert True is False', 'PASS after source repair', 'harness/compat_check.py'),
('Unconditional proposition success', 'harness/propositions.py:check_document', 'UNFIXED', 'assertion_status::test_proposition_status_reflects_contradictions', 'assert True is False', 'PASS after source repair', 'harness/propositions.py'),
('Unsupported generated_on stamp', 'docs/model_stage_inventory.json', 'UNFIXED', 'generation_stamp::test_inventory_stamp_has_build_input_provenance', 'AssertionError: generated_on lacks a build-input binding', 'strict xfail; withdrawal patch PASS', '.tmp/patches/generated-on.diff'),
('Live run assigned sealed historical date', 'scripts/search_v2_run.py:main/refresh/_candidate_path; scripts/search_v2_run_evidence.py:main/update_fixes', 'UNFIXED', 'dates::test_refresh_cli_uses_explicit_current_date / test_refresh_refuses_stale_date_before_io / test_dated_label_is_not_prefixed_with_first_run_date', 'SystemExit: 2; TypeError: refresh() got an unexpected keyword argument; AssertionError (full output below)', 'PASS after source repair', 'scripts/search_v2_run.py; scripts/search_v2_run_evidence.py'),
('Sealed first run reruns on a later date', 'scripts/measure_search_v2_measurement.py:refresh_measurement', 'UNFIXED', 'dates::test_sealed_first_run_refuses_later_clock_before_io / test_sealed_artifact_identity_does_not_follow_clock', 'Failed: sealed run reached I/O on a different date', 'PASS after source repair', 'scripts/measure_search_v2_measurement.py'),
('Gate registry union', 'harness/gate_scorecard.py:register_gates/main', 'UNFIXED: registration API absent', 'scorecard::test_production_registration_merges_gate_ids / test_registration_conflict_preserves_original_bytes', "AttributeError: module 'harness.gate_scorecard' has no attribute 'register_gates'", 'PASS after source repair', 'harness/gate_scorecard.py'),
('Held-source CRLF/digest custody', 'outputs/handover/** provenance + .gitattributes', 'UNFIXED attributes; digests match', 'custody::test_every_held_provenance_digest_and_git_attribute / test_crlf_plant_fires_on_lf_digest', "assert 'auto' == 'unset'", 'strict xfail; real scratch Git-attribute plant PASS', '.tmp/patches/held-bytes.diff'),
('Wrong-endpoint acceptance', 'harness/target_endpoint.py', 'FIXED@e3014d02', 'tests/test_wrong_endpoint_acceptance.py (existing)', 'Already proved by existing regression; not duplicated', 'DONE; covered by full suite', 'none'),
]

lines = [
'# LANE RG report', '',
f'MEASURED HEAD: `{head}`. Requested base matches. No commit, reset, checkout, stash, push, or external acquisition was performed.', '',
'The focused regressions pass with strict xfails for unapplied owner patches. The full-suite result below is authoritative; no release/ship or whole-suite-green claim is made.', '',
'## Static versus dynamic disclosure', '',
'| Static / authored | Dynamic / measured |', '|---|---|',
'| Synthetic counterexample text, symbolic trial IDs, requirement assertions | Execution of live, pinned-parent, and proposed patched production paths |',
'| Sealed first-run date is a historical artefact identity | Refresh date must equal an injected/testable UTC clock reading |',
'| Patch proposals and fail-closed wording | Actual pytest output, Git attributes, physical-byte SHA-256, Git commit identities |',
'| No asserted research estimates or portfolio counts | Corpus paths/digests come from records on disk, never report prose |', '',
'## Coverage and boundaries', '',
'MEASURED: executable coverage addresses 8 of 9 numbered audit families; AUD 6 refers to an effect_type module absent from this base. AUD 2 covers the identity collision; its separate persisted effect-type-refusal subcase also depends on the later type-system branch. AUD 8 proves a cached-query/configuration mismatch; its patch refuses stale cache use. It does **not** execute CENTRAL/ICTRP/ISRCTN searches or claim the full amended protocol is implemented. Those obligations remain integration work.', '',
'AUD 1/2/3/4/7/8/9 and the custody/stamp fixes are READY-BEHIND-INTEGRATOR: their files are outside the lane’s explicit editable list, and no narrower owner was named for them. The patches remain unapplied. No CHK, ELX, or HD-owned source was edited. The heredoc-escape class is skipped here because lane HD owns it.', '',
'The assertion-literal regressions cover false checked flags and the historical publication-bias sentence. This is not a claim to have re-run or repaired all 25 historical TRUE-DEFECT adjudications in LIT2. That report is from another integration tree. The requested publication-bias literal is in manuscript.render on this base; the referenced grade/limitations/index candidates do not contain that exact unconditional sentence.', '',
'The only exact generated_on field found in harness/scripts/docs Python/JSON search is docs/model_stage_inventory.json. No writer supplying that date was found. Its patch withdraws the unbound stamp; it does not invent a build date. A positive control demonstrates a hash-bound input date and rejects a mismatched date.', '',
'Registry collision proof is bounded: the base contains one-file reads/migration and no lane registration/merge API. The before test fails on that missing capability, not on a reenacted filesystem copy. The new production `--merge-registry` path unions disjoint gate_ids, is idempotent for identical rows, and refuses conflicting duplicate rows without changing the original bytes.', '',
'Pinned historical modules execute with current imports, a bounded function-path regression rather than a full historical environment reconstruction. Adjustment pre-fix parent: `405cb80b79c9473e7cbd2baeaeb09aa170669920`. Publication pre-fix parent: `4ee334537f952ff5898b27446f3c4f3eac14ba12`. Source copies and SHA-256 inventory: `.tmp/prefix/MANIFEST.json`.', '',
'The custody scan recursively reads held JSON provenance, checks named original and extracted-text digests against bytes on disk, and asks Git for each effective text attribute. The two detected attribute gaps are the RoB2 extracted text files; recorded bytes already match. The scratch CRLF plant uses an actual temporary Git repository and text=auto attribute, then verifies the -text positive control. build_provenance.txt is a build log and contains no path/sha256 custody pairs.', '',
'## Defect table', '',
'Test shorthand `family::name` means `tests/test_week_regressions_family.py::name`. Full verbatim outputs follow; table excerpts are abbreviated where indicated. Original audit test paths in early logs predate splitting the tests into one file per family.', '',
'| Defect | Where | State on base | Test | Pre-fix output | Post-fix output | Files changed / proposed |',
'|---|---|---|---|---|---|---|',
]
for row in rows:
    lines.append('| ' + ' | '.join(str(x).replace('|', '/') for x in row) + ' |')
lines += ['', '## Verification', '',
    'PowerShell does not expand the pytest wildcard for Python. The equivalent focused command explicitly expands `Path("tests").glob("test_week_regressions_*.py")` and passes those files to `python -X utf8 -m pytest ... -q -p no:cacheprovider`.', '',
    'Focused final summary: `' + summary('regressions-final.txt') + '`.', '',
    'MEASURED focused counts: ' + counts('regressions-final.txt') + '.', '',
    'Full suite command: `python -X utf8 -m pytest tests -q -p no:cacheprovider`.', '',
    'Full final summary: `' + summary('full-suite-final.txt') + '`.', '',
    'MEASURED full-suite counts: ' + counts('full-suite-final.txt') + '.', '',
    'The full run was collected before the final generation-stamp tests and stronger scratch-attribute/family-prefix assertions; the final focused run covers those additions. The initial full run caught an early reason-audit fixture that did not trigger; its keyword was corrected and the plant was rerun with --runxfail before the strict-xfail final verification.', '',
    'The full-suite fixstate failure concerns generated ledger/README currency. These owner files were not changed. `.tmp/patches/fixstate-generated.diff` is rendered from the existing production renderers; the owner should regenerate it after integration because dependencies can move. No pre-existing test was weakened or deleted. The compatibility-sweep test rewrites an existing JSON file’s line endings; those test side effects are restored to the initial HEAD bytes before delivery.', '',
    'No project-status/submission promotion occurred; the external project index and workbook were not edited.', '',
]
for title, name in [
    ('Live-date, sealed-date and registry pre-fix failures (verbatim)', 'dates-scorecard-before.txt'),
    ('Assertion-status pre-fix failures (verbatim)', 'assertion-before.txt'),
    ('Owner-file plants on live base with --runxfail (verbatim)', 'owner-before.txt'),
    ('Historical adjustment pre-fix failure (verbatim)', 'historical-adjustment-before.txt'),
    ('Historical publication-bias pre-fix failure (verbatim)', 'historical-publication-before.txt'),
    ('Generation stamp pre-fix failure (verbatim)', 'generation-before.txt'),
    ('Focused final output (verbatim)', 'regressions-final.txt'),
    ('Full suite final output (verbatim)', 'full-suite-final.txt'),
    ('Search-completeness limb (verbatim)', 'search-completeness.txt'),
    ('Generated-view patch overlay verification (verbatim)', 'generated-view-proof.txt'),
    ('Unified patch applicability checks (verbatim)', 'patch-checks.txt'),
]:
    lines += ['## ' + title, '', '```text', read(name).rstrip(), '```', '']
(root / 'LANE-RG-REPORT.md').write_text(chr(10).join(lines), encoding='utf-8', newline=chr(10))
print('Wrote LANE-RG-REPORT.md', summary('regressions-final.txt'), summary('full-suite-final.txt'))
