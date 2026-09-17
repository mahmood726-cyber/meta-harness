"""Synthetic preservation plants; never used as research output."""
import copy
import pytest


def fixture_registry(tmp_path):
    from harness.family_compact import compact_registry
    row = {'nct_id': 'NCT00000001', 'acronym': 'FIXTURE', 'start_date': '2000-01-01'}
    full = {'snapshot': '2026-08-30', 'records': {'NCT00000001': {'raw': {'studies': [row]}}}, 'report_links': {}}
    snapshot = tmp_path / '2026-08-30'
    snapshot.mkdir()
    (snapshot / 'studies.txt').write_text('nct_id|acronym|start_date\nNCT00000001|FIXTURE|2000-01-01\n', encoding='utf8')
    return full, compact_registry(full), snapshot


def test_mutated_row_hash_refuses_regeneration(tmp_path):
    from harness.family_compact import compact_registry, regenerate
    row = {'nct_id': 'NCT00000001', 'acronym': 'FIXTURE', 'start_date': '2000-01-01'}
    full = {'snapshot': '2026-08-30', 'records': {'NCT00000001': {'raw': {'studies': [row]}}}, 'report_links': {}}
    compact = compact_registry(full)
    compact['rows'][0]['row_sha256'] = '0' * 64
    snapshot = tmp_path / '2026-08-30'
    snapshot.mkdir()
    (snapshot / 'studies.txt').write_text('nct_id|acronym|start_date\nNCT00000001|FIXTURE|2000-01-01\n', encoding='utf8')
    with pytest.raises(ValueError, match='NOT PRESERVED.*hash'):
        regenerate(compact, snapshot=snapshot)


def test_exact_roundtrip_and_deterministic_sidecars(tmp_path):
    from harness.family_compact import regenerate, read_compact_registry, write_registry
    full, compact, snapshot = fixture_registry(tmp_path)
    path = tmp_path / 'family_registry.json'
    write_registry(path, compact)
    before = {p.name: p.read_bytes() for p in tmp_path.glob('family*')}
    write_registry(path, compact)
    assert before == {p.name: p.read_bytes() for p in tmp_path.glob('family*')}
    assert regenerate(read_compact_registry(path), snapshot=snapshot) == full


@pytest.mark.parametrize('plant', ['missing_row', 'wrong_snapshot', 'inline', 'source_change', 'duplicate', 'missing_table'])
def test_fail_closed_plants(tmp_path, plant):
    from harness.family_compact import regenerate
    _, compact, snapshot = fixture_registry(tmp_path)
    table = snapshot / 'studies.txt'
    if plant == 'missing_row':
        compact['rows'][0]['nct_id'] = 'NCT00000002'
    elif plant == 'wrong_snapshot':
        compact['rows'][0]['snapshot'] = '2025-01-01'
    elif plant == 'inline':
        compact['rows'][0]['inline']['acronym'] = 'TAMPERED'
    elif plant == 'source_change':
        table.write_text(table.read_text(encoding='utf8').replace('FIXTURE', 'CHANGED'), encoding='utf8')
    elif plant == 'duplicate':
        table.write_text(table.read_text(encoding='utf8') + 'NCT00000001|FIXTURE|2000-01-01\n', encoding='utf8')
    else:
        table.unlink()
    with pytest.raises(ValueError, match='NOT PRESERVED'):
        regenerate(compact, snapshot=snapshot)


def test_batch_regeneration_checks_each_topic(tmp_path):
    from harness.family_compact import regenerate_many
    full, compact, snapshot = fixture_registry(tmp_path)
    assert regenerate_many({'a': compact, 'b': copy.deepcopy(compact)}, snapshot) == {'a': full, 'b': full}
    bad = copy.deepcopy(compact)
    bad['rows'][0]['row_sha256'] = '0' * 64
    with pytest.raises(ValueError, match='NOT PRESERVED'):
        regenerate_many({'a': compact, 'b': bad}, snapshot)


def test_inline_family_table_matches_evidence():
    from pathlib import Path
    import json
    from harness.family_compact import read_families
    from harness.page import _trial_families
    root = Path(__file__).resolve().parents[1]
    for path in sorted((root / 'cache').glob('*/families.json')):
        inline = json.loads(path.read_text(encoding='utf8'))
        full = read_families(path)
        assert _trial_families({'trial_families': inline['families'], 'family_count_chain': inline['count_chain']}) == _trial_families({'trial_families': full['families'], 'family_count_chain': full['count_chain']})


def test_glp1_publication_joins_do_not_become_registry_ids():
    from harness import strands
    doc = {'strands': [{'members': [{'id': 'PMID 12345678', 'pmid': '12345678', 'family_id': 'NCT00000001'}]}]}
    assert strands._report_keys(doc) == {'12345678'}
