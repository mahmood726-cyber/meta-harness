"""Defect plants plus offline integration contracts; no network or served writes."""
import ast
from copy import deepcopy
import io
import json
from pathlib import Path
import types

import pytest

from harness import g1_noac as lane
from harness.secondary_meta import SecondaryRow, typed_match_text, typed_match_registry, verify_typed, g1_countable

ROOT = Path(__file__).resolve().parents[1]


def source(**updates):
    f = lane.fact('NCT00000001', 'stroke_se', 'EFFECT', 'PRIMARY_A', 'plant: HR 0.80 (0.70-0.90)')
    f.update(measure='HR', population='ITT', timepoint='trial end', definition='STROKE_OR_SYSTEMIC_EMBOLISM',
             ci_percent='95', values={'effect': '0.80', 'lower': '0.70', 'upper': '0.90'})
    f.update(updates)
    return f


def secondary(**updates):
    vals = dict(meta_pmid='plant_meta', meta_doi='', location={'kind': 'text', 'id': 'plant'}, source_digest='a'*64,
                provenance='TYPED_TEXT', trial_label='plant', measure='HR', outcome_definition='stroke',
                population='ITT', arm_dose='standard', effect='0.80', lower='0.70', upper='0.90')
    vals.update(updates)
    return SecondaryRow(**vals)


def base_aact_rate_plant():
    """Execute the actual unedited base aact_lane AST with in-memory I/O and planted rows."""
    tree = ast.parse((ROOT / 'scripts/k_gap_bulk_acquire.py').read_text(encoding='utf-8'))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'aact_lane')
    data = {'outcomes.txt': [{'nct_id': 'NCT00000001', 'id': 'o', 'title': 'stroke', 'time_frame': '1 year',
                             'outcome_type': 'PRIMARY', 'units': '%/year'}],
            'outcome_analyses.txt': [],
            'outcome_measurements.txt': [{'nct_id': 'NCT00000001', 'outcome_id': 'o', 'result_group_id': 'g',
                                          'param_type': 'NUMBER', 'units': '%/year', 'param_value_num': '3.55'}],
            'outcome_counts.txt': [{'nct_id': 'NCT00000001', 'outcome_id': 'o', 'result_group_id': 'g',
                                    'scope': 'Measure', 'count': '100'}]}
    class Sink(io.StringIO):
        def close(self):
            pass
    sink = Sink()
    def memory_open(path, mode, **kwargs):
        return io.BytesIO(sink.getvalue().encode()) if mode == 'rb' else sink
    import hashlib
    env = dict(time=types.SimpleNamespace(time=lambda: 0), json=json, hashlib=hashlib, AACT_IDX='memory_only',
               open=memory_open, _rows=lambda name, want: iter(data[name]))
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<base-aact-function>', 'exec'), env)
    env['aact_lane'](['NCT00000001'])
    return json.loads(sink.getvalue())


def test_rate_never_counts_with_base_pre_fix():
    before = base_aact_rate_plant()
    assert before['NCT00000001']['groups']['o'][0]['count'] == 3
    assert lane.measurement_kind({'param_type': 'NUMBER', 'param_value': '3.55', 'units': '%/year'}, {}) == 'RATE'
    assert lane.measurement_kind({'param_type': 'NUMBER', 'param_value': '3', 'units': 'patients'}, {}) == 'COUNT'


@pytest.mark.parametrize('units', ['per 100 patient-years', 'Number of events per 100 patient years', 'yearly event rate (percentage)'])
def test_all_held_rate_units_refused(units):
    assert lane.measurement_kind({'units': units, 'param_type': 'NUMBER', 'param_value': '3'}, {}) == 'RATE'


def test_unknown_fractional_negative_and_percentage_are_not_counts():
    for value, units in [('3', ''), ('3.5', 'patients'), ('-1', 'participants'), ('3', '%')]:
        assert lane.measurement_kind({'param_value': value, 'param_type': 'NUMBER', 'units': units}, {}) != 'COUNT'


def test_comparator_only_and_relayed_never_verified():
    assert lane.route([source(tier='SECONDARY')])['state'] == 'SECONDARY_ONLY'
    assert lane.route([source(tier='RELAYED')])['state'] == 'SECONDARY_ONLY'
    base = secondary(meta_pmid='comparator', state='PRIMARY_VERIFIED')
    assert g1_countable([base], {'comparator'}) == []  # Existing anti-circularity is preserved.
    assert len(g1_countable([secondary(state='PRIMARY_VERIFIED')], {'comparator'})) == 1


def test_single_source_not_verified_and_duplicate_not_independent():
    f = source()
    assert lane.route([f])['state'] == 'SINGLE_SOURCE'
    assert lane.route([f, deepcopy(f)])['state'] == 'SINGLE_SOURCE'
    assert lane.route([f, source(source_id='PRIMARY_B')])['state'] == 'TWO_SOURCE_VERIFIED'
    base = verify_typed(secondary(), [('text', 'one-source', 'stroke hazard ratio 0.80 (0.70-0.90)')], ['stroke'])
    assert base.state == 'PRIMARY_VERIFIED'


def test_population_never_matches_and_base_does_match():
    # Requirement: an ITT tuple never MATCHES an on-treatment tuple. They are different analyses (INCOMPARABLE),
    # so the pair neither verifies nor conflicts; with no comparable pair the row stays SINGLE_SOURCE.
    a, b = source(), source(population='ON_TREATMENT', source_id='PRIMARY_B')
    assert lane.compare_facts(a, b)['state'] == 'INCOMPARABLE'
    assert 'POPULATION_DIFFERS' in lane.compare_facts(a, b)['reasons']
    assert lane.route([a, b])['state'] == 'SINGLE_SOURCE'
    assert lane.route([a, dict(b, values={'effect': '0.80', 'lower': '0.70', 'upper': '0.90'})])['state'] != 'TWO_SOURCE_VERIFIED'
    assert typed_match_text(secondary(), 'On-treatment stroke hazard ratio 0.80 (0.70-0.90)', ['stroke'], 'plant')
    assert lane.compare_facts(a, source())['state'] == 'MATCH'


def test_low_dose_never_fills_standard_and_placebo_does_not_flip_arm():
    assert lane.arm_role('Dabigatran 110 mg', 'dabigatran', '150').startswith('REFUSED')
    assert lane.arm_role('Dabigatran 150 mg', 'dabigatran', '150') == 'STANDARD'
    assert lane.arm_role('Low Dose Edoxaban/Placebo Warfarin', 'edoxaban', '60') == 'REFUSED_LOW_DOSE'
    assert lane.arm_role('High Dose Edoxaban/Placebo Warfarin', 'edoxaban', '60') == 'STANDARD'
    assert lane.arm_role('Warfarin/Placebo Edoxaban', 'edoxaban', '60') == 'CONTROL'
    reg = {'outcomes': {'o': {'title': 'stroke', 'time_frame': 'trial end'}},
           'analyses': [{'outcome_id': 'o', 'param_type': 'Hazard Ratio', 'param_value': '.80',
                         'ci_lower': '.70', 'ci_upper': '.90', 'arm': 'low dose'}]}
    assert typed_match_registry(secondary(), reg, ['stroke'], 'low-dose-plant')


def test_identity_needs_unique_basis():
    assert lane.resolve_identity('Trial X', [], [], [], {'NCT00000001'})['state'] == 'UNRESOLVED'
    good = {'nct_id': 'NCT00000001', 'acronym': 'Trial X'}
    assert lane.resolve_identity('Trial X', [], [], [good], {'NCT00000001'})['state'] == 'MATCHED'
    assert lane.resolve_identity('Trial X', [], [], [good, dict(good, nct_id='NCT00000002')],
                                 {'NCT00000001', 'NCT00000002'})['state'] == 'UNRESOLVED'


def test_components_composites_and_definitions_not_interchanged():
    assert lane.outcome_key('Major and nonmajor clinically relevant bleeding') is None
    assert lane.outcome_key('Major or clinically relevant non-major bleeding') is None
    assert lane.outcome_key('Stroke/Systemic Embolism/Vascular Death') is None
    assert lane.outcome_key('Bleeding Events', 'ICH Major bleed') is None
    assert lane.outcome_key('TIMI Bleeding', 'Major bleed') is None
    assert lane.outcome_key('Bleeding Events', 'Major bleed') == 'major_bleeding'
    assert lane.outcome_key('Stroke or systemic embolism') == 'stroke_se'
    assert lane.compare_facts(source(definition='ISTH'), source(definition='ISTH_MODIFIED'))['state'] == 'INCOMPARABLE'


def test_unknown_metadata_is_disclosed_and_numeric_disagreement_conflicts():
    # Changed at integration: an axis neither source states is SILENT -- listed on the route, never assumed to agree.
    # (The lane's original rule made every AACT-vs-abstract pair unverifiable: 19 of 19 pairs refused on timepoint.)
    r = lane.route([source(timepoint='UNKNOWN'), source(source_id='PRIMARY_B', timepoint='UNKNOWN')])
    assert r['state'] == 'TWO_SOURCE_VERIFIED' and r['silent_axes'] == ['timepoint']
    changed = source(source_id='PRIMARY_B', values={'effect': '.50', 'lower': '.40', 'upper': '.60'})
    assert lane.route([source(), changed])['state'] == 'CONFLICT'
    assert lane.compare_facts(source(), source(ci_percent='99'))['state'] == 'INCOMPARABLE'
    assert lane.compare_facts(source(), source(timepoint='32 months'))['state'] == 'INCOMPARABLE'
    assert lane.printed_equal('0.707', '0.71')
    assert not lane.printed_equal('0.65', '0.66')


def test_held_integration_and_proposed_pool():
    d = lane.read_json(ROOT / 'outputs/g1_noac/g1_noac.json')
    assert len(d['identities']) == len(d['comparator']['regimens'])
    assert all(i['state'] == 'MATCHED' for i in d['identities'])
    assert len(d['rows']) == len(d['identities']) * len(d['comparator']['outcomes'])
    for f in d['facts']:
        assert f['span']
        if f['source_id'].startswith('FDA:'):
            assert 'committed text extraction' in f['span']
            assert f['source_held_text_sha256'] in f['span']
            assert 'source_pdf_sha256' not in f
        if f['kind'] == 'COUNTS':
            assert 0 <= f['values']['events_t'] <= f['values']['n_t']
            assert 0 <= f['values']['events_c'] <= f['values']['n_c']
    assert d['proposed_major_bleeding']['admissible_to_verified_pool'] is False
    assert d['proposed_major_bleeding']['result']['k'] == len(d['identities'])
    assert d['proposed_major_bleeding']['result']['ci_provenance'].startswith('synth.pool:PM')
    assert d['census']['topic_scope']['N'] == len(list((ROOT / 'topics').glob('*.json')))
    assert all(r['state'] != 'EXACT' for r in d['reproduction'])
    rely_harm = next(r for r in d['rows'] if r['item'] == 'RE-LY/major_bleeding')
    assert rely_harm['tuple_routes']['RATE']['state'] == 'CONFLICT'
    # HR 0.93 (0.81-1.07): AACT posted analysis == FDA 2010 review Table 2; the row stays CONFLICT on its rates.
    assert rely_harm['effect_route']['state'] == 'TWO_SOURCE_VERIFIED'
    fid = {f['fact_id']: f for f in d['facts']}
    assert {fid[x]['source_id'].split(':')[0] for pair in rely_harm['effect_route']['verified_facts'] for x in pair} == {'AACT', 'FDA'}
    # The served-tuple flag is true only when a verified pair contains the estimate we actually serve.
    for r in d['rows']:
        verified = {x for pair in r['effect_route'].get('verified_facts', []) for x in pair}
        assert r['served_tuple_two_source'] == bool(verified & set(r['served_comparison'].get('matching_facts', [])))
    assert rely_harm['route']['state'] == 'CONFLICT'


def test_no_future_or_secondary_source_can_supply_a_numeric_tuple():
    assert lane.route([])['state'] == 'NOT_HELD'
    assert lane.route([source(span='')])['state'] != 'TWO_SOURCE_VERIFIED'


def baseline_outputs():
    """Exact pre-fix output for LANE_REPORT; all calls are read-only/in-memory."""
    reg = {'outcomes': {'o': {'title': 'stroke', 'time_frame': 'trial end'}},
           'analyses': [{'outcome_id': 'o', 'param_type': 'Hazard Ratio', 'param_value': '.80',
                         'ci_lower': '.70', 'ci_upper': '.90', 'arm': 'low dose'}]}
    tree = ast.parse((ROOT / 'scripts/k_gap_table.py').read_text(encoding='utf-8'))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'resolve_unit')
    env = {'PUBNCT': {}}
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<base-identity-function>', 'exec'), env)
    unresolved = env['resolve_unit']({'cited': [], 'ncts': [], 'author': '', 'year': '', 'acronyms': []},
                                     None, {'pmid_nct': {}}, None)
    return {'rate': base_aact_rate_plant(),
            'single_source': verify_typed(secondary(), [('text', 'one-source', 'stroke hazard ratio 0.80 (0.70-0.90)')], ['stroke']).state,
            'population': typed_match_text(secondary(), 'On-treatment stroke hazard ratio 0.80 (0.70-0.90)', ['stroke'], 'plant'),
            'dose': typed_match_registry(secondary(), reg, ['stroke'], 'low-dose-plant'),
            'anti_circularity': [r.to_dict() for r in g1_countable([secondary(meta_pmid='comparator', state='PRIMARY_VERIFIED')], {'comparator'})],
            'identity_without_basis': unresolved,
            'timepoint': typed_match_text(secondary(timepoint='32 months'), 'At 5 years stroke hazard ratio 0.80 (0.70-0.90)', ['stroke'], 'plant'),
            'definition': typed_match_text(secondary(), 'stroke or systemic embolism or death hazard ratio 0.80 (0.70-0.90)', ['stroke'], 'plant'),
            'confidence_level': typed_match_text(secondary(), 'stroke hazard ratio 0.80; 99% CI 0.70-0.90', ['stroke'], 'plant')}


def test_base_identity_and_extra_semantic_plants():
    b = baseline_outputs()
    assert b['identity_without_basis']['ncts'] == []
    assert b['timepoint']['result'] == 'TYPED_MATCH'
    assert b['definition']['result'] == 'TYPED_MATCH'
    # 99% text is not recognised by the base regex: preserve this refusal too.
    assert b['confidence_level'] is None


# --- route plants added at integration (g1/noac): absent is not different, different is not conflicting ---------

def test_silent_axis_is_listed_not_assumed_and_value_tuple_verifies():
    a = source()
    b = source(source_id='PRIMARY_B', timepoint='UNKNOWN', population='UNKNOWN')
    r = lane.route([a, b])
    assert r['state'] == 'TWO_SOURCE_VERIFIED'
    assert r['silent_axes'] == ['population', 'timepoint']


def test_silent_axis_does_not_rescue_a_value_mismatch():
    a = source()
    b = source(source_id='PRIMARY_B', timepoint='UNKNOWN', values={'effect': '0.80', 'lower': '0.71', 'upper': '0.90'})
    assert lane.compare_facts(a, b)['state'] == 'DIFFERS'
    assert lane.route([a, b])['state'] == 'CONFLICT'


@pytest.mark.parametrize('axis', ['kind', 'measure', 'ci_percent'])
def test_required_axis_unstated_never_verifies(axis):
    b = source(source_id='PRIMARY_B', **{axis: 'UNKNOWN'})
    assert lane.compare_facts(source(), b)['state'] == 'UNRESOLVED'
    assert lane.route([source(), b])['state'] == 'SINGLE_SOURCE'


def test_ci_level_difference_is_incomparable_not_conflict():
    b = source(source_id='PRIMARY_B', ci_percent='97.5', values={'effect': '0.80', 'lower': '0.68', 'upper': '0.93'})
    assert lane.compare_facts(source(), b)['state'] == 'INCOMPARABLE'
    assert lane.route([source(), b])['state'] == 'SINGLE_SOURCE'


def test_conflict_outranks_a_match_elsewhere_in_the_row():
    match = source(source_id='PRIMARY_B')
    clash = source(source_id='PRIMARY_C', values={'effect': '0.81', 'lower': '0.70', 'upper': '0.90'})
    assert lane.route([source(), match, clash])['state'] == 'CONFLICT'


def test_low_dose_arm_never_fills_standard_slot_even_with_matching_values():
    b = source(source_id='PRIMARY_B', dose='LOW')
    a = source(dose='STANDARD')
    assert lane.compare_facts(a, b)['state'] == 'INCOMPARABLE'


def test_denominator_reproduction_arithmetic_and_plants():
    d = lane.read_json(ROOT / 'outputs/g1_noac/g1_noac.json')
    dr = d['census']['denominator_reproduction']
    assert dr['label'].startswith('DENOMINATOR_ARITHMETIC_ONLY')
    for name, arms in dr['targets'].items():
        for arm, x in arms.items():
            assert x['residual'] == x['comparator'] - x['aact_started_sum']
            for lab, implied in x['implied_if_others_exact'].items():
                assert implied == dr['aact_started'][lab][arm] + x['residual']
    # Plant: a second standard-dose STARTED row (e.g. a low-dose arm mis-typed as standard) must refuse, not sum.
    index = deepcopy(d['aact'])
    rely = next(m for m in index['milestones'] if m['nct_id'] == 'NCT00262600' and m['title'].strip().upper() == 'STARTED'
                and 'Dabigatran 150' in next(g['title'] for g in index['result_groups'] if g['id'] == m['result_group_id']))
    index['milestones'].append(dict(rely))
    with pytest.raises(ValueError, match='STARTED_ARMS_NOT_UNIQUE'):
        lane.denominator_reproduction(index, d['identities'], d['comparator'])
