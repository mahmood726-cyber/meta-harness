"""Locate legacy quotations in held bytes before endpoint admission.

Offsets are zero-based, end-exclusive Unicode character offsets in decoded text
(or the selected abstract for records.json#PMID-...). Only whitespace is folded.
"""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re

from . import target_endpoint as te
from . import extract

LEGACY = frozenset({
    'fulltext_verified', 'fulltext_verified_arms', 'aact_verified',
    'abstract_verified', 'abstract_verified_arms', 'registry_verified',
    'pre_specified_dose', 'published_rate',
})


def _fold_map(text):
    chars, positions = [], []
    for match in re.finditer(r'\S+|\s+', text):
        part = match.group()
        if part.isspace():
            chars.append(' ')
            positions.append((match.start(), match.end()))
        else:
            chars.extend(part)
            positions.extend((i, i + 1) for i in range(match.start(), match.end()))
    return ''.join(chars), positions


def locate(text, span):
    folded, positions = _fold_map(text)
    needle = ' '.join(span.split())
    if not needle:
        return None
    start = folded.find(needle)
    if start < 0:
        return None
    # Repeated quotations cannot uniquely identify a result occurrence.
    if folded.find(needle, start + 1) >= 0:
        return None
    return [positions[start][0], positions[start + len(needle) - 1][1]]


def _spans(entry):
    for key in ('source_span', 'verbatim_span'):
        if entry.get(key):
            return [str(entry[key])]
    source = str(entry.get('source') or '')
    pairs = ((chr(34), chr(34)), (chr(0x201c), chr(0x201d)),
             (chr(0x2018), chr(0x2019)), (chr(39), chr(39)))
    spans = []
    for left, right in pairs:
        pattern = re.escape(left) + '([^' + re.escape(right) + ']+)' + re.escape(right)
        for match in re.finditer(pattern, source):
            if left == chr(39) and ((match.start() and source[match.start()-1].isalnum()) or
                                    (match.end() < len(source) and source[match.end()].isalnum())):
                continue
            spans.append(match.group(1))
    return list(dict.fromkeys(spans))


@lru_cache(maxsize=8)
def _record_paths(root):
    index = {}
    for path in sorted((Path(root) / 'cache').glob('*/records.json')):
        data = json.loads(path.read_text(encoding='utf-8'))
        for rec in data.get('records', []):
            index.setdefault(str(rec.get('id')), []).append((path, rec.get('abstract') or ''))
    return index


def _documents(root, pid, entry, record):
    root = Path(root).resolve()
    if entry.get('document_ref'):
        ref = str(entry['document_ref'])
        name, _, fragment = ref.partition('#')
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            return [], 'DOCUMENT_OUTSIDE_REPOSITORY'
        if fragment and fragment != 'PMID-' + pid:
            return [], 'DOCUMENT_IDENTIFIER_MISMATCH'
        return [(path, fragment)], None
    candidates = _record_paths(str(root)).get(pid, [])
    # Match the actual record used by this build, not an unrelated same-ID cache.
    candidates = [(p, a) for p, a in candidates if a == (record.get('abstract') or '')]
    docs = [(p, 'PMID-' + pid) for p, a in candidates if a]
    docs += [(p.parent / ('ft_' + pid + '.txt'), '') for p, _ in candidates]
    return docs, None


def bind_entry(spec, row, entry, root, record=None):
    row = dict(row)
    row.update(endpoint_binding='unbound_legacy_unlocated', endpoint_definition_span=None,
               endpoint_result_span=None, binding_document=None, binding_document_sha256=None,
               binding_offsets=None, binding_searched=[])
    pid = str(row.get('id', '')).removeprefix('PMID ')
    docs, error = _documents(root, pid, entry, record or {})
    spans = _spans(entry)
    row['binding_requested_spans'] = spans
    reason = error or ('NO_VERBATIM_SPAN' if not spans else 'SPAN_NOT_FOUND')
    for path, fragment in docs:
        ref = path.relative_to(Path(root).resolve()).as_posix() + ('#' + fragment if fragment else '')
        row['binding_searched'].append(ref)
        if not path.is_file():
            continue
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        row.update(binding_document=ref, binding_document_sha256=digest)
        # Explicit digests always take precedence over missing quotations; never fall back.
        if any(entry.get(key) and str(entry[key]).lower() != digest
               for key in ('document_sha256', 'extracted_text_sha256')):
            reason = 'DIGEST_MISMATCH'
            break
        try:
            text = raw.decode('utf-8')
            if path.name == 'records.json':
                data = json.loads(text)
                records = [r for r in data.get('records', []) if str(r.get('id')) == pid]
                if len(records) != 1:
                    reason = 'DOCUMENT_IDENTIFIER_MISMATCH'
                    break
                text = records[0].get('abstract') or ''
        except (UnicodeError, ValueError):
            reason = 'DOCUMENT_DECODE_ERROR'
            break
        hits = [(span, locate(text, span)) for span in spans]
        hits = [(s, off) for s, off in hits if off is not None]
        if len(hits) != 1:
            if len(hits) > 1:
                reason = 'AMBIGUOUS_QUOTATIONS'
                break
            continue
        _, offsets = hits[0]
        quoted = text[offsets[0]:offsets[1]]
        # Expand a quoted fragment only to its containing held sentence. For
        # whole-abstract quotations, select among the overlapping sentences.
        sentences = []
        cursor = 0
        # A result sentence may start with an arm count (e.g. REWIND).
        for sentence in re.split(r'(?<=\.)\s+(?=[A-Z(0-9])', text):
            start = text.find(sentence, cursor)
            end = start + len(sentence)
            cursor = end
            if start < offsets[1] and end > offsets[0] and sentence.strip():
                sentences.append(sentence.strip())
        result = sentences[0] if len(sentences) == 1 else quoted
        if len(sentences) > 1:
            keys = ('effect', 'ci_low', 'ci_high') if row.get('effect') is not None else ('ai', 'n1i', 'ci', 'n2i')
            numbers = {float(row[k]) for k in keys if row.get(k) is not None}
            # Some abstracts state arm sizes once at randomisation, then give
            # event counts with percentages. Require those denominators in
            # explicit n= declarations; never infer them from unrelated digits.
            denominators = {float(n) for n in re.findall(r'\bn\s*=\s*([0-9]+)', text, re.I)}
            if row.get('effect') is None:
                needed_denoms = {float(row[k]) for k in ('n1i', 'n2i') if row.get(k) is not None}
                if needed_denoms.issubset(denominators):
                    numbers = {float(row[k]) for k in ('ai', 'ci') if row.get(k) is not None}
            matches = [s for s in sentences if numbers and numbers.issubset(
                {float(n.replace(chr(0xb7), '.')) for n in re.findall(
                    '[0-9]+(?:[.' + chr(0xb7) + '][0-9]+)?', s)})]
            result = matches[0] if len(matches) == 1 else None
        if result and ('<table' in result or result.count('<tr') > 1):
            result = None  # a multi-outcome table is not a result sentence
        binding = te.bind_result_span(text, result)
        row['binding_source_offsets'] = offsets
        if result is not None:
            start = text.rfind(result, 0, max(offsets[1], offsets[0] + len(result)))
            if start < 0:
                start = text.find(result, max(0, offsets[0] - len(result)))
            offsets = [start, start + len(result)]
        else:
            binding['binding_reason'] = 'located quotation has no unique result sentence matching the row numbers'
            binding['endpoint_result_span'] = quoted
        # Non-composite endpoints (e.g. diarrhea, MADRS) have no component
        # vocabulary in bind_result_span; classify the located result sentence,
        # never its surrounding abstract, through the existing keyword path.
        if result and binding['binding'] == te.BINDING_NONE and not te.canonical_components(spec):
            binding.update(binding=te.BINDING_SELF, endpoint_definition_span=result,
                           binding_reason='located result sentence; non-composite keyword classification')
        # Lexical adapter only: the shared binder recognizes 'primary outcome'
        # but not the publication's 'primary-outcome'. Locator bytes stay exact.
        if binding['binding'] == te.BINDING_NONE and result and 'primary-outcome' in result:
            binding = te.bind_result_span(text, result.replace('primary-outcome', 'primary outcome'))
            binding['endpoint_result_span'] = result
        if binding['binding'] == te.BINDING_NONE:
            cls = te._unbound_classification(binding)
        else:
            lexical_spec = spec
            if not te.canonical_components(spec):
                lexical_spec = dict(spec, keywords=list(spec.get('keywords') or []) +
                                    [kw[:-1] for kw in spec.get('keywords') or [] if kw.endswith(' events')])
            cls = te._classify(lexical_spec, binding['endpoint_definition_span'], components=binding['components'])
            # A keyword miss with no recognized components is not proof of a
            # different endpoint. Preserve admission and disclose uncertainty.
            if (cls['target_endpoint_class'] == te.DIFFERENT_OUTCOME
                    and not binding['components']):
                binding.update(binding=te.BINDING_NONE, endpoint_definition_span=None,
                               binding_reason='located sentence does not establish endpoint identity')
                cls = te._unbound_classification(binding)
        row.update(cls)
        row.update(endpoint_binding='located_in_held_bytes', binding_offsets=offsets,
                   endpoint_result_span=binding['endpoint_result_span'],
                   endpoint_definition_span=binding['endpoint_definition_span'],
                   endpoint_binding_reason=binding['binding_reason'],
                   binding_offset_basis='decoded abstract' if path.name == 'records.json' else 'decoded document')
        row['endpoint_admissibility'] = te.admissibility(spec, row)['verdict']
        row['binding_reason'] = binding['binding_reason']
        if row['endpoint_admissibility'] == te.ENDPOINT_UNBOUND:
            row.update(endpoint_binding='located_unbindable', endpoint_admissibility='UNBOUND_LEGACY')
        return row
    row['endpoint_binding_reason'] = reason
    row['endpoint_admissibility'] = 'UNBOUND_LEGACY'
    return row


def admit_legacy_rows(spec, trials, rec_by_id, verified_effects, verified_arms, dose_selection, root):
    """Admit labelled legacy uncertainty; refuse only established incompatibility."""
    kept, refused = [], []
    for original in trials:
        row = original
        if row.get('provenance') in LEGACY or not row.get('endpoint_binding'):
            pid = str(row.get('id', '')).removeprefix('PMID ')
            mappings = ((dose_selection,) if row.get('provenance') == 'pre_specified_dose' else
                        (verified_effects, verified_arms))
            entries = [(m or {}).get(pid) for m in mappings]
            entries = [e for e in entries if e and e.get('outcome') == spec.get('name')
                       and e.get('source', '') == row.get('source', '')]
            if len(entries) > 1:
                numeric = ('effect', 'ci_low', 'ci_high') if row.get('effect') is not None else ('ai', 'ci', 'n1i', 'n2i')
                entries = [e for e in entries if all(e.get(k) == row.get(k) for k in numeric)]
            entry = entries[0] if len(entries) == 1 else {'source': row.get('source', '')}
            row = bind_entry(spec, row, entry, root, rec_by_id.get(pid))
            if row['endpoint_binding'] in ('unbound_legacy_unlocated', 'located_unbindable'):
                kept.append(row)
                continue
        yes, no = te.admit_rows(spec, [row])
        for refusal in no:
            refusal.update({k:v for k,v in row.items() if k.startswith('binding_') or k == 'endpoint_binding_reason'})
        kept.extend(yes)
        refused.extend(no)
    return kept, refused
