"""Deterministic PHILO table segmentation from hash-verified held evidence."""
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
PDF = 'evidence/acquisition_cascade/held/PHILO/unpaywall.pdf'
SHA = '6d5c10e40a00e9eb88be44796b9213b480f628f7862243333219c0a019494267'
OUTPUT = 'evidence/acquisition_cascade/excerpts/PHILO_Table3_adverse_events.tables.txt'


def one(pattern, text, flags=0):
    hits = list(re.finditer(pattern, text, flags))
    if len(hits) != 1:
        raise ValueError(f'REFUSED source pattern {pattern!r}: {len(hits)} matches')
    return hits[0]


def held(root, pdf, sha):
    path = Path(root) / pdf
    if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
        raise ValueError(f'REFUSED source SHA mismatch: {pdf}')
    return path.with_suffix('.local.txt').read_text(encoding='utf-8')


def render(root=ROOT):
    text = held(root, PDF, SHA)
    population = one(r'Of the \d+ patients randomized to\s+treatment,.*?dogrel group\.', text, re.S)[0]
    n = one(r'analysis set:\s*(\d+) in the ticagrelor group and (\d+) in the clopi-\s*dogrel group', population)
    block = one(r'(Table 3\. Adverse Events for All Patients)\n(.*?)\nTable 4\.', text, re.S)
    # Capture only total major, its non-CABG child, and dyspnea; no transcribed numbers.
    cell = r'(\d+\s*\([\d.]+\))'
    effect = r'([\d.]+\s*\([\d.]+[–-][\d.]+\))'
    major = one(r'^Major bleeding \(PLATO-defined\)\s+'+cell+r'\s+'+cell+r'\s+'+effect, block[2], re.M)
    child = one(r'^\s*Non-CABG-related\s+'+cell+r'\s+'+cell+r'\s+'+effect,
                block[2].split('Minor bleeding', 1)[0], re.M)
    dyspnea = one(r'^Dyspnea\s+'+cell+r'\s+'+cell, block[2], re.M)
    comments = '\n'.join('# '+line for line in population.splitlines())
    return (f'# EXCERPT PHILO Table 3; cell boundaries segmented from held text.\n'
            f'# held PDF: {PDF} sha256 {SHA}\n'
            '# population (verbatim; line breaks preserved):\n'+comments+'\n'
            '=== TABLES (excerpt) ===\nTABLE '+block[1]+'\n'
            f'Outcome | Ticagrelor patients N={n[1]} | Clopidogrel patients N={n[2]} | HR (95% CI)\n'
            +'Major bleeding (PLATO-defined) | '+' | '.join(major.groups())+'\n'
            +'Major bleeding (PLATO-defined)\nNon-CABG-related | '+' | '.join(child.groups())+'\n'
            +'Adverse Events for All Patients\nDyspnea | '+' | '.join(dyspnea.groups())+' | \n').encode('utf-8')


def main():
    path = ROOT / OUTPUT
    path.write_bytes(render())
    print(path.relative_to(ROOT).as_posix())


if __name__ == '__main__':
    main()
