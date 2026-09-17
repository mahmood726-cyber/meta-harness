"""Evidence-bearing trial families, extending identity's publication units.

No network, pooling, or outcome-based eligibility decisions. Missing evidence is
explicitly unknown; an unlinked report remains a flagged candidate family.
"""
from __future__ import annotations
import hashlib
import itertools
import json
import math
import re
from pathlib import Path
from typing import TypedDict
from . import identity, arm_object, target_endpoint
from .family_compact import read_registry

class TrialFamily(TypedDict):
    family_id: str
    reports: list[dict]
    arms: list[dict]
    randomised_contrasts: list[dict]
    outcome_status: list[dict]

REGISTRY = re.compile(r'\b(?:NCT\d{8}|\d{4}-\d{6}-\d{2}|ISRCTN\d+|jRCT\w+|ACTRN\d+)\b', re.I)
ROLES = [
    ('RETRACTION', r'retract(?:ion|ed)'), ('CORRECTION', r'correction|erratum|corrigendum'),
    ('COST_EFFECTIVENESS', r'cost[- ]effect|cost[- ]utility|economic evaluation'),
    ('SAP', r'statistical analysis plan'), ('PROTOCOL', r'\bprotocol\b'),
    ('DESIGN_PAPER', r'rationale and design|study design'),
    ('POOLED_ANALYSIS', r'pooled (?:post[- ]hoc )?analysis|analysis of individual participant data from two clinical trials'),
    ('HTA', r'meta-analysis|systematic review|health technology assessment'),
    ('EXTENSION', r'\bextension\b|post-trial follow-up|open-label continuation|open-label.*follow-up'),
    ('SUBGROUP', r'subgroup|substudy|sub-study'),
    ('SECONDARY_ANALYSIS', r'secondary analysis|post[- ]hoc|subanalysis'),
    ('CONFERENCE_ABSTRACT', r'conference abstract|congress abstract'),
    ('PRIMARY', r'randomi[sz]ed controlled trial|randomi[sz]ed.*placebo-controlled trial'),
]

def field(value=None, span=None, code='NOT_HELD'):
    return {'value': value, 'span': span} if value not in (None, '', []) and span else {'value': None, 'absence_code': code}

def cell(state='UNKNOWN', span=None, code='NOT_HELD'):
    return {'state': state, 'span': span} if span else {'state': state, 'absence_code': code}

def report_role(rec):
    for key in ('title', 'pubtypes'):
        if key == 'pubtypes':
            abstract = str(rec.get('abstract') or '')
            objective = re.search(r'OBJECTIVES?:[^.]*in relation to[^.]*\.', abstract,re.I)
            interaction = re.search(r'interaction between[^.]*treatment effect was assessed',abstract,re.I)
            if objective and interaction:
                return 'SUBGROUP', {'source':'record.abstract','quote':abstract,
                                    'match':interaction.group(), 'objective_span':objective.group()}
        text = ' '.join(rec.get(key) or []) if key == 'pubtypes' else str(rec.get(key) or '')
        for role, pattern in ROLES:
            m = re.search(pattern, text, re.I)
            if m:
                return role, {'source': 'record.'+key, 'quote': text, 'match': m.group()}
    if str(rec.get('id_type')).lower() == 'nct':
        return 'REGISTRY_RECORD', {'source': 'record.id_type', 'quote': 'nct'}
    for kind in ('FDA', 'EMA'):
        if rec.get('source_kind') == 'REGULATORY_'+kind:
            return 'REGULATORY_'+kind, {'source':'record.source_kind', 'quote':rec['source_kind']}
    return 'ROLE_UNRESOLVED', {'absence_code': 'NO_TYPED_ROLE_EVIDENCE'}

def registry_ids(rec):
    values = set(str(x) for x in rec.get('registry_ids') or [])
    for key in ('nct', 'eudract', 'isrctn', 'jrct'):
        if rec.get(key):
            values.add(str(rec[key]))
    values.update(m.group() for m in REGISTRY.finditer(' '.join(str(rec.get(k) or '') for k in ('id','abstract'))))
    return sorted(values, key=lambda v: (0 if v.upper().startswith('NCT') else
                  1 if re.fullmatch(r'\d{4}-\d{6}-\d{2}',v) else
                  2 if v.upper().startswith('ISRCTN') else 3 if v.lower().startswith('jrct') else 4, v))

def _rid(rec):
    return identity._norm(rec.get('id') or rec.get('pmid') or rec.get('doi') or rec.get('pmc') or rec.get('url'))

def randomised_contrasts(arms, agents, randomized=False):
    """Compare COMPLETE linked arm intervention sets; same-drug dose trials fail.

    Missing linkage cannot be treated as placebo. Shared background must be
    explicitly represented by both arms. Matching placebo has no active drug.
    """
    if not randomized:
        return []
    out = []
    for a, b in itertools.combinations(arms, 2):
        if not a.get('linkage_complete') or not b.get('linkage_complete'):
            continue
        av, bv = set(a['active_interventions']), set(b['active_interventions'])
        for agent in agents:
            match = lambda values: {v for v in values if re.search(r'(?<!\w)'+re.escape(agent.lower())+r'(?!\w)', v)}
            aa, bb = match(av), match(bv)
            if bool(aa) == bool(bb) or av-aa != bv-bb:
                continue
            out.append({'arm_ids':[a['arm_id'], b['arm_id']], 'drug':agent,
                        'background_therapy':sorted(av-aa), 'span':[a['span'], b['span']]})
    return out

def families(records, *, companion_reports=None, config=None, registry=None, ledger=None):
    config, registry, ledger = config or {}, registry or {}, ledger or {}
    records = [dict(r, id=_rid(r), registry_ids=registry_ids(r)) for r in records]
    if any(not r['id'] for r in records):
        raise ValueError('Every report requires a held identifier')
    # Meta-analyses describe multiple trials and are retained separately by the consumer.
    records = [r for r in records if report_role(r)[0] not in {'HTA','POOLED_ANALYSIS'}]
    by_id = {r['id']:r for r in records}
    for r in records:
        ncts = [n for n in r['registry_ids'] if n.upper().startswith('NCT')]
        if len(ncts)>1:
            # A paper citing several trials is not proof that their registry
            # identifiers are aliases. Do not let it bridge trial identities.
            r['mentioned_registry_ids'] = r['registry_ids']
            r['registry_ids'] = []
            r['original_nct_field'] = r.get('nct')
            r['nct'] = ''
            r['parent_link_absence_code'] = 'MULTIPLE_REGISTRY_PARENTS'
            continue
        for n in r['registry_ids']:
            if n.upper().startswith('NCT'):
                r['nct'] = n.upper()
                break
    # Reuse PU companion linkage, but do not accept free-text family labels as registry IDs.
    units = identity.build_publication_units(records, companion_reports)
    for c in companion_reports or []:
        child, parent = by_id.get(str(c.get('pmid'))), by_id.get(str(c.get('parent_pmid')))
        if child is not None and parent is not None:
            related = child.setdefault('related_report_ids', [])
            if parent['id'] not in related:
                related.append(parent['id'])
            child['parent_link_basis'] = {'source':'identity companion_reports','row':c,
                                          'publication_unit':units[child['id']]}
    groups = identity.build_identities(records, strict=True)
    out = []
    for group in groups:
        members = [by_id[i] for i in sorted(set(group['members']))]
        regs = registry_ids({'registry_ids':list({v for r in members for v in r['registry_ids']})})
        reports = []
        for r in members:
            role, basis = report_role(r)
            report = {'report_id':r['id'], 'role':role, 'span_basis':basis,
                      'retrieved_via':(ledger.get('records',{}).get(r['id'],{}).get('found_by') or r.get('found_by') or ['LEGACY_UNRECORDED'])}
            if role == 'EXTENSION':
                text = ' '.join(str(r.get(k) or '') for k in ('title','abstract'))
                loss = re.search(r'open[- ]label|cross(?:ed)?[- ]over|all (?:participants|patients).*received', text, re.I)
                report['randomised_contrast_preserved'] = False if loss else None
                report['contrast_preservation_basis'] = field(False, {'source':'record.title_abstract','quote':loss.group()}) if loss else field(code='NOT_ESTABLISHED')
                report['standalone_pool_eligible'] = False if loss else None
            reports.append(report)
        primaries = sorted(r['report_id'] for r in reports if r['role'] == 'PRIMARY')
        seed = primaries or sorted(r['report_id'] for r in reports)
        fid = regs[0] if regs else 'SYN-'+hashlib.sha256(json.dumps(seed,separators=(',',':')).encode()).hexdigest()[:12]
        flags = [] if regs else ['NO_REGISTRY_RECORD']
        if any(r.get('parent_link_absence_code') for r in members):
            flags = ['MULTIPLE_REGISTRY_PARENTS','PARENT_UNRESOLVED']
        if regs and not fid.upper().startswith('NCT'):
            flags.append('IDENTITY_FROM_HELD_TEXT')
        if not primaries and not regs:
            flags.append('PARENT_UNRESOLVED')
        held = registry.get(fid, {})
        for r in held.get('raw',{}).get('id_information',[]):
            if REGISTRY.fullmatch(r.get('id_value','')) and r['id_value'] not in regs:
                regs.append(r['id_value'])
        objects = [arm_object.build(r, config) for r in members]
        arms = held.get('arms') or []
        agents = list((config.get('include') or {}).get('intervention_any') or config.get('intervention_terms') or [])
        population = held.get('population') or {'absence_code':'REGISTRY_ELIGIBILITY_NOT_HELD', 'report_fields':[o['population'] for o in objects]}
        life = held.get('lifecycle') or {k:field(code='REGISTRY_DATE_NOT_HELD') for k in ('registered','started','completed','results_posted')}
        life = dict(life, publication_found=field(code='PUBLICATION_DATE_NOT_HELD'))
        dates = [(r.get('year'), r['id']) for r in members if r.get('year') and r.get('id_type') != 'nct']
        if dates:
            year, rid = min(dates, key=lambda x:str(x[0]))
            life['publication_found'] = field(year, {'report_id':rid, 'source':'record.year', 'precision':'year'})
        sources = sorted({s for r in reports for s in r['retrieved_via']})
        source_by_id = {s['source_id']:s for s in ledger.get('sources') or []}
        entered = []
        for sid in sources:
            src = source_by_id.get(sid,{})
            kind = str(src.get('kind',''))
            if 'SEED' in kind or 'IDENTIFIER' in kind:
                entered.append('SEEDED_IDENTIFIER')
            elif src.get('state') in {'RAN_OK','RAN_ZERO'} and src.get('discovery_capable'):
                entered.append('EXECUTED_QUERY('+sid+')')
            elif kind == 'MANUAL_ADDITION':
                entered.append('MANUAL_ADDITION')
            else:
                entered.append('LEGACY_UNRECORDED')
        f = {'family_id':fid, 'identity_flag':flags[0] if flags else 'REGISTRY_ANCHORED', 'flags':flags,
             'identity_basis':{'primary_report_ids':primaries, 'registry_ids':regs, 'fallback_report_ids':seed if not primaries else []},
             'aliases':{'acronym':sorted({str(r['acronym']) for r in members if r.get('acronym')} |
                         {r['acronym'] for r in held.get('raw',{}).get('studies',[]) if r.get('acronym')}),
                        'registry_ids':regs, 'mentioned_registry_ids':sorted({n for r in members for n in r.get('mentioned_registry_ids',[])}),
                        'report_ids':sorted(r['id'] for r in members),
                        'dois':sorted({r['doi'] for r in members if r.get('doi')})},
             'reports':reports, 'arms':arms, 'arm_absence_code':None if arms else 'NO_COMPLETE_ARM_STRUCTURE',
             'abstract_arm_objects':objects if not arms else [],
             'randomised_contrasts':randomised_contrasts(arms, agents, held.get('randomized',False)),
             'population':population, 'analysis_sets':[{'report_id':r['id'], **o['analysis_set']} for r,o in zip(members,objects)],
             'lifecycle':life, 'entered_via':sorted(set(entered)), 'outcome_status':[],
             'eligibility':cell(code='FAMILY_SCREEN_NOT_RUN'), 'registry_design':held.get('design',{}),
             'source_records':members}
        specs = [config['primary_outcome']] if config.get('primary_outcome') else []
        specs += list(config.get('secondary_outcomes') or []) + list(config.get('harm_outcomes') or [])
        for spec in specs:
            # Mention alone does not establish measurement, reporting, or prospective registration.
            f['outcome_status'].append({'outcome':spec['name'], **{k:cell(code='NO_VERIFIED_OUTCOME_SPAN') for k in
                ('prospectively_specified','measured','reported','extractable','in_primary_pool')},
                'registered_outcome_candidates':held.get('design_outcomes',[])})
        refresh_registered_outcomes([f], config)
        for status in f['outcome_status']:
            spec = next(s for s in specs if s['name']==status['outcome'])
            for result in held.get('registry_results',[]):
                match = target_endpoint._classify(spec,result['outcome'].get('title',''))
                if match['target_endpoint_class'] != 'EXACT_TARGET':
                    continue
                measurements = result.get('measurement_samples') or []
                analyses = result.get('analyses') or []
                numeric = []
                for row in measurements+analyses:
                    raw = row.get('param_value_num') or row.get('param_value')
                    try:
                        value = float(raw)
                    except (TypeError, ValueError):
                        continue
                    if math.isfinite(value):
                        numeric.append({'value':value,'param_type':row.get('param_type'),
                                        'source_row':row,'source_table':'outcome_measurements' if row in measurements else 'outcome_analyses'})
                if numeric:
                    evidence = {'source':'AACT registry results','outcome_row':result['outcome'],'typed_values':numeric}
                    for key in ('measured','reported','extractable'):
                        status[key] = cell('YES',evidence)
                    status['extractable']['scope'] = 'Typed registry outcome values; not automatically a poolable contrast or target effect measure.'
                    break
        f['eligibility'] = screen_family(f, config)
        out.append(f)
    return sorted(out, key=lambda f:f['family_id'])

def refresh_registered_outcomes(nodes, config):
    """Match outcome identity without claiming that a latest snapshot proves timing."""
    specs = [config['primary_outcome']] if config.get('primary_outcome') else []
    specs += list(config.get('secondary_outcomes') or []) + list(config.get('harm_outcomes') or [])
    by_name = {s['name']:s for s in specs}
    for f in nodes:
        for status in f['outcome_status']:
            candidates = []
            for item in status.get('registered_outcome_candidates',[]):
                row = item.get('row',item)
                match = target_endpoint._classify(by_name[status['outcome']],row.get('measure',''))
                if match['target_endpoint_class'] != 'DIFFERENT_OUTCOME':
                    candidates.append({'row':row, **match})
            status['registered_outcome_candidates'] = candidates
            exact = [c['row'] for c in candidates if c['target_endpoint_class']=='EXACT_TARGET' and
                     c['row'].get('outcome_type','').lower() in {'primary','secondary'}]
            if exact:
                status['prospectively_specified'] = {
                    'state':'UNKNOWN','absence_code':'REGISTRY_HISTORY_OR_DATED_PROTOCOL_NOT_HELD',
                    'span':{'source':'AACT.design_outcomes','rows':exact},
                    'registered_in_current_snapshot':True}
            else:
                status['prospectively_specified'] = cell(code='NO_EXACT_REGISTERED_OUTCOME_MATCH')

def attach_review(review, nodes):
    """Attach family IDs without altering existing pooling membership or estimates."""
    by_report = {r['report_id']:f for f in nodes for r in f['reports']}
    eligible = {f['family_id'] for f in nodes if f['eligibility']['state']=='ELIGIBLE'}
    contributing = set()
    for r in review.get('screening',{}).get('records',[]):
        f = by_report.get(identity._norm(r.get('id')))
        if f:
            r['family_id'] = f['family_id']
            r['family_eligibility'] = f['eligibility']
    for outcome in review.get('outcomes') or []:
        for key in ('trials','declared_absent_trials'):
            for row in outcome.get(key) or []:
                f = by_report.get(identity._norm(row.get('id')))
                if not f:
                    continue
                row['family_id'] = f['family_id']
                if key == 'trials':
                    contributing.add(f['family_id'])
                    for status in f['outcome_status']:
                        if status['outcome'] == outcome.get('name'):
                            if outcome.get('primary'):
                                status['in_primary_pool'] = cell('YES', {'source':'review.outcomes.trials','report_id':identity._norm(row.get('id'))})
                            span = row.get('span') or row.get('source_span') or row.get('quote')
                            if not span:
                                source = (row.get('study_effect') or {}).get('source_provenance') or {}
                                candidate = source.get('span')
                                if candidate:
                                    # Legacy source strings prefix the literal quotation with a label.
                                    candidate = candidate.split(': ',1)[-1]
                                    if any(candidate in str(r.get('abstract','')) for r in f['source_records']):
                                        span = {'quote':candidate,'source':'held abstract','report_id':identity._norm(row.get('id'))}
                            if span:
                                for k in ('reported','measured','extractable'):
                                    status[k] = cell('YES', span)
    for f in nodes:
        for status in f['outcome_status']:
            if status['in_primary_pool']['state'] == 'UNKNOWN':
                status['in_primary_pool'] = cell('NO', {'source':'review.outcomes.trials','family_id':f['family_id']})
    review['trial_families'] = nodes
    inputs = {r['id']:r for f in nodes for r in f['source_records']}
    for r in review.get('screening',{}).get('records',[]):
        inputs.setdefault(identity._norm(r.get('id')),r)
    review['family_count_chain'] = {'publications_screened':sum(r.get('id_type') != 'nct' for r in inputs.values()),
                                  'registry_records_screened':sum(r.get('id_type') == 'nct' for r in inputs.values()),
                                  'trial_families':len(nodes), 'eligible_families':len(eligible), 'contributing':len(contributing),
                                  'eligibility_unresolved':sum(f['eligibility']['state']=='UNKNOWN' for f in nodes),
                                  'contributing_without_structural_eligibility':sorted(contributing-eligible)}
    return review['family_count_chain']

def count_sentence(chain):
    return (f"{chain['publications_screened']} publications screened + {chain.get('registry_records_screened',0)} registry records → {chain['trial_families']} trial families → "
            f"{chain['eligible_families']} eligible families → {chain['contributing']} contributing families. "
            f"{chain['eligible_families']} trials met eligibility. "
            f"{chain.get('eligibility_unresolved',0)} families have unresolved structural eligibility; existing pooling membership is preserved.")

def screen_family(family, config):
    """One P/I/C/design decision, independent of outcomes and report availability.

    The SF lane is absent on landing-3. This conservative structural contract
    abstains when the local arm and population evidence does not prove the rule.
    It is additive; legacy membership is retained and discrepancies are exposed.
    """
    inc = config.get('include') or {}
    design = family.get('registry_design') or {}
    requirements = config.get('family_requirements') or {}
    conditions = (family.get('population',{}).get('conditions') or {}).get('value') or []
    text = ' '.join(conditions).lower()
    if design.get('allocation') and design['allocation'].upper() != 'RANDOMIZED':
        return cell('INELIGIBLE', {'source':'AACT.designs','row':design})
    if not design or not conditions or not family.get('arms'):
        return cell(code='INSUFFICIENT_PICD_EVIDENCE')
    if requirements.get('parallel') and design.get('intervention_model','').upper() not in {'PARALLEL','PARALLEL ASSIGNMENT'}:
        return cell(code='PARALLEL_DESIGN_NOT_PROVEN')
    if requirements.get('adult'):
        bound = (family.get('population',{}).get('age_min') or {})
        age = re.fullmatch(r'(\d+(?:\.\d+)?)\s+Years?', str(bound.get('value') or ''),re.I)
        if not age:
            return cell(code='ADULT_ENTRY_AGE_NOT_PROVEN')
        if float(age.group(1)) < 18:
            return cell('INELIGIBLE', bound.get('span'))
    if inc.get('population_any') and not any(t.lower() in text for t in inc['population_any']):
        return cell(code='ENTRY_POPULATION_NOT_ESTABLISHED')
    if any(t.lower() in text for t in inc.get('population_none') or []):
        return cell('INELIGIBLE', family['population']['conditions']['span'])
    if not family['randomised_contrasts']:
        return cell(code='INTERVENTION_CONTRAST_NOT_PROVEN')
    if (inc.get('design_double_blind') or requirements.get('double_blind')) and design.get('masking','').upper() not in {'DOUBLE','TRIPLE','QUADRUPLE'}:
        return cell(code='BLINDING_NOT_PROVEN')
    # A drug-vs-active comparator pair is not evidence of placebo control.
    if 'placebo' in [str(x).lower() for x in inc.get('comparator_any') or []]:
        if not any('placebo' in str(a.get('drug',{}).get('value','')).lower() for a in family['arms']):
            return cell(code='PLACEBO_CONTROL_NOT_PROVEN')
    return cell('ELIGIBLE', {'design':design,'population':family['population']['conditions']['span'],
                             'protocol_requirements':requirements,
                             'contrasts':family['randomised_contrasts']})

def protocol_requirements(root, slug, config):
    """Apply explicit structured B-prime design/population declarations only.

    The lane instruction excludes outcomes from eligibility, including the
    protocol's separate ascertainment clause. No inference from a trial name.
    """
    path = Path(root)/'protocols'/f'{slug}.md'
    if not path.exists():
        return config
    text = path.read_text(encoding='utf8')
    line = next((x for x in text.splitlines() if x.startswith('- **Eligibility (B-prime).**')),None)
    if not line:
        return config
    return dict(config,family_requirements={
        'parallel':'Parallel-group randomised' in line,
        'double_blind':'double-blind, placebo-controlled' in line,
        'adult':'in adults with type 2 diabetes' in line,
        'span':{'source':f'protocols/{slug}.md','quote':line}})

def prepare(root, slug, records, config, ledger=None):
    """Read held family ingredients; registry collection is an explicit offline step."""
    root = Path(root)
    config = protocol_requirements(root,slug,config)
    path = root/'cache'/slug/'family_registry.json'
    ingredients = read_registry(path) if path.exists() else {}
    by_id = {_rid(r):dict(r) for r in records}
    discovery = root/'cache'/slug/'family_discovery.json'
    ledger = dict(ledger or {})
    if discovery.exists():
        d = json.loads(discovery.read_text(encoding='utf8'))
        for r in d.get('r3_records',[]) + d.get('records',[]):
            by_id.setdefault(_rid(r),dict(r))
        ledger['sources'] = list(ledger.get('sources') or []) + [d['source']]
    for rid, r in by_id.items():
        links = ingredients.get('report_links',{}).get(rid,[])
        index = ingredients.get('records',{})
        text = ' '.join(str(r.get(k) or '') for k in ('title','abstract'))
        matches = []
        if not r.get('nct') and not any(n.upper().startswith('NCT') for n in registry_ids(r)):
            for n, held in index.items():
                studies = held.get('raw',{}).get('studies') or []
                acronym = (studies[0].get('acronym') if studies else '') or ''
                iv = held.get('raw',{}).get('interventions') or []
                names = {x['name'].lower() for x in iv if x.get('name')}
                if (len(acronym)>=3 and re.search(r'(?<!\w)'+re.escape(acronym)+r'(?!\w)',text,re.I)
                        and len(held.get('arms') or [])>=2 and len(names)>=2
                        and all(name in text.lower() for name in names)):
                    matches.append((n,acronym,iv))
            if len(matches)==1:
                n,acronym,iv = matches[0]
                r['nct'] = n
                r['identity_source'] = {'source':'held acronym + shared registry arms','acronym':acronym,
                                        'nct_id':n,'interventions':iv,'quote':text}
                if any(link['nct_id']!=n for link in links):
                    r['identity_link_conflicts'] = {'absence_code':'AACT_REFERENCE_CONFLICTS_WITH_NAMED_FAMILY','rows':links}
        ns = {v['nct_id'] for v in links}
        if not r.get('nct') and len(ns)==1:
            n = next(iter(ns))
            study = (index.get(n,{}).get('raw',{}).get('studies') or [{}])[0]
            start = str(study.get('start_date') or '')[:4]
            year = str(r.get('year') or '')[:4]
            if (year.isdigit() and start.isdigit() and int(year)<int(start)
                    and report_role(r)[0] not in {'PROTOCOL','SAP','DESIGN_PAPER'}):
                r['identity_link_conflicts'] = {'absence_code':'PUBLICATION_PRECEDES_TRIAL_START',
                                               'rows':links,'publication_year':r['year'],'start_date':study['start_date']}
                continue
            r['nct'] = n
            r['identity_source'] = {'source':'AACT.study_references','rows':links}
    companions = list(config.get('companion_reports') or [])
    path = root/'docs/study_families.json'
    if path.exists():
        companions += json.loads(path.read_text(encoding='utf8')).get('topics',{}).get(slug,[])
    return families(list(by_id.values()), companion_reports=companions, config=config,
                    registry=ingredients.get('records',{}), ledger=ledger)

def load_registry(root, slug):
    path = Path(root)/'cache'/slug/'family_registry.json'
    return read_registry(path).get('records',{}) if path.exists() else {}
