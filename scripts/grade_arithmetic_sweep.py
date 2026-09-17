"""Offline corpus GRADE audit and GS artifact regeneration. Run from repository root."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import grade

LANE_BASE = 'e3b70bfa36dc65a3920b20fd4e2d628a270e7d28'


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def public_grade(value, suppressed):
    """Keep the audit rationale, but do not republish a refused pooled statistic."""
    from harness.leakscan import _DERIVED_KEYS
    if not suppressed:
        return value
    if isinstance(value, dict):
        result = {k: public_grade(v, True) for k, v in value.items() if k not in _DERIVED_KEYS}
        removed = sorted(set(value) & _DERIVED_KEYS)
        if removed:
            result['suppressed_fields'] = removed
            result['suppression_reason'] = 'Primary pooled estimand is refused; original baseline remains addressable by baseline_commit.'
        return result
    if isinstance(value, list):
        return [public_grade(v, True) for v in value]
    return value


def sweep(write=False, baseline_commit=LANE_BASE):
    from harness import statistical_layers
    from harness.page import render_page
    rows = []
    for path in sorted((ROOT / 'docs/reviews').glob('*/review.json')):
        review = json.loads(path.read_text(encoding='utf-8'))
        old = subprocess.run(['git', 'show', baseline_commit + ':' + path.relative_to(ROOT).as_posix()], capture_output=True, check=True)
        baseline = json.loads(old.stdout).get('grade')
        ghost_path = ROOT / 'cache' / review['slug'] / 'ghost.json'
        ghost = json.loads(ghost_path.read_text(encoding='utf-8')) if ghost_path.exists() else None
        revised = grade.grade(review, ghost)
        mismatch = bool(baseline and baseline.get('certainty') not in {'provisional', 'not_rateable'} and
                        baseline.get('certainty') != grade.arithmetic_certainty(baseline))
        primary = next((o for o in review.get('outcomes', []) if o.get('primary')), {})
        suppressed = bool((primary.get('result') or {}).get('suppressed_incompatible') or
                          (review.get('grade') or {}).get('certainty') == 'not_rateable')
        row = {'slug': review['slug'], 'before': public_grade(baseline, suppressed), 'after': public_grade(revised, suppressed), 'before_mismatch': mismatch,
               'after_mismatch': False}
        if revised:
            grade.validate_arithmetic(revised)
        if write:
            review['grade'] = revised
            from harness import claimgraph, design_variance
            design_variance.annotate_grade(review)
            claimgraph.stamp_review(review)
            objects = statistical_layers.build(review, ROOT)
            review['statistical_layers'] = objects
            for name, obj in objects.items():
                dump(ROOT / 'cache' / review['slug'] / (name + '.json'), obj)
            row['computability'] = {name: sum(s.get('computable', False) for s in obj.get('specifications', obj.get('rows', []))) for name, obj in objects.items()}
            from harness.canonical import review_sha256, sha256_text
            review.setdefault('reproduction', {})['review_sha256'] = review_sha256(review)
            dump(path, review)
            html = render_page(review)
            (path.parent / 'index.html').write_text(html, encoding='utf-8', newline='\n')
            # Rehash local artifacts; do not claim a new census or release PASS.
            for filename in ['manifest.json', 'REPRODUCTION.json']:
                metadata_path = path.parent / filename
                if metadata_path.exists():
                    metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
                    metadata.update(review_sha256=review_sha256(review), html_sha256=sha256_text(html))
                    dump(metadata_path, metadata)
        rows.append(row)
    out = {'measurement': 'MEASURED', 'baseline_commit': subprocess.check_output(['git', 'rev-parse', baseline_commit], text=True).strip(),
           'denominator': len(rows), 'denominator_name': 'all docs/reviews/*/review.json pages on disk',
           'pages_with_grade_before': sum(bool(r['before']) for r in rows),
           'before_mismatch': sum(r['before_mismatch'] for r in rows),
           'after_mismatch': sum(r['after_mismatch'] for r in rows),
           'after_provisional': sum((r['after'] or {}).get('certainty') == 'provisional' for r in rows),
           'arithmetic': 'bounded ordinal GRADE scale: high(3), moderate(2), low(1), very_low(0); max(0,min(3,start-downgrades+upgrades)); unassessed domains yield provisional',
           'rows': rows}
    dump(ROOT / 'docs/grade_arithmetic_sweep.json', out)
    print(json.dumps({k: v for k, v in out.items() if k != 'rows'}, indent=2))
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='regenerate local objects and pages; no network, no commit')
    parser.add_argument('--baseline', default=LANE_BASE, help='immutable before-state commit; defaults to the GS lane base')
    args = parser.parse_args()
    sweep(args.write, args.baseline)
