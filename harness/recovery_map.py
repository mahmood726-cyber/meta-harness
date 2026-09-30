"""Outcome-scoped recovery, with RELAYED values quarantined from synthesis."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATES = frozenset({'REPORTED_OTHER_FORM', 'COUNTS_RECOVERED',
                    'POPULATION_UNRESOLVED', 'ANALYSIS_READY'})
COUNT_KEYS = ('ai', 'n1i', 'ci', 'n2i')


def load_map(root=ROOT):
    return json.loads((Path(root) / 'docs/recovery_maps.json').read_text(encoding='utf-8'))['topics']


def denominator_for(outcome, trial, *, root=ROOT):
    """Return typed RELAYED denominators, never synthesis-ready integers alone."""
    name = outcome.get('name', '') if isinstance(outcome, dict) else outcome
    if not re.search(r'28[- ]day.*mortality|mortality.*28', name, re.I):
        raise ValueError(f'OUTCOME_POPULATION_NOT_HELD: {trial}: {name}')
    matches = [(d, e) for d in load_map(root).values() for e in d['entries']
               if trial in (e['trial'], e['pmid'])]
    if len(matches) != 1:
        raise ValueError(f'RECOVERY_IDENTITY_UNRESOLVED: {trial}')
    d, e = matches[0]
    return dict(n1i=e['n1i'], n2i=e['n2i'], population=d['population'],
                provenance='RELAYED', poolable=False)


def classify(entry, population, outcome, abstract):
    """Explicit population mismatch takes precedence; percentages are not counts.

    Deliberately no automatic ANALYSIS_READY promotion: this lane holds no WHO
    forest-table bytes. A boolean or investigator quote cannot establish binding.
    """
    own_form = []
    for sentence in re.split(r'(?<=[.;])\s+', abstract):
        if (re.search(r'mortality|\bdied\b|\bdeaths?\b', sentence, re.I)
                and re.search(r'28\s*[- ]?\s*days?|day\s*28', sentence, re.I)
                and re.search(r'\d+(?:\.\d+)?\s*%', sentence)):
            own_form.append(sentence)
    rule = outcome.get('population')
    state = ('POPULATION_UNRESOLVED' if rule and rule != population else
             'REPORTED_OTHER_FORM' if own_form else 'COUNTS_RECOVERED')
    return {'state': state, 'provenance': 'RELAYED', 'poolable': False,
            'reason': f"RELAYED_COUNTS_NOT_BOUND: {entry['trial']}" +
                      (f'; selected population {rule!r} differs from {population!r}'
                       if state == 'POPULATION_UNRESOLVED' else ''),
            'reported_other_form': own_form,
            'relayed_counts': {k: entry[k] for k in COUNT_KEYS},
            'population': population, 'recovery': 'ACTIVE'}


def require_poolable(row):
    """Fail closed even if a caller forges ANALYSIS_READY on a relayed row."""
    recovery = row.get('recovery_map', row)
    if recovery.get('provenance') == 'RELAYED' or 'relayed_counts' in recovery:
        raise ValueError(f"RELAYED_COUNTS_NOT_BOUND: {row.get('id', row.get('trial', 'unknown trial'))}")
    return row


def attach(review, slug, *, root=ROOT):
    """Mutate mortality rows only, return the ledger; never append pool members."""
    data = load_map(root).get(slug)
    if not data:
        return []
    path = Path(root) / 'cache' / slug / 'records.json'
    records = {str(r['id']): r for r in json.loads(path.read_text(encoding='utf-8'))['records']}
    ledger = []
    for outcome in review.get('outcomes', []):
        if not re.search(r'28[- ]day.*mortality|mortality.*28', outcome.get('name', ''), re.I):
            continue
        for entry in data['entries']:
            status = classify(entry, data['population'], outcome,
                              records.get(entry['pmid'], {}).get('abstract', ''))
            rows = [r for key in ('trials', 'declared_absent_trials') for r in outcome.get(key, [])
                    if (entry['pmid'] and entry['pmid'] in re.findall(r'\b\d+\b', str(r.get('id', ''))))
                    or r.get('label') == entry['trial']]
            for row in rows:
                before = row.get('result_status', {}).get('state', row.get('state'))
                row['recovery_map'] = status.copy()
                # Existing source-bound pooled effects are independent of the relay.
                if row not in outcome.get('trials', []):
                    row['state'] = status['state']
                    row['reason_code'] = status['state']
                    row['result_status'] = {'state': status['state'], 'basis': status['reason']}
                ledger.append(dict(trial=entry['trial'], pmid=entry['pmid'], before=before,
                                   after=row.get('result_status', {}).get('state'), **{'recovery_state': status['state']}))
            if not rows:
                ledger.append(dict(trial=entry['trial'], pmid=entry['pmid'], before='NO_ROW',
                                   after=status['state'], recovery_state=status['state']))
    review['recovery_map'] = ledger
    return ledger
