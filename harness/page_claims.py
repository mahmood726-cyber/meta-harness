"""Object-first prose for overview, pool summaries and missing-evidence panels.

No rendered-text ingestion: each object is made from an identified review field.
Unadjudicated recorded decisions remain OWED, never promoted to source FACTs.
"""
from html import escape

from . import claimgraph as cg
from . import scope_identity


def _text(value):
    return cg._canonical(value) if isinstance(value, (dict, list)) else str(value)


class Section:
    def __init__(self, graph=None):
        self.graph = graph if graph is not None else cg.ClaimGraph()
        self.parts = []

    def add(self, kind, **fields):
        cid = 'page-' + cg._sha({'class': kind, **fields})[:20]
        if cid not in self.graph.objects:
            self.graph.add(cid, kind, **fields)
        self.parts.append(cid)
        return cid

    def judgement(self, label, record, text, *, rule=None):
        return self.add('JUDGEMENT', text=text,
                        basis={'source_field': label, 'record': record,
                               **({'rule_id': rule} if rule else {})},
                        adjudication='RULE' if rule else 'OWED')

    def counts(self, label, states):
        return self.add('TRANSFORMATION', operation='state_counts', inputs=states,
                        value={s: states.count(s) for s in sorted(set(states))}, label=label)

    def interpretation(self, text, alternative):
        return self.add('INTERPRETATION', text=text, alternatives=[alternative])

    def html(self):
        if getattr(self.graph, '_collect_page_objects', False):
            return ''
        # Validate the dependency closure of this section, not every unrelated
        # object registered for an independent whole-page scan.
        local = cg.ClaimGraph(self.graph.root)
        pending = list(self.parts)
        while pending:
            cid = pending.pop()
            if cid in local.objects or cid not in self.graph.objects:
                continue
            local.objects[cid] = self.graph.objects[cid]
            pending.extend(local.objects[cid].get('depends_on') or [])
        local.invalidated = self.graph.invalidated.copy()
        rendered = local.render_all()
        return ''.join('<p>' + rendered[cid] + '</p>' for cid in self.parts)


def pool_object(outcome, graph):
    """Only the reported-effect schema is migrated; other schemas stay debt."""
    rows = outcome.get('trials') or []
    result = outcome.get('result') or {}
    if (not rows or result.get('scale') not in ('HR', 'RR', 'OR', 'IRR')
            or not all(cg._fact_evidence(t).get('document_sha256') for t in rows)
            or any(result.get(k) for k in ('pool_refused', 'pooled_ci_refused', 'suppressed_incompatible', 'unrenderable'))
            or any(any(t.get(k) is None for k in ('effect', 'ci_low', 'ci_high')) for t in rows)):
        return None
    refs = []
    for trial in rows:
        row = dict(trial, scale=trial.get('scale') or outcome.get('estimand'))
        cid = 'fact-' + cg._sha(row)[:16]
        if cid not in graph.objects:
            graph.add(cid, 'FACT', row=row)
        refs.append(cid)
    fields = dict(operation='reported_effect_pool', input_refs=refs,
                  depends_on=sorted(set(refs)), scale=result['scale'],
                  value={k: result.get(k) for k in cg.POOL_FIELDS},
                  precision=4, label=str(outcome.get('name')))
    cid = 'outcome-pool-' + cg._sha(fields)[:20]
    if cid not in graph.objects:
        graph.add(cid, 'TRANSFORMATION', **fields)
    return cid


def known_missing(outcome, graph=None):
    panel = outcome.get('known_missing_sensitivity') or {}
    if not panel:
        return ''
    section = Section(graph)
    rows = panel.get('rows') or []
    section.counts('Known-missing per-item debt states',
                   [str(r.get('missing_class') or 'UNCLASSIFIED') for r in rows])
    section.counts('Known-missing per-item value states',
                   [str(r.get('value_status') or 'UNCLASSIFIED') for r in rows])
    section.interpretation(
        'These rows describe sensitivity questions and do not replace the primary pool.',
        'Unresolved extraction or typing may change the result; a missing target value does not demonstrate no effect.')
    for row in rows:
        # Do not repeat the stale aggregate headline or turn NOT_IN_COMMITTED_SOURCE
        # into a claim that a publication contains no effect.
        key = row.get('trial_key') or row.get('name')
        fields = ('value_status', 'missing_class', 'why_eligible', 'verify_basis', 'source_ref')
        text = str(key) + ': ' + '; '.join(f'{k}: {row[k]}' for k in fields if row.get(k))
        section.judgement('known_missing_sensitivity.rows', row, text)
        if row.get('sensitivity') or row.get('effect') is not None or row.get('ai') is not None:
            section.judgement('known_missing_sensitivity.rows.sensitivity', row,
                              f'{key}: sensitivity recomputation is owed; no registered sensitivity estimate is asserted.')
    if panel.get('combined'):
        section.judgement('known_missing_sensitivity.combined', panel['combined'],
                          'Combined sensitivity recomputation is owed; no registered combined estimate is asserted.')
    return ("<div class='kms-panel' id='known-missing-sensitivity'><h3>Known eligible trials not in this pool, and what they would do</h3>"
            + section.html() + '</div>')


def outcome_summary(outcome, graph=None):
    section = Section(graph)
    cid = pool_object(outcome, section.graph)
    if cid is None:
        return None
    section.parts.append(cid)
    loo = (outcome.get('result') or {}).get('leave_one_out') or {}
    if loo.get('per_trial') and len(outcome.get('trials') or []) >= 3:
        section.add('TRANSFORMATION', operation='reported_effect_leave_one_out',
                    pool_ref=cid, depends_on=[cid], value=loo['per_trial'],
                    label='Leave-one-out (influence)')
    section.counts('Pooled per-item states', ['POOLED' for _ in outcome.get('trials') or []])
    mid, fields = cg.membership_object(outcome)
    if mid not in section.graph.objects:
        section.graph.add(mid, 'TRANSFORMATION', **fields)
    section.parts.append(mid)
    names = ', '.join(str(t.get('label') or t.get('id')) for t in outcome.get('trials') or [])
    section.judgement('outcomes.trials', [t.get('id') for t in outcome.get('trials') or []],
                      'Contributors to this pool: ' + names, rule='enumerate-pool-inputs')
    for field in ('estimand', 'population', 'timepoint', 'method'):
        if outcome.get(field):
            section.judgement('outcomes.' + field, outcome[field],
                              f'Declared {field}: {outcome[field]}')
    return '<h4>' + escape(str(outcome.get('name') or 'Outcome')) + '</h4>' + section.html()


def outcome_details(outcome, graph=None):
    section = Section(graph)
    compat = outcome.get('compat_key') or {}
    trials = outcome.get('trials') or []
    section.counts('Pooled effect-measure per-item states',
                   [str(t.get('scale') or 'UNASSESSED') for t in trials])
    section.counts('Pooled endpoint component per-item states',
                   [_text(sorted(t['components'])) if t.get('components') else 'UNASSESSED' for t in trials])
    section.counts('Pooled unification per-item states',
                   [str((t.get('unification') or {}).get('status') or 'UNASSESSED') for t in trials])
    for key, value in sorted(compat.items()):
        if key in {'effect_measure', 'matched', 'mismatches', 'endpoint_canonical',
                   'endpoint_canonical_status', 'dimension_matches', 'underlying_checked'}:
            # Stored blanket verdicts are not the evidence for a new aggregate.
            # The corresponding item states are rendered above and below.
            continue
        if key == 'randomised_contrast':
            section.judgement('outcomes.compat_key.randomised_contrast', value,
                              'Parser-confirmed contrast coverage requires per-item arm-contrast states; no count is inferred from this stored aggregate.')
            continue
        # These are compatibility decisions, not new empirical FACT assertions.
        section.judgement('outcomes.compat_key.' + key, value,
                          f'Compatibility {key}: {_text(value)}')
    for dimension, rows in sorted((outcome.get('compat_underlying') or {}).get('per_trial', {}).items()):
        section.counts('Compatibility ' + dimension + ' per-item states',
                       [_text(row.get('value')) for row in rows])
        for row in rows:
            section.judgement('outcomes.compat_underlying.' + dimension, row,
                              f"{dimension}; {row.get('trial_id')}: {_text(row.get('value'))}; recorded basis: {_text(row.get('span'))}")
    result = outcome.get('result') or {}
    for field in ('composite_heterogeneity', 'design_refusal'):
        if result.get(field):
            section.judgement('outcomes.result.' + field, result[field], _text(result[field]))
    if outcome.get('recovery_disclosure'):
        section.judgement('outcomes.recovery_disclosure', outcome['recovery_disclosure'], outcome['recovery_disclosure'])
    return '<h5>Compatibility key (pooling contract)</h5>' + section.html()


def harm_summary(outcome, graph=None):
    result = outcome.get('result') or {}
    if result.get('state') != 'HARMS_INCOMPLETE':
        return None
    section = Section(graph)
    rows = result.get('known_eligible_outcome_reports_unresolved') or []
    section.counts('Unresolved harm-report per-item states',
                   [str(r.get('state') or r.get('reason_code') or 'UNRESOLVED') for r in rows])
    section.judgement('outcomes.result.state', result['state'],
                      'HARMS_INCOMPLETE: this outcome has no asserted complete pooled result.',
                      rule='harms-incomplete-state')
    for row in rows:
        section.judgement('outcomes.result.known_eligible_outcome_reports_unresolved', row,
                          'Unresolved harm report: ' + _text(row))
    return '<h4>' + escape(str(outcome.get('name'))) + '</h4>' + section.html()


def provenance_trial(trial, outcome, graph=None):
    if not cg._fact_evidence(trial).get('document_sha256'):
        return None
    section = Section(graph)
    row = dict(trial, scale=trial.get('scale') or outcome.get('estimand'))
    cid = 'fact-' + cg._sha(row)[:16]
    if cid not in section.graph.objects:
        section.graph.add(cid, 'FACT', row=row)
    section.parts.append(cid)
    section.add('FACT', row=row, display='located-provenance')
    for field in ('design', 'analysis_set', 'censoring', 'timepoint', 'derivation',
                  'selection_rule', 'alternatives', 'source_hierarchy_limitations',
                  'target_endpoint_class', 'target_endpoint_alternatives',
                  'registered_primary_selection_rule', 'cross_source',
                  'consumer_consistency_state', 'source_warning',
                  'endpoint_definition', 'follow_up_window', 'components'):
        if trial.get(field):
            section.judgement('outcomes.trials.' + field, trial[field],
                              f'{field}: {_text(trial[field])}')
    return '<tr><td colspan="4">' + section.html() + '</td></tr>'


def overview(review, neutral=False, graph=None):
    primary = cg.primary_outcome(review) or {}
    section = Section(graph)
    if pool_object(primary, section.graph) is None:
        return None
    # A research question is furniture, rendered as a heading by a semantic rule.
    head = '<h2>' + escape(str(review.get('title') or 'Overview')) + '</h2>'
    head += '<h3>' + escape(str(review.get('question') or 'Research question')) + '</h3>'
    inv = review.get('invalidation') or {}
    if inv.get('stale'):
        section.judgement('invalidation', inv,
                          'STALE — this topic\'s result is not current.', rule='invalidation-stale-flag')
        section.counts('Invalidation per-item reason states',
                       [str(r.get('code') or 'UNCLASSIFIED') for r in inv.get('reasons') or []])
    for field in ('identifier_scope', 'scope_identity'):
        record = review.get(field) or {}
        if record:
            if field == 'scope_identity':
                text = '; '.join(f"{k}: {record.get(k, {}).get('type', 'UNCLASSIFIED')}"
                                 for k in ('eligibility_scope', 'search_scope'))
            else:
                text = '; '.join(f'{k}: {record[k]}' for k in ('verdict', 'state', 'detail', 'qualification', 'note') if record.get(k))
            section.judgement(field, record, field + ': ' + text)
    retrieval = (review.get('search') or {}).get('retrieval_class') or {}
    if retrieval:
        section.judgement('search.retrieval_class', retrieval,
                          'Retrieval classification: ' + str(retrieval.get('class') or 'UNCLASSIFIED'))
    scope = review.get('scope_identity') or {}
    if scope_identity.requires_qualification(scope):
        included = [row for row in (review.get('screening') or {}).get('records') or []
                    if row.get('decision') == 'include']
        section.add('TRANSFORMATION', operation='count', inputs=included, value=len(included),
                    label='Screened-in records of the pre-identified set met eligibility; '
                          + scope_identity.QUALIFIED_SCOPE_PHRASE + '. Screened-in record count')
    contrasts = (review.get('arm_contrast') or {}).get('trials') or {}
    if contrasts:
        section.counts('Pooled parser-contrast per-item states',
                       [str((contrasts.get(cg.trial_key(t)) or {}).get('status') or 'UNASSESSED')
                        for t in primary.get('trials') or []])
    if not neutral:
        section.interpretation(
            'This page is intended to make the evidence auditable; auditability alone does not establish stronger evidence.',
            'A reader may prioritise independent source review and unresolved evidence debt over the available audit trail.')
        for row in review.get('limitations') or []:
            ack = row.get('unwired_acknowledged') if isinstance(row, dict) else None
            if ack:
                text = (f"Hazard acknowledgement {row.get('limitation_id')}: {row.get('kind')}; "
                        f"{row.get('evidence_state')}; severity {row.get('severity')}; "
                        f"{ack.get('reason')}; recorded signer {ack.get('signed_by')}; "
                        f"recorded date {ack.get('date')}; tranche {ack.get('tranche')}.")
                section.judgement('limitations.unwired_acknowledged', row, text)
        section.interpretation(
            'Open-access selection, incomplete retrieval, small pools and partially assessed bias can limit this review.',
            'The importance of each limitation depends on the source-level evidence and the intended use of the estimate.')
    if review.get('grade'):
        if 'grade-certainty' not in section.graph.objects:
            section.graph.add('grade-certainty', 'TRANSFORMATION', **cg.certainty_object(review['grade']))
        section.parts.append('grade-certainty')
    return (head + section.html() + outcome_summary(primary, section.graph)
            + known_missing(primary, section.graph))


def register(review, graph):
    """Build exactly the same registry for independent scans and renderers."""
    graph._collect_page_objects = True
    try:
        overview(review, graph=graph)
        for outcome in review.get('outcomes') or []:
            outcome_summary(outcome, graph)
            outcome_details(outcome, graph)
            harm_summary(outcome, graph)
            known_missing(outcome, graph)
            for trial in outcome.get('trials') or []:
                provenance_trial(trial, outcome, graph)
    finally:
        graph._collect_page_objects = False
