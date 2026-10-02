"""Build the offline lane audit and census; only writes outputs/g1_noac."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.g1_noac import read_json, scan_aact, audit, render_report, SLUG


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--aact', type=Path)
    parser.add_argument('--reuse-index', action='store_true', help='Replay the previously captured local AACT rows')
    parser.add_argument('--census', action='store_true', help='Print the full all-topic census (always computed)')
    args = parser.parse_args()
    review = read_json(ROOT / 'docs/reviews' / SLUG / 'review.json')
    ncts = {t['family_id'] for o in review['outcomes'] for t in o['trials']}
    out = ROOT / 'outputs/g1_noac'
    if args.reuse_index:
        index = read_json(out / 'g1_noac.json')['aact']
    elif args.aact:
        index = scan_aact(args.aact, ncts)
    else:
        parser.error('Supply --aact SNAPSHOT or explicit --reuse-index')
    result = audit(ROOT, index)
    out.mkdir(parents=True, exist_ok=True)
    # LF on every platform: the committed outputs must be the bytes a rebuild produces (tests/test_g1_noac.py).
    (out / 'g1_noac.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8',
                                      newline='\n')
    (out / 'G1_NOAC.md').write_text(render_report(result), encoding='utf-8', newline='\n')
    print(json.dumps(result['census'], indent=2))


if __name__ == '__main__':
    main()
