"""Execute owner patches without changing their live files."""
import pytest
import importlib
import test_week_regressions_audit as audit


@pytest.mark.parametrize('module,test,args', [
    ('harms', 'test_generic_adverse_events_do_not_prove_specific_harm', ['Gastrointestinal adverse events']),
    ('harms', 'test_generic_adverse_events_do_not_prove_specific_harm', ['Adverse events leading to discontinuation']),
    ('known_missing', 'test_missing_candidates_merge_family_and_report_identity', []),
    ('comparator_second_pass', 'test_comparator_only_text_cannot_establish_current_pool_overlap', []),
    ('screen', 'test_title_omission_requires_review_not_ineligibility', []),
    ('reason_audit', 'test_kidney_and_cv_death_values_do_not_prove_mace_value', []),
])
@pytest.mark.parametrize('version', ['base', 'patched'])
def test_owner_patch_holds(monkeypatch, module, test, args, version):
    family = {'harms': 'harms', 'known_missing': 'missing', 'comparator_second_pass': 'overlap', 'screen': 'screening', 'reason_audit': 'reason'}[module]
    tests = importlib.import_module('test_week_regressions_' + family)
    patched = audit.load_pin(version + '/harness/' + module + '.py')
    monkeypatch.setattr(tests, module, patched)
    if version == 'base':
        with pytest.raises(AssertionError):
            getattr(tests, test)(*args)
    else:
        getattr(tests, test)(*args)
