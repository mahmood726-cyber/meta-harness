"""HELDREPLAY plants and offline census; run this file with --census for JSON.

Temporary acquisition files are removed in finally blocks. No Git mutations,
network fetches, cache writes, or served-artifact writes are performed.
"""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import types
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import source_coverage as sc
from harness.canonical import canonical_json, review_core


# The PRE-FIX source_coverage is pinned to the last commit before the tracked-witness fix; 'HEAD' would become the
# fixed module itself once this lands, and the pre-fix plant would silently compare the fix with itself.
PRE_FIX_COMMIT = 'b0ae05a7cf440048ef07338ab2cf756dccf3241a'


def base_module():
    source = subprocess.check_output(
        ['git', '--no-optional-locks', '-C', str(ROOT), 'show', f'{PRE_FIX_COMMIT}:harness/source_coverage.py']
    ).decode('utf-8')
    module = types.ModuleType('heldreplay_base')
    module.__file__ = str(ROOT / 'harness/source_coverage.py')
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    return module


@contextmanager
def plants(*, records=False):
    """Real held bytes, duplicated under an untracked lexically earlier directory."""
    folder = ROOT / sc._HELD / '000_HELDREPLAY_PLANT'
    folder.mkdir()  # Refuse to overwrite a pre-existing directory.
    created = []
    try:
        for suffix in ('local.txt', 'html', 'pdf'):
            p = folder / ('plant.' + suffix)
            p.write_bytes(b'HELDREPLAY synthetic acquisition fixture; not evidence.\n')
            created.append(p)
        if records:
            for original in sorted((ROOT / sc._HELD).glob('*/europepmc_record_*.json')):
                if original.parent == folder:
                    continue
                p = folder / original.name
                if not p.exists():
                    p.write_bytes(original.read_bytes())
                    created.append(p)
        yield folder
    finally:
        for p in created:
            p.unlink()
        folder.rmdir()


def specimen():
    p = next(sorted((ROOT / sc._HELD).glob('*/europepmc_record_*.json')).__iter__())
    record = json.loads(p.read_text(encoding='utf-8'))['resultList']['result'][0]
    return str(record['pmid']), record['abstractText']


def test_untracked_record_cannot_shadow_tracked_witness():
    pid, abstract = specimen()
    base = base_module()
    before = sc.coverage_of(pid, abstract)
    with plants(records=True):
        old_dirty = base.coverage_of(pid, abstract)
        assert old_dirty['verbatim_path'] != before['verbatim_path']
        assert sc.coverage_of(pid, abstract) == before
    assert sc.coverage_of(pid, abstract) == before


def test_ignored_local_text_pdf_html_do_not_change_review_bytes():
    from harness.pipeline import build_review_core
    slug = 'ticagrelor-vs-clopidogrel-acs'
    config = read(ROOT / 'topics' / (slug + '.json'))
    records = read(ROOT / 'cache' / slug / 'records.json')
    sha = read(ROOT / 'docs/reviews' / slug / 'manifest.json')['protocol_sha']
    def build():
        return canonical_json(build_review_core(slug, config, records, sha))
    clean = build()
    with plants():
        assert build() == clean
    assert build() == clean


def test_tracked_witness_is_retained_negative_plant():
    pid, abstract = specimen()
    assert sc.coverage_of(pid, abstract) == base_module().coverage_of(pid, abstract)
    assert sc.coverage_of(pid, abstract)['coverage'] == sc.VERBATIM


def test_untracked_only_witness_is_unverified():
    pid, abstract = specimen()
    with patch.object(sc.subprocess, 'check_output', return_value=b''):
        result = sc.coverage_of(pid, abstract)
    assert result == {'inspected': 'the committed record abstract', 'coverage': sc.UNVERIFIED}


def test_unavailable_git_refuses_named_pmid():
    pid, abstract = specimen()
    with patch.object(sc.subprocess, 'check_output', side_effect=OSError('plant')):
        with pytest.raises(ValueError, match=f'refused PMID {pid}: cannot establish tracked held files'):
            sc.coverage_of(pid, abstract)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def differences(a, b, path='$'):
    if isinstance(a, dict) and isinstance(b, dict):
        return [d for k in sorted(a.keys() | b.keys())
                for d in differences(a.get(k), b.get(k), path + '.' + k)]
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return [d for i, (x, y) in enumerate(zip(a, b))
                for d in differences(x, y, f'{path}[{i}]')]
    return [] if a == b else [{'path': path, 'before': a, 'after': b}]


def census():
    from harness.pipeline import build_review_core
    from harness.page import render_page
    from harness.registration import protocol_sha
    base = base_module()
    pid, abstract = specimen()
    plant_outputs = {'pmid': pid, 'base_clean': base.coverage_of(pid, abstract)}
    with plants(records=True):
        plant_outputs['base_dirty'] = base.coverage_of(pid, abstract)
        plant_outputs['fixed_dirty'] = sc.coverage_of(pid, abstract)
    plant_outputs['fixed_removed'] = sc.coverage_of(pid, abstract)
    rows, failures = [], []
    for topic in sorted((ROOT / 'topics').glob('*.json')):
        slug = topic.stem
        print('CENSUS ' + slug, file=sys.stderr, flush=True)
        try:
            config = read(topic)
            records = read(ROOT / 'cache' / slug / 'records.json')
            served_path = ROOT / 'docs/reviews' / slug / 'review.json'
            served = read(served_path) if served_path.exists() else None
            manifest = ROOT / 'docs/reviews' / slug / 'manifest.json'
            sha = read(manifest)['protocol_sha'] if manifest.exists() else protocol_sha(slug)
            def build():
                return build_review_core(slug, config, records, sha)
            with patch.object(sc, 'verbatim_record', base.verbatim_record):
                before = build()
            clean = build()
            with plants(records=True):
                dirty = build()
                dirty_page = render_page(dirty)
                with patch.object(sc, 'verbatim_record', base.verbatim_record):
                    base_dirty = build()
            removed = build()
            delta = differences(before, clean)
            committed_delta = differences(review_core(served), clean) if served else []
            rows.append({
                'slug': slug, 'clean_sha256': hashlib.sha256(canonical_json(clean).encode()).hexdigest(),
                'base_to_fixed_changes': delta,
                'base_dirty_changes': differences(before, base_dirty),
                'dirty_identical': canonical_json(clean) == canonical_json(dirty),
                'removed_identical': canonical_json(clean) == canonical_json(removed),
                'rendered_identical': render_page(clean) == dirty_page == render_page(removed),
                'served': served is not None,
                'committed_coverage_changes': [d for d in committed_delta if '.source_coverage' in d['path']],
                'committed_other_change_paths': [d['path'] for d in committed_delta if '.source_coverage' not in d['path']],
            })
        except Exception as exc:
            failures.append({'slug': slug, 'error': type(exc).__name__ + ': ' + str(exc)})
    def tally(names, total):
        return {'n': len(names), 'N': total, 'n_of_N': f'{len(names)} of {total}', 'items': names}
    total = len(list((ROOT / 'topics').glob('*.json')))
    served_rows = [r for r in rows if r['served']]
    return {
        'plants': plant_outputs,
        'topics_attempted': total,
        'comparisons_completed': len(rows),
        'rules': {
            'base_untracked_record_changes_review': tally([r['slug'] for r in rows if r['base_dirty_changes']], len(rows)),
            'fixed_dirty_or_removed_changes_review_or_page': tally([r['slug'] for r in rows if not all(r[k] for k in ('dirty_identical', 'removed_identical', 'rendered_identical'))], len(rows)),
            'clean_base_to_fixed_changes': tally([r['slug'] for r in rows if r['base_to_fixed_changes']], len(rows)),
            'committed_review_differs_from_fixed_build': tally([r['slug'] for r in served_rows if r['committed_coverage_changes'] or r['committed_other_change_paths']], len(served_rows)),
            'committed_coverage_differs': tally([r['slug'] for r in served_rows if r['committed_coverage_changes']], len(served_rows)),
            'build_failures': tally([r['slug'] for r in failures], total),
        },
        'topics': rows, 'failures': failures,
    }


if __name__ == '__main__':
    if sys.argv[1:] != ['--census']:
        raise SystemExit('usage: python tests/test_held_replay_independence.py --census')
    result = census()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(result['failures']) or bool(result['rules']['fixed_dirty_or_removed_changes_review_or_page']['n']))
