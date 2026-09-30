"""Offline G1SEMA table extraction, native-gate replay and all-topic census.

Run with --write to write only .tmp/g1sema artifacts; otherwise prints census.
Bibliography typed-element logic adapted from lanes/G1REFS2/harness/jats_refs.py:
that module cannot import here because harness.comparator_refs is not held.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
from html import escape
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from harness import proposal_gate as gate, identity_join, meta_match

SLUG = 'semaglutide-obesity-mace'
MEDIA = 'application/jats+xml'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def text(node):
    return gate.flat(''.join(node.itertext())) if node is not None else ''


def xml(node):
    return ET.tostring(node, encoding='unicode')


def integer(value):
    if not re.fullmatch(r'(?:[1-9]\d*|[1-9]\d{0,2}(?:,\d{3})+)', value):
        raise ValueError('REFUSED_COUNT_TOKEN:' + value)
    return int(value.replace(',', ''))


def drug_scope(value):
    drugs = sorted(set(re.findall(r'\b(?:semaglutide|liraglutide|tirzepatide)\b', value.lower())))
    if drugs == ['semaglutide']:
        return 'SEMAGLUTIDE_ONLY'
    return 'REFUSED_MIXED_DRUG_ARMS' if 'semaglutide' in drugs else 'REFUSED_DIFFERENT_DRUG:' + ','.join(drugs)


def mace_flag(header, value):
    if header != 'MACE':
        raise ValueError('REFUSED_DIFFERENT_ENDPOINT:' + header)
    if value not in ('+', ''):
        raise ValueError('REFUSED_OUTCOME_MARKER:' + value)
    return value == '+'


def binding(row, field, candidate):
    """Exact structural witness comparison, independent of lexical gate acceptance."""
    expected = row['fields'][field]
    if candidate != expected:
        raise ValueError('REFUSED_OTHER_ROW_OR_COLUMN:' + field)
    return expected


def validate_ledger(ledger, expected):
    paths = [r['path'] for r in ledger]
    if len(paths) != len(set(paths)) or set(paths) != set(expected):
        raise ValueError('REFUSED_ROW_DENOMINATOR_DUPLICATE_OR_MISSING')


def bibliography(ref):
    # G1REFS2 typed pub-id, article-title, first surname and year logic.
    out = {}
    for key, tag in [('title', 'article-title'), ('first_author', 'surname'), ('year', 'year')]:
        values = [text(e) for e in ref.iter(tag)]
        if values:
            if key != 'first_author' and len(set(values)) != 1:
                raise ValueError('REFUSED_AMBIGUOUS_REFERENCE:' + key)
            out[key] = values[0]
    for key, pattern in [('pmid', r'\d{6,9}'), ('doi', r'10\.\d{4,9}/\S+')]:
        values = {text(e) for e in ref.iter('pub-id') if e.get('pub-id-type') == key}
        if len(values) > 1 or any(not re.fullmatch(pattern, v) for v in values):
            raise ValueError('REFUSED_REFERENCE_IDENTIFIER:' + key)
        if values:
            out[key] = next(iter(values))
    return out


def extract(tree):
    tables, ledger, trials = tree.findall('.//table-wrap'), [], []
    refs = {e.get('id'): e for e in tree.findall('.//ref-list/ref')}
    pooled = None
    for ti, table in enumerate(tables):
        trs = table.findall('.//tr')
        headers = [text(c) for c in trs[0]]
        for ri, tr in enumerate(trs):
            cells = list(tr)
            path = f'table[{ti}]/tr[{ri}]'
            ledger.append(dict(path=path, kind='header' if ri == 0 else 'trial' if 'Trial name' in headers else 'pooled_outcome', label=text(cells[0])))
            if ri == 0:
                continue
            if len(cells) != len(headers) or any(c.get('rowspan', '1') != '1' or c.get('colspan', '1') != '1' for c in cells):
                raise ValueError('REFUSED_TABLE_GRID:' + path)
            fields = {h: dict(value=text(c), path=f'{path}/cell[{ci}]', header=h, span=xml(c)) for ci, (h, c) in enumerate(zip(headers, cells))}
            if 'Trial name' not in headers:
                if fields.get('Clinical outcome', {}).get('value') == 'MACE':
                    if pooled is not None:
                        raise ValueError('REFUSED_AMBIGUOUS_MACE_ROW')
                    pooled = dict(k=integer(fields['Number of RCTs']['value']), fields=fields, path=path)
                continue
            label_cell = copy.deepcopy(cells[headers.index('Trial name')])
            for parent in label_cell.iter():
                for child in list(parent):
                    if child.tag == 'xref':
                        parent.remove(child)
            label_text = gate.flat(' '.join(label_cell.itertext())).strip(' ,')
            ncts = re.findall(r'\bNCT\d{8}\b', label_text)
            label = re.sub(r'\bNCT\d{8}\b', '', label_text).strip(' ,')
            rid = [x.get('rid') for x in cells[0].iter('xref') if x.get('ref-type') == 'bibr']
            if not rid or any(x not in refs for x in rid):
                raise ValueError('REFUSED_REFERENCE_NOT_HELD:' + label)
            references = [dict(rid=x, path=f"ref[@id='{x}']", **bibliography(refs[x])) for x in rid]
            if gate.RELAYED.search(gate.normalise_document(xml(tr), MEDIA)):
                raise ValueError('REFUSED_RELAYED_NOT_DATA:' + path)
            trials.append(dict(label=label, registration=ncts[0] if len(ncts) == 1 else None,
                               path=path, fields=fields, references=references, span=xml(tr),
                               n_active=integer(fields['Active (n)']['value']),
                               n_total=integer(fields['Total population (n)']['value']),
                               drug_scope=drug_scope(fields['Medication/type']['value']),
                               mace=mace_flag('MACE', fields['MACE']['value'])))
    if pooled is None:
        raise ValueError('REFUSED_MACE_SUMMARY_NOT_HELD')
    validate_ledger(ledger, [f'table[{ti}]/tr[{ri}]' for ti,t in enumerate(tables) for ri,_ in enumerate(t.findall('.//tr'))])
    return trials, ledger, pooled


def load(root=ROOT):
    item = read(root / 'comparator_refs/MANIFEST.json')[SLUG]
    if item.get('isOpenAccess') != 'Y' or not item.get('licence'):
        raise ValueError('REFUSED_NON_OA_JATS')
    filename = item['file']
    if Path(filename).name != filename or '/' in filename or '\\' in filename:
        raise ValueError('REFUSED_MANIFEST_PATH')
    raw = (root / 'comparator_refs' / filename).read_bytes()
    if hashlib.sha256(raw).hexdigest() != item['sha256']:
        raise ValueError('REFUSED_SHA256_MISMATCH')
    gate.normalise_document(raw.decode('utf-8'), MEDIA)
    tree = ET.fromstring(raw)
    pmids = [text(e) for e in tree.findall('./front/article-meta/article-id') if e.get('pub-id-type') == 'pmid']
    if pmids != [item['pmid']] or len(tree.findall('.//ref-list/ref')) != item['n_refs']:
        raise ValueError('REFUSED_DOCUMENT_IDENTITY_OR_REF_COUNT')
    return item, tree


def proposal(item, trials, tree):
    p = dict(slug=SLUG, comparator_pmid=item['pmid'], document_ref='comparator_refs/' + item['file'],
             document_sha256=item['sha256'], proposed_by='deterministic G1SEMA JATS parser',
             scope_note='All-incretin comparator; included studies are not semaglutide-only MACE inputs.',
             trial_set_scope='included_studies_only', trial_set_complete=False,
             primary_scope=dict.fromkeys(gate.SCOPE), pooled=dict.fromkeys(gate.POOLED), trials=[],
             not_found=['CONTROL_N_NOT_PRINTED', 'TRIAL_MACE_COUNTS_AND_EFFECTS_NOT_TABULATED',
                        'ARMS_FOLLOWUP_AND_PATHS_NOT_IN_NATIVE_SCHEMA: see extracted.json'])
    p['primary_scope'].update(outcome_as_printed='MACE', span='MACE')
    p['pooled']['span'] = ''
    # Use the printed contiguous MACE narrative for native k/effect roles.
    spans = [xml(e) for e in tree.findall('.//p') if re.search(r'MACE\s*\(\d+ RCTs', gate.normalise_document(xml(e), MEDIA))]
    if len(spans) == 1:
        span = spans[0]
        normalized = gate.normalise_document(span, MEDIA)
        selected = re.search(r'MACE\s*\(\d+ RCTs;.*?(?=\s+and all-cause mortality)', normalized)
        own = selected[0] if selected else ''
        k = list(gate.K.finditer(own))
        estimate = gate.parse_estimate(own)
        p['pooled'].update(estimate, span=span, field_spans={k:escape(own) for k in gate.POOLED})
        if len(k) == 1:
            p['pooled']['k'] = int(k[0][1])
    for row in trials:
        r = dict.fromkeys(gate.TRIAL)
        r.update(label=row['label'], registration=row['registration'], span=row['span'],
                 field_spans=dict(label=row['fields']['Trial name']['span']))
        if row['registration']:
            r['field_spans']['registration'] = row['fields']['Trial name']['span']
        # Mixed-drug active totals must not masquerade as semaglutide-arm N.
        if row['drug_scope'] == 'SEMAGLUTIDE_ONLY':
            r['n_1'] = row['n_active']
            r['field_spans']['n_1'] = row['fields']['Active (n)']['span']
        p['trials'].append(r)
    return p


def compare(trials, pooled, root):
    review = read(root / 'docs/reviews' / SLUG / 'review.json')
    primary = next(o for o in review['outcomes'] if o.get('primary'))
    inventory = identity_join.our_identities(SLUG, root, review)
    ours = primary['trials']
    rows, used = [], set()
    for row in trials:
        joins = [identity_join.join(dict(label=row['label'], registration=row['registration'], **{k:v for k,v in ref.items() if k not in ('rid','path')}), inventory) for ref in row['references']]
        hits = {j['index'] for j in joins if j['status'] == 'JOINED'}
        result = dict(label=row['label'], path=row['path'], mace=row['mace'], drug_scope=row['drug_scope'], identity_joins=joins)
        if any(j['status'] == 'AMBIGUOUS' for j in joins) or len(hits) > 1:
            result.update(status='ABSTAIN', reason='AMBIGUOUS_REFERENCE_IDENTITY')
        elif not hits:
            result.update(status='MISSING_FROM_OURS', reason='NO_COMPATIBLE_HELD_IDENTITY')
        else:
            index = next(iter(hits))
            matches = [i for i,r in enumerate(ours) if identity_join.join(r, inventory).get('index') == index]
            if not matches:
                result.update(status='IN_INVENTORY_UNPOOLED', reasons=identity_join.states(inventory[index], primary['name']))
            elif len(matches) != 1 or row['drug_scope'] != 'SEMAGLUTIDE_ONLY':
                result.update(status='ABSTAIN', reason='AMBIGUOUS_OR_DIFFERENT_DRUG')
            else:
                if row['mace']:
                    used.add(matches[0])
                status, reason = meta_match._compare(meta_match._ours(ours[matches[0]], primary), {'n1':row['n_active']})
                result.update(status=status, reason=reason, our_label=ours[matches[0]].get('label'))
        rows.append(result)
    selected = [r for r in rows if r['mace']]
    return dict(trials=rows, comparator_k=pooled['k'], table_mace_members=len(selected),
                our_served_k=primary['result'].get('k'), K_MATCH='yes' if pooled['k'] == primary['result'].get('k') else 'no',
                membership_count_agrees=len(selected) == pooled['k'],
                comparator_only=[dict(label=r['label'], status=r['status'], reason=r.get('reason') or r.get('reasons'), drug_scope=r['drug_scope']) for r in selected if not r.get('our_label')],
                ours_only=[dict(label=r.get('label'), reason='NO_JOINED_MACE_MARKER_ROW') for i,r in enumerate(ours) if i not in used],
                scope_warning='Broader drugs and populations; K_MATCH is descriptive, not parity.')


def ratio(items, denominator):
    return dict(n=len(items), N=denominator, n_of_N=f'{len(items)} of {denominator}', items=items)


def run(root=ROOT):
    item, tree = load(root)
    trials, ledger, pooled = extract(tree)
    p = proposal(item, trials, tree)
    verified = gate.verify(p, root)
    compared = compare(trials, pooled, root)
    topics = [f.stem for f in sorted((root / 'topics').glob('*.json')) if isinstance(read(f), dict)]
    fields = [f for f in verified['fields'] if f['status'] != 'not_proposed']
    census = dict(topic_coverage=ratio([SLUG], len(topics)), topics_examined=topics,
                  out_of_scope=[s for s in topics if s != SLUG],
                  physical_rows=ratio([r['path'] + ':' + r['kind'] + ':' + r['label'] for r in ledger], len(ledger)),
                  trial_rows=ratio([r['label'] for r in trials], len(trials)),
                  mace_members=ratio([r['label'] for r in trials if r['mace']], len(trials)),
                  drug_refusals=ratio([r['label'] + ':' + r['drug_scope'] for r in trials if r['drug_scope'] != 'SEMAGLUTIDE_ONLY'], len(trials)),
                  native_gate_accepted=ratio([f['path'] for f in fields if f['status'] == 'accepted'], len(fields)),
                  native_gate_refused=ratio([f['path'] + ':' + str(f['reason']) for f in fields if f['status'] == 'rejected'], len(fields)),
                  comparison=compared)
    return p, dict(trials=trials, all_rows=ledger, pooled=pooled), verified, census


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    p, extracted, verified, census = run()
    if args.write:
        target = ROOT / '.tmp/g1sema'
        target.mkdir(parents=True, exist_ok=True)
        for name, data in [('proposal',p), ('extracted',extracted), ('gate',verified), ('census',census)]:
            (target / (name + '.json')).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(census, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
