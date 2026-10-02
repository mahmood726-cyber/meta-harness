"""Offline census. Default prints JSON only; --write-relay updates the allowed map."""
from pathlib import Path
import sys
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import re
import math
from dataclasses import asdict
from harness import table_binding as binding, table_rows, measure_identity, synth, extract, dose_arms, verified_inputs
from scripts import make_philo_excerpt as philo, make_plato_fda_excerpt as plato

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'ticagrelor-vs-clopidogrel-acs'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def specs(config):
    return [s for s in measure_identity.protocol_specs(config) if s.get('name')]


def lane_bindings():
    config = read(ROOT/'topics'/f'{SLUG}.json')
    out = []
    for spec in specs(config):
        for name in [philo.OUTPUT, *plato.OUTPUTS]:
            # Explicit proposed HR peer class; the immutable RR target is retained.
            cfg = dict(spec, peer_measures=['HR'] if spec['name'] == 'Major bleeding' else [spec.get('estimand')])
            try:
                out.append((spec['name'], binding.bind(SLUG,cfg,ROOT/name)))
            except ValueError as exc:
                if 'ROW_IDENTITY' not in str(exc):
                    raise
    return out


def proposed_pool(bound):
    rows = [dict(b['input'],id=b['pmid'],trial=b['trial']) for n,b in bound if n == 'Major bleeding']
    binding.require_pool(rows)
    studies = [synth.Study(label=r['trial'],effect=r['effect'],ci_low=r['ci_low'],ci_high=r['ci_high'],measure='HR') for r in rows]
    result = asdict(synth.pool(studies,scale='HR'))
    yv = [s.yi_vi() for s in studies]
    # At k=2 the REML contrast likelihood and PM Q=1 have the same solution.
    reml_two = max(0.0,((yv[0][0]-yv[1][0])**2-yv[0][1]-yv[1][1])/2)
    return dict(label='PROPOSED SERVED CHANGE',method=synth.method_text('HR'),
                inputs=rows,result=result,reml_two_study_check=reml_two,
                protocol_change_required=True,disperse_in_pool=False)


def relay_block(bound):
    """Reviewer numbers are parsed from the instruction file and quarantined."""
    prompt = (ROOT/'docs/relays/ticagrelor-vs-clopidogrel-acs.relay.txt').read_text(encoding='utf-8')
    relayed = philo.one(r'dyspnoea (\d+)/(\d+) vs\s+(\d+)/(\d+), published HR ([\d.]+) \(([\d.]+)-([\d.]+)\)',prompt)
    major = philo.one(r'major bleeding \(study-defined, NOT the non-CABG row\) HR ([\d.]+)\s+\(([\d.]+)-([\d.]+)\)',prompt)
    b = next(b for n,b in bound if n == 'Major bleeding' and b['trial'] == 'PLATO')
    d = next(b for n,b in bound if n == 'Dyspnea' and b['trial'] == 'PLATO')
    base = dict(trial=b['trial'],pmid=b['pmid'],provenance='RELAYED',derivation='RELAYED',poolable=False)
    def value(v,state,evidence=None):
        return dict(value=v,binding_state=state,held_evidence=evidence,provenance='RELAYED',poolable=False)
    dyspnea = dict(base,outcome='Dyspnea',definition='REVIEWER_NEJM_DYSPNEA',
        document_ref=d['document_ref'],values={})
    for k,v in zip(('ai','n1i','ci','n2i'),relayed.groups()[:4]):
        same = int(v) == d[k]
        dyspnea['values'][k] = value(int(v),'BOUND' if same else 'DEFINITION_DIFFERS',
                                   {'value':d[k],'definition':d['definition'],'excerpt_sha':d['excerpt_sha']})
    for k,v in zip(('effect','ci_low','ci_high'),relayed.groups()[4:]):
        dyspnea['values'][k] = value(float(v),'RELAYED_ONLY',
              'FDA page 255 onset prose repeats the number; definition is not explicitly bound to the seven-term Table23 group or the unheld NEJM footnote.')
    dyspnea['values']['measure'] = value('HAZARD_RATIO','RELAYED_ONLY',
        'Reviewer says table header HR/OR, measure named by footnote; NEJM footnote is not held, so no independent footnote verification.')
    dyspnea['values']['population'] = value('treated','RELAYED_ONLY')
    window = philo.one(r'window (through \d+ days after discontinuation)',prompt)[1]
    dyspnea['values']['window'] = value(window,'RELAYED_ONLY')
    bleeding = dict(base,outcome='Major bleeding',definition=b['definition'],document_ref=b['document_ref'],values={})
    for k,v in zip(('effect','ci_low','ci_high'),major.groups()):
        actual = b['input'][k]
        bleeding['values'][k] = value(float(v),'BOUND' if float(v)==actual else 'RELAYED_ONLY',
                                     {'value':actual,'excerpt_sha':b['excerpt_sha']})
    for k in ('ai','n1i','ci','n2i'):
        # These values are obtained independently from held Table12, not invented relay numbers.
        bleeding['values'][k] = value(b[k],'BOUND',{'value':b[k],'excerpt_sha':b['excerpt_sha']})
    bleeding['values']['measure'] = value(b['selected_measure'],'BOUND','Table12 explicitly says Hazard ratio (95% CI)')
    return dict(source='Investigator-supplied NEJM relay in docs/relays/ticagrelor-vs-clopidogrel-acs.relay.txt; never a pool input',
                population='treated (relay; outcome-specific source validation required)',entries=[dyspnea,bleeding])


def write_relay():
    path = ROOT/'docs/recovery_maps.json'
    old = path.read_bytes()
    data = json.loads(old)
    block = relay_block(lane_bindings())
    if SLUG in data['topics']:
        if data['topics'][SLUG] == block:
            return
        if data['topics'][SLUG].get('source') != block['source']:
            raise ValueError('REFUSED overwrite of a different existing ticagrelor recovery map')
        text=old.decode('utf-8')
        key=json.dumps(SLUG)+':'
        if text.count(key)!=1:
            raise ValueError('REFUSED ambiguous ticagrelor recovery map')
        start=text.index('{',text.index(key)+len(key))
        _, end=json.JSONDecoder().raw_decode(text[start:])
        nl='\r\n' if b'\r\n' in old else '\n'
        replacement=(nl+'    ').join(json.dumps(block,ensure_ascii=False,indent=2).splitlines())
        # Refresh only our value; every byte before and after it is preserved.
        path.write_bytes((text[:start]+replacement+text[start+end:]).encode('utf-8'))
        return
    # Insert immediately after topics {; all existing bytes, including tocilizumab, survive.
    marker = b'"topics": {'
    if old.count(marker) != 1:
        raise ValueError('REFUSED ambiguous recovery map structure')
    nl = b'\r\n' if b'\r\n' in old else b'\n'
    item = json.dumps({SLUG:block},ensure_ascii=False,indent=2)[2:-2]
    addition = nl + nl.join(('  '+line).encode('utf-8') for line in item.splitlines()) + b','
    new = old.replace(marker,marker+addition,1)
    if json.loads(new)['topics']['tocilizumab-covid19-mortality'] != data['topics']['tocilizumab-covid19-mortality']:
        raise ValueError('REFUSED tocilizumab modification')
    path.write_bytes(new)


def ratio(n,items,**extra):
    return dict(n=len(items),N=n,n_of_N=f'{len(items)} of {n}',items=items,**extra)


def census():
    bound = lane_bindings()
    excerpts = sorted((ROOT/'evidence/acquisition_cascade/excerpts').glob('*.txt'))
    topics = sorted((ROOT/'topics').glob('*.json'))
    parsed, parse_refused = {}, {}
    for path in excerpts:
        try:
            parsed[path] = table_rows.parse(path)
        except ValueError as exc:
            parse_refused[path.name] = str(exc).replace(str(path)+': ', '')
    binds, abstract_rows, abs_outcomes, abs_changes = set(),[],set(),[]
    matching_refusals = set()
    rules = {r:[] for r in ('ROW_IDENTITY','PUBLISHED_SAME_MEASURE','CRUDE_RR_NOT_HR','ABSENCE_SUPERSEDED')}
    total_outcomes = 0
    for topic in topics:
        config = read(topic)
        slug = config.get('slug',topic.stem)
        review_path = ROOT/'docs/reviews'/slug/'review.json'
        review = read(review_path) if review_path.exists() else {'outcomes':[]}
        for spec in specs(config):
            total_outcomes += 1
            outcome = next((o for o in review['outcomes'] if o['name']==spec['name']),{})
            label = slug+' / '+spec['name']
            if measure_identity.check_pool(outcome.get('trials',[])):
                if any(p['code']=='MEASURE_MIX_POOLED' for p in measure_identity.check_pool(outcome.get('trials',[]))):
                    rules['CRUDE_RR_NOT_HR'].append(label)
            absent = [r for r in outcome.get('declared_absent_trials',[]) if re.search(
                r'inspected abstract|found in the abstract',json.dumps(r),re.I)]
            if absent:
                abs_outcomes.add(label)
            abstract_rows.extend(label+' / '+r['id'] for r in absent)
            changed_abs = False
            for path,tables in parsed.items():
                # Use the binder's identity selector, including Total Major; a generic
                # keyword prefilter would silently omit the FDA Table12 alias.
                candidates=[]
                for table in tables:
                    try:
                        candidates.append(binding.select_row(table,spec))
                    except ValueError:
                        pass
                if not candidates:
                    continue
                cfg = dict(spec)
                if slug==SLUG and spec['name']=='Major bleeding':
                    cfg['peer_measures']=['HR']
                try:
                    b = binding.bind(slug,cfg,path)
                except (ValueError,FileNotFoundError,KeyError) as exc:
                    matching_refusals.add(path.name+' / '+str(exc).split(':',1)[0])
                    continue
                binds.add(path.name)
                if b['published_effect'] and b['input'].get('derivation')=='PUBLISHED':
                    rules['PUBLISHED_SAME_MEASURE'].append(label+' / '+b['trial'])
                for r in absent:
                    if b['pmid'] in re.findall(r'\b\d+\b',r['id']):
                        binding.supersede_absence(r,b)
                        item=label+' / '+r['id']
                        if item not in rules['ABSENCE_SUPERSEDED']:
                            rules['ABSENCE_SUPERSEDED'].append(item)
                        changed_abs=True
            if changed_abs:
                abs_changes.append(label)
    review = read(ROOT/'docs/reviews'/SLUG/'review.json')
    changes=[]
    for outcome in review['outcomes']:
        relevant=[b for name,b in bound if name==outcome['name']]
        if not relevant:
            continue
        changes.append(dict(outcome=outcome['name'],before=[{k:r[k] for k in
            ('id','ai','n1i','ci','n2i','effect','ci_low','ci_high','scale') if k in r} for r in outcome['trials']],
            after=[dict(trial=b['trial'],pmid=b['pmid'],input=b['input'],definition=b['definition']) for b in relevant]))
    # Row identity census: rows excluded by the existing variant vocabulary.
    rows=[(p.name,t,r) for p,ts in parsed.items() for t in ts for r in t['rows']]
    excluded=[p+' / '+r['label'] for p,t,r in rows if table_rows.variants(r)]
    return dict(topics_examined=len(topics),outcomes_examined=total_outcomes,
        ticagrelor_inputs_change=ratio(len(review['outcomes']),changes),
        committed_excerpts_bind=ratio(len(excerpts),sorted(binds)),
        abstract_absent_outcomes_covered=ratio(len(abs_outcomes),sorted(set(abs_changes))),
        abstract_absent_trial_rows_covered=ratio(len(abstract_rows),sorted(rules['ABSENCE_SUPERSEDED'])),
        row_variant_flags=ratio(len(rows),excluded),
        published_same_measure_preference=ratio(len(bound),sorted(set(rules['PUBLISHED_SAME_MEASURE']))),
        mixed_measure_outcomes=ratio(total_outcomes,sorted(rules['CRUDE_RR_NOT_HR'])),
        patient_unit_excludes_event_columns=ratio(len(bound),[n+' / '+b['trial'] for n,b in bound if b['excluded_columns']]),
        relayed_entries_quarantined=ratio(len(relay_block(bound)['entries']),
            [e['trial']+' / '+e['outcome'] for e in relay_block(bound)['entries'] if not e['poolable']]),
        disperse_recovery_active=ratio(1,[binding.disperse()['trial']]),
        excerpt_parse_refusals=parse_refused,matching_bind_refusals=sorted(matching_refusals),
        disperse={k:v for k,v in binding.disperse().items() if k!='record'},
        proposed_pool=proposed_pool(bound))


def plant_evidence():
    """Executable pre-fix transcripts, not a narrative invented from expectations."""
    bound=lane_bindings()
    ph=next(b for n,b in bound if n=='Major bleeding' and b['trial']=='PHILO')
    pl=next(b for n,b in bound if n=='Major bleeding' and b['trial']=='PLATO')
    counts={k:ph[k] for k in ('ai','n1i','ci','n2i')}
    published=ph['input']
    base=synth.Study('PHILO plant',**counts,effect=published['effect'],
                     ci_low=published['ci_low'],ci_high=published['ci_high'],measure='HR')
    variants=[]
    for name,label in [('Major bleeding','Major bleeding non-CABG-related'),('Dyspnea','Dyspnea leading to discontinuation')]:
        table=table_rows.parse(ROOT/philo.OUTPUT)[0]
        table['rows']=[dict(table['rows'][0],label=label)]
        selected,reason=table_rows.select(table,[name],[])
        try:
            binding.select_row(table,{'name':name})
        except ValueError as exc:
            post=str(exc)
        variants.append(dict(plant=label,base={'label':selected['label'],'reason':reason},post=post))
    review=read(ROOT/'docs/reviews'/SLUG/'review.json')
    dy=next(b for n,b in bound if n=='Dyspnea' and b['trial']=='PHILO')
    absent=next(r for o in review['outcomes'] if o['name']=='Dyspnea' for r in o['declared_absent_trials'] if dy['pmid'] in r['id'])
    abstract=next(r['abstract'] for r in read(ROOT/'cache'/SLUG/'records.json')['records'] if str(r['id'])==dy['pmid'])
    extraction=extract.extract_trial(abstract,['dyspnea','dyspnoea'],['ticagrelor'],['clopidogrel'],declared_composite=False,estimand='RR')
    current=next(o for o in review['outcomes'] if o['name']=='Major bleeding')['trials']
    mixed=synth.pool([synth.Study('PHILO',effect=published['effect'],ci_low=published['ci_low'],ci_high=published['ci_high']),
                     synth.Study('PLATO',**{k:pl[k] for k in ('ai','n1i','ci','n2i')})],scale='HR')
    d=binding.disperse_held_record()
    km=next(s for s in d['record']['abstract'].split(';') if 'Kaplan-Meier' in s and '%' in s)
    pct=float(re.search(r'(\d+(?:\.\d+)?)%',km)[1])
    fake=dict(ai=round(pct*1000/100),n1i=1000,ci=1,n2i=1000)
    controls=[dict(trial_id=d['pmid'],outcome='major bleeding',control_id='shared',n2i=100,ci=10,control_n=100,control_events=10) for _ in range(2)]
    mi='Myocardial infarction (HR 0.8; 95% CI 0.6 to 1.0).'
    relay=relay_block(bound)['entries'][0]
    relay_plant=dict(outcome='Dyspnea',derivation='RELAYED',effect=relay['values']['effect']['value'])
    try:
        binding.require_pool([relay_plant])
    except ValueError as exc:
        relay_post=str(exc)
    return dict(row_identity=variants,
        published_preference={'base_Study_exp_y':math.exp(base.yi_vi()[0]),'base_label':'HR','post_input':published,'separate_counts':counts},
        absence={'base_extract_trial':extraction,'committed_pre_fix':{k:absent[k] for k in ('id','state','reason','result_status')},
                 'post':binding.supersede_absence(absent,dy)['result_status']},
        mixed={'base_pool':{'scale':mixed.scale,'k':mixed.k,'estimate':mixed.estimate},'post':measure_identity.check_pool(current)},
        km={'plant_only_synthetic_denominator':1000,'base_yi_vi':synth.Study('plant',**fake).yi_vi(),'post':dose_arms.km_products(fake,km)},
        control={'base_pool_k':synth.pool([synth.Study(str(i),ai=12,n1i=100,ci=10,n2i=100) for i in range(2)]).k,
                 'post':dose_arms.control_problems(controls),'negative_split':dose_arms.control_problems(dose_arms.split_control(controls))},
        endpoint={'base_extract_effect':extract.extract_effect(mi),'post':dose_arms.endpoint_problem(mi,'MACE composite')},
        relay={'base_runtime':verified_inputs.runtime(relay_plant),'post':relay_post})


if __name__ == '__main__':
    if '--write-relay' in sys.argv:
        write_relay()
    else:
        print(json.dumps(census(),ensure_ascii=False,indent=2))
