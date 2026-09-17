"""Deterministic manuscript rendered from registered typed objects.

Numerical synthesis and forest labels require source-backed effect inputs;
recorded judgements remain labelled judgements and interpretations show an
alternative. The legacy numeral gate remains a second, narrower check.
"""
from __future__ import annotations

import html as _html

from harness import identity as _identity_mod
from . import claimgraph


def _e(s):
    return _html.escape(str(s)) if s is not None else ""


def _fmt(x, nd=2):
    if x is None:
        return ""
    try:
        return f"{round(float(x), nd):g}"
    except (TypeError, ValueError):
        return str(x)


def _unit_label(unit):
    if unit == "prespecified_subgroup":
        return "pre-specified subgroup"
    if unit == "post_hoc_subgroup":
        return "post-hoc subgroup"
    return "trial"


def _evidence_unit_summary(outcome):
    trials = outcome.get("trials") or []
    if not trials or all((t.get("evidence_unit") or "trial") == "trial" for t in trials):
        return None
    counts = {}
    for t in trials:
        unit = t.get("evidence_unit") or "trial"
        counts[unit] = counts.get(unit, 0) + 1
    bits = []
    if counts.get("trial"):
        bits.append(f"{counts['trial']} trial" + ("" if counts["trial"] == 1 else "s"))
    for unit in ("prespecified_subgroup", "post_hoc_subgroup"):
        group = [t for t in trials if t.get("evidence_unit") == unit]
        if not group:
            continue
        details = sorted({t.get("evidence_unit_detail") for t in group if t.get("evidence_unit_detail")})
        if len(group) == 1 and details:
            bits.append(f"1 {_unit_label(unit)} of {details[0]}")
        else:
            bits.append(f"{len(group)} {_unit_label(unit)}" + ("" if len(group) == 1 else "s"))
    return " + ".join(bits)


def _k_phrase(outcome):
    k = (outcome.get("result") or {}).get("k")
    eu = _evidence_unit_summary(outcome)
    return f"k = {k} ({eu})" if eu and k is not None else f"{k} trials"


def _forest_k_phrase(outcome):
    k = (outcome.get("result") or {}).get("k")
    eu = _evidence_unit_summary(outcome)
    return f"k = {k} ({eu})" if eu and k is not None else f"k={k}"


def _primary(review):
    return next((o for o in review.get("outcomes", []) if o.get("primary")), None)


def object_numerals(review):
    """The set of numeral strings the manuscript is ALLOWED to print — every one derived from a committed
    object field. The gate limb checks the rendered manuscript's risky numerals against this set."""
    out = set()

    def add(v, nd=2):
        if isinstance(v, bool) or v is None:
            return
        if isinstance(v, int):
            out.add(str(v))
        elif isinstance(v, float):
            out.add(str(v))  # FACT rows preserve the recorded precision.
            out.add(str(abs(v)))  # The legacy gate tokenises magnitudes.
            out.add(f"{round(v, nd):g}")
            out.add(f"{round(v, 1):g}")
            out.add(f"{abs(round(v, nd)):g}")

    prim = _primary(review) or {}
    res = prim.get("result") or {}
    for k in ("k", "estimate", "ci_low", "ci_high", "tau2", "pi_low", "pi_high"):
        add(res.get(k))
    # every pooled trial's values
    for o in review.get("outcomes", []):
        for t in o.get("trials", []):
            for k in ("effect", "ci_low", "ci_high", "ai", "n1i", "ci", "n2i", "e1i", "t1i", "e2i", "t2i",
                      "mean1", "sd1", "nc1", "mean2", "sd2", "nc2"):
                add(t.get(k))
        r2 = o.get("result") or {}
        for k in ("k", "estimate", "ci_low", "ci_high"):
            add(r2.get(k))
    # counts: pooled k, declared-absent count, screening totals
    scr = review.get("screening") or {}
    add(len(scr.get("records", []) or []))
    for o in review.get("outcomes", []):
        add(len(o.get("trials", []) or []))
        add(len(o.get("declared_absent_trials", []) or []))
        states = [row.get('state') or row.get('reason_code') or 'UNCLASSIFIED'
                  for row in o.get('declared_absent_trials') or []]
        for state in set(states):
            add(states.count(state))
        if review.get("publication_units"):
            counts = _identity_mod.outcome_counts(o)
            add(counts["pooled"].get("trials"))
            add(counts["pooled"].get("publications"))
            add(counts["absent"].get("trials"))
            add(counts["absent"].get("publications"))
        units = {}
        for t in o.get("trials", []) or []:
            unit = t.get("evidence_unit") or "trial"
            units[unit] = units.get(unit, 0) + 1
        for v in units.values():
            add(v)
    # grade downgrades, rob coverage
    g = review.get("grade") or {}
    add(g.get("downgrades"))
    s = review.get("rob_sensitivity") or {}
    add(s.get("n_trials"))
    add(s.get("n_rob_rated"))
    for stratum in ("full", "drop_high", "low_only"):
        st = s.get(stratum) or {}
        for k in ("k", "estimate", "ci_low", "ci_high"):
            add(st.get(k))
    # the confidence/prediction-interval level is a fixed statistical constant the manuscript states
    out.add("95")
    out.add("12.71")
    # numerals present in committed TEXT fields the manuscript quotes verbatim (title, question, and each
    # outcome's timepoint/population) are object-sourced, not invented (e.g. 'semaglutide 2.4 mg', 'Week 68')
    import re as _re
    texts = [review.get("title") or "", review.get("question") or ""]
    for o in review.get("outcomes", []):
        texts += [str(o.get("timepoint") or ""), str(o.get("population") or ""), str(o.get("name") or "")]
        # Follow-up values quoted by the compatibility limitation come from
        # the per-trial admission objects, including retrospective sensitivity.
        for trial in o.get("trials", []):
            for dimension in ("follow_up_window", "endpoint_definition"):
                cell = (trial.get("admission") or {}).get(dimension) or {}
                texts.append(str(cell.get("trial_value") or ""))
        for trial in o.get('trials') or []:
            texts += [str(trial.get('id') or ''), str(trial.get('label') or '')]
    for txt in texts:
        for m in _re.findall(r"\d+(?:\.\d+)?", txt):
            out.add(m)
            if "." not in m:
                continue
            out.add(f"{float(m):g}")
    # Recorded GRADE bases are now visible judgements, including the quoted
    # source numbers. Permit their actual input tokens, never rendered output.
    for domain in (g.get('domains') or {}).values():
        for token in _re.findall(r"\d+(?:\.\d+)?", str(domain.get('basis') or '')):
            out.add(token)
            out.add(f"{float(token):g}")
    from . import risk_prose
    rob_rows = risk_prose._rows(review)
    overall_states = risk_prose._states(rob_rows)
    for state in set(overall_states):
        add(overall_states.count(state))
    levels = [str((entry.get('domains') or {}).get('D3_missing_outcome_data', {}).get('level') or 'not assessed')
              for _, entry in rob_rows]
    add(sum(level.lower() in ('not assessed', 'unassessed', 'not_assessed') for level in levels))
    screen_states = [str(row.get('decision') or row.get('final_decision') or 'unclassified')
                     for row in scr.get('records') or []]
    for state in set(screen_states):
        add(screen_states.count(state))
    return out


def _forest(review, writer=None):
    """A minimal object-derived forest plot (SVG) of the primary outcome: one row per pooled trial with its
    effect and CI, and a diamond for the pooled estimate. Ratio scales use a log x-axis with null at 1."""
    prim = _primary(review)
    if not prim or not prim.get("trials"):
        return ""
    res = prim.get("result") or {}
    if res.get("suppressed_incompatible"):
        return ""  # FAIL CLOSED (audit 23): no forest for an incompatible (suppressed) pool
    import math
    scale = (res.get("scale") or prim.get("estimand") or "").upper()
    is_ratio = scale in ("HR", "RR", "OR", "IRR") or scale.startswith("MIXED")
    rows = []
    for t in prim["trials"]:
        e, lo, hi = t.get("effect"), t.get("ci_low"), t.get("ci_high")
        if e is None and t.get("ai") is not None:
            # 2x2 -> RR for display only (not a stored number; skip if incomputable)
            try:
                a, n1, c, n2 = t["ai"], t["n1i"], t["ci"], t["n2i"]
                e = (a / n1) / (c / n2) if c and n2 and n1 else None
            except (TypeError, ZeroDivisionError):
                e = None
        if e is None and t.get("mean1") is not None:
            e = t["mean1"] - t["mean2"]
            lo = hi = None
        if e is not None:
            rows.append((str(t.get("label")), e, lo, hi))
    if not rows:
        return ""
    pooled = (res.get("estimate"), res.get("ci_low"), res.get("ci_high"))
    xs = [v for _, e, lo, hi in rows for v in (e, lo, hi) if v is not None]
    if pooled[0] is not None:
        xs += [v for v in pooled if v is not None]
    if is_ratio:
        xs = [x for x in xs if x and x > 0]
        if not xs:
            return ""
        tx = [math.log(x) for x in xs]
    else:
        tx = xs
    lo_x, hi_x = min(tx), max(tx)
    span = (hi_x - lo_x) or 1.0
    W, rowh, padL, padR, padT = 640, 22, 190, 60, 30
    if writer is not None:
        W, padL, padR = 1100, 340, 310
    H = padT + rowh * (len(rows) + 2) + 20

    def xpix(v):
        if v is None:
            return None
        vv = math.log(v) if is_ratio else v
        return padL + (vv - lo_x) / span * (W - padL - padR)

    null = 1.0 if is_ratio else 0.0
    parts = [f"<svg viewBox='0 0 {W} {H}' role='img' aria-label='Forest plot of the primary outcome' "
             f"style='max-width:100%;height:auto;font:12px system-ui'>"]
    nx = xpix(null)
    if nx is not None and lo_x <= (math.log(null) if is_ratio else null) <= hi_x:
        parts.append(f"<line x1='{nx:.1f}' y1='{padT-6}' x2='{nx:.1f}' y2='{H-24}' stroke='#b0bec5' stroke-dasharray='3 3'/>")
    y = padT
    for index, (lab, e, lo, hi) in enumerate(rows):
        if writer is not None:
            trial = prim['trials'][index]
            source_row = dict(trial, scale=trial.get('scale') or prim.get('estimand'))
            source_ref = 'fact-' + claimgraph._sha(source_row)[:16]
        cx = xpix(e)
        if lo is not None and hi is not None:
            xl, xh = xpix(lo), xpix(hi)
            parts.append(f"<line x1='{xl:.1f}' y1='{y:.1f}' x2='{xh:.1f}' y2='{y:.1f}' stroke='#37474f'/>")
        parts.append(f"<rect x='{cx-3:.1f}' y='{y-3:.1f}' width='6' height='6' fill='#1d3b4d'/>")
        label_text = (_e(lab) if writer is None else writer.effect_display(
            'forest-label-' + str(index), source_ref, 'label'))
        parts.append(f"<text x='6' y='{y+4:.1f}' fill='#12232e'>{label_text}</text>")
        val = f"{_fmt(e)}" + (f" [{_fmt(lo)}, {_fmt(hi)}]" if lo is not None else "")
        value_text = (_e(val) if writer is None else writer.effect_display(
            'forest-point-' + str(index), source_ref, 'point'))
        parts.append(f"<text x='{W-padR+6}' y='{y+4:.1f}' fill='#37474f'>{value_text}</text>")
        y += rowh
    # pooled diamond
    if pooled[0] is not None and pooled[1] is not None:
        y += rowh // 2
        xc, xl, xh = xpix(pooled[0]), xpix(pooled[1]), xpix(pooled[2])
        parts.append(f"<polygon points='{xl:.1f},{y:.1f} {xc:.1f},{y-6:.1f} {xh:.1f},{y:.1f} {xc:.1f},{y+6:.1f}' fill='#b31412'/>")
        pool_label = f'Pooled ({_forest_k_phrase(prim)})'
        if writer is not None:
            pool_label = writer.effect_display('forest-pooled-label', 'manuscript-result', 'label')
        else:
            pool_label = _e(pool_label)
        parts.append(f"<text x='6' y='{y+4:.1f}' fill='#b31412' font-weight='600'>{pool_label}</text>")
        pv = f"{_fmt(pooled[0])} [{_fmt(pooled[1])}, {_fmt(pooled[2])}]"
        if writer is not None:
            pv = writer.effect_display('forest-pooled-point', 'manuscript-result', 'point')
        else:
            pv = _e(pv)
        parts.append(f"<text x='{W-padR+6}' y='{y+4:.1f}' fill='#b31412' font-weight='600'>{pv}</text>")
    axis = f"{scale or 'effect'} ({'log scale, null=1' if is_ratio else 'null=0'})"
    if writer is not None:
        axis = writer.svg(writer.computation('forest-axis', {'label': axis}, unit='forest-label'))
    else:
        axis = _e(axis)
    parts.append(f"<text x='{padL}' y='{H-6}' fill='#78909c'>{axis}</text></svg>")
    return "".join(parts)


def compute(unit, inputs):
    """Named prose transformations over structured records, never rendered text."""
    if unit == 'question':
        return 'Recorded review question: ' + str(inputs.get('question') or 'not recorded')
    if unit == 'screening':
        records = inputs.get('records') or []
        states = [str(r.get('decision') or r.get('final_decision') or 'unclassified') for r in records]
        counts = {s: states.count(s) for s in sorted(set(states))}
        return f'Screening records: {len(records)}; recorded per-item decisions: {counts}.'
    if unit == 'search':
        states = inputs.get('source_status') or {}
        return 'Recorded retrieval adapter states: ' + '; '.join(
            f'{key}: {value}' for key, value in sorted(states.items())) + '.'
    if unit == 'registration':
        import re
        text = inputs.get('protocol_text') or ''
        retrospective = bool(re.search(r'\bNCT\d{8}\b|\bPMID[:\s]|\b\d{7,8}\b|hazard ratio|95%\s*CI|odds ratio|rate ratio', text))
        pre = inputs.get('preregistration') or {}
        if pre.get('prospective') and not retrospective:
            return ('The recorded protocol-only commit is ' + str(pre.get('sha') or '')[:12]
                    + '; the registration record marks it prospective.')
        return ('Prospective registration is not demonstrated by the recorded protocol/history. '
                'Recorded build SHA: ' + str(pre.get('build_sha') or inputs.get('sha') or '')[:12] + '.')
    if unit == 'availability':
        return ('The committed cache and code are the replay inputs: python scripts/build_topic.py '
                + str(inputs.get('slug') or '') + '. Recorded protocol SHA: '
                + str(inputs.get('sha') or '')[:12] + '. RETRACTED (round-2): Protocol-SHA byte-for-byte reproduction is not claimed; mutable post-registration inputs are also required.')
    if unit == 'evidence-units':
        states = [t.get('evidence_unit') or 'trial' for t in inputs]
        counts = {s: states.count(s) for s in sorted(set(states))}
        return f'Primary pooled evidence units: {counts}.'
    if unit == 'forest-label':
        return str(inputs['label'])
    if unit == 'forest-point':
        e, lo, hi = inputs['effect'], inputs.get('ci_low'), inputs.get('ci_high')
        return _fmt(e) + (f' [{_fmt(lo)}, {_fmt(hi)}]' if lo is not None else '')
    raise ValueError('unknown manuscript computation: ' + unit)


def register(graph, review):
    """Register all manuscript units independently of the HTML consumer."""
    from .section_prose import Writer, register_pool
    from . import risk_prose
    w = Writer(graph, 'manuscript')
    parts = []

    def paragraph(value):
        parts.append('<p>' + value + '</p>')

    paragraph(w.judgement('generation',
        'This manuscript is generated from the review object. Registered transformations and recorded judgements are labelled separately.',
        {'rule_id': 'harness.manuscript:typed-rendering', 'implementation': 'harness/manuscript.py'}))
    parts.append('<h4>Abstract</h4><h5>Question</h5>')
    paragraph(w.computation('question', {'question': review.get('question')}))
    parts.append('<h5>Methods</h5>')
    pre = (review.get('reproduction') or {}).get('preregistration') or {}
    protocol = review.get('protocol') or {}
    paragraph(w.computation('registration', {'preregistration': pre, 'sha': protocol.get('sha'),
                                            'protocol_text': protocol.get('text')}))
    paragraph(w.computation('search', {'source_status': (review.get('search') or {}).get('source_status')}))
    paragraph(w.interpretation('search-retraction',
        'We retract the earlier blanket claim of registry-first or systematic-search completeness. It remains a retracted claim; replay of known-item retrieval does not establish discovery completeness.',
        'A documented independent search with a measured reference universe could support a narrower coverage claim.'))
    paragraph(w.computation('screening', {'records': (review.get('screening') or {}).get('records')}))
    if 'fact-coverage' in graph.objects:
        paragraph(w.ref('fact-coverage'))
    prim = _primary(review)
    parts.append('<h5>Results</h5>')
    if not prim:
        paragraph(w.judgement('no-primary', 'No primary outcome is recorded.',
                             {'rule_id': 'primary-flag-required', 'source_field': 'outcomes'}, owed=True))
    else:
        res = prim.get('result') or {}
        trials = prim.get('trials') or []
        paragraph(w.computation('evidence-units', trials))
        if res.get('suppressed_incompatible') or res.get('pool_refused'):
            paragraph(w.judgement('result-refused',
                ('INCOMPATIBLE estimand classes: no pooled effect is reported.' if res.get('suppressed_incompatible')
                 else 'The recorded pooling rule refused a pooled effect; trial estimates remain individually reportable.'),
                {'rule_id': 'respect-pooling-refusal', 'source_field': 'outcomes.primary.result',
                 'recorded_refusal': res.get('pool_refused') or res.get('estmeasure')}, owed=True))
        elif trials and not res.get('pooled_ci_refused'):
            paragraph(register_pool(graph, 'manuscript-result', trials, res.get('scale') or prim.get('estimand'),
                                    'Primary outcome'))
        else:
            paragraph(w.judgement('result-unavailable',
                'No pooled interval is served for this recorded outcome state; this does not establish outcome absence.',
                {'rule_id': 'no-interval-without-renderable-pool', 'source_field': 'outcomes.primary.result',
                 'recorded_state': res}, owed=True))
        mid, member = claimgraph.membership_object(prim)
        if mid not in graph.objects:
            graph.add(mid, 'TRANSFORMATION', **member)
        if prim.get('declared_absent_trials'):
            paragraph(w.ref(mid))
    parts.append('<h5>Certainty</h5>')
    g = review.get('grade') or {}
    if g.get('certainty') == 'not_rateable':
        paragraph(w.judgement('certainty-refused',
            'Overall GRADE certainty is not rateable. Recorded reason: ' + str(g.get('not_rateable_reason') or 'not supplied'),
            {'rule_id': 'no-certainty-for-refused-effect-object', 'source_field': 'grade'}, owed=True))
    elif g:
        paragraph(w.ref('grade-certainty'))
        paragraph(w.ref('grade-downgrades'))
    parts.append('<h4>Methods</h4>')
    paragraph(w.judgement('methods',
        'The reported-effect transformation uses random effects (Paule-Mandel with a Hartung-Knapp interval). '
        'Held source evidence is required for each effect input; missing evidence refuses the transformation.',
        {'rule_id': 'harness.claimgraph:reported_effect_pool', 'implementation': 'harness/claimgraph.py'}))
    paragraph(w.interpretation('replay',
        'Deterministic replay establishes consistency of the committed inputs and computation; it does not validate search completeness or extraction.',
        'A reproducible result can still change when missing evidence is recovered or an extraction is corrected.'))
    parts.append('<h4>Results</h4>')
    if prim:
        if 'manuscript-result' in graph.objects:
            try:
                # The graphic uses the same freshly computed result as the prose.
                # No stale stored aggregate controls the diamond or its label.
                fresh = graph.recompute('manuscript-result')
                import copy
                graphical = copy.deepcopy(review)
                _primary(graphical)['result'] = dict(fresh, scale=prim.get('estimand'))
                parts.append('<figure>' + _forest(graphical, w) + '</figure>')
            except (ValueError, KeyError, TypeError, ZeroDivisionError):
                pass  # The source/pool refusal is already rendered in the abstract.
        rows = []
        for trial in prim.get('trials') or []:
            row = dict(trial, scale=trial.get('scale') or prim.get('estimand'))
            cid = 'fact-' + claimgraph._sha(row)[:16]
            if cid not in graph.objects:
                graph.add(cid, 'FACT', row=row)
            rows.append('<tr><td>' + w.ref(cid) + '</td></tr>')
        if rows:
            parts.append('<table class="arms"><tr><th>Source estimate</th></tr>' + ''.join(rows) + '</table>')
    parts.append('<h4>Risk-of-bias sensitivity</h4>')
    # The shared RoB registry supplies exactly the same state counts everywhere.
    if 'risk-overall-states' not in graph.objects:
        risk_prose.register(graph, review)
    paragraph(w.ref('risk-overall-states'))
    paragraph(w.ref('risk-d3-states'))
    parts.append('<h4>Limitations</h4>')
    paragraph(w.interpretation('limitations',
        'Machine-derived domain judgements support an auditable partial assessment; they are not a formal human risk-of-bias assessment.',
        'Human review of the held sources may revise a recorded domain judgement or identify information missing from the machine inputs.'))
    if g:
        for name in claimgraph.GRADE_DOMAINS:
            owned = 'risk-grade-domain-' + name
            paragraph(w.ref(owned if owned in graph.objects else 'grade-domain-' + name))
    parts.append('<h4>Data availability &amp; reproduction</h4>')
    paragraph(w.computation('availability', {'slug': review.get('slug'), 'sha': protocol.get('sha')}))
    return ''.join(parts)


@claimgraph._provenance_batch()
def render(review, neutral=False):
    from .section_prose import Writer
    local = claimgraph.review_graph(review, include_sections=False)
    document = register(local, review)
    return Writer(local, 'manuscript').finish(document)
