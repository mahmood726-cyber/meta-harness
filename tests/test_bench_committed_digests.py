"""Pinned benchmark inputs must survive a fresh Git checkout.

Static: topic names and reference-field conventions. Dynamic: pins and blob bytes.
Never pass Git's binary stdout through a text-mode shell pipeline.
"""
import hashlib
import json
from functools import lru_cache
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SLUGS = ('hcq-covid-prophylaxis-bench', 'daratumumab-rrmm-pfs-bench')


@lru_cache(None)
def blob(ref):
    return subprocess.check_output(['git', 'cat-file', '-p', 'HEAD:' + ref], cwd=ROOT)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def pins(value, location=''):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ('sha256', 'source_sha256', 'document_sha256', 'source_article_sha256'):
                fields = {'sha256': ('source_ref', 'source', 'ref'),
                          'source_sha256': ('source_ref',),
                          'document_sha256': ('document_ref',),
                          'source_article_sha256': ('source_article',)}[key]
                ref = next((value[f] for f in fields if isinstance(value.get(f), str)
                            and value[f].startswith(('cache/', 'topics/', 'protocols/'))), None)
                if ref:
                    yield location + '/' + key, ref, item
            yield from pins(item, location + '/' + key)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from pins(item, location + '/' + str(i))


def declarations():
    for slug in SLUGS:
        topic = f'topics/{slug}.json'
        cfg = json.loads((ROOT / topic).read_bytes())
        yield topic, cfg
        for source in cfg.get('benchmark', {}).get('comparator_sources', []):
            ref = source['metadata_ref']
            yield ref, json.loads((ROOT / ref).read_bytes())
        for path in sorted((ROOT / 'cache' / slug).glob('*.json')):
            yield path.relative_to(ROOT).as_posix(), json.loads(path.read_bytes())
        ref = f'cache/{slug}/arm_contrast.json'
        doc = json.loads((ROOT / ref).read_bytes())
        yield ref, dict(source_ref=f'cache/{slug}/records.json', sha256=doc['records_sha256'])
        ref = f'cache/{slug}/raw/INDEX.json'
        ledger = json.loads((ROOT / f'cache/{slug}/retrieval_ledger.json').read_bytes())
        yield ref, dict(source_ref=ref, sha256=ledger['snapshot']['raw_index_sha256'])
        for row in json.loads((ROOT / ref).read_bytes()):
            yield ref, dict(source_ref=f"cache/{slug}/{row['path']}", sha256=row['file_sha256'])
    ref = 'cache/benchmarks/v1/medi-102-e35319-g004.source.json'
    yield ref, json.loads((ROOT / ref).read_bytes())


CASES = [(owner, loc, ref, expected) for owner, obj in declarations()
         for loc, ref, expected in pins(obj)]


@pytest.mark.parametrize('owner,loc,ref,expected', CASES)
def test_pinned_source_matches_committed_blob(owner, loc, ref, expected):
    assert digest(blob(ref)) == expected, (owner, loc, ref)
    assert digest((ROOT / ref).read_bytes()) == expected, (owner, loc, ref, 'working tree')


@pytest.mark.parametrize('slug', SLUGS)
def test_route_records_are_checkout_stable(slug):
    ref = f'cache/{slug}/records.json'
    assert (ROOT / ref).read_bytes() == blob(ref)
