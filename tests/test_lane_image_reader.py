"""Synthetic plants: no paper data or live runner."""
from pathlib import Path
from PIL import Image
from scripts import lane_image_reader as lr

OPEN = '<permissions><license href="https://creativecommons.org/licenses/by/4.0/">CC BY</license></permissions>'


def test_hash_mismatch_never_calls(tmp_path):
    p = tmp_path / 'x.png'
    Image.new('RGB', (2, 2)).save(p)
    calls = []
    out = lr.read_image(p, '0' * 64, OPEN, runner=lambda *a, **k: calls.append(1))
    assert out['state'] == 'HASH_MISMATCH' and not calls


def test_closed_never_calls(tmp_path):
    p = tmp_path / 'x.png'
    Image.new('RGB', (2, 2)).save(p)
    for xml in ['<permissions>All rights reserved</permissions>', OPEN.replace('/by/', '/by-nc/')]:
        calls = []
        out = lr.read_image(p, lr.digest(p), xml, runner=lambda *a, **k: calls.append(1))
        assert out['state'] == 'LICENCE_REFUSED' and not calls


def test_dedupe():
    rows = [dict(file='a.jpg', sha256='a', meta='1', topic='x'),
            dict(file='a.jpg', sha256='a', meta='1', topic='y'),
            dict(file='a.gif', sha256='b', meta='1', topic='x')]
    groups = lr.dedupe(rows)
    assert len(groups) == 1 and groups[0]['file'] == 'a.jpg'
    assert len(groups[0]['sources']) == 3


def test_tiff_hashes_and_pixels(tmp_path):
    p = tmp_path / 'x.tif'
    Image.new('RGB', (3, 4), (2, 3, 4)).save(p)
    q, hashes = lr.prepare_image(p)
    assert hashes == {'source_sha256': lr.digest(p), 'attached_sha256': lr.digest(q)}
    assert q.suffix == '.png'
    assert Image.open(p).tobytes() == Image.open(q).tobytes()


def test_reader_a_is_never_secondary():
    out = lr.funnel([{'state': 'READER_A_ONLY', 'rows': [{'label': 'trial'}],
                      'candidates': [{'topic': 'x', 'trial': 'trial'}]}], 11)
    assert out['secondary'] == 0
    assert out['read'] == {'n': 1, 'N': 1}


def test_mocked_recorded_runner(tmp_path, monkeypatch):
    import json
    from scripts import g1_forest_reader as fr
    p = tmp_path / 'x.png'
    Image.new('RGB', (2, 2)).save(p)
    answer = dict(legible=False, row_kind='none', measure='', model_printed=None,
                  rows=[], pooled=dict(label=None, effect=None, lower=None, upper=None), notes='synthetic')
    calls = []
    def runner(*a, **kw):
        calls.append(kw['images'])
        return dict(rc=0, stdout=b'', stderr=f'--------\nmodel: {fr.CODEX_MODEL}\n--------\n'.encode(),
                    last_message=json.dumps(answer).encode(), argv=['mock'])
    monkeypatch.setattr(lr, 'REC_DIR', tmp_path / 'records')
    out = lr.read_image(p, lr.digest(p), OPEN, runner=runner)
    assert calls == [(p,)]
    assert out['state'] == 'READER_A_ONLY' and out['record_id']


def test_metadata_never_grants_a_model_read():
    # was test_metadata_fallback_requires_open_grant: it asserted the lane's metadata fallback (a parallel licence rule,
    # removed by the coverage lane 15 Oct). The requirement: classify_permissions alone decides.
    from harness import copy_licence
    xml = '<permissions>Creative Commons Attribution License (CC BY)</permissions>'
    assert lr.checked_licence(xml, 'cc by')[0] == copy_licence.classify_permissions(xml)[0]
    assert lr.checked_licence(xml, 'cc by-nc')[0] == copy_licence.classify_permissions(xml)[0]
    assert lr.checked_licence('<permissions>All rights reserved</permissions>', 'cc by')[0] == 'NOT_OPEN'
    assert lr.checked_licence(OPEN.replace('/by/', '/by-nc/'), 'cc by')[0] == 'CC_RESTRICTED'


def test_auth_preflight_fails_closed(monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setattr(lr.subprocess, 'run', lambda *a, **kw: SimpleNamespace(returncode=1, stdout=b'', stderr=b'Not logged in'))
    assert lr.client_preflight()['state'] == 'AUTH_REQUIRED'


def test_a_words_only_cc_by_with_open_metadata_is_not_a_model_read():
    # 34484209 shape: permissions say 'Creative Commons Attribution' in words, no licence URL; Europe PMC metadata says
    # 'cc by'. The one licence rule (copy_licence.classify_permissions) decides; metadata never grants a model read.
    xml = ("<article><front><article-meta><permissions><license><license-p>This is an open access article under the "
           "Creative Commons Attribution License.</license-p></license></permissions></article-meta></front></article>")
    from harness import copy_licence
    assert lr.checked_licence(xml, metadata_license="cc by")[0] == copy_licence.classify_permissions(xml)[0]


# ---- D8 ruling (Dispatch, on Mahmood's delegation, 15 Oct 23:50): an explicit, unambiguous CC BY statement in the text
# counts as CC BY without a URL -- recorded PER DOCUMENT (verbatim statement, location, sha256), never as a new rule ----
def test_a_recorded_document_ruling_opens_exactly_that_document(tmp_path, monkeypatch):
    import hashlib, json as _json
    stmt = ("This is an open-access article distributed under the terms of the Creative Commons Attribution License "
            "(CC BY).")
    xml = f"<article><front><article-meta><permissions><license><license-p>{stmt}</license-p></license></permissions></article-meta></front></article>"
    sha = hashlib.sha256(xml.encode("utf-8")).hexdigest()
    rulings = tmp_path / "rulings.json"
    rulings.write_text(_json.dumps({"rulings": {sha: {"verbatim_statement": stmt, "location": "permissions/license/license-p",
                                                       "ruling": "D8 23:50 15 Oct"}}}), encoding="utf-8")
    monkeypatch.setattr(lr, "LICENCE_RULINGS", rulings)
    assert lr.checked_licence(xml, "cc by", jats_sha256=sha)[0] == "CC"
    # another document with the same words but a different sha is NOT opened by that ruling
    assert lr.checked_licence(xml + " ", "cc by", jats_sha256=sha[::-1])[0] != "CC"
    # the same sha whose text no longer carries the verbatim statement is refused (the ruling is bound to the words)
    assert lr.checked_licence(xml.replace("(CC BY)", "(CC BY-NC)"), "cc by", jats_sha256=sha)[0] != "CC"
