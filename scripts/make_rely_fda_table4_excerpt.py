"""Build the committed EXCERPT of FDA PRADAXA label (Oct 2010) Table 4 -- RE-LY first stroke or systemic embolism --
from the held text extraction. US government work (public domain). Every cell must occur verbatim, exactly once, in the
whitespace-collapsed held text, or the script refuses; the held text's sha256 must equal HELD.json's.

    python scripts/make_rely_fda_table4_excerpt.py HELD_ROOT      # HELD_ROOT = evidence/acquisition_cascade/held
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REL = 'RE-LY-regulatory/fda_label_2010-10.txt'
OUT = ROOT / 'evidence/acquisition_cascade/excerpts/RELY_FDA2010_Table4_stroke_SE.tables.txt'
# (verbatim run in the held text, cells it is segmented into)
RUNS = [
    ('Table 4 First Occurrence of Stroke or Systemic Embolism in the RE-LY Study', None),
    ('Patients randomized 6076 6015 6022', ['Patients randomized', '6076', '6015', '6022']),
    ('Patients (%) with events 134 (2.2%) 183 (3%) 202 (3.4%)', ['Patients (%) with events', '134 (2.2%)', '183 (3%)', '202 (3.4%)']),
    ('Hazard ratio vs. warfarin (95% CI) 0.65 (0.52, 0.81) 0.90 (0.74,1.10)',
     ['Hazard ratio vs. warfarin (95% CI)', '0.65 (0.52, 0.81)', '0.90 (0.74,1.10)']),
]


def collapse(s):
    return re.sub(r'\s+', ' ', s).strip()


def main(held_root):
    held_root = Path(held_root)
    raw = (held_root / REL).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    ledger = json.loads((held_root / 'HELD.json').read_text(encoding='utf-8'))
    if ledger.get(REL, {}).get('sha256') != sha:
        raise SystemExit('REFUSED: held text sha256 differs from HELD.json')
    text = collapse(raw.decode('utf-8'))
    for run, _cells in RUNS:
        if text.count(collapse(run)) != 1:
            raise SystemExit('REFUSED: not exactly once in the held text: ' + run)
    lines = [
        '# EXCERPT of the FDA PRADAXA label (NDA 022512, October 2010; US government work, public domain), section 14 '
        f'Table 4. Every value is verbatim from the committed text extraction evidence/acquisition_cascade/held/{REL} '
        f'(sha256 {sha}); the CELL BOUNDARIES are this excerpt\'s segmentation of that text run.',
        '# columns (verbatim header runs): PRADAXA 150 mg twice daily | PRADAXA 110 mg twice daily | Warfarin',
        '',
        '=== TABLES (excerpt) ===',
        'TABLE ' + RUNS[0][0],
        'Row | PRADAXA 150 mg twice daily | PRADAXA 110 mg twice daily | Warfarin',
    ]
    for _run, cells in RUNS[1:]:
        lines.append(' | '.join(cells) if len(cells) == 4 else ' | '.join(cells + ['']))
    OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print(OUT)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'evidence/acquisition_cascade/held')
