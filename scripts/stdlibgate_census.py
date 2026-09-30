"""Offline all-topic parser census and reproducible equivalence snapshot."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import proposal_gate as gate


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def snapshot():
    registry = json.loads((ROOT / gate.DOCUMENT_REGISTRY).read_text(encoding='utf-8'))['documents']
    docs, missing, proposals = [], [], {}
    for row in registry:
        path = ROOT / row['document_ref']
        if not path.is_file():
            missing.append(row['document_ref'])
            continue
        raw = path.read_text(encoding='utf-8')
        normalized = gate.normalise_document(raw, row['media_type'])
        tables = gate._table_rows(raw, row['media_type'])
        docs.append(dict(document_ref=row['document_ref'], slug=row['slug'],
                         normalized_sha256=hashlib.sha256(normalized.encode('utf-8')).hexdigest(),
                         tables_sha256=digest(tables), rows=len(tables[0]), errors=tables[1]))
    for name in ('toci', 'sema'):
        if name == 'toci':
            import ast
            import types
            import re
            source = ROOT / 'scripts/g1_toci_comparator.py'
            tree = ast.parse(source.read_text(encoding='utf-8'))
            names = {'one', 'text', 'normalized', 'extract', 'proposal'}
            nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
            ns = dict(gate=gate, re=re, hashlib=hashlib,
                      SLUG='tocilizumab-covid19-mortality',
                      HELD='evidence/acquisition_cascade/held/WHO-REACT/PMC8261689.local.html')
            exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), 'exec'), ns)
            builder = types.SimpleNamespace(**ns)
            path = ROOT / builder.HELD
            if not path.is_file():
                proposals[name] = {'missing': str(path.relative_to(ROOT))}
                continue
            raw = path.read_bytes()
            p = builder.proposal(builder.extract(raw), raw)
        else:
            from scripts import g1_sema_comparator as builder
            manifest = builder.read(ROOT / 'comparator_refs/MANIFEST.json')[builder.SLUG]
            path = ROOT / 'comparator_refs' / manifest['file']
            if not path.is_file():
                proposals[name] = {'missing': str(path.relative_to(ROOT))}
                continue
            item, tree = builder.load()
            trials, _, _ = builder.extract(tree)
            p = builder.proposal(item, trials, tree)
        result = gate.verify(p, ROOT)
        proposals[name] = dict(proposal_sha256=digest(p), verify_sha256=digest(result),
                               fields=result['fields'], status=result['status'], reason=result['reason'])
    topics = sorted(p.stem for p in (ROOT / 'topics').glob('*.json'))
    items = [s for s in topics if any(d['slug'] == s for d in docs)]
    errors = [d for d in docs if d['errors']]
    return dict(documents=docs, missing=missing, proposals=proposals,
                census=dict(topics_examined=topics, registered_document_coverage=dict(
                    n=len(items), N=len(topics), n_of_N=f'{len(items)} of {len(topics)}', items=items),
                    table_refusals=dict(n=len(errors), N=len(docs),
                        n_of_N=f'{len(errors)} of {len(docs)}', items=errors)))


if __name__ == '__main__':
    print(json.dumps(snapshot(), ensure_ascii=False, indent=2))
