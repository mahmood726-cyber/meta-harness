"""Conservative dose arms and causal pre-pool refusal checks."""
from __future__ import annotations
import re
from copy import deepcopy
from typing import TypedDict


class Arm(TypedDict):
    label: str
    drug: str
    dose: str | None
    n: int | None


def is_multi_arm(text):
    return bool(re.search(r'\b\d+(?::\d+){2,}\b|\b(?:three|four|multi)[- ]arm', text, re.I))


def parse_arms(text) -> list[Arm]:
    """Parse the randomisation clause, not result percentages or total N/ratio.

    Drug names remain source spellings (AZD6140 is not silently recoded).
    n is known only from a contiguous explicit n= annotation.
    """
    m = re.search(r'randomi[sz]ed[^.]*?to receive (?:either )?(.+?)(?:\.(?!\d)|$)', text, re.I)
    if not m:
        return []
    arms = []
    for part in re.split(r',\s*(?:or\s+)?|\s+or\s+', m[1]):
        a = re.search(r'(?:twice-daily\s+)?(?P<drug>[A-Za-z][A-Za-z0-9-]*)\s+(?P<dose>\d+(?:\.\d+)?[- ]mg\b.*)', part)
        if a:
            n = re.search(r'\bn\s*=\s*(\d+)', part, re.I)
            arms.append(dict(label=part.strip(), drug=a['drug'], dose=a['dose'].strip(),
                             n=int(n[1]) if n else None))
    # A shared leading frequency governs repeated doses of the same named drug.
    if arms and m[1].lower().startswith('twice-daily '):
        for arm in arms:
            if arm['drug'] == arms[0]['drug']:
                arm['dose'] += ' twice daily'
    return arms


def km_products(row, text):
    """Flag arithmetic coincidence as suspicion, not proof of fabrication."""
    hits = []
    for sentence in re.split(r'(?<=[.;])\s+', text):
        if not re.search(r'Kaplan[-– ]Meier|\bKM\b', sentence, re.I):
            continue
        for match in re.finditer(r'(\d+(?:\.\d+)?)\s*%', sentence):
            pct = float(match[1])
            if not 0 <= pct <= 100:
                continue
            for count, denom in (('ai', 'n1i'), ('ci', 'n2i')):
                n, a = row.get(denom), row.get(count)
                if (isinstance(n, (int, float)) and n > 0 and isinstance(a, (int, float))
                        and a == round(pct * n / 100)):
                    hits.append(dict(problem='KM_PERCENT_TO_COUNT', field=count, percent=pct,
                                     n=n, count=a, span=sentence))
    return hits


def control_problems(comparisons):
    groups = {}
    for row in comparisons:
        # Scope controls by trial AND outcome; distinct outcomes are not duplication.
        key = (row.get('trial_id'), row.get('outcome'), row.get('control_id'))
        if not all(key):
            raise ValueError(f'SHARED_CONTROL_IDENTITY_UNRESOLVED: {key}')
        groups.setdefault(key, []).append(row)
    errors = []
    for key, rows in groups.items():
        if any(not isinstance(r.get(k), (int, float)) or r[k] < 0
               for r in rows for k in ('n2i', 'ci')):
            errors.append(dict(problem='SHARED_CONTROL_UNBOUND', control=key))
            continue
        if len(rows) > 1:
            ns = {r.get('control_n') for r in rows}
            events = {r.get('control_events') for r in rows}
            if len(ns) != 1 or None in ns or len(events) != 1 or None in events:
                errors.append(dict(problem='SHARED_CONTROL_UNBOUND', control=key))
            elif (sum(r.get('n2i', 0) for r in rows) > next(iter(ns)) or
                  sum(r.get('ci', 0) for r in rows) > next(iter(events))):
                errors.append(dict(problem='SHARED_CONTROL_DOUBLE_COUNTED', control=key))
    return errors


def require_controls(comparisons):
    problems = control_problems(comparisons)
    if problems:
        raise ValueError('; '.join(f"{p['problem']}: {p['control']}" for p in problems))
    return comparisons


def split_control(comparisons):
    """Split BOTH events and N; do not create zero-event evidence from missing data."""
    rows = deepcopy(comparisons)
    groups = {}
    for r in rows:
        key = (r.get('trial_id'), r.get('outcome'), r.get('control_id'))
        if not all(key):
            raise ValueError(f'SHARED_CONTROL_IDENTITY_UNRESOLVED: {key}')
        groups.setdefault(key, []).append(r)
    for key, group in groups.items():
        ns, es = {r.get('control_n') for r in group}, {r.get('control_events') for r in group}
        if len(ns) != 1 or None in ns or len(es) != 1 or None in es:
            raise ValueError(f'SHARED_CONTROL_UNBOUND: {key}')
        for r in group:
            r['n2i'], r['ci'] = next(iter(ns)) / len(group), next(iter(es)) / len(group)
    return rows


def endpoint_problem(result_span, target):
    mi = re.search(r'myocardial infarction|\bMI\b', result_span, re.I)
    composite = re.search(r'composite|\bMACE\b', target, re.I)
    if mi and composite and not (re.search(r'stroke', result_span, re.I) and
                                 re.search(r'death|mortality', result_span, re.I)):
        return 'MI_ONLY_NOT_COMPOSITE'
    return None


def assess(record, row=None, target='', result_span=''):
    text = record.get('abstract', '')
    problems = km_products(row or {}, text)
    endpoint = endpoint_problem(result_span, target)
    if endpoint:
        problems.append({'problem': endpoint, 'span': result_span})
    disperse = bool(re.search(r'\bDISPERSE-2\b', record.get('title', ''), re.I))
    if disperse:
        problems.append({'problem': 'FULL_TABLE_NOT_HELD', 'reason': 'full table not held; recovery active'})
    return dict(arms=parse_arms(text), status='REFUSED' if problems else 'NO_RULE_FIRED',
                recovery='ACTIVE' if disperse else None, problems=problems)


def require_poolable(record, row, target='', result_span=''):
    assessment = assess(record, row, target, result_span)
    if assessment['status'] == 'REFUSED':
        raise ValueError(f"{record.get('id')}: " + '; '.join(p['problem'] for p in assessment['problems']))
    return row
