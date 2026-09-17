"""Refresh only GLP1 companion coverage; no invented assessments or network."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import glp1, rob2, claimgraph


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def write(path, value):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    base = 'cache/' + glp1.SLUG + '/'
    data = glp1.augment(load(base + 'records.json'))
    records = {r['id']: r for r in data['records']}
    effects = load(base + 'verified_effects.json')
    new = ('26630143', '38785209', '34873344')
    contrast = load(base + 'arm_contrast.json')
    rob = load(base + 'rob2.json')
    designs = load(base + 'registry_designs.json')
    for pmid in new:
        rec = records[pmid]
        text = rec['abstract'].lower()
        # Existing AACT parser has not measured these contrasts. Record the debt,
        # rather than letting absence silently pass or asserting parser verification.
        contrast['trials'][pmid] = {'nct': rec['nct'], 'status': 'unknown',
            'basis': 'AACT arm-label parser not run for this added row; abstract reports random assignment versus placebo.',
            'source_span': rec['abstract'], 'common': [], 'differing': []}
        design = designs.get(rec['nct']) or {}
        secondary = []
        if pmid == '38785209':
            identity = effects[pmid]['endpoint_identity']
            secondary = [identity['measure_verbatim']]
        domains = rob2.assess(design, [], glp1.OUTCOME, rob2._simple_matches,
            registered_secondaries=secondary,
            blinded_by_text=any(t in text for t in ('double-blind', 'double blind')),
            randomized_by_text=any(t in text for t in ('randomly assigned', 'randomized', 'randomised')))
        basis = rob2.rob_basis(domains)
        rob['trials'][pmid] = {'nct': rec['nct'], 'registry_in_aact': bool(design),
            'assessed_from': 'held registry design and abstract; machine signals only',
            'formal_rob2': 'NOT_ASSESSED', 'overall': rob2.overall(domains),
            'domains': domains, 'rob_basis': basis,
            'assessed_domains': basis['assessed_domains'], 'unassessed_domains': basis['unassessed_domains']}
    write(base + 'arm_contrast.json', contrast)
    write(base + 'rob2.json', rob)
    integrity = load(base + 'integrity.json')
    for pmid in ('26630143', '38785209'):
        integrity['per_pmid'][pmid] = {'retracted': None, 'concern': None,
            'status': 'NOT_ASSESSED', 'evidence': 'Current PubMed correction/retraction check not performed; offline lane.'}
    integrity.update(n_pooled=len(integrity['per_pmid']),
        unassessed_pmids=['26630143', '38785209'],
        n_pubmed_checked=sum(r.get('status') != 'NOT_ASSESSED' for r in integrity['per_pmid'].values()))
    write(base + 'integrity.json', integrity)
    path = 'docs/evidence/override-audit-2026-09-14/overrides.json'
    audit = [r for r in load(path) if r['topic'] != glp1.SLUG]
    for pmid, row in effects.items():
        assert claimgraph.verify_fact(row)['verified']
        audit.append({'topic': glp1.SLUG, 'file': 'verified_effects.json', 'trial': pmid,
            'outcome': row['outcome'], 'source_committed': True,
            'source_committed_evidence': row['document_ref'],
            'document_sha256': row['document_sha256'], 'span_offset': row['span_offset'],
            'override_with': {k: row[k] for k in ('effect', 'ci_low', 'ci_high', 'scale')},
            'judgement': 'B-prime source hierarchy: exact declared 3-point MACE row; digits, bounds, digest and span verified offline. FLOW censoring UNKNOWN retained.',
            'rule_group': 'Document-bound target endpoint', 'harness_module': 'harness.verified_source'})
    write(path, audit)
    print('GLP1 companion coverage refreshed; contrast parser and formal RoB 2 remain explicitly unassessed.')


if __name__ == '__main__':
    main()
