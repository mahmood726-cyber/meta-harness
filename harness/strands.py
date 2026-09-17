"""Topic-declared synthesis strands; refusals are data, never pool members."""
import copy
from html import escape

from . import claimgraph, effect_type, verified_source
from .synth import Study, pool


def declarations(config):
    rows = config.get('strands') or []
    if (not rows or sum(r.get('primary') is True for r in rows) != 1
            or len({r['id'] for r in rows}) != len(rows)):
        raise ValueError('Strands require unique ids and exactly one primary')
    for row in rows:
        rule = row.get('membership_rule')
        if (not isinstance(rule, dict) or set(rule) - {'include_ids', 'exclude_ids'}
                or any(not isinstance(v, list) for v in rule.values())):
            raise ValueError('Invalid strand membership_rule')
    return rows


def selected(row, declaration):
    key = claimgraph.trial_key(row)
    rule = declaration['membership_rule']
    return (('include_ids' not in rule or key in rule['include_ids'])
            and key not in rule.get('exclude_ids', []))


def build(config, candidates, target, decisions, records=None, coercions=()):
    eligibility = {claimgraph.trial_key(d): d for d in decisions}
    typed, admitted, rejected = [], [], []
    for candidate in candidates:
        row = copy.deepcopy(candidate)
        key = claimgraph.trial_key(row)
        row.update(pmid=key, trial=row.get('label') or row.get('trial') or key)
        decision = eligibility.get(key, {})
        reason = verified_source.refusal(row)
        if reason:
            row.update(status='UNVERIFIED_FACT/REFUSED', axis='source', reason=reason)
        elif decision.get('decision') != 'include':
            row.update(status='REFUSED', axis='eligibility',
                       reason=decision.get('reason') or 'No include decision')
        else:
            kept, refused, effects = effect_type.type_rows([row], target, records, coercions)
            typed.extend(effects)
            if kept:
                admitted.extend(kept)
                continue
            row = refused[0]
            row.update(status='REFUSED', axis=row['unification'].get('axis_name'),
                       axis_number=row['unification'].get('axis'))
        rejected.append(row)
    doc = {'slug': config['slug'], 'generated_from_declarations': True,
           'primary_strand': next(d['id'] for d in declarations(config) if d['primary']),
           'strands': [], 'additional_effect_types': typed,
           'sensitivity_values': copy.deepcopy(config.get('strand_sensitivity_values', []))}
    for row in doc['sensitivity_values']:
        row['pooled'] = False
        reason = verified_source.refusal(row)
        if reason:
            row.update(status='UNVERIFIED_FACT/REFUSED', reason=reason)
    for declaration in declarations(config):
        members = [r for r in admitted if selected(r, declaration)]
        refused = [r for r in rejected if selected(r, declaration)]
        result = None
        if members:
            scales = {r['scale'] for r in members}
            if len(scales) != 1:
                raise ValueError('Strand mixes effect measures')
            scale = next(iter(scales))
            fields = set(Study.__dataclass_fields__) - {'label', 'measure'}
            studies = [Study(label=r['trial'], measure=scale,
                             **{k: r[k] for k in fields if k in r}) for r in members]
            pooled = pool(studies, scale=scale)
            result = {k: getattr(pooled, k) for k in
                      ('k', 'estimate', 'ci_low', 'ci_high', 'tau2', 'pi_low', 'pi_high', 'ci_provenance')}
            result.update(effect=pooled.estimate, scale=scale,
                          crosses_null=pooled.ci_low <= (0 if scale in ('MD', 'SMD', 'RD') else 1) <= pooled.ci_high)
        doc['strands'].append(dict(strand=declaration['id'], name=declaration['label'],
            primary=declaration['primary'], membership_rule=declaration['membership_rule'],
            effect_measure=(result or {}).get('scale'),
            members=members, refused=refused, k=len(members), pool=result,
            status='POOLED' if members else 'REFUSED',
            reason=None if members else 'No admitted source-backed typed effects'))
    return doc


def render(review):
    from .page import render_strands_section
    doc = review['strands']
    out = [render_strands_section(doc)]
    for strand in doc['strands']:
        out.append('<h4>' + escape(strand['name']) + ': membership and refusals</h4>')
        out.append('<table><tr><th>Trial</th><th>Status</th><th>Axis</th><th>Reason</th></tr>')
        for row in strand['members'] + strand['refused']:
            out.append('<tr>' + ''.join('<td>' + escape(str(value or '')) + '</td>' for value in
                       (row['trial'], row.get('status', 'POOLED'), row.get('axis'), row.get('reason'))) + '</tr>')
        out.append('</table>')
    out.append('<h4>Sensitivity values (never pooled)</h4>')
    for row in doc.get('sensitivity_values', []):
        graph = claimgraph.ClaimGraph()
        cid = row.get('claim_id', 'sensitivity-' + claimgraph.trial_key(row))
        graph.add(cid, 'FACT', row=row)
        out.append(graph.render(cid))
    return ''.join(out)
