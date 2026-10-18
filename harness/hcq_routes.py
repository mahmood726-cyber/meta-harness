"""Declared HCQ benchmark routes. Static locators; all counts read from held bytes."""
import hashlib
import json
import re
from pathlib import Path

KEY = 'hcq_covid_prophylaxis'
SLUG = 'hcq-covid-prophylaxis-bench'
LOCATORS = {
    '10.1056/NEJMoa2016638': r'The incidence of new illness compatible with Covid-19.*?; the absolute difference',
    '10.1001/jamainternmed.2020.6319': r'There was no significant difference in infection rates.*?; P',
}

def for_config(config, root):
    if config.get('slug') != SLUG or config.get('typed_routes') != KEY:
        raise ValueError('HCQ route declaration is mis-scoped')
    spec = config['primary_outcome']
    if spec['name'] != 'Developing COVID-19' or spec['estimand'] != 'RR':
        raise ValueError('HCQ route outcome mismatch')
    ref = f'cache/{SLUG}/records.json'
    raw = (Path(root)/ref).read_bytes()
    records = json.loads(raw)['records']
    result = {}
    for doi, pattern in LOCATORS.items():
        hits = [r for r in records if r.get('doi', '').lower() == doi.lower()]
        if len(hits) != 1:
            raise ValueError('HCQ report identity ambiguous or missing: '+doi)
        rec = hits[0]
        matches = list(re.finditer(pattern, rec['abstract']))
        if len(matches) != 1:
            raise ValueError('HCQ outcome span ambiguous or missing: '+doi)
        span = matches[0].group()
        if not re.search(r'hydroxychloroquine.*placebo', span, re.I):
            raise ValueError('HCQ arm orientation not bound')
        cells = re.findall(r'(\d+) of (\d+) \[(\d+(?:\.\d+)?)%\]', span)
        if len(cells) != 2:
            raise ValueError('HCQ count pairs not bound')
        for events, total, pct in cells:
            if not 0 < int(events) < int(total) or abs(100*int(events)/int(total)-float(pct)) > .11:
                raise ValueError('HCQ counts fail percentage corroboration')
        (a, n, _), (c, m, _) = cells
        result[rec['id']] = dict(outcome=spec['name'], override=True,
            ai=int(a), n1i=int(n), ci=int(c), n2i=int(m),
            provenance='abstract_verified', source=span, source_span=span,
            document_ref=ref, document_sha256=hashlib.sha256(raw).hexdigest(),
            source_level=1, kind='extracted_counts',
            verification='HCQ anchored primary-result counts with percentage corroboration')
    result.update(table_routes(config, root, records))
    return result

def table_routes(config, root, records):
    import xml.etree.ElementTree as ET
    result = {}
    for doi, name in [('10.1093/cid/ciaa1571', 'PMC7665393'),
                      ('10.1056/NEJMoa2021801', 'PMC7722693')]:
        rec = next(r for r in records if r.get('doi') == doi)
        ref = f'cache/{SLUG}/{name}.xml'
        raw = (Path(root)/ref).read_bytes()
        doc = ET.fromstring(raw)
        ids = {e.get('pub-id-type'): e.text for e in doc.findall('.//article-meta/article-id')}
        if ids.get('pmid') != rec['id'] or ids.get('doi', '').lower() != doi.lower():
            raise ValueError('HCQ fulltext identity mismatch')
        tables = list(doc.iter('table-wrap'))
        def rows(table):
            return [[''.join(c.itertext()).strip() for c in tr] for tr in table.iter('tr')]
        base = dict(outcome=config['primary_outcome']['name'], override=True,
            document_ref=ref, document_sha256=hashlib.sha256(raw).hexdigest(),
            source_level=1, provenance='fulltext_verified')
        if name == 'PMC7665393':
            # The primary events exclude illness before medication. Table 1 is
            # explicitly randomized N, not that analysis set. Never pair them.
            paragraphs = re.findall(r'<p[ >].*?</p>', raw.decode('utf8'), re.S)
            evidence = [p for p in paragraphs if 'excluded from the primary analysis' in p]
            if len(evidence) != 1:
                raise ValueError('HCQ primary-analysis exclusion evidence unbound')
            base.update(absent=True, kind='typed_refusal', provenance='REFUSED_ON_EVIDENCE',
                refusal_provenance='REFUSED_ON_EVIDENCE', reason_code='NO_OPEN_SOURCE', reason='NO_OPEN_SOURCE-for-denominator: primary-analysis events exclude illness before initiating study medicine; held Table 1 gives randomized denominators only. Referenced supplementary tables are not embedded in the held XML.',
                source=evidence[0], source_span=evidence[0])
            result[rec['id']] = base
            continue
        else:
            if config.get('design_effect_conversion'):
                result[rec['id']] = effective_counts(config, root, raw, doc, base)
                continue
            outcomes = next(t for t in tables if t.get('id') == 't2')
            row = next(r for r in rows(outcomes) if r[0] == 'Covid-19, either symptomatically compatible or PCR positivity regardless of symptoms')
            values = re.fullmatch(r'(\d+\.\d+) \((\d+\.\d+)[–-](\d+\.\d+)\)', row[3])
            if not values:
                raise ValueError('HCQ adjusted RR cell unbound')
            base.update(zip(('effect', 'ci_low', 'ci_high'), map(float, values.groups())))
            base.update(scale='RR', kind='extracted_effect', typed_route='hcq_adjusted_infection_rr',
                        verification='Table 2 broad infection endpoint; use published adjusted RR accounting for clustering, not naive person counts.')
        # Preserve original XML bytes as the cited span; the downstream binder must
        # independently admit the tuple (combined counts may remain extraction debt).
        blocks = re.findall(r'<table-wrap\b.*?</table-wrap>', raw.decode('utf8'), re.S)
        span = next(b for b in blocks if ('id="'+outcomes.get('id')+'"') in b)
        if name == 'PMC7722693':
            paras = re.findall(r'<p[ >].*?</p>', raw.decode('utf8'), re.S)
            matches = [p for p in paras if 'either became PCR-positive or had symptoms compatible with Covid-19' in p and 'risk ratio' in p]
            if len(matches) != 1:
                raise ValueError('HCQ adjusted result prose unbound')
            span = matches[0]
            adjustment = [f for f in re.findall(r'<fn\b.*?</fn>', raw.decode('utf8'), re.S)
                          if 'Risk ratios were adjusted' in f and 'to account for clustering' in f]
            if len(adjustment) != 1:
                raise ValueError('HCQ cluster adjustment evidence unbound')
            base['design_adjustment'] = dict(kind='PUBLISHED_ADJUSTED_SUBSTITUTED',
                source=ref, span=adjustment[0], document_sha256=hashlib.sha256(raw).hexdigest())
            prose_values = re.search(r'risk ratio, (\d+\.\d+) \[95% CI, (\d+\.\d+) to (\d+\.\d+)\]', span)
            if not prose_values or tuple(map(float, prose_values.groups())) != tuple(base[k] for k in ('effect','ci_low','ci_high')):
                raise ValueError('HCQ adjusted effect differs between primary table and prose')
        base.update(source=span, source_span=span)
        result[rec['id']] = base
    return result

def bind_combined_counts(spec, row):
    """Recompute an explicitly declared derived tuple from primary table cells."""
    from . import target_endpoint as te
    root = Path(__file__).resolve().parents[1]
    def refuse(reason):
        out = te._unbound_classification({'binding': te.BINDING_NONE,
            'endpoint_result_span': None, 'endpoint_definition_span': None,
            'components': set(), 'binding_reason': reason})
        return dict(out, hand_binding_state='ABSTAIN')
    if spec.get('name') != 'Developing COVID-19' or spec.get('estimand') != 'RR':
        return refuse('HCQ combined-count outcome declaration mismatch')
    cfg = json.loads((root/'topics'/f'{SLUG}.json').read_text(encoding='utf8'))
    if cfg.get('typed_routes') != KEY:
        return refuse('HCQ combined-count route is not declared by topic')
    records = json.loads((root/'cache'/SLUG/'records.json').read_text(encoding='utf8'))['records']
    candidates = table_routes(cfg, root, records)
    pid = str(row.get('id', '')).removeprefix('PMID ')
    expected = candidates.get(pid)
    if not expected or expected.get('absent') or expected.get('typed_route') != row.get('typed_route'):
        return refuse('HCQ combined-count report identity mismatch')
    numeric = ('ai','n1i','ci','n2i') if 'ai' in expected else ('scale','effect','ci_low','ci_high')
    for field in numeric + ('document_ref','document_sha256','source_span','design_adjustment'):
        if row.get(field) != expected.get(field):
            return refuse('HCQ combined-count primary witness mismatch: '+field)
    endpoint = 'PCR-confirmed, symptomatic Covid-19' if row.get('typed_route') == 'hcq_effective_sample_size' else 'PCR positive or probable COVID-19'
    out = te._classify(spec, endpoint)
    if out['target_endpoint_class'] != te.EXACT_TARGET:
        return refuse('HCQ primary outcome vocabulary does not bind')
    out.update(hand_binding_state='BOUND', endpoint_binding='primary_table_arithmetic' if 'ai' in expected else 'primary_table_and_prose_agree',
        endpoint_result_span=expected['source_span'],
        endpoint_definition_span=endpoint,
        endpoint_binding_reason=expected['verification'],
        held_document=dict(ref=expected['document_ref'],sha256=expected['document_sha256'],representation='xml'),
        spans=[dict(role='result',text=expected['source_span'])])
    return out


def effective_counts(config, root, raw, doc, base):
    """Declared effective sample size; every event and denominator read from XML."""
    declaration = config['design_effect_conversion']
    if declaration != dict(method='effective_sample_size', icc=1.0, rounding='nearest_integer'):
        raise ValueError('HCQ design-effect declaration unsupported')
    table = doc.find('.//table-wrap[@id="t2"]')
    rows = [[''.join(c.itertext()).strip() for c in tr] for tr in table.iter('tr')]
    if not any(r[0].startswith('Primary outcome: PCR-confirmed, symptomatic Covid-19') for r in rows):
        raise ValueError('HCQ primary endpoint unbound')
    headers = [re.sub(r'[^a-z]', '', c.lower()) for c in rows[0]]
    if headers[1:3] != ['hydroxychloroquinegroup', 'usualcaregroup']:
        raise ValueError('HCQ arm headers do not bind intervention/comparator orientation')
    target = [r for r in rows if r[0].startswith('All patients')]
    if len(target) != 1:
        raise ValueError('HCQ primary-analysis population ambiguous')
    counts = []
    for cell in target[0][1:3]:
        match = re.fullmatch(r'(\d+)/(\d+) \((\d+\.\d+)\)', cell)
        if not match:
            raise ValueError('HCQ raw counts unbound')
        event, total, pct = map(float, match.groups())
        if not 0 < event < total or abs(event/total*100-pct) > .11:
            raise ValueError('HCQ raw count percentage mismatch')
        counts.extend([int(event), int(total)])
    text = raw.decode('utf8')
    population = re.search(r'The analysis included (\d+) healthy contacts of (\d+) index case patients', text)
    if not population:
        raise ValueError('HCQ cluster denominator unbound')
    contacts, clusters = map(int, population.groups())
    if counts[1]+counts[3] != contacts or not 0 < clusters < contacts:
        raise ValueError('HCQ cluster population mismatch')
    meta_ref = 'cache/benchmarks/v1/PMC7787432.xml'
    meta_raw = (Path(root)/meta_ref).read_bytes()
    method = [p for p in re.findall(r'<p[ >].*?</p>', meta_raw.decode('utf8'), re.S)
              if 'For cluster trials, we found the design effect' in p]
    if len(method) != 1:
        raise ValueError('HCQ comparator method unbound')
    de = 1+(contacts/clusters-1)*declaration['icc']
    keys = ('ai','n1i','ci','n2i')
    unrounded = dict(zip(keys, [v/de for v in counts]))
    base.update({k:round(v) for k,v in unrounded.items()})
    span = next(b for b in re.findall(r'<table-wrap\b.*?</table-wrap>', text, re.S) if 'id="t2"' in b)
    explanation = (f"Declared effective sample size: DE = 1 + ({contacts}/{clusters} - 1) * ICC {declaration['icc']} = {de}; "
        f"raw counts {dict(zip(keys, counts))}; unrounded {unrounded}; round events and denominators to nearest integer. "
        'ICC is the benchmark assumption, not an estimated trial ICC. Cochrane Handbook 23.1.4.')
    base.update(kind='extracted_counts', typed_route='hcq_effective_sample_size',
        verification=explanation, source=span, source_span=span,
        design_adjustment=dict(kind='ICC_DESIGN_EFFECT', source=base['document_ref'],
            document_sha256=base['document_sha256'], span=population.group(),
            raw_counts=dict(zip(keys, counts)), unrounded_counts=unrounded,
            design_effect=de, icc=declaration['icc'], rounding=declaration['rounding'],
            method_source=meta_ref, method_sha256=hashlib.sha256(meta_raw).hexdigest(),
            method_span=method[0], explanation=explanation,
            handbook='https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-23#section-23-1-4'))
    return base
