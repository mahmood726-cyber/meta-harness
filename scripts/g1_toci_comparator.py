"""Offline WHO REACT table audit. No served data, registry or git mutations.

The lane verifier adds held HTML/table bindings; it is NOT the unmodified
proposal_gate.verify. Both verdicts are emitted, including native refusals.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from harness import identity_join as ij, proposal_gate as gate, meta_match
from harness import recovery_map, trial_mortality_extract as tm
from harness.trial_family import load_registry

SLUG = 'tocilizumab-covid19-mortality'
HELD = 'evidence/acquisition_cascade/held/WHO-REACT/PMC8261689.local.html'


def one(items, reason):
    if len(items) != 1:
        raise ValueError(reason)
    return items[0]


def text(node):
    return gate.flat(node.get_text(' ', strip=True))


def normalized(raw):
    return text(gate.parse_html(raw))


def extract(raw):
    """Bind Table 1 rowspans to drug sections, retaining individual dose arms."""
    soup = gate.parse_html(raw)
    table = one([t for t in soup.find_all('table') if all(s in text(t) for s in
                ('Trial registration No.', 'Treatment group', 'No. of patients'))],
                'REFUSED_TABLE1_AMBIGUOUS')
    trs = table.find_all('tr')
    section, rows, excluded = None, [], []
    i = 0
    while i < len(trs):
        cells = trs[i].find_all(['td', 'th'], recursive=False)
        if len(cells) == 1:
            section = text(cells[0])
            i += 1
            continue
        if len(cells) < 4 or cells[0].name == 'th' or int(cells[0].get('rowspan', 1)) < 2:
            i += 1
            continue
        label, registration = text(cells[0]), text(cells[1])
        width = int(cells[0]['rowspan'])
        if int(cells[1].get('rowspan', 1)) != width or i + width > len(trs):
            raise ValueError('REFUSED_ROWSPAN:' + label)
        arms, spans = [], []
        for offset in range(width):
            tr = trs[i + offset]
            cs = tr.find_all(['td', 'th'], recursive=False)
            start = 2 if offset == 0 else 0
            if len(cs) <= start + 1:
                raise ValueError('REFUSED_ARM_SCHEMA:' + label)
            treatment, n = text(cs[start]), text(cs[start + 1])
            if not re.fullmatch(r'[1-9]\d*', n):
                raise ValueError('REFUSED_PATIENT_COUNT:' + label + ':' + n)
            role = ('intervention' if re.fullmatch(r'Anti–IL-6(?: \([^)]*\))?', treatment)
                    else 'control' if re.fullmatch(r'(?:Placebo \+ usual care|Usual care)(?: [a-z])?', treatment)
                    else 'unresolved')
            arms.append(dict(treatment=treatment, n=int(n), role=role,
                             span=text(tr), n_span=n, treatment_span=treatment))
            spans.append(text(tr))
        i += width
        if section != 'Tocilizumab':
            excluded.append(dict(label=label, section=section, reason='NOT_TOCILIZUMAB_USUAL_CARE_SECTION'))
            continue
        if any(a['role'] == 'unresolved' for a in arms) or sum(a['role']=='control' for a in arms) != 1:
            raise ValueError('REFUSED_ARM_ROLES:' + label)
        nct = registration if re.fullmatch(r'NCT\d{8}', registration) else None
        if nct is None and not registration.startswith('EU-CTR '):
            raise ValueError('REFUSED_REGISTRATION:' + label)
        rows.append(dict(label=label, registration=nct, registration_as_printed=registration,
                         drug=section, arms=arms, span=' '.join(spans), zero_death=None,
                         zero_death_span=None))
    if not rows or len({r['label'] for r in rows}) != len(rows):
        raise ValueError('REFUSED_EMPTY_OR_DUPLICATE_TRIAL_TABLE')
    paragraphs = [text(p) for p in soup.find_all('p')]
    zero = one([p for p in paragraphs if re.search(r'trials recorded no deaths by 28 days', p)],
               'REFUSED_ZERO_DEATH_STATEMENT')
    zero = zero[zero.index('Three trials recorded no deaths'):]
    zero_ids = set(re.findall(r'\bNCT\d{8}\b', zero))
    if not zero_ids or not zero_ids <= {r['registration'] for r in rows}:
        raise ValueError('REFUSED_ZERO_DEATH_IDENTITY')
    for row in rows:
        if row['registration'] in zero_ids:
            row.update(zero_death='NO_DEATHS_BOTH_ARMS_28_DAYS', zero_death_span=zero)
    population = one([p for p in paragraphs if 'we restricted the analyses to trial participants with outcomes recorded.' in p],
                     'REFUSED_POPULATION_UNBOUND')
    population = population[population.index('Because outcome data were generally complete'):]
    pooled = one([p for p in paragraphs if re.match(r'In \d+ trials that randomized .*? to tocilizumab', p)],
                 'REFUSED_TOCILIZUMAB_K_UNBOUND')
    k = int(re.match(r'In (\d+) trials', pooled)[1])
    pooled_span = pooled.split(' This corresponds')[0]
    effect = one([m.group() for p in paragraphs for m in re.finditer(
        r'The corresponding summary ORs were .*? for tocilizumab', p)], 'REFUSED_TOCILIZUMAB_OR_UNBOUND')
    estimate = gate.parse_estimate(effect)
    if not estimate or len(rows) != k:
        raise ValueError('REFUSED_TOCILIZUMAB_TABLE_K_OR_ESTIMATE')
    full = text(soup)
    scope = one(sorted(set(re.findall(r'all-cause mortality at 28 days after randomization', full))),
                'REFUSED_PRIMARY_SCOPE')
    pmid = one([m['content'] for m in soup.find_all('meta') if m.get('name') == 'citation_pmid'], 'REFUSED_COMPARATOR_PMID')
    return dict(rows=rows, excluded=excluded, k=k, k_span=pooled_span, effect=estimate,
                effect_span=effect, population='OUTCOMES_RECORDED', population_span=population,
                scope_span=scope, pmid=pmid, source=HELD, sha256=hashlib.sha256(raw).hexdigest())


def proposal(table, raw):
    doc = normalized(raw)
    # k and the abstract's explicit labelled OR inhabit one contiguous parent.
    a, b = sorted([doc.index(table['effect_span']), doc.index(table['k_span'])])
    end = max(doc.index(table[s]) + len(table[s]) for s in ('effect_span','k_span'))
    pooled = dict(table['effect'], k=table['k'], span=doc[a:end],
                  field_spans={k:table['effect_span'] for k in gate.POOLED if k != 'k'})
    pooled['field_spans']['k'] = table['k_span']
    trials = []
    for row in table['rows']:
        inter = [a for a in row['arms'] if a['role']=='intervention']
        control = one([a for a in row['arms'] if a['role']=='control'], 'REFUSED_CONTROL')
        item = dict.fromkeys(gate.TRIAL)
        item.update(label=row['label'], registration=row['registration'],
                    n_1=inter[0]['n'] if len(inter)==1 else None, n_2=control['n'], span=row['span'])
        item['field_spans'] = dict(label=row['label'], registration=row['registration'] or '')
        item['field_spans']['n_2'] = control['span']
        if len(inter)==1:
            item['field_spans']['n_1'] = inter[0]['span']
        trials.append(item)
    return dict(slug=SLUG, comparator_pmid=table['pmid'], document_ref=HELD,
                document_sha256=table['sha256'], proposed_by='G1TOCI deterministic held HTML extractor',
                primary_scope=dict(outcome_as_printed=table['scope_span'], timepoint_as_printed='28 days',
                                   measure_as_printed=None, span=table['scope_span']),
                pooled=pooled, trials=trials, trial_set_scope='selected_outcome', trial_set_complete=False,
                scope_note='WHO tocilizumab 28-day mortality; Table 1 arm sizes, not forest-image death counts. '
                           'Requires held-HTML gate integration. Duplicate registrations are distinct cohorts. '
                           'Individual dose arms and zero-death types are in comparator_table.json.',
                not_found=['PER_TRIAL_FOREST_IMAGE_DEATH_COUNTS_NOT_TEXT',
                           'MULTIDOSE_COMBINED_N_NOT_PRINTED: n_1 is null; individual arms retained',
                           'NATIVE_GATE_HELD_HTML_AND_TABLE_NUMBER_BINDING_NOT_IMPLEMENTED'])


def verify_held(p, raw):
    """Fail-closed proposed extension, no monkeypatch or forged cache panel.

    Lexical checks use identical HTML text normalization. Typed arm Ns must
    equal a fresh structural extraction; all other fields use native _reparse.
    """
    reason = gate._schema(p)
    if reason:
        return dict(status='rejected', reason=reason)
    table = extract(raw)
    expected = proposal(table, raw)
    if any(p.get(k) != expected[k] for k in ('slug','comparator_pmid','document_ref','document_sha256')):
        return dict(status='rejected', reason='REFUSED_SOURCE_IDENTITY_OR_HASH')
    doc = normalized(raw)
    groups = [('primary_scope',gate.SCOPE), ('pooled',gate.POOLED)]
    fields = []
    pairs = [(name,p[name],expected[name],keys) for name,keys in groups]
    if len(p['trials']) != len(expected['trials']):
        return dict(status='rejected', reason='REFUSED_TRIAL_TABLE_MEMBERSHIP')
    pairs += [(f'trials.{i}',r,expected['trials'][i],gate.TRIAL) for i,r in enumerate(p['trials'])]
    for prefix, item, exp, keys in pairs:
        parent = gate.flat(item['span'])
        for key in keys:
            value = item[key]
            span = gate.flat(item.get('field_spans',{}).get(key,item['span']))
            why = None
            if value is not None:
                if not parent or parent not in doc or not span or span not in parent:
                    why = 'REFUSED_SPAN_NOT_HELD'
                elif gate.RELAYED.search(parent):
                    why = 'REFUSED_RELAYED_NOT_DATA'
                elif value != exp[key] or span != gate.flat(exp.get('field_spans',{}).get(key,exp['span'])):
                    why = 'REFUSED_TYPED_SOURCE_BINDING:' + key
                elif key not in ('n_1','n_2'):
                    why = gate._reparse(key,value,span)
                elif type(value) is not int or value <= 0:
                    why = 'REFUSED_COUNT_TYPE_OR_RANGE'
            elif exp[key] is not None:
                why = 'REFUSED_REQUIRED_FIELD_DROPPED:' + key
            fields.append(dict(path=prefix+'.'+key,status='rejected' if why else 'not_proposed' if value is None else 'accepted',reason=why))
    return dict(status='rejected' if any(f['status']=='rejected' for f in fields) else 'accepted',
                verifier='LANE_HELD_HTML_EXTENSION_NOT_NATIVE_GATE',fields=fields)


def resolution_module(root):
    spec = importlib.util.spec_from_file_location('harness._g1_toci_resolution',
        root/'lanes/TOCI2/harness/toci_resolution.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_registration(raw):
    """Own article registration paragraphs, excluding citation/reference lists."""
    if raw.lstrip().startswith(b'<?xml'):
        article = ET.fromstring(raw)
        paragraphs = [gate.flat(' '.join(p.itertext())) for section in
                      article.findall('.//body') + article.findall('.//article-meta/abstract')
                      for p in section.iter('p')]
    else:
        soup = gate.parse_html(raw)
        paragraphs = [text(p) for p in soup.find_all('p') if not p.find_parent(['ref-list'])]
    spans = [s for s in paragraphs if re.search(
        r'ClinicalTrials\.gov(?:\s+(?:number|identifier))?\s*[,:(]|clinicaltrials\.gov/(?:ct2/)?show/NCT',s,re.I)]
    ids = sorted({n for s in spans for n in re.findall(r'\bNCT\d{8}\b',s)})
    return (ids[0],spans) if len(ids)==1 else (None,[])


def own_trials(root):
    """TOCI2 option (a) membership only; never calculate its relayed option (c)."""
    tr = resolution_module(root)
    block = recovery_map.load_map(root)[SLUG]
    entries = {e['pmid']:e for e in block['entries'] if e.get('pmid')}
    registry = load_registry(root,SLUG)
    path = root/'cache'/SLUG/'records.json'
    raw = path.read_bytes()
    records = {str(r['id']):r for r in json.loads(raw)['records']}
    review = json.loads((root/'docs/reviews'/SLUG/'review.json').read_bytes())
    outcome = one([o for o in review['outcomes'] if re.search(r'28.day all.cause mortality',o['name'],re.I)],'REFUSED_OUR_OUTCOME')
    ids = {m[0] for key in ('trials','declared_absent_trials') for r in outcome[key]
           if (m:=re.findall(r'\b\d{7,9}\b',r['id']))}
    files = {p.stem.removeprefix('ft_'):p for p in path.parent.glob('ft_*.txt')}
    trials = []
    for pmid in sorted(ids | set(entries) | set(files)):
        record, entry = records.get(pmid,{}), entries.get(pmid)
        names = sorted({s['acronym'] for s in registry.get(record.get('nct'),{}).get('raw',{}).get('studies',[]) if s.get('acronym')})
        titles = re.findall(r'\(([A-Z][A-Za-z]*[A-Z][A-Za-z-]*)\)',record.get('title',''))
        name = entry['trial'] if entry else names[0] if len(names)==1 else titles[0] if len(titles)==1 else record.get('title','PMID '+pmid)
        file = files.get(pmid)
        bundle = tm.extract(file.read_bytes(),file.relative_to(root).as_posix(),pmid) if file else (tm.recovery_abstract(record,path.relative_to(root).as_posix(),raw) or {'statements':[]})
        binding = tm.select(bundle,name,entry)
        binding.update(pmid=pmid,nct=record.get('nct'),label=name)
        if file and not binding['nct']:
            nct, spans = source_registration(file.read_bytes())
            if nct:
                binding.update(nct=nct,registration_spans=spans)
        if name == 'CORIMUNO-TOC':
            binding.update(tr.corimuno(file.read_bytes(),file.relative_to(root).as_posix(),pmid,name)['binding'])
        if binding['state']=='SOURCE_UNRESOLVED':
            wrong = re.search(r'[^.]*died before (?!28\b)\d+ days from randomization[^.]*',record.get('abstract',''))
            binding.update(state='TIMEPOINT_MISMATCH' if wrong else 'DENOMINATOR_UNBOUND',
                           reason='TIMEPOINT_MISMATCH:'+wrong[0] if wrong else 'DENOMINATOR_UNBOUND: no source-bound target pair')
        if binding['state']=='ANALYSIS_READY':
            binding['counts'] = tm.require_poolable(binding,root)
        trials.append(binding)
    remap = tr.remap((root/tr.REMAP_SOURCE).read_bytes())
    remap['label'] = remap['trial']
    nct,spans = source_registration((root/tr.REMAP_SOURCE).read_bytes())
    if nct:
        remap.update(nct=nct,registration_spans=spans)
    trials.append(remap)
    return trials, review, outcome


def compare_sizes(row, own):
    counts = own.get('counts') or {}
    inter = [a['n'] for a in row['arms'] if a['role']=='intervention']
    controls = [a['n'] for a in row['arms'] if a['role']=='control']
    if len(inter)!=1 or len(controls)!=1:
        return 'ABSTAIN', ['MULTIDOSE_COMBINED_POPULATION_NOT_PRINTED']
    if any(counts.get(k) is None for k in ('n1i','n2i')):
        return 'IN_INVENTORY_UNPOOLED', [own.get('reason') or own['state']]
    differs = [f'ARM_SIZE_{k}: comparator={n}; ours={counts[k]}' for k,n in zip(('n1i','n2i'),inter+controls) if n != counts[k]]
    if differs:
        return 'VALUE_DIFFERS', differs + ['POPULATION: WHO OUTCOMES_RECORDED versus own '+str(own.get('population','UNRESOLVED'))]
    if own['state'] != 'ANALYSIS_READY':
        return 'IN_INVENTORY_UNPOOLED', [own.get('reason') or own['state']]
    return 'MATCH', ['SAME_IDENTITY_AND_ARM_SIZES_ONLY; population equivalence not certified']


def comparisons(table, trials, inventory):
    enriched = []
    for t in trials:
        own = dict(t)
        linked = ij.join(own,inventory)
        if linked['status']=='JOINED':
            # Retain source-extracted aliases: the inventory can lack the
            # publication's acronym even when it joins correctly by PMID.
            own_ids = ij.identity(own)
            node_ids = inventory[linked['index']]['identities']
            own['identities'] = {k:own_ids[k] | node_ids[k] for k in ij.KEYS}
        enriched.append(own)
    rows, used = [], set()
    for row in table['rows']:
        linked = ij.join(row,enriched)
        inv = ij.join(row,inventory)
        out = dict(label=row['label'],registration=row['registration'],zero_death=row['zero_death'],identity_join=linked)
        # A single registration can cover ward and ICU cohorts. Never claim both
        # match one publication solely because their NCT is the same.
        duplicate = row['registration'] and sum(r['registration']==row['registration'] for r in table['rows'])>1
        if duplicate or linked['status']=='AMBIGUOUS' or inv['status']=='AMBIGUOUS':
            out.update(status='ABSTAIN',reasons=['SHARED_REGISTRATION_COHORT_UNRESOLVED' if duplicate else 'AMBIGUOUS_IDENTITY'],in_option_a=False)
        elif linked['status']=='JOINED':
            idx = linked['index']
            own = enriched[idx]
            status,reasons = compare_sizes(row,own)
            is_pool = own['state']=='ANALYSIS_READY'
            if is_pool:
                used.add(idx)
            out.update(status=status,reasons=reasons,our_trial=own['trial'],our_pmid=own.get('pmid'),
                       our_state=own['state'],in_option_a=is_pool,
                       own_arm_sizes={k:(own.get('counts') or {}).get(k) for k in ('n1i','n2i')})
            if not is_pool and own.get('reason') and own['reason'] not in reasons:
                out['reasons'].append(own['state']+': '+own['reason'])
            if own['state']=='TIMEPOINT_MISMATCH':
                out['reasons'].append('Any WHO 28-day count relay remains RELAYED, not an own-source pool input')
        elif inv['status']=='JOINED':
            out.update(status='IN_INVENTORY_UNPOOLED',reasons=['NOT_HELD: no TOCI2 own-source 28-day pair',
                       *ij.states(inventory[inv['index']], '28-day all-cause mortality')],in_option_a=False)
        else:
            out.update(status='MISSING_FROM_OURS',reasons=['NOT_HELD: no compatible identity in held inventory'],in_option_a=False)
        if duplicate and linked['status']=='JOINED':
            own = enriched[linked['index']]
            out['reasons'].append(own.get('reason') or own['state'])
        rows.append(out)
    ready = [t for t in enriched if t['state']=='ANALYSIS_READY']
    return dict(rows=rows,comparator_k=table['k'],our_option_a_k=len(ready),
                K_MATCH='yes' if table['k']==len(ready) else 'no',
                comparator_not_in_our_pool=[dict(trial=r['label'],reasons=r['reasons']) for r in rows if not r['in_option_a']],
                our_pool_not_in_comparator=[t['trial'] for i,t in enumerate(enriched) if t['state']=='ANALYSIS_READY' and i not in used],
                our_option_a_members=[t['trial'] for t in ready])


def metric(items,total):
    return dict(n=len(items),N=total,n_of_N=f'{len(items)} of {total}',items=items)


def run(root=ROOT):
    root = Path(root)
    coverage = []
    for p in sorted((root/'topics').glob('*.json')):
        json.loads(p.read_bytes())
        coverage.append(dict(topic=p.stem,state='EXTRACTED' if p.stem==SLUG else 'OUTSIDE_LANE'))
    if SLUG not in [c['topic'] for c in coverage]:
        raise ValueError('REFUSED_TOPIC_NOT_HELD')
    raw = (root/HELD).read_bytes()
    table = extract(raw)
    p = proposal(table,raw)
    checked = verify_held(p,raw)
    if checked['status'] != 'accepted':
        raise ValueError('REFUSED_LANE_PROPOSAL:'+json.dumps(checked))
    topic = json.loads((root/'topics'/f'{SLUG}.json').read_bytes())
    if str(topic['comparator_pmid']) != table['pmid']:
        raise ValueError('REFUSED_TOPIC_COMPARATOR_IDENTITY')
    trials, review, outcome = own_trials(root)
    diff = comparisons(table,trials,ij.our_identities(SLUG,root,review))
    native = gate.verify(p,root)
    census = dict(topics=metric([SLUG],len(coverage)),topic_coverage=coverage,
        rules={s:metric([r['label'] for r in diff['rows'] if r['status']==s],len(table['rows'])) for s in
               ('MATCH','VALUE_DIFFERS','IN_INVENTORY_UNPOOLED','MISSING_FROM_OURS','ABSTAIN')})
    census['rules'].update(
        ZERO_DEATH_TYPED=metric([r['label'] for r in table['rows'] if r['zero_death']],len(table['rows'])),
        NON_TARGET_SECTION_EXCLUDED=metric([r['section']+': '+r['label'] for r in table['excluded']],len(table['rows'])+len(table['excluded'])),
        NATIVE_GATE_REFUSED=metric([SLUG] if native['status']!='accepted' else [],1),
        LANE_FIELDS_REJECTED=metric([f['path'] for f in checked['fields'] if f['status']=='rejected'],len(checked['fields'])),
        MULTIDOSE_NOT_COLLAPSED=metric([r['label'] for r in table['rows'] if sum(a['role']=='intervention' for a in r['arms'])>1],len(table['rows'])))
    census['comparison'] = diff
    census['gate'] = dict(native_status=native['status'],native_reason=native['reason'],lane_status=checked['status'])
    census['population'] = dict(type=table['population'],span=table['population_span'])
    census['pooled'] = dict(k=table['k'],**table['effect'])
    return dict(proposal=p,table=table,lane_gate=checked,native_gate=native,census=census,
                own_states=[{k:t.get(k) for k in ('trial','pmid','nct','registration_spans','state','reason','counts')} for t in trials])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    result = run()
    if args.write:
        dest = ROOT/'.tmp/g1toci'
        dest.mkdir(parents=True,exist_ok=True)
        for name,key in [('proposal','proposal'),('comparator_table','table'),('lane_gate','lane_gate'),
                         ('native_gate','native_gate'),('census','census'),('own_states','own_states')]:
            (dest/f'{name}.json').write_text(json.dumps(result[key],indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result['census'],indent=2,ensure_ascii=True))


if __name__ == '__main__':
    main()
