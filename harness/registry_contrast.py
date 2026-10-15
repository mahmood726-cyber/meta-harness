"""Role-preserving, fail-closed intervention contrast eligibility."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def load(config):
    path = ROOT/'cache'/str(config.get('slug', ''))/'registry_contrast.json'
    try:
        doc = json.loads(path.read_text(encoding='utf8'))
        return doc if isinstance(doc.get('records'), dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def enabled(config):
    """Apply the add-on ruling to a declared add-on/containing-regimen question.

    A vocabulary lists molecules, not the kind of contrast (e.g. substitution
    versus add-on). Read that distinction from the topic's protocol wording.
    """
    declaration = ' '.join(str(config.get(k) or '') for k in ('intervention','question'))
    return bool(config.get('intervention_agents')) and bool(re.search(
        r'add[- ]on|added to|adding .+? to|addition of|containing|\bplus\b', declaration, re.I))


def terms(config):
    agents = config.get('intervention_agents') or {}
    if isinstance(agents, dict):
        return sorted(set(str(t).lower() for k, v in agents.items() for t in [k] + list(v or [])))
    return [str(t).lower() for t in agents]


def matches(text, vocabulary):
    return any(re.search(r'(?<![\w])'+re.escape(t)+r'(?![\w])', text, re.I) for t in vocabulary)


def active(text, vocabulary):
    # A named placebo is not exposure to the matching active agent.
    text = re.sub(r"\bplacebo\s*(?:\((?:for\s+)?)?(?:(?:for|to|matching|matched to)\s+)?[A-Za-z0-9 /-]+", '', text, flags=re.I) if text.lower().strip().startswith('placebo') else text
    for t in sorted(vocabulary, key=len, reverse=True):
        text = re.sub(re.escape(t)+r'\s*[- ](?:matching\s+)?placebo\b', '', text, flags=re.I)
    return matches(text, vocabulary)


def aact_arms(raw):
    groups = raw.get('design_groups') or []
    iv = {r['id']:r for r in raw.get('interventions', [])}
    links = raw.get('design_group_interventions') or []
    out = []
    for g in groups:
        ids = [r['intervention_id'] for r in links if r['design_group_id'] == g['id']]
        if any(i not in iv for i in ids):
            return []
        names = [iv[i]['name'] for i in ids]
        out.append({'role':g.get('group_type',''), 'label':g.get('title',''),
                    'description':g.get('description',''), 'interventions':names,
                    'complete':bool(ids), 'source':g})
    return out


def v2_arms(record):
    module = record.get('protocolSection', {}).get('armsInterventionsModule', record)
    groups = module.get('armGroups') or module.get('arms') or []
    iv = module.get('interventions') or []
    out = []
    for g in groups:
        if not isinstance(g, dict):
            return []
        names = [i.get('name','') for i in iv if isinstance(i, dict) and g.get('label') in (i.get('armGroupLabels') or [])]
        names += [re.sub(r'^\w+:\s*', '', n) for n in g.get('interventionNames', [])]
        out.append({'role':g.get('type',''), 'label':g.get('label',''),
                    'description':g.get('description',''), 'interventions':names,
                    'complete':bool(names), 'source':g})
    return out


def arm_verdict(arms, vocabulary):
    if len(arms) < 2:
        return None
    values, roles, drugsets = [], [], []
    for a in arms:
        role = re.sub(r'[^A-Z]', '', a['role'].upper())
        label, desc = a['label'], a['description']
        names = a['interventions']
        present = any(active(n, vocabulary) for n in names)
        # Registry intervention links can include post-progression crossover.
        # Only remove that exposure when the initial regimen is explicitly described
        # and the agent occurs solely in the later conditional treatment clause.
        later = re.search(r'participants who.*?(?:progression|cross.?over)|(?:after|following).*?disease progression', desc, re.I)
        if later and not active(label, vocabulary) and not active(desc[:later.start()], vocabulary) and active(desc[later.start():], vocabulary):
            present = False
            names = [n for n in names if not active(n, vocabulary)]
        if role in {'PLACEBOCOMPARATOR','SHAMCOMPARATOR'} and re.search(r'placebo|sham', label+' '+desc, re.I):
            present = False
        # A labelled drug contradicted by its linked interventions is unresolved.
        if active(label, vocabulary) and not present and not re.search(r'placebo|sham', label, re.I):
            return None
        values.append(present)
        roles.append(role)
        drugsets.append({n.lower() for n in names if not re.search(r'placebo|sham', n, re.I)})
    if any(r not in {'EXPERIMENTAL','ACTIVECOMPARATOR','PLACEBOCOMPARATOR','SHAMCOMPARATOR','NOINTERVENTION'} for r in roles):
        return None
    if all(values):
        return False  # agent in every randomized regimen, irrespective of role labels
    # Many registries label both arms EXPERIMENTAL (including standard therapy).
    for i, a in enumerate(arms):
        if re.search(r'\bstandard (?:therapy|care|treatment)\b|\bcontrol arm\b', a['label'], re.I):
            roles[i] = 'ACTIVECOMPARATOR'
    if 'EXPERIMENTAL' not in roles and any(r in {'PLACEBOCOMPARATOR','SHAMCOMPARATOR','NOINTERVENTION'} for r in roles):
        roles = ['EXPERIMENTAL' if r == 'ACTIVECOMPARATOR' else r for r in roles]
    # The source-backed subset regimen is the backbone comparator in a two-arm
    # add-on design. This does not orient unrelated active-vs-active regimens.
    if len(arms) == 2 and roles == ['EXPERIMENTAL', 'EXPERIMENTAL']:
        for i in range(2):
            if drugsets[i] < drugsets[1-i]:
                roles[i] = 'ACTIVECOMPARATOR'
    controls = [v for v, r in zip(values,roles) if r in {'ACTIVECOMPARATOR','PLACEBOCOMPARATOR','SHAMCOMPARATOR','NOINTERVENTION'}]
    experiments = [v for v, r in zip(values,roles) if r == 'EXPERIMENTAL']
    if not experiments or not controls:
        return None
    if any(controls):
        return False
    if not all(a['complete'] or r == 'NOINTERVENTION' for a,r in zip(arms,roles)):
        return None
    return True if any(experiments) else None


def abstract_verdict(rec, vocabulary):
    text = rec.get('abstract') or ''
    # Restrict fallback to design/treatment descriptions, before reported results.
    methods = re.split(r'\b(?:RESULTS|FINDINGS|CONCLUSIONS?):', text, flags=re.I)[0]
    # Slash notation is an explicit active/placebo allocation in a randomized
    # placebo-controlled treatment description, including crossover studies.
    if re.search(r'randomi[sz]ed.*?placebo[- ]controlled', methods, re.I):
        for term in vocabulary:
            pair = re.search(r'(?<![\w])'+re.escape(term)+r'\s*(?:\([^)]*\))?\s*/\s*placebo\b', methods, re.I)
            if pair:
                return True, methods
    for sentence in re.split(r'(?<=[.!?])\s+', methods):
        if re.search(r'previous (?:study|trial)|previously (?:shown|reported)', sentence, re.I):
            continue
        if not re.search(r'plus|combination|receiv|assign|allocat|compar|treat|alone|placebo|intervention', sentence, re.I):
            continue
        for m in re.finditer(r'\b(?:versus|vs\.?|or|whereas|compared (?:with|to))\s+', sentence, re.I):
            left, right = sentence[:m.start()], sentence[m.end():]
            if re.match(r'\d', right.strip()):
                continue
            l, r = active(left, vocabulary), active(right, vocabulary)
            if l and r:
                return False, sentence
            absent_side = right if l else left
            if l != r and re.search(r'\balone\b|\bplacebo\b|\b(?:standard|usual)(?: of)? (?:care|therapy)\b', absent_side, re.I):
                return True, sentence
    return None, ''


def assess(rec, config, doc):
    vocabulary = terms(config)
    if not enabled(config):
        return None
    ncts = set(re.findall(r'NCT\d{8}', str(rec.get('nct') or '')+' '+str(rec.get('id') or '')))
    refs = doc.get('report_links', {}).get(str(rec.get('id')), [])
    if not ncts:
        ncts.update(r['nct_id'] for r in refs)
    evidence = []
    if len(ncts) == 1:
        nct = next(iter(ncts))
        raw = doc.get('records', {}).get(nct, {})
        arms = aact_arms(raw) if raw else v2_arms(rec)
        verdict = arm_verdict(arms, vocabulary)
        evidence = arms
        source = 'registry arms/interventions: '+nct
    else:
        verdict = None
        source = 'registry identity unavailable or ambiguous'
    if verdict is None:
        verdict, quote = abstract_verdict(rec, vocabulary)
        if quote:
            source = 'record.abstract'
            evidence = quote
    decision = 'include' if verdict is True else 'exclude' if verdict is False else 'unresolved'
    rule = 'I-CONTRAST' if verdict is True else 'X-CONTRAST' if verdict is False else 'UNRESOLVED-CONTRAST'
    reason = ('Intervention agent present in experimental arm and absent from comparator arms.' if verdict is True else
              'Intervention agent occurs in a comparator arm; not the required add-on contrast.' if verdict is False else
              'UNRESOLVED: experimental/comparator arm contrast cannot be read; not eligible for pooling.')
    return {'decision':decision,'rule_id':rule,'reason':reason+' Source: '+source,
            'span':json.dumps(evidence,ensure_ascii=False), 'source':source, 'arms':evidence}
