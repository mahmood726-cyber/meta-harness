"""Offline NOAC primary-source audit. Does not modify served evidence."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import xml.etree.ElementTree as ET

SLUG = 'noac-vs-warfarin-af-stroke'
TWO_SOURCE_RULE = ('TWO_SOURCE_VERIFIED requires the same typed tuple at printed precision '
                   'in two independent primary sources: trial, outcome, kind, measure and CI level stated and equal in '
                   'both, no axis stated differently by the two (population, dose, timepoint, definition), and every '
                   'value equal; an axis stated by only one source is listed as silent, never assumed to agree. '
                   'Tuples that differ on a stated axis are different analyses (INCOMPARABLE), not a conflict. '
                   'One primary is SINGLE_SOURCE; same tuple with different values is CONFLICT (both quoted, never '
                   'averaged); comparator-only is SECONDARY_ONLY.')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def fold(text):
    return re.sub(r'\s+', ' ', re.sub('[\u2010-\u2015\u2212]', '-', text)).strip()


def measurement_kind(row, outcome):
    """Units override NUMBER. Percentages and unknown units cannot become counts."""
    units = (row.get('units') or outcome.get('units') or '').lower()
    if re.search(r'year|patient.?years?|person.?years?|/yr', units):
        return 'RATE'
    if '%' in units or 'percent' in units:
        return 'PERCENTAGE'
    if re.fullmatch(r'(?:participants|patients|subjects|events|number of participants(?: with event)?)', units.strip()) and \
            row.get('param_type', '').upper() in {'NUMBER', 'COUNT_OF_PARTICIPANTS', 'COUNT_OF_UNITS'}:
        try:
            val = Decimal(row['param_value'])
            if val.is_finite() and val >= 0 and val == val.to_integral():
                return 'COUNT'
        except (KeyError, InvalidOperation):
            pass
    return 'REFUSED_UNKNOWN_OR_NONINTEGER_UNIT'


def population(text):
    text = fold(text).lower()
    if re.search(r'per.protocol', text):
        return 'PER_PROTOCOL_ON_TREATMENT' if re.search(r'on.treatment|as.treated|during treatment', text) else 'PER_PROTOCOL'
    if re.search(r'on.treatment|as.treated|safety|treated set|treated participants|during treatment', text):
        return 'ON_TREATMENT'
    if re.search(r'\bmitt\b|modified intent', text):
        return 'MODIFIED_ITT'
    if re.search(r'intention.to.treat|\bitt\b|randomized set|randomised set|all randomi[sz]ed', text):
        return 'ITT'
    return 'UNKNOWN'


def arm_role(title, drug, standard_dose):
    text = fold(title).lower()
    if text.startswith('warfarin'):
        return 'CONTROL'
    if drug.lower() not in text:
        return 'REFUSED_UNRESOLVED_ARM'
    if drug.lower() in {'dabigatran', 'edoxaban'}:
        if re.search(r'low[- ]dose', text):
            return 'REFUSED_LOW_DOSE'
        if drug.lower() == 'edoxaban' and re.search(r'high[- ]dose', text):
            return 'STANDARD'
        if not re.search(r'(?<!\d)' + re.escape(str(standard_dose)) + r'\s*mg\b', text):
            return 'REFUSED_DOSE_NOT_STANDARD'
    return 'STANDARD'


def printed_equal(a, b):
    try:
        x, y = Decimal(str(a)), Decimal(str(b))
        if not (x.is_finite() and y.is_finite()):
            return False
        precision = max(x.as_tuple().exponent, y.as_tuple().exponent)
        quantum = Decimal(1).scaleb(precision)
        return x.quantize(quantum, rounding=ROUND_HALF_UP) == y.quantize(quantum, rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError, ValueError):
        return False


SEMANTICS = ('nct', 'outcome', 'kind', 'measure', 'population', 'dose', 'timepoint', 'definition', 'ci_percent')


# Axes that must be STATED and EQUAL in both sources before two tuples are the same quantity at all.
REQUIRED_AXES = ('nct', 'outcome', 'kind', 'measure', 'ci_percent')


def _stated(v):
    return v not in (None, '', 'UNKNOWN')


def compare_facts(a, b):
    """Typed pair comparison. Four outcomes, deliberately distinct:
    INCOMPARABLE -- an axis is stated by both and differs (ITT vs on-treatment, 95% vs 97.5% CI): two DIFFERENT
                    analyses, which is neither agreement nor disagreement;
    DIFFERS      -- nothing distinguishes the two analyses, and the printed values disagree (a real conflict);
    MATCH        -- no stated axis differs and every value agrees at printed precision; axes stated by only one
                    source are listed in silent_axes, never treated as agreeing or as differing;
    UNRESOLVED   -- a required axis is unstated, or the tuples carry different value fields."""
    differences = [k.upper() + '_DIFFERS' for k in SEMANTICS if a.get(k) != b.get(k) and _stated(a.get(k)) and _stated(b.get(k))]
    silent = [k for k in SEMANTICS if not (_stated(a.get(k)) and _stated(b.get(k)))]
    unknown = [k.upper() + '_NOT_ESTABLISHED' for k in silent]
    if differences:
        return {'state': 'INCOMPARABLE', 'reasons': differences + unknown, 'silent_axes': silent}
    if any(k in silent for k in REQUIRED_AXES):
        return {'state': 'UNRESOLVED', 'reasons': unknown + ['REQUIRED_AXIS_NOT_STATED'], 'silent_axes': silent}
    av, bv = a.get('values', {}), b.get('values', {})
    if not av or set(av) != set(bv):
        return {'state': 'UNRESOLVED', 'reasons': unknown + ['INCOMPLETE_TUPLE'], 'silent_axes': silent}
    bad = [k for k in av if (str(av[k]) != str(bv[k]) if a['kind'] == 'COUNTS' else not printed_equal(av[k], bv[k]))]
    return {'state': 'DIFFERS' if bad else 'MATCH',
            'reasons': unknown + ['VALUE_DIFFERS:' + k for k in bad], 'silent_axes': silent}


def numeric_agreement(a, b):
    av, bv = a.get('values', {}), b.get('values', {})
    return bool(av) and set(av) == set(bv) and a['kind'] == b['kind'] and \
        a['measure'] == b['measure'] and a['ci_percent'] == b['ci_percent'] and \
        all(printed_equal(av[k], bv[k]) for k in av)


def route(facts):
    primary = [f for f in facts if f.get('tier') == 'PRIMARY' and f.get('span') and f.get('source_id')]
    if not primary:
        return {'state': 'SECONDARY_ONLY' if facts else 'NOT_HELD', 'reasons': ['NO_ANCHORED_PRIMARY_TUPLE']}
    independent = {f['source_id'] for f in primary}
    if len(independent) < 2:
        return {'state': 'SINGLE_SOURCE', 'reasons': ['FEWER_THAN_TWO_INDEPENDENT_PRIMARY_SOURCES']}
    pairs = [(a, b, compare_facts(a, b)) for i, a in enumerate(primary) for b in primary[i+1:]
             if a['source_id'] != b['source_id']]
    conflicts = [(a, b, p) for a, b, p in pairs if p['state'] == 'DIFFERS']
    if conflicts:  # a conflict outranks any match: both tuples are quoted, never averaged, never verified
        return {'state': 'CONFLICT', 'reasons': sorted({v for _, _, p in conflicts for v in p['reasons']}),
                'conflicting_facts': [[a.get('fact_id'), b.get('fact_id')] for a, b, _ in conflicts]}
    matches = [(a, b, p) for a, b, p in pairs if p['state'] == 'MATCH']
    if matches:  # the verified object is the matched TUPLE; other analyses in the same sources stay unverified
        return {'state': 'TWO_SOURCE_VERIFIED', 'reasons': [],
                'verified_facts': [[a.get('fact_id'), b.get('fact_id')] for a, b, _ in matches],
                'silent_axes': sorted({k for _, _, p in matches for k in p['silent_axes']})}
    return {'state': 'SINGLE_SOURCE', 'reasons': sorted({v for _, _, p in pairs for v in p['reasons']}) or
            ['NO_COMPARABLE_PAIR']}


def resolve_identity(label, records, references, studies, family_ids):
    """Require self-naming source plus exact PMID/NCT reference or unique registry title."""
    candidates = []
    needle = fold(label).lower()
    for rec in records:
        text = fold(rec.get('abstract', '') + ' ' + rec.get('title', ''))
        if not re.search(r'(?<![\w-])' + re.escape(needle) + r'(?![\w-])', text.lower()):
            continue
        for ref in references:
            if ref['pmid'] == str(rec.get('id')) and ref['nct_id'] in family_ids and \
                    ref.get('reference_type', '').lower() in {'result', 'derived'} and rec.get('nct') == ref['nct_id']:
                candidates.append({'nct': ref['nct_id'], 'pmid': ref['pmid'],
                                   'basis': 'SELF_NAMING_ABSTRACT_AND_AACT_REFERENCE_AND_EXPLICIT_NCT',
                                   'span': text, 'reference': ref})
    for st in studies:
        if st['nct_id'] in family_ids and any(needle in fold(st.get(k, '')).lower()
                                             for k in ('acronym', 'brief_title', 'official_title')):
            candidates.append({'nct': st['nct_id'], 'basis': 'AACT_ACRONYM_OR_TITLE', 'span': st})
    ncts = {c['nct'] for c in candidates}
    return {'label': label, 'state': 'MATCHED' if len(ncts) == 1 else 'UNRESOLVED',
            'nct': next(iter(ncts)) if len(ncts) == 1 else None, 'evidence': candidates,
            'reason': None if len(ncts) == 1 else 'NO_UNIQUE_DETERMINISTIC_IDENTITY_BASIS'}


def comparator(root):
    path = root / 'cache/comparators/34985309/2026-09-30_kgap_jats.xml'
    raw = path.read_bytes()
    xml = ET.fromstring(raw)
    paragraphs = [' '.join(''.join(p.itertext()).split()) for p in xml.iter('p')]
    result = {'source': str(path.relative_to(root)).replace('\\', '/'),
              'sha256': hashlib.sha256(raw).hexdigest(), 'outcomes': {}}
    for name, phrase in [('stroke_se', 'stroke/systemic embolism'), ('major_bleeding', 'major bleeding')]:
        pattern = re.compile(re.escape(phrase) + r' \((\d+)/(\d+) \[[^\]]+\] vs (\d+)/(\d+) \[[^\]]+\]; HR ([\d.]+), 95% CI ([\d.]+)[\u2013-]([\d.]+)\)')
        hits = [(p, pattern.search(p)) for p in paragraphs]
        p, m = next((p, m) for p, m in hits if m)
        result['outcomes'][name] = {'counts': dict(zip(('events_t', 'n_t', 'events_c', 'n_c'), map(int, m.groups()[:4]))),
                                    'effect': dict(zip(('effect', 'lower', 'upper'), m.groups()[4:])), 'span': m.group()}
    dose_p = next(p for p in paragraphs if p.startswith('For these analyses, a standard-dose'))
    standard = dose_p.split('A lower-dose')[0]
    result['regimens'] = [{'drug': m[0], 'dose': m[1], 'label': m[2]} for m in re.findall(
        r'(dabigatran|rivaroxaban|apixaban|edoxaban) (\d+)mg.*?\((RE-LY|ROCKET AF|ARISTOTLE|ENGAGE AF-TIMI 48)\)', standard)]
    result['dose_span'] = dose_p
    result['methods_spans'] = [p for p in paragraphs if 'Cox models were stratified' in p or
                               'Efficacy outcomes were assessed' in p or 'primary safety outcome was major bleeding' in p]
    p = next(p for p in paragraphs if 'randomized to standard-dose DOAC' in p)
    m = re.search(r'n=([\d,]+) randomized to standard-dose DOAC', p)
    result['randomized_standard_n'] = int(m[1].replace(',', ''))
    result['randomized_span'] = p
    w = [p for p in paragraphs if re.search(r'[\d,]+ on warfarin\)', p)]
    if len(w) != 1:
        raise ValueError('COMPARATOR_WARFARIN_N_NOT_UNIQUE')
    result['randomized_warfarin_n'] = int(re.search(r'([\d,]+) on warfarin\)', w[0])[1].replace(',', ''))
    result['randomized_warfarin_span'] = w[0]
    result['per_trial_status'] = 'NOT_REPORTED_BY_COMPARATOR'
    # The comparator is an NIHMS author manuscript (licence: text mining / fair use), so committed outputs carry only
    # the single SENTENCE that holds each typed value, plus the sha256 of its whole paragraph -- never paragraphs.
    def sentence(par, needle):
        hits = [x for x in re.split(r'(?<=[.;])\s+(?=[A-Z])', par) if needle in x]
        if len(hits) != 1:
            raise ValueError('COMPARATOR_SENTENCE_NOT_UNIQUE:' + needle)
        return {'excerpt': hits[0], 'paragraph_sha256': hashlib.sha256(par.encode('utf-8')).hexdigest()}
    result['dose_span'] = sentence(dose_p, 'standard-dose DOAC treatment strategy was defined')
    result['randomized_span'] = sentence(result['randomized_span'], 'randomized to standard-dose DOAC')
    result['randomized_warfarin_span'] = sentence(result['randomized_warfarin_span'], 'on warfarin)')
    needles = ['Cox models were stratified by trial', 'Efficacy outcomes were assessed using an intention-to-treat',
               'patients were censored at 32-months', 'The primary safety outcome was major bleeding']
    result['methods_spans'] = [sentence(next(p for p in result['methods_spans'] if k in p), k) for k in needles]
    return result


def outcome_key(title, category=''):
    """Composite components are never added together or substituted for their union."""
    t, c = fold(title).lower(), fold(category).lower()
    if re.search(r'\bgusto\b|\btimi\b', t):
        return None
    if c:
        return 'major_bleeding' if re.fullmatch(r'major bleed(?:s|ing)?', c) else None
    if 'stroke' in t and re.search(r'systemic|\bsee\b', t) and not re.search(
            r'death|mortality|myocardial|\bmi\b|\bpe\b|bleed|individual endpoints', t):
        return 'stroke_se'
    if re.search(r'major.*bleed', t) and not re.search(r'non.?major|minor|stroke', t):
        return 'major_bleeding'
    return None


def definition(outcome, text):
    if outcome == 'stroke_se':
        return 'STROKE_OR_SYSTEMIC_EMBOLISM'
    if 'ISTH' in text or 'International Society on Thrombosis' in text:
        return 'ISTH_MODIFIED' if 'minor modifications' in text else 'ISTH'
    return 'UNKNOWN'


def fact(nct, outcome, kind, source_id, span, **kwargs):
    return dict(nct=nct, outcome=outcome, kind=kind, source_id=source_id,
                tier='PRIMARY', span=span, measure='NA', population='UNKNOWN',
                dose='STANDARD', timepoint='UNKNOWN', definition='UNKNOWN',
                ci_percent='NA', values={}, **kwargs)


def aact_facts(index, identities, regimens):
    facts, decisions = [], []
    specs = {i['nct']: next(r for r in regimens if r['label'] == i['label'])
             for i in identities if i['state'] == 'MATCHED'}
    for o in index['outcomes']:
        spec = specs.get(o['nct_id'])
        if spec is None:
            continue
        groups = {g['id']: g for g in index['result_groups'] if g['outcome_id'] == o['id']}
        roles = {gid: arm_role(g['title'], spec['drug'], spec['dose']) for gid, g in groups.items()}
        for gid, role in roles.items():
            decisions.append({'rule': 'STANDARD_DOSE', 'item': o['id'] + '/' + gid,
                              'role': role, 'title': groups[gid]['title']})
        meta = {'population': population(o['population'] + ' ' + o['time_frame'] + ' ' + o['description']),
                'timepoint': fold(o['time_frame'])}
        measurements = [m for m in index['outcome_measurements'] if m['outcome_id'] == o['id']]
        paired = {}
        for m in measurements:
            kind = measurement_kind(m, o)
            outcome = outcome_key(o['title'], m['classification'] or m['category'])
            decisions.append({'rule': 'UNITS', 'item': m['id'], 'nct': m['nct_id'], 'kind': kind,
                              'value': m['param_value'], 'units': m['units'], 'outcome': outcome,
                              'refusal': 'OUTCOME_COMPONENT_COMPOSITE_OR_DEFINITION_NOT_TARGET' if outcome is None else
                              'RATE_NOT_EVENT_COUNT' if kind == 'RATE' else None})
            if outcome is None or roles.get(m['result_group_id']) not in ('STANDARD', 'CONTROL'):
                continue
            role = roles[m['result_group_id']]
            paired.setdefault((outcome, kind, m['classification'], m['category']), {}).setdefault(role, []).append(m)
        for (outcome, kind, classification, category), pair in paired.items():
            if set(pair) != {'STANDARD', 'CONTROL'} or any(len(v) != 1 for v in pair.values()):
                decisions.append({'rule': 'PAIR', 'item': o['id'], 'reason': 'NO_UNIQUE_STANDARD_CONTROL_PAIR'})
                continue
            rows = [pair[k][0] for k in ('STANDARD', 'CONTROL')]
            counts = []
            for m in rows:
                candidates = [c for c in index['outcome_counts'] if c['outcome_id'] == o['id'] and
                              c['result_group_id'] == m['result_group_id'] and c['scope'].lower() == 'measure' and
                              c['units'].lower() in ('participants', 'patients', 'subjects')]
                counts.append(candidates[0] if len(candidates) == 1 else None)
            f = fact(o['nct_id'], outcome, 'COUNTS' if kind == 'COUNT' else kind,
                     'AACT', {'outcome': o, 'measurements': rows, 'denominators': counts,
                              'groups': [groups[m['result_group_id']] for m in rows]})
            f.update(meta, definition=definition(outcome, o['title'] + ' ' + o['description']))
            if kind == 'COUNT' and all(counts):
                f['values'] = dict(events_t=int(rows[0]['param_value']), n_t=int(counts[0]['count']),
                                   events_c=int(rows[1]['param_value']), n_c=int(counts[1]['count']))
            elif kind in ('RATE', 'PERCENTAGE'):
                f['values'] = dict(t=rows[0]['param_value'], c=rows[1]['param_value'])
                f['units'] = rows[0]['units']
            else:
                f['refusal'] = 'NO_COMPLETE_EVENT_COUNT_DENOMINATOR_TUPLE'
            facts.append(f)
        for a in index['outcome_analyses']:
            if a['outcome_id'] != o['id']:
                continue
            links = [g for g in index['outcome_analysis_groups'] if g['outcome_analysis_id'] == a['id']]
            linked_roles = [roles.get(g['result_group_id']) for g in links]
            if sorted(str(x) for x in linked_roles) != ['CONTROL', 'STANDARD']:
                decisions.append({'rule': 'ANALYSIS_ARMS', 'item': a['id'], 'reason': 'NOT_STANDARD_VS_CONTROL', 'roles': linked_roles})
                continue
            key = outcome_key(o['title'])
            if key is None and re.search(r'bleed', o['title'], re.I):
                key = outcome_key(a['groups_description'])
            if key is None:
                continue
            if not re.search(r'hazard ratio|cox proportional hazard', a['param_type'], re.I):
                decisions.append({'rule': 'MEASURE', 'item': a['id'], 'reason': 'UNSUPPORTED_ANALYSIS_MEASURE'})
                continue
            if not all(a[k] for k in ('param_value', 'ci_lower_limit', 'ci_upper_limit', 'ci_percent')):
                decisions.append({'rule': 'CI', 'item': a['id'], 'reason': 'INCOMPLETE_HR_CI'})
                continue
            f = fact(o['nct_id'], key, 'EFFECT', 'AACT', {'outcome': o, 'analysis': a, 'analysis_groups': links,
                     'groups': [groups[g['result_group_id']] for g in links]})
            f.update(meta, measure='HR', definition=definition(key, o['title'] + ' ' + o['description']),
                     ci_percent=str(Decimal(a['ci_percent']).normalize()),
                     values=dict(effect=a['param_value'], lower=a['ci_lower_limit'], upper=a['ci_upper_limit']))
            facts.append(f)
    return facts, decisions


EFFECT_RX = re.compile(r'(hazard ratio|relative risk)(?: with \w+| in the \w+ group)?[,]?\s*'
                       r'([\d.]+);\s*([\d.]+)%\s*(?:confidence interval \[CI\]|CI),\s*([\d.]+) to ([\d.]+)', re.I)


def abstract_facts(records, identities, regimens):
    facts = []
    for ident in identities:
        if ident['state'] != 'MATCHED':
            continue
        spec = next(r for r in regimens if r['label'] == ident['label'])
        for rec in records:
            if rec.get('id_type') != 'pmid' or rec.get('nct') != ident['nct']:
                continue
            text = rec.get('abstract', '')
            # Sentences split only at punctuation followed by capital letters, never decimal points.
            for sentence in re.split(r'(?<=[.!?])\s+(?=[A-Z])', text):
                low = sentence.lower()
                key = 'major_bleeding' if 'major bleeding' in low and not re.search(r'nonmajor|non-major', low) else None
                if key is None and ('primary' in low or 'intention-to-treat analysis' in low) and \
                        'stroke or systemic embolism' in text.lower() and 'bleed' not in low:
                    key = 'stroke_se'
                if key is None:
                    continue
                for m in EFFECT_RX.finditer(sentence):
                    prefix = sentence[:m.start()]
                    if key == 'major_bleeding' and re.search(r'death|mortality', prefix, re.I):
                        continue
                    if spec['drug'] in ('edoxaban', 'dabigatran'):
                        if spec['drug'] == 'edoxaban':
                            mentions = list(re.finditer(r'(high|low)-dose edoxaban', prefix, re.I))
                            if not mentions or mentions[-1][1].lower() != 'high':
                                continue
                        else:
                            mentions = list(re.finditer(r'(\d+) mg of dabigatran', prefix, re.I))
                            if not mentions or mentions[-1][1] != spec['dose']:
                                continue
                    f = fact(ident['nct'], key, 'EFFECT', 'PUBMED:' + rec['id'], sentence)
                    pop = population(sentence)
                    if pop == 'UNKNOWN' and spec['drug'] == 'rivaroxaban' and 'primary analysis' in low:
                        pop = population(next((s for s in re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
                                               if 'per-protocol' in s), ''))
                    f.update(measure='HR' if m[1].lower() == 'hazard ratio' else 'RR', population=pop,
                             definition=definition(key, sentence), ci_percent=m[3],
                             values=dict(effect=m[2], lower=m[4], upper=m[5]),
                             source_ref=f'cache/{SLUG}/records.json#{rec["id"]}',
                             timepoint='UNKNOWN')
                    facts.append(f)
            # Explicit event numerators are preserved without inventing arm denominators.
            if spec['drug'] == 'rivaroxaban':
                for s in re.split(r'(?<=[.!?])\s+(?=[A-Z])', text):
                    m = re.search(r'primary end point occurred in (\d+) patients.*?and in (\d+)(?: patients)? in the warfarin group', s)
                    if m:
                        f = fact(ident['nct'], 'stroke_se', 'NUMERATORS_ONLY', 'PUBMED:' + rec['id'], s)
                        f.update(population=population(s), values={'events_t': int(m[1]), 'events_c': int(m[2])},
                                 refusal='ARM_DENOMINATORS_NOT_REPORTED_IN_ABSTRACT')
                        facts.append(f)
            # RE-LY abstract has annualized bleeding rates, but no bleeding effect/CI.
            if spec['drug'] == 'dabigatran':
                for s in re.split(r'(?<=[.!?])\s+(?=[A-Z])', text):
                    m = re.search(r'rate of major bleeding was ([\d.]+)% per year in the warfarin group.*?([\d.]+)% per year in the group receiving ' + spec['dose'] + r' mg', s)
                    if m:
                        f = fact(ident['nct'], 'major_bleeding', 'RATE', 'PUBMED:' + rec['id'], s)
                        f.update(values={'t': m[2], 'c': m[1]}, units='% per year')
                        facts.append(f)
    return facts


def fda_facts(root, identities):
    facts = []
    for path in sorted((root / 'evidence/acquisition_cascade/excerpts').glob('*FDA*')):
        text = path.read_text(encoding='utf-8')
        label = 'RE-LY' if 'PRADAXA' in text else 'ROCKET AF' if 'XARELTO' in text else None
        ident = next((i for i in identities if i['label'] == label and i['state'] == 'MATCHED'), None)
        if ident is None:
            continue
        # Only table body, excluding explanatory header comments.
        body = text.split('=== TABLES (excerpt) ===')[-1]
        m = re.search(r'^Major [^|]+\|\s*(\d+)\s*\([\d.]+\)\s*\|\s*(\d+)\s*\([\d.]+\)\s*\|\s*([\d.]+)\s*\(([\d.]+),\s*([\d.]+)\)', body, re.M)
        if not m:
            raise ValueError('FDA_MAJOR_ROW_NOT_PARSED:' + path.name)
        n = re.search(r'Randomized patients\s*\|\s*(\d+)\s*\|\s*(\d+)', body)
        if n is None:
            n = re.search(r'XARELTO N=(\d+).*?Warfarin N=(\d+)', body)
        if n is None:
            raise ValueError('FDA_DENOMINATORS_NOT_PARSED:' + path.name)
        f = fact(ident['nct'], 'major_bleeding', 'EFFECT', 'FDA:' + path.name, text)
        ci = re.search(r'(\d+)% CI', body)
        f.update(measure='HR', ci_percent=ci[1], values=dict(zip(('effect', 'lower', 'upper'), m.groups()[2:])),
                 population=population(body), source_ref=str(path.relative_to(root)).replace('\\', '/'),
                 sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                 timepoint='ON_TREATMENT_PLUS_2_DAYS' if re.search(r'On Treatment Plus 2 Days', body, re.I) else 'UNKNOWN',
                 source_held_text_sha256=re.search(r'sha256 ([a-f0-9]{64})', text)[1])
        facts.append(f)
        c = dict(f, kind='COUNTS', measure='NA', ci_percent='NA',
                 values={'events_t': int(m[1]), 'n_t': int(n[1]), 'events_c': int(m[2]), 'n_c': int(n[2])})
        facts.append(c)
    return facts


def count_census(items, selected):
    names = sorted(selected)
    return {'n': len(names), 'N': len(items), 'n_of_N': f'{len(names)} of {len(items)}', 'items': names}


def denominator_reproduction(index, identities, comp):
    """Arithmetic about how the comparator built its denominators -- never a result of ours.
    For each comparator total T (randomised, and each outcome's analysed N per arm): residual = T minus the sum of the
    four trials' AACT 'STARTED' arm sizes. The IMPLIED contribution of trial t is T minus the other three trials' AACT
    sizes -- valid only under the stated assumption that those three contributed exactly their AACT sizes."""
    started = {}
    regimens = {r['label']: r for r in comp['regimens']}
    for ident in identities:
        spec = regimens[ident['label']]
        groups = {g['id']: g for g in index['result_groups'] if g['nct_id'] == ident['nct']}
        arms = {'t': [], 'c': []}
        for m in index['milestones']:
            if m['nct_id'] != ident['nct'] or m['title'].strip().upper() != 'STARTED' or m['result_group_id'] not in groups:
                continue
            role = arm_role(groups[m['result_group_id']]['title'], spec['drug'], spec['dose'])
            if role == 'STANDARD':
                arms['t'].append(int(m['count']))
            elif role == 'CONTROL':
                arms['c'].append(int(m['count']))
        if len(arms['t']) != 1 or len(arms['c']) != 1:
            raise ValueError('STARTED_ARMS_NOT_UNIQUE:' + ident['label'] + ':' + json.dumps(arms))
        started[ident['label']] = {'t': arms['t'][0], 'c': arms['c'][0], 'source': 'AACT milestones STARTED'}
    targets = {'randomized': {'t': comp['randomized_standard_n'], 'c': comp['randomized_warfarin_n']}}
    for key, o in comp['outcomes'].items():
        targets[key + '_analysed'] = {'t': o['counts']['n_t'], 'c': o['counts']['n_c']}
    out = {}
    for name, tgt in targets.items():
        per_arm = {}
        for arm in ('t', 'c'):
            total = sum(v[arm] for v in started.values())
            implied = {lab: tgt[arm] - (total - started[lab][arm]) for lab in started}
            per_arm[arm] = {'comparator': tgt[arm], 'aact_started_sum': total, 'residual': tgt[arm] - total,
                            'implied_if_others_exact': {lab: implied[lab] for lab in started}}
        out[name] = per_arm
    return {'aact_started': started, 'targets': out,
            'label': ('DENOMINATOR_ARITHMETIC_ONLY: AACT STARTED is participant flow, not proof of randomisation (ROCKET AF '
                      'STARTED counts treated participants); implied values are not held in any primary source')}


def audit(root, index):
    """Pure replay from the captured AACT index and held clone sources."""
    from .trial_family import load_registry
    from .synth import Study, pool
    from dataclasses import asdict
    root = Path(root)
    comp = comparator(root)
    review = read_json(root / 'docs/reviews' / SLUG / 'review.json')
    records = read_json(root / 'cache' / SLUG / 'records.json')['records']
    families = load_registry(root, SLUG)
    identities = [resolve_identity(s['label'], records, index['study_references'], index['studies'], families)
                  for s in comp['regimens']]
    facts, decisions = aact_facts(index, identities, comp['regimens'])
    facts += abstract_facts(records, identities, comp['regimens'])
    facts += fda_facts(root, identities)
    for i, f in enumerate(facts):
        f['fact_id'] = f'F{i+1:03}'
    rows = []
    for ident in identities:
        for key in ('stroke_se', 'major_bleeding'):
            held = [f for f in facts if f['nct'] == ident['nct'] and f['outcome'] == key]
            effects = [f for f in held if f['kind'] == 'EFFECT']
            tuple_routes = {kind: route([f for f in held if f['kind'] == kind])
                            for kind in sorted({f['kind'] for f in held})}
            row_route = route(effects)
            conflicts = [v for v in tuple_routes.values() if v['state'] == 'CONFLICT']
            if conflicts:
                row_route = {'state': 'CONFLICT', 'reasons': sorted({reason for v in conflicts for reason in v['reasons']})}
            crosschecks = []
            for i, a in enumerate(effects):
                for b in effects[i+1:]:
                    if a['source_id'] == b['source_id']:
                        continue
                    crosschecks.append({'facts': [a['fact_id'], b['fact_id']],
                                        'numeric_agreement_only': numeric_agreement(a, b), **compare_facts(a, b)})
            # Alternatives are retained; a row never selects whichever population happens to agree.
            row = {'item': ident['label'] + '/' + key, 'nct': ident['nct'], 'outcome': key,
                   'route': row_route, 'effect_route': route(effects), 'tuple_routes': tuple_routes,
                   'fact_ids': [f['fact_id'] for f in held], 'crosschecks': crosschecks}
            outcome = next(o for o in review['outcomes'] if ('major' in o['name'].lower()) == (key == 'major_bleeding'))
            served = next((t for t in outcome['trials'] if t['family_id'] == ident['nct']), None)
            if served is None:
                row['served_comparison'] = {'state': 'NOT_SERVED', 'reasons': ['EXTRACTION_DEBT'],
                                            'source': 'review.json/outcomes/trials'}
            else:
                matches = [f['fact_id'] for f in effects if f['measure'] == served['scale'] and
                           all(printed_equal(f['values'][k], served[s]) for k, s in
                               [('effect', 'effect'), ('lower', 'ci_low'), ('upper', 'ci_high')])]
                reasons = []
                if served.get('analysis_set_literal') == 'ITT' and served.get('analysis_set') == 'per-protocol':
                    reasons.append('SERVED_POPULATION_FIELDS_CONTRADICT:ITT_vs_per-protocol')
                # Compare source CI level before classifying a transformed served interval as an error.
                transformed = []
                for f in effects:
                    if f['population'] != 'ITT' or f['measure'] != served['scale'] or f['ci_percent'] == '95':
                        continue
                    import math
                    from scipy.stats import norm
                    z = norm.ppf((1 + float(f['ci_percent']) / 100) / 2)
                    se = (math.log(float(f['values']['upper'])) - math.log(float(f['values']['lower']))) / (2 * z)
                    bounds = [math.exp(math.log(float(f['values']['effect'])) + sign * norm.ppf(.975) * se) for sign in (-1, 1)]
                    if all(abs(x - served[k]) <= .0005 for x, k in zip(bounds, ('ci_low', 'ci_high'))):
                        transformed.append({'fact_id': f['fact_id'], 'source_ci_percent': f['ci_percent'], 'derived_95': bounds})
                row['served_comparison'] = {'state': 'DIFFERS' if reasons or not (matches or transformed) else 'MATCH',
                    'comparison_scope': 'reported estimate/CI only; full semantic verification remains the route above',
                    'reasons': reasons or ([] if matches or transformed else ['NO_PRIMARY_ESTIMATE_CI_MATCH']),
                    'matching_facts': matches, 'ci_transform_matches': transformed,
                    'served': {k: served.get(k) for k in ('id', 'effect', 'ci_low', 'ci_high', 'scale',
                                                        'analysis_set_literal', 'analysis_set', 'dose_regimen')}}
            # Is the SERVED estimate itself one of the two-source-verified tuples? (A row can verify a different
            # analysis -- e.g. per-protocol -- while serving the ITT estimate from a single source.)
            verified_ids = {x for pair in row['effect_route'].get('verified_facts', []) for x in pair}
            row['served_tuple_two_source'] = bool(verified_ids & set(row['served_comparison'].get('matching_facts', [])))
            rows.append(row)

    reproduction = []
    for key in ('stroke_se', 'major_bleeding'):
        target = comp['outcomes'][key]['counts']
        for pop in ('ITT', 'ON_TREATMENT'):
            selected, missing = [], []
            for ident in identities:
                candidates = [f for f in facts if f['nct'] == ident['nct'] and f['outcome'] == key and
                              f['kind'] == 'COUNTS' and f['population'] == pop and len(f['values']) == 4]
                verified = [f for f in candidates if route([f] + [g for g in candidates if g is not f and
                            g['source_id'] != f['source_id']])['state'] == 'TWO_SOURCE_VERIFIED']
                unique = {json.dumps(f['values'], sort_keys=True): f for f in verified}
                if len(unique) == 1:
                    selected.append(next(iter(unique.values())))
                else:
                    missing.append(ident['label'])
            subtotal = {k: sum(f['values'][k] for f in selected) for k in target}
            reproduction.append({'outcome': key, 'population': pop, 'tier': 'TWO_SOURCE_VERIFIED_ONLY',
                'state': 'INCOMPLETE' if missing else 'EXACT' if subtotal == target else 'DIFFERS',
                'k': len(selected), 'N': len(identities), 'missing': missing,
                'verified_subtotal': subtotal, 'target': target,
                'unexplained_target_minus_verified_subtotal': {k: target[k] - subtotal[k] for k in target},
                'residual_interpretation': 'An incomplete subtotal is not a four-trial reproduction residual.'})
    # Additional exploratory arithmetic, not verification: all held primary count tuples, including unknown populations.
    import itertools
    for key in ('stroke_se', 'major_bleeding'):
        choices = []
        missing = []
        for ident in identities:
            candidates = [f for f in facts if f['nct'] == ident['nct'] and f['outcome'] == key and
                          f['kind'] == 'COUNTS' and len(f['values']) == 4]
            if not candidates:
                missing.append(ident['label'])
            choices.append(candidates)
        combinations = []
        target = comp['outcomes'][key]['counts']
        for combo in itertools.product(*choices):
            total = {k: sum(f['values'][k] for f in combo) for k in target}
            combinations.append({'facts': [f['fact_id'] for f in combo], 'total': total,
                                 'target_minus_total': {k: target[k]-total[k] for k in target}, 'exact': total == target,
                                 'populations': [f['population'] for f in combo]})
        reproduction.append({'outcome': key, 'tier': 'SINGLE_SOURCE_DIAGNOSTIC_NOT_VERIFIED',
                             'state': 'INCOMPLETE' if missing else 'DIAGNOSTIC_ONLY',
                             'missing': missing, 'combinations': combinations,
                             'censoring_warning': comp['methods_spans'][2]['excerpt']})
    # Participant-flow STARTED is not automatically randomised (ROCKET starts with treated participants).
    starts = []
    for ident in identities:
        spec = next(s for s in comp['regimens'] if s['label'] == ident['label'])
        candidates = []
        for m in index['milestones']:
            if m['nct_id'] != ident['nct'] or m['title'].lower() != 'started':
                continue
            g = next(g for g in index['result_groups'] if g['id'] == m['result_group_id'])
            if arm_role(g['title'], spec['drug'], spec['dose']) == 'STANDARD':
                candidates.append({'milestone': m, 'group': g})
        starts.append({'label': ident['label'], 'candidates': candidates})
    start_total = sum(int(x['candidates'][0]['milestone']['count']) for x in starts if len(x['candidates']) == 1)
    reproduction.append({'outcome': 'randomized_standard_n', 'state': 'NOT_VERIFIED', 'target': comp['randomized_standard_n'],
                         'started_diagnostic_sum': start_total, 'target_minus_started': comp['randomized_standard_n']-start_total,
                         'rows': starts, 'reason': 'STARTED_IS_NOT_PROOF_OF_RANDOMIZED;TWO_SOURCE_N_NOT_HELD'})

    proposed_inputs = []
    for ident in identities:
        candidates = [f for f in facts if f['nct'] == ident['nct'] and f['outcome'] == 'major_bleeding' and f['kind'] == 'EFFECT']
        # FDA body is the independent source of the formerly unbound RELY/ROCKET rows;
        # otherwise use the published abstract. Selection does not upgrade verification.
        chosen = next((f for f in candidates if f['source_id'].startswith('FDA:')), None)
        if chosen is None:
            chosen = next((f for f in candidates if f['source_id'].startswith('PUBMED:')), None)
        if chosen:
            proposed_inputs.append(chosen)
    row_by_nct = {r['nct']: r for r in rows if r['outcome'] == 'major_bleeding'}
    two_source = [f['fact_id'] for f in proposed_inputs
                  if any(f['fact_id'] in pair for pair in row_by_nct[f['nct']]['effect_route'].get('verified_facts', []))]
    all_verified = len(two_source) == len(identities)
    proposed = {'label': 'PROPOSED_SENSITIVITY_NOT_SERVED_' + ('ALL_INPUTS_TWO_SOURCE' if all_verified else
                                                                'NOT_ALL_INPUTS_TWO_SOURCE_VERIFIED'),
                'admissible_to_verified_pool': False, 'inputs': [f['fact_id'] for f in proposed_inputs],
                'inputs_two_source_verified': two_source,
                'reason': (f'{len(two_source)} of {len(proposed_inputs)} input HRs are two-source verified; populations and '
                           'definitions differ across trials (safety vs unstated populations; ISTH vs modified-ISTH); '
                           'source-anchored HR arithmetic only, never served.')}
    if len(proposed_inputs) == len(identities) and all(f['ci_percent'] == '95' for f in proposed_inputs):
        studies = [Study(label=f['nct'], measure=f['measure'], effect=float(f['values']['effect']),
                        ci_low=float(f['values']['lower']), ci_high=float(f['values']['upper'])) for f in proposed_inputs]
        proposed['result'] = asdict(pool(studies, scale='HR'))
    else:
        proposed['state'] = 'REFUSED_INCOMPLETE_STANDARD_DOSE_HR95_INPUTS'
    served_result = review['outcomes'][0]['result']
    comp_point = comp['outcomes']['stroke_se']['effect']['effect']
    result_comparison = {'served': served_result, 'point_agrees_at_comparator_precision': printed_equal(served_result['estimate'], comp_point),
        'method_difference': review['method_declared'], 'comparator_methods': comp['methods_spans'],
        'measure_difference': served_result.get('effect_label'),
        'major_bleeding_served': next(o['result'] for o in review['outcomes'] if 'major' in o['name'].lower())}
    topics = sorted(p.stem for p in (root / 'topics').glob('*.json'))
    # Parse every topic; this lane is deliberately topic-specific, other topics are not asserted safe.
    for slug in topics:
        read_json(root / 'topics' / (slug + '.json'))
    census = {'topic_scope': count_census(topics, [SLUG] if SLUG in topics else []),
              'out_of_scope_topics': [s for s in topics if s != SLUG],
              'k_matched': count_census(identities, [i['label'] for i in identities if i['state'] == 'MATCHED']),
              'routes': {state: count_census(rows, [r['item'] for r in rows if r['route']['state'] == state])
                         for state in ('TWO_SOURCE_VERIFIED', 'SINGLE_SOURCE', 'CONFLICT', 'NOT_HELD', 'SECONDARY_ONLY')},
              'served_comparisons': {state: count_census(rows, [r['item'] for r in rows if r['served_comparison']['state'] == state])
                                    for state in ('MATCH', 'DIFFERS', 'NOT_SERVED')}}
    measurements = [d for d in decisions if d['rule'] == 'UNITS']
    census['rates_refused_as_events'] = count_census(measurements, [d['item'] for d in measurements if d['kind'] == 'RATE'])
    base_eligible = [m for m in index['outcome_measurements'] if not (m['category'] or m['classification']) and
                     m['param_type'].upper() in {'NUMBER', 'COUNT_OF_PARTICIPANTS', 'COUNT_OF_UNITS'}]
    rate_ids = {d['item'] for d in measurements if d['kind'] == 'RATE'}
    census['base_number_as_count_changed'] = count_census(base_eligible, [m['id'] for m in base_eligible if m['id'] in rate_ids])
    arms = [d for d in decisions if d['rule'] == 'STANDARD_DOSE']
    census['nonstandard_arms_refused'] = count_census(arms, [d['item'] for d in arms if d['role'].startswith('REFUSED')])
    census['numeric_agreement_not_full_verification'] = count_census(rows, [r['item'] for r in rows if
        any(c['numeric_agreement_only'] for c in r['crosschecks']) and r['route']['state'] != 'TWO_SOURCE_VERIFIED'])
    all_pairs = [(r['item'] + ':' + '/'.join(c['facts']), c) for r in rows for c in r['crosschecks']]
    for key in ('POPULATION', 'TIMEPOINT', 'DEFINITION', 'CI_PERCENT', 'MEASURE'):
        census[key.lower() + '_refusals'] = count_census(all_pairs, [name for name, c in all_pairs
            if any(reason.startswith(key + '_') for reason in c['reasons'])])
    census['outcome_binding_refusals'] = count_census(measurements, [d['item'] for d in measurements if d['outcome'] is None])
    primary_effects = [f for f in facts if f['kind'] == 'EFFECT']
    secondary_labels = ['COMBINE_AF/' + key for key in comp['outcomes']]
    census['comparator_only_excluded_from_primary_verification'] = count_census(primary_effects + secondary_labels, secondary_labels)
    census['reproduction'] = [{k: v for k, v in r.items() if k not in ('rows', 'censoring_warning')} for r in reproduction]
    census['denominator_reproduction'] = denominator_reproduction(index, identities, comp)
    held_paths = [root / 'cache' / SLUG / 'records.json', root / 'docs/reviews' / SLUG / 'review.json',
                  # The model-proposal store is deliberately NOT read: a harness module never touches it
                  # (tests/test_model_source.py import/read sweep).
                  root / 'outputs/k_gap/k_gap_table.csv',
                  root / 'outputs/k_gap/G1_STATUS.md']
    return {'two_source_rule': TWO_SOURCE_RULE,
            'held_source_digests': {str(p.relative_to(root)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in held_paths},
            'comparator': comp, 'identities': identities, 'facts': facts,
            'rows': rows, 'decisions': decisions, 'reproduction': reproduction, 'proposed_major_bleeding': proposed,
            'result_comparison': result_comparison, 'census': census, 'aact': index}


def render_report(data):
    lines = ['# G1 NOAC primary-source audit', '', TWO_SOURCE_RULE, '',
             'Identity matching is separate from verified value matching. Nothing here changes served results.', '',
             '| Trial/outcome | Route | Served estimate comparison |', '|---|---|---|']
    for r in data['rows']:
        lines.append(f'| {r["item"]} | {r["route"]["state"]} | {r["served_comparison"]["state"]} |')
    lines += ['', '## Comparator evidence', '']
    for o in data['comparator']['outcomes'].values():
        lines += ['> ' + o['span'], '']
    for s in [data['comparator']['dose_span'], data['comparator']['randomized_span'],
              data['comparator']['randomized_warfarin_span']] + data['comparator']['methods_spans']:
        lines += ['> ' + s['excerpt'] + ' [paragraph sha256 ' + s['paragraph_sha256'][:12] + ']', '']
    lines += ['## Source tuples', '', 'Full AACT records, row hashes, excerpts and abstract spans are in g1_noac.json.', '',
              '| Fact | NCT / outcome | Source | Kind / population / definition | Values |', '|---|---|---|---|---|']
    for f in data['facts']:
        lines.append(f'| {f["fact_id"]} | {f["nct"]} / {f["outcome"]} | {f["source_id"]} | '
                     f'{f["kind"]} / {f["population"]} / {f["definition"]} | {json.dumps(f["values"])} |')
    lines += ['', '## Proposed arithmetic only', '', '```json', json.dumps(data['proposed_major_bleeding'], indent=2), '```', '',
              '## Census and reproduction', '', '```json', json.dumps(data['census'], indent=2), '```', '']
    return '\n'.join(lines)


def scan_aact(snapshot, ncts):
    """Filter raw pipe-delimited records before decoding; retain exact rows and hashes."""
    tables = {}
    needles = {n.encode() for n in ncts}
    for table in ('studies', 'study_references', 'id_information', 'outcomes',
                  'result_groups', 'outcome_measurements', 'outcome_counts',
                  'outcome_analyses', 'outcome_analysis_groups', 'milestones'):
        selected = []
        with (Path(snapshot) / (table + '.txt')).open('rb') as fh:
            header = fh.readline().decode('utf-8').rstrip('\r\n').split('|')
            if 'nct_id' not in header:
                raise ValueError('MISSING_COLUMN:' + table + ':nct_id')
            nct_col = header.index('nct_id')
            for line_no, raw in enumerate(fh, 2):
                # nct_id is an exact early field, not a mention in a citation.
                if raw.split(b'|', nct_col + 1)[nct_col] not in needles:
                    continue
                cells = raw.decode('utf-8').rstrip('\r\n').split('|')
                if len(cells) != len(header):
                    raise ValueError(f'MALFORMED_ROW:{table}:{line_no}')
                row = dict(zip(header, cells))
                row['_source'] = {'table': table, 'line': line_no,
                                  'row_sha256': hashlib.sha256(raw).hexdigest(),
                                  'snapshot': Path(snapshot).name}
                selected.append(row)
        tables[table] = selected
    return tables
