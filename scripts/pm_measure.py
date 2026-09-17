"""Offline merged-lane census, source audit and adversarial plant evidence."""
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import claimgraph, page
from scripts.cgx3a_source_audit import audit
from scripts.verify_all import limb_gate_every_page


def main():
    out = ROOT / '.tmp' / 'pm'
    out.mkdir(parents=True, exist_ok=True)
    folder = ROOT / 'docs' / 'reviews' / 'glp1-ra-mace-t2d'
    review = json.loads((folder / 'review.json').read_text(encoding='utf-8'))
    graph = claimgraph.review_graph(review)
    html = (folder / 'index.html').read_text(encoding='utf-8')
    served = claimgraph.scan_rendered(html, graph)
    fresh = claimgraph.scan_rendered(page.render_page(review), graph)
    plant_text = 'The pooled hazard ratio is 0.123456.'
    planted = html.replace('</main>', '<p>' + plant_text + '</p></main>', 1)
    assert planted != html
    plant = [v for v in claimgraph.scan_rendered(planted, graph)['violations']
             if v['detail'] == plant_text]
    assert len(plant) == 1 and plant[0]['code'] == 'SENTENCE_WITHOUT_OBJECT'
    source_audit = audit()
    strands = []
    for strand in review['strands']['strands']:
        cid = claimgraph.register_strand(graph, strand)
        strands.append({'id': strand['strand'],
                        'stored': strand.get('pool'),
                        'recomputed': graph.recompute(cid) if cid else None})
    result = {'served': served, 'fresh': fresh,
              'object_classes': dict(Counter(o['class'] for o in graph.objects.values())),
              'plant': plant, 'source_audit': source_audit, 'strands': strands}
    (out / 'measurement.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('WHOLE PAGE:', served['with_object'], 'registered of', served['rendered_units'], 'nonstructural text units')
    print('CLASSES:', served['with_object_by_class'])
    print('STRUCTURAL:', served['structural_count'], 'of', served['visible_units_before_structural_rules'], 'visible text units before structural rules')
    print('VIOLATIONS:', dict(Counter(v['code'] for v in served['violations'])))
    print('SOURCE AUDIT:', {k: source_audit[k] for k in ('all_source_ids_found', 'all_facts_verified', 'typed_object_violations', 'primary_recomputed')})
    print('STRANDS:', json.dumps(strands))
    print('PLANT: REFUSED (expected)')
    print(json.dumps(plant, indent=2))
    verdict = limb_gate_every_page('glp1-ra-mace-t2d')
    (out / 'gate.json').write_text(json.dumps(verdict, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('GATE:', verdict[0])
    print(verdict[1])


if __name__ == '__main__':
    main()
