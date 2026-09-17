"""Progressive replay with explicitly unidentified attribution steps."""
from __future__ import annotations

import hashlib
import json
import math
import re
from html import escape

from . import comparator_truth, envelope, parity_relation


def replay(step_inputs, scale, comparator_options, *, root=envelope.ROOT, reason=None):
    """Replay explicit intermediate tables; never substitute our data for theirs.

    The caller must hold each input table and the comparator's method convention.
    Missing tables/methods remain unidentified; adjacent computable steps alone
    support a delta. Comparator pooled numbers are not used as trial inputs.
    """
    definitions = [('their trials + their data + their method', 'reference'),
                   ('our membership + their extraction + their method', 'membership'),
                   ('our membership + our extraction + their method', 'endpoint definition / effect estimate'),
                   ('our membership + our extraction + our model', 'model')]
    rows = []
    for i, (choice, attribution) in enumerate(definitions):
        inputs = step_inputs[i]
        refusal = None
        if inputs is None:
            inputs = []
            refusal = 'intermediate per-trial input table not held'
        if i < 3 and comparator_options is None:
            refusal = reason or 'exact comparator method convention not held'
        options = comparator_options if i < 3 and comparator_options is not None else {}
        row = envelope.compute_spec(str(i), 'replay', choice, inputs, scale, root=root, reason=refusal, **options)
        row.update(step=i, attribution=attribution, delta_log_effect=None)
        if i == 0 and not row['computable']:
            row['reason'] = 'NOT REPRODUCIBLE FROM HELD TEXT: ' + row.get('reason', '')
        if i and row['computable'] and rows[-1]['computable']:
            if scale in {'MD', 'SMD'}:
                row['delta_raw_effect'] = row['result']['estimate'] - rows[-1]['result']['estimate']
            else:
                row['delta_log_effect'] = math.log(row['result']['estimate']) - math.log(rows[-1]['result']['estimate'])
        rows.append(row)
    return rows


def build(review, env, root=envelope.ROOT):
    comp = review.get('comparator') or {}
    path = root / 'cache' / review['slug'] / 'comparator_fulltext.txt'
    text = path.read_text(encoding='utf-8') if path.exists() else ''
    held = {'path': path.relative_to(root).as_posix(),
            'document_sha256': hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None}
    method_match = re.search(r'Pooled summary estimates.*?small number of studies\.', text, re.I | re.S)
    method = {**held, 'span': method_match.group(0) if method_match else None,
              'status': 'PM with Hartung-Knapp named in held text; variance-floor convention unstated' if method_match else 'NOT_COMPUTABLE: exact comparator method not recovered'}
    reported = comp.get('reported') or []
    truth = comparator_truth.assess_review(review['slug'], review, None, text)
    parity = parity_relation.load_parity_row(str(root), review['slug'])
    relation = parity_relation.compute(parity, review) if parity else {'relation': 'NOT_ENUMERABLE'}
    # Held text is prose and summary tables. Per-trial input rows must be supplied
    # separately with located provenance; published pooled digits are not inputs.
    theirs = comp.get('held_per_trial_inputs') or []
    inputs = [envelope.trial_input(r) for r in envelope.primary(review).get('trials', [])]
    rows = replay([theirs or None, None, inputs, inputs], env['scale'], None, root=root,
                  reason='held text names PM/Hartung-Knapp but not its variance floor; exact comparator replay is unidentified')
    return {'schema_version': 1, 'class': 'TRANSFORMATION', 'slug': review['slug'],
            'input_set_version': env['input_set_version'], 'comparator': comp.get('name'),
            'requested_comparator': ('Hasebe 2025: COMPARATOR NOT HELD' if not re.search(r'Hasebe.{0,80}2025|2025.{0,80}Hasebe', text, re.S) else 'Hasebe 2025 mentioned; identity requires resolution') if review['slug'] == envelope.topic_id('incretin_cardiovascular') else ('held comparator used' if text else 'COMPARATOR NOT HELD'),
            'held_source': held, 'method': method, 'comparator_truth': truth,
            'trial_set_relation': relation, 'reported_summary': reported,
            'coincidence': 'equal rounded pooled effects from different trial sets do not establish replication; numerical coincidence unverified while replay is unavailable',
            'rows': rows}


def render(obj):
    rows = ''.join('<tr><td>' + str(r['step']) + ': ' + escape(r['choice']) + '</td><td>' +
                   escape(r['attribution']) + '</td><td>' + escape(json.dumps(r['result'] if r['computable'] else r['reason'], ensure_ascii=False, sort_keys=True)) +
                   '</td><td>' + escape(str(r['delta_log_effect'])) + '</td></tr>' for r in obj['rows'])
    return '<section id="gs-decomposer"><h3>Disagreement decomposer</h3><p>' + escape(str(obj['comparator']) + '; ' + obj['requested_comparator']) + '</p><p>' + escape(obj['coincidence']) + '</p><table><tr><th>Replay step</th><th>Attribution</th><th>Result</th><th>Delta log effect (null = unidentified)</th></tr>' + rows + '</table></section>'
