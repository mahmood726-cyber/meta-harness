"""Offline B-prime GLP1 sources and declared delivery strands.

Constants select endpoints and documents; effects are read from held sources.
"""
from pathlib import Path
import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET

from harness import claimgraph, extract


ROOT = Path(__file__).resolve().parents[1]
SLUG = 'glp1-ra-mace-t2d'
OUTCOME = '3-point major adverse cardiovascular events'
RAW = 'outputs/search_v2/lanes/R3/lane_r3/raw/'
PUBLICATIONS = {'38785209': '058-pubmed-glp1-ra-mace-t2d-flow-efetch.xml',
                '34873344': '139-pubmed-freedom-cvo-primary-34873344-efetch.xml'}


def read(path):
    return (ROOT / path).read_bytes().decode('utf-8')


def publication(pmid):
    path = RAW + PUBLICATIONS[pmid]
    article = next(a for a in ET.fromstring(read(path)).findall('PubmedArticle')
                   if a.findtext('MedlineCitation/PMID') == pmid)
    abstract = ' '.join(''.join(a.itertext()) for a in article.findall('.//AbstractText'))
    ncts = re.findall(r'NCT\d{8}', abstract)
    return {'id': pmid, 'id_type': 'pmid',
            'acronym': 'FLOW' if pmid == '38785209' else 'FREEDOM-CVO',
            'title': ''.join(article.find('.//ArticleTitle').itertext()),
            'abstract': abstract,
            'pubtypes': [p.text for p in article.findall('.//PublicationType')],
            'year': article.findtext('.//JournalIssue/PubDate/Year'),
            'journal': article.findtext('.//ISOAbbreviation'),
            'nct': ncts[-1] if ncts else None,
            'entered_via': 'held R3 PubMed query response', 'held_document': path}


def augment(records):
    records = copy.deepcopy(records)
    have = {r['id'] for r in records['records']}
    records['records'] += [publication(p) for p in PUBLICATIONS if p not in have]
    return records


def evidence(path, span, retrieved, document=None):
    text = read(path)
    offset = text.find(span)
    if offset < 0:
        raise ValueError(f'UNLOCATED span: {path}')
    document = document or path
    return {'document_path': document, 'document_ref': document,
            'document_sha256': hashlib.sha256((ROOT / document).read_bytes()).hexdigest(),
            'extracted_text': path,
            'extracted_text_sha256': hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
            'retrieved_utc': retrieved, 'span': span, 'span_offset': offset}


def entries():
    config = json.loads(read('topics/' + SLUG + '.json'))
    held = json.loads(read('cache/' + SLUG + '/records.json'))
    records = {r['id']: r for r in held['records']}
    result = {}
    for pmid in config['primary_outcome']['trial_annotations']:
        abstract = records[pmid]['abstract']
        scale, effect, low, high = extract.extract_effect(abstract.replace('·', '.'))
        # JSON escaping is part of the held file; span remains byte-located.
        span = json.dumps(abstract, ensure_ascii=False)[1:-1]
        result[pmid] = dict(effect=effect, ci_low=low, ci_high=high, scale=scale,
            source=span, source_level=1,
            **evidence('cache/' + SLUG + '/records.json', span,
                       held['fetched_utc'][:10] + 'T00:00:00Z'))
    sources = json.loads(read('outputs/handover/glp1_regulatory/regulatory_sources_glp1.json'))
    for source in sources['sources']:
        decision = source['decisions'][0]
        if decision['decision'] != 'EXTRACTED':
            continue
        pmid = decision['trial_key'].split()[-1]
        text_path = source['held']['extracted_text']
        text = read(text_path)
        if pmid == '26630143':
            span = claimgraph.locate_span(text, decision['span'])
        else:
            start = text.index('Table 19. Time to First Occurrence', text.index('### PAGE 58'))
            end = text.index('Based on a Cox proportional hazards regression model.', start)
            span = text[start:end + len('Based on a Cox proportional hazards regression model.')]
        eff = decision['effect']
        ev = evidence(text_path, span, source['fetched_utc'], source['held']['held_in_tree'])
        if ev['document_sha256'] != source['document_sha256']:
            raise ValueError('Regulatory source digest changed')
        result[pmid] = dict(effect=eff['estimate'], ci_low=eff['ci_low'], ci_high=eff['ci_high'],
                           scale=eff['scale'], source=span, source_level=2, **ev)
    flow = publication('38785209')
    text = read(flow['held_document'])
    start = text.index('the risk of major cardiovascular events 18% lower')
    end = text.index('), and the risk of death', start) + 1
    span = text[start:end]
    scale, effect, low, high = extract.extract_effect(span)
    adjudication = json.loads(read('outputs/handover/glp1_reviewerB/ADJUDICATIONS.json'))['decisions'][1]
    local_read = json.loads(read('cache/' + SLUG + '/source_reads.json'))['FLOW']
    if hashlib.sha256((ROOT / flow['held_document']).read_bytes()).hexdigest() != local_read['document_sha256']:
        raise ValueError('FLOW locally read source changed')
    result['38785209'] = dict(effect=effect, ci_low=low, ci_high=high, scale=scale,
        source=span, source_level=1, **evidence(flow['held_document'], span, local_read['retrieved_utc']),
        retrieval_mode=local_read['retrieval_mode'],
        endpoint_identity_source='AACT design_outcomes NCT03819153 (level 3)',
        endpoint_identity=adjudication['aact_span'], censoring='UNKNOWN',
        analysis_set='UNKNOWN')
    for pmid, row in result.items():
        if row['retrieved_utc'].endswith('T00:00:00Z'):
            row['retrieved_precision'] = 'day; UTC start-of-day representation, not a measured fetch time'
        row.update(outcome=OUTCOME, override=True,
                   verification='digest and verbatim span checked against committed bytes',
                   target_result_status='REPORTED_3POINT')
        row.setdefault('analysis_set', 'ITT' if row['source_level'] == 2 else 'UNKNOWN')
        row.setdefault('censoring', 'on-study' if row['source_level'] == 2 else 'UNKNOWN')
        row['timepoint'] = 'end of randomised follow-up'
        fact = claimgraph.verify_fact(row)
        if not fact['verified']:
            raise ValueError(f'{pmid}: {fact}')
    return result


def sensitivity():
    path = 'outputs/handover/glp1_regulatory/fda_media_172242_ITCA650.pdf.txt'
    text = read(path)
    start = text.index('3-Point MACE* 73/2070')
    span = text[start:text.index('\n', start)]
    values = re.search(r'(1\.\d+) \((0\.\d+), (1\.\d+)\)', span)
    effect, low, high = map(float, values.groups())
    sources = json.loads(read('outputs/handover/glp1_regulatory/regulatory_sources_glp1.json'))
    retrieved = next(s['fetched_utc'] for s in sources['sources']
                     if s['held']['extracted_text'] == path)
    row = dict(id='PMID 34873344', trial='FREEDOM-CVO', scale='HR', effect=effect,
               ci_low=low, ci_high=high, source=span, source_level=2,
               analysis_set='ITT', censoring='on-treatment', timepoint='end of treatment',
               pooled=False, adjudication='ADJ-GLP1-001',
               **evidence(path, span, retrieved, document='outputs/handover/glp1_regulatory/held/fda_media_172242_ITCA650.pdf'))
    assert claimgraph.verify_fact(row)['verified']
    return row

