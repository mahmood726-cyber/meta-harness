"""Offline, deterministic acquisition hints. No clinical values or pool admission.

Only the canonical comparator_fulltext.txt supplies identity. Proposal and panel
hashes anchor it; proposals supply labels, not remembered bibliographic details.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('author', 'year', 'journal', 'title', 'doi', 'pmid', 'nct')
IDS = {
    'doi': re.compile(r'(?<![\w/])10\.\d{4,9}/[^\s<>\[\]"]+'),
    'pmid': re.compile(r'\b(?:PMID|PUBMED)\s*:?\s*(\d{6,9})\b', re.I),
    'nct': re.compile(r'\bNCT\d{8}\b'),
}
RESOLUTIONS = ('RESOLVED_BY_IDENTIFIER', 'RESOLVED_BY_CITATION_ONLY', 'UNRESOLVED')
HYPOTHESES = ('NOT_RETRIEVED_BY_SEARCH', 'OUTSIDE_OUR_PROTOCOL_SCOPE',
              'DIFFERENT_OUTCOME_OR_TIMEPOINT', 'UNKNOWN')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def slug_ok(slug):
    if not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]*', slug):
        raise ValueError('REFUSED_INVALID_SLUG')


def identifiers(field, span):
    return {((m[1] if field == 'pmid' else m[0]).rstrip('.,;'))
            for m in IDS[field].finditer(span)}


def source(slug, root):
    """Verify base gate AND raw canonical bytes before identity extraction."""
    from harness.proposal_gate import verify as proposal_verify
    slug_ok(slug)
    p = read(root / 'evidence/g1_proposals' / (slug + '.json'))
    gate = proposal_verify(p, root)
    if gate['accepted'] is None:
        raise ValueError('REFUSED_PROPOSAL:' + str(gate['reason']))
    canonical = root / 'cache' / slug / 'comparator_fulltext.txt'
    # A differently located document is not silently substituted for the brief's
    # required source. Its gate-verified hash is retained, with no identity fields.
    if not canonical.is_file() or Path(p['document_ref']).as_posix() != f'cache/{slug}/comparator_fulltext.txt':
        return p, None, 'REFUSED_CANONICAL_COMPARATOR_SOURCE_UNAVAILABLE'
    raw = canonical.read_bytes()
    if hashlib.sha256(raw).hexdigest() != p['document_sha256']:
        raise ValueError('REFUSED_SHA256_MISMATCH:' + slug)
    return p, raw.decode('utf-8'), None


def citation_candidates(label, text):
    """Cochrane labelled blocks or numbered bibliography entries, never body prose."""
    blocks = list(re.finditer(r'(?P<label>[\w’‐-]+\s+(?:19|20)\d{2}[a-z]?)\s+\{[^}]+\}', text))
    for i, m in enumerate(blocks):
        if m['label'] == label:
            end = blocks[i + 1].start() if i + 1 < len(blocks) else len(text)
            block = text[m.end():end].strip()
            # Bibliographic links delimit reports, including companion reports.
            reports = re.split(r'\[ Google Scholar \]', block)
            if 'unpublished data only' in m[0]:
                return [block]
            year = re.search(r'\b(?:19|20)\d{2}\b', label)
            chosen = [r.strip() for r in reports if year and re.search(year[0] + r'\s*;', r)]
            return chosen if len(chosen) == 1 else []
    headings = list(re.finditer(r'\b(?:REFERENCES|References)\s+1\.', text))
    if not headings:
        return []
    tail = text[headings[-1].end() - 2:]
    refs = list(re.finditer(r'(?<!\S)(\d{1,3})\.\s+(?=[A-ZÀ-Ž])', tail))
    citations = [(m[1], re.split(r'\b(?:Table \d|Associated Data|Supplementary Materials)\b', tail[m.end():refs[i+1].start() if i+1 < len(refs) else len(tail)])[0].strip())
                 for i, m in enumerate(refs)]
    refnum = re.search(r'\[\s*(\d+)\s*\]|\bet al\s+(\d+)\b', label)
    if refnum:
        number = next(g for g in refnum.groups() if g)
        return [c for n, c in citations if n == number]
    analyses = set(re.findall(r'\bet al\s+(\d{1,3})\s+analysis of\s+' + re.escape(label) + r'(?!\w)', text[:headings[-1].start()]))
    if analyses:
        return [c for n, c in citations if n in analyses] if len(analyses) == 1 else []
    # Explicit table label -> reference number. Merely mentioning an acronym in
    # a bibliography can select a commentary instead of the trial report.
    links = set(re.findall(r'(?<!\w)' + re.escape(label) + r'(?:\s+trial)?[,]?\s+(\d{1,3})(?!\d)', text[:headings[-1].start()]))
    return [c for n, c in citations if n in links] if len(links) == 1 else []


def parse_citation(citation):
    """Parse conservative author-list / title / journal / year citation grammar."""
    out = {k: None for k in FIELDS}
    spans = {}
    # Comma-separated author lists ending in initials or 'et al.'; initials may
    # themselves contain periods. Journal starts after the title's final period.
    m = re.match(r'(?P<authors>.+?(?:et al\s*(?:\.|;[^.]+\.)|[A-Z]{1,4}\.))\s+(?P<title>.+?)\.\s+(?P<journal>[A-Z][A-Za-z &’‐-]+?)[.]?\s+(?P<year>(?:19|20)\d{2})(?=\s*(?:[;(:]|doi:))', citation)
    if m:
        first = re.match(r'[^,]+', m['authors'])[0]
        title = re.sub(r'^on behalf of .+?\.\s+', '', m['title'])
        out.update(author=first, title=title, journal=m['journal'], year=m['year'])
        spans.update({k: out[k] for k in ('author', 'title', 'journal', 'year')})
    else:
        unpublished = re.match(r'(?P<authors>.+?[A-Z]{1,4}\.)\s+(?P<title>.+?)\.\s+Unpublished data\.', citation)
        if unpublished:
            out.update(author=unpublished['authors'].split(',')[0], title=unpublished['title'])
            spans.update({k: out[k] for k in ('author', 'title')})
    for key in IDS:
        hits = identifiers(key, citation)
        if len(hits) == 1:
            out[key] = next(iter(hits))
            match = next(m for m in IDS[key].finditer(citation)
                         if out[key] in m[0])
            spans[key] = match[0]
    return {**out, 'spans': spans}


def resolve(row, text):
    result = {**dict.fromkeys(FIELDS), 'spans': {}}
    label = row['label']
    if text is None:
        return result, [], 'UNRESOLVED', 'Canonical comparator text unavailable'
    if label not in text:
        return result, [], 'UNRESOLVED', 'REFUSED_LABEL_NOT_VERBATIM_IN_CANONICAL_TEXT'
    evidence = [label]
    candidates = citation_candidates(label, text)
    if len(candidates) == 1:
        citation = candidates[0]
        result = parse_citation(citation)
        evidence.append(citation)
    # Only already gate-accepted identifier fields, bound to their own held spans.
    for key, proposal_key in [('nct', 'registration'), ('pmid', 'pmid')]:
        value = row.get(proposal_key)
        span = row.get('field_spans', {}).get(proposal_key, row['span'])
        if value and span in text and str(value) in identifiers(key, span):
            if result[key] and result[key] != str(value):
                return {**dict.fromkeys(FIELDS), 'spans': {}}, evidence, 'UNRESOLVED', 'REFUSED_CONFLICTING_IDENTIFIERS'
            result[key], result['spans'][key] = str(value), span
            evidence.append(span)
    # Partial author/year table citations are useful acquisition hints but a lone
    # surname or acronym is not a resolved citation.
    if not result['author']:
        author = re.match(r'([A-ZÀ-Ž][\w’\'-]*(?:\s+[a-z]+)?)\s+(?=(?:19|20)\d{2}|et al|\[|\()', label)
        if author:
            result['author'] = author[1]
            result['spans']['author'] = author[1]
    if not result['year']:
        year = re.search(r'\b(?:19|20)\d{2}\b', label)
        if year:
            result['year'], result['spans']['year'] = year[0], year[0]
        elif result['author']:
            # A table can print its year immediately after an author/trial label.
            years = list(re.finditer(re.escape(label) + r'\s+((?:19|20)\d{2})\b', text))
            if len({m[1] for m in years}) == 1:
                result['year'] = years[0][1]
                result['spans']['year'] = years[0][0]
                evidence.append(years[0][0])
    resolution = ('RESOLVED_BY_IDENTIFIER' if any(result[k] for k in IDS) else
                  'RESOLVED_BY_CITATION_ONLY' if result['author'] and result['year'] else 'UNRESOLVED')
    reason = ('Unique printed identifier' if resolution == RESOLUTIONS[0] else
              'Printed author/year citation; bibliographic fields may be absent' if resolution == RESOLUTIONS[1] else
              'No unique usable reference or identifier in held canonical text')
    return result, list(dict.fromkeys(evidence)), resolution, reason


def build_queue(topic_row, root=ROOT):
    root = Path(root)
    slug = topic_row['slug']
    p, text, refusal = source(slug, root)
    queue = {k: p[k] for k in ('slug', 'comparator_pmid', 'document_sha256')}
    queue.update(document_ref=p['document_ref'], source_refusal=refusal, missing=[])
    from .identity_join import join, our_identities
    held_identities = our_identities(slug, root)
    for gap in topic_row['trials']:
        if gap['status'] != 'MISSING_FROM_OURS':
            continue
        rows = [r for r in p['trials'] if r['label'] == gap['label']]
        if len(rows) != 1:
            raise ValueError('REFUSED_AMBIGUOUS_PROPOSAL_LABEL:' + gap['label'])
        resolved, evidence, resolution, reason = resolve(rows[0], text)
        identity_row = dict(rows[0], **{k: v for k, v in resolved.items() if k != 'spans' and v is not None})
        if join(identity_row, held_identities)['status'] != 'NOT_JOINED':
            continue
        # Inventory absence is only a search-gap hypothesis; lexical identity
        # failures can cause it. No scope exclusion inferred from a broad review.
        hypothesis = 'NOT_RETRIEVED_BY_SEARCH' if gap.get('our_state') == 'NOT_IN_INVENTORY' else 'UNKNOWN'
        queue['missing'].append(dict(label=gap['label'], resolved=resolved,
            resolution=resolution, resolution_note=reason, identity_evidence=evidence,
            evidence_kind='RELAYED' if any(re.search(r'(?i)unpublished data|investigator.supplied|personal communication', s) for s in evidence) else 'PRINTED',
            why_missing_hypothesis=hypothesis, scope_difference=None,
            scope_evidence=[{'source': 'proposal.scope_note', 'span': p['scope_note']},
                            {'source': 'baseline_census.trial', 'span': json.dumps(gap, ensure_ascii=False, sort_keys=True)}]))
    return queue


def verify(queue, root=ROOT, baseline=None):
    """Raise named ValueError on any refusal; True means reproducible hints only."""
    root = Path(root)
    if not isinstance(queue, dict):
        raise ValueError('REFUSED_QUEUE_SCHEMA')
    slug = queue.get('slug')
    slug_ok(slug)
    p, text, refusal = source(slug, root)
    if queue.get('document_sha256') != p['document_sha256']:
        raise ValueError('REFUSED_SHA256_MISMATCH:' + slug)
    if queue.get('comparator_pmid') != p['comparator_pmid']:
        raise ValueError('REFUSED_COMPARATOR_IDENTITY:' + slug)
    if not isinstance(queue.get('missing'), list):
        raise ValueError('REFUSED_MISSING_SCHEMA')
    for entry in queue['missing']:
        if not isinstance(entry, dict) or not isinstance(entry.get('resolved'), dict):
            raise ValueError('REFUSED_ENTRY_SCHEMA')
        resolved = entry['resolved']
        spans = resolved.get('spans')
        if not isinstance(spans, dict) or set(spans) - set(FIELDS):
            raise ValueError('REFUSED_SPANS_SCHEMA')
        for key in FIELDS:
            if key not in resolved:
                raise ValueError('REFUSED_MISSING_FIELD:' + key)
            value = resolved[key]
            if value is None:
                if key in spans:
                    raise ValueError('REFUSED_SPAN_WITHOUT_VALUE:' + key)
                continue
            span = spans.get(key)
            if not isinstance(span, str) or not span or text is None or span not in text:
                raise ValueError('REFUSED_SPAN_NOT_HELD:' + key)
            if not isinstance(value, str) or not value:
                raise ValueError('REFUSED_FIELD_TYPE:' + key)
            if key in IDS and value not in identifiers(key, span):
                raise ValueError('REFUSED_IDENTIFIER_NOT_IN_OWN_SPAN:' + key)
            if key not in IDS and value not in span:
                raise ValueError('REFUSED_LITERAL_NOT_IN_OWN_SPAN:' + key)
            if key == 'year' and not re.fullmatch(r'(?:19|20)\d{2}', value):
                raise ValueError('REFUSED_YEAR_TYPE')
        for span in entry.get('identity_evidence', []):
            if not isinstance(span, str) or not span or text is None or span not in text:
                raise ValueError('REFUSED_IDENTITY_EVIDENCE_NOT_HELD')
    # Re-derive links and membership: containment alone must not permit borrowing
    # another trial's real identifier or dropping an inconvenient missing label.
    if baseline is None:
        from scripts.g1_proposal_census import census
        baseline = census(root)
    rows = [r for r in baseline['topics'] if r['slug'] == slug]
    if len(rows) != 1 or queue != build_queue(rows[0], root):
        raise ValueError('REFUSED_QUEUE_NOT_REPRODUCIBLE:' + slug)
    return True


def load(slug, root=ROOT):
    slug_ok(slug)
    queue = read(Path(root) / 'evidence/g1_inventory_queue' / (slug + '.json'))
    if queue.get('slug') != slug:
        raise ValueError('REFUSED_QUEUE_SLUG_MISMATCH')
    verify(queue, root)
    return queue
