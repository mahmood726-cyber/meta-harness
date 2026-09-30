"""Partial WHO REACT binding; relayed counts never become synthesis input."""
from __future__ import annotations
import re
from copy import deepcopy
from typing import Literal, TypedDict
from . import recovery_map


class Binding(TypedDict):
    trial: str
    nct: str | None
    numerator: Literal['BOUND', 'RELAYED']
    denominator: Literal['BOUND', 'RELAYED', 'CONFLICT']
    bound_values: dict
    conflict_detail: list


def acronym(value):
    return re.sub(r'[^A-Z0-9]', '', (value or '').upper())


def bind(topic_block, excerpt_rows):
    """Accept parse()'s evidence bundle, with optional selected_outcome on block.

    NCT is authoritative when present; a failed NCT join never falls back to name.
    No mutation of entries, review, pools, or the recovery map.
    """
    results = []
    outcome = topic_block.get('selected_outcome', {'name': '28-day mortality'})
    if isinstance(outcome, str):
        outcome = {'name': outcome}
    mortality = bool(re.search(r'28[- ]day.*mortality|mortality.*28', outcome.get('name', ''), re.I))
    for entry in topic_block['entries']:
        result = dict(recovery_map.classify(entry, topic_block['population'], outcome, ''),
                      trial=entry['trial'], nct=entry.get('nct'), numerator='RELAYED', denominator='RELAYED',
                      bound_values={}, conflict_detail=[], binding='NONE',
                      source_population=excerpt_rows['population'])
        candidates = [r for r in excerpt_rows['rows'] if
                      (r['nct'] == entry['nct'] if entry.get('nct') else
                       len(acronym(entry['trial'])) >= 3 and acronym(r['trial']) == acronym(entry['trial']))]
        refusal = None
        if not mortality:
            refusal = 'SELECTED_OUTCOME_POPULATION_NOT_HELD'
        elif outcome.get('population') and outcome['population'] != topic_block['population']:
            refusal = 'SELECTED_POPULATION_MISMATCH'
        elif len(candidates) != 1:
            refusal = 'AMBIGUOUS_TRIAL_IDENTITY' if candidates else 'TRIAL_NOT_HELD'
        elif len(candidates[0]['intervention']) != 1 or len(candidates[0]['comparator']) != 1:
            refusal = 'AMBIGUOUS_TABLE1_ARMS'
        elif candidates[0]['group'] != 'Tocilizumab':
            refusal = 'TRIAL_EXCLUDED_FROM_META_ANALYSIS'
        if refusal:
            result['reason'] = refusal + ': ' + entry['trial']
            results.append(result)
            continue
        row = candidates[0]
        result['nct'] = row['nct']
        for key, arm in [('n1i', row['intervention'][0]), ('n2i', row['comparator'][0])]:
            if arm['n'] != entry[key]:
                result['conflict_detail'].append({'field': key, 'relayed': entry[key], 'held': arm['n'], 'span': arm['span']})
        if result['conflict_detail']:
            result.update(denominator='CONFLICT', state='POPULATION_UNRESOLVED',
                          reason='DENOMINATOR_CONFLICT: ' + entry['trial'])
        else:
            result.update(denominator='BOUND', state='COUNTS_RECOVERED', binding='PARTIAL')
            result['bound_values'] = {key: {'value': arm['n'], 'span': arm['span']} for key, arm in
                                      [('n1i', row['intervention'][0]), ('n2i', row['comparator'][0])]}
        deaths = [d for d in excerpt_rows.get('deaths', []) if d['nct'] == row['nct'] and acronym(d['trial']) == acronym(row['trial'])]
        if len(deaths) == 1 and all(deaths[0][k] == entry[k] for k in ('ai', 'ci')):
            result['numerator'] = 'BOUND'
            result['bound_values'].update({k: {'value': deaths[0][k], 'span': deaths[0]['span']} for k in ('ai', 'ci')})
            if result['denominator'] == 'BOUND':
                result['binding'] = 'COUNTS_BOUND_NOT_ADMITTED'
        elif deaths:
            result['reason'] += '; NUMERATOR_CONFLICT_OR_AMBIGUITY: ' + entry['trial']
        # Retain quarantine even if a future text source supplies all counts:
        # independent endpoint/population admission remains the integrator's job.
        results.append(result)
    return results


def require_poolable(row):
    recovery_map.require_poolable(row)
    raise ValueError('RECOVERY_BINDING_NOT_ADMITTED: ' + row.get('trial', 'unknown trial'))


def attach(review, slug, *, root=recovery_map.ROOT):
    """Decorate existing mapped rows after synthesis; no inputs are constructed.

    Registry NCT joins precede exact normalized trial names. The committed
    excerpt can bind denominators only; relayed numerators remain quarantined.
    """
    if slug != 'tocilizumab-covid19-mortality':
        return []
    from . import recovery_excerpt, trial_family
    block = deepcopy(recovery_map.load_map(root).get(slug))
    if not block:
        return []
    registry = trial_family.load_registry(root, slug)
    for entry in block['entries']:
        ids = [n for n, rec in registry.items() if any(
            acronym(s.get('acronym')) == acronym(entry['trial'])
            for s in rec.get('raw', {}).get('studies', []))]
        if len(ids) == 1:
            entry['nct'] = ids[0]
        elif ids:
            raise ValueError('AMBIGUOUS_RECOVERY_REGISTRY_IDENTITY: ' + entry['trial'])
    evidence = recovery_excerpt.load(root)
    ledger = []
    for outcome in review.get('outcomes', []):
        if not re.search(r'28[- ]day.*mortality|mortality.*28', outcome.get('name', ''), re.I):
            continue
        # Recovery describes the source's outcome-recorded subset. It does not
        # assert equivalence to the protocol's ITT population or admit a pool.
        block['selected_outcome'] = {'name': outcome['name']}
        bindings = bind(block, evidence)
        for row in outcome.get('trials', []) + outcome.get('declared_absent_trials', []):
            mapped = row.get('recovery_map')
            if not mapped:
                continue
            matches = [b for entry, b in zip(block['entries'], bindings) if
                       (entry.get('pmid') and str(row.get('id', '')) in
                        (entry['pmid'], 'PMID ' + entry['pmid'])) or
                       acronym(row.get('label')) == acronym(entry['trial'])]
            if len(matches) != 1:
                raise ValueError('RECOVERY_ROW_IDENTITY_UNRESOLVED: ' + str(row.get('id')))
            bound = deepcopy(matches[0])
            bound['evidence'] = deepcopy(evidence['evidence'])
            bound['target_population'] = outcome.get('population')
            bound['population_equivalence'] = 'NOT_ADJUDICATED'
            bound['reason'] += '; source-subset recovery only; target population equivalence NOT_ADJUDICATED'
            # Preserve the own-source form disclosure, without making its
            # percentage/ratio a source of the relayed integer numerator.
            bound['reported_other_form'] = mapped.get('reported_other_form', [])
            row['recovery_binding'] = bound
            row['recovery_map'] = deepcopy(bound)
            if row not in outcome.get('trials', []):
                row.update(state=bound['state'], reason_code=bound['state'], reason=bound['reason'],
                           result_status=dict(state=bound['state'], basis=bound['reason']))
            ledger.append(dict(id=row.get('id'), outcome=outcome['name'], **deepcopy(bound)))
    review['recovery_bindings'] = ledger
    # Keep the existing summary consistent with the typed row display.
    for old in review.get('recovery_map', []):
        matches = [b for b in ledger if b['trial'] == old['trial']]
        if len(matches) == 1:
            old.update(after=matches[0]['state'], recovery_state=matches[0]['state'])
    return ledger
