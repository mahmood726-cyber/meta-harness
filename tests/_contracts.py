"""Test contracts for the enforcement-gate era: the evidence PARTITION of an outcome (pooled | set aside on admission with
the candidate tuple | other declared-absent) and admitted-pool semantics -- properties, never corpus counts. Drafted by
Codex lane T (gpt-6-astra, xhigh, 2026-09-22) while sorting 56 failing tests into regression / pinned finding / red by
design; read and adopted by the integrator, who added no assertion that recomputes what the code computes."""
import json
from pathlib import Path
from harness import admission, estmeasure

def partition(root, slug, outcome):
    from harness.family_compact import read_families
    families = read_families(Path(root)/'cache'/slug/'families.json')['families']
    by_report = {str(r['report_id']).replace('PMID ', ''): f for f in families for r in f.get('reports', [])}
    by_family = {f['family_id']: f for f in families}
    pooled = outcome.get('trials') or []
    absent = outcome.get('declared_absent_trials') or []
    ids = lambda rows: [str(t['id']).replace('PMID ', '') for t in rows]
    assert len(ids(pooled)) == len(set(ids(pooled)))
    assert not set(ids(pooled)) & set(ids(absent))
    for row in pooled + [a for a in absent if admission.is_set_aside(a)]:
        fam = by_report.get(str(row['id']).replace('PMID ', '')) or by_family.get(row.get('family_id'))
        verdict = admission.verdict(row, fam)
        assert row['admission_verdict'] == verdict
        if row in pooled:
            assert verdict['final'] in {'ADMISSIBLE', 'MIGRATION_STATE_UNBOUND_LEGACY'}
        else:
            assert verdict['final'] == 'INADMISSIBLE'
            assert row['reason_code'] in verdict['failing']
            assert row.get('candidate_tuple') and row.get('reason') and row.get('recovery')
    assert outcome['admission_summary']['pooled_rows'] == len(pooled)
    if not pooled:
        assert outcome['result'].get('present') is False
        assert not outcome['result'].get('k') and outcome['result'].get('estimate') is None
        assert outcome['result'].get('reason')
    return pooled, absent

def accounted_row(root, slug, outcome, pid):
    pooled, absent = partition(root, slug, outcome)
    rows = [r for r in pooled + absent if str(r['id']).replace('PMID ', '') == pid]
    assert len(rows) == 1, (slug, pid)
    return rows[0], rows[0] in pooled

def scale_contract(outcome):
    rows = outcome.get('trials') or []
    result = outcome['result']
    if not rows:
        assert result.get('present') is False and result.get('estimate') is None
        return
    effects = [t.get('effect_object') or estmeasure.classify(t.get('scale') or outcome.get('served_estimand') or outcome['estimand'], t.get('source', '')) for t in rows]
    expected = estmeasure.pool_compatibility(effects)
    assert result['estmeasure'] == expected
    incompatible = expected['status'] == 'incompatible'
    assert bool(result.get('suppressed_incompatible')) == incompatible
    if incompatible:
        assert all(result.get(k) is None for k in ('estimate', 'ci_low', 'ci_high', 'tau2', 'pi_low', 'pi_high'))
    elif expected['status'] == 'compatible_labels':
        assert set(result.get('scale_mixed') or []) == set(expected['labels'])
        label = result['effect_label']
        for name in expected['labels']:
            count = sum(e['reported_label'] == name for e in effects)
            assert f'{count} {name}' in label

def candidate_cross_source(root, slug, outcome, pid):
    from harness.pipeline import _cross_source
    import subprocess
    row, pooled = accounted_row(root, slug, outcome, pid)
    root = Path(root)
    cfg = json.loads((root/'topics'/f'{slug}.json').read_text(encoding='utf-8'))
    recs = json.loads((root/'cache'/slug/'records.json').read_text(encoding='utf-8'))
    record = next(r for r in recs['records'] if str(r['id']) == pid)
    ex = dict(row, **row.get('candidate_tuple', {}))
    if pooled:
        return row['cross_source']
    # Exercise source identity even when admission excludes the clinical row; never re-admit it.
    previous = json.loads(subprocess.check_output(['git', 'show', f'38c04411484dbea035a8e4c8e22c57c2794f9495:docs/reviews/{slug}/review.json'], cwd=root))
    original = next(t for o in previous['outcomes'] if o.get('primary') for t in o['trials'] if str(t['id']).replace('PMID ', '') == pid)
    assert all(original.get(k) == v for k, v in row['candidate_tuple'].items())
    ex = dict(original, **row['candidate_tuple'])
    return _cross_source(ex, record['nct'], recs['ctgov_results'], cfg['primary_outcome'], cfg['intervention_terms'], cfg['comparator_terms'])
