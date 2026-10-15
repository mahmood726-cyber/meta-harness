#!/usr/bin/env python3
"""Independent Topic 20 audit. NOT a production replay or gate test.

Run: python audit.py [--output results.json]
Requires Python 3.10+, NumPy and SciPy. No network calls or repository writes.
Inputs are manually transcribed evidence, not exported production objects.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any
import numpy as np
from scipy.optimize import brentq
from scipy.stats import chi2, norm, t


def ratio_meta(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """PM random effects, floored HKSJ CI; PI uses the review's t(k-1) rule."""
    if len(rows) < 2:
        raise ValueError("Meta-analysis needs at least two rows.")
    x = np.array([[r['effect'], r['lower'], r['upper']] for r in rows], dtype=float)
    if not np.all(np.isfinite(x)) or np.any(x <= 0):
        raise ValueError("Effects and bounds must be positive, finite numbers.")
    if np.any(x[:, 1] >= x[:, 2]) or np.any(x[:, 0] < x[:, 1]) or np.any(x[:, 0] > x[:, 2]):
        raise ValueError("Invalid confidence interval.")
    y = np.log(x[:, 0])
    v = ((np.log(x[:, 2]) - np.log(x[:, 1])) / (2 * norm.ppf(0.975))) ** 2
    df = len(rows) - 1
    def q(tau2: float) -> float:
        w = 1.0 / (v + tau2)
        mu = float(np.dot(w, y) / w.sum())
        return float(np.dot(w, (y - mu) ** 2))
    q0 = q(0.0)
    if q0 <= df:
        tau2 = 0.0
    else:
        hi = 1.0
        while q(hi) > df:
            hi *= 2.0
            if hi > 1e12:
                raise ArithmeticError("Could not bracket PM variance.")
        tau2 = float(brentq(lambda z: q(z) - df, 0.0, hi, xtol=1e-14))
    w = 1.0 / (v + tau2)
    mu = float(np.dot(w, y) / w.sum())
    floor = max(1.0, q(tau2) / df)
    se = math.sqrt(floor / float(w.sum()))
    crit = float(t.ppf(0.975, df))
    ci = np.exp(mu + np.array([-1.0, 1.0]) * crit * se)
    pi = np.exp(mu + np.array([-1.0, 1.0]) * crit * math.sqrt(tau2 + se * se))
    fw = 1.0 / v
    fmu = float(np.dot(fw, y) / fw.sum())
    fse = math.sqrt(1.0 / float(fw.sum()))
    return {
        'k': len(rows), 'trial_ids': [r['id'] for r in rows],
        'effect': math.exp(mu), 'hksj_ci': ci.tolist(), 'tau2': tau2,
        'Q': q0, 'Q_at_tau2': q(tau2), 'I2_percent': max(0.0, (q0-df)/q0)*100 if q0 else 0.0,
        'Q_p_value': float(chi2.sf(q0, df)), 'hksj_variance_floor': floor,
        'weights_percent': (100*w/w.sum()).tolist(),
        'prediction_interval_t_k_minus_1': pi.tolist(),
        'common_effect_diagnostic': math.exp(fmu),
        'common_effect_ci_diagnostic': np.exp(fmu + np.array([-1.0, 1.0])*norm.ppf(0.975)*fse).tolist(),
        'within_study_standard_errors_from_printed_CIs': np.sqrt(v).tolist(),
    }


def crude_rr(a: int, n: int, b: int, m: int) -> dict[str, Any]:
    """Unadjusted participant RR and log-Wald CI; no continuity correction."""
    if not (0 < a < n and 0 < b < m):
        raise ValueError("This diagnostic requires nonzero event and nonevent cells.")
    rr = (a / n) / (b / m)
    se = math.sqrt(1/a - 1/n + 1/b - 1/m)
    ci = np.exp(math.log(rr) + np.array([-1., 1.])*norm.ppf(.975)*se)
    return {'events_t': a, 'n_t': n, 'events_c': b, 'n_c': m,
            'risk_ratio': rr, 'ci95_log_wald': ci.tolist(),
            'status': 'AUDITOR_DERIVED_NOT_ADMITTED_TO_HARNESS'}


def run() -> dict[str, Any]:
    data = json.loads(Path(__file__).with_name('inputs.json').read_text(encoding='utf-8'))
    rows = data['trials']
    hashes = []
    passages = data['passages']
    # The supplied pack's passage strings are the hash inputs, not a downloaded PDF.
    for p in passages:
        got = hashlib.sha256(p['text'].encode('utf-8')).hexdigest()
        hashes.append({'id': p['id'], 'expected': p['expected_sha256'], 'computed': got, 'matches': got == p['expected_sha256']})
    pooled = ratio_meta(rows)
    mortality_diagnostics = {
        r['label']: crude_rr(r['events_t'], r['n_t'], r['events_c'], r['n_c'])
        for r in rows if 'events_t' in r
    }
    safety = {
        'EMPHASIS_HF_laboratory_potassium_above_5_5_mmol_L': crude_rr(158, 1336, 96, 1340),
        'EMPHASIS_HF_laboratory_potassium_above_6_0_mmol_L': crude_rr(33, 1336, 25, 1340),
        'EMPHASIS_HF_investigator_reported_hyperkalemia_separate_endpoint': crude_rr(109, 1360, 50, 1369),
    }
    checks = {
        'all_three_passage_hashes_match': len(hashes) == 3 and all(h['matches'] for h in hashes),
        'displayed_pooled_rounding_matches': (f"{pooled['effect']:.2f}", *(f"{z:.2f}" for z in pooled['hksj_ci'])) == ('0.88', '0.29', '2.63'),
        'displayed_prediction_rounding_matches': tuple(f"{z:.2f}" for z in pooled['prediction_interval_t_k_minus_1']) == ('0.12','6.63'),
        'pm_equation_Q_equals_df': abs(pooled['Q_at_tau2'] - (pooled['k']-1)) < 1e-10,
        'RALES_reported_Cox_ratio_is_not_crude_RR': abs(mortality_diagnostics['RALES']['risk_ratio']-0.70) > 0.05,
        'J_EMPHASIS_reported_HR_is_not_crude_RR': abs(mortality_diagnostics['J-EMPHASIS-HF']['risk_ratio']-1.77) > 0.08,
        'safety_denominators_are_not_randomized_N': (1336,1340) != (1364,1373),
    }
    if not all(checks.values()):
        raise AssertionError(f"Audit self-check failed: {checks}")
    return {
        'identity': {k:data[k] for k in ('slug','pinned_ref','review_sha256')},
        'scope': 'Independent numerical reconstruction and manual-evidence checks, NOT a full repository replay, source acquisition proof or production-gate test.',
        'primary_analysis': pooled, 'passage_hashes': hashes,
        'mortality_count_diagnostics_not_replacements_for_HRs': mortality_diagnostics,
        'safety_recovery_diagnostics_not_pooled': safety,
        'leave_one_out_diagnostics_not_served_under_k2_policy': [
            {'omitted': r['label'], **ratio_meta(rows[:i]+rows[i+1:])}
            for i, r in enumerate(rows)
        ], 'self_checks': checks,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('results.json'))
    args = parser.parse_args()
    result = run()
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({'self_checks': result['self_checks'], 'primary': result['primary_analysis'],
                      'safety': result['safety_recovery_diagnostics_not_pooled'], 'output': str(args.output)}, indent=2))
