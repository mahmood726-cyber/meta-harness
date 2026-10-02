"""Defect plants plus offline integration contracts; no network or served writes."""
import os
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
    # The shared AACT adapter (kgap/aact_adapter.py, INDEX_RULES 2) -- which replaced the pre-fix aact_lane that turned
    # RE-LY's 3.55 %/year into "3 events" (dispatched from this branch) -- fed one planted rate row and one planted
    # people-unit count row through its real build_entries.
    from kgap import aact_adapter
    def rows(name, want):
        data = {'outcomes.txt': [{'nct_id': 'NCT00000001', 'id': 'o', 'title': 'stroke', 'time_frame': '1 year',
                                  'outcome_type': 'PRIMARY', 'population': '', 'units_analyzed': ''}],
                'result_groups.txt': [{'nct_id': 'NCT00000001', 'id': g, 'result_type': 'Outcome', 'title': g}
                                      for g in ('g_rate', 'g_count')],
                'outcome_analyses.txt': [],
                'outcome_measurements.txt': [
                    {'nct_id': 'NCT00000001', 'outcome_id': 'o', 'result_group_id': 'g_rate', 'param_type': 'NUMBER',
                     'units': '%/year', 'param_value_num': '3.55', 'category': '', 'classification': ''},
                    {'nct_id': 'NCT00000001', 'outcome_id': 'o', 'result_group_id': 'g_count', 'param_type': 'NUMBER',
                     'units': 'participants', 'param_value_num': '42', 'category': '', 'classification': ''}],
                'outcome_counts.txt': [{'nct_id': 'NCT00000001', 'outcome_id': 'o', 'result_group_id': g,
                                        'scope': 'Measure', 'units': 'Participants', 'count': '100'}
                                       for g in ('g_rate', 'g_count')]}
        return iter(data.get(name, []))
    original = aact_adapter._rows
    aact_adapter._rows = rows
    try:
        return aact_adapter.build_entries(['NCT00000001'], {'id': 'plant', 'digest': 'plant', 'rules': 2})
    finally:
        aact_adapter._rows = original


def test_rate_never_counts_shared_adapter_and_here():
    entry = base_aact_rate_plant()['NCT00000001']
    groups = {g['group']: g['count'] for g in entry['groups'].get('o', [])}
    assert 'g_rate' not in groups          # the %/year rate is never an event count (the dispatched defect, now fixed)
    assert groups.get('g_count') == 42      # and a people-unit integer still is: the check can fail both ways
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


def test_build_script_runs_and_reproduces_committed_outputs(tmp_path):
    """The build must RUN (a syntax error once shipped while 'deterministic' checks compared untouched files) and its
    replay must reproduce the committed bytes exactly."""
    import shutil
    import subprocess
    import sys
    work = tmp_path / 'repo'
    # exactly what a --reuse-index replay reads (harness/g1_noac.audit), nothing wider
    for rel in ('harness', 'docs/reviews/' + lane.SLUG, 'cache/' + lane.SLUG, 'topics', 'outputs/g1_noac',
                'evidence/acquisition_cascade/excerpts'):
        shutil.copytree(ROOT / rel, work / rel, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for rel in ('scripts/g1_noac_build.py', 'cache/comparators/34985309/2026-09-30_kgap_jats.xml',
                'outputs/k_gap/k_gap_table.csv', 'outputs/k_gap/G1_STATUS.md'):
        (work / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, work / rel)
    before = {p: (work / 'outputs/g1_noac' / p).read_bytes() for p in ('g1_noac.json', 'G1_NOAC.md')}
    run = subprocess.run([sys.executable, str(work / 'scripts/g1_noac_build.py'), '--reuse-index'], cwd=work,
                         capture_output=True, text=True, encoding='utf-8', env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    assert run.returncode == 0, run.stderr[-2000:]
    after = {p: (work / 'outputs/g1_noac' / p).read_bytes() for p in before}
    assert after == before
    assert b'\r\n' not in after['G1_NOAC.md'] and b'"same_trials"' in after['g1_noac.json']


def test_same_trials_selection_and_ci_level_plants():
    d = lane.read_json(ROOT / 'outputs/g1_noac/g1_noac.json')
    st = d['same_trials']
    assert set(st) == {'stroke_se', 'major_bleeding'}
    for key, v in st.items():
        assert v['ours']['k'] == 4 and not v['missing']
        assert {i['trial'] for i in v['inputs']} == {i['label'] for i in d['identities']}
        for i in v['inputs']:
            # a non-95% interval is never pooled as 95%: it is converted and the converted interval is recorded
            assert (i['ci95_used'] is None) == (i['ci_percent'] == '95')
    eng = next(i for i in st['stroke_se']['inputs'] if i['trial'].startswith('ENGAGE'))
    assert eng['population'] == 'ITT' and eng['ci_percent'] == '99'
    assert abs(eng['ci95_used'][0] - 0.744) < 0.001 and abs(eng['ci95_used'][1] - 1.017) < 0.001
    # a population mismatch is disclosed, never hidden
    rely = next(i for i in st['major_bleeding']['inputs'] if i['trial'] == 'RE-LY')
    assert rely['population_matches_comparator'] is False


def test_same_trials_verdict_types():
    comp = {'outcomes': {k: {'effect': {'effect': '0.81', 'lower': '0.74', 'upper': '0.89'}} for k in ('stroke_se', 'major_bleeding')}}
    def fact(i, nct, est, lo, hi, pop='ITT'):
        f = lane.fact(nct, 'stroke_se', 'EFFECT', 'AACT', 'plant', fact_id=f'P{i}')
        f.update(measure='HR', population=pop, ci_percent='95', values={'effect': est, 'lower': lo, 'upper': hi})
        return f
    ids = [{'label': f'T{i}', 'nct': f'NCT0000000{i}'} for i in range(3)]
    agree = [fact(i, ids[i]['nct'], '0.81', '0.71', '0.93') for i in range(3)]
    r = lane.same_trials(agree, [], comp, ids)['stroke_se']
    assert r['verdict_random_effects'] == 'AGREE' and r['n_two_source'] == 0
    # same side of the null but a gap of >= 10% of the comparator's CI half-width (log scale): not AGREE
    near = [fact(i, ids[i]['nct'], '0.80', '0.70', '0.92') for i in range(3)]
    assert lane.same_trials(near, [], comp, ids)['stroke_se']['verdict_random_effects'] == 'SAME_CONCLUSION_DIFFERENT_ESTIMATE'
    harm = [fact(i, ids[i]['nct'], '1.30', '1.10', '1.55') for i in range(3)]
    assert lane.same_trials(harm, [], comp, ids)['stroke_se']['verdict_random_effects'] == 'DIFFERENT_CONCLUSION'
    # an on-treatment tuple is chosen only when no ITT tuple exists, and is then flagged
    mixed = agree[:2] + [fact(2, ids[2]['nct'], '0.81', '0.71', '0.93', pop='ON_TREATMENT')]
    r = lane.same_trials(mixed, [], comp, ids)['stroke_se']
    assert r['n_population_matches'] == 2


def test_same_trials_verdict_is_the_trackers_rule():
    import importlib.util
    spec = importlib.util.spec_from_file_location('g1_tracker_for_test', ROOT / 'scripts' / 'g1_tracker.py')
    trk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trk)
    comp = {'outcomes': {k: {'effect': {'effect': '0.81', 'lower': '0.74', 'upper': '0.89'}} for k in ('stroke_se', 'major_bleeding')}}
    ids = [{'label': f'T{i}', 'nct': f'NCT0000000{i}'} for i in range(3)]
    for est, lo, hi in [('0.80', '0.70', '0.92'), ('0.70', '0.60', '0.82'), ('1.30', '1.10', '1.55'), ('0.95', '0.80', '1.12')]:
        facts = []
        for i in range(3):
            f = lane.fact(ids[i]['nct'], 'stroke_se', 'EFFECT', 'AACT', 'plant', fact_id=f'P{i}')
            f.update(measure='HR', population='ITT', ci_percent='95', values={'effect': est, 'lower': lo, 'upper': hi})
            facts.append(f)
        r = lane.same_trials(facts, [], comp, ids)['stroke_se']
        o = r['ours']
        want = trk.result_verdict({'estimate': o['estimate'], 'ci_low': o['ci_low'], 'ci_high': o['ci_high']},
                                  {'estimate': 0.81, 'ci_low': 0.74, 'ci_high': 0.89}, 'HR')['verdict']
        assert r['verdict_random_effects'] == want


def test_tracker_file_is_g1_matched_by_the_kgap_converter():
    """The committed tracker file is written by the k-gap lane's own converter (from_g1_noac): every comparator trial's
    route comes from this lane's two-source verdict; nothing comparator-only counts."""
    d = lane.read_json(ROOT / 'outputs/k_gap/g1/noac-vs-warfarin-af-stroke.json')
    assert d['k_matched'] == d['N_comparator_trials'] == 4
    assert d['routes'] == {'PRIMARY': 4}
    assert all('TWO_SOURCE_VERIFIED' in t['basis'] for t in d['trials'])
    assert d['g1_status']['state'] == 'G1_MATCHED' and d['g1_status']['unmet'] == []
    src = lane.read_json(ROOT / 'outputs/g1_noac/g1_noac.json')
    import hashlib
    assert d['lane_source']['sha256'] == hashlib.sha256((ROOT / 'outputs/g1_noac/g1_noac.json').read_bytes()).hexdigest()
    rows = {r['nct']: r for r in src['rows'] if r['outcome'] == 'stroke_se'}
    assert all(r['route']['state'] == 'TWO_SOURCE_VERIFIED' for r in rows.values())


def test_rely_two_source_is_aact_plus_fda_label_and_standard_dose_only():
    d = lane.read_json(ROOT / 'outputs/g1_noac/g1_noac.json')
    fid = {f['fact_id']: f for f in d['facts']}
    row = next(r for r in d['rows'] if r['item'] == 'RE-LY/stroke_se')
    pair = row['effect_route']['verified_facts'][0]
    assert sorted(fid[x]['source_id'].split(':')[0] for x in pair) == ['AACT', 'FDA']
    fda = next(fid[x] for x in pair if fid[x]['source_id'].startswith('FDA'))
    assert fda['values'] == {'effect': '0.65', 'lower': '0.52', 'upper': '0.81'} and fda['arm_column'].startswith('PRADAXA 150 mg')
    assert fda['population'] == 'UNKNOWN'   # the label says 'Patients randomized', never ITT: silent, not assumed
    # plant: the 110 mg column (HR 0.90) can never fill the standard-dose slot
    path = ROOT / 'evidence/acquisition_cascade/excerpts/RELY_FDA2010_Table4_stroke_SE.tables.txt'
    text = path.read_text(encoding='utf-8')
    body = text.split('=== TABLES (excerpt) ===')[-1]
    ident = {'nct': 'NCT00262600', 'label': 'RE-LY'}
    swapped = body.replace('PRADAXA 150 mg twice daily | PRADAXA 110 mg', 'PRADAXA 110 mg twice daily | PRADAXA 150 mg')
    f = lane.fda_stroke_facts(ROOT, path, text, swapped, ident)[0]
    assert f['values']['effect'] == '0.90' and '150 mg' in f['arm_column']   # follows the HEADER, not the position
    with pytest.raises(ValueError, match='ARM_COLUMNS_NOT_UNIQUE'):
        lane.fda_stroke_facts(ROOT, path, text, body.replace('110 mg', '150 mg'), ident)


def test_rocket_identity_from_its_own_registration_sentence():
    import importlib.util, sys as _sys
    _sys.path.insert(0, str(ROOT / 'scripts'))
    spec = importlib.util.spec_from_file_location('k_gap_table_for_test', ROOT / 'scripts' / 'k_gap_table.py')
    kt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kt)
    m = kt.self_registration_sentences([str(ROOT / 'cache' / lane.SLUG / 'records.json')])
    assert m[kt.k_gap.norm_acronym('ROCKET AF')] == ['NCT00403767']
    # plant: two different NCTs claimed by one acronym are kept (both), so the resolver reports ambiguity, never a pick
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, 'records.json')
        with open(p, 'w', encoding='utf-8') as fh:
            json.dump({'records': [{'abstract': 'Funded by X; PLANT ClinicalTrials.gov number, NCT00000001.'},
                                   {'abstract': 'Funded by Y; PLANT ClinicalTrials.gov number, NCT00000002.'}]}, fh)
        assert kt.self_registration_sentences([p])[kt.k_gap.norm_acronym('PLANT')] == ['NCT00000001', 'NCT00000002']
    row = next(t for t in lane.read_json(ROOT / 'outputs/k_gap/k_gap_table.json')['trials']
               if t['slug'] == lane.SLUG and t['label'] == 'ROCKET AF')
    assert row['ncts'] == ['NCT00403767'] and row['identity_basis'] == ['acronym_self_registration_sentence:ROCKET AF']
