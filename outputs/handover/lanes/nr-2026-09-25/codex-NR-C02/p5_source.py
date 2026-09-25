# harness/trial_family.py at 1fa77f2c (excerpts, verbatim)

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


def effective_eligibility(f):
    """The eligibility cell a family EFFECTIVELY carries: the structural screen's cell after the attach-time
    overrides (a family with no registry parent is REGISTRY_PARENT_UNRESOLVED; one whose report is no longer held
    is SOURCE_RECORD_DELETED). attach_review writes this onto the node; harness/admission.py reads it BEFORE pooling
    on the un-attached node, and the gate re-reads it from the page's own copy -- one function, three readers."""
    if not (f.get('identity_basis') or {}).get('registry_ids'):
        return cell(code='REGISTRY_PARENT_UNRESOLVED')
    missing = _missing_source_ids(f)
    if missing:
        el = cell(code='SOURCE_RECORD_DELETED')
        el['missing_source_ids'] = sorted(missing)
        return el
    return f.get('eligibility') or cell()


# eligibility cell (excerpt of the structural screen)
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

