"""Measured plants against committed review inputs; no invented research values."""
import copy
import json
import re
from pathlib import Path
from unittest.mock import patch

from harness import census, claim, page

ROOT = Path(__file__).resolve().parents[1]


def review(slug):
    return json.loads((ROOT / 'docs/reviews' / slug / 'review.json').read_text(encoding='utf-8'))


def rendered(core, cc):
    core = copy.deepcopy(core)
    core['reproduction']['claim_check'] = cc
    return page.render_page(core)


def count(html):
    return int(re.search(r'Claims checked: (\d+)', html).group(1))


def test_iv_iron_real_calls():
    core = review('iv-iron-hfref-hosp')
    completed = []
    original = claim.significance_contradictions
    def spy(*args, **kwargs):
        result = original(*args, **kwargs)
        completed.append(result)
        return result
    with patch.object(claim, 'significance_contradictions', spy):
        cc = census._claim_check(core)
    assert count(rendered(core, cc)) == len(completed)


def test_raising_surface_is_failed():
    core = review('glp1-ra-mace-t2d')
    before = count(rendered(core, census._claim_check(core)))
    with patch.object(page, 'render_overview', side_effect=RuntimeError('CHK planted renderer failure')):
        cc = census._claim_check(core)
    html = rendered(core, cc)
    assert count(html) == before - 1
    assert 'failed: 1' in html
    assert any(r['state'] == 'FAILED' and 'CHK planted' in r['reason'] for r in cc['receipts'])


def test_k8_cannot_use_k1_label():
    core = review('glp1-ra-mace-t2d')
    primary = next(o for o in core['outcomes'] if o.get('primary'))
    assert primary['result']['k'] == 8
    primary['result']['ci_provenance'] = 'source-reported-CI:k=1-verbatim'
    assert census._interval_provenance_check(core)


def test_zero_is_failing_state():
    core = review('iv-iron-hfref-hosp')
    html = rendered(core, {'claims_checked': 0, 'receipts': [], 'contradictions': []})
    assert count(html) == 0
    assert "class='absent'><strong>No checkable pooled claim (Claims checked: 0)" in html
    assert 'limitation, not a clean result' in html


def test_strand_pool_cannot_use_k1_label():
    core = review('iv-iron-hfref-hosp')
    pool = next(s['pool'] for s in core['strands']['strands'] if s.get('pool') and s['pool']['k'] > 1)
    pool['ci_provenance'] = 'source-reported-CI:k=1-verbatim'
    assert census._interval_provenance_check(core)


def test_checker_exception_and_digest(monkeypatch):
    core = review('iv-iron-hfref-hosp')
    baseline = census._claim_check(core)
    original = claim.significance_contradictions
    calls = []
    def raises_once(*args):
        calls.append(True)
        if len(calls) == 1:
            raise RuntimeError('CHK checker failure')
        return original(*args)
    monkeypatch.setattr(claim, 'significance_contradictions', raises_once)
    cc = census._claim_check(core)
    assert cc['claims_checked'] == baseline['claims_checked'] - 1
    assert cc['receipts'][0]['state'] == 'FAILED'
    assert 'CHK checker failure' in cc['receipts'][0]['reason']
    assert [r['inputs_sha256'] for r in baseline['receipts']] == [r['inputs_sha256'] for r in cc['receipts']]
    assert all(len(r['inputs_sha256']) == 64 for r in cc['receipts'])


def test_page_ignores_inflated_legacy_count():
    core = review('iv-iron-hfref-hosp')
    cc = census._claim_check(core)
    cc['claims_checked'] = 999
    assert count(rendered(core, cc)) == sum(r['state'] == 'COMPLETED' for r in cc['receipts'])


def test_limb_exception_receipt(monkeypatch, capsys):
    from scripts import verify_all
    def good():
        return verify_all.PASS, 'positive control'
    def bad():
        raise RuntimeError('CHK limb failure')
    monkeypatch.setattr(verify_all, 'LIMBS', [('good', good), ('bad', bad)])
    assert verify_all.main() == 1
    line = next(s for s in capsys.readouterr().out.splitlines() if s.startswith('CHECK_RECEIPTS '))
    receipts = json.loads(line.removeprefix('CHECK_RECEIPTS '))
    assert [r['state'] for r in receipts] == ['COMPLETED', 'FAILED']
    assert 'CHK limb failure' in receipts[1]['reason']


def test_unattended_limbs_refuse(monkeypatch, capsys):
    from scripts import verify_all
    monkeypatch.setattr(verify_all, '_target', lambda *a: ('unresolvable target', 'missing'))
    assert verify_all.main() == 1
    line = next(s for s in capsys.readouterr().out.splitlines() if s.startswith('CHECK_RECEIPTS '))
    receipts = json.loads(line.removeprefix('CHECK_RECEIPTS '))
    assert len(receipts) == len(verify_all.LIMBS)
    assert all(r['state'] == 'PLANNED' for r in receipts)
