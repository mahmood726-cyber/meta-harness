"""SHA-verified deterministic lane excerpts, emitted to stdout only.

The lane's explicit file allowlist excludes new evidence files. render() returns
one independently hashed excerpt per row for the integrator to commit; the lane
report embeds the same bytes. This command never updates served artifacts.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from harness.effect_definition_binding import extract_documents

SOURCES = {
    'medical': ('PLATO-regulatory/022433Orig1s000MedR',
                '2222a5139d2a2f6cc1432dcf925a152d2fe0fbe77eecb28c1fd84bee98979010',
                '375bfc0adbb0066470b0137b24b1e2d103d922981ecb9321848fe08e5bf276f0'),
    'statistical': ('PLATO-regulatory/022433Orig1s000StatR',
                    'f8ec365d90d071e98a49cf5bee808c649b41a0d9750d92c9fcb1e339ab006a17',
                    'f6d8bb64d5d1582949e0b5dac611723351b417dd66c80e0860a6a8c60ee0ac49'),
    'philo': ('PHILO/unpaywall',
              '6d5c10e40a00e9eb88be44796b9213b480f628f7862243333219c0a019494267',
              'f0409c6c544f2ec3ecfd181511751dfbbaa700dafa8ad2cba7d7a9b241c15e19'),
}


def read_sources(root=ROOT):
    documents = {}
    for key, (stem, pdf_sha, text_sha) in SOURCES.items():
        base = Path(root) / 'evidence/acquisition_cascade/held' / stem
        for suffix, sha in (('.pdf', pdf_sha), ('.local.txt', text_sha)):
            path = base.with_suffix(suffix)
            if not path.is_file():
                raise ValueError('REFUSED MISSING_HELD_SOURCE: ' + path.name)
            if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
                raise ValueError('REFUSED SOURCE_SHA_MISMATCH: ' + path.name)
        path = base.with_suffix('.local.txt')
        documents[key] = {'source': path.relative_to(root).as_posix(),
                          'text': path.read_text(encoding='utf-8'),
                          'text_sha256': text_sha, 'pdf_sha256': pdf_sha}
    return documents


def render(root=ROOT):
    rows, _ = extract_documents(read_sources(root))
    excerpts = {}
    for row in rows:
        # Exactly one result row per excerpt, including PHILO.
        payload = (f'# {row.trial}; {row.source}; PDF page {row.page}\n'
                   f'# text sha256 {row.source_sha256}; characters {row.start}:{row.end}\n'
                   f'# label: {row.label}\n# binding_state: {row.binding_state}\n'
                   f'# definition: {row.definition}\n{row.quote}\n').encode('utf-8')
        key = f'{row.trial}-p{row.page}-c{row.start}'
        excerpts[key] = {'sha256': hashlib.sha256(payload).hexdigest(), 'text': payload.decode('utf-8')}
    return excerpts


if __name__ == '__main__':
    print(json.dumps(render(), ensure_ascii=False, sort_keys=True, indent=2))
