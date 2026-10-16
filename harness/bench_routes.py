"""Opt-in benchmark locators. Values are re-read, then checked against source-generated pins.

Static: topic/report identities and endpoint/analysis anchors.
Dynamic: held spans, effects, confidence limits and document hashes.
"""
import hashlib
import json
from pathlib import Path
from . import extract

ROOT = Path(__file__).resolve().parents[1]
KEY = 'daratumumab_rrmm_pfs'
SLUG = 'daratumumab-rrmm-pfs-bench'
ROUTES = {
    '32482541': 'Median progression-free survival (PFS) was significantly prolonged',
    '32001798': 'D-Rd prolonged progression-free survival (PFS) in the intent-to-treat population',
    '40680754': 'Analysis of progression-free survival 2 showed',
}

def load_pins(root):
    return json.loads((Path(root)/'tests/fixtures/r3_bench_route_pins.json').read_text(encoding='utf8'))

def for_config(config, *, root=ROOT):
    if not config.get('typed_routes'):
        return {}
    if config['typed_routes'] != KEY or config.get('slug') != SLUG:
        raise ValueError('Unknown or mis-scoped typed route declaration')
    outcome = config['primary_outcome']['name']
    if outcome != 'Progression-free survival':
        raise ValueError('Typed route endpoint mismatch')
    ref = f'cache/{SLUG}/records.json'
    raw = (Path(root)/ref).read_bytes()
    records = json.loads(raw)['records']
    pins = load_pins(root)
    result = {}
    for pid, anchor in ROUTES.items():
        base = dict(outcome=outcome, override=True, document_ref=ref,
                    document_sha256=hashlib.sha256(raw).hexdigest(), source_level=1)
        try:
            pin = pins[pid]
            hits = [r for r in records if str(r.get('id')) == pid]
            if len(hits) != 1:
                raise ValueError('TYPED_ROUTE_REPORT_AMBIGUOUS')
            text = hits[0]['abstract']
            if pin['anchor'] != anchor or text.count(anchor) != 1:
                raise ValueError('TYPED_ROUTE_ANCHOR_UNBOUND')
            start = text.index(anchor)
            match = extract._EFFECT.search(extract._norm(text), start)
            if match is None:
                raise ValueError('TYPED_ROUTE_EFFECT_UNBOUND')
            span = text[start:match.end()]
            value = extract._effect_from_match(match, span)
            if value is None:
                raise ValueError('TYPED_ROUTE_EFFECT_INVALID')
            value = dict(zip(('scale', 'effect', 'ci_low', 'ci_high'), value))
            if span != pin['span'] or value != pin['value']:
                raise ValueError('TYPED_ROUTE_VALUE_MISMATCH')
            base.update(source=span, source_span=span)
            if pid == '40680754':
                raise ValueError('ENDPOINT_UNBOUND: held update reports PFS2, not PFS')
            result[pid] = dict(base, **value, provenance='abstract_verified')
        except (KeyError, TypeError, ValueError) as error:
            result[pid] = dict(base, absent=True, kind='typed_refusal',
                               provenance='REFUSED_ON_EVIDENCE',
                               reason_code='REFUSED_ON_EVIDENCE', reason=str(error))
    return result
