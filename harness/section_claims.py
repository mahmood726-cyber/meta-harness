"""Typed rendering for selection, harms and review-boundary disclosures.

Projections describe the *recorded ledger*, not independently verified clinical
facts. Clinical prose without located evidence is deliberately left as scan debt.
No HTML is parsed, blessed or wrapped after rendering.
"""
from collections import Counter
from copy import deepcopy
from html import escape
from html import unescape

from . import claimgraph as cg
from . import identity


def projection(graph, row, field, label=None):
    """Register an exact field selection; mutations invalidate the stored value."""
    inputs = {'record': row, 'field': field}
    cid = 'ledger-field-' + cg._sha(inputs)[:20]
    if cid not in graph.objects:
        graph.add(cid, 'TRANSFORMATION', operation='ledger_field', inputs=inputs,
                  value=deepcopy(row.get(field)), label=label or field, ledger_projection=True)
    return cid


def aggregate(graph, operation, inputs, label):
    cid = 'ledger-aggregate-' + cg._sha([operation, inputs, label])[:20]
    if cid not in graph.objects:
        graph.add(cid, 'TRANSFORMATION', operation=operation, inputs=inputs,
                  label=label, value=None)
        try:
            graph.objects[cid]['value'] = graph.recompute(cid)
        except (KeyError, TypeError, ValueError):
            # Keep the invalid object so ClaimGraph renders a typed refusal.
            pass
    return cid


SCREEN_FIELDS = ('id', 'id_type', 'decision', 'rule_id', 'found_by',
                 'trial_family_id', 'publication_role', 'completeness_state', 'reason', 'span')
HARM_FIELDS = ('label', 'id', 'trial_family_id', 'publication_role', 'reason',
               'state', 'state_basis', 'source_span', 'completeness_state',
               'completeness_basis', 'harm_absence_state', 'harm_source_span')
RETRIEVAL_FIELDS = ('kind', 'query', 'run_utc', 'state', 'flow', 'cap', 'discovery_capable')


def register(graph, review):
    recs = (review.get('screening') or {}).get('records') or []
    primary = cg.primary_outcome(review) or {}
    search = review.get('search') or {}
    for row in recs:
        for field in SCREEN_FIELDS:
            projection(graph, row, field)
    if recs:
        aggregate(graph, 'selection_flow', {'records': recs, 'primary': primary}, 'Selection ledger')
    if search:
        for field in ('databases', 'cache_ref', 'run_utc'):
            projection(graph, search, field)
        for source in (search.get('retrieval') or {}).get('sources') or []:
            for field in RETRIEVAL_FIELDS:
                aggregate(graph, 'retrieval_cell', {'source': source, 'field': field}, 'Retrieval ledger')
        for row in (search.get('retrieval_class') or {}).get('basis') or []:
            for field in ('query', 'kind', 'features'):
                projection(graph, row, field)
        for source in search.get('sources') or []:
            for index, query in enumerate(source.get('queries') or []):
                aggregate(graph, 'query_item', {'source': source, 'index': index}, 'Recorded query')
        states = list((search.get('source_status') or {}).values())
        aggregate(graph, 'state_counts', states, 'Adapter states')
    for outcome in review.get('outcomes') or []:
        if outcome.get('kind') != 'harm':
            continue
        rows = outcome.get('declared_absent_trials') or []
        for row in rows:
            for field in HARM_FIELDS:
                projection(graph, row, field)
        aggregate(graph, 'harms_states', {'rows': rows, 'trials': outcome.get('trials') or []},
                  'Harms ledger: ' + outcome.get('name', 'unnamed'))
    comparator = review.get('comparator') or {}
    parity = (review.get('reproduction') or {}).get('parity') or {}
    if parity and (comparator.get('overlap') or {}).get('shared_trials') is not None:
        aggregate(graph, 'parity_consistency', parity_inputs(review), 'Parity enumeration check')
    for field in ('quantity_match', 'treatment_strategy_match', 'outcome_match'):
        obj = comparator.get(field)
        if obj:
            cid = 'comparator-judgement-' + cg._sha([field, obj])[:20]
            if cid not in graph.objects:
                graph.add(cid, 'JUDGEMENT', text=f"Recorded {field}: {obj.get('status')}. {obj.get('note') or ''}",
                          basis={'review_field': '/comparator/' + field, 'stored_assessment': obj},
                          adjudication='OWED')
    boundary_objects(graph, review)


def boundary_objects(graph, review):
    """Interpretations state alternatives; factual historical assertions stay debt."""
    objects = {
        'oa': ('Open-access comparator only. Restricting the benchmark to an OA-retrievable publication narrows the comparator set.',
               'An OA comparator supports a reproducible comparison within that restricted set; it does not establish comparison with the full literature.'),
        'small-k': ('Small k on many topics. Sparse trial sets limit what can be inferred about between-trial heterogeneity.',
                    'A sparse trial set can still be reported as individual trial evidence, with uncertainty and pooling refusals shown.'),
        'screening': ('Dual screening is not fully independent. Agreement between rule screeners sharing criteria should not be read as independent validation.',
                      'Agreement can describe consistency under shared criteria without establishing independent reliability.'),
    }
    for key, (text, alternative) in objects.items():
        cid = 'section-boundary-' + key
        if cid not in graph.objects:
            graph.add(cid, 'INTERPRETATION', text=text, alternatives=[alternative])


def local_graph(review):
    graph = cg.ClaimGraph()
    register(graph, review)
    return graph


def screening_rows(review):
    graph = local_graph(review)
    rendered = graph.render_all()
    rows = (review.get('screening') or {}).get('records') or []
    return ''.join('<tr>' + ''.join('<td>' + rendered[projection(graph, row, field)] + '</td>'
                                   for field in screening_fields(review)) + '</tr>' for row in rows)


def screening_fields(review):
    rows = (review.get('screening') or {}).get('records') or []
    return [field for field in SCREEN_FIELDS
            if (field != 'found_by' or (review.get('search') or {}).get('retrieval'))
            and (field not in ('trial_family_id', 'publication_role', 'completeness_state')
                 or any(row.get(field) for row in rows))]


def selection_flow(review):
    graph = local_graph(review)
    inputs = {'records': (review.get('screening') or {}).get('records') or [],
              'primary': cg.primary_outcome(review) or {}}
    cid = aggregate(graph, 'selection_flow', inputs, 'Selection ledger')
    return '<p>' + graph.render(cid) + '</p>'


def harms_unpooled(outcome):
    """Only the no-pooled-trials schema; other harms schemas retain their renderer."""
    graph = local_graph({'outcomes': [outcome]})
    rendered = graph.render_all()
    rows = outcome.get('declared_absent_trials') or []
    cid = aggregate(graph, 'harms_states', {'rows': rows, 'trials': outcome.get('trials') or []},
                    'Harms ledger: ' + outcome.get('name', 'unnamed'))
    body = '<h4>' + escape(outcome.get('name', '')) + '</h4><p>' + rendered[cid] + '</p>'
    groups = (HARM_FIELDS[:4], HARM_FIELDS[4:8], HARM_FIELDS[8:10], HARM_FIELDS[10:])
    body += '<table class="arms"><tr><th>Trial identity</th><th>Recorded extraction assessment</th><th>Completeness</th><th>Harms assessment</th></tr>'
    for row in rows:
        body += '<tr>' + ''.join('<td>' + '<br>'.join(rendered[projection(graph, row, field)] for field in fields)
                                + '</td>' for fields in groups) + '</tr>'
    return body + '</table>'


def boundary(review, key):
    return local_graph(review).render('section-boundary-' + key)


def search_metadata(review):
    graph = local_graph(review)
    source = review.get('search') or {}
    rendered = graph.render_all()
    rows = [(field, rendered[projection(graph, source, field)])
            for field in ('databases', 'cache_ref', 'run_utc')]
    return '<table class="kv">' + ''.join('<tr><th>' + field.replace('_', ' ') + '</th><td>' + value + '</td></tr>'
                                         for field, value in rows) + '</table>'


def retrieval_rows(retrieval):
    graph = local_graph({'search': {'retrieval': retrieval}})
    rendered = graph.render_all()
    return ''.join('<tr>' + ''.join('<td>' + rendered[aggregate(
        graph, 'retrieval_cell', {'source': source, 'field': field}, 'Retrieval ledger')] + '</td>'
        for field in RETRIEVAL_FIELDS) + '</tr>' for source in retrieval.get('sources') or [])


def retrieval_basis_rows(classification):
    graph = local_graph({'search': {'retrieval_class': classification}})
    rendered = graph.render_all()
    return ''.join('<tr>' + ''.join('<td>' + rendered[projection(graph, row, field)] + '</td>'
                                   for field in ('query', 'kind', 'features')) + '</tr>'
                   for row in classification.get('basis') or [])


def query_render(source, index):
    graph = local_graph({'search': {'sources': [source]}})
    cid = aggregate(graph, 'query_item', {'source': source, 'index': index}, 'Recorded query')
    return graph.render(cid)


def comparator_assessment(review, field):
    obj = review['comparator'][field]
    cid = 'comparator-judgement-' + cg._sha([field, obj])[:20]
    return local_graph(review).render(cid)


def parity_inputs(review):
    return {'trials': (cg.primary_outcome(review) or {}).get('trials') or [],
            'overlap': (review.get('comparator') or {}).get('overlap') or {}}


def parity_check(review):
    graph = local_graph(review)
    cid = aggregate(graph, 'parity_consistency', parity_inputs(review), 'Parity enumeration check')
    return graph.render(cid)


def recompute(operation, inputs):
    if operation == 'query_item':
        return inputs['source']['queries'][inputs['index']]
    if operation == 'retrieval_cell':
        from . import page
        source, field = inputs['source'], inputs['field']
        funnel = source.get('funnel') or {}
        if field == 'kind':
            text = page._retrieval_kind_label(source.get('kind'))
        elif field == 'state':
            text = page._retrieval_state_text(source)
        elif field == 'flow':
            text = ' -> '.join(page._retrieval_value(funnel.get(key)) for key in ('hits', 'fetched', 'retained'))
        elif field == 'cap':
            text = page._retrieval_cap_text(funnel.get('cap'))
        elif field == 'discovery_capable':
            text = 'yes' if source.get(field) else 'no'
        elif field in ('query', 'run_utc'):
            return source.get(field) or 'not recorded'
        else:
            raise ValueError('unsupported retrieval field')
        # These source-format functions use only this known presentation tag;
        # no arbitrary rendered prose is parsed or registered.
        return unescape(text.replace('<strong>', '').replace('</strong>', ''))
    if operation == 'parity_consistency':
        overlap = inputs['overlap']
        shared, only = overlap['shared_trials'], overlap.get('only_ours') or []
        if len(set(shared)) != len(shared) or len(set(only)) != len(only):
            raise ValueError('duplicate comparator trial labels')
        ours = identity.unit_counts(inputs['trials'])['trials']
        enumerated = len(set(shared) | set(only))
        return {'pooled_families': ours, 'shared_labels': len(shared), 'only_ours_labels': len(only),
                'enumerated_ours': enumerated, 'count_consistent': ours == enumerated}
    if operation == 'ledger_field':
        if inputs['field'] not in inputs['record']:
            return None
        return inputs['record'][inputs['field']]
    if operation == 'selection_flow':
        records, primary = inputs['records'], inputs['primary']
        if len({row['id'] for row in records}) != len(records):
            raise ValueError('duplicate screened record identifiers')
        included = [r for r in records if r.get('decision') == 'include']
        excluded = [r for r in records if r.get('decision') == 'exclude']
        unresolved = [r for r in records if r.get('decision') not in ('include', 'exclude')]
        return {'screened_records': len(records), 'included': identity.unit_counts(included),
                'excluded_by_rule': dict(sorted(Counter(r.get('rule_id') or 'UNCLASSIFIED' for r in excluded).items())),
                'unresolved_records': len(unresolved),
                'pooled_primary': identity.unit_counts(primary.get('trials') or []),
                'unpooled_primary_states': dict(sorted(Counter(r.get('state') or r.get('reason_code') or 'UNCLASSIFIED'
                                                             for r in primary.get('declared_absent_trials') or []).items())),
                'unpooled_primary_kinds': dict(sorted(Counter(r.get('absent_kind') or 'UNCLASSIFIED'
                                                            for r in primary.get('declared_absent_trials') or []).items()))}
    if operation == 'harms_states':
        rows = inputs['rows']
        return {'extracted_rows': len(inputs['trials']), 'unpooled_rows': len(rows),
                'states': dict(sorted(Counter(r.get('harm_absence_state') or r.get('state') or 'UNCLASSIFIED' for r in rows).items()))}
    raise ValueError('unsupported section operation')


def transformation_text(obj, value):
    if obj['operation'] == 'query_item':
        return 'Recorded query: ' + str(value)
    if obj['operation'] == 'retrieval_cell':
        return str(value)
    if obj['operation'] == 'parity_consistency':
        return (f"Parity enumeration check: {value['pooled_families']} pooled trial families; "
                f"{value['shared_labels']} recorded shared labels and {value['only_ours_labels']} only-ours labels "
                f"enumerate {value['enumerated_ours']} distinct labels. "
                + ('Counts reconcile; identifier-level trial-set validation remains owed.' if value['count_consistent'] else
                   'UNRENDERABLE parity relation: the recorded overlap does not reconcile with the current pool; adjudication OWED.'))
    if obj['operation'] == 'ledger_field':
        # A ledger observation is explicitly labelled, not silently promoted to FACT.
        text = (', '.join(str(item) for item in value) if isinstance(value, list) else
                cg._canonical(value) if isinstance(value, dict) else ('not recorded' if value is None else str(value)))
        return 'Recorded ' + obj['label'] + ': ' + text
    if obj['operation'] == 'selection_flow':
        return (f"{value['screened_records']} records screened; {identity.count_phrase(value['included'], 'trial family')} included. "
                f"Excluded records by rule: {cg._canonical(value['excluded_by_rule'])}; unresolved records: {value['unresolved_records']}. "
                f"Pooled in the primary outcome: {identity.count_phrase(value['pooled_primary'], 'trial family')}. "
                f"Unpooled primary report states: {cg._canonical(value['unpooled_primary_states'])}; "
                f"recorded absence/refusal kinds: {cg._canonical(value['unpooled_primary_kinds'])}.")
    if obj['operation'] == 'harms_states':
        prefix = 'HARMS_INCOMPLETE. ' if value['states'].get('KNOWN_REPORTED_NOT_YET_EXTRACTED') else ''
        return (prefix + f"{value['extracted_rows']} extracted rows; {value['unpooled_rows']} unpooled rows. "
                f"Per-report harms states: {cg._canonical(value['states'])}. These ledger states do not establish harm absence.")
    raise ValueError('unsupported section rendering')
