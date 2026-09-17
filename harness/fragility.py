"""One-change conclusion fragility with explicit counterfactual null studies."""
from __future__ import annotations

import json
import math
from html import escape
from statistics import median

from . import claimgraph, envelope
from .known_missing import _study_from_trial
from .synth import Study


def _changes(base, result, scale):
    null = 0. if scale in {'MD', 'SMD'} else 1.
    direction = lambda value: (value > null) - (value < null)
    crosses = lambda r: r['ci'][0] <= null <= r['ci'][1]
    return {'direction_changed': direction(base['estimate']) != direction(result['estimate']),
            'ci_crossing_changed': crosses(base) != crosses(result), 'ci_includes_null': crosses(result)}


def leave_one_out(studies, scale):
    """Numerical kernel, also used for the explicitly synthetic binding plant."""
    baseline = envelope.calculate(studies, scale)
    rows = []
    for i, study in enumerate(studies):
        try:
            result = envelope.calculate(studies[:i] + studies[i+1:], scale)
            rows.append({'change': 'leave-one-out', 'trial': study.label, 'computable': True,
                         'result': result, **_changes(baseline, result, scale)})
        except ValueError as exc:
            rows.append({'change': 'leave-one-out', 'trial': study.label, 'computable': False,
                         'reason': 'NOT_COMPUTABLE: ' + str(exc)})
    return rows


def build(review, env, root=envelope.ROOT):
    prim = envelope.primary(review)
    inputs = [envelope.trial_input(r) for r in prim.get('trials', [])]
    scale = env['scale']
    baseline = env['specifications'][0]
    rows = []
    def add(change, name, data, reason=None):
        row = envelope.compute_spec(f'{change}:{name}', change, name, data, scale, root=root, reason=reason)
        row.update(change=change, trial=name)
        if not baseline['computable']:
            row.update(computable=False, result=None, reason='NOT_COMPUTABLE: baseline lacks verified inputs; changes cannot be assessed')
        elif row['computable']:
            row.update(_changes(baseline['result'], row['result'], scale))
        rows.append(row)
    rob_path = root / 'cache' / review['slug'] / 'rob2.json'
    rob = json.loads(rob_path.read_text(encoding='utf-8')) if rob_path.exists() else review.get('rob2', {})
    for i, trial in enumerate(inputs):
        add('leave-one-out', trial.get('label') or claimgraph.trial_key(trial), inputs[:i] + inputs[i+1:])
        entry = (rob.get('trials') or {}).get(claimgraph.trial_key(trial)) or {}
        add('RoB-exclusion', trial.get('label') or claimgraph.trial_key(trial), inputs[:i] + inputs[i+1:],
            reason=None if entry.get('overall') in {'high', 'some concerns', 'some_concerns'} else 'no assessed non-low formal RoB judgement authorizes this exclusion')
    for alt in env.get('alternatives', []):
        matches = [i for i, r in enumerate(inputs) if claimgraph.trial_key(r) == claimgraph.trial_key(alt['row'])]
        data = list(inputs)
        if matches:
            data[matches[0]] = alt['row']
        add('endpoint-correction', alt['name'] + ': ' + alt['choice'], data,
            reason=None if matches else 'alternative trial is not in served pool; addition is not a single endpoint correction')
    for size in ['median', 'largest']:
        row = {'change': 'null-study', 'trial': size, 'class': 'TRANSFORMATION',
               'inputs': inputs, 'computable': False,
               'scenario': 'hypothetical unpublished null study; never an observed FACT',
               'size_definition': 'information size 1/SE^2; largest means smallest observed SE, not participant N'}
        if baseline['computable']:
            studies = [_study_from_trial(r, scale) for r in inputs]
            ses = [math.sqrt(s.yi_vi()[1]) for s in studies]
            se = median(ses) if size == 'median' else min(ses)
            if scale in {'MD', 'SMD'}:
                row['reason'] = 'NOT_COMPUTABLE: requested HR=1 null-study scenario is not an additive-scale estimand'
            else:
                from scipy.stats import norm
                z = float(norm.ppf(.975))
                null = Study('hypothetical null', effect=1., ci_low=math.exp(-z*se), ci_high=math.exp(z*se))
                result = envelope.calculate(studies + [null], scale)
                row.update(computable=True, result=result, hypothetical={'effect': 1., 'se': se},
                           **_changes(baseline['result'], result, scale))
        else:
            row['reason'] = 'NOT_COMPUTABLE: baseline lacks verified inputs'
        rows.append(row)
    return {'schema_version': 1, 'class': 'TRANSFORMATION', 'slug': review['slug'],
            'input_set_version': env['input_set_version'], 'baseline': baseline, 'rows': rows,
            'search_scope': 'single changes only; no claim of a global minimum beyond one change',
            'minimum_changes_direction': 1 if any(r.get('direction_changed') for r in rows) else None,
            'minimum_changes_ci_crossing': 1 if any(r.get('ci_crossing_changed') for r in rows) else None}


def sentence(obj):
    rows = obj['rows']
    usable = [r for r in rows if r.get('computable')]
    if not usable:
        return f'fragility: NOT_COMPUTABLE (0 of {len(rows)} enumerated single changes assessed); no stability conclusion is justified'
    direction = [r for r in usable if r.get('direction_changed')]
    crossing = [r for r in usable if r.get('ci_crossing_changed')]
    d = ('one change changes direction: ' + ', '.join(r['trial'] for r in direction)) if direction else 'no assessed single change changes direction'
    c = ('one change alters CI crossing: ' + ', '.join(r['trial'] for r in crossing)) if crossing else 'no assessed single change alters CI crossing'
    nulls = []
    for size in ['median', 'largest']:
        row = next((r for r in rows if r.get('change') == 'null-study' and r.get('trial') == size), {})
        answer = ('yes' if row.get('ci_includes_null') else 'no') if row.get('computable') else 'NOT_COMPUTABLE'
        nulls.append(f'one hypothetical null study of {size} information size yields a CI including the null: {answer}')
    return f'fragility: {d}; {c}; ' + '; '.join(nulls) + f'; {len(usable)} of {len(rows)} enumerated single changes assessed; larger combinations untested'


def render(obj):
    rows = ''.join('<tr><td>' + escape(r['change'] + ': ' + r['trial']) + '</td><td>' +
                   escape(json.dumps({k: v for k, v in r.items() if k in {'result', 'reason', 'direction_changed', 'ci_crossing_changed', 'scenario'}}, ensure_ascii=False, sort_keys=True)) + '</td></tr>' for r in obj['rows'])
    return '<section id="gs-fragility"><h3>Conclusion fragility</h3><p>' + escape(sentence(obj)) + '</p><table><tr><th>Single change</th><th>Result</th></tr>' + rows + '</table></section>'
