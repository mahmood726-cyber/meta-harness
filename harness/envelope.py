"""Source-gated sensitivity specifications; never modifies the primary membership."""
from __future__ import annotations

import copy
import json
import math
import re
from html import escape
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import norm, t

from . import claimgraph
from .topic_registry import topic_id
from .known_missing import _study_from_trial
from .synth import pool

ROOT = Path(__file__).resolve().parents[1]


def trial_input(row):
    """Retain all numerical engine inputs and source evidence, not whole page metadata."""
    from dataclasses import fields
    from .synth import Study
    keys = {f.name for f in fields(Study)} | {'id', 'scale', 'provenance', 'nct', 'endpoint',
           'document_sha256', 'retrieved_utc', 'document_path', 'extracted_text',
           'extracted_text_sha256', 'span', 'source_ref'}
    return {k: copy.deepcopy(v) for k, v in row.items() if k in keys}


def calculate(studies, scale, method='PM', interval='HKSJ', model='random'):
    """Canonical PM path; explicit alternative models retain log-scale pooling."""
    if len(studies) < 2:
        raise ValueError('at least two trials required for an envelope pool')
    if scale.upper() not in {'HR', 'RR', 'OR', 'IRR', 'MD', 'SMD'}:
        raise ValueError('unsupported effect scale')
    if method not in {'PM', 'REML'} or interval not in {'HKSJ', 'Wald'} or model not in {'random', 'fixed'}:
        raise ValueError('unsupported model specification')
    canonical = pool(studies, scale=scale)
    yi, vi = np.array([s.yi_vi() for s in studies]).T
    if not np.all(np.isfinite(yi)) or not np.all(np.isfinite(vi)) or np.any(vi <= 0):
        raise ValueError('nonfinite effect or nonpositive variance')
    k = len(studies)
    tau2 = canonical.tau2
    if model == 'fixed':
        tau2 = 0.
    elif method == 'REML':
        def objective(tau):
            w = 1 / (vi + tau)
            mu = np.sum(w * yi) / np.sum(w)
            return float(np.sum(np.log(vi + tau)) + np.log(np.sum(w)) + np.sum(w * (yi - mu)**2))
        bound = max(1., float(np.var(yi) * 10), float(np.max(vi) * 10))
        fit = minimize_scalar(objective, bounds=(0, bound), method='bounded', options={'xatol': 1e-14})
        if not fit.success or fit.x >= bound * .999:
            raise ValueError('REML optimization did not converge within bounds')
        tau2 = 0. if objective(0.) <= fit.fun else float(fit.x)
    w = 1 / (vi + tau2)
    mu = float(np.sum(w * yi) / np.sum(w))
    q = float(np.sum(w * (yi - mu)**2))
    se = math.sqrt(1 / float(np.sum(w)))
    if interval == 'HKSJ':
        se *= math.sqrt(max(1., q / (k - 1)))
    crit = float(t.ppf(.975, k - 1) if interval == 'HKSJ' else norm.ppf(.975))
    bt = (lambda x: x) if scale.upper() in {'MD', 'SMD'} else math.exp
    ci = [bt(mu - crit * se), bt(mu + crit * se)]
    estimate = bt(mu)
    # Preserve the existing engine exactly for the declared primary path.
    if method == 'PM' and interval == 'HKSJ' and model == 'random':
        estimate, ci = canonical.estimate, [canonical.ci_low, canonical.ci_high]
    pi = None
    pi_reason = None
    if model == 'fixed':
        pi_reason = 'NOT_COMPUTABLE: fixed-effect model has no between-study predictive distribution'
    elif tau2 == 0:
        pi_reason = 'NOT_COMPUTABLE: tau2=0 collapses the prescribed PI onto the CI; no distinct PI is served'
    else:
        half = float(t.ppf(.975, k - 1)) * math.sqrt(tau2 + se**2)
        pi = [bt(mu - half), bt(mu + half)]
        if pi == ci:
            pi, pi_reason = None, 'NOT_COMPUTABLE: PI numerically identical to CI'
    return {'estimate': estimate, 'ci': ci, 'tau2': tau2, 'pi': pi,
            'pi_reason': pi_reason, 'i2': max(0., (canonical.Q-k+1)/canonical.Q)*100 if canonical.Q > 0 else 0.,
            'k': k, 'scale': scale, 'method': method, 'interval': interval, 'model': model}


def compute_spec(spec_id, axis, choice, inputs, scale, *, root=ROOT, reason=None, **options):
    obj = {'spec_id': spec_id, 'axis': axis, 'choice': choice, 'inputs': copy.deepcopy(inputs),
           'options': options, 'computable': False, 'result': None}
    failures = []
    keys = [claimgraph.trial_key(row) or row.get('label') for row in inputs]
    if len(set(keys)) != len(keys):
        failures.append('duplicate trial identity in specification')
    for row in inputs:
        if row.get('scale') and row['scale'].upper() != scale.upper():
            failures.append(f"{row.get('label')}: incompatible effect scale")
        verdict = claimgraph.verify_fact(row, root=root)
        if not verdict['verified']:
            failures.append(f"{row.get('label') or row.get('id')}: {verdict['reason']}")
    if reason:
        failures.append(reason)
    if failures:
        obj['reason'] = 'NOT_COMPUTABLE: ' + '; '.join(failures)
        return obj
    try:
        obj['result'] = calculate([_study_from_trial(x, scale) for x in inputs], scale, **options)
        obj['computable'] = True
    except (ValueError, OverflowError, ZeroDivisionError, TypeError) as exc:
        obj['reason'] = f'NOT_COMPUTABLE: {exc}'
    return obj


def primary(review):
    return next((x for x in review.get('outcomes', []) if x.get('primary')), {})


def _regulatory_alternatives(root):
    path = root / 'outputs/handover/glp1_regulatory/regulatory_sources_glp1.json'
    if not path.exists():
        return []
    rows = []
    for source in json.loads(path.read_text(encoding='utf-8'))['sources']:
        for decision in source.get('decisions', []):
            if decision.get('decision') != 'EXTRACTED':
                continue
            row = claimgraph.regulatory_fact(source, decision, root=root)
            row['label'] = decision['trial']
            row['endpoint'] = decision['outcome']
            # A table transcription can use pipes whereas extracted PDF uses newlines.
            # Select the literal complete table, never normalize the evidence bytes.
            if not row['provenance']['span'] and decision['trial'] == 'FREEDOM-CVO':
                text = (root / source['held']['extracted_text']).read_bytes().decode('utf-8')
                starts = [m.start() for m in re.finditer(r'Table 19\.', text)]
                for start in starts:
                    candidate = text[start:start+2200]
                    if '1.24 (0.90, 1.70)' in candidate and '85/2075' in candidate:
                        row['provenance']['span'] = candidate
                        break
            rows.append({'name': decision['trial'], 'choice': 'strict 3-point, end of study', 'row': row})
            if decision['trial'] == 'FREEDOM-CVO':
                text = (root / source['held']['extracted_text']).read_bytes().decode('utf-8')
                for match in re.finditer(r'Table 24\.', text):
                    span = text[match.start():match.start()+2200]
                    m = re.search(r'3-Point MACE.*?(\d+\.\d+)\s*\((\d+\.\d+),\s*(\d+\.\d+)\)', span, re.S)
                    if m and 'End of Treatment' in span and 'FREEDOM' in span:
                        alt = copy.deepcopy(row)
                        alt.update(effect=float(m[1]), ci_low=float(m[2]), ci_high=float(m[3]))
                        alt['provenance']['span'] = span
                        alt['source'] = span
                        alt['endpoint'] = '3-point MACE, FREEDOM-only, end of treatment'
                        rows.append({'name': decision['trial'], 'choice': 'end of treatment', 'row': alt})
                        break
    return rows


def build(review, root=ROOT):
    root = Path(root)
    prim = primary(review)
    inputs = [trial_input(r) for r in prim.get('trials', [])]
    scale = (prim.get('result') or {}).get('scale') or prim.get('estimand') or 'HR'
    specs = []
    def add(sid, axis, choice, rows=inputs, **kw):
        specs.append(compute_spec(sid, axis, choice, rows, scale, root=root, **kw))
    add('served', 'reference', 'served primary pool')
    add('reml', 'tau estimator', 'REML', method='REML')
    add('wald', 'interval', 'Wald', interval='Wald')
    add('fixed', 'model', 'fixed', model='fixed', interval='Wald')
    rob_path = root / 'cache' / review['slug'] / 'rob2.json'
    rob = json.loads(rob_path.read_text(encoding='utf-8')) if rob_path.exists() else review.get('rob2', {})
    by_id = rob.get('trials') or {}
    def low(row):
        entry = by_id.get(claimgraph.trial_key(row)) or by_id.get(row.get('label')) or {}
        domains = entry.get('domains') or {}
        return entry.get('overall') == 'low' and len(domains) == 5 and all(d.get('level') == 'low' for d in domains.values())
    low_rows = [r for r in inputs if low(r)]
    add('low-rob', 'risk of bias', 'formally low in all five domains', low_rows,
        reason=None if len(low_rows) >= 2 else 'fewer than two trials with all five RoB domains low')
    alternatives = []
    if review['slug'] == topic_id('incretin_cardiovascular'):
        alternatives = _regulatory_alternatives(root)
        missing = (prim.get('known_missing_sensitivity') or {}).get('rows', [])
        for name in ['ELIXA', 'FREEDOM-CVO', 'FLOW']:
            key = next((claimgraph.trial_key(a['row']) for a in alternatives if a['name'] == name), None)
            present = [r for r in inputs if name == r.get('label') or (key and key == claimgraph.trial_key(r))]
            absent = [r for r in inputs if r not in present]
            add(f'without-{name}', 'membership', f'without {name}', absent)
            alt = next((x['row'] for x in alternatives if x['name'] == name), None)
            if alt is None:
                alt = next((dict(x, label=name) for x in missing if name in (x.get('trial_key'), x.get('name'))), {'label': name})
            add(f'with-{name}', 'membership', f'with {name}', absent + [alt])
        for alternative in alternatives:
            row = alternative['row']
            rest = [r for r in inputs if claimgraph.trial_key(r) != claimgraph.trial_key(row)]
            add('alternative-' + str(len(specs)), 'endpoint/timepoint', alternative['name'] + ': ' + alternative['choice'], rest + [row])
        if not any(x['choice'] == 'end of treatment' for x in alternatives):
            add('freedom-eot', 'timepoint', 'FREEDOM-CVO end of treatment', inputs + [{'label': 'FREEDOM-CVO end of treatment'}], reason='no verified trial-only end-of-treatment row recovered')
        records_path = root / 'cache' / review['slug'] / 'records.json'
        # The abstract row is kept as an unsupported alternative, never promoted to FACT.
        add('elixa-four-point', 'endpoint', 'ELIXA four-point abstract', inputs + [{'label': 'ELIXA four-point', 'source_ref': records_path.relative_to(root).as_posix(), 'reason': 'abstract has no CGX held-document provenance'}])
    for strand in (review.get('strands') or {}).get('strands') or []:
        strand_id = strand.get('strand') or strand.get('id')
        if not strand_id:
            raise ValueError('Declared strand has no identifier')
        candidates = [trial_input(row) for row in strand.get('members', []) + strand.get('refused', [])]
        add('all-candidates-' + strand_id, 'membership',
            strand_id + ': all candidates; censoring unverified; endpoint compatibility unverified', candidates)
    return {'schema_version': 1, 'class': 'TRANSFORMATION', 'slug': review['slug'], 'scale': scale,
            'benefit_direction': 'lower' if review['slug'] == topic_id('incretin_cardiovascular') else prim.get('benefit_direction'),
            'enumeration': 'one-axis-at-a-time around served pool; not a Cartesian product',
            'input_set_version': claimgraph.input_set_version(prim),
            'alternatives': alternatives, 'specifications': specs}


def sentence(obj):
    specs = obj['specifications']
    results = [s['result'] for s in specs if s['computable']]
    n, total = len(results), len(specs)
    if not results:
        return f'across 0 computable specifications of {total} enumerated, effect range and conclusions are NOT_COMPUTABLE'
    null = 0. if obj['scale'] in {'MD', 'SMD'} else 1.
    direction = obj.get('benefit_direction')
    favours = sum(r['estimate'] < null if direction == 'lower' else r['estimate'] > null for r in results) if direction in {'lower', 'higher'} else None
    favoured = f'{favours} of {n} favoured the intervention ({direction} is favourable)' if favours is not None else 'favourable direction NOT_ASSESSED (outcome benefit direction unspecified)'
    excludes = sum(r['ci'][1] < null or r['ci'][0] > null for r in results)
    return (f"across {n} computable specifications of {total} enumerated, {obj['scale']} ranged "
            f"{min(r['estimate'] for r in results):.6g}-{max(r['estimate'] for r in results):.6g}; "
            f"{favoured}; {excludes} of {n} had a CI excluding {null:g}")


def render(obj):
    rows = []
    for s in obj['specifications']:
        result = s['result'] if s['computable'] else s.get('reason', 'NOT_COMPUTABLE')
        rows.append('<tr><td>' + escape(s['spec_id']) + '</td><td>' + escape(s['choice']) + '</td><td>' + escape(json.dumps(result, ensure_ascii=False, sort_keys=True)) + '</td></tr>')
    return '<section id="gs-envelope"><h3>Robustness envelope</h3><p>' + escape(sentence(obj)) + '</p><table><tr><th>Specification</th><th>Choice</th><th>Result (tau2 beside I2)</th></tr>' + ''.join(rows) + '</table></section>'
