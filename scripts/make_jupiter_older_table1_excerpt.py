"""Offline, byte-deterministic excerpt from a pinned NIH author manuscript."""
from pathlib import Path
import hashlib
import re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'evidence/acquisition_cascade/held/JUPITER-older/pmc_article.html'
SHA = 'e01ea8e91646dd3c47e4c6490ea5d214221cf23c1353e6e11c7890bd22eb127d'
OUTPUT = 'evidence/acquisition_cascade/excerpts/JUPITER-older_Table1_baseline.tables.txt'
TABLE3 = 'evidence/acquisition_cascade/excerpts/JUPITER-older_Table3.tables.txt'


def require(condition, reason):
    if not condition:
        raise ValueError('JUPITER_REFUSED: ' + reason)


def text(node):
    return ' '.join(node.get_text(' ', strip=True).split())


def one(items, label):
    require(len(items) == 1, f'{label}: expected one, found {len(items)}')
    return items[0]


def held(root=ROOT):
    data = (Path(root) / SOURCE).read_bytes()
    require(hashlib.sha256(data).hexdigest() == SHA, f'SOURCE_SHA_MISMATCH {SOURCE}')
    return BeautifulSoup(data, 'html.parser')


def age_columns(table, width):
    cells = table.thead.find('tr').find_all('th', recursive=False)
    require(len(cells) == 3, 'AGE_HEADER missing or ambiguous')
    labels = [text(c) for c in cells[1:]]
    require(labels == ['Age 70–97 years', 'Age 50–69 years'], f'AGE_HEADER refused {labels}')
    require(all(int(c.get('colspan', 1)) == width for c in cells[1:]), 'AGE_COLUMN_WIDTH')
    return labels[0]


def baseline(soup):
    section = one(soup.select('section#T1'), 'Table 1')
    table = one(section.find_all('table'), 'Table 1 DOM table')
    age = age_columns(table, 2)
    headers = [text(c) for c in table.thead.find_all('th') if re.fullmatch(r'(?:Rosuvastatin|Placebo) \(N=\d+\)', text(c))]
    require(len(headers) == 4, 'BASELINE_ARMS')
    arms = []
    for label, header in zip(('Rosuvastatin', 'Placebo'), headers[:2]):
        m = re.fullmatch(re.escape(label) + r' \(N=(\d+)\)', header)
        require(m is not None, f'ARM_ORDER {header}')
        arms.append(dict(arm=label, denominator=int(m[1]), source_span=header))
    return dict(age=age, arms=arms, caption=text(section.find('h3')))


def safety_dom(soup):
    """Independent DOM parse; never obtains table values from the excerpt."""
    section = one(soup.select('section#T3'), 'Table 3')
    table = one(section.find_all('table'), 'Table 3 DOM table')
    age = age_columns(table, 5)
    tiers = [[text(c) for c in tr.find_all('th', recursive=False)] for tr in table.thead.find_all('tr')]
    require(tiers[2] == ['Monitored adverse event', 'Rosuvastatin', 'Placebo', 'Hazard ratio † (95% CI)', 'Rosuvastatin', 'Placebo', 'Hazard ratio † (95% CI)'], 'SAFETY_ARM_MEASURE_HEADER')
    require(tiers[3] == ['', 'N', 'Rate *', 'N', 'Rate *', 'N', 'Rate *', 'N', 'Rate *'], 'SAFETY_N_RATE_HEADER')
    footnotes = [text(one(soup.select('#' + ident), ident)) for ident in ('TFN6', 'TFN7')]
    require('Rates are per 100 person-years' in footnotes[0], 'RATE_BASIS')
    require('Hazard ratios compare hazards in the rosuvastatin group to placebo' in footnotes[1], 'HR_DIRECTION')
    rows = {}
    for tr in table.tbody.find_all('tr', recursive=False):
        cells = tr.find_all('td', recursive=False)
        require(len(cells) == 11 and all(int(c.get('colspan', 1)) == 1 for c in cells), 'SAFETY_ROW_ALIGNMENT')
        values = [text(c) for c in cells]
        require(values[0] not in rows, 'DUPLICATE_ROW ' + values[0])
        rows[values[0]] = values[1:6]
    return dict(age=age, rows=rows, footnotes=footnotes,
                count_labels=tiers[3][1:5], caption=text(section.find('h3')))


def verify_table3(soup, root=ROOT):
    dom = safety_dom(soup)
    excerpt = (Path(root) / TABLE3).read_text(encoding='utf-8')
    hashes = re.findall(r'sha256 ([a-f0-9]{64})', excerpt)
    require(hashes == [SHA], 'TABLE3_EXCERPT_SHA')
    require('(Age 70–97 years)' in excerpt, 'TABLE3_EXCERPT_AGE')
    rows = [line.split(' | ') for line in excerpt.splitlines() if ' | ' in line][1:]
    require(len(rows) == 3 and len({r[0] for r in rows}) == len(rows), 'TABLE3_EXCERPT_ROWS')
    for row in rows:
        require(row[0] in dom['rows'] and row[1:] == dom['rows'][row[0]], 'TABLE3_DOM_MISMATCH ' + row[0])
    return dom


def render(root=ROOT):
    soup = held(root)
    b = baseline(soup)
    verify_table3(soup, root)
    return (f'# EXCERPT JUPITER older Table 1; DOM-segmented baseline arm sizes.\n'
            f'# held: {SOURCE} sha256 {SHA}\n'
            '# Baseline randomized denominators; Table 3 N does not explicitly establish patient counts.\n'
            '=== TABLES (excerpt) ===\nTABLE ' + b['caption'] + '\n'
            'Age group | Rosuvastatin N | Placebo N\n' + b['age'] + ' | ' +
            ' | '.join(str(a['denominator']) for a in b['arms']) + '\n').encode('utf-8')


if __name__ == '__main__':
    (ROOT / OUTPUT).write_bytes(render())
    print(OUTPUT)
