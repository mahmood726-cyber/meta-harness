"""Offline, definition-only HOPE-3 witness; no synthesis or decision API."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from harness import component_typing

SLUG = 'statins-primary-prevention-elderly'
OUTCOME = 'Major vascular events'
HELD = Path('evidence/acquisition_cascade/held')
PDF = HELD / 'HOPE-3/hope3_nejm2016_leicester.pdf'
TEXT = PDF.with_suffix('.local.txt')
EXCERPT = Path('evidence/acquisition_cascade/excerpts/HOPE3_first_coprimary_definition_sentence.txt')
POLICY = Path('docs/endpoint_policies.json')
ADDED = ('component_basis_history', 'component_basis_held')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(text: str) -> str:
    text = re.sub(r'(?<=\w)\s*[-\u2011]\s*\n\s*(?=\w)', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def pending(doc):
    rows = doc['topics'][SLUG][OUTCOME]['pending']
    matches = [r for r in rows if r['input'] == 'NCT00468923']
    if len(matches) != 1:
        raise ValueError('PENDING_ID: refused absent/ambiguous NCT00468923')
    return matches[0]


def bind(sentence: str, relayed: list[str]) -> dict:
    # Preserve the complete sentence as evidence; type ONLY the first clause.
    match = re.fullmatch(r'(The first coprimary outcome was the composite of [^.]+?), and the second coprimary outcome additionally included ([^.]+)\.', sentence)
    if not match:
        raise ValueError('FIRST_COPRIMARY_REQUIRED: refused definition without separated first/second clauses')
    clause = match[1]
    typed = component_typing.derive(clause + '.')
    if not typed or typed['untyped']:
        raise ValueError('UNTYPED_DEFINITION: refused incomplete first-coprimary typing')
    # The base vocabulary drops fatality qualifiers; validate them separately.
    items = re.split(r',\s*(?:or\s+)?', clause.split('composite of ', 1)[1])
    vocabulary = {
        'death from cardiovascular causes': 'cardiovascular death',
        'nonfatal myocardial infarction': 'nonfatal myocardial infarction',
        'nonfatal stroke': 'nonfatal stroke',
    }
    if any(item not in vocabulary for item in items) or len(items) != 3:
        raise ValueError('COMPONENT_MISMATCH: refused extra, missing, or differently qualified components')
    qualified = sorted(vocabulary[item] for item in items)
    normalized = sorted(re.sub(r'^nonfatal ', '', c) for c in qualified)
    if qualified != sorted(relayed) or normalized != typed['components']:
        raise ValueError('COMPONENT_MISMATCH: refused disagreement with RELAYED set/base typing')
    return {'components': qualified, 'base_typing': typed, 'first_clause_span': clause,
            'first_clause_offsets': [match.start(1), match.end(1)],
            'equals_relayed': True, 'poolable': False}


def build(root: Path = ROOT) -> dict:
    import fitz
    registry = json.loads((root / HELD / 'HELD.json').read_text(encoding='utf-8'))
    meta = registry[PDF.relative_to(HELD).as_posix()]
    pdf_bytes = (root / PDF).read_bytes()
    if sha(pdf_bytes) != meta['sha256']:
        raise ValueError('PDF_HASH: refused PDF differing from HELD.json')
    text_bytes = (root / TEXT).read_bytes()
    local = text_bytes.decode('utf-8')
    candidates = []
    for page, body in re.findall(r'=== PAGE (\d+) ===\s*(.*?)(?==== PAGE |\Z)', local, re.S):
        for match in re.finditer(r'The first coprimary outcome was the composite of [^.]+\.', normalize(body)):
            candidates.append((int(page), match.group()))
    if not candidates:
        raise ValueError('DEFINITION_ABSENT: refused missing held first-coprimary sentence')
    page, sentence = candidates[0]
    with fitz.open(stream=pdf_bytes, filetype='pdf') as pdf:
        pdf_text = normalize(pdf[page - 1].get_text())
    if sentence not in pdf_text:
        raise ValueError('PDF_TEXT_MISMATCH: refused local sentence not found on PDF page')
    doc = json.loads((root / POLICY).read_text(encoding='utf-8'))
    typing = bind(sentence, pending(doc)['component_set'])
    printed = re.search(r'\b(20\d{2})\s+The authors', pdf_text)
    if not printed:
        raise ValueError('PAGE_LABEL: refused missing journal page label')
    return {'state': 'HELD', 'scope': 'Main-report first coprimary definition only; >=70 subgroup RESULT NOT_HELD; no admission decision',
            'path': EXCERPT.as_posix(), 'sha256': sha((sentence + '\n').encode()),
            'span': sentence, 'pdf_page': page, 'journal_page': printed[1],
            'source_path': PDF.as_posix(), 'source_sha256': sha(pdf_bytes),
            'source': meta['source'], 'licence': meta['licence'],
            'local_text_path': TEXT.as_posix(), 'local_text_sha256': sha(text_bytes),
            'normalization': 'Whitespace collapsed; PDF line-wrap hyphens removed; words and punctuation preserved',
            **typing}


def refuse_pool(*args, **kwargs):
    raise ValueError('POOLING_DISABLED: refused pooled estimate; DECISION_REQUIRED_BEFORE_INTERVAL remains')


def update_bytes(before: bytes, witness: dict) -> bytes:
    doc = json.loads(before)
    row = pending(doc)
    if any(k in row for k in ADDED):
        if row.get('component_basis_held') == witness and row.get('component_basis_history') == [row['component_basis']]:
            return before
        raise ValueError('WITNESS_CONFLICT: refused replacing existing component history/witness')
    # Append at the pending object's opening: every original byte stays intact.
    anchor = re.compile(rb'(\{\s*)("input"\s*:\s*"NCT00468923")')
    matches = list(anchor.finditer(before))
    if len(matches) != 1:
        raise ValueError('PENDING_ANCHOR: refused ambiguous policy byte insertion')
    addition = {'component_basis_history': [row['component_basis']], 'component_basis_held': witness}
    payload = json.dumps(addition, ensure_ascii=False, indent=2)[2:-2].encode('utf-8') + b',\n      '
    pos = matches[0].start(2)
    after = before[:pos] + payload + before[pos:]
    check = json.loads(after)
    for key in ADDED:
        del pending(check)[key]
    if check != doc:
        raise ValueError('POLICY_MUTATION: refused changes outside component witness fields')
    return after


def options(root: Path, witness: dict) -> str:
    text = (root / 'docs/decisions/hope3_endpoint_policy_options.md').read_text(encoding='utf-8')
    rows = text.splitlines()
    matches = [i for i, row in enumerate(rows) if row.startswith('| NCT00468923 |')]
    if len(matches) != 1:
        raise ValueError('OPTIONS_ROW: refused absent/ambiguous HOPE-3 row')
    cells = rows[matches[0]].split('|')
    cells[2] = (' HELD main-report first coprimary definition: ' + ', '.join(witness['components'])
                + '; matches the RELAYED set. Witness: `' + witness['path'] + '` (PDF page '
                + str(witness['pdf_page']) + ', journal page ' + witness['journal_page'] + '; sha256 '
                + witness['sha256'] + '). Historical basis: ' + cells[2].strip() + ' ')
    cells[3] = ' NOT_HELD >=70 subgroup RESULT; age analysis supplement not held; Ridker 2017 closed and not held. Main-report definition does not supply a subgroup result. '
    for i in (5, 6):
        cells[i] = ' CONDITIONAL; held main-report definition; OA age-specific result with endpoint/population binding and recorded decision still required '
    rows[matches[0]] = '|'.join(cells)
    return '\n'.join(rows) + '\n'


def census(root: Path = ROOT) -> dict:
    topics = sorted((root / 'topics').glob('*.json'))
    for path in topics:
        json.loads(path.read_text(encoding='utf-8'))
    names = [p.stem for p in topics if p.stem == SLUG]
    witness = build(root) if names else None
    item = [SLUG + '/NCT00468923'] if witness else []
    return {'topic_scope': {'n': len(names), 'N': len(topics), 'n_of_N': f'{len(names)} of {len(topics)}', 'items': names},
            'rules': {rule: {'n': len(item), 'N': len(names), 'n_of_N': f'{len(item)} of {len(names)}', 'items': item}
                      for rule in ('HELD_COMPONENT_WITNESS', 'FIRST_SECOND_SEPARATION', 'SUBGROUP_RESULT_NOT_HELD', 'POOLING_DISABLED', 'DECISION_BYTES_PRESERVED')}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--census', action='store_true')
    parser.add_argument('--pooled-estimate', nargs='?', const='REFUSED')
    args = parser.parse_args()
    if args.pooled_estimate is not None:
        refuse_pool()
    if args.census:
        print(json.dumps(census(), indent=2))
        return
    witness = build()
    before = (ROOT / POLICY).read_bytes()
    after = update_bytes(before, witness)
    table = options(ROOT, witness)
    (ROOT / EXCERPT).write_bytes((witness['span'] + '\n').encode('utf-8'))
    (ROOT / POLICY).write_bytes(after)
    dest = ROOT / '.tmp/hope3b/options.md'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(table.encode('utf-8'))
    print('HELD definition witness written; subgroup result NOT_HELD; decision unchanged; pooling disabled.')


if __name__ == '__main__':
    main()
