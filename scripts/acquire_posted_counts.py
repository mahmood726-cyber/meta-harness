"""Retain verbatim AACT rows for one trial; no effects or counts entered by hand.

Pass --snapshot (a local AACT export), --nct, and --output explicitly.
Replay uses the resulting small file and never scans the snapshot.
"""
import argparse
import json
from pathlib import Path


def acquire(snapshot, nct, output):
    import re
    if not re.fullmatch(r'NCT\d{8}', nct):
        raise ValueError('invalid registry identifier')
    result = dict(snapshot=snapshot.name, nct_id=nct, tables={})
    for name in ('outcomes', 'outcome_counts', 'outcome_measurements', 'result_groups'):
        with (snapshot/(name+'.txt')).open('rb') as f:
            header = next(f).decode('utf8').rstrip('\r\n')
            fields = header.split('|')
            if 'nct_id' not in fields:
                raise ValueError('missing nct_id column: '+name)
            index = fields.index('nct_id')
            lines = []
            for line in f:
                if nct.encode('ascii') not in line:
                    continue
                text = line.decode('utf8').rstrip('\r\n')
                if text.split('|')[index] == nct:
                    lines.append(text)
        if not lines:
            raise ValueError('no source rows: '+name)
        result['tables'][name] = dict(header=header, lines=lines)
    output.write_text(json.dumps(result, indent=2), encoding='utf8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--nct', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    acquire(args.snapshot, args.nct, args.output)
