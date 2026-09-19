"""Hostile-audit counterexamples, with owner patches kept unapplied."""
import importlib.util
from pathlib import Path
import pytest
from harness import harms, known_missing, comparator_second_pass, screen, reason_audit, design_key

ROOT = Path(__file__).resolve().parents[1]


from test_week_regressions_audit import load_pin, estimator_requirement


def test_spurious_refusal_stays_unreported_when_generic_signal_is_removed():
    from harness import absence
    row = {'id': 'plant', 'reason_code': absence.SIGNAL_SPURIOUS,
           'absent_kind': 'refused_on_evidence'}
    spec = {'name': 'Gastrointestinal adverse events'}
    records = {'plant': {'abstract': 'Serious adverse events were similar between groups.'}}
    proposed = load_pin('patched/harness/harms.py')
    assert proposed._hm_state_for_absent(row, spec, records, None)['harm_source_reported'] is True
    actual = harms._hm_state_for_absent(row, spec, records, None)
    assert actual['harm_absence_state'] == harms.RETRIEVED_REFUSED_WITH_REASON
    assert actual['harm_source_reported'] is False

@pytest.mark.parametrize('name', ['Gastrointestinal adverse events', 'Adverse events leading to discontinuation'])
def test_generic_adverse_events_do_not_prove_specific_harm(name):
    assert harms.reporting_signal('Serious adverse events were similar between the two groups.', {'name': name}) is None

