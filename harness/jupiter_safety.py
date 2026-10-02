"""Source-bound JUPITER older safety disclosures. No pool or protocol mutation.

Table 3's bare N does not prove PATIENTS versus EVENTS. A baseline denominator
cannot remove that ambiguity; reconstruction therefore remains fail-closed.
"""
from pathlib import Path
import re
from . import measure_identity, subgroup_provenance
from scripts import make_jupiter_older_table1_excerpt as source

ROOT = source.ROOT
SLUG = 'statins-primary-prevention-elderly'
DEFINITIONS = {'Muscle symptoms/myopathy': 'Muscle weakness, stiffness or pain',
               'Muscle symptoms': 'Muscle weakness, stiffness or pain',
               'Myopathy': 'Myopathy', 'New-onset diabetes': 'Newly diagnosed diabetes'}


def select_definition(outcome, labels):
    expected = DEFINITIONS.get(outcome)
    source.require(expected is not None and list(labels) == [expected],
                   f'DEFINITION_MISMATCH {outcome}: refused {list(labels)}; no substitution or addition')
    return expected


def require_age(age):
    source.require(age == 'Age 70–97 years', f'POPULATION_MISMATCH refused {age}')


def rate_as_percent(value, unit):
    source.require(unit == 'PERCENT_PATIENTS', f'RATE_NOT_PERCENT refused {value} {unit}')
    source.require(0 <= value <= 100, f'INVALID_PERCENT {value}')
    return value


def reconstruct(arms, count_span, definition, *, derivation='HELD_TABLE'):
    """Only explicitly patient-labelled counts may become a separate RR.

    Caller must have bound count_span to the same source row and age stratum.
    This pure typed guard does not constitute independent source authentication.
    """
    source.require(derivation == 'HELD_TABLE', f'COUNT_PROVENANCE refused {derivation}')
    source.require(bool(re.fullmatch(r'(?:Patients|Participants) with (?:at least one|>=1|≥1) event', count_span)),
                   f'COUNT_UNIT_UNRESOLVED {definition}: refused {count_span!r}')
    source.require(len(arms) == 2, f'COUNT_ARMS {definition}')
    for a in arms:
        require_age(a['age'])
        n, d = a['n'], a['denominator']
        source.require(type(n) is int and type(d) is int and 0 < n <= d,
                       f'COUNT_RANGE refused {definition}: {n}/{d}')
    a, c = arms
    return dict(measure='RISK_RATIO', derivation='RECONSTRUCTED',
                label=definition + ' — reconstructed RR',
                effect=(a['n']/a['denominator'])/(c['n']/c['denominator']),
                ai=a['n'], n1i=a['denominator'], ci=c['n'], n2i=c['denominator'])


def require_distinct_labels(candidates):
    labels = {}
    for c in candidates:
        m = measure_identity.normalize(c.get('measure'))
        source.require(m != measure_identity.Measure.UNKNOWN and bool(c.get('label')),
                       f'MEASURE_LABEL_UNKNOWN refused {c}')
        source.require(c['label'] not in labels or labels[c['label']] == m,
                       f'MEASURE_LABEL_COLLISION refused {c["label"]}')
        labels[c['label']] = m
    return candidates


def inspect(root=ROOT):
    soup = source.held(root)
    b = source.baseline(soup)
    dom = source.verify_table3(soup, root)
    require_age(b['age'])
    require_age(dom['age'])
    source.require((Path(root)/source.OUTPUT).read_bytes() == source.render(root), 'BASELINE_EXCERPT_MISMATCH')
    pmid = source.one(soup.select('meta[name=citation_pmid]'), 'citation PMID')['content']
    source.require(bool(re.fullmatch(r'\d{7,9}', pmid)), 'PMID_FORMAT')
    paragraphs = list(dict.fromkeys(source.text(p) for p in soup.find_all('p')))
    model = source.one([p for p in paragraphs if 'Cox proportional hazards models' in p], 'Cox methods')
    window = source.one([p for p in paragraphs if 'For safety end points including incident diabetes' in p], 'safety follow-up')
    # Full local paragraphs preserve context: prespecified outcomes are NOT a
    # prespecified age cutpoint. Capture every held paragraph on specification.
    specification_nodes = list(dict.fromkeys(source.text(p) for p in soup.find_all(['h1', 'p'])))
    spans = [p for p in specification_nodes if re.search(r'exploratory analys|cut-?point|pre-?specified|Secondary analysis of the JUPITER', p, re.I)]
    rows = {}
    for label in dict.fromkeys(DEFINITIONS.values()):
        cells = dom['rows'][label]
        match = re.fullmatch(r'(\d+\.\d+) \((\d+\.\d+)[–-](\d+\.\d+)\)', cells[4])
        source.require(match is not None, f'HR_SYNTAX {label}')
        hr, low, high = map(float, match.groups())
        source.require(0 < low <= hr <= high, f'HR_CI {label}')
        arms = [dict(a, age=b['age'], n=int(cells[i]), rate=float(cells[i+1]),
                     rate_unit='PER_100_PERSON_YEARS', count_unit='UNKNOWN')
                for a, i in zip(b['arms'], (0, 2))]
        candidate = dict(measure='HAZARD_RATIO', derivation='PUBLISHED', effect=hr,
                         ci_low=low, ci_high=high, label=label + ' — published Cox HR')
        try:
            rr = reconstruct(arms, 'N', label)
        except ValueError as exc:
            rr, refusal = None, str(exc)
        else:
            refusal = None
        rows[label] = dict(definition=label, age=b['age'], arms=arms, count_unit='UNKNOWN',
                           count_unit_basis=dict(header='Monitored adverse event', columns=dom['count_labels'],
                                                 footnotes=dom['footnotes']),
                           selected=candidate, candidates=require_distinct_labels([candidate] + ([rr] if rr else [])),
                           reconstruction_refusal=refusal, source_span=' | '.join([label]+cells),
                           selection_policy='KEEP_PUBLISHED_HR; disclose separate RR only if PATIENTS established')
    return dict(pmid=pmid, source_sha=source.SHA, source_document=source.SOURCE,
                baseline=b, rows=rows, model_span=model, safety_window_span=window,
                rate_basis=dom['footnotes'][0], person_year_denominators=None,
                person_year_refusal='Exact person-years not reported; do not invert rounded rates',
                provenance_spans=spans, provenance=subgroup_provenance.classify(' '.join(spans)))


def bind(slug, outcome, report_id, evidence):
    source.require(slug == SLUG, f'UNSUPPORTED_TOPIC {slug}')
    source.require(str(report_id) in (evidence['pmid'], 'PMID '+evidence['pmid']), f'REPORT_IDENTITY {report_id}')
    definition = select_definition(outcome, [DEFINITIONS.get(outcome)])
    row = evidence['rows'][definition]
    require_age(row['age'])
    return dict(row, report_id=report_id, state='BOUND_HR_AND_BASELINE_COUNTS_UNRESOLVED',
                source_sha=evidence['source_sha'], safety_window_span=evidence['safety_window_span'],
                model_span=evidence['model_span'])


def provenance_review(config, evidence):
    ann = config['primary_outcome']['trial_annotations'].get(evidence['pmid'], {})
    declared = ann.get('evidence_unit')
    conflict = str(declared).startswith('prespecified') and evidence['provenance']['state'] in ('POST_HOC', 'CONFLICTING_STATEMENTS')
    return dict(state=evidence['provenance']['state'], declared=declared,
                conflict='SUBGROUP_PROVENANCE_CONFLICT' if conflict else None,
                spans=evidence['provenance_spans'], annotation=ann,
                proposed_edit=dict(path='/primary_outcome/trial_annotations/'+evidence['pmid']+'/evidence_unit',
                                   before=declared, after='post_hoc_subgroup'), numeric_change=False)
