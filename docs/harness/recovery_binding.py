"""Partial WHO REACT binding; relayed counts never become synthesis input."""
from __future__ import annotations
import re
import json
from copy import deepcopy
from pathlib import Path
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


FIGURE_BINDING = 'docs/recovery_figure_binding.json'


def check_transcription_state(row):
    state = row.get('transcription_state')
    if state not in ('MODEL_TRANSCRIBED_CHECKED', 'CROSS_PROVIDER_VERIFIED'):
        raise ValueError('TRANSCRIPTION_STATE_REFUSED: missing/unknown checked state')
    provider = row.get('consensus_provider')
    if not isinstance(provider, str) or not provider.strip():
        raise ValueError('TRANSCRIPTION_STATE_REFUSED: missing consensus provider')
    witnesses = row.get('cross_provider_witnesses')
    if not isinstance(witnesses, list):
        raise ValueError('TRANSCRIPTION_STATE_REFUSED: missing witness audit')
    for witness in witnesses:
        if (not isinstance(witness.get('provider'), str) or not witness['provider'].strip()
                or witness['provider'].strip().casefold() == provider.strip().casefold()
                or not isinstance(witness.get('disagreeing_cells'), list)
                or not re.fullmatch(r'mc-[0-9a-f]{32}', witness.get('record_id', ''))):
            raise ValueError('TRANSCRIPTION_STATE_REFUSED: invalid cross-provider witness')
    verified = bool(witnesses) and all(not w['disagreeing_cells'] for w in witnesses)
    if (state == 'CROSS_PROVIDER_VERIFIED') != verified:
        raise ValueError('TRANSCRIPTION_STATE_REFUSED: state disagrees with witness audit')


def load_figure_binding(root, block, excerpt):
    """Validate the committed offline result, without reading its source records.

    Record replay/staleness is a separate offline test. These checks establish
    the artifact contract and its consistency with committed runtime inputs.
    """
    def refuse(reason):
        raise ValueError('FIGURE_BINDING_REFUSED: ' + reason)

    try:
        data = json.loads((Path(root) / FIGURE_BINDING).read_text(encoding='utf-8'))
        if data['schema'] != 'recovery_figure_binding/1' or data['topic'] != 'tocilizumab-covid19-mortality':
            refuse('schema/topic')
        ids = data['record_ids']
        if (not isinstance(ids, list) or len(ids) < 3 or len(set(ids)) < 3
                or any(not isinstance(i, str) or not re.fullmatch(r'mc-[0-9a-f]{32}', i) for i in ids)):
            refuse('record_ids: three distinct recorded readings required')
        models = data['model_ids']
        if not isinstance(models, list) or len(models) < 3 or len(set(models)) < 3 or not all(isinstance(m, str) and m for m in models):
            refuse('model_ids: three distinct readers required')
        if not re.fullmatch(r'[0-9a-f]{64}', data['figure_sha256']):
            refuse('figure_sha256')
        for value in [data, *data['entries']]:
            if (value['poolable'] is not False or value['population_equivalence'] != 'NOT_ADJUDICATED'
                    or value['population'] != 'outcomes recorded'):
                refuse('population/nonpoolability: ' + value.get('trial', 'artifact'))
        entries = data['entries']
        if (len(entries) != len(block['entries']) or
                sorted(e['trial'] for e in entries) != sorted(e['trial'] for e in block['entries'])):
            refuse('recovery trial inventory')
        for entry in entries:
            trial = entry['trial']
            if entry['record_ids'] != ids or entry['figure_sha256'] != data['figure_sha256']:
                refuse('record_ids/figure provenance: ' + trial)
            relay, = [e for e in block['entries'] if e['trial'] == trial]
            if entry['relayed'] != {k: relay[k] for k in recovery_map.COUNT_KEYS}:
                refuse('stale relayed counts: ' + trial)
            state = entry['state']
            if state not in ('MODEL_TRANSCRIBED_CHECKED', 'CROSS_PROVIDER_VERIFIED', 'CONFLICT', 'REFUSED'):
                refuse('unknown state: ' + trial)
            if state == 'REFUSED':
                if not entry.get('reasons') or 'figure_counts' in entry:
                    refuse('unnamed refusal or admitted counts on refused row: ' + trial)
                continue
            check_transcription_state(entry)
            if state != 'CONFLICT' and state != entry['transcription_state']:
                refuse('transcription state mismatch: ' + trial)
            counts = entry['figure_counts']
            if (set(counts) != set(recovery_map.COUNT_KEYS) or
                    any(type(v) is not int or v < 0 for v in counts.values()) or
                    not 0 <= counts['ai'] <= counts['n1i'] or not 0 <= counts['ci'] <= counts['n2i'] or
                    min(counts['n1i'], counts['n2i']) <= 0):
                refuse('typed figure counts: ' + trial)
            conflicts = [k for k in recovery_map.COUNT_KEYS if counts[k] != entry['relayed'][k]]
            if entry['conflicts'] != conflicts or (state == 'CONFLICT') != bool(conflicts):
                refuse('conflict state: ' + trial)
            rows = [r for r in data['gate_rows'] if r['row']['kind'] == 'trial'
                    and acronym(r['row']['agent']) == 'TOCILIZUMAB' and acronym(r['row']['trial']) == acronym(trial)]
            if (len(rows) != 1 or rows[0]['status'] != 'ADMITTED' or rows[0]['reasons']
                    or rows[0]['record_ids'] != ids or rows[0]['figure_sha256'] != data['figure_sha256']
                    or rows[0]['poolable'] is not False
                    or {k: rows[0]['row'][k] for k in recovery_map.COUNT_KEYS} != counts
                    or rows[0]['table1_evidence'] != excerpt['evidence']):
                refuse('gate witness/excerpt mismatch: ' + trial)
            check_transcription_state(rows[0])
            for field in ('transcription_state', 'consensus_provider', 'cross_provider_witnesses'):
                if rows[0][field] != entry[field]:
                    refuse('transcription witness mismatch: ' + trial)
            if acronym(trial) == 'BACCBAY':
                note = entry['own_paper']
                if note['safety_counts'] != counts or not note['explanation'] or not re.fullmatch(r'[0-9a-f]{64}', note['sha256']):
                    refuse('own-paper comparison: ' + trial)
        return data
    except (OSError, KeyError, TypeError, ValueError) as exc:
        if str(exc).startswith('FIGURE_BINDING_REFUSED:'):
            raise
        refuse(FIGURE_BINDING + ': ' + str(exc))


def apply_figure_binding(bound, figure):
    """Attach a typed display witness; preserve the original relayed values."""
    bound['figure_binding'] = deepcopy(figure)
    bound['binding'] = figure['state']
    bound['state'] = figure['state']
    bound['poolable'] = False
    if figure['state'] in ('MODEL_TRANSCRIBED_CHECKED', 'CROSS_PROVIDER_VERIFIED', 'CONFLICT'):
        bound['figure_counts'] = deepcopy(figure['figure_counts'])
        bound['record_ids'] = list(figure['record_ids'])
        bound['figure_sha256'] = figure['figure_sha256']
        # These labels refer only to figure counts, not target-population admission.
        bound['numerator'] = figure['transcription_state']
        bound['denominator'] = figure['transcription_state']
    bound['reason'] = '; '.join([figure['state'] + ': ' + figure['trial'],
                                *figure.get('reasons', []),
                                'never pooled: population not adjudicated'])
    if figure['state'] == 'CONFLICT':
        bound['reason'] += '; figure/relayed conflict: ' + ', '.join(figure['conflicts'])
    return bound


def attach(review, slug, *, root=recovery_map.ROOT):
    """Decorate existing mapped rows after synthesis; no inputs are constructed.

    Registry NCT joins precede exact normalized trial names. The committed
    excerpt binds denominators; the committed offline artifact binds figure
    counts for display only. Relayed values remain quarantined and unchanged.
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
    artifact = load_figure_binding(root, block, evidence)
    ledger = []
    for outcome in review.get('outcomes', []):
        if not re.search(r'28[- ]day.*mortality|mortality.*28', outcome.get('name', ''), re.I):
            continue
        # Recovery describes the source's outcome-recorded subset. It does not
        # assert equivalence to the protocol's ITT population or admit a pool.
        block['selected_outcome'] = {'name': outcome['name']}
        bindings = bind(block, evidence)
        displayed = set()
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
            displayed.add(bound['trial'])
            figure, = [e for e in artifact['entries'] if e['trial'] == bound['trial']]
            apply_figure_binding(bound, figure)
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
        # A recovery-map entry need not have a review row (e.g. REMAP-CAP).
        # Show its witness without manufacturing a source row or a pool member.
        outcome['recovery_figure_unmatched'] = [
            {'figure_binding': deepcopy(e), 'reason': 'NO_MATCHING_REVIEW_ROW: ' + e['trial']}
            for e in artifact['entries'] if e['trial'] not in displayed]
    review['recovery_bindings'] = ledger
    # Keep the existing summary consistent with the typed row display.
    for old in review.get('recovery_map', []):
        matches = [b for b in ledger if b['trial'] == old['trial']]
        if len(matches) == 1:
            old.update(after=matches[0]['state'], recovery_state=matches[0]['state'])
    return ledger
