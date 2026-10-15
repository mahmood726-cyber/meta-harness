"""Captain's plants: expectations only; arm facts are read from registry cache."""
import json
from pathlib import Path
import pytest
from harness import screen

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'daratumumab-rrmm-pfs-bench'
BAD = ['NCT04181827', 'NCT05083169', 'NCT04649060']
GOOD = ['NCT02076009', 'NCT02136134', 'NCT03158688', 'NCT03180736', 'NCT03234972']


@pytest.mark.parametrize('nct', BAD + GOOD)
def test_registry_plants(nct):
    from harness import registry_contrast
    cfg = json.loads((ROOT/'topics'/f'{SLUG}.json').read_text(encoding='utf8'))
    doc = registry_contrast.load(cfg)
    assert doc['records'][nct]['design_groups'], 'plant requires real registry arms'
    result = registry_contrast.assess({'id':nct, 'nct':nct}, cfg, doc)
    assert result['rule_id'] == ('X-CONTRAST' if nct in BAD else 'I-CONTRAST')


def test_missing_arms_cannot_pass():
    from harness import registry_contrast
    cfg = json.loads((ROOT/'topics'/f'{SLUG}.json').read_text(encoding='utf8'))
    assert registry_contrast.assess({}, cfg, {})['decision'] == 'unresolved'


def test_screen_excludes_bad_plants():
    cfg = json.loads((ROOT/'topics'/f'{SLUG}.json').read_text(encoding='utf8'))
    data = json.loads((ROOT/'cache'/SLUG/'records.json').read_text(encoding='utf8'))
    records = [r for r in data['records'] if r.get('nct') in BAD]
    decisions = screen.run(records, cfg)['decisions']
    for nct in BAD:
        ids = {r['id'] for r in records if r.get('nct') == nct}
        assert any(d['id'] in ids and d['rule_id'] == 'X-CONTRAST' for d in decisions)
    assert not any(d['decision'] == 'include' for d in decisions)


def test_registry_precedes_misleading_abstract():
    from harness import registry_contrast as rc
    cfg = json.loads((ROOT/'topics'/f'{SLUG}.json').read_text(encoding='utf8'))
    data = json.loads((ROOT/'cache'/SLUG/'records.json').read_text(encoding='utf8'))
    good_abstract = next(r['abstract'] for r in data['records'] if r.get('nct') == GOOD[3])
    for nct in BAD:
        assert rc.assess({'id':nct, 'abstract':good_abstract}, cfg, rc.load(cfg))['rule_id'] == 'X-CONTRAST'


def test_ctgov_v2_parity_and_no_identifier_switch():
    from harness import registry_contrast as rc
    cfg = json.loads((ROOT/'topics'/f'{SLUG}.json').read_text(encoding='utf8'))
    doc = rc.load(cfg)
    for nct in BAD + GOOD:
        raw = doc['records'][nct]
        arms = rc.aact_arms(raw)
        module = {'armGroups':[{'label':a['label'], 'type':a['role'], 'description':a['description'],
                               'interventionNames':a['interventions']} for a in arms]}
        # Renaming the record removes the plant identifier from the parser input.
        converted = rc.v2_arms({'protocolSection':{'armsInterventionsModule':module}})
        assert rc.arm_verdict(converted, rc.terms(cfg)) == (nct not in BAD)


def test_missing_links_do_not_establish_absence():
    from harness import registry_contrast as rc
    cfg = json.loads((ROOT/'topics'/f'{SLUG}.json').read_text(encoding='utf8'))
    doc = rc.load(cfg)
    for nct in GOOD:
        doc['records'][nct]['design_group_interventions'] = []
        assert rc.assess({'id':nct}, cfg, doc)['decision'] == 'unresolved'


@pytest.mark.parametrize('pmid', ['11994052', '19552097'])
def test_explicit_abstract_arm_forms(pmid):
    from harness import registry_contrast as rc
    slug = 'metformin-pcos-ovulation'
    cfg = json.loads((ROOT/'topics'/f'{slug}.json').read_text(encoding='utf8'))
    records = json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf8'))['records']
    rec = next(r for r in records if r['id'] == pmid)
    verdict = rc.assess(rec, cfg, {})
    assert verdict['decision'] == 'include'
    assert verdict['source'] == 'record.abstract'


def test_unknown_extra_arm_role_cannot_pass():
    from harness import registry_contrast as rc
    cfg = json.loads((ROOT/'topics'/f'{SLUG}.json').read_text(encoding='utf8'))
    raw = rc.load(cfg)['records'][GOOD[0]]
    arms = rc.aact_arms(raw)
    arms.append(dict(arms[0], role=''))
    assert rc.arm_verdict(arms, rc.terms(cfg)) is None


def test_available_registry_arms_not_labelled_unavailable():
    from harness.page import render_page
    review = json.loads((ROOT/'docs/reviews'/SLUG/'review.json').read_text(encoding='utf8'))
    assert any('Source: registry arms/interventions:' in d.get('reason', '')
               for d in review['screening']['records'])
    html = render_page(review)
    assert 'registry dates, sponsors and arm contrasts are unavailable' not in html
