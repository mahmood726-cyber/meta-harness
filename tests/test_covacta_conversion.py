"""Plants for the delegated CT.gov percentage conversion (synthetic mutations)."""
import pytest
from scripts import covacta_conversion as c
from harness import page


def test_covacta_unique_integer_conversion():
    assert c.unique_count('19.7', 294) == 58
    assert c.unique_count('19.4', 144) == 28
    for percentage, n in [('19.7', 10000), ('19.7', 3), ('NaN', 294)]:
        with pytest.raises(ValueError):
            c.unique_count(percentage, n)


def test_covacta_source_and_visible_conversion():
    binding = c.binding()
    assert binding['served'] == dict(ai=58, n1i=294, ci=28, n2i=144)
    assert binding['licence_class'] == 'PUBLIC_DOMAIN_REGISTRY'
    html = page._declared_conversion_block(binding)
    assert 'unique integer' in html and '19.7' in html and '19.4' in html
    assert 'corroboration' in html.lower()


def test_covacta_changed_source_refuses(tmp_path, monkeypatch):
    monkeypatch.setattr(c, 'SOURCE', tmp_path / 'missing.json')
    with pytest.raises((ValueError, FileNotFoundError)):
        c.binding()


def test_covacta_tampered_source_refuses(tmp_path, monkeypatch):
    changed = tmp_path / 'changed.json'
    changed.write_bytes(c.SOURCE.read_bytes() + b' ')
    monkeypatch.setattr(c, 'SOURCE', changed)
    with pytest.raises(ValueError, match='digest'):
        c.binding()


def test_covacta_notice_discloses_conversion_and_no_pool():
    from scripts import refresh_result_change_notices as n
    row = dict(c.binding(), id='NCT04320615', label='COVACTA', **c.binding()['served'])
    result = dict(licence_await=True, reason='No admissible pooled result: 1 of 3 eligible trials (TOCIBRAS) awaits an open-licence source')
    reason = n._reason([], {}, after_trials=[row], after_result=result)
    assert 'single-trial rows, not pooled' in reason
    assert 'unique integer' in reason and '19.7%' in reason
    assert n._note(result) == result['reason']
