"""Conservative integration of held-source lane diagnostics before synthesis."""
from dataclasses import asdict
from pathlib import Path
import re
from . import measure_identity as mi, timepoint_identity as ti, population_rules as pop
from . import table_rows, recovery_map, dose_arms

BLOCKING = ('TARGET_MEASURE_UNAVAILABLE', 'UNRESOLVED_MEASURE_ATTRIBUTION', 'ORIGIN_SOURCE_UNREADABLE', 'TIMEPOINT_MISMATCH',
            'POPULATION_RULE_INCONSISTENT', 'UNIT_MIX_POOLED',
            'VARIANT_ROW_MISMATCH', 'SHARED_CONTROL_DOUBLE_COUNTED', 'KM_PERCENT_TO_COUNT')
SCALES = {'HAZARD_RATIO': 'HR', 'RISK_RATIO': 'RR', 'ODDS_RATIO': 'OR',
          'RATE_RATIO': 'IRR', 'MEAN_DIFFERENCE': 'MD'}


def problem(code, item, **detail):
    return dict(code=code, item=str(item), **detail)


def table_entry(entry, directory):
    """Bind an exact held row; parser limitations never throw through the build.

    A parser refusal is distinct from overturning a previously validated entry.
    Only a positively bound contradiction refuses that existing numeric route.
    """
    out = dict(entry)
    out.pop('table_row', None)
    try:
        recovery_map.require_poolable(out)
    except ValueError:
        out['relay_refusal'] = 'RELAYED_COUNTS_NOT_BOUND'
    if out.get('provenance') == 'RELAYED' or str(out.get('derivation', '')).upper() == 'RELAYED' or 'relayed_counts' in out:
        out['relay_refusal'] = 'RELAYED_COUNTS_NOT_BOUND'
    ref = str(out.get('document_ref') or '').split('#')[0]
    if not ref.endswith('.tables.txt'):
        return out
    root = Path(directory).parent.parent.resolve()
    paths = [(Path(directory) / ref).resolve(), (root / ref).resolve()]
    try:
        path = next((p for p in paths if p.is_relative_to(root) and p.is_file()), None)
        if path is None:
            raise ValueError('TABLE_SOURCE_NOT_HELD')
        norm = lambda s: ' '.join(table_rows._norm(s).split())
        span = norm(out.get('source_span') or '')
        matches = [(row, tab) for tab in table_rows.parse(path) for row in tab['rows']
                   if norm(' | '.join([row['label']] + row['cells'])) == span]
        if len(matches) != 1:
            raise ValueError('TABLE_ROW_UNBOUND')
        row, tab = matches[0]
        typed = table_rows.typed(row, tab)
        typed.update(row_label=row['label'], caption=tab['caption'], source_sha=tab['source_sha'])
        out['table_row'] = typed
        if out.get('effect') is not None:
            eff = typed.get('effect')
            if eff and any(out.get(k) != eff[v] for k, v in
                           [('effect', 'value'), ('ci_low', 'ci_low'), ('ci_high', 'ci_high')]):
                out['table_conflict'] = 'TABLE_VALUE_MISMATCH'
            if eff and typed['measure'] in SCALES and not out.get('table_conflict'):
                out['scale'] = SCALES[typed['measure']]
        out['table_binding'] = {'state': 'REFUSED' if typed['refusals'] else 'BOUND',
                                'reason': '; '.join(typed['refusals']) or 'exact held row'}
    except (ValueError, OSError, UnicodeError) as exc:
        out['table_binding'] = {'state': 'REFUSED', 'reason': str(exc), 'document_ref': ref}
    return out


def measure(row, spec):
    if row.get('effect') is None:
        if row.get('mean1') is not None:
            return mi.Measure.MEAN_DIFFERENCE
        if row.get('e1i') is not None:
            return mi.Measure.RATE_RATIO
        # This is an explicit supported numeric transformation, not borrowing a label.
        if mi._valid_counts(row) and str(row.get('reconstruction_measure') or spec.get('estimand', '')).upper() == 'OR':
            return mi.Measure.ODDS_RATIO
    table = row.get('table_row') or {}
    if row.get('effect') is not None and table.get('measure') in SCALES:
        return mi.normalize(table['measure'])
    return mi.measure_of(row)


def select_estimator(selected, candidates, declared_estimand, peers=()):
    from . import design_key, target_endpoint
    target = mi.normalize(declared_estimand)
    # Preserve the pre-existing source hierarchy unless its choice crosses odds.
    # In particular, a published HR must not become count-derived RR just because
    # the topic declares RR. Its actual measure is disclosed by prepare/finish.
    prior = design_key.select_estimator_by_source_hierarchy(
        selected, candidates, declared_estimand)
    prior_measure = measure(prior, {})
    risk_rate = (mi.Measure.RISK_RATIO, mi.Measure.HAZARD_RATIO, mi.Measure.RATE_RATIO)
    crosses_odds = (target == mi.Measure.ODDS_RATIO and prior_measure in risk_rate) or (
        prior_measure == mi.Measure.ODDS_RATIO and target in risk_rate)
    if not crosses_odds:
        return prior
    base_components = target_endpoint._components_from_text(mi.row_span(selected))
    def same_endpoint(candidate):
        components = target_endpoint._components_from_text(mi.row_span(candidate))
        return not (base_components or components) or components == base_components
    pool = [dict(selected)] + [dict(c) for c in candidates if c and same_endpoint(c)]
    published = [c for c in pool if c.get('effect') is not None
                 and measure(c, {}) == target and target != mi.Measure.UNKNOWN]
    counts = [c for c in pool if c.get('effect') is None and mi._valid_counts(c)
              and target in (mi.Measure.RISK_RATIO, mi.Measure.ODDS_RATIO)]
    other = [c for c in pool if c.get('effect') is None and measure(c, {}) == target
             and not mi._count_row(c) and target != mi.Measure.UNKNOWN]
    risk_rate = (mi.Measure.RISK_RATIO, mi.Measure.HAZARD_RATIO, mi.Measure.RATE_RATIO)
    fallback = [c for c in pool if c.get('effect') is not None
                and target in risk_rate and measure(c, {}) in risk_rate]
    if counts:
        # Retain the existing source ratio-label audit (e.g. mislabeled RRR).
        chosen = design_key.select_estimator_by_source_hierarchy(counts[0], published, declared_estimand)
        if not published and any(c.get('effect') is not None for c in pool):
            chosen['selection_rule'] = 'KEEP_RECONSTRUCTION_EFFECT_CLASS_MISMATCH'
    else:
        chosen = dict((published or other or fallback or pool)[0])
        chosen['selection_rule'] = 'TARGET_FIRST_PUBLISHED' if published else 'TARGET_FIRST_AVAILABLE'
    if chosen.get('effect') is None and mi._valid_counts(chosen) and counts:
        chosen['reconstruction_measure'] = SCALES[target.value]
    chosen.update({k: selected[k] for k in ('id', 'label') if k in selected})
    audited = chosen.get('alternatives', [])
    declared_class = design_key._declared_estimand_class(declared_estimand)
    chosen['alternatives'] = [dict(c, **design_key._candidate_summary(c, chosen, declared_class))
                              for c in pool if any(c.get(k) != chosen.get(k)
                              for k in ('effect', 'ci_low', 'ci_high', 'ai', 'n1i', 'ci', 'n2i', 'scale'))]
    for alternative in chosen['alternatives']:
        if (alternative.get('effect') is not None and measure(alternative, {}) != target
                and alternative.get('not_selected_reason') != 'NOT_TARGET_CLASS'):
            alternative['not_selected_reason'] = 'NOT_TARGET_MEASURE'
        audit = next((a.get('ratio_label_audit') for a in audited
                      if all(a.get(k) == alternative.get(k) for k in ('effect','ci_low','ci_high','scale'))
                      and a.get('ratio_label_audit')), None)
        if audit:
            alternative['ratio_label_audit'] = audit
    return chosen


def _origin(row, record):
    # Only the document that supplied the bound row can supply its baseline witness.
    span = row.get('source_span') or ti.row_span(row)
    ref = str(row.get('document_ref') or '').split('#')[0]
    abstract = record.get('abstract') or ''
    if span and span in abstract and (not ref or ref.endswith('records.json')):
        return ' '.join(ti.origin_spans(abstract))
    # An explicit full-text reference cannot borrow an abstract's time origin.
    root = Path(__file__).resolve().parents[1]
    path = (root / ref).resolve()
    if ref and not ref.endswith('.json') and path.is_relative_to(root) and path.is_file():
        try:
            text = path.read_text(encoding='utf-8')
            if span and ti.plain(span) in ti.plain(text):
                return ' '.join(ti.origin_spans(text))
        except (OSError, UnicodeError) as exc:
            raise ValueError('ORIGIN_SOURCE_UNREADABLE: ' + ref + ': ' + str(exc)) from exc
    return ''


def prepare(out, spec, config, records):
    problems = out.setdefault('lane_problems', [])
    rule = pop.rule_for(out, config)
    out['population_rule'] = asdict(rule)
    target = spec.get('timepoint')
    out['timepoint_target'] = target or 'MISSING'
    if not target:
        problems.append(problem('TARGET_TIMEPOINT_MISSING', out['name'], blocking=False))
    retained = []
    for row in out.get('trials', []) + out.get('declared_absent_trials', []):
        rid = str(row.get('id', ''))
        record = records.get(rid.replace('PMID ', ''), {})
        origin_error = ''
        try:
            origin = _origin(row, record)
        except ValueError as exc:
            origin, origin_error = '', str(exc)
        tp = ti.parse(row.get('timepoint_span') or ti.row_span(row), origin)
        if origin_error:
            row['origin_source_error'] = origin_error
        row['typed_timepoint'] = asdict(tp)
        row['population_class'] = pop.classify(row)
        row['population_decision'] = pop.admissibility(row, rule)
        dose = dose_arms.assess(record, None, out['name'], '')
        dose['problems'].extend(dose_arms.km_products(row, ti.row_span(row)))
        if dose['problems']:
            dose['status'] = 'REFUSED'
        if dose['arms'] or dose['problems']:
            row['dose_assessment'] = dose
        if row not in out.get('trials', []):
            continue
        codes = ['ORIGIN_SOURCE_UNREADABLE'] if origin_error else []
        # Recovery attachment happens after synthesis. Incoming relay annotations
        # are untrusted pool inputs, including forged ANALYSIS_READY wrappers.
        try:
            recovery_map.require_poolable(row)
        except ValueError:
            codes.append('RELAYED_COUNTS_NOT_BOUND')
        parsed_target = ti.parse(str(target or ''))
        from . import extract
        semantic_mismatch = extract.timepoint_mismatch(str(target or ''), ti.row_span(row))
        if semantic_mismatch and not origin_error:
            codes.append('TIMEPOINT_MISMATCH')
            row['timepoint_reason'] = semantic_mismatch
        if not origin_error and target and parsed_target.elapsed_days is not None and tp.elapsed_days is not None:
            if ti.compare(parsed_target, tp) == 'MISMATCH':
                codes.append('TIMEPOINT_MISMATCH')
        # The derived efficacy/safety policy is disclosed, not a protocol amendment.
        # Opposite population decisions within this outcome are enforced below.
        row['population_decision']['scope'] = 'DISCLOSURE; existing source admission retained unless inconsistent'
        if row.get('table_conflict'):
            codes.append(row['table_conflict'])
        flags = (row.get('table_row') or {}).get('variant_flags', [])
        if ('NON_CABG' in flags and re.search('major bleeding', out['name'], re.I)
                and not re.search(r'non[- ]cabg', out['name'], re.I)) or (
                'LEADING_TO_DISCONTINUATION' in flags and re.search(r'dyspn[oe]+a', out['name'], re.I)
                and not re.search('discontinuation', out['name'], re.I)):
            codes.append('VARIANT_ROW_MISMATCH')
        if (row.get('relay_refusal') or row.get('provenance') == 'RELAYED' or str(row.get('derivation', '')).upper() == 'RELAYED'
                or 'relayed_counts' in row):
            codes.append('RELAYED_COUNTS_NOT_BOUND')
        codes.extend(p['problem'] for p in dose['problems'])
        m = measure(row, spec)
        row['measure_identity'] = m.value
        target_measure = mi.normalize(spec.get('estimand'))
        if m == mi.Measure.UNKNOWN:
            codes.append('UNRESOLVED_MEASURE_ATTRIBUTION')
        elif (target_measure == mi.Measure.ODDS_RATIO and m in
              (mi.Measure.RISK_RATIO, mi.Measure.HAZARD_RATIO, mi.Measure.RATE_RATIO)) or (
              m == mi.Measure.ODDS_RATIO and target_measure in
              (mi.Measure.RISK_RATIO, mi.Measure.HAZARD_RATIO, mi.Measure.RATE_RATIO)):
            # Only the odds boundary is decided. Within risk/rate, preserve
            # admission and disclose the actual class below; never relabel it.
            codes.append('TARGET_MEASURE_UNAVAILABLE')
        if row.get('effect') is not None and m.value in SCALES:
            row['scale'] = SCALES[m.value]
        if codes:
            row['lane_refusals'] = sorted(set(codes))
            row.update(reason_code=codes[0], reason='; '.join(sorted(set(codes))),
                       absent_kind='refused_on_evidence', state='REFUSED_ON_EVIDENCE')
            problems.extend(problem(c, rid, blocking=True) for c in sorted(set(codes)))
        else:
            retained.append(row)
    old = out['trials']
    out['declared_absent_trials'].extend(r for r in old if r not in retained)
    old[:] = retained
    pool_codes = []
    measures = {measure(r, spec) for r in retained} - {mi.Measure.UNKNOWN}
    if len(measures) > 1:
        classes = sorted(m.value for m in measures)
        out['measure_mix'] = dict(classes=classes, inputs_by_class={
            cls: [str(r.get('id') or r.get('label') or i)
                  for i, r in enumerate(retained) if measure(r, spec).value == cls]
            for cls in classes})
        problems.append(problem('MEASURE_MIX_POOLED', out['name'], blocking=False,
                                severity='ADVISORY', **out['measure_mix']))
    inconsistency = pop.consistency({'outcomes': [out]}, config)
    if inconsistency:
        pool_codes.append('POPULATION_RULE_INCONSISTENT')
    counts = [r for r in retained if r.get('ai') is not None and r.get('effect') is None]
    if any(p['code'] == 'UNIT_MIX_POOLED' for p in ti.pool_problems(counts)):
        pool_codes.append('UNIT_MIX_POOLED')
    controls = [dict(r, outcome=out['name']) for r in retained
                if all(r.get(k) for k in ('trial_id', 'control_id'))]
    if controls:
        pool_codes.extend(p['problem'] for p in dose_arms.control_problems(controls))
    if pool_codes:
        for row in retained:
            row['lane_refusals'] = sorted(set(pool_codes))
            row.update(reason_code=pool_codes[0], reason='; '.join(sorted(set(pool_codes))),
                       absent_kind='refused_on_evidence', state='REFUSED_ON_EVIDENCE')
        out['declared_absent_trials'].extend(retained)
        old[:] = []
        problems.extend(problem(c, out['name'], blocking=True) for c in sorted(set(pool_codes)))
    return bool(pool_codes)


def finish(out, spec):
    fields = mi.outcome_identity(out, spec)
    measures = {measure(r, spec).value for r in out.get('trials', [])}
    if len(measures) == 1:
        fields['served_measure'] = next(iter(measures))
    out.update(fields)
    if fields['served_measure'] == 'UNKNOWN' and out.get('trials'):
        out['measure_inputs'] = {cls: [str(r.get('id') or r.get('label') or i)
                                      for i, r in enumerate(out['trials']) if measure(r, spec).value == cls]
                                 for cls in sorted(measures)}
    if not out.get('trials') and any(r.get('lane_refusals') for r in out.get('declared_absent_trials', [])):
        refusals = [dict(id=r.get('id'), codes=r['lane_refusals']) for r in out['declared_absent_trials'] if r.get('lane_refusals')]
        out['result'] = dict(present=False, state='LANE_REFUSED', refused=refusals,
                             reason='Named lane refusals: ' + '; '.join(str(r) for r in refusals))
    result = out.get('result')
    if isinstance(result, dict):
        if out.get('measure_inputs'):
            result['measure_inputs'] = out['measure_inputs']
        if out.get('measure_mix'):
            result['measure_mix'] = out['measure_mix']
        result.update(fields, timepoint_target=out.get('timepoint_target', spec.get('timepoint') or 'MISSING'))
        if fields['target_measure'] != fields['served_measure']:
            result['measure_disclosure'] = fields.copy()
    return out


def attach_recovery(review, slug):
    recovery_map.attach(review, slug)
    from . import recovery_binding
    recovery_binding.attach(review, slug)
    for out in review.get('outcomes', []):
        for row in out.get('declared_absent_trials', []):
            if row.get('recovery_map'):
                row['reason'] = row['recovery_map']['reason']
