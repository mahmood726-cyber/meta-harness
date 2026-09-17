"""Lane GL plants: held spans, primary membership, sensitivity isolation."""
import copy
import json
from pathlib import Path

from harness import claimgraph
from harness.pipeline import _build_outcome

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'glp1-ra-mace-t2d'


def regulatory(index=0):
    doc = json.loads((ROOT / 'outputs/handover/glp1_regulatory/regulatory_sources_glp1.json').read_text(encoding='utf-8'))
    source = doc['sources'][index]
    row = claimgraph.regulatory_fact(source, source['decisions'][0])
    row.update(source=row['provenance']['span'], source_level=2, override=True,
               outcome='3-point major adverse cardiovascular events')
    return row


def test_glp1_unlocated_verified_row_refused():
    row = copy.deepcopy(regulatory())
    row['source'] += ' INVENTED SPAN'
    row['provenance']['span'] = row['source']
    spec = {'name': row['outcome'], 'keywords': ['MACE'], 'estimand': 'HR'}
    outcome = _build_outcome(spec, 'efficacy',
        [{'id': '26630143', 'id_type': 'pmid', 'label': 'ELIXA'}],
        {'26630143': {'id': '26630143', 'abstract': ''}},
        ['lixisenatide'], ['placebo'], verified_effects={'26630143': row})
    assert not outcome['trials'], f"UNLOCATED ROW WOULD POOL: {outcome['trials']}"


def test_glp1_elixa_located_and_primary_membership():
    row = regulatory()
    text = (ROOT / row['provenance']['extracted_text']).read_bytes().decode('utf-8')
    assert text.find(row['source']) >= 0
    from scripts.reproduce_review import replay_core
    core = replay_core(SLUG)
    strands = core.get('strands', {}).get('strands', [])
    primary = next((s for s in strands if s['strand'] == 'CONVENTIONAL_GLP1RA'), None)
    assert primary is not None, 'CONVENTIONAL_GLP1RA strand is absent on base'
    members = {m['pmid'] for m in primary['members']}
    assert '26630143' in members
    assert primary['k'] == len(members)
    assert not members & {'38785209', '34215025', '30291013', '34873344'}
    assert {r['pmid']: r['axis'] for r in primary['refused']} == {
        '38785209': 'censoring', '34215025': 'censoring', '30291013': 'endpoint_components'}


def test_glp1_freedom_sensitivity_never_pooled():
    from scripts.reproduce_review import replay_core
    core = replay_core(SLUG)
    strands = core.get('strands', {}).get('strands', [])
    assert strands, 'GLP1 strands absent on base'
    assert any(r['effect'] == 1.36 for r in core['strands']['sensitivity_values'])
    assert all(m['effect'] != 1.36 for s in strands for m in s['members'])
