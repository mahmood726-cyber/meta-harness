"""Offline, deterministic Table 1 excerpt; no OCR or network inference."""
from __future__ import annotations
import hashlib
import html
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
HELD = 'evidence/acquisition_cascade/held/WHO-REACT/PMC8261689.local.html'
OUTPUT = 'evidence/acquisition_cascade/excerpts/WHO-REACT_Table1_arm_sizes.tables.txt'
# Integrity pin measured from the supplied held bytes, not a research value.
SHA256 = 'bbed7fae330b3af11faa1a63191db3db3e7dea44ac33bc7df18c0201479cf94a'


def normalize(value):
    return ' '.join(html.unescape(re.sub(r'<[^>]*>', ' ', str(value))).split())


def witness(value, source):
    quote = normalize(value)
    start = normalize(source).find(quote)
    if not quote or start < 0:
        raise ValueError('VERBATIM_NOT_HELD: ' + quote)
    return {'quote': quote, 'start': start, 'end': start + len(quote)}


def parse(raw, expected_sha256=SHA256):
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise ValueError('HELD_SHA256_MISMATCH: ' + digest)
    source = raw.decode('utf-8')
    soup = BeautifulSoup(source, 'html.parser')
    sections = [s for s in soup.select('section.tw') if s.find('h3') and
                re.match(r'Table 1\.', normalize(s.find('h3')))]
    if len(sections) != 1:
        raise ValueError('TABLE1_STRUCTURE_UNRESOLVED')
    section = sections[0]
    table = section.find('table')
    if table is None:
        raise ValueError('TABLE1_STRUCTURE_NOT_HELD: text fallback not established')
    headers = [normalize(c) for c in table.select('thead tr')[0].find_all('th')]
    if headers[1:4] != ['Trial registration No.', 'Treatment group b', 'No. of patients']:
        raise ValueError('TABLE1_COLUMN_SCHEMA_CHANGED')
    rows, current, group = [], None, ''
    for tr in table.select('tbody tr'):
        cells = tr.find_all(['td', 'th'], recursive=False)
        values = [normalize(c) for c in cells]
        if len(cells) == 1:
            group = values[0]
            current = None
            continue
        if group != 'Tocilizumab' and not group.startswith('Anti–IL-6 vs corticosteroids'):
            continue
        if not values or values[0] == 'Total':
            current = None
            continue
        if int(cells[0].get('rowspan', 1)) > 1:
            current = {'trial': values[0], 'nct': next(iter(re.findall(r'\bNCT\d{8}\b', values[1])), None),
                       'registration': values[1], 'arms': [], 'group': group}
            rows.append(current)
            arm, size = values[2:4]
        elif current is not None:
            arm, size = values[:2]
        else:
            raise ValueError('ORPHAN_TABLE1_ARM: ' + values[0])
        if not re.fullmatch(r'\d+', size):
            raise ValueError('NONINTEGER_ARM_SIZE: ' + current['trial'])
        current['arms'].append({'label': arm, 'n': int(size), 'span': witness(tr, source)})
    rows = [r for r in rows if r['group'] == 'Tocilizumab' or
            any(a['label'] == 'Tocilizumab' for a in r['arms'])]
    for r in rows:
        r['intervention'] = [a for a in r['arms'] if re.match(r'Anti[–-]IL-6|Tocilizumab', a['label'])]
        r['comparator'] = [a for a in r['arms'] if a not in r['intervention']]
    text = normalize(source)
    pop = re.search(r'Because outcome data were generally complete[^.]*participants with outcomes recorded\.', text)
    population = {'state': 'OUTCOMES_RECORDED', 'span': witness(pop.group(), source)} if pop else {'state': 'UNSTATED'}
    # Retain ALL death-bearing sentences (including alt/title attributes) for audit.
    blocks = [normalize(n) for n in soup.find_all(['p', 'figcaption', 'tr'])]
    attributes = [normalize(n.get(a)) for n in soup.find_all(True) for a in ('alt', 'title', 'aria-label') if n.get(a)]
    candidates = [s for s in blocks + attributes
                  if re.search(r'\bdeath(?:s)?\b|\bdied\b|\bmortality\b', s, re.I)]
    # Only explicitly named trial + 28-day + two named-arm integer counts qualify.
    deaths = []
    for sentence in candidates:
        zero = re.search(r'\b(?:Three|\d+) trials recorded no deaths by 28 days[^.]*\.', sentence)
        if zero:
            ids = set(re.findall(r'\bNCT\d{8}\b', zero.group()))
            for row in rows:
                if row['nct'] in ids:
                    deaths.append({'trial': row['trial'], 'nct': row['nct'], 'ai': 0, 'ci': 0,
                                   'total_deaths': 0, 'basis': 'NO_DEATHS_IN_TRIAL_IMPLIES_ZERO_IN_EACH_ARM',
                                   'span': witness(zero.group(), source)})
    for r in rows:
        for sentence in candidates:
            if not re.search(r'(?<!\w)' + re.escape(r['trial']) + r'(?!\w)', sentence, re.I):
                continue
            m = re.search(re.escape(r['trial']) + r'\s+28[- ]day mortality: (\d+) deaths (?:in|with) tocilizumab and (\d+) deaths (?:in|with) (?:placebo|usual care)', sentence, re.I)
            if m:
                deaths.append({'trial': r['trial'], 'nct': r['nct'], 'ai': int(m[1]), 'ci': int(m[2]),
                               'span': witness(m.group(), source)})
    for r in rows:
        for arm in r['arms']:
            arm['span'].update(source=HELD, sha256=digest)
    return {'sha256': digest, 'method': 'HTML table structure', 'rows': rows,
            'caption': witness(section.find('h3'), source),
            'footnotes': [witness(f, source) for f in section.select('.tw-foot .fn')],
            'population': population, 'deaths': deaths, 'death_text_candidates': candidates}


def render(data):
    lines = ['# EXCERPT of WHO REACT Table 1; cell boundaries derived from HTML table structure.',
             f'# held HTML: {HELD} sha256 {data["sha256"]}',
             '# population (verbatim): ' + data['population'].get('span', {}).get('quote', 'UNSTATED')]
    lines += ['# footnote (verbatim): ' + f['quote'] for f in data['footnotes']]
    lines += ['# numerators: ' + ('trial death counts extracted below; other trial numerators remain RELAYED' if data['deaths'] else
              'No explicit per-trial arm death counts found in held text; numerators remain RELAYED.'),
              '# Multi-arm sizes are listed separately, never summed; STORM is excluded per footnote k.',
              '', '=== TABLES (excerpt) ===', 'TABLE ' + data['caption']['quote'],
              'Trial | NCT (or printed registration) | intervention arm n | comparator arm n']
    for r in data['rows']:
        lines.append(' | '.join([r['trial'], r['nct'] or r['registration'],
                                '; '.join(str(a['n']) for a in r['intervention']),
                                '; '.join(str(a['n']) for a in r['comparator'])]))
    for d in data['deaths']:
        lines.append('# deaths (verbatim): ' + d['span']['quote'])
    return ('\n'.join(lines) + '\n').encode('utf-8')


def main():
    data = parse((ROOT / HELD).read_bytes())
    (ROOT / OUTPUT).write_bytes(render(data))
    print(f'{OUTPUT}: {len(data["rows"])} rows; sha256 {data["sha256"]}; {len(data["deaths"])} death-count pairs')


if __name__ == '__main__':
    main()
