"""Frozen G1 benchmark v1; conservative deterministic screening.

Hardcode disclosure:
  Static: preregistered query/budgets, registry patterns, area/text-rule maps.
  Dynamic: API hits, article XML, registry dates, on-disk topic terms.
  Research results: never hardcoded. Ambiguous evidence fails closed.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import random
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / 'registry/benchmarks/PREREGISTRATION_G1_BENCH_v1.md'
PREREG_COMMIT = '4adf8793ab88506bfdc23c0f45bfade7ce4165c6'
QUERY = '(TITLE:"meta-analysis" OR TITLE:"meta analysis" OR TITLE:"metaanalysis") AND (ABSTRACT:"randomized" OR ABSTRACT:"randomised") AND OPEN_ACCESS:y AND (LICENSE:"cc by" OR LICENSE:"cc0") AND (FIRST_PDATE:[2020-01-01 TO 2026-09-30]) AND SRC:MED'
QUERY_SHA256 = hashlib.sha256(QUERY.encode('utf-8')).hexdigest()
SEED = int(QUERY_SHA256[:8], 16)
EPMC = 'https://www.ebi.ac.uk/europepmc/webservices/rest/'
SCOPE = 'Open-access meta-analyses whose included trials are all recent (started 2010 or later) and prospectively registered.'
REGISTRIES = {
    'NCT': r'\bNCT\d{8}\b',
    'EudraCT': r'\b(?:EudraCT\s*[:#-]?\s*)?\d{4}-\d{6}-\d{2}\b',
    'ISRCTN': r'\bISRCTN\d{8}\b', 'ACTRN': r'\bACTRN\d{14}\b',
    'ChiCTR': r'\bChiCTR[-A-Z0-9]+\b', 'CTRI': r'\bCTRI/\d{4}/\d{2,3}/\d{6}\b',
    'UMIN': r'\bUMIN\d{9}\b', 'jRCT': r'\bjRCT\w+\b',
    'DRKS': r'\bDRKS\d{8}\b', 'IRCT': r'\bIRCT\w+\b', 'NTR': r'\bNTR\d+\b',
    'PACTR': r'\bPACTR\d+\b', 'KCT': r'\bKCT\d{7}\b',
    'CTIS': r'\b\d{4}-\d{6}-\d{2}-\d{2}\b',
}
# In the frozen C9 order.
AREA_KEYWORDS = {
    'cardiovascular': r'cardiovascular|cardiac|heart|coronary|myocardial|stroke|hypertension|atrial|vascular|thrombo|blood pressure',
    'endocrine/metabolic': r'diabet|endocrin|metabol|obes|thyroid|glyc[ae]mi|insulin|weight loss',
    'infectious disease': r'infect|covid|sars.cov|hiv|tuberculo|malaria|sepsis|viral|bacter|antibiotic',
    'oncology': r'cancer|neoplasm|oncolog|tumou?r|carcinoma|lymphoma|myeloma|leuk[ae]mia|chemotherapy',
    'psychiatry': r'psychiatr|depress|anxiety|schizophren|bipolar|psychosis|mental disorder',
    'neurology': r'neurolog|alzheimer|parkinson|epilep|seizure|migraine|dementia|multiple sclerosis|brain',
    'respiratory': r'respiratory|pulmonary|asthma|copd|lung|bronch|sleep apn',
    'gastroenterology/hepatology': r'gastro|hepat|liver|bowel|crohn|colitis|digest|pancrea|cirrho|irritable|gastric',
    'renal/urology': r'renal|kidney|urolog|urinary|dialysis|prostat|bladder',
    'obstetrics/gynaecology': r'obstetric|gyn[ae]+colog|pregnan|maternal|uterine|ovarian|fertility|cesarean|caesarean|postpartum',
    'musculoskeletal/rheumatology': r'musculoskeletal|rheumat|arthritis|osteopor|osteoarth|fracture|back pain|joint|bone',
    'critical care/anaesthesia/surgery': r'critical care|intensive care|anaesthe|anesthe|surg|operative|ventilat|analgesi',
    'other': r'.*',
}


class FetchError(RuntimeError):
    pass


class MissingResource(FetchError):
    pass


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def parse_xml(raw, expected=None):
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise FetchError(f'Invalid XML: {exc}') from exc
    for node in root.iter():
        node.tag = node.tag.rsplit('}', 1)[-1]
    if root.tag.lower() in ('html', 'error') or (expected and root.tag != expected):
        raise FetchError(f'Unexpected XML root: {root.tag}')
    return root


class Client:
    def __init__(self):
        self.last_request = 0.0

    def get(self, url, kind):
        for attempt in range(5):
            time.sleep(max(0.0, 0.35 - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            try:
                request = Request(url, headers={'User-Agent': 'G1BenchmarkScreen/1.0', 'Accept': 'application/json' if kind == 'json' else 'application/xml'})
                with urlopen(request, timeout=45) as response:
                    raw = response.read()
                    content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' in content_type or re.search(br'<(?:!doctype\s+html|html)\b', raw[:1024], re.I):
                    raise FetchError(f'HTML response at {url}')
                if kind == 'json':
                    try:
                        value = json.loads(raw)
                    except (ValueError, UnicodeError) as exc:
                        raise FetchError(f'Invalid JSON at {url}: {exc}') from exc
                    if not isinstance(value, dict):
                        raise FetchError(f'Expected JSON object at {url}')
                    return value
                parse_xml(raw)
                return raw
            except HTTPError as exc:
                if exc.code in (404, 410):
                    raise MissingResource(f'HTTP {exc.code}: {url}') from exc
                if exc.code != 429 and not 500 <= exc.code < 600:
                    raise FetchError(f'HTTP {exc.code}: {url}') from exc
                if attempt == 4:
                    raise FetchError(f'HTTP {exc.code} after 5 attempts: {url}') from exc
                retry = exc.headers.get('Retry-After', '')
                time.sleep(max(2 ** attempt, float(retry) if retry.isdigit() else 0))
            except (URLError, TimeoutError, OSError) as exc:
                if attempt == 4:
                    raise FetchError(f'Network failure after 5 attempts at {url}: {exc}') from exc
                time.sleep(2 ** attempt)
        raise FetchError(f'Exhausted retries: {url}')


def order_hits(hits):
    ordered = sorted(hits, key=lambda h: int(h['id']))
    random.Random(SEED).shuffle(ordered)
    return ordered


def search_hits(client):
    cursor, hits, expected, seen = '*', [], None, set()
    while True:
        url = EPMC + 'search?' + urlencode({'query': QUERY, 'resultType': 'core', 'format': 'json', 'pageSize': 1000, 'cursorMark': cursor})
        page = client.get(url, 'json')
        if 'hitCount' not in page or 'resultList' not in page:
            raise FetchError('Search response missing hitCount/resultList')
        count = int(page['hitCount'])
        if expected is not None and count != expected:
            raise FetchError('Search hit count changed during cursor paging')
        expected = count
        results = page['resultList'].get('result', [])
        for hit in results:
            key = hit.get('id')
            if not key or not str(key).isdigit() or key in seen:
                raise FetchError(f'Invalid/duplicate search id: {key}')
            seen.add(key)
            hits.append(hit)
        print(f'SEARCH {len(hits)}/{expected}', flush=True)
        if len(hits) == expected:
            return hits
        next_cursor = page.get('nextCursorMark')
        if not results or not next_cursor or next_cursor == cursor or len(hits) > expected:
            raise FetchError('Incomplete or inconsistent search cursor paging')
        cursor = next_cursor


def fetch_xml(pmcid, client):
    if not re.fullmatch(r'PMC\d+', pmcid or ''):
        raise MissingResource('No valid PMCID')
    path = ROOT / 'cache/benchmarks/v1' / (pmcid + '.xml')
    if path.exists():
        raw = path.read_bytes()
        parse_xml(raw, 'article')
        return raw
    raw = client.get(EPMC + pmcid + '/fullTextXML', 'xml')
    parse_xml(raw, 'article')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


def text(node):
    return ' '.join(' '.join(node.itertext()).split()) if node is not None else ''


def month(value):
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r'(\d{4})-(\d{2})(?:-(\d{2}))?', value.strip())
    if match:
        try:
            date = datetime(int(match[1]), int(match[2]), int(match[3] or '1'))
            return date.year, date.month
        except ValueError:
            return None
    for fmt in ('%d/%m/%Y', '%Y/%m/%d', '%B %Y', '%b %Y', '%B %d, %Y'):
        try:
            date = datetime.strptime(value.strip(), fmt)
            return date.year, date.month
        except ValueError:
            pass
    return None


def registry_name(rid):
    return next((name for name, pattern in REGISTRIES.items() if re.fullmatch(pattern, rid, re.I)), 'unknown')


def fetch_registry(rid, client):
    registry = registry_name(rid)
    evidence = {'id': rid, 'registry': registry, 'start': None, 'registered': None}
    if registry == 'NCT':
        url = 'https://clinicaltrials.gov/api/v2/studies/' + rid + '?fields=protocolSection.statusModule'
        evidence['source'] = url
        try:
            data = client.get(url, 'json')
        except MissingResource as exc:
            return {**evidence, 'unreadable': str(exc)}
        status = data.get('protocolSection', {}).get('statusModule', {})
        evidence.update(start=status.get('startDateStruct', {}).get('date'), registered=status.get('studyFirstSubmitDate'), source_record=status)
    elif registry == 'ISRCTN':
        url = 'https://www.isrctn.com/api/query/format/default?' + urlencode({'q': rid})
        evidence['source'] = url
        try:
            raw = client.get(url, 'xml')
        except MissingResource as exc:
            return {**evidence, 'unreadable': str(exc)}
        root = parse_xml(raw)
        if {s.upper() for s in re.findall(REGISTRIES['ISRCTN'], text(root), re.I)} != {rid}:
            return {**evidence, 'unreadable': 'Registry response did not uniquely identify requested ISRCTN'}
        starts = {text(n) for n in root.iter('overallStartDate') if text(n)}
        assigned = {text(n) for n in root.iter('dateAssigned') if text(n)}
        evidence.update(start=next(iter(starts)) if len(starts) == 1 else None, registered=next(iter(assigned)) if len(assigned) == 1 else None, response_sha256=hashlib.sha256(raw).hexdigest())
    else:
        evidence['unreadable'] = 'No reliable machine-readable date API configured for ' + registry
    return evidence


def accepted_license(value):
    return bool(re.fullmatch(r'(?:cc[ -]by(?:\s+\d+(?:\.\d+)?)?|cc0(?:\s+\d+(?:\.\d+)?)?)', (value or '').strip(), re.I))


DESIGN = re.compile(r'\brandomi[sz]ed(?:[ -]controlled)?\s+(?:clinical\s+)?trials?\b', re.I)
WORDS = {word: i for i, word in enumerate('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty twenty-one twenty-two twenty-three twenty-four twenty-five'.split())}
NUMBER = r'(?:\d[\d,]*|' + '|'.join(sorted(WORDS, key=len, reverse=True)) + ')'
COUNT = re.compile(r'\b(' + NUMBER + r')\s+(?:(?:eligible|included|randomi[sz]ed|controlled|clinical|parallel[ -]group)\s+)*(?:RCTs?|trials?|studies)\b', re.I)


def extract_k(abstract, root):
    sources = [('abstract', abstract)]
    sources += [('results', text(sec)) for sec in root.findall('.//body//sec') if re.search(r'\bresults?\b', text(sec.find('title')), re.I)]
    matches = []
    for source, passage in sources:
        for match in COUNT.finditer(passage):
            span = passage[max(0, match.start()-100):match.end()+120]
            sentence = re.split(r'[.!?;]', passage[:match.start()])[-1] + re.split(r'[.!?;]', passage[match.start():])[0]
            if re.search(r'\b(?:excluded|ongoing|non.randomi[sz]ed|observational)\b', sentence, re.I):
                continue
            if not re.search(r'\b(?:includ\w*|eligible|met\s+(?:the\s+)?inclusion|analy[sz]ed|pooled)\b', sentence, re.I):
                continue
            number = match[1].lower()
            value = int(number.replace(',', '')) if number[0].isdigit() else WORDS[number]
            matches.append({'k': value, 'source': source, 'span': span})
    values = {m['k'] for m in matches}
    return (next(iter(values)) if len(values) == 1 else None), matches


def included_ids(root):
    def clean(node):
        if node.tag in ('ref-list', 'ref', 'mixed-citation', 'element-citation'):
            return ''
        return ' '.join([node.text or ''] + [clean(child) + ' ' + (child.tail or '') for child in node])
    nodes = root.findall('./body') + root.findall('./back//supplementary-material')
    passage = ' '.join(clean(node) for node in nodes)
    found = {}
    ctis_spans = [m.span() for m in re.finditer(REGISTRIES['CTIS'], passage, re.I)]
    for registry, pattern in REGISTRIES.items():
        for match in re.finditer(pattern, passage, re.I):
            if registry == 'EudraCT' and any(a <= match.start() < b for a, b in ctis_spans):
                continue
            span = passage[max(0, match.start()-180):match.end()+180]
            local_sentence = re.split(r'[.;\n]', passage[:match.start()])[-1][-180:]
            if re.search(r'\b(?:excluded|ongoing|other reviews?|previous reviews?)\b', local_sentence, re.I):
                continue
            rid = match[0].upper()
            if registry == 'EudraCT':
                rid = re.search(r'\d{4}-\d{6}-\d{2}', rid)[0]
            found.setdefault(rid, {'id': rid, 'registry': registry, 'span': span})
    return sorted(found), [found[rid] for rid in sorted(found)]


def outcome_terms(abstract, root):
    passages = [abstract]
    passages += [text(sec) for sec in root.findall('.//sec') if re.search(r'outcomes?|endpoints?', text(sec.find('title')), re.I)]
    terms, spans = set(), []
    for passage in passages:
        for match in re.finditer(r'\b(?:primary\s+|secondary\s+|pooled\s+)?(?:outcomes?|end[ -]?points?)\s+(?:of\s+interest\s+)?(?:were|was|included?|comprised|:|assessed\s+were)\s+([^.;]{3,250})', passage, re.I):
            spans.append(match[0])
            for item in re.split(r',|\band\b|\bor\b', match[1], flags=re.I):
                item = re.sub(r'^(?:the\s+|a\s+|an\s+)', '', item.strip(), flags=re.I).strip(' :()')
                if len(item) >= 3:
                    terms.add(item.lower())
    return sorted(terms), spans


def per_trial_rows(root, ids, k, abstract):
    outcomes, spans = outcome_terms(abstract, root)
    references = {r.get('id'): r for r in root.findall('.//back//ref')}
    surnames = {}
    for node in root.findall('.//body//tr') + root.findall('.//body//p'):
        linked_ids = [rid for rid in ids if rid.lower() in text(node).lower()]
        refs = [references.get(rid) for x in node.findall('.//xref') if x.get('ref-type') == 'bibr' for rid in x.get('rid', '').split()]
        refs = [r for r in refs if r is not None]
        if len(linked_ids) == 1 and len(refs) == 1:
            name = text(refs[0].find('.//surname'))
            if name:
                surnames[linked_ids[0]] = name
    for table in root.findall('.//table-wrap'):
        content = text(table)
        outcome = next((o for o in outcomes if o in content.lower()), None)
        if not outcome or not re.search(r'pool|meta.analysis|effect|risk ratio|odds ratio|mean difference|hazard ratio|events|mortality', content, re.I):
            continue
        matched, rows = set(), []
        for row in table.findall('.//tr'):
            row_text = text(row)
            row_ids = {rid for rid in ids if rid.lower() in row_text.lower() or (rid in surnames and re.search(r'\b' + re.escape(surnames[rid]) + r'\b', row_text, re.I))}
            if len(row_ids) == 1:
                matched.update(row_ids)
                rows.append(row_text)
        if len(matched) / k >= 0.8:
            return {'kind': 'table', 'element_id': table.get('id'), 'caption': text(table.find('caption')), 'outcome': outcome, 'matched_ids': sorted(matched), 'rows': rows, 'outcome_spans': spans}
    for fig in root.findall('.//fig'):
        caption = text(fig.find('caption'))
        outcome = next((o for o in outcomes if o in caption.lower()), None)
        caption_span = None
        if not outcome:
            label = re.search(r'\bforest\s+plots?\s+(?:of|for|showing)\s+(?:(?:HRs?|ORs?|RRs?|hazard ratios?|odds ratios?|risk ratios?|mean differences?)\s+(?:for|of)\s+)?(.+)', caption, re.I)
            if label:
                named = re.split(r'\s+(?:in|between|among|comparing)\s+|[.;()]', label[1], maxsplit=1, flags=re.I)[0].strip().lower()
                named = re.sub(r'^(?:the|a|an)\s+', '', named)
                generic = re.search(r'\b(?:studies|trials|results|meta.analysis|primary outcome|secondary outcome)\b', named)
                if len(named) >= 3 and not generic and term_matches(named, abstract):
                    outcome, caption_span = named, label[0]
        if re.search(r'\bforest\b', caption, re.I) and outcome:
            return {'kind': 'figure', 'element_id': fig.get('id'), 'caption': caption, 'outcome': outcome, 'outcome_spans': spans + ([caption_span] if caption_span else []), 'outcome_source': 'caption corroborated by abstract' if caption_span else 'outcome statement'}
    return None


def strings(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [s for item in value for s in strings(item)]
    return []


def topic_outcomes(topic):
    terms = []
    primary = topic.get('primary_outcome', {})
    if isinstance(primary, dict):
        terms += strings(primary.get('name', '')) + strings(primary.get('keywords', []))
    else:
        terms += strings(primary)
    def walk(obj, in_outcome=False):
        if isinstance(obj, dict):
            for key, value in obj.items():
                context = in_outcome or 'outcome' in key.lower()
                if context and ('keyword' in key.lower() or key.lower().endswith('_terms')):
                    terms.extend(strings(value))
                walk(value, context)
        elif isinstance(obj, list):
            for item in obj:
                walk(item, in_outcome)
    walk(topic)
    return sorted(set(t.strip() for t in terms if t.strip()))


def term_matches(term, passage):
    return bool(re.search(r'(?<!\w)' + re.escape(term.lower()) + r'(?!\w)', passage.lower()))


def overlap(topics, passage):
    for topic in topics:
        interventions = [term for key in ('intervention_terms', 'intervention_agents', 'intervention_class_terms') for term in strings(topic.get(key, [])) if term.strip() and term_matches(term, passage)]
        outcomes = [term for term in topic_outcomes(topic) if term_matches(term, passage)]
        if interventions and outcomes:
            return {'topic': topic.get('slug', topic.get('_file')), 'intervention_terms': sorted(set(interventions)), 'outcome_terms': outcomes}
    return None


def therapeutic_area(hit):
    headings = hit.get('meshHeadingList', {}).get('meshHeading', [])
    major = [h.get('descriptorName', '') for h in headings if h.get('majorTopic_YN') == 'Y']
    passage = ' '.join(major) if major else hit.get('title', '')
    for area, pattern in AREA_KEYWORDS.items():
        match = re.search(pattern, passage, re.I)
        if match:
            return area, {'source': 'MeSH major headings' if major else 'title', 'text': passage, 'matched': match[0]}


def screen_candidate(hit, client, topics, areas):
    result = {key: hit.get(key) for key in ('id', 'pmid', 'pmcid', 'title', 'license')}
    result.update(verdict='EXCLUDED', first_failure=None, evidence={}, checks={})
    criterion = 'C1'
    def fail(criterion, evidence, verdict='EXCLUDED'):
        result.update(verdict=verdict, first_failure=criterion, evidence=evidence)
        return result
    try:
        if not accepted_license(hit.get('license')):
            return fail('C1', {'license': hit.get('license'), 'reason': 'Only exact CC BY or CC0 accepted'})
        try:
            raw = fetch_xml(hit.get('pmcid'), client)
        except MissingResource as exc:
            return fail('C1', {'reason': str(exc)})
        root = parse_xml(raw, 'article')
        result['xml_sha256'] = hashlib.sha256(raw).hexdigest()
        result['xml_cache'] = 'cache/benchmarks/v1/' + hit['pmcid'] + '.xml'
        result['checks']['C1'] = {'license': hit['license'], 'xml_sha256': result['xml_sha256']}
        abstract = re.sub(r'<[^>]+>', ' ', html.unescape(hit.get('abstractText') or '')) or ' '.join(text(a) for a in root.findall('.//article-meta/abstract'))
        body = text(root.find('body'))
        criterion = 'C2'
        types = hit.get('pubTypeList', {}).get('pubType', hit.get('pubType', []))
        types = types if isinstance(types, list) else [types]
        design = DESIGN.search(abstract)
        if any(re.search(r'retract', t, re.I) for t in types) or re.search(r'^retraction\b', hit.get('title', ''), re.I):
            return fail('C2', {'reason': 'Retracted publication or retraction notice', 'pubType': types})
        if not design:
            return fail('C2', {'reason': 'Abstract does not state randomized/randomised (controlled) trials', 'abstract': abstract})
        own_design = hit.get('title', '') + ' ' + abstract
        excluded = re.search(r'network\s+meta.analysis|individual[ -](?:participant|patient)[ -]data|diagnostic[ -]accuracy|umbrella\s+review|(?:meta.analysis|review)\s+of\s+observational', own_design, re.I)
        if excluded and not (re.search(r'network|individual', excluded[0], re.I) and re.search(r'\bpairwise\b|aggregate[ -]data', own_design, re.I)):
            return fail('C2', {'reason': 'Excluded design or ambiguous pairwise design', 'span': excluded[0]})
        self_description = re.search(r'\b(?:this|our|we\s+conducted\s+(?:a|an))\s+[^.]{0,60}(?:network meta.analysis|individual.participant.data meta.analysis|diagnostic.accuracy review|umbrella review|review of observational studies)', body, re.I)
        if self_description and not re.search(r'pairwise|aggregate[ -]data', own_design, re.I):
            return fail('C2', {'reason': 'Excluded/ambiguous body self-description', 'span': self_description[0]})
        result['checks']['C2'] = {'span': design[0], 'pubType': types}
        criterion = 'C3'
        k, counts = extract_k(abstract, root)
        if k is None or not 3 <= k <= 25:
            return fail('C3', {'reason': 'Included RCT count missing, ambiguous, or outside 3..25', 'counts': counts})
        result['k'] = k
        result['checks']['C3'] = counts
        criterion = 'C4'
        ids, id_evidence = included_ids(root)
        result['registry_ids'] = ids
        if len(ids) != k:
            return fail('C4', {'reason': 'Distinct included-trial registry id count must equal k', 'k': k, 'ids': ids, 'spans': id_evidence})
        result['checks']['C4'] = id_evidence
        criterion = 'C5'
        dates = []
        result['registry_dates'] = dates
        for rid in ids:
            record = fetch_registry(rid, client)
            dates.append(record)
            if month(record.get('start')) is not None and month(record['start']) < (2010, 1):
                return fail('C5', {'reason': 'Trial started before 2010-01', 'trials': [record]})
        result['checks']['C5'] = {'known_starts': [d.get('start') for d in dates]}
        criterion = 'C6'
        unreadable = [d for d in dates if month(d.get('start')) is None or month(d.get('registered')) is None]
        if unreadable:
            return fail('C6', {'reason': 'UNREADABLE registry dates', 'trials': unreadable})
        late = [d for d in dates if month(d['registered']) > month(d['start'])]
        if late:
            return fail('C6', {'reason': 'Registered after start month', 'trials': late})
        result['checks']['C6'] = dates
        criterion = 'C7'
        rows = per_trial_rows(root, ids, k, abstract)
        if rows is None:
            return fail('C7', {'reason': 'No qualifying per-trial outcome table or forest caption naming a pooled outcome', 'outcome_terms': outcome_terms(abstract, root)[0]})
        result['checks']['C7'] = rows
        criterion = 'C8'
        matched = overlap(topics, hit.get('title', '') + ' ' + abstract)
        if matched:
            return fail('C8', matched)
        result['checks']['C8'] = {'overlap': False}
        criterion = 'C9'
        area, evidence = therapeutic_area(hit)
        result['area'] = area
        result['checks']['C9'] = evidence
        if areas.get(area, 0) >= 3:
            return fail('C9', {**evidence, 'area': area, 'already_qualified': areas[area]}, 'EXCLUDED_AREA_CAP')
        result.update(verdict='QUALIFIES', evidence={'reason': 'Passed C1..C9'})
        return result
    except FetchError as exc:
        return fail(criterion, {'reason': str(exc), 'exception': type(exc).__name__}, 'SCREEN_ERROR')


def main():
    prereg_bytes = PREREG.read_bytes()
    if QUERY not in prereg_bytes.decode('utf-8'):
        raise RuntimeError('Script query does not match frozen preregistration')
    output = ROOT / 'registry/benchmarks'
    if (output / 'hits_v1.json').exists() or (output / 'candidates_v1.json').exists():
        raise RuntimeError('v1 run artifacts already exist; refusing to overwrite')
    paths = sorted((ROOT / 'topics').glob('*.json'))
    if not paths:
        raise RuntimeError('No topic records: C8 cannot run')
    topics, topic_sources = [], []
    for path in paths:
        raw = path.read_bytes()
        topic = json.loads(raw)
        if not isinstance(topic, dict):
            raise RuntimeError(f'Invalid topic object: {path.name}')
        topic['_file'] = path.name
        topics.append(topic)
        topic_sources.append({'file': 'topics/' + path.name, 'sha256': hashlib.sha256(raw).hexdigest()})
    run_utc, client = utc_now(), Client()
    hits = search_hits(client)
    raw_hits = [{**{key: hit.get(key) for key in ('id', 'pmid', 'pmcid', 'title', 'license', 'firstPublicationDate')}, 'pubType': hit.get('pubTypeList', {}).get('pubType', hit.get('pubType', [])), 'core_record': hit} for hit in hits]
    write_json(output / 'hits_v1.json', {'run_utc': run_utc, 'query': QUERY, 'query_sha256': QUERY_SHA256, 'n_hits': len(hits), 'hits': raw_hits})
    screen_hits(hits, client, topics, topic_sources, run_utc, prereg_bytes)


def screen_hits(hits, client, topics, topic_sources, run_utc, prereg_bytes):
    """Screen a fixed source snapshot; also supports audited implementation replay."""
    output = ROOT / 'registry/benchmarks'
    report = {'prereg_commit': PREREG_COMMIT, 'prereg_sha256': hashlib.sha256(prereg_bytes).hexdigest(), 'query': QUERY, 'query_sha256': QUERY_SHA256, 'seed': SEED, 'run_utc': run_utc, 'scope': SCOPE, 'topic_sources': topic_sources, 'n_hits': len(hits), 'n_screened': 0, 'n_qualifies': 0, 'n_screen_errors': 0, 'complete': False, 'screened': [], 'first_failure_counts': {}, 'screen_error_counts': {}}
    report['screening_script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report['screening_run_utc'] = utc_now()
    areas = Counter()
    for hit in order_hits(hits):
        result = screen_candidate(hit, client, topics, areas)
        report['screened'].append(result)
        report['n_screened'] += 1
        if result['verdict'] == 'QUALIFIES':
            report['n_qualifies'] += 1
            areas[result['area']] += 1
        elif result['verdict'] == 'SCREEN_ERROR':
            report['n_screen_errors'] += 1
        report['first_failure_counts'] = dict(Counter(r['first_failure'] for r in report['screened'] if r['first_failure'] and r['verdict'] != 'SCREEN_ERROR'))
        report['screen_error_counts'] = dict(Counter(r['first_failure'] for r in report['screened'] if r['verdict'] == 'SCREEN_ERROR'))
        write_json(output / 'candidates_v1.json', report)
        print(f"SCREEN {report['n_screened']} id={hit['id']} {result['verdict']} {result['first_failure'] or '-'} qualifies={report['n_qualifies']}", flush=True)
        if report['n_qualifies'] >= 20 or report['n_screened'] >= 800:
            break
    report['complete'] = True
    report['completed_utc'] = utc_now()
    report['stop_reason'] = '20 qualifiers' if report['n_qualifies'] == 20 else ('800 screened' if report['n_screened'] == 800 else 'hit list exhausted')
    write_json(output / 'candidates_v1.json', report)
    print(json.dumps({key: report[key] for key in ('n_hits', 'n_screened', 'n_qualifies', 'n_screen_errors', 'first_failure_counts', 'screen_error_counts', 'stop_reason')}, indent=2), flush=True)
    print('QUALIFYING CANDIDATES', flush=True)
    for candidate in report['screened']:
        if candidate['verdict'] == 'QUALIFIES':
            print(json.dumps({key: candidate[key] for key in ('pmid', 'title', 'area', 'k')}, ensure_ascii=False), flush=True)

    return report


if __name__ == '__main__':
    main()
