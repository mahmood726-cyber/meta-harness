"""Object-first renderers for recorded typing, membership and audit ledgers.

Recorded decisions are OWED judgements, not source-verified clinical FACTs.
Field projections report the stored ledger only. No HTML/text is ingested into
the registry, and no topic identifiers or research results are constants here.
"""
from copy import deepcopy
from html import escape

from . import claimgraph as cg
from .page_claims import Section
from .section_claims import projection


class Builder:
    def __init__(self, graph=None):
        self.graph = graph if graph is not None else cg.ClaimGraph()
        self.section = Section(self.graph)

    def ref(self, cid):
        return '<!--remainder:' + cid + '-->'

    def field(self, row, field):
        return self.ref(projection(self.graph, deepcopy(row), field))

    def decision(self, path, record, label):
        return self.ref(self.section.judgement(
            path, deepcopy(record), label + ': ' + cg._canonical(record)))

    def count(self, label, states):
        return self.ref(self.section.counts(label, states))

    def interpretation(self, text, alternative):
        return self.ref(self.section.interpretation(text, alternative))

    def finish(self, document):
        if getattr(self.graph, '_collect_remainder', False):
            return ''
        for cid, rendered in self.graph.render_all().items():
            document = document.replace(self.ref(cid), rendered)
        return document


def typed_effects(outcome, graph=None):
    from .effect_type import AXES, known
    effects = outcome.get('effect_types') or []
    if not effects:
        return ''
    b = Builder(graph)
    body = "<section class='typed-effects'><h4>Typed effects</h4><p>"
    body += b.interpretation(
        'Candidate rows include recorded type refusals; typing decisions below await adjudication.',
        'A recorded typing decision can be incomplete or incorrect even when a numeric effect is source-verified.') + '</p>'
    policy = outcome.get('effect_type_target') or {}
    body += '<p>' + b.decision('outcomes.effect_type_target', policy, 'Recorded binding policy') + '</p>'
    body += '<table><tr><th>Axis</th>'
    body += ''.join('<th>' + escape(str(e['trial'])) + '</th>' for e in effects) + '</tr>'
    for axis in AXES:
        body += '<tr><th>' + escape(axis) + '</th>'
        for effect in effects:
            field = effect['axes'][axis]
            css = ('span' if field['basis'].get('span') else 'rule') if known(field) else 'UNKNOWN'
            body += '<td class="' + css + '">' + b.decision('outcomes.effect_types.axes.' + axis,
                                       {'trial': effect['trial'], **field}, 'Recorded ' + axis) + '</td>'
        body += '</tr>'
    body += '</table><ul>'
    for effect in effects:
        body += '<li>' + b.decision('outcomes.effect_types.unification',
            {'trial': effect['trial'], 'unification': effect.get('unification')},
            'Recorded unification') + '</li>'
    body += '</ul><h4>Coercion register</h4>'
    coercions = outcome.get('coercions') or []
    body += '<p>' + b.count('Declared coercion entries', ['DECLARED' for _ in coercions]) + '</p>'
    for row in coercions:
        body += '<p>' + b.decision('outcomes.coercions', row, 'Recorded coercion') + '</p>'
    return b.finish(body + '</section>')


def strand_rows(review, graph=None):
    """Presentation only; selection and pooling remain in the strand engine."""
    b = Builder(graph)
    doc = review.get('strands') or {}
    body = ''
    for strand in doc.get('strands') or []:
        body += '<h4>' + escape(str(strand['name'])) + ': membership and refusals</h4>'
        body += '<table><tr><th>Trial</th><th>Recorded membership decision</th></tr>'
        for collection in ('members', 'refused'):
            for row in strand.get(collection) or []:
                record = {k: row[k] for k in ('trial', 'status', 'axis', 'reason') if k in row}
                record.update(strand=strand['strand'], collection=collection)
                body += '<tr><td>' + b.field(row, 'trial') + '</td><td>'
                body += b.decision('strands.' + collection, record, 'Recorded strand membership') + '</td></tr>'
        body += '</table>'
    body += '<h4>Sensitivity values (never pooled)</h4>'
    for row in doc.get('sensitivity_values') or []:
        cid = row.get('claim_id', 'sensitivity-' + cg.trial_key(row))
        if cid not in b.graph.objects:
            b.graph.add(cid, 'FACT', row=deepcopy(row))
        body += b.ref(cid)
    return b.finish(body)


def absent_trial(row, graph=None):
    b = Builder(graph)
    identity = {k: row[k] for k in ('label', 'id', 'pmid', 'nct') if k in row}
    decision = {k: row[k] for k in ('reason', 'reason_code', 'state', 'source_span',
        'verbatim_span', 'reason_code_audit', 'state_basis', 'completeness_state',
        'completeness_basis', 'harm_absence_state', 'harm_source_span',
        'published_alternative', 'design') if k in row}
    return b.finish('<tr><td colspan="2">' + b.decision('outcomes.declared_absent_trials.identity',
        identity, 'Recorded trial identity') + '</td><td colspan="2">' + b.decision(
        'outcomes.declared_absent_trials', decision, 'Recorded non-pooling assessment') + '</td></tr>')


def reason_audit(review, graph=None):
    audit = review.get('reason_code_audit') or {}
    if not audit:
        return ''
    b = Builder(graph)
    rows = audit.get('rows') or []
    body = "<div class='audit-block'><h3>Reason-code audit</h3><p>"
    body += b.count('Recorded reason-code audit per-item states',
                    [str(r.get('verdict') or 'UNASSESSED') for r in rows]) + '</p>'
    unextracted = (review.get('unextracted_outcome_audit') or {}).get('rows') or []
    body += '<p>' + b.count('Recorded outcome audit per-item states',
                    [str(r.get('status') or 'UNASSESSED') for r in unextracted]) + '</p>'
    body += '<table><tr><th>Trial</th><th>Outcome</th><th>Recorded assessment</th></tr>'
    for row in rows:
        if row.get('verdict') not in ('REASON_FALSE_VALUE_HELD', 'REASON_WRONG_KIND', 'NOT_VERIFIABLE'):
            continue
        body += '<tr><td>' + b.field(row, 'trial_key') + '</td><td>' + b.field(row, 'outcome') + '</td><td>'
        body += b.decision('reason_code_audit.rows', row, 'Recorded reason-code audit') + '</td></tr>'
    return b.finish(body + '</table></div>')


def protocol_metadata(review, neutral=False, graph=None):
    b = Builder(graph)
    protocol = review.get('protocol') or {}
    body = '<table class="kv">'
    for key in ('sha', 'committed_utc', 'method_declared', 'target_endpoint_selection', 'eligibility'):
        if protocol.get(key):
            body += '<tr><th>' + escape(key.replace('_', ' ')) + '</th><td>' + b.field(protocol, key) + '</td></tr>'
    body += '</table>'
    if protocol.get('text') and not neutral:
        body += '<pre class="proto">' + b.field(protocol, 'text') + '</pre>'
    return b.finish(body)


def header(review, neutral=False, graph=None):
    b = Builder(graph)
    sub = b.interpretation('Meta-analysis auditability does not establish authority.',
                          'An auditable analysis may still have incomplete evidence or incorrect decisions.')
    rep = review.get('reproduction') or {}
    pin = ''
    if rep.get('review_sha256'):
        pin = '<div><h4>Pinned audit identity: canonical review object</h4>' + b.field(rep, 'review_sha256') + '</div>'
    return b.finish('<div class="sub">' + sub + '</div>' + pin)


def reproduction_metadata(review, graph=None):
    b = Builder(graph)
    rep = review.get('reproduction') or {}
    body = '<table class="kv">'
    for key in ('failures', 'preregistration', 'protocol_sha', 'review_sha256', 'from_cache'):
        body += '<tr><th>' + escape(key.replace('_', ' ')) + '</th><td>' + b.field(rep, key) + '</td></tr>'
    body += '</table><p>' + b.interpretation(
        'A stored build SHA or cache replay does not establish prospective registration.',
        'Prospective precedence requires a protocol-only history and independent chronology evidence.') + '</p>'
    return b.finish(body)


def comparator_metadata(review, graph=None):
    b = Builder(graph)
    comparator = review.get('comparator') or {}
    body = '<table class="kv">'
    for key in ('name', 'year', 'journal', 'pmid', 'doi', 'open_access', 'url'):
        if key in comparator:
            body += '<tr><th>' + escape(key.replace('_', ' ')) + '</th><td>' + b.field(comparator, key) + '</td></tr>'
    return b.finish(body + '</table>')


def comparator_assessments(review, graph=None):
    b = Builder(graph)
    comparator = review.get('comparator') or {}
    body = '<h4>Recorded comparator assessments</h4>'
    for key in ('scope', 'truth', 'overlap', 'comparator_trial_set', 'quantity_match',
                'comparator_recency', 'treatment_strategy_match', 'outcome_match'):
        if comparator.get(key):
            body += '<p>' + b.decision('comparator.' + key, comparator[key], 'Recorded ' + key) + '</p>'
    if review.get('comparator_scope_note'):
        body += '<p>' + b.decision('comparator_scope_note', review['comparator_scope_note'],
                                   'Recorded comparator resolution') + '</p>'
    body += '<p>' + b.interpretation(
        'Recorded overlap and recency assessments require reconciliation with the current trial identities.',
        'A matching estimate or a stored trial count alone does not establish an independent corroboration.') + '</p>'
    return b.finish(body)


REPORTING_FIELDS = (
    ('5 Eligibility criteria', ('protocol', 'eligibility')),
    ('6 Information sources and dates', ('search', 'databases')),
    ('7 Search strategy', ('search', 'sources')),
    ('8 Selection process', ('screening', 'records')),
    ('9 Data collection', ('outcomes',)),
    ('15 Certainty assessment', ('grade',)),
    ('16a Selection flow', ('screening', 'records')),
    ('16b Exclusions', ('screening', 'records')),
    ('24 Registration and protocol', ('reproduction', 'preregistration')),
)


def presence(inputs):
    """A field-presence check, explicitly not a reporting-quality certification."""
    value = inputs['record']
    for key in inputs['path']:
        if not isinstance(value, dict) or key not in value:
            return 'ABSENT: ' + '.'.join(inputs['path'])
        value = value[key]
    state = 'PRESENT' if value not in (None, '', [], {}) else 'EMPTY'
    return state + ': ' + '.'.join(inputs['path'])


def reporting(review, graph=None):
    b = Builder(graph)
    body = '<p>' + b.interpretation(
        'This table checks whether reporting fields are present; it does not certify PRISMA compliance.',
        'A present field may be incomplete, stale or unsupported by the source evidence.') + '</p>'
    body += '<table class="recs"><tr><th>Reporting item</th><th>Field presence rule</th></tr>'
    for label, path in REPORTING_FIELDS:
        # Carry only the required input branch; unrelated results cannot change
        # the identity or expected output of this presence check.
        inputs = {'record': {path[0]: deepcopy(review.get(path[0]))}, 'path': list(path)}
        cid = b.section.add('TRANSFORMATION', operation='reporting_presence', inputs=inputs,
                            label=label, value=presence(inputs))
        body += '<tr><th>' + escape(label) + '</th><td>' + b.ref(cid) + '</td></tr>'
    return b.finish(body + '</table>')


def receipt(unit, record, graph=None):
    """Deterministic receipt for renderer metadata, never a clinical estimate."""
    b = Builder(graph)
    inputs = {'unit': unit, 'record': deepcopy(record)}
    cid = b.section.add('TRANSFORMATION', operation='renderer_receipt',
                        inputs=inputs, value=receipt_text(inputs))
    return b.finish(b.ref(cid))


def receipt_text(inputs):
    unit, record = inputs['unit'], inputs['record']
    if unit == 'snapshot':
        from .page import _retrieval_mode_label
        return ('Recorded snapshot: records_sha256 ' + str(record.get('records_sha256') or '')
                + '; retrieved_utc ' + str(record.get('retrieved_utc'))
                + '; mode ' + _retrieval_mode_label(record.get('mode')) + '.')
    if unit == 'source_status':
        return 'Recorded adapter states: ' + '; '.join(f'{k}: {v}' for k, v in sorted(record.items()))
    if unit == 'retrieval_class':
        return 'Recorded retrieval classification: ' + ' '.join(str(record.get(k) or '')
                    for k in ('label', 'retraction', 'distinction'))
    if unit == 'search_provenance':
        return ('Recorded search provenance: ' + str(record.get('heading') or '')
                + ' The registry-first (AACT) adapter status for this topic is '
                + str(record.get('registry_first_status') or '') + '; '
                + ' '.join(str(record.get(k) or '') for k in
                           ('class_statement', 'discovery_statement', 'retraction')))
    if unit == 'identifier_scope':
        return 'Recorded identifier scope: ' + cg._canonical(record)
    if unit == 'controls':
        return 'Recorded control assessment (not an independent validation): ' + cg._canonical(record)
    if unit == 'check_ledger':
        return 'Recorded check scope and contradictions (not universal coverage): ' + cg._canonical(record)
    if unit == 'protocol_dimensions':
        dimensions = record.get('agreed_dimensions') or []
        return 'Recorded agreed protocol dimensions: ' + (', '.join(dimensions) if dimensions else 'none; no agreement inferred over an empty set')
    raise ValueError('unsupported renderer receipt')


def replay_boundary(graph=None):
    b = Builder(graph)
    return b.finish(b.interpretation(
        'This page replays the committed retrieval snapshot; it is not a claim that the protocol SHA alone regenerates the page byte-for-byte. A live re-search is a separate, dated event (see Re-search below if present).',
        'A live re-search is a separate dated event and may retrieve a different set of records.'))


def register(review, graph):
    graph._collect_remainder = True
    try:
        from . import integration_prose
        integration_prose.register(review, graph)
        header(review, graph=graph)
        protocol_metadata(review, graph=graph)
        reproduction_metadata(review, graph=graph)
        comparator_metadata(review, graph=graph)
        comparator_assessments(review, graph=graph)
        reporting(review, graph=graph)
        search = review.get('search') or {}
        retrieval = search.get('retrieval') or {}
        classification = search.get('retrieval_class') or {}
        for unit, record in (
            ('snapshot', retrieval.get('snapshot') or {}),
            ('source_status', search.get('source_status') or {}),
            ('retrieval_class', classification),
            ('search_provenance', classification.get('search_provenance') or {}),
            ('identifier_scope', review.get('identifier_scope') or {}),
            ('controls', {key: (review.get('screening') or {}).get(key) for key in ('positive_control', 'negative_control')}),
            ('check_ledger', (review.get('reproduction') or {}).get('claim_check') or {}),
            ('check_ledger', (review.get('reproduction') or {}).get('proposition_check') or {}),
            ('protocol_dimensions', review.get('protocol_config') or {}),
        ):
            receipt(unit, record, graph)
        replay_boundary(graph)
        reason_audit(review, graph=graph)
        if (review.get('strands') or {}).get('generated_from_declarations'):
            strand_rows(review, graph=graph)
        for outcome in review.get('outcomes') or []:
            typed_effects(outcome, graph=graph)
            for row in outcome.get('declared_absent_trials') or []:
                absent_trial(row, graph=graph)
    finally:
        graph._collect_remainder = False
