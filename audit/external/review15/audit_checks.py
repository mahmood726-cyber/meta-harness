#!/usr/bin/env python3
"""Independent, standard-library checks for topic 15 at ref 0730234d0b4f.

Inputs are explicitly labelled manual transcriptions. No network is used.
No production harness code is imported. No canonical certificate or complete
review hash is recomputed. The lexical check exercises only the positive
whole-token title-match step for these ASCII fixtures, not full screening,
registry/family adjudication, production publication gates, or code replay.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any


def count_effects(row: dict[str, int]) -> dict[str, Any]:
    a, nt, c, nc = (row[x] for x in ('events_t', 'n_t', 'events_c', 'n_c'))
    if not all(isinstance(x, int) and not isinstance(x, bool) for x in (a, nt, c, nc)):
        raise ValueError('Counts and denominators must be integers.')
    if not (0 < a < nt and 0 < c < nc):
        raise ValueError('This check requires positive events and non-events in both arms.')
    rr = (a / nt) / (c / nc)
    se_rr = math.sqrt(1 / a - 1 / nt + 1 / c - 1 / nc)
    odds_ratio = a * (nc - c) / (c * (nt - a))
    se_or = math.sqrt(1 / a + 1 / (nt - a) + 1 / c + 1 / (nc - c))
    interval = lambda point, se: [math.exp(math.log(point) - 1.96 * se), math.exp(math.log(point) + 1.96 * se)]
    return {'rr': rr, 'rr_log_se': se_rr, 'rr_ci95': interval(rr, se_rr),
            'or': odds_ratio, 'or_ci95': interval(odds_ratio, se_or),
            'risk_t': a / nt, 'risk_c': c / nc, 'risk_difference': a / nt - c / nc}


def positive_title_match(title: str, terms: list[str]) -> str | None:
    """Isolated positive branch; lower-case and whole-token literal matching.

    Matches the boundary form in pinned harness/screen.py. It intentionally
    does not implement lexicon synonym folding or negative population rules.
    These fixtures have no relevant alternative spellings or preceding
    negation of a matched positive phrase. This is NOT full screen_record.
    """
    text = title.lower()
    for term in terms:
        pattern = r'(?<![a-z0-9])' + re.escape(term.lower()) + r'(?![a-z0-9])'
        if re.search(pattern, text):
            return term
    return None


def execute(data: dict[str, Any]) -> dict[str, Any]:
    hashes = []
    for passage in data['passages']:
        digest = hashlib.sha256(passage['text'].encode('utf-8')).hexdigest()
        hashes.append({'label': passage['label'], 'actual_sha256': digest,
                       'expected_sha256': passage['expected_sha256'],
                       'matches': digest == passage['expected_sha256']})
    if not all(x['matches'] for x in hashes):
        raise AssertionError('Passage digest mismatch.')
    discontinuation = count_effects(data['effects']['discontinuation_counts'])
    displayed = data['effects']['discontinuation_rendered_3dp']
    reconstructed = {'rr': round(discontinuation['rr'], 3),
                     'lower': round(discontinuation['rr_ci95'][0], 3),
                     'upper': round(discontinuation['rr_ci95'][1], 3)}
    if reconstructed != displayed:
        raise AssertionError('Reconstructed discontinuation RR differs from displayed rounding.')
    mace_counts = count_effects(data['effects']['mace_counts'])
    titles = data['titles']
    terms = data['population_positive_terms']
    lexical = {
        'primary_title_match': positive_title_match(titles['primary'], terms),
        'companion_title_match': positive_title_match(titles['companion'], terms),
        'companion_without_word_but_match': positive_title_match(titles['companion'].replace(' but ', ' '), terms),
        'counterfactual_scope': 'Removing but is a diagnostic fixture, not a proposed edit to source text or the production algorithm.'
    }
    if lexical['primary_title_match'] is None or lexical['companion_title_match'] is not None or lexical['companion_without_word_but_match'] is None:
        raise AssertionError('The expected positive-title-match fixture was not reproduced.')
    families = data['family_fixture']
    before = Counter(row['family_state'] for row in families)
    after = Counter(data['local_adjudication_only'].get(row['nct'], row['family_state']) for row in families)
    ids = data['rendered_record_ids']
    if len(ids) != 66 or len(set(ids)) != 66:
        raise AssertionError('Manual record-ID fixture is not a unique 66-record list.')
    return {
        'scope': 'Independent calculations and isolated/manual-fixture checks; NOT full repository replay or an end-to-end gate test.',
        'audit_date': data['audit_date'], 'ref': data['ref'], 'review_sha256_as_recorded': data['review_sha256'],
        'passage_hashes': hashes,
        'discontinuation_reconstruction': discontinuation,
        'discontinuation_matches_displayed_rounding': True,
        'mace_reported_hr_preserved': data['effects']['mace_reported_hr'],
        'mace_count_diagnostics_NOT_replacements_for_HR': mace_counts,
        'positive_title_match_fixture': lexical,
        'family_states_as_transcribed': dict(before),
        'family_states_if_only_SELECT_and_SUSTAIN6_are_corrected': dict(after),
        'family_correction_scope': 'Only these two families adjudicated; not a final eligible-trial census.',
        'record_fixture': {'n': len(ids), 'companion_38907684_present': data['companion_pmid'] in ids,
                           'safety_39948761_present': data['safety_report_pmid'] in ids,
                           'scope': 'Presence in the manually transcribed displayed 66-record ledger only; not absence from the entire repository.'},
        'unresolved_report_count_if_only_38907684_linked': data['unresolved_report_candidate_count'] - 1,
        'checks_not_executed': ['canonical review hash', 'complete HTML hash', 'full certificate verifier',
                               'reproduce_review.py', 'full screen_record', 'model-call replay',
                               'systematic search completeness', 'all 66 independent record adjudications']
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    parser.add_argument('--inputs', type=Path, default=here / 'inputs.json')
    parser.add_argument('--output', type=Path, default=here / 'results.json')
    args = parser.parse_args()
    data = json.loads(args.inputs.read_text(encoding='utf-8'))
    result = execute(data)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
