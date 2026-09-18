from pathlib import Path
import subprocess

from scripts.assertion_literal_sweep import scan_source, sweep, blockers, adjudicate, finding_key

ROOT = Path(__file__).resolve().parents[1]


def test_lit2_verbatim_prefix_plants():
    for name, filename, literal in (
        ('census', 'harness/census.py', 'True'),
        ('search_v2_run', 'scripts/search_v2_run.py',
         'RAN (development run; per-source states in its snapshot ledger)'),
    ):
        pinned = ROOT / '.tmp/lit2' / (name + '-prefixed.py')
        # The local pin preserves the incoming worktree; the committed base also
        # contains these exact plants, so this regression remains portable.
        source = pinned.read_text(encoding='utf8') if pinned.exists() else subprocess.check_output(
            ['git', 'show', '3f8add72:' + filename], cwd=ROOT).decode('utf8')
        assert any(f['kind'] == 'STATUS_CONSTANT' and f['literal'] == literal
                   for f in scan_source(source, filename))


def test_status_assignments_and_serialized_dicts():
    sources = [
        'def emit(x):\n    x["state"] = "RAN_OK"\n    return x\n',
        'def emit(x):\n    x.status = "PASS"\n    return x\n',
        'def emit():\n    x = {"checked": True}\n    return json.dumps(x)\n',
        'json.dump({"status": "PASS"}, stream)\n',
    ]
    for source in sources:
        assert any(f['kind'] == 'STATUS_CONSTANT' for f in scan_source(source, 'plant.py'))


def test_adjudication_is_content_bound_and_true_defects_still_refuse():
    import copy
    import pytest
    finding = scan_source('def render():\n    return {"checked": True}\n', 'plant.py')[0]
    entry = {**finding, 'verdict': 'DEFENSIBLE-CONDITIONED', 'reason': 'Fixture tests a reviewed literal.',
             'by': 'test fixture', 'when_utc': '2000-01-01T00:00:00Z'}
    entries = {finding_key(finding): entry}
    assert not blockers({'findings': adjudicate([copy.deepcopy(finding)], entries)})
    changed = {**finding, 'literal_sha256': 'changed'}
    assert blockers({'findings': adjudicate([changed], entries)})[0]['verdict'] == 'UNADJUDICATED'
    entry['verdict'] = 'TRUE-DEFECT'
    entry['fix'] = 'claimed fixed but still present'
    assert blockers({'findings': adjudicate([copy.deepcopy(finding)], entries)})
    entry['verdict'] = 'ALLOWLIST'
    with pytest.raises(ValueError, match='INVALID_ADJUDICATION'):
        adjudicate([finding], entries)
    entry['verdict'] = 'FALSE-POSITIVE'
    with pytest.raises(ValueError, match='UNSUPPORTED_TEMPLATE'):
        adjudicate([{**finding, 'kind': 'UNSUPPORTED_TEMPLATE'}], entries)


def test_unported_search_state_remains_a_blocking_finding():
    import json
    name = 'scripts/search_v2_run.py'
    fs = scan_source((ROOT / name).read_text(encoding='utf8'), name)
    entries = json.loads((ROOT / 'registry/assertion_literal_adjudications.json').read_text(encoding='utf8'))['adjudications']
    found = [f for f in adjudicate(fs, entries) if f['literal'].startswith('RAN (development run;')]
    assert found and all(f['verdict'] == 'TRUE-DEFECT' for f in found)
    assert blockers({'findings': found})


def test_proposition_checked_tracks_result(monkeypatch):
    from harness import propositions
    monkeypatch.setattr(propositions, 'check_propositions', lambda r: [{'code': 'FIXTURE_CONTRADICTION'}])
    assert propositions.check_document({})['checked'] is False
    monkeypatch.setattr(propositions, 'check_propositions', lambda r: [])
    assert propositions.check_document({})['checked'] is True


def test_unconditional_claim_and_temporal_targets():
    findings = scan_source('def render(obj):\n    return "Publication bias assessed from the trial registry"\nRUN_DATE = "2026-09-15"\n', 'plant.py')
    assert {f['kind'] for f in findings} == {'ASSERTION', 'FIXED_TIME'}


def test_state_alias_and_inline_branch():
    source = 'def render(obj):\n    pub = obj.get("publication_bias") or {}\n    assessed = pub.get("assessed", False)\n    return "Publication bias assessed from registry" if assessed else "Publication bias not assessed automatically"\n'
    assert {f['kind'] for f in scan_source(source, 'plant.py')} == {'CONDITIONED'}


def test_status_word_alone_does_not_establish_a_state_read():
    source = 'def render(label):\n    if label == "verified":\n        return "Publication bias assessed from registry"\n'
    assert scan_source(source, 'plant.py')[0]['kind'] == 'ASSERTION'


def test_docstrings_and_field_keys_are_not_claims():
    assert not scan_source('"""Verified records were not retrieved"""\nx = {"verified": False}\n', 'plant.py')


def test_working_tree_is_fully_adjudicated_and_limb_refuses_unfixed_defects():
    from harness.assertion_literal_limb import limb_assertion_literals
    findings = sweep(ROOT)['findings']
    assert not [f for f in findings if f['verdict'] == 'UNADJUDICATED']
    defects = blockers({'findings': findings})
    assert defects
    verdict, detail = limb_assertion_literals(ROOT)
    assert verdict == 'REFUSED'
    assert all(f"{f['file']}:{f['line']}" in detail for f in defects)


def test_historical_publication_bias_plant():
    source = subprocess.check_output(['git', 'show', '04902ecf^:harness/manuscript.py'], cwd=ROOT).decode('utf8')
    findings = scan_source(source, 'harness/manuscript.py')
    assert any(f['kind'] == 'ASSERTION' and 'publication bias assessed' in f['literal'] for f in findings)


def test_historical_sidecar_data_not_missing_emitter():
    source = subprocess.check_output(['git', 'show', 'c6e1cdef:docs/model_stage_inventory.json'], cwd=ROOT).decode('utf8')
    assert any(f['kind'] == 'FIXED_TIME' and f['literal'] == '2026-09-14'
               for f in scan_source(source, 'docs/model_stage_inventory.json'))


def test_base_search_date_plant():
    source = subprocess.check_output(['git', 'show', '3f8add72:scripts/search_v2_run.py'], cwd=ROOT).decode('utf8')
    assert any(f['kind'] == 'FIXED_TIME' and f['literal'] == '2026-09-15'
               for f in scan_source(source, 'scripts/search_v2_run.py'))


def test_prose_alias_reaches_return():
    source = 'def summary():\n    claim = "Every value was checked against source"\n    output = claim\n    return output\n'
    assert scan_source(source, 'plant.py')[0]['kind'] == 'ASSERTION'


def test_fixed_generation_date_is_not_cleared_by_a_comment():
    source = '# reviewed and approved\ngenerated_utc = "2000-01-01"\n'
    findings = scan_source(source, 'plant.py')
    assert findings[0]['kind'] == 'FIXED_TIME'
    assert blockers({'findings': adjudicate(findings, {})})


def test_manuscript_verification_does_not_infer_arm_checks():
    from harness.manuscript import _verification_phrase
    assert 'UNPROVEN' in _verification_phrase({})
    review = {'outcomes': [{'trials': [{'verified': 'verified'}]}]}
    assert 'positive source-digit verification state' in _verification_phrase(review)
    review['outcomes'][0]['trials'].append({'verified': 'not-yet'})
    assert 'UNPROVEN' in _verification_phrase(review)


def test_unported_funding_retrieval_claim_remains_blocking():
    import json
    name = 'harness/consumer_consistency.py'
    entries = json.loads((ROOT / 'registry/assertion_literal_adjudications.json').read_text(encoding='utf8'))['adjudications']
    findings = adjudicate(scan_source((ROOT / name).read_text(encoding='utf8'), name), entries)
    assert any(f['literal'] == 'not stated in retrieved source' for f in blockers({'findings': findings}))


def test_detector_gap_plants_fire_without_status_words():
    plants = [
        'def render():\n    return "Every page here passed a two-limb gate"\n',
        'def render():\n    return "Every number traces to a committed source"\n',
        'def render():\n    return "No pooled trial is retracted"\n',
        'def render():\n    return "Records identified (committed search)"\n',
        'def scan():\n    return {"claims_checked": count, "surfaces_checked": surfaces}\n',
        'def panel():\n    items = [("method", True, "Every extraction was verified against source")]\n    rows = []\n    for label, ok, text in items:\n        rows.append(text)\n    return "<p>" + "".join(rows) + "</p>"\n',
    ]
    for source in plants:
        assert scan_source(source, 'plant.py'), source


def test_verification_banner_reports_partial_coverage(tmp_path):
    import json
    from harness.index import _verification_section
    target = tmp_path / 'reviews' / 'fixture'
    target.mkdir(parents=True)
    for states in [('verified', 'unknown'), ('verified', 'verified_handchecked')]:
        (target / 'review.json').write_text(json.dumps({'outcomes': [
            {'trials': [{'verified': state} for state in states]}]}), encoding='utf8')
        text = _verification_section(str(tmp_path))
        expected = sum(state in ('verified', 'verified_handchecked') for state in states)
        assert f'{expected} of 2 pooled trial-outcome numbers' in text
        assert 'Every pooled number is verified' not in text
        assert 'independently establish' in text


def test_limb_refuses_unadjudicated_and_stale_source(tmp_path):
    import json
    from harness.assertion_literal_limb import limb_assertion_literals
    (tmp_path / 'harness').mkdir()
    (tmp_path / 'docs').mkdir()
    source = tmp_path / 'harness' / 'plant.py'
    source.write_text('def render():\n    return "Every trial was checked against source"\n', encoding='utf8')
    saved = tmp_path / 'docs/assertion_literal_sweep.json'
    saved.write_text(json.dumps(sweep(tmp_path)), encoding='utf8')
    verdict, detail = limb_assertion_literals(tmp_path)
    assert verdict == 'REFUSED' and 'UNADJUDICATED' in detail
    source.write_text('def render():\n    return "method description"\n', encoding='utf8')
    verdict, detail = limb_assertion_literals(tmp_path)
    assert verdict == 'REFUSED' and 'STALE_ASSERTION_SWEEP' in detail
    saved.write_text(json.dumps(sweep(tmp_path)), encoding='utf8')
    assert limb_assertion_literals(tmp_path)[0] == 'PASS'
