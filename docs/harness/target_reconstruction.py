"""Offline, source-bound target reconstruction. Returns candidates, never admissions.

Contract: held_text is the decoded held record; source_span is a single bound
outcome sentence within it. config/spec are the unchanged topic specification.
Numeric fields supplied on a review row are deliberately not used as counts.
"""
from __future__ import annotations

import math
import re
from statistics import NormalDist

from . import dose_arms, population_rules, recovery_map, timepoint_identity
from .extract import composite_component_mismatch, extract_effect, declared_is_composite, _names_composite
from .measure_identity import Measure, measure_of, normalize

_NUM = r"(?:\d{1,3}(?:,\d{3})+|\d+)"
_PAIR = re.compile(
    rf"(?P<a>{_NUM})\s*(?:\(\s*\d+(?:[.·]\d+)?%\s*\)\s*)?"
    rf"(?:of\s+(?:the\s+)?|/)(?P<n>{_NUM})\s+(?:patients|participants)\b", re.I)
_KEYS = recovery_map.COUNT_KEYS


def _refuse(row, code, detail=''):
    return dict(status='REFUSAL', code=code, refused=str(row.get('id', 'unnamed row')),
                reason=detail or code, poolable=False)


def _norm(text):
    return ' '.join(text.replace('·', '.').split()).lower()


def bind_abstract(trial, record, spec, config):
    """Recover the exact sentence behind a served row, without trusting its numbers.

    Truncated review spans may locate a sentence, but only the held full sentence
    supplies numbers. Ambiguous matches stay unbound and fail closed.
    """
    text = record.get('abstract', '')
    served = _norm(trial.get('source', '') or trial.get('source_span', ''))
    sentences = [m.group(0).strip() for m in re.finditer(r'.+?(?:\.(?=\s|$)|$)', text, re.S)]
    matches = [s for s in sentences if len(s) >= 40 and _norm(s)[:100] in served]
    span = matches[0] if len(matches) == 1 else ''
    # Only an endpoint-specific population statement can supplement a result.
    pop = [s for s in sentences if population_rules.classify(s) != 'UNKNOWN'
           and re.search(r'\b(?:mortality|deaths?|died)\b', s, re.I)
           and re.search(r'\b(?:mortality|deaths?|died)\b', span, re.I)
           and timepoint_identity.compare(spec.get('timepoint'), s) == 'MATCH']
    return dict(trial, held_text=text, source_span=span,
                population_span=pop[0] if len(pop) == 1 else '',
                spec=spec, config=config, record=record)


def reconstruct(row, target_measure):
    """Woolf OR / Katz RR from two explicit, arm-labelled patient fractions.

    UNCHANGED means no conversion, not permission to pool. The new candidate is
    poolable=False until the existing endpoint/design/admission path accepts it.
    """
    target = normalize(target_measure)
    if str(row.get('derivation', '')).upper() == 'RELAYED':
        return _refuse(row, 'RELAYED_COUNTS_NOT_BOUND')
    try:
        recovery_map.require_poolable(row)
    except ValueError as exc:
        return _refuse(row, 'RELAYED_COUNTS_NOT_BOUND', str(exc))
    if target == Measure.UNKNOWN:
        return _refuse(row, 'TARGET_MEASURE_UNKNOWN', str(target_measure))
    if row.get('effect') is not None and measure_of(row, row.get('source_span', '')) == target:
        return dict(status='UNCHANGED', row=row, poolable=False)
    if target == Measure.HAZARD_RATIO:
        return _refuse(row, 'HAZARD_RATIO_NOT_RECONSTRUCTIBLE_FROM_COUNTS')
    if target not in (Measure.ODDS_RATIO, Measure.RISK_RATIO):
        return _refuse(row, 'TARGET_MEASURE_UNSUPPORTED', target.value)
    text, span = row.get('held_text', ''), row.get('source_span', '')
    if not span or not text or span not in text:
        return _refuse(row, 'COUNTS_NOT_HELD', 'No unique verbatim outcome span in held bytes')
    spec, config = row.get('spec', {}), row.get('config', {})
    if normalize(spec.get('estimand')) != target:
        return _refuse(row, 'PROTOCOL_TARGET_CONFLICT')
    if (composite_component_mismatch(spec.get('name', ''), span)
            or (not declared_is_composite(spec.get('name', '')) and _names_composite(span))):
        return _refuse(row, 'ENDPOINT_MISMATCH')
    unit = timepoint_identity.count_unit(span)
    # Mortality fractions count unique patients even without "patients who".
    if (unit == 'UNKNOWN' and _PAIR.search(span) and re.search(r'\bdied\b', span, re.I)
            and not re.search(r'\b(?:events|episodes)\b', span, re.I)):
        unit = 'PATIENTS'
    if unit != 'PATIENTS':
        return _refuse(row, 'EVENT_COUNTS_NOT_PATIENTS' if unit == 'EVENTS' else 'COUNT_UNIT_UNKNOWN')
    if timepoint_identity.compare(spec.get('timepoint'), span) != 'MATCH':
        return _refuse(row, 'TIMEPOINT_MISMATCH_OR_MISSING')
    popspan = row.get('population_span', '')
    if popspan and popspan not in text:
        return _refuse(row, 'POPULATION_SPAN_NOT_HELD')
    rule = population_rules.rule_for(spec, config)
    # An explicit result population always takes precedence over methods context.
    popsource = span if population_rules.classify(span) != 'UNKNOWN' else popspan
    allowed = population_rules.admissibility({'source': popsource}, rule)
    if not allowed['allowed']:
        return _refuse(row, allowed['code'])
    try:
        dose_arms.require_poolable(row.get('record', {'abstract': text}), row,
                                   spec.get('name', ''), span)
    except ValueError as exc:
        return _refuse(row, 'ARM_OR_ENDPOINT_UNRESOLVED', str(exc))
    pairs = list(_PAIR.finditer(span))
    if len(pairs) != 2:
        return _refuse(row, 'COUNTS_NOT_HELD', 'Requires exactly two explicit patient fractions')
    arms = {}
    for i, pair in enumerate(pairs):
        label = span[pair.end():pairs[i+1].start() if i == 0 else len(span)]
        hits = [arm for arm, terms in [('i', config.get('intervention_terms', [])),
                                      ('c', config.get('comparator_terms', []))]
                if any(re.search(r'(?<!\w)' + re.escape(t) + r'(?!\w)', label, re.I) for t in terms)]
        if len(hits) != 1 or hits[0] in arms:
            return _refuse(row, 'ARM_IDENTITY_UNRESOLVED')
        arms[hits[0]] = pair
    if set(arms) != {'i', 'c'}:
        return _refuse(row, 'ARM_IDENTITY_UNRESOLVED')
    inputs = {}
    for key, arm, group in [('ai', 'i', 'a'), ('n1i', 'i', 'n'), ('ci', 'c', 'a'), ('n2i', 'c', 'n')]:
        m = arms[arm]
        inputs[key] = dict(value=int(m[group].replace(',', '')), span=m[group],
                           start=text.index(span) + m.start(group),
                           end=text.index(span) + m.end(group))
    a, n, c, m = (inputs[k]['value'] for k in _KEYS)
    if not (n > 0 and m > 0 and 0 <= a <= n and 0 <= c <= m):
        return _refuse(row, 'INVALID_COUNTS')
    b, d = n-a, m-c
    correction = 0.5 if min(a, b, c, d) == 0 else 0.0
    a, b, c, d = (v + correction for v in (a, b, c, d))
    if target == Measure.ODDS_RATIO:
        value, variance = a*d/(b*c), 1/a + 1/b + 1/c + 1/d
        method = 'Woolf log-OR'
    else:
        value = (a/(a+b))/(c/(c+d))
        variance = 1/a - 1/(a+b) + 1/c - 1/(c+d)
        method = 'Katz log-RR'
    delta = NormalDist().inv_cdf(0.975) * math.sqrt(variance)
    published = None
    effect = extract_effect(span.replace('·', '.'))
    published_measure = measure_of({'effect': effect[1], 'source_span': span}) if effect else Measure.UNKNOWN
    if effect and published_measure != Measure.UNKNOWN:
        published = dict(measure=published_measure.value, value=effect[1], ci_low=effect[2],
                         ci_high=effect[3], derivation='PUBLISHED', source_span=span, poolable=False)
    return dict(status='RECONSTRUCTED', measure=target.value, value=value,
                ci_low=math.exp(math.log(value)-delta), ci_high=math.exp(math.log(value)+delta),
                derivation='RECONSTRUCTED_FROM_COUNTS', inputs=inputs, method=method,
                correction=correction, source_span=span, population_span=popsource,
                published_candidate=published, poolable=False, admission='REQUIRED')



def allocated_mortality_counts(record, spec, intervention, comparator):
    """Bind printed mortality numerators to uniquely printed allocated arms.

    Handles an allocation sentence followed by the result sentence. Percentages
    are never inverted to manufacture counts. Ambiguous arm matches abstain.
    This is a candidate only; the pipeline still applies its admission gates.
    """
    if normalize(spec.get('estimand')) not in (Measure.RISK_RATIO, Measure.ODDS_RATIO):
        return None
    if not re.search(r'\b(?:mortality|death)\b', spec.get('name', ''), re.I):
        return None
    text = record.get('abstract') or ''
    allocations = list(re.finditer(
        rf'(?P<n1>{_NUM}) patients were assigned to receive (?P<arm1>[^.;]+?) and '
        rf'(?P<n2>{_NUM}) to receive (?P<arm2>[^.;]+)[.]', text, re.I))
    results = list(re.finditer(
        rf'(?P<a>{_NUM}) patients\s*\([\d.]+%\) in the (?P<arm1>[^.;]+?) group and '
        rf'(?P<c>{_NUM}) patients\s*\([\d.]+%\) in the (?P<arm2>[^.;]+?) group '
        r'died within \d+ days after randomization', text, re.I))
    def arm(label):
        hits = [key for key, terms in [('i', intervention), ('c', comparator)]
                if any(re.search(r'(?<!\w)'+re.escape(t)+r'(?!\w)',label,re.I) for t in terms)]
        return hits[0] if len(hits)==1 else None
    if len(allocations)!=1 or len(results)!=1:
        return None
    allocation, result = allocations[0], results[0]
    if allocation.end()>result.start() or timepoint_identity.compare(spec.get('timepoint'),result.group())!='MATCH':
        return None
    if (arm(allocation['arm1']),arm(allocation['arm2']),arm(result['arm1']),arm(result['arm2']))!=('i','c','i','c'):
        return None
    values = {k:int(m[g].replace(',','')) for k,m,g in
              [('ai',result,'a'),('ci',result,'c'),('n1i',allocation,'n1'),('n2i',allocation,'n2')]}
    if not (0<=values['ai']<=values['n1i'] and 0<=values['ci']<=values['n2i'] and min(values['n1i'],values['n2i'])>0):
        return None
    span=text[allocation.start():result.end()]
    return dict(values, source=span, source_span=span, provenance='abstract',
                derivation='reconstructed', count_binding='PRINTED_ALLOCATED_ARMS_AND_MORTALITY',
                count_witnesses={k:dict(value=values[k],span=m[g],start=m.start(g),end=m.end(g))
                                for k,m,g in [('ai',result,'a'),('ci',result,'c'),('n1i',allocation,'n1'),('n2i',allocation,'n2')]})
