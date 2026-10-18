"""Declared posted-result count conversion; no inferred arm IDs or numeric constants."""
import hashlib
import json
from pathlib import Path


def route(config, root, record):
    d = config['posted_results_conversion']
    if d['method'] != 'sum_disjoint_dose_arms' or d['analysis_set_policy'] != 'posted_outcome_analysed_N':
        raise ValueError('POSTED_COUNTS_CONVERSION_UNSUPPORTED')
    if str(record['id']) != d['report_id'] or d['nct_id'] not in json.dumps(record):
        raise ValueError('POSTED_COUNTS_REPORT_IDENTITY')
    raw = (Path(root)/d['source_ref']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != d['sha256']:
        raise ValueError('POSTED_COUNTS_DIGEST')
    doc = json.loads(raw)
    if doc['snapshot'] != d['snapshot'] or doc['nct_id'] != d['nct_id']:
        raise ValueError('POSTED_COUNTS_SNAPSHOT_IDENTITY')
    evidence = []
    def rows(table):
        obj = doc['tables'][table]
        keys = obj['header'].split('|')
        result = []
        for line in obj['lines']:
            cells = line.split('|')
            if len(cells) != len(keys):
                raise ValueError('POSTED_COUNTS_SCHEMA')
            r = dict(zip(keys, cells))
            if r['nct_id'] != d['nct_id']:
                raise ValueError('POSTED_COUNTS_TRIAL_IDENTITY')
            result.append((r, dict(table=table, header=obj['header'], row=line)))
        return result
    def one(candidates):
        if len(candidates) != 1:
            raise ValueError('POSTED_COUNTS_NONUNIQUE_JOIN')
        r, ev = candidates[0]
        evidence.append(ev)
        return r
    outcome = one([(r,e) for r,e in rows('outcomes') if r['title'] == d['outcome_title']])
    if outcome['title'] not in config['primary_outcome']['keywords'] or outcome['param_type'] != 'COUNT_OF_PARTICIPANTS':
        raise ValueError('POSTED_COUNTS_ENDPOINT_UNBOUND')
    titles = d['intervention_titles'] + d['comparator_titles']
    if len(set(titles)) != len(titles) or not d['intervention_titles'] or not d['comparator_titles']:
        raise ValueError('POSTED_COUNTS_ARMS_OVERLAP')
    groups = [(r,e) for r,e in rows('result_groups') if r['outcome_id'] == outcome['id']]
    if sorted(r['title'] for r,e in groups) != sorted(titles):
        raise ValueError('POSTED_COUNTS_ARM_PARTITION')
    values = {}
    for title in titles:
        group = one([(r,e) for r,e in groups if r['title'] == title])
        agent = 'hydroxychloroquine' if title in d['intervention_titles'] else 'placebo'
        if agent not in group['description'].lower():
            raise ValueError('POSTED_COUNTS_ARM_IDENTITY')
        def joined(table):
            return [(r,e) for r,e in rows(table) if r['outcome_id'] == outcome['id'] and r['result_group_id'] == group['id']]
        count = one(joined('outcome_counts'))
        measurement = one(joined('outcome_measurements'))
        if (count['scope'] != 'Measure' or count['units'] != 'Participants'
                or measurement['units'] != 'Participants' or measurement['param_type'] != 'COUNT_OF_PARTICIPANTS'
                or measurement['title'] != outcome['title'] or measurement['category'] or measurement['classification']):
            raise ValueError('POSTED_COUNTS_ANALYSIS_SET')
        event, total = int(measurement['param_value']), int(count['count'])
        if not 0 <= event <= total or total <= 0:
            raise ValueError('POSTED_COUNTS_INVALID')
        values[title] = [event, total]
    def combine(names):
        return tuple(sum(values[n][i] for n in names) for i in range(2))
    a,n = combine(d['intervention_titles']); c,m = combine(d['comparator_titles'])
    span = '\n'.join(e['table']+'\n'+e['header']+'\n'+e['row'] for e in evidence)
    if (d['comparison_status'], d['comparison_reason']) != ('DIVERGENT_NAMED', 'ANALYSIS_SET'):
        raise ValueError('POSTED_COUNTS_COMPARISON_VOCABULARY')
    return dict(outcome=config['primary_outcome']['name'], override=True,
        ai=a, n1i=n, ci=c, n2i=m, kind='extracted_counts', typed_route='hcq_combined_dose_counts',
        provenance='aact_verified', source_level=1, source=span, source_span=span,
        document_ref=d['source_ref'], document_sha256=d['sha256'],
        verification='Posted participant counts joined by outcome and group; arm titles and descriptions bind orientation; disjoint HCQ dose arms summed with analysed N.',
        analysis_set_comparison=dict(status=d['comparison_status'], reason_code=d['comparison_reason'],
            analysis_set=d['analysis_set_policy'], endpoint=outcome['title'], evidence=evidence,
            reason='Use the posted outcome analysed denominators. Comparator figure uses a different analysis set; its denominators are not substituted for posted N.'),
        design_adjustment=dict(kind='COMBINED_DISJOINT_ARMS', method=d['method'], arms=values,
            source=d['source_ref'], document_sha256=d['sha256'], span=span))
