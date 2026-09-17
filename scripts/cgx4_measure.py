"""Offline whole-page evidence and renderer grouping for the CGX4 lane."""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bs4 import BeautifulSoup
from harness import claimgraph as cg, page


def regions(document):
    soup = BeautifulSoup(document, 'html.parser')
    yield 'header', str(soup.header)
    loose = []
    for node in soup.main.children:
        if getattr(node, 'get', None) and 'tab' in node.get('class', []):
            if loose:
                yield 'strand tables and sensitivity', ''.join(loose)
                loose = []
            yield node['id'], str(node)
        else:
            loose.append(str(node))
    if loose:
        yield 'strand tables and sensitivity', ''.join(loose)


def measure(slug, output):
    directory = ROOT / 'docs/reviews' / slug
    review = json.loads((directory / 'review.json').read_text(encoding='utf-8'))
    graph = cg.review_graph(review)
    served_html = (directory / 'index.html').read_text(encoding='utf-8')
    fresh_html = page.render_page(review)
    served = cg.scan_rendered(served_html, graph)
    fresh = cg.scan_rendered(fresh_html, graph)
    plant = 'The pooled hazard ratio was 7.77.'
    scan = cg.scan_rendered(fresh_html.replace('</body>', '<p>' + plant + '</p></body>'), graph)
    hits = [v for v in scan['violations'] if v['detail'] == plant]
    assert hits and hits[0]['code'] == 'SENTENCE_WITHOUT_OBJECT'
    section_scans = {name: cg.scan_rendered(body, graph) for name, body in regions(served_html)}
    sources = []
    for cid, obj in graph.objects.items():
        if obj['class'] == 'FACT':
            row = obj['row']
            sources.append({'claim_id': cid, 'id': row.get('id'),
                            'evidence': cg._fact_evidence(row), 'validation': cg.verify_fact(row)})
    strands = {}
    for strand in (review.get('strands') or {}).get('strands') or []:
        local = cg.ClaimGraph()
        cid = cg.register_strand(local, strand)
        # register_strand returns the pool reference for the migrated schema.
        strands[strand['strand']] = local.recompute(cid) if cid else None
    result = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'served': served, 'fresh': fresh, 'served_equals_fresh': served_html == fresh_html,
              'regions': section_scans, 'plant': hits, 'sources': sources,
              'strands': strands, 'typed_object_violations': graph.check(),
              'object_classes': dict(Counter(o['class'] for o in graph.objects.values()))}
    baseline_path = ROOT / '.tmp/cgx4/base.json'
    if baseline_path.exists():
        baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
        old_html = subprocess.check_output(['git', 'show', 'HEAD:docs/reviews/' + slug + '/index.html'], cwd=ROOT).decode('utf-8')
        grouped = {}
        offset = 0
        for name, body in regions(old_html):
            visible = cg.scan_rendered(body, graph)['visible_units_before_structural_rules']
            grouped[name] = [v for v in baseline['violations']
                             if offset < int(v['unit_id'].split('-')[1]) <= offset + visible]
            offset += visible
        assert offset == baseline['visible_units_before_structural_rules'], (offset, baseline['visible_units_before_structural_rules'])
        assert sum(map(len, grouped.values())) == len(baseline['violations'])
        result['baseline_by_renderer'] = grouped
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"{slug}: {served['with_object']} registered of {served['rendered_units']}; {len(served['violations'])} violations")
    print('PLANT: REFUSED')
    print(json.dumps(hits, indent=2))
    print('Strands:', json.dumps(strands))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--slug', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    measure(args.slug, args.output)
