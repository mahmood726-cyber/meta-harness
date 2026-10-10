#!/usr/bin/env python3
"""Independent numerical / transcription checks for meta-harness topic 13.

Run: python audit.py
Dependencies: numpy, scipy
This is NOT a repository replay or an implementation of its publication gates.
Inputs are a manually transcribed snapshot of the pinned HTML and the user's
three supplied audit passages. The snapshot consistency check is an auditor-
proposed invariant, not an exercised production check.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any
import numpy as np
import scipy
from scipy.optimize import brentq
from scipy.stats import norm, t

ROOT = Path(__file__).resolve().parent


def pool(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Generic IV log-ratio, PM tau2, floored HKSJ t(k-1) and declared PI."""
    if len(rows) < 2:
        raise ValueError('This independent function requires at least two rows.')
    for row in rows:
        e, lo, hi = row['effect'], row['lower'], row['upper']
        if not (0 < lo < e < hi and all(math.isfinite(x) for x in (e, lo, hi))):
            raise ValueError(f'Invalid effect/interval: {row}')
    y = np.log([r['effect'] for r in rows])
    v = ((np.log([r['upper'] for r in rows]) - np.log([r['lower'] for r in rows])) /
         (2 * norm.ppf(.975))) ** 2
    k = len(rows)
    def residual(tau2: float) -> float:
        w = 1 / (v + tau2)
        mu = float(np.dot(w, y) / w.sum())
        return float(np.dot(w, (y - mu)**2) - (k - 1))
    if residual(0) <= 0:
        tau2 = 0.0
    else:
        upper = 1.0
        while residual(upper) > 0:
            upper *= 2
            if upper > 1e8:
                raise RuntimeError('Unable to bracket PM root.')
        tau2 = float(brentq(residual, 0, upper, xtol=1e-14))
    w = 1 / (v + tau2)
    mu = float(np.dot(w, y) / w.sum())
    q_res = float(np.dot(w, (y-mu)**2))
    floor_factor = max(1.0, q_res/(k-1))
    se = float(np.sqrt(floor_factor/w.sum()))
    critical = float(t.ppf(.975, k-1))
    w0 = 1/v
    mu0 = float(np.dot(w0, y)/w0.sum())
    Q = float(np.dot(w0, (y-mu0)**2))
    i2 = max(0.0, (Q-k+1)/Q)*100 if Q else 0.0
    return {
        'k': k, 'estimate': math.exp(mu),
        'ci_low': math.exp(mu-critical*se), 'ci_high': math.exp(mu+critical*se),
        'tau2': tau2, 'Q': Q, 'I2_percent': i2,
        'pi_low': math.exp(mu-critical*math.sqrt(tau2+se*se)),
        'pi_high': math.exp(mu+critical*math.sqrt(tau2+se*se)),
        'HKSJ_floor_factor': floor_factor, 'df': k-1,
        'weights': {row['trial']: float(weight) for row, weight in zip(rows, w/w.sum())},
    }


def screening_contradictions(snapshot: list[dict[str, Any]]) -> list[str]:
    """Proposed invariant applied only to supplied, manually transcribed states.

    This fixture has no legitimate report-specific exclusions: each X2 concerns
    a trial population/setting, not a duplicate or non-results publication.
    """
    return [r['nct'] for r in snapshot
            if r['family_status'] == 'ELIGIBLE' and r['record_rule'] == 'X2'
            and r['exclusion_scope'] == 'trial_population_or_setting']


def main() -> None:
    data = json.loads((ROOT/'inputs.json').read_text(encoding='utf-8'))
    primary = pool(data['efficacy_rows'])
    expected = data['expected_independent_reconstruction']
    # These expected values reproduce the published rounding. They are not hashes
    # of the review core and do not establish a full deterministic replay.
    for key, val in expected.items():
        assert math.isclose(primary[key], val, abs_tol=1e-9, rel_tol=0), (key, primary[key], val)
    digests = []
    for row in data['sample_passages']:
        sha = hashlib.sha256(row['passage'].encode('utf-8')).hexdigest()
        match = sha == row['expected_sha256']
        digests.append({'pmid': row['pmid'], 'computed_sha256': sha, 'matches': match})
        assert match, (row['pmid'], sha)
    loo = []
    for i, row in enumerate(data['efficacy_rows']):
        out = pool(data['efficacy_rows'][:i]+data['efficacy_rows'][i+1:])
        out['omitted_trial'] = row['trial']
        out['CI_includes_one'] = out['ci_low'] <= 1 <= out['ci_high']
        loo.append(out)
    assert all(r['CI_includes_one'] for r in loo)
    # A measure label change alone does not alter generic-IV log(effect) inputs.
    relabelled = copy.deepcopy(data['efficacy_rows'])
    relabelled[1]['served_measure'] = 'HR'
    assert pool(relabelled) == primary
    z_975 = float(norm.ppf(.9875))
    se = (math.log(1.04)-math.log(.73))/(2*z_975)
    lower = math.exp(math.log(.87)-float(norm.ppf(.975))*se)
    upper = math.exp(math.log(.87)+float(norm.ppf(.975))*se)
    unrounded = copy.deepcopy(data['efficacy_rows'])
    unrounded[2]['lower'], unrounded[2]['upper'] = lower, upper
    mismatch = screening_contradictions(data['screening_snapshot'])
    assert len(mismatch) == 5
    corrected = copy.deepcopy(data['screening_snapshot'])
    for row in corrected:
        row['family_status'] = 'INELIGIBLE'
    assert not screening_contradictions(corrected)
    out = {
        'scope': data['scope'], 'identity': data['identity'],
        'environment': {'numpy': np.__version__, 'scipy': scipy.__version__},
        'primary': primary, 'sample_passage_digest_checks': digests,
        'leave_one_out': loo,
        'ENGAGE_conversion_from_rounded_printed_97_5_CI': {
            'z_two_sided_97_5': z_975, 'SE_from_printed_bounds': se,
            'derived_95_CI_lower': lower, 'derived_95_CI_upper': upper,
            'pool_using_unrounded_conversion': pool(unrounded),
            'note': 'Derivation assumes a log-Wald interpretation. Printed bounds are rounded; this does not recover an exact original unrounded SE.'},
        'screening_snapshot_contradictions': mismatch,
        'locally_corrected_family_count': {
            'served_eligible': 12, 'five_population_setting_exclusions_removed': 5,
            'remaining_holding_other_classifications_fixed': 7,
            'note': 'Not a complete re-adjudication; efficacy membership remains 4.'},
        'measure_relabel_only_preserves_numeric_pool': True,
        'all_assertions_passed': True,
    }
    (ROOT/'results.json').write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
