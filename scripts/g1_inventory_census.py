"""Replay all topics; --write regenerates only the lane's acquisition queues."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.inventory_queue import build_queue, verify, read, RESOLUTIONS, HYPOTHESES
from scripts.g1_proposal_census import census as proposal_census, metric


def census(root=ROOT, write=False):
    root = Path(root)
    base = proposal_census(root)
    all_rows, topics = [], []
    for topic in base['topics']:
        missing = [t for t in topic['trials'] if t['status'] == 'MISSING_FROM_OURS']
        rows = []
        refusal = None
        if missing or (root / 'evidence/g1_inventory_queue' / (topic['slug'] + '.json')).exists():
            queue = build_queue(topic, root)
            path = root / 'evidence/g1_inventory_queue' / (topic['slug'] + '.json')
            verify(queue, root, base)
            if write:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            held = read(path)
            verify(held, root, base)
            if held != queue:
                raise ValueError('REFUSED_STALE_QUEUE:' + topic['slug'])
            refusal = queue['source_refusal']
            rows = [dict(item=topic['slug'] + '::' + r['label'],
                         resolution=r['resolution'], hypothesis=r['why_missing_hypothesis']) for r in held['missing']]
        all_rows.extend(rows)
        add = sum(r['hypothesis'] == 'NOT_RETRIEVED_BY_SEARCH' for r in rows)
        topics.append(dict(slug=topic['slug'], missing=len(rows), source_refusal=refusal,
            resolution={k: metric([r['item'] for r in rows if r['resolution'] == k], len(rows)) for k in RESOLUTIONS},
            hypothesis={k: metric([r['item'] for r in rows if r['hypothesis'] == k], len(rows)) for k in HYPOTHESES},
            ceiling=dict(label='CEILING, not a claim', our_k=topic['our_k'], hypothetical_additions=add,
                         k=topic['our_k'] + add if topic['our_k'] is not None else None)))
    return dict(interpretation='Acquisition hints only. NOT_RETRIEVED_BY_SEARCH is a hypothesis from unmatched inventory labels, not proof of search failure. Scope notes are retained but do not establish trial-specific ineligibility. CEILING assumes every hypothesised search gap is a distinct eligible trial screened in; no pool admission or effect estimate.',
                topics_examined=metric([t['slug'] for t in topics], len(list((root / 'topics').glob('*.json')))),
                missing=metric([r['item'] for r in all_rows], base['rules']['MISSING_FROM_OURS']['N']),
                resolution={k: metric([r['item'] for r in all_rows if r['resolution'] == k], len(all_rows)) for k in RESOLUTIONS},
                hypothesis={k: metric([r['item'] for r in all_rows if r['hypothesis'] == k], len(all_rows)) for k in HYPOTHESES},
                topics=topics)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    print(json.dumps(census(write=args.write), ensure_ascii=False, indent=2, sort_keys=True))
