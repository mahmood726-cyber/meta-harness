# LANE RG report

MEASURED HEAD: `237e90946f5b257265b0a3b1c986a8907d12eded`. Requested base matches. No commit, reset, checkout, stash, push, or external acquisition was performed.

The focused regressions pass with strict xfails for unapplied owner patches. The full-suite result below is authoritative; no release/ship or whole-suite-green claim is made.

## Static versus dynamic disclosure

| Static / authored | Dynamic / measured |
|---|---|
| Synthetic counterexample text, symbolic trial IDs, requirement assertions | Execution of live, pinned-parent, and proposed patched production paths |
| Sealed first-run date is a historical artefact identity | Refresh date must equal an injected/testable UTC clock reading |
| Patch proposals and fail-closed wording | Actual pytest output, Git attributes, physical-byte SHA-256, Git commit identities |
| No asserted research estimates or portfolio counts | Corpus paths/digests come from records on disk, never report prose |

## Coverage and boundaries

MEASURED: executable coverage addresses 8 of 9 numbered audit families; AUD 6 refers to an effect_type module absent from this base. AUD 2 covers the identity collision; its separate persisted effect-type-refusal subcase also depends on the later type-system branch. AUD 8 proves a cached-query/configuration mismatch; its patch refuses stale cache use. It does **not** execute CENTRAL/ICTRP/ISRCTN searches or claim the full amended protocol is implemented. Those obligations remain integration work.

AUD 1/2/3/4/7/8/9 and the custody/stamp fixes are READY-BEHIND-INTEGRATOR: their files are outside the lane’s explicit editable list, and no narrower owner was named for them. The patches remain unapplied. No CHK, ELX, or HD-owned source was edited. The heredoc-escape class is skipped here because lane HD owns it.

The assertion-literal regressions cover false checked flags and the historical publication-bias sentence. This is not a claim to have re-run or repaired all 25 historical TRUE-DEFECT adjudications in LIT2. That report is from another integration tree. The requested publication-bias literal is in manuscript.render on this base; the referenced grade/limitations/index candidates do not contain that exact unconditional sentence.

The only exact generated_on field found in harness/scripts/docs Python/JSON search is docs/model_stage_inventory.json. No writer supplying that date was found. Its patch withdraws the unbound stamp; it does not invent a build date. A positive control demonstrates a hash-bound input date and rejects a mismatched date.

Registry collision proof is bounded: the base contains one-file reads/migration and no lane registration/merge API. The before test fails on that missing capability, not on a reenacted filesystem copy. The new production `--merge-registry` path unions disjoint gate_ids, is idempotent for identical rows, and refuses conflicting duplicate rows without changing the original bytes.

Pinned historical modules execute with current imports, a bounded function-path regression rather than a full historical environment reconstruction. Adjustment pre-fix parent: `405cb80b79c9473e7cbd2baeaeb09aa170669920`. Publication pre-fix parent: `4ee334537f952ff5898b27446f3c4f3eac14ba12`. Source copies and SHA-256 inventory: `.tmp/prefix/MANIFEST.json`.

The custody scan recursively reads held JSON provenance, checks named original and extracted-text digests against bytes on disk, and asks Git for each effective text attribute. The two detected attribute gaps are the RoB2 extracted text files; recorded bytes already match. The scratch CRLF plant uses an actual temporary Git repository and text=auto attribute, then verifies the -text positive control. build_provenance.txt is a build log and contains no path/sha256 custody pairs.

## Defect table

Test shorthand `family::name` means `tests/test_week_regressions_family.py::name`. Full verbatim outputs follow; table excerpts are abbreviated where indicated. Original audit test paths in early logs predate splitting the tests into one file per family.

| Defect | Where | State on base | Test | Pre-fix output | Post-fix output | Files changed / proposed |
|---|---|---|---|---|---|---|
| AUD 1: harm endpoint specificity | harness/harms.py:reporting_signal | UNFIXED | harms::test_generic_adverse_events_do_not_prove_specific_harm | AssertionError: assert {'kind': 'term_signal', 'reported': True, 'span': 'Serious adverse events were similar between the two groups.'} is None | strict xfail; patched-copy PASS | .tmp/patches/harm-endpoint.diff |
| AUD 2: family/report collision | harness/known_missing.py:_missing_candidates | UNFIXED | missing::test_missing_candidates_merge_family_and_report_identity | AssertionError: one family must not be counted twice | strict xfail; patched-copy PASS | .tmp/patches/missing-family.diff |
| AUD 3: stale comparator overlap | harness/comparator_second_pass.py:parse_trial_set/apply | UNFIXED | overlap::test_comparator_only_text_cannot_establish_current_pool_overlap | AssertionError: current pool is not an input to this parser | strict xfail; patched-copy PASS | .tmp/patches/comparator-overlap.diff |
| AUD 4: title omission becomes ineligibility | harness/screen.py:screen_record | UNFIXED | screening::test_title_omission_requires_review_not_ineligibility | assert 'exclude' != 'exclude' | strict xfail; patched-copy PASS | .tmp/patches/screen-title.diff |
| AUD 5: substring adjustment labels | harness/design_key.py:key_for_trial | FIXED@3f8add72 | adjustment::test_adjustment_plant_fires_on_pinned_parent / test_adjustment_labels_require_estimator_evidence | AssertionError | pinned-parent fires; live PASS | tests + .tmp/prefix/adjustment/design_key.py |
| AUD 6: unlocated effect-type binding | harness/effect_type.py:check_review | NOT PRESENT ON BASE | none | No such module on this checkout | NOT CLAIMED | none |
| AUD 7: different endpoint used as held MACE evidence | harness/reason_audit.py:find_value_in_sources | UNFIXED | reason::test_kidney_and_cv_death_values_do_not_prove_mace_value | AssertionError (complete output in owner-before appendix) | strict xfail; patched-copy PASS | .tmp/patches/reason-endpoint.diff |
| AUD 8: cached query contract | harness/fetch.py:ensure | UNFIXED; bounded subcase | search_contract::test_cached_queries_must_match_requested_contract | Failed: DID NOT RAISE <class 'ValueError'> | strict xfail; patched-copy PASS | .tmp/patches/search-contract.diff |
| AUD 9: composite disclosure uses unselected abstract | harness/pipeline.py:composite disclosure block | UNFIXED | composite::test_selected_endpoint_controls_composite_warning | AssertionError (complete output in owner-before appendix) | strict xfail; patched-copy PASS | .tmp/patches/composite-selection.diff |
| Publication-bias assertion literal | harness/manuscript.py:render | FIXED@04902ecf | publication_bias::test_publication_bias_plant_fires_on_pinned_parent / test_missing_publication_bias_object_cannot_be_claimed_assessed | AssertionError | pinned-parent fires; live PASS | tests + .tmp/prefix/publication/manuscript.py |
| Unconditional compatibility success | harness/compat_check.py:enrich | UNFIXED | assertion_status::test_compatibility_status_reflects_remaining_violations | assert True is False | PASS after source repair | harness/compat_check.py |
| Unconditional proposition success | harness/propositions.py:check_document | UNFIXED | assertion_status::test_proposition_status_reflects_contradictions | assert True is False | PASS after source repair | harness/propositions.py |
| Unsupported generated_on stamp | docs/model_stage_inventory.json | UNFIXED | generation_stamp::test_inventory_stamp_has_build_input_provenance | AssertionError: generated_on lacks a build-input binding | strict xfail; withdrawal patch PASS | .tmp/patches/generated-on.diff |
| Live run assigned sealed historical date | scripts/search_v2_run.py:main/refresh/_candidate_path; scripts/search_v2_run_evidence.py:main/update_fixes | UNFIXED | dates::test_refresh_cli_uses_explicit_current_date / test_refresh_refuses_stale_date_before_io / test_dated_label_is_not_prefixed_with_first_run_date | SystemExit: 2; TypeError: refresh() got an unexpected keyword argument; AssertionError (full output below) | PASS after source repair | scripts/search_v2_run.py; scripts/search_v2_run_evidence.py |
| Sealed first run reruns on a later date | scripts/measure_search_v2_measurement.py:refresh_measurement | UNFIXED | dates::test_sealed_first_run_refuses_later_clock_before_io / test_sealed_artifact_identity_does_not_follow_clock | Failed: sealed run reached I/O on a different date | PASS after source repair | scripts/measure_search_v2_measurement.py |
| Gate registry union | harness/gate_scorecard.py:register_gates/main | UNFIXED: registration API absent | scorecard::test_production_registration_merges_gate_ids / test_registration_conflict_preserves_original_bytes | AttributeError: module 'harness.gate_scorecard' has no attribute 'register_gates' | PASS after source repair | harness/gate_scorecard.py |
| Held-source CRLF/digest custody | outputs/handover/** provenance + .gitattributes | UNFIXED attributes; digests match | custody::test_every_held_provenance_digest_and_git_attribute / test_crlf_plant_fires_on_lf_digest | assert 'auto' == 'unset' | strict xfail; real scratch Git-attribute plant PASS | .tmp/patches/held-bytes.diff |
| Wrong-endpoint acceptance | harness/target_endpoint.py | FIXED@e3014d02 | tests/test_wrong_endpoint_acceptance.py (existing) | Already proved by existing regression; not duplicated | DONE; covered by full suite | none |

## Verification

PowerShell does not expand the pytest wildcard for Python. The equivalent focused command explicitly expands `Path("tests").glob("test_week_regressions_*.py")` and passes those files to `python -X utf8 -m pytest ... -q -p no:cacheprovider`.

Focused final summary: `25 passed, 10 xfailed in 50.46s`.

MEASURED focused counts: 25 of 35 passed; 10 of 35 xfailed.

Full suite command: `python -X utf8 -m pytest tests -q -p no:cacheprovider`.

Full final summary: `1 failed, 996 passed, 9 xfailed in 1226.74s (0:20:26)`.

MEASURED full-suite counts: 1 of 1006 failed; 996 of 1006 passed; 9 of 1006 xfailed.

The full run was collected before the final generation-stamp tests and stronger scratch-attribute/family-prefix assertions; the final focused run covers those additions. The initial full run caught an early reason-audit fixture that did not trigger; its keyword was corrected and the plant was rerun with --runxfail before the strict-xfail final verification.

The full-suite fixstate failure concerns generated ledger/README currency. These owner files were not changed. `.tmp/patches/fixstate-generated.diff` is rendered from the existing production renderers; the owner should regenerate it after integration because dependencies can move. No pre-existing test was weakened or deleted. The compatibility-sweep test rewrites an existing JSON file’s line endings; those test side effects are restored to the initial HEAD bytes before delivery.

No project-status/submission promotion occurred; the external project index and workbook were not edited.

## Live-date, sealed-date and registry pre-fix failures (verbatim)

```text
FFFFFFF                                                                  [100%]
================================== FAILURES ===================================
_________________ test_refresh_cli_uses_explicit_current_date _________________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001B6D2A089D0>

    def test_refresh_cli_uses_explicit_current_date(monkeypatch):
        monkeypatch.setattr(live.datetime, "datetime", FutureClock)
        seen = {}
        monkeypatch.setattr(live, "refresh", lambda *a, **kw: seen.update(kw) or 0)
        monkeypatch.setattr(live, "_topics_arg", lambda value: [])
>       assert live.main(["refresh", "--label", "r9", "--topics", "all", "--run-date", "2031-02-03"]) == 0
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_week_regressions_dates.py:21: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
scripts\search_v2_run.py:371: in main
    args = ap.parse_args(argv)
           ^^^^^^^^^^^^^^^^^^^
C:\Users\mahmo\AppData\Local\Programs\Python\Python313\Lib\argparse.py:1930: in parse_args
    self.error(msg)
C:\Users\mahmo\AppData\Local\Programs\Python\Python313\Lib\argparse.py:2686: in error
    self.exit(2, _('%(prog)s: error: %(message)s\n') % args)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = ArgumentParser(prog='__main__.py', usage=None, description=None, formatter_class=<class 'argparse.HelpFormatter'>, conflict_handler='error', add_help=True)
status = 2
message = '__main__.py: error: unrecognized arguments: --run-date 2031-02-03\n'

    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, _sys.stderr)
>       _sys.exit(status)
E       SystemExit: 2

C:\Users\mahmo\AppData\Local\Programs\Python\Python313\Lib\argparse.py:2673: SystemExit
---------------------------- Captured stderr call -----------------------------
usage: __main__.py [-h] {refresh,status} ...
__main__.py: error: unrecognized arguments: --run-date 2031-02-03
__________________ test_refresh_refuses_stale_date_before_io __________________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001B6C0CC8510>

    def test_refresh_refuses_stale_date_before_io(monkeypatch):
        monkeypatch.setattr(live.datetime, "datetime", FutureClock)
        monkeypatch.setattr(live, "_split", lambda: pytest.fail("I/O reached before date validation"))
        with pytest.raises(SystemExit, match="UTC"):
>           live.refresh("r9", [], "all", "unused", None, ("ctgov",), run_date="2026-09-15")
E           TypeError: refresh() got an unexpected keyword argument 'run_date'

tests\test_week_regressions_dates.py:29: TypeError
____________ test_dated_label_is_not_prefixed_with_first_run_date _____________

    def test_dated_label_is_not_prefixed_with_first_run_date():
>       assert Path(live._candidate_path("2031-02-03r9", "all")).name == "candidates-2031-02-03r9-all.json"
E       AssertionError: assert 'candidates-2...03r9-all.json' == 'candidates-2...03r9-all.json'
E         
E         - candidates-2031-02-03r9-all.json
E         + candidates-2026-09-152031-02-03r9-all.json
E         ?            ++++++++++

tests\test_week_regressions_dates.py:33: AssertionError
_____________ test_sealed_first_run_refuses_later_clock_before_io _____________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001B6D2AB87C0>

    def test_sealed_first_run_refuses_later_clock_before_io(monkeypatch):
        monkeypatch.setattr(sealed.dt, "datetime", FutureClock)
        monkeypatch.setattr(sealed, "_validate_measurement_split", lambda: pytest.fail("sealed run reached I/O on a different date"))
        with pytest.raises(SystemExit, match="sealed"):
>           sealed.refresh_measurement()

tests\test_week_regressions_dates.py:41: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
scripts\measure_search_v2_measurement.py:335: in refresh_measurement
    _validate_measurement_split()
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

>   monkeypatch.setattr(sealed, "_validate_measurement_split", lambda: pytest.fail("sealed run reached I/O on a different date"))
                                                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: sealed run reached I/O on a different date

tests\test_week_regressions_dates.py:39: Failed
_____________ test_sealed_artifact_identity_does_not_follow_clock _____________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001B6D29AB8A0>

    def test_sealed_artifact_identity_does_not_follow_clock(monkeypatch):
        monkeypatch.setattr(sealed.dt, "datetime", FutureClock)
>       assert sealed.FIRST_RUN_DATE in sealed.CANDIDATE_PATH.name
               ^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: module 'scripts.measure_search_v2_measurement' has no attribute 'FIRST_RUN_DATE'

tests\test_week_regressions_dates.py:46: AttributeError
________________ test_production_registration_merges_gate_ids _________________

tmp_path = WindowsPath('C:/mh-w-RG/.tmp/pytest-of-mahmo/pytest-1/test_production_registration_m0')

    def test_production_registration_merges_gate_ids(tmp_path):
        target = tmp_path / scorecard.REGISTRY_PATH
        target.parent.mkdir(parents=True)
        a = {"schema_version": 2, "gates": [{"gate_id": "plant-a", "events": []}]}
        b = {"schema_version": 2, "gates": [{"gate_id": "plant-b", "events": []}]}
        target.write_text(json.dumps(a), encoding="utf-8")
>       scorecard.register_gates(tmp_path, b)
        ^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: module 'harness.gate_scorecard' has no attribute 'register_gates'

tests\test_week_regressions_scorecard.py:13: AttributeError
_____________ test_registration_conflict_preserves_original_bytes _____________

tmp_path = WindowsPath('C:/mh-w-RG/.tmp/pytest-of-mahmo/pytest-1/test_registration_conflict_pre0')

    def test_registration_conflict_preserves_original_bytes(tmp_path):
        target = tmp_path / scorecard.REGISTRY_PATH
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps({"gates": [{"gate_id": "plant-a", "events": []}]}))
        before = target.read_bytes()
        with pytest.raises(ValueError, match="conflict"):
>           scorecard.register_gates(tmp_path, {"gates": [{"gate_id": "plant-a", "events": [{"event_id": "different"}]}]})
            ^^^^^^^^^^^^^^^^^^^^^^^^
E           AttributeError: module 'harness.gate_scorecard' has no attribute 'register_gates'

tests\test_week_regressions_scorecard.py:25: AttributeError
=========================== short test summary info ===========================
FAILED tests/test_week_regressions_dates.py::test_refresh_cli_uses_explicit_current_date
FAILED tests/test_week_regressions_dates.py::test_refresh_refuses_stale_date_before_io
FAILED tests/test_week_regressions_dates.py::test_dated_label_is_not_prefixed_with_first_run_date
FAILED tests/test_week_regressions_dates.py::test_sealed_first_run_refuses_later_clock_before_io
FAILED tests/test_week_regressions_dates.py::test_sealed_artifact_identity_does_not_follow_clock
FAILED tests/test_week_regressions_scorecard.py::test_production_registration_merges_gate_ids
FAILED tests/test_week_regressions_scorecard.py::test_registration_conflict_preserves_original_bytes
7 failed in 9.10s
```

## Assertion-status pre-fix failures (verbatim)

```text
FF.                                                                      [100%]
================================== FAILURES ===================================
_______________ test_proposition_status_reflects_contradictions _______________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001A2DC129810>

    def test_proposition_status_reflects_contradictions(monkeypatch):
        monkeypatch.setattr(propositions, 'check_propositions', lambda review: [{'code': 'PLANT_CONTRADICTION'}])
        result = propositions.check_document({})
        assert result['contradictions']
>       assert result['checked'] is False
E       assert True is False

tests\test_week_regressions_assertion_status.py:9: AssertionError
___________ test_compatibility_status_reflects_remaining_violations ___________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001A2DC129220>

    def test_compatibility_status_reflects_remaining_violations(monkeypatch):
        monkeypatch.setattr(compat_check, 'check', lambda *args: [{'code': 'PLANT_CONTRADICTION'}])
        result = compat_check.enrich({})['compat_underlying']
        assert result['post_fix_violations']
>       assert result['checked'] is False
E       assert True is False

tests\test_week_regressions_assertion_status.py:16: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_week_regressions_assertion_status.py::test_proposition_status_reflects_contradictions
FAILED tests/test_week_regressions_assertion_status.py::test_compatibility_status_reflects_remaining_violations
2 failed, 1 passed in 6.36s
```

## Owner-file plants on live base with --runxfail (verbatim)

```text
FFFFF..F.FF.F.                                                           [100%]
================================== FAILURES ===================================
_ test_generic_adverse_events_do_not_prove_specific_harm[Gastrointestinal adverse events] _

name = 'Gastrointestinal adverse events'

    @pytest.mark.xfail(strict=True, reason='READY-BEHIND-INTEGRATOR: .tmp/patches/harm-endpoint.diff')
    @pytest.mark.parametrize('name', ['Gastrointestinal adverse events', 'Adverse events leading to discontinuation'])
    def test_generic_adverse_events_do_not_prove_specific_harm(name):
>       assert harms.reporting_signal('Serious adverse events were similar between the two groups.', {'name': name}) is None
E       AssertionError: assert {'kind': 'term_signal', 'reported': True, 'span': 'Serious adverse events were similar between the two groups.'} is None
E        +  where {'kind': 'term_signal', 'reported': True, 'span': 'Serious adverse events were similar between the two groups.'} = <function reporting_signal at 0x0000017BAF78DF80>('Serious adverse events were similar between the two groups.', {'name': 'Gastrointestinal adverse events'})
E        +    where <function reporting_signal at 0x0000017BAF78DF80> = harms.reporting_signal

tests\test_week_regressions_audit.py:21: AssertionError
_ test_generic_adverse_events_do_not_prove_specific_harm[Adverse events leading to discontinuation] _

name = 'Adverse events leading to discontinuation'

    @pytest.mark.xfail(strict=True, reason='READY-BEHIND-INTEGRATOR: .tmp/patches/harm-endpoint.diff')
    @pytest.mark.parametrize('name', ['Gastrointestinal adverse events', 'Adverse events leading to discontinuation'])
    def test_generic_adverse_events_do_not_prove_specific_harm(name):
>       assert harms.reporting_signal('Serious adverse events were similar between the two groups.', {'name': name}) is None
E       AssertionError: assert {'kind': 'term_signal', 'reported': True, 'span': 'Serious adverse events were similar between the two groups.'} is None
E        +  where {'kind': 'term_signal', 'reported': True, 'span': 'Serious adverse events were similar between the two groups.'} = <function reporting_signal at 0x0000017BAF78DF80>('Serious adverse events were similar between the two groups.', {'name': 'Adverse events leading to discontinuation'})
E        +    where <function reporting_signal at 0x0000017BAF78DF80> = harms.reporting_signal

tests\test_week_regressions_audit.py:21: AssertionError
__________ test_missing_candidates_merge_family_and_report_identity ___________

    @pytest.mark.xfail(strict=True, reason='READY-BEHIND-INTEGRATOR: .tmp/patches/missing-family.diff')
    def test_missing_candidates_merge_family_and_report_identity():
        review = {'screening': {'records': [{'id': 'report-a', 'trial_family_id': 'PLANT', 'decision': 'include'}]},
                  'outcomes': [{'primary': True, 'declared_absent_trials': [{'id': 'report-a'}]}]}
        rows = known_missing._missing_candidates(review, {'known_eligible_missing': [{'trial': 'PLANT'}]})
>       assert len(rows) == 1, 'one family must not be counted twice'
E       AssertionError: one family must not be counted twice
E       assert 2 == 1
E        +  where 2 = len([{'note': '', 'trial': 'PLANT', 'why_eligible': 'known_eligible_missing via None'}, {'id': 'report-a', 'why_eligible': 'screened in but not pooled'}])

tests\test_week_regressions_audit.py:29: AssertionError
_______ test_comparator_only_text_cannot_establish_current_pool_overlap _______

    @pytest.mark.xfail(strict=True, reason='READY-BEHIND-INTEGRATOR: .tmp/patches/comparator-overlap.diff')
    def test_comparator_only_text_cannot_establish_current_pool_overlap():
        profile = comparator_second_pass.PROFILES['glp1-ra-mace-t2d']['trial_set']
        text = profile['source_term'] + ' ' + ' '.join(t['aliases'][0] for t in profile['trials'])
        result = comparator_second_pass.parse_trial_set('glp1-ra-mace-t2d', text)
        assert result['k'] == len(profile['trials'])
>       assert result.get('shared_k') is None, 'current pool is not an input to this parser'
E       AssertionError: current pool is not an input to this parser
E       assert 7 is None
E        +  where 7 = <built-in method get of dict object at 0x0000017BC1058980>('shared_k')
E        +    where <built-in method get of dict object at 0x0000017BC1058980> = {'k': 8, 'measurement': 'MEASURED', 'only_ours': ['SOUL'], 'only_theirs': ['ELIXA'], ...}.get

tests\test_week_regressions_audit.py:38: AssertionError
____________ test_title_omission_requires_review_not_ineligibility ____________

    @pytest.mark.xfail(strict=True, reason='READY-BEHIND-INTEGRATOR: .tmp/patches/screen-title.diff')
    def test_title_omission_requires_review_not_ineligibility():
        record = {'id': 'plant', 'id_type': 'pmid', 'title': 'Cardiovascular outcomes',
                  'abstract': 'Adults with diabetes were randomly assigned to liraglutide or placebo in a double-blind trial.',
                  'pubtypes': ['Randomized Controlled Trial'], 'conditions': [], 'interventions': []}
        inc = {'population_any': ['diabetes'], 'intervention_any': ['liraglutide'], 'intervention_in_title': True}
        result = screen.screen_record(record, inc, set())
>       assert result[0] != 'exclude', result
E       AssertionError: ('exclude', 'X2', "population not on-topic: title/conditions do not mention any of ['diabetes'] (an incidental abstract mention does not qualify).", 'examined title/conditions: “Cardiovascular outcomes”')
E       assert 'exclude' != 'exclude'

tests\test_week_regressions_audit.py:48: AssertionError
___________ test_kidney_and_cv_death_values_do_not_prove_mace_value ___________

    @pytest.mark.xfail(strict=True, reason='READY-BEHIND-INTEGRATOR: .tmp/patches/reason-endpoint.diff')
    def test_kidney_and_cv_death_values_do_not_prove_mace_value():
        sources = [{'source_id': 'synthetic-plant', 'text': 'Results were similar for a composite of the kidney-specific components of the primary outcome (hazard ratio, 0.79; 95% CI, 0.66 to 0.94) and for death from cardiovascular causes (hazard ratio, 0.71; 95% CI, 0.56 to 0.89).'}]
>       assert reason_audit.find_value_in_sources(sources, ['major adverse cardiovascular events', 'death from cardiovascular causes'], 'Major adverse cardiovascular events') is None
E       AssertionError: assert {'source_id': 'synthetic-plant', 'source_kind': 'held', 'span': 'Results were similar for a composite of the kidney-sp...tio, 0.79; 95% CI, 0.66 to 0.94) and for death from cardiovascular causes (hazard ratio, 0.71; 95% CI, 0.56 to 0.89).'} is None
E        +  where {'source_id': 'synthetic-plant', 'source_kind': 'held', 'span': 'Results were similar for a composite of the kidney-sp...tio, 0.79; 95% CI, 0.66 to 0.94) and for death from cardiovascular causes (hazard ratio, 0.71; 95% CI, 0.56 to 0.89).'} = <function find_value_in_sources at 0x0000017BC101BB00>([{'source_id': 'synthetic-plant', 'text': 'Results were similar for a composite of the kidney-specific components of t...io, 0.79; 95% CI, 0.66 to 0.94) and for death from cardiovascular causes (hazard ratio, 0.71; 95% CI, 0.56 to 0.89).'}], ['major adverse cardiovascular events', 'death from cardiovascular causes'], 'Major adverse cardiovascular events')
E        +    where <function find_value_in_sources at 0x0000017BC101BB00> = reason_audit.find_value_in_sources

tests\test_week_regressions_audit.py:70: AssertionError
_____________ test_every_held_provenance_digest_and_git_attribute _____________

    @pytest.mark.xfail(strict=True, reason='READY-BEHIND-INTEGRATOR: .tmp/patches/held-bytes.diff')
    def test_every_held_provenance_digest_and_git_attribute():
        pairs = set()
        for record in (ROOT / 'outputs/handover').rglob('*.json'):
            pairs.update(source_pairs(json.loads(record.read_text(encoding='utf-8'))))
        assert pairs, 'no provenance records discovered'
        errors = []
        for rel, digest in sorted(pairs):
            attr = subprocess.check_output(['git', 'check-attr', 'text', '--', rel], cwd=ROOT, text=True).strip().rsplit(': ', 1)[-1]
            try:
                verify_bytes(ROOT / rel, digest, attr)
            except (AssertionError, OSError) as exc:
                errors.append(str(exc))
>       assert not errors, '\n'.join(errors)
E       AssertionError: C:\mh-w-RG\outputs\handover\rob2_method\rob2_cribsheet.pdf.txt: held bytes require -text
E         assert 'auto' == 'unset'
E           
E           - unset
E           + auto
E         C:\mh-w-RG\outputs\handover\rob2_method\rob2_full_guidance.pdf.txt: held bytes require -text
E         assert 'auto' == 'unset'
E           
E           - unset
E           + auto
E       assert not ["C:\\mh-w-RG\\outputs\\handover\\rob2_method\\rob2_cribsheet.pdf.txt: held bytes require -text\nassert 'auto' == 'uns...\rob2_method\\rob2_full_guidance.pdf.txt: held bytes require -text\nassert 'auto' == 'unset'\n  \n  - unset\n  + auto"]

tests\test_week_regressions_custody.py:59: AssertionError
______________ test_selected_endpoint_controls_composite_warning ______________

    @pytest.mark.xfail(strict=True, reason='READY-BEHIND-INTEGRATOR: .tmp/patches/composite-selection.diff')
    def test_selected_endpoint_controls_composite_warning():
>       assert not disclosure(ROOT / 'harness/pipeline.py')
E       assert not "pooled trials use each trial's OWN primary composite; component sets differ across trials (varying extra components across trials: unstable angina) — the pooled estimate mixes composite definitions (disclosed, not adjusted)"
E        +  where "pooled trials use each trial's OWN primary composite; component sets differ across trials (varying extra components across trials: unstable angina) — the pooled estimate mixes composite definitions (disclosed, not adjusted)" = disclosure((WindowsPath('C:/mh-w-RG') / 'harness/pipeline.py'))

tests\test_week_regressions_composite.py:31: AssertionError
______________ test_cached_queries_must_match_requested_contract ______________

tmp_path = WindowsPath('C:/mh-w-RG/.tmp/pytest-of-mahmo/pytest-6/test_cached_queries_must_match0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x0000017BC1099310>

    @pytest.mark.xfail(strict=True, reason='READY-BEHIND-INTEGRATOR: .tmp/patches/search-contract.diff')
    def test_cached_queries_must_match_requested_contract(tmp_path, monkeypatch):
>       requirement(fetch, tmp_path, monkeypatch)

tests\test_week_regressions_search_contract.py:19: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

module = <module 'harness.fetch' from 'C:\\mh-w-RG\\harness\\fetch.py'>
tmp_path = WindowsPath('C:/mh-w-RG/.tmp/pytest-of-mahmo/pytest-6/test_cached_queries_must_match0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x0000017BC1099310>

    def requirement(module, tmp_path, monkeypatch):
        path = tmp_path / 'records.json'
        path.write_text(json.dumps({'records': [], 'pubmed_queries': ['12345678[uid]']}), encoding='utf-8')
        monkeypatch.setattr(module, 'cache_path', lambda slug: str(path))
        monkeypatch.setattr(module, 'run', lambda config: pytest.fail('network acquisition attempted'))
>       with pytest.raises(ValueError, match='query contract'):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE <class 'ValueError'>

tests\test_week_regressions_search_contract.py:13: Failed
=========================== short test summary info ===========================
FAILED tests/test_week_regressions_audit.py::test_generic_adverse_events_do_not_prove_specific_harm[Gastrointestinal adverse events]
FAILED tests/test_week_regressions_audit.py::test_generic_adverse_events_do_not_prove_specific_harm[Adverse events leading to discontinuation]
FAILED tests/test_week_regressions_audit.py::test_missing_candidates_merge_family_and_report_identity
FAILED tests/test_week_regressions_audit.py::test_comparator_only_text_cannot_establish_current_pool_overlap
FAILED tests/test_week_regressions_audit.py::test_title_omission_requires_review_not_ineligibility
FAILED tests/test_week_regressions_audit.py::test_kidney_and_cv_death_values_do_not_prove_mace_value
FAILED tests/test_week_regressions_custody.py::test_every_held_provenance_digest_and_git_attribute
FAILED tests/test_week_regressions_composite.py::test_selected_endpoint_controls_composite_warning
FAILED tests/test_week_regressions_search_contract.py::test_cached_queries_must_match_requested_contract
9 failed, 5 passed in 22.93s
```

## Historical adjustment pre-fix failure (verbatim)

```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import sys; sys.path.insert(0,'tests'); from test_week_regressions_audit import estimator_requirement,load_pin; estimator_requirement(load_pin('adjustment/design_key.py'))
                                                                                                                    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\mh-w-RG\tests\test_week_regressions_audit.py", line 55, in estimator_requirement
    assert result['estimator_source'] not in {'PUBLISHED_ADJUSTED', 'PUBLISHED_UNADJUSTED'}
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError
```

## Historical publication-bias pre-fix failure (verbatim)

```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import sys; sys.path.insert(0,'tests'); from test_week_regressions_audit import load_pin; from test_week_regressions_publication_bias import requirement; requirement(load_pin('publication/manuscript.py'))
                                                                                                                                                              ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\mh-w-RG\tests\test_week_regressions_publication_bias.py", line 11, in requirement
    assert 'publication bias assessed from the trial registry' not in html
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError
```

## Generation stamp pre-fix failure (verbatim)

```text
F..                                                                      [100%]
================================== FAILURES ===================================
_______________ test_inventory_stamp_has_build_input_provenance _______________

    @pytest.mark.xfail(strict=True, reason='READY-BEHIND-INTEGRATOR: .tmp/patches/generated-on.diff')
    def test_inventory_stamp_has_build_input_provenance():
>       validate_stamp(json.loads((ROOT / 'docs/model_stage_inventory.json').read_text(encoding='utf-8')), ROOT)

tests\test_week_regressions_generation_stamp.py:23: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

document = {'_doc': 'Inventory of model-derived stages and artifacts. The ordinary verify/page build does not make live model cal...utputs and write committed summaries.', 'model_identifier': 'GPT-5 as documented in docs/crossfamily.json', ...}, ...]}
root = WindowsPath('C:/mh-w-RG')

    def validate_stamp(document, root):
        if 'generated_on' not in document:
            return
        binding = document.get('generation_input')
>       assert isinstance(binding, dict), 'generated_on lacks a build-input binding'
E       AssertionError: generated_on lacks a build-input binding
E       assert False
E        +  where False = isinstance(None, dict)

tests\test_week_regressions_generation_stamp.py:14: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_week_regressions_generation_stamp.py::test_inventory_stamp_has_build_input_provenance
1 failed, 2 passed in 2.98s
```

## Focused final output (verbatim)

```text
.....x..x.....x..xxxx........x..xx.                                      [100%]
25 passed, 10 xfailed in 50.46s
```

## Full suite final output (verbatim)

```text
........................................................................ [  7%]
........................................................................ [ 14%]
........................................................................ [ 21%]
........................................................................ [ 28%]
............................F........................................... [ 35%]
........................................................................ [ 42%]
........................................................................ [ 50%]
........................................................................ [ 57%]
........................................................................ [ 64%]
........................................................................ [ 71%]
........................................................................ [ 78%]
........................................................................ [ 85%]
........................................................................ [ 93%]
....................................x..x.....xxxx........x..xx........   [100%]
================================== FAILURES ===================================
__________________________ test_real_store_validates __________________________

    def test_real_store_validates() -> None:
        ok, reasons = fixstate.check(ROOT)
    
>       assert ok, "\n".join(reasons)
E       AssertionError: docs/fix_ledger.json is stale; run python scripts/render_fix_ledger.py
E         docs/evidence/search-v2-measurement-2026-09-15/README.md fix-state line is stale; run python scripts/rewrite_fixstate_lines.py
E       assert False

tests\test_fixstate.py:457: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
1 failed, 996 passed, 9 xfailed in 1226.74s (0:20:26)
```

## Search-completeness limb (verbatim)

```text
('PASS', 'TARGET verify_all.limb_search_completeness: head=237e90946f5b257265b0a3b1c986a8907d12eded base=none tree=dirty:27 files files=3 registry/search_completeness.json harness/search_v2.py harness/search_completeness.py\nsearch_v2 measurement current for engine a57dc45d6824 (outputs/search_v2/candidates-2026-09-15r3-all.json); states: RAN_OK 0 of 21; RAN_OK_WITH_SOURCE_ERRORS 21 of 21; RAN_ZERO 0 of 21; RAN_ERROR 0 of 21; NOT_RUN 0 of 21')
```

## Generated-view patch overlay verification (verbatim)

```text
fixstate.check with generated patch overlaid: (True, [])
```

## Unified patch applicability checks (verbatim)

```text
comparator-overlap.diff: 0 
composite-selection.diff: 0 
fixstate-generated.diff: 0 
generated-on.diff: 0 
harm-endpoint.diff: 0 
held-bytes.diff: 0 
missing-family.diff: 0 
reason-endpoint.diff: 0 
screen-title.diff: 0 
search-contract.diff: 0
```
