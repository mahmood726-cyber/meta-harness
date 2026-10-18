"""Round-two plants: held evidence, with explicit mutation-only adversarial inputs."""
import copy
import json
from pathlib import Path
import pytest
from harness import pipeline, screen, registry_contrast, bench_report_selection

ROOT = Path(__file__).resolve().parents[1]
DARA = 'daratumumab-rrmm-pfs-bench'
HCQ = 'hcq-covid-prophylaxis-bench'

def load(slug):
    return tuple(json.loads(p.read_text(encoding='utf8')) for p in
                 (ROOT/'topics'/f'{slug}.json', ROOT/'cache'/slug/'records.json'))

def test_r2b_bench_controls_select_reports():
    cfg, data = load(DARA)
    selected, _ = bench_report_selection.apply(cfg, data, ROOT)
    companions = {str(c['pmid']) for c in selected['companion_reports']}
    assert not companions.intersection(cfg['positive_control_pmids'])

@pytest.mark.parametrize('verdict', [dict(decision='include'), dict(decision='exclude', rule_id='X-CONTRAST-REGISTRY', reason='plant', span='plant')])
def test_r2b_bench_selected_contrast_exemption(monkeypatch, verdict):
    cfg, data = load(DARA)
    _, selected = bench_report_selection.apply(cfg, data, ROOT)
    rec = next(r for r in selected['records'] if r.get('report_selection_evidence'))
    monkeypatch.setattr(registry_contrast, 'assess', lambda *args: verdict)
    assert screen.run([rec], cfg)['decisions'][0]['decision'] == 'include'

def test_r2b_bench_castor_qol_not_independent():
    cfg, data = load(DARA)
    selected, records = bench_report_selection.apply(cfg, data, ROOT)
    rec = next(r for r in records['records'] if str(r['id']) == '33555030')
    verdict = screen.run([rec], selected)['decisions'][0]
    assert verdict['decision'] == 'exclude'
    assert verdict['rule_id'] in ('X-DEDUP', 'X-FAMILY')

@pytest.mark.parametrize('citation', ['Smith-Jones et al 2020', 'Smith et al. 2020'])
def test_r2b_bench_citation_typed_refusal(tmp_path, citation):
    import xml.etree.ElementTree as ET
    cfg, data = load(DARA)
    ref = Path('cache/benchmarks/v1/PMC10519573.xml')
    doc = ET.fromstring((ROOT/ref).read_bytes())
    cell = doc.find('.//table-wrap[@id="T1"]//tbody/tr')[0]
    cell.clear()
    cell.text = citation
    (tmp_path/ref).parent.mkdir(parents=True)
    (tmp_path/ref).write_bytes(ET.tostring(doc))
    with pytest.raises(ValueError, match='REPORT_SELECTION_'):
        bench_report_selection.apply(cfg, data, tmp_path)

def test_r2b_bench_route_partition_reaches_builder(monkeypatch):
    cfg, data = load(HCQ)
    inp = pipeline.outcome_inputs(HCQ, cfg, data)
    assert inp['varms'] and inp['veffs'] is not None
    monkeypatch.setattr(pipeline, '_build_outcome', lambda *args, **kw: kw)
    result = pipeline.build_outcome_from_inputs(inp, cfg['primary_outcome'], 'primary', HCQ)
    assert result['verified_arms'] == inp['varms']
    assert result['verified_effects'] == inp['veffs']

def test_r2b_hcq_registry_counts_required():
    from harness import bench_routes
    cfg, _ = load(HCQ)
    row = bench_routes.for_config(cfg)['33068425']
    assert not row.get('absent'), row
    assert row['typed_route'] == 'hcq_combined_dose_counts'
    assert row['analysis_set_comparison']['status'] == 'DIVERGENT_NAMED'
    assert row['analysis_set_comparison']['reason_code'] == 'ANALYSIS_SET'

def test_r2b_hcq_round_half_up_and_page():
    from harness import hcq_routes, page
    assert hcq_routes.round_half_up(2.5) == 3
    cfg, _ = load(HCQ)
    row = dict(hcq_routes.for_config(cfg, ROOT)['33289973'], id='PMID 33289973')
    html = page._trial_inputs({'trials': [row]})
    raw = row['design_adjustment']['raw_counts']
    rr = lambda r: (r['ai']/r['n1i'])/(r['ci']/r['n2i'])
    assert f'{rr(raw):.3f}' in html and f'{rr(row):.3f}' in html

@pytest.mark.parametrize('grade', ['serious', 'Grade 3', 'Grade >=3', 'Grade III-IV', 'severe', 'SAEs'])
def test_r2b_harm_extracted_span_grade(grade):
    from harness import harm_grade, extract
    cfg, data = load(HCQ)
    rec = next(r for r in data['records'] if str(r['id']) == '32492293')
    spec = cfg['harm_outcomes'][0]
    span = next(s for s in extract._sentences(rec['abstract']) if 'Side effects' in s)
    assert not harm_grade.mismatch(spec, dict(source=span+'; no serious adverse events were reported.', source_span=span))
    high = span.replace('Side effects', grade+' adverse events')
    assert harm_grade.mismatch(spec, dict(source=high, source_span=high))
    assert not harm_grade.mismatch(dict(spec, grade=None), dict(source_span=high))


@pytest.mark.parametrize('field', ['ai', 'n1i', 'ci', 'n2i'])
def test_r2b_hcq_posted_count_tampering_refused(field):
    from harness import bench_routes, hand_binding, verify
    cfg, data = load(HCQ)
    decl = cfg['posted_results_conversion']
    row = dict(bench_routes.for_config(cfg)[decl['report_id']], id=decl['report_id'])
    assert hand_binding.bind_hand_row(cfg['primary_outcome'], row)['hand_binding_state'] == 'BOUND'
    assert verify.verify_pooled(row, '')[0] == 'verified'
    row[field] += 1
    assert hand_binding.bind_hand_row(cfg['primary_outcome'], row)['hand_binding_state'] == 'ABSTAIN'
    assert verify.verify_pooled(row, '')[0] == 'not-yet'


def test_r2b_hcq_posted_titles_not_group_order(tmp_path):
    import hashlib
    from harness import posted_counts
    cfg, data = load(HCQ)
    decl = cfg['posted_results_conversion']
    rec = next(r for r in data['records'] if r['id'] == decl['report_id'])
    ref = Path(decl['source_ref'])
    raw = json.loads((ROOT/ref).read_bytes())
    expected = posted_counts.route(cfg, ROOT, rec)
    for table in raw['tables'].values():
        table['lines'].reverse()
    (tmp_path/ref).parent.mkdir(parents=True)
    body = json.dumps(raw).encode('utf8')
    (tmp_path/ref).write_bytes(body)
    decl['sha256'] = hashlib.sha256(body).hexdigest()
    actual = posted_counts.route(cfg, tmp_path, rec)
    assert [actual[k] for k in ('ai','n1i','ci','n2i')] == [expected[k] for k in ('ai','n1i','ci','n2i')]
    decl['intervention_titles'], decl['comparator_titles'] = decl['comparator_titles'], decl['intervention_titles']
    with pytest.raises(ValueError, match='POSTED_COUNTS_ARM_IDENTITY'):
        posted_counts.route(cfg, tmp_path, rec)


@pytest.mark.parametrize('grade', ['serious', 'Grade 3', 'Grade >=3', 'Grade III-IV', 'severe', 'SAEs'])
def test_r2b_harm_cell_header_has_priority(grade):
    from harness import harm_grade
    assert harm_grade.mismatch({'grade':'any grade'}, {'extracted_cell_span':grade})
    assert not harm_grade.mismatch({'grade':'any grade'}, {'extracted_cell_span':'Any adverse events', 'source':'serious events 3 versus 4'})


def test_r2b_hcq_posted_json_roundtrip_binds():
    from harness import bench_routes, hand_binding
    cfg, _ = load(HCQ)
    pid = cfg['posted_results_conversion']['report_id']
    row = dict(bench_routes.for_config(cfg)[pid], id=pid)
    saved = json.loads(json.dumps(row))
    assert hand_binding.bind_hand_row(cfg['primary_outcome'], saved)['hand_binding_state'] == 'BOUND'


def test_r2b_hcq_declared_controls_pass(tmp_path):
    from harness import gate
    cfg, data = load(HCQ)
    assert cfg.get('positive_control_pmids') and cfg.get('negative_control_pmids')
    inp = pipeline.outcome_inputs(HCQ, cfg, data)
    (tmp_path/'review.json').write_text(json.dumps({'screening':{'records':inp['scr']['decisions']}}), encoding='utf8')
    assert gate.check_controls(str(tmp_path), {'slug':HCQ}) == []
