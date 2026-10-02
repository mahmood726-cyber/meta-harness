"""Offline definition ledger. Binding is evidence annotation, never pool admission.

All numbers come from held bytes. Table layouts below are parsing contracts,
not effect lookups. An image without a text layer remains an explicit gap.
"""
from __future__ import annotations

import hashlib
import math
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

NUM = r'(?:\d+(?:\.\d+)?|\.\d+)'
CI = rf'({NUM})\s*\(\s*(?:95%\s*CI\s*[:,]?\s*)?({NUM})\s*[,–-]\s*({NUM})\s*\)'
HR = re.compile(rf'\b(?:HR|hazard ratio)\s*[,=:]?\s*({NUM})\s*[;(\[]\s*(?:95%\s*(?:confidence interval\s*)?\(?CI\)?\s*[:,]?\s*)?({NUM})\s*[,–-]\s*({NUM})', re.I)
OUTCOME = re.compile(r'dyspn(?:ea|oea)|bleed(?:ing|s)?|hemorrhag', re.I)
PAGE = re.compile(r'^=== PAGE (\d+) ===$', re.M)


def norm(text):
    return re.sub(r'\s+', ' ', text).strip()


def variants(label):
    patterns = {
        'NON_CABG': r'non[- ]?CABG|no CABG',
        'CABG': r'(?<!non-)(?<!non )\bCABG[- ]related|^CABG',
        'NONPROCEDURAL': r'non[- ]?procedural|spontaneous',
        'PROCEDURAL': r'(?<!non-)(?<!non)\bprocedural|coronary procedural',
        'NONCORONARY': r'non[- ]coronary',
        'DISCONTINUATION': r'discontinu|drug stopped',
        'SERIOUS': r'serious|\bSAEs?\b',
        'FATAL': r'fatal', 'LIFE_THREATENING': r'life[- ]threatening',
        'OTHER_MAJOR': r'major other|other major', 'MINOR': r'minor',
        'MINIMAL': r'minimal', 'TIMI': r'\bTIMI\b',
        'SUBGROUP': r'Japan|baseline|asthma|COPD|ASA strata|through Day|No CABG',
    }
    return tuple(k for k, p in patterns.items() if re.search(p, label, re.I))


def definition(label, context='', *, effect=False):
    own = norm(label)
    if re.search(r'dyspn', own, re.I):
        # Explicit definition must belong to THIS passage/table, not a nearby table.
        defs = []
        if re.search(r'preferred terms?\s*:', context + ' ' + own, re.I):
            m = re.search(r'preferred terms?\s*:\s*([^\n]+)', context + ' ' + own, re.I)
            defs.append('PREFERRED_TERMS:' + norm(m[1]).lower())
        if re.search(r'single (?:MedDRA )?(?:PT|preferred term)|preferred term only', own + ' ' + context, re.I):
            defs.append('DYSPNEA_SINGLE_PT')
        if len(defs) > 1:
            return None
        return defs[0] if defs else (None if effect else 'DYSPNEA_REPORTED_AE')
    if re.search(r'bleed|total major|major fatal|life-threatening|major other|^fatal$', own, re.I):
        if re.search(r'\bTIMI\b', own, re.I):
            return 'TIMI:' + own.lower()
        if re.search(r'PLATO[- ]defined', own + ' ' + context, re.I):
            if re.search(r'total major|^major bleeding\s*\(PLATO-defined\)', own, re.I):
                return 'STUDY_DEFINED_TOTAL_MAJOR_BLEEDING'
            return 'PLATO:' + own.lower()
        if re.search(r'composite of major and minor bleeding', own, re.I):
            return 'COMPOSITE_MAJOR_AND_MINOR:' + own.lower()
    return None


@dataclass
class EffectRow:
    trial: str
    source: str
    page: int | None
    start: int
    end: int
    quote: str
    label: str
    definition: str | None
    variant_flags: tuple[str, ...]
    effect: float | None = None
    ci_low: float | None = None
    ci_high: float | None = None
    scale: str | None = None
    counts: dict = field(default_factory=dict)
    unit: str = 'NOT_STATED'
    population: str | None = None
    window: str | None = None
    model: str | None = None
    binding_state: str = 'UNRESOLVED'
    reason: str = ''
    poolable: bool = False
    source_sha256: str = ''
    context_quote: str = ''

    def to_dict(self):
        return asdict(self)


def make_row(text, source, trial, start, end, label, *, context='', values=None,
             counts=None, unit='NOT_STATED', flags=(), **metadata):
    quote = text[start:end]
    if not quote:
        raise ValueError('REFUSED EMPTY_SOURCE_SPAN: ' + source)
    pages = list(PAGE.finditer(text, 0, start))
    d = definition(label, context, effect=values is not None)
    row = EffectRow(trial, source, int(pages[-1][1]) if pages else None,
                    start, end, quote, norm(label), d,
                    tuple(sorted(set(variants(label) + tuple(flags)))),
                    counts=counts or {}, unit=unit, context_quote=context, **metadata)
    if values is not None:
        row.effect, row.ci_low, row.ci_high = map(float, values)
        if not all(math.isfinite(x) for x in values) or not 0 < row.ci_low <= row.effect <= row.ci_high:
            raise ValueError('REFUSED INVALID_HR_CI: ' + row.label)
        row.scale = 'HR'
    row.binding_state = 'BOUND' if d else 'UNRESOLVED'
    row.reason = 'HELD_DEFINITION' if d else 'REFUSED DEFINITION_NOT_STATED: ' + row.label
    return row


def parse_passage(text, *, trial='UNKNOWN', source='passage'):
    """One supplied passage only; no cross-passage definition inheritance."""
    rows = []
    for m in HR.finditer(text):
        # Last sentence/semicolon boundary, excluding decimal points.
        prefix = re.split(r'(?<!\d)[.;]\s+', text[:m.start()])[-1]
        start = m.start() - len(prefix)
        rows.append(make_row(text, source, trial, start, m.end(), prefix,
                             values=tuple(map(float, m.groups()))))
    return rows


def plain_outcome_binding(row, outcome):
    if row.trial not in ('PLATO', 'PHILO'):
        return 'REFUSED TRIAL_NOT_TARGET: ' + row.trial
    if row.variant_flags:
        return 'REFUSED VARIANT_FOR_PLAIN_OUTCOME: ' + ','.join(row.variant_flags)
    if row.binding_state != 'BOUND':
        return row.reason
    if outcome == 'Major bleeding' and row.definition == 'STUDY_DEFINED_TOTAL_MAJOR_BLEEDING':
        return 'BOUND'
    if outcome == 'Dyspnea' and row.definition and row.definition.startswith(('DYSPNEA_', 'PREFERRED_TERMS:')):
        return 'BOUND'
    return 'REFUSED OUTCOME_DEFINITION_MISMATCH: ' + row.label


def pair_counts(effect, counts):
    """Only an indivisible source row with the same definition may supply counts."""
    keys = ('trial', 'source', 'source_sha256', 'start', 'end', 'definition',
            'variant_flags', 'population', 'window')
    if effect.effect is None or not counts.counts:
        raise ValueError('REFUSED MISSING_EFFECT_OR_COUNTS: ' + effect.label)
    if effect.binding_state != 'BOUND' or counts.binding_state != 'BOUND':
        raise ValueError('REFUSED UNRESOLVED_DEFINITION: ' + effect.label)
    if any(getattr(effect, k) != getattr(counts, k) for k in keys):
        raise ValueError('REFUSED CROSS_DEFINITION_OR_SOURCE_ROW_COUNTS: ' + effect.label)
    if counts.unit not in ('PATIENTS', 'EVENTS_AND_PATIENTS'):
        raise ValueError('REFUSED NON_PATIENT_COUNTS: ' + counts.label)
    return {k: v for k, v in counts.counts.items() if not k.startswith('bleeding_events')}


def require_poolable(row):
    raise ValueError('REFUSED DEFINITION_LEDGER_NOT_POOL_INPUT: ' + row.label)


def medical_rows(text, source):
    rows = []
    definition_span = re.search(r'PLATO-defined .Total Major.*?assigned bleeding events', text, re.S)
    population_span = re.search(r'Table 13: Patients with Adjudicated Major Bleeds[^\n]*\n\(Patients Received at least One Dose of Treatment\)', text)
    corroboration = re.search(r'^Major Bleed (\d+) \([\d.]+\) (\d+) \([\d.]+\)', text, re.M)
    if not all((definition_span, population_span, corroboration)):
        raise ValueError('REFUSED FDA_DEFINITION_OR_PATIENT_CORROBORATION: ' + source)
    # Both revisions of the same table; keep separate page provenance.
    for table in re.finditer(r'Table \d+: Sponsor[^\n]*K-M%[^\n.]*\n(.*?)Source: p\. \d+, PLATO study report', text, re.S):
        if 'Hazard ratio' not in table[1]:
            continue
        arms = re.search(r'Ticagrelor[^\n]*\n\s*N = (\d+)\s+Clopidogrel[^\n]*\n\s*N = (\d+)', table[1])
        if not arms:
            raise ValueError('REFUSED FDA_TABLE_ARM_HEADER: ' + source)
        pattern = (rf'^\s*(Total Major|Major Fatal/ Life-threatening|Fatal|Life-threatening|Major Other)\s+'
                   rf'(\d+)\s+(\d+)\s*\({NUM}%\),\s*(?:{NUM}%|-)\s+'
                   rf'(\d+)\s+(\d+)\s*\({NUM}%\),\s*(?:{NUM}%|-)\s+({CI}|-)')
        hits = list(re.finditer(pattern, table[1], re.M))
        expected_labels = {'Total Major', 'Major Fatal/ Life-threatening', 'Fatal', 'Life-threatening', 'Major Other'}
        if {m[1] for m in hits} != expected_labels or len(hits) != len(expected_labels):
            raise ValueError('REFUSED FDA_TABLE_MISSING_OR_DUPLICATE_ROWS: ' + source)
        for m in hits:
            values = tuple(map(float, m.group(7, 8, 9))) if m[6] != '-' else None
            a, b = table.start(1) + m.start(), table.start(1) + m.end()
            if m[1] == 'Total Major' and (int(m[3]), int(m[5])) != tuple(map(int, corroboration.groups())):
                raise ValueError('REFUSED FDA_PATIENT_CORROBORATION_MISMATCH: ' + source)
            rows.append(make_row(text, source, 'PLATO', a, b, m[1],
                context=definition_span[0] + '\n' + table[0], values=values,
                counts={'bleeding_events_1': int(m[2]), 'patients_1': int(m[3]),
                        'bleeding_events_2': int(m[4]), 'patients_2': int(m[5]),
                        'n_1': int(arms[1]), 'n_2': int(arms[2])}, unit='EVENTS_AND_PATIENTS',
                population=population_span[0]))
    # Grouped dyspnea table: whitespace-split characters are joined only inside this table.
    table = re.search(r'Table 23: Dyspnea AEs, SAEs, AE leading to discontinuation in all patients and in patients\s+who had baseline asthma or COPD\s+(.*?)\n\s*vi\) Onset', text, re.S)
    if not table:
        raise ValueError('REFUSED FDA_DYSPNEA_TABLE_NOT_HELD')
    foot = re.search(r'\* Preferred Terms:.*?painful respiration\.', table[1], re.S)
    if not foot:
        raise ValueError('REFUSED FDA_DYSPNEA_DEFINITION_FOOTNOTE')
    compact = re.sub(r'\s+', '', table[1].split('Subjects with baseline asthma or COPD')[0])
    denominators = re.search(r'N(\d+)adverseevent', compact)
    safety_ns = rows[0].counts
    if not denominators or denominators[1] != str(safety_ns['n_1']) + str(safety_ns['n_2']):
        raise ValueError('REFUSED FDA_DYSPNEA_DENOMINATORS')
    cell = r'(\d+)\([\d.]+%\)'
    for label, pattern in [
        ('Dyspnea adverse event', r'(?<!serious)adverseevent'+cell+cell+r'([\d.]+)(?=serious)'),
        ('Dyspnea serious adverse event', r'seriousadverseevent'+cell+cell+r'([\d.]+)(?=adverse)'),
        ('Dyspnea adverse event, drug stopped', r'adverseevent,drugstopped'+cell+cell+r'([\d.]+)$')]:
        m = re.search(pattern, compact)
        if not m:
            raise ValueError('REFUSED FDA_DYSPNEA_COUNT_LAYOUT: ' + label)
        row = make_row(text, source, 'PLATO', table.start(), table.end(), label,
            context=norm(foot[0]), counts={'patients_1': int(m[1]), 'patients_2': int(m[2]),
            'n_1': safety_ns['n_1'], 'n_2': safety_ns['n_2']}, unit='PATIENTS')
        # Printed RR lacks a CI; retain its label and never relabel as HR.
        row.effect, row.scale = float(m[3]), 'RR_ROUNDED_NO_CI'
        rows.append(row)
    # Onset sections intentionally cannot inherit the preceding preferred-term footnote.
    for m in re.finditer(r'vi\) Onset of Dyspnea\s+(.*?)(?=vii\)|=== PAGE)', text, re.S):
        if 'HR' in m[1] and not HR.search(m[1]):
            raise ValueError('REFUSED FDA_ONSET_HR_LAYOUT')
        for hr in HR.finditer(m[1]):
            rows.append(make_row(text, source, 'PLATO', m.start(1), m.start(1)+hr.end(),
                'Dyspnea onset', values=tuple(map(float, hr.groups())),
                model='time to first event' if 'time to first event' in m[1] else None))
    # Cox tables preserve every coefficient, including covariates and interactions.
    for table in re.finditer(r'Table \d+: Cox Regression for ([^\n]*Bleeding[^\n]*(?:\n(?!No\.|N No\.)[^\n]+)?)\n', text):
        tail = text[table.end():].split('=== PAGE', 1)[0]
        if 'Haz. Ratio' not in tail:
            continue
        for m in re.finditer(rf'^([^\n|]+)\|\s*({NUM})\s+{NUM}\s+-?{NUM}\s+{NUM}\s+({NUM})\s+({NUM})\s*$', tail, re.M):
            row = make_row(text, source, 'PLATO', table.end()+m.start(), table.end()+m.end(), table[1],
                values=tuple(map(float, m.group(2, 3, 4))), flags=('ADJUSTED_COX_COEFFICIENT',),
                context=table[0] + tail[:m.start()], model='Cox regression')
            row.reason = 'REFUSED ADJUSTED_COEFFICIENT_NOT_PLAIN_EFFECT: ' + norm(m[1])
            rows.append(row)
    # Prose HRs near bleeding: preserve the clause, no inferred definitions/count joins.
    for m in HR.finditer(text):
        if any(r.start <= m.start() < r.end for r in rows):
            continue
        start = max(text.rfind('\n\n', 0, m.start()) + 2, m.start()-600)
        passage = text[start:m.end()]
        if re.search('bleed', passage, re.I):
            rows.append(make_row(text, source, 'PLATO', start, m.end(), passage,
                                 values=tuple(map(float, m.groups()))))
    # Unadjusted point-only estimates have no CI and cannot become complete effects.
    for m in re.finditer(r'\bhazard ratio\s+('+NUM+r')(?=[, ]).*?(?=;|\n)', text, re.I):
        nearby = text[max(0,m.start()-200):m.end()+180]
        if not re.search(r'bleeding rates|bleeding|bleeds', nearby, re.I) or HR.match(m[0]):
            continue
        row = make_row(text, source, 'PLATO', m.start(), m.end(), m[0], context=nearby)
        row.effect, row.scale = float(m[1]), 'HR_POINT_ONLY'
        row.reason = 'REFUSED HR_CONFIDENCE_INTERVAL_NOT_PRINTED_IN_PASSAGE: ' + row.label
        rows.append(row)
    return rows


def philo_rows(text, source):
    rows = []
    table = re.search(r'Table 3\. Adverse Events for All Patients\n(.*?)\nTable 4\.', text, re.S)
    if not table:
        raise ValueError('REFUSED PHILO_TABLE3_NOT_HELD')
    population = re.search(r'Safety data were analyzed\s+for all patients who took at least 1 dose of study medication\s+\(equivalent to the on-treatment population\)', text)
    ns = re.search(r'analysis set:\s*(\d+) in the ticagrelor group and (\d+) in the clopi-\s*dogrel group', text)
    if not population or not ns:
        raise ValueError('REFUSED PHILO_SAFETY_POPULATION_OR_DENOMINATORS')
    parent = ''
    for m in re.finditer(r'^([^\n]+)$', table[1], re.M):
        line = m[0]
        if re.match(r'(?:Major|Minor|Composite).*bleeding', line):
            parent = line.split('  ')[0].strip()
        if re.match(r'Any adverse event', line):
            parent = ''
        if not parent and not line.startswith('Dyspnea'):
            continue
        c = re.match(rf'\s*(.*?)\s+(\d+)\s*(?:\(({NUM})\))?\s+(\d+)\s*\(({NUM})\)(?:\s+{CI})?\s*$', line)
        if not c:
            raise ValueError('REFUSED PHILO_ROW_LAYOUT: ' + line)
        label = c[1] if c[1] == parent or c[1] == 'Dyspnea' else parent + ' / ' + c[1]
        values = tuple(map(float, c.group(6, 7, 8))) if c[6] else None
        rows.append(make_row(text, source, 'PHILO', table.start(1)+m.start(), table.start(1)+m.end(),
            label, context='Table 3. Adverse Events for All Patients\n' + parent, values=values,
            counts={'patients_1': int(c[2]), 'patients_2': int(c[4]),
                    'n_1': int(ns[1]), 'n_2': int(ns[2])}, unit='PATIENTS', population=population[0]))
    # Japanese subgroup is not the all-patient safety row.
    for m in re.finditer(r'In patients\s+recruited from Japan,.*?\(HR,.*?\)\.', text, re.S):
        hr = HR.search(m[0])
        if hr:
            rows.append(make_row(text, source, 'PHILO', m.start(), m.end(), 'Major bleeding / Japan',
                values=tuple(map(float, hr.groups())), flags=('SUBGROUP',)))
    return rows


def statistical_rows(text, source):
    rows = []
    table = re.search(r'Table 11 Analyses on Non CABG TIMI Major Bleeding by Median ASA in TRITON[^\S\n]*\n(.*?)(?=In summary)', text, re.S)
    if not table:
        raise ValueError('REFUSED STATR_BLEEDING_TABLE_NOT_HELD')
    for m in re.finditer(rf'^(low|high)\s+({NUM})\s+({NUM})\s+({NUM})\s+(\d+)\s+({NUM})\s+(\d+)\s+([^\n]+)', table[1], re.M):
        rows.append(make_row(text, source, 'TRITON', table.start(1)+m.start(), table.start(1)+m.end(),
            'Non CABG TIMI Major Bleeding / ASA strata ' + m[1] + ' / ' + m[8],
            values=tuple(map(float, m.group(2, 3, 4))),
            counts={'events_combined': int(m[5]), 'total_combined': int(m[7])}, unit='EVENTS',
            context=table[0].split('Median \nASA')[0]))
    if not rows or len(rows) != len(re.findall(r'^(?:low|high)\s', table[1], re.M)):
        raise ValueError('REFUSED STATR_BLEEDING_ROW_LAYOUT')
    return rows


def statement_audit(text, source):
    """Every outcome mention, with bounded surrounding held text and locator.

    Includes narrative counts, percentages, partial HRs, prior trials, headings,
    and image-only figure captions. These are audit leads, never effect rows.
    """
    result = []
    for m in OUTCOME.finditer(text):
        start = text.rfind('\n', 0, m.start()) + 1
        end = text.find('\n', m.end())
        end = len(text) if end < 0 else end
        if result and result[-1]['start'] == start:
            continue
        pages = list(PAGE.finditer(text, 0, start))
        result.append({'source': source, 'page': int(pages[-1][1]) if pages else None,
                       'start': start, 'end': end, 'quote': text[start:end],
                       'context': text[max(0,start-250):min(len(text),end+400)],
                       'state': 'AUDIT_ONLY_NOT_POOLABLE'})
    return result


def extract_documents(documents):
    rows, audit = [], []
    for key, doc in documents.items():
        parser = {'medical': medical_rows, 'statistical': statistical_rows, 'philo': philo_rows}[key]
        new = parser(doc['text'], doc['source'])
        for row in new:
            row.source_sha256 = doc['text_sha256']
        rows.extend(new)
        audit.extend(statement_audit(doc['text'], doc['source']))
    return rows, audit
