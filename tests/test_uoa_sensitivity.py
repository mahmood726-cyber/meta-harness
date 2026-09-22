"""Unit-of-analysis/design caveat rendering.

Balanced crystalloids keeps design-refused reconstructed cluster-crossover rows out of the pool.
The unit-of-analysis caveat now covers the remaining pooled factorial marginal contrast, while
the refused cluster-crossover rows are carried by the typed design-refusal object.
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # tests/ on the path for _contracts
import json
import os
import re

from harness import page

DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "reviews")


def _load(slug):
    return json.load(open(os.path.join(DOCS, slug, "review.json"), encoding="utf-8"))


def test_crystalloids_uoa_caveat_matches_post_refusal_factorial_state():
    from pathlib import Path
    from _contracts import partition
    from harness import unit_of_analysis
    r = _load('balanced-crystalloids-vs-saline-mortality')
    primary = next(o for o in r['outcomes'] if o.get('primary'))
    partition(Path(__file__).resolve().parents[1], 'balanced-crystalloids-vs-saline-mortality', primary)
    root = Path(__file__).resolve().parents[1]
    records = json.loads((root/'cache/balanced-crystalloids-vs-saline-mortality/records.json').read_text(encoding='utf-8'))
    expected = unit_of_analysis.scan_pooled(r, {str(x['id']): x for x in records['records']})
    assert (r.get('unit_of_analysis') or []) == expected
    # Design refusals remain named even if no factorial member is admitted.
    refused = primary.get('design_refusals') or []
    assert {row.get('trial') for row in refused} >= {'SMART', 'SALT', 'SPLIT'}
    markup = page._riskofbias(r, False)
    assert 'point estimate is unaffected' not in markup
    assert 'within-subject' not in markup
    if any(o['trials'] for o in r['outcomes']):
        for caveat in r.get('unit_of_analysis') or []:
            assert caveat.get('design')
        if any(u.get('design') == 'factorial' for u in r.get('unit_of_analysis') or []):
            assert 'individual-randomized factorial designs' in markup
            assert 'source-reported adjusted marginal estimate' in markup
