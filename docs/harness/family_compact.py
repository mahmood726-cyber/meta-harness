"""Offline, snapshot-bound AACT row references and lossless JSON interning.

The inline projection supports the existing family computation without AACT.
Only regenerate() establishes preservation against the local source snapshot.
"""
from __future__ import annotations
import copy
import hashlib
import json
import gzip
from pathlib import Path
from . import aact

SNAPSHOT = '2026-08-30'
FORMAT = 'aact-row-references-v1'
INLINE = {
    'studies': ('nct_id', 'acronym', 'start_date', 'study_first_posted_date', 'completion_date', 'results_first_posted_date'),
    'interventions': ('id', 'nct_id', 'name'),
    'designs': ('nct_id', 'allocation', 'intervention_model', 'masking'),
    'id_information': ('nct_id', 'id_value'),
    'design_outcomes': ('id', 'nct_id', 'measure', 'outcome_type'),
    'outcomes': ('id', 'nct_id', 'title'),
    'outcome_measurements': ('id', 'nct_id', 'outcome_id', 'param_value_num', 'param_value', 'param_type'),
    'outcome_analyses': ('id', 'nct_id', 'outcome_id', 'param_value_num', 'param_value', 'param_type'),
    'study_references': ('id', 'nct_id', 'pmid', 'reference_type'),
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def row_hash(row):
    return hashlib.sha256(canonical(row).encode('utf8')).hexdigest()


def inventory(full):
    rows = {}
    for held in full.get('records', {}).values():
        for table, values in held.get('raw', {}).items():
            table = 'outcome_measurements' if table == 'outcome_measurement_samples' else table
            for row in values:
                rows[canonical(row)] = (table, row)
    for values in full.get('report_links', {}).values():
        for row in values:
            rows[canonical(row)] = ('study_references', row)
    return rows


def intern(value):
    """Intern large evidence objects/strings once in a shared JSON object table."""
    objects, seen = [], {}
    def visit(v):
        if isinstance(v, dict):
            v = {k: visit(x) for k, x in v.items()}
        elif isinstance(v, list):
            v = [visit(x) for x in v]
        elif not isinstance(v, str):
            return v
        key = canonical(v)
        if len(key) < 120:
            return v
        if key in seen:
            return {'$object': seen[key]}
        seen[key] = len(objects)
        objects.append(v)
        return {'$object': seen[key]}
    return {'data': visit(value), 'objects': objects}


def expand(packed):
    objects = packed['objects']
    def visit(v, ancestors=frozenset()):
        if isinstance(v, dict):
            if set(v) == {'$object'}:
                i = v['$object']
                if not isinstance(i, int) or i < 0 or i >= len(objects) or i in ancestors:
                    raise ValueError('NOT PRESERVED: invalid object reference')
                return visit(objects[i], ancestors | {i})
            return {k: visit(x, ancestors) for k, x in v.items()}
        if isinstance(v, list):
            return [visit(x, ancestors) for x in v]
        return v
    return visit(packed['data'])


def compact_registry(full):
    if full.get('snapshot') != SNAPSHOT:
        raise ValueError('NOT PRESERVED: unexpected snapshot')
    known = inventory(full)
    rows, indexes = [], {}
    for encoded, (table, row) in sorted(known.items(), key=lambda item: (item[1][0], item[0])):
        digest = row_hash(row)
        # Surrogate IDs are scoped to this exact snapshot, never cross-snapshot identities.
        key = {'id': row['id']} if row.get('id') else {'nct_id': row['nct_id']}
        indexes[encoded] = len(rows)
        rows.append({'table': table, 'nct_id': row['nct_id'], 'row_key': key,
                     'row_sha256': digest, 'snapshot': SNAPSHOT,
                     'inline': {k: row[k] for k in INLINE.get(table, ('nct_id',)) if k in row}})
    def visit(v):
        if isinstance(v, dict):
            i = indexes.get(canonical(v))
            if i is not None:
                return {'$row': i}
            return {k: visit(x) for k, x in v.items()}
        if isinstance(v, list):
            return [visit(x) for x in v]
        return v
    return {'format': FORMAT, 'snapshot': SNAPSHOT, 'rows': rows, 'payload': intern(visit(full))}


def materialize(doc, source_rows=None):
    if doc.get('format') != FORMAT:
        return copy.deepcopy(doc)
    def visit(v):
        if isinstance(v, dict):
            if set(v) == {'$row'}:
                i = v['$row']
                if not isinstance(i, int) or i < 0 or i >= len(doc['rows']):
                    raise ValueError('NOT PRESERVED: invalid row reference')
                ref = doc['rows'][i]
                if source_rows is not None:
                    return copy.deepcopy(source_rows[i])
                # Keep the reference alongside the operational fields in evidence spans.
                return dict(ref['inline'], source_reference={k: ref[k] for k in
                            ('table', 'nct_id', 'row_key', 'row_sha256', 'snapshot')})
            return {k: visit(x) for k, x in v.items()}
        if isinstance(v, list):
            return [visit(x) for x in v]
        return v
    return visit(expand(doc['payload']))


def regenerate(doc, snapshot=None):
    """Rebuild all original rows; any missing/mutated reference refuses the entire result."""
    if doc.get('format') != FORMAT or doc.get('snapshot') != SNAPSHOT:
        raise ValueError('NOT PRESERVED: unsupported registry/snapshot')
    path = Path(snapshot or aact.snapshot_dir() or '')
    if not path.is_dir() or path.name != SNAPSHOT:
        raise ValueError('NOT PRESERVED: required snapshot unavailable')
    wanted = {}
    for i, ref in enumerate(doc['rows']):
        if ref['snapshot'] != SNAPSHOT or not ref['row_key'] or not ref['nct_id']:
            raise ValueError('NOT PRESERVED: invalid row identity/snapshot')
        table = ref['table']
        if not table.isidentifier():
            raise ValueError('NOT PRESERVED: invalid table')
        wanted.setdefault(table, {}).setdefault(ref['nct_id'], []).append((i, ref))
    found = {}
    for table, by_nct in sorted(wanted.items()):
        table_path = path / (table + '.txt')
        if not table_path.is_file():
            raise ValueError('NOT PRESERVED: missing table ' + table)
        for row in aact._iter_rows(str(table_path)):
            for i, ref in by_nct.get(row.get('nct_id'), []):
                if all(row.get(k) == v for k, v in ref['row_key'].items()):
                    if row_hash(row) != ref['row_sha256']:
                        raise ValueError('NOT PRESERVED: row hash mismatch ' + table + ' ' + ref['nct_id'])
                    if ref['inline'] != {k: row[k] for k in INLINE.get(table, ('nct_id',)) if k in row}:
                        raise ValueError('NOT PRESERVED: inline projection mismatch')
                    if i in found:
                        raise ValueError('NOT PRESERVED: ambiguous row key')
                    found[i] = row
    if len(found) != len(doc['rows']):
        raise ValueError('NOT PRESERVED: snapshot cannot produce every referenced row')
    return materialize(doc, found)


def regenerate_many(documents, snapshot=None):
    """Verify a cohort in one streaming pass per source table, without changing row identity."""
    rows, seen, payload = [], {}, {}
    for slug, doc in sorted(documents.items()):
        if doc.get('format') != FORMAT or doc.get('snapshot') != SNAPSHOT:
            raise ValueError('NOT PRESERVED: unsupported registry/snapshot')
        indexes = {}
        for i, ref in enumerate(doc['rows']):
            key = canonical(ref)
            if key not in seen:
                seen[key] = len(rows)
                rows.append(ref)
            indexes[i] = seen[key]
        def remap(v):
            if isinstance(v, dict):
                if set(v) == {'$row'}:
                    return {'$row': indexes[v['$row']]}
                return {k: remap(x) for k, x in v.items()}
            if isinstance(v, list):
                return [remap(x) for x in v]
            return v
        payload[slug] = remap(expand(doc['payload']))
    return regenerate({'format': FORMAT, 'snapshot': SNAPSHOT, 'rows': rows, 'payload': intern(payload)}, snapshot)


def read_registry(path):
    return materialize(read_compact_registry(path))


def read_compact_registry(path):
    path = Path(path)
    doc = json.loads(path.read_text(encoding='utf8'))
    if doc.get('format') == FORMAT:
        for key in ('rows', 'payload'):
            if isinstance(doc[key], str):
                name = doc[key]
                if Path(name).name != name:
                    raise ValueError('NOT PRESERVED: invalid sidecar path')
                doc[key] = json.loads(gzip.decompress((path.parent / name).read_bytes()))
    return doc


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf8', newline='\n')


def compact_families(doc):
    # Preserve all source/provenance data by interning; page-facing values stay inline.
    inline = []
    for f in doc['families']:
        inline.append({
            'family_id': f['family_id'], 'aliases': {'acronym': f['aliases']['acronym']},
            'reports': [{k: r[k] for k in ('report_id', 'role')} for r in f['reports']],
            'arms': [{'arm_id': a['arm_id'], 'label': {'value': a.get('label', {}).get('value')}} for a in f['arms']],
            'arm_absence_code': f['arm_absence_code'],
            'randomised_contrasts': [{k: c[k] for k in ('drug', 'arm_ids')} for c in f['randomised_contrasts']],
            'eligibility': {'state': f['eligibility']['state']},
            'lifecycle': {k: {x: v[x] for x in ('value', 'absence_code') if x in v} for k, v in f['lifecycle'].items()},
            'outcome_status': [{'outcome': s['outcome'], **{k: {'state': s[k]['state']} for k in
                ('prospectively_specified', 'measured', 'reported', 'extractable', 'in_primary_pool')}} for s in f['outcome_status']],
        })
    return {'schema_version': 2, 'format': 'family-evidence-interned-v1',
            'count_chain': doc['count_chain'], 'families': inline, 'evidence': intern(doc)}


def read_families(path):
    path = Path(path)
    doc = json.loads(path.read_text(encoding='utf8'))
    if doc.get('format') != 'family-evidence-interned-v1':
        return doc
    evidence = doc['evidence']
    if isinstance(evidence, str):
        if Path(evidence).name != evidence:
            raise ValueError('NOT PRESERVED: invalid evidence path')
        evidence = json.loads(gzip.decompress((path.parent / evidence).read_bytes()))
    result = expand(evidence)
    registry = read_compact_registry(path.with_name('family_registry.json'))
    # Family evidence shares the same source-row reference catalogue as its registry.
    result = materialize(dict(registry, payload=intern(result)))
    # JSON member order is not evidence, but retain the inline page's lifecycle order.
    inline = {f['family_id']: f for f in doc['families']}
    for family in result['families']:
        family['lifecycle'] = {k: family['lifecycle'][k] for k in inline[family['family_id']]['lifecycle']}
    return result


def write_gzip(path, value):
    data = json.dumps(value, separators=(',', ':'), ensure_ascii=False).encode('utf8')
    Path(path).write_bytes(gzip.compress(data, mtime=0))


def write_registry(path, doc):
    path = Path(path)
    output = copy.deepcopy(doc)
    for key in ('rows', 'payload'):
        name = 'family_registry.' + key + '.json.gz'
        write_gzip(path.with_name(name), output[key])
        output[key] = name
    # Stable report joins stay inspectable without opening the evidence sidecar.
    links = materialize(doc).get('report_links', {})
    if 'report_links' in doc and doc['report_links'] != links:
        raise ValueError('NOT PRESERVED: report-link projection mismatch')
    # Preserve the already held member order when round-tripping an acquisition cache.
    output['report_links'] = doc.get('report_links', links)
    write_json(path, output)


def write_families(path, doc, full_registry=None):
    path = Path(path)
    compact = read_compact_registry(path.with_name('family_registry.json'))
    lookup = {r['row_sha256']: i for i, r in enumerate(compact['rows'])}
    def visit(v):
        if isinstance(v, dict):
            # Full rows imported from FN and projected rows produced during replay.
            ref = v.get('source_reference')
            digest = ref['row_sha256'] if ref else row_hash(v)
            if digest in lookup:
                return {'$row': lookup[digest]}
            return {k: visit(x) for k, x in v.items()}
        if isinstance(v, list):
            return [visit(x) for x in v]
        return v
    output = compact_families(doc)
    output['evidence'] = 'families.evidence.json.gz'
    write_gzip(path.with_name(output['evidence']), intern(visit(doc)))
    write_json(path, output)
