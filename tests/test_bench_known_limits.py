"""Open review items: executable failures, never silent skips."""
import copy
import json
from pathlib import Path
import pytest
from harness import extract, pipeline

ROOT = Path(__file__).resolve().parents[1]
REASON = 'KNOWN LIMIT (bench r3, review closed at three rounds): '

@pytest.mark.xfail(strict=True, reason=REASON + 'P2 automatic-family path bypasses _dedup without families.json')
def test_bench_automatic_family_preserves_dedup(monkeypatch):
    slug = 'daratumumab-rrmm-pfs-bench'
    cfg = json.loads((ROOT/'topics'/f'{slug}.json').read_text(encoding='utf8'))
    records = json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf8'))
    assert not (ROOT/'cache'/slug/'families.json').exists()
    original = pipeline._dedup
    def tagged(*args, **kwargs):
        return [dict(r, dedup_passed=True) for r in original(*args, **kwargs)]
    monkeypatch.setattr(pipeline, '_dedup', tagged)
    inp = pipeline.outcome_inputs(slug, copy.deepcopy(cfg), copy.deepcopy(records))
    assert inp['merged']
    assert all(r.get('dedup_passed') for r in inp['merged'])

@pytest.mark.xfail(strict=True, reason=REASON + 'PFS2 before OS contaminates a non-PFS target')
def test_bench_pfs2_not_os():
    text = 'PFS2 HR 0.70 (95% CI 0.60-0.82); overall survival HR 0.80 (95% CI 0.70-0.91).'
    matches = list(extract._EFFECT.finditer(text))
    expected = extract._effect_from_match(matches[-1], text)[1]
    assert extract.extract_trial(text, ['overall survival'], ['drug'], [], estimand='HR')['effect'] == expected


CLOSED_REASON = 'KNOWN LIMIT (bench review closed at three rounds 18 Oct): '
CLOSED_LIMITS = [
    'harm_grade refuses the held Mitja negated serious-event sentence and three adversarial all-event clauses',
    'extracted_cell_span has no production producer',
    'comparator-selected record bypasses registry-contrast EXCLUDE and overwrites its reason',
    'Rajasingham registry SECONDARY outcome binding is not cross-checked against held PMC7665393 Table 2',
    'CASTOR QoL exclusion reason says companion/duplicate report of None',
]


def held_bench(slug):
    return tuple(json.loads((ROOT / folder / filename).read_text(encoding='utf8'))
                 for folder, filename in [('topics', slug + '.json'),
                                          ('cache/' + slug, 'records.json')])


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=CLOSED_REASON + CLOSED_LIMITS[0])
@pytest.mark.parametrize('case', ['held_mitja', 'none_serious', 'none_severe', 'separate_serious'])
def test_closed_harm_all_event_clause(case):
    from harness import harm_grade
    cfg, data = held_bench('hcq-covid-prophylaxis-bench')
    rec = next(r for r in data['records'] if r['id'] == '33289973')
    held = next(s for s in extract._sentences(rec['abstract'])
                if 'but no treatment-related serious adverse events were reported' in s)
    # Explicit adversarial inputs from the closure spec, not research observations.
    spans = {'held_mitja': held,
             'none_serious': 'adverse events 30 vs 20 (none serious)',
             'none_severe': 'adverse events 30 vs 20, none of which were severe',
             'separate_serious': 'Adverse events 30 vs 20; serious adverse events in 3 vs 2'}
    assert not harm_grade.mismatch(cfg['harm_outcomes'][0], {'source_span': spans[case]})


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=CLOSED_REASON + CLOSED_LIMITS[1])
def test_closed_harm_cell_span_has_production_producer():
    import subprocess
    # A producer must at least mention the field outside its sole consumer.
    found = subprocess.run(['rg', '-l', 'extracted_cell_span', 'harness/'],
                           cwd=ROOT, capture_output=True, text=True, check=True)
    candidates = [ROOT / name for name in found.stdout.splitlines()
                  if Path(name).name != 'harm_grade.py']
    assert candidates, 'Only harm_grade reads the field; no production producer supplies it'


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=CLOSED_REASON + CLOSED_LIMITS[2])
def test_closed_selected_registry_exclusion_survives(monkeypatch):
    from harness import bench_report_selection, registry_contrast, screen
    cfg, data = held_bench('daratumumab-rrmm-pfs-bench')
    cfg, data = bench_report_selection.apply(cfg, data, ROOT)
    rec = next(r for r in data['records'] if r.get('report_selection_evidence'))
    # An explicit adversarial verdict, using this record's held source span.
    verdict = dict(decision='exclude', rule_id='X-CONTRAST-REGISTRY',
                   reason='Registry contrast exclusion must survive comparator selection',
                   span=rec['report_selection_evidence']['table_row'])
    monkeypatch.setattr(registry_contrast, 'assess', lambda *args: verdict)
    actual = screen.run([rec], cfg)['decisions'][0]
    assert {k: actual[k] for k in verdict} == verdict


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=CLOSED_REASON + CLOSED_LIMITS[3])
def test_closed_rajasingham_binding_crosschecks_held_table(monkeypatch):
    import xml.etree.ElementTree as ET
    from harness import bench_routes, hand_binding
    cfg, _ = held_bench('hcq-covid-prophylaxis-bench')
    decl = cfg['posted_results_conversion']
    posted = json.loads((ROOT / decl['source_ref']).read_text(encoding='utf8'))
    table = posted['tables']['outcomes']
    outcomes = [dict(zip(table['header'].split('|'), line.split('|'))) for line in table['lines']]
    outcome = next(r for r in outcomes if r['title'] == decl['outcome_title'])
    assert outcome['outcome_type'] == 'SECONDARY'
    assert outcome['title'] in cfg['primary_outcome']['keywords']
    ref = ROOT / 'cache/hcq-covid-prophylaxis-bench/PMC7665393.xml'
    raw = ref.read_bytes()
    parse = ET.fromstring
    doc = parse(raw)
    assert doc.findtext('.//article-id[@pub-id-type="pmid"]') == decl['report_id']
    rows = list(doc.find('.//table-wrap[@id="T2"]').iter('tr'))
    target = next(r for r in rows if ''.join(r[0].itertext()) == 'PCR positive or probable COVID-19')
    other = next(r for r in rows if ''.join(r[0].itertext()) == 'PCR confirmed COVID-19')
    row = dict(bench_routes.for_config(cfg)[decl['report_id']], id=decl['report_id'])
    assert hand_binding.bind_hand_row(cfg['primary_outcome'], row)['hand_binding_state'] == 'BOUND'
    # Replace the broad endpoint's cells with the narrower held row's cells.
    # All counts come from XML; no invented effect or participant counts.
    for index in range(1, len(target)):
        target[index].clear()
        target[index].text = ''.join(other[index].itertext())
    mutated = ET.tostring(doc)
    def changed_primary(text, *args, **kwargs):
        return parse(mutated if text == raw else text, *args, **kwargs)
    monkeypatch.setattr(ET, 'fromstring', changed_primary)
    assert hand_binding.bind_hand_row(cfg['primary_outcome'], row)['hand_binding_state'] == 'ABSTAIN'


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=CLOSED_REASON + CLOSED_LIMITS[4])
def test_closed_castor_qol_reason_has_no_none_parent():
    from harness import bench_report_selection, screen
    cfg, data = held_bench('daratumumab-rrmm-pfs-bench')
    cfg, data = bench_report_selection.apply(cfg, data, ROOT)
    rec = next(r for r in data['records'] if str(r['id']) == '33555030')
    verdict = screen.run([rec], cfg)['decisions'][0]
    assert verdict['decision'] == 'exclude'
    assert 'companion/duplicate report of None' not in verdict['reason']
