"""Additive document-bound verified-effect contract; legacy readers remain valid."""
from . import claimgraph

FIELDS = ('source_level', 'document_ref', 'document_sha256', 'document_path',
          'extracted_text', 'extracted_text_sha256', 'retrieved_utc', 'span',
          'span_offset', 'analysis_set', 'censoring', 'timepoint',
          'endpoint_identity_source', 'endpoint_identity', 'target_result_status', 'retrieved_precision', 'retrieval_mode')


def metadata(row):
    evidence = row.get('provenance') if isinstance(row.get('provenance'), dict) else row
    return {key: row.get(key, evidence.get(key)) for key in FIELDS
            if key in row or key in evidence}


def refusal(row):
    if not row or not (row.get('source_level') or row.get('document_sha256')
                       or isinstance(row.get('provenance'), dict)):
        return None  # Historical contract, unchanged for other pages.
    evidence = row.get('provenance') if isinstance(row.get('provenance'), dict) else row
    if row.get('source') != evidence.get('span'):
        return 'source differs from document-bound span'
    result = claimgraph.verify_fact(row)
    if result['verified'] and evidence.get('span_offset') is not None:
        text = (claimgraph.ROOT / evidence['extracted_text']).read_bytes().decode('utf-8')
        if text.find(evidence['span']) != evidence['span_offset']:
            return 'recorded character offset does not locate span'
    return None if result['verified'] else result['reason']
