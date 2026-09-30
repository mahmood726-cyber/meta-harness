"""Offline second instrument. No imports from excerpt generators or bindings.

PDF page selectors and label aliases are static navigation, never research values.
All expected numbers are extracted from held bytes, independently of the excerpt.
Run with --details for every cell and its source/excerpt spans; default is a census.
"""
from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('evidence/acquisition_cascade')
FILES = (
    'PHILO_Table3_adverse_events.tables.txt',
    'PLATO_FDA2011_Table12_major_bleeding.tables.txt',
    'PLATO_FDA2011_Table23_dyspnea.tables.txt',
    'WHO-REACT_Table1_arm_sizes.tables.txt',
)
SOURCES = ('PHILO/unpaywall.pdf', 'PLATO-regulatory/022433Orig1s000MedR.pdf',
           'PLATO-regulatory/022433Orig1s000MedR.pdf', 'WHO-REACT/PMC8261689.local.html')


def compact(text):
    return re.sub(r'\s+', '', text).casefold().replace('–', '-').replace('−', '-')


def numbers(text):
    """Lexical decimals preserve digits, order, and precision; whitespace is PDF noise."""
    return re.findall(r'\d+(?:\.\d+)?', re.sub(r'\s+', '', text))


def ev(value, span):
    return {'value': value, 'span': span}


@lru_cache(maxsize=16)
def pdf_page(path, page):
    from pypdf import PdfReader
    obj = PdfReader(path).pages[page - 1]
    if obj.rotation:
        obj.transfer_rotation_to_content()
    return obj.extract_text(extraction_mode='layout')


def pdf_rows(text, pattern):
    """Match labels without PDF inter-glyph whitespace; retain complete source line."""
    result = []
    for line in text.splitlines():
        cols = re.split(r'\s{3,}', line.strip())
        if cols and re.fullmatch(pattern, compact(cols[0])):
            result.append((cols, line.strip()))
    return result


class Tables(HTMLParser):
    """DOM row/cell parser, retaining cell markup spans and rowspan metadata."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self.table = None
        self.row = None
        self.cell = None
        self.line = 0
        self.text = []

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            if self.table is not None:
                raise ValueError('REFUSED nested table')
            self.table = []
        elif tag == 'tr' and self.table is not None:
            self.row = []
        elif tag in ('th', 'td') and self.row is not None:
            self.cell = ['', dict(attrs), self.getpos()]

    def handle_data(self, data):
        self.text.append(data)
        if self.cell is not None:
            self.cell[0] += data

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            self.cell[0] = ' '.join(self.cell[0].split())
            self.row.append(self.cell)
            self.cell = None
        elif tag == 'tr' and self.row is not None:
            self.table.append(self.row)
            self.row = None
        elif tag == 'table' and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def html_source(path):
    parser = Tables()
    parser.feed(path.read_text(encoding='utf-8'))
    candidates = [t for t in parser.tables if t and
                  any(c[0] == 'Trial registration No.' for c in t[0])]
    if len(candidates) != 1:
        raise ValueError('REFUSED ambiguous/missing trial-characteristics DOM table')
    table = candidates[0]
    rows = {}
    group = None
    current = None
    for row in table:
        texts = [c[0] for c in row]
        if len(row) == 1:
            group = texts[0]
            current = None
        elif len(row) >= 4 and re.match(r'(NCT|EU-CTR)', texts[1]):
            current = (group, texts[0])
            if current in rows:
                raise ValueError('REFUSED duplicate trial in group: ' + str(current))
            rows[current] = {'label': ev(texts[0], str(row[0])),
                             'id': ev(texts[1], str(row[1])), 'arms': []}
            rows[current]['arms'].append((texts[2], ev(texts[3], str(row[2:4]))))
        elif current and len(row) >= 2 and re.match(
                r'Anti|Usual care|Placebo|Control|Corticosteroids', texts[0]):
            rows[current]['arms'].append((texts[0], ev(texts[1], str(row[:2]))))
    return rows, table[0]


def source_model(root, index):
    path = root / BASE / 'held' / SOURCES[index]
    model = {'rows': {}, 'headers': [], 'notes': []}
    if index == 3:
        rows, header = html_source(path)
        model['headers'] = [ev('Trial', str(header[0])),
                            ev('NCT (or printed registration)', str(header[1])),
                            ev('intervention arm n', str(header[2:4])),
                            ev('comparator arm n', str(header[2:4]))]
        for (group, name), row in rows.items():
            if group != 'Tocilizumab' and not (group.startswith('Anti–IL-6 vs') and name == 'STORM'):
                continue
            active = [v for arm, v in row['arms'] if arm.startswith(('Anti', 'Tocilizumab'))]
            control = [v for arm, v in row['arms'] if arm.startswith(('Usual', 'Placebo', 'Control', 'Corticosteroids'))]
            if not active or len(control) != 1:
                raise ValueError('REFUSED unresolved arms: ' + name)
            model['rows'][name] = [row['label'], row['id'],
                ev('; '.join(v['value'] for v in active), str(active)), control[0]]
        return model

    page = (7, 235, 255)[index]
    text = pdf_page(str(path), page)
    span = lambda s: f'{SOURCES[index]} PDF page {page}: {s}'
    if index == 0:
        pop = pdf_page(str(path), 3)
        match = re.search(r'analysis set:\s*(\d+) in the ticagrelor group and (\d+) in the clopi-', pop)
        if not match:
            raise ValueError('REFUSED missing PHILO safety population')
        head = next(line.strip() for line in text.splitlines() if 'HR for ticagrelor' in line)
        ci = next(line.strip() for line in text.splitlines() if '95% CI' in line)
        confidence = re.search(r'\d+%\s*CI', ci)[0]
        model['headers'] = [ev('Outcome', span('Table3. Adverse Events for All Patients')),
            ev('Ticagrelor patients N=' + match[1], 'PDF page 3: ' + match[0] + '; ' + head),
            ev('Clopidogrel patients N=' + match[2], 'PDF page 3: ' + match[0] + '; ' + head),
            ev('HR (' + confidence + ')', span(head + ' ' + ci))]
        patterns = [('Major bleeding (PLATO-defined)', r'majorbleeding\(plato-defined\)'),
                    ('Non-CABG-related', 'non-cabg-related'), ('Dyspnea', 'dyspnea')]
        for name, pattern in patterns:
            matches = pdf_rows(text.split('Table4.')[0], pattern)
            if not matches:
                continue
            cols, line = matches[0]  # first Non-CABG row lies under major, before minor bleeding
            model['rows'][name] = [ev(cols[0], span(line))] + [ev(v, span(line)) for v in cols[1:]]
            if len(cols) == 3:
                model['rows'][name].append(ev('', span(line)))
    elif index == 1:
        denom_line = next(line for line in text.splitlines() if len(re.findall(r'N\s*=\s*\d+', line)) == 2)
        denoms = re.findall(r'N\s*=\s*(\d+)', denom_line)
        head = text[text.index('Tic agrelor'):text.index('P rimary')]
        if not all(w in compact(head) for w in ('clopidogrel', 'numberofbleeding', 'k m'.replace(' ', ''), 'hazardratio')):
            raise ValueError('REFUSED missing Table12 measure/arm header')
        corroboration = pdf_page(str(path), 236)
        patient_row = pdf_rows(corroboration, 'majorbleed')
        model['headers'] = [ev('Outcome', span('Characteristic'))]
        for arm, denominator in zip(('Ticagrelor', 'Clopidogrel'), denoms):
            for suffix in ('bleeding events', 'patients N=' + denominator, 'KM% one year'):
                model['headers'].append(ev(arm + ' ' + suffix, span(head.strip()) + '; Table13 PDF page 236: Patients with Adjudicated Major Bleeds'))
        confidence = re.search(r'(\d+)%ci', compact(head))[1]
        model['headers'].append(ev('Hazard ratio (' + confidence + '% CI)', span(head.strip())))
        for cols, line in pdf_rows(text, 'totalmajor'):
            # label / event count / patients (%), KM / event count / patients (%), KM / HR
            if len(cols) != 6:
                raise ValueError('REFUSED Table12 column count')
            cells = [cols[0], cols[1], *cols[2].rsplit(',', 1), cols[3], *cols[4].rsplit(',', 1), cols[5]]
            if not patient_row or numbers(' '.join(patient_row[0][0][1:])) != numbers(cells[2] + ' ' + cells[5]):
                raise ValueError('REFUSED Table12 patient-unit corroboration')
            model['rows']['Total Major'] = [ev(v, span(line)) for v in cells]
    else:
        region = text.split('Dy  spn')[1].split('Su bjec')[0]
        # Compact full line only after identifying row/column boundaries. N line is fused;
        # derive denominators independently from the clearly separated Table13 header.
        denom_text = pdf_page(str(path), 236)
        denom_line = next(line for line in denom_text.splitlines() if len(re.findall(r'N\s*=\s*\d+', line)) == 2)
        denoms = re.findall(r'N\s*=\s*(\d+)', denom_line)
        if 'N' + ''.join(denoms) not in re.sub(r'\s+', '', region):
            raise ValueError('REFUSED Table23 fused denominator corroboration')
        head = next(line for line in region.splitlines() if 'RR' in line)
        if not all(w in compact(head) for w in ('ticagrelor', 'clopidogrel', 'rr')):
            raise ValueError('REFUSED Table23 arm/measure header')
        model['headers'] = [ev('Outcome', span('Dyspnea Adverse Event*')),
            ev('Ticagrelor patients N=' + denoms[0], span(head + ' ' + denom_line)),
            ev('Clopidogrel patients N=' + denoms[1], span(head + ' ' + denom_line)),
            ev('RR (rounded; no CI)', span(head))]
        aliases = {'adverseevent': 'Dyspnea adverse event',
                   'seriousadverseevent': 'Dyspnea serious adverse event',
                   'adverseevent,drugstopped': 'Dyspnea adverse event leading to discontinuation (drug stopped)'}
        # Inter-glyph spacing overlaps layout gaps: use the grammar of two n (%) cells
        # and one decimal RR after the independently identified row label.
        for line in region.splitlines():
            clean = re.sub(r'\s+', '', line)
            m = re.fullmatch(r'([a-z,]+)(\d+\(\d+\.\d+%\))(\d+\(\d+\.\d+%\))(\d+\.\d+)', clean)
            if m and m[1] in aliases:
                name = aliases[m[1]]
                model['rows'][name] = [ev(name, span(line.strip()))] + [ev(m[i], span(line.strip())) for i in (2, 3, 4)]
    return model


def compare_cell(key, supplied, expected, excerpt_span, numeric=False):
    # Preserve punctuation as well as every digit: dropping '%' or adding a minus
    # sign must not pass merely because the unsigned numeric tokens are unchanged.
    actual = compact(supplied)
    target = compact(expected['value']) if expected else None
    status = 'NOT_FOUND_BY_SECOND_INSTRUMENT' if expected is None else ('AGREE' if actual == target else 'DISAGREE')
    return {'cell': key, 'status': status, 'excerpt_value': supplied,
            'source_value': expected['value'] if expected else None,
            'excerpt_span': excerpt_span, 'source_span': expected['span'] if expected else None,
            **({'excerpt_numbers': numbers(supplied), 'source_numbers': numbers(expected['value']) if expected else None} if numeric else {})}


def provenance_checks(root, index, text):
    """Separate provenance/quoted-value census; these are not table data cells."""
    checks = []
    if index == 0:
        page = pdf_page(str(root / BASE / 'held' / SOURCES[index]), 3)
        for pattern in (r'Of the (\d+) patients randomized to', r'treatment, (\d+) received study drug'):
            held, supplied = re.search(pattern, page), re.search(pattern, text)
            checks.append(compare_cell('population: ' + pattern, supplied[1] if supplied else '<MISSING>',
                ev(held[1], 'PDF page 3: ' + held[0]) if held else None,
                supplied[0] if supplied else 'missing population quotation'))
    if index == 1:
        m = re.search(r'# Table 12 PDF page (\d+);', text)
        checks.append(compare_cell('Table12 PDF page', m[1] if m else '<MISSING>',
            ev('235', 'Independently navigated PDF page 235: Table 12 heading and Total Major row; page 202 is Table of Tables'),
            m[0] if m else 'missing page declaration'))
        # A contents-list entry must not stand in for the actual table caption.
        caption = next((s[6:] for s in text.splitlines() if s.startswith('TABLE ')), '')
        page = pdf_page(str(root / BASE / 'held' / SOURCES[index]), 235)
        source_caption = next(s.strip() for s in page.splitlines() if s.startswith('Table 12:'))
        checks.append(compare_cell('Table12 caption', caption, ev(source_caption, 'PDF page 235: ' + source_caption), caption))
    if index == 2:
        page = pdf_page(str(root / BASE / 'held' / SOURCES[index]), 255)
        for key, pattern in [('unbound onset HR', r'\[HR [\d.]+ \(\d+% CI [\d.]+, [\d.]+\)\]')]:
            held = re.search(pattern, page)
            supplied = re.search(pattern, text)
            checks.append(compare_cell(key, supplied[0] if supplied else '<MISSING>',
                ev(held[0], 'PDF page 255 onset prose: ' + held[0]) if held else None,
                supplied[0] if supplied else 'missing HR prose'))
        held_note = re.search(r'\*preferredterms:.*?painfulrespiration\.', compact(page))
        note = re.search(r'^# footnote \(verbatim\): (.*(?:\n# .*)*)', text, re.M)
        supplied_note = re.sub(r'\n# ', '\n', note[1]) if note else '<MISSING>'
        checks.append(compare_cell('grouped preferred-terms footnote', supplied_note,
            ev(held_note[0], 'PDF page 255 whitespace-normalized footnote: ' + held_note[0]) if held_note else None,
            supplied_note))
    if index == 3:
        parser = Tables()
        parser.feed((root / BASE / 'held' / SOURCES[index]).read_text(encoding='utf-8'))
        held_text = ' '.join(parser.text)
        normalized = compact(held_text)
        for lineno, line in enumerate(text.splitlines(), 1):
            match = re.match(r'# (population|footnote|deaths) \(verbatim\): (.*)', line)
            if not match:
                continue
            quote = match[2]
            start = normalized.find(compact(quote))
            checks.append(compare_cell(f'{match[1]} quotation line {lineno}', quote,
                ev(normalized[start:start + len(compact(quote))],
                   f'HTMLParser DOM text whitespace-normalized character span [{start}:{start + len(compact(quote))}]: ' +
                   normalized[start:start + len(compact(quote))]) if start >= 0 else None, line))
    return checks


def regeneration(root=ROOT):
    """Use only AFTER recording independence. Pure renders never write evidence/."""
    from scripts import make_philo_excerpt as philo, make_plato_fda_excerpt as plato
    from scripts import make_react_excerpt as react
    def render_all():
        return {philo.OUTPUT: philo.render(root), **plato.render(root),
                react.OUTPUT: react.render(react.parse((root / react.HELD).read_bytes()))}
    first, second = render_all(), render_all()
    return [{'excerpt': Path(name).name,
             'held_excerpt_sha256': hashlib.sha256((root / name).read_bytes()).hexdigest(),
             'generated_sha256': hashlib.sha256(data).hexdigest(),
             'byte_identical': data == (root / name).read_bytes(),
             'repeat_identical': data == second[name]} for name, data in first.items()]


def verify(root, index, excerpt=None, model=None):
    path = excerpt or root / BASE / 'excerpts' / FILES[index]
    text = path.read_text(encoding='utf-8')
    if text.count('=== TABLES (excerpt) ===') != 1:
        raise ValueError('REFUSED missing/duplicate TABLES marker: ' + path.name)
    source = root / BASE / 'held' / SOURCES[index]
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    header = re.search(r'^# held (?:PDF|HTML): (\S+) sha256 ([0-9a-f]{64})$', text, re.M)
    if not header or header[2] != digest or header[1] != (BASE / 'held' / SOURCES[index]).as_posix():
        raise ValueError('REFUSED source SHA-256/path mismatch: ' + path.name)
    model = model if model is not None else source_model(root, index)
    cells = []
    seen = set()
    header_seen = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.startswith('#') or '|' not in line:
            continue
        cols = [c.strip() for c in line.split('|')]
        is_header = cols[0] in ('Outcome', 'Trial')
        if is_header:
            if header_seen:
                raise ValueError('REFUSED duplicate excerpt header')
            header_seen = True
            expected = model['headers']
        else:
            if cols[0] in seen:
                raise ValueError('REFUSED duplicate excerpt row: ' + cols[0])
            seen.add(cols[0])
            expected = model['rows'].get(cols[0], [])
        for i in range(max(len(cols), len(expected))):
            val = cols[i] if i < len(cols) else '<MISSING>'
            target = expected[i] if i < len(expected) else None
            cells.append(compare_cell(f'{cols[0]} / column {i}', val, target,
                f'{path.name}:{lineno}: {line}', numeric=not is_header and i > (1 if index == 3 else 0)))
    if not header_seen:
        raise ValueError('REFUSED missing excerpt header')
    for name in sorted(model['rows'].keys() - seen):
        cells.append(compare_cell(name + ' / missing row', '<MISSING>', model['rows'][name][0], path.name))
    counts = Counter(c['status'] for c in cells)
    provenance = provenance_checks(root, index, text)
    return {'excerpt': FILES[index], 'source_sha256': digest, 'sha256_status': 'AGREE',
            'N': len(cells), 'counts': dict(counts),
            'n_of_N': {s: f'{counts[s]} of {len(cells)}' for s in
                       ('AGREE', 'DISAGREE', 'NOT_FOUND_BY_SECOND_INSTRUMENT')},
            'flagged_items': [c for c in cells if c['status'] != 'AGREE'], 'cells': cells,
            'provenance_checks': provenance}


def census(root=ROOT, details=False):
    results = []
    for i in range(len(FILES)):
        try:
            result = verify(root, i)
        except (ValueError, OSError) as exc:
            result = {'excerpt': FILES[i], 'refused': str(exc)}
        if not details:
            result.pop('cells', None)
        results.append(result)
    provenance = [c for r in results for c in r.get('provenance_checks', [])]
    counts = Counter(c['status'] for c in provenance)
    return {'scope': 'All four named excerpts; topic files are enumerated, not eligible for this lane.',
            'provenance_n_of_N': {s: f'{counts[s]} of {len(provenance)}' for s in ('AGREE', 'DISAGREE', 'NOT_FOUND_BY_SECOND_INSTRUMENT')},
            'topics_enumerated': len(list((root / 'topics').glob('*.json'))), 'excerpts': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--details', action='store_true')
    parser.add_argument('--regenerate', action='store_true', help='Only after recording independent results')
    args = parser.parse_args()
    result = census(args.root, args.details)
    if args.regenerate:
        # Direct script invocation needs the repo root for the scripts namespace.
        import sys
        sys.path.insert(0, str(ROOT))
        result['regeneration'] = regeneration(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(any('refused' in r or r.get('flagged_items') or
                   any(c['status'] != 'AGREE' for c in r.get('provenance_checks', []))
                   for r in result['excerpts']) or
               any(not r['byte_identical'] or not r['repeat_identical'] for r in result.get('regeneration', [])))


if __name__ == '__main__':
    raise SystemExit(main())
