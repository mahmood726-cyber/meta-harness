"""Binding GS plants; synthetic values here are test fixtures only."""
import importlib
import pytest

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def glp1():
    return json.loads((ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json').read_text(encoding='utf-8'))


def test_unsourced_envelope_refused():
    module = importlib.import_module('harness.envelope')
    row = module.compute_spec('plant', 'source', 'missing', [
        {'label': 'plant', 'effect': .8, 'ci_low': .7, 'ci_high': .9}], 'HR')
    assert not row['computable']
    assert 'NOT_COMPUTABLE' in module.render({'specifications': [row], 'scale': 'HR'})


def test_fragility_direction_plant():
    module = importlib.import_module('harness.fragility')
    from harness.synth import Study
    studies = [Study('a', effect=.1, ci_low=.09, ci_high=.11),
               Study('b', effect=1.2, ci_low=1.1, ci_high=1.3),
               Study('c', effect=1.2, ci_low=1.1, ci_high=1.3)]
    table = module.leave_one_out(studies, 'HR')
    assert any(r['direction_changed'] for r in table)
    assert 'changes direction' in module.sentence({'rows': table})


def test_grade_arithmetic_plant():
    from harness import grade
    with pytest.raises(ValueError, match='REFUSED'):
        grade.validate_arithmetic({'start': 'high', 'downgrades': 2,
                                       'certainty': 'moderate'})


def test_real_regulatory_positive_controls_and_duplicate_refusal():
    from harness import envelope, claimgraph
    alternatives = envelope._regulatory_alternatives(ROOT)
    assert len(alternatives) == 3
    assert all(claimgraph.verify_fact(a['row'])['verified'] for a in alternatives)
    rows = [a['row'] for a in alternatives[:2]]
    spec = envelope.compute_spec('real', 'source', 'FDA rows', rows, 'HR')
    assert spec['computable'], spec
    assert spec['result']['pi'] != spec['result']['ci']
    duplicate = envelope.compute_spec('duplicate', 'source', 'same trial twice', rows + [rows[0]], 'HR')
    assert not duplicate['computable']


def test_served_primary_numerical_reproduction_at_page_precision():
    """Numerical positive control is distinct from provenance certification."""
    from harness import envelope
    from harness.known_missing import _study_from_trial
    from harness.synth import pool
    p = envelope.primary(glp1())
    studies = [_study_from_trial(row, 'HR') for row in p['trials']]
    result = envelope.calculate(studies, 'HR')
    assert result['k'] == 7
    assert abs(result['estimate'] - pool(studies, 'HR').estimate) < 1e-6
    assert abs(round(result['estimate'], 4) - p['result']['estimate']) < 1e-6
    assert result['pi'] != result['ci']
    assert envelope.build(glp1())['specifications'][0]['computable']
    assert 'D3 unassessed on 7 of 7' in glp1()['grade']['rob_basis']


def test_reml_floor_and_zero_tau_pi_refusal():
    from harness.envelope import calculate
    from harness.synth import Study
    studies = [Study(str(i), effect=.8, ci_low=.7, ci_high=.9) for i in range(3)]
    reml = calculate(studies, 'HR', method='REML')
    assert reml['tau2'] == 0
    assert reml['pi'] is None and 'NOT_COMPUTABLE' in reml['pi_reason']
    wald = calculate(studies, 'HR', interval='Wald')
    assert reml['ci'][0] < wald['ci'][0] < wald['ci'][1] < reml['ci'][1]


def test_reml_equal_variance_analytic_solution_and_fixed_control():
    import math
    from scipy.stats import norm
    from harness.envelope import calculate
    from harness.synth import Study, pool
    z = norm.ppf(.975)
    studies = [Study(str(i), effect=math.exp(y), ci_low=math.exp(y-z*.1), ci_high=math.exp(y+z*.1)) for i, y in enumerate([-.5, 0., .5])]
    reml = calculate(studies, 'HR', method='REML')
    assert abs(reml['tau2'] - .24) < 1e-6
    fixed = calculate(studies, 'HR', model='fixed', interval='Wald')
    canonical = pool(studies, 'HR')
    assert abs(fixed['estimate'] - canonical.estimate_fixed) < 1e-6
    assert abs(fixed['ci'][0] - canonical.ci_low_fixed) < 1e-6


def test_grade_upgrades_and_named_provisional():
    from harness.grade import validate_arithmetic
    validate_arithmetic({'start': 'high', 'downgrades': 2, 'upgrades': 1, 'certainty': 'moderate'})
    with pytest.raises(ValueError, match='REFUSED'):
        validate_arithmetic({'certainty': 'provisional'})
    from harness import claimgraph
    obj = {'start': 'high', 'downgrades': 2, 'upgrades': 1, 'certainty': 'moderate',
           'domains': {name: {'assessed': True, 'downgrade': 2 if name == 'risk_of_bias' else 0}
                       for name in ['risk_of_bias', 'inconsistency', 'imprecision', 'indirectness', 'publication_bias']}}
    assert claimgraph.certainty_object(obj)['value'] == 'moderate'
    assert claimgraph.certainty_violations({'grade': obj}) == []


def test_decomposer_adjacent_deltas_require_two_verified_steps():
    from harness import envelope, decomposer
    rows = [a['row'] for a in envelope._regulatory_alternatives(ROOT)[:2]]
    steps = decomposer.replay([rows, rows, rows, rows], 'HR', {'method': 'PM', 'interval': 'HKSJ'})
    assert all(s['computable'] for s in steps)
    assert all(s['delta_log_effect'] == 0. for s in steps[1:])
    missing = decomposer.replay([None, None, rows, rows], 'HR', None)
    assert not missing[0]['computable'] and missing[3]['computable']
    assert missing[3]['delta_log_effect'] is None


def test_corpus_render_contract_and_tampered_sentence(tmp_path):
    from harness.gate import check_statistical_layers
    from harness.canonical import review_sha256, sha256_text
    for path in sorted((ROOT / 'docs/reviews').glob('*/review.json')):
        assert check_statistical_layers(path.parent) == [], path.parent.name
        obj = json.loads(path.read_text(encoding='utf-8'))
        manifest = json.loads((path.parent / 'manifest.json').read_text(encoding='utf-8'))
        assert review_sha256(obj) == manifest['review_sha256']
        assert sha256_text((path.parent / 'index.html').read_text(encoding='utf-8')) == manifest['html_sha256']
    original = ROOT / 'docs/reviews/glp1-ra-mace-t2d'
    (tmp_path / 'review.json').write_bytes((original / 'review.json').read_bytes())
    html = (original / 'index.html').read_text(encoding='utf-8')
    tampered = html.replace('Robustness envelope', 'Unverified robustness envelope')
    assert tampered != html
    (tmp_path / 'index.html').write_text(tampered, encoding='utf-8')
    assert any('rendering not generated' in r for r in check_statistical_layers(tmp_path))
    (tmp_path / 'index.html').write_text(html.replace('</body>', '<p>fragility: fully stable</p></body>'), encoding='utf-8')
    assert any('unbound envelope/fragility' in r for r in check_statistical_layers(tmp_path))


def test_http_ui_contract():
    """Equivalent E2E: render artifacts -> HTTP on required loopback -> parse sections."""
    import functools
    import http.server
    import threading
    import urllib.request
    from html.parser import HTMLParser
    class Parser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.ids = []
        def handle_starttag(self, tag, attrs):
            self.ids.extend(v for k, v in attrs if k == 'id')
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 8000), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen('http://127.0.0.1:8000/docs/reviews/glp1-ra-mace-t2d/') as response:
            html = response.read().decode('utf-8')
        parser = Parser()
        parser.feed(html)
        for name in ['gs-envelope', 'gs-fragility', 'gs-decomposer']:
            assert parser.ids.count(name) == 1
        assert 'Unassessed domains:' in html and 'observed-evidence confidence interval' in html
        assert '{{' not in html
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
