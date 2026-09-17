"""Typed RoB/GRADE renderer. Aggregates use per-item states, not cached totals."""
from __future__ import annotations

import json

from . import claimgraph, funding, rob_sensitivity
from .section_prose import Writer, register_pool

DOMAINS = (
    ('D1_randomisation', 'Randomisation'),
    ('D2_deviations', 'Deviations/blinding'),
    ('D3_missing_outcome_data', 'Missing outcome data'),
    ('D4_outcome_measurement', 'Outcome measurement'),
    ('D5_selective_reporting', 'Selective reporting'),
)


def _rows(review):
    primary = next((o for o in review.get('outcomes') or [] if o.get('primary')), {})
    assessed = (review.get('rob2') or {}).get('trials') or {}
    return [(trial, assessed.get(claimgraph.trial_key(trial)) or
             rob_sensitivity._rob_entry(assessed, trial)) for trial in primary.get('trials') or []]


def _states(rows):
    return [rob_sensitivity._norm(entry.get('overall')) or 'not assessed' for _, entry in rows]


def compute(unit, inputs):
    if unit == 'overall-states':
        states = [row['state'] for row in inputs]
        counts = {s: states.count(s) for s in sorted(set(states))}
        rated = sum(s != 'not assessed' for s in states)
        return (f'Coverage: {rated} of {len(states)} primary-outcome pooled trials have a recorded '
                f'overall rating on assessed domains. Per-item overall states: {counts}.')
    if unit == 'd3-states':
        states = [str(row.get('level') or 'not assessed') for row in inputs]
        unassessed = sum(s.lower() in ('not assessed', 'unassessed', 'not_assessed') for s in states)
        return (f'D3 (missing outcome data): NOT ASSESSED for {unassessed} of {len(states)} '
                'primary-outcome pooled trials. Study discontinuation is not outcome missingness.')
    if unit == 'identity':
        return str(inputs.get('id') or inputs.get('label') or 'identity not recorded')
    if unit == 'sensitivity-state':
        states = [row['state'] for row in inputs]
        low = states.count('low')
        adverse = sum(s not in ('low', 'not assessed') for s in states)
        missing = states.count('not assessed')
        kind = rob_sensitivity._low_only_kind_from_counts(adverse, missing)
        if not states:
            relation = 'The low-risk-only relation is not assessable.'
        elif low == len(states):
            relation = 'All pooled trials are low risk on assessed domains; the re-pool is the full pool.'
        elif not low:
            relation = 'NOT ESTIMABLE: no pooled trial qualifies as low risk on assessed domains.'
        else:
            relation = 'The low-only stratum contains fewer trials than the full pool.'
        return (f'{relation} Low-only kind: {kind} ({adverse} adverse rating exclusions, '
                f'{missing} unassessed-domain exclusions); {low} of {len(states)} rows retained.')
    if unit == 'grade-assessments':
        names = claimgraph.GRADE_DOMAINS
        missing = [n.replace('_', ' ') for n in names if (inputs.get(n) or {}).get('assessed') is not True]
        return ('Unassessed domains: ' + (', '.join(missing) or 'none')
                + '. Unassessed never counts as favourable; certainty remains provisional when a required domain is unassessed.')
    if unit == 'funding-summary':
        known = sum(funding.funding_known(row) for row in inputs)
        industry = sum(funding.industry_tied(row) for row in inputs)
        return (f'Recorded funding entries: {industry} of {known} known '
                f'({len(inputs) - known} unknown) are classified as industry-funded or industry-tied. '
                'Unknown funding is not counted as independently funded.')
    if unit == 'contrast-summary':
        states = [row.get('status') or 'unclassified' for row in inputs]
        counts = {s: states.count(s) for s in sorted(set(states))}
        return f'Recorded arm-parser per-item states: {counts}. This measures the parser, not the trial.'
    if unit == 'design-summary':
        states = [row.get('design') or 'unclassified' for row in inputs]
        counts = {s: states.count(s) for s in sorted(set(states))}
        return f'Recorded unit-of-analysis per-item designs: {counts}.'
    raise ValueError('unknown risk computation: ' + unit)


def register(graph, review):
    w = Writer(graph, 'risk')
    parts = []

    def p(value):
        parts.append('<p>' + value + '</p>')

    rows = _rows(review)
    states = [{'id': claimgraph.trial_key(t), 'state': state}
              for (t, _), state in zip(rows, _states(rows))]
    p(w.computation('overall-states', states))
    p(w.computation('d3-states', [dict((entry.get('domains') or {}).get('D3_missing_outcome_data') or {},
                                     id=claimgraph.trial_key(t)) for t, entry in rows]))
    p(w.interpretation('partial-assessment',
        'Registry-machine-signal-restricted partial machine assessment is not a formal human risk-of-bias assessment.',
        'A human assessment using the complete held report may change the recorded domain judgements.'))
    parts.append('<table class="recs"><tr><th>Trial</th><th>Overall</th>'
                 + ''.join('<th>' + label + '</th>' for _, label in DOMAINS) + '</tr>')
    for index, (trial, entry) in enumerate(rows):
        key = claimgraph.trial_key(trial)
        token = claimgraph._sha({'key': key, 'row': index})[:12]
        ident = w.computation('identity-' + token, trial, unit='identity')
        overall = w.judgement('overall-' + token,
            'Recorded overall rating on assessed domains: ' + str(entry.get('overall') or 'not assessed'),
            {'rule_id': 'recorded-partial-rob-overall', 'source_field': 'rob2.trials.' + key,
             'domains': entry.get('domains') or {}}, owed=not bool(entry))
        cells = []
        for domain, label in DOMAINS:
            recorded = (entry.get('domains') or {}).get(domain) or {}
            level = recorded.get('level') or 'not assessed'
            basis = recorded.get('basis')
            text = label + ': ' + str(level) + '. Recorded basis: ' + str(basis or 'not supplied')
            cells.append('<td>' + w.judgement(token + '-' + domain, text,
                {'rule_id': recorded.get('rule_id') or 'recorded-domain-needs-adjudication',
                 'source_field': 'rob2.trials.' + key + '.domains.' + domain,
                 'recorded_basis': basis, 'inputs': recorded.get('inputs')},
                owed=not bool(recorded.get('rule_id') and basis) or level == 'not assessed') + '</td>')
        parts.append('<tr><td>' + ident + '</td><td>' + overall + '</td>' + ''.join(cells) + '</tr>')
    parts.append('</table><h4>Risk-of-bias sensitivity</h4>')
    p(w.computation('sensitivity-state', states))
    primary = next((o for o in review.get('outcomes') or [] if o.get('primary')), {})
    result = primary.get('result') or {}
    if rows and not any(result.get(k) for k in ('pool_refused', 'suppressed_incompatible', 'pooled_ci_refused')):
        scale = result.get('scale') or primary.get('estimand')
        strata = [('full', 'Full pool (all pooled trials)', [t for t, _ in rows]),
                  ('drop-high', 'Excluding high risk of bias', [t for (t, _), s in zip(rows, _states(rows)) if s != 'high']),
                  ('low-only', 'Low risk of bias only', [t for (t, _), s in zip(rows, _states(rows)) if s == 'low'])]
        parts.append('<table class="arms"><tr><th>Stratum</th><th>Re-pooled estimate</th></tr>')
        for name, label, trials in strata:
            if trials:
                value = register_pool(graph, 'risk-pool-' + name, trials, scale, label)
            else:
                value = w.judgement('empty-' + name, 'NOT ESTIMABLE: the stratum contains no trial rows.',
                                     {'rule_id': 'empty-stratum-no-pool', 'states': states}, owed=True)
            parts.append('<tr><th scope="row">' + label + '</th><td>' + value + '</td></tr>')
        parts.append('</table>')
    elif result.get('pool_refused') or result.get('suppressed_incompatible') or result.get('pooled_ci_refused'):
        p(w.judgement('sensitivity-refused', 'No RoB-stratified pooled interval is served for the refused primary pool.',
                      {'rule_id': 'respect-primary-pool-refusal', 'recorded_result': result}, owed=True))
    p(w.interpretation('sensitivity-reading',
        'A low-only comparison can reflect both recorded bias judgements and assessment availability.',
        'An unchanged trial set gives an identical re-pool and provides no additional sensitivity contrast.'))
    g = review.get('grade') or {}
    if g:
        parts.append('<h4>GRADE certainty</h4>')
        if g.get('certainty') == 'not_rateable':
            p(w.judgement('grade-refusal', 'Overall certainty: not rateable. Recorded reason: '
                          + str(g.get('not_rateable_reason') or 'not supplied'),
                          {'rule_id': 'respect-not-rateable-effect-object', 'source_field': 'grade'}, owed=True))
        else:
            p(w.ref('grade-certainty'))
            p(w.ref('grade-downgrades'))
        p(w.computation('grade-assessments', g.get('domains') or {}))
        for domain in claimgraph.GRADE_DOMAINS:
            recorded = (g.get('domains') or {}).get(domain) or {}
            if domain == 'risk_of_bias':
                p(w.judgement('grade-domain-' + domain,
                    'Recorded risk-of-bias downgrade: ' + str(recorded.get('downgrade', 0)) + '. '
                    + compute('overall-states', states),
                    {'rule_id': 'recorded-grade-judgement-with-live-item-counts',
                     'recorded_domain': recorded, 'per_item_states': states},
                    owed=recorded.get('assessed') is not True))
            elif domain == 'publication_bias' and recorded.get('assessed') is not True:
                p(w.judgement('grade-domain-' + domain,
                    'Publication bias: NOT ASSESSED; a PICO-scoped item-level census is owed. '
                    'A broad registry summary does not establish this review population\'s publication-bias rate.',
                    {'rule_id': 'aggregate-requires-pico-scoped-items', 'source_field': 'grade.domains.publication_bias',
                     'recorded_domain': recorded}, owed=True))
            else:
                p(w.ref('grade-domain-' + domain))
    if review.get('rob_spancheck'):
        p(w.judgement('spancheck-debt',
            'The recorded cross-family RoB span-check summary lacks per-item verdicts in this review object. '
            'An agreement percentage is not recomputed or asserted here; item-level audit evidence is owed.',
            {'rule_id': 'aggregate-requires-per-item-states', 'source_field': 'rob_spancheck',
             'recorded_summary': review['rob_spancheck']}, owed=True))
    fund = review.get('funding') or []
    if fund:
        parts.append('<h4>Funding / conflict-of-interest disclosure</h4>')
        p(w.computation('funding-summary', fund))
        for i, row in enumerate(fund):
            text = (str(row.get('id')) + ': recorded funding classification ' +
                    str(row.get('sponsor_class') or row.get('type') or 'unknown') +
                    '; status ' + str(row.get('status') or 'not supplied') +
                    '; sponsors ' + ', '.join(row.get('sponsors') or []) +
                    '; source evidence ' + json.dumps(row.get('sources') or [{
                        k: row.get(k) for k in ('source_id', 'source', 'basis_span', 'span', 'role')}],
                        ensure_ascii=False, sort_keys=True))
            p(w.judgement('funding-' + str(i), text,
                {'rule_id': 'harness.funding:recorded-classification', 'source_field': f'funding.{i}',
                 'recorded_inputs': row}, owed=not funding.funding_known(row)))
        p(w.interpretation('funding-reading',
            'Funding is disclosed without a numerical bias adjustment; author affiliations alone are not sponsor evidence.',
            'Source-specific funding roles may be more informative than a single industry/public classification.'))
    contrasts = (review.get('arm_contrast') or {}).get('trials') or {}
    if contrasts:
        parts.append('<h4>Arm-contrast disclosure</h4>')
        p(w.computation('contrast-summary', list(contrasts.values())))
        for key, row in sorted(contrasts.items()):
            p(w.judgement('contrast-' + claimgraph._sha(key)[:12],
                key + ': recorded parser state ' + str(row.get('status') or 'unclassified') +
                '. Recorded basis: ' + str(row.get('basis') or 'not supplied') +
                '. Differing arm labels: ' + '; '.join(row.get('differing') or []),
                {'rule_id': 'recorded-arm-parser-result', 'source_field': 'arm_contrast.trials.' + key,
                 'recorded_inputs': row}, owed=row.get('status') != 'verified'))
    uoa = review.get('unit_of_analysis') or []
    if uoa:
        parts.append('<h4>Unit-of-analysis/design caveat</h4>')
        p(w.computation('design-summary', uoa))
        for i, row in enumerate(uoa):
            text = str(row.get('id')) + ': recorded design ' + str(row.get('design')) + '.'
            if (row.get('design') or '').lower() == 'factorial':
                text += (' For individual-randomized factorial designs, an acceptable source-reported adjusted marginal estimate '
                         'requires design-key disclosure and interaction evidence.')
            p(w.judgement('design-' + str(i), text,
                {'rule_id': 'recorded-design-requires-explicit-adjustment', 'recorded_inputs': row}, owed=True))
    return ''.join(parts)


@claimgraph._provenance_batch()
def render(review):
    local = claimgraph.review_graph(review, include_sections=False)
    document = register(local, review)
    return Writer(local, 'risk').finish(document)
